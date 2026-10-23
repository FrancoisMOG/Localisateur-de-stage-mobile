# Stages Auto – version smartphone

Application mobile du localisateur d'entreprises pour stages (Pôle Automobile – GRETA Lille Métropole). Elle s'installe sur l'écran d'accueil d'un téléphone comme une application (PWA), sans passer par un store.

## Fonctionnalités

- Recherche par ville, adresse ou position GPS du téléphone (📍)
- Rayon en un geste : 5, 10, 15, 25 ou 50 km (réglage fin dans Filtres)
- Onglets **Carte**, **Liste**, **Filtres**, **Sélection**
- Sur chaque fiche : **Appeler**, **E-mail**, **Itinéraire** (GPS), **Retenir**
- Filtres par prestations (mécanique, carrosserie, vitrage…), taille, contact, recrutement
- PDF professionnel (logos, coordonnées, cases de suivi) partagé directement depuis le téléphone : mail, WhatsApp, Drive…
- La sélection et la dernière recherche sont mémorisées sur le téléphone

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `index.html` | L'application (données et logo inclus) |
| `template.html` | Modèle de l'application, sans les données |
| `export_data.py` | Reconstruit `index.html` à partir du tableau Excel |
| `manifest.webmanifest` | Nom, couleurs et icônes pour l'installation |
| `sw.js` | Mise en cache : l'application s'ouvre même sans réseau |
| `icon-*.png`, `make_icons.py` | Icônes de l'application et script qui les dessine |
| `logo_greta.png` | Logo République française / GRETA Lille Métropole |

## Installer sur un téléphone

L'application doit être ouverte depuis une adresse **https** (hébergement web) :

- **Android (Chrome)** : ouvrir l'adresse, menu ⋮ → *Installer l'application* ou *Ajouter à l'écran d'accueil*.
- **iPhone (Safari)** : ouvrir l'adresse, bouton Partager → *Sur l'écran d'accueil*.

## Mettre à jour les données

```
python export_data.py "C:\chemin\vers\entreprises_region_automobile_contacts.xlsx"
```

Puis changer `VERSION` dans `sw.js` (ex. `stages-auto-v2`) pour que les téléphones déjà installés récupèrent les nouvelles données.

## Données personnelles

`index.html` contient des noms de dirigeants, des contacts RH et des coordonnées professionnelles. Ne pas l'héberger sur une adresse publique sans avoir vérifié ce point (dépôt GitHub privé, hébergement à accès restreint).
