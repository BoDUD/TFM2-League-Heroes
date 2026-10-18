#!/usr/bin/env python3
"""Gangplank's walk: Codex's skin swap over oppi's Swain run (assets/source/gangplank/codex_run/gangplank-run-generated.png,
2026-10-18, tools/art/pack_redo_1018.py; the user: 「船长走路也有点僵硬的」) read back as 8 frames on the design's grid for
tools/art/rig_gangplank.py.

    python tools/art/design_gangplank_run.py [--probe]   # -> assets/source/gangplank/hd/run_<k>.png (k = 0..7)

Read from Codex's raw generation (1902 x 827; the delivered 2208 x 960 is that picture enlarged by 1.16, so its squares
are uneven). Each figure is found as a big non-green piece, read back at SIZE px a square (regrid.py; --probe prints the
read-back heights at several sizes against the design's 62 rows hat to soles), alpha 0/255 at 128; the key's fringe
(green 40 over red and blue) is cleared; every colour is snapped to the design's own palette; 8-connected crumbs of at
most 4 squares apart from the figure are dropped; the design's head, hat and hand cannon (top HEAD_ROWS rows) stamped
on each frame where they match best. The frames keep oppi's order.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import regrid as RG  # noqa: E402


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + p if os.name == "nt" and not p.startswith(pre) else p


SRC = os.path.join(ROOT, "assets", "source", "gangplank")
SHEET = os.path.join(SRC, "codex_run", "gangplank-run-generated.png")
SIZE = 6.15
DESIGN_ROWS = 62
HEAD_ROWS = 24          # the design's hat, face, beard top and the hand cannon on the shoulder: stamped as drawn on every
                        # frame (Codex redrew them 0-15 % bigger or smaller frame to frame - a flickering head)


def stamp_head(d, des):
    """The design's top HEAD_ROWS rows put over the frame where they match best; the frame's own squares inside that
    box cleared first (its redrawn hat and cannon)."""
    t = des[:HEAD_ROWS].astype(float)
    tm = t[..., 3] > 0
    H, W = t.shape[:2]
    f = np.zeros((d.shape[0] + 8, d.shape[1] + 16, 4), np.uint8)
    f[4:4 + d.shape[0], 8:8 + d.shape[1]] = d
    best = None
    for y in range(0, 9):
        for x in range(0, f.shape[1] - W + 1):
            w = f[y:y + H, x:x + W].astype(float)
            m = (w[..., 3] > 0) | tm
            e = (((w[..., :3] - t[..., :3]) ** 2).sum(-1) * m).sum() / m.sum() + 2e4 * ((w[..., 3] > 0) != tm).mean()
            if best is None or e < best[0]:
                best = (e, y, x)
    _, y, x = best
    box = f[y:y + H, x:x + W]
    box[...] = 0
    box[tm] = des[:HEAD_ROWS][tm]
    ys, xs = np.nonzero(f[..., 3])
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (y - 4, x - 8)


def figures(a):
    g = (a[..., 1] > 180) & (a[..., 1] - np.maximum(a[..., 0], a[..., 2]) > 100)
    op = ~g
    lbl, n = ndimage.label(ndimage.binary_closing(op, iterations=3))
    sizes = ndimage.sum(op, lbl, range(1, n + 1))
    boxes = []
    for k in [k + 1 for k, s in enumerate(sizes) if s > 8000]:
        ys, xs = np.nonzero(lbl == k)
        boxes.append((ys.min(), ys.max(), xs.min(), xs.max()))
    boxes.sort(key=lambda b: (b[0] // 300, b[2]))
    if len(boxes) != 8:
        sys.exit(f"{len(boxes)} figures found, not 8")
    return [np.dstack([a[y0:y1 + 1, x0:x1 + 1], np.where(op[y0:y1 + 1, x0:x1 + 1], 255, 0)]).astype(np.uint8)
            for y0, y1, x0, x1 in boxes]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--size", type=float, default=SIZE)
    args = ap.parse_args()
    a = np.asarray(Image.open(lp(SHEET)).convert("RGB")).astype(np.int64)
    figs = figures(a)
    if args.probe:
        print("auto size", RG.regrid(figs[0])[1])
        for s in (5.8, 6.0, 6.1, 6.15, 6.2, 6.3, 6.5):
            print(s, [RG.regrid(f, s)[0].shape[0] for f in figs])
        return
    des = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "design.png"))).convert("RGBA")).astype(np.int64)
    pal = np.unique(des[des[..., 3] > 0][:, :3], axis=0)
    for k, sub in enumerate(figs):
        d, _, _ = RG.regrid(sub, args.size)
        d = d.astype(np.int64)
        op = d[..., 3] >= 128
        op &= ~((d[..., 1] - np.maximum(d[..., 0], d[..., 2])) > 40)
        px = d[op][:, :3]
        d[op, :3] = pal[np.argmin(((px[:, None, :] - pal[None, :, :]) ** 2).sum(-1), 1)]
        lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
        sizes = ndimage.sum(op, lbl, range(1, n + 1))
        for j, z in enumerate(sizes):
            if z <= 4:
                op[lbl == j + 1] = False
        d[..., 3] = np.where(op, 255, 0)
        d[~op] = 0
        ys, xs = np.nonzero(op)
        d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype(np.uint8)
        d, at = stamp_head(d, des.astype(np.uint8))
        Image.fromarray(d).save(lp(os.path.join(SRC, "hd", f"run_{k}.png")))
        print(f"frame {k}: {d.shape[1]} x {d.shape[0]} squares, {n - 1} crumbs before cleaning, head stamped at {at}")


if __name__ == "__main__":
    main()
