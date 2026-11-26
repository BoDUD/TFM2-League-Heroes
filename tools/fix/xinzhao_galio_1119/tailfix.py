"""Galio's tail reaches his left leg in every run frame (the user, 2026-11-19: 「尾巴这里对吗 走路的时候」): the tail's
stone rises from under his left fist and ends in a black cap at x 86; in run[2]-[5] the striding leg covers that end,
but in run[0], [1], [7] the leg is ahead and 2-6 squares of clear show between them - the tail reads as cut off, every
other step. There the tail's end band (2 grey rows under its top outline row, the row with "Ggggga") goes on to the
leg's outline: the cap becomes grey, grey to the leg, outline rows above and below over the gap; run[6]'s one clear
square under it gets outline.

    join(c, k) -> picture
"""
import numpy as np

GREY = (124, 143, 145, 255)
BLACK = (3, 2, 1, 255)
TOP = {0: 104, 1: 103, 7: 101}          # the row of the tail's top outline ("Ggggga" at x 76-81) where a gap shows


def join(c, k):
    new = c.copy()
    if k == 6:
        if new[106, 86, 3] == 0:
            new[106, 86] = BLACK
        return new
    if k not in TOP:
        return new
    r0 = TOP[k]
    def leg_x(y):
        x = 87
        while x < 100 and c[y, x, 3] == 0:
            x += 1
        return x
    for dy, kind in ((0, "outline"), (1, "grey"), (2, "grey"), (3, "outline")):
        y = r0 + dy
        xl = leg_x(y)
        x_from = 87 if kind == "outline" else (86 if dy == 1 else 84)
        for x in range(x_from, xl):
            new[y, x] = BLACK if kind == "outline" else GREY
    return new
