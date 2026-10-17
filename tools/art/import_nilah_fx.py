#!/usr/bin/env python3
"""Nilah's effects from Codex's overview (assets/source/nilah/codex_fx/overview.jpg: Codex delivered one picture of its
drafts before its quota ran out; the user: 「你拿我给你的这个修复啊 这个特效好啊」) as the game sheets league_nilah_fx /
league_nilah_big and the pictures drawn into her frames (assets/source/nilah/fx_bake, laid in by rig_nilah.py).

    python tools/art/import_nilah_fx.py [--review DIR]

The overview holds 28 effect cells (some a 2x2 of frames, some one picture) and 9 cells of the pictures for her frames.
Each picture is read where it is drawn (brighter than the cells' black and their grid), made left-right symmetric at
the overview's own size (one half mirrored: the client never mirrors an effect picture), brought to game pixels (a
pixel drawn where enough of the squares under it are, its colour their mean snapped to her water and joy ramps), and
the frames of each effect are Codex's pictures in turn, with the build-up and fade made from them (smaller, darker,
broken into droplets). Its fixes: the one-sided pictures (q_hit's comet, eq_hit's diagonal, a_hit's curl, r_pull's ray)
left out or halved; the figures in r_pull's ring and the wake left out; the veils' horizontal bands turned upright
and kept at her sides, flowing up; the ribbons, flames and rings opened round the unit's body. Spots and times as
tools/art/fx_nilah.py (whose own drawings this replaces).
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import fx_nilah as F  # noqa: E402
from design_varus import srgb2lab  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "nilah", "codex_fx", "overview.jpg")
MOD = os.path.join(ROOT, "league")
W, JOY = F.WATER, F.JOY
EXTRA = [(0x2F, 0x6F, 0xA8), (0x12, 0x3F, 0x73), (0x6E, 0xA8, 0xD8)]    # the rings' deep blues
PAL = np.array(W + list(JOY.values()) + EXTRA, float)
PAL_LAB = srgb2lab(PAL)
# one step darker (None: gone) - the fades
DIMMER = {W[0]: W[1], W[1]: W[2], W[2]: W[3], W[3]: W[4], W[4]: W[5], W[5]: None,
          JOY["white"]: JOY["blush"], JOY["blush"]: JOY["pink"], JOY["pink"]: JOY["lilac"], JOY["lilac"]: None,
          JOY["sky"]: W[3], JOY["mint"]: W[3], JOY["gold"]: JOY["pink"],
          EXTRA[0]: EXTRA[1], EXTRA[1]: None, EXTRA[2]: EXTRA[0]}
T = 70               # drawn: its brightest channel above this (the cells' black is under 10, their grid under 40)

# the cells (top-left in the overview, 287 x 267; the bake cells 287 x 160)
CELLS = [(206, 34), (506, 34), (806, 34), (1107, 34), (1406, 34), (1707, 34),
         (206, 360), (504, 358), (806, 359), (1106, 360), (1406, 360), (1706, 359),
         (204, 687), (505, 686), (806, 686), (1107, 686), (1403, 686), (1706, 686),
         (206, 1009), (506, 1008), (805, 1011), (1107, 1011), (1403, 1011), (1706, 1009),
         (227, 1338), (503, 1338), (802, 1338), (1126, 1338),
         (206, 1634), (506, 1634), (806, 1634), (1106, 1635), (1406, 1635), (1708, 1635),
         (206, 1801), (506, 1801), (806, 1803)]


def box(cell, part="all"):
    x, y = CELLS[cell]
    w, h = (287, 267) if y < 1600 else (287, 158)
    hx, hy = w // 2, h // 2
    return {"all": (x, y, x + w, y + h), "TL": (x, y, x + hx, y + hy), "TR": (x + hx, y, x + w, y + hy),
            "BL": (x, y + hy, x + hx, y + h), "BR": (x + hx, y + hy, x + w, y + h),
            "L": (x, y, x + hx, y + h), "R": (x + hx, y, x + w, y + h)}[part]


_IMG = None


def img():
    global _IMG
    if _IMG is None:
        _IMG = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
    return _IMG


def snap(rgb):
    lab = srgb2lab(np.asarray(rgb, float).reshape(-1, 3))
    d = ((lab[:, None] - PAL_LAB[None]) ** 2).sum(-1)
    return PAL[d.argmin(1)].reshape(np.asarray(rgb).shape).astype(np.uint8)


def piece(cell, part="all", rot=0, keep=None, thr=T):
    """(rgb, drawn mask) of a cell's part; rot quarter-turns; keep(rgb) -> bool mask of the squares to read; thr the
    brightness that counts as drawn (higher: a glow round a line left out)."""
    x0, y0, x1, y1 = box(cell, part)
    a = img()[y0:y1, x0:x1]
    m = a.max(2) > thr
    if keep is not None:
        m &= keep(a)
    # the cell's frame line and its labels' leftovers: nothing within 3 px of the box
    m[:3], m[-3:], m[:, :3], m[:, -3:] = False, False, False, False
    if rot:
        a, m = np.rot90(a, rot), np.rot90(m, rot)
    return a, m


def read(a, m, s, ax, ay, hw, top, bot, need=0.45, half="left"):
    """Game pixels x -hw..hw, rows top..bot (pixel rows from the anchor), s overview px a game px about (ax, ay); the
    half read ("left", "right") mirrored onto the other, or "both" (no mirror)."""
    H = bot - top + 1
    out = np.zeros((H, 2 * hw + 1, 4), np.uint8)
    xs = range(-hw, 1) if half == "left" else range(0, hw + 1) if half == "right" else range(-hw, hw + 1)
    for j in range(H):
        ya, yb = ay + (top + j - 0.5) * s, ay + (top + j + 0.5) * s
        r0, r1 = max(0, int(round(ya))), min(a.shape[0], int(round(yb)))
        if r1 <= r0:
            continue
        for i in xs:
            xa, xb = ax + (i - 0.5) * s, ax + (i + 0.5) * s
            c0, c1 = max(0, int(round(xa))), min(a.shape[1], int(round(xb)))
            if c1 <= c0:
                continue
            mm = m[r0:r1, c0:c1]
            if mm.mean() < need:
                continue
            col = a[r0:r1, c0:c1][mm].mean(0)
            # the brightest third keeps the white cores white
            px = a[r0:r1, c0:c1][mm]
            lum = px @ np.array([0.3, 0.59, 0.11])
            if (lum > 235).mean() > 0.34:
                col = px[lum > 235].mean(0)
            out[j, i + hw, :3] = snap(col)
            out[j, i + hw, 3] = 255
    if half == "left":
        out[:, hw + 1:] = out[:, :hw][:, ::-1]
    elif half == "right":
        out[:, :hw] = out[:, hw + 1:][:, ::-1]
    return out


def fit(cell, part="all", size=("w", 12), half="left", rot=0, keep=None, need=0.45, axis=None, squash=1.0, thr=T):
    """A picture at game size: size ("w" | "h", n) its width or height; its axis the drawn part's middle column (or
    axis, overview px in the part); squash < 1 flattens it (rows read squash times as tall). -> RGBA, odd width,
    anchored on its middle row."""
    a, m = piece(cell, part, rot, keep, thr)
    ys, xs = np.nonzero(m)
    ax = (xs.min() + xs.max() + 1) / 2.0 if axis is None else axis
    ay = (ys.min() + ys.max() + 1) / 2.0
    half_w = max(ax - xs.min(), xs.max() + 1 - ax)
    half_h = (ys.max() + 1 - ys.min()) / 2.0
    kind, n = size
    s = half_w / (n / 2.0) if kind == "w" else half_h / (n / 2.0) * squash
    sy = s / squash
    hw = int(math.ceil(half_w / s - 0.5))
    hh = int(math.ceil(half_h / sy - 0.5))
    a2 = a if squash == 1.0 else np.repeat(a, 1, 0)
    if squash != 1.0:        # rows: read with sy by resampling the rows first
        k = sy / s
        rows = np.clip((np.arange(int(a.shape[0] / k)) * k).astype(int), 0, a.shape[0] - 1)
        a2, m2 = a[rows], m[rows]
        ay2 = ay / k
        return read(a2, m2, s, ax, ay2, hw, -hh, hh, need, half)
    return read(a2, m, s, ax, ay, hw, -hh, hh, need, half)


# ---------------------------------------------------------------- frame tools
def dim(a, k=1):
    a = a.copy()
    for _ in range(k):
        for y, x in zip(*np.nonzero(a[..., 3])):
            nxt = DIMMER.get(tuple(int(v) for v in a[y, x, :3]))
            if nxt is None:
                a[y, x] = 0
            else:
                a[y, x, :3] = nxt
    return a


def drops(a, most=4):
    """Only the small pieces (droplets, glints) of a picture."""
    lab, n = ndimage.label(a[..., 3] > 0)
    out = np.zeros_like(a)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() <= most:
            out[m] = a[m]
    return out


def pad_to(a, hw, hh):
    """a centred on a (2 hw + 1) x (2 hh + 1) canvas."""
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    h, w = a.shape[:2]
    y0, x0 = hh - h // 2, hw - w // 2
    ys0, xs0 = max(0, -y0), max(0, -x0)
    sub = a[ys0:ys0 + min(h - ys0, out.shape[0] - max(0, y0)), xs0:xs0 + min(w - xs0, out.shape[1] - max(0, x0))]
    out[max(0, y0):max(0, y0) + sub.shape[0], max(0, x0):max(0, x0) + sub.shape[1]] = sub
    return out


def sides(a, gap):
    """A picture's left half moved out to leave 2 gap + 1 columns clear in the middle, mirrored to the right."""
    h, w = a.shape[:2]
    c = w // 2
    left = a[:, :c]
    cols = np.nonzero(left[..., 3].any(0))[0]
    if not len(cols):
        return a
    left = left[:, :cols.max() + 1]
    hw = gap + left.shape[1]
    out = np.zeros((h, 2 * hw + 1, 4), np.uint8)
    out[:, :left.shape[1]] = left
    out[:, hw + 1:] = out[:, :hw][:, ::-1]
    return out


def clear_middle(a, hw, rows=None):
    a = a.copy()
    c = a.shape[1] // 2
    r = slice(None) if rows is None else rows
    a[r, c - hw:c + hw + 1] = 0
    return a


def bottom(a):
    """Anchor on the bottom: rows moved so the picture's last drawn row is its last row (and its height odd)."""
    rows = np.nonzero(a[..., 3].any(1))[0]
    return a[:rows.max() + 1]


# ---------------------------------------------------------------- the effects
def effects():
    """{name: [frames]} (RGBA, odd width, symmetric) and the anchors: 'core' (middle row) or 'feet' (last row)."""
    e = {}
    star = lambda n: fit(8, "TL", ("w", n), "left")
    # a_hit: the star, the crown, the splash, its droplets (the curl is one-sided: left out)
    e["a_hit"] = [star(7), fit(0, "BL", ("w", 10)), fit(0, "BR", ("w", 12)), dim(drops(fit(0, "BR", ("w", 12)), 6))]
    # qa_hit: the spike, the spike with its glints, the burst, the burst's glints fading
    e["qa_hit"] = [fit(1, "L", ("h", 10)), fit(1, "R", ("h", 14)), fit(2, "all", ("h", 17)),
                   dim(drops(fit(2, "all", ("h", 17)), 8))]
    # q_hit: the star, the clean X, the big X (its comet's half left out), it breaking, the spray
    e["q_hit"] = [star(7), fit(5, "TL", ("w", 13)), fit(3, "all", ("w", 17), "left"),
                  dim(fit(4, "all", ("w", 17), "left")), dim(drops(fit(5, "BR", ("w", 15)), 6))]
    # eq_hit: a little star, the ring, the ring of droplets, the broken ring
    e["eq_hit"] = [star(5), fit(6, "TL", ("w", 11)), fit(6, "TR", ("w", 13)), dim(fit(6, "BL", ("w", 13)))]
    # e_hit: the star, the two columns of water, the second's splash
    col2 = fit(7, "R", ("h", 17))
    e["e_hit"] = [star(6), fit(7, "L", ("h", 17)), col2, dim(col2[col2.shape[0] // 2:])]
    # r_hit (quick): the four stars in turn
    e["r_hit"] = [fit(8, "TL", ("w", 8)), fit(8, "TR", ("w", 11)), fit(8, "BL", ("w", 11)), dim(fit(8, "BR", ("w", 11)))]
    # r_pull: the star, the burst, the starburst, the orb splash, its droplets
    e["r_pull"] = [fit(9, "TL", ("w", 10)), fit(9, "TR", ("w", 14)), fit(9, "BL", ("w", 16)), fit(9, "BR", ("w", 18)),
                   dim(drops(fit(9, "BR", ("w", 18)), 8))]
    # w_ally (on the ally, the soles under it): the three ribbon pictures moved out round its body
    rib = [sides(fit(c, "all", ("h", 24)), 8) for c in (10, 11, 15)]
    e["w_ally"] = [dim(drops(rib[0], 6), 0), rib[0], rib[1], rib[2], dim(rib[2], 2)]
    # r_heal: the flames rising, taller, the arch (the shield), fading
    fl1 = sides(fit(12, "all", ("h", 16)), 8)
    fl2 = sides(fit(12, "all", ("h", 24)), 9)
    fl3 = sides(fit(16, "all", ("h", 26)), 9)
    arch = fit(17, "all", ("h", 45), squash=1.35)      # stretched up: its top over the unit's head
    e["r_heal"] = [fl1, fl2, fl3, arch, dim(arch, 2)]
    # eq_spin round her waist: the ring opening, full, brightest, breaking, droplets
    ring = lambda n: fit(18, "all", ("w", n))
    e["eq_spin"] = [dim(ring(41)), ring(53), ring(57), dim(ring(57), 2), dim(drops(dim(ring(57)), 5))]
    # r_spin: the storm growing, its three pictures in turn, tightening for the burst
    st = lambda c, n: fit(c, "all", ("w", n))
    e["r_spin"] = [st(19, 41), st(19, 61), st(19, 77), st(20, 77), st(21, 77), st(19, 77), st(20, 77), st(21, 67)]
    # r_burst: the round rings seen flat (squash 0.45)
    bu = lambda c, n: fit(c, "all", ("w", n), squash=0.45)
    e["r_burst"] = [bu(22, 37), bu(22, 57), bu(23, 81), dim(bu(23, 81), 2), dim(drops(dim(bu(23, 81)), 6))]
    # q_on: the ring round her, its light running round it (a band of it a step darker in turn)
    qr = clear_middle(fit(24, "all", ("h", 33), need=0.3, thr=140), 6, slice(0, 17))
    e["q_on"] = [turn(qr, k, 4) for k in range(4)]
    # the veils: Codex's three upright ribbon pictures (its veil cells drew level bands, a carpet across the unit, not
    # round it) at the unit's sides, taking turns, the second round each a little higher (flowing up)
    e["w_on"] = ribbons(45, 9)
    e["w_ally_veil"] = ribbons(41, 8)
    return e


def turn(a, k, n):
    """The ring with the band of angles k / n (from straight up, mirrored) a step darker."""
    out = a.copy()
    h, w = a.shape[:2]
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    for y, x in zip(*np.nonzero(a[..., 3])):
        t = math.atan2(abs(x - cx), -(y - cy)) / math.pi        # 0 top .. 1 bottom
        if int(t * n) % n == k:
            nxt = DIMMER.get(tuple(int(v) for v in a[y, x, :3]))
            out[y, x] = 0 if nxt is None else (*nxt, 255)
    return out


def ribbons(H, gap):
    """Six frames: the ribbon cells 10, 11, 15 at H rows round a clear middle 2 gap + 1 wide, then again raised 2."""
    pics = [sides(fit(c, "all", ("h", H)), gap) for c in (10, 11, 15)]
    hw = max(p.shape[1] for p in pics) // 2
    hh = max(p.shape[0] for p in pics) // 2 + 1
    pics = [pad_to(p, hw, hh) for p in pics]
    return pics + [np.roll(p, -2, axis=0) * (np.arange(p.shape[0]) < p.shape[0] - 2)[:, None, None].astype(np.uint8)
                   for p in pics]


def threads(tex):
    """Each band of colour (upright after the turn) brought to its middle line: per row, each run of one colour keeps
    its middle square (two for a run of six or more) - thin ribbons, the sparkles kept."""
    out = np.zeros_like(tex)
    for y in range(tex.shape[0]):
        row = tex[y]
        x = 0
        while x < row.shape[0]:
            if not row[x, 3]:
                x += 1
                continue
            x1 = x
            while x1 + 1 < row.shape[0] and row[x1 + 1, 3] and (row[x1 + 1, :3] == row[x, :3]).all():
                x1 += 1
            mid = (x + x1) // 2
            out[y, mid] = row[mid]
            if x1 - x + 1 >= 6:
                out[y, mid + 1] = row[mid + 1]
            x = x1 + 1
    return out


def veil(cell, H, gap, strip):
    """Six frames: the cell's bands turned upright, H rows; a strip `strip` wide at each side past `gap` columns."""
    a, m = piece(cell, "all", rot=1)
    ys, xs = np.nonzero(m)
    a, m = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = a.shape[0] / H
    tex = read(a, m, s, a.shape[1] / 2.0, a.shape[0] / 2.0, int(a.shape[1] / s / 2), -(H // 2), H // 2, 0.45,
               "both")
    tex = threads(tex)
    out = []
    for k in range(6):
        t = np.roll(tex, -k * H // 6, axis=0)
        hw = gap + strip
        f = np.zeros((t.shape[0], 2 * hw + 1, 4), np.uint8)
        f[:, :strip] = t[:, 1:1 + strip]
        f[:, hw + 1:] = f[:, :hw][:, ::-1]
        f[:2] = 0                                    # the rolled texture's seam row kept off the top
        out.append(f)
    return out


# ---------------------------------------------------------------- her frames' pictures
def water_only(a):
    """The wake's squares without her figure (skin, gold, purple, hair): cyan-blue or white."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((g >= r + 25) & (b >= r + 25)) | ((r > 200) & (g > 200) & (b > 200))


def bake_piece(cell, rows, length, need=0.25, keep=None, cols=None):
    """A frame picture at her dense squares (PPU 2.5), length squares long: (RGBA, its drawn bounds)."""
    x0, y0, x1, y1 = box(cell)
    a = img()[y0 + rows[0]:y0 + rows[1], x0 + (cols[0] if cols else 0):x0 + (cols[1] if cols else 287)]
    m = a.max(2) > T
    if keep is not None:
        m &= keep(a)
    m = ndimage.binary_opening(m, np.ones((2, 2)))
    ys, xs = np.nonzero(m)
    a, m = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1], m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = a.shape[1] / length
    H, Wd = int(math.ceil(a.shape[0] / s)), int(math.ceil(a.shape[1] / s))
    out = np.zeros((H, Wd, 4), np.uint8)
    for j in range(H):
        for i in range(Wd):
            r0, r1 = int(j * s), max(int(j * s) + 1, int((j + 1) * s))
            c0, c1 = int(i * s), max(int(i * s) + 1, int((i + 1) * s))
            mm = m[r0:r1, c0:c1]
            if not mm.size or mm.mean() < need:
                continue
            px = a[r0:r1, c0:c1][mm]
            lum = px @ np.array([0.3, 0.59, 0.11])
            col = px[lum > 235].mean(0) if (lum > 235).mean() > 0.34 else px.mean(0)
            out[j, i, :3] = snap(col)
            out[j, i, 3] = 255
    return out


def thicken(pic, n=1):
    """A thin line made n squares thicker above and below, the new squares a step darker than the ones they grow
    from (Codex's whips are a square thick at her size: under half a game pixel)."""
    out = pic.copy()
    for _ in range(n):
        op = out[..., 3] > 0
        grown = out.copy()
        for dy in (1, -1):
            src = np.roll(out, dy, axis=0)
            m = ~op & (src[..., 3] > 0) & ~(grown[..., 3] > 0)
            for y, x in zip(*np.nonzero(m)):
                c = DIMMER.get(tuple(int(v) for v in src[y, x, :3]))
                if c is not None:
                    grown[y, x] = (*c, 255)
        out = grown
    return out


def specks_off(pic, most=2):
    lab, n = ndimage.label(pic[..., 3] > 0)
    out = pic.copy()
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() <= most:
            out[m] = 0
    return out


def put(can, pic, x, y, ax, ay):
    """pic on the canvas with its square (ax, ay) on (x, y)."""
    h, w = pic.shape[:2]
    for j in range(h):
        for i in range(w):
            if pic[j, i, 3]:
                X, Y = x + i - ax, y + j - ay
                if 0 <= X < can.shape[1] and 0 <= Y < can.shape[0]:
                    can[Y, X] = pic[j, i]


def end_row(pic, left=True):
    """The middle row of the picture's drawn squares at its left (or right) end."""
    lab, n = ndimage.label(pic[..., 3] > 0, np.ones((3, 3)))
    sizes = ndimage.sum(np.ones(lab.shape), lab, range(1, n + 1))
    op = lab == (int(np.argmax(sizes)) + 1)                 # the whip itself, not a droplet off it
    cols = np.nonzero(op.any(0))[0]
    c = cols.min() if left else cols.max()
    rows = np.nonzero(op[:, c:c + 3].any(1) if left else op[:, max(0, c - 2):c + 1].any(1))[0]
    return c, int(round(rows.mean()))


def bakes():
    """{(tag, frame): (over, under)} on her frames' canvas (F.BAKE_W x F.BAKE_H)."""
    out = {}
    new = lambda: np.zeros((F.BAKE_H, F.BAKE_W, 4), np.uint8)
    for (tag, k), cell, length, tip, th in ((("attack", 3), 28, 30, (166, 78), 1), (("attack", 4), 29, 36, (168, 74), 1),
                                            (("attack_q", 3), 30, 40, (169, 65), 1),
                                            (("attack_q", 4), 31, 46, (164, 69), 0),
                                            (("skill", 4), 32, 52, (191, 70), 1), (("skill", 5), 33, 50, (191, 70), 0)):
        pic = specks_off(thicken(bake_piece(cell, (54, 134), length, keep=water_only), th), 3)
        c, r = end_row(pic)
        can = new()
        put(can, pic, tip[0] + 1, tip[1], c, r)
        out[(tag, k)] = (can, None)
    # the wake from her waist leftward, under her (the figure Codex drew at its right end left out)
    for k, cell, waist, length in ((1, 34, (95, 108), 64), (2, 35, (106, 107), 84), (3, 36, (117, 106), 88)):
        pic = specks_off(bake_piece(cell, (28, 140), length, keep=water_only, cols=(0, 205)), 3)
        c, r = end_row(pic, left=False)
        can = new()
        put(can, pic, waist[0], waist[1], c, r)
        out[("skill2", k)] = (None, can)
    return out


# ---------------------------------------------------------------- the sheets
FEET_FX = {"w_ally", "r_heal", "w_on", "w_ally_veil"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every effect at 6x here")
    a = ap.parse_args()
    e = effects()
    bad = []
    for name, frames in e.items():
        for k, f in enumerate(frames):
            if not (f == f[:, ::-1]).all():
                bad.append(f"{name} {k + 1} not symmetric")
            if not f[..., 3].any():
                bad.append(f"{name} {k + 1} empty")
    if bad:
        sys.exit("\n".join(bad))
    tables = {"league_nilah_fx": {}, "league_nilah_big": {}}
    for name, (_, spot, ms, big, tag) in F.FX.items():
        out = []
        for f, t in zip(e[name], ms):
            if name in FEET_FX:
                f = bottom(f)
                h, w = f.shape[:2]
                fr = G.centre_frame(f, -(w // 2), 10 - (h - 1))       # its last row on the row over the soles
            elif name == "q_on":
                h, w = f.shape[:2]
                fr = G.centre_frame(f, -(w // 2), -9 - h // 2)
            elif name in ("eq_spin", "r_spin", "r_burst"):
                f = clear_middle(f, 6, slice(0, f.shape[0] // 2))
                h, w = f.shape[:2]
                fr = G.centre_frame(f, -(w // 2), spot[1] - h // 2)
            else:
                h, w = f.shape[:2]
                fr = G.centre_frame(f, -(w // 2), spot[1] - h // 2)
            out.append((fr, float(t)))
        tables["league_nilah_big" if big else "league_nilah_fx"][tag] = out
    for sheet, tags in tables.items():
        w, h = G.write_sheet(os.path.join(MOD, "effects", sheet), tags, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(
            f"{t} {len(v)}f {sum(m for _, m in v):.0f}ms" for t, v in tags.items()))
    os.makedirs(F.BAKE_DIR, exist_ok=True)
    for old in os.listdir(F.BAKE_DIR):
        if old.endswith(".png"):
            os.remove(os.path.join(F.BAKE_DIR, old))
    for (tag, k), (over, under) in bakes().items():
        for arr, suf in ((over, ""), (under, "_under")):
            if arr is not None:
                Image.fromarray(arr).save(os.path.join(F.BAKE_DIR, f"{tag}_{k}{suf}.png"))
    print("baked", F.BAKE_DIR)
    if a.review:
        F.review(a.review, tables)


if __name__ == "__main__":
    main()
