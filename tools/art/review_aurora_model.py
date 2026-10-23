#!/usr/bin/env python3
"""Aurora's step-1 takes for the user's pick, read on Codex's fine squares and cut at several PPUs (the user: 「太模糊了
用PPU调下像素」): every take at every PPU as the game draws it (hat top to soles 38 game px) beside the pack's mid mages,
feet on one line, and the takes at 4x with their faces at 12x for the middle PPU.

    for p in 1.75 2.0 2.25; do python tools/art/design_aurora_model.py --ppu $p --options C:/t/au_work/opts_$p; done
    python tools/art/review_aurora_model.py --opts C:/t/au_work/opts_{ppu} --out dist/aurora_packs

Writes <out>/aurora_model_review.png.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from review_aurora_size import NEIGHBOURS, frame0, lp, shown  # noqa: E402
from review_illaoi_model import BG, on_bg, row  # noqa: E402

TAKES = ("A-1", "A-2")
PPUS = (1.75, 2.0, 2.25)


def face_box(im):
    """The glasses' eyes (the violet-blue squares) with a margin: the face at 12x."""
    d = np.asarray(im).astype(int)
    m = (d[..., 3] > 0) & (d[..., 2] > 140) & (d[..., 0] < 120) & (d[..., 2] > d[..., 1] + 40)
    m[:d.shape[0] // 4] = False
    m[d.shape[0] // 2:] = False
    ys, xs = np.nonzero(m)
    cy, cx = int(np.median(ys)), int(np.median(xs))
    h = d.shape[0] // 7
    return (max(0, cx - h - 2), max(0, cy - h), min(d.shape[1], cx + h + 2), min(d.shape[0], cy + h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opts", required=True, help="folder pattern with {ppu}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    load = lambda t, p: Image.open(lp(os.path.join(a.opts.format(ppu=p), f"opt_{t}.png"))).convert("RGBA")
    parts = []
    for p in PPUS:
        cells = []
        for t in TAKES:
            im = load(t, p)
            cells.append((f"{t} PPU {p}", f"{im.width}x{im.height} sq = {im.width / p:.0f}x{im.height / p:.0f} px",
                          shown(im, p, 4)))
        for hero in NEIGHBOURS:
            f, q = frame0(hero)
            cells.append((hero, f"{f.width / q:.0f}x{f.height / q:.0f}", shown(f, q, 4)))
        parts.append(row(cells))
    mid = PPUS[len(PPUS) // 2]
    ims = {t: load(t, mid) for t in TAKES}
    parts.append(row([(f"{t} PPU {mid} 4x", "", ims[t].resize((ims[t].width * 4, ims[t].height * 4), Image.NEAREST))
                      for t in TAKES] +
                     [(f"{t} face 12x", "", on_bg(ims[t].crop(face_box(ims[t]))).resize(
                         ((face_box(ims[t])[2] - face_box(ims[t])[0]) * 12,
                          (face_box(ims[t])[3] - face_box(ims[t])[1]) * 12), Image.NEAREST)) for t in TAKES]))
    can = Image.new("RGBA", (max(p.width for p in parts), sum(p.height for p in parts)), BG)
    y = 0
    for p in parts:
        can.alpha_composite(p, (0, y))
        y += p.height
    os.makedirs(lp(a.out), exist_ok=True)
    path = os.path.join(a.out, "aurora_model_review.png")
    can.convert("RGB").save(lp(path))
    print(path, can.size)


if __name__ == "__main__":
    main()
