#!/usr/bin/env python3
"""Darius's dense (PPU 1.5) design: Codex's step-0 picture read back on its own grid.

    python tools/art/design_darius_hd.py [--review DIR]

Asked (assets/source/darius/PICTURE_PROMPT_PPU.md) for 63 squares of 11 px from the axe's ring to the soles, Codex's
image_gen drew two pictures (assets/source/darius/hd/raw/, its HANDOFF.md), both with real alpha this time:
generation-01 on ~9.8-px squares (119 rows: cut to 63 it would lose nearly half its lines) and generation-02 on
17.2 x 16.45-px squares (the autocorrelation of its colour edges peaks at 16-17), 61 rows from the ring to the soles -
read here, nothing cut. design_fiora_hd.grid() reads it one square a design square (one fitted pitch and phase per
axis, the median of each square's middle half: regrid.py's peak picking jitters on these pictures), the colours cut to
COLOURS by k-means in Lab (design_varus.kmeans) -> hd/design.png. Codex's face is kept as drawn.

With --review: <dir>/darius_ppu_size.png (the design at PPU 1.5 and at 1.45, next to Darius now, Jax, Xin Zhao and
Fiora as the game draws them, feet on one line, 3 screen pixels a game pixel) and <dir>/darius_ppu_closeup.png
(Codex's picture and the design at 8x).
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
import design_fiora_hd as FD  # noqa: E402
import design_varus as V  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "darius", "hd")
PITCH = (15.0, 18.0)              # generation-02's squares lie in here (and not their doubles)
COLOURS = 40
PEERS = ["darius", "jax", "xinzhao", "fiora"]


def lp(path):
    return FD.lp(path)


def read():
    a = np.asarray(Image.open(lp(os.path.join(HD, "raw", "generation-02.png"))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    FD.PITCH = PITCH
    d, size = FD.grid(a)
    op = d[..., 3] > 0
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out, size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    d, size = read()
    Image.fromarray(d).save(lp(os.path.join(HD, "design.png")))
    print(f"square {size[0]:.2f} x {size[1]:.2f}, design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    im = Image.fromarray(d)
    cells = [(f"new 1.5: {d.shape[0] / 1.5:.1f}px", FD.shown(im, 1.5, 3)),
             (f"new 1.45: {d.shape[0] / 1.45:.1f}px", FD.shown(im, 1.45, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == "darius" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "darius_ppu_size.png"))
    raw = Image.open(lp(os.path.join(HD, "raw", "generation-02.png"))).convert("RGBA")
    raw = raw.crop(raw.getbbox())
    z = 8
    cdx = raw.resize((round(raw.width * d.shape[0] * z / raw.height), d.shape[0] * z), Image.LANCZOS)
    FD.strip([("Codex's picture (generation-02)", cdx),
              (f"design {d.shape[1]}x{d.shape[0]} on its own squares", FD.shown(im, 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "darius_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
