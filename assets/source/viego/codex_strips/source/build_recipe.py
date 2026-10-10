from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np, json, math, shutil, hashlib

B=Path(__file__).resolve().parent/'input'; O=Path(__file__).resolve().parents[1]
for p in [O,O/'raw',O/'preview',O/'1x',O/'source']:p.mkdir(parents=True,exist_ok=True)
D=Image.open(B/'design/viego_design_1x.png').convert('RGBA')
H=Image.open(B/'design/viego_head_1x.png').convert('RGBA')
da=np.array(D);hm=np.array(H)[:,:,3]>0
palette=np.unique(da[da[:,:,3]>0,:3],axis=0)
C=json.loads((B/'viego_cells.json').read_text())
layout={'idle':(3,2),'run':(4,2),'attack':(3,2),'skill':(3,2),'skill2':(4,2),'ult':(4,2),'possess':(4,1),'hit':(2,1),'dead':(4,2)}
impact={'attack':(5,14),'skill':(4,8),'skill2':(5,24),'ult':(6,19),'possess':(3,10)}
def poly(points):
    m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(points,fill=255);return np.array(m)>0
mask_weapon=poly([(43,65),(49,64),(49,59),(58,55),(58,62),(61,63),(94,48),(96,51),(69,68),(59,69),(56,76),(50,79),(43,76)]) & ~hm
# Remove body-color regions from the rigid weapon, while preserving the source gripping hand.
teal=(da[:,:,1]>da[:,:,0]*1.3) & (da[:,:,1]>70)
seed=mask_weapon & teal
expanded=seed.copy()
for yy in [-1,0,1]:
    for xx in [-1,0,1]:expanded |=np.roll(np.roll(seed,yy,0),xx,1)
outline=np.all(da[:,:,:3]==(4,2,14),axis=2)
mask_weapon=(seed|(expanded&outline)) & ~hm
mask_weapon[:71,76:]=da[:71,76:,3]>0
mask_weapon[67:72,50:56] |= (da[67:72,50:56,3]>0)&~hm[67:72,50:56]
mask_near=poly([(48,68),(54,67),(59,73),(61,79),(57,81),(50,79),(49,74)]) & ~hm & ~mask_weapon
mask_far=poly([(73,76),(78,76),(80,82),(81,87),(77,89),(74,86),(73,81)]) & ~hm
mask_tail=poly([(77,87),(85,91),(86,96),(79,94),(73,92)])
mask_lleg=poly([(54,85),(65,85),(66,89),(63,94),(63,100),(52,100),(52,95),(53,90)])
mask_rleg=poly([(65,85),(75,85),(78,90),(80,100),(70,100),(69,95),(66,91)]) & ~mask_lleg
parts={}
def cut(mask):
    a=da.copy();a[~mask]=0;return Image.fromarray(a)
for name,m in [('weapon',mask_weapon),('near',mask_near),('far',mask_far),('tail',mask_tail),('left',mask_lleg),('right',mask_rleg)]:parts[name]=cut(m)
# Recover the straight blade hidden by the idle head by translating existing blade
# pixels along its axis. No new colors, sizes, geometric body, or generated model.
w=parts['weapon'].copy();bladepatch=Image.new('RGBA',(128,128));bladepatch.alpha_composite(parts['weapon'].crop((76,48,96,65)),(76,48))
for tx,ty in [(-18,9),(-12,6),(-6,3)]:
    tmp=Image.new('RGBA',(128,128));tmp.alpha_composite(bladepatch,(tx,ty));tmp.alpha_composite(w);w=tmp
parts['weapon']=w
used=hm|mask_weapon|mask_near|mask_far|mask_tail|mask_lleg|mask_rleg
parts['torso']=cut(~used)
parts['pelvis']=cut(poly([(54,83),(74,83),(78,90),(53,90)]))
parts['head']=H
for n,p in parts.items():p.save(O/'source'/f'part_{n}.png')

def rotpoint(p,pivot,angle):
    t=math.radians(angle);c=math.cos(t);s=math.sin(t);x=p[0]-pivot[0];y=p[1]-pivot[1]
    return (pivot[0]+c*x-s*y,pivot[1]+s*x+c*y)
def warp(part,pivot,angle=0,shift=(0,0)):
    t=math.radians(angle);c=math.cos(t);s=math.sin(t);px,py=pivot;dx,dy=shift
    # Inverse map; samples the existing pixel part without scaling.
    coeff=(c,s,px-c*(px+dx)-s*(py+dy),-s,c,py+s*(px+dx)-c*(py+dy))
    return part.transform((128,128),Image.Transform.AFFINE,coeff,Image.Resampling.NEAREST)
def layer(canvas,im):canvas.alpha_composite(im)

# angle is screen-clockwise. Blade originally points roughly -26 degrees.
# Each tuple: torso lean, vertical offset, arm swing, blade angle, leg mode, whole dx.
plans={
 'run':[(0,0,0,-26,'run0',0),(0,-1,0,-26,'run1',0),(0,0,0,-26,'run2',0),(0,-1,0,-26,'run3',0),(0,0,0,-26,'run4',0),(0,-1,0,-26,'run5',0),(0,0,0,-26,'run6',0),(0,-1,0,-26,'run7',0)],
 'attack':[(0,0,0,-26,'stand',0),(-5,0,20,-45,'stand',-1),(-8,0,35,-85,'stand',-1),(12,-3,125,-55,'jump',2),(15,6,145,0,'lunge',3),(0,0,0,-26,'stand',0)],
 'skill':[(0,0,12,-36,'stand',0),(-8,0,-20,-170,'stand',-1),(-8,3,-10,-170,'crouch',-1),(15,0,150,0,'lunge',3),(15,0,150,0,'lunge',3),(0,0,20,-26,'stand',0)],
 'skill2':[(0,0,150,20,'stand',0),(0,-2,-10,145,'jump',-2),(0,0,135,-90,'stand',0),(0,2,135,-90,'crouch',0),(18,0,-25,-155,'lunge',3),(8,0,145,0,'lunge',2),(0,0,15,-26,'stand',0)],
 'ult':[(0,0,0,-26,'stand',0),(-8,3,30,-70,'crouch',0),(8,-2,145,20,'jump',1),(0,-5,0,0,'jump',1),(0,0,135,90,'stand',0),(12,6,145,90,'kneel',1),(12,6,145,90,'kneel',1),(0,0,25,-26,'stand',0)],
 'possess':[(0,0,15,-26,'stand',0),(0,0,-15,145,'stand',-1),(12,6,145,65,'kneel',2),(0,0,25,-26,'stand',0)],
 'hit':[(0,0,0,-26,'stand',-2),(0,0,0,-26,'stand',0)],
 'dead':[(-8,0,25,-55,'stand',-2),(8,0,115,70,'stand',1),(10,5,145,90,'kneel',1),(14,7,145,90,'kneel',1),(16,8,145,90,'kneel',1),(18,9,145,90,'kneel',1),(18,9,145,90,'kneel',1),(18,9,145,90,'kneel',1)]
}
def make(tag,i,pivot):
    lean,dy,arm,blade,legs,dx=plans[tag][i]
    shift=(pivot[0]-64+dx,pivot[1]-88+dy)
    if tag=='hit' or (tag=='attack' and i in(0,5)):
        direct=warp(D,(0,0),0,shift)
        return direct,{'head_translation':list(shift),'gripping_hand':[53+shift[0],69+shift[1]],'sword_tip':[93+shift[0],50+shift[1]],'torso_lean_degrees':0,'leg_pose':'stand','source':'approved_design_exact_translation','grid_scale':1}
    canvas=Image.new('RGBA',(128,128));meta={}
    hip=(65,86)
    # Lower body uses actual design pixels, moving each intact leg, not generated substitutes.
    if legs.startswith('run'):
        k=int(legs[-1]);phase=k*math.pi/4
        front=math.cos(phase);raise_l=round(max(0,-math.sin(phase))*2);raise_r=round(max(0,math.sin(phase))*2)
        lx=round(front*4);rx=-lx
        # Two intact legs physically exchange fore/aft positions each half-cycle.
        order=['right','left'] if front>=0 else ['left','right']
        legposes={'left':((shift[0]+lx,shift[1]-dy-raise_l),round(-front*12)), 'right':((shift[0]+rx,shift[1]-dy-raise_r),round(front*12))}
    elif legs=='lunge':
        order=['left','right'];legposes={'left':((shift[0]-3,0),18),'right':((shift[0]+4,-1),-25)}
    elif legs in ('crouch','kneel'):
        order=['left','right'];amount=18 if legs=='crouch' else 35
        legposes={'left':((shift[0]-1,0),amount),'right':((shift[0]+2,0),-amount)}
    else:
        order=['left','right'];legposes={'left':(shift,0),'right':(shift,0)}
    for n in order:
        if legs=='kneel':
            source=np.array(parts[n]);upper=source.copy();lower=source.copy()
            upper[94:]=0;lower[:94]=0
            root=(60,86) if n=='left' else(69,86)
            knee=(60,93) if n=='left' else(74,94)
            thigh_angle=50 if n=='left' else35
            k=rotpoint(knee,root,thigh_angle)
            k=(k[0]+shift[0],99)
            before=rotpoint(knee,root,thigh_angle)
            thighshift=(shift[0],99-before[1])
            layer(canvas,warp(Image.fromarray(upper),root,thigh_angle,thighshift))
            layer(canvas,warp(Image.fromarray(lower),knee,90 if n=='left' else-90,(k[0]-knee[0],k[1]-knee[1])))
            continue
        ls,la=legposes[n];im=warp(parts[n],(61,86) if n=='left' else(69,86),la,ls)
        # Grounded legs land on row99; jump and passing feet remain above ground.
        bbox=im.getbbox()
        if bbox and legs not in('jump','stand'):
            arr=np.array(im);target=99
            if legs.startswith('run'):target=99-(raise_l if n=='left' else raise_r)
            im=warp(im,(0,0),0,(0,target-(bbox[3]-1)))
        layer(canvas,im)
    tail_angle=round(math.sin(i*math.pi/4)*8) if tag=='run' else lean
    layer(canvas,warp(parts['tail'],hip,tail_angle,shift))
    layer(canvas,warp(parts['torso'],hip,lean,shift))
    layer(canvas,warp(parts['pelvis'],hip,lean,shift))
    shoulder=rotpoint((58,77),hip,lean)
    shoulder=(shoulder[0]+shift[0],shoulder[1]+shift[1])
    # Arm source thickness preserved by a rigid, unscaled transform.
    near_shift=(shoulder[0]-58,shoulder[1]-77)
    near=warp(parts['near'],(58,77),arm+lean,near_shift)
    grip=rotpoint((53,69),(58,77),arm+lean);grip=(grip[0]+near_shift[0],grip[1]+near_shift[1])
    # Unfold the raised arm for the overhead leap using existing armored forearm
    # pixels, with no scaling or thin geometric replacement.
    if tag=='ult' and i==3:
        grip=(shoulder[0]-4,57+shift[1]-2)
        near=Image.new('RGBA',(128,128));patch=parts['near'].crop((49,71,57,79))
        for top in range(round(grip[1]),round(shoulder[1])-4,5):near.alpha_composite(patch,(round(grip[0])-3,top))
    farangle=round(math.sin(i*math.pi/4)*16) if tag=='run' else (-35 if legs in('lunge','kneel') else lean)
    two_handed=(tag=='attack' and i in(1,2,3,4)) or(tag=='skill2' and i in(2,3)) or(tag=='ult' and i in(3,4,5,6))
    if two_handed:
        farshoulder=rotpoint((75,77),hip,lean);farshoulder=(farshoulder[0]+shift[0],farshoulder[1]+shift[1])
        farangle=math.degrees(math.atan2(grip[1]-farshoulder[1],grip[0]-farshoulder[0])-math.atan2(10,3))
        layer(canvas,warp(parts['far'],(75,77),farangle,(farshoulder[0]-75,farshoulder[1]-77)))
    else:layer(canvas,warp(parts['far'],(75,77),farangle,shift))
    sword_angle=blade+26
    sword=warp(parts['weapon'],(53,69),sword_angle,(grip[0]-53,grip[1]-69))
    tip=rotpoint((93,50),(53,69),sword_angle);tip=(tip[0]+grip[0]-53,tip[1]+grip[1]-69)
    # Ground stabbing keeps the intact weapon assembly and only conceals the part
    # that penetrates the ground, as requested by the action specification.
    if blade in(90,65) and tag in('ult','possess','dead'):
        meta['unclipped_sword_tip']=list(tip);tip=(tip[0],99)
    elif sword.getbbox() and sword.getbbox()[3]>100:
        correction=100-sword.getbbox()[3]
        sword=warp(sword,(0,0),0,(0,correction));grip=(grip[0],grip[1]+correction);tip=(tip[0],tip[1]+correction)
        near=warp(near,(0,0),0,(0,correction))
    layer(canvas,near)
    # Head is never rotated, scaled, re-colored, or regenerated.
    hc=rotpoint((67,73),hip,lean)
    hshift=(round(hc[0]+shift[0]-67),round(hc[1]+shift[1]-73))
    if tag=='run':hshift=(pivot[0]-64,dy)
    if tag=='hit':hshift=(pivot[0]-64+dx,0)
    layer(canvas,warp(H,(0,0),0,hshift))
    layer(canvas,sword)
    # Sword must not occlude the protected head; redraw exact head at the front.
    layer(canvas,warp(H,(0,0),0,hshift))
    arr=np.array(canvas);arr[100:]=0
    # All alpha binary; all colors are original source pixels.
    arr[arr[:,:,3]==0]=0;arr[:,:,3]=np.where(arr[:,:,3]>0,255,0)
    canvas=Image.fromarray(arr)
    # Remove detached diagnostic edge specks while protecting every head pixel.
    protected=np.array(warp(H,(0,0),0,hshift))[:,:,3]>0
    alive=arr[:,:,3]>0;seen=np.zeros_like(alive)
    for yy,xx in zip(*np.where(alive)):
        if seen[yy,xx]:continue
        stack=[(int(yy),int(xx))];seen[yy,xx]=1;component=[]
        while stack:
            cy,cx=stack.pop();component.append((cy,cx))
            for ny in range(max(0,cy-1),min(128,cy+2)):
                for nx in range(max(0,cx-1),min(128,cx+2)):
                    if alive[ny,nx] and not seen[ny,nx]:seen[ny,nx]=1;stack.append((ny,nx))
        if len(component)<3 and not any(protected[p] for p in component):
            for p in component:arr[p]=0
    canvas=Image.fromarray(arr)
    meta.update({'head_translation':list(hshift),'gripping_hand':list(map(lambda v:round(v,2),grip)),'sword_tip':list(map(lambda v:round(v,2),tip)),'torso_lean_degrees':lean,'leg_pose':legs,'source':'approved_design_rigid_parts','grid_scale':1})
    return canvas,meta

manifest={'schema_version':1,'scale':8,'cell_1x':[128,128],'sole_row':99,'source_design_sha256':hashlib.sha256((B/'design/viego_design_1x.png').read_bytes()).hexdigest(),'animations':{}}
for tag,framespec in C['tags'].items():
    cols,rows=layout[tag];sheet=Image.new('RGBA',(cols*128,rows*128));frames=[];entries=[]
    for i,s in enumerate(framespec):
        if tag=='idle':
            original=Image.open(B/'viego_idle.png').convert('RGBA')
            im=original.crop(((i%cols)*1024,(i//cols)*1024,(i%cols+1)*1024,(i//cols+1)*1024)).resize((128,128),Image.Resampling.NEAREST)
            meta={'source':'supplied_idle_unchanged'}
        else:im,meta=make(tag,i,s['pivot'])
        sheet.alpha_composite(im,((i%cols)*128,(i//cols)*128));frames.append(im)
        box=im.getbbox();entries.append({'frame':i+1,'rect_1x':[(i%cols)*128,(i//cols)*128,128,128],'rect_8x':[(i%cols)*1024,(i//cols)*1024,1024,1024],'pivot':s['pivot'],'ms':s['ms'],'bbox':list(box) if box else None,'impact':tag in impact and impact[tag][0]==i+1,**meta})
    sheet.save(O/'1x'/f'viego_{tag}_1x.png')
    if tag=='idle':shutil.copy2(B/'viego_idle.png',O/'viego_idle.png')
    else:sheet.resize((cols*1024,rows*1024),Image.Resampling.NEAREST).save(O/f'viego_{tag}.png')
    previews=[]
    for f,s in zip(frames,framespec):
        normalized=warp(f,(0,0),0,(64-s['pivot'][0],88-s['pivot'][1]))
        bg=Image.new('RGBA',(128,128),(205,205,205,255));bg.alpha_composite(normalized);previews.append(bg.crop((15,15,120,102)).resize((420,348),Image.Resampling.NEAREST).convert('RGB'))
    previews[0].save(O/'preview'/f'viego_{tag}.gif',save_all=True,append_images=previews[1:],duration=[s['ms'] for s in framespec],loop=0,disposal=2)
    manifest['animations'][tag]={'file':f'viego_{tag}.png','size':[cols*1024,rows*1024],'layout':[cols,rows],'impact_frame':impact.get(tag,(None,None))[0],'impact_tick':impact.get(tag,(None,None))[1],'frames':entries}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
shutil.copy2(B/'viego_cells.json',O/'viego_cells.json')
shutil.copy2(B/'design/viego_design_1x.png',O/'source/viego_design_1x.png')
shutil.copy2(B/'design/viego_head_1x.png',O/'source/viego_head_1x.png')
# Contact sheets show every frame at 4x, with numbered labels outside the art.
for tag,info in manifest['animations'].items():
    cols,rows=info['layout'];sheet=Image.open(O/'1x'/f'viego_{tag}_1x.png')
    contact=Image.new('RGB',(cols*440,rows*375),(215,215,215));draw=ImageDraw.Draw(contact)
    for i,entry in enumerate(info['frames']):
        c,r=i%cols,i//cols;frame=sheet.crop((c*128,r*128,(c+1)*128,(r+1)*128)).crop((15,15,120,102))
        bg=Image.new('RGBA',frame.size,(215,215,215,255));bg.alpha_composite(frame)
        contact.paste(bg.resize((420,348),Image.Resampling.NEAREST).convert('RGB'),(c*440+10,r*375+20))
        draw.text((c*440+10,r*375+4),f'{tag} {i+1} | {entry["ms"]}ms'+(' IMPACT' if entry['impact'] else''),fill=(20,20,20))
    contact.save(O/'preview'/f'viego_{tag}_contact.png')
print('Built',sum(len(t['frames']) for t in manifest['animations'].values()),'frames including provided idle.')

