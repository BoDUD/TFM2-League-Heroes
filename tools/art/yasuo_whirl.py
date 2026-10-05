#!/usr/bin/env python3
"""Yasuo's Q3 whirlwind drawn again from above (2026-10-05): a vortex that reads the same whichever way it flies.

    python tools/art/yasuo_whirl.py [--review <png>]     # writes assets/source/yasuo/yasuo_fx_tornado.png
    python tools/art/import_yasuo.py                     # then: the strip -> league/effects/league_yasuo_big

Codex's whirlwind was an upright funnel seen from the side (its foot in a cloud of dust). A projectile's picture is
turned to its flight (.claude/skills/tfm2-hero-mod/references/champion-data.md section 6), so flying left the funnel
stood on its head and flying up or down it lay on its side - on the red side, where Yasuo mostly casts leftward, every
Q3 went out upside down (the user chose the redraw: 「亚索 Q3 龙卷风重画」). Seen from above, as Janna's Howling Gale
is drawn, a whirlwind has no up and down: three spiral arms round a bright eye, turning a third of a turn over the six
frames (so the loop is seamless), a short wind trail behind it (drawn on the left: the picture is drawn flying right
and turned with the flight, so the trail is always behind) and specks of dust thrown off its rim.

Game size: the vortex 24 squares across (the projectile's radius 12000), in the colours of Codex's funnel (the steel,
mid and light blues, the pale whites and the dust's greys), no outline (an effect). Every square is one flat 8x8 block
in the strip, as tools/art/import_yasuo.py reads its native strips.
"""
import argparse
import math
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "assets", "source", "yasuo", "yasuo_fx_tornado.png")
Z = 8
FRAMES = 6
CELL = (36, 30)                  # w, h of each frame (game squares)
EYE = (20, 15)                   # the vortex's middle square in the cell (the importer's anchor)
R = 11.6                         # the vortex's radius (squares): 24 across, the projectile's 12000
ARMS = 3
TWIST = 0.5                      # radians an arm turns per square outward
PAL = {
    "D": (0x34, 0x72, 0xA3),     # steel
    "M": (0x50, 0x96, 0xC3),     # mid blue
    "L": (0x7E, 0xBC, 0xD8),     # light blue
    "P": (0xCC, 0xE4, 0xEC),     # pale
    "W": (0xF1, 0xF9, 0xFC),     # white
    "G": (0x91, 0x9C, 0x9A),     # dust
    "g": (0xC1, 0xD8, 0xDC),     # light dust
}
# the trail behind (left of) the vortex: (row from the eye, first column from the eye, length per frame, colour)
TRAIL = [(-5, -R - 1, (5, 6, 7, 6, 5, 4), "L"), (-1, -R - 2, (8, 7, 6, 7, 8, 9), "P"),
         (3, -R - 1, (6, 7, 8, 9, 8, 7), "W"), (6, -R + 1, (3, 4, 3, 2, 3, 4), "L")]
DUST = [(0.4, 1.8, "G"), (1.5, 2.6, "g"), (2.4, 1.6, "G"), (3.3, 2.4, "g"), (4.4, 2.0, "G"), (5.4, 2.8, "g")]


def frame(k):
    """{(x, y): letter} of frame k on the cell."""
    out = {}
    turn = 2 * math.pi / ARMS * k / FRAMES          # a third of a turn over the loop
    ex, ey = EYE
    for y in range(CELL[1]):
        for x in range(CELL[0]):
            dx, dy = x - ex, y - ey
            r = math.hypot(dx, dy)
            if r > R + 1.6:
                continue
            th = math.atan2(dy, dx)
            v = math.cos(ARMS * (th - turn) + TWIST * r)  # +1 on an arm's crest, -1 between the arms
            if r < 1.6:
                ch = "W"
            elif r < 2.8:
                ch = "P" if v > -0.5 else "L"
            elif r <= R - 1.2:
                ch = "W" if v > 0.6 else "P" if v > 0.15 else "L" if v > -0.3 else "M" if v > -0.7 else "D"
            elif r <= R + 0.4:                           # the rim: the arms' tips, the gaps between them open
                if v < -0.35:
                    continue
                ch = "P" if v > 0.5 else "L" if v > 0.0 else "M"
            else:                                        # the arms flung past the rim
                if v < 0.55:
                    continue
                ch = "L"
            out[(x, y)] = ch
    for row, col, lengths, ch in TRAIL:                  # the wind behind it
        y = ey + row
        x1 = int(round(ex + col))
        for x in range(x1 - lengths[k], x1 + 1):
            if 0 <= x < CELL[0] and 0 <= y < CELL[1] and (x, y) not in out:
                out[(x, y)] = ch if x > x1 - lengths[k] + 1 else "P"
    for a0, dr, ch in DUST:                              # specks thrown off the rim, turning with it
        a = a0 + turn * 1.5
        x = int(round(ex + (R + dr) * math.cos(a)))
        y = int(round(ey + (R + dr) * math.sin(a)))
        if 0 <= x < CELL[0] and 0 <= y < CELL[1] and (x, y) not in out:
            out[(x, y)] = ch
    return out


def strip():
    a = np.zeros((CELL[1], CELL[0] * FRAMES, 4), np.uint8)
    for k in range(FRAMES):
        for (x, y), ch in frame(k).items():
            a[y, k * CELL[0] + x] = PAL[ch] + (255,)
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review")
    args = ap.parse_args()
    a = strip()
    Image.fromarray(np.repeat(np.repeat(a, Z, 0), Z, 1), "RGBA").save(OUT)
    print("wrote", os.path.relpath(OUT, ROOT), f"{FRAMES} cells of {CELL[0]}x{CELL[1]}")
    if args.review:
        bg = np.zeros_like(a)
        bg[...] = (92, 104, 88, 255)
        m = a[..., 3] > 0
        bg[m] = a[m]
        Image.fromarray(np.repeat(np.repeat(bg, 10, 0), 10, 1)).save(args.review)


if __name__ == "__main__":
    main()
