#!/usr/bin/env python3
"""The idle as a breath drawn from the design's own pixels (import_native.py runs it last on every hero's idle).

Players saw the pack in ban/pick 「清一色的不动 不然就是动两个像素点」: the idles were the design six times with a 1-row bob
at 1.2 s, 14 of them still. Image-model redraws (skin swaps on oppi's idles) moved, but every frame was a new drawing:
specks in the armour, swords and capes changing shape, the loop jumping (the user: 「模型有变形和不干净的地方」). Here every
frame is the design itself:
- the body breathes down and up, BODY rows over 8 frames on a sine (0 0 1 2 2 2 1 0), by removing rows through the
  thighs - horizontal seams (a row per column, neighbouring columns at most a row apart) where the colours repeat most,
  so a straight shaft or a flat area loses a row unseen and nothing below the knees ever moves;
- the body leans a column forward as it sinks (a step at one row of the thighs, where it shows least), as oppi's
  idles lean 1-2 columns with the breath (the user: 「左右摇摆也可以加 反正你得调到完美」);
- the head (hair, skin and eyes grown from the head point, with its outline ring) follows a frame late as one piece,
  so it nods against the body; the neck it uncovers is the row under it drawn up.
The user approved this on Garen and Darius (「对 很不错」, 2026-10-08).
"""
import numpy as np

BODY = [0, 0, 1, 2, 2, 2, 1, 0]     # rows the body is down per frame
LAG = 1                             # frames the head is late
SWAY = [0, 0, 0, 1, 1, 1, 0, 0]     # columns the body leans forward with the breath (oppi's lean 1-2, in phase)
MS = 110


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def cost_rows(a, lo, hi):
    """Cost of removing row y at column x (merging rows y and y+1): colour change, an opacity change counting double."""
    op = a[..., 3] > 0
    c = np.zeros((hi - lo + 1, a.shape[1]))
    for i, y in enumerate(range(lo, hi + 1)):
        same_op = op[y] & op[y + 1]
        diff = (np.abs(a[y, :, :3].astype(int) - a[y + 1, :, :3]).sum(-1) > 0) & same_op
        c[i] = diff * 1.0 + (op[y] != op[y + 1]) * 2.0
    return c


def seam(c):
    """The cheapest horizontal path through the cost rows: a row index per column, neighbours at most 1 apart."""
    R, W = c.shape
    acc = c.copy()
    back = np.zeros((R, W), int)
    for x in range(1, W):
        for r in range(R):
            lo, hi = max(0, r - 1), min(R, r + 2)
            k = int(np.argmin(acc[lo:hi, x - 1])) + lo
            back[r, x] = k
            acc[r, x] += acc[k, x - 1] + 0.01 * abs(k - r)
    r = int(np.argmin(acc[:, -1]))
    path = [r]
    for x in range(W - 1, 0, -1):
        r = back[r, x]
        path.append(r)
    return path[::-1]


def remove(a, path, lo):
    """Delete the seam's pixel in every column: the column above it slides down a row."""
    b = a.copy()
    for x in range(a.shape[1]):
        s = lo + path[x]
        b[1:s + 1, x] = a[0:s, x]
        b[0, x] = 0
    return b


def lean(a, dx, lo, hi):
    """Everything above one row of the thighs moves dx columns (forward +): the row where the step shows least (the
    shifted row above matches the row under it best), so the hips go with the body and the feet stay."""
    if not dx:
        return a, None
    op = a[..., 3] > 0
    best = None
    for y in range(lo, hi + 1):
        up = np.roll(a[y], dx, axis=0)
        uo = np.roll(op[y], dx)
        lo_ = op[y + 1]
        cost = int((uo != lo_).sum()) + int((uo & lo_ & (np.abs(up[:, :3].astype(int) - a[y + 1, :, :3]).sum(-1) > 0)).sum())
        if best is None or cost < best[0]:
            best = (cost, y)
    y = best[1]
    b = a.copy()
    b[:y + 1] = np.roll(a[:y + 1], dx, axis=1)
    return b, y


def head_box(a, head):
    """(hx, hy, crown, chin, half) from the head point; the crown searched up its column, at most 14 rows."""
    hx, hy = head
    col = a[:int(hy), int(round(hx)), 3] > 0
    tops = np.nonzero(col)[0]
    crown = int(tops.min()) if len(tops) else int(hy) - 8
    crown = max(crown, int(hy) - 14)
    r = max(4.0, hy - crown)
    return hx, hy, crown, int(round(hy + 0.45 * r)), int(round(0.75 * r))


def head_piece(a, hx, hy, crown, chin, half):
    """The head as one piece: above the head point everything in the head box (the hair), below it the colours found
    round the head point (skin, eyes), grown from the point; plus the outline squares that ring it."""
    H, W = a.shape[:2]
    op = a[..., 3] > 0
    r = hy - crown
    core = set()
    for y in range(int(crown), int(hy) + 1):
        for x in range(int(hx - 0.6 * r), int(hx + 0.6 * r) + 1):
            if 0 <= y < H and 0 <= x < W and op[y, x]:
                core.add(tuple(int(v) for v in a[y, x, :3]))
    if not core:
        return np.zeros(op.shape, bool)
    dark = min(core, key=lum)
    core.discard(dark)                                       # the outline colour joins only as the ring
    y0, y1 = max(0, crown - 1), min(H, chin + 1)
    x0, x1 = max(0, int(hx) - half - 1), min(W, int(hx) + half + 2)
    ok = np.zeros(op.shape, bool)
    for y in range(y0, y1):
        for x in range(x0, x1):
            ok[y, x] = op[y, x] and (y <= hy - 3 or tuple(int(v) for v in a[y, x, :3]) in core)
    m = np.zeros(op.shape, bool)
    sy, sx = int(round(hy)), int(round(hx))
    if not ok[sy, sx]:                                       # the point on an outline or a gap: the nearest head square
        near = [(abs(y - sy) + abs(x - sx), y, x) for y, x in zip(*np.nonzero(ok)) if abs(y - sy) <= 4 and abs(x - sx) <= 4]
        if not near:
            return np.zeros(op.shape, bool)
        _, sy, sx = min(near)
    st = [(sy, sx)]
    while st:
        y, x = st.pop()
        if not (y0 <= y < y1 and x0 <= x < x1) or m[y, x] or not ok[y, x]:
            continue
        m[y, x] = True
        st += [(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)]
    ring = np.zeros_like(m)
    for y, x in zip(*np.nonzero(m)):
        for ny in (y - 1, y, y + 1):
            for nx in (x - 1, x, x + 1):
                if 0 <= ny < H and 0 <= nx < W and op[ny, nx] and not m[ny, nx] and ny < chin and \
                        tuple(int(v) for v in a[ny, nx, :3]) == dark:
                    ring[ny, nx] = True
    return m | ring


def move_piece(a, m, dy):
    """Move the masked piece dy rows (down +); when it rises, the squares it leaves at its foot take the pixel under."""
    b = a.copy()
    ys, xs = np.nonzero(m)
    b[ys, xs] = 0
    if dy < 0:
        for x in set(xs.tolist()):
            low = ys[xs == x].max()
            if low + 1 < a.shape[0] and a[low + 1, x, 3]:
                for y in range(low, low + dy, -1):
                    b[y, x] = a[low + 1, x]
    b[ys + dy, xs] = a[ys, xs]
    return b


def pieces(op):
    labs = np.zeros(op.shape, int)
    n = 0
    for y, x in zip(*np.nonzero(op)):
        if labs[y, x]:
            continue
        n += 1
        st = [(y, x)]
        labs[y, x] = n
        while st:
            cy, cx = st.pop()
            for ny in (cy - 1, cy, cy + 1):
                for nx in (cx - 1, cx, cx + 1):
                    if 0 <= ny < op.shape[0] and 0 <= nx < op.shape[1] and op[ny, nx] and not labs[ny, nx]:
                        labs[ny, nx] = n
                        st.append((ny, nx))
    return labs, n


def breathe(design, head, body=BODY, lag=LAG, nod=True, sway=SWAY):
    """8 frames from one design frame: (frames, the head piece). head = (x, y) head point in the frame's coordinates.
    The frames come 2 squares bigger all round (a pivot-centred frame stays centred), so the lean is never cut."""
    design = np.pad(design, ((2, 2), (2, 2), (0, 0)))
    head = (head[0] + 2, head[1] + 2)
    ys, xs = np.nonzero(design[..., 3])
    sole = ys.max()
    hx, hy, crown, chin, half = head_box(design, head)
    h = sole - crown + 1
    lo, hi = int(sole - 0.45 * h), int(sole - 0.15 * h)
    piece = head_piece(design, hx, hy, crown, chin, half) if nod else np.zeros(design.shape[:2], bool)
    base_pieces = pieces(design[..., 3] > 0)[1]
    out = []
    n = len(body)
    for k in range(n):
        a = design.copy()
        d = body[k]
        for _ in range(d):
            a = remove(a, seam(cost_rows(a, lo, hi)), lo)
        dx = sway[k]
        a, _ = lean(a, dx, lo + d, hi + d)
        rel = body[(k - lag) % n] - d
        if rel and piece.any():
            m = np.zeros_like(piece)
            py, px = np.nonzero(piece)
            m[py + d, px + dx] = True
            a = move_piece(a, m, rel)
        labs, nn = pieces(a[..., 3] > 0)
        if nn > base_pieces:                                 # squares the head left behind
            for i in range(1, nn + 1):
                if (labs == i).sum() <= 3:
                    a[labs == i] = 0
        out.append(a)
    return out, piece
