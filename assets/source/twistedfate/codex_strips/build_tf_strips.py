from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,shutil,hashlib
ROOT=Path(r'C:/Users/OWNER/Documents/Codex/2026-10-04/new-chat-3')
IN=ROOT/'work/twistedfate-strips-input/twistedfate_strips_pack'
OUT=ROOT/'outputs/twistedfate-strips';OUT.mkdir(parents=True,exist_ok=True)
CELLS=json.loads((IN/'twistedfate_cells.json').read_text(encoding='utf-8'))
D=Image.open(IN/'design/twistedfate_design_1x.png').convert('RGBA')
H=Image.open(IN/'design/twistedfate_head_1x.png').convert('RGBA'); HB=H.getbbox();HEAD=H.crop(HB)
C=Image.open(IN/'design/twistedfate_cards_1x.png').convert('RGBA');CB=C.getbbox();CARDS=C.crop(CB)
PAL=set(tuple(p[:3]) for p in np.array(D).reshape(-1,4) if p[3])
INK='#0D0B12';NAVY='#262A3A';LIGHT='#3A4057';GOLD='#F2C23A';BROWN='#6B4224';SKIN='#D58C5C'
LAYOUT={'idle':(3,2),'run':(4,2),'attack':(3,2),'skill':(3,2),'skill2':(2,1),'ult':(4,1),'ult_gate':(3,2),'ult_land':(3,1),'hit':(2,1),'dead':(4,2)}
NEAR={
 'attack':[(54,84),(61,81),(52,80),(74,80),(72,83),(55,84)],
 'skill':[(60,80),(53,80),(52,85),(74,85),(72,87),(54,84)],
 'skill2':[(61,81),(64,80)],
 'ult':[(51,81),(43,79),(43,79),(43,79)],
 'ult_gate':[(61,90)]*6,'ult_land':[(61,90),(59,85),(54,84)],
 'hit':[(54,82),(54,84)],'dead':[(53,85),(53,82),(54,84),(54,85),(59,89),(58,91),(54,84),(54,84)]}
FAR={'ult':[(74,81),(81,79),(81,79),(81,79)],'ult_gate':[(73,83)]*6,'ult_land':[(73,83),(72,86),(70,87)]}
def paste(canvas,im,xy):canvas.alpha_composite(im,dest=tuple(map(int,xy)))
def patch(canvas,box,dx,dy):paste(canvas,D.crop(box),(box[0]+dx,box[1]+dy))
def limb(im,points,near=False):
 d=ImageDraw.Draw(im);d.line(points,fill=INK,width=5);d.line(points,fill=NAVY,width=3)
 d.line([(x,y-1) for x,y in points],fill=LIGHT,width=1)
 x,y=points[-1];d.rectangle((x-1,y-1,x+1,y+1),fill=GOLD)
 if not near:
  d.rectangle((x,y,x+2,y+2),fill=SKIN);d.point((x,y),fill='#B8BCC8')
def leg(im,hip,knee,foot,side):
 d=ImageDraw.Draw(im);d.line([hip,knee,foot],fill=INK,width=5);d.line([hip,knee,foot],fill=NAVY,width=3)
 d.line([knee,foot],fill=BROWN,width=3)
 x,y=foot;d.rectangle((x-1,y-3,x+1,y-3),fill=GOLD)
 d.line([(x-1,y),(x+3,y)],fill=INK,width=3);d.line([(x,y-1),(x+3,y-1)],fill=BROWN,width=1)
def make(tag,i,info):
 im=Image.new('RGBA',(128,96));px,py=info['pivot'];dx=px-64;dy=py-88
 crouch=0;hop=0;lean=0
 if tag=='skill':crouch=[0,0,4,4,3,0][i];hop=[0,2,0,0,0,0][i]
 if tag=='ult_gate':crouch=9+[0,0,1,1,0,0][i]
 if tag=='ult_land':crouch=[9,4,0][i]
 if tag=='hit':lean=[-2,0][i]
 if tag=='dead':crouch=[2,0,1,2,6,7,0,0][i];lean=[-1,-2,-1,-2,-1,-2,0,0][i]
 if tag=='dead' and i>=6:
  lying=D.crop(D.getbbox()).transpose(Image.Transpose.ROTATE_90)
  x=px-lying.width//2;y=82-lying.height
  paste(im,lying,(x,y));return im,{'head_rect':[x,y,HEAD.height,HEAD.width],'head_transform':'rotate_90_ccw','cards_rect':[x+22,y+14,6,8],'cards_transform':'rotate_90_ccw','hand':[x+27,y+18],'pose':'lying'}
 if (tag=='attack' and i in [0,5]) or (tag=='skill' and i==5) or (tag=='ult_land' and i==2) or (tag=='hit' and i==1):
  full=D.crop(D.getbbox());paste(im,full,(49+dx,59+dy))
  return im,{'head_rect':[49+dx,59+dy,24,18],'head_transform':'translate','cards_rect':[51+dx,81+dy,8,6],'hand':[54+dx,86+dy],'pose':'exact_idle'}
 dx+=lean;dy-=hop
 bob=([0,1,0,1,0,1,0,1][i] if tag=='run' else 0)
 topdy=dy+crouch-bob
 # Back skirt kept at original size, with at most one-column sway.
 sway=([-1,0,1,0,1,0,-1,0][i] if tag=='run' else (1 if i%2 else 0))
 patch(im,(49,89,58,99),dx+sway,dy)
 if tag=='run':
  dr=ImageDraw.Draw(im)
  dr.line([(59+dx,86+topdy),(54+dx+sway,93+dy)],fill=INK,width=5)
  dr.line([(59+dx,86+topdy),(54+dx+sway,93+dy)],fill=NAVY,width=3)
  dr.line([(58+dx,87+topdy),(53+dx+sway,94+dy)],fill='#C08A1C',width=1)
 if tag in ['run','ult_gate','ult_land','dead'] or crouch:
  if tag=='run':
   stride=[-3,-1,2,3,3,1,-2,-3][i]
   for side,sgn in [(0,-1),(1,1)]:
    leg(im,(61+side*5+dx,89+dy-bob),(61+side*4+dx+sgn*stride//2,94+dy),(61+side*3+dx+sgn*stride,98+dy),side)
  else:
   for side in [0,1]:leg(im,(61+side*5+dx,min(79,89+topdy)),(57+side*12+dx,96+dy),(58+side*10+dx,98+dy),side)
 else:
  lower=D.crop((58,89,73,100));la=np.array(lower)
  # These two skin pixels belong to the original far hand, not to the legs.
  la[0,12]=[0,0,0,0];la[1,12]=[0,0,0,0]
  legdx=px-64 if tag=='hit' else dx
  paste(im,Image.fromarray(la),(58+legdx,89+dy))
 # Copy collar, waistcoat and coat torso exactly; articulated arms are drawn
 # below the head so the original face never gets overpainted.
 patch(im,(55,77,68,81),dx,topdy)
 torso=D.crop((58,81,68,89))
 ta=np.array(torso)
 # Erase all old fan/finger pixels where the source hand overlapped the torso.
 ca=np.array(C)
 for yy in range(81,87):
  for xx in range(58,59):
   if ca[yy,xx,3]:ta[yy-81,xx-58]=[0,0,0,0]
 paste(im,Image.fromarray(ta),(58+dx,81+topdy))
 near=NEAR.get(tag,[(54,84)]*len(CELLS['tags'][tag]))[i]
 if tag=='run':near=(54,84-bob)
 nx,ny=near[0]+dx,near[1]+dy
 far=FAR.get(tag,[(70,87)]*len(CELLS['tags'][tag]))[i]
 fx,fy=far[0]+dx,far[1]+dy
 if tag=='run':fx+=([1,0,-1,-2,-1,0,1,2][i])
 near_sh=(57+dx,81+topdy);far_sh=(66+dx,81+topdy)
 elbow=((near_sh[0]+nx)//2-1,(near_sh[1]+ny)//2+1)
 if tag=='attack' and i==2:elbow=(55+dx,78+dy)
 limb(im,[far_sh,((far_sh[0]+fx)//2,(far_sh[1]+fy)//2+1),(fx,fy)])
 limb(im,[near_sh,elbow,(nx,ny)],True)
 cardxy=(nx-1,ny-3)
 # Unchanged fan including fingers and white cuff. Attach its cuff to the arm.
 paste(im,CARDS,cardxy)
 headxy=(HB[0]+dx,HB[1]+topdy)
 paste(im,HEAD,headxy)
 # The floor constraint applies to all authored coordinates, not a post-export crop.
 assert im.getbbox()[3]<=82,(tag,i,im.getbbox())
 return im,{'head_rect':[headxy[0],headxy[1],HEAD.width,HEAD.height],'head_transform':'translate','cards_rect':[cardxy[0],cardxy[1],CARDS.width,CARDS.height],'hand':[nx+2,ny+2],'pose':'crouch' if crouch else 'hop' if hop else 'standing'}

manifest={'cell_1x':[128,96],'scale':8,'palette':['#'+bytes(c).hex() for c in sorted(PAL)],'animations':{}}
validation={};frames_all={};story=Image.new('RGB',(8*240,10*200),'#252836');sd=ImageDraw.Draw(story)
for row,(tag,(cols,rows)) in enumerate(LAYOUT.items()):
 frames=[]; records=[]
 if tag=='idle':
  sheet=Image.open(IN/'twistedfate_idle.png').convert('RGBA');small=sheet.resize((cols*128,rows*96),Image.Resampling.NEAREST)
 else:small=Image.new('RGBA',(cols*128,rows*96))
 for i,info in enumerate(CELLS['tags'][tag]):
  if tag=='idle':im=small.crop((i%cols*128,i//cols*96,i%cols*128+128,i//cols*96+96));meta={'head_transform':'source_idle','hand':[info['pivot'][0]-8,info['pivot'][1]-4]}
  else:
   im,meta=make(tag,i,info);paste(small,im,(i%cols*128,i//cols*96))
  a=np.array(im); colors=set(tuple(v[:3]) for v in a.reshape(-1,4) if v[3]);assert colors<=PAL
  assert set(np.unique(a[:,:,3]))<={0,255};assert not a[82:,:,3].any()
  if meta.get('head_transform') in ['translate','rotate_90_ccw']:
   expected=HEAD if meta['head_transform']=='translate' else HEAD.transpose(Image.Transpose.ROTATE_90)
   x,y,w,h=meta['head_rect'];region=np.array(im.crop((x,y,x+w,y+h)));hm=np.array(HEAD)[:,:,3]>0
   hm=np.array(expected)[:,:,3]>0
   assert np.array_equal(region[hm],np.array(expected)[hm]),(tag,i,'head')
  if 'cards_rect' in meta:
   expected=CARDS if meta.get('cards_transform')!='rotate_90_ccw' else CARDS.transpose(Image.Transpose.ROTATE_90)
   x,y,w,h=meta['cards_rect'];reg=np.array(im.crop((x,y,x+w,y+h)));cm=np.array(expected)[:,:,3]>0
   assert np.array_equal(reg[cm],np.array(expected)[cm]),(tag,i,'cards occluded')
  frames.append(im)
  cell=[i%cols*1024,i//cols*768,1024,768]
  bb=im.getbbox();record={'frame':i+1,'ms':info['ms'],'cell_rect_px':cell,'pivot_1x':info['pivot'],'pivot_cell_px':[n*8 for n in info['pivot']],'bbox_cell_1x':bb,'bbox_sheet_px':[cell[0]+bb[0]*8,cell[1]+bb[1]*8,cell[0]+bb[2]*8,cell[1]+bb[3]*8],**meta}
  if tag in ['attack','skill'] and i==3:record['release_tick']=12;record['release_hand_cell_px']=[n*8 for n in meta['hand']]
  records.append(record)
  display=Image.new('RGB',(128,96),'#252836');display.paste(im,(0,0),im)
  bbox=im.getbbox();crop=display.crop((max(0,bbox[0]-4),max(0,bbox[1]-3),min(128,bbox[2]+4),84))
  crop=crop.resize((crop.width*3,crop.height*3),Image.Resampling.NEAREST)
  story.paste(crop,(i*240+8,row*200+35));sd.text((i*240+8,row*200+8),f'{tag} {i+1} / {info["ms"]} ms',fill='white')
 big=small.resize((small.width*8,small.height*8),Image.Resampling.NEAREST)
 if tag=='idle':shutil.copy2(IN/'twistedfate_idle.png',OUT/'twistedfate_idle.png')
 else:big.save(OUT/f'twistedfate_{tag}.png')
 small.save(OUT/f'twistedfate_{tag}_1x.png')
 preview=[]
 for im in frames:
  p=Image.new('RGB',(128,96),'#252836');p.paste(im,(0,0),im);preview.append(p.crop((25,30,125,84)).resize((400,216),Image.Resampling.NEAREST))
 preview[0].save(OUT/f'preview_{tag}.gif',save_all=True,append_images=preview[1:],duration=[v['ms'] for v in CELLS['tags'][tag]],loop=0 if tag!='dead' else 1,disposal=2)
 manifest['animations'][tag]={'image':f'twistedfate_{tag}.png','grid':[cols,rows],'size_px':list(big.size),'frames':records}
 validation[tag]={'frame_count':len(frames),'grid_8px':True,'binary_alpha':True,'palette_subset':True,'floor_clear':True,'head_pixels_identical':True,'fan_pixels_identical':True,'lying_head_rotated_90_degrees':tag=='dead','idle_copied':tag=='idle'}
 frames_all[tag]=frames
story.save(OUT/'all_frames_preview.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
shutil.copy2(IN/'twistedfate_cells.json',OUT/'twistedfate_cells.json')
print('Exported',sum(len(v) for v in frames_all.values()),'frames',json.dumps(validation))
