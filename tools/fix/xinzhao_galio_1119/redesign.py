"""Xin Zhao's ready-stance spear made the attack frames' spear (the user, 2026-11-19: 「待机时候枪末尾是这样的 攻击时就不是这个
模型了」): the butt loses the silver ring + gold ornament between its gold band and its silver tip (the attack butt is band
+ tip, hd_dead[7] / hd_q3[3]), band + tip then slide in along the shaft (the length of the attack frames' spear); the
blade loses the crescent hook the attack blades do not have. Every pixel kept is the frame's own, moved whole.

    butt(c, oy=0)  -> picture       hook(c, oy=0) -> picture       (oy: the frame's spear 1 px higher = -1)
"""
import numpy as np

U = np.array([2.0, -1.0]) / np.sqrt(5.0)          # the butt's shaft runs 2 right : 1 up
N = np.array([1.0, 2.0]) / np.sqrt(5.0)           # square to it
O = np.array([56.0, 17.0])                         # where the shaft leaves the head (ready stance, hd)


def is_moveable(p):
    return p[3] == 0 or int(p[0]) + int(p[1]) + int(p[2]) < 80 or tuple(int(v) for v in p[:3]) in {
        (105, 75, 54), (151, 112, 73), (104, 53, 39), (65, 35, 29), (143, 73, 48)}


def tcoords(c, oy):
    h, w = c.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs - O[0], ys - (O[1] + oy)
    return px * U[0] + py * U[1], np.abs(px * N[0] + py * N[1])


def butt(c, oy=0, band_shift=(-6, 3)):
    """Band A (t 9.5-13) stays the band, the spike (t > 19) comes right after it; then both slide by band_shift."""
    t, d = tcoords(c, oy)
    lane = (d <= 6) & (c[..., 3] > 0)
    band = lane & (t > 9.5) & (t <= 13.0)
    spike = lane & (t > 20.0)
    new = c.copy()
    new[lane & (t > 9.5)] = 0                       # band A, silver ring, gold ornament, spike: all lifted
    h, w = c.shape[:2]
    for m, s in ((band, band_shift), (spike, (band_shift[0] - 6, band_shift[1] + 3))):
        ys, xs = np.nonzero(m)
        for y, x in zip(ys, xs):
            qy, qx = y + s[1], x + s[0]
            if 0 <= qy < h and 0 <= qx < w and (new[qy, qx][3] == 0 or is_moveable(new[qy, qx])):
                new[qy, qx] = c[y, x]
    return new


def hook(c, oy=0, outline=(8, 10, 17)):
    """The crescent above the blade's collar goes (ready stance: rows 29-35, x 9-24, and its root at (17-19, 36),
    (17-18, 37)); the collar's top-left gets its outline back at (20, 36) and (19, 37). The hand's outline (25, 35) stays."""
    new = c.copy()
    for y in range(29, 36):
        for x in range(9, 25):
            new[y + oy, x] = 0
    for x, y in ((17, 36), (18, 36), (19, 36), (17, 37), (18, 37)):
        new[y + oy, x] = 0
    for x, y in ((20, 36), (19, 37)):
        new[y + oy, x] = (*outline, 255)
    return new
