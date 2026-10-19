from pathlib import Path
import json,re,shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label

OUT=Path(__file__).resolve().parent
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'raw').mkdir(exist_ok=True)
(OUT/'pixel_1x').mkdir(exist_ok=True)
specs=json.loads((OUT/'export-specs.json').read_text(encoding='utf-8'))
generations=json.loads((OUT/'export-sources.json').read_text(encoding='utf-8'))
latest={r['key']:r for r in generations}
manifest=[]
allframes={}

def color_ramp(s):
    # Fixed specified ramps; omit the darkest border-like shade of each ramp.
    excluded={'#7A4210','#5E2488','#6E1E3E'}
    colors=list(dict.fromkeys(h.upper() for h in re.findall(r'#[0-9A-Fa-f]{6}',s['prompt']) if h.upper() not in excluded and h.upper()!='#000000'))
    return colors,np.array([tuple(bytes.fromhex(h[1:])) for h in colors],dtype=np.uint8)

def source_mask(a):
    mask=(a[:,:,3]>=224)&(a[:,:,:3].max(axis=2)>=100)
    # Keep solid generated art, discard minute alpha-conversion speckle components.
    labels,n=label(mask)
    sizes=np.bincount(labels.ravel())
    good=sizes>=max(5,int(mask.size*.000006));good[0]=False
    return good[labels]

for s in specs:
    r=latest[s['key']]
    src=Image.open(OUT/r['path']).convert('RGBA')
    a=np.array(src)
    valid=source_mask(a)
    yy,xx=np.where(valid)
    if not len(xx):raise RuntimeError(s['key']+' empty source')
    # Common crop for all source frames preserves animation scale.
    box=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
    if s['key']=='a_hit':
        # Its three source frames already occupy equally spaced full-width cells;
        # cropping the smaller first flash would shift its pivot.
        box=[0,0,src.width,src.height]
    w,h=s['cell_1x'];cols=s['cols'];rows=s['rows']
    # Pad half a logical cell at outer edges, leaving breathing space.
    pad_x=(box[2]-box[0])/(cols*w)*.5
    pad_y=(box[3]-box[1])/(rows*h)*.5
    if s['key']=='a_hit':pad_x=pad_y=0
    x0,y0,x1,y1=box[0]-pad_x,box[1]-pad_y,box[2]+pad_x,box[3]+pad_y
    colors,palette=color_ramp(s)
    frames=[];frameqa=[]
    for frame in range(s['frames']):
        row,col=divmod(frame,cols)
        arr=np.zeros((h,w,4),dtype=np.uint8)
        for y in range(h):
            ya=max(0,int(round(y0+(row*h+y)*(y1-y0)/(rows*h))))
            yb=min(src.height,int(round(y0+(row*h+y+1)*(y1-y0)/(rows*h))))
            for x in range(w):
                xa=max(0,int(round(x0+(col*w+x)*(x1-x0)/(cols*w))))
                xb=min(src.width,int(round(x0+(col*w+x+1)*(x1-x0)/(cols*w))))
                region=a[ya:yb,xa:xb];m=valid[ya:yb,xa:xb]
                if not m.size or m.mean()<.22:continue
                pix=region[:,:,:3][m].astype(np.int16)
                d=((pix[:,None,:].astype(float)-palette[None,:,:].astype(float))**2).sum(axis=2)
                indices=d.argmin(axis=1)
                counts=np.bincount(indices,minlength=len(palette))
                ci=counts.argmax()
                arr[y,x,:3]=palette[ci];arr[y,x,3]=255
        # Enforce the supplied per-frame symmetry by selecting the brighter source
        # member of each mirrored pair, never drawing a new effect silhouette.
        mirrored=arr[:,::-1,:].copy() if s['symmetry']=='left-right' else arr[::-1,:,:].copy()
        lum=(arr[:,:,:3]*np.array([.2126,.7152,.0722])).sum(axis=2)* (arr[:,:,3]>0)
        ml=(mirrored[:,:,:3]*np.array([.2126,.7152,.0722])).sum(axis=2)*(mirrored[:,:,3]>0)
        arr=np.where((ml>lum)[:,:,None],mirrored,arr)
        # Clear the reserved central body region for following support effects.
        reserved=None
        if s['key']=='p_heal':reserved=(w//3,3,w-w//3,h-2)
        if s['key']=='e_hit':reserved=(w//3,3,w-w//3,h-3)
        if reserved:
            rx0,ry0,rx1,ry1=reserved;arr[ry0:ry1,rx0:rx1]=0
        # Palette-only lift of the brightest surviving source shade in a fading
        # frame; no pixels or effect geometry are added.
        bright_colors=np.array([[255,255,255],[255,244,200],[255,224,246],[255,228,238]],dtype=np.uint8)
        opacity=arr[:,:,3]>0
        has_core=any(np.any(np.all(arr[:,:,:3]==c,axis=2)&opacity) for c in bright_colors)
        lifted=None
        if opacity.any() and not has_core:
            unique=np.unique(arr[:,:,:3][opacity],axis=0)
            light=unique[np.argmax(unique@np.array([.2126,.7152,.0722]))]
            target=bright_colors[np.argmin(((bright_colors.astype(float)-light.astype(float))**2).sum(axis=1))]
            match=np.all(arr[:,:,:3]==light,axis=2)&opacity
            arr[match,:3]=target
            lifted=dict(source=light.tolist(),target=target.tolist())
        im=Image.fromarray(arr)
        mirror=arr[:,::-1,:] if s['symmetry']=='left-right' else arr[::-1,:,:]
        assert np.array_equal(arr,mirror),s['key']+' symmetry'
        assert set(np.unique(arr[:,:,3])).issubset({0,255})
        opaque=int((arr[:,:,3]>0).sum())
        frameqa.append(dict(frame=frame,opaque_pixels=opaque,nonempty=opaque>0,has_bright_core=any(bool(np.any(np.all(arr[:,:,:3]==c,axis=2)&opacity)) for c in bright_colors),palette_lift=lifted,bbox=im.getbbox(),reserved_body_region=reserved))
        frames.append(im)
    strip=Image.new('RGBA',(w*s['frames'],h))
    for i,im in enumerate(frames):strip.paste(im,(i*w,0))
    strip.save(OUT/'pixel_1x'/s['file'])
    big=strip.resize((strip.width*8,strip.height*8),Image.Resampling.NEAREST)
    big.save(OUT/s['file'])
    reconstructed=np.array(big).reshape(h,8,w*s['frames'],8,4)
    assert np.all(reconstructed==np.array(strip)[:,None,:,None,:])
    rawname=s['key']+'-generated.png'
    # Raw files are already included beside the script.
    allframes[s['key']]=frames
    manifest.append(dict(name=s['key'],file=s['file'],pixel_1x='pixel_1x/'+s['file'],raw='raw/'+rawname,frames=s['frames'],cell_1x=[w,h],cell_8x=[w*8,h*8],layout='horizontal-row',symmetry=s['symmetry'],binding=s['binding'],source_layout=[cols,rows],source_crop=box,palette=colors,frame_checks=frameqa,checks=dict(binary_alpha=True,symmetry=True,nearest_8x_match=True,all_frames_nonempty=all(q['nonempty'] for q in frameqa),all_frames_bright=all(q['has_bright_core'] for q in frameqa))))

(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
prompts=['Mode: built-in image_gen. All effect art AI-generated. Export: majority-color grid sampling, fixed supplied ramps, alpha threshold, per-frame symmetry, horizontal reflow, nearest-neighbor 8x.\n']
for r in generations:
    prompts.append('\n'+r['key']+(' retry' if r.get('retry') else '')+'\nReferences: '+', '.join(r['refs'])+'\n'+r['prompt']+'\n')
# Preserve the included original generation prompts.

def overview(tick):
    im=Image.new('RGB',(1200,1000),(22,27,39));d=ImageDraw.Draw(im)
    for i,s in enumerate(specs):
        x=i%4*300;y=i//4*200
        d.text((x+12,y+10),s['key']+' / '+str(s['frames'])+' frames',fill=(233,235,245))
        f=allframes[s['key']][tick%len(allframes[s['key']])]
        scale=min(6,260//f.width,155//f.height)
        z=f.resize((f.width*scale,f.height*scale),Image.Resampling.NEAREST)
        im.paste(z,(x+(300-z.width)//2,y+35+(155-z.height)//2),z)
    return im
overview(1).save(OUT/'overview.png')
sequence=[overview(i) for i in range(60)]
sequence[0].save(OUT/'preview.gif',save_all=True,append_images=sequence[1:],duration=130,loop=0)
summary=dict(effects=len(manifest),frames=sum(s['frames'] for s in specs),failures=[m['name'] for m in manifest if not m['checks']['all_frames_nonempty']],dim_frames=[(m['name'],[q['frame'] for q in m['frame_checks'] if not q['has_bright_core']]) for m in manifest if not m['checks']['all_frames_bright']])
print(json.dumps(summary,ensure_ascii=False,indent=2))
