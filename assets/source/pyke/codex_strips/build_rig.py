from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math,json,hashlib,shutil
import numpy as np

ROOT=Path(__file__).resolve().parent/'source'
OUT=Path(__file__).resolve().parent
CELL=(128,96)
SCALE=8
cells=json.loads((ROOT/'pyke_cells.json').read_text())
design=Image.open(ROOT/'design/pyke_design_1x.png').convert('RGBA')
head=Image.open(ROOT/'design/pyke_head_1x.png').convert('RGBA')
palette=sorted({tuple(p[:3]) for p in np.array(design).reshape(-1,4) if p[3]})

def maskpart(poly):
    m=Image.new('L',(128,128));ImageDraw.Draw(m).polygon(poly,fill=255)
    a=np.array(design);a[np.array(m)==0]=0
    return Image.fromarray(a)

yy,xx=np.indices((128,128))
wm=((yy<55)&(xx<69))|((yy>=55)&(yy<=58)&(xx<=57))|((yy>=59)&(yy<=60)&(xx<=51))|((yy>=61)&(yy<=64)&(xx<=46))|((yy>=65)&(yy<=76)&(xx<=43))
wa=np.array(design);wa[~wm]=0;weapon=Image.fromarray(wa)
rear=maskpart([(43,60),(47,60),(50,62),(54,62),(56,64),(56,68),(53,69),(49,67),(45,65),(43,64)])
front=maskpart([(83,81),(86,81),(88,84),(90,86),(90,89),(94,91),(94,95),(89,96),(88,91),(86,89),(85,87),(83,85),(81,83)])
claw=maskpart([(88,90),(91,89),(94,91),(94,95),(90,96),(88,93)])
leftleg=maskpart([(49,84),(54,81),(61,82),(65,85),(65,89),(59,93),(59,100),(49,100)])
rightleg=maskpart([(65,88),(71,87),(77,90),(81,94),(81,100),(62,100),(62,94)])

def remove_parts(base,parts):
    a=np.array(base)
    for p in parts:a[np.array(p)[:,:,3]>0]=0
    return Image.fromarray(a)

core=remove_parts(design,[weapon,rear,front,head])
run_core=remove_parts(core,[leftleg,rightleg])
for name,im in [('weapon',weapon),('rear_arm',rear),('front_arm',front),('core',core),('left_leg',leftleg),('right_leg',rightleg),('head',head)]:
    (OUT/'parts').mkdir(exist_ok=True);im.save(OUT/'parts'/f'{name}_1x.png')

def point_rotate(pt,pivot,angle):
    t=math.radians(angle);x,y=pt[0]-pivot[0],pt[1]-pivot[1]
    return (round(pivot[0]+math.cos(t)*x+math.sin(t)*y),round(pivot[1]-math.sin(t)*x+math.cos(t)*y))

def layer(part,pivot,target,angle=0):
    # Copy original pixel art into an anchored padded canvas, then rotate as one rigid piece.
    pad=Image.new('RGBA',(192,192));pad.alpha_composite(part,(96-pivot[0],96-pivot[1]))
    if angle:pad=pad.rotate(angle,resample=Image.Resampling.NEAREST,center=(96,96))
    im=Image.new('RGBA',(128,128));im.alpha_composite(pad,(target[0]-96,target[1]-96))
    return im

def translate(part,dx,dy):
    im=Image.new('RGBA',(128,128));im.alpha_composite(part,(dx,dy));return im

def clean_black_fragments(im):
    a=np.array(im);pending=set(zip(*np.where(a[:,:,3]>0)))
    while pending:
        q=pending.pop();todo=[q];points=[q]
        while todo:
            y,x=todo.pop()
            for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
                n=(y+dy,x+dx)
                if n in pending:pending.remove(n);todo.append(n);points.append(n)
        if len(points)<=3 and all(tuple(a[y,x,:3])==(5,3,3) for y,x in points):
            for y,x in points:a[y,x]=0
    return Image.fromarray(a)

def darken(part):
    a=np.array(part)
    # Use only pre-existing shades from the approved palette.
    mapping={(92,85,67):(58,52,46),(222,161,126):(119,59,35),(119,59,35):(79,35,19),(239,157,36):(151,77,25),(249,182,50):(205,119,32)}
    for c,d in mapping.items():
        if d in palette:a[np.all(a[:,:,:3]==c,axis=2)&(a[:,:,3]>0),:3]=d
    return Image.fromarray(a)

def actor(rear_angle=0,weapon_angle=0,front_angle=0,with_weapon=True,bob=0,run_index=None,jump=0,dive=False,front_grip=False):
    body=run_core.copy() if run_index is not None else core.copy()
    if run_index is not None:
        # Whole leg pieces cross under the hips; no scanline warping and no invented bodies.
        la=[-45,0,45,0,45,0,-45,0][run_index]
        ra=[45,0,-45,0,-45,0,45,0][run_index]
        lt=[(62,83),(61,83),(62,83),(62,83),(65,83),(64,83),(63,83),(62,83)][run_index]
        rt=[(66,89),(65,89),(63,89),(65,89),(61,89),(63,89),(65,89),(65,89)][run_index]
        far=layer(darken(rightleg),(69,89),rt,ra)
        near=layer(leftleg,(59,83),lt,la)
        # Keep feet within the original foot-bottom without shrinking leg art.
        for im in [far,near]:
            bb=im.getbbox()
            if bb and bb[3]>100:im2=translate(im,0,100-bb[3]);im.paste(im2)
        body.alpha_composite(far);body.alpha_composite(near)
    shoulder=(55,65)
    rear_layer=layer(rear,shoulder,shoulder,rear_angle)
    hand=point_rotate((44,62),shoulder,rear_angle)
    if front_grip:hand=point_rotate((91,91),(83,82),front_angle)
    weapon_layer=layer(weapon,(44,62),hand,weapon_angle) if with_weapon else Image.new('RGBA',(128,128))
    body.alpha_composite(rear_layer)
    body.alpha_composite(weapon_layer)
    body.alpha_composite(layer(front,(83,82),(83,82),front_angle))
    if not with_weapon:body.alpha_composite(layer(claw,(90,91),hand,90))
    # Head is pasted last, verbatim. The source core was cleared using the exact head alpha mask.
    body.alpha_composite(head)
    tip=point_rotate((66,48),(44,62),weapon_angle)
    tip=(tip[0]+hand[0]-44,tip[1]+hand[1]-62) if with_weapon else None
    if dive:
        # The complete costume rotates forward; the head remains upright at its transformed attachment.
        body=remove_parts(body,[head])
        body=layer(body,(64,88),(64,88),-45)
        hp=point_rotate((74,65),(64,88),-45)
        body.alpha_composite(translate(head,hp[0]-74,hp[1]-65))
        hand=point_rotate(hand,(64,88),-45)
        tip=point_rotate(tip,(64,88),-45) if tip else None
    dy=bob-jump
    if dy:
        body=translate(body,0,dy);hand=(hand[0],hand[1]+dy);tip=(tip[0],tip[1]+dy) if tip else None
    return body,hand,tip,(0,dy)

CONFIG={
 'attack':[(0,0,0,0),(-45,45,0,-1),(-90,0,45,0),(180,-45,45,3),(135,-90,0,2),(0,0,0,0)],
 'skill_stab':[(45,-45,45,0),(45,-45,45,-1),(135,-45,45,1),(180,-45,45,3),(0,0,0,0)],
 'skill':[(0,0,45,0),(-45,45,45,-1),(-45,45,45,-1),(-45,45,45,0),(180,-45,45,2),(135,0,0,0)],
 'hit':[(45,45,-45,-2),(0,0,0,0)],
 'ult':[(0,0,45,0),(-90,-135,90,0),(-90,-135,90,0),(180,-135,90,2),(180,-135,90,2),(0,0,0,0)],
 'skill2':[(0,0,0,0),(0,0,45,1),(0,0,45,2),(0,0,0,0)]
}
GRIDS={'idle':(3,2),'run':(4,2),'attack':(3,2),'skill_stab':(3,2),'skill':(3,2),'skill2':(4,1),'ult':(3,2),'hit':(2,1),'dead':(4,2)}
RELEASE={'attack':(4,12),'skill_stab':(4,13),'skill':(5,36),'ult':(4,18)}
manifest={'schema':1,'unit':'1x pixel cells','scale':8,'cell':[128,96],'feet_row':81,'source_design_sha256':hashlib.sha256((ROOT/'design/pyke_design_1x.png').read_bytes()).hexdigest(),'route':'imagegen motion studies + approved-pixel rigid-part repair','tags':{}}
all_frames={}
for tag,entries in cells['tags'].items():
    nc,nr=GRIDS[tag];sheet=Image.new('RGBA',(nc*128,nr*96));frames=[];records=[]
    for i,entry in enumerate(entries):
        px,py=entry['pivot'];shift=0;rot=0;hshift=(0,0);tip=None;hand=None
        if tag=='idle':
            src=Image.open(ROOT/'pyke_idle.png').convert('RGBA')
            fr=src.crop(((i%nc)*1024,(i//nc)*768,(i%nc+1)*1024,(i//nc+1)*768)).resize(CELL,Image.Resampling.NEAREST)
            # The supplied file is already an exact 8x asset; this only reads the native cells.
            hand=(px-20,44);tip=(px+2,30);head_origin=(px+4,41)
        else:
            if tag=='run':
                body,hand,tip,hshift=actor(front_angle=[0,0,45,45,0,0,-45,-45][i],run_index=i,bob=-1 if i in [2,6] else 0)
            elif tag=='dead':
                body,hand,tip,hshift=actor(rear_angle=45 if i else 0,front_angle=-45 if i else 0)
                if i in [2,3]:
                    # The torso tips backwards as a rigid piece; retain the unrotated face until prone.
                    fall_angle=45 if i==2 else 90
                    body=remove_parts(body,[head]);body=layer(body,(64,88),(64,88),fall_angle)
                    hp=point_rotate((74,65),(64,88),fall_angle);body.alpha_composite(translate(head,hp[0]-74,hp[1]-65));hshift=(hp[0]-74,hp[1]-65)
                    hand=point_rotate(hand,(64,88),fall_angle);tip=point_rotate(tip,(64,88),fall_angle)
                elif i>=4:
                    body,hand,tip,_=actor(with_weapon=False)
                    body=layer(body,(64,88),(64,88),90);rot=90
                    body.alpha_composite(layer(weapon,(44,62),(72,96),-45))
                    hand=None;tip=(98,97)
                bb=body.getbbox()
                if bb and bb[3]>100:
                    fix=100-bb[3];body=translate(body,0,fix);hshift=(hshift[0],hshift[1]+fix)
                    if hand:hand=(hand[0],hand[1]+fix)
                    if tip:tip=(tip[0],tip[1]+fix)
            else:
                ra,wa,fa,shift=CONFIG[tag][i]
                jump=5 if tag=='ult' and i in [1,2] else 0
                body,hand,tip,hshift=actor(ra,wa,fa,with_weapon=not(tag=='skill' and i>=4),jump=jump,dive=tag=='skill2' and i in [1,2],front_grip=tag=='ult' and i in [3,4])
                if tag=='skill2' and i in [1,2]:
                    hp=point_rotate((74,65),(64,88),-45);hshift=(hp[0]-74,hp[1]-65)
                bb=body.getbbox()
                if bb and bb[3]>100:
                    fix=100-bb[3];body=translate(body,0,fix);hshift=(hshift[0],hshift[1]+fix)
                    hand=(hand[0],hand[1]+fix);tip=(tip[0],tip[1]+fix) if tip else None
            fr=Image.new('RGBA',CELL);dx=px-64+shift;dy=py-88
            fr.alpha_composite(body,(dx,dy))
            hand=(hand[0]+dx,hand[1]+dy) if hand else None
            tip=(tip[0]+dx,tip[1]+dy) if tip else None
            head_origin=(68+dx+hshift[0],59+dy+hshift[1]) if rot==0 else None
        fr=clean_black_fragments(fr)
        # Manifest landmarks refer to actual visible pixels, not rounding gaps after 45-degree rotation.
        opaque_y,opaque_x=np.where(np.array(fr)[:,:,3]>0)
        def snap(pt):
            if pt is None:return None
            distances=(opaque_x-pt[0])**2+(opaque_y-pt[1])**2
            j=int(distances.argmin());return (int(opaque_x[j]),int(opaque_y[j]))
        hand=snap(hand);tip=snap(tip)
        # Detect overflow; never silently cut the actor at the health-bar baseline.
        assert not np.array(fr)[82:,:,3].any(),(tag,i,'below feet line')
        fr.save(OUT/'frames'/f'{tag}_{i+1:02d}_1x.png')
        frames.append(fr);sheet.alpha_composite(fr,((i%nc)*128,(i//nc)*96))
        records.append({'frame':i+1,'ms':entry['ms'],'cell_rect':[(i%nc)*128,(i//nc)*96,128,96],'pivot':entry['pivot'],'bbox':list(fr.getbbox()) if fr.getbbox() else None,'hand':hand,'harpoon_tip':tip,'harpoon_held':not(tag=='skill' and i>=4) and not(tag=='dead' and i>=4),'head_origin':head_origin,'head_rotation':rot,'whole_body_shift_x':shift,'release':tag in RELEASE and i+1==RELEASE[tag][0]})
    all_frames[tag]=frames
    if tag!='idle':sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST).save(OUT/f'pyke_{tag}.png')
    sheet.save(OUT/f'pyke_{tag}_1x.png')
    info={'grid':[nc,nr],'image_size':[sheet.width*8,sheet.height*8],'frames':records}
    if tag in RELEASE:info['release_frame'],info['release_tick']=RELEASE[tag]
    manifest['tags'][tag]=info
    gifs=[]
    for fr in frames:
        bg=Image.new('RGBA',CELL,'#b9b9bd');bg.alpha_composite(fr);gifs.append(bg.convert('RGB').resize((512,384),Image.Resampling.NEAREST))
    gifs[0].save(OUT/'preview'/f'pyke_{tag}.gif',save_all=True,append_images=gifs[1:],duration=[e['ms'] for e in entries],loop=0,disposal=2)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
contact=Image.new('RGB',(2048,9*230),'#dddddf');d=ImageDraw.Draw(contact)
for row,(tag,frames) in enumerate(all_frames.items()):
    d.text((10,row*230+5),tag,fill='black',font=font)
    for i,fr in enumerate(frames):
        b=Image.new('RGBA',CELL,'#dddddf');b.alpha_composite(fr);contact.paste(b.resize((256,192),Image.Resampling.NEAREST).convert('RGB'),(i*256,row*230+30))
contact.save(OUT/'preview'/'all_actions.png')
print('Built',len(manifest['tags']),'actions',sum(len(v['frames']) for v in manifest['tags'].values()),'frames')
