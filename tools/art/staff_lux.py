#!/usr/bin/env python3
"""Lux's staff in twelve directions, 30 degrees apart, for the cast frames (casts_lux_hd.py).

    python tools/art/staff_lux.py --sheet PNG      # every direction at 8x

The design's staff (design_lux_hd: the crescent head to the lower left, 210 degrees) turns and mirrors onto squares
about its middle M (a half-square point): 30, 60, 120, 150, 210, 240, 300 and 330 degrees, the same squares. Level
and upright have no such turn, so the level staff (head to the left, 180) is the design's turned a twelfth (RotSprite:
Scale2x three times, turned, read back on its squares) for its two end pieces only, tidied square by square (TIDY),
with the shaft drawn level the design's way (design_lux_hd.shaft: the cream core, the gold spiral every PERIOD squares,
an outline each side) and as long; its turns and mirrors give 0, 90 and 270. Every direction is the same length.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_lux_hd as DL  # noqa: E402

HALF_LEN = DL.HALF * math.hypot(1, DL.K)       # squares from M to where each end piece starts, along the shaft
PAD = 24


def design():
    return np.asarray(Image.open(DL.lp(os.path.join(DL.HD, "design.png"))).convert("RGBA"))


def design_staff(d):
    """The design's staff alone (its shaft under the glove too) on the design's grid."""
    band, head, end = DL.staff_masks(d)
    glove = np.zeros(band.shape, bool)
    for x, y in DL.GLOVE:
        glove[y, x] = True
    st = np.zeros_like(d)
    m = (band | head | end) & (d[..., 3] > 0) & ~glove
    st[m] = d[m]
    for (x, y), c in DL.shaft(d.shape[:2]).items():
        if glove[y, x]:
            st[y, x, :3] = c
            st[y, x, 3] = 255
    return st


def shaft(M, u, half, shape):
    """{(x, y): rgb} the shaft drawn design_lux_hd's way along unit u through M, `half` squares each way."""
    u = np.asarray(u, float) / np.hypot(*u)
    n = np.array((-u[1], u[0]))
    out = {}
    for y in range(shape[0]):
        for x in range(shape[1]):
            v = np.array((x + 0.5 - M[0], y + 0.5 - M[1]))
            s, t = float(v @ u), float(v @ n)
            if abs(s) > half or abs(t) > DL.EDGE:
                continue
            side = 1 if s >= 0 else -1
            if abs(t) <= DL.CORE:
                w = math.cos(2 * math.pi * (abs(s) + 0.8 * t * side) / DL.PERIOD)
                out[(x, y)] = DL.GOLD if w > 0.5 else (DL.CREAM if t * side <= 0 else DL.SHADE)
            else:
                out[(x, y)] = DL.OUTLINE_SQ
    return out


# ------------------------------------------------------------------------------------------------ the level staff
# its end pieces tidied after the turn: (x, y) in the level staff's own grid (M at LEVEL_M) -> rgb, None = cleared
LEVEL_M = (DL.M[0] + PAD, DL.M[1] + PAD)
TIDY = {}


def scale2x(a):
    H, W = a.shape[:2]
    p = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    B, Dd, E, F, Hh = p[:-2, 1:-1], p[1:-1, :-2], p[1:-1, 1:-1], p[1:-1, 2:], p[2:, 1:-1]

    def eq(x, y):
        return (x == y).all(-1)

    c0 = eq(Dd, B) & ~eq(B, F) & ~eq(Dd, Hh)
    c1 = eq(B, F) & ~eq(B, Dd) & ~eq(F, Hh)
    c2 = eq(Dd, Hh) & ~eq(Dd, B) & ~eq(Hh, F)
    c3 = eq(Hh, F) & ~eq(Dd, Hh) & ~eq(B, F)
    out = np.zeros((H * 2, W * 2, a.shape[2]), a.dtype)
    out[0::2, 0::2] = np.where(c0[..., None], Dd, E)
    out[0::2, 1::2] = np.where(c1[..., None], F, E)
    out[1::2, 0::2] = np.where(c2[..., None], Dd, E)
    out[1::2, 1::2] = np.where(c3[..., None], F, E)
    return out


def rotsprite(img, deg, about):
    """img turned deg (counter-clockwise on screen) about `about`, on a grid PAD larger each side; the read-back
    phase with the fewest squares drawn."""
    big = img
    for _ in range(3):
        big = scale2x(big)
    S = 8
    H, W = img.shape[:2]
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    ax, ay = about
    yy, xx = np.mgrid[0:H + 2 * PAD, 0:W + 2 * PAD]
    best = None
    for oy in range(0, S, 2):
        for ox in range(0, S, 2):
            X = xx - PAD + (ox + 0.5) / S
            Y = yy - PAD + (oy + 0.5) / S
            dx, dy = X - ax, Y - ay
            sx = ax + c * dx - s * dy
            sy = ay + s * dx + c * dy
            bx, by = np.floor(sx * S).astype(int), np.floor(sy * S).astype(int)
            ok = (bx >= 0) & (bx < W * S) & (by >= 0) & (by < H * S)
            out = np.zeros((H + 2 * PAD, W + 2 * PAD, 4), np.uint8)
            out[ok] = big[by[ok], bx[ok]]
            n = int((out[..., 3] > 0).sum())
            if best is None or n < best[0]:
                best = (n, out)
    return best[1]


def level_staff(st):
    """The level staff, head to the left: (rgba on the design grid + PAD each side, M there)."""
    turned = rotsprite(st, -30, DL.M)
    mx, my = LEVEL_M
    out = np.zeros_like(turned)
    yy, xx = np.mgrid[0:out.shape[0], 0:out.shape[1]]
    ends = ((xx + 0.5) < mx - HALF_LEN + 0.5) | ((xx + 0.5) > mx + HALF_LEN - 0.5)
    for (x, y), c in shaft((mx, my), (1.0, 0.0), HALF_LEN, out.shape[:2]).items():
        out[y, x, :3] = c
        out[y, x, 3] = 255
    keep = ends & (turned[..., 3] > 0)
    out[keep] = turned[keep]
    for (x, y), c in TIDY.items():
        if c is None:
            out[y, x] = 0
        else:
            out[y, x, :3] = c
            out[y, x, 3] = 255
    return out


# ------------------------------------------------------------------------------------------------ the directions
# the dihedral turns about M: (dx, dy) -> (a dx + b dy, c dx + d dy); squares map onto squares about a half-square M
D4 = {"id": (1, 0, 0, 1), "rot180": (-1, 0, 0, -1), "mirror_x": (-1, 0, 0, 1), "mirror_y": (1, 0, 0, -1),
      "transpose": (0, 1, 1, 0), "anti": (0, -1, -1, 0), "rot_ccw": (0, 1, -1, 0), "rot_cw": (0, -1, 1, 0)}


def turn(img, M, mat):
    """img's squares moved by mat about M -> (img on a fresh grid, its M)."""
    a, b, c, d = mat
    ys, xs = np.nonzero(img[..., 3] > 0)
    dx, dy = xs + 0.5 - M[0], ys + 0.5 - M[1]
    nx, ny = a * dx + b * dy, c * dx + d * dy
    R = int(np.ceil(np.abs(np.concatenate([nx, ny])).max())) + 2
    out = np.zeros((2 * R, 2 * R, 4), np.uint8)
    X = np.floor(nx + R).astype(int)
    Y = np.floor(ny + R).astype(int)
    out[Y, X] = img[ys, xs]
    return out, (float(R), float(R))


def head_angle(mat, base):
    """The head's direction (degrees, counter-clockwise, y up) after mat, from the base staff's head (dx, dy)."""
    a, b, c, d = mat
    hx, hy = base
    return math.degrees(math.atan2(-(c * hx + d * hy), a * hx + b * hy)) % 360


class Staffs:
    """Lux's staff in every direction: at(deg) -> (rgba, M, head unit (dx, dy) on screen)."""

    def __init__(self, d=None):
        d = design() if d is None else d
        st = design_staff(d)
        lv = level_staff(st)
        self.bases = [(st, DL.M, (-1.0, -DL.K)), (lv, LEVEL_M, (-1.0, 0.0))]
        self.cache = {}

    def options(self):
        out = {}
        for bi, (img, M, h) in enumerate(self.bases):
            for name, mat in D4.items():
                ang = round(head_angle(mat, h)) % 360
                # the level staff: mirrors keep its lit top (mirror_x for 0, the turns for upright)
                out.setdefault(ang, (bi, name))
                if bi == 1 and ang == 0:
                    out[ang] = (bi, "mirror_x")
        return out

    def at(self, deg):
        deg = int(round(deg / 30.0) * 30) % 360
        if deg not in self.cache:
            bi, name = self.options()[deg]
            img, M, h = self.bases[bi]
            out, m2 = turn(img, M, D4[name])
            a, b, c, dd = D4[name]
            hu = np.array((a * h[0] + b * h[1], c * h[0] + dd * h[1]), float)
            self.cache[deg] = (out, m2, hu / np.hypot(*hu), name)
        return self.cache[deg][:3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    S = Staffs()
    tiles = []
    for deg in range(0, 360, 30):
        img, M, hu = S.at(deg)
        print(deg, S.cache[deg][3], img.shape, "head", np.round(hu, 2))
        im = Image.fromarray(img)
        bg = Image.new("RGBA", im.size, (150, 165, 150, 255))
        bg.alpha_composite(im)
        tiles.append(bg.convert("RGB").resize((im.width * 8, im.height * 8), Image.NEAREST))
    if a.sheet:
        w = max(t.width for t in tiles)
        h = max(t.height for t in tiles)
        c = Image.new("RGB", (6 * (w + 6), 2 * (h + 6)), (40, 40, 40))
        for i, t in enumerate(tiles):
            c.paste(t, ((i % 6) * (w + 6), (i // 6) * (h + 6)))
        c.save(a.sheet)


if __name__ == "__main__":
    main()
