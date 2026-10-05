from pathlib import Path
from PIL import Image
import numpy as np
import json, shutil

ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'work/alistar-run-redraw/alistar_run_pack'
OUT=ROOT/'outputs/alistar-run'
OUT.mkdir(exist_ok=True,parents=True)
(OUT/'raw').mkdir(exist_ok=True)
raw=Path(r'C:\Users\OWNER\.codex\generated_images\01a10a0f-7421-7cb3-8ff4-b585c25c5644\exec-42a00340-638a-4ff6-ba4d-72d3526e2892.png')
shutil.copy2(raw,OUT/'raw/legs_redraw.png')
base=np.array(Image.open(SRC/'alistar_run_base.png').convert('RGBA').resize((512,192),Image.Resampling.NEAREST))
palette=np.unique(base[base[:,:,3]>0],axis=0)
legcols=np.array([(18,3,25,255),(21,11,75,255),(59,24,136,255),(85,38,195,255),(115,61,245,255),(154,99,243,255),(66,23,20,255),(135,62,40,255)])
im=Image.open(raw).convert('RGB')
# Read back the generated legs on their logical grid; remove green, white and pink guides.
def read_cell(i):
    w,h=im.size; x=i%4;y=i//4
    cell=im.crop((round(x*w/4),round(y*h/2),round((x+1)*w/4),round((y+1)*h/2)))
    a=np.array(cell.resize((32,32),Image.Resampling.NEAREST))
    rgb=a.astype(float)
    green=(rgb[:,:,1]>rgb[:,:,0]*1.3+10)&(rgb[:,:,1]>rgb[:,:,2]*1.3+10)
    pale=(rgb.min(axis=2)>175)|((rgb[:,:,0]>210)&(rgb[:,:,1]>110)&(rgb[:,:,2]>110))
    keep=~green&~pale
    dist=((a[:,:,None,:].astype(float)-legcols[None,None,:,:3])**2).sum(axis=3)
    b=legcols[dist.argmin(axis=2)].astype('uint8');b[~keep]=0
    return b

def isolated(i,side):
    a=read_cell(i)
    # Use only the generated leg below the existing apron, excluding arms and guide labels.
    crop=a[11:24,1:14] if side=='left' else a[11:24,17:29]
    ys,xs=np.where(crop[:,:,3]>0)
    crop=crop[ys.min():ys.max()+1,xs.min():xs.max()+1]
    return Image.fromarray(crop)

# The passing poses are assembled from the generated bent/pushing leg drawings.
# Each generated leg is registered separately to the supplied hip and hoof guides.
near_sources=[(0,'right'),(1,'right'),(0,'right'),(3,'left'),(4,'left'),(5,'left'),(4,'left'),(7,'right')]
far_sources=[(0,'left'),(1,'left'),(3,'right'),(3,'right'),(4,'right'),(5,'right'),(7,'right'),(7,'left')]
targets=[(62.5,0,52,1),(60,0,53.5,3),(57.5,0,57,3),(55,0,60,1),(53,1,61.5,0),(54.5,3,59,0),(58,3,56.5,0),(61,1,54,0)]
frames=[]; records=[]
for i,(nx,nlift,fx,flift) in enumerate(targets):
    x=(i%4)*128;y=(i//4)*96
    b=base[y:y+96,x:x+128].copy();layers=[]
    for name,source,hx,tx,lift in [('far',far_sources[i],56,fx,flift),('near',near_sources[i],59,nx,nlift)]:
        foot_y=81-lift;top=68;hh=foot_y-top+1
        leg=np.array(isolated(*source).resize((7,hh),Image.Resampling.NEAREST))
        mask=leg[:,:,3]>0
        # Align the actual hoof centre and thigh centre, retaining the generated silhouette.
        bottom_x=np.where(mask[-1])[0];top_x=np.where(mask[0])[0]
        bottom_center=(bottom_x.min()+bottom_x.max())/2 if len(bottom_x) else 3
        top_center=(top_x.min()+top_x.max())/2 if len(top_x) else 3
        layer=np.zeros_like(b)
        for row in range(hh):
            t=row/max(1,hh-1)
            shift=round((hx-top_center)*(1-t)+(tx-bottom_center)*t)
            for col in np.where(mask[row])[0]:
                xx=shift+col
                if 0<=xx<128:layer[top+row,xx]=leg[row,col]
        # Remove isolated one-pixel residue left by the generated backdrop.
        for yy,xx in zip(*np.where(layer[:,:,3]>0)):
            if np.count_nonzero(layer[max(0,yy-1):yy+2,max(0,xx-1):xx+2,3])==1:
                layer[yy,xx]=0
        layers.append(layer)
    for layer in layers:
        mask=layer[:,:,3]>0;b[mask]=layer[mask]
    fixed=base[y:y+96,x:x+128];mask=fixed[:,:,3]>0;b[mask]=fixed[mask]
    assert np.array_equal(b[mask],fixed[mask])
    assert not b[82:,:,3].any()
    frames.append(Image.fromarray(b))
    far_visible=(layers[0][:,:,3]>0)&(layers[1][:,:,3]==0)&(fixed[:,:,3]==0)
    near_visible=(layers[1][:,:,3]>0)&(fixed[:,:,3]==0)
    assert far_visible.sum()>0 and near_visible.sum()>0
    records.append({'frame':i+1,'guide_near_hoof_x':nx,'near_lift':nlift,'guide_far_hoof_x':fx,'far_lift':flift,'far_visible_pixels':int(far_visible.sum()),'near_visible_pixels':int(near_visible.sum()),'upper_body_exact':True})
sheet=Image.new('RGBA',(512,192))
for i,f in enumerate(frames):sheet.paste(f,((i%4)*128,(i//4)*96))
sheet.save(OUT/'alistar_run_1x.png')
sheet.resize((4096,1536),Image.Resampling.NEAREST).save(OUT/'alistar_run.png')
preview=[]
for f in frames:
    canvas=Image.new('RGB',(128,96),(232,234,240));canvas.paste(f,(0,0),f)
    preview.append(canvas.resize((512,384),Image.Resampling.NEAREST))
preview[0].save(OUT/'preview_run.gif',save_all=True,append_images=preview[1:],duration=[120,130]*4,loop=0,disposal=2)
sheet.resize((2048,768),Image.Resampling.NEAREST).save(OUT/'contact_sheet.png')
shutil.copy2(SRC/'alistar_run_cells.json',OUT/'alistar_run_cells.json')
(OUT/'validation.json').write_text(json.dumps({'size':[4096,1536],'grid':[4,2],'frame_ms':125,'pixel_scale':8,'binary_alpha':True,'original_body_preserved':True,'frames':records},ensure_ascii=False,indent=2),encoding='utf8')
print(OUT)
