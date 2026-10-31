#!/usr/bin/env python3
"""The Crimson Brambleback's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_brambleback_hd.py   # writes assets/source/brambleback/hd/{A-1,B-1}.png (+ _4x)

Step 0 (assets/source/brambleback/codex_picture/brambleback-picture, 2026-10-31, Codex 2026-10-31/new-chat-4,
brambleback_picture_done.zip): asked 1536 and 11 px squares; its own 11 px cuts (brambleback-A/B.png, 54 x 40 and
62 x 37) lost the face, so only its raw drafts are read: raw/brambleback-{A,B}-generated.png (1254 canvases, soft
alpha), drawn on 6 px squares (A, 201 x 132) and 7 px (B, 131 x 74), measured by regrid's own edge phase and counted
on the face at 4x.
A-1 / B-1 = each raw on its own squares (one pixel per drawn square); a smaller PPU is the size review's (and the
rig's) own pixelate from these.
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


SRC = os.path.join(ROOT, "assets", "source", "brambleback", "codex_picture", "brambleback-picture")
OUT = os.path.join(ROOT, "assets", "source", "brambleback", "hd")
COLOURS = {"A-1": 32, "B-1": 32}
FILES = {"A-1": "raw/brambleback-A-generated.png", "B-1": "raw/brambleback-B-generated.png"}
SIZES = {"A-1": 6.0, "B-1": 7.0}


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
