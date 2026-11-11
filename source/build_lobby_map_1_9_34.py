#!/usr/bin/env python3
"""Renders assets/oa/textures/item/br_lobby_map.png (512x512) from the datapack's target voxel model.
Usage: build_lobby_map_1_9_34.py <map_target.npz> <out.png>"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
t = np.load(sys.argv[1]); V = t['V']; pal = [str(p).replace('minecraft:', '').split('[')[0] for p in t['pal']]; low = int(t['low'])
NY, NZ, NX = V.shape
SKIP = {'air', 'cave_air', 'short_grass', 'tall_grass', 'fern', 'snow', 'seagrass', 'tall_seagrass', 'kelp', 'kelp_plant', 'vine', 'lantern', 'ladder', 'stone_pressure_plate'}
def colour(n, shade_seed):
    c = None
    rules = [('water', (46, 98, 190)), ('oak_leaves', (46, 112, 38)), ('spruce_leaves', (30, 82, 50)), ('azalea', (70, 120, 50)), ('grass_block', (98, 160, 58)), ('snow_block', (240, 246, 250)),
             ('packed_ice', (170, 200, 240)), ('blue_ice', (120, 170, 245)), ('dirt_path', (176, 144, 90)), ('sand', (226, 214, 150)), ('gravel', (140, 136, 134)), ('cobblestone', (120, 120, 120)),
             ('mossy', (100, 126, 90)), ('stone_brick', (130, 130, 134)), ('stone', (124, 124, 124)), ('deepslate', (66, 66, 72)), ('andesite', (136, 136, 134)), ('bricks', (170, 80, 62)),
             ('dark_oak', (74, 50, 28)), ('spruce_planks', (110, 80, 48)), ('spruce', (96, 70, 44)), ('oak_planks', (186, 152, 92)), ('oak', (170, 140, 86)), ('oxidized', (60, 170, 140)),
             ('weathered', (90, 160, 110)), ('exposed', (160, 130, 100)), ('copper', (190, 110, 70)), ('sea_lantern', (200, 240, 235)), ('blackstone', (40, 36, 44)), ('quartz', (236, 232, 224)),
             ('hay', (200, 170, 40)), ('wool', (230, 230, 230)), ('tulip', (230, 90, 120)), ('daisy', (240, 240, 240)), ('allium', (170, 100, 220)), ('poppy', (210, 40, 40)), ('dandelion', (240, 210, 40)),
             ('cornflower', (80, 110, 230)), ('bluet', (220, 230, 240)), ('chest', (170, 110, 30)), ('barrel', (120, 84, 44)), ('coal', (60, 60, 60)), ('redstone', (200, 40, 40)), ('glass', (190, 225, 240)), ('prismarine', (80, 150, 140)), ('dirt', (130, 94, 60))]
    for k, v in rules:
        if k in n: c = v; break
    if n == 'blue_wool': c = (50, 80, 200)
    if n == 'red_wool': c = (200, 50, 50)
    if n == 'light_blue_wool': c = (110, 170, 230)
    return c or (150, 150, 150)
H = np.full((NZ, NX), low, int); C = np.zeros((NZ, NX, 3)); D = np.zeros((NZ, NX))
for z in range(NZ):
    for x in range(NX):
        col = V[:, z, x]; top = None
        for y in range(NY - 1, -1, -1):
            n = pal[col[y]]
            if n in SKIP: continue
            top = (y, n); break
        if top is None: C[z, x] = (30, 30, 30); continue
        y, n = top; H[z, x] = y + low
        c = np.array(colour(n, 0), float)
        if n == 'water':
            d = 0
            while y - d >= 0 and pal[col[y - d]] == 'water': d += 1
            D[z, x] = d; f = min(1, (d - 1) / 5)
            c = np.array((92, 160, 220), float) * (1 - f) + np.array((24, 56, 140), float) * f
        C[z, x] = c
# hill shading
Hn = H.astype(float)
sh = np.zeros_like(Hn); sh[1:, 1:] = (Hn[1:, 1:] - Hn[:-1, :-1])
C = np.clip(C * (1 + 0.07 * np.clip(sh, -3, 3))[..., None], 0, 255)
rng = np.random.default_rng(7); C = np.clip(C + rng.normal(0, 3.0, (NZ, NX, 1)), 0, 255)
img = Image.fromarray(C.astype(np.uint8), 'RGB').resize((512, 512), Image.BICUBIC).convert('RGBA')
S = 512 / 305.0
def px(x, z): return ((x + 152.5) * S, (z + 152.5) * S)
d = ImageDraw.Draw(img, 'RGBA')
try: F = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 15, index=0)
except Exception: F = ImageFont.load_default()
def label(x, z, text, fill=(255, 255, 255), dy=12):
    cx, cz = px(x, z); w = d.textlength(text, font=F); cx = min(max(cx, w / 2 + 8), 512 - w / 2 - 8)
    d.rounded_rectangle((cx - w / 2 - 4, cz + dy - 1, cx + w / 2 + 4, cz + dy + 18), 5, fill=(10, 14, 24, 190))
    d.text((cx - w / 2, cz + dy - 1), text, font=F, fill=fill)
def icon(x, z, kind):
    cx, cz = px(x, z)
    if kind == 'cave':
        d.ellipse((cx - 9, cz - 9, cx + 9, cz + 9), fill=(20, 40, 90, 235), outline=(220, 240, 255, 255), width=2)
        for a in range(0, 180, 60):
            import math
            dx, dz = math.cos(math.radians(a)) * 6, math.sin(math.radians(a)) * 6
            d.line((cx - dx, cz - dz, cx + dx, cz + dz), fill=(230, 245, 255, 255), width=2)
    elif kind == 'ruin':
        d.polygon([(cx, cz - 10), (cx + 10, cz), (cx, cz + 10), (cx - 10, cz)], fill=(10, 120, 120, 235), outline=(210, 255, 250, 255))
        d.ellipse((cx - 3, cz - 3, cx + 3, cz + 3), fill=(255, 230, 120, 255))
    elif kind == 'tower':
        d.rectangle((cx - 7, cz - 7, cx + 7, cz + 7), fill=(70, 70, 78, 235), outline=(240, 220, 120, 255), width=2)
        d.rectangle((cx - 2, cz - 2, cx + 2, cz + 2), fill=(240, 220, 120, 255))
    elif kind == 'ship':
        d.polygon([(cx - 9, cz - 3), (cx + 9, cz - 3), (cx + 5, cz + 6), (cx - 5, cz + 6)], fill=(120, 76, 40, 240), outline=(255, 235, 190, 255))
        d.line((cx, cz - 3, cx, cz - 13), fill=(255, 235, 190, 255), width=2); d.polygon([(cx, cz - 13), (cx + 8, cz - 8), (cx, cz - 6)], fill=(240, 240, 250, 255))
    elif kind == 'plaza':
        d.ellipse((cx - 9, cz - 9, cx + 9, cz + 9), outline=(255, 215, 90, 255), width=3)
icon(-78, 111, 'ship'); label(-78, 111, '帆船', (255, 235, 190), dy=-34)
icon(0, 0, 'plaza'); label(0, 0, '中央広場', (255, 230, 140), dy=-32)
d.rectangle((0, 0, 511, 511), outline=(20, 24, 36, 255), width=4)
img.convert('RGBA').save(sys.argv[2])
print('ok')
