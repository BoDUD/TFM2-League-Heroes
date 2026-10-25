#!/usr/bin/env python3
"""Rumble's effects redrawn where Gemini's pictures did not read at game size or did not look like League's (the user,
2026-10-25: 「注意R画的太小了 特效和英雄联盟不一样 你能改就帮我改改」; compared with Riot's ability videos
ability_0068_{Q,W,E,R,P}1 the same day), into assets/source/rumble/fx_fix/pixel_1x (+ manifest.json), which
import_rumble_fx.py reads before the Gemini delivery (fix_yorick_fx.py's way).

    python tools/art/fix_rumble_fx.py [--review DIR]

  r_fall    The Equalizer's landing, after League: a rocket diving nose first with its fire trail, a white star of a
            flash, the blast, then the rocket stuck in the ground amid dark cracks glowing red-hot, small flames and
            sparks flickering along them (frames 6-9 loop while the zone burns), the glow dying to embers. Drawn bigger
            than Gemini's (「R画的太小了」): the cracks 43 px across and the flames up to 13 px tall, the rocket left
            sticking out with its fins spread (League's wrecks along the line), so the six landings make one wide
            burning line.
  w_shield  Scrap Shield: League's is a tight cyan shell of shards round the mech, not Gemini's thin ring - a faceted
            dome round him, crystal facets on its shoulders (none over his head: the shell is drawn over him), glints
            running round it, a few scraps riding it.
  e_harpoon The harpoon: Gemini's came out as a blur at 16 x 8 - a steel harpoon with a barbed head, cyan arcs on the
            shaft, a spark trail (drawn going right, symmetric top to bottom).
  e_zap     The slowed one: League shows small blue-white arcs and sparkles round him, not Gemini's closed cage.
  a_hit     The ball's blow: Gemini's flash came out two squares wide - a star flash, steel shards and sparks.
  oh_on     Overheat: Gemini's frames 4-6 lay on painted grey panels that cannot be keyed off the smoke: its frame 3's
            fire turned to smoke, rising and thinning (frames 1-3 kept as processed).
Every picture symmetric left to right, the harpoon top to bottom; colours from the pack's ramps (pack_rumble_fx.py).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import process_rumble_fx as PR  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "rumble", "fx_fix")
GEM = os.path.join(ROOT, "assets", "source", "rumble", "gemini_fx", "rumble_fx")


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5)) + (255,)


W0, Y1, Y2, OR, RD, DR = map(hx, ("#FFFFFF", "#FFF4A8", "#FFCC3C", "#FF8A1C", "#E8441A", "#9C2010"))   # fire
S1, S2, S3, S4, S5 = map(hx, ("#D0C8C0", "#948C86", "#605A56", "#3A3634", "#1E1C1C"))                  # smoke
E0, E1, E2, E3, E4 = map(hx, ("#FFFFFF", "#CCF6FF", "#70DCFF", "#2C98F4", "#1A4CB8"))                  # electric
T1, T2, T3, T4 = map(hx, ("#E2E6EA", "#A0A8B0", "#646C74", "#3A4046"))                                 # steel
B1, B2, B3, B4 = map(hx, ("#FFF2C4", "#ECBE56", "#B47E2C", "#72501C"))                                 # brass
INK = S5                                                                                              # an object's outline


# ------------------------------------------------------------------------------------------------- drawing
def blank(w, h):
    return np.zeros((h, w, 4), np.uint8)


def put(c, x, y, col, over=True):
    x, y = int(round(x)), int(round(y))
    if 0 <= y < c.shape[0] and 0 <= x < c.shape[1] and (over or not c[y, x, 3]):
        c[y, x] = col


def line(c, x0, y0, x1, y1, col, over=True):
    x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        put(c, x0, y0, col, over)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(c, cx, cy, rx, ry, col, over=True):
    for y in range(c.shape[0]):
        for x in range(c.shape[1]):
            if ((x - cx) / max(rx, 0.01)) ** 2 + ((y - cy) / max(ry, 0.01)) ** 2 <= 1.0:
                put(c, x, y, col, over)


def stamp(c, rows, x0, y0, pal, over=True):
    """A small picture given as rows of characters (pal: character -> colour, '.' clear) with its top-left at (x0, y0)."""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != ".":
                put(c, x0 + i, y0 + j, pal[ch], over)


def mirror(c):
    """Left to right symmetric from the left half (the middle column of an odd width kept)."""
    w = c.shape[1]
    out = c.copy()
    out[:, w - w // 2:] = c[:, :w // 2][:, ::-1]
    return out


def mirror_tb(c):
    h = c.shape[0]
    out = c.copy()
    out[h - h // 2:] = c[:h // 2][::-1]
    return out


def outline(c, col=INK):
    """A 1-square outline round everything drawn (4-neighbours)."""
    op = c[..., 3] > 0
    ring = ndimage.binary_dilation(op, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)) & ~op
    out = c.copy()
    out[ring] = col
    return out


# ------------------------------------------------------------------------------------------------- the rocket
# nose down (The Equalizer's rockets fall nose first and stick in the ground); 7 wide with its outline, the fins spread
ROCKET = ["o.....o",
          "of...fo",
          ".ofmfo.",
          "..mLm..",
          "..mLm..",
          "..dLd..",
          "..dmd..",
          "..rRr..",
          "...r...",
          "...o..."]
RPAL = {"o": INK, "f": T3, "m": T2, "L": T1, "d": T3, "R": RD, "r": DR}
STUCK = 7                          # rows of the rocket left out of the ground when it is stuck (the fins and the tail)


def rocket(c, cx, top):
    stamp(c, ROCKET, cx - 3, top, RPAL)


def trail(c, cx, bottom, n):
    """The fire and smoke trail above a falling rocket's tail (bottom: the row just over the tail), n rows long."""
    for k in range(n):
        y = bottom - k
        f = k / max(n - 1, 1)
        if f < 0.18:
            cols, hw = (W0, Y1), 1
        elif f < 0.4:
            cols, hw = (Y1, Y2), 1
        elif f < 0.6:
            cols, hw = (Y2, OR), 1
        elif f < 0.75:
            cols, hw = (OR, RD), 1 if k % 2 else 0
        else:
            cols, hw = (S2, S3), 1 if k % 3 else 0
        put(c, cx, y, cols[0])
        for d in range(1, hw + 1):
            put(c, cx - d, y, cols[1])
            put(c, cx + d, y, cols[1])


# ------------------------------------------------------------------------------------------------- r_fall
RW, RH = 45, 62                    # the landing's cell (game px); the ground ellipse's middle 5 rows over its bottom
GX, GY = RW // 2, RH - 6           # the landing point
CRACKS = [(21, 0), (17, -4), (12, -6), (6, -6), (19, 4), (14, 5), (8, 6), (3, 5)]   # left half's crack ends from (GX, GY)


def cracks(c, glow, k):
    """Dark cracks radiating from the landing point in the ground's perspective (left half, mirrored later); `glow`
    0..1: how far out from the middle each crack glows red-hot; k: the flicker phase (one crack in three brightest)."""
    for i, (ex, ey) in enumerate(CRACKS):
        x1, y1 = GX - ex, GY + ey
        mx, my = GX - ex * 0.55 + (1 if i % 2 else -1) * 0.6, GY + ey * 0.55 + (0.6 if i % 3 == 0 else -0.4)
        line(c, GX - 2, GY, mx, my, S5)
        line(c, mx, my, x1, y1, S4)
        if glow > 0:
            n = 14
            for t in range(int(round(glow * n))):
                f = t / float(n)
                x = GX - 2 + (mx - GX + 2) * f * 1.7
                y = GY + (my - GY) * f * 1.7
                hot = (i + k) % 3 == 0
                col = (Y2 if t < 4 else OR) if hot else (OR if t < 4 else RD)
                if glow < 0.6:
                    col = RD if t < 3 else DR
                put(c, x, y, col)


def scorch(c, rx, ry, col=S4):
    disc(c, GX, GY, rx, ry, col)


def molten(c, k, size=1.0):
    """The ground red-hot round the rocket: a glowing pool (dark red rim, orange, a yellow core), its edge flickering."""
    disc(c, GX, GY, 15 * size, 4.4 * size, DR)
    disc(c, GX, GY, 11 * size, 3.4 * size, RD)
    disc(c, GX, GY, 7 * size, 2.3 * size, OR)
    if size >= 1:
        disc(c, GX, GY, 3.5, 1.2, Y2)
    for x in range(GX - 15, GX):
        if (x + k) % 4 == 0:
            put(c, x, GY - 4 * size, RD)


def stuck(c, glow):
    """The rocket stuck nose down in the ground: its tail and spread fins out of it, red-hot where it went in."""
    top = GY - STUCK
    stamp(c, ROCKET[:STUCK], GX - 3, top, RPAL)
    if glow:
        put(c, GX - 1, GY - 1, RD)
        put(c, GX, GY - 1, OR)
        put(c, GX + 1, GY - 1, RD)


def flame(c, x, y, h):
    """One flame standing on (x, y), h rows tall: a yellow root, orange, a red tip; 3 wide in its lower part, 5 wide at
    the root of a tall one."""
    for j in range(h):
        f = j / max(h - 1, 1)
        col = Y1 if f < 0.2 else (Y2 if f < 0.45 else (OR if f < 0.75 else RD))
        put(c, x, y - j, col)
        if f < 0.6:
            put(c, x - 1, y - j, OR if f < 0.3 else RD)
            put(c, x + 1, y - j, OR if f < 0.3 else RD)
        if h >= 9 and f < 0.25:
            put(c, x - 2, y - j, RD)
            put(c, x + 2, y - j, RD)


def flames(c, k, size):
    """Flames round the pool (left half), each a different height each frame k."""
    spots = [(GX - 5, GY - 1), (GX - 10, GY + 1), (GX - 15, GY), (GX - 19, GY + 2)]
    for i, (x, y) in enumerate(spots):
        h = [11, 8, 13, 9][(i + k) % 4] - 2 * i + size
        if h >= 2:
            flame(c, x, y, h)


def sparks(c, k, n=6):
    rng = np.random.default_rng(7 + k)
    for _ in range(n):
        x = GX - rng.integers(2, 20)
        y = GY - rng.integers(10, 24) - (k % 4) * 2
        put(c, x, y, rng.choice([Y2, OR, RD]))


def fireball(c, cx, cy, puffs):
    """A lumpy cloud of fire: puffs (dx, dy, r) round (cx, cy), each shaded dark red to a white core."""
    for shrink, col in ((0, DR), (1.2, RD), (2.6, OR), (3.8, Y2), (5.0, Y1), (6.2, W0)):
        for dx, dy, r in puffs:
            if r - shrink > 0.4:
                disc(c, cx + dx, cy + dy - shrink * 0.3, r - shrink, (r - shrink) * 0.85, col)


def smoke(c, cx, cy, puffs):
    for dx, dy, r in puffs:
        disc(c, cx + dx, cy + dy, r, r * 0.85, S4)
    for dx, dy, r in puffs:
        disc(c, cx + dx, cy + dy - 0.8, r - 1.0, (r - 1.0) * 0.85, S3)
    for dx, dy, r in puffs:
        disc(c, cx + dx - 0.6, cy + dy - 1.6, r - 2.4, (r - 2.4) * 0.85, S2)


def r_fall():
    fr = []
    # 1-2: the rocket diving nose first, its fire trail above it
    for nose in (24, 44):
        c = blank(RW, RH)
        top = nose - len(ROCKET) + 1
        trail(c, GX, top - 1, 17)
        rocket(c, GX, top)
        fr.append(c)
    # 3: the white star of the impact (League's spiky flash)
    c = blank(RW, RH)
    for (dx, dy, n) in [(1, 0, 21), (0, -1, 18), (1, -1, 12), (1, -0.45, 17), (0.45, -1, 15), (1, 0.35, 10)]:
        for t in range(n):
            put(c, GX - dx * t, GY - 4 + dy * t, W0 if t < n * 0.3 else (Y1 if t < n * 0.65 else Y2))
    disc(c, GX, GY - 4, 9, 5, Y1)
    disc(c, GX, GY - 4, 6, 3.4, W0)
    fr.append(c)
    # 4: the blast - a lumpy dome of fire, debris flying, the cracks opening
    c = blank(RW, RH)
    cracks(c, 1.0, 0)
    fireball(c, GX, GY - 9, [(0, 0, 12), (-8, -3, 8.5), (-4, -11, 8), (-13, 2, 6.5), (0, -14, 7)])
    for x, y in [(GX - 20, GY - 17), (GX - 15, GY - 26), (GX - 8, GY - 29), (GX - 21, GY - 7)]:
        stamp(c, ["dd", "Dd"], x, y, {"d": S4, "D": S5})
    fr.append(c)
    # 5: the fire falling back into the pool, smoke rising, the rocket showing
    c = blank(RW, RH)
    cracks(c, 1.0, 1)
    molten(c, 1)
    smoke(c, GX, GY - 21, [(0, -2, 6.5), (-8, 0, 5.5), (-4, -7, 5)])
    fireball(c, GX, GY - 6, [(0, 0, 8), (-7, 1, 6)])
    stuck(c, True)
    fr.append(c)
    # 6-9: burning - the rocket in the red-hot pool, the cracks glowing, flames and sparks flickering (a loop)
    for k in range(4):
        c = blank(RW, RH)
        cracks(c, 1.0, k)
        molten(c, k)
        flames(c, k, 0)
        stuck(c, True)
        sparks(c, k)
        fr.append(c)
    # 10-11: the fire dying: the glow fading, a wisp of smoke, then embers in the dark cracks
    c = blank(RW, RH)
    cracks(c, 0.5, 0)
    molten(c, 0, 0.6)
    flames(c, 1, -5)
    stuck(c, False)
    for j, (x, y) in enumerate([(GX - 1, GY - 11), (GX - 2, GY - 12), (GX - 2, GY - 13), (GX - 1, GY - 14),
                                (GX - 1, GY - 15)]):
        put(c, x, y, S2 if j < 2 else S3)
    fr.append(c)
    c = blank(RW, RH)
    cracks(c, 0.25, 1)
    scorch(c, 5, 1.5, S5)
    stuck(c, False)
    put(c, GX - 7, GY - 1, RD)
    put(c, GX - 12, GY, DR)
    fr.append(c)
    return [mirror(f) for f in fr]


# ------------------------------------------------------------------------------------------------- w_shield
SW, SH = 57, 43


def w_shield():
    """A faceted dome round him: a 14-sided shell, a band of crystal facets over its top, glints running round it, a few
    scraps riding it."""
    fr = []
    cx, cy, rx, ry = SW // 2, SH / 2 - 0.5, SW / 2 - 1.5, SH / 2 - 1.5
    n = 14
    outer = [(cx + rx * math.sin(2 * math.pi * i / n), cy - ry * math.cos(2 * math.pi * i / n)) for i in range(n)]
    inner = [(cx + (rx - 4) * math.sin(2 * math.pi * (i + 0.5) / n), cy - (ry - 3.5) * math.cos(2 * math.pi * (i + 0.5) / n))
             for i in range(n)]
    for k in range(4):
        c = blank(SW, SH)
        # the facets over the top (the upper band): each outer edge and the inner point between its corners
        for i in range(n):
            a, b = outer[i], outer[(i + 1) % n]
            p = inner[i]
            if p[1] < cy - 2 and abs(p[0] - cx) > 12:      # not over his head (the shell is drawn over him)
                line(c, a[0], a[1], p[0], p[1], E3)
                line(c, b[0], b[1], p[0], p[1], E3)
                q = inner[(i + 1) % n]
                if i % 2 == k % 2 and abs(q[0] - cx) > 12:
                    line(c, p[0], p[1], q[0], q[1], E4)
        # the shell's rim: bright on top, darker round the bottom
        for i in range(n):
            a, b = outer[i], outer[(i + 1) % n]
            col = E1 if min(a[1], b[1]) < cy - ry * 0.4 else (E2 if min(a[1], b[1]) < cy + ry * 0.4 else E3)
            line(c, a[0], a[1], b[0], b[1], col)
        # glints running round the rim (two, mirrored, a step on each frame)
        for g in (1 + k, 5 + k):
            a = outer[g % n]
            put(c, a[0], a[1], E0)
            put(c, a[0] - 1, a[1], E0)
            put(c, a[0], a[1] - 1, E1)
        # scraps riding the shell: brass plates and steel nuts at the sides, bobbing
        bob = [0, -1, 0, 1][k]
        for (x, y, kind) in [(3, 16 + bob, "plate"), (2, 26 - bob, "nut"), (6, 34 + bob, "plate")]:
            if kind == "plate":
                stamp(c, ["oo", "bB"], x, y, {"o": B3, "b": B4, "B": B2})
            else:
                stamp(c, ["mL", "dm"], x, y, {"m": T2, "L": T1, "d": T3})
        fr.append(mirror(c))
    return fr


# ------------------------------------------------------------------------------------------------- e_harpoon
HW_, HH_ = 17, 9


# the upper half (rows 0-4, row 4 the middle; mirrored below): a spark trail, the brass collar, the steel shaft, the
# barbed head with its tip on the right
HARPOON_TOP = [".................",
               ".................",
               ".........ko......",
               "...b......kTLk...",
               "eE.BmLmmLmmLLLLTk"]
HPAL = {"e": E1, "E": E2, "b": B3, "B": B2, "m": T2, "L": T1, "T": T2, "k": T4, "o": T3}
# cyan arcs jumping along the shaft (row, column) per frame, upper half
ARCS = [[(3, 5), (2, 6), (3, 7)], [(3, 7), (2, 8), (3, 9)], [(3, 4), (2, 5), (2, 6), (3, 8)], [(2, 6), (3, 7), (2, 8)]]


def e_harpoon():
    """The harpoon flying right: a steel shaft, a barbed head, a brass collar, cyan arcs on the shaft, a spark trail."""
    fr = []
    for k in range(4):
        c = blank(HW_, HH_)
        stamp(c, HARPOON_TOP, 0, 0, HPAL)
        for j, (y, x) in enumerate(ARCS[k]):
            put(c, x, y, E1 if j == 1 else E2)
        put(c, 1 + k % 2, 3, E3)                  # a spark peeling off the trail
        fr.append(mirror_tb(c))
    return fr


# ------------------------------------------------------------------------------------------------- e_zap
ZW, ZH = 21, 31


def e_zap():
    """Blue-white arcs flickering up his sides and sparkles round him (the body's 16 middle columns left empty)."""
    fr = []
    spans = [(6, 13), (15, 23), (9, 17), (19, 27)]
    for k in range(4):
        c = blank(ZW, ZH)
        y0, y1 = spans[k]
        x = 1 + (k % 2)
        for y in range(y0, y1 + 1):
            put(c, x, y, E2)
            if (y - y0) % 3 == 1:
                x = 2 - (x - 1) if x in (1, 2) else 1
                put(c, x, y, E1)
        put(c, 1, y0 - 1, E0)
        put(c, 2, y1 + 1, E3)
        # sparkles: one bright, one dim, drifting up a row each frame
        for (sx, sy, col) in [(3, 22 - 2 * k, E0), (1, 8 + (k * 5) % 12, E1), (4, 3 + k, E3)]:
            put(c, sx, sy, col)
        fr.append(mirror(c))
    return fr


# ------------------------------------------------------------------------------------------------- a_hit
AW = 13


def a_hit():
    fr = []
    c0 = AW // 2
    c = blank(AW, AW)                         # 1: the star flash
    for t in range(4):
        col = W0 if t < 2 else Y1
        for dx, dy in ((t, 0), (-t, 0), (0, t), (0, -t)):
            put(c, c0 + dx, c0 + dy, col)
    for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        put(c, c0 + dx, c0 + dy, Y1)
        put(c, c0 + 2 * dx, c0 + 2 * dy, Y2)
    fr.append(c)
    c = blank(AW, AW)                         # 2: the burst - sparks out, steel shards flying
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        for r, col in ((3, Y1), (4, Y2), (5, OR)):
            put(c, c0 + r * math.cos(a), c0 + r * math.sin(a), col)
    for dx, dy in ((4, -4), (-4, -4), (5, 2), (-5, 2)):
        put(c, c0 + dx, c0 + dy, T2)
        put(c, c0 + dx + (1 if dx > 0 else -1), c0 + dy, T3)
    put(c, c0, c0, Y1)
    fr.append(mirror(c))
    c = blank(AW, AW)                         # 3: the sparks fading out
    for ang in range(22, 360, 45):
        a = math.radians(ang)
        put(c, c0 + 5.5 * math.cos(a), c0 + 5.5 * math.sin(a), RD if ang % 90 else OR)
    for dx, dy in ((5, -5), (-5, -5)):
        put(c, c0 + dx, c0 + dy, T3)
    fr.append(mirror(c))
    return [mirror(f) for f in fr]


# ------------------------------------------------------------------------------------------------- oh_on
def oh_on():
    """Gemini's frames 1-3 as processed; 4-6 its frame 3 turned to smoke, rising and thinning."""
    man = {e["name"]: e for e in json.load(open(PR.lp(os.path.join(GEM, "manifest.json")), encoding="utf-8"))["effects"]}
    e = man["oh_on"]
    a = np.asarray(Image.open(PR.lp(os.path.join(GEM, "pixel_1x", e["file"]))).convert("RGBA"))
    w, h = e["cell_1x"]
    cs = [a[:, k * w:(k + 1) * w].copy() for k in range(e["frames"])]
    f3 = cs[2]
    op = f3[..., 3] > 0
    lum = f3[..., :3].astype(int).mean(-1)
    sat = f3[..., :3].astype(int).max(-1) - f3[..., :3].astype(int).min(-1)
    fire = op & (sat > 60)
    out = cs[:3]
    for step, (rise, erode, cols) in enumerate([(2, 0, (S4, S3, S2)), (5, 1, (S4, S3, S2)), (8, 2, (S3, S2, S1))]):
        m = op.copy()
        for _ in range(erode):
            m = ndimage.binary_erosion(m, np.ones((3, 3), bool)) | (ndimage.binary_erosion(m, np.ones((1, 3), bool)) &
                                                                     (np.indices(m.shape)[0] % 2 == 0))
        c = np.zeros_like(f3)
        shade = np.where(lum > 190, 2, np.where(lum > 120, 1, 0))
        for i, col in enumerate(cols):
            c[m & (shade == i)] = col
        c = np.roll(c, -rise, axis=0)
        c[h - rise:] = 0
        # embers: the brightest fire squares left as sparks, fewer each step
        ys, xs = np.nonzero(fire & (lum > 200))
        for j in range(0, len(ys), 5 + 4 * step):
            put(c, xs[j], ys[j] - rise - step, OR if step < 2 else RD)
        c[..., 3] = np.where(c[..., 3] > 0, 255, 0)
        out.append(PR.S.PP.symmetric(c))
    return out


DRAWN = {"r_fall": r_fall, "w_shield": w_shield, "e_harpoon": e_harpoon, "e_zap": e_zap, "a_hit": a_hit, "oh_on": oh_on}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--only")
    a = ap.parse_args()
    os.makedirs(PR.lp(os.path.join(OUT, "pixel_1x")), exist_ok=True)
    names = a.only.split(",") if a.only else list(DRAWN)
    man_path = os.path.join(OUT, "manifest.json")
    old = {}
    if os.path.isfile(PR.lp(man_path)):
        old = {e["name"]: e for e in json.load(open(PR.lp(man_path), encoding="utf-8"))["effects"]}
    sheets = []
    for name in names:
        cells = DRAWN[name]()
        h, w = cells[0].shape[:2]
        for k, c in enumerate(cells):
            m = c[::-1] if name in PR.FLYING else c[:, ::-1]
            if not (c == m).all():
                sys.exit(f"{name} frame {k + 1}: not symmetric")
        strip = np.concatenate(cells, axis=1)
        Image.fromarray(strip).save(PR.lp(os.path.join(OUT, "pixel_1x", f"rumble_fx_{name}.png")))
        old[name] = {"name": name, "file": f"rumble_fx_{name}.png", "frames": len(cells), "cell_1x": [w, h],
                     "symmetry": "top-bottom" if name in PR.FLYING else "left-right",
                     "source": "drawn by tools/art/fix_rumble_fx.py" + (" (frames 1-3 Gemini's)" if name == "oh_on" else "")}
        sheets.append((name, strip, w))
        print(f"{name}: {len(cells)} frames of {w}x{h}")
    with open(PR.lp(man_path), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"effects": [old[k] for k in DRAWN if k in old]}, f, ensure_ascii=False, indent=1)
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        path = os.path.join(a.review, "rumble_fx_fixed.png")
        print(path, PR.review_sheet(sheets, path, Z=6))


if __name__ == "__main__":
    main()
