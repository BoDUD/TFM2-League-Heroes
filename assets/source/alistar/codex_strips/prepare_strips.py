from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json, shutil

src=Path('work/alistar-strips/alistar_strips_pack'); out=Path('outputs/alistar-strips')
cells=json.loads((src/'alistar_cells.json').read_text(encoding='utf-8'))
design=np.array(Image.open(src/'design/alistar_design_1x.png').convert('RGBA'))
palette=np.unique(design[design[:,:,3]>0,:3],axis=0)
head=Image.open(src/'design/alistar_head_1x.png').convert('RGBA').crop((62,66,85,84))
headarray=np.array(head)
manifest={'cell_1x':[128,96],'scale':8,'palette':[list(map(int,c)) for c in palette], 'status':'review_draft','tags':{},'coordinate_convention':'rect/bbox = x,y,width,height; frame and hit_frame are one-based'}
hitframes={'attack':4,'skill':4,'skill2':5,'ult':4}
ticks={'attack':12,'skill':14,'skill2':19,'ult':14}
allframes={}; audit={}

def majority_read(path,cols,rows):
    # Reconstruct the specified logical canvas from generator raster using mode,
    # not center samples, interpolation, row deletion or limb assembly.
    a=np.array(Image.open(path).convert('RGBA')); h,w=a.shape[:2]
    small=np.zeros((rows*96,cols*128,4),dtype=np.uint8)
    for y in range(small.shape[0]):
        y0=round(y*h/small.shape[0]);y1=max(y0+1,round((y+1)*h/small.shape[0]))
        for x in range(small.shape[1]):
            x0=round(x*w/small.shape[1]);x1=max(x0+1,round((x+1)*w/small.shape[1]))
            block=a[y0:y1,x0:x1].reshape(-1,4)
            green=(block[:,1]>190)&(block[:,0]<90)&(block[:,2]<100)
            solid=(block[:,3]>=128)&~green
            if solid.sum()<=len(block)/2:continue
            rgb=block[solid,:3].astype(np.int32)
            inds=((rgb[:,None,:]-palette[None,:,:].astype(np.int32))**2).sum(2).argmin(1)
            k=np.bincount(inds,minlength=len(palette)).argmax()
            small[y,x,:3]=palette[k];small[y,x,3]=255
    return small,[w,h]

def translate(a,dx,dy):
    result=np.zeros_like(a);h,w=a.shape[:2]
    sx=max(0,-dx);sy=max(0,-dy);ex=min(w,w-dx);ey=min(h,h-dy)
    if ex>sx and ey>sy:result[sy+dy:ey+dy,sx+dx:ex+dx]=a[sy:ey,sx:ex]
    return result

def bbox(a):
    yy,xx=np.where(a[:,:,3]>0)
    return [int(xx.min()),int(yy.min()),int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)] if len(xx) else None

def clean_fragments(a):
    mask=a[:,:,3]>0;seen=np.zeros(mask.shape,dtype=bool);h,w=mask.shape
    for y,x in np.argwhere(mask):
        if seen[y,x]:continue
        stack=[(y,x)];seen[y,x]=True;component=[]
        while stack:
            yy,xx=stack.pop();component.append((yy,xx))
            for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                ny,nx=yy+dy,xx+dx
                if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;stack.append((ny,nx))
        if len(component)<12 or (min(p[0] for p in component)<=2 and len(component)<150):
            for yy,xx in component:a[yy,xx]=0
    return a

for tag in ['idle','run','attack','skill','skill2','ult','hit','dead']:
    n=len(cells['tags'][tag]);cols=4 if n==8 else 2 if n==2 else 3;rows=1 if n==2 else 2
    if tag=='idle':
        a=np.array(Image.open(src/'alistar_idle.png').convert('RGBA'))[::8,::8]
        shutil.copy2(src/'alistar_idle.png',out/'alistar_idle.png');rawsize=[cols*1024,rows*768]
    else:a,rawsize=majority_read(out/f'raw/{tag}.png',cols,rows)
    frames=[];data=[]
    for i,meta in enumerate(cells['tags'][tag]):
        cx=i%cols;cy=i//cols;f=a[cy*96:(cy+1)*96,cx*128:(cx+1)*128].copy()
        corrections={}
        if tag!='idle':
            f=clean_fragments(f)
            yy,xx=np.where(f[:,:,3]>0)
            # Align the full figure, never slide upper body over still legs.
            sole=int(yy.max());lower=(yy>=sole-3)
            anchor=float(np.median(xx[lower]))
            dx=round(meta['pivot'][0]-anchor);dy=81-sole
            f=translate(f,dx,dy);corrections['whole_figure_translation']=[dx,dy]
            red=np.argwhere((f[:,:,:3]==[251,18,13]).all(2)&(f[:,:,3]>0))
            if len(red):ey,ex=np.mean(red,axis=0)
            else:ex,ey=meta['head'][0],meta['head'][1]+3
            # Allowed head-only replacement. Body parts are not pasted/assembled.
            x0=max(0,round(ex)-14);x1=min(128,round(ex)+13)
            y0=max(0,round(ey)-16);y1=min(82,round(ey)+6)
            f[y0:y1,x0:x1]=0
            h=head.rotate(90,expand=True) if tag=='dead' and i>=5 else head
            if tag=='run':
                hx=meta['pivot'][0]-2;hy=48+(i%2)
            elif tag=='dead' and i>=5:
                hx=max(1,round(ex)-h.width//2);hy=82-h.height
            else:
                hx=round(ex)-11;hy=round(ey)-12
            hx=max(0,min(128-h.width,hx));hy=max(0,min(82-h.height,hy))
            im=Image.fromarray(f);im.paste(h,(hx,hy),h);f=np.array(im)
            corrections['head_rect']=[hx,hy,h.width,h.height]
            corrections['head_rotation']=90 if tag=='dead' and i>=5 else 0
            target=np.array(h);m=target[:,:,3]>0
            assert np.array_equal(f[hy:hy+h.height,hx:hx+h.width][m],target[m])
            # Nothing is deleted below soles: whole figure was aligned there.
            assert not f[82:,:,3].any()
            if tag=='dead' and i==7:f=frames[6].copy();corrections={'copied_frame':7}
        frames.append(f)
        b=bbox(f); entry={'frame':i+1,'rect_1x':[cx*128,cy*96,128,96],'rect_px':[cx*1024,cy*768,1024,768],'pivot_1x':meta['pivot'],'pivot_px':[p*8 for p in meta['pivot']],'duration_ms':meta['ms'],'bbox_1x':b,'bbox_px':[p*8 for p in b],'corrections':corrections}
        if hitframes.get(tag)==i+1:
            entry['hit_tick']=ticks[tag]
            # Manually reviewed visible striking hands (cell-local coordinates).
            points={'attack':[[87,77]],'skill':[[65,79],[81,79]],'skill2':[],'ult':[[32,58],[83,58]]}
            entry['fist_positions_1x']=points[tag]
            entry['fist_positions_method']='visual estimate; review before hitbox import'
            if tag=='skill2':entry['contact_type']='headbutt';entry['head_contact_1x']=[corrections['head_rect'][0]+22,corrections['head_rect'][1]+12]
        data.append(entry)
    sheet=np.zeros((rows*96,cols*128,4),dtype=np.uint8)
    for i,f in enumerate(frames):sheet[(i//cols)*96:(i//cols+1)*96,(i%cols)*128:(i%cols+1)*128]=f
    im=Image.fromarray(sheet);im.save(out/f'alistar_{tag}_1x.png')
    if tag!='idle':im.resize((cols*1024,rows*768),Image.Resampling.NEAREST).save(out/f'alistar_{tag}.png')
    reread=np.array(Image.open(out/f'alistar_{tag}.png').convert('RGBA'))
    exact=np.array_equal(reread,np.repeat(np.repeat(sheet,8,0),8,1))
    actual=np.unique(sheet[sheet[:,:,3]>0,:3],axis=0)
    validcolors=all(any(np.array_equal(c,p) for p in palette) for c in actual)
    assert exact and validcolors and set(np.unique(sheet[:,:,3]))<={0,255}
    manifest['tags'][tag]={'file':f'alistar_{tag}.png','size_px':[cols*1024,rows*768],'raw_size_px':rawsize,'frames':data,'hit_frame':hitframes.get(tag)}
    audit[tag]={'grid_exact':exact,'palette_valid':validcolors,'alpha_binary':True,'colors':len(actual),'heights':[bbox(f)[3] for f in frames],'head_exact':tag!='idle','legs_exact':'not satisfied / needs artistic revision' if tag not in ['idle','run','dead'] else 'supplied idle / variable motion'}
    allframes[tag]=frames
    previews=[]
    for f in frames:
        bg=Image.new('RGBA',(128,96),'#252332');bg.alpha_composite(Image.fromarray(f));previews.append(bg.convert('RGB').resize((512,384),Image.Resampling.NEAREST))
    durations=[m['ms'] for m in cells['tags'][tag]]
    previews[0].save(out/f'preview_{tag}.gif',save_all=True,append_images=previews[1:],duration=durations,loop=0)

manifest['clips']={'butt':{'source':'skill2','frames':[5,6]},'slam':{'source':'skill','frames':[3,4,5,6]}}
for clip,definition in manifest['clips'].items():
    frames=[allframes[definition['source']][i-1] for i in definition['frames']]
    im=Image.fromarray(np.concatenate(frames,axis=1));im.save(out/f'alistar_{clip}_1x.png');im.resize((len(frames)*1024,768),Image.Resampling.NEAREST).save(out/f'alistar_{clip}.png')
    seq=[allframes['idle'][0]]+frames
    ims=[]
    for f in seq:
        bg=Image.new('RGBA',(128,96),'#252332');bg.alpha_composite(Image.fromarray(f));ims.append(bg.convert('RGB').resize((512,384),Image.Resampling.NEAREST))
    times=[250]+[cells['tags'][definition['source']][i-1]['ms'] for i in definition['frames']]
    ims[0].save(out/f'preview_idle_to_{clip}.gif',save_all=True,append_images=ims[1:],duration=times,loop=0)

# Compact contact sheet for review, frame order kept.
contact=Image.new('RGB',(1024,8*220),'#252332');d=ImageDraw.Draw(contact)
for row,(tag,frames) in enumerate(allframes.items()):
    d.text((10,row*220+5),tag,fill='white')
    for i,f in enumerate(frames):
        crop=Image.fromarray(f).crop((16,0,112,88)).resize((120,110),Image.Resampling.NEAREST)
        contact.paste(crop,(i*128,row*220+40),crop)
        d.text((i*128+4,row*220+160),str(i+1),fill='white')
contact.save(out/'contact_sheet.png')
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(out/'validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
shutil.copy2(src/'alistar_cells.json',out/'alistar_cells.json')
shutil.copytree(src/'design',out/'design',dirs_exist_ok=True)
print(json.dumps(audit))
