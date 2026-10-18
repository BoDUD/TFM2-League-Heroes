#!/usr/bin/env python3
"""league_gangplank's boots in the design (assets/source/gangplank/hd/design.png) made boots again (the user, 2026-10-18,
on the uncut redo take: 「问题还是在 脚这里变形」 with a crop of both feet).

    python tools/art/fix_gangplank_feet.py [--check]

Codex's redo take drew the near foot (rows 57-61, columns 13-20) narrower than its cuff, widening backward with a sole
two outline rows thick - a stump - and the far foot with an outline square through its sole (59, 32). The far foot is a
proper boot (the ankle under the cuff, the toe forward); the near foot is laid out on its rows instead, from the design's
own squares and colours: rows 57-60 of the far foot moved 15 columns left under the near cuff, the ankle row twice (the
near foot stands a row lower, as drawn), its upper sole row a shade lighter (the near side is lit); the far foot's notch
gets the sole's brown beside it. Idempotent: --check only reports whether the design is already fixed.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from design_gangplank_hd import lp  # noqa: E402

PATH = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "source", "gangplank", "hd", "design.png")
DX = -15                       # far foot columns -> near foot columns
MID, LIGHT, DARK = (98, 65, 51), (117, 83, 68), (73, 47, 36)


def fixed(d):
    out = d.copy()
    far = d[57:61, 28:39].copy()                  # ankle, foot, sole top, sole outline
    far[2, 4] = (*MID, 255)                       # the notch (row 59, column 32) closed
    out[59, 32] = (*MID, 255)
    near = np.zeros((5, 11, 4), np.uint8)
    near[0] = far[0]                              # ankle
    near[1] = far[0]                              # ankle again: the near foot a row lower
    near[2] = far[1]
    near[3] = far[2]
    near[4] = far[3]
    lit = (near[3, :, 3] > 0) & np.all(near[3, :, :3] == MID, axis=-1)
    near[3][lit] = (*LIGHT, 255)
    lit = (near[2, :, 3] > 0) & np.all(near[2, :, :3] == DARK, axis=-1)
    near[2][lit] = (*MID, 255)
    out[57:62, 13:24] = 0
    out[57:62, 28 + DX:39 + DX] = near
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    d = np.asarray(Image.open(lp(PATH)).convert("RGBA")).copy()
    done = d[59, 32, 3] > 0 and tuple(d[59, 32, :3]) == MID and d[61, 13:24, 3].sum() > 0 and d[61, 24:, 3].sum() == 0 \
        and np.array_equal(d[58, 13:24], d[57, 13:24])
    if a.check:
        print("fixed" if done else "not fixed")
        return
    if done:
        print("already fixed")
        return
    Image.fromarray(fixed(d)).save(lp(PATH))
    print("written", PATH)


if __name__ == "__main__":
    main()
