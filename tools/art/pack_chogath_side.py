#!/usr/bin/env python3
"""Cho'Gath's side-view redraw pack for Codex (assets/source/chogath/SIDE_PROMPTS.md): step 1's side takes were drawn
off the grid (side-1 ~7.5 px squares, 115 rows; side-2 ~11 px, 71 rows), and brought to 46 rows they broke (cut: a
huge head on a crushed body; voted: muddy). The user, 2026-10-19: Codex redraws the side ON the grid.

    python tools/art/pack_chogath_side.py [--out %TEMP%/cg_work/chogath_side_pack]

Writes <out>/ (and <out>.zip): SIDE_PROMPTS.md, 1_side_look.png (step 1's side-1 as drawn: the look and pose to keep),
2_target.png (side-1 voted down to 46 rows, 16 px a square on the 1254 canvas: size, place, pose - its details are
muddy), 3_layout.png (with the grid, the top and ground lines), 4_idle_head.png (the approved idle's head, 8x: drawn
square for square in the side view), 5_idle.png (the approved idle A-1 at 16 px on the canvas: colours and density),
style/7..10 (as the step-1 pack).
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
import design_chogath_model as M  # noqa: E402
from design_chogath_hd import lp  # noqa: E402
from pack_chogath_model import CANVAS, GREY, PX, ROWS, SOLE_Y, STYLE, TMP, lines  # noqa: E402
from pack_gangplank_model import cut, up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "chogath")
HEAD = (20, 41, 41, 65)   # rows / cols of the head (crown plates to jaw, both tusks) in hd/idle.png
EYE_ROW = 26              # the idle's eyes (cyan, rows 25-27)


def place(g, x_mid=None):
    """A figure of game squares at PX on the canvas, soles on SOLE_Y, centred: (canvas, x0, y0)."""
    gh, gw = g.shape[:2]
    x0 = (CANVAS // PX - gw) // 2 * PX
    y0 = SOLE_Y - gh * PX
    can = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    can.paste(Image.fromarray(up(g, PX)), (x0, y0))
    return can, x0, y0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(TMP, "chogath_side_pack"))
    a = ap.parse_args()
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "style"))
    side = M.voted("side-1")
    can, x0, y0 = place(side)
    can.save(os.path.join(out, "2_target.png"))
    eye = SOLE_Y - (ROWS - EYE_ROW) * PX
    lines(can, y0, eye, f"SIDE: green top y {y0}   blue eyes y {eye}   red ground y {SOLE_Y}   one square = {PX} px   "
                       f"{side.shape[1]} x {side.shape[0]} squares").save(os.path.join(out, "3_layout.png"))
    shutil.copyfile(lp(os.path.join(SRC, "codex_model", "chogath-model", "chogath-model-side-1.png")),
                    os.path.join(out, "1_side_look.png"))
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    r0, r1, c0, c1 = HEAD
    h = idle[r0:r1, c0:c1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out, "4_idle_head.png"))
    ic, _, _ = place(idle)
    ic.save(os.path.join(out, "5_idle.png"))
    for fname, (hero, tag) in STYLE.items():
        cut(hero, tag, os.path.join(out, "style", fname))
    shutil.copyfile(lp(os.path.join(SRC, "SIDE_PROMPTS.md")), os.path.join(out, "SIDE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(f"side {side.shape[1]}x{side.shape[0]} squares at ({x0},{y0}); head {h.shape[1]}x{h.shape[0]} ->", zp)


if __name__ == "__main__":
    main()
