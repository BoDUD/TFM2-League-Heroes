#!/usr/bin/env python3
"""league_ahri redone at PPU 2.2 from Codex's picture (tools/art/design_ahri_hd.py; the user, 2026-10-23: 「下一个英雄重做
阿狸」), every action posed here from the design's own squares (rig_lux_hd.py's way) after her old frames and League's
clips (the user, 2026-10-24, Codex out of quota: 「你直接照着重画吧 没额度了」「做到完美了喊我review」).

    python tools/art/rig_ahri_hd.py --parts DIR         # the parts tinted
    python tools/art/rig_ahri_hd.py --review DIR        # every tag at 3x + GIFs
    python tools/art/rig_ahri_hd.py                     # orig strips + the 1x sheet
    python tools/art/hero_reels.py --hero ahri          # then: the idle / ban-pick reels from idle_base

No square is redrawn: the parts (the tails, the two legs, the body, the far arm raised by her face and the near arm
hanging by the tails) are cut square by square and placed only by whole squares, quarter turns and whole-row shifts;
the legs of the run and the falls are the design's own leg rows laid along two bones (Legs). Where an arm leaves, the
hair, robe and tails it covered are filled from their own squares beside it (UNDER). Standing, the parts rebuild the
design exactly (Poser.check).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design_ahri_hd as DA  # noqa: E402
import ppu_rig as R  # noqa: E402
import rig_xinzhao_hd as XZ  # noqa: E402

HERO = "ahri"
PPU = DA.PPU
DESIGN_ROWS = 88
ROWS = DESIGN_ROWS / PPU
SQUARE = XZ.SQUARE
HD = os.path.join(R.ROOT, "assets", "source", HERO, "hd")
PAD = 48
PIVOT_COL = 58                  # between the soles (her near boot 49-56, her far one 58-68)
OUTLINE = (10, 2, 16)
O = OUTLINE


def lp(path):
    return R.lp(path)


def hexes(d):
    return np.array([["%02X%02X%02X" % tuple(int(v) for v in d[y, x, :3]) for x in range(d.shape[1])]
                     for y in range(d.shape[0])])


# ------------------------------------------------------------------------------------------------ the parts
OUT_HEX = "%02X%02X%02X" % OUTLINE
HAIR = {"1A1738", "282655", "494693"}
HAIR_SHADE = {"6C5984"}
TAIL = {"8A7CBA", "9A86A7", "A99BDF", "CBBAD5", "BFB3F9", "D0C6FB", "E5DCFC", "FCFBFC", "DAC0C5"}
TAIL_SEED = (20, 40)            # a square of the tails' fan
TAIL_BITS_X = 40                # tail-coloured specks west of this column (between hair locks) are tails too
NEAR_SEED, NEAR_TOP, NEAR_BOX = (50, 48), 45, (40, 43, 54, 63)        # the near arm: x0, y0, x1, y1
FAR_SEED, FAR_BOX = (71, 34), (66, 27, 77, 47)                       # the far arm
FAR_EXTRA = [(73, 29), (73, 30)]                                     # its nail tip, walled off by its outline
LEG_TOP = 58                    # the legs from this row down (the skirt's hem above)
KNEE_ROW = 72
TASSEL = {"5C1FA2", "7127CC", "9D4EF5", "5B257E"}
# the columns of each leg, per row band: near (image left, in front) west of the split, far east of it
LEG_SPLIT = [(58, 71, 59), (72, 88, 58)]         # rows y0..y1: far leg from this column
LEG_COLS = [(58, 63, 53, 63), (64, 88, 49, 70)]   # rows y0..y1: the legs' columns x0..x1
HAIR_SEED, HAIR_BOX = (40, 50), (30, 36, 50, 62)                      # the long hair hanging down her back
PARTS = ["tails", "hair", "leg_far", "leg_near", "upper", "arm_far", "arm_near"]     # back to front
Z = {name: i for i, name in enumerate(PARTS)}


def flood(allowed, seed, box=None):
    m = allowed.copy()
    if box is not None:
        x0, y0, x1, y1 = box
        yy, xx = np.mgrid[0:m.shape[0], 0:m.shape[1]]
        m &= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    lbl, _ = ndimage.label(m)
    return lbl == lbl[seed[1], seed[0]]


def masks(d):
    """The parts' squares: each colour square in one part; each outline square with the frontmost part beside it
    (a seam belongs to the part in front: when that part moves, the one behind shows its own squares there)."""
    op = d[..., 3] > 0
    H, W = op.shape
    hx = hexes(d)
    out = op & (hx == OUT_HEX)
    col = op & ~out
    yy, xx = np.mgrid[0:H, 0:W]
    tail_col = col & np.isin(hx, list(TAIL))
    tails = flood(tail_col, TAIL_SEED)
    lbl, n = ndimage.label(tail_col)
    for j in range(1, n + 1):
        comp = lbl == j
        if xx[comp].max() < TAIL_BITS_X:
            tails |= comp
    # the tails' own shading in a hair colour (a few dark squares walled in by the fan): tails too
    fan = ndimage.binary_dilation(tails)
    holes = ndimage.binary_fill_holes(fan) & ~fan & op
    lbl, n = ndimage.label(holes)
    for j in range(1, n + 1):
        if (lbl == j).sum() <= 12:
            tails |= (lbl == j) & col
    # ... and lone dark squares among the tails' squares (the fan's own shading), nothing but tails round them
    cand = col & ~tails
    lbl, n = ndimage.label(cand, structure=np.ones((3, 3)))
    for j in range(1, n + 1):
        comp = lbl == j
        if comp.sum() > 6:
            continue
        ring = ndimage.binary_dilation(comp, structure=np.ones((5, 5))) & ~comp & col
        if ring.any() and (tails[ring]).all():
            tails |= comp
    allowed = col & ~np.isin(hx, list(HAIR)) & ~tails
    near = flood(allowed & (yy >= NEAR_TOP), NEAR_SEED, NEAR_BOX)
    hair = flood(col & np.isin(hx, list(HAIR | HAIR_SHADE)) & ~tails, HAIR_SEED, HAIR_BOX)
    far = flood(allowed, FAR_SEED, FAR_BOX)
    for x, y in FAR_EXTRA:
        far[y, x] = True
    legs = np.zeros_like(op)
    for y0, y1, x0, x1 in LEG_COLS:
        legs |= (yy >= y0) & (yy <= y1) & (xx >= x0) & (xx <= x1)
    legs &= col & ~near & ~far & ~tails & ~hair
    # above the knees, the tails' lower lobe, a hair lock and the sash's violet tassel lie beside the thighs: not legs
    legs &= ~((yy < KNEE_ROW) & np.isin(hx, list(TAIL | HAIR | TASSEL)))
    split = np.full((H, W), 999)
    for y0, y1, s in LEG_SPLIT:
        split[y0:y1 + 1] = s
    leg_near, leg_far = legs & (xx < split), legs & (xx >= split)
    parts = {"tails": tails, "hair": hair, "leg_far": leg_far, "leg_near": leg_near, "arm_far": far, "arm_near": near}
    taken = np.zeros_like(op)
    for m in parts.values():
        taken |= m
    parts["upper"] = col & ~taken
    owner = np.full((H, W), -1)
    for name, m in parts.items():
        owner[m] = Z[name]
    for y, x in zip(*np.nonzero(out)):
        best = -1
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            q = (y + dy, x + dx)
            if 0 <= q[0] < H and 0 <= q[1] < W:
                best = max(best, owner[q])
        if best < 0:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (y + dy, x + dx)
                    if 0 <= q[0] < H and 0 <= q[1] < W:
                        best = max(best, owner[q])
        if best < 0:                                     # an outline square among outline squares: the nearest part's
            dist = np.where(owner >= 0, (yy - y) ** 2 + (xx - x) ** 2, 10 ** 9)
            best = owner.flat[int(np.argmin(dist))]
        parts[PARTS[best]] = parts[PARTS[best]] | ((yy == y) & (xx == x))
    return {name: parts[name] for name in PARTS}


def piece(d, m):
    """The squares of mask m cut out on their bounding box, and the box's top-left (x, y)."""
    ys, xs = np.nonzero(m)
    sub = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
    return sub, (int(xs.min()), int(ys.min()))


# ------------------------------------------------------------------------------------------------ drawing
class Frame:
    """A frame being composed in design squares (PAD squares round the design)."""

    def __init__(self, d):
        self.d = d
        self.a = np.zeros((d.shape[0] + 2 * PAD, d.shape[1] + 2 * PAD, 4), np.uint8)

    def stamp(self, img, x0, y0, under=False):
        ys, xs = np.nonzero(img[..., 3] > 0)
        Y, X = ys + y0 + PAD, xs + x0 + PAD
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
        if under:                                       # only where nothing is drawn yet
            free = self.a[Y, X, 3] == 0
            Y, X, ys, xs = Y[free], X[free], ys[free], xs[free]
        self.a[Y, X] = img[ys, xs]


def sheared(img, k, pivot, up, profile=1.0):
    """img's rows shifted: k columns at the far end, growing from 0 at row `pivot` - rows below it (up False) or above
    it (up True: the tails' fan over its root)."""
    h, w = img.shape[:2]
    if up:
        s = [0 if r >= pivot else int(round(k * ((pivot - r) / max(1, pivot)) ** profile)) for r in range(h)]
    else:
        s = [0 if r <= pivot else int(round(k * ((r - pivot) / max(1, h - 1 - pivot)) ** profile)) for r in range(h)]
    lo, hi = min(s), max(s)
    out = np.zeros((h, w + hi - lo, 4), np.uint8)
    for r in range(h):
        out[r, s[r] - lo:s[r] - lo + w] = img[r]
    return out, lo


def transformed(img, x0, y0, t):
    """A part's picture (top-left x0, y0 in design squares) moved by its transform t: "shear" (whole rows shifted,
    `shear` columns at the far end from row `pivot`, design rows; `up` for the rows above it), "rot" (quarter turns
    clockwise on screen about t["about"]), "mirror" (left-right about t["about"]'s column), then (dx, dy)."""
    out, x, y = img, x0, y0
    k = t.get("shear", 0)
    if k:
        out, lo = sheared(out, k, t.get("pivot", 0) - y, t.get("up", False), t.get("profile", 1.0))
        x += lo
    if t.get("rot") or t.get("mirror"):
        ax, ay = t["about"]
        ys, xs = np.nonzero(out[..., 3] > 0)
        fx, fy = xs + x + 0.5, ys + y + 0.5
        if t.get("mirror"):
            fx = 2 * ax - fx
        for _ in range(t.get("rot", 0) % 4):
            fx, fy = ax - (fy - ay), ay + (fx - ax)
        tx, ty = np.floor(fx).astype(int), np.floor(fy).astype(int)
        nx, ny = tx.min(), ty.min()
        new = np.zeros((ty.max() - ny + 1, tx.max() - nx + 1, 4), np.uint8)
        new[ty - ny, tx - nx] = out[ys, xs]
        out, x, y = new, nx, ny
    return out, x + t.get("dx", 0), y + t.get("dy", 0)


def fold(cells, outline=O):
    """A bone's squares with the outline ring closed round them (the slices carry no edge squares of their own)."""
    out = dict(cells)
    for (x, y) in list(cells):
        for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + ddx, y + ddy)
            if q not in cells:
                out.setdefault(q, np.array((*outline, 255), np.uint8))
    return out


def cells_img(cells):
    """{(x, y): rgba} -> (picture, x0, y0)."""
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    x0, y0 = min(xs), min(ys)
    img = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
    for (x, y), c in cells.items():
        img[y - y0, x - x0, :3] = np.asarray(c)[:3]
        img[y - y0, x - x0, 3] = 255
    return img, x0, y0


# ------------------------------------------------------------------------------------------------ the legs
# The run's and the falls' legs are the idle's own (league_jinx: 「走路时和待机时 左腿不一样了？」), on two bones each: the
# thigh is the design's thigh rows (bare skin under the skirt's hem, then the red stocking) laid along hip -> knee, the
# shin the design's knee and shin rows along knee -> ankle - a square near the bone takes the row at that length and
# its square at that side (each row less the outline square at each end; one outline ring round each bone); below
# the ankle the design's whole boot hangs as drawn, never turned standing (「脚变形」).
GROUND = 88.0                   # the soles' bottom edge
THIGH_ROWS = {"near": (58, 71), "far": (58, 71)}
SHIN_ROWS = {"near": (72, 79), "far": (72, 79)}
HIP = {"near": (56.0, 56.0), "far": (61.0, 56.0)}
KNEE = {"near": (55.5, 72.0), "far": (60.5, 72.0)}
ANKLE = {"near": (53.0, 80.0), "far": (61.0, 80.0)}    # where the boot's top meets the shin


class Legs:
    def __init__(self, d, M):
        hx = hexes(d)
        self.slices, self.boot = {}, {}
        for key in ("near", "far"):
            m = M["leg_" + key]
            for seg, (r0, r1) in (("thigh", THIGH_ROWS[key]), ("shin", SHIN_ROWS[key])):
                rows = []
                for y in range(r0, r1 + 1):
                    xs = np.nonzero(m[y] & (hx[y] != OUT_HEX))[0]
                    rows.append(d[y, xs.min():xs.max() + 1].copy())
                self.slices[(key, seg)] = rows
            yy = np.arange(d.shape[0])[:, None]
            self.boot[key] = piece(d, m & (yy >= int(ANKLE[key][1])))

    def bone(self, rows, A, B):
        """{(x, y): rgba} the rows laid along A -> B (square edges)."""
        A, B = np.asarray(A, float), np.asarray(B, float)
        v = B - A
        L = max(1e-6, float(np.hypot(*v)))
        u = v / L
        n = np.array((u[1], -u[0]))                     # down -> +x: a row's left stays on the left
        cells = {}
        for y in range(int(math.floor(min(A[1], B[1]))) - 6, int(math.ceil(max(A[1], B[1]))) + 6):
            for x in range(int(math.floor(min(A[0], B[0]))) - 6, int(math.ceil(max(A[0], B[0]))) + 6):
                p = np.array((x + 0.5, y + 0.5)) - A
                t, s_ = float(p @ u), float(p @ n)
                if t < -0.5 or t > L + 0.5:
                    continue
                row = rows[int(round(min(1.0, max(0.0, t / L)) * (len(rows) - 1)))]
                xi = int(math.floor(len(row) / 2 + s_))
                if 0 <= xi < len(row) and row[xi][3]:
                    cells[(x, y)] = row[xi]
        return cells

    def items(self, key, hip, knee, ankle, turn=0):
        """Items (z, name, picture, x, y) of one leg: its thigh hip -> knee, its shin knee -> ankle (over the thigh)
        and its whole boot at the ankle (turned `turn` quarter turns clockwise about it: lying)."""
        z = Z["leg_" + key]
        out = []
        for i, (seg, A, B) in enumerate((("thigh", hip, knee), ("shin", knee, ankle))):
            img, x0, y0 = cells_img(fold(self.bone(self.slices[(key, seg)], A, B)))
            out.append((z + 0.01 * i, seg + "_" + key, img, x0, y0))
        bimg, (bx, by) = self.boot[key]
        ax, ay = ANKLE[key]
        if turn:
            bimg, bx, by = transformed(bimg, bx, by, dict(rot=turn, about=(ax, ay)))
        out.append((z + 0.05, "boot_" + key, bimg, int(round(bx + ankle[0] - ax)), int(round(by + ankle[1] - ay))))
        return out


# ------------------------------------------------------------------------------------------------ under the arms
UNDER_CLOSE = 2


def under(d, M, arm):
    """{(x, y): rgba} what shows where `arm` was when it moves: inside the body's silhouette without it (the hull of
    the rest, holes closed), each square the colour of the nearest colour square of the body or the tails; outside it
    nothing (the background)."""
    op = d[..., 3] > 0
    hx = hexes(d)
    rest = op & ~M[arm] if arm != "hair" else op
    hull = ndimage.binary_fill_holes(ndimage.binary_closing(rest, structure=np.ones((3, 3)), iterations=UNDER_CLOSE))
    src = (M["upper"] | M["tails"]) & (hx != OUT_HEX)
    if arm == "hair":                                   # behind the long hair: more of its own dark locks
        src = (M["upper"] | M["hair"]) & np.isin(hx, list(HAIR))
    _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
    out = {}
    for y, x in zip(*np.nonzero(M[arm] & hull)):
        out[(x, y)] = d[iy[y, x], ix[y, x]].copy()
    return out


# ------------------------------------------------------------------------------------------------ composing
UPPER = ["tails", "hair", "upper", "arm_far", "arm_near"]      # what "trunk" moves (over the legs)


def compose(d, pieces, pose, legs, unders):
    """pose: {"dx", "dy": the whole figure; "trunk": tails, hair, body and arms over the legs (dx, dy); a part's name: its
    transform (dx, dy, shear, rot, mirror, about); "legs": {"near" / "far": (hip, knee, ankle)} the legs on bones
    (Legs.items); "prone": the death on the ground (prone_items)}."""
    f = Frame(d)
    gdx, gdy = pose.get("dx", 0), pose.get("dy", 0)
    items = []
    hide = set()
    lg = pose.get("legs")
    if lg:
        hide |= {"leg_near", "leg_far"}
        for key in ("near", "far"):
            items += legs.items(key, *lg[key])
    for name in PARTS:
        if name in hide:
            continue
        img, (x0, y0) = pieces[name]
        if name == "upper":
            img = img.copy()
            for arm in ("arm_far", "arm_near", "hair"):
                if pose.get(arm):                       # the arm (or the hair) moves: what it covered shows
                    for (x, y), c in unders[arm].items():
                        img[y - y0, x - x0] = c
        items.append((Z[name], name, img, x0, y0))
    if pose.get("prone"):
        items = prone_items(pieces, pose["prone"], legs, unders, pose)
    for _, name, img, x0, y0 in sorted(items, key=lambda t: t[0]):
        out, x, y = transformed(img, x0, y0, dict(pose.get(name, {})))
        if name in UPPER and "trunk" in pose:
            out, x, y = transformed(out, x, y, pose["trunk"])
        f.stamp(out, x + gdx, y + gdy)
    return f.a


# The death on her back (League's and her old sheet's: knocked over, she lands, bounces and lies still): her body,
# hair and arms turn a quarter counter-clockwise about her hips (no square redrawn) and lie on the ground, head to the
# left; her near leg is drawn on its bones from the turned hip - thrown up as she lands, then lying along the ground
# - with the design's whole lower leg turned (DEAD_TURN). The tails, which grow from under her, turn a quarter
# counter-clockwise and mirror about their root (a lossless move): the long upper tail then lies along the ground
# over her legs (her old sheet's death), the others fall below the ground line and are not drawn (on_rig clears it).
PRONE_PIVOT = (58.0, 58.0)
# the knee from the turned hip and the ankle from the knee (dx, dy in squares)
DEAD_LEGS = {"up": ((2, -12), (6, -6)), "flat": ((14, 0), (8, 1))}
DEAD_TURN = {"up": 2, "flat": 3}                  # the lower leg: upside down (soles to the sky), or lying toes-up
TAIL_ROOT_AT = (47.0, 62.0)                       # the tails' root, design squares


def prone_items(pieces, pr, legs, unders, pose):
    """Items of the body on its back: pr = {"lift": rows off the ground, "dx": columns on, "legs": "up" | "flat"}."""
    group = []
    for name in ("hair", "upper", "arm_far", "arm_near"):
        img, (x0, y0) = pieces[name]
        group.append((Z[name], name, img, x0, y0))
    px, py = PRONE_PIVOT
    turned = [(z, n) + transformed(img, x, y, dict(rot=3, about=(px, py))) for z, n, img, x, y in group]
    bottom = max(y + img.shape[0] for _, n, img, x, y in turned if n == "upper")
    sy = int(round(GROUND - bottom)) - pr.get("lift", 0)
    sx = pr.get("dx", 0)
    items = [(z, n + "_lying", img, x + sx, y + sy) for z, n, img, x, y in turned]
    hx, hy = px + sx, py + sy                           # the turned hip
    mode = pr.get("legs", "flat")
    (kdx, kdy), (adx, ady) = DEAD_LEGS[mode]
    items += [(Z["leg_far"] if it[1].endswith("near") else it[0],) + it[1:] for it in
              legs.items("near", (hx, hy), (hx + kdx, hy + kdy), (hx + kdx + adx, hy + kdy + ady), turn=DEAD_TURN[mode])]
    img, (x0, y0) = pieces["tails"]
    rx, ry = TAIL_ROOT_AT
    t, tx, ty = transformed(img, x0, y0, dict(rot=1, mirror=True, about=(rx, ry)))   # (x, y) -> (-y, -x)
    # the root (turned onto itself) under the turned hips
    items.append((Z["tails"] - 1, "tails_lying", t, tx + int(round(hx - rx)) + pr.get("tail_dx", 0),
                  ty + int(round(hy - ry)) + pr.get("tail_dy", 0)))
    return items


# ------------------------------------------------------------------------------------------------ poses
STAND = {}


def P(dx=0, **kw):
    """A pose: the whole figure moved dx columns (legs and all) and any part's transform in kw."""
    out = dict(kw)
    if dx:
        out["dx"] = dx
    return out


TAIL_ROOT = 62                  # the row the tails grow from (behind her hips)


def tails(k, up=True):
    """The tails swinging: their tips k columns (right +) from where they fan, the root still."""
    return {"tails": dict(shear=k, pivot=TAIL_ROOT, up=up, profile=1.3)}


# The run (8 frames of 125 ms), the legs half a cycle apart through RUN_PHASE: (thigh, shin) degrees from straight
# down (+ = forward) and the rows the whole leg is lifted; the planted leg lands ahead, sweeps back under her and
# pushes off, the free leg kicks its foot up behind and swings its knee forward - the feet cross every half cycle.
RUN_HIP_X = {"near": 57.0, "far": 59.0}
RUN_HIP_Y = 56.0
RUN_LEAN = 1
RUN_PHASE = [(25, 8, 0), (12, 0, 0), (0, -6, 0), (-14, -16, 0), (-24, -40, 1), (-8, -62, 4), (16, -28, 3), (28, 2, 1)]
TAILS_RUN = [-4, -6, -5, -3, -4, -6, -5, -3]
HAIR_RUN = [2, 3, 2, 1, 2, 3, 2, 1]


def run_poses():
    lt = {k: float(np.hypot(*np.subtract(KNEE[k], HIP[k]))) for k in KNEE}
    ls = {k: float(np.hypot(*np.subtract(ANKLE[k], KNEE[k]))) for k in KNEE}
    bh = {k: GROUND - ANKLE[k][1] for k in KNEE}
    out = []
    for i in range(len(RUN_PHASE)):
        spec = {"near": RUN_PHASE[i], "far": RUN_PHASE[(i + 4) % len(RUN_PHASE)]}
        rad = {k: (math.radians(v[0]), math.radians(v[1])) for k, v in spec.items()}
        plant = [k for k in spec if spec[k][2] == 0]
        hy = max(GROUND - bh[k] - lt[k] * math.cos(rad[k][0]) - ls[k] * math.cos(rad[k][1]) for k in plant)
        lgs = {}
        for key in ("near", "far"):
            th, sh = rad[key]
            hip = np.array((RUN_HIP_X[key], hy - spec[key][2]))
            knee = hip + lt[key] * np.array((math.sin(th), math.cos(th)))
            ankle = knee + ls[key] * np.array((math.sin(sh), math.cos(sh)))
            lgs[key] = (tuple(hip), tuple(knee), tuple(ankle))
        out.append(dict(trunk=dict(dx=RUN_LEAN, dy=int(round(hy - RUN_HIP_Y))), legs=lgs,
                        **sway(TAILS_RUN[i], HAIR_RUN[i])))
    return out


def stance(spec, lean=0, hip_x=None, sink=0):
    """A pose's legs on bones: spec {"near" / "far": (thigh, shin) degrees from straight down (+ forward), the rows
    the leg is lifted}; the planted feet on the ground, the upper body on the hips (lean columns ahead, sink rows
    lower). -> {"legs", "trunk"}."""
    hip_x = hip_x or {k: HIP[k][0] for k in HIP}
    lt = {k: float(np.hypot(*np.subtract(KNEE[k], HIP[k]))) for k in KNEE}
    ls = {k: float(np.hypot(*np.subtract(ANKLE[k], KNEE[k]))) for k in KNEE}
    bh = {k: GROUND - ANKLE[k][1] for k in KNEE}
    rad = {k: (math.radians(v[0]), math.radians(v[1])) for k, v in spec.items()}
    plant = [k for k in spec if spec[k][2] == 0] or list(spec)
    hy = max(GROUND - bh[k] - lt[k] * math.cos(rad[k][0]) - ls[k] * math.cos(rad[k][1]) for k in plant) + sink
    lgs = {}
    for key in ("near", "far"):
        th, sh = rad[key]
        hip = np.array((hip_x[key] + lean, hy - spec[key][2]))
        knee = hip + lt[key] * np.array((math.sin(th), math.cos(th)))
        ankle = knee + ls[key] * np.array((math.sin(sh), math.cos(sh)))
        lgs[key] = (tuple(hip), tuple(knee), tuple(ankle))
    return {"legs": lgs, "trunk": dict(dx=lean, dy=int(round(hy - HIP["near"][1])))}


LT = {k: float(np.hypot(*np.subtract(KNEE[k], HIP[k]))) for k in KNEE}
LS = {k: float(np.hypot(*np.subtract(ANKLE[k], KNEE[k]))) for k in KNEE}
BEND = {"near": 1, "far": -1}                    # the design's knees: the near one ahead of its hip-ankle line


def ik(hip, ankle, lt, ls, bend):
    """The knee of a two-bone leg from hip to ankle (the ankle pulled in when out of reach): on the side `bend`
    (+1 ahead, -1 behind) of the hip-ankle line."""
    hip, ankle = np.asarray(hip, float), np.asarray(ankle, float)
    v = ankle - hip
    L = float(np.hypot(*v))
    if L > lt + ls - 1e-3:
        ankle = hip + v / L * (lt + ls - 1e-3)
        v, L = ankle - hip, lt + ls - 1e-3
    a = (lt * lt - ls * ls + L * L) / (2 * L)
    h = math.sqrt(max(0.0, lt * lt - a * a))
    base = hip + v / L * a
    perp = np.array((-v[1], v[0])) / L                  # the line turned a quarter: (-y, x)
    k1, k2 = base + perp * h, base - perp * h
    knee = k1 if (k1[0] - k2[0]) * bend >= 0 else k2
    return tuple(hip), tuple(knee), tuple(ankle)


def feet(at, lean=0, sink=0, bend=None, hip_dy=None):
    """Legs placed by their ankles: at {"near" / "far": (ankle x, rows lifted)} (design squares), the hips `lean`
    columns ahead and `sink` rows lower than the design's (hip_dy: per leg, a hip raised as the body twists); the
    knees by ik(). -> {"legs", "trunk"}."""
    bend = dict(BEND, **(bend or {}))
    lgs = {}
    for k in ("near", "far"):
        hip = (HIP[k][0] + lean, HIP[k][1] + sink + (hip_dy or {}).get(k, 0))
        ax, lift = at[k]
        lgs[k] = ik(hip, (ax, ANKLE[k][1] - lift), LT[k], LS[k], bend[k])
    return {"legs": lgs, "trunk": dict(dx=lean, dy=sink)}


def F(at, lean=0, sink=0, bend=None, **kw):
    """A pose on feet() legs plus any part's transform in kw."""
    out = feet(at, lean=lean, sink=sink, bend=bend)
    if "trunk" in kw:
        u = kw.pop("trunk")
        out["trunk"] = dict(dx=out["trunk"]["dx"] + u.get("dx", 0), dy=out["trunk"]["dy"] + u.get("dy", 0))
    out.update(kw)
    return out


FEET = {"near": (ANKLE["near"][0], 0), "far": (ANKLE["far"][0], 0)}   # where the design stands


def at(near=0, far=0, lift_near=0, lift_far=0):
    """The ankles moved from where the design stands (columns) and lifted (rows)."""
    return {"near": (FEET["near"][0] + near, lift_near), "far": (FEET["far"][0] + far, lift_far)}


def S(spec, lean=0, sink=0, **kw):
    """A pose on stance() legs plus any part's transform in kw."""
    out = stance(spec, lean=lean, sink=sink)
    out.update(kw)
    return out


FWD = dict(rot=1, about=(70, 41), dy=-1)        # the far arm thrust forward: its forearm turned level, palm out


def fwd(dx=0, dy=0):
    return dict(FWD, dx=FWD.get("dx", 0) + dx, dy=FWD["dy"] + dy)


def far(dx=0, dy=0):
    return dict(dx=dx, dy=dy)


SET = {"near": (0, 0, 0), "far": (0, 0, 0)}       # straight legs


IN = dict(dx=-2, dy=3)                          # the far arm drawn in: the hand by her chin, ready to throw


def sway(tk=0, hk=0):
    """The tails' tips tk columns and the long hair's ends hk columns from where they hang (right +)."""
    out = {}
    if tk:
        out["tails"] = dict(shear=tk, pivot=TAIL_ROOT, up=True, profile=1.3)
    if hk:
        out["hair"] = dict(shear=hk, pivot=HAIR_PIVOT, profile=1.2)
    return out


HAIR_PIVOT = 40                 # the long hair hangs still above this row


def Q(dx=0, dy=0, lean=0, far=None, near=None, tk=0, hk=0, legs=None, sink=0, bend=None):
    """A pose: the whole figure moved (dx, dy), the upper body `lean` columns over the legs (legs: feet() on bones
    at those ankles instead of the design's own legs, sinking `sink` rows), the far / near arm's transform, the sway."""
    out = feet(legs, lean=lean, sink=sink, bend=bend) if legs else ({"trunk": dict(dx=lean)} if lean else {})
    if dx:
        out["dx"] = dx
    if dy:
        out["dy"] = dy
    if far:
        out["arm_far"] = far
    if near:
        out["arm_near"] = near
    out.update(sway(tk, hk))
    return out


POSES = {
    # the orb flicked from her raised hand (the kit's shot on the 4th frame, 233 ms): she draws the hand in by her
    # chin and sways back, thrusts the arm out at the foe stepping in, holds, settles
    "attack": [Q(far=IN, tk=-2, hk=1),
               Q(lean=-1, far=IN, tk=-6, hk=2),
               Q(lean=-2, far=dict(IN, dx=-3), tk=-8, hk=2, legs=at(-2, 1), sink=1),
               Q(lean=2, far=fwd(1), tk=3, hk=-2, legs=at(-3, 3), sink=2),
               Q(lean=2, far=fwd(1), tk=2, hk=-2, legs=at(-3, 3), sink=2),
               Q(lean=1, far=far(-1, 1), tk=1, hk=-1),
               Q(tk=0)],
    # Orb of Deception (the throw on the 4th frame, 167 ms): she crouches drawing the hand in, springs up, throws in
    # the air, lands in a lunge and rises
    "skill": [Q(far=IN, tk=-3, hk=1, legs=at(-1, 1), sink=3),
              Q(dy=-6, far=dict(IN, dy=1), tk=-7, hk=2),
              Q(dy=-9, far=dict(IN, dx=-3), tk=-9, hk=3),
              Q(dy=-7, lean=2, far=fwd(2), tk=4, hk=-2),
              Q(dy=-4, lean=2, far=fwd(2), tk=3, hk=-2),
              Q(lean=2, far=fwd(1), tk=2, hk=-1, legs=at(-4, 4), sink=4),
              Q(far=far(-1, 1), tk=0, legs=at(-2, 2), sink=2),
              Q(tk=0)],
    # Charm (the kiss on the 3rd frame, 150 ms): the hand to her lips, the kiss blown out at the foe, held, back
    "skill2": [Q(far=far(-2, 1), tk=-2, hk=1),
               Q(lean=-1, far=far(-3, 2), tk=-4, hk=1),
               Q(lean=1, far=fwd(1), tk=3, hk=-1, legs=at(-2, 2), sink=1),
               Q(lean=1, far=fwd(1), tk=2, hk=-1, legs=at(-2, 2), sink=1),
               Q(far=fwd(), tk=1),
               Q(far=far(-1), tk=0),
               Q(tk=0)],
    # Spirit Rush (the dash from the 1st frame): she crouches, dashes low (the tails and hair streaming back), lands
    "ult": [Q(near=far(-1), tk=-4, hk=1, legs=at(-2, 2), sink=3),
            Q(lean=3, far=fwd(1), near=far(-2, -1), tk=-11, hk=4, legs=at(-8, 5), sink=4),
            Q(lean=3, far=fwd(1), near=far(-2, -1), tk=-13, hk=5, legs=at(-8, 5), sink=4),
            Q(lean=3, far=fwd(1), near=far(-2, -1), tk=-14, hk=5, legs=at(-8, 5), sink=4),
            Q(lean=3, far=fwd(1), near=far(-2, -1), tk=-13, hk=5, legs=at(-8, 5), sink=4),
            Q(lean=3, far=fwd(1), near=far(-2, -1), tk=-12, hk=4, legs=at(-8, 5), sink=4),
            Q(lean=2, near=far(-1), tk=-7, hk=3, legs=at(-4, 4), sink=4),
            Q(tk=-3, hk=1, legs=at(-2, 2), sink=2),
            Q(tk=0)],
    "hit": [Q(dx=-2, tk=4, hk=-2), Q(dx=-1, tk=2, hk=-1)],
    # struck: knocked back off her feet, she lands and sinks down
    "dead": [Q(dx=-2, tk=4, hk=-2),
             Q(dx=-4, dy=-4, tk=6, hk=-3),
             dict(prone=dict(lift=7, dx=-10, legs="up")),
             dict(prone=dict(lift=1, dx=-12, legs="up")),
             dict(prone=dict(lift=0, dx=-12, legs="flat")),
             dict(prone=dict(lift=1, dx=-12, legs="flat")),
             dict(prone=dict(lift=0, dx=-12, legs="flat")),
             dict(prone=dict(lift=0, dx=-12, legs="flat"))],
}


# ------------------------------------------------------------------------------------------------ the rig
def picture(d):
    big = np.repeat(np.repeat(d, SQUARE, 0), SQUARE, 1)
    pad = np.zeros((big.shape[0] + 4 * SQUARE, big.shape[1] + 4 * SQUARE, 4), np.uint8)
    pad[2 * SQUARE:-2 * SQUARE, 2 * SQUARE:-2 * SQUARE] = big
    Image.fromarray(pad).save(lp(os.path.join(HD, "picture.png")))


def design():
    d = np.asarray(Image.open(lp(os.path.join(HD, "design.png"))).convert("RGBA"))
    picture(d)
    D = XZ.Design(HERO, PPU, ROWS, regrid=SQUARE)
    if D.d.shape != d.shape or (D.d != d).any():
        sys.exit("hd/picture.png does not read back as hd/design.png")
    D.px = PIVOT_COL
    D.d0 = D.d.copy()
    return D


def drop_stray_outline(can):
    """Outline squares with no coloured square within two (a moved part's corner) taken out, until none is left."""
    out = can.copy()
    while True:
        op = out[..., 3] > 0
        isout = op & (np.abs(out[..., :3].astype(int) - np.array(O)).sum(-1) < 30)
        near = ndimage.binary_dilation(op & ~isout, structure=np.ones((5, 5), bool))
        stray = isout & ~near
        if not stray.any():
            return out
        out[stray] = 0


class AhriRig(R.Rig):
    def finish(self, can):
        return drop_stray_outline(super().finish(can))


def on_rig(rig, a):
    """A composed frame (design squares + PAD) on the rig's canvas (the design's (0, 0) at ox, oy)."""
    can = rig.canvas()
    ys, xs = np.nonzero(a[..., 3] > 0)
    Y, X = ys - PAD + rig.oy, xs - PAD + rig.ox
    ok = (Y >= 0) & (Y < can.shape[0]) & (X >= 0) & (X < can.shape[1])
    can[Y[ok], X[ok]] = a[ys[ok], xs[ok]]
    can[rig.GY:] = 0
    return can


class Poser:
    def __init__(self, d):
        self.d = d
        self.M = masks(d)
        self.pieces = {n: piece(d, m) for n, m in self.M.items()}
        self.unders = {arm: under(d, self.M, arm) for arm in ("arm_far", "arm_near", "hair")}
        self.legs = Legs(d, self.M)

    def check(self):
        """Standing, the parts rebuild the design square for square; the parts cover it once."""
        d = self.d
        op = d[..., 3] > 0
        n = sum(m.astype(int) for m in self.M.values())
        if (n[op] != 1).any() or (n[~op] != 0).any():
            sys.exit(f"parts: {int((n[op] != 1).sum())} squares not in exactly one part")
        a = self.frame(STAND)
        got = a[PAD:PAD + d.shape[0], PAD:PAD + d.shape[1]]
        if (got != d).any() or int((a[..., 3] > 0).sum()) != int(op.sum()):
            sys.exit("the standing pose does not rebuild the design")

    def frame(self, pose):
        return compose(self.d, self.pieces, pose, self.legs, self.unders)


def frames(rig):
    d = rig.D.d0
    ps = Poser(d)
    ps.check()
    sheet = R.sheet_of(HERO)
    out = {}
    for tag in sheet:
        if tag in ("idle", "bp"):
            continue
        n = len(sheet[tag])
        if tag in POSES:
            poses = POSES[tag]
        elif tag == "run":
            poses = run_poses()
        else:
            poses = [STAND] * n
        if len(poses) != n:
            sys.exit(f"{tag}: {len(poses)} poses for {n} frames")
        fr = [on_rig(rig, ps.frame(p)) for p in poses]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        out[tag] = list(zip(fr, [m for _, m in sheet[tag]]))
    out["idle"] = [(fr_, m) for fr_, m in out["idle_base"]]
    return {t: out[t] for t in sheet if t in out}


def parts_picture(d, M, out):
    tint = {"tails": (0, 220, 255), "hair": (255, 120, 200), "leg_far": (140, 70, 20), "leg_near": (255, 0, 0), "upper": (60, 200, 60),
            "arm_far": (170, 0, 255), "arm_near": (255, 230, 0)}
    img = np.zeros(d.shape[:2] + (3,), np.uint8) + 200
    for name, m in M.items():
        img[m] = (d[m, :3] * 0.45 + np.array(tint[name]) * 0.55).astype(np.uint8)
    Image.fromarray(img).resize((d.shape[1] * 8, d.shape[0] * 8), Image.NEAREST).save(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    rig = AhriRig(D, pad=(120, 110, 110, 30))
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        ps = Poser(D.d0)
        ps.check()
        parts_picture(D.d0, ps.M, os.path.join(a.parts, "ahri_parts.png"))
        return
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
