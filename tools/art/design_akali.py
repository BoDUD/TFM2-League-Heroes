#!/usr/bin/env python3
"""Rebuild Akali's approved design (the user's pick "B大眼", 2026-09-30) from Codex's step-1 drawing, byte for byte.

    python tools/art/design_akali.py [--out assets/source/native/akali_native.png] [--check]

Codex redrew the user's picture at 80 squares from the crown to the soles on an exact 8x grid, 29 colours
(assets/source/akali/codex_model/design_akali_B_1x.png). Steps:
1. Shrink to 46 rows crown to soles (55 with the ponytail) by deleting whole rows and columns, no pixel mixed: the rows
   are split into as many groups as the target has, in each group the rows most like the nearest row still kept go
   first (comparing with the original neighbours let two identical eye rows delete each other), nine offsets of the
   grouping tried, the one losing least kept; eye pixels count 12 times. Then the outline ring is completed outside.
2. tidy_codex18.one_outline (one outline ring, the second black ring turned into the material's dark shade), then
   Codex's camouflage specks merged: majority passes inside each colour family (greens, darks, creams) and blobs of
   at most two pixels taking the colour of the family round them.
3. The eyes: the shrink keeps the liner row and one row of eye; the skin row under it becomes the second eye row (a
   lash row over two rows of eye, as the base game's masked ninja has).
4. Hand edits (the user's pick was cleaned before approval): the top as one green piece with a dark-green wrap line
   and hem, the midriff, the hips as dark trousers with the cream sash tail, the loincloth as one green panel with a
   pale spiral and a gold tip.
The result sits on a 128x128 canvas at 8x with the soles on row 99 and the feet's middle on column 64.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tidy_codex18 as TC  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "akali", "codex_model", "design_akali_B_1x.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "akali_native.png")
CROWN, SOLES = 32, 111          # Codex's canvas: crown and soles rows (80 rows)
ROWS = 46                       # crown to soles at game size
EYE_W = 12
WHITE, IRIS = (0xFF, 0xF7, 0xE5), (0x6A, 0x38, 0x23)
SKIN = [(0xDD, 0xA3, 0x72), (0xF4, 0xBF, 0x8B)]
FAMILIES = {
    "green": [(0x22, 0x3A, 0x35), (0x35, 0x52, 0x47), (0x4C, 0x65, 0x4B), (0x68, 0x7C, 0x47), (0x84, 0x94, 0x5C)],
    "dark": [(0x23, 0x26, 0x32), (0x37, 0x34, 0x40), (0x34, 0x36, 0x46), (0x40, 0x49, 0x56), (0x48, 0x49, 0x56),
             (0x51, 0x48, 0x56), (0x5B, 0x5C, 0x66)],
    "cream": [(0xDE, 0xD0, 0xB1), (0xC1, 0xB4, 0x96), (0xA2, 0x97, 0x7D)],
}
N8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
CODE = {"#": "11131D", "a": "232632", "c": "373440", "h": "343646", "H": "404956", "b": "484956", "n": "514856",
        "s": "5B5C66", "t": "657183", "m": "223A35", "g": "355247", "f": "4C654B", "e": "687C47", "E": "84945C",
        "i": "DDA372", "j": "F4BF8B", "k": "BD8157", "W": "FFF7E5", "L": "6A3823", "w": "DED0B1", "v": "C1B496",
        "u": "A2977D", "Y": "CCAA5B", "y": "A48142", "z": "72552E", "S": "97A7B6", "T": "C9D5DD"}
EDITS = [   # (row, first column, codes) on the 45x55 figure
    (22, 21, "mmmmm"), (23, 19, "eeeffm"), (24, 19, "emeeeee"), (25, 19, "meeeeef"), (26, 18, "meeeeffg"),
    (27, 18, "mfffggmm"), (28, 19, "mmmmmmm"), (29, 19, "ajjjjja"),
    (34, 15, "ccaaafeeegcc"), (35, 15, "caaaafeeegcc"), (36, 15, "ccwwafeeegcc"), (37, 15, "ccwwafeeegccc"),
    (38, 14, "cccwwafeEegccaaa"), (39, 14, "cccwwafeEEgccca"), (40, 13, "ccccvvaafeEEgccc"),
    (41, 12, "cccccaaaafeEeEgcc"), (42, 12, "ccccccaa##feEEegcc"), (43, 23, "feg"), (44, 23, "feg"), (45, 23, "feg"),
    (46, 23, "Yy"),
]


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# ------------------------------------------------------------------------------------------------ 1 shrink
def palette(a):
    op = a[..., 3] > 0
    cols = np.unique(a[op][:, :3], axis=0)
    idx = np.full(a.shape[:2], -1, int)
    for k, c in enumerate(cols):
        idx[op & (a[..., :3] == c).all(-1)] = k
    return cols, idx


def outline_colour(idx):
    H, W = idx.shape
    edge = []
    for y in range(H):
        for x in range(W):
            if idx[y, x] >= 0 and any(not (0 <= yy < H and 0 <= xx < W) or idx[yy, xx] < 0
                                      for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))):
                edge.append(idx[y, x])
    return int(np.bincount(edge).argmax())


def pick(lines, weights, n_out, offset):
    n = len(lines)
    edges = [min(n, max(0, int(round(i * n / n_out)) + (offset if 0 < i < n_out else 0))) for i in range(n_out + 1)]
    alive = [True] * n
    keep, lost = [], 0
    for g in range(n_out):
        idxs = list(range(edges[g], edges[g + 1]))
        if not idxs:
            return None, 1e18
        while len(idxs) > 1:
            best = None
            for i in idxs:
                nb = []
                for step in (-1, 1):
                    j = i + step
                    while 0 <= j < n and not alive[j]:
                        j += step
                    if 0 <= j < n:
                        nb.append(j)
                d = min(int(((lines[i] != lines[j]) * np.maximum(weights[i], weights[j])).sum()) for j in nb)
                if best is None or d < best[0]:
                    best = (d, i)
            lost += best[0]
            idxs.remove(best[1])
            alive[best[1]] = False
        keep.append(idxs[0])
    return keep, lost


def seam_shrink(idx, wmap, th, tw):
    best = None
    for oy in range(3):
        rows, lost_r = pick([idx[y] for y in range(idx.shape[0])], [wmap[y] for y in range(idx.shape[0])], th, oy)
        if rows is None:
            continue
        sub, subw = idx[rows], wmap[rows]
        for ox in range(3):
            cols, lost_c = pick([sub[:, x] for x in range(sub.shape[1])], [subw[:, x] for x in range(sub.shape[1])], tw, ox)
            if cols is None:
                continue
            if best is None or lost_r + lost_c < best[0]:
                best = (lost_r + lost_c, sub[:, cols])
    return best[1]


def outline_out(idx, line):
    H, W = idx.shape
    res = idx.copy()
    for y in range(H):
        for x in range(W):
            if idx[y, x] >= 0:
                continue
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < H and 0 <= xx < W and idx[yy, xx] >= 0 and idx[yy, xx] != line:
                    res[y, x] = line
                    break
    return res


def shrink(src):
    cols, idx = palette(src)
    line = outline_colour(idx)
    ys, xs = np.nonzero(idx >= 0)
    idx = idx[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    eye_k = [k for k, c in enumerate(cols) if tuple(int(v) for v in c) in (WHITE, IRIS)]
    wmap = np.where(np.isin(idx, eye_k), EYE_W, 1)
    scale = ROWS / (SOLES - CROWN + 1)
    small = seam_shrink(idx, wmap, round(idx.shape[0] * scale), round(idx.shape[1] * scale))
    small = outline_out(np.pad(small, 1, constant_values=-1), line)
    out = np.zeros(small.shape + (4,), np.uint8)
    op = small >= 0
    out[op, :3] = cols[small[op]]
    out[op, 3] = 255
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


# ------------------------------------------------------------------------------------------------ 2-4 tidy
def flatten(a, keep, passes=3, need=5):
    fam = {c: f for f, cs in FAMILIES.items() for c in cs}
    H, W = a.shape[:2]
    for _ in range(passes):
        out = a.copy()
        for y in range(1, H - 1):
            for x in range(1, W - 1):
                if a[y, x, 3] == 0 or keep[y, x]:
                    continue
                me = tuple(int(v) for v in a[y, x, :3])
                if me not in fam:
                    continue
                nb = [tuple(int(v) for v in a[y + dy, x + dx, :3]) for dy, dx in N8 if a[y + dy, x + dx, 3] > 0]
                cand = [c for c in set(nb) if c != me and fam.get(c) == fam[me]]
                if not cand:
                    continue
                best = max(cand, key=nb.count)
                if nb.count(best) >= need and nb.count(best) > nb.count(me):
                    out[y, x, :3] = best
        a = out
    return a


def small_blobs(a, keep, most=2):
    fam = {c: f for f, cs in FAMILIES.items() for c in cs}
    H, W = a.shape[:2]
    col = lambda y, x: tuple(int(v) for v in a[y, x, :3]) if a[y, x, 3] > 0 else None  # noqa: E731
    seen = np.zeros((H, W), bool)
    out = a.copy()
    for y in range(H):
        for x in range(W):
            c = col(y, x)
            if seen[y, x] or c is None or c not in fam or keep[y, x]:
                continue
            blob, stack = [], [(y, x)]
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                blob.append((cy, cx))
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and not seen[ny, nx] and col(ny, nx) == c:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            if len(blob) > most or any(keep[p] for p in blob):
                continue
            nb = []
            for cy, cx in blob:
                for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and (ny, nx) not in blob:
                        nb.append(col(ny, nx))
            cand = [n for n in nb if n in fam]
            if not cand or None in nb:
                continue
            best = max(set(cand), key=cand.count)
            if cand.count(best) * 2 >= len(nb):
                for p in blob:
                    out[p][:3] = best
    return out


def base_eyes(a):
    a = a.copy()
    for y, x in [(y, x) for y in range(a.shape[0]) for x in range(a.shape[1])
                 if a[y, x, 3] and tuple(int(v) for v in a[y, x, :3]) in (WHITE, IRIS)]:
        below = a[y + 1, x]
        if below[3] > 0 and tuple(int(v) for v in below[:3]) in SKIN:
            a[y + 1, x] = a[y, x]
    return a


def edits(a):
    a = a.copy()
    for y, x0, codes in EDITS:
        for k, ch in enumerate(codes):
            h = CODE[ch]
            a[y, x0 + k] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return a


def build():
    src = np.asarray(Image.open(lp(SRC)).convert("RGBA"))
    a = TC.one_outline(shrink(src), colours=[WHITE, IRIS])
    keep = TC.protected(a, [WHITE, IRIS])
    a = small_blobs(small_blobs(TC.despeckle(flatten(a, keep), keep), keep), keep)
    fig = edits(base_eyes(a))
    ys, xs = np.nonzero(fig[..., 3] > 0)
    fig = fig[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    soles = np.nonzero(fig[-1, :, 3] > 0)[0]
    fx = (soles.min() + soles.max() + 1) // 2
    canvas = np.zeros((128, 128, 4), np.uint8)
    x0, y0 = 64 - fx, 100 - fig.shape[0]
    m = fig[..., 3] > 0
    canvas[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]][m] = fig[m]
    return canvas, fig


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true", help="compare with the committed design instead of writing it")
    a = ap.parse_args()
    canvas, fig = build()
    big = Image.fromarray(np.repeat(np.repeat(canvas, 8, 0), 8, 1))
    if a.check:
        old = np.asarray(Image.open(lp(a.out)).convert("RGBA"))
        same = old.shape == np.asarray(big).shape and (old == np.asarray(big)).all()
        print("identical" if same else "DIFFERENT", a.out)
        sys.exit(0 if same else 1)
    big.save(lp(a.out))
    op = fig[..., 3] > 0
    print(f"{a.out}: {fig.shape[1]}x{fig.shape[0]}, {len(np.unique(fig[op][:, :3], axis=0))} colours, {int(op.sum())} px")


if __name__ == "__main__":
    main()
