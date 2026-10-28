#!/usr/bin/env python3
"""Scar's Codex poses (assets/source/scar/codex_poses: POSE_PROMPTS.md, 22 key poses of his own TFT clips on his
design, 2026-10-28) as game pictures: cropped, the design's head where Codex did not put it, gaps closed.

    python tools/art/design_scar_poses.py --sheet DIR      # all poses beside the design (4x)
    python tools/art/design_scar_poses.py                  # writes assets/source/scar/hd/pose_<name>.png (+ .json)

Codex delivered every pose twice: 1254 px canvases on exact 12 px squares and pixel_1x/ (105 x 105, one pixel a
square, on the pose pack's own grid from the canvas corner), all in the design's 36 colours, and it pasted the design's
head (approved-head-1x.png = the pack's 1_head.png, 27 x 29) square for square into the 20 poses that stand. So each
pose is read from pixel_1x as it is; its json keeps where the figure's top-left square is on that grid (grid_at: Codex
drew each pose where its reference put it, so rig_scar places them by it) and where the head box went (manifest.json).
The two falls kept a head Codex drew itself, about 16 squares and the sockets smeared (8x, 2026-10-28): d_fall gets
the design's head upright, centred where Codex's was; d_down (on his back, the head at the image left) the design's
head turned a quarter left so the mask looks up and the neck meets the body, its right edge on the shoulder. Codex's
own head squares round a pasted head that it does not cover are cleared where they are head-only colours; loose specks
dropped, small holes closed (design_silco_poses.close_gaps).

The walk is read from Codex's raw drafts instead (raw/scar-pose-run<k>-generated.png): to hold the head on one column
with the soles fixed Codex resampled the body's rows in pixel_1x, so the waist sat 36 to 40 rows under the head and 3 to
7 squares across from frame to frame (the user, 2026-10-28: 「走路的时候身体和头不协调 导致身体看起来变形」). Each
raw frame is read whole at one scale (the drafts were drawn 7.5 to 10.5 px a square, so the scale is the frame's own):
its jaw (the bottom of its skull, the largest bone-coloured blob in the top part) to its soles = WALK_JAW rows plus the
TFT walk's bob (WALK_NECK: his model's neck over the soles, pack_scar_poses' skeletons, less their mean); every square
the commonest design colour in its block's middle; the design's head on it, its skull's middle on the raw skull's middle
and its jaw on the raw jaw.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_scar_hd import lp  # noqa: E402
from design_silco_poses import close_gaps  # noqa: E402
import pack_scar_poses as PK  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "scar", "codex_poses", "scar-poses")
OUT = os.path.join(ROOT, "assets", "source", "scar", "hd")
NAMES = list(PK.POSES)
# the falls: where the design's head goes (its box's middle, on pixel_1x's grid) and how it is turned
TURN = {"d_down": 1}             # quarter turns left (np.rot90): the top of the head to the image left, the mask up
# the falls read from Codex's raw drafts too (the user, 2026-10-28: 「死亡时候身体这么长？」): it drew them with a
# grown man's build (the body ten of its skulls long lying down, the walk's five) and pixel_1x kept it, his legs 1.45
# times the walk's. Read again: d_fall at 16 raw px a square (his legs the walk's 34 squares, the boots its size);
# d_down at 18.6 across (his jaw at x 235 to his soles at 1220 = the walk's WALK_JAW 53 squares) and 12.5 down (as
# pixel_1x read it: as thick as he was). The design's head on the raw skull nearest `skull` (raw px), its skull's middle
# on that skull's middle, turned TURN.
DEATH = {"d_fall": dict(b=16.0, by=16.0, skull=(380, 560), spear=True),
         "d_down": dict(b=18.6, by=12.5, skull=(196, 980), spear=False)}
SPEAR_LEN = 76                   # squares: the walk's spear (upright_spear), so the one flying in d_fall is as long
SPECK = 6                        # parts apart from the figure smaller than this are dropped
WALK_SPECK = 20                  # the walk's: bits of the drafts' own spear left beside it
WALK = [f"run{k}" for k in range(1, 9)]
WALK_JAW = 53                    # rows from the jaw to the soles: pixel_1x's walk on average (its head at 21-23 + 22, soles 97)
# his TFT walk (pack_scar_poses' skeletons, 12 px squares): the neck's height over the soles
WALK_NECK = {"run1": 57.4, "run2": 55.6, "run3": 58.3, "run4": 57.3, "run5": 57.7, "run6": 55.5, "run7": 58.6,
             "run8": 57.6}
SKULL = (10, 9, 23, 22)          # the design head's skull (bone squares) in approved-head-1x.png: x0, y0, x1, y1
# his spear in the walk: upright in his fist, the same spear every frame (the user, 2026-10-28: 「走路时武器别歪啊」 -
# the drafts lean it -11 to +8 degrees and it ran 72 to 78 squares): SPEAR_FROM's (the cleanest point) turned upright
SPEAR_FROM = "run2"
INK = (6, 1, 14)                 # the design's outline
NECK_ROW = 17                    # approved-head-1x.png's rows from here down: the ear's tip over, then his shoulder
SKULL_COLOURS = ((252, 248, 229), (207, 202, 176), (197, 179, 177), (175, 175, 147), (125, 125, 107), (149, 138, 157))
VIOLET = ((70, 5, 136), (110, 4, 191))      # the shaft's and the point's violets: nothing else of his wears them
BANDAGE = ((252, 248, 229), (207, 202, 176), (175, 175, 147), (197, 179, 177), (125, 125, 107), (149, 138, 157))
# his own colours where the spear runs (the bandaged arm, the cloth, the ear, the hair); not the skin's purples: his
# purple arm is the far one, never by the spear, and the drafts' spear edges read as them
BODY = BANDAGE + ((229, 20, 157), (186, 10, 130), (207, 25, 37), (247, 53, 60), (127, 17, 36), (38, 17, 200),
                  (51, 33, 250), (44, 24, 161))
SPEAR_RAW = dict(shaft=16, point=60, point_len=180, tip=40, butt=160, butt_w=36, butt_len=70)   # raw px: half widths, the ends
SPEAR_HALF = 5                   # squares each side of the shaft's column the upright spear is read on
SPEAR_TOP = 24                   # rows from its butt down to his jaw: the drafts' median (18 to 28), so it rides his bob
SPEAR_GRIP = 30                  # rows over the soles where it is in his fist: its column is the draft's line there


def design(name="idle.png"):
    return np.asarray(Image.open(lp(os.path.join(OUT, name))).convert("RGBA"))


def head():
    return np.asarray(Image.open(lp(os.path.join(SRC, "approved-head-1x.png"))).convert("RGBA")).copy()


def head_colours(d, h):
    """The colours only the head uses: not shared with the body, the spear or the outline."""
    x0, y0, x1, y1 = PK.HEAD_BOX
    rest = d.copy()
    rest[y0:y1, x0:x1][h[..., 3] > 0] = 0
    return {tuple(c) for c in h[h[..., 3] > 0][:, :3]} - {tuple(c) for c in rest[rest[..., 3] > 0][:, :3]}


def manifest():
    with open(lp(os.path.join(SRC, "manifest.json")), encoding="utf-8") as f:
        return {p["file"][len("scar-pose-"):-4]: p for p in json.load(f)["poses"]}


def palette(d):
    return np.unique(d[d[..., 3] > 0][:, :3], axis=0).astype(int)


def raw_walk(name, pal):
    """A raw walk draft -> (RGBA ints, each pixel's nearest design colour (-1 clear))."""
    a = np.asarray(Image.open(lp(os.path.join(SRC, "raw", f"scar-pose-{name}-generated.png"))).convert("RGBA")).astype(int)
    op = a[..., 3] >= 128
    lab = np.full(op.shape, -1)
    lab[op] = np.argmin(((a[op][:, None, :3] - pal[None]) ** 2).sum(-1), 1)
    return a, lab


def of(pal, colours):
    return [i for i, c in enumerate(pal) if tuple(c) in colours]


def spear_of(lab, pal):
    """The spear in a raw draft -> (m, c: its shaft's line x = m y + c, fitted to the violet pixels by RANSAC; the
    pixels that are spear: along the line, not his body's own colours)."""
    ys, xs = np.nonzero(np.isin(lab, of(pal, VIOLET)))
    rng = np.random.default_rng(0)
    best = (0, 0.0, 0.0)
    for _ in range(3000):
        j, k = rng.choice(len(ys), 2, replace=False)
        if abs(ys[j] - ys[k]) < 200:
            continue
        m = (xs[k] - xs[j]) / (ys[k] - ys[j])
        c = xs[j] - m * ys[j]
        n = int((np.abs(xs - (m * ys + c)) < 6).sum())
        if n > best[0]:
            best = (n, m, c)
    inl = np.abs(xs - (best[1] * ys + best[2])) < 6
    m, c = np.polyfit(ys[inl], xs[inl], 1)
    y0, y1 = ys[inl].min(), ys[inl].max()
    Y, X = np.mgrid[0:lab.shape[0], 0:lab.shape[1]]
    dist = np.abs(X - (m * Y + c)) / np.hypot(1, m)
    w = np.where(Y <= y0 + SPEAR_RAW["butt_len"], SPEAR_RAW["butt_w"],
                 np.where(Y >= y1 - SPEAR_RAW["point_len"], SPEAR_RAW["point"], SPEAR_RAW["shaft"]))
    spear = ((Y >= y0 - SPEAR_RAW["butt"]) & (Y <= y1 + SPEAR_RAW["tip"]) & (dist <= w) & (lab >= 0) &
             ~np.isin(lab, of(pal, BODY)))
    return m, c, spear


def erase(a, lab, spear):
    """The spear taken off a raw draft: where it crossed his body (drawn on both sides of it within 40 px in its row)
    the nearest body colour to the right, else clear."""
    lab = lab.copy()
    keep = (lab >= 0) & ~spear
    for y in np.nonzero(spear.any(1))[0]:
        k = np.nonzero(keep[y])[0]
        for x in np.nonzero(spear[y])[0]:
            r = k[(k > x) & (k <= x + 40)]
            lab[y, x] = lab[y, r[0]] if len(r) and len(k[(k < x) & (k >= x - 40)]) else -1
    return lab


def squares(lab, pal, b, top, bottom, mid, left, right, by=None):
    """lab on squares of b raw px (by px high, b unless given): the rows up from `bottom`, the column `left` centred on
    x = mid, `right` columns after it; every square the commonest design colour in its block's middle, drawn where most
    of that middle is."""
    by = by or b
    H = int(np.ceil((bottom - top) / by)) + 1
    W = left + right
    out = np.zeros((H, W, 4), np.uint8)
    for r in range(H):
        y1 = bottom - (H - 1 - r) * by
        y0 = int(round(y1 - by * 0.8))
        y1 = int(round(y1 - by * 0.2))
        for c in range(W):
            x0 = mid + (c - left - 0.5) * b
            win = lab[max(0, y0):max(0, y1), max(0, int(round(x0 + b * 0.2))):max(0, int(round(x0 + b * 0.8)))].ravel()
            if len(win) and (win >= 0).sum() * 2 > len(win):
                out[r, c, :3] = pal[np.bincount(win[win >= 0]).argmax()]
                out[r, c, 3] = 255
    return out


def scale_of(name, lab, pal):
    """A raw draft's scale -> (raw px a square, its skull's middle x, its jaw y, its soles y)."""
    bone = [i for i, c in enumerate(pal) if c.min() > 150 and c.max() - c.min() < 70]
    ys, xs = np.nonzero(lab >= 0)
    m = np.isin(lab, bone)
    m[int(ys.min() + 0.45 * (ys.max() - ys.min())):] = False      # the skull, not the bandaged arm
    lb, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    sky, skx = np.nonzero(lb == np.argmax(ndimage.sum(m, lb, range(1, n + 1))) + 1)
    jaw, mid, sole = sky.max(), (skx.min() + skx.max()) / 2, ys.max()
    rows = WALK_JAW + WALK_NECK[name] - np.mean(list(WALK_NECK.values()))
    return (sole + 1 - jaw) / rows, mid, jaw, sole


def upright_spear(d):
    """SPEAR_FROM's spear turned upright (sheared about its grip, the rows kept) on its own squares, the shaft its hand
    hid drawn like the nearest whole shaft row -> squares, the shaft on column SPEAR_HALF."""
    pal = palette(d)
    _, lab = raw_walk(SPEAR_FROM, pal)
    m, c, spear = spear_of(lab, pal)
    b, _, _, sole = scale_of(SPEAR_FROM, lab, pal)
    gy = sole - SPEAR_GRIP * b
    gx = m * gy + c
    Y, X = np.mgrid[0:lab.shape[0], 0:lab.shape[1]]
    sx = np.clip(np.round(X + m * (Y - gy)).astype(int), 0, lab.shape[1] - 1)   # upright: the line is x = gx
    up = np.where(spear, lab, -1)[Y, sx]
    ys, _ = np.nonzero(up >= 0)
    t = squares(up, pal, b, ys.min(), ys.max() + 1, gx, SPEAR_HALF, SPEAR_HALF + 1)
    rows = np.nonzero(t[..., 3].any(1))[0]
    whole = [r for r in rows if t[r, SPEAR_HALF, 3] and (t[r, :, 3] > 0).sum() <= 3]
    for r in range(rows[0], rows[-1] + 1):
        if not t[r, SPEAR_HALF, 3]:
            t[r] = t[min(whole, key=lambda w: abs(r - w))]
    return t[rows[0]:rows[-1] + 1]


def walk_frame(name, d, spear):
    """A walk frame read from its raw draft at one scale, its own spear taken off and `spear` (upright_spear) put back
    upright: on the draft's line where his fist is (SPEAR_GRIP), its butt SPEAR_TOP rows over his jaw; his bandage stays
    over the shaft -> (squares, where the design head's top-left goes)."""
    pal = palette(d)
    _, lab = raw_walk(name, pal)
    b, mid, jaw, sole = scale_of(name, lab, pal)
    m, c, sp = spear_of(lab, pal)
    gx = m * (sole - SPEAR_GRIP * b) + c
    lab = erase(None, lab, sp)
    ys, xs = np.nonzero(lab >= 0)
    top = min(ys.min(), jaw - (SPEAR_TOP + 2) * b)
    left = int(np.ceil((mid - min(xs.min(), gx - (SPEAR_HALF + 2) * b)) / b)) + 1   # the skull's middle square
    right = int(np.ceil((max(xs.max(), gx + (SPEAR_HALF + 3) * b) - mid) / b)) + 1
    out = squares(lab, pal, b, top, sole + 1, mid, left, right)
    H = out.shape[0]
    jaw_row = H - 1 - int(round((sole + 1 - jaw) / b))
    x0, y0 = left + int(np.floor((gx - mid) / b + 0.5)) - SPEAR_HALF, jaw_row - SPEAR_TOP
    bandage = {tuple(pal[i]) for i in of(pal, BANDAGE)}
    put = np.zeros(out.shape[:2], bool)
    for (r, c), v in np.ndenumerate(spear[..., 3]):
        y, x = r + y0, c + x0
        if v and 0 <= y < H and 0 <= x < out.shape[1]:
            put[y, x] = True
            if not (out[y, x, 3] and tuple(out[y, x, :3]) in bandage):
                out[y, x] = spear[r, c]
    # the drafts' spear outline left loose by the shaft: ink on his edge with nothing of his to outline (only clear, ink
    # or the spear round it), in the spear's columns and two either side
    band = np.zeros_like(put)
    band[:, max(0, x0 - 2):x0 + spear.shape[1] + 2] = True
    while True:
        dark = (out[..., 3] > 0) & np.all(out[..., :3] == INK, -1) & ~put & band
        colour = np.pad((out[..., 3] > 0) & ~np.all(out[..., :3] == INK, -1) & ~put, 1)
        clear = np.pad(out[..., 3] == 0, 1, constant_values=True)
        near, edge = np.zeros_like(dark), np.zeros_like(dark)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                near |= colour[1 + dy:1 + dy + H, 1 + dx:1 + dx + out.shape[1]]
                edge |= clear[1 + dy:1 + dy + H, 1 + dx:1 + dx + out.shape[1]]
        loose = dark & edge & ~near
        if not loose.any():
            break
        out[loose] = 0
    # over his jaw, left of the shaft there is only the spear (his shoulder and head are right of it)
    side = np.zeros_like(put)
    side[:jaw_row, :max(0, x0 + SPEAR_HALF - 1)] = True
    out[side & ~put] = 0
    return out, (int(round(left - (SKULL[0] + SKULL[2]) / 2)), jaw_row - SKULL[3])


def death_frame(name, d):
    """A fall read from its raw draft (DEATH) -> (squares, the raw skull's middle square (column, row), the figure's
    middle column on the pack's grid as pixel_1x had it)."""
    pal = palette(d)
    _, lab = raw_walk(name, pal)
    k = DEATH[name]
    bone = [i for i, c in enumerate(pal) if c.min() > 150 and c.max() - c.min() < 70]
    m = np.isin(lab, bone)
    lb, n = ndimage.label(m, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(m, lb, range(1, n + 1))
    blobs = [j + 1 for j in range(n) if sizes[j] > 800]
    j = min(blobs, key=lambda j: np.hypot(*(np.array(ndimage.center_of_mass(m, lb, j))[::-1] - k["skull"])))
    sy, sx = np.nonzero(lb == j)
    cx, cy = (sx.min() + sx.max()) / 2, (sy.min() + sy.max()) / 2
    flying = None
    if k["spear"]:                            # the spear flying free of him (the largest part not his): on its own
        parts, n = ndimage.label(lab >= 0, structure=np.ones((3, 3), bool))
        his = parts[int(cy), int(cx)]
        sizes = ndimage.sum(lab >= 0, parts, range(1, n + 1))
        sp = parts == max((j for j in range(1, n + 1) if j != his), key=lambda j: sizes[j - 1])
        flying = np.where(sp, lab, -1)
        lab = np.where(sp, -1, lab)
    ys, xs = np.nonzero(lab >= 0)
    left = int(np.ceil((cx - xs.min()) / k["b"])) + 1
    right = int(np.ceil((xs.max() - cx) / k["b"])) + 1
    out = squares(lab, pal, k["b"], ys.min(), ys.max() + 1, cx, left, right, k["by"])
    row = out.shape[0] - 1 - int((ys.max() + 1 - cy) / k["by"])
    if flying is not None:                    # its middle where the body's scale puts it, from the skull
        fy, fx = np.nonzero(flying >= 0)
        bs = np.hypot(fx.max() - fx.min(), fy.max() - fy.min()) / SPEAR_LEN
        mx, my = (fx.min() + fx.max()) / 2, (fy.min() + fy.max()) / 2
        t = squares(flying, pal, bs, fy.min(), fy.max() + 1, mx, int(np.ceil((mx - fx.min()) / bs)) + 1,
                    int(np.ceil((fx.max() - mx) / bs)) + 1)
        tc = int(np.ceil((mx - fx.min()) / bs)) + 1
        tr = t.shape[0] - 1 - int((fy.max() + 1 - my) / bs)
        at_x = left + int(round((mx - cx) / k["b"])) - tc
        at_y = row + int(round((my - cy) / k["by"])) - tr
        pad = max(0, -at_x, -at_y, at_x + t.shape[1] - out.shape[1], at_y + t.shape[0] - out.shape[0])
        out = np.pad(out, ((pad, pad), (pad, pad), (0, 0)))
        left, row, at_x, at_y = left + pad, row + pad, at_x + pad, at_y + pad
        reg = out[at_y:at_y + t.shape[0], at_x:at_x + t.shape[1]]
        on = (t[..., 3] > 0) & (reg[..., 3] == 0)
        reg[on] = t[on]
    old = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"scar-pose-{name}.png"))).convert("RGBA"))
    oxs = np.nonzero(old[..., 3].max(0) >= 128)[0]
    return out, (left, row), (oxs.min() + oxs.max()) / 2


def head_only(h):
    """The approved head without the design's own body round its jaw: from NECK_ROW down only the skull's colours and
    the ink by them (the box also took the design's shoulder pad, studs and collar, left of the jaw, which sat over the
    walk's own shoulder: 「这一部分连接处又看起来变形了」)."""
    h = h.copy()
    bone = np.isin(h[..., :3].reshape(-1, 3).view([("", h.dtype)] * 3).ravel(),
                   np.array(SKULL_COLOURS, h.dtype).view([("", h.dtype)] * 3).ravel()).reshape(h.shape[:2])
    bone &= h[..., 3] > 0
    ink = (h[..., 3] > 0) & np.all(h[..., :3] == INK, -1)
    by = ndimage.binary_dilation(bone, structure=np.ones((3, 3), bool))
    low = np.zeros(h.shape[:2], bool)
    low[NECK_ROW:] = True
    h[low & ~bone & ~(ink & by)] = 0
    return h


def read(name, d, h, only, spear=None):
    """The pose -> (figure, the head box's top-left in it, the figure's top-left square on the pack's grid)."""
    if name in WALK:
        a, head_box = walk_frame(name, d, spear)
    elif name in DEATH:
        a, skull_at, mid = death_frame(name, d)
    else:
        a = np.asarray(Image.open(lp(os.path.join(SRC, "pixel_1x", f"scar-pose-{name}.png"))).convert("RGBA")).copy()
        a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    pad = 20
    big = np.pad(a, ((pad, pad), (pad, pad), (0, 0)))
    if name in WALK:                                              # the design head where the raw head was
        h = head_only(h)
        hy, hx = np.nonzero(h[..., 3] > 0)
        py, px = hy + head_box[1] + pad, hx + head_box[0] + pad
        pasted = np.zeros(big.shape[:2], bool)
        pasted[py, px] = True
        for y in range(py.min() - 4, py.max() + 5):
            for x in range(px.min() - 4, px.max() + 5):
                if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                    big[y, x] = 0
        big[py, px] = h[hy, hx]
        head_at = (head_box[0] + pad, head_box[1] + pad)
    elif name in DEATH:
        mark = np.zeros(h.shape[:2], bool)
        mark[(SKULL[1] + SKULL[3]) // 2, (SKULL[0] + SKULL[2]) // 2] = True
        hd = np.rot90(head_only(h), TURN.get(name, 0)).copy()
        my, mx = np.argwhere(np.rot90(mark, TURN.get(name, 0)))[0]
        hx0 = skull_at[0] - mx + pad
        hy0 = skull_at[1] - my + pad
        hy, hx = np.nonzero(hd[..., 3] > 0)
        py, px = hy + hy0, hx + hx0
        pasted = np.zeros(big.shape[:2], bool)
        pasted[py, px] = True
        for y in range(py.min() - 3, py.max() + 4):
            for x in range(px.min() - 3, px.max() + 4):
                if not pasted[y, x] and big[y, x, 3] and tuple(big[y, x, :3]) in only:
                    big[y, x] = 0
        big[py, px] = hd[hy, hx]
        head_at = (hx0, hy0)
    else:
        o = manifest()[name]["head"]["origin"]
        head_at = (o[0] + pad, o[1] + pad)
    big = close_gaps(big, d)
    op = big[..., 3] > 0
    lb, n = ndimage.label(op, structure=np.ones((3, 3), bool))
    sizes = ndimage.sum(op, lb, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < (WALK_SPECK if name in WALK else SPECK):
            big[lb == j] = 0
    ys, xs = np.nonzero(big[..., 3] > 0)
    oy, ox = ys.min(), xs.min()
    grid = (int(ox - pad), int(oy - pad))
    if name in DEATH:                         # across where pixel_1x had him: the figure's middle on its middle
        grid = (int(round(mid - (xs.max() - ox) / 2)), grid[1])
    return big[oy:ys.max() + 1, ox:xs.max() + 1], (int(head_at[0] - ox), int(head_at[1] - oy)), grid


def big4(a, z):
    im = Image.fromarray(np.repeat(np.repeat(a, z, 0), z, 1))
    bg = Image.new("RGBA", im.size, (200, 205, 195, 255))
    bg.alpha_composite(im)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--only", help="comma separated pose names")
    a = ap.parse_args()
    names = a.only.split(",") if a.only else NAMES
    d, h = design(), head()
    only = head_colours(d, h)
    spear = upright_spear(d)
    figs = {}
    for n in names:
        fig, at, grid = read(n, d, h, only, spear)
        figs[n] = (fig, at, grid)
        print(f"{n:9s} {fig.shape[1]} x {fig.shape[0]}, head box at {at}, on the grid at {grid}")
    if a.sheet:
        os.makedirs(lp(a.sheet), exist_ok=True)
        z = 4
        tiles = [("design", d)] + [(n, figs[n][0]) for n in names]
        rows = [tiles[i:i + 6] for i in range(0, len(tiles), 6)]
        for j, row in enumerate(rows):
            Hm = max(t.shape[0] for _, t in row)
            W = sum(t.shape[1] * z + 12 for _, t in row)
            sheet = Image.new("RGBA", (W, Hm * z + 24), (90, 96, 90, 255))
            dr = ImageDraw.Draw(sheet)
            x = 0
            for n, t in row:
                sheet.alpha_composite(big4(t, z), (x, 24 + (Hm - t.shape[0]) * z))
                dr.text((x + 4, 4), f"{n} {t.shape[1]}x{t.shape[0]}", fill=(255, 255, 0, 255))
                x += t.shape[1] * z + 12
            path = os.path.join(a.sheet, f"scar_poses_{j}.png")
            sheet.convert("RGB").save(lp(path))
            print(path)
        return
    os.makedirs(lp(OUT), exist_ok=True)
    for n, (fig, at, grid) in figs.items():
        Image.fromarray(fig).save(lp(os.path.join(OUT, f"pose_{n}.png")))
        with open(lp(os.path.join(OUT, f"pose_{n}.json")), "w", encoding="utf-8") as fh:
            json.dump({"head_at": [at[0], at[1]], "grid_at": [grid[0], grid[1]]}, fh)


if __name__ == "__main__":
    main()
