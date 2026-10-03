from pathlib import Path
from PIL import Image, ImageDraw
import math,json,shutil
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'work/aatrox-strips/aatrox_strips_pack';OUT=ROOT/'outputs/aatrox-strips'
for p in [OUT,OUT/'logical',OUT/'previews',OUT/'frames']:p.mkdir(exist_ok=True)
cells=json.loads((REF/'aatrox_cells.json').read_text(encoding='utf8'))
src=Image.open(REF/'design/aatrox_design_1x.png').convert('RGBA')
head=Image.open(REF/'design/aatrox_head_1x.png').convert('RGBA')
sword=Image.open(REF/'design/aatrox_sword_1x.png').convert('RGBA')
palette=set(src.getdata())-{(0,0,0,0)}
def c(h):return tuple(bytes.fromhex(h))+(255,)
INK=c('0A0408')
def blank(size=(128,128)):return Image.new('RGBA',size)
def maskpart(test):
    im=blank()
    for y in range(128):
        for x in range(128):
            if src.getpixel((x,y))[3] and test(x,y):im.putpixel((x,y),src.getpixel((x,y)))
    return im
def leg_test(x,y):return y>=88 and x>=(57 if y<95 else 54) and not sword.getpixel((x,y))[3]
legs=maskpart(leg_test)
wings=maskpart(lambda x,y:y<84 and (x<=55 or x>=69) and not head.getpixel((x,y))[3])
body=maskpart(lambda x,y:y<88 and not head.getpixel((x,y))[3] and not sword.getpixel((x,y))[3] and not wings.getpixel((x,y))[3] and not(y>=77 and (x<=61 or x>=66)))
fullupper=maskpart(lambda x,y:y<88 and not sword.getpixel((x,y))[3])
nearleg=blank();farleg=blank()
for y in range(88,100):
    for x in range(128):
        if legs.getpixel((x,y))[3]:(nearleg if x<64 else farleg).putpixel((x,y),legs.getpixel((x,y)))

def shift(im,dx=0,dy=0,size=(128,128)):
    dest=blank(size);dest.alpha_composite(im,(int(dx),int(dy)));return dest
def compose(dst,im,dx=0,dy=0):dst.alpha_composite(im,(int(dx),int(dy)))
def clean_black_islands(im,protected=None):
    points={(x,y) for y in range(128) for x in range(128) if im.getpixel((x,y))[3]};removed=0
    while points:
        seed=points.pop();group={seed};todo=[seed]
        while todo:
            x,y=todo.pop()
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    q=(x+dx,y+dy)
                    if q in points:points.remove(q);group.add(q);todo.append(q)
        if all(im.getpixel(q)==INK for q in group) and not(protected and any(protected.getpixel(q)[3] for q in group)):
            for q in group:im.putpixel(q,(0,0,0,0));removed+=1
    return removed
def rotate(im,anchor,angle,target=None):
    # Inverse nearest-neighbor rigid transform on the native grid.
    ax,ay=anchor;tx,ty=target or anchor;rad=math.radians(angle);co=math.cos(rad);si=math.sin(rad)
    out=blank();bbox=im.getbbox()
    if not bbox:return out
    corners=[(x,y) for x in (bbox[0]-1,bbox[2]+1) for y in (bbox[1]-1,bbox[3]+1)]
    pts=[(tx+co*(x-ax)-si*(y-ay),ty+si*(x-ax)+co*(y-ay)) for x,y in corners]
    for y in range(max(0,math.floor(min(p[1] for p in pts))),min(128,math.ceil(max(p[1] for p in pts))+1)):
        for x in range(max(0,math.floor(min(p[0] for p in pts))),min(128,math.ceil(max(p[0] for p in pts))+1)):
            sx=round(ax+co*(x-tx)+si*(y-ty));sy=round(ay-si*(x-tx)+co*(y-ty))
            if 0<=sx<128 and 0<=sy<128:out.putpixel((x,y),im.getpixel((sx,sy)))
    return out
BASE=math.degrees(math.atan2(8,-20))
def blade(wrist,angle):
    delta=angle-BASE;im=rotate(sword,(58,86),delta,wrist)
    r=math.radians(delta);vx,vy=-21,9
    unit=(math.cos(math.radians(angle)),math.sin(math.radians(angle)))
    tip=max([(x,y) for y in range(128) for x in range(128) if im.getpixel((x,y))[3]],key=lambda q:(q[0]-wrist[0])*unit[0]+(q[1]-wrist[1])*unit[1])
    return im,tip
def arm(dst,shoulder,elbow,wrist,red=False,claw=False):
    d=ImageDraw.Draw(dst);path=[shoulder,elbow,wrist]
    d.line(path,fill=INK,width=5,joint='curve')
    d.line(path,fill=c('8F0E2B' if red else '3B586B'),width=3,joint='curve')
    d.line([(x,y-1) for x,y in path],fill=c('BF1630' if red else '5B8498'),width=1)
    x,y=wrist;d.rectangle((x-2,y-1,x+1,y+2),fill=INK)
    d.rectangle((x-1,y,x,y+1),fill=c('BF1630' if red else '3B586B'))
    if claw:
        for yy in (-2,0,2):d.line([(x,y+yy),(x+3,y+yy)],fill=c('BF1630'),width=1)
    return (wrist[0]+3,wrist[1]) if claw else wrist
def opened_wings(stage):
    im=blank();d=ImageDraw.Draw(im);reach=round(10+stage*27)
    for side in (-1,1):
        a=(64+side*4,74);b=(64+side*reach,47);cc=(64+side*(reach-3),73);dd=(64+side*(reach//2),65);e=(64+side*(reach//2),80)
        d.polygon([a,b,cc,dd,e],fill=INK)
        d.polygon([(a[0]+side,a[1]-2),(b[0]-side*2,b[1]+3),(cc[0]-side*2,cc[1]-3),(dd[0],dd[1]-1),(e[0]-side,e[1]-3)],fill=c('42224C'))
        d.line([a,b],fill=c('3B586B'),width=2);d.line([(a[0],a[1]-1),(b[0],b[1]-1)],fill=c('5B8498'),width=1)
        d.line([b,cc],fill=c('8F0E2B'),width=1);d.line([a,dd],fill=c('270D28'),width=1)
    return im

plans={
'attack':[(BASE,(58,86),0,0),(175,(57,84),-1,0),(45,(68,78),0,1),(0,(72,84),2,1),(12,(72,85),1,0),(BASE,(58,86),0,0)],
'attack_p':[(-125,(59,79),0,0),(177,(56,86),-2,0),(165,(55,85),-2,0),(0,(75,84),2,1),(0,(75,84),2,1),(BASE,(58,86),0,0)],
'skill':[(BASE,(58,86),0,0),(-130,(53,70),-1,0),(-100,(53,62),0,0),(0,(68,74),1,1),(65,(67,78),2,1),(65,(67,78),1,1),(BASE,(58,86),0,0)],
'q2':[(BASE,(58,86),0,0),(-150,(53,72),-1,0),(-115,(53,64),-1,0),(-30,(69,78),1,0),(0,(75,84),2,1),(12,(75,84),1,1),(BASE,(58,86),0,0)],
'q3':[(-130,(54,73),0,1),(-110,(53,62),0,-2),(-100,(53,60),0,-3),(-15,(67,70),1,-1),(65,(67,78),2,1),(65,(67,78),1,1),(BASE,(58,86),0,0)]}
HIT={'attack':3,'attack_p':3,'skill':4,'q2':4,'q3':4,'skill2':3}
manifest={'cell_logical':[112,96],'scale':8,'coordinate_system':'Top-left origin. Frame points local unless sheet suffix. Pivot from supplied cells; soles logical row81 inclusive.','animations':{}}
records={};frames_by_tag={};warnings=[]

for tag,entries in cells['tags'].items():
    if tag=='idle':continue
    frames=[];meta=[]
    for i,entry in enumerate(entries):
        px,py=entry['pivot'];dx=px-64;dy=py-88;pose=blank();tip=None;hand=None;head_move=(0,0);angle=BASE;wrist=(58,86);lift=0
        if tag=='run':
            step=[-18,-6,10,18,18,6,-10,-18][i];bob=[0,1,1,0,0,1,1,0][i]
            for part,sign,hip in [(farleg,-1,(68,88)),(nearleg,1,(60,88))]:
                leg=rotate(part,hip,sign*step)
                b=leg.getbbox();leg=shift(leg,0,99-b[3]+1-([2,1,0,0,0,1,2,0][i] if sign==1 else [0,0,2,1,2,0,0,1][i]))
                compose(pose,leg)
            compose(pose,wings,0,bob);compose(pose,body,0,bob);head_move=(0,bob)
            wrist=(58,86+bob);angle=BASE+[0,2,0,-2,0,2,0,-2][i]
            arm(pose,(57,77+bob),(55,82+bob),wrist)
            arm(pose,(68,77+bob),(72,81+bob),(70-round(step/6),85+bob),True)
        elif tag=='dead':
            # Stagger, kneel, slump, then a held fallen pose. No frame flips the back.
            turn=[0,8,20,35,50,60,70,70][i];down=[0,1,4,7,9,11,14,14][i]
            if i<2:
                character=maskpart(lambda x,y:not sword.getpixel((x,y))[3])
                fallen=rotate(character,(64,88),turn,(64,88+down))
            else:
                fallen=blank()
                for part,hip,spin,target in [(farleg,(68,88),75,(70,95)),(nearleg,(60,88),-75,(64,95))]:
                    folded=rotate(part,hip,spin,target);lb=folded.getbbox()
                    if lb[3]>100:folded=shift(folded,0,100-lb[3])
                    compose(fallen,folded)
                compose(fallen,rotate(fullupper,(64,88),turn,(64,88+down)))
            bb=fallen.getbbox();fallen=shift(fallen,0,max(0,99-bb[3]+1) if i>=2 else min(0,100-bb[3]))
            bb=fallen.getbbox()
            if bb[3]>100:fallen=shift(fallen,0,100-bb[3])
            compose(pose,fallen)
            if i==0:wrist=(58,86);angle=BASE
            else:wrist=(73,97);angle=180
            s,tip=blade(wrist,angle);bb=s.getbbox()
            if bb[3]>100:s=shift(s,0,100-bb[3]);tip=(tip[0],tip[1]+100-bb[3])
            compose(pose,s)
        else:
            if tag in plans:angle,wrist,bdx,bdy=plans[tag][i]
            elif tag=='skill2':bdx=0;bdy=0
            elif tag=='ult':bdx=0;bdy=[1,0,0,0,0,0][i]
            else:bdx=[-2,0][i];bdy=0
            if tag=='q3':lift=[0,2,3,1,0,0,0][i]
            compose(pose,legs,0,-lift)
            if tag=='ult' and i in (2,3,4):compose(pose,opened_wings([0,0,.6,1,1,0][i]))
            else:compose(pose,wings,bdx,bdy)
            compose(pose,body,bdx,bdy);head_move=(bdx,bdy)
            ns=(57+bdx,77+bdy);fs=(68+bdx,77+bdy)
            if tag=='skill2':
                wrist=(58,86);angle=BASE
                throws=[((68,80),(65,85)),((72,74),(68,71)),((73,73),(70,70)),((75,76),(82,76)),((75,76),(82,76)),((68,80),(65,85))]
                elbow,fw=throws[i];hand=arm(pose,fs,elbow,fw,True,i in (1,2,3,4))
            elif tag=='ult':
                if i in (2,3,4):wrist=(48,80);angle=150;hand=arm(pose,fs,(73,78),(79,77),True,True)
                else:wrist=(58,86);angle=BASE;arm(pose,fs,(69,82),(65,85),True)
            elif tag=='hit':
                wrist=(58+bdx,86);arm(pose,fs,(69+bdx,82),(65+bdx,85),True)
            else:
                fw=(wrist[0]+2,wrist[1]+1);arm(pose,fs,(round((fs[0]+fw[0])/2),round((fs[1]+fw[1])/2)+1),fw,True)
            elbow=(round((ns[0]+wrist[0])/2)-2,round((ns[1]+wrist[1])/2)+2)
            arm(pose,ns,elbow,wrist)
        if tag!='dead':
            compose(pose,head,*head_move)
            s,tip=blade(wrist,angle);bb=s.getbbox()
            if bb[3]>100:
                # Reposition entire blade and wrist, never clip or bend the sword.
                delta=100-bb[3];s=shift(s,0,delta);tip=(tip[0],tip[1]+delta);warnings.append({'tag':tag,'frame':i+1,'blade_vertical_adjust':delta})
            compose(pose,s)
        # Exact design stance at each non-death recovery endpoint.
        if tag not in ('run','dead','hit') and (i==len(entries)-1 or (i==0 and tag in ('attack','skill','q2','skill2'))):
            pose=src.copy();tip=(37,95);head_move=(0,0)
        else:
            protected=shift(head,*head_move) if tag!='dead' else None
            if tag not in ('run','dead'):compose(protected,legs,0,-lift)
            removed=clean_black_islands(pose,protected)
            if removed:warnings.append({'tag':tag,'frame':i+1,'isolated_black_pixels_removed':removed})
        cell=shift(pose,dx,dy,(112,96));bb=cell.getbbox()
        assert bb and bb[3]<=82,(tag,i,bb)
        assert set(cell.getdata())-{(0,0,0,0)}<=palette
        assert set(cell.getchannel('A').getdata())=={0,255}
        # Head stays exact and front-facing for all non-death frames.
        if tag!='dead':
            for hy in range(61,73):
                for hx in range(57,68):
                    hc=head.getpixel((hx,hy))
                    if hc[3]:assert cell.getpixel((hx+dx+head_move[0],hy+dy+head_move[1]))==hc,(tag,i,'head')
        if tag not in ('run','dead'):
            # A posed blade may cover a shin; leg layer itself is never altered.
            assert legs.tobytes()==maskpart(leg_test).tobytes()
        frames.append(cell)
        meta.append({'frame':i+1,'duration_ms':entry['ms'],'pivot_logical':entry['pivot'],'pivot_px':[px*8,py*8],'bbox_logical':list(bb),'bbox_px':[v*8 for v in bb],'head_offset':list(head_move),'sword_angle_degrees':angle,'sword_tip_logical':[tip[0]+dx,tip[1]+dy] if tip else None,'cast_hand_logical':[hand[0]+dx,hand[1]+dy] if hand else None,'hit_frame':i==HIT.get(tag,-1),'lift':lift})
    cols=2 if tag=='hit' else 3 if len(entries)==6 else 4;rows=math.ceil(len(entries)/cols)
    sheet=blank((112*cols,96*rows))
    for i,cell in enumerate(frames):
        x=(i%cols)*112;y=(i//cols)*96;compose(sheet,cell,x,y)
        meta[i]['cell_rect_px']=[x*8,y*8,112*8,96*8];meta[i]['cell_rect_logical']=[x,y,112,96]
        meta[i]['pivot_sheet_px']=[(x+entries[i]['pivot'][0])*8,(y+70)*8]
    big=sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST)
    expected=Image.open(REF/f'now/aatrox_now_{tag}.png').size;assert big.size==expected,(tag,big.size,expected)
    big.save(OUT/f'aatrox_{tag}.png');sheet.save(OUT/'logical'/f'aatrox_{tag}_1x.png')
    # Preview frames stay aligned to their pivots; durations use the original table.
    gif=[]
    for cell,entry in zip(frames,entries):
        tile=Image.new('RGB',(112,96),'#222536');tile.paste(cell,(56-entry['pivot'][0],70-entry['pivot'][1]),cell)
        gif.append(tile.resize((448,384),Image.Resampling.NEAREST))
    gif[0].save(OUT/'previews'/f'aatrox_{tag}.gif',save_all=True,append_images=gif[1:],duration=[e['ms'] for e in entries],loop=0,disposal=2)
    contact=Image.new('RGB',(len(frames)*112,96),'#222536')
    for i,cell in enumerate(frames):contact.paste(cell,(i*112,0),cell)
    contact.resize((len(frames)*224,192),Image.Resampling.NEAREST).save(OUT/'previews'/f'{tag}_contact.png')
    manifest['animations'][tag]={'size_px':list(big.size),'layout':[cols,rows],'frame_count':len(frames),'hit_frame':HIT.get(tag,-1)+1 if tag in HIT else None,'frames':meta}
    records[tag]={'mode':'authorized_native_pixel_animation','pose_plan':plans.get(tag,tag),'prompt':'Preserve supplied final design, exact head and standing legs; rigidly move/turn supplied straight sword; animate '+tag+' according to MODEL_STRIPS.md. No image generator was used for final frames.'}
    frames_by_tag[tag]=frames
shutil.copy2(REF/'aatrox_idle.png',OUT/'aatrox_idle.png');shutil.copy2(REF/'aatrox_cells.json',OUT/'aatrox_cells.json')
idle_image=Image.open(REF/'aatrox_idle.png').convert('RGBA');idle_logical=idle_image.resize((336,192),Image.Resampling.NEAREST)
idle_frames=[]
for i,e in enumerate(cells['tags']['idle']):
    x=(i%3)*112;y=(i//3)*96;ic=idle_logical.crop((x,y,x+112,y+96));bb=ic.getbbox();idle_frames.append({'frame':i+1,'pivot_logical':e['pivot'],'pivot_px':[v*8 for v in e['pivot']],'duration_ms':e['ms'],'cell_rect_px':[x*8,y*8,896,768],'cell_rect_logical':[x,y,112,96],'bbox_logical':list(bb),'bbox_px':[v*8 for v in bb],'sword_tip_logical':[32,77],'hit_frame':False})
manifest['animations']['idle']={'source':'unchanged supplied aatrox_idle.png','frame_count':6,'duration_ms':200,'layout':[3,2],'size_px':[2688,1536],'frames':idle_frames}
manifest['adjustments']=warnings
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'generation_prompts.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'animations':len(frames_by_tag),'new_frames':sum(map(len,frames_by_tag.values())),'adjustments':warnings},ensure_ascii=False))
