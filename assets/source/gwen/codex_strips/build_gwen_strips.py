from PIL import Image, ImageDraw
import numpy as np
from pathlib import Path
import json, shutil, math, hashlib

B=Path('work/gwen_strips_pack/gwen_strips_pack'); O=Path('outputs/gwen-strips'); O.mkdir(parents=True,exist_ok=True)
(O/'raw').mkdir(exist_ok=True); (O/'preview').mkdir(exist_ok=True)
D=Image.open(B/'design/gwen_design_1x.png').convert('RGBA'); H=Image.open(B/'design/gwen_head_1x.png').convert('RGBA'); HB=H.getbbox(); head=H.crop(HB)
cells=json.loads((B/'gwen_cells.json').read_text(encoding='utf-8'))
def part(box,polygon=None):
    im=D.crop(box)
    if polygon:
        m=Image.new('L',im.size); ImageDraw.Draw(m).polygon([(x-box[0],y-box[1]) for x,y in polygon],fill=255)
        im.putalpha(Image.fromarray(np.minimum(np.array(im.getchannel('A')),np.array(m))))
    return im
leftarm=part((56,74,62,83),[(58,74),(61,75),(61,79),(59,82),(56,80),(57,76)])
rightarm=part((72,73,77,82),[(74,73),(76,74),(76,80),(74,81),(72,78)])
torso=part((54,70,78,89)); a=np.array(torso)
for y in range(a.shape[0]):
    for x in range(a.shape[1]):
        gx,gy=x+54,y+70
        if gx>=76 and gy>=74: a[y,x]=0
torso=Image.fromarray(a)
ta=np.array(torso)
for arm,ax,ay in [(leftarm,56,74),(rightarm,72,73)]:
    aa=np.array(arm)
    for yy,xx in np.argwhere(aa[:,:,3]>0):
        tx,ty=xx+ax-54,yy+ay-70
        if 0<=tx<ta.shape[1] and 0<=ty<ta.shape[0]: ta[ty,tx]=0
torso=Image.fromarray(ta)
legs=part((57,87,71,100)); lleg=part((57,87,64,100)); rleg=part((64,87,71,100))
# Weapon artwork comes from the approved model. Continue its concealed blade
# using stamps of its own diagonal middle segment, under the torso layer.
weapon=Image.new('RGBA',(128,128)); wa=np.array(D); wm=np.zeros((128,128),bool)
wm[73:91,74:88]=(wa[73:91,74:88,1]>100)&(wa[73:91,74:88,2]>150)&(wa[73:91,74:88,0]<150)&(wa[73:91,74:88,3]>0)
wm0=wm.copy(); wm=wm0|np.roll(wm0,1,0)|np.roll(wm0,-1,0)|np.roll(wm0,1,1)|np.roll(wm0,-1,1)
wm=wm&(wa[:,:,3]>0)&(np.indices(wm.shape)[1]>=74)&(np.indices(wm.shape)[0]>=72)&(np.indices(wm.shape)[0]<91)
wr=wa.copy(); wr[~wm]=0; weapon.alpha_composite(Image.fromarray(wr))
ba=np.array(D); bm=np.zeros((128,128),bool)
bm[83:97,34:58]=(ba[83:97,34:58,1]>100)&(ba[83:97,34:58,2]>150)&(ba[83:97,34:58,0]<150)&(ba[83:97,34:58,3]>0)
bm0=bm.copy(); bm=bm0|np.roll(bm0,1,0)|np.roll(bm0,-1,0)|np.roll(bm0,1,1)|np.roll(bm0,-1,1)
bm=bm&(ba[:,:,3]>0)&(np.indices(bm.shape)[1]<58)&(np.indices(bm.shape)[0]>=83)
ba[~bm]=0; bladefull=Image.fromarray(ba); weapon.alpha_composite(bladefull)
stamp=bladefull.crop((46,87,52,92))
for k in range(1,6): weapon.paste(stamp,(46+6*k,87-2*k),stamp)
wb=(34,72,88,97); weapon=weapon.crop(wb)
palette=sorted(set(tuple(p[:3]) for p in np.array(D).reshape(-1,4) if p[3]))
def rotated(im,deg): return im.rotate(deg,Image.Resampling.NEAREST,expand=True)
def pivotpaste(dest,im,anchor,destpoint,deg=0):
    if deg==0:
        dest.alpha_composite(im,(round(destpoint[0]-anchor[0]),round(destpoint[1]-anchor[1]))); return
    rad=math.radians(deg); cx,cy=im.width/2,im.height/2; v=(anchor[0]-cx,anchor[1]-cy)
    r=rotated(im,deg); ar=(r.width/2+v[0]*math.cos(rad)+v[1]*math.sin(rad),r.height/2-v[0]*math.sin(rad)+v[1]*math.cos(rad))
    dest.alpha_composite(r,(round(destpoint[0]-ar[0]),round(destpoint[1]-ar[1])))
def place(frame,im,x,y): frame.alpha_composite(im,(round(x),round(y)))
def build(tag,i,p):
    px,py=p['pivot']; frame=Image.new('RGBA',(128,96)); ox,oy=px-64,py-88
    bob=0; shiftx=0; bodyangle=0; weaponangle=0; detached=False; openangle=0; hand=None
    if tag=='run': bob=[0,-1,0,0,0,-1,0,0][i]; weaponangle=-98
    if tag=='attack': shiftx=[0,0,-1,2,1,0][i]; weaponangle=[-20,158,158,158,95,0][i]
    if tag=='skill': shiftx=[0,0,0,0,0,2,2,0][i]; bob=[0,0,0,0,0,2,2,0][i]; weaponangle=[145,145,158,145,158,140,140,0][i]; openangle=[0,26,0,26,0,36,36,0][i]
    if tag=='skill2': shiftx=[0,2,3,0,0,0,0,0][i]; bob=[0,1,0,0,-1,-1,0,0][i]; weaponangle=[0,-25,0,0,135,158,110,0][i]
    if tag=='hit': shiftx=[-2,0][i]
    if tag=='dead':
        detached=i>=1
        bob=[0,0,1,10,15,18,26,26][i]; shiftx=[-1,-2,-2,0,0,0,-3,-3][i]
        bodyangle=[0,0,0,-15,-35,-55,-80,-80][i]
    x,y=ox+shiftx,oy+bob
    # Animate complete approved body parts, never substitute geometric bodies.
    if detached:
        pivotpaste(frame,weapon,(43,7),(px-6,76),28)
    elif tag=='run':
        hand=(px-5,py-16+bob); pivotpaste(frame,weapon,(43,7),hand,weaponangle)
    elif tag in ('attack','skill') and i not in (0,len(cells['tags'][tag])-1):
        hand=(px+15+shiftx,py-16+bob); pivotpaste(frame,weapon,(43,7),hand,weaponangle)
        if openangle:
            # The second blade uses the same accepted blade art and palette.
            pivotpaste(frame,weapon,(43,7),hand,weaponangle+openangle)
    elif tag=='skill2' and 4<=i<=6:
        hand=(px-3,py-32+bob); pivotpaste(frame,weapon,(43,7),hand,weaponangle)
    else:
        hand=(x+77,y+79); pivotpaste(frame,weapon,(43,7),hand,weaponangle)
    if tag=='run' or tag=='skill2' and i<3:
        stride=[(-2,2,15,-15),(-1,1,8,-8),(0,0,0,0),(2,-2,-15,15),(2,-2,-15,15),(1,-1,-8,8),(0,0,0,0),(-2,2,15,-15)][i]
        for leg,base,d,ang in [(lleg,57,stride[0],stride[2]),(rleg,64,stride[1],stride[3])]:
            r=rotated(leg,ang); place(frame,r,base+x+d,82-r.height)
    elif tag=='dead' and i>=3:
        pivotpaste(frame,legs,(7,0),(px+5,py+1),bodyangle)
    elif tag in ('attack','skill') and (tag=='attack' and i==3 or tag=='skill' and i in (5,6)):
        place(frame,lleg,57+x-3,82-lleg.height); place(frame,rleg,64+x+3,82-rleg.height)
    else: place(frame,legs,57+x,87+oy)
    if bodyangle: pivotpaste(frame,torso,(10,18),(px,py+bob//2),bodyangle)
    else: place(frame,torso,54+x,70+y)
    if tag in ('attack','skill') and hand and i not in (0,len(cells['tags'][tag])-1):
        pivotpaste(frame,rightarm,(2,1),(px+5+shiftx,py-16+bob),90)
        pivotpaste(frame,leftarm,(2,1),(px+6+shiftx,py-17+bob),85)
    elif tag=='skill2' and 4<=i<=6:
        pivotpaste(frame,leftarm,(2,1),(px-7,py-19+bob),-160)
        pivotpaste(frame,rightarm,(2,1),(px+7,py-19+bob),150)
    elif tag=='ult' and i in (1,2,3,4):
        pivotpaste(frame,rightarm,(2,1),(px+10,py-16),[-135,-135,90,60][i-1])
        place(frame,leftarm,56+x,74+y)
    else:
        place(frame,leftarm,56+x,74+y); place(frame,rightarm,72+x,73+y)
    hx,hy=54+x,56+y
    if tag=='dead' and i>=3: hx,hy=px-15,py-12+min(i-3,3)
    # Head pixels are unchanged and are pasted last; translation only.
    frame.paste(head,(round(hx),round(hy)),head)
    if tag=='ult' and i<=2:
        needle=part((45,89,48,92)); place(frame,needle,px+10,py-25 if i else py-15)
    if tag=='dead' and i>=1:
        frame=Image.new('RGBA',(128,96))
        pivotpaste(frame,weapon,(43,7),(px-4,79),-22)
        actor=Image.new('RGBA',(128,128)); actor.alpha_composite(torso,(54,70)); actor.alpha_composite(legs,(57,87)); actor.alpha_composite(leftarm,(56,74)); actor.alpha_composite(rightarm,(72,73))
        ab=(54,70,78,100); actor=actor.crop(ab)
        angle=[0,0,0,15,30,50,80,80][i]
        pivotpaste(frame,actor,(10,18),(px,py),angle)
        hx=px-10 if i<=2 else px-10-round(18*math.sin(math.radians(angle)))
        hy=38 if i<=2 else round(70-18*math.cos(math.radians(angle))-14)
        frame.paste(head,(hx,hy),head)
        hand=None
    # Move the whole frame upwards when a posed part would cross the floor;
    # no row is deleted, and no actor pixels are scaled.
    ar=np.array(frame); below=int((ar[82:,:,3]>0).sum()); box=frame.getbbox()
    if box and box[3]>82:
        up=box[3]-82; fixed=Image.new('RGBA',(128,96)); fixed.alpha_composite(frame,(0,-up)); frame=fixed; hy-=up
        if hand: hand=(hand[0],hand[1]-up)
    ar=np.array(frame); ar[ar[:,:,3]==0]=0
    frame=Image.fromarray(ar)
    tip=None
    if hand:
        rad=math.radians(weaponangle)
        tip=[round(hand[0]-43*math.cos(rad)+16*math.sin(rad)),round(hand[1]+43*math.sin(rad)+16*math.cos(rad))]
    return frame,{'head_rect':[round(hx),round(hy),head.width,head.height],'hand':list(map(round,hand)) if hand else None,'tip':tip,'pixels_below_before_cleanup':below,'body_bob':bob,'shift_x':shiftx,'weapon_angle':weaponangle,'open_angle':openangle}

manifest={'coordinate_units':'1x logical pixels unless stated','cell':[128,96],'scale':8,'palette':['#%02X%02X%02X'%c for c in palette],'source_design_sha256':hashlib.sha256((B/'design/gwen_design_1x.png').read_bytes()).hexdigest(),'route':'approved-pixel-part rig, no body resizing or row deletion; generated action sheets retained as pose drafts','animations':{}}
impact={'attack':(3,11),'skill':(5,17),'skill2':(5,16),'ult':(3,10)}
allpreview=Image.new('RGB',(1024,8*224),(220,220,220)); draw=ImageDraw.Draw(allpreview)
for row,(tag,seq) in enumerate(cells['tags'].items()):
    n=len(seq); cols=2 if tag=='hit' else 3 if n==6 else 4; rows=math.ceil(n/cols)
    sheet=Image.new('RGBA',(cols*128,rows*96)); frames=[]; data=[]
    for i,p in enumerate(seq):
        if tag=='idle':
            src=Image.open(B/'gwen_idle.png'); frame=src.crop(((i%3)*1024,(i//3)*768,(i%3+1)*1024,(i//3+1)*768)).resize((128,96),Image.Resampling.NEAREST); info={'head_rect':[59,38,22,14],'hand':None,'pixels_below_before_cleanup':0}
        else: frame,info=build(tag,i,p)
        if tag=='dead' and i==7: frame=frames[6].copy(); info=data[6]['rig'].copy()
        frames.append(frame); sheet.paste(frame,((i%cols)*128,(i//cols)*96))
        a=np.array(frame); coords=np.argwhere(a[:,:,3]>0); bb=frame.getbbox()
        cyan=(a[:,:,1]>100)&(a[:,:,2]>150)&(a[:,:,0]<150)&(a[:,:,3]>0)
        if tag in impact and i==impact[tag][0]:
            tip=info.get('tip')
        else: tip=None
        data.append({'index':i+1,'cell_rect':[i%cols*128,i//cols*96,128,96],'cell_rect_8x':[i%cols*1024,i//cols*768,1024,768],'pivot':p['pivot'],'ms':p['ms'],'bbox':list(bb) if bb else None,'head_rect':info['head_rect'],'scissor_tip':tip,'gripping_hand':info['hand'],'impact':tag in impact and i==impact[tag][0],'rig':info})
        crop=frame.crop((0,20,128,84)).resize((256,128),Image.Resampling.NEAREST)
        if i<4: allpreview.paste(crop,(i*256,row*224+30),crop)
    sheet.save(O/f'gwen_{tag}_1x.png'); sheet.resize((cols*1024,rows*768),Image.Resampling.NEAREST).save(O/f'gwen_{tag}.png')
    if tag=='idle': shutil.copy2(B/'gwen_idle.png',O/'gwen_idle.png')
    gifframes=[]
    for f in frames:
        rgb=Image.new('RGBA',(128,96),(224,224,224,255)); rgb.alpha_composite(f); gifframes.append(rgb.convert('RGB').resize((512,384),Image.Resampling.NEAREST))
    gifframes[0].save(O/'preview'/f'gwen_{tag}.gif',save_all=True,append_images=gifframes[1:],duration=[p['ms'] for p in seq],loop=0,disposal=2)
    manifest['animations'][tag]={'frames':data,'frame_count':n,'image_size':[cols*1024,rows*768],'grid':[cols,rows],'impact_frame':impact[tag][0]+1 if tag in impact else None,'impact_tick':impact[tag][1] if tag in impact else None}
    draw.text((8,row*224+5),tag,fill=(30,30,30))
allpreview.save(O/'preview'/'gwen_overview.png')
shutil.copy2(B/'gwen_cells.json',O/'gwen_cells.json')
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Built',sum(len(v) for v in cells['tags'].values()),'frames',flush=True)
