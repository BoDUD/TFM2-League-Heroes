from PIL import Image,ImageDraw
import numpy as np,json,hashlib,math
from pathlib import Path
SRC=Path(__file__).resolve().parent/'approved_source'
OUT=Path(__file__).resolve().parent.parent;WORK=Path(__file__).resolve().parent/'source_parts';WORK.mkdir(parents=True,exist_ok=True)
design=Image.open(SRC/'design/renekton_design_1x.png').convert('RGBA')
head=Image.open(SRC/'design/renekton_head_1x.png').convert('RGBA')
arr=np.array(design); used=np.zeros((128,128),bool); layers={}
# Shape masks extract existing approved pixels; no replacement character drawn.
def extract(name,poly=None,mask=None):
 global used
 if mask is None:
  m=Image.new('1',(128,128));ImageDraw.Draw(m).polygon(poly,fill=1);mask=np.array(m,bool)
 mask=mask & (arr[:,:,3]>0) & ~used
 if name=='near':
  yy,xx=np.indices(mask.shape)
  # Keep the forearm/blade, return covered thigh/tail/chest pixels to body layers.
  grey=np.isin(arr[:,:,0],[75,147,194]) & np.isin(arr[:,:,1],[72,145,192])
  teal=(arr[:,:,0]<10)&(arr[:,:,1]>60)&(arr[:,:,2]>60)
  mask &= ~((yy>=79)&grey)
  mask &= ~((yy>=83)&(xx>=40)&teal)
  mask &= ~((xx>=55)&(yy>=71)&(yy<79))
  # Tiny disconnected shoulder-border fragments stay on the fixed pauldron.
  visited=np.zeros_like(mask)
  for y,x in np.argwhere(mask):
   if visited[y,x]:continue
   todo=[(int(y),int(x))];visited[y,x]=1;component=[]
   while todo:
    yy,xx=todo.pop();component.append((yy,xx))
    for dy in [-1,0,1]:
     for dx in [-1,0,1]:
      yn,xn=yy+dy,xx+dx
      if 0<=yn<128 and 0<=xn<128 and mask[yn,xn] and not visited[yn,xn]:visited[yn,xn]=1;todo.append((yn,xn))
   if len(component)<=10:
    for yy,xx in component:mask[yy,xx]=0
 if name in ['rearleg','frontleg']:
  yy,xx=np.indices(mask.shape)
  # Claude, 2026-10-08: the rear foot drawn as the front one reaches column 62 (tools/art/fix_renekton_foot.py)
  foot=(((yy>=94)&(xx>=43)&(xx<=60))|((yy>=96)&(xx>=61)&(xx<=62))) if name=='rearleg' else ((yy>=93)&(xx>=71)&(xx<=88))
  mask |= foot & (arr[:,:,3]>0) & ~used
 used|=mask
 data=np.zeros_like(arr);data[mask]=arr[mask];layers[name]=Image.fromarray(data)
extract('head',mask=np.array(head)[:,:,3]>0)
extract('near',[(55,70),(58,73),(51,78),(48,80),(58,80),(59,85),(49,91),(40,92),(33,88),(28,78),(27,68),(33,72),(42,76),(48,72)])
extract('far',[(80,79),(87,81),(88,84),(93,86),(94,93),(90,94),(86,91),(82,88),(80,86)])
extract('rearleg',[(49,85),(55,85),(56,89),(60,92),(57,94),(57,96),(60,100),(47,100),(43,97),(44,94),(47,92),(46,90)])
extract('frontleg',[(73,83),(80,86),(81,89),(85,91),(83,94),(82,96),(88,100),(74,100),(71,97),(73,94),(71,91)])
extract('tail',[(36,90),(42,91),(46,88),(49,88),(50,90),(47,94),(44,97),(41,98),(38,96)])
# Claude, the narrowed design (blade and tail columns cut, 2026-10-07): everything left of the body (column 45) left
# over goes with the blade arm above row 90 and with the tail from row 90 down, so no ghost of the blade stays behind
yy_,xx_=np.indices((128,128)); rest=(arr[:,:,3]>0)&~used&(xx_<45)
for nm,m in (('near',rest&(yy_<90)),('tail',rest&(yy_>=90))):
 la=np.array(layers[nm]);la[m]=arr[m];layers[nm]=Image.fromarray(la);used|=m
core=np.zeros_like(arr);core[(arr[:,:,3]>0)&~used]=arr[(arr[:,:,3]>0)&~used];layers['core']=Image.fromarray(core)
for n,im in layers.items(): im.save(WORK/(n+'.png'))
edge_arr=np.array(layers['near']);edge_rgb=edge_arr[:,:,:3]
eyy,exx=np.indices((128,128))
ivory=((edge_rgb==[249,238,219]).all(2)|(edge_rgb==[238,207,161]).all(2)|(edge_rgb==[203,163,116]).all(2))&(edge_arr[:,:,3]>0)&(eyy>=77)
edge_arr[~ivory]=0;blade_edge=Image.fromarray(edge_arr)
# Exact palette from approved model.
palette=sorted({tuple(map(int,p[:3])) for p in arr.reshape(-1,4) if p[3]})
cells=json.loads((SRC/'renekton_cells.json').read_text())
specs={"run":{"cols":4,"rows":2,"ms":[96,96,96,96,96,96,96,96],"hit":None,"anim":"RUN 8-frame seamless heavy charge. Near leg leads in frame1, far leg leads in frame5. Frames3 and7 lifted foot passes BESIDE the other foot 2-3 pixels higher; the legs genuinely CROSS and swap front/back every half cycle. Body bobs1 pixel, tail swings slightly, blade low trailing. Head x offset to pivot stays fixed. Far leg darker."},"attack":{"cols":3,"rows":2,"ms":[60,60,80,80,100],"hit":3,"anim":"BASIC ATTACK5 frames:1 idle;2 windup blade back/up;3 HIT blade and near arm forward RIGHT at chest height whole body lunges2 pixels;4 followthrough blade low infront;5 idle. Same idle legs."},"skill":{"cols":3,"rows":2,"ms":[60,60,70,70,70,80],"hit":3,"anim":"Q FRONTAL SWEEP6frames:1 low behind crouch1pixel;2 back shoulder raise;3 HIT wide sweep forwardRIGHT chestheight;4 low infront;5 blade returningbehind;6 idle. Entire time front3/4, no spinning backview. Idlelegs."},"skill2":{"cols":4,"rows":1,"ms":[60,60,60,60],"hit":3,"anim":"E DASH4frames:1 lowered readiness;2 bodyforward3pixels lower2rows, legs separate oneback onefront, blade forwardRIGHThipheight;3 slashthrough blade swept backLEFT;4 riseidle. Never allfours."},"skill2_w":{"cols":4,"rows":2,"ms":[60,70,60,70,60,70,80],"hit":2,"anim":"W7frames:1 neararm blade overhead;2 FIRSTCHOP down infront to RIGHT;3 raise overhead;4 SECONDCHOP;5 raise;6 THIRDCHOP;7 idle. Body and legs exact idle body."},"ult":{"cols":3,"rows":2,"ms":[80,80,100,100,100,100],"hit":3,"anim":"R6frames:1 rising blade low;2 arms spread down/out;3 ROAR arms wide, head copy moves UP onepixel no rotation;4-5hold;6idle. No effects no enlargement. Legs exactidle."},"hit":{"cols":2,"rows":1,"ms":[100,100],"hit":None,"anim":"HIT2frames:1 entireidlebody jolt LEFT2pixels;2 recover LEFT1pixel. Character silhouette parts retained."},"dead":{"cols":4,"rows":2,"ms":[100,110,110,120,130,150,200,300],"hit":None,"anim":"DEATH8frames:1 joltleft;2 knockleft3pixels;3 WHOLE character includingblade/tail tipsbackwards45degrees;4 whole character90degrees lying ONBACK with head LEFT feetRIGHT;5-8 identical still corpse. Groundlowestrow81."}}
def moved(im,dx=0,dy=0,angle=0,anchor=(64,88)):
 # Map onto roomy canvas and rigidly rotate with nearest-neighbour sampling.
 canvas=Image.new('RGBA',(256,256))
 canvas.alpha_composite(im,(64+int(dx),64+int(dy)))
 if angle:canvas=canvas.rotate(angle,Image.Resampling.NEAREST,center=(64+anchor[0]+dx,64+anchor[1]+dy))
 return canvas.crop((64,64,192,192))
def darken(im):
 aa=np.array(im); mp={(1,128,132):(2,89,95),(2,89,95):(2,89,95),(194,192,192):(147,145,145),(147,145,145):(75,72,80),(2,24,178):(1,14,132)}
 for old,new in mp.items():mask=(aa[:,:,:3]==old).all(2)&(aa[:,:,3]>0);aa[mask,:3]=new
 return Image.fromarray(aa)
def cleanup_tiny(frame,protected):
 aa=np.array(frame);mask=aa[:,:,3]>0;seen=np.zeros(mask.shape,bool);removed=0
 for y,x in np.argwhere(mask):
  if seen[y,x]:continue
  todo=[(int(y),int(x))];seen[y,x]=True;points=[]
  while todo:
   yy,xx=todo.pop();points.append((yy,xx))
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     yn,xn=yy+dy,xx+dx
     if 0<=yn<96 and 0<=xn<128 and mask[yn,xn] and not seen[yn,xn]:seen[yn,xn]=True;todo.append((yn,xn))
  if len(points)<=10 and not any(protected[yy,xx] for yy,xx in points):
   for yy,xx in points:aa[yy,xx]=0;removed+=1
 return Image.fromarray(aa),removed
def compose(nearangle=0,farangle=0,tailangle=0,rear=(0,0),front=(0,0),farshade=False,headup=0,nearshift=(0,0),farshift=(0,0),tailshift=0):
 im=Image.new('RGBA',(128,128))
 im.alpha_composite(moved(layers['tail'],dx=tailshift,angle=tailangle,anchor=(48,89)))
 im.alpha_composite(moved(darken(layers['frontleg']) if farshade else layers['frontleg'],*front))
 im.alpha_composite(moved(layers['rearleg'],*rear))
 im.alpha_composite(layers['core'])
 im.alpha_composite(moved(layers['far'],*farshift,angle=farangle,anchor=(82,81)))
 im.alpha_composite(moved(layers['near'],*nearshift,angle=nearangle,anchor=(55,71)))
 im.alpha_composite(moved(layers['head'],dy=-headup))
 return im
# Idle reconstruction must be precisely the approved original.
assert np.array_equal(np.array(compose()),arr),'idle reconstruction mismatch'
def config(tag,i):
 c=dict(nearangle=0,farangle=0,tailangle=0,rear=(0,0),front=(0,0),farshade=False,headup=0,nearshift=(0,0),farshift=(0,0),tailshift=0)
 dx=dy=angle=0
 if tag=='run':
  # Exact intact leg pieces cross over alternate hip positions, not squashed.
  nearx=[23,19,13,7,1,5,11,17][i];farx=[-25,-21,-15,-9,-3,-7,-13,-19][i]
  neary=[0,-1,-2,-2,0,0,1,0][i];fary=[0,0,1,0,0,-1,-2,-2][i]
  c.update(rear=(nearx,neary),front=(farx,fary),farshade=True,tailangle=[0,0,0,0,0,0,0,0][i])
  dy=[0,0,-1,0,0,0,-1,0][i]
  c['tailshift']=[0,-1,-1,0,0,1,1,0][i]
 elif tag=='attack':
  c['nearangle']=[0,-90,180,90,0][i];dx=[0,-1,2,1,0][i]
 elif tag=='skill':
  c['nearangle']=[0,-90,180,90,-45,0][i];dx=[-1,-1,2,1,0,0][i]
 elif tag=='skill2':
  c['nearangle']=[-45,90,0,0][i];c['rear']=[(0,-1),(-3,-3),(-2,-1),(0,0)][i]
  c['front']=[(0,-1),(3,-2),(2,-1),(0,0)][i];dx=[1,3,2,0][i];dy=[1,2,1,0][i]
 elif tag=='skill2_w':
  c['nearangle']=[-90,90,-90,90,-90,90,0][i];dx=[0,1,0,1,0,1,0][i]
 elif tag=='ult':
  c['nearangle']=[0,-45,-45,-45,-45,0][i]
  c['farangle']=[0,45,45,45,45,0][i];c['headup']=1 if i in [2,3,4] else 0
 elif tag=='hit':dx=[-2,-1][i]
 elif tag=='dead':
  dx=[-1,-3,-3,-3,-3,-3,-3,-3][i]
  angle=[0,0,45,90,90,90,90,90][i]
  # The blade is drawn in as he loses balance so the corpse rests on ground.
  c['nearangle']=0 if i==0 else -90
  if i>=3:c['nearshift']=(9,0)
 # On frontal strikes the two arms use the two existing outer shoulder corners.
 if tag in ['attack','skill','skill2','skill2_w'] and c['nearangle'] in [90,180]:
  c['nearshift']=(29,10) if c['nearangle']==180 else (29,-2 if tag=='skill2' else 0)
  c['farshift']=(-27,-10);c['farangle']=-45
 return c,dx,dy,angle
manifest={'schema':1,'scale':8,'cell_1x':[128,96],'feet_row':81,'palette':['#%02X%02X%02X'%p for p in palette],'source_model_sha256':hashlib.sha256(design.tobytes()).hexdigest(),'animations':{}}
allframes={}
for tag,spec in specs.items():
 sheet=Image.new('RGBA',(128*spec['cols'],96*spec['rows']))
 frames=[];metadata=[]
 for i,cd in enumerate(cells['tags'][tag]):
  cfg,dx,dy,rotation=config(tag,i);model=compose(**cfg)
  if rotation:model=moved(model,angle=rotation,anchor=(64,88))
  bx=model.getbbox();px,py=cd['pivot']
  tx=px-64+dx;ty=py-88+dy
  # Whole-frame placement only. Do not shrink or delete any rows.
  if bx[3]+ty>82:ty-=bx[3]+ty-82
  frame=Image.new('RGBA',(128,96));frame.alpha_composite(model,(tx,ty))
  protection=Image.new('RGBA',(128,128))
  protection.alpha_composite(moved(layers['head'],dy=-cfg['headup']))
  protection.alpha_composite(moved(layers['rearleg'],*cfg['rear']))
  protection.alpha_composite(moved(layers['frontleg'],*cfg['front']))
  protection.alpha_composite(moved(blade_edge,*cfg['nearshift'],angle=cfg['nearangle'],anchor=(55,71)))
  if rotation:protection=moved(protection,angle=rotation,anchor=(64,88))
  fitted=Image.new('RGBA',(128,96));fitted.alpha_composite(protection,(tx,ty))
  frame,removed=cleanup_tiny(frame,np.array(fitted)[:,:,3]>0)
  assert not np.array(frame)[82:,:,3].any(),(tag,i,'below feet')
  assert frame.getbbox()[0]>0 and frame.getbbox()[2]<128,(tag,i,'horizontal clip')
  col=i%spec['cols'];row=i//spec['cols'];sheet.alpha_composite(frame,(col*128,row*96))
  frames.append(frame)
  hit=spec['hit']==i+1 or (tag=='skill2_w' and i+1 in [4,6])
  blade=moved(layers['near'],*cfg['nearshift'],angle=cfg['nearangle'],anchor=(55,71))
  if rotation:blade=moved(blade,angle=rotation,anchor=(64,88))
  bb=blade.getbbox()
  edge=moved(blade_edge,*cfg['nearshift'],angle=cfg['nearangle'],anchor=(55,71))
  if rotation:edge=moved(edge,angle=rotation,anchor=(64,88))
  ey,ex=np.where(np.array(edge)[:,:,3]>0);blade_mid=[round(float(ex.mean())+tx,3),round(float(ey.mean())+ty,3)]
  headtransform={'translation_from_design':[tx,ty-cfg['headup']],'rotation_deg':rotation if tag=='dead' else 0}
  metadata.append({'index':i+1,'ms':cd['ms'],'cell_rect_1x':[col*128,row*96,128,96],'cell_rect_8x':[col*1024,row*768,1024,768],'pivot_local_1x':[px,py],'pivot_sheet_1x':[col*128+px,row*96+py],'pivot_sheet_8x':[(col*128+px)*8,(row*96+py)*8],'bbox_local_1x':list(frame.getbbox()),'bbox_local_8x':[v*8 for v in frame.getbbox()],'head_transform':headtransform,'whole_body_offset_from_pivot':[dx,dy],'placement_translation_from_design':[tx,ty],'arm_blade_angle_deg':cfg['nearangle'],'body_rotation_deg':rotation,'hit_frame':hit,'blade_midpoint_local_1x':blade_mid if hit else None,'blade_midpoint_sheet_8x':[(col*128+blade_mid[0])*8,(row*96+blade_mid[1])*8] if hit else None,'blade_midpoint_method':'centroid of transformed ivory blade-edge pixels; no arm/handle pixels included','rig_config':{k:list(v) if isinstance(v,tuple) else v for k,v in cfg.items()}})
  metadata[-1]['isolated_border_pixels_removed']=removed
 sheet.save(OUT/(f'renekton_{tag}_1x.png'))
 sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST).save(OUT/(f'renekton_{tag}.png'))
 manifest['animations'][tag]={'frames':metadata,'grid':[spec['cols'],spec['rows']],'size_px':[sheet.width*8,sheet.height*8],'hit_frame':spec['hit'],'hit_tick':{'attack':7,'skill':7,'skill2':7,'skill2_w':4,'ult':10}.get(tag),'impact_frames':[2,4,6] if tag=='skill2_w' else ([spec['hit']] if spec['hit'] else []),'empowered_only_frames':[6] if tag=='skill2_w' else [],'source_route':'approved-model rigid-part composition; generated run attempt rejected'}
 allframes[tag]=frames
 # GIF animation makes pose/timing review straightforward.
 bgframes=[]
 for frame,cd in zip(frames,cells['tags'][tag]):
  aligned=Image.new('RGBA',frame.size);aligned.alpha_composite(frame,(64-cd['pivot'][0],70-cd['pivot'][1]))
  bg=Image.new('RGBA',frame.size,'#DCE5E8');bg.alpha_composite(aligned)
  bgframes.append(bg.convert('RGB').resize((512,384),Image.Resampling.NEAREST))
 bgframes[0].save(OUT/(f'preview_{tag}.gif'),save_all=True,append_images=bgframes[1:],duration=spec['ms'],loop=0,disposal=2)
# Preserve the supplied idle byte-for-byte.
import shutil
shutil.copy2(SRC/'renekton_idle.png',OUT/'renekton_idle.png')
shutil.copy2(SRC/'renekton_cells.json',OUT/'renekton_cells.json')
manifest['animations']['idle']={'source_route':'supplied unchanged','size_px':[3072,1536],'frames':[{'index':i+1,'ms':cd['ms'],'pivot_local_1x':cd['pivot'],'cell_rect_1x':[(i%3)*128,(i//3)*96,128,96]} for i,cd in enumerate(cells['tags']['idle'])]}
idle_big=Image.open(OUT/'renekton_idle.png').convert('RGBA');idle_small=Image.fromarray(np.array(idle_big)[::8,::8])
idle_small.save(OUT/'renekton_idle_1x.png')
for fm in manifest['animations']['idle']['frames']:
 x,y,w,h=fm['cell_rect_1x'];box=idle_small.crop((x,y,x+w,y+h)).getbbox();px,py=fm['pivot_local_1x']
 fm.update(cell_rect_8x=[x*8,y*8,w*8,h*8],bbox_local_1x=list(box),bbox_local_8x=[v*8 for v in box],pivot_sheet_1x=[x+px,y+py],pivot_sheet_8x=[(x+px)*8,(y+py)*8],hit_frame=False,blade_midpoint_local_1x=None)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Compact montage of all action frames, labels outside assets.
montage=Image.new('RGB',(220*8+120,160*8),'#DCE5E8');draw=ImageDraw.Draw(montage)
for row,(tag,frames) in enumerate(allframes.items()):
 draw.text((8,row*160+16),tag,fill='#17232B')
 for col,frame in enumerate(frames):
  crop=frame.crop((12,18,122,84)).resize((220,132),Image.Resampling.NEAREST)
  montage.paste(crop,(120+col*220,row*160+24),crop)
  draw.text((120+col*220,row*160+8),str(col+1),fill='#17232B')
montage.save(OUT/'all_actions_review.png')
print('done',[(k,len(v)) for k,v in allframes.items()])



