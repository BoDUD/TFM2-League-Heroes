#!/usr/bin/env python3
"""Pantheon's dense (PPU) designs: Codex's step-0 pictures read back on their own grid, one palette for both.

    python tools/art/design_pantheon_hd.py [--size A B]   # writes assets/source/pantheon/hd/{A,B}.png (+ _4x previews)

Step 0 (assets/source/pantheon/codex_picture, 2026-10-16, Codex new-chat-2): A (League's idle, the spear held low) and B
(Comet Spear's wind-up, the spear over his shoulder) on 1254 squares (asked 1536). Asked for 76 squares of 11 px from
the helmet's top to the soles, Codex drew squares of about 6.7 px (the autocorrelation of each picture's colour edges,
work: A 6.64 down / 13.17 = 2 x 6.6 across, B 6.86 / 6.70; regrid's own measure took 7.0 / 8.0) - its HANDOFF: not on
the 11-px grid, soft edges. regrid.py reads each one pixel per drawn square at SIZE; the painted colours of both are cut
to COLOURS together by k-means in Lab (design_varus.kmeans), alpha 0/255 (Codex's soft edge of alpha < 128 dropped).
The game shows it at PPU 1.5 (the user's pick with the kit plan) at the height picked from
tools/art/review_pantheon_ppu.py.
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


SRC = os.path.join(ROOT, "assets", "source", "pantheon", "codex_picture", "pantheon-picture")
OUT = os.path.join(ROOT, "assets", "source", "pantheon", "hd")
COLOURS = 40
SIZES = (6.7, 6.8)


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"pantheon-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs=2, type=float, default=SIZES, help="square sizes of A and B in px")
    a = ap.parse_args()
    os.makedirs(lp(OUT), exist_ok=True)
    A, B = read("A", a.size[0]), read("B", a.size[1])
    h = max(A.shape[0], B.shape[0])
    both = np.zeros((h, A.shape[1] + B.shape[1], 4), np.uint8)
    both[:A.shape[0], :A.shape[1]] = A
    both[:B.shape[0], A.shape[1]:] = B
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    for name, part in (("A", out[:A.shape[0], :A.shape[1]]), ("B", out[:B.shape[0], A.shape[1]:])):
        Image.fromarray(part).save(lp(os.path.join(OUT, f"{name}.png")))
        Image.fromarray(np.repeat(np.repeat(part, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{name}_4x.png")))
        print(name, part.shape[1], "x", part.shape[0])


if __name__ == "__main__":
    main()
