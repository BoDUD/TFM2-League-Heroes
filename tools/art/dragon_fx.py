"""The dragons' attack and death effects, drawn square by square on the frames' grid (one square = one dense pixel) as
pixel art: a few flat tones of the element, a dark outline, no blur, no half-transparent pixels (the user, 2026-11-10:
「小龙攻击的时候火焰不够大啊 看不出来在攻击」「大龙 远古龙应该也是 看不出喷射的火焰」「大龙的死亡帧还是没有」).

- breath(): a drake's / the Elder's breath, a cone from its mouth down onto the ground in front of its feet;
- burst(): the blast where the breath lands;
- wave(): the native serpen's shockwave (its attack frames 3-5 draw a ring round itself, radius 96 / 98 / 111 game px)
  made of the element: flames, water crests, rock spikes, wind curls, sparks, goo;
- spit() / splash(): Baron's acid spat at the side he bites at, and its splash on the target;
- sink(): Baron's death - he slumps back into his pit, melting at the pit line.

Every shape is a "heat" field (1 in the middle, 0 at its edge) the tones are cut from; the fields are bent by value noise
so flames lick and water ripples. Deterministic: every call takes its own seed.
"""
import math

import numpy as np
from scipy import ndimage
from skimage.draw import line as sk_line, polygon as sk_polygon

# outline, deep, base, light, highlight, core
TONES = {
    "infernal": [(66, 12, 8), (164, 34, 16), (234, 96, 24), (255, 168, 48), (255, 226, 118), (255, 251, 212)],
    "elder": [(30, 10, 54), (88, 36, 156), (146, 82, 232), (96, 206, 248), (186, 244, 255), (248, 255, 255)],
    "ocean": [(6, 38, 58), (18, 100, 138), (34, 166, 198), (104, 222, 236), (196, 248, 252), (255, 255, 255)],
    "mountain": [(48, 32, 20), (106, 72, 44), (160, 118, 74), (204, 170, 116), (234, 214, 170), (250, 242, 218)],
    "cloud": [(58, 74, 100), (124, 148, 184), (178, 202, 230), (218, 234, 250), (244, 250, 255), (255, 255, 255)],
    "hextech": [(22, 20, 78), (48, 66, 196), (76, 144, 255), (146, 216, 255), (218, 246, 255), (255, 255, 255)],
    "chemtech": [(22, 44, 10), (62, 116, 20), (124, 196, 34), (186, 238, 76), (230, 255, 156), (250, 255, 218)],
    "baron": [(34, 8, 46), (96, 28, 126), (176, 46, 194), (234, 94, 224), (255, 170, 246), (255, 230, 255)],
    "smoke": [(30, 26, 30), (64, 58, 64), (96, 90, 96), (130, 124, 128), (164, 160, 162), (194, 192, 194)],
}
ROCK = [(36, 30, 28), (78, 68, 62), (118, 106, 96), (162, 150, 136), (204, 194, 180)]   # outline, dark .. light
BARON_TEAL = [(16, 66, 70), (54, 176, 170), (150, 244, 232)]

KIND = {"infernal": "fire", "elder": "fire", "ocean": "water", "mountain": "rock", "cloud": "wind",
        "hextech": "bolt", "chemtech": "goo", "baron": "goo"}


def tones(el):
    return [np.array(t, np.uint8) for t in TONES[el]]


class Noise:
    """smooth value noise on a 128 x 128 lattice (wrapping), sampled anywhere"""

    def __init__(self, seed, n=128):
        self.g = np.random.default_rng(seed).random((n, n))
        self.n = n

    def __call__(self, u, v):
        n = self.n
        x0 = np.floor(u).astype(int)
        y0 = np.floor(v).astype(int)
        fx = u - x0
        fy = v - y0
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        x0 %= n
        y0 %= n
        x1 = (x0 + 1) % n
        y1 = (y0 + 1) % n
        g = self.g
        top = g[y0, x0] + (g[y0, x1] - g[y0, x0]) * fx
        bot = g[y1, x0] + (g[y1, x1] - g[y1, x0]) * fx
        return top + (bot - top) * fy

    def fbm(self, u, v, octaves=3):
        s, amp, tot = 0.0, 1.0, 0.0
        for o in range(octaves):
            s = s + amp * self(u * 2 ** o + 17.3 * o, v * 2 ** o + 9.1 * o)
            tot += amp
            amp *= 0.5
        return s / tot


def grid(shape):
    H, W = shape
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    return xx + 0.5, yy + 0.5


CROSS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)


def clean(m, least=4):
    """a mask without specks (pieces under `least` squares) and pinholes"""
    lbl, n = ndimage.label(m, structure=CROSS)
    if n:
        sz = ndimage.sum(m, lbl, range(1, n + 1))
        m = np.isin(lbl, 1 + np.nonzero(sz >= least)[0])
    holes = ndimage.binary_fill_holes(m) & ~m
    lbl, n = ndimage.label(holes, structure=CROSS)
    if n:
        sz = ndimage.sum(holes, lbl, range(1, n + 1))
        m = m | np.isin(lbl, 1 + np.nonzero(sz <= 2)[0])
    return m


def paint(heat, el, cuts, outline=True, least=4):
    """the field cut into the element's tones: heat > cuts[0] drawn, deep / base / light / highlight / core above each
    cut, the drawn shape's edge the outline tone"""
    t = tones(el)
    m = clean(heat > cuts[0], least)
    idx = np.zeros(heat.shape, int)
    for k, c in enumerate(cuts):
        idx[heat > c] = k + 1
    idx[~m] = 0
    idx[m & (idx == 0)] = 1
    out = np.zeros(heat.shape + (4,), np.uint8)
    for k in range(1, 6):
        mm = idx == k
        out[mm, :3] = t[k]
        out[mm, 3] = 255
    if outline:
        edge = m & ~ndimage.binary_erosion(m, structure=CROSS)
        out[edge, :3] = t[0]
    return out


def over(top, bottom):
    out = bottom.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def put(layer, ys, xs, rgb):
    H, W = layer.shape[:2]
    ok = (ys >= 0) & (ys < H) & (xs >= 0) & (xs < W)
    layer[ys[ok], xs[ok], :3] = rgb
    layer[ys[ok], xs[ok], 3] = 255


def disc(layer, cx, cy, r, fill, edge=None, hi=None):
    """a round blob (a drop, an ember, a bubble's body) with an outline and a highlight square up-left"""
    H, W = layer.shape[:2]
    x0, x1 = int(math.floor(cx - r - 1)), int(math.ceil(cx + r + 1))
    y0, y1 = int(math.floor(cy - r - 1)), int(math.ceil(cy + r + 1))
    if max(0, y0) >= min(H, y1) or max(0, x0) >= min(W, x1):
        return
    ys, xs = np.mgrid[max(0, y0):min(H, y1), max(0, x0):min(W, x1)]
    d = np.hypot(xs + 0.5 - cx, ys + 0.5 - cy)
    inside = d <= r
    if not inside.any():
        return
    put(layer, ys[inside], xs[inside], fill)
    if edge is not None and r >= 1.5:
        ring = inside & (d > r - 1.0)
        put(layer, ys[ring], xs[ring], edge)
    if hi is not None and r >= 2:
        put(layer, np.array([int(cy - r * 0.35)]), np.array([int(cx - r * 0.35)]), hi)


def ring_dot(layer, cx, cy, r, edge, hi):
    """a bubble: a ring with a highlight square"""
    H, W = layer.shape[:2]
    y0, y1, x0, x1 = max(0, int(cy - r - 2)), min(H, int(cy + r + 2)), max(0, int(cx - r - 2)), min(W, int(cx + r + 2))
    if y0 >= y1 or x0 >= x1:
        return
    ys, xs = np.mgrid[y0:y1, x0:x1]
    d = np.hypot(xs + 0.5 - cx, ys + 0.5 - cy)
    ring = (d <= r) & (d > r - 1.2)
    put(layer, ys[ring], xs[ring], edge)
    put(layer, np.array([int(cy - r * 0.4)]), np.array([int(cx - r * 0.4)]), hi)


def stroke(layer, pts, rgb, width=1):
    """a polyline `width` squares thick"""
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        rr, cc = sk_line(int(round(y0)), int(round(x0)), int(round(y1)), int(round(x1)))
        for oy in range(-(width // 2), width - width // 2):
            for ox in range(-(width // 2), width - width // 2):
                put(layer, rr + oy, cc + ox, rgb)


def outline_layer(layer, rgb):
    """an outline one square round everything drawn on the layer (the drawn squares untouched)"""
    m = layer[..., 3] > 0
    ring = ndimage.binary_dilation(m, structure=CROSS) & ~m
    out = layer.copy()
    out[ring, :3] = rgb
    out[ring, 3] = 255
    return out


def chunk(layer, cx, cy, r, rng, light_from=(-1, -1)):
    """a rock chunk: an irregular 5-7 sided stone, its face lit from up-left (light / mid / dark facets), outlined"""
    n = rng.integers(5, 8)
    ang = np.sort(rng.random(n)) * 2 * math.pi
    rad = r * (0.7 + 0.3 * rng.random(n))
    xs = cx + rad * np.cos(ang)
    ys = cy + rad * np.sin(ang) * 0.85
    rr, cc = sk_polygon(ys, xs, shape=layer.shape[:2])
    if len(rr) == 0:
        return
    m = np.zeros(layer.shape[:2], bool)
    m[rr, cc] = True
    gx, gy = cc + 0.5 - cx, rr + 0.5 - cy
    lit = gx * light_from[0] + gy * light_from[1]
    tone = np.where(lit > r * 0.25, 3, np.where(lit < -r * 0.25, 1, 2))
    for k in (1, 2, 3):
        sel = tone == k
        put(layer, rr[sel], cc[sel], np.array(ROCK[k], np.uint8))
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS)
    ys_, xs_ = np.nonzero(edge)
    put(layer, ys_, xs_, np.array(ROCK[0], np.uint8))


def zigzag(rng, p0, p1, segs, amp):
    """a lightning path from p0 to p1: `segs` straight legs, each joint thrown sideways up to `amp` squares"""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0) or 1.0
    nx, ny = -(y1 - y0) / L, (x1 - x0) / L
    pts = [(x0, y0)]
    for i in range(1, segs):
        t = i / segs
        o = (rng.random() * 2 - 1) * amp * (1 - abs(2 * t - 1) * 0.4)
        pts.append((x0 + (x1 - x0) * t + nx * o, y0 + (y1 - y0) * t + ny * o))
    pts.append((x1, y1))
    return pts


def bolt(layer, rng, p0, p1, el, segs=6, amp=6.0, fork=0.35, width=3):
    """a lightning bolt: a white core, a light rim (`width` squares in all), the outline; a fork or two off its joints"""
    t = tones(el)
    pts = zigzag(rng, p0, p1, segs, amp)
    tmp = np.zeros_like(layer)
    stroke(tmp, pts, t[4], width)
    stroke(tmp, pts, t[5], 1)
    for i in range(1, len(pts) - 1):
        if rng.random() < fork:
            x, y = pts[i]
            ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + (rng.random() - 0.5) * 2.2
            ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) * (0.15 + 0.2 * rng.random())
            q = (x + math.cos(ang) * ln, y + math.sin(ang) * ln)
            sub = zigzag(rng, (x, y), q, 3, amp * 0.5)
            stroke(tmp, sub, t[3], 2)
            stroke(tmp, sub, t[5], 1)
    return over(outline_layer(tmp, t[0]), layer)


# ---- the drakes' breath -------------------------------------------------------------------------------------------

def cone_coords(shape, a, b):
    """(t, s, L): t along a -> b (0 at a, 1 at b), s the signed distance sideways, L the length"""
    X, Y = grid(shape)
    (ax, ay), (bx, by) = a, b
    ux, uy = bx - ax, by - ay
    L = math.hypot(ux, uy)
    ux, uy = ux / L, uy / L
    px, py = X - ax, Y - ay
    return (px * ux + py * uy) / L, -px * uy + py * ux, L


def breath(shape, mouth, ground, el, phase, seed):
    """the breath, mouth -> ground: phase 0 the whole cone (it has just reached the ground), 1 its tail leaving the
    mouth (the cone from 40% of the way on, thinner), 2 nothing but what it leaves in the air"""
    kind = KIND[el]
    rng = np.random.default_rng(seed)
    out = np.zeros(shape + (4,), np.uint8)
    if phase >= 2:
        return out
    t, s, L = cone_coords(shape, mouth, ground)
    nz = Noise(seed)
    w0, w1 = (7.0, 30.0) if phase == 0 else (5.0, 24.0)
    w = w0 + (w1 - w0) * np.clip(t, 0, 1.15) ** 0.8
    t0, t1 = (0.0, 1.06) if phase == 0 else (0.42, 1.04)
    along = np.clip((t - t0) / 0.07, 0, 1) * np.clip((t1 - t) / 0.10, 0, 1)
    if kind == "bolt":
        # a faint electric cone, the bolts on it
        sl = np.abs(s) / (w * 0.8)
        heat = (1 - sl ** 2) * along * (0.55 + 0.5 * nz.fbm(t * L / 5 - phase * 4, s / 5))
        out = paint(heat, el, (0.08, 0.30, 0.62, 0.95, 1.5))
        a = (mouth[0] + (ground[0] - mouth[0]) * t0, mouth[1] + (ground[1] - mouth[1]) * t0)
        for k in range(3 if phase == 0 else 2):
            off = (k - 1) * w1 * 0.45
            end = (ground[0] + off, ground[1] + rng.uniform(-4, 4))
            out = bolt(out, rng, a, end, el, segs=6, amp=7.0)
        return out
    if kind == "wind":
        cell, wob = 9.0, 0.30
    elif kind == "water":
        cell, wob = 8.0, 0.18
    elif kind == "rock":
        cell, wob = 6.0, 0.40
    elif kind == "goo":
        cell, wob = 7.0, 0.30
    else:
        cell, wob = 6.0, 0.5
    if kind == "fire":
        # flames: wider, licking edges, streaks along the flow, mostly orange with a yellow-white heart
        w = w * 1.25
        turb = (nz.fbm(t * L / 11.0 - phase * 3.0, s / 6.0) - 0.5) * 2
        sl = np.abs(s + turb * w * wob) / w
        streak = nz.fbm(t * L / 14.0 - phase * 4.0, s / 3.5 + 40)
        heat = (1 - sl ** 1.3) * along * (0.5 + 0.75 * streak)
        heat *= 1.0 - 0.3 * np.clip(t, 0, 1)
        return paint(heat, el, (0.04, 0.3, 0.52, 0.72, 0.88))
    turb = (nz.fbm(t * L / cell - phase * 3.0, s / cell) - 0.5) * 2
    sl = np.abs(s + turb * w * wob) / w
    heat = (1 - sl ** 1.6) * along
    heat *= 0.72 + 0.56 * nz.fbm(t * L / (cell * 0.7) - phase * 5.0, s / (cell * 0.7) + 40)
    heat *= 1.0 - 0.22 * np.clip(t, 0, 1)
    if kind == "fire":
        out = paint(heat, el, (0.0, 0.16, 0.38, 0.60, 0.80))
    elif kind == "water":
        out = paint(heat, el, (0.0, 0.18, 0.42, 0.72, 0.92))
        # streaks along the flow
        X, Y = grid(shape)
        streak = (np.abs(((s + 2.0 * np.sin(t * L / 7.0 + phase)) / 6.0) % 1.0 - 0.5) < 0.09) & (heat > 0.3) & (sl < 0.8)
        out[streak, :3] = tones(el)[4]
        for _ in range(10):
            tt = rng.uniform(t0 + 0.15, 1.0)
            side = rng.choice([-1, 1]) * rng.uniform(0.9, 1.5)
            x = mouth[0] + (ground[0] - mouth[0]) * tt
            y = mouth[1] + (ground[1] - mouth[1]) * tt
            ww = w0 + (w1 - w0) * tt ** 0.8
            disc(out, x + side * ww, y + rng.uniform(-3, 3), rng.uniform(1.6, 2.6), tones(el)[3], tones(el)[0], tones(el)[5])
    elif kind == "rock":
        out = paint(heat * 0.9, el, (0.0, 0.22, 0.48, 0.74, 1.5))
        for _ in range(9 if phase == 0 else 6):
            tt = rng.uniform(t0 + 0.1, 1.0)
            ww = w0 + (w1 - w0) * tt ** 0.8
            x = mouth[0] + (ground[0] - mouth[0]) * tt + rng.uniform(-0.8, 0.8) * ww
            y = mouth[1] + (ground[1] - mouth[1]) * tt
            chunk(out, x, y, rng.uniform(2.5, 5.0), rng)
    elif kind == "wind":
        out = paint(heat, el, (0.05, 0.25, 0.50, 0.78, 1.5))
        for k in range(4):
            tt = t0 + (k + 0.6) / 4.6 * (1.0 - t0)
            x = mouth[0] + (ground[0] - mouth[0]) * tt
            y = mouth[1] + (ground[1] - mouth[1]) * tt
            r = 3.0 + 6.0 * tt
            curl(out, x + rng.uniform(-3, 3), y, r, el, rng.random() < 0.5)
    else:  # goo
        blobs = nz.fbm(t * L / 9.0 - phase * 2.0, s / 9.0 + 70) > 0.42
        heat = np.where(blobs | (sl < 0.55), heat, heat * 0.2)
        out = paint(heat, el, (0.08, 0.26, 0.52, 0.80, 1.5))
        for _ in range(7):
            tt = rng.uniform(t0 + 0.1, 1.0)
            ww = w0 + (w1 - w0) * tt ** 0.8
            x = mouth[0] + (ground[0] - mouth[0]) * tt + rng.uniform(-1.3, 1.3) * ww
            y = mouth[1] + (ground[1] - mouth[1]) * tt
            ring_dot(out, x, y, rng.uniform(1.8, 3.2), tones(el)[0], tones(el)[5])
    return out


def curl(layer, cx, cy, r, el, flip):
    """a wind curl: a spiral stroke (light core on a deep rim)"""
    t = tones(el)
    pts = []
    turns = 1.25
    for i in range(28):
        a = i / 27 * turns * 2 * math.pi
        rr = r * (1 - i / 27 * 0.75)
        x = cx + rr * math.cos(a) * (-1 if flip else 1)
        y = cy + rr * math.sin(a) * 0.7
        pts.append((x, y))
    tmp = np.zeros_like(layer)
    stroke(tmp, pts, t[4], 2)
    tmp = outline_layer(tmp, t[1])
    layer[...] = over(tmp, layer)


def burst(shape, centre, R, el, phase, seed):
    """the blast on the ground where the breath lands: a flat base (R wide, 0.42 R deep) and the element rising out of
    it; phase 0 it starts (0.7 R), 1 at full size, 2 dying down (lower, darker, broken)"""
    kind = KIND[el]
    rng = np.random.default_rng(seed)
    X, Y = grid(shape)
    cx, cy = centre
    size = (0.72, 1.0, 1.05)[phase]
    R = R * size
    dx = (X - cx) / R
    dy = (Y - cy) / R
    nz = Noise(seed + 1)
    if kind == "bolt":
        ang = np.arctan2(dy + 0.3, dx)
        r = np.hypot(dx, (dy + 0.3) / 0.9)
        jag = 0.5 * (0.65 + 0.7 * nz.fbm(np.cos(ang) * 3.0 + 3 + phase, np.sin(ang) * 3.0 + 3))
        flash = (1 - r / jag) * (1.25, 1.15, 0.7)[phase]
        glow = (1 - np.hypot(dx / 1.25, dy / 0.4)) * (0.55, 0.6, 0.45)[phase]
        out = paint(np.maximum(flash, glow), el, (0.03, 0.25, 0.5, 0.72, 0.88))
        for k in range((7, 9, 5)[phase]):
            a = (k + rng.uniform(-0.3, 0.3)) / (7, 9, 5)[phase] * 2 * math.pi
            ln = R * rng.uniform(1.0, 1.7)
            out = bolt(out, rng, (cx, cy - R * 0.3), (cx + math.cos(a) * ln * 1.15, cy - R * 0.3 + math.sin(a) * ln * 0.7),
                       el, segs=5, amp=3.5, fork=0.3, width=2)
        return out
    t = tones(el)
    lift = (0.0, 0.12, 0.4)[phase]
    ground = 1 - np.hypot(dx / 1.15, dy / 0.4)
    body = billows(X, Y, cx, cy - lift * R, R, rng, 8)
    churn = nz.fbm(X / 6.0, Y / 8.0 + phase * 2.5)
    if kind == "fire":
        if phase < 2:
            heat = np.maximum(ground * 0.8, body) * (0.55 + 0.7 * churn)
            out = paint(heat, el, (0.04, 0.24, 0.46, 0.66, 0.84))
        else:
            # dying: the fire breaks up and sinks to embers, darker
            heat = np.maximum(ground * 0.75, body * 0.62) * (0.5 + 0.75 * churn)
            out = paint(heat, el, (0.12, 0.32, 0.56, 0.8, 1.5))
        for _ in range((10, 16, 18)[phase]):
            ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
            d = R * rng.uniform(0.9, 1.7)
            disc(out, cx + math.cos(ang) * d * 1.1, cy + math.sin(ang) * d - lift * R * 2, rng.uniform(0.8, 1.5), t[4])
    elif kind == "water":
        heat = ground * 0.8
        cols = [(0.0, 1.05, 0.26)] + [(rng.uniform(-1, 1), rng.uniform(0.35, 0.8), rng.uniform(0.14, 0.22)) for _ in range(11)]
        for ox, hh, ww in cols:
            bx, by = cx + ox * R, cy + abs(ox) * R * 0.12 - R * 0.05
            h = hh * R * (0.85, 1.1, 0.75)[phase]
            v = (by - Y) / h
            hw = ww * R * np.sqrt(np.clip(1 - v ** 4, 0, 1)) * (v > -0.4)
            f = np.clip(1 - (np.abs(X - bx) / np.maximum(hw, 1e-3)) ** 2, 0, 1) * np.clip(1 - np.abs(v) ** 2, 0, 1) * (v < 1)
            heat = np.maximum(heat, f)
        heat *= 0.7 + 0.5 * churn
        out = paint(heat, el, (0.04, 0.24, 0.48, 0.74, 0.92))
        for _ in range((12, 18, 14)[phase]):
            ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
            d = R * rng.uniform(0.9, 1.7)
            disc(out, cx + math.cos(ang) * d * 1.15, cy + math.sin(ang) * d * (1.0 + phase * 0.2) + phase * 6,
                 rng.uniform(1.6, 2.8), t[3], t[0], t[5])
    elif kind == "rock":
        dust = np.maximum(ground * 0.85, body * 0.8) * (0.55 + 0.6 * churn)
        out = paint(dust, el, (0.06, 0.26, 0.5, 0.74, 1.5))
        if phase >= 1:
            for k, ox in enumerate((-0.55, 0.0, 0.5)):
                spike(out, cx + ox * R, cy + abs(ox) * R * 0.1, R * 0.22, R * (0.9 if ox == 0 else 0.6), rng)
        for _ in range((8, 12, 10)[phase]):
            ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
            d = R * rng.uniform(0.7, 1.6) * (1 + 0.25 * phase)
            chunk(out, cx + math.cos(ang) * d * 1.1, cy + math.sin(ang) * d, rng.uniform(2.5, 5.5), rng)
    elif kind == "wind":
        heat = np.maximum(ground * 0.7, body * 0.75) * (0.55 + 0.6 * churn)
        out = paint(heat, el, (0.08, 0.3, 0.55, 0.8, 1.5))
        for k in range((3, 5, 4)[phase]):
            ang = rng.uniform(-math.pi, 0)
            d = R * rng.uniform(0.3, 0.9)
            curl(out, cx + math.cos(ang) * d, cy + math.sin(ang) * d * 0.8 - lift * R, R * rng.uniform(0.25, 0.4), el,
                 k % 2 == 0)
    else:  # goo
        blobs = nz.fbm(X / 8.0 + 30, Y / 8.0 + phase) > 0.46
        heat = np.maximum(ground * 0.85, body) * (0.6 + 0.5 * churn)
        heat = np.where(blobs | (heat > 0.35), heat, 0)
        out = paint(heat, el, (0.06, 0.26, 0.52, 0.80, 1.5))
        for _ in range((8, 12, 10)[phase]):
            ang = rng.uniform(-math.pi, 0)
            d = R * rng.uniform(0.8, 1.5)
            disc(out, cx + math.cos(ang) * d * 1.1, cy + math.sin(ang) * d * 0.9, rng.uniform(1.5, 2.6), t[3], t[0], t[5])
        for _ in range(5):
            ring_dot(out, cx + rng.uniform(-0.8, 0.8) * R, cy - rng.uniform(0.2, 1.2) * R, rng.uniform(2, 3.4), t[0], t[5])
    return out


def billows(X, Y, cx, cy, R, rng, n):
    """a heap of round puffs over (cx, cy): a big one in the middle and `n` round its upper half - a blast's body"""
    pts = [(0.0, -0.15 * R, 0.6 * R)]
    for _ in range(n):
        ang = rng.uniform(-math.pi * 0.97, -math.pi * 0.03)
        d = rng.uniform(0.3, 0.8) * R
        pts.append((math.cos(ang) * d * 1.2, math.sin(ang) * d * 0.95, rng.uniform(0.3, 0.52) * R))
    heat = np.zeros_like(X)
    for ox, oy, r in pts:
        heat = np.maximum(heat, 1 - np.hypot(X - cx - ox, Y - cy - oy) / r)
    return heat


# ---- the shockwave ring --------------------------------------------------------------------------------------------

def wave(shape, anchor, radius, el, phase, seed):
    """the shockwave round the anchor made of the element: a ground band and, every ~11 squares round the circle,
    something rising from it - flame tongues, water crests, dust puffs with rock spikes, cloud puffs with wind curls,
    sparks, goo with bubbles; phase 0 the first ring, 1 the second (taller), 2 the last (low, darker, every other one)"""
    kind = KIND[el]
    rng = np.random.default_rng(seed)
    X, Y = grid(shape)
    ax, ay = anchor
    d = np.hypot(X - ax, Y - ay)
    band = ((9.0, 8.0, 5.0) if kind == "bolt" else (7.0, 6.0, 4.0))[phase]
    line = 1 - np.abs(d - radius) / (band / 2)
    H0 = (26.0, 32.0, 18.0)[phase]
    spacing = 11.0
    n = int(2 * math.pi * radius / spacing)
    if kind == "bolt":
        heat = np.where(line > 0, 0.35 + 0.65 * line, 0.0)
    else:
        heat = np.where(line > 0, 0.55 + 0.1 * line, 0.0)
    t = tones(el)
    tongues = []
    for i in range(n):
        if phase == 2 and i % 2:
            continue
        a = (i + rng.uniform(-0.3, 0.3)) / n * 2 * math.pi
        tongues.append((ax + radius * math.cos(a), ay + radius * math.sin(a), H0 * rng.uniform(0.42, 1.0),
                        spacing * rng.uniform(0.45, 0.62), rng.uniform(-0.25, 0.25)))
    if kind != "bolt":
        for bx, by, h, w, bend in tongues:
            sub = (slice(max(0, int(by - h - 5)), max(0, int(by + w + 5))),
                   slice(max(0, int(bx - 1.4 * w - 4)), max(0, int(bx + 1.4 * w + 5))))
            xs, ys = X[sub], Y[sub]
            v = (by - ys) / h
            if kind == "fire":
                vv = np.clip(v, 0, 1)
                hw = np.where(v >= 0, w * (1 - vv) ** 1.2 * (1 + 1.2 * vv), w * np.sqrt(np.clip(1 - (v / 0.3) ** 2, 0, 1)))
                lat = np.abs(xs - bx - bend * h * vv ** 2) / np.maximum(hw, 1e-3)
                f = np.clip(1 - lat ** 2, 0, 1) * np.clip(1 - vv ** 1.6, 0, 1) * (v > -0.3)
            elif kind == "water":
                hw = w * np.sqrt(np.clip(1 - v ** 4, 0, 1)) * (v > -0.35)
                lat = np.abs(xs - bx) / np.maximum(hw, 1e-3)
                f = np.clip(1 - lat ** 2, 0, 1) * np.clip(1 - np.abs(v) ** 2, 0, 1) * (v < 1)
            else:   # puffs: dust, cloud, goo
                pr = w * (1.1 if kind == "goo" else 1.3)
                rr = np.hypot(xs - bx, (ys - (by - h * 0.3)) / 1.05) / pr
                f = np.clip(1 - rr ** 2, 0, 1)
            heat[sub] = np.maximum(heat[sub], f)
    nz = Noise(seed + 2)
    heat *= 0.78 + 0.44 * nz.fbm(X / 5.0, Y / 7.0 + phase * 3)
    heat *= (1.0, 1.0, 0.75)[phase]
    cuts = {"fire": (0.05, 0.22, 0.45, 0.66, 0.86), "water": (0.05, 0.25, 0.5, 0.78, 0.94),
            "goo": (0.06, 0.28, 0.55, 0.82, 1.5), "rock": (0.06, 0.3, 0.56, 0.8, 1.5),
            "wind": (0.06, 0.3, 0.56, 0.8, 0.95), "bolt": (0.05, 0.3, 0.62, 0.9, 1.5)}[kind]
    out = paint(heat, el, cuts)
    if kind == "fire":
        for bx, by, h, w, bend in tongues[::3]:
            disc(out, bx + rng.uniform(-w, w), by - h * rng.uniform(1.05, 1.4), rng.uniform(0.7, 1.3), t[4])
    elif kind == "water":
        for bx, by, h, w, bend in tongues[::2]:
            disc(out, bx + rng.uniform(-w, w), by - h * rng.uniform(1.1, 1.5), rng.uniform(1.4, 2.4), t[3], t[0], t[5])
    elif kind == "goo":
        for bx, by, h, w, bend in tongues[::3]:
            ring_dot(out, bx + rng.uniform(-w, w), by - h * rng.uniform(0.9, 1.4), rng.uniform(2.2, 3.4), t[0], t[5])
    elif kind == "rock":
        for k, (bx, by, h, w, bend) in enumerate(tongues):
            if k % 2 == 0:
                spike(out, bx + rng.uniform(-2, 2), by + 1, w * 1.05, h * 1.05, rng)
        for bx, by, h, w, bend in tongues[1::4]:
            chunk(out, bx + rng.uniform(-w, w), by - h * rng.uniform(1.0, 1.4), rng.uniform(2.2, 3.8), rng)
    elif kind == "wind":
        for k, (bx, by, h, w, bend) in enumerate(tongues[::2]):
            curl(out, bx, by - h * 0.55, max(5.0, h * 0.45), el, k % 2 == 0)
    else:  # bolt
        for k, (bx, by, h, w, bend) in enumerate(tongues):
            if phase == 2 or k % 2 == 0:
                out = bolt(out, rng, (bx, by), (bx + rng.uniform(-w, w), by - h * rng.uniform(0.8, 1.15)), el, segs=3,
                           amp=3.0, fork=0.3, width=2)
    return out


def spike(layer, bx, by, w, h, rng):
    """a rock spike out of the ground: a triangle, its left face light, its right face dark, outlined"""
    lean = rng.uniform(-0.25, 0.25) * h
    tip = (bx + lean, by - h)
    xs = np.array([bx - w, tip[0], bx + w])
    ys = np.array([by + 1, tip[1], by + 1])
    rr, cc = sk_polygon(ys, xs, shape=layer.shape[:2])
    if len(rr) == 0:
        return
    m = np.zeros(layer.shape[:2], bool)
    m[rr, cc] = True
    # the ridge from the tip down the middle
    t = np.clip((by - (rr + 0.5)) / max(h, 1), 0, 1)
    ridge = bx + lean * t
    left = (cc + 0.5) < ridge
    put(layer, rr[left], cc[left], np.array(ROCK[3], np.uint8))
    put(layer, rr[~left], cc[~left], np.array(ROCK[1], np.uint8))
    edge = m & ~ndimage.binary_erosion(m, structure=CROSS)
    ys_, xs_ = np.nonzero(edge)
    put(layer, ys_, xs_, np.array(ROCK[0], np.uint8))


def charge(shape, mouth, el, seed):
    """the breath gathering in the open mouth (attack frame 2): a bright ball and sparks drawn into it"""
    rng = np.random.default_rng(seed)
    X, Y = grid(shape)
    r = np.hypot(X - mouth[0], Y - mouth[1])
    nz = Noise(seed)
    heat = (1 - r / 9.0) * (0.75 + 0.5 * nz.fbm(X / 3.0, Y / 3.0))
    out = paint(heat, el, (0.0, 0.2, 0.45, 0.7, 0.88))
    t = tones(el)
    for k in range(7):
        a = k / 7 * 2 * math.pi + rng.uniform(-0.3, 0.3)
        d0, d1 = rng.uniform(14, 20), rng.uniform(10, 12)
        p0 = (mouth[0] + math.cos(a) * d0, mouth[1] + math.sin(a) * d0)
        p1 = (mouth[0] + math.cos(a) * d1, mouth[1] + math.sin(a) * d1)
        stroke(out, [p0, p1], t[4], 1)
    return out


def drake_attack(frames, anchor, el, mouth, soles, rings, glow, seed=5):
    """a drake's / the Elder's 5 attack frames (padded canvases) with the breath: 2 gathering at `glow` (the jaws of
    the raised head), 3 the breath from `mouth` reaching the ground and the first ring, 4 the blast at full size and the
    ring further out, 5 the blast dying and the last ring"""
    shape = frames[0].shape[:2]
    ground = (mouth[0], soles + 46.0)
    out = []
    for i, a in enumerate(frames):
        if i == 1:
            a = over(charge(shape, glow, el, seed), a)
        if 2 <= i <= 4:
            ph = i - 2
            a = over(a, wave(shape, anchor, rings[ph], el, ph, seed + 10 * i))
            a = over(breath(shape, mouth, ground, el, ph, seed + i), a)
            a = over(burst(shape, ground, 40.0, el, ph, seed + 3 * i), a)
        out.append(a)
    return out


# ---- Baron ---------------------------------------------------------------------------------------------------------

def spit(shape, mouth, aim, phase, seed):
    """Baron's acid spat from `mouth` toward `aim`: phase 0 a gob gathering in the jaws, 1 the stream at full length
    (whole by the jaws, breaking into globs further out), 2 it torn off the jaws and in globs, 3 drops falling"""
    el = "baron"
    rng = np.random.default_rng(seed)
    t_ = tones(el)
    if phase == 0:
        return charge(shape, mouth, el, seed)
    out = np.zeros(shape + (4,), np.uint8)
    t, s, L = cone_coords(shape, mouth, aim)
    nz = Noise(seed)
    if phase < 3:
        t0, t1 = (0.0, 1.05) if phase == 1 else (0.36, 1.12)
        w = (4.0 + 15.0 * np.clip(t, 0, 1.15) ** 0.8) * (1.0 if phase == 1 else 0.85)
        turb = (nz.fbm(t * L / 9.0 - phase * 3, s / 6.0) - 0.5) * 2
        sl = np.abs(s + turb * w * 0.45) / w
        along = np.clip((t - t0) / 0.05, 0, 1)
        g = nz.fbm(t * L / 7.0 - phase * 2.0, s / 6.0 + 70)
        bar = np.clip((t - (0.45 if phase == 1 else 0.3)) / 0.6, 0, 1) * 0.5
        heat = (1 - sl ** 1.4) * along * (0.55 + 0.7 * g) * np.clip((t1 + 0.1 - t) / 0.22, 0, 1)
        heat = np.where(g > 0.24 + bar, heat, 0)
        out = paint(heat, el, (0.1, 0.32, 0.6, 0.86, 1.5), least=6)
        glint = (heat > 0.55) & (nz(t * L / 3.0, s / 3.0 + 99) > 0.8)
        out[glint, :3] = BARON_TEAL[2]
    n = {1: 9, 2: 14, 3: 12}[phase]
    for _ in range(n):
        tt = rng.uniform(0.35, 1.2) if phase < 3 else rng.uniform(0.55, 1.3)
        ww = 4.0 + 15.0 * min(tt, 1.0) ** 0.8
        x = mouth[0] + (aim[0] - mouth[0]) * tt
        y = mouth[1] + (aim[1] - mouth[1]) * tt + rng.uniform(-1.3, 1.3) * ww + (10 if phase == 3 else 0)
        disc(out, x, y, rng.uniform(1.6, 3.0), t_[3], t_[0], t_[5])
    return out


def splash(phase, size=150, seed=61):
    """the acid hitting the target (the frame's centre): 7 frames - a flash, the splash crown rising and spreading,
    drops falling, a bubbling puddle shrinking away"""
    el = "baron"
    rng = np.random.default_rng(seed + phase)
    shape = (size, size)
    cx, cy = size / 2, size / 2 + 8
    X, Y = grid(shape)
    t_ = tones(el)
    nz = Noise(seed)
    out = np.zeros(shape + (4,), np.uint8)
    if phase == 0:
        dy = (Y - (cy - 6)) / 0.8
        r = np.hypot(X - cx, dy)
        ang = np.arctan2(dy, X - cx)
        edge = 11 + 10 * nz.fbm(np.cos(ang) * 1.6 + 5, np.sin(ang) * 1.6 + 5)
        return paint((1 - r / edge) * 1.1, el, (0.0, 0.25, 0.5, 0.75, 0.9))
    if phase in (1, 2, 3):
        return burst(shape, (cx, cy), 38.0, el, phase - 1, seed + phase)
    if phase in (1, 2, 3):
        R = (34.0, 48.0, 54.0)[phase - 1]
        dx, dy = (X - cx) / R, (Y - cy) / R
        base = 1 - np.hypot(dx, dy / 0.42)
        up = np.clip(-dy, 0, None)
        rise = (1.1, 1.0, 0.6)[phase - 1]
        # the crown: a ring of spikes round the splash's rim
        ang = np.arctan2(dy / 0.42, dx)
        rim = np.abs(np.hypot(dx, dy / 0.42) - 0.75) < 0.22
        spikes = np.clip(1 - up / (rise * (0.6 + 0.4 * np.abs(np.sin(ang * 5 + phase)))), 0, 1) * (np.abs(dx) < 1.0)
        col = np.where(dy < 0.2, spikes * np.clip(1 - np.abs(dx) / (0.35 + 0.65 * up / rise + 0.2), 0, 1), 0)
        heat = np.maximum(base * (1.1 if phase == 1 else 0.9), col * 0.9)
        heat = np.maximum(heat, np.where(rim & (dy < 0.3), 0.5, 0))
        heat *= 0.7 + 0.6 * nz.fbm(X / 6.0 + phase * 5, Y / 6.0)
        out = paint(heat, el, (0.06, 0.26, 0.52, 0.80, 0.95))
        for _ in range((10, 16, 12)[phase - 1]):
            a = rng.uniform(-math.pi, 0)
            d = R * rng.uniform(0.8, 1.5)
            fall = (0, 0, 10)[phase - 1]
            disc(out, cx + math.cos(a) * d * 1.2, cy + math.sin(a) * d * 0.9 + fall, rng.uniform(1.6, 3.0), t_[3], t_[0],
                 t_[5])
        glint = (heat > 0.6) & (nz(X / 3.0, Y / 3.0 + 50) > 0.8)
        out[glint, :3] = BARON_TEAL[2]
        return out
    # 4 .. 6: the puddle bubbling and shrinking
    R = (46.0, 38.0, 26.0)[phase - 4]
    dx, dy = (X - cx) / R, (Y - cy) / (R * 0.4)
    heat = (1 - np.hypot(dx, dy)) * (0.75 + 0.5 * nz.fbm(X / 7.0, Y / 4.0 + phase))
    out = paint(heat, el, (0.0, 0.3, 0.6, 0.85, 1.5))
    for _ in range((6, 4, 2)[phase - 4]):
        ring_dot(out, cx + rng.uniform(-0.7, 0.7) * R, cy - rng.uniform(2, 10), rng.uniform(1.8, 3.2), t_[0], t_[5])
    return out


def sink(frame, pit, steps, seed=71):
    """Baron's last death pose slumping back into his pit: one frame a step in `steps` (0 = standing, 1 = gone), the
    body lowered (the part under the pit line cut off), a glowing magenta seam where it melts into the pit, drops
    and dust thrown up off the seam"""
    rng = np.random.default_rng(seed)
    ys = np.nonzero(frame[..., 3].any(1))[0]
    top = ys.min()
    height = pit + 1 - top
    t_ = tones("baron")
    out = []
    for s in steps:
        dy = int(round(height * s))
        f = np.zeros_like(frame)
        if dy < frame.shape[0]:
            f[dy:] = frame[:frame.shape[0] - dy]
        f[pit + 1:] = 0
        m = f[..., 3] > 0
        cols = np.nonzero(m[max(0, pit - 1):pit + 1].any(0))[0]
        if len(cols):
            x0, x1 = cols.min(), cols.max()
            # the seam: the bottom two rows of what is left, lit
            for y, tone in ((pit, t_[4]), (pit - 1, t_[3])):
                row = m[y, x0:x1 + 1]
                xs = np.nonzero(row)[0] + x0
                put(f, np.full(len(xs), y), xs, tone)
            for _ in range(int(6 + 10 * (1 - s))):
                x = rng.uniform(x0, x1)
                disc(f, x, pit - rng.uniform(4, 18), rng.uniform(1.2, 2.4), t_[3], t_[0], t_[5])
        out.append(f)
    return out


def roar(shape, centre, radius, seed=81):
    """a purple shock ring round Baron as he screams (death frame 2)"""
    rng = np.random.default_rng(seed)
    X, Y = grid(shape)
    d = np.hypot(X - centre[0], (Y - centre[1]) / 0.55)
    nz = Noise(seed)
    heat = (1 - np.abs(d - radius) / 5.0) * (0.7 + 0.6 * nz.fbm(X / 6.0, Y / 6.0))
    return paint(heat, "baron", (0.15, 0.4, 0.7, 0.9, 1.5))
