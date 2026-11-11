from pathlib import Path
import json,shutil,zipfile
src=Path('release_1_9_5/resourcepack');P=Path('release_1_9_6/resourcepack');shutil.copytree(src,P,dirs_exist_ok=True)
def load(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
a=P/'assets/minecraft/atlases/items.json';atlas=load(a);entries={s.get('sprite',s.get('resource')):s for s in atlas['sources'] if s['type']=='minecraft:single'}
for resource,sprite in [('oa:item/killing_face','oa:item/killing_face'),('minecraft:block/gray_wool','oa:material/gray_wool'),('minecraft:block/light_gray_concrete','oa:material/light_gray_concrete')]:
 if sprite not in entries:atlas['sources'].append({'type':'minecraft:single','resource':resource,'sprite':sprite})
save(a,atlas)
p=P/'assets/oa/models/item/killing.json';m=load(p);m['textures']['back']='oa:material/purple_concrete';m['textures']['strap']='oa:material/gray_wool';m['textures']['buckle']='oa:material/light_gray_concrete';save(p,m)
# Keep the inventory icon inside its slot; magnify every in-world/held display context.
p=P/'assets/oa/items/tayayuyu.json';base=load(p)['model'];scaled=dict(base);scaled['transformation']={'translation':[0,0,0],'left_rotation':[0,0,0,1],'scale':[1.75,1.75,1.75],'right_rotation':[0,0,0,1]}
save(p,{'model':{'type':'minecraft:select','property':'minecraft:display_context','cases':[{'when':'gui','model':base}],'fallback':scaled}})
p=P/'pack.mcmeta';d=load(p);d['pack']['description']='OA Visuals 完全版 1.9.6 / Java26.3';save(p,d)
p=P/'README_JA.md';s=p.read_text().replace('Resources 1.9.5','Resources 1.9.6');s=s.replace('インベントリ・手持ち・地面・ロビー展示に共通で反映します。','画像はインベントリ・手持ち・地面・ロビー展示に共通で反映します。手持ち・地面・展示などの表示は元の1.75倍に拡大し、インベントリのアイコンは枠内に収まる元の倍率を維持します。');s=s.replace('正面には提供画像KillingFace.pngをそのまま使用しています。','正面には提供画像KillingFace.pngをそのまま使用しています。正面とひも・裏面の素材をすべてアイテム用アトラスへ登録し、ブロック用アトラスとの参照混在を避けています。');p.write_text(s)
# Verify every direct model texture against the actual ITEM atlas, rather than file existence alone.
sprites={s.get('sprite',s.get('resource')):s['resource'] for s in atlas['sources'] if s['type']=='minecraft:single'}
missing=[];checked=0
for model in (P/'assets/oa/models').rglob('*.json'):
 for ref in load(model).get('textures',{}).values():
  if isinstance(ref,dict):ref=ref['sprite']
  if ref.startswith('#'):continue
  checked+=1
  if ref not in sprites:missing.append((str(model.relative_to(P)),ref))
assert not missing,missing
for sprite,res in sprites.items():
 if res.startswith('oa:'):assert(P/'assets/oa/textures'/(res[3:]+'.png')).is_file(),(sprite,res)
assert (P/'assets/oa/textures/item/killing_face.png').read_bytes()==(src/'assets/oa/textures/item/killing_face.png').read_bytes()
assert m['display']['gui']==load(src/'assets/oa/models/item/killing.json')['display']['gui']
assert set(scaled['transformation'])=={'translation','left_rotation','scale','right_rotation'}
for p in P.rglob('*.json'):load(p)
changed=[]
for old in (src/'assets').rglob('*'):
 if old.is_file() and old.read_bytes()!=(P/old.relative_to(src)).read_bytes():changed.append(str(old.relative_to(src)))
assert set(changed)=={'assets/minecraft/atlases/items.json','assets/oa/models/item/killing.json','assets/oa/items/tayayuyu.json'},changed
p=P/'VALIDATION.json';v=load(p);v['resourcepack_version']='1.9.6';v['fix196']={'killing':'face explicitly added to item atlas; all mask textures use item-atlas sprites; original face and equipment texture unchanged','all_model_direct_textures_checked_against_item_atlas':checked,'unregistered_textures':missing,'tayayuyu_scale':1.75,'gui_icon':'unchanged; fit within inventory slot','transformation':'complete translation/left_rotation/scale/right_rotation','json_refs_zip':'pass','minecraft_rendering':'not tested'};save(p,v)
shutil.copyfile('release_1_9_6/build196.py',P/'source/build196.py')
out=Path('release_1_9_6/OA_BattleRoyale_Resources_v1.9.6.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PASS: item-atlas registration for',checked,'model texture refs; source face preserved; transform complete; unrelated assets unchanged; JSON; ZIP CRC. Game rendering not tested.')
