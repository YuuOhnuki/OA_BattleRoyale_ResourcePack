from pathlib import Path
import json,math,zipfile,shutil
P=Path('release_1_9_8/resourcepack');base=Path('release_1_9_7/resourcepack')
def load(p):return json.loads(p.read_text())
for p in P.rglob('*.json'):load(p)
a=load(P/'assets/minecraft/atlases/items.json');sprites={s.get('sprite',s.get('resource')) for s in a['sources'] if s['type']=='minecraft:single'}
for p in (P/'assets/oa/models').rglob('*.json'):
 m=load(p)
 for v in m.get('textures',{}).values():
  if isinstance(v,str) and not v.startswith('#'):assert v in sprites,(p,v)
 for el in m.get('elements',[]):
  assert all(-16<=v<=32 for a in [el['from'],el['to']] for v in a),(p,el)
  for face in el['faces'].values():
   assert face['texture'].startswith('#')
   assert face['texture'][1:] in m['textures']
   assert all(0<=q<=16 for q in face.get('uv',[0,0,16,16])),(p,face)
for p in (base/'assets/oa/textures').rglob('*'):
 if p.is_file():assert p.read_bytes()==(P/p.relative_to(base)).read_bytes()
for p in ['assets/oa/models/item/killing.json','assets/oa/models/item/raji.json']:
 assert(P/p).read_bytes()==(base/p).read_bytes()
assert load(P/'assets/oa/items/tayayuyu.json')['model']=={'type':'minecraft:model','model':'oa:item/tayayuyu'}
g=load(Path('release_1_9_8/grip198.json'))
def rot(v,angles):
 x,y,z=v;rx,ry,rz=map(math.radians,angles)
 x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
 x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
 y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
 return [x,y,z]
for kind,anchor in [('taya',g['anchor']),('yuttari',[8,6,8])]:
 for hand,left in [('righthand',False),('lefthand',True)]:
  for view in ['firstperson','thirdperson']:
   d=g[kind+'_display'][view+'_'+hand];r=d['rotation'][:];t=d['translation'][:]
   if left:r[1]*=-1;r[2]*=-1;t[0]*=-1
   point=rot([x-8 for x in anchor],r);point=[point[i]*d['scale'][i]+t[i] for i in range(3)]
   expected=([-1.13 if left else 1.13,-1.75,1.13] if view=='firstperson' else [0,-1.5,.5 if kind=='taya' else 0])
   assert max(abs(point[i]-expected[i]) for i in range(3))<.00001,(kind,view,hand,point)
m=load(P/'assets/oa/models/item/yuttari.json');assert len(m['elements'])==12 and m['textures']['skin']=='oa:skin/f_kirisan_1110'
assert load(P/'assets/oa/models/item/hotchikisu.json')['display']['firstperson_righthand']['scale']==[1,1,1]
f=Path('revision/pack/data/oa/function/visual/held_particles.mcfunction').read_text();assert f.count('run particle minecraft:dust')==9
assert all(f'kind:{i}' in f for i in range(1,10));assert 'inventory.' not in f and 'oa_overwork' not in f and 'oa_furoball' not in f
assert all(' 2 normal @a[distance=..32]' in l for l in f.splitlines() if 'run particle' in l)
# No gameplay modifiers or effects are granted by this visual-only function.
assert not any(w in f for w in ['attribute ','effect give','damage ','tp ','clear @'])
v=load(P/'VALIDATION.json');v['resourcepack_version']='1.9.8';v['model198']={'taya':'1.75x held size preserved; wrapper removed; image bottom grip anchor fixed in both hands','stapler':'hinged cover/magazine/anvil/paper; held display scale x1.25','yuttari':'12 elements: 6 skin parts plus outer skin layer; F_KiRiSaN_1110; held scale x2','texture_atlas_and_uv':'pass','affine_grip_anchor_math':'pass, both hands/first and third person','source_texture_bytes':'unchanged','client_rendering':'not tested'};(P/'VALIDATION.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile('release_1_9_8/validate_visual198.py',P/'source/validate_visual198.py')
out=Path('release_1_9_8/OA_BattleRoyale_Resources_v1.9.8.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PASS JSON, model item-atlas sprites, UVs, geometry bounds, grip anchor transforms (both hands), particle slot/rate guards, ZIP CRC. Server/client tests NOT performed.')
