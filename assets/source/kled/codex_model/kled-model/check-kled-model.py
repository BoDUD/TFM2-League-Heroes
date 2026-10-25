from pathlib import Path
from PIL import Image
import numpy as np
import json

root = Path('outputs/kled-model')
report = {}
for path in sorted(root.glob('kled-*.png')):
    im = Image.open(path).convert('RGBA')
    rgba = np.asarray(im)
    alpha = rgba[:, :, 3]
    ys, xs = np.where(alpha >= 128)
    bbox = [int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)] if len(xs) else None
    grid_cells = 0
    uniform_cells = 0
    for y in range(0, im.height-13, 14):
        for x in range(0, im.width-13, 14):
            cell = rgba[y:y+14, x:x+14].copy()
            if not np.any(cell[:, :, 3] >= 128):
                continue
            grid_cells += 1
            cell[cell[:, :, 3] == 0] = 0
            uniform_cells += bool(np.all(cell == cell[0, 0]))
    report[path.name] = {
        'size': list(im.size),
        'visible_bbox_alpha128': bbox,
        'alpha_levels': int(len(np.unique(alpha))),
        'hard_alpha_only': bool(np.all((alpha == 0) | (alpha == 255))),
        'exact_14px_uniform_cell_fraction': round(uniform_cells / max(1, grid_cells), 4),
        'target_top': 70 if '-A-' in path.name else 378,
        'target_bottom': 1190,
        'target_size': [1254, 1254],
        'note': 'Measurements only. No resampling, alpha thresholding, repainting, or grid repair applied to deliverables.'
    }
(root/'qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
