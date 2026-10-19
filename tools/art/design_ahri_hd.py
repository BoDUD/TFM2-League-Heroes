#!/usr/bin/env python3
"""Ahri's dense design: Codex's picture A read back on its own grid, nothing cut, drawn at 85 %.

    python tools/art/design_ahri_hd.py [--review DIR]

Asked (assets/source/ahri/PICTURE_PROMPT_PPU.md, tools/art/pack_ahri_ppu.py) for 60 squares of 11 px from the ear tips
to the soles, Codex's image_gen drew (assets/source/ahri/hd/raw/, its HANDOFF.md) ahri-A-draft (~9-px squares, 124
rows, the tails down to her shins), ahri-A-generated (~16-px squares, 54 x 69) and ahri-S-generated; its own 47 x 60
export (hd/ahri-A.png) was resampled by nearest and broke the face. The user, 2026-10-20, picked 「A 正式稿原样」:
ahri-A-generated read back here one square a design square (design_fiora_hd.grid: one fitted pitch and phase per axis,
the median of each square's middle half), the colours cut to COLOURS by k-means in Lab (design_varus.kmeans), clear
squares carrying no colour -> hd/design.png. Then 「太大了 得缩小一点」 and 「85%」: the 69 rows stand for 34 game rows
(her 40 now x 0.85), PPU 69 / 34.

With --review: <dir>/ahri_design_12x.png (the design at 12x) and <dir>/ahri_ppu_size.png (as the game draws it next
to Ahri now, LeBlanc and Lux).
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

HD = os.path.join(ROOT, "assets", "source", "ahri", "hd")
RAW = os.path.join(HD, "raw", "ahri-A-generated.png")
PITCH = (14.0, 18.0)              # its squares (~16 px) lie in here, not their doubles
COLOURS = 32
ROWS = 34                         # game rows ear tips to soles (her 40 now at 85 %)


def lp(path):
    return FD.lp(path)


def read():
    a = np.asarray(Image.open(lp(RAW)).convert("RGBA")).copy()
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
    ppu = d.shape[0] / ROWS
    print(f"square {size[0]:.2f} x {size[1]:.2f}, design {d.shape[1]}x{d.shape[0]}, PPU {ppu:.4f}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    im = Image.fromarray(d)
    FD.shown(im, 1, 12).save(os.path.join(a.review, "ahri_design_12x.png"))
    cells = [(f"new {ppu:.2f}", FD.shown(im, ppu, 4))]
    for h in ("ahri", "leblanc", "lux"):
        f, p = FD.frame0(h)
        cells.append((("now" if h == "ahri" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 4)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "ahri_ppu_size.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
