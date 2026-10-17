from pathlib import Path
import sys, json, math, hashlib, shutil
import numpy as np
from PIL import Image, ImageDraw

REPO=Path(r'D:/TFM2-Workshop/repo/.claude/worktrees/reverent-wescoff-785c93')
sys.path.insert(0,str(REPO/'tools/art'))
import rigkit as rk

SRC=Path('work/khazix_strips_pack/khazix_strips_pack')
OUT=Path('outputs/khazix-strips')
OUT.mkdir(parents=True,exist_ok=True)
for sub in ('raw','previews','frames_1x'): (OUT/sub).mkdir(exist_ok=True)
DES=np.asarray(Image.open(SRC/'design/khazix_design_1x.png')).copy()
HEAD=np.asarray(Image.open(SRC/'design/khazix_head_1x.png')).copy()
HM=HEAD[:,:,3]>0
OP=DES[:,:,3]>0
PAL=set(tuple(int(v) for v in p[:3]) for p in DES[OP])
BLACK=(11,8,20)
CELLS=json.loads((SRC/'khazix_cells.json').read_text())
SHAPE=DES.shape[:2]

def rows(spec):
    m=np.zeros(SHAPE,bool)
    for y,(x0,x1) in spec.items():m[y,x0:x1+1]=True
    return m & OP

FAR=rows({**{y:(55,60) for y in range(75,77)},**{y:(55,61) for y in range(77,80)},**{y:(56,62) for y in range(80,82)},**{y:(57,64) for y in range(82,84)},**{y:(57,65) for y in range(84,86)},**{y:(57,64) for y in range(86,88)},88:(58,65),89:(58,64),90:(58,63),91:(58,62),92:(57,62),93:(58,61),94:(57,61),95:(57,60),96:(57,60),97:(56,59),98:(56,59),99:(56,58)})
NEAR=rows({**{y:(78,84) for y in range(75,78)},**{y:(79,87) for y in range(78,82)},**{y:(81,87) for y in range(82,85)},**{y:(77,86) for y in range(85,88)},88:(77,85),89:(77,84),90:(79,84),91:(80,85),92:(80,86),93:(81,86),94:(81,87),95:(82,87),96:(83,88),97:(84,88),98:(85,88),99:(86,88)})
FAR &= ~HM;NEAR &= ~HM
FLEG=rows({**{y:(56,61) for y in range(83,86)},**{y:(52,59) for y in range(86,90)},**{y:(50,56) for y in range(90,95)},**{y:(47,54) for y in range(95,100)}})&~(FAR|NEAR|HM)
NLEG=rows({83:(68,75),**{y:(68,77) for y in range(84,89)},**{y:(64,77) for y in range(89,94)},**{y:(64,81) for y in range(94,100)}})&~(FAR|NEAR|HM|FLEG)
# Wing material masks, expanded only onto the existing black outline cells.
GREEN=[rk.rgb(h) for h in ('5E6E1C','9CB83A','D2E47A')]
gm=rk.colour_mask(DES,GREEN)
adj=np.zeros(SHAPE,bool)
for dy in (-1,0,1):
    for dx in (-1,0,1):adj|=np.roll(np.roll(gm,dy,0),dx,1)
wm=gm|(adj & rk.colour_mask(DES,[BLACK]))
wm[69:]=False; wm[:,61:]=False
yy,xx=np.indices(SHAPE)
W1=wm & (xx>=54)&(yy<=63)
W2=wm & ~W1

parts={
 'far':rk.Part.from_canvas(DES,FAR,(56.5,75.5)),
 'near':rk.Part.from_canvas(DES,NEAR,(79.5,75.5)),
 'fleg':rk.Part.from_canvas(DES,FLEG,(61.5,84.5)),
 'nleg':rk.Part.from_canvas(DES,NLEG,(69.5,84.5)),
 'wing1':rk.Part.from_canvas(DES,W1,(60.5,63.5)),
 'wing2':rk.Part.from_canvas(DES,W2,(60.5,67.5)),
 'head':rk.Part.from_canvas(HEAD,HM,(73.5,75.5)),
}
BASE=DES.copy();BASE[FAR|NEAR]=0
# The far shoulder/forearm overlaps the rear hip in this tiny approved silhouette.
# Keep its existing hip pixels on the body too, so raising the arm does not detach a leg.
HIP_BRIDGE=rows({**{y:(61,67) for y in range(81,84)},**{y:(59,67) for y in range(83,87)}})&~HM
HIP_BRIDGE[87,58]=OP[87,58]
BASE[HIP_BRIDGE]=DES[HIP_BRIDGE]

def transform_part(part,deg):return rk.turn(part,deg) if deg else part
def allshift(a,dx,dy):return rk.shifted(a,dx,dy)
def paste_head(dst,dx=0,dy=0,deg=0,at=None):
    p=transform_part(parts['head'],deg)
    joint=at or (73.5+dx,75.5+dy)
    rk.place(dst,p,joint)
    mask=np.zeros_like(dst);rk.place(mask,p,joint)
    return mask[:,:,3]>0,list(joint)

def pose(fa=0,na=0,dx=0,dy=0,wings=0,legs=None,darker=False,far_joint_x=0,near_joint_x=0):
    body=BASE.copy()
    if wings:
        body[W1|W2]=0
        rk.place(body,transform_part(parts['wing1'],-45),(60.5,63.5))
        rk.place(body,transform_part(parts['wing2'],45),(60.5,67.5))
    if legs is not None:
        body[FLEG|NLEG]=0
        for key,mask,hip,leg in [('fleg',FLEG,(61.5,84.5),legs[0]),('nleg',NLEG,(69.5,84.5),legs[1])]:
            if isinstance(leg,dict):
                layer=rk.swing_leg(DES,mask,84,96,leg['dx'],leg.get('lift',0))
            else:
                layer=np.zeros_like(DES);rk.place(layer,transform_part(parts[key],leg),hip)
            if key=='fleg' and darker:
                shade={'6A4ED0':'46309A','46309A':'2A1A5C','9478F0':'6A4ED0','4EB8F0':'2A78D0','2A78D0':'1A3E8A','CC7632':'B4662A'}
                original=layer.copy()
                for a,b in shade.items():layer[rk.colour_mask(original,[rk.rgb(a)])]=[*rk.rgb(b),255]
            rk.put(body,layer,0,0)
    far=transform_part(parts['far'],fa)
    near=transform_part(parts['near'],na)
    out=np.zeros_like(DES)
    rk.place(out,far,(56.5+far_joint_x,75.5))
    rk.put(out,body,0,0)
    # Far blade is a visible foreground surface; the rigid arm geometry itself is not altered.
    far_canvas=np.zeros_like(DES);rk.place(far_canvas,far,(56.5+far_joint_x,75.5))
    # Approved blade colors locate the entire exposed scythe segment.
    far_blade_source=DES.copy();far_blade_source[~FAR]=0;far_blade_source[:85]=0
    far_blade=rk.Part.from_canvas(far_blade_source,far_blade_source[:,:,3]>0,(56.5,75.5))
    rk.place(out,transform_part(far_blade,fa),(56.5+far_joint_x,75.5))
    rk.place(out,near,(79.5+near_joint_x,75.5))
    out=allshift(out,dx,dy)
    hm,head_at=paste_head(out,dx,dy)
    return out,hm,head_at,{'far_angle':fa,'near_angle':na,'whole_shift':[dx,dy],'wings_open':bool(wings),'legs':legs,'arm_joint_x_offsets':[far_joint_x,near_joint_x]}

def death(deg,dx=0,dy=0,curl=False):
    actor,_,_,params=pose(0 if deg==90 else -45,0 if deg==90 else 45,legs=(-45,45) if curl else None)
    if deg==90:
        p=rk.Part.from_canvas(actor,actor[:,:,3]>0,(64.5,88.5))
        out=np.zeros_like(actor);rk.place(out,transform_part(p,90),(64.5+dx,88.5+dy))
        hp=transform_part(parts['head'],90)
        # Exact whole-body quarter turn maps the original face joint to this coordinate.
        at=(64.5+(75.5-88.5)+dx,88.5-(73.5-64.5)+dy)
        hm=np.zeros_like(out);rk.place(hm,hp,at)
        return out,hm[:,:,3]>0,list(at),{'whole_angle':90,'curl':curl}
    actor[HM]=0
    p=rk.Part.from_canvas(actor,actor[:,:,3]>0,(64.5,88.5))
    out=np.zeros_like(actor);rk.place(out,transform_part(p,deg),(64.5+dx,88.5+dy))
    th=math.radians(deg);hx,hy=9,-13
    at=(64.5+hx*math.cos(th)+hy*math.sin(th)+dx,88.5-hx*math.sin(th)+hy*math.cos(th)+dy)
    hm,at=paste_head(out,at=at)
    return out,hm,at,{'whole_angle':deg,'curl':curl}

PLAN={
 'attack':[dict(fa=-45,na=90),dict(fa=-45,na=180),dict(fa=0,na=90,dx=1),dict(fa=-45,na=45,dx=3),dict(fa=-45,na=0,dx=2),dict()],
 'skill':[dict(fa=-45,na=135,dx=-2),dict(fa=-45,na=180,dx=-1),dict(fa=0,na=90,dx=1),dict(fa=-45,na=90,dx=3),dict(fa=-45,na=90,dx=3),dict()],
 'skill2':[dict(fa=-45,na=45,legs=(-45,45),dy=2),dict(fa=-45,na=90,wings=1,legs=(-45,90),dy=-5),dict(fa=-45,na=90,wings=1,legs=(-45,90),dy=-6),dict(fa=-45,na=45,legs=(-45,45),dy=2),dict(fa=180,na=0,wings=1),dict(fa=90,na=0,wings=1,dx=3),dict()],
 'ult':[dict(fa=-45,na=45,wings=1,dy=-1),dict(fa=45,na=-45),dict()],
 'hit':[dict(fa=-45,na=45,dx=-2),dict()],
}
runfar=[0,6,14,20,22,16,9,3];runnear=[0,-6,-8,-17,-22,-16,-11,-5]
lf=[1,3,3,1,0,0,0,0];ln=[0,0,0,0,1,3,3,1]
near_swing=[1,1,0,-1,-1,-1,0,1]
PLAN['run']=[dict(fa=0,na=0,far_joint_x=-near_swing[i],near_joint_x=near_swing[i],dy=0 if i in (0,4) else -1,legs=({'dx':runfar[i],'lift':lf[i]},{'dx':runnear[i],'lift':ln[i]}),darker=True) for i in range(8)]

def pixel_hash(a):return hashlib.sha256(a.tobytes()).hexdigest()
def floor_fit(result):
    a,hm,head_at,params=result
    low=np.nonzero(a[:,:,3].any(1))[0].max()
    if low>99:
        off=99-int(low);a=allshift(a,0,off);hm=allshift(np.dstack([hm]*4).astype(np.uint8),0,off)[:,:,0]>0
        head_at[1]+=off;params['floor_lift']=off
    return a,hm,head_at,params

RELEASE={'attack':(4,11),'skill':(4,12),'skill2':(6,20),'ult':(2,6)}
manifest={'cell_1x':[128,96],'scale':8,'palette':['#%02X%02X%02X'%c for c in sorted(PAL)],'approved_design_sha256':hashlib.sha256((SRC/'design/khazix_design_1x.png').read_bytes()).hexdigest(),'actions':{}}
qa={};allframes={}
# Copy idle byte-for-byte, also retaining unmodified source contract.
shutil.copy2(SRC/'khazix_idle.png',OUT/'khazix_idle.png');shutil.copy2(SRC/'khazix_cells.json',OUT/'khazix_cells.json')
for tag in ('idle','run','attack','skill','skill2','ult','hit','dead'):
    meta=CELLS['tags'][tag];n=len(meta);cols=rk.layout(n)[0];rowsn=math.ceil(n/cols)
    sheet=np.zeros((rowsn*96,cols*128,4),np.uint8)
    entries=[];frames=[];masks=[]
    results=[]
    if tag=='dead':
        results=[pose(-45,45,dx=-1),pose(-45,90,dx=-3),death(45,dx=-2),death(60,dx=-3,dy=2),death(90,dx=-2,curl=True),death(90,dx=-3,curl=True),death(90,dx=-3,curl=True),death(90,dx=-3,curl=True)]
    elif tag=='idle':results=[pose() for _ in range(n)]
    else:results=[pose(**p) for p in PLAN[tag]]
    for i,result in enumerate(results):
        a,hm,hat,params=floor_fit(result)
        if tag=='skill2' and i in (0,3):
            drop=99-int(np.nonzero(a[:,:,3].any(1))[0].max())
            a=allshift(a,0,drop)
            hm=allshift(np.dstack([hm]*4).astype(np.uint8),0,drop)[:,:,0]>0
            hat[1]+=drop;params['landing_floor_drop']=drop
        if tag!='idle':
            # Preserve copied face bits, remove tiny orphan outlines without changing the approved standing body.
            orphan=rk.orphan_outline(a,BLACK)&~hm
            a[orphan]=0
            for comp in rk.pieces(a)[1:]:
                if len(comp)<=3 and not any(hm[y,x] for y,x in comp):
                    for y,x in comp:a[y,x]=0
        # All coordinates are positioned by the supplied pivot; head offsets are art-controlled for stable identity.
        px,py=meta[i]['pivot'];sx=px-64;sy=py-88
        cell=np.zeros((96,128,4),np.uint8);rk.put(cell,a,sx,sy)
        hcell=np.zeros_like(cell);rk.put(hcell,np.dstack([hm]*4).astype(np.uint8),sx,sy)
        head_mask=hcell[:,:,0]>0
        assert np.count_nonzero(cell[:,:,3])==np.count_nonzero(a[:,:,3]),(tag,i,'cell clipping')
        assert not cell[82:,:,3].any(),(tag,i,'floor clipping')
        assert set(tuple(int(v) for v in p[:3]) for p in cell[cell[:,:,3]>0])<=PAL
        bbox=Image.fromarray(cell).getbbox()
        X,Y=(i%cols)*128,(i//cols)*96
        sheet[Y:Y+96,X:X+128]=cell
        entry={'frame':i+1,'cell_rect_1x':[X,Y,128,96],'cell_rect_8x':[X*8,Y*8,1024,768],'pivot':meta[i]['pivot'],'ms':meta[i]['ms'],'bbox':bbox,'bbox_8x':[v*8 for v in bbox],'head_joint':[hat[0]+sx,hat[1]+sy],'head_rotation':90 if tag=='dead' and i>=4 else 0,'head_mask_pixels':int(head_mask.sum()),'pose':params,'pixel_hash':pixel_hash(cell)}
        if tag in RELEASE and i+1==RELEASE[tag][0]:
            blade=rk.colour_mask(cell,[rk.rgb(c) for c in ('C8A8A8','F2DCD4','FFF6F0')])
            ys,xs=np.nonzero(blade & ~head_mask)
            xx=int(xs.max());yy=int(ys[xs==xx].min())
            entry['release']={'tick':RELEASE[tag][1],'claw_tip_1x':[xx,yy],'claw_tip_8x':[xx*8+4,yy*8+4],'sheet_tip_8x':[(X+xx)*8+4,(Y+yy)*8+4]}
        entries.append(entry);frames.append(cell);masks.append(head_mask)
        Image.fromarray(cell).save(OUT/'frames_1x'/f'{tag}_{i+1:02}.png')
    small=Image.fromarray(sheet);small.save(OUT/f'khazix_{tag}_1x.png')
    if tag!='idle':small.resize((cols*1024,rowsn*768),Image.Resampling.NEAREST).save(OUT/f'khazix_{tag}.png')
    # Build readable fixed-view animated previews at the original durations.
    gifs=[]
    for cell in frames:
        im=Image.new('RGBA',(128,96),(245,245,245,255));im.alpha_composite(Image.fromarray(cell))
        gifs.append(im.resize((512,384),Image.Resampling.NEAREST).convert('RGB'))
    gifs[0].save(OUT/'previews'/f'khazix_{tag}.gif',save_all=True,append_images=gifs[1:],duration=[x['ms'] for x in meta],loop=0,disposal=2)
    # Compact contact strip: frame boundaries/labels are only in the review image.
    review=Image.new('RGBA',(n*300,260),'white');d=ImageDraw.Draw(review)
    for i,cell in enumerate(frames):
        crop=Image.fromarray(cell).crop((24,22,108,83)).resize((252,183),Image.Resampling.NEAREST)
        review.alpha_composite(crop,(i*300+24,40));d.text((i*300+24,10),f'{tag} {i+1} / {meta[i]["ms"]}ms',fill='black')
        d.line((i*300+24,220,i*300+275,220),fill='lightgray')
    review.save(OUT/'previews'/f'{tag}_contact.png')
    qa[tag]={'frame_count':n,'durations_ms':[x['ms'] for x in meta],'unique_frames':len(set(x['pixel_hash'] for x in entries)),'native_contract_preserved':True,'raw_generation':'raw/'+tag+'_generated.png' if tag!='idle' else 'provided idle','per_frame':rk.audit(frames,frames[0],BLACK,81)}
    manifest['actions'][tag]={'file':f'khazix_{tag}.png','size_8x':[cols*1024,rowsn*768],'grid':[cols,rowsn],'frames':entries}
    allframes[tag]=frames

(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
# Component identity proof and exact reconstruction before posing.
reconstructed,_,_,_=pose()
print('idle reconstruction exact:',np.array_equal(reconstructed,DES))
print(json.dumps({tag:{'unique':q['unique_frames'],'areas':[x['area'] for x in q['per_frame']],'pieces':[x['pieces'] for x in q['per_frame']],'orphans':[x['orphans'] for x in q['per_frame']]} for tag,q in qa.items()},indent=2))
