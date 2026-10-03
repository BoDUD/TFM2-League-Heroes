from PIL import Image
from pathlib import Path
import numpy as np,json,sys

base=Path(__file__).parent
palette=np.array(json.loads((base/'palette.json').read_text(encoding='utf-8'))['colors'],dtype=float)

def readback(path,block,phase_x,phase_y,dest,eye_rect=None):
 im=Image.open(path).convert('RGBA');a=np.asarray(im);w,h=im.size
 # Each output pixel samples the center of an inferred large square in the source.
 # No body drawing, stretching, interpolation or source silhouette sculpting.
 xs=np.arange(phase_x+block/2,w,block)
 ys=np.arange(phase_y+block/2,h,block)
 sample=a[np.clip(np.rint(ys).astype(int),0,h-1)[:,None],np.clip(np.rint(xs).astype(int),0,w-1)[None,:]].copy()
 opaque=sample[:,:,3]>=128
 rgb=sample[:,:,:3].astype(float)
 dist=((rgb[:,:,None,:]-palette[None,None,:,:])**2).sum(-1)
 if eye_rect is not None:
  # Role-aware palette quantization: the supplied pure-white swatch belongs only to eyes.
  x0,y0,x1,y1=eye_rect
  eye_region=(xs[None,:]>=x0)&(xs[None,:]<x1)&(ys[:,None]>=y0)&(ys[:,None]<y1)
  white=np.flatnonzero((palette.min(axis=1)>245))
  for idx in white:dist[:,:,idx]=np.where(eye_region,dist[:,:,idx],float('inf'))
 colors=palette[dist.argmin(-1)].astype(np.uint8)
 logical=np.zeros_like(sample);logical[:,:,:3]=colors;logical[:,:,3]=np.where(opaque,255,0)
 logical[~opaque]=0
 yy,xx=np.nonzero(opaque)
 crop=logical[yy.min():yy.max()+1,xx.min():xx.max()+1]
 image=Image.fromarray(crop)
 dest.parent.mkdir(parents=True,exist_ok=True);image.save(dest)
 image.resize((image.width*16,image.height*16),Image.Resampling.NEAREST).save(base/(dest.stem+'_inspection.png'))
 info={'source':str(path),'block_px':block,'phase_xy':[phase_x,phase_y],
  'sampled_canvas_size':[len(xs),len(ys)],'logical_size':list(image.size),'solid_pixels':int((crop[:,:,3]>0).sum()),
  'palette_colors':len(np.unique(crop[:,:,:3][crop[:,:,3]>0],axis=0)),
  'method':'center sample per inferred large square, alpha threshold128, nearest supplied30-color palette, transparent margin crop only',
  'row_widths':[int(np.count_nonzero(row[:,3])) for row in crop],
  'row_extents':[[int(np.flatnonzero(row[:,3])[0]),int(np.flatnonzero(row[:,3])[-1])+1] if np.any(row[:,3]) else None for row in crop]}
 if eye_rect is not None:info['white_allowed_source_rect']=eye_rect
 return info

if __name__=='__main__':
 path,block,px,py,dest=sys.argv[1:]
 info=readback(Path(path),float(block),float(px),float(py),Path(dest))
 print(json.dumps(info,ensure_ascii=False))
