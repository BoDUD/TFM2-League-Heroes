from PIL import Image, ImageDraw
from pathlib import Path
import numpy as np, json
from regrid_khazix import ROOT, HEX, PAL

src=np.asarray(Image.open('work/B_regridded_1x.png')).copy()
# Source-cell extraction; drop the dangling bottom toe-cell row so both feet share row47.
src=src[:48]
# Eye cleanup within existing face, not a new drawn actor. Protect these columns/rows below.
for y in (23,24):
    for x in (41,42): src[y,x]=[*PAL[19],255]
for x,y in [(40,23),(40,24),(43,23),(43,24),(41,22),(42,22),(41,25),(42,25)]:
    src[y,x]=[*PAL[0],255]
# Two teeth sampled from the pale approved shoulder/blade palette in the existing red jaw.
for x,y in [(43,26),(44,27)]:
    if src[y,x,3]:src[y,x]=[*PAL[14],255]

delete_top=[2,4,6]
right_columns=[49,51,53,55,57,59,61,62]
left_columns={
    'A':[2,4,6,8,10,12,14,16,18,20,22,24,27,29],
    'B':[3,5,7,9,11,13,15,17,20,24,26,28],
}
metrics={}
final_arrays={}
for label,height in [('A',40),('B',44)]:
    columns=left_columns[label]+right_columns
    arr=np.delete(src,columns,axis=1)
    # Keep the face untouched; reduce ONLY rows above the shell.
    if label=='B':
        arr=np.concatenate([arr[:30],arr[29:30],arr[30:33],arr[32:33],arr[33:37],arr[36:37],arr[37:41],arr[40:41],arr[41:]],axis=0)
    arr=np.delete(arr,delete_top,axis=0)
    # Existing toe/claw bottom cells use the one outline color for a clean common foot floor.
    arr[-1,arr[-1,:,3]>0]=[*PAL[0],255]
    # Feet are centered on logical x64; original outer foot span was48 cells.
    foot_width=48-len(left_columns[label])
    x0=64-foot_width//2
    y0=100-arr.shape[0]
    canvas=np.zeros((128,128,4),dtype=np.uint8)
    canvas[y0:y0+arr.shape[0],x0:x0+arr.shape[1]]=arr
    small=Image.fromarray(canvas)
    small.save(ROOT/f'khazix_design_{label}_1x.png')
    full=small.resize((1024,1024),Image.Resampling.NEAREST)
    full.save(ROOT/f'khazix_design_{label}.png')
    colors=sorted(set(tuple(int(v) for v in p[:3]) for p in canvas.reshape(-1,4) if p[3]))
    bbox=small.getbbox()
    info={'source':'raw/B_pixel_generated.png','source_grid':'work/B_grid.json','source_shell_top_row':8,'source_sole_row':47,'removed_source_rows':delete_top,'removed_source_columns':columns,'duplicated_body_rows':[] if label=='A' else [29,32,36,40],
    'shell_to_sole_rows':height,'antennae_above_shell_rows':5,'total_height_rows':arr.shape[0],'total_width_columns':bbox[2]-bbox[0],'feet_outer_span_columns':foot_width,'right_claw_overhang_from_front_foot':8,'sole_row':99,'shell_top_row':100-height,'antenna_top_row':y0,'feet_midpoint_x':x0+(foot_width/2),'bbox_1x':bbox,'opaque_colors':len(colors),'alpha_values':[0,255],'strict_8x8_grid':True}
    assert arr.shape[0]==height+5
    assert info['total_width_columns']<=(56 if label=='A' else 60)
    assert foot_width<=(34 if label=='A' else 37)
    assert bbox[3]==100 and not canvas[100:,:,3].any()
    assert len(colors)<=30 and set(np.unique(canvas[:,:,3]))=={0,255}
    assert np.array_equal(np.asarray(full),np.repeat(np.repeat(canvas,8,axis=0),8,axis=1))
    metrics[label]=info; final_arrays[label]=arr
    (ROOT/f'palette_{label}.txt').write_text('\n'.join('#%02X%02X%02X'%c for c in colors)+'\n')

(ROOT/'validation.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
(ROOT/'palette.txt').write_text('\n'.join('#'+h for h in HEX)+'\n',encoding='utf-8')
swatch=Image.new('RGB',(540,150),'white'); d=ImageDraw.Draw(swatch)
for i,h in enumerate(HEX):
    x=(i%9)*60;y=(i//9)*50
    d.rectangle((x,y,x+59,y+34),fill='#'+h);d.text((x+2,y+36),str(i),fill='black')
swatch.save(ROOT/'palette.png')
# Visual review on a light ground, including approved game heroes at identical8x pixel scale.
bar=Image.open('work/khazix_pack1/khazix/3_quality_bar.png').convert('RGBA')
preview=Image.new('RGBA',(1984,930),'white');preview.alpha_composite(bar,(0,500));d=ImageDraw.Draw(preview)
for n,label in enumerate(('A','B')):
    arr=final_arrays[label]; sprite=Image.fromarray(arr).resize((arr.shape[1]*8,arr.shape[0]*8),Image.Resampling.NEAREST)
    xx=440+n*600;yy=430-sprite.height
    preview.alpha_composite(sprite,(xx,yy));d.text((xx,440),label+' shell '+str(metrics[label]['shell_to_sole_rows'])+' / width '+str(metrics[label]['total_width_columns']),fill='black')
preview.save(ROOT/'comparison.png')
print(json.dumps(metrics,indent=2))
