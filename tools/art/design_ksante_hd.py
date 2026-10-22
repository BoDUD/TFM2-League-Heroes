#!/usr/bin/env python3
"""K'Sante's step-0 pictures read back on their own grid, one palette for all four.

    python tools/art/design_ksante_hd.py   # writes assets/source/ksante/hd/{A,SA,O,SO}.png (+ _4x)

Step 0 (assets/source/ksante/codex_picture, 2026-10-22, Codex 2026-10-22/new-chat): A the base idle 3/4 front, SA its
side, O the All Out idle 3/4 front, SO its side, raw on 1254 squares (asked 1536 and 11 px squares; its HANDOFF: soft
edges, the side views still a little 3/4, the All Out tonfa ends a little under the boots). Codex's own 11 px export
(ksante-*.png) lost the face and most of the crimson coat, so the RAW drafts are read: their squares by the
autocorrelation of the colour-edge profiles (both axes), A 13.5, SA 12.7, O 9.7, SO 9.8 px - the All Out pair is drawn
on finer squares. Each is read one pixel per drawn square; the painted colours of the four are cut to COLOURS together
by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "ksante", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "ksante", "hd")
COLOURS = 48
NAMES = ("A", "SA", "O", "SO")
SIZES = {"A": 13.5, "SA": 12.7, "O": 9.7, "SO": 9.8}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"ksante-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    parts = [read(n, SIZES[n]) for n in NAMES]
    h = max(p.shape[0] for p in parts)
    both = np.zeros((h, sum(p.shape[1] for p in parts), 4), np.uint8)
    x = 0
    for p in parts:
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    for name, p in zip(NAMES, parts):
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()
