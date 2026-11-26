"""Xin Zhao's run (8 frames, each drawn apart): its spear made the attack frames' spear too (the user, 2026-11-19: 「对，接着
改跑步」), like the ready stance (redesign.py): the crescent hook above the blade's collar goes (per-frame pixel lists read
off the frames, the collar's outline closed), and the butt loses the silver ring + gold ornament between its gold band
and its silver tip: the tip (the frame's own, found as the last all-silver run along band -> tip) slides back onto the band.

    edit(c, k) -> picture for hd_run[k]
"""
import numpy as np

OUTLINE = (8, 10, 17, 255)
# hook: (box x0, y0, x1, y1 inclusive: all cleared), extra pixels cleared, pixels set to outline
HOOK = {
    0: ((21, 35, 26, 40), [(21, 41), (22, 41), (21, 42)], [(23, 41), (22, 42)]),
    1: ((22, 34, 26, 39), [], [(23, 40), (24, 40)]),
    2: ((21, 33, 25, 38), [], [(22, 39), (23, 39)]),
    3: ((19, 33, 24, 38), [(19, 39), (20, 39)], [(21, 39), (22, 38)]),
    4: ((21, 35, 26, 39), [], [(22, 40), (23, 40)]),
    5: ((22, 34, 26, 39), [], [(24, 39), (23, 40)]),
    6: ((21, 33, 26, 38), [], [(22, 39), (23, 39)]),
    7: ((19, 34, 24, 39), [(19, 40), (20, 40)], [(21, 40), (22, 39)]),
}
# butt: the gold band's centre and the tip (read off the frames)
BUTT = {
    0: ((72.0, 19.5), (79.5, 15.0)),
    1: ((73.0, 18.0), (80.5, 14.5)),
    2: ((73.0, 17.5), (80.0, 13.0)),
    3: ((71.0, 17.5), (79.0, 12.5)),
    4: ((72.0, 18.5), (79.5, 14.0)),
    5: ((74.0, 17.5), (81.0, 13.5)),
    6: ((73.0, 17.5), (80.0, 13.0)),
    7: ((71.5, 18.5), (79.0, 14.5)),
}
SHAFT = {(105, 75, 54), (151, 112, 73), (104, 53, 39), (65, 35, 29), (143, 73, 48), (208, 124, 85)}


def dark(p):
    return int(p[0]) + int(p[1]) + int(p[2]) < 80


def silver(p):
    r, g, b = (int(v) for v in p[:3])
    return b >= r and b >= g and b > 110 and r > 70          # silver and its blue-grey shade (82, 91, 122)


def hook(c, k):
    (x0, y0, x1, y1), extra, line = HOOK[k]
    new = c.copy()
    new[y0:y1 + 1, x0:x1 + 1] = 0
    for x, y in extra:
        new[y, x] = 0
    for x, y in line:
        new[y, x] = OUTLINE
    return new


def butt(c, k, band_end=0.7):
    (bx, by), (tx, ty) = BUTT[k]
    u = np.array([tx - bx, ty - by], float)
    L = np.linalg.norm(u)
    u /= L
    h, w = c.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    px, py = xs - bx, ys - by
    t = px * u[0] + py * u[1]
    lat = np.abs(-px * u[1] + py * u[0])
    op = c[..., 3] > 0
    lane = op & (lat <= 3.5) & (t > band_end) & (t <= L + 4)
    # the tip: from the far end inward, the longest run whose core pixels are all silver or outline
    core = op & (lat <= 1.5) & (t > band_end)
    t0 = L + 4
    for cand in np.arange(L + 3, band_end, -0.5):
        sel = core & (t >= cand)
        if all(silver(c[y, x]) or dark(c[y, x]) for y, x in zip(*np.nonzero(sel))):
            t0 = cand
        else:
            break
    spike = lane & (t >= t0 - 0.5)
    want = t0 - 0.5 - band_end
    best = None
    for dx in range(-8, 2):
        for dy in range(-2, 8):
            v = np.array([dx, dy], float)
            along, side = -(v @ u), abs(-v[0] * u[1] + v[1] * u[0])
            score = abs(along - want) + 0.7 * side
            if best is None or score < best[0]:
                best = (score, (dx, dy))
    s = best[1]
    new = c.copy()
    new[lane] = 0
    for y, x in zip(*np.nonzero(spike)):
        qy, qx = y + s[1], x + s[0]
        if 0 <= qy < h and 0 <= qx < w:
            q = new[qy, qx]
            if q[3] == 0 or dark(q) or tuple(int(v) for v in q[:3]) in SHAFT:
                new[qy, qx] = c[y, x]
    return new, dict(t0=round(float(t0), 1), want=round(float(want), 1), shift=s, spike_px=int(spike.sum()), cleared=int(lane.sum()))


def edit(c, k):
    new, info = butt(hook(c, k), k)
    return new, info
