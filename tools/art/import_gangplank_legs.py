#!/usr/bin/env python3
"""Gangplank's walk legs drawn by Codex along the guides of tools/art/pack_gangplank_legs.py (the delivery composited on
the template: the upper body is the template's own squares, checked pixel for pixel by Codex) read back cell by cell.

    python tools/art/import_gangplank_legs.py     # -> assets/source/gangplank/hd/run_<k>.png (k = 0..7)

Each cell (CW x CH squares at Z px, legs_guides.json) sampled in the middle of each square, the key removed, trimmed
(soles on the bottom row: one foot is planted in every frame of the cycle). Prints each frame's boots against the hips
(the red sash's middle) to check the legs trade front and back.
"""
import json
import os

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "gangplank")


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


def main():
    g = json.load(open(lp(os.path.join(SRC, "hd", "legs_guides.json")), encoding="utf-8"))
    Z, CW, CH = g["Z"], g["CW"], g["CH"]
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_run", "gangplank-legs.png"))).convert("RGB")).astype(int)
    offsets = []
    for i in range(8):
        cx, cy = (i % 4) * CW * Z, (i // 4) * CH * Z
        c = a[cy + Z // 2:cy + CH * Z:Z, cx + Z // 2:cx + CW * Z:Z]
        key = (c[..., 1] > 200) & (c[..., 0] < 90) & (c[..., 2] < 90)
        fig = ~key
        lbl, k = ndimage.label(fig, structure=np.ones((3, 3)))
        sizes = ndimage.sum(fig, lbl, range(1, k + 1))
        fig = np.isin(lbl, [j + 1 for j, s in enumerate(sizes) if s > 4])
        rgba = np.zeros(c.shape[:2] + (4,), np.uint8)
        rgba[fig, :3] = c[fig]
        rgba[fig, 3] = 255
        ys, xs = np.nonzero(fig)
        f = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        offsets.append((int(xs.min()), int(ys.min())))           # the trim, for stamp_gangplank_boots.py
        Image.fromarray(f).save(lp(os.path.join(SRC, "hd", f"run_{i}.png")))
        h = f.shape[0]
        fi = f.astype(int)
        low = fi[h // 2:h - 8]
        sash = (low[..., 3] > 0) & (low[..., 0] > 170) & (low[..., 1] < 90) & (low[..., 2] < 90)
        hx = np.nonzero(sash)[1].mean()
        boot = (fi[..., 3] > 0) & (fi[..., 0] > 60) & (fi[..., 0] < 150) & (fi[..., 1] > 30) & (fi[..., 1] < 100) \
            & (fi[..., 2] < 80) & (fi[..., 0] > fi[..., 2] + 25)
        boot[:h - 10] = False
        bl, bk = ndimage.label(boot)
        feet = sorted((round(float(np.nonzero(bl == j)[1].mean() - hx)), int(h - 1 - np.nonzero(bl == j)[0].max()))
                      for j in range(1, bk + 1) if (bl == j).sum() >= 8)
        print(f"frame {i}: {f.shape[1]} x {h}, boots (x from hips, lift): {feet}")
    with open(lp(os.path.join(SRC, "hd", "run_offsets.json")), "w", encoding="utf-8") as fh:
        json.dump(offsets, fh)


if __name__ == "__main__":
    main()
