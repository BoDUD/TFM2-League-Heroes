#!/usr/bin/env python3
"""Lux's dense (PPU 2.2) design: Codex's step-0 picture read back on its own squares, one and a half to a square.

    python tools/art/design_lux_hd.py [--review DIR] [--out PNG]

Asked (assets/source/lux/PICTURE_PROMPT_PPU.md) for 53 squares of 11 px from her head's top to her soles in League's
idle (the staff held across her front), Codex's image_gen drew one 1254-px picture on its own ~6.7-px squares, 121
rows (hd/raw/lux-generated.png), and its export (hd/raw/lux-A.png) sampled that on 15.7-px cells: the body a jumble
of colours, the face gone. Read on twice its square (60 rows) the armour, the face and the staff's shaft still broke
up (a square takes one of four), so:
- the picture's own squares are read first (design_fiora_hd.grid: one fitted pitch and phase per axis, the median of
  each square's middle half; the semi-transparent rim dropped at alpha 128), cut to COLOURS by k-means in Lab
  (design_varus.kmeans);
- then STEP of them make a design square: the mean in Lab of the parts of the squares it covers (outline squares
  apart), snapped to those colours; the outline where it covers OUTLINE_SHARE of outline, or almost nothing else.
  81 rows: 36.8 game px at PPU 2.2 (her 1x sprite 35-36, Jinx 37) - the face, the armour's trims and the staff kept;
- speckle cleaned as Jinx's (design_jinx_hd.clean: colours nearer than MERGE merged, a square with no same-coloured
  neighbour takes its commonest near-tone one's colour);
- the far eye and the mouth set by hand (FACE: the far eye navy over blue like the near one, the lips the picture's red);
- the staff's shaft drawn straight (Codex's bent at her hand): a line through M at K rows a column, HALF columns each
  way, a cream core (its lower side a shade darker) with the gold spiral's turns every PERIOD squares and an outline
  each side, centrally symmetric about M - a half turn about M lays it on the same squares, the crescent head and the
  small end swapped (rig_lux_hd.py's casts point the head forward that way); the two end pieces as read (HEAD, END:
  the pieces past the shaft), Codex's old shaft round them cleared, the near glove over the shaft (GLOVE).
-> hd/design.png. With --review: <dir>/lux_ppu_size.png (the design next to Lux now and this pack's PPU heroes as the
game draws them, 3 screen pixels a game pixel) and <dir>/lux_ppu_closeup.png (Codex's picture and the design at 8x).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_fiora_hd as FD  # noqa: E402
import design_jinx_hd as JD  # noqa: E402
import design_varus as V  # noqa: E402

HD = os.path.join(ROOT, "assets", "source", "lux", "hd")
RAW = "lux-generated.png"
PITCH = (6.0, 7.5)              # the picture's own square (6.82 x 6.59)
COLOURS = 44
STEP = 1.5                      # its squares to a design square
OUTLINE = (13, 3, 20)
OUTLINE_SHARE = 0.45
PPU = 2.2
FACE = {(40, 21): (28, 47, 112), (40, 22): (18, 127, 224), (37, 26): (195, 59, 58), (38, 26): (195, 59, 58)}
# the staff (design squares)
M = (33.5, 47.5)                # the shaft's middle: a half-square point, so a half turn maps squares onto squares
K = -0.58                       # rows per column: through her glove (26.5, 51.5) and the picture's shaft past her far
                                # arm (44, 41.4) and at its head (14.5, 58.5)
HALF = 19.0                     # columns from M to each end
CORE, EDGE = 0.75, 1.4          # across the shaft: the core, then the outline (Codex's: 1.3 squares of cream, thin edges)
PERIOD = 3.0                    # squares along the shaft between the spiral's gold turns
CREAM, SHADE, GOLD, OUTLINE_SQ = (251, 249, 247), (240, 215, 169), (244, 179, 60), OUTLINE
GLOVE = {(x, y) for x in range(24, 29) for y in range(50, 53)} | {(25, 53), (26, 53), (27, 53)}
HEAD = (lambda x, y: (x <= 18) & (y >= 55), (6, 62))   # where the crescent head lies, and a square of it
END = (lambda x, y: (x >= 46) & (y <= 42), (58, 32))    # the small end
OLD = [(11, 22, 52, 57), (11, 19, 58, 61), (47, 99, 30, 41)]   # x0, x1, y0, y1: Codex's shaft round the new one
# across her body Codex's shaft bent at her hand: its squares beside the new one (cream, white, pale gold, within
# SCRUB_T of the line, columns SCRUB_X) take the body's colour from beyond them in their column
SCRUB_X = (27, 46)
SCRUB_T = 2.7
PALE = {(251, 249, 247), (240, 215, 169), (251, 208, 169), (235, 200, 128), (218, 206, 205), (253, 240, 132),
        (173, 230, 253)}
PEERS = ["lux", "jinx", "varus", "caitlyn", "riven"]


def lp(path):
    return FD.lp(path)


def cover(n, phase=0.0):
    """(design squares x n) weights: how much of each of n squares the design square t covers."""
    t_n = int(np.ceil((n - phase) / STEP))
    w = np.zeros((t_n, n))
    for t in range(t_n):
        a, b = phase + t * STEP, phase + (t + 1) * STEP
        for s in range(int(np.floor(a)), int(np.ceil(b))):
            if 0 <= s < n:
                w[t, s] = max(0.0, min(b, s + 1) - max(a, s))
    return w


def read():
    a = np.asarray(Image.open(lp(os.path.join(HD, "raw", RAW))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    FD.PITCH = PITCH
    n, size = FD.grid(a)
    op = n[..., 3] > 0
    idx, pal = V.kmeans(n, COLOURS)
    q = np.zeros_like(n)
    q[op, :3] = pal[idx[op]]
    out_sq = (op & (np.abs(q[..., :3].astype(int) - np.array(OUTLINE)).sum(-1) < 40)).astype(float)
    lab = color.rgb2lab(q[..., :3] / 255.0)
    plab = color.rgb2lab(pal[None].astype(float) / 255.0)[0]
    wy, wx = cover(n.shape[0]), cover(n.shape[1])
    opf = op.astype(float)
    inner = opf * (1 - out_sq)
    cov, oc, wi = wy @ opf @ wx.T, wy @ out_sq @ wx.T, wy @ inner @ wx.T
    area = wy.sum(1)[:, None] * wx.sum(1)[None, :]
    mean = np.stack([wy @ (lab[..., c] * inner) @ wx.T for c in range(3)], -1) / np.maximum(wi, 1e-9)[..., None]
    k = np.argmin(((mean[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
    keep = cov >= 0.5 * area
    d = np.zeros(cov.shape + (4,), np.uint8)
    d[keep, :3] = pal[k[keep]]
    d[keep & ((oc >= OUTLINE_SHARE * cov) | (wi < 0.2 * area)), :3] = OUTLINE
    d[keep, 3] = 255
    ys, xs = np.nonzero(d[..., 3])
    return JD.clean(d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]), size


def shaft(shape):
    """{(x, y): rgb} the straight shaft (a half turn about M maps it onto itself, colours and all)."""
    u = np.array((1.0, K)) / math.hypot(1, K)
    n = np.array((-u[1], u[0]))
    smax = HALF * math.hypot(1, K)
    out = {}
    for y in range(shape[0]):
        for x in range(shape[1]):
            v = np.array((x + 0.5 - M[0], y + 0.5 - M[1]))
            s, t = float(v @ u), float(v @ n)
            if abs(s) > smax or abs(t) > EDGE:
                continue
            side = 1 if s >= 0 else -1
            if abs(t) <= CORE:
                w = math.cos(2 * math.pi * (abs(s) + 0.8 * t * side) / PERIOD)
                out[(x, y)] = GOLD if w > 0.5 else (CREAM if t * side <= 0 else SHADE)
            else:
                out[(x, y)] = OUTLINE_SQ
    return out


def staff_masks(d):
    """(shaft squares, head, end) masks of the design: the shaft's band and the end pieces past it."""
    op = d[..., 3] > 0
    band = np.zeros(op.shape, bool)
    for (x, y) in shaft(op.shape):
        band[y, x] = True
    yy, xx = np.mgrid[0:op.shape[0], 0:op.shape[1]]

    def piece(spec):
        region, (sx, sy) = spec
        lbl, _ = ndimage.label(op & ~band & region(xx, yy), structure=np.ones((3, 3)))
        return lbl == lbl[sy, sx]

    return band, piece(HEAD), piece(END)


def across(x, y):
    """The square's distance from the shaft's line (+ below it)."""
    u = np.array((1.0, K)) / math.hypot(1, K)
    return float(np.array((x + 0.5 - M[0], y + 0.5 - M[1])) @ np.array((-u[1], u[0])))


def restaff(d):
    """The design with its shaft drawn straight (Codex's old shaft round it cleared)."""
    band, head, end = staff_masks(d)
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:op.shape[0], 0:op.shape[1]]
    old = np.zeros(op.shape, bool)
    for x0, x1, y0, y1 in OLD:
        old |= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    out = d.copy()
    out[old & op & ~band & ~head & ~end] = 0
    stale = np.zeros(op.shape, bool)
    for y in range(op.shape[0]):
        for x in range(SCRUB_X[0], SCRUB_X[1] + 1):
            if op[y, x] and not band[y, x] and (x, y) not in GLOVE and abs(across(x, y)) <= SCRUB_T                     and tuple(int(v) for v in d[y, x, :3]) in PALE:
                stale[y, x] = True
    for y, x in zip(*np.nonzero(stale)):
        step = 1 if across(x, y) > 0 else -1          # away from the line
        yy_ = y + step
        while 0 <= yy_ < op.shape[0] and (stale[yy_, x] or band[yy_, x]):
            yy_ += step
        if 0 <= yy_ < op.shape[0] and op[yy_, x]:
            out[y, x] = d[yy_, x]
    for (x, y), c in shaft(op.shape).items():
        if (x, y) in GLOVE or head[y, x] or end[y, x]:
            continue
        out[y, x, :3] = c
        out[y, x, 3] = 255
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--out", help="write the design here instead of hd/design.png")
    a = ap.parse_args()
    d, size = read()
    for (x, y), c in FACE.items():
        d[y, x, :3] = c
    d = restaff(d)
    Image.fromarray(d).save(lp(a.out or os.path.join(HD, "design.png")))
    print(f"square {size[0]:.2f} x {size[1]:.2f} -> design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    im = Image.fromarray(d)
    cells = [(f"new {PPU}: {d.shape[0] / PPU:.1f}px", FD.shown(im, PPU, 3))]
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == "lux" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "lux_ppu_size.png"))
    raw = Image.open(lp(os.path.join(HD, "raw", RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 8
    cdx = raw.resize((round(raw.width * d.shape[0] * z / raw.height), d.shape[0] * z), Image.LANCZOS)
    FD.strip([("Codex's picture", cdx), (f"design {d.shape[1]}x{d.shape[0]} on its own squares", FD.shown(im, 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "lux_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
