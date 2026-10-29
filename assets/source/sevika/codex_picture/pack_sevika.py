from PIL import Image
from pathlib import Path
import json

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR if (SCRIPT_DIR / 'raw').is_dir() else SCRIPT_DIR.parent / 'outputs' / 'sevika-picture'
report = {}
for key, target_height in [('A', 54), ('B', 48)]:
    source = Image.open(ROOT / 'raw' / f'sevika-{key}-generated.png').convert('RGBA')
    mask = source.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    source.putalpha(mask)
    source.paste((0,0,0,0), mask=mask.point(lambda a: 255-a))
    bounds = mask.getbbox()
    body = source.crop(bounds)
    logical_width = round(body.width * target_height / body.height)
    logical = body.resize((logical_width, target_height), Image.Resampling.NEAREST)
    hard_alpha = logical.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    logical = logical.convert('RGB').quantize(colors=48, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert('RGBA')
    logical.putalpha(hard_alpha)
    logical.paste((0,0,0,0), mask=hard_alpha.point(lambda a: 255-a))
    logical.save(ROOT / f'sevika-{key}-pixels.png')
    packed = logical.resize((logical_width * 11, target_height * 11), Image.Resampling.NEAREST)
    # Grid origin is x=0, y=4, so the foot baseline is exactly 1390.
    x = round((1536 - packed.width)/22)*11
    y = 1390 - packed.height
    canvas = Image.new('RGBA', (1536,1536))
    canvas.paste(packed, (x,y))
    canvas.save(ROOT / f'sevika-{key}.png')
    report[key] = {'source_size':source.size, 'source_bbox':bounds, 'logical_size':logical.size, 'pixel_block':11, 'canvas':canvas.size, 'bbox':canvas.getbbox(), 'alpha_values':sorted(set(canvas.getchannel('A').get_flattened_data())), 'palette_limit':48, 'grid_origin':[0,4], 'feet_baseline':1390}

# Comparison is a non-runtime contact sheet, at the same 11px pixel scale.
preview = Image.new('RGB', (1500,750), '#dededb')
for key, left in [('A',70), ('B',790)]:
    canvas=Image.open(ROOT / f'sevika-{key}.png')
    bounds=canvas.getbbox()
    crop=canvas.crop(bounds)
    preview.paste(crop,(left,680-crop.height),crop)
preview.save(ROOT / 'sevika-AB-preview.png')
(ROOT / 'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
