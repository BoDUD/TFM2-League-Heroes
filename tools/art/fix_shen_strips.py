#!/usr/bin/env python3
"""Shen's action strips from Codex's step-2 raws (assets/source/shen/codex_strips/raw) + the approved design.

    python tools/art/fix_shen_strips.py [--review DIR] [--only TAG]

Writes assets/source/native/shen_<tag>.png (every frame a 128 x 128 canvas cell at 8x, the soles on row 99, the
standing point on column 64) and shen_cells.json; then tools/art/import_native.py --hero shen.

Codex drew every frame as its own generator image after League's pose (pack: assets/source/shen/MODEL_STRIPS.md) and
then made "final" copies itself by resizing and re-quantising them: those are blurred and lost the glowing eyes
(codex_strips/1x, kept for reference only). The raws are crisp, but each frame came out at its own square size
(about 6.5-10.7 px on the 1254-px image; the canvas square is 1254 / 128 = 9.8), i.e. some frames are drawn with up to
40 % more squares than the design. Here, per frame:
  1. read the raw on its own grid (the skill's regrid.py) at its square size - measured from the outline, which is one
     square thick (SQUARE overrides), and map every square to the design's 30 colours (CIELAB);
  2. bring it to the design's scale by deleting whole rows and columns evenly (design_rengar.even_drop: never two
     neighbours, the cheapest lines; the eyes' rows and columns and the soles kept), the factor being its square size
     over the canvas square (FIX corrects frames Codex drew bigger or smaller on the canvas);
  3. stand it where League's frame stands: its lowest row on League's lowest row (the soles' row for a grounded frame),
     its eyes on League's head column (else its middle on League's);
  4. clear specks (pieces of fewer than SPECK squares apart from the body) and close the outline.
The idle is the design square for square, breathing (the body above the sash sinks over the legs); the run is a trot
of the design's own legs moved whole (TROT) under its own upper body: leaning, the near fist up (run_upper). Q and R start from the design itself (League's casts start from the idle
pose).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import strips  # noqa: E402
from regrid import regrid  # noqa: E402
import design_rengar as R  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "shen", "codex_strips", "raw")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "shen_native.png")
SPEC = os.path.join(ROOT, "assets", "source", "shen", "poses.json")
POSE = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Temp", "sn_work", "pose")   # native_pose renders (League)
OUT = os.path.join(ROOT, "assets", "source", "native")
Z = 8
SOLES, MID = 99, 64
PIVOT = (MID, SOLES - 11)
CANVAS_SQUARE = 1254 / 128
# The run: a scissor step of the design's own legs, nothing redrawn (the user: 「腿别变形」「脚也别变形」「颜色都不一致」
# after Codex's two skin swaps and legs drawn from League's joints were all rejected; 「好歹有点换脚的感觉啊 平行走路？？？？」
# on legs lifting in place). Each leg is two rigid pieces of the design: the thigh (the hakama bulb, rows 85-90) and
# the lower leg (cuff, shin and boot, rows 91-99). A leg moves sideways whole (both pieces, NEAR_STEP / FAR_STEP
# columns: the near one forward while the planted far one slides back, then the other way, 2 columns inwards at most,
# the thighs tucking under the apron's edges); a step lifts only the lower leg, BEHIND its own thigh (a bent knee: the
# thigh never rises into the sash, nothing is cut but what goes behind). The tail hem moves with the near leg it hangs
# beside, the near boot in front of it, so the two keep the idle's arrangement; the body sinks a row as a foot lands.
# (Lifting the whole leg hid the bulb's top under the sash and ran the mirrored near boot through the tail hem:
# 「你看不到变形吗」.)
NEAR_STEP = [(2, 0), (1, 0), (1, 0), (0, 0), (0, 1), (1, 2), (2, 2), (2, 1)]        # (columns, lower leg rows up)
FAR_STEP = [(-2, 1), (-1, 2), (0, 2), (0, 1), (0, 0), (-1, 0), (-1, 0), (-2, 0)]
TROT_BOB = [1, 0, 0, 0, 1, 0, 0, 0]
KNEE_ROW = 91                     # the lower leg's first row
LEG_TOP = 85
# The run's own upper body (the user, 2026-10-11, with Viego's: 「慎的待机和跑步应该也不一样 我意思你顺便处理」 - the trot
# carried the idle's stance): he leans into the run, every row above the sash moved forward RUN_LEAN columns per row
# up from it (whole rows), the hood, his raised far arm with the sword and the near forearm moved whole (a sheared
# blade or hood gets steps) - the far arm with the hood it holds the hilt beside - and his near fist comes up before his
# chest: the bracer and the fist turned a quarter turn back about the elbow (rigkit.rot90: lossless), as League's Shen
# runs. Rows are the design's (before the 90% cut; run_upper maps them).
RUN_LEAN = 0.35
RUN_HEAD = {59: (60, 70), 60: (59, 71), 61: (59, 72), 62: (59, 73), 63: (60, 73), 64: (60, 72), 65: (60, 72),
            66: (60, 72), 67: (60, 72), 68: (61, 72), 69: (61, 72), 70: (61, 71)}
RUN_FAR = {54: (60, 62), 55: (59, 63), 56: (57, 63), 57: (55, 62), 58: (55, 62), 59: (54, 59), 60: (54, 58),
           61: (54, 58), 62: (54, 58), 63: (53, 59), 64: (53, 59), 65: (53, 59), 66: (53, 59), 67: (53, 59),
           68: (52, 59), 69: (51, 59), 70: (51, 58), 71: (50, 58), 72: (50, 57), 73: (49, 56), 74: (48, 55),
           75: (48, 54), 76: (47, 53), 77: (47, 52), 78: (47, 51), 79: (47, 51), 80: (47, 51), 81: (47, 51),
           82: (48, 51), 83: (48, 51), 84: (48, 50)}
RUN_NEAR = {77: (75, 78), 78: (74, 78), 79: (74, 81), 80: (72, 81), 81: (74, 83), 82: (75, 83), 83: (78, 82),
            84: (78, 82), 85: (80, 81)}           # the bracer and the fist (the bare upper arm ends on row 78)
NECK_ROW = 70                     # the hood's chin: the hood and the far arm move with this row's shift
NEAR_ELBOW = (74.5, 78.5)         # (x, y): the near forearm turns about it
EYE = (239, 226, 246)
OUTLINE = (11, 1, 15)              # the design's outline colour (palette()[0], its darkest)
SPECK = 4

# tag -> [(source, ms)]; a source is a Codex frame name (placed by ITS League frame) or ("sink", name, row, n): that
# frame with everything above `row` moved n rows down over the rest (a breath, nothing redrawn)
TAGS = {
    # the idle breathes without a cut: the body above the sash (and the whole near hand) sinks over the legs, which stay
    # square for square (import_native's idle_breathe cut two rows out of the trousers, boots, apron and tail hem)
    "idle": [(("breath", n), 140) for n in (0, 0, 1, 2, 2, 2, 1, 0)],
    "run": [(("trot", k), 100) for k in range(1, 9)],
    "attack": [(f"attack_{k}", ms) for k, ms in zip(range(1, 7), (50, 60, 60, 90, 80, 60))],
    # Q: Codex's four frames were four bodies (frame 4 tall and thin); the palm push is one drawing held
    # (League's Q starts from the idle pose: the design itself, so the cast starts without a jump)
    "skill": [("design", 60), ("skill_3", 240)],
    "skill2": [(f"skill2_{k}", ms) for k, ms in zip(range(1, 5), (50, 50, 100, 100))],
    # R: Codex's four channel frames were four different drawings (they flickered as a loop): the wind-up ends on
    # ult_2 (sword down, hands together before the chest) and the channel is that drawing breathing
    # (ult_3, the fists pushed forward, has a bare chest where the design wears its chest plate: left out). League's
    # R starts from the idle pose, and Codex's ult_1 was the idle redrawn (85 % on the design's squares, 15 % the same
    # colour, a two-row eye slit): the design itself, as for Q
    "ult": [("design", 150), ("ult_2", 150)],
    "ult_loop": [("ult_2", 300), (("sink", "ult_2", 84, 1), 300)],
    "hit": [("hit_1", 100)],
    "dead": [(f"dead_{k}", ms) for k, ms in zip(range(1, 9), (100, 100, 120, 150, 150, 200, 250, 400))],
}
# frames moved whole after placement (columns, rows)
NUDGE = {}
# eyes painted where Codex's glow did not survive the read (canvas row, column after placement): on the frame's skin
# eye slit, where Codex's raw has them (two in a front view, one in a side view)
EYES = {"skill_3": [(64, 67), (64, 68)], "attack_2": [(57, 58), (57, 60)], "skill2_3": [(77, 72)],
        "skill2_4": [(72, 74)], "dead_4": [(66, 64)], "dead_6": [(76, 73)], "dead_7": [(79, 69)]}
AIR = {"attack_3", "skill2_2", "skill2_3", "skill2_4"}   # off the ground: the lowest row stays where League's is
SQUARE = {}          # name -> square size in raw px, when the outline measure is off
# name -> extra scale factor: Codex drew these figures bigger on the canvas than the design (judged against the design's
# silhouette, soles aligned: work/sn/sizecheck_sn.py; the head template and mask measures were too noisy to trust)
FIX = {"skill_2": 0.92, "skill_3": 0.85, "skill_4": 0.9, "attack_1": 0.95, "attack_5": 0.88, "ult_1": 0.8, "skill2_1": 0.9, "ult_2": 0.95,
       "ult_3": 0.9, "ult_loop_2": 0.85, "ult_loop_3": 0.85, "ult_loop_4": 0.9, "hit_1": 0.8, "dead_1": 0.95,
       "dead_2": 0.95}


def lp(path):
    return R.lp(path)


def design():
    return np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))[::Z, ::Z].copy()


def palette(des):
    return np.array(sorted({tuple(int(v) for v in c[:3]) for c in des[des[..., 3] > 0]}), np.uint8)


SKIN = ((238, 169, 109), (182, 115, 70))


def glow(a):
    """Codex's glowing eyes, which the nearest-colour map would turn into the silver of the trims: light violet or
    white squares with skin right beside them (the eye slit), in the figure's upper part; at most the 4 of the row
    that has the most (the blade's lavender edge and the mask's rim are not eyes)."""
    c = a[..., :3].astype(int)
    op = a[..., 3] >= 128
    violet = op & (c[..., 2] - c[..., 1] > 25) & (c[..., 0] - c[..., 1] > 10) & (c.sum(-1) > 450)
    white = op & (c.min(-1) > 215)
    skinish = op & (c[..., 0] > 150) & (c[..., 0] - c[..., 2] > 50) & (c[..., 1] > 80)
    beside = np.zeros_like(op)
    for dx in (-2, -1, 1, 2):
        beside |= np.roll(skinish, dx, axis=1)
    cand = (violet | white) & beside
    ys = np.nonzero(op)[0]
    if not len(ys):
        return cand
    cand[int(ys.min() + 0.45 * (ys.max() - ys.min())):] = False
    if cand.sum() == 0:
        return cand
    row = int(np.argmax(cand.sum(1)))
    keep = np.zeros_like(cand)
    xs = np.nonzero(cand[row])[0]
    if len(xs) > 4:                      # the two most violet of them
        v = (c[row, xs, 2] - c[row, xs, 1]) + (c[row, xs, 0] - c[row, xs, 1])
        xs = xs[np.argsort(-v)[:2]]
    keep[row, xs] = True
    return keep


def pal_map(a, pal):
    """Every square to the nearest design colour (CIELAB) - never to the eye colour, which only glow() sets."""
    pal = np.array([c for c in pal if tuple(int(v) for v in c) != EYE], np.uint8)
    pl = R.lab(pal.astype(float))
    lab = R.lab(a[..., :3].astype(float))
    idx = ((lab[..., None, :] - pl[None, None]) ** 2).sum(-1).argmin(-1)
    out = np.zeros_like(a)
    out[..., :3] = pal[idx]
    out[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    out[glow(a)] = EYE + (255,)
    return out


def outline_square(a):
    """The silhouette's outer ring is one square of near-black: the median length of the dark runs that start at the
    transparent edge, along every row and column (the mean of the runs near that median)."""
    op = a[..., 3] >= 128
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    dark = op & (lum < 40)
    runs = []
    for o, dk in ((op, dark), (op.T, dark.T)):
        for r_op, r_dk in zip(o, dk):
            if r_op.sum() < 5:
                continue
            d = np.diff(r_op.astype(int))
            for e in np.nonzero(d == 1)[0] + 1:
                n = 0
                while e + n < len(r_dk) and r_dk[e + n]:
                    n += 1
                if 3 <= n <= 20:
                    runs.append(n)
            for e in np.nonzero(d == -1)[0]:
                n = 0
                while e - n >= 0 and r_dk[e - n]:
                    n += 1
                if 3 <= n <= 20:
                    runs.append(n)
    runs = np.array(runs, float)
    m = np.median(runs)
    return float(runs[(runs > m * 0.6) & (runs < m * 1.5)].mean())


def raw(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name + ".png"))).convert("RGBA"))


def read(name, pal):
    """The raw on its own grid, in the design's colours, cropped; and its square size."""
    a = raw(name)
    s = SQUARE.get(name) or outline_square(a.astype(float))
    rb, _, _ = regrid(a, s)
    return pal_map(R.crop(rb), pal), s


def weights(a):
    w = np.ones(a.shape[:2])
    eye = (a[..., :3] == EYE).all(-1) & (a[..., 3] > 0)
    w[eye] = 12
    lum = a[..., :3].astype(int).sum(-1)
    w[(lum > 560) & (a[..., 3] > 0)] = 3        # silver trims, the blade
    return w


def scale_to(a, f):
    """Whole rows and columns deleted evenly so the figure is f of its size (never two neighbouring lines, the eyes'
    rows and columns and the two lowest rows kept)."""
    if f >= 0.999:
        return a
    H, W = a.shape[:2]
    eye = (a[..., :3] == EYE).all(-1) & (a[..., 3] > 0)
    ey, ex = np.nonzero(eye)
    idx = a[..., 0].astype(np.int64) * 65536 + a[..., 1].astype(np.int64) * 256 + a[..., 2] + (a[..., 3] > 0) * 2 ** 25
    w = weights(a)
    R.JITTER = 1
    qr, qc = H - round(H * f), W - round(W * f)
    hr = set(ey.tolist()) | {H - 2, H - 1}
    dr = R.even_drop([idx[y] for y in range(H)], [w[y] for y in range(H)], 1, H - 3, qr, hr) if qr else []
    kr = [y for y in range(H) if y not in dr]
    a, idx, w = a[kr], idx[kr], w[kr]
    hc = set(ex.tolist())
    dc = R.even_drop([idx[:, x] for x in range(W)], [w[:, x] for x in range(W)], 1, W - 2, qc, hc) if qc else []
    kc = [x for x in range(W) if x not in dc]
    return a[:, kc]


def league(tag, cells):
    """League's frames of a tag at game size on our canvas (as the pack showed them) and their head columns."""
    cw, ch = cells["cell"]
    frs = cells["tags"][tag]
    nat = np.asarray(Image.open(os.path.join(POSE, f"shen_native_{tag}.png")).convert("RGBA"))
    cols = nat.shape[1] // (cw * Z)
    out = []
    for i, fr in enumerate(frs):
        X, Y = (i % cols) * cw * Z, (i // cols) * ch * Z
        g = nat[Y:Y + ch * Z, X:X + cw * Z][::Z, ::Z].copy()
        g[np.abs(g[..., :3].astype(int) - 225).sum(-1) < 12] = 0
        dx, dy = PIVOT[0] - fr["pivot"][0], PIVOT[1] - fr["pivot"][1]
        g = shift(g, dx, dy)
        out.append((g, fr["head"][0] + dx))
    return out


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys, ye = max(0, dy), min(H, H + dy)
    xs, xe = max(0, dx), min(W, W + dx)
    if ys < ye and xs < xe:
        out[ys:ye, xs:xe] = a[ys - dy:ye - dy, xs - dx:xe - dx]
    return out


def feet_mid(a, bottom):
    """Middle column of what stands on the lowest 3 rows."""
    xs = np.nonzero((a[max(bottom - 2, 0):bottom + 1, :, 3] > 0).any(0))[0]
    return (xs.min() + xs.max()) / 2


def place(fig, lol, ref, air=False):
    """fig (cropped) on the 128 canvas. Grounded: its lowest row on the soles' row; off the ground: on League's lowest
    row. Sideways: it moves from the design's stance as League's frame moves from League's idle (feet middles when
    grounded, middles of mass in the air) - so a pose that starts like the idle starts where the idle stands.
    ref = (League idle's feet middle, League idle's middle, the design's feet middle, the design's middle)."""
    l_feet, l_mid, d_feet, d_mid = ref
    ly = np.nonzero(lol[..., 3] > 0)
    if air:
        bottom = min(int(ly[0].max()), SOLES)
        tx = d_mid + float(ly[1].mean()) - l_mid
        fx = float(np.nonzero(fig[..., 3] > 0)[1].mean())
    else:
        bottom = SOLES
        tx = d_feet + feet_mid(lol, int(ly[0].max())) - l_feet
        fx = feet_mid(fig, fig.shape[0] - 1)
    x0 = int(round(tx - fx))
    y0 = bottom + 1 - fig.shape[0]
    can = np.zeros((128, 128, 4), np.uint8)
    H, W = fig.shape[:2]
    ys, xs = max(0, y0), max(0, x0)
    ye, xe = min(128, y0 + H), min(128, x0 + W)
    can[ys:ye, xs:xe] = fig[ys - y0:ye - y0, xs - x0:xe - x0]
    return can


def place_ref(des, cells):
    g = league("idle", cells)[0][0]
    ly = np.nonzero(g[..., 3] > 0)
    dy = np.nonzero(des[..., 3] > 0)
    return (feet_mid(g, int(ly[0].max())), float(ly[1].mean()), feet_mid(des, SOLES), float(dy[1].mean()))


def despeck(a):
    op = a[..., 3] > 0
    lab, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n <= 1:
        return a
    sizes = ndimage.sum(op, lab, range(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    near = ndimage.binary_dilation(lab == main, iterations=2)
    out = a.copy()
    for i, s in enumerate(sizes, 1):
        if i != main and s < SPECK and not (near & (lab == i)).any():
            out[lab == i] = 0
    return out


def close(a, pal):
    out, _, _ = strips.complete_outline(a, color=tuple(int(v) for v in pal[0]), feet=SOLES, keep=None)
    return out


def pinholes(a, most=2):
    """Enclosed transparent spots of at most `most` squares take their commonest opaque neighbour's colour."""
    op = a[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    out = a.copy()
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) > most:
            continue
        for y, x in zip(ys, xs):
            nb = [tuple(a[yy, xx]) for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
                  if 0 <= yy < 128 and 0 <= xx < 128 and a[yy, xx, 3] > 0]
            if nb:
                out[y, x] = max(set(nb), key=nb.count)
    return out


def finish(a, pal):
    return close(pinholes(a), pal)


def action_frame(name, tag, k, pal, lol, ref):
    fig, s = read(name, pal)
    f = s / CANVAS_SQUARE * FIX.get(name, 1.0)
    fig = R.crop(scale_to(fig, f))
    g, _ = lol[k - 1]
    a = despeck(place(fig, g, ref, name in AIR))
    if name in NUDGE:
        a = shift(a, *NUDGE[name])
    a = finish(a, pal)
    for y, x in EYES.get(name, ()):
        assert a[y, x, 3] > 0, (name, y, x)
        a[y, x] = EYE + (255,)
    return a, s, f


def masked(des, rows, cols_by_row):
    """The design's squares in the given rows, each row limited to its column range (inclusive)."""
    out = np.zeros_like(des)
    for y in rows:
        c0, c1 = cols_by_row(y)
        out[y, c0:c1 + 1] = des[y, c0:c1 + 1]
    return out


def trot_parts(des):
    """The design's run pieces: upper body, tail hem, apron, and each leg as thigh + lower leg."""
    tail = masked(des, range(LEG_TOP, 95), lambda y: (46, 53 if y >= 91 else 52))
    apron = masked(des, range(LEG_TOP, 94), lambda y: (62, 65 if y >= 91 else 67))
    far = masked(des, range(LEG_TOP, 100), lambda y: (68, 75) if y <= 90 else (66, 77))
    near = masked(des, range(LEG_TOP, 100),
                  lambda y: (53, 61) if y <= 90 else ((54, 59) if y <= 92 else ((53, 58) if y <= 94 else (51, 57))))
    upper = des.copy()
    upper[LEG_TOP:, :78] = 0
    upper[LEG_TOP + 2:] = 0
    tail_top, hem = tail.copy(), tail.copy()
    tail_top[KNEE_ROW:] = 0
    hem[:KNEE_ROW] = 0
    parts = {"tail_top": tail_top, "hem": hem, "apron": apron}
    # the upper body in the run's pieces: the hood, the far arm with the sword, the near forearm, the torso (the rest)
    torso = upper.copy()
    for name, spec in (("head", RUN_HEAD), ("far_arm", RUN_FAR), ("near_fore", RUN_NEAR)):
        piece = masked(torso, sorted(spec), lambda y: spec[y])
        torso[piece[..., 3] > 0] = 0
        parts[name] = piece
    parts["torso"] = torso
    for name, leg in (("near", near), ("far", far)):
        thigh, low = leg.copy(), leg.copy()
        thigh[KNEE_ROW:] = 0
        low[:KNEE_ROW] = 0
        parts[name + "_thigh"], parts[name + "_low"] = thigh, low
    return parts


def trot_layers(parts, k):
    """Frame k's pieces with their moves, back to front."""
    bob = TROT_BOB[k - 1]
    ndx, nup = NEAR_STEP[k - 1]
    fdx, fup = FAR_STEP[k - 1]
    # the tail hem's lower half (rows >= KNEE_ROW, beside the near boot) rises with the near lower leg, over the tail's
    # upper half: the cloth lifted by the knee. Lifted alone, the near boot ran over the hem's corner (or, behind it,
    # lost its ankle): 「右腿好了 左腿还有一点」. The tail's upper half sinks with the body.
    return [(parts["far_low"], fdx, -fup), (parts["far_thigh"], fdx, bob), (parts["tail_top"], ndx, bob),
            (parts["hem"], ndx, -nup), (parts["near_low"], ndx, -nup), (parts["near_thigh"], ndx, bob),
            (parts["apron"], 0, bob)] + [(c, 0, bob) for c in parts["run_upper"]]


def bare_outline_gone(a):
    """Outline squares with no colour beside them taken out (rigkit.orphan_outline, until none is left): the turned
    forearm's lower edge (its outline on the bracer's side) hung under the elbow as a stalk."""
    import rigkit as K
    a = a.copy()
    outline = tuple(int(v) for v in OUTLINE)
    while True:
        gone = K.orphan_outline(a, outline)
        if not gone.any():
            return a
        a[gone] = 0


def plan_point(plan, x, y):
    """A design point (x, y) on the 90% canvas: down one for every removed row under it, the removed columns between
    it and the pivot closing in."""
    rows = [CH + r for r in plan["rows"]]
    cols = [CW + c for c in plan["cols"]]
    y2 = y + sum(1 for r in rows if r > y)
    if x < CW:
        return x + sum(1 for c in cols if x < c < CW), y2
    return x - sum(1 for c in cols if CW < c <= x), y2


def run_upper(parts, plan):
    """The run's upper body on the 90% pieces, back to front: the far arm with the sword and the hood moved with the
    neck's shift, the torso leant row by row (RUN_LEAN), the near forearm turned up about the elbow, moved with the
    elbow's row."""
    import rigkit as K
    neck = plan_point(plan, CW, NECK_ROW)[1]
    leg = plan_point(plan, CW, LEG_TOP)[1]

    def lean(y):
        return int(math.floor((leg - max(y, neck)) * RUN_LEAN + 0.5)) if y < leg else 0

    torso = np.zeros_like(parts["torso"])
    for y in range(128):
        torso[y] = shift(parts["torso"][y:y + 1], lean(y), 0)[0]
    ex, ey = plan_point(plan, *NEAR_ELBOW)
    fore = parts["near_fore"]
    near = np.zeros_like(fore)
    K.place(near, K.rot90(K.Part.from_canvas(fore, fore[..., 3] > 0, (ex, ey)), 3), (ex + lean(int(ey)), ey))
    return [shift(parts["far_arm"], lean(neck), 0), torso, shift(parts["head"], lean(neck), 0), near]


SHRINK = 0.9                          # the user: 「慎的模型太大 缩小一点」 (46 rows -> 42, like Talon and Olaf)
SHRINK_KEEP = ["!EFE2F6+3,5,4,4"]     # no line through the eyes and the mask
SHRINK_ANCHOR = "EFE2F6"
CH, CW = 88, 64                       # the pivot: the centre of the pivot-centred arrays shrink_frames works on


def to_c(a):
    """A 128 x 128 canvas (pivot 64, 88) as a pivot-centred array (177 x 129)."""
    out = np.zeros((2 * CH + 1, 2 * CW + 1, 4), np.uint8)
    out[:128, :128] = a
    return out


def from_c(arr):
    h, w = arr.shape[0] // 2, arr.shape[1] // 2
    can = np.zeros((128, 128, 4), np.uint8)
    r0, c0 = CH - h, CW - w
    rs, cs = slice(max(0, r0), min(128, r0 + arr.shape[0])), slice(max(0, c0), min(128, c0 + arr.shape[1]))
    can[rs, cs] = arr[rs.start - r0:rs.stop - r0, cs.start - c0:cs.stop - c0]
    return can


def design_plan(des):
    """The lines the design loses (shrink_frames.plan_tag on the design alone): applied to the design AND to each of
    its moving parts, so a part keeps its exact squares in every frame it is moved in (the import's shrink cut the
    moving legs at fixed canvas columns: a different column of the leg in every frame - 「还有轻微的变形」)."""
    import shrink_frames as SF
    fr = [(to_c(des), 160)]
    body = SF.body_of(fr)
    return SF.plan_tag(fr, body, SHRINK, keep_colours=SHRINK_KEEP), body


def shrunk(a, plan):
    import shrink_frames as SF
    return from_c(SF.apply_tag([(to_c(a), 100)], plan)[0][0])


def shrunk_row(plan, y):
    """Canvas row y of the design after the plan (rows removed above it move it up)."""
    return y - sum(1 for r in plan["rows"] if CH + r < y)


def shrink_tag(frames, body, anchor=SHRINK_ANCHOR):
    """Codex's frames of one action shrunk together (one plan, the lines following the eyes; not in the death, where
    the lying frames' eyes sit low or are gone and the offset lines fell under the soles). A frame whose lowest row
    ended under the soles (an empty line removed below the figure moved its pivot) is moved back up whole."""
    import shrink_frames as SF
    sheet = {"t": [(to_c(a), ms) for a, ms in frames]}
    SF.shrink_sheet(sheet, SHRINK, body=body, keep_colours=SHRINK_KEEP, anchor=anchor)
    out = []
    for a, ms in sheet["t"]:
        a = from_c(a)
        low = int(np.nonzero(a[..., 3].any(1))[0].max())
        if low > SOLES:
            a = shift(a, 0, SOLES - low)
        out.append((a, ms))
    return out


def breath_parts(des):
    """The idle's breathing body (rows < BREATH_ROW, the near hand down to HAND_END) and what stays (the legs)."""
    up = des.copy()
    up[BREATH_ROW:, :HAND_COL] = 0
    up[HAND_END:] = 0
    low = des.copy()
    low[:BREATH_ROW] = 0
    low[BREATH_ROW:HAND_END, HAND_COL:] = 0
    return up, low


def compose(parts):
    can = np.zeros((128, 128, 4), np.uint8)
    for part, dx, dy in parts:
        p = shift(part, dx, dy)
        m = p[..., 3] > 0
        can[m] = p[m]
    can[SOLES + 1:] = 0
    return can


def sink(a, row, n):
    """Everything above `row` n rows lower, over what is below (moved, not redrawn)."""
    up = a.copy()
    up[row:] = 0
    out = a.copy()
    out[:row] = 0
    up = shift(up, 0, n)
    m = up[..., 3] > 0
    out[m] = up[m]
    return out


BREATH_ROW, HAND_COL, HAND_END = 85, 76, 89   # the sash's underside; the near hand (cols >= 76, above row 89)


def breath(des, n):
    """The design with its body (rows < BREATH_ROW and the near hand) n rows lower over its legs."""
    if not n:
        return des.copy()
    up = des.copy()
    up[BREATH_ROW:, :HAND_COL] = 0
    up[HAND_END:] = 0
    out = des.copy()
    out[:BREATH_ROW] = 0
    out[BREATH_ROW:HAND_END, HAND_COL:] = 0
    up = shift(up, 0, n)
    m = up[..., 3] > 0
    out[m] = up[m]
    return out


def source_of(name):
    tag, k = name.rsplit("_", 1)
    return tag, int(k)


def build(only=None):
    des = design()
    pal = palette(des)
    lols, cache, sheet, info, lol = {}, {}, {}, {}, {}

    def league_cells():
        """League's renders (POSE) are read only for a Codex frame: --only run / idle build without them."""
        if not lol:
            lol["cells"] = json.load(open(os.path.join(POSE, "shen_cells.json"), encoding="utf-8"))
            lol["ref"] = place_ref(des, lol["cells"])
        return lol["cells"], lol["ref"]

    def frame(name):
        if name not in cache:
            tag, k = source_of(name)
            cells, ref = league_cells()
            if tag not in lols:
                lols[tag] = league(tag, cells)
            a, s, f = action_frame(name, tag, k, pal, lols[tag], ref)
            cache[name] = a
            info[name] = (s, f)
        return cache[name]

    plan, body0 = design_plan(des)
    des90 = shrunk(des, plan)
    up, low = breath_parts(des)
    up90, low90 = shrunk(up, plan), shrunk(low, plan)
    run_parts = {n: shrunk(p, plan) for n, p in trot_parts(des).items()}
    run_parts["run_upper"] = run_upper(run_parts, plan)
    for tag, rows in TAGS.items():
        if only and tag not in only:
            continue
        frames, codex = [], []
        for k, (src, ms) in enumerate(rows, 1):
            if src == "design":
                a = des90
            elif isinstance(src, tuple) and src[0] == "breath":
                a = compose([(low90, 0, 0), (up90, 0, src[1])])
            elif isinstance(src, tuple) and src[0] == "trot":
                a = bare_outline_gone(compose(trot_layers(run_parts, src[1])))
            elif isinstance(src, tuple) and src[0] == "sink":
                a = ("sink", src[1], src[2], src[3])
            else:
                a = ("codex", src)
                codex.append((frame(src), ms))
            frames.append((a, ms))
        done = {}
        if codex:
            names = [f[0][1] for f in frames if isinstance(f[0], tuple) and f[0][0] == "codex"]
            for name, (a, _) in zip(names, shrink_tag(codex, body0, None if tag == "dead" else SHRINK_ANCHOR)):
                done[name] = a
        out = []
        for a, ms in frames:
            if isinstance(a, tuple) and a[0] == "codex":
                a = done[a[1]]
            elif isinstance(a, tuple) and a[0] == "sink":
                srcf = done.get(a[1]) if a[1] in done else shrink_tag([(frame(a[1]), 100)], body0)[0][0]
                a = sink(srcf, shrunk_row(plan, a[2]), a[3])
            out.append((a, ms))
        sheet[tag] = out
    return sheet, info


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def write(sheet):
    cells = {"cell": [128, 128], "scale": Z, "tags": {}}
    path = lp(os.path.join(OUT, "shen_cells.json"))
    if os.path.exists(path):        # --only rebuilds some tags: keep the others' cells, in TAGS order
        with open(path, encoding="utf-8") as f:
            old = json.load(f)["tags"]
        cells["tags"] = {t: old[t] for t in TAGS if t in old and t not in sheet}
    for tag, frames in sheet.items():
        cols, rows = layout(len(frames))
        strip = np.zeros((rows * 128, cols * 128, 4), np.uint8)
        for k, (a, ms) in enumerate(frames):
            r, c = divmod(k, cols)
            strip[r * 128:(r + 1) * 128, c * 128:(c + 1) * 128] = a
        Image.fromarray(strip).resize((cols * 128 * Z, rows * 128 * Z), Image.NEAREST).save(
            lp(os.path.join(OUT, f"shen_{tag}.png")))
        cells["tags"][tag] = [{"pivot": list(PIVOT), "ms": ms} for _, ms in frames]
    cells["tags"] = {t: cells["tags"][t] for t in TAGS if t in cells["tags"]}
    with open(lp(os.path.join(OUT, "shen_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write("{" + json.dumps({"cell": cells["cell"], "scale": Z})[1:-1] + ', "tags": {\n')
        f.write(",\n".join(f'  "{t}": ' + json.dumps(v) for t, v in cells["tags"].items()))
        f.write("\n}}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--review", help="write <tag>_<k>.png (128 x 128) here instead of the strips")
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    sheet, info = build(a.only)
    for name, (s, f) in info.items():
        print(f"{name:12s} square {s:5.2f}  scale {f:.2f}")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for tag, frames in sheet.items():
            for k, (fr, _) in enumerate(frames):
                Image.fromarray(fr).save(os.path.join(a.review, f"{tag}_{k + 1}.png"))
        print("review frames in", a.review)
        return
    write(sheet)
    print("wrote", ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
