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


def pixelate(a, k, pivot, outline, pal=None):
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
    if pal is None:
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




# ------------------------------------------------------------------------------------------------- flat pixel art
DARK_SUM = 70                    # r + g + b under this: outline / black lines, never recoloured
# squares kept as drawn, per hero (ppu_restyle RESTYLE crisp keep): league_mordekaiser's teal glow - his eyes are a few
# teal squares in his visor, dark ones round bright ones, and the cleanup took them (「铁男的眼睛完全看不到了」)
def _face(a):
    """The face: skin in the upper half of the figure grown 2 squares and its holes filled (eyes, brows, mouth) -
    league_garen's eyes became a black band under the lines pass (「盖伦也要调一下吧 像素」)."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] > 0
    skin = op & (rgb[..., 0] > 170) & (rgb[..., 1] > 110) & (rgb[..., 2] > 80) & (rgb[..., 0] - rgb[..., 2] > 40)
    rows = np.nonzero(op.any(1))[0]
    if not len(rows):
        return skin
    skin[rows.min() + (rows.max() - rows.min()) // 2:] = False
    if not skin.any():
        return skin
    m = ndimage.binary_fill_holes(ndimage.binary_dilation(skin, iterations=2))
    return m & op


def _face_blue(a):
    """league_soraka's face: her light blue skin in the top third of the figure (her arms and legs are blue too) grown 2
    squares and its holes filled (eyes, mouth)."""
    rgb = a[..., :3].astype(int)
    op = a[..., 3] > 0
    skin = op & (rgb[..., 2] > rgb[..., 0] + 30) & (rgb[..., 2] > 150) & (rgb[..., 1] > 100) & (rgb[..., 0] > 80)
    rows = np.nonzero(op.any(1))[0]
    if not len(rows):
        return skin
    skin[rows.min() + (rows.max() - rows.min()) // 3:] = False
    if not skin.any():
        return skin
    m = ndimage.binary_fill_holes(ndimage.binary_dilation(skin, iterations=2))
    return m & op


def _thin_warm(a):
    """Thin gold / orange parts (league_soraka's staff: the lines pass turned its 2-3 squares wide shaft black): warm
    squares that a horizontal or vertical run of 5 cannot cover."""
    rgb = a[..., :3].astype(int)
    warm = (a[..., 3] > 0) & (rgb[..., 0] > 150) & (rgb[..., 0] > rgb[..., 2] + 60)
    wide = (ndimage.binary_opening(warm, structure=np.ones((1, 5))) |
            ndimage.binary_opening(warm, structure=np.ones((5, 1))))
    return ndimage.binary_dilation(warm & ~wide) & (a[..., 3] > 0)


KEEP = {"teal": lambda a: (a[..., 1].astype(int) > a[..., 0] + 40) & (a[..., 2].astype(int) > a[..., 0] + 40),
        "face": _face, "face_blue": _face_blue, "soraka": lambda a: _face_blue(a) | _thin_warm(a)}


def _lab(rgb):
    """sRGB (..., 3) 0-255 -> CIE Lab (D65)."""
    c = rgb / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    xyz = c @ np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]).T
    xyz /= np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def crisp(frames, n=16, passes=2, contrast=1.2, lines=True, keep=None, seed=0, fit=None):
    """A hero's frames brought to flat pixel art like league_zeri's (the user, 2026-10-13: 「铁男感觉还是没泽丽那么像素啊」,
    picked 16 colours + lines from a preview): one palette for every frame (no colour flicker between them) -
    contrast stretched round the hero's mean colour, the non-dark colours cut to n (k-means in Lab, each colour the
    mean of its members); `passes` majority passes (a square unlike its 8 neighbours takes their commonest colour
    when 4 or more share it); then a dark line on the darker side of every edge between two parts far apart in
    brightness (luminance jump over 70: the square at half its brightness). Outline / black squares stay, and so do the
    ones `keep` names (KEEP).
    frames: [RGBA uint8] -> new list. fit: the frames the palette is taken from instead (league_mordekaiser's narrowed
    run: the palette of the frames before, so no other frame changes)."""
    ops = [f[..., 3] > 0 for f in frames]
    src = fit if fit is not None else frames
    px = np.concatenate([f[f[..., 3] > 0][:, :3].astype(float) for f in src])
    mu = px.mean(0)
    stretch = lambda x: np.clip(mu + (x - mu) * contrast, 0, 255)
    sp = stretch(px)
    lit = sp.sum(1) >= DARK_SUM
    rng = np.random.default_rng(seed)
    sample = sp[lit][rng.choice(int(lit.sum()), min(int(lit.sum()), 40000), replace=False)]
    lab_s = _lab(sample)
    centres = lab_s[rng.choice(len(lab_s), n, replace=False)]
    for _ in range(25):
        idx = ((lab_s[:, None] - centres[None]) ** 2).sum(-1).argmin(1)
        for j in range(n):
            if (idx == j).any():
                centres[j] = lab_s[idx == j].mean(0)
    idx = ((lab_s[:, None] - centres[None]) ** 2).sum(-1).argmin(1)
    colours = np.array([sample[idx == j].mean(0) if (idx == j).any() else sample[0] for j in range(n)])
    out = []
    for f, op in zip(frames, ops):
        a = f.copy()
        rgb = stretch(a[..., :3].astype(float))
        glow = (op & KEEP[keep](a)) if keep else np.zeros_like(op)
        m = op & ~glow & (rgb.sum(-1) >= DARK_SUM) & (a[..., :3].astype(int).sum(-1) >= DARK_SUM)
        if m.any():
            j = ((_lab(rgb[m])[:, None] - centres[None]) ** 2).sum(-1).argmin(1)
            a[m, :3] = np.clip(colours[j].round(), 0, 255).astype(np.uint8)
        for _ in range(passes):
            a = _majority(a, op, glow)
        if lines:
            a = _edge_lines(a, op, glow)
        out.append(a)
    return out


def _majority(a, op, glow):
    H, W = op.shape
    key = (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2]
    key = np.where(op, key, -1)
    pk = np.pad(key, 1, constant_values=-1)
    nb = np.stack([pk[1 + dy:1 + dy + H, 1 + dx:1 + dx + W] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                   if (dy, dx) != (0, 0)])                       # (8, H, W)
    same = (nb[:, None] == nb[None]) & (nb[None] >= 0)          # (8, 8, H, W)
    cnt = same.sum(1)                                           # how many neighbours share neighbour i's colour
    cnt = np.where(nb >= 0, cnt, 0)
    best = np.take_along_axis(nb, cnt.argmax(0)[None], 0)[0]
    bestn = cnt.max(0)
    own = (nb == key[None]).sum(0)
    valid = (nb >= 0).sum(0)
    dark = a[..., :3].astype(int).sum(-1) < DARK_SUM
    change = op & ~dark & ~glow & (own <= 1) & (bestn >= 4) & (valid >= 6) & (best >= 0)
    b = a.copy()
    b[change, 0] = (best[change] >> 16) & 255
    b[change, 1] = (best[change] >> 8) & 255
    b[change, 2] = best[change] & 255
    return b


def _edge_lines(a, op, glow, jump=70, k=0.5):
    lum = a[..., :3].astype(float).mean(-1)
    H, W = op.shape
    pl = np.pad(np.where(op, lum, -1e9), 1, constant_values=-1e9)
    brighter = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nb = pl[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
        brighter |= nb - lum > jump
    m = op & ~glow & brighter & (lum >= 25)
    b = a.copy()
    b[m, :3] = (a[m, :3] * k).astype(np.uint8)
    return b
