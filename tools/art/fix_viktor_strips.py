#!/usr/bin/env python3
"""Viktor's action strips from Codex's step-2 delivery (assets/source/viktor/codex_strips/, Codex's rig of the design's
parts; the user: 「帮我完成下一步吧」) into assets/source/native/ for tools/art/import_native.py.

    python tools/art/fix_viktor_strips.py

Fix 1 (the user, at the design: 「法杖这一段有点歪 可以顺便修复了」): the staff's lower shaft stood one column right of
its upper part (design_viktor.py step 1b). Codex's frames carry the design's staff, upright or turned whole, so in
every frame the old lower piece (its four columns, rows 31-40 of the figure) is found by an exact match of its pixels
and moved one column left the same way (design_viktor.kink). A piece the rig turned is not upright and is not matched;
the count per strip is printed.
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import design_viktor as D  # noqa: E402

CODEX = os.path.join(REPO, "assets", "source", "viktor", "codex_strips")
NATIVE = os.path.join(REPO, "assets", "source", "native")
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_e", "ult", "hit", "dead"]
Z = 8


def old_piece():
    """The design's lower shaft before fix 1 (Codex's frames were built from that design): (piece, opaque mask)."""
    a = np.array(Image.open(D.lp(D.SRC)).convert("RGBA"))
    c = a[D.Y0:D.Y0 + D.H, D.X0:D.X0 + D.W].copy()
    D.staff(c)
    a0, b0 = D.KINK_COLS
    rows = list(D.KINK_ROWS)
    return c[rows[0]:rows[-1] + 1, a0:b0]


def fix(strip, piece):
    """Every exact match of the piece in the strip (1x): the shaft moved one column left, as design_viktor.kink."""
    h, w = piece.shape[:2]
    H, W = strip.shape[:2]
    hits = 0
    for y in range(H - h + 1):
        for x in range(1, W - w):
            if not np.array_equal(strip[y:y + h, x:x + w], piece):
                continue
            for r in range(y, y + h):
                old = strip[r].copy()
                strip[r, x - 1:x + w - 1] = old[x:x + w]
                right = old[x + w]
                if right[3] and tuple(int(v) for v in right[:3]) in D.CAPE:
                    strip[r, x + w - 1] = right
                elif right[3]:
                    strip[r, x + w - 1, :3], strip[r, x + w - 1, 3] = D.INK, 255
                else:
                    strip[r, x + w - 1] = 0
            hits += 1
    return hits


def main():
    piece = old_piece()
    for tag in TAGS:
        big = np.array(Image.open(D.lp(os.path.join(CODEX, f"viktor_{tag}.png"))).convert("RGBA"))
        one = big[Z // 2::Z, Z // 2::Z].copy()
        n = fix(one, piece)
        Image.fromarray(np.repeat(np.repeat(one, Z, 0), Z, 1)).save(D.lp(os.path.join(NATIVE, f"viktor_{tag}.png")))
        print(f"{tag:9s} shaft fixed in {n} frame(s)")
    shutil.copyfile(os.path.join(CODEX, "viktor_cells.json"), os.path.join(NATIVE, "viktor_cells.json"))


if __name__ == "__main__":
    main()
