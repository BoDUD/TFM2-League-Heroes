#!/usr/bin/env python3
"""Renata's rig sources from Codex's step-1 takes: the design and the R machine at her scale.

    python tools/art/design_renata.py

  design   assets/source/renata/hd/design.png = take 1 brought to 60 rows by whole rows / columns deleted
           (tools/art/design_renata_cut.py: model1_cut.png, 34 x 60, hair top row 0, soles row 59; picked by me on
           the user's 「codex交付了 然后动作帧按照塔姆那样做吧 做到完美了喊我review」 - the sharpest face: the magenta eye,
           the mask and its gold ring all read).
  machine  assets/source/renata/hd/machine.png: Codex's renata-machine-1 (the chemtech machine alone, drawn after its
           renata-ult-1) read back on its own grid (regrid's 7 px), a k-means palette, then whole rows / columns
           deleted down to her scale in renata-ult-1 (she stands HER_PX px there, hair top to soles, = 60 squares).
           machine.json: where its top-left square goes in design squares (column, row) - machine-1 registered on
           ult-1 by MACHINE_OFF (an SSD search: +8 / -4 px), her standing point in ult-1 HER_FOOT = the design's
           (STAND_COL, 59).
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_renata_cut as DC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renata")
HD = os.path.join(SRC, "hd")
HER_PX = 712                    # renata-ult-1: her silver streak's top y 510, her soles y 1222
HER_FOOT = (440, 1222)          # her standing point there (between the boots), px
STAND_COL = 15                  # the design column over her standing point (between the boots)
MACHINE_OFF = (8, -4)           # machine-1's px moved by this lie on ult-1's
MACHINE_SQ = 7.0                # regrid's measure of machine-1's squares
COLOURS = 32


def lp(path):
    return DC.lp(path)


def main():
    d = np.asarray(Image.open(lp(os.path.join(HD, "model1_cut.png"))).convert("RGBA")).copy()
    Image.fromarray(d).save(lp(os.path.join(HD, "design.png")))
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", "renata-machine-1.png"))).convert("RGBA")).copy()
    ys, xs = np.nonzero(a[..., 3] >= 128)
    x0px, y0px = int(xs.min()), int(ys.min())
    m, sq, _ = RG.regrid(a, MACHINE_SQ)
    m[..., 3] = np.where(m[..., 3] >= 128, 255, 0)
    m = DC.crop(m)
    op = m[..., 3] > 0
    idx, pal = V.kmeans(m, COLOURS)
    q = np.zeros_like(m)
    q[op, :3] = pal[idx[op]]
    q[op, 3] = 255
    k = 60.0 / HER_PX * MACHINE_SQ          # design squares per machine square
    cut = DC.cut(q, k)
    Image.fromarray(cut).save(lp(os.path.join(HD, "machine.png")))
    per_px = 60.0 / HER_PX
    col = (x0px + MACHINE_OFF[0] - HER_FOOT[0]) * per_px + STAND_COL
    row = (y0px + MACHINE_OFF[1] - HER_FOOT[1]) * per_px + 59
    with open(lp(os.path.join(HD, "machine.json")), "w", encoding="utf-8") as f:
        json.dump({"col": int(round(col)), "row": int(round(row)), "k": round(k, 4)}, f)
    print(f"design {d.shape[1]}x{d.shape[0]}; machine read back {m.shape[1]}x{m.shape[0]} -> {cut.shape[1]}x{cut.shape[0]} "
          f"(k {k:.3f}), top-left at design ({col:.1f}, {row:.1f})")


if __name__ == "__main__":
    main()
