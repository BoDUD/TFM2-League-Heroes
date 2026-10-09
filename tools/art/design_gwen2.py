#!/usr/bin/env python3
"""Gwen's design 2 (assets/source/native/gwen_native.png): the letter grid assets/source/gwen/design/gwen_design2.txt.

    python tools/art/design_gwen2.py [--check]

2026-10-09: the user liked Codex's picture of her carrying the closed scissors on her shoulder with a smug face
(「codex生成的这一版非常不错 你能还原吗」). Hand tracing it at game size could not reproduce the face (the picture's head
is tilted; 「你现在头是做正的 所以强行画五官就不一致」), so Codex drew it again ON THE GAME GRID (26-px squares, 38 rows
crown to soles, the chibi head of the approved sprite; codex_grid/gwen-grid-A_1x.png is one pixel per square). That 1x
sits on the 128 canvas with the soles on row 99 and the feet's middle on column 64; the scissors' handle, which the
sampling had broken into scraps, is redrawn by hand from Codex's generation source (the round pivot screw at the
face's right, the far hand's glove on the shaft under it, the shaft forking to two heart finger loops with
see-through holes, four spikes), the right ringlet and the waist under the arm tidied, five pinholes filled, the
outline closed (work/gs/g3 in the 璐璐 session). Z (#ff00ff) marks the loops' holes: an opaque colour through the rig
and the import's outline pass, cleared to transparent by clean_gwen.py at the end (a clear hole gets outlined shut).
design_gwen.py (the previous design) is superseded.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GRID = os.path.join(ROOT, "assets", "source", "gwen", "design", "gwen_design2.txt")
OUT = os.path.join(ROOT, "assets", "source", "native", "gwen_native.png")
X0 = 40                                # the grid's first column on the canvas
HOLE = (255, 0, 255)                   # the hole marker


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hx(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def read():
    """(canvas, palette {letter: rgb})."""
    pal, can = {}, np.zeros((128, 128, 4), np.uint8)
    for line in open(lp(GRID), encoding="utf-8"):
        line = line.rstrip("\r\n")
        if line.startswith("# palette"):
            pal = {t.split("=")[0]: hx(t.split("=")[1]) for t in line.split()[2:]}
        if len(line) < 4 or not line[:3].strip().isdigit():
            continue
        y = int(line[:3])
        for i, ch in enumerate(line[3:]):
            if ch in " .":
                continue
            can[y, X0 + i, :3] = pal[ch]
            can[y, X0 + i, 3] = 255
    return can, pal


def build():
    return read()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    can = build()
    ys, xs = np.nonzero(can[..., 3] > 0)
    info = (f"{xs.max() - xs.min() + 1} x {ys.max() - ys.min() + 1} (rows {ys.min()}-{ys.max()}, cols {xs.min()}-{xs.max()}), "
            f"{len({tuple(p[:3]) for p in can[can[..., 3] > 0]})} colours")
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, can) else "DIFFERENT", info)
        sys.exit(0 if np.array_equal(old, can) else 1)
    Image.fromarray(can).save(lp(OUT))
    print(OUT, info)


if __name__ == "__main__":
    main()
