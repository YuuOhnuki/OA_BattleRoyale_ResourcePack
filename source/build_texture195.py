from pathlib import Path
import json,shutil,zipfile,hashlib
from PIL import Image
src=Path('release_1_9_4/resourcepack');dst=Path('release_1_9_5/resourcepack');shutil.copytree(src,dst,dirs_exist_ok=True)
image=Path('upload/tayayuyu.png');target=dst/'assets/oa/textures/item/tayayuyu.png';shutil.copyfile(image,target)
assert image.read_bytes()==target.read_bytes()
im=Image.open(target);assert im.mode=='RGBA' and im.size==(50,50)
assert im.getchannel('A').getextrema()==(0,255)
p=dst/'pack.mcmeta';d=json.loads(p.read_text());d['pack']['description']='OA Visuals 完全版 1.9.5 / Java26.3';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
p=dst/'README_JA.md';s=p.read_text().replace('Resources 1.9.4','Resources 1.9.5');s+='''

## たやゆゆの武器
提供されたtayayuyu.png（50×50、透過PNG）を、そのまま武器のテクスチャとして使用しています。インベントリ・手持ち・地面・ロビー展示に共通で反映します。能力やデータパックの変更は不要です。
''';p.write_text(s)
count=0
for p in dst.rglob('*.json'):json.loads(p.read_text());count+=1
assert json.loads((dst/'assets/oa/models/item/tayayuyu.json').read_text())['textures']['layer0']=='oa:item/tayayuyu'
assert json.loads((dst/'assets/oa/items/tayayuyu.json').read_text())['model']['model']=='oa:item/tayayuyu'
changed=[]
for p in (src/'assets').rglob('*'):
 if p.is_file():
  q=dst/p.relative_to(src);assert q.exists()
  if p.read_bytes()!=q.read_bytes():changed.append(str(p.relative_to(src)))
assert changed==['assets/oa/textures/item/tayayuyu.png'],changed
p=dst/'VALIDATION.json';v=json.loads(p.read_text());v['resourcepack_version']='1.9.5';v['tayayuyu195']={'source':'provided tayayuyu.png','size':[50,50],'rgba_transparency':True,'source_bytes':'identical','other_assets':'unchanged from 1.9.4','json_texture_references_zip':'pass','minecraft_rendering':'not tested'};p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(dst/'source').mkdir(exist_ok=True);shutil.copyfile(image,dst/'source/tayayuyu195.png');shutil.copyfile('release_1_9_5/build_texture195.py',dst/'source/build_texture195.py')
out=Path('release_1_9_5/OA_BattleRoyale_Resources_v1.9.5.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(dst.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(dst))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PASS: source image exact, RGBA alpha, texture references, other assets preserved, JSON, ZIP CRC. Minecraft rendering not tested.')
