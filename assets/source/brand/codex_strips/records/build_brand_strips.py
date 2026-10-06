from pathlib import Path
import json, math, shutil, hashlib
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'work/brand_strips_pack/brand_strips_pack'
OUT=ROOT/'outputs/brand-strips'
CELLS=json.loads((SRC/'brand_cells.json').read_text(encoding='utf-8'))
D=Image.open(SRC/'design/brand_design_1x.png').convert('RGBA')
H=Image.open(SRC/'design/brand_head_1x.png').convert('RGBA')
A=np.array(D)
PALETTE=set(tuple(p[:3]) for p in A.reshape(-1,4) if p[3])

def blank(size=(128,128)):return Image.new('RGBA',size)
def move(im,dx,dy):
    out=blank(im.size);out.paste(im,(int(round(dx)),int(round(dy))));return out
def mask_part(poly):
    m=Image.new('L',D.size);ImageDraw.Draw(m).polygon(poly,fill=255)
    a=A.copy();a[:,:,3]=np.minimum(a[:,:,3],np.array(m))
    # Clothing that visually overlaps the arm's bounding polygon belongs to BODY.
    for color in ['3A2A1F','513E2D','805B40','AA784B','B46117','CD7D2B']:
        rgb=[int(color[j:j+2],16) for j in (0,2,4)]
        a[(a[:,:,:3]==rgb).all(axis=2)]=0
    a[a[:,:,3]==0]=0
    return Image.fromarray(a)
LEFT=mask_part([(55,70),(59,71),(62,74),(60,78),(57,82),(55,88),(45,88),(46,82),(51,76)])
RIGHT=mask_part([(71,71),(75,72),(76,77),(78,81),(83,84),(84,90),(75,90),(71,83),(71,77)])
BODY=A.copy()
for p in [H,LEFT,RIGHT]:BODY[np.array(p)[:,:,3]>0]=0
BODY=Image.fromarray(BODY)
LEGS=blank();LEGS.paste(BODY.crop((0,86,128,128)),(0,86))
UPPER=np.array(BODY);UPPER[86:]=0;UPPER=Image.fromarray(UPPER)
LL=np.array(LEGS);LL[:,64:]=0;LL=Image.fromarray(LL)
RL=np.array(LEGS);RL[:,:64]=0;RL=Image.fromarray(RL)

def rot(im,deg,center):return im.rotate(deg,resample=Image.Resampling.NEAREST,center=center)
def composite(*parts):
    out=blank()
    for p in parts:out.alpha_composite(p)
    return out
def bbox(im):
    b=im.getchannel('A').getbbox();return list(b) if b else None
def point_rot(p,a,deg):
    x,y=p[0]-a[0],p[1]-a[1];c=math.cos(math.radians(deg));s=math.sin(math.radians(deg))
    return [a[0]+x*c+y*s,a[1]-x*s+y*c]

def clean_rotation_fragments(arr,protect=None):
    mask=arr[:,:,3]>0;seen=set();components=[]
    for y,x in zip(*np.where(mask)):
        if (y,x) in seen:continue
        stack=[(y,x)];seen.add((y,x));part=[]
        while stack:
            cy,cx=stack.pop();part.append((cy,cx))
            for dy in [-1,0,1]:
                for dx in [-1,0,1]:
                    p=(cy+dy,cx+dx)
                    if 0<=p[0]<96 and 0<=p[1]<128 and mask[p] and p not in seen:seen.add(p);stack.append(p)
        components.append(part)
    if len(components)<2:return arr,0
    components.sort(key=len,reverse=True);main=np.array(components[0]);changed=0
    for part in components[1:]:
        if protect is not None and any(protect[y,x] for y,x in part):continue
        if len(part)<=2:
            for y,x in part:arr[y,x]=0;changed+=1
        else:
            p=np.array(part);dist=((p[:,None]-main[None,:])**2).sum(axis=2);k,l=np.unravel_index(np.argmin(dist),dist.shape)
            a,b=p[k],main[l];steps=int(np.max(abs(b-a)));color=arr[tuple(a)].copy()
            for n in range(1,steps):
                q=np.rint(a+(b-a)*n/steps).astype(int)
                arr[tuple(q)]=color;changed+=1
    return arr,changed

PARAM={
 'attack':[(0,0,0,0,0),(0,115,0,0,0),(-10,145,0,0,0),(0,55,2,1,0),(0,30,1,1,0),(0,0,0,0,0)],
 'skill':[(0,0,0,0,0),(-110,115,0,0,0),(-125,140,0,-1,0),(70,0,4,10,60),(60,0,4,9,55),(0,0,0,0,0)],
 'skill2':[(0,0,0,0,0),(75,130,0,0,0),(-40,55,0,0,0),(0,135,-1,0,0),(0,110,-1,0,0),(0,55,2,0,0),(0,35,1,0,0),(0,0,0,0,0)],
 'ult':[(0,0,0,1,10),(75,130,0,-3,15),(65,120,0,-4,25),(-40,55,0,-4,20),(-30,40,0,-2,10),(0,0,0,0,0)],
 'hit':[(0,0,-2,0,0),(0,0,-1,0,0)],
}
RELEASE={'attack':(3,11),'skill':(3,11),'skill2':(5,17),'ult':(3,11)}
manifest={'schema':'brand-strips-v1','coordinate_units':'native pixels; rectangles use exclusive right/bottom','cell':[128,96],'scale':8,'feet_row':81,'palette':['#%02X%02X%02X'%p for p in sorted(PALETTE)],'animations':{}}
all_frames={}

def darken(im):
    arr=np.array(im);pal=np.array(sorted(PALETTE),dtype=np.int32)
    for color in np.unique(arr[:,:,:3][arr[:,:,3]>0],axis=0):
        # One material-preserving darker palette entry.
        target=color.astype(float)*.8
        k=np.argmin(((pal-target)**2).sum(axis=1))
        arr[(arr[:,:,:3]==color).all(axis=2)&(arr[:,:,3]>0),:3]=pal[k]
    return Image.fromarray(arr)

for tag,info in CELLS['tags'].items():
    count=len(info);cols=2 if tag=='hit' else 4 if tag in ['run','skill2','dead'] else 3;rows=1 if tag=='hit' else 2
    sheet=blank((cols*128,rows*96));frames=[];records=[]
    if tag=='idle':
        shutil.copy2(SRC/'brand_idle.png',OUT/'brand_idle.png')
        # Existing idle is exact 8x, retain it byte-for-byte.
        idle=Image.open(SRC/'brand_idle.png').convert('RGBA')
        idle_native=Image.fromarray(np.array(idle)[::8,::8])
    for i,meta in enumerate(info):
        px,py=meta['pivot'];dx=px-64;dy=py-88
        head_delta=[dx,dy];angles=(0,0);hand_positions=None
        if tag=='idle':frame=idle_native.crop(((i%cols)*128,(i//cols)*96,(i%cols+1)*128,(i//cols+1)*96))
        elif tag=='run':
            phase=2*math.pi*i/8;bob=-1 if i in [2,3,6,7] else 0
            la=45+15*math.sin(phase);ra=-45-15*math.sin(phase)
            lp=rot(LL,la,(60,86));rp=rot(RL,ra,(68,86))
            # Alternate far-side shading; move whole limbs, no resampling or deletion.
            if math.sin(phase)>=0:lp=darken(lp)
            else:rp=darken(rp)
            l=rot(LEFT,7*math.sin(phase),(58,73));r=rot(RIGHT,-7*math.sin(phase),(73,74))
            leg_parts=[rp,lp] if math.sin(phase)>0 else [lp,rp]
            local=composite(*leg_parts,l,UPPER,r,H)
            leg_bottom=max(lp.getbbox()[3],rp.getbbox()[3])-1
            # Translate existing leg cutouts vertically onto the common ground line.
            leg_delta=99-leg_bottom-bob
            lp=move(lp,0,leg_delta);rp=move(rp,0,leg_delta)
            leg_parts=[rp,lp] if math.sin(phase)>0 else [lp,rp]
            local=composite(*leg_parts,l,UPPER,r,H)
            frame=move(local,dx,dy+bob)
            head_delta=[dx,dy+bob]
        elif tag=='dead':
            deg=[0,0,30,45,90,90,90,90][i]
            l=rot(LEFT,-70 if i==1 else 0,(58,73));r=rot(RIGHT,100 if i==1 else 0,(73,74))
            death_head=H
            if i>=6:
                low=np.array(H);low[:60]=0;death_head=Image.fromarray(low)
            local=composite(l,BODY,r,death_head)
            local=rot(local,deg,(64,99))
            desired_dx=dx-([1,2,3,4,5,5,5,5][i])
            # A rigid fall shifts up as necessary so its lowest pixel remains on row 81.
            desired_dy=81-(local.getbbox()[3]-1)
            frame=move(local,desired_dx,desired_dy)
            head_delta=[desired_dx,desired_dy]
            if i==7:frame=frames[6].copy()
        else:
            al,ar,sx,sy,crouch=PARAM[tag][i];angles=(al,ar)
            l=rot(LEFT,al,(58,73));r=rot(RIGHT,ar,(73,74))
            if crouch:
                legs=composite(rot(LL,-crouch,(60,86)),rot(RL,crouch,(68,86)))
                local=composite(l,UPPER,legs,r,H)
            else:local=composite(l,BODY,r,H)
            # Make arms visible over torso, then head in its original 3/4 view.
            local=composite(local,l,r,H)
            final_dx=dx+sx;final_dy=dy+sy
            floor=81
            if tag=='ult' and i in [1,2,3,4]:floor=81-[0,3,4,4,2,0][i]
            lowest=local.getbbox()[3]-1+final_dy
            if tag=='ult' and i in [1,2,3,4]:final_dy+=floor-lowest
            elif lowest>floor:final_dy-=lowest-floor
            frame=move(local,final_dx,final_dy)
            head_delta=[final_dx,final_dy]
            hand_positions=[point_rot((51,85),(58,73),al),point_rot((79,86),(73,74),ar)]
            hand_positions=[[round(p[0]+final_dx),round(p[1]+final_dy)] for p in hand_positions]
        # Canvas is 128x96; figure must lie wholly above baseline.
        arr=np.array(frame)[:96].copy()
        protect=np.array(move(H,*head_delta))[:96,:,3]>0 if tag not in ['idle','dead'] else None
        if tag!='idle':arr,cleanup_count=clean_rotation_fragments(arr,protect)
        else:cleanup_count=0
        frame=Image.fromarray(arr)
        if hand_positions:
            measured=[]
            warm=(arr[:,:,3]>0)&(arr[:,:,0]>160)&(arr[:,:,1]>30)&(arr[:,:,2]<80)
            wy,wx=np.where(warm)
            for hx,hy in hand_positions:
                distances=(wx-hx)**2+(wy-hy)**2;k=int(np.argmin(distances))
                assert distances[k]<=25,(tag,i,'fire hand missing',hx,hy)
                measured.append([int(wx[k]),int(wy[k])])
            hand_positions=measured
        assert not arr[82:,:,3].any(),(tag,i,bbox(frame))
        assert set(np.unique(arr[:,:,3])).issubset({0,255})
        colors=set(tuple(p[:3]) for p in arr.reshape(-1,4) if p[3])
        assert colors.issubset(PALETTE),(tag,i,colors-PALETTE)
        head_exact=None
        if tag not in ['idle','dead']:
            pasted=move(H,*head_delta);mask=np.array(pasted)[:96,:,3]>0
            head_exact=bool(np.array_equal(arr[mask],np.array(pasted)[:96][mask]));assert head_exact,(tag,i)
        frames.append(frame)
        ox=(i%cols)*128;oy=(i//cols)*96;sheet.paste(frame,(ox,oy))
        rec={'frame':i+1,'ms':meta['ms'],'cell_rect':[ox,oy,ox+128,oy+96],'cell_rect_8x':[ox*8,oy*8,(ox+128)*8,(oy+96)*8],'pivot':meta['pivot'],'pivot_sheet':[ox+px,oy+py],'bbox':bbox(frame),'head_translation':head_delta,'head_exact':head_exact,'opaque_pixels':int((arr[:,:,3]>0).sum()),'fire_hands':hand_positions,'rotation_fragment_cleanup_pixels':cleanup_count}
        if tag in RELEASE and i==RELEASE[tag][0]:
            rec['release']={'tick':RELEASE[tag][1],'hand':'both' if tag in ['skill','ult'] else 'front','positions':hand_positions if tag in ['skill','ult'] else [hand_positions[1]]}
            rec['release']['positions_sheet']=[[x+ox,y+oy] for x,y in rec['release']['positions']]
            rec['release']['positions_8x']=[[x*8,y*8] for x,y in rec['release']['positions']]
        if tag=='dead':rec['head_rotation_degrees']=[0,0,30,45,90,90,90,90][i]
        if tag=='skill2' and i==2:rec['secondary_release']={'event':'E blaze','hands':hand_positions}
        records.append(rec)
    sheet.save(OUT/'1x'/f'brand_{tag}_1x.png')
    if tag!='idle':sheet.resize((cols*1024,rows*768),Image.Resampling.NEAREST).save(OUT/f'brand_{tag}.png')
    # Verify the saved strip is exactly one source cell per 8x8 pure block.
    delivered=np.array(Image.open(OUT/f'brand_{tag}.png').convert('RGBA'))
    assert np.array_equal(delivered,np.repeat(np.repeat(np.array(sheet),8,0),8,1))
    gifframes=[]
    for frame in frames:
        preview=Image.new('RGB',(512,384),'#DADADA');big=frame.resize((512,384),Image.Resampling.NEAREST);preview.paste(big,(0,0),big);gifframes.append(preview)
    gifframes[0].save(OUT/'previews'/f'brand_{tag}.gif',save_all=True,append_images=gifframes[1:],duration=[m['ms'] for m in info],loop=0,disposal=2)
    manifest['animations'][tag]={'file':f'brand_{tag}.png','size':[cols*1024,rows*768],'grid':[cols,rows],'frames':records,'source':'supplied idle' if tag=='idle' else 'image_gen pose draft; final corrected with rigid cutouts from approved design','raw':None if tag=='idle' else f'raw/brand_{tag}_raw.png'}
    all_frames[tag]=frames

(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(SRC/'brand_cells.json',OUT/'brand_cells.json')
(OUT/'palette.txt').write_text('\n'.join('#%02X%02X%02X'%p for p in sorted(PALETTE))+'\n',encoding='utf-8')
# Representative release/run/fall frames in a compact review sheet.
overview=Image.new('RGB',(1024,768),'#DADADA');draw=ImageDraw.Draw(overview)
for j,(tag,idx) in enumerate([('idle',0),('run',2),('attack',3),('skill',3),('skill2',5),('ult',3),('hit',0),('dead',6)]):
    f=all_frames[tag][idx].crop((20,26,108,86)).resize((264,180),Image.Resampling.NEAREST)
    x=(j%4)*256;y=(j//4)*384;overview.paste(f,(x,y+64),f);draw.text((x+12,y+20),f'{tag}: frame {idx+1}',fill='#222222')
overview.save(OUT/'brand_actions_overview.png')
print(json.dumps({'checks':'passed','animations':{t:len(f) for t,f in all_frames.items()},'palette':len(PALETTE)},ensure_ascii=False))
