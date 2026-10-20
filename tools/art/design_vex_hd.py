#!/usr/bin/env python3
"""Vex's step-0 pictures read back on their own grid, one palette for all four.

    python tools/art/design_vex_hd.py [--size 9]   # writes assets/source/vex/hd/{A,B,SA,SB}.png (+ _4x)

Step 0 (assets/source/vex/codex_picture, 2026-10-20, Codex new-chat-3): A / B (3/4 front, the Shadow risen / lying flat)
and SA / SB (the side, facing right) drawn on 1254 squares (raw/*-generated.png; asked 1536 and 11 px squares). Its own
1536 cuts are those raws resampled to 11 px, so the raws are read: their outline steps are 9 px (regrid's guesses 9 for
B / SA / SB, 10 for A). Its HANDOFF: soft edges, semi-transparent rim.
regrid.py reads each one pixel per drawn square; the painted colours of all four are cut to COLOURS together by k-means
in Lab (design_varus.kmeans), alpha 0/255. BODY_TOP: rows above her own ear tips (the risen Shadow's), so a picture's
height for the game is hers alone - B's height for A, SB's for SA (the same 9 px squares, soles on one line).
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


SRC = os.path.join(ROOT, "assets", "source", "vex", "codex_picture", "vex-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "vex", "hd")
COLOURS = 40
NAMES = ("A", "B", "SA", "SB")
SIZE = 9.0


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"vex-{name}-generated.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def body_top():
    """Rows above her ear tips in each picture: the flat-Shadow pictures' heights are hers."""
    h = {n: Image.open(lp(os.path.join(OUT, f"{n}.png"))).height for n in NAMES}
    return {"A": h["A"] - h["B"], "B": 0, "SA": h["SA"] - h["SB"], "SB": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=float, default=SIZE, help="square size in px")
    a = ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    parts = [read(n, a.size) for n in NAMES]
    h = max(p.shape[0] for p in parts)
    both = np.zeros((h, sum(p.shape[1] for p in parts), 4), np.uint8)
    x = 0
    for p in parts:
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    for name, p in zip(NAMES, parts):
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])
    print("rows above her ear tips", body_top())


if __name__ == "__main__":
    main()
