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
The soles stand on row 99, the feet's middle on column 64; 16 colours. --check compares with the file instead.
"""
import argparse
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


def rgb(h):
    return tuple(int(h[k:k + 2], 16) for k in (0, 2, 4))


def design():
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
    big = np.repeat(np.repeat(can, Z, 0), Z, 1)
    print(f"figure x {xs.min()}..{xs.max()} y {ys.min()}..{sole}, {len(np.unique(can[op][:, :3], axis=0))} colours")
    if args.check:
        same = np.array_equal(np.asarray(Image.open(G.lp(OUT)).convert("RGBA")), big)
        print("assets/source/native/blitzcrank_native.png:", "same" if same else "DIFFERS")
        sys.exit(0 if same else 1)
    Image.fromarray(big).save(G.lp(OUT))
    print("wrote assets/source/native/blitzcrank_native.png")


if __name__ == "__main__":
    main()
