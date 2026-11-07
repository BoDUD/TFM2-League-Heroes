#!/usr/bin/env python3
"""Baron Nashor's game-size design: the user's pick of step 0 at its height, on the spider legs the user picked.

    python tools/art/design_baronnashor_model.py   # writes assets/source/baronnashor/hd/idle.png (+ _8x, _face12x)

The user's pick (2026-11-03, 「A1 46」): A-1 (hd/A-1.png, Codex's picture A - the S-curved idle on the two legs the
user had it add - read on its own 11 px squares: 58 x 94) at 46 game px from the crest tips to its soles, PPU 94 / 46
= 2.04 -> A-1's own 94 rows, kept 1:1 (no reduction).
2026-11-07 the user asked for TFT's spider legs (「大龙的腿应该是这样的」) and picked L6 (「L6（每边 3 条）」): Codex
(assets/source/baronnashor/codex_legs, LEGS_PROMPT.md) drew A-1 at 11 px a square on the 1254 canvas, its two hind
legs and ivory feet swapped for a short segmented column and three thin spider legs a side. The idle is L6 read back on
those squares (one pixel a square: its centre), every colour put on A-1's palette (nearest in Lab: Codex's near-black
outline and the teal it ran down from the belly to the column), 80 x 94: the same 94 rows, L6_LEFT columns more on
the left (the legs spread wider than the old feet) and the rest on the right. A-1's own squares above BODY_ROWS (all but
the hips) come back unchanged (checked). Its face (FACE_BOX, shown at 12x): the blue head, the yellow diamond eye and
the side eyes, the red mouth, the ivory tusks; nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pixel_down as PD  # noqa: E402
from design_baronnashor_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "baronnashor", "hd")
L6 = os.path.join(ROOT, "assets", "source", "baronnashor", "codex_legs", "baronnashor-legs", "baronnashor-legs-L6.png")
L6_PX = 11                    # Codex's squares in L6 (from the canvas's top-left corner)
L6_LEFT = 10                  # L6's columns left of A-1's: A-1's column c is the idle's c + L6_LEFT
BODY_ROWS = 66                # A-1's rows above its hips, which L6 keeps square for square
PPU = 2.04
FACE_BOX = (14 + L6_LEFT, 14, 46 + L6_LEFT, 42)   # x0, y0, x1, y1: the blue head, the eyes, the red mouth, the tusks


def l6():
    """L6 on its own squares, cut to the figure, hard alpha, on A-1's palette."""
    a = np.asarray(Image.open(lp(L6)).convert("RGBA"))
    g = a[L6_PX // 2::L6_PX, L6_PX // 2::L6_PX].copy()
    op = g[..., 3] >= 128
    ys, xs = np.nonzero(op)
    g, op = g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    base = np.asarray(Image.open(lp(os.path.join(HD, "A-1.png"))).convert("RGBA"))
    pal = np.unique(base[base[..., 3] > 0][:, :3], axis=0)
    lab_p = PD._lab(pal.astype(float))
    lab_g = PD._lab(g[op][:, :3].astype(float))
    out = np.zeros_like(g)
    out[op, :3] = pal[np.argmin(((lab_g[:, None] - lab_p[None]) ** 2).sum(-1), axis=1)]
    out[op, 3] = 255
    keep = out[:BODY_ROWS, L6_LEFT:L6_LEFT + base.shape[1]]
    if keep.shape[1] != base.shape[1] or not (keep == base[:BODY_ROWS]).all() \
            or out[:BODY_ROWS, :L6_LEFT, 3].any() or out[:BODY_ROWS, L6_LEFT + base.shape[1]:, 3].any():
        sys.exit("L6's body is not A-1's above its hips: check L6_LEFT / BODY_ROWS")
    return out


def main():
    im = l6()
    Image.fromarray(im).save(lp(os.path.join(HD, "idle.png")))
    Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, "idle_8x.png")))
    Image.fromarray(np.repeat(np.repeat(im[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]], 12, 0), 12, 1)).save(
        lp(os.path.join(HD, "idle_face12x.png")))
    print("idle", im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU}),",
          len(np.unique(im[im[..., 3] > 0][:, :3], axis=0)), "colours")


if __name__ == "__main__":
    main()
