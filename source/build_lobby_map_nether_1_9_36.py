#!/usr/bin/env python3
"""ネザー会場のロビー用マップ画像 assets/oa/textures/item/br_lobby_map_nether.png (512x512) を生成する。
使い方: build_lobby_map_nether_1_9_36.py <データパックの source/map_nether_target.npz> <out.png>
画像はデータパックのネザー会場モデル（上からの俯瞰）から計算した、オリジナルの絵。外部画像は使っていない。"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
t = np.load(sys.argv[1]); G = t['grid']; pal = [str(p).replace('minecraft:', '').split('[')[0] for p in t['palette']]
N, _, NY = G.shape; Y0 = -20
SKIP = {'air', 'cave_air', 'crimson_roots', 'warped_roots', 'lantern', 'soul_lantern', 'chest'}
RULES = [('lava', (236, 104, 24)), ('crimson_nylium', (150, 34, 48)), ('nether_wart_block', (130, 24, 36)), ('warped_nylium', (28, 128, 118)), ('warped_wart_block', (20, 110, 104)),
         ('crimson_stem', (110, 40, 60)), ('warped_stem', (30, 100, 100)), ('shroomlight', (240, 170, 80)), ('soul_soil', (86, 66, 52)), ('soul_sand', (100, 80, 60)), ('bone_block', (225, 220, 200)),
         ('smooth_basalt', (62, 62, 70)), ('polished_basalt', (84, 84, 92)), ('basalt', (74, 76, 84)), ('magma', (190, 80, 30)), ('gilded', (212, 170, 60)), ('chiseled', (74, 70, 86)),
         ('red_nether_bricks', (110, 30, 36)), ('cracked_nether_bricks', (60, 26, 32)), ('nether_brick_fence', (70, 30, 36)), ('nether_bricks', (84, 36, 42)),
         ('polished_blackstone', (62, 58, 70)), ('blackstone', (44, 40, 50)), ('netherrack', (112, 52, 52)), ('coal_ore', (70, 70, 74)), ('redstone_ore', (190, 40, 40)), ('bedrock', (30, 30, 30))]
def colour(n):
    for k, v in RULES:
        if k in n: return v
    return (140, 140, 140)
C = np.zeros((N, N, 3)); H = np.zeros((N, N))
for xi in range(N):
    for zi in range(N):
        col = G[xi, zi, :]; top = None
        for y in range(NY - 1, -1, -1):
            n = pal[col[y]]
            if n in SKIP: continue
            top = (y, n); break
        if top is None: C[zi, xi] = (30, 30, 30); continue
        y, n = top; H[zi, xi] = y
        C[zi, xi] = colour(n)
sh = np.zeros_like(H); sh[1:, 1:] = H[1:, 1:] - H[:-1, :-1]
C = np.clip(C * (1 + 0.10 * np.clip(sh, -3, 3))[..., None] + (H[..., None] - 8) * 3.0, 0, 255)
rng = np.random.default_rng(11); C = np.clip(C + rng.normal(0, 3.0, (N, N, 1)), 0, 255)
img = Image.fromarray(C.astype(np.uint8), 'RGB').resize((512, 512), Image.BICUBIC).convert('RGBA')
S = 512 / 305.0
def px(x, z): return ((x + 152.5) * S, (z + 152.5) * S)
d = ImageDraw.Draw(img, 'RGBA')
F = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 15, index=0)
def label(x, z, text, fill=(255, 255, 255), dy=0):
    cx, cz = px(x, z); w = d.textlength(text, font=F); cx = min(max(cx, w / 2 + 8), 512 - w / 2 - 8)
    d.rounded_rectangle((cx - w / 2 - 4, cz + dy - 1, cx + w / 2 + 4, cz + dy + 18), 5, fill=(10, 14, 24, 190))
    d.text((cx - w / 2, cz + dy - 1), text, font=F, fill=fill)
label(0, 0, '中央の宝物庫', (255, 224, 130), dy=-9)
label(-72, 0, '大要塞', (255, 200, 120), dy=-9)
label(80, -78, '玄武岩の柱', (230, 230, 240), dy=-9)
label(80, 80, 'ソウルサンドの谷', (240, 215, 180), dy=-9)
label(-60, 86, '真紅の森', (255, 190, 200), dy=-9)
label(-30, -96, '歪んだ森', (170, 245, 235), dy=-9)
label(0, 140, '溶岩の湖', (255, 190, 120), dy=-9)
d.rectangle((0, 0, 511, 511), outline=(20, 24, 36, 255), width=4)
img.convert('RGBA').save(sys.argv[2]); print('ok')
