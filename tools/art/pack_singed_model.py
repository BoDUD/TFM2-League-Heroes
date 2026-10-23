#!/usr/bin/env python3
"""Singed's step-1 pack for Codex (assets/source/singed/MODEL_PROMPTS.md): the step-0 design at game size, squares
drawn BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_singed_model.py [--out C:/t/si_work/singed_model_pack]

The user's pick (2026-10-23): 36 game px from the top of his bald head to the soles at PPU 1.5 -> 54 squares; the green
tank rises above the head, so the whole figure (hd/A, the tank cap its first row, the head's outline row 19 of 105) is
66 squares; 3/4 only (no side view). About 49 squares across, so one picture on 16 px squares (66 x 16 = 1056 inside
Codex's 1254 canvas), two takes: A, his idle, 3/4 front, 66 rows x ~49. The soles' bottom edge is a whole number of
squares from the canvas top (1184 = 74 x 16), so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0, the look to keep), 2_target_A.png (cut to
the count: size, place, pose - details broken), 3_layout_A.png (with the grid, the top / eye / ground lines),
4_head.png (his head read back, 8x), style/5..7.
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
from design_singed_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "singed")
# name -> (rows, px a square, soles' bottom edge, his eye row in hd/<name>.png)
PICS = {"A": (66, 16, 1184, 29)}
HEAD = (17, 44, 38, 66)   # rows / cols of his head (the scalp to the scarf) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_drmundo.png": ("drmundo", "hd_idle"), "6_style_urgot.png": ("urgot", "hd_idle"),
         "7_style_gangplank.png": ("gangplank", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/si_work/singed_model_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    report = []
    for name, (rows, px, sole, eye_row) in PICS.items():
        RM.PX, RM.SOLE_Y, RM.ROWS = px, sole, rows
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
        k = rows / d.shape[0]
        g = RM.target(d, k)
        can, x0, y0 = RM.place(g)
        can.save(os.path.join(out, f"2_target_{name}.png"))
        top = sole - round(d.shape[0] * k) * px
        eye = sole - round((d.shape[0] - eye_row) * k) * px
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   blue his eyes y {eye}   red ground y {sole}   "
                 f"one square = {px} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "singed-picture", "raw", f"singed-{name}-generated.png")),
                        os.path.join(out, f"1_picture_{name}.png"))
        report.append(f"{name} {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {px}, top y {top}, eyes y {eye}, "
                      f"ground y {sole}")
    r0, r1, c0, c1 = HEAD
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("\n".join(report), "\n->", zp)


if __name__ == "__main__":
    main()
