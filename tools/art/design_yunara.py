#!/usr/bin/env python3
"""Yunara's design at the user's size: Codex's step-1 take 2 (assets/source/yunara/hd/model2.png, read back by
tools/art/design_yunara_cut.py: 72 x 103 squares, ornament top to soles) brought to 60 squares (40 game rows at PPU 1.5,
「选 A，40 行，第 1 步按游戏格子重画，头放大到约四分之一，念珠画小一点」), the beads apart from her body.

    python tools/art/design_yunara.py [--review DIR]

Her body and her beads are cut apart first: whole-row / whole-column deletion (design_akali.dp_keep, the way
design_yunara_cut.py cuts) ran through the beads at different places and squashed them into ovals. So:
  body  model2 with the six floating beads taken off (four stand apart; two touch her - the top-left one the ornaments'
        gold tassel at column 20, the lower right one the trousers' outline at column 44 - and are cut off by a disc
        round their centre on their side of that line), whole rows / columns deleted to 60 rows, the closed eye's
        row and columns, the brow and the lips kept (HARD_ROWS / HARD_COLS);
  bead  drawn square by square at BEAD x BEAD in model2's own colours (the step-1 bead sheet's beads, 8 x 8-10 at
        their 11-px grid, are about the size the user asked for, but their row / column cut lost the round outline and
        their k-means colours are not the take's; a 6 x 6 read as a box): an octagon, the light gold on its upper right,
        the brown on its lower left, three studs; her beads are this one bead turned by quarter turns (exact) so they
        do not look stamped and seem to spin as they turn;
  where the beads float: their centres in model2 carried through the body's kept rows and columns.
The violet dragon-head bead hangs from her far hand by its streamers: it stays with the body (it moves with that hand).
Writes assets/source/yunara/hd/design.png (the body), design_keep.json (model2's kept rows / columns), bead.png and
beads.json (the six beads' centres on the design's grid and their quarter turns), and with --review an 8x sheet of
the read-back, the body, the body with its beads and the bead.
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
import design_akali as DA  # noqa: E402
import design_yunara_cut as DC  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "yunara", "hd")
TALL = 60
HARD_ROWS = {21, 24, 26}          # the brow, the closed eye, the lips (model2's rows)
HARD_COLS = {36, 37, 38, 39}      # the lips' and the eye's columns
# the beads touching her: (centre row, centre column, radius, keep-side test) in model2's squares
TOUCHING = [
    (29.0, 14.5, 7.0, lambda R, C: C <= 19),                               # by the ornaments' tassel (column 20)
    (75.5, 51.0, 6.8, lambda R, C: (C >= 45) & ~((R >= 79) & (C == 45))),  # by the trousers' outline (column 44)
]
BEAD = 7                          # the bead's rows and columns on the design
OUTLINE = (8, 2, 14)              # the design's own outline colour
BEAD_COLOURS = {"O": OUTLINE, "B": (164, 81, 50), "K": (91, 51, 53), "G": (223, 155, 48), "L": (248, 194, 68),
                "S": (85, 77, 72), "T": (57, 50, 51), "M": (188, 119, 38)}
BEAD_ROWS = ["..OOO..",            # an octagon reads round at 7 (a 6 x 6 read as a box at game size)
             ".OBGLO.",
             "OKSGLLO",
             "OBBGGTO",
             "OKBSBMO",
             ".OKBBO.",
             "..OOO.."]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def bead_masks(m):
    """The six beads' masks on model2 (the four pieces standing apart, the two touching her)."""
    op = m[..., 3] > 0
    R, C = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    body = 1 + int(np.argmax(sizes))
    masks = [lab == k for k in range(1, n + 1) if k != body]
    for cy, cx, r, side in TOUCHING:
        masks.append(op & ((R - cy) ** 2 + (C - cx) ** 2 <= r * r) & side(R, C))
    return masks


def cut_body(body):
    """body cut to TALL rows (the hard rows / columns kept); (design, kept rows, kept columns) in body's own squares."""
    wt = DC.weights(body)
    code = body.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)
    h, w = body.shape[:2]
    k = TALL / h
    rows, _ = DA.dp_keep(list(code), list(wt), TALL, hard=HARD_ROWS)
    cols, _ = DA.dp_keep(list(code[rows].T), list(wt[rows].T), max(round(w * k), (w + 1) // 2), hard=HARD_COLS)
    return body[rows][:, cols], rows, cols


def bead_sprite():
    out = np.zeros((BEAD, BEAD, 4), np.uint8)
    for r, line in enumerate(BEAD_ROWS):
        for c, ch in enumerate(line):
            if ch != ".":
                out[r, c] = (*BEAD_COLOURS[ch], 255)
    return out


def mapped(kept, v):
    """model2's line v on the design: interpolated between the kept lines, beyond them at the cut's own scale."""
    kept = np.asarray(kept, float)
    idx = np.arange(len(kept), dtype=float)
    k = (len(kept) - 1) / (kept[-1] - kept[0])
    if v < kept[0]:
        return (v - kept[0]) * k
    if v > kept[-1]:
        return idx[-1] + (v - kept[-1]) * k
    return float(np.interp(v, kept, idx))


def place(rows, cols, y, x):
    """model2's (y, x) on the design's grid (may lie left of its first column or right of its last)."""
    return int(round(mapped(rows, y))), int(round(mapped(cols, x)))


def stamp(can, img, cy, cx):
    h, w = img.shape[:2]
    y0, x0 = int(round(cy - (h - 1) / 2)), int(round(cx - (w - 1) / 2))
    m = img[..., 3] > 0
    sub = can[max(0, y0):y0 + h, max(0, x0):x0 + w]
    mm = m[max(0, -y0):max(0, -y0) + sub.shape[0], max(0, -x0):max(0, -x0) + sub.shape[1]]
    sub[mm] = img[max(0, -y0):max(0, -y0) + sub.shape[0], max(0, -x0):max(0, -x0) + sub.shape[1]][mm]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    a = ap.parse_args()
    m = load("model2.png")
    masks = bead_masks(m)
    body = m.copy()
    centres = []
    for bm in masks:
        body[bm] = 0
        ys, xs = np.nonzero(bm)
        centres.append(((ys.min() + ys.max()) / 2.0, (xs.min() + xs.max()) / 2.0))
    ys, xs = np.nonzero(body[..., 3] > 0)
    y0, x0 = int(ys.min()), int(xs.min())
    body = body[y0:ys.max() + 1, x0:xs.max() + 1]
    body = G.complete_outline(body, color=OUTLINE)[0]       # the tassel's and trousers' edges where a bead touched
    design, rows, cols = cut_body(body)
    keep = {"rows": [int(r) + y0 for r in rows], "cols": [int(c) + x0 for c in cols]}
    bead = bead_sprite()
    beads = []
    for k, (cy, cx) in enumerate(sorted(centres)):
        r, c = place(keep["rows"], keep["cols"], cy, cx)
        beads.append({"row": r, "col": c, "turn": k % 4})
    Image.fromarray(design).save(lp(os.path.join(SRC, "design.png")))
    Image.fromarray(bead).save(lp(os.path.join(SRC, "bead.png")))
    with open(lp(os.path.join(SRC, "design_keep.json")), "w", encoding="utf-8") as f:
        json.dump(keep, f)
    with open(lp(os.path.join(SRC, "beads.json")), "w", encoding="utf-8") as f:
        json.dump(beads, f, indent=1)
    print(f"body {body.shape[1]}x{body.shape[0]} -> design {design.shape[1]}x{design.shape[0]}; bead "
          f"{bead.shape[1]}x{bead.shape[0]}; beads at " + ", ".join(f"({b['row']},{b['col']})" for b in beads))
    if not a.review:
        return
    pad = 10
    full = np.zeros((design.shape[0] + 2 * pad, design.shape[1] + 2 * pad, 4), np.uint8)
    full[pad:pad + design.shape[0], pad:pad + design.shape[1]] = design
    for b in beads:
        stamp(full, np.rot90(bead, b["turn"]), b["row"] + pad, b["col"] + pad)
    cells = [("read-back (model2)", m), ("body cut", design), ("with beads", full), ("bead", bead)]
    z = 8
    W = sum(c.shape[1] * z for _, c in cells) + 20 * (len(cells) + 1)
    H = max(c.shape[0] * z for _, c in cells) + 40
    can = Image.new("RGBA", (W, H), (200, 205, 195, 255))
    dr = ImageDraw.Draw(can)
    x = 20
    for lab_, c in cells:
        im = Image.fromarray(c).resize((c.shape[1] * z, c.shape[0] * z), Image.NEAREST)
        can.alpha_composite(im, (x, H - 10 - im.height))
        dr.text((x, 4), lab_, fill=(20, 20, 20, 255))
        x += im.width + 20
    os.makedirs(a.review, exist_ok=True)
    can.convert("RGB").save(os.path.join(a.review, "yunara_design.png"))
    print("review ->", a.review)


if __name__ == "__main__":
    main()
