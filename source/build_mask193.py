from pathlib import Path
import json,shutil
from PIL import Image,ImageDraw
src=Path('release_1_7_0/resourcepack');dst=Path('release_1_9_3/resourcepack')
shutil.copytree(src,dst,dirs_exist_ok=True)
assets=dst/'assets/oa'
# Keep the supplied face file byte-for-byte. The armor atlas packs it at native 32x32 pixels.
face_path=Path('upload/KillingFace.png');face=Image.open(face_path).convert('RGBA');assert face.size==(32,32)
shutil.copyfile(face_path,assets/'textures/item/killing_face.png')
atlas=Image.new('RGBA',(256,128),(0,0,0,0));atlas.paste(face,(32,32))
draw=ImageDraw.Draw(atlas)
# Standard humanoid helmet UV layout, scaled by four. Only the front and thin straps are opaque.
for x0 in [0,64,96]:
 draw.rectangle((x0,45,x0+31,49),fill=(108,111,118,255))
 draw.line((x0,45,x0+31,45),fill=(151,154,160,255),width=1)
 draw.line((x0,49,x0+31,49),fill=(69,72,79,255),width=1)
# Small rear join: no skin or skull texture under the belt.
draw.rectangle((109,43,114,51),fill=(133,136,143,255))
draw.rectangle((111,44,112,50),fill=(83,86,93,255))
atlas.save(assets/'textures/entity/equipment/humanoid/killing_mask.png')
# Item representation is a shallow mask with a real open head strap, not a textured head cube.
textures={'face':'oa:item/killing_face','back':'minecraft:block/purple_concrete','strap':'minecraft:block/gray_wool','buckle':'minecraft:block/light_gray_concrete','particle':'oa:item/killing_face'}
def box(frm,to,texture):
 return {'from':frm,'to':to,'faces':{side:{'texture':'#'+texture,'uv':[0,0,16,16]} for side in ['up','down','north','south','east','west']}}
plate=box([3.5,3.5,11.75],[12.5,12.5,12.5],'back')
plate['faces']['south']={'texture':'#face','uv':[0,0,16,16]}
model={'ambientocclusion':False,'gui_light':'front','textures':textures,'elements':[
 plate,
 box([3.3,7.65,3.3],[3.75,8.35,11.8],'strap'),
 box([12.25,7.65,3.3],[12.7,8.35,11.8],'strap'),
 box([3.3,7.65,3.3],[12.7,8.35,3.75],'strap'),
 box([7.45,7.35,3.05],[8.55,8.65,3.4],'buckle')],
 'display':{
  'gui':{'rotation':[0,0,0],'translation':[0,0,0],'scale':[1.65,1.65,1.65]},
  'ground':{'rotation':[0,0,0],'translation':[0,3,0],'scale':[.7,.7,.7]},
  'fixed':{'rotation':[0,180,0],'scale':[1.2,1.2,1.2]},
  'firstperson_righthand':{'rotation':[0,-90,25],'translation':[1.13,3.2,1.13],'scale':[.85,.85,.85]},
  'firstperson_lefthand':{'rotation':[0,90,-25],'translation':[1.13,3.2,1.13],'scale':[.85,.85,.85]},
  'thirdperson_righthand':{'rotation':[0,0,0],'translation':[0,3,1],'scale':[.8,.8,.8]},
  'thirdperson_lefthand':{'rotation':[0,0,0],'translation':[0,3,1],'scale':[.8,.8,.8]}}}
(assets/'models/item/killing.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
p=dst/'pack.mcmeta';d=json.loads(p.read_text());d['pack']['description']='OA Visuals 完全版 1.9.3 / Java26.3';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=dst/'README_JA.md';s=p.read_text().replace('1.7.0','1.9.3').replace('データパック1.9.3と組み合わせて','データパック1.9.2と組み合わせて');s+='''

## キリングのお面
正面には提供画像KillingFace.pngをそのまま使用しています。装着時は正面の四角いお面と、頭の左右から後頭部へ回る灰色のひもだけを描画し、それ以外の頭部分は透明です。自分のスキンの髪や後頭部が見えます。インベントリ・手持ち・地面の表示にも、お面と立体的な灰色のひものモデルを使用します。

データパック1.9.2のまま使用できます。装備の能力・MCID・所持制限等は変更しません。このZIPは他の装備・アイテム・マップ表示の素材も含む完全版です。古いOAリソースパックは無効にして、この完全版を有効にしてください。ゲーム内でF3+Tを押すとリソースを再読み込みできます。

ファイル形式、UV位置、正面画像の一致、参照先の静的検査を実施しました。Minecraft内での装着・表示角度の実機検証は未実施です。
''';p.write_text(s)
(dst/'source').mkdir(exist_ok=True)
shutil.copyfile('release_1_9_3/build_mask193.py',dst/'source/build_mask193.py')
shutil.copyfile(face_path,dst/'source/KillingFace.png')
# Preserve the existing equipment asset and data-pack item model IDs.
assert json.loads((assets/'equipment/killing_mask.json').read_text())=={'layers':{'humanoid':[{'texture':'oa:killing_mask'}]}}
print('Created complete resource pack. Face source preserved; equipment atlas: 256x128; model: 5 elements.')
