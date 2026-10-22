#!/usr/bin/env python3
"""Illaoi's step-0 pictures read back on their own grid: one palette for her two, one for the tentacle.

    python tools/art/design_illaoi_hd.py   # writes assets/source/illaoi/hd/{A,SA,T}.png (+ _4x)

Step 0 (assets/source/illaoi/codex_picture/illaoi-picture, 2026-10-23, Codex 2026-10-22/new-chat-5): A her idle 3/4
front, SA "the side" (drawn smaller and still a little 3/4), T a tentacle from the front, raw on 1254 squares (asked 1536
and 11 px squares; soft alpha, no exact grid). Codex's squares, by a comb over the edge profiles: A 9.8 both ways, T 10.0;
SA has no clear peak - read on 8.0 (the least-error plateau 7.8-8.2, 104 rows against A's 102, so drawn with A's count).
Every picture is read on SIZE px squares, one pixel per drawn square (the RAW drafts, not Codex's own cut); her painted
colours cut to COLOURS together and the tentacle's to its own by k-means in Lab (design_varus.kmeans), alpha 0/255.
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


SRC = os.path.join(ROOT, "assets", "source", "illaoi", "codex_picture", "illaoi-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "illaoi", "hd")
GROUPS = ((("A", "SA"), 40), (("T",), 24))   # pictures sharing one palette, and its colours
SIZES = {"A": 9.8, "SA": 8.0, "T": 10.0}


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"illaoi-{name}.png"))).convert("RGBA")).copy()
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
    for names, colours in GROUPS:
        parts = [read(n, SIZES[n]) for n in names]
        h = max(p.shape[0] for p in parts)
        both = np.zeros((h, sum(p.shape[1] for p in parts), 4), np.uint8)
        x = 0
        for p in parts:
            both[:p.shape[0], x:x + p.shape[1]] = p
            x += p.shape[1]
        op = both[..., 3] > 0
        idx, pal = V.kmeans(both, colours)
        out = np.zeros_like(both)
        out[op, :3] = pal[idx[op]]
        out[op, 3] = 255
        x = 0
        for name, p in zip(names, parts):
            part = out[:p.shape[0], x:x + p.shape[1]]
            x += p.shape[1]
            part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))]
            Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
            Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
            print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()
