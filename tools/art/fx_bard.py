#!/usr/bin/env python3
"""league_bard's effects drawn here in code (Codex was out of credit for step 3: the user, 2026-10-14: 「codex没额度了
你能直接做吗特效」), to the specs of assets/source/bard/PROMPTS_FX.md (tools/art/pack_bard_fx.py), as the game sheets
league_bard_fx and league_bard_big.

    python tools/art/fx_bard.py [--review out.png]

Every picture is pixel art at game size (1 square = 1 game px) on a Layer: intensity fields (balls, stars, bursts of
rays) stepped onto a ramp - white core, then the ramp's shades down to its darkest, nothing below a threshold - so
the light has hard edges and no outline; and lines plotted square by square at a chosen shade: the rings are
8-connected ellipses without L corners (a pixel artist's clean line), the bands two squares thick, light inside and
darker outside. Where two parts meet the brighter wins, except what is painted over everything (R's gold statue). The
ramps are the pack's: Bard's cosmic gold, the purple-blue starlight, the shrine's leaf green.
Symmetry (the client never mirrors an effect, and turns a flying picture with its flight): the flying pictures are
symmetric top to bottom, every other one left to right, square for square (asserted).
Placement (import_kassadin's conventions): spots are game px from the pivot (x forward, y down), a unit's soles 11
under it; a hit on the upper body at (0, -12), the ground under a unit at (0, 11). The flying pictures start with an
empty frame (a homing projectile's first move is its lift: the picture would point up for a tick, champion-data.md;
import_jhin.flight) and hold their last frame a second. Times from the kit (build_bard.P): the stun's band lasts the
stun (1.5 s), R's mark the orb's flight (0.4 s), the stasis 2.5 s.
Tags: one per view of build_bard.py; e_door_out is the door again, p_slow / q_slow the slow, w_haste / e_haste the haste.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

MOD = os.path.join(ROOT, "league")


def hexes(s):
    return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in s.split(", ")]


GOLD = hexes("#FFFFFF, #FFF6C8, #FFE27A, #F5C343, #D9962B, #A86A1E")
STAR = hexes("#FFFFFF, #F2E8FF, #C7B3FF, #8E7BEA, #5A4CC4, #2E2A7A")
LEAF = hexes("#F4FFE0, #C6F27A, #7FCF4A, #3E8F3A, #2F6B34")
STEPS = (0.86, 0.70, 0.52, 0.34, 0.20)      # intensity at or above -> ramp index 0..4, then the last
SHADE_I = (0.93, 0.78, 0.61, 0.43, 0.27, 0.15)  # the intensity standing for ramp index 0..5


# ------------------------------------------------------------------------------------------------ the layer
class Layer:
    """A picture built from intensity fields and plotted squares, each on its own ramp; the brighter wins a square."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.I = np.zeros((h, w))
        self.R = np.full((h, w), -1)
        self.ramps = []
        yy, xx = np.mgrid[0:h, 0:w]
        self.x = xx - (w - 1) / 2            # square centres from the picture's middle
        self.y = yy - (h - 1) / 2

    def _k(self, ramp):
        if ramp not in self.ramps:
            self.ramps.append(ramp)
        return self.ramps.index(ramp)

    def add(self, field, ramp, cut=0.12):
        """Lay an intensity field (0..1) down on a ramp where it beats what is there (cut: the weakest drawn)."""
        k = self._k(ramp)
        f = np.where(field >= cut, field, 0)
        win = f > self.I
        self.I = np.where(win, f, self.I)
        self.R = np.where(win, k, self.R)
        return self

    def plot(self, pts, ramp, shade, force=False):
        """Squares (x, y from the middle) at a ramp's shade (0 = its lightest), where brighter (or always: force)."""
        k = self._k(ramp)
        v = SHADE_I[min(shade, len(ramp) - 1, len(SHADE_I) - 1)]
        for x, y in pts:
            ix, iy = int(round(x + (self.w - 1) / 2)), int(round(y + (self.h - 1) / 2))
            if 0 <= ix < self.w and 0 <= iy < self.h and (force or v > self.I[iy, ix]):
                self.I[iy, ix] = v
                self.R[iy, ix] = k
        return self

    def paint(self, mask, ramp, shade):
        """Every square of a mask at a shade, over whatever is there."""
        k = self._k(ramp)
        v = SHADE_I[min(shade, len(ramp) - 1, len(SHADE_I) - 1)]
        self.I = np.where(mask, v, self.I)
        self.R = np.where(mask, k, self.R)
        return self

    def image(self):
        out = np.zeros((self.h, self.w, 4), np.uint8)
        for k, ramp in enumerate(self.ramps):
            m = (self.R == k) & (self.I > 0)
            idx = np.full(self.I.shape, len(ramp) - 1)
            for i, t in reversed(list(enumerate(STEPS))):
                idx = np.where(self.I >= t, min(i, len(ramp) - 1), idx)
            for i, col in enumerate(ramp):
                mm = m & (idx == i)
                out[mm, :3] = col
                out[mm, 3] = 255
        return out


# ------------------------------------------------------------------------------------------------ shapes
def ball(L, cx, cy, r, soft=1.0):
    d = np.hypot(L.x - cx, L.y - cy)
    return np.clip(1 - (d / max(r, 1e-6)) ** 2 * soft, 0, 1)


def star4(L, cx, cy, r, w=0.9):
    """A four-pointed star: bright arms along the axes, tapering, and a core."""
    dx, dy = np.abs(L.x - cx), np.abs(L.y - cy)
    arm_h = np.clip(1 - dx / (r + 0.5), 0, 1) * np.clip(1 - dy / (w * (1 - dx / (r + 1)) + 0.35), 0, 1)
    arm_v = np.clip(1 - dy / (r + 0.5), 0, 1) * np.clip(1 - dx / (w * (1 - dy / (r + 1)) + 0.35), 0, 1)
    core = ball(L, cx, cy, max(1.2, r * 0.35))
    return np.maximum(np.maximum(arm_h, arm_v), core)


def rays(L, cx, cy, spec):
    """Rays from (cx, cy), each (angle in degrees: 0 = right, 90 = down; length; half width at the root), brightest
    at the root and thinning to the tip."""
    f = np.zeros_like(L.I)
    X, Y = L.x - cx, L.y - cy
    for a, ln, w in spec:
        r = math.radians(a)
        u = X * math.cos(r) + Y * math.sin(r)
        v = -X * math.sin(r) + Y * math.cos(r)
        t = np.clip(u / (ln + 0.5), 0, 1)
        g = (1 - t) * np.clip(1 - np.abs(v) / (w * (1 - t) + 0.5), 0, 1)
        f = np.maximum(f, np.where(u >= -0.5, g, 0))
    return f


def burst(L, cx, cy, axial, diagonal, w=0.8, turn=0):
    return rays(L, cx, cy, [(turn + a, axial if a % 90 == 0 else diagonal, w) for a in range(0, 360, 45)])


def ring(L, cx, cy, rx, ry, th, arc=None):
    """An elliptic ring `th` squares thick all round (the distance to the ellipse taken as (e - 1) / |grad e|, so a
    flat ellipse keeps its thickness at its ends); arc (a0, a1) in degrees keeps a part (0 = right, 90 = down)."""
    X, Y = L.x - cx, L.y - cy
    rx, ry = max(rx, 1e-6), max(ry, 1e-6)
    e = np.hypot(X / rx, Y / ry)
    grad = np.hypot(X / rx ** 2, Y / ry ** 2) / np.maximum(e, 1e-6)
    dist = np.abs(e - 1) / np.maximum(grad, 1e-6)
    f = np.clip(1 - dist / max(th / 2, 0.5), 0, 1)
    if arc is not None:
        f = np.where(in_arc(np.degrees(np.arctan2(Y, X)), arc), f, 0)
    return f


def in_arc(ang, arc):
    a0, a1 = arc
    return ((ang - a0) % 360) <= ((a1 - a0) % 360)


def disc(L, cx, cy, rx, ry):
    e = np.hypot((L.x - cx) / max(rx, 1e-6), (L.y - cy) / max(ry, 1e-6))
    return e <= 1


def ellipse_pts(rx, ry, cx=0, cy=0, arc=None):
    """An ellipse line one square thick round (cx, cy): the quarter x, y >= 0 sampled and rounded, the middle square
    of every L corner dropped (8-connected, no doubled steps), mirrored into the other three quarters; arc keeps the
    squares whose angle (0 = right, 90 = down) is in it."""
    if rx < 0.5:
        q = [(0, y) for y in range(int(round(ry)) + 1)]
    elif ry < 0.5:
        q = [(x, 0) for x in range(int(round(rx)) + 1)]
    else:
        n = int(8 * (rx + ry)) + 8
        pts = []
        for i in range(n + 1):
            t = (math.pi / 2) * i / n
            p = (int(math.floor(rx * math.cos(t) + 0.5)), int(math.floor(ry * math.sin(t) + 0.5)))
            if not pts or p != pts[-1]:
                pts.append(p)
        q = []
        for p in pts:
            if len(q) >= 2 and abs(q[-2][0] - p[0]) == 1 and abs(q[-2][1] - p[1]) == 1:
                q.pop()
            q.append(p)
    out = set()
    for x, y in q:
        for sx in (1, -1):
            for sy in (1, -1):
                out.add((sx * x, sy * y))
    pts = sorted(out)
    if arc is not None:
        pts = [(x, y) for x, y in pts if in_arc(math.degrees(math.atan2(y, x)), arc)]
    return [(x + cx, y + cy) for x, y in pts]


def band(L, cx, cy, rx, ry, ramp, inner, outer, arc=None, cut=1.0):
    """An elliptic band about two squares thick on the ellipse (rx + 0.5, ry + 0.5): the squares inside its middle
    line at shade `inner`, those outside at `outer` (a lit rim with its shadow)."""
    X, Y = L.x - cx, L.y - cy
    ax, ay = rx + 0.5, ry + 0.5
    e = np.hypot(X / ax, Y / ay)
    grad = np.hypot(X / ax ** 2, Y / ay ** 2) / np.maximum(e, 1e-6)
    d = (e - 1) / np.maximum(grad, 1e-6)
    m = np.abs(d) <= cut
    if arc is not None:
        m &= in_arc(np.degrees(np.arctan2(Y, X)), arc)
    ys, xs = np.nonzero(m & (d < 0))
    L.plot([(L.x[y, x], L.y[y, x]) for y, x in zip(ys, xs)], ramp, inner)
    ys, xs = np.nonzero(m & (d >= 0))
    L.plot([(L.x[y, x], L.y[y, x]) for y, x in zip(ys, xs)], ramp, outer)
    return L


def twinkle(L, x, y, size, ramp, shade=0):
    """A sparkle: size 1 one square; 2 a plus, its arms a shade darker; 3 a plus with arms of two, the outer squares
    two shades darker."""
    L.plot([(x, y)], ramp, shade)
    if size >= 2:
        L.plot([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)], ramp, shade + 1)
    if size >= 3:
        L.plot([(x + 2, y), (x - 2, y), (x, y + 2), (x, y - 2)], ramp, shade + 2)
    return L


def lr(points):
    """(x, y) pairs plus their mirrors about the vertical axis."""
    out = []
    for x, y in points:
        out.append((x, y))
        if x != 0:
            out.append((-x, y))
    return out


def tb(points):
    out = []
    for x, y in points:
        out.append((x, y))
        if y != 0:
            out.append((x, -y))
    return out


def sym_lr(a):
    """The left half mirrored onto the right (the shapes are symmetric already; this only settles ties)."""
    w = a.shape[1]
    out = a.copy()
    out[:, w - w // 2:] = a[:, :w // 2][:, ::-1]
    return out


def sym_tb(a):
    h = a.shape[0]
    out = a.copy()
    out[h - h // 2:] = a[:h // 2][::-1]
    return out


# ------------------------------------------------------------------------------------------------ the pictures
def a_bolt():
    """His attack: a golden star flying right - a white-hot core, a long level glint, starlight sparks behind."""
    fr = []
    for k in range(4):
        L = Layer(15, 7)
        L.add(ball(L, 4, 0, 2.3), GOLD)
        L.add(rays(L, 4, 0, [(0, 3, 0.5), (180, 8 if k % 2 == 0 else 7, 0.6)]) * 0.92, GOLD)
        L.add(rays(L, 4, 0, [(90, 2 if k % 2 else 1, 0.3), (270, 2 if k % 2 else 1, 0.3)]) * 0.85, GOLD)
        for j, (x, y) in enumerate([(-1, 2), (-4, 1), (-6, 2)]):
            if (j + k) % 3 != 2:
                L.plot(tb([(x, y)]), STAR, 1 if (j + k) % 3 == 0 else 3)
        fr.append(sym_tb(L.image()))
    return fr


def a_hit():
    """The attack's hit on the upper body: a glint, an eight-rayed burst, its sparks flying apart."""
    fr = []
    for k in range(4):
        L = Layer(17, 17)
        if k == 0:
            L.add(star4(L, 0, 0, 2.2, 0.6), GOLD)
        elif k == 1:
            L.add(burst(L, 0, 0, 7, 4, 0.7), GOLD)
            L.add(ball(L, 0, 0, 2.6), GOLD)
        elif k == 2:
            L.add(ball(L, 0, 0, 1.8) * 0.7, GOLD)
            for x, y in lr([(5, -5), (5, 5)]):
                twinkle(L, x, y, 2, GOLD, 0)
            for x, y in lr([(0, -7), (7, 0), (0, 7)]):
                L.plot([(x, y)], STAR, 1)
        else:
            for x, y in lr([(6, -6), (6, 6)]):
                L.plot([(x, y)], GOLD, 3)
            for x, y in lr([(8, 0), (0, -8)]):
                L.plot([(x, y)], STAR, 3)
        fr.append(sym_lr(L.image()))
    return fr


def p_meep():
    """A Meep: a round golden spirit flying right, one big eye at its front, little fins flapping top and bottom, a
    starlight tail."""
    fr = []
    for k in range(4):
        L = Layer(15, 11)
        cx = 2
        L.add(ball(L, cx, 0, 3.8), GOLD)
        L.paint(disc(L, cx, 0, 3.6, 3.6) & ~disc(L, cx, 0, 2.6, 2.6) & (L.I < SHADE_I[3]), GOLD, 3)
        flap = (1, 2, 1, 0)[k]
        for y in range(4, 4 + flap):
            L.plot(tb([(cx - 1, y)]), GOLD, 2 + (y - 4))
        L.plot(tb([(cx - 2, 4)]), GOLD, 3)
        for j, x in enumerate((-3, -5, -7)):
            yy = ((k + j) % 3) - 1
            L.plot(tb([(x, yy)]), STAR, (1, 2, 3)[j])
        img = L.image()
        c0, r0 = (15 - 1) // 2 + cx, (11 - 1) // 2
        img[r0, c0 + 2, :3] = (46, 42, 122)               # the eye: a dark-blue pupil, a white glint before it
        img[r0, c0 + 1, :3] = (90, 76, 196)
        img[r0, c0 + 3, :3] = (255, 255, 255)
        img[r0, [c0 + 1, c0 + 2, c0 + 3], 3] = 255
        fr.append(sym_tb(img))
    return fr


def p_hit():
    """A Meep's splash: a flash, a golden pop, a starlight shock ring opening, its sparks fading."""
    fr = []
    for k in range(5):
        L = Layer(23, 17)
        if k == 0:
            L.add(star4(L, 0, 0, 2.6, 0.7), GOLD)
        elif k == 1:
            L.add(ball(L, 0, 0, 4.6), GOLD)
            L.add(burst(L, 0, 0, 7, 0, 0.6), GOLD)
        elif k == 2:
            band(L, 0, 0, 7, 5, STAR, 1, 3)
            L.add(ball(L, 0, 0, 3.0) * 0.9, GOLD)
            for x, y in lr([(6, -5)]):
                twinkle(L, x, y, 2, STAR, 0)
        elif k == 3:
            L.plot(ellipse_pts(9, 6), STAR, 3)
            L.plot(ellipse_pts(9, 6, arc=(20, 160)), STAR, 2)
            L.add(ball(L, 0, 0, 1.6) * 0.8, GOLD)
            for x, y in lr([(8, -6), (10, 2)]):
                twinkle(L, x, y, 2, STAR, 1)
        else:
            for x, y in lr([(10, -6), (6, 7), (11, 1)]):
                L.plot([(x, y)], STAR, 3)
        fr.append(sym_lr(L.image()))
    return fr


def q_bolt():
    """Cosmic Binding: a big golden orb with a cross glint, a tapering starlight tail with stars in it."""
    fr = []
    for k in range(4):
        L = Layer(21, 11)
        L.add(ball(L, 5, 0, 3.8), GOLD)
        L.add(rays(L, 5, 0, [(0, 4, 0.5), (90, 4 if k % 2 == 0 else 3, 0.5), (270, 4 if k % 2 == 0 else 3, 0.5)]),
              GOLD)
        t = np.clip(1 - np.abs(L.y) / np.maximum(0.4, 3.0 * (L.x + 10) / 14), 0, 1) * ((L.x > -10) & (L.x < 5))
        L.add(t * (0.30 + 0.45 * np.clip((L.x + 10) / 14, 0, 1)), STAR, cut=0.2)
        for j, (x, y) in enumerate([(0, 1), (-3, 2), (-6, 1), (-8, 0)]):
            if (j + k) % 2 == 0:
                L.plot(tb([(x, y)]), STAR, 0)
        fr.append(sym_tb(L.image()))
    return fr


def q_hit():
    """The binding's hit: a glint, a burst of eight rays, a starlight ring with stars on it, the ring breaking up."""
    fr = []
    for k in range(5):
        L = Layer(23, 23)
        if k == 0:
            L.add(star4(L, 0, 0, 3.0, 0.8), GOLD)
        elif k == 1:
            L.add(burst(L, 0, 0, 10, 6, 0.9), GOLD)
            L.add(ball(L, 0, 0, 3.8), GOLD)
        elif k == 2:
            band(L, 0, 0, 7, 7, STAR, 1, 3)
            L.add(ball(L, 0, 0, 3.0) * 0.95, GOLD)
            for x, y in lr([(0, -8), (6, -6), (6, 6), (0, 8)]):
                twinkle(L, x, y, 2, STAR, 0)
        elif k == 3:
            for a0 in range(0, 360, 45):
                L.plot(ellipse_pts(9, 9, arc=(a0 + 8, a0 + 30)), STAR, 2)
            for x, y in lr([(0, -10), (7, -7), (10, 0), (7, 7), (0, 10)]):
                twinkle(L, x, y, 2, STAR, 1)
        else:
            for x, y in lr([(3, -10), (10, -3), (8, 7), (2, 10)]):
                L.plot([(x, y)], STAR, 3)
        fr.append(sym_lr(L.image()))
    return fr


def q_bind():
    """The stun: a golden band round the unit's waist, its front lit, its back dim behind him; two pairs of stars
    riding round it; it flashes on and fades out."""
    fr = []
    RX, RY = 12, 4
    for k in range(6):
        L = Layer(29, 13)
        front_in, front_out, back = (0, 2, 3) if k == 0 else ((2, 4, 5) if k == 5 else (1, 3, 4))
        L.plot(ellipse_pts(RX, RY, arc=(180, 360)), GOLD, back)
        band(L, 0, 0, RX - 0.5, RY - 0.5, GOLD, front_in, front_out, arc=(0, 180))
        if k == 0:
            for x, y in lr([(13, 0)]):
                twinkle(L, x, y, 3, GOLD, 0)
        if k < 5:
            for phase in (25, 115):
                p = math.radians(phase + 30 * k)
                x, y = RX * math.sin(p), RY * math.cos(p)
                if y > 0:
                    for xx, yy in lr([(round(x), round(y))]):
                        twinkle(L, xx, yy, 2, STAR, 0)
                else:
                    L.plot(lr([(round(x), round(y))]), STAR, 2)
        fr.append(sym_lr(L.image()))
    return fr


def w_shrine():
    """The thrown shrine: a white-gold core in a wreath of turning leaves, flying right."""
    fr = []
    for k in range(4):
        L = Layer(15, 13)
        L.add(ball(L, 1, 0, 2.8), GOLD)
        for a in (20 + 20 * k, 80 + 20 * k, 140 + 20 * k):
            for s in (1, -1):
                r1, r2 = math.radians(s * a), math.radians(s * (a + 22))
                L.plot([(1 + 4.6 * math.cos(r1), 4.6 * math.sin(r1))], LEAF, 1)
                L.plot([(1 + 4.6 * math.cos(r2), 4.6 * math.sin(r2))], LEAF, 3)
        L.plot(tb([(-5, 1)]), GOLD, 2 + k % 2)
        fr.append(sym_tb(L.image()))
    return fr


def w_land():
    """The shrine at an ally's feet: a lit ground ring and grass, the shrine's orb bursting, healing light (leaves and
    plus signs) rising round him."""
    fr = []
    W, H = 27, 35
    gy = (H - 1) / 2 - 3                      # the ground row (from the middle)
    for k in range(6):
        L = Layer(W, H)
        if k <= 2:
            band(L, 0, gy, 6 + 2 * k, 2 + 0.5 * k, GOLD, 1 + k, 3 + min(k, 2))
        if k <= 3:
            for x, h in ((5, 2), (7, 1)) if k == 0 else ((8 + k, 2), (10 + k, 1), (6 + k, 3)):
                L.plot(lr([(x, gy - j) for j in range(h)]), LEAF, 1 if h == 3 else 2)
        if k == 0:
            L.add(ball(L, 0, gy - 2, 2.2), GOLD)
        if k == 1:
            L.add(ball(L, 0, gy - 3, 3.6), GOLD)
            L.add(rays(L, 0, gy - 3, [(270, 9, 0.7), (0, 5, 0.4), (180, 5, 0.4)]), GOLD)
        if 2 <= k <= 5:
            up = (k - 2) * 6
            for j, (x, dy) in enumerate([(7, 4), (10, 9), (5, 13), (9, 17)]):
                y = gy - dy - up
                if y < -(H - 1) / 2 + 2:
                    continue
                if j % 2 == 0:
                    for xx, yy in lr([(x, y)]):
                        twinkle(L, xx, yy, 2, LEAF, 0 if k < 5 else 2)
                else:
                    L.plot(lr([(x, y), (x + 1, y - 1)]), LEAF, 1 if k < 5 else 3)
            for x, dy in ((3, 6), (11, 13)):
                y = gy - dy - up
                if y > -(H - 1) / 2 + 1:
                    L.plot(lr([(x, y)]), GOLD, 1 if k < 5 else 3)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, H - 1 - 3          # anchor: the ground row


def e_door():
    """Magical Journey's door: an upright gold oval opening on a starry tunnel (rings going deep), stars twinkling
    in it; it opens, holds, closes. Behind him (z -1), its foot on the ground."""
    fr = []
    RX, RY = 14, 20
    W, H = 2 * RX + 5, 2 * RY + 5
    for k in range(6):
        L = Layer(W, H)
        rx = {0: 0, 1: 6, 2: RX, 3: RX, 4: 6, 5: 0}[k]
        if rx == 0:
            L.plot([(0, y) for y in range(-RY, RY + 1)], GOLD, 0 if k == 0 else 2)
            L.plot([(0, -RY - 1), (0, RY + 1)], GOLD, 2)
            for x, y in lr([(1, -6), (1, 6)]):
                L.plot([(x, y)], GOLD, 2)
        else:
            inside = disc(L, 0, 0, rx - 0.5, RY - 0.5)
            L.paint(inside, STAR, 4)
            L.paint(disc(L, 0, 2, rx * 0.5, RY * 0.5), STAR, 5)
            for s, sh in ((0.78, 3), (0.55, 4)):
                L.plot(ellipse_pts(rx * s, RY * s, 0, 2 * (1 - s)), STAR, sh, force=True)
            if rx == RX:
                stars = [(4, -10), (8, -2), (3, 7), (6, 12), (2, -15)]
                for j, (x, y) in enumerate(stars):
                    on = (j + k) % 2 == 0
                    for xx, yy in lr([(x, y)]):
                        if on:
                            twinkle(L, xx, yy, 2, STAR, 0)
                        else:
                            L.plot([(xx, yy)], STAR, 1, force=True)
            band(L, 0, 0, rx, RY, GOLD, 1, 3)
            L.plot(ellipse_pts(rx + 1, RY + 1, arc=(230, 310)), GOLD, 0)
            for x, y in lr([(0, -RY - 1)]):
                twinkle(L, x, y, 3 if rx == RX else 2, GOLD, 0)
            if rx == RX:
                for x, y in lr([(RX + 1, 0)]):
                    twinkle(L, x, y, 2, GOLD, 0)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, (H - 1) / 2 + RY + 1         # anchor: the oval's foot on the ground


def e_ride():
    """An ally taken along: a gold ring at his feet, sparks streaming up at his sides."""
    fr = []
    W, H = 23, 29
    gy = (H - 1) / 2 - 2
    for k in range(4):
        L = Layer(W, H)
        if k < 2:
            L.plot(ellipse_pts(7 + 2 * k, 2 + k, 0, gy), GOLD, 1 + 2 * k)
        for j, (x, y) in enumerate([(8, 0), (10, -6), (7, -11), (9, -16)]):
            yy = gy + y - 4 * k
            if yy < -(H - 1) / 2 + 1 or (k == 3 and j % 2):
                continue
            if j % 2 == 0:
                for xx, y2 in lr([(x, yy)]):
                    twinkle(L, xx, y2, 2, GOLD, 0 if k < 3 else 2)
            else:
                L.plot(lr([(x, yy), (x, yy + 1), (x, yy + 2)]), GOLD, 1 if k < 3 else 3)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, H - 1 - 2


def r_orb():
    """Tempered Fate's orb: a big golden ball with a white heart, a ring of gold round it whose nodes take turns."""
    fr = []
    for k in range(4):
        L = Layer(17, 17)
        L.add(ball(L, 0, 0, 5.0), GOLD)
        L.plot(ellipse_pts(7, 7), GOLD, 3)
        axes = [(0, -7), (7, 0), (0, 7), (-7, 0)]
        diag = [(5, -5), (5, 5), (-5, 5), (-5, -5)]
        for x, y in (axes if k % 2 == 0 else diag):
            twinkle(L, x, y, 2, GOLD, 0)
        fr.append(sym_tb(sym_lr(L.image())))
    return fr


def r_mark():
    """Where the orb will land, for its flight: a gold ellipse on the ground with four gems, a second one closing in
    and brightening."""
    fr = []
    RX, RY = 26, 9
    W, H = 2 * RX + 5, 2 * RY + 5
    for k in range(6):
        L = Layer(W, H)
        L.plot(ellipse_pts(RX, RY), GOLD, 3 if k < 3 else 2)
        g = 1 - k / 6
        L.plot(ellipse_pts(max(1, round(RX * g)), max(1, round(RY * g))), GOLD, 2 if k < 5 else 1)
        for x, y in lr([(RX, 0)]) + [(0, -RY), (0, RY)]:
            twinkle(L, x, y, 2, GOLD, 0 if k >= 3 else 1)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, (H - 1) / 2          # anchor: the ellipse's middle on the ground


def r_dome():
    """The orb lands: a white-gold blast, a gold ring running out over the ground with flares rising from it, the
    dome of stopped time standing over the zone, fading as the statues take over."""
    fr = []
    RX, RY, DY = 26, 9, 22                       # the zone's ground ellipse (r_r 26000) and the dome's height
    W, H = 2 * RX + 5, DY + RY + 18
    base = (H - 1) / 2 - RY - 3                  # the ground's middle row (from the picture's middle)
    for k in range(5):
        L = Layer(W, H)
        if k == 0:
            L.add(ball(L, 0, base, 5.5), GOLD)
            L.add(rays(L, 0, base, [(270, 14, 1.0), (0, 9, 0.6), (180, 9, 0.6)]), GOLD)
            L.plot(ellipse_pts(9, 3, 0, base), GOLD, 1)
        else:
            rx, ry, dy = (16, 6, 13) if k == 1 else (RX, RY, DY)
            lit = {1: (0, 2), 2: (0, 2), 3: (1, 3), 4: (3, 4)}[k]
            band(L, 0, base, rx - 0.5, ry - 0.5, GOLD, *lit)
            top = [(x, y) for x, y in ellipse_pts(rx, dy, 0, base) if y <= base]
            L.plot(top, GOLD, lit[0] + 1)
            if k in (2, 3):
                L.plot([(x, y) for x, y in ellipse_pts(rx - 1, dy - 1, 0, base) if y <= base - 1], GOLD, lit[1])
                L.plot([(x, y) for x, y in ellipse_pts(rx, dy, 0, base, arc=(235, 305))], GOLD, 0)
            if k <= 2:
                n = 6 if k == 1 else 8
                for j in range(n):
                    a = math.radians(180 / (n - 1) * j) if n > 1 else 0
                    x = round(rx * math.cos(a))
                    y = base + round(ry * math.sin(a))
                    ln = (6, 9)[k - 1] - (j % 2) * 3
                    L.add(rays(L, x, y, [(270, ln, 0.5)]) * 0.95, GOLD)
                    L.add(rays(L, -x, y, [(270, ln, 0.5)]) * 0.95, GOLD)
            if k == 1:
                L.add(ball(L, 0, base, 3.5) * 0.9, GOLD)
            if k == 3:
                for x, y in lr([(9, base - 18), (19, base - 13), (24, base - 5)]):
                    twinkle(L, x, y, 2, STAR, 0)
            if k == 4:
                for x, y in lr([(13, base - 21), (22, base - 10)]):
                    L.plot([(x, y)], STAR, 2)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, (H - 1) / 2 + base


def statue(L, fy, shade_body=3):
    """A unit turned to gold (a banished unit is not drawn: this stands in for it): a chibi's big head, body, arms
    and legs, lit from above, a dark-gold edge; feet on row fy."""
    X, Y = L.x, L.y - fy
    head = np.hypot(X / 6.5, (Y + 22) / 6.2) <= 1
    body = (Y >= -16) & (Y <= -8) & (np.abs(X) <= 4 + (Y + 16) / 8)
    arms = (np.abs(X) >= 6) & (np.abs(X) <= 7) & (Y >= -15) & (Y <= -9)
    legs = (np.abs(X) >= 1.5) & (np.abs(X) <= 4) & (Y >= -7) & (Y <= -1)
    feet = (np.abs(X) >= 1.5) & (np.abs(X) <= 5) & (Y >= -1) & (Y <= 0)
    m = head | body | arms | legs | feet
    edge = np.zeros_like(m)
    edge[1:] |= m[:-1]
    edge[:-1] |= m[1:]
    edge[:, 1:] |= m[:, :-1]
    edge[:, :-1] |= m[:, 1:]
    edge &= ~m
    L.paint(edge, GOLD, 5)
    L.paint(m, GOLD, shade_body)
    L.paint(head & (np.hypot(X / 5.0, (Y + 24) / 3.6) <= 1), GOLD, shade_body - 1)
    L.paint(head & (np.hypot(X / 1.6, (Y + 26) / 1.2) <= 1), GOLD, max(0, shade_body - 3))
    L.paint(body & (np.abs(X) <= 1.5) & (Y <= -12), GOLD, shade_body - 1)
    L.paint(m & (Y >= -21) & (Y <= -17) & (np.abs(X) <= 4.5) & ~(np.abs(X) <= 1.5), GOLD, shade_body + 1)
    return m


def r_lock():
    """A unit in the stasis (2.5 s): the gold statue standing in for it, in a thin gold bubble whose light runs round
    its rim, a few stars of stopped time in it."""
    fr = []
    RX, RY = 13, 18
    W, H = 2 * RX + 3, 2 * RY + 3
    fy = RY - 3                                   # the statue's soles (from the middle), 3 above the bubble's bottom
    for k in range(6):
        L = Layer(W, H)
        L.plot(ellipse_pts(RX, RY), GOLD, 0 if k == 0 else 3)
        if k == 0:
            L.plot(ellipse_pts(RX - 1, RY - 1), GOLD, 2)
        else:
            a = 250 - 28 * (k - 1)               # the light running down both sides of the rim
            L.plot(ellipse_pts(RX, RY, arc=(a - 18, a + 18)), GOLD, 1)
            L.plot(ellipse_pts(RX, RY, arc=(180 - a - 18 + 360, 180 - a + 18 + 360)), GOLD, 1)
            L.plot(ellipse_pts(RX - 1, RY - 1, arc=(240, 300)), GOLD, 2)
        statue(L, fy)
        for j, (x, y) in enumerate([(10, -10), (9, 4), (11, -2)]):
            if (j + k) % 3 == 0:
                for xx, yy in lr([(x, y)]):
                    twinkle(L, xx, yy, 2, STAR, 0)
            elif (j + k) % 3 == 1:
                L.plot(lr([(x, y)]), STAR, 2)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, (H - 1) / 2 + fy


def r_free():
    """The stasis ends: the bubble flashes and cracks, bursts into gold shards that fly off, and sparks."""
    fr = []
    RX, RY = 13, 18
    W, H = 2 * RX + 11, 2 * RY + 11
    for k in range(4):
        L = Layer(W, H)
        if k == 0:
            band(L, 0, 0, RX - 0.5, RY - 0.5, GOLD, 0, 2)
            for x0, y0, x1, y1 in ((5, -RY + 1, 7, -11), (7, -11, 6, -8), (RX, -3, 9, -1), (9, -1, 10, 2),
                                   (5, RY - 1, 6, 12)):
                for t in np.linspace(0, 1, 12):
                    L.plot(lr([(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)]), GOLD, 0)
        else:
            if k == 1:
                L.add(ball(L, 0, 0, 7.5) * 0.85, GOLD)
            d = {1: 1.0, 2: 1.25, 3: 1.45}[k]
            for j, a in enumerate((-80, -50, -20, 10, 40, 70, 100)):
                r = math.radians(a)
                x, y = RX * d * math.cos(r), RY * d * math.sin(r)
                tx, ty = -math.sin(r), math.cos(r)
                pts = [(x - tx, y - ty), (x, y)] + ([(x + tx, y + ty)] if j % 2 == 0 and k < 3 else [])
                L.plot(lr([(round(px), round(py)) for px, py in pts]), GOLD, 1 if k < 3 else 3)
            if k >= 2:
                for x, y in lr([(5, -RY * d * 0.8), (RX * d * 0.9, 9), (4, RY * d * 0.85)]):
                    twinkle(L, round(x), round(y), 2 if k == 2 else 1, STAR, 1 if k == 2 else 2)
        fr.append(sym_lr(L.image()))
    return fr, (W - 1) / 2, (H - 1) / 2 + RY - 3


def slow():
    """Slowed: a dim starlight ring at the feet, its front lit, two stars dragging round it."""
    fr = []
    for k in range(4):
        L = Layer(23, 9)
        L.plot(ellipse_pts(10, 3), STAR, 3)
        L.plot(ellipse_pts(10, 3, arc=(20, 160)), STAR, 2)
        p = math.radians(40 + 25 * k)
        for x, y in lr([(round(10 * math.sin(p)), round(3 * math.cos(p)))]):
            twinkle(L, x, y, 2, STAR, 0)
        fr.append(sym_lr(L.image()))
    return fr


def haste():
    """Hasted: gold and green speed lines streaming at his legs' sides, taking turns."""
    fr = []
    for k in range(4):
        L = Layer(23, 11)
        for j, (x, y, ln) in enumerate([(7, -3, 3), (9, 0, 4), (7, 3, 3)]):
            on = (j + k) % 3
            pts = [(x + i, y) for i in range(ln)]
            L.plot(lr(pts[:1]), GOLD if j != 1 else LEAF, 0 if on == 0 else 2)
            L.plot(lr(pts[1:]), GOLD if j != 1 else LEAF, 1 if on == 0 else 3)
        for x, y in lr([(6, 4 if k % 2 else -4)]):
            L.plot([(x, y)], LEAF, 1)
        fr.append(sym_lr(L.image()))
    return fr


# ------------------------------------------------------------------------------------------------ the sheets
HIT, SOLES = (0, -12), (0, 11)
EMPTY = None


def place(cell, anchor, spot):
    """The picture with its anchor (x, y in its own squares) on a spot from the pivot, as a frame centred on the
    pivot (odd sizes); EMPTY: a 3 x 3 frame with nothing in it."""
    if cell is EMPTY:
        return np.zeros((3, 3, 4), np.uint8)
    ax, ay = anchor
    h, w = cell.shape[:2]
    x0, y0 = int(round(spot[0] - ax)), int(round(spot[1] - ay))
    hw = max(abs(x0), abs(x0 + w - 1)) + 1
    hh = max(abs(y0), abs(y0 + h - 1)) + 1
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    out[hh + y0:hh + y0 + h, hw + x0:hw + x0 + w] = cell
    return out


def seq(frames, ms, spot, anchor=None):
    out = []
    for k, f in enumerate(frames):
        a = anchor if anchor is not None else ((f.shape[1] - 1) / 2, (f.shape[0] - 1) / 2) if f is not EMPTY else None
        out.append((place(f, a, spot), ms[k] if isinstance(ms, (list, tuple)) else ms))
    return out


def flight(frames, ms, total, lead):
    """A flying picture's frames (import_jhin.flight): `lead` empty ticks, then the frames in turn every ms over
    `total` ms, the last held a second (the loop never restarts in a flight)."""
    k = max(1, math.ceil(total / ms))
    cells = [EMPTY] + [frames[i % len(frames)] for i in range(k)]
    return seq(cells, [lead * 1000 / 60] + [ms] * (k - 1) + [1000], (0, 0))


CELLS = {}


def tables():
    fx, big = {}, {}

    def cells(name, drawn):
        CELLS[name] = drawn[0] if isinstance(drawn, tuple) else drawn
        return drawn

    # the attack: 52 px at 5 a tick (~10 ticks), a homing bolt chasing: drawn for twice that; the Meep 4.5 a tick
    fx["a_bolt"] = flight(cells("a_bolt", a_bolt()), 60, 360, lead=2)
    fx["a_hit"] = seq(cells("a_hit", a_hit()), [40, 50, 60, 70], HIT)
    fx["p_meep"] = flight(cells("p_meep", p_meep()), 70, 420, lead=2)
    fx["p_hit"] = seq(cells("p_hit", p_hit()), [40, 50, 60, 70, 80], HIT)
    # Q: 95 px at 6 a tick (16 ticks); the shrine to an ally within 50 px at 4 a tick
    fx["q_bolt"] = flight(cells("q_bolt", q_bolt()), 60, 300, lead=1)
    fx["q_hit"] = seq(cells("q_hit", q_hit()), [40, 50, 60, 70, 80], HIT)
    fx["q_bind"] = seq(cells("q_bind", q_bind()), [220, 256, 256, 256, 256, 256], (0, -4))
    fx["w_shrine"] = flight(cells("w_shrine", w_shrine()), 80, 480, lead=2)
    f, ax, ay = cells("w_land", w_land())
    fx["w_land"] = seq(f, [60, 80, 100, 110, 110, 90], SOLES, (ax, ay))
    f, ax, ay = cells("e_ride", e_ride())
    fx["e_ride"] = seq(f, [60, 80, 80, 80], SOLES, (ax, ay))
    fx["p_slow"] = fx["q_slow"] = seq(cells("slow", slow()), 100, SOLES)
    fx["w_haste"] = fx["e_haste"] = seq(cells("haste", haste()), 90, (0, 11 - 3))
    f, ax, ay = cells("e_door", e_door())
    big["e_door"] = big["e_door_out"] = seq(f, [50, 60, 150, 150, 60, 50], SOLES, (ax, ay))
    big["r_orb"] = seq(cells("r_orb", r_orb()), 70, (0, 0))
    f, ax, ay = cells("r_mark", r_mark())
    big["r_mark"] = seq(f, [60, 60, 70, 70, 70, 70], SOLES, (ax, ay))
    f, ax, ay = cells("r_dome", r_dome())
    big["r_dome"] = seq(f, [40, 60, 80, 100, 120], SOLES, (ax, ay))
    f, ax, ay = cells("r_lock", r_lock())
    big["r_lock"] = seq(f, [417, 417, 417, 417, 416, 416], SOLES, (ax, ay))
    f, ax, ay = cells("r_free", r_free())
    big["r_free"] = seq(f, [50, 60, 70, 80], SOLES, (ax, ay))
    return fx, big


TB_NAMES = {"a_bolt", "p_meep", "q_bolt", "w_shrine"}


def check(fx, big):
    bad = []
    for tags in (fx, big):
        for name, frames in tags.items():
            for k, (a, _) in enumerate(frames):
                if name in TB_NAMES or name == "r_orb":
                    if not (a == a[::-1]).all():
                        bad.append(f"{name} {k + 1}: not symmetric top to bottom")
                if name not in TB_NAMES:
                    if not (a == a[:, ::-1]).all():
                        bad.append(f"{name} {k + 1}: not symmetric left to right")
                if a.shape[0] % 2 == 0 or a.shape[1] % 2 == 0:
                    bad.append(f"{name} {k + 1}: even size {a.shape[:2]}")
    return bad


def review(path, z=6):
    rows = list(CELLS.items())
    W = max(sum(f.shape[1] + 2 for f in fr) for _, fr in rows) * z + 80
    H = sum(max(f.shape[0] for f in fr) * z + 6 for _, fr in rows)
    img = Image.new("RGBA", (W, H), (36, 40, 34, 255))
    d = ImageDraw.Draw(img)
    y = 0
    for name, fr in rows:
        d.text((4, y + 2), name, fill=(255, 255, 255, 255))
        x = 80
        hh = max(f.shape[0] for f in fr)
        for f in fr:
            img.alpha_composite(Image.fromarray(f).resize((f.shape[1] * z, f.shape[0] * z), Image.NEAREST),
                                (x, y + (hh - f.shape[0]) * z))
            x += (f.shape[1] + 2) * z
        y += hh * z + 6
    img.convert("RGB").save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    fx, big = tables()
    bad = check(fx, big)
    for b in bad:
        print("BAD", b)
    for sheet, tags in (("league_bard_fx", fx), ("league_bard_big", big)):
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    if a.review:
        review(a.review)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
