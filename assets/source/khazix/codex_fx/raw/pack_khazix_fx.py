from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json,re,hashlib,shutil

OUT=Path('outputs/khazix-fx');SRC=Path('work/khazix_fx_pack/khazix_fx_pack')
prompts=json.loads(Path('work/fx_prompts.json').read_text())
bindings={x['file']:x for x in json.loads((SRC/'fx_list.json').read_text(encoding='utf-8'))}
for sub in ['pixel_1x','previews']:(OUT/sub).mkdir(exist_ok=True)
manifest={'generation':'native imagegen; one generation per effect','pixel_block':16,'duration_note':'Input has no VFX durations. 100ms per frame is used ONLY for review GIFs; importer must set runtime timings.','effects':[]}
left_right={'ut','p_ready','w_heal','slow','r_cast','r_on','e_reset','evo','e_land'}
top_bottom={'w_spike','e_land'}
holes={'ut':12,'w_heal':10,'r_cast':12,'r_on':20,'evo':12}
allframes={}
for item in prompts:
    tag=item['tag'];prompt=item['prompt'];file=f'khazix_fx_{tag}.png'
    if not (OUT/'raw'/f'{tag}_generated.png').exists():continue
    n=int(re.search(r'(\d+) frames',prompt).group(1))
    W,H=map(int,re.search(r'image size (\d+)x(\d+)',prompt).groups())
    cw,ch=W//n,H;gw,gh=cw//16,ch//16
    palette=np.array([tuple(bytes.fromhex(x)) for x in dict.fromkeys(re.findall(r'#([0-9A-Fa-f]{6})',prompt)) if x.upper()!='000000'],dtype=np.int16)
    original=Image.open(OUT/'raw'/f'{tag}_generated.png').convert('RGBA')
    raw=np.array(original);rw,rh=original.size
    size_numbers=[int(v) for v in re.findall(r'\d+',bindings[file]['size'])]
    intended_h=size_numbers[-1]
    visible_rows=np.flatnonzero((raw[:,:,3]>100).sum(1)>max(2,rw*.003))
    occupied_h=int(visible_rows[-1]-visible_rows[0]+1)
    viewport_h=min(rh,round(occupied_h/min(.94,intended_h/gh)))
    viewport_top=max(0,min(rh-viewport_h,round((visible_rows[0]+visible_rows[-1]+1-viewport_h)/2)))
    viewport_bottom=viewport_top+viewport_h
    frames=[];entries=[]
    for i in range(n):
        x0=round(i*rw/n);x1=round((i+1)*rw/n)
        src=raw[viewport_top:viewport_bottom,x0:x1]
        source_h=src.shape[0]
        # Regrid generated source by categorical coverage and palette votes.
        rgb=src[:,:,:3].astype(np.int16)
        distances=((rgb[:,:,None,:].astype(np.int32)-palette[None,None,:,:])**2).sum(3)
        indexes=distances.argmin(2)
        alpha=src[:,:,3].astype(np.float32)/255
        cells=np.zeros((gh,gw,4),dtype=np.uint8)
        for y in range(gh):
            ya,yb=round(y*source_h/gh),round((y+1)*source_h/gh)
            for x in range(gw):
                xa,xb=round(x*(x1-x0)/gw),round((x+1)*(x1-x0)/gw)
                weight=alpha[ya:yb,xa:xb]
                if weight.mean()<.25:continue
                votes=np.bincount(indexes[ya:yb,xa:xb].ravel(),weights=weight.ravel(),minlength=len(palette))
                chosen=votes.argmax()
                white=np.flatnonzero(np.all(palette==255,axis=1))
                if len(white) and votes[white[0]]>=votes.sum()*.10:chosen=white[0]
                cells[y,x]=[*palette[chosen],255]
        if tag!='w_spike':
            op=cells[:,:,3]>0
            padded=np.pad(op,1)
            edge=op&(~padded[:-2,1:-1]|~padded[2:,1:-1]|~padded[1:-1,:-2]|~padded[1:-1,2:])
            for dark,light in [('3A0E6A','7A22B8'),('4A3CB0','7C6CF0'),('2E7A28','72C84C')]:
                d=np.array(tuple(bytes.fromhex(dark)),dtype=np.uint8)
                l=np.array(tuple(bytes.fromhex(light)),dtype=np.uint8)
                if any(np.array_equal(c,d) for c in palette):cells[edge&np.all(cells[:,:,:3]==d,2),:3]=l
        # Packing invariants: reflect generated half/quadrant; no procedural VFX drawing.
        if tag in left_right:
            cells[:,gw//2:]=cells[:,:gw-gw//2][:,::-1]
        if tag in top_bottom:
            cells[gh//2:]=cells[:gh-gh//2][::-1]
        if tag in holes and not(tag=='evo' and i==5):
            hole=holes[tag];cells[:,(gw-hole)//2:(gw+hole)//2]=0
        if tag!='w_spike':
            op=cells[:,:,3]>0;padded=np.pad(op,1)
            edge=op&(~padded[:-2,1:-1]|~padded[2:,1:-1]|~padded[1:-1,:-2]|~padded[1:-1,2:])
            for dark,light in [('3A0E6A','7A22B8'),('4A3CB0','7C6CF0'),('2E7A28','72C84C')]:
                d=np.array(tuple(bytes.fromhex(dark)),dtype=np.uint8);l=np.array(tuple(bytes.fromhex(light)),dtype=np.uint8)
                if any(np.array_equal(c,d) for c in palette):cells[edge&np.all(cells[:,:,:3]==d,2),:3]=l
        cells[cells[:,:,3]==0]=0
        frames.append(cells)
        mask=cells[:,:,3]>0
        colors=cells[mask,:3].astype(float)
        luminance=colors@np.array([.2126,.7152,.0722]) if len(colors) else np.array([0])
        entries.append({'frame':i+1,'raw_cell_rect':[x0,viewport_top,x1-x0,source_h],'rect':[i*cw,0,cw,ch],'bbox_1x':Image.fromarray(cells).getbbox(),'opaque_pixels':int(mask.sum()),'mean_luminance':round(float(luminance.mean()),2),'brightest_decile_mean':round(float(np.sort(luminance)[-max(1,len(luminance)//10):].mean()),2),'white_pixels':int(np.all(cells[:,:,:3]==255,2)[mask].sum()),'pixel_sha256':hashlib.sha256(cells.tobytes()).hexdigest()})
        assert mask.any(),(tag,i,'empty frame')
        if tag in left_right:assert np.array_equal(cells,cells[:,::-1]),tag
        if tag in top_bottom:assert np.array_equal(cells,cells[::-1]),tag
    small=Image.fromarray(np.concatenate(frames,axis=1));small.save(OUT/'pixel_1x'/file)
    small.resize((W,H),Image.Resampling.NEAREST).save(OUT/file)
    meta={'tag':tag,'file':file,'frames':n,'size':[W,H],'cell':[cw,ch],'cell_game_pixels':[gw,gh],'binding':bindings[file],'raw':'raw/'+tag+'_generated.png','raw_size':[rw,rh],'symmetry_x':tag in left_right,'symmetry_y':tag in top_bottom,'central_empty_width':holes.get(tag),'palette':['#%02X%02X%02X'%tuple(c) for c in palette],'generation_prompt':'raw/generation_prompts.json#'+tag,'correction':'equal cell regrid; palette votes; binary alpha; reflect generated half where required; clear actor interior except evolution frame 6','frame_data':entries}
    manifest['effects'].append(meta);allframes[tag]=frames
    pics=[]
    for cell in frames:
        picture=Image.new('RGBA',(gw,gh),(21,24,38,255));picture.alpha_composite(Image.fromarray(cell))
        pics.append(picture.resize((gw*8,gh*8),Image.Resampling.NEAREST).convert('RGB'))
    pics[0].save(OUT/'previews'/f'{tag}.gif',save_all=True,append_images=pics[1:],duration=100,loop=0,disposal=2)
    review=Image.new('RGB',(n*180,200),(21,24,38));d=ImageDraw.Draw(review)
    for i,cell in enumerate(frames):
        im=Image.fromarray(cell).resize((gw*4,gh*4),Image.Resampling.NEAREST)
        review.paste(im,(i*180+(180-im.width)//2,24+(176-im.height)//2),im)
        d.text((i*180+10,6),f'{tag} {i+1}',fill='white')
    review.save(OUT/'previews'/f'{tag}_contact.png')
shutil.copy2(SRC/'fx_list.json',OUT/'fx_list.json')
shutil.copy2('work/fx_prompts.json',OUT/'raw/generation_prompts.json')
shutil.copy2(__file__,OUT/'raw/pack_khazix_fx.py')
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
# Overview preserves distinct source animations and uses presentation timing only.
pics=[]
for f in range(24):
    im=Image.new('RGB',(960,800),(21,24,38));d=ImageDraw.Draw(im)
    for j,(tag,cells) in enumerate(allframes.items()):
        cell=cells[f%len(cells)];p=Image.fromarray(cell).resize((cell.shape[1]*4,cell.shape[0]*4),Image.Resampling.NEAREST)
        x=j%4*240;y=j//4*200
        im.paste(p,(x+(240-p.width)//2,y+26+(174-p.height)//2),p)
        d.text((x+12,y+8),tag,fill='white')
    pics.append(im)
pics[0].save(OUT/'previews/all_fx.gif',save_all=True,append_images=pics[1:],duration=100,loop=0,disposal=2)
print('Packed',len(manifest['effects']),'effects,',sum(m['frames'] for m in manifest['effects']),'frames')
