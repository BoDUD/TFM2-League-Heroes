#!/usr/bin/env python3
"""league_nilah's dense design (PPU 2.5) from Codex's step 0 (front) and step 1 (side), on one 85 x 128 grid.

    python tools/art/design_nilah_hd.py [--side A|B] [--preview DIR]

The user picked picture A (the folded whip-blade raised upright), 99 squares head to soles kept 1:1, PPU 2.5
(2026-10-13). So:
  1. front = picture A read back on its own 12-px grid (regrid.py, 64 x 106) laid on the step-1 grid (pack_nilah_model.py:
     blade tip row 10, hair row 15, soles row 115, standing point column 42);
  2. one palette: the front's own K Lab k-means colours (design_varus.kmeans; the read-back had ~2400 near colours);
  3. side = Codex's step-1 side take (assets/source/nilah/codex_model): drawn on ~10-px (A) / ~8.5-px (B) squares at
     its own scale, not on the 12-px grid it was asked for. Every source pixel is snapped to the palette, then each
     square of the grid takes the palette colour most of its source pixels have (an area vote, so no mixed mud),
     scaled so the blade tip and the soles land on the front's rows 10 and 115, the feet's middle on column 42.
Writes assets/source/nilah/hd/front.png and side.png (one square = one dense pixel, 85 x 128).
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_varus as dv  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nilah")
OUT = os.path.join(SRC, "hd")
SQ, COLS, ROWS = 12, 85, 128
TOP, SOLE, MID = 10, 115, 42
K = 36


def readback():
    """Picture A read back on its own grid and laid on the step-1 grid (pack_nilah_model.py's layout)."""
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_rg_A.png")
    subprocess.run([sys.executable, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts", "regrid.py"),
                    os.path.join(SRC, "codex_picture", "nilah-model-A.png"), tmp, "--size", str(SQ)],
                   check=True, capture_output=True)
    r = np.array(Image.open(tmp).convert("RGBA"))
    os.remove(tmp)
    r[..., 3] = np.where(r[..., 3] > 0, 255, 0)
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    can[TOP:TOP + r.shape[0], MID - 34:MID - 34 + r.shape[1]] = r
    return can


def snap_idx(rgb, pal):
    lab = dv.srgb2lab(rgb.astype(float))
    pl = dv.srgb2lab(pal.astype(float))
    out = np.empty(lab.shape[:-1], int)
    flat, fo = lab.reshape(-1, 3), out.reshape(-1)
    for i in range(0, len(flat), 200000):
        fo[i:i + 200000] = ((flat[i:i + 200000, None] - pl[None]) ** 2).sum(-1).argmin(1)
    return out


def side(path, pal):
    """Codex's side take onto the grid by an area vote of palette indices."""
    a = np.array(Image.open(path).convert("RGBA"))
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    tip, sole = ys.min(), ys.max() + 1
    s = (sole - tip) / (SOLE + 1 - TOP)
    low = op[sole - int(3 * s):sole]                      # the feet: the lowest three squares
    fx = np.nonzero(low.any(0))[0]
    mid = (fx.min() + fx.max() + 1) / 2
    idx = np.where(op, snap_idx(a[..., :3], pal), -1)
    g = np.zeros((ROWS, COLS, 4), np.uint8)
    for r in range(ROWS):
        y0 = sole - (SOLE + 1 - r) * s
        for c in range(COLS):
            x0 = mid + (c - MID - 0.5) * s
            ya, yb, xa, xb = int(round(y0)), int(round(y0 + s)), int(round(x0)), int(round(x0 + s))
            if yb <= 0 or xb <= 0 or ya >= a.shape[0] or xa >= a.shape[1]:
                continue
            cell = idx[max(ya, 0):yb, max(xa, 0):xb].ravel()
            if (cell >= 0).sum() * 2 < cell.size:
                continue
            v = np.bincount(cell[cell >= 0], minlength=len(pal))
            g[r, c, :3] = pal[v.argmax()]
            g[r, c, 3] = 255
    print(f"side {os.path.basename(path)}: {s:.2f} px a square, feet middle x {mid:.0f}")
    return g


# The front's head (memory one-face-all-frames: every frame keeps the idle's 3/4 head): rows 15-37 (row 37 the chin's
# outline), columns 30-60; from row 35 down only columns 38 on (the ponytail's start to the left is the side's own).
HEAD = (15, 38, 30, 61, 35, 38)
# per side take: the rows / columns cleared first (its own smaller head; the blade behind her stays) and the shift that
# puts the front's chin (row 37) on the take's chin (row 35) over its face's middle
SIDE_HEAD = {"A": dict(clear=(12, 35, 33, 61), dy=-2, dx=0), "B": dict(clear=(12, 35, 33, 61), dy=-2, dx=-1)}


def paste_head(front, sd, spec):
    r0, r1, c0, c1, low, lc = HEAD
    cr0, cr1, cc0, cc1 = spec["clear"]
    out = sd.copy()
    out[cr0:cr1, cc0:cc1] = 0
    for r in range(r0, r1):
        for c in range(c0, c1):
            if front[r, c, 3] and (r < low or c >= lc):
                out[r + spec["dy"], c + spec["dx"]] = front[r, c]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--side", default="A")
    ap.add_argument("--preview")
    a = ap.parse_args()
    front = readback()
    _, pal = dv.kmeans(front, K)
    op = front[..., 3] > 0
    front[op, :3] = pal[snap_idx(front[op][:, :3], pal)]
    sd = side(os.path.join(SRC, "codex_model", f"nilah-side-{a.side}.png"), pal)
    sd = paste_head(front, sd, SIDE_HEAD[a.side])
    Image.fromarray(front).save(os.path.join(OUT, "front.png"))
    Image.fromarray(sd).save(os.path.join(OUT, "side.png"))
    print("colours", len(pal), "front", len(np.unique(front[op][:, :3], axis=0)))
    if a.preview:
        os.makedirs(a.preview, exist_ok=True)
        z = 6
        bg = Image.new("RGBA", (COLS * 2 * z, ROWS * z), (225, 225, 225, 255))
        for i, im in enumerate((front, sd)):
            bg.alpha_composite(Image.fromarray(im).resize((COLS * z, ROWS * z), Image.NEAREST), (i * COLS * z, 0))
        bg.convert("RGB").save(os.path.join(a.preview, f"nilah_design_side{a.side}.png"))


if __name__ == "__main__":
    main()
