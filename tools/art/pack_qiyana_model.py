#!/usr/bin/env python3
"""Qiyana's step-1 pack for Codex (assets/source/qiyana/MODEL_PROMPTS.md): the step-0 design at game size, squares
drawn BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_qiyana_model.py [--out C:/t/qy_work/qiyana_model_pack]

The user's picks (2026-10-22): 40 game px from her crest's tip to her soles, PPU 1.5, 3/4 only (no side view) -> 60
squares. One picture, two takes: A, her relaxed idle with the ring blade beside her, 60 rows x ~50, 18 px squares on
Codex's 1254 canvas. The soles' bottom edge is a whole number of squares from the canvas top, so the grid starts at
the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0's raw draft, the look to keep), 2_target_A.png
(cut to the count: size, place, pose - details broken), 3_layout_A.png (with the grid, the top / eye / ground lines),
4_head_A.png (the head read back, 8x), style/5..8.
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
from design_qiyana_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "qiyana")
A_ROWS = 60
# name -> (px a square, soles' bottom edge, eye row in hd/<name>.png)
PICS = {"A": (18, 1188, 42)}
HEADS = {"4_head_A.png": ("A", (0, 62, 52, 114))}   # file -> (design, (row0, row1, col0, col1)): crest, hair, face
GREY = (225, 225, 225)
STYLE = {"5_style_nilah.png": ("nilah", "hd_idle"), "6_style_irelia.png": ("irelia", "hd_idle"),
         "7_style_neeko.png": ("neeko", "hd_idle"), "8_style_vex.png": ("vex", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/qy_work/qiyana_model_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    report = []
    for name, (px, sole, eye_row) in PICS.items():
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
        k = A_ROWS / d.shape[0]
        rows = A_ROWS
        RM.PX, RM.SOLE_Y, RM.ROWS = px, sole, rows
        g = RM.target(d, k)
        can, x0, y0 = RM.place(g)
        assert x0 >= px and x0 + g.shape[1] * px <= RM.CANVAS - px, (name, x0, g.shape)
        can.save(os.path.join(out, f"2_target_{name}.png"))
        top = sole - rows * px
        eye = sole - round((d.shape[0] - eye_row) * k) * px
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   blue the eyes y {eye}   red ground y {sole}   "
                                f"one square = {px} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "raw", f"qiyana-{name}.png")),
                        os.path.join(out, f"1_picture_{name}.png"))
        report.append(f"{name} {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {px}, top y {top}, eyes y {eye}, "
                      f"ground y {sole}")
    for fname, (name, (r0, r1, c0, c1)) in HEADS.items():
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
        h = d[r0:r1, c0:c1]
        hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
        hb.alpha_composite(Image.fromarray(up(h, 8)))
        hb.convert("RGB").save(os.path.join(out, fname))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("\n".join(report), "\n->", zp)


if __name__ == "__main__":
    main()
