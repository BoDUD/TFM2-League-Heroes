#!/usr/bin/env python3
"""league_wukong's run: the staff one straight rod in both hands (2026-10-22, the user: 「猴子跑步的时候感觉武器看起来是歪
的」 and 「这里金箍棒都断了吧」; then on the first fix - #446 kept the front piece, laid its half turn behind him for the back
end and cleared the far hand that no longer held it: 「猴子手呢 断了？？」「这质量你能说改好了？」).

Codex's nine run frames (assets/source/wukong/hd/act/run_*.png, tools/art/rig_frames_1018.py) hold the staff in both
hands - the near fist before his face, the far hand behind his shoulder - but draw it in three pieces that do not line
up: the front piece out of the near fist at about 1:2, the back piece through the far hand at about 2:5, and between
the hands (behind him) a line of about 1:4. Each frame now
  - keeps both hands and everything else as drawn, and clears the old front piece (past the near grip), the old back
    piece (its cap, bands and steel left of the far hand; its steel between the hand and his body, with the outline
    squares that border only staff or air) and the loose squares they leave;
  - gets one straight rod through both grips - the near grip where the front piece's steel left the fist, the far grip
    in the middle of the gap the far hand leaves in the back piece's steel - its slope at first smoothed (1-2-1
    with the neighbouring frames until the user's 「还是有点歪啊」: it tilted 6 degrees over the cycle) - now one slope for
    the whole cycle (the mean of the frames'), the rod through the middle of the two grips, within a square and a half
    of each (the fists are five squares tall) - drawn behind everything (the fists hold it): each end ROD_END squares
    past its grip (as far as Codex's front piece reached), a red cap, four gold bands and the steel between, in Codex's
    own colours, outlined, lit from above;
  - is padded PAD columns on each side (the flatter rod reaches past Codex's frame);
  - loses Codex's green key specks on his body (his eye is the same green: only from EYE_ROWS down).

    import wukong_run_staff as W;  frames = W.straighten_all(frames)    # all nine together (the slope is smoothed)
"""
import math

import numpy as np
from scipy import ndimage

PAD = 10               # columns added on each side
ROD_END = 19.0         # each end of the rod past its grip
CAP_LEN, BANDS_END = 5.5, 13.5     # from a tip: the red cap, then four gold bands two squares each, then the steel
CORE_W, SHAFT_W, EDGE = 1.8, 1.1, 0.9   # half widths: the cap and bands, the steel; the outline round them
OUTLINE = (7, 16, 3)
CAP = [(241, 11, 3), (241, 2, 1), (194, 6, 4)]              # Codex's colours: lit, base, shaded
GOLD = [(254, 218, 21), (248, 213, 19), (230, 134, 17)]
AMBER = [(230, 134, 17), (206, 108, 10), (170, 78, 10)]
STEEL = [(114, 101, 82), (114, 101, 82), (81, 44, 31)]
FRONT_W = 4.5          # the old front piece: squares within this of its axis past the grip
BACK_W = 4.0           # the old back piece: squares within this of its axis
BACK_CORE = 12         # columns up to here hold only the old back piece (its cap and bands, the air round them)
BACK_REACH = 30        # the old back piece followed at most this far right (its steel into the far hand and on)
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
    return float(np.mean([p[0] for p in near])) + 0.5, float(np.mean([p[1] for p in near])) + 0.5


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


def _axis(mask):
    """A piece's axis y = a + b x (least squares over its squares' middles) -> (a, b)."""
    ys, xs = np.nonzero(mask)
    b, a = np.polyfit(xs + 0.5, ys + 0.5, 1)
    return a, b


def staff_palette(frames):
    """The staff's own colours: every square of each frame's front piece region (past its grip, above its row)."""
    out = set()
    for f in frames:
        gx, gy = grip(f)
        sub = f[:int(gy) + 3, int(gx) + 2:]
        out |= {tuple(int(v) for v in c) for c in sub[sub[..., 3] > 0][:, :3]}
    return out


def _clear(f, pal):
    """f without its old staff pieces -> (that frame, near grip, far grip)."""
    H, W = f.shape[:2]
    op = f[..., 3] > 0
    xs = np.arange(W)[None, :]
    back_cap, front_cap = _caps(f)
    gx, gy = grip(f)
    tip = (front_cap[3] + 1.0, front_cap[1] - (front_cap[3] + 1.0 - front_cap[0]) * 0.5)
    front = _biggest(op & _capsule((H, W), (gx, gy), tip, FRONT_W) & (xs >= int(gx) + 1))
    # the old back piece's axis, fit on the staff's own colours in its cap and bands
    own = np.zeros((H, W), bool)
    for y, x in zip(*np.nonzero(op & (xs <= BACK_REACH))):
        own[y, x] = tuple(int(v) for v in f[y, x, :3]) in pal
    ba, bb = _axis(_biggest(own & (xs <= BACK_CORE) &
                            _capsule((H, W), back_cap[:2], (BACK_CORE, back_cap[1] - 4.5), BACK_W)))
    # the far grip: the middle of the widest gap the far hand leaves in that piece's steel
    st = _steel(f)
    sy, sx = np.nonzero(st)
    on = (np.abs(sy + 0.5 - (ba + bb * (sx + 0.5))) <= 3.0) & (sx >= 8) & (sx <= BACK_REACH)
    pts = sorted(zip(sx[on], sy[on]))
    gap = max(((p, q) for p, q in zip(pts, pts[1:]) if q[0] - p[0] >= 3), key=lambda pq: pq[1][0] - pq[0][0],
              default=None)
    if gap:
        (x0, y0), (x1, y1) = gap
        far = ((x0 + x1) / 2 + 0.5, (y0 + y1) / 2 + 0.5)
        left_x = x0
    else:
        x0 = pts[-1][0]
        far = (x0 + 3.5, ba + bb * (x0 + 3.5))
        left_x = x0
    xb = back_cap[2] - 1.0
    band = _capsule((H, W), (xb, ba + bb * xb), (BACK_REACH + 1, ba + bb * (BACK_REACH + 1)), BACK_W)
    back_left = _biggest(op & band & (xs <= left_x))
    steel_r = st & band & (xs > left_x) & (xs <= BACK_REACH)
    dark = f[..., :3].astype(int).sum(-1) < 90
    body = op & ~back_left & ~steel_r & ~dark & ~front
    ring = (dark & band & (xs > left_x) & (xs <= BACK_REACH) & ndimage.binary_dilation(steel_r, np.ones((3, 3), bool))
            & ~ndimage.binary_dilation(body, np.ones((3, 3), bool)))
    out = f.copy()
    out[back_left | steel_r | ring | front] = 0
    lab, n = ndimage.label(out[..., 3] > 0, np.ones((3, 3), bool))
    if n > 1:
        sizes = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
        main = 1 + int(np.argmax(sizes))
        for i in range(1, n + 1):
            if i != main and sizes[i - 1] < 12:
                out[lab == i] = 0
    return out, (gx, gy), far


def _rod_colour(t, u):
    """t: squares from the nearer tip; u: across the rod (+ = down). -> colour or None."""
    if t < -0.5:
        return None
    steel = t >= BANDS_END
    half = SHAFT_W if steel else CORE_W
    if abs(u) > half + EDGE:
        return None
    if abs(u) > half or t < 0.5:
        return OUTLINE
    fam = CAP if t < CAP_LEN else (STEEL if steel else (GOLD if int((t - CAP_LEN) // 2) % 2 == 0 else AMBER))
    return fam[0] if u < -0.5 else (fam[2] if u > 0.5 else fam[1])


def _rod(base, near, far, slope):
    """The rod at `slope` through the middle of the grips, from ROD_END past the far grip to ROD_END past the near
    one, under base."""
    H, W = base.shape[:2]
    mx, my = (near[0] + far[0]) / 2, (near[1] + far[1]) / 2
    gx, gy = near[0], my + slope * (near[0] - mx)
    n = math.hypot(1.0, slope)
    ex, ey = 1.0 / n, slope / n
    nx, ny = -ey, ex
    hx = far[0]
    hy = gy + slope * (hx - gx)
    back = (hx - ex * ROD_END, hy - ey * ROD_END)
    total = (gx - hx) * ex + (gy - hy) * ey + 2 * ROD_END
    out = base.copy()
    for yy in range(H):
        for xx in range(W):
            if out[yy, xx, 3]:
                continue
            px, py = xx + 0.5, yy + 0.5
            along = (px - back[0]) * ex + (py - back[1]) * ey
            if along < -0.5 or along > total + 0.5:
                continue
            c = _rod_colour(min(along, total - along), (px - gx) * nx + (py - gy) * ny)
            if c is not None:
                out[yy, xx, :3] = c
                out[yy, xx, 3] = 255
    return out


def _green_out(f):
    """Codex's green key specks from EYE_ROWS down -> their neighbours' commonest colour."""
    H, W = f.shape[:2]
    g = f.astype(int)
    green = (g[..., 3] > 0) & (g[..., 1] > g[..., 0] + 80) & (g[..., 1] > g[..., 2] + 60)
    green[:EYE_ROWS] = False
    out = f.copy()
    for y, x in zip(*np.nonzero(green)):
        nb = [tuple(int(v) for v in f[y2, x2]) for y2 in range(y - 1, y + 2) for x2 in range(x - 1, x + 2)
              if (y2, x2) != (y, x) and 0 <= y2 < H and 0 <= x2 < W and f[y2, x2, 3] > 0 and not green[y2, x2]]
        if nb:
            vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True)
            out[y, x] = vals[cnt.argmax()]
    return out


def straighten_all(frames):
    """The run's frames (in cycle order) with the staff one straight rod in both hands, each padded PAD columns on
    either side -> new RGBA arrays."""
    pal = staff_palette(frames)
    cleared = [_clear(_green_out(f), pal) for f in frames]
    raw = [(near[1] - far[1]) / (near[0] - far[0]) for _, near, far in cleared]
    slopes = [float(np.mean(raw))] * len(raw)        # one slope for the cycle: the rod never tilts as he runs
    out = []
    for (base, near, far), s in zip(cleared, slopes):
        H, W = base.shape[:2]
        padded = np.zeros((H, W + 2 * PAD, 4), np.uint8)
        padded[:, PAD:PAD + W] = base
        out.append(_rod(padded, (near[0] + PAD, near[1]), (far[0] + PAD, far[1]), s))
    return out
