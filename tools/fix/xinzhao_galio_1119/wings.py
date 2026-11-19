"""Galio's wings flap (the user, 2026-11-19: 「接下来改加里奥吧 走路时翅膀不动 待机也是」). In his 8 run frames both wings
are one sprite moved up / down with the body (100 % of their pixels equal at an offset); the stance has its own pair.
A wing = its warm pixels (gold / orange / brown feathers) in its zone + the dark outline touching them; it turns as a
rigid piece about its root behind the shoulder (RotSprite: Scale2x x3, rotate, sample the 8 x 8 centres) and goes back
BEHIND the body: drawn only where the frame is clear once the old wing is lifted. Where the wing left a body pixel
without its outline, the outline is put back. Nothing of the body moves.

    template(c, zones) -> {side: (pixels mask, root)}
    flap(c, tmpl, offset, angles) -> picture
"""
import numpy as np

OUT = (8, 10, 17, 255)


def warm(p):
    r, g, b = int(p[0]), int(p[1]), int(p[2])
    return p[3] > 0 and r > 90 and r >= g and g > b + 15


def dark(p):
    return p[3] > 0 and int(p[0]) + int(p[1]) + int(p[2]) < 80


def inside(poly, x, y):
    """point in polygon (pixel centre)"""
    px, py = x + 0.5, y + 0.5
    n, ins = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > py) != (y2 > py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
            ins = not ins
    return ins


def template(c, polys):
    """polys: {side: (polygon, root)}. The wing = the warm pixels inside its polygon that connect (8-way, through warm
    pixels) to the polygon's largest warm piece (the feathers; gold trims on the arm or the shoulder are other pieces),
    plus its own outline: dark pixels reached from them through dark pixels that touch no body pixel (a dark pixel next
    to the stone body is the body's outline and stays with the body)."""
    h, w = c.shape[:2]
    out = {}
    op = c[..., 3] > 0
    W = np.zeros((h, w), bool); K = np.zeros((h, w), bool)
    for y in range(h):
        for x in range(w):
            if op[y, x]:
                W[y, x] = warm(c[y, x]); K[y, x] = dark(c[y, x])
    body = op & ~W & ~K
    nbr8 = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
    for side, (poly, root) in polys.items():
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        inpoly = np.zeros((h, w), bool)
        for y in range(max(0, int(min(ys))), min(h, int(max(ys)) + 1)):
            for x in range(max(0, int(min(xs))), min(w, int(max(xs)) + 1)):
                inpoly[y, x] = inside(poly, x, y)
        cand = W & inpoly
        # largest 8-connected warm piece
        seen = np.zeros((h, w), bool); best = []
        for y0, x0 in zip(*np.nonzero(cand)):
            if seen[y0, x0]:
                continue
            comp, stack = [], [(y0, x0)]; seen[y0, x0] = True
            while stack:
                y, x = stack.pop(); comp.append((y, x))
                for dy, dx in nbr8:
                    q, p = y + dy, x + dx
                    if 0 <= q < h and 0 <= p < w and cand[q, p] and not seen[q, p]:
                        seen[q, p] = True; stack.append((q, p))
            if len(comp) > len(best):
                best = comp
        m = np.zeros((h, w), bool)
        for y, x in best:
            m[y, x] = True
        # its outline: dark pixels touching no body pixel (4-way), reached through such dark pixels
        def pure(q, p):
            return K[q, p] and inpoly[q, p] and not any(0 <= q + a < h and 0 <= p + b < w and body[q + a, p + b] for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1)))
        stack = [(y, x) for y, x in best]
        while stack:
            y, x = stack.pop()
            for dy, dx in nbr8:
                q, p = y + dy, x + dx
                if 0 <= q < h and 0 <= p < w and not m[q, p] and pure(q, p):
                    m[q, p] = True; stack.append((q, p))
        out[side] = (m, root)
    return out


def scale2x(a):
    """EPX on an RGBA array (colours compared exactly)."""
    h, w = a.shape[:2]
    P = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    def eq(u, v):
        return np.all(u == v, axis=-1)
    Pc = P[1:-1, 1:-1]; A = P[:-2, 1:-1]; B = P[1:-1, 2:]; C = P[1:-1, :-2]; D = P[2:, 1:-1]
    o = np.zeros((h * 2, w * 2, 4), a.dtype)
    e1 = np.where((eq(C, A) & ~eq(C, D) & ~eq(A, B))[..., None], A, Pc)
    e2 = np.where((eq(A, B) & ~eq(A, C) & ~eq(B, D))[..., None], B, Pc)
    e3 = np.where((eq(D, C) & ~eq(D, B) & ~eq(C, A))[..., None], C, Pc)
    e4 = np.where((eq(B, D) & ~eq(B, A) & ~eq(D, C))[..., None], D, Pc)
    o[0::2, 0::2] = e1; o[0::2, 1::2] = e2; o[1::2, 0::2] = e3; o[1::2, 1::2] = e4
    return o


def rotsprite(sprite, root, deg):
    """sprite: RGBA (clear outside the piece); turn it by deg (screen degrees, + = clockwise) about root (x, y)."""
    big = scale2x(scale2x(scale2x(sprite)))
    h, w = sprite.shape[:2]
    th = np.radians(deg)
    cs, sn = np.cos(th), np.sin(th)
    out = np.zeros_like(sprite)
    rx, ry = root
    ys, xs = np.mgrid[0:h, 0:w]
    # each output pixel's centre, turned back into the source, read in the 8x picture
    dx, dy = xs + 0.5 - rx, ys + 0.5 - ry
    sx = cs * dx + sn * dy + rx
    sy = -sn * dx + cs * dy + ry
    bx, by = np.floor(sx * 8).astype(int), np.floor(sy * 8).astype(int)
    ok = (bx >= 0) & (bx < w * 8) & (by >= 0) & (by < h * 8)
    out[ok] = big[by[ok], bx[ok]]
    return out


def flap(c, tmpl, offset, angles, ref):
    """c: the frame; tmpl from template(ref, ...); offset (dx, dy) of the wings in c against ref; angles {side: deg}."""
    h, w = c.shape[:2]
    new = c.copy()
    ox, oy = offset
    lifted = np.zeros((h, w), bool)
    sprites = {}
    for side, (m, root) in tmpl.items():
        ys, xs = np.nonzero(m)
        ty, tx = ys + oy, xs + ox
        ok = (ty >= 0) & (ty < h) & (tx >= 0) & (tx < w)
        same = np.all(c[ty[ok], tx[ok]] == ref[ys[ok], xs[ok]], axis=1)
        new[ty[ok][same], tx[ok][same]] = 0
        lifted[ty[ok][same], tx[ok][same]] = True
        sp = np.zeros_like(c)
        sp[ty[ok], tx[ok]] = ref[ys[ok], xs[ok]]
        sprites[side] = (sp, (root[0] + ox, root[1] + oy))
    body = new[..., 3] > 0
    for side, (sp, root) in sprites.items():
        r = rotsprite(sp, root, angles.get(side, 0.0))
        put = (r[..., 3] > 0) & ~body
        new[put] = r[put]
    # outline back where a body pixel now borders clear
    a = new[..., 3] > 0
    add = []
    for y in range(h):
        for x in range(w):
            if a[y, x] or not lifted[max(0, y - 1):y + 2, max(0, x - 1):x + 2].any():
                continue
            nb = [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and 0 <= y + dy < h and 0 <= x + dx < w]
            if any(body[q, p] and not dark(c[q, p]) and not warm(new[q, p]) for q, p in nb if abs(q - y) + abs(p - x) == 1):
                add.append((y, x))
    for y, x in add:
        new[y, x] = OUT
    return new
