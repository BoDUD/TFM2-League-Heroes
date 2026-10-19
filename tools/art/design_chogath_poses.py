#!/usr/bin/env python3
"""Cho'Gath's Codex poses (assets/source/chogath/codex_poses, 2026-10-19, Codex new-chat-7: POSE_PROMPTS.md) read back at
the side design's scale, in its colours, with the idle's head.

    python tools/art/design_chogath_poses.py --sheet DIR     # all poses beside the side design (12x crops + 1x)
    python tools/art/design_chogath_poses.py                 # writes assets/source/chogath/hd/pose_<name>.png

Codex drew the bodies about the asked size but with finer squares (~10 px: its head came out at ~10 px a design square,
the bodies at ~15-17), so its own grid is not ours. Each pose is sampled on a grid of SCALE[name] px a square from
the figure's top-left (SCALE = the square root of the pose's opaque area over the side design's, so every pose carries
the side design's amount of body), a square opaque when most of it is, its colour the median of its opaque pixels;
every colour snaps to the nearest of the side design's own (Lab); the outline closed (strips.complete_outline). One face
in all frames: Codex's smaller head is covered by the idle's head (pack_chogath_side.HEAD) with its eyes on Codex's
eyes (the topmost cyan squares; the tongue's cyan below is not used).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import pixel_down as PD  # noqa: E402
import strips  # noqa: E402
from design_chogath_hd import lp  # noqa: E402
from design_chogath_side import cyan, snap  # noqa: E402
from pack_chogath_side import HEAD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "chogath", "codex_poses", "chogath-poses")
OUT = os.path.join(ROOT, "assets", "source", "chogath", "hd")
POSES = ["crouch", "rise", "rear", "slam", "lunge", "fall", "lie"]


def area_scale(a, side):
    return float(np.sqrt((a[..., 3] >= 128).sum() / (side[..., 3] > 0).sum()))


def sample(a, s):
    """One square per s x s px cell from the figure's top-left: opaque when most of it is, the median colour."""
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    y0, x0 = ys.min(), xs.min()
    H = int(np.ceil((ys.max() + 1 - y0) / s))
    W = int(np.ceil((xs.max() + 1 - x0) / s))
    out = np.zeros((H, W, 4), np.uint8)
    for j in range(H):
        for i in range(W):
            ya, yb = int(round(y0 + j * s)), int(round(y0 + (j + 1) * s))
            xa, xb = int(round(x0 + i * s)), int(round(x0 + (i + 1) * s))
            m = op[ya:yb, xa:xb]
            if m.size and m.mean() > 0.5:
                out[j, i, :3] = np.median(a[ya:yb, xa:xb][m][:, :3], 0)
                out[j, i, 3] = 255
    return out


def eye_point(fig):
    """The middle of the topmost cyan rows (the eyes; the tongue's cyan lies lower)."""
    yy, xx = np.nonzero(cyan(fig))
    top = yy <= yy.min() + 2
    return yy[top].mean(), xx[top].mean()


def with_head(fig, idle):
    r0, r1, c0, c1 = HEAD
    head = idle[r0:r1, c0:c1]
    hy, hx = eye_point(head)
    sy, sx = eye_point(fig)
    oy, ox = int(round(sy - hy)), int(round(sx - hx))
    pad = 30
    can = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    m = head[..., 3] > 0
    can[pad + oy:pad + oy + head.shape[0], pad + ox:pad + ox + head.shape[1]][m] = head[m]
    ys, xs = np.nonzero(can[..., 3] > 0)
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def finish(fig):
    ink = PD.edge_colour(fig)
    pad = np.pad(fig, ((1, 1), (1, 1), (0, 0)))
    pad, _, _ = strips.complete_outline(pad, color=ink, feet=fig.shape[0])
    ys, xs = np.nonzero(pad[..., 3] > 0)
    return pad[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


# ------------------------------------------------------------------------------------------------- the hind legs
# Codex drew the hind legs of rise, rear and slam thin and long (3-4 squares thick, 14-17 rows; the side design's are
# 5-6 thick and 9-12 rows) - the user, 2026-10-19, picked round 1's slim bodies with the legs mended here: its legs are
# cut away and the side design's own hind legs (lossless pieces, below) put on, the near one in front of the body and the
# far one behind it, a step to the right and two rows higher as on the side design (its far foot is lifted).
# The side design's hind legs (hd/side.png rows, columns): the near leg with its hip plate and its big talon foot, the far
# leg with its own talons.
NEAR_LEG = (33, 44, 16, 30)
FAR_LEG = (34, 42, 31, 41)
# per pose: cut = boxes (rows r0-r1, columns c0-c1, inclusive) whose squares are Codex's legs; keep = boxes of squares
# that stay where they are (rear's tail lying on the ground); drop = rows the rest of the body comes down onto the new
# legs; near = the near leg piece's left column on the pose (its feet on the ground row, the far piece placed from it as
# on the side design). Slam keeps Codex's legs: they kick back in the air 5-7 squares thick and 12-15 long, about the
# side design's own (the side design's legs turned a quarter there read as two lumps).
LEGFIX = {
    "rise": dict(cut=[(54, 64, 23, 63), (53, 56, 60, 70)], keep=[], drop=0, near=28),
    # the tail lies on the ground from the left leg's root: its root (rows 57-63) and the rest of it stay where they
    # are, the leg's shaft right of them and both feet go; the new near leg covers the shaft's last columns
    "rear": dict(cut=[(54, 69, 35, 42), (64, 69, 29, 34), (57, 69, 43, 62)], keep=[(57, 63, 0, 34), (64, 69, 0, 28)],
                 drop=3, near=27),
}


def leg_piece(side, box):
    r0, r1, c0, c1 = box
    return side[r0:r1 + 1, c0:c1 + 1].copy()


def put(can, piece, y, x, under=False):
    """piece's opaque squares onto can at (y, x) (clipped); under: only where can is clear."""
    h, w = piece.shape[:2]
    y0, x0 = max(0, y), max(0, x)
    y1, x1 = min(can.shape[0], y + h), min(can.shape[1], x + w)
    if y1 <= y0 or x1 <= x0:
        return
    sub = piece[y0 - y:y1 - y, x0 - x:x1 - x]
    m = sub[..., 3] > 0
    if under:
        m &= can[y0:y1, x0:x1, 3] == 0
    can[y0:y1, x0:x1][m] = sub[m]


def fix_legs(name, fig, side):
    """The pose with Codex's hind legs replaced by the side design's (LEGFIX)."""
    fx = LEGFIX[name]
    H, W = fig.shape[:2]
    cut = np.zeros((H, W), bool)
    for r0, r1, c0, c1 in fx["cut"]:
        cut[r0:r1 + 1, c0:c1 + 1] = True
    keep = np.zeros((H, W), bool)
    for r0, r1, c0, c1 in fx["keep"]:
        keep[r0:r1 + 1, c0:c1 + 1] = True
    op = fig[..., 3] > 0
    fixed = op & keep & ~cut
    body = op & ~cut & ~keep
    pad = 16
    can = np.zeros((H + 2 * pad, W + 2 * pad, 4), np.uint8)
    near, far = leg_piece(side, NEAR_LEG), leg_piece(side, FAR_LEG)
    ground = pad + H - 1                                         # the pose's ground row on the canvas
    nx = pad + fx["near"]
    ny = ground - near.shape[0] + 1
    fxx = nx + (FAR_LEG[2] - NEAR_LEG[2])
    fy = ny + (FAR_LEG[0] - NEAR_LEG[0])
    put(can, far, fy, fxx)
    # the fixed part (on the ground), then the body brought down onto the legs
    lay = np.zeros_like(can)
    lay[pad:pad + H, pad:pad + W][fixed] = fig[fixed]
    m = lay[..., 3] > 0
    can[m] = lay[m]
    lay = np.zeros_like(can)
    d = fx["drop"]
    lay[pad + d:pad + d + H, pad:pad + W][body] = fig[body]
    m = lay[..., 3] > 0
    can[m] = lay[m]
    put(can, near, ny, nx)
    ys, xs = np.nonzero(can[..., 3] > 0)
    return can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def build(name, side, idle):
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"chogath-pose-{name}.png"))).convert("RGBA"))
    s = area_scale(a, side)
    fig = snap(sample(a, s), side)
    fig = with_head(fig, idle)
    if name in LEGFIX:
        fig = fix_legs(name, finish(fig), side)
    fig = finish(fig)
    return fig, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    side = np.asarray(Image.open(lp(os.path.join(OUT, "side.png"))).convert("RGBA"))
    idle = np.asarray(Image.open(lp(os.path.join(OUT, "idle.png"))).convert("RGBA"))
    figs = {}
    for n in POSES:
        figs[n], s = build(n, side, idle)
        print(n, f"{s:.1f} px a square ->", figs[n].shape[1], "x", figs[n].shape[0])
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        cells = [("side", side)] + list(figs.items())
        z = 6
        H = max(c.shape[0] for _, c in cells)
        W = sum(c.shape[1] + 4 for _, c in cells)
        can = Image.new("RGBA", (W * z, (H + 6) * z), (96, 112, 96, 255))
        x = 0
        for _, c in cells:
            im = Image.fromarray(np.repeat(np.repeat(c, z, 0), z, 1))
            can.alpha_composite(im, (x * z, (H + 3 - c.shape[0]) * z))
            x += c.shape[1] + 4
        can.convert("RGB").save(lp(os.path.join(a.sheet, "chogath_poses.png")))
        return
    for n, f in figs.items():
        Image.fromarray(f).save(lp(os.path.join(OUT, f"pose_{n}.png")))


if __name__ == "__main__":
    main()
