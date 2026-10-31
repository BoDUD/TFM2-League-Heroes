#!/usr/bin/env python3
"""The Crimson Raptor's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_raptor_hd.py   # writes assets/source/raptor/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/raptor/codex_picture/raptor-picture, 2026-10-31, Codex 2026-10-31/new-chat-6,
raptor_picture_done.zip): asked 1536 and 11 px squares, delivered raw/raptor-A-raw.png (1254, its revised A: the red
crest point added), raw/raptor-A-initial-raw.png (1254, no crest point, a bigger face) and raw/raptor-B-raw.png
(1536 x 1024), soft alpha; its own raptor-{A,B}-pixels.png (49 x 38 / 60 x 35) are a downscale of those (muddy, not
used). The squares measured by regrid's own edge phase: A 11 px (75 x 56), A initial 9 px (110 x 82), B 9 px
(100 x 54; on 11 px it reads 93 x 51, a little coarser).
A-1 = A on 11, A-2 = the initial A on 9, B-1 = B on 9, B-2 = B on 11 (one pixel per drawn square).
Every picture is read on SIZE px squares; its colours cut to COLOURS by k-means in Lab (design_varus.kmeans),
alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "raptor", "codex_picture", "raptor-picture")
OUT = os.path.join(ROOT, "assets", "source", "raptor", "hd")
COLOURS = {"A-1": 32, "A-2": 32, "B-1": 32, "B-2": 32}
FILES = {"A-1": "raw/raptor-A-raw.png", "A-2": "raw/raptor-A-initial-raw.png", "B-1": "raw/raptor-B-raw.png",
         "B-2": "raw/raptor-B-raw.png"}
SIZES = {"A-1": 11.0, "A-2": 9.0, "B-1": 9.0, "B-2": 11.0}
SHRINK = {}


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
