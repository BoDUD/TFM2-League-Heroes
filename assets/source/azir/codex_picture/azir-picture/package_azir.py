import sys, json, shutil, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, r'D:/TFM2-Workshop/repo/.claude/worktrees/azir/.claude/skills/tfm2-hero-mod/scripts')
from regrid import regrid
base=Path(__file__).resolve().parent.parent
out=base/'outputs/azir-picture'
manifest=json.loads((base/'work/azir-manifest.json').read_text(encoding='utf-8-sig'))
metrics={}
tiles=[]
for key,src in manifest.items():
    raw=out/'raw'/f'{key}.png'
    raw.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,raw)
    if key.startswith('rejected'): continue
    im=Image.open(src).convert('RGBA')
    pixels,pitch,bounds=regrid(np.asarray(im))
    logical=Image.fromarray(pixels)
    measured_size=logical.size
    target_h={'A':84,'SA':84,'T':55,'U':64,'US':52,'D':66}[key]
    logical=logical.resize((round(logical.width*target_h/logical.height),target_h),Image.Resampling.NEAREST)
    (out/'logical').mkdir(exist_ok=True)
    logical.save(out/'logical'/f'azir-{key}.png')
    # Packaging only: preserve generated squares, expand each read-back square
    # to exactly 11x11. No repainted anatomy or geometric substitute model.
    sprite=logical.resize((logical.width*11,logical.height*11),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(1536,1536))
    x=768-sprite.width//2
    y=1390-sprite.height
    assert x>0 and y>0 and x+sprite.width<1536
    canvas.paste(sprite,(x,y))
    canvas.save(out/f'azir-{key}.png')
    a=np.asarray(canvas)
    assert set(np.unique(a[:,:,3])).issubset({0,255})
    metrics[key]={'raw_size':im.size,'measured_raw_pitch':pitch,'readback_size':measured_size,'logical_size':logical.size,'packed_bbox':canvas.getbbox(),'alpha':[0,255],'scale':11}
    tile=Image.new('RGB',(400,500),(225,225,225))
    preview=logical.resize((logical.width*5,logical.height*5),Image.Resampling.NEAREST)
    tile.paste(preview,(200-preview.width//2,465-preview.height),preview)
    ImageDraw.Draw(tile).text((18,15),key,fill=(25,25,25))
    tiles.append(tile)
contact=Image.new('RGB',(1200,1000),(225,225,225))
for i,tile in enumerate(tiles):contact.paste(tile,((i%3)*400,(i//3)*500))
contact.save(out/'preview.png')
(out/'qa.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
print(json.dumps(metrics,indent=2))
