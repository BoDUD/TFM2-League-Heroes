#!/usr/bin/env python3
"""Draw the ground warnings of Aatrox's three Q casts at League's sizes (x 72.7 to TFM2 units, 1000 units a pixel),
as native strips for import_aatrox.py: assets/source/aatrox/aatrox_fx_q1_warn.png, _q2_warn, _q3_warn (8x) and their
cells in aatrox_fx_anchors.json; also World Ender's fear ring (aatrox_fx_r_fear_ring.png, below).

    python tools/art/warn_aatrox.py [--preview <png>]

League (wiki, The Darkin Blade): Q1 a 625 x 180 rectangle from him, the sweet spot at the far edge; Q2 a trapezoid from
100 behind him to 475 ahead, 300 -> 500 wide, the sweet spot at the far edge; Q3 a 300-radius circle 200 ahead with a
180-radius sweet spot inside. The angle is fixed for the 0.6 s wind-up and the shape shows on the ground meanwhile.
Here: Q1 45 x 13 px, Q2 42 px long (7 behind) and 22 -> 36 across, Q3 a 22-px circle with a 13-px middle.

One frame every STEP ticks from the cast to the blow (BLOW, build_aatrox.py q_hit_t): frame k is the wind-up after
(k + 1) x STEP ticks, the fill reaching that share of the shape from his side (Q1, Q2) or from the middle (Q3, from a
disc of Q3_MIN so its first frames are no loose plus sign) - the time left until the blow, read off the ground.
import_aatrox.py plays the first frames on the picture-only twins of the shape build_aatrox.py re-lays at TELE_T (0, 9,
18: q*_tele, _b, _c) and the rest on the real shape laid at q_lock_t, so the fill runs on without a jump; whole ticks
a frame (the first warning had 6 frames of 1.7 ticks over the last 10 ticks only: a flicker).
The outline is the whole shape from the first frame (RED, BRIGHT once the real shape lies - the angle fixed); the
sweet spot has its own outline (ORANGE, GOLD on the last frame). The fill is solid, DARK in the body and RED in the
sweet spot: the first warning drew it as a 50% checkerboard over 1/8 single dots, which read as speckle at 2-4x and
under the camera's non-integer zoom (the effects audit counted up to 116 loose squares a frame). Flat colours and whole
pixels like the other effects (FIRE ramp of import_aatrox.py).
The line shapes are LineRangeProjectile views (centred on the line: Q1's 45000 line, Q2's 26000 line, the trapezoid's
middle 14 px ahead of him); Q3's circle is a ViewEffect on the point 14500 ahead, on the ground (the FEET spot).

The fear ring (R's fear on minions and monsters, import_aatrox.py r_feared): a flat ellipse FEAR_RX x FEAR_RY on the
ground round a unit's feet, drawn under the unit, in the swirl's purples (SHADE, the band 8E5BA8 since fix round 3:
the darker band barely read on the arena) with two lighter arcs that turn a half round over its 4 frames (two arcs:
the loop then repeats) - the swirl over the head (Codex's r_feared) lay on tall champions' faces.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "aatrox")
Z = 8
BLOW = 36                               # the blow, ticks from the cast (build_aatrox.py q_hit_t, League's 0.6 s)
STEP = 2                                # ticks a frame: whole ticks
LOCKED = 26                             # the real shape lies from here (build_aatrox.py q_lock_t): the outline brightens
N = BLOW // STEP                        # frames over the wind-up

DARK, RED, BRIGHT, ORANGE, GOLD = "8F0E2B", "B8102A", "E0202E", "FF5A2A", "FFB347"

Q1 = dict(length=45, half=6.5, sweet=9)                       # 625 x 180, the far 125
Q2 = dict(back=7, front=34.5, half0=11, half1=18, sweet=7)     # -100..475, 300 -> 500, the far 100
Q3 = dict(r=22, sweet=13)                                      # 300, 180
Q3_MIN = 2.6                    # the first frames' disc (r 1.2 / 2.4 were a 5-square plus alone in the circle)
SHADE = ("1A0A22", "34163F", "5A2E6E", "8E5BA8", "C9A6D8")    # import_aatrox.RAMPS["SHADE"]
FEAR_RX, FEAR_RY = 10.5, 4.5    # the fear ring's half axes (px): 21 x 9, out past a minion's or a champion's feet
# the band's shade (SHADE index; its rim one darker, the arcs one lighter): 2 (5A2E6E, rim 34163F) barely read on
# the arena at 1-3x (the review, fix round 3) - 3, 8E5BA8 with a 5A2E6E rim and C9A6D8 arcs
FEAR_BAND = 3
FEAR_IN = 0.5                   # the band's inner edge (ellipse measure: 1 the outer rim)


def rgba(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


def edge(mask):
    """Squares of the mask with a 4-neighbour outside it."""
    p = np.pad(mask, 1)
    inner = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return mask & ~inner


def paint(shape, sweet, reach, k):
    """One frame: `shape` and `sweet` masks, `reach` the squares the fill has reached by frame k. Solid fills inside
    the closed outline: no loose square anywhere."""
    h, w = shape.shape
    out = np.zeros((h, w, 4), np.uint8)
    body = shape & ~sweet
    out[body & reach] = rgba(DARK)
    out[sweet & reach] = rgba(RED if k < N - 1 else BRIGHT)
    out[edge(shape)] = rgba(RED if (k + 1) * STEP <= LOCKED else BRIGHT)
    out[edge(sweet) & shape] = rgba(ORANGE if k < N - 1 else GOLD)
    # the round fill a square short of Q3's ring left 1-2 square pockets between them: filled
    out[pockets(shape & (out[..., 3] == 0), 6)] = rgba(DARK)
    return out


def pockets(mask, most):
    """Squares of `mask` in 4-connected pieces of at most `most` squares."""
    h, w = mask.shape
    seen = np.zeros_like(mask)
    small = np.zeros_like(mask)
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        piece, todo = [], [(y0, x0)]
        seen[y0, x0] = True
        while todo:
            y, x = todo.pop()
            piece.append((y, x))
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    todo.append((yy, xx))
        if len(piece) <= most:
            for y, x in piece:
                small[y, x] = True
    return small


def q1():
    L, hw, s = Q1["length"], Q1["half"], Q1["sweet"]
    h = int(2 * hw)
    yy, xx = np.mgrid[0:h, 0:L]
    shape = np.ones((h, L), bool)
    sweet = xx >= L - s
    frames = [paint(shape, sweet, xx < round(L * (k + 1) / N), k) for k in range(N)]
    return frames, (L // 2, h // 2)


def q2():
    b, f, h0, h1, s = Q2["back"], Q2["front"], Q2["half0"], Q2["half1"], Q2["sweet"]
    L = int(round(b + f))
    H = int(2 * h1) + 1
    yy, xx = np.mgrid[0:H, 0:L]
    half = h0 + (h1 - h0) * (xx + 0.5) / L
    shape = np.abs(yy - H // 2) <= half
    sweet = shape & (xx >= L - s)
    frames = [paint(shape, sweet, xx < round(L * (k + 1) / N), k) for k in range(N)]
    return frames, (L // 2, H // 2)


def q3():
    r, s = Q3["r"], Q3["sweet"]
    D = 2 * r + 1
    yy, xx = np.mgrid[0:D, 0:D]
    d = np.hypot(yy - r, xx - r)
    shape = d <= r + 0.3
    sweet = d <= s + 0.3
    frames = [paint(shape, sweet, d <= max(Q3_MIN, r * (k + 1) / N), k) for k in range(N)]
    return frames, (r, r)


def fear_ring(n=4):
    """The fear's ground ring: an elliptic band (SHADE[FEAR_BAND]) with its outer rim a shade darker, two lighter
    arcs a half turn apart (the lightest at their heads while the ramp has one), turned a half round over n frames
    (then the loop repeats)."""
    W, H = 2 * int(FEAR_RX) + 1, 2 * int(FEAR_RY) + 1
    cx, cy = W // 2, H // 2
    yy, xx = np.mgrid[0:H, 0:W]
    e = ((xx - cx) / FEAR_RX) ** 2 + ((yy - cy) / FEAR_RY) ** 2
    band = (e <= 1.0) & (e >= FEAR_IN)
    rim = band & (e >= 0.8)
    ang = np.arctan2((yy - cy) / FEAR_RY, (xx - cx) / FEAR_RX)
    frames = []
    for k in range(n):
        ph = (ang - k * np.pi / n) % np.pi                        # two arcs a half turn apart: n steps make the loop
        f = np.zeros((H, W, 4), np.uint8)
        f[band] = rgba(SHADE[FEAR_BAND])
        f[rim] = rgba(SHADE[FEAR_BAND - 1])
        f[band & (ph < 1.1)] = rgba(SHADE[FEAR_BAND + 1])
        if FEAR_BAND + 2 < len(SHADE):
            f[band & (ph >= 0.75) & (ph < 1.1)] = rgba(SHADE[FEAR_BAND + 2])
        frames.append(f)
    return frames, (cx, cy)


def write(name, frames, anchor, anchors):
    h, w = frames[0].shape[:2]
    strip = np.concatenate(frames, axis=1)
    big = np.repeat(np.repeat(strip, Z, 0), Z, 1)
    Image.fromarray(big).save(G.lp(os.path.join(SRC, f"aatrox_fx_{name}.png")))
    anchors[name] = {"cell": [w, h], "anchor": list(anchor), "frames": len(frames)}
    print(f"aatrox_fx_{name}.png {len(frames)} frames {w}x{h}, anchor {anchor}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="also write the frames on a grass colour at 6x")
    a = ap.parse_args()
    path = G.lp(os.path.join(SRC, "aatrox_fx_anchors.json"))
    with open(path, encoding="utf-8") as f:
        anchors = json.load(f)
    made = {"q1_warn": q1(), "q2_warn": q2(), "q3_warn": q3(), "r_fear_ring": fear_ring()}
    for name, (frames, anchor) in made.items():
        write(name, frames, anchor, anchors)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(anchors, f, indent=1)
    if a.preview:
        S = 6
        rows = []
        for name, (frames, _) in made.items():
            h, w = frames[0].shape[:2]
            row = np.zeros((h + 4, (w + 4) * N, 4), np.uint8)
            row[...] = (88, 110, 64, 255)
            for k, fr in enumerate(frames):
                sub = row[2:2 + h, 2 + k * (w + 4):2 + k * (w + 4) + w]
                m = fr[..., 3] > 0
                sub[m] = fr[m]
            rows.append(row)
        W = max(r.shape[1] for r in rows)
        sheet = np.concatenate([np.pad(r, ((0, 0), (0, W - r.shape[1]), (0, 0))) for r in rows], axis=0)
        Image.fromarray(np.repeat(np.repeat(sheet, S, 0), S, 1)).save(a.preview)


if __name__ == "__main__":
    main()
