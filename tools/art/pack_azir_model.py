#!/usr/bin/env python3
"""Azir's step-1 pack for Codex (assets/source/azir/MODEL_PROMPTS.md): the step-0 designs at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_azir_model.py [--out C:/t/az_work/azir_model_pack]

The user's picks (2026-10-23): Azir 38 game px from his helmet's crest to his soles at PPU 1.5 -> 57 squares; 3/4 only;
the summons as the size review showed them - the soldier 36 game px tall (spear tip to soles) -> 54 squares, R's guard
from the SIDE 32 -> 48, the Sun Disc 48 -> 72 (all PPU 1.5, effect pictures). Step 0's sceptre rose 23 rows over the
crest; SHORT cuts SHORTEN rows of its shaft (under the gem, over his hand) so its head is about 14 squares over the crest.
Five pictures, each on its own square size so it fills Codex's 1254 canvas:
  A   his idle, 3/4 front, ~71 rows (two takes),
  T   the sand soldier from the front, 54 rows,
  US  the Imperial Guard from the side facing right (the left-facing one is its mirror, made by Claude), 48 rows,
  D   the Sun Disc from the front, 72 rows.
The soles' bottom edge is a whole number of squares from the canvas top, so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_*.png (step 0, the look to keep), 2_target_*.png (cut to the
count: size, place, pose - details broken), 3_layout_*.png (with the grid, the top / eye / ground lines), 4_head.png (his
helmet read back, 8x), style/5..7.
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
from design_azir_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "azir")
# name -> (rows, px a square, soles' bottom edge, eye row in the (shortened) design or None)
PICS = {"A": (71, 16, 1190, 26), "T": (54, 20, 1190, None), "US": (48, 22, 1188, None), "D": (72, 16, 1184, None)}
SHORT = (37, 9, 20)   # A: the sceptre's shaft rows 37.. (9 of them) cut in columns 0..13; cols 14..19 slide over the body
HEAD = (13, 42, 19, 50)   # rows / cols of the helmet (crest, cheek wings, the eye) in the shortened A
GREY = (225, 225, 225)
STYLE = {"5_style_xerath.png": ("xerath", "hd_idle"), "6_style_nasus.png": ("nasus", "hd_idle"),
         "7_style_ksante.png": ("ksante", "hd_idle")}


def shorten(d):
    """hd/A with SHORT's rows of the sceptre's shaft taken out: everything above them in the sceptre's columns slides
    down; the body's columns keep their pixels where the slid sceptre is clear."""
    r0, n, c1 = SHORT
    out = d.copy()
    out[:r0, :c1] = 0
    out[:r0 + n, :14] = 0
    top = d[:r0, :c1]
    dst = out[n:r0 + n, :c1]
    on = top[..., 3] > 0
    dst[on] = top[on]
    ys = np.nonzero(out[..., 3].any(axis=1))[0]
    return out[ys[0]:]


def design(name):
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{name}.png"))).convert("RGBA"))
    return shorten(d) if name == "A" else d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/az_work/azir_model_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    report = []
    for name, (rows, px, sole, eye_row) in PICS.items():
        RM.PX, RM.SOLE_Y, RM.ROWS = px, sole, rows
        d = design(name)
        k = rows / d.shape[0]
        g = RM.target(d, k)
        can, x0, y0 = RM.place(g)
        can.save(os.path.join(out, f"2_target_{name}.png"))
        top = sole - round(d.shape[0] * k) * px
        eye = None if eye_row is None else sole - round((d.shape[0] - eye_row) * k) * px
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   " + ("" if eye is None else f"blue the eyes y {eye}   ")
                 + f"red ground y {sole}   one square = {px} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "azir-picture", f"azir-{name}.png")),
                        os.path.join(out, f"1_picture_{name}.png"))
        report.append(f"{name} {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {px}, top y {top}, eyes y {eye}, "
                      f"ground y {sole}")
    r0, r1, c0, c1 = HEAD
    h = design("A")[r0:r1, c0:c1]
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
