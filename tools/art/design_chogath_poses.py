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
# Round 2 (POSE_PROMPTS_2.md: rise, rear and slam redrawn with the side design's thick body and short legs). The user,
# 2026-10-19: round 2 「这大虫子怎么这么胖啊」, round 1 too thin next to oppi's Cho'Gath (its trunk as wide as the head, a
# stalk under it) -> 「身材照着他的修一下就行了 看起来不是太胖也不是太瘦」: round 2's bodies at crouch's scale (17 px a
# square: by area they would come out smaller), then whole columns (and for slam rows) dropped by least loss
# (design_chogath_model.keep_axis). With the head's columns kept the trunk under it stays a head wide and more (1.5 heads:
# 「这有点胖吧」 for the rear), so rise and rear are slimmed whole - Codex's own smaller head too - before the idle's head
# goes on (WHOLE): their trunks 1.25-1.3 heads wide, round 1's 1.0, the fill of the box 0.46-0.49 (oppi 0.45-0.57).
SRC2 = os.path.join(ROOT, "assets", "source", "chogath", "codex_poses2", "chogath-poses2")
ROUND2 = {"rise": (17.0, 0.66, 1.0), "rear": (17.0, 0.66, 1.0), "slam": (17.0, 0.92, 0.92)}
WHOLE = {"rise", "rear"}


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


def slim(fig, idle, cols_k, rows_k):
    """Whole columns / rows dropped by least loss (design_chogath_model.keep_axis), the pasted head's kept."""
    import design_chogath_model as M
    r0, r1, c0, c1 = HEAD
    head = idle[r0:r1, c0:c1]
    hy, hx = eye_point(head)
    ey, ex = eye_point(fig)
    H, W = fig.shape[:2]
    hr, hc = int(round(ey - hy)), int(round(ex - hx))
    keep_c = range(max(0, hc), min(W, hc + head.shape[1]))
    keep_r = range(max(0, hr), min(H, hr + head.shape[0]))
    key = np.where(fig[..., 3] > 0, fig[..., 0].astype(int) * 65536 + fig[..., 1].astype(int) * 256 + fig[..., 2], -1)
    cols = M.keep_axis([key[:, x] for x in range(W)], round(W * cols_k), keep_c) if cols_k < 1 else list(range(W))
    sub = key[:, cols]
    rows = M.keep_axis([sub[y] for y in range(H)], round(H * rows_k), keep_r) if rows_k < 1 else list(range(H))
    return fig[np.ix_(rows, cols)]


def slim_whole(fig, cols_k):
    """Whole columns dropped by least loss over the whole figure (no head kept: the idle's head goes on after)."""
    import design_chogath_model as M
    W = fig.shape[1]
    key = np.where(fig[..., 3] > 0, fig[..., 0].astype(int) * 65536 + fig[..., 1].astype(int) * 256 + fig[..., 2], -1)
    cols = M.keep_axis([key[:, x] for x in range(W)], round(W * cols_k), range(W // 2, W // 2 + 1))
    return fig[:, cols]


def build(name, side, idle):
    if name in ROUND2:
        s, ck, rk = ROUND2[name]
        a = np.asarray(Image.open(lp(os.path.join(SRC2, f"chogath-pose-{name}.png"))).convert("RGBA"))
        raw = snap(sample(a, s), side)
        if name in WHOLE:
            return finish(with_head(slim_whole(raw, ck), idle)), s
        return finish(slim(with_head(raw, idle), idle, ck, rk)), s
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"chogath-pose-{name}.png"))).convert("RGBA"))
    s = area_scale(a, side)
    fig = finish(with_head(snap(sample(a, s), side), idle))
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
