#!/usr/bin/env python3
"""Senna's action strips from Codex's per-frame generator drafts (assets/source/senna/codex_strips/raw).

    python tools/art/fix_senna_strips.py --sheet OUT.png       # every finished frame at 4x on one feet line
    python tools/art/fix_senna_strips.py --info                 # per-frame numbers
    python tools/art/fix_senna_strips.py --write                # assets/source/native/senna_<tag>.png + senna_cells.json
then tools/art/import_native.py --hero senna (COMPLETE closes the outline; BREATHE_SKIP: the idle stands as drawn).

How it came about (2026-10-10): Codex drew every frame as its own image (step-2 pack, work/se/strips_pack_se.py) and
sampled each draft at a fixed 12-px pitch into its 1x frames - but the drafts' squares are 8, 9, 10 or 12 px, so the
fixed pitch skipped squares and every frame came out another size. The user kept Codex's motion (「Codex跑步是对的
只要精修就行了」, then 「有问题的地方你帮忙修复 完美版了再喊我review」). Measured on the drafts read back on their own
grids: Codex drew the HEAD at the design's size (the face 10-13 x 8-16 squares against the design's 11 x 12) but the
BODY 1.1-1.6 times the design's (chin to soles 26-39 squares against 24). So, per frame:
  1. the draft read back on its own grid (the skill's regrid.py helpers; the alpha's faint noise cut at 128 first) and
     every square to the nearest of the design's 25 colours (CIELAB); League's pivot is the draft canvas's x 627 (the
     pack's 1024 canvas drawn as 1254 px: 64 x 1254 / 128), read onto the grid; the soles' row from SOLE;
  2. the head found: the skin component by the eyes, flooded through the head's colours inside a box round the face;
  3. the whole frame scaled DOWN by deleting whole rows and columns evenly (never two neighbours, the soles kept), so
     the cannon stays a straight piece - by SCALE (the median of three estimates of the design's body size);
  4. the cannon slid up its own axis where it would hide under the health bar (slide_cannon);
  5. its own head cleared and ONE head pasted unscaled on every frame (canon_head: run 6's, cleaned - CANON_EDITS), its
     chin and face centre on the shrunk head's; what is left of the own head round it cleared (HALO); the run's claw
     tips over the hood (HORN_TAGS); the swap's holes filled;
  6. squares hanging on by one neighbour off, the ground the figure encloses (now or after the import's outline)
     filled (onion);
  7. on League's cell: the soles on the feet row (81 of 96), the pivot column on League's pivot (the run steadied on
     its head, one pivot); frames HOLD repeats (the fall's kneel, R's last shot).
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
import regrid as RG  # noqa: E402
import strips as G  # noqa: E402
import design_senna as D  # noqa: E402
from native_refs import layout  # noqa: E402

R = D.R
RAW = os.path.join(ROOT, "assets", "source", "senna", "codex_strips", "raw")
NATIVE = os.path.join(ROOT, "assets", "source", "native")
# League's pivots and frame times per tag (native_pose.py on poses.json, the cells it wrote) - read; the cells the
# import reads (OUT_CELLS) are written from them: the idle the design, the steadied run on one pivot
CELLS = os.path.join(ROOT, "assets", "source", "senna", "league_cells.json")
OUT_CELLS = os.path.join(NATIVE, "senna_cells.json")
IDLE_MS = 140
CACHE = os.path.join(os.environ.get("LOCALAPPDATA", "."), "Temp", "se_work", "rb_cache")
FRAMES = {"run": 8, "attack": 6, "skill": 6, "skill2": 6, "ult": 8, "hit": 1, "dead": 6}
TAGS = list(FRAMES)
PIVOT_RAW_X = 627          # the pack's pivot column 64 of 128 on Codex's 1254-px canvas
Z = 8
FEET_ROW = 81              # the cell's feet line (native_pose: cell 128 x 96, feet 14 px above the bottom)
DESIGN_BODY = 24           # the design's chin to soles (its face rows 11-21, soles 45 of the figure)
# frames standing upright (the body measured chin to soles); the rest crouch, lunge or fall (measured by the face)
STANDING = ({f"run_{k}" for k in range(1, 9)} | {"skill_3", "skill_4", "skill_5", "skill_6", "skill2_5", "skill2_6"}
            | {f"ult_{k}" for k in range(2, 9)} | {"attack_5"})
C_FACE = 0.71              # body scale per face scale, the median over the standing frames (2026-10-10)
# the share of rows and columns each frame keeps: the median of three estimates, each off by 10-15 % on its own
# (2026-10-10): the face's size against the design's x C_FACE; the area of the figure without the cannon, matched to
# League's same frame (League's head and body area over its idle's, native_pose --parts at height 40) against the
# design's; and, standing, the chin-to-soles over the design's 24. Never above 1 (rows are only taken out).
SCALE = {
         "run_1": 0.912, "run_2": 0.86, "run_3": 0.86, "run_4": 0.727, "run_5": 0.745, "run_6": 0.727,
         "run_7": 0.752, "run_8": 0.878, "attack_1": 0.639, "attack_2": 0.748, "attack_3": 0.632, "attack_4": 0.716,
         "attack_5": 0.825, "attack_6": 0.878, "skill_1": 0.608, "skill_2": 0.677, "skill_3": 0.849, "skill_4": 0.923,
         "skill_5": 0.847, "skill_6": 0.74, "skill2_1": 0.845, "skill2_2": 0.851, "skill2_3": 0.804, "skill2_4": 0.835,
         "skill2_5": 0.742, "skill2_6": 0.745, "ult_1": 0.727, "ult_2": 0.939, "ult_3": 0.75, "ult_4": 0.778,
         "ult_5": 0.947, "ult_6": 0.89, "ult_7": 0.913, "ult_8": 0.756, "hit_1": 0.783, "dead_1": 0.614,
         "dead_2": 0.654, "dead_3": 0.71, "dead_4": 0.693, "dead_5": 0.633, "dead_6": 0.648,
}
SKIN = set("bkKs")
HEAD_COLOURS = set("bkKsxXca9pPqWEe")
GOLD = set("yYgG")
BOOT = set("TtNn")

DES = np.asarray(Image.open(R.lp(D.OUT)).convert("RGBA"))
if DES.shape[0] != 128:
    DES = np.asarray(Image.fromarray(DES).resize((128, 128), Image.NEAREST))
USED = {tuple(int(v) for v in p) for p in DES[DES[..., 3] > 0][:, :3]}
KEYS = [k for k, v in D.RGB.items() if v in USED]
PL = R.lab(np.array([D.RGB[k] for k in KEYS]))
INV = {v: k for k, v in D.RGB.items()}


# ----------------------------------------------------------------------------------------------- reading the drafts
def letters(a):
    near = ((R.lab(a[..., :3])[..., None, :] - PL[None, None]) ** 2).sum(-1).argmin(-1)
    return np.where(a[..., 3] >= 128, np.array(KEYS)[near], " ")


def read(tag, k):
    """The draft on its own grid as a letter array (trimmed) and League's pivot column on it."""
    os.makedirs(CACHE, exist_ok=True)
    src = os.path.join(RAW, f"{tag}_{k}.png")
    key = os.path.join(CACHE, f"{tag}_{k}.json")
    mt = os.path.getmtime(R.lp(src))
    if os.path.exists(key):
        c = json.load(open(key, encoding="utf-8"))
        if c["mtime"] == mt:
            return np.array([list(r) for r in c["rows"]]), c["square"], c["pivot"]
    raw = np.asarray(Image.open(R.lp(src)).convert("RGBA")).copy()
    raw[..., 3] = np.where(raw[..., 3] >= 128, 255, 0)
    raw[raw[..., 3] == 0] = 0
    op = raw[..., 3] >= 128
    ys, xs = np.nonzero(op)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    ex, ey = RG.profile(raw, op, 1), RG.profile(raw, op, 0)
    size = RG.square_size(ex, x0, x1)
    bx, by = RG.boundaries(ex, x0, x1, size), RG.boundaries(ey, y0, y1, size)
    H, W = len(by) - 1, len(bx) - 1
    out = np.zeros((H, W, 4), np.uint8)
    for j in range(H):
        cy = (by[j] + by[j + 1]) // 2
        for i in range(W):
            cx = (bx[i] + bx[i + 1]) // 2
            win = raw[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2].reshape(-1, 4)
            if (win[:, 3] >= 128).sum() * 2 > len(win):
                out[j, i, :3] = np.median(win[win[:, 3] >= 128][:, :3], axis=0).astype(np.uint8)
                out[j, i, 3] = 255
    g = letters(out)
    filled = g != " "
    rr, cc = np.nonzero(filled.any(1))[0], np.nonzero(filled.any(0))[0]
    g = g[rr.min():rr.max() + 1, cc.min():cc.max() + 1]
    pivot = int(np.searchsorted(bx, PIVOT_RAW_X, side="right") - 1 - cc.min())
    with open(key, "w", encoding="utf-8") as f:
        json.dump({"mtime": mt, "square": size, "pivot": pivot, "rows": ["".join(r) for r in g]}, f)
    return g, size, pivot


# ------------------------------------------------------------------------------------------------------- measuring
def face(g):
    """(top, bottom, left, right) of the face: the skin component touching the most eye squares (else the highest
    sizeable one)."""
    lab, n = ndimage.label(np.isin(g, list(SKIN)), np.ones((3, 3)))
    eyes = np.argwhere(g == "X")
    best, score = None, None
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 10:
            continue
        near = sum(1 for ey, ex in eyes if ((np.abs(ys - ey) <= 1) & (np.abs(xs - ex) <= 1)).any())
        s = near * 1000 + len(ys) - ys.min() * 3
        if score is None or s > score:
            best, score = (int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())), s
    return best


LEG = set("9pPqr")
LYING = {"dead_4", "dead_5", "dead_6"}
# the soles' row in each read-back (the standing foot's outline; lying, the body's lowest row), checked frame by frame
# on the letters (2026-10-10): Codex drew boots in greys AND whites, and the cannon's teal drum or its crystal tip often
# hangs lower than the feet, so no colour rule found them all
SOLE = {"run_1": 46, "run_2": 47, "run_3": 44, "run_4": 54, "run_5": 54, "run_6": 52, "run_7": 54, "run_8": 45,
        "attack_1": 61, "attack_2": 46, "attack_3": 53, "attack_4": 50, "attack_5": 52, "attack_6": 42,
        "skill_1": 49, "skill_2": 49, "skill_3": 46, "skill_4": 40, "skill_5": 43, "skill_6": 52,
        "skill2_1": 36, "skill2_2": 34, "skill2_3": 40, "skill2_4": 39, "skill2_5": 52, "skill2_6": 55,
        "ult_1": 39, "ult_2": 58, "ult_3": 48, "ult_4": 49, "ult_5": 40, "ult_6": 41, "ult_7": 37, "ult_8": 45,
        "hit_1": 45,
        "dead_1": 52, "dead_2": 35, "dead_3": 44, "dead_4": 36, "dead_5": 31, "dead_6": 24}


def soles(g, pivot, name=""):
    """The soles' row: under the lowest boot - a component of boot greys with the leggings' dark right above it - the
    lowest square in its columns (its outline). A body lying down: its lowest square that is not the cannon's."""
    H, W = g.shape
    if name in SOLE:
        return SOLE[name]
    if name in LYING:
        body = ~np.isin(g, list("mMcEW ")) & (g != " ")
        return int(np.nonzero(body.any(1))[0].max())
    lab, n = ndimage.label(np.isin(g, list(BOOT)), np.ones((3, 3)))
    best = None
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) < 3 or abs((xs.min() + xs.max()) / 2 - pivot) > 22:
            continue
        legs = sum(1 for y, x in zip(ys, xs) for dy in (1, 2, 3)
                   if y - dy >= 0 and g[y - dy, x] in LEG)
        if legs < 2:
            continue
        bottom = ys.max()
        for x in range(xs.min(), xs.max() + 1):
            y = bottom
            while y + 1 < H and g[y + 1, x] not in " " and g[y + 1, x] in "0yYgGTtNne":
                y += 1
                if y - ys.max() >= 2:
                    break
            bottom = max(bottom, y)
        best = bottom if best is None else max(best, bottom)
    return best if best is not None else H - 1


def head_mask(g, fb):
    """The head: flooded from the face through the head's colours inside a box round the face, the gold squares it
    holds (hood edge, loc rings) and its outline ring."""
    fy0, fy1, fx0, fx1 = fb
    H, W = g.shape
    box = np.zeros(g.shape, bool)
    box[max(fy0 - 9, 0):min(fy1 + 3, H), max(fx0 - 8, 0):min(fx1 + 7, W)] = True
    can = np.isin(g, list(HEAD_COLOURS)) & box
    lab, _ = ndimage.label(can, np.ones((3, 3)))
    seeds = set(lab[fy0:fy1 + 1, fx0:fx1 + 1][np.isin(g[fy0:fy1 + 1, fx0:fx1 + 1], list(SKIN))].ravel()) - {0}
    m = np.isin(lab, list(seeds))
    gold = np.isin(g, list(GOLD)) & box
    k4 = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
    for _ in range(2):
        m |= gold & (ndimage.convolve(m.astype(int), k4, mode="constant") >= 2)
    ring = (g == "0") & box & ndimage.binary_dilation(m, np.ones((3, 3)))
    return m | ring


_CANON = {}


def canon_head():
    """(letters of the canonical head, its mask, its anchor (chin row, face-centre column))."""
    if not _CANON:
        g, _, _ = read(*CANON_HEAD)
        g = g.copy()
        fb = face(g)
        m = head_mask(g, fb)
        m[:CANON_ROWS + 1] |= g[:CANON_ROWS + 1] != " "
        for y, last in CANON_CLAW.items():
            m[y, :last + 1] = False
        m = ndimage.binary_fill_holes(m) & (g != " ")
        lab, _ = ndimage.label(m, np.ones((3, 3)))          # the head's own piece (not the cannon's claws by the chin)
        ids, counts = np.unique(lab[fb[0]:fb[1] + 1, fb[2]:fb[3] + 1], return_counts=True)
        m = lab == max((c, i) for i, c in zip(ids, counts) if i)[1]
        for y, x, text in CANON_EDITS:
            for i, ch in enumerate(text):
                g[y, x + i] = ch
        _CANON["v"] = (g, m, (fb[1], (fb[2] + fb[3]) // 2))
    return _CANON["v"]


def canon_horn():
    """run 6's claw tips over the hood (CANON_CLAW): (letters, rows, columns) on run 6's read-back."""
    g, _, _ = read(*CANON_HEAD)
    claw = np.zeros(g.shape, bool)
    for y, last in CANON_CLAW.items():
        claw[y, :last + 1] = g[y, :last + 1] != " "
    lab, _ = ndimage.label(claw, np.ones((3, 3)))
    sizes = ndimage.sum(claw, lab, range(1, lab.max() + 1))
    claw = lab == 1 + int(np.argmax(sizes))
    ys, xs = np.nonzero(claw)
    return g[ys, xs], ys, xs


def scale_of(name, g, fb, sole):
    if name in SCALE:
        return SCALE[name]
    fy0, fy1, fx0, fx1 = fb
    if name in STANDING:
        f = DESIGN_BODY / max(sole - fy1, 1)
    else:
        f = C_FACE * np.sqrt(11 * 12 / ((fy1 - fy0 + 1) * (fx1 - fx0 + 1)))
    return min(f, 1.0)


# ------------------------------------------------------------------------------------------------------ the frames
def even_pick(lines, weights, lo, hi, q, hard):
    """q lines in lo..hi, the i-th near lo + (i + 0.5) * L / q, the cheapest within 2 of it (a line costs its weighted
    difference from the nearer neighbour), neighbours of a picked line only when nothing else is left."""
    def cost(j):
        return min(float(((lines[j] != lines[n]) * np.maximum(weights[j], weights[n])).sum())
                   for n in (j - 1, j + 1) if 0 <= n < len(lines))

    cand = [i for i in range(lo, hi + 1) if i not in hard]
    q = min(q, len(cand))
    picked = []
    L = hi - lo + 1
    for t in range(q):
        p = lo + (t + 0.5) * L / q - 0.5
        free = [i for i in cand if i not in picked]
        apart = [i for i in free if all(abs(i - j) > 1 for j in picked)]
        pool = apart or free
        near = [i for i in pool if abs(i - p) <= 2] or sorted(pool, key=lambda i: abs(i - p))[:1]
        picked.append(min(near, key=lambda i: (cost(i), abs(i - p))))
    return sorted(picked)


def drop(lines, weights, lo, hi, q, hard):
    """R.even_drop (never two neighbours, the cheapest near even places); even_pick when it cannot place them all."""
    if q <= 0:
        return []
    try:
        return R.even_drop(lines, weights, lo, hi, q, hard)
    except ValueError:
        return even_pick(lines, weights, lo, hi, q, hard)


CANNON = set("mMcaGgyYEWeTt9Nn0")
# rows the cannon may still hang under the soles, per tag (art-spec "Nothing under the feet": none in the run; a swing
# or a fall a row or two)
DEBUG = {}
WHOLE = {"run"}            # tags where nothing may hang under the soles (art-spec: idle and run)
# one head for every upright frame: run 6's (its face 11 x 12 like the design's, the hood, the two green eyes, the lips and
# the locs drawn closest to the design's) - each frame's own head was drawn another size (faces 8 x 8 to 13 x 16), and
# in a loop the head pulsed; the design's own head cannot be lifted out whole (the cannon's claws and ring run into its
# hood and locs). The fall and the flinch keep their own heads (tilted, lying, thrown back).
CANON_HEAD = ("run", 6)
# run 6's head whole (2026-10-10, 「眼睛有很多奇怪的地方」): the flood above leaves out the locs' red-brown squares and
# loose loc rings, and each became a hole by the eyes (or kept the frame's own hair, hood or eye squares there) - so the
# canonical head is every square of run 6 down to the chin's outline row (CANON_ROWS), the flood's squares under it (the
# hood's and the locs' ends), minus the cannon's claw tips standing over the hood's top left (CANON_CLAW: rows, last
# column). And its far eye cleaned: Codex drew it iris, dark, white (the white on the face's edge read as a third eye,
# the design's the same) - now iris, then skin; the lash square between the eyes skin too (the lashes ran across).
CANON_ROWS = 20
CANON_CLAW = {0: 99, 1: 99, 2: 99, 3: 25, 4: 24, 5: 23}
# (row, column, letters) on run 6's read-back: the far eye's dark + white -> skin; the lash square between the eyes ->
# skin; the brows apart (「眉毛连在一起不修吗」: the near brow ran on into the far one a row lower between the eyes, one
# bar over both) - the near brow 3 squares over the near eye, the far one 2 over the far eye, skin between
CANON_EDITS = [(13, 32, "KKPP"), (14, 32, "KK"), (15, 32, "K0"), (16, 35, "Kk0")]
HALO = 3                   # squares round the pasted head where the frame's own head may have left pieces
HORN_TAGS = {"run"}        # the claw tips over the hood: the run's (the cannon on her back); the casts hold it
# every frame wears it (2026-10-10): the fall's own heads (Codex drew each another size, tilt and eye - teal blocks, white
# slits - and pasted unscaled on bodies cut to 0.61-0.71 they came out half again the body's share in Codex's own
# drawing: 「眼睛有很多奇怪的地方」「死亡后赛娜模型变形不修吗」) gave way to the canonical head like the flinch's
OWN_HEAD = set()
EYES = {}                  # (row, column, letters) eye repaints on an own head's read-back, by frame
PIECE_MIN = 12             # a separate piece smaller than this is a speck (the dropped cannon in the death is bigger)
BODY_ONLY = set("PrqpKsk")


BAR_HALF, BAR_ROWS = 13, 8     # the health bar under the feet: 25 x 7 px (asset/base/sprite/hp_outline) round the pivot
SLIDE_MAX = 8                  # squares along its axis; further, the cannon leaves the hands
SLIDE_MAX_TAG = {"run": 10, "dead": 0}   # the run's frames 6-8 need up to 8.5 (the hands still on it); a body falling
#                                          drops the cannon in front of her: it lies there


def slide_cannon(g, srow, keep_out, piv, whole, limit=None):
    """Slide the cannon along its own axis, rigidly, until none of it is hidden under the health bar - the bar the game
    draws under the feet, 25 x 7 px round the pivot (asset/base/sprite/hp_outline). `whole`: nothing of it under the
    soles at all (the run, art-spec "Nothing under the feet"); else only the bar's box counts: a muzzle pointing at the
    ground beside her stays (it lies in front of her, and the bar does not cover it). The axis is fitted to the maroon
    wing plates (a colour nothing else has); the cannon is every cannon-coloured square in a band round that axis that
    hangs together with the plates, and its outline, minus the head and a square round it. The hands stay put - the
    cannon slides through them, at most SLIDE_MAX squares. Squares it uncovers inside the body take the body colour
    round them; what it leaves under the soles and pieces cut off from the figure go.
    Returns (letters, (dx, dy), pad): the letters padded by `pad` on every side when the cannon moved (pad 0 and the
    letters as they were when nothing needs it or it cannot be done within SLIDE_MAX)."""
    H, W = g.shape

    def bad(ys, xs):
        if whole:
            return ys > srow
        return (ys > srow) & (ys <= srow + BAR_ROWS) & (np.abs(xs - piv) <= BAR_HALF)

    ys0, xs0 = np.nonzero(g != " ")
    if not bad(ys0, xs0).any():
        return g, (0, 0), 0
    pts = np.argwhere(np.isin(g, ["m", "M"]))
    if len(pts) < 8:
        return g, (0, 0), 0
    c = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - c)
    u = vt[0] / np.linalg.norm(vt[0])                 # (dy, dx)
    if u[0] > 0:
        u = -u                                         # pointing up (toward the grip)
    nrm = np.array([-u[1], u[0]])
    t_m = (pts - c) @ u
    d_m = np.abs((pts - c) @ nrm)
    dmax = np.percentile(d_m, 95) + 2.5
    allp = np.argwhere(g != " ")
    t = (allp - c) @ u
    d = np.abs((allp - c) @ nrm)
    inb = (d <= dmax) & (t >= t_m.min() - 9) & (t <= t_m.max() + 12)
    sel = allp[inb]
    near_head = ndimage.binary_dilation(keep_out, np.ones((3, 3)))
    sel = sel[np.isin(g[sel[:, 0], sel[:, 1]], list(CANNON - {"0"})) & ~near_head[sel[:, 0], sel[:, 1]]]
    cand = np.zeros(g.shape, bool)
    cand[sel[:, 0], sel[:, 1]] = True
    # only what hangs together with the maroon plates (8-connected), not stray hood gold or boot greys in the band
    lab, _ = ndimage.label(cand, np.ones((3, 3)))
    keep = set(lab[np.isin(g, ["m", "M"]) & cand].ravel()) - {0}
    mask = np.isin(lab, list(keep))
    # and the squares inside it in other colours (2026-10-10: Codex shaded the plates with browns and plums that read
    # back as the skin's and the clothes' letters - left behind, a slide of even one row opened holes along the cannon):
    # in the band, mostly surrounded by it, or enclosed by it
    band = np.zeros(g.shape, bool)
    band[allp[inb][:, 0], allp[inb][:, 1]] = True
    band &= ~near_head
    for _ in range(4):
        nb = ndimage.convolve(mask.astype(int), np.ones((3, 3), int), mode="constant") - mask
        add = band & ~mask & (g != "0") & (nb >= 5)
        if not add.any():
            break
        mask |= add
    mask |= ndimage.binary_fill_holes(mask) & band & (g != " ")
    # its outline: dark squares touching it and no square of the body
    body = (np.isin(g, list(BODY_ONLY)) & ~mask) | keep_out
    ring = ((g == "0") & ndimage.binary_dilation(mask, np.ones((3, 3)))
            & ~ndimage.binary_dilation(body, np.ones((3, 3))))
    mask |= ring
    DEBUG["cannon"] = (g.copy(), mask.copy())
    ys, xs = np.nonzero(mask)
    other = (g != " ") & ~mask
    oy, ox = np.nonzero(other)
    if bad(oy, ox).any() and whole:
        pass                                           # the body itself under the soles: nothing to slide
    # the smallest move along u that clears the bar (or the soles)
    move = None
    for step in np.arange(0.25, (SLIDE_MAX if limit is None else limit) + 0.01, 0.25):
        dy, dx = int(round(step * u[0])), int(round(step * u[1]))
        if (dy, dx) == (0, 0):
            continue
        if not bad(ys + dy, xs + dx).any():
            move = (dy, dx)
            break
    if move is None:
        return g, (0, 0), 0
    dy, dx = move
    pad = 20
    out = np.full((H + 2 * pad, W + 2 * pad), " ", dtype="<U1")
    out[pad:pad + H, pad:pad + W] = np.where(mask, " ", g)
    moved = np.zeros(out.shape, bool)
    moved[ys + dy + pad, xs + dx + pad] = True
    # uncovered squares inside the body: the body colour round them
    for y, x in zip(ys + pad, xs + pad):
        if moved[y, x]:
            continue
        nb = [out[y + j, x + i] for j in (-1, 0, 1) for i in (-1, 0, 1)
              if (j or i) and out[y + j, x + i] in BODY_ONLY]
        if len(nb) >= 4:
            out[y, x] = max(set(nb), key=nb.count)
    out[ys + dy + pad, xs + dx + pad] = g[ys, xs]
    # what the move left under the soles (Codex drew some of its edge in the clothes' dark plum, which the cannon's
    # colours leave out), then pieces cut off from the figure
    left = (out != " ") & ~moved
    left[:srow + 1 + pad] = False
    out[left] = " "
    lab, n = ndimage.label(out != " ", np.ones((3, 3)))
    if n > 1:
        sizes = ndimage.sum(np.ones(out.shape), lab, range(1, n + 1))
        main = 1 + int(np.argmax(sizes))
        for i in range(1, n + 1):
            if i != main and sizes[i - 1] < 12:
                out[lab == i] = " "
    return out, (dx, dy), pad


KEEP_GAPS = {}             # {frame: [(row, column) in a gap League also has (between an arm and the body...)]}
FILL_HOLES = True          # (False: the review's "before")


def onion(out, todo):
    """Fill the `todo` squares of `out` from their edge in, each the commonest colour round it (the outline's only when
    no two others are there); the number filled."""
    n = int(todo.sum())
    todo = todo.copy()
    while todo.any():
        nbs = ndimage.convolve((out != " ").astype(int), np.ones((3, 3), int), mode="constant")
        edge = todo & (nbs >= 3)
        if not edge.any():
            edge = todo & (nbs >= 1)
        if not edge.any():
            break
        for y, x in zip(*np.nonzero(edge)):
            nb = [out[y + j, x + i] for j in (-1, 0, 1) for i in (-1, 0, 1)
                  if 0 <= y + j < out.shape[0] and 0 <= x + i < out.shape[1] and out[y + j, x + i] != " "]
            inner = [v for v in nb if v != "0"]
            pick = inner if len(inner) >= 2 else nb
            out[y, x] = max(sorted(set(pick)), key=pick.count)
        todo &= ~edge
    return n


def frame(tag, k):
    """(finished frame letters, pivot column, soles row, info)."""
    name = f"{tag}_{k}"
    g, sq, pivot = read(tag, k)
    H, W = g.shape
    fb = face(g)
    sole = soles(g, pivot, name)
    f = scale_of(name, g, fb, sole)
    mask = head_mask(g, fb)
    if name in EYES:
        g = g.copy()
        for y, x, text in EYES[name]:
            g[y, x:x + len(text)] = list(text)
            mask[y, x:x + len(text)] = True
    # 3. scale the whole frame by whole rows and columns
    idx = np.vectorize(ord)(g)
    w = np.vectorize(lambda v: D.WEIGHT.get(chr(v), 1))(idx)
    R.JITTER = 1
    qr, qc = round(H * (1 - f)), round(W * (1 - f))
    hard_r = {sole, sole - 1} | set(range(sole + 1, H))
    dr = drop([idx[y] for y in range(H)], [w[y] for y in range(H)], 1, H - 2, qr, hard_r)
    kr = [y for y in range(H) if y not in dr]
    sub, ws = idx[kr], w[kr]
    dc = drop([sub[:, x] for x in range(W)], [ws[:, x] for x in range(W)], 1, W - 2, qc, {pivot})
    kc = [x for x in range(W) if x not in dc]
    small = g[np.ix_(kr, kc)].copy()
    smask = mask[np.ix_(kr, kc)]

    def at(keep, v):
        return int(np.clip(np.searchsorted(keep, v), 0, len(keep) - 1))

    # the cannon slid up its own axis where it hangs under the soles (the head kept out of it)
    small, slid, sp = slide_cannon(small, at(kr, sole), smask, at(kc, pivot), tag in WHOLE,
                                   0 if SLIDE_MAX == 0 else SLIDE_MAX_TAG.get(tag, SLIDE_MAX))
    if sp:
        smask = np.pad(smask, sp)

    # 4. the frame's own head, unscaled, over the shrunk one (chin and face centre on the shrunk head's)
    fy0, fy1, fx0, fx1 = fb
    ay0, ax0 = fy1, (fx0 + fx1) // 2
    ay1, ax1 = at(kr, ay0) + sp, at(kc, ax0) + sp
    pad = 16
    out = np.full((small.shape[0] + 2 * pad, small.shape[1] + 2 * pad), " ", dtype="<U1")
    out[pad:pad + small.shape[0], pad:pad + small.shape[1]] = np.where(smask, " ", small)
    if name in OWN_HEAD:
        hg, hm, (hy, hx) = g, mask, (ay0, ax0)
    else:
        hg, hm, (hy, hx) = canon_head()
    ys, xs = np.nonzero(hm)
    out[ys - hy + ay1 + pad, xs - hx + ax1 + pad] = hg[ys, xs]
    cleared = 0
    if name not in OWN_HEAD:
        # what is left of the frame's own head round the pasted one (its hood's edge, loc rings, the cannon's claw tip
        # cut short by the bigger hood): pieces lying wholly within HALO squares of the pasted head above its chin - the
        # cannon, a hand or the body reach further and stay
        head = np.zeros(out.shape, bool)
        head[ys - hy + ay1 + pad, xs - hx + ax1 + pad] = True
        near = ndimage.binary_dilation(head, np.ones((2 * HALO + 1, 2 * HALO + 1))) & ~head
        near[ay1 + pad + 1:] = False
        lab, n = ndimage.label((out != " ") & ~head, np.ones((3, 3)))
        for i in range(1, n + 1):
            piece = lab == i
            if not (piece & ~near).any():
                out[piece] = " "
                cleared += int(piece.sum())
        if tag in HORN_TAGS:
            # the run carries the cannon on her back, its claw tips standing over the hood's top left (Codex drew them in
            # 7 of 8 frames, each cut to another stub by the bigger pasted hood): the frame's own go (whatever is not
            # the head above the eyes and left of the face), run 6's go in behind the head
            corner = np.zeros(out.shape, bool)
            corner[:ay1 + pad - 2, :ax1 + pad - 3] = True
            gone = corner & ~head & (out != " ")
            out[gone] = " "
            cleared += int(gone.sum())
            cl, cy, cx = canon_horn()
            Y, X = cy - hy + ay1 + pad, cx - hx + ax1 + pad
            free = out[Y, X] == " "
            out[Y[free], X[free]] = cl[free]
    # holes the head swap left (the shrunk head's squares the pasted one does not cover - its chin and neck - and the
    # gaps between the pasted locs and the shoulder): every hole (ground enclosed by the figure) touching the shrunk
    # head or the pasted one fills from its edge in, each square the commonest colour round it (the outline's only
    # when nothing else is there)
    swap = np.zeros(out.shape, bool)
    swap[pad:pad + small.shape[0], pad:pad + small.shape[1]] = smask
    pasted = np.zeros(out.shape, bool)
    pasted[ys - hy + ay1 + pad, xs - hx + ax1 + pad] = True
    swap |= ndimage.binary_dilation(pasted, np.ones((3, 3)))
    ground, _ = ndimage.label(out == " ")
    outside = set(ground[0]) | set(ground[-1]) | set(ground[:, 0]) | set(ground[:, -1])
    todo = np.isin(ground, list(set(ground[swap & (out == " ")].ravel()) - outside - {0}))
    filled = onion(out, todo)
    # pieces cut off from the figure (a claw tip that slid out from behind the hood, Codex's specks)
    lab, n = ndimage.label(out != " ", np.ones((3, 3)))
    dropped_px = 0
    if n > 1:
        sizes = ndimage.sum(np.ones(out.shape), lab, range(1, n + 1))
        main = 1 + int(np.argmax(sizes))
        for i in range(1, n + 1):
            if i != main and sizes[i - 1] < PIECE_MIN:
                out[lab == i] = " "
                dropped_px += int(sizes[i - 1])
    filled_rows = np.nonzero((out != " ").any(1))[0]
    filled_cols = np.nonzero((out != " ").any(0))[0]
    t, l = filled_rows.min(), filled_cols.min()
    out = out[t:filled_rows.max() + 1, l:filled_cols.max() + 1]
    piv = at(kc, pivot) + sp + pad - l
    srow = at(kr, sole) + sp + pad - t
    # 6. ground the figure encloses - Codex's gaps between plates, cloak and legs, now or once the import closes the
    # outline (complete_outline puts the outline colour in clear squares by light ones, which can shut a narrow gap):
    # filled like the swap's holes (Jax's rule, 2026-10-03: only gaps League has stay - none here so far)
    # squares hanging on by one neighbour (a loc's or a claw's last outline square, a brown crumb by the muzzle): at
    # game size a speck off the outline
    for _ in range(3):
        op = out != " "
        lone = op & (ndimage.convolve(op.astype(int), np.ones((3, 3), int), mode="constant") - op <= 1)
        if not lone.any():
            break
        out[lone] = " "
    holes = 0
    for _ in range(6 if FILL_HOLES else 0):   # a filled gap moves the outline the import adds: again till none is shut
        a = np.pad(to_rgba(out), ((1, 1), (1, 1), (0, 0)))
        b, _, _ = G.complete_outline(a, color=D.RGB["0"], dark=70, feet=max(srow + 1, a.shape[0] - 2))
        ground, _ = ndimage.label(b[..., 3] == 0)
        outside = set(ground[0]) | set(ground[-1]) | set(ground[:, 0]) | set(ground[:, -1])
        shut = ((ground != 0) & ~np.isin(ground, list(outside)))[1:-1, 1:-1] & (out == " ")
        clear, _ = ndimage.label(out == " ")                   # and the ground shut already (the import would ink it)
        rim = set(clear[0]) | set(clear[-1]) | set(clear[:, 0]) | set(clear[:, -1])
        shut |= (clear != 0) & ~np.isin(clear, list(rim))
        for y, x in KEEP_GAPS.get(name, ()):
            lab_, _ = ndimage.label(shut)
            if lab_[y, x]:
                shut &= lab_ != lab_[y, x]
        if not shut.any():
            break
        holes += onion(out, shut)
    info = dict(square=sq, size=(H, W), scale=round(f, 3), dropped=(len(dr), len(dc)), face=fb,
                head_col=int(ax1 + pad - l), chin=int(ay1 + pad - t),
                head_sq=(ys - hy + ay1 + pad - t, xs - hx + ax1 + pad - l),
                head=int(mask.sum()), filled=filled, cleared=cleared, holes=holes, out=out.shape, slid=slid, specks=dropped_px,
                pieces=int(ndimage.label(out != " ", np.ones((3, 3)))[1]))
    return out, piv, srow, info


def to_rgba(g):
    a = np.zeros(g.shape + (4,), np.uint8)
    for ch, rgb in D.RGB.items():
        m = g == ch
        a[m, :3] = rgb
        a[m, 3] = 255
    return a


def place(tag, k, cells, head_at=None):
    """The finished frame on League's cell (128 x 96): soles on FEET_ROW, pivot column on League's pivot - or, given
    `head_at`, the head's face-centre column there (the run, steadied on its head)."""
    g, piv, srow, info = frame(tag, k)
    cw, ch = cells["cell"]
    px, py = cells["tags"][tag][k - 1]["pivot"]
    a = to_rgba(g)
    cell = np.zeros((ch, cw, 4), np.uint8)
    dy, dx = FEET_ROW - srow, px - piv
    info["origin"] = px
    if head_at is not None:
        dx = head_at - info["head_col"]
    info["head_x"] = info["head_col"] + dx
    info["head_cell"] = (info["head_sq"][0] + dy, info["head_sq"][1] + dx)
    info["chin_y"] = info["chin"] + dy
    ys, xs = np.nonzero(a[..., 3] > 0)
    Y, X = ys + dy, xs + dx
    ok = (Y >= 0) & (Y < ch) & (X >= 0) & (X < cw)
    cell[Y[ok], X[ok]] = a[ys[ok], xs[ok]]
    info["clipped"] = int((~ok).sum())
    info["below_feet"] = int((Y[ok] > FEET_ROW).sum())
    return cell, info


STEADY = {"run"}          # loops steadied on the head: every frame's face centre on the strip's mean column


# the fall after frame 3 (2026-10-10, 「死亡后赛娜模型变形不修吗」): Codex drew frames 4-6 lying flat - a long thin body,
# the cloak a curl, cut to the design's size a flattened strip under the head, and the last of them is what stays on
# the ground while she is dead. League's fall ends on her hands and knees (its frames 3-6): frames 4-6 hold frame 3's
# kneel (one hand down, the cannon dropped before her), the head sinking a row. And R's last frame: Codex drew it 10
# columns left of frame 7 (its front boot 18 columns back, its head 5) where League holds the shot still through frames
# 6-8 - so it holds frame 7. {tag: {frame: (frame held, rows down)}}
HOLD = {"dead": {4: (3, 0), 5: (3, 1), 6: (3, 1)}, "ult": {8: (7, 0)}}


def held(cell, info, sink):
    """A placed frame again with its pasted head `sink` rows lower (moved whole, over the collar)."""
    cell, info = cell.copy(), dict(info)
    if sink:
        Y, X = info["head_cell"]
        px = cell[Y, X].copy()
        cell[Y, X] = 0
        cell[Y + sink, X] = px
        info["head_cell"] = (Y + sink, X)
        info["chin_y"] = info["chin_y"] + sink
        # the gaps the move opens (the frame's filled loc gaps stay where they were): filled as in frame()
        g = np.full(cell.shape[:2], " ", dtype="<U1")
        for ch, rgb in D.RGB.items():
            g[(cell[..., 3] > 0) & (cell[..., :3] == rgb).all(-1)] = ch
        ground, _ = ndimage.label(g == " ")
        outside = set(ground[0]) | set(ground[-1]) | set(ground[:, 0]) | set(ground[:, -1])
        if onion(g, (ground != 0) & ~np.isin(ground, list(outside))):
            cell = to_rgba(g)
    return cell, info


def build(cells):
    out = {}
    for tag, n in FRAMES.items():
        fr = [place(tag, k, cells) for k in range(1, n + 1)]
        for k, (src, sink) in HOLD.get(tag, {}).items():
            fr[k - 1] = held(*fr[src - 1], sink)
        if tag in STEADY:
            # the head on one column and every frame on one pivot (League's mean): the head stands still in the game
            col = int(round(np.mean([info["head_x"] for _, info in fr])))
            origin = int(round(np.mean([info["origin"] for _, info in fr])))
            fr = [place(tag, k, cells, head_at=col) for k in range(1, n + 1)]
            for _, info in fr:
                info["origin"] = origin
        out[tag] = fr
    return out


def idle_cell(cells):
    """The design on the cell: soles on FEET_ROW, the feet's middle on column 64 (design_senna.on_canvas)."""
    cw, ch = cells["cell"]
    cell = np.zeros((ch, cw, 4), np.uint8)
    ys, xs = np.nonzero(DES[..., 3] > 0)
    d0 = DES[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    cell[FEET_ROW + 1 - d0.shape[0]:FEET_ROW + 1, xs.min():xs.min() + d0.shape[1]] = d0
    return cell


def write(cells, frames):
    """senna_<tag>.png (8x, native_refs.layout) for every tag, the idle the design alone, and OUT_CELLS: each frame's
    pivot (its origin column, League's pivot row) and time."""
    cw, ch = cells["cell"]
    py = cells["tags"]["run"][0]["pivot"][1]
    out = {"idle": [{"pivot": [64, py], "ms": IDLE_MS}]}
    frames = {"idle": [(idle_cell(cells), {"origin": 64})], **frames}
    for tag, fr in frames.items():
        if tag != "idle":
            out[tag] = [{"pivot": [int(info["origin"]), py], "ms": cells["tags"][tag][i]["ms"]}
                        for i, (_, info) in enumerate(fr)]
        cols, rows = layout(len(fr))
        sheet = np.zeros((rows * ch, cols * cw, 4), np.uint8)
        for i, (cell, _) in enumerate(fr):
            y, x = (i // cols) * ch, (i % cols) * cw
            sheet[y:y + ch, x:x + cw] = cell
        img = Image.fromarray(sheet).resize((cols * cw * Z, rows * ch * Z), Image.NEAREST)
        img.save(R.lp(os.path.join(NATIVE, f"senna_{tag}.png")))
        print("wrote", f"senna_{tag}.png", len(fr), "frames")
    with open(R.lp(OUT_CELLS), "w", encoding="utf-8", newline="\n") as f:
        f.write("{" + json.dumps({"cell": cells["cell"], "scale": Z})[1:-1] + ', "tags": {\n')
        f.write(",\n".join(f'  "{t}": ' + json.dumps(v) for t, v in out.items()))
        f.write("\n}}\n")
    print("wrote", os.path.basename(OUT_CELLS))


def sheet(cells, frames, path, z=4):
    cw, ch = cells["cell"]
    des = np.zeros((ch, cw, 4), np.uint8)
    ys, xs = np.nonzero(DES[..., 3] > 0)
    d0 = DES[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    dy = FEET_ROW - (d0.shape[0] - 1)
    des[dy:dy + d0.shape[0], 64 - (64 - xs.min()):64 - (64 - xs.min()) + d0.shape[1]] = d0
    rows = []
    for tag, fr in frames.items():
        cells_ = [("idle", des)] + [(f"{tag} {i + 1}", c) for i, (c, _) in enumerate(fr)]
        img = Image.new("RGBA", (len(cells_) * 100 * z // 2, 72 * z // 2 + 14), (92, 98, 86, 255))
        dr = ImageDraw.Draw(img)
        for i, (nm, c) in enumerate(cells_):
            crop = c[20:92, 14:114]
            im = Image.fromarray(np.ascontiguousarray(crop)).resize((crop.shape[1] * z // 2 * 1, crop.shape[0] * z // 2 * 1), Image.NEAREST)
            img.alpha_composite(im, (i * 100 * z // 2, 14))
            dr.line([(i * 100 * z // 2, 14 + (FEET_ROW + 1 - 20) * z // 2), ((i + 1) * 100 * z // 2 - 4, 14 + (FEET_ROW + 1 - 20) * z // 2)],
                    fill=(70, 76, 66, 255))
            dr.text((i * 100 * z // 2 + 2, 1), nm, fill=(255, 255, 255, 255))
        rows.append(img)
    W = max(i.width for i in rows)
    out = Image.new("RGB", (W, sum(i.height for i in rows)), (255, 255, 255))
    y = 0
    for i in rows:
        out.paste(i.convert("RGB"), (0, y))
        y += i.height
    out.save(path)
    print("sheet", path, out.size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--info", action="store_true")
    a = ap.parse_args()
    cells = json.load(open(R.lp(CELLS), encoding="utf-8"))
    frames = build(cells)
    if a.info:
        for tag, fr in frames.items():
            for i, (_, info) in enumerate(fr):
                print(f"{tag}_{i + 1}", {k: v for k, v in info.items() if k not in ("head_sq", "head_cell")})
    if a.sheet:
        sheet(cells, frames, a.sheet)
    if a.write:
        write(cells, frames)


if __name__ == "__main__":
    main()
