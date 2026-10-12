#!/usr/bin/env python3
"""Garen's dense frames (PPU 2.5) read straight from his original pictures, no image model in between.

    python tools/art/ppu_garen.py                  # write assets/source/ppu/garen_<tag>.png (+ .json sizes)
    python tools/art/ppu_garen.py --review DIR     # garen_hd_<tag>.png (8x) and garen_hd_<tag>.gif

The user, 2026-10-12: 「这个分支用来重建老英雄的 用PPU重建 先是盖伦 但是所有模型图生成就不拜托codex了 我们自己处理 因为也有原稿
对比了」, then 「按原稿走 密度2.5」. The originals are the GPT strips in assets/source/garen (garen_<tag>.png, round 3/4,
garen_ref_v3.png's chibi): drawn about 3.5 picture pixels to a square, so 2.5 x the 1x sprite (92 rows head to sole) is
their own density - every square is the area average of the picture under it, mapped to one palette for the whole hero.
The 1x sheet (Codex's step-2 redraw) is a different drawing; only its frame sizes, timing and standing point are kept:
an hd frame is round(2.5 x its 1x frame) round the same centre, the soles on the 1x soles' row.

idle: the first picture of garen_idle.png is the design; the loop is that design breathing (tools/art/idle_breathe.py,
the 1x recipe: the body above the shins down 0-2 rows and a column forward, the head a frame late), the sword lifted out
first and stamped back with the body so the cut rows never step through the blade.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import idle_breathe as IB  # noqa: E402
import import_native as N  # noqa: E402
import ppu_hd  # noqa: E402
import strips as G  # noqa: E402

PPU = 2.5
HERO = "garen"
PICS = os.path.join(ROOT, "assets", "source", "garen")
OUT = os.path.join(ROOT, "assets", "source", "ppu")
STEM = os.path.join(ROOT, "league", "champions", "league_garen")
ROWS = 92                       # head to sole in the design: round(2.5 x the 1x idle's 37 rows) (92.5, the lower)
ROWS_1X = 37                    # the 1x design (the sheet without league.dll), the old 1x idle's height
COLOURS = 40                    # the hero's palette (median cut of the design), plus the outline
FRAMES = {"idle": 6}            # pictures in each original strip
# the idle's blade from the guard to the tip, lifted out before the breath and stamped back moved with the body:
# (start, end) of its middle line and its half width, in 1x px from the idle frame's centre (both densities)
BLADE = ((-5.2, 1.7), (13.4, 9.9), 2.5)
# the idle's blade redrawn straight (the user: 「剑感觉有点歪？」 - the picture's edges are not parallel, 0.445 and 0.478,
# its lower edge bends flat near the tip and the point sits under the middle line; averaged down, the two edges
# stepped unevenly and the fuller wobbled). Measured on the picture (strip px, garen_idle.png picture 1): the middle
# line through (220, 459.05) at slope 0.4615, half width 16.6 across it (outline outside), from the guard (x 200)
# straight to x 322, then both edges meet on the middle line at x 345. Its colours: the picture's own, for each square
# the median of the picture's blade pixels at the same distance from the middle line, within 12 px along it.
BLADE_SRC = {"seed": (270, 470), "through": (220, 459.05), "slope": 0.4615, "half": 16.6, "start": 200,
             "bend": 322, "tip": 345, "along": 12}


def load_strip(tag):
    a = np.asarray(Image.open(os.path.join(PICS, f"garen_{tag}.png")).convert("RGBA")).astype(np.float32) / 255
    return G.split_strip(a, FRAMES[tag])


def regrid(fr, scale):
    """A picture's frame at `scale` (hd px per picture px), the soles' bottom edge on y = 0 and the feet's middle on
    x = 0: (array, column of its left edge, row of its top edge) in those coordinates."""
    x0, y0, x1, y1 = fr.bbox(0.5)
    fx = G.feet_mid(fr, scale, px=3)
    out, u0, r0 = G.render(fr, scale, scale, fx, y1, X0=0.0, Y0=-0.5, cut=0.5)
    return out, u0, r0, (fx, y1, scale)


def blade_coords(x, y):
    """Picture points -> (along the blade's middle line from its start, across it, + down) in picture px."""
    b = BLADE_SRC
    ux, uy = 1 / np.hypot(1, b["slope"]), b["slope"] / np.hypot(1, b["slope"])
    sx, sy = b["start"], b["through"][1] + b["slope"] * (b["start"] - b["through"][0])
    return (x - sx) * ux + (y - sy) * uy, -(x - sx) * uy + (y - sy) * ux


def straight_blade(a, u0, r0, geo, pal):
    """The idle's blade in the regridded picture `a` redrawn from BLADE_SRC: straight parallel edges, a point on the
    middle line, a one-square outline; squares of the old blade left outside take the body behind them or go clear.
    Gold and blue squares (the guard over the blade's root) are never painted. -> (picture, blade squares)."""
    b = BLADE_SRC
    fx, ay, s = geo
    pic = np.asarray(Image.open(os.path.join(PICS, "garen_idle.png")).convert("RGBA")).astype(int)
    op = pic[..., 3] > 128
    lum = 0.299 * pic[..., 0] + 0.587 * pic[..., 1] + 0.114 * pic[..., 2]
    sat = pic[..., :3].max(-1) - pic[..., :3].min(-1)
    lab, _ = ndimage.label(op & (lum > 60) & (sat < 70))
    old = ndimage.binary_fill_holes(lab == lab[b["seed"][1], b["seed"][0]])
    py, px = np.nonzero(old)
    pt, pd = blade_coords(px + 0.5, py + 0.5)
    pcol = pic[py, px, :3]
    L = blade_coords(b["bend"], b["through"][1] + b["slope"] * (b["bend"] - b["through"][0]))[0]
    T = blade_coords(b["tip"], b["through"][1] + b["slope"] * (b["tip"] - b["through"][0]))[0]
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    sx = fx + (u0 + xx) / s                                     # each square's middle in the picture
    sy = ay + (r0 + yy + 0.5) / s
    t, d = blade_coords(sx, sy)
    half = np.where(t <= L, b["half"], b["half"] * (T - t) / (T - L))
    inside = (t >= 0) & (t <= T) & (np.abs(d) <= half)
    rgb = a[..., :3].astype(int)
    body_col = (a[..., 3] > 0) & (rgb.max(-1) - rgb.min(-1) >= 70)   # the guard's gold and blue
    paint = inside & ~body_col
    out = a.copy()
    step = 0.5 / s                                              # half a square across, in picture px
    for y, x in zip(*np.nonzero(paint)):
        for win in (b["along"], 3 * b["along"]):
            sel = (np.abs(pd - d[y, x]) <= step) & (np.abs(pt - min(t[y, x], L)) <= win)
            if sel.sum() >= 3:
                break
        c = np.median(pcol[sel], axis=0) if sel.any() else pcol.mean(0)
        out[y, x, :3] = pal.colors[((pal.colors - c) ** 2).sum(1).argmin()].astype(np.uint8)
        out[y, x, 3] = 255
    ring = ~inside & ~body_col & (t >= -1 / s) & ndimage.binary_dilation(inside, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    dark = pal.colors[G.lum(pal.colors).argmin()].astype(np.uint8)
    out[ring, :3] = dark
    out[ring, 3] = 255
    # what the old blade and its outline covered beyond the new one (each square by the picture under its middle)
    old_line = ndimage.binary_dilation(old, iterations=4) & ~old & op & (lum < 70)
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    ok = (ix >= 0) & (iy >= 0) & (ix < pic.shape[1]) & (iy < pic.shape[0])
    was = np.zeros((h, w), bool)
    was[ok] = (old | old_line)[iy[ok], ix[ok]]
    left = was & ~inside & ~ring & ~body_col & (out[..., 3] > 0)
    out[left] = 0
    out = N.fill_behind(out, left)
    return out, int(paint.sum())


def design():
    """The idle design at both densities from picture 1 of garen_idle.png: {"hd": (array, u0, r0), "1x": ...} on
    ROWS and ROWS_1X rows, one palette (made on the hd one), crumbs dropped."""
    fr = load_strip("idle")[0]
    x0, y0, x1, y1 = fr.bbox(0.5)
    hd = regrid(fr, ROWS / (y1 - y0))
    pal = G.Palette([hd[0]], colors=COLOURS)
    out = {}
    for k, rows in (("hd", ROWS), ("1x", ROWS_1X)):
        a, u0, r0, geo = hd if k == "hd" else regrid(fr, rows / (y1 - y0))
        a = G.drop_lonely(pal.apply(a))
        a, _ = straight_blade(a, u0, r0, geo, pal)
        out[k] = (a, u0, r0)
    return out, pal


def frame_1x(tag, i=0):
    return ppu_hd.read_sheet(STEM)[tag][i][0]


def standing(tag):
    """Where the 1x frame 0 of `tag` stands: (soles' bottom edge, feet's middle) in 1x px from the frame's centre."""
    one = frame_1x(tag)
    op = one[..., 3] > 0
    sole = int(np.nonzero(op.any(1))[0].max())
    xs = np.nonzero(op[sole - 1:sole + 1].any(0))[0]
    h, w = one.shape[:2]
    return sole + 1 - h / 2, (xs.min() + xs.max() + 1) / 2 - w / 2, (w, h)


def place(a, u0, r0, size, sole_dy, feet_dx, k=1.0, margin=0):
    """`a` (feet-relative, see regrid) on an empty (w, h) frame whose centre stands sole_dy over the soles' bottom
    edge and feet_dx right of the feet's middle (1x px; k = the frame's px per 1x px). None when a pixel would come
    within `margin` of the frame's edge."""
    w, h = size
    out = np.zeros((h, w, 4), np.uint8)
    sole_row = int(round(h / 2 + sole_dy * k)) - 1
    feet_x = w / 2 + feet_dx * k
    ys, xs = np.nonzero(a[..., 3])
    Y = sole_row + 1 + r0 + ys
    X = np.floor(feet_x + u0 + xs).astype(int)
    if Y.min() < margin or X.min() < margin or Y.max() >= h - margin or X.max() >= w - margin:
        return None
    out[Y, X] = a[ys, xs]
    return out


def fit(pair, sole_dy, feet_dx, size, margin=(2, 3)):
    """Both densities placed: the 1x frame grown from `size` (odd, alike at both ends, so its centre stays) until
    both fit with `margin` (1x, hd) clear all round; the hd frame is round(PPU x the 1x frame)."""
    w, h = size
    while True:
        W, H = ppu_hd.hd_size(w, h, PPU)
        one = place(*pair["1x"], (w, h), sole_dy, feet_dx, 1.0, margin[0])
        hd = place(*pair["hd"], (W, H), sole_dy, feet_dx, PPU, margin[1])
        if one is not None and hd is not None:
            return one, hd
        a1 = place(*pair["1x"], (w + 200, h + 200), sole_dy, feet_dx, 1.0)
        ah = place(*pair["hd"], (W + 500, H + 500), sole_dy, feet_dx, PPU)
        grow_w = grow_h = False
        for arr, m, bw, bh in ((a1, margin[0], w, h), (ah, margin[1], W, H)):
            ys, xs = np.nonzero(arr[..., 3])
            pad_x = (arr.shape[1] - bw) // 2
            pad_y = (arr.shape[0] - bh) // 2
            grow_w |= xs.min() - pad_x < m or xs.max() - pad_x >= bw - m
            grow_h |= ys.min() - pad_y < m or ys.max() - pad_y >= bh - m
        w, h = w + 2 * grow_w, h + 2 * grow_h


def blade_mask(a, k):
    """BLADE's drawn pixels in the frame `a` of k px per 1x px (pixel centres within the half width of the line,
    from its start on; the dark outline squares up to 0.6 1x px further)."""
    (x0, y0), (x1, y1), r = BLADE
    h, w = a.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    px = ((xs + 0.5) - w / 2) / k
    py = ((ys + 0.5) - h / 2) / k
    dx, dy = x1 - x0, y1 - y0
    t = ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)
    d = np.hypot(px - (x0 + t * dx), py - (y0 + t * dy))
    dark = a[..., :3].astype(int).sum(-1) < 210                          # its outline, a square further out
    return (a[..., 3] > 0) & (t >= 0) & (((t <= 1.08) & (d <= r)) | (dark & (t <= 1.15) & (d <= r + 0.6)))


def eye(a):
    """The near eye's iris: the middle of the bright blue squares in the top third (the head point for the nod)."""
    top = int(np.nonzero(a[..., 3].any(1))[0].min())
    h = a.shape[0]
    rgb = a[..., :3].astype(int)
    blue = (a[..., 3] > 0) & (rgb[..., 2] > 150) & (rgb[..., 2] > rgb[..., 0] + 80)
    blue[top + (h - top) // 3:] = False
    ys, xs = np.nonzero(blue)
    return float(xs.mean()), float(ys.mean())


def breathe(a, k):
    """8 idle frames of the design `a` (k px per 1x px): the blade lifted out (the squares it covered filled with the
    body round them), idle_breathe.py's breath at k x its 1x rows (rounded: the same dip on screen), the blade stamped back with the body."""
    blade = blade_mask(a, k)
    body_rows = [int(round(v * k)) for v in IB.BODY]
    lift = a.copy()
    lift[blade] = 0
    lift = N.fill_behind(lift, blade)
    frames, rows = IB.breathe(lift, eye(a), body=body_rows)
    ys, xs = np.nonzero(blade)
    out = []
    for f, dip, lean in zip(frames, body_rows, IB.SWAY):
        f[ys + 2 + dip, xs + 2 + lean] = a[ys, xs]
        out.append(np.ascontiguousarray(f[2:-2, 2:-2]))
    return out, rows, int(blade.sum())


def gif(frames, path, zoom, ms):
    bg = (90, 120, 90, 255)
    ims = []
    for f in frames:
        im = Image.new("RGBA", (f.shape[1], f.shape[0]), bg)
        im.alpha_composite(Image.fromarray(f))
        ims.append(im.convert("RGB").resize((f.shape[1] * zoom, f.shape[0] * zoom), Image.NEAREST))
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=ms, loop=0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write review pictures here")
    args = ap.parse_args()
    pair, pal = design()
    sole_dy, feet_dx, size = standing("idle")
    one, hd = fit(pair, sole_dy, feet_dx, size)
    print("idle 1x", one.shape[1], "x", one.shape[0], "(was", size, ") hd", hd.shape[1], "x", hd.shape[0],
          "colours", len(pal.colors))
    idle_hd, rows, n = breathe(hd, PPU)
    idle_1x, rows1, n1 = breathe(one, 1)
    print("idle breath hd: cut cost", rows["dip_cost"], "lean", rows["lean_cost"], "nod", rows["neck"] is not None,
          "blade", n, "| 1x:", rows1["dip_cost"], rows1["lean_cost"], rows1["neck"] is not None, "blade", n1)
    if args.review:
        os.makedirs(args.review, exist_ok=True)
        Image.fromarray(hd).resize((hd.shape[1] * 6, hd.shape[0] * 6), Image.NEAREST).save(
            os.path.join(args.review, "garen_design_hd_6x.png"))
        Image.fromarray(one).resize((one.shape[1] * 15, one.shape[0] * 15), Image.NEAREST).save(
            os.path.join(args.review, "garen_design_1x_15x.png"))
        gif(idle_hd, os.path.join(args.review, "garen_hd_idle.gif"), 4, IB.MS)
        gif(idle_1x, os.path.join(args.review, "garen_1x_idle.gif"), 10, IB.MS)


if __name__ == "__main__":
    main()
