#!/usr/bin/env python3
"""Zippy's redrawn run (assets/source/zippy/codex_run: RUN_PROMPTS.md, 8 frames over the whole 0.8 s sprint with both
passings, after the user's 「感觉走路换腿有点问题啊」, 2026-10-31) at the design's body size, on the design's palette, gaps
closed, the design's face on each - design_zippy_poses.py's reading, the run's own source.

    python tools/art/design_zippy_run.py --sheet DIR      # the eight frames beside the design (4x)
    python tools/art/design_zippy_run.py                  # writes assets/source/zippy/hd/pose_run<k>.png (+ .json)

Codex drew over the run pack's references (pack_zippy_run.py: the same canvas, scale and root column as the pose pack)
and only moved each drawing up or down to put its lowest row on the line (manifest.json translation_px, x always 0), so
the root's column is ROOT_X as for the poses. It drew on ~7 px squares (the regrid edge phase reads 7 across and down;
8 across on run2, run4, run5 and run8 is its 7 px squares read a little wide), the head copied square for square: read
on SQ px the design's face matches best (88-97% of its squares) - so every frame is read on SQ px squares, one design
square each (no bringing down), snapped to the design's colours, its cracks closed and the design's face pasted
(design_zippy_poses.put_face). Its legs swap as asked (feet.json: the near leg ahead in run1-2, the far one in run4-7,
the toes level in run3 and run8; Codex's validation.json).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_zippy_poses as DP  # noqa: E402
import regrid as RG  # noqa: E402
from design_zippy_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "zippy", "codex_run", "zippy-run")
OUT = DP.OUT
ROOT_X = DP.ROOT_X            # the run pack's root column on the canvas (pack_zippy_run: as the pose pack)
SQ = 7.0                      # Codex's squares (px), one design square each
NAMES = [f"run{k}" for k in range(1, 9)]


def read(name):
    """A run frame on SQ px squares, the design's palette and face -> (figure, the root's square in it, the face's
    offset)."""
    d = DP.design()
    a = np.asarray(Image.open(lp(os.path.join(SRC, f"zippy-run-{name}.png"))).convert("RGBA")).copy()
    g, _, (bx, _) = RG.regrid(a, SQ)
    gy, gx = np.nonzero(g[..., 3] >= 128)
    i = max(0, np.searchsorted(bx, ROOT_X) - 1)
    col = i + (ROOT_X - bx[i]) / SQ
    g = g[gy.min():gy.max() + 1, gx.min():gx.max() + 1].copy()
    g[..., 3] = np.where(g[..., 3] >= 128, 255, 0)
    root = (col - gx.min(), g.shape[0])
    g = close_gaps(DP.snap(g, d), d)
    g, off, share = DP.put_face(g, d)
    print(f"{name}: face at {off}, {share:.0%} of its squares matched before")
    op = g[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < DP.SPECK:
            g[lb == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    face = None if off is None else (int(off[0] - xs.min()), int(off[1] - ys.min()))
    return (g[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (round(root[0] - xs.min()), round(root[1] - ys.min())),
            face)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    a = ap.parse_args()
    figs = {n: read(n) for n in NAMES}
    for n, (fig, piv, face) in figs.items():
        print(f"{n}: {fig.shape[1]} x {fig.shape[0]}, pivot at {piv}, face at {face}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", DP.design())] + [(n, figs[n][0]) for n in NAMES]
        Hm = max(t.shape[0] for _, t in tiles)
        W = sum(t.shape[1] * z + 12 for _, t in tiles)
        sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
        dr = ImageDraw.Draw(sheet)
        x = 0
        for n, t in tiles:
            sheet.alpha_composite(DP.big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
            dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
            x += t.shape[1] * z + 12
        path = os.path.join(a.sheet, "zippy_run_frames.png")
        sheet.convert("RGB").save(lp(path))
        print(path)
        return
    for n, (fig, piv, face) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"pivot": [piv[0], piv[1]], "face": None if face is None else [face[0], face[1]]}, fh)


if __name__ == "__main__":
    main()
