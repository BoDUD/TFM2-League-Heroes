#!/usr/bin/env python3
"""Baron Nashor's (纳什男爵) step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_baronnashor_hd.py   # writes assets/source/baronnashor/hd/{A-1,A-2,B-1}.png (+ _4x)

Step 0 (assets/source/baronnashor/codex_picture/baronnashor-picture, 2026-11-03, Codex 2026-11-03/new-chat,
baronnashor_picture_done.zip): asked 1536 and 11 px squares with no legs; the user had Codex add a pair of short hind
legs (「画个腿，不然怎么看出来走动」), so baronnashor-A.png (= raw/baronnashor-A-legs-generated.png: the S-curved idle on two
legs) and baronnashor-B.png (= raw/baronnashor-B-legs-generated.png: reared up, claws spread) are the designs; the
legless raws are history. 1254 canvases with soft alpha. regrid's own edge phase reads A on 11 px and B on 12; by eye
A's outline steps look nearer 13.
A-1 = A on 11 px, A-2 = A on 13 px, B-1 = B on 12 px (one pixel per drawn square); a smaller PPU is the size review's
(and the rig's) own pixelate from these.
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
import regrid as RG  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "baronnashor", "codex_picture", "baronnashor-picture")
OUT = os.path.join(ROOT, "assets", "source", "baronnashor", "hd")
COLOURS = {"A-1": 32, "A-2": 32, "B-1": 32}
FILES = {"A-1": "baronnashor-A.png", "A-2": "baronnashor-A.png", "B-1": "baronnashor-B.png"}
SIZES = {"A-1": 11.0, "A-2": 13.0, "B-1": 12.0}


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
