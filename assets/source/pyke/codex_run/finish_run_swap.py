from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np,json,shutil,zipfile
out=Path('outputs/pyke-run');out.mkdir(parents=True,exist_ok=True)
sheet=Image.open('work/run-candidate-sheet.png').convert('RGBA')
native=sheet.resize((512,192),Image.Resampling.NEAREST)
sheet.save(out/'pyke_run.png');native.save(out/'pyke_run_1x.png')
green=Image.new('RGBA',sheet.size,'#00ff00');green.alpha_composite(sheet);green.convert('RGB').save(out/'pyke_run_green.png')
source=np.array(Image.open('work/pyke_run_swap_pack/2_pyke_design.png').convert('RGBA'))[::8,::8]
palette={tuple(v[:3]) for v in source.reshape(-1,4) if v[3]}
fixed=Image.open('work/run-fixed-upper.png').convert('RGBA');fixed.alpha_composite(Image.open('work/run-fixed-extension.png'))
placement=json.loads(Path('work/run-placement.json').read_text())
frames=[];report=[]
(out/'frames').mkdir(exist_ok=True)
contact=Image.new('RGB',(1024,512),'#303642');draw=ImageDraw.Draw(contact)
for i,p in enumerate(placement):
 fr=native.crop(((i%4)*128,(i//4)*96,(i%4+1)*128,(i//4+1)*96));a=np.array(fr)
 expect=Image.new('RGBA',(128,96));expect.alpha_composite(fixed,(0,-18+p['upper_bob']));e=np.array(expect);mask=e[:,:,3]>0
 assert np.array_equal(a[mask],e[mask]),f'fixed pixels frame {i+1}'
 assert not np.any(a[82:,:,3]),f'floor frame {i+1}'
 assert set(np.unique(a[:,:,3]))<={0,255}
 assert {tuple(v[:3]) for v in a.reshape(-1,4) if v[3]}<=palette
 ys,xs=np.where(a[:,:,3]>0);assert ys.max()==81
 # Remove invariant cloth/hand pixels before measuring the new legs.
 leg=a.copy();leg[mask]=0;leg[:64]=0
 ly,lx=np.where(leg[:,:,3]>0)
 gold=(leg[:,:,3]>0)&(leg[:,:,0]>180)&(leg[:,:,1]>100)&(leg[:,:,1]<200)&(leg[:,:,2]<60)
 gy,gx=np.where(gold & (np.indices(gold.shape)[0]<75))
 sole=(leg[79:82,:,3]>0);sy,sx=np.where(sole)
 report.append({'frame':i+1,'upper_bob':p['upper_bob'],'fixed_pixels_exact':True,'opaque_bbox':list(fr.getbbox()),'bottom_row':int(ys.max()),'leg_x_extent':[int(lx.min()),int(lx.max())],'leg_width':int(lx.max()-lx.min()+1),'gold_knee_mean_x':round(float(gx.mean()),2) if gx.size else None,'bottom_three_rows_x_extent':[int(sx.min()),int(sx.max())] if sx.size else None})
 fr.save(out/'frames'/f'run_{i+1:02d}_1x.png')
 preview=Image.new('RGBA',(128,96),'#303642');preview.alpha_composite(fr)
 zoom=preview.resize((512,384),Image.Resampling.NEAREST).convert('RGB');frames.append(zoom)
 contact.paste(preview.resize((256,192),Image.Resampling.NEAREST).convert('RGB'),((i%4)*256,(i//4)*256+24));draw.text(((i%4)*256+12,(i//4)*256+6),str(i+1),fill='white')
assert len({f.tobytes() for f in frames})==8
assert report[0]['gold_knee_mean_x']<report[4]['gold_knee_mean_x']-10
assert report[2]['leg_width']<report[0]['leg_width']
assert report[6]['leg_width']<report[4]['leg_width']
assert np.array_equal(np.array(sheet),np.repeat(np.repeat(np.array(native),8,0),8,1))
frames[0].save(out/'pyke_run_preview.gif',save_all=True,append_images=frames[1:],duration=[140,130]*4,loop=0,disposal=2)
contact.save(out/'pyke_run_contact.png')
validation={'frame_count':8,'layout':[4,2],'cell_native':[128,96],'scale':8,'pivot_x':64,'floor_row':81,'source_palette_size':len(palette),'hard_alpha':True,'exact_8x_blocks':True,'upper_body_exact':True,'crossing_width_checks':True,'near_leg_alternation_check':True,'duration_ms':135,'gif_duration_ms':[140,130]*4,'in_game_tested':False,'frames':report}
(out/'validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2('work/prepare_run_swap.py',out/'prepare_run_swap.py');shutil.copy2(__file__,out/'finish_run_swap.py')
(out/'references').mkdir(exist_ok=True)
for file in Path('work/pyke_run_swap_pack').glob('*'):
 if file.is_file():shutil.copy2(file,out/'references'/file.name)
shutil.copy2('work/run-swap-prompt.txt',out/'raw/prompt_initial.txt')
print(json.dumps(report,ensure_ascii=False))
