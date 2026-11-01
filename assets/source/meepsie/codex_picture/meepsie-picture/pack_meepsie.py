from PIL import Image
from pathlib import Path
import numpy as np
import json

root=Path(__file__).resolve().parent
# Shared material ramp: outline, moonrock, indigo, purple, leaf and meep.
palette=[(20,10,29),(246,253,252),(199,232,244),(133,177,210),(79,115,166),
 (31,43,67),(48,58,108),(65,74,152),(89,101,185),
 (65,22,98),(113,35,161),(173,58,220),(230,163,247),
 (15,63,45),(32,105,53),(87,154,36),(157,209,39),
 (97,143,23),(176,222,48),(218,246,105)]
reports={}
for key,width in [('A',50),('B',26)]:
    source=Image.open(root/'raw'/f'meepsie-{key}-coarse-revision.png').convert('RGBA')
    alpha=source.getchannel('A').point(lambda v:255 if v>=180 else 0)
    box=alpha.getbbox()
    source.putalpha(alpha)
    small=source.crop(box).resize((width,40),Image.Resampling.LANCZOS)
    a=np.asarray(small).copy()
    mask=a[:,:,3]>=128
    rgb=a[:,:,:3].astype(float)
    colors=np.array(palette)
    # Quantize by perceptually weighted squared distance, without dithering.
    d=((rgb[:,:,None,:]-colors[None,None,:,:])**2*np.array([.3,.5,.2])).sum(axis=3)
    a[:,:,:3]=colors[d.argmin(axis=2)]
    a[:,:,3]=mask*255
    a[~mask]=0
    # Restore the pilot's eye clusters lost during downsampling. These are
    # local face edits, not substitute actor artwork.
    ink=palette[0]+(255,)
    lime=palette[18]+(255,)
    light=palette[19]+(255,)
    green=palette[17]+(255,)
    white=palette[1]+(255,)
    if key=='A':
        for yy,left,right in [(11,27,32),(12,26,33),(13,26,33),(14,26,33),(15,26,33),(16,26,33),(17,27,32),(18,27,32),(19,28,31)]:
            a[yy,left:right+1]=lime
        a[12,27:32]=light
        a[18,27:33]=green
        a[19,28:32]=green
        a[13:16,27:29]=ink
        a[13:16,31:33]=ink
        a[13,27]=white
        a[13,31]=white
        a[16,29:31]=green
        a[9:11,29]=lime
        a[8:10,28:30]=light
        a[19,26:28]=lime
        a[19,32:34]=lime
    else:
        for yy,left,right in [(13,21,23),(14,20,24),(15,20,24),(16,20,24),(17,20,24),(18,21,24),(19,21,23)]:
            a[yy,left:right+1]=lime
        a[14:17,22:24]=ink
        a[14,22]=white
        a[18:20,21]=green
        a[11:13,22]=lime
        a[10:12,21:23]=light
        a[20,23:25]=lime
    logical=Image.fromarray(a)
    logical.save(root/f'meepsie-{key}-pixels.png')
    packed=logical.resize((width*11,440),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(1536,1536))
    origin=((1536-width*11)//2,950)
    canvas.paste(packed,origin)
    canvas.save(root/f'meepsie-{key}.png')
    reports[key]={'source':f'raw/meepsie-{key}-coarse-revision.png','source_crop':box,'canvas':[1536,1536],'logical_size':[width,40],'grid_px':11,'origin':origin,'bbox':canvas.getbbox(),'alpha_levels':sorted(set(canvas.getchannel('A').getdata())),'palette_colors':len(logical.getcolors())-1}
(root/'qa.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print(json.dumps(reports,indent=2))
