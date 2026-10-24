#!/usr/bin/env python3
"""Sejuani's step-1b pack for Codex (assets/source/sejuani/REDRAW_PROMPTS.md): the picked designs redrawn finer, for a
higher PPU at the same height.

    python tools/art/pack_sejuani_redraw.py [--out C:/t/se_work/sejuani_redraw_pack]

The user picked A-2 (the idle, hd/idle.png 61x53, its face redrawn) and B-1 (the run / Q, hd/run.png 63x56) on 2026-10-24,
then asked for a higher PPU (「先调高ppu像素吧」): PPU 2.0 at the same 36 game px from the ice horn's tip to the hooves ->
A 72 rows; B on A's scale (56 x 72 / 53 -> 76). A is then about 83 squares across, B about 86: 14 px squares (86 x 14 =
1204 inside Codex's 1254 canvas; 15 px would not fit). Two takes each. The lowest point's bottom edge is a whole number
of squares from the canvas top (1190 = 85 x 14), so the grid starts at the corner.
Writes <out>/ (and <out>.zip): REDRAW_PROMPTS.md, 1_picture_{A,B}.png (the picked step-1 takes as Codex drew them: the
look, the proportions and the pose to keep), 2_target_{A,B}.png (the picked designs brought to the new count: size and
place - blocky), 3_layout_{A,B}.png (with the grid, the top / eye / ground lines), 4_face_{A,B}.png (the redrawn faces,
12x: where both eyes and the mouth go), style/5..7.
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
from design_sejuani_hd import lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sejuani")
A_ROWS = 72      # 36 game px x PPU 2.0
PX = 14
SOLE = 1190      # 85 x 14
# name -> (design, Codex's take, her eye row in the design, the face box in the design: rows, cols)
PICS = {"A": ("idle", "A-2", 12, (6, 17, 30, 42)), "B": ("run", "B-1", 17, (11, 22, 40, 52))}
GREY = (225, 225, 225)
STYLE = {"5_style_nunu.png": ("nunu", "idle"), "6_style_volibear.png": ("volibear", "hd_idle"),
         "7_style_braum.png": ("braum", "hd_idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/se_work/sejuani_redraw_pack")
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    RM.PX, RM.SOLE_Y = PX, SOLE
    a_rows = Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).height
    k = A_ROWS / a_rows   # B on A's scale
    report = []
    for name, (design, take, eye_row, (r0, r1, c0, c1)) in PICS.items():
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", f"{design}.png"))).convert("RGBA"))
        RM.ROWS = round(d.shape[0] * k)
        g = RM.target(d, k)
        can, x0, y0 = RM.place(g)
        can.save(os.path.join(out, f"2_target_{name}.png"))
        top = SOLE - g.shape[0] * PX
        eye = SOLE - round((d.shape[0] - eye_row) * k) * PX
        lay = Image.new("RGBA", (RM.CANVAS, RM.CANVAS), (255, 255, 255, 255))
        lay.alpha_composite(can)
        RM.lines(lay, top, eye, f"{name}: orange the top y {top}   blue her eyes y {eye}   red ground y {SOLE}   "
                 f"one square = {PX} px   {g.shape[1]} x {g.shape[0]} squares")
        lay.convert("RGB").save(os.path.join(out, f"3_layout_{name}.png"))
        shutil.copyfile(lp(os.path.join(SRC, "codex_model", "sejuani-model", "raw", f"sejuani-{take}-original.png")),
                        os.path.join(out, f"1_picture_{name}.png"))
        h = d[r0:r1, c0:c1]
        hb = Image.new("RGBA", (h.shape[1] * 12, h.shape[0] * 12), GREY + (255,))
        hb.alpha_composite(Image.fromarray(up(h, 12)))
        hb.convert("RGB").save(os.path.join(out, f"4_face_{name}.png"))
        report.append(f"{name} {g.shape[1]}x{g.shape[0]} at ({x0},{y0}) px {PX}, top y {top}, eyes y {eye}, ground y {SOLE}")
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "REDRAW_PROMPTS.md")), os.path.join(out, "REDRAW_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print("\n".join(report), "\n->", zp)


if __name__ == "__main__":
    main()
