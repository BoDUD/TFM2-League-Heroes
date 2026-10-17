#!/usr/bin/env python3
"""league_tahmkench's action frames posed from the approved design's own squares (no Codex strips: the user, 2026-10-16,
「codex额度不够了 你能画吗？用点工具和技术 然后弄到完美了喊我review」).

    python tools/art/rig_tahmkench.py --review DIR      # every tag at the design's density, 3x, + a GIF per tag
    python tools/art/rig_tahmkench.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet
    python tools/art/ppu_restyle.py --hero tahmkench && python tools/art/rig_tahmkench.py --pinholes &&
        python tools/art/ppu_hd.py --hero tahmkench

The design (assets/source/tahmkench/hd/A.png, 151 x 125 squares: hat top to soles, 2.98 squares a game pixel) is cut
into parts by fixed square ranges and posed only losslessly (memory no-deformation-lossless-poses): whole-part moves,
quarter turns, whole-column shifts (the tail), layering (the body over the feet). What is new is drawn from the
design's own colours:
  * the open mouth: everything above the mouth line (hat, eye, snout, the upper teeth, both whiskers) lifted `d` rows,
    the jaw (the lower teeth, the chin) kept; the gap inside the lips is the mouth's own magenta with a darker throat
    line, outside them (the cheek left of the mouth's corner, the snout's right end) the cut row repeated;
  * the tongue (attack, Q, death): a stroke along a polyline in the whiskers' pinks, lit on top, a dark outline.
Actions (League's clips, tools/lol/native_pose.py / assets/source/tahmkench/poses.json, for the beats):
  run 8     a waddle: the body bobs over the feet, the feet step half a cycle apart (lifted while swinging forward),
            the tail sways, the far arm swings (his two short legs stand 39 squares apart: they cannot cross)
  attack 5  the tongue slap: lean back with the mouth opening, the tongue curling up, the slap forward (frame 3)
  skill 5   Tongue Lash: crouch, rear back, lurch forward mouth wide, the tongue's root out (frame 4; the lash is an
            effect), recover
  skill2 4  Abyssal Dive under: squat, hop, head-first into the ground (a quarter turn cut at the ground), tail only
  w_land 4  up: mouth-first out of the ground (a quarter turn, mouth open), in the air, landing squat, stand
  ult 5     Devour: lean back opening, the mouth at its widest, the gulp (shut, sunk), full, stand
  dead 6    flinch, stagger, slump, sink, lie (sunk into the ground line, tongue out, eye shut), still
  idle      breathing (the body over the feet 0 / 1 row), hit: moved back with a white flash
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
if os.name == "nt" and not ROOT.startswith(chr(92) * 2):
    ROOT = chr(92) * 2 + "?" + chr(92) + os.path.abspath(ROOT)   # the repo sits deep under the MSIX profile: long paths
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
sys.path.insert(0, HERE)
import strips as G  # noqa: E402
import pixel_down as PD  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "tahmkench")
STEM = os.path.join(ROOT, "league", "champions", "league_tahmkench")
ORIG = os.path.join(ROOT, "assets", "source", "ppu", "orig")
PPU = 1.2                                   # the user's pick: 1.8 by the recommendation, then 「感觉太高清了 降低点像素」 -
                                            # shown 1.8 / 1.6 / 1.5 / 1.4 / 1.3 / 1.2 at one game size: 「塔姆用 PPU 1.5」,
                                            # then 「降到1.2吧」
DESIGN = np.asarray(Image.open(os.path.join(SRC, "hd", "A.png")).convert("RGBA")).copy()
DH, DW = DESIGN.shape[:2]                   # 125 x 151
GAME_ROWS = 42
NATIVE = DH / GAME_ROWS                     # design squares a game pixel
FEET_MID = 94                               # the design's column between the feet (the pack's standing point)

# ------------------------------------------------------------------------------------------------- colours
OUTLINE = (4, 2, 8)
MOUTH = (167, 37, 82)                       # the inside of the mouth
THROAT = (115, 15, 45)
LIP = (83, 11, 35)
PINK_L, PINK, PINK_D = (216, 148, 124), (212, 104, 101), (146, 81, 81)    # the whiskers' pinks (the tongue)
SALMON = {(216, 148, 124), (212, 104, 101)}
DARKS = {(4, 2, 8), (53, 5, 23), (83, 11, 35), (115, 15, 45)}
WHITE_FLASH = 0.45

# ------------------------------------------------------------------------------------------------- the canvas
CW, CH = 360, 240                           # native squares
OX, OY = 90, 100                            # where the design's (0, 0) goes when standing
GROUND = OY + DH                            # the first row under the soles
PIVOT = (OX + FEET_MID + 0.5, GROUND)
PAD = 30                                    # rows over the design for a lifted head


def col(a, r, c):
    return tuple(int(v) for v in a[r, c, :3])


def opaque(a):
    return a[..., 3] > 0


# ------------------------------------------------------------------------------------------------- parts (design rows)
def box(r0, r1, c0, c1):
    m = np.zeros((DH, DW), bool)
    m[r0:r1 + 1, c0:c1 + 1] = True
    return m & opaque(DESIGN)


FOOT_N = box(111, DH - 1, 55, 93)
FOOT_F = box(110, DH - 1, 96, 132)
HAT = box(0, 16, 70, 124)
FAR_ARM = box(62, 96, 134, DW - 1)
TAIL_END = 26                               # columns left of this sway as the tail


def whiskers():
    """Both whiskers: their salmon squares (pieces of 15 or more) and the dark squares touching them."""
    sal = np.array([[DESIGN[r, c, 3] > 0 and col(DESIGN, r, c) in SALMON for c in range(DW)] for r in range(DH)])
    lbl, n = ndimage.label(sal, structure=np.ones((3, 3)))
    keep = np.zeros_like(sal)
    for k in range(1, n + 1):
        if (lbl == k).sum() >= 15:
            keep |= lbl == k
    ring = ndimage.binary_dilation(keep, structure=np.ones((3, 3))) & ~keep
    dark = np.array([[DESIGN[r, c, 3] > 0 and col(DESIGN, r, c) in DARKS for c in range(DW)] for r in range(DH)])
    return keep | (ring & dark)


# the near whisker's root, pale where it leaves the gold ring (not salmon yet): its squares by row, with the ring
NEAR_ROOT = {38: (101, 104), 39: (101, 105), 40: (100, 106), 41: (100, 106), 42: (99, 106), 43: (99, 106),
             44: (99, 105), 45: (99, 104), 46: (99, 104), 47: (99, 104), 48: (99, 104)}
GOLD_RING = (33, 39, 103, 109)


def near_root():
    m = np.zeros((DH, DW), bool)
    for r, (c0, c1) in NEAR_ROOT.items():
        m[r, c0:c1 + 1] = True
    r0, r1, c0, c1 = GOLD_RING
    m[r0:r1 + 1, c0:c1 + 1] = True
    return m & opaque(DESIGN) & ~np.array([[col(DESIGN, r, c) == MOUTH for c in range(DW)] for r in range(DH)])


WHISKERS = whiskers() | near_root()


def mouth_cut():
    """{column: the first row that stays with the jaw}: in the mouth the first magenta square (the upper teeth hang
    above it), left of it the lip's slope from the corner (row 33, column 80), the cheek and the snout's end cut on
    one row each."""
    cut = {}
    for x in range(96, 128):
        rs = [r for r in range(37, 50) if DESIGN[r, x, 3] and col(DESIGN, r, x) == MOUTH]
        if rs:
            cut[x] = rs[0]
    have = sorted(cut)
    for x in range(96, 128):
        if x not in cut:
            lo = max([v for v in have if v < x], default=have[0])
            hi = min([v for v in have if v > x], default=have[-1])
            cut[x] = int(round((cut[lo] + cut[hi]) / 2))
    for x in range(63, 80):
        cut[x] = 33
    for x in range(80, 96):
        cut[x] = int(round(33 + (cut[96] - 33) * (x - 80) / 16))
    for x in range(128, DW):
        cut[x] = 41
    return cut


CUT = mouth_cut()
MOUTH_COLS = range(80, 128)


def padded(a=None):
    a = DESIGN if a is None else a
    out = np.zeros((DH + PAD, DW, 4), np.uint8)
    out[PAD:] = a
    return out


def open_mouth(d):
    """The design (padded PAD rows on top) with the upper head lifted d rows."""
    a = padded()
    if d == 0:
        return a
    wh = np.zeros(a.shape[:2], bool)
    wh[PAD:] = WHISKERS
    up = np.zeros(a.shape[:2], bool)
    for x, c in CUT.items():
        up[:PAD + c, x] = opaque(a)[:PAD + c, x]
    up &= ~wh
    out = a.copy()
    out[wh] = 0
    ys, xs = np.nonzero(up)
    out[ys, xs] = 0
    out[ys - d, xs] = a[ys, xs]
    for x, c in CUT.items():
        for y in range(PAD + c - d, PAD + c):
            if x in MOUTH_COLS:
                # the gap: magenta, the throat one row darker along the jaw, the lips' corners dark
                edge = x in (MOUTH_COLS.start, MOUTH_COLS.stop - 1)
                out[y, x] = (*(LIP if edge else THROAT if y == PAD + c - 1 else MOUTH), 255)
            else:
                src_y = PAD + c - 1
                xx = x
                while xx > 0 and wh[src_y, xx]:          # the face square left of a whisker
                    xx -= 1
                if a[src_y, x, 3] and a[src_y, xx, 3]:
                    out[y, x] = a[src_y, xx]
    # under the whiskers' old place: the square to the left that is not whisker (chin, cheek), else clear
    for y, x in zip(*np.nonzero(wh)):
        if out[y, x, 3]:
            continue
        for dx in range(1, 8):
            if x - dx >= 0 and a[y, x - dx, 3] and not wh[y, x - dx]:
                out[y, x] = out[y, x - dx] if out[y, x - dx, 3] else a[y, x - dx]
                break
    ys, xs = np.nonzero(wh)
    out[ys - d, xs] = a[ys, xs]
    return out


# ------------------------------------------------------------------------------------------------- composing
def put(dst, src, mask, dx, dy, under=False):
    ys, xs = np.nonzero(mask)
    ty, tx = ys + dy, xs + dx
    ok = (ty >= 0) & (ty < dst.shape[0]) & (tx >= 0) & (tx < dst.shape[1])
    ys, xs, ty, tx = ys[ok], xs[ok], ty[ok], tx[ok]
    if under:
        free = dst[ty, tx, 3] == 0
        ys, xs, ty, tx = ys[free], xs[free], ty[free], tx[free]
    dst[ty, tx] = src[ys, xs]


def pose(d=0, bob=0, lean=0, nf=(0, 0), ff=(0, 0), tail=0, arm=(0, 0), hat=None, lift=0):
    """One frame on the canvas: the mouth open d rows, the body (all but the feet) bob rows down and lean columns
    forward over the feet, the near / far foot moved (dx, dy), the tail's tip `tail` rows (column shift to its tip),
    the far arm moved, the hat moved by (dx, dy) or None (on the head), the whole figure `lift` rows up."""
    src = open_mouth(d)
    H = src.shape[0]
    feet_n = np.zeros(src.shape[:2], bool)
    feet_f = np.zeros(src.shape[:2], bool)
    feet_n[PAD:] = FOOT_N
    feet_f[PAD:] = FOOT_F
    arm_m = np.zeros(src.shape[:2], bool)
    arm_m[PAD:] = FAR_ARM
    hat_m = np.zeros(src.shape[:2], bool)
    if hat is not None:      # the hat as it sits after the mouth's lift (it rides on the upper head)
        hm = np.zeros(src.shape[:2], bool)
        hm[PAD:PAD + 17] = True
        hm[:PAD] = True
        hat_m = hm & opaque(src) & (np.arange(DW)[None, :] >= 70) & (np.arange(DW)[None, :] <= 124)
        hat_m &= np.arange(H)[:, None] < PAD + 17 - d
    body = opaque(src) & ~feet_n & ~feet_f & ~arm_m & ~hat_m
    # the tail: columns left of TAIL_END shifted toward the tip
    if tail:
        t = src.copy()
        for x in range(TAIL_END):
            k = int(round(tail * (TAIL_END - x) / TAIL_END))
            if k:
                colm = src[:, x].copy()
                t[:, x] = 0
                lo, hi = max(0, k), min(H, H + k)
                t[lo:hi, x] = colm[lo - k:hi - k]
        src = t
        body = opaque(src) & ~feet_n & ~feet_f & ~arm_m & ~hat_m
    can = np.zeros((CH, CW, 4), np.uint8)
    oy = OY - PAD - lift
    put(can, src, feet_n, OX + nf[0], oy + nf[1])
    put(can, src, feet_f, OX + ff[0], oy + ff[1])
    put(can, src, arm_m & ~opaque(np.zeros_like(src)), OX + lean + arm[0], oy + bob + arm[1])
    put(can, src, body, OX + lean, oy + bob)
    put(can, src, arm_m, OX + lean + arm[0], oy + bob + arm[1], under=True)
    if hat is not None:
        put(can, src, hat_m, OX + lean + hat[0], oy + bob + hat[1])
    return can


def tongue(can, pts, width=5.0):
    """The tongue along pts (canvas squares, from inside the mouth outward): pink, lit on its upper side, a darker
    underside and a dark outline; the tip rounded."""
    pts = np.asarray(pts, float)
    seg = np.diff(pts, axis=0)
    lens = np.hypot(seg[:, 0], seg[:, 1])
    total = lens.sum()
    m = np.zeros(can.shape[:2], np.int8)          # 0 none, 1 dark, 2 mid, 3 lit
    ys, xs = np.mgrid[0:can.shape[0], 0:can.shape[1]]
    best = np.full(can.shape[:2], 1e9)
    side = np.zeros(can.shape[:2])
    along = np.zeros(can.shape[:2])
    acc = 0.0
    for (x0, y0), (dx, dy), L in zip(pts[:-1], seg, lens):
        t = np.clip(((xs + 0.5 - x0) * dx + (ys + 0.5 - y0) * dy) / (L * L), 0, 1)
        px, py = x0 + t * dx, y0 + t * dy
        dist = np.hypot(xs + 0.5 - px, ys + 0.5 - py)
        sgn = np.sign((xs + 0.5 - x0) * dy - (ys + 0.5 - y0) * dx)       # which side of the bone
        upd = dist < best
        best[upd] = dist[upd]
        side[upd] = sgn[upd]
        along[upd] = (acc + t * L)[upd]
        acc += L
    w = width / 2 * (1 - 0.35 * along / max(total, 1))                    # thinner to the tip
    inside = best <= w
    lit = inside & (side < 0) & (best > w * 0.25)
    dark = inside & (side > 0) & (best > w * 0.45)
    m[inside] = 2
    m[lit] = 3
    m[dark] = 1
    ring = ndimage.binary_dilation(inside, structure=np.ones((3, 3))) & ~inside
    for v, c in ((1, PINK_D), (2, PINK), (3, PINK_L)):
        can[m == v] = (*c, 255)
    can[ring & (can[..., 3] == 0)] = (*LIP, 255)
    can[ring & (can[..., 3] > 0) & ~inside] = can[ring & (can[..., 3] > 0) & ~inside]
    edge = ring & ~(m > 0)
    can[edge] = (*LIP, 255)
    return can


def mouth_spot(d, lean=0, bob=0, lift=0):
    """Canvas point inside the opened mouth, near its lower middle (where a tongue starts)."""
    x = 112
    y = CUT[x] - 2
    return OX + lean + x, OY + y + bob - lift


def turned(k, dx, dy, d=0):
    """The design (mouth open d) turned k quarter turns counter-clockwise, its bottom dy rows over the ground, its
    middle dx columns right of the standing point, cut under the ground."""
    src = open_mouth(d)
    ys, xs = np.nonzero(opaque(src))
    src = src[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    t = np.rot90(src, k).copy()
    h, w = t.shape[:2]
    can = np.zeros((CH, CW, 4), np.uint8)
    top = GROUND - h - dy
    left = int(round(PIVOT[0] - w / 2)) + dx
    sub = can[max(0, top):top + h, max(0, left):left + w]
    sub[...] = t[max(0, -top):max(0, -top) + sub.shape[0], max(0, -left):max(0, -left) + sub.shape[1]]
    can[GROUND:] = 0
    return can


def flash(can):
    out = can.copy()
    m = opaque(out)
    out[m, :3] = (out[m, :3].astype(float) * (1 - WHITE_FLASH) + 255 * WHITE_FLASH).astype(np.uint8)
    return out


def shut_eye(can, lean=0, bob=0):
    """The eye (design rows 27-30, columns 93-101) painted shut: a dark line on the lid colour."""
    out = can.copy()
    for r in range(26, 31):
        for c in range(92, 103):
            y, x = OY + r + bob, OX + c + lean
            v = col(DESIGN, r, c)
            if sum(v) > 400 and v[1] > 200 and v[2] < 140:          # the yellow-green eye
                out[y, x] = (*((194, 191, 142) if r < 29 else LIP), 255)
    return out


def cut_ground(can):
    out = can.copy()
    out[GROUND:] = 0
    return out


# ------------------------------------------------------------------------------------------------- the actions
RUN_N = [(7, 0), (4, 0), (0, 0), (-4, 0), (-7, 0), (-4, -4), (0, -6), (4, -4)]   # near foot (dx, dy) by frame


def frames():
    out = {}
    out["idle"] = [(pose(bob=b, tail=t), 125) for b, t in zip([0, 1, 2, 3, 3, 2, 1, 0], [0, 1, 1, 2, 2, 1, 1, 0])]
    run = []
    for i in range(8):
        nf = RUN_N[i]
        ff = RUN_N[(i + 4) % 8]
        bob = [0, 3, 5, 3, 0, 3, 5, 3][i]
        run.append((pose(bob=bob, lean=2, nf=nf, ff=(ff[0], ff[1]), tail=[2, 4, 2, 0, -2, -4, -2, 0][i],
                         arm=([2, 2, 0, -2, -2, -2, 0, 2][i], [0, -1, -2, -1, 0, -1, -2, -1][i])), 100))
    out["run"] = run
    # attack: the tongue slap (release on frame 3)
    a1 = pose(d=4, lean=-2)
    a2 = pose(d=9, lean=-3)
    x, y = mouth_spot(9, lean=-3)
    a2 = tongue(a2, [(x - 4, y), (x + 14, y - 2), (x + 30, y - 10), (x + 36, y - 24), (x + 30, y - 32)], 6)
    a3 = pose(d=6, lean=3, bob=1)
    x, y = mouth_spot(6, lean=3, bob=1)
    a3 = tongue(a3, [(x - 6, y), (x + 14, y - 2), (x + 34, y + 6), (x + 46, y + 22)], 6)
    a4 = pose(d=4, lean=1)
    x, y = mouth_spot(4, lean=1)
    a4 = tongue(a4, [(x - 6, y), (x + 8, y), (x + 16, y + 4)], 5)
    out["attack"] = [(a1, 80), (a2, 80), (a3, 90), (a4, 90), (pose(), 100)]
    # Q: Tongue Lash (release on frame 4: the lash itself is an effect)
    q4 = pose(d=12, lean=4)
    x, y = mouth_spot(12, lean=4)
    q4 = tongue(q4, [(x - 6, y), (x + 14, y - 1), (x + 30, y + 1), (x + 40, y + 4)], 6)
    out["skill"] = [(pose(bob=2), 80), (pose(d=4, lean=-2), 80), (pose(d=9, lean=2), 80), (q4, 100),
                    (pose(d=2), 110)]
    # W: under and up
    out["skill2"] = [(pose(bob=5), 100), (pose(lift=12), 100), (cut_ground(pose(lift=-55)), 100),
                     (cut_ground(pose(lift=-105)), 100)]
    out["w_land"] = [(cut_ground(pose(d=14, lift=-45)), 80), (pose(d=10, lift=18), 80), (pose(bob=6), 90),
                     (pose(), 90)]
    # R: Devour
    out["ult"] = [(pose(d=6, lean=-2), 100), (pose(d=16, lean=-3), 100), (pose(bob=2, lean=1), 100),
                  (pose(bob=1, arm=(-4, 0)), 100), (pose(), 100)]
    # death
    # lying: sunk to the ground line, the hat slid down over the shut eye, the tongue lolling to the ground
    d5 = pose(d=4, bob=22, hat=(3, 8))
    x, y = mouth_spot(4, bob=22)
    d5 = shut_eye(tongue(d5, [(x - 4, y), (x + 8, y + 3), (x + 14, y + 10), (x + 16, y + 18)], 5), bob=22)
    d5 = cut_ground(d5)
    out["dead"] = [(pose(d=4, lean=-2), 120), (pose(d=2, lean=-3, hat=(0, -5)), 120),
                   (pose(bob=6, lean=1, hat=(1, -2)), 140), (cut_ground(pose(bob=14, hat=(2, 4))), 160),
                   (d5, 200), (d5.copy(), 400)]
    out["hit"] = [(flash(pose(lean=-4)), 90), (pose(lean=-2), 120)]
    return out


# ------------------------------------------------------------------------------------------------- the game's frames
ORDER = ["idle", "run", "attack", "skill", "skill2", "w_land", "ult", "hit", "dead"]
FEET = 11                                   # 1x rows from the pivot down to the ground row
PAL = np.unique(DESIGN[DESIGN[..., 3] > 0][:, :3], axis=0)
PALF = PAL.astype(float)
K = PPU / NATIVE


EYE = {(177, 230, 47), (223, 246, 77), (236, 249, 134), (89, 220, 67), (102, 132, 32)}
GOLD = {(221, 161, 40), (246, 203, 68), (177, 124, 30)}
KEEP = [(EYE, 0.2), (GOLD, 0.34)]          # small features kept through the coarse grid (league_elise's eye-keeping face):
                                           # a square this much of these colours takes their commonest one


def down2(a):
    """The native frame brought to PPU squares a game pixel on a grid through the pivot (pixel_down.pixelate), then
    the eye and the gold rings kept (KEEP)."""
    out, (nx0, ny0) = PD.pixelate(a, K, PIVOT, OUTLINE, PALF)
    H, W = a.shape[:2]
    c = 1.0 / K
    px, py = PIVOT
    Hn, Wn = out.shape[:2]
    cx = np.floor((np.arange(W) + 0.5 - px) / c).astype(int) + nx0
    cy = np.floor((np.arange(H) + 0.5 - py) / c).astype(int) + ny0
    ok = ((cy >= 0) & (cy < Hn))[:, None] & ((cx >= 0) & (cx < Wn))[None, :]
    cell = cy[:, None] * Wn + cx[None, :]
    tot = np.bincount(cell[ok], minlength=Hn * Wn)
    rgb = a[..., :3]
    for cols, share in KEEP:
        m = np.zeros((H, W), bool)
        for col_ in cols:
            m |= np.all(rgb == np.array(col_, np.uint8), axis=-1)
        m &= a[..., 3] > 0
        if not m.any():
            continue
        n = np.bincount(cell[ok & m], minlength=Hn * Wn)
        hit = np.nonzero((n >= share * np.maximum(tot, 1)) & (n > 0))[0]
        ys, xs = np.nonzero(ok & m)
        keys = cell[ys, xs]
        for k in hit:
            r, q = divmod(int(k), Wn)
            vals, cnt = np.unique(rgb[ys[keys == k], xs[keys == k]], axis=0, return_counts=True)
            out[r, q, :3] = vals[cnt.argmax()]
            out[r, q, 3] = 255
    return out, (nx0, ny0)


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


def down(can, corner):
    """(the 1x frame round the pivot, the PPU frame PPU x its size about the same centre)."""
    px, py = float(corner[0]), corner[1] - FEET * PPU
    ys, xs = np.nonzero(can[..., 3] > 0)
    hw = int(np.ceil(max(px - xs.min(), xs.max() + 1 - px) / PPU - 0.5))
    hh = int(np.ceil(max(py - ys.min(), ys.max() + 1 - py) / PPU - 0.5))
    one = G.complete_outline(one_of(can, px, py, hw, hh), color=OUTLINE)[0]
    W, H = round((2 * hw + 1) * PPU), round((2 * hh + 1) * PPU)
    return one, crop_hd(can, px, py, W, H)


def tidy(a):
    """The outline closed round moved edges, enclosed pinholes (up to 6 squares) filled with their commonest
    neighbour, specks of 1-2 squares off."""
    out = G.complete_outline(a, color=OUTLINE)[0]
    op = out[..., 3] > 0
    holes = ndimage.binary_fill_holes(op) & ~op
    lbl, n = ndimage.label(holes)
    for k in range(1, n + 1):
        m = lbl == k
        if m.sum() > 6:
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
            if sz[k - 1] < 3:
                out[lbl == k] = 0
    return out


def strip_of(frames):
    H = max(h.shape[0] for h in frames)
    strip = np.zeros((H, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        strip[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return strip


def export(acts, review_dir=None):
    sheet = {}
    os.makedirs(ORIG, exist_ok=True)
    for tag in ORDER:
        ones, hds = [], []
        for can, t in acts[tag]:
            small, corner = down2(can)
            one, hd = down(tidy(small), corner)
            ones.append((one, float(t)))
            hds.append(hd)
        sheet[tag] = ones
        Image.fromarray(strip_of(hds)).save(os.path.join(ORIG, f"tahmkench_{tag}.png"))
        with open(os.path.join(ORIG, f"tahmkench_{tag}.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in hds], "ppu": PPU}, f)
        if review_dir:
            os.makedirs(review_dir, exist_ok=True)
            Z = 4
            w = max(h.shape[1] for h in hds)
            hgt = max(h.shape[0] for h in hds)
            big = Image.new("RGBA", (len(hds) * (w + 4) * Z, hgt * Z), (96, 112, 96, 255))
            for j, h in enumerate(hds):
                big.alpha_composite(Image.fromarray(h).resize((h.shape[1] * Z, h.shape[0] * Z), Image.NEAREST),
                                    (j * (w + 4) * Z, (hgt - h.shape[0]) * Z))
            big.convert("RGB").save(os.path.join(review_dir, f"ppu_{tag}.png"))
    w, h = G.write_sheet(STEM, sheet)
    print(f"league/champions/league_tahmkench#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(f)}" for t, f in sheet.items()))


def pinholes(most=4):
    """After tools/art/ppu_restyle.py: enclosed gaps of up to `most` squares in the restyled strips
    (assets/source/ppu/tahmkench_<tag>.png) take the commonest colour round them. Then ppu_hd.py again."""
    src = os.path.join(ROOT, "assets", "source", "ppu")
    total = 0
    for tag in ORDER:
        meta = json.load(open(os.path.join(src, f"tahmkench_{tag}.json"), encoding="utf-8"))
        strip = np.asarray(Image.open(os.path.join(src, f"tahmkench_{tag}.png")).convert("RGBA")).copy()
        x = 0
        for W, H in meta["sizes"]:
            f = strip[:H, x:x + W]
            op = f[..., 3] > 0
            holes = ndimage.binary_fill_holes(op) & ~op
            lbl, n = ndimage.label(holes)
            for k in range(1, n + 1):
                m = lbl == k
                if m.sum() > most:
                    continue
                ring = ndimage.binary_dilation(m, structure=np.ones((3, 3))) & op
                cols, cnt = np.unique(f[ring][:, :3], axis=0, return_counts=True)
                f[m, :3] = cols[cnt.argmax()]
                f[m, 3] = 255
                total += int(m.sum())
            x += W + 1
        Image.fromarray(strip).save(os.path.join(src, f"tahmkench_{tag}.png"))
    print(f"tahmkench: {total} pinhole squares filled")


# ------------------------------------------------------------------------------------------------- review
def review(acts, out_dir, z=3):
    os.makedirs(out_dir, exist_ok=True)
    allc = np.concatenate([np.stack([f for f, _ in fr]) for fr in acts.values()])
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 2, GROUND + 2, xs.min() - 2, xs.max() + 3
    for tag, fr in acts.items():
        tiles = []
        for f, _ in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            tiles.append(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
        sheet = Image.new("RGB", (len(tiles) * (tiles[0].width + 6), tiles[0].height), (60, 60, 60))
        for i, t in enumerate(tiles):
            sheet.paste(t, (i * (t.width + 6), 0))
        sheet.save(os.path.join(out_dir, f"tahmkench_{tag}.png"))
        small = [t.resize((t.width * 2 // z, t.height * 2 // z), Image.NEAREST) for t in tiles]
        pal_src = Image.new("RGB", (small[0].width, small[0].height * len(small)))
        for i, t in enumerate(small):
            pal_src.paste(t, (0, i * t.height))
        pal = pal_src.quantize(255, dither=Image.Dither.NONE)
        q = [t.quantize(palette=pal, dither=Image.Dither.NONE) for t in small]
        q[0].save(os.path.join(out_dir, f"tahmkench_{tag}.gif"), save_all=True, append_images=q[1:],
                  duration=[ms for _, ms in fr], loop=0, optimize=False)
    print("review ->", out_dir)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", help="the native frames at 3x and a GIF per tag here (nothing written to the repo)")
    ap.add_argument("--ppu-review", help="also the PPU frames at 4x here")
    ap.add_argument("--pinholes", action="store_true", help="after ppu_restyle.py: fill the restyled strips' pinholes")
    a = ap.parse_args()
    if a.pinholes:
        pinholes()
        return
    acts = frames()
    if a.review:
        review(acts, a.review)
        return
    export(acts, a.ppu_review)


if __name__ == "__main__":
    main()
