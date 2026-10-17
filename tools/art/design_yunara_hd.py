#!/usr/bin/env python3
"""Yunara's dense (PPU) designs: Codex's step-0 pictures read back on their own grid, one palette for all three.

    python tools/art/design_yunara_hd.py   # writes assets/source/yunara/hd/{A,B,W}.png (+ _4x previews)

Step 0 (assets/source/yunara/codex_picture, 2026-10-17, Codex new-chat-3): A (the idle, six beads round her), B (the
palm strike, eight beads arcing over her head) and W (eight beads and the dragon-head bead) on 1254 squares, not the asked
1536. Asked for 72 squares of 11 px ornament top to soles, Codex drew squares of 9 px (A, W) and 8 px (B) (its HANDOFF:
no exact grid, soft edges). regrid.py reads each one pixel per drawn square; the painted colours of all three are cut
to COLOURS together by k-means in Lab (design_varus.kmeans, the Aphelios way), alpha 0/255 (alpha < 128 dropped).
"""
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


SRC = os.path.join(ROOT, "assets", "source", "yunara", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "yunara", "hd")
COLOURS = 40
SIZES = {"A": 9.0, "B": 8.0, "W": 9.0}   # regrid's own measure, the same on x and y


def read(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"yunara-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, SIZES[name])
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    os.makedirs(lp(OUT), exist_ok=True)
    parts = {k: read(k) for k in SIZES}
    h = max(p.shape[0] for p in parts.values())
    both = np.zeros((h, sum(p.shape[1] for p in parts.values()), 4), np.uint8)
    x = 0
    spans = {}
    for k, p in parts.items():
        both[:p.shape[0], x:x + p.shape[1]] = p
        spans[k] = (x, p.shape)
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for k, (x, shape) in spans.items():
        part = out[:shape[0], x:x + shape[1]]
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{k}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{k}_4x.png")))
        print(k, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()
