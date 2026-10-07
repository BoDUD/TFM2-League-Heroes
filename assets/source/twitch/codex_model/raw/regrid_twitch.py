from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
import json

ROOT=Path(__file__).resolve().parents[1]/'outputs/twitch-model'
HEX=['0A0806','3A4440','6A746A','9AA394','B85A5A','F09A92','8A1418','E02A3A','C8B48C','F6EAC8','7A4A10','C88A1C','FCC23A','FFE68A','FFFFFF','8A2A0C','D24A1A','F28030','0A3A5A','10689A','3296C8','D8AE68','163A32','2C6252','4A9070','7A3C24','3A2838','6A4A60','C8B0B8','9ACDEB','2EC882','B4FAD4']
PAL=np.array([tuple(bytes.fromhex(h)) for h in HEX],dtype=int)
def detect(hist):
    top=np.argsort(hist)[-80:]; weights=hist[top]
    ps=np.arange(9.,21.,.005)
    vals=np.exp(2j*np.pi*top[None,:]/ps[:,None])@weights
    ix=np.argmax(abs(vals)); period=float(ps[ix])
    phase=float(np.angle(vals[ix])*period/(2*np.pi))%period
    return period,phase

reports=[]; sprites=[]
for name,target,maxwidth in [('A',36,44),('B',38,45)]:
    im=Image.open(ROOT/'raw'/f'{name}-generated.png').convert('RGBA')
    a=np.array(im); rgb=a[:,:,:3].astype(float); m=a[:,:,3]>=128
    hx=(abs(rgb[:,1:]-rgb[:,:-1]).sum(2)*(m[:,1:]&m[:,:-1])).sum(0)
    hy=(abs(rgb[1:]-rgb[:-1]).sum(2)*(m[1:]&m[:-1])).sum(1)
    px,ox=detect(hx); py,oy=detect(hy)
    xs=np.arange(ox+.5*px,im.width,px).astype(int)
    ys=np.arange(oy+.5*py,im.height,py).astype(int)
    c=a[ys[:,None],xs[None,:]].copy(); visible=c[:,:,3]>=128
    yy,xx=np.nonzero(visible); c=c[yy.min():yy.max()+1,xx.min():xx.max()+1]
    v=c[:,:,3]>=128; out=np.zeros_like(c)
    p=c[v,:3].astype(int); ds=((p[:,None,:]-PAL[None,:,:])**2).sum(2)
    inds=np.argmin(ds,axis=1); inds[(p.max(1)<55)]=0
    out[v,:3]=PAL[inds]; out[v,3]=255
    Image.fromarray(out).save(ROOT/'raw'/f'{name}-regridded-untrimmed.png')
    original=list(out.shape[:2]); deleted_rows=[]; deleted_cols=[]
    # Whole rows/columns only. Protect the upper face and all facial columns.
    protected_top=int(original[0]*.56)
    while out.shape[0]>target:
        h,w=out.shape[:2]; options=range(protected_top,h-3)
        scores=[]
        for y in options:
            scores.append((np.count_nonzero(np.any(out[y]!=out[y-1],axis=1))+np.count_nonzero(np.any(out[y]!=out[y+1],axis=1)),y))
        _,y=min(scores); deleted_rows.append(y); out=np.delete(out,y,axis=0)
    while out.shape[1]>maxwidth:
        h,w=out.shape[:2]; options=list(range(2,max(3,int(w*.3))))+list(range(int(w*.76),w-2))
        scores=[]
        for x in options:
            scores.append((np.count_nonzero(np.any(out[:,x]!=out[:,x-1],axis=1))+np.count_nonzero(np.any(out[:,x]!=out[:,x+1],axis=1)),x))
        _,x=min(scores); deleted_cols.append(x); out=np.delete(out,x,axis=1)
    for _ in range(8):
        h,w=out.shape[:2]; footxs=np.nonzero(out[-3:,:,3])[1]
        anchor=int(round((footxs.min()+footxs.max())/2)); start=64-anchor
        low,high=(42,86) if name=='A' else (41,87)
        if start>=low and start+w<=high:break
        candidates=range(2,max(3,int(w*.25))) if start<low else range(int(w*.8),w-2)
        x=min(candidates,key=lambda col:np.count_nonzero(np.any(out[:,col]!=out[:,col-1],axis=1)))
        deleted_cols.append(x);out=np.delete(out,x,axis=1)
    h,w=out.shape[:2]
    assert h==target and w<=maxwidth,(name,original,(h,w))
    # Foot center anchor: midpoint of the occupied columns in the final 3 rows.
    footxs=np.nonzero(out[-3:,:,3])[1]; anchor=int(round((footxs.min()+footxs.max())/2))
    canvas=np.zeros((128,128,4),dtype=np.uint8); x0=64-anchor; y0=100-h
    assert x0>=42-(name=='B') and x0+w<=86+(name=='B'),(x0,w)
    canvas[y0:y0+h,x0:x0+w]=out
    Image.fromarray(canvas).save(ROOT/f'twitch_design_{name}_1x.png')
    Image.fromarray(canvas).resize((1024,1024),Image.Resampling.NEAREST).save(ROOT/f'twitch_design_{name}.png')
    Image.fromarray(out).save(ROOT/f'twitch_design_{name}_sprite_1x.png')
    colors=np.unique(out[out[:,:,3]>0,:3],axis=0)
    assert len(colors)<=32 and not canvas[100:,:,3].any()
    enlarged=np.array(Image.open(ROOT/f'twitch_design_{name}.png'))
    assert np.array_equal(enlarged,np.repeat(np.repeat(canvas,8,axis=0),8,axis=1))
    reports.append(dict(version=name,source_size=list(im.size),source_grid=dict(x=px,y=py,phase_x=ox,phase_y=oy),source_cells=original,height=h,width=w,colors=len(colors),alpha=[0,255],canvas_bbox=[x0,y0,x0+w,100],feet_center=64,deleted_row_indices=deleted_rows,deleted_column_indices=deleted_cols))
    sprites.append(out)
palette=Image.new('RGB',(512,64),'white'); d=ImageDraw.Draw(palette)
for i,color in enumerate(PAL):d.rectangle((i%16*32,i//16*32,i%16*32+31,i//16*32+31),fill=tuple(color))
palette.save(ROOT/'palette.png'); (ROOT/'palette.txt').write_text('\n'.join('#'+h for h in HEX))
(ROOT/'validation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
preview=Image.new('RGBA',(900,420),'white'); d=ImageDraw.Draw(preview)
for i,s in enumerate(sprites):
    stamp=Image.fromarray(s).resize((s.shape[1]*8,s.shape[0]*8),Image.Resampling.NEAREST)
    preview.alpha_composite(stamp,(40+i*440,360-stamp.height));d.text((40+i*440,380),f'{reports[i]["version"]}: {s.shape[1]} x {s.shape[0]} px',fill='black')
preview.convert('RGB').save(ROOT/'twitch_design_comparison.png')
print(json.dumps(reports,indent=2))
