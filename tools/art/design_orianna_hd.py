#!/usr/bin/env python3
"""Orianna's step-0 pictures read back on their own grid, her body and her ball apart, one palette for both pictures.

    python tools/art/design_orianna_hd.py [--size A B]   # writes assets/source/orianna/hd/{A,B,A_ball,B_ball}.png

Step 0 (assets/source/orianna/codex_picture, 2026-10-16, Codex new-chat-3): A (League's idle, the ball floating before
her) and B (one hand raised to command the ball) on 1254 squares (asked 1536). Asked for 72 squares of 11 px from the
bun to the soles, Codex drew squares of about 7 px, not evenly (the Fourier peak of the colour edges: A 8.0 across /
6.8 down, B 6-7.6; regrid's own measure 7-8) - its HANDOFF: not on one grid, soft alpha. regrid.py reads each one pixel
per drawn square at SIZE; the painted colours of both are cut to COLOURS together by k-means in Lab
(design_varus.kmeans), alpha 0/255 (Codex's soft edge below 128 dropped). The ball is the figure's second-largest
connected part (8-neighbour), written apart: in the game it is its own picture.
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


SRC = os.path.join(ROOT, "assets", "source", "orianna", "codex_picture")
OUT = os.path.join(ROOT, "assets", "source", "orianna", "hd")
COLOURS = 40
SIZES = (7.0, 7.0)


def read(name, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"orianna-{name}.png"))).convert("RGBA")).copy()
    d, sq, _ = RG.regrid(a, size)
    print(name, "square", sq)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def parts(op):
    """Connected parts of a mask (8 neighbours), largest first: lists of (y, x)."""
    seen = np.zeros_like(op)
    out = []
    for y0, x0 in zip(*np.nonzero(op)):
        if seen[y0, x0]:
            continue
        stack, cells = [(y0, x0)], []
        seen[y0, x0] = True
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < op.shape[0] and 0 <= xx < op.shape[1] and op[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        stack.append((yy, xx))
        out.append(cells)
    return sorted(out, key=len, reverse=True)


def split(d):
    """-> (body, ball) cropped; specks (parts under 1% of the body) stay with the body."""
    ps = parts(d[..., 3] > 0)
    ball = np.zeros_like(d)
    ys, xs = np.array(ps[1]).T
    ball[ys, xs] = d[ys, xs]
    body = d.copy()
    body[ys, xs] = 0
    crop = lambda a: a[np.ix_(np.any(a[..., 3] > 0, 1), np.any(a[..., 3] > 0, 0))]
    print("  parts", [len(p) for p in ps[:4]])
    return crop(body), crop(ball)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", nargs=2, type=float, default=SIZES, help="square sizes of A and B in px")
    a = ap.parse_args()
    if not os.path.exists(lp(OUT)):
        os.mkdir(lp(OUT))
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
        body, ball = split(part)
        for tag, im in ((name, body), (name + "_ball", ball), (name + "_full", part)):
            Image.fromarray(im).save(lp(os.path.join(OUT, f"{tag}.png")))
            Image.fromarray(np.repeat(np.repeat(im, 4, 0), 4, 1)).save(lp(os.path.join(OUT, f"{tag}_4x.png")))
        print(name, "body", body.shape[1], "x", body.shape[0], "ball", ball.shape[1], "x", ball.shape[0])


if __name__ == "__main__":
    main()
