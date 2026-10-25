from pathlib import Path
from PIL import Image
import numpy as np
import re, json, hashlib

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE if (HERE/'raw').exists() else BASE/'outputs/kled_fx'
JOB_PATH = HERE/'generation-jobs.json' if (HERE/'generation-jobs.json').exists() else BASE/'work/kled-jobs.json'
JOBS = json.loads(JOB_PATH.read_text(encoding='utf-8'))
(ROOT/'pixel_1x').mkdir(exist_ok=True)
(ROOT/'previews').mkdir(exist_ok=True)
manifest=[]
for job in JOBS:
    if job['kind'] != 'fx': continue
    src = ROOT/'raw'/job['file']
    if not src.exists(): continue
    im=Image.open(src).convert('RGBA')
    original_size=list(im.size)
    n=job['frames']; cw,ch=job['cell_1x']
    expected_ratio=n*cw/ch
    crop_box=None
    if im.width/im.height < expected_ratio*.85:
        alpha=np.asarray(im)[:,:,3]
        ys,xs=np.where(alpha>=128)
        if len(ys):
            margin=max(1,round(im.width/(n*cw)))
            crop_box=[0,max(0,int(ys.min())-margin),im.width,min(im.height,int(ys.max())+1+margin)]
            im=im.crop(crop_box)
    a=np.array(im)
    # Colors are selected from this effect's requested ramps. Index 0 is transparent.
    hexes=list(dict.fromkeys(re.findall(r'#[0-9A-Fa-f]{6}', job['prompt'])))
    hexes=[h for h in hexes if h.lower()!='#000000']
    pal=np.array([[0,0,0,0]]+[[int(h[k:k+2],16) for k in (1,3,5)]+[255] for h in hexes],dtype=np.uint8)
    frames=[]; counts=[]
    for f in range(n):
        # Equal source cells follow the explicit horizontal-sheet generation contract.
        x0=round(f*im.width/n); x1=round((f+1)*im.width/n)
        cell=a[:,x0:x1]
        grid=np.zeros((ch,cw,4),dtype=np.uint8)
        for y in range(ch):
            ya=round(y*im.height/ch);yb=max(ya+1,round((y+1)*im.height/ch))
            for x in range(cw):
                xa=round(x*cell.shape[1]/cw);xb=max(xa+1,round((x+1)*cell.shape[1]/cw))
                patch=cell[ya:yb,xa:xb].reshape(-1,4)
                ids=np.zeros(len(patch),dtype=np.int16)
                mask=(patch[:,3]>=128)&(patch[:,:3].max(axis=1)>16)
                if mask.any():
                    delta=patch[mask,:3].astype(np.int32)[:,None,:]-pal[None,1:,:3].astype(np.int32)
                    ids[mask]=1+np.argmin((delta*delta).sum(axis=2),axis=1)
                winner=0
                # Preserve thin generated sparks: coverage is separate from color majority.
                if np.count_nonzero(ids) >= len(ids)*.15:
                    winner=1+int(np.bincount(ids[ids>0]-1,minlength=len(pal)-1).argmax())
                grid[y,x]=pal[winner]
        # Enforce exact per-frame symmetry, preserving the chosen generated half.
        if job['symmetry']=='left-right':
            for x in range(cw//2): grid[:,cw-1-x]=grid[:,x]
        else:
            for y in range(ch//2): grid[ch-1-y]=grid[y]
        counts.append(int((grid[:,:,3]>0).sum()))
        frames.append(grid)
    sheet=Image.fromarray(np.concatenate(frames,axis=1))
    sheet.save(ROOT/'pixel_1x'/job['file'])
    sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST).save(ROOT/job['file'])
    pilframes=[Image.fromarray(f) for f in frames]
    # GIF is a review artifact; the transparent PNGs are the import source.
    preview=[]
    for fr in pilframes:
        bg=Image.new('RGBA',fr.size,'#1c222b');bg.alpha_composite(fr)
        preview.append(bg.convert('RGB').resize((cw*8,ch*8),Image.Resampling.NEAREST))
    preview[0].save(ROOT/'previews'/(job['id']+'.gif'),save_all=True,append_images=preview[1:],duration=110,loop=0)
    assert set(np.unique(np.asarray(sheet)[:,:,3])).issubset({0,255})
    for frame in frames:
        reflected=np.flip(frame,axis=1 if job['symmetry']=='left-right' else 0)
        assert np.array_equal(frame,reflected)
    manifest.append({
        'binding':job.get('binding'),'runtime_binding_tested':False,'file':job['file'],'frames':n,'cell_1x':[cw,ch], 'symmetry':job['symmetry'],
        'source_size':original_size,'sampling_crop':crop_box,'pixel_1x_size':list(sheet.size),'preview_scale':8,
        'opaque_pixels_per_frame':counts,'nonempty_frames':all(v>0 for v in counts),
        'raw_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'method':'Equal-cell foreground-color majority after nearest requested-palette quantization; alpha128 with 15% source-pixel coverage to preserve thin sparks; black fallback removed; left/top half reflected for exact symmetry.',
        'aspect_ratio_error':round(abs(im.width/im.height-(n*cw/ch))/(n*cw/ch),4),
    })
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'processed':len(manifest),'total':21,'empty':[m['file'] for m in manifest if not m['nonempty_frames']],'aspect_warnings':[m['file'] for m in manifest if m['aspect_ratio_error']>.15]},ensure_ascii=False))
