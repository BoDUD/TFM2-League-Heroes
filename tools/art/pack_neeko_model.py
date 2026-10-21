#!/usr/bin/env python3
"""Neeko's step-1 pack for Codex (assets/source/neeko/MODEL_PROMPTS.md): the step-0 design at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_neeko_model.py [--out C:/t/nk_work/neeko_model_pack]

The user's picks (2026-10-21): 40 game px from her highest quill to her soles at PPU 2.5 -> 100 rows; the head BIGGER
than step 0's slim take (chibi: hair and face about a third of her height, the quills on top); 3/4 view only.
Step 0's head (rows 0..NECK of hd/A.png, quills, hair and face) is enlarged HEAD_K times about the neck before the cut,
so the target shows the new proportions. One picture, two takes: A her idle, 3/4 front, 100 rows x ~50, 11 px
squares on Codex's 1254 canvas. The soles' bottom edge is a whole number of squares from the canvas top, so the grid
starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_A.png (step 0, the look to keep), 2_target_A.png (cut to
the count with the big head: size, place, pose - details broken), 3_layout_A.png (with the grid, the top / eye / ground
lines), 4_head.png (step 0's head read back, 8x), style/5..7.
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
from design_neeko_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "neeko")
ROWS, PX, SOLE = 100, 11, 1210
NECK, NECK_X, HEAD_K = 66, 61, 1.35     # step 0's chin line, the neck's column, the head's enlargement
EYE_ROW = 48                            # her eyes in hd/A.png (before the enlargement)
HEAD = (14, 72, 30, 92)                 # rows, cols of step 0's head for 4_head.png
GREY = (225, 225, 225)
STYLE = {"5_style_zoe.png": ("zoe", "hd_idle"), "6_style_seraphine.png": ("seraphine", "idle"),
         "7_style_zyra.png": ("zyra", "hd_idle")}


def big_head(d):
    """hd/A.png with rows 0..NECK enlarged HEAD_K times about (NECK_X, NECK), the body below unchanged."""
    head = Image.fromarray(d[:NECK])
    hw, hh = round(head.width * HEAD_K), round(head.height * HEAD_K)
    head = head.resize((hw, hh), Image.NEAREST)
    left = max(0, round(NECK_X * HEAD_K) - NECK_X)
    right = max(0, hw - left - d.shape[1])
    W, H = d.shape[1] + left + right, hh + d.shape[0] - NECK
    can = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    can.alpha_composite(Image.fromarray(np.ascontiguousarray(d[NECK:])), (left, hh))
    can.alpha_composite(head, (left + NECK_X - round(NECK_X * HEAD_K), 0))
    a = np.asarray(can)
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], round(EYE_ROW * HEAD_K) - ys.min()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/nk_work/neeko_model_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    RM.PX, RM.SOLE_Y, RM.ROWS = PX, SOLE, ROWS
    d0 = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "A.png"))).convert("RGBA"))
    d, eye_row = big_head(d0)
    k = ROWS / d.shape[0]
    g = RM.target(d, k)
    can, x0, y0 = RM.place(g)
    can.save(os.path.join(out, "2_target_A.png"))
    top = SOLE - round(d.shape[0] * k) * PX
    eye = SOLE - round((d.shape[0] - eye_row) * k) * PX
    lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    RM.lines(lay, top, eye, f"A: orange the top y {top}   blue the eyes y {eye}   red ground y {SOLE}   "
                            f"one square = {PX} px   {g.shape[1]} x {g.shape[0]} squares")
    lay.convert("RGB").save(os.path.join(out, "3_layout_A.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "neeko-A.png")), os.path.join(out, "1_picture_A.png"))
    r0, r1, c0, c1 = HEAD
    h = d0[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"A {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {PX}, top y {top}, eyes y {eye}, ground y {SOLE}\n->", zp)


if __name__ == "__main__":
    main()
