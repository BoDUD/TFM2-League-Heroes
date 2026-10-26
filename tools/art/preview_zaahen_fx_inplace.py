"""Zaahen's effects over him at game size (two frames each, the pivot and the ground line as the kit plays them):
the check sheet dist/zaahen_packs/zaahen_fx_inplace.png.

    python tools/art/preview_zaahen_fx_inplace.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT + '/tools/art')
import pack_zaahen_fx as PF  # noqa: E402
import import_zaahen_fx as IZ  # noqa: E402
from import_hwei_fx import anchor  # noqa: E402

man = json.load(open(IZ.SRC + '/manifest.json', encoding='utf-8'))
meta = {e["file"][:-4].replace("zaahen_fx_", ""): e for e in man}
hero = PF.design_1x()                 # 48 x 50 game px
Z = 5
cells = []
for tag, (pic, kind, times, spots) in IZ.FX.items():
    cs = IZ.cells(pic, meta[pic], IZ.SRC)
    anc = anchor(cs, kind)
    picks = [len(cs) // 3, (2 * len(cs)) // 3] if len(cs) > 2 else [len(cs) - 1]
    for k in picks:
        c = cs[k]
        W, H = 110, 100
        can = Image.new('RGBA', (W, H), (104, 112, 72, 255))
        px, py = W // 2, H - 22                        # the pivot; soles 11 under it
        sole = py + 11
        hx = px - hero.shape[1] // 2
        if tag != 'w_glaive':
            can.alpha_composite(Image.fromarray(hero), (hx, sole - hero.shape[0]))
        sx, sy = spots[0]
        ox = round(px + sx - anc[0])
        oy = round(py + sy - anc[1])
        if tag == 'w_glaive':
            ox, oy = 20, H // 2 - c.shape[0] // 2
        can.alpha_composite(Image.fromarray(c), (ox, oy))
        d = ImageDraw.Draw(can)
        d.line([(0, sole), (W, sole)], fill=(150, 60, 60, 255))
        d.text((2, 2), f"{tag} {k + 1}/{len(cs)}", fill=(255, 255, 255, 255))
        cells.append(can.resize((W * Z, H * Z), Image.NEAREST))
cols = 6
rows = (len(cells) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cells[0].width, rows * cells[0].height), (0, 0, 0))
for i, c in enumerate(cells):
    sheet.paste(c.convert('RGB'), ((i % cols) * c.width, (i // cols) * c.height))
out = ROOT + '/dist/zaahen_packs/zaahen_fx_inplace.png'
sheet.save(out)
print(out, sheet.size)
