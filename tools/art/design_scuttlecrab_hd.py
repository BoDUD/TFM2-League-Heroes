#!/usr/bin/env python3
"""The Scuttle Crab's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_scuttlecrab_hd.py   # writes assets/source/scuttlecrab/hd/{A-1,A-2,A-3,B-1,B-3}.png (+ _4x)

Step 0 (assets/source/scuttlecrab/codex_picture/scuttle-picture, 2026-11-01, Codex 2026-11-01/new-chat-4,
scuttle_picture_done.zip): asked 1536 and 11 px squares, delivered two drafts with soft alpha, raw/scuttle-A-original.png
(1254, 3/4) and raw/scuttle-B-original.png (1512x1040, side view), plus its own 46x32 / 50x33 readings
(scuttle-A-logical.png, scuttle-B-logical.png: sampled down, the face and the plates muddy).
The squares measured by regrid's own edge phase and counted on the outline's steps at 8x: A 8 px; B 6 px (regrid finds
12, every other edge), read at 12 to stay near A's size (at 6 it is ~230 squares wide).
A-1 = the A draft on its squares, A-2 = the same on squares twice as big, A-3 = Codex's 46x32; B-1 = the B draft on 12 px,
B-3 = Codex's 50x33. Every picture is read on SIZE px squares; its colours cut to COLOURS by k-means in Lab
(design_varus.kmeans), alpha 0/255. The *-logical files are taken as they are.
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


SRC = os.path.join(ROOT, "assets", "source", "scuttlecrab", "codex_picture", "scuttle-picture")
OUT = os.path.join(ROOT, "assets", "source", "scuttlecrab", "hd")
COLOURS = {"A-1": 32, "A-2": 24, "B-1": 32}
FILES = {"A-1": "raw/scuttle-A-original.png", "A-2": "raw/scuttle-A-original.png", "A-3": "scuttle-A-logical.png",
         "B-1": "raw/scuttle-B-original.png", "B-3": "scuttle-B-logical.png"}
SIZES = {"A-1": 8.0, "A-2": 16.0, "B-1": 12.0}
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
        if name not in SIZES:
            out = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
            Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
            Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
            print(name, out.shape[1], "x", out.shape[0], "(as delivered)")
            continue
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
