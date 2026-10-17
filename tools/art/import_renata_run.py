#!/usr/bin/env python3
"""Renata's walk from Codex's skin swap (assets/source/renata/codex_run: League's own Run as the skeleton, our idle as
the skin - tools/art/pack_renata_run.py; the user, 2026-10-17: 「codex重画的交付了 你处理一洗吧」) brought to the design.

    python tools/art/import_renata_run.py [--review DIR]

Codex's picture is 1717 x 916 RGB (not the pack's 1440 x 768), a 4 x 2 sheet on an uneven green, drawn on its own ~6 px
squares, the figure 66-70 squares tall: League's proportions (its legs half again as long as ours), our head and torso.
Per frame: the green keyed with a tolerance, the cell read back square by square on its own grid (regrid, 6 px), every
square snapped to the design's nearest colour; the legs - the LEG_SRC rows over the soles - brought to the design's
LEG_DST rows by whole rows taken at one fixed spacing (the same rows of every frame, counted from its soles: no
flicker), everything over them kept as drawn; then the design's own head (hair, face, mask: rows 0..HEAD_ROWS-1 of
the body part, never the pistol) laid over Codex's where it matches best, so the face is the idle's in every frame.
Writes assets/source/renata/hd/run.npz: the 8 frames (RGBA, design squares) and where each one's head sits (its
design (0, 0) in the frame), for tools/art/rig_renata.py's run_frames.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import regrid as RG  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "renata", "codex_run", "renata_run_swap.png")
OUT = os.path.join(ROOT, "assets", "source", "renata", "hd", "run.npz")
COLS, ROWS = 4, 2
SQ = 6.0                 # Codex's own squares (regrid's measure)
LEG_SRC, LEG_DST = 35, 23   # Codex's legs (waist to soles) -> the design's
HEAD_ROWS = 13           # the design's head: hair top to the mask's lower edge


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def keyed_cells():
    a = np.asarray(Image.open(lp(SRC)).convert("RGB")).astype(int)
    H, W = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    key = (g > 140) & (g > r + 60) & (g > b + 60)
    rgba = np.dstack([a, np.where(key, 0, 255)]).astype(np.uint8)
    rgba[key] = 0
    cw, ch = W / COLS, H / ROWS
    return [rgba[int(round((k // COLS) * ch)):int(round((k // COLS + 1) * ch)),
                 int(round((k % COLS) * cw)):int(round((k % COLS + 1) * cw))].copy() for k in range(COLS * ROWS)]


def read_back(cell, pal):
    d, _, _ = RG.regrid(cell, SQ)
    d[..., 3] = np.where(d[..., 3] >= 128, 255, 0)
    op = d[..., 3] > 0
    near = np.argmin(((d[..., :3].astype(int)[..., None, :] - pal[None, None]) ** 2).sum(-1), -1)
    d[op, :3] = pal[near[op]]
    d[~op] = 0
    ys, xs = np.nonzero(op)
    return d[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def shorten(d):
    """The LEG_SRC rows over the soles brought to LEG_DST by whole rows at one spacing (counted from the soles)."""
    top = d.shape[0] - LEG_SRC
    rows = [top + int(np.floor((i + 0.5) * LEG_SRC / LEG_DST)) for i in range(LEG_DST)]
    return np.concatenate([d[:top], d[rows]], 0)


def head_place(d, head, hm):
    """Where the design head matches the frame best: (squares matched, dx, dy) of the head's (0, 0)."""
    ys, xs = np.nonzero(hm)
    best = (-1, 0, 0)
    for dy in range(-3, 7):
        for dx in range(-8, d.shape[1] - head.shape[1] + 9):
            ty, tx = ys + dy, xs + dx
            ok = (ty >= 0) & (ty < d.shape[0]) & (tx >= 0) & (tx < d.shape[1])
            same = np.all(d[ty[ok], tx[ok], :3] == head[ys[ok], xs[ok], :3], -1) & (d[ty[ok], tx[ok], 3] > 0)
            n = int(same.sum())
            if n > best[0]:
                best = (n, dx, dy)
    return best


def build():
    import rig_renata as R
    D = R.DESIGN
    pal = np.unique(D[D[..., 3] > 0][:, :3], axis=0).astype(int)
    hm = (R.LAB == R.BODY) & (np.arange(R.DH)[:, None] < HEAD_ROWS) & (D[..., 3] > 0)
    head = np.zeros_like(D)
    head[hm] = D[hm]
    frames, places = [], []
    for cell in keyed_cells():
        f = shorten(read_back(cell, pal))
        n, dx, dy = head_place(f, head, hm)
        # the design head over Codex's (its squares where the head mask has them)
        ys, xs = np.nonzero(hm)
        ty, tx = ys + dy, xs + dx
        ok = (ty >= 0) & (ty < f.shape[0]) & (tx >= 0) & (tx < f.shape[1])
        f[ty[ok], tx[ok]] = head[ys[ok], xs[ok]]
        frames.append(f)
        places.append((dx, dy))
        print(f"frame {len(frames)}: {f.shape[1]} x {f.shape[0]} squares, head matched {n} of {int(hm.sum())} at ({dx}, {dy})")
    return frames, places


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    frames, places = build()
    np.savez_compressed(lp(OUT), places=np.array(places), **{f"f{i}": f for i, f in enumerate(frames)})
    print("written", OUT)


if __name__ == "__main__":
    main()
