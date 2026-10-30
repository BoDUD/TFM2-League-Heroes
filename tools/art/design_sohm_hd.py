#!/usr/bin/env python3
"""Sohm's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_sohm_hd.py   # writes assets/source/sohm/hd/{A-1,A-2,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/sohm/codex_picture, 2026-10-30, Codex 2026-10-30/new-chat-4, sohm_model_draft.zip): asked
1536 and 11 px squares, delivered sohm-A.png (= raw/exec-8ed0ded7-....png, 1254, figure ~436 x 556 at alpha 128) and
sohm-B.png (= raw/exec-c45f50ae-....png, 1254, ~446 x 554), soft alpha; the other three raws are Codex's own dropped
tries. The squares measured by regrid's own edge phase: A 7.0 px, B 8.0 px (both look 7-8 px at 5x).
A-1 / B-1 = each on its own squares (the most detail), A-2 / B-2 = on 9 / 10 px (a smaller figure).
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


SRC = os.path.join(ROOT, "assets", "source", "sohm", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "sohm", "hd")
COLOURS = {"A-1": 36, "A-2": 32, "B-1": 36, "B-2": 32}
A_RAW = "raw/exec-8ed0ded7-e6f6-439e-ab29-29a48c7a37c4.png"   # = sohm-A.png
B_RAW = "raw/exec-c45f50ae-48f6-4bee-b64e-83b58263c65d.png"   # = sohm-B.png
FILES = {"A-1": A_RAW, "A-2": A_RAW, "B-1": B_RAW, "B-2": B_RAW}
SIZES = {"A-1": 7.0, "A-2": 9.0, "B-1": 8.0, "B-2": 10.0}


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
