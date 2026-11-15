"""1.9.40: ロビーの地上マップのパネル（br_lobby_map.png）に、地点の名前（市街地・雪山・森林・小島・湖）を足す。

元の絵は build_lobby_map_1_9_39.py（会場のブロックから描く）で作ったもの。その上に同じ形の名札を描き足す。
使い方: py -3 source/add_area_labels_1_9_40.py assets/oa/textures/item/br_lobby_map.png
座標は会場の座標（中心が 0,0、東が +x、南が +z。会場は 305×305）。
"""
import sys

from PIL import Image, ImageDraw, ImageFont

S = 512 / 305.0


def px(x, z):
    return ((x + 152.5) * S, (z + 152.5) * S)


path = sys.argv[1]
img = Image.open(path).convert('RGBA')
d = ImageDraw.Draw(img, 'RGBA')
try:
    F = ImageFont.truetype('C:/Windows/Fonts/YuGothB.ttc', 15)
except OSError:
    F = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 15, index=0)


def label(x, z, text, fill=(255, 255, 255), dy=0):
    cx, cz = px(x, z)
    w = d.textlength(text, font=F)
    cx = min(max(cx, w / 2 + 8), 512 - w / 2 - 8)
    cz = min(max(cz + dy, 8), 512 - 26)
    d.rounded_rectangle((cx - w / 2 - 4, cz - 1, cx + w / 2 + 4, cz + 18), 5, fill=(10, 14, 24, 190))
    d.text((cx - w / 2, cz - 1), text, font=F, fill=fill)


# 地点（パネルの絵で、その地域の真ん中あたり。ほかの名札・道の交点を避ける）
label(-97, -5, '市街地', (255, 210, 170))      # 西：家が並ぶ町
label(-60, -130, '雪山', (225, 240, 255))      # 北：雪原と岩山
label(95, -20, '森林', (190, 240, 170))        # 東：深い森
label(120, 116, '小島', (255, 240, 190))       # 南東：桟橋の先の島（島の上）
label(38, -55, '湖', (180, 220, 255))          # 中央の北：湖（湖の右）
img.save(path)
print('ok')
