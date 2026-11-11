from pathlib import Path
import json,shutil,math,zipfile
src=Path('release_1_9_3/resourcepack');p=Path('release_1_9_4/resourcepack');shutil.copytree(src,p,dirs_exist_ok=True)
f=p/'assets/oa/models/item/killing.json';m=json.loads(f.read_text());m['display']['gui']={'rotation':[20,45,0],'translation':[0,0,0],'scale':[1.1,1.1,1.1]};f.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
f=p/'pack.mcmeta';d=json.loads(f.read_text());d['pack']['description']='OA Visuals 完全版 1.9.4 / Java26.3';f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
f=p/'README_JA.md';s=f.read_text().replace('Resources 1.9.3','Resources 1.9.4');s=s.replace('インベントリ・手持ち・地面の表示にも、お面と立体的な灰色のひものモデルを使用します。','インベントリは左右45度・上方20度の斜めから、お面と側面・後部の灰色のひもが見える表示です。表示倍率は1.1倍に抑え、枠内に収めています。手持ち・地面にも、お面と立体的な灰色のひものモデルを使用します。');f.write_text(s)
for f in p.rglob('*.json'):json.loads(f.read_text())
# Orthographic model-space bounds for the GUI transform (Minecraft pixel slots use 16 model units).
coords=[];rx=math.radians(20);ry=math.radians(45)
for el in m['elements']:
 for x in [el['from'][0]-8,el['to'][0]-8]:
  for y in [el['from'][1]-8,el['to'][1]-8]:
   for z in [el['from'][2]-8,el['to'][2]-8]:
    # JOML rotationXYZ composes X after Y when applied to a vertex.
    xx=x*math.cos(ry)+z*math.sin(ry);zz=-x*math.sin(ry)+z*math.cos(ry)
    yy=y*math.cos(rx)-zz*math.sin(rx)
    coords.append((xx*1.1,yy*1.1))
assert all(-8<x<8 and -8<y<8 for x,y in coords),coords
changed=[]
for old in (src/'assets').rglob('*'):
 if old.is_file() and old.read_bytes()!=(p/old.relative_to(src)).read_bytes():changed.append(str(old.relative_to(src)))
assert changed==['assets/oa/models/item/killing.json'],changed
v=json.loads((p/'VALIDATION.json').read_text());v['resourcepack_version']='1.9.4';v['killing_gui194']={'rotation':[20,45,0],'scale':1.1,'gui_bounds_model_units':{'x':[min(c[0] for c in coords),max(c[0] for c in coords)],'y':[min(c[1] for c in coords),max(c[1] for c in coords)]},'only_changed_asset':changed[0],'json_and_slot_bounds':'pass','minecraft_client_rendering':'not tested'};(p/'VALIDATION.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile('release_1_9_4/build_mask194.py',p/'source/build_mask194.py')
out=Path('release_1_9_4/OA_BattleRoyale_Resources_v1.9.4.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(p.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(p))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PASS JSON, GUI projected bounds, unchanged other assets, ZIP CRC. Client rendering not tested.')
print(v['killing_gui194']['gui_bounds_model_units'])
