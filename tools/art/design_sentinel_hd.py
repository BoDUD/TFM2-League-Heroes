#!/usr/bin/env python3
"""The Blue Sentinel's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_sentinel_hd.py   # writes assets/source/sentinel/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/sentinel/codex_picture/sentinel-picture, 2026-10-31, Codex 2026-10-31/new-chat-3,
sentinel_picture_done.zip): asked 1536 and 11 px squares, delivered 1254 canvases with soft alpha, two rounds each:
raw/sentinel-{A,B}-initial.png and raw/sentinel-{A,B}-revised.png (= its sentinel-A.png / sentinel-B.png). The
squares measured by regrid's own edge phase: A revised 8 px (97 x 64), A initial 10 px (84 x 64), B revised 10 px
(its rows step 10-11.5, read on 10), B initial 10 px.
A-1 / B-1 = the revised round, A-2 / B-2 = the initial one, each on its own squares (one pixel per drawn square).
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


SRC = os.path.join(ROOT, "assets", "source", "sentinel", "codex_picture", "sentinel-picture")
OUT = os.path.join(ROOT, "assets", "source", "sentinel", "hd")
COLOURS = {"A-1": 32, "A-2": 32, "B-1": 32, "B-2": 32}
FILES = {"A-1": "raw/sentinel-A-revised.png", "A-2": "raw/sentinel-A-initial.png", "B-1": "raw/sentinel-B-revised.png",
         "B-2": "raw/sentinel-B-initial.png"}
SIZES = {"A-1": 8.0, "A-2": 10.0, "B-1": 10.0, "B-2": 10.0}
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
