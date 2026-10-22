#!/usr/bin/env python3
"""K'Sante's step-1 pack for Codex (assets/source/ksante/MODEL_PROMPTS.md): the step-0 designs at game size, squares
drawn BIG so the image generator's habit of filling the canvas lands on the right count (Gwen's way).

    python tools/art/pack_ksante_model.py [--out C:/t/ks_work/ksante_model_pack]

The user's picks (2026-10-22): 「奎桑提用陀斧顶到脚底 48 游戏像素，PPU 1.5，只做四分之三侧面」 - 48 game px from the
ntofo tops to the soles at PPU 1.5 -> 72 squares; All Out on the same scale (57 / 56 of it, step 0's sizes) -> 73
squares; 3/4 only (no side views). Two pictures, each on squares of its own size so it fills Codex's 1254 canvas:
  A   the base idle, 3/4 front, 72 rows x ~68, 15 px squares (two takes),
  O   the All Out idle, 3/4 front, 73 rows x ~103, 11 px squares (two takes).
The soles' bottom edge is a whole number of squares from the canvas top, so the grid starts at the corner.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_{A,O}.png (step 0's raw drafts, the look to keep - Codex's
own 11 px export lost the face and the crimson coat), 2_target_*.png (cut to the count: size, place, pose - details
broken), 3_layout_*.png (with the grid, the top / eye / ground lines), 4_head_{base,allout}.png (heads read back, 8x),
style/5..7.
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
from design_ksante_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ksante")
# name -> (rows, px a square, soles' bottom edge, eye row in hd/<name>.png)
PICS = {"A": (72, 15, 1185, 23), "O": (73, 11, 1188, 20)}
HEADS = {"4_head_base.png": ("A", (10, 36, 15, 55)), "4_head_allout.png": ("O", (0, 32, 45, 95))}
GREY = (225, 225, 225)
STYLE = {"5_style_braum.png": ("braum", "hd_idle"), "6_style_ornn.png": ("ornn", "hd_idle"),
         "7_style_galio.png": ("galio", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ks_work/ksante_model_pack")
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
        shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "raw", f"ksante-{name}.png")),
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
