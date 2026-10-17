from pathlib import Path
import sys, json
import numpy as np
from PIL import Image, ImageDraw

REPO=Path('D:/TFM2-Workshop/repo/.claude/worktrees/nervous-austin-5d9567')
sys.path.insert(0,str(REPO/'tools/art'))
sys.path.insert(0,str(REPO/'.claude/skills/tfm2-hero-mod/scripts'))
from regrid import regrid
from design_riven import keep_axis, palette
from strips import complete_outline

OUT=Path('outputs/zeri-model')
raw,size,axes=regrid(np.asarray(Image.open(OUT/'raw/zeri_B_attempt1.png').convert('RGBA')),18)
pal,idx=palette(raw,31,seed=1)
dark=pal.max(1)<48
pal[dark]=[16,12,20]
Image.fromarray(raw).save(OUT/'raw/zeri_shared_readback_1x.png')
stats=[]
for name,height,width in [('A',40,30),('B',42,32)]:
    # Preserve the complete face and both foot soles. Only delete whole source lines.
    h,w=idx.shape
    protected_rows=range(15,25)
    rows=keep_axis([idx[y] for y in range(h)],height,protected_rows)
    for edge in [0,h-1]:
        if edge not in rows:
            replace=min((r for r in rows if r not in protected_rows and r not in [0,h-1]),key=lambda r:abs(r-edge))
            rows.remove(replace); rows.append(edge); rows.sort()
    cols=keep_axis([idx[rows][:,x] for x in range(w)],width,range(15,24))
    sub=idx[np.ix_(rows,cols)]
    fig=np.zeros(sub.shape+(4,),np.uint8)
    mask=sub>=0
    fig[mask,:3]=pal[sub[mask]]; fig[mask,3]=255
    keep=np.zeros(fig.shape[:2],bool)
    keep[np.ix_([rows.index(r) for r in protected_rows],[cols.index(c) for c in range(15,24)])]=True
    # Repair deleted outline only inside the final frame; no extra row under the soles.
    fig,added,darkened=complete_outline(fig,color=(16,12,20),feet=height-1,keep=keep)
    ys,xs=np.nonzero(fig[...,3]>0)
    fig=fig[ys.min():ys.max()+1,xs.min():xs.max()+1]
    feet=np.where((fig[-3:,:,3]>0).any(0))[0]
    foot_mid=(feet.min()+feet.max())/2
    x0=int(round(64-foot_mid)); y0=100-fig.shape[0]
    can=np.zeros((128,128,4),np.uint8)
    can[y0:y0+fig.shape[0],x0:x0+fig.shape[1]]=fig
    Image.fromarray(can).save(OUT/f'zeri_design_{name}_1x.png')
    zoom=np.repeat(np.repeat(can,8,0),8,1)
    Image.fromarray(zoom).save(OUT/f'zeri_design_{name}.png')
    colors=sorted({tuple(map(int,c)) for c in can[can[...,3]>0,:3]})
    (OUT/f'palette_{name}.hex').write_text('\n'.join('#%02X%02X%02X'%c for c in colors)+'\n')
    swatch=Image.new('RGB',(8*32,4*32),'white')
    draw=ImageDraw.Draw(swatch)
    for i,c in enumerate(colors):
        draw.rectangle((i%8*32,i//8*32,i%8*32+31,i//8*32+31),fill=c)
    swatch.save(OUT/f'palette_{name}.png')
    stat=dict(version=name,height=int(fig.shape[0]),width=int(fig.shape[1]),canvas_1x=[128,128],canvas_8x=[1024,1024],top_row=y0,sole_row=99,left_col=x0,foot_mid_col=x0+foot_mid,color_count=len(colors),alpha_values=list(map(int,np.unique(can[...,3]))),source_grid=list(raw.shape[:2]),source_cell_size=size,rows_kept=rows,columns_kept=cols,face_rows_preserved=list(protected_rows),face_cols_preserved=list(range(15,24)),outline_added=added,outline_darkened=darkened)
    assert stat['height']==height and stat['width']<=width
    assert len(colors)<=32 and stat['alpha_values']==[0,255]
    assert not can[100:,:,3].any()
    assert np.array_equal(zoom, np.repeat(np.repeat(np.asarray(Image.open(OUT/f'zeri_design_{name}_1x.png')),8,0),8,1))
    stats.append(stat)
(OUT/'image-qa.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')
# Preview is a presentation surface only, not a source sprite.
preview=Image.new('RGBA',(800,440),'#EEEEF0')
draw=ImageDraw.Draw(preview)
for i,name in enumerate(['A','B']):
    can=Image.open(OUT/f'zeri_design_{name}_1x.png')
    bbox=can.getbbox(); crop=can.crop(bbox)
    zoom=crop.resize((crop.width*8,crop.height*8),Image.Resampling.NEAREST)
    preview.alpha_composite(zoom,(i*400+(400-zoom.width)//2,400-zoom.height))
    draw.text((i*400+145,415),f'{name} / {stats[i]["height"]} px',fill='#222222')
preview.convert('RGB').save(OUT/'zeri_design_comparison.png')
print(json.dumps([{k:v for k,v in s.items() if k not in ['rows_kept','columns_kept']} for s in stats]))
