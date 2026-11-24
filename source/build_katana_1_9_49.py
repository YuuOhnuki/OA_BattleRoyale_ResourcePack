"""刀（アシスト武器）のアイテム画像 16x16 を描く（オリジナル、外部画像なし。1.9.49）。"""
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
img=Image.new('RGBA',(16,16),(0,0,0,0));px=img.load()
OUT=(28,30,38,255); SPINE=(150,160,176,255); BLADE=(206,214,226,255); EDGE=(250,252,255,255); HAMON=(178,200,222,255)
GOLD=(214,170,60,255); GOLD_D=(140,104,32,255); WRAP=(36,30,44,255); SAME=(236,228,210,255); RED=(178,40,48,255)
def put(x,y,c):
    if 0<=x<16 and 0<=y<16: px[x,y]=c
# 刃：根元(6,9)→切っ先(14,1)。わずかに反らせる（切っ先側を1つ上へ）
spine=[(6,9),(7,8),(8,7),(9,6),(10,5),(11,4),(12,3),(13,2)]
for i,(x,y) in enumerate(spine):
    put(x-1,y,OUT); put(x,y-1,OUT)
    put(x,y,SPINE)
    put(x+1,y,BLADE if i<len(spine)-1 else EDGE)
    put(x+1,y+1,EDGE)
    if i%2==0: put(x+1,y,HAMON)
put(14,1,EDGE); put(13,1,OUT); put(14,0,OUT); put(15,1,OUT); put(14,2,EDGE); put(15,2,OUT)
for x,y in spine: put(x+2,y+1,OUT) if px[x+2,y+1][3]==0 else None
# 鍔（つば）：根元を横切る金の板
for x,y in [(3,8),(4,9),(5,10),(6,11),(7,12)]: put(x,y,GOLD)
for x,y in [(3,7),(2,8),(7,13),(8,12)]: put(x,y,GOLD_D)
put(5,9,GOLD_D); put(6,10,GOLD_D)
# 柄（つか）：黒の柄巻と白い鮫皮の菱目、柄頭は金
for i,(x,y) in enumerate([(4,11),(3,12),(2,13)]):
    put(x,y,SAME if i%2==0 else WRAP); put(x+1,y,WRAP); put(x,y+1,WRAP)
    put(x-1,y,OUT) if px[x-1,y][3]==0 else None
put(1,14,GOLD); put(0,14,GOLD_D); put(1,15,GOLD_D); put(2,14,RED)
out=R/'assets/oa/textures/item/katana.png'
img.save(out)
img.resize((256,256),Image.NEAREST).save(R/'source/katana_preview.png')
print(out)
