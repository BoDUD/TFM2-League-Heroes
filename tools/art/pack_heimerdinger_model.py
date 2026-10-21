#!/usr/bin/env python3
"""Heimerdinger's step-1 pack for Codex (assets/source/heimerdinger/MODEL_PROMPTS.md): the step-0 designs at game size,
squares drawn BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_heimerdinger_model.py [--out C:/t/hd_work/heimerdinger_model_pack]

The user's picks (2026-10-21): he is 36 game px from the top of his hair to his soles, the Q turret 20, the apex turret
30, all at PPU 1.5 -> 54, 30 and 45 squares; 3/4 only (no side views). Three pictures, each on squares of its own
size so it fills Codex's 1254 canvas:
  A   his idle, 3/4 front, 54 rows x ~52, 20 px squares (two takes),
  T   the Q turret from the front, 30 rows x ~38, 28 px squares (one take),
  X   the apex turret from the front, 45 rows x ~42, 24 px squares (one take).
The soles' bottom edge is a whole number of squares from the canvas top, so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_{A,T,X}.png (step 0, the look to keep), 2_target_*.png
(cut to the count: size, place, pose - details broken), 3_layout_*.png (with the grid, the top / eye / ground lines),
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
from design_heimerdinger_hd import FROM, lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heimerdinger")
# name -> (rows, px a square, soles' bottom edge, eye row in hd/<name>.png or None)
PICS = {"A": (54, 20, 1180, 60), "T": (30, 28, 1176, None), "X": (45, 24, 1176, None)}
HEAD = (0, 100, 0, 130)   # rows / cols of the hair, the goggles and the moustache in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_vex.png": ("vex", "hd_idle"), "6_style_ziggs.png": ("ziggs", "hd_idle"),
         "7_style_jayce_cannon.png": ("jayce", "hd_c_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/hd_work/heimerdinger_model_pack")
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
        eye = None if eye_row is None else sole - round((d.shape[0] - eye_row) * k) * px
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   " + ("" if eye is None else f"blue the goggles y {eye}   ")
                 + f"red ground y {sole}   one square = {px} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "raw", f"heimerdinger-{FROM[name]}.png")),
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
