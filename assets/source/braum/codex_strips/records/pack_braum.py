"""Extract generated animation sheets, quantize to source palette, package previews.
This exports generated art; it does not manufacture replacement body poses.
"""
from pathlib import Path
from collections import Counter
import json, shutil, zipfile
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'outputs' / 'braum-strips'
SOURCE = ROOT / 'work' / 'braum'
GENERATED = Path(r'C:\Users\OWNER\.codex\generated_images\01a13018-1a3e-7372-9838-fc67c9dd6134')
CONFIG = ROOT / 'work' / 'braum_sheets.json'

def export_cell(sheet, box, scale):
    a = np.array(sheet.crop(tuple(box)).convert('RGBA'))
    # Discard semitransparent generation fringe, keep largest connected actor.
    mask = a[:,:,3] >= 210
    labels, count = ndimage.label(mask)
    sizes = np.bincount(labels.ravel()); sizes[0] = 0
    if count == 0: raise ValueError('Empty generated cell')
    keep = np.flatnonzero(sizes >= max(60, sizes.max() * .01))
    mask = np.isin(labels, keep)
    ys,xs = np.where(mask)
    left,top,right,bottom = xs.min(),ys.min(),xs.max()+1,ys.max()+1
    a = a[top:bottom,left:right]; mask = mask[top:bottom,left:right]
    h,w = mask.shape
    tw,th = round(w*scale),round(h*scale)
    # Majority palette vote over each target pixel footprint, never center sampling.
    result = np.zeros((th,tw,4),np.uint8)
    for y in range(th):
        y0,y1 = round(y*h/th),round((y+1)*h/th)
        for x in range(tw):
            x0,x1 = round(x*w/tw),round((x+1)*w/tw)
            m = mask[y0:y1,x0:x1]
            if m.sum() < m.size/2: continue
            rgb = a[y0:y1,x0:x1,:3][m].astype(np.int32)
            dist = ((rgb[:,None,:]-PALETTE[None,:,:])**2).sum(axis=2)
            ids = dist.argmin(axis=1)
            color = np.bincount(ids,minlength=len(PALETTE)).argmax()
            result[y,x,:3] = PALETTE[color]
            result[y,x,3] = 255
    return Image.fromarray(result), [int(left+box[0]),int(top+box[1]),int(right+box[0]),int(bottom+box[1])]

design=np.array(Image.open(SOURCE/'design/braum_design_1x.png').convert('RGBA'))
PALETTE=np.unique(design[design[:,:,3]>0,:3],axis=0).astype(np.int32)

def main():
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    spec=json.loads((SOURCE/'cells.json').read_text(encoding='utf-8'))
    OUT.mkdir(parents=True,exist_ok=True)
    for folder in ('raw','previews','strips','records'): (OUT/folder).mkdir(exist_ok=True)
    shutil.copy2(SOURCE/'cells.json',OUT/'cells.json')
    shutil.copy2(SOURCE/'design/braum_design_1x.png',OUT/'records/approved_design_1x.png')
    rows=[]; animations={}
    for tag,c in cfg.items():
        raw=GENERATED/c['file']; shutil.copy2(raw,OUT/'raw'/f'{tag}_generated.png')
        sheet=Image.open(raw)
        frames=[]
        for i,box in enumerate(c['boxes']):
            sprite,source_box=export_cell(sheet,box,c['scale'])
            frame=Image.new('RGBA',(256,170))
            # Stable body anchor defined per frame, retain intentional aerial lift.
            x=c.get('x',68)+(c.get('dx',[0]*len(c['boxes']))[i])
            foot=c.get('foot',[163]*len(c['boxes']))[i]
            y=foot-sprite.height
            if x<0 or y<0 or x+sprite.width>256: raise ValueError((tag,i,sprite.size,x,y))
            frame.alpha_composite(sprite,(x,y))
            name=f'braum_{tag}_{i+1}'
            frame.save(OUT/f'{name}_1x.png')
            big=Image.new('RGBA',(1536,1024))
            big.paste(frame.resize((1536,1020),Image.Resampling.NEAREST),(0,0))
            big.save(OUT/f'{name}.png')
            duration=next(f['ms'] for f in spec['frames'] if f['file']==name+'.png')
            rows.append({'file':name+'.png','source':f'raw/{tag}_generated.png','source_box':source_box,'ms':duration,'bbox':frame.getbbox(),'scale':c['scale']})
            frames.append((frame,duration))
        animations[tag]=frames
        strip=Image.new('RGBA',(256*len(frames),170))
        for i,(f,_) in enumerate(frames): strip.paste(f,(256*i,0))
        strip.save(OUT/'strips'/f'braum_{tag}_strip_1x.png')
        # Opaque presentation background prevents GIF disposal artifacts.
        gif=[]
        for f,_ in frames:
            bg=Image.new('RGBA',f.size,(30,35,47,255)); bg.alpha_composite(f)
            gif.append(bg.convert('RGB').resize((768,510),Image.Resampling.NEAREST))
        gif[0].save(OUT/'previews'/f'braum_{tag}.gif',save_all=True,append_images=gif[1:],duration=[d for _,d in frames],loop=0,disposal=2)
    contact=Image.new('RGB',(8*256,7*195),(30,35,47)); draw=ImageDraw.Draw(contact)
    for row,(tag,frames) in enumerate(animations.items()):
        for col,(f,_) in enumerate(frames):
            contact.paste(f,(col*256,row*195+20),f)
            draw.text((col*256+10,row*195+3),f'{tag} {col+1}',fill='white')
    contact.save(OUT/'previews/braum_all_frames.png')
    (OUT/'records/manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    checks=[]
    colors={tuple(v) for v in PALETTE.tolist()}
    for row in rows:
        small=np.array(Image.open(OUT/row['file'].replace('.png','_1x.png')))
        big=np.array(Image.open(OUT/row['file']))
        expected=np.repeat(np.repeat(small,6,axis=0),6,axis=1)
        assert big.shape==(1024,1536,4)
        assert np.array_equal(expected,big[:1020])
        assert not big[978:,:,3].any()
        assert set(np.unique(small[:,:,3])).issubset({0,255})
        assert all(tuple(v) in colors for v in np.unique(small[small[:,:,3]>0,:3],axis=0))
        checks.append({'file':row['file'],'format_palette_alpha_grid_baseline':'PASS'})
    assert len(rows)==38
    (OUT/'records/validation.json').write_text(json.dumps({'frames':len(rows),'palette_colors':len(PALETTE),'checks':checks,'visual_status':'generated approximation; exact head/shield pixel identity and pose parity NOT certified'},indent=2),encoding='utf-8')
    print(f'Exported and validated {len(rows)} frames in {OUT}')

if __name__=='__main__': main()
