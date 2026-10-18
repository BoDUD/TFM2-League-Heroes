#!/usr/bin/env python3
"""Gangplank's step-1 redo pack for Codex (assets/source/gangplank/MODEL_PROMPTS_V2.md): the same design on 50 rows,
squares drawn BIG so the image generator's habit of filling the canvas lands on the right count.

    python tools/art/pack_gangplank_model2.py [--out %TEMP%/gp_work/gangplank_model_pack2]

Round 1 (codex_model, 2026-10-18) came back 81 x 78 squares (~13 px on 1254) for 50 asked: every cut to 50 rows
(design_gangplank_cut.py: even_cut or pixelate) broke the cannon, the blade, the straps and the face into specks at
game size - muddy, so it goes back for an on-grid redraw (skill art-spec "A muddy design"). This round asks for PX px
squares on Codex's own 1254 canvas: 50 rows fill ~1050 px, so a figure that fills the picture IS 50 rows.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS_V2.md, 1_round1_A1.png (round 1's take, the look to keep),
2_target_50.png (the 50-row cut at PX on the canvas: size, place, pose - its details are broken), 3_layout_50.png (with
the grid, hat-top, beard and ground lines), 4_head.png (round 1's head read back, 8x), style/5..8 as round 1.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_gangplank_hd import lp  # noqa: E402
from pack_gangplank_model import STYLE, cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gangplank")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "gp_work")
PX = 21                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1176           # the soles' bottom edge (56 squares x 21)
BEARD_ROW = 15          # the beard's red tie, rows from the hat top in the 50-row cut


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "gangplank_model_pack2"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    g = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelA1_cut.png"))).convert("RGBA"))
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target_50.png"))
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    chin = y0 + BEARD_ROW * PX
    dr.line([(0, y0), (CANVAS, y0)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, chin), (CANVAS, chin)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"green hat top y {y0}   blue beard tie y {chin}   red ground y {SOLE_Y}   one square = {PX} px"
                      f"   {gw} x {gh} squares", fill=(40, 40, 40, 255))
    lay.convert("RGB").save(os.path.join(out, "3_layout_50.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_model", "gangplank-model-A-1.png")), os.path.join(out, "1_round1_A1.png"))
    h = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "modelA1.png"))).convert("RGBA"))[0:28, 14:56]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS_V2.md")), os.path.join(out, "MODEL_PROMPTS_V2.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}), hat top y {y0}, beard y {chin}, ground y {SOLE_Y} ->", zp)


if __name__ == "__main__":
    main()
