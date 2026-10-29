#!/usr/bin/env python3
"""Steb's step-0 pictures read back on their own squares and one step coarser, each on its own palette.

    python tools/art/design_steb_hd.py   # writes assets/source/steb/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/steb/codex_picture, 2026-10-29, Codex 2026-10-29/new-chat-5, steb_picture_done.zip): asked
1536 and 11 px squares, delivered 1254 raw canvases with soft alpha (raw/steb-{A,B}-raw.png) and Codex's own 40x54 /
50x40 cut by point sampling (B squeezed sideways, its HANDOFF says so) - so the raw drafts are read. regrid's measure:
A (the idle, a baton on his shoulder) ~8 px squares, 104 rows quiff to soles; B (the fighting crouch, the batons
level) ~9 px, 81 rows. -1 is read on the drawn square, -2 a step coarser (fewer rows for a lower PPU).
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


SRC = os.path.join(ROOT, "assets", "source", "steb", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "steb", "hd")
COLOURS = {"A-1": 36, "A-2": 36, "B-1": 36, "B-2": 36}
FILES = {"A-1": "steb-A-raw.png", "A-2": "steb-A-raw.png", "B-1": "steb-B-raw.png", "B-2": "steb-B-raw.png"}
SIZES = {"A-1": 8.0, "A-2": 10.5, "B-1": 9.0, "B-2": 11.5}


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
