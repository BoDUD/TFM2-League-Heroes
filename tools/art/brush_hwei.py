#!/usr/bin/env python3
"""Hwei's paintbrush at the design's own length in every pose (design_hwei_poses.py calls normalize()).

Codex drew the brush 1.1-1.5 times the design's in its poses (grip to point 29-41 squares, the design's 26.5; its
HANDOFF says so), so a swing would grow the brush out of the idle's hand. Each pose's own brush is taken away and the
design's is drawn in its place: the same grip, the same direction, the design's length and parts. The brush along its
axis from the grip (u, squares; read on hd/idle.png from the hand at (40.5, 54.5) to the point at (60, 72.5), 47 deg):
the dark wood shaft, a gold-and-crimson band, a navy and a teal ring, a pale ring, the crimson head widening, the navy
bristles, the wooden point; a 1-square near-black outline round it. Behind the hand a short butt with a gold cap (the
design hides it in the sleeve; Codex's poses show it). Each part in its shades, the lit one on the side facing up (the
design's light), as the design shades it.

normalize(fig, spec): the old brush's axis refined from its own squares near the hand-read one (refine), then the old
brush (a capsule from its butt - or the grip when the sleeve hides it - to its point, as wide as it was drawn) cleared
beyond the hand (the hand and what it holds kept, |u| <= HAND), the new brush drawn, the hand's
pixels laid back over it; old-brush squares the body closes round (where it crossed the coat) take their nearest
neighbours' colours. A brush lying on the ground (the deaths) keeps its point where it lay and is shortened from the
butt.
"""
import math

import numpy as np
from scipy import ndimage

K = (10, 0, 14)                                   # the outline
# (u from, u to, half width at the start, at the end, shades lit -> dark): the design's brush, grip at u 0, point 26.5
PARTS = [
    (-5.0, -4.0, 1.4, 1.4, [(252, 186, 47), (224, 150, 40)]),                  # the butt's gold cap
    (-4.0, 6.0, 1.5, 1.5, [(118, 66, 39), (92, 49, 38), (70, 34, 37)]),        # the shaft
    (6.0, 8.0, 1.7, 1.7, [(252, 186, 47), (188, 34, 37), (154, 26, 31)]),      # gold and crimson band
    (8.0, 10.0, 1.7, 1.7, [(26, 54, 136), (19, 34, 78), (12, 15, 38)]),        # navy ring
    (10.0, 12.0, 1.7, 1.8, [(0, 198, 220), (4, 162, 176)]),                    # teal ring
    (12.0, 13.0, 2.0, 2.4, [(253, 223, 193), (242, 184, 148)]),                # pale ring
    (13.0, 16.5, 2.7, 3.5, [(188, 34, 37), (154, 26, 31)]),                    # the crimson head
    (16.5, 22.0, 3.4, 3.0, [(37, 85, 166), (31, 70, 109), (19, 34, 78)]),      # the navy bristles
    (22.0, 26.5, 2.8, 0.5, [(253, 223, 193), (242, 184, 148)]),                # the wooden point
]
TIP = 26.5
BUTT = -5.0
HAND = 2.5                                        # |u| round the grip kept as Codex drew it (the fingers)
OVERSHOOT = 2.0                                   # the old brush cleared this far past its read ends
SPECK = 30                                        # loose bits near the old brush, up to this many squares, go


def frame(G, deg):
    """The brush's axis u (grip -> point) and its side v, v pointing up (the lit side)."""
    r = math.radians(deg)
    u = (math.sin(r), math.cos(r))                # 0 deg straight down, 90 to the image right
    v = (u[1], -u[0])
    if v[1] > 0 or (abs(v[1]) < 1e-6 and v[0] > 0):
        v = (-v[0], -v[1])
    return u, v


def part_at(t):
    for p in PARTS:
        if p[0] <= t < p[1] or (p is PARTS[-1] and t <= p[1]):
            return p
    return None


def half_width(p, t):
    a, b, w0, w1, _ = p
    k = 0.0 if b == a else (t - a) / (b - a)
    return w0 + (w1 - w0) * min(1.0, max(0.0, k))


def render(shape, G, deg, t_from=BUTT, t_to=TIP):
    """(RGBA layer of the brush, its mask) on a canvas of `shape` (rows, columns), grip G (square edges) and direction
    deg; only the part t_from..t_to of the axis."""
    H, W = shape
    u, v = frame(G, deg)
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5 - G[0], yy + 0.5 - G[1]
    t = px * u[0] + py * u[1]
    s = px * v[0] + py * v[1]
    out = np.zeros((H, W, 4), np.uint8)
    inner = np.zeros((H, W), bool)
    for p in PARTS:
        a, b = max(p[0], t_from), min(p[1], t_to)
        if a >= b:
            continue
        m = (t >= a) & (t < b) if p is not PARTS[-1] else (t >= a) & (t <= b)
        w = np.vectorize(lambda tt: half_width(p, tt))(t[m]) if m.any() else None
        if w is None:
            continue
        sm = s[m]
        ins = np.abs(sm) <= w - 0.5
        idx = np.nonzero(m)
        iy, ix = idx[0][ins], idx[1][ins]
        sh = p[4]
        ss = sm[ins] / np.maximum(w[ins], 1e-6)
        if len(sh) == 3:
            k = np.where(ss > 0.33, 0, np.where(ss < -0.33, 2, 1))
        else:
            k = np.where(ss > 0.0, 0, 1)
        cols = np.asarray(sh)[k]
        out[iy, ix, :3] = cols
        out[iy, ix, 3] = 255
        inner[iy, ix] = True
    # the outline: squares next to the brush's inside (8-neighbours), within the axis's reach
    ring = ndimage.binary_dilation(inner, np.ones((3, 3), bool)) & ~inner
    reach = (t >= t_from - 1.0) & (t <= t_to + 1.0)
    ring &= reach
    out[ring, :3] = K
    out[ring, 3] = 255
    return out, inner | ring


def capsule(shape, a, b, r):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5, yy + 0.5
    vx, vy = b[0] - a[0], b[1] - a[1]
    L2 = max(vx * vx + vy * vy, 1e-9)
    t = np.clip(((px - a[0]) * vx + (py - a[1]) * vy) / L2, 0, 1)
    return (px - a[0] - t * vx) ** 2 + (py - a[1] - t * vy) ** 2 <= r * r


def inpaint(fig, holes):
    """Each hole square the colour of its nearest kept square (the coat round where the brush crossed it)."""
    if not holes.any():
        return fig
    have = (fig[..., 3] > 0) & ~holes
    _, (iy, ix) = ndimage.distance_transform_edt(~have, return_indices=True)
    out = fig.copy()
    out[holes] = fig[iy[holes], ix[holes]]
    out[holes, 3] = 255
    return out


SHAFT_R = 2.4                                     # the old shaft's half width to clear near the hand
HEAD_FROM = 9.0                                   # u past which the old brush is its head (cleared as wide as drawn)


def refine(fig, spec, reach=6.0):
    """The old brush's head as drawn, near the hand-read one (read at 7x, a square or two off; Codex's heads 6-8 squares
    wide): its squares within `reach` of the read segment past HEAD_FROM -> (the direction from the read grip through
    their middle, the point's end along it, the head's half width: the 95th percentile of their distance from that line
    plus 1.0). A lying brush (no grip): all its squares, their main direction (PCA) -> (None, point, butt, half width)."""
    G = spec.get("grip")
    T = spec["tip"]
    A = G if G is not None else spec["butt"]
    vx, vy = T[0] - A[0], T[1] - A[1]
    L = math.hypot(vx, vy)
    ux, uy = vx / L, vy / L
    ys, xs = np.nonzero(fig[..., 3] > 0)
    P = np.stack([xs + 0.5, ys + 0.5], 1)
    rel = P - np.array(A, float)
    t = rel @ np.array([ux, uy])
    s = rel @ np.array([-uy, ux])
    if G is None:
        m = (np.abs(s) <= reach) & (t >= -3.0) & (t <= L + 3.0)
        Q = P[m]
        c = Q.mean(0)
        w, vecs = np.linalg.eigh(np.cov((Q - c).T))
        d = vecs[:, int(np.argmax(w))]
        if d[0] * ux + d[1] * uy < 0:
            d = -d
        tt = (Q - c) @ d
        ss = (Q - c) @ np.array([-d[1], d[0]])
        return None, tuple(c + d * tt.max()), tuple(c + d * tt.min()), float(np.percentile(np.abs(ss), 95)) + 1.0
    m = (np.abs(s) <= reach) & (t >= HEAD_FROM) & (t <= L + 3.0)
    c = P[m].mean(0)
    d = c - np.array(G, float)
    d /= np.linalg.norm(d)
    rel = P - np.array(G, float)
    tt = rel @ d
    ss = rel @ np.array([-d[1], d[0]])
    near = (np.abs(ss) <= 4.0) & (tt >= HEAD_FROM)
    tip = np.array(G, float) + d * tt[near].max()
    head = (np.abs(ss) <= reach) & (tt >= HEAD_FROM) & (tt <= tt[near].max() + 1.0)
    return tuple(G), tuple(tip), spec.get("butt"), float(np.percentile(np.abs(ss[head]), 95)) + 1.0


def normalize(fig, spec, pad=12):
    """The pose's brush at the design's length -> (figure, the grip and the direction on the returned figure, its
    offset: what was added on the left / top). spec: grip (x, y) or None for a brush lying on the ground, tip (x, y),
    butt (x, y) or None (hidden in the sleeve), r: the old brush's half width to clear (default 3.6)."""
    grip, tip, butt, r_fit = refine(fig, spec)
    spec = dict(spec, grip=grip, tip=tip, butt=butt, r=max(spec.get("r", 0.0), r_fit))
    f = np.pad(fig, ((pad, pad), (pad, pad), (0, 0)))
    sh = (pad, pad)
    T = (spec["tip"][0] + sh[0], spec["tip"][1] + sh[1])
    if spec.get("grip") is None:                     # lying: the point kept, the length from the butt
        B0 = (spec["butt"][0] + sh[0], spec["butt"][1] + sh[1])
        deg = math.degrees(math.atan2(T[0] - B0[0], T[1] - B0[1]))
        u, _ = frame(T, deg)
        G = (T[0] - TIP * u[0], T[1] - TIP * u[1])
        B0 = (B0[0] - OVERSHOOT * u[0], B0[1] - OVERSHOOT * u[1])
        T2 = (T[0] + OVERSHOOT * u[0], T[1] + OVERSHOOT * u[1])
        r = spec.get("r", 3.0)
        old = capsule(f.shape[:2], B0, T2, r)
        keep_hand = np.zeros(f.shape[:2], bool)
    else:
        G = (spec["grip"][0] + sh[0], spec["grip"][1] + sh[1])
        deg = math.degrees(math.atan2(T[0] - G[0], T[1] - G[1]))
        u, _ = frame(G, deg)
        T2 = (T[0] + OVERSHOOT * u[0], T[1] + OVERSHOOT * u[1])
        r = spec.get("r", 3.6)
        yy, xx = np.mgrid[0:f.shape[0], 0:f.shape[1]]
        t = (xx + 0.5 - G[0]) * u[0] + (yy + 0.5 - G[1]) * u[1]
        sd = np.abs(-(xx + 0.5 - G[0]) * u[1] + (yy + 0.5 - G[1]) * u[0])
        Lt = (T2[0] - G[0]) * u[0] + (T2[1] - G[1]) * u[1]
        old = (t > HAND) & (t <= Lt) & (sd <= np.where(t < HEAD_FROM, SHAFT_R, r))
        if spec.get("butt"):                          # the old butt past the new one (along the forearm: narrow)
            Bt = (spec["butt"][0] + sh[0] - G[0]) * u[0] + (spec["butt"][1] + sh[1] - G[1]) * u[1] - OVERSHOOT
            old |= (t < BUTT - 0.5) & (t >= Bt) & (sd <= SHAFT_R - 0.4)
        B0 = (G[0] + min(Bt if spec.get("butt") else 0.0, 0.0) * u[0],
              G[1] + min(Bt if spec.get("butt") else 0.0, 0.0) * u[1])
        keep_hand = (np.abs(t) <= HAND) & (sd <= r)
    op = f[..., 3] > 0
    cleared = old & op & ~keep_hand
    hand = f.copy()
    g = f.copy()
    g[cleared] = 0
    body = ndimage.binary_fill_holes(g[..., 3] > 0)
    holes = cleared & body                           # crossed the coat: filled from round it
    g = inpaint(g, holes)
    # behind the hand: the butt where Codex showed one, nothing where its sleeve hid it (the design's way)
    layer, m = render(f.shape[:2], G, deg, t_from=BUTT if spec.get("butt") or spec.get("grip") is None else -HAND)
    g[m] = layer[m]
    if spec.get("grip") is not None:                 # the fingers back over the shaft
        hm = keep_hand & op
        g[hm] = hand[hm]
    # bits of the old brush outside the cleared capsule (its outline's corners, a wider head): small pieces near it
    # that do not touch the figure's main piece
    near = capsule(f.shape[:2], B0, T2, r + 4.0)
    lbl, n = ndimage.label(g[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        size = ndimage.sum(g[..., 3] > 0, lbl, range(1, n + 1))
        main = 1 + int(np.argmax(size))
        for j in range(1, n + 1):
            if j != main and size[j - 1] <= SPECK and (near & (lbl == j)).any():
                g[lbl == j] = 0
    ys, xs = np.nonzero(g[..., 3] > 0)
    y0, x0 = ys.min(), xs.min()
    g = g[y0:ys.max() + 1, x0:xs.max() + 1]
    off = (pad - x0, pad - y0)
    return g, ((G[0] - x0, G[1] - y0), deg), off
