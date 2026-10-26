#!/usr/bin/env python3
"""Zaahen's step-0 pictures read back on their own grid, each group on one palette.

    python tools/art/design_zaahen_hd.py   # writes assets/source/zaahen/hd/{A-1,A-2,B-2}.png (+ _4x)

Step 0 (assets/source/zaahen/codex_picture/zaahen-picture, 2026-10-26, Codex 2026-10-26/new-chat-4): asked 1536 and
11 px squares, delivered 1254 canvases with soft alpha and uneven squares (Codex's own HANDOFF says so). A = his idle
3/4 front with the glaive across him and the wings folded; B = wings spread and the glaive raised, feet on the ground
(made from A, a little smaller: Codex's note). -1 = Codex's first take of A ("initial", fine and less chibi), -2 its
pick ("selected") and B made from it. Squares by the colour runs along the rows (the mode): A-1 ~7, A-2 ~7-7.5,
B-2 ~7.5-9; regrid places the boundaries on the colour edges, so these only seed it.
Every picture is read on SIZE px squares, one pixel per drawn square; the colours of a group cut to COLOURS together by
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


SRC = os.path.join(ROOT, "assets", "source", "zaahen", "codex_picture", "zaahen-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "zaahen", "hd")
GROUPS = ((("A-1",), 32), (("A-2", "B-2"), 40))   # pictures sharing one palette, and its colours
FILES = {"A-1": "A-initial.png", "A-2": "A-selected.png", "B-2": "B-selected.png"}
SIZES = {"A-1": 7.0, "A-2": 7.5, "B-2": 7.5}


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
    ap.add_argument("--size", nargs="*", default=[], metavar="NAME=PX", help="another square for a picture")
    a = ap.parse_args()
    SIZES.update({k: float(v) for k, v in (x.split("=") for x in a.size)})
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
