#!/usr/bin/env python3
"""Ahri's dense design: Codex's step-0 picture read back on its own squares.

    python tools/art/design_ahri_hd.py [--step 1.0] [--review DIR] [--out PNG]

Asked (assets/source/ahri/PICTURE_PROMPT_PPU.md) for 60 squares of 11 px from her ear tips to her soles, Codex drew
two pictures (hd/raw/): its pick, the second, on ~17.5-px squares (54 rows: the user, 2026-10-23, 「PPU调高点吧 这也太糊了」)
and the first on ~9.8-px squares (119 rows, the face, the tails' locks and the trims clear), which is read:
- the picture's own squares read first (design_fiora_hd.grid: one fitted pitch and phase per axis, the median of
  each square's middle half; the semi-transparent rim dropped at alpha 128), cut to COLOURS by k-means in Lab
  (design_varus.kmeans);
- then `step` of them make a design square (design_lux_hd's way: the mean in Lab of the parts of the squares it
  covers, outline squares apart, snapped to those colours; the outline where it covers OUTLINE_SHARE of outline);
  step 1 keeps them as they are;
- speckle cleaned as Jinx's (design_jinx_hd.clean).
-> hd/design.png. With --review DIR: <dir>/ahri_ppu_size.png (the design at PPUS beside this pack's PPU heroes and
Ahri now, as the game draws them, 3 screen pixels a game pixel) and <dir>/ahri_ppu_closeup.png (Codex's picture and
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

HD = os.path.join(ROOT, "assets", "source", "ahri", "hd")
RAW = "ahri-first.png"
PITCH = (9.3, 10.3)             # the picture's own square (9.80 x 9.79)
COLOURS = 48
OUTLINE_SHARE = 0.45
PEERS = ["ahri", "lux", "jinx", "caitlyn", "riven"]


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
    ap.add_argument("--step", type=float, default=1.0)
    ap.add_argument("--review")
    ap.add_argument("--out", help="write the design here instead of hd/design.png")
    ap.add_argument("--ppu", type=float, nargs="*", default=[], help="the PPUs the review shows the design at")
    a = ap.parse_args()
    d, size = read(a.step)
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
        cells.append((("now" if h == "ahri" else h) + (f" {p}" if p != 1 else " 1x"), FD.shown(f, p, 3)))
    FD.strip(cells).convert("RGB").save(os.path.join(a.review, "ahri_ppu_size.png"))
    raw = Image.open(lp(os.path.join(HD, "raw", RAW))).convert("RGBA")
    raw.putalpha(raw.getchannel("A").point(lambda v: 255 if v >= 128 else 0))
    raw = raw.crop(raw.getbbox())
    z = 4
    cdx = raw.resize((round(raw.width * d.shape[0] * z / raw.height), d.shape[0] * z), Image.LANCZOS)
    FD.strip([("Codex's picture", cdx), (f"design {d.shape[1]}x{d.shape[0]} on its own squares", FD.shown(im, 1, z))]) \
        .convert("RGB").save(os.path.join(a.review, "ahri_ppu_closeup.png"))
    print("review written to", a.review)


if __name__ == "__main__":
    main()
