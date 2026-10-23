"""Extrait le tableau Excel des entreprises en JSON compact pour le localisateur.

Usage : python export_data.py "chemin/vers/entreprises_region_automobile_contacts.xlsx"
Régénère index.html (application mobile) à partir de template.html.
Penser à changer VERSION dans sw.js pour que les téléphones rechargent les nouvelles données.
"""
import json, sys, os, base64, collections, urllib.parse, urllib.request
import openpyxl

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\F-MOGLIA\Desktop\Pôle _ Automobile\entreprises_region_automobile_contacts.xlsx"
HERE = os.path.dirname(os.path.abspath(__file__))

TAILLES = ['1 ou 2 salariés', '3 à 5 salariés', '6 à 9 salariés', '10 à 19 salariés', '20 à 49 salariés',
           '50 à 99 salariés', '100 à 199 salariés', '200 à 249 salariés', '250 à 499 salariés',
           '500 à 999 salariés', '1 000 à 1 999 salariés', '2 000 à 4 999 salariés']

wb = openpyxl.load_workbook(SRC, read_only=True)
ws = wb['Toutes les entreprises']
it = ws.iter_rows(values_only=True)
head = [h for h in next(it)]
col = {h: i for i, h in enumerate(head)}
# Colonnes « Prest. … » : Oui / Probable
PREST = [h[len('Prest. '):] for h in head if h and h.startswith('Prest. ')]
rows = [r for r in it if r[0]]

def g(r, name):
    v = r[col[name]]
    if v is None:
        return ''
    return str(v).strip()

# Position de repli : moyenne des établissements du même code postal
par_cp = collections.defaultdict(list)
for r in rows:
    if r[col['Latitude']] is not None:
        par_cp[g(r, 'Code postal')].append((float(r[col['Latitude']]), float(r[col['Longitude']])))

def ban(adresse, cp, ville):
    """Géocode via la Base Adresse Nationale ; renvoie (lat, lon, précis) ou None."""
    for q, precis in ((f'{adresse} {cp} {ville}', True), (f'{cp} {ville}', False)):
        try:
            url = 'https://data.geopf.fr/geocodage/search?' + urllib.parse.urlencode({'q': q, 'limit': 1, 'postcode': cp})
            f = json.load(urllib.request.urlopen(url, timeout=10))['features']
            if f:
                lon, lat = f[0]['geometry']['coordinates']
                return lat, lon, precis and f[0]['properties']['type'] in ('housenumber', 'street')
        except Exception:
            pass
    return None

out, sans_pos = [], 0
for r in rows:
    lat, lon, prec = r[col['Latitude']], r[col['Longitude']], g(r, 'Précision position')
    if lat is None:
        res = ban(g(r, 'Adresse'), g(r, 'Code postal'), g(r, 'Ville'))
        if res:
            lat, lon, precis = res
            prec = 'Adresse (BAN)' if precis else 'Approximative (code postal)'
    if lat is None:
        pts = par_cp.get(g(r, 'Code postal'))
        if not pts:
            sans_pos += 1
            continue
        lat = sum(p[0] for p in pts) / len(pts)
        lon = sum(p[1] for p in pts) / len(pts)
        prec = 'Approximative (code postal)'
    taille = g(r, 'Nombre de salariés')
    out.append({
        'n': g(r, 'Nom Etablissement'), 'v': g(r, 'Ville'), 'cp': g(r, 'Code postal'), 'a': g(r, 'Adresse'),
        's': g(r, 'Libellé Secteur'), 'act': g(r, 'Activité (NAF)'), 'naf': g(r, 'Code NAF'),
        'e': TAILLES.index(taille) if taille in TAILLES else -1,
        't': g(r, 'Téléphone'), 'm': g(r, 'Mail entreprise'), 'mrh': g(r, 'Mail RH / recrutement'),
        'c': g(r, 'Personne à contacter (RH ou direction)'), 'd': g(r, 'Dirigeant(s) (registre officiel)'),
        'w': g(r, 'Site web'), 'li': g(r, 'Page LinkedIn entreprise'), 'lirh': g(r, 'Profil(s) LinkedIn RH'),
        'siret': g(r, 'SIRET'), 'f': g(r, 'Fiche annuaire officiel'),
        'r': g(r, 'Recrute actuellement ?'), 'o': g(r, 'Offres / recrutement repérés'),
        'lat': round(float(lat), 5), 'lon': round(float(lon), 5),
        'ap': 1 if prec.startswith('Approx') else 0,
        'po': [i for i, p in enumerate(PREST) if g(r, 'Prest. ' + p) == 'Oui'],
        'pp': [i for i, p in enumerate(PREST) if g(r, 'Prest. ' + p) == 'Probable'],
    })

data = json.dumps({'tailles': TAILLES, 'prest': PREST, 'e': out}, ensure_ascii=False, separators=(',', ':'))
with open(os.path.join(HERE, 'template.html'), encoding='utf-8') as fh:
    html = fh.read().replace('/*__DATA__*/null', data)
# Logo République française / GRETA Lille Métropole intégré dans la page
with open(os.path.join(HERE, 'logo_greta.png'), 'rb') as fh:
    html = html.replace('__LOGO_SRC__', 'data:image/png;base64,' + base64.b64encode(fh.read()).decode())
with open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8') as fh:
    fh.write(html)
print(f'{len(out)} établissements exportés, {sans_pos} ignorés (sans position)')
