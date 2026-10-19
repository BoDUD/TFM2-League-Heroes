"""Export generated FX paintings using the pack's requested majority-cell workflow.
No procedural VFX shapes are drawn. Only raster sampling, palette snapping,
mirroring, sheet assembly and labelled QA previews are performed here.
"""
from pathlib import Path
from collections import Counter
import json, re, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
JOBS = json.loads((ROOT / 'processing' / 'jobs.json').read_text(encoding='utf-8'))
RAMP_DARK = {'#C06E18','#7A3E10','#6E522C','#46321A','#6E1C0A','#6E1A12'}
# The painted opening flashes/rings can exceed the explicit brief sizes.
# Fit only these oversized raster motifs to their specified game-space envelopes.
OPENING_ENVELOPES={
    'q_burst':{0:(12,10,19),1:(24,9,19)},
    'r_land':{0:(14,8,26),1:(40,14,26)},
    'e_hit':{0:(10,10,10)},
    'e_taunt':{0:(8,8,5),1:(8,9,5),2:(8,9,5),3:(8,8,5)},
    'r_slow':{0:(18,6,5),1:(18,6,5)},
    'r_shock':{0:(24,8,20),1:(44,16,20),2:(64,24,20),3:(74,28,18)},
}

def palette_for(job):
    colors = list(dict.fromkeys(re.findall(r'#[0-9A-Fa-f]{6}',job['prompt'].split('RAW GENERATION')[0])))
    colors = [x.upper() for x in colors if x.upper() != '#000000' and x.upper() not in RAMP_DARK]
    return colors, np.array([[int(c[k:k+2],16) for k in (1,3,5)] for c in colors],dtype=np.int32)

def snap_majority(crop, width, height, palette):
    rgba = np.array(crop.convert('RGBA'))
    rgb = rgba[:,:,:3].astype(np.int32)
    # Transparent background is a distinct vote. Snap all visible source pixels
    # before taking the most frequent color in each requested logical grid cell.
    labels = np.zeros(rgba.shape[:2],dtype=np.uint8)
    active = rgba[:,:,3] >= 128
    active_rgb = rgb[active]
    if len(active_rgb):
        labels[active] = np.argmin(((active_rgb[:,None,:]-palette[None,:,:])**2).sum(axis=2),axis=1)+1
    result = np.zeros((height,width,4),dtype=np.uint8)
    ih,iw = labels.shape
    for y in range(height):
        ya,yb = round(y*ih/height),round((y+1)*ih/height)
        for x in range(width):
            xa,xb = round(x*iw/width),round((x+1)*iw/width)
            votes = np.bincount(labels[ya:yb,xa:xb].ravel(),minlength=len(palette)+1)
            # Majority coverage decides binary opacity separately, so a cell
            # with several gold shades cannot lose to a minority of transparent
            # pixels simply because its opaque votes are split among shades.
            winner = int(votes[1:].argmax())+1 if votes[1:].sum() >= votes.sum()*.5 else 0
            if winner:
                result[y,x,:3] = palette[winner-1]
                result[y,x,3] = 255
    # Mirror the better-preserved source half; never blend colors or create motifs.
    half = width//2
    left_count = np.count_nonzero(result[:,:half,3])
    right_count = np.count_nonzero(result[:,width-half:,3])
    side = 'left' if left_count >= right_count else 'right'
    if side == 'left':
        result[:,width-half:] = result[:,:half][:,::-1]
    else:
        result[:,:half] = result[:,width-half:][:,::-1]
    return result, side

def adaptive_cuts(profile,count):
    length=len(profile)
    if count==1:
        return [0,length]
    smooth=np.convolve(profile.astype(float),np.ones(5)/5,mode='same')
    cuts=[0]
    for i in range(1,count):
        expected=length*i/count
        lo=max(cuts[-1]+1,round(expected-length/count*0.27))
        hi=min(length-1,round(expected+length/count*0.27))
        segment=smooth[lo:hi+1]
        low=segment.min()
        candidates=np.flatnonzero(segment<=low+max(1,low*.03))+lo
        groups=np.split(candidates,np.flatnonzero(np.diff(candidates)>1)+1)
        group=max(groups,key=lambda g:(len(g),-abs(g.mean()-expected)))
        cuts.append(round(float(group.mean())))
    return cuts+[length]

def export_one(job):
    raw = OUT / 'raw' / job['file']
    if not raw.exists():
        return None
    source = Image.open(raw).convert('RGBA')
    width,height = job['cell_1x']
    cols,rows = job['raw_layout']['cols'],job['raw_layout']['rows']
    hexes,palette = palette_for(job)
    mask=np.array(source.getchannel('A'))>=128
    xcuts=adaptive_cuts(mask.sum(axis=0),cols)
    ycuts=adaptive_cuts(mask.sum(axis=1),rows)
    frames,halves = [],[]
    raw_boxes=[]
    for n in range(job['frames']):
        cx,cy = n%cols,n//cols
        box=(xcuts[cx],ycuts[cy],xcuts[cx+1],ycuts[cy+1])
        crop=source.crop(box)
        opaque=crop.getchannel('A').point(lambda a:255 if a>=128 else 0)
        bbox=opaque.getbbox()
        nw,nh=round(source.width/cols),round(source.height/rows)
        aligned=Image.new('RGBA',(nw,nh))
        if bbox:
            dx=round(nw/2-(bbox[0]+bbox[2])/2)
            dy=box[1]-round(cy*source.height/rows)
            if job['id'] in {'a_hit','q_hit','r_hit','e_taunt'}:
                # Align thin rays/marks to logical pixel centers instead of
                # splitting them across four pixels at a grid intersection.
                dx=round(nw/2+nw/width*.5-(bbox[0]+bbox[2])/2)
                dy=round(nh/2+nh/height*.5-(bbox[1]+bbox[3])/2)
            elif job['id'] in {'q_dust','q_slow','r_slow'}:
                dy=nh-bbox[3]
            aligned.paste(crop,(dx,dy))
        envelope=OPENING_ENVELOPES.get(job['id'],{}).get(n)
        if envelope:
            ew,eh,center_y=envelope
            art_box=aligned.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
            drawing,side=snap_majority(aligned.crop(art_box),ew,eh,palette)
            frame=np.zeros((height,width,4),dtype=np.uint8)
            x=(width-ew)//2; y=round(center_y-eh/2)
            frame[y:y+eh,x:x+ew]=drawing
        else:
            frame,side = snap_majority(aligned,width,height,palette)
        frames.append(frame)
        halves.append(side)
        raw_boxes.append(list(box))
    sheet = Image.fromarray(np.concatenate(frames,axis=1))
    sheet.save(OUT/'pixel_1x'/job['file'])
    sheet.resize((sheet.width*8,sheet.height*8),Image.Resampling.NEAREST).save(OUT/job['file'])
    occupied = [int(np.count_nonzero(f[:,:,3])) for f in frames]
    unique = len({f.tobytes() for f in frames})
    assert all(np.array_equal(f,f[:,::-1]) for f in frames),job['id']
    assert set(np.unique(np.concatenate(frames,axis=1)[:,:,3])) <= {0,255},job['id']
    assert all(occupied), (job['id'],'empty frame',occupied)
    return {'id':job['id'],'file':job['file'],'frames':job['frames'],'cell_1x':[width,height],
        'cell_8x':[width*8,height*8],'sheet_1x':[sheet.width,sheet.height],
        'sheet_8x':[sheet.width*8,sheet.height*8],'layout':'single horizontal row, no gutters',
        'loop':job['loop'],'binding':job['binding'],'symmetry':'exact horizontal mirror per frame',
        'symmetry_source_half':halves,'alpha_values':[0,255],'palette':hexes,
        'raw_layout':job['raw_layout'],'raw_frame_boxes':raw_boxes,'raw_size':list(source.size),'source_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
        'opening_envelopes':OPENING_ENVELOPES.get(job['id'],{}),
        'occupied_pixels_per_frame':occupied,'distinct_frames':unique,
        'all_frames_nonempty':all(occupied),'all_frames_distinct':unique==job['frames'],
        'processing':'alpha-profile valley frame cuts near expected grid; align horizontal emitter and center hits / bottom-align foot dust; source alpha>=128; majority opaque coverage per logical pixel then most-frequent allowed RGB color among opaque samples; copy denser half to opposite half; nearest-neighbor 8x export'}

def previews(entries):
    try:
        font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    except OSError:
        font=ImageFont.load_default()
    boards=[]
    tilew,tileh=340,235
    for t in range(60):
        board=Image.new('RGB',(tilew*4,tileh*4),(22,27,36))
        draw=ImageDraw.Draw(board)
        for index,e in enumerate(entries):
            j=next(x for x in JOBS if x['id']==e['id'])
            sheet=Image.open(OUT/'pixel_1x'/e['file']).convert('RGBA')
            w,h=e['cell_1x']; n=t%e['frames']
            frame=sheet.crop((n*w,0,(n+1)*w,h)).resize((w*4,h*4),Image.Resampling.NEAREST)
            x,y=(index%4)*tilew,(index//4)*tileh
            board.paste(frame,(x+(tilew-frame.width)//2,y+32+(195-frame.height)//2),frame)
            draw.text((x+12,y+8),f"{e['id']}  {n+1}/{e['frames']}  {w}x{h}",font=font,fill=(225,232,242))
        boards.append(board)
    boards[0].save(OUT/'previews'/'animation_overview.gif',save_all=True,append_images=boards[1:],duration=140,loop=0,disposal=2)
    boards[2].save(OUT/'previews'/'overview.png')

def main():
    entries=[]
    for j in JOBS:
        entry=export_one(j)
        if entry:
            entries.append(entry)
            print(j['id'],entry['occupied_pixels_per_frame'],'distinct',entry['distinct_frames'])
    manifest={'version':1,'character':'Rammus','expected_sheets':13,'exported_sheets':len(entries),
        'total_frames':sum(x['frames'] for x in entries),'source':'image_gen paintings',
        'reference_texture_included':False,'entries':entries}
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    if entries:
        previews(entries)
    print('exported',len(entries),'of13')

if __name__=='__main__':
    main()
