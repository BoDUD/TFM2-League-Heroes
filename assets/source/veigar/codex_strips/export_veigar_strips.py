from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
import numpy as np
import build_veigar_strips as build

ROOT=build.ROOT; OUT=build.OUT; REF=build.REF; WORK=build.WORK
(OUT/'1x').mkdir(exist_ok=True); (OUT/'previews').mkdir(exist_ok=True)
cells=build.CELLS
manifest={'version':1,'character':'Veigar','approved_model':'Provided B design, 40px tall',
 'scale':8,'native_cell_size':[96,96],'cell_size_px':[768,768],
 'coordinates':'Rectangles are [x,y,width,height]; bbox also provides exclusive max coordinates. Native coordinates are before the 8x display enlargement.',
 'skill2_layout_resolution':'User approved 7 frames in 3x3; slots 8 and 9 empty; frame7 returns to idle.',
 'generation_method':'Built-in image_gen generated one motion study per action. Final frames were repaired by reposing original approved raster parts, with exact original head and original palette. Draft bodies are not treated as approved replacements.',
 'animations':{}}
checks={}; failures=[]
sourcehash=hashlib.sha256((REF/'design/veigar_design_1x.png').read_bytes()).hexdigest()
manifest['approved_source_sha256']=sourcehash
manifest['palette']=['#'+bytes(c).hex().upper() for c in sorted(build.PALETTE)]

def bbox(a):
 y,x=np.where(a[:,:,3]>0)
 return [int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)]

def exact_head(frame,hm):
 m=hm[:,:,3]>0
 return np.array_equal(frame[m],hm[m])

for tag in ['idle','run','attack','skill','skill2','ult','hit','dead']:
 frames=build.ALL[tag]; cols,rows=build.GRIDS[tag]
 atlas=np.zeros((rows*96,cols*96,4),dtype=np.uint8)
 records=[];results=[]
 for i,fr in enumerate(frames):
  x=i%cols*96; y=i//cols*96
  atlas[y:y+96,x:x+96]=fr
  box=bbox(fr); pv=cells['tags'][tag][i]['pivot']; ms=cells['tags'][tag][i]['ms']
  rgb=set(map(tuple,fr[fr[:,:,3]>0,:3]))
  colors_ok=rgb<=build.PALETTE
  alpha_ok=set(np.unique(fr[:,:,3]))<={0,255}
  ground=83 if tag=='dead' and i>=5 else 81
  below=int(np.count_nonzero(fr[ground+1:,:,3]))
  groups=build.components(fr[:,:,3]>0)
  eye=np.zeros(fr.shape[:2],bool)
  for e in build.EYES: eye|=(np.all(fr[:,:,:3]==e,axis=2)&(fr[:,:,3]>0))
  hm=build.HEADS[tag][i] if tag!='idle' else None
  if hm is not None:
   outside=int(np.count_nonzero(eye&(hm[:,:,3]==0)))
   head_ok=exact_head(fr,hm)
   hb=bbox(hm)
  else:
   outside=0;head_ok=True;hb=[24,42,48,60]
  result={'frame':i+1,'palette_ok':colors_ok,'binary_alpha':alpha_ok,
          'pixels_below_allowed_line':below,'component_count':len(groups),
          'eye_pixels_outside_head':outside,'head_source_pixels_preserved':head_ok,
          'opaque_area':int(np.count_nonzero(fr[:,:,3])),
          'area_ratio_to_idle':round(np.count_nonzero(fr[:,:,3])/786,4),
          'head_bbox_native':hb}
  passed=colors_ok and alpha_ok and below==0 and len(groups)==1 and outside==0 and head_ok
  result['passed']=passed
  if not passed:failures.append([tag,i+1,result])
  results.append(result)
  rec={'index':i,'frame_number':i+1,'duration_ms':ms,
       'cell_rect_px':[x*8,y*8,768,768],
       'cell_rect_native':[x,y,96,96],
       'pivot_cell_native':pv,'pivot_cell_px':[pv[0]*8,pv[1]*8],
       'pivot_sheet_px':[(x+pv[0])*8,(y+pv[1])*8],
       'bbox_cell_native_xyxy':box,
       'bbox_cell_px':[box[0]*8,box[1]*8,(box[2]-box[0])*8,(box[3]-box[1])*8],
       'bbox_sheet_px':[(x+box[0])*8,(y+box[1])*8,(box[2]-box[0])*8,(box[3]-box[1])*8],
       'floor_row_native':81,'allowed_bottom_row_native':ground,
       'head_bbox_cell_native_xyxy':hb}
  records.append(rec)
 small=Image.fromarray(atlas)
 small.save(OUT/'1x'/f'veigar_{tag}_1x.png')
 if tag=='idle':shutil.copy2(REF/'veigar_idle.png',OUT/'veigar_idle.png')
 else:small.resize((cols*768,rows*768),Image.Resampling.NEAREST).save(OUT/f'veigar_{tag}.png')
 large=np.array(Image.open(OUT/f'veigar_{tag}.png').convert('RGBA'))
 grid_ok=np.array_equal(large,np.repeat(np.repeat(atlas,8,axis=0),8,axis=1))
 assert grid_ok
 unused=list(range(len(frames),cols*rows))
 for i in unused:assert not np.any(atlas[i//cols*96:(i//cols+1)*96,i%cols*96:(i%cols+1)*96,3])
 durations=[f['ms'] for f in cells['tags'][tag]]
 anim={'file':f'veigar_{tag}.png','native_file':f'1x/veigar_{tag}_1x.png',
       'canvas_px':[cols*768,rows*768],'grid':[cols,rows],
       'frame_count':len(frames),'durations_ms':durations,'total_duration_ms':sum(durations),
       'unused_slots_1based':[i+1 for i in unused],'frames':records}
 if tag in ('attack','skill','skill2','ult'):
  anim.update(release_frame_1based=4,release_elapsed_ms=sum(durations[:3]),reference_tick_hint=12)
 manifest['animations'][tag]=anim
 checks[tag]={'strict_8x8_grid':grid_ok,'empty_unused_slots':True,'frames':results}
 # Palette-only GIF preview: frame durations are rounded by GIF's 10ms clock.
 gifframes=[]
 for i,fr in enumerate(frames):
  pv=cells['tags'][tag][i]['pivot']
  f=Image.fromarray(fr)
  stable=Image.new('RGBA',(112,96))
  stable.paste(f,(56-pv[0],0))
  bg=Image.new('RGB',(448,384),'#242936')
  z=stable.resize((448,384),Image.Resampling.NEAREST)
  bg.paste(z,(0,0),z)
  d=ImageDraw.Draw(bg)
  d.text((16,14),f'{tag}  {i+1}/{len(frames)}  {durations[i]} ms',fill='#E8EBF2',font_size=19)
  gifframes.append(bg)
 gifframes[0].save(OUT/'previews'/f'veigar_{tag}.gif',save_all=True,append_images=gifframes[1:],duration=durations,loop=0,disposal=2,optimize=False)

# Strong run-specific checks: fixed head X relative to supplied pivot, bob <=2.
runheads=[]
for i,hm in enumerate(build.HEADS['run']):
 b=bbox(hm);pv=cells['tags']['run'][i]['pivot']
 runheads.append([b[0]-pv[0],b[1]-pv[1]])
checks['run']['head_offsets_relative_to_pivot']=runheads
checks['run']['constant_head_x']=len(set(v[0] for v in runheads))==1
checks['run']['bob_range_pixels']=max(v[1] for v in runheads)-min(v[1] for v in runheads)
checks['run']['unique_frames']=len(set(hashlib.sha256(f.tobytes()).hexdigest() for f in build.ALL['run']))
checks['run']['leg_alternation']='Original near/far boot pixels exchange forward/back offsets between frames1 and5; crossing poses at frames3 and7.'
assert checks['run']['constant_head_x'] and checks['run']['bob_range_pixels']<=2
checks['idle']['byte_identical_to_supplied']=hashlib.sha256((OUT/'veigar_idle.png').read_bytes()).hexdigest()==hashlib.sha256((REF/'veigar_idle.png').read_bytes()).hexdigest()
assert checks['idle']['byte_identical_to_supplied']

(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps({'passed':not failures,'failures':failures,'animations':checks},ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(REF/'veigar_cells.json',OUT/'veigar_cells.json')
shutil.copy2(REF/'design/veigar_design_1x.png',OUT/'approved_design_1x.png')
shutil.copy2(REF/'design/veigar_head_1x.png',OUT/'approved_head_1x.png')

# Static key-pose preview, 4x, plus a full labeled contact sheet.
selected=[('run',0),('run',4),('attack',3),('skill',3),('skill2',3),('ult',3),('hit',0),('dead',7)]
preview=Image.new('RGB',(1280,640),'#141820');d=ImageDraw.Draw(preview)
for j,(tag,i) in enumerate(selected):
 x=j%4*320;y=j//4*320
 d.rounded_rectangle((x+8,y+8,x+312,y+312),radius=12,fill='#252B38')
 d.text((x+24,y+22),f'{tag} / frame {i+1}',fill='#EAEFF6',font_size=19)
 fr=Image.fromarray(build.ALL[tag][i]);pv=cells['tags'][tag][i]['pivot']
 crop=fr.crop((pv[0]-40,26,pv[0]+32,86)).resize((288,240),Image.Resampling.NEAREST)
 preview.paste(crop,(x+16,y+60),crop)
preview.save(OUT/'veigar_actions_preview.png')
shutil.copy2(WORK/'contact.png',OUT/'previews/veigar_all_frames.png')
print(json.dumps({'passed':not failures,'frames':sum(len(v) for v in build.ALL.values()),'failures':failures,'run_checks':{k:v for k,v in checks['run'].items() if k!='frames'}},ensure_ascii=False))
