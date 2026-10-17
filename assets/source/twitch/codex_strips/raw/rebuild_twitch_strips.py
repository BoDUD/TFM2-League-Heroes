from pathlib import Path
from collections import Counter
import json, hashlib, math, shutil, sys
import numpy as np
from PIL import Image, ImageDraw

HOME=Path(__file__).resolve().parents[1]
SRC=HOME/'work/twitch-strips-pack/twitch_strips_pack'
OUT=HOME/'outputs/twitch-strips'
if Path(__file__).resolve().parent.name=='raw':
    OUT=Path(__file__).resolve().parents[1]
    SRC=OUT/'source'
sys.path.insert(0,r'D:\TFM2-Workshop\repo\.claude\worktrees\objective-hermann-292254\tools\art')
import rigkit as rig

cells=json.loads((SRC/'twitch_cells.json').read_text())
design=np.array(Image.open(SRC/'design/twitch_design_1x.png').convert('RGBA'))
head=np.array(Image.open(SRC/'design/twitch_head_1x.png').convert('RGBA'))
palette=np.unique(design[design[:,:,3]>0,:3],axis=0)
outline=tuple(palette[np.argmin(palette.sum(1))])
LAYOUT={'idle':(3,2),'run':(4,2),'attack':(3,2),'skill':(3,1),'skill2':(4,1),'skill2_e':(3,2),'ult':(3,1),'hit':(2,1),'dead':(4,2)}
CAST={'attack':(2,7),'skill':(1,6),'skill2':(2,9),'skill2_e':(2,10),'ult':(1,6)}
for p in ['raw','preview','1x','source']: (OUT/p).mkdir(parents=True,exist_ok=True)
shutil.copy2(SRC/'twitch_cells.json',OUT/'twitch_cells.json')
for f in (SRC/'design').glob('*.png'):shutil.copy2(f,OUT/'source'/f.name)

def maskrows(spec):return rig.mask_rows(spec)
op=design[:,:,3]>0
armmask=maskrows({79:(56,59),80:(55,60),81:(55,60),82:(55,62),83:(57,63),84:(57,65),85:(58,66),86:(58,64),87:(58,64),88:(57,64),89:(57,64),90:(57,64)})&op
bowmask=maskrows({82:(74,82),83:(67,85),84:(68,89),85:(68,89),86:(66,88),87:(66,88),88:(67,88),89:(67,88),90:(77,88),91:(85,88)})&op
tailmask=rig.mask_box(80,90,44,54)&op
legcolors=[(112,67,94),(253,246,208),(63,35,31),(25,59,67)]
legmask=rig.colour_mask(design,legcolors)&rig.mask_box(91,99,51,80)
legmask|=(rig.mask_box(95,99,51,80)&op)
nearlegmask=legmask&rig.mask_box(91,99,51,62)
farlegmask=legmask&rig.mask_box(91,99,66,80)
neararm=rig.Part.from_canvas(design,armmask,(56,80))
bow=rig.Part.from_canvas(design,bowmask,(67,86))
whole=rig.Part.from_canvas(design,op,(64,88))
tail=rig.Part.from_canvas(design,tailmask,(54,88))

# Backfill only the compact chest patch exposed by moving the original near arm.
body=design.copy(); body[armmask|bowmask]=0
for y in range(79,91):
    for x in range(55,67):
        if not design[y,x,3] or body[y,x,3]:continue
        candidates=[]
        for dx in [-2,-3,-4,-5,-6]:
            if body[y,x+dx,3] and tuple(body[y,x+dx,:3]) in [(25,59,67),(51,107,94),(0,64,122),(6,107,172)]:candidates.append(tuple(body[y,x+dx]))
        if not candidates:candidates=[(25,59,67,255)]
        if candidates:body[y,x]=Counter(candidates).most_common(1)[0][0]

def pose(armdeg=0,bowdeg=0,armshift=(0,0),bowshift=(0,0),split=False):
    if armdeg==bowdeg==0 and armshift==bowshift==(0,0) and not split:
        return design.copy(),[86,90],[64,85],[78,89]
    a=body.copy()
    # Crossbow and its supporting hand are rigid; the near arm remains a rigid source cutout.
    bp=rig.turn(bow,bowdeg); ap=rig.turn(neararm,armdeg)
    rig.place(a,bp,(67+bowshift[0],86+bowshift[1]))
    rig.place(a,ap,(56+armshift[0],80+armshift[1]))
    rig.put(a,head,0,0)
    def point(p,j,deg,shift):
        x,y=p[0]-j[0],p[1]-j[1]; t=math.radians(deg)
        return [round(j[0]+x*math.cos(t)+y*math.sin(t)+shift[0]),round(j[1]-x*math.sin(t)+y*math.cos(t)+shift[1])]
    return a,point((86,90),(67,86),bowdeg,bowshift),point((64,85),(56,80),armdeg,armshift),point((78,89),(67,86),bowdeg,bowshift)

def settle(a,px,dx=0,dy=0):
    return rig.shifted(a,px-64+dx,-18+dy)

def prepare_source_grid(action):
    # Majority color per detected generated cell, no filtered resize and no row deletion.
    raw=Image.open(OUT/'raw'/f'{action}-generated.png').convert('RGBA'); a=np.array(raw)
    rgb=a[:,:,:3].astype(float); m=a[:,:,3]>=128
    hx=(abs(rgb[:,1:]-rgb[:,:-1]).sum(2)*(m[:,1:]&m[:,:-1])).sum(0)
    hy=(abs(rgb[1:]-rgb[:-1]).sum(2)*(m[1:]&m[:-1])).sum(1)
    def axis(h):
        top=np.argsort(h)[-100:]; weights=h[top]; periods=np.arange(3.5,13,.01)
        vals=np.exp(2j*np.pi*top[None,:]/periods[:,None])@weights
        i=np.argmax(abs(vals)); p=float(periods[i]); o=float(np.angle(vals[i])*p/(2*np.pi))%p
        return p,o
    px,ox=axis(hx);py,oy=axis(hy)
    xb=np.arange(ox,raw.width,px).round().astype(int); yb=np.arange(oy,raw.height,py).round().astype(int)
    result=np.zeros((len(yb)-1,len(xb)-1,4),np.uint8)
    for y in range(len(yb)-1):
        for x in range(len(xb)-1):
            block=a[yb[y]:yb[y+1],xb[x]:xb[x+1]]
            pix=block[block[:,:,3]>=128]
            if len(pix)<block.shape[0]*block.shape[1]*.5:continue
            rgbpix=pix[:,:3].astype(int)
            idx=np.argmin(((rgbpix[:,None,:]-palette[None,:,:].astype(int))**2).sum(2),axis=1)
            c=palette[np.bincount(idx,minlength=len(palette)).argmax()]
            result[y,x]=[*c,255]
    Image.fromarray(result).save(OUT/'raw'/f'{action}-majority-grid-1x.png')
    return dict(period_x=px,period_y=py,phase_x=ox,phase_y=oy,status='pose_reference_only_identity_drift_not_final')

manifest={'schema_version':1,'cell':[128,96],'scale':8,'soles_row':81,'coordinate_units':'1x grid cells; rect_px is 8x atlas pixels','approved_design_sha256':hashlib.sha256((SRC/'design/twitch_design_1x.png').read_bytes()).hexdigest(),'tags':{}}
frames_by_tag={}; reports={}
for tag,meta in cells['tags'].items():
    cols,rows=LAYOUT[tag]; frames=[]; entries=[]
    sourcegrid=prepare_source_grid(tag) if tag!='idle' else None
    for i,row in enumerate(meta):
        px,py=row['pivot']; dx=dy=0; hrot=0; exacthead=True
        bowtip=[86,90]; nearhand=[64,85]; farhand=[78,89]
        if tag=='idle':
            atlas=np.array(Image.open(SRC/'twitch_idle.png'))[::8,::8]
            a=atlas[(i//cols)*96:(i//cols+1)*96,(i%cols)*128:(i%cols+1)*128].copy()
            headat=[px-5,48]
        elif tag=='run':
            a=design.copy();a[nearlegmask|farlegmask|tailmask]=0
            phases=[12,10,8,3,0,2,8,10]; step=phases[i]
            near_lift=2 if i in [2,3] else 0; far_lift=2 if i in [6,7] else 0
            far=np.zeros_like(design);far[farlegmask]=design[farlegmask]
            far=rig.shifted(far,-step,-far_lift)
            # The far leg uses the existing darker gray-purple, retaining white claws.
            light=(far[:,:,:3]==[112,67,94]).all(2)&(far[:,:,3]>0)
            far[light,:3]=[63,35,31]
            near=np.zeros_like(design);near[nearlegmask]=design[nearlegmask]
            near=rig.shifted(near,step,-near_lift)
            rig.put(a,far,0,0);rig.put(a,near,0,0)
            rig.place(a,tail,(54,88+(1 if i in [2,3,6,7] else 0)))
            dy=-1 if i in [2,3,6,7] else 0
            a=settle(a,px,dy=dy)[:96];headat=[59+px-64,66-18+dy]
        elif tag=='attack':
            params=[(0,0,(0,0),(0,0)),(0,0,(1,-1),(1,-1)),(0,0,(-2,-2),(-2,-2)),(0,0,(0,-1),(0,-1)),(0,0,(0,0),(0,0))]
            a,bowtip,nearhand,farhand=pose(*params[i]);dx=[0,1,-1,0,0][i]
            a=settle(a,px,dx=dx)[:96];headat=[59+px-64+dx,48]
        elif tag=='skill':
            # Fixed rat legs/body take priority over impossible below-floor whole-body descent.
            p=[(-1,0),(-2,0),(0,0)][i]
            a,bowtip,nearhand,farhand=pose(0,0,p,p);dx=[-1,-2,0][i]
            a=settle(a,px,dx=dx)[:96];headat=[59+px-64+dx,48]
        elif tag=='skill2':
            if i==0:a,bowtip,nearhand,farhand=pose(-45,0,(0,0),(0,0),True)
            elif i==1:a,bowtip,nearhand,farhand=pose(135,0,(0,0),(0,0),True);dx=-1
            elif i==2:a,bowtip,nearhand,farhand=pose(0,0,(3,-1),(0,0),True);dx=1
            else:a,bowtip,nearhand,farhand=pose()
            if i<2:
                # 3x3 hand-carried cask cut from the approved emerald/backpack colors.
                patch=design[79:82,55:58].copy()
                rig.put(a,patch,nearhand[0]-1,nearhand[1]-3)
            a=settle(a,px,dx=dx)[:96];headat=[59+px-64+dx,48]
        elif tag=='skill2_e':
            if i==2:
                a,bowtip,nearhand,farhand=pose(135,0,(0,0),(1,-1),True);dy=-3
            elif i in [0,1]:
                p=(0,-(i+1));a,bowtip,nearhand,farhand=pose(0,0,p,p)
            elif i==3:a,bowtip,nearhand,farhand=pose(0,0,(0,-1),(0,-1))
            else:a,bowtip,nearhand,farhand=pose()
            a=settle(a,px,dy=dy)[:96];headat=[59+px-64,48+dy]
        elif tag=='ult':
            if i==0:a,bowtip,nearhand,farhand=pose(0,0,(0,-3),(0,-3))
            elif i==1:a,bowtip,nearhand,farhand=pose(135,0,(0,0),(8,-6),True)
            else:a,bowtip,nearhand,farhand=pose(0,0,(0,-1),(0,-1))
            a=settle(a,px)[:96];headat=[59+px-64,48]
        elif tag=='hit':
            dx=-2 if i==0 else 0;a=settle(design,px,dx=dx)[:96];headat=[59+px-64+dx,48]
        elif tag=='dead':
            if i<2:
                dx=-2-i;a=settle(design,px,dx=dx)[:96];headat=[59+px-64+dx,48]
            else:
                hrot=45 if i==2 else 90
                # Counterclockwise turn makes the head left and the feet right.
                part=rig.turn(whole,hrot); ys,xs=np.nonzero(part.s[:,:,3])
                a=np.zeros((96,128,4),np.uint8)
                at=(px,81-(ys.max()-part.j[1]))
                rig.place(a,part,at);headat=None;exacthead=i!=2
                # Metadata points transformed by the same complete-figure rotation.
                def rotatepoint(p):
                    t=math.radians(hrot);x=p[0]-64;y=p[1]-88
                    return [round(at[0]+x*math.cos(t)+y*math.sin(t)),round(at[1]-x*math.sin(t)+y*math.cos(t))]
                bowtip=rotatepoint(bowtip);nearhand=rotatepoint(nearhand);farhand=rotatepoint(farhand)
        if tag!='idle' and not (tag=='dead' and i>=2):
            # Exact approved head is retained; no outline completion is allowed to touch it.
            expected=rig.shifted(head,px-64+dx,-18+dy)[:96]
            hm=expected[:,:,3]>0
            assert np.array_equal(a[hm],expected[hm]),(tag,i,'head mismatch')
            bowtip=[bowtip[0]+px-64+dx,bowtip[1]-18+dy]
            nearhand=[nearhand[0]+px-64+dx,nearhand[1]-18+dy]
            farhand=[farhand[0]+px-64+dx,farhand[1]-18+dy]
        if tag!='idle':
            assert not a[82:,:,3].any(),(tag,i,'below feet')
        colors={tuple(c) for c in a[a[:,:,3]>0,:3]}
        assert colors.issubset({tuple(c) for c in palette})
        assert set(np.unique(a[:,:,3])).issubset({0,255})
        ys,xs=np.nonzero(a[:,:,3]);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        entry=dict(index=i+1,rect=[(i%cols)*128,(i//cols)*96,128,96],rect_px=[(i%cols)*1024,(i//cols)*768,1024,768],pivot=[px,py],ms=row['ms'],bbox=bbox,head_exact=exacthead,head_rotation=hrot,head_bbox_origin=headat,opaque_pixels=int(len(xs)),source='provided_idle' if tag=='idle' else 'approved_design_rigid_parts_after_generated_pose_review')
        if tag=='run':entry['stride']=dict(near_foot=[57+step+px-64,97-near_lift-18+dy],far_foot=[76-step+px-64,98-far_lift-18+dy],near_lift=near_lift,far_lift=far_lift,head_relative_x=59-64,bob=dy)
        if tag in CAST and i==CAST[tag][0]:entry['release']=dict(tick=CAST[tag][1],bow_tip=bowtip,near_hand=nearhand,far_hand=farhand,hand_empty=tag=='skill2')
        entries.append(entry);frames.append(a)
    frames_by_tag[tag]=frames
    atlas=np.zeros((rows*96,cols*128,4),np.uint8)
    for i,a in enumerate(frames):atlas[(i//cols)*96:(i//cols+1)*96,(i%cols)*128:(i%cols+1)*128]=a
    Image.fromarray(atlas).save(OUT/'1x'/f'twitch_{tag}_1x.png')
    if tag=='idle':shutil.copy2(SRC/'twitch_idle.png',OUT/'twitch_idle.png')
    else:Image.fromarray(atlas).resize((cols*1024,rows*768),Image.Resampling.NEAREST).save(OUT/f'twitch_{tag}.png')
    reread=np.array(Image.open(OUT/f'twitch_{tag}.png'))
    assert np.array_equal(reread,np.repeat(np.repeat(atlas,8,axis=0),8,axis=1))
    frames_png=[]
    for frame_no,a in enumerate(frames):
        # Previews stabilize on the pivot, unlike import atlases, to reveal jitter.
        preview=Image.new('RGBA',(128,96),(225,231,226,255))
        pivot=meta[frame_no]['pivot'];stable=rig.shifted(a,60-pivot[0],70-pivot[1])
        preview.alpha_composite(Image.fromarray(stable)); preview=preview.crop((16,34,105,85)).resize((356,204),Image.Resampling.NEAREST).convert('RGB')
        frames_png.append(preview)
    frames_png[0].save(OUT/'preview'/f'twitch_{tag}.gif',save_all=True,append_images=frames_png[1:],duration=[m['ms'] for m in meta],loop=0,disposal=2)
    manifest['tags'][tag]=dict(file=f'twitch_{tag}.png',size=[cols*1024,rows*768],grid=[cols,rows],frames=entries,source_grid=sourcegrid)
    reports[tag]=dict(frames=len(frames),unique_frames=len({hashlib.sha256(a.tobytes()).hexdigest() for a in frames}),palette_valid=True,hard_alpha=True,grid_8x=True,below_feet=sum(int(a[82:,:,3].sum()>0) for a in frames),head_exact_frames=sum(e['head_exact'] for e in entries),areas=[e['opaque_pixels'] for e in entries])
    reports[tag]['connected_components']=[len(rig.pieces(a)) for a in frames]
    assert all(n==1 for n in reports[tag]['connected_components']),(tag,'loose piece')

# Compact per-action frame review, including all 44 frames, not atlas downscaling.
review=Image.new('RGB',(8*288,9*244),(242,243,240));d=ImageDraw.Draw(review)
for r,(tag,fs) in enumerate(frames_by_tag.items()):
    for j,a in enumerate(fs):
        bg=Image.new('RGBA',(128,96),'white');bg.alpha_composite(Image.fromarray(a))
        thumb=bg.crop((12,34,108,84)).resize((288,150),Image.Resampling.NEAREST)
        review.paste(thumb.convert('RGB'),(j*288,r*244+32));d.text((j*288+8,r*244+8),f'{tag} {j+1} / {cells["tags"][tag][j]["ms"]} ms',fill='black')
review.save(OUT/'preview/twitch_all_frames.png')
# Animated overview: individual GIFs preserve exact timings; overview samples at 50 ms.
actions=[t for t in frames_by_tag if t!='idle']; overview=[]
for time in range(0,2000,50):
    page=Image.new('RGB',(712,944),(242,243,240));dr=ImageDraw.Draw(page)
    for k,tag in enumerate(actions):
        durations=[r['ms'] for r in cells['tags'][tag]];total=sum(durations)
        now=min(time,total-1) if tag=='dead' else time%total
        index=0
        while now>=durations[index]:now-=durations[index];index+=1
        a=frames_by_tag[tag][index];pivot=cells['tags'][tag][index]['pivot']
        a=rig.shifted(a,60-pivot[0],70-pivot[1]);bg=Image.new('RGBA',(128,96),(225,231,226,255));bg.alpha_composite(Image.fromarray(a))
        tile=bg.crop((16,34,105,85)).resize((356,204),Image.Resampling.NEAREST)
        x,y=(k%2)*356,(k//2)*236;page.paste(tile.convert('RGB'),(x,y+28));dr.text((x+12,y+9),f'{tag}  {index+1}/{len(durations)}',fill='black')
    overview.append(page)
overview[0].save(OUT/'preview/twitch_actions_overview.gif',save_all=True,append_images=overview[1:],duration=50,loop=0,disposal=2)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports,indent=2))
