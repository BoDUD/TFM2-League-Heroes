#!/usr/bin/env python3
"""Riven's design (assets/source/native/riven_native.png) from the user's picture, step by step.

    python tools/art/design_riven.py [--check]

The picture (assets/source/riven/codex_model/design_riven_A_generated.png: Codex's small Riven A, which the user
chose and handed over) is pixel art at about 10 source pixels a square, 50 squares from the tuft to the soles.
The route is the one the Ahri session found for the 18 redraws (a straight 3x shrink, colour voting or area
averaging turn the face to mush):
  1. regrid: square borders from the colour changes (peaks of the count of figure rows / columns whose colour
     changes there, at least 0.6 of a square apart, gaps over 1.6 squares split evenly); each square takes the
     median colour of the 3x3 source pixels at its middle, opaque when most of them are -> 50x48;
  2. palette: 24 colours, k-means in Lab over the unique colours weighted by the square root of their counts
     (small distinct features keep a colour of their own), each cluster shown by its commonest real colour;
  3. shrink to 46 rows by deleting whole rows and columns, never mixing pixels: the rows are cut into as many
     groups as the target has, and in each group the rows most like their neighbour go until one is left
     (columns the same, width in proportion); nine offsets of the grouping, the least loss kept; then the
     outline ring completed outside (an empty pixel beside a coloured non-outline one);
  4. one outline (tools/art/tidy_codex18.py's one_outline): outline spurs off, the black just inside the
     outline turned into the material's own darkest shade, lone specks inside an area taken by the area, the
     face left alone;
  5. the eyes, the user's version 1 (2026-09-30): both 2x2 on one row with two skin columns between and a
     cheek column before - lashes over each, a white catch-light and dark green on top, green below, in three
     colours (#FFFFFF, #163A22, #3E8E48) used nowhere else; no mouth;
  7. the size (the user, after seeing her in game: 46 rows stood a head over Garen's 37): 40 rows, the user's pick
     of 40 / 42 - rows and columns deleted as in step 3 but never through the face, which stays square for square,
     then step 4's outline pass again;
  6. on the 128x128 canvas, soles on row 99, the middle of the feet on column 64, shown at 8x.
--check compares the result with the committed riven_native.png instead of writing it.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PICTURE = os.path.join(ROOT, "assets", "source", "riven", "codex_model", "design_riven_A_generated.png")
OUT = os.path.join(ROOT, "assets", "source", "native", "riven_native.png")
HEIGHT, K = 46, 24
SMALL = 40                      # step 7: the height the user picked for the game
FACE_ROWS = range(12, 17)       # the 46-row design's lashes, eyes and cheeks (rows from its top) ...
FACE_COLS = range(11, 20)       # ... and its cheek, eyes, skin between and the cheek beyond (columns)
DARK = 40
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def lp(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


# ----------------------------------------------------------------------------- 1. regrid
def profile(a, op, axis):
    d = np.abs(np.diff(a[..., :3].astype(int), axis=axis)).max(axis=2) > 36
    if axis == 1:
        both = op[:, 1:] | op[:, :-1]
        return np.concatenate([[0], (d & both).sum(axis=0)]).astype(float)
    both = op[1:] | op[:-1]
    return np.concatenate([[0], (d & both).sum(axis=1)]).astype(float)


def boundaries(e, lo, hi, size):
    cand = [x for x in range(lo + 1, hi) if e[x] > 0 and e[x] >= e[x - 1] and e[x] >= e[x + 1]]
    cand.sort(key=lambda x: -e[x])
    picked = []
    for x in cand:
        if all(abs(x - p) >= 0.6 * size for p in picked) and e[x] >= 0.15 * e.max():
            picked.append(x)
    picked = sorted(set(picked + [lo, hi + 1]))
    out = [picked[0]]
    for b in picked[1:]:
        gap = b - out[-1]
        n = int(round(gap / size))
        if n >= 2 and gap > 1.6 * size:
            start = out[-1]
            for k in range(1, n):
                out.append(int(round(start + gap * k / n)))
        out.append(b)
    return out


def regrid(a):
    op = a[..., 3] >= 128
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    ex, ey = profile(a, op, 1), profile(a, op, 0)
    pk = [x for x in range(x0 + 1, x1) if ex[x] > 0.3 * ex.max() and ex[x] >= ex[x - 1] and ex[x] >= ex[x + 1]]
    d = np.diff(pk)
    d = d[(d >= 6) & (d <= 24)]
    size = float(np.median(d)) if len(d) else 12.0
    bx, by = boundaries(ex, x0, x1, size), boundaries(ey, y0, y1, size)
    out = np.zeros((len(by) - 1, len(bx) - 1, 4), np.uint8)
    for j in range(len(by) - 1):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(len(bx) - 1):
            cx = (bx[i] + bx[i + 1]) // 2
            win = a[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            if (win[:, 3] >= 128).sum() * 2 > len(win):
                out[j, i, :3] = np.median(win[win[:, 3] >= 128][:, :3], axis=0).astype(np.uint8)
                out[j, i, 3] = 255
    ys, xs = np.nonzero(out[..., 3] > 0)
    return out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


# ----------------------------------------------------------------------------- 2. palette
def to_lab(rgb):
    c = rgb.astype(float) / 255.0
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = c @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def palette(img, k, seed=0):
    op = img[..., 3] > 0
    px = img[op][:, :3]
    uniq, inv, cnt = np.unique(px, axis=0, return_inverse=True, return_counts=True)
    lab = to_lab(uniq)
    w = np.sqrt(cnt)
    rng = np.random.default_rng(seed)
    cent = [lab[np.argmax(cnt)]]
    for _ in range(k - 1):
        d = np.min([((lab - c) ** 2).sum(1) for c in cent], axis=0) * w
        cent.append(lab[rng.choice(len(lab), p=d / d.sum())])
    cent = np.array(cent)
    for _ in range(30):
        lbl = np.argmin(((lab[:, None] - cent[None]) ** 2).sum(-1), axis=1)
        for j in range(k):
            m = lbl == j
            if m.any():
                cent[j] = (lab[m] * w[m, None]).sum(0) / w[m].sum()
    lbl = np.argmin(((lab[:, None] - cent[None]) ** 2).sum(-1), axis=1)
    pal = np.zeros((k, 3), int)
    for j in range(k):
        m = np.nonzero(lbl == j)[0]
        pal[j] = uniq[m[np.argmax(cnt[m])]] if len(m) else 0
    idx = np.full(img.shape[:2], -1, int)
    idx[op] = lbl[inv.ravel()]
    return pal, idx


def outline_colour(pal, idx):
    op = idx >= 0
    pad = np.pad(op, 1)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    vals, cnt = np.unique(idx[edge], return_counts=True)
    lum = pal[vals].sum(1)
    dark = vals[lum < np.percentile(pal.sum(1), 30) + 1]
    best = [v for v in vals[np.argsort(-cnt)] if v in dark]
    return best[0] if best else vals[np.argmax(cnt)]


# ----------------------------------------------------------------------------- 3. shrink by deleting lines
def pick(lines, n_out, offset):
    n = len(lines)
    edges = [min(n, max(0, int(round(i * n / n_out)) + (offset if 0 < i < n_out else 0))) for i in range(n_out + 1)]
    keep, lost = [], 0
    for g in range(n_out):
        idxs = list(range(edges[g], edges[g + 1]))
        if not idxs:
            return None, 1e9
        while len(idxs) > 1:
            best = None
            for i in idxs:
                d = min(int((lines[i] != lines[j]).sum()) for j in (i - 1, i + 1) if 0 <= j < n)
                if best is None or d < best[0]:
                    best = (d, i)
            lost += best[0]
            idxs.remove(best[1])
        keep.append(idxs[0])
    return keep, lost


def seam_shrink(idx, th, tw):
    best = None
    for oy in range(3):
        rows, lost_r = pick([idx[y] for y in range(idx.shape[0])], th, oy)
        if rows is None:
            continue
        sub = idx[rows]
        for ox in range(3):
            cols, lost_c = pick([sub[:, x] for x in range(sub.shape[1])], tw, ox)
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


def render(idx, pal):
    img = np.zeros(idx.shape + (4,), np.uint8)
    m = idx >= 0
    img[m, :3] = pal[idx[m]]
    img[m, 3] = 255
    ys, xs = np.nonzero(img[..., 3] > 0)
    return img[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


# ----------------------------------------------------------------------------- 4. one outline
def lum(rgb):
    rgb = rgb.astype(float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def shifted(m, dy, dx):
    out = np.zeros_like(m)
    H, W = m.shape
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = m[ys, xs]
    return out


def one_outline(a, keep):
    a = a.copy()
    for _ in range(2):
        op = a[..., 3] > 0
        cnt = sum(shifted(op, dy, dx).astype(int) for dy, dx in N4)
        a[op & (lum(a[..., :3]) < DARK) & (cnt <= 1) & ~keep] = 0
    op = a[..., 3] > 0
    L = lum(a[..., :3])
    edge = np.zeros_like(op)
    for dy, dx in N4:
        edge |= op & ~shifted(op, dy, dx)
    ring2 = np.zeros_like(op)
    for dy, dx in N4:
        ring2 |= shifted(edge, dy, dx)
    ring2 &= op & ~edge & (L < DARK) & ~keep
    H, W = op.shape
    out = a.copy()
    for y, x in zip(*np.nonzero(ring2)):
        cols = [tuple(int(v) for v in a[y + dy, x + dx]) for dy, dx in N8
                if 0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and L[y + dy, x + dx] >= DARK]
        if len(cols) >= 2:
            out[y, x] = min(cols, key=lambda c: (lum(np.array(c[:3])), -cols.count(c)))
    op = out[..., 3] > 0
    res = out.copy()
    for y in range(1, H - 1):
        for x in range(1, W - 1):
            if not op[y, x] or keep[y, x]:
                continue
            nb = [tuple(int(v) for v in out[y + dy, x + dx]) for dy, dx in N4]
            me = tuple(int(v) for v in out[y, x])
            if me in nb or any(n[3] == 0 for n in nb):
                continue
            best = max(set(nb), key=nb.count)
            if nb.count(best) >= 3:
                res[y, x] = best
    return res


# ----------------------------------------------------------------------------- 5. the eyes
def hexc(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def eyes(a):
    """Version 1: cheek col 12, near eye 13-14, skin 15-16, far eye 17-18; lashes row 13, eyes rows 14-15."""
    skin, shade, lash = hexc("FBC697"), hexc("E39F6B"), hexc("1C0903")
    hi, dark, iris = hexc("FFFFFF"), hexc("163A22"), hexc("3E8E48")

    def put(x, y, c):
        a[y, x, :3] = c
        a[y, x, 3] = 255
    for x in (13, 14, 17, 18):
        put(x, 13, lash)
    for x in (15, 16):
        for y in (13, 14, 15):
            put(x, y, skin)
    put(12, 14, shade)
    put(12, 15, skin)
    for x0 in (13, 17):
        put(x0, 14, hi)
        put(x0 + 1, 14, dark)
        put(x0, 15, iris)
        put(x0 + 1, 15, iris)
    return a


# ----------------------------------------------------------------------------- 7. the size the user picked
def keep_axis(lines, target, protect):
    """Which lines stay: the protected run whole, the deletions shared in proportion by the parts before and after
    it, each part shrunk by pick() at the offset that loses least."""
    n = len(lines)
    lo, hi = min(protect), max(protect) + 1
    parts = [list(range(0, lo)), list(range(hi, n))]
    drop = n - target
    q0 = round(drop * len(parts[0]) / (len(parts[0]) + len(parts[1])))
    kept = []
    for part, q in zip(parts, (q0, drop - q0)):
        sub = [lines[i] for i in part]
        best = None
        for off in range(3):
            k, lost = pick(sub, len(part) - q, off)
            if k is not None and (best is None or lost < best[1]):
                best = (k, lost)
        kept.append([part[i] for i in best[0]])
    return kept[0] + list(range(lo, hi)) + kept[1]


def smaller(a):
    """46 rows looked too big beside the other heroes (the user, 2026-09-30: "锐雯的整体体型在游戏里做的有点大了吧";
    Garen 37, Ahri 38, Darius 42); the user picked SMALL rows. Whole rows and columns are deleted as in step 3,
    never the face's (rows FACE_ROWS, columns FACE_COLS of the 46-row design stay whole), width in proportion, then
    the outline pass again with the face kept."""
    H, W = a.shape[:2]
    cols = sorted({tuple(int(v) for v in p[:3]) for p in a[a[..., 3] > 0]})
    lut = {c: i for i, c in enumerate(cols)}
    idx = np.full((H, W), -1, int)
    op = a[..., 3] > 0
    for y, x in zip(*np.nonzero(op)):
        idx[y, x] = lut[tuple(int(v) for v in a[y, x, :3])]
    rows = keep_axis([idx[y] for y in range(H)], SMALL, FACE_ROWS)
    sub = idx[rows]
    keep_cols = keep_axis([sub[:, x] for x in range(W)], round(W * SMALL / H), FACE_COLS)
    small = idx[np.ix_(rows, keep_cols)]
    pal = np.array(cols, np.uint8)
    out = np.zeros(small.shape + (4,), np.uint8)
    m = small >= 0
    out[m, :3] = pal[small[m]]
    out[m, 3] = 255
    keep = np.zeros(m.shape, bool)
    fr = [rows.index(r) for r in FACE_ROWS]
    fc = [keep_cols.index(c) for c in FACE_COLS]
    keep[fr[0]:fr[-1] + 1, fc[0]:fc[-1] + 1] = True
    return one_outline(out, keep)


def design():
    src = np.asarray(Image.open(lp(PICTURE)).convert("RGBA"))
    grid = regrid(src)
    pal, idx = palette(grid, K)
    line = outline_colour(pal, idx)
    ys, xs = np.nonzero(idx >= 0)
    idx = idx[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    th = HEIGHT
    tw = max(1, round(idx.shape[1] * th / idx.shape[0]))
    small = outline_out(np.pad(seam_shrink(idx, th, tw), 1, constant_values=-1), line)
    a = render(small, pal)
    keep = np.zeros(a.shape[:2], bool)
    keep[12:18, 11:21] = True                 # the face (x 11-20, y 12-17) is left to step 5
    a = eyes(one_outline(a, keep))
    ys, xs = np.nonzero(a[..., 3] > 0)
    a = smaller(a[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    H, W = a.shape[:2]
    feet = [x for x in range(W) if (a[H - 3:, x, 3] > 0).any() and x < W * 2 // 3]
    x0 = int(round(64 - (feet[0] + feet[-1]) / 2))
    canvas = np.zeros((128, 128, 4), np.uint8)
    canvas[100 - H:100, x0:x0 + W] = a
    return Image.fromarray(canvas).resize((1024, 1024), Image.NEAREST)


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
          f"{len({tuple(c) for c in a[op][:, :3]})} colours")


if __name__ == "__main__":
    main()
