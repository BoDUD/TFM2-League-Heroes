#!/usr/bin/env python3
"""Cassiopeia's step-1 take read back on its own grid and brought to the picked game size (PPU 1.3: 57 rows from the
crest tip to the ground = 44 game rows), with review sheets.

    python tools/art/design_cassiopeia_cut.py [--take A-2] [--size 15] [--out dist/cassiopeia_packs]

Step 1 (assets/source/cassiopeia/codex_model, 2026-10-18, Codex new-chat-7) on 1254 squares (asked 18 px squares, 57
rows): A-1 reads at 17 px (73 x 71 squares, finer, the crest high and the figure big), A-2 at 15 px (69 x 78 squares:
coarser blocks, League's big diamonds on the tail, both eyes 2 squares, the claws whole). A-2 is the take - fewer
lines to drop and it reads better at game size (the user left the strips to me: 「动作帧就参照塔姆那种方法做吧 做好后自己
review 真正没问题了完美了喊我review」). Read back (regrid.py, alpha 0/255 at 128), colours cut to COLOURS by k-means
(design_varus.kmeans), then brought to BODY rows by design_rell_cut.even_cut: whole rows / columns dropped one per
equal window, never the face's lines (FACE) nor two neighbours.
Writes assets/source/cassiopeia/hd/model{take}{,_cut}.png and <out>/cassiopeia_model_review.png (at game size beside
the pack's mages: the cut at PPU 1.3 and the uncut read-back at its own PPU) + cassiopeia_model_takes.png (each at 6x).
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
import design_rell_cut as RC  # noqa: E402
import design_varus as V  # noqa: E402
import regrid as RG  # noqa: E402
import review_cassiopeia_size as RW  # noqa: E402

lp = RW.lp
SRC = os.path.join(ROOT, "assets", "source", "cassiopeia")
COLOURS = 44
PPU = 1.3
BODY = 57            # crest tip to ground (44 game rows)
GAME = 44
FACE = {"A-2": (18, 28, 54, 67)}   # rows / cols of the eyes, brows, nose, fangs in the read-back
NEIGHBOURS = ["nami", "syndra", "morgana", "elise", "orianna", "swain"]


def read(take, size):
    a = np.asarray(Image.open(lp(os.path.join(SRC, "codex_model", f"cassiopeia-model-{take}.png")))
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
    ap.add_argument("--take", default="A-2")
    ap.add_argument("--size", type=float, default=15.0)
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "cassiopeia_packs"))
    a = ap.parse_args()
    d = read(a.take, a.size)
    tag = a.take.replace("-", "")
    os.makedirs(lp(os.path.join(SRC, "hd")), exist_ok=True)
    Image.fromarray(d).save(lp(os.path.join(SRC, "hd", f"model{tag}.png")))
    k = BODY / d.shape[0]
    rows, cols = BODY, round(d.shape[1] * k)
    r0, r1, c0, c1 = FACE[a.take]
    cut = RC.even_cut(d, rows, cols, (list(range(r0, r1 + 1)), list(range(c0, c1 + 1))))
    Image.fromarray(cut).save(lp(os.path.join(SRC, "hd", f"model{tag}_cut.png")))
    own = d.shape[0] / GAME
    print("read", d.shape[1], "x", d.shape[0], f"(own PPU {own:.2f}) -> cut", cut.shape[1], "x", cut.shape[0])
    cells = [(f"{a.take} cut PPU {PPU:g}", f"{cut.shape[1] / PPU:.0f}x{cut.shape[0] / PPU:.0f}",
              RW.shown(Image.fromarray(cut), PPU, 4)),
             (f"{a.take} uncut PPU {own:.2f}", f"{d.shape[1] / own:.0f}x{d.shape[0] / own:.0f}",
              RW.shown(Image.fromarray(d), own, 4))]
    for hero in NEIGHBOURS:
        im, p = RW.frame0(hero)
        cells.append((hero, f"{im.width / p:.0f}x{im.height / p:.0f}", RW.shown(im, p, 4)))
    os.makedirs(lp(a.out), exist_ok=True)
    RW.strip(cells).convert("RGB").save(lp(os.path.join(a.out, "cassiopeia_model_review.png")))
    close = [(f"cut {BODY}", "", Image.fromarray(np.repeat(np.repeat(cut, 6, 0), 6, 1))),
             (f"uncut {d.shape[0]}", "", Image.fromarray(np.repeat(np.repeat(d, 6, 0), 6, 1)))]
    RW.strip(close).convert("RGB").save(lp(os.path.join(a.out, "cassiopeia_model_takes.png")))


if __name__ == "__main__":
    main()
