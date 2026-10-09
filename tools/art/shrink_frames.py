#!/usr/bin/env python3
"""Make a finished hero smaller without resampling: whole rows and columns are taken out, never anything blended.

Players found league_xinzhao, league_xerath, league_samira and league_sivir too big (2026-10-08). A resample of the
frames (each new square the majority of the old squares it covers) lost details - Xin Zhao's hand went, a black line
ran down Sivir's middle (the user: 「不要丢失细节 赵兴手就没你弄没了 希维尔缩小后中间一条黑线」). Here a square is
never invented or merged: of every ten rows (and columns) of the body one is taken out, the one that is the most like
its neighbour - a row repeated in a robe or a leg goes, the rows that carry a hand, an eye, an outline that turns,
anything one square thick, differ from both neighbours and stay; and a line that crosses a small single-colour
piece (a hand, an eye, a gem: at most DETAIL squares) costs DETAIL_WEIGHT more per square of it (the user, after the
first try: 「赵兴的手还是丢失了啊」 - a line through his hand on the spear had been cheap, the shaft runs on both sides). One choice per action for all its frames (summed
over them, aligned on the pivot), so a body part keeps its shape from frame to frame. The soles stay on their row:
rows go only above them and everything over a removed row moves down one; columns go on both sides of the pivot and
the halves close in on it.

    import shrink_frames as SF
    plans = SF.shrink_sheet(sheet, 0.9)      # {tag: [(frame centred on its pivot, ms)]}, changed in place
    SF.move_point(plans["idle"], dx, dy)     # a point (from the pivot) after the shrink

Used by import_native.py (SHRINK) as its last step before the sheet is written.
"""
import numpy as np

import strips as G


def _canvas(frames):
    """The frames on one canvas each, pivot at (H, W): (stack, H, W)."""
    H = max(a.shape[0] // 2 for a, _ in frames)
    W = max(a.shape[1] // 2 for a, _ in frames)
    st = np.zeros((len(frames), 2 * H + 1, 2 * W + 1, 4), np.uint8)
    for k, (a, _) in enumerate(frames):
        h, w = a.shape[0] // 2, a.shape[1] // 2
        st[k, H - h:H + h + 1, W - w:W + w + 1] = a
    return st, H, W


def _diff(st, axis):
    """cost[i]: squares where line i differs from line i - 1 (rows: axis 1, columns: axis 2), over all frames; the
    cheaper of the two neighbours, as a line equal to either neighbour goes without loss."""
    a = st.astype(np.int16)
    op = a[..., 3] > 0
    n = st.shape[axis]
    prev = np.full(n, 10 ** 9)
    for i in range(1, n):
        x, y = np.take(a, i, axis), np.take(a, i - 1, axis)
        ox, oy = np.take(op, i, axis), np.take(op, i - 1, axis)
        prev[i] = int(((ox | oy) & ((x != y).any(-1))).sum())
    nxt = np.append(prev[1:], 10 ** 9)
    return np.minimum(prev, nxt)


DETAIL = 16          # a single-colour piece this small (a hand, an eye, a gem, a buckle) is a detail
DETAIL_WEIGHT = 40   # what one of its squares adds to the cost of the line through it


def _details(st):
    """Per frame, the squares of small single-colour pieces (4-connected, at most DETAIL squares; not the darkest
    colour, the outline, which runs everywhere): a line through them takes a square off a hand or an eye."""
    out = np.zeros(st.shape[:3], bool)
    for k in range(st.shape[0]):
        a = st[k]
        op = a[..., 3] > 0
        if not op.any():
            continue
        key = (a[..., 0].astype(np.int32) << 16) | (a[..., 1].astype(np.int32) << 8) | a[..., 2]
        dark = int(key[op][np.argmin(a[..., :3][op].astype(int).sum(-1))])
        seen = np.zeros(op.shape, bool)
        Hh, Ww = op.shape
        for y, x in zip(*np.nonzero(op)):
            if seen[y, x] or key[y, x] == dark:
                continue
            c = key[y, x]
            stack, piece = [(y, x)], []
            seen[y, x] = True
            while stack:
                v, u = stack.pop()
                piece.append((v, u))
                if len(piece) > DETAIL:
                    break
                for dv, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q, w = v + dv, u + du
                    if 0 <= q < Hh and 0 <= w < Ww and not seen[q, w] and op[q, w] and key[q, w] == c:
                        seen[q, w] = True
                        stack.append((q, w))
            if len(piece) <= DETAIL and not stack:
                for v, u in piece:
                    out[k, v, u] = True
    return out


def _kept(st, colours, limit=10):
    """Per frame, the squares no removed line may cross while its stretch has another: small pieces (at most `limit`,
    4-connected) in the hero's skin colours - hands and fingers - and, for colours written "!RRGGBB" (eyes, lips),
    the whole box from the first to the last of them - the face from the eyes to the mouth."""
    out = np.zeros(st.shape[:3], bool)
    if not colours:
        return out
    face, margin = [], (0, 0, 0, 0)
    for h in [h for h in colours if h.startswith("#")]:
        # "#RRGGBB>AABBCC,DDEEFF": squares of RRGGBB with one of the others right above AND below - Samira's knee
        # bands (red between the trouser greens; the sash is the same red but sits on skin and black): a cut
        # through a band in the run's rebuilt legs bent the leg (「腿变形了」)
        col, _, between = h[1:].partition(">")
        c = tuple(int(col[i:i + 2], 16) for i in (0, 2, 4))
        mids = [tuple(int(m[i:i + 2], 16) for i in (0, 2, 4)) for m in between.split(",") if m]
        for k in range(st.shape[0]):
            a = st[k]
            m = (a[..., 3] > 0) & (a[..., :3] == c).all(-1)
            if mids:
                env = np.zeros(a.shape[:2], bool)
                for mc in mids:
                    env |= (a[..., :3] == mc).all(-1) & (a[..., 3] > 0)
                up, down = np.zeros_like(env), np.zeros_like(env)
                up[1:] = env[:-1]
                down[:-1] = env[1:]
                m &= up & down
            out[k] |= m
    colours = [h for h in colours if not h.startswith("#") and not h.startswith("=")]
    for h in colours:
        if h.startswith("!"):
            hexs, _, m = h[1:].partition("+")              # "!RRGGBB+up,down,left,right": the box grown by that
            face.append(tuple(int(hexs[i:i + 2], 16) for i in (0, 2, 4)))
            if m:
                margin = tuple(int(v) for v in m.split(","))
    colours = [h for h in colours if not h.startswith("!")]
    for k in range(st.shape[0]):                       # the face: every line from the eyes to the mouth
        m = np.zeros(st.shape[1:3], bool)
        for c in face:
            m |= (st[k][..., 3] > 0) & (st[k][..., :3] == c).all(-1)
        if m.any():
            ys, xs = np.nonzero(m)
            up, down, left, right = margin
            out[k, max(ys.min() - up, 0):ys.max() + 1 + down, max(xs.min() - left, 0):xs.max() + 1 + right] = True
    rgb = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in colours]
    for k in range(st.shape[0]):
        a = st[k]
        sk = np.zeros(a.shape[:2], bool)
        for c in rgb:
            sk |= (a[..., 3] > 0) & (a[..., :3] == c).all(-1)
        seen = np.zeros(sk.shape, bool)
        for y, x in zip(*np.nonzero(sk)):
            if seen[y, x]:
                continue
            stack, piece = [(y, x)], []
            seen[y, x] = True
            while stack:
                v, u = stack.pop()
                piece.append((v, u))
                for dv, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q, w = v + dv, u + du
                    if 0 <= q < sk.shape[0] and 0 <= w < sk.shape[1] and sk[q, w] and not seen[q, w]:
                        seen[q, w] = True
                        stack.append((q, w))
            if len(piece) <= limit:
                for v, u in piece:
                    out[k, v, u] = True
    return out


def _pick(cost, lo, hi, k, avoid=(), keep=None):
    """k lines in [lo, hi), one in each of k equal stretches: the cheapest there (no two side by side)."""
    out = []
    lo, hi = max(lo, 1), min(hi, len(cost))              # a small action's canvas may not reach the idle's edges
    if k <= 0 or hi - lo < 2:
        return out
    edges = np.linspace(lo, hi, k + 1)
    for s in range(k):
        a, b = int(round(edges[s])), int(round(edges[s + 1]))
        cand = [i for i in range(a, b) if i not in avoid and (i - 1) not in out and (i + 1) not in out]
        if cand:
            # the line crossing the fewest kept squares (none, as a rule), then the cheapest
            k_ = (lambda i: int(keep[i])) if keep is not None else (lambda i: 0)
            out.append(min(cand, key=lambda i: (k_(i), cost[i], abs(i - (a + b) / 2))))
    # (a stretch's pick that crosses kept squares is moved by plan_tag's move_off - by the HARD keep only and to
    # the nearest free line: moving it here by the soft keep to the cheapest line anywhere sent every head and
    # torso row down to the legs, where nothing is kept - Samira's 「太怪了」)
    return out


def plan_tag(frames, body, scale, keep_colours=(), edge_rows=(), edge_cols=(), hard_frames=None, shifts=None):
    """The rows and columns (canvas lines, from the pivot) the hero loses. body = (top, bottom, left, right) of the
    idle's body from the pivot (bottom = the soles' row): of its rows and columns 1 - scale go; of what lies beyond
    it (a raised or held-out weapon) the same share. One plan serves every action (shrink_sheet passes all their
    frames together), so the body loses the same lines in each - an action one row taller than the idle would pop at
    every animation change. edge_rows / edge_cols: every action's own outermost two lines (pivot-relative), kept.
    shifts: per frame (dy, dx) of the body against the action's first frame (anchor_shifts): the lines are chosen on
    the frames moved back onto the first and removed at that much offset in each, so every frame loses the same lines
    of HIM, not of the canvas."""
    st, H, W = _canvas(frames)
    if shifts is not None:
        st = np.stack([_moved(f, -dy, -dx) for f, (dy, dx) in zip(st, shifts)])
    occ = (st[..., 3] > 0).any(0)
    rows, cols = np.nonzero(occ.any(1))[0], np.nonzero(occ.any(0))[0]
    top, bottom, left, right = body
    cut = 1 - scale
    det = _details(st)
    rc = _diff(st, 1) + DETAIL_WEIGHT * det.sum((0, 2))
    cc = _diff(st, 2) + DETAIL_WEIGHT * det.sum((0, 1))
    kept = _kept(st, keep_colours)
    kr, kc = kept.sum((0, 2)), kept.sum((0, 1))        # kept squares on each line, over the frames
    # the figure's outermost lines on every side stay: they hold its tips and its outline (Sivir's first plan
    # took her hair's top row and both side columns - 「希维尔缩小后整体有点变形」); with a shared plan, every
    # action's own extremes are passed in too
    big = 10 ** 6
    edge_r = {rows.min(), rows.min() + 1, H + bottom - 1, H + bottom} | {H + r for r in edge_rows}
    edge_c = ({cols.min(), cols.min() + 1, cols.max() - 1, cols.max(), W + left, W + left + 1,
               W + right - 1, W + right} | {W + c for c in edge_cols})
    for edge in edge_r:
        if 0 <= edge < len(kr):
            kr[edge] += big
    for edge in edge_c:
        if 0 <= edge < len(kc):
            kc[edge] += big
    r_body0, r_sole = H + top, H + bottom                  # canvas rows of the body's top and the soles' row
    r_pick = _pick(rc, r_body0, r_sole, int(round(cut * (r_sole - r_body0))), keep=kr)
    if rows.min() < r_body0:                               # what rises over the body
        r_pick += _pick(rc, rows.min(), r_body0, int(round(cut * (r_body0 - rows.min()))), r_pick, keep=kr)
    c_l, c_r = W + left, W + right
    c_pick = (_pick(cc, c_l, W, int(round(cut * (W - c_l))), keep=kc)
              + _pick(cc, W + 1, c_r + 1, int(round(cut * (c_r - W))), keep=kc))
    if cols.min() < c_l:
        c_pick += _pick(cc, cols.min(), c_l, int(round(cut * (c_l - cols.min()))), c_pick, keep=kc)
    if cols.max() > c_r:
        c_pick += _pick(cc, c_r + 1, cols.max() + 1, int(round(cut * (cols.max() - c_r))), c_pick, keep=kc)
    # a line still on kept squares (a side whose every column crosses the head) moves to the cheapest free line of
    # the whole figure, the other side of the pivot too (Samira's head fills her right half: 「莎米拉发型每个动作帧都改对了？」)
    def move_off(picks, keep, cost, lo, hi, skip, drop):
        for j, i in enumerate(picks):
            if keep[i] <= 0:
                continue
            free = [c for c in range(lo, hi) if keep[c] <= 0 and c not in skip and c not in picks
                    and (c - 1) not in picks and (c + 1) not in picks]
            if free:
                # the nearest free lines first (bands of 6), the cheapest among them: a head stretch's line goes to
                # the shoulders, not down to the legs (Samira's three body rows all left her legs: 「太怪了」)
                picks[j] = min(free, key=lambda c: (abs(c - i) // 6, cost[c]))
            elif drop:
                picks[j] = None                        # columns: the head fills a whole side - one column fewer
            else:
                # rows: never one fewer (every action must lose the same number, or it stands a row taller than
                # the idle and pops at the change) - the line with the fewest kept squares
                cand = [c for c in range(lo, hi) if c not in skip and c not in picks
                        and (c - 1) not in picks and (c + 1) not in picks]
                picks[j] = min(cand, key=lambda c: (keep[c], cost[c])) if cand else i
        return [c for c in picks if c is not None]
    # only the face / head box ("!" colours) and the edges are held this hard; a hand line that could not be
    # avoided stays cut
    hard = _kept(st, [c for c in keep_colours if c[0] in "!#"])
    # "=RRGGBB": no ROW through a square of that colour, columns may still cross it (Renekton's knee guard: a row
    # through it halved the guard and shifted the stripes of his leg - 「这里是像素缺失吗」「在左脚啊」)
    row_only = _kept(st, ["#" + c[1:] for c in keep_colours if c[0] == "="])     # its squares themselves
    if hard_frames is not None:
        # the death's lying frames put the head at the body's height: in the sum over all frames they made every
        # standing row "the head" and the whole cut fell on the legs (Samira: 「太怪了」) - they count as soft only
        hard[~np.asarray(hard_frames, bool)] = False
    hr, hc = hard.sum((0, 2)) + row_only.sum((0, 2)), hard.sum((0, 1))
    for edge in edge_r:
        if 0 <= edge < len(hr):
            hr[edge] += big
    hr[H] += big                                       # the pivot row: the hips' join, the belt (Samira's run
    kr[H] += big                                       # legs came off their hips with it: 「腿变形了」)
    for edge in edge_c:
        if 0 <= edge < len(hc):
            hc[edge] += big
    r_pick = move_off(r_pick, hr, rc, rows.min(), H + bottom + 1, (), False)
    c_pick = move_off(c_pick, hc, cc, cols.min(), cols.max() + 1, (W,), True)
    return {"rows": sorted(i - H for i in r_pick), "cols": sorted(i - W for i in c_pick),       # from the pivot
            "lost": int(rc[r_pick].sum() + cc[c_pick].sum()) if r_pick or c_pick else 0,
            "shifts": [tuple(int(v) for v in d) for d in shifts] if shifts is not None else None}


def _moved(a, dy, dx):
    """A canvas moved by (dy, dx), what leaves it dropped, the rest empty."""
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = a[ys, xs]
    return out


def anchor_points(frames, colour, near=None):
    """Per frame the centre of `colour` (a colour only one feature has: Xerath's eye core) from the pivot, or None.
    near: start point of a track - each frame keeps only the squares within 10 of the last centre found (an effect
    baked into the frame may carry the colour too)."""
    st, H, W = _canvas(frames)
    rgb = tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))
    pts, last = [], near
    for f in st:
        m = (f[..., 3] > 0) & (f[..., :3] == rgb).all(-1)
        ys, xs = np.nonzero(m)
        ys, xs = ys - H, xs - W
        if last is not None and len(ys):
            ok = (np.abs(ys - last[0]) <= 10) & (np.abs(xs - last[1]) <= 10)
            ys, xs = ys[ok], xs[ok]
        p = (float(ys.mean()), float(xs.mean())) if len(ys) else None
        if p is not None and near is not None:
            last = p
        pts.append(p)
    return pts


def anchor_shifts(frames, colour, ref=None):
    """Per frame (dy, dx) of the anchor against `ref` (default: the first frame that shows it); a frame without it
    takes the last one's."""
    pts = anchor_points(frames, colour, near=ref)
    if ref is None:
        ref = next((p for p in pts if p is not None), None)
    out, last = [], (0, 0)
    for p in pts:
        if p is not None and ref is not None:
            last = (int(round(p[0] - ref[0])), int(round(p[1] - ref[1])))
        out.append(last)
    return out


def move_point(plan, dx, dy):
    """(dx, dy) from the pivot after the plan: down one for each removed row under it (they are all above the soles,
    which stay), in one for each removed column between it and the pivot."""
    ny = dy + sum(1 for i in plan["rows"] if i > dy)
    if dx < 0:
        return dx + sum(1 for i in plan["cols"] if dx < i < 0), ny
    return dx - sum(1 for i in plan["cols"] if 0 < i < dx), ny


def apply_tag(frames, plan):
    """The frames without the plan's rows and columns, each centred on its pivot again: the pivot's row moves up by
    every removed row (all lie above the soles, so the soles keep their place under the pivot) and its column by the
    removed columns left of it."""
    st, H, W = _canvas(frames)
    shifts = plan.get("shifts") or [(0, 0)] * len(frames)
    out = []
    for k, (_, ms) in enumerate(frames):
        dy, dx = shifts[k] if k < len(shifts) else (0, 0)
        gone_r = {H + i + dy for i in plan["rows"] if 0 <= H + i + dy < st.shape[1]}
        gone_c = {W + i + dx for i in plan["cols"] if 0 <= W + i + dx < st.shape[2]}
        keep_r = [i for i in range(st.shape[1]) if i not in gone_r]
        keep_c = [i for i in range(st.shape[2]) if i not in gone_c]
        pr = H - len(gone_r)
        pc = W - sum(1 for i in gone_c if i < W)
        out.append((G.centre_frame(st[k][np.ix_(keep_r, keep_c)], -pc, -pr), ms))
    return out


def body_of(frames):
    """(top, bottom, left, right) of the first frame's figure from its pivot: the body range every action's counts come
    from."""
    st, H, W = _canvas(frames[:1])
    ys, xs = np.nonzero(st[0, ..., 3] > 0)
    return (ys.min() - H, ys.max() - H, xs.min() - W, xs.max() - W)


def shrink_sheet(sheet, scale, body_tag="idle", same_as=None, keep_colours=(), body=None, tags=None, anchor=None,
                 keep_by_tag=None, still=()):
    """Every action of the sheet (or only `tags`) made `scale` as big; returns {tag: plan}. same_as {tag: source tag}: a
    copy of another action's frames (import_native's bake: the attack with a flash drawn in) takes its source's plan.
    body: the range the counts come from (body_of the idle as drawn), when the idle has been shrunk already.
    anchor: a colour only one feature has; the lines then follow the body from frame to frame (anchor_shifts).
    keep_by_tag: {tag: keep colours} for an action that needs other ones (a lying death).
    still: actions whose body stands still from frame to frame while something over it floats (Karma's idle: her ring
    bobs, and the anchor colour is on the ring too) - the lines as chosen, taken at the same place in every frame: the
    anchor read the ring's float as the body moving and cut her legs one row higher in two frames
    (「待机动画效果的时候腿部变形啊」)."""
    if body is None:
        body = body_of(sheet[body_tag])
    # one plan per action from its own frames (its head box and hands are tight there; one plan for all the actions
    # at once made the lying death frames and the jumps protect every standing row and the whole cut fell on the legs)
    # - but the counts come from the idle's body range for all, and no pick is ever dropped, so every action loses
    # the same number of body rows and columns: the same height, no pop at an animation change
    plans = {}
    same_as = same_as or {}
    todo = [t for t in sheet if tags is None or t in tags]

    def root(t):
        return root(same_as[t]) if t in same_as and same_as[t] in sheet else t
    refs = {}
    for tag in sorted(todo, key=lambda t: t != root(t)):
        if root(tag) != tag and root(tag) in plans:
            plans[tag] = dict(plans[root(tag)])
            if anchor:
                # a copy is a slice of its source with an effect drawn in (attack_fx1 = the attack from 183 ms): its
                # own frames' offsets, against its source's first frame
                plans[tag]["shifts"] = anchor_shifts(sheet[tag], anchor, refs[root(tag)])
        else:
            fr = sheet[root(tag)]
            if anchor:
                refs[tag] = next((p for p in anchor_points(fr, anchor) if p is not None), None)
            plans[tag] = plan_tag(fr, body, scale, (keep_by_tag or {}).get(tag, keep_colours),
                                  shifts=anchor_shifts(fr, anchor, refs[tag]) if anchor else None)
            if tag in still:
                plans[tag]["shifts"] = None
    for tag in todo:
        sheet[tag] = apply_tag(sheet[tag], plans[tag])
    return plans
