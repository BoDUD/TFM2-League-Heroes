#!/usr/bin/env python3
"""Volibear's walk from Codex's skin swap over oppi's Alistar run (POSE_PROMPTS.md part B) -> assets/source/volibear/hd/
run_<n>.png (+ run.json: each frame's head offset and soles row, the design's head square for square on every frame).

    python tools/art/design_volibear_run.py

Codex's sheet (codex_poses/volibear-pose/raw/volibear-run.png, 2172 x 724, 5 x 2 cells, 9 frames on green) came back at
0.754 of the pack's size; its own squares measure ~5 px (regrid's guesses 5-6), the figures 47-54 squares tall, about
the design's height. Each cell: the green keyed out (g > 180, r and b < 120), the largest piece kept, read back at
SQUARE px, snapped to the design's palette. One face (memory one-face-all-frames): the design's head (the squares of
design_volibear_poses' head: rows 0-12 inside columns 13-38, its inner outline against the shoulders left out) is
matched over each frame (the offset whose squares agree most) and laid over it, Codex's own head cleared within 2
squares above and right of it first (its crown stood higher on some frames: a black spike, a second ear).
"""
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
import regrid as RG  # noqa: E402
import rig_volibear as V  # noqa: E402
import design_volibear_poses as DP  # noqa: E402

lp = V.lp
SRC = os.path.join(ROOT, "assets", "source", "volibear", "codex_poses", "volibear-pose", "raw", "volibear-run.png")
OUT = os.path.join(ROOT, "assets", "source", "volibear", "hd")
SQUARE = 5.0
N = 9


def head_of(D):
    d = D.d
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    head = D.parts["body"] & (yy <= DP.HEAD_ROW) & (xx >= DP.HEAD_COLS[0]) & (xx <= DP.HEAD_COLS[1])
    dk = V.dark(d)
    rest = ~head & (d[..., 3] > 0)
    head &= ~(dk & head & ndimage.binary_dilation(rest & ~dk, structure=V.R.CROSS))
    ys, xs = np.nonzero(head)
    y0, x0 = ys.min(), xs.min()
    m = head[y0:ys.max() + 1, x0:xs.max() + 1]
    return np.where(m[..., None], d[y0:ys.max() + 1, x0:xs.max() + 1], 0).astype(np.uint8), m, (x0, y0)


def best_offset(f, hd, hm):
    """Where the head agrees most with the frame (opaque squares and close colours)."""
    H, W = f.shape[:2]
    h, w = hm.shape
    best = None
    for oy in range(-3, H - h + 1):
        for ox in range(-3, W - w + 4):
            ys, xs = np.nonzero(hm)
            Y, X = ys + oy, xs + ox
            ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
            if ok.sum() < 0.8 * len(ys):
                continue
            fy, fx = Y[ok], X[ok]
            on = f[fy, fx, 3] > 0
            col = np.abs(f[fy, fx, :3].astype(int) - hd[ys[ok], xs[ok], :3].astype(int)).sum(-1)
            score = on.sum() - (col[on] > 90).sum() * 0.5
            if best is None or score > best[0]:
                best = (score, ox, oy)
    return best[1], best[2]


def main():
    D = V.front()
    d = D.d
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)
    hd, hm, (hx0, hy0) = head_of(D)
    a = np.asarray(Image.open(lp(SRC)).convert("RGBA")).copy()
    r, g, b = (a[..., i].astype(int) for i in range(3))
    a[(g > 180) & (r < 120) & (b < 120), 3] = 0
    H, W = a.shape[:2]
    cw, ch = W / 5, H / 2
    meta = []
    for n in range(N):
        x0, y0 = int(n % 5 * cw), int(n // 5 * ch)
        c = a[y0:int(y0 + ch), x0:int(x0 + cw)].copy()
        op = c[..., 3] > 0
        lbl, k = ndimage.label(op, structure=np.ones((3, 3)))
        sz = ndimage.sum(op, lbl, range(1, k + 1))
        c[lbl != 1 + int(np.argmax(sz)), 3] = 0
        f, _, _ = RG.regrid(c, SQUARE)
        f[..., 3] = np.where(f[..., 3] >= 128, 255, 0)
        f = DP.snap(f, pal)
        pad = 4
        f = np.pad(f, ((pad, 0), (0, pad), (0, 0)))
        ox, oy = best_offset(f, hd, hm)
        ys, xs = np.nonzero(hm)
        # Codex's own head where it stood out of the design's (a higher crown, a second ear): cleared within 2 squares
        # above and right of the head, never on the shoulder hump left and below it
        put = np.zeros(f.shape[:2], bool)
        put[ys + oy, xs + ox] = True
        yy, xx = np.mgrid[0:f.shape[0], 0:f.shape[1]]
        ring = ndimage.binary_dilation(put, iterations=2) & ~put & (yy <= oy + 9) & (xx >= ox + 4)
        f[ring] = 0
        f[ys + oy, xs + ox] = hd[ys, xs]
        f = f[np.ix_(np.any(f[..., 3] > 0, 1), np.any(f[..., 3] > 0, 0))]
        top = int(np.nonzero(np.any(f[..., 3] > 0, 1))[0][0])
        Image.fromarray(f).save(lp(os.path.join(OUT, f"run_{n}.png")))
        meta.append({"size": [f.shape[1], f.shape[0]], "head": [int(ox), int(oy - pad)], "soles": f.shape[0]})
        print(n, f.shape[1], "x", f.shape[0], "head at", (ox, oy - pad), "top", top)
    # the design's (0, 0) for a frame = its head's place minus the head's own place in the design
    for m in meta:
        m["origin"] = [m["head"][0] - int(hx0), m["head"][1] - int(hy0)]
    with open(lp(os.path.join(OUT, "run.json")), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh)
    big = [np.asarray(Image.open(lp(os.path.join(OUT, f"run_{n}.png")))) for n in range(N)]
    Hm = max(x.shape[0] for x in big)
    sheet = np.zeros((Hm, sum(x.shape[1] + 2 for x in big), 4), np.uint8)
    x = 0
    for im in big:
        sheet[Hm - im.shape[0]:, x:x + im.shape[1]] = im
        x += im.shape[1] + 2
    Image.fromarray(np.repeat(np.repeat(sheet, 6, 0), 6, 1)).save(lp(os.path.join(OUT, "run_6x.png")))


if __name__ == "__main__":
    main()
