#!/usr/bin/env python3
"""Gnar's step-1 pack for Codex (assets/source/gnar/MODEL_PROMPTS.md): the step-0 designs at game size, squares drawn
BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_gnar_model.py [--out C:/t/gn_work/gnar_model_pack]

The user's picks (2026-10-20): Mini Gnar 32 game px from his skull cap to his soles, Mega Gnar 44 from his highest crest,
both at PPU 1.5 -> 48 and 66 squares; Mini only 3/4 (「只用做四分之三的测面就行了 完全侧面的不做」), Mega 3/4 and side-on
(「大纳尔可以做完全侧面的」). Three pictures, each on squares of its own size so it fills Codex's 1254 canvas:
  A   Mini's idle, 3/4 front, 48 rows x ~50, 20 px squares,
  M   Mega's idle, 3/4 front, 66 rows x ~95, 12 px squares,
  SM  Mega SIDE-ON facing right, 66 rows x ~113, 10 px squares (one-face-all-frames: M's head turned a little).
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_{A,M,SM}.png (step 0, the look to keep),
2_target_{A,M,SM}.png (cut to the count: size, place, pose - details broken), 3_layout_{A,M,SM}.png (with the grid, the
top / eye / ground lines), 4_head_mini.png / 4_head_mega.png (heads read back, 8x), style/5..7.
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
from design_gnar_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "gnar")
# name -> (rows, px a square, soles' bottom edge, eye row in hd/<name>.png)
PICS = {"A": (48, 20, 1180, 24), "M": (66, 12, 1188, 45), "SM": (66, 10, 1180, 35)}
HEADS = {"4_head_mini.png": ("A", (0, 46, 10, 81)), "4_head_mega.png": ("M", (18, 72, 58, 126))}
GREY = (225, 225, 225)
STYLE = {"5_style_yuumi.png": ("yuumi", "hd_idle"), "6_style_gragas.png": ("gragas", "hd_idle"),
         "7_style_chogath.png": ("chogath", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/gn_work/gnar_model_pack")
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
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   blue the eyes y {eye}   red ground y {sole}   "
                                f"one square = {px} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", f"gnar-{name}.png")),
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
