#!/usr/bin/env python3
"""Kayn's three designs (2026-10-04): the base look and the two forms the user picked from Codex's step-1 delivery.

    python tools/art/design_kayn.py [--check]

Codex drew each design as a coarse pixel draft (assets/source/kayn/codex_model/*_raw.png, ~17-23 px squares on 1254
px) and cut it to the target height itself by deleting whole rows (outside the face) while keeping every column: the
base came out 40 x 50, squashed, its scythe's crescent broken into a checker. Shown that cut beside the drafts brought
down evenly (work/ka/draft_to_size.py: kayn_size_options.png), the user picked by screenshot 「应该是 40 44 40」:
  base    the draft read back on its own grid (the skill's regrid.py, 51 x 51), snapped to Codex's shared 24-colour
          palette (codex_model/palette.json) in CIELAB and brought to 40 rows by area mode - 40 x 40;
  darkin  the same from its draft (52 x 53) to 44 rows - 44 x 45; the scythe's lowest five squares (one row under the
          feet: the game draws the health bar there) dropped;
  shadow  Codex's own 40-row cut (codex_model/kayn_shadow_A_1x.png) - 40 x 61, as delivered.
Each gets one dark ring (strips.complete_outline, nothing under the soles) and goes on the 128x128 canvas at 8x with
the soles on row 99 and the middle of the feet on column 64:
  assets/source/native/kayn_native.png, kayn_darkin_native.png, kayn_shadow_native.png.
--check rebuilds and compares with the files on disk.
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
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "kayn", "codex_model")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
SOLE_ROW, MID_COL, Z = 99, 64, 8


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def srgb2lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def palette():
    cols = json.load(open(lp(os.path.join(SRC, "palette.json")), encoding="utf-8"))["colors"]
    return np.array([[int(c[k:k + 2], 16) for k in (1, 3, 5)] for c in cols])


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def from_draft(name, rows, P):
    """The draft read back on its own grid, palette-snapped, area-mode down to `rows` rows (palette indices)."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA"))
    sq = crop(regrid(a)[0])
    d = ((srgb2lab(sq[..., :3])[:, :, None, :] - srgb2lab(P)[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    idx[sq[..., 3] < 128] = -1
    H, W = idx.shape
    s = H / rows
    cols = int(round(W / s))
    out = np.full((rows, cols), -1)
    for r in range(rows):
        for c in range(cols):
            y0, y1, x0, x1 = r * s, (r + 1) * s, c * s, (c + 1) * s
            w = np.zeros(len(P) + 1)
            for y in range(int(y0), min(H, int(np.ceil(y1)))):
                wy = min(y + 1, y1) - max(y, y0)
                for x in range(int(x0), min(W, int(np.ceil(x1)))):
                    wx = min(x + 1, x1) - max(x, x0)
                    w[idx[y, x] + 1] += wy * wx
            out[r, c] = -1 if w[0] > w[1:].max() else int(w[1:].argmax())
    a = np.zeros(out.shape + (4,), np.uint8)
    m = out >= 0
    a[m, :3] = P[out[m]]
    a[m, 3] = 255
    return a


def ring(a, feet):
    """One dark ring round the figure; `feet` is the soles' row (nothing is added under it)."""
    pad = np.zeros((a.shape[0] + 2, a.shape[1] + 2, 4), np.uint8)
    pad[1:-1, 1:-1] = a
    out, _, _ = strips.complete_outline(pad, feet=feet + 1)
    return out


def feet_mid(a, soles):
    """The middle between the outer edges of the feet on the soles' row."""
    xs = np.nonzero(a[soles, :, 3] > 0)[0]
    return (xs.min() + xs.max()) / 2


def on_canvas(fig, soles, mid):
    can = np.zeros((128, 128, 4), np.uint8)
    y0 = SOLE_ROW - soles
    x0 = int(round(MID_COL - mid))
    h, w = fig.shape[:2]
    can[y0:y0 + h, x0:x0 + w] = fig
    if can[SOLE_ROW + 1:, :, 3].any():
        sys.exit("something under the soles' row")
    return np.repeat(np.repeat(can, Z, 0), Z, 1)


def build():
    P = palette()
    out = {}
    # base: 40 rows; the soles are its last row
    base = crop(from_draft("kayn_design_A_raw.png", 40, P))
    base = crop(ring(base, base.shape[0] - 1))
    out["kayn_native.png"] = on_canvas(base, base.shape[0] - 1, feet_mid(base, base.shape[0] - 1))
    # darkin: 44 rows; its last row is the scythe's tip under the feet - dropped, the soles are the row above
    dk = crop(from_draft("kayn_darkin_A_raw.png", 44, P))
    dk = crop(dk[:-1])
    dk = crop(ring(dk, dk.shape[0] - 1))
    out["kayn_darkin_native.png"] = on_canvas(dk, dk.shape[0] - 1, feet_mid(dk, dk.shape[0] - 1))
    # shadow: Codex's own cut, ringed where it is open
    sh = crop(np.asarray(Image.open(lp(os.path.join(SRC, "kayn_shadow_A_1x.png"))).convert("RGBA")))
    sh = crop(ring(sh, sh.shape[0] - 1))
    # its soles' row also holds the cyan blade's tip: the feet middle from the two feet only (columns left of it)
    xs = np.nonzero(sh[-1, :, 3] > 0)[0]
    feet = xs[xs < sh.shape[1] * 0.75]
    out["kayn_shadow_native.png"] = on_canvas(sh, sh.shape[0] - 1, (feet.min() + feet.max()) / 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    for name, img in build().items():
        path = os.path.join(NATIVE, name)
        if a.check:
            old = np.asarray(Image.open(lp(path)).convert("RGBA"))
            print(name, "identical" if np.array_equal(old, img) else "DIFFERENT")
            continue
        Image.fromarray(img).save(lp(path))
        fig = crop(img[Z // 2::Z, Z // 2::Z])
        cols = len({tuple(c) for c in fig[fig[..., 3] > 0][:, :3]})
        print(name, "figure", fig.shape[:2], "colours", cols)


if __name__ == "__main__":
    main()
