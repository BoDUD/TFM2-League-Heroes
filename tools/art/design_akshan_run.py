#!/usr/bin/env python3
"""Akshan's walk: Codex's skin swap over oppi's Swain run (assets/source/akshan/codex_run/akshan-run-sheet.png, 2026-10-18,
tools/art/pack_akshan_run.py) read back as 8 frames on the design's grid for tools/art/rig_akshan.py.

    python tools/art/design_akshan_run.py      # -> assets/source/akshan/hd/run_<k>.png (k = 0..7) + a review sheet

The sheet came back 1862 x 845 (asked 2016 x 912 = 84 x 76 squares a cell at 6 px): Codex kept the reference's density,
5.5 px a square (a frame 375-384 px tall against the design's 69 rows). Each figure is found as a big non-green piece
(the key is near #00FF00 but not exact: (2,250,2) .. (18,242,13)), read back at 5.5 px (regrid.py), alpha 0/255 at 128;
the key's fringe (pixels whose green stands 40 over red and blue) is cleared; every colour is snapped to the design's own
palette (no colour the idle does not have); 8-connected crumbs of at most 4 squares apart from the figure are dropped.
The frames keep oppi's order (contact, down, passing, up, then the other leg).
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402
import rig_akshan as A  # noqa: E402

lp = A.lp
SRC = os.path.join(ROOT, "assets", "source", "akshan")
SHEET = os.path.join(SRC, "codex_run", "akshan-run-sheet.png")
SIZE = 5.5


def figures(a):
    g = (a[..., 1] > 180) & (a[..., 1] - np.maximum(a[..., 0], a[..., 2]) > 100)
    op = ~g
    lbl, n = ndimage.label(ndimage.binary_closing(op, iterations=3))
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    boxes = []
    for k in [k + 1 for k, s in enumerate(sizes) if s > 20000]:
        ys, xs = np.nonzero(lbl == k)
        boxes.append((ys.min(), ys.max(), xs.min(), xs.max()))
    boxes.sort(key=lambda b: (b[0] // 300, b[2]))
    if len(boxes) != 8:
        sys.exit(f"{len(boxes)} figures found, not 8")
    return [np.dstack([a[y0:y1 + 1, x0:x1 + 1], np.where(op[y0:y1 + 1, x0:x1 + 1], 255, 0)]).astype(np.uint8)
            for y0, y1, x0, x1 in boxes]


def main():
    a = np.asarray(Image.open(lp(SHEET)).convert("RGB")).astype(np.int64)
    des = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")).astype(np.int64)
    pal = np.unique(des[des[..., 3] > 0][:, :3], axis=0)
    out = []
    for k, sub in enumerate(figures(a)):
        d, _, _ = RG.regrid(sub, SIZE)
        d = d.astype(np.int64)
        op = d[..., 3] >= 128
        fringe = (d[..., 1] - np.maximum(d[..., 0], d[..., 2])) > 40
        op &= ~fringe
        px = d[op][:, :3]
        d[op, :3] = pal[np.argmin(((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1), 1)]
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        sizes = ndimage.sum(op, lbl, range(1, n + 1))
        for j, z in enumerate(sizes):
            if z <= 4:
                op[lbl == j + 1] = False
        d[..., 3] = np.where(op, 255, 0)
        d[~op] = 0
        ys, xs = np.nonzero(op)
        d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
        Image.fromarray(d).save(lp(os.path.join(SRC, "hd", f"run_{k}.png")))
        out.append(d)
        print(f"frame {k}: {d.shape[1]} x {d.shape[0]} squares, {n - 1} crumbs before cleaning")


if __name__ == "__main__":
    main()
