#!/usr/bin/env python3
"""Morgana's eyes as League's (the user, 2026-10-08: 「莫甘娜的眼睛看不看能不能调整 像英雄联盟一点」, picked A): the
pink 2x2 doll eyes become narrow, violet-glowing almond eyes - one lit row (a bright and a deep violet, the bright on
the outer side), the row under them skin, and the lids' outer corners flicked up one square.

    python tools/art/fix_morgana_eyes.py            # edits the design and every strip in place (8x), then
    python tools/art/import_native.py --hero morgana

The face is the design's in every frame, so the old eye block (design rows 68-71, columns 60-67) is found square for
square in each strip and swapped for the new one; a frame where it is not found (the head turned, the death) keeps
its eyes and is listed. Only the idle carries the design's face square for square; the other actions' faces were
drawn frame by frame, so there each frame's own pink eyes (2-6 squares on the face) get the same restyle: the top
row violet (the bright outward), the rows under it skin, the outer lid corner up; closed eyes (no pink) stay. Run
twice, it finds nothing left to change.
"""
import glob
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NATIVE = os.path.join(ROOT, "assets", "source", "native")
R0, R1, C0, C1 = 68, 72, 60, 68          # the eye block in the design (rows, columns, end exclusive)


def rgb(h):
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


SKIN, LID = rgb("F2D6EA"), rgb("0F0117")
GLOW, DEEP = rgb("C9A6FF"), rgb("8A4FE0")


def new_eyes(d):
    """The design with version A's eyes."""
    d = d.copy()
    d[70, 61], d[70, 62] = GLOW, DEEP            # her right eye (image left): the glow outward
    d[70, 65], d[70, 66] = DEEP, GLOW            # her left eye (image right)
    for c in (61, 62, 65, 66):
        d[71, c] = SKIN
    d[68, 60] = d[69, 60] = LID                  # the outer corners up
    d[68, 66] = LID
    return d


def load1x(path):
    a = np.asarray(Image.open(path).convert("RGBA"))
    return a[::8, ::8].copy()


def save8x(a, path):
    Image.fromarray(np.repeat(np.repeat(a, 8, 0), 8, 1)).save(path)


PINK = np.array((0xC8, 0x3C, 0xA6))
WHITE = (0xF8, 0xF7, 0xF9)


def eyes_in(cell):
    """The pink eyes of one frame: [(y0, y1, x0, x1)] - 4-connected pieces of the eye pink (2-4 squares, a box of
    at most 2 x 2) on skin (the cheek right under them), at most two. Nothing bigger, nothing 8-connected: a piece
    joined diagonally to a pink hair highlight gave a box over the hair, which the restyle painted skin
    (「放技能和平A时脸严重变形」)."""
    op = cell[..., 3] > 0
    core = op & (np.abs(cell[..., :3].astype(int) - PINK).sum(-1) < 60)
    pink = core | (op & (cell[..., :3] == (0xA2, 0x1E, 0x93)).all(-1))
    skin = op & (cell[..., :3] == SKIN[:3]).all(-1)
    seen = np.zeros_like(pink)
    out = []
    for y, x in zip(*np.nonzero(pink)):
        if seen[y, x]:
            continue
        st, piece = [(y, x)], []
        seen[y, x] = True
        while st:
            v, u = st.pop()
            piece.append((v, u))
            for dv, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q, w = v + dv, u + du
                if 0 <= q < pink.shape[0] and 0 <= w < pink.shape[1] and not seen[q, w] and pink[q, w]:
                    seen[q, w] = True
                    st.append((q, w))
        if not (2 <= len(piece) <= 4) or not any(core[v, u] for v, u in piece):
            continue
        ys, xs = zip(*piece)
        y0, y1, x0, x1 = min(ys), max(ys), min(xs), max(xs)
        if y1 - y0 > 1 or x1 - x0 > 1 or y1 + 1 >= skin.shape[0]:
            continue
        below = [skin[y1 + 1, x] for x in range(x0, x1 + 1)]
        if all(below):
            out.append((y0, y1, x0, x1))
    return sorted(out, key=lambda b: b[2])[:2]


def restyle(cell, eyes):
    """Version A on the frame's own eyes, inside their 2 x 2 boxes only: the top row a bright and a deep violet (the
    bright outward), the row under it skin; the lid's outer corner (one skin square diagonally above-outside) dark."""
    mid = sum((b[2] + b[3]) / 2 for b in eyes) / len(eyes)
    for y0, y1, x0, x1 in eyes:
        outer_left = (x0 + x1) / 2 <= mid
        for x in range(x0, x1 + 1):
            cell[y0, x] = DEEP
        cell[y0, x0 if outer_left else x1] = GLOW
        for y in range(y0 + 1, y1 + 1):
            for x in range(x0, x1 + 1):
                cell[y, x] = SKIN
        v, u = y0 - 1, (x0 - 1 if outer_left else x1 + 1)
        if 0 <= v and 0 <= u < cell.shape[1] and (cell[v, u, :3] == SKIN[:3]).all():
            cell[v, u] = LID


def main():
    import json
    global CELLS
    with open(os.path.join(NATIVE, "morgana_cells.json"), encoding="utf-8") as f:
        CELLS = json.load(f)
    dpath = os.path.join(NATIVE, "morgana_native.png")
    des = load1x(dpath)
    old = des[R0:R1, C0:C1].copy()
    new = new_eyes(des)[R0:R1, C0:C1]
    if (old == new).all():
        print("morgana_native.png: the eyes are already version A")
    h, w = old.shape[:2]
    for path in [dpath] + sorted(glob.glob(os.path.join(NATIVE, "morgana_*.png"))):
        if path.endswith("morgana_native.png") and path != dpath:
            continue
        a = load1x(path)
        hits = 0
        # every place the old block sits square for square
        for y in range(a.shape[0] - h + 1):
            row = a[y:y + h]
            for x in range(a.shape[1] - w + 1):
                if a[y, x, 3] == old[0, 0, 3] and (row[:, x:x + w] == old).all():
                    a[y:y + h, x:x + w] = new
                    hits += 1
        tag = os.path.basename(path)[len("morgana_"):-4]
        rest = []
        if path != dpath and tag in CELLS["tags"] and not hits:     # the idle took the design's block
            ncol = a.shape[1] // 96
            for k in range(len(CELLS["tags"][tag])):
                cell = a[(k // ncol) * 96:(k // ncol + 1) * 96, (k % ncol) * 96:(k % ncol + 1) * 96]
                eyes = eyes_in(cell)
                if eyes:
                    restyle(cell, eyes)
                    rest.append(f"{k + 1}:{len(eyes)}")
        if hits or rest:
            save8x(a, path)
        print(f"{os.path.basename(path)}: {hits} design eye block(s), frame by frame " + (" ".join(rest) or "-"))
        if path == dpath:
            continue


if __name__ == "__main__":
    main()
