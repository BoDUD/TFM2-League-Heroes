#!/usr/bin/env python3
"""Alistar's design (assets/source/native/alistar_native.png): Codex's generated draft A read back on its own grid,
mapped to a 24-colour palette in CIELAB and halved by 2x2 blocks.

    python tools/art/design_alistar.py [--check] [--review OUT.png]

How it came about (2026-10-05): the user picked Codex's picture A (codex_picture/alistar-model-A.png: League's idle,
hunched forward, both hands hanging in front, the wide shackles). For step 1 (42 / 46 rows asked) Codex delivered A / B
cut by whole rows and columns from its coarse draft B (codex_model/alistar_design_A_1x.png / _B_1x.png: the horns and
shackles squeezed, a 1-square near eye) and three generated drafts; its first draft A was the most detailed and twice
the size. The options sheet showed that draft halved (44 rows), area-voted to 42 / 46, draft B as read back and Codex's
A / B; the user took 「1 原稿2×2减半 44行」. Steps:
  1. codex_model/alistar_generated_A.png (13 px squares on 1254 x 1254) read back on its own grid (the skill's
     regrid.py, alpha >= 128): 88 x 79;
  2. every square the nearest colour of PALETTE (a 24-colour k-means of that read-back in CIELAB, work/al/
     design_opts_al.py) in CIELAB;
  3. every 2x2 block one square: an eye square wins (the reddest); the outline when 2 of its 4 squares are outline on
     the silhouette's edge (3 inside the figure); else the majority of its other colours, ties the darker;
  4. FIX: the near eye's extra square above it -> the brow (both eyes on one row: near 2 squares, far 1); the nose
     ring, lost to the ivory and bronze in the halving, two silver squares under the snout;
  5. on the 128x128 canvas at 8x: the soles on row 99, the middle of the hooves (the lowest three rows) on column 64;
  6. strips.complete_outline (one outline square outside every light edge, nothing under the soles);
  7. HORNS (the user: 「我说的是鼻子上那个鼻环下面一条杠」「当然牛角也有问题」, picked B): the right shackle's bronze rim that
     touched the chin under the nose ring (canvas row 84) -> beard and iron; the image-left horn - halved from the
     draft's Z-shaped horn into a pale blob whose banded tip poked under the near eye - is replaced by the right horn
     mirrored about column 73 (both horns now curve up from the sides of the head, as League's), its old squares
     painted as the shoulder (above row 73) and the lavender chest (below), the iron band 3 rows under its tip.
--check compares the result with the committed alistar_native.png instead of writing it.
"""
import argparse
import os
import sys
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "alistar", "codex_model")
RAW = os.path.join(SRC, "alistar_generated_A.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "alistar_native.png")
SOLE_ROW, MID_COL = 99, 64
FEET_ROWS = 3
PALETTE = ["#A8826E", "#733DF5", "#FB120D", "#150B4B", "#048AFC", "#F5B743", "#90379B", "#C3FAFD", "#421714", "#0153D9",
           "#C8672F", "#F47589", "#FBD59B", "#5526C3", "#873E28", "#9A63F3", "#18B8FB", "#56E1FD", "#3B1888", "#443A3F",
           "#FAF1D6", "#120319", "#E1B590", "#BB88FB"]
OUTLINE = "#120319"
EYE = "#FB120D"
EYES = [(43, 52), (44, 53), (44, 54), (44, 62)]       # eye squares of the read-back (row, col)
BROW = (0x3B, 0x18, 0x88)
SILVER, SILVER_D = (0xD8, 0xDC, 0xE4), (0x8E, 0x96, 0xA2)
# (row, col) on the halved 44 x 41 figure -> colour. The options sheet the user picked from labelled the read-back by
# its k-means assignment; mapping to the rounded palette by nearest colour differs in three squares - kept as shown.
SHOWN = {(8, 24): (0x18, 0xB8, 0xFB), (28, 27): (0x3B, 0x18, 0x88), (31, 6): (0xA8, 0x82, 0x6E)}
FIX = {**SHOWN,(21, 27): BROW,                 # the near eye's top square: brow, so both eyes sit on row 22
       (26, 30): SILVER_D, (27, 30): SILVER}   # the nose ring


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def hexrgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def srgb2lab(c):
    c = np.asarray(c, float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def read_back():
    a = regrid(np.asarray(Image.open(lp(RAW)).convert("RGBA")))[0]
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], op[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def to_index(a, op, pal):
    lab_p = srgb2lab(pal)
    lab = srgb2lab(a[..., :3])
    d = ((lab[..., None, :] - lab_p[None, None]) ** 2).sum(-1)
    idx = d.argmin(-1)
    idx[~op] = -1
    return idx


def halve(idx, pal, outline, eyes):
    H, W = idx.shape
    eyeset = set(eyes)
    H2, W2 = (H + 1) // 2, (W + 1) // 2
    pad = np.full((H2 * 2, W2 * 2), -1)
    pad[:H, :W] = idx
    out = np.full((H2, W2), -1)
    for y in range(H2):
        for x in range(W2):
            ops = [int(v) for v in pad[2 * y:2 * y + 2, 2 * x:2 * x + 2].ravel() if v >= 0]
            if len(ops) < 2:
                continue
            cnt = Counter(ops)
            inner = Counter({k: v for k, v in cnt.items() if k != outline})
            inblk = [(yy, xx) for yy in (2 * y, 2 * y + 1) for xx in (2 * x, 2 * x + 1) if (yy, xx) in eyeset]
            if inblk:
                out[y, x] = max((idx[p] for p in inblk), key=lambda k: int(pal[k][0]) + int(pal[k][2]) - int(pal[k][1]))
            elif cnt.get(outline, 0) >= (2 if len(ops) < 4 else 3) or not inner:
                out[y, x] = outline
            else:
                top = max(inner.values())
                out[y, x] = min([k for k, v in inner.items() if v == top], key=lambda k: lum(pal[k]))
    return out


def build():
    pal = np.array([hexrgb(h) for h in PALETTE])
    outline = PALETTE.index(OUTLINE)
    a, op = read_back()
    idx = to_index(a, op, pal)
    h = halve(idx, pal, outline, EYES)
    fig = np.zeros(h.shape + (4,), np.uint8)
    m = h >= 0
    fig[m, :3] = pal[h[m]]
    fig[m, 3] = 255
    can = np.pad(fig, ((2, 2), (2, 2), (0, 0)))
    sole = 2 + int(np.nonzero(m.any(1))[0].max())
    can, _, _ = strips.complete_outline(can, color=tuple(hexrgb(OUTLINE)), feet=sole)
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    for (r, c), col in FIX.items():
        fig[r, c, :3] = col
        fig[r, c, 3] = 255
    feet = np.nonzero((fig[-FEET_ROWS:, :, 3] > 0).any(0))[0]
    mid = int(round((feet.min() + feet.max()) / 2))
    can = np.zeros((128, 128, 4), np.uint8)
    y0, x0 = SOLE_ROW + 1 - fig.shape[0], MID_COL - mid
    can[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    horns(can)
    ys, xs = np.nonzero(can[..., 3] > 0)
    fig = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return np.asarray(Image.fromarray(can).resize((1024, 1024), Image.NEAREST)), fig


def horns(can):
    """Step 7 on the 128x128 canvas at 1x (rows / columns are canvas squares)."""
    c = {k: np.array(hexrgb(v) + [255], np.uint8) for k, v in dict(
        OL=OUTLINE, beard="#3B1888", iron="#443A3F", shoulder="#733DF5", chest="#9A63F3").items()}
    ivory = [np.array(hexrgb(v) + [255], np.uint8) for v in ("#A8826E", "#E1B590", "#FAF1D6")]
    a0 = can.copy()
    can[84, 74] = can[84, 75] = can[83, 76] = c["beard"]
    can[84, 76] = can[84, 77] = can[84, 78] = c["iron"]
    old = [(y, x) for y in range(64, 82) for x in range(60, 71)
           if any((can[y, x] == v).all() for v in ivory + [c["iron"]])]
    rh = {(y, x) for y in range(64, 83) for x in range(76, 86) if any((a0[y, x] == v).all() for v in ivory)}
    rim = {(y + dy, x + dx) for (y, x) in rh for dy in (-1, 0, 1) for dx in (-1, 0, 1)}
    rim = {p for p in rim if p not in rh and (a0[p] == c["OL"]).all()}
    for (y, x) in old:
        can[y, x] = c["shoulder"] if y < 73 else c["chest"]
    for (y, x) in rh | rim:
        can[y, 146 - x] = a0[y, x]
    top = min(y for y, _ in rh)
    for (y, x) in rh:
        if y == top + 3:
            can[y, 146 - x] = c["iron"]


def review(fig, path):
    """The design at 12x with a grid, at 1x on the arena colour and on the dark card colour."""
    z = 12
    big = Image.fromarray(fig).resize((fig.shape[1] * z, fig.shape[0] * z), Image.NEAREST)
    W, H = big.width + 160, big.height + 20
    img = Image.new("RGB", (W, H), (225, 225, 225))
    img.paste(big, (10, 10), big)
    d = ImageDraw.Draw(img)
    for x in range(0, fig.shape[1] + 1, 5):
        d.line([(10 + x * z, 10), (10 + x * z, 10 + big.height)], fill=(0, 150, 0))
    for y in range(0, fig.shape[0] + 1, 5):
        d.line([(10, 10 + y * z), (10 + big.width, 10 + y * z)], fill=(0, 150, 0))
    small = Image.fromarray(fig)
    for i, bg in enumerate(((92, 98, 86), (30, 30, 40))):
        s = Image.new("RGB", (fig.shape[1] + 8, fig.shape[0] + 8), bg)
        s.paste(small, (4, 4), small)
        img.paste(s.resize((s.width * 2, s.height * 2), Image.NEAREST), (big.width + 30, 10 + i * (s.height * 2 + 10)))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    a = ap.parse_args()
    out, fig = build()
    print("figure", fig.shape[:2], "colours", len({tuple(p) for p in fig[fig[..., 3] > 0][:, :3]}))
    if a.review:
        review(fig, a.review)
    if a.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        print("identical" if np.array_equal(old, out) else "DIFFERENT")
        return
    os.makedirs(os.path.dirname(lp(OUT)), exist_ok=True)
    Image.fromarray(out).save(lp(OUT))
    print(OUT)


if __name__ == "__main__":
    main()
