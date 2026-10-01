#!/usr/bin/env python3
"""Blitzcrank's design: Codex's game-size B2 finished by hand (the user, 2026-10-01: "你可以修一修吧 不一定要依赖codex",
then "就用这版").

    python tools/art/design_blitzcrank.py [--check]

Reads assets/source/blitzcrank/codex_model/blitzcrank_design_B2_raw.png (Codex's B2 at 8x on the 128x128 canvas, the
figure at x 41..86, y 56..99) and writes assets/source/native/blitzcrank_native.png (8x), the strips pack's design and
import_native's:
1. the head and the feet, which Codex kept in round 1's lemon yellows, take the body's new gold ramp (colour for
   colour, darkest to lightest; no pixel moves);
2. both smokestacks redrawn as in the picture - a gold cap with a dark opening on a steel body narrowing downward (B2
   drew the near one as a tall straight post and hung the far one off the dome above an empty gap); the far one now
   reaches down to its shoulder.
3. the head two columns to the right (the user, 2026-10-02: "头部可以往右侧面调一调？现在太靠左贴到铠甲了"): B2 set it on
   column 64, three left of the collar's middle under it, its face against the near shoulder plate; now its chin sits in
   the collar and a gap opens to the plate. The squares it leaves stay clear (sky between the near stack and the dome;
   import_native closes the outline); it now covers the far smokestack's inner two columns (the stack stands behind).
The soles stand on row 99, the feet's middle on column 64; 16 colours. Also writes assets/source/native/blitzcrank_idle.png,
the design on each idle cell's pivot (import_native plays frame 1 six times). design_b2() is the design before step 3,
the one Codex drew the action strips from (fix_blitzcrank_strips.py matches its head and moves it like this).
--check compares with the files instead.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "blitzcrank", "codex_model", "blitzcrank_design_B2_raw.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "blitzcrank_native.png")
IDLE = os.path.join(ROOT, "assets", "source", "native", "blitzcrank_idle.png")
CELLS = os.path.join(ROOT, "assets", "source", "native", "blitzcrank_cells.json")
Z = 8
OX, OY = 41, 56                 # the figure's top-left on the canvas
GOLD = {"6a360d": "672d01", "925409": "984b01", "ac680f": "bc6802", "c78306": "dd8702", "f0b913": "f9af07",
        "ffdd4b": "fddc36"}
C = {"#": "170f1d", "a": "292536", "b": "672d01", "d": "373e56", "e": "984b01", "f": "454759", "i": "bc6802",
     "k": "dd8702", "l": "67718f", "m": "f9af07", "o": "fddc36", "p": "a2aecc", "r": "bfcde0", "t": "e2ebfc"}
# (figure row, first column, pixels): '.' leaves the pixel, ' ' clears it
NEAR = [(0, 11, ".#####."), (1, 11, "#maaak#"), (2, 11, "#ommki#"), (3, 11, "#mkkie#"), (4, 11, "#rplld#"),
        (5, 11, " #pldd#"), (6, 11, " #pld# "), (7, 11, " #lld# "), (8, 11, " #ldd# ")]
FAR = [(2, 28, ".####."), (3, 28, "#maak#"), (4, 28, "#mkki#"), (5, 28, "#kiie#"), (6, 28, "#pldd#"),
       (7, 28, "#lld# "), (8, 28, "#ldd# "), (9, 28, "#fdd# ")]
OLD_NEAR = (0, 9, 12, 17)       # rows, columns of B2's straight post (cleared first)
PIVOT = (64, 88)                # the standing point on the canvas
# the head (the dome, the eyes and the chin), row by row on the canvas: first and last column, outline to outline
HEAD = {59: (63, 65), 60: (62, 66), 61: (61, 67), 62: (60, 68), 63: (60, 68), 64: (60, 68), 65: (60, 68), 66: (60, 68),
        67: (61, 67), 68: (62, 66)}
HEAD_SHIFT = 2


def rgb(h):
    return tuple(int(h[k:k + 2], 16) for k in (0, 2, 4))


def move_head(a, rows, n):
    """The head's rows {row: (first, last column)} moved n columns to the right in place; the squares it leaves are
    cleared. Returns the cleared squares (row, column)."""
    head = {y: a[y, x0:x1 + 1].copy() for y, (x0, x1) in rows.items()}
    left = set()
    for y, (x0, x1) in rows.items():
        a[y, x0:x1 + 1] = 0
        left |= {(y, x) for x in range(x0, x0 + n)}
    for y, (x0, x1) in rows.items():
        seg = head[y]
        op = seg[..., 3] > 0
        a[y, x0 + n:x1 + 1 + n][op] = seg[op]
    return left


def design_b2():
    a = np.asarray(Image.open(G.lp(SRC)).convert("RGBA"))
    can = a[Z // 2::Z, Z // 2::Z].copy()
    can[can[..., 3] < 128] = 0
    can[can[..., 3] > 0, 3] = 255
    fig = can[OY:OY + 44, OX:OX + 46].copy()
    op = fig[..., 3] > 0
    for old, new in GOLD.items():
        m = (fig[..., :3] == rgb(old)).all(-1) & op
        fig[m, :3] = rgb(new)
    y0, y1, x0, x1 = OLD_NEAR
    fig[y0:y1, x0:x1] = 0
    for rows in (NEAR, FAR):
        for y, x, s in rows:
            for k, ch in enumerate(s):
                if ch == ".":
                    continue
                fig[y, x + k] = 0 if ch == " " else rgb(C[ch]) + (255,)
    can[:] = 0
    can[OY:OY + 44, OX:OX + 46] = fig
    return can


def design():
    can = design_b2()
    move_head(can, HEAD, HEAD_SHIFT)
    return can


def idle_strip(can):
    """The design on each idle cell's pivot (3 x 2 cells), 1x."""
    with open(G.lp(CELLS), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    frs = cells["tags"]["idle"]
    out = np.zeros((2 * ch, 3 * cw, 4), np.uint8)
    ys, xs = np.nonzero(can[..., 3])
    for k, fr in enumerate(frs):
        X, Y = (k % 3) * cw, (k // 3) * ch
        dx, dy = fr["pivot"][0] - PIVOT[0], fr["pivot"][1] - PIVOT[1]
        for y, x in zip(ys, xs):
            if 0 <= y + dy < ch and 0 <= x + dx < cw:
                out[Y + y + dy, X + x + dx] = can[y, x]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with assets/source/native/blitzcrank_native.png")
    args = ap.parse_args()
    can = design()
    op = can[..., 3] > 0
    ys, xs = np.nonzero(op)
    sole = ys.max()
    feet = np.nonzero(op[sole - 2:sole + 1].any(0))[0]
    assert sole == 99 and abs((feet.min() + feet.max()) / 2 - 64) <= 0.5
    print(f"figure x {xs.min()}..{xs.max()} y {ys.min()}..{sole}, {len(np.unique(can[op][:, :3], axis=0))} colours")
    bad = 0
    for path, img in ((OUT, can), (IDLE, idle_strip(can))):
        big = np.repeat(np.repeat(img, Z, 0), Z, 1)
        name = "assets/source/native/" + os.path.basename(path)
        if args.check:
            same = np.array_equal(np.asarray(Image.open(G.lp(path)).convert("RGBA")), big)
            bad += not same
            print(name + ":", "same" if same else "DIFFERS")
        else:
            Image.fromarray(big).save(G.lp(path))
            print("wrote", name)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
