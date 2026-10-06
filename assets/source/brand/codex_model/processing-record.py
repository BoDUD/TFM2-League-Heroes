from pathlib import Path
from PIL import Image
import numpy as np
import json, shutil

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs/brand-model'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'raw').mkdir(exist_ok=True)
GEN=Path(r'C:\Users\OWNER\.codex\generated_images\01a1116f-288b-72d2-8cd8-24fce6dfabfd')
FILES={'A':'exec-6c973281-3b58-45b5-94a0-18cb794a4f1d.png','B':'exec-37b95882-da43-4b60-8fc0-a44cfd0b020f.png'}
HEX='0A0608 1E1A26 2E2838 423A50 5C526C A01808 E04010 FF8A1A FFD040 FFF4B0 8A1206 D02A0A FF6A14 FFA428 6A1A20 A0281C 3E3020 6A5434 92784C B89C6C 2A1E16 4A3424 7A4A1A C08030 F0C060 FFFFFF'.split()
PAL=np.array([[int(h[i:i+2],16) for i in (0,2,4)] for h in HEX],dtype=np.int32)

def own_grid(path):
    a=np.array(Image.open(path).convert('RGBA'))
    # Generated coarse drafts use approximately ten screen pixels per native cell.
    # Read a central 4x4 patch per cell; no image resampling or interpolation.
    rows=[]
    for y in range(5,a.shape[0],10):
        row=[]
        for x in range(5,a.shape[1],10):
            patch=a[max(0,y-2):y+2,max(0,x-2):x+2]
            opaque=patch[:,:,3]>=128
            if opaque.sum()<8: row.append([0,0,0,0]); continue
            rgb=np.median(patch[:,:,:3][opaque],axis=0)
            k=np.argmin(((PAL-rgb)**2).sum(axis=1))
            row.append([*PAL[k],255])
        rows.append(row)
    grid=np.array(rows,dtype=np.uint8)
    ys,xs=np.where(grid[:,:,3]>0)
    return grid[ys.min():ys.max()+1,xs.min():xs.max()+1]

for v,f in FILES.items():
    shutil.copy2(GEN/f,OUT/'raw'/f'brand_{v}_raw.png')
    g=own_grid(GEN/f)
    Image.fromarray(g).save(ROOT/f'work/grid_{v}.png')
    Image.fromarray(g).resize((g.shape[1]*8,g.shape[0]*8),Image.Resampling.NEAREST).save(ROOT/f'work/grid_{v}_preview.png')
    print(v,'native grid',g.shape[:2])
shutil.copy2(GEN/'exec-a3de136a-7c72-4b6b-a858-41a6087129f4.png',OUT/'raw'/'brand_A_initial_raw.png')

def pick(start,end,count):
    return np.rint(np.linspace(start,end,count)).astype(int).tolist()

metrics={}
for v in FILES:
    g=np.array(Image.open(ROOT/f'work/grid_{v}.png').convert('RGBA'))
    if v=='A':
        # Keep both original eye rows while deleting redundant crown/chin rows.
        ys=pick(0,9,6)+[10,11,12,14,15,16,18,19,21,22,24,25]+pick(26,72,25)
        xs=pick(0,27,16)+pick(28,41,9)+pick(42,55,9)
    else:
        ys=pick(0,9,6)+[10,11,13,15,17,18,19,20,22,23]+pick(24,65,27)
        xs=pick(0,23,16)+pick(24,37,10)+pick(38,50,8)
        xs[xs.index(21)]=22
    s=g[np.array(ys)[:,None],np.array(xs)[None,:]].copy()
    # Align each foot's bottom by moving the existing lower-leg/foot pixels only.
    for lo,hi in [(0,17),(17,34)]:
        yy,xx=np.where(s[34:,lo:hi,3]>0)
        bottom=34+int(yy.max())
        if bottom<42:
            part=s[34:bottom+1,lo:hi].copy()
            s[34:,lo:hi]=0
            s[34+42-bottom:43,lo:hi]=part
    # Restore two bright eyes from the generated face's original eye rows.
    eye_y=ys.index(18)
    eye_source=[35,40] if v=='A' else [31,35]
    for x in eye_source:
        eye_x=int(np.argmin(abs(np.array(xs)-x)))
        s[eye_y,eye_x]=[*PAL[8],255]
        if eye_y>0:s[eye_y-1,eye_x]=[*PAL[0],255]
    # Unify existing silhouette boundary pixels to one near-black; no expansion.
    mask=s[:,:,3]>0
    padded=np.pad(mask,1)
    inside=padded[1:-1,:-2]&padded[1:-1,2:]&padded[:-2,1:-1]&padded[2:,1:-1]
    boundary=mask&~inside
    warm=(s[:,:,0]>110)&(s[:,:,0]>s[:,:,2]*1.5)
    s[boundary&~warm]=[*PAL[0],255]
    s[boundary&warm]=[*PAL[10],255]
    # Eyes are interior highlights and must stay readable.
    for x in eye_source:
        eye_x=int(np.argmin(abs(np.array(xs)-x)))
        if mask[eye_y,eye_x]:s[eye_y,eye_x]=[*PAL[8],255]
    canvas=np.zeros((128,128,4),dtype=np.uint8)
    canvas[57:100,47:81]=s
    im=Image.fromarray(canvas)
    im.save(OUT/f'brand_design_{v}_1x.png')
    big=im.resize((1024,1024),Image.Resampling.NEAREST)
    big.save(OUT/f'brand_design_{v}.png')
    colors=sorted(set(tuple(p[:3]) for p in s.reshape(-1,4) if p[3]))
    yy,xx=np.where(s[:,:,3]>0)
    metrics[v]={'crown_to_soles':37,'head':12 if v=='A' else 10,'flames':6,'width':int(xx.max()-xx.min()+1),'total_height':int(yy.max()-yy.min()+1),'colors':len(colors),'sole_row':99,'alpha':[0,255],'native_raw_grid':list(g.shape[:2]),'kept_rows':ys,'kept_columns':xs}
    (OUT/f'palette_{v}.txt').write_text('\n'.join('#%02X%02X%02X'%c for c in colors)+'\n',encoding='utf-8')
    read=np.array(Image.open(OUT/f'brand_design_{v}.png'))
    assert np.array_equal(read,np.repeat(np.repeat(canvas,8,0),8,1))
    assert len(colors)<=28 and set(np.unique(read[:,:,3]))=={0,255}
    assert not read[800:,:,3].any()
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,ensure_ascii=False))

# A neutral-background comparison is a preview only; both delivered assets retain alpha.
preview=Image.new('RGB',(768,440),'#E4E4E4')
from PIL import ImageDraw
draw=ImageDraw.Draw(preview)
for v,x in [('A',32),('B',416)]:
    a=Image.open(OUT/f'brand_design_{v}.png').crop((360,448,664,816))
    preview.paste(a,(x,48),a)
    draw.text((x,20),f'{v} - head {metrics[v]["head"]}px',fill='#222222')
preview.save(OUT/'brand_comparison.png')
