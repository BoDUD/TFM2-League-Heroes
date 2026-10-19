from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import label
import json
OUT=Path(__file__).resolve().parent
manifest=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
PALETTE=[tuple(c) for c in manifest[0]['palette']]
P=np.array(PALETTE,dtype=float)

def sample(src,phase=(0,0)):
    im=Image.open(src).convert('RGBA')
    a=np.array(im)
    ys,xs=np.where(a[:,:,3]>=128)
    box=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
    x0,y0,x1,y1=box
    # One nearest-neighbor sample per fixed logical cell; no anatomical repaint.
    xx=np.clip((x0+(np.arange(24)+.5+phase[0])*(x1-x0)/24).astype(int),0,im.width-1)
    yy=np.clip((y0+(np.arange(21)+.5+phase[1])*(y1-y0)/21).astype(int),0,im.height-1)
    s=a[yy[:,None],xx[None,:]].copy()
    rgb=s[:,:,:3].astype(float)
    dist=((rgb[:,:,None,:]-P[None,None,:,:])**2*np.array([.25,.50,.25])).sum(axis=-1)
    ix=dist.argmin(axis=-1)
    alpha=np.where(s[:,:,3]>=128,255,0).astype(np.uint8)
    out=np.zeros((21,24,4),dtype=np.uint8)
    out[:,:,:3]=np.array(PALETTE,dtype=np.uint8)[ix]
    out[:,:,3]=alpha
    out[alpha==0]=0
    return Image.fromarray(out),box

def preserve_accents(source,small,box,phase):
    # These colours are selected from existing source clusters in the same grid
    # cell, preserving small highlights/nose that a centre sample can miss.
    a=np.array(Image.open(source).convert('RGBA'))
    rgb=a[:,:,:3].astype(int);valid=a[:,:,3]>=128
    white=valid&(rgb.min(axis=2)>235)
    pink=valid&(rgb[:,:,0]>215)&(rgb[:,:,1]<170)&(rgb[:,:,2]>90)&(rgb[:,:,2]<210)&(rgb[:,:,0]>rgb[:,:,2]+25)
    arr=np.array(small);notes=[]
    x0,y0,x1,y1=box;dx=(x1-x0)/24;dy=(y1-y0)/21
    for kind,mask,color in [('white-highlight',white,PALETTE[3]),('pink-accent',pink,PALETTE[5])]:
        labs,n=label(mask)
        for k in range(1,n+1):
            yy,xx=np.where(labs==k)
            if not (100<=len(xx)<=a.shape[0]*a.shape[1]*.0025):continue
            cx=float(xx.mean());cy=float(yy.mean())
            gx=int(np.floor((cx-x0)/dx-phase[0]));gy=int(np.floor((cy-y0)/dy-phase[1]))
            if not(0<=gx<24 and 0<=gy<21):continue
            # No source-free pixels or geometry are drawn; choose a sampled
            # cluster colour only in its existing destination cell.
            old=arr[gy,gx].tolist()
            arr[gy,gx]=(*color,255)
            notes.append(dict(kind=kind,source_centroid=[cx,cy],cell=[gx,gy],old_rgba=old,new_rgba=list((*color,255))))
    return Image.fromarray(arr),notes

for m in manifest:
    src=OUT/m['raw']
    small,box=sample(src,m['sampling_phase'])
    small,notes=preserve_accents(src,small,box,m['sampling_phase'])
    n=m['draft']
    old=Image.open(OUT/f'yuumi-ride-{n}_1x.png').convert('RGBA')
    assert small.tobytes()==old.tobytes(), 'Regenerated pixels differ'
    small.save(OUT/f'yuumi-ride-{n}_1x.png')
    big=Image.new('RGBA',(1254,1254))
    big.paste(small.resize((1200,1050),Image.Resampling.NEAREST),(50,100))
    big.save(OUT/f'yuumi-ride-{n}.png')
print('Both drafts rebuilt identically from raw.')
