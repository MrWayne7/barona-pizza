#!/usr/bin/env python3
"""Saca del manual de marca los logos, ilustraciones y fotos, y los deja optimizados en static/img."""
import os, sys, io
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

M = sys.argv[1]            # carpeta con los rasters del manual
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')
LINO = np.array([244, 235, 233], float); CARMIN = (173, 41, 29)

def alpha_from(im, bg, fg):
    a = np.asarray(im.convert('RGB'), float)
    bg = np.array(bg, float); fg = np.array(fg, float)
    d = fg - bg
    t = ((a - bg) @ d) / (d @ d)
    return np.clip(t, 0, 1)

def trim(alpha, pad=6):
    ys, xs = np.where(alpha > 0.08)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return (max(0, x0 - pad), max(0, y0 - pad), min(alpha.shape[1], x1 + pad), min(alpha.shape[0], y1 + pad))

def ink(alpha, color):
    h, w = alpha.shape
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = color; out[..., 3] = (alpha * 255).round()
    return Image.fromarray(out, 'RGBA')

def fit(im, m):
    if max(im.size) > m:
        s = m / max(im.size); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    return im

def save(im, name, q=88, m=None):
    if m: im = fit(im, m)
    p = os.path.join(OUT, name)
    im.save(p, 'WEBP', quality=q, method=6)
    print(f'{name:28} {im.size}  {os.path.getsize(p)//1024} KB')
    return im.size

def cut(page, box, bg, fg):
    im = Image.open(os.path.join(M, page)).convert('RGB').crop(box)
    a = alpha_from(im, bg, fg)
    b = trim(a)
    return a[b[1]:b[3], b[0]:b[2]]

def sticker(a, r):
    """calcomanía: fondo lino con borde, tinta roja encima (como los stickers del manual)"""
    pad = r * 3
    A = np.pad(a, pad)
    solid = ndi.binary_fill_holes(A > 0.35)
    solid = ndi.binary_dilation(solid, iterations=r)
    solid = ndi.gaussian_filter(solid.astype(float), 1.2)
    solid = np.clip((solid - 0.35) / 0.3, 0, 1)
    h, w = A.shape
    out = np.zeros((h, w, 4), float)
    out[..., :3] = LINO; out[..., 3] = solid
    for c in range(3):
        out[..., c] = out[..., c] * (1 - A) + CARMIN[c] * A
    out[..., 3] = np.maximum(out[..., 3], A)
    out[..., 3] *= 255
    return Image.fromarray(out.round().astype(np.uint8), 'RGBA')

RED = (176, 38, 34)    # tinta tal como sale del PDF
BGL = (243, 228, 225)  # lino tal como sale del PDF
sizes = {}
# ---- variaciones de marca (pág. 13) ----
V = 'v13-13.png'
for name, box, m in [('logo-horizontal', (540, 620, 2220, 1180), 900), ('logo-lateral', (2520, 540, 3420, 1200), 700),
                     ('mascota-roja', (1060, 1410, 1690, 2010), 520), ('wordmark-rojo', (2500, 1500, 3420, 1950), 700)]:
    a = cut(V, box, BGL, RED)
    sizes[name] = save(ink(a, CARMIN), name + '.webp', m=m)
    if name == 'wordmark-rojo': sizes['wordmark-blanco'] = save(ink(a, tuple(int(x) for x in LINO)), 'wordmark-blanco.webp', m=m)
    if name == 'mascota-roja':
        sizes['mascota-sticker'] = save(sticker(a, 14), 'mascota-sticker.webp', m=560)
        fav = fit(sticker(a, 22), 180); fav.save(os.path.join(OUT, 'icono-180.png'))
        fit(sticker(a, 22), 48).save(os.path.join(OUT, 'favicon.png'))
# ---- logo completo rojo (pág. 3) y blanco (pág. 7) ----
a = cut('v3-03.png', (0, 0, 4000, 2250), BGL, RED); sizes['lockup-rojo'] = save(ink(a, CARMIN), 'lockup-rojo.webp', m=800)
im7 = Image.open(os.path.join(M, 'v7-07.png')).convert('RGB')
a7 = alpha_from(im7, (172, 37, 37), BGL); b = trim(a7); a7 = a7[b[1]:b[3], b[0]:b[2]]
sizes['lockup-blanco'] = save(ink(a7, tuple(int(x) for x in LINO)), 'lockup-blanco.webp', m=800)
h7, w7 = a7.shape
am = a7[:int(h7 * 0.57), int(w7 * 0.2):int(w7 * 0.8)]; b = trim(am); am = am[b[1]:b[3], b[0]:b[2]]
sizes['mascota-blanca'] = save(ink(am, tuple(int(x) for x in LINO)), 'mascota-blanca.webp', m=520)
# ---- recursos gráficos (pág. 15) ----
V = 'v15-15.png'
for name, box in [('ilus-cajas', (760, 520, 1680, 1620)), ('ilus-masa', (2120, 600, 3330, 1540)), ('ilus-fiesta', (3590, 440, 4590, 1700)),
                  ('ilus-mano', (840, 1790, 1420, 2580)), ('ilus-gaseosa', (2260, 1850, 3020, 2740)), ('ilus-sonrisa', (3830, 1900, 4340, 2510))]:
    a = cut(V, box, BGL, RED)
    sizes[name] = save(ink(a, CARMIN), name + '.webp', m=760)
    sizes[name + '-sticker'] = save(sticker(a, 16), name + '-sticker.webp', m=640, q=86)
# ---- fotos del manual ----
def photo(src, name, box=None, m=1400, q=74):
    im = Image.open(os.path.join(M, src)).convert('RGB')
    if box:
        w, h = im.size; im = im.crop((int(w * box[0]), int(h * box[1]), int(w * box[2]), int(h * box[3])))
    sizes[name] = save(im, name + '.webp', q=q, m=m)
    sizes[name + '-s'] = save(im, name + '-s.webp', q=70, m=720)
photo('im23-000.jpg', 'foto-pizza'); photo('im5-000.jpg', 'foto-masa', m=1104); photo('im16-000.jpg', 'foto-miga', m=920)
photo('im18-000.jpg', 'foto-cajas'); photo('im24-000.jpg', 'foto-letrero', box=(0.12, 0.05, 0.92, 0.95)); photo('im23-001.jpg', 'foto-vasos')
import json
json.dump(sizes, open(os.path.join(OUT, 'sizes.json'), 'w'))
