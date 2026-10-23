#!/usr/bin/env python3
"""Aurora's step-1 pack for Codex (assets/source/aurora/MODEL_PROMPTS.md): the step-0 design at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_aurora_model.py [--out C:/t/au_work/aurora_model_pack]

The user's picks (2026-10-23): hat top to soles 38 game px, PPU 1.5, 3/4 only - 57 squares from the hat's crown to the
soles; the rabbit ears above it on the same scale (hd/A: hat from row HAT of 110 -> 72 rows in all). One picture, two
takes, on PX px squares so it fills Codex's 1254 canvas. The soles' bottom edge is a whole number of squares from the
canvas top, so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0's raw draft, the look to keep), 2_target_A.png
(cut to the count: size, place, pose - details broken), 3_layout_A.png (with the grid, the hat top / eye / ground
lines), 4_head_A.png (the head read back, 8x), style/5..8.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_rammus_model as RM  # noqa: E402
from design_aurora_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aurora")
BODY_ROWS = 57          # hat top to soles
HAIR, EYE = 23, 46      # rows in hd/A.png (110 rows): the hat crown's top, the eyes
PX, SOLE = 16, 1200     # px a square, the soles' bottom edge (75 squares)
HEAD = (18, 64, 6, 54)  # rows, cols of hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_neeko.png": ("neeko", "hd_idle"), "6_style_zoe.png": ("zoe", "hd_idle"),
         "7_style_yuumi.png": ("yuumi", "hd_idle"), "8_style_hwei.png": ("hwei", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/au_work/aurora_model_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    k = BODY_ROWS / (d.shape[0] - HAIR)
    RM.PX, RM.SOLE_Y, RM.ROWS = PX, SOLE, round(d.shape[0] * k)
    g = RM.target(d, k)
    can, x0, y0 = RM.place(g)
    assert x0 >= PX and x0 + g.shape[1] * PX <= RM.CANVAS - PX and y0 >= PX, (x0, y0, g.shape)
    can.save(os.path.join(out, "2_target_A.png"))
    hair = SOLE - BODY_ROWS * PX
    eye = SOLE - round((d.shape[0] - EYE) * k) * PX
    lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    RM.lines(lay, hair, eye, f"A: orange the hat's top y {hair}   blue the eyes y {eye}   red ground y {SOLE}   "
                             f"one square = {PX} px   {g.shape[1]} x {g.shape[0]} squares (ear tips y {y0})")
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "aurora-picture", "raw", "aurora-A-final.png")),
                    os.path.join(out, "1_picture_A.png"))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head_A.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"A {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {PX}, hat y {hair}, eyes y {eye}, ground y {SOLE} ->", zp)


if __name__ == "__main__":
    main()
