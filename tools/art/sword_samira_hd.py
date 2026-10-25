#!/usr/bin/env python3
"""Samira's greatsword straight on her PPU 2.84 design (the user, 2026-10-25: 「背后的武器看起来是歪的」): Codex drew the
blade in two pieces off one line - the grip and the guard by her head point one way, the blade showing past her leg
lies 12 squares to the right and steeper. The pommel, the tassel, the grip and the guard stay as drawn; the blade is
drawn again by code (Caitlyn's way for straight props) along one line from the guard to the tip beside her far foot,
behind her: the old blade's squares where they show (between her near arm and her body, past her leg) taken off, the
new blade laid under the figure, in the old blade's own shades across its width (the light edge up), its outline
closed.

    sword(d) -> d with the straight blade (used by tools/art/design_samira_hd.py)
"""
import numpy as np
from scipy import ndimage

H = lambda s: [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in s.split()]  # noqa: E731
# the blade's shades across its width, the light edge first (Codex's own: the old blade past her leg)
SHADES = H("E9EBF2 CED0DB A7AAB6 8C8D95 6B6C77 47414A")
BLADE = set(SHADES)
OUTLINE = (0x0C, 0x0A, 0x11)
GUARD = (21.5, 28.0)            # where the blade leaves the guard (design squares, x y)
TIP = (75.0, 102.5)             # its tip, beside her far foot
WIDTH = 6.0                     # squares across the blade
TAPER = 9.0                     # squares over which it narrows to the tip
SPECK = 4
# where the old blade shows: between her near arm and her body, and past her leg (x0, x1, y0, y1)
OLD = [(17, 32, 29, 51), (55, 77, 61, 105)]


def sword(d):
    d = d.copy()
    h, w = d.shape[:2]
    op = d[..., 3] > 0
    cols = np.array([[tuple(d[y, x, :3]) in BLADE for x in range(w)] for y in range(h)])
    old = np.zeros((h, w), bool)
    for x0, x1, y0, y1 in OLD:
        old[y0:y1, x0:x1] = True
    take = old & op & cols
    d[take] = 0
    # the old blade's outline left alone in the open: dark squares there touching nothing but the cleared / background
    op = d[..., 3] > 0
    dark = op & np.all(d[..., :3] == OUTLINE, -1)
    body = op & ~dark
    near_body = ndimage.binary_dilation(body, structure=np.ones((3, 3)))
    d[old & dark & ~near_body] = 0
    # the new blade, behind her
    yy, xx = np.mgrid[0:h, 0:w]
    gx, gy = GUARD
    tx, ty = TIP
    L = np.hypot(tx - gx, ty - gy)
    ux, uy = (tx - gx) / L, (ty - gy) / L
    px, py = xx + 0.5 - gx, yy + 0.5 - gy
    t = px * ux + py * uy                       # along the blade
    s = px * uy - py * ux                       # across it (negative: its upper side, the light edge)
    half = np.where(t > L - TAPER, WIDTH / 2 * np.clip((L - t) / TAPER, 0, 1), WIDTH / 2)
    inside = (t >= 0) & (t <= L) & (np.abs(s) <= half)
    k = np.clip(((s + half) / np.maximum(2 * half, 1e-6) * len(SHADES)).astype(int), 0, len(SHADES) - 1)
    blade = np.zeros_like(d)
    for i, c in enumerate(SHADES):
        m = inside & (k == i)
        blade[m] = (*c, 255)
    ring = ndimage.binary_dilation(inside, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)) & ~inside
    blade[ring] = (*OUTLINE, 255)
    op = d[..., 3] > 0
    put = (blade[..., 3] > 0) & ~op
    d[put] = blade[put]
    # what is left of the old blade's outline standing alone: pieces of up to SPECK squares
    op = d[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    sz = ndimage.sum(op, lbl, range(1, n + 1))
    for i in range(1, n + 1):
        if sz[i - 1] <= SPECK:
            d[lbl == i] = 0
    return d
