#!/usr/bin/env python3
"""league_rell's action frames posed from the approved designs' own squares (no Codex strips: the user, 2026-10-16,
「动作帧你自己做吧 参考塔姆的方式」 - tools/art/rig_tahmkench.py's way).

    python tools/art/rig_rell.py --review DIR        # every tag on the canvas, 6x sheets + a 3x GIF per tag
    python tools/art/rig_rell.py                     # the frames -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero rell && python tools/art/ppu_hd.py --hero rell

Two designs (tools/art/design_rell_cut.py, the user's picks):
  A, mounted = Codex's step-1 take A-2 read back on its own grid (assets/source/rell/hd/modelA2.png, 100 x 86 squares,
    1.95 a game pixel) - the user picked it pixelated to PPU 1.5 (design_A.png, 66 rows = 44 game rows). Posed at that
    native density, every frame brought to PPU 1.5 the same way (pixel_down.pixelate, the grid through the same point,
    the same palette): the standing frame IS design_A.
  B, dismounted = take B-2 cut evenly to 60 rows (design_B.png, 48 x 60 at PPU 1.5, 40 game rows), posed at PPU 1.5.
Posed only losslessly (memory no-deformation-lossless-poses): whole-part moves, quarter turns, row shifts of the horse's
legs (the shank slants, the hoof is carried whole), layering (the body over the legs' tops). The lance's thrust repeats
its shaft's column X_EXT (a uniform cone there) to push the tip out, or drops columns to pull it in. The W and death
frames break the horse into pieces that all move, so nothing behind a piece is ever shown.
Actions (League's clips: Run_Slow, Auto_Attack1, Spell1, Rell_Spell2_Dismount, Spell2_Flip, Rell_Mounted_Spell4_Running,
Death; tools/lol/pose_ref.py with the horse's textures, Armor_* hidden mounted, Horse_* hidden on foot):
  idle 8      breathing: the horse and her sink 0-2 native rows over the standing legs
  run 8       Run_Slow (League's move at her speed, a 1.0 s trot): the diagonal pairs (near fore + far hind, then the
              other two) swing and lift as League's hooves do (their x from the hoof joints, scaled), the body bobbing
  attack 6    the lance thrust: drawn back, out with the forehand stepping in (the blow on frame 3), back
  skill 5     Shattering Strike: gathering, the forehand up, the lunge with the lance far out (the blow on frame 4)
  skill2 6    Crash Down: crouch, the leap, the horse bursting into armour pieces while she (B, in that armour) rises,
              the apex, the fall, the landing crouch on foot
  skill2_up 4 Mount Up: on foot crouching, rising as the pieces come back, the horse formed in the air, the charge
  ult 6       Magnet Storm: the stamp, the horse rearing, the second stamp with the lance out, held, back
  f_ult 6     the same on foot (League's Biped_Spell4_Cast): the stamp, a hop, the second stamp, held, back
  hit 2       moved back with a white flash
  dead 8      a flinch, the horse kneels, it comes loose, falls apart, the pieces land and bounce, she lies among
              them, held
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
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rell")
STEM = os.path.join(ROOT, "league", "champions", "league_rell")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.5
FEET = 11                         # 1x rows from the pivot down to the ground row
ORDER = ["idle", "run", "attack", "skill", "skill2", "skill2_up", "ult", "hit", "dead",
         "f_idle", "f_run", "f_attack", "f_skill", "f_hit", "f_dead", "f_ult"]


def lp(path):
    path = os.path.abspath(path)
    pre = chr(92) * 2 + "?" + chr(92)
    return pre + path if os.name == "nt" and not path.startswith(pre) else path


def load(path):
    return np.asarray(Image.open(lp(path)).convert("RGBA")).copy()


# ------------------------------------------------------------------------------------------------- A, native
A0 = load(os.path.join(SRC, "hd", "modelA2.png"))
AH, AW = A0.shape[:2]                                 # 86 x 100
A_OP = A0[..., 3] > 0
NATIVE = AH / 44.0                                    # squares a game pixel
KA = PPU / NATIVE
PAL_A = PD.palette_of(A0)                             # design_rell_cut made design_A with these (pixelate's defaults)
OUT_A = PD.edge_colour(A0)
ANCHOR = (50, AH)                                     # design_A's pixelate grid ran through (W / 2, H)

LEG_TOP = 66                                          # the four legs are apart from this row down
HOOF_TOP = 76                                         # the hooves (rows 76-85) are carried whole


def legs():
    lbl, n = ndimage.label(A_OP[LEG_TOP:])
    out = []
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > 100:
            full = np.zeros((AH, AW), bool)
            full[LEG_TOP:] = m
            out.append(full)
    out.sort(key=lambda m: np.nonzero(m.any(0))[0].min())
    return out


L1, L2, L3, L4 = legs()                               # hind near, hind far, fore near, fore far (left to right)
LEGS = {"hn": L1, "hf": L2, "fn": L3, "ff": L4}
LEG_ORDER = ["hf", "ff", "hn", "fn"]                  # the far legs first
ALL_LEGS = L1 | L2 | L3 | L4
X_EXT = 76                                            # the lance's shaft column repeated for a thrust (rows LANCE_ROWS)
LANCE_ROWS = (20, 37)


def box(r0, r1, c0, c1):
    m = np.zeros((AH, AW), bool)
    m[r0:r1 + 1, c0:c1 + 1] = True
    return m & A_OP


def colour_set(a, op):
    return {tuple(int(v) for v in c) for c in a[op][:, :3]}


def cls(pred):
    """Squares of A whose colour passes pred(r, g, b)."""
    rgb = A0[..., :3].astype(int)
    return A_OP & pred(rgb[..., 0], rgb[..., 1], rgb[..., 2])


# her leg down the horse's flank: the bodysuit's blue-violet, the skin and red-brown straps, the boot, and the dark
# squares round them, in rows 34-66 between columns 37 and 50
_blue = cls(lambda r, g, b: (b > r + 15) & (b > g + 10))
_red = cls(lambda r, g, b: (r > g + 40) & (r > b + 30))
_dark = cls(lambda r, g, b: r + g + b < 110)
_her = (_blue | _red) & box(34, 66, 37, 50)
LANCE_BUTT = box(22, 33, 22, 38)
LANCE = box(20, 36, 52, AW - 1) | LANCE_BUTT
RIDER = (box(0, 35, 26, 51) & ~LANCE_BUTT) | box(0, 21, 52, 58)
RIDER |= _her | (ndimage.binary_dilation(_her, structure=np.ones((3, 3))) & _dark & box(34, 66, 37, 50))
RIDER &= ~LANCE
HORSE = A_OP & ~RIDER & ~LANCE & ~ALL_LEGS
RIDER_CHIN = 19                                       # her hair top to the chin, A's rows
PIECES = {                                            # the horse's armour, broken where W and death break it
    "tail": HORSE & box(0, AH - 1, 0, 13),
    "rear": HORSE & box(0, AH - 1, 14, 37),
    "front": HORSE & box(0, AH - 1, 38, 51),
    "head": HORSE & box(0, AH - 1, 52, AW - 1),
    "hn": L1, "hf": L2, "fn": L3, "ff": L4,
}


def extend(a, ext):
    """The lance's tip pushed out ext columns (its shaft column X_EXT repeated) or pulled in (columns from X_EXT on
    dropped) - only in the lance's rows, right of X_EXT, where nothing but the lance is drawn."""
    if ext == 0:
        return a
    r0, r1 = LANCE_ROWS
    out = np.zeros((a.shape[0], a.shape[1] + max(ext, 0), 4), np.uint8)
    out[:, :a.shape[1]] = a
    band = a[r0:r1 + 1]
    out[r0:r1 + 1, X_EXT:] = 0
    if ext > 0:
        for i in range(ext):
            out[r0:r1 + 1, X_EXT + i] = band[:, X_EXT]
        out[r0:r1 + 1, X_EXT + ext:X_EXT + ext + a.shape[1] - X_EXT] = band[:, X_EXT:]
    else:
        tail = band[:, X_EXT - ext:]
        out[r0:r1 + 1, X_EXT:X_EXT + tail.shape[1]] = tail
    return out


# the native canvas
NW, NH = 280, 200
NG = 170                                              # the native ground line (the first row under the hooves)
AX0, AY0 = 90, NG - AH


def ncan():
    return np.zeros((NH, NW, 4), np.uint8)


def put(dst, src, m, dx, dy):
    ys, xs = np.nonzero(m)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    dst[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]


def leg(dst, name, ldx=0, lift=0, dx=0):
    """A leg from its own squares: the shank's rows slanting toward the hoof's offset, the hoof moved whole by ldx,
    the whole leg lifted `lift` rows (its top goes up under the body)."""
    m = LEGS[name]
    ys, xs = np.nonzero(m)
    t = np.clip((ys - LEG_TOP + 1) / (HOOF_TOP - LEG_TOP + 1), 0, 1)
    k = np.round(ldx * t).astype(int)
    ty, tx = AY0 + ys - lift, AX0 + xs + dx + k
    ok = (ty >= 0) & (ty < NH) & (tx >= 0) & (tx < NW)
    dst[ty[ok], tx[ok]] = A0[ys[ok], xs[ok]]


def mounted(dx=0, sink=0, lift=0, ext=0, lg=None, flash=False):
    """A standing on the native canvas: the body (horse, her, lance) dx forward and `sink` rows down over the legs,
    everything `lift` rows up, the lance's tip ext columns out; lg: {leg: (hoof dx, lift)}."""
    can = ncan()
    lg = lg or {}
    for name in LEG_ORDER:
        ldx, ll = lg.get(name, (0, 0))
        leg(can, name, ldx, ll + lift, dx)
    src = extend(A0, ext)
    body = np.zeros(src.shape[:2], bool)
    body[:, :] = src[..., 3] > 0
    body[:, :AW] &= ~ALL_LEGS
    put(can, src, body, AX0 + dx, AY0 + sink - lift)
    can[NG:] = 0
    return can


def pieces(offsets, rider=None, lance=None):
    """The horse broken: each piece of PIECES moved by offsets[name] = (dx, dy) (missing: not drawn); rider / lance:
    (dx, dy, quarter turns) or None."""
    can = ncan()
    for name in ["tail", "rear", "hf", "ff", "front", "hn", "fn", "head"]:
        if name in offsets:
            ddx, ddy = offsets[name]
            put(can, A0, PIECES[name], AX0 + ddx, AY0 + ddy)
    for part, spec in ((RIDER, rider), (LANCE, lance)):
        if spec is None:
            continue
        ddx, ddy, k = spec
        ys, xs = np.nonzero(part)
        sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
        sub[ys - ys.min(), xs - xs.min()] = A0[ys, xs]
        if k:         # fallen forward on the ground (lie(): the head upright), its left at the part's old left + ddx
            sub = lie(sub, RIDER_CHIN - ys.min())
            y0 = NG - sub.shape[0] + ddy
        else:
            y0 = AY0 + ys.min() + ddy
        x0 = AX0 + xs.min() + ddx
        put(can, sub, sub[..., 3] > 0, x0, y0)
    can[NG:] = 0
    return can


def on_ground(name, dx=0):
    """The offset that sets a piece on the ground line, dx columns aside."""
    ys = np.nonzero(PIECES[name].any(1))[0]
    return dx, (NG - 1) - (AY0 + ys.max())


# ------------------------------------------------------------------------------------------------- the PPU canvas
CW, CH = 180, 140
GY = 124                                              # the ground line (the first row under the soles / hooves)
PX = 80                                               # the pivot column (the horse's middle, her feet's middle)
PXA = PX + 5                                          # where A's pixelate grid point (ANCHOR) lands: the hooves' middle
                                                      # is 6.5 native columns left of it


def blank():
    return np.zeros((CH, CW, 4), np.uint8)


def to_ppu(native, dst=None):
    """A native canvas brought to PPU 1.5 on design_A's grid and laid on the PPU canvas."""
    small, (nx0, ny0) = PD.pixelate(native, KA, (AX0 + ANCHOR[0], NG), OUT_A, PAL_A)
    dst = blank() if dst is None else dst
    ys, xs = np.nonzero(small[..., 3] > 0)
    ty, tx = ys + GY - ny0, xs + PXA - nx0
    ok = (ty >= 0) & (ty < CH) & (tx >= 0) & (tx < CW) & (ty < GY)
    dst[ty[ok], tx[ok]] = small[ys[ok], xs[ok]]
    return dst


# ------------------------------------------------------------------------------------------------- B, at PPU
B0 = load(os.path.join(SRC, "hd", "design_B.png"))
BH, BW = B0.shape[:2]                                 # 60 x 48
B_OP = B0[..., 3] > 0
BX0, BY0 = PX - 16, GY - BH                           # the feet's middle (columns 3-30) on the pivot


def bbox(r0, r1, c0, c1):
    m = np.zeros((BH, BW), bool)
    m[r0:r1 + 1, c0:c1 + 1] = True
    return m & B_OP


B_HEM = 51                                            # the armour skirt's hem: below it only the legs and the lance
# the legs under the hem: (rows, columns, the first row of the boot carried whole); the shin above it slants
B_LEGS = {"n": ((52, BH - 1), (2, 9), 55), "f": ((47, BH - 1), (22, 31), 53)}


def bleg_mask(name):
    (r0, r1), (c0, c1), _ = B_LEGS[name]
    return bbox(r0, r1, c0, c1)


B_FOOT_N, B_FOOT_F = bleg_mask("n"), bleg_mask("f")
B_BODY = B_OP & ~B_FOOT_N & ~B_FOOT_F


def bleg(dst, name, ox, oy, fdx=0, lift=0):
    """A leg of B: its shin's rows slanting toward the boot, the boot moved whole by fdx, all lifted `lift` rows."""
    (r0, r1), _, boot = B_LEGS[name]
    m = bleg_mask(name)
    ys, xs = np.nonzero(m)
    t = np.clip((ys - r0 + 1) / (boot - r0 + 1), 0, 1)
    k = np.round(fdx * t).astype(int)
    ty, tx = oy + ys - lift, ox + xs + k
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    dst[ty[ok], tx[ok]] = B0[ys[ok], xs[ok]]


B_WAIST = 30                                          # the upper body (a slump bows it over the hips) above this row


def dismounted(dst=None, dx=0, sink=0, lift=0, nf=(0, 0), ff=(0, 0), bow=(0, 0), lance_up=False):
    """B on the PPU canvas: the body dx forward, `sink` rows down over the legs, all `lift` rows up; the near / far
    boot moved fdx with its lift: nf / ff = (fdx, lift); bow: the upper body moved (dx, dy) over the hips; lance_up:
    the lance turned a quarter counter-clockwise about its grip (raised up and forward over her head)."""
    dst = blank() if dst is None else dst
    bleg(dst, "f", BX0 + dx, BY0 - lift, ff[0], ff[1])
    bleg(dst, "n", BX0 + dx, BY0 - lift, nf[0], nf[1])
    if lance_up:
        # the whole lance: everything of B from row 27 down and column 25 on but her boots, with B_LANCE (its warm
        # squares alone left the shaft's dark shading behind as a loose stick and turned a dotted line)
        lm = B_LANCE_WHOLE
        put(dst, B0, B_BODY & ~lm, BX0 + dx, BY0 + sink - lift)
        ys, xs = np.nonzero(lm)
        sub = np.zeros((ys.max() - ys.min() + 1, xs.max() - xs.min() + 1, 4), np.uint8)
        sub[ys - ys.min(), xs - xs.min()] = B0[ys, xs]
        t = np.rot90(sub, 1).copy()                     # the grip (the box's top-left) to the bottom-left
        gx, gy = BX0 + dx + xs.min(), BY0 + sink - lift + ys.min()
        put(dst, t, t[..., 3] > 0, gx, gy - t.shape[0] + 1)
        dst[GY:] = 0
        return dst
    if bow == (0, 0):
        put(dst, B0, B_BODY, BX0 + dx, BY0 + sink - lift)
    else:
        upper = B_BODY & (np.arange(BH)[:, None] < B_WAIST)
        put(dst, B0, B_BODY & ~upper, BX0 + dx, BY0 + sink - lift)
        put(dst, B0, upper, BX0 + dx + bow[0], BY0 + sink - lift + bow[1])
    dst[GY:] = 0
    return dst


def shift(a, dx, dy):
    out = np.zeros_like(a)
    ys, xs = np.nonzero(a[..., 3] > 0)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < a.shape[0]) & (tx >= 0) & (tx < a.shape[1]) & (ty < GY)
    out[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
    return out


def flash(a, k=0.55):
    out = a.copy()
    m = out[..., 3] > 0
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


# ------------------------------------------------------------------------------------------------- the run
# League's Run_Slow (1.0 s, 8 frames 125 ms apart): per frame the hooves' x about their own mean and their lift, game px
# at 44 rows (H_L_Front_Foot / H_R_Back_Foot - one diagonal pair; the other pair is the same 4 frames later), and the
# pelvis's rise
FORE = [(4.1, 6.3), (8.3, 6.0), (10.3, 4.4), (3.1, 0.0), (-5.0, 0.0), (-8.1, 1.4), (-9.2, 5.3), (-3.3, 5.9)]
HIND = [(-0.3, 5.7), (5.5, 5.4), (8.6, 4.0), (6.1, 0.3), (-2.1, 0.3), (-5.6, 1.9), (-7.5, 4.9), (-4.8, 5.6)]
PELVIS = [-1.5, 0.7, 2.7, -0.9, -1.6, 0.7, 2.7, -0.8]
RUN_K = 0.35                                          # native columns a League px of swing
RUN_LIFT = 0.45                                       # native rows a League px of lift (the shank stays straight)
RUN_MS = 125
FAR_K = 0.6                                           # the far legs' swing (seen across the body, shorter)


def run_frame(i):
    j = (i + 4) % 8
    def q(v):
        return int(round(v[0] * RUN_K)), int(round(v[1] * RUN_LIFT))
    far = lambda v: (v[0] * FAR_K, v[1])
    lg = {"fn": q(FORE[i]), "hf": q(far(HIND[i])), "ff": q(far(FORE[j])), "hn": q(HIND[j])}
    sink = int(round((2.7 - PELVIS[i]) * 0.4))
    return to_ppu(mounted(sink=sink, lg=lg))


# ------------------------------------------------------------------------------------------------- her walk on foot
# League's Biped_Walk (a 0.82 s cycle, 8 frames 103 ms apart): each foot's x about its mean and its lift, game px at 40
# rows (L_Foot = the far, forward foot; R_Foot = the near one), and the pelvis's rise
WALK_F = [(19.1, 1.2), (14.1, 0.0), (7.6, 0.0), (1.5, 0.0), (-4.6, 0.0), (-11.2, 0.3), (-14.8, 2.5), (-12.0, 4.7)]
WALK_N = [(-8.6, 0.0), (-15.0, 1.3), (-15.5, 4.5), (-4.0, 5.0), (9.9, 2.7), (15.2, 0.0), (11.7, 0.0), (6.6, 0.0)]
WALK_PEL = [1.4, -2.2, -2.0, -0.2, 2.7, 0.5, -2.3, -1.5]
WALK_K = 0.15                                         # squares a League px of swing (her boots stay under the hem)
WALK_LIFT = 0.3
WALK_MS = 103


def walk_frame(i):
    q = lambda v: (int(round(v[0] * WALK_K)), int(round(v[1] * WALK_LIFT)))
    sink = int(round((2.7 - WALK_PEL[i]) * 0.3))
    return dismounted(sink=sink, nf=q(WALK_N[i]), ff=q(WALK_F[i]))


def b_lance():
    """B's lance (its gold and brown squares from row 28 down, right of column 21, and the dark squares touching
    them there): it stays planted where it stood when she falls."""
    rgb = B0[..., :3].astype(int)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    zone = np.zeros((BH, BW), bool)
    zone[28:, 22:] = True
    warm = B_OP & zone & (r - b > 60) & (g - b > 15)
    dark = B_OP & zone & (r + g + b < 120)
    return warm | (ndimage.binary_dilation(warm, structure=np.ones((3, 3))) & dark)


B_LANCE = b_lance()
_rr, _cc = np.mgrid[0:BH, 0:BW]
# f_ult's raised lance: the band along the lance's slant (it runs from her grip at row 28, column 22 down to the right,
# ~0.8 columns a row) - the narrow upright strip down the skirt's edge stays with her (turned, it stuck out sideways)
B_LANCE_WHOLE = B_OP & (_rr >= 27) & (_cc >= 25) & (_cc - 22 >= (_rr - 28) * 0.45) & ~B_FOOT_N & ~B_FOOT_F


def lie(piece, chin):
    """A figure (cropped RGBA) face down on the ground, fallen forward: everything under the chin row turned a quarter
    clockwise (the neck to the right), the head kept upright beside the neck, both resting on the ground line ->
    (picture, its width)."""
    head, rest = piece[:chin], piece[chin:]
    crop = lambda a: a[np.ix_(np.any(a[..., 3] > 0, 1), np.any(a[..., 3] > 0, 0))]
    head, rest = crop(head), crop(np.rot90(rest, -1).copy())
    h = max(head.shape[0], rest.shape[0])
    out = np.zeros((h, rest.shape[1] + head.shape[1] - 2, 4), np.uint8)
    out[h - rest.shape[0]:, :rest.shape[1]] = rest
    hx = rest.shape[1] - 2
    m = head[..., 3] > 0
    sub = out[h - head.shape[0]:, hx:hx + head.shape[1]]
    sub[m] = head[m]
    return out


B_CHIN = 18                                           # B's hair top to the chin


def lying_b():
    """B fallen forward (lie()), her lance left planted where it stood, she on the ground behind it."""
    body = np.where((B_OP & ~B_LANCE)[..., None], B0, 0).astype(np.uint8)
    flat = lie(body, B_CHIN)
    dst = blank()
    put(dst, B0, B_LANCE, BX0, BY0)
    lx = BX0 + np.nonzero(B_LANCE.any(0))[0].min()
    put(dst, flat, flat[..., 3] > 0, lx - flat.shape[1] + 6, GY - flat.shape[0])
    return dst


def b_shut(a):
    """Her eyes shut: the eye's white and iris squares (B rows 9-13, columns 13-19) take the skin's dark shade."""
    return a


# ------------------------------------------------------------------------------------------------- actions
IDLE_MS = 150
BREATH = [0, 1, 1, 2, 2, 1, 1, 0]


def frames():
    out = {}
    out["idle"] = [(to_ppu(mounted(sink=b)), IDLE_MS) for b in BREATH]
    out["run"] = [(run_frame(i), RUN_MS) for i in range(8)]
    # the thrust (the kit's blow on tick 14 = 233 ms: frame 3, 160-260 ms). 2026-10-19 audit: the 5-frame thrust moved
    # 17 % of her squares a frame against the pack's 40 % - drawn further back, lunging further with the forehand
    # stepping in, 6 frames
    step = {"fn": (2, 0), "ff": (2, 0), "hn": (-1, 0), "hf": (-1, 0)}
    out["attack"] = [(to_ppu(mounted(dx=-3, ext=-5, sink=1)), 90), (to_ppu(mounted(dx=-1, ext=-1)), 70),
                     (to_ppu(mounted(dx=4, ext=12, sink=1, lg=step)), 100), (to_ppu(mounted(dx=3, ext=9, lg=step)), 80),
                     (to_ppu(mounted(dx=1, ext=3)), 67), (to_ppu(mounted()), 60)]
    # Shattering Strike (q_at 24 ticks = 400 ms: frame 4)
    fore_up = {"fn": (3, 4), "ff": (3, 4)}
    out["skill"] = [(to_ppu(mounted(dx=-3, sink=2, ext=-3)), 120),
                    (to_ppu(mounted(dx=-1, lift=2, lg=fore_up)), 120),
                    (to_ppu(mounted(dx=4, sink=1, ext=8, lg={"fn": (4, 0), "ff": (4, 0), "hn": (-2, 0), "hf": (-2, 0)})), 120),
                    (to_ppu(mounted(dx=5, sink=1, ext=14, lg={"fn": (4, 0), "ff": (4, 0), "hn": (-2, 0), "hf": (-2, 0)})), 100),
                    (to_ppu(mounted(dx=2, ext=4)), 40)]
    # Crash Down: the horse bursts into its armour, she (on foot, in it) rises and comes down
    burst = {"tail": (-22, -16), "rear": (-14, -26), "front": (0, -32), "head": (16, -22),
             "hn": (-20, -22), "hf": (-8, -30), "fn": (10, -28), "ff": (22, -20)}
    far = {k: (int(v[0] * 1.8), int(v[1] * 1.9)) for k, v in burst.items()}
    out["skill2"] = [(to_ppu(mounted(sink=3)), 100),
                     (to_ppu(mounted(lift=6, lg={k: (0, 3) for k in LEGS})), 100),
                     (dismounted(to_ppu(pieces(burst)), lift=12), 110),
                     (dismounted(to_ppu(pieces(far)), lift=16), 110),
                     (dismounted(lift=6), 100),
                     (dismounted(sink=2, nf=(-1, 0), ff=(1, 0)), 113)]
    # Mount Up: the pieces come back round her, the horse forms and charges (the kit's 20-tick strip)
    back = {k: (int(v[0] * 1.2), int(v[1] * 0.8)) for k, v in burst.items()}
    out["skill2_up"] = [(dismounted(sink=2), 70),
                        (dismounted(to_ppu(pieces(back)), lift=6), 80),
                        (to_ppu(mounted(dx=3, lift=3, ext=4, lg={"fn": (3, 2), "ff": (3, 2)})), 90),
                        (to_ppu(mounted(dx=5, ext=10, lg={"fn": (4, 0), "ff": (4, 0), "hn": (-2, 0), "hf": (-2, 0)})), 93)]
    # Magnet Storm (the kit's first yank on the animation's first tick): the stamp, the horse rearing, the second stamp
    # with the lance out, held, back. 2026-10-19 audit: the 5 frames were nearly one pose (16 % a frame)
    # rearing: the body up over the standing hind legs (a negative sink), the forelegs lifted
    rear = {"fn": (3, 5), "ff": (3, 5), "hn": (-1, 0), "hf": (-1, 0)}
    out["ult"] = [(to_ppu(mounted(dx=1, sink=3, ext=4)), 80), (to_ppu(mounted(dx=-2, sink=-2, ext=-3, lg=rear)), 90),
                  (to_ppu(mounted(dx=-1, sink=-2, ext=-4, lg={"fn": (4, 7), "ff": (4, 7), "hn": (-1, 0), "hf": (-1, 0)})), 70),
                  (to_ppu(mounted(dx=2, sink=3, ext=7)), 90), (to_ppu(mounted(dx=1, sink=2, ext=5)), 90),
                  (to_ppu(mounted(sink=1, ext=1)), 80)]
    out["hit"] = [(shift(to_ppu(mounted()), -3, 0), 90), (shift(to_ppu(mounted()), -1, 0), 120)]
    # death: the horse kneels, falls apart, she lies among the pieces
    loose = {"tail": (-4, 4), "rear": (-3, 6), "front": (0, 7), "head": (4, 6), "hn": (-3, 0), "hf": (-1, 0),
             "fn": (2, 0), "ff": (4, 0)}
    down = {"tail": on_ground("tail", -10), "rear": on_ground("rear", -4), "front": on_ground("front", 2),
            "head": on_ground("head", 8), "hn": on_ground("hn", -8), "hf": on_ground("hf", -2),
            "fn": on_ground("fn", 6), "ff": on_ground("ff", 12)}
    lying = pieces(down, rider=(-44, 0, 1), lance=(6, (NG - 1) - (AY0 + 36), 0))
    # 8 frames (2026-10-19 audit, the pack's deaths have 8): the armour first coming loose, the pieces falling 3 rows
    # above the ground, a 1-row bounce
    half = {k: (v[0] // 2, v[1] // 2) for k, v in loose.items()}
    flat = to_ppu(lying)
    out["dead"] = [(shift(to_ppu(mounted()), -3, 0), 120), (to_ppu(mounted(dx=-2, sink=5)), 120),
                   (to_ppu(pieces(half, rider=(-4, 4, 0), lance=(2, 6, 0))), 90),
                   (to_ppu(pieces(loose, rider=(-8, 8, 0), lance=(4, 12, 0))), 140),
                   (shift(flat, 0, -3), 80), (flat, 160), (shift(flat, 0, -1), 70), (flat.copy(), 400)]
    # on foot (the add-on's body while she is dismounted): the same beats as League's biped clips
    out["f_idle"] = [(dismounted(sink=b), IDLE_MS) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    out["f_run"] = [(walk_frame(i), WALK_MS) for i in range(8)]
    out["f_attack"] = [(dismounted(dx=-1, sink=1), 100), (dismounted(dx=1), 100), (dismounted(dx=3, ff=(1, 0)), 110),
                       (dismounted(dx=2, ff=(1, 0)), 90), (dismounted(), 67)]
    out["f_skill"] = [(dismounted(dx=-2, sink=1, nf=(-1, 0)), 120), (dismounted(dx=0, lift=1), 120),
                      (dismounted(dx=4, sink=1, ff=(2, 0)), 120), (dismounted(dx=5, sink=1, ff=(2, 0)), 100),
                      (dismounted(dx=1), 40)]
    out["f_hit"] = [(dismounted(dx=-3), 90), (dismounted(dx=-1), 120)]
    # Magnet Storm on foot (League's Biped_Spell4_Cast; the add-on plays f_ult while she is dismounted - the mounted
    # ult brought the horse back for half a second): the stamp, a hop, the second stamp, held, back
    # (2026-10-19, after League's Biped_Spell4_Cast: the lance raised over her head on the hop - turned a quarter about
    # her grip - and driven down on the second stamp)
    out["f_ult"] = [(dismounted(dx=1, sink=2, nf=(-1, 0), ff=(1, 0)), 80), (dismounted(dx=-1, lift=3, lance_up=True), 90),
                    (dismounted(dx=-1, lift=4, nf=(-1, 1), ff=(-1, 1), lance_up=True), 70),
                    (dismounted(dx=2, sink=3, nf=(-1, 0), ff=(2, 0)), 90), (dismounted(dx=1, sink=2, ff=(1, 0)), 90),
                    (dismounted(sink=1), 80)]
    # she sinks to her knees in the armour (its skirt to the ground) and slumps forward over her hips
    slump = dismounted(dx=-2, sink=13, nf=(-2, 0), ff=(1, 0), bow=(3, 3))
    # 8 frames (2026-10-19 audit): a step between the knees giving and the slump, the head dropping a little further
    out["f_dead"] = [(dismounted(dx=-2), 120), (dismounted(dx=-3, sink=4, nf=(-1, 0)), 120),
                     (dismounted(dx=-3, sink=9, nf=(-2, 0), ff=(1, 0), bow=(1, 1)), 120),
                     (dismounted(dx=-2, sink=11, nf=(-2, 0), ff=(1, 0), bow=(2, 2)), 100), (slump, 140),
                     (dismounted(dx=-2, sink=13, nf=(-2, 0), ff=(1, 0), bow=(4, 4)), 120), (slump.copy(), 200),
                     (slump.copy(), 400)]
    done = {t: [(tidy(a), ms) for a, ms in out[t]] for t in ORDER}
    for t in ("hit", "f_hit"):
        done[t][0] = (flash(done[t][0][0]), done[t][0][1])
    return done


# ------------------------------------------------------------------------------------------------- finishing
OUTLINE = tuple(int(v) for v in OUT_A)
HOLE_FILL = 6
SPECK = 4


def tidy(a):
    out = G.complete_outline(a, color=OUTLINE, feet=GY - 1)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > HOLE_FILL:
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
            if sz[k - 1] < SPECK:
                out[lbl == k] = 0
    return out


CORNER = (PX + 0.5, GY)


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


def down(can):
    """(the 1x frame centred on the pivot, the PPU frame round(PPU x its size) round the pivot). The pivot: the pivot
    column, FEET 1x rows above the ground line."""
    px, py = CORNER[0], CORNER[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh))[0]
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


# ------------------------------------------------------------------------------------------------- review
def review(acts, out_dir, z=6, zg=3):
    os.makedirs(out_dir, exist_ok=True)
    allc = np.concatenate([np.stack([f for f, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, GY + 3, xs.min() - 2, xs.max() + 3
    for tag, fr in acts.items():
        tiles = []
        for f, _ in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB"))
        sheet = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 6), (y1 - y0) * z), (60, 60, 60))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST), (i * ((x1 - x0) * z + 6), 0))
        sheet.save(os.path.join(out_dir, f"rell_{tag}.png"))
        small = [t.resize(((x1 - x0) * zg, (y1 - y0) * zg), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"rell_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


def check_idle():
    """The standing frame must be the user's pick (design_A.png) square for square."""
    f = to_ppu(mounted())
    ys, xs = np.nonzero(f[..., 3] > 0)
    got = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    want = load(os.path.join(SRC, "hd", "design_A.png"))
    same = got.shape == want.shape and np.array_equal(got, want)
    diff = None if got.shape != want.shape else int((np.any(got != want, -1)).sum())
    print("idle == design_A:", same, "shape", got.shape, want.shape, "squares differing", diff)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="every tag's frames at 6x and a 3x GIF here (nothing written to the repo)")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check_idle()
        return
    acts = frames()
    if a.review:
        review(acts, a.review)
        return
    sheet = {}
    os.makedirs(lp(ORIG), exist_ok=True)
    for tag, frs in acts.items():
        ones, hds = [], []
        for can, t in frs:
            one, hd = down(can)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(lp(os.path.join(ORIG, f"rell_{tag}.png")))
        with open(lp(os.path.join(ORIG, f"rell_{tag}.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
    w, h = G.write_sheet(lp(STEM), sheet)
    print(f"league/champions/league_rell#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


if __name__ == "__main__":
    main()
