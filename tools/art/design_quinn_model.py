#!/usr/bin/env python3
"""Quinn's step-1 game-size designs read back on their own grids, one palette for all eight, and cut to the count.

    python tools/art/design_quinn_model.py   # writes assets/source/quinn/hd/model{Q1,Q2,S1,S2,V1,V2,R1,R2}.png,
                                             # the cuts model*_cut.png (+ _8x) and model_review.png

Step 1 (assets/source/quinn/codex_model/quinn-model, 2026-10-19, Codex new-chat-4): asked 22 px squares and 49 rows
crest to soles for Q (3/4 front, the crossbow raised) and S (side-on), 30 px / 34 squares wing tip to wing tip for
Valor (V) and 18 px / about 64 x 49 squares for the ride (R), her head about 15 squares. Codex drew each at its own
square (the commonest run of one colour along the rows, checked against the outline steps): Q-1 19 px, Q-2 20, S-1
19, S-2 15, V-1 22.5, V-2 28, R-1 14.7, R-2 17.5. regrid.py reads each one pixel per drawn square; the colours of all
eight are cut together by k-means in Lab (design_varus.kmeans), alpha 0/255.
The cuts (design_rell_cut.even_cut: whole rows and columns, one per equal window, never the head's rows): Q and S to
ROWS rows; V to VALOR_W columns; R by Q-1's factor (her face as big as the idle's).
"""
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
from design_quinn_hd import lp  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "quinn", "codex_model", "quinn-model")
OUT = os.path.join(ROOT, "assets", "source", "quinn", "hd")
COLOURS = 48
ROWS = 49          # 38 game px x PPU 1.3
VALOR_W = 34
FILES = {"Q1": ("quinn-model-Q-1.png", 19.0), "Q2": ("quinn-model-Q-2.png", 20.0),
         "S1": ("quinn-model-S-1.png", 19.0), "S2": ("quinn-model-S-2.png", 15.0),
         "V1": ("valor-model-V-1.png", 22.5), "V2": ("valor-model-V-2.png", 28.0),
         "R1": ("quinn-model-R-1.png", 14.7), "R2": ("quinn-model-R-2.png", 17.5)}
HEAD_SHARE = 0.34  # crest to chin as a share of Q / S's height (kept whole by the cut)


def read(name):
    fname, size = FILES[name]
    a = np.asarray(Image.open(lp(os.path.join(SRC, fname))).convert("RGBA")).copy()
    d, _, _ = RG.regrid(a, size)
    op = d[..., 3] >= 128
    ys, xs = np.nonzero(op)
    d = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    d[..., 3] = np.where(op[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 255, 0)
    return d


def save(name, d):
    Image.fromarray(d).save(lp(os.path.join(OUT, f"model{name}.png")))
    Image.fromarray(np.repeat(np.repeat(d, 8, 0), 8, 1)).save(lp(os.path.join(OUT, f"model{name}_8x.png")))
    print(name, d.shape[1], "x", d.shape[0])


def head_rows(d):
    return list(range(0, round(d.shape[0] * HEAD_SHARE) + 1))


def main():
    parts = {k: read(k) for k in FILES}
    h = max(p.shape[0] for p in parts.values())
    both = np.zeros((h, sum(p.shape[1] for p in parts.values()), 4), np.uint8)
    x = 0
    for p in parts.values():
        both[:p.shape[0], x:x + p.shape[1]] = p
        x += p.shape[1]
    op = both[..., 3] > 0
    idx, pal = V.kmeans(both, COLOURS)
    out = np.zeros_like(both)
    out[op, :3] = pal[idx[op]]
    out[op, 3] = 255
    x = 0
    done = {}
    for name, p in parts.items():
        part = out[:p.shape[0], x:x + p.shape[1]]
        x += p.shape[1]
        part = part[np.ix_(np.any(part[..., 3] > 0, 1), np.any(part[..., 3] > 0, 0))].copy()
        done[name] = part
        save(name, part)
    cuts = {}
    for name in ("Q1", "Q2", "S1", "S2"):
        d = done[name]
        cols = round(d.shape[1] * ROWS / d.shape[0])
        cuts[name] = RC.even_cut(d, ROWS, cols, (head_rows(d), []))
    for name in ("V1", "V2"):
        d = done[name]
        rows = round(d.shape[0] * VALOR_W / d.shape[1])
        cuts[name] = RC.even_cut(d, rows, VALOR_W, ([], []))
    k = ROWS / done["Q1"].shape[0]
    for name in ("R1", "R2"):
        d = done[name]
        cuts[name] = RC.even_cut(d, round(d.shape[0] * k), round(d.shape[1] * k), ([], []))
    for name, d in cuts.items():
        save(name + "_cut", d)
    # the review sheet: every take as drawn and cut, 6x, labelled
    cells = []
    for name in FILES:
        for tag, d in (("", done[name]), ("_cut", cuts[name])):
            cells.append((f"{name}{tag} {d.shape[1]}x{d.shape[0]}", np.repeat(np.repeat(d, 6, 0), 6, 1)))
    rows_ = [cells[:8], cells[8:]]
    W = max(sum(c[1].shape[1] + 16 for c in r) for r in rows_) + 16
    Hs = [max(c[1].shape[0] for c in r) + 40 for r in rows_]
    can = Image.new("RGBA", (W, sum(Hs)), (200, 200, 200, 255))
    dr = ImageDraw.Draw(can)
    y = 0
    for r, H in zip(rows_, Hs):
        x = 16
        for label, im in r:
            can.alpha_composite(Image.fromarray(im), (x, y + H - im.shape[0] - 4))
            dr.text((x, y + 6), label, fill=(20, 20, 20, 255))
            x += im.shape[1] + 16
        y += H
    can.convert("RGB").save(lp(os.path.join(OUT, "model_review.png")))


if __name__ == "__main__":
    main()
