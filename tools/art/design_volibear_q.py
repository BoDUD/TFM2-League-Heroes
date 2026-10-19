#!/usr/bin/env python3
"""Volibear's Q from Codex (assets/source/volibear/codex_q, Q_PROMPTS.md) -> assets/source/volibear/hd/q_charge_<n>.png,
q_pounce_<n>.png and q.json (each frame's head offset -> the design's (0, 0), and its lift off the ground).

    python tools/art/design_volibear_q.py

Codex's charge (8 frames, 4 x 2, a skin swap over league_nidalee's cougar run: on all fours) kept the pack's size within
4 % (2098 px wide for 2016): one square is CHARGE_PX. Its pounce (5 frames in a row, take 2 - the dive reads clearest)
came back larger than the pack: its head matches the design's at POUNCE_PX (9 px a square; 7 and 8 tried). Each
frame: the green keyed out (g > 180, r and b < 120), the figure the largest piece (frames ordered by their place), read
back on that square, snapped to the design's palette. Codex's own heads stay: on all fours and in the dive the head is
drawn lowered with the jaws open, so the design's upright head agreed with only 50-70 % of its squares wherever it
was put, and laid over it left a second head round it (tried 2026-10-19); the upright frames agree 96 %. The design's
head only places each frame (the offset whose squares agree most: the head where the idle's is). The pounce keeps
Codex's heights: the soles of its lowest frame are the ground, the leap's frames lift above it.
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
from design_volibear_run import head_of  # noqa: E402

lp = V.lp
SRC = os.path.join(ROOT, "assets", "source", "volibear", "codex_q", "volibear-q", "raw")
OUT = os.path.join(ROOT, "assets", "source", "volibear", "hd")
CHARGE_PX = 6.24
POUNCE_PX = 9.0


def figures(name, rows):
    """The sheet's figures (pieces over 3000 px), ordered row by row (rows: how many) and left to right, each with its
    place on the sheet."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()
    r, g, b = (a[..., i].astype(int) for i in range(3))
    a[(g > 180) & (r < 120) & (b < 120), 3] = 0
    op = a[..., 3] > 0
    lbl, k = ndimage.label(op, structure=np.ones((3, 3)))
    sz = ndimage.sum(op, lbl, range(1, k + 1))
    objs = ndimage.find_objects(lbl)
    band = a.shape[0] / rows
    out = []
    for j in [i + 1 for i in range(k) if sz[i] > 3000]:
        sl = objs[j - 1]
        c = a[sl].copy()
        c[lbl[sl] != j, 3] = 0
        out.append((int((sl[0].start + sl[0].stop) / 2 // band), sl[1].start, sl[0].stop, c))
    return sorted(out, key=lambda t: (t[0], t[1]))


def best_offset(f, hd, hm):
    """Where the design's head agrees square by square with Codex's own head: the most squares of close colour (a
    count of opaque squares alone pulled it into the middle of the body - two heads)."""
    H, W = f.shape[:2]
    h, w = hm.shape
    ys, xs = np.nonzero(hm)
    want = hd[ys, xs, :3].astype(int)
    best = None
    for oy in range(-3, H - h + 4):
        for ox in range(-3, W - w + 4):
            Y, X = ys + oy, xs + ox
            ok = (Y >= 0) & (Y < H) & (X >= 0) & (X < W)
            if ok.sum() < 0.9 * len(ys):
                continue
            got = f[Y[ok], X[ok]].astype(int)
            close = (got[:, 3] > 0) & (np.abs(got[:, :3] - want[ok]).sum(-1) < 70)
            score = close.sum() - 0.5 * (got[:, 3] == 0).sum()
            if best is None or score > best[0]:
                best = (score, ox, oy)
    return best[1], best[2]


def frame(c, px, pal, hd, hm):
    f, _, _ = RG.regrid(c, px)
    f[..., 3] = np.where(f[..., 3] >= 128, 255, 0)
    f = DP.snap(f, pal)
    pad = 4
    f = np.pad(f, ((pad, 0), (pad, pad), (0, 0)))
    ox, oy = best_offset(f, hd, hm)            # (only to place the frame: the head where the idle's is)
    rows = np.nonzero(np.any(f[..., 3] > 0, 1))[0]
    cols = np.nonzero(np.any(f[..., 3] > 0, 0))[0]
    f = f[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]
    return f, (int(ox - cols[0]), int(oy - rows[0]))


def main():
    D = V.front()
    d = D.d
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)
    hd, hm, (hx0, hy0) = head_of(D)
    meta = {}
    for key, name, rows, px in (("charge", "volibear-q-charge.png", 2, CHARGE_PX),
                                ("pounce", "volibear-q-pounce-2.png", 1, POUNCE_PX)):
        figs = figures(name, rows)
        ground = max(f[2] for f in figs)
        meta[key] = []
        tiles = []
        for n, (_, _, bottom, c) in enumerate(figs):
            f, (hx, hy) = frame(c, px, pal, hd, hm)
            Image.fromarray(f).save(lp(os.path.join(OUT, f"q_{key}_{n}.png")))
            lift = int(round((ground - bottom) / px)) if key == "pounce" else 0
            meta[key].append({"size": [f.shape[1], f.shape[0]], "origin": [hx - int(hx0), hy - int(hy0)], "lift": lift})
            tiles.append(f)
            print(key, n, f.shape[1], "x", f.shape[0], "head", (hx, hy), "lift", lift)
        Hm = max(t.shape[0] for t in tiles)
        sheet = np.zeros((Hm, sum(t.shape[1] + 2 for t in tiles), 4), np.uint8)
        x = 0
        for t in tiles:
            sheet[Hm - t.shape[0]:, x:x + t.shape[1]] = t
            x += t.shape[1] + 2
        Image.fromarray(np.repeat(np.repeat(sheet, 6, 0), 6, 1)).save(lp(os.path.join(OUT, f"q_{key}_6x.png")))
    with open(lp(os.path.join(OUT, "q.json")), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(meta, fh)


if __name__ == "__main__":
    main()
