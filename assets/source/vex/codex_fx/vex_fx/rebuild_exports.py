from pathlib import Path
import json,re,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parent
specs=json.loads((root/'source_specs.json').read_text(encoding='utf-8'))
ramps={
 'mint':['FFFFFF','D6FFF2','8CF5D6','3EDDB4','1E9C8A','0E5A5A'],
 'shadow':['E8E4FF','A98CFF','7A3CFF','4A1E9E','261055','120830'],
 'eyes':['FFFFFF','CFF7FC','8EC8FF']}
manifest=[]
previews=[]
for s in specs:
    name=s['file']; key=name[7:-4]; n=s['frames']; w,h=map(int,re.findall(r'\d+',s['size']))
    groups=['mint'] if key in ('g_mark','g_pop') else ['shadow'] if key=='e_slow' else ['shadow','eyes'] if key=='r_mark' else ['mint','shadow','eyes']
    hexes=list(dict.fromkeys(c for group in groups for c in ramps[group]))
    pal=np.array([[int(c[i:i+2],16) for i in (0,2,4)] for c in hexes],dtype=np.int32)
    im=Image.open(root/'raw'/name).convert('RGBA'); a=np.array(im); H,W=a.shape[:2]
    projection=(a[:,:,3]>=112).sum(0).astype(float)
    smooth=np.convolve(projection,np.ones(7)/7,mode='same')
    boundaries=[0]
    for i in range(1,n):
        mid=round(i*W/n); radius=round(W/n*.22)
        candidates=np.arange(mid-radius,mid+radius+1)
        score=smooth[candidates]+np.abs(candidates-mid)/max(1,radius)*.5
        boundaries.append(int(candidates[score.argmin()]))
    boundaries.append(W)
    frames=[]
    max_width=max(np.diff(boundaries))
    for i in range(n):
        frame=a[:,boundaries[i]:boundaries[i+1]]
        padded=np.zeros((H,max_width,4),dtype=np.uint8)
        offset=(max_width-frame.shape[1])//2
        padded[:,offset:offset+frame.shape[1]]=frame
        frames.append(padded)
    # Shared crop retains relative frame scale and phase; no per-frame enlargement.
    boxes=[]
    for f in frames:
        yy,xx=np.where(f[:,:,3]>=112)
        boxes.append((int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1))
    x0=min(b[0] for b in boxes); y0=min(b[1] for b in boxes)
    x1=max(b[2] for b in boxes); y1=max(b[3] for b in boxes)
    output=[]; frame_info=[]
    for i,f in enumerate(frames):
        crop=f[y0:y1,x0:min(x1,f.shape[1])]
        # Explicitly authorized regrid: palette classification then majority vote per target cell.
        # Keep a transparent border. E cast occupies overhead area, not the actor body.
        tw,th=w-2,h-2
        if key=='e_cast': th=16
        yy=np.linspace(0,crop.shape[0],th+1).round().astype(int)
        xx=np.linspace(0,crop.shape[1],tw+1).round().astype(int)
        out=np.zeros((h,w,4),dtype=np.uint8)
        for cy in range(th):
            for cx in range(tw):
                block=crop[yy[cy]:yy[cy+1],xx[cx]:xx[cx+1]]
                pixels=block.reshape(-1,4)
                if not len(pixels):continue
                valid=pixels[:,3]>=112
                if valid.sum()<=len(pixels)//2:continue
                colors=pixels[valid,:3].astype(np.int32)
                dist=((colors[:,None,:]-pal[None,:,:])**2).sum(2)
                bins=np.bincount(dist.argmin(1),minlength=len(pal))
                color=pal[bins.argmax()]
                out[cy+1,cx+1]=[*color,255]
        # Pairwise symmetry: prefer the brighter of the two sampled pixels,
        # retaining highlights rather than introducing an invented shape.
        reflected=out[:,::-1] if s['symmetry']=='left-right' else out[::-1,:]
        score=out[:,:,:3].sum(2).astype(int)+out[:,:,3].astype(int)*4
        rscore=reflected[:,:,:3].sum(2).astype(int)+reflected[:,:,3].astype(int)*4
        out=np.where((rscore>score)[:,:,None],reflected,out)
        # Ties use canonical half so RGB symmetry holds even for equal-brightness colors.
        if s['symmetry']=='left-right':out[:,w//2:]=out[:,:w-w//2][:,::-1]
        else:out[h//2:]=out[:h-h//2][::-1]
        if key=='w_shield':out[14:42,5:29]=0
        if key=='e_cast':out[16:]=0
        out[out[:,:,3]==0]=0
        frame=Image.fromarray(out); output.append(frame)
        frame_info.append({'index':i,'bbox':frame.getbbox(),'opaque_pixels':int((out[:,:,3]==255).sum())})
    sheet=Image.new('RGBA',(n*w,h))
    for i,frame in enumerate(output):sheet.paste(frame,(i*w,0))
    sheet.save(root/'pixel_1x'/name)
    sheet.resize((n*w*8,h*8),Image.Resampling.NEAREST).save(root/name)
    rgba=np.array(sheet)
    checks={'size':sheet.size== (n*w,h),'hard_alpha':set(np.unique(rgba[:,:,3]).tolist()) <= {0,255},
      'symmetry':all(np.array_equal(np.array(f),np.array(f)[:,::-1] if s['symmetry']=='left-right' else np.array(f)[::-1]) for f in output),
      'nonempty_frames':all(f['opaque_pixels']>0 for f in frame_info)}
    if key=='w_shield':checks['body_area_clear']=all(not np.array(f)[14:42,5:29,3].any() for f in output)
    if key=='e_cast':checks['body_area_clear']=all(not np.array(f)[16:,:,3].any() for f in output)
    assert all(checks.values()),(name,checks)
    manifest.append({'file':name,'frames':n,'cell_1x':[w,h],'sheet_1x':[n*w,h],'preview_scale':8,
       'symmetry':s['symmetry'],'binding':s['binding'],'loop':key in ('a_bolt','q_bolt','e_slow','g_mark','r_missile','r_mark'),
       'raw_size':[W,H],'raw_cell_boundaries_x':boundaries,'raw_crop_per_cell':[x0,y0,x1,y1], 'frame_details':frame_info,'checks':checks,
       'palette':['#'+c for c in hexes], 'sha256_1x':hashlib.sha256((root/'pixel_1x'/name).read_bytes()).hexdigest()})
    previews.append((key,output))
    # Preview timing is illustrative only, not an engine timing contract.
    gif=[]
    scale=min(8,320//max(w,h))
    for f in output:
        bg=Image.new('RGB',(w*scale,h*scale),(24,29,40));bg.paste(f.resize(bg.size,Image.Resampling.NEAREST),mask=f.resize(bg.size,Image.Resampling.NEAREST).getchannel('A'));gif.append(bg)
    (root/'previews').mkdir(exist_ok=True)
    gif[0].save(root/'previews'/f'{key}.gif',save_all=True,append_images=gif[1:],duration=120,loop=0)
(root/'manifest.json').write_text(json.dumps({'schema_version':1,'source':'image_gen','export_method':'per-cell palette majority; alpha112 threshold; explicit symmetry; actor exclusion masks','effects':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
contact=Image.new('RGB',(1100,16*150),(24,29,40));d=ImageDraw.Draw(contact)
for row,(key,frames) in enumerate(previews):
    d.text((12,row*150+5),key,fill='white')
    for i,f in enumerate(frames):
        scale=min(6,165//f.width,110//f.height)
        large=f.resize((f.width*scale,f.height*scale),Image.Resampling.NEAREST)
        contact.paste(large,(12+i*180,row*150+30),large)
contact.save(root/'overview.png')
print('Exported',len(manifest),'sheets;',sum(s['frames'] for s in specs),'frames. All structural checks passed.')

