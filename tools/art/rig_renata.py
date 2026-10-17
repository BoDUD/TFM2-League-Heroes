#!/usr/bin/env python3
"""league_renata's action frames posed from the approved design's own squares (no Codex strips: the user, 2026-10-17,
「codex交付了 然后动作帧按照塔姆那样做吧 做到完美了喊我review」; league_tahmkench's, league_swain's and league_yunara's way).

    python tools/art/rig_renata.py --review DIR      # every tag on the canvas, 4x / 2x sheets + a GIF per tag + checks
    python tools/art/rig_renata.py                   # the PPU frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero renata && python tools/art/ppu_hd.py --hero renata

The design (assets/source/renata/hd/design.png, 34 x 60 squares at the final PPU 1.5: Codex's step-1 take 1 with whole
rows / columns deleted, tools/art/design_renata.py) is posed without rescaling. Its parts are told by fixed square ranges
and colours on the design:
  ARM   the golden mechanical near arm (rows 25-46: it comes out under the cape and hangs down to the hand by her hip),
  UPF   the far upper arm (bare brown skin under the cape's far edge, down to the elbow),
  FORE  the far forearm and the black glove (right of column 26, rows 16-32), PISTOL the long pistol above the glove:
        she holds it upright in the design (League's combat idle); the user, 2026-10-17, 「改成平时空手：待机和跑步不拿枪
        （枪插在胯部），只有普攻拔枪开枪」 - so every frame but the attack's hangs the empty forearm down from the elbow
        (flipped top to bottom: exact) and tucks the pistol upside down in at her far hip; the attack turns forearm and
        pistol together level,
  LEG_N / LEG_F  the white flared trouser legs (split at the crotch) with their boots,
  BODY  the rest (head, hair, cape, vest, shirt).
Moves are lossless (memory no-deformation-lossless-poses): whole-part translation, exact quarter turns and flips about
square centres, whole-row shifts (a trouser leg swinging about the hip), layering (the body sinking over the legs). Where
the near arm leaves its place, the squares it covered over her long hair are the hair's own colours (the hair's row
continued, like league_swain's empty sleeve); below the hair they stay open (the arm hung free beside her hip).
The R machine (hd/machine.png, Codex's renata-machine-1 at her scale) stands behind her in the ult frames, its place from
hd/machine.json, revealed core first (league_renata_r's unfolding) - it rides in her own frames so it turns with her on
the red side (memory red-side-caster-pictures).
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


SRC = os.path.join(ROOT, "assets", "source", "renata")
STEM = os.path.join(ROOT, "league", "champions", "league_renata")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.5
FEET = 11                         # 1x rows from the pivot down to the ground row
DESIGN = load(os.path.join(SRC, "hd", "design.png"))
MACHINE = load(os.path.join(SRC, "hd", "machine.png"))
MACHINE_AT = json.load(open(lp(os.path.join(SRC, "hd", "machine.json")), encoding="utf-8"))
DH, DW = DESIGN.shape[:2]         # 60 x 34
OUTLINE = (5, 2, 6)

# ------------------------------------------------------------------------------------------------- the canvas
CW, CH = 200, 150
SOLE = 130                        # the canvas row of the design's last row (the soles)
TORSO_X = 15                      # the design column over the pivot: between her boots
PIV_X = 90                        # the pivot column on the canvas
OX, OY = PIV_X - TORSO_X, SOLE - (DH - 1)   # where the design's (0, 0) goes standing
CORNER = (PIV_X + 0.5, SOLE + 1)  # the pivot column and the ground line, in squares

# ------------------------------------------------------------------------------------------------- parts
BODY, ARM, UPF, FORE, PISTOL, LEG_N, LEG_F = range(7)
PISTOL_END = 15                   # the pistol above this row (its barrel and fittings), the forearm and the glove below
WAIST = 34                        # the trousers start under the vest's points
SPLIT_TOP, SPLIT_BOT, SPLIT_BOOT = 19, 15, 12   # the near leg's last column: by the hips, the shins, the boots
SHIN_ROW, BOOT = 47, 55           # where the split moves to SPLIT_BOT; the first boot row
RGB = DESIGN[..., :3].astype(int)
OP = DESIGN[..., 3] > 0


def colour_is(*cols):
    m = np.zeros((DH, DW), bool)
    for c in cols:
        m |= np.all(RGB == c, -1)
    return m & OP


# the design's colour families (its 37-colour palette)
DARK = colour_is((5, 2, 6), (25, 20, 39), (61, 1, 16))                   # the outline and its darkest neighbours
HAIR = colour_is((46, 25, 63), (35, 40, 66), (25, 20, 39))
CAPE = colour_is((204, 221, 251), (231, 241, 251), (162, 166, 236), (178, 190, 247), (141, 150, 207),
                 (107, 119, 151), (93, 115, 161), (71, 79, 109), (150, 158, 177), (129, 117, 112))
SKIN = colour_is((200, 120, 77), (165, 84, 51))
WARM = OP & (RGB[..., 0] > 95) & ((RGB[..., 0] > RGB[..., 2] + 30) | ((RGB[..., 0] > 140) & (RGB[..., 1] < 90)))
# gold, brass, the magenta lines, the arm's browns (anything warm that is not the skin of her face / far arm)


def labels():
    R, C = np.mgrid[0:DH, 0:DW]
    lab = np.full((DH, DW), -1)
    lab[OP] = BODY
    # the far forearm and glove (right of column 26, rows 16-32) and the pistol above the glove (rows 3-15)
    lab[OP & (C >= 27) & (R >= PISTOL_END + 1) & (R <= 32)] = FORE
    lab[OP & (C >= 27) & (R >= 3) & (R <= PISTOL_END)] = PISTOL
    # the far upper arm: its skin in columns 24-26 under the cape (rows 23-32), with the outline between it and the
    # forearm
    upf = SKIN & (C >= 24) & (C <= 26) & (R >= 23) & (R <= 32)
    upf |= DARK & (C == 26) & (R >= 24) & (R <= 32) & ndimage.binary_dilation(upf, structure=np.ones((3, 3)))
    lab[upf] = UPF
    # the near arm: the warm squares in its box (rows 25-28 where it comes out under the cape, columns 7-13; rows
    # 29-46 down to the hand, columns 0-11), and the outline squares that touch only it
    box = ((R >= 25) & (R <= 28) & (C >= 7) & (C <= 13)) | ((R >= 29) & (R <= 46) & (C <= 11))
    arm = box & (WARM | colour_is((64, 42, 14), (61, 1, 16))) & ~SKIN
    # its outline: dark squares within 2 of its colours that touch no other material (the outline it shares with the
    # hair, the cape or a trouser leg stays with them)
    near = ndimage.binary_dilation(arm, structure=np.ones((5, 5)))
    others = OP & ~arm & ~DARK
    touch_other = ndimage.binary_dilation(others, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]]))
    arm |= box & DARK & near & ~touch_other
    lab[arm] = ARM
    # the trouser legs and their boots (the vest's navy points and the hair stay with the body)
    legs = OP & (R >= WAIST) & (lab == BODY) & ~(HAIR & (R <= 37))
    split = np.where(R < SHIN_ROW, SPLIT_TOP, np.where(R < BOOT, SPLIT_BOT, SPLIT_BOOT))
    lab[legs & (C <= split)] = LEG_N
    lab[legs & (C > split)] = LEG_F
    return lab


LAB = labels()


def part(*ks):
    return np.isin(LAB, ks)


def leg_rows(k):
    ys = np.nonzero((LAB == k).any(1))[0]
    return int(ys.min()), int(ys.max())


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


def stamp(can, img, x, y, under=False):
    """img's opaque squares with its top-left on canvas (x, y)."""
    put(can, img, img[..., 3] > 0, x, y, under)


KNEE = 0.45                            # the knee's place down the trouser leg (hip 0, sole 1)
UNDERLAY = 3                           # rows of each leg's top kept standing under the swung legs


def knee_row(k):
    top, bot = leg_rows(k)
    return top + int(round((bot - top) * KNEE))


def swung(k, knee=0, foot=0, lift=0):
    """Leg k as (squares, mask, pad) on the design grid, two bones and lossless: the thigh (hip to KNEE of the leg) by
    whole-row shifts growing from 0 at the hip to `knee` columns at the knee, the shin (knee to the hem) shifted from
    `knee` to `foot` columns at the hem and lifted `lift` rows (it rides over the thigh where they meet), the boot
    under it moved whole by (foot, -lift)."""
    top, bot = leg_rows(k)
    kr = knee_row(k)
    m = LAB == k
    P = 24
    out = np.zeros((DH + 2 * P, DW + 2 * P, 4), np.uint8)
    om = np.zeros(out.shape[:2], bool)
    for r in range(top, kr):
        dx = int(round(knee * (r - top) / max(1, kr - top)))
        xs = np.nonzero(m[r])[0]
        out[r + P, xs + dx + P] = DESIGN[r, xs]
        om[r + P, xs + dx + P] = True
    hem = BOOT - 1
    for r in range(kr, bot + 1):
        dx = foot if r >= BOOT else int(round(knee + (foot - knee) * (r - kr) / max(1, hem - kr)))
        xs = np.nonzero(m[r])[0]
        out[r - lift + P, xs + dx + P] = DESIGN[r, xs]
        om[r - lift + P, xs + dx + P] = True
    return out, om, P


def turned(mask, k=0, flip=False):
    """The design's squares under mask, cut to their box, flipped top to bottom (flip) and turned k quarter turns
    counter-clockwise (exact): (image, the box's top-left (row, col) on the design)."""
    ys, xs = np.nonzero(mask)
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = DESIGN[ys, xs]
    if flip:
        sub = sub[::-1]
    return np.rot90(sub, k).copy(), (int(ys.min()), int(xs.min()))


def where_after(mask, sq, k=0, flip=False):
    """Where design square sq = (row, col) of the part under mask lands in turned(mask, k, flip) (its box's
    coordinates)."""
    ys, xs = np.nonzero(mask)
    h, w = ys.max() - ys.min() + 1, xs.max() - xs.min() + 1
    r, c = sq[0] - ys.min(), sq[1] - xs.min()
    if flip:
        r = h - 1 - r
    for _ in range(k % 4):            # one counter-clockwise quarter turn: (r, c) in an h x w box -> (w - 1 - c, r)
        r, c, h, w = w - 1 - c, r, w, h
    return int(r), int(c)


def placed(mask, k, flip, anchor, at):
    """A drawing callable: the part under mask turned (k quarter turns counter-clockwise, flipped first if flip) and
    moved so that its design square `anchor` lands on design square `at` (both (row, col))."""
    img, _ = turned(mask, k, flip)
    r, c = where_after(mask, anchor, k, flip)

    def draw(can, x0, y0):
        stamp(can, img, x0 + at[1] - c, y0 + at[0] - r)
    return draw


# the near arm: its shoulder end where it comes out under the cape, and its hand
ARM_TOP = (25, 10)                    # (row, col): the arm's top square under the cape
ARM_HAND = (44, 5)
SHOULDER = (24, 10)                   # the column the arm's top keeps when it is held out (+ reach: in 3/4 view the
                                      # near arm thrust forward starts over her chest, its shoulder behind it)
# the far arm: the elbow (the forearm's lowest skin square) and where it sits on the upper arm
ELBOW = (31, 28)


def arm_level(reach=0, drop=0):
    """The near arm mirrored about its diagonal (exact: flipped top to bottom, then a quarter turn clockwise): held out
    forward and a little up - a punch at shoulder height - its top on (ARM_TOP rows - 1 + drop, SHOULDER's column +
    reach)."""
    return placed(LAB == ARM, 3, True, ARM_TOP, (ARM_TOP[0] - 1 + drop, SHOULDER[1] + reach))


def arm_up(dx=0, dy=0):
    """The near arm flipped top to bottom about its top square: raised over her head (the hand up, the lit side
    kept)."""
    return placed(LAB == ARM, 0, True, ARM_TOP, (ARM_TOP[0] + dy, ARM_TOP[1] + dx))


def arm_at(dx=0, dy=0):
    """The near arm as drawn, moved whole."""
    return placed(LAB == ARM, 0, False, ARM_TOP, (ARM_TOP[0] + dy, ARM_TOP[1] + dx))


def gun_fwd(dx=0, dy=0):
    """The far forearm, glove and pistol turned a quarter clockwise about the elbow: the pistol drawn, level and
    pointing forward at the elbow's height (a shot from the hip: the muzzle near the targets' pivot height, memory
    bullet-tilt-muzzle), its elbow square kept on ELBOW (+dx, +dy)."""
    return placed(part(FORE, PISTOL), 3, False, ELBOW, (ELBOW[0] + dy, ELBOW[1] + dx))


def fore_hang(dx=0, dy=0):
    """The far forearm and the empty glove flipped top to bottom about the elbow: hanging down by her side (exact, the
    lit side kept), the elbow square on ELBOW (+dx, +dy)."""
    return placed(LAB == FORE, 0, True, ELBOW, (ELBOW[0] + dy, ELBOW[1] + dx))


TUCK = (35, 22)                       # where the tucked pistol's top square goes: at her far hip under the vest's points
                                      # (higher, its dark barrel ran into the navy vest; one column left of the hanging glove)
PISTOL_TOP_IN = (PISTOL_END, 29)      # the pistol's square that comes out on top when it is turned muzzle down


def hanging(dx=0):
    """A drawing callable for pose(gun=...): the pistol tucked in at her hip and the empty forearm hanging, moved dx
    columns (a walking swing)."""
    def draw(can, x0, y0):
        pistol_tucked()(can, x0, y0)
        fore_hang(dx)(can, x0, y0)
    return draw


def pistol_tucked(dx=0, dy=0):
    """The pistol upside down (flipped top to bottom: exact), tucked in at her far hip - the muzzle down along her thigh,
    the fittings at the belt."""
    return placed(LAB == PISTOL, 0, True, PISTOL_TOP_IN, (TUCK[0] + dy, TUCK[1] + dx))


# ------------------------------------------------------------------------------------------------- the hair behind the arm
HAIR_MID = (46, 25, 63)                # the hair's own middle purple (its commonest colour)


def hair_behind():
    """The squares the near arm covers over her long hair (rows 25-33), in the hair's middle purple, flat (the hair's
    row continued; the body's outline beside it stays). -> (squares, mask)."""
    out = np.zeros_like(DESIGN)
    m = np.zeros((DH, DW), bool)
    arm = LAB == ARM
    for r in range(25, 34):
        xs = np.nonzero(arm[r])[0]
        if not len(xs) or not HAIR[r, :xs.min() + 1].any():
            continue
        for x in xs:
            # only between the hair and the body (something of hers right of it in the design)
            right = OP[r, x + 1:] & (LAB[r, x + 1:] != ARM)
            if not right.any():
                continue
            out[r, x] = (*HAIR_MID, 255)
            m[r, x] = True
    return out, m


HAIR_FILL = hair_behind()


# ------------------------------------------------------------------------------------------------- posing
class Frame:
    def __init__(self, can, x0, y0):
        self.can, self.x0, self.y0 = can, x0, y0

    def done(self, base):
        out = finish(self.can, base)
        out[SOLE + 1:] = 0
        return out


def pose(bob=0, dx=0, legs=((0, 0, 0), (0, 0, 0)), arm=None, gun=None, upf=True, lift=0, hide=(), behind=(),
         extra=()):
    """One frame (a Frame): the body (all but the legs) bob rows down over the legs and dx columns on, the whole
    figure lift rows up; the near / far leg (knee columns, foot columns, lift rows: see swung); arm: None (the near arm
    as drawn) or a callable drawing it (gets the canvas and the body's origin) - moved away, the hair behind it shows;
    gun: None (the far forearm hanging empty, the pistol tucked in at her hip) or a callable drawing the forearm with the
    pistol drawn (the attack); upf: the far upper arm drawn; hide: parts left out; behind: callables
    drawn first (under everything: the R machine); extra: callables drawn last."""
    can = blank()
    x0, y0 = OX + dx, OY - lift
    for f in behind:
        f(can, x0, y0 + bob)
    # the legs' tops as they stand, under everything (nothing opens between the vest and a swinging leg)
    for k in (LEG_F, LEG_N):
        if k in hide:
            continue
        top = leg_rows(k)[0]
        put(can, DESIGN, (LAB == k) & (np.arange(DH)[:, None] < top + UNDERLAY), x0 - dx, y0)
    for k, spec in ((LEG_F, legs[1]), (LEG_N, legs[0])):
        if k in hide:
            continue
        src, m, P = swung(k, *spec)
        put(can, src, m, x0 - dx - P, y0 - P)
    if arm is not None:
        put(can, HAIR_FILL[0], HAIR_FILL[1], x0, y0 + bob)
    body = part(BODY) & ~part(*hide)
    put(can, DESIGN, body, x0, y0 + bob)
    if upf and UPF not in hide:
        put(can, DESIGN, LAB == UPF, x0, y0 + bob)
    if FORE not in hide:
        if gun is None:
            # the pistol in at her hip, the empty hand hanging by her side
            pistol_tucked()(can, x0, y0 + bob)
            fore_hang()(can, x0, y0 + bob)
        else:
            gun(can, x0, y0 + bob)
    if ARM not in hide:
        if arm is None:
            put(can, DESIGN, LAB == ARM, x0, y0 + bob)
        else:
            arm(can, x0, y0 + bob)
    for f in extra:
        f(can, x0, y0 + bob)
    return Frame(can, x0, y0 + bob)


def flash(can, k=0.55):
    out = can.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- the R machine
MR, MC = MACHINE_AT["row"], MACHINE_AT["col"]        # its top-left square in design squares
MH, MW = MACHINE.shape[:2]
_my, _mx = np.mgrid[0:MH, 0:MW]
_mop = MACHINE[..., 3] > 0
M_CY, M_CX = float(_my[_mop].mean()), float(_mx[_mop].mean())    # the machine's middle


# ------------------------------------------------------------------------------------------------- her size
# The user on the first review, 2026-10-17: 「模型太大」 (she stood as tall as Darius; the slim heroines are 35-38 rows).
# The 60-row design (40 game rows) is brought to TARGET rows by whole rows and columns deleted (design_renata_cut.cut:
# never two neighbours; the face, the magenta, the gold and the outline cost more - lossless, every square left as
# drawn), and everything worked out on the 60 rows above - the parts, the hair behind the arm, every design point - is
# carried over by the kept rows / columns; the R machine is cut by the same share and keeps its place against her
# soles and standing column.
import design_renata_cut as DC  # noqa: E402

TARGET = 54                        # 36 game rows at PPU 1.5
# The first cut (2026-10-17) took all six rows from her legs - two through the crotch - and the user saw the legs run
# together: 「感觉模型还是有变形」. The lines that carry her shape are kept now: the head and face (rows 0-14), the hips,
# the crotch and the thighs down past the knees (34-47), the trousers' flared hems and the boots (53-59), and every
# column from the mechanical arm to the pistol (4-32); the rows go from the cape, the vest and the long hair (15-33) and
# the plain shins (48-52), the columns from the hair's and the pistol's outer edges.
HARD_ROWS = set(range(0, 15)) | set(range(34, 48)) | set(range(53, 60))
HARD_COLS = set(range(4, 33))
_D60 = DESIGN
_code = _D60.astype(np.int64) @ np.array([1 << 24, 1 << 16, 1 << 8, 1], np.int64)
_wt = DC.weights(_D60)
_rows, _ = DC.DA.dp_keep(list(_code), list(_wt), TARGET, hard=HARD_ROWS)
_cols, _ = DC.DA.dp_keep(list(_code[_rows].T), list(_wt[_rows].T), round(_D60.shape[1] * TARGET / _D60.shape[0]),
                         hard=HARD_COLS)
RK, CK = np.array(_rows), np.array(_cols)
DESIGN = _D60[np.ix_(RK, CK)]
SCALE = DESIGN.shape[0] / _D60.shape[0]
LAB = LAB[np.ix_(RK, CK)]
HAIR_FILL = (HAIR_FILL[0][np.ix_(RK, CK)], HAIR_FILL[1][np.ix_(RK, CK)])


def mr(r):
    """The new design row nearest to the 60-row design's row r."""
    return int(np.argmin(np.abs(RK - r)))


def mc(c):
    return int(np.argmin(np.abs(CK - c)))


def mp(p_):
    return (mr(p_[0]), mc(p_[1]))


_stand60 = TORSO_X
DH, DW = DESIGN.shape[:2]
TORSO_X = mc(TORSO_X)
OX, OY = PIV_X - TORSO_X, SOLE - (DH - 1)
WAIST, SHIN_ROW, BOOT = mr(WAIST), mr(SHIN_ROW), mr(BOOT)
ARM_TOP, ARM_HAND, SHOULDER, ELBOW, TUCK, PISTOL_TOP_IN = (mp(q) for q in (ARM_TOP, ARM_HAND, SHOULDER, ELBOW, TUCK,
                                                                         PISTOL_TOP_IN))
MR = (DH - 1) + int(round((MR - (_D60.shape[0] - 1)) * SCALE))
MC = TORSO_X + int(round((MC - _stand60) * SCALE))
MACHINE = DC.cut(MACHINE, SCALE)
MH, MW = MACHINE.shape[:2]
_my, _mx = np.mgrid[0:MH, 0:MW]
_mop = MACHINE[..., 3] > 0
M_CY, M_CX = float(_my[_mop].mean()), float(_mx[_mop].mean())


def machine(reach=1.0, dy=0, dx=0):
    """A drawing callable: the machine behind her, only its squares within `reach` (0..1) of the farthest blade tip
    from its middle (the core first: the blades unfold), moved (dx, dy)."""
    d = np.hypot((_my - M_CY) / 1.0, (_mx - M_CX) / 1.0)
    keep = _mop & (d <= reach * d[_mop].max() + 0.01)
    img = np.zeros_like(MACHINE)
    img[keep] = MACHINE[keep]
    if reach < 1.0:
        # the cut blade ends closed: the outline on the cut edge (complete_outline only rings light edges)
        img = G.complete_outline(img, color=OUTLINE)[0]

    def draw(can, x0, y0):
        stamp(can, img, x0 + MC + dx, y0 + MR + dy, under=True)
    return draw


# ------------------------------------------------------------------------------------------------- tidying
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
        m = (lr | ud) & ~op & coloured
        if not m.any():
            break
        out[m, :3] = OUTLINE
        out[m, 3] = 255
    return out


def tidy(a, hole=10, speck=4):
    """The outline closed round moved edges (strips.complete_outline), 1-square slits closed, small enclosed holes
    filled with their commonest neighbour, loose specks off, nothing under the soles."""
    out = G.complete_outline(cracks(a), color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > hole:
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


def orphans(can):
    op = can[..., 3] > 0
    dark = op & np.all(can[..., :3] == OUTLINE, -1)
    nb = ndimage.convolve((op & ~dark).astype(int), np.ones((3, 3), int), mode="constant")
    return dark & (nb == 0)


def deorphan(can, base, reach=4):
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
    a = tidy(can)
    for _ in range(4):
        b = tidy(deorphan(unblot(a, base), base))
        if (b == a).all():
            break
        a = b
    return a


# ------------------------------------------------------------------------------------------------- idle, run
# the user on the first review: 「上下摆动模型变形」 - the first idle lifted the upper body two rows and filled the waist
# with the row under it (the vest's points grew). Now the upper body (both arms and the pistol with it) sinks a row OVER
# the trousers' top and back: layering, every square as drawn.
BREATH = [0, 0, 0, 1, 1, 1, 1, 0]
IDLE_MS = 150


def breathe(k):
    """The design standing, everything but the legs k rows down over the trousers' top (memory
    no-deformation-lossless-poses: layering, nothing stretched)."""
    return pose(bob=k)


RUN_MS = 133                           # League's Run: 3 cycles in 3.2 s, 1067 ms a cycle, 8 frames
# The walk is Codex's (the user on the first review: 「走路姿势很奇怪」 - two posed walks from the design's own legs stayed
# a jumble: both hands hang at her hips over short legs, and her near trouser leg stands slanted): League's own Run as
# the skeleton, our idle as the skin (tools/art/pack_renata_run.py), read back and brought to the design by
# tools/art/import_renata_run.py (the legs shortened to the design's at one fixed spacing, the design's head laid over
# every frame). Each frame stands on the ground line with its head where the idle's head is (Codex's bob kept: the
# head rides 1-4 rows over its idle place, League's own rise and fall).
RUN_NPZ = os.path.join(SRC, "hd", "run.npz")


def run_frames():
    z = np.load(lp(RUN_NPZ))
    places = z["places"]
    out = []
    for i, (dx, dy) in enumerate(places):
        f = z[f"f{i}"]
        can = blank()
        stamp(can, f, OX - int(dx), SOLE - (f.shape[0] - 1))
        out.append((Frame(can, OX, SOLE - (f.shape[0] - 1) + int(dy)), RUN_MS))
    return out


# ------------------------------------------------------------------------------------------------- the casts
LUNGE = ((-2, -6, 0), (3, 7, 0))       # Q's lunge: the near leg back, the far leg forward, straight out


def lying(fr, cw=True, dx=0):
    """The figure turned a quarter (clockwise: she falls forward, the head ahead; counter-clockwise: on her back, the
    head behind her), laid on the ground line."""
    can = fr.can
    ys, xs = np.nonzero(can[..., 3] > 0)
    sub = can[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = np.rot90(sub, -1 if cw else 1).copy()
    out = blank()
    h, w = t.shape[:2]
    stamp(out, t, PIV_X - w // 2 + dx, SOLE + 1 - h)
    return out


def cut_ground(fr):
    fr.can[SOLE + 1:] = 0
    return fr


def casts():
    """Every cast strip: (Frame, ms). Release ticks (tools/kit/build_renata.py): the attack's shot on a_st (the start of
    frame 3), E's missiles on e_rel, Q's hand on q_rel, R's wave on r_rel."""
    out = {}
    # attack (League's Attack1): the pistol drawn from her hip, fired level from the hip, the recoil, put back
    out["attack"] = [(pose(dx=-1), 60), (pose(gun=gun_fwd(-1, -1)), 60),
                     (pose(dx=1, gun=gun_fwd()), 80), (pose(dx=1, gun=gun_fwd(-1, -1)), 90),
                     (pose(gun=gun_fwd(-1, -1)), 80), (pose(), 130)]
    # E Loyalty Program (League's Spell3: a crouch, then the arm swept up and thrown forward as the missiles leave)
    out["skill"] = [(pose(bob=2), 70), (pose(bob=1, arm=arm_up()), 80), (pose(dx=1, arm=arm_level(4)), 90),
                    (pose(dx=1, arm=arm_level(5)), 100), (pose(arm=arm_level(2)), 93)]
    # Q Handshake (League's Spell1_Activate: a lunge, the mechanical arm thrust straight out - the hand flies)
    out["skill2"] = [(pose(dx=-1), 90), (pose(bob=2, legs=LUNGE, arm=arm_level(3)), 110),
                     (pose(bob=3, dx=2, legs=LUNGE, arm=arm_level(7)), 110), (pose(bob=3, dx=2, legs=LUNGE, arm=arm_level(7)), 100),
                     (pose(bob=1, legs=((-1, -2, 0), (1, 3, 0)), arm=arm_level(3)), 90)]
    # Q's fling (League's Spell1_Fling_Back): still in the lunge, the arm yanked back over her shoulder as she leans
    # back, then up out of the lunge
    out["skill2_fling"] = [(pose(bob=3, legs=LUNGE, arm=arm_level(6)), 70),
                           (pose(bob=3, dx=-1, legs=LUNGE, arm=arm_up()), 90),
                           (pose(bob=2, dx=-2, legs=LUNGE, arm=arm_up(-1)), 120),
                           (pose(bob=1, dx=-1, legs=((-1, -2, 0), (1, 3, 0))), 120)]
    # W Bailout (the mechanical arm held out toward the ally)
    out["skill_w"] = [(pose(arm=arm_level(3)), 90), (pose(dx=1, arm=arm_level(5)), 120), (pose(), 90)]
    # R Hostile Takeover (League's Spell4): the arm raised high, the machine unfolding behind her (core, then the
    # blades), the wave sent (r_rel = the start of frame 4), the machine folding away
    out["ult"] = [(pose(bob=2, arm=arm_level(3)), 100),
                  (pose(arm=arm_up(), behind=[machine(0.6, dy=3)]), 100),
                  (pose(arm=arm_up(), behind=[machine()]), 100),
                  (pose(dx=1, arm=arm_up(), behind=[machine()]), 120),
                  (pose(dx=1, arm=arm_up(), behind=[machine()]), 120),
                  (pose(arm=arm_level(3), behind=[machine(0.6, dy=3)]), 127)]
    # death (League's Death): the blow, a stagger back, down on her knees (sunk into the ground line), fallen on her
    # back (the head behind her, as League's)
    kneel = cut_ground(pose(lift=-12))
    flat = lying(pose(), cw=False)
    out["dead"] = [(pose(dx=-2), 100), (pose(dx=-2, bob=4), 120), (kneel, 150), (Frame(flat, OX, OY), 150),
                   (Frame(flat.copy(), OX, OY), 400)]
    return out


def actions():
    acts = {"idle": [(breathe(b), IDLE_MS) for b in BREATH], "run": run_frames()}
    base = tidy(pose().can)
    acts["hit"] = [(pose(dx=-3), 90), (pose(dx=-1), 120)]
    acts.update(casts())
    acts = {t: [(f.done(base), ms) for f, ms in fr] for t, fr in acts.items()}
    acts["hit"][0] = (flash(acts["hit"][0][0]), acts["hit"][0][1])
    return acts, base


# ------------------------------------------------------------------------------------------------- the muzzle flash
# Codex's a_flash (tools/art/pack_renata_fx.py: on her own fine squares, pointing forward, symmetric top to bottom;
# the delivery's pixel_1x, read by import_renata_fx.flash_cells) laid over the finished shot frames - after finish(), so
# no outline closes round the light - its root (the cell's left edge, middle row) a square past the barrel's end. A
# picture with a front rides in her own frames and turns with her (memory red-side-caster-pictures). Flash frames 1-3
# on attack frames 3-5 (the shot on a_st, the recoil, the gun still out); nothing before the delivery.
FLASH_ON = {2: 0, 3: 1, 4: 2}          # attack frame (0-based) -> flash frame


def with_flash(can, f):
    """The frame with the flash f rooted a square past the muzzle: the rightmost square within 4 rows of the elbow's
    row (the pistol points forward at the elbow's height), the flash's middle row on the barrel's middle."""
    r0 = OY + ELBOW[0]
    lo = max(0, r0 - 4)
    band = can[lo:r0 + 5, :, 3] > 0
    c = int(np.nonzero(band.any(0))[0].max())
    rows = np.nonzero(band[:, c])[0] + lo
    top = int(round((rows.min() + rows.max()) / 2 - (f.shape[0] - 1) / 2))
    out = can.copy()
    ys, xs = np.nonzero(f[..., 3] > 0)
    out[top + ys, c + 1 + xs] = f[ys, xs]
    return out


def add_flash(acts):
    try:
        import import_renata_fx as F
        cells = F.flash_cells()
    except (OSError, KeyError, ValueError, SystemExit) as e:
        print("no muzzle flash:", e)
        return acts
    if cells is None:
        return acts
    out = dict(acts)
    out["attack"] = [(with_flash(f, cells[FLASH_ON[j]]) if j in FLASH_ON else f, ms)
                     for j, (f, ms) in enumerate(acts["attack"])]
    return out


# ------------------------------------------------------------------------------------------------- checks and review
def stats(can):
    op = can[..., 3] > 0
    n = ndimage.label(op, structure=np.ones((3, 3)))[1]
    holes = int((ndimage.binary_fill_holes(op) & ~op).sum())
    return n, holes, int(orphans(can).sum()), int(op.sum())


def small_holes(can, most=4):
    op = can[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    sz = ndimage.sum(np.ones(lbl.shape), lbl, range(1, n + 1)) if n else []
    return int(sum(s_ for s_ in sz if s_ <= most))


def new_orphans(can, base, reach=4):
    o = orphans(can)
    near = ndimage.binary_dilation(orphans(base), structure=np.ones((2 * reach + 1, 2 * reach + 1)))
    return int((o & ~near).sum())


def checks(acts, base):
    """Per frame: pieces (8-connected: 1 is right), small enclosed holes and orphan outline squares beyond the design's
    own, colours outside the design's and the machine's palette (the hit flash aside), squares under the soles, opaque
    area against the design's."""
    pal = {tuple(int(v) for v in c) for c in DESIGN[DESIGN[..., 3] > 0][:, :3]}
    pal |= {tuple(int(v) for v in c) for c in MACHINE[MACHINE[..., 3] > 0][:, :3]}
    pal.add(OUTLINE)
    _, _, bo, ba = stats(base)
    bad_all = 0
    for tag, fr in acts.items():
        rep = []
        for j, (can, _) in enumerate(fr):
            op = can[..., 3] > 0
            n, _, _, area = stats(can)
            holes = small_holes(can)
            orphan = new_orphans(can, base)
            extra = len({tuple(int(v) for v in c) for c in can[op][:, :3]} - pal)
            under = int(op[SOLE + 1:].sum())
            bad = n > 1 or holes or orphan or under or (extra and tag != "hit")
            bad_all += bool(bad)
            rep.append(f"{j + 1}:{'!' if bad else ''}p{n} h{holes} o{orphan} c{extra} a{100 * area // ba}%")
        print(f"{tag:12s} " + "  ".join(rep))
    return bad_all


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
            sheet.save(os.path.join(out_dir, f"renata_{tag}{suffix}.png"))
        small = [t.resize((t.width * 3, t.height * 3), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"renata_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


def parts_sheet(out_dir, z=12):
    """The design with each part tinted (for checking the masks)."""
    os.makedirs(out_dir, exist_ok=True)
    tint = {BODY: None, ARM: (255, 60, 60), UPF: (60, 200, 255), FORE: (255, 220, 0), PISTOL: (255, 140, 0),
            LEG_N: (60, 255, 60), LEG_F: (200, 60, 255)}
    img = DESIGN.copy()
    for k, c in tint.items():
        if c is None:
            continue
        m = LAB == k
        img[m, :3] = (img[m, :3].astype(int) // 2 + np.array(c) // 2).astype(np.uint8)
    bg = Image.new("RGBA", (DW, DH), (40, 40, 40, 255))
    bg.alpha_composite(Image.fromarray(img))
    hb = HAIR_FILL[0].copy()
    bg2 = Image.new("RGBA", (DW, DH), (40, 40, 40, 255))
    d2 = DESIGN.copy()
    d2[LAB == ARM] = 0
    m = HAIR_FILL[1]
    d2[m] = hb[m]
    bg2.alpha_composite(Image.fromarray(d2))
    both = Image.new("RGB", (DW * 2 + 2, DH), (0, 0, 0))
    both.paste(bg.convert("RGB"), (0, 0))
    both.paste(bg2.convert("RGB"), (DW + 2, 0))
    both.resize((both.width * z, both.height * z), Image.NEAREST).save(os.path.join(out_dir, "renata_parts.png"))


# ------------------------------------------------------------------------------------------------- the game's frames
ORDER = ["idle", "run", "attack", "skill", "skill2", "skill2_fling", "skill_w", "ult", "hit", "dead"]


def one_of(can, px, py, hw, hh, need=0.5):
    """The 1x frame: each game pixel the commonest colour of the PPU squares under it (half of them drawn or more)."""
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


def down(can):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot). The pivot: the pivot
    column, FEET 1x rows above the ground line."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh), color=OUTLINE)[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


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
    for tag in ORDER:
        ones, hds = [], []
        for can, t in acts[tag]:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"renata_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"renata_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_renata#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the frames at 4x / 2x and a GIF per tag here (nothing written to the repo)")
    ap.add_argument("--parts", help="the design with its parts tinted here")
    a = ap.parse_args()
    if a.parts:
        parts_sheet(a.parts)
        return
    acts, base = actions()
    checks(acts, base)
    acts = add_flash(acts)             # after the checks: the light is not her palette and stands apart
    if a.review:
        review(acts, a.review)
        return
    export(acts)


if __name__ == "__main__":
    main()
