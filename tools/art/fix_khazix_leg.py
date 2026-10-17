#!/usr/bin/env python3
"""Kha'Zix's rear-left leg put back (the user: 「螳螂左腿模型还不正常」, 2026-10-08).

In the approved design (assets/source/khazix/codex_model/khazix_design_A_1x.png, rows 83-95) that leg is a 2-px
navy #46309a shaft with a 1-px #0b0814 outline on both sides and a #2a78d0 accent, bending down-left from the hip to
the orange claw. The import crushed it to a single dark line hanging over the claw. This traces the design's leg back
at the strips' scale (hip (57, 69) to the claw top (52, 78); the claw itself was imported right and stays), in every
cell of every khazix strip whose leg region still equals idle frame 1's - the design pose Codex copied around.

    python tools/art/fix_khazix_leg.py
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
O = (0x0B, 0x08, 0x14)      # outline
N = (0x46, 0x30, 0x9A)      # the leg's navy
C = (0x2A, 0x78, 0xD0)      # the blue accent the design has on the shaft's edge
# (row, col, colour) in idle frame 1's cell coordinates
EDITS = [(69, 56, O), (69, 57, N), (69, 58, N),
         (70, 55, O), (70, 56, N), (70, 57, N), (70, 58, O),
         (71, 54, O), (71, 55, C), (71, 56, N), (71, 57, N), (71, 58, O),
         (72, 54, O), (72, 55, N), (72, 56, N), (72, 57, O),
         (73, 54, O), (73, 55, N), (73, 56, N), (73, 57, O),
         (74, 54, O), (74, 55, N), (74, 56, N), (74, 57, O),
         (75, 53, O), (75, 54, N), (75, 55, N), (75, 56, O),
         (76, 53, O), (76, 54, N), (76, 55, N), (76, 56, O),
         (77, 52, O), (77, 53, N), (77, 54, N), (77, 55, O),
         (78, 52, O), (78, 53, N), (78, 54, N), (78, 55, O)]
REGION = (66, 82, 49, 60)   # rows, cols that identify the old leg (compared before patching a cell)


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def main():
    cells = json.load(open(lp(os.path.join(NATIVE, "khazix_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    idle = np.asarray(Image.open(lp(os.path.join(NATIVE, "khazix_idle.png"))).convert("RGBA"))[Z // 2::Z, Z // 2::Z]
    r0, r1, c0, c1 = REGION
    ref = idle[0:ch, 0:cw][r0:r1, c0:c1].copy()
    for path in sorted(glob.glob(os.path.join(NATIVE, "khazix_*.png"))):
        if path.endswith(("_native.png", "_head_1x.png")):
            continue
        a = np.asarray(Image.open(lp(path)).convert("RGBA"))[Z // 2::Z, Z // 2::Z].copy()
        rows, colls = a.shape[0] // ch, a.shape[1] // cw
        done = []
        for k in range(rows * colls):
            y, x = (k // colls) * ch, (k % colls) * cw
            cell = a[y:y + ch, x:x + cw]
            if cell[r0:r1, c0:c1].tobytes() != ref.tobytes():
                continue
            for r, c, col in EDITS:
                cell[r, c] = (*col, 255)
            done.append(k + 1)
        if done:
            Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST).save(lp(path))
            print(os.path.basename(path), "cells", done)


if __name__ == "__main__":
    main()
