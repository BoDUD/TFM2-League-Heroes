#!/usr/bin/env python3
"""Fizz's gulp: the ripples and bubbles left where his shark swallowed a small yordle's body.

    python tools/art/fx_fizz_gulp.py [--review out.png]

The user's easter egg, 2026-11-05 (「鲨鱼吃小矮子」): when Chum the Waters kills a small yordle the shark swallows the
body - no corpse is left on the ground (Teemo and Heimerdinger excepted). The swallow is native (the match add-on banishes
the body a moment after the bite, tools/kit/fizz_yordle.py); this is the banish's lock picture on the spot: the water
closing over the body - a ring of the shark's pool spreading on the ground, the body's last bubbles rising and popping -
then nothing (the last frame is empty, so a held last frame shows nothing either). Drawn on the game grid (1x pixels) in
the colours of the shark's pool (league_fizz_big's r_shark frames), left-right symmetric (the client never mirrors an
effect), centred on the body's pivot with the ground 11 rows under it. Written as league/effects/league_fizz_gulp.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

OUT = os.path.join(ROOT, "league", "effects", "league_fizz_gulp")
TAG = "gulp"


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# the shark's pool (league_fizz_big r_shark2's last frames, by count)
WATER, DEEP, LIGHT, FOAM, WHITE = map(hexc, ["#3CC0F0", "#1A84D0", "#8CE6FF", "#D8F8FF", "#FFFFFF"])

HALF = 15                      # columns each side of the pivot
TOP, BOTTOM = -22, 17          # pivot-relative rows drawn (y down)
GROUND = 11                    # a unit's soles under its pivot
W, H = 2 * HALF + 1, BOTTOM - TOP + 1
# the frames in ticks (60 a second); the last one empty
TICKS = [4, 4, 5, 5, 5, 6, 6]


class Frame:
    """A cell of W x H game pixels; x, y pivot-relative (x right, y down). Every pixel is mirrored left to right."""

    def __init__(self):
        self.a = np.zeros((H, W, 4), np.uint8)

    def put(self, x, y, c, mirror=True):
        for xx in ({x, -x} if mirror else {x}):
            u, r = xx + HALF, y - TOP
            if 0 <= u < W and 0 <= r < H:
                self.a[r, u] = (*c, 255)


def ellipse(rx, ry):
    """The pixels of an ellipse's rim round the pivot's foot (right half; `put` mirrors them), traced by angle so the
    steep ends stay closed."""
    pts = set()
    for k in range(361):
        a = np.pi * k / 360 - np.pi / 2
        pts.add((int(round(rx * np.cos(a))), GROUND + int(round(ry * np.sin(a)))))
    return sorted(pts)


def ring(f, rx, ry, outer, inner=None, gaps=0, seed=0, fill=None):
    """An ellipse on the ground round the pivot's foot: `outer` on its rim, `inner` one step in (the pool's two tones),
    `fill` inside; `gaps` short breaks in the rim (the same each side)."""
    rng = np.random.default_rng(seed)
    rim = ellipse(rx, ry)
    cut = set()
    if gaps:
        for c in rng.choice(len(rim), size=min(gaps, len(rim)), replace=False):
            cut |= {rim[c], rim[min(c + 1, len(rim) - 1)]}
    if fill is not None:
        for x in range(0, rx):
            for y in range(GROUND - ry + 1, GROUND + ry):
                if (x / (rx - 0.5)) ** 2 + ((y - GROUND) / (ry - 0.5)) ** 2 < 1:
                    f.put(x, y, fill)
    if inner is not None and rx > 2 and ry > 1:
        for x, y in ellipse(rx - 1, ry - 1):
            f.put(x, y, inner)
    for p in rim:
        if p not in cut:
            f.put(*p, outer)


def bubble(f, x, y, big=False):
    """A bubble: a light ring with a white glint top left (one each side of the axis unless x is 0)."""
    pts = [(-1, 0), (1, 0), (0, -1), (0, 1)] if not big else [(-2, -1), (-2, 0), (-2, 1), (2, -1), (2, 0), (2, 1),
                                                                  (-1, -2), (0, -2), (1, -2), (-1, 2), (0, 2), (1, 2)]
    for dx, dy in pts:
        f.put(x + dx, y + dy, LIGHT)
    f.put(x - 1, y - 1, WHITE)


def pop(f, x, y):
    """A popping bubble: four foam specks."""
    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 1)]:
        f.put(x + dx, y + dy, FOAM)


def drops(f, pts, c=FOAM):
    for x, y in pts:
        f.put(x, y, c)


def frames():
    out = []
    # 1 the water closes: a small dark pool with a light rim, a splash of foam up the middle
    f = Frame()
    ring(f, 8, 3, LIGHT, WATER, fill=DEEP)
    drops(f, [(0, GROUND - 4), (0, GROUND - 6), (2, GROUND - 5), (4, GROUND - 3)], WHITE)
    out.append(f)
    # 2 the ring spreads, the first bubbles come up
    f = Frame()
    ring(f, 11, 4, LIGHT, WATER, fill=WATER)
    bubble(f, 3, GROUND - 6)
    bubble(f, 0, GROUND - 3, big=True)
    drops(f, [(6, GROUND - 4), (9, GROUND - 2)])
    out.append(f)
    # 3 wider and lighter, the bubbles rising
    f = Frame()
    ring(f, 13, 4, FOAM, LIGHT, gaps=2, seed=3)
    bubble(f, 3, GROUND - 11)
    bubble(f, 0, GROUND - 8, big=True)
    bubble(f, 6, GROUND - 4)
    out.append(f)
    # 4 the ring breaking up, a bubble pops
    f = Frame()
    ring(f, 14, 5, LIGHT, None, gaps=4, seed=4)
    pop(f, 3, GROUND - 15)
    bubble(f, 0, GROUND - 13, big=True)
    bubble(f, 6, GROUND - 9)
    out.append(f)
    # 5 the last arcs, the big bubble pops
    f = Frame()
    ring(f, 15, 5, FOAM, None, gaps=7, seed=5)
    pop(f, 0, GROUND - 18)
    bubble(f, 6, GROUND - 14)
    out.append(f)
    # 6 the last bubble pops, a few specks on the water
    f = Frame()
    pop(f, 6, GROUND - 18)
    drops(f, [(11, GROUND), (14, GROUND + 1), (4, GROUND + 2)], LIGHT)
    out.append(f)
    # 7 nothing: the body is gone
    out.append(Frame())
    ms = [t * 1000.0 / 60 for t in TICKS]
    assert len(out) == len(ms)
    return [(f.a, m) for f, m in zip(out, ms)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the frames at 8x here")
    a = ap.parse_args()
    fr = frames()
    cells = []
    for k, (cell, ms) in enumerate(fr):
        assert (cell == cell[:, ::-1]).all(), f"frame {k + 1} is not symmetric"
        assert set(np.unique(cell[..., 3])) <= {0, 255}
        cells.append((G.centre_frame(cell, -HALF, TOP), ms))      # centred on the pivot, as the client draws it
    assert not cells[-1][0][..., 3].any(), "the last frame must be empty"
    w, h = G.write_sheet(OUT, {TAG: cells}, share=True)
    print(f"league/effects/league_fizz_gulp#sheet.png {w}x{h}: {TAG} {len(cells)}f "
          f"{sum(m for _, m in cells):.0f}ms ({sum(TICKS)} ticks)")
    if a.review:
        Z = 8
        img = Image.new("RGBA", ((W + 2) * Z * len(fr), H * Z), (90, 140, 90, 255))
        for k, (cell, _) in enumerate(fr):
            img.alpha_composite(Image.fromarray(cell).resize((W * Z, H * Z), Image.NEAREST), (k * (W + 2) * Z, 0))
            # the ground line
            for u in range(W * Z):
                if u % 4 < 2:
                    img.putpixel((k * (W + 2) * Z + u, (GROUND - TOP) * Z + Z // 2), (255, 255, 255, 120))
        img.convert("RGB").save(a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()
