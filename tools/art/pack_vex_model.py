#!/usr/bin/env python3
"""Vex's step-1 pack for Codex (assets/source/vex/MODEL_PROMPTS.md): the step-0 designs at game size, squares drawn BIG
so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_vex_model.py [--out C:/t/vx_work/vex_model_pack]

The user's pick (2026-10-20): picture A (the Shadow risen behind her), 34 game px from her ear tips to her soles at PPU
1.5 -> her own 51 squares; the risen Shadow stands 18 of step 0's 94 rows above her, so the whole picture is ROWS = 63
squares. A is 75 x 94 at step 0 (50 squares wide at the count), so a square is PX = 17 px: the figure is about
850 x 1071 on Codex's own 1254 canvas. Two pictures of the same Vex and Shadow at that count (side-view-design: every
action is drawn from the side view):
  A   the idle, 3/4 front (step 0's A cut to the count: 2_target_A.png),
  SA  SIDE-ON facing right (step 0's SA cut to the count: 2_target_SA.png).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png / 1_picture_SA.png (step 0, the look to keep),
2_target_A.png / 2_target_SA.png (cut to the count at PX: size, place, pose - details broken), 3_layout_A.png /
3_layout_SA.png (with the grid, her ear-tip / eye / ground lines), 4_head.png (A's head read back, 8x), style/5..7.
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
import pack_rammus_model as RM  # noqa: E402
from design_vex_hd import body_top, lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "vex")
PX = 17                 # pixels a square on the canvas
SOLE_Y = 1190           # the soles' bottom edge (70 squares x 17)
ROWS = 63               # the risen Shadow's ear tips to her soles (her own 51 = 34 game px x PPU 1.5)
EYE_ROW = {"A": 50, "SA": 50}    # her eyes' row in hd/{A,SA}.png (magenta: A rows 49-51, SA row 47 and the lid below)
HEAD = (18, 72, 28, 75)  # rows / cols of her hood, ears, face and hair in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_zoe.png": ("zoe", "hd_idle"), "6_style_yuumi.png": ("yuumi", "hd_idle"),
         "7_style_nocturne.png": ("nocturne", "idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/vx_work/vex_model_pack")
    a = ap.parse_args()
    RM.PX, RM.SOLE_Y, RM.ROWS = PX, SOLE_Y, ROWS
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    tops = body_top()
    report = []
    for name in ("A", "SA"):
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
        k = ROWS / d.shape[0]
        g = RM.target(d, k)
        can, x0, y0 = RM.place(g)
        can.save(os.path.join(out, f"2_target_{name}.png"))
        ear = SOLE_Y - round((d.shape[0] - tops[name]) * k) * PX
        eye = SOLE_Y - round((d.shape[0] - EYE_ROW[name]) * k) * PX
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, ear, eye, f"{name}: orange her ear tips y {ear}   blue her eyes y {eye}   red ground y {SOLE_Y}   "
                                f"Shadow top y {y0}   one square = {PX} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "vex-picture", f"vex-{name}.png")),
                        os.path.join(out, f"1_picture_{name}.png"))
        report.append(f"{name} {g.shape[1]}x{g.shape[0]} at ({x0},{y0}), ear tips y {ear}, eyes y {eye}")
    A = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    r0, r1, c0, c1 = HEAD
    h = A[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("; ".join(report), "; ground y", SOLE_Y, "->", zp)


if __name__ == "__main__":
    main()
