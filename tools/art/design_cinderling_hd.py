#!/usr/bin/env python3
"""The Cinderling's (绯红树怪) step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_cinderling_hd.py   # writes assets/source/cinderling/hd/{A-1,B-1}.png (+ _4x)

Step 0 (assets/source/cinderling/codex_picture/cinderling-picture, 2026-11-02, Codex 2026-11-02/new-chat-3,
cinderling_picture_done.zip): asked 1536 and 11 px squares; Codex drew 1254 canvases with soft alpha, two rounds each,
and called its own second round (cinderling-A/B.png) a reference only. The first rounds are the better drawings (the
face: the big eye, the G spiral, the fangs): raw/cinderling-A-generation-1.png on 8 px squares (A, 89 x 71) and
raw/cinderling-B-generation-1.png on 7 px (B), measured by regrid's own edge phase and counted on the eye at 5x.
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


SRC = os.path.join(ROOT, "assets", "source", "cinderling", "codex_picture", "cinderling-picture")
OUT = os.path.join(ROOT, "assets", "source", "cinderling", "hd")
COLOURS = {"A-1": 32, "B-1": 32}
FILES = {"A-1": "raw/cinderling-A-generation-1.png", "B-1": "raw/cinderling-B-generation-1.png"}
SIZES = {"A-1": 8.0, "B-1": 7.0}


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
