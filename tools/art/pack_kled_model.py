#!/usr/bin/env python3
"""Kled's step-1 pack for Codex (assets/source/kled/MODEL_PROMPTS.md): the step-0 design at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_kled_model.py [--out C:/t/kl_work/kled_model_pack]

The user's pick (2026-10-24): 40 game px from the tip of his hat spike to Skaarl's claws at PPU 2.0 -> 80 squares
(hd/A, the spike its first row, 244 rows); A mounted on Skaarl and B on foot with the axe, both 3/4 front, B on A's
scale (hd/B 177 rows -> 58). A is about 55 squares across, B about 61: 14 px squares (80 x 14 = 1120 tall inside
Codex's 1254 canvas; Sejuani's PPU 2.0 redraw took 14 too). Two takes each. The lowest point's bottom edge (A the claws,
B the boots) is a whole number of squares from the canvas top (1190 = 85 x 14), so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_{A,B}.png (step 0, the look to keep), 2_target_{A,B}.png (cut
to the count: size, place, pose - details broken), 3_layout_{A,B}.png (with the grid, the top / eye / ground lines),
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
from design_kled_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kled")
# name -> (rows, px a square, lowest point's bottom edge, his eye row in hd/<name>.png)
PICS = {"A": (80, 14, 1190, 70), "B": (58, 14, 1190, 67)}
HEAD = (0, 100, 10, 112)   # rows / cols of his head (the hat spike to the beard's tip, both ears) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_sejuani.png": ("sejuani", "hd_idle"), "6_style_nunu.png": ("nunu", "hd_idle"),
         "7_style_ziggs.png": ("ziggs", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/kl_work/kled_model_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    report = []
    for name, (rows, px, sole, eye_row) in PICS.items():
        RM.PX, RM.SOLE_Y, RM.ROWS = px, sole, rows
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
        a_rows = Image.open(lp(os.path.join(SRC, "hd", "A.png"))).height
        k = PICS["A"][0] / a_rows   # B on A's scale
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
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "kled-picture", "raw", f"kled-{name}-generated.png")),
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
