"""Read generated 8px blocks by majority color; translate whole frames, never reduce actors."""
from pathlib import Path
import hashlib,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent
SRC=OUT/'source'
ROOT=OUT
for name in ['previews','source']: (OUT/name).mkdir(exist_ok=True)
cells=json.loads((OUT/'gragas_cells.json').read_text(encoding='utf-8'))
source=np.array(Image.open(SRC/'gragas_design_1x.png').convert('RGBA'))
colors=np.unique(source[source[:,:,3]>0,:3],axis=0)
assert len(colors)==24
palette=Image.new('P',(1,1))
palette.putpalette(np.vstack((colors,np.repeat(colors[:1],256-24,axis=0))).ravel().tolist())

def components(mask):
    seen=np.zeros_like(mask);groups=[];h,w=mask.shape
    for y,x in zip(*np.nonzero(mask)):
        if seen[y,x]: continue
        todo=[(y,x)];seen[y,x]=True;points=[]
        while todo:
            cy,cx=todo.pop();points.append((cx,cy))
            for dy,dx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                ny,nx=cy+dy,cx+dx
                if 0<=ny<h and 0<=nx<w and mask[ny,nx] and not seen[ny,nx]:
                    seen[ny,nx]=True;todo.append((ny,nx))
        groups.append(np.array(points))
    return groups

def read_grid(path):
    im=Image.open(path).convert('RGBA')
    # Padding only adds empty canvas to complete the final partial grid cell.
    padded=Image.new('RGBA',((im.width+7)//8*8,(im.height+7)//8*8));padded.paste(im,(0,0))
    indices=np.array(padded.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE))
    indices[indices>=24]=0
    indices[np.array(padded)[:,:,3]<128]=24
    h,w=indices.shape
    blocks=indices.reshape(h//8,8,w//8,8).transpose(0,2,1,3).reshape(-1,64)
    chosen=np.array([np.bincount(b,minlength=25).argmax() for b in blocks]).reshape(h//8,w//8)
    a=np.zeros((h//8,w//8,4),dtype=np.uint8)
    a[chosen<24,:3]=colors[chosen[chosen<24]];a[chosen<24,3]=255
    return a,im.size

configs={'run':(4,2,55,8,'run-attempt4.png'),'attack':(3,2,64,5,'attack-attempt1.png'),
         'skill':(3,2,64,5,'skill-attempt1.png'),'skill2':(4,2,55,8,'skill2-attempt1.png'),
         'ult':(3,2,64,5,'ult-attempt1.png'),'hit':(2,1,110,2,'hit-attempt1.png'),
         'dead':(4,2,55,8,'dead-attempt1.png')}
manifest={'version':2,'route':'image_gen redrawn complete poses; majority-color grid readback',
          'scale':8,'cell_native':[128,128],'cell_output':[1024,1024],
          'palette':['#'+bytes(c).hex() for c in colors],
          'component_rig_used':False,'actor_resized':False,'frames':{},'raw':{},'checks':{}}
all_frames={}
for action,(cols,rows,step,count,filename) in configs.items():
    raw_path=OUT/'raw'/filename
    grid,size=read_grid(raw_path)
    groups=[[] for _ in range(count)];removed=[]
    for component in components(grid[:,:,3]>0):
        if len(component)<=2:
            removed.append(component.tolist());continue
        centre=component.mean(0)
        col=min(cols-1,max(0,int(centre[0]//step)))
        row=min(rows-1,max(0,int(centre[1]//step)))
        index=row*cols+col
        if index<count:groups[index].append(component)
    native=Image.new('RGBA',(cols*128,rows*128))
    records=[];frames=[];decoded=[]
    for i,group in enumerate(groups):
        if not group: raise ValueError((action,i,'empty generated frame'))
        coords=np.concatenate(group)
        decoded.append(coords)
    if action=='dead': decoded[7]=decoded[6].copy() # exact still hold, one complete drawn pose
    if action=='run': decoded=decoded[4:]+decoded[:4] # cycle phase starts with the near-foot landing
    for i,coords in enumerate(decoded):
        x0,y0=coords.min(0);x1,y1=coords.max(0)+1
        if action=='run':
            head=coords[(coords[:,1]>=y0)&(coords[:,1]<y0+10)]
            light=np.array([tuple(grid[y,x,:3]) in {tuple(bytes.fromhex(c)) for c in ['FED19C','FDDCB9','FDF6E1','E6A679']} for x,y in head])
            assert light.any()
            anchor=round(float(np.median(head[light,0])))
            target=cells['tags'][action][i]['pivot'][0]+2
        elif action=='dead' and i>=4:
            anchor=round(float((x0+x1)/2));target=cells['tags'][action][i]['pivot'][0]
        else:
            feet=coords[coords[:,1]>=y1-3,0]
            anchor=round(float((feet.min()+feet.max())/2));target=cells['tags'][action][i]['pivot'][0]
        translation=(int(target-anchor),int(100-y1))
        final=coords+np.array(translation)
        assert (final>=0).all() and final[:,0].max()<128 and final[:,1].max()<100,(action,i,final.min(0),final.max(0))
        a=np.zeros((128,128,4),dtype=np.uint8)
        a[final[:,1],final[:,0]]=grid[coords[:,1],coords[:,0]]
        assert not a[100:,:,3].any()
        im=Image.fromarray(a)
        frames.append(im)
        native.paste(im,(i%cols*128,i//cols*128))
        source_box=[int(x0),int(y0),int(x1),int(y1)]
        records.append({'index':i,'frame_number':i+1,
           'rect_native':[i%cols*128,i//cols*128,128,128],
           'rect_output':[i%cols*1024,i//cols*1024,1024,1024],
           'pivot_native':cells['tags'][action][i]['pivot'],
           'pivot_output':[v*8 for v in cells['tags'][action][i]['pivot']],
           'duration_ms':cells['tags'][action][i]['ms'],
           'bbox_native':list(im.getbbox()),'bbox_output':[v*8 for v in im.getbbox()],
           'raw_global_grid_bbox':source_box,'raw_bbox_pixels':[v*8 for v in source_box],
           'translation_native':list(translation),'opaque_pixels':len(coords),
           'body_height_including_pose':int(y1-y0),'component_areas':[len(c) for c in group],
           'source':filename,'source_frame_number':7 if action=='dead' and i==7 else ((i+4)%8+1 if action=='run' else i+1),
           'actor_resampled':False})
    if action in ['attack','skill','skill2','ult']:
        records[2]['release_or_impact_tick']={'attack':8,'skill':9,'skill2':8,'ult':10}[action]
    native.save(OUT/f'gragas_{action}_1x.png')
    big=native.resize((native.width*8,native.height*8),Image.Resampling.NEAREST)
    big.save(OUT/f'gragas_{action}.png')
    a=np.array(native);b=np.array(big)
    blocks=b.reshape(a.shape[0],8,a.shape[1],8,4)
    assert np.array_equal(blocks,np.broadcast_to(a[:,None,:,None,:],blocks.shape))
    assert set(np.unique(a[:,:,3]))=={0,255}
    assert {tuple(c) for c in a[a[:,:,3]>0,:3]}<={tuple(c) for c in colors}
    assert big.size==(cols*1024,rows*1024)
    if count==5: assert not a[128:,256:,3].any()
    manifest['frames'][action]=records
    manifest['raw'][action]={'file':filename,'size':list(size),'grid_step_pixels':8,
         'isolated_fringe_blocks_removed':removed,'sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest()}
    manifest['checks'][action]={'output_size':list(big.size),'count':count,'strict_8x8_blocks':True,
         'palette_only':True,'binary_alpha':True,'footline_clear':True,'unused_cells_empty':True,
         'no_actor_resize_or_component_animation':True}
    all_frames[action]=frames
    previews=[]
    for i,im in enumerate(frames):
        normalized=Image.new('RGBA',(128,128));normalized.paste(im,(64-cells['tags'][action][i]['pivot'][0],0))
        crop=normalized.crop((18,38,114,103)).resize((576,390),Image.Resampling.NEAREST)
        bg=Image.new('RGBA',crop.size,'#dce1e8');bg.alpha_composite(crop);previews.append(bg.convert('RGB'))
    previews[0].save(OUT/f'previews/gragas_{action}.gif',save_all=True,append_images=previews[1:],
        duration=[c['ms'] for c in cells['tags'][action]],loop=1 if action=='dead' else 0,disposal=2)

manifest['frames']['idle']=[]
idle=Image.open(OUT/'gragas_idle.png')
for i,c in enumerate(cells['tags']['idle']):
    x=i%4*1024;y=i//4*1024;box=idle.crop((x,y,x+1024,y+1024)).getbbox()
    manifest['frames']['idle'].append({'index':i,'frame_number':i+1,'rect_output':[x,y,1024,1024],
       'rect_native':[x//8,y//8,128,128],'pivot_native':c['pivot'],'duration_ms':c['ms'],
       'bbox_output':list(box),'bbox_native':[v//8 for v in box],'source':'provided idle unchanged'})
manifest['checks']['idle_byte_identical']=True
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(OUT/'validation.json').write_text(json.dumps(manifest['checks'],indent=2),encoding='utf-8')

sheet=Image.new('RGB',(2400,1750),'#dce1e8');d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
for row,(action,frames) in enumerate(all_frames.items()):
    d.text((8,row*250+5),action,fill='#192139',font=font)
    for i,im in enumerate(frames):
        norm=Image.new('RGBA',(128,128));norm.paste(im,(64-cells['tags'][action][i]['pivot'][0],0))
        view=norm.crop((18,38,114,103)).resize((288,195),Image.Resampling.NEAREST)
        sheet.paste(view,(i*300,row*250+30),view)
        d.text((i*300+135,row*250+230),str(i+1),fill='#192139',font=small)
sheet.save(OUT/'gragas-strips-contact.png')
print(json.dumps({a:{'heights':[f['body_height_including_pose'] for f in fs],
                    'widths':[f['bbox_native'][2]-f['bbox_native'][0] for f in fs]} for a,fs in manifest['frames'].items() if a!='idle'},indent=2))
