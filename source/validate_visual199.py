from pathlib import Path
import math,json,zipfile,shutil
P=Path('release_1_9_9/resourcepack');B=Path('release_1_9_8/resourcepack');F=Path('revision/pack/data/oa/function')
def load(p):return json.loads(p.read_text())
for p in P.rglob('*.json'):load(p)
a=load(P/'assets/minecraft/atlases/items.json');sprites={s.get('sprite',s.get('resource')) for s in a['sources'] if s['type']=='minecraft:single'}
for p in (P/'assets/oa/models').rglob('*.json'):
 m=load(p)
 for value in m.get('textures',{}).values():
  if isinstance(value,str) and not value.startswith('#'):assert value in sprites,(p,value)
 for el in m.get('elements',[]):
  assert all(-16<=v<=32 for q in [el['from'],el['to']] for v in q)
  for face in el['faces'].values():assert all(0<=v<=16 for v in face.get('uv',[0,0,16,16]))
for p in (B/'assets/oa/textures').rglob('*'):
 if p.is_file():assert p.read_bytes()==(P/p.relative_to(B)).read_bytes()
for name,factor in [('komame',1.75),('yuttari',.75)]:
 m=load(P/f'assets/oa/models/item/{name}.json');old=load(B/f'assets/oa/models/item/{name}.json')
 for ctx in ['firstperson_righthand','firstperson_lefthand','thirdperson_righthand','thirdperson_lefthand','ground']:
  for a,b in zip(m['display'][ctx]['scale'],old['display'][ctx]['scale']):assert abs(a-b*factor)<1e-6,(name,ctx,a,b)
# Numeric model only: compare fixed-point fireball speed to exact vanilla reference across flight.
v=.1;fv=150000;dist=0
for tick in range(59):
 v=(v+.1)*.95;fv=(fv+150000)*95//100
 assert abs(fv/1000000-v*1.5)<.00003
 assert fv/1000000/12<.25
 dist+=fv/1000000
assert 118<dist<120
vy=1.35;height=0;frames=0
while vy>0:height+=vy;vy=(vy-.08)*.98;frames+=1
assert 10<height<10.2 and frames==15
carrier=(F/'furoball/carrier/tick.mcfunction').read_text();assert 'Passengers[0]' not in carrier and 'execute on passengers' in carrier and 'oa.id = #f_car_owner' in carrier
up=(F/'furoball/up.mcfunction').read_text();assert '~ ~0.02 ~' in up and up.count('Motion:')==1
assert '#f_step oa.tmp 13' in (F/'furoball/tick.mcfunction').read_text()
assert '$(step)' in (F/'furoball/move.mcfunction').read_text()
spawn=(F/'furoball/spawn.mcfunction').read_text();assert 'billboard:"center"' in spawn and 'scale:[1.5f,1.5f,1.5f]' in spawn
# Existing masks and other bespoke assets stay unchanged.
for n in ['raji','killing','hotchikisu','tayayuyu']:assert(P/f'assets/oa/models/item/{n}.json').read_bytes()==(B/f'assets/oa/models/item/{n}.json').read_bytes()
p=P/'VALIDATION.json';d=load(p);d['resourcepack_version']='1.9.9';d['visual199']={'komame':'voxel bar, wood stick, bean chunks; held scale x1.75','yuttari':'held scale x0.75; grip maintained','atlas_refs_uv_json':'pass','fireball_numeric_model':'1.5x native air speed within fixed-point rounding','air_range_59_ticks_m':dist,'carrier_ballistic_model_rise_m':height,'actual_player_height':'not measured','server_client_multiplayer':'not tested'};p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
shutil.copyfile('release_1_9_9/validate_visual199.py',P/'source/validate_visual199.py')
out=Path('release_1_9_9/OA_BattleRoyale_Resources_v1.9.9.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(P.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print('PASS atlas/UV/JSON, source textures unchanged, size ratios, live-rider source check, speed/arc numeric models, ZIP. Player/server tests NOT performed. Modeled range:',round(dist,4),'m; carrier rise:',round(height,4),'m.')
