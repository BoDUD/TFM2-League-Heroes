"""Xin Zhao's hair ribbons flutter while he stands (the user, 2026-11-19: 「发带能动吗 动画效果」): in the ready stance the
two blue ribbon tails hang left of the head over clear background (x < 30, rows 11-26: nothing but ribbon there). Each
column of them moves up / down as a whole (outline included) by a wave that travels from the root to the tips: 0 at the
root (x >= 30), up to AMP px at the tips; the body, the hair and the spear never move.

    wave(c, phase, n=6, oy=0) -> picture     (phase 0..n-1; oy: the frame drawn 1 px higher = -1)
"""
import numpy as np

ROOT_X, TIP_X = 30, 18          # the ribbons leave the hair at x 30 and end at x 18 (ready stance, hd)
ROWS = (11, 26)                 # their rows
AMP = 2.0                       # px at the tips
WAVE = 12.0                     # px per wave along the ribbon


def dy_of(x, phase, n):
    if x >= ROOT_X:
        return 0
    s = (ROOT_X - x) / (ROOT_X - TIP_X)            # 0 at the root, 1 at the tips
    a = AMP * min(1.0, s) ** 1.2
    return int(round(a * np.sin(2 * np.pi * (phase / n) - 2 * np.pi * (ROOT_X - x) / WAVE)))


def wave(c, phase, n=6, oy=0):
    h, w = c.shape[:2]
    new = c.copy()
    y0, y1 = ROWS[0] + oy, ROWS[1] + oy
    new[y0:y1 + 1, :ROOT_X] = 0
    for x in range(ROOT_X):
        d = dy_of(x, phase, n)
        for y in range(y0, y1 + 1):
            if c[y, x, 3] == 0:
                continue
            q = y + d
            if 0 <= q < h:
                new[q, x] = c[y, x]
    return new
