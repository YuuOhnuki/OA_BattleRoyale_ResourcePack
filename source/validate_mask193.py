from pathlib import Path
from PIL import Image
import json,hashlib,zipfile,shutil
P=Path('release_1_9_3/resourcepack');A=P/'assets/oa';base=Path('release_1_7_0/resourcepack')
count=0
for p in P.rglob('*.json'):json.loads(p.read_text());count+=1
json.loads((P/'pack.mcmeta').read_text())
original=Path('upload/KillingFace.png');copied=A/'textures/item/killing_face.png'
assert original.read_bytes()==copied.read_bytes()
face=Image.open(original).convert('RGBA');atlas=Image.open(A/'textures/entity/equipment/humanoid/killing_mask.png').convert('RGBA')
assert face.size==(32,32) and atlas.size==(256,128)
assert atlas.crop((32,32,64,64)).tobytes()==face.tobytes()
for x in [0,64,96]:
 assert all(atlas.getpixel((i,47))[3]==255 for i in range(x,x+32))
 assert all(atlas.getpixel((i,33))[3]==0 for i in range(x,x+32))
assert atlas.getpixel((20,10))[3]==0
m=json.loads((A/'models/item/killing.json').read_text())
assert len(m['elements'])==5
assert m['elements'][0]['faces']['south']['texture']=='#face'
assert m['display']['gui']['rotation']==[0,0,0]
assert m['textures']['face']=='oa:item/killing_face'
assert all(0<=c<=16 for el in m['elements'] for vector in [el['from'],el['to']] for c in vector)
assert json.loads((A/'items/killing.json').read_text())['model']['model']=='oa:item/killing'
assert json.loads((A/'equipment/killing_mask.json').read_text())['layers']['humanoid'][0]['texture']=='oa:killing_mask'
# Only this mask and current metadata/docs are changed; every other previous asset remains byte-identical.
changed=[]
for old in (base/'assets').rglob('*'):
 if old.is_file():
  new=P/old.relative_to(base);assert new.exists()
  if old.read_bytes()!=new.read_bytes():changed.append(str(old.relative_to(base)))
assert set(changed)=={'assets/oa/models/item/killing.json','assets/oa/textures/entity/equipment/humanoid/killing_mask.png'},changed
# The current data pack still addresses exactly these asset IDs.
d=json.loads(Path('revision/pack/data/oa/item_modifier/visual/k5.json').read_text())
components=next(f['components'] for f in d['functions'] if f['type']=='minecraft:set_components')
assert components['minecraft:equippable']['asset_id']=='oa:killing_mask' and components['minecraft:item_model']=='oa:killing'
v=json.loads((P/'VALIDATION.json').read_text());v['resourcepack_version']='1.9.3';v['killing_mask193']={'face_file':'unchanged supplied KillingFace.png, 32x32','armor_atlas':'256x128; exact face at head-front UV 8,8; transparent sides/back except gray strap','item_model':'5 elements; thin front plate and open side/rear straps','other_assets':'byte-identical to 1.7.0','data_pack_change_required':False,'json_uv_references_and_zip_crc':'pass','minecraft_client_visual_test':'not tested'};(P/'VALIDATION.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile('release_1_9_3/validate_mask193.py',P/'source/validate_mask193.py')
out=Path('release_1_9_3/OA_BattleRoyale_Resources_v1.9.3.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PASS:',count,'JSON files; source bytes and front pixels exact; gray straps and transparency; other assets unchanged; current data-pack asset IDs; ZIP CRC. Client rendering NOT tested.')
print('ZIP',out.stat().st_size,'bytes')
