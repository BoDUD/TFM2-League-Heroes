#!/usr/bin/env python3
"""The Sentry's step-0 pictures read back on their own grid, each on its own palette.

    python tools/art/design_sentry_hd.py   # writes assets/source/sentry/hd/{A-1,A-2,A-3,B-1,B-2}.png (+ _4x)

Step 0 (assets/source/sentry/codex_picture/sentry-picture, 2026-11-02, Codex 2026-11-02/new-chat,
sentry_picture_done.zip): asked 1536 and 11 px squares; delivered sentry-A.png / sentry-B.png (Codex's own read-back
at 22 x 34 / 20 x 34 on 11 px: coarse, the core a blur of 4 squares) and the raw both came from:
raw/generation-02.png (1774 x 887, A on the left half, B on the right, soft alpha), drawn on 9 px squares (counted on
the outline steps). A-1 = raw A on 9 (one pixel per drawn square), A-2 = Codex's own A on 11, A-3 = raw A on 12
(coarser, between the two); B-1 = raw B on 9, B-2 = Codex's own B. Every picture is read on SIZE px squares; its
colours cut to COLOURS by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "sentry", "codex_picture", "sentry-picture")
OUT = os.path.join(ROOT, "assets", "source", "sentry", "hd")
RAW = "raw/generation-02.png"
# name -> (file, x range of the file or None, square px, colours)
PICS = {
    "A-1": (RAW, (0, 887), 9.0, 28),
    "A-2": ("sentry-A.png", None, 11.0, 24),
    "A-3": (RAW, (0, 887), 12.0, 24),
    "B-1": (RAW, (887, 1774), 9.0, 28),
    "B-2": ("sentry-B.png", None, 11.0, 24),
}


def read(name):
    f, xr, size, _ = PICS[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, f))).convert("RGBA")).copy()
    if xr:
        a = a[:, xr[0]:xr[1]].copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    argparse.ArgumentParser().parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    for name, (_, _, _, colours) in PICS.items():
        d = read(name)
        op = d[..., 3] > 0
        idx, pal = V.kmeans(d, colours)
        out = np.zeros_like(d)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        Image.fromarray(out).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(out, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, out.shape[1], "x", out.shape[0])


if __name__ == "__main__":
    main()
