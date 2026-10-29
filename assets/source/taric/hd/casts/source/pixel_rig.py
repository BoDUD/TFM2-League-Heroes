"""Taric: source-pixel cutouts, rigid weapon/head, articulated limbs. No generated anatomy.
User explicitly chose manual pixel editing on 2026-10-29.
"""
from pathlib import Path
import json, math
from PIL import Image, ImageDraw
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=HERE.parents[1]
PACK=HERE/'inputs' if (HERE/'inputs').exists() else HERE/'pack'
OUT=HERE.parent if (HERE/'inputs').exists() else BASE/'outputs/taric-actions'
REVIEW=HERE/'diagnostics'
REVIEW.mkdir(exist_ok=True)
SRC=Image.open(PACK/'refs/design_1x.png').convert('RGBA')
Z=8
SIZE=(112,144)  # 8-pixel horizontal safety gutters during rigid-part placement

def part(points):
    mask=Image.new('L',SRC.size)
    ImageDraw.Draw(mask).polygon(points,fill=255)
    a=np.array(SRC)
    a[np.array(mask)==0]=0
    return Image.fromarray(a)

PARTS={
 'head':part([(24,0),(30,0),(34,4),(37,7),(35,11),(35,15),(32,18),(29,19),(25,18),(23,16),(20,17),(16,15),(12,16),(8,16),(8,13),(15,10),(16,6),(21,2)]),
 'torso':part([(20,17),(27,18),(32,18),(37,21),(38,27),(36,32),(37,36),(33,40),(32,49),(30,56),(24,57),(21,51),(21,43),(16,39),(17,31),(18,25)]),
 'near_shoulder':part([(4,21),(8,17),(13,15),(19,16),(20,18),(19,21),(17,24),(17,25),(14,25),(12,23),(8,24),(5,24)]),
 'far_shoulder':part([(30,16),(34,15),(39,16),(41,18),(42,20),(44,23),(43,25),(40,26),(38,23),(35,21),(33,20),(31,19)]),
 'near_upper':part([(10,23),(15,23),(18,26),(17,29),(14,32),(10,33),(7,31),(7,28),(9,26)]),
 'near_lower':part([(8,29),(13,29),(15,32),(14,35),(12,38),(12,39),(8,39),(6,37),(7,33)]),
 'near_hand':part([(8,36),(12,36),(12,39),(11,41),(8,41),(8,39),(7,38)]),
 'bare_upper':part([(37,27),(40,27),(42,29),(43,33),(42,35),(39,35),(37,32),(36,30)]),
 'bare_lower':part([(39,32),(43,32),(45,36),(46,39),(44,41),(41,39),(40,36)]),
 'bare_hand':part([(43,38),(46,38),(47,40),(47,43),(45,45),(43,45),(41,43),(42,41),(42,39)]),
 'near_thigh':part([(20,37),(24,38),(24,42),(22,46),(21,49),(18,50),(15,48),(14,46),(15,42),(18,40)]),
 'near_shin':part([(17,46),(21,46),(23,49),(22,52),(20,55),(21,58),(23,60),(23,61),(19,61),(15,61),(12,61),(12,59),(14,57),(16,54),(15,51)]),
 'far_thigh':part([(32,37),(36,38),(38,43),(39,46),(38,50),(35,51),(32,49),(32,46),(33,42)]),
 'far_shin':part([(35,47),(39,47),(40,50),(39,53),(37,56),(39,58),(42,60),(42,61),(35,61),(33,60),(32,57),(33,54),(33,51)]),
}

# Separate the original rigid hammer, including its original short grip.
weapon=Image.new('RGBA',SRC.size)
arr=np.array(SRC)
wa=np.zeros_like(arr)
ranges={38:(9,12),39:(9,12),40:(9,12),41:(3,12),42:(2,12),43:(1,12),44:(0,12),45:(0,12),46:(0,12),47:(0,12),48:(0,14),49:(0,14),50:(0,14),51:(0,14),52:(0,14),53:(0,14),54:(2,13),55:(4,13),56:(4,12),57:(4,11),58:(4,10),59:(4,9),60:(4,7)}
for y,(x0,x1) in ranges.items():wa[y,x0:x1]=arr[y,x0:x1]
PARTS['weapon']=Image.fromarray(wa)

# Remove shoulder pixels inadvertently included beneath the hair silhouette.
ha=np.array(PARTS['head'])
for y in range(14,ha.shape[0]):
 for x in range(ha.shape[1]):
  r,g,b=map(int,ha[y,x,:3])
  if x<22 and not (max(r,g,b)<45 or (r>g*1.2 and r>b*.8)):
   ha[y,x]=0
PARTS['head']=Image.fromarray(ha)

for which,box in [('near',(12,58,24,62)),('far',(32,58,43,62))]:
 x0,y0,x1,y1=box
 fa=np.zeros_like(arr);fa[y0:y1,x0:x1]=arr[y0:y1,x0:x1]
 PARTS[which+'_foot']=Image.fromarray(fa)
 sa=np.array(PARTS[which+'_shin']);sa[58:]=0
 PARTS[which+'_shin']=Image.fromarray(sa)

# Only source cloak colours, never paint a geometric substitute body.
ca=np.zeros_like(arr)
cloak_colours={(4,12,107),(12,9,74),(14,7,50),(2,17,134),(1,22,160),(6,11,184),(11,22,247),(8,53,226)}
for y in range(25,58):
 for x in range(12,48):
    if tuple(arr[y,x,:3]) in cloak_colours and arr[y,x,3]: ca[y,x]=arr[y,x]
# Trace the approved cape contour, filling only areas previously hidden by limbs.
cloak=Image.new('RGBA',SRC.size)
cd=ImageDraw.Draw(cloak)
cd.polygon([(17,26),(36,26),(39,35),(42,43),(43,49),(47,55),(45,57),(39,56),(33,56),(27,57),(21,56),(17,53),(13,47),(13,39)],fill=(22,2,22,255))
cd.polygon([(18,27),(35,27),(38,36),(41,44),(42,50),(45,55),(40,55),(33,55),(27,56),(21,55),(18,52),(14,46),(14,39)],fill=(12,9,74,255))
cloak.alpha_composite(Image.fromarray(ca))
PARTS['cape']=cloak

def vadd(a,b):return (a[0]+b[0],a[1]+b[1])
def vsub(a,b):return (a[0]-b[0],a[1]-b[1])
def rot(v,angle):
 c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
 return(c*v[0]-s*v[1],s*v[0]+c*v[1])
def bearing(v):return math.degrees(math.atan2(v[1],v[0]))
def length(v):return math.hypot(*v)
def endpoint(a,n,angle):return vadd(a,rot((n,0),angle))

def paste(canvas,name,src_anchor,dest_anchor,angle=0,ground=None):
 c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
 ax,ay=src_anchor;dx,dy=dest_anchor;dx+=8
 coeff=(c,s,ax-c*dx-s*dy,-s,c,ay+s*dx-c*dy)
 tile=PARTS[name].transform(SIZE,Image.Transform.AFFINE,coeff,resample=Image.Resampling.NEAREST)
 if ground is not None:
  # Hand-retouched cloth fold: the free cloth pools above the ground instead of cutting through it.
  ta=np.array(tile);edge=int(ground)
  for yy in range(edge,ta.shape[0]):
   dest=2*edge-yy-1
   if dest>=0:
    mask=ta[yy,:,3]>0
    ta[dest,mask]=ta[yy,mask]
  ta[edge:]=0;tile=Image.fromarray(ta)
 canvas.alpha_composite(tile)

def limb(canvas,upper,lower,srcj,destroot,upper_angle,lower_angle,hand=None):
 a,b,c=srcj
 b1=endpoint(destroot,length(vsub(b,a)),upper_angle)
 c1=endpoint(b1,length(vsub(c,b)),lower_angle)
 ra=upper_angle-bearing(vsub(b,a));rb=lower_angle-bearing(vsub(c,b))
 paste(canvas,upper,a,destroot,ra)
 paste(canvas,lower,b,b1,rb)
 if hand:paste(canvas,hand,c,c1,rb)
 return c1,rb

def bodypoint(p,pelvis,tilt):return vadd(pelvis,rot(vsub(p,(27,36)),tilt))

def pose(tag,k):
 # Absolute screen angles; source limb lengths and head/weapon sizes never change.
 p=dict(pelvis=(48,89),tilt=0,head=0,near=(105,98),bare=(74,62),legs=((108,90),(75,88)),weapon=0,cape=0,drop=None)
 if tag=='run':
    near=[(58,54),(85,90),(117,123),(145,220),(100,78),(80,37),(55,50),(58,54)][k]
    far=[(145,220),(55,10),(55,50),(58,54),(85,90),(85,80),(117,123),(145,220)][k]
    p.update(pelvis=(48,88-[0,1,0,0,1,1,0,0][k]),tilt=2,legs=(near,far),near=(113,115),bare=[(50,68),(45,46),(58,35),(75,40),(87,75),(73,82),(60,78),(50,68)][k],weapon=3,cape=[-9,-6,-3,-5,-9,-6,-3,-5][k])
 elif tag=='attack':
    arms=[(205,236),(190,202),(352,358),(25,30),(95,115),(105,98)]
    p.update(near=arms[k],bare=[(40,30),(45,35),(75,70),(30,345),(55,65),(74,62)][k],weapon=[100,78,-105,-80,15,0][k],legs=((121,82),(53,83)),tilt=[-4,-1,7,10,3,0][k])
 elif tag=='attack_p':
    p.update(near=[(208,212),(242,262),(18,30),(31,44),(188,155),(105,98)][k],bare=[(38,25),(65,70),(0,315),(0,315),(50,40),(74,62)][k],weapon=[98,180,-75,-85,78,0][k],legs=((140,81),(52,88)),tilt=[-3,-3,16,22,3,0][k])
 elif tag=='skill':
    p.update(near=[(210,235),(12,30),(352,356),(350,354),(8,285),(105,98)][k],bare=[(345,300),(225,280),(220,280),(220,278),(50,70),(74,62)][k],weapon=[120,-95,-110,-110,-110,0][k],legs=((120,86),(61,87)),tilt=[-4,4,6,7,3,0][k])
 elif tag=='skill2':
    p.update(bare=[(145,218),(325,310),(305,285),(305,285),(345,320),(140,215)][k],near=(105,98),weapon=0,head=[0,-2,-3,-3,-1,0][k])
 elif tag=='ult':
    p.update(near=[(105,98),(320,310),(255,270),(255,270),(255,270),(255,270),(105,98)][k],bare=[(74,62),(25,330),(15,330),(15,330),(15,330),(15,330),(74,62)][k],weapon=[0,180,180,180,180,180,0][k],legs=((117,87),(67,87)),tilt=[0,-5,-4,-4,-4,-4,0][k],head=[0,-6,-7,-7,-7,-7,0][k])
 elif tag=='hit':p.update(tilt=-12 if k==0 else 0,near=(116,105) if k==0 else(105,98),bare=(354,350) if k==0 else(74,62),legs=((121,89),(60,85)))
 elif tag=='dead':
    p.update(pelvis=[(48,89),(43,91),(40,95),(40,101),(40,103),(40,104),(39,105),(39,105)][k],tilt=[-12,-24,-32,12,30,45,60,65][k],head=[-8,-12,-18,10,20,25,25,28][k],near=[(115,110),(120,110),(115,90),(100,80),(75,80),(65,55),(40,50),(40,50)][k],bare=[(10,345),(350,345),(350,350),(55,65),(45,65),(45,75),(35,80),(35,80)][k],legs=[((120,85),(60,85)),((130,90),(35,90)),((145,20),(35,86)),((130,350),(50,160)),((145,345),(55,160)),((145,345),(55,160)),((145,345),(55,160)),((145,345),(55,160))][k],drop=None if k==0 else[(0,0,0),(84,54,0),(85,69,10),(85,86,0),(85,108,270),(85,108,270),(85,108,270),(85,108,270)][k])
 return p

def render(tag,k):
 p=pose(tag,k);canvas=Image.new('RGBA',SIZE)
 if tag=='attack_p' and k in (2,3):
  p.update(legs=((170,80),(-10,80)),near=(45,50) if k==2 else(50,55),weapon=-35 if k==2 else-45)
 if tag=='dead' and k>=5:p['bare']=(-5,15) if k==5 else(0,0)
 if tag=='dead' and k==4:p['bare']=(45,40)
 if tag=='dead' and k>=4:p['drop']=(89,108,270)
 if tag=='dead' and k>=3:p['legs']=(p['legs'][0],(180,0))
 if tag=='dead' and k in (0,1):p['pelvis']=(p['pelvis'][0],88)
 if tag=='dead' and k>=5:p['pelvis']=(p['pelvis'][0],103)
 raised=(tag=='skill2' and k in (2,3)) or (tag=='skill' and k in (1,2,3))
 if raised:p['bare']=(270,270 if k==2 else 268)
 if tag=='ult' and k in (3,5):p['head']=-6;p['bare']=(15,328)
 pelvis=p['pelvis'];tilt=p['tilt']
 feet=Image.new('RGBA',SIZE)
 # Legs use fixed source segment lengths. Set standing feet on the original baseline.
 farhip=bodypoint((34,39),pelvis,tilt);nearhip=bodypoint((21,39),pelvis,tilt)
 # Resolve both feet before the free cloth so its hem can fold against the same floor.
 farankle=endpoint(endpoint(farhip,length((2,9)),p['legs'][1][0]),11,p['legs'][1][1])
 nearankle=endpoint(endpoint(nearhip,length((-3,9)),p['legs'][0][0]),11,p['legs'][0][1])
 paste(feet,'far_foot',(36,59),farankle,0)
 paste(feet,'near_foot',(18,59),nearankle,0)
 floor=feet.getbbox()[3] if tag!='dead' else 115
 farankle,farangle=limb(canvas,'far_thigh','far_shin',[(34,39),(36,48),(36,59)],farhip,*p['legs'][1])
 paste(canvas,'far_foot',(36,59),farankle,0)
 paste(canvas,'cape',(27,36),pelvis,tilt+p['cape'],ground=floor)
 nearankle,nearangle=limb(canvas,'near_thigh','near_shin',[(21,39),(18,48),(18,59)],nearhip,*p['legs'][0])
 paste(canvas,'near_foot',(18,59),nearankle,0)
 # Far arm may pass behind torso/hair; its joint chain is still constructed continuously.
 farroot=bodypoint((38,17) if raised else(38,26),pelvis,tilt)
 barew,ba=limb(canvas,'bare_upper','bare_lower',[(38,27),(40,33),(43,38)],farroot,*p['bare'],hand='bare_hand')
 paste(canvas,'torso',(27,36),pelvis,tilt,ground=floor)
 # The near shoulder advances with the torso's cross-body sweep, rather than stretching the arm/handle.
 reach=(tag in ('attack','attack_p') and k in (2,3)) or (tag=='skill' and k in (1,2,3,4))
 near_shoulder_x=18 if reach else 13
 nearroot=bodypoint((near_shoulder_x,24),pelvis,tilt)
 wrist,na=limb(canvas,'near_upper','near_lower',[(13,24),(11,31),(10,38)],nearroot,*p['near'],hand='near_hand')
 # Hand-source grip at y40: position the same rigid weapon at the same fixed hand socket.
 grip=vadd(wrist,rot((0,0 if tag=='hit' and k==0 else 1),na))
 weapon_front=(tag in ('attack','attack_p') and k in (2,3)) or (tag=='skill' and k in (1,2,3,4))
 if p['drop'] is None and not weapon_front:paste(canvas,'weapon',(10,40),grip,p['weapon'])
 elif p['drop'] is not None:
    wx,wy,wa=p['drop'];paste(canvas,'weapon',(6,52),(wx,wy),wa)
 paste(canvas,'near_hand',(10,38),wrist,na)
 paste(canvas,'far_shoulder',(38,23),bodypoint((38,17) if raised else(38,23),pelvis,tilt),tilt)
 paste(canvas,'near_shoulder',(13,21),bodypoint((near_shoulder_x,21),pelvis,tilt),tilt)
 neck=bodypoint((27,18),pelvis,tilt)
 paste(canvas,'head',(27,18),neck,tilt+p['head'])
 if weapon_front:
  paste(canvas,'weapon',(10,40),grip,p['weapon'])
  paste(canvas,'near_hand',(10,38),wrist,na)
 # Normalize the planted foot, using leg geometry only, never scaling the actor.
 if tag!='dead':
    fb=feet.getbbox()
    if fb:
       dy=115-fb[3]
       shifted=Image.new('RGBA',SIZE);shifted.alpha_composite(canvas,(0,dy));canvas=shifted
 bbox=canvas.getbbox();left=8
 if bbox and bbox[0]<10:left=max(0,bbox[0]-2)
 if bbox and bbox[2]>left+94:left=min(16,bbox[2]+2-96)
 canvas=canvas.crop((left,0,left+96,128))
 # Remove isolated 1-6 pixel seam specks only, never whole limbs or the death weapon.
 a=np.array(canvas);m=a[:,:,3]>0;seen=np.zeros(m.shape,bool)
 for y,x in zip(*np.nonzero(m)):
  if seen[y,x]:continue
  todo=[(int(y),int(x))];seen[y,x]=True;pts=[]
  while todo:
   yy,xx=todo.pop();pts.append((yy,xx))
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     ny,nx=yy+dy,xx+dx
     if 0<=ny<128 and 0<=nx<96 and m[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
  if len(pts)<=6:
   for yy,xx in pts:a[yy,xx]=0
 canvas=Image.fromarray(a)
 return canvas,p

def export():
 (OUT/'logical').mkdir(parents=True,exist_ok=True)
 (OUT/'rig-parts').mkdir(exist_ok=True)
 for name,im in PARTS.items():im.save(OUT/'rig-parts'/f'{name}.png')
 SRC.save(OUT/'logical/design.png')
 spec=json.loads((PACK/'sheets.json').read_text())
 log=[]
 for s in spec['sheets']:
    cells=[]
    for fr in s['frames']:
      im,p=render(s['tag'],fr-1);cells.append(im)
      log.append(dict(tag=s['tag'],frame=fr,pose=p))
    logical=Image.new('RGBA',(192,128))
    if len(cells)==1:logical.alpha_composite(cells[0],(48,0))
    else:
     for k,im in enumerate(cells):logical.alpha_composite(im,(k*96,0))
    logical.save(OUT/'logical'/(s['name']+'.png'))
    big=logical.resize((1536,1024),Image.Resampling.NEAREST)
    final=Image.new('RGBA',big.size);final.alpha_composite(big,(0,4));final.save(OUT/(s['name']+'.png'))
 (OUT/'rig-poses.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
 # Source component preview, not a production animation.
 names=list(PARTS)
 preview=Image.new('RGBA',(48*4,80*math.ceil(len(names)/4)),(110,115,105,255))
 dr=ImageDraw.Draw(preview)
 for i,name in enumerate(names):
  x=(i%4)*48;y=(i//4)*80
  preview.alpha_composite(PARTS[name],(x,y+12));dr.text((x,y),name,fill='white')
 preview.resize((preview.width*4,preview.height*4),Image.Resampling.NEAREST).save(REVIEW/'parts-review.png')
 print('Exported',len(spec['sheets']),'sheets and',len(log),'frames')

if __name__=='__main__':export()
