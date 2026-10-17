from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np, json, shutil, zipfile

root=Path('outputs/tryndamere-model'); root.mkdir(parents=True,exist_ok=True)
raw=Path(r'C:/Users/OWNER/.codex/generated_images/01a10b97-ec8f-7451-ad15-366dd6554e45')
sources={'A_initial':'exec-1cf889a0-3793-4336-8034-7747a9f0093d.png','A_retry':'exec-644b7b86-2de8-40e7-bee8-6d8bdd25f0db.png','A_selected':'exec-836788f5-0297-461b-abb2-18e20c5f6a23.png','B_generated':'exec-277b1aff-ced9-46b9-bc15-2ffb1db4bc21.png'}
for label,name in sources.items(): shutil.copy2(raw/name,root/'raw'/f'{label}.png')
hexes=['0E0E16','8C4A2C','C8784A','E8955C','FFB97A','2A3044','44506A','303A52','4C5C78','7A8AA6','C8D2E4','6E6E7C','B0AEBC','E2DEE8','3A2418','6A4630','0C2A36','145060','2A7A86','00A89C','3CF0DC','C8FFF8','A0302C','E8F4FF']
palette=np.array([tuple(bytes.fromhex(h)) for h in hexes],dtype=int)
im=Image.open(raw/sources['A_selected']).convert('RGBA')
grid=np.zeros((39,57,4),dtype=np.uint8)
for y in range(39):
 for x in range(57):
  p=im.getpixel((round(59+(x+.5)*20.6),round(415+(y+.5)*20.6)))
  if p[3]>=128:
   # Eye white is reserved for deliberate face pixels below.
   idx=np.argmin(((palette[:-1]-np.array(p[:3]))**2).sum(axis=1))
   grid[y,x]=[*palette[idx],255]
# Explicit face repair on source grid, preserves two level eyes and beard.
def put(x,y,c): grid[y,x]=[*palette[c],255]
for x in range(37,41): put(x,9,0); put(x,10,3); put(x,11,3); put(x,12,0); put(x,13,0)
for x in [37,38,40]: put(x,10,23)
put(39,11,4); put(39,12,22)
# Remove entire columns outside the protected face columns 30..41.
deleted=[3,6,9,12,15,18,21,23,25,27,43,45,47,49,51,53,55]
grid=np.delete(grid,deleted,axis=1)
# A: head14 plus body28, extend only existing torso rows without filtering.
a=np.concatenate([grid[:14],grid[14:18],grid[17:18],grid[18:20],grid[19:20],grid[20:22],grid[21:22],grid[22:]],axis=0)
assert a.shape==(42,40,4)
# B differs only in proportion: omit two helmet rows, extend two torso rows.
b=np.concatenate([np.delete(a[:14],[4,6],axis=0),a[14:18],a[17:18],a[18:20],a[19:20],a[20:]],axis=0)
assert b.shape==(42,40,4)
# Ensure a one-colour near-black floor edge and a common baseline for boots.
for arr in [a,b]:
 for x0,x1 in [(13,19),(30,37)]:
  arr[41,x0:x1]=[*palette[0],255]
metrics={}
for label,arr,head in [('A',a,14),('B',b,12)]:
 canvas=Image.new('RGBA',(128,128)); canvas.paste(Image.fromarray(arr),(40,58))
 canvas.save(root/f'tryndamere_design_{label}_1x.png')
 full=canvas.resize((1024,1024),Image.Resampling.NEAREST); full.save(root/f'tryndamere_design_{label}.png')
 colors=sorted(set(tuple(p) for p in np.asarray(canvas).reshape(-1,4) if p[3]))
 bbox=canvas.getbbox(); metrics[label]={'width':bbox[2]-bbox[0],'height':bbox[3]-bbox[1],'head_rows':head,'bbox_1x':bbox,'sole_row':99,'opaque_colors':len(colors),'alpha_values':[0,255],'face_eye_row':68 if label=='A' else 66}
 assert len(colors)<=26 and bbox[3]==100 and bbox[3]-bbox[1]==42
 assert np.array_equal(np.asarray(full),np.repeat(np.repeat(np.asarray(canvas),8,axis=0),8,axis=1))
 assert np.count_nonzero(np.asarray(canvas)[100:,:,3])==0
(root/'validation.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
(root/'palette.txt').write_text('\n'.join('#'+h for h in hexes)+'\n',encoding='utf-8')
swatch=Image.new('RGB',(480,120),'white'); d=ImageDraw.Draw(swatch)
for i,h in enumerate(hexes):
 x=(i%12)*40; y=(i//12)*60; d.rectangle((x,y,x+39,y+39),fill='#'+h); d.text((x+2,y+42),str(i),fill='black')
swatch.save(root/'palette.png')
comparison=Image.new('RGBA',(720,440),(245,245,245,255)); d=ImageDraw.Draw(comparison)
for i,(label,arr) in enumerate([('A',a),('B',b)]):
 sprite=Image.fromarray(arr).resize((320,336),Image.Resampling.NEAREST); comparison.alpha_composite(sprite,(20+i*360,60)); d.text((20+i*360,20),label+'  head '+str(14 if label=='A' else 12)+' / height 42',fill='black')
comparison.save(root/'comparison.png')
print(json.dumps(metrics,indent=2))

