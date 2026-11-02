#!/usr/bin/env python3
"""Gromp's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_gromp_hd.py   # writes assets/source/gromp/hd/{A-1,A-2,A-3,B-1}.png (+ _4x)

Step 0 (assets/source/gromp/codex_picture/gromp-picture, 2026-11-01, Codex 2026-11-01/new-chat-5,
gromp_picture_done.zip): asked 1536 and 11 px squares; delivered gromp-A.png / gromp-B.png (Codex's own read-back at
56 x 32 / 56 x 31 on 11 px, muddy: the face lost) and the raws: raw/gromp-A-initial.png (1536 x 1024, real alpha over
a black glow; the biggest, clearest face), raw/gromp-A-revised.png and raw/gromp-B-generated.png (1254, smaller).
Squares by regrid's edge phase: the first A 12 px (105 x 54), the revised A 12 px (73 x 41), B 13 px (67 x 38).
A-1 = the first A on 12, A-2 = the first A on 16 (coarser), A-3 = the revised A on 12, B-1 = B on 13 (one pixel per
drawn square). Every picture is read on SIZE px squares; its colours cut to COLOURS by k-means in Lab
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


SRC = os.path.join(ROOT, "assets", "source", "gromp", "codex_picture", "gromp-picture")
OUT = os.path.join(ROOT, "assets", "source", "gromp", "hd")
COLOURS = {"A-1": 32, "A-2": 28, "A-3": 28, "B-1": 28}
FILES = {"A-1": "raw/gromp-A-initial.png", "A-2": "raw/gromp-A-initial.png", "A-3": "raw/gromp-A-revised.png",
         "B-1": "raw/gromp-B-generated.png"}
SIZES = {"A-1": 12.0, "A-2": 16.0, "A-3": 12.0, "B-1": 13.0}
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
