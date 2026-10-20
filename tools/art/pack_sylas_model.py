#!/usr/bin/env python3
"""Sylas's step-1 pack for Codex (assets/source/sylas/MODEL_PROMPTS.md): design A at game size, 3/4 front only (the user,
2026-10-20: no side view - the idle, the ban-pick card, the one face of every frame and the base of every action),
squares drawn BIG so the image generator's habit of filling the canvas lands on the right count.

    python tools/art/pack_sylas_model.py [--out C:/t/sy_work/sylas_model_pack]

The user's pick (2026-10-20): A (League's long chains), 38 game px hair top to soles, PPU 1.2 -> ROWS = 46 squares;
the chains trail out to the left, so the figure is ~66 squares wide; 16 px squares put it 1056 x 736 px on Codex's own
1254 canvas.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0's A: the look to keep), 2_target.png (A cut to
the count at PX on the canvas: size, place, pose - its details are broken), 3_layout.png (with the grid, the hair top,
eye and ground lines), 4_head.png (A's head read back, 8x), style/7..10.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_sylas_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402
from pack_graves_model import lines  # noqa: E402
import pack_graves_model  # noqa: E402
from review_sylas_size import body_height  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sylas")
PX = 16                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1168           # the soles' bottom edge (73 squares x 16)
ROWS = 46               # hair top to soles: 38 game px x PPU 1.2
EYE_ROW = 23            # his eyes' row in hd/A.png (cols 112 and 125)
HEAD = (0, 44, 86, 134)  # rows / cols of the head (the hair to the gold neck plate) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"7_style_warwick.png": ("warwick", "hd_idle"), "8_style_graves.png": ("graves", "hd_idle"),
         "9_style_darius.png": ("darius", "hd_idle"), "10_style_jayce.png": ("jayce", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/sy_work/sylas_model_pack")
    a = ap.parse_args()
    out = a.out
    pack_graves_model.PX, pack_graves_model.CANVAS = PX, CANVAS   # lines() reads them
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    k = ROWS / body_height(d)
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    op = g[..., 3] > 0
    g = g[np.ix_(np.any(op, 1), np.any(op, 0))]
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    crown = SOLE_Y - ROWS * PX    # the hair top
    eye = SOLE_Y - round((d.shape[0] - EYE_ROW) * k) * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target.png"))
    marks = [(crown, (40, 170, 60, 255)), (eye, (60, 110, 230, 255)), (SOLE_Y, (230, 40, 40, 255))]
    lines(can, marks, f"green hair top y {crown}   blue eyes y {eye}   red ground y {SOLE_Y}"
                      f"   one square = {PX} px   {gw} x {gh} squares").save(os.path.join(out, "3_layout.png"))
    raw = os.path.join(SRC, "codex_picture", "raw")
    shutil.copyfile(lp(os.path.join(raw, "sylas-A-generated.png")), os.path.join(out, "1_picture_A.png"))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}), hair top y {crown}, eyes y {eye}, ground y {SOLE_Y} ->", zp)


if __name__ == "__main__":
    main()
