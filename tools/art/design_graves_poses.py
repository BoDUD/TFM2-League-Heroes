#!/usr/bin/env python3
"""Graves's Codex poses (assets/source/graves/codex_poses, 2026-10-20, Codex new-chat-4: POSE_PROMPTS.md) read back at
the side design's scale, in its colours, with the idle's head.

    python tools/art/design_graves_poses.py --sheet DIR     # all poses beside the side design (8x + 1x)
    python tools/art/design_graves_poses.py                 # writes assets/source/graves/hd/pose_<name>.png

Codex drew every pose with its own square size (regrid: tilt ~16 px, shoulder ~14, kneel ~17, lunge / stagger ~11, hop
~10, lie ~12), so its own grid is not ours. The scale of each (SCALE, Codex px a design square) comes from two
measures that agree within a square or two: the distance between his eyes (the two white squares, 4 squares apart in the
designs) and the square root of the figure's area over the side design's (less the gun for the poses without it);
SCALE takes the mean for the poses with the gun and the eyes for the rest (the lying figure's area overlaps itself).
Each pose is sampled on that grid from the figure's top-left (design_chogath_poses.sample: a square opaque when most of
it is, the median colour), every colour snapped to the side design's own (Lab), the outline closed. One face in all
frames: Codex's head is covered by the idle's (design_graves_model.head_mask) with its near eye on Codex's near eye.
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
from design_graves_hd import lp  # noqa: E402
from design_graves_model import IDLE_CHIN, IDLE_HEAD_COLS, IDLE_JAW_COLS, IDLE_NECK, head_mask  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "graves", "codex_poses", "raw")
OUT = os.path.join(ROOT, "assets", "source", "graves", "hd")
SCALE = {"tilt": 16.4, "lunge": 13.7, "shoulder": 14.2, "hop": 14.9, "stagger": 15.5, "kneel": 17.0, "lie": 13.5}
IDLE_EYE = (11, 30)            # the idle's near eye (row, column): its white square
# The legs the side design stands on (the user's rule: legs as the idle's, never deformed). Codex drew tilt's legs 19
# rows long (the design's 15) and lunge's back leg stretched to about 30 squares (its skeleton asked 18), so both stand on
# the side design's own legs (rows from DESIGN_LEGS, the back leg to column 33, the front past it): the pose's squares
# from row `split` down within `cols` go (from row low[0] down every column from low[1]: tilt's stock reaches below its
# belt left of its legs), the design's legs come in with their top row on `split` and their parting
# (design column 33) on `hip`; `spread` moves the back and the front leg whole (columns) for a wider stance.
DESIGN_LEGS, DESIGN_PART = 42, 33
GRAFT = {"tilt": dict(split=39, cols=(19, 73), low=(43, 0), hip=32, spread=(0, 0)),
         "lunge": dict(split=37, cols=(0, 70), low=(37, 0), hip=40, spread=(-3, 2))}


def eyes(a, thresh=235, least=20):
    """His two eyes in Codex's picture: the pair of white blobs (at least `least` px each) at one height (within 8 px),
    30-90 px apart - (row, column) of each, left to right; a lone white speck elsewhere (a highlight) is not an eye."""
    w = (a[..., 0] > thresh) & (a[..., 1] > thresh) & (a[..., 2] > thresh) & (a[..., 3] > 200)
    lab, k = ndimage.label(w)
    cs = [ndimage.center_of_mass(w, lab, i) for i in range(1, k + 1) if (lab == i).sum() >= least]
    pairs = [(p, q) for p in cs for q in cs if p[1] < q[1] and abs(p[0] - q[0]) <= 8 and 30 <= q[1] - p[1] <= 90]
    if len(pairs) != 1:
        raise SystemExit(f"eyes: {len(pairs)} pairs among {cs}")
    return list(pairs[0])


def with_head(fig, idle, eye):
    """The idle's head laid with its near eye on the pose's near eye `eye` (row, column on the pose's grid: the left
    white square of Codex's picture)."""
    hm = head_mask(idle, IDLE_NECK, IDLE_CHIN, IDLE_HEAD_COLS, IDLE_JAW_COLS)
    ey, ex = eye
    oy, ox = int(round(ey - IDLE_EYE[0])), int(round(ex - IDLE_EYE[1]))
    pad = 30
    can = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    ys, xs = np.nonzero(hm)
    can[pad + ys + oy, pad + xs + ox] = idle[ys, xs]
    ys, xs = np.nonzero(can[..., 3] > 0)
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (oy, ox)


def graft(fig, side, g):
    """The pose on the side design's legs (GRAFT)."""
    out = fig.copy()
    y0, (c0, c1) = g["split"], g["cols"]
    out[y0:, c0:c1 + 1] = 0
    out[g["low"][0]:, g["low"][1]:] = 0
    legs = side[DESIGN_LEGS:]
    H = max(out.shape[0], y0 + legs.shape[0])
    W0 = out.shape[1]
    pad = 10
    can = np.zeros((H, W0 + 2 * pad, 4), np.uint8)
    can[:out.shape[0], pad:pad + W0] = out
    xx = np.arange(side.shape[1])
    for part, dx in ((xx <= DESIGN_PART, g["spread"][0]), (xx > DESIGN_PART, g["spread"][1])):
        piece = np.where(part[None, :, None], legs, 0).astype(np.uint8)
        ys, xs = np.nonzero(piece[..., 3] > 0)
        tx = xs + g["hip"] - DESIGN_PART + dx + pad
        ok = (tx >= 0) & (tx < can.shape[1])
        can[ys[ok] + y0, tx[ok]] = piece[ys[ok], xs[ok]]
    # the gaps between the pose's belt and the legs' tops (enclosed and small): the outline
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    ink = PD.edge_colour(side)
    for j in range(1, n + 1):
        h = lab == j
        if h.sum() <= 20:
            can[h] = (*ink, 255)
    ys, xs = np.nonzero(can[..., 3] > 0)
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def finish(fig, most=12):
    """The outline closed; small enclosed holes the readback left (under the lying figure's scarf) take the outline."""
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


def read(name, side, idle):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"graves-pose-{name}.png"))).convert("RGBA"))
    sc = SCALE[name]
    fig = snap(sample(a, sc), side)
    ys, xs = np.nonzero(a[..., 3] >= 128)
    ey, ex = eyes(a)[0]                               # the near (left) eye, Codex's px
    fig, _ = with_head(fig, idle, ((ey - ys.min()) / sc - 0.5, (ex - xs.min()) / sc - 0.5))
    if name in GRAFT:
        fig = graft(fig, side, GRAFT[name])
    return finish(fig)


def big(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    side = np.asarray(Image.open(lp(os.path.join(OUT, "side.png"))).convert("RGBA"))
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    figs = {n: read(n, side, idle) for n in SCALE}
    if a.sheet:
        os.makedirs(a.sheet, exist_ok=True)
        z = 6
        cells = [("side design", side)] + list(figs.items())
        W = sum(f.shape[1] * z + 20 for _, f in cells) + 20
        H = max(f.shape[0] for _, f in cells) * z + 60
        can = Image.new("RGB", (W, H), (255, 255, 255))
        dr = ImageDraw.Draw(can)
        x = 20
        for name, f in cells:
            b = big(f, z)
            can.paste(b.convert("RGB"), (x, H - 20 - b.height))
            dr.text((x, 4), f"{name} {f.shape[1]}x{f.shape[0]}", fill=(0, 0, 0))
            x += b.width + 20
        dr.line([(0, H - 20), (W, H - 20)], fill=(200, 0, 0))
        can.save(os.path.join(a.sheet, "graves_poses_sheet.png"))
        print(os.path.join(a.sheet, "graves_poses_sheet.png"))
        return
    for n, f in figs.items():
        Image.fromarray(f).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        print(n, f.shape[1], "x", f.shape[0])


if __name__ == "__main__":
    main()
