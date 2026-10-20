#!/usr/bin/env python3
"""Warwick's Codex poses (assets/source/warwick/codex_poses: POSE_PROMPTS.md, nine of League's whole-body poses on
skeletons) read back at the design's scale, in its colours, with the design's own head.

    python tools/art/design_warwick_poses.py --measure          # each raw pose's square size (regrid) and eye distance
    python tools/art/design_warwick_poses.py --sheet DIR        # all poses beside the design (6x + 1x)
    python tools/art/design_warwick_poses.py                    # writes assets/source/warwick/hd/pose_<name>.png

Codex draws every pose with its own square size, so its own grid is not ours: the scale of each (SCALE, Codex px a
design square) comes from regrid's estimate checked against the distance between his two yellow eyes (7 squares apart
in the design, centre to centre). Each pose is sampled on that grid from the figure's top-left
(design_chogath_poses.sample: a square opaque when most of it is, the median colour), every colour snapped to the
design's own (Lab), the outline closed. One face in all frames (memory one-face-all-frames): Codex's head is covered by
the design's (HEAD_POLY: the ears, the face and its mane, never the back rig or the shoulders) with its near eye on
Codex's near eye.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_poses import sample  # noqa: E402
from design_chogath_side import snap  # noqa: E402
from design_warwick_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "warwick", "codex_poses")
OUT = os.path.join(ROOT, "assets", "source", "warwick", "hd")
NAMES = ["crouch", "rear", "leap", "bite", "howl", "strike", "raise", "stagger", "lie"]
# Codex px a design square, per pose: the median of four measures that disagree by a square or two (--measure): the eyes'
# distance over the design's 7 squares (a turned head shortens it), and the square roots of the copper's (gauntlets,
# spike, plates), the blue fur's and the whole figure's area over the design's (an upright body shows more of itself)
SCALE = {"crouch": 12.5, "rear": 13.5, "leap": 13.2, "bite": 12.9, "howl": 14.3, "strike": 12.0, "raise": 13.3,
         "stagger": 12.8, "lie": 8.7}
EYE = (252, 218, 30)           # the design's yellow eyes (one square wide, two tall): near (27, 65), far (27, 72)
DESIGN_NEAR_EYE = (27.5, 65.0)  # (row, column) of the near eye's middle in hd/idle.png
EYE_GAP = 7.0                   # squares between the eyes' middles in the design
# the design's head (ears, face, mane) as a polygon in design squares (x, y): the near ear's tip and outer edge, the
# forehead under the back rig, the far ear, the far cheek, the muzzle, the jaw, the mane's bottom and left edge
HEAD_POLY = [(41, 9), (46, 12), (49, 16), (58, 17), (62, 8), (66, 10), (71, 18), (76, 20), (79, 23), (79, 29),
             (78, 32), (74, 34), (75, 44), (66, 44), (62, 41), (49, 41), (49, 27), (46, 22), (43, 16), (41, 9)]


def head_mask(d):
    img = Image.new("L", (d.shape[1], d.shape[0]), 0)
    ImageDraw.Draw(img).polygon(HEAD_POLY, fill=255)
    m = np.asarray(img) > 0
    return m & (d[..., 3] > 0)


def eyes_px(a, least=50):
    """Codex's two yellow eyes: the two biggest yellow blobs (row, column of each middle), left to right - the eyes are
    the only big yellow in the picture (the copper's highlights and the vial's yellow-green are small or not yellow)."""
    rgb = a[..., :3].astype(int)
    y = (rgb[..., 0] > 200) & (rgb[..., 1] > 170) & (rgb[..., 2] < 90) & (a[..., 3] > 200)
    lab, k = ndimage.label(y)
    blobs = sorted(((int((lab == i).sum()), ndimage.center_of_mass(y, lab, i)) for i in range(1, k + 1)), reverse=True)
    blobs = [c for n, c in blobs if n >= least][:2]
    if len(blobs) != 2:
        raise SystemExit(f"eyes: {len(blobs)} big yellow blobs")
    return tuple(sorted(blobs, key=lambda c: c[1]))


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"warwick-pose-{name}.png"))).convert("RGBA"))


def with_head(fig, idle, eye):
    """The design's head laid with its near eye on the pose's near eye `eye` (row, column on the pose's grid); Codex's
    own head squares under it replaced, and any of Codex's eye-yellow left outside it cleared to its neighbours."""
    hm = head_mask(idle)
    ey, ex = eye
    oy, ox = int(round(ey - DESIGN_NEAR_EYE[0])), int(round(ex - DESIGN_NEAR_EYE[1]))
    pad = 40
    can = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    ys, xs = np.nonzero(hm)
    can[pad + ys + oy, pad + xs + ox] = idle[ys, xs]
    ys, xs = np.nonzero(can[..., 3] > 0)
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def finish(fig, most=12):
    """The outline closed; small enclosed holes the readback left take the outline."""
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    op = pad[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    for j in range(1, n + 1):
        h = lab == j
        if h.sum() <= most:
            pad[h] = (*ink, 255)
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def read(name, idle):
    a = raw(name)
    sc = SCALE[name]
    fig = snap(sample(a, sc), idle)
    ys, xs = np.nonzero(a[..., 3] >= 128)
    (ey, ex), _ = eyes_px(a)
    fig = with_head(fig, idle, ((ey - ys.min()) / sc - 0.5, (ex - xs.min()) / sc - 0.5))
    return finish(fig)


def measure():
    import regrid as RG
    for n in NAMES:
        a = raw(n).copy()
        _, sq, _ = RG.regrid(a)
        (y0, x0), (y1, x1) = eyes_px(a)
        ys, xs = np.nonzero(a[..., 3] >= 128)
        print(f"{n:8s} regrid {sq:5.2f} px; eyes {x1 - x0:5.1f} px apart -> {((x1 - x0) / EYE_GAP):5.2f} px a square; "
              f"figure {xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1} px")


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--measure", action="store_true")
    a = ap.parse_args()
    if a.measure:
        measure()
        return
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    figs = {n: read(n, idle) for n in NAMES}
    if a.sheet:
        os.makedirs(a.sheet, exist_ok=True)
        z = 5
        cells = [("design", idle)] + list(figs.items())
        rows = [cells[:5], cells[5:]]
        W = max(sum(f.shape[1] * z + 20 for _, f in r) for r in rows) + 20
        Hs = [max(f.shape[0] for _, f in r) * z + 40 for r in rows]
        can = Image.new("RGB", (W, sum(Hs)), (255, 255, 255))
        dr = ImageDraw.Draw(can)
        y0 = 0
        for r, H in zip(rows, Hs):
            x = 20
            for name, f in r:
                b = big(f, z)
                can.paste(b.convert("RGB"), (x, y0 + H - 10 - b.height))
                dr.text((x, y0 + 4), f"{name} {f.shape[1]}x{f.shape[0]}", fill=(0, 0, 0))
                x += b.width + 20
            dr.line([(0, y0 + H - 10), (W, y0 + H - 10)], fill=(200, 0, 0))
            y0 += H
        can.save(os.path.join(a.sheet, "warwick_poses_sheet.png"))
        print(os.path.join(a.sheet, "warwick_poses_sheet.png"))
        return
    for n, f in figs.items():
        Image.fromarray(f).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        print(n, f.shape[1], "x", f.shape[0])


if __name__ == "__main__":
    main()
