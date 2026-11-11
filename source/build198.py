from pathlib import Path
import json,shutil,math,copy
from PIL import Image
P=Path('revision/pack');F=P/'data/oa/function';R=Path('release_1_9_8/resourcepack');shutil.copytree('release_1_9_7/resourcepack',R,dirs_exist_ok=True)
def load(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def w(n,s):
 p=F/(n+'.mcfunction');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n')
# The official vanilla model transforms were read directly from the official 26.3 client JAR.
vanilla=load(Path('release_1_9_8/vanilla_displays.json'))
def rotate(v,angles):
 # JOML rotationXYZ: column vector receives Z, then Y, then X.
 x,y,z=v;rx,ry,rz=map(math.radians,angles)
 x,y=x*math.cos(rz)-y*math.sin(rz),x*math.sin(rz)+y*math.cos(rz)
 x,z=x*math.cos(ry)+z*math.sin(ry),-x*math.sin(ry)+z*math.cos(ry)
 y,z=y*math.cos(rx)-z*math.sin(rx),y*math.sin(rx)+z*math.cos(rx)
 return [x,y,z]
def anchored(rot,scale,anchor,target,left=False):
 actual=rot[:] if not left else [rot[0],-rot[1],-rot[2]]
 v=rotate([q-8 for q in anchor],actual);t=[target[i]-scale*v[i] for i in range(3)]
 if left:t[0]=-t[0]
 return {'rotation':rot,'translation':[round(n,6) for n in t],'scale':[scale]*3}
# Keep the enlarged sprite; move the grip point rather than magnifying the transform's translation.
im=Image.open(R/'assets/oa/textures/item/tayayuyu.png').convert('RGBA');alpha=im.getchannel('A')
y=max(y for y in range(im.height) if any(alpha.getpixel((x,y))>127 for x in range(im.width)))
xs=[x for x in range(im.width) if alpha.getpixel((x,y))>127];x=sum(xs)/len(xs)
anchor=[(x+.5)/im.width*16,(1-(y+.5)/im.height)*16,8]
model=load(R/'assets/oa/models/item/tayayuyu.json');display={}
for context,d in {**vanilla['generated'].get('display',{}),**vanilla['handheld']['display']}.items():
 display[context]=copy.deepcopy(d)
 if context!='gui':display[context]['scale']=[v*1.75 for v in d.get('scale',[1,1,1])]
display['gui']={'rotation':[0,0,0],'translation':[0,0,0],'scale':[1,1,1]}
for hand,left in [('righthand',False),('lefthand',True)]:
 # Upright map shape in third person, with its bottom tip held in the palm.
 display['thirdperson_'+hand]=anchored([0,90 if left else -90,0],.85*1.75,anchor,[0,-1.5,.5],left)
 display['firstperson_'+hand]=anchored([0,90 if left else -90,-25 if left else 25],.68*1.75,anchor,[-1.13 if left else 1.13,-1.75,1.13],left)
model['display']=display;save(R/'assets/oa/models/item/tayayuyu.json',model)
save(R/'assets/oa/items/tayayuyu.json',{'model':{'type':'minecraft:model','model':'oa:item/tayayuyu'}})
# Stapler: non-flat hinged cover, visible spring/magazine, anvil, paper sheets and pivot caps.
def box(frm,to,tex,rotation=None):
 d={'from':frm,'to':to,'faces':{s:{'texture':'#'+tex,'uv':[0,0,16,16]} for s in ['up','down','north','south','east','west']}}
 if rotation:d['rotation']=rotation
 return d
hinge={'origin':[12,5.5,8],'axis':'z','angle':-22.5,'rescale':False}
e=[box([1.3,1.85,4.4],[14.5,2.35,11.6],'rubber'),box([1.2,2.25,4.3],[14.5,3.1,11.7],'red'),box([1.9,3.1,7],[4.6,3.35,9],'metal'),
 box([.8,3.36,5],[8.3,3.48,11],'paper'),box([.65,3.51,5],[8.2,3.63,11],'paper'),
 box([11.5,3.1,5],[14.1,6.0,11],'metal'),box([12,4.1,4.35],[13.5,5.6,5.05],'rubber'),box([12,4.1,10.95],[13.5,5.6,11.65],'rubber'),
 box([2.1,5.45,4.9],[13.2,7.35,11.1],'red',hinge),box([2.9,7.35,5.2],[12.3,7.7,10.8],'red',hinge),
 box([1.75,5.5,5.25],[2.9,7.1,10.75],'red',hinge),box([2.25,4.75,6],[12.1,5.45,10],'metal',hinge),
 box([2.05,4.3,6.25],[3.1,5.1,9.75],'metal',hinge),box([5.7,4.5,7.5],[11.8,4.8,8.5],'rubber',hinge)]
for x in [4.0,4.8,5.6,6.4,7.2,8.0,8.8,9.6]:e.append(box([x,4.72,6.15],[x+.16,4.84,9.85],'metal',hinge))
old=load(R/'assets/oa/models/item/hotchikisu.json');hdisplay=copy.deepcopy(old['display'])
for d in hdisplay.values():d['scale']=[round(v*1.25,5) for v in d.get('scale',[1,1,1])]
hdisplay['gui']={'rotation':[25,135,0],'translation':[0,-.5,0],'scale':[.88,.88,.88]}
hdisplay['firstperson_lefthand']={'rotation':[0,-90,15],'translation':[0,0,0],'scale':[1,1,1]}
hdisplay['thirdperson_lefthand']={'rotation':[0,-90,0],'translation':[0,1,0],'scale':[.875,.875,.875]}
hdisplay['fixed']={'rotation':[0,0,0],'translation':[0,0,0],'scale':[1.25]*3}
save(R/'assets/oa/models/item/hotchikisu.json',{'ambientocclusion':False,'gui_light':'front','textures':{'red':'oa:material/red_concrete','metal':'oa:material/iron_block','rubber':'oa:material/black_wool','paper':'oa:material/white_concrete','particle':'oa:material/red_concrete'},'elements':e,'display':hdisplay})
# F_KiRiSaN_1110 full 3D skin figurine (all six body parts + second skin layer).
# Front is the +Z face, so GUI and held item models share a consistent visible face.
parts=[
 ('head',[6,12,6],[10,16,10],{'south':[8,8,16,16],'north':[24,8,32,16],'east':[0,8,8,16],'west':[16,8,24,16],'up':[8,0,16,8],'down':[16,0,24,8]},(32,0)),
 ('body',[6,6,7],[10,12,9],{'south':[20,20,28,32],'north':[32,20,40,32],'east':[16,20,20,32],'west':[28,20,32,32],'up':[20,16,28,20],'down':[28,16,36,20]},(0,16)),
 ('right_arm',[4,6,7],[6,12,9],{'south':[44,20,48,32],'north':[52,20,56,32],'east':[40,20,44,32],'west':[48,20,52,32],'up':[44,16,48,20],'down':[48,16,52,20]},(0,16)),
 ('left_arm',[10,6,7],[12,12,9],{'south':[36,52,40,64],'north':[44,52,48,64],'east':[32,52,36,64],'west':[40,52,44,64],'up':[36,48,40,52],'down':[40,48,44,52]},(16,0)),
 ('right_leg',[6,0,7],[8,6,9],{'south':[4,20,8,32],'north':[12,20,16,32],'east':[0,20,4,32],'west':[8,20,12,32],'up':[4,16,8,20],'down':[8,16,12,20]},(0,16)),
 ('left_leg',[8,0,7],[10,6,9],{'south':[20,52,24,64],'north':[28,52,32,64],'east':[16,52,20,64],'west':[24,52,28,64],'up':[20,48,24,52],'down':[24,48,28,52]},(-16,0))]
ye=[]
for name,frm,to,uv,offset in parts:
 for overlay in [False,True]:
  pad=.06 if overlay else 0;dx,dy=offset if overlay else (0,0)
  faces={}
  for side,rect in uv.items():
   rr=[rect[0]+dx,rect[1]+dy,rect[2]+dx,rect[3]+dy];assert all(0<=v<=64 for v in rr)
   faces[side]={'texture':'#skin','uv':[v/4 for v in rr]}
  ye.append({'from':[v-pad for v in frm],'to':[v+pad for v in to],'faces':faces})
yold=load(R/'assets/oa/models/item/yuttari.json');yd=copy.deepcopy(yold['display'])
for context,d in yd.items():
 if context!='gui':d['scale']=[v*2 for v in d.get('scale',[1,1,1])]
yd['gui']={'rotation':[10,25,0],'translation':[0,0,0],'scale':[.85]*3}
for hand,left in [('righthand',False),('lefthand',True)]:
 yd['thirdperson_'+hand]=anchored([0,90 if left else -90,0],2,[8,6,8],[0,-1.5,0],left)
 yd['firstperson_'+hand]=anchored([0,25 if left else -25,0],2.4,[8,6,8],[-1.13 if left else 1.13,-1.75,1.13],left)
save(R/'assets/oa/models/item/yuttari.json',{'ambientocclusion':False,'gui_light':'front','textures':{'skin':'oa:skin/f_kirisan_1110','particle':'oa:skin/f_kirisan_1110'},'elements':ye,'display':yd})
# Continuous, bounded colored dust. Only held/equipped uniques; inventory storage and non-uniques are excluded.
colors={1:('ゆうあ',[1,.2,.65]),2:('ぴちぴち',[.15,.6,1]),3:('lazi',[1,.82,.12]),4:('ネロ',[.2,.16,.25]),5:('キリング',[.65,.2,.95]),6:('ゆったり',[.2,.95,1]),7:('ほちきす',[.95,.2,.2]),8:('こまめ',[.6,.28,.4]),9:('たやゆゆ',[.15,.85,.3])}
lines=[]
for k,(n,rgb) in colors.items():
 lines += ['scoreboard players set #held_color oa.tmp 0']
 for slot in ['weapon.mainhand','weapon.offhand','armor.head']:
  lines += [f'execute if items entity @s {slot} *[minecraft:custom_data~{{oa:{{unique:1b,kind:{k}}}}}] run scoreboard players set #held_color oa.tmp 1']
 lines += ['execute if score #held_color oa.tmp matches 1 run particle minecraft:dust{color:'+json.dumps(rgb,separators=(',',':'))+',scale:0.85} ~ ~0.9 ~ 0.28 0.45 0.28 0.015 2 normal @a[distance=..32]']
w('visual/held_particles','\n'.join(lines))
p=F/'tick.mcfunction';p.write_text(p.read_text()+'\nexecute if score #clock oa.beat matches 0 as @a[gamemode=!spectator,nbt=!{Health:0.0f}] at @s run function oa:visual/held_particles\n')
for p in P.rglob('*'):
 if p.suffix in ['.mcfunction','.mcmeta','.md']:
  s=p.read_text();t=s.replace('1.9.7','1.9.8')
  if s!=t:p.write_text(t)
p=R/'pack.mcmeta';d=load(p);d['pack']['description']='OA Visuals 完全版 1.9.8 / Java26.3';save(p,d)
p=P/'README_JA.md';s=p.read_text();s+='''

固有装備9種はメインハンド・オフハンド・頭装備のいずれかにある間、テーマ色の粒子を本人の周囲に出します。同じ種類を複数スロットに持っても演出は重複させません。5tickごとに各色2粒、周囲32mのプレイヤーへ表示します。通常の1個所持なら10人合計で毎秒約80粒です。インベントリに保管しているだけの装備、ゆー・ふろボール、観戦者は対象外です。所持条件を外れると新たな粒子の発生は止まり、出た粒子は自然に消えます。能力のCTや対象判定は変更しません。
''';p.write_text(s)
p=P/'WEAPONS_JA.md';s=p.read_text();s+='\n所持・装着時の粒子色：ゆうあ＝ピンク、ぴちぴち＝青、lazi＝黄、ネロ＝暗紫、キリング＝紫、ゆったり＝水色、ほちきす＝赤、こまめ＝小豆色、たやゆゆ＝緑。手持ち・頭装備のみで発生し、保管中は発生しません。\n';p.write_text(s)
p=R/'README_JA.md';s=p.read_text().replace('Resources 1.9.7','Resources 1.9.8').replace('データパック1.9.7','データパック1.9.8');s+='''

たやゆゆは画像下端を握り位置の基準とし、拡大したまま手から離れないよう表示コンテキストごとに持ち位置を調整しました。モデル全体を後から拡大して表示位置まで移動する方式は廃止しています。ほちきすは赤い可動カバー、金属マガジン、後部ヒンジ、台座のアンビル、紙を追加し、手持ち等の表示倍率を従来の1.25倍にしています。ゆったりはF_KiRiSaN_1110のスキンを、頭・胴・両腕・両脚と各外側レイヤーに貼った立体人形です。手持ちの高さは従来のおよそ2倍の表示倍率、インベントリは枠内に収めています。実際の手との重なり・見た目はMinecraft内では未検証です。
''';p.write_text(s)
for out in [P/'source/build198.py',R/'source/build198.py']:shutil.copyfile('release_1_9_8/build198.py',out)
for out in [P/'source/vanilla_displays198.json',R/'source/vanilla_displays198.json']:shutil.copyfile('release_1_9_8/vanilla_displays.json',out)
Path('release_1_9_8/grip198.json').write_text(json.dumps({'anchor':anchor,'taya_display':display,'yuttari_display':yd},indent=2))
print('Built held particle runtime, anchored Taya, detailed stapler, and 12-element skin figurine.')
