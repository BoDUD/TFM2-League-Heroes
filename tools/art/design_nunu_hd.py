#!/usr/bin/env python3
"""Nunu & Willump's step-0 pictures read back on their own grid: one palette for the two.

    python tools/art/design_nunu_hd.py   # writes assets/source/nunu/hd/{A,SA}.png (+ _4x)

Step 0 (assets/source/nunu/codex_picture/nunu-picture, 2026-10-23, Codex 2026-10-23/new-chat-3): A the idle 3/4 front,
SA the side, raw on 1254 squares (asked 1536 and 11 px squares; soft alpha, no exact grid). Codex drew far finer than
asked: the edge profiles' autocorrelation peaks at 4-4.6 px (A) and 3.7-4 (SA), about 190 rows - no game-size design.
So both are brought to 105 rows from the pompom to the soles (A 852 px tall -> 8.1 px squares, SA 694 -> 6.6;
Illaoi's 102), a resample, not a readback: the step-1 model redraws on the game grid anyway.
Each RAW draft's figure (alpha >= 128) is box-averaged to ROWS rows (colours weighted by alpha, a square figure when
most of it is); the colours of the two cut to 40 together by k-means in Lab (design_varus.kmeans), alpha 0/255.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_varus as V  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


SRC = os.path.join(ROOT, "assets", "source", "nunu", "codex_picture", "nunu-picture", "raw")
OUT = os.path.join(ROOT, "assets", "source", "nunu", "hd")
GROUPS = ((("A", "SA"), 40),)   # pictures sharing one palette, and its colours
ROWS = {"A": 105, "SA": 105}


def read(name, rows):
    """The figure (alpha >= 128) brought to `rows` rows by box averages: a square is figure when most of it is."""
    im = Image.open(lp(os.path.join(SRC, f"nunu-{name}-generated.png"))).convert("RGBA")
    a = np.asarray(im)
    ys, xs = np.nonzero(a[..., 3] >= 128)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    size = im.height / rows
    w = round(im.width / size)
    pre = np.asarray(im).astype(float)
    pre[..., :3] *= pre[..., 3:] / 255          # colours weighted by alpha (no grey fringe)
    box = np.asarray(Image.fromarray(pre.astype(np.uint8)).resize((w, rows), Image.BOX)).astype(float)
    alpha = np.asarray(im.split()[3].resize((w, rows), Image.BOX))
    d = np.zeros((rows, w, 4), np.uint8)
    op = alpha >= 128
    d[..., :3] = np.clip(box[..., :3] * 255 / np.maximum(alpha[..., None], 1), 0, 255)
    d[..., 3] = np.where(op, 255, 0)
    print(name, "square", round(size, 2))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    for names, colours in GROUPS:
        parts = [read(n, ROWS[n]) for n in names]
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
