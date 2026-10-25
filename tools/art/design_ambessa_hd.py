#!/usr/bin/env python3
"""Ambessa's step-0 pictures read back on their own grid, A and SA on one palette.

    python tools/art/design_ambessa_hd.py [--a 5.0] [--b 5.0]   # writes assets/source/ambessa/hd/{A,SA}.png (+ _4x)

Step 0 (assets/source/ambessa/codex_picture/ambessa-picture, 2026-10-25): A her idle 3/4 front, SA her side, both
facing right, raw on 1254 canvases (asked 1536 and 11 px squares from the no-reference pack; Codex looked up the official
splash itself and drew her from it: the teal fur mantle, the swept silver hair, the black iron plate, the crimson scarf
and sash, the hooked crescent drakehound blades with open holes; soft alpha, no exact grid, far finer than asked).
Codex's own 11 px export (ambessa-A.png / ambessa-SA.png) is a box-sampled squash of the raw, not read here.
Codex's squares: the face's steps at 6x about 30 px (5 px), the colour edges' autocorrelation 5 / 9-10 / 14 both ways
(A), 5-6 / 11 (SA); regrid is given a little above (it splits rows below the real square).
Every picture is read on SIZE px squares, one pixel per drawn square; the colours of the two cut to COLOURS together by
k-means in Lab (design_varus.kmeans), alpha 0/255.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "ambessa", "codex_picture", "ambessa-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "ambessa", "hd")
GROUPS = ((("A", "SA"), 40),)   # pictures sharing one palette, and its colours
FILES = {"A": "ambessa-A.png", "SA": "ambessa-SA.png"}
SIZES = {"A": 5.0, "SA": 5.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=float, default=SIZES["A"])
    ap.add_argument("--b", type=float, default=SIZES["SA"], help="SA's square")
    a = ap.parse_args()
    SIZES.update(A=a.a, SA=a.b)
    os.makedirs(lp(OUT), exist_ok=True)
    for names, colours in GROUPS:
        parts = [read(n, SIZES[n]) for n in names]
        h = max(p.shape[0] for p in parts)
        both = np.zeros((h, sum(p.shape[1] for p in parts), 4), np.uint8)
        x = 0
        for p in parts:
            both[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1]
        op = both[..., 3] > 0
        idx, pal = V.kmeans(both, colours)
        out = np.zeros_like(both)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        x = 0
        for name, p in zip(names, parts):
            part = out[:p.shape[0], x:x + p.shape[1]]
            x += p.shape[1]
            part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
            Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
            Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
            print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()
