#!/usr/bin/env python3
"""Poppy's step-1 pack for Codex (assets/source/poppy/MODEL_PROMPTS.md): design B at game size, squares drawn BIG so
the image generator's habit of filling the canvas lands on the right count (league_gangplank round 2: 21 px squares on
1254 came back on the count).

    python tools/art/pack_poppy_model.py [--out %TEMP%/pp_work/poppy_model_pack]

The user's pick (2026-10-18): B (the hammer upright by her near foot), 36 game px pigtail top to soles, PPU 1.3 ->
HAIR_ROWS = 47 squares from the pigtail top to the soles; the haft and pommel rise TOP_ROWS above her hair
(design_poppy_hd.BODY_TOP B scaled), so the whole figure is ROWS squares. At PX px a square on Codex's own 1254
canvas that is ~1134 px: a figure that fills the picture IS the count.
Writes <out>/ (and <out>.zip): MODEL_PROMPTS.md, 1_picture_B.png (step 0's B, the look to keep), 2_target.png (B cut
to the count at PX on the canvas: size, place, pose - its details are broken), 3_layout.png (with the grid, the
pommel-top, pigtail-top, eye and ground lines), 4_head.png (B's head read back, 8x), style/5..8.
"""
import argparse
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_poppy_hd import BODY_TOP, lp  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "poppy")
TMP = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "pp_work")
PX = 21                 # pixels a square on the canvas
CANVAS = 1254
SOLE_Y = 1197           # the soles' bottom edge (57 squares x 21)
HAIR_ROWS = 47          # 36 game px x PPU 1.3
EYE_ROW = 54            # her eyes' row in hd/B.png (violet squares, rows 54-55, cols 64-67 and 75-76)
HEAD = (15, 62, 34, 90)  # rows / cols of the head (pigtails to chin) in hd/B.png
STYLE = {"5_style_cassiopeia.png": ("cassiopeia", "hd_idle"), "6_style_maokai.png": ("maokai", "hd_idle"),
         "7_style_ziggs.png": ("ziggs", "hd_idle"), "8_style_tristana.png": ("tristana", "idle")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "poppy_model_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "B.png"))).convert("RGBA"))
    k = HAIR_ROWS / (d.shape[0] - BODY_TOP["B"])
    g, _ = PD.pixelate(d, k, (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
    op = g[..., 3] > 0
    g = g[np.ix_(np.any(op, 1), np.any(op, 0))]
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    hair = SOLE_Y - HAIR_ROWS * PX
    eye = SOLE_Y - round((d.shape[0] - EYE_ROW) * k) * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    can.save(os.path.join(out, "2_target.png"))
    lay = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    lay.alpha_composite(can)
    dr = ImageDraw.Draw(lay)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(0, CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    dr.line([(0, y0), (CANVAS, y0)], fill=(230, 150, 30, 255), width=3)
    dr.line([(0, hair), (CANVAS, hair)], fill=(40, 170, 60, 255), width=3)
    dr.line([(0, eye), (CANVAS, eye)], fill=(60, 110, 230, 255), width=3)
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    dr.text((12, 12), f"orange pommel top y {y0}   green pigtail top y {hair}   blue eyes y {eye}   red ground y "
                      f"{SOLE_Y}   one square = {PX} px   {gw} x {gh} squares", fill=(40, 40, 40, 255))
    lay.convert("RGB").save(os.path.join(out, "3_layout.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_picture", "poppy-B.png")), os.path.join(out, "1_picture_B.png"))
    r0, r1, c0, c1 = HEAD
    h = d[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), (225, 225, 225, 255))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_head.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "MODEL_PROMPTS.md")), os.path.join(out, "MODEL_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"{gw}x{gh} squares at ({x0},{y0}), pommel y {y0}, pigtails y {hair}, eyes y {eye}, ground y {SOLE_Y} ->", zp)


if __name__ == "__main__":
    main()
