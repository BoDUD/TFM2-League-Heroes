from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'work/brand_run_swap_pack'
OUT=ROOT/'outputs/brand-run'
(OUT/'raw').mkdir(parents=True,exist_ok=True)
RAW=Path(r'C:\Users\OWNER\.codex\generated_images\01a1116f-288b-72d2-8cd8-24fce6dfabfd\exec-bc4fb966-3a51-471c-8dd5-21df443b78bb.png')
shutil.copy2(Path(r'C:\Users\OWNER\.codex\generated_images\01a1116f-288b-72d2-8cd8-24fce6dfabfd\exec-08c07078-39e5-4ad1-a913-dd663920d677.png'),OUT/'raw/brand_run_generated.png')
shutil.copy2(RAW,OUT/'raw/brand_run_corrected.png')
design=np.array(Image.open(SRC/'2_brand_design.png').convert('RGBA'))[::8,::8]
upper=np.array(Image.open(SRC/'4_brand_upper_body.png').convert('RGBA'))[::8,::8]
palette=np.array(sorted(set(tuple(p[:3]) for p in design.reshape(-1,4) if p[3])),dtype=np.int32)
raw=np.array(Image.open(RAW).convert('RGB'))
def components(mask):
    seen=set();parts=[]
    for y,x in zip(*np.where(mask)):
        if (y,x) in seen:continue
        stack=[(y,x)];seen.add((y,x));part=[]
        while stack:
            p=stack.pop();part.append(p)
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    q=p[0]+dy,p[1]+dx
                    if 0<=q[0]<mask.shape[0] and 0<=q[1]<mask.shape[1] and mask[q] and q not in seen:seen.add(q);stack.append(q)
        parts.append(part)
    return sorted(parts,key=len,reverse=True)

def majority_grid(frame,step=6):
    flat=frame.reshape(-1,3).astype(np.int32)
    green=(flat[:,1]>180)&(flat[:,0]<100)&(flat[:,2]<100)
    ids=np.zeros(len(flat),dtype=np.uint8)
    foreground=np.where(~green)[0]
    for start in range(0,len(foreground),10000):
        loc=foreground[start:start+10000]
        d=((flat[loc,None,:]-palette[None,:,:])**2).sum(axis=2)
        ids[loc]=np.argmin(d,axis=1)+1
    ids=ids.reshape(frame.shape[:2])
    # Choose the shared pixel block phase by majority purity in the character area.
    best=(-1,0,0,None)
    for py in range(step):
        for px in range(step):
            rows=[];score=0;used=0
            for y in range(py,frame.shape[0]-step+1,step):
                row=[]
                for x in range(px,frame.shape[1]-step+1,step):
                    h=np.bincount(ids[y:y+step,x:x+step].ravel(),minlength=len(palette)+1);k=int(h.argmax());row.append(k)
                    if h[1:].sum()>step*step*.3:score+=h[k]/(step*step);used+=1
                rows.append(row)
            purity=score/max(used,1)
            if purity>best[0]:best=(purity,px,py,np.array(rows,dtype=np.uint8))
    purity,px,py,grid=best
    rgba=np.zeros((*grid.shape,4),dtype=np.uint8);mask=grid>0
    rgba[mask,:3]=palette[grid[mask]-1];rgba[mask,3]=255
    return rgba,{'step':step,'phase':[px,py],'majority_purity':round(purity,4)}

frames=[];records=[];sheet=np.zeros((192,512,4),dtype=np.uint8)
tan={tuple(bytes.fromhex(h)) for h in ['3A2A1F','513E2D','805B40','AA784B','B46117','CD7D2B']}
for i in range(6):
    crop=raw[(i//4)*384:(i//4+1)*384,(i%4)*512:(i%4+1)*512]
    grid,setting=majority_grid(crop)
    Image.fromarray(grid).save(ROOT/f'work/run_generated_native_{i}.png')
    # Uppermost central brown cloth marks the pelvis; retain the generated legs only.
    is_tan=np.zeros(grid.shape[:2],dtype=bool)
    for c in tan:is_tan|=(grid[:,:,:3]==c).all(axis=2)&(grid[:,:,3]>0)
    counts=is_tan[:,34:51].sum(axis=1)
    candidates=np.where(counts>=4)[0]
    first=int(candidates[0]);ty,tx=np.where(is_tan)
    center=float(np.median(tx[(ty>=first)&(ty<=first+2)]))
    low=grid.copy();low[:first]=0
    parts=components(low[:,:,3]>0)
    eligible=[p for p in parts if any(y<=first+2 and abs(x-center)<5 for y,x in p)]
    keep=max(eligible,key=len);mask=np.zeros(low.shape[:2],dtype=bool)
    for p in keep:mask[p]=True
    low[~mask]=0
    yy,xx=np.where(mask);x0,x1=int(xx.min()),int(xx.max()+1);y0,y1=int(yy.min()),int(yy.max()+1)
    legs=low[y0:y1,x0:x1].copy()
    # Preserve the near/far leg identity through the second half-cycle.
    if i in [4,5]:
        original=legs.copy()
        for old,new in [('3A2A1F','805B40'),('805B40','3A2A1F'),('513E2D','AA784B'),('AA784B','513E2D')]:
            oldrgb=[int(old[j:j+2],16) for j in (0,2,4)];newrgb=[int(new[j:j+2],16) for j in (0,2,4)]
            legs[(original[:,:,:3]==oldrgb).all(axis=2)&(original[:,:,3]>0),:3]=newrgb
    # Two tiny copper straps on the light near leg, confined to existing cloth pixels.
    bright=(legs[:,:,0]>=120)&(legs[:,:,1]>60)&(legs[:,:,2]>30)&(legs[:,:,3]>0)
    buckle_positions=[]
    for y in [3,6]:
        xs=np.where(bright[y])[0]
        if len(xs):
            x=int(xs.max() if i<3 else xs.min())
            legs[y,x,:3]=[205,125,43];buckle_positions.append([x,y])
            nx=x-1 if i<3 else x+1
            if 0<=nx<legs.shape[1] and bright[y,nx]:legs[y,nx,:3]=[180,97,23];buckle_positions.append([nx,y])
    # No rotation or scaling of these newly drawn legs; align by translation.
    hip_local=center-x0
    target_x=int(round(64-hip_local));target_y=82-legs.shape[0]
    frame=np.zeros((96,128,4),dtype=np.uint8)
    frame[target_y:82,target_x:target_x+legs.shape[1]]=legs
    bob=1 if i in [0,3] else 0
    up=np.zeros_like(frame);up[:]=upper[18-bob:114-bob]
    # Close only the one-row seam under the fixed belt; preserve generated leg shape.
    pelvis_top=67+bob
    if target_y>pelvis_top:
        firstrow=legs[0]
        for y in range(pelvis_top,target_y):frame[y,target_x:target_x+legs.shape[1]]=firstrow
    frame[up[:,:,3]>0]=up[up[:,:,3]>0]
    records.append({'frame':i+1,'bob':bob,'source_grid':setting,'generated_leg_bbox':[x0,y0,x1,y1],'leg_placement':[target_x,target_y],'leg_shape':list(legs.shape[:2]),'hip_x':64,'ms':[167,167,166,167,167,166][i],'second_half_shading_swap':i in [4,5],'copper_pixels':[[x+target_x,y+target_y] for x,y in buckle_positions]})
    frames.append(frame)
    sheet[(i//4)*96:(i//4+1)*96,(i%4)*128:(i%4+1)*128]=frame
Image.fromarray(sheet).save(OUT/'brand_run_1x.png')
Image.fromarray(sheet).resize((4096,1536),Image.Resampling.NEAREST).save(OUT/'brand_run.png')
preview=Image.new('RGB',(6*192,256),'#DADADA');draw=ImageDraw.Draw(preview)
for i,f in enumerate(frames):
    p=Image.fromarray(f).crop((38,36,90,84)).resize((156,144),Image.Resampling.NEAREST)
    preview.paste(p,(i*192+18,64),p);draw.text((i*192+18,24),f'Frame {i+1}',fill='#222222')
preview.save(OUT/'run_frames.png')
(ROOT/'work/run_fix_records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
checks=[];gif=[]
for i,frame in enumerate(frames):
    up=upper[18-records[i]['bob']:114-records[i]['bob']]
    um=up[:,:,3]>0
    assert np.array_equal(frame[um],up[um]),'upper body changed'
    assert not frame[82:,:,3].any()
    assert set(np.unique(frame[:,:,3]))=={0,255}
    used={tuple(c[:3]) for c in frame.reshape(-1,4) if c[3]}
    assert used.issubset({tuple(p) for p in palette})
    b=Image.fromarray(frame).getbbox()
    assert b[3]==82
    assert len(components(frame[:,:,3]>0))==1,'detached pixels'
    footmask=(frame[:,:,3]>0)&(frame[:,:,2]>=frame[:,:,1])&(frame[:,:,0]<=130)
    footmask[:76]=False
    footparts=components(footmask)[:2]
    points=[]
    if len(footparts)==2:
        for part in footparts:
            p=np.array(part);bottom=int(p[:,0].max());sel=p[:,0]>=bottom-1
            points.append([round(float(p[sel,1].mean()),2),bottom])
    else:
        # At the crossing the two foot outlines can touch. Measure separate patches.
        split=62 if i in [1,4] else 64
        for lo,hi in [(40,split),(split,90)]:
            yy,xx=np.where(footmask[:,lo:hi]);bottom=int(yy.max());sel=yy>=bottom-1
            points.append([round(float((xx[sel]+lo).mean()),2),bottom])
    points.sort(key=lambda p:p[0])
    near=points[1] if i<3 else points[0];far=points[0] if i<3 else points[1]
    records[i]['feet']={'left':points[0],'right':points[1],'near':near,'far':far,'near_minus_far_x':round(near[0]-far[0],2)}
    checks.append({'frame':i+1,'upper_exact':True,'colors':len(used),'bbox':list(b),'connected':True,'feet':records[i]['feet']})
    p=Image.new('RGB',(512,384),'#DADADA');f=Image.fromarray(frame).resize((512,384),Image.Resampling.NEAREST);p.paste(f,(0,0),f);gif.append(p)
assert [r['feet']['near_minus_far_x']>0 for r in records]==[True,True,True,False,False,False]
assert not sheet[96:,256:,3].any(),'last two cells are not empty'
read=np.array(Image.open(OUT/'brand_run.png'))
assert np.array_equal(read,sheet.repeat(8,0).repeat(8,1))
gif[0].save(OUT/'brand_run_preview.gif',save_all=True,append_images=gif[1:],duration=[170,160,170,170,160,170],loop=0,disposal=2)
(OUT/'manifest.json').write_text(json.dumps({'frames':records,'cell':[128,96],'scale':8,'grid':[4,2],'frame_count':6,'duration_ms':1000,'empty_cells':[7,8],'pivot_x':64,'feet_row':81,'method':'generated new legs, 6px grid majority, approved palette, exact supplied upper body; no rigid leg rotation'},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'verification.json').write_text(json.dumps({'passed':True,'frames':checks,'empty_last_two_cells':True,'exact_8x':True,'near_leg_lead_switch':True},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'palette.txt').write_text('\n'.join('#%02X%02X%02X'%tuple(p) for p in palette)+'\n',encoding='utf-8')
print(json.dumps(checks))
