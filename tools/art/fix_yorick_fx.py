#!/usr/bin/env python3
"""Two of Codex's Yorick effects drawn again on the grid (assets/source/yorick/fx_fix/pixel_1x, read by
import_yorick_fx.py before the delivery's own):

    python tools/art/fix_yorick_fx.py

k_bite: Codex drew a blue blob with a white face (frame 2 reads as a cute ghost); PROMPTS_FX.md asked for two rows of
ivory fangs snapping shut. Here: 14 x 14, 3 frames, left-right symmetric - the jaws open (an upper and a lower row of
four bone fangs on dark gums), snapped shut with a white-cyan flash where they meet, then cyan motes and mist puffs.
e_mist: Codex drew bracket-like arcs; the prompt asked for a churning ball of Black Mist with a trail. Here: 16 x 10,
4 frames, flying right, top-bottom symmetric - a ball (sea-green rim, near-black teal core, a pale highlight pair, two
cyan motes) churning a step a frame and a tapering trail rippling behind it.
Colours from pack_yorick_fx's ramps (MIST, SOUL, BONE); no outline (effects carry none).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "source", "yorick", "fx_fix", "pixel_1x")


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


M0, M1, M2, M3, M4, M5 = (rgb(c) for c in ("#E8FFF4", "#9CF0C8", "#3CC090", "#1A7A62", "#0C3E38", "#06201E"))
S0, S1, S2, S3 = (rgb(c) for c in ("#FFFFFF", "#CFFFFF", "#80F0FF", "#2CC8E8"))
B0, B1, B2 = (rgb(c) for c in ("#FFFDF0", "#E8DCB8", "#B8A880"))
GUM = (58, 28, 60, 255)


def put(a, pts, c, mirror="lr"):
    """Squares (x, y) and their mirror (lr: across the columns, tb: across the rows)."""
    h, w = a.shape[:2]
    for x, y in pts:
        a[y, x] = c
        if mirror == "lr":
            a[y, w - 1 - x] = c
        else:
            a[h - 1 - y, x] = c


def fang(a, x, y, down):
    """A pointed bone fang 3 squares wide at its root (row y), its tip 2 rows on (down or up), and its mirror."""
    d = 1 if down else -1
    put(a, [(x, y), (x + 1, y)], B1)
    put(a, [(x + 2, y)], B2)
    put(a, [(x, y + d)], B0)
    put(a, [(x + 1, y + d)], B1)
    put(a, [(x + 1, y + 2 * d)], B0 if down else B1)


def bite():
    W = H = 14
    frames = []
    # 1: open - a gum band with two fangs pointing down on top, two pointing up below (mirrored: four a row)
    a = np.zeros((H, W, 4), np.uint8)
    put(a, [(x, 2) for x in range(1, 7)], GUM)
    put(a, [(x, 11) for x in range(1, 7)], GUM)
    for x in (1, 4):
        fang(a, x, 3, True)
        fang(a, x, 10, False)
    frames.append(a)
    # 2: snapped shut - the gums closer, the tips crossing on the middle rows, a white-cyan flash where they meet
    a = np.zeros((H, W, 4), np.uint8)
    put(a, [(x, 4) for x in range(1, 7)], GUM)
    put(a, [(x, 9) for x in range(1, 7)], GUM)
    for x in (1, 4):
        fang(a, x, 5, True)
        fang(a, x, 8, False)
    put(a, [(6, 6), (6, 7)], S0)
    put(a, [(0, 6), (0, 7)], S2)
    put(a, [(1, 5), (6, 5), (6, 8)], S1)
    frames.append(a)
    # 3: cyan motes and dark mist puffs
    a = np.zeros((H, W, 4), np.uint8)
    put(a, [(1, 3), (4, 1), (2, 11)], S2)
    put(a, [(5, 6), (6, 9)], S3)
    put(a, [(2, 7), (3, 7), (3, 8), (4, 4), (5, 4)], M3)
    put(a, [(2, 8), (4, 5), (6, 12)], M4)
    frames.append(a)
    return frames


# the cloud's top half (rows 1-4, mirrored onto rows 8-5): x from 7 to 15, '#' rim, 'o' body, '.' deep, ' ' clear
CLOUD = ["  ## ##  ",
         " #oo#oo# ",
         "#ooo.ooo#",
         "#oo...oo#"]


def mist():
    W, H = 16, 10
    frames = []
    for k in range(4):
        a = np.zeros((H, W, 4), np.uint8)
        for r, line in enumerate(CLOUD, 1):
            for i, ch in enumerate(line):
                if ch != " ":
                    put(a, [(7 + i, r)], {"#": M2, "o": M3, ".": M4}[ch], "tb")
        # the churn: the lit bumps and a pale curl walking round a step a frame
        lit = [[(9, 1), (8, 2)], [(12, 1), (13, 2)], [(15, 3), (14, 2)], [(10, 1), (12, 2)]][k]
        put(a, lit, M1, "tb")
        put(a, [lit[0]], M0, "tb")
        mote = [(12, 3), (10, 4), (13, 4), (11, 3)][k]           # two cyan motes in the mist
        put(a, [mote], S2, "tb")
        # the trail: wisps tapering to the left, rippling
        wisp = [(6, 3), (5, 4), (3, 3), (2, 4)] if k % 2 == 0 else [(6, 4), (4, 3), (3, 4), (1, 3)]
        put(a, wisp[:2], M3, "tb")
        put(a, wisp[2:], M4, "tb")
        put(a, [(5, 3) if k % 2 == 0 else (5, 4)], M2, "tb")
        frames.append(a)
    return frames


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fr in (("k_bite", bite()), ("e_mist", mist())):
        for k, c in enumerate(fr):
            if name == "e_mist":
                assert (c == c[::-1]).all(), (name, k)
            else:
                assert (c == c[:, ::-1]).all(), (name, k)
        strip = np.concatenate(fr, axis=1)
        Image.fromarray(strip).save(os.path.join(OUT, f"yorick_fx_{name}.png"))
        print(name, len(fr), "frames", fr[0].shape[1], "x", fr[0].shape[0])


if __name__ == "__main__":
    sys.exit(main())
