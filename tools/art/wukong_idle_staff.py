#!/usr/bin/env python3
"""league_wukong's staff held slanting across him (his idle and the poses drawn like it): one straight rod (2026-10-29, the
user on the pick card: 「怎么感觉猴子后面的金箍棒又做歪了？」 -> 「拉直，先给我看」).

Codex's frames (assets/source/wukong/hd/act, tools/art/rig_frames_1018.py) draw the staff in two pieces his body splits:
the front piece in his near fist down to the lower-left cap, and the back piece behind his head up to the upper-right
cap. The two run nearly parallel (about 1:1.2) but the back piece sits some five squares lower than the front piece's
line would carry it, so the staff looks bent behind him. Each frame now
  - keeps the front piece, his fist and everything else as drawn;
  - clears the old back piece: from its cap down along its own axis until the squares across it are no longer the
    staff's own colours (his hair, his shoulder), the staff's squares and the outline squares that border only staff
    or air within BACK_W of that axis, and the loose specks they leave;
  - draws the back piece again on the front piece's own axis (least squares over its squares), behind everything (only
    into clear squares), its tip as far from the front tip as Codex's back tip was (the staff keeps its length): a red
    cap, four gold bands and the steel, in Codex's colours and widths (tools/art/wukong_run_staff.py's rod).
The run has its own (wukong_run_staff.py: two hands, one slope for the cycle).

    import wukong_idle_staff as WI;  f = WI.straighten(f)
    python tools/art/wukong_idle_staff.py --preview DIR [names]   # before / after at 10x and 4x, nothing written
"""
import argparse
import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

import wukong_run_staff as WS


HERE = os.path.dirname(os.path.abspath(__file__))
ACT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "source", "wukong", "hd", "act")
BACK_W = 3.0           # the old back piece: squares within this of its axis
BACK_FIT = 8.0         # its axis fitted on the first squares this far from its cap
TOP = 10               # clear rows added on top (the back tip on the straight line may reach higher)
CAP_END = 1.5          # a tip this far past its cap's middle
# Codex's staff colours (the steel's highlight is his skin's colour and its edge a dark green in some frames)
STAFF = {c for fam in (WS.CAP, WS.GOLD, WS.AMBER, WS.STEEL) for c in fam} | {(252, 174, 88), (30, 47, 24)}
FILL_NEAR = 5          # a cleared square with this many of its 8 neighbours his (not air, not outline) is his again
RIGHT = 6              # clear columns added on the right (the back tip on the straight line may reach further)
NAMES = [f"idle_{i}" for i in range(7)]


def _red(f):
    a = f.astype(int)
    return (a[..., 3] > 0) & (a[..., 0] > 180) & (a[..., 1] < 60) & (a[..., 2] < 40)


def caps(f):
    """The two red caps: (front = the leftmost, back = the most up-right) as (x, y) of their middles."""
    lab, n = ndimage.label(_red(f), np.ones((3, 3), bool))
    cs = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) >= 4:
            cs.append((xs.mean() + 0.5, ys.mean() + 0.5))
    front = min(cs)
    back = max(cs, key=lambda c: c[0] - c[1])
    return front, back


def _near(shape, p, d, w, t0, t1):
    """Squares within w of the ray p + t d (t0..t1, d a unit vector)."""
    H, W = shape
    ys, xs = np.mgrid[0:H, 0:W]
    vx, vy = xs + 0.5 - p[0], ys + 0.5 - p[1]
    t = vx * d[0] + vy * d[1]
    off = np.abs(-vx * d[1] + vy * d[0])
    return (t >= t0) & (t <= t1) & (off <= w), t


def _fit(mask):
    """A piece's axis through its squares' middles -> (a point on it, a unit vector), by total least squares."""
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs + 0.5, ys + 0.5], 1)
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c)
    d = vt[0]
    return c, d / np.hypot(*d)


def _unit(p, q):
    d = np.array([q[0] - p[0], q[1] - p[1]], float)
    return d / np.hypot(*d)


def _piece(f, op, dark, cap, toward):
    """The staff's piece from `cap` toward `toward` (a point the staff runs at): its own colours from its first BACK_FIT
    squares, followed along its axis until the squares across it are none of those (his hair, his fist, his shoulder)
    -> (its squares with the outline squares that border only staff or air, where it stops)."""
    H, W = f.shape[:2]
    m, _ = _near((H, W), cap, _unit(cap, toward), BACK_W, -2.0, BACK_FIT)
    c, d = _fit(op & ~dark & m)
    if d @ _unit(cap, toward) < 0:
        d = -d
    # its own colours near the cap and every colour of Codex's staff (its steel is past the first squares)
    own = {tuple(int(v) for v in x) for x in f[op & ~dark & m][:, :3]} | STAFF
    stop = BACK_FIT
    for t in np.arange(BACK_FIT, 40.0, 0.5):
        x, y = cap[0] + d[0] * t, cap[1] + d[1] * t
        mids = [(int(math.floor(y + s_ * d[0])), int(math.floor(x - s_ * d[1]))) for s_ in (-1.0, 0.0, 1.0)]
        mids = [(yy, xx) for yy, xx in mids if 0 <= yy < H and 0 <= xx < W]
        if sum(1 for yy, xx in mids if op[yy, xx] and not dark[yy, xx]
               and tuple(int(v) for v in f[yy, xx, :3]) not in own) >= 2:
            stop = t
            break
    band, _ = _near((H, W), cap, d, BACK_W, -2.5, stop)
    colours = np.array([tuple(int(v) for v in x) in own for x in f.reshape(-1, 4)[:, :3]]).reshape(H, W)
    staff = op & band & colours & ~dark
    body = op & ~staff & ~dark
    ring = op & dark & band & ~ndimage.binary_dilation(body, np.ones((3, 3), bool))
    return staff | ring, (cap[0] + d[0] * stop, cap[1] + d[1] * stop)


def _cleared(f):
    """f padded TOP rows on top and RIGHT columns on the right (the soles and the hip column stay where they were),
    without the two old pieces -> (frame, grip, front cap, back cap)."""
    f = pad(f)
    op = f[..., 3] > 0
    dark = f[..., :3].astype(int).sum(-1) < 90
    front, back = caps(f)
    fp, grip = _piece(f, op, dark, front, back)
    bp, _ = _piece(f, op, dark, back, front)
    out = f.copy()
    out[fp | bp] = 0
    # the old outline left standing alone where a piece crossed his outline (dark squares with nothing but dark or air
    # round them, near where the pieces were)
    near = ndimage.binary_dilation(fp | bp, np.ones((3, 3), bool), iterations=2)
    for _ in range(4):
        o = out[..., 3] > 0
        lit = o & (out[..., :3].astype(int).sum(-1) >= 90)
        alone = o & ~lit & near & ~ndimage.binary_dilation(lit, np.ones((3, 3), bool))
        # and spurs: an outline square sticking out (one neighbour or none across its sides)
        sides = ndimage.convolve(o.astype(int), np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]]), mode="constant")
        alone |= o & ~lit & near & (sides <= 1)
        if not alone.any():
            break
        out[alone] = 0
    # his hair (or shoulder) where the old staff lay over its edge: a cleared square mostly surrounded by him takes
    # the commonest colour round it, a few passes from the inside out (the outline is closed again by the rig)
    gone = fp | bp
    for _ in range(4):
        o = out[..., 3] > 0
        lit = o & (out[..., :3].astype(int).sum(-1) >= 90)
        k = ndimage.convolve(lit.astype(int), np.ones((3, 3), int), mode="constant") - lit
        todo = gone & ~o & (k >= FILL_NEAR)
        if not todo.any():
            break
        H, W = out.shape[:2]
        for y, x in zip(*np.nonzero(todo)):
            nb = [tuple(int(v) for v in out[y2, x2]) for y2 in range(y - 1, y + 2) for x2 in range(x - 1, x + 2)
                  if (y2, x2) != (y, x) and 0 <= y2 < H and 0 <= x2 < W and lit[y2, x2]]
            vals, cnt = np.unique(np.array(nb), axis=0, return_counts=True)
            out[y, x] = vals[cnt.argmax()]
    lab, n = ndimage.label(out[..., 3] > 0, np.ones((3, 3), bool))
    if n > 1:
        sizes = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
        main = 1 + int(np.argmax(sizes))
        for i in range(1, n + 1):
            if i != main and sizes[i - 1] < 12:
                out[lab == i] = 0
    # his outline where the old pieces lay against him: Codex's hair (or shoulder) squares that touched the staff's
    # outline touch air now - one outline square beside each, as everywhere else round him (ppu_rig.tidy closes broken
    # outlines but does not lay a new one)
    o = out[..., 3] > 0
    lit = o & (out[..., :3].astype(int).sum(-1) >= 90)
    bare = ~o & ndimage.binary_dilation(gone, np.ones((3, 3), bool)) &         ndimage.binary_dilation(lit, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
    out[bare, :3] = OUTLINE
    out[bare, 3] = 255
    return out, grip, front, back


def pad(f):
    """TOP clear rows on top, RIGHT clear columns on the right."""
    H, W = f.shape[:2]
    out = np.zeros((H + TOP, W + RIGHT, 4), np.uint8)
    out[TOP:, :W] = f
    return out


# Codex's staff, as he draws it in every frame (measured along his staffs in the idle, W, Q and attack frames): from a
# tip, a red cap (CAP squares), a gold clasp with a dark groove round it (to GOLD), then the grey steel shaft; the cap and the
# clasp 4 squares across, the steel 2, all inside a one-square outline; lit from above (the upper side light, the lower
# side shaded). (t: squares from the tip along the staff; u: across it, + toward the bottom of the screen.)
CAP, GOLD = 4.5, 9.9
RINGS = ((6.6, 7.8),)  # one groove a whole square wide (thinner ones break into single pixels on the slant)
CORE, SHAFT, EDGE = 1.9, 1.0, 0.9
CHAMFER = 1.0          # the tip's corners cut back this far (Codex's tips are blunt, not square)
OUTLINE = (7, 16, 3)
C_CAP = {"hi": (241, 11, 3), "mid": (241, 2, 1), "lo": (194, 6, 4), "glint": (206, 108, 10)}
C_GOLD = {"hi": (254, 218, 21), "mid": (248, 213, 19), "lo": (230, 134, 17)}
C_RING = {"hi": (170, 78, 10), "mid": (148, 60, 12), "lo": (148, 60, 12)}   # a dark gold groove, not a red stripe
C_STEEL = {"hi": (114, 101, 82), "lo": (81, 44, 31)}
SLOPE = (3, 4)         # rows up per columns across: 36.9 degrees, the user's 36 on a step pattern that repeats every 4 columns


def staff_colour(t, u):
    """Codex's staff at (t, u) -> RGB or None (air)."""
    if t < -0.5:
        return None
    half = SHAFT if t >= GOLD else CORE
    half -= max(0.0, CHAMFER - t)                    # the tip's cut corners
    if abs(u) > half + EDGE:
        return None
    if abs(u) > half or t < 0.5:
        return OUTLINE
    if t < CAP:
        if u < -0.9:
            return C_CAP["glint"] if 1.5 <= t < CAP - 0.5 else C_CAP["hi"]      # the light along its upper edge
        return C_CAP["mid"] if u < 0.9 else C_CAP["lo"]
    if t < GOLD:
        fam = C_RING if any(a <= t < b for a, b in RINGS) else C_GOLD
        return fam["hi"] if u < -0.9 else (fam["mid"] if u < 0.9 else fam["lo"])
    return C_STEEL["hi"] if u < 0.0 else C_STEEL["lo"]


def _rod(base, grip, back_reach, front_reach):
    """The straight staff through `grip` (a square's middle) at SLOPE, back_reach squares up-right to one tip and
    front_reach down-left to the other, only into clear squares - behind his body, under his fist."""
    H, W = base.shape[:2]
    ry, rx = SLOPE
    n = math.hypot(rx, ry)
    ex, ey = rx / n, -ry / n                 # up-right along the staff
    nx, ny = ry / n, rx / n                  # across it, + down
    total = back_reach + front_reach
    tip = (grip[0] - ex * front_reach, grip[1] - ey * front_reach)       # the lower-left tip
    out = base.copy()
    for yy in range(H):
        for xx in range(W):
            if out[yy, xx, 3]:
                continue
            px, py = xx + 0.5 - tip[0], yy + 0.5 - tip[1]
            along = px * ex + py * ey
            if along < -0.5 or along > total + 0.5:
                continue
            c = staff_colour(min(along, total - along), px * nx + py * ny)
            if c is not None:
                out[yy, xx, :3] = c
                out[yy, xx, 3] = 255
    return out


def straighten_all(frames):
    """The idle's frames (RGBA, as Codex drew them) with one rigid staff through the near fist: at SLOPE in every frame,
    the same length in every frame (the mean of Codex's: his caps sit 10-15 squares and 51-58 squares from the fist), its
    axis through the middle of the square nearest each frame's grip (the same pixels in every frame, moved with his
    fist); padded (pad) -> (new frames, notes)."""
    cleared = [_cleared(f) for f in frames]
    fronts = [float(np.hypot(*(np.array(fc) - np.array(g)))) + CAP_END for _, g, fc, _ in cleared]
    backs = [float(np.hypot(*(np.array(bc) - np.array(g)))) + CAP_END for _, g, _, bc in cleared]
    front_reach, back_reach = round(float(np.mean(fronts))), round(float(np.mean(backs)))
    out, notes = [], []
    for (base, g, _, _) in cleared:
        grip = (math.floor(g[0]) + 0.5, math.floor(g[1]) + 0.5)
        out.append(_rod(base, grip, back_reach, front_reach))
        notes.append(f"grip ({grip[0]}, {grip[1]})")
    notes.append(f"slope {SLOPE[0]}:{SLOPE[1]} ({math.degrees(math.atan2(*SLOPE)):.1f} deg), reach front {front_reach}, back {back_reach}"
                 f" (Codex's: front {', '.join(f'{v:.1f}' for v in fronts)}; back {', '.join(f'{v:.1f}' for v in backs)})")
    return out, notes


def _load(name):
    return np.asarray(Image.open(os.path.join(ACT, name + ".png")).convert("RGBA"))


def preview(names, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    def show(a, z):
        bg = Image.new("RGBA", (a.shape[1], a.shape[0]), (80, 96, 80, 255))
        bg.alpha_composite(Image.fromarray(a))
        return bg.resize((a.shape[1] * z, a.shape[0] * z), Image.NEAREST)

    before = [_load(n) for n in names]
    after, notes = straighten_all(before)
    print("\n".join(notes))
    rows = []
    for n, a, b in zip(names, before, after):
        big = [show(pad(a), 8), show(b, 8)]
        t = Image.new("RGBA", (sum(i.width for i in big) + 30, big[0].height + 16), (30, 30, 30, 255))
        t.paste(big[0], (0, 16))
        t.paste(big[1], (big[0].width + 30, 16))
        ImageDraw.Draw(t).text((2, 2), f"{n}: before | after", fill=(255, 255, 0, 255))
        rows.append(t)
    W = max(r.width for r in rows)
    s = Image.new("RGBA", (W * 2 + 20, ((len(rows) + 1) // 2) * (rows[0].height + 10)), (20, 20, 20, 255))
    for k, r in enumerate(rows):
        s.paste(r, ((k % 2) * (W + 20), (k // 2) * (r.height + 10)))
    s.convert("RGB").save(os.path.join(out_dir, "wukong_idle_staff.png"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", required=True)
    ap.add_argument("names", nargs="*")
    a = ap.parse_args()
    preview(a.names or NAMES, a.preview)
