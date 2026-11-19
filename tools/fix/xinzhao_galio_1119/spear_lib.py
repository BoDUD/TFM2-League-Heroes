"""spear.py's measurement as a module: measure(cell) / ends(cell)."""
import numpy as np

SHAFT = {(105, 75, 54), (151, 112, 73), (104, 53, 39)}
SILVER = {(139, 151, 180), (165, 175, 200), (195, 206, 225), (100, 107, 139), (249, 249, 250)}


def measure(c):
    rgb = c[:, :, :3]
    alpha = c[:, :, 3] > 0
    key = rgb[:, :, 0] * 65536 + rgb[:, :, 1] * 256 + rgb[:, :, 2]
    shaft = np.isin(key, [r * 65536 + g * 256 + b for r, g, b in SHAFT]) & alpha
    silver = np.isin(key, [r * 65536 + g * 256 + b for r, g, b in SILVER]) & alpha
    ys, xs = np.nonzero(shaft)
    if len(xs) < 6:
        return None
    pts = np.stack([xs, ys], 1).astype(float)
    m = pts.mean(0)
    best = (-1, 0.0, 0.0)
    for th in np.arange(0, 180, 0.5):
        r = np.radians(th)
        nrm = np.array([-np.sin(r), np.cos(r)])
        rho = (pts - m) @ nrm
        hist, edges = np.histogram(rho, bins=np.arange(rho.min() - 2, rho.max() + 3, 1.0))
        win = np.convolve(hist, np.ones(3, int), "same")
        i = int(win.argmax())
        if win[i] > best[0]:
            best = (int(win[i]), th, (edges[i] + edges[i + 1]) / 2)
    support, th, rho0 = best
    r = np.radians(th)
    u = np.array([np.cos(r), np.sin(r)])
    nrm = np.array([-np.sin(r), np.cos(r)])
    m = m + nrm * rho0
    on = np.abs((pts - m) @ nrm) <= 1.5
    pts = pts[on]
    lin = float(support)
    oy, ox = np.nonzero(alpha)
    op = np.stack([ox, oy], 1).astype(float) - m
    t = op @ u
    d = np.abs(op @ np.array([-u[1], u[0]]))
    band = d <= 2.0
    ts = np.round(t[band]).astype(int)
    occupied = set(ts.tolist())
    st = np.round((pts - m) @ u).astype(int)
    lo, hi = st.min(), st.max()
    # walk out from the shaft until 3 empty steps in a row
    def walk(start, step):
        x, gap, last = start, 0, start
        while gap < 3:
            x += step
            if x in occupied:
                last, gap = x, 0
            else:
                gap += 1
        return last
    a, b = walk(lo, -1), walk(hi, 1)
    length = b - a + 1
    # blade: silver pixels in the band within 30 px of either end; the end with more silver is the blade end
    sv = np.stack(np.nonzero(silver)[::-1], 1).astype(float) - m
    svt, svd = sv @ u, np.abs(sv @ np.array([-u[1], u[0]]))
    near = svd <= 4.0
    blade = 0
    for end, sgn in ((a, 1), (b, -1)):
        sel = near & ((svt - end) * sgn >= -1) & ((svt - end) * sgn <= 30)
        if sel.sum() > 0:
            ext = svt[sel]
            blade = max(blade, int(round(ext.max() - ext.min() + 1)))
    ang = th
    measure.last = (m + u * a, m + u * b, length)
    return length, blade, ang, lin, len(xs)


def ends(c):
    r = measure(c)
    if r is None:
        return None
    pa, pb, L = measure.last
    return (int(round(pa[0])), int(round(pa[1]))), (int(round(pb[0])), int(round(pb[1]))), L

