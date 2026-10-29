from pathlib import Path
from collections import deque
import json
import numpy as np
from PIL import Image, ImageDraw
import pixel_rig as rig

def components(a):
 m=a[:,:,3]>0;seen=np.zeros_like(m);found=[]
 for y,x in zip(*np.nonzero(m)):
  if seen[y,x]:continue
  todo=[(int(y),int(x))];seen[y,x]=True;pts=[]
  while todo:
   yy,xx=todo.pop();pts.append((yy,xx))
   for dy in (-1,0,1):
    for dx in (-1,0,1):
     ny,nx=yy+dy,xx+dx
     if 0<=ny<m.shape[0] and 0<=nx<m.shape[1] and not seen[ny,nx] and m[ny,nx]:seen[ny,nx]=True;todo.append((ny,nx))
  found.append(pts)
 return sorted(found,key=len,reverse=True)

spec=json.loads((rig.PACK/'sheets.json').read_text())
palette=set(map(tuple,np.asarray(rig.SRC)[np.asarray(rig.SRC)[:,:,3]>0,:3].tolist()))
rows=[]
previews={}
for s in spec['sheets']:
 for fr,ms in zip(s['frames'],s['ms']):
  im,p=rig.render(s['tag'],fr-1)
  a=np.array(im);comps=components(a)
  rows.append({'action':s['tag'],'frame':fr,'head_source':'rig-parts/head.png','weapon_source':'rig-parts/weapon.png','alpha_binary':bool(np.isin(a[:,:,3],[0,255]).all()),'palette_exact':all(tuple(c) in palette for c in a[a[:,:,3]>0,:3].tolist()),'component_sizes':[len(c) for c in comps],'bbox':im.getbbox()})
  bg=Image.new('RGBA',im.size,(118,125,112,255));bg.alpha_composite(im)
  frame=bg.convert('RGB').resize((384,512),Image.Resampling.NEAREST)
  previews.setdefault(s['tag'],[]).append((frame,ms))
(rig.OUT/'previews').mkdir(exist_ok=True)
for tag,frames in previews.items():
 frames[0][0].save(rig.OUT/'previews'/(tag+'.gif'),save_all=True,append_images=[im for im,ms in frames[1:]],duration=[ms for im,ms in frames],loop=0,disposal=2)
(rig.OUT/'pixel-QA.json').write_text(json.dumps({'frames':rows,'sheets':len(spec['sheets']),'frame_count':len(rows)},indent=2),encoding='utf8')
print(json.dumps([{k:r[k] for k in ('action','frame','component_sizes')} for r in rows]))
