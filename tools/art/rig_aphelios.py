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
CW, CH = 130, 120
SOLE = 110                        # the canvas row of the design's last row (the soles)
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


# ------------------------------------------------------------------------------------------------- legs at any angle
# The 2026-10-22 redo (the user: 「厄斐琉斯也少动作帧 你也帮我补全吧」, picked one body for every weapon with each
# weapon's attack and Q its own): the legs bend - crouches, a kneel, lunges, jumps. A leg given as angles is drawn
# again from its hip under the coat as trousers - a thigh and a shin of the design's own lengths at League's angles
# (tools/lol/pose_joints.py on the clip's frame, the foreshortening kept: LOL below) - with the design's own boot put
# on the ankle whole. The left leg (LEG_N; League's R_ side) is behind, the right one (LEG_F; League's L_) in front.
HIPS = {LEG_N: (5.5, 49.5), LEG_F: (13.5, 49.5)}     # design (x, y) of each hip, under the coat
THIGH, SHIN = 8.5, 6.0                                 # design squares hip -> knee, knee -> ankle (ankle on row 64)
BOOT_TOP = 63                                          # the design row each boot is cut from (its top)
BOOT_DROP = DH - 1 - BOOT_TOP                          # rows from a boot's top to its sole
TROUSER = ((41, 50, 84), (35, 48, 68), (32, 35, 57), (22, 27, 41))   # across a leg, lit (upper left) to shaded
LEG_W = 3.6                                            # a trouser's width inside its outline
TAIL_ROWS = (44, 60)                                   # the coat's two tails: from the waist to their ends


def boot(k):
    """Leg k's boot: (squares, the column of the leg's middle in them) - the design's own, cut at BOOT_TOP."""
    m = (LAB == k) & (np.arange(DH)[:, None] >= BOOT_TOP)
    ys, xs = np.nonzero(m)
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = DESIGN[ys, xs]
    return sub, HIPS[k][0] - xs.min()


def capsule(segs, width):
    """(inside, v): squares whose middle lies within width / 2 of one of the segments (canvas, continuous), and each
    one's place across its segment (+1 the side toward the light, upper left; -1 the other)."""
    inside = np.zeros((CH, CW), bool)
    v = np.zeros((CH, CW))
    Y, X = np.mgrid[0:CH, 0:CW]
    for (x0, y0), (x1, y1) in segs:
        vx, vy = x1 - x0, y1 - y0
        L = math.hypot(vx, vy) or 1e-6
        ux, uy = vx / L, vy / L
        nx, ny = -uy, ux
        if nx + ny > 0:                                  # n toward the upper left
            nx, ny = -nx, -ny
        px, py = X + 0.5 - x0, Y + 0.5 - y0
        t = np.clip(px * ux + py * uy, 0, L)
        dx, dy = px - t * ux, py - t * uy
        d = np.hypot(dx, dy)
        m = d <= width / 2
        new = m & ~inside
        v[new] = ((dx * nx + dy * ny) / (width / 2))[new]
        inside |= m
    return inside, v


def limb_layer(segs, width, cols):
    """A limb as its own layer: the capsule coloured across (cols[0] on the lit side), an outline ring round it."""
    inside, v = capsule(segs, width)
    lay = np.zeros((CH, CW, 4), np.uint8)
    k = np.clip(((1 - v) / 2 * len(cols)).astype(int), 0, len(cols) - 1)
    for i, c in enumerate(cols):
        m = inside & (k == i)
        lay[m, :3] = c
        lay[m, 3] = 255
    ring = ndimage.binary_dilation(inside, structure=np.ones((3, 3))) & ~inside
    lay[ring, :3] = OUTLINE
    lay[ring, 3] = 255
    return lay


def leg_points(k, spec, x0, y0):
    """(hip, knee, ankle) of leg k on the canvas: spec = (thigh deg, shin deg[, thigh scale, shin scale]) - degrees
    from straight down, positive toward his front - the design's body at (x0, y0)."""
    t, s = spec[0], spec[1]
    ft, fs = (spec[2], spec[3]) if len(spec) > 2 else (1.0, 1.0)
    hx, hy = x0 + HIPS[k][0], y0 + HIPS[k][1]
    kx, ky = hx + THIGH * ft * math.sin(math.radians(t)), hy + THIGH * ft * math.cos(math.radians(t))
    ax, ay = kx + SHIN * fs * math.sin(math.radians(s)), ky + SHIN * fs * math.cos(math.radians(s))
    return (hx, hy), (kx, ky), (ax, ay)


def boot_at(ankle):
    """The canvas row a boot's top goes on for an ankle point (the design's ankle, 64.0, puts it on BOOT_TOP)."""
    return int(math.floor(ankle[1])) - 1


def sole_row(k, spec):
    """The design row of leg k's sole with the body standing (bob 0)."""
    _, _, ankle = leg_points(k, spec, 0, 0)
    return boot_at(ankle) + BOOT_DROP


def ground_bob(legs):
    """Rows the body goes down so the lower sole stands on the ground row (DH - 1 as designed)."""
    return (DH - 1) - max(sole_row(LEG_N, legs[0]), sole_row(LEG_F, legs[1]))


def draw_legs(can, legs, x0, y0):
    """The two legs at their angles, the left (behind) first: trousers, then the boot on the ankle - upright, or a
    quarter turn with a shin lying back (a kneeling leg: on its toes, the sole toward his back) or forward."""
    for k, spec in ((LEG_N, legs[0]), (LEG_F, legs[1])):
        hip, knee, ankle = leg_points(k, spec, x0, y0)
        lay = limb_layer([(hip, knee), (knee, ankle)], LEG_W, TROUSER)
        img, mid = BOOTS[k]
        h, w = img.shape[:2]
        if spec[1] < -55:            # the shin lies back: its top (the shaft) turned toward the knee on the right
            stamp(lay, np.rot90(img, -1).copy(), int(round(ankle[0])) - (h - 1), int(round(ankle[1] - mid)))
        elif spec[1] > 55:
            stamp(lay, np.rot90(img, 1).copy(), int(round(ankle[0])), int(round(ankle[1] - (w - mid))))
        else:
            stamp(lay, img, int(round(ankle[0] - mid)), boot_at(ankle))
        m = lay[..., 3] > 0
        can[m] = lay[m]


def sheared(lay, hip_row, lean):
    """The body leaning: every row above hip_row moved round(lean x its height over the hips / 45) columns (whole-row
    shifts; positive: toward his front)."""
    if not lean:
        return lay
    out = np.zeros_like(lay)
    for r in range(CH):
        k = int(round(lean * max(0, hip_row - r) / 45.0))
        if k > 0:
            out[r, k:] = lay[r, :-k]
        elif k < 0:
            out[r, :k] = lay[r, -k:]
        else:
            out[r] = lay[r]
    return out


def pose(bob=0, dx=0, legs=None, sway=0, hide=(), arm=None, extra=(), near_arm=0, lean=0, lift=0):
    """One frame on the canvas. The body (everything but the legs: the coat, the head, the arms, the rifle) bob rows
    down and dx columns on; legs: None - the design's own legs standing - or ((thigh, shin[, scales]) of the left leg,
    the same of the right) in degrees (leg_points): the legs drawn at those angles and the body sunk so the lower sole
    stands on the ground (bob is added to that); lean: columns the head moves toward his front over the hips (sheared);
    lift: rows the whole figure is off the ground (a jump). near_arm: the hanging near arm swung that many columns at the
    hand (whole-row shifts from the shoulder); sway: the coat's tails swayed back that many columns; parts in `hide`
    left out; arm: a callable drawing the far arm instead (it gets the canvas and the body's offset); extra: callables
    run last, the same way."""
    can = blank()
    x0 = OX + dx
    if legs is None:
        y0 = OY + bob
        for k in (LEG_N, LEG_F):                 # the legs as designed (the coat over their tops)
            put(can, DESIGN, LAB == k, x0, OY)
    else:
        y0 = OY + ground_bob(legs) + bob
        draw_legs(can, legs, x0, y0)
    lay = blank()
    body = (LAB >= 0) & ~part(LEG_N, LEG_F, TAIL_N, TAIL_F) & ~part(*hide)
    if arm is not None:
        body &= LAB != FAR_ARM
    if near_arm:
        body &= LAB != NEAR_ARM
        top, bot = np.nonzero((LAB == NEAR_ARM).any(1))[0][[0, -1]]
        for r in range(top, bot + 1):
            dxa = int(round(near_arm * (r - top) / max(1, bot - top)))
            m = np.zeros((DH, DW), bool)
            m[r] = LAB[r] == NEAR_ARM
            put(lay, DESIGN, m, x0 + dxa, y0)
    put(lay, DESIGN, body, x0, y0)
    if RIFLE in hide:      # the rifle off his back: the outline it shared with him left one square thick
        zone = np.zeros(lay.shape[:2], bool)
        ys, xs = np.nonzero(ndimage.binary_dilation(LAB == RIFLE, structure=np.ones((3, 3))))
        zone[np.clip(ys + y0, 0, CH - 1), np.clip(xs + x0, 0, CW - 1)] = True
        for _ in range(2):
            loose = orphans(lay) & zone
            if not loose.any():
                break
            lay[loose] = 0
    for k, leg in ((TAIL_N, LEG_N), (TAIL_F, LEG_F)):
        if k in hide:
            continue
        # each tail of the coat follows its leg: whole rows from the waist down moved toward the leg's knee (a bit
        # past it, toward the ankle), in proportion
        reach = 0.0
        if legs is not None:
            hip, knee, ankle = leg_points(leg, legs[0] if leg == LEG_N else legs[1], 0, 0)
            reach = (knee[0] - hip[0]) + 0.3 * (ankle[0] - knee[0])
        top, bot = TAIL_ROWS
        for r in range(top, bot + 1):
            m = np.zeros((DH, DW), bool)
            m[r] = LAB[r] == k
            put(lay, DESIGN, m, x0 - sway + int(round(reach * (r - top) / (bot - top))), y0)
    if arm is not None:
        arm(lay, x0, y0)
    for f in extra:
        f(lay, x0, y0)
    lay = sheared(lay, y0 + int(HIPS[LEG_N][1]), lean)
    m = lay[..., 3] > 0
    can[m] = lay[m]
    return up(can, lift) if lift > 0 else can


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


BOOTS = {k: boot(k) for k in (LEG_N, LEG_F)}


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


def calibrum_whole():
    """Calibrum whole: the weapon sheet's first piece brought to the design's density like the other four (W_K) - the
    design's own is cut where his arm and body cover it, so a rifle seen on its own (tossed, falling, lying, held up)
    takes this one. Levelled, the muzzle forward; its grip (the teal handle) in the middle."""
    import design_aphelios_cut as DC
    w = load(os.path.join(SRC, "hd", "weapons2.png"))
    lab, _ = ndimage.label(w[..., 3] > 0, structure=np.ones((3, 3)))
    m = lab == 1
    ys, xs = np.nonzero(m)
    sub = w[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
    up_ = snapped(G.complete_outline(DC.cut(sub, W_K), color=OUTLINE)[0])
    return np.rot90(up_, -1).copy()


CAL_WHOLE = calibrum_whole()
CAL_GRIP = (5, 13)                     # the teal handle in the levelled picture (rows 26-34 of the upright one)


# ------------------------------------------------------------------------------------------------- arms at any angle
# The far forearm (as designed raised: the hand beside his head, the elbow under it) turned about its elbow to any
# angle, the near arm (hanging, the hand at HAND_LOW) about its shoulder. Each square is taken from the design square it
# turns from (nearest), so a quarter turn is exact and any other angle is the thin limb drawn at that angle. Pivots
# sit on square middles (a quarter turn maps middles onto middles).
FORE_PIVOT = (21.5, 37.5)             # design (x, y): the far elbow (ELBOW's middle)
FORE_LEN = (20.5, 15.0)               # elbow -> the hand's grip: as designed / shortened (forward: FORE_CUT's rows out)
NEAR_PIVOT = (8.5, 30.5)              # design (x, y): the near shoulder, under the collar
NEAR_LEN = 17.0                       # shoulder -> the near hand's grip


def cut(mask):
    """The design's squares under mask cut to their box, and the box's top-left (x, y)."""
    ys, xs = np.nonzero(mask)
    sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
    sub[ys - ys.min(), xs - xs.min()] = DESIGN[ys, xs]
    return sub, (int(xs.min()), int(ys.min()))


FORE_FULL, _FB = cut(LAB == FAR_ARM)
FORE_PIV_FULL = (FORE_PIVOT[0] - _FB[0], FORE_PIVOT[1] - _FB[1])
# the forearm shortened for every angle but its own: design rows 29-33 (the navy sleeve between the gold band and the
# elbow guard) out - 25 squares raised beside the head read as an arm, levelled they read as a pole (FORE_CUT)
_CUT_ROWS = [r - _FB[1] for r in range(29, 34)]
FORE_SHORT = np.delete(FORE_FULL, _CUT_ROWS, axis=0)
FORE_PIV_SHORT = (FORE_PIV_FULL[0], FORE_PIV_FULL[1] - len(_CUT_ROWS))
NEAR_SPR, _NB = cut(LAB == NEAR_ARM)
NEAR_PIV = (NEAR_PIVOT[0] - _NB[0], NEAR_PIVOT[1] - _NB[1])


def stamp_turned(can, spr, piv, at, deg, under=False):
    """spr (its pivot piv: (x, y) in its squares) turned deg counter-clockwise on screen about the pivot, the pivot on
    canvas point `at`; each canvas square takes the sprite square it turns from."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    h, w = spr.shape[:2]
    r = math.hypot(max(piv[0], w - piv[0]), max(piv[1], h - piv[1])) + 1
    for Y in range(int(at[1] - r), int(at[1] + r) + 1):
        for X in range(int(at[0] - r), int(at[0] + r) + 1):
            if not (0 <= Y < can.shape[0] and 0 <= X < can.shape[1]):
                continue
            dx, dy = X + 0.5 - at[0], Y + 0.5 - at[1]
            sx = piv[0] + dx * c - dy * s
            sy = piv[1] + dx * s + dy * c
            i, j = int(math.floor(sy + 1e-6)), int(math.floor(sx + 1e-6))
            if 0 <= i < h and 0 <= j < w and spr[i, j, 3] > 0 and (not under or can[Y, X, 3] == 0):
                can[Y, X] = spr[i, j]


def held_turned(name, rifle, k, whole=False):
    """(picture, grip (row, col)) of the weapon - Calibrum levelled (whole: CAL_WHOLE) or `name` as held forward - k
    quarter turns counter-clockwise."""
    img, (gr, gc) = ((CAL_WHOLE, CAL_GRIP) if whole else (RIFLE_FWD, RIFLE_GRIP)) if rifle else held(name)
    for _ in range(k % 4):
        h, w = img.shape[:2]
        img, (gr, gc) = np.rot90(img, 1).copy(), (w - 1 - gc, gr)
    return img, (gr, gc)


def far_arm(theta=90, edx=0, edy=0, weapon=None, rifle=False, wdx=0, wdy=0, wrot=0, whole=False):
    """The far forearm at theta degrees about its elbow (moved edx, edy): 90 as designed (the hand beside his head),
    0 forward, 180 back, -90 down; in the hand the weapon (or Calibrum levelled: rifle; whole: CAL_WHOLE) by its grip
    (+ wdx, wdy), turned wrot quarter turns, behind the arm and the body."""
    def draw(can, x0, y0):
        own = abs(theta - 90) < 1e-6
        spr, piv, L = (FORE_FULL, FORE_PIV_FULL, FORE_LEN[0]) if own else (FORE_SHORT, FORE_PIV_SHORT, FORE_LEN[1])
        at = (x0 + FORE_PIVOT[0] + edx, y0 + FORE_PIVOT[1] + edy)
        stamp_turned(can, spr, piv, at, theta - 90)
        if weapon is not None or rifle:
            hx = at[0] + L * math.cos(math.radians(theta))
            hy = at[1] - L * math.sin(math.radians(theta))
            img, (gr, gc) = held_turned(weapon, rifle, wrot, whole)
            stamp(can, img, int(math.floor(hx - gc + 1e-6)) + wdx, int(math.floor(hy - gr + 1e-6)) + wdy, under=True)
    return draw


def near_arm_at(theta, weapon=None, wdx=0, wdy=0, wrot=0):
    """An `extra` drawing the near arm at theta degrees about its shoulder (-90: hanging as designed, 0 forward, 180
    back), its hand holding `weapon` (behind it); pose(hide=(NEAR_ARM,)) leaves the designed one out and the coat it
    covered is filled from round it."""
    def draw(can, x0, y0):
        at = (x0 + NEAR_PIVOT[0], y0 + NEAR_PIVOT[1])
        stamp_turned(can, NEAR_SPR, NEAR_PIV, at, theta + 90)
        if weapon is not None:
            hx = at[0] + NEAR_LEN * math.cos(math.radians(theta))
            hy = at[1] - NEAR_LEN * math.sin(math.radians(theta))
            img, (gr, gc) = held_turned(weapon, weapon == "cal", wrot)
            stamp(can, img, int(math.floor(hx - gc + 1e-6)) + wdx, int(math.floor(hy - gr + 1e-6)) + wdy, under=True)
    return draw


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
# League's run as rig numbers (tools/lol/pose_joints.py on aphelios_A_Run1, his A_Idle1 the rest; Riot's model is read
# locally, these numbers are all that is kept): (dx, lean, left leg, right leg) - the body's travel over the feet
# (League's pelvis x 0.83 squares a px: his legs are 0.55 of League's), the columns his head leans, each leg (thigh deg,
# shin deg from straight down, + toward his front; each bone's foreshortened share)
RUN = [
    (-1, 1, (-21, -22, 0.88, 0.88), (22, 14, 1.0, 0.99)),
    (0, 1, (-24, -53, 0.92, 0.75), (24, 2, 1.0, 0.94)),
    (0, 1, (8, -56, 1.0, 0.74), (-1, -2, 0.92, 0.93)),
    (0, 1, (22, -9, 0.98, 0.91), (-9, -9, 0.87, 0.87)),
    (-1, 1, (22, 7, 0.99, 0.99), (-9, -23, 0.84, 0.77)),
    (-1, 1, (20, -2, 0.99, 0.96), (-5, -58, 0.81, 0.66)),
    (0, 1, (5, -13, 0.99, 0.9), (20, -33, 0.99, 0.75)),
    (0, 1, (-12, -12, 0.92, 0.91), (23, 7, 1.0, 0.97)),
]

# The other actions' legs: League's stances read off its clips (A-E_Attack1, the Q's, A_Spell2, spell4, death - A-E
# his weapons: A Calibrum, B Severum, C Gravitum, D Infernum, E Crescendum) drawn as plain stances - the front (right)
# leg toward his front, the back one behind - since League's legs seen from the 3/4 side cross and fold toward the
# camera, and this coat to the ankles leaves a leg readable only by where its knee and boot go.
LEGS = {
    "wide": ((-25, -22), (28, 24)),          # feet apart, braced
    "wide_half": ((-12, -10), (14, 12)),
    "crouch": ((-30, 15), (50, -8)),         # the knees bent
    "deep": ((-45, 30), (70, -20)),          # down low
    "kneel": ((15, -95), (65, -5)),          # on the back knee, the front foot planted
    "kneel2": ((20, -95), (40, -95)),        # on both knees, sitting back
    "lunge": ((-40, -38), (55, 0)),          # the back leg straight out, the front knee bent
    "lunge_half": ((-25, -22), (35, 0)),
    "tuck": ((45, -55), (70, -30)),          # in the air, the knees drawn up
    "dangle": ((5, -10), (15, -5)),          # in the air, the legs hanging
    "stagger": ((-10, 5), (12, -2)),
}


def at(legs, **kw):
    """A frame with the named stance (LEGS), pose's other arguments as they are."""
    return pose(legs=LEGS[legs], **kw)


def mirrored(can):
    """The frame turned to face the other way about the pivot column (a turn in a spin: his only side is the 3/4
    front, so half a turn shows the same side facing back)."""
    out = blank()
    for x in range(CW):
        ox = 2 * PIV_X - x
        if 0 <= ox < CW:
            out[:, x] = can[:, ox]
    return out


def run_frames(**kw):
    """League's run (A_Run1, 8 frames of 133 ms): his legs at its angles, leaning into it, the near arm swinging
    against the front leg, the coat's tails trailing more on the push-off."""
    out = []
    for dx, lean, left, right in RUN:
        arm = -int(round(np.clip(right[0] / 10.0, -2, 2)))
        sway = 1 + int(abs(right[0]) > 15)
        out.append((pose(dx=dx, lean=lean + 1, legs=(left, right), near_arm=arm, sway=sway, **kw), RUN_MS))
    return out


def weapon_arm(w, theta, **k):
    """The far arm at theta holding weapon w (Calibrum: levelled, off his back)."""
    return far_arm(theta, rifle=w == "cal", weapon=None if w == "cal" else w, **k)


def raised(w, **k):
    """The far arm raised as designed, weapon w held up in it: the stance's hold (FORM_HOLD), Calibrum whole and upright
    (a quarter turn, its grip in the hand)."""
    if w == "cal":
        return far_arm(90, rifle=True, whole=True, wrot=1, **k)
    hold = {kk: v for kk, v in FORM_HOLD[w].items() if kk in ("wdx", "wdy")}
    hold.update(k)
    return far_arm(90, weapon=w, **hold)


def stand(w):
    """The stance a strip ends on: the design (Calibrum on his back) or weapon w's."""
    return pose() if w == "cal" else stance(w)


KICK_AT = 2                            # a basic attack's first kick frame (the shot 80 ms in: a_st 6 ticks)


def attack_frames():
    """Every cast strip: (canvas, ms) a frame. A basic attack: two frames up to the shot (80 ms), the kick three times
    (20 ms each: the muzzle flash's frames, muzzle_overs), the hold, the recovery, the weapon's stance - each weapon
    after its own League attack (A-E_Attack1)."""
    out = {}
    # the game plays `attack` itself on every attack's first tick, before the tree's CasterAnimation: the stance, so no
    # weapon flashes up for a tick
    out["attack"] = [(pose(), 100)]
    H = (RIFLE,)                       # every frame with a weapon in the far hand: Calibrum off his back
    W = weapon_arm
    kick = lambda f: [(f, ms) for ms in SHOT_MS]
    # Calibrum (A_Attack1): feet set wide, the rifle brought up and levelled, fired leaning back on the kick, held,
    # lowered
    out["a_cal"] = ([(at("wide_half", lean=1, hide=H, arm=W("cal", -15, edy=-1)), 40),
                     (at("wide", lean=1, hide=H, arm=W("cal", 0, edy=-3)), 40)]
                    + kick(at("wide", dx=-1, lean=-1, hide=H, arm=W("cal", 0, edy=-3, wdx=-1)))
                    + [(at("wide", hide=H, arm=W("cal", 0, edy=-3)), 70),
                       (at("wide_half", hide=H, arm=W("cal", -10, edy=-2)), 60), (stand("cal"), 80)])
    # Severum (B_Attack1): dropping into a crouch, onto the back knee, the pistol fired from the kneel, getting up
    out["a_sev"] = ([(at("crouch", hide=H, arm=W("sev", 0, edy=-2)), 40),
                     (at("kneel", hide=H, arm=W("sev", 0, edy=-3)), 40)]
                    + kick(at("kneel", dx=-1, lean=-1, hide=H, arm=W("sev", 0, edy=-3, wdx=-1)))
                    + [(at("kneel", hide=H, arm=W("sev", 0, edy=-3)), 80),
                       (at("crouch", hide=H, arm=W("sev", -10, edy=-2)), 60), (stand("sev"), 70)])
    # Gravitum (C_Attack1): a lunge with the cannon at the chest, pushed forward on the shot
    out["a_grav"] = ([(at("lunge_half", lean=1, hide=H, arm=W("grav", 0, edy=-1)), 40),
                      (at("lunge", lean=2, hide=H, arm=W("grav", 0, edy=-2)), 40)]
                     + kick(at("lunge", dx=-1, hide=H, arm=W("grav", 0, edy=-2, wdx=-1)))
                     + [(at("lunge", lean=1, hide=H, arm=W("grav", 0, edy=-2)), 80),
                        (at("lunge_half", hide=H, arm=W("grav", -10, edy=-1)), 60), (stand("grav"), 70)])
    # Infernum (D_Attack1): swung up over the head, brought down into a crouch, fired low and wide, back up
    out["a_inf"] = ([(pose(lean=-1, hide=H, arm=W("inf", 90, wrot=1, wdx=2, wdy=-6)), 40),
                     (at("crouch", lean=2, hide=H, arm=W("inf", 40, edy=-1)), 40)]
                    + kick(at("deep", dx=-1, lean=1, hide=H, arm=W("inf", -20, wdx=-1)))
                    + [(at("deep", lean=1, hide=H, arm=W("inf", -20)), 80),
                       (at("crouch", hide=H, arm=W("inf", -5, edy=-1)), 60), (stand("inf"), 70)])
    # Crescendum (E_Attack1): drawn back over the head leaning back, thrown in a lunge (the chakram leaves the hand on
    # the shot), the hand following through, the chakram caught again
    out["a_cre"] = ([(at("wide", lean=-2, hide=H, arm=W("cre", 135)), 40),
                     (at("wide", hide=H, arm=W("cre", 60, edy=-1)), 40)]
                    + kick(at("lunge", dx=-1, lean=2, hide=H, arm=far_arm(0, edy=-3)))
                    + [(at("lunge", lean=2, hide=H, arm=far_arm(-15, edy=-2)), 80),
                       (at("wide_half", hide=H, arm=W("cre", 15, edy=-1)), 60), (stand("cre"), 70)])
    out.update(q_frames())
    out["skill2"] = swap_frames("cal")
    out["ult"] = ult_frames("cal")
    out["dead"] = dead_frames("cal")
    # the add-on's weapon forms of W, R and the death (view.rs plays <w>_skill2 / <w>_ult / <w>_dead while that weapon
    # is in his main hand)
    for w in FORMS:
        out[f"{w}_skill2"] = swap_frames(w)
        out[f"{w}_ult"] = ult_frames(w)
        out[f"{w}_dead"] = dead_frames(w)
    return out


def q_frames():
    """Each weapon's Q after its own League clip, as long as its CasterAnimation in tools/kit/build_aphelios.py
    (333 / 233 / 233 / 300 / 267 ms), its moment where the kit puts it."""
    H = (RIFLE,)
    W = weapon_arm
    out = {}
    # Calibrum's Moonshot (A_Spell1_Activate, the shot 167 ms in): curled up low, springing up, the aim from a crouch,
    # the shot with a big kick
    out["q_cal"] = [(at("deep", lean=2, hide=H, arm=W("cal", -35, edy=1)), 50),
                    (at("tuck", lift=6, hide=H, arm=W("cal", 20, edy=-2)), 50),
                    (at("crouch", hide=H, arm=W("cal", 0, edy=-3)), 67),
                    (at("crouch", dx=-2, lean=-2, hide=H, arm=W("cal", 0, edy=-3, wdx=-1)), 80),
                    (at("crouch", hide=H, arm=W("cal", 0, edy=-3)), 50), (stand("cal"), 36)]
    # Severum's Onslaught (B_Spell1_Attack): feet wide firing, a turn round (the half turns mirrored), firing from a
    # crouch
    out["q_sev"] = [(at("wide", hide=H, arm=W("sev", 0, edy=-3)), 40),
                    (at("wide", dx=-1, lean=-1, hide=H, arm=W("sev", 0, edy=-3, wdx=-1)), 40),
                    (mirrored(at("crouch", hide=H, arm=W("sev", 20, edy=-2))), 40),
                    (mirrored(at("deep", hide=H, arm=W("sev", 0, edy=-2))), 40),
                    (at("crouch", dx=-1, lean=-1, hide=H, arm=W("sev", 0, edy=-3, wdx=-1)), 40), (stand("sev"), 33)]
    # Gravitum's Binding Eclipse (C_Spell1, the bind 133 ms in): the cannon raised, a jump with it over the head,
    # landing low with it levelled
    out["q_grav"] = [(at("crouch", hide=H, arm=W("grav", 90, wdx=3, wdy=-4)), 40),
                     (at("tuck", lift=8, hide=H, arm=W("grav", 90, edy=-2, wdx=3, wdy=-6)), 50),
                     (at("deep", hide=H, arm=W("grav", 30, edy=-2)), 43),
                     (at("crouch", hide=H, arm=W("grav", 0, edy=-2)), 60), (stand("grav"), 40)]
    # Infernum's Duskwave (D_Spell1A, the wave 167 ms in): held low and wound back behind, swept forward in a lunge,
    # followed through
    out["q_inf"] = [(at("wide", lean=-1, hide=H, arm=W("inf", -60)), 60),
                    (at("wide", lean=-2, hide=H, arm=W("inf", -85)), 50),
                    (at("lunge", lean=2, hide=H, arm=W("inf", -25)), 57),
                    (at("lunge", lean=3, hide=H, arm=W("inf", 5, edy=-1)), 60),
                    (at("lunge_half", lean=1, hide=H, arm=W("inf", 25, edy=-2)), 40), (stand("inf"), 33)]
    # Crescendum's Sentry (E_Spell1, tossed 167 ms in): a hop, landing low, the turret tossed out of the hand
    out["q_cre"] = [(at("crouch", hide=H, arm=W("cre", 60, edy=-1)), 50),
                    (at("tuck", lift=6, hide=H, arm=W("cre", 90)), 60),
                    (at("deep", hide=H, arm=W("cre", 30, edy=-1)), 57),
                    (at("deep", lean=1, hide=H, arm=far_arm(-20)), 60), (stand("cre"), 40)]
    return out


def thrown(w, dx, dy, k):
    """An `extra` drawing weapon w (Calibrum: whole) on its own, k quarter turns, its grip at (dx, dy) from the far
    elbow - a weapon in the air."""
    def draw(can, x0, y0):
        img, (gr, gc) = held_turned(w, w == "cal", k, whole=True)
        stamp(can, img, int(x0 + FORE_PIVOT[0] + dx - gc), int(y0 + FORE_PIVOT[1] + dy - gr), under=True)
    return draw


def dropped(w, dx):
    """An `extra` drawing weapon w (Calibrum: whole) lying on the ground, levelled, its grip dx columns in front of the
    pivot (wherever his body has sunk to)."""
    def draw(can, x0, y0):
        img, (gr, gc) = held_turned(w, w == "cal", 0, whole=True)
        stamp(can, img, PIV_X + dx - gc, SOLE + 1 - img.shape[0], under=True)
    return draw


def swap_frames(w):
    """W, the weapons changing hands (League's A_Spell2, 300 ms): down low, a spring up with the main weapon raised,
    tossed over the head at the top (a quarter turn in the air), caught landing, rising, the stance."""
    H = (RIFLE,)
    W = lambda theta, **k: weapon_arm(w, theta, **k)
    return [(at("deep", hide=H, arm=W(-30)), 50),
            (at("tuck", lift=6, hide=H, arm=raised(w)), 50),
            (at("tuck", lift=9, hide=H, arm=far_arm(90), extra=(thrown(w, 2, -30, 1),)), 50),
            (at("deep", hide=H, arm=raised(w)), 50),
            (at("crouch", hide=H, arm=W(45)), 50), (stand(w), 50)]


def ult_frames(w):
    """R, Moonlight Vigil (League's spell4, 400 ms, the moonlight 230 ms in): a crouch, the leap, the apex, firing down
    from the air with a kick, falling, landing low, the stance."""
    H = (RIFLE,)
    W = lambda theta, **k: weapon_arm(w, theta, **k)
    return [(at("crouch", hide=H, arm=W(-15, edy=-1)), 50),
            (at("tuck", lift=9, hide=H, arm=W(45, edy=-2)), 60),
            (at("dangle", lift=13, hide=H, arm=W(15, edy=-3)), 120),
            (at("dangle", lift=13, dx=-1, lean=-1, hide=H, arm=W(-20, edy=-3, wdx=-1)), 60),
            (at("dangle", lift=5, hide=H, arm=W(-10, edy=-2)), 40),
            (at("deep", hide=H, arm=W(-15, edy=-1)), 30), (stand(w), 40)]


def dead_frames(w):
    """Death (League's death, 1040 ms): struck back, staggering, the weapon flung up and falling away, the knees
    giving, down on both knees, slumping forward over them, still. w: the weapon in his hand (cal: Calibrum)."""
    H = (RIFLE,)
    W = lambda theta, **k: weapon_arm(w, theta, **k)
    limp = far_arm(-80, edy=2)
    fall = lambda dx, dy, k: (thrown(w, dx, dy, k),)
    lying = (dropped(w, 12),)
    return [(pose(dx=-1, lean=-2, hide=H, arm=W(-30)), 100),
            (at("stagger", dx=-2, lean=-3, hide=H, arm=limp, extra=fall(6, -34, 1)), 100),
            (at("stagger", dx=-2, lean=-1, hide=H, arm=limp, extra=fall(10, -18, 2)), 100),
            (at("crouch", dx=-2, lean=1, hide=H, arm=limp, extra=fall(12, 4, 3)), 80),
            (at("kneel2", dx=-2, lean=2, hide=H, arm=limp, extra=lying), 80),
            (at("kneel2", dx=-2, lean=3, hide=H, arm=limp, extra=lying), 100),
            (at("kneel2", dx=-2, lean=5, bob=1, hide=H, arm=far_arm(-90, edy=3), extra=lying), 120),
            (at("kneel2", dx=-2, lean=7, bob=2, hide=H, arm=far_arm(-90, edy=4), extra=lying), 360)]


def stance(w):
    """Weapon w's standing frame (its <w>_idle's first): Calibrum off his back, w in the raised hand (Infernum low)."""
    return pose(hide=(RIFLE,), arm=arm_up(w, **FORM_HOLD[w]))


def flourish_frames(w=None):
    """A fidget for the idle reel and the ban/pick card (tools/art/hero_reels.json picks it; the game never plays the
    tag itself - the user, 2026-10-22: the idle is frame 0 held with snippets, and his actions are all too big for one):
    Calibrum's form runs the raised hand back over his hair and down again; a weapon held up is twirled in the hand
    (quarter turns about its grip: exact); Infernum, held low, is nudged forward twice."""
    if w is None:
        return [(pose(), 120), (pose(arm=far_arm(105)), 110), (pose(lean=-1, arm=far_arm(122)), 160),
                (pose(arm=far_arm(105)), 110)]
    if w == "inf":
        return [(stance("inf"), 120)] + [(pose(hide=(RIFLE,), arm=arm_up("inf", low=True, wdx=k, wdy=-(k // 2))), 110)
                                         for k in (2, 4)]
    hold = {k: v for k, v in FORM_HOLD[w].items() if k in ("wdx", "wdy")}
    return [(pose(hide=(RIFLE,), arm=far_arm(90, weapon=w, wrot=k, **hold)), 90) for k in range(4)]


def up(can, k):
    """The whole frame k rows up (a leap: nothing of him moves apart)."""
    if k <= 0:
        return can
    out = blank()
    out[:-k] = can[k:]
    return out


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
    """{a_<w>: [(the flash on the PPU canvas, its 1x picture) or None, a frame]}: the three kick frames (from KICK_AT)
    one flash frame each, its root (the box's left edge, its middle row) on the weapon's drawn front, x PPU nearest."""
    out = {}
    for w in WEAPONS:
        tag = f"a_{w}"
        fr = flash_frames(w)
        overs = [None] * len(acts[tag])
        for i in range(3):
            can = acts[tag][KICK_AT + i][0]
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
            overs[KICK_AT + i] = (ov, f)
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
    acts["flourish"] = flourish_frames()
    for w in FORMS:
        acts[f"{w}_flourish"] = flourish_frames(w)
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


def gaps(can):
    """Enclosed clear squares that are not the space between his legs (a gap a trouser or boot square borders) nor a
    weapon's own opening (at least half the colours round it a weapon's)."""
    op = can[..., 3] > 0
    lbl, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    trouser = np.zeros(op.shape, bool)
    legs = set(TROUSER) | {tuple(int(v) for v in c) for img, _ in BOOTS.values() for c in img[img[..., 3] > 0][:, :3]}
    for c in legs - {OUTLINE}:
        trouser |= op & np.all(can[..., :3] == c, -1)
    out = 0
    for k in range(1, n + 1):
        m = lbl == k
        ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
        if (ring & trouser).any():
            continue
        around = {tuple(int(v) for v in c) for c in can[ring][:, :3]} - {OUTLINE}
        if around and len(around & WEAPON_COLOURS) * 2 >= len(around):
            continue                   # a weapon's own opening (the chakram's ring closed by his head)
        out += int(m.sum())
    return out


WEAPON_COLOURS = {tuple(int(v) for v in c) for img in list(WEAPON.values()) + [CAL_WHOLE]
                  for c in img[img[..., 3] > 0][:, :3]} - {OUTLINE}


def checks(acts, base):
    """Per frame: pieces (8-connected; a weapon in the air is one more), enclosed gaps (gaps: not between the legs)
    and orphan outline squares beyond the design's own, colours outside the design's palette (the hits' flash aside),
    squares under the soles, opaque area against the design's; printed as one line a tag, '!' on a frame with a
    fault."""
    pal = {tuple(int(v) for v in c) for c in DESIGN[DESIGN[..., 3] > 0][:, :3]}
    _, _, bo, ba = stats(base)
    stand_gaps = {w: gaps(finish(stance(w), base)) for w in FORMS}
    for tag, fr in acts.items():
        rep = []
        w = tag.split("_")[0] if tag.split("_")[0] in FORMS else tag.split("_")[1] if tag.startswith(("a_", "q_")) else None
        own = stand_gaps.get(w, gaps(base))
        for j, (can, _) in enumerate(fr):
            op = can[..., 3] > 0
            n, _, _, area = stats(can)
            holes = gaps(can)
            orphan = new_orphans(can, base)
            extra = len({tuple(int(v) for v in c) for c in can[op][:, :3]} - pal)
            under = int(op[SOLE + 1:].sum())
            airborne = tag.endswith(("dead", "skill2")) and n == 2
            flashed = tag.endswith("hit") and j == 0          # the flash's colours: no trousers to tell the legs by
            bad = (n != 1 and not airborne) or (holes > own and not flashed) or orphan or under or (extra and not flashed)
            rep.append(f"{j + 1}:{'!' if bad else ''}p{n} h{holes - own:+d} o{orphan} c{extra} a{100 * area // ba}%")
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
    + [f"{w}_{t}" for w in ("sev", "grav", "inf", "cre") for t in ("skill2", "ult", "dead")]     + ["flourish"] + [f"{w}_flourish" for w in ("sev", "grav", "inf", "cre")]


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
