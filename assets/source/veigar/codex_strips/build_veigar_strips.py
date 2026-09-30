"""Pose the approved pixel artwork using original-color raster layers.

Image-gen action drafts supply gesture studies. Final geometry is repaired with
the approved source pixels so generation cannot redesign the character. No
geometric surrogate bodies, new palettes, or smooth resampling are used.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json, math, hashlib, shutil
from collections import deque

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'work/strips-reference/veigar_strips_pack'
OUT=ROOT/'outputs/veigar-strips'
WORK=ROOT/'work/strips-build'
OUT.mkdir(parents=True,exist_ok=True); WORK.mkdir(parents=True,exist_ok=True)
CELLS=json.loads((REF/'veigar_cells.json').read_text())
BASE=np.array(Image.open(REF/'design/veigar_design_1x.png').convert('RGBA'))
HEAD=np.array(Image.open(REF/'design/veigar_head_1x.png').convert('RGBA'))
HEIGHT,WIDTH=BASE.shape[:2]
Y,X=np.mgrid[:HEIGHT,:WIDTH]
EYES=[(255,209,50),(255,242,138)]
PALETTE=set(map(tuple,BASE[BASE[:,:,3]>0,:3]))
HEADMASK=HEAD[:,:,3]>0
BODYMASK=(BASE[:,:,3]>0)&~HEADMASK

# Mutually exclusive original-pixel layers; summing them reconstructs BASE.
MASKS={}
MASKS['head']=HEADMASK
remaining=BODYMASK.copy()
for name,mask in [
 ('near_leg',(Y>=96)&(X<65)),
 ('far_leg',(Y>=96)&(X>=65)),
 ('staff_hand',((X<=55)&(Y<=87))|((X<=57)&(Y>=88))),
 ('far_arm',(X>=72)&(Y<=89)),
 ('near_arm',(X<=60)&(Y>=79)&(Y<=91)),
]:
 m=remaining&mask; MASKS[name]=m; remaining &= ~m
MASKS['torso']=remaining
LAYERS={}
for n,m in MASKS.items():
 a=np.zeros_like(BASE); a[m]=BASE[m]; LAYERS[n]=a
 assert not (n!='head' and any(np.any(np.all(a[:,:,:3]==e,axis=2)&(a[:,:,3]>0)) for e in EYES))
rebuild=np.zeros_like(BASE)
for a in LAYERS.values(): rebuild[a[:,:,3]>0]=a[a[:,:,3]>0]
assert np.array_equal(rebuild,BASE)

def matrix(angle=0,pivot=(0,0),delta=(0,0)):
 a=math.radians(angle); c,s=math.cos(a),math.sin(a)
 px,py=pivot; dx,dy=delta
 return np.array([[c,-s,px-c*px+s*py+dx],[s,c,py-s*px-c*py+dy],[0,0,1]],float)

def warp(layer,m):
 inv=np.linalg.inv(m)
 coeff=tuple(inv[:2].reshape(-1))
 return np.array(Image.fromarray(layer).transform((128,128),Image.Transform.AFFINE,coeff,Image.Resampling.NEAREST))

def over(dst,src):
 m=src[:,:,3]>0; dst[m]=src[m]

def segment_matrix(a,b,c,d):
 """Similarity warp an original sleeve between two specified joint pairs."""
 a,b,c,d=map(lambda x:np.array(x,dtype=float),(a,b,c,d))
 u=b-a; v=d-c
 scale=np.linalg.norm(v)/max(1,np.linalg.norm(u))
 # Keep the original sleeve thickness and texture at roughly native scale.
 scale=max(.78,min(1.5,scale))
 angle=math.atan2(v[1],v[0])-math.atan2(u[1],u[0])
 co,si=math.cos(angle)*scale,math.sin(angle)*scale
 A=np.array([[co,-si],[si,co]])
 t=c-A@a
 return np.array([[A[0,0],A[0,1],t[0]],[A[1,0],A[1,1],t[1]],[0,0,1]])

def pose(**kw):
 return dict(body=(0,0),body_angle=0,head=(0,0),head_angle=0,
             hand=(52,83),staff_angle=0,far_angle=0,far_delta=(0,0),
             near_leg=(0,0,0),far_leg=(0,0,0),squint=False,
             ground=81,air=0,whole_angle=0,exact=False,**kw)

def P(**kw):
 d=pose(); d.update(kw); return d

# Pose stages follow the supplied LoL references and the reviewed image-gen drafts.
# Uniform artwork scale; all listed offsets are native game pixels.
POSES={
 'run':[
  P(near_leg=(3,0,-12),far_leg=(-2,-2,14),far_angle=3),
  P(body=(0,-1),head=(0,-1),hand=(52,82),near_leg=(2,-1,4),far_leg=(-1,0,-9),far_angle=-2),
  P(body=(0,-2),head=(0,-2),hand=(52,81),near_leg=(0,-2,17),far_leg=(0,-2,-3),far_angle=-4),
  P(body=(0,-1),head=(0,-1),hand=(52,82),near_leg=(-1,-1,8),far_leg=(2,-1,-9),far_angle=-1),
  P(near_leg=(-2,-2,14),far_leg=(3,0,-12),far_angle=3),
  P(body=(0,-1),head=(0,-1),hand=(52,82),near_leg=(-1,0,-9),far_leg=(2,-1,4),far_angle=5),
  P(body=(0,-2),head=(0,-2),hand=(52,81),near_leg=(0,-2,-3),far_leg=(0,-2,17),far_angle=5),
  P(body=(0,-1),head=(0,-1),hand=(52,82),near_leg=(2,0,-9),far_leg=(-1,-1,8),far_angle=2),
 ],
 'attack':[
  P(exact=True),
  P(body=(-1,0),head=(-1,0),hand=(54,77),staff_angle=18,far_angle=-10),
  P(body=(-1,1),head=(-1,1),hand=(55,78),staff_angle=-38,far_angle=-12),
  P(body=(1,1),head=(1,1),hand=(64,83),staff_angle=90,far_angle=-8,far_delta=(2,0),near_leg=(-1,0,0),far_leg=(2,0,0)),
  P(body=(1,0),head=(1,0),hand=(63,83),staff_angle=84,far_angle=-5,far_delta=(2,0),far_leg=(1,0,0)),
  P(exact=True),
 ],
 'skill':[
  P(exact=True),
  P(body=(-1,2),head=(-1,2),hand=(53,87),staff_angle=-75,far_angle=-4,near_leg=(-1,0,0)),
  P(body=(-1,3),head=(-1,3),hand=(52,87),staff_angle=-92,far_angle=-10,near_leg=(-2,0,0)),
  P(body=(2,2),head=(2,2),hand=(65,84),staff_angle=92,far_angle=-6,far_delta=(3,0),near_leg=(-2,0,0),far_leg=(3,0,-4)),
  P(body=(2,1),head=(2,1),hand=(64,84),staff_angle=90,far_angle=-3,far_delta=(3,0),near_leg=(-1,0,0),far_leg=(2,0,0)),
  P(exact=True),
 ],
 'skill2':[
  P(exact=True),
  P(hand=(53,77),staff_angle=26,far_angle=-8),
  P(body=(0,2),head=(0,2),hand=(54,83),staff_angle=-66,far_angle=9),
  P(body=(0,2),head=(0,2),hand=(53,84),staff_angle=-125,far_angle=3),
  P(body=(-1,0),head=(-1,0),hand=(49,84),staff_angle=-95,far_angle=12),
  P(hand=(51,83),staff_angle=-34,far_angle=5),
  P(exact=True),
 ],
 'ult':[
  P(body=(0,1),head=(0,1),hand=(52,84),far_angle=3),
  P(body=(0,3),head=(0,3),hand=(54,84),staff_angle=12,far_angle=11),
  P(body=(0,-5),head=(0,-5),hand=(54,76),staff_angle=8,far_angle=-18,near_leg=(1,-7,14),far_leg=(-1,-5,-12),air=4),
  P(body=(0,-10),head=(0,-10),hand=(55,62),staff_angle=16,far_angle=-30,far_delta=(2,-7),near_leg=(2,-10,24),far_leg=(-1,-9,-18),air=9),
  P(body=(0,-2),head=(0,-2),hand=(53,79),staff_angle=6,far_angle=-7,near_leg=(1,-1,8),far_leg=(-1,-2,-8)),
  P(body=(0,3),head=(0,3),hand=(52,85),staff_angle=-8,far_angle=10),
  P(exact=True),
 ],
 'hit':[
  P(body=(-2,0),head=(-3,0),hand=(50,82),staff_angle=-8,far_angle=-8,far_delta=(-1,0),squint=True),
  P(exact=True),
 ],
 'dead':[
  P(exact=True),
  P(body=(-2,0),head=(-3,0),hand=(51,84),staff_angle=-28,far_angle=-14,near_leg=(1,-1,15)),
  P(body=(-2,2),head=(-3,2),hand=(51,86),staff_angle=-60,far_angle=-25,near_leg=(2,-1,22)),
  P(body=(-1,4),head=(-2,4),hand=(51,87),staff_angle=-80,far_angle=18,near_leg=(2,0,28),far_leg=(1,0,-18)),
  P(hand=(52,85),staff_angle=-75,whole_angle=-32,far_angle=15),
  P(hand=(52,85),staff_angle=-55,whole_angle=-58,far_angle=65,ground=83),
  P(hand=(52,84),staff_angle=-20,whole_angle=-79,far_angle=100,ground=83),
  P(hand=(52,84),staff_angle=-10,whole_angle=-88,far_angle=118,ground=83),
 ]}

def components(alpha):
 pts=set(zip(*np.where(alpha))); groups=[]
 while pts:
  start=pts.pop(); group=[start]; q=[start]
  while q:
   y,x=q.pop()
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     z=(y+dy,x+dx)
     if z in pts: pts.remove(z);q.append(z);group.append(z)
  groups.append(group)
 return sorted(groups,key=len,reverse=True)

def render_source(p):
 if p['exact']:return BASE.copy(),HEAD.copy()
 dst=np.zeros_like(BASE)
 bx,by=p['body']
 # Far limbs sit behind the torso; original pixels remain the only paint source.
 for name,anchor,params in [('far_leg',(70,96),p['far_leg']),('near_leg',(59,96),p['near_leg'])]:
  dx,dy,a=params
  over(dst,warp(LAYERS[name],matrix(a,anchor,(dx,dy))))
 far_m=matrix(p['far_angle'],(71,83),(bx+p['far_delta'][0],by+p['far_delta'][1]))
 over(dst,warp(LAYERS['far_arm'],far_m))
 over(dst,warp(LAYERS['torso'],matrix(p['body_angle'],(65,88),p['body'])))
 # Sleeve is texture-preserving and driven by shoulder/grip joint endpoints.
 near_m=segment_matrix((59,82),(53,84),(59+bx,82+by),p['hand'])
 over(dst,warp(LAYERS['near_arm'],near_m))
 weapon_m=matrix(p['staff_angle'],(52,83),(p['hand'][0]-52,p['hand'][1]-83))
 over(dst,warp(LAYERS['staff_hand'],weapon_m))
 head=HEAD.copy()
 if p['squint']:
  for e in EYES:
   em=np.all(head[:,:,:3]==e,axis=2)&(head[:,:,3]>0)&(Y==75)
   head[em]=(17,16,32,255)
 hm=matrix(p['head_angle'],(65,76),p['head'])
 head=warp(head,hm)
 over(dst,head)
 if p['whole_angle']:
  wm=matrix(p['whole_angle'],(65,90))
  dst=warp(dst,wm); head=warp(head,wm)
 # Remove isolated single-pixel transform artifacts only; never bulk-draw a body.
 for group in components(dst[:,:,3]>0)[1:]:
  if len(group)<=2:
   for yy,xx in group:
    if head[yy,xx,3]==0: dst[yy,xx]=0
 return dst,head

def place(src,head,p,pivot,tag,index):
 # Reference approved idle transform: original (74,88) maps to cell pivot.
 tx=pivot[0]-74; ty=pivot[1]-88
 yy,xx=np.where(src[:,:,3]>0)
 bottom=int(yy.max())+ty
 # Keep jump lift; crouched feet stay planted. Run's head bob stays unmodified.
 if tag=='dead' and p['whole_angle']:
  ty += p['ground']-bottom
 elif bottom>p['ground']:
  # Feet occasionally gain a rotated-outline pixel; cut that extremity at the
  # floor rather than shifting the whole head/body and introducing run jitter.
  pass
 frame=np.zeros((96,96,4),dtype=np.uint8)
 hm=np.zeros_like(frame)
 for target,layer in [(frame,src),(hm,head)]:
  sy,sx=np.where(layer[:,:,3]>0); nx=sx+tx;ny=sy+ty
  ok=(nx>=0)&(nx<96)&(ny>=0)&(ny<=p['ground'])
  target[ny[ok],nx[ok]]=layer[sy[ok],sx[ok]]
 return frame,hm,[tx,ty]

GRIDS={'idle':(3,2),'run':(4,2),'attack':(3,2),'skill':(3,2),'skill2':(3,3),'ult':(4,2),'hit':(2,1),'dead':(4,2)}
ALL={}; HEADS={}; META={}
for tag,poses in POSES.items():
 frames=[]; heads=[];meta=[]
 for i,p in enumerate(poses):
  src,head=render_source(p)
  frame,hm,shift=place(src,head,p,CELLS['tags'][tag][i]['pivot'],tag,i)
  frames.append(frame);heads.append(hm);meta.append({'pose':p,'translation':shift})
 ALL[tag]=frames; HEADS[tag]=heads;META[tag]=meta
idle=np.array(Image.open(REF/'veigar_idle.png').convert('RGBA'))[::8,::8]
ALL['idle']=[idle[(i//3)*96:(i//3+1)*96,(i%3)*96:(i%3+1)*96].copy() for i in range(6)]

# Diagnostic source layers and native contact sheet before final export.
contact=Image.new('RGB',(8*240,8*264),'#242936');d=ImageDraw.Draw(contact)
order=['idle','run','attack','skill','skill2','ult','hit','dead']
for row,tag in enumerate(order):
 for i,fr in enumerate(ALL[tag]):
  im=Image.fromarray(fr)
  # Preview is centered on the input pivot so translations do not look like jitter.
  pivot=CELLS['tags'][tag][i]['pivot']
  crop=im.crop((pivot[0]-44,30,pivot[0]+36,86))
  zoom=crop.resize((240,168),Image.Resampling.NEAREST)
  contact.paste(zoom,(i*240,row*264+36),zoom)
  d.text((i*240+8,row*264+12),f'{tag} {i+1} / {CELLS["tags"][tag][i]["ms"]}ms',fill='#ECEDF4',font_size=16)
  cs=components(fr[:,:,3]>0)
  d.text((i*240+8,row*264+216),'parts '+','.join(str(len(c)) for c in cs),fill='#ADB5C5',font_size=12)
contact.save(WORK/'contact.png')
np.savez_compressed(WORK/'frames.npz',**{tag:np.array(fr) for tag,fr in ALL.items()})
np.savez_compressed(WORK/'heads.npz',**{tag:np.array(fr) for tag,fr in HEADS.items()})
(WORK/'pose_metadata.json').write_text(json.dumps(META,indent=2))
for name,layer in LAYERS.items():
 im=Image.fromarray(layer); box=im.getbbox(); im.crop(box).resize(((box[2]-box[0])*12,(box[3]-box[1])*12),Image.Resampling.NEAREST).save(WORK/(name+'.png'))
print('Built',sum(map(len,ALL.values())),'frames. Component sizes:')
for tag,frames in ALL.items():
 print(tag,[list(map(len,components(fr[:,:,3]>0))) for fr in frames])
