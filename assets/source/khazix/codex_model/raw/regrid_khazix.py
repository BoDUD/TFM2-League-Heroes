from PIL import Image
from pathlib import Path
import numpy as np, json

ROOT=Path('outputs/khazix-model')
HEX=['0B0814','2A1A5C','46309A','6A4ED0','9478F0','1A3E8A','2A78D0','4EB8F0','A0EAFF','5A2410','9A4A1E','CC7632','C8A8A8','F2DCD4','FFF6F0','6A0A14','C41E22','F2503C','E6EE5A','FFFFC0','5E6E1C','9CB83A','D2E47A','F2FAC0','6A3010','B4662A','E89A50']
PAL=np.array([tuple(bytes.fromhex(h)) for h in HEX],dtype=int)

def detect_axis(hist):
    coords=np.arange(len(hist))
    # Fit the repeated source-cell boundaries; no filtered resize of artwork.
    top=np.argsort(hist)[-60:]
    weights=hist[top]
    ps=np.arange(8.,16.,.002)
    vals=np.exp(2j*np.pi*top[None,:]/ps[:,None])@weights
    ix=np.argmax(np.abs(vals))
    period=float(ps[ix]); phase=float(np.angle(vals[ix])*period/(2*np.pi))%period
    return period,phase

def regrid(label):
    im=Image.open(ROOT/'raw'/f'{label}_pixel_generated.png').convert('RGBA')
    a=np.asarray(im); rgb=a[:,:,:3].astype(float); mask=a[:,:,3]>=128
    hx=(np.abs(rgb[:,1:]-rgb[:,:-1]).sum(2)*(mask[:,1:]&mask[:,:-1])).sum(0)
    hy=(np.abs(rgb[1:]-rgb[:-1]).sum(2)*(mask[1:]&mask[:-1])).sum(1)
    px,ox=detect_axis(hx); py,oy=detect_axis(hy)
    xs=np.arange(ox+.5*px,im.width,px).astype(int)
    ys=np.arange(oy+.5*py,im.height,py).astype(int)
    cells=a[ys[:,None],xs[None,:]].copy()
    visible=cells[:,:,3]>=128
    yy,xx=np.nonzero(visible)
    cells=cells[yy.min():yy.max()+1,xx.min():xx.max()+1]
    visible=cells[:,:,3]>=128
    out=np.zeros_like(cells)
    # Yellow-white is reserved for the one face eye, not wings or blade whites.
    for y,x in zip(*np.nonzero(visible)):
        p=cells[y,x,:3].astype(int)
        candidates=list(range(len(PAL)))
        # Green hues exist only in wings; yellow-white exists only at the eye.
        if not (x < 25 and y < 17):
            candidates=[i for i in candidates if i not in (20,21,22,23)]
        if not (39 <= x <= 44 and 22 <= y <= 26):
            candidates=[i for i in candidates if i not in (18,19)]
        ds=((PAL[candidates]-p)**2).sum(1)
        idx=candidates[int(np.argmin(ds))]
        # Neutral dark fragments become the only outline; saturated dark chitin stays violet.
        if max(p)<48 or (max(p)-min(p)<22 and max(p)<75):idx=0
        out[y,x]=[*PAL[idx],255]
    Image.fromarray(out).save(Path('work')/f'{label}_regridded_1x.png')
    Image.fromarray(out).resize((out.shape[1]*8,out.shape[0]*8),Image.Resampling.NEAREST).save(Path('work')/f'{label}_regridded_8x.png')
    info={'period_x':px,'period_y':py,'phase_x':ox,'phase_y':oy,'crop_cell_x':int(xx.min()),'crop_cell_y':int(yy.min()),'width':out.shape[1],'height':out.shape[0]}
    Path('work',f'{label}_grid.json').write_text(json.dumps(info,indent=2))
    print(label,info)
    return out

if __name__=='__main__':
    regrid('A'); regrid('B')
