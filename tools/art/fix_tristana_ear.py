#!/usr/bin/env python3
"""Tristana's right ear attached to her head (the user: 「小炮的耳朵看起来脱离了英雄」, 2026-10-08).

Her left ear flows into the hair with no line between; the right ear came with a full outline ring, so a black channel
separates it from the head and it reads as floating. This opens the ring at the ear's root - the two junction columns
become hair white and ear pink over the five middle rows, as on the left ear - in every cell of every tristana strip
whose junction region still matches idle frame 1's (compared on its opaque pixels, so what lies behind the ear's top
does not matter).

    python tools/art/fix_tristana_ear.py
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
HAIR = (0xFF, 0xF4, 0xE4)
PINK = (0xF6, 0x99, 0xB4)
EDITS = ([(r, 51, HAIR) for r in range(55, 60)] + [(r, 52, PINK) for r in range(55, 60)]
         + [(r, 53, PINK) for r in range(55, 60)])
REGION = (50, 64, 47, 63)   # rows, cols that identify the old junction (idle frame 1's cell coordinates)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def main():
    cells = json.load(open(lp(os.path.join(NATIVE, "tristana_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    idle = np.asarray(Image.open(lp(os.path.join(NATIVE, "tristana_idle.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    r0, r1, c0, c1 = REGION
    ref = idle[0:ch, 0:cw][r0:r1, c0:c1].copy()
    rm = ref[..., 3] > 0
    assert rm.sum() > 50, "the reference region is empty - wrong coordinates"
    for path in sorted(glob.glob(os.path.join(NATIVE, "tristana_*.png"))):
        if path.endswith("_native.png"):
            continue
        a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
        rows, colls = a.shape[0] // ch, a.shape[1] // cw
        done = []
        for k in range(rows * colls):
            y, x = (k // colls) * ch, (k % colls) * cw
            cell = a[y:y + ch, x:x + cw]
            hit = None                                       # the junction, searched a few squares around (bobbed heads)
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if 0 <= r0 + dy and r1 + dy <= ch and 0 <= c0 + dx and c1 + dx <= cw:
                        win = cell[r0 + dy:r1 + dy, c0 + dx:c1 + dx]
                        if np.array_equal(win[rm], ref[rm]):
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
