#!/usr/bin/env python3
"""Size / boldness test, round 2 - local tests only, nothing of this goes into the game (the user, 2026-11-15:
「火箭做的质量太低金克斯的 拉克丝的可以」, then 「不对拉克丝做的也不行 别装进游戏」): three effects drawn by our
own code at PPU 1 (one square a game pixel), bigger, as a pixel artist would - oppi is only the size / richness bar
beside them.

    python -I tools/art/fx_chunky2.py --out C:/t/par_work/vfx_pilot [--root C:/t/inst_bv]

  rocket  league_jinx_big:r_rocket - a NEW shark rocket in our design language (Jinx's purple shark, pink bands):
          4-5 tones a material, a specular streak, a dark outline, an angry eye, teeth in an open jaw, shaded fins,
          metal bands with rivets, a flared nozzle, and a flame drawn anew in every frame (white core, yellow, orange,
          magenta tongues, sparks); the rocket bobs a square
  blast   league_jinx_big:r_blast - the flash, then ONE billowing cloud (a union of puffs that grow from the centre),
          banded by heat (white, yellow, orange, magenta, purple), outlined; it cools and breaks up unevenly as its
          puffs drift apart at different speeds; a ground shockwave out to the kit's 62 px
  beam    league_lux_r:beam - Final Spark as a prismatic beam: white core, pale gold, gold, cyan, blue, pink, magenta
          bands that shimmer frame to frame, sparkle stars and glints along and round it, a charge orb at the wand
          that grows through the telegraph, a rich burst at the far end; the tag's 6 frames
Writes test_<effect>_v2.gif (lanes: ours now (hd_) | new | oppi, game size x4) and test_<effect>_v2.png.
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import vfx_pilot as VP  # noqa: E402
import vfx_pixelfx as F  # noqa: E402

H = F.hexrgb
INK = H("#1C0F2E")                                   # the outline
PURPLE = [H(h) for h in ("#D2C6FF", "#A794F2", "#7E6AD8", "#5D4AB4", "#3E3088", "#2A1F5E")]
BELLY = [H(h) for h in ("#F2EEFF", "#CFC6F4", "#A99CDE")]
PINK = [H(h) for h in ("#FFD2EC", "#FF8ACB", "#E8549E", "#A82E6E")]
METAL = [H(h) for h in ("#E6E8F8", "#AEB4D6", "#7C82AC", "#555A82", "#363A5C")]
MOUTH = [H(h) for h in ("#7A1838", "#4E0E26", "#2A0614")]
TOOTH = [H(h) for h in ("#FFFFFF", "#D8D4EC", "#9C96BE")]
EYE = [H(h) for h in ("#FFF4B0", "#FFD23C", "#E89A1E")]
FIRE = [H(h) for h in ("#FFFFFF", "#FFF4A8", "#FFD23C", "#FF9A2A", "#F2582E", "#E0306A", "#9A1E5A")]
OUTLINE = H("#2E0E36")
SMOKE = [H(h) for h in ("#C2A8C6", "#94789E", "#66507A", "#3E2E52")]
LUX = [H(h) for h in ("#FFFFFF", "#FFF8D8", "#FFE680", "#FFC933", "#F2A22A")]
PRISM = [H(h) for h in ("#8EF0FF", "#4AA8FF", "#FF9AD8", "#E04AB0", "#B48CFF")]


def crop_centre(img, cx, cy):
    """crop round pixel (cx, cy) - the anchor - to the smallest odd frame holding every drawn pixel."""
    a = img[..., 3] > 0
    if not a.any():
        return np.zeros((1, 1, 4), np.uint8)
    ys, xs = np.nonzero(a)
    ex = int(max(abs(xs.min() - cx), abs(xs.max() - cx)))
    ey = int(max(abs(ys.min() - cy), abs(ys.max() - cy)))
    out = np.zeros((2 * ey + 1, 2 * ex + 1, 4), np.uint8)
    y0, x0 = cy - ey, cx - ex
    sy0, sx0 = max(y0, 0), max(x0, 0)
    sy1, sx1 = min(cy + ey + 1, img.shape[0]), min(cx + ex + 1, img.shape[1])
    out[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = img[sy0:sy1, sx0:sx1]
    return out


def outline_of(mask):
    p = np.pad(mask, 1)
    return (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~mask


def tri(pix, pts):
    """a filled triangle (pixel centres inside)."""
    (ax, ay), (bx, by), (cx, cy) = pts
    gx, gy = pix.xx + 0.5, pix.yy + 0.5
    d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(d) < 1e-9:
        return np.zeros_like(gx, bool)
    l0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / d
    l1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / d
    return (l0 >= -0.02) & (l1 >= -0.02) & (1 - l0 - l1 >= -0.02)


# ----------------------------------------------------------------------------- the rocket
L, HH = 92, 15.0                                     # body length (tail to nose) and half height, game px


def _profile(u):
    """top and bottom of the body (as fractions of HH, up negative) at u = 0 (tail) .. 1 (snout)."""
    rise = np.sin(np.clip(u / 0.45, 0, 1) * math.pi / 2)
    snout_t = np.sqrt(np.clip(1 - np.clip((u - 0.62) / 0.38, 0, 1) ** 2.3, 0, 1))
    snout_b = np.sqrt(np.clip(1 - np.clip((u - 0.6) / 0.4, 0, 1) ** 1.7, 0, 1))
    top = np.where(u < 0.45, -(0.62 + 0.38 * rise), np.where(u < 0.62, -1.0, -(0.22 + 0.78 * snout_t)))
    bot = np.where(u < 0.45, 0.62 + 0.38 * rise, np.where(u < 0.6, 1.0, 0.12 + 0.88 * snout_b))
    return top, bot


def draw_rocket(pix, x0, cy, frame):
    """the rocket with its tail at x0, its axis on row cy; returns the nose's pixel (the anchor)."""
    gx = pix.xx + 0.5
    gy = pix.yy + 0.5
    u = (gx - x0) / L
    top, bot = _profile(u)
    t_px, b_px = cy + top * HH, cy + bot * HH
    body = (u >= 0) & (u <= 1) & (gy >= t_px) & (gy <= b_px)
    half = np.maximum((b_px - t_px) / 2, 1e-3)
    v = (gy - (t_px + b_px) / 2) / half                  # -1 top .. 1 bottom across the body
    # ---- fins (under the body's outline, over the flame): dorsal, tail stabilisers, the near pectoral
    fins = np.zeros_like(body)
    fin_shade = []
    dors = tri(pix, [(x0 + 0.40 * L, cy - HH + 1), (x0 + 0.60 * L, cy - HH + 1), (x0 + 0.36 * L, cy - HH - 13)])
    tail_t = tri(pix, [(x0 + 0.02 * L, cy - 0.6 * HH), (x0 + 0.18 * L, cy - 0.8 * HH), (x0 - 4, cy - HH - 9)])
    tail_b = tri(pix, [(x0 + 0.02 * L, cy + 0.6 * HH), (x0 + 0.18 * L, cy + 0.8 * HH), (x0 - 4, cy + HH + 9)])
    pect = tri(pix, [(x0 + 0.46 * L, cy + 0.55 * HH), (x0 + 0.62 * L, cy + 0.7 * HH), (x0 + 0.40 * L, cy + HH + 10)])
    for m, light_side in ((dors, -1), (tail_t, -1), (tail_b, 1), (pect, 1)):
        fins |= m
        fin_shade.append((m, light_side))
    # ---- nozzle: a flared metal bell behind the tail
    nz = (gx >= x0 - 8) & (gx < x0 + 1)
    nz_h = HH * (0.56 + 0.22 * np.clip((x0 - gx) / 8, 0, 1))
    nozzle = nz & (np.abs(gy - cy) <= nz_h)
    whole = body | fins | nozzle
    # outline first (on empty pixels), then the parts
    pix.paint(outline_of(whole), INK)
    for m, side in fin_shade:
        # fins: light along their leading edge, deep at the tips (tones by distance from the body)
        dist = np.abs(gy - cy) / HH
        pix.paint(m, PURPLE[3])
        pix.paint(m & (dist < 1.25), PURPLE[2])
        pix.paint(m & (dist > 1.55), PURPLE[4])
        edge = m & ~np.roll(m, 1, axis=1)               # the fin's front edge catches the light
        pix.paint(edge, PURPLE[1])
    pix.paint(nozzle, METAL[2])
    pix.paint(nozzle & (gy - cy < -0.25 * nz_h), METAL[1])
    pix.paint(nozzle & (gy - cy < -0.6 * nz_h), METAL[0])
    pix.paint(nozzle & (gy - cy > 0.45 * nz_h), METAL[3])
    pix.paint(nozzle & (gx < x0 - 6.5), METAL[4])            # the rim
    rings = nozzle & ((np.floor(gx).astype(int) - int(x0)) % 4 == 0) & (np.abs(gy - cy) > nz_h - 2)
    pix.paint(rings, METAL[0])                               # rivets on the bell
    # ---- the body, 5 tones round the cylinder + the belly
    # the tone boundaries bend with the body (a cylinder narrowing to the snout), not straight stripes
    vb = v - 0.18 * np.clip((u - 0.55) / 0.45, 0, 1) ** 2 + 0.12 * np.clip((0.3 - u) / 0.3, 0, 1)
    tone = np.digitize(vb, [-0.62, -0.18, 0.32, 0.72])     # 0 highlight .. 4 deep
    for k, c in enumerate(PURPLE[:5]):
        pix.paint(body & (tone == k), c)
    # reflected light along the belly's edge (a pixel artist's rim light)
    rim = body & (v > 0.86) & (u > 0.12) & (u < 0.72)
    pix.paint(rim, PURPLE[2])
    belly = body & (u > 0.5) & (v > 0.15)
    pix.paint(belly, BELLY[2])
    pix.paint(belly & (v < 0.55), BELLY[1])
    pix.paint(belly & (v < 0.35) & (u > 0.62), BELLY[0])
    # specular: a streak along the top, a hot spot
    spec = body & (np.abs(v + 0.74) < 0.09) & (u > 0.24) & (u < 0.66)
    pix.paint(spec, PURPLE[0])
    pix.paint(body & (np.abs(v + 0.74) < 0.12) & (np.abs(u - 0.55) < 0.025), H("#FFFFFF"))
    # pink bands with their seams and rivets
    for b0, b1 in ((0.20, 0.25), (0.29, 0.34)):
        band = body & (u >= b0) & (u < b1)
        bt = np.digitize(v, [-0.5, 0.25, 0.7])
        for k, c in enumerate(PINK):
            pix.paint(band & (bt == k), c)
        seam = body & ((np.abs(u - b0) * L < 0.6) | (np.abs(u - b1) * L < 0.6))
        pix.paint(seam, PURPLE[5])
        mid = (b0 + b1) / 2
        riv = band & (np.abs(u - mid) * L < 0.6) & ((np.floor(gy).astype(int) % 4) == 0) & (np.abs(v) < 0.85)
        pix.paint(riv, PINK[0])
    # the jaw: an open mouth under the snout, teeth top and bottom
    mx0, mx1 = x0 + 0.76 * L, x0 + L - 1
    mu = (gx - mx0) / (mx1 - mx0)
    m_top = cy + 0.05 * HH + (1 - mu) * 0.08 * HH
    m_bot = cy + 0.55 * HH * np.clip(1 - mu, 0, 1) ** 0.8 + 0.08 * HH
    mouth = body & (gx >= mx0) & (gx <= mx1) & (gy >= m_top) & (gy <= m_bot)
    pix.paint(outline_of(mouth) & body, INK)
    pix.paint(mouth, MOUTH[0])
    pix.paint(mouth & (gy > m_top + 2), MOUTH[1])
    pix.paint(mouth & (gy > (m_top + m_bot) / 2 + 1) & (gx < mx0 + 0.55 * (mx1 - mx0)), MOUTH[2])
    teeth = np.zeros_like(mouth)
    xs_t = np.arange(int(mx0) + 1, int(mx1) - 1, 3)
    for tx in xs_t:
        ut = (tx + 0.5 - mx0) / (mx1 - mx0)
        ty = cy + 0.05 * HH + (1 - ut) * 0.08 * HH
        by_ = cy + 0.55 * HH * max(0.0, 1 - ut) ** 0.8 + 0.08 * HH
        teeth |= tri(pix, [(tx - 1.0, ty), (tx + 2.0, ty), (tx + 0.5, ty + 3.2)])          # upper, pointing down
        if by_ - ty > 5:
            teeth |= tri(pix, [(tx + 0.5, by_), (tx + 3.0, by_), (tx + 1.8, by_ - 2.8)])    # lower, pointing up
    teeth &= mouth
    pix.paint(teeth, TOOTH[0])
    pix.paint(teeth & (np.roll(teeth, -1, axis=1) == 0), TOOTH[1])                       # shaded right side
    # the eye: yellow, pupil forward, a glint, an angry brow
    ex, ey = x0 + 0.80 * L, cy - 0.42 * HH
    eye = pix.ellipse_mask(ex, ey, 3.2, 2.5) & body
    pix.paint(outline_of(eye) & body, INK)
    pix.paint(eye, EYE[1])
    pix.paint(eye & (pix.yy + 0.5 < ey - 0.4), EYE[0])
    pupil = pix.ellipse_mask(ex + 1.3, ey + 0.4, 1.3, 1.4) & eye
    pix.paint(pupil, INK)
    pix.paint(pix.ellipse_mask(ex - 0.8, ey - 0.8, 0.5, 0.5) & eye, H("#FFFFFF"))
    brow = body & (np.abs((gy - (ey - 3.6)) - 0.45 * (gx - ex)) < 0.9) & (np.abs(gx - ex) < 4.5)
    pix.paint(brow, INK)
    # gill slits behind the eye
    for k in range(3):
        gxk = x0 + (0.66 - 0.035 * k) * L
        slit = body & (np.abs(gx - gxk - 0.25 * (gy - cy)) < 0.55) & (v > -0.45) & (v < 0.25)
        pix.paint(slit, PURPLE[4])
    return int(round(x0 + L)) - 1


def draw_flame(pix, xn, cy, frame, rng):
    """the exhaust: tongues of fire behind the nozzle at xn, every frame a new shape."""
    gx = pix.xx + 0.5
    gy = pix.yy + 0.5
    base = [52, 44, 58, 48][frame % 4]
    layers = ((FIRE[6], 1.00, 1.00), (FIRE[5], 0.92, 0.86), (FIRE[4], 0.80, 0.72), (FIRE[3], 0.66, 0.58),
              (FIRE[2], 0.50, 0.44), (FIRE[1], 0.34, 0.30), (FIRE[0], 0.20, 0.17))
    ph = rng.random(4) * 6.28
    for col, wf, lf in layers:
        ln = base * lf
        d = xn - gx                                          # distance behind the nozzle
        hw = 10.5 * wf * np.clip(1 - d / max(ln, 1), 0, 1) ** 0.6
        # tongues: the edge breaks into flicking points along its length
        tongue = 1 + 0.28 * np.sin(d * 0.55 + ph[0]) + 0.16 * np.sin(d * 1.3 + ph[1])
        off = 1.2 * np.sin(d * 0.21 + ph[2])
        m = (d >= -1) & (d <= ln) & (np.abs(gy - cy - off) <= hw * tongue)
        pix.paint(m, col)
    for s in range(9):                                       # sparks and embers thrown back
        sx = xn - base * (0.4 + 0.9 * rng.random())
        sy = cy + rng.normal() * 6
        r = 0.5 if rng.random() < 0.7 else 1.0
        pix.paint(pix.ellipse_mask(sx, sy, r, r), FIRE[1 + int(rng.integers(0, 4))])


def rocket_frames(n=4):
    out = []
    for k in range(n):
        W, Hh = 220, 70
        pix = F.Pix(W, Hh)
        cy = 34 + [0, 1, 0, -1][k % 4]                       # a one-square bob
        x0 = 78
        rng = np.random.default_rng(90 + k)
        draw_flame(pix, x0 - 8, cy + 0.5, k, rng)
        nose = draw_rocket(pix, x0, cy + 0.5, k)
        out.append(crop_centre(pix.img, nose, 34))
    return out


# ----------------------------------------------------------------------------- the blast: one cloud
def blast_frames(n=8):
    """frame 0 the flash; then one cloud of puffs: each puff a circle that grows from near the centre outward and later
    drifts off at its own speed and shrinks, so the cloud billows and then breaks up unevenly; colour by heat (how far
    in the cloud and how late)."""
    W = Hh = 241
    cx = cy = 120
    gy0 = cy + 12
    rng = np.random.default_rng(23)
    P = 26
    ang = rng.random(P) * 6.28
    dist = np.sqrt(rng.random(P)) * 0.9                     # where in the ball (0 centre .. 1 rim)
    size = 0.35 + 0.3 * rng.random(P)
    drift = np.stack([np.cos(ang), np.sin(ang) * 0.8 - 0.6], 1) * (0.5 + rng.random((P, 1)))
    out = []
    for k in range(n):
        pix = F.Pix(W, Hh)
        bx, by = cx + 0.5, cy - 8 + 0.5
        if k <= 3:
            rr = [32, 50, 62, 66][k]
            cols = [[FIRE[0], FIRE[1], FIRE[2]], [FIRE[1], FIRE[2], FIRE[3]], [FIRE[2], FIRE[3], FIRE[4]],
                    [FIRE[4], FIRE[5]]][k]
            pix.ring(cx + 0.5, gy0 + 0.5, rr, rr * 0.5, [5, 4, 3, 2][k], cols)
        if k == 0:
            pix.star(bx, by, 40, [FIRE[0], FIRE[2]])
            pix.dot(bx, by, 22, [FIRE[3], FIRE[2], FIRE[1], FIRE[0]])
            out.append(crop_centre(pix.img, cx, cy))
            continue
        R = [0, 32, 44, 48, 48, 46, 42, 38][k]                 # the cloud's reach
        t = (k - 1) / (n - 2)                                   # 0 .. 1 over the cloud's life
        split = max(0.0, (k - 3) / (n - 4))                     # 0 until it starts breaking
        heat = max(0.0, 1.1 - 1.25 * t)
        mask = np.zeros((Hh, W), bool)
        gx, gyy = pix.xx + 0.5, pix.yy + 0.5
        light = np.full((Hh, W), -9.0)                         # each puff lit from up-left (for the smoke's tones)
        for i in range(P):
            px_ = bx + math.cos(ang[i]) * dist[i] * R + drift[i, 0] * split * 46
            py_ = by + math.sin(ang[i]) * dist[i] * R * 0.85 + drift[i, 1] * split * 40 - 10 * split
            pr = R * size[i] * (1 - 0.55 * split * (0.5 + size[i]))
            if pr < 2.5:
                continue
            m = np.hypot(gx - px_, (gyy - py_) / 0.92) <= pr
            mask |= m
            lit = -((gyy - py_) * 0.75 + (gx - px_) * 0.45) / pr
            light = np.where(m, np.maximum(light, lit), light)
        if not mask.any():
            out.append(np.zeros((1, 1, 4), np.uint8))
            continue
        pix.paint(outline_of(mask), OUTLINE)
        # heat: one field for the whole cloud - hottest at its (rising) heart, cooling outward and with time - so the
        # bands run round the cloud as a fireball's do; a little noise keeps the rings ragged
        hy = by - 14 * t
        noise = 0.07 * np.sin(gx * 0.31 + k) * np.sin(gyy * 0.27 - k)
        heatmap = heat * np.clip(1 - np.hypot(gx - bx, (gyy - hy) / 0.9) / (R * 1.05), 0, 1) ** 0.75 + noise
        heatmap = heatmap + 0.12 * np.clip(light, -1, 1) * heat
        ramp = [FIRE[6], FIRE[5], FIRE[4], FIRE[3], FIRE[2], FIRE[1], FIRE[0]]
        cuts = [-9, 0.1, 0.22, 0.36, 0.52, 0.68, 0.85]
        for c, lo in zip(ramp, cuts):
            pix.paint(mask & (heatmap >= lo), c)
        if heat < 0.35:                                         # cooling: the outer parts turn to shaded smoke
            smoke = mask & (heatmap < 0.1)
            pix.paint(smoke, SMOKE[2])
            pix.paint(smoke & (light > 0.25), SMOKE[1])
            pix.paint(smoke & (light > 0.6), SMOKE[0])
            pix.paint(smoke & (light < -0.35), SMOKE[3])
        for s in range(12):                                     # embers
            ex_ = bx + rng.integers(-80, 81)
            ey_ = by + rng.integers(-70, 40) - 6 * k
            pix.paint(pix.ellipse_mask(ex_, ey_, 0.5, 0.5), FIRE[2 + (s + k) % 3])
        out.append(crop_centre(pix.img, cx, cy))
    return out


# ----------------------------------------------------------------------------- the beam
def beam_frames(durs):
    W, Hh = 401, 121                                             # room for the wand's flare left of the caster
    cx, cy = 200, 60
    x0, x1 = cx - 170 + 24, cx + 168
    phases = ["charge1", "charge2", "ignite", "beam1", "beam2", "fade"][:len(durs)]
    out = []
    for k, ph in enumerate(phases):
        pix = F.Pix(W, Hh)
        rng = np.random.default_rng(171 + k)
        xs = np.arange(W)
        wob = (1.3 * np.sin(xs * 0.19 + k * 1.7) + 0.9 * np.sin(xs * 0.47 + k * 0.9)).round().astype(int)
        cyc = np.sin(xs * 0.045 + k * 1.1)                       # the rainbow's bands swap along the beam
        inside = (pix.xx >= x0) & (pix.xx <= x1)
        dy = np.abs(pix.yy - cy)

        def band(half, col, flick=True, mask=None):
            w = half + (wob[pix.xx] if flick and half > 2 else 0)
            m = inside & (dy <= w)
            if mask is not None:
                m &= mask
            pix.paint(m, col)

        def sparkles(nst, reach, cols):
            for s in range(nst):
                sx = x0 + 18 + rng.integers(0, x1 - x0 - 18)
                sy = cy + rng.integers(-reach, reach + 1)
                if rng.random() < 0.35:
                    pix.star(sx + 0.5, sy + 0.5, int(rng.integers(2, 5)), [cols[0], cols[1]])
                else:
                    pix.paint(pix.ellipse_mask(sx + 0.5, sy + 0.5, 0.5, 0.5), cols[s % len(cols)])

        def orb(r, star):
            pix.star(x0 + 0.5, cy + 0.5, star, [LUX[0], LUX[3]])
            for a in (0.785, 2.356):                              # short diagonal rays
                for sgn in (1, -1):
                    for d in range(2, int(star * 0.45)):
                        px_ = x0 + 0.5 + math.cos(a) * d * sgn
                        py_ = cy + 0.5 + math.sin(a) * d * sgn
                        pix.paint(pix.ellipse_mask(px_, py_, 0.5, 0.5), LUX[2])
            pix.ring(x0 + 0.5, cy + 0.5, r + 2, r + 2, 2, [PRISM[0], PRISM[2]])
            pix.dot(x0 + 0.5, cy + 0.5, r, [LUX[3], LUX[2], LUX[1], LUX[0]])

        if ph == "charge1":
            pix.paint(inside & (dy == 0) & ((pix.xx // 3) % 2 == 0), LUX[3])     # a dotted telegraph line
            orb(5, 9)
            for s in range(8):
                a = rng.random() * 6.28
                d = 9 + rng.integers(0, 10)
                pix.paint(pix.ellipse_mask(x0 + math.cos(a) * d, cy + math.sin(a) * d * 0.8, 0.5, 0.5), LUX[2])
        elif ph == "charge2":
            band(1, LUX[3], False)
            pix.paint(inside & (dy == 0), LUX[0])
            orb(10, 18)
            for s in range(16):                                   # motes rushing into the orb
                a = rng.random() * 6.28
                d = 12 + rng.integers(0, 16)
                p0 = (x0 + math.cos(a) * d, cy + math.sin(a) * d * 0.8)
                p1 = (x0 + math.cos(a) * (d - 4), cy + math.sin(a) * (d - 4) * 0.8)
                pix.line(p0, p1, 1, [PRISM[s % 5], LUX[1]])
        elif ph == "ignite":
            band(20, PRISM[1], False)
            band(18, LUX[2], False)
            band(14, LUX[1], False)
            band(10, LUX[0], False)
            orb(20, 50)
            sparkles(30, 26, [LUX[0], LUX[1], PRISM[0], PRISM[2]])
        elif ph in ("beam1", "beam2"):
            b2 = ph == "beam2"
            # the prismatic edges: magenta / pink / blue / cyan, their order rolling along the beam
            warm = cyc > 0
            band(17, PRISM[3], mask=warm)
            band(17, PRISM[4], mask=~warm)
            band(15, PRISM[2], mask=warm)
            band(15, PRISM[1], mask=~warm)
            band(13, PRISM[0])
            band(11, LUX[4])
            band(9, LUX[3])
            band(7, LUX[2])
            band(5 if b2 else 6, LUX[1])
            band(3 if b2 else 4, LUX[0], False)
            # glints riding the core
            for s in range(10):
                gxk = x0 + 20 + rng.integers(0, x1 - x0 - 30)
                pix.paint((pix.xx >= gxk) & (pix.xx < gxk + int(rng.integers(3, 9))) & (dy == int(rng.integers(0, 3))),
                          H("#FFFFFF"))
            sparkles(36, 30, [LUX[0], LUX[1], PRISM[0], PRISM[2], PRISM[4]])
            orb(15 if not b2 else 13, 36 if not b2 else 30)
            # the far end: a burst of rays and a banded flare
            ex_ = x1 - 4
            pix.star(ex_ + 0.5, cy + 0.5, 22 if not b2 else 18, [LUX[0], PRISM[1]])
            pix.dot(ex_ + 0.5, cy + 0.5, 11 if not b2 else 9, [PRISM[2], LUX[2], LUX[1], LUX[0]])
            for s in range(10):
                a = (rng.random() - 0.5) * 2.2
                d = 14 + rng.integers(0, 16)
                p1 = (ex_ + math.cos(a) * d, cy + math.sin(a) * d)
                pix.line((ex_ + math.cos(a) * (d - 5), cy + math.sin(a) * (d - 5)), p1, 1, [PRISM[s % 5], LUX[1]])
        else:                                                     # fading: a thinning, breaking beam, sparkles left
            gaps = ((pix.xx // 19 + k) % 4) != 0
            band(6, PRISM[1], False, gaps)
            band(4, LUX[3], False, gaps)
            band(2, LUX[1], False, gaps)
            pix.paint(inside & gaps & (dy == 0), LUX[0])
            orb(6, 12)
            sparkles(30, 20, [LUX[1], LUX[2], PRISM[0], PRISM[2], PRISM[4]])
        out.append(crop_centre(pix.img, cx, cy))
    return out


# ----------------------------------------------------------------------------- run
def texels(frames):
    return int(sum(f.shape[0] * f.shape[1] for f in frames))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    here = os.path.isdir(os.path.join(ROOT, "league", "effects"))
    ap.add_argument("--root", default=ROOT if here else r"C:\t\inst_bv", help="a tree with league/effects")
    ap.add_argument("--oppi", default=VP.OPPI)
    ap.add_argument("--only", nargs="*", default=["rocket", "blast", "beam"])
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    jobs = {"rocket": ("jinx_r_rocket", "league_jinx_big", "r_rocket", {"path": "fx/jinxult.aseprite", "tag": "ult"}),
            "blast": ("jinx_r_blast", "league_jinx_big", "r_blast",
                      {"path": "effects/jinxultexplosion.aseprite", "tag": "explode"}),
            "beam": ("lux_r_beam", "league_lux_r", "beam", {"path": "effects/luxult.aseprite", "tag": "ult"})}
    for key in a.only:
        name, sheet, tag, op = jobs[key]
        d, im = VP.load_fanim(a.root, sheet)
        now1 = VP.tag_frames(d, im, tag)
        nowh = VP.tag_frames(d, im, "hd_" + tag)
        durs = [dd for _, dd in now1]
        frames = {"rocket": lambda: rocket_frames(len(durs)), "blast": lambda: blast_frames(len(durs)),
                  "beam": lambda: beam_frames(durs)}[key]()
        test = [(f, dd) for f, dd in zip(frames, durs)]
        ofr = VP.oppi_frames(op, a.oppi)
        lanes = [("ours now (hd_)", nowh, 2, VP.extent(nowh, 2)),
                 ("new (PPU 1, our code)", test, 4, VP.extent(test, 4)),
                 (f"oppi ({os.path.basename(op['path'])}, the bar)", ofr or [], 4,
                  VP.extent(ofr, 4) if ofr else (40, 40))]
        bw = max(b[0] for *_, b in lanes)
        bh = max(b[1] for *_, b in lanes)
        lanes = [(t, fr, z, (bw, bh)) for t, fr, z, _b in lanes]
        total = sum(durs)
        reps = max(1, int(round(1.2 / total))) if total < 0.6 else 1
        block = VP.Block(f"{name} v2: {sheet}:{tag} ({len(durs)} frames, {total:.2f} s)", lanes, bw > 1.6 * bh)
        VP.write_gif(os.path.join(a.out, f"test_{name}_v2.gif"), [block], total * reps)
        VP.strip_png(os.path.join(a.out, f"test_{name}_v2.png"), test, 4)
        t_now = texels([f for f, _ in now1]) + texels([f for f, _ in nowh])
        t1 = texels(frames)
        print(f"{name}: texels now (1x + hd_) {t_now}, v2 1x only {t1} ({t1 / t_now:.0%}); sizes "
              f"{sorted({(f.shape[1], f.shape[0]) for f in frames})[-3:]}")


if __name__ == "__main__":
    main()
