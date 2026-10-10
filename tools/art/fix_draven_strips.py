#!/usr/bin/env python3
"""Draven's action strips from Codex's step-2 frames (assets/source/draven/codex_strips) + the approved design.

    python tools/art/fix_draven_strips.py [--run M|V] [--review DIR]

Writes assets/source/native/draven_<tag>.png (every frame a 128 x 128 canvas cell at 8x, the soles on row 99, the
standing point on column 64) and draven_cells.json; then tools/art/import_native.py --hero draven.

Codex drew every frame as one image after League's pose (STRIPS_PROMPTS: assets/source/draven/MODEL_STRIPS.md). The
user on the delivery (2026-10-10): 「Codex做的东西有点奇怪 请你帮忙修复」 and, on the run, 「我记得德莱文在联盟里的走路
姿势不是这样的」. What was off, and what this script does about it:
  - run: the pack kept the design's upper body (the far axe raised over the head) and asked only for the legs - League
    runs (and oppi's Draven runs) with both axes held low at his sides. RUN: the design's head, mantle, torso and near
    arm square for square, the far arm and its axe brought down (variant "M": the near arm + axe mirrored onto the far
    shoulder - both axes low at the sides like oppi's run; "V": the raised arm flipped upside down about the shoulder),
    Codex's crossing legs (it drew them into the pack's boot boxes) under it, the upper body bobbing BOB rows.
  - skill (Q, 4 x 50 ms): Codex redrew the whole body every frame (one frame 1.7 times the design, the raised arm on
    the other side in another) - it flickered. SPIN: the design itself, its raised axe spinning in the fist (lossless
    quarter turns about the fist, behind the body), the way oppi's Q keeps the body still.
  - attack: Codex raised the FAR axe in frames 2-3 and threw with the NEAR hand in frame 4, frame 5 had the axes in
    the other hands again and frame 6 mirrored the design. ATTACK: frame 1 (crouch, both axes low), frame 6 (the near
    axe raised - the wind-up for the near hand), frame 4 (the throw, the near hand empty), then the idle.
  - skill2 / ult: their last frame was the design mirrored (attack 6, skill2 6) or another man (ult 7, slim, front-on,
    no axes): dropped, the previous frame held longer.
  - dead: the three lying frames were three different jumbles: frame 4 held for all of them.
Timings: the release frames start where the kit fires (attack 180 ms = tick 11, E 180 ms = tick 11, R 270 ms = tick 16).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "assets", "source", "draven", "codex_strips", "1x")
DESIGN = os.path.join(ROOT, "assets", "source", "native", "draven_native.png")
OUT = os.path.join(ROOT, "assets", "source", "native")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
Z = 8
SOLES, MID = 99, 64
PIVOT = (MID, SOLES - 11)          # 11 rows over the soles, as tools/lol/native_pose.py puts it
BOB = [0, 1, 1, 0, 0, 1, 1, 0]     # the run's upper body (the pack's a_upper_body.png per frame)
HIP_ROW, AXE_X, AXE_LOW = 81, 80, 93   # the pack kept the design's rows < 81 and the near axe (rows 81-93, cols >= 80)

# (tag, [(source, ms)]): a source is a Codex frame name, "design", ("spin", quarter turns) or ("run", k)
TAGS = {
    "idle": [("design", 140)],
    "run": [(("run", k), 100) for k in range(8)],
    "attack": [("attack_1", 80), ("attack_6", 100), ("attack_4", 220)],
    "skill": [(("spin", 1), 50), (("spin", 2), 50), (("spin", 3), 50), ("design", 50)],
    "skill2": [("skill2_1", 60), ("skill2_2", 60), ("skill2_3", 60), ("skill2_4", 80), ("skill2_5", 140)],
    "ult": [("ult_1", 60), ("ult_2", 70), ("ult_3", 70), ("ult_4", 70), ("ult_5", 80), ("ult_6", 150)],
    "hit": [("hit_1", 100)],
    "dead": [("dead_1", 100), ("dead_2", 100), ("dead_3", 120), ("dead_4", 750)],
}


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    a = np.asarray(Image.open(lp(path)).convert("RGBA"))
    a = a[Z // 2::Z, Z // 2::Z] if a.shape[0] == 128 * Z else a
    a = a.copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] >= 128, 3] = 255
    return a


def box(a, rows, cols):
    m = np.zeros(a.shape[:2], bool)
    m[rows[0]:rows[1] + 1, cols[0]:cols[1] + 1] = True
    return m & (a[..., 3] > 0)


# ---------------------------------------------------------------- the design's parts (canvas rows / columns)
def far_arm(d):
    """The raised far arm with its axe: the axe and fist (rows 46-62 left of the head), the wrap and the upper arm
    down to the shoulder (rows 63-69, left of the mantle's teal/fur)."""
    m = box(d, (46, 62), (36, 57))
    m |= box(d, (63, 64), (36, 54))
    m |= box(d, (65, 65), (36, 53)) | box(d, (66, 66), (36, 52)) | box(d, (67, 67), (36, 53))
    m |= box(d, (68, 69), (36, 52))
    return m


def far_axe(d):
    """The raised axe alone (the fist and wrist, rows 56-62 columns 47-53, stay with the arm)."""
    return box(d, (46, 55), (36, 57)) | box(d, (56, 62), (36, 46))


FAR_FIST = (48.5, 56.5)            # the far fist's middle (both halves: a quarter turn maps squares onto squares)


def near_arm(d):
    """The near arm (upper arm from the mantle's edge, forearm, fist) with its axe - without the near leg's outline
    squares the box catches (pieces under 10 squares)."""
    m = box(d, (72, 83), (72, 84)) | box(d, (73, 93), (78, 91))
    lab, n = ndimage.label(m, structure=np.ones((3, 3)))
    for i in range(1, n + 1):
        if (lab == i).sum() < 10:
            m[lab == i] = False
    return m


M_ARM = (-4, -2)                   # the mirrored far arm's place: its skin upper arm shows left of the mantle


def TASSEL(d):
    """The crimson cloth hanging behind the far shoulder."""
    return box(d, (71, 80), (44, 55))


def turn(part, mask, centre, q):
    """`part` (masked) turned q quarter turns clockwise on screen about centre (x, y): lossless."""
    out = np.zeros_like(part)
    om = np.zeros(mask.shape, bool)
    cx, cy = centre
    for y, x in zip(*np.nonzero(mask)):
        dx, dy = x - cx, y - cy
        for _ in range(q % 4):
            dx, dy = -dy, dx
        X, Y = int(round(cx + dx)), int(round(cy + dy))
        if 0 <= X < 128 and 0 <= Y < 128:
            out[Y, X] = part[y, x]
            om[Y, X] = True
    return out, om


def flip(part, mask, axis, at):
    """Mirrored about column `at` (axis "h") or row `at` (axis "v")."""
    out = np.zeros_like(part)
    om = np.zeros(mask.shape, bool)
    for y, x in zip(*np.nonzero(mask)):
        X, Y = (2 * at - x, y) if axis == "h" else (x, 2 * at - y)
        if 0 <= X < 128 and 0 <= Y < 128:
            out[Y, X] = part[y, x]
            om[Y, X] = True
    return out, om


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys0, ys1 = max(0, dy), min(H, H + dy)
    xs0, xs1 = max(0, dx), min(W, W + dx)
    out[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


def over(dst, src):
    """src drawn over dst (src's opaque squares win)."""
    out = dst.copy()
    m = src[..., 3] > 0
    out[m] = src[m]
    return out


# ---------------------------------------------------------------- Q: the raised axe spinning in the fist
def spin(d, q):
    """The design with its raised axe turned q quarter turns about the fist, drawn behind the body."""
    ax = far_axe(d)
    body = d.copy()
    body[ax] = 0
    part = np.zeros_like(d)
    part[ax] = d[ax]
    t, tm = turn(part, ax, FAR_FIST, q)
    return over(t, body)


# ---------------------------------------------------------------- the run
def run_upper(d, variant):
    """The run's upper body: the design without its raised far arm, the far arm + axe brought down, the legs gone
    (everything under the belt but the near axe)."""
    fm = far_arm(d)
    body = d.copy()
    body[fm] = 0
    if variant == "V":                                   # the raised arm flipped upside down about the shoulder row
        part = np.zeros_like(d)
        part[fm] = d[fm]
        arm, am = flip(part, fm, "v", 70)
    else:                                                # the near arm + axe mirrored onto the far shoulder
        nm = near_arm(d)
        part = np.zeros_like(d)
        part[nm] = d[nm]
        arm, am = flip(part, nm, "h", 64)
        arm = shift(arm, *M_ARM)
        # the crimson cloth hanging behind the far shoulder goes under the arm (over it, the arm's skin was hidden
        # and only its red wrap showed: a red stump)
        cloth = TASSEL(d)
        under = np.zeros_like(d)
        under[cloth] = d[cloth]
        body[cloth] = 0
        arm = over(under, arm)
    legs = np.zeros(d.shape[:2], bool)
    legs[HIP_ROW:] = True
    legs[HIP_ROW:AXE_LOW + 1, AXE_X:] = False
    body[legs] = 0
    return arm, body


def codex_legs(d, k):
    """Codex's legs in run frame k: its frame minus the pack's upper body (the design's rows < 81 and the near axe,
    moved down BOB[k]) wherever that upper body is opaque and Codex kept it."""
    fr = load(os.path.join(SRC, f"run_{k + 1}.png"))
    up = d.copy()
    keep = np.zeros(d.shape[:2], bool)
    keep[:HIP_ROW] = True
    keep[HIP_ROW:AXE_LOW + 1, AXE_X:] = True
    up[~keep] = 0
    up = shift(up, 0, BOB[k])
    same = (up[..., 3] > 0) & (fr == up).all(-1)
    legs = fr.copy()
    legs[same] = 0
    return legs


WAIST = (70, 92, 44, 64)           # rows, columns by the far hip: gaps there are closed with the trousers' shadow
SHADOW = (0x29, 0x2A, 0x32)


RAW = os.path.join(ROOT, "assets", "source", "draven", "codex_strips", "raw")
PITCH = 1254 / 128                 # the generator drew the 1024 canvas at 1254 px: one game square = 9.8 px


def raw_legs(d, k):
    """The legs as the generator drew them in run frame k (raw/run_<k>.png read on the 128 grid: each square the
    median of its middle 3 x 3, the nearest design colour in CIELAB) - Codex's own 1x had moved and resampled them
    into the pack's boot boxes, which broke them into thin specks (the user: 「腿部严重变形」). Everything under the
    belt but the near axe, lifted so the soles stand on row 99."""
    import design_rengar as R
    pal = np.unique(d[d[..., 3] > 0][:, :3], axis=0)
    pl = R.lab(pal.astype(float))
    im = np.asarray(Image.open(lp(os.path.join(RAW, f"run_{k + 1}.png"))).convert("RGBA")).astype(float)
    a = np.zeros((128, 128, 4), np.uint8)
    for y in range(HIP_ROW - 2, 128):
        for x in range(128):
            cy, cx = int((y + 0.5) * PITCH), int((x + 0.5) * PITCH)
            if not (1 <= cy < im.shape[0] - 1 and 1 <= cx < im.shape[1] - 1):
                continue
            blk = im[cy - 1:cy + 2, cx - 1:cx + 2].reshape(-1, 4)
            if (blk[:, 3] >= 128).mean() < 0.5:
                continue
            c = np.median(blk[blk[:, 3] >= 128][:, :3], axis=0)
            a[y, x, :3] = pal[((R.lab(c[None]) - pl) ** 2).sum(-1).argmin()]
            a[y, x, 3] = 255
    b = BOB[k]
    a[:HIP_ROW + b] = 0
    a[:AXE_LOW + b + 1, AXE_X:] = 0
    ys = np.nonzero(a[..., 3])[0]
    return shift(a, 0, SOLES - ys.max()) if len(ys) and ys.max() > SOLES else a


# the raw legs of frames 1-4 make one whole stride (the near foot lands in 4, pushes back through 1-2, swings in 3;
# the far one lands in 3, pushes back in 4, kicks up in 1, swings in 2); frames 5-8 kept both feet where 1-4 had
# them (no swap), so the run plays 1-4 twice (two legs alike: a stride and its half-cycle twin look the same)
LEG_SRC = [0, 1, 2, 3, 0, 1, 2, 3]
LEGS = "rig"                       # "rig": rig_draven_legs.py on League's skeleton; "raw": the generator's legs


RIBBONS = (80, 93, 57, 67)          # rows, columns: the belt's ribbons hanging between the legs in the design
RIBBON_COLOURS = {(0xCA, 0x22, 0x4A), (0x74, 0x23, 0x42), (0x9C, 0x34, 0x4C), (0x08, 0x70, 0x82), (0x06, 0x48, 0x53),
                  (0x42, 0x1D, 0x30), (0x1A, 0x0E, 0x0E)}


def ribbons(d):
    """The design's ribbons under the belt (crimson, teal and their outline), drawn over the rigged legs."""
    r0, r1, c0, c1 = RIBBONS
    out = np.zeros_like(d)
    for y in range(r0, r1 + 1):
        for x in range(c0, c1 + 1):
            if d[y, x, 3] and tuple(int(v) for v in d[y, x, :3]) in RIBBON_COLOURS:
                out[y, x] = d[y, x]
    return out


# ---------------------------------------------------------------- the run Codex redrew whole (codex_run/)
RUN2 = os.path.join(ROOT, "assets", "source", "draven", "codex_run", "1x")
# design head (canvas rows, first/last column): hair crest, headband, face, moustache, beard down to the scarf
HEAD_ROWS = {60: (57, 67), 61: (57, 67), 62: (57, 67), 63: (57, 67), 64: (59, 67), 65: (59, 66), 66: (60, 66),
             67: (59, 66), 68: (58, 66)}
GOLD = (0xF3, 0xCB, 0x57)
AXE8 = ((78, 92), (29, 47), (1, 1))   # run 8's smeared far axe: rows, columns of run 4's, moved (dx, dy)


def head_mask(d):
    m = np.zeros(d.shape[:2], bool)
    for y, (c0, c1) in HEAD_ROWS.items():
        m[y, c0:c1 + 1] = True
    return m & (d[..., 3] > 0)


HAIR = {(0x74, 0x23, 0x42), (0x6B, 0x34, 0x3D), (0x42, 0x1D, 0x30), (0x9C, 0x34, 0x4C)}


def band(a):
    """Where the head is: (the hair crest's top row, the middle column of the hair in its top 4 rows), searched in
    columns 56-78 (the design's raised axe ends at column 57; the run's axes hang lower, at the sides)."""
    win = a[40:75, 56:79]
    op = win[..., 3] > 0
    rows = np.nonzero(op.any(1))[0]
    top = rows.min()
    hair = np.array([[tuple(int(v) for v in win[y, x, :3]) in HAIR and op[y, x] for x in range(win.shape[1])]
                     for y in range(top, top + 4)])
    xs = np.nonzero(hair)[1]
    return 40 + top, 56 + xs.mean()


def run2_frame(d, k):
    """Codex's whole-figure run frame k with the design's own head put on Codex's (found by the headband), run 8's
    smeared far axe replaced by run 4's, and the frame moved sideways so the head stands on the design's column."""
    a = load(os.path.join(RUN2, f"run_{k + 1}.png"))
    if k == 7:
        b = load(os.path.join(RUN2, "run_4.png"))
        (r0, r1), (c0, c1), (dx, dy) = AXE8
        a[r0 + dy:r1 + dy + 1, c0 + dx:c1 + dx + 1] = 0
        part = b[r0:r1 + 1, c0:c1 + 1]
        m = part[..., 3] > 0
        a[r0 + dy:r1 + dy + 1, c0 + dx:c1 + dx + 1][m] = part[m]
    dr, dc = band(d)
    fr, fc = band(a)
    dy, dx = fr - dr, int(round(fc - dc))
    # Codex's head out: the hair above the mantle, the face's columns down to the beard
    for y in range(54 + dy, 63 + dy):
        a[y, 55 + dx:71 + dx] = 0
    for y in range(63 + dy, 69 + dy):
        a[y, 58 + dx:68 + dx] = 0
    hm = head_mask(d)
    head = np.zeros_like(d)
    head[hm] = d[hm]
    a = over(a, shift(head, dx, dy))
    return shift(a, -dx, 0)          # the head on the design's column: the body moves with it


def run_frame(d, k, variant):
    arm, body = run_upper(d, variant)
    if LEGS == "rig":
        import rig_draven_legs as RL
        legs = over(RL.legs(k), shift(ribbons(d), 0, BOB[k]))
    else:
        legs = raw_legs(d, LEG_SRC[k])
    up = over(shift(arm, 0, BOB[k]), shift(body, 0, BOB[k]))   # the body over the far arm's root
    fr = over(legs, up)
    # Codex's hips were drawn for the raised-arm body: lowered, the far arm closes a pocket by the far hip in the
    # bobbing frames - the far hip's shadow fills it (the axes' ring holes stay open)
    op = fr[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lab, n = ndimage.label(holes)
    r0, r1, c0, c1 = WAIST
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) >= 3 and r0 <= ys.min() and ys.max() <= r1 and c0 <= xs.min() and xs.max() <= c1:
            fr[ys, xs, :3] = SHADOW
            fr[ys, xs, 3] = 255
    return fr


# ---------------------------------------------------------------- 90 % (the user 10-10: 「模型可以适当缩小点」, picked 90 %)
SCALE = 0.9
CREST = 60                          # the design's hair crest row: its body, crest to soles, 40 rows -> 36
BODY_COLS = (38, 89)                # its columns, both axes included: 52 -> 47
SKIN = ["D59660", "F0AF76", "FFCF94", "AF714D"]
SHRINK_TAGS = ("run", "skill2", "ult", "dead")


def head_box(a, d):
    """(top, bottom, left, right) of the design's head in frame a: where the most of its squares (HEAD_ROWS) match
    colour for colour - 77 of 77 where the head is pasted, 16-47 in Codex's own heads (every action frame's box was
    checked by eye, 2026-10-10)."""
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    t0, b0, l0, r0 = ys.min(), ys.max(), xs.min(), xs.max()
    key = lambda x: (x[..., 0].astype(np.int32) << 16) | (x[..., 1].astype(np.int32) << 8) | x[..., 2]
    pk, pm = key(d[t0:b0 + 1, l0:r0 + 1]), hm[t0:b0 + 1, l0:r0 + 1]
    ak, op = key(a), a[..., 3] > 0
    h, w = pk.shape
    best = (-1, 0, 0)
    for y in range(0, 128 - h):
        for x in range(0, 128 - w):
            s = int(((ak[y:y + h, x:x + w] == pk) & pm & op[y:y + h, x:x + w]).sum())
            if s > best[0]:
                best = (s, y, x)
    _, y, x = best
    return y, y + h - 1, x, x + w - 1


def shrink_plan(frames, heads, scale=SCALE):
    """The rows and columns each frame of an action loses (canvas lines): (1 - scale) of the frame's own height and
    width (a lying body loses rows of its thickness, not 4), in as many equal stretches of it, in each the line most
    like its neighbour over the whole action (shrink_frames' costs: a hand, an eye, any small piece dearer; so the
    frames of an action lose the same parts of him), never the head (its box + 1), the soles' two rows, the pivot
    row, the standing column, the figure's two outermost lines or a line with none of that frame's squares - such a
    pick moves to the nearest free line. Every head stays square for square."""
    import shrink_frames as SF
    st = np.stack(frames)
    det = SF._details(st)
    rc = SF._diff(st, 1) + SF.DETAIL_WEIGHT * det.sum((0, 2))
    cc = SF._diff(st, 2) + SF.DETAIL_WEIGHT * det.sum((0, 1))
    kept = SF._kept(st, SKIN)
    kr0, kc0 = kept.sum((0, 2)), kept.sum((0, 1))
    big, cut = 10 ** 6, 1 - scale
    out = []
    for a, (t, b, l, r) in zip(frames, heads):
        op = a[..., 3] > 0
        fr, fc = op.any(1), op.any(0)
        ys, xs = np.nonzero(fr)[0], np.nonzero(fc)[0]
        top, left, right = ys.min(), xs.min(), xs.max()
        bad_r = set(range(t - 1, b + 2)) | {SOLES, SOLES - 1, PIVOT[1], top, top + 1} | set(np.nonzero(~fr)[0])
        bad_c = set(range(l - 1, r + 2)) | {MID, left, left + 1, right - 1, right} | set(np.nonzero(~fc)[0])
        kr, kc = kr0.copy(), kc0.copy()
        kr[list(bad_r)] += big
        kc[list(bad_c)] += big
        n_r = int(round(cut * (SOLES - top + 1)))
        n_c = int(round(cut * (right - left + 1)))
        nl = int(round(n_c * (MID - left) / max(1, right - left)))
        r_pick = SF._pick(rc, top, SOLES, n_r, keep=kr)
        c_pick = SF._pick(cc, left, MID, nl, keep=kc) + SF._pick(cc, MID + 1, right + 1, n_c - nl, keep=kc)

        def move(picks, bad, lo, hi, cost):
            picks = list(picks)
            for j, i in enumerate(picks):
                if i not in bad:
                    continue
                free = [c for c in range(lo, hi + 1) if c not in bad and c not in picks
                        and (c - 1) not in picks and (c + 1) not in picks]
                if free:
                    picks[j] = min(free, key=lambda c: (abs(c - i) // 4, cost[c]))
            return sorted(picks)
        out.append((move(r_pick, bad_r, top, SOLES, rc), move(c_pick, bad_c, left, right, cc)))
    return out


def shrink_apply(a, rows, cols):
    """Frame a without those rows and columns: what is over a removed row comes down one (the soles stay on row 99),
    what is beside a removed column closes in on the standing column."""
    out = np.zeros_like(a)
    ys, xs = np.nonzero(a[..., 3] > 0)
    for y, x in zip(ys, xs):
        if y in rows or x in cols:
            continue
        ny = y + sum(1 for r in rows if r > y)
        nx = x + sum(1 for c in cols if x < c < MID) if x < MID else x - sum(1 for c in cols if MID < c < x)
        out[ny, nx] = a[y, x]
    return out


def shrink(sheet, d, tags=SHRINK_TAGS):
    """The tags made SCALE as big, without resampling; returns {tag: [(rows, cols) per frame]}."""
    plans = {}
    for tag in tags:
        frames = [a for a, _ in sheet[tag]]
        plans[tag] = shrink_plan(frames, [head_box(a, d) for a in frames])
        sheet[tag] = [(shrink_apply(a, *p), ms) for (a, ms), p in zip(sheet[tag], plans[tag])]
    return plans


# ---------------------------------------------------------------- the strips
# ---------------------------------------------------------------- League's idle and attack at 90 % (codex_pose/)
# the user 10-10: 「另外待机姿势能改成和英雄联盟一样吗 攻击姿势也是」 - Codex redrew the idle (both axes low, League's
# draven_idle1) and the attack (League's attack1 at 0/100/190/270/420 ms) at 36 rows (assets/source/draven/POSE_REDO.md)
POSE = os.path.join(ROOT, "assets", "source", "draven", "codex_pose", "1x")
POSE_ATTACK = [50, 60, 73, 117, 100]       # the release frame (4) starts at 183 ms = tick 11, the kit's a_st
HIT_BACK = 2                              # the hit: the new idle stepped back this many columns (Talon's way)


POSE_HEAD = {"attack_2": (63, 57)}         # (row, column) of the head's box where the match missed (tilted back)
POSE_SOLES = {"attack_5": 2}               # Codex left its soles this many rows low (its HANDOFF): lifted, then
POSE_ROWS = {"attack_5": 2}                # this many rows out (38 -> 36, not through the head)
OUTLINE = (0x1A, 0x0E, 0x0E)


def pose_frame(d, name):
    """Codex's frame `name` with the design's own head on the head it drew (head_box, or POSE_HEAD): Codex's hair
    squares outside it (its crest drawn taller or wider, rows over the headband) cleared and the outline they leave
    bordering nothing; every head then the same. attack_5 lifted and two rows shorter (POSE_SOLES, POSE_ROWS)."""
    a = load(os.path.join(POSE, f"{name}.png"))
    if name in POSE_SOLES:
        a = shift(a, 0, -POSE_SOLES[name])
    t, b, l, r = head_box(a, d)
    if name in POSE_HEAD:
        t, l = POSE_HEAD[name]
        b, r = t + (b - t), l + (r - l)
    hm = head_mask(d)
    ys, xs = np.nonzero(hm)
    head = np.zeros_like(d)
    head[hm] = d[hm]
    head = shift(head, l - xs.min(), t - ys.min())
    on = head[..., 3] > 0
    rows, cols = range(max(0, t - 6), t + 5), range(max(0, l - 3), min(128, r + 4))
    for y in rows:
        for x in cols:
            if not on[y, x] and a[y, x, 3] and tuple(int(v) for v in a[y, x, :3]) in HAIR:
                a[y, x] = 0
    for _ in range(3):
        for y in rows:
            for x in cols:
                if on[y, x] or not a[y, x, 3] or tuple(int(v) for v in a[y, x, :3]) != OUTLINE:
                    continue
                if not any(0 <= v < 128 and 0 <= u < 128 and (on[v, u] or a[v, u, 3] and
                                                              tuple(int(c) for c in a[v, u, :3]) != OUTLINE)
                           for v, u in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1))):
                    a[y, x] = 0
    a = over(a, head)
    if name in POSE_ROWS:
        a = shrink_rows(a, POSE_ROWS[name], (t, b, l, r))
    return a


def shrink_rows(a, n, hb):
    """Frame a n rows shorter: the n rows most like their neighbours between the head and the soles (shrink_frames'
    costs), never the head's (+1), the pivot row or the soles' two."""
    import shrink_frames as SF
    st = a[None]
    rc = SF._diff(st, 1) + SF.DETAIL_WEIGHT * SF._details(st).sum((0, 2))
    keep = np.zeros(128, np.int64)
    t, b, _, _ = hb
    keep[max(0, t - 1):b + 2] += 10 ** 6
    keep[[PIVOT[1], SOLES, SOLES - 1]] += 10 ** 6
    keep[~(a[..., 3] > 0).any(1)] += 10 ** 6
    return shrink_apply(a, SF._pick(rc, b + 2, SOLES - 1, n, keep=keep), [])


# ---------------------------------------------------------------- Q on the new idle: the far axe spinning in its fist
FAR_AXE2 = ((69, 84), (36, 47))            # the axe held out behind (rows, columns) with the fist's left outline;
FAR_POMMEL2 = []                           # the fist itself (skin, columns 48-49) stays on the arm
FAR_FIST2 = (47.5, 75.5)                   # the fist's middle (x, y): quarter turns map squares onto squares


def spin2(a, q):
    """The new idle with its far axe turned q quarter turns about the fist, drawn behind the body (League's Q
    twirls the axe in the hand)."""
    (r0, r1), (c0, c1) = FAR_AXE2
    m = box(a, (r0, r1), (c0, c1))
    for y, x in FAR_POMMEL2:
        m[y, x] = a[y, x, 3] > 0
    body = a.copy()
    body[m] = 0
    part = np.zeros_like(a)
    part[m] = a[m]
    t, _ = turn(part, m, FAR_FIST2, q)
    return over(t, body)


def frame_of(d, src, variant):
    if src == "design":
        return d.copy()
    if isinstance(src, tuple) and src[0] == "spin":
        return spin(d, src[1])
    if isinstance(src, tuple) and src[0] == "run":
        return run2_frame(d, src[1]) if variant == "C" else run_frame(d, src[1], variant)
    if isinstance(src, tuple) and src[0] == "pose":
        return pose_frame(d, src[1])
    if isinstance(src, tuple) and src[0] == "pose_back":
        return shift(pose_frame(d, src[1]), -src[2], 0)
    if isinstance(src, tuple) and src[0] == "spin2":
        return spin2(pose_frame(d, "idle_1"), src[1])
    return load(os.path.join(SRC, f"{src}.png"))


def pose_tags():
    """TAGS with Codex's League-pose idle, attack and the hit from them, once codex_pose/ is in."""
    tags = dict(TAGS)
    if os.path.isdir(lp(POSE)):
        tags["idle"] = [(("pose", "idle_1"), 140)]
        tags["attack"] = [(("pose", f"attack_{k + 1}"), ms) for k, ms in enumerate(POSE_ATTACK)]
        tags["hit"] = [(("pose_back", "idle_1", HIT_BACK), 100)]
        tags["skill"] = [(("spin2", 1), 50), (("spin2", 2), 50), (("spin2", 3), 50), (("pose", "idle_1"), 50)]
    return tags


def layout(n):
    cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
    return cols, -(-n // cols)


def build(variant="C", small=True):
    """Every tag's frames; small: the tags Codex drew at 40 rows made SCALE as big (all of them until codex_pose/ is
    in)."""
    d = load(DESIGN)
    tags = pose_tags()
    sheet = {tag: [(frame_of(d, src, variant), ms) for src, ms in rows] for tag, rows in tags.items()}
    if small and SCALE < 1:
        shrink(sheet, d, SHRINK_TAGS if os.path.isdir(lp(POSE)) else tuple(sheet))
    return sheet


def write(sheet):
    cells = {"cell": [128, 128], "scale": Z, "tags": {}}
    for tag, frames in sheet.items():
        cols, rows = layout(len(frames))
        strip = np.zeros((rows * 128, cols * 128, 4), np.uint8)
        for k, (a, ms) in enumerate(frames):
            r, c = divmod(k, cols)
            strip[r * 128:(r + 1) * 128, c * 128:(c + 1) * 128] = a
        Image.fromarray(strip).resize((cols * 128 * Z, rows * 128 * Z), Image.NEAREST).save(
            lp(os.path.join(OUT, f"draven_{tag}.png")))
        cells["tags"][tag] = [{"pivot": list(PIVOT), "ms": ms} for _, ms in frames]
    with open(lp(os.path.join(OUT, "draven_cells.json")), "w", encoding="utf-8", newline="\n") as f:
        f.write("{" + json.dumps({"cell": cells["cell"], "scale": Z})[1:-1] + ', "tags": {\n')
        f.write(",\n".join(f'  "{t}": ' + json.dumps(v) for t, v in cells["tags"].items()))
        f.write("\n}}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default="C", choices=["C", "M", "V"])
    ap.add_argument("--review", help="write <tag>_<k>.png (128 x 128) here instead of the strips")
    a = ap.parse_args()
    sheet = build(a.run)
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
