from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import numpy as np,json
ROOT=Path('work/pyke_run_swap_pack');OUT=Path('outputs/pyke-run')
design=np.array(Image.open(ROOT/'2_pyke_design.png').convert('RGBA'))[::8,::8]
upper=np.array(Image.open(ROOT/'4_pyke_upper_body.png').convert('RGBA'))[::8,::8]
colors=sorted({tuple(v[:3]) for v in design.reshape(-1,4) if v[3]})
pal=Image.new('P',(1,1));rgb=colors+[(0,255,0)];flat=sum([list(c) for c in rgb],[]);pal.putpalette(flat+[0]*(768-len(flat)))
raw=Image.open(OUT/'raw/pyke_run_phase_fix_raw.png').convert('RGB')
assert raw.size==(2048,768)
quant=np.array(raw.quantize(palette=pal,dither=Image.Dither.NONE))
native=np.zeros((192,512,4),np.uint8)
for y in range(192):
 for x in range(512):
  block=quant[y*4:y*4+4,x*4:x*4+4].reshape(-1)
  v=int(np.bincount(block,minlength=256).argmax())
  if v<len(colors):native[y,x]=[*colors[v],255]
Image.fromarray(native).resize((4096,1536),Image.Resampling.NEAREST).save('work/run-regrid.png')
sheet=Image.new('RGBA',(512,192));stats=[]
for i in range(8):
 source_i=[0,7,2,3,4,1,6,5][i]
 a=native[(source_i//4)*96:(source_i//4+1)*96,(source_i%4)*128:(source_i%4+1)*128]
 # Take the freshly drawn lower body only; frame-local floor is measured, not trimmed away.
 lower=a.copy();lower[:61]=0;lower[:,84:]=0;lower[:,:28]=0
 ys,xs=np.where(lower[:,:,3]>0);bottom=int(ys.max());dy=81-bottom
 legs=Image.fromarray(lower);fr=Image.new('RGBA',(128,96));fr.alpha_composite(legs,(0,dy))
 fa=np.array(fr);fa[:64]=0;fr=Image.fromarray(fa)
 bob=0 if i in [0,4] else -1 if i in [2,6] else 0
 up=Image.fromarray(upper);fr.alpha_composite(up,(0,-18+bob))
 # The supplied upper cut stops at the belt. Keep the fixed design's exposed forearm/claw too.
 arm=design.copy();yy,xx=np.indices((128,128))
 cloth_colors=[(17,51,65),(28,30,46),(28,76,79),(116,3,22),(161,6,25),(211,9,25)]
 cloth=np.zeros((128,128),bool)
 for c in cloth_colors:cloth|=np.all(design[:,:,:3]==c,axis=2)
 keep=((yy>=83)&cloth)|((yy>=83)&(yy<=95)&(xx>=83)&(xx<=94))
 arm[~keep]=0
 fr.alpha_composite(Image.fromarray(arm),(0,-18+bob))
 fr.save('work/run-candidate-'+str(i+1)+'.png');sheet.alpha_composite(fr,((i%4)*128,(i//4)*96))
 stats.append({'frame':i+1,'raw_source_frame':source_i+1,'raw_bottom':bottom,'leg_shift_y':dy,'upper_bob':bob})
sheet.resize((4096,1536),Image.Resampling.NEAREST).save('work/run-candidate-sheet.png')
contact=Image.new('RGBA',(2048,448),'#dddde0');draw=ImageDraw.Draw(contact)
for i in range(8):
 fr=Image.open('work/run-candidate-'+str(i+1)+'.png');bg=Image.new('RGBA',fr.size,'#dddde0');bg.alpha_composite(fr);contact.alpha_composite(bg.resize((256,192),Image.Resampling.NEAREST),(i*256,32));draw.text((i*256+5,8),str(i+1),fill='black')
contact.convert('RGB').save('work/run-candidate-contact.png');print(json.dumps(stats))
Image.fromarray(arm).save('work/run-fixed-extension.png')
Image.fromarray(upper).save('work/run-fixed-upper.png')
Path('work/run-placement.json').write_text(json.dumps(stats,indent=2))
