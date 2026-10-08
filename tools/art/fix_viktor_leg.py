#!/usr/bin/env python3
"""Viktor's rear shin coloured in (the user: 「这里是不是少色素了啊」「腿上」, 2026-10-08).

His rear leg runs down-left from the thigh (navy #3e4270 at rows 67-68) to the foot (rows 72-73), but the three shin rows
between were drawn as bare outline with a transparent hole at (70, 49): the leg read as missing a piece. This gives the
shin two squares of the leg's own navy along its slant (the shadow #3a2c40 under the thigh as in row 68), outlines kept,
in every cell of every viktor strip whose shin still matches idle frame 1's hollow one (searched 4 squares around:
29 cells - attack, hit, idle, skill, skill2, skill2_e, ult and dead 1).

    python tools/art/fix_viktor_leg.py
"""
import glob
import json
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")
Z = 8
N = (0x3E, 0x42, 0x70)      # the leg's navy
S = (0x3A, 0x2C, 0x40)      # its shadow
O = (0x0B, 0x09, 0x10)      # outline
# (row, col, colour) in idle frame 1's cell coordinates
EDITS = [(69, 48, N), (69, 49, S), (70, 48, N), (70, 49, N), (71, 48, N), (71, 49, O)]
REGION = (67, 73, 46, 52)   # rows, cols of the hollow shin itself (the cloak and staff around it move per action)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def main():
    cells = json.load(open(lp(os.path.join(NATIVE, "viktor_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    idle = np.asarray(Image.open(lp(os.path.join(NATIVE, "viktor_idle.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    r0, r1, c0, c1 = REGION
    ref = idle[0:ch, 0:cw][r0:r1, c0:c1].copy()
    assert (ref[..., 3] > 0).sum() > 20, "the reference region is empty - wrong coordinates"
    for path in sorted(glob.glob(os.path.join(NATIVE, "viktor_*.png"))):
        if path.endswith("_native.png"):
            continue
        a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
        rows, colls = a.shape[0] // ch, a.shape[1] // cw
        done = []
        for k in range(rows * colls):
            y, x = (k // colls) * ch, (k % colls) * cw
            cell = a[y:y + ch, x:x + cw]
            hit = None
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    if 0 <= r0 + dy and r1 + dy <= ch and 0 <= c0 + dx and c1 + dx <= cw:
                        if cell[r0 + dy:r1 + dy, c0 + dx:c1 + dx].tobytes() == ref.tobytes():
                            hit = (dy, dx)
                            break
                if hit:
                    break
            if hit is None:
                continue
            for r, c, col in EDITS:
                cell[r + hit[0], c + hit[1]] = (*col, 255)
            done.append(k + 1)
        if done:
            Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST).save(lp(path))
            print(os.path.basename(path), "cells", done)


if __name__ == "__main__":
    main()
