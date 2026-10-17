from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,shutil,collections,numpy as np,zipfile
BASE=Path(__file__).resolve().parent
WORK=BASE; OUT=BASE
for sub in ['pixel_1x','raw','previews','prompts']:(OUT/sub).mkdir(parents=True,exist_ok=True)
jobs=json.loads((WORK/'source_jobs.json').read_text(encoding='utf-8'))
bindings=json.loads((WORK/'source_bindings.json').read_text(encoding='utf-8-sig'))
manifest=[]; checks=[]
for j,b in zip(jobs,bindings):
 name=j['name']; raw=OUT/'raw'/f'{name}.png'
 if not raw.exists():continue
 (OUT/'prompts'/f'{name}.txt').write_text(j['prompt'],encoding='utf-8')
 colors=list(dict.fromkeys(re.findall(r'#[0-9A-Fa-f]{6}',j['prompt'].split('Effect:')[0])))
 pal=np.array([tuple(bytes.fromhex(c[1:])) for c in colors],dtype=np.int32)
 a=np.array(Image.open(raw).convert('RGBA'));H,W=a.shape[:2]
 # Quantize first, then take most frequent transparent/palette class per virtual logical grid block.
 opaque=(a[:,:,3]>=128)&(a[:,:,:3].max(axis=2)>15)
 rgb=a[:,:,:3].astype(np.int32);dist=((rgb[:,:,None,:]-pal[None,None,:,:])**2).sum(axis=3)
 idx=dist.argmin(axis=2)+1;idx[~opaque]=0
 frames=[]; edits=[]
 for f in range(j['n']):
  c=f%j['cols'];r=f//j['cols'];w=j['w'];h=j['h'];p=np.zeros((h,w),dtype=np.int32)
  for y in range(h):
   for x in range(w):
    x0=round((c*w+x)*W/(j['cols']*w));x1=round((c*w+x+1)*W/(j['cols']*w))
    y0=round((r*h+y)*H/(j['rows']*h));y1=round((r*h+y+1)*H/(j['rows']*h))
    votes=np.bincount(idx[y0:y1,x0:x1].flatten(),minlength=len(pal)+1)
    coverage=0.12 if name=='e_stun' else (0.25 if name=='p_heal' else 0.5)
    if votes[1:].sum()>=votes.sum()*coverage:p[y,x]=votes[1:].argmax()+1
  if name in ['q_barrel','r_cask']:
   yy,xx=np.where(p>0)
   if len(yy):
    dy=round(h/2-(yy.min()+yy.max()+1)/2); q=np.zeros_like(p)
    ya=max(0,-dy);yb=min(h,h-dy);q[ya+dy:yb+dy]=p[ya:yb];p=q
  if name in ['q_barrel','r_cask']:
   yy,xx=np.where(p>0)
   if len(xx):
    dx=w-2-xx.max();q=np.zeros_like(p);xa=max(0,-dx);xb=min(w,w-dx);q[:,xa+dx:xb+dx]=p[:,xa:xb];p=q
  if name=='q_land':
   yy,xx=np.where(p>0)
   if len(yy):
    dy=h-1-yy.max()-(1 if f%2==0 else 0);q=np.zeros_like(p);ya=max(0,-dy);yb=min(h,h-dy);q[ya+dy:yb+dy]=p[ya:yb];p=q
  if name=='p_heal':
   q=np.zeros_like(p);q[:,:w//2-2]=p[:,2:w//2];p=q
  axis=0 if name in ['q_barrel','r_cask'] else 1
  # The requested exact symmetry uses the upper/left half as authoritative.
  if axis==1:p[:,w//2:]=p[:,:w//2][:,::-1]
  else:p[h//2:,:]=p[:h//2,:][::-1,:]
  # Clear the explicit actor silhouette channels.
  clear={'w_drink':8,'p_heal':12}.get(name)
  if clear:p[:,(w-clear)//2:(w+clear)//2]=0
  if name=='w_on':p[h-40:h,(w-26)//2:(w+26)//2]=0
  # No dark perimeter on ephemeral VFX: remove only deepest ramp pixels on exposed edges.
  if name not in ['q_barrel','r_cask','q_land','q_boom','r_boom']:
   deepest=len(pal)
   for y,x in zip(*np.where(p==deepest)):
    neighbors=[p[yy,xx] for yy,xx in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)] if 0<=yy<h and 0<=xx<w]
    if 0 in neighbors:p[y,x]=max(1,deepest-1)
  rgba=np.zeros((h,w,4),dtype=np.uint8)
  for k,color in enumerate(pal,1):rgba[p==k]=[*color,255]
  frames.append(Image.fromarray(rgba))
 sheet=Image.new('RGBA',(j['n']*w,h))
 for f,im in enumerate(frames):sheet.paste(im,(f*w,0))
 fname=f'gragas_fx_{name}.png';sheet.save(OUT/'pixel_1x'/fname);sheet.resize((sheet.width*8,h*8),Image.Resampling.NEAREST).save(OUT/fname)
 previews=[]
 for im in frames:
  tile=Image.new('RGBA',(max(w,64),max(h,64)),(20,26,36,255));tile.alpha_composite(im,((tile.width-w)//2,(tile.height-h)//2))
  previews.append(tile.resize((tile.width*4,tile.height*4),Image.Resampling.NEAREST).convert('RGB'))
 previews[0].save(OUT/'previews'/f'{name}.gif',save_all=True,append_images=previews[1:],duration=120,loop=0,disposal=2)
 alpha=np.array(sheet)[:,:,3];sym=all(np.array_equal(np.array(im),np.flip(np.array(im),axis=axis)) for im in frames)
 nonempty=[im.getbbox() is not None for im in frames]
 check=dict(name=name,frames=len(frames),size_1x=list(sheet.size),size_8x=[sheet.width*8,h*8],symmetry='top-bottom' if axis==0 else 'left-right',symmetry_pass=sym,binary_alpha=bool(np.isin(alpha,[0,255]).all()),all_frames_nonempty=all(nonempty),frame_bboxes=[im.getbbox() for im in frames])
 checks.append(check)
 manifest.append(dict(name=name,file=fname,logical_cell=[w,h],frames=j['n'],layout='horizontal',scale=8,raw_layout=[j['cols'],j['rows']],raw_size=[W,H],binding=b['binding'],game_size=b['size'],symmetry=check['symmetry'],preview_duration_ms=120,timing_status='preview only; runtime timing not provided'))
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
# Visual audit: all 77 frames on a dark background, labeled by sheet name.
contact=Image.new('RGB',(1180,16*185),(20,26,36));d=ImageDraw.Draw(contact)
for row,j in enumerate(jobs):
 name=j['name'];path=OUT/'pixel_1x'/f'gragas_fx_{name}.png'
 if not path.exists():continue
 s=Image.open(path).convert('RGBA');w=j['w'];h=j['h'];d.text((10,row*185+5),f'{name}  {j["n"]} frames  {w}x{h}',fill=(240,240,240))
 sc=min(4,145//max(w,h))
 for f in range(j['n']):
  im=s.crop((f*w,0,(f+1)*w,h)).resize((w*sc,h*sc),Image.Resampling.NEAREST)
  contact.paste(im,(20+f*163+(150-im.width)//2,row*185+30+(145-im.height)//2),im)
contact.save(OUT/'contact.png')
print(json.dumps({'completed':len(manifest),'frames':sum(x['frames'] for x in manifest),'checks':checks},ensure_ascii=False))

