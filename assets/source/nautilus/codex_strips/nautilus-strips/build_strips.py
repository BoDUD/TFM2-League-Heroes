from pathlib import Path
import json, shutil, math, hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
PORTABLE=(Path(__file__).parent/'design').is_dir()
SRC=Path(__file__).parent if PORTABLE else ROOT/'work/nautilus_strips_pack/nautilus_strips_pack'
OUT=Path(__file__).parent if PORTABLE else ROOT/'outputs/nautilus-strips'
OUT.mkdir(exist_ok=True,parents=True)
A=np.array(Image.open(SRC/'design/nautilus_design_1x.png').convert('RGBA'))
HEAD=np.array(Image.open(SRC/'design/nautilus_head_1x.png').convert('RGBA'))
PAL=sorted(set(map(tuple,A[A[:,:,3]>0,:3])))
C=lambda h:tuple(bytes.fromhex(h))+ (255,)
INK=C('070211'); DARK=C('2D3041'); MID=C('3D4150'); GRAY=C('70747A'); BRONZE=C('8C3815'); LIGHT=C('DC741C')
CELLS=json.loads((SRC/'nautilus_cells.json').read_text(encoding='utf-8'))
def blank():return Image.new('RGBA',(128,128))
def cut(mask):
    a=A.copy();a[~mask]=0; return Image.fromarray(a)
Y,X=np.indices((128,128))
# Approved anchor silhouette: crown/flukes above the hood, left shaft and rope.
wm=((Y<=62)|((Y>=63)&(Y<=74)&(X<=55))|((Y>=63)&(Y<=67)&(X>=75))|((Y>=75)&(X>=49)&(X<=53))) & (A[:,:,3]>0)
weapon=cut(wm)
# Reconstruct the shaft hidden by the idle glove, using its existing iron colours.
wd=ImageDraw.Draw(weapon)
wd.rectangle((50,82,53,85),fill=DARK);wd.line((51,82,51,85),fill=GRAY,width=1)
W=np.array(weapon)
core=A.copy();core[wm]=0
core[(X<=55)&(Y>=74)&(Y<=89)]=0
core[(X>=76)&(Y>=74)&(Y<=90)]=0
core[Y>=90]=0
core[HEAD[:,:,3]>0]=HEAD[HEAD[:,:,3]>0]
CORE=Image.fromarray(core)
L=cut((Y>=90)&(X>=54)&(X<=64)); R=cut((Y>=90)&(X>=69)&(X<=80))
GLOVE=cut((Y>=84)&(Y<=89)&(X>=77)&(X<=81)).crop((77,84,82,90))
def shifted(im,dx,dy):
    q=blank();q.alpha_composite(im,(int(dx),int(dy)));return q
def part(im):
    b=im.getbbox();return im.crop(b),b
WP,WB=part(weapon)
def anchor(dst,grip=(51,83),rot=0):
    p=WP.copy();jx,jy=51-WB[0],83-WB[1]
    crown=(64-WB[0],56-WB[1])
    for _ in range(rot%4):
        h=p.height;p=p.transpose(Image.Transpose.ROTATE_270)
        jx,jy=h-1-jy,jx;crown=(h-1-crown[1],crown[0])
    x,y=round(grip[0]-jx),round(grip[1]-jy)
    # Translate the COMPLETE rigid weapon above the ground; never crop it.
    y=min(y,100-p.height);x=max(0,min(x,128-p.width));y=max(0,y)
    dst.alpha_composite(p,(x,y))
    return {'grip':[x+jx,y+jy],'crown':[x+crown[0],y+crown[1]],'quarter_turns':rot%4,'bbox':[x,y,x+p.width,y+p.height]}
def arm(dst,s,h,bend=1):
    # Thick material-matched articulated arm. The original grey glove is kept rigid.
    sx,sy=s;hx,hy=h
    ex=round((sx+hx)/2-bend*(hy-sy)*.18);ey=round((sy+hy)/2+bend*(hx-sx)*.18)
    d=ImageDraw.Draw(dst)
    d.line([s,(ex,ey),h],fill=INK,width=7)
    d.line([s,(ex,ey),h],fill=DARK,width=5)
    d.line([(sx-1,sy),(ex-1,ey),(hx-1,hy)],fill=MID,width=2)
    cx=round((ex+hx)/2);cy=round((ey+hy)/2)
    d.rectangle((cx-2,cy-2,cx+2,cy+2),fill=BRONZE)
    d.line((cx-2,cy-2,cx+1,cy-2),fill=LIGHT,width=1)
    dst.alpha_composite(GLOVE,(hx-2,hy-2))
def legs(dst,dx=0,dy=0,step=0,lift=0,seat=0):
    if not step and not lift and not seat:
        dst.alpha_composite(shifted(L,dx,dy));dst.alpha_composite(shifted(R,dx,dy));return
    # Whole rows translate; all source leg squares are retained, boots never flattened.
    for im,sign in [(L,1),(R,-1)]:
        ar=np.array(im);q=np.zeros_like(ar)
        for y in range(90,100):
            xs=np.where(ar[y,:,3]>0)[0]
            off=round(step*sign*(y-89)/10)+seat
            up=abs(lift) if (sign==1 and lift>0) or (sign==-1 and lift<0) else 0
            yy=min(99,y+dy-up)
            for x in xs:
                xx=x+dx+off
                if 0<=yy<128 and 0<=xx<128:q[yy,xx]=ar[y,x]
        dst.alpha_composite(Image.fromarray(q))
def chain(dst,a,b):
    d=ImageDraw.Draw(dst);d.line([a,b],fill=INK,width=3);d.line([a,b],fill=GRAY,width=1)
    dist=math.dist(a,b)
    for t in np.arange(0,dist,4):
        f=t/max(dist,1);x=round(a[0]+f*(b[0]-a[0]));y=round(a[1]+f*(b[1]-a[1]))
        d.point((x,min(99,y+1)),fill=MID)
def frame(dx=0,dy=0,step=0,lift=0,seat=0,wp=None,hands=None,ch=False):
    dst=blank();meta={}
    if wp is not None:meta['anchor']=anchor(dst,*wp)
    legs(dst,dx,0 if dy>0 else dy,step,lift,seat)
    dst.alpha_composite(shifted(CORE,dx,dy))
    hands=list(hands or [(51+dx,83+dy),(79+dx,87+dy)])
    if wp is not None:hands[0]=tuple(meta['anchor']['grip'])
    arm(dst,(54+dx,76+dy),hands[0],-1);arm(dst,(77+dx,76+dy),hands[1],1)
    # Exact approved helmet stencil is composited last, no rectangular replacement.
    dst.alpha_composite(shifted(Image.fromarray(HEAD),dx,dy))
    if ch:chain(dst,hands[0],(127,hands[0][1]))
    meta.update(head_translation=[dx,dy],hands=[list(p) for p in hands])
    return dst,meta
def idle(dx=0,dy=0):
    return shifted(Image.fromarray(A),dx,dy),{'head_translation':[dx,dy],'hands':[[51+dx,83+dy],[79+dx,87+dy]],'anchor':{'grip':[51+dx,83+dy],'crown':[64+dx,56+dy],'quarter_turns':0}}
frames={}; infos={}
def add(tag,f):
    frames[tag]=[x[0] for x in f];infos[tag]=[x[1] for x in f]
add('hit',[idle(-2),idle(-1)])
run=[]
for i,step in enumerate([-2,2,8,12,18,12,8,2]):
    dx=CELLS['tags']['run'][i]['pivot'][0]-66;dy=-1 if i in [2,3,6,7] else 0
    f,m=frame(dx,dy,step,2 if i==2 else -2 if i==6 else 0,wp=((51+dx,83+dy),0))
    m['run_leg_row_shift']=step;run.append((f,m))
add('run',run)
add('attack',[idle(),frame(-2,wp=((42,82),0),hands=[(42,82),(77,85)]),frame(1,step=3,wp=((74,76),1),hands=[(72,76),(78,85)]),frame(3,dy=1,step=5,wp=((78,78),1),hands=[(73,78),(79,86)]),frame(1,wp=((78,76),0),hands=[(78,76),(78,84)]),idle()])
add('skill',[frame(wp=((54,79),0),hands=[(54,79),(79,83)]),frame(-1,wp=((55,64),0),hands=[(55,64),(76,65)]),frame(-2,wp=((48,65),0),hands=[(48,65),(74,65)]),frame(2,wp=((75,65),1),hands=[(75,65),(79,69)]),frame(3,hands=[(87,78),(81,81)],ch=True),frame(-1,hands=[(82,80),(87,80)],ch=True)])
add('skill_pull',[frame(3,-2,step=-3,lift=1,hands=[(85,78),(90,78)],ch=True),frame(3,-1,step=-2,lift=1,hands=[(86,80),(91,80)],ch=True),frame(1,step=3,wp=((78,76),1),hands=[(76,76),(80,84)]),idle()])
add('skill2',[idle(),frame(wp=((51,83),0),hands=[(51,83),(83,64)]),frame(2,dy=3,step=3,wp=((51,83),0),hands=[(53,85),(85,96)]),frame(1,dy=1,wp=((51,83),0),hands=[(52,84),(84,89)]),frame(wp=((51,83),0),hands=[(51,83),(81,84)]),idle()])
add('ult',[idle(),frame(wp=((56,62),0),hands=[(56,62),(76,63)]),frame(-2,wp=((47,63),0),hands=[(47,63),(74,63)]),frame(2,wp=((77,63),1),hands=[(76,63),(81,67)]),frame(3,dy=3,step=4,wp=((88,69),2),hands=[(85,73),(86,77)]),frame(2,dy=3,step=3,wp=((88,69),2),hands=[(85,73),(86,77)]),frame(1,wp=((80,72),0),hands=[(80,72),(79,78)]),idle()])
add('dead',[idle(-2),frame(-1,wp=((42,83),0),hands=[(44,84),(78,87)]),frame(1,dy=2,seat=1,wp=((41,83),0),hands=[(45,87),(79,89)]),frame(0,dy=4,seat=3,wp=((41,83),0),hands=[(46,88),(80,91)]),frame(-1,dy=6,seat=4,wp=((41,83),0),hands=[(47,90),(80,93)]),frame(-2,dy=8,seat=5,wp=((41,83),0),hands=[(48,91),(80,95)]),frame(-2,dy=9,seat=5,wp=((41,83),0),hands=[(48,91),(80,95)]),frame(-2,dy=9,seat=5,wp=((41,83),0),hands=[(48,91),(80,95)])])
# Source idle is preserved byte for byte.
if SRC.resolve()!=OUT.resolve():shutil.copy2(SRC/'nautilus_idle.png',OUT/'nautilus_idle.png')
ia=Image.open(SRC/'nautilus_idle.png').convert('RGBA')
frames['idle']=[ia.crop(((i%4)*1024,(i//4)*1024,(i%4+1)*1024,(i//4+1)*1024)).resize((128,128),Image.Resampling.NEAREST) for i in range(8)]
infos['idle']=[{'head_translation':[0,0]} for _ in range(8)]
impacts={'attack':(4,13),'skill':(5,14),'skill2':(3,8),'ult':(5,16)}
manifest={'schema_version':1,'cell':[128,128],'scale':8,'ground_row':99,'design':'p35','source_idle_sha256':hashlib.sha256((SRC/'nautilus_idle.png').read_bytes()).hexdigest(),'actions':{}}
audit=[]
order=['idle','run','attack','skill','skill_pull','skill2','ult','hit','dead']
sheet=Image.new('RGB',(8*256,9*170),(39,43,50));sd=ImageDraw.Draw(sheet)
for row,tag in enumerate(order):
    fs=frames[tag];cols=2 if tag=='hit' else 3 if tag in ['attack','skill','skill2'] else 4
    rows=math.ceil(len(fs)/cols);strip=Image.new('RGBA',(cols*128,rows*128));entries=[]
    gif=[]
    for i,im in enumerate(fs):
        ar=np.array(im);ar[ar[:,:,3]==0]=0;im=Image.fromarray(ar);frames[tag][i]=im
        ys,xs=np.where(ar[:,:,3]>0);meta=infos[tag][i]
        assert ys.max()<=99,(tag,i,'ground',ys.max())
        assert set(map(tuple,ar[ar[:,:,3]>0,:3])).issubset(set(PAL)),(tag,i,'palette')
        if tag!='idle':
            dx,dy=meta['head_translation'];hh=np.array(shifted(Image.fromarray(HEAD),dx,dy));mask=hh[:,:,3]>0
            assert np.array_equal(ar[mask],hh[mask]),(tag,i,'helmet')
        strip.alpha_composite(im,((i%cols)*128,(i//cols)*128))
        e={'frame':i+1,'cell_rect_px':[(i%cols)*1024,(i//cols)*1024,1024,1024],'pivot':CELLS['tags'][tag][i]['pivot'],'bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'ms':CELLS['tags'][tag][i]['ms'],**meta}
        if tag in impacts and impacts[tag][0]==i+1:e['impact_tick']=impacts[tag][1]
        entries.append(e)
        bg=Image.new('RGB',(512,512),(39,43,50));bg.paste(im.resize((512,512),Image.Resampling.NEAREST),(0,0),im.resize((512,512),Image.Resampling.NEAREST).getchannel('A'));gif.append(bg)
        thumb=im.crop((16,24,120,104)).resize((208,160),Image.Resampling.NEAREST);sheet.paste(thumb,(i*256+40,row*170),thumb.getchannel('A'))
    sd.text((3,row*170+5),tag,fill='white')
    strip.save(OUT/f'nautilus_{tag}_1x.png')
    if tag!='idle':strip.resize((cols*1024,rows*1024),Image.Resampling.NEAREST).save(OUT/f'nautilus_{tag}.png')
    gif[0].save(OUT/'previews'/f'{tag}.gif',save_all=True,append_images=gif[1:],duration=[e['ms'] for e in entries],loop=0,disposal=2)
    manifest['actions'][tag]={'file':f'nautilus_{tag}.png','frames':entries,'grid':[cols,rows]}
    audit.append({'tag':tag,'frames':len(fs),'palette_ok':True,'ground_ok':True,'exact_head_ok':True if tag!='idle' else 'source preserved'})
sheet.save(OUT/'previews/contact_sheet.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
if SRC.resolve()!=OUT.resolve():
    shutil.copy2(SRC/'nautilus_cells.json',OUT/'nautilus_cells.json')
    shutil.copytree(SRC/'design',OUT/'design',dirs_exist_ok=True)
print(json.dumps(audit))
