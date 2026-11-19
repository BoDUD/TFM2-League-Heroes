"""Shorten Xin Zhao's spear in one frame without touching anything else: each end piece (blade + collar, or butt +
ornament) slides inward along the shaft by an integer step the shaft's own pixel pattern repeats with, so the joint
shows no seam; the pixels it leaves at the tip go clear. The moved piece is drawn over the shaft and clear pixels only
(never over the hand, the head or the armour: those stay in front).

    slide(c, tip, cut, want, band=7) -> (new picture, shift, seam mismatches)
      tip: the end's outermost point; cut: a point on the free shaft just inside the end piece (the piece = every opaque
      pixel beyond the cut, toward the tip, within `band` px of the axis); want: how many px to shorten.
"""
import numpy as np

# colours of the free shaft and its outline (dark browns, black)
SHAFT = {(105, 75, 54), (151, 112, 73), (104, 53, 39), (65, 35, 29), (143, 73, 48)}


def is_dark(p):
    return int(p[0]) + int(p[1]) + int(p[2]) < 80


def spearish(p):
    """A pixel the moved piece may cover: clear, outline, shaft brown."""
    return p[3] == 0 or is_dark(p) or tuple(int(v) for v in p[:3]) in SHAFT


def piece_mask(c, tip, cut, band):
    h, w = c.shape[:2]
    u = np.array(tip, float) - np.array(cut, float)
    L = np.linalg.norm(u)
    u /= L
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs - cut[0], ys - cut[1]
    t = px * u[0] + py * u[1]
    d = np.abs(-px * u[1] + py * u[0])
    return (c[..., 3] > 0) & (t > 0.5) & (t <= L + 3) & (d <= band), u, L


def apply(c, mask, s):
    h, w = c.shape[:2]
    new = c.copy()
    new[mask] = 0
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        qy, qx = y + s[1], x + s[0]
        if 0 <= qy < h and 0 <= qx < w and (mask[qy, qx] or spearish(c[qy, qx])):
            new[qy, qx] = c[y, x]
    return new


def seam(c, mask, s, cut, u, band):
    """Mismatches where the moved piece meets the shaft left in place: c[p] vs c[p - s] over the 6 px of shaft around
    the new joint (cut + s), within the band."""
    h, w = c.shape[:2]
    j = np.array(cut, float) + np.array(s, float)
    bad = n = 0
    for y in range(h):
        for x in range(w):
            px, py = x - j[0], y - j[1]
            t = px * u[0] + py * u[1]
            d = abs(-px * u[1] + py * u[0])
            if -3 <= t <= 3 and d <= band:
                sy, sx = y - s[1], x - s[0]
                a = c[y, x]
                b = c[sy, sx] if 0 <= sy < h and 0 <= sx < w else np.zeros(4, c.dtype)
                if a[3] == 0 and b[3] == 0:
                    continue
                n += 1
                bad += int(not np.array_equal(a, b))
    return bad, n


def slide(c, tip, cut, want, band=7, spread=2.5, pick=None):
    mask, u, L = piece_mask(c, tip, cut, band)
    best = None
    for dx in range(-30, 31):
        for dy in range(-30, 31):
            v = np.array([dx, dy], float)
            n = np.linalg.norm(v)
            if n == 0 or abs(n - want) > spread:
                continue
            if np.dot(v / n, -u) < np.cos(np.radians(12)):
                continue
            bad, tot = seam(c, mask, (dx, dy), cut, u, band)
            key = (bad / max(tot, 1), abs(n - want))
            if best is None or key < best[0]:
                best = (key, (dx, dy), bad, tot)
    s = pick or best[1]
    bad, tot = seam(c, mask, s, cut, u, band)
    return apply(c, mask, s), s, (bad, tot), int(mask.sum())
