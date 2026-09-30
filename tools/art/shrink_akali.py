#!/usr/bin/env python3
"""Akali at 40 rows: the approved 47-row design and Codex's strips with whole rows and columns deleted, never the face.

    python tools/art/shrink_akali.py [--check] [--review DIR]

The user saw Riven (46 rows) and Vayne (48) stand a head over the others in game and had both cut to 40; Akali stood at
47 (the ponytail's tip to the soles, 43 from the crown) and the user asked for 40 as well ("阿卡丽缩小一点吧 40行").
Sources, at the approved size: assets/source/akali/native47/akali_native.png (the design, tools/art/design_akali.py)
and akali_<tag>.png (Codex's strips v3 with the hand fix, 8x, in the cells and pivots of
assets/source/native/akali_cells.json). Nothing is redrawn or resampled: every kept pixel is the source's.
1. The design: 7 rows and 6 columns go, found by dynamic programming (design_akali.dp_keep: never two neighbours, a
   deleted line costing its difference from the nearer neighbour, eyes weighing 12, steel 6, gold 4) with the face
   (rows 9-15: the brow, the liner, both eye rows and the mask's two rows; columns 18-25), the ponytail's top (rows 0-5)
   and the feet (rows 41-46) kept: rows 6, 8 (the hair over the brow), 16, 18, 20 (shoulders, chest), 32, 39 (the
   trousers); columns 0, 5, 11 (the ponytail), 27 (the hair's edge), 29, 31 (by the kama arm). 31x40, 36 from the crown.
2. Every strip frame: the design's head (HEAD_BOX, the block Codex pasted in every frame, its eyes left out of the
   search because the hit and death frames close them) is found in it, and the rows and columns the design loses
   inside that box go, so the face is the design's in every frame. The rest by zones round the head, with as many
   deletions as the design has there for its length: below the head down to the ankles 5 of 25 rows, preferring the
   design's rows (the shoulders under the face, the trousers over the soles); the feet (6 rows over the soles) kept;
   left of the head 3 of the first 12 columns, right of it 2 of the first 9; and 16% of anything reaching further
   (the kama thrown out, the lunges, a blade over the head) - each zone by the same dynamic programming.
3. The outline put back where a deleted line held it (a pixel whose outline neighbour went gets one on the new
   edge), never under the soles. Each frame stays on its pivot, the soles 11 rows under it.
Writes assets/source/native/akali_native.png and akali_<tag>.png (8x, the cells and pivots unchanged); then run
tools/art/import_native.py --hero akali. --check compares with the committed files instead of writing.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_akali as D  # noqa: E402
from import_native import blocks  # noqa: E402
from native_refs import Z, layout  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "akali", "native47")
OUT = os.path.join(ROOT, "assets", "source", "native")
CELLS = os.path.join(OUT, "akali_cells.json")
HEIGHT = 40
KEEP_ROWS = set(range(0, 6)) | set(range(9, 16)) | set(range(41, 47))   # the design's: ponytail top, face, feet
KEEP_COLS = set(range(18, 26))                                           # the liner and both eyes
HEAD_BOX = (12, 3, 27, 15)       # x0, y0, x1, y1 on the 47-row design: the head Codex pasted (no ponytail)
EYE_BOX = (18, 11, 25, 13)       # the liner and the eyes: left out of the search (closed when hit or dying)
FOUND = 0.8                      # share of the head's pixels that must match
# frames whose head Codex drew anew (thrown back when hit or dying, lying on its side at the end): their face's box
# (x0, y0, x1, y1 in the 96x96 cell), kept whole while the rest loses 7 rows in 47 and 6 columns in 37
FACE_AT = {("hit", 1): (36, 41, 46, 50), ("dead", 1): (40, 42, 48, 50), ("dead", 6): (49, 66, 57, 72),
           ("dead", 7): (40, 72, 49, 80), ("dead", 8): (37, 71, 47, 79)}
BODY = 20                        # a body at least this long (the face to the ankles) loses the design's 5 rows, so
                                 # the run's bob and the crouches keep their pixels; a shorter one in proportion
FEET = 6                         # rows over the soles (and the soles) never deleted
SOLES = 11                       # the soles' row under the pivot
FURTHER = 6 / 37                 # deletions per line of anything beyond the design's own reach
PRIOR = 2.0                      # cost per line of distance from the design's own choice (steadies the strips)
OUTLINE = (0x10, 0x10, 0x1A)
TAGS = ["idle", "run", "attack", "attack_p", "skill", "skill2", "skill2_dash", "ult", "ult2", "hit", "dead"]


def rgb(h):
    return tuple(int(h[k:k + 2], 16) for k in (1, 3, 5))


WEIGHT = {**{rgb(h): D.WEIGHTS["steel"] for h in D.STEEL}, **{rgb(h): D.WEIGHTS["gold"] for h in D.GOLD},
          rgb("#FFF8E8"): D.WEIGHTS["eye"], rgb("#714129"): D.WEIGHTS["eye"]}


def figure(path):
    """The design at 1x, cropped to its pixels, and where its corner was on the 128 canvas."""
    a = blocks(path)
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(), (int(xs.min()), int(ys.min()))


def index(a, pal):
    """Colour indices (-1 empty) and weights of an RGBA picture; new colours join pal."""
    idx = np.full(a.shape[:2], -1, int)
    w = np.ones(a.shape[:2], int)
    for y, x in zip(*np.nonzero(a[..., 3] > 0)):
        c = tuple(int(v) for v in a[y, x, :3])
        if c not in pal:
            pal[c] = len(pal)
        idx[y, x] = pal[c]
        w[y, x] = WEIGHT.get(c, 1)
    return idx, w


# ------------------------------------------------------------------------------------------------ 1 the design
def design_cuts(fig):
    pal = {}
    idx, w = index(fig, pal)
    H, W = idx.shape
    th, tw = HEIGHT, round(W * HEIGHT / H)
    best = None
    for order in ("rc", "cr"):
        if order == "rc":
            r, lr = D.dp_keep(list(idx), list(w), th, KEEP_ROWS)
            c, lc = D.dp_keep(list(idx[r].T), list(w[r].T), tw, KEEP_COLS)
        else:
            c, lc = D.dp_keep(list(idx.T), list(w.T), tw, KEEP_COLS)
            r, lr = D.dp_keep(list(idx[:, c]), list(w[:, c]), th, KEEP_ROWS)
        if best is None or lr + lc < best[0]:
            best = (lr + lc, r, c)
    _, r, c = best
    return sorted(set(range(H)) - set(r)), sorted(set(range(W)) - set(c))


# ------------------------------------------------------------------------------------------------ 2 the frames
def find_head(frame, fig):
    """(share matched, x, y) of the design's corner in the frame, by the head box without the eyes."""
    x0, y0, x1, y1 = HEAD_BOX
    tpl = fig[y0:y1 + 1, x0:x1 + 1]
    m = tpl[..., 3] > 0
    m[EYE_BOX[1] - y0:EYE_BOX[3] - y0 + 1, EYE_BOX[0] - x0:EYE_BOX[2] - x0 + 1] = False
    th, tw = tpl.shape[:2]
    best = (0.0, 0, 0)
    for y in range(frame.shape[0] - th + 1):
        for x in range(frame.shape[1] - tw + 1):
            s = ((frame[y:y + th, x:x + tw] == tpl).all(-1) & m).sum() / m.sum()
            if s > best[0]:
                best = (s, x - x0, y - y0)
    return best


def line_cost(lines, weights, i):
    """What deleting line i loses: its weighted difference from the nearer-looking neighbour (outside: empty)."""
    def diff(j):
        if j < 0 or j >= len(lines):
            other, ow = np.full_like(lines[i], -1), np.ones_like(weights[i])
        else:
            other, ow = lines[j], weights[j]
        return float(((lines[i] != other) * np.maximum(weights[i], ow)).sum())
    return min(diff(i - 1), diff(i + 1))


def pick(costs, k, banned):
    """k of the lines, never two neighbours nor a banned one, the least total cost; [] if impossible."""
    n, INF = len(costs), float("inf")
    if k <= 0:
        return []
    # f[i][t]: least cost choosing t among lines < i, line i-1 not chosen (so line i is free to take)
    f = np.full((n + 2, k + 1), INF)
    take = np.zeros((n + 2, k + 1), bool)
    f[0][0] = 0.0
    for i in range(n):
        for t in range(k + 1):
            if f[i][t] == INF:
                continue
            if f[i][t] < f[i + 1][t]:
                f[i + 1][t], take[i + 1][t] = f[i][t], False
            if t < k and i not in banned and f[i][t] + costs[i] < f[i + 2][t + 1]:
                f[i + 2][t + 1], take[i + 2][t + 1] = f[i][t] + costs[i], True
    end = min((f[i][k], i) for i in (n, n + 1))
    if end[0] == INF:
        return []
    out, i, t = [], end[1], k
    while i > 0:
        if take[i][t]:
            out.append(i - 2)
            i, t = i - 2, t - 1
        else:
            i -= 1
    return sorted(out)


def zone_cuts(idx, w, axis, lo, hi, k, prefer, banned=()):
    """k lines to delete among lo..hi (inclusive) along axis (0 rows, 1 columns), near the preferred ones."""
    if k <= 0 or hi < lo:
        return []
    lines = [idx[i] if axis == 0 else idx[:, i] for i in range(idx.shape[axis])]
    wts = [w[i] if axis == 0 else w[:, i] for i in range(idx.shape[axis])]
    span = list(range(lo, hi + 1))
    costs = [line_cost(lines, wts, i) + (PRIOR * min(min(abs(i - p) for p in prefer), 5) if prefer else 0.0)
             for i in span]
    chosen = pick(costs, k, {j for j, i in enumerate(span) if i in banned})
    return [span[j] for j in chosen]


def extent(idx, axis, lo, hi):
    """Lines lo..hi (inclusive, either order) from lo to the farthest one holding a pixel: their count."""
    step = 1 if hi >= lo else -1
    far = None
    for i in range(lo, hi + step, step):
        if 0 <= i < idx.shape[axis] and ((idx[i] if axis == 0 else idx[:, i]) >= 0).any():
            far = i
    return 0 if far is None else abs(far - lo) + 1


def frame_cuts(frame, fig, drow, dcol, pivot, pal, face_at=None):
    """(rows, columns) of a 96x96 frame to delete, and the head's (share, x, y). The frame's outermost rows and
    columns never go: the outline put back on the new edge would make up for them."""
    idx, w = index(frame, pal)
    share, hx, hy = find_head(frame, fig)
    H, W = fig.shape[:2]
    x0, y0, x1, y1 = HEAD_BOX
    soles = pivot[1] + SOLES
    ys, xs = np.nonzero(idx >= 0)
    edge_r, edge_c = {int(ys.min()), int(ys.max()), soles}, {int(xs.min()), int(xs.max())}
    rows, cols = [], []
    if face_at is None and share >= FOUND:
        rows += [hy + r for r in drow if y0 <= r <= y1]
        cols += [hx + c for c in dcol if x0 <= c <= x1]
        top, bottom, left, right = hy + y0, hy + y1, hx + x0, hx + x1
        body = [r for r in drow if r > y1 and r < H - FEET]            # the design's rows below the head
        prefer_r = [hy + r for r in body if r <= H - 1 - 15] + [soles - (H - 1 - r) for r in body if r > H - 1 - 15]
        zone = (bottom + 1, soles - FEET)
        n = zone[1] - zone[0] + 1
        k = len(body) if n >= BODY else round(n * len(body) / (H - FEET - y1 - 1))
        rows += zone_cuts(idx, w, 0, zone[0], zone[1], k, prefer_r, edge_r)
        # above the head: the design's own rows there stay (the ponytail's top), 16% of anything higher
        up = extent(idx, 0, top - 1, 0)
        rows += zone_cuts(idx, w, 0, top - up, top - 1 - y0, round(max(0, up - y0) * FURTHER), [], edge_r)
        left_d = [c for c in dcol if c < x0]
        right_d = [c for c in dcol if c > x1]
        lx = extent(idx, 1, left - 1, 0)
        k_l = round(min(lx, x0) * len(left_d) / x0) + round(max(0, lx - x0) * FURTHER)
        cols += zone_cuts(idx, w, 1, left - lx, left - 1, k_l, [hx + c for c in left_d], edge_c)
        rx = extent(idx, 1, right + 1, idx.shape[1] - 1)
        k_r = round(min(rx, W - 1 - x1) * len(right_d) / (W - 1 - x1)) + round(max(0, rx - (W - 1 - x1)) * FURTHER)
        banned = edge_c | ({right + 1} if x1 in dcol else set())
        cols += zone_cuts(idx, w, 1, right + 1, right + rx, k_r, [hx + c for c in right_d], banned)
        below = extent(idx, 0, soles + 1, idx.shape[0] - 1)
        rows += zone_cuts(idx, w, 0, soles + 1, soles + below, round(below * FURTHER), [], edge_r)
    else:
        # a head Codex drew anew: its face (FACE_AT) kept, 7 rows in 47 and 6 columns in 37 of the rest, the feet
        # kept while she stands
        if face_at is None:
            sys.exit(f"the design's head is not in this frame ({share:.0%}) and FACE_AT has no face for it")
        fx0, fy0, fx1, fy1 = face_at
        keep_r = set(range(fy0, fy1 + 1)) | edge_r
        if fy1 < soles - 15:
            keep_r |= set(range(soles - FEET, soles + 1))
        hh, ww = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        rows = zone_cuts(idx, w, 0, ys.min(), ys.max(), round(hh * (H - HEIGHT) / H), [], keep_r)
        cols = zone_cuts(idx, w, 1, xs.min(), xs.max(), round(ww * len(dcol) / W), [],
                         set(range(fx0, fx1 + 1)) | edge_c)
    return sorted(set(rows)), sorted(set(cols)), (share, hx, hy)


def cut(a, rows, cols, pivot):
    """The frame without those rows and columns, the outline put back where a deleted line held it, on its pivot."""
    H, W = a.shape[:2]
    kr = [y for y in range(H) if y not in rows]
    kc = [x for x in range(W) if x not in cols]
    small = a[np.ix_(kr, kc)].copy()
    soles = pivot[1] + SOLES
    out = small.copy()
    dark = lambda p: p[3] > 0 and tuple(int(v) for v in p[:3]) == OUTLINE  # noqa: E731
    for y in range(small.shape[0]):
        for x in range(small.shape[1]):
            if small[y, x, 3] == 0:
                continue
            oy, ox = kr[y], kc[x]
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if not (0 <= ny < small.shape[0] and 0 <= nx < small.shape[1]) or small[ny, nx, 3] > 0:
                    continue
                if kr[ny] > soles:
                    continue
                py, px = oy + dy, ox + dx                  # the original neighbour, maybe on a deleted line
                if (py in rows or px in cols) and 0 <= py < H and 0 <= px < W and dark(a[py, px]):
                    out[ny, nx] = OUTLINE + (255,)
    # back on the pivot: the soles on their row, the pivot column where it was
    sy = sum(1 for r in rows if r < soles)
    sx = sum(1 for c in cols if c < pivot[0])
    res = np.zeros_like(a)
    oh, ow = out.shape[:2]
    res[sy:sy + oh, sx:sx + ow] = out[:H - sy, :W - sx]
    return res


# ------------------------------------------------------------------------------------------------ files
def strip_frames(tag, n, cell):
    a = blocks(os.path.join(SRC, f"akali_{tag}.png"))
    cols, rows = layout(n)
    return [a[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]]
            for k in range(n)], (cols, rows)


def to_strip(frames, grid, cell):
    cols, rows = grid
    a = np.zeros((rows * cell[1], cols * cell[0], 4), np.uint8)
    for k, f in enumerate(frames):
        a[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]] = f
    return np.repeat(np.repeat(a, Z, 0), Z, 1)


def design_canvas(idle, pivot):
    """The 40-row design on the 128 canvas (8x), cut from the shrunk idle: the soles on row 99, the feet's middle on
    column 64, as design_akali.py places the 47-row one."""
    ys, xs = np.nonzero(idle[..., 3] > 0)
    fig = idle[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    soles = np.nonzero(fig[-1, :, 3] > 0)[0]
    fx = (soles.min() + soles.max() + 1) // 2
    canvas = np.zeros((128, 128, 4), np.uint8)
    x0, y0 = 64 - fx, 100 - fig.shape[0]
    canvas[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return np.repeat(np.repeat(canvas, Z, 0), Z, 1), fig


def review(before, after, path, z=5):
    """The strip at 47 over the strip at 40, each frame cropped to what both show, on a grey ground, 5x."""
    boxes = []
    for a in before + after:
        ys, xs = np.nonzero(a[..., 3] > 0)
        boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    x0, y0 = min(b[0] for b in boxes) - 1, min(b[1] for b in boxes) - 1
    x1, y1 = max(b[2] for b in boxes) + 2, max(b[3] for b in boxes) + 2
    tiles = []
    for strip in (before, after):
        row = []
        for a in strip:
            t = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
            t[...] = (72, 76, 84, 255)
            c = a[y0:y1, x0:x1]
            t[c[..., 3] > 0] = c[c[..., 3] > 0]
            row.append(np.pad(t, ((0, 0), (0, 2), (0, 0))))
        tiles.append(np.concatenate(row, 1))
    img = np.concatenate([tiles[0], np.zeros((2,) + tiles[0].shape[1:], np.uint8), tiles[1]], 0)
    img[..., 3] = 255
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(np.repeat(np.repeat(img, z, 0), z, 1)).save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the committed files instead of writing them")
    ap.add_argument("--review", help="write the frames before/after side by side to this folder")
    o = ap.parse_args()
    fig, _ = figure(os.path.join(SRC, "akali_native.png"))
    drow, dcol = design_cuts(fig)
    print(f"design {fig.shape[1]}x{fig.shape[0]}: rows {drow}, columns {dcol}")
    with open(CELLS, encoding="utf-8") as f:
        spec = json.load(f)
    cell = tuple(spec["cell"])
    pal = {}
    written, same = [], True
    for tag in TAGS:
        table = spec["tags"][tag]
        frames, grid = strip_frames(tag, len(table), cell)
        new = []
        for k, (fr, row) in enumerate(zip(frames, table)):
            rows, cols, (share, hx, hy) = frame_cuts(fr, fig, drow, dcol, row["pivot"], pal, FACE_AT.get((tag, k + 1)))
            new.append(cut(fr, rows, cols, row["pivot"]))
            print(f"  {tag:11s} {k + 1}: head {share:4.0%} at ({hx:3d},{hy:3d})  rows -{len(rows)} {rows}  "
                  f"columns -{len(cols)} {cols}")
        if tag == "idle":
            big, small = design_canvas(new[0], table[0]["pivot"])
            print(f"design at {HEIGHT}: {small.shape[1]}x{small.shape[0]}")
            written.append(("akali_native.png", big))
        written.append((f"akali_{tag}.png", to_strip(new, grid, cell)))
        if o.review:
            review(frames, new, os.path.join(o.review, f"akali_{tag}_40.png"))
    for name, a in written:
        path = os.path.join(OUT, name)
        if o.check:
            old = np.asarray(Image.open(D.lp(path)).convert("RGBA"))
            ok = old.shape == a.shape and (old == a).all()
            same &= ok
            print(("same " if ok else "DIFFERENT ") + name)
        else:
            Image.fromarray(a).save(D.lp(path))
    if o.check:
        sys.exit(0 if same else 1)
    print(f"written {len(written)} files to {OUT}")


if __name__ == "__main__":
    main()
