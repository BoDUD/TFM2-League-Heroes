"""The dragons mod's own pictures on the battlefield. 0.4.0 (the user, 2026-11-11: 「拿了龙魂没有特效的 都要补 还有远古龙
斩杀特效的」): what a Dragon Soul does each time it triggers, the soul taken, the Elder Dragon's burn and its execute.
0.5.0, the elemental rift's terrain: the Cloud rift's wind currents, the Hextech rift's gates, the Ocean rift's brush,
honeyfruit and rain, the Chemtech rift's fog, the Mountain rift's rocks, the Infernal rift's burning walls. Pixel art drawn square by square with tools/art/dragon_fx.py's brushes (a few flat tones of the element, a dark
outline, no blur, no half-transparent pixels), one square = one game pixel (1000 simulation units): the mod's client
extension draws these frames itself on the match's own render map (addons/league_dragons/src/world.rs), no champion's
data needed.

    python tools/art/dragons_soul_fx.py            # writes the sheet and the table
    python tools/art/dragons_soul_fx.py --check    # both are what this script makes (exit 1 if not)
    python tools/art/dragons_soul_fx.py --preview out.png   # a contact sheet, 4x, on the map's green

(numpy, scipy, scikit-image and pillow, like dragon_fx.py.)

Writes addons/league_dragons/effects/league_dragons_fx#sheet.png (every animation a row of frames),
addons/league_dragons/src/fx_atlas.rs (where each animation is on the sheet, its anchor - the point put on the champion's
feet - and how many ticks a frame stays) and addons/league_dragons/src/fx_runs.bin (the same frames as rows of equal
pixels, compiled into the DLL: what the mod draws square by square when it cannot draw the sheet). Deterministic: every
frame has its own seed.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import dragon_fx as fx  # noqa: E402

ADDON = os.path.join(ROOT, "addons", "league_dragons")
SHEET = os.path.join(ADDON, "effects", "league_dragons_fx#sheet.png")
TABLE = os.path.join(ADDON, "src", "fx_atlas.rs")
RUNS = os.path.join(ADDON, "src", "fx_runs.bin")
SHEET_W = 1056    # the widest a row may get before it wraps
ELEMENTS = ["infernal", "mountain", "ocean", "cloud", "hextech", "chemtech"]


def blank(w, h):
    return np.zeros((h, w, 4), np.uint8)


def tone(el, k):
    return fx.tones(el)[k]


def sparks(layer, rng, cx, cy, n, spread, rise, el, r=(0.7, 1.4), k=4):
    """embers / drops flung up and out of (cx, cy)"""
    for _ in range(n):
        a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
        d = spread * rng.uniform(0.35, 1.0)
        fx.disc(layer, cx + math.cos(a) * d, cy + math.sin(a) * d * 0.8 - rise, rng.uniform(*r), tone(el, k))


def ground_ring(shape, cx, cy, radius, band, el, seed, cuts=(0.1, 0.34, 0.6, 0.84, 1.5), squash=0.5):
    """a flat ring on the ground round (cx, cy): `radius` wide, half as deep"""
    X, Y = fx.grid(shape)
    d = np.hypot(X - cx, (Y - cy) / squash)
    nz = fx.Noise(seed)
    heat = (1 - np.abs(d - radius) / (band / 2)) * (0.75 + 0.5 * nz.fbm(X / 4.0, Y / 4.0))
    return fx.paint(heat, el, cuts, least=2)


def pillar(shape, cx, base, width, height, el, seed, strength=1.0, cuts=(0.08, 0.3, 0.55, 0.78, 0.93)):
    """a column of light / flame standing on (cx, base): widest a third up, licking at its top"""
    X, Y = fx.grid(shape)
    v = (base - Y) / max(height, 1.0)
    nz = fx.Noise(seed)
    wob = (nz.fbm(Y / 5.0 + 3, X / 9.0) - 0.5) * width * 0.5
    hw = width * (0.55 + 0.45 * np.sin(np.clip(v, 0, 1) * math.pi) ** 0.6)
    lat = np.abs(X - cx - wob * np.clip(v, 0, 1)) / np.maximum(hw, 1e-3)
    heat = np.clip(1 - lat ** 2, 0, 1) * np.clip(1 - np.clip(v, 0, 2) ** 3, 0, 1) * (v > -0.08)
    heat *= strength * (0.72 + 0.56 * nz.fbm(X / 3.5, Y / 5.0 + 11))
    return fx.paint(heat, el, cuts, least=3)


# ---- the souls' triggers ------------------------------------------------------------------------------------------

def infernal_blast():
    """Infernal soul: the blast on the champion hit (25 game px round him)"""
    w, h, anchor = 72, 64, (36, 50)
    out = []
    for i, (phase, R, seed) in enumerate([(0, 15, 11), (1, 20, 12), (1, 22, 13), (2, 22, 14), (2, 20, 15)]):
        f = fx.burst((h, w), anchor, R, "infernal", phase, 300 + seed)
        ring = ground_ring((h, w), anchor[0], anchor[1], (10, 18, 24, 27, 29)[i], (7, 7, 6, 4, 3)[i], "infernal", 320 + i)
        out.append(fx.over(f, ring))
    for i in range(2):   # the embers left in the air
        f = blank(w, h)
        rng = np.random.default_rng(340 + i)
        sparks(f, rng, anchor[0], anchor[1] - 6, (16, 9)[i], 30, (10, 18)[i], "infernal", r=((0.8, 1.6), (0.6, 1.1))[i], k=(4, 3)[i])
        sparks(f, rng, anchor[0], anchor[1] - 4, (6, 3)[i], 22, (6, 12)[i], "smoke", r=(1.2, 2.2), k=2)
        out.append(f)
    return w, h, anchor, 4, out


def hex_spark():
    """Hextech soul: the lightning striking a champion (the bolt between them is drawn by the mod, square by square)"""
    w, h, anchor = 44, 44, (22, 26)
    out = []
    for i, (phase, R) in enumerate([(0, 9), (1, 12), (1, 13), (2, 12)]):
        out.append(fx.burst((h, w), (anchor[0], anchor[1] + 2), R, "hextech", phase, 400 + i))
    f = blank(w, h)
    rng = np.random.default_rng(409)
    for _ in range(7):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(6, 16)
        p = (anchor[0] + math.cos(a) * d, anchor[1] - 4 + math.sin(a) * d * 0.8)
        q = (p[0] + math.cos(a) * 4, p[1] + math.sin(a) * 3)
        fx.stroke(f, [p, q], tone("hextech", 4), 1)
    out.append(fx.outline_layer(f, tone("hextech", 1)))
    return w, h, anchor, 4, out


def mountain_shield():
    """Mountain soul: the shield going up - stones rise round the champion and close into an amber shell"""
    w, h, anchor = 60, 64, (30, 54)
    out = []
    amber = [np.array(c, np.uint8) for c in [(86, 52, 14), (176, 112, 30), (232, 172, 60), (255, 222, 128), (255, 246, 206)]]
    for i in range(7):
        f = blank(w, h)
        rng = np.random.default_rng(500 + i)
        t = i / 6
        if i <= 4:   # the stones: out of the ground, up round him
            n = 7
            for k in range(n):
                a = k / n * 2 * math.pi + 0.3
                rad = 19 - 3 * min(1.0, t * 2)
                lift = (0, 8, 16, 22, 26)[i] * (0.8 + 0.4 * ((k * 7) % 5) / 4)
                x = anchor[0] + math.cos(a) * rad
                y = anchor[1] + math.sin(a) * rad * 0.42 - lift
                fx.chunk(f, x, y, (3.2, 4.2, 4.4, 3.8, 2.8)[i] + (k % 3) * 0.6, rng)
        if i <= 1:   # the ground they break out of
            dust = ground_ring((h, w), anchor[0], anchor[1], 17 + 3 * i, 7, "mountain", 520 + i)
            f = fx.over(f, dust)
        if i >= 2:   # the shell: a six-sided outline round his body, brightest when it closes
            cx, cy = anchor[0], anchor[1] - 18
            pts = [(cx + math.cos(k / 6 * 2 * math.pi + math.pi / 6) * 17, cy + math.sin(k / 6 * 2 * math.pi + math.pi / 6) * 22)
                   for k in range(7)]
            shell = blank(w, h)
            bright = {2: 1, 3: 3, 4: 4, 5: 2, 6: 1}[i]
            fx.stroke(shell, pts, amber[bright], 2 if i in (3, 4) else 1)
            if i in (3, 4):   # the facets catching the light
                for k in (0, 2, 4):
                    fx.stroke(shell, [(cx, cy), pts[k]], amber[bright - 2], 1)
            if i == 6:        # breaking up as it settles into him
                keep = np.random.default_rng(540).random(shell.shape[:2]) < 0.45
                shell[~keep] = 0
            shell = fx.outline_layer(shell, amber[0]) if i < 6 else shell
            f = fx.over(shell, f)
        out.append(f)
    return w, h, anchor, 5, out


def ocean_heal():
    """Ocean soul: the healing water - a ring of water closes on the champion and rises as drops"""
    w, h, anchor = 60, 68, (30, 58)
    out = []
    t3, t0, t5 = tone("ocean", 3), tone("ocean", 0), tone("ocean", 5)
    for i in range(8):
        rng = np.random.default_rng(600 + i)
        f = blank(w, h)
        if i <= 5:
            radius = (24, 21, 18, 15, 12, 9)[i]
            ring = ground_ring((h, w), anchor[0], anchor[1], radius, (5, 6, 6, 6, 5, 4)[i], "ocean", 620 + i,
                               cuts=(0.1, 0.3, 0.55, 0.8, 0.95))
            f = fx.over(ring, f)
        if i >= 1:   # crests standing up on the ring, then the drops going up round him
            n = (0, 6, 8, 9, 9, 8, 6, 4)[i]
            for k in range(n):
                a = (k + rng.uniform(-0.2, 0.2)) / n * 2 * math.pi
                rad = (24, 21, 18, 15, 13, 12, 12, 12)[i] * rng.uniform(0.75, 1.0)
                rise = (0, 5, 11, 18, 26, 34, 42, 48)[i] * rng.uniform(0.55, 1.0)
                x = anchor[0] + math.cos(a) * rad
                y = anchor[1] + math.sin(a) * rad * 0.45 - rise
                r = (0, 2.2, 2.6, 2.6, 2.4, 2.0, 1.6, 1.2)[i] * rng.uniform(0.8, 1.15)
                fx.disc(f, x, y, r, t3, t0, t5)
        if 2 <= i <= 5:   # the swell under his feet
            swell = pillar((h, w), anchor[0], anchor[1] + 1, (9, 11, 10, 7)[i - 2], (16, 26, 30, 24)[i - 2], "ocean", 640 + i,
                           strength=(0.8, 0.95, 0.85, 0.6)[i - 2], cuts=(0.2, 0.42, 0.66, 0.86, 0.97))
            f = fx.over(f, swell)
        out.append(f)
    return w, h, anchor, 5, out


def cloud_gust():
    """Cloud soul: the gust after the ultimate - wind curls whip round the champion and streak off behind him"""
    w, h, anchor = 68, 56, (34, 46)
    out = []
    for i in range(7):
        rng = np.random.default_rng(700 + i)
        f = blank(w, h)
        if i <= 4:
            puff = ground_ring((h, w), anchor[0], anchor[1], (8, 14, 20, 25, 29)[i], (8, 7, 6, 4, 3)[i], "cloud", 720 + i,
                               cuts=(0.12, 0.36, 0.62, 0.86, 1.5))
            f = fx.over(puff, f)
        n = (2, 3, 4, 4, 3, 2, 1)[i]
        for k in range(n):
            a = k / max(n, 1) * 2 * math.pi + i * 0.9
            rad = (8, 12, 16, 19, 22, 24, 26)[i]
            fx.curl(f, anchor[0] + math.cos(a) * rad, anchor[1] - 14 + math.sin(a) * rad * 0.5 - i * 1.5,
                    (6, 7.5, 8.5, 8.5, 7.5, 6, 5)[i], "cloud", k % 2 == 0)
        if i >= 2:   # speed lines
            for k in range((0, 0, 4, 6, 6, 5, 3)[i]):
                y = anchor[1] - rng.uniform(2, 34)
                x0 = anchor[0] + rng.uniform(-30, 14)
                ln = rng.uniform(6, 13)
                fx.stroke(f, [(x0, y), (x0 + ln, y)], tone("cloud", 4), 1)
        f = fx.outline_layer(f, tone("cloud", 0)) if i >= 5 else f
        out.append(f)
    return w, h, anchor, 5, out


def chem_rage():
    """Chemtech soul: the last stand below half health - the toxin flares up round the champion and bubbles off"""
    w, h, anchor = 60, 68, (30, 58)
    out = []
    t0, t3, t5 = tone("chemtech", 0), tone("chemtech", 3), tone("chemtech", 5)
    for i in range(7):
        rng = np.random.default_rng(800 + i)
        f = blank(w, h)
        if i <= 3:
            f = fx.burst((h, w), anchor, (11, 15, 17, 16)[i], "chemtech", (0, 1, 1, 2)[i], 820 + i)
        if 1 <= i <= 5:
            flare = pillar((h, w), anchor[0], anchor[1], (9, 12, 12, 10, 7)[i - 1], (22, 34, 40, 38, 30)[i - 1], "chemtech",
                           840 + i, strength=(0.85, 1.0, 0.95, 0.8, 0.6)[i - 1], cuts=(0.16, 0.38, 0.62, 0.84, 0.96))
            f = fx.over(f, flare) if i <= 2 else fx.over(flare, f)
        for k in range((0, 3, 5, 6, 6, 5, 3)[i]):
            x = anchor[0] + rng.uniform(-18, 18)
            y = anchor[1] - (6, 10, 18, 26, 34, 42, 50)[i] * rng.uniform(0.5, 1.0)
            fx.ring_dot(f, x, y, rng.uniform(1.8, 3.2), t0, t5)
            if rng.random() < 0.5:
                fx.disc(f, x + rng.uniform(-6, 6), y + rng.uniform(-4, 8), rng.uniform(1.0, 1.8), t3, t0, t5)
        out.append(f)
    return w, h, anchor, 5, out


def soul_claim(el):
    """A Dragon Soul taken: the element rises round each champion of the team - a ring on the ground, a pillar through
    him, sparks off its top"""
    w, h, anchor = 60, 84, (30, 72)
    kind = fx.KIND[el]
    out = []
    for i in range(9):
        rng = np.random.default_rng(900 + 17 * ELEMENTS.index(el) + i)
        f = blank(w, h)
        if i <= 6:
            radius = (6, 11, 16, 20, 23, 25, 27)[i]
            ring = ground_ring((h, w), anchor[0], anchor[1], radius, (6, 7, 7, 6, 5, 4, 3)[i], el, 930 + i,
                               cuts=(0.1, 0.32, 0.58, 0.82, 0.95))
            f = fx.over(ring, f)
        if 1 <= i <= 7:
            hgt = (20, 40, 56, 64, 64, 54, 36)[i - 1]
            wid = (6, 9, 11, 11, 9, 7, 5)[i - 1]
            col = pillar((h, w), anchor[0], anchor[1], wid, hgt, el, 950 + 3 * i, strength=(0.8, 0.95, 1.0, 1.0, 0.9, 0.75, 0.55)[i - 1])
            f = fx.over(col, f)
        if i >= 2:
            n = (0, 0, 4, 7, 9, 9, 8, 6, 4)[i]
            top = anchor[1] - (0, 0, 30, 44, 54, 60, 64, 68, 72)[i]
            for _ in range(n):
                x = anchor[0] + rng.uniform(-16, 16)
                y = top + rng.uniform(-6, 22)
                if kind == "rock":
                    fx.chunk(f, x, y, rng.uniform(1.6, 2.6), rng)
                elif kind in ("water", "goo"):
                    fx.disc(f, x, y, rng.uniform(1.2, 2.2), tone(el, 3), tone(el, 0), tone(el, 5))
                elif kind == "bolt":
                    fx.stroke(f, [(x, y), (x + rng.uniform(-3, 3), y - rng.uniform(3, 6))], tone(el, 5), 1)
                else:
                    fx.disc(f, x, y, rng.uniform(0.7, 1.4), tone(el, 4))
        out.append(f)
    return w, h, anchor, 5, out


# ---- the Elder Dragon ------------------------------------------------------------------------------------------------

def elder_burn():
    """Aspect of the Dragon: the Elder's flame catching on a champion"""
    w, h, anchor = 28, 36, (14, 31)
    out = []
    for i in range(6):
        f = pillar((h, w), anchor[0], anchor[1], (4, 6, 7, 7, 6, 4)[i], (10, 18, 24, 26, 22, 14)[i], "elder", 1000 + i,
                   strength=(0.8, 1.0, 1.0, 0.95, 0.8, 0.6)[i])
        rng = np.random.default_rng(1010 + i)
        sparks(f, rng, anchor[0], anchor[1] - 8, (0, 2, 3, 4, 4, 3)[i], 10, (0, 6, 10, 14, 18, 22)[i], "elder", r=(0.6, 1.0), k=4)
        out.append(f)
    return w, h, anchor, 5, out


def elder_execute():
    """The Elder's execute: a shaft of the Elder's fire comes down on the champion, bursts on the ground and leaves a
    ring of embers - big enough to read across a team fight"""
    w, h, anchor = 96, 136, (48, 116)
    out = []
    X, Y = fx.grid((h, w))
    for i in range(11):
        rng = np.random.default_rng(1100 + i)
        f = blank(w, h)
        # the shaft: a thin line down (0-1), the full column (2-4), thinning out (5-7)
        if i <= 7:
            reach = (0.45, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)[i]
            half = (1.5, 2.5, 9, 12, 11, 8, 5, 2.5)[i]
            top = anchor[1] - 112
            bottom = top + 112 * reach
            nz = fx.Noise(1120 + i)
            lat = np.abs(X - anchor[0] - (nz.fbm(Y / 7.0, X * 0 + i) - 0.5) * half * 0.6) / half
            inside = (Y >= top) & (Y <= bottom)
            heat = np.clip(1 - lat ** 2, 0, 1) * inside * (0.75 + 0.5 * nz.fbm(X / 3.0, Y / 6.0 + i * 2))
            heat *= np.clip((Y - top) / 14.0, 0.25, 1.0)          # fading into the sky
            shaft = fx.paint(heat, "elder", (0.1, 0.32, 0.56, 0.78, 0.92), least=3)
            f = fx.over(shaft, f)
        # the burst on the ground
        if 2 <= i <= 6:
            b = fx.burst((h, w), anchor, (18, 26, 30, 30, 26)[i - 2], "elder", (0, 1, 1, 2, 2)[i - 2], 1140 + i)
            f = fx.over(b, f)
        # the shock ring running out along the ground
        if i >= 2:
            radius = (0, 0, 12, 20, 27, 33, 38, 42, 45, 47, 48)[i]
            ring = ground_ring((h, w), anchor[0], anchor[1], radius, (0, 0, 8, 8, 8, 7, 7, 6, 6, 5, 4)[i], "elder", 1160 + i,
                               cuts=((0.1, 0.32, 0.58, 0.82, 0.95) if i < 9 else (0.1, 0.4, 0.75, 1.5, 1.5)), squash=0.42)
            f = fx.over(f, ring)
        # the embers going up after it
        if i >= 5:
            sparks(f, rng, anchor[0], anchor[1] - 8, (0, 0, 0, 0, 0, 10, 16, 18, 16, 11, 6)[i], 34,
                   (0, 0, 0, 0, 0, 6, 16, 28, 40, 52, 62)[i], "elder", r=(0.8, 1.7), k=(4, 4, 4, 4, 4, 5, 5, 4, 4, 3, 3)[i])
        out.append(f)
    return w, h, anchor, 5, out


# ---- the elemental rift's terrain (league_dragons 0.5.0) ------------------------------------------------------------------

LEAF = {
    # outline, deep, base, light, highlight
    "ocean": [(8, 52, 50), (18, 104, 88), (36, 152, 112), (98, 204, 140), (186, 240, 186)],
    # outline, deep purple, light purple, toxic green, pale green
    "chemtech": [(40, 16, 62), (88, 44, 132), (140, 84, 180), (150, 210, 60), (226, 250, 150)],
}


def wind(direction):
    """a tile of a Cloud rift's wind current: streaks running along the flow ("h" to the right, "v" downward, "d" down the
    river's diagonal). It repeats every 48 squares along the flow (the diagonal one every (24, 24)), and its 8 frames
    carry the streaks one whole period on, so the tiles laid end to end flow without a seam"""
    n = 8
    w, h = {"h": (48, 32), "v": (32, 48), "d": (48, 48)}[direction]
    period = 48.0 if direction != "d" else 24.0 * math.sqrt(2)
    rng = np.random.default_rng(1200)
    streaks = [(rng.uniform(-11, 11), rng.uniform(0, period), rng.uniform(9, 15), int(rng.integers(3, 5)))
               for _ in range(7 if direction != "d" else 5)]
    c = math.sqrt(0.5)
    out = []
    for f in range(n):
        layer = blank(w, h)
        for across, phase, length, k in streaks:
            head = (phase + f * period / n) % period
            for rep in range(-3, 4):
                s1 = head + rep * period
                s0 = s1 - length
                if direction == "h":
                    p0, p1 = (s0, h / 2 + across), (s1, h / 2 + across)
                elif direction == "v":
                    p0, p1 = (w / 2 + across, s0), (w / 2 + across, s1)
                else:   # along (c, c) from the tile's top-left corner, `across` to its side
                    p0, p1 = (s0 * c + across * c, s0 * c - across * c), (s1 * c + across * c, s1 * c - across * c)
                fx.stroke(layer, [p0, p1], tone("cloud", k), 1)
                fx.stroke(layer, [((p0[0] + 2 * p1[0]) / 3, (p0[1] + 2 * p1[1]) / 3), p1], tone("cloud", 5), 1)
        out.append(fx.outline_layer(layer, tone("cloud", 1)))
    return w, h, ((w // 2, h // 2) if direction != "d" else (0, 0)), 5, out


def gate():
    """a hex-gate (Hextech rift): a six-sided ring of Hextech blue on the ground with brass corners, a glint running
    round it, a shimmer rising from its middle"""
    w, h, anchor = 60, 48, (30, 28)
    brass = [np.array(c, np.uint8) for c in [(60, 40, 10), (150, 108, 30), (226, 180, 70), (255, 232, 150)]]
    cx, cy = anchor
    R, sq = 22.0, 0.74
    corners = [(cx + math.cos(k / 6 * 2 * math.pi) * R, cy + math.sin(k / 6 * 2 * math.pi) * R * sq) for k in range(7)]
    inner = [(cx + (x - cx) * 0.7, cy + (y - cy) * 0.7) for x, y in corners]
    out = []
    for i in range(8):
        ring = blank(w, h)
        fx.stroke(ring, corners, tone("hextech", 2), 2)
        fx.stroke(ring, inner, tone("hextech", 1), 1)
        k = i * 6 // 8
        fx.stroke(ring, [corners[k], corners[k + 1]], tone("hextech", 4), 2)
        t = (i * 6 / 8) % 1
        gx = corners[k][0] + (corners[k + 1][0] - corners[k][0]) * t
        gy = corners[k][1] + (corners[k + 1][1] - corners[k][1]) * t
        fx.disc(ring, gx, gy, 1.7, tone("hextech", 5))
        f = fx.outline_layer(ring, tone("hextech", 0))
        for x, y in corners[:6]:
            fx.disc(f, x, y, 2.3, brass[2], brass[0], brass[3])
        rng = np.random.default_rng(1300 + i)
        for _ in range(4):
            x = cx + rng.uniform(-10, 10)
            y = cy - rng.uniform(2, 16) - (i % 4) * 2
            fx.stroke(f, [(x, y), (x, y - rng.uniform(2, 4))], tone("hextech", 4), 1)
        out.append(f)
    return w, h, anchor, 6, out


def gate_flash():
    """a champion going through a hex-gate: a quick column of Hextech light and a ring, at both gates"""
    w, h, anchor = 48, 76, (24, 62)
    out = []
    for i in range(6):
        f = blank(w, h)
        col = pillar((h, w), anchor[0], anchor[1], (5, 10, 12, 9, 6, 3)[i], (30, 58, 62, 58, 46, 30)[i], "hextech", 1400 + i,
                     strength=(0.9, 1.0, 1.0, 0.9, 0.75, 0.55)[i])
        f = fx.over(col, f)
        ring = ground_ring((h, w), anchor[0], anchor[1], (8, 14, 19, 22, 24, 25)[i], (6, 6, 5, 4, 4, 3)[i], "hextech", 1420 + i,
                           cuts=(0.1, 0.32, 0.58, 0.82, 0.95), squash=0.74)
        f = fx.over(f, ring)
        rng = np.random.default_rng(1440 + i)
        for _ in range((0, 4, 6, 6, 5, 3)[i]):
            x = anchor[0] + rng.uniform(-16, 16)
            y = anchor[1] - rng.uniform(6, 56)
            fx.stroke(f, [(x, y), (x + rng.uniform(-2, 2), y - rng.uniform(3, 6))], tone("hextech", 5), 1)
        out.append(f)
    return w, h, anchor, 4, out


def brush(kind):
    """a patch of the rift's new brush (Ocean) / chem-fog (Chemtech), 38 squares round its middle: a ring of clumps with
    tufts inside, open enough to see who stands in it; 4 frames swaying. From above, like the map: no squash"""
    w, h, anchor = 96, 92, (48, 48)
    pal = [np.array(c, np.uint8) for c in LEAF[kind]]
    rng = np.random.default_rng(1500 if kind == "ocean" else 1600)
    n = 16
    clumps = []
    for k in range(n):
        a = (k + rng.uniform(-0.25, 0.25)) / n * 2 * math.pi
        rad = 33 + rng.uniform(-3, 3)
        clumps.append((anchor[0] + math.cos(a) * rad, anchor[1] + math.sin(a) * rad, rng.uniform(5.5, 8.0),
                       rng.uniform(0, 2 * math.pi)))
    tufts = [(anchor[0] + rng.uniform(-22, 22), anchor[1] + rng.uniform(-20, 24), rng.uniform(0, 2 * math.pi)) for _ in range(13)]
    bubbles = [(anchor[0] + rng.uniform(-30, 30), anchor[1] + rng.uniform(-26, 30), rng.uniform(1.8, 3.0), int(rng.integers(0, 4)))
               for _ in range(9)]
    out = []
    for i in range(4):
        f = blank(w, h)
        turn = i / 4 * 2 * math.pi
        for x, y, ph in tufts:
            lean = math.sin(ph + turn) * 1.6
            for dx, ln in ((-2, 4), (0, 6), (2, 4)):
                fx.stroke(f, [(x + dx, y), (x + dx + lean, y - ln)], pal[3 if dx == 0 else 2], 1)
        f = fx.outline_layer(f, pal[0])
        for x, y, r, ph in sorted(clumps, key=lambda c: c[1]):
            ox = math.sin(ph + turn) * 1.0
            fx.disc(f, x + ox, y, r, pal[1], pal[0])
            fx.disc(f, x + ox - r * 0.2, y - r * 0.25, r * 0.62, pal[2])
            fx.disc(f, x + ox - r * 0.36, y - r * 0.42, r * 0.3, pal[3])
        if kind == "chemtech":
            for x, y, r, ph in bubbles:
                rise = ((i + ph) % 4) * 3
                fx.ring_dot(f, x, y - rise, r, pal[0], pal[4])
                fx.disc(f, x + 1, y - rise + 1, max(0.8, r * 0.35), pal[3])
        out.append(f)
    return w, h, anchor, 15, out


def fruit():
    """a honeyfruit plant (Ocean rift): a stem, leaves and three glowing fruits that bob"""
    w, h, anchor = 28, 34, (14, 29)
    stem = np.array((30, 96, 60), np.uint8)
    leaf = np.array((60, 150, 80), np.uint8)
    edge = np.array((14, 52, 40), np.uint8)
    gold = [np.array(c, np.uint8) for c in [(120, 70, 10), (236, 170, 40), (255, 226, 110), (255, 250, 210)]]
    out = []
    for i in range(4):
        f = blank(w, h)
        bob = (0, -1, 0, 1)[i]
        fx.stroke(f, [(14, 29), (14, 15)], stem, 2)
        fx.stroke(f, [(14, 22), (8, 17)], stem, 1)
        fx.stroke(f, [(14, 20), (20, 15)], stem, 1)
        f = fx.outline_layer(f, edge)
        for x, y in ((7, 25), (21, 25), (14, 28)):
            fx.disc(f, x, y, 3.3, leaf, edge)
        for x, y, r in ((8, 15, 3.6), (20, 13, 3.6), (14, 9, 4.2)):
            fx.disc(f, x, y + bob, r, gold[1], gold[0], gold[3])
            fx.disc(f, x - 1, y + bob - 1, r * 0.45, gold[2])
        out.append(f)
    return w, h, anchor, 12, out


def fruit_eat():
    """a honeyfruit eaten: its glow bursts into drops and a ring of water"""
    w, h, anchor = 44, 48, (22, 36)
    gold = [np.array(c, np.uint8) for c in [(120, 70, 10), (236, 170, 40), (255, 226, 110), (255, 250, 210)]]
    out = []
    for i in range(5):
        rng = np.random.default_rng(1700 + i)
        f = ground_ring((h, w), anchor[0], anchor[1], (6, 11, 15, 18, 20)[i], (5, 5, 4, 3, 3)[i], "ocean", 1720 + i,
                        cuts=(0.1, 0.3, 0.55, 0.8, 0.95), squash=0.7)
        for _ in range((8, 10, 9, 7, 4)[i]):
            a = rng.uniform(-math.pi, 0)
            d = rng.uniform(4, 16) + i * 2
            x, y = anchor[0] + math.cos(a) * d, anchor[1] - 10 + math.sin(a) * d - i * 3
            fx.disc(f, x, y, rng.uniform(1.2, 2.2) - i * 0.15, gold[1 + (i < 2)], gold[0], gold[3])
        out.append(f)
    return w, h, anchor, 5, out


def boulder(layer, cx, cy, rx, ry, seed):
    """a round lump of rock: a lumpy outline, lit from the upper left (light, mid, dark faces), outlined"""
    from scipy import ndimage
    X, Y = fx.grid(layer.shape[:2])
    nz = fx.Noise(seed)
    nx, ny = (X - cx) / rx, (Y - cy) / ry
    m = np.hypot(nx, ny) + (nz.fbm(X / 5.0, Y / 5.0) - 0.5) * 0.4 < 1
    lit = -(nx * 0.6 + ny * 0.8) + (nz.fbm(X / 3.0 + 9, Y / 3.0) - 0.5) * 0.55
    face = np.where(lit > 0.5, 4, np.where(lit > 0.1, 3, np.where(lit > -0.35, 2, 1)))
    for k in (1, 2, 3, 4):
        sel = m & (face == k)
        layer[sel, :3] = np.array(fx.ROCK[k], np.uint8)
        layer[sel, 3] = 255
    edge = m & ~ndimage.binary_erosion(m, structure=fx.CROSS)
    layer[edge, :3] = np.array(fx.ROCK[0], np.uint8)
    layer[edge, 3] = 255


def rock():
    """a Mountain rift's rock: dust breaks the ground, the boulders rise out of it; the last frame is the rock standing.
    Its foot lies just under the anchor (the middle of the round thing champions cannot enter)"""
    w, h, anchor = 64, 66, (32, 42)
    cx, cy = anchor
    full = blank(w, h)
    for k, (x, y, rx, ry) in enumerate(sorted([(cx - 1, cy - 14, 15, 14), (cx - 14, cy - 3, 11, 10), (cx + 13, cy - 2, 12, 11),
                                               (cx + 1, cy + 4, 9, 7), (cx - 21, cy + 7, 4.5, 3.5), (cx + 22, cy + 8, 4, 3.2)],
                                              key=lambda b: b[1])):
        boulder(full, x, y, rx, ry, 1800 + k)
    ground = cy + 12
    full[ground:, :] = 0
    out = []
    for i, frac in enumerate((0.12, 0.32, 0.56, 0.8, 1.0, 1.0)):
        f = blank(w, h)
        drop = int(round((1 - frac) * 34))
        if drop:
            f[drop:ground] = full[:ground - drop]
        else:
            f[:ground] = full[:ground]
        if i < 5:   # the dust it throws up, thinning as it settles
            dust = ground_ring((h, w), cx, ground - 2, (14, 19, 23, 26, 28)[i], (9, 9, 8, 6, 4)[i], "mountain", 1820 + i,
                               cuts=(0.1, 0.34, 0.6, 0.86, 1.5), squash=0.5)
            f = fx.over(f, dust)
            r2 = np.random.default_rng(1840 + i)
            for _ in range((6, 7, 6, 4, 2)[i]):
                fx.chunk(f, cx + r2.uniform(-24, 24), ground - r2.uniform(4, 26) - i * 2, r2.uniform(1.6, 2.8), r2)
        out.append(f)
    return w, h, anchor, 30, out


def ember():
    """a wall on fire (Infernal rift): a flame that flickers, a spark or two off its top"""
    w, h, anchor = 24, 34, (12, 30)
    out = []
    for i in range(6):
        f = pillar((h, w), anchor[0], anchor[1], (4, 5, 6, 5, 4, 5)[i], (14, 19, 23, 20, 16, 20)[i], "infernal", 1900 + i,
                   strength=(0.9, 1.0, 1.0, 0.95, 0.9, 1.0)[i], cuts=(0.1, 0.3, 0.52, 0.74, 0.9))
        rng = np.random.default_rng(1920 + i)
        sparks(f, rng, anchor[0], anchor[1] - 12, (1, 2, 3, 2, 2, 3)[i], 8, (4, 8, 12, 16, 20, 10)[i], "infernal", r=(0.6, 1.0), k=4)
        out.append(f)
    return w, h, anchor, 6, out


def rain():
    """a tile of the Ocean rift's rain: thin streaks falling down and a little left. It repeats every 128 squares both
    ways; each of its 8 frames is the last one moved on by (-16, 32), a whole tile every 4 and 8 frames"""
    w = h = 128
    rng = np.random.default_rng(2000)
    drops = [(rng.uniform(0, w), rng.uniform(0, h), rng.uniform(4, 8), int(rng.integers(3, 5))) for _ in range(40)]
    out = []
    for i in range(8):
        f = blank(w, h)
        for x, y, ln, k in drops:
            px, py = (x - i * 16) % w, (y + i * 32) % h
            for ox in (-w, 0, w):
                for oy in (-h, 0, h):
                    fx.stroke(f, [(px + ox, py + oy), (px + ox - ln * 0.5, py + oy + ln)], tone("ocean", k), 1)
        out.append(f)
    return w, h, (0, 0), 3, out


def terrain():
    """the elemental rift's pictures, in the sheet's order after the effects"""
    return [("wind_h",) + wind("h"), ("wind_v",) + wind("v"), ("wind_d",) + wind("d"), ("gate",) + gate(),
            ("gate_flash",) + gate_flash(), ("brush_ocean",) + brush("ocean"), ("brush_chem",) + brush("chemtech"),
            ("fruit",) + fruit(), ("fruit_eat",) + fruit_eat(), ("rock",) + rock(), ("ember",) + ember(), ("rain",) + rain()]


def animations():
    """[(name, frame width, frame height, anchor, ticks a frame, frames)] in the sheet's order"""
    out = [("infernal_blast",) + infernal_blast(), ("hex_spark",) + hex_spark(), ("mountain_shield",) + mountain_shield(),
           ("ocean_heal",) + ocean_heal(), ("cloud_gust",) + cloud_gust(), ("chem_rage",) + chem_rage(),
           ("elder_burn",) + elder_burn(), ("elder_execute",) + elder_execute()]
    out += [(f"soul_{el}",) + soul_claim(el) for el in ELEMENTS]
    out += terrain()
    return out


def pack(anims):
    """every animation a row (wrapped when it is wider than the sheet): the sheet and [(name, x, y, w, h, n, per_row,
    ax, ay, ticks)]"""
    rows, y = [], 0
    for name, w, h, anchor, ticks, frames in anims:
        per_row = min(len(frames), SHEET_W // w)
        lines = -(-len(frames) // per_row)
        rows.append((name, 0, y, w, h, len(frames), per_row, anchor[0], anchor[1], ticks))
        y += lines * h
    # as small as the rows need (multiples of 4): the game keeps every sheet it draws in its image cache
    width = -(-max(r[6] * r[3] for r in rows) // 4) * 4
    height = -(-y // 4) * 4
    sheet = np.zeros((height, width, 4), np.uint8)
    for (name, x0, y0, w, h, n, per_row, _, _, _), (_, _, _, _, _, frames) in zip(rows, anims):
        for k, f in enumerate(frames):
            assert f.shape == (h, w, 4), (name, k, f.shape)
            assert set(np.unique(f[..., 3])) <= {0, 255}, f"{name} {k}: half-transparent pixels"
            assert f[..., 3].any(), f"{name} {k}: an empty frame"
            x, yy = x0 + (k % per_row) * w, y0 + (k // per_row) * h
            sheet[yy:yy + h, x:x + w] = f
    return sheet, rows


def runs_of(anims):
    """the frames as runs of equal pixels: b"DFXR", u16 colours, the colours (RGBA), u16 animations, then per animation
    u8 frames and per frame u16 runs and the runs (x, y, width, colour: a byte each, from the frame's top-left)"""
    palette, body = {}, bytearray()
    for name, w, h, anchor, ticks, frames in anims:
        assert w <= 255 and h <= 255 and len(frames) <= 255, name
        body.append(len(frames))
        for f in frames:
            runs = bytearray()
            n = 0
            for y in range(h):
                x = 0
                while x < w:
                    if f[y, x, 3] == 0:
                        x += 1
                        continue
                    c = tuple(int(v) for v in f[y, x, :3])
                    x0 = x
                    while x < w and f[y, x, 3] and tuple(int(v) for v in f[y, x, :3]) == c:
                        x += 1
                    k = palette.setdefault(c, len(palette))
                    assert k <= 255, "more than 256 colours"
                    runs += bytes((x0, y, x - x0, k))
                    n += 1
            body += n.to_bytes(2, "little") + runs
    out = bytearray(b"DFXR") + len(palette).to_bytes(2, "little")
    for c in palette:        # insertion order = index
        out += bytes(c) + bytes([255])
    out += len(anims).to_bytes(2, "little") + body
    return bytes(out)


def table(rows, size):
    lines = [
        "//! Where each of the mod's own battlefield effects is on `effects/league_dragons_fx#sheet.png`.",
        "//! Generated by tools/art/dragons_soul_fx.py - do not edit by hand.",
        "",
        "/// One animation: its frames run left to right from (`x`, `y`), `per_row` to a line, each `w` x `h`; (`ax`, `ay`) is",
        "/// the point of a frame put on the place it plays at (a champion's feet); a frame stays `ticks` simulation ticks.",
        "#[derive(Clone, Copy, Debug, PartialEq, Eq)]",
        "pub struct Anim {",
        "    pub name: &'static str,",
        "    pub x: u16,",
        "    pub y: u16,",
        "    pub w: u16,",
        "    pub h: u16,",
        "    pub frames: u8,",
        "    pub per_row: u8,",
        "    pub ax: u16,",
        "    pub ay: u16,",
        "    pub ticks: u8,",
        "}",
        "",
        f"/// The sheet's size in pixels.",
        f"pub const SHEET: (u16, u16) = ({size[0]}, {size[1]});",
        "",
        f"pub const ANIMS: [Anim; {len(rows)}] = [",
    ]
    for name, x, y, w, h, n, per_row, ax, ay, ticks in rows:
        lines.append(f'    Anim {{ name: "{name}", x: {x}, y: {y}, w: {w}, h: {h}, frames: {n}, per_row: {per_row}, ax: {ax}, '
                     f"ay: {ay}, ticks: {ticks} }},")
    lines.append("];")
    return "\n".join(lines) + "\n"


def preview(anims, path, scale=4):
    """every animation's frames in a row, `scale` x, on the 5v5 map's grass"""
    pad = 4
    W = max(len(f) * (w + pad) for _, w, _, _, _, f in anims) + pad
    H = sum(h + pad for _, _, h, _, _, _ in anims) + pad
    img = np.zeros((H, W, 3), np.uint8)
    img[...] = (58, 92, 52)
    y = pad
    for name, w, h, anchor, ticks, frames in anims:
        for k, f in enumerate(frames):
            x = pad + k * (w + pad)
            cell = img[y:y + h, x:x + w]
            cell[...] = (66, 104, 58) if k % 2 == 0 else (60, 96, 54)
            # a champion-sized dummy (16 x 28) standing on the anchor
            ax, ay = anchor
            cell[max(0, ay - 28):ay, max(0, ax - 8):ax + 8] = (40, 46, 60)
            m = f[..., 3] > 0
            cell[m] = f[m][:, :3]
        y += h + pad
    Image.fromarray(img).resize((W * scale, H * scale), Image.NEAREST).save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview")
    args = ap.parse_args()
    anims = animations()
    sheet, rows = pack(anims)
    text = table(rows, (sheet.shape[1], sheet.shape[0]))
    runs = runs_of(anims)
    if args.preview:
        preview(anims, args.preview)
        print(f"preview: {args.preview}")
        return
    if args.check:
        ok = True
        have = np.asarray(Image.open(SHEET).convert("RGBA")) if os.path.exists(SHEET) else None
        if have is None or have.shape != sheet.shape or not (have == sheet).all():
            print(f"{SHEET} is not what this script draws: run it")
            ok = False
        old = open(TABLE, encoding="utf-8", newline="").read().replace("\r\n", "\n") if os.path.exists(TABLE) else ""
        if old != text:
            print(f"{TABLE} is not what this script writes: run it")
            ok = False
        if not os.path.exists(RUNS) or open(RUNS, "rb").read() != runs:
            print(f"{RUNS} is not what this script writes: run it")
            ok = False
        print("the effects sheet, its table and its runs are up to date" if ok else "out of date")
        sys.exit(0 if ok else 1)
    os.makedirs(os.path.dirname(SHEET), exist_ok=True)
    Image.fromarray(sheet).save(SHEET, optimize=True)
    with open(TABLE, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    with open(RUNS, "wb") as f:
        f.write(runs)
    frames = sum(r[5] for r in rows)
    print(f"{len(rows)} animations, {frames} frames -> {SHEET} ({sheet.shape[1]} x {sheet.shape[0]}), {TABLE}, "
          f"{RUNS} ({len(runs)} bytes)")


if __name__ == "__main__":
    main()
