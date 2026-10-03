#!/usr/bin/env python3
"""Caitlyn's run on the second design: the design's upper body on hand-drawn crossing legs (2026-10-03).

    python tools/art/fix_caitlyn_run_v2.py --cells assets/source/native/caitlyn_cells.json --out assets/source/native/caitlyn_run.png [--check]

Codex's v2 run kept one leg kicked up behind in all 8 frames (no crossing step), and its legs-only redo shrank the legs
back into short shuffling steps - the players' complaint. The user: 「你来修复吧 codex太笨了」. Legs drawn along bone
lines (each square coloured by its length along the leg) scattered the gold garter, boot top and buckle into specks
on every slanted leg: 「走路的时候腿有点变形」. So, as the first design's run (tools/art/fix_caitlyn_run.py, approved:
「挺不错的」), every leg here is drawn square by square (LEG: one leg's eight phases, the design's leg materials and
length - navy tights, the gold garter, the brown knee pad, the gold boot top, the brown boot, the foot toe forward),
and each frame is
- the design (assets/source/caitlyn/design_v2) from the top down to its skirt's lining (2 rows over the standing
  point): head, hat, hair, the rifle carried as in the idle, the skirt - lowered by STEP (League's pelvis), the legs
  staying on the ground (the skirt slides over the thighs);
- the near leg at phase k in frame k + 1, the far leg 4 phases on and 3 squares further right (the hips 3 apart):
  planted under her and sliding back (1-3), pushing off (4), the heel kicked up behind (5-6), swung through (7) and
  reaching forward to land (8). The near foot passes the far one between frames 2 and 3 and back between 7 and 8.
  The far leg is drawn first with its outline ring, the near one with its ring over it, the upper body over both.
Writes the 4 x 2 strip of 96 x 96 cells at 8x (the cells and pivots of the run in the cells table).
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

DESIGN = os.path.join(ROOT, "assets", "source", "caitlyn", "design_v2", "caitlyn_design_v2_1x.png")
PIVOT = (64, 88)                 # the design's standing point on its canvas
Z = 8
CUT = -2                         # the upper body: rows to 2 over the standing point (the skirt's lining)
STEP = [0, 1, 2, 1, 0, 1, 2, 1]  # the upper body's rows down per frame (League's pelvis)
FAR = 3                          # the far leg: the near leg's drawing 3 squares to the right
PAL = {"r": "30345C", "C": "FDC429", "t": "683934", "v": "7A4429", "w": "915526", "d": "0D0012"}
X0, Y0 = -12, -1                 # the grids' first column and row (squares from the standing point)
# one leg (the near one: its hip over columns -3/-2) in its eight phases; rows -1..10, columns from -12
LEG = [
    # 1: planted, the foot a square ahead of the hip
    ["..........rr..........",
     "..........rr..........",
     "..........Ct..........",
     "..........vw..........",
     "..........rr..........",
     "...........rr.........",
     "...........CC.........",
     "...........vv.........",
     "...........vw.........",
     "...........vC.........",
     "...........vvw........",
     "...........tvw........"],
    # 2: planted under the hip
    ["..........rr..........",
     "..........rr..........",
     "..........Ct..........",
     "..........vw..........",
     "..........rr..........",
     "..........rr..........",
     "..........CC..........",
     "..........vv..........",
     "..........vw..........",
     "..........vC..........",
     "..........vvw.........",
     "..........tvw........."],
    # 3: planted, sliding back under her
    ["..........rr..........",
     "..........rr..........",
     "..........Ct..........",
     "..........vw..........",
     ".........rr...........",
     ".........rr...........",
     ".........CC...........",
     ".........vv...........",
     "........vw............",
     "........vC............",
     "........vvw...........",
     "........tvw..........."],
    # 4: pushing off behind, the heel up
    ["..........rr..........",
     ".........rr...........",
     ".........Ct...........",
     "........vw............",
     "........rr............",
     ".......rr.............",
     ".......CC.............",
     "......vv..............",
     "......vw..............",
     ".....vw...............",
     ".....vvw..............",
     ".......vw............."],
    # 5: the heel lifting behind, the knee bent
    ["..........rr..........",
     "..........rr..........",
     ".........Ct...........",
     ".........vw...........",
     "........rr............",
     ".......rr.............",
     "......CC..............",
     ".....vv...............",
     "....vw................",
     "....tv................",
     "......................",
     "......................"],
    # 6: the heel kicked up high, the shin level behind the knee
    ["..........rr..........",
     "..........rr..........",
     "..........Ct..........",
     "..........vw..........",
     ".....vvCCrrr..........",
     "....tvwCCrr...........",
     "....tv................",
     "......................",
     "......................",
     "......................",
     "......................",
     "......................"],
    # 7: swung through, the knee forward, the foot tucked under her
    ["..........rr..........",
     "...........rr.........",
     "............Ct........",
     "............vw........",
     "...........rr.........",
     "...........rr.........",
     "..........CC..........",
     "..........vv..........",
     ".........vvw..........",
     ".........tvw..........",
     "......................",
     "......................"],
    # 8: reaching forward, the heel about to land
    ["..........rr..........",
     "...........rr.........",
     "...........Ct.........",
     "............vw........",
     "............rr........",
     ".............rr.......",
     ".............CC.......",
     "..............vv......",
     "..............vw......",
     "..............vvw.....",
     "..............tvw.....",
     "......................"],
]


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


def rgba(ch):
    h = PAL[ch]
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255], np.uint8)


def leg_cells(phase, dx):
    out = {}
    for i, row in enumerate(LEG[phase]):
        for j, ch in enumerate(row):
            if ch != ".":
                out[(X0 + j + dx, Y0 + i)] = rgba(ch)
    return out


def ring(cells):
    r = set()
    for x, y in cells:
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ddx, y + ddy)
            if q not in cells:
                r.add(q)
    return r


def frame(upper, k, pivot, cell):
    c = np.zeros((cell[1], cell[0], 4), np.uint8)

    def put(x, y, col):
        tx, ty = pivot[0] + x, pivot[1] + y
        if 0 <= tx < cell[0] and 0 <= ty < cell[1]:
            c[ty, tx] = col

    for phase, dx in (((k + 4) % 8, FAR), (k, 0)):         # the far leg first, the near one over it
        cells = leg_cells(phase, dx)
        for x, y in ring(cells):
            put(x, y, rgba("d"))
        for (x, y), col in cells.items():
            put(x, y, col)
    dy = STEP[k]
    ys, xs = np.nonzero(upper[..., 3])
    for y, x in zip(ys, xs):
        put(x - PIVOT[0], y - PIVOT[1] + dy, upper[y, x])
    c[pivot[1] + 12:] = 0                                   # nothing under the soles' row
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true", help="compare with --out instead of writing it")
    a = ap.parse_args()
    cells = json.load(open(lp(a.cells), encoding="utf-8"))
    cell = cells["cell"][:2]
    run = cells["tags"]["run"]
    d = np.asarray(Image.open(lp(DESIGN)).convert("RGBA")).copy()
    d[PIVOT[1] + CUT + 1:] = 0
    strip = np.zeros((2 * cell[1], 4 * cell[0], 4), np.uint8)
    for k, fr in enumerate(run):
        strip[(k // 4) * cell[1]:(k // 4 + 1) * cell[1], (k % 4) * cell[0]:(k % 4 + 1) * cell[0]] = frame(d, k, fr["pivot"], cell)
    big = np.repeat(np.repeat(strip, Z, 0), Z, 1)
    if a.check:
        same = np.array_equal(np.asarray(Image.open(lp(a.out)).convert("RGBA")), big)
        print("run", "same" if same else "DIFFERENT")
        return
    Image.fromarray(big).save(lp(a.out))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
