#!/usr/bin/env python3
"""The idle as a breath drawn from the design's own pixels (import_native.py runs it last on every hero's idle).

Players saw the pack in ban/pick 「清一色的不动 不然就是动两个像素点」; image-model redraws moved but deformed (「模型有变形和
不干净的地方」). This is the base game's own recipe, measured on its 78 sprites: the whole figure above the shins
translates rigidly 0-1-2 rows down and back over the cycle, the shins swallow the rows, the feet never move. Deformation
in the first two attempts came from cutting too high (thigh seams stepped through Evelynn's lashers and Fiora's legs),
from re-choosing the cut per frame (swords and fists popped), and from a 110 ms cadence with something moving in six of
eight transitions (dithered hair shimmered, Fiora's thin rapier flapped; the user: 「魔性变形」「还是有点不自然」). So here:
- every cut is chosen ONCE for the loop, straight across each connected shape of the cut zone, and only where removing
  the row is invisible or nearly so: the row equals the row under it (the cost report prints any shape above 0);
- the cut zone is the bottom 10-30% of the figure (the shins, as in the base game): above it everything - hips, props,
  hair - moves as one rigid piece, so nothing bends;
- the body sinks 0 0 1 2 2 2 1 0 over 8 x 140 ms (1.12 s, the base game's pace); the head and all it carries follow a
  frame late through one near-invisible row under the chin (the nod the user approved on Garen and Darius); the lean
  (「左右摇摆也可以加」) is a 1-column weight shift hinged on the lowest shin row, below both cut rows.
"""
import numpy as np

BODY = [0, 0, 1, 2, 2, 2, 1, 0]     # rows the body is down per frame
LAG = 1                             # frames the head is late
SWAY = [0, 0, 0, 0, 1, 1, 1, 0]     # columns the body leans forward, a frame after the dip (the weight settles)
MS = 140


def merge_cost(a, lo, hi, feet=None):
    """(rows lo..hi) x columns: the visible pixels of taking row y out (rows y and y+1 meet): a colour change or an
    opacity change there, and 100 from row `feet` down in the columns standing on the soles' row (never cut a foot)."""
    op = a[..., 3] > 0
    c = np.zeros((hi - lo + 1, a.shape[1]))
    sole = int(np.nonzero(op.any(1))[0].max())
    standing = op[sole]
    for i, y in enumerate(range(lo, hi + 1)):
        same = op[y] & op[y + 1]
        diff = (np.abs(a[y, :, :3].astype(int) - a[y + 1, :, :3]).sum(-1) > 0) & same
        c[i] = diff * 1.0 + (op[y] != op[y + 1]) * 2.0
        if feet is not None and y + 1 >= feet:
            c[i] += (op[y] | op[y + 1]) * standing * 100.0
    return c


def step_cost(a, lo, hi, dx):
    """(rows lo..hi) x columns: the visible pixels of a dx-column step between row y (moved) and row y+1 (kept)."""
    op = a[..., 3] > 0
    c = np.zeros((hi - lo + 1, a.shape[1]))
    for i, y in enumerate(range(lo, hi + 1)):
        up, uo = np.roll(a[y], dx, axis=0), np.roll(op[y], dx)
        same = uo & op[y + 1]
        c[i] = (uo != op[y + 1]) * 1.0 + (same & (np.abs(up[:, :3].astype(int) - a[y + 1, :, :3]).sum(-1) > 0)) * 1.0
    return c


def groups(a, lo, hi):
    """Column groups of the band rows lo..hi: shapes (8-connected inside the band) whose columns overlap are one group.
    A list of column arrays; columns with nothing in the band belong to no group."""
    op = a[lo:hi + 1, :, 3] > 0
    H, W = op.shape
    lab = np.zeros(op.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
    cols = [set(np.nonzero((lab == i).any(0))[0].tolist()) for i in range(1, n + 1)]
    merged = []
    for c in cols:
        for m in [m for m in merged if m & c]:
            merged.remove(m)
            c = c | m
        merged.append(c)
    return [np.array(sorted(m)) for m in merged]


def pick(cost, gs, lo, k, W, gap=2):
    """Per column, k rows (cheapest first; rows at least `gap` apart) straight across each group; (rows, worst group
    cost). Columns in no group take the band's lowest row (nothing there: free)."""
    rows = np.full((k, W), lo + cost.shape[0] - 1, int)
    worst = 0.0
    for g in gs:
        tot = cost[:, g].sum(1)
        order = list(np.argsort(tot, kind="stable"))
        chosen = []
        for r in order:
            if all(abs(r - c) >= gap for c in chosen):
                chosen.append(r)
            if len(chosen) == k:
                break
        while len(chosen) < k:
            chosen.append(chosen[-1])
        worst = max(worst, float(tot[chosen[k - 1]]))
        for j, r in enumerate(chosen):
            rows[j, g] = lo + r
    return rows, worst


def take_out(a, rows):
    """Take out, in every column x, the rows in rows[:, x] (frame rows): what is above slides down."""
    b = a.copy()
    for x in range(a.shape[1]):
        col = a[:, x].copy()
        for r in sorted(rows[:, x].tolist()):                # highest first: the lower ones keep their index
            col[1:r + 1] = col[0:r].copy()
            col[0] = 0
        b[:, x] = col
    return b


def double(a, rows):
    """Double, in every column x, the row rows[x]: what is above rises a row."""
    b = a.copy()
    for x in range(a.shape[1]):
        r = rows[x]
        b[0:r, x] = a[1:r + 1, x]
    return b


def shift_over(a, rows, dx):
    """In every column x, everything at or over row rows[x] moves dx columns (forward +)."""
    b = a.copy()
    W = a.shape[1]
    for x in range(W):
        sx = x - dx
        r = rows[x]
        b[:r + 1, x] = a[:r + 1, sx] if 0 <= sx < W else 0
    return b


def head_box(a, head):
    """(hx, hy, crown) from the head point; the crown searched up its column, at most 14 rows."""
    hx, hy = head
    col = a[:int(hy), int(round(hx)), 3] > 0
    tops = np.nonzero(col)[0]
    crown = int(tops.min()) if len(tops) else int(hy) - 8
    return hx, hy, max(crown, int(hy) - 14)


def pieces(op):
    lab = np.zeros(op.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if lab[y, x]:
            continue
        n += 1
        st = [(y, x)]
        lab[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n
                        st.append((ny, nx))
    return lab, n


def breathe(design, head, body=BODY, lag=LAG, nod=True, sway=SWAY, nod_max=6.0, zone=(0.30, 2), **_):
    """8 frames from one design frame: (frames, report). head = (x, y) head point in the frame's coordinates.
    The frames come 2 squares bigger all round (a pivot-centred frame stays centred), so the lean is never cut."""
    a0 = np.pad(design, ((2, 2), (2, 2), (0, 0)))
    head = (head[0] + 2, head[1] + 2)
    op = a0[..., 3] > 0
    ys = np.nonzero(op.any(1))[0]
    top, sole = int(ys.min()), int(ys.max())
    W = a0.shape[1]
    hx, hy, crown = head_box(a0, head)
    h = sole - top + 1
    r = max(4.0, hy - crown)
    # the cut zone: the shins, the bottom 10-30% of the figure (the base game cuts there); feet protected. Alistar's
    # flat dark belt was the cheapest row of the default zone, so only his hump breathed while the fists stood
    # (「牛头有点怪」): his zone is forced into the legs, zone=(0.20, 1)
    lo, hi = int(sole - zone[0] * h), sole - zone[1]
    dip, dip_cost = pick(merge_cost(a0, lo, hi, feet=sole - 3), groups(a0, lo, hi), lo, 2, W)
    # the lean's hinge, per group: a standing shape (feet on the soles' row) hinges at the ankle - below its own cut
    # rows, above the boot's last two rows; a hanging shape (a fist, a tail off the ground) moves whole (hinge = sole)
    standing = op[sole]
    sc = step_cost(a0, lo, sole - 1, 1)
    lean = np.full(W, sole, int)                             # a hanging column moves whole, down to its last pixel
    lean_cost = 0.0
    for g in groups(a0, lo, sole - 1):
        gs = g[standing[g]]                                  # the hinge binds only the columns standing on the soles
        if not len(gs):
            continue
        gd = int(dip[:, gs].max())                           # below this group's own cuts in those columns
        llo, lhi = max(gd + 1, lo), sole - 3                 # the boot's last two rows never shift
        if llo > lhi:
            llo = lhi = sole - 3
        cand = sc[llo - lo:lhi - lo + 1, gs].sum(1)
        r = int(np.argmin(cand)) + llo
        lean[gs] = r
        lean_cost = max(lean_cost, float(cand.min()))
    # the nod's row: just under the chin (3-8 rows under the eyes; a ponytail above the crown must not widen it)
    nlo, nhi = int(round(hy + 3)), min(int(round(hy + 8)), lo - 3)
    neck = neck_cost = None
    if nod and nhi > nlo:
        neck, neck_cost = pick(merge_cost(a0, nlo, nhi), groups(a0, nlo, nhi), nlo, 1, W)
        neck = neck[0]
        if neck_cost > nod_max:                              # a nod that would dent the collar: leave the head rigid
            neck = None
    out = []
    n = len(body)
    for k in range(n):
        a = a0.copy()
        rel = body[(k - lag) % n] - body[k]
        if neck is not None and rel:                         # the head's row first: it lies over everything else
            a = take_out(a, neck[None, :]) if rel > 0 else double(a, neck)
        d = body[k]
        if d:
            a = take_out(a, dip[:d])
        if sway[k]:
            a = shift_over(a, lean, sway[k])                 # the hinge is below the cuts: its row has not moved
        out.append(a)
    return out, dict(dip=dip, dip_cost=dip_cost, lean_cost=lean_cost, neck=neck, neck_cost=neck_cost)
