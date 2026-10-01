#!/usr/bin/env python3
"""Jax's design (assets/source/native/jax_native.png) from Codex's game-size draft, step by step.

    python tools/art/design_jax.py [--check]

Step 1 of the user's order (sprite -> strips -> effects), drawn the way main's league_lucian and league_vayne were:
Codex drew the sprite at game size from the user's picture (assets/source/jax/MODEL_PROMPTS.md; the draft is
assets/source/jax/codex_model/jax_design_A.png, version A of two: the picture's proportions, four one-square cyan
eye lights on the bronze mask). The user picked "A41" of A45 / A43 / A41 / B52 / B44 / B41 (2026-09-30).
  1. regrid (.claude/skills/tfm2-hero-mod/scripts/regrid.py): square borders from the colour changes, each square
     the median of its middle, ~10 px squares -> 46 rows x 55 columns, one square to one game pixel, no resampling;
  2. palette: 24 colours (tools/art/design_riven.palette: k-means in Lab over the unique colours weighted by the
     square root of their counts, each cluster shown by its commonest real colour);
  3. the eye lights: every cyan square becomes EYE, a cyan used nowhere else (import_native steadies the frames on
     it), and the top pair is levelled - Codex drew the top-right light a row high; the prompt's pattern is
     cyan-gold-cyan / gold-gold-gold / cyan-gold-cyan;
  4. nothing below the soles (the game draws the health bar there): the lantern's lowest spike, one row under the
     soles, goes;
  5. one outline (design_riven.one_outline + outline_rgba: spurs off, the black just inside the outline turned into
     the material's own darkest shade, the ring completed), the mask kept square for square;
  6. the size: 41 rows (the user's pick; Riven 40, Darius 42): whole rows and columns deleted, never through the
     mask (design_riven.keep_axis), then step 5 again;
  7. on the 128x128 canvas, soles on row 99, the middle of the feet on column 64, shown at 8x.
tools/art/shrink_jax.py then cut him to 36 rows (players found him too big, 2026-10-01): it starts from this 41-row
design kept in assets/source/jax/native41/, and --check compares the result with that copy when it is there (with the
committed jax_native.png otherwise) instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_riven as R  # noqa: E402
import regrid as G  # noqa: E402

DRAFT = os.path.join(ROOT, "assets", "source", "jax", "codex_model", "jax_design_A.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "jax_native.png")
APPROVED = os.path.join(ROOT, "assets", "source", "jax", "native41", "jax_native.png")   # shrink_jax.py's source
K = 24
EYE = (0x46, 0xF0, 0xFF)          # the four lights on the mask; no other square uses it
HEIGHT = 41


def cyan(a):
    return (a[..., 3] > 0) & (a[..., 1] > 150) & (a[..., 2] > 150) & (a[..., 0] < 140)


def soles(a):
    return int(np.nonzero((a[..., 3] > 0).any(1))[0].max())


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (ys.min(), xs.min())


def step1_to_5():
    src = np.asarray(Image.open(R.lp(DRAFT)).convert("RGBA"))
    grid, _, _ = G.regrid(src)
    g = np.pad(grid, ((1, 1), (1, 1), (0, 0)))
    eye = cyan(g)
    pal, idx = R.palette(g, K)
    a = np.zeros(g.shape, np.uint8)
    m = idx >= 0
    a[m, :3] = pal[idx[m]]
    a[m, 3] = 255
    a[eye, :3] = EYE
    # step 3: the top-right light a row down (grid row 15 -> 16, column 33; +1 for the border)
    a[16, 34, :3] = a[16, 33, :3]
    a[17, 34, :3] = EYE
    # step 4: the lantern's lowest spike, one row under the soles (grid row 44)
    a[46:] = 0
    eye = np.all(a[..., :3] == EYE, -1) & (a[..., 3] > 0)
    ys, xs = np.nonzero(eye)
    rows = range(ys.min() - 3, ys.max() + 3)          # the mask: its rows and columns never change
    cols = range(xs.min() - 3, xs.max() + 3)
    keep = np.zeros(eye.shape, bool)
    keep[rows.start:rows.stop, cols.start:cols.stop] = True
    a = R.outline_rgba(R.one_outline(a, keep), feet=soles(a), keep=keep)
    a, (y0, x0) = crop(a)
    return a, range(rows.start - y0, rows.stop - y0), range(cols.start - x0, cols.stop - x0)


def step6(a, face_rows, face_cols):
    H, W = a.shape[:2]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, W), -1, int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]
    fr, fc = list(face_rows), list(face_cols)
    rows = R.keep_axis([idx[y] for y in range(H)], HEIGHT, fr)
    sub = idx[rows]
    kc = R.keep_axis([sub[:, x] for x in range(W)], round(W * HEIGHT / H), fc)
    small = np.pad(idx[np.ix_(rows, kc)], 1, constant_values=-1)
    pal = np.array(cols, np.uint8)
    out = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    out[m, :3] = pal[small[m]]
    out[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    keep[rows.index(fr[0]) + 1:rows.index(fr[-1]) + 2, kc.index(fc[0]) + 1:kc.index(fc[-1]) + 2] = True
    return crop(R.outline_rgba(R.one_outline(out, keep), feet=soles(out), keep=keep))[0]


def design():
    a, fr, fc = step1_to_5()
    a = step6(a, fr, fc)
    H, W = a.shape[:2]
    feet = np.nonzero(a[H - 1, :, 3] > 0)[0]          # the soles' row holds the two feet only
    x0 = int(round(64 - (feet.min() + feet.max() + 1) / 2))
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[100 - H:100, x0:x0 + W] = a
    return Image.fromarray(canvas).resize((1024, 1024), Image.NEAREST), a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    img, a = design()
    if args.check:
        old = np.asarray(Image.open(R.lp(APPROVED if os.path.exists(R.lp(APPROVED)) else OUT)).convert("RGBA"))
        new = np.asarray(img)
        print("identical" if old.shape == new.shape and (old == new).all() else
              f"differs: {int(np.any(old != new, -1).sum())} px")
        return
    img.save(R.lp(OUT))
    op = a[..., 3] > 0
    print(f"{OUT}: {a.shape[1]}x{a.shape[0]}, {len({tuple(c) for c in a[op][:, :3]})} colours")


if __name__ == "__main__":
    main()
