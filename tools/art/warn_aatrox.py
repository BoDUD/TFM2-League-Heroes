#!/usr/bin/env python3
"""Draw the ground warnings of Aatrox's three Q casts at League's sizes (x 72.7 to TFM2 units, 1000 units a pixel),
as native strips for import_aatrox.py: assets/source/aatrox/aatrox_fx_q1_warn.png, _q2_warn, _q3_warn (8x) and their
cells in aatrox_fx_anchors.json.

    python tools/art/warn_aatrox.py [--preview <png>]

League (wiki, The Darkin Blade): Q1 a 625 x 180 rectangle from him, the sweet spot at the far edge; Q2 a trapezoid from
100 behind him to 475 ahead, 300 -> 500 wide, the sweet spot at the far edge; Q3 a 300-radius circle 200 ahead with a
180-radius sweet spot inside. The angle is fixed for the 0.6 s wind-up and the shape shows on the ground meanwhile.
Here: Q1 45 x 13 px, Q2 42 px long (7 behind) and 22 -> 36 across, Q3 a 22-px circle with a 13-px middle. Every frame
the dark red fill reaches further from his side (Q1, Q2) or from the middle (Q3) - the wind-up running out - over a
dark outline; the sweet spot is drawn in brighter reds and flares on the last frame. Flat colours and whole pixels like
the other effects (FIRE ramp of import_aatrox.py).
The line shapes are LineRangeProjectile views (centred on the line: Q1's 45000 line, Q2's 28000 line, the trapezoid's
middle 14 px ahead of him); Q3's circle is a ViewEffect on the point 14500 ahead, on the ground (the FEET spot).
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
N = 6                                   # frames over the wind-up

DARK, RED, BRIGHT, ORANGE, GOLD = "8F0E2B", "B8102A", "E0202E", "FF5A2A", "FFB347"

Q1 = dict(length=45, half=6.5, sweet=9)                       # 625 x 180, the far 125
Q2 = dict(back=7, front=34.5, half0=11, half1=18, sweet=7)     # -100..475, 300 -> 500, the far 100
Q3 = dict(r=22, sweet=13)                                      # 300, 180


def rgba(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)] + [255], np.uint8)


def edge(mask):
    """Squares of the mask with a 4-neighbour outside it."""
    p = np.pad(mask, 1)
    inner = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
    return mask & ~inner


def paint(shape, sweet, reach, k):
    """One frame: `shape` and `sweet` masks, `reach` the squares the fill has reached by frame k."""
    h, w = shape.shape
    out = np.zeros((h, w, 4), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    dots = ((yy + xx) % 2 == 0)                                  # a half dither: the ground shows through
    sparse = ((yy % 2 == 0) & ((xx + yy // 2) % 4 == 0))         # an eighth: the shape before the fill reaches it
    body = shape & ~sweet
    out[body & sparse] = rgba(DARK)
    out[body & reach & dots] = rgba(DARK)
    out[sweet & (sparse | (reach & dots))] = rgba(RED if k < N - 1 else BRIGHT)
    out[edge(shape)] = rgba(RED if k < 3 else BRIGHT)
    out[edge(sweet) & shape] = rgba(ORANGE if k < N - 1 else GOLD)
    return out


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
    frames = [paint(shape, sweet, d <= r * (k + 1) / N, k) for k in range(N)]
    return frames, (r, r)


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
    made = {"q1_warn": q1(), "q2_warn": q2(), "q3_warn": q3()}
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
