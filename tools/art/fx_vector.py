#!/usr/bin/env python3
"""A pixel-art effect frame redrawn finer as the same drawing - by code, no picture generator (the user, 2026-11-14:
「所有英雄你觉得特效模糊的 不是太清晰的 你也改改 改成高清一点的 ... 动画和特效都不依赖codex全部交给你来完成」「不合格的特效和动画
你可以手搓」). tools/art/fx_handmade.py stores and applies what this draws.

What was "blurry": a Scale2x twin is its 1x frame again - 2 x 2 dense blocks, only 45-degree corners between solid areas
cut by one dense pixel - so every curve with longer runs (a ring's top, a zone's rim, a slash, a blob's outline) keeps its
2-dense-pixel stairs, thin rings are chains of blocks, and a picture that was enlarged before it became the 1x frame
(2 x 2 game-pixel blocks) is drawn in 4 x 4 dense blocks.

The redraw (redraw / redraw_tag):
- The frame's colours are ranked, transparent lowest (rank_order: touching colours next to each other, rims low, cores
  high). Each level set S_k = {rank >= k} is a binary picture whose boundary is closed loops of unit cracks (the edge
  between a pixel inside and one outside), traced with S on the left (Cracks). Two pixels touching only at a corner are
  joined across it when their side is the sparser one there and the line goes on past one of them (a thin diagonal line
  stays a line; a zig-zag of crackle, two dots, a dither stay squares touching at a point).
- Each crack carries one vertex on the segment between the two pixel centres it separates: v = midpoint + d * normal,
  |d| <= CLAMP < 0.5. Whatever the smoothing does, every 1x pixel centre stays on its own side of every boundary: the
  redraw sampled at the 1x centres is the 1x frame (same shape, size, anchor - the kit's hit area still matches).
- d starts at the area-true marching-squares value (K_CONVEX out for each convex end, in for each concave one) and each
  free vertex is moved along its normal onto a parabola fitted to the vertices up to `window` steps either side of it
  (weighted least squares over the chord length; never past a pinned vertex, never round a bend), then put back into the
  corridor: stairs of any slope come out straight, arcs keep their radius, nothing far along the loop is felt
  (smooth_level).
- The ring / zone drawer: a loop an axis-aligned ellipse explains (fit_ellipse: least squares, then Gauss-Newton on the
  corridor offsets; at least `ellipse` of its vertices inside their corridors) is snapped to that ellipse - the
  parameters come straight from the 1x frame.
- Kept as drawn (sharp: the contour passes through the pixel corner): both corners of a cap (the end of a 1-px line, a
  spark's arm, a lone pixel - a cone's tip stays a point on its stairs' lines instead); a right angle between two runs
  of corner_run or more; every corner of a stretch of stairs shorter than min_stair turns - twice that between two 1-px
  tips (crosses, small stars and diamonds, jogs keep their shape); loops of 6 cracks or fewer. The top of every bump keeps its mean height (extremal runs).
- The offsets are shared by every level using the same crack (boundaries that coincide at 1x coincide in the redraw:
  no slivers; the levels stay nested); a 1-px mark sitting on a smoothed boundary rides with it (couple) and keeps its
  width; a thin pixel squeezed under half its square is redrawn as its square; dither is redrawn as its squares
  (keep_square); a stray dense pixel of a colour not its own square's is removed.
- Rasterised by even-odd scanline fill at the dense pixel centres (fill), the sample point a hair off-centre (EPS_J) so
  that a centre exactly on a 45-degree edge falls the same way everywhere (a 1-px diagonal line comes out exactly two
  dense pixels a row). Only the frame's own colours, alpha as in the frame; a frame that is its own mirror stays so.
- A picture enlarged k times before it became the frame (block_grid) is reduced to its source grid and redrawn k * P
  times finer.

    python -I tools/art/fx_vector.py SHEET TAG [--ppu 2] [--out DIR]     # a quick look: 1x | redraw, every distinct frame
"""
import numpy as np

EPS_J = (1.0e-4, 0.37e-4)      # sample jitter (x, y): a centre exactly on a 45-degree edge falls one way, everywhere alike
CLAMP = 0.44                   # |d| at most this (a vertex never reaches a pixel centre)
K_CONVEX = 0.10355             # (sqrt(2) - 1) / 4: a crack's offset for each convex end (area-true chamfer)
NEAR_MISS = 1.25               # an ellipse missing a vertex's corridor by less than this (in pixels) ...
NEAR_SHARE = 0.04              # ... at more than this share of a loop's vertices is not that loop's shape
COUNT = {"ellipse": 0, "squeezed": 0}   # what the last redraws did (a survey's counters): loops snapped to an ellipse, thin
#                                        pixels redrawn as their squares after a squeeze


# ----------------------------------------------------------------------------- labels and their order
def tag_palette(frames):
    """every colour of a tag's frames (RGBA rows, sorted) - one palette, one order for the whole animation"""
    px = [a[a[..., 3] > 0] for a in frames if (a[..., 3] > 0).any()]
    if not px:
        return np.zeros((0, 4), np.uint8)
    return np.unique(np.concatenate(px), axis=0)


def to_labels(arr, pal):
    """lab (0 transparent, i + 1 = pal[i]) of a frame whose colours are all in pal"""
    lab = np.zeros(arr.shape[:2], np.int32)
    m = arr[..., 3] > 0
    if m.any():
        c = arr[m].astype(np.int32)
        d = (c[:, None, :] != pal[None].astype(np.int32)).any(-1)
        lab[m] = (~d).argmax(1) + 1
    return lab


def depth(mask):
    """chessboard distance of each pixel of mask to the nearest pixel outside it (1 at the edge)"""
    d = np.zeros(mask.shape, np.int32)
    cur = mask.copy()
    n = 0
    while cur.any():
        n += 1
        d[cur] = n
        p = np.pad(cur, 1)
        cur = cur & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:] & p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:]
        if n > 400:
            break
    return d


def rank_order(labs, K):
    """An order of the labels 1..K (transparent 0 stays lowest) that keeps touching colours next to each other where it
    can: start from each colour's mean depth inside the drawing (rims low, cores high), then improve the sum over touching
    pixel pairs of |rank a - rank b| by moving single labels. -> rank[label] (0..K), rank[0] = 0."""
    A = np.zeros((K + 1, K + 1), np.float64)
    dsum = np.zeros(K + 1)
    dcnt = np.zeros(K + 1)
    for lab in labs:
        p = np.pad(lab, 1)
        for a, b in ((p[1:, :], p[:-1, :]), (p[:, 1:], p[:, :-1])):
            ne = a != b
            np.add.at(A, (a[ne], b[ne]), 1.0)
            np.add.at(A, (b[ne], a[ne]), 1.0)
        d = depth(lab > 0)
        np.add.at(dsum, lab.ravel(), d.ravel())
        np.add.at(dcnt, lab.ravel(), 1)
    mean = dsum / np.maximum(dcnt, 1)
    order = [0] + sorted(range(1, K + 1), key=lambda k: (mean[k], k))

    def cost(o):
        r = np.empty(K + 1)
        r[o] = np.arange(K + 1)
        return float((A * np.abs(r[:, None] - r[None, :])).sum())
    best = cost(order)
    improved = True
    guard = 0
    while improved and guard < 20:
        improved = False
        guard += 1
        for i in range(1, K + 1):
            for j in range(1, K + 1):
                if i == j:
                    continue
                o = order[:]
                x = o.pop(i)
                o.insert(j, x)
                c = cost(o)
                if c < best - 1e-9:
                    best, order, improved = c, o, True
    rank = np.empty(K + 1, np.int32)
    rank[order] = np.arange(K + 1)
    return rank


# ----------------------------------------------------------------------------- tracing
class Cracks:
    """the cracks of a binary picture S (h x w): directed so that S is on the left, each with its successor"""

    def __init__(self, S):
        h, w = S.shape
        self.h, self.w = h, w
        p = np.pad(S, 1)
        up, dn = p[:-1, 1:-1], p[1:, 1:-1]            # (h + 1, w): pixel above / below each horizontal crack
        lf, rt = p[1:-1, :-1], p[1:-1, 1:]            # (h, w + 1): pixel left / right of each vertical crack
        self.nh = (h + 1) * w
        hact = (up != dn).ravel()
        vact = (lf != rt).ravel()
        self.active = np.concatenate([hact, vact])
        # direction: 0 E, 1 S, 2 W, 3 N
        hdir = np.where(up, 0, 2).ravel()
        vdir = np.where(lf, 3, 1).ravel()
        self.dir = np.concatenate([hdir, vdir]).astype(np.int8)
        Yh, Xh = np.mgrid[0:h + 1, 0:w]
        Yv, Xv = np.mgrid[0:h, 0:w + 1]
        # midpoints (pixel units, origin the frame's top-left corner)
        self.mx = np.concatenate([(Xh + 0.5).ravel(), Xv.ravel().astype(np.float64)])
        self.my = np.concatenate([Yh.ravel().astype(np.float64), (Yv + 0.5).ravel()])
        # end corner of each directed crack
        ex = np.concatenate([np.where(up, Xh + 1, Xh).ravel(), Xv.ravel()])
        ey = np.concatenate([Yh.ravel(), np.where(lf, Yv, Yv + 1).ravel()])
        # saddles: at a corner whose 2x2 pixels are S on one diagonal only, the sparser side is the one connected
        # (a thin line of either side stays one line)
        q = np.pad(S, 3).astype(np.int32)
        c = q.cumsum(0).cumsum(1)
        c = np.pad(c, ((1, 0), (1, 0)))
        # count of S in the 6x6 window centred on each corner (X, Y), X in 0..w, Y in 0..h
        cnt = c[6:6 + h + 1, 6:6 + w + 1] - c[0:h + 1, 6:6 + w + 1] - c[6:6 + h + 1, 0:w + 1] + c[0:h + 1, 0:w + 1]
        P2 = np.pad(S, 1)                              # pixel (x, y) at P2[y + 1, x + 1]

        def pix(x, y):
            return P2[y + 1, x + 1]
        # ... and only where the line goes on past one of its two pixels, the same way (a zig-zag of crackle, two dots
        # touching at a corner are not joined: they stay squares touching at a point)
        P4 = np.pad(S, 3)
        Yc, Xc = np.mgrid[0:h + 1, 0:w + 1]

        def at(x, y):
            return P4[y + 3, x + 3]
        nw, se, ne, sw = at(Xc - 1, Yc - 1), at(Xc, Yc), at(Xc, Yc - 1), at(Xc - 1, Yc)
        sad_main = nw & se & ~ne & ~sw                 # S on the main diagonal
        sad_anti = ne & sw & ~nw & ~se

        def goes_on(v):
            """each diagonal pair of colour v: a pixel of v beyond one of its ends, in that end's far quadrant"""
            def is_(x, y):
                return at(x, y) == v
            main = (is_(Xc - 2, Yc - 2) | is_(Xc - 2, Yc - 1) | is_(Xc - 1, Yc - 2)
                    | is_(Xc + 1, Yc + 1) | is_(Xc + 1, Yc) | is_(Xc, Yc + 1))
            anti = (is_(Xc + 1, Yc - 2) | is_(Xc + 1, Yc - 1) | is_(Xc, Yc - 2)
                    | is_(Xc - 2, Yc + 1) | is_(Xc - 2, Yc) | is_(Xc - 1, Yc + 1))
            return main, anti
        fg_main, fg_anti = goes_on(True)
        bg_main, bg_anti = goes_on(False)
        long_main, long_anti = fg_main, fg_anti
        sparse_fg = cnt <= 18
        # S joined across the corner / the outside joined across it / neither (both S pixels keep sharp corners there)
        self.fg_conn = (sad_main & sparse_fg & long_main) | (sad_anti & sparse_fg & long_anti)
        bg_conn = (sad_main & ~sparse_fg & bg_anti) | (sad_anti & ~sparse_fg & bg_main)
        self.pinch_at = (sad_main | sad_anti) & ~self.fg_conn & ~bg_conn
        d = self.dir
        X, Y = ex, ey
        # ahead-left / ahead-right pixels of each directed crack at its end corner
        alx = np.choose(d, [X, X, X - 1, X - 1])
        aly = np.choose(d, [Y - 1, Y, Y, Y - 1])
        arx = np.choose(d, [X, X - 1, X - 1, X])
        ary = np.choose(d, [Y, Y, Y - 1, Y - 1])
        AL, AR = pix(alx, aly), pix(arx, ary)
        fgc = self.fg_conn[Y, X]
        left = ~AL & (~AR | ~fgc)
        right = AR & (AL | fgc)
        turn = np.where(left, 1, np.where(right, -1, 0)).astype(np.int8)     # +1 left (convex), -1 right (concave)
        self.bridge = right & ~AL                      # a concave corner where two pixels touch only diagonally
        self.pinch = left & self.pinch_at[Y, X]        # a corner where two pixels touch at a point and stay apart
        nd = (d + np.where(left, 3, np.where(right, 1, 0))) % 4
        # the crack leaving corner (X, Y) in direction nd
        nxt_h = np.where(nd == 0, Y * w + X, Y * w + X - 1)
        nxt_v = self.nh + np.where(nd == 1, Y * (w + 1) + X, (Y - 1) * (w + 1) + X)
        self.next = np.where((nd == 0) | (nd == 2), nxt_h, nxt_v)
        self.ex, self.ey = ex.astype(np.float64), ey.astype(np.float64)
        self.sx = self.ex - np.choose(d, [1.0, 0.0, -1.0, 0.0])
        self.sy = self.ey - np.choose(d, [0.0, 1.0, 0.0, -1.0])
        self.turn = turn
        # normal from S to outside: the right-hand side of the direction
        self.nx = np.choose(d, [0.0, -1.0, 0.0, 1.0])
        self.ny = np.choose(d, [1.0, 0.0, -1.0, 0.0])

    def loops(self):
        """[index array of each loop's cracks, in order]"""
        act = self.active
        seen = np.zeros(len(act), bool)
        nxt = self.next.tolist()
        out = []
        for s in np.nonzero(act)[0].tolist():
            if seen[s]:
                continue
            loop = []
            i = s
            while not seen[i]:
                seen[i] = True
                loop.append(i)
                i = nxt[i]
            out.append(np.array(loop, np.int64))
        return out


# ----------------------------------------------------------------------------- smoothing a loop
def run_info(turn):
    """for a loop's turns (turn[i] = the turn after crack i): each crack's run length, and each run's (start, length,
    turn before, turn after)"""
    n = len(turn)
    brk = np.nonzero(turn != 0)[0]                  # a run ends at each crack followed by a turn
    if len(brk) == 0:
        return np.full(n, n), []
    runs = []
    length = np.zeros(n, np.int32)
    for j, e in enumerate(brk):
        s = (brk[j - 1] + 1) % n                    # first crack of this run
        ln = (e - s) % n + 1
        idx = (s + np.arange(ln)) % n
        length[idx] = ln
        runs.append((s, ln, int(turn[brk[j - 1]]), int(turn[e])))
    return length, runs


def _ellipse_d(par, x, y, nx, ny):
    """(d, ok): where each normal line m + d n crosses the ellipse par = (cx, cy, a, b), leaving it outwards"""
    cx, cy, a, b = par
    ux, uy = (x - cx) / a, (y - cy) / b
    vx, vy = nx / a, ny / b
    qa = vx * vx + vy * vy
    qb = 2 * (ux * vx + uy * vy)
    qc = ux * ux + uy * uy - 1
    disc = qb * qb - 4 * qa * qc
    ok = disc >= 0
    sq = np.sqrt(np.where(ok, disc, 0.0))
    d1, d2 = (-qb - sq) / (2 * qa), (-qb + sq) / (2 * qa)
    d = np.where(np.abs(d1) < np.abs(d2), d1, d2)
    ok &= (ux + d * vx) * vx + (uy + d * vy) * vy > 0
    return d, ok


def fit_ellipse(x, y, nx, ny, rounds=4):
    """An axis-aligned ellipse through a loop's crack midpoints (x, y; normals nx, ny), fitted on the vertices it can
    explain: -> (offsets d along the normals that put each vertex on the ellipse, inlier mask, (cx, cy, a, b)) or None.
    A vertex is an inlier when the ellipse crosses its corridor (|d| < 0.5: the digitised ellipse is this loop there).
    First the conic by least squares, then the four numbers refined on the inliers' squared offsets (Gauss-Newton)."""
    w = np.ones(len(x), bool)
    ox, oy = x.mean(), y.mean()                      # fitted about the loop's middle (the right-hand side stays positive)
    xs, ys = x - ox, y - oy
    par = None
    for _ in range(rounds):
        if w.sum() < 12:
            break
        A = np.stack([xs[w] ** 2, ys[w] ** 2, xs[w], ys[w]], -1)
        sol, *_ = np.linalg.lstsq(A, np.ones(w.sum()), rcond=None)
        p, q, r, s = sol
        if p <= 0 or q <= 0:
            break
        cx, cy = -r / (2 * p), -s / (2 * q)
        k = 1 + p * cx * cx + q * cy * cy
        par = np.array([cx + ox, cy + oy, np.sqrt(k / p), np.sqrt(k / q)])
        d, ok = _ellipse_d(par, x, y, nx, ny)
        inl = ok & (np.abs(d) < 0.6)
        if (inl == w).all():
            break
        w = inl
    if par is None:
        return None
    for _ in range(8):
        d, ok = _ellipse_d(par, x, y, nx, ny)
        inl = ok & (np.abs(d) < 0.6)
        if inl.sum() < 12:
            return None
        J = np.empty((inl.sum(), 4))
        for k in range(4):
            e = np.zeros(4)
            e[k] = 1e-4
            d2, _ = _ellipse_d(par + e, x, y, nx, ny)
            J[:, k] = (d2[inl] - d[inl]) / 1e-4
        step, *_ = np.linalg.lstsq(J, -d[inl], rcond=None)
        par = par + step
        if np.abs(step).max() < 1e-4:
            break
    d, ok = _ellipse_d(par, x, y, nx, ny)
    inl = ok & (np.abs(d) < 0.5)
    # a vertex the ellipse misses by a little says the loop is not an ellipse (an oval with flatter sides, a lens): only
    # clear features (a knot on a ring, a spike: far off) may stand out of one
    near = ~inl & ok & (np.abs(d) < NEAR_MISS)
    if near.mean() > NEAR_SHARE:
        return None
    return d, inl, tuple(par)


def smooth_level(mx, my, nx, ny, turn, bridge, pinch, start, length, window=7, iters=6, pull=0.02, corner_run=3, bend=0.86,
                 min_stair=4, ellipse=0.8):
    """Offsets d of every vertex of a level's loops (concatenated: loop j is start[j] .. start[j] + length[j] - 1, in
    order) and, for each crack, whether the corner after it is kept sharp (the contour passes through the lattice corner).

    Sharp: both corners of a cap (the end of a 1-px line, a spark's arm, a lone pixel - but not the tip of a cone, whose
    stairs go down both sides: that stays a point on their lines); a right angle between two runs of corner_run or more;
    every corner of a stretch of stairs shorter than min_stair turns (a jog or two between two bumps is drawn as it is:
    small sparks, crosses and stars keep their shape); every corner of a loop of 6 cracks or fewer. A concave corner where
    two pixels touch only diagonally is never sharp (the bridge between them keeps its width).

    Each free vertex is then moved along its normal onto a parabola fitted (weighted least squares over the chord length)
    to the vertices up to `window` steps either side of it - never looking past a pinned one or round a bend - and put
    back into its corridor: straight runs of stairs come out straight (a fit of collinear points is their line), arcs keep
    their radius (a parabola follows them), and nothing far away along the loop is felt."""
    n = len(mx)
    d0 = np.zeros(n)
    pinned = np.zeros(n, bool)
    sharp = np.zeros(n, bool)                           # the corner after crack i
    modelled = np.zeros(n, bool)
    groups = []
    loop_of = np.zeros(n, np.int64)
    pos = np.zeros(n, np.int64)
    for j, (s, ln) in enumerate(zip(start, length)):
        sl = slice(s, s + ln)
        t = turn[sl]
        loop_of[sl] = j
        pos[sl] = np.arange(ln)
        sh = np.zeros(ln, bool)
        pin = np.zeros(ln, bool)
        if ln <= 6:                                     # a lone pixel, a domino: their squares
            sh[:] = t != 0
        else:
            rl, runs = run_info(t)
            for i in np.nonzero(t != 0)[0]:
                if rl[i] >= corner_run and rl[(i + 1) % ln] >= corner_run:
                    sh[i] = True
            for rs, rn, t0, t1 in runs:
                if t0 == t1 and t0 != 0:                # an extremal run
                    if rn == 1:
                        c, g = rs, t0
                        cone = (t[(c + 1) % ln] == -g and t[(c + 2) % ln] == g and t[(c + 3) % ln] != g
                                and t[(c - 2) % ln] == -g and t[(c - 3) % ln] == g and t[(c - 4) % ln] != g)
                        if cone:
                            pin[[(c - 1) % ln, c, (c + 1) % ln]] = True
                        else:
                            sh[(c - 1) % ln] = sh[c] = True
                            # an arm: a straight 1-px line, two or more long, standing on a body that spreads both
                            # ways at its foot (a star's arm on its core, a bar on a band) keeps its square foot too
                            lf, lb = rl[(c + 1) % ln], rl[(c - 1) % ln]
                            ef, bb = (c + lf) % ln, (c - 1 - lb) % ln
                            if max(lf, lb) >= 2 and t[ef] == -g and t[bb] == -g:
                                sh[ef] = sh[bb] = True
                    else:
                        groups.append(s + (rs + np.arange(rn)) % ln)
            # stretches of stairs: the turns between one pair of like turns and the next
            tn = np.nonzero(t != 0)[0]
            if len(tn) >= 2:
                sg = t[tn]
                brk = np.nonzero(sg == np.roll(sg, -1))[0]          # a stretch ends at turn k when turn k + 1 is alike
                if len(brk) == 0:
                    pass                                             # one endless staircase (cannot close): leave
                else:
                    for q, e in enumerate(brk):
                        b0 = (brk[q - 1] + 1) % len(tn)
                        cnt_ = (e - b0) % len(tn) + 1
                        # between two 1-px tips (a small star's arm to the next, a small diamond's side) a few steps
                        # more are still the drawing's own shape, not a slope
                        tips = ((tn[b0] - tn[b0 - 1]) % ln == 1) and ((tn[(e + 1) % len(tn)] - tn[e]) % ln == 1)
                        if cnt_ < min_stair or (tips and cnt_ < 2 * min_stair):
                            sh[tn[(b0 + np.arange(cnt_)) % len(tn)]] = True
        sh &= ~bridge[sl]
        sh |= pinch[sl]
        sh &= t != 0
        model = None
        if ellipse and ln >= 24:
            fit = fit_ellipse(mx[sl], my[sl], nx[sl], ny[sl])
            if fit is not None and fit[1].mean() >= ellipse:
                dm, inl, _ = fit
                # an ellipse: its vertices sit on it - no corner of it is kept sharp, no bump of it pinned
                sh &= (~inl & ~np.roll(inl, -1)) | pinch[sl]
                pin &= ~inl
                model = (dm, inl)
                modelled[sl] = inl
                COUNT["ellipse"] += 1
        tb = np.roll(t, 1)
        shb = np.roll(sh, 1)
        d0[sl] = np.where(sh | shb, 0.0, K_CONVEX * (tb.astype(np.float64) + t))   # beside a sharp corner: on the pixel edge
        pin |= sh | shb
        if model is not None:
            dm, inl = model
            take = inl & ~(sh | shb)
            d0[sl] = np.where(take, np.clip(dm, -CLAMP, CLAMP), d0[sl])
            pin |= take
        pinned[sl] = pin
        sharp[sl] = sh
    if pinned.all():
        return d0, sharp
    st = np.asarray(start)[loop_of]
    ln_of = np.asarray(length)[loop_of]
    m = window
    shifts = np.arange(-m, m + 1)
    idx = st[None, :] + (pos[None, :] + shifts[:, None]) % ln_of[None, :]            # (2m + 1, n)
    # a window never wraps onto itself, and never looks past a pinned vertex (the pinned one is its last point)
    valid = np.abs(shifts)[:, None] <= ((ln_of - 1) // 2)[None, :]
    blocked = np.zeros(n, bool)
    for s in range(1, m + 1):
        valid[m + s] &= ~blocked
        blocked = blocked | pinned[idx[m + s]]
    blocked = np.zeros(n, bool)
    for s in range(1, m + 1):
        valid[m - s] &= ~blocked
        blocked = blocked | pinned[idx[m - s]]
    # ... and never spans a bend: the window ends where the chord across it falls under `bend` of the path along it
    # (a parabola follows an arc for about 50 degrees either side; a tight turn fitted wider comes out pinched)
    vx0, vy0 = mx + d0 * nx, my + d0 * ny
    nx0 = st + (pos + 1) % ln_of
    seg0 = np.hypot(vx0[nx0] - vx0, vy0[nx0] - vy0)[idx]
    fwd = np.zeros(n)
    bwd = np.zeros(n)
    straight = np.ones(n, bool)
    for s in range(1, m + 1):
        fwd = fwd + seg0[m + s - 1]
        bwd = bwd + seg0[m - s]
        chord = np.hypot(vx0[idx[m + s]] - vx0[idx[m - s]], vy0[idx[m + s]] - vy0[idx[m - s]])
        straight &= (chord >= bend * (fwd + bwd)) | (s <= 2)
        valid[m + s] &= straight
        valid[m - s] &= straight
    taper = (1.0 - (np.abs(shifts) / (m + 1.0)) ** 3) ** 3
    W = valid * taper[:, None]
    cnt = valid.sum(0)
    nxt = st + (pos + 1) % ln_of
    free = ~pinned
    d = d0.copy()
    for _ in range(iters):
        vx, vy = mx + d * nx, my + d * ny
        seg = np.hypot(vx[nxt] - vx, vy[nxt] - vy)
        Sg = seg[idx]
        u = np.zeros((2 * m + 1, n))
        for s in range(1, m + 1):
            u[m + s] = u[m + s - 1] + Sg[m + s - 1]
            u[m - s] = u[m - s + 1] - Sg[m - s]
        X, Y = vx[idx], vy[idx]
        S0, S1, S2, S3, S4 = (W.sum(0), (W * u).sum(0), (W * u * u).sum(0), (W * u ** 3).sum(0), (W * u ** 4).sum(0))
        A = np.empty((n, 3, 3))
        A[:, 0, 0] = S0
        A[:, 0, 1] = A[:, 1, 0] = S1
        A[:, 0, 2] = A[:, 1, 1] = A[:, 2, 0] = S2
        A[:, 1, 2] = A[:, 2, 1] = S3
        A[:, 2, 2] = S4
        quad = cnt >= 5
        A[~quad, 2, :] = 0.0
        A[~quad, :, 2] = 0.0
        A[~quad, 2, 2] = 1.0
        A += np.eye(3)[None] * 1e-9
        Bx = np.stack([(W * X).sum(0), (W * u * X).sum(0), np.where(quad, (W * u * u * X).sum(0), 0.0)], -1)
        By = np.stack([(W * Y).sum(0), (W * u * Y).sum(0), np.where(quad, (W * u * u * Y).sum(0), 0.0)], -1)
        cx = np.linalg.solve(A, Bx[..., None])[..., 0]
        cy = np.linalg.solve(A, By[..., None])[..., 0]
        sx, sy, tx, ty = cx[:, 0], cy[:, 0], cx[:, 1], cy[:, 1]
        rx, ry = sx - mx, sy - my
        den = nx * ty - ny * tx
        num = rx * ty - ry * tx
        tl = np.hypot(tx, ty) + 1e-12
        good = np.abs(den) > 0.35 * tl
        dn = np.where(good, num / np.where(good, den, 1.0), rx * nx + ry * ny)
        dn = np.where(cnt >= 3, dn, d)
        dn = d0 + (dn - d0) * (1.0 - pull)
        dn[pinned] = d0[pinned]
        dn = np.clip(dn, -CLAMP, CLAMP)
        for g in groups:
            f = g[free[g]]
            if len(f):
                dn[f] -= (dn[g] - d0[g]).sum() / len(f)
        d = np.clip(dn, -CLAMP, CLAMP)
    return d, sharp


# ----------------------------------------------------------------------------- rasterising
def fill(loops_xy, H, W, P):
    """even-odd fill of closed polygons (vertex arrays in pixel units) sampled at the dense pixel centres (P a pixel)"""
    flip = np.zeros((H, W + 1), np.int32)
    jx, jy = EPS_J
    for vx, vy in loops_xy:
        ax, ay = vx, vy
        bx, by = np.roll(vx, -1), np.roll(vy, -1)
        ymin, ymax = np.minimum(ay, by), np.maximum(ay, by)
        r_lo = np.ceil((ymin - jy) * P - 0.5).astype(np.int64)
        r_hi = np.ceil((ymax - jy) * P - 0.5).astype(np.int64)
        span = int((r_hi - r_lo).max()) if len(r_lo) else 0
        dy = by - ay
        ok0 = dy != 0
        slope = np.where(ok0, (bx - ax) / np.where(ok0, dy, 1.0), 0.0)
        for k in range(span):
            r = r_lo + k
            ok = ok0 & (r < r_hi) & (r >= 0) & (r < H)
            if not ok.any():
                continue
            yr = (r[ok] + 0.5) / P + jy
            xc = ax[ok] + (yr - ay[ok]) * slope[ok]
            c0 = np.floor((xc - jx) * P + 0.5).astype(np.int64)
            c0 = np.clip(c0, 0, W)
            np.add.at(flip, (r[ok], c0), 1)
    return (np.cumsum(flip, axis=1)[:, :W] & 1).astype(bool)


# ----------------------------------------------------------------------------- a frame
def keep_square(lab):
    """1x pixels redrawn as their squares whatever the contours say: dither (a pixel none of whose four neighbours has
    its colour while two or more of its diagonal ones do)"""
    p = np.pad(lab, 1, constant_values=-9)
    c = p[1:-1, 1:-1]
    four = (p[:-2, 1:-1] == c) | (p[2:, 1:-1] == c) | (p[1:-1, :-2] == c) | (p[1:-1, 2:] == c)
    tl, tr, bl, br = p[:-2, :-2] == c, p[:-2, 2:] == c, p[2:, :-2] == c, p[2:, 2:] == c
    diag = tl.astype(int) + tr + bl + br
    # a line's pixel has its two like diagonal neighbours opposite each other; dither has them on one side, or three
    core = ~four & ((diag >= 3) | (tl & tr) | (bl & br) | (tl & bl) | (tr & br))
    q = np.pad(core, 1)
    near = (q[:-2, :-2] & tl) | (q[:-2, 2:] & tr) | (q[2:, :-2] & bl) | (q[2:, 2:] & br)
    k = core | (~four & near)
    # ... and the pixels round them (a dither's rim: its notches are not the ends of lines)
    q = np.pad(k, 1)
    return (q[:-2, :-2] | q[:-2, 1:-1] | q[:-2, 2:] | q[1:-1, :-2] | q[1:-1, 1:-1] | q[1:-1, 2:] | q[2:, :-2]
            | q[2:, 1:-1] | q[2:, 2:])


def couple(lab, R, d, rigid):
    """The cracks' offsets with every thin mark riding on the boundary it sits at: a pixel whose neighbours above and
    below (or left and right) both have other colours is one pixel thick; when one of its two edges is rigid (kept beside
    a sharp corner at every level drawing it - the mark's own edge) and the other was smoothed (a ring's rim snapped to
    its ellipse), the rigid edge takes the smoothed one's shift: the mark moves with the rim and keeps its width, and
    the smooth boundary is left exactly as it was fitted."""
    h, w = lab.shape
    nh = (h + 1) * w
    p = np.pad(lab, 1)
    c = p[1:-1, 1:-1]
    Rp = np.pad(R, 1)
    # the sign of each crack's normal (from the higher rank to the lower) along +y (horizontal cracks) / +x (vertical)
    sgn = np.concatenate([np.where(Rp[:-1, 1:-1] > Rp[1:, 1:-1], 1.0, -1.0).ravel(),
                          np.where(Rp[1:-1, :-1] > Rp[1:-1, 1:], 1.0, -1.0).ravel()])
    o = d * sgn
    Y, X = np.mgrid[0:h, 0:w]
    ty = (p[:-2, 1:-1] != c) & (p[2:, 1:-1] != c)
    tx = (p[1:-1, :-2] != c) & (p[1:-1, 2:] != c)
    a = np.concatenate([(Y[ty] * w + X[ty]), nh + Y[tx] * (w + 1) + X[tx]])
    b = np.concatenate([((Y[ty] + 1) * w + X[ty]), nh + Y[tx] * (w + 1) + X[tx] + 1])
    if not len(a):
        return d
    ts = np.zeros_like(o)
    tc = np.zeros_like(o)
    for u, v in ((a, b), (b, a)):
        m = rigid[u] & ~rigid[v]
        np.add.at(ts, u[m], o[v[m]])
        np.add.at(tc, u[m], 1.0)
    o = np.where(tc > 0, ts / np.maximum(tc, 1), o)
    return np.clip(o, -CLAMP, CLAMP) * sgn


def redraw_labels(lab, rank, P, window=7, iters=6, pull=0.02, corner_run=3, bend=0.86, min_stair=4, ellipse=0.8,
                  ride=True, stats=None):
    """the label picture lab (0 transparent) P times finer -> dense label picture"""
    h, w = lab.shape
    K = int(rank.max())
    R = rank[lab]
    H, W = h * P, w * P
    n_cr = (h + 1) * w + h * (w + 1)
    dsum = np.zeros(n_cr)
    dcnt = np.zeros(n_cr)
    hcnt = np.zeros(n_cr)
    levels = []
    for k in range(1, K + 1):
        S = R >= k
        if not S.any():
            levels.append(None)
            continue
        cr = Cracks(S)
        loops = cr.loops()
        cat = np.concatenate(loops)
        lens = [len(lp) for lp in loops]
        starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
        d, sq = smooth_level(cr.mx[cat], cr.my[cat], cr.nx[cat], cr.ny[cat], cr.turn[cat], cr.bridge[cat], cr.pinch[cat],
                             starts, lens,
                             window, iters, pull, corner_run, bend, min_stair, ellipse)
        dsum[cat] += d
        dcnt[cat] += 1
        hcnt[cat] += sq | np.concatenate([np.roll(sq[a:a + ln], 1) for a, ln in zip(starts, lens)])
        sqf = np.zeros(n_cr, bool)
        sqf[cat] = sq
        levels.append((cr, loops, sqf))
    dmean = dsum / np.maximum(dcnt, 1)
    if ride:
        dmean = couple(lab, R, dmean, (hcnt == dcnt) & (dcnt > 0))
    out = np.zeros((H, W), np.int32)
    prev = None
    for k in range(1, K + 1):
        if levels[k - 1] is None:
            break
        cr, loops, sqf = levels[k - 1]
        polys = []
        for lp in loops:
            vx, vy = cr.mx[lp] + dmean[lp] * cr.nx[lp], cr.my[lp] + dmean[lp] * cr.ny[lp]
            s = sqf[lp]
            if s.any():
                # a sharp corner: the contour goes through the corner after its crack - the lattice corner moved with
                # the two cracks that meet there (their normals are at right angles)
                nl = np.roll(lp, -1)
                qx = cr.ex[lp] + dmean[lp] * cr.nx[lp] + dmean[nl] * cr.nx[nl]
                qy = cr.ey[lp] + dmean[lp] * cr.ny[lp] + dmean[nl] * cr.ny[nl]
                px = np.stack([vx, np.where(s, qx, vx)], -1).ravel()
                py = np.stack([vy, np.where(s, qy, vy)], -1).ravel()
                polys.append((px, py))
            else:
                polys.append((vx, vy))
        M = fill(polys, H, W, P)
        if prev is not None:
            M &= prev
        out += M
        prev = M
    inv = np.zeros(K + 1, np.int32)
    inv[rank] = np.arange(K + 1)
    dense = inv[out]
    sq = keep_square(lab)
    # no thin mark squeezed away: a pixel in no 2 x 2 block of its own colour (a 1-px line, rim or gap - transparent
    # ones too) keeps at least half of its square; one that two boundaries smoothed apart from each other squeezed
    # further is redrawn as its square
    p = np.pad(lab, 1, constant_values=-9)
    c = p[1:-1, 1:-1]
    thick = np.zeros(lab.shape, bool)
    for dy in (0, 1):
        for dx in (0, 1):
            thick |= ((p[dy:dy + h, dx:dx + w] == c) & (p[dy + 1:dy + 1 + h, dx:dx + w] == c)
                      & (p[dy:dy + h, dx + 1:dx + 1 + w] == c) & (p[dy + 1:dy + 1 + h, dx + 1:dx + 1 + w] == c))
    own = (dense.reshape(h, P, w, P) == lab[:, None, :, None]).sum(axis=(1, 3))
    sq |= ~thick & (own < (P * P) // 2)
    COUNT["squeezed"] += int((~thick & (own < (P * P) // 2)).sum())
    if stats is not None:
        stats["squeezed"] = int((~thick & (own < (P * P) // 2)).sum())
    if sq.any():
        big = np.repeat(np.repeat(lab, P, 0), P, 1)
        m = np.repeat(np.repeat(sq, P, 0), P, 1)
        dense[m] = big[m]
    # no stray speck: a dense pixel of a colour that is not its own square's and that touches no pixel of that colour
    # (a sliver between two boundaries, cut to a dot by the grid) takes its square's colour
    big = np.repeat(np.repeat(lab, P, 0), P, 1)
    for _ in range(2):
        q = np.pad(dense, 1, constant_values=-1)
        alone = ((q[:-2, 1:-1] != dense) & (q[2:, 1:-1] != dense) & (q[1:-1, :-2] != dense) & (q[1:-1, 2:] != dense)
                 & (dense != big))
        if not alone.any():
            break
        dense[alone] = big[alone]
    if stats is not None:
        blk = dense.reshape(h, P, w, P)
        own = (blk == lab[:, None, :, None]).mean(axis=(1, 3))
        stats["lost"] = int(((own == 0) & (lab > 0)).sum())
        stats["min_own"] = float(own[lab > 0].min()) if (lab > 0).any() else 1.0
        stats["changed"] = float((dense != np.repeat(np.repeat(lab, P, 0), P, 1)).mean())
    return dense


def block_grid(arr, min_px=40):
    """(k, oy, ox) when the frame is a picture enlarged k times before it became the frame (k x k blocks from (oy, ox)),
    else (1, 0, 0). A frame of fewer than min_px drawn pixels says nothing by itself (a few specks)."""
    m = arr[..., 3] > 0
    if m.sum() < min_px:
        return 1, 0, 0
    h, w = m.shape
    for k in (3, 2):
        for oy in range(k):
            for ox in range(k):
                # pad so that the grid from (oy, ox) covers the frame
                top, left = (k - oy) % k, (k - ox) % k
                H2 = -(-(h + top) // k) * k
                W2 = -(-(w + left) // k) * k
                a = np.zeros((H2, W2, 4), np.uint8)
                a[top:top + h, left:left + w] = arr
                c = a.reshape(H2 // k, k, W2 // k, k, 4)
                if (c == c[:, :1, :, :1]).all(axis=(1, 3, 4)).all():
                    return k, oy, ox
    return 1, 0, 0


def redraw(arr, P=2, pal=None, rank=None, symmetric=True, grid=None, **kw):
    """a 1x frame (RGBA uint8, alpha 0 or 255) redrawn P times finer -> RGBA uint8 (h * P, w * P). grid: the enlargement
    of the tag's other frames - a frame of a few specks that is made of the same blocks is read on that grid too."""
    h, w = arr.shape[:2]
    if not (arr[..., 3] > 0).any():
        return np.zeros((h * P, w * P, 4), np.uint8)
    k, oy, ox = block_grid(arr)
    if k == 1 and grid and grid > 1:
        k2, oy2, ox2 = block_grid(arr, min_px=1)
        if k2 == grid:
            k, oy, ox = k2, oy2, ox2
    if k > 1:
        # the picture it was enlarged from, redrawn k * P times finer and put back on the frame's grid
        top, left = (k - oy) % k, (k - ox) % k
        H2, W2 = -(-(h + top) // k) * k, -(-(w + left) // k) * k
        a = np.zeros((H2, W2, 4), np.uint8)
        a[top:top + h, left:left + w] = arr
        small = a[::k, ::k]
        big = redraw(small, P * k, pal, rank, False, None, **kw)
        out = big[top * P:(top + h) * P, left * P:(left + w) * P]
    else:
        if pal is None:
            pal = tag_palette([arr])
        lab = to_labels(arr, pal)
        if rank is None:
            rank = rank_order([lab], len(pal))
        dense = redraw_labels(lab, rank, P, **kw)
        cols = np.concatenate([np.zeros((1, 4), np.uint8), pal])
        out = cols[dense]
    if symmetric:
        for axis in (1, 0):
            if (arr == np.flip(arr, axis)).all():
                b = np.flip(out, axis)
                o = out.copy()
                take = (out[..., 3] == 0) & (b[..., 3] > 0)
                o[take] = b[take]
                n = o.shape[axis]
                half = np.take(o, range(n // 2), axis=axis)
                mid = np.take(o, range(n // 2, n - n // 2), axis=axis)
                out = np.concatenate([half, mid, np.flip(half, axis)], axis=axis)
    return out


def redraw_tag(frames, P=2, **kw):
    """every frame of a tag redrawn with one palette and one colour order"""
    pal = tag_palette(frames)
    labs = [to_labels(a, pal) for a in frames if (a[..., 3] > 0).any()]
    rank = rank_order(labs, len(pal)) if labs else None
    # the tag's enlargement: what most of its frames with enough pixels to tell are made of
    ks = [block_grid(a)[0] for a in frames if (a[..., 3] > 0).sum() >= 40]
    grid = max(set(ks), key=ks.count) if ks else 1
    cache = {}
    out = []
    for a in frames:
        key = (a.shape, a.tobytes())
        if key not in cache:
            cache[key] = redraw(a, P, pal, rank, grid=grid, **kw)
        out.append(cache[key])
    return out


def _main():
    import argparse
    import json
    import os
    from PIL import Image
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("tag")
    ap.add_argument("--ppu", type=int, default=2)
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    stem = os.path.join(root, a.sheet.split("_", 1)[0], "effects", a.sheet)
    fan = json.load(open(stem + "#anim.fanim", encoding="utf-8-sig"))["anims"][a.tag]["frames"]
    img = np.asarray(Image.open(stem + "#sheet.png").convert("RGBA"))
    frames = []
    for f in fan:
        x, y, w, h = (int(f["data"][k]) for k in "xywh")
        frames.append(img[y:y + h, x:x + w].copy())
    new = redraw_tag(frames, a.ppu)
    seen, rows = set(), []
    for fr, g in zip(frames, new):
        key = (fr.shape, fr.tobytes())
        if key in seen or not fr[..., 3].any():
            continue
        seen.add(key)
        k = 8 // a.ppu
        left = np.repeat(np.repeat(fr, 8, 0), 8, 1)
        right = np.repeat(np.repeat(g, k, 0), k, 1)
        rows.append(np.concatenate([left, np.zeros((left.shape[0], 8, 4), np.uint8), right], 1))
    W = max(r.shape[1] for r in rows)
    can = np.zeros((sum(r.shape[0] + 8 for r in rows), W, 4), np.uint8)
    can[..., :3] = (92, 98, 86)
    can[..., 3] = 255
    y = 0
    for r in rows:
        m = r[..., 3] > 0
        can[y:y + r.shape[0], :r.shape[1]][m] = r[m]
        y += r.shape[0] + 8
    p = os.path.join(a.out, f"{a.sheet}__{a.tag}_redraw.png")
    Image.fromarray(can).save(p)
    print(p)


if __name__ == "__main__":
    _main()
