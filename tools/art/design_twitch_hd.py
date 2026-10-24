#!/usr/bin/env python3
"""Twitch's dense design: the user's picture read back on its own squares.

    python tools/art/design_twitch_hd.py [--step 1.0] [--review DIR] [--ppu 2.0 2.2 2.5] [--out PNG]

The pack (tools/art/pack_twitch_ppu.py) asked for 70 squares of 11 px; the user brought a picture of their own
(2026-10-24: 「用这一张就行了」, hd/raw/twitch-user.png: 1536 x 1024, ~8-px squares, a webp, alpha up to 254), read
Ahri's way (design_ahri_hd.py):
- the picture's own squares read first (design_fiora_hd.grid: one fitted pitch and phase per axis, the median of
  each square's middle half; alpha cut at 128), cut to COLOURS by k-means in Lab (design_varus.kmeans);
- then STEP of them make a design square (design_lux_hd's way: the mean in Lab of the parts of the squares it
  covers, outline squares apart, snapped to those colours; the outline where it covers OUTLINE_SHARE of outline);
- speckle cleaned as Jinx's (design_jinx_hd.clean);
- the face set by hand (FACE).
-> hd/design.png. With --review DIR: <dir>/twitch_ppu_size.png (the design at --ppu beside this pack's PPU heroes and
Twitch now, as the game draws them, 3 screen pixels a game pixel) and <dir>/twitch_ppu_closeup.png (the picture and
the design at 4x).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from skimage import color

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_fiora_hd as FD  # noqa: E402
import design_jinx_hd as JD  # noqa: E402
import design_lux_hd as DL  # noqa: E402
import design_varus as V  # noqa: E402

HERO = "twitch"
HD = os.path.join(ROOT, "assets", "source", "twitch", "hd")
RAW = "twitch-user.png"
PITCH = (7.7, 8.3)              # the picture's own square (~8 px: its edges' comb peaks at 8.0)
COLOURS = 48
STEP = 1.0                      # its squares to a design square (set once the user picks the PPU)
GAME_ROWS = 32                  # his sprite now, ears to soles: the game size he keeps
PPU = 2.2
OUTLINE_SHARE = 0.45
H = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # noqa: E731
FACE = {}
PEERS = ["twitch", "jinx", "caitlyn", "varus", "kogmaw"]


def lp(path):
    return FD.lp(path)


def native():
    a = np.asarray(Image.open(lp(os.path.join(HD, "raw", RAW))).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    FD.PITCH = PITCH
    n, size = FD.grid(a)
    op = n[..., 3] > 0
    idx, pal = V.kmeans(n, COLOURS)
    q = np.zeros_like(n)
    q[op, :3] = pal[idx[op]]
    q[op, 3] = 255
    return q, pal, size


def outline_of(pal):
    """The palette's darkest colour: the outline."""
    return tuple(int(v) for v in pal[np.argmin(pal.astype(int).sum(1))])


def read(step):
    q, pal, size = native()
    if step == 1:
        d = q
    else:
        out = outline_of(pal)
        op = q[..., 3] > 0
        out_sq = (op & (np.abs(q[..., :3].astype(int) - np.array(out)).sum(-1) < 40)).astype(float)
        lab = color.rgb2lab(q[..., :3] / 255.0)
        plab = color.rgb2lab(pal[None].astype(float) / 255.0)[0]
        DL.STEP = step
        wy, wx = DL.cover(q.shape[0]), DL.cover(q.shape[1])
        opf = op.astype(float)
        inner = opf * (1 - out_sq)
        cov, oc, wi = wy @ opf @ wx.T, wy @ out_sq @ wx.T, wy @ inner @ wx.T
        area = wy.sum(1)[:, None] * wx.sum(1)[None, :]
        mean = np.stack([wy @ (lab[..., c] * inner) @ wx.T for c in range(3)], -1) / np.maximum(wi, 1e-9)[..., None]
        k = np.argmin(((mean[..., None, :] - plab[None, None]) ** 2).sum(-1), -1)
        keep = cov >= 0.5 * area
        d = np.zeros(cov.shape + (4,), np.uint8)
        d[keep, :3] = pal[k[keep]]
        d[keep & ((oc >= OUTLINE_SHARE * cov) | (wi < 0.2 * area)), :3] = out
        d[keep, 3] = 255
    ys, xs = np.nonzero(d[..., 3])
    return JD.clean(d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]), size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=float, default=STEP)
    ap.add_argument("--review")
    ap.add_argument("--out", help="write the design here instead of hd/design.png")
    ap.add_argument("--ppu", type=float, nargs="*", default=[], help="the PPUs the review shows the design at")
    a = ap.parse_args()
    d, size = read(a.step)
    if a.step == STEP:
        for (x, y), c in FACE.items():
            d[y, x, :3] = c
    Image.fromarray(d).save(lp(a.out or os.path.join(HD, "design.png")))
    print(f"square {size[0]:.2f} x {size[1]:.2f}, step {a.step} -> design {d.shape[1]}x{d.shape[0]}, "
          f"{len(np.unique(d[d[..., 3] > 0][:, :3], axis=0))} colours")
    if not a.review:
        return
    os.makedirs(a.review, exist_ok=True)
    im = Image.fromarray(d)
    cells = [(f"new {p}: {d.shape[0] / p:.1f}px", FD.shown(im, p, 3)) for p in a.ppu]
    for h in PEERS:
        f, p = FD.frame0(h)
        cells.append((("now" if h == HERO else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "twitch_ppu_size.png"))
    raw = Image.open(lp(os.path.join(HD, "raw", RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 4
    cdx = raw.resize((round(raw.width * d.shape[0] * z / raw.height), d.shape[0] * z), Image.LANCZOS)
    FD.strip([("the picture", cdx), (f"design {d.shape[1]}x{d.shape[0]} on its own squares", FD.shown(im, 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "twitch_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
