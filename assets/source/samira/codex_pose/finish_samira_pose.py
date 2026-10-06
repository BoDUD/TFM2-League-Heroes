from PIL import Image, ImageDraw
import numpy as np, json
from pathlib import Path

out=Path('outputs/samira-pose'); refs=Path('work/samira-pose-pack')
design=np.array(Image.open(refs/'1_design_1x.png').convert('RGBA'))
head=np.array(Image.open(refs/'4_head_1x.png').convert('RGBA'))
palette=np.array(sorted({tuple(map(int,p[:3])) for p in design[design[:,:,3]>0]}),dtype=float)
raw=np.array(Image.open(out/'raw/pose_generated.png').convert('RGBA'))
s=8.44; ox=1.991; oy=2.759
H,W=raw.shape[:2]; grid=np.zeros((int(np.ceil(H/s)),int(np.ceil(W/s)),4),dtype=np.uint8)
for y in range(grid.shape[0]):
 for x in range(grid.shape[1]):
  b=raw[max(0,round(oy+y*s)):min(H,round(oy+(y+1)*s)),max(0,round(ox+x*s)):min(W,round(ox+(x+1)*s))]
  mask=b[:,:,3]>180
  if not mask.size or mask.mean()<.45: continue
  color=np.median(b[:,:,:3][mask],axis=0)
  grid[y,x,:3]=palette[np.argmin(((palette-color)**2).sum(axis=1))]; grid[y,x,3]=255
yy,xx=np.where(grid[:,:,3]>0); bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
actor=grid[bbox[1]:bbox[3],bbox[0]:bbox[2]]
Image.fromarray(actor).resize((actor.shape[1]*8,actor.shape[0]*8),Image.Resampling.NEAREST).save(out/'raw/regridded_preview.png')
print('source bbox',bbox,'actor',actor.shape)
# Top 17 source rows contain the generated head/hilt and are replaced.
# Three redundant rows below the neck are removed without touching the head.
body=actor[17:].copy(); deleted_body_rows=[3,17,22]
body=np.delete(body,deleted_body_rows,axis=0)
if body.shape[0]!=25: raise ValueError(f'Expected 25 body rows, got {body.shape}')
bottom=np.where(body[-1,:,3]>0)[0]; gaps=np.where(np.diff(bottom)>1)[0]
if not len(gaps): raise ValueError('Missing visible foot gap')
center=(bottom[gaps[0]]+bottom[gaps[0]+1]+1)/2
left=round(64-center)
canvas=np.zeros((128,128,4),dtype=np.uint8)
# Approved sword handle/red pommel stays in its original position.
canvas[60:75,52:57]=design[60:75,52:57]
# Reuse a three-row ribbon fragment from the generated hilt, rather than draw it.
canvas[62:65,50:53]=actor[7:10,6:9]
canvas[75:100,left:left+body.shape[1]]=body
# Copy full approved head rectangle, including transparent cells, byte-for-byte.
canvas[60:75,57:77]=head[60:75,57:77]
small=Image.fromarray(canvas); small.save(out/'samira_pose_1x.png')
large=small.resize((1024,1024),Image.Resampling.NEAREST); large.save(out/'samira_pose.png')
used=sorted({'#'+bytes(p[:3]).hex().upper() for p in canvas[canvas[:,:,3]>0]})
qa={'source_grid_bbox':bbox,'source_cell':[s,ox,oy],'source_actor_size':[int(actor.shape[1]),int(actor.shape[0])],'generated_head_rows_replaced':17,'body_rows_deleted':deleted_body_rows,'head_rectangle':[57,60,77,75],'head_entire_rectangle_exact':bool(np.array_equal(canvas[60:75,57:77],head[60:75,57:77])),'hair_top_row':60,'soles_bottom_row':99,'hair_to_soles_rows':40,'width_including_weapons':small.getbbox()[2]-small.getbbox()[0],'body_left':left,'foot_gap_center':float(center+left),'col64_inside_foot_gap':bool(left+bottom[gaps[0]]<64<left+bottom[gaps[0]+1]),'color_count':len(used),'only_approved_palette':all(tuple(map(int,p[:3])) in set(map(tuple,palette.astype(int))) for p in canvas[canvas[:,:,3]>0]),'alpha_values':list(map(int,np.unique(canvas[:,:,3]))),'strict8x8':bool(np.array_equal(np.array(large),np.repeat(np.repeat(canvas,8,axis=0),8,axis=1))),'nothing_below_soles':not bool(canvas[100:,:,3].any()),'palette':used}
(out/'qa.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
(out/'palette.txt').write_text('\n'.join(used)+'\n',encoding='utf-8')
print(json.dumps(qa))
# Small comparative preview with a light background for inspection.
preview=Image.new('RGB',(800,410),'#ddd'); draw=ImageDraw.Draw(preview)
for i,(label,im) in enumerate([('Approved design',Image.fromarray(design)),('New pose',small)]):
 crop=im.crop(im.getbbox()); enlarged=crop.resize((crop.width*8,crop.height*8),Image.Resampling.NEAREST)
 preview.paste(enlarged,(30+i*360,40),enlarged); draw.text((30+i*360,15),label,fill='black')
preview.save(out/'comparison.png')
