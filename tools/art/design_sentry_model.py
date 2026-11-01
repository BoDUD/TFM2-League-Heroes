#!/usr/bin/env python3
"""The Sentry's game-size design: the user's pick of step 0 at its height.

    python tools/art/design_sentry_model.py   # writes assets/source/sentry/hd/idle.png (+ _8x, _core12x)

The pick (2026-11-02, the user: 「造型用这个」 on review_sentry_size's "A-3 34 PPU 1.53"): A-3 (hd/A-3.png, Codex's raw A
read on 12 px squares: 28 x 44, TFT's idle at a slight 3/4, the tall pointed shard at the left, the shorter blunt one
at the right, the azure core in the round hole between them) at 34 game px from the left tip to the bottom points: kept
1:1 at PPU 1.29 (44 rows = 34.1 game px; the review's 1.53 resampled the same picture up by 1.18). Its core (its face:
the laser and the bolts leave from it) sits at CORE_BOX, centre CORE (shown at 12x); nothing is redrawn.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_sentry_hd import lp  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "sentry", "hd")
PPU = 1.29
PICKS = {"idle": "A-3"}   # out -> take, 1:1
CORE_BOX = (9, 17, 21, 30)   # x0, y0, x1, y1: the hole and its rim
CORE = (14, 22)               # the core's centre square (its near-white highlight)


def main():
    for out, take in PICKS.items():
        im = np.asarray(Image.open(lp(os.path.join(HD, f"{take}.png"))).convert("RGBA")).copy()
        Image.fromarray(im).save(lp(os.path.join(HD, f"{out}.png")))
        Image.fromarray(np.repeat(np.repeat(im, 8, 0), 8, 1)).save(lp(os.path.join(HD, f"{out}_8x.png")))
        x0, y0, x1, y1 = CORE_BOX
        Image.fromarray(np.repeat(np.repeat(im[y0:y1, x0:x1], 12, 0), 12, 1)).save(
            lp(os.path.join(HD, f"{out}_core12x.png")))
        print(out, im.shape[1], "x", im.shape[0], f"({im.shape[0] / PPU:.1f} game px at PPU {PPU})")


if __name__ == "__main__":
    main()
