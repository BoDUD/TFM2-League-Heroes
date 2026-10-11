from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent; SRC=OUT/'raw/input'
from rig_primitives import Part,mask_rows,rot90,place,put
OUT.mkdir(parents=True,exist_ok=True)
for s in ['parts','previews','raw']:(OUT/s).mkdir(exist_ok=True)
design=np.array(Image.open(SRC/'design/zeri_design_1x.png').convert('RGBA'))
head=np.array(Image.open(SRC/'design/zeri_head_1x.png').convert('RGBA'))
# The supplied head mask omits the right bun's last columns. Preserve those
# approved source squares with the head, rather than leaving floating crumbs.
for y in range(62,69):
    for x in range(69,72 if y in (64,65) else 71):
        if design[y,x,3]:head[y,x]=design[y,x]
spec=json.loads((SRC/'zeri_cells.json').read_text())
palette={tuple(c) for c in design[design[...,3]>0,:3]}
def rows_mask(spec):return mask_rows(spec)&(design[...,3]>0)
right=rows_mask({**{y:(71,76) for y in range(60,69)},69:(70,76),70:(69,75),71:(69,74),72:(69,73),73:(69,74),74:(69,75),75:(69,75),76:(69,76),77:(70,75),78:(70,74),79:(71,73),80:(71,72),81:(70,72),82:(70,72)}) & ~(head[...,3]>0)
left=rows_mask({78:(53,55),79:(54,56),80:(54,56),81:(53,56),82:(53,56),83:(54,56),84:(54,56),85:(54,56),86:(53,55),87:(53,56),88:(53,56),89:(53,55),90:(54,54)})
legL=rows_mask({88:(58,62),89:(58,61),90:(57,61),91:(56,60),92:(56,59),93:(55,58),94:(54,59),95:(54,59),96:(54,59),97:(54,60),98:(54,60),99:(55,60)})
legR=rows_mask({88:(66,69),89:(66,69),90:(66,70),91:(67,70),92:(67,70),93:(67,71),94:(67,72),95:(67,72),96:(67,73),97:(68,74),98:(67,74),99:(68,74)})
hm=head[...,3]>0
assert not (right&hm).any() and not (left&hm).any()
rightP=Part.from_canvas(design,right,(70,81));leftP=Part.from_canvas(design,left,(55,80))
right_hand=right & mask_rows({y:(72,74) for y in range(73,80)})
left_hand=left & mask_rows({y:(53,56) for y in range(83,91)})
rightHP=Part.from_canvas(design,right_hand,(70,81))
leftHP=Part.from_canvas(design,left_hand,(55,80))
lp=Part.from_canvas(design,legL,(60,88));rp=Part.from_canvas(design,legR,(68,88))
body=design.copy();body[right|left|legL|legR|hm]=0
# Reconstruct only the small coat patch concealed by each original shoulder.
# All added colors are sampled from the accepted coat. Arms cover it in idle.
for y in range(79,84):
    for x in range(54,57):
        if left[y,x]:body[y,x]=[3,87,134,255] if x==54 else [1,126,158,255]
for y in range(79,83):
    for x in range(70,73):
        if right[y,x]:body[y,x]=[3,87,134,255] if x<72 else [10,4,17,255]
for name,mask in [('head',hm),('rifle_arm',right),('free_arm',left),('left_leg',legL),('right_leg',legR)]:
    a=np.zeros_like(design);a[mask]=design[mask];Image.fromarray(a).save(OUT/'parts'/f'{name}_1x.png')
Image.fromarray(body).save(OUT/'parts/body_1x.png')
def pose(shoot=False,left_turn=0,left_offset=(0,0),right_offset=(0,0),lmove=(0,0),rmove=(0,0),lflip=False,rflip=False,offset=(0,0)):
    a=body.copy()
    place(a,lp.flip_h() if lflip else lp,(60+lmove[0],88+lmove[1]))
    place(a,rp.flip_h() if rflip else rp,(68+rmove[0],88+rmove[1]))
    # Cast shoulder anchor remains at the outer edge of the coat, gun/arm rotate together.
    ra=rot90(rightP,1) if shoot else rightP
    rat=(70+right_offset[0],(79 if shoot else 81)+right_offset[1])
    la=rot90(leftP,left_turn)
    lat=(55+left_offset[0],80+left_offset[1])
    place(a,la,lat);place(a,ra,rat)
    put(a,head,0,0)
    hands=np.zeros_like(a)
    place(hands,rot90(leftHP,left_turn),lat)
    place(hands,rot90(rightHP,1) if shoot else rightHP,rat)
    handmask=hands[...,3]>0
    assert np.array_equal(a[handmask],hands[handmask]),'An original hand is occluded'
    if offset!=(0,0):
        b=np.zeros_like(a);put(b,a,*offset);a=b
    # Native muzzle pixel, transformed with the rifle arm.
    if shoot:muzzle=(89+right_offset[0]+offset[0],82+right_offset[1]+offset[1])
    else:muzzle=(73+right_offset[0]+offset[0],61+right_offset[1]+offset[1])
    return a,muzzle,offset
idle=pose()[0]
assert np.array_equal(idle,design),'Part partition must reproduce the accepted model exactly'
poses={}
stride=[(-2,0,2,-2),(0,-1,0,-3),(1,-2,-1,-1),(2,-2,-2,0),(2,-2,-2,0),(0,-3,0,-1),(-1,-1,1,-2),(-2,0,2,-2)]
poses['run']=[pose(lmove=(lx,ly),rmove=(rx,ry),left_offset=(0,(-1 if i<4 else 0)),offset=(0,-1 if i in [2,6] else 0)) for i,(lx,ly,rx,ry) in enumerate(stride)]
poses['attack']=[pose(),pose(shoot=True,left_turn=3),pose(shoot=True,left_turn=3,offset=(-1,0)),pose(shoot=True,left_turn=3),pose()]
poses['skill']=[pose(right_offset=(0,-1)),pose(shoot=True,left_turn=3),pose(shoot=True,left_turn=3,offset=(-1,0)),pose(shoot=True,left_turn=3,offset=(-2,0)),pose()]
poses['skill2']=[pose(lmove=(0,-1),rmove=(0,-1),offset=(0,1)),pose(lmove=(-3,-2),rmove=(-2,-3),left_turn=3,offset=(2,-1)),pose(lmove=(2,-1),rmove=(-1,-2),offset=(1,0)),pose()]
poses['skill2_back']=[pose(lmove=(0,-1),rmove=(0,-1),offset=(0,1)),pose(lmove=(-1,-2),rmove=(1,-2),offset=(-2,-2)),pose(lmove=(-1,-1),rmove=(0,-1),offset=(-1,1)),pose()]
poses['ult']=[pose(lmove=(0,-1),rmove=(0,-1),offset=(0,1)),pose(left_turn=3,left_offset=(-1,-1),right_offset=(1,-1),offset=(0,-2)),pose(left_offset=(-1,0),lmove=(-1,0),rmove=(1,0)),pose()]
poses['hit']=[pose(offset=(-2,0)),pose(offset=(-1,0))]
# Never resample the model at 45 degrees. Lossless rigid 90-degree fall instead.
fallen=np.rot90(design,-1).copy()
yy,xx=np.nonzero(fallen[...,3]);fall=fallen[yy.min():yy.max()+1,xx.min():xx.max()+1]
def death_frame(dx=0):
    a=np.zeros_like(design);put(a,fall,64-fall.shape[1]//2+dx,100-fall.shape[0]);return a,None,None
poses['dead']=[pose(offset=(-2,0)),pose(lmove=(0,-2),rmove=(0,-2),offset=(-2,2)),pose(lmove=(0,-3),rmove=(0,-3),offset=(-3,3)),death_frame(),death_frame(),death_frame(),death_frame(),death_frame()]
shutil.copy2(SRC/'zeri_idle.png',OUT/'zeri_idle.png');shutil.copy2(SRC/'zeri_cells.json',OUT/'zeri_cells.json')
shutil.copy2(SRC/'design/zeri_design_1x.png',OUT/'raw/approved_design_1x.png')
shutil.copy2(SRC/'design/zeri_head_1x.png',OUT/'raw/approved_head_1x.png')
manifest=dict(cell=[80,72],scale=8,pivot_source='zeri_cells.json',sole_row=59,palette=['#%02X%02X%02X'%c for c in sorted(palette)],route='lossless approved-model part rig; translation, flip, quarter turns only',release={'attack':{'frame':3,'tick':8},'skill':{'frame':4,'tick':16},'ult':{'frame':3,'tick':9}},tags={})
manifest['source_sha256']=hashlib.sha256((SRC/'design/zeri_design_1x.png').read_bytes()).hexdigest()
manifest['native_body_bbox']=[53,60,77,100]
manifest['head_mask_note']='Original mask plus approved right bun tip at x69-71, y62-68; no redraw.'
idle_strip=np.array(Image.open(OUT/'zeri_idle.png').convert('RGBA'))[4::8,4::8]
idle_records=[]
for i,t in enumerate(spec['tags']['idle']):
    x0=i%3*80;y0=i//3*72;c=idle_strip[y0:y0+72,x0:x0+80]
    ys,xs=np.nonzero(c[...,3]);assert not c[60:,:,3].any()
    idle_records.append(dict(frame=i+1,rect=[x0,y0,80,72],pivot=t['pivot'],ms=t['ms'],bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],muzzle=[73+t['pivot'][0]-64,61+t['pivot'][1]-88]))
manifest['tags']['idle']=dict(image='zeri_idle.png',size=list(Image.open(OUT/'zeri_idle.png').size),copied_unchanged=True,frames=idle_records)
assert hashlib.sha256((SRC/'zeri_idle.png').read_bytes()).digest()==hashlib.sha256((OUT/'zeri_idle.png').read_bytes()).digest()
contact=Image.new('RGB',(8*192,8*210),'#EEEEF0');draw=ImageDraw.Draw(contact)
checks=[]
for row,(tag,frames) in enumerate(poses.items()):
    n=len(frames);columns={2:2,4:4,5:3,8:4}[n];nr=(n+columns-1)//columns
    strip=np.zeros((nr*72,columns*80,4),np.uint8);records=[];gif=[]
    for i,((a,muzzle,offset),timing) in enumerate(zip(frames,spec['tags'][tag])):
        p=timing['pivot'];dx=p[0]-64;dy=p[1]-88
        cell=np.zeros((72,80,4),np.uint8);put(cell,a,dx,dy)
        assert not cell[60:,:,3].any(),(tag,i,'below soles')
        assert (cell[...,3]>0).sum()==(a[...,3]>0).sum(),(tag,i,'cell clipped source pixels')
        colors={tuple(c) for c in cell[cell[...,3]>0,:3]};assert colors<=palette
        assert set(np.unique(cell[...,3]))<={0,255}
        x0=i%columns*80;y0=i//columns*72;strip[y0:y0+72,x0:x0+80]=cell
        ys,xs=np.nonzero(cell[...,3]);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        expected=np.zeros_like(cell)
        if offset is not None:put(expected,head,dx+offset[0],dy+offset[1]);mask=expected[...,3]>0;assert np.array_equal(cell[mask],expected[mask]),(tag,i,'head changed')
        rec=dict(frame=i+1,rect=[x0,y0,80,72],pivot=p,ms=timing['ms'],bbox=bbox,pixels=int((cell[...,3]>0).sum()),sha256=hashlib.sha256(cell.tobytes()).hexdigest(),head_mode='exact_translation' if offset is not None else 'whole_model_quarter_turn',head_exact_translation=offset is not None)
        if muzzle:rec['muzzle']=[muzzle[0]+dx,muzzle[1]+dy]
        if manifest['release'].get(tag,{}).get('frame')==i+1:rec['release']=True
        records.append(rec)
        im=Image.fromarray(cell).resize((320,288),Image.Resampling.NEAREST)
        bg=Image.new('RGBA',im.size,'#EEEEF0');bg.alpha_composite(im);gif.append(bg.convert('RGB'))
        small=Image.fromarray(cell).resize((192,173),Image.Resampling.NEAREST)
        contact.paste(small,(i*192,row*210),small)
        draw.text((i*192+10,row*210+180),f'{tag} {i+1} / {timing["ms"]} ms',fill='#222222')
    zoom=np.repeat(np.repeat(strip,8,0),8,1);Image.fromarray(zoom).save(OUT/f'zeri_{tag}.png')
    Image.fromarray(strip).save(OUT/f'zeri_{tag}_1x.png')
    gif[0].save(OUT/'previews'/f'zeri_{tag}.gif',save_all=True,append_images=gif[1:],duration=[t['ms'] for t in spec['tags'][tag]],loop=0 if tag!='dead' else 1,disposal=2)
    manifest['tags'][tag]=dict(image=f'zeri_{tag}.png',size=[zoom.shape[1],zoom.shape[0]],frames=records)
    assert Image.open(SRC/'now'/f'zeri_now_{tag}.png').size==(zoom.shape[1],zoom.shape[0])
    if tag in ['attack','skill']:assert not strip[72:144,160:240,3].any(),'Unused sixth cell must be empty'
    checks.append(dict(tag=tag,frames=n,unique_frames=len(set(r['sha256'] for r in records)),grid=True,palette=True,alpha=True,sole=True,unclipped=True,head_translation_checked=tag!='dead',death_quarter_turn_source=tag=='dead'))
contact.save(OUT/'zeri_actions_contact.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'qa.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks))
