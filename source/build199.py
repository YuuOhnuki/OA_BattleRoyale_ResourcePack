from pathlib import Path
import json,shutil,math,copy
P=Path('revision/pack');F=P/'data/oa/function';R=Path('release_1_9_9/resourcepack');shutil.copytree('release_1_9_8/resourcepack',R,dirs_exist_ok=True)
def load(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def edit(n,a,b):
 p=F/(n+'.mcfunction');s=p.read_text();assert a in s,(n,a);p.write_text(s.replace(a,b))
# Player entities are not saved as nested passengers. Test the live passenger relation instead.
edit('furoball/carrier/tick','execute unless data entity @s Passengers[0] run return run function oa:furoball/carrier/release','''scoreboard players operation #f_car_owner oa.tmp = @s oa.fowner
scoreboard players set #f_has_rider oa.tmp 0
execute on passengers if entity @s[type=minecraft:player,gamemode=!spectator,nbt=!{Health:0.0f}] if score @s oa.id = #f_car_owner oa.tmp run scoreboard players set #f_has_rider oa.tmp 1
execute if score #f_has_rider oa.tmp matches 0 run return run function oa:furoball/carrier/release''')
edit('furoball/up','execute if data entity @s RootVehicle run return 0','scoreboard players set #f_mounted oa.tmp 0\nexecute on vehicle run scoreboard players set #f_mounted oa.tmp 1\nexecute if score #f_mounted oa.tmp matches 1 run return 0')
edit('furoball/up','summon minecraft:armor_stand ~ ~-0.95 ~','summon minecraft:armor_stand ~ ~0.02 ~')
# Native Ghast fireball: initial speed .1, per-tick speed=(speed+.1)*.95 in air.
# Scaled initial/acceleration by 1.5 produces the same 1.5 ratio at every tick.
p=F/'load.mcfunction';p.write_text(p.read_text()+'''\nscoreboard objectives add oa.fvel dummy
scoreboard players set #f_accel oa.tmp 150000
scoreboard players set #f_air95 oa.tmp 95
scoreboard players set #f_air100 oa.tmp 100
''')
p=F/'furoball/spawn.mcfunction';s=p.read_text().replace('item_display:"fixed",brightness:', 'item_display:"fixed",billboard:"center",teleport_duration:1,brightness:').replace('scale:[0.5f,0.5f,0.5f]','scale:[1.5f,1.5f,1.5f]');s=s.replace('scoreboard players set @e[tag=oa.furo_new] oa.ftime 60','scoreboard players set @e[tag=oa.furo_new] oa.ftime 60\nscoreboard players operation @e[tag=oa.furo_new] oa.fvel = #f_accel oa.tmp');p.write_text(s)
edit('furoball/tick','scoreboard players set #f_step oa.tmp 4','''scoreboard players operation @s oa.fvel += #f_accel oa.tmp
scoreboard players operation @s oa.fvel *= #f_air95 oa.tmp
scoreboard players operation @s oa.fvel /= #f_air100 oa.tmp
execute store result storage oa:furo_move step double 0.00000008333333333333333 run scoreboard players get @s oa.fvel
particle minecraft:flame ~ ~ ~ 0.2 0.2 0.2 0.01 3 normal @a[distance=..48]
execute if score #clock oa.beat matches 5.. run particle minecraft:smoke ~ ~ ~ 0.15 0.15 0.15 0.005 1 normal @a[distance=..48]
scoreboard players set #f_step oa.tmp 13''')
p=F/'furoball/step.mcfunction';s=p.read_text();s=s.replace('particle minecraft:flame ~ ~ ~ 0.08 0.08 0.08 0.01 2 normal @a[distance=..48]\n','').replace('tp @s ^ ^ ^0.25','function oa:furoball/move with storage oa:furo_move');p.write_text(s)
(F/'furoball/move.mcfunction').write_text('$tp @s ^ ^ ^$(step)\n')
# Gameplay damage, radius, knockback, launch initial velocity and fall protection remain unchanged.
def rot(v,a):
 x,y,z=v;rx,ry,rz=map(math.radians,a)
 x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
 x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
 y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
 return [x,y,z]
def anchored(r,s,anchor,target,left=False):
 rr=r[:] if not left else [r[0],-r[1],-r[2]];v=rot([x-8 for x in anchor],rr);t=[target[i]-s*v[i] for i in range(3)]
 if left:t[0]*=-1
 return {'rotation':r,'translation':[round(v,6) for v in t],'scale':[s]*3}
def box(fr,to,tex):return {'from':fr,'to':to,'faces':{s:{'texture':'#'+tex,'uv':[0,0,16,16]} for s in ['up','down','north','south','east','west']}}
# Minecraft-style ice bar: bevelled voxel silhouette, embedded azuki chunks, wooden stick.
a=R/'assets/minecraft/atlases/items.json';atlas=load(a);have={s.get('sprite') for s in atlas['sources']}
for material in ['pink_terracotta','white_terracotta','stripped_birch_log','stripped_birch_log_top']:
 sprite='oa:material/'+material
 if sprite not in have:atlas['sources'].append({'type':'minecraft:single','resource':'minecraft:block/'+material,'sprite':sprite})
save(a,atlas)
e=[box([7.4,0,7.5],[8.6,.3,8.5],'wood'),box([7.25,.3,7.5],[8.75,6.3,8.5],'wood'),box([5.5,5.5,6.9],[10.5,6.2,9.1],'ice'),box([5,6.2,6.8],[11,14.6,9.2],'ice'),box([5.5,14.6,6.9],[10.5,15.35,9.1],'ice'),box([6,15.35,7],[10,15.8,9],'light')]
for el in e[:2]:
 for face in ['up','down']:el['faces'][face]['texture']='#endgrain'
beans=[(5.6,7.3,.45,.6),(7.5,6.8,.55,.4),(9.3,7.8,.6,.75),(6.9,9.3,.65,.5),(9.8,10.6,.4,.65),(5.8,11.3,.55,.75),(8.2,12.0,.65,.5),(9.1,13.8,.6,.4),(6.4,13.6,.5,.65)]
for idx,(x,y,w,h) in enumerate(beans):
 e.append(box([x,y,9.195],[x+w,y+h,9.245],'bean'))
 e.append(box([16-x-w,y+.12,6.755],[16-x,y+h+.12,6.805],'bean'))
# Small pale frozen grains, no photo texture wrapping around the bar.
for x,y in [(6.4,8.5),(8.8,9.9),(7.3,11.1),(10.0,12.8),(6.1,14.4)]:e.append(box([x,y,9.2],[x+.22,y+.22,9.24],'light'))
p=R/'assets/oa/models/item/komame.json';old=load(p);display=copy.deepcopy(old['display'])
for c,d in display.items():
 if c!='gui':d['scale']=[round(v*1.75,6) for v in d.get('scale',[1,1,1])]
for hand,left in [('righthand',False),('lefthand',True)]:
 display['firstperson_'+hand]=anchored([0,90 if left else -90,-15 if left else 15],1.1*1.75,[8,3,8],[-1.13 if left else 1.13,-1.75,1.13],left)
 display['thirdperson_'+hand]=anchored([0,90 if left else -90,0],.9*1.75,[8,3,8],[0,-1.5,.5],left)
display['gui']={'rotation':[10,-25,-25],'translation':[0,0,0],'scale':[.85]*3}
display['fixed']={'rotation':[0,180,0],'scale':[1.75]*3}
save(p,{'ambientocclusion':False,'gui_light':'front','textures':{'ice':'oa:material/pink_terracotta','bean':'oa:material/brown_terracotta','light':'oa:material/white_terracotta','wood':'oa:material/stripped_birch_log','endgrain':'oa:material/stripped_birch_log_top','particle':'oa:material/pink_terracotta'},'elements':e,'display':display})
# Reduce Yuttari model sizes, while preserving its waist grip in both hands.
p=R/'assets/oa/models/item/yuttari.json';m=load(p)
for c,d in m['display'].items():
 if c!='gui':d['scale']=[round(v*.75,6) for v in d.get('scale',[1,1,1])]
for hand,left in [('righthand',False),('lefthand',True)]:
 m['display']['thirdperson_'+hand]=anchored([0,90 if left else -90,0],1.5,[8,6,8],[0,-1.5,0],left)
 m['display']['firstperson_'+hand]=anchored([0,25 if left else -25,0],1.8,[8,6,8],[-1.13 if left else 1.13,-1.75,1.13],left)
save(p,m)
for p in P.rglob('*'):
 if p.suffix in ['.mcfunction','.mcmeta','.md']:
  s=p.read_text();t=s.replace('1.9.8','1.9.9').replace('約45m','約120m').replace('射程目安45m','射程目安約120m')
  if s!=t:p.write_text(t)
p=R/'pack.mcmeta';m=load(p);m['pack']['description']='OA Visuals 完全版 1.9.9 / Java26.3';save(p,m)
p=P/'README_JA.md';s=p.read_text();s+='''

ふろボールの上昇は、保存される乗客NBTではなく実際の乗車関係と所有者IDで維持を判定します。キャリアは地面に埋めず足元から0.02m上に出し、一度だけ上向き初速1.35を与えます。頂点付近まで乗車し、その後は落下ダメージを無効にしたまま自然落下します。上昇目標は約10mですが、実機の上昇高は未測定です。

火の玉の見た目はカメラに向く大きな発光火球と炎・煙です。実体は引き続き表示エンティティで、バニラのガスト火球による追加ダメージ・地形破壊は起こしません。26.3通常火球の空気中の初速0.1・加速度0.1・抵抗0.95に対し、初速と加速度を0.15にした1.5倍の速度推移です。最大速度目安2.85m/tick、飛翔寿命約3秒、空中での到達距離目安約120m。各tickは12回に分けて衝突を検査します。水では従来どおり爆発します。ダメージ・爆発範囲等は変更しません。
''';p.write_text(s)
p=P/'WEAPONS_JA.md';s=p.read_text();s=s.replace('約120mまで飛びます。','空気中の通常火球の1.5倍の速度推移で、最大約120mまで飛びます。');s+='\n小豆バーはMinecraftの素材色・ボクセル形状に、小豆粒・木目の棒を組み合わせた立体モデルです。手持ち等の倍率は以前の1.75倍。ゆったりの立体人形の倍率は直前の0.75倍。インベントリのアイコンは枠に収める倍率を維持します。\n';p.write_text(s)
p=R/'README_JA.md';s=p.read_text().replace('Resources 1.9.8','Resources 1.9.9').replace('データパック1.9.8','データパック1.9.9');s+='''

小豆バーをMinecraftらしい角を落とした棒アイスと木目の棒にし、表面に小豆粒と淡い氷の粒を追加しています。写真風テクスチャは使わず、アイテム用アトラスへ登録したバニラ素材を使用します。手持ち・地面等の倍率は直前の1.75倍。ゆったり人形は直前の0.75倍に縮小し、握り位置を再計算しました。インベントリは枠内の倍率です。火球・上昇の修正には同版データパックも必要です。
''';p.write_text(s)
for target in [P/'source/build199.py',R/'source/build199.py']:shutil.copyfile('release_1_9_9/build199.py',target)
print('Built live passenger fix, 1.5x native fireball air-speed curve, fireball billboard, voxel azuki bar, smaller Yuttari.')
