#!/usr/bin/env python3
"""Bringing dense (PPU) frames to a coarser grid the way the user took for the PPU heroes (2026-10-13, league_zeri's look:
「都要像泽丽那样像素多但是有清晰的感觉」「要有像素风」): each square the mean of its pixels snapped to the frame's own
commonest colours, near-black squares outline, single odd squares merged. tools/art/ppu_restyle.py (the game frames) and
tools/art/ppu_hd.py (the lo_ frames the BP / encyclopedia / pick screens draw) use it.
"""
import os
import re

import numpy as np
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])


def edge_colour(a):
    """The commonest colour on the outer edge (the hero's outline colour)."""
    op = a[..., 3] > 0
    edge = op & ~ndimage.binary_erosion(op, structure=CROSS)
    cols, n = np.unique(a[edge][:, :3], axis=0, return_counts=True)
    return tuple(int(v) for v in cols[np.argmax(n)]) if len(n) else (0, 0, 0)


def sizes_of():
    """addons/league_main/src/hd.rs SIZES -> {hero: size} (league_gragas 0.80 -> gragas 0.8)."""
    src = open(os.path.join(ROOT, "addons", "league_main", "src", "hd.rs"), encoding="utf-8").read()
    m = re.search(r"pub const SIZES[^=]*=\s*&\[(.*?)\];", src, re.S)
    return {h: float(v) for h, v in re.findall(r'\("league_(\w+)",\s*([0-9.]+)\)', m.group(1))} if m else {}


def palette_of(a, n=64):
    """The frame's own commonest colours (opaque), at most n."""
    px = a[a[..., 3] > 0][:, :3]
    if not len(px):
        return np.zeros((1, 3))
    cols, cnt = np.unique(px, axis=0, return_counts=True)
    return cols[np.argsort(-cnt)[:n]].astype(float)


def despeckle(a):
    """A single square whose four neighbours all share one other colour takes that colour (near-black ones stay:
    eyes, lines)."""
    key = (a[..., 0].astype(np.int64) << 24) | (a[..., 1].astype(np.int64) << 16) |           (a[..., 2].astype(np.int64) << 8) | a[..., 3].astype(np.int64)
    p = np.pad(key, 1, constant_values=-1)
    up, dn, lf, rt = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
    m = (up == dn) & (dn == lf) & (lf == rt) & (up != key) & (up >= 0) & (a[..., 3] > 0) &         (a[..., :3].astype(int).sum(-1) >= 70)
    out = a.copy()
    ys, xs = np.nonzero(m)
    out[ys, xs] = a[ys - 1, xs]
    return out


def pixelate(a, k, pivot, outline):
    """`a` (a dense frame, its pivot at `pivot` = (x, y)) brought to k times as many pixels a side (k < 1): squares of
    1/k dense pixels on a grid through the pivot. Each square: the mean of its opaque pixels snapped to the frame's own
    64 commonest colours (clean shading, no stray colours), clear where half or more is clear, the outline colour where
    40 % or more is near-black (eyes, lines) or, on the silhouette's edge, a quarter or more; single squares unlike all
    four neighbours take theirs. -> (frame, new pivot)."""
    H, W = a.shape[:2]
    c = 1.0 / k
    px, py = pivot
    nx0, ny0 = int(np.ceil(px / c)), int(np.ceil(py / c))          # squares left of / above the pivot
    nx1, ny1 = int(np.ceil((W - px) / c)), int(np.ceil((H - py) / c))
    Wn, Hn = nx0 + nx1, ny0 + ny1
    cx = np.floor((np.arange(W) + 0.5 - px) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - py) / c).astype(int) + ny0
    cell = (cy[:, None] * Wn + cx[None, :]).ravel()
    n = Hn * Wn
    op = (a[..., 3] > 0).ravel().astype(float)
    tot = np.bincount(cell, minlength=n)
    na = np.bincount(cell, weights=op, minlength=n)
    rgb = np.stack([np.bincount(cell, weights=a[..., c_].ravel() * op, minlength=n) for c_ in range(3)], 1)
    rgb /= np.maximum(na, 1)[:, None]
    alpha = np.bincount(cell, weights=a[..., 3].ravel().astype(float), minlength=n) / np.maximum(na, 1)
    dark = np.bincount(cell, weights=((a[..., :3].astype(int).sum(-1) < 70).ravel() * op), minlength=n)
    dark = (dark / np.maximum(tot, 1)).reshape(Hn, Wn)
    keep = ((na > 0) & (na * 2 >= tot)).reshape(Hn, Wn)
    pal = palette_of(a)
    rgb = rgb.reshape(Hn, Wn, 3)
    d = ((rgb[..., None, :] - pal[None, None]) ** 2).sum(-1)
    col = pal[np.argmin(d, -1)]
    out = np.zeros((Hn, Wn, 4), np.uint8)
    out[keep, :3] = col[keep]
    out[keep, 3] = np.clip(np.round(alpha.reshape(Hn, Wn)[keep]), 1, 255)
    edge = keep & ~ndimage.binary_erosion(keep, structure=CROSS)
    m = keep & ((dark >= 0.4) | (edge & (dark >= 0.25)))
    out[m, :3] = outline
    return despeckle(out), (nx0, ny0)


