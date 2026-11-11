import json,math
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
p=Path('edit/resources/assets/oa/models/item/itori.json');v=json.loads(p.read_text());palette=json.loads(Path('edit/resources/source/ITORI_PALETTE.json').read_text())
fig=plt.figure(figsize=(12,6),facecolor='#10131d')
for i,(elev,azim,title) in enumerate([(12,-65,'ITORI  /  EYE OF PERCEPTION'),(12,-20,'DEPTH & RAISED GOLD DETAIL')]):
 ax=fig.add_subplot(1,2,i+1,projection='3d',computed_zorder=False);ax.set_facecolor('#10131d')
 polys=[];cols=[]
 for e in v['elements']:
  a,b=np.array(e['from']),np.array(e['to']);P=np.array([[x,y,z] for x in [a[0],b[0]] for y in [a[1],b[1]] for z in [a[2],b[2]]]);rot=e.get('rotation')
  if rot:
   an=math.radians(rot['angle']);M=np.array([[math.cos(an),-math.sin(an),0],[math.sin(an),math.cos(an),0],[0,0,1]]);o=np.array(rot['origin']);P=(P-o)@M.T+o
  # matplotlib z is vertical: native model Y -> plot Z.
  P=P[:,[0,2,1]]
  k=int(e['faces']['north']['uv'][0]*4)//6;c=np.array(palette[min(k,9)])/255
  for ids,shade in [([0,1,3,2],.65),([4,5,7,6],.9),([0,4,6,2],.9),([1,5,7,3],1),([0,4,5,1],.7),([2,6,7,3],1)]:polys.append(P[ids]);cols.append(tuple(np.clip(c*shade,0,1)))
 coll=Poly3DCollection(polys,facecolors=cols,edgecolors='none',zsort='average');ax.add_collection3d(coll);ax.set_xlim(-2,18);ax.set_ylim(-2,18);ax.set_zlim(-2,18);ax.set_box_aspect((1,1,1));ax.view_init(elev=elev,azim=azim);ax.set_axis_off();ax.set_title(title,color='#e9d7b5',fontsize=10,pad=-10)
fig.subplots_adjust(0,0,1,1,wspace=0);out=Path('edit/resources/source/ITORI_PREVIEW.png');out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,dpi=160,facecolor=fig.get_facecolor());print(out.resolve())
