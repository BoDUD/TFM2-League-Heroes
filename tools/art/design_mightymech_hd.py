#!/usr/bin/env python3
"""The Mighty Mech's (超级机甲) step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_mightymech_hd.py   # writes assets/source/mightymech/hd/{A-1,B-1}.png (+ _4x)

Step 0 (assets/source/mightymech/codex_picture/mightymech-picture, 2026-11-03, Codex 2026-11-03/new-chat-2,
mightymech_picture_done.zip): asked 1536 and 11 px squares; Codex drew 1254 canvases with soft alpha
(raw/mightymech-A-generated.png facing left, raw/mightymech-B-generated.png) and then resampled them itself onto 34x46 /
48x46 (mightymech-A-1x.png / -B-1x.png: the sampling missed its own grid, mush - not used). The raws measured by
regrid's own edge phase and checked at 6x: both on 7 px squares. A is mirrored to face right like B.
A-1 / B-1 = each raw on its own squares (one pixel per drawn square): A 83x116, B 136x115; a smaller PPU is the size
review's (and the rig's) own pixelate from these.
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


SRC = os.path.join(ROOT, "assets", "source", "mightymech", "codex_picture", "mightymech-picture")
OUT = os.path.join(ROOT, "assets", "source", "mightymech", "hd")
COLOURS = {"A-1": 32, "B-1": 32}
FILES = {"A-1": "raw/mightymech-A-generated.png", "B-1": "raw/mightymech-B-generated.png"}
MIRROR = {"A-1"}   # the raw A faces left
SIZES = {"A-1": 7.0, "B-1": 7.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, FILES[name]))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d[:, ::-1].copy() if name in MIRROR else d


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
