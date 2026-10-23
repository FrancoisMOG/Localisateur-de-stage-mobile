"""Dessine les icônes de l'application (épingle blanche sur fond bleu GRETA) sans dépendance externe."""
import math, os, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE, WHITE, ORANGE = (31, 95, 191), (255, 255, 255), (217, 72, 15)


def color_at(x, y):
    """x, y entre 0 et 1. Le motif tient dans les 60 % centraux (zone sûre des icônes « maskable »)."""
    cx, cy, r = 0.5, 0.43, 0.17
    tip = 0.75
    d = math.hypot(x - cx, y - cy)
    if d <= 0.065:
        return BLUE
    if d <= r:
        return WHITE
    # Pointe : triangle tangent au cercle
    if cy < y <= tip:
        half = r * (tip - y) / (tip - cy) * 0.98
        if abs(x - cx) <= half:
            return WHITE
    # Ombre orange sous la pointe
    if math.hypot((x - cx) / 0.13, (y - 0.785) / 0.028) <= 1:
        return ORANGE
    return BLUE


def png(size, path, ss=3):
    rows = []
    for py in range(size):
        row = bytearray([0])
        for px in range(size):
            acc = [0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = color_at((px + (sx + .5) / ss) / size, (py + (sy + .5) / ss) / size)
                    acc[0] += c[0]; acc[1] += c[1]; acc[2] += c[2]
            row += bytes(v // (ss * ss) for v in acc)
        rows.append(bytes(row))
    raw = zlib.compress(b''.join(rows), 9)
    chunk = lambda t, d: struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as fh:
        fh.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0))
                 + chunk(b'IDAT', raw) + chunk(b'IEND', b''))


for s in (180, 192, 512):
    png(s, os.path.join(HERE, f'icon-{s}.png'))
print('icônes créées')
