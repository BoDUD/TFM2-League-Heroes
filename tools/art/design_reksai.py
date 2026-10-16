#!/usr/bin/env python3
"""Rek'Sai's designs from Codex's step-1 takes: A-2 (the surface idle) and B-2 (burrowed), read back on their own
grids - no cut, no shrink.

    python tools/art/design_reksai.py [--grid DIR]     # --grid: 10x pictures with the square numbers (for rigging)

Step 1 (assets/source/reksai/codex_model, Codex 2026-10-17/new-chat, round 2): asked for 54 squares of 12 px (A, crest
top to claw tips = 36 game px at PPU 1.5, the head ~1.3x) and B at A's scale; Codex drew squares of ~14 px (A) and
~16 px (B) on 1254 canvases with soft edges: A-2 reads back 57 x 70 squares, B-2 33 x 52 - B at A's scale (the crest
band's width 22 vs 25 squares, the heights 33 / 57 as asked 31 / 54). Kept square for square: PPU = 57 / 36 (the user's
36 game px with nothing deleted). regrid.py reads each square, alpha >= 128 is opaque, then one 40-colour palette for
both (k-means in Lab with a farthest-point start, so the fangs' cream and the crest's magenta keep their own colours)
and the outline: every square darker than OUTLINE_SUM becomes the darkest colour. Writes assets/source/reksai/hd/
design_A.png, design_B.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import regrid as RG  # noqa: E402
import design_varus as V  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "reksai")
TAKES = {"A": "reksai-model-A-2.png", "B": "reksai-model-B-2.png"}
COLOURS = 40
OUTLINE_SUM = 90            # r + g + b below this: the outline


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def read(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", TAKES[name]))).convert("RGBA")).copy()
    g, _, _ = RG.regrid(a)
    op = g[..., 3] >= 128
    g[..., 3] = np.where(op, 255, 0)
    g[~op] = 0
    ys, xs = np.nonzero(op)
    return g[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def designs():
    A, B = read("A"), read("B")
    pad = np.zeros((max(A.shape[0], B.shape[0]), A.shape[1] + B.shape[1], 4), np.uint8)
    pad[:A.shape[0], :A.shape[1]] = A
    pad[:B.shape[0], A.shape[1]:] = B
    idx, pal = V.kmeans(pad, COLOURS)
    dark = pal[np.argmin(pal.astype(int).sum(1))]
    out = []
    for k, d in ((0, A), (A.shape[1], B)):
        sub = idx[:d.shape[0], k:k + d.shape[1]]
        q = np.zeros_like(d)
        op = sub >= 0
        q[op, :3] = pal[sub[op]]
        q[op, 3] = 255
        q[op & (d[..., :3].astype(int).sum(-1) < OUTLINE_SUM), :3] = dark
        out.append(q)
    return out


def grid(a, path, z=10):
    h, w = a.shape[:2]
    bg = Image.new("RGBA", (w * z + 40, h * z + 40), (235, 235, 235, 255))
    bg.alpha_composite(Image.fromarray(a).resize((w * z, h * z), Image.NEAREST), (30, 30))
    d = ImageDraw.Draw(bg)
    for x in range(0, w + 1, 5):
        d.line([(30 + x * z, 20), (30 + x * z, 30 + h * z)], fill=(255, 0, 0, 160))
        d.text((32 + x * z, 4), str(x), fill=(0, 0, 0, 255))
    for y in range(0, h + 1, 5):
        d.line([(20, 30 + y * z), (30 + w * z, 30 + y * z)], fill=(255, 0, 0, 160))
        d.text((2, 32 + y * z), str(y), fill=(0, 0, 0, 255))
    bg.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid")
    a = ap.parse_args()
    A, B = designs()
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    for name, d in (("A", A), ("B", B)):
        Image.fromarray(d).save(lp(os.path.join(SRC, "hd", f"design_{name}.png")))
        n = len({tuple(c) for c in d[d[..., 3] > 0][:, :3].tolist()})
        print(f"design_{name}.png {d.shape[1]}x{d.shape[0]} squares, {n} colours")
        if a.grid:
            os.makedirs(a.grid, exist_ok=True)
            grid(d, os.path.join(a.grid, f"grid_{name}.png"))


if __name__ == "__main__":
    main()
