#!/usr/bin/env python3
"""1.9.167: ロビーの地図パネル用の洞窟マップの絵地図（512×512）を、生成したモデルから描く。
使い方: py -3 scripts/render_cave_panel.py <データパックのルート> <出力PNG>
入力：source/map_cave_target.npz と MAP_CAVE_MANIFEST.json（scripts/build_map_cave.py の出力）。
向きはネザーの絵地図と同じ（右＝東 +x、下＝南 +z）。"""
import sys, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT, OUTP = sys.argv[1], sys.argv[2]
d = np.load(f"{ROOT}/source/map_cave_target.npz")
g, pal = d['grid'], [str(p) for p in d['palette']]
m = json.load(open(f"{ROOT}/MAP_CAVE_MANIFEST.json", encoding='utf8'))
N = g.shape[0]; OFF = N // 2; Y0 = m['y_range'][0]
air = np.array([p == 'minecraft:air' for p in pal])
water = np.array(['water' in p for p in pal])

# 各列の「いちばん上の床」（歩ける空間の最上段の床ブロック）と、その材質
top_floor = np.full((N, N), -1); top_mat = np.zeros((N, N), int); has_water = np.zeros((N, N), bool)
A = air[g]; W = water[g]
for yi in range(g.shape[2] - 2, 0, -1):
    cand = (~A[:, :, yi]) & A[:, :, yi + 1] & (top_floor < 0) & (~W[:, :, yi])
    top_floor[cand] = yi; top_mat[cand] = g[:, :, yi][cand]
has_water = W.any(axis=2)
openm = top_floor >= 0

def color_of(name):
    n = name.split(':')[1]
    table = {'calcite': (214, 206, 226), 'amethyst_block': (154, 102, 210), 'smooth_basalt': (80, 78, 88),
             'moss_block': (88, 140, 52), 'clay': (150, 156, 170), 'rooted_dirt': (128, 96, 70),
             'dripstone_block': (150, 118, 92), 'gravel': (128, 122, 118), 'stone': (118, 118, 118), 'tuff': (104, 106, 96), 'andesite': (126, 126, 128),
             'sculk': (16, 52, 62), 'deepslate': (74, 74, 80), 'cobbled_deepslate': (82, 82, 88),
             'polished_deepslate': (88, 88, 96), 'deepslate_tiles': (64, 64, 72), 'deepslate_bricks': (72, 72, 80),
             'chiseled_deepslate': (58, 58, 66), 'granite': (150, 110, 96)}
    for k, v in table.items():
        if n.startswith(k): return v
    if 'slab' in n: return (70, 70, 80)
    if 'chest' in n: return (200, 160, 60)
    return (110, 108, 104)
pcol = np.array([color_of(p) for p in pal], float)

rng = np.random.default_rng(3)
img = np.zeros((N, N, 3), float)
# 岩の地（暗い茶灰色＋ざらつき）
img[:] = (34, 30, 28)
img += rng.normal(0, 5, (N, N, 1))
fl = np.where(openm, top_floor + Y0, 0)
base = pcol[top_mat]
shade = np.clip(0.80 + 0.035 * (fl + 30), 0.6, 1.25)[:, :, None]
img = np.where(openm[:, :, None], base * shade + rng.normal(0, 6, (N, N, 1)), img)
img = np.where(has_water[:, :, None], np.array([46, 86, 170.0]) + rng.normal(0, 5, (N, N, 1)), img)
# 開いた場所のふち（壁）を暗く
edge = openm & ~(np.roll(openm, 1, 0) & np.roll(openm, -1, 0) & np.roll(openm, 1, 1) & np.roll(openm, -1, 1))
img[edge] *= 0.55
# 物（家・柱・祭壇）：床より上に岩以外の固体がある所
img = np.clip(img, 0, 255).astype(np.uint8)
im = Image.fromarray(img.transpose(1, 0, 2))   # [z, x] にする（下＝南）
S = 512
im = im.resize((S, S), Image.NEAREST)

# 光るもの（ランタン・結晶・ベリー）をにじませて描く
glow = Image.new('RGBA', (S, S), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
sc = S / N
gcol = {'lantern': (255, 190, 90), 'soul_lantern': (120, 220, 255), 'amethyst_cluster': (220, 150, 255), 'cave_vines': (255, 200, 80), 'glow_lichen': (170, 220, 160), 'sea_pickle': (140, 255, 200)}
ids = {}
for i, p in enumerate(pal):
    n = p.split(':')[1].split('[')[0]
    for k in gcol:
        if n == k: ids[i] = gcol[k]
for i, c in ids.items():
    xs, zs = np.nonzero((g == i).any(axis=2))
    for x, z in zip(xs, zs):
        r = 2.4 if 'lantern' in pal[i] else 1.6
        gd.ellipse([x * sc - r, z * sc - r, x * sc + r, z * sc + r], fill=c + (150,))
glow = glow.filter(ImageFilter.GaussianBlur(2.2))
im = Image.alpha_composite(im.convert('RGBA'), glow)

# 外周の枠（エリアの外の暗がり）と、ボーダーの目安
dr = ImageDraw.Draw(im)
dr.rectangle([0, 0, S - 1, S - 1], outline=(18, 14, 12, 255), width=6)

# ラベル
font = ImageFont.truetype('C:/Windows/Fonts/YuGothB.ttc', 15)
def label(x, z, text):
    px, pz = (x + OFF) * sc, (z + OFF) * sc
    w = dr.textlength(text, font=font)
    box = [px - w / 2 - 6, pz - 11, px + w / 2 + 6, pz + 11]
    ov = Image.new('RGBA', (S, S), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.rounded_rectangle(box, 5, fill=(20, 16, 24, 175))
    im.alpha_composite(ov)
    ImageDraw.Draw(im).text((px, pz), text, font=font, fill=(244, 232, 200, 255), anchor='mm')
for a, (x, z) in m['area_centers'].items():
    name = m['areas'][a]
    dz = 0
    if a == '3': name = '鍾乳洞と地底湖'; dz = 30
    if a == '4': name = '廃坑とディープダーク'
    label(x, z + dz, name)
label(0, 18, '地下神殿')
im.convert('RGB').save(OUTP)
print('saved', OUTP)
