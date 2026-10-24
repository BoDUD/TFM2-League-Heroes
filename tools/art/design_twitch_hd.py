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
- the goggle, the grin and the nose redrawn by hand (face()).
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
STEP = 1.534                    # its squares to a design square: 109 x 71, PPU 2.2 at his 32 px (the user picked 2.2
                                # from 2.2 / 2.5 / 3.0, 2026-10-24: 「用 PPU 2.2，牙齿和脸手修清楚」)
GAME_ROWS = 32                  # his sprite now, ears to soles: the game size he keeps
PPU = 2.2
OUTLINE_SHARE = 0.45
H = lambda h: tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # noqa: E731
# the face redrawn by hand (the user, 2026-10-24: 「牙齿和脸手修清楚」 - read at 1.534 squares a square the teeth ran
# into one smear and the goggle into a gold blob): the design's own colours by letter, P a paler lens highlight
C = dict(a='474335', b='302D27', c='5D5C45', d='7A7958', e='9D9A6E', f='0E0A10', g='735036', h='A46049', j='4A311D',
         k='94691F', l='DCB24C', n='724E15', o='C69E63', p='E5BB7A', q='573A14', s='352318', u='511724', v='7A2031', w='7D3511', P='F2D9A6')


def face():
    """(x, y) -> colour letter on the 109 x 71 design."""
    F = {}
    # goggle: a round lens (cream, darker rim) with a 2x2 pupil, a gold ring lit top-left, a dark edge
    cx, cy = 63.5, 18.5
    for y in range(12, 26):
        for x in range(57, 71):
            r = np.hypot(x - cx, y - cy)
            lit = (x - cx) + (y - cy)
            if r < 1.2: F[x, y] = 'f'
            elif r < 2.5: F[x, y] = 'P' if lit < -1.5 else ('p' if lit < 2 else 'o')
            elif r < 3.1: F[x, y] = 'j'
            elif r < 4.1: F[x, y] = 'l' if lit < 1 else 'k'
            elif r < 4.6: F[x, y] = 'f'
    # mouth: a grin slanting down to the snout, the gum on top, upper and lower teeth locked, the lower gum
    for x in range(64, 79):
        t = 26 + (x - 63) // 4
        if x == 64:                     # the back corner: closed to a dark slit
            F[x, t + 1], F[x, t + 2] = 'u', 'f'
            continue
        if x == 78:                     # the front corner, under the nose
            F[x, t], F[x, t + 1], F[x, t + 2] = 'v', 'u', 'f'
            continue
        F[x, t] = 'v'
        F[x, t + 1] = 'p' if x % 3 else 'f'
        F[x, t + 2] = 'o' if x % 3 == 1 else ('u' if x < 67 else 'f')
        F[x, t + 3] = 'v'
        F[x, t + 4] = 'b'
    # the fang at the corner, over the lower gum and below the chin
    for (x, y), c in {(76, 31): 'p', (77, 31): 'p', (76, 32): 'p', (77, 32): 'o', (76, 33): 'o', (77, 33): 'f',
                      (75, 33): 'b', (75, 34): 'f', (76, 34): 'o', (77, 34): 'f', (76, 35): 'f'}.items():
        F[x, y] = c
    # the nose: red-brown, lit on top, a nostril
    for (x, y), c in {(78, 23): 'w', (79, 23): 'w', (80, 23): 'h', (78, 24): 'w', (79, 24): 'j', (80, 24): 'w',
                      (81, 24): 'w', (78, 25): 'j', (79, 25): 'w', (80, 25): 'w', (81, 25): 'w', (78, 26): 'j',
                      (79, 26): 'j', (80, 26): 'j'}.items():
        F[x, y] = c
    return F


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
        for (x, y), c in face().items():
            if d[y, x, 3]:
                d[y, x, :3] = H(C[c])
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
