from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'outputs/kayle_ascend'
WORK=BASE/'work/kayle_ascend'
(OUT/'pixel_1x').mkdir(exist_ok=True)
HEX=['FFFFFF','FFF6C8','FFE27A','F7B931','C47A12','FFE6A8','FFB347','F07A1C','B8460C','FFFBEA','FFF0B0','DDEBFF','9CC4FF']
PAL=np.array([[int(c[i:i+2],16) for i in (0,2,4)] for c in HEX],dtype=np.int32)
NAMES=['wings1','wings2','wings3','bolt_x','wave_x','q_sword_x','e_bolt_x','bolt_hit_x','e_hit_x','q_blast_x','e_blast_x']
def clean(im):
    a=np.array(im.convert('RGBA'))
    mask=a[:,:,3]>=160
    lab,n=ndimage.label(mask)
    counts=np.bincount(lab.ravel()); good=counts>=max(8,int(mask.size*.000025));good[0]=False
    a[:,:,3]=np.where(good[lab],255,0)
    a[a[:,:,3]==0]=0
    return Image.fromarray(a)
def quant(im):
    a=np.array(im.convert('RGBA'));rgb=a[:,:,:3].astype(np.int32)
    dist=((rgb[:,:,None,:]-PAL[None,None,:,:])**2).sum(axis=3)
    out=np.zeros_like(a);out[:,:,:3]=PAL[dist.argmin(axis=2)];out[:,:,3]=np.where(a[:,:,3]>=110,255,0);out[out[:,:,3]==0]=0
    return Image.fromarray(out)
def resize(im,size):
    return quant(im.resize(size,Image.Resampling.BOX))
def lr(im):
    a=np.array(im);w=im.width;a[:,w//2:]=a[:,:w//2][:,::-1];return Image.fromarray(a)
def tb(im):
    a=np.array(im);h=im.height;a[h//2:]=a[:h//2][::-1];return Image.fromarray(a)
def crop(im):
    box=im.getchannel('A').getbbox();return im.crop(box) if box else im
def component(im,kind):
    a=np.array(im);lab,n=ndimage.label(a[:,:,3]>0);options=[]
    for idx,sl in enumerate(ndimage.find_objects(lab),1):
        if sl is None:continue
        area=int((lab[sl]==idx).sum());cy=(sl[0].start+sl[0].stop)/2;cx=(sl[1].start+sl[1].stop)/2
        if kind=='halo' and abs(cx-im.width/2)<im.width*.12 and cy<im.height*.4:
            options.append((area,idx,sl))
        if kind=='left' and cx<im.width*.42:
            options.append((area,idx,sl))
    _,idx,sl=max(options)
    a[lab!=idx]=0
    return Image.fromarray(a).crop((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop))
records=[];sheet_previews=[]
for name in NAMES:
    record=json.loads((WORK/(name+'.json')).read_text(encoding='utf-8'))
    w,h,n=record['w'],record['h'],record['n']
    raw=Image.open(OUT/'raw'/('kayle_fx_'+name+'.png')).convert('RGBA')
    cuts=[i/n for i in range(n+1)]
    if name=='e_hit_x':cuts=[0,.105,.280,.463,.660,.837,1]
    cells=[clean(raw.crop((round(cuts[i]*raw.width),0,round(cuts[i+1]*raw.width),raw.height))) for i in range(n)]
    boxes=[im.getchannel('A').getbbox() for im in cells]
    frames=[]
    for i,(im,box) in enumerate(zip(cells,boxes)):
        frame=Image.new('RGBA',(w,h))
        if name.startswith('wings'):
            # Retain generated left wing, mirror it exactly; registration only, no procedural artwork.
            left=im.crop((0,0,int(im.width*.43),im.height))
            if name=='wings3':
                # Halo is a separate generated object in the center above the roots.
                halo=resize(component(cells[0],'halo'),(14,4));frame.paste(halo,((w-14)//2,4))
                # Exclude any halo fringe from wing extraction.
                left=component(im,'left')
                wing=resize(crop(left),(w//2-7,30))
                frame.paste(wing,(1,3))
            elif name=='wings1':
                wing=resize(component(im,'left'),(w//2-7,20))
                frame.paste(wing,(1,h//2))
            else:
                wing=resize(crop(left),(w//2-7,23))
                frame.paste(wing,(1,3))
            frame=lr(frame)
        elif name in ['bolt_x','wave_x','q_sword_x','e_bolt_x']:
            # Fit the generated projectile to its specified cell with a one-column leading margin.
            tw,th=w-2,h-2
            frame.paste(resize(crop(im),(tw,th)),(1,1));frame=tb(frame)
            bb=frame.getchannel('A').getbbox();obj=frame.crop(bb)
            frame=Image.new('RGBA',(w,h));frame.paste(obj,(w-1-obj.width,bb[1]))
        else:
            # Use a common group scale; preserve growth/decay proportions between frames.
            maxw=max(b[2]-b[0] for b in boxes);maxh=max(b[3]-b[1] for b in boxes)
            bw,bh=box[2]-box[0],box[3]-box[1]
            tw=max(2,round(bw/maxw*(w-2)));tw=min(w-2,tw+(tw%2))
            th=max(2,round(bh/maxh*(h-6 if name=='e_blast_x' else h-2)))
            if name=='q_blast_x':th=min(h-2,th+(th%2))
            obj=resize(im.crop(box),(tw,th))
            y=h-4-th if name=='e_blast_x' else (h-th)//2
            frame.paste(obj,((w-tw)//2,y));frame=lr(frame)
            if name=='q_blast_x':frame=tb(frame)
        frames.append(frame)
    sheet=Image.new('RGBA',(w*n,h))
    for i,f in enumerate(frames):sheet.paste(f,(i*w,0))
    filename='kayle_fx_'+name+'.png'
    sheet.save(OUT/'pixel_1x'/filename)
    sheet.resize((w*n*16,h*16),Image.Resampling.NEAREST).save(OUT/filename)
    symmetry='left-right' if name.startswith('wings') or name.endswith('hit_x') or name=='e_blast_x' else 'top-bottom'
    if name=='q_blast_x':symmetry='both'
    records.append(dict(name=name,file=filename,cell=[w,h],frames=n,sheet_1x=[w*n,h],sheet_16x=[w*n*16,h*16],symmetry=symmetry,anchor=[w/2,h/2] if name.startswith('wings') else None,frame_ms_preview=100 if name.startswith('wings') else 60 if 'blast' in name else 50 if 'hit' in name else 60,source_sha256=hashlib.sha256((OUT/'raw'/filename).read_bytes()).hexdigest()))
    # Compact inspection board, nearest-neighbor only.
    s=min(5,1000//sheet.width)
    thumb=sheet.resize((sheet.width*s,sheet.height*s),Image.Resampling.NEAREST)
    sheet_previews.append((name,thumb))
manifest={'generator':'built-in image_gen','technical_normalization_authorized':True,'palette':['#'+c for c in HEX],'animation_count':11,'frame_count':sum(r['frames'] for r in records),'timing_note':'Preview timings only; new pack does not define engine durations. Preserve existing engine durations on import.','assets':records}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
board=Image.new('RGB',(1040,sum(t.height+38 for _,t in sheet_previews)),(27,29,40));draw=ImageDraw.Draw(board);y=0
for name,thumb in sheet_previews:
    draw.text((12,y+6),name,fill='white');board.paste(thumb,(12,y+30),thumb);y+=thumb.height+38
board.save(OUT/'preview_sheet.png')
print(json.dumps({'assets':len(records),'frames':manifest['frame_count'],'board':str(OUT/'preview_sheet.png')}))
