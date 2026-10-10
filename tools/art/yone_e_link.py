#!/usr/bin/env python3
"""The spirit tether of Yone's Soul Unbound: a straight line from the body he leaves behind to him (the user,
2026-10-11: 「另外永恩的E帮我加个连接线特效」, then 「你这个线弄直啊」).

    python tools/art/yone_e_link.py      # writes assets/source/yone/yone_fx_e_link.png and league/effects/league_yone_link

The anchor's end_effects send a BackToCasterLinearProjectile (league_yone_e_link, tools/fix/yone_e_link.py) from the
body to him every 2 ticks at 15000 a tick. A projectile's picture is turned to its flight, and a homing link bends
after him when he walks: the first version (40 px links at 2000 a tick every 16 ticks) made a curved chain, stepped
where the links met. Trials on a mock of his walk (1.2 px a tick, turning) and his dash: links drawn from the body
to their heads fanned out (each tail swung off the body by his walk during its flight); slower or sparser links
(6000-12000 a tick, every 3-4 ticks) bent and showed their seams. At 15000 a tick every 2 ticks the links reach
him in a few ticks (about 8 at 120 px), so they lie on the line from the body to him; each one draws 40 px behind
its head (30 px apart: they overlap) and 15 px ahead, so the line ends within 15 px of his pivot, on his body, when
the leading link reaches him and is removed. A brighter bead on each head (5 rows) flows from the body to him.
Drawn pointing right, head on the pivot, exactly symmetric top to bottom (it is turned over when it flies left): a
near-white core in a violet sheath, his spirit's colours (yone_fx_spirit / e_return). The view is `repeat: false`,
one frame a tick while the link grows out of the body (15 px a tick, its flight), then the last frame held longer
than any flight. The spawn tick shows a single pixel (a projectile's view is not yet turned on the tick it appears).
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yone")
OUT = os.path.join(ROOT, "league", "effects", "league_yone_link")
Z = 8
STEP = 15                                # px a tick: the link's 15000
AHEAD = 15                               # px drawn ahead of the head: half the 30 px between links
BACK = 40                                # px drawn behind the head once grown
TICKS = -(-BACK // STEP)                 # frames grown; the last is held
H = 5                                    # rows; row 2 is the pivot's
TICK_MS = 1000 / 60


def rgb(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)


CORE, LIGHT, MID, DEEP = (rgb(c) for c in ("#F8F5FD", "#AC90FB", "#886CF3", "#6F45E1"))


def link(back):
    """The line from `back` px behind the pivot to AHEAD px in front, the bead on the pivot. Column c is pivot + c - back."""
    w = back + AHEAD + 1
    a = np.zeros((H, w, 4), np.uint8)
    for c in range(w):
        x = c - back                     # px from the pivot, + towards him
        if x > AHEAD - 3:                # the line's far end thins to its core
            a[2, c] = MID
            continue
        a[2, c] = CORE
        a[1, c] = a[3, c] = MID
    p = back                             # the bead: a small diamond on the pivot
    for dx, rows in ((-2, (2,)), (-1, (1, 2, 3)), (0, (0, 1, 2, 3, 4)), (1, (1, 2, 3)), (2, (2,))):
        if 0 <= p + dx < w:
            for r in rows:
                a[r, p + dx] = CORE if r == 2 or (dx == 0 and r in (1, 3)) else LIGHT
    a[0, p] = a[4, p] = DEEP
    return a


def main():
    tag = [(np.array([[CORE]], np.uint8), TICK_MS)]          # spawn tick: one pixel on the pivot
    for k in range(1, TICKS + 1):
        back = min(STEP * k, BACK)
        arr = link(back)
        tag.append((G.centre_frame(arr, -back, -(H // 2)), TICK_MS if k < TICKS else 10000))
    for arr, _ in tag:
        if not (arr == arr[::-1]).all():
            sys.exit("a link is not symmetric top to bottom")
    sample = link(48)
    Image.fromarray(np.repeat(np.repeat(sample, Z, 0), Z, 1), "RGBA").save(G.lp(os.path.join(SRC, "yone_fx_e_link.png")))
    w, h = G.write_sheet(OUT, {"e_link": tag})
    print(f"league/effects/league_yone_link#sheet.png {w}x{h}: e_link {len(tag)} frames, "
          f"the last {BACK} px back + {AHEAD} ahead")


if __name__ == "__main__":
    main()
