#!/usr/bin/env python3
"""Heimerdinger's step-0 pictures read back on their own grid, one palette for all four.

    python tools/art/design_heimerdinger_hd.py   # writes assets/source/heimerdinger/hd/{A,SA,T,X}.png (+ _4x)

Step 0 (assets/source/heimerdinger/codex_picture, 2026-10-21, Codex new-chat-4, heimerdinger_picture_fixed.zip): raw/ are
Codex's drawings on 1254 squares (asked 1536 and 11 px squares); its fixed/ copies are smoothed down to the asked count
and read muddy, so the raws are read. Their squares are about 4 px (the outline steps at 6x; regrid's own guess, 7-11,
skips steps), so A reads 152 squares tall: a picture to pick the look and size from, redrawn at game size in step 1.
Codex worked from the first pack, which had the turrets swapped: its T (the gear tripod) is the APEX turret and its X
(four legs, two exhaust stacks) the small Q turret - both true to League - so here T = raw X and X = raw T.
Each is read one pixel per drawn square; the painted colours of the four are cut to COLOURS together by k-means in Lab
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


SRC = os.path.join(ROOT, "assets", "source", "heimerdinger", "codex_picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "heimerdinger", "hd")
COLOURS = 48
FROM = {"A": "A", "SA": "SA", "T": "X", "X": "T"}   # ours -> Codex's file (its turrets swapped, see above)
SIZE = 4.0


def read(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"heimerdinger-{FROM[name]}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, SIZE)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    parts = [read(n) for n in FROM]
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
    for name, p in zip(FROM, parts):
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()
