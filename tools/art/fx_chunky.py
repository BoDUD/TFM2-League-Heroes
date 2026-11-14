#!/usr/bin/env python3
"""Size / boldness test for three effects (the coordinator's 2026-11-15 hypothesis: most of the gap to oppi is size,
thickness and brightness): drawn by our own code at PPU 1 - chunky game-pixel squares, bigger - instead of fine PPU 2
on small pictures. oppi is a size reference only; nothing of his is drawn here.

    python -I tools/art/fx_chunky.py --out C:/t/par_work/vfx_pilot [--root C:/t/inst_bv]

  league_jinx_big:r_rocket  our shark rocket from its own hd_ frames shown as 1x (twice the size, one square a game
                            pixel), a dark outline round the body, a bigger, brighter, flickering flame
  league_jinx_big:r_blast   a big bright fireball: a flash, then a banded ball (white core, yellow, orange, magenta,
                            dark purple outline) that billows and breaks into puffs, a shockwave ring at the kit's
                            62 px radius on the ground; the tag's 8 x 70 ms (League: flash 0-0.3 s, fire to ~0.6 s)
  league_lux_r:beam         a beam as thick as oppi's (33 px): white core, pale / gold / orange bands, a one-square
                            prismatic fringe, a flare at the wand and a burst at the far end, edges flickering between
                            frames; the tag's 6 frames (charge 0.47 s = League's 1 s, the beam, the fade)
Writes test_<effect>.gif (lanes: ours now (hd_) | test | oppi, game size x4) and test_<effect>.png strips to --out,
and prints the texels of each tag now (1x + hd_) and as tested (1x only: the sheet left out of fx_ppu.rs; or 1x plus
a 2x nearest hd_ twin if it stays registered). Our art and the generated frames stay local until the user decides.
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
FIRE = [H(h) for h in ("#FFFFFF", "#FFF4A8", "#FFD23C", "#FF9A2A", "#F2582E", "#E0306A", "#9A1E5A")]
OUTLINE = H("#2E0E36")
SMOKE = [H(h) for h in ("#B49AB8", "#8A6E96", "#5E4A70", "#3A2A4A")]
LUX = [H(h) for h in ("#FFFFFF", "#FFF8D8", "#FFE680", "#FFC933", "#F2A22A")]
PRISM = [H(h) for h in ("#A8F0FF", "#FFB8E8", "#D2B8FF")]


def crop_centre(img, cx, cy):
    """crop round (cx, cy) - the anchor, the centre of a pixel - to the smallest odd frame holding every drawn pixel."""
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


def lumpy(pix, cx, cy, r, squash, lobes, seed, amp=0.12):
    """a billowing cloud of radius r: a core disc and `lobes` round puffs on its rim (a fire cloud's edge is a chain
    of bumps, not a star's points), y squashed."""
    rng = np.random.default_rng(seed)
    gx = pix.xx + 0.5 - cx
    gy = (pix.yy + 0.5 - cy) / max(squash, 1e-3)
    m = np.hypot(gx, gy) <= r * 0.78
    a0 = rng.random() * 6.28
    for i in range(lobes):
        a = a0 + i * 6.28 / lobes + rng.uniform(-0.25, 0.25)
        d = r * rng.uniform(0.5, 0.62)
        pr = r * (0.36 + amp * rng.uniform(0.5, 1.5))
        m |= np.hypot(gx - d * math.cos(a), gy - d * math.sin(a)) <= pr
    return m


def banded_ball(pix, cx, cy, r, colours, seed, squash=0.92, lobes=7, outline=True, core_shift=(-0.18, -0.2),
                hot=1.0):
    """a fireball: a lumpy disc in bands (outer colour first), each band smaller and pulled up-left, and a dark
    outline round the whole; hot > 1 widens the inner (white / yellow) bands - the white-hot peak."""
    n = len(colours)
    outer = lumpy(pix, cx, cy, r, squash, lobes, seed)
    if outline:
        p = np.pad(outer, 1)
        ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~outer
        pix.paint(ring, OUTLINE)
    for i, c in enumerate(colours):
        k = 1 - (i / n) ** hot
        m = lumpy(pix, cx + core_shift[0] * r * (1 - k), cy + core_shift[1] * r * (1 - k), r * k, squash, lobes,
                  seed + i, amp=0.12 + 0.03 * i) & outer
        pix.paint(m, c)


# ----------------------------------------------------------------------------- the rocket
def rocket(hd_frames):
    """our hd_ shark rocket shown as 1x (twice as big, one square a game pixel): outlined, a bigger flickering flame."""
    out = []
    for k, (f, _d) in enumerate(hd_frames):
        h0, w0 = f.shape[:2]
        tail = 70                                            # room for the flame behind the body
        W, Hh = w0 + 2 * tail, h0 + 16
        pix = F.Pix(W, Hh)
        ox, oy = tail, 8
        body = np.zeros((Hh, W), bool)
        body[oy:oy + h0, ox:ox + w0] = f[..., 3] > 0
        ys, xs = np.nonzero(body)
        x_tail = xs.min()
        rows = ys[xs < x_tail + 6]
        cy = (rows.min() + rows.max()) / 2.0 + 0.5 if len(rows) else (oy + h0 / 2)
        # the flame: tapering banded lobes behind the tail, its length flickering frame to frame
        rng = np.random.default_rng(31 + k)
        L = 46 + 10 * math.sin(k * 1.9) + rng.integers(0, 6)
        for j, (col, wfrac, lfrac) in enumerate(((FIRE[5], 1.0, 1.0), (FIRE[3], 0.78, 0.82), (FIRE[2], 0.55, 0.62),
                                                 (FIRE[1], 0.34, 0.42), (FIRE[0], 0.18, 0.24))):
            hw = 11 * wfrac
            ln = L * lfrac
            gx = (x_tail + 2) - (pix.xx + 0.5)
            gy = pix.yy + 0.5 - cy
            prof = hw * np.clip(1 - gx / max(ln, 1), 0, 1) ** 0.7 * (1 + 0.18 * np.sin(gx * 0.9 + k * 2.1 + j))
            m = (gx >= -2) & (gx <= ln) & (np.abs(gy) <= prof)
            pix.paint(m, col)
        for s in range(6):                                   # sparks shed by the flame
            sx = x_tail - 10 - rng.integers(0, int(L))
            sy = cy + rng.integers(-12, 13)
            pix.paint(pix.ellipse_mask(sx, sy, 0.5, 0.5), FIRE[1 + s % 3])
        # the body over the flame, then its outline
        blk = pix.img[oy:oy + h0, ox:ox + w0]
        m = f[..., 3] > 0
        blk[m] = f[m]
        pix.outline(body, OUTLINE)
        anchor_x, anchor_y = ox + (w0 - 1) // 2 + (w0 % 2 == 0) * 0, oy + (h0 - 1) // 2
        out.append(crop_centre(pix.img, anchor_x + (1 if w0 % 2 == 0 else 0), anchor_y + (1 if h0 % 2 == 0 else 0)))
    return out


# ----------------------------------------------------------------------------- the blast
def blast(n=8):
    """the explosion, frame by frame (0-7: flash, ball forming, full billow, rising, breaking, puffs, smoke, wisps);
    the anchor at the canvas centre, the ground 12 px under it, the ball's centre 6 px over it."""
    W = Hh = 221
    cx = cy = 110
    gy = cy + 12
    out = []
    for k in range(n):
        pix = F.Pix(W, Hh)
        bx, by = cx + 0.5, cy - 6 + 0.5
        if k <= 3:                                            # the shockwave on the ground: out to the kit's 62 px
            rr = [30, 48, 60, 66][k]
            cols = [[FIRE[0], FIRE[1], FIRE[2]], [FIRE[1], FIRE[2], FIRE[3]], [FIRE[2], FIRE[3], FIRE[4]],
                    [FIRE[4], FIRE[5]]][k]
            pix.ring(cx + 0.5, gy + 0.5, rr, rr * 0.5, [4, 4, 3, 2][k], cols)
        if k == 0:                                            # the flash
            pix.star(bx, by, 34, [FIRE[0], FIRE[2]])
            pix.dot(bx, by, 20, [FIRE[2], FIRE[1], FIRE[0]])
        elif k in (1, 2, 3):                                  # the ball billows
            r = [34, 46, 48][k - 1]
            lift = [0, 2, 8][k - 1]
            banded_ball(pix, bx, by - lift, r, FIRE[6:0:-1] + [FIRE[0]] if k < 3 else FIRE[6:1:-1], seed=11 + k,
                        hot=[1.8, 1.5, 1.1][k - 1])
            if k == 1:
                pix.star(bx, by - lift, 44, [FIRE[0], FIRE[2]])
        else:                                                 # it breaks into puffs that rise, shrink and darken
            rng = np.random.default_rng(5)
            puffs = [(-30, -10, 20), (28, -14, 19), (0, -38, 22), (-18, 16, 15), (22, 18, 14), (-40, -34, 12),
                     (40, -36, 12)]
            step = k - 4
            for i, (dx, dy, r0) in enumerate(puffs):
                spread = 1 + 0.22 * step
                px_ = bx + dx * spread
                py_ = by + dy * spread - 7 * step
                r = r0 * (1 - 0.17 * step) + rng.integers(-1, 2)
                if r < 3:
                    continue
                if step == 0:
                    cols = FIRE[6:1:-1]
                elif step == 1:
                    cols = [FIRE[6], FIRE[5], FIRE[4], FIRE[3]]
                elif step == 2:
                    cols = [SMOKE[3], SMOKE[2], FIRE[6], FIRE[5]]
                else:
                    cols = [SMOKE[3], SMOKE[2], SMOKE[1]]
                banded_ball(pix, px_, py_, r, cols, seed=40 + i + 7 * step, lobes=5)
            for s in range(10):                               # embers
                ex = bx + rng.integers(-70, 71)
                ey = by + rng.integers(-60, 30) - 6 * step
                pix.paint(pix.ellipse_mask(ex, ey, 0.5, 0.5), FIRE[2 + (s + step) % 3])
        out.append(crop_centre(pix.img, cx, cy))
    return out


# ----------------------------------------------------------------------------- the beam
def beam(durs):
    """Final Spark: the caster 170 px left of the frame's centre, the beam from her wand (24 px on) to the end."""
    W, Hh = 345, 111
    cx, cy = 172, 55
    x0, x1 = cx - 170 + 24, cx + 168
    out = []
    phases = ["charge1", "charge2", "ignite", "beam1", "beam2", "fade"][:len(durs)]
    for k, ph in enumerate(phases):
        pix = F.Pix(W, Hh)
        rng = np.random.default_rng(71 + k)
        xs = np.arange(W)
        wob = np.round(1.2 * np.sin(xs * 0.21 + k * 1.7) + 0.8 * np.sin(xs * 0.53 + k * 0.9)).astype(int)
        inside = (pix.xx >= x0) & (pix.xx <= x1)
        dy = np.abs(pix.yy - cy)

        def band(half, col, flick=True):
            w = half + (wob[pix.xx] if flick and half > 2 else 0)
            pix.paint(inside & (dy <= w), col)
        if ph == "charge1":
            pix.paint(inside & (dy == 0), LUX[3])
            pix.star(x0, cy + 0.5, 5, [LUX[0], LUX[3]])
        elif ph == "charge2":
            band(1, LUX[3], False)
            pix.paint(inside & (dy == 0), LUX[1])
            pix.star(x0, cy + 0.5, 12, [LUX[0], LUX[3]])
            pix.dot(x0, cy + 0.5, 5, [LUX[3], LUX[1], LUX[0]])
            for s in range(10):                               # motes pulled into the wand
                a = rng.random() * 6.28
                d = 10 + rng.integers(0, 14)
                pix.paint(pix.ellipse_mask(x0 + math.cos(a) * d, cy + math.sin(a) * d * 0.7, 0.5, 0.5), LUX[2])
        elif ph == "ignite":                                  # one blinding frame
            band(20, LUX[2], False)
            band(15, LUX[1], False)
            band(10, LUX[0], False)
            pix.star(x0, cy + 0.5, 46, [LUX[0], LUX[2]])
            pix.dot(x0, cy + 0.5, 22, [LUX[2], LUX[1], LUX[0]])
        elif ph in ("beam1", "beam2"):
            core = 6 if ph == "beam1" else 5
            # a one-square prismatic fringe outside the bands, its colour changing along the beam
            fr = 17 + (1 if ph == "beam1" else 0)
            for i, col in enumerate(PRISM):
                seg = ((pix.xx // 9 + k) % 3 == i)
                pix.paint(inside & seg & (dy <= fr + wob[pix.xx]) & (dy > fr - 1 + wob[pix.xx]), col)
            band(16, LUX[4])
            band(13, LUX[3])
            band(10, LUX[2])
            band(core + 2, LUX[1])
            band(core, LUX[0], False)
            pix.star(x0, cy + 0.5, 32 if ph == "beam1" else 28, [LUX[0], LUX[3]])
            pix.dot(x0, cy + 0.5, 15, [LUX[3], LUX[1], LUX[0]])
            pix.star(x1 - 3, cy + 0.5, 16 if ph == "beam1" else 13, [LUX[0], LUX[3]])
            pix.dot(x1 - 6, cy + 0.5, 8, [LUX[3], LUX[1], LUX[0]])
            for s in range(16):                               # sparks thrown off the edges
                sx = x0 + 20 + rng.integers(0, x1 - x0 - 20)
                sy = cy + (1 if rng.random() < 0.5 else -1) * (19 + rng.integers(0, 8))
                pix.paint(pix.ellipse_mask(sx, sy, 0.5, 0.5), [LUX[2], PRISM[s % 3]][s % 2])
        else:                                                 # fading: a thin broken beam, sparks left behind
            gaps = ((pix.xx // 23 + k) % 4) != 0
            pix.paint(inside & gaps & (dy <= 4 + wob[pix.xx] // 2), LUX[3])
            pix.paint(inside & gaps & (dy <= 2), LUX[1])
            pix.star(x0, cy + 0.5, 12, [LUX[1], LUX[3]])
            for s in range(24):
                sx = x0 + rng.integers(0, x1 - x0)
                sy = cy + rng.integers(-14, 15)
                pix.paint(pix.ellipse_mask(sx, sy, 0.5, 0.5), [LUX[2], LUX[1], PRISM[s % 3]][s % 3])
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
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    jobs = [("jinx_r_rocket", "league_jinx_big", "r_rocket", {"path": "fx/jinxult.aseprite", "tag": "ult"}),
            ("jinx_r_blast", "league_jinx_big", "r_blast",
             {"path": "effects/jinxultexplosion.aseprite", "tag": "explode"}),
            ("lux_r_beam", "league_lux_r", "beam", {"path": "effects/luxult.aseprite", "tag": "ult"})]
    for name, sheet, tag, op in jobs:
        d, im = VP.load_fanim(a.root, sheet)
        now1 = VP.tag_frames(d, im, tag)
        nowh = VP.tag_frames(d, im, "hd_" + tag)
        durs = [dd for _, dd in now1]
        if tag == "r_rocket":
            frames = rocket(nowh)
        elif tag == "r_blast":
            frames = blast(len(durs))
        else:
            frames = beam(durs)
        test = [(f, dd) for f, dd in zip(frames, durs)]
        ofr = VP.oppi_frames(op, a.oppi)
        lanes = [("ours now (hd_)", nowh, 2, VP.extent(nowh, 2)),
                 ("test (PPU 1, bigger, our code)", test, 4, VP.extent(test, 4)),
                 (f"oppi ({os.path.basename(op['path'])}, size reference)", ofr or [], 4,
                  VP.extent(ofr, 4) if ofr else (40, 40))]
        bw = max(b[0] for *_, b in lanes)
        bh = max(b[1] for *_, b in lanes)
        lanes = [(t, fr, z, (bw, bh)) for t, fr, z, _b in lanes]
        total = sum(durs)
        reps = max(1, int(round(1.2 / total))) if total < 0.6 else 1
        block = VP.Block(f"{name}: {sheet}:{tag} ({len(durs)} frames, {total:.2f} s)", lanes, bw > 1.6 * bh)
        VP.write_gif(os.path.join(a.out, f"test_{name}.gif"), [block], total * reps)
        VP.strip_png(os.path.join(a.out, f"test_{name}.png"), test, 4)
        t_now = texels([f for f, _ in now1]) + texels([f for f, _ in nowh])
        t1 = texels(frames)
        print(f"{name}: {sheet}:{tag}  texels now (1x + hd_) {t_now}  test 1x only {t1} ({t1 / t_now:.0%})  "
              f"test 1x + 2x hd_ twin {5 * t1} ({5 * t1 / t_now:.0%});  test sizes "
              f"{sorted({(f.shape[1], f.shape[0]) for f in frames})[-3:]}")


if __name__ == "__main__":
    main()
