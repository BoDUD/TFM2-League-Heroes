#!/usr/bin/env python3
"""Warwick's step-1 pack for Codex (assets/source/warwick/MODEL_PROMPTS.md): design A at game size, 3/4 front only (the
user, 2026-10-20: 「不做侧面 只做四分之三的侧面」 - the idle, the ban-pick card, the one face of every frame and the base
of every action), squares drawn BIG so the image generator's habit of filling the canvas lands on the right count.

    python tools/art/pack_warwick_model.py [--out C:/t/ww_work/warwick_model_pack]

The user's pick (2026-10-20): A (hunched as in League), 46 game px spike top to soles (「不选42的 选大一号的那个」), PPU 1.5 -> ROWS = 69 squares;
the tail reaches out behind, so the figure is ~94 squares wide; 12 px squares put it 828 x 1128 px on Codex's own 1254
canvas.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0's A: the look to keep), 2_target.png (A cut to
the count at PX on the canvas: size, place, pose - its details are broken), 3_layout.png (with the grid, the spike top,
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
from design_warwick_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402
from pack_graves_model import lines  # noqa: E402
import pack_graves_model  # noqa: E402
from review_warwick_size import body_height  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "warwick")
PX = 12                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1176           # the soles' bottom edge (98 squares x 12)
ROWS = 69               # spike top to soles: 46 game px x PPU 1.5
EYE_ROW = 57            # his eyes' row in hd/A.png (cols 126 and 141)
HEAD = (14, 82, 84, 160)  # rows / cols of the head (the spike's vial to the jaw, both ears) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"7_style_graves.png": ("graves", "hd_idle"), "8_style_vex.png": ("vex", "hd_idle"),
         "9_style_volibear.png": ("volibear", "hd_idle"), "10_style_nasus.png": ("nasus", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ww_work/warwick_model_pack")
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
    crown = SOLE_Y - ROWS * PX    # the spike top
    eye = SOLE_Y - round((d.shape[0] - EYE_ROW) * k) * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target.png"))
    marks = [(crown, (40, 170, 60, 255)), (eye, (60, 110, 230, 255)), (SOLE_Y, (230, 40, 40, 255))]
    lines(can, marks, f"green spike top y {crown}   blue eyes y {eye}   red ground y {SOLE_Y}"
                      f"   one square = {PX} px   {gw} x {gh} squares").save(os.path.join(out, "3_layout.png"))
    raw = os.path.join(SRC, "codex_picture", "raw")
    shutil.copyfile(lp(os.path.join(raw, "warwick-A-original.png")), os.path.join(out, "1_picture_A.png"))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}), spike top y {crown}, eyes y {eye}, ground y {SOLE_Y} ->", zp)


if __name__ == "__main__":
    main()
