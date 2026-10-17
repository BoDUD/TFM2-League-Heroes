from PIL import Image
from pathlib import Path
import numpy as np,json,hashlib
OUT=Path(__file__).resolve().parent.parent
SRC=Path(__file__).resolve().parent/'approved_source'
manifest=json.loads((OUT/'manifest.json').read_text())
head=Image.open(SRC/'design/renekton_head_1x.png').convert('RGBA')
allowed={tuple(bytes.fromhex(h[1:])) for h in manifest['palette']}
def islands(alpha):
 mask=alpha>0;seen=np.zeros(mask.shape,bool);sizes=[]
 for y,x in np.argwhere(mask):
  if seen[y,x]:continue
  todo=[(int(y),int(x))];seen[y,x]=True;n=0
  while todo:
   yy,xx=todo.pop();n+=1
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     yn=yy+dy;xn=xx+dx
     if 0<=yn<mask.shape[0] and 0<=xn<mask.shape[1] and mask[yn,xn] and not seen[yn,xn]:seen[yn,xn]=True;todo.append((yn,xn))
  sizes.append(n)
 return sorted(sizes,reverse=True)
report={}
for tag,spec in manifest['animations'].items():
 big=np.array(Image.open(OUT/f'renekton_{tag}.png').convert('RGBA'))
 if tag=='idle':
  report[tag]={'provided_byte_identical':(SRC/'renekton_idle.png').read_bytes()==(OUT/'renekton_idle.png').read_bytes()}
  continue
 small=np.array(Image.open(OUT/f'renekton_{tag}_1x.png').convert('RGBA'))
 checks={'size_correct':list(big.shape[1::-1])==spec['size_px'],'strict_8px_grid':np.array_equal(big,np.repeat(np.repeat(small,8,0),8,1)),'binary_alpha':set(map(int,np.unique(small[:,:,3])))<={0,255},'approved_palette_only':{tuple(map(int,p)) for p in small[:,:,:3][small[:,:,3]>0]}<=allowed,'empty_unused_cells':True,'frames':[]}
 for fm in spec['frames']:
  x,y,w,h=fm['cell_rect_1x'];frame=small[y:y+h,x:x+w]
  tx,ty=fm['placement_translation_from_design']
  hd=Image.new('RGBA',(128,128));hd.alpha_composite(head,(0,-fm['rig_config']['headup']))
  angle=fm['body_rotation_deg']
  if angle:
   tmp=Image.new('RGBA',(256,256));tmp.alpha_composite(hd,(64,64));tmp=tmp.rotate(angle,Image.Resampling.NEAREST,center=(128,152));hd=tmp.crop((64,64,192,192))
  fitted=Image.new('RGBA',(128,96));fitted.alpha_composite(hd,(tx,ty));expected=np.array(fitted);mask=expected[:,:,3]>0
  checks['frames'].append({'index':fm['index'],'head_pixels_exact':bool(np.array_equal(frame[mask],expected[mask])),'below_feet_empty':bool(not frame[82:,:,3].any()),'connected_component_sizes':islands(frame[:,:,3]),'bbox_area_pixels':int((frame[:,:,3]>0).sum())})
 count=len(spec['frames']);cols,rows=spec['grid']
 for i in range(count,cols*rows):
  cell=small[(i//cols)*96:(i//cols+1)*96,(i%cols)*128:(i%cols+1)*128]
  if cell[:,:,3].any():checks['empty_unused_cells']=False
 if tag=='dead':
  corpse=[]
  for i in range(3,8):
   cell=Image.fromarray(small[(i//cols)*96:(i//cols+1)*96,(i%cols)*128:(i%cols+1)*128]);px,py=spec['frames'][i]['pivot_local_1x']
   normalized=Image.new('RGBA',(128,96));normalized.alpha_composite(cell,(64-px,70-py));corpse.append(np.array(normalized))
  checks['corpse_frames_4_to_8_identical_relative_to_pivot']=all(np.array_equal(corpse[0],a) for a in corpse[1:])
 if tag=='run':
  checks['head_horizontal_offset_to_pivot_fixed']=len({f['head_transform']['translation_from_design'][0]-f['pivot_local_1x'][0] for f in spec['frames']})==1
 report[tag]=checks
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({tag:{k:v for k,v in checks.items() if k!='frames'}|({'head_all':all(f['head_pixels_exact'] for f in checks['frames']),'max_small_islands':max(sum(n<=2 for n in f['connected_component_sizes']) for f in checks['frames'])} if 'frames' in checks else{}) for tag,checks in report.items()},indent=2))


