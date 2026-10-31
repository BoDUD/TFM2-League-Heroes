#!/usr/bin/env python3
"""Zippy's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_zippy_hd.py   # writes assets/source/zippy/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/zippy/codex_picture/zippy-picture, 2026-10-31, Codex 2026-10-31/new-chat-2,
zippy_picture_done.zip): asked 1536 and 11 px squares, delivered raw/zippy-A-raw.png (1030 x 1526) and
raw/zippy-B-raw.png (1330 x 1182), hard alpha (round1 drafts kept beside them, not used); Codex's own zippy-A.png /
zippy-B.png are nearest resizes of those onto 1536 and its *-grid11.png an 11 px re-cut (detail lost: not used). The
squares measured by regrid's own edge phase and checked at 3x on the face shards and the crest: A 17.0 px (52 x 83),
B 14.0 px (86 x 78).
A-1 / B-1 = each on its own squares (the most detail); A-2 / B-2 = A-1 / B-1 brought to SHRINK of the squares a side by
pixel_down.pixelate (a smaller figure: read on coarser squares, regrid still follows the drawn 17 / 14 px edges).
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
import pixel_down as PD  # noqa: E402
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "zippy", "codex_picture", "zippy-picture")
OUT = os.path.join(ROOT, "assets", "source", "zippy", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
FILES = {"A-1": "raw/zippy-A-raw.png", "A-2": "raw/zippy-A-raw.png", "B-1": "raw/zippy-B-raw.png",
         "B-2": "raw/zippy-B-raw.png"}
SIZES = {"A-1": 17.0, "A-2": 17.0, "B-1": 14.0, "B-2": 14.0}
SHRINK = {"A-2": 0.8, "B-2": 0.8}


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
        if name in SHRINK:
            d, _ = PD.pixelate(d, SHRINK[name], (d.shape[1] / 2, d.shape[0]), PD.edge_colour(d))
            op_ = d[..., 3] > 0
            ys, xs = np.nonzero(op_)
            d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
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
