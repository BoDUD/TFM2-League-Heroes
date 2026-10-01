#!/usr/bin/env python3
"""Jax at 36 rows: the approved 41-row design and strips with whole rows and columns deleted, never the mask.

    python tools/art/shrink_jax.py [--check] [--review DIR]

Players found him too big in game ("贾克斯模型被反应尺寸太大", 2026-10-01): at 41 rows (the plume's top to the soles)
and 50 columns (the lamppost's hook to its lantern) he covered 1158 pixels standing, more than any hero but Malphite
(Darius 998, Garen 722). The user picked 36 rows from 39 / 37 / 36 / 35 previews ("36 行"). The method is
tools/art/shrink_tristana.py's: nothing is redrawn or resampled, every kept pixel is the source's. Sources, at the
approved size: the design and the strips as approved (assets/source/native/jax_*.png at 41 rows, copied to
assets/source/jax/native41/ by the first run; every run starts from there, so a second run changes nothing and --check
can tell).
1. The design: 5 rows and 6 columns go, in each zone round the mask as many as ROWS and COLS say, found by dynamic
   programming (shrink_tristana.zone_cuts: never two neighbours, a deleted line costing its weighted difference from
   the nearer neighbour; the mask's cyan lights weigh 12, its bronze 4), the outline on top and at both sides, the
   mask's rows and columns (the bronze faceplate pasted in every frame) and the feet (FEET rows over the soles) kept.
   44x36.
2. Every frame with the mask (Codex drew the four lights, export_jax.py pasted the design's mask on them): the mask is
   found, and the frame loses lines in zones round it, as many as the design loses there for its length - over the
   mask (the hood and the plume; where the lamppost is raised past the plume's reach, FURTHER of the rest), under it
   down to the feet (a crouch or a frame in the air in proportion, the feet kept), left of it (the hood's back, the
   cape, the lamppost's hook) and right of it (the arm, the lantern) - each zone by the same dynamic programming,
   one line in each of as many equal stretches (a long thin thing - the lamppost's shaft, the plume - loses its share,
   not all of them), the cheapest there by its difference from the nearer line, PENALTY for the pole's and the
   lantern's pixels on it and FOOT_PENALTY for the shoes', and preferring the lines the design loses (counted from the
   mask). The idle, the design on every idle pivot, loses exactly the design's lines. Lying in the death (no lights): the design's share of rows and columns over the whole
   figure. The frame's outermost rows and columns never go (the outline would come back for them).
3. The colours of RECOLOUR (the user's pick of three; nothing else changes).
4. The outline put back where a deleted line held it (a pixel whose outline neighbour went gets one on the new edge,
   in that neighbour's colour), never under the soles. Each frame stays on its pivot, the soles 11 rows under it.
Writes assets/source/native/jax_native.png and jax_<tag>.png (8x, cells and pivots unchanged); then run
tools/art/import_native.py --hero jax and tools/art/preview_jax.py. --check compares with the files instead of writing.
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
import shrink_tristana as ST  # noqa: E402
from import_native import blocks  # noqa: E402

OUT = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "jax", "native41")
CELLS = os.path.join(OUT, "jax_cells.json")
HEIGHT = 36
WIDTH = 44
# where the design's 5 rows and 6 columns go, in proportion to the lines each side of the mask: 2 rows over it (the
# plume, the hood's top) and 3 under it (the shoulders, the body, the legs over the feet); 3 columns left of it (the
# lamppost's hook, the cape, the hood's back) and 3 right of it (the arm, the lamppost, the lantern). One pass over the
# whole height took all five rows from the plume, which is all alike, and left the body as big
ROWS = {"above": 2, "below": 3}
COLS = {"left": 3, "right": 3}
FOUND = 0.8                              # share of the mask's bronze and lights that must match
EYE = (0x46, 0xF0, 0xFF)                 # the four lights on the mask; no other pixel uses it
MASK_COLOURS = {(0x70, 0x4A, 0x23), (0xA1, 0x73, 0x37), (0xB4, 0x83, 0x40), (0x2C, 0x18, 0x20), EYE}
OUTLINES = {(0x0F, 0x02, 0x13), (0x11, 0x03, 0x15), (0x17, 0x02, 0x1C)}
WEIGHT = {EYE: 12, **{c: 4 for c in MASK_COLOURS - {EYE}}}
FEET = 4                                 # rows over the soles (and the soles) never deleted: the shoes from their
                                         # magenta strap row down (3 took the strap off in some frames only)
POLE = (0x69, 0x3A, 0x5D)                # the lamppost's pole
GLOW = (0x8A, 0x29, 0x01)                # the lantern's glass
# what a deleted line pays for each pixel of these on it, besides its difference from the nearer neighbour: a uniform
# shaft costs nothing to shorten, and the first pass took all of a zone's lines from the pole (the lantern on the
# hands, a shallow shaft broken in two); the shoes' columns over the feet rows likewise
PENALTY = {POLE: 6, GLOW: 3}
FOOT_PENALTY = 4
SOLES = 11                               # the soles' row under the pivot
TAGS = ["idle", "run", "attack", "attack_w", "attack_e", "attack_r", "skill", "skill2", "skill2_burst", "ult", "hit",
        "dead"]
# the colours: players found the picture's hot magenta hood and bright blue plume ugly ("贾克斯的颜色太丑 能不能换个颜色
# 模型没问题", 2026-10-01); the user picked "A 紫金" of three: the hood and cape a royal purple, the plume a deeper
# blue, the skin a touch greyer so the bronze mask stands out. The model, the mask, the lamppost, the outline as drawn
RECOLOUR = {"BB1E8E": "7E4FB5", "7E0260": "5C3389", "550343": "3E2263", "C62D57": "A27BD0",      # hood and cape
            "242EB4": "2F4A9C", "1B2496": "233A7E", "12166B": "18285A",                         # plume
            "8580BA": "8D86AE", "5D59AE": "65619A", "34195F": "3A2A5C"}                         # skin


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


def eyes(a):
    return (a[..., 3] > 0) & (a[..., :3] == np.array(EYE, np.uint8)).all(-1)


def mask_box(fig):
    """x0, y0, x1, y1 (inclusive) of the mask on the design: its bronze and lights round the four lights, and the
    outline round them."""
    ey, ex = np.nonzero(eyes(fig))
    cy, cx = (ey.min() + ey.max()) / 2, (ex.min() + ex.max()) / 2
    m = np.zeros(fig.shape[:2], bool)
    for y, x in zip(*np.nonzero(fig[..., 3] > 0)):
        if abs(y - cy) <= 4.5 and abs(x - cx) <= 4.5 and tuple(int(v) for v in fig[y, x, :3]) in MASK_COLOURS:
            m[y, x] = True
    ys, xs = np.nonzero(m)
    return int(xs.min()) - 1, int(ys.min()) - 1, int(xs.max()) + 1, int(ys.max()) + 1


# ------------------------------------------------------------------------------------------------ 1 the design
def design_cuts(fig, box):
    pal = {}
    idx, w = index(fig, pal)
    H, W = idx.shape
    x0, y0, x1, y1 = box
    rows = (ST.zone_cuts(idx, w, 0, 0, y0 - 1, ROWS["above"], [], {0}) +
            ST.zone_cuts(idx, w, 0, y1 + 1, H - 2 - FEET, ROWS["below"], []))
    cols = (ST.zone_cuts(idx, w, 1, 0, x0 - 1, COLS["left"], [], {0}) +
            ST.zone_cuts(idx, w, 1, x1 + 1, W - 1, COLS["right"], [], {W - 1}))
    if H - len(rows) != HEIGHT or W - len(cols) != WIDTH:
        sys.exit(f"the cuts make {W - len(cols)}x{H - len(rows)}, not {WIDTH}x{HEIGHT}")
    return sorted(rows), sorted(cols)


# ------------------------------------------------------------------------------------------------ 2 the frames
def find_mask(frame, fig, box):
    """(share matched, x, y): where the design's corner falls in the frame, by its mask's bronze and lights (the
    pasted faceplate; the hood and the outline round it are Codex's own in every frame), searched round the lights."""
    x0, y0, x1, y1 = box
    tpl = fig[y0:y1 + 1, x0:x1 + 1]
    m = np.zeros(tpl.shape[:2], bool)
    for y, x in zip(*np.nonzero(tpl[..., 3] > 0)):
        m[y, x] = tuple(int(v) for v in tpl[y, x, :3]) in MASK_COLOURS
    ey, ex = np.nonzero(eyes(frame))
    if not len(ey):
        return 0.0, 0, 0
    dy, dx = np.nonzero(eyes(fig))
    best = (0.0, 0, 0)
    for oy in range(-2, 3):
        for ox in range(-2, 3):
            hx, hy = int(ex.min()) - int(dx.min()) + ox, int(ey.min()) - int(dy.min()) + oy
            if hy + y0 < 0 or hx + x0 < 0 or hy + y1 >= frame.shape[0] or hx + x1 >= frame.shape[1]:
                continue
            s = ((frame[hy + y0:hy + y1 + 1, hx + x0:hx + x1 + 1] == tpl).all(-1) & m).sum() / m.sum()
            if s > best[0]:
                best = (float(s), hx, hy)
    return best


def is_design(frame, fig):
    """The design's corner in the frame if the frame is the design (an idle frame), else None."""
    f, (x, y) = ST.figure(frame)
    if f.shape == fig.shape and (f == fig).all():
        return x, y
    return None


def penalties(frame, soles):
    """Per pixel: what a deleted line pays for it (PENALTY by colour, FOOT_PENALTY over the feet rows)."""
    pen = np.zeros(frame.shape[:2])
    op = frame[..., 3] > 0
    for c, v in PENALTY.items():
        pen[op & (frame[..., :3] == np.array(c, np.uint8)).all(-1)] = v
    if soles is not None:
        pen[max(0, soles - FEET):soles + 1][op[max(0, soles - FEET):soles + 1]] += FOOT_PENALTY
    return pen


def group_cuts(idx, w, pen, axis, lo, hi, k, prefer, banned=()):
    """k lines among lo..hi (inclusive) along axis (0 rows, 1 columns), one in each of k equal stretches - a long
    thin thing (the lamppost's shaft, the plume) loses its share, not all k - each the cheapest there: its weighted
    difference from the nearer neighbour, the penalties on it, PRIOR per line from the design's own choice; never a
    banned line, never next to one already taken."""
    if k <= 0 or hi < lo:
        return []
    lines = [idx[i] if axis == 0 else idx[:, i] for i in range(idx.shape[axis])]
    wts = [w[i] if axis == 0 else w[:, i] for i in range(idx.shape[axis])]
    span = list(range(lo, hi + 1))
    k = min(k, (len(span) + 1) // 2)
    cost = {i: ST.line_cost(lines, wts, i) + float((pen[i] if axis == 0 else pen[:, i]).sum()) +
            (ST.PRIOR * min(min(abs(i - p) for p in prefer), 5) if prefer else 0.0) for i in span}
    bounds = [lo + round(j * len(span) / k) for j in range(k + 1)]
    out = []
    for j in range(k):
        free = [i for i in span if i not in banned and i not in out and all(abs(i - o) > 1 for o in out)]
        here = [i for i in free if bounds[j] <= i < bounds[j + 1]] or free
        if not here:
            break
        out.append(min(here, key=lambda i: cost[i]))
    return sorted(out)


def ratio(n, length, cuts, further):
    """Deletions for n lines where the design has `cuts` in `length`: its share up to its reach, `further` past it."""
    return round(min(n, length) * cuts / length) + round(max(0, n - length) * further)


def frame_cuts(frame, fig, box, drow, dcol, pivot, pal):
    """(rows, columns) of a 96x96 frame to delete, and how they were found."""
    idx, w = index(frame, pal)
    H, W = fig.shape[:2]
    rows_f, cols_f = len(drow) / H, len(dcol) / W
    soles = pivot[1] + SOLES
    ys, xs = np.nonzero(idx >= 0)
    top, low, left, right = int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())
    edge_r, edge_c = {top, low}, {left, right}
    at = is_design(frame, fig)
    if at is not None:                                            # the idle: exactly the design's lines
        return [at[1] + r for r in drow], [at[0] + c for c in dcol], "the design"
    standing = low >= soles - 1
    pen = penalties(frame, soles if standing else None)
    share, hx, hy = find_mask(frame, fig, box)
    feet = set(range(soles - FEET, soles + 1)) if standing else set()
    if share < FOUND:                                             # lying down, no lights: the design's share
        rows = group_cuts(idx, w, pen, 0, top, low, round((low - top + 1) * rows_f), [], edge_r | feet)
        cols = group_cuts(idx, w, pen, 1, left, right, round((right - left + 1) * cols_f), [], edge_c)
        return rows, cols, "no mask"
    x0, y0, x1, y1 = box
    mt, mb, ml, mr = hy + y0, hy + y1, hx + x0, hx + x1          # the mask in the frame: never cut
    rows, cols = [], []
    # over the mask: the hood and the plume (and the lamppost raised over them)
    above = [r for r in drow if r < y0]
    if top < mt:
        k = ratio(mt - top, y0, len(above), rows_f)
        rows += group_cuts(idx, w, pen, 0, top, mt - 1, k, [hy + r for r in above], edge_r)
    # under the mask down to the feet (in the air: down to the figure's lowest row less the feet's rows)
    below = [r for r in drow if y1 < r < H - 1 - FEET]
    lo, hi = mb + 1, min(soles, low) - FEET - 1
    if hi >= lo:
        length = (H - 1 - FEET) - (y1 + 1)
        k = ratio(hi - lo + 1, length, len(below), rows_f)
        rows += group_cuts(idx, w, pen, 0, lo, hi, k, [hy + r for r in below], edge_r | feet)
    # left of the mask: the hood's back, the cape, the lamppost's hook
    lefts = [c for c in dcol if c < x0]
    if left < ml:
        k = ratio(ml - left, x0, len(lefts), cols_f)
        cols += group_cuts(idx, w, pen, 1, left, ml - 1, k, [hx + c for c in lefts], edge_c)
    # right of the mask: the arm, the lamppost, the lantern
    rights = [c for c in dcol if c > x1]
    if right > mr:
        k = ratio(right - mr, W - 1 - x1, len(rights), cols_f)
        cols += group_cuts(idx, w, pen, 1, mr + 1, right, k, [hx + c for c in rights], edge_c)
    return sorted(set(rows)), sorted(set(cols)), f"mask {share:4.0%} at ({hx:3d},{hy:3d})"


def recolour(a):
    """RECOLOUR on an RGBA picture (exact colours; the rest as it is)."""
    out = a.copy()
    op = a[..., 3] > 0
    for src, dst in RECOLOUR.items():
        s = np.array([int(src[i:i + 2], 16) for i in (0, 2, 4)], np.uint8)
        m = op & (a[..., :3] == s).all(-1)
        out[m, :3] = [int(dst[i:i + 2], 16) for i in (0, 2, 4)]
    return out


def cut(a, rows, cols, pivot):
    """The frame without those rows and columns, the outline put back where a deleted line held it, on its pivot."""
    H, W = a.shape[:2]
    kr = [y for y in range(H) if y not in rows]
    kc = [x for x in range(W) if x not in cols]
    small = a[np.ix_(kr, kc)].copy()
    soles = pivot[1] + SOLES
    out = small.copy()
    for y, x in zip(*np.nonzero(small[..., 3] > 0)):
        oy, ox = kr[y], kc[x]
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if not (0 <= ny < small.shape[0] and 0 <= nx < small.shape[1]) or small[ny, nx, 3] > 0 or out[ny, nx, 3] > 0:
                continue
            if kr[ny] > soles:
                continue
            py, px = oy + dy, ox + dx                    # the original neighbour, maybe on a deleted line
            if (py in rows or px in cols) and 0 <= py < H and 0 <= px < W and a[py, px, 3] > 0 \
                    and tuple(int(v) for v in a[py, px, :3]) in OUTLINES:
                out[ny, nx] = a[py, px]
    sy = sum(1 for r in rows if r < soles)               # back on the pivot: the soles on their row
    sx = sum(1 for c in cols if c < pivot[0])            # and the pivot column where it was
    res = np.zeros_like(a)
    oh, ow = out.shape[:2]
    res[sy:sy + oh, sx:sx + ow] = out[:H - sy, :W - sx]
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="compare with the files instead of writing them")
    ap.add_argument("--review", help="write the frames before/after side by side to this folder")
    o = ap.parse_args()
    names = ["jax_native.png"] + [f"jax_{t}.png" for t in TAGS]
    if not os.path.exists(D.lp(os.path.join(SRC, "jax_native.png"))):
        os.makedirs(D.lp(SRC), exist_ok=True)
        for name in names:
            shutil.copyfile(D.lp(os.path.join(OUT, name)), D.lp(os.path.join(SRC, name)))
        print("the 41-row design and strips copied to", SRC)
    big = blocks(os.path.join(SRC, "jax_native.png"))
    fig, corner = ST.figure(big)
    box = mask_box(fig)
    drow, dcol = design_cuts(fig, box)
    print(f"design {fig.shape[1]}x{fig.shape[0]}, mask {box}: rows {drow}, columns {dcol}")
    with open(CELLS, encoding="utf-8") as f:
        spec = json.load(f)
    cell = tuple(spec["cell"])
    pal = {}
    written = []
    for tag in TAGS:
        table = spec["tags"][tag]
        frames, grid = ST.strip_frames(os.path.join(SRC, f"jax_{tag}.png"), len(table), cell)
        new = []
        for k, (fr, row) in enumerate(zip(frames, table)):
            rows, cols, how = frame_cuts(fr, fig, box, drow, dcol, row["pivot"], pal)
            new.append(cut(fr, rows, cols, row["pivot"]))
            print(f"  {tag:12s} {k + 1}: {how}  rows -{len(rows)} {rows}  columns -{len(cols)} {cols}")
        if tag == "idle":
            feet = np.nonzero(fig[-1, :, 3] > 0)[0]                    # the stance's middle stays where it was
            mid = (int(feet.min()) + int(feet.max()) + 1) // 2
            canvas, sfig = ST.design_canvas(new[0], (corner[0] + sum(1 for c in dcol if c < mid),
                                                     corner[1] + len(drow)), big.shape[0])
            print(f"design at {HEIGHT}: {sfig.shape[1]}x{sfig.shape[0]}")
            written.append(("jax_native.png", recolour(canvas)))
        written.append((f"jax_{tag}.png", recolour(ST.to_strip(new, grid, cell))))
        if o.review:
            ST.review(frames, new, os.path.join(o.review, f"jax_{tag}_36.png"))
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
