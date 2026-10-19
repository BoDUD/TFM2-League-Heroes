#!/usr/bin/env python3
"""LeBlanc's run legs from Codex (tools/art/pack_leblanc_legs.py's pack; delivered 2026-10-19 as
outputs/leblanc-legs/leblanc-legs-run.png, 1514 x 1039 for the asked 1680 x 1152: its squares 5.41 px) read back:
each cell's upper body matched square for square against the design's (an offset of a few px, the frame's bob
included), then only the squares below the gold belt - the legs and the gown - taken, each square's centre colour
snapped to the design's palette; the upper body, the staff arm and the cape at her back stay the design's own
(Codex redrew them, 「上半身和披风经过模型重绘」 in its HANDOFF).

    python tools/art/import_leblanc_legs.py --sheet <leblanc-legs-run.png> [--review DIR]

-> assets/source/leblanc/hd/run_lower_<k>.png (k 0-7): the design-sized lower layer of run frame k on a canvas
LOW_PAD squares wider each side (a stride reaches past the design's columns), rows from HIP_ROW + 1 down, and
hd/run_lower.json (each frame's bob in rows). With --review: the eight frames (our upper body over the read-back
lower half) beside Codex's cells at 6x.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pack_leblanc_legs as P  # noqa: E402
import ppu_rig as R  # noqa: E402

HD = os.path.join(R.ROOT, "assets", "source", "leblanc", "hd")
LOW_PAD = 12                      # squares either side of the design's columns the lower layer may reach
SEARCH = 14                       # px searched round the expected place of each cell's upper body
NEW_DIST, NEW_SHADES = 40, 3      # a colour this far from every design colour is new; the new ones cut to this many


def is_key(p):
    return p[..., 1] > 200 and p[..., 0] < 90 and p[..., 2] < 90


def palette():
    d = np.asarray(Image.open(R.lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)


def read(sheet_path):
    src = np.asarray(Image.open(sheet_path).convert("RGB")).astype(int)
    H, W = src.shape[:2]
    cw, ch = W / 4, H / 2
    s = cw / P.CW
    body = P.body(P.rest_body())
    ox, oy = P.STAND[0] - P.STAND_COL, P.STAND[1] - P.GROUND
    pal = palette()
    new = []

    def at(cell, r, c, dx, dy):
        x, y = int((c + ox + 0.5) * s + dx), int((r + oy + 0.5) * s + dy)
        if 0 <= y < cell.shape[0] and 0 <= x < cell.shape[1]:
            p = cell[y, x]
            if not (p[1] > p[0] + 40 and p[1] > p[2] + 40):        # green ground and the dark green cell lines
                return p
        return None

    up_rows = range(10, P.HIP_ROW + 1)
    ref = body[10:P.HIP_ROW + 1, :, 3] > 0
    frames = []
    for k in range(8):
        x0, y0 = int(round((k % 4) * cw)), int(round((k // 4) * ch))
        cell = src[y0:int(round(y0 + ch)), x0:int(round(x0 + cw))]
        best = None
        for dy in range(-SEARCH, SEARCH + 1):
            for dx in range(-SEARCH, SEARCH + 1):
                got = np.array([[at(cell, r, c, dx, dy) is not None for c in range(body.shape[1])] for r in up_rows])
                score = int((got ^ ref).sum())
                if best is None or score < best[0]:
                    best = (score, dx, dy)
        score, dx, dy = best
        bob = int(round(dy / s))
        rows = range(P.HIP_ROW + 1, P.CH - oy)
        low = np.zeros((len(rows), body.shape[1] + 2 * LOW_PAD, 4), np.uint8)
        for i, r in enumerate(rows):
            for j, c in enumerate(range(-LOW_PAD, body.shape[1] + LOW_PAD)):
                if c < P.CAPE_X and c >= 0:
                    continue                                 # the cape at her back: the design's own
                p = at(cell, r, c, dx, dy - bob * s)
                if p is None:
                    continue
                low[i, j] = (*p, 255)
        frames.append([low, bob, score, dx, dy])
    # the colours the design has none of (Codex's sheer stockings: no near design colour within NEW_DIST) cut to
    # NEW_SHADES by k-means and added to the palette; every square then snapped to the nearest
    allpx = np.concatenate([f[0][f[0][..., 3] > 0][:, :3].astype(int) for f in frames])
    far = allpx[np.min(((allpx[:, None, :] - pal[None]) ** 2).sum(-1), 1) > NEW_DIST ** 2]
    if len(far) >= NEW_SHADES:
        cents = kmeans(far, NEW_SHADES)
        pal = np.concatenate([pal, cents])
    print("palette", len(pal), "added", len(pal) - len(palette()))
    for f in frames:
        low = f[0]
        m = low[..., 3] > 0
        px = low[m][:, :3].astype(int)
        low[m, :3] = pal[np.argmin(((px[:, None, :] - pal[None]) ** 2).sum(-1), 1)]
        # one-square dark hairs (clear on both sides: Codex's own cape edge hanging beside the design's cape) go
        for _ in range(4):
            op = low[..., 3] > 0
            dk = op & (low[..., :3].astype(int).sum(-1) < 70)
            lone = dk.copy()
            lone[:, 1:-1] &= ~op[:, :-2] & ~op[:, 2:]
            lone[:, 0] = lone[:, -1] = False
            if not lone.any():
                break
            low[lone] = 0
        m = low[..., 3] > 0
        # pieces apart from the figure (specks, a cell line's leavings) go
        lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(m, lbl, range(1, n + 1))
            for k in range(1, n + 1):
                if sz[k - 1] < 12:
                    low[lbl == k] = 0
    return [tuple(f) for f in frames]


def kmeans(px, k, iters=30):
    px = px.astype(float)
    cents = px[np.linspace(0, len(px) - 1, k).astype(int)].copy()
    for _ in range(iters):
        lab = np.argmin(((px[:, None, :] - cents[None]) ** 2).sum(-1), 1)
        for j in range(k):
            if (lab == j).any():
                cents[j] = px[lab == j].mean(0)
    return np.round(cents).astype(int)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--review")
    a = ap.parse_args()
    frames = read(a.sheet)
    meta = []
    for k, (low, bob, score, dx, dy) in enumerate(frames):
        Image.fromarray(low).save(R.lp(os.path.join(HD, f"run_lower_{k}.png")))
        meta.append(dict(bob=bob, match=score, dx=dx, dy=dy))
        print(k, "bob", bob, "upper-body mismatch", score, "offset px", dx, dy)
    with open(R.lp(os.path.join(HD, "run_lower.json")), "w", encoding="utf-8") as f:
        json.dump({"hip_row": P.HIP_ROW, "pad": LOW_PAD, "frames": meta}, f, indent=1)


if __name__ == "__main__":
    main()
