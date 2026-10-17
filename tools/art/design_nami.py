#!/usr/bin/env python3
"""Nami's design (assets/source/native/nami_native.png) from Codex's game-size drawing, step by step.

    python tools/art/design_nami.py [--check]

The drawing is Codex's third round A (assets/source/nami/codex_model/nami_design_A_1x.png, 128x128 at one pixel a
square; its prompt in assets/source/nami/MODEL_PROMPTS.md): drawn at game size from the user's picture and read
back on its own grid by Codex, 42x64 squares, 20 colours. Round 1 had been drawn at ~1.7x and every shrink of it
blurred ("主要是要不模糊细节好"); so nothing here mixes pixels:
  1. the face (the user: "怎么方形的脸？", picked D of four options): the flat 8x7 rectangle becomes an oval - a lock of
     hair down the near cheek from row 48, the far cheek running down to a pointed chin, a shaded row under it; the
     eyes 2x2 with a white catch-light top left and amber elsewhere (league_morgana's approved eyes; the amber
     #F2B233 only there), lashes over each, one dark-red mouth square on the middle line; the far cheek and the
     forehead under the fringe in the skin's shadow;
  2. the size (the user: "体型还是太大 能不能尽量和别的英雄一个尺寸", picked W): whole rows and columns deleted to 50
     rows (the seam shrink of the 18 redraws: in each group the line most like its neighbour goes, nine offsets,
     the least loss kept), never the face's rows and columns or the staff's shaft column -> 36x50, league_janna's area;
  3. the fin's pale parts from the skin's #DDEBD0 to the picture's pale yellow-green #E8E6A8;
  4. on the 128x128 canvas at 8x: the lowest pixel on row 96, three above the soles row 99 (she floats like
     league_janna), the belt's middle on column 64.
--check compares the result with the committed nami_native.png instead of writing it.
"""
import argparse
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DRAWING = os.path.join(ROOT, "assets", "source", "nami", "codex_model", "nami_design_A_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "nami_native.png")
ROWS = 48                          # the target; the protected face rows keep 2 more (50)
FACE_ROWS = range(43, 53)          # in the drawing: the fringe to the chin's shade
FACE_COLS = range(55, 68)          # the fin-ear to the far cheek
STAFF_COL = 75                     # the staff's one-square shaft
FLOAT, SOLE_ROW = 3, 99

C = {"OL": "0E0B14", "H1": "F08A3C", "H2": "CB552B", "H3": "93321F", "S1": "DDEBD0", "S2": "B5D1BC",
     "WH": "F2FDFD", "AM": "F2B233", "MO": "9C3F46", "FIN": "E8E6A8", "..": None}
FACE_D = {  # (x, y) in the drawing: colour
    # oval: the near cheek behind a lock from row 48, the far cheek down to a pointed chin at x 61-62
    (58, 48): "H2",
    (58, 49): "H2", (59, 49): "S2", (65, 49): "OL", (66, 49): "..",
    (58, 50): "H2", (59, 50): "H3", (60, 50): "S2", (61, 50): "S1", (62, 50): "MO", (63, 50): "S1",
    (64, 50): "OL", (65, 50): "..", (66, 50): "..",
    (58, 51): "H2", (59, 51): "H3", (60, 51): "OL", (61, 51): "S1", (62, 51): "S2", (63, 51): "OL",
    (64, 51): "H1", (65, 51): "OL",
    (61, 52): "S2", (62, 52): "S2", (63, 52): "S2",
    # eyes: catch-light top left, amber elsewhere
    (59, 46): "WH", (60, 46): "AM", (59, 47): "AM", (60, 47): "AM",
    (63, 46): "WH", (64, 46): "AM", (63, 47): "AM", (64, 47): "AM",
    # shade: the far cheek and the forehead under the fringe
    (65, 45): "S2", (65, 46): "S2", (65, 47): "S2", (65, 48): "S2", (64, 49): "S2",
    (61, 44): "S2", (62, 44): "S2", (63, 44): "S2",
}


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ----------------------------------------------------------------------------- 1. the face
def face(a):
    a = a.copy()
    for (x, y), c in FACE_D.items():
        if C[c] is None:
            a[y, x] = 0
        else:
            a[y, x, :3] = hexc(C[c])
            a[y, x, 3] = 255
    return a


# ----------------------------------------------------------------------------- 2. the size
def to_index(a):
    op = a[..., 3] > 0
    pal = sorted({tuple(int(v) for v in p[:3]) for p in a[op]})
    lut = {c: i for i, c in enumerate(pal)}
    idx = np.full(a.shape[:2], -1, int)
    for y, x in zip(*np.nonzero(op)):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]
    return np.array(pal), idx


def render(idx, pal):
    img = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    img[m, :3] = pal[idx[m]]
    img[m, 3] = 255
    return img


def pick(lines, n_out, offset, protect):
    n = len(lines)
    edges = [min(n, max(0, int(round(i * n / n_out)) + (offset if 0 < i < n_out else 0))) for i in range(n_out + 1)]
    keep, lost = [], 0
    for g in range(n_out):
        idxs = list(range(edges[g], edges[g + 1]))
        if not idxs:
            return None, 1e9
        while len(idxs) > 1:
            cand = [i for i in idxs if i not in protect]
            if not cand:
                break
            best = None
            for i in cand:
                d = min(int((lines[i] != lines[j]).sum()) for j in (i - 1, i + 1) if 0 <= j < n)
                if best is None or d < best[0]:
                    best = (d, i)
            lost += best[0]
            idxs.remove(best[1])
        keep.extend(idxs)
    return keep, lost


def shrink(a, rows):
    pal, idx = to_index(a)
    ys, xs = np.nonzero(idx >= 0)
    y0, x0 = ys.min(), xs.min()
    idx = idx[y0:ys.max() + 1, x0:xs.max() + 1]
    scale = rows / idx.shape[0]
    tw = int(round(idx.shape[1] * (1 - (1 - scale) * 0.8)))   # a little less narrowing than lengthwise
    prow = {y - y0 for y in FACE_ROWS}
    pcol = {x - x0 for x in FACE_COLS} | {STAFF_COL - x0}
    best = None
    for oy in range(3):
        rws, lr = pick([idx[y] for y in range(idx.shape[0])], rows, oy, prow)
        if rws is None:
            continue
        sub = idx[rws]
        for ox in range(3):
            cls, lc = pick([sub[:, x] for x in range(sub.shape[1])], tw, ox, pcol)
            if cls is None:
                continue
            if best is None or lr + lc < best[0]:
                best = (lr + lc, sub[:, cls])
    return render(best[1], pal)


# ----------------------------------------------------------------------------- 3. the fin
FIN_TOP = 33      # in the shrunk figure: the fan fin starts on row 33 (the open hand ends on row 29)
BELT_ROWS = range(25, 28)


def fin(a):
    """Skin-coloured squares of the tail's fan fin (rows FIN_TOP down) -> the picture's pale yellow-green."""
    a = a.copy()
    m = (a[..., :3] == hexc(C["S1"])).all(-1) & (a[..., 3] > 0)
    m[:FIN_TOP] = False
    a[m, :3] = hexc(C["FIN"])
    return a


# ----------------------------------------------------------------------------- 4. the canvas
def place(a):
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    gold = np.zeros(a.shape[:2], bool)
    for h in ("F6D57F", "D3A04A"):
        gold |= (a[..., :3] == hexc(h)).all(-1) & (a[..., 3] > 0)
    H, W = a.shape[:2]
    belt = [x for x in range(W) if gold[BELT_ROWS.start:BELT_ROWS.stop, x].any() and x < W * 3 // 4]
    mid = (belt[0] + belt[-1]) / 2
    canvas = np.zeros((128, 128, 4), np.uint8)
    bottom = SOLE_ROW + 1 - FLOAT
    x0 = int(round(64 - mid))
    canvas[bottom - H:bottom, x0:x0 + W] = a
    return Image.fromarray(canvas).resize((1024, 1024), Image.NEAREST)


def design():
    src = np.asarray(Image.open(lp(DRAWING)).convert("RGBA"))
    return place(fin(shrink(face(src), ROWS)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    img = design()
    if args.check:
        old = np.asarray(Image.open(lp(OUT)).convert("RGBA"))
        new = np.asarray(img)
        print("identical" if old.shape == new.shape and (old == new).all() else
              f"differs: {int(np.any(old != new, -1).sum())} px")
        return
    img.save(lp(OUT))
    a = np.asarray(img)[::8, ::8]
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    print(f"{OUT}: {xs.max() - xs.min() + 1}x{ys.max() - ys.min() + 1}, rows {ys.min()}-{ys.max()}, "
          f"cols {xs.min()}-{xs.max()}, {len({tuple(c) for c in a[op][:, :3]})} colours")


if __name__ == "__main__":
    main()
