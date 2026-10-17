#!/usr/bin/env python3
"""Mordekaiser's Obliterate (Q) drawn at game size: the user, 2026-10-13: 「铁男1技能的特效感觉也不足」.

    python tools/art/fx_mordekaiser_q.py [--review out.png]     (tools/art/import_mordekaiser.py calls frames())

Codex's Q pictures were small for him (the slam 11-27 px at his feet, the crack a 45 x 10 px band, the hits 5-19 px)
and the crack, a line picture turned with the cast, sat 11 px under its pivot: turned half round on the red side it
floated above the line. League's Obliterate is a heavy blow: the mace comes down at the end of the line and the
ground there erupts. So every picture now stands upright on a point and is never turned (tools/kit/build_mordekaiser.py
stamps them with hidden projectiles, league_yasuo Q3's way):
  q_slam   where the mace head lands (40 px ahead: his slam frame): a flash, five soul spikes shooting out of the
           ground, a shock ring, cracks running out, iron shards thrown up and falling, dust - 48 x 46 px, 520 ms
  q_burst  three smaller eruptions back along the line toward him (32, 22, 12 px ahead, a tick apart) - 26 x 28 px
  q_hit    on every enemy hit: a soul star and its ring, 26 px
  q_iso_hit on the one enemy alone (the isolation bonus): a bigger star with a pillar of soul through it, 36 px
In his effects' own ramps (pack_mordekaiser_fx.py: SOUL white -> cyan -> teal, IRON, DARK smoke), no outline (VFX
spec), every picture left-right symmetric (an effect on a point is never mirrored for the red side). Spots are game
px from the pivot; the ground under a point is 11 px below it.
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


def hexes(*hs):
    return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in hs]


SOUL = hexes("#FFFFFF", "#D8FFF8", "#7CFFEE", "#22E0D0", "#0E9C98", "#0A5A5C")
IRON = hexes("#E0E6F0", "#A8B0C0", "#6E7688", "#3E4452")
DUST = hexes("#B8AC94", "#8A7E6A")      # (pack_mordekaiser_fx.py DUST, its middle two)
GROUND = 11                      # the ground row under a point
FLAT = 0.32                      # a ground circle seen from the camera: y radius / x radius
HIT = -14                        # a hit on a unit's upper body


class Pic:
    """A drawing round a pivot (x right, y down, game px); `put` keeps the first colour unless `over`."""

    def __init__(self, half_w, up, down):
        self.cx, self.cy = half_w, up
        self.a = np.zeros((up + down + 1, 2 * half_w + 1, 4), np.uint8)

    def put(self, x, y, c, over=True):
        i, j = int(round(y)) + self.cy, int(round(x)) + self.cx
        if 0 <= i < self.a.shape[0] and 0 <= j < self.a.shape[1]:
            if over or self.a[i, j, 3] == 0:
                self.a[i, j, :3] = c
                self.a[i, j, 3] = 255

    def put2(self, x, y, c, over=True):
        """x and its mirror -x."""
        self.put(x, y, c, over)
        self.put(-x, y, c, over)

    def frame(self):
        """Left-right symmetric (the left half copied onto the right where the right is empty and the other way),
        trimmed round the pivot."""
        a = self.a
        m = a[:, ::-1]
        a = np.where((a[..., 3:] == 0) & (m[..., 3:] > 0), m, a)
        return G.centre_frame(a, -self.cx, -self.cy)


def ring(p, r, cols, gy=GROUND, flat=FLAT, front_only=False, gaps=0.0, rng=None, jag=0.0, thick=1):
    """A shock ring on the ground: the near half in cols[0], the far half in cols[1] (or none); jag: its edge
    ragged by up to that many px, gaps: the share of it broken away (in runs, not single pixels)."""
    n = max(24, int(r * 8))
    noise = np.zeros(n)
    if jag and rng is not None:
        noise = np.convolve(rng.uniform(-jag, jag, n + 6), np.ones(5) / 5, "same")[3:n + 3]
    hole = np.zeros(n, bool)
    if gaps and rng is not None:
        k = 0
        while k < n:
            run = int(rng.integers(2, 6))
            hole[k:k + run] = rng.random() < gaps
            k += run
    for k in range(n):
        if hole[k]:
            continue
        t = np.pi * k / n          # 0..pi: the near (lower) half; the far half mirrored up
        for d in range(thick):
            rr = r + noise[k] - d
            x, y = rr * np.cos(t), gy + rr * flat * np.sin(t)
            p.put2(x, y, cols[min(d, len(cols) - 1)] if front_only else cols[0])
            if not front_only and len(cols) > 1:
                p.put2(x, gy - rr * flat * np.sin(t), cols[1], over=False)


def disc(p, r, cols, cx=0.0, cy=0.0, flat=1.0, over=True):
    """A filled ellipse shaded from its middle (cols[0]) to its edge (cols[-1])."""
    ri = int(np.ceil(r))
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            d = np.hypot(dx, dy / flat) / max(r, 1e-6)
            if d <= 1.0:
                c = cols[min(len(cols) - 1, int(d * len(cols)))]
                p.put2(cx + dx, cy + dy, c, over)


def star(p, r, cols, cy=0.0, rays=8, width=1.0, lean=0.0):
    """Rays from a point: each a line thinning outward, coloured by its distance (cols inner -> outer)."""
    for k in range(rays):
        t = 2 * np.pi * k / rays + lean
        reach = r * (1.0 if k % 2 == 0 else 0.6)
        for s in np.linspace(0, reach, int(reach * 3) + 2):
            c = cols[min(len(cols) - 1, int(s / max(reach, 1e-6) * len(cols)))]
            w = width * (1 - s / max(reach, 1e-6))
            x, y = s * np.cos(t), cy + s * np.sin(t)
            p.put2(x, y, c)
            if w > 0.5:
                p.put2(x + 0.5 * -np.sin(t), y + 0.5 * np.cos(t), c, over=False)


def spike(p, x0, height, lean, base, cols, gy=GROUND, broken=0.0, rng=None):
    """A soul spike shooting out of the ground at x0: base px wide at the ground, a sharp tip `height` up, leaning
    `lean` px sideways at the tip; shaded across (white middle line, cyan, teal edges). broken: the share of its
    upper part already gone."""
    top = int(height)
    for i in range(top + 1):
        u = i / max(height, 1)
        if broken and u > 1 - broken:
            if rng is not None and rng.random() < 0.25:
                p.put2(x0 + lean * u + rng.uniform(-2, 2), gy - i, cols[3])
            continue
        hw = base / 2 * (1 - u) ** 1.2
        xc = x0 + lean * u
        for dx in np.arange(-hw - 0.5, hw + 0.51, 0.5):
            f = abs(dx) / max(hw + 0.5, 0.5)
            k = 0 if f < 0.25 else 1 if f < 0.5 else 2 if f < 0.8 else 3
            if u > 0.85:
                k = min(k, 1)         # the tip burns white
            p.put2(xc + dx, gy - i, cols[k])


def crack(p, angle, length, cols, rng, gy=GROUND, grown=1.0):
    """A glowing crack running out on the ground: a jagged 1-px line (cols[0] near the middle, cols[1] out), its
    rim one shade darker where the ground is still clear."""
    x, y, t = 0.0, 0.0, angle
    steps = int(length * grown)
    pts = []
    for s in range(steps):
        t += rng.uniform(-0.35, 0.35)
        x += np.cos(t)
        y += np.sin(t) * FLAT * 1.6
        pts.append((x, y, s / max(length, 1)))
    for x, y, f in pts:
        c = cols[0] if f < 0.45 else cols[1]
        p.put2(x, gy + y, c)
    for x, y, f in pts:
        p.put2(x, gy + y - 1, cols[2], over=False)
        p.put2(x, gy + y + 1, cols[2], over=False)


def shard(p, x, y, c):
    """An iron fragment: a 2 x 2 chip with its light corner."""
    p.put2(x, y, c[0])
    p.put2(x + 1, y, c[1])
    p.put2(x, y + 1, c[1])
    p.put2(x + 1, y + 1, c[2])


def dust(p, x, y, r, cols, rng, fill=0.75):
    """A dirt cloud kicked up: a speckled half ellipse on the ground, lighter on top."""
    for dy in range(-int(r), 1):
        for dx in range(-int(r * 1.3), int(r * 1.3) + 1):
            if (dx / 1.3) ** 2 + (dy * 1.4) ** 2 <= r * r and rng.random() < fill:
                p.put2(x + dx, y + dy, cols[0] if dy < -r / 2.5 else cols[1], over=False)


def throws(rng, n, speed, spread, up=1.0):
    """n shards / sparks thrown up and outward from the ground, one side (put2 mirrors them)."""
    out = []
    for _ in range(n):
        a = np.radians(rng.uniform(25, 25 + spread))
        v = rng.uniform(0.6, 1.0) * speed
        out.append((v * np.cos(a), -v * np.sin(a) * up, rng.uniform(1, 6)))
    return out


def fly(p, parts, t, c, gy=GROUND, g=0.55, sparks=False):
    for vx, vy, x0 in parts:
        x, y = x0 + vx * t, gy - 2 + vy * t + g * t * t
        if y > gy:
            continue
        if sparks:
            p.put2(x, y, c[0])
        else:
            shard(p, x, y, c)


# ---------------------------------------------------------------------------------------------------------- q_slam
SLAM_MS = [40, 50, 60, 60, 70, 70, 80, 90]
# the five spikes: (x at the ground, height, lean at the tip, base width) - put2 mirrors the two side pairs
SPIKES = [(0, 34, 0, 9), (5, 26, 7, 7), (10, 17, 11, 6)]


def q_slam():
    rng = np.random.default_rng(7)
    shards = throws(rng, 5, 3.4, 50)
    sparks = throws(rng, 6, 4.4, 60)
    cracks = [(np.radians(a), L, np.random.default_rng(s)) for a, L, s in ((8, 22, 1), (-12, 19, 2), (30, 15, 3),
                                                                           (-35, 13, 4), (60, 9, 5))]
    out = []
    for f, ms in enumerate(SLAM_MS):
        p = Pic(26, 38, 16)
        grow = [0.3, 0.75, 1, 1, 1, 1, 1, 1][f]
        warm = [SOUL[1], SOUL[2], SOUL[4]] if f < 5 else [SOUL[3], SOUL[4], SOUL[5]] if f < 7 else \
            [SOUL[4], SOUL[5], SOUL[5]]
        if f >= 1:                                   # the cracks under everything
            for t, L, r in cracks:
                crack(p, t, L, warm, np.random.default_rng(int(L * 7)), grown=grow)
        if f == 0:
            disc(p, 7, [SOUL[0], SOUL[1], SOUL[2]], cy=GROUND - 2, flat=0.55)
            star(p, 9, [SOUL[0], SOUL[1], SOUL[2]], cy=GROUND - 4, rays=8, width=1.4)
        if f in (1, 2, 3, 4):                         # the shock ring, out and fading
            r = [0, 13, 19, 24, 27][f]
            cols = [[SOUL[0], SOUL[2]], [SOUL[1], SOUL[3]], [SOUL[3], SOUL[4]], [SOUL[4], SOUL[5]]][f - 1]
            ring(p, r, cols, gaps=0.0 if f < 4 else 0.35, rng=rng)
        if f == 1:                                    # the blow's dome
            disc(p, 13, [SOUL[0], SOUL[0], SOUL[1], SOUL[2], SOUL[3]], cy=GROUND - 1, flat=0.8)
        if f in (1, 2, 3, 4, 5):                      # the spikes: up, held, breaking
            h = [0, 0.55, 1.0, 1.0, 0.9, 0.55][f]
            brk = [0, 0, 0, 0.15, 0.45, 0.7][f]
            cols = [SOUL[0], SOUL[1], SOUL[2], SOUL[3]] if f < 4 else [SOUL[2], SOUL[3], SOUL[4], SOUL[5]]
            for x0, height, lean, base in SPIKES:
                spike(p, x0, height * h, lean * h, base, cols, broken=brk, rng=rng)
        if f >= 2:                                    # iron thrown up and falling, sparks
            fly(p, shards, (f - 1) * 3.2, IRON)
            if f <= 5:
                fly(p, sparks, (f - 1) * 3.0, [SOUL[1] if f < 4 else SOUL[3]], sparks=True)
        if f >= 2:                                    # dust at the foot of it
            r = [0, 0, 4, 5.5, 6.5, 7, 7, 6][f]
            fill = [0, 0, 0.8, 0.75, 0.6, 0.45, 0.3, 0.15][f]
            for x in (12, 19):
                dust(p, x, GROUND, r * (1 if x == 12 else 0.8), DUST, np.random.default_rng(f * 10 + x), fill * 0.7)
        if f >= 5:                                    # embers rising off the cracks
            for k in range(4):
                p.put2(3 + 5 * k, GROUND - (f - 4) * 3 - k * 2, SOUL[2] if f < 7 else SOUL[4])
        out.append((p.frame(), ms))
    return out


# ---------------------------------------------------------------------------------------------------------- q_burst
BURST_MS = [40, 50, 60, 60, 70, 70, 80]


def q_burst():
    rng = np.random.default_rng(11)
    shards = throws(rng, 3, 2.4, 50)
    cr = [(np.radians(a), L) for a, L in ((10, 11), (-20, 9), (45, 6))]
    out = []
    for f, ms in enumerate(BURST_MS):
        p = Pic(14, 30, 14)
        warm = [SOUL[1], SOUL[2], SOUL[4]] if f < 4 else [SOUL[3], SOUL[4], SOUL[5]]
        for t, L in cr:
            crack(p, t, L, warm, np.random.default_rng(int(L * 13)), grown=[0.5, 1, 1, 1, 1, 1, 1][f])
        if f == 0:
            star(p, 6, [SOUL[0], SOUL[1], SOUL[2]], cy=GROUND - 2, rays=6, width=1.0)
        h = [0, 0.6, 1.0, 1.0, 0.8, 0.0, 0.0][f]
        if h:
            brk = [0, 0, 0, 0.2, 0.55, 0, 0][f]
            cols = [SOUL[0], SOUL[1], SOUL[2], SOUL[3]] if f < 3 else [SOUL[1], SOUL[2], SOUL[3], SOUL[4]]
            for x0, height, lean, base in ((0, 22, 0, 6), (4, 15, 5, 5)):
                spike(p, x0, height * h, lean * h, base, cols, broken=brk, rng=rng)
        if f in (1, 2):
            ring(p, [0, 8, 12][f], [SOUL[2], SOUL[4]] if f == 1 else [SOUL[3], SOUL[5]])
        if f >= 2:
            fly(p, shards, (f - 1) * 3.0, IRON)
            dust(p, 9, GROUND, [0, 0, 3, 4, 4.5, 4.5, 4][f], DUST, np.random.default_rng(f), [0, 0, .55, .5, .35, .2, .1][f])
        if f >= 4:
            for k in range(3):
                p.put2(2 + 4 * k, GROUND - (f - 3) * 3 - k, SOUL[2] if f < 6 else SOUL[4])
        out.append((p.frame(), ms))
    return out


# ---------------------------------------------------------------------------------------------------------- hits
HIT_MS = [40, 50, 60, 70, 70]
ISO_MS = [40, 50, 60, 70, 70, 80]


def q_hit():
    rng = np.random.default_rng(23)
    sparks = [(np.cos(a) * v, np.sin(a) * v) for a, v in zip(rng.uniform(-np.pi, 0, 5), rng.uniform(2.5, 3.5, 5))]
    out = []
    for f, ms in enumerate(HIT_MS):
        p = Pic(15, 15 - HIT, 15 + HIT)
        if f == 0:
            star(p, 6, [SOUL[0], SOUL[1]], cy=HIT, rays=4, width=1.2)
            disc(p, 2.5, [SOUL[0]], cy=HIT)
        if f == 1:
            star(p, 12, [SOUL[0], SOUL[1], SOUL[2], SOUL[3]], cy=HIT, rays=8, width=1.6, lean=np.pi / 8)
            disc(p, 4, [SOUL[0], SOUL[1]], cy=HIT)
        if f in (2, 3):
            star(p, [0, 0, 10, 7][f], [SOUL[1], SOUL[2], SOUL[3]] if f == 2 else [SOUL[3], SOUL[4]], cy=HIT, rays=8,
                 width=1.2, lean=np.pi / 8)
            for fl in (1.0, -1.0):                    # round it, both halves (a burst, not a ring on the ground)
                ring(p, [0, 0, 8, 11][f], [SOUL[2] if f == 2 else SOUL[4]], gy=HIT, flat=fl, gaps=0.45, rng=rng,
                     jag=1.2, front_only=True)
        if f >= 2:
            for k, (vx, vy) in enumerate(sparks):
                t = f * 2.6
                if k % 2:
                    shard(p, vx * t * 0.8, HIT + vy * t * 0.8 + 0.06 * t * t, IRON)
                else:
                    p.put2(vx * t, HIT + vy * t, SOUL[1] if f < 4 else SOUL[3])
        out.append((p.frame(), ms))
    return out


def q_iso_hit():
    rng = np.random.default_rng(31)
    sparks = [(np.cos(a) * v, np.sin(a) * v) for a, v in zip(rng.uniform(-np.pi, 0.4, 7), rng.uniform(2.5, 4.0, 7))]
    out = []
    for f, ms in enumerate(ISO_MS):
        p = Pic(20, 30 - HIT, 20 + HIT)
        if f == 0:
            star(p, 8, [SOUL[0], SOUL[1]], cy=HIT, rays=4, width=1.6)
            disc(p, 3.5, [SOUL[0]], cy=HIT)
        if f in (1, 2, 3):                            # the pillar of soul through the target
            h = [0, 1.0, 0.85, 0.5][f]
            cols = [SOUL[0], SOUL[1], SOUL[2], SOUL[3]] if f < 3 else [SOUL[2], SOUL[3], SOUL[4], SOUL[5]]
            spike(p, 0, 30 * h, 0, 7, cols, gy=HIT + 14)
            spike(p, 0, 10 * h, 0, 5, cols, gy=HIT + 14)
        if f == 1:
            star(p, 16, [SOUL[0], SOUL[1], SOUL[2], SOUL[3]], cy=HIT, rays=8, width=2.0, lean=np.pi / 8)
            disc(p, 6, [SOUL[0], SOUL[0], SOUL[1]], cy=HIT)
        if f in (2, 3, 4):
            r = [0, 0, 11, 15, 17][f]
            cols = [[SOUL[1], SOUL[2]], [SOUL[2], SOUL[3]], [SOUL[4], SOUL[5]]][f - 2]
            ring(p, r, cols, gy=HIT, flat=1.0, gaps=[0, 0, 0.15, 0.35, 0.6][f], rng=rng, jag=1.5, thick=2,
                 front_only=True)
            ring(p, r, cols, gy=HIT, flat=-1.0, gaps=[0, 0, 0.15, 0.35, 0.6][f], rng=rng, jag=1.5, thick=2,
                 front_only=True)
        if f >= 2:
            for k, (vx, vy) in enumerate(sparks):
                t = f * 2.4
                if k % 2:
                    shard(p, vx * t * 0.8, HIT + vy * t * 0.8 + 0.06 * t * t, IRON)
                else:
                    p.put2(vx * t, HIT + vy * t, SOUL[1] if f < 4 else SOUL[3])
        out.append((p.frame(), ms))
    return out


def frames():
    """{tag: [(frame centred on its pivot, ms)]} - the sheet each goes in: tools/art/import_mordekaiser.py BIG."""
    return {"q_slam": q_slam(), "q_burst": q_burst(), "q_hit": q_hit(), "q_iso_hit": q_iso_hit()}


def review(path, Z=6):
    from PIL import ImageDraw
    rows = []
    for tag, fr in frames().items():
        ims = [Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST) for a, _ in fr]
        H = max(i.height for i in ims) + 20
        W = sum(i.width + 8 for i in ims) + 90
        img = Image.new("RGB", (W, H), (88, 104, 88))
        d = ImageDraw.Draw(img)
        d.text((4, 4), tag, fill=(255, 255, 255))
        x = 90
        for i, (a, ms) in zip(ims, fr):
            img.paste(i, (x, H - i.height), i)
            d.text((x, 2), f"{ms}", fill=(255, 255, 0))
            x += i.width + 8
        rows.append(img)
    W = max(r.width for r in rows)
    can = Image.new("RGB", (W, sum(r.height for r in rows)), (40, 40, 40))
    y = 0
    for r in rows:
        can.paste(r, (0, y))
        y += r.height
    can.save(path)
    return can.size


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="every frame at 6x here")
    a = ap.parse_args()
    for tag, fr in frames().items():
        print(tag, len(fr), "frames", sum(m for _, m in fr), "ms", "max", max(f.shape[1] for f, _ in fr), "x",
              max(f.shape[0] for f, _ in fr))
    if a.review:
        print(review(a.review))
