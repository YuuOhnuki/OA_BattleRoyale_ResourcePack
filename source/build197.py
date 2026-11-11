from pathlib import Path
import json,shutil
P=Path('revision/pack');F=P/'data/oa/function';R=Path('release_1_9_7/resourcepack');shutil.copytree('release_1_9_6/resourcepack',R,dirs_exist_ok=True)
def load(p):return json.loads(p.read_text())
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
# Native player heads render skull profiles when worn. A pumpkin with an explicit no-overlay equippable renders the custom item model instead.
p=P/'data/oa/item_modifier/visual/k3.json';d=load(p)
for fn in d['functions']:
 if fn['type']=='minecraft:set_item':fn['item']='minecraft:carved_pumpkin'
 if fn['type']=='minecraft:set_components':
  fn['components'].pop('minecraft:profile',None);fn['components']['!minecraft:profile']={}
  fn['components']['minecraft:equippable']={'slot':'head','swappable':True,'damage_on_hurt':False,'dispensable':False}
 if fn['type']=='minecraft:set_custom_data':fn['tag']='{oa:{visual_v140:1b,head_v130:1b,mask_v197:1b}}'
save(p,d)
p=F/'inventory/visual.mcfunction';s=p.read_text();s=s.replace('oa:{head_v130:1b}','oa:{mask_v197:1b}');p.write_text(s)
# Keep the registered motif model and ability identity. Only visual migration changes.
for p in P.rglob('*'):
 if p.suffix in ['.mcfunction','.mcmeta','.md']:
  s=p.read_text();t=s.replace('1.9.2','1.9.7')
  if s!=t:p.write_text(t)
# Three item-atlas materials: dark rigid cup, textile bands, silver microphone grille.
a=R/'assets/minecraft/atlases/items.json';atlas=load(a)
if not any(s.get('sprite')=='oa:material/black_wool' for s in atlas['sources']):atlas['sources'].append({'type':'minecraft:single','resource':'minecraft:block/black_wool','sprite':'oa:material/black_wool'})
save(a,atlas)
def box(frm,to,tex='cup'):
 return {'from':frm,'to':to,'faces':{s:{'texture':'#'+tex,'uv':[0,0,16,16]} for s in ['up','down','north','south','east','west']}}
elements=[
 box([4.5,3.7,11.25],[11.5,7.8,14.25]),
 box([5.05,4.0,13.8],[10.95,7.35,14.65]),
 box([3.6,4.15,10.3],[4.7,7.5,13.15]),
 box([11.3,4.15,10.3],[12.4,7.5,13.15]),
 box([4.45,7.7,11.15],[11.55,8.1,13.75],'band'),
 box([4.5,3.5,11.35],[11.5,3.95,13.8],'band'),
 box([3.3,4.4,11.5],[3.95,6.9,13.0],'band'),
 box([12.05,4.4,11.5],[12.7,6.9,13.0],'band'),
 box([3.2,6.05,3.0],[3.85,6.85,11.8],'band'),
 box([12.15,6.05,3.0],[12.8,6.85,11.8],'band'),
 box([3.2,6.05,2.8],[12.8,6.85,3.5],'band'),
 box([3.2,6.8,6.4],[3.85,12.6,7.1],'band'),
 box([12.15,6.8,6.4],[12.8,12.6,7.1],'band'),
 box([3.2,12.15,6.4],[12.8,12.8,7.1],'band'),
 box([3.3,10.7,3.0],[12.7,11.4,3.6],'band'),
 box([3.3,6.8,3.0],[3.9,11.4,3.6],'band'),
 box([12.1,6.8,3.0],[12.7,11.4,3.6],'band'),
 box([7.05,2.85,12.2],[8.95,3.7,13.65],'band'),
 box([7.5,2.85,13.6],[8.5,3.4,13.8],'grille'),
 box([7.75,.9,12.9],[8.25,2.9,13.4],'band')]
m={'ambientocclusion':False,'gui_light':'front','textures':{'cup':'oa:material/black_concrete','band':'oa:material/black_wool','grille':'oa:material/gray_concrete','particle':'oa:material/black_concrete'},'elements':elements,'display':{
 'gui':{'rotation':[20,35,0],'translation':[0,0,0],'scale':[.9,.9,.9]},
 'head':{'rotation':[0,180,0],'translation':[0,0,0],'scale':[1.6,1.6,1.6]},
 'ground':{'translation':[0,3,0],'scale':[.65,.65,.65]},
 'fixed':{'rotation':[0,180,0],'scale':[1,1,1]},
 'firstperson_righthand':{'rotation':[0,-90,25],'translation':[1.13,3.2,1.13],'scale':[.85,.85,.85]},
 'firstperson_lefthand':{'rotation':[0,90,-25],'translation':[1.13,3.2,1.13],'scale':[.85,.85,.85]},
 'thirdperson_righthand':{'rotation':[0,0,0],'translation':[0,3,1],'scale':[.8,.8,.8]},
 'thirdperson_lefthand':{'rotation':[0,0,0],'translation':[0,3,1],'scale':[.8,.8,.8]}}}
save(R/'assets/oa/models/item/raji.json',m)
p=R/'pack.mcmeta';d=load(p);d['pack']['description']='OA Visuals 完全版 1.9.7 / Java26.3';save(p,d)
p=R/'README_JA.md';s=p.read_text().replace('Resources 1.9.6','Resources 1.9.7').replace('データパック1.9.2','データパック1.9.7');s+='''

## laziの防音マスク
参考写真を元に、口元を覆う黒い立体カップ、頭上・側面・後頭部の黒い布バンド、下部のマイク端子と短いケーブルを組み合わせたMinecraft用モデルを作成しています。顔全体をプレイヤーヘッドで覆う方式から、顔の上半分が見える立体マスクへ変更しています。写真そのものを貼り付ける方式ではありません。

このマスクの装着表示にはデータパック1.9.7とリソパ1.9.7の両方が必要です。既存の所持マスクは、データパックの通常インベントリ判定で新しい外観へ更新します。被り物の描画ベースはくり抜かれたカボチャですが、明示した装着コンポーネントにはカボチャの視界オーバーレイを設定していません。能力・名前・MCIDは維持します。装着位置・サイズのMinecraft内実機検証は未実施です。
''';p.write_text(s)
p=P/'README_JA.md';s=p.read_text();s+='''

laziの防音マスクはリソパ1.9.7と組み合わせると、参考写真を模した黒い立体カップと頭部バンドの外観になります。旧プレイヤーヘッド方式を廃止し、装着時も独自モデルを描画します。カボチャの視界オーバーレイは指定していません。既存品は通常のインベントリ判定で外観のみ更新し、固有装備の種類・シリアル・能力は保持します。ロビー展示には既存のoa:rajiモデルIDのまま反映します。実機での装着位置は未検証です。
''';p.write_text(s)
for out in [P/'source/build197.py',R/'source/build197.py']:shutil.copyfile('release_1_9_7/build197.py',out)
print('Built data-pack mask migration and complete resource pack (20 model elements).')
