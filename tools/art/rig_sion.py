#!/usr/bin/env python3
"""league_sion's sheets from Codex's step-2 strips (assets/source/sion/codex_strips) and the PPU design (hd/front.png).

    python tools/art/rig_sion.py [--review DIR] [--frames-only]

Codex drew 36 action frames on the pack's 7-px grid (tools/art/pack_sion_strips.py: 219 x 146 squares, the standing
point column PIV_X, the soles' row SOLE; the design pasted at DESIGN_AT), in the design's 27 colours, and pasted the
design's head into every frame by translation (its HEAD_POLY). Here, for every frame:
  * the size: Codex's bodies came out 5-22 % bigger than the design's (the parts' areas: skin, trousers, loin cloth),
    while its closing frames are the design itself - the hero swelled on every cast and shrank back. Each action's
    frames are brought to the design's size by one factor (SCALE: 1 / the median of its frames' measures,
    body_scale()), as tools/art/design_sion.py brought the design down: whole rows and columns deleted, the ones most
    like their neighbours, evenly spread (design_riven.pick), the soles kept on SOLE and the standing column on PIV_X;
    the head is taken out first and pasted back the design's size on the shrunken neck (one face, one size);
  * the outline closed where the cut or the paste left it open (strips.complete_outline + close_all), loose specks
    cleared, pinholes filled (specks, pinholes);
  * W (skill2_w): Codex's frame 2 swung the axe overhead and drew the far gauntlet as a block - dropped; the flex is
    frames 1, 3, 3 (held), then the design;
  * idle = the design breathing (the upper body BREATH rows up over the legs), hit = the design moved 2 and 1 squares
    back, run = the design walking league_nautilus / league_braum's way (walk_frame; the user: 「你向前那样冲刺模型永远会变形」),
    ult (R's charge) = Codex's charge pose, its upper body bobbing over its planted legs (ULT_BOB).
The canvas is the game's density (PPU 1.52: the design's 67 squares crown to soles for 44 game px). Each frame is then
written twice (tools/art/rig_bard.py's way): the dense frame (the canvas itself round the pivot -> assets/source/ppu/
sion_<tag>.png + .json, ppu_hd.py's drawn strips) and the 1x frame (pixel_down.pixelate at 1 / PPU) for the sheet's
plain tags; `python tools/art/ppu_hd.py --hero sion` then adds the hd_ / lo_ tags.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import design_riven as R  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "sion")
CODEX = os.path.join(SRC, "codex_strips")
DESIGN = os.path.join(SRC, "hd", "front.png")
FRAMES = os.path.join(SRC, "frames")
STEM = os.path.join(ROOT, "league", "champions", "league_sion")
PPU_SRC = os.path.join(ROOT, "assets", "source", "ppu")
PPU = 1.52                      # canvas squares a game pixel (design_sion.HD_PPU)
FEET = 11                       # 1x rows from the pivot down to the soles (the pack's 128-canvas heroes)
# On the battlefield he is drawn at SIZE of the 1x size (addons/league_main/src/hd.rs SIZES; the user, 2026-10-14:
# 「模型太大了吧 和铁男差不多大就行了吧」 -> 80 % (Mordekaiser's body area on a true-scale sheet), then 「调成90%」 ->
# 90 %, 1.69 squares a game pixel): the DLL scales about the frame's centre, so every dense frame is drawn SHIFT rows
# lower - the soles, (FEET + 0.5) x PPU under the pivot, land there again (tools/art/rig_braum.py's way)
SIZE = 0.90
SHIFT = round((FEET + 0.5) * PPU * (1 / SIZE - 1))
COLS, ROWS = 219, 146
PIV_X, SOLE = 100, 140          # pack_sion_strips.py
DESIGN_AT = (43, 66)            # the design's top-left on the canvas (pack_sion_strips.py's print)
OUTLINE = (8, 7, 7)
# the head object Codex pasted by translation (its restore_strip_heads.py): stake, ribbon, bald head, jaw cage - in
# design coordinates (x, y)
HEAD_POLY = [(40, 0), (60, 0), (60, 8), (63, 10), (65, 14), (65, 20), (62, 24), (56, 24), (52, 21), (50, 19), (50, 14),
             (40, 14)]
NECK = (22, 57)                 # the design's jaw bottom (row, col): the head sits on the neck there
# the body parts whose areas measure a frame's size against the design's (the head is the design's in every frame)
SKIN = [(157, 158, 188), (125, 110, 151), (189, 202, 219), (209, 222, 235), (94, 69, 112)]
CLOTH = [(108, 97, 55)]
TROUSERS = [(117, 61, 32), (91, 47, 25), (71, 23, 37), (48, 18, 27), (78, 51, 42), (51, 31, 27)]
# Codex's frames per tag (its file numbers) in the order the tag plays them; "design" = the design itself (the
# closing frames Codex took from the design)
TAGS = {
    "attack": [1, 2, 3, 4, "design"],
    "skill_charge": [1, 2, 3, 4],
    "skill": [1, 2, 3, 4, "design"],
    "skill2": [1, 2, 3, 4, "design"],
    "skill2_w": [1, 3, 3, "design"],
    "ult_hit": [1, 2, 3, 4, "design"],
    "dead": [1, 2, 3, 4, 5, 5],
}
# frame times (ms): the pack's cells.json; skill2_w: frame 2 dropped, frame 3 shown in its place and held
MS = {
    "attack": [70, 80, 60, 90, 110], "skill_charge": [130, 170, 170, 200], "skill": [60, 60, 80, 100, 100],
    "skill2": [60, 70, 90, 90, 100], "skill2_w": [60, 90, 120, 120], "ult_hit": [60, 60, 80, 100, 120],
    "dead": [100, 120, 150, 150, 200, 400],
}
# frames still bigger than their neighbours after their tag's factor, by eye and measure (body_scale): Q's slam frame 1
# came out 13 % over the charge it follows (both arms up, shoulders wider) - shrunk again by this much
SCALE_FIX = {("skill", 1): 0.91}
BREATH = [0, 1, 2, 2, 1, 0]
IDLE_MS = 160
# the design's legs (rows, columns; ends exclusive): under the belt (WALK_BAND), clear of the axe blade at the near
# side and of the far hand hanging beside the far thigh
WALK_BAND = 52
WALK_NEAR = ((53, 62, 31, 50), (62, 75, 28, 50))
WALK_FAR = ((53, 63, 61, 81), (63, 75, 61, 87))
CLOTH_BOX = ((53, 75, 50, 61),)       # the loin cloth between them: it hangs from the belt, it does not breathe
# per frame: the near leg's (columns forward, rows lifted), the far leg's, the figure's rise (canvas squares:
# league_nautilus's 1x steps x PPU, as league_galio's)
WALK = [((0, 0), (0, 3), 2), ((0, 0), (2, 5), 3), ((0, 0), (2, 2), 2), ((0, 0), (2, 0), 0),
        ((0, 3), (0, 0), 2), ((2, 5), (0, 0), 3), ((2, 2), (0, 0), 2), ((2, 0), (0, 0), 0)]
WALK_MS = 115
CRACK = 3                       # bare squares a step opens, this many columns wide at most: a crack
SPECK = 8
PINHOLE = 6
# R's charge: Codex's charge pose (ult 1, brought to the design's size by its own measure) is a sprint stride, one foot
# off the ground - the user's rule for the big heroes: no sprint (「你向前那样冲刺模型永远会变形」). Its upper body charges on
# the design's own legs walking (walk_frame's steps): its legs (canvas rows from ULT_CUT[0], columns ULT_CUT[1]..[2]) go,
# the rest is moved ULT_SHIFT (rows, columns) so its belt's lower edge sits on the design's (WALK_BAND) over the legs'
# middle; the near arm with the axe and the far arm hanging beside the far leg stay as drawn.
ULT_CUT = (114, 76, 129)
ULT_SHIFT = (5, -8)
ULT_MS = 104                    # 8 steps over R's 50-tick charge


def load(p):
    return np.asarray(Image.open(p).convert("RGBA")).copy()


def design():
    return load(DESIGN)


def on_canvas(d, dx=0, dy=0):
    can = np.zeros((ROWS, COLS, 4), np.uint8)
    x0, y0 = DESIGN_AT
    can[y0 + dy:y0 + dy + d.shape[0], x0 + dx:x0 + dx + d.shape[1]] = d
    return can


def head_mask(own=False):
    """The head object's squares in the design (HEAD_POLY, opaque); own: without the shoulder's edge the polygon takes in
    left of the head (rows 13-14, columns before 50) - Codex pasted those design squares too, a grey stroke beside the
    head wherever the shoulder is lower than the design's."""
    d = design()
    m = Image.new("L", (d.shape[1], d.shape[0]))
    ImageDraw.Draw(m).polygon(HEAD_POLY, fill=255)
    m = (np.asarray(m) > 0) & (d[..., 3] > 0)
    if own:
        m[13:15, :50] = False
    return m


def find_head(a):
    """Codex's translation of the pasted head: (dy, dx) from the design's own place on the canvas, the most squares equal."""
    d, hm = design(), head_mask()
    ys, xs = np.nonzero(hm)
    want = d[ys, xs]
    x0, y0 = DESIGN_AT
    best = (-1, 0, 0)
    for dy in range(-40, 30):
        for dx in range(-40, 50):
            yy, xx = ys + y0 + dy, xs + x0 + dx
            if yy.min() < 0 or xx.min() < 0 or yy.max() >= ROWS or xx.max() >= COLS:
                continue
            n = int((a[yy, xx] == want).all(-1).sum())
            if n > best[0]:
                best = (n, dy, dx)
    assert best[0] >= 0.9 * len(ys), f"no pasted head found ({best[0]} of {len(ys)} squares)"
    return best[1], best[2]


def paste_head(a, dy, dx):
    d, hm = design(), head_mask(own=True)
    ys, xs = np.nonzero(hm)
    x0, y0 = DESIGN_AT
    a[ys + y0 + dy, xs + x0 + dx] = d[ys, xs]
    return a


def body_scale(a):
    """A frame's size against the design's: the square root of its skin, loin cloth and trousers' area over the
    design's (the head is the design's own everywhere)."""
    def area(x):
        n = 0
        for c in SKIN + CLOTH + TROUSERS:
            n += int(((x[..., 3] > 0) & (x[..., :3] == c).all(-1)).sum())
        return n
    return (area(a) / area(design())) ** 0.5


def keys(a):
    return np.where(a[..., 3] > 0, (a[..., 0].astype(np.int64) << 16) | (a[..., 1].astype(np.int64) << 8) | a[..., 2], -1)


def least(lines, n_out):
    """design_riven.pick at the offset that loses least: the n_out lines kept, the others the most like a neighbour."""
    if n_out >= len(lines):
        return list(range(len(lines)))
    best = None
    for off in range(3):
        k, lost = R.pick(lines, n_out, off)
        if k is not None and (best is None or lost < best[1]):
            best = (k, lost)
    return best[0]


def shrink(a, f):
    """The canvas `a` brought to f of its size by deleting whole rows and columns (the soles' row SOLE and the standing
    column PIV_X kept where they are). -> (canvas, row map, column map: old index -> new index of the nearest kept)."""
    k = keys(a)
    op = a[..., 3] > 0
    ys, xs = np.nonzero(op)
    top, left, right = ys.min(), xs.min(), xs.max()
    rows = list(range(top, SOLE))
    kr = least([k[y] for y in rows], round((SOLE + 1 - top) * f) - 1)
    kept_r = [rows[i] for i in kr] + [SOLE]
    lcols, rcols = list(range(left, PIV_X)), list(range(PIV_X + 1, right + 1))
    kl = least([k[:, x] for x in lcols], round(len(lcols) * f)) if lcols else []
    kr2 = least([k[:, x] for x in rcols], round(len(rcols) * f)) if rcols else []
    kept_l, kept_rc = [lcols[i] for i in kl], [rcols[i] for i in kr2]
    out = np.zeros_like(a)
    new_y = {y: SOLE - (len(kept_r) - 1 - i) for i, y in enumerate(kept_r)}
    new_x = {x: PIV_X - (len(kept_l) - i) for i, x in enumerate(kept_l)}
    new_x[PIV_X] = PIV_X
    new_x.update({x: PIV_X + 1 + i for i, x in enumerate(kept_rc)})
    yk, xk = np.array(sorted(new_y)), np.array(sorted(new_x))
    out[np.ix_([new_y[y] for y in yk], [new_x[x] for x in xk])] = a[np.ix_(yk, xk)]
    ymap = lambda y: new_y[yk[np.abs(yk - y).argmin()]]
    xmap = lambda x: new_x[xk[np.abs(xk - x).argmin()]]
    return out, ymap, xmap


def specks(a, most=SPECK):
    """Loose pieces apart from the figure, at most `most` squares, cleared."""
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lab, range(1, n + 1))
        for i, z in enumerate(sizes, 1):
            if z <= most:
                a[lab == i] = 0
    return a


RIBBON_EDGE = [(129, 0, 1), (156, 1, 5)]   # the ribbon's own dark red rim (the design draws it with no black line)


def close_all(a):
    """Every light square still touching the ground 4-wise gets an outline square there (nothing under SOLE); the
    ribbon's dark red rim is its edge already, as in the design (a black line round it in the actions only flickered)."""
    op = a[..., 3] > 0
    light = op & (a[..., :3].astype(int).sum(-1) >= 70)
    for c in RIBBON_EDGE:
        light &= ~(a[..., :3] == c).all(-1)
    out = a.copy()
    for y, x in zip(*np.nonzero(light)):
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy <= SOLE and 0 <= xx < COLS and not op[yy, xx]:
                out[yy, xx] = (*OUTLINE, 255)
    return out


def pinholes(a, most=PINHOLE):
    lab, n = ndimage.label(a[..., 3] == 0)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    for i in range(1, n + 1):
        if i not in border and (lab == i).sum() <= most:
            a[lab == i] = (*OUTLINE, 255)
    return a


ORPHAN_ROW = 110                # canvas rows from here down (under the belt): where moving legs meet the axe
CLOTH_COLS = (92, 105)          # canvas columns of the loin cloth: its tatters' 1-square tips are drawn so


def orphans(a):
    """Outline stubs that outline nothing: a dark square under ORPHAN_ROW with at most one opaque 4-neighbour and no
    light square among its 8 - what a moved part leaves of a shared edge (the boot's edge on the axe blade's when he
    breathes or lifts the foot: a 1-square stick hanging there). Again until none is left (a stick's next square becomes
    one). Thick outlines keep their corners (two neighbours)."""
    for _ in range(6):
        op = a[..., 3] > 0
        dark = op & (a[..., :3].astype(int).sum(-1) < 70)
        light = op & ~dark
        for c in RIBBON_EDGE:
            light |= (a[..., :3] == c).all(-1) & op
        p = np.pad(op, 1)
        n4 = p[:-2, 1:-1].astype(int) + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]
        near = ndimage.binary_dilation(light, structure=np.ones((3, 3)))
        m = dark & (n4 <= 1) & ~near
        m[:ORPHAN_ROW] = False
        m[:, CLOTH_COLS[0]:CLOTH_COLS[1]] = False
        if not m.any():
            break
        a[m] = 0
    return a


def tidy(a):
    a = orphans(specks(a))
    a = G.complete_outline(a, color=OUTLINE, feet=SOLE)[0]
    a = pinholes(close_all(a))
    a[SOLE + 1:] = 0
    return a


def codex(tag, n):
    return load(os.path.join(CODEX, f"sion_{tag}_{n}_1x.png"))


RIBBON = [(251, 38, 24), (129, 0, 1), (156, 1, 5), (252, 99, 46)]   # the ribbon's (and the eyes') reds


def scaled_frame(a, f):
    """A Codex frame without its head, shrunk by f, the design's head pasted back on the shrunken neck. Squares of the
    ribbon's reds outside the pasted head are what Codex's own generated ribbon left (its restore script cleared most):
    they go too (a red tatter under the ribbon)."""
    dy, dx = find_head(a)
    hm = head_mask()
    ys, xs = np.nonzero(hm)
    x0, y0 = DESIGN_AT
    b = a.copy()
    b[ys + y0 + dy, xs + x0 + dx] = 0
    for c in RIBBON:
        b[(b[..., :3] == c).all(-1) & (b[..., 3] > 0)] = 0
    s, ymap, xmap = shrink(b, f)
    ny, nx = ymap(NECK[0] + y0 + dy), xmap(NECK[1] + x0 + dx)
    return tidy(paste_head(s, ny - (NECK[0] + y0), nx - (NECK[1] + x0)))


def scale_of(tag):
    """1 / the median size of the tag's own Codex frames (not the design copies)."""
    nums = sorted({n for n in TAGS[tag] if n != "design"})
    return 1.0 / float(np.median([body_scale(codex(tag, n)) for n in nums]))


def actions():
    d = design()
    idle = on_canvas(d)
    out = {"idle": [(tidy(breathe(idle, upper(idle), k)), IDLE_MS) for k in BREATH],
           "run": [(tidy(walk_frame(idle, n_, f_, r_)), WALK_MS) for n_, f_, r_ in WALK]}
    for tag, nums in TAGS.items():
        f = scale_of(tag)
        frames = []
        for n, ms in zip(nums, MS[tag]):
            fix = SCALE_FIX.get((tag, n), 1.0)
            frames.append((tidy(idle.copy()) if n == "design" else scaled_frame(codex(tag, n), f * fix), ms))
        out[tag] = frames
    out["hit"] = [(tidy(on_canvas(d, dx=-2)), 80.0), (tidy(on_canvas(d, dx=-1)), 120.0)]
    out["ult"] = [(f, ULT_MS) for f in charge()]
    return out


def charge():
    """R's charge frames: Codex's charge pose's upper body over the design's legs walking."""
    u = codex("ult", 1)
    u = scaled_frame(u, 1.0 / body_scale(u))
    r0, c0, c1 = ULT_CUT
    u[r0:, c0:c1] = 0
    dy, dx = ULT_SHIFT
    top = np.zeros_like(u)
    ys, xs = np.nonzero(u[..., 3] > 0)
    top[ys + dy, xs + dx] = u[ys, xs]
    legs = on_canvas(design())
    legs[~box_mask(WALK_NEAR + WALK_FAR + CLOTH_BOX)] = 0
    out = []
    for n_, f_, r_ in WALK:
        w = walk_frame(legs, n_, f_, r_)
        t = np.roll(top, -r_, axis=0)
        m = t[..., 3] > 0
        w[m] = t[m]
        out.append(tidy(largest(w)))
    return out


def largest(a):
    """Only the figure's own piece (8-connected): the cut leaves the near boot's edge column behind as a loose stick."""
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(a[..., 3] > 0, lab, range(1, n + 1))
        a[(lab > 0) & (lab != 1 + int(np.argmax(sizes)))] = 0
    return a


def box_mask(boxes, dy=0, dx=0):
    m = np.zeros((ROWS, COLS), bool)
    x0, y0 = DESIGN_AT
    for r0, r1, c0, c1 in boxes:
        m[y0 + dy + r0:y0 + dy + r1, x0 + dx + c0:x0 + dx + c1] = True
    return m


def breathe(can, mask, k):
    """The masked squares moved k rows up; the squares they uncover take the colour of the square under them."""
    if k == 0:
        return can.copy()
    out = can.copy()
    ys, xs = np.nonzero(mask)
    out[ys, xs] = 0
    rest = out.copy()
    out[ys - k, xs] = can[ys, xs]
    hole = (out[..., 3] == 0) & mask
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            below = y + 1
            while below < can.shape[0] and out[below, x, 3] == 0 and mask[below, x]:
                below += 1
            if below < can.shape[0] and rest[below, x, 3] > 0:
                out[y, x] = rest[below, x]
            elif below < can.shape[0] and out[below, x, 3] > 0:
                out[y, x] = out[below, x]
    return out


def upper(can):
    """The idle's squares that breathe: all but the legs and the loin cloth."""
    return (can[..., 3] > 0) & ~box_mask(WALK_NEAR + WALK_FAR + CLOTH_BOX)


def walk_frame(idle, near_step, far_step, rise):
    """league_galio's / league_braum's walk on the idle: each leg's squares moved (dx, -lift) after losing their top
    `lift` rows; the far leg first, the near one over it, the body over both; the whole frame `rise` rows up; the cracks
    a step opens take the outline."""
    H, W = idle.shape[:2]
    op = idle[..., 3] > 0
    near, far = box_mask(WALK_NEAR) & op, box_mask(WALK_FAR) & op
    band = DESIGN_AT[1] + WALK_BAND
    body = idle.copy()
    body[near | far] = 0
    out = np.zeros_like(idle)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        leg = np.where(m[..., None], idle, 0).astype(np.uint8)
        leg[:band + 1 + lift] = 0
        ys, xs = np.nonzero(leg[..., 3] > 0)
        ok = (ys - lift >= 0) & (xs + dx < W)
        out[ys[ok] - lift, xs[ok] + dx] = leg[ys[ok], xs[ok]]
    m = body[..., 3] > 0
    out[m] = body[m]
    ground = np.zeros_like(op)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        if lift:
            ys, xs = np.nonzero(m)
            ground[ys.max() - lift + 1:ys.max() + 1, xs.min():xs.max() + dx + 1] = True
    own = ndimage.binary_fill_holes(op) & ~op
    for _ in range(3):
        wop = out[..., 3] > 0
        crack = (op & ~wop & ~ground) | (ndimage.binary_fill_holes(wop) & ~wop & ~own)
        fill = np.zeros_like(crack)
        for arr in (crack, crack.T):
            f = fill if arr is crack else fill.T
            for y in np.nonzero(arr.any(1))[0]:
                xs = np.nonzero(arr[y])[0]
                for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
                    if len(run) <= CRACK:
                        f[y, run] = True
        if not fill.any():
            break
        out[fill] = (*OUTLINE, 255)
    return np.roll(out, -rise, axis=0)


def review_sheet(frames, path, z=4):
    tiles = [Image.fromarray(c) for c, _ in frames]
    op = np.zeros((ROWS, COLS), bool)
    for c, _ in frames:
        op |= c[..., 3] > 0
    ys, xs = np.nonzero(op)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    w, h = box[2] - box[0], box[3] - box[1]
    big = Image.new("RGBA", (len(tiles) * (w * z + 6), h * z), (255, 0, 255, 255))
    for k, t in enumerate(tiles):
        c = t.crop(box)
        big.alpha_composite(c.resize((w * z, h * z), Image.NEAREST), (k * (w * z + 6), 0))
    big.convert("RGB").save(path)


ORDER = ["idle", "run", "attack", "skill_charge", "skill", "skill2", "skill2_w", "ult", "ult_hit", "hit", "dead"]


def pivot():
    """The pivot's centre on the canvas: the standing column's centre, (FEET + 0.5) 1x rows above the soles' bottom
    edge (tools/art/rig_bard.py's)."""
    return PIV_X + 0.5, SOLE + 1 - (FEET + 0.5) * PPU


def one_x(can, p):
    """The 1x frame: pixel_down.pixelate at 1 / PPU on a grid whose square round the pivot is centred on it; odd size,
    the pivot's square in the middle, and wide and tall enough that round(PPU x its size) holds the dense frame without
    growing it (the DLL wants hd_idle exactly round(PPU x the 1x width))."""
    px, py = p
    lo, (nx0, ny0) = PD.pixelate(can, 1 / PPU, (px - PPU / 2, py - PPU / 2), OUTLINE)
    ys, xs = np.nonzero(lo[..., 3])
    hw, hh = max(nx0 - xs.min(), xs.max() - nx0), max(ny0 - ys.min(), ys.max() - ny0)
    dy, dx = np.nonzero(can[..., 3])
    need_w = max(px - dx.min(), dx.max() + 1 - px)
    need_h = max(py - dy.min(), dy.max() + 1 - py)
    while round((2 * hw + 1) * PPU) / 2 < need_w:
        hw += 1
    while round((2 * hh + 1) * PPU) / 2 < need_h:
        hh += 1
    out = np.zeros((2 * hh + 1, 2 * hw + 1, 4), np.uint8)
    out[ys - ny0 + hh, xs - nx0 + hw] = lo[ys, xs]
    out, _, _ = G.complete_outline(out, color=OUTLINE, feet=hh + FEET)
    return out


def dense(can, one, p):
    """The game's frame: the canvas SHIFT rows lower on a frame of round(PPU x the 1x frame's size), grown alike at
    both ends where the drawing needs more, the pivot at its centre."""
    lx, ly = p
    W, H = round(one.shape[1] * PPU), round(one.shape[0] * PPU)
    ys, xs = np.nonzero(can[..., 3])
    yd = ys + SHIFT
    while W / 2 < max(lx - xs.min(), xs.max() + 1 - lx):
        W += 2
    while H / 2 < max(ly - yd.min(), yd.max() + 1 - ly):
        H += 2
    f = np.zeros((H, W, 4), np.uint8)
    ox, oy = int(np.floor(W / 2 - lx + 0.5)), int(np.floor(H / 2 - ly + 0.5))
    f[yd + oy, xs + ox] = can[ys, xs]
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="write every tag's canvas frames at 4x on magenta here")
    ap.add_argument("--frames-only", action="store_true", help="only the review sheets, no game files")
    a = ap.parse_args()
    acts = actions()
    p = pivot()
    sheet = {}
    for tag in ORDER:
        frames = acts[tag]
        if a.review:
            os.makedirs(a.review, exist_ok=True)
            review_sheet(frames, os.path.join(a.review, f"sion_{tag}.png"))
        if a.frames_only:
            continue
        ones, hds = [], []
        for can, ms in frames:
            one = one_x(can, p)
            ones.append((one, round(float(ms), 3)))
            hds.append(dense(can, one, p))
        sheet[tag] = ones
        H = max(h.shape[0] for h in hds)
        strip = np.zeros((H, sum(h.shape[1] + 1 for h in hds) - 1, 4), np.uint8)
        x = 0
        for h in hds:
            strip[:h.shape[0], x:x + h.shape[1]] = h
            x += h.shape[1] + 1
        Image.fromarray(strip).save(os.path.join(PPU_SRC, f"sion_{tag}.png"))
        with open(os.path.join(PPU_SRC, f"sion_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds]}, f)
    if sheet:
        w, h = G.write_sheet(STEM, sheet)
        print(f"league/champions/league_sion#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
