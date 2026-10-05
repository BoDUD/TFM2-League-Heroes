#!/usr/bin/env python3
"""Xerath's action strips: Codex's step-2 delivery (assets/source/xerath/codex_strips/) with the body moving.

    python tools/art/fix_xerath_strips.py [--check]

Codex re-posed the design's own parts (its HANDOFF: the arms cut out and turned by quarter turns, the body, pauldrons,
chains, seal and legs square for square the design's) - the casting body is the idle's, as the user's rule asks. But
the body never moves: every cast stands bolt upright, which the user called 「僵硬」 on Tryndamere and Sivir. As
tools/art/rig_tryndamere.py's accepted casts, the upper body leans over the hips here: each row from HIP_ROW up moves
round((HIP_ROW - row) x lean) columns (+ forward, to the image right), the hood moving whole with its chin row (never
sheared: the triangle eyes would go diagonal), the legs below HIP_ROW as drawn. LEAN gives each frame's lean: back
while he draws a throw or charges, forward into the release, a little forward in the channel; at most 0.12 (2 columns
at the chin: 「倾斜不要太大」).
The death's heap (frames 6-8) also had loose black dashes of 1-4 squares beside it, read as stray outline: pieces of at
most SPECK squares that are all outline go (DEAD_SPECKS).
Reads codex_strips/xerath_<tag>.png (8x) and xerath_cells.json, writes assets/source/native/xerath_<tag>.png (8x) for
tools/art/import_native.py. --check compares instead of writing.
"""
import argparse
import json
import math
import os
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "xerath", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
# rows under / over the frame's pivot (the design's canvas: pivot row 88, the hood's chin row 68, the torso's lowest
# row 85 - under it the two legs)
HIP_DY, NECK_DY = -3, -20
SPECK = 4
LEAN = {
    "attack": [-0.08, -0.08, 0.0, 0.12, 0.10, 0.04],
    "skill": [-0.06, -0.08, -0.08, -0.08, -0.08, 0.12, 0.04],
    "skill_quick": [-0.06, -0.08, -0.08, 0.12, 0.04],
    "skill2": [-0.06, -0.08, 0.12, 0.10, -0.06, 0.0],
    "ult": [0.0, -0.06, -0.08, -0.06, 0.04],
    "ult_loop": [0.04] * 6,
    "ult_shot": [0.12, 0.08, 0.04],
    "hit": [-0.10, -0.04],
    "run": [0.06] * 8,
}
DEAD_SPECKS = [5, 6, 7]          # 0-based frames of the death


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def shift_of(dy, lean):
    """Columns a row (dy rows from the pivot) moves for a lean: 0 from the hips down, the hood as its chin row."""
    if not lean or dy >= HIP_DY:
        return 0
    v = (HIP_DY - max(dy, NECK_DY)) * lean
    return int(math.floor(abs(v) + 0.5)) * (1 if v > 0 else -1)


def lean_cell(c, pivot_y, lean):
    out = np.zeros_like(c)
    for y in range(c.shape[0]):
        d = shift_of(y - pivot_y, lean)
        if d > 0:
            out[y, d:] = c[y, :-d]
        elif d < 0:
            out[y, :d] = c[y, -d:]
        else:
            out[y] = c[y]
    return out


def drop_specks(c):
    """Pieces of at most SPECK squares that are all outline (luminance < 40) go."""
    op = c[..., 3] > 0
    lum = (c[..., :3].astype(int) * [299, 587, 114]).sum(-1) / 1000
    seen = np.zeros(op.shape, bool)
    H, W = op.shape
    gone = 0
    for y, x in zip(*np.nonzero(op)):
        if seen[y, x]:
            continue
        q, pts = deque([(y, x)]), []
        seen[y, x] = True
        while q:
            a, b = q.popleft()
            pts.append((a, b))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    u, v = a + dy, b + dx
                    if 0 <= u < H and 0 <= v < W and op[u, v] and not seen[u, v]:
                        seen[u, v] = True
                        q.append((u, v))
        if len(pts) <= SPECK and all(lum[a, b] < 40 for a, b in pts):
            for a, b in pts:
                c[a, b] = 0
            gone += len(pts)
    return gone


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    cells = json.load(open(lp(os.path.join(SRC, "xerath_cells.json")), encoding="utf-8"))
    cw, ch = cells["cell"]
    for tag, frs in cells["tags"].items():
        big = np.asarray(Image.open(lp(os.path.join(SRC, f"xerath_{tag}.png"))).convert("RGBA"))
        one = big[Z // 2::Z, Z // 2::Z].copy()
        cols, _ = layout(len(frs))
        notes = []
        for i, fr in enumerate(frs):
            x0, y0 = (i % cols) * cw, (i // cols) * ch
            c = one[y0:y0 + ch, x0:x0 + cw]
            lean = LEAN.get(tag, [0] * len(frs))[i]
            if lean:
                c[:] = lean_cell(c.copy(), fr["pivot"][1], lean)
            if tag == "dead" and i in DEAD_SPECKS:
                notes.append(f"frame {i + 1}: -{drop_specks(c)} speck squares")
        res = np.repeat(np.repeat(one, Z, 0), Z, 1)
        path = os.path.join(OUT, f"xerath_{tag}.png")
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            print(tag, "identical" if np.array_equal(old, res) else "DIFFERENT")
        else:
            Image.fromarray(res).save(lp(path))
            print(tag, LEAN.get(tag, "-"), "; ".join(notes))


if __name__ == "__main__":
    main()
