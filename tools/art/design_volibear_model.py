#!/usr/bin/env python3
"""Volibear's step-1 game-size designs read back on their own grid, one palette for both views.

    python tools/art/design_volibear_model.py   # writes assets/source/volibear/hd/model{B,S,S_cut}.png (+ _8x)

Step 1 (assets/source/volibear/codex_model/volibear-model, 2026-10-19, Codex new-chat-2): asked 21 px squares, 53 rows
from the ear top to the soles, a 3/4 front view (B, design B: the arms hanging down) and a side-on one facing right
(side). Codex's first takes came back fine-grained (B-1 ~11 px, 103 rows; side-1 ~10 px, 117 rows); its "grid
correction" takes are on the count: B-2 at 21 px reads 51 x 54, side-2 (~20 px) 35 x 58 - the same 1125 px tall as
B-2 on narrower squares. regrid.py reads each one pixel per drawn square at 21 px; the colours of both are cut
together by k-means in Lab (design_varus.kmeans), alpha 0/255. The side view is brought to B's 54 rows by
design_rell_cut.even_cut (whole rows and columns, one per equal window, never the head's rows SIDE_HEAD) -> modelS_cut.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402
from design_volibear_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "volibear", "codex_model", "volibear-model", "raw")
OUT = os.path.join(ROOT, "assets", "source", "volibear", "hd")
COLOURS = 40
FILES = {"B": ("volibear-model-B-2-grid-correction.png", 21.0), "S": ("volibear-model-side-2-grid-correction.png", 21.0)}
SIDE_HEAD = (0, 16)   # rows of the side view's head (ear top to chin)


def read(name):
    fname, size = FILES[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, fname))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def save(name, d):
    Image.fromarray(d).save(lp(os.path.join(OUT, f"model{name}.png")))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(lp(os.path.join(OUT, f"model{name}_8x.png")))
    print(name, d.shape[1], "x", d.shape[0])


def main():
    parts = {k: read(k) for k in FILES}
    h = max(p.shape[0] for p in parts.values())
    both = np.zeros((h, sum(p.shape[1] for p in parts.values()), 4), np.uint8)
    x = 0
    for p in parts.values():
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    done = {}
    for name, p in parts.items():
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))].copy()
        done[name] = part
        save(name, part)
    s, rows = done["S"], done["B"].shape[0]
    cols = round(s.shape[1] * rows / s.shape[0])
    save("S_cut", RC.even_cut(s, rows, cols, (list(range(SIDE_HEAD[0], SIDE_HEAD[1] + 1)), [])))


if __name__ == "__main__":
    main()
