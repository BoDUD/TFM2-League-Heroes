from pathlib import Path
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent if Path(__file__).resolve().parent.name == 'raptor-picture' else ROOT / 'outputs' / 'raptor-picture'
RAW = OUT / 'raw'
RAW.mkdir(parents=True, exist_ok=True)

def export(source, variant, width, height):
    shutil.copy2(source, RAW / f'raptor-{variant}-raw.png')
    im = Image.open(source).convert('RGBA')
    a = np.array(im)
    mask = a[:, :, 3] >= 128
    a[:, :, 3] = mask.astype('uint8') * 255
    a[~mask] = 0
    clean = Image.fromarray(a)
    cropped = clean.crop(clean.getbbox())
    small = cropped.resize((width, height), Image.Resampling.NEAREST)
    arr = np.array(small)
    opaque = arr[:, :, 3] >= 128
    rgb = Image.fromarray(arr[:, :, :3])
    arr[:, :, :3] = np.array(rgb)
    arr[:, :, 3] = opaque.astype('uint8') * 255
    arr[~opaque] = 0
    small = Image.fromarray(arr)
    small.save(OUT / f'raptor-{variant}-pixels.png')
    sprite = small.resize((width * 11, height * 11), Image.Resampling.NEAREST)
    canvas = Image.new('RGBA', (1536, 1536))
    x = ((1536 // 11 - width) // 2) * 11
    y = (126 - height) * 11
    canvas.paste(sprite, (x, y))
    canvas.save(OUT / f'raptor-{variant}.png')
    data = np.array(canvas)
    assert set(np.unique(data[:, :, 3])) == {0, 255}
    for yy in range(y, y + height * 11, 11):
        for xx in range(x, x + width * 11, 11):
            assert np.all(data[yy:yy+11, xx:xx+11] == data[yy, xx])
    return {'canvas': [1536,1536], 'logical_size': [width,height], 'grid_px':11,
            'grid_origin':[0,0], 'sprite_origin':[x,y], 'alpha_values':[0,255],
            'visible_bbox': canvas.getbbox(), 'source_size':list(im.size),
            'route':'AI-generated art, uniform grid export; original preserved'}

if __name__ == '__main__':
    import sys
    report = {'A': export(Path(sys.argv[1]), 'A', 49,38),
              'B': export(Path(sys.argv[2]), 'B',60,35)}
    (OUT / 'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    preview = Image.new('RGB',(1040,500),'#e3e1de')
    d = ImageDraw.Draw(preview)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
    for i,variant in enumerate(('A','B')):
        icon = Image.open(OUT/f'raptor-{variant}-pixels.png').convert('RGBA')
        icon = icon.resize((icon.width*7,icon.height*7),Image.Resampling.NEAREST)
        preview.paste(icon,(i*520+(520-icon.width)//2,120+(280-icon.height)),icon)
        d.text((i*520+28,28),f'{variant} / '+('3-4 view' if variant=='A' else 'side view'),fill='#272530',font=font)
    preview.save(OUT/'preview.png')
    print(json.dumps(report,ensure_ascii=False))
