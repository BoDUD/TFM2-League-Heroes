#!/usr/bin/env python3
"""league_aphelios's action frames posed from the approved design's own squares (no Codex strips: the user, 2026-10-16,
「动作帧的话可以学习塔姆那种方法做 不依赖codex 但是要做完美 做完美了后再喊我review」; league_tahmkench's way).

    python tools/art/rig_aphelios.py --review DIR      # every tag on the canvas, 4x sheets + a GIF per tag + checks
    python tools/art/rig_aphelios.py                   # the PPU frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero aphelios && python tools/art/ppu_hd.py --hero aphelios

The muzzle flashes are drawn into the shot frames (the client never mirrors an effect picture, only his own frames:
SKILL.md "Both sides" - a CasterViewEffect flash pointed right on the red side): Codex's one picture
(assets/source/aphelios/codex_fx/pixel_1x/aphelios_fx_muzzle.png, 3 frames) recoloured square for square to each
weapon's ramp, the kick frame of a_<w> split in three 20-ms frames, one flash frame each, its root on the weapon's
drawn front; in the 1x frames as drawn, in the PPU frames x PPU (nearest) as orig/aphelios_a_<w>.over.png, which
ppu_restyle.py lays on after the outline (fx=True: no outline round the light).

The design (assets/source/aphelios/hd/design.png, 25 x 69 squares at the final PPU 1.5: Codex's step-1 take 2 with whole
rows and columns deleted, tools/art/design_aphelios_cut.py) is posed without rescaling. Its parts are told on the
read-back before the cut (hd/model2.png, 41 x 111, where the rifle, the arms and the legs are clear) by fixed square
ranges and colours, then carried to the design through the cut's kept rows and columns (hd/model2_keep.json). Moves are
lossless (memory no-deformation-lossless-poses): whole-part translation, exact quarter turns, whole-row shifts (a leg
swinging about the hip), layering (the body sinking a row over the legs). What is new is drawn from the design's own
colours: the far arm stretched forward along a bone line (league_caitlyn's thin-limb way: each square takes the design
forearm's colour at that length and side).
The four other weapons come from the step-1 weapon sheet (hd/weapons2.png, read back on its 10-px grid), each brought
to the design's density by its own row / column deletion (no resampling), its outline closed.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


SRC = os.path.join(ROOT, "assets", "source", "aphelios")
STEM = os.path.join(ROOT, "league", "champions", "league_aphelios")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.5
FEET = 11                         # 1x rows from the pivot down to the ground row
DESIGN = load(os.path.join(SRC, "hd", "design.png"))
FULL = load(os.path.join(SRC, "hd", "model2.png"))
KEEP = json.load(open(lp(os.path.join(SRC, "hd", "model2_keep.json")), encoding="utf-8"))
DH, DW = DESIGN.shape[:2]         # 69 x 25
OUTLINE = (2, 2, 2)

# ------------------------------------------------------------------------------------------------- the canvas
CW, CH = 130, 100
SOLE = 90                         # the canvas row of the design's last row (the soles)
TORSO_X = 13                      # the design column over the pivot: his torso's middle (league_drmundo's lesson: a
                                  # pivot between the feet leaves the body off-centre and red-side caster pictures off)
PIV_X = 48                        # the pivot column on the canvas
OX, OY = PIV_X - TORSO_X, SOLE - (DH - 1)   # where the design's (0, 0) goes standing
CORNER = (PIV_X + 0.5, SOLE + 1)  # the pivot column and the ground line, in squares

# ------------------------------------------------------------------------------------------------- parts
BODY, RIFLE, NEAR_ARM, FAR_ARM, LEG_N, LEG_F, TAIL_N, TAIL_F = range(8)


def labels():
    """Each design square's part, told on the read-back (rows 0-110, columns 0-40) and carried through the cut."""
    f = FULL
    h, w = f.shape[:2]
    R, C = np.mgrid[0:h, 0:w]
    op = f[..., 3] > 0
    rgb = f[..., :3].astype(int)
    cyan = (rgb[..., 1] > 140) & (rgb[..., 2] > 140) & (rgb[..., 0] < 170) & (rgb[..., 1] > rgb[..., 0] + 40)
    purple = (rgb[..., 0] > 90) & (rgb[..., 2] > 140) & (rgb[..., 1] < 100)
    scarf = cyan | purple
    lab = np.zeros((h, w), int)
    # Calibrum: the coloured pieces (4-connected, the outline between them) on his left whose colours are the
    # blade's (ice blue, white, the teal grip - not the sleeve's navy), above the hips; its outline squares are only
    # those that touch nothing but the blade, so his back keeps its own edge when the rifle leaves it (the user,
    # 2026-10-16: 「后背有点变形啊 切武器的时候 看着有点怪」 - the first rifle was every square left of column 10, which
    # took the coat's edge and the outline between them)
    dark0 = op & (rgb.sum(-1) < 40)
    pieces, n = ndimage.label(op & ~dark0)
    blade = np.zeros((h, w), bool)
    for k in range(1, n + 1):
        m = pieces == k
        ys, xs = np.nonzero(m)
        navy = (rgb[m].sum(-1) < 260).mean()
        if xs.mean() < 10.5 and ys.max() < 75 and navy < 0.5:
            blade |= m
    lab[op & (C >= 10) & (C <= 16) & (R >= 44) & (R <= 73) & ~scarf] = NEAR_ARM
    lab[op & (C >= 30) & (R >= 26) & (R <= 58) & ~scarf] = FAR_ARM
    lab[op & (R >= 77) & (C <= 18) & ~scarf] = LEG_N
    lab[op & (R >= 77) & (C >= 19) & ~scarf] = LEG_F
    lab[op & (R >= 60) & scarf & (C <= 21)] = TAIL_N
    lab[op & (R >= 60) & scarf & (C >= 22)] = TAIL_F
    # an outline square goes with the part of the coloured squares beside it (the scarf tail's edge, not the leg);
    # the blade's only when the blade is all it touches
    dark = dark0
    lab[blade] = RIFLE
    fixed = lab.copy()
    for y, x in zip(*np.nonzero(dark)):
        nb = [lab[yy, xx] for yy in range(max(0, y - 1), min(h, y + 2)) for xx in range(max(0, x - 1), min(w, x + 2))
              if op[yy, xx] and not dark[yy, xx]]
        if nb:
            vals, cnt = np.unique(nb, return_counts=True)
            if len(vals) > 1 and RIFLE in vals:
                cnt = cnt[vals != RIFLE]
                vals = vals[vals != RIFLE]
            fixed[y, x] = vals[cnt.argmax()]
        elif x < 11 and y < 75:
            fixed[y, x] = RIFLE        # the outer outline beyond the blade (no colour beside it)
    out = fixed[np.array(KEEP["rows"])][:, np.array(KEEP["cols"])]
    out[DESIGN[..., 3] == 0] = -1
    return out


LAB = labels()


def part(*ks):
    return np.isin(LAB, ks)


def leg_rows(k):
    ys = np.nonzero((LAB == k).any(1))[0]
    return int(ys.min()), int(ys.max())


HIP_N = leg_rows(LEG_N)[0]
HIP_F = leg_rows(LEG_F)[0]


# ------------------------------------------------------------------------------------------------- composing
def blank():
    return np.zeros((CH, CW, 4), np.uint8)


def put(dst, src, mask, dx, dy, under=False):
    """src's squares under mask, moved (dx, dy), onto dst (under: only where dst is empty)."""
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    dst[ty, tx] = src[ys, xs]


def knee_row(k):
    top, bot = leg_rows(k)
    return top + int(round((bot - top) * KNEE))


def swung(k, knee=0, foot=0, lift=0):
    """Leg k as (squares, mask) on the design grid, two bones and lossless: the thigh (hip to KNEE of the leg) by
    whole-row shifts growing from 0 at the hip to `knee` columns at the knee, the shin (knee to sole) moved whole
    `foot` columns and lifted `lift` rows (it rides over the thigh where they meet)."""
    top, bot = leg_rows(k)
    kr = knee_row(k)
    m = LAB == k
    P = 12
    out = np.zeros((DH + 2 * P, DW + 2 * P, 4), np.uint8)
    om = np.zeros(out.shape[:2], bool)
    for r in range(top, kr):
        dx = int(round(knee * (r - top) / max(1, kr - top)))
        xs = np.nonzero(m[r])[0]
        out[r + P, xs + dx + P] = DESIGN[r, xs]
        om[r + P, xs + dx + P] = True
    for r in range(kr, bot + 1):           # the shin: from the knee's shift at its top to `foot` at the sole
        dx = int(round(knee + (foot - knee) * (r - kr) / max(1, bot - kr)))
        xs = np.nonzero(m[r])[0]
        out[r - lift + P, xs + dx + P] = DESIGN[r, xs]
        om[r - lift + P, xs + dx + P] = True
    return out, om, P


def pose(bob=0, dx=0, legs=((0, 0, 0), (0, 0, 0)), sway=0, hide=(), arm=None, extra=(), near_arm=0):
    """One frame on the canvas: the body (everything but the legs) bob rows down over the legs and dx columns on; the
    near / far leg (knee columns, foot columns, lift rows, see swung); near_arm: the hanging near arm swung that many
    columns at the hand (whole-row shifts from the shoulder); the scarf tails swayed `sway` columns; parts in `hide` left out; arm: a callable
    drawing the far arm instead (it gets the canvas and the body's offset); extra: callables run last, the same way."""
    can = blank()
    x0, y0 = OX + dx, OY
    # the far leg behind, the near leg in front of it
    # the legs' tops as they stand, under everything (nothing opens between the coat and a swinging thigh)
    for k in (LEG_F, LEG_N):
        top = leg_rows(k)[0]
        m = (LAB == k) & (np.arange(DH)[:, None] < top + UNDERLAY)
        put(can, DESIGN, m, x0, y0)
    for k, spec in ((LEG_F, legs[1]), (LEG_N, legs[0])):
        src, m, P = swung(k, *spec)
        put(can, src, m, x0 - P, y0 - P)
    body = (LAB >= 0) & ~part(LEG_N, LEG_F, TAIL_N, TAIL_F) & ~part(*hide)
    if arm is not None:
        body &= LAB != FAR_ARM
    if near_arm:
        body &= LAB != NEAR_ARM
        top, bot = np.nonzero((LAB == NEAR_ARM).any(1))[0][[0, -1]]
        for r in range(top, bot + 1):
            dxa = int(round(near_arm * (r - top) / max(1, bot - top)))
            xs = np.nonzero(LAB[r] == NEAR_ARM)[0]
            put(can, DESIGN, np.isin(np.arange(DH)[:, None] * 0 + np.arange(DW)[None, :], xs) & (np.arange(DH)[:, None] == r),
                x0 + dxa, y0 + bob)
    put(can, DESIGN, body, x0, y0 + bob)
    if RIFLE in hide:      # the rifle off his back: the outline it shared with him left one square thick
        zone = np.zeros(can.shape[:2], bool)
        ys, xs = np.nonzero(ndimage.binary_dilation(LAB == RIFLE, structure=np.ones((3, 3))))
        zone[np.clip(ys + y0 + bob, 0, CH - 1), np.clip(xs + x0, 0, CW - 1)] = True
        for _ in range(2):
            loose = orphans(can) & zone
            if not loose.any():
                break
            can[loose] = 0
    for k in (TAIL_N, TAIL_F):
        if k not in hide:
            put(can, DESIGN, LAB == k, x0 - sway, y0 + bob)
    if arm is not None:
        arm(can, x0, y0 + bob)
    for f in extra:
        f(can, x0, y0 + bob)
    return can


def cut_ground(can):
    """Nothing under the ground line (a body sunk over the legs: the legs folded under him)."""
    out = can.copy()
    out[SOLE + 1:] = 0
    return out


def flash(can, k=0.55):
    out = can.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


def cracks(a):
    out = a.copy()
    for _ in range(2):
        op = out[..., 3] > 0
        lr = np.zeros_like(op)
        lr[:, 1:-1] = op[:, :-2] & op[:, 2:]
        ud = np.zeros_like(op)
        ud[1:-1] = op[:-2] & op[2:]
        dark = op & np.all(out[..., :3] == OUTLINE, -1)
        coloured = ndimage.convolve((op & ~dark).astype(int), np.ones((3, 3), int), mode="constant") > 0
        m = (lr | ud) & ~op & coloured       # a slit beside colour, not the gap of an outline taken off
        if not m.any():
            break
        out[m, :3] = OUTLINE
        out[m, 3] = 255
    return out


def tidy(a, hole=10, speck=4):
    """The outline closed round moved edges (strips.complete_outline), 1-square slits closed, small enclosed holes
    filled with their commonest neighbour, loose specks off."""
    out = G.complete_outline(cracks(a), color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        legs = np.nonzero(m)[0].min() >= OY + LEG_ZONE      # behind the legs: the dark of the trousers
        if m.sum() > (LEG_HOLE if legs else hole):
            continue
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[m, :3] = cols[cnt.argmax()]
        out[m, 3] = 255
    op = out[..., 3] > 0
    lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(op, lbl, range(1, n + 1))
        for k in range(1, n + 1):
            if sz[k - 1] < speck:
                out[lbl == k] = 0
    out[SOLE + 1:] = 0
    return out


LEG_ZONE, LEG_HOLE = 50, 16        # design rows from which an enclosed gap is behind the legs, and its largest fill


# ------------------------------------------------------------------------------------------------- the weapons
W_K = 0.5          # the sheet's weapons drawn bigger than his own Calibrum (55 rows against 45): his scale x 0.8,
                   # 0.5 of the read-back (the least a row / column deletion can do: never two neighbours)
W_PARTS = {"grav": (3, 2), "cre": (4,), "sev": (5,), "inf": (6,)}   # the sheet's 8-connected pieces (2: Gravitum's star)


def weapons():
    import design_aphelios_cut as DC
    w = load(os.path.join(SRC, "hd", "weapons2.png"))
    lab, _ = ndimage.label(w[..., 3] > 0, structure=np.ones((3, 3)))
    out = {}
    for name, ids in W_PARTS.items():
        m = np.isin(lab, ids)
        ys, xs = np.nonzero(m)
        sub = w[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
        sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
        out[name] = G.complete_outline(DC.cut(sub, W_K), color=OUTLINE)[0]
    return out


DPAL = np.unique(DESIGN[DESIGN[..., 3] > 0][:, :3], axis=0).astype(int)


def snapped(a):
    """a's colours moved to the design's nearest (the sheet's ice blues and teals onto Calibrum's own)."""
    out = a.copy()
    op = out[..., 3] > 0
    px = out[op][:, :3].astype(int)
    d = ((px[:, None, :] - DPAL[None, :, :]) ** 2).sum(-1)
    out[op, :3] = DPAL[d.argmin(1)].astype(np.uint8)
    return out


WEAPON = {k: snapped(v) for k, v in weapons().items()}
# how each is held in the far hand pointing forward: (mirror left-right, the grip's square in the held picture)
GRIP = {"sev": (True, (6, 2)), "grav": (False, (14, 6)), "cre": (False, (9, 8)), "inf": (False, (4, 24))}


def held(name):
    img = WEAPON[name]
    mirror, grip = GRIP[name]
    return (img[:, ::-1].copy() if mirror else img), grip


def turned(mask, k):
    """The design's squares under mask, cut to their box and turned k quarter turns counter-clockwise (exact)."""
    ys, xs = np.nonzero(mask)
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = DESIGN[ys, xs]
    return np.rot90(sub, k).copy(), (int(ys.min()), int(xs.min()))


def stamp(can, img, x, y, under=False):
    """img's opaque squares with its top-left on canvas (x, y)."""
    m = img[..., 3] > 0
    put(can, img, m, x, y, under)


# the far arm (raised, the hand beside his head) turned a quarter clockwise about its elbow: pointing forward. Its
# forearm cloth (columns FORE_CUT of the turned arm, one navy material) is shortened by whole columns: the turned
# forearm was 25 squares (it was drawn raised beside the head), 20 reads as an arm, not a pole.
ELBOW = (37, 21)                   # design square where the forearm meets the body
FORE_CUT = range(7, 12)
_ARM, _BOX = turned(LAB == FAR_ARM, -1)
ARM_FWD = np.delete(_ARM, list(FORE_CUT), axis=1)
ELBOW_AT = (ELBOW[1] - _BOX[1] - 0, 0)       # unused placeholder (kept for the docs below)
ARM_ROW = _ARM.shape[0] // 2      # the turned arm's middle row (the hand's grip row)


def arm_fwd(dx=0, dy=0, weapon=None, wdx=0, wdy=0, rifle=False):
    """A pose's far arm: the forearm turned forward, its elbow end on ELBOW (+dx, dy); the weapon in the hand (its
    grip on the hand's end + wdx, wdy) or Calibrum levelled with its grip in the hand; both behind the body and the
    arm (the far hand holds them)."""
    def draw(can, x0, y0):
        # the turned arm's left column is the elbow; its rows centred on the elbow's row
        ax = x0 + ELBOW[1] - 1 + dx
        ay = y0 + ELBOW[0] - ARM_ROW + dy
        hx, hy = ax + ARM_FWD.shape[1] - 4, ay + ARM_ROW          # inside the glove
        stamp(can, ARM_FWD, ax, ay)
        if rifle:
            stamp(can, RIFLE_FWD, hx - RIFLE_GRIP[1] + wdx, hy - RIFLE_GRIP[0] + wdy, under=True)
        elif weapon is not None:
            img, (gr, gc) = held(weapon)
            stamp(can, img, hx - gc + wdx, hy - gr + wdy, under=True)
    return draw


FORMS = ("sev", "grav", "inf", "cre")
FORM_HOLD = {"sev": dict(wdx=1, wdy=-2), "grav": dict(wdx=3, wdy=-4), "inf": dict(low=True), "cre": dict(wdx=3, wdy=-4)}
HAND_UP = (17, 21)
HAND_LOW = (47, 6)                 # design square of the hanging near hand's grip (Infernum rests low there, League's
                                   # aphelios_D_Idle1)                 # design square of the raised hand's grip (the idle's far hand beside his head)


def arm_up(weapon=None, dx=0, dy=0, wdx=0, wdy=0, low=False):
    """The idle's raised far arm (moved dx, dy) holding a weapon up by its grip (behind the arm); low: the weapon in
    the hanging near hand instead, behind the body."""
    def draw(can, x0, y0):
        put(can, DESIGN, LAB == FAR_ARM, x0 + dx, y0 + dy)
        if weapon is not None and low:
            img, (gr, gc) = held(weapon)
            stamp(can, img, x0 + HAND_LOW[1] - gc + wdx, y0 + HAND_LOW[0] - gr + wdy, under=True)
        elif weapon is not None:
            img, (gr, gc) = held(weapon)
            stamp(can, img, x0 + HAND_UP[1] - gc + dx + wdx, y0 + HAND_UP[0] - gr + dy + wdy, under=True)
    return draw


def rifle_over(dx=0, dy=0):
    """Calibrum turned level over his head (the swap's flourish), behind the arm."""
    def draw(can, x0, y0):
        stamp(can, RIFLE_FWD, x0 - 12 + dx, y0 + 1 + dy, under=True)
    return draw


def lying(can, ccw=True):
    """The whole frame turned a quarter (counter-clockwise: he falls on his back, the head behind him), laid on the
    ground line about the pivot."""
    ys, xs = np.nonzero(can[..., 3] > 0)
    sub = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = np.rot90(sub, 1 if ccw else -1).copy()
    out = blank()
    h, w = t.shape[:2]
    top = SOLE + 1 - h
    left = PIV_X - w // 2 - (6 if ccw else -6)
    stamp(out, t, left, top)
    return out


# Calibrum off his back, a quarter turn clockwise: levelled, the muzzle forward; its teal grip (columns 24-34 of the
# turned blade) in the far hand
RIFLE_FWD, RIFLE_BOX = turned(LAB == RIFLE, -1)
RIFLE_GRIP = (4, 28)


# ------------------------------------------------------------------------------------------------- idle, hit, run
BREATH = [0, 0, 1, 1, 2, 2, 1, 1]     # rows the body above the waist rises (the BP idle rule: >= 2 rows)
IDLE_MS = 150
WAIST = 44                            # design rows above this rise with the breath (the coat's hem stays)


def breathe(k, **kw):
    """The design standing (pose(**kw): a weapon form), everything above WAIST (the rifle and both arms carried whole)
    k rows up; the squares left open over the waist take the square under them."""
    can = pose(**kw)
    if k == 0:
        return can
    out = can.copy()
    up = np.zeros(can.shape[:2], bool)
    up[:OY + WAIST] = can[:OY + WAIST, :, 3] > 0
    carried = np.zeros(can.shape[:2], bool)
    for p_ in (RIFLE, NEAR_ARM, FAR_ARM):
        ys, xs = np.nonzero(LAB == p_)
        carried[ys + OY, xs + OX] = True
    up |= carried
    ys, xs = np.nonzero(up)
    out[ys, xs] = 0
    out[ys - k, xs] = can[ys, xs]
    hole = (out[..., 3] == 0) & up & ~carried
    for y in sorted(set(np.nonzero(hole)[0]), reverse=True):
        for x in np.nonzero(hole[y])[0]:
            if out[y + 1, x, 3] > 0:
                out[y, x] = out[y + 1, x]
    return out


RUN_MS = 133                           # League's aphelios_A_Run1: 1.067 s a cycle (tools/lol/anim_graph.py)
KNEE = 0.45                            # the knee's place down the leg (hip 0, sole 1)
UNDERLAY = 4                           # rows of each leg's top kept standing under the swung legs
# League's run at game size (tools/lol/pose_joints.py assets/source/aphelios/poses.json --tag run, game px from the
# pivot): per frame the hip's y and, per leg, the knee's and the foot's x from its hip and the foot's height off the
# ground (League's L = his near leg, z toward the camera). His legs here are 0.6 of League's (the coat hides the
# thighs), so the columns and the lift are scaled by LEG_K, the hip's bob by 0.9.
LEAGUE_RUN = [  # (hip y, (near knee dx, foot dx, lift), (far knee dx, foot dx, lift)), game px
    (-11.5, (3.6, 6.1, 0.0), (-2.9, -6.2, 4.6)),
    (-9.2, (3.2, 3.4, 0.7), (-3.1, -8.5, 6.6)),
    (-10.7, (-0.2, -0.4, 0.7), (1.2, -4.6, 7.0)),
    (-10.8, (-1.3, -2.9, 0.7), (3.3, 1.9, 2.1)),
    (-11.3, (-1.2, -4.4, 4.4), (3.5, 4.8, 0.1)),
    (-8.8, (-0.6, -6.0, 7.0), (2.8, 2.4, 0.9)),
    (-10.1, (3.0, -0.9, 3.9), (0.7, -1.3, 0.9)),
    (-11.5, (3.3, 4.6, 1.6), (-1.8, -4.0, 2.2)),
]
LEG_K = 0.6 * PPU


def run_frames(**kw):
    hips = [h for h, _, _ in LEAGUE_RUN]
    top = min(hips)
    out = []
    for i, (hy, n, f) in enumerate(LEAGUE_RUN):
        leg = lambda t: (int(round(t[0] * LEG_K)), int(round(t[1] * LEG_K)), int(round(t[2] * LEG_K)))
        bob = int(round((hy - top) * 0.9))
        # the near arm swings against the near leg, the scarf's tails trail behind more on the push-off
        arm = -int(round(np.clip(n[1] * LEG_K / 3, -2, 2)))
        sway = 1 + int(round(abs(n[1] * LEG_K) > 3))
        out.append((pose(bob=bob, legs=(leg(n), leg(f)), sway=sway, near_arm=arm, **kw), RUN_MS))
    return out


def attack_frames():
    """Every cast strip: (canvas, ms) a frame. Shot frames are the second of each basic attack (80 ms in)."""
    out = {}
    cal = lambda dx=0, dy=0, bob=0, **k: pose(dx=dx, bob=bob, hide=(RIFLE,), arm=arm_fwd(dy=dy, rifle=True, **k))
    fwd = lambda w, dx=0, dy=0, bob=0, **k: pose(dx=dx, bob=bob, arm=arm_fwd(weapon=w, dy=dy, **k))
    up = lambda w=None, dx=0, dy=0, bob=0, **k: pose(dx=dx, bob=bob, arm=arm_up(w, dy=dy, **k))
    # basic attacks: aim, the shot with its kick, hold, back to the stance
    out["a_cal"] = [(cal(dy=-3), 80), (cal(dx=-1, dy=-3, wdx=-1), 60), (cal(dy=-3), 100), (pose(), 110)]
    # the game plays `attack` itself on every attack's first tick, before the tree's CasterAnimation: the stance, so no
    # weapon flashes up for a tick
    out["attack"] = [(pose(), 100)]
    # the last frame is the weapon's own stance (its <w>_idle comes next): Calibrum's stance there showed his main hand
    # empty for 110 ms after every shot (2026-10-19 audit)
    for w in ("sev", "grav", "inf", "cre"):
        out[f"a_{w}"] = [(fwd(w, dy=-3), 80), (fwd(w, dx=-1, dy=-3, wdx=-1), 60), (fwd(w, dy=-3), 100),
                         (stance(w), 110)]
    # the Crescendum's chakram leaves the hand on the shot
    out["a_cre"][1] = (pose(dx=-1, arm=arm_fwd(dy=-3)), 60)
    out["a_cre"][2] = (pose(arm=arm_fwd(dy=-3)), 100)
    # the kick frame three times (20 ms each): the muzzle flash's three frames go on them (muzzle_overs)
    for w in WEAPONS:
        k = out[f"a_{w}"]
        out[f"a_{w}"] = [k[0]] + [(k[1][0], ms) for ms in SHOT_MS] + k[2:]
    # Q (each strip as long as its CasterAnimation in tools/kit/build_aphelios.py: 333 / 233 / 233 / 300 / 267 ms,
    # shortened for the balance - a long hold cost attacks): Calibrum's Moonshot (aim held while the shot is locked, the
    # shot ~170 ms in), Severum's Onslaught (both
    # hands firing: the kick each frame), Gravitum's Binding Eclipse (the cannon raised, the bind ~130 ms in),
    # Infernum's Duskwave (the wave pushed forward ~170 ms in), Crescendum's Sentry (tossed ~170 ms in)
    out["q_cal"] = [(cal(dy=-5), 100), (cal(dy=-5), 60), (cal(dx=-2, dy=-5, wdx=-1), 80), (cal(dx=-1, dy=-5), 50),
                    (pose(), 43)]
    out["q_sev"] = [(fwd("sev", dy=-4), 60), (fwd("sev", dx=-1, dy=-4, wdx=-1), 60), (fwd("sev", dy=-2), 60),
                    (fwd("sev", dx=-1, dy=-2, wdx=-1), 53)]
    g = dict(wdx=3, wdy=-4)          # the cannon held up by its handle in the hand, clear of the head
    out["q_grav"] = [(up("grav", **g), 90), (up("grav", dy=-2, **g), 50), (up("grav", dy=-2, bob=1, **g), 60),
                     (up("grav", **g), 33)]
    out["q_inf"] = [(fwd("inf", dy=-2), 90), (fwd("inf", dx=1, dy=-2, wdx=1), 80), (fwd("inf", dx=-1, dy=-2), 80),
                    (stance("inf"), 50)]
    out["q_cre"] = [(fwd("cre", dy=-1), 90), (fwd("cre", dy=-5), 80), (pose(arm=arm_fwd(dy=-5)), 60),
                    (stance("cre"), 37)]
    # W: the weapons change hands - Calibrum swung over the head and back
    lift = lambda k, a: (lambda can, x0, y0: (put(can, DESIGN, LAB == RIFLE, x0, y0 - k),
                                              put(can, DESIGN, LAB == FAR_ARM, x0, y0 - a)))
    out["skill2"] = [(pose(bob=1, hide=(RIFLE, FAR_ARM), extra=(lift(4, 2),)), 100),
                     (pose(hide=(RIFLE, FAR_ARM), extra=(lift(2, 1),)), 100), (pose(), 100)]
    # R: Moonlight Vigil - a low aim, the moonlight on the third frame (~230 ms in) with a big kick
    out["ult"] = [(cal(dy=-4, bob=2), 120), (cal(dy=-4, bob=2), 110), (cal(dx=-3, dy=-4, bob=2, wdx=-1), 100),
                  (cal(dx=-1, dy=-4, bob=1), 40), (pose(), 30)]
    out["dead"] = dead_frames()
    # the add-on's weapon forms of W, R and the death (view.rs plays <w>_skill2 / <w>_ult / <w>_dead while that weapon
    # is in his main hand - they showed Calibrum whatever he held, League's A-E_Spell2 hold each its own)
    for w in FORMS:
        kw = dict(FORM_HOLD[w])
        low = kw.pop("low", False)
        wdy = kw.pop("wdy", 0)
        hold = lambda dy=0, lift=0: arm_up(w, dy=dy, wdy=wdy - lift, low=low, **kw)
        out[f"{w}_skill2"] = [(pose(bob=1, hide=(RIFLE,), arm=hold(-2, 4 if low else 2)), 100),
                              (pose(hide=(RIFLE,), arm=hold(-1, 2 if low else 1)), 100), (stance(w), 100)]
        fw = lambda dx=0, dy=0, bob=0, **k: pose(dx=dx, bob=bob, hide=(RIFLE,), arm=arm_fwd(weapon=w, dy=dy, **k))
        out[f"{w}_ult"] = [(fw(dy=-4, bob=2), 120), (fw(dy=-4, bob=2), 110), (fw(dx=-3, dy=-4, bob=2, wdx=-1), 100),
                           (fw(dx=-1, dy=-4, bob=1), 40), (stance(w), 30)]
        out[f"{w}_dead"] = dead_frames(w)
    return out


def stance(w):
    """Weapon w's standing frame (its <w>_idle's first): Calibrum off his back, w in the raised hand (Infernum low)."""
    return pose(hide=(RIFLE,), arm=arm_up(w, **FORM_HOLD[w]))


def dead_frames(w=None):
    """Death in 8 frames: the blow, a stagger with the knees giving (the body 3 rows down over the legs), falling on his
    back (the whole figure a quarter turn, 7 then 3 rows off the ground), down, a 1-row bounce, down, still. w: a
    weapon form (its stance), else Calibrum's."""
    kw = {} if w is None else dict(hide=(RIFLE,), arm=arm_up(w, **FORM_HOLD[w]))
    if w == "inf":
        # Infernum, held low and level, would stand on end under him turned with the figure and hold him off the
        # ground: it falls out of his hand and lies on the ground past his feet, its end behind them
        down = lying(pose(hide=(RIFLE,), arm=arm_up(None)))
        img, _ = held(w)
        right = int(np.nonzero((down[..., 3] > 0).any(0))[0].max())
        stamp(down, img, right - 10, SOLE + 1 - img.shape[0], under=True)
    else:
        down = lying(pose(**kw))

    def off(n):
        f = blank()
        f[:-n] = down[n:]
        return f
    return [(pose(dx=-2, **kw), 100), (pose(dx=-3, bob=3, **kw), 120), (off(7), 60), (off(3), 70), (down, 90),
            (off(1), 60), (down.copy(), 140), (down.copy(), 400)]


WEAPONS = ["cal", "sev", "grav", "inf", "cre"]
SHOT_MS = [20, 20, 20]                 # the kick frame's 60 ms, a flash frame each


def flash_frames(w):
    """Codex's muzzle flash (3 cells of 12 x 10 game px) in weapon w's ramp, cut to the three's common box."""
    import pack_aphelios_fx as PK
    ramps = {k: [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in r.split(", ")]
             for k, r in (("cal", PK.GREEN), ("sev", PK.RED), ("grav", PK.VIOLET), ("inf", PK.BLUE), ("cre", PK.SILVER))}
    a = load(os.path.join(SRC, "codex_fx", "pixel_1x", "aphelios_fx_muzzle.png"))
    a[a[..., 3] < 128] = 0
    a[..., 3][a[..., 3] > 0] = 255
    cw = a.shape[1] // 3
    src, dst = np.array(ramps["cal"], float), np.array(ramps[w], np.uint8)
    cells = []
    for k in range(3):
        c = a[:, k * cw:(k + 1) * cw].copy()
        op = c[..., 3] > 0
        c[op, :3] = dst[((c[op][:, :3].astype(float)[:, None] - src[None]) ** 2).sum(2).argmin(1)]
        cells.append(c)
    op = np.zeros(cells[0].shape[:2], bool)
    for c in cells:
        op |= c[..., 3] > 0
    ys, xs = np.nonzero(op)
    return [c[ys.min():ys.max() + 1, xs.min():xs.max() + 1] for c in cells]


def front(a):
    """The drawn front of a frame (its last opaque column) and the middle row of what is drawn in its last two."""
    op = a[..., 3] > 0
    x1 = int(np.nonzero(op.any(0))[0].max())
    ys = np.nonzero(op[:, x1 - 1:x1 + 1].any(1))[0]
    return x1, (ys.min() + ys.max()) / 2.0


def muzzle_overs(acts):
    """{a_<w>: [(the flash on the PPU canvas, its 1x picture) or None, a frame]}: frames 2-4 (the kick) one flash
    frame each, its root (the box's left edge, its middle row) on the weapon's drawn front, x PPU nearest."""
    out = {}
    for w in WEAPONS:
        tag = f"a_{w}"
        fr = flash_frames(w)
        overs = [None] * len(acts[tag])
        for i in range(3):
            can = acts[tag][1 + i][0]
            x1, ym = front(can)
            f = fr[i]
            big = np.asarray(Image.fromarray(f).resize((round(f.shape[1] * PPU), round(f.shape[0] * PPU)),
                                                       Image.NEAREST))
            ov = np.zeros_like(can)
            x0, y0 = x1, int(round(ym - big.shape[0] / 2.0 + 0.5))
            sub = ov[max(0, y0):y0 + big.shape[0], x0:x0 + big.shape[1]]
            b = big[max(0, -y0):max(0, -y0) + sub.shape[0], :sub.shape[1]]
            m = b[..., 3] > 0
            sub[m] = b[m]
            overs[1 + i] = (ov, f)
        out[tag] = overs
    return out


def actions():
    acts = {"idle": [(breathe(b), IDLE_MS) for b in BREATH], "run": run_frames()}
    base = tidy(pose())
    acts["hit"] = [(pose(dx=-3), 90), (pose(dx=-1), 120)]
    # the add-on's whole-body weapon forms (addons/league_aphelios view.rs renames the playing idle / run / hit / attack
    # to <weapon>_<tag> while that weapon is in his main hand): Calibrum off his back, the weapon up in the raised hand
    for w in FORMS:
        kw = dict(hide=(RIFLE,), arm=arm_up(w, **FORM_HOLD[w]))
        acts[f"{w}_idle"] = [(breathe(b, **kw), IDLE_MS) for b in BREATH]
        acts[f"{w}_run"] = run_frames(**kw)
        acts[f"{w}_hit"] = [(pose(dx=-3, **kw), 90), (pose(dx=-1, **kw), 120)]
        acts[f"{w}_attack"] = [(pose(**kw), 100)]
    acts.update(attack_frames())
    acts = {t: [(finish(c, base), ms) for c, ms in fr] for t, fr in acts.items()}
    for t in ["hit"] + [f"{w}_hit" for w in FORMS]:
        acts[t][0] = (flash(acts[t][0][0]), acts[t][0][1])       # the flash after the outline is closed
    return acts, base


# ------------------------------------------------------------------------------------------------- checks and review
def orphans(can):
    op = can[..., 3] > 0
    dark = op & np.all(can[..., :3] == OUTLINE, -1)
    nb = ndimage.convolve((op & ~dark).astype(int), np.ones((3, 3), int), mode="constant")
    return dark & (nb == 0)


def new_orphans(can, base, reach=4):
    """Orphan outline squares that are not the design's own: none of the design's orphans within `reach` rows and
    columns of it (the parts move by a few squares; the design's own double outline moves with them)."""
    o = orphans(can)
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    return int((o & ~near).sum())


def deorphan(can, base, reach=4):
    """The orphan outline squares a move left (none of the design's own double outline near) taken off, one at a time,
    unless that splits the figure."""
    out = can.copy()
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    pieces = lambda a: ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))[1]
    n0 = pieces(out)
    for y, x in np.argwhere(orphans(out) & ~near):
        keep = out[y, x].copy()
        out[y, x] = 0
        if pieces(out) > n0:
            out[y, x] = keep
    return out


def unblot(can, base, reach=4):
    """Outline squares buried in a black lump (all four sides opaque, no colour round them: two parts' outlines laid
    over each other, the legs crossing) take the commonest colour within two squares, outward from the colour; the
    design's own double outline (its orphans' places) stays."""
    out = can.copy()
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    for _ in range(4):
        op = out[..., 3] > 0
        dark = op & np.all(out[..., :3] == OUTLINE, -1)
        four = np.zeros_like(op)
        four[1:-1, 1:-1] = op[:-2, 1:-1] & op[2:, 1:-1] & op[1:-1, :-2] & op[1:-1, 2:]
        lump = orphans(out) & four & ~near
        if not lump.any():
            break
        col = op & ~dark
        for y, x in np.argwhere(lump):
            win = out[max(0, y - 2):y + 3, max(0, x - 2):x + 3]
            m = col[max(0, y - 2):y + 3, max(0, x - 2):x + 3]
            if m.any():
                vals, cnt = np.unique(win[m][:, :3], axis=0, return_counts=True)
                out[y, x, :3] = vals[cnt.argmax()]
    return out


def finish(can, base):
    """tidy and deorphan in turn until the frame stops changing (a pinhole filled may need its outline, an outline
    closed may leave an orphan)."""
    a = tidy(can)
    for _ in range(4):
        b = tidy(deorphan(unblot(a, base), base))
        if (b == a).all():
            break
        a = b
    return a


def stats(can):
    op = can[..., 3] > 0
    n = ndimage.label(op, structure=np.ones((3, 3)))[1]
    holes = int((ndimage.binary_fill_holes(op) & ~op).sum())
    return n, holes, int(orphans(can).sum()), int(op.sum())


def checks(acts, base):
    """Per frame: pieces (8-connected), enclosed holes and orphan outline squares beyond the design's own, colours
    outside the design's palette (the hit flash aside), squares under the soles, opaque area against the design's;
    printed as one line a tag, '!' on a frame with a fault."""
    pal = {tuple(int(v) for v in c) for c in DESIGN[DESIGN[..., 3] > 0][:, :3]}
    _, bh, bo, ba = stats(base)
    for tag, fr in acts.items():
        rep = []
        for j, (can, _) in enumerate(fr):
            op = can[..., 3] > 0
            n, holes, _, area = stats(can)
            orphan = new_orphans(can, base)
            extra = len({tuple(int(v) for v in c) for c in can[op][:, :3]} - pal)
            under = int(op[SOLE + 1:].sum())
            bad = n != 1 or holes > bh or orphan or under or (extra and tag != "hit")
            rep.append(f"{j + 1}:{'!' if bad else ''}p{n} h{holes - bh:+d} o{orphan} c{extra} a{100 * area // ba}%")
        print(f"{tag:8s} " + "  ".join(rep))


def review(acts, out_dir, z=4):
    os.makedirs(out_dir, exist_ok=True)
    for tag, fr in acts.items():
        allc = np.stack([f for f, _ in fr])
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 2, SOLE + 3, xs.min() - 2, xs.max() + 3
        tiles = []
        for f, _ in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB"))
        for scale, suffix in ((z, ""), (2, "_2x")):
            big = [t.resize((t.width * scale, t.height * scale), Image.NEAREST) for t in tiles]
            sheet = Image.new("RGB", (len(big) * (big[0].width + 6), big[0].height), (60, 60, 60))
            for i, t in enumerate(big):
                sheet.paste(t, (i * (t.width + 6), 0))
            sheet.save(os.path.join(out_dir, f"aphelios_{tag}{suffix}.png"))
        small = [t.resize((t.width * 3, t.height * 3), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"aphelios_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


# ------------------------------------------------------------------------------------------------- the game's frames
ORDER = ["idle", "run", "attack", "a_cal", "a_sev", "a_grav", "a_inf", "a_cre", "q_cal", "q_sev", "q_grav", "q_inf", "q_cre",
         "skill2", "ult", "hit", "dead"] + [f"{w}_{t}" for w in ("sev", "grav", "inf", "cre") for t in ("idle", "run", "hit", "attack")] \
    + [f"{w}_{t}" for w in ("sev", "grav", "inf", "cre") for t in ("skill2", "ult", "dead")]


def one_of(can, px, py, hw, hh, need=0.5):
    w1, h1 = 2 * hw + 1, 2 * hh + 1
    one = np.zeros((h1, w1, 4), np.uint8)
    for j in range(h1):
        ya, yb = py + (j - hh - 0.5) * PPU, py + (j - hh + 0.5) * PPU
        for i in range(w1):
            xa, xb = px + (i - hw - 0.5) * PPU, px + (i - hw + 0.5) * PPU
            blk = can[max(0, int(np.floor(ya + 0.5))):max(0, int(np.floor(yb + 0.5))),
                      max(0, int(np.floor(xa + 0.5))):max(0, int(np.floor(xb + 0.5)))].reshape(-1, 4)
            if not len(blk) or (blk[:, 3] > 0).sum() < need * len(blk):
                continue
            cols, n = np.unique(blk[blk[:, 3] > 0][:, :3], axis=0, return_counts=True)
            one[j, i, :3] = cols[n.argmax()]
            one[j, i, 3] = 255
    return one


def crop_hd(can, px, py, W, H):
    hx0, hy0 = int(round(px - W / 2.0)), int(round(py - H / 2.0))
    hd = np.zeros((H, W, 4), np.uint8)
    sx0, sy0 = max(0, hx0), max(0, hy0)
    sub = can[sy0:min(can.shape[0], hy0 + H), sx0:min(can.shape[1], hx0 + W)]
    hd[sy0 - hy0:sy0 - hy0 + sub.shape[0], sx0 - hx0:sx0 - hx0 + sub.shape[1]] = sub
    return hd


def down(can, over=None):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot, the flash's PPU frame
    cut alike or None). The pivot: the pivot column, FEET 1x rows above the ground line. With a flash (muzzle_overs:
    (PPU canvas, 1x picture)) the box holds it too and the 1x frame gets the 1x picture on its own drawn front."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    both = can[..., 3] > 0
    if over is not None:
        both = both | (over[0][..., 3] > 0)
    ys, xs = np.nonzero(both)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh), color=OUTLINE)[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    if over is None:
        return one, crop_hd(can, px, py, W, H), None
    ov, f = over
    x1, ym = front(one)
    y0 = int(round(ym - f.shape[0] / 2.0 + 0.5))
    sub = one[max(0, y0):y0 + f.shape[0], x1:x1 + f.shape[1]]
    b = f[max(0, -y0):max(0, -y0) + sub.shape[0], :sub.shape[1]]
    m = b[..., 3] > 0
    sub[m] = b[m]
    return one, crop_hd(can, px, py, W, H), crop_hd(ov, px, py, W, H)


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def export(acts):
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    overs = muzzle_overs(acts)
    for tag in ORDER:
        ones, hds, ovs = [], [], []
        for k, (can, t) in enumerate(acts[tag]):
            one, hd, ov = down(can, overs[tag][k] if tag in overs else None)
            ones.append((one, float(t)))
            hds.append(hd)
            ovs.append(ov if ov is not None else np.zeros_like(hd))
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"aphelios_{tag}.png")))
        over_png = lp(os.path.join(ORIG, f"aphelios_{tag}.over.png"))
        if tag in overs:
            Image.fromarray(strip_of(ovs)).save(over_png)
        elif os.path.isfile(over_png):
            os.remove(over_png)
        with open(lp(os.path.join(ORIG, f"aphelios_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_aphelios#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the frames at 4x / 2x and a GIF per tag here (nothing written to the repo)")
    a = ap.parse_args()
    acts, base = actions()
    checks(acts, base)
    if a.review:
        review(acts, a.review)
        return
    export(acts)


if __name__ == "__main__":
    main()
