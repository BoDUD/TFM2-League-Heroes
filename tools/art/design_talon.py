#!/usr/bin/env python3
"""Talon's game-size design (step 1): the approved letter grid -> the native 8x canvas.

    python tools/art/design_talon.py --final    # assets/source/talon/design/talon_design.txt -> assets/source/native/talon_native.png
    python tools/art/design_talon.py --check    # the grid vs the committed native png

How it came about (2026-10-10). The user picked Codex's picture A (assets/source/talon/picture: League's idle crouch,
blue-violet hood with the silver blade crest, the rust-red blade cape, the wrist blade at the hip). Codex's own step-1
sprites were crude two-tone blocks (rejected: 「GPT做的有点差」), and every automatic trace of the 190-row picture down
to 40 rows came out as black specks and grey mush. What the user kept:
  1. the silhouette of a material-vote trace of picture A (one cell = the picture's block, the head traced 1.55x
     bigger over the body: 42 x 32);
  2. inside it, every cell hand-pixelled in the pack's way - big flat areas, 2-3 shades a material, black only on the
     silhouette and the structural lines: the hood (a-e), the three silver pauldron tiers, the red cape with three
     silver blade tips and the hem's spear blade, the wrist blade at the hip, belt + gold buckle, teal sash, gunmetal
     legs with silver knee guards;
  3. the face WITHOUT eyes (the user: 「这眼睛不对 你要么就别画眼睛了 拿头罩遮住」): under the silver crest a black band
     of hood shadow, below it the lit lower face (cheeks, nose, mouth, chin) - the splash's look.
Approved 「这个可以下一步吧」: 42 x 32, 22 colours, the outline closed. Strips: keep the face this way (no eyes).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GRID = os.path.join(ROOT, "assets", "source", "talon", "design", "talon_design.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "talon_native.png")
SOLE_ROW, MID_COL, Z = 99, 64, 8

PAL = {
    "k": "#120E1A",                                                        # outline
    "a": "#141250", "b": "#221F7E", "c": "#3533AA", "d": "#4D4BD2", "e": "#7279F6",   # blue-violet hood / clothes
    "p": "#4A0B15", "q": "#6E1219", "r": "#A01C24", "s": "#D82A2F",                   # rust-red cape / scarf
    "u": "#35343F", "v": "#55525E", "w": "#7A7986", "x": "#A4A6B4", "y": "#CFD0DC", "z": "#FAFAFC",  # steel
    "f": "#7A4A30", "g": "#C27E4E", "h": "#ECB486",                                   # skin
    "m": "#0A4A66", "n": "#2A92A2",                                                   # teal sash
    "o": "#D09A38",                                                                   # gold buckle
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def grid():
    rows = [l.rstrip("\r\n") for l in open(lp(GRID), encoding="utf-8") if l.strip()]
    w = max(len(r) for r in rows)
    return [r.ljust(w, ".") for r in rows]


def canvas(rows):
    """The grid on the 128 x 128 canvas: its lowest row on SOLE_ROW, the middle of the feet on MID_COL."""
    H, W = len(rows), len(rows[0])
    feet = [c for c in range(W) if any(rows[r][c] != "." for r in range(H - 3, H))]
    y0 = SOLE_ROW + 1 - H
    x0 = int(round(MID_COL - (min(feet) + max(feet)) / 2))
    can = np.zeros((128, 128, 4), np.uint8)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch != ".":
                h = PAL[ch]
                can[y0 + r, x0 + c] = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can = canvas(grid())
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
        print("same" if (old == can).all() else f"differs in {int((old != can).any(-1).sum())} squares")
        return
    if a.final:
        Image.fromarray(can).resize((128 * Z, 128 * Z), Image.NEAREST).save(lp(OUT))
        ys, xs = np.nonzero(can[..., 3])
        print(OUT, f"rows {ys.min()}-{ys.max()} cols {xs.min()}-{xs.max()}",
              len({tuple(p) for p in can[can[..., 3] > 0][:, :3]}), "colours")


if __name__ == "__main__":
    main()
