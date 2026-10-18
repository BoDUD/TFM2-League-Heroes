#!/usr/bin/env python3
"""Akshan's step-1 take read back on its own grid and brought to the picked game size (PPU 1.5: 57 rows from the top of
the hair to the soles = 38 game rows), with review sheets.

    python tools/art/design_akshan_cut.py --hair R --face R0 R1 C0 C1 [--out dist/akshan_packs]

Step 1 (assets/source/akshan/codex_model, 2026-10-18, Codex new-chat-8) on 1254 squares (asked 15 px squares, 57 rows):
A-1 reads at 10 px (regrid's own measure and the eyes at 5x: a white square and a two-square pupil) and keeps the asked
place (gun top y 152, soles y 1200); A-2 overshoots the canvas and its far eye fails - A-1 is the take (the user left the
strips to me: 「动作帧就参照塔姆那种方法做吧 做好后自己review 真正没问题了完美了喊我review」). Read back (regrid.py, alpha
0/255 at 128), colours cut to COLOURS by k-means (design_varus.kmeans), then brought to BODY rows hair to soles:
  cut - design_rell_cut.even_cut: whole rows / columns dropped one per equal window, never the face's lines (FACE) nor
        two neighbours.
Writes assets/source/akshan/hd/modelA1{,_cut}.png and <out>/akshan_model_review.png (at game size beside the pack's
marksmen: the cut at PPU 1.5 and the uncut read-back at its own PPU) + akshan_model_takes.png (each at 6x).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402
import review_akshan_size as RW  # noqa: E402

lp = RW.lp
SRC = os.path.join(ROOT, "assets", "source", "akshan")
COLOURS = 44
PPU = 1.5
BODY = 57            # hair top to soles (38 game rows)
SIZE = 10.0
HAIR = None          # hair tip row in the read-back (measured below from the tail-free columns when None)
FACE = None          # (rows, cols) of the face, set after the first read
NEIGHBOURS = ["lucian", "jhin", "caitlyn", "gangplank", "xinzhao", "wukong"]
BG = (196, 200, 190, 255)


def read(size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", "akshan-model-A-1.png")))
                   .convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    d = d[np.ix_(np.any(op, 1), np.any(op, 0))].copy()
    op = d[..., 3] >= 128
    idx, pal = V.kmeans(d, COLOURS)
    out = np.zeros_like(d)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "akshan_packs"))
    ap.add_argument("--hair", type=int, required=True, help="top row of the hair in the read-back")
    ap.add_argument("--face", type=int, nargs=4, required=True, metavar=("R0", "R1", "C0", "C1"))
    a = ap.parse_args()
    d = read(SIZE)
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    Image.fromarray(d).save(lp(os.path.join(SRC, "hd", "modelA1.png")))
    body = d.shape[0] - a.hair
    k = BODY / body
    rows, cols = round(d.shape[0] * k), round(d.shape[1] * k)
    r0, r1, c0, c1 = a.face
    cut = RC.even_cut(d, rows, cols, (list(range(r0, r1 + 1)), list(range(c0, c1 + 1))))
    Image.fromarray(cut).save(lp(os.path.join(SRC, "hd", "modelA1_cut.png")))
    own = body / 38
    print("read", d.shape[1], "x", d.shape[0], f"(hair-soles {body}, own PPU {own:.2f}) -> cut", cut.shape[1], "x",
          cut.shape[0])
    cells = [("A-1 cut PPU 1.5", f"{cut.shape[1] / PPU:.0f}x{cut.shape[0] / PPU:.0f}", RW.shown(Image.fromarray(cut), PPU, 4)),
             (f"A-1 uncut PPU {own:.2f}", f"{d.shape[1] / own:.0f}x{d.shape[0] / own:.0f}",
              RW.shown(Image.fromarray(d), own, 4))]
    for hero in NEIGHBOURS:
        im, p = RW.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RW.shown(im, p, 4)))
    RW.strip(cells).convert("RGB").save(lp(os.path.join(a.out, "akshan_model_review.png")))
    close = [("cut 57", "", Image.fromarray(np.repeat(np.repeat(cut, 6, 0), 6, 1))),
             (f"uncut {body}", "", Image.fromarray(np.repeat(np.repeat(d, 6, 0), 6, 1)))]
    RW.strip(close).convert("RGB").save(lp(os.path.join(a.out, "akshan_model_takes.png")))


if __name__ == "__main__":
    main()
