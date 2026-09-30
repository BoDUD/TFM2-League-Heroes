#!/usr/bin/env python3
"""Fiora's design (assets/source/native/fiora_native.png) from Codex's game-size draft, step by step.

    python tools/art/design_fiora.py [--check]

Step 1 of the user's order (sprite -> strips -> effects): Codex drew the sprite at game size from the picture the user
picked (the en-garde stance, the rapier held level; assets/source/fiora/MODEL_PROMPTS.md). The draft is
assets/source/fiora/codex_model/fiora_design_B.png, version B of two (the base heroes' bigger head). Of A/B at 40, 42
and 44 rows the user picked "B40" (2026-10-01, after first saying A40: "等等 A40不如B40").
  1. regrid (.claude/skills/tfm2-hero-mod/scripts/regrid.py): square borders from the colour changes, ~10.5 px squares
     -> 51 rows x 79 columns, one square to one game pixel, no resampling;
  2. palette: 24 colours (design_riven.palette), the irises one teal (EYE) used nowhere else;
  3. one outline (design_riven.one_outline + outline_rgba), the face kept square for square;
  4. the size: 40 rows (Riven, Vayne and Akali are 40): whole rows and columns deleted, never through the face
     (design_riven.keep_axis), then step 3 again;
  5. the rapier: right of the guard one bare row of bright silver, no outline along it (the outline pass had ringed it
     and Codex drew it two squares thick) - a one-square line, which strips.complete_outline leaves open;
  6. square edits (EDITS, each checked against the colour it replaces): three collar gems that took the eye teal go back
     to the gem blue; the near eye: the user saw "眼睛上有白色的方块" and picked 改法2 - the light-grey pair over it
     becomes the lash black and the white corner square the dark pupil;
  7. on the 128x128 canvas, soles on row 99, the middle of the feet on column 64, shown at 8x.
--check compares the result with the committed fiora_native.png instead of writing it.
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

DRAFT = os.path.join(ROOT, "assets", "source", "fiora", "codex_model", "fiora_design_B.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "fiora_native.png")
K = 24
HEIGHT = 40
EYE = (0x18, 0xB4, 0xC8)          # the irises; no other square uses it
BLADE = (0xE6, 0xE8, 0xF0)        # the rapier's blade: one square, bright silver, no outline along it
GEM = (0x01, 0x89, 0xD8)
LASH = (0x03, 0x09, 0x12)
PUPIL = (0x02, 0x25, 0x39)
# (x, y) on the 40-row figure, the colour expected there, the colour it becomes
EDITS = [
    ((20, 15), EYE, GEM), ((17, 16), EYE, GEM), ((20, 16), EYE, GEM),       # collar gems, not eyes
    ((18, 8), (0x80, 0x88, 0x9C), LASH), ((19, 8), (0x80, 0x88, 0x9C), LASH),  # over the near eye: lashes
    ((18, 9), (0xF2, 0xF2, 0xF6), PUPIL),                                     # the white corner: the pupil
]


def soles(a):
    return int(np.nonzero((a[..., 3] > 0).any(1))[0].max())


def crop(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (ys.min(), xs.min())


def face_box(g):
    """The face: skin-coloured squares in the top third of the figure, grown by 2."""
    op = g[..., 3] > 0
    ys = np.nonzero(op)[0]
    top, h = ys.min(), ys.max() - ys.min() + 1
    r, gg, b = (g[..., k].astype(int) for k in range(3))
    skin = op & (r > 200) & (gg > 160) & (b > 120) & (r - b > 40)
    skin[top + h // 3:] = False
    sy, sx = np.nonzero(skin)
    return range(sy.min() - 2, sy.max() + 3), range(sx.min() - 2, sx.max() + 3)


def step1_to_3():
    src = np.asarray(Image.open(R.lp(DRAFT)).convert("RGBA"))
    grid, _, _ = G.regrid(src)
    g = np.pad(grid, ((1, 1), (1, 1), (0, 0)))
    rows, cols = face_box(g)
    r, gg, b = (g[..., k].astype(int) for k in range(3))
    eye = (g[..., 3] > 0) & (b > 150) & (b - r > 60) & (gg > 90)
    box = np.zeros(eye.shape, bool)
    box[rows.start:rows.stop, cols.start:cols.stop] = True
    eye &= box
    pal, idx = R.palette(g, K)
    a = np.zeros(g.shape, np.uint8)
    m = idx >= 0
    a[m, :3] = pal[idx[m]]
    a[m, 3] = 255
    a[eye, :3] = EYE
    a = R.outline_rgba(R.one_outline(a, box), feet=soles(a), keep=box)
    a, (y0, x0) = crop(a)
    return a, range(rows.start - y0, rows.stop - y0), range(cols.start - x0, cols.stop - x0)


def step4(a, face_rows, face_cols):
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


def step5(a):
    """Columns right of the guard hold at most 5 figure rows (counted from the right edge): keep the lightest row."""
    a = a.copy()
    op = a[..., 3] > 0
    H, W = op.shape
    x = W - 1
    while x > 0 and 0 < op[:, x].sum() <= 5:
        x -= 1
    x0 = x + 1
    lum = a[..., :3].astype(int).sum(-1)
    rows = [int(np.nonzero(op[:, c])[0][np.argmax(lum[np.nonzero(op[:, c])[0], c])]) for c in range(x0, W)
            if op[:, c].any()]
    y = int(np.bincount(rows).argmax())
    a[:, x0:] = 0
    a[y, x0:W, :3] = BLADE
    a[y, x0:W, 3] = 255
    return a


def step6(a):
    a = a.copy()
    for (x, y), was, new in EDITS:
        if tuple(int(v) for v in a[y, x, :3]) != was:
            raise SystemExit(f"edit at {(x, y)}: expected {was}, found {tuple(a[y, x, :3])} - the draft or a step changed")
        a[y, x, :3] = new
    return a


def design():
    a, fr, fc = step1_to_3()
    a = step6(step5(step4(a, fr, fc)))
    H, W = a.shape[:2]
    feet = np.nonzero(a[H - 1, :, 3] > 0)[0]          # the soles' row holds the two feet only
    x0 = int(round(64 - (feet.min() + feet.max() + 1) / 2))
    if x0 < 0 or x0 + W > 128:
        raise SystemExit(f"the figure ({W} wide, feet middle at {x0}) does not fit the 128-square canvas")
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[100 - H:100, x0:x0 + W] = a
    return Image.fromarray(canvas).resize((1024, 1024), Image.NEAREST), a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    img, a = design()
    if args.check:
        old = np.asarray(Image.open(R.lp(OUT)).convert("RGBA"))
        new = np.asarray(img)
        print("identical" if old.shape == new.shape and (old == new).all() else
              f"differs: {int(np.any(old != new, -1).sum())} px")
        return
    img.save(R.lp(OUT))
    op = a[..., 3] > 0
    print(f"{OUT}: {a.shape[1]}x{a.shape[0]}, {len({tuple(c) for c in a[op][:, :3]})} colours")


if __name__ == "__main__":
    main()
