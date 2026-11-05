#!/usr/bin/env python3
"""Pantheon's takeoff for Grand Starfall: the burst of light where he leaves the ground and the streak he rides into the sky.

    python tools/art/fx_pantheon_jump.py [--review out.png]

The user, 2026-11-05: 「潘森大招飞起来也没有那个联盟里的特效？如果真没有的话就补」 - the kit played nothing at the leap: the
crouch's light (r_cast, 60 ticks) ended the tick he jumped, ult_leap carries no light, and 17 ticks later he is banished
into the sky. League plays Pantheon_Base_R_Cas_Jump_Shockwave there (its emitters: Dustring and Dustring1 - smoke tinted
with his cape's nebula -, Temp_BurstUp - stars thrown up -, sparks, an impact flare and a nova flash) with
Pantheon_Base_R_cas (air streaks swept upward, an initial, an inward and a horizontal flash, sharp stars).
Drawn here on the game grid (1x pixels) in the colours of his imported effects (import_pantheon_fx.py's GOLD and COSMIC
ramps, no outline on light), symmetric left to right (the client never mirrors an effect), as one picture on the spot he
leaves (league_pantheon_r_jump: a CasterViewEffect in the leap, not following, z -1 - under him, so his body rides the
streak): a white flash and a horizontal flash on the ground, a column of light shooting up from his feet past the top of
the frame, a gold shockwave ring spreading on the ground with nebula dust thrown out along it, white stars and gold sparks
flying up; the column then lifts off the ground and thins away upward (he is banished r_leap ticks into it) and the dust
settles, all gone before he lands (r_fall). Written as league/effects/league_pantheon_jump (its own small sheet; the
hero's other effect sheets come from Codex's pack through import_pantheon_fx.py).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import strips as G  # noqa: E402
from build_pantheon import P  # noqa: E402

OUT = os.path.join(ROOT, "league", "effects", "league_pantheon_jump")
TAG = "r_jump"


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# import_pantheon_fx.py's ramps
WHITE, PALE, GOLD, AMBER, ORANGE, DEEP = map(hexc, ["#FFFFFF", "#FFF6C8", "#FFE066", "#FFB627", "#F07A12", "#A4440B"])
STAR, LAV, VIOLET, NIGHT, DARK = map(hexc, ["#C9D2FF", "#7C83F0", "#4A3FB5", "#2B1F72", "#160F3D"])

HALF = 44                      # columns each side of the pivot
TOP, BOTTOM = -132, 24         # pivot-relative rows drawn (y down)
FEET = 11                      # a unit's soles under its pivot
W, H = 2 * HALF + 1, BOTTOM - TOP + 1
# the frames in ticks (60 a second): the column stands while he rises (r_leap) and is gone before he lands (r_fall)
TICKS = [2, 3, 3, 4, 4, 5, 6, 7]
assert sum(TICKS) < P["r_fall"], "the takeoff must be over before the landing"


class Frame:
    """A cell of W x H game pixels; x, y pivot-relative (x right, y down). Every pixel is mirrored left to right."""

    def __init__(self):
        self.a = np.zeros((H, W, 4), np.uint8)

    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if not (TOP <= y <= BOTTOM and -HALF <= x <= HALF):
            return
        for xx in {x, -x}:
            self.a[y - TOP, xx + HALF, :3] = c
            self.a[y - TOP, xx + HALF, 3] = 255

    def has(self, x, y):
        return TOP <= y <= BOTTOM and -HALF <= x <= HALF and self.a[y - TOP, x + HALF, 3] > 0


def rng(seed):
    return np.random.default_rng(seed)


def flash(f, cy, rx, ry):
    """A flat burst on the ground: white core, pale gold, gold rim."""
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(0, int(rx) + 2):
            d = (x / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 0.3:
                f.put(x, y, WHITE)
            elif d <= 0.65:
                f.put(x, y, PALE)
            elif d <= 1.0:
                f.put(x, y, GOLD)


def hline(f, y, reach, ramp=(WHITE, PALE, GOLD, AMBER)):
    """The horizontal flash along the ground: brightest in the middle."""
    n = len(ramp)
    for x in range(0, reach + 1):
        f.put(x, y, ramp[min(n - 1, int(x / (reach + 1) * n))])


def spike(f, top, bottom, ramp=(WHITE, PALE)):
    """A thin vertical flare (League's inward flash): a 1-px core with a pale side."""
    for y in range(top, bottom + 1):
        f.put(0, y, ramp[0])
        if y > top + 1:
            f.put(1, y, ramp[1])


def ring(f, rx, ry, front, back, thick=1.0, gaps=0, seed=0):
    """The shockwave: an ellipse on the ground round his feet, its front half (towards the viewer) brighter.
    gaps: every n-th short arc left out (the ring breaking up as it fades)."""
    r = rng(seed)
    skip = set()
    if gaps:
        arcs = 24
        skip = {k for k in range(arcs) if r.random() < 1.0 / gaps}
    for y in range(int(FEET - ry) - 2, int(FEET + ry) + 3):
        for x in range(0, int(rx) + 3):
            d = np.hypot(x / rx, (y - FEET) / ry)
            # the band's width in normalised units: thick px measured along the short axis
            if abs(d - 1.0) * ry <= thick / 2 + 0.25:
                if skip and int((np.arctan2(y - FEET, x) / np.pi + 1) * 12) % 24 in skip:
                    continue
                f.put(x, y, front if y >= FEET else back)


THREAD = 12                    # rows at the top of a column thinning to a thread (it goes on into the sky)


def column(f, bottom, top, hw_bottom, hw_top, ragged=0.0, seed=1, taper=0, head=False):
    """The streak of light he rides up: from `bottom` to `top` (rows), half-widths tapering upward; white core, pale
    gold, gold and amber bands, a ragged orange edge near its foot (ragged: the share of rows that get it).
    head: the top is the streak's bright point (still shooting up), else its last THREAD rows thin to a broken gold
    thread (it goes on into the sky); taper: rows at the foot narrowed to a dimmer point (the column off the ground)."""
    r = rng(seed)
    span = max(1, bottom - top)
    for y in range(top, bottom + 1):
        t = (bottom - y) / span                       # 0 at the foot, 1 at the top
        hw = hw_bottom + (hw_top - hw_bottom) * t ** 0.7
        dim = 0
        if taper and y > bottom - taper:
            k = (bottom - y + 1) / (taper + 1)
            hw *= k
            dim = 2 if k < 0.35 else 1 if k < 0.7 else 0
        k = y - top
        if head and k < 5:                            # the point: white, a pale side lower down
            for x, c in ((0, WHITE), (1, PALE)):
                if x <= k // 2:
                    f.put(x, y, c)
            continue
        if not head and k < THREAD:                   # the thread: 1 px, gold to pale, broken near its end
            if k in (1, 4, 6):
                continue
            f.put(0, y, AMBER if k < 3 else GOLD if k < 8 else PALE)
            continue
        whole = int(np.floor(hw + 0.5))
        for x in range(0, whole + 1):
            q = x / max(hw, 0.5)
            band = 0 if q <= 0.34 else 1 if q <= 0.6 else 2 if q <= 0.85 else 3
            f.put(x, y, (WHITE, PALE, GOLD, AMBER, ORANGE, ORANGE)[band + dim])
        if ragged and t < 0.45 and r.random() < ragged:
            f.put(whole + 1, y, ORANGE)


def star(f, x, y, size=1, core=WHITE, arm=STAR, tip=LAV):
    """A small four-pointed star (League's Q_Stars / Cross_Stars)."""
    f.put(x, y, core)
    for k in range(1, size + 1):
        c = arm if k < size or size == 1 else tip
        for dx, dy in ((k, 0), (-k, 0), (0, k), (0, -k)):
            f.put(x + dx, y + dy, c)


def sparks(f, pts, head=GOLD, tail=AMBER):
    """Sparks flying up: a bright head, a 1-px tail under it."""
    for x, y in pts:
        f.put(x, y, head)
        if tail:
            f.put(x, y + 1, tail)


def smooth_noise(seed, cell=3):
    """Value noise in [0, 1] over the right half: a coarse random grid smoothed up (clouds, not salt and pepper)."""
    r = rng(seed)
    small = (r.random((H // cell + 2, (HALF + 1) // cell + 2)) * 255).astype(np.uint8)
    big = Image.fromarray(small).resize((small.shape[1] * cell, small.shape[0] * cell), Image.BILINEAR)
    return np.asarray(big, np.float64)[:H, :HALF + 1] / 255.0


def dust(f, puffs, fade=0.0, seed=7, specks=0):
    """Nebula dust thrown out along the ring (League's Dustring, smoke tinted with his cape's nebula): puffs
    (x, y, radius) on the right half (mirrored), lit from above; fade erodes them and darkens them."""
    r = rng(seed)
    noise = 0.7 * smooth_noise(seed) + 0.3 * r.random((H, HALF + 1))
    for y in range(TOP, BOTTOM + 1):
        for x in range(0, HALF + 1):
            best, lift = -1.0, 0.0
            for px, py, pr in puffs:
                d = np.hypot((x - px) / pr, (y - py) / (pr * 0.75))
                v = 1.0 - d
                if v > best:
                    best, lift = v, (py - y) / pr
            v = best + 0.45 * (noise[y - TOP, x] - 0.5) - fade
            if v <= 0:
                continue
            shade = v + 0.55 * lift - 0.5 * fade
            c = LAV if shade > 0.62 else VIOLET if shade > 0.3 else NIGHT if shade > 0.02 else DARK
            if not f.has(x, y):
                f.put(x, y, c)
    for _ in range(specks):                           # stars in the nebula
        px, py, pr = puffs[int(r.integers(len(puffs)))]
        x = int(round(px + r.uniform(-0.6, 0.6) * pr))
        y = int(round(py + r.uniform(-0.5, 0.4) * pr))
        if f.has(x, y):
            f.put(x, y, STAR if r.random() < 0.6 else WHITE)


def ring_puffs(rx, ry, size, rise):
    """Dust puffs thrown out along the ring (on it and just outside), the biggest at its sides, rising a little as
    the smoke does: (x, y, r) on the right half."""
    out = []
    for deg, k in ((0, 1.0), (36, 0.85), (-30, 0.8), (68, 0.7), (-62, 0.6), (90, 0.55), (-90, 0.45)):
        a = np.radians(deg)
        out.append((1.04 * rx * np.cos(a), FEET + 1.04 * ry * np.sin(a) - rise * k, size * k))
    return out


def frames():
    out = []
    # 1 the initial flash: a white burst at his feet, the inward flare up his legs, the horizontal flash
    f = Frame()
    flash(f, FEET - 1, 7, 3)
    spike(f, -8, FEET)
    hline(f, FEET, 15)
    out.append(f)
    # 2 the launch: the column shoots up from his feet (its point still rising), the ground flash, the ring forming
    f = Frame()
    column(f, FEET - 1, -74, 4, 2, ragged=0.5, seed=2, head=True)
    flash(f, FEET - 1, 10, 4)
    ring(f, 14, 4, PALE, GOLD, thick=1.2)
    hline(f, FEET, 23)
    sparks(f, [(9, 4), (13, 7), (6, -2)])
    out.append(f)
    # 3 the column at full height (on into the sky), the shockwave spreading, the dust thrown out, stars flying up
    f = Frame()
    dust(f, ring_puffs(21, 6, 5.5, 1), fade=0.05, seed=3, specks=2)
    ring(f, 21, 6, WHITE, PALE, thick=1.6)
    column(f, FEET, TOP, 5, 1.5, ragged=0.6, seed=3)
    flash(f, FEET - 1, 7, 3)
    for x, y in [(8, -22), (6, -46)]:
        star(f, x, y)
    sparks(f, [(12, -4), (16, 0), (9, -32), (11, -60)])
    out.append(f)
    # 4 the ring wider, gold; the dust spreading; the stars and sparks higher
    f = Frame()
    dust(f, ring_puffs(27, 8, 7.5, 2), fade=0.1, seed=4, specks=3)
    ring(f, 27, 8, PALE, GOLD, thick=1.4, seed=4)
    column(f, FEET - 2, TOP, 4, 1.2, ragged=0.4, seed=4)
    for x, y in [(9, -40), (5, -66), (10, -92)]:
        star(f, x, y)
    star(f, 13, -20, size=2)
    sparks(f, [(17, -12), (21, -4), (12, -50), (14, -78)])
    out.append(f)
    # 5 the column lifts off the ground (he goes up with it), the ring breaking up, the dust at its widest
    f = Frame()
    dust(f, ring_puffs(31, 9, 8.5, 3), fade=0.2, seed=5, specks=3)
    ring(f, 31, 9, GOLD, AMBER, thick=1.0, gaps=4, seed=5)
    column(f, -16, TOP, 3, 1, seed=5, taper=8)
    for x, y in [(10, -62), (6, -90), (11, -112)]:
        star(f, x, y)
    sparks(f, [(15, -34), (19, -22), (13, -100)], head=AMBER, tail=ORANGE)
    out.append(f)
    # 6 a thin streak high up, the ring's last arcs, the dust settling
    f = Frame()
    dust(f, ring_puffs(33, 10, 8.5, 4), fade=0.32, seed=6, specks=2)
    ring(f, 33, 10, AMBER, ORANGE, thick=1.0, gaps=2, seed=6)
    column(f, -64, TOP, 1.5, 0.6, seed=6, taper=10)
    star(f, 11, -86)
    star(f, 7, -114, size=2)
    sparks(f, [(17, -54), (14, -122)], head=AMBER, tail=None)
    out.append(f)
    # 7 the last of the streak, the dust thinning, a star or two
    f = Frame()
    dust(f, ring_puffs(34, 10, 8, 5), fade=0.5, seed=7, specks=1)
    column(f, -104, TOP, 0.6, 0.5, seed=7, taper=6)
    star(f, 12, -106, core=STAR, arm=LAV)
    sparks(f, [(18, -76)], head=ORANGE, tail=None)
    out.append(f)
    # 8 the last wisps
    f = Frame()
    dust(f, ring_puffs(35, 11, 7, 6), fade=0.68, seed=8)
    sparks(f, [(20, -96)], head=DEEP, tail=None)
    out.append(f)
    ms = [t * 1000.0 / 60 for t in TICKS]
    assert len(out) == len(ms)
    return [(f.a, m) for f, m in zip(out, ms)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write the frames at 6x here")
    a = ap.parse_args()
    fr = frames()
    cells = []
    for k, (cell, ms) in enumerate(fr):
        assert (cell == cell[:, ::-1]).all(), f"frame {k + 1} is not symmetric"
        assert set(np.unique(cell[..., 3])) <= {0, 255}
        cells.append((G.centre_frame(cell, -HALF, TOP), ms))      # centred on the pivot, as the client draws it
    w, h = G.write_sheet(OUT, {TAG: cells}, share=True)
    print(f"league/effects/league_pantheon_jump#sheet.png {w}x{h}: {TAG} {len(cells)}f "
          f"{sum(m for _, m in cells):.0f}ms ({sum(TICKS)} ticks)")
    if a.review:
        Z = 6
        img = Image.new("RGBA", ((W + 2) * Z * len(fr), H * Z), (60, 70, 60, 255))
        for k, (cell, _) in enumerate(fr):
            img.alpha_composite(Image.fromarray(cell).resize((W * Z, H * Z), Image.NEAREST), (k * (W + 2) * Z, 0))
        img.convert("RGB").save(a.review)
        print("review", a.review)


if __name__ == "__main__":
    main()
