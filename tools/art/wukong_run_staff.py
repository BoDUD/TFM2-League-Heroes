#!/usr/bin/env python3
"""league_wukong's run: the staff made one straight piece (2026-10-22, the user: 「猴子跑步的时候感觉武器看起来是歪的」,
then on its back end: 「这里金箍棒都断了吧」).

Codex's nine run frames (assets/source/wukong/hd/act/run_*.png, tools/art/rig_frames_1018.py) draw the staff in three
pieces that do not line up: the front piece from the near fist up past his face (about 1:2), a middle piece in the far
hand behind him and the back piece from there down to its cap at hip height (about 2:5) - its end 5-6 rows above the
front piece's line, so the staff read as broken at his back. Each frame now keeps the front piece as drawn (the fist
holds it) and replaces the back one by the front piece itself turned a half turn about the staff's middle on the front
piece's own axis (the 金箍棒's two capped ends are alike; a half turn about a point on whole half-squares resamples
nothing), drawn behind him only where nothing else is. The old back piece and the far hand that held it are cleared
(the hand would hold nothing now: the far arm stays behind his body), with the loose squares they leave, and Codex's
green key specks on his body go too (his eye is the same green: only below EYE_ROWS).

    import wukong_run_staff as W;  pal = W.staff_palette(frames);  frame = W.straighten(frame, pal)
"""
import numpy as np
from scipy import ndimage

FRONT_W = 4.5          # the front piece: squares within this of its axis past the grip
BACK_W = 4.0           # the old back piece: squares within this of its axis
BACK_CORE = 12         # columns up to here hold only the back piece (its cap and bands, the background round them)
BACK_REACH = 30        # the old back piece followed at most this far right (its steel into the far hand)
EYE_ROWS = 22          # green squares from this row down are Codex's key specks, not his eye


def _caps(f):
    """The staff's red caps -> (back cap, front cap): (mean x, mean y, min x, max x) each."""
    a = f.astype(int)
    red = (a[..., 3] > 0) & (a[..., 0] > 180) & (a[..., 1] < 40) & (a[..., 2] < 40)
    lab, n = ndimage.label(red, np.ones((3, 3), bool))
    caps = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) >= 4:
            caps.append((xs.mean(), ys.mean(), xs.min(), xs.max()))
    return min(caps), max(caps, key=lambda c: c[0] - c[1])


def _steel(f):
    a = f.astype(int)
    return ((a[..., 3] > 0) & (np.abs(a[..., 0] - a[..., 1]) < 25) & (np.abs(a[..., 1] - a[..., 2]) < 35) &
            (a[..., 0] > 60) & (a[..., 0] < 140))


def grip(f):
    """Where the front piece's steel leaves the near fist: (x, y) of its leftmost steel squares right of column 53."""
    ys, xs = np.nonzero(_steel(f))
    pts = sorted((x, y) for x, y in zip(xs, ys) if x >= 53 and y <= 26)
    near = [p for p in pts if p[0] <= pts[0][0] + 1]
    return float(np.mean([p[0] for p in near])), float(np.mean([p[1] for p in near]))


def _capsule(shape, p0, p1, w):
    H, W = shape
    ys, xs = np.mgrid[0:H, 0:W]
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    t = np.clip(((xs + 0.5 - x0) * dx + (ys + 0.5 - y0) * dy) / (dx * dx + dy * dy), 0, 1)
    return np.hypot(xs + 0.5 - (x0 + t * dx), ys + 0.5 - (y0 + t * dy)) <= w


def _biggest(m):
    lab, n = ndimage.label(m, np.ones((3, 3), bool))
    if n < 2:
        return m
    return lab == 1 + int(np.argmax(ndimage.sum(m, lab, range(1, n + 1))))


def staff_palette(frames):
    """The staff's own colours: every square of each frame's front piece region (past its grip, above its row)."""
    out = set()
    for f in frames:
        gx, gy = grip(f)
        sub = f[:int(gy) + 3, int(gx) + 2:]
        out |= {tuple(int(v) for v in c) for c in sub[sub[..., 3] > 0][:, :3]}
    return out


def straighten(f, pal):
    """One run frame with its staff made one straight piece (see the module's note). -> new RGBA array."""
    H, W = f.shape[:2]
    op = f[..., 3] > 0
    xs = np.arange(W)[None, :]
    back_cap, front_cap = _caps(f)
    gx, gy = grip(f)
    # the front piece and its axis (y = a + b x)
    tip = (front_cap[3] + 1.0, front_cap[1] - (front_cap[3] + 1.0 - front_cap[0]) * 0.5)
    front = _biggest(op & _capsule((H, W), (gx, gy), tip, FRONT_W) & (xs >= int(round(gx)) + 1))
    fy, fx = np.nonzero(front)
    b, a = np.polyfit(fx + 0.5, fy + 0.5, 1)
    # the old back piece: its axis fit on the staff's colours in its cap and bands, followed to its last steel square
    own = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(op & (xs <= BACK_REACH))):
        own[y, x] = tuple(int(v) for v in f[y, x, :3]) in pal
    core = _biggest(own & (xs <= BACK_CORE) &
                    _capsule((H, W), back_cap[:2], (BACK_CORE, back_cap[1] - 4.5), BACK_W))
    cy, cx = np.nonzero(core)
    bb, ba = np.polyfit(cx + 0.5, cy + 0.5, 1)
    sy, sx = np.nonzero(_steel(f))
    on = (np.abs(sy + 0.5 - (ba + bb * (sx + 0.5))) <= 2.5) & (sx <= BACK_REACH)
    x_end = int(sx[on].max()) + 1 if on.any() else BACK_CORE
    x0 = back_cap[2] - 1.0
    band = _capsule((H, W), (x0, ba + bb * x0), (x_end + 0.5, ba + bb * (x_end + 0.5)), BACK_W)
    dark = f[..., :3].astype(int).sum(-1) < 90
    back = _biggest(op & band & (xs <= x_end) & ((xs <= BACK_CORE) | own | dark))
    out = f.copy()
    out[back] = 0
    # the loose squares it leaves (its outline past the band): small pieces cut off from him
    lab, n = ndimage.label(out[..., 3] > 0, np.ones((3, 3), bool))
    if n > 1:
        sizes = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
        main = 1 + int(np.argmax(sizes))
        for i in range(1, n + 1):
            if i != main and sizes[i - 1] < 12:
                out[lab == i] = 0
    # the front piece turned a half turn about the staff's middle on its axis, behind him
    mx = (x0 + fx.max() + 1.0) / 2.0
    c2x, c2y = int(round(2 * mx)), int(round(2 * (a + b * mx)))
    ty, tx = c2y - 1 - fy, c2x - 1 - fx
    ok = (tx >= 0) & (tx < W) & (ty >= 0) & (ty < H)
    ty, tx, sy, sx = ty[ok], tx[ok], fy[ok], fx[ok]
    free = out[ty, tx, 3] == 0
    out[ty[free], tx[free]] = f[sy[free], sx[free]]
    # Codex's green key specks below his eye -> their neighbours' commonest colour
    g = out.astype(int)
    green = (g[..., 3] > 0) & (g[..., 1] > g[..., 0] + 80) & (g[..., 1] > g[..., 2] + 60)
    green[:EYE_ROWS] = False
    fixed = out.copy()
    for y, x in zip(*np.nonzero(green)):
        nb = [tuple(int(v) for v in out[yy, xx]) for yy in range(y - 1, y + 2) for xx in range(x - 1, x + 2)
              if (yy, xx) != (y, x) and 0 <= yy < H and 0 <= xx < W and out[yy, xx, 3] > 0 and not green[yy, xx]]
        if nb:
            vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True)
            fixed[y, x] = vals[cnt.argmax()]
    return fixed
