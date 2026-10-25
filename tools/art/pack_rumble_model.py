#!/usr/bin/env python3
"""Rumble's step-1 pack for Codex (assets/source/rumble/MODEL_PROMPTS.md): the step-0 design at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_rumble_model.py [--out outputs/rumble_model_pack]

The pick (2026-10-25, review_rumble_size.py): 44 game px from the tip of his mohawk to the mech's red feet at PPU 1.75
(Yorick's) -> 77 squares (hd/A, the mohawk its first row, 247 rows); about 88 squares across with the mace and the
cannon, so 13 px squares (88 x 13 = 1144 inside Codex's 1254 canvas). The pilot's head is only ~29% of the height in
step 0 (rows 0-72): take 1 keeps the design, take 2 is the "more chibi" B the step-0 pack asked for and did not get
(the head about a third of the height, the mech more compact). The feet's bottom edge is a whole number of squares from
the canvas top (1196 = 92 x 13), so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0, the look to keep), 2_target_A.png (cut to the
count: size, place, pose - details broken), 3_layout_A.png (with the grid, the top / eye / ground lines), 4_head.png (his
head read back, 8x), style/5..7.
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
from design_rumble_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rumble")
# name -> (rows, px a square, lowest point's bottom edge, his eye row in hd/<name>.png)
PICS = {"A": (77, 13, 1196, 56)}
HEAD = (0, 76, 104, 182)   # rows / cols of his head (the mohawk to the chin, both ears, the goggles) in hd/A.png
GREY = (225, 225, 225)
STYLE = {"5_style_kled.png": ("kled", "hd_idle"), "6_style_blitzcrank.png": ("blitzcrank", "idle"),
         "7_style_urgot.png": ("urgot", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "rumble_model_pack"))
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
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "rumble-1.png")), os.path.join(out, f"1_picture_{name}.png"))
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
