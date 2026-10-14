#!/usr/bin/env python3
"""Nilah's effects drawn square by square (Codex ran out of quota after its first try, 2026-10-14: 「codex没额度了 你能直接
做吗特效」) from assets/source/nilah/PROMPTS_FX.md - the same names, frame counts, sizes and ramps - as the game sheets
league_nilah_fx and league_nilah_big.

    python tools/art/fx_nilah.py --drawn [--review DIR]      # DIR: every effect at 6x and a GIF of each on her idle

SUPERSEDED: the sheets now come from Codex's overview (tools/art/import_nilah_fx.py, the user: 「你拿我给你的这个修复啊
这个特效好啊」); this file keeps the effects table (FX: spots, times, sheets), Pic / Dense and review() that tool uses,
and writes its own drawings only with --drawn.

Every picture is hard-edged pixel art in game pixels, no outline: her water ramp (white core to deep blue) and the joy
ramp (pastel pink, lilac, sky, mint, gold) for the veil, the heal and the storm's glints. Brighter squares win where two
shapes meet, and every frame is made left-right symmetric about the pivot's column (the client never mirrors an effect
picture, champion-data section 6): a shape is drawn, then each square takes the brighter of itself and its mirror.
The pictures round a figure (eq_spin, r_spin, r_burst, q_on, w_on, w_ally, r_heal) keep its middle clear except the
rings' front arcs, which pass in front of her legs. Spots are game px from the pivot (x forward, y down; the soles are
11 under it); times from the kit (tools/kit/build_nilah.py P, 60 ticks a second).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

MOD = os.path.join(ROOT, "league")
HEX = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
WATER = [HEX(h) for h in ("#FFFFFF", "#DFFBFF", "#9EEBFF", "#4FC8F2", "#1E8FD0", "#0E5294")]
JOY = {k: HEX(h) for k, h in (("white", "#FFFFFF"), ("blush", "#FFE3F4"), ("pink", "#F7A6DA"), ("lilac", "#CDA2FF"),
                               ("sky", "#9FC4FF"), ("mint", "#8EF2DC"), ("gold", "#FFE68A"))}
W = WATER
HUES = ["pink", "lilac", "sky", "mint", "gold"]
LUM = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]

HIT = (0, -14)       # a hit on a unit's upper body
CORE = (0, -7)       # her waist: the rings' centre
SOLES = (0, 11)


class Pic:
    """A frame in game px, x from -hw to hw (the pivot's column 0), y from y0 to y1 (pivot-relative)."""

    def __init__(self, hw, y0, y1):
        self.hw, self.y0 = hw, y0
        self.a = np.zeros((y1 - y0 + 1, 2 * hw + 1, 4), np.uint8)

    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        j, i = y - self.y0, x + self.hw
        if 0 <= j < self.a.shape[0] and 0 <= i < self.a.shape[1]:
            old = self.a[j, i]
            if old[3] == 0 or LUM(c) > LUM(old[:3]):
                self.a[j, i] = (*c, 255)

    def grid(self):
        ys, xs = np.mgrid[0:self.a.shape[0], 0:self.a.shape[1]]
        return xs - self.hw, ys + self.y0

    def field(self, mask_levels):
        """[(bool mask, colour)] painted in turn (brighter wins)."""
        for m, c in mask_levels:
            for j, i in zip(*np.nonzero(m)):
                self.put(i - self.hw, j + self.y0, c)

    def clear(self, m):
        self.a[m] = 0

    def mirror(self):
        b = self.a[:, ::-1]
        lum = self.a[..., :3].astype(float) @ np.array([0.3, 0.59, 0.11])
        lumb = b[..., :3].astype(float) @ np.array([0.3, 0.59, 0.11])
        take = (b[..., 3] > 0) & ((self.a[..., 3] == 0) | (lumb > lum))
        self.a[take] = b[take]
        return self

    def frame(self, spot):
        """The frame centred on the pivot, the picture's origin on spot."""
        sx, sy = spot
        return G.centre_frame(self.a, -self.hw + sx, self.y0 + sy)


# ---------------------------------------------------------------- shapes
def blob(p, cx, cy, r, ramp, lobes=0, wob=0.0, hollow=0.0, cut=(0.32, 0.58, 0.82)):
    """A splash round (cx, cy): ramp[0] in the core, then ramp[1], ramp[2], ramp[3] out to its rim; lobes waves the rim
    (symmetric: the angle is from straight up, on |x|); hollow empties the middle out to that fraction."""
    X, Y = p.grid()
    dx, dy = X - cx, Y - cy
    th = np.arctan2(np.abs(dx), -dy)
    rr = r * (1 + wob * np.cos(lobes * th)) if lobes else r
    rho = np.hypot(dx, dy) / np.maximum(rr, 0.5)
    inside = rho <= 1.0
    if hollow:
        inside &= rho >= hollow
    levels = []
    bands = [0.0, *cut, 1.0]
    for k in range(len(bands) - 1):
        lo, hi = bands[k], bands[k + 1]
        if hollow:       # a ring: the brightest on its inner edge
            m = inside & (rho >= hollow + (1 - hollow) * lo) & (rho <= hollow + (1 - hollow) * hi + 1e-9)
        else:
            m = inside & (rho >= lo) & (rho <= hi + 1e-9)
        levels.append((m, ramp[min(k, len(ramp) - 1)]))
    p.field(levels)


def ring(p, cx, cy, rx, ry, t, col, arc=None, gaps=None):
    """An elliptical band t px thick inward from (rx, ry); arc(theta) -> colour or None per angle (theta from the front,
    0 = straight down toward the viewer, symmetric on |x|)."""
    X, Y = p.grid()
    dx, dy = X - cx, Y - cy
    o = (dx / (rx + 0.5)) ** 2 + (dy / (ry + 0.5)) ** 2 <= 1
    i = (dx / max(rx - t + 0.5, 0.1)) ** 2 + (dy / max(ry - t + 0.5, 0.1)) ** 2 < 1
    m = o & ~i
    th = np.arctan2(np.abs(dx) / rx, dy / ry)  # the ellipse's own angle: 0 at the front (below), pi at the back
    for j, k in zip(*np.nonzero(m)):
        c = col if arc is None else arc(th[j, k])
        if c is not None:
            p.put(k - p.hw, j + p.y0, c)


def line(p, x0, y0, x1, y1, col, w=1):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for s in np.linspace(0, 1, n):
        x, y = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
        for ox in range(-(w // 2), w - w // 2):
            if abs(x1 - x0) >= abs(y1 - y0):
                p.put(x, y + ox, col)
            else:
                p.put(x + ox, y, col)


def streak(p, x0, y0, x1, y1, ramp, w=3):
    """A blade of water: a white middle line, ramp[1] beside it, ramp[2] at its ends."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L == 0:
        return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    n = int(L * 2) + 1
    for s in np.linspace(0, 1, n):
        x, y = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
        end = min(s, 1 - s) * L
        core = ramp[0] if end > 1.5 else ramp[2]
        p.put(x, y, core)
        if w >= 3 and end > 0.8:
            half = (w - 1) / 2 * min(1.0, end / 3.0)
            for k in (-1, 1):
                p.put(x + nx * k * half, y + ny * k * half, ramp[1] if end > 2.5 else ramp[3])


def drop(p, x, y, size, ramp):
    """A droplet: 1 px of ramp[0] (size 1), a 2x2 with a white corner (size 2), a 3-px plus (size 3)."""
    if size <= 1:
        p.put(x, y, ramp[0])
    elif size == 2:
        p.put(x, y, ramp[0]); p.put(x + 1, y, ramp[1]); p.put(x, y + 1, ramp[1]); p.put(x + 1, y + 1, ramp[2])
    else:
        p.put(x, y, ramp[0])
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            p.put(x + dx, y + dy, ramp[1])


def sparkle(p, x, y, arm, col, inner=None):
    """A four-point twinkle: a white middle, arms of col (inner next to the middle; the water's pale blue on the water
    effects, blush on the joy's)."""
    p.put(x, y, JOY["white"])
    if inner is None:
        inner = W[1] if col in WATER else JOY["blush"]
    for k in range(1, arm + 1):
        c = col if k == arm else inner
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            p.put(x + dx, y + dy, c)


def ray_drops(p, cx, cy, r, angles, size, ramp):
    """Droplets at radius r, at angles (degrees from straight up, mirrored by the frame's symmetry)."""
    for a in angles:
        t = math.radians(a)
        drop(p, cx + r * math.sin(t), cy - r * math.cos(t), size, ramp)


FADE = [W[2], W[3], W[4], W[5]]
DIM = [W[3], W[4], W[5], W[5]]


# ---------------------------------------------------------------- the hits (on the target, z over it)
def a_hit():
    out = []
    p = Pic(6, -6, 6); sparkle(p, 0, 0, 2, W[2]); out.append(p)
    p = Pic(6, -6, 6); blob(p, 0, 0, 4.4, W, lobes=6, wob=0.12); ray_drops(p, 0, 0, 5.6, (35, 95, 150), 1, W); out.append(p)
    p = Pic(6, -6, 6); blob(p, 0, 0, 5.4, [W[1], W[2], W[3], W[4]], lobes=6, wob=0.15, hollow=0.45)
    ray_drops(p, 0, 0, 6, (30, 90, 150), 1, W[1:]); out.append(p)
    p = Pic(6, -6, 6); ray_drops(p, 0, 0, 6, (25, 70, 120, 165), 1, FADE); ray_drops(p, 0, 0, 3, (60, 140), 1, DIM)
    out.append(p)
    return out


def qa_hit():
    out = []
    p = Pic(7, -7, 7); sparkle(p, 0, 0, 2, W[1]); p.put(0, -3, W[2]); p.put(0, 3, W[2]); out.append(p)
    p = Pic(7, -7, 7); blob(p, 0, 0, 5, [W[2], W[3], W[3], W[4]], lobes=6, wob=0.12); streak(p, 0, -6, 0, 6, W, 3)
    out.append(p)
    p = Pic(7, -7, 7); blob(p, 0, 0, 6.6, [W[1], W[2], W[3], W[4]], lobes=6, wob=0.14, hollow=0.5)
    streak(p, 0, -4, 0, 4, [W[1], W[2], W[3], W[4]], 1)
    for (x, y), h in zip(((4, -5), (6, 2)), ("pink", "mint")):
        sparkle(p, x, y, 1, JOY[h])
    out.append(p)
    p = Pic(7, -7, 7); ray_drops(p, 0, 0, 6.5, (40, 100, 160), 1, FADE); p.put(5, -5, JOY["lilac"]); p.put(6, 3, JOY["sky"])
    out.append(p)
    return out


def q_hit():
    out = []
    p = Pic(8, -8, 8); sparkle(p, 0, 0, 3, W[2]); out.append(p)
    p = Pic(8, -8, 8); streak(p, -5, -5, 5, 5, W, 3); out.append(p)
    p = Pic(8, -8, 8); blob(p, 0, 0, 7.8, [W[2], W[3], W[4], W[5]], lobes=8, wob=0.1, hollow=0.62)
    streak(p, -6, -6, 6, 6, W, 3); ray_drops(p, 0, 0, 8, (0, 90, 180), 1, W); out.append(p)
    p = Pic(8, -8, 8)
    for a, b in ((2.2, 3.6), (5.2, 6.8)):
        line(p, a, a, b, b, W[1]); line(p, a, a + 1, b - 1, b, W[3])
    ray_drops(p, 0, 0, 8, (20, 70, 115, 160), 2, W[1:]); out.append(p)
    p = Pic(8, -8, 8); ray_drops(p, 0, 0, 8, (30, 80, 130, 170), 1, FADE); ray_drops(p, 0, 0, 4.5, (45, 135), 1, DIM)
    out.append(p)
    return out


def eq_hit():
    out = []
    p = Pic(7, -7, 7); sparkle(p, 0, 0, 2, W[1]); p.put(1, 1, W[2]); p.put(1, -1, W[2]); out.append(p)
    p = Pic(7, -7, 7); ring(p, 0, 0, 5, 5, 1, W[0], arc=lambda t: W[0] if t < 2.4 else W[1])
    ring(p, 0, 0, 4, 4, 1, W[2]); out.append(p)
    p = Pic(7, -7, 7); ring(p, 0, 0, 7, 7, 1, W[2], arc=lambda t: W[2] if (t * 6 / math.pi) % 2 < 1.2 else None)
    ring(p, 0, 0, 6, 6, 1, W[3], arc=lambda t: W[3] if (t * 6 / math.pi) % 2 < 1.2 else None)
    ray_drops(p, 0, 0, 7, (30, 90, 150), 2, W); out.append(p)
    p = Pic(7, -7, 7); ray_drops(p, 0, 0, 7, (30, 90, 150), 1, FADE); out.append(p)
    return out


def e_hit():
    out = []
    p = Pic(7, -9, 6); sparkle(p, 0, 0, 2, W[1]); p.put(0, -3, W[2]); out.append(p)
    p = Pic(7, -9, 6)
    for x, top in ((0, -8), (1, -6), (2, -3)):
        line(p, x, top, x, 4, W[0] if x == 0 else W[1] if x == 1 else W[3])
    p.put(0, -8, W[1]); blob(p, 0, 4, 3, [W[2], W[3], W[4], W[4]])
    drop(p, 4, 1, 1, W); drop(p, 5, -2, 1, W[1:]); out.append(p)
    p = Pic(7, -9, 6)
    X, Y = p.grid()
    e = (X / 7.5) ** 2 + ((Y - 3) / 2.6) ** 2
    p.field([(e <= 1, W[3]), (e <= 0.6, W[2]), (e <= 0.25, W[1])])
    line(p, 0, -3, 0, 1, W[1]); drop(p, 1, -6, 1, W); drop(p, 5, -3, 2, W[1:]); out.append(p)
    p = Pic(7, -9, 6); ray_drops(p, 0, 3, 6.5, (55, 95), 1, FADE); drop(p, 3, -3, 1, W[3:]); drop(p, 0, 4, 1, W[4:])
    out.append(p)
    return out


def r_hit():
    out = []
    p = Pic(6, -6, 6); p.put(0, 0, W[0]); p.put(1, 0, W[1]); p.put(0, 1, W[1]); p.put(0, -1, W[1]); out.append(p)
    p = Pic(6, -6, 6); streak(p, -4, -4, 4, 4, W, 3); out.append(p)
    p = Pic(6, -6, 6); streak(p, -5, -5, 5, 5, [W[1], W[2], W[3], W[4]], 3); ray_drops(p, 0, 0, 6, (0, 90), 1, W)
    out.append(p)
    p = Pic(6, -6, 6); ray_drops(p, 0, 0, 6, (20, 90, 160), 1, FADE); line(p, 2, 2, 3, 3, W[4]); out.append(p)
    return out


def r_pull():
    out = []
    p = Pic(9, -9, 9); ring(p, 0, 0, 9, 9, 2, W[2], arc=lambda t: W[1] if (t * 4 / math.pi) % 2 < 1 else W[3]); out.append(p)
    p = Pic(9, -9, 9); ring(p, 0, 0, 5, 5, 2, W[1])
    for a in (45, 135):               # the streaks curling in
        t = math.radians(a)
        for s in np.linspace(0, 1, 9):
            r = 9 - 3 * s
            tt = t - 0.5 * (1 - s)
            p.put(r * math.sin(tt), -r * math.cos(tt), W[2] if s > 0.5 else W[3])
    out.append(p)
    p = Pic(9, -9, 9); blob(p, 0, 0, 4.2, W, lobes=4, wob=0.2); sparkle(p, 0, 0, 4, W[2]); out.append(p)
    p = Pic(9, -9, 9); blob(p, 0, 0, 8.8, [W[1], W[2], W[3], W[4]], lobes=8, wob=0.12, hollow=0.55)
    ray_drops(p, 0, 0, 9, (0, 45, 90, 135, 180), 1, W); out.append(p)
    p = Pic(9, -9, 9); ray_drops(p, 0, 0, 8.5, (20, 65, 110, 155), 2, FADE); ray_drops(p, 0, 0, 5, (45, 135), 1, DIM)
    out.append(p)
    return out


# ---------------------------------------------------------------- on allies
def ribbon(p, side_x, y_bot, y_top, amp, phase, hues, wave=18.0, flow=None, thick=(0.25, 0.7)):
    """A thin ribbon of light rising from y_bot to y_top at side_x (its mirror comes with the frame), one smooth wave of
    amp px; its colour runs through hues bottom to top; 2 px thick between thick[0] and thick[1] of its height, 1 px at
    its ends; flow (offset, duty) cuts it into three pieces that move up with offset."""
    n = max(1, y_bot - y_top)
    for y in range(y_top, y_bot + 1):
        s = (y_bot - y) / n
        if flow is not None and ((s * 3 - flow[0]) % 1.0) > flow[1]:
            continue
        x = side_x + amp * math.sin(2 * math.pi * (y / wave) + phase)
        c = JOY[hues[min(len(hues) - 1, int(s * len(hues)))]]
        p.put(x, y, c)
        if thick[0] < s < thick[1]:
            p.put(x + (1 if side_x > 0 else -1), y, c)


def w_ally():
    """The veil touching an ally: sparkles, then ribbons rising at both sides, opening and fading."""
    out = []
    S = 11
    p = Pic(16, -24, 10)
    for x, y in ((S, -4), (S + 1, -14)):
        sparkle(p, x, y, 1, JOY["pink"])
    out.append(p)
    p = Pic(16, -24, 10)
    ribbon(p, S, 9, -8, 1.0, 0.0, ["mint", "sky", "lilac", "pink"])
    sparkle(p, S + 3, -6, 1, JOY["gold"]); sparkle(p, S - 1, -13, 1, JOY["pink"]); out.append(p)
    p = Pic(16, -24, 10)
    ribbon(p, S + 1, 9, -18, 1.5, 0.9, ["mint", "sky", "lilac", "pink", "gold"])
    for (x, y, h) in ((S + 4, -14, "gold"), (S, -21, "pink"), (S + 4, 2, "mint")):
        sparkle(p, x, y, 2 if y < -10 else 1, JOY[h])
    out.append(p)
    p = Pic(16, -24, 10)
    ribbon(p, S + 2, 2, -21, 1.5, 1.8, ["sky", "lilac", "pink"], flow=(0.3, 0.55))
    sparkle(p, S + 3, -22, 1, JOY["gold"]); p.put(S - 1, -12, JOY["mint"]); out.append(p)
    p = Pic(16, -24, 10)
    p.put(S + 2, -22, JOY["pink"]); p.put(S + 4, -11, JOY["mint"]); p.put(S, -17, JOY["white"]); out.append(p)
    for q in out:
        q.clear(np.abs(q.grid()[0]) <= S - 3)
    return out


def r_heal():
    """The heal and shield: a water glow under the ally, thin lines of light rising at its sides with bubbles and
    glints, a thin dome of light over it (the shield), fading."""
    out = []
    S = 11

    def glow(p, rx, cols):
        X, Y = p.grid()
        e = (X / rx) ** 2 + ((Y - 10) / 1.5) ** 2
        p.field([(e <= 1, cols[0]), (e <= 0.4, cols[1])])

    p = Pic(14, -26, 11); glow(p, 8.5, (W[3], W[2])); out.append(p)
    p = Pic(14, -26, 11); glow(p, 11.5, (W[3], W[2]))
    for x, top in ((S, -2), (S + 2, 3)):
        line(p, x, top, x, 8, W[2] if x == S else W[3])
    p.put(S, -3, W[1])
    for x, y in ((S + 2, -4), (S - 1, -9)):
        drop(p, x, y, 1, W[1:])
    out.append(p)
    p = Pic(14, -26, 11); glow(p, 12.5, (W[4], W[3]))
    for x, top, bot in ((S, -16, -9), (S, -6, 2), (S + 2, -3, 6)):
        line(p, x, top, x, bot, W[1] if x == S else W[3])
    for x, y, h in ((S + 3, -11, "pink"), (S - 1, -20, "gold"), (S + 3, 1, "mint")):
        sparkle(p, x, y, 1, JOY[h])
    drop(p, S - 2, -24, 2, W); out.append(p)
    p = Pic(14, -26, 11)
    ring(p, 0, -6, S + 1, 19, 1, W[1], arc=lambda t: (JOY["lilac"] if t < 2.0 else W[1]) if 1.25 < t < 2.45 else None)
    for x, y, h in ((S + 3, -20, "pink"), (S + 3, -2, "mint")):
        sparkle(p, x, y, 1, JOY[h])
    drop(p, S + 1, 6, 1, W[2:]); out.append(p)
    p = Pic(14, -26, 11)
    ring(p, 0, -6, S + 1, 19, 1, W[3], arc=lambda t: W[3] if 1.9 < t < 2.45 else None)
    for x, y in ((S + 1, -12), (S + 2, -1), (S - 2, -23)):
        drop(p, x, y, 1, FADE)
    out.append(p)
    for q in out:
        X, Y = q.grid()
        q.clear((np.abs(X) <= S - 3) & (Y > -24) & (Y < 9))
    return out


# ---------------------------------------------------------------- round her (big, z over her)
def spin_arc(lead, bright, base, dark=None, span=0.9, mid=None):
    """A ring's colour by angle: bright at the two leading arcs at +-lead (mirrored), mid just behind them, base behind
    those out to span, dark (or none) elsewhere."""
    def f(t):
        d = min(abs(t - lead), abs(t - (math.pi - lead)))
        if d < 0.16:
            return bright
        if mid is not None and d < 0.34:
            return mid
        if d < span:
            return base
        return dark
    return f


def keep_out(p, hw, top, bot, front=True):
    """Clear the figure's middle (|x| <= hw, top..bot); front keeps the squares below the ring's centre (its front arc)."""
    X, Y = p.grid()
    m = (np.abs(X) <= hw) & (Y >= top) & (Y <= bot)
    if front:
        m &= Y < 0
    p.clear(m)


def eq_spin():
    out = []
    p = Pic(29, -13, 13); ring(p, 0, 0, 20, 7, 2, W[1], arc=lambda t: W[0] if t < 0.5 else W[2] if t < 1.25 else None)
    out.append(p)
    p = Pic(29, -13, 13); ring(p, 0, 0, 26, 10, 3, W[3], arc=spin_arc(0.7, W[0], W[3], W[4], 0.8, mid=W[2]))
    ring(p, 0, 0, 26, 10, 1, W[1], arc=lambda t: W[1] if t < 0.9 else None)
    out.append(p)
    p = Pic(29, -13, 13); ring(p, 0, 0, 28, 11, 3, W[3], arc=spin_arc(1.6, W[0], W[3], W[4], 0.7, mid=W[2]))
    ring(p, 0, 0, 28, 11, 1, W[1], arc=lambda t: W[1] if 1.3 < t < 1.9 else None)
    for a in (55, 100, 135):
        t = math.radians(a)
        drop(p, 29 * math.sin(t) * 0.98, -12 * math.cos(t), 2, W)
    out.append(p)
    p = Pic(29, -13, 13)
    ring(p, 0, 0, 28, 11, 1, W[3], arc=lambda t: W[2] if (t * 9 / math.pi) % 2 < 0.8 else None)
    for a in (20, 70, 110, 160):
        t = math.radians(a)
        drop(p, 29 * math.sin(t), -12 * math.cos(t), 2, W[1:])
    out.append(p)
    p = Pic(29, -13, 13)
    for a in (35, 85, 130, 170):
        t = math.radians(a)
        drop(p, 28 * math.sin(t), -12 * math.cos(t), 1, FADE)
    out.append(p)
    for q in out:
        keep_out(q, 6, -13, 13)
    return [q for q in out]


def r_spin():
    out = []
    glints = ["pink", "mint", "gold", "lilac"]
    for k in range(8):
        grow = min(1.0, (k + 1) / 3.0) if k < 7 else 0.85
        p = Pic(38, -17, 17)
        # the ripple on the ground (her soles 18 under the ring's centre)
        ring(p, 0, 15, int(30 * grow), int(2 * grow) + 1, 1, W[4],
             arc=lambda t, k=k: W[3] if ((t * 10 / math.pi + k * 0.5) % 2) < 1 else None)
        lead = (k * 0.55) % math.pi
        ring(p, 0, 0, int(round(38 * grow)), int(round(15 * grow)), 2, W[3],
             arc=spin_arc(lead, W[0], W[3], W[4], 0.7, mid=W[2]))
        lead2 = (math.pi - k * 0.8) % math.pi
        ring(p, 0, -1, int(round(25 * grow)), int(round(10 * grow)), 2, W[2],
             arc=spin_arc(lead2, W[1], W[3], None, 0.6))
        if k >= 2:
            for j, a in enumerate((40 + 13 * k % 30, 95, 140 - 9 * k % 25)):
                t = math.radians(a)
                rr = 38 * grow + 1
                x, y = rr * math.sin(t), -16 * grow * math.cos(t)
                if j == 1:
                    sparkle(p, x, y, 1, JOY[glints[k % 4]])
                else:
                    drop(p, x, y, 2 if (j + k) % 2 else 1, W)
        p.mirror()
        keep_out(p, 7, -17, 17)
        out.append(p)
    return out


def r_burst():
    out = []
    p = Pic(40, -18, 18); ring(p, 0, 0, 15, 6, 2, W[0], arc=lambda t: W[0] if t < 1.6 or t > 2.6 else W[1]); out.append(p)
    p = Pic(40, -18, 18)
    ring(p, 0, 0, 28, 12, 3, W[3], arc=lambda t: W[2] if t < 1.0 else W[3] if t < 2.2 else W[4])
    ring(p, 0, 0, 28, 12, 1, JOY["lilac"], arc=lambda t: JOY["pink"] if t < 0.9 else JOY["lilac"] if t < 1.9 else JOY["mint"])
    ring(p, 0, 0, 25, 9, 1, W[0], arc=lambda t: W[0] if t < 2.0 else None)
    out.append(p)
    p = Pic(40, -18, 18)
    ring(p, 0, 0, 40, 18, 3, W[3], arc=lambda t: W[2] if t < 1.2 else W[3] if t < 2.4 else W[4])
    ring(p, 0, 0, 40, 18, 1, JOY["mint"], arc=lambda t: JOY["gold"] if t < 0.6 else JOY["pink"] if t < 1.6 else JOY["lilac"])
    ring(p, 0, 0, 37, 15, 1, W[1], arc=lambda t: W[1] if t < 2.2 else None)
    for a, h in ((50, "pink"), (120, "mint"), (160, "gold")):
        t = math.radians(a)
        sparkle(p, 33 * math.sin(t), -13 * math.cos(t), 1, JOY[h])
    out.append(p)
    p = Pic(40, -18, 18)
    ring(p, 0, 0, 40, 18, 1, W[3], arc=lambda t: W[2] if (t * 10 / math.pi) % 2 < 0.9 else None)
    for a in (25, 60, 95, 130, 165):
        t = math.radians(a)
        drop(p, 38 * math.sin(t), -17 * math.cos(t), 2, W[1:])
    sparkle(p, 30, -6, 1, JOY["lilac"]); out.append(p)
    p = Pic(40, -18, 18)
    for a in (40, 80, 115, 150):
        t = math.radians(a)
        drop(p, 39 * math.sin(t), -17 * math.cos(t), 1, FADE)
    p.put(28, 8, JOY["pink"]); p.put(33, -9, JOY["mint"]); out.append(p)
    for q in out:
        keep_out(q, 7, -18, 18)
    return out


# ---------------------------------------------------------------- buffs (looped)
def q_on():
    """Six droplets round her taking turns to brighten, thin pale arcs at her sides that shimmer (centre (0, -9))."""
    out = []
    spots = [(13, -12), (15, -3), (13, 7)]           # right half (mirrored): high, middle, low, from her centre
    for k in range(4):
        p = Pic(16, -27, 7)
        for j, (x, y) in enumerate(spots):
            hot = (j == k % 3)
            drop(p, x, y - 9, 2 if hot else 1, W if hot else W[3:])
        for y in range(-22, 2):
            phase = (y + 2 * k) % 8
            if phase < 3:
                p.put(16 if -16 < y < -4 else 15, y, W[2] if phase == 1 else W[3])
        p.mirror()
        out.append(p)
    return out


def veil(hw, y_bot, y_top, side, ribbons, sparks):
    """Thin ribbons of the joy's colours flowing up both her sides (their pieces move up each frame, a seamless loop of
    6), white-hearted sparkles taking turns."""
    out = []
    for k in range(6):
        p = Pic(hw, y_top - 2, y_bot)
        for j, (dx, amp, hues, top) in enumerate(ribbons):
            ribbon(p, side + dx, y_bot, y_top + top, amp, j * math.pi, hues, wave=20.0 + 4 * j,
                   flow=(k / 6.0 + j * 0.5, 0.62))
        for j, (x, y) in enumerate(sparks):
            if (j + k) % 3 == 0:
                sparkle(p, x, y, 2 if j % 2 == 0 else 1, JOY["gold" if j % 2 else "pink"])
            elif (j + k) % 3 == 1:
                p.put(x, y, JOY["blush"])
        p.mirror()
        X, _ = p.grid()
        p.clear(np.abs(X) < side - 2)
        out.append(p)
    return out


def w_on():
    return veil(19, 10, -34, 13, [(0, 1.5, ["mint", "sky", "lilac", "pink", "gold"], 0),
                                 (2, 1.2, ["pink", "lilac", "sky", "mint"], 8)],
                [(16, -30), (14, -10), (17, 3), (13, -22), (18, -17)])


def w_ally_veil():
    return veil(17, 10, -29, 12, [(0, 1.3, ["sky", "lilac", "pink", "gold"], 0), (2, 1.0, ["mint", "sky", "pink"], 9)],
                [(14, -25), (15, -6), (12, -17), (16, 3)])


# ---------------------------------------------------------------- drawn into her frames (her dense squares)
# The whips and the dash's wake have a front and a back, so they go into her own frames (the client mirrors those on
# the red side). They are drawn on her frames' canvas (tools/art/import_nilah_strips.py: 219 x 146 squares, the
# pivot's column PIV 80, the soles on row 140), widened to BAKE_W for Q's reach, at PPU 2.5 squares a game pixel;
# tools/art/rig_nilah.py lays them over (or under) her frames and keeps them in their own strips, which
# tools/art/ppu_restyle.py (RESTYLE["nilah"] fx) puts on after it grows her outline - an effect has no outline.
BAKE_W, BAKE_H = 270, 146
BAKE_DIR = os.path.join(ROOT, "assets", "source", "nilah", "fx_bake")


class Dense(Pic):
    """Her frames' canvas, x and y as the canvas's columns and rows."""

    def __init__(self):
        super().__init__(0, 0, BAKE_H - 1)
        self.a = np.zeros((BAKE_H, BAKE_W, 4), np.uint8)

    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= y < BAKE_H and 0 <= x < BAKE_W:
            old = self.a[y, x]
            if old[3] == 0 or LUM(c) > LUM(old[:3]):
                self.a[y, x] = (*c, 255)


def tube(p, pts, half, cols=(W[0], W[1], W[2], W[3]), cut=(0.3, 0.62, 0.92, 1.2)):
    """A band of water along pts (x, y) with half thickness half (one per point): cols from its middle line out."""
    from scipy import ndimage
    path = np.zeros((BAKE_H, BAKE_W), bool)
    hmap = np.zeros((BAKE_H, BAKE_W))
    for (x, y), h in zip(pts, half):
        xi, yi = int(round(x)), int(round(y))
        if 0 <= yi < BAKE_H and 0 <= xi < BAKE_W:
            path[yi, xi] = True
            hmap[yi, xi] = max(hmap[yi, xi], h)
    d, (iy, ix) = ndimage.distance_transform_edt(~path, return_indices=True)
    rho = d / np.maximum(hmap[iy, ix], 0.3)
    for k in range(len(cols) - 1, -1, -1):
        p.field([((rho <= cut[k]) & (hmap[iy, ix] > 0), cols[k])])


def path(x0, y0, x1, y1, wave=0.0, waves=1.0, phase=0.0):
    n = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 2
    out = []
    for s in np.linspace(0, 1, n):
        x, y = x0 + (x1 - x0) * s, y0 + (y1 - y0) * s
        out.append((x, y + wave * math.sin(2 * math.pi * waves * s + phase) * min(1.0, 4 * s)))
    return out


def taper(n, h0, h1, ends=0.15):
    """Half thicknesses along a band: h0 to h1, thinner over its last `ends`."""
    out = []
    for k in range(n):
        s = k / max(1, n - 1)
        h = h0 + (h1 - h0) * s
        if s > 1 - ends:
            h *= max(0.45, (1 - s) / ends)
        out.append(h)
    return out


def dense_splash(p, cx, cy, r, ring=False):
    X, Y = p.grid()
    d = np.hypot(X - cx, Y - cy) / r
    th = np.arctan2(np.abs(Y - cy), X - cx)       # symmetric about the whip's line
    d = d / (1 + 0.18 * np.cos(5 * th))
    if ring:
        p.field([((d <= 1) & (d > 0.55), W[2]), ((d <= 0.85) & (d > 0.6), W[1])])
    else:
        p.field([(d <= 1, W[3]), (d <= 0.75, W[2]), (d <= 0.5, W[1]), (d <= 0.25, W[0])])


def ddrop(p, x, y, big=False):
    p.put(x, y, W[0]); p.put(x + 1, y, W[1]); p.put(x, y + 1, W[2]); p.put(x + 1, y + 1, W[3])
    if big:
        p.put(x - 1, y, W[2]); p.put(x, y - 1, W[1]); p.put(x + 2, y, W[3]); p.put(x, y + 2, W[3])


def arc_band(p, cx, cy, r, half, a0, a1, cols=(W[0], W[1], W[2], W[3])):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
           for a in np.linspace(a0, a1, int(abs(a1 - a0) * r / 20) + 6)]
    tube(p, pts, [half * (0.5 + 0.5 * math.sin(math.pi * k / (len(pts) - 1))) + 0.4 for k in range(len(pts))], cols)


def bake():
    """{(tag, frame number): (over, under)} - the canvases (None where nothing)."""
    out = {}
    # the attack: the folded blade lets go its whip from the tip (166, 78) / (168, 74)
    p = Dense(); pts = path(166, 78, 181, 77, wave=2.0, waves=1.2)
    tube(p, pts, taper(len(pts), 1.4, 1.1)); ddrop(p, 176, 82); ddrop(p, 183, 73)
    out[("attack", 3)] = (p.a, None)
    p = Dense(); pts = path(168, 74, 189, 75, wave=0.8, waves=0.5)
    tube(p, pts, taper(len(pts), 1.5, 1.2, 0.05)); dense_splash(p, 190, 75, 4.2)
    for x, y in ((195, 70), (196, 80), (186, 69), (186, 81)):
        ddrop(p, x, y)
    out[("attack", 4)] = (p.a, None)
    # the empowered attack: a longer whip, a fan of water opening ahead of its tip
    p = Dense(); pts = path(169, 65, 195, 66, wave=1.5, waves=1.0)
    tube(p, pts, taper(len(pts), 1.6, 1.3)); arc_band(p, 189, 66, 10, 1.1, -14, 14)
    ddrop(p, 182, 61)
    out[("attack_q", 3)] = (p.a, None)
    p = Dense(); pts = path(164, 69, 196, 69, wave=0.6, waves=0.5)
    tube(p, pts, taper(len(pts), 1.6, 1.4, 0.05))
    for r, h, a in ((10, 1.6, 26), (19, 1.5, 26), (28, 1.3, 25)):
        arc_band(p, 196, 69, r, h, -a, a)
    for a in (-27, 27):                   # the fan's edges
        t = math.radians(a)
        line(p, 198 + 3 * math.cos(t), 69 + 3 * math.sin(t), 196 + 29 * math.cos(t), 69 + 29 * math.sin(t), W[3])
    for a in (-24, -8, 8, 24):
        t = math.radians(a)
        ddrop(p, 196 + 32 * math.cos(t), 69 + 32 * math.sin(t), big=abs(a) < 10)
    out[("attack_q", 4)] = (p.a, None)
    # Formless Blade: the whip straight out to 62 game px (column 80 + 62 x 2.5 = 235), then its spray along the line
    p = Dense(); pts = path(191, 70, 235, 70)
    tube(p, pts, taper(len(pts), 1.3, 1.2, 0.03)); dense_splash(p, 236, 70, 5.5)
    for x, y in ((203, 66), (214, 74), (224, 66), (243, 64), (243, 76)):
        ddrop(p, x, y)
    out[("skill", 4)] = (p.a, None)
    p = Dense()
    for x0, x1, c in ((196, 203, W[4]), (207, 213, W[3]), (217, 225, W[3]), (228, 236, W[2])):
        line(p, x0, 70, x1, 70, c)
    for x, y in ((205, 68), (220, 72), (232, 67), (238, 72)):
        ddrop(p, x, y)
    out[("skill", 5)] = (p.a, None)
    # Slipstream: a wake trailing left from her waist, under her
    for k, (wx, wy, L, h, spray) in enumerate(((95, 108, 62, 2.6, 0.0), (106, 107, 88, 3.2, 0.0),
                                               (117, 106, 90, 3.0, 0.45)), 1):
        p = Dense()
        n = 120
        pts, hs = [], []
        for j in range(n):
            s = j / (n - 1)
            if spray and s > 1 - spray and j % 7 > 2:
                continue
            pts.append((wx - L * s, wy + 2.0 * math.sin(s * 3.0 * math.pi + k)))
            hs.append(h * (1 - 0.6 * s))
        tube(p, pts, hs, (W[1], W[2], W[3], W[4]))
        # the crest: a white line along its top
        for (x, y), hh in zip(pts, hs):
            p.put(x, y - hh * 0.9, W[0])
        for x, y in ((wx - L - 3, wy - 4), (wx - L + 4, wy + 5), (wx - L * 0.6, wy - 6)):
            ddrop(p, x, y)
        out[("skill2", k)] = (None, p.a)
    return out


def write_bake():
    os.makedirs(BAKE_DIR, exist_ok=True)
    for old in os.listdir(BAKE_DIR):
        if old.endswith(".png"):
            os.remove(os.path.join(BAKE_DIR, old))
    for (tag, k), (over, under) in bake().items():
        for a, suf in ((over, ""), (under, "_under")):
            if a is not None:
                Image.fromarray(a).save(os.path.join(BAKE_DIR, f"{tag}_{k}{suf}.png"))
    print("baked", BAKE_DIR)


# ---------------------------------------------------------------- the table
seq = lambda ms: list(enumerate(ms))
# effect -> (frames, spot, frame times, big sheet, sheet tag)
FX = {
    "a_hit": (a_hit, HIT, [40, 50, 60, 70], False, "a_hit"),
    "qa_hit": (qa_hit, HIT, [40, 50, 60, 70], False, "qa_hit"),
    "q_hit": (q_hit, HIT, [40, 50, 60, 70, 80], False, "q_hit"),
    "eq_hit": (eq_hit, HIT, [40, 50, 60, 70], False, "eq_hit"),
    "e_hit": (e_hit, HIT, [40, 50, 60, 70], False, "e_hit"),
    # the storm's cuts come every r_per 7 ticks (117 ms): its hit runs 110 ms
    "r_hit": (r_hit, HIT, [20, 25, 30, 35], False, "r_hit"),
    "r_pull": (r_pull, HIT, [50, 60, 60, 70, 80], False, "r_pull"),
    "w_ally": (w_ally, (0, 0), [50, 60, 70, 80, 90], False, "w_ally"),
    "r_heal": (r_heal, (0, 0), [70, 80, 90, 110, 130], False, "r_heal"),
    # the spin tag q_spin 370 ms, its cut on tick 9 (150 ms) as the ring is brightest
    "eq_spin": (eq_spin, CORE, [50, 60, 70, 80, 110], True, "eq_spin"),
    # Apotheosis: 8 frames up to its burst on r_final 46 ticks (767 ms), the burst's 5 frames over the rest and on
    "r_spin": (r_spin, CORE, [95] * 7 + [100], True, "r_spin"),
    "r_burst": (r_burst, CORE, [50, 70, 80, 90, 110], True, "r_burst"),
    "q_on": (q_on, (0, 0), [120] * 4, False, "q_on"),
    "w_on": (w_on, (0, 0), [100] * 6, True, "w_on"),
    "w_ally_veil": (w_ally_veil, (0, 0), [100] * 6, True, "w_ally"),
}


def build():
    """{effect: [Pic]} with every frame mirrored."""
    return {name: [p.mirror() for p in fn()] for name, (fn, *_r) in FX.items()}


def check(pics):
    bad = []
    for name, ps in pics.items():
        for k, p in enumerate(ps):
            a = p.a
            if not (a == a[:, ::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric")
            al = a[..., 3]
            if al.any() and set(np.unique(al)) - {0, 255}:
                bad.append(f"{name} {k + 1} soft alpha")
            if not al.any():
                bad.append(f"{name} {k + 1} empty")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect at 6x and GIFs on her idle here")
    ap.add_argument("--drawn", action="store_true", help="really overwrite the sheets with these drawings")
    a = ap.parse_args()
    if not a.drawn:
        sys.exit("the sheets come from tools/art/import_nilah_fx.py; pass --drawn to write these drawings instead")
    pics = build()
    bad = check(pics)
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_nilah_fx": {}, "league_nilah_big": {}}
    for name, (_, spot, ms, big, tag) in FX.items():
        tables["league_nilah_big" if big else "league_nilah_fx"][tag] = [
            (p.frame(spot), float(t)) for p, t in zip(pics[name], ms)]
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    write_bake()
    if a.review:
        review(a.review, tables)


def review(out, tables):
    import tfm2_ase as T
    from PIL import ImageDraw
    os.makedirs(out, exist_ok=True)
    sp = T.load_sprite(os.path.join(MOD, "champions", "league_nilah"))
    idle = np.asarray(sp.frames[sp.tag_frames("idle")[0]].convert("RGBA"))
    Z = 6
    rows = []
    for sheet, tags in tables.items():
        for tag, frames in tags.items():
            W = max(f.shape[1] for f, _ in frames)
            H = max(max(f.shape[0] for f, _ in frames), idle.shape[0])
            cells = []
            gif = []
            for f, ms in frames:
                c = np.zeros((H, W if W > idle.shape[1] else idle.shape[1], 4), np.uint8)
                cw, ch = c.shape[1], c.shape[0]
                bg = Image.new("RGBA", (cw, ch), (92, 104, 70, 255))
                bg.alpha_composite(Image.fromarray(idle), ((cw - idle.shape[1]) // 2, (ch - idle.shape[0]) // 2))
                bg.alpha_composite(Image.fromarray(f), ((cw - f.shape[1]) // 2, (ch - f.shape[0]) // 2))
                big = bg.resize((cw * Z, ch * Z), Image.NEAREST)
                cells.append(big)
                gif.append((big, ms))
            strip = Image.new("RGB", (sum(c.width + 8 for c in cells) + 110, cells[0].height + 8), (24, 24, 30))
            d = ImageDraw.Draw(strip)
            d.text((4, 4), tag + (" (big)" if sheet.endswith("big") else ""), fill=(255, 255, 255))
            x = 110
            for c in cells:
                strip.paste(c.convert("RGB"), (x, 4))
                x += c.width + 8
            rows.append(strip)
            loops = 3
            gif[0][0].convert("RGB").save(os.path.join(out, f"nilah_fx_{sheet[13:]}_{tag}.gif"), save_all=True,
                                          append_images=[g.convert("RGB") for g, _ in gif[1:]] * 1 +
                                          [g.convert("RGB") for g, _ in gif] * (loops - 1),
                                          duration=[int(m) for _, m in gif] * loops, loop=0)
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height for r in rows)), (24, 24, 30))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(os.path.join(out, "nilah_fx_all.png"))
    print("review", out, sheet.size)


if __name__ == "__main__":
    main()
