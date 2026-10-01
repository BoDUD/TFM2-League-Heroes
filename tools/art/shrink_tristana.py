#!/usr/bin/env python3
"""Tristana at 34 rows: the approved 41-row design and strips with whole rows and columns deleted, never the head.

    python tools/art/shrink_tristana.py [--check] [--review DIR]

She is a yordle, and at 41 rows (goggles to soles; 56 wide with the cannon, the most pixels of any hero in the pack)
she stood a head over Garen (37) and Teemo (38 with his hat). The user picked 34 rows from 36 / 34 / 32 previews
("34 行"), the head kept whole: a yordle's head is most of her, so the rows go from the goggles' top, the neck, the
waist and the legs, the columns from the left ear's tip and the cannon's barrel and bell.
The method is the one tools/art/shrink_akali.py used for Akali's 47 -> 40 (removed with her redo, adc593a^):
nothing is redrawn or resampled, every kept pixel is the source's. Sources, at the approved size: the design and the
strips as approved (assets/source/native/tristana_*.png at 41 rows, copied to assets/source/tristana/native41/ by the
first run; every run starts from there, so a second run changes nothing and --check can tell).
1. The design: 7 rows and 10 columns go, found by dynamic programming (design_akali.dp_keep: never two neighbours, a
   deleted line costing its difference from the nearer neighbour; the amber eyes weigh 12, the mouth 6, the cannon's
   steel and brass 2) with the outline on top, the head from the hair's top down to the neck (rows 7-21), the feet
   (rows 38-40), the thighs and knees (rows 33-36), the head's columns but the left ear's tip (5-36) and the bell's
   rims (44, 45, 54, 55) kept: rows 1 (the goggles' cups), 22, 24, 27, 29, 31 (the shoulders and the waist - through
   the cannon, which loses as many), 37 (the boots); columns 1, 3 (the left ear's tip), 37, 39, 41, 43 (the brass
   barrel), 46, 48, 50, 52 (inside the bell). 46x34. A first cut took a thigh row (34) and a boot row (37): the left
   leg's slant from the thigh to the boot came out in steps (the user: "小炮缩放后左腿看起来像少了一块？"). The user picked this smaller cannon ("炮可以调小一点", B) over the first 34-row cut, which kept the
   cannon whole (50 wide), and one that only narrowed the bell (47).
2. Every upright frame: the design's head (HEAD_BOX, the block Codex pasted in every frame; its eyes out of the search,
   closed in the hit) is found in it and the rows and columns the design loses inside that box go, so the head is the
   design's in every frame. The rest by zones round the head, with as many deletions as the design has there for its
   length: below the head down to the feet the design's 6 rows of its 20 (preferring its rows, counted from the
   soles; the thighs and knees in every frame are the design's rows 33-36 counted from the soles, kept), the feet (3 rows over the soles) kept; right of the head 8 of the first 19 columns (the cannon held
   forward); 10/56 of anything reaching further (the cannon raised over the head, swung behind her) - each zone by
   the same dynamic programming.
3. The outline put back where a deleted line held it (a pixel whose outline neighbour went gets one on the new edge),
   never under the soles. Each frame stays on its pivot, the soles 11 rows under it.
4. Frames that are another frame turned whole are turned again from the shrunk one: W's 4th and 5th are its 3rd turned
   90 and 45 degrees clockwise (Codex's own construction; the bottom row and the middle column where they were), and
   the death's 5th-8th tools/art/fix_tristana_dead.py's: the 3rd's body with the hit's closed eyes turned 45 / 90 / 90
   / 90 and put down by its plan, beside the cannon lying on the ground (the 2nd's lowest piece, cut as the 2nd), and
   that one cannon replaces the 3rd and 4th's own, so it lies still from the 2nd frame on.
Writes assets/source/native/tristana_native.png and tristana_<tag>.png (8x, cells and pivots unchanged); then run
tools/art/import_native.py --hero tristana. --check compares with the files instead of writing.
"""
import argparse
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import design_akali as D  # noqa: E402
import fix_tristana_dead as FD  # noqa: E402
from import_native import blocks  # noqa: E402
from native_refs import Z, layout  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "tristana", "native41")
CELLS = os.path.join(OUT, "tristana_cells.json")
HEIGHT = 34
KEEP_ROWS = {0} | set(range(7, 22)) | set(range(33, 37)) | {38, 39, 40}   # the design's: the outline on top (it would
    # come back), the head from the hair's top to the neck, the thighs and knees (a thigh row cut the left leg's slant
    # into steps: "左腿看起来像少了一块"), the feet
WIDTH = 46                                     # 10 columns: the left ear's tip, the brass barrel, inside the bell
KEEP_COLS = {0} | set(range(5, 37)) | {44, 45, 54, 55}   # the outline at the ear's tip, the head but the ear's tip,
                                                         # the bell's rims
HEAD_BOX = (0, 0, 36, 17)        # x0, y0, x1, y1 (inclusive) on the 41-row design: goggles to chin, both ears
EYE_BOX = (18, 12, 25, 15)       # the lashes, the eyes and the row under them: out of the search (closed in the hit)
FOUND = 0.8                      # share of the head's pixels that must match
BODY = 20                        # the design's rows from under the chin to over the feet
FEET = 3                         # rows over the soles (and the soles) never deleted
SOLES = 11                       # the soles' row under the pivot
FURTHER = 10 / 56                # deletions per line of anything beyond the design's own reach
PRIOR = 2.0                      # cost per line of distance from the design's own choice (steadies the strips)
OUTLINE = (0x19, 0x14, 0x21)
TAGS = ["idle", "attack", "skill", "skill2", "ult", "hit", "dead"]   # not the run: Codex redrew it at 34 rows, the head
# moving with the body (tristana_run.png comes from its redo, assets/source/tristana/codex_run_redo/)
# frames turned whole from another frame (1-based): (source frame, turn)
TURNED = {("skill2", 4): (3, "cw90"), ("skill2", 5): (3, "cw45")}
# frames Codex turned a little as a whole (R's 5th about 24 degrees, the death's 4th about 25): the design's head is not
# in them upright, and turning them back and again would double the nearest-neighbour steps; their face (the eyes'
# box, from the lashes to the mouth: x0, y0, x1, y1 in the cell) is kept and the rest loses 7 rows in 41 and 10
# columns in 56, the feet kept while she stands
FACE_AT = {("ult", 5): (57, 61, 68, 70), ("dead", 4): (71, 49, 82, 57)}
DEAD_PLAN = {5: (45, 9, 10), 6: (90, 2, 16), 7: (90, 0, 16), 8: (90, 0, 16)}   # fix_tristana_dead.py's (1-based)
WEIGHT = {(246, 186, 48): 12, (130, 29, 63): 6,                               # amber eyes, mouth
          **{c: 2 for c in ((0x73, 0x97, 0xC3), (0x44, 0x5E, 0x80), (0x7E, 0x87, 0x9E), (0xB9, 0xDD, 0xED),
                            (0xBF, 0xCC, 0xD8))},                              # steel: the bell, the lenses
          **{c: 2 for c in ((0xC8, 0x99, 0x4E), (0x87, 0x60, 0x2E), (0xE6, 0xBF, 0x86), (0xA3, 0x6A, 0x43))}}  # brass


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


def figure(a):
    """The picture cropped to its pixels, and its corner."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(), (int(xs.min()), int(ys.min()))


# ------------------------------------------------------------------------------------------------ 1 the design
def design_cuts(fig):
    pal = {}
    idx, w = index(fig, pal)
    H, W = idx.shape
    th, tw = HEIGHT, WIDTH
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
    total, r, c = best
    if not np.isfinite(total) or len(r) != th or len(c) != tw:
        sys.exit(f"no {tw}x{th} cut keeps the kept rows and columns")
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
    H, W = fig.shape[:2]
    soles = pivot[1] + SOLES
    ys, xs = np.nonzero(idx >= 0)
    edge_r, edge_c = {int(ys.min()), int(ys.max()), soles}, {int(xs.min()), int(xs.max())}
    if face_at is not None:
        fx0, fy0, fx1, fy1 = face_at
        keep_r = set(range(fy0, fy1 + 1)) | edge_r
        if fy1 < soles - 15:
            keep_r |= set(range(soles - FEET, soles + 1))
        hh, ww = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
        rows = zone_cuts(idx, w, 0, int(ys.min()), int(ys.max()), round(hh * len(drow) / H), [], keep_r)
        cols = zone_cuts(idx, w, 1, int(xs.min()), int(xs.max()), round(ww * len(dcol) / W), [],
                         set(range(fx0, fx1 + 1)) | edge_c)
        return sorted(set(rows)), sorted(set(cols)), (None, fx0, fy0)
    share, hx, hy = find_head(frame, fig)
    if share < FOUND:
        sys.exit(f"the design's head is not in this frame ({share:.0%})")
    x0, y0, x1, y1 = HEAD_BOX
    rows = [hy + r for r in drow if y0 <= r <= y1]
    cols = [hx + c for c in dcol if x0 <= c <= x1]
    top, bottom, left, right = hy + y0, hy + y1, hx + x0, hx + x1
    body = [r for r in drow if y1 < r < H - FEET]                  # the design's rows under the chin
    prefer_r = [hy + r for r in body if r <= y1 + 4] + [soles - (H - 1 - r) for r in body if r > y1 + 4]
    zone = (bottom + 1, soles - FEET)
    n = zone[1] - zone[0] + 1
    k = len(body) if n >= BODY else round(n * len(body) / BODY)
    thighs = {soles - (H - 1 - r) for r in range(33, 37)}         # the design's thighs and knees over the soles
    rows += zone_cuts(idx, w, 0, zone[0], zone[1], k, prefer_r, edge_r | thighs)
    up = extent(idx, 0, top - 1, 0)                                # over the goggles: the cannon raised
    rows += zone_cuts(idx, w, 0, top - up, top - 1, round(up * FURTHER), [], edge_r)
    lx = extent(idx, 1, left - 1, 0)                               # behind her: the cannon swung back
    cols += zone_cuts(idx, w, 1, left - lx, left - 1, round(lx * FURTHER), [], edge_c)
    right_d = [c for c in dcol if c > x1]
    rx = extent(idx, 1, right + 1, idx.shape[1] - 1)
    reach = W - 1 - x1
    k_r = round(min(rx, reach) * len(right_d) / reach) + round(max(0, rx - reach) * FURTHER)
    banned = edge_c | ({right + 1} if x1 in dcol else set())
    cols += zone_cuts(idx, w, 1, right + 1, right + rx, k_r, [hx + c for c in right_d], banned)
    return sorted(set(rows)), sorted(set(cols)), (share, hx, hy)


def cut(a, rows, cols, pivot):
    """The frame without those rows and columns, the outline put back where a deleted line held it, on its pivot."""
    H, W = a.shape[:2]
    kr = [y for y in range(H) if y not in rows]
    kc = [x for x in range(W) if x not in cols]
    small = a[np.ix_(kr, kc)].copy()
    soles = pivot[1] + SOLES
    out = small.copy()

    def dark(p):
        return p[3] > 0 and tuple(int(v) for v in p[:3]) == OUTLINE

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
    sy = sum(1 for r in rows if r < soles)                 # back on the pivot: the soles on their row
    sx = sum(1 for c in cols if c < pivot[0])              # and the pivot column where it was
    res = np.zeros_like(a)
    oh, ow = out.shape[:2]
    res[sy:sy + oh, sx:sx + ow] = out[:H - sy, :W - sx]
    return res


# ------------------------------------------------------------------------------------------------ 4 turned frames
def turn(fig, how):
    if how == "cw90":
        return np.rot90(fig, -1).copy()
    if how == "cw45":
        return np.asarray(Image.fromarray(fig).rotate(-45, resample=Image.NEAREST, expand=True)).copy()
    raise ValueError(how)


def place_like(old, fig):
    """fig on an empty cell, its lowest row and its middle column where old's were."""
    ys, xs = np.nonzero(old[..., 3] > 0)
    f, _ = figure(fig)
    out = np.zeros_like(old)
    bottom, mid = int(ys.max()), (int(xs.min()) + int(xs.max()) + 1) // 2
    top, left = bottom - f.shape[0] + 1, mid - f.shape[1] // 2
    region = out[top:top + f.shape[0], left:left + f.shape[1]]
    m = f[..., 3] > 0
    region[m] = f[m]
    return out


def dead_turned(dead, hit1, head, eye, cannon, pivots):
    """The death's 5th-8th rebuilt from the shrunk 3rd (fix_tristana_dead.py): its body with the hit's closed eyes
    (eye: the eye box in the shrunk head), turned and put down by DEAD_PLAN beside the cannon on the ground."""
    hm = head[..., 3] > 0
    c3 = dead[2]
    s3, hx, hy = FD.find_head(c3, head, hm)
    body = [p for p in FD.pieces(c3[..., 3] > 0) if p[hy:hy + head.shape[0], hx:hx + head.shape[1]].any()][0]
    fig = np.where(body[..., None], c3, 0).astype(np.uint8)
    s1, gx, gy = FD.find_head(hit1, head, hm)
    x0, y0, x1, y1 = eye
    fig[hy + y0:hy + y1, hx + x0:hx + x1] = hit1[gy + y0:gy + y1, gx + x0:gx + x1]
    fig, _ = figure(fig)
    out = {}
    for k, (deg, lift, dx) in DEAD_PLAN.items():
        px, py = pivots[k - 1]
        cell = cannon.copy()
        f, _ = figure(FD.rotate(fig, deg))
        bottom = py + SOLES - lift
        top, left = bottom - f.shape[0] + 1, px + dx - f.shape[1] // 2
        reg = cell[top:top + f.shape[0], left:left + f.shape[1]]
        m = f[..., 3] > 0
        reg[m] = f[m]
        out[k] = cell
    return out, (s3, s1)


# ------------------------------------------------------------------------------------------------ files
def strip_frames(path, n, cell):
    a = blocks(path)
    cols, rows = layout(n)
    return [a[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]].copy()
            for k in range(n)], (cols, rows)


def to_strip(frames, grid, cell):
    cols, rows = grid
    a = np.zeros((rows * cell[1], cols * cell[0], 4), np.uint8)
    for k, f in enumerate(frames):
        a[k // cols * cell[1]:(k // cols + 1) * cell[1], k % cols * cell[0]:(k % cols + 1) * cell[0]] = f
    return np.repeat(np.repeat(a, Z, 0), Z, 1)


def design_canvas(idle, corner, size):
    """The shrunk design on the source's 128 canvas (8x): the soles on the row they had, the feet's middle on the
    column they had."""
    fig, _ = figure(idle)
    canvas = np.zeros((size, size, 4), np.uint8)
    x0, y0 = corner
    canvas[y0:y0 + fig.shape[0], x0:x0 + fig.shape[1]] = fig
    return np.repeat(np.repeat(canvas, Z, 0), Z, 1), fig


def review(before, after, path, z=5):
    """The strip at 41 over the strip at 34, each frame cropped to what both show, on a grey ground, 5x."""
    boxes = []
    for a in before + after:
        ys, xs = np.nonzero(a[..., 3] > 0)
        boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    H, W = before[0].shape[:2]
    x0, y0 = max(0, min(b[0] for b in boxes) - 1), max(0, min(b[1] for b in boxes) - 1)
    x1, y1 = min(W, max(b[2] for b in boxes) + 2), min(H, max(b[3] for b in boxes) + 2)
    tiles = []
    for strip in (before, after):
        row = []
        for a in strip:
            t = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
            t[...] = (92, 98, 86, 255)
            c = a[y0:y1, x0:x1]
            t[c[..., 3] > 0] = c[c[..., 3] > 0]
            row.append(np.pad(t, ((0, 0), (0, 2), (0, 0))))
        tiles.append(np.concatenate(row, 1))
    img = np.concatenate([tiles[0], np.zeros((2,) + tiles[0].shape[1:], np.uint8), tiles[1]], 0)
    img[..., 3] = 255
    os.makedirs(path.rsplit(os.sep, 1)[0], exist_ok=True)
    Image.fromarray(np.repeat(np.repeat(img, z, 0), z, 1)).save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    ap.add_argument("--review", help="write the frames before/after side by side to this folder")
    o = ap.parse_args()
    names = ["tristana_native.png"] + [f"tristana_{t}.png" for t in TAGS]
    if not os.path.exists(D.lp(os.path.join(SRC, "tristana_native.png"))):
        os.makedirs(D.lp(SRC), exist_ok=True)
        for name in names:
            shutil.copyfile(D.lp(os.path.join(OUT, name)), D.lp(os.path.join(SRC, name)))
        print("the 41-row design and strips copied to", SRC)
    big = blocks(os.path.join(SRC, "tristana_native.png"))
    fig, corner = figure(big)
    drow, dcol = design_cuts(fig)
    print(f"design {fig.shape[1]}x{fig.shape[0]}: rows {drow}, columns {dcol}")
    with open(CELLS, encoding="utf-8") as f:
        spec = json.load(f)
    cell = tuple(spec["cell"])
    pal = {}
    written, shrunk, sources = [], {}, {}
    for tag in TAGS:
        table = spec["tags"][tag]
        frames, grid = strip_frames(os.path.join(SRC, f"tristana_{tag}.png"), len(table), cell)
        sources[tag] = frames
        new, cuts = [], {}
        for k, (fr, row) in enumerate(zip(frames, table)):
            if (tag, k + 1) in TURNED or (tag == "dead" and k + 1 in DEAD_PLAN):
                new.append(None)
                continue
            rows, cols, (share, hx, hy) = frame_cuts(fr, fig, drow, dcol, row["pivot"], pal, FACE_AT.get((tag, k + 1)))
            cuts[k + 1] = (rows, cols)
            new.append(cut(fr, rows, cols, row["pivot"]))
            head = "face kept" if share is None else f"head {share:4.0%}"
            print(f"  {tag:7s} {k + 1}: {head} at ({hx:3d},{hy:3d})  rows -{len(rows)} {rows}  "
                  f"columns -{len(cols)} {cols}")
        for (t, k), (src, how) in TURNED.items():
            if t == tag:
                new[k - 1] = place_like(frames[k - 1], turn(figure(new[src - 1])[0], how))
                print(f"  {tag:7s} {k}: frame {src} turned {how}")
        shrunk[tag] = (new, grid, cuts)
    # the death's turned frames: the shrunk head (the head box of the shrunk design) finds the body and the closed eyes
    small = shrunk["idle"][0][0]
    sfig, _ = figure(small)
    kept_r = [r for r in range(HEAD_BOX[1], HEAD_BOX[3] + 1) if r not in drow]
    kept_c = [c for c in range(HEAD_BOX[0], HEAD_BOX[2] + 1) if c not in dcol]
    head = fig[np.ix_(kept_r, kept_c)]
    eye = (sum(1 for c in kept_c if c < EYE_BOX[0]), sum(1 for r in kept_r if r < EYE_BOX[1]),
           sum(1 for c in kept_c if c <= EYE_BOX[2]), sum(1 for r in kept_r if r <= EYE_BOX[3]))
    dead, grid, cuts = shrunk["dead"]
    # the cannon on the ground: the 2nd frame's lowest piece (she is high in the air there; in the 5th her turned body
    # touches it), cut as the 2nd - it lies in the same place in the 2nd to the 8th
    lowest = max(FD.pieces(sources["dead"][1][..., 3] > 0), key=lambda p: np.nonzero(p)[0].mean())
    cannon41 = np.where(lowest[..., None], sources["dead"][1], 0).astype(np.uint8)
    pivots = [r["pivot"] for r in spec["tags"]["dead"]]
    cannon = cut(cannon41, *cuts[2], pivots[1])
    turned, (s3, s1) = dead_turned(dead, shrunk["hit"][0][0], head, eye, cannon, pivots)
    for k, c in turned.items():
        dead[k - 1] = c
    for k in (3, 4):                        # the cannon lies still from the 2nd frame on: the same piece in every frame
        f = dead[k - 1]
        low = max(FD.pieces(f[..., 3] > 0), key=lambda p: np.nonzero(p)[0].mean())
        f[low] = 0
        m = cannon[..., 3] > 0
        f[m] = cannon[m]
    print(f"  dead 5-8: the 3rd's body (head {s3}/{(head[..., 3] > 0).sum()}), the hit's eyes ({s1}), turned")
    for tag in TAGS:
        new, grid, _ = shrunk[tag]
        if tag == "idle":
            feet = np.nonzero(fig[-1, :, 3] > 0)[0]                    # the stance's middle stays where it was
            mid = (int(feet.min()) + int(feet.max()) + 1) // 2
            canvas, sfig = design_canvas(new[0], (corner[0] + sum(1 for c in dcol if c < mid),
                                                  corner[1] + len(drow)), big.shape[0])
            print(f"design at {HEIGHT}: {sfig.shape[1]}x{sfig.shape[0]}")
            written.append(("tristana_native.png", canvas))
        written.append((f"tristana_{tag}.png", to_strip(new, grid, cell)))
        if o.review:
            review(sources[tag], new, os.path.join(o.review, f"tristana_{tag}_34.png"))
    same = True
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
