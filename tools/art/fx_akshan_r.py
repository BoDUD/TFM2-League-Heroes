#!/usr/bin/env python3
"""Akshan's Comeuppance (R) drawn at game size: a player, 2026-10-23: the R "has no effect and no damage"; the user:
「应该是瞄准的时候没特效 导致玩家感觉没伤害」 - nothing showed while he aimed, and Codex's bullet (13 x 5 px) and hit
(17 px) read like his attack's (9 x 3 px shot).

    python tools/art/fx_akshan_r.py [--review out.png]     (tools/art/import_akshan_fx.py calls frames())

  r_bullet  the bullet in flight, drawn pointing right (the game turns it): a white-hot head in a red-gold glow and a
            tapering red trail behind it - 29 x 9 px, 3 frames looped (the trail flickers)
  r_hit     on the unit hit, at its upper body: a white flash, eight red-gold rays, a red ring thrown out - 31 px,
            5 frames, 300 ms
  r_sight   the lock on the champion while he channels (a buff picture following it): a red ring with four ticks
            pointing in and a white dot, breathing in and out - 29 px, 4 frames looped
In his Comeuppance ramps (tools/art/pack_akshan_fx.py RED and GOLD), no outline (VFX spec), every picture left-right
symmetric except the bullet. Spots are game px from the unit's pivot; a hit lands 14 px over it (import_akshan_fx HIT).
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


RED = hexes("#FFFFFF", "#FFD0C0", "#FF7A5A", "#E8341C", "#A8160E", "#600A08")
GOLD = hexes("#FFFFFF", "#FFF4C8", "#FFD36A", "#FFA62B", "#E2681A", "#9C3A12")
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

    def frame(self, sym=True):
        """Trimmed round the pivot; with sym the left half copied onto the right where the right is empty and back."""
        a = self.a
        if sym:
            m = a[:, ::-1]
            a = np.where((a[..., 3:] == 0) & (m[..., 3:] > 0), m, a)
        return G.centre_frame(a, -self.cx, -self.cy)


def disc(p, r, cols, cx=0.0, cy=0.0, flat=1.0, over=True, mirror=True):
    """A filled ellipse shaded from its middle (cols[0]) to its edge (cols[-1])."""
    ri = int(np.ceil(r))
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            d = np.hypot(dx, dy / flat) / max(r, 1e-6)
            if d <= 1.0:
                c = cols[min(len(cols) - 1, int(d * len(cols)))]
                (p.put2 if mirror else p.put)(cx + dx, cy + dy, c, over)


def circle(p, r, c, cy=0.0, gaps=(), over=True):
    """A one-pixel ring; gaps: angle ranges (radians) left open."""
    n = max(24, int(r * 8))
    for k in range(n):
        t = 2 * np.pi * k / n
        if any(a <= t < b for a, b in gaps):
            continue
        p.put(r * np.cos(t), cy + r * np.sin(t), c, over)


def rays(p, r0, r1, cols, cy=0.0, n=8, lean=0.0, short=0.6):
    """Rays from r0 out to r1 (every other one shorter), coloured inner -> outer."""
    for k in range(n):
        t = 2 * np.pi * k / n + lean
        reach = r1 if k % 2 == 0 else r0 + (r1 - r0) * short
        for s in np.linspace(r0, reach, int((reach - r0) * 3) + 2):
            c = cols[min(len(cols) - 1, int((s - r0) / max(reach - r0, 1e-6) * len(cols)))]
            p.put2(s * np.cos(t), cy + s * np.sin(t), c)


# ------------------------------------------------------------------ the bullet
def r_bullet():
    out = []
    for f in range(3):
        p = Pic(15, 5, 5)
        # the trail behind the head (x < 0): two tapering bands, red outside, gold inside, flickering per frame
        for x in range(-14, 6):
            u = (x + 14) / 20                     # 0 at the tail's end, 1 at the head
            half = 0.6 + 2.4 * u ** 1.5
            if x < -14 + (2 - f) * 2 and (x + f) % 3 == 0:
                continue                          # the far end breaks up, a little differently each frame
            for dy in np.arange(-half, half + 0.01, 0.5):
                g = abs(dy) / max(half, 0.5)
                cols = GOLD if g < 0.45 else RED
                k = 2 + int(g * 3) - int(u * 2)
                p.put(x, dy, cols[max(1, min(len(cols) - 1, k))], over=False)
        # the head: a white-hot slug in a gold glow, a red rim
        disc(p, 4.2, [RED[3]], cx=8, flat=0.75, mirror=False)
        disc(p, 3.4, [GOLD[2]], cx=8.5, flat=0.75, mirror=False)
        disc(p, 2.3, [GOLD[0], GOLD[1]], cx=9, flat=0.7, mirror=False)
        p.put(12, 0, RED[2])
        p.put(13, 0, RED[3] if f == 1 else RED[2])
        out.append((p.frame(sym=False), 60))
    return out


# ------------------------------------------------------------------ the hit
def r_hit():
    out = []
    # (flash radius, ray reach, ring radius, ms)
    for k, (fl, ry, rg, ms) in enumerate([(5, 9, 0, 40), (6, 14, 8, 50), (4, 15, 12, 60), (2, 13, 15, 70), (0, 0, 15, 80)]):
        p = Pic(17, 32, 4)
        if rg:
            circle(p, rg, RED[3] if k < 3 else RED[4], cy=HIT, gaps=() if k < 3 else ((0.3, 0.9), (2.2, 2.8), (4.0, 4.4)))
            if k < 3:
                circle(p, rg - 1, RED[2], cy=HIT, over=False)
        if ry:
            rays(p, fl, ry, [GOLD[1], GOLD[2], RED[2], RED[3], RED[4]][k // 2:], cy=HIT, lean=0.2 * k)
        if fl:
            disc(p, fl, [GOLD[0], GOLD[0], GOLD[1], GOLD[2], RED[2]], cy=HIT)
        if k == 4:
            for t in np.linspace(0, 2 * np.pi, 10, endpoint=False):
                p.put(13 * np.cos(t + 0.3), HIT + 13 * np.sin(t + 0.3), RED[4])
        out.append((p.frame(), ms))
    return out


# ------------------------------------------------------------------ the lock while he aims
def r_sight():
    out = []
    for k, r in enumerate([12, 13, 14, 13]):
        p = Pic(15, 30, 2)
        # the ring, open where the ticks cut in
        gap = 0.28
        opens = [(t - gap, t + gap) for t in (0.0, np.pi / 2, np.pi, 3 * np.pi / 2)]
        opens = [(a % (2 * np.pi), b % (2 * np.pi)) if a >= 0 else (a + 2 * np.pi, 2 * np.pi) for a, b in opens] + [(0, gap)]
        circle(p, r, RED[3], cy=HIT, gaps=opens)
        circle(p, r - 1, RED[2] if k % 2 == 0 else RED[1], cy=HIT, gaps=opens, over=False)
        # four ticks pointing in, from just outside the ring to well inside it
        for t in (0.0, np.pi / 2, np.pi, 3 * np.pi / 2):
            for s in np.arange(r - 6, r + 2.01, 0.5):
                c = RED[1] if s < r - 3 else RED[3]
                p.put(s * np.cos(t), HIT + s * np.sin(t), c)
        # the dot in the middle, brighter on the breath in
        disc(p, 1.2 if k % 2 == 0 else 1.6, [GOLD[0], RED[2]], cy=HIT)
        out.append((p.frame(), 100))
    return out


def frames():
    """{tag: [(frame centred on its pivot, ms)]} - all three in league_akshan_fx (tools/art/import_akshan_fx.py)."""
    return {"r_bullet": r_bullet(), "r_hit": r_hit(), "r_sight": r_sight()}


def review(path, Z=6):
    from PIL import ImageDraw
    rows = []
    for tag, fr in frames().items():
        ims = [Image.fromarray(a).resize((a.shape[1] * Z, a.shape[0] * Z), Image.NEAREST) for a, _ in fr]
        H = max(i.height for i in ims) + 20
        W = sum(i.width + 8 for i in ims) + 90
        img = Image.new("RGB", (W, H), (60, 66, 60))
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the three pictures at 6x here")
    a = ap.parse_args()
    for tag, fr in frames().items():
        print(tag, " ".join(f"{f.shape[1]}x{f.shape[0]}" for f, _ in fr))
    if a.review:
        review(a.review)


if __name__ == "__main__":
    main()
