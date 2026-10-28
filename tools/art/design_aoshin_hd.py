#!/usr/bin/env python3
"""Ao Shin's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_aoshin_hd.py   # writes assets/source/aoshin/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/aoshin/codex_picture, 2026-10-28, Codex 2026-10-28/new-chat-4): asked 1536 and 11 px squares,
delivered A on 1254 and B on 1717 x 916, soft alpha, the outer PNGs = raw/A-selected / raw/B-selected byte for byte
(raw/A-first = a first, finer A, not chosen by Codex). A (hovering upright) is drawn on ~10.5 px squares (the colour
edges' autocorrelation peaks at 11 / 21 / 32 across, 10 / 21 / 31 down), 763 px tall; B (the lunge) on ~8.3 px (9 / 17 /
25 / 32 across, 9 / 16 / 27 down), 393 px tall and 1484 wide - the tail streams far back. A-1 = A read near Codex's
own squares; A-2 = raw/A-first (Codex's first A: the tail curled under him like TFT's idle, ~8 px squares: peaks 4 / 8 /
12 / 16, 802 px tall) on its own squares; B-1 = B on its own squares, B-2 = B on coarser 11 px (a shorter figure).
Every picture is read on SIZE px squares, one pixel per drawn square; its colours cut to COLOURS by k-means in Lab
(design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "aoshin", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "aoshin", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "aoshin-A.png", "A-2": "raw/A-first.png", "B-1": "aoshin-B.png", "B-2": "aoshin-B.png"}
SIZES = {"A-1": 10.5, "A-2": 8.0, "B-1": 8.3, "B-2": 11.0}


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
    for name in FILES:
        d = read(name, SIZES[name])
        op = d[..., 3] > 0
        idx, pal = V.kmeans(d, COLOURS[name])
        out = np.zeros_like(d)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
