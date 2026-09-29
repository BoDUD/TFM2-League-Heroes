#!/usr/bin/env python3
"""Tidy Codex's step-2 redraw of the 18 heroes (model_strips_18: every strip drawn from the approved design) into
the native strips.

    python tools/art/tidy_codex18.py <hero> <Codex's delivery folder>

Codex delivers <hero>_<tag>.png for every tag of assets/source/native/<hero>_cells.json, on the same cells, every
game pixel an 8x8 block, the design's palette and its head pasted into every frame. One thing is fixed here on the
game pixels before the strips are written to assets/source/native/: the doubled outline. A study of the LoL Reborn
pack (oppi) against ours found our designs use black as the shadow tone, so the ring just inside the 1-px outline
is black as well (inner-ring black 0.58 against oppi's 0.30 and the base game's 0.20), and hair, cloth and thin
props melt into the outline at game size. Per frame:
  - a near-black pixel on the silhouette's edge with at most one opaque 4-neighbour (an outline spur) goes;
    coloured pixels are never removed (chains, braids and wand tips are 1 px wide);
  - a near-black pixel just inside the edge takes the darkest of its lighter 8-neighbours (at least two of them):
    the material's own dark shade instead of a second ring of black;
  - a lone pixel inside an area (its colour on none of its four neighbours, three or four of which share one
    colour) takes that colour: the specks of noise (Fiddlesticks's red and grey dots in his dark wood). Lines stay:
    a pixel of a chain, a crack or an edge has at least two neighbours of its own colour or of different ones.
The face round the eyes (EYE_COLOURS) is left alone. Then run import_native.py --hero <hero>.
Fiddlesticks and Kayle (merged before the 18) are cleaned the same way in place: their own
assets/source/native folder is the delivery.
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

SRC = os.path.join(ROOT, "assets", "source", "native")
Z = 8
DARK = 40                       # luma under this is "black" (outline, black shadow)
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))
# the colours of each hero's eyes in Codex's delivery (Thresh's green glints are also on his hood flame and lantern:
# only the pixels round the eyes are kept, see protected())
EYE_COLOURS = {"thresh": [(13, 200, 78), (4, 71, 29)],
               # merged before the 18 (PRs #27 and #26), cleaned the same way in place: run with their own
               # assets/source/native folder as the delivery
               "fiddlesticks": [(200, 224, 96)], "kayle": [(226, 138, 8)]}


def blocks(path):
    a = np.asarray(Image.open(G.lp(path)).convert("RGBA"))
    if a.shape[0] % Z or a.shape[1] % Z:
        sys.exit(f"{path}: {a.shape[1]}x{a.shape[0]} is not a multiple of {Z}")
    b = a.reshape(a.shape[0] // Z, Z, a.shape[1] // Z, Z, 4)
    if not (b == b[:, :1, :, :1]).all():
        sys.exit(f"{path}: not made of flat {Z}x{Z} blocks")
    out = b[:, 0, :, 0].copy()
    if not set(np.unique(out[..., 3])) <= {0, 255}:
        sys.exit(f"{path}: semi-transparent pixels")
    return out


def lum(rgb):
    rgb = rgb.astype(float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def protected(a, colours):
    """The face: from 2 rows over the eyes to 4 rows under them, 3 columns either side (sockets, lashes, brows and
    the mouth - Kayle's mouth is one lone red pixel)."""
    op = a[..., 3] > 0
    m = np.zeros(op.shape, bool)
    for c in colours:
        m |= op & np.all(a[..., :3] == np.array(c, np.uint8), -1)
    grown = m.copy()
    for dy in range(-2, 5):
        for dx in range(-3, 4):
            grown |= shifted(m, dy, dx)
    return grown


def one_outline(a, colours=()):
    """One frame at game size: outline spurs off, the second ring of black turned into the material's dark shade."""
    a = a.copy()
    keep = protected(a, colours)
    for _ in range(2):
        op = a[..., 3] > 0
        cnt = sum(shifted(op, dy, dx).astype(int) for dy, dx in N4)
        a[op & (lum(a[..., :3]) < DARK) & (cnt <= 1) & ~keep] = 0
    op = a[..., 3] > 0
    L = lum(a[..., :3])
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    ring2 = np.zeros_like(op)
    for dy, dx in N4:
        ring2 |= shifted(edge, dy, dx)
    ring2 &= op & ~edge & (L < DARK) & ~keep
    H, W = op.shape
    out = a.copy()
    for y, x in zip(*np.nonzero(ring2)):
        cols = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N8
                if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and L[y + dy, x + dx] >= DARK]
        if len(cols) >= 2:
            out[y, x] = min(cols, key=lambda c: (lum(np.array(c[:3])), -cols.count(c)))
    return despeckle(out, keep)


def despeckle(a, keep):
    """Lone pixels inside an area take the colour of the area (3 or 4 of the 4 neighbours share it)."""
    op = a[..., 3] > 0
    H, W = op.shape
    out = a.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or keep[y, x]:
                continue
            nb = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N4]
            me = tuple(int(v) for v in a[y, x])
            if me in nb or any(n[3] == 0 for n in nb):
                continue
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 3:
                out[y, x] = best
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero")
    ap.add_argument("delivery")
    a = ap.parse_args()
    h = a.hero
    with open(G.lp(os.path.join(SRC, f"{h}_cells.json")), encoding="utf-8") as f:
        spec = json.load(f)
    cw, ch = spec["cell"]
    colours = EYE_COLOURS.get(h, [])
    for tag in spec["tags"]:
        new = blocks(os.path.join(a.delivery, f"{h}_{tag}.png"))
        old = blocks(os.path.join(SRC, f"{h}_{tag}.png"))
        if new.shape != old.shape:
            sys.exit(f"{h}_{tag}.png: {new.shape[1]}x{new.shape[0]} game pixels, the cells need "
                     f"{old.shape[1]}x{old.shape[0]}")
        out = new.copy()
        for y in range(0, new.shape[0], ch):
            for x in range(0, new.shape[1], cw):
                out[y:y + ch, x:x + cw] = one_outline(new[y:y + ch, x:x + cw], colours)
        n = int((out != new).any(-1).sum())
        Image.fromarray(np.repeat(np.repeat(out, Z, 0), Z, 1)).save(G.lp(os.path.join(SRC, f"{h}_{tag}.png")))
        print(f"{h}_{tag}.png: {n} pixels of the doubled outline changed")


if __name__ == "__main__":
    main()
