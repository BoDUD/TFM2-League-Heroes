#!/usr/bin/env python3
"""Fill the outline square cut into Xayah's near thigh, in the design and every approved strip frame.

    python tools/art/fix_xayah_thigh.py [--check]
    python tools/art/import_native.py --hero xayah

The user, on the showcase (2026-10-08): 「大腿上有个像素缺失了 其他都很好」 - the design's square (86, 66) is outline with
skin to its right and below (the thigh's top left corner). The strips the user approved stay as they are: the square is
found in each frame by the design's 3x3 neighbourhood round it (turned with the lying death frames) - exactly one per
frame - and only it gets the thigh's shade (design_xayah.py HOLES carries the same square for the design itself).
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8
AT = (86, 66)                                 # (row, column) on the design canvas
INK = (11, 4, 14)
SHADE = (0xE8, 0x9C, 0x86)                    # the thigh's shade (design_xayah LETTERS "m")


def lp(p):
    p = os.path.abspath(p)
    return p if p.startswith(chr(92) * 2) else chr(92) * 2 + "?" + chr(92) + p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    design = np.asarray(Image.open(lp(os.path.join(NATIVE, "xayah_native.png"))).convert("RGBA"))
    design = design if design.shape[0] == 128 else design[Z // 2::Z, Z // 2::Z]
    y, x = AT
    pat = design[y - 1:y + 2, x - 1:x + 2].astype(int)
    if tuple(pat[1, 1, :3]) == SHADE:
        pat = pat.copy()
        pat[1, 1, :3] = INK
    pats = [np.rot90(pat, k) for k in range(4)]
    todo = 0
    for f in sorted(glob.glob(lp(os.path.join(NATIVE, "xayah_*.png")))):
        if f.endswith("_native.png"):
            continue
        big = np.asarray(Image.open(f).convert("RGBA")).copy()
        a8 = big[Z // 2::Z, Z // 2::Z].astype(int)
        hits = [(yy, xx) for yy in range(1, a8.shape[0] - 1) for xx in range(1, a8.shape[1] - 1)
                if tuple(a8[yy, xx, :3]) == INK and a8[yy, xx, 3]
                and any((a8[yy - 1:yy + 2, xx - 1:xx + 2] == p).all() for p in pats)]
        todo += len(hits)
        print(f"{os.path.basename(f)}: {len(hits)}")
        if a.check or not hits:
            continue
        for yy, xx in hits:
            big[yy * Z:(yy + 1) * Z, xx * Z:(xx + 1) * Z, :3] = SHADE
        Image.fromarray(big, "RGBA").save(f)
    sys.exit(1 if a.check and todo else 0)


if __name__ == "__main__":
    main()
