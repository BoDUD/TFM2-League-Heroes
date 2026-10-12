#!/usr/bin/env python3
"""Kassadin's PPU design: Codex's step-1 raws read back on their own grid, one palette, the Nether Blade drawn in.

    python tools/art/design_kassadin_hd.py [--preview out.png]

The user (2026-10-12): 「卡萨丁换方案用PPU 你看看codex生成的 另外手上的武器呢？」, then picked front A (the retry) +
side A, 37 game rows (PPU = 134 / 37 = 3.62, a float PPU like league_ashe's) and 「我在读回图上手描刃」.
Sources: assets/source/kassadin/codex_model/readback/kassadin-front-A-retry.png (93 x 134) and kassadin-side-A.png
(88 x 133), Codex's raws (codex_model/raw, ~10 px squares) read back square for square with the skill's regrid.py.
Steps:
  * one palette for both views: their own colours, k-means (design_varus.kmeans) to K colours over both at once;
  * the Nether Blade (League's voidblade_glow: a black-violet straight blade with notched edges and a violet glowing
    rim) drawn square by square from the near hand, straight at 45 degrees down and forward - BLADE gives the base and
    the length per view; the hand stays on top of it;
  * written to assets/source/kassadin/ppu/front.png and side.png (the hd designs), soles on the last row.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_varus import kmeans  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kassadin", "codex_model", "readback")
OUT = os.path.join(ROOT, "assets", "source", "kassadin", "ppu")
VIEWS = {"front": "kassadin-front-A-retry.png", "side": "kassadin-side-A.png"}
K = 32
GAME_ROWS = 37
# the blade: (base x, base y) just under the near hand's wrist, its length along the 45-degree line, the pad to the right
BLADE = {"front": ((80, 82), 32), "side": ((78, 85), 32)}
# blade colours: League's voidblade_glow - a black-violet body, a violet rim, a lilac edge, a white-lilac point
CORE = (26, 6, 48)
CORE2 = (46, 14, 82)
RIM = (116, 38, 220)
EDGE = (204, 150, 255)
TIP = (240, 220, 255)
INK = (14, 6, 26)
HAND = ((60, 200, 200), 140)    # cyan hand: colours whose green and blue are both above 140 and red below


def load(name):
    return np.asarray(Image.open(os.path.join(SRC, name)).convert("RGBA")).copy()


def quantize(arrs):
    """One palette over both views (their own colours)."""
    h = max(a.shape[0] for a in arrs)
    both = np.concatenate([np.pad(a, ((0, h - a.shape[0]), (0, 0), (0, 0))) for a in arrs], 1)
    idx, pal = kmeans(both, K)
    out, x = [], 0
    for a in arrs:
        sub = idx[:a.shape[0], x:x + a.shape[1]]
        q = np.zeros_like(a)
        op = sub >= 0
        q[op, :3] = pal[sub[op]]
        q[op, 3] = 255
        out.append(q)
        x += a.shape[1]
    return out, pal


def is_hand(rgb):
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    return g > HAND[1] and b > HAND[1] and r < 200


def blade(a, base, length, direction=(1, 1), bright=False, crop=True):
    """Draw the blade from `base` along `direction` (a multiple of 45 degrees: (1, 1) down and forward, (1, 0) forward,
    (1, -1) up and forward, (0, -1) up, (0, 1) down), under the hand's squares. `length` counts squares along the
    larger axis (diagonals as long as the design's). bright: Nether Blade's empowered strike - the whole rim lit.
    crop: grow the picture for the blade and trim it (the design); else draw inside `a` as it is (the rig's canvas)."""
    if crop:
        pad = length + 6
        a = np.pad(a, ((0, pad), (0, pad), (0, 0)))
    H, W = a.shape[:2]
    bx, by = base
    dx, dy = direction
    n_ = np.hypot(dx, dy)
    ux, uy = dx / n_, dy / n_                        # along the blade
    nx, ny = -uy, ux                                 # across it
    L = length * n_
    hand = np.zeros((H, W), bool)
    y0, y1 = max(0, int(by - L - 8)), min(H, int(by + L + 8))
    x0, x1 = max(0, int(bx - L - 8)), min(W, int(bx + L + 8))
    for y in range(y0, y1):
        for x in range(x0, x1):
            if a[y, x, 3] and is_hand(a[y, x]):
                hand[y, x] = True
    body = np.zeros((H, W), bool)
    col = np.zeros((H, W, 3), np.uint8)
    for y in range(y0, y1):
        for x in range(x0, x1):
            px, py = x + 0.5 - bx, y + 0.5 - by
            t = px * ux + py * uy
            d = px * nx + py * ny
            if t < -1 or t > L:
                continue
            f = t / L
            w = 3.6 * (1 - f) ** 0.55 + 0.5                # half width tapering to the point
            k = (t % 8.0)
            if 3.0 < k < 5.0 and 0.1 < f < 0.8:            # the teeth (voidblade_glow), a pair every 8, both sides
                w += 1.0 + (1.0 if abs(k - 4.0) < 0.75 else 0.0)
            if abs(d) > w:
                continue
            body[y, x] = True
            if f > 0.9:
                col[y, x] = TIP
            elif abs(d) > w - 0.9:
                col[y, x] = EDGE if (d < 0 or bright) else RIM   # the lit side up-right, the rim below
            elif abs(d) > w - 2.0:
                col[y, x] = (EDGE if bright else RIM) if d < 0 else (160, 85, 255)
            else:
                col[y, x] = CORE2 if d < 0 else CORE
    out = a.copy()
    put = body & ~hand
    out[put, :3] = col[put]
    out[put, 3] = 255
    # one square of ink round the blade where it meets the background
    p = np.pad(put, 1)
    ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~put & (out[..., 3] == 0)
    out[ring, :3] = INK
    out[ring, 3] = 255
    if not crop:
        return out
    ys, xs = np.nonzero(out[..., 3])
    return out[:ys.max() + 1, :xs.max() + 1]


def base_views():
    """{view: the read-back on the shared palette, no blade}."""
    arrs = [load(VIEWS[v]) for v in VIEWS]
    qs, _ = quantize(arrs)
    return dict(zip(VIEWS, qs))


def build():
    arrs = [load(VIEWS[v]) for v in VIEWS]
    qs, pal = quantize(arrs)
    out = {}
    for (v, _), q in zip(VIEWS.items(), qs):
        base, length = BLADE[v]
        out[v] = blade(q, base, length)
    return out, pal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview")
    a = ap.parse_args()
    views, pal = build()
    os.makedirs(OUT, exist_ok=True)
    for v, arr in views.items():
        Image.fromarray(arr).save(os.path.join(OUT, v + ".png"))
        n = len({tuple(c) for c in arr[arr[..., 3] > 0][:, :3]})
        print(v, arr.shape[1], "x", arr.shape[0], n, "colours, PPU", round(arr.shape[0] / GAME_ROWS, 3))
    if a.preview:
        Z = 4
        tiles = [Image.fromarray(views[v]).resize((views[v].shape[1] * Z, views[v].shape[0] * Z), Image.NEAREST)
                 for v in views]
        H = max(t.height for t in tiles)
        img = Image.new("RGBA", (sum(t.width + 30 for t in tiles), H), (225, 225, 225, 255))
        x = 0
        for t in tiles:
            img.alpha_composite(t, (x, H - t.height))
            x += t.width + 30
        img.convert("RGB").save(a.preview)


if __name__ == "__main__":
    main()
