#!/usr/bin/env python3
"""league_gangplank's action frames posed from the approved design's own squares (the user, 2026-10-18: 「动作帧参考塔姆
那种做法 不用依赖codex 然后做完了你自己review 完美了再喊我review」).

    python tools/art/rig_gangplank.py --parts DIR       # the design with its parts tinted + pose tries (12x)
    python tools/art/rig_gangplank.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_gangplank.py --audit DIR       # per-frame checks + every tag at 6x
    python tools/art/rig_gangplank.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The design: Codex's step-1 redo take A-2 (the slimmer belly, 「普朗克不是大肚子」) read back on its own 21 px grid,
UNCUT - 57 x 62 squares, PPU 1.5 (41 game rows). The 50-row cut for PPU 1.2 (hd/design_cut50.png, design_gangplank_cut.py)
broke the gun hand into specks in every frame (the user: 「拿枪的那个手啊」). Its boots made boots again by
tools/art/fix_gangplank_feet.py (「脚这里变形」). The hat's top row 0, the soles row 61. Every pose is
lossless (memory no-deformation-lossless-poses): parts cut square by square from the design and only moved by whole
squares or mirrored (league_jarvaniv / league_ziggs); nothing is drawn again.
Parts: the hand cannon (gold; its bell points BACK over the shoulder, so a shot mirrors it to point forward), the near
arm (the glove on the cannon, the red wrap and the gold bracer, from the near shoulder), the far hand (the red wrap, the
fist and the hilt), the cutlass (mirrored top to bottom it points up: the raised blade), the body (head, torso, sash,
coat tails) and the two legs (row LEG_TOP down, split between the boots; the coat's purple and its gold trim stay with
the body). Hands and props move whole (league_ziggs: a hand turned about its shoulder lands behind the head or across
the face; a hand moved against the body stretches the sleeve), the legs move whole.
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
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rigkit as K  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "gangplank"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "gangplank", "hd")
P = 60                                          # padding round a design-sized layer


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign:
    """What ppu_rig.Rig needs of a design: the squares, the standing point, the outline colour."""
    TURN_PAD = P

    def __init__(self, d, px):
        self.hero, self.ppu = HERO, PPU
        self.d = d
        self.d0 = d.copy()
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = px
        self.outline = PD.edge_colour(d)
        self.parts, self.order, self.props = {}, [], set()

    def box(self, y0, y1, x0, x1):
        m = np.zeros((self.H, self.W), bool)
        m[max(0, y0):y1 + 1, max(0, x0):min(self.W, x1 + 1)] = True
        return m & (self.d[..., 3] > 0)

    def part(self, name, m):
        for k in self.parts:
            self.parts[k] &= ~m
        self.parts[name] = m.copy()
        if name not in self.order:
            self.order.append(name)

    def rest(self):
        m = self.d[..., 3] > 0
        for v in self.parts.values():
            m &= ~v
        return m

    def layer(self, name, m=None):
        m = self.parts[name] if m is None else m
        out = np.zeros_like(self.d)
        out[m] = self.d[m]
        return out


def pad(a):
    out = np.zeros((a.shape[0] + 2 * P, a.shape[1] + 2 * P, 4), np.uint8)
    out[P:P + a.shape[0], P:P + a.shape[1]] = a
    return out




# ------------------------------------------------------------------------------------------------- the design's parts
LEG_TOP = 52                                    # the lower legs from here down: the cuffs' top outline and the boots
                                                # (the thighs stay on the body: moved, they slid under the sash -
                                                # 「移动时腿部还是有点变形」)
STAND = 24                                      # the column between the boots: the standing point
GUN_PIVOT = (11.5, 13.5)                        # the cannon's middle (its quarter turns)
GUN_MIRROR = 12                                 # the column the cannon is mirrored about to point forward
ELBOW = (12.5, 29.5)                            # the near forearm's lower end: it turns about it
SHOULDER = (35.5, 22.5)                         # the far shoulder: the sword arm turns about it
PT, PL = 12, 8                                  # the pose stamps' rows above and columns left of the design


def cls_purple(d):
    r, g, b = (d[..., i].astype(int) for i in range(3))
    return (d[..., 3] > 0) & (b > g + 15) & (r > g) & (r + g + b > 90)


def design():
    d = load("design.png")
    D = CutDesign(d, px=STAND)
    coat = cls_purple(d)
    # the hand cannon with the glove and the fingers on it (the hat's brim from column 15 on rows 7-11 and the hair from
    # column 21 stay with the head)
    D.part("gun", D.box(8, 18, 3, 16) | D.box(12, 18, 17, 20))
    # the near forearm: the red wrap and the gold bracer under the cannon, down to the elbow
    D.part("near_arm", D.box(19, 30, 7, 18))
    # the far arm: the upper arm down the torso's side and the red-wrapped forearm (turned about the far shoulder with
    # the fist and the cutlass for a swing); the fist and the hilt; the cutlass on its own
    D.part("far_upper", D.box(21, 37, 34, 41))
    D.part("far_hand", D.box(37, 44, 37, 44))
    D.part("blade", D.box(44, 56, 42, 56) | D.box(45, 47, 41, 41))
    # the lower legs: the gold cuff and the boot of each, the coat's purple left with the body
    D.part("near_leg", D.box(LEG_TOP, D.H - 1, 12, 25) & ~coat)
    D.part("far_leg", D.box(LEG_TOP, D.H - 1, 26, 38) & ~coat)
    D.part("body", D.rest())
    return D


def vflip(layer, row):
    """A padded layer mirrored top to bottom about design row `row` (the blade raised: it points up)."""
    y = P + row
    out = np.zeros_like(layer)
    for i in range(layer.shape[0]):
        j = 2 * y - i
        if 0 <= j < layer.shape[0]:
            out[j] = layer[i]
    return out


def hflip(layer, col):
    """A padded layer mirrored left to right about design column `col` (the cannon turned to point forward)."""
    x = P + col
    out = np.zeros_like(layer)
    for i in range(layer.shape[1]):
        j = 2 * x - i
        if 0 <= j < layer.shape[1]:
            out[:, j] = layer[:, i]
    return out


class Form:
    """The design's layers; pose() -> canvas."""

    def __init__(self, D, rig_pad):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        L = {k: pad(D.layer(k)) for k in D.order}
        self.L = L
        self.gun_fwd = hflip(L["gun"], GUN_MIRROR)
        self.blade_up = vflip(L["blade"], 44)
        self.ref_holes = None
        L["body_bare"] = bare_body(D, L["body"])
        # Codex's gun-hand poses (tools/art/design_gangplank_poses.py): the stamp and its edit mask on the design's grid
        # with PT rows above and PL columns left of it
        self.stamps = {}
        for k in ("Q", "R"):
            st = np.asarray(Image.open(lp(os.path.join(SRC, f"pose_{k}.png"))).convert("RGBA")).copy()
            ed = np.asarray(Image.open(lp(os.path.join(SRC, f"pose_{k}_edit.png")))) > 0
            self.stamps[k] = (st, ed)

    def pose(self, crouch=0, whole=(0, 0), gun=(0, 0), gun_fwd=False, gun_rot=0, arm=None, hand=(0, 0), blade=None,
             blade_up=False, legs=None, leg_layers=None, fill=True, no_blade=False, sword=0, sword_at=(0, 0), arm_rot=0,
             stamp=None, legs_under=None):
        """crouch: rows the body (with hands and props) sets down onto the legs; whole: the whole figure; gun: the
        cannon and the near arm moved together (arm: the arm's own move, default = gun's); gun_fwd: the cannon mirrored
        to point forward; gun_rot: quarter turns of the cannon counter-clockwise about GUN_PIVOT; hand: the far fist with the cutlass (blade: the blade's own move, default = hand's);
        blade_up: the blade mirrored to point up from the fist; legs: ((near dx, dy), (far dx, dy))."""
        if crouch < 0:
            raise ValueError("the body never lifts off the legs")
        wx, wy = whole
        U = (wx, wy + crouch)
        (nlx, nly), (flx, fly) = legs or ((0, 0), (0, 0))
        L = self.L
        arm = gun if arm is None else arm
        blade = hand if blade is None else blade
        legs_l = leg_layers if leg_layers is not None else [(L["far_leg"], dict(dx=wx + flx, dy=wy + fly)),
                                                             (L["near_leg"], dict(dx=wx + nlx, dy=wy + nly))]
        # the lower legs over the body: a cuff lifted or the body sunk hides the thigh's lowest rows (the knee bends);
        # legs_under (the walk's drawn legs): under the body, which is then the design's without its trousers
        layers = [*(legs_under or []), (L["body_bare" if legs_under else "body"], dict(dx=U[0], dy=U[1])), *legs_l]
        if stamp is None:
            layers += [(L["near_arm"], dict(dx=U[0] + arm[0], dy=U[1] + arm[1], rot=arm_rot, about=ELBOW)),
                       (self.gun_fwd if gun_fwd else L["gun"], dict(dx=U[0] + gun[0], dy=U[1] + gun[1], rot=gun_rot,
                                                                     about=GUN_PIVOT))]
        if sword:
            # the whole sword arm (upper arm, forearm, fist, cutlass) turned `sword` quarter turns counter-clockwise
            # about the far shoulder, then moved sword_at
            o = dict(dx=U[0] + sword_at[0], dy=U[1] + sword_at[1], rot=sword, about=SHOULDER)
            layers += [(L["far_upper"], o), (L["blade"], o), (L["far_hand"], o)]
        else:
            layers.append((L["far_upper"], dict(dx=U[0], dy=U[1])))
            if not no_blade:
                layers.append((self.blade_up if blade_up else L["blade"], dict(dx=U[0] + blade[0], dy=U[1] + blade[1])))
            layers.append((L["far_hand"], dict(dx=U[0] + hand[0], dy=U[1] + hand[1])))
        can = R.compose(self.rig, layers)
        if stamp is not None:
            # Codex's arm, cannon and near shoulder put on with the upper body, clear squares too (the old arm's place)
            st, ed = self.stamps[stamp]
            ys, xs = np.nonzero(ed)
            cy = ys - PT + self.rig.oy + U[1]
            cx = xs - PL + self.rig.ox + U[0]
            can[cy, cx] = st[ys, xs]
        return self.close_holes(can) if fill else can

    MOST = 10

    def close_holes(self, can):
        """Small enclosed holes the idle does not have (where a turned arm leaves its shoulder) filled from the squares
        round them."""
        if self.ref_holes is None:
            idle = self.pose(fill=False)
            op = idle[..., 3] > 0
            self.ref_holes = ndimage.binary_dilation(ndimage.binary_fill_holes(op) & ~op, iterations=2)
        op = can[..., 3] > 0
        holes = ndimage.binary_fill_holes(op) & ~op & ~self.ref_holes
        lbl, n = ndimage.label(holes)
        fill = np.zeros_like(holes)
        for k in range(1, n + 1):
            m = lbl == k
            if m.sum() <= self.MOST:
                fill |= m
        if not fill.any():
            return can
        out = R.fill_under(can, fill)
        left = fill & (out[..., 3] == 0)
        if left.any():
            src = (out[..., 3] > 0) & (out[..., :3].astype(int).sum(-1) >= 70)
            _, (iy, ix) = ndimage.distance_transform_edt(~src, return_indices=True)
            out[left] = out[iy[left], ix[left]]
        return out


def form():
    return Form(design(), rig_pad=(40, 40, 30, 12))


def over(base, top):
    out = base.copy()
    m = top[..., 3] > 0
    out[m] = top[m]
    return out


def sheet(cans, path, z=4):
    allc = np.stack(cans)
    ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
    y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    tiles = []
    for c in cans:
        bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
        bg.alpha_composite(Image.fromarray(c[y0:y1, x0:x1]))
        tiles.append(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
    out = Image.new("RGB", (sum(t.width + 6 for t in tiles), tiles[0].height), (40, 40, 40))
    x = 0
    for t in tiles:
        out.paste(t, (x, 0))
        x += t.width + 6
    out.save(lp(path))


# frame lengths (ms), timed to the kit (tools/kit/build_gangplank.py): attack 26 ticks (433 ms), the hit on tick 9;
# Q 24 (400), the shot on tick 10; E 22 (367), the keg on tick 9; W 20 (333), the bite on tick 10; R 24 (400), the
# flare on tick 10
MS = {"idle": [140] * 8, "run": [110] * 8, "attack": [60, 80, 100, 100, 93], "skill": [80, 80, 90, 90, 60],
      "skill2": [70, 80, 90, 70, 57], "skill_w": [80, 90, 60, 60, 43], "ult": [80, 90, 100, 80, 50],
      "hit": [100, 100], "dead": [100, 100, 120, 70, 100, 60, 120, 500]}

# The idle's breath and the walk's bob: the body (thighs too) sets down a row onto the lower legs, which are drawn over
# it - the cuffs hide the thighs' lowest row, the boots stay where they stand (league_jarvaniv's dip)


def frames_all(F):
    p = F.pose
    out = {}
    out["idle"] = [p(crouch=1) if b else p() for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    # auto attack (League's Gangplank_Attack1/2: the cutlass raised and brought down in a big chop): the whole sword arm
    # - upper arm, red-wrapped forearm, fist and cutlass, one piece - turned a quarter about the far shoulder so it
    # reaches forward with the blade up (the user: the blade mirrored up from a fist at the hip read 「很奇怪 变形」),
    # moved down 4-7 rows so it leaves the shoulder line UNDER the beard (turned about the shoulder point alone its top
    # edge ran along the beard: 「左手攻击时候头部感觉很怪」), the head still; the chop down to its hanging place (frame 3, the hit on a_hit), stepping in; back
    out["attack"] = [p(sword=1, sword_at=(-1, 6)), p(sword=1, sword_at=(0, 3)),
                     p(crouch=1, whole=(1, 0)), p(crouch=1, whole=(1, 0)), p()]
    # Q Parrrley (League's Gangplank_Spell1: the arm held straight out, the pistol aimed forward at the chest): Codex's
    # pose Q (tools/art/design_gangplank_poses.py) - the near arm out from the shoulder, the cannon aimed past the beard,
    # the near shoulder and the coat's side drawn whole - on the design's own body (the arm posed from the design's
    # squares read 「左手攻击导致身体看起来非常非常奇怪」); stepping in, the shot (frame 3, q_rel), the recoil (frame 4:
    # the cannon kicked up to the sky - Codex's pose R - as League's frames 4-6; 2026-10-19 frame audit: it only stepped
    # back), back
    out["skill"] = [p(stamp="Q"), p(whole=(1, 0), stamp="Q"), p(whole=(1, 0), stamp="Q"), p(stamp="R"), p()]
    # E Powder Keg (League's Gangplank_Spell3: a keg set down with a stoop): he bends at the knees as he puts it down (frame 3, e_rel - the keg itself is thrown by the kit at the enemy's feet), up again
    # (the arms go down with the body: a fist moved off its forearm pulled the wrist apart - 「左手...变形」); up with the
    # cutlass raised as League's frames 4-6 (the attack's first two poses, the whole sword arm turned about the shoulder;
    # 2026-10-19 frame audit: it only stooped)
    out["skill2"] = [p(crouch=1), p(crouch=2), p(whole=(1, 0), crouch=2), p(sword=1, sword_at=(-1, 6)),
                     p(sword=1, sword_at=(0, 3))]
    # W Remove Scurvy (League's Gangplank_Spell2: a bite of citrus): his near hand is at his mouth already - he bows into
    # the bite and chews (frames 2-3, w_rel; the fruit is the effect w_cast); the hand never moves toward the face (a
    # square nearer, the cannon covered the hat's brim and his cheek)
    out["skill_w"] = [p(crouch=1), p(crouch=2), p(crouch=1), p(crouch=2), p()]
    # R Cannon Barrage (League's Gangplank_Spell4: the pistol held straight up as the signal): Codex's pose R - the near
    # arm raised straight up beside the hat, the cannon to the sky - on the design's own body; up on his toes as the
    # flare is fired (frame 3, r_rel; the flare is the effect r_cast), down; first a crouch with the cannon still on his
    # shoulder, as League's frames 1-2 (2026-10-19 frame audit: four frames of one pose)
    out["ult"] = [p(crouch=1), p(stamp="R"), p(whole=(0, -1), stamp="R"), p(stamp="R"), p()]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # the death (League's Gangplank_Death: he staggers and falls back): back, down on his knees, on his back (a quarter
    # turn counter-clockwise, the head to the back), lying sunk into the ground line
    sink = p(crouch=2, whole=(-1, 0))
    sit = p(crouch=4, whole=(-1, 0))
    # (turned from his standing frame: from the crouch the lower legs, drawn over the body, piled onto it)
    lying = R.lie(F.rig, p(no_blade=True), k=1, dx=-2, sink=6)   # the cutlass dropped under him

    # (8 frames since the 2026-10-19 frame audit: the fall lands 3 rows above the ground, lies, bounces a row, lies)
    def off(n):
        f = np.zeros_like(lying)
        f[:-n] = lying[n:]
        return f
    out["dead"] = [p(whole=(-1, 0)), sink, sit, off(3), lying, off(1), lying.copy(), lying.copy()]
    return out


# ------------------------------------------------------------------------------------------------- the walk
# The design's own lower legs moved whole (memory codex-legs-deform) under thighs that stay on the body: each cuff and
# boot steps on its own side, planted and sliding back, then lifted and carried forward, the far one half a cycle later
# - a stride of 2 (the cuffs never slide more than a square off the thighs) - the body set down a row on each contact
# and the whole figure a row up as the legs pass (league_ziggs's D walk, league_braum's spring); the hands never move
# against the body (「手臂有点变形吧」).
def _steps(stride, lifts):
    near = [round(stride * (1 - k / 4) + 1e-9) for k in range(5)]
    swing = [1, stride - 1 - (stride > 4), stride]
    dx = [v - stride // 2 for v in near + swing]
    up = [0] * 5 + list(lifts)
    return dict(near=list(zip(dx, up)), far=[(dx[(i + 4) % 8], up[(i + 4) % 8]) for i in range(8)],
                bob=[1, 0, 0, 0, 1, 0, 0, 0])


# stride 2: the boots stand 3 squares apart in his stance, and a stride of 4 brought them together on the contact
# frames - one wide merged boot (「脚这里变形」); now they never touch, the step reads from the lift and the spring
WALK_STEP = dict(_steps(2, (1, 2, 1)), rise=[0, 0, 1, 0, 0, 0, 1, 0])


def walk(F, steps=None):
    st = steps or WALK_STEP
    out = []
    L = F.L
    rise = st.get("rise", [0] * len(st["bob"]))
    for (ndx, nup), (fdx, fup), bob, up in zip(st["near"], st["far"], st["bob"], rise):
        legs = [(L["far_leg"], dict(dx=fdx, dy=-fup - up)), (L["near_leg"], dict(dx=ndx, dy=-nup - up))]
        out.append(F.pose(whole=(0, bob - up), leg_layers=legs))
    return out


# The walk since 2026-10-22 (the user: 「船长的走路脚好像变形的」 - the sixth time on his feet). Codex's walk below (its
# eight frames are the design's upper body, square for square, over Codex's legs) crossed his feet in a 3/4 view: in
# frames 2, 3 and 5 the two stamped boots lay over each other as one misshapen block, the trousers above them in
# patches. Now the legs are drawn on League's gangplank_run (RUN_JOINTS, from
#   python tools/lol/pose_joints.py assets/source/gangplank/poses.json --tag run
#       --joints Pelvis,L_Hip,L_KneeLower,L_Foot,L_Toe,R_Hip,R_KneeLower,R_Foot,R_Toe --json assets/source/gangplank/run_joints.json;
# League's L leg is the near one), the way league_jarvaniv's and league_jax's runs are: each trouser leg a thigh and a
# shin from his hip on League's angles (the knee solved where League's foot stands, rigkit.leg_chain), in the design's
# two teals lit on the left with one outline, the design's own cuff and boot on the ankle; the far leg in the design's
# colours RUN_FAR_DIM darker and standing RUN_FAR_UP row higher (passing, the near boot reads in front of it, never one
# block); the hips RUN_HIP 5 columns apart (8 in the stance: crossing, the boots lay over each other); the legs under the
# body, so the coat, the sash and the belt hang over the trousers' tops as drawn. The design's upper body bobs with
# League's hips (rigkit.hip_bobs, 0-RUN_BOB rows). His legs are short (11 squares hip to ankle): the bones are
# RUN_BONE long, the knees a little bent standing, so the feet travel about as far as Codex's did.
RUN_JOINTS = os.path.join(R.ROOT, "assets", "source", "gangplank", "run_joints.json")
RUN_HIP = {"near": (26.0, 43.0), "far": (31.0, 43.0)}         # under the belt
RUN_ANKLE = {"near": (18.5, 53.0), "far": (31.5, 53.0)}       # the design's cuffs' top middles, its boots standing
RUN_BONE = 7.0                                                # thigh and shin
RUN_HW = {"near": (3.0, 2.6, 2.2), "far": (2.7, 2.4, 2.0)}   # trouser half widths at the hip, the knee, the ankle
RUN_TEAL = {"near": ((57, 88, 87), (39, 57, 57)), "far": ((39, 57, 57), (30, 44, 44))}   # lit, shaded
RUN_TROUSERS = (41, 15, 37)                                   # the design's trousers: from this row, these columns
RUN_FAR_DIM, RUN_FAR_UP = 0.75, 0
RUN_PLANT_TOE = 7.9                                           # a League toe this low (game px; the soles on 11) stands
RUN_BOB = 2


def bare_body(D, body):
    """The body layer without the trousers (the teal under the belt) and the outline squares that border only them
    or air."""
    d = D.d.astype(int)
    tm = (d[..., 3] > 0) & (d[..., 1] > d[..., 0] + 15) & (d[..., 2] > d[..., 0] + 5)
    y0, x0, x1 = RUN_TROUSERS
    tm[:y0] = False
    tm[:, :x0] = False
    tm[:, x1 + 1:] = False
    m = np.zeros(body.shape[:2], bool)
    m[P:P + D.H, P:P + D.W] = tm
    out = body.copy()
    op = out[..., 3] > 0
    line = op & np.all(out[..., :3] == np.array(D.outline), -1)
    keep = op & ~m & ~line
    lone = line & ndimage.binary_dilation(m, np.ones((3, 3), bool)) & ~ndimage.binary_dilation(keep, np.ones((3, 3), bool))
    out[m | lone] = 0
    return out


def run_bone(shape, p0, p1, hw0, hw1):
    """A tapered segment p0 -> p1 (design coordinates) in a padded layer -> (mask, side: -1..1 across it, + left)."""
    H, W = shape
    ys, xs = np.mgrid[0:H, 0:W]
    px, py = xs + 0.5 - P, ys + 0.5 - P
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    l2 = max(dx * dx + dy * dy, 1e-6)
    t = ((px - x0) * dx + (py - y0) * dy) / l2
    tc = np.clip(t, 0, 1)
    hw = hw0 + (hw1 - hw0) * tc
    m = (np.hypot(px - (x0 + tc * dx), py - (y0 + tc * dy)) <= hw) & (t >= -0.25) & (t <= 1.15)
    return m, ((px - x0) * dy - (py - y0) * dx) / math.sqrt(l2) / np.maximum(hw, 1e-6)


def run_leg(F, side, hip, knee, ank):
    """One trouser leg hip -> knee -> ankle with the design's own cuff and boot on the ankle -> padded layer."""
    D = F.D
    shape = (D.H + 2 * P, D.W + 2 * P)
    lay = np.zeros(shape + (4,), np.uint8)
    w0, w1, w2 = RUN_HW[side]
    m1, s1 = run_bone(shape, hip, knee, w0, w1)
    m2, s2 = run_bone(shape, knee, ank, w1, w2)
    m = m1 | m2
    lit, shade = RUN_TEAL[side]
    s = np.where(m2, s2, s1)
    lay[m & (s > -0.15)] = lit + (255,)
    lay[m & (s <= -0.15)] = shade + (255,)
    lay[ndimage.binary_dilation(m, np.ones((3, 3), bool)) & ~m] = tuple(D.outline) + (255,)
    ax, ay = RUN_ANKLE[side]
    boot = K.shifted(F.L[side + "_leg"], int(round(ank[0] - ax)), int(round(ank[1] - ay)))
    bm = boot[..., 3] > 0
    lay[bm] = boot[bm]
    if side == "far":
        pal = np.array(sorted({tuple(c) for c in D.d[D.d[..., 3] > 0][:, :3].tolist()} - {tuple(D.outline)}), float)
        dim = (lay[..., 3] > 0) & np.any(lay[..., :3] != np.array(D.outline), -1)
        want = lay[dim, :3].astype(float) * RUN_FAR_DIM
        lay[dim, :3] = pal[np.argmin(((want[:, None, :] - pal[None]) ** 2).sum(-1), 1)].astype(np.uint8)
    return lay


def league_walk(F):
    """The walk: a frame per League run frame (RUN_JOINTS). -> canvases."""
    with open(lp(RUN_JOINTS), encoding="utf-8") as f:
        joints = json.load(f)
    bobs = K.hip_bobs([fr["joints"]["Pelvis"][1] for fr in joints], RUN_BOB)
    out = []
    for k, fr in enumerate(joints):
        j = fr["joints"]
        legs = {}
        for side, s in (("near", "L"), ("far", "R")):
            th = K.bone_angle(j[f"{s}_Hip"][:2], j[f"{s}_KneeLower"][:2])
            sh = K.bone_angle(j[f"{s}_KneeLower"][:2], j[f"{s}_Foot"][:2])
            hip = (RUN_HIP[side][0], RUN_HIP[side][1] + bobs[k])
            ground = RUN_ANKLE[side][1] - (RUN_FAR_UP if side == "far" else 0)
            knee, ank, _, _, _ = K.leg_chain(hip, th, sh, RUN_BONE, RUN_BONE, ground,
                                             j[f"{s}_Toe"][1] >= RUN_PLANT_TOE)
            legs[side] = run_leg(F, side, hip, knee, ank)
        can = F.pose(whole=(0, bobs[k]), leg_layers=[], legs_under=[(legs["far"], {}), (legs["near"], {})], fill=False)
        out.append(F.close_holes(can))
    return out


# The walk from 2026-10-18 to 2026-10-22 (the user: 「船长走路也有点僵硬的」; kept for the record): Codex's skin swap over
# oppi's Swain run (Akshan's accepted way), assets/source/gangplank/hd/run_<k>.png read back by
# tools/art/design_gangplank_run.py with the design's head, hat and hand cannon stamped on. Each frame stands with its
# soles on the design's ground row and the middle of its red sash (the hips) over the design's, so the body does not
# slide from frame to frame. walk() above stays for reference too.
RUN_FRAMES = 8


def sash_x(a):
    """The middle column of the red sash (bright red under the belly) in the lower half of a frame."""
    h = a.shape[0]
    low = a[h // 2:h - 8].astype(int)
    m = (low[..., 3] > 0) & (low[..., 0] > 170) & (low[..., 1] < 90) & (low[..., 2] < 90)
    return float(np.nonzero(m)[1].mean())


def codex_walk(F):
    rig, D = F.rig, F.D
    cx = sash_x(D.d)
    out = []
    for k in range(RUN_FRAMES):
        f = load(f"run_{k}.png")
        h, w = f.shape[:2]
        x0 = rig.ox + int(round(cx - sash_x(f)))
        y0 = rig.oy + D.ground - h
        can = rig.canvas()
        m = f[..., 3] > 0
        can[y0:y0 + h, x0:x0 + w][m] = f[m]
        out.append(can)
    return out


def frames(F):
    """{tag: [(canvas, ms)]} in the sheet's order."""
    a = frames_all(F)
    a = {"idle": a["idle"], "run": league_walk(F), **{k: v for k, v in a.items() if k != "idle"}}
    out = {}
    for tag, cans in a.items():
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def audit(F, acts, out_dir):
    """Every frame after ppu_rig's finish(): its pieces (8-connected), new enclosed holes, colours in no design,
    outline squares with no colour beside them (rig_jarvaniv.audit); each tag at 6x."""
    from PIL import ImageDraw
    os.makedirs(lp(out_dir), exist_ok=True)
    rig = F.rig
    allowed = {tuple(c) for c in F.D.d[F.D.d[..., 3] > 0][:, :3].tolist()} | {tuple(F.D.outline)}
    idle = rig.finish(acts["idle"][0][0])
    iop = idle[..., 3] > 0
    idark = iop & (np.abs(idle[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
    base_orphan = int((idark & ~ndimage.binary_dilation(iop & ~idark, structure=R.CROSS)).sum())
    idle_holes = ndimage.binary_fill_holes(iop) & ~iop
    bad = 0
    for tag, fr in acts.items():
        tiles = []
        for i, (c, _) in enumerate(fr):
            f = rig.finish(c)
            op = f[..., 3] > 0
            lbl, n = ndimage.label(op, structure=np.ones((3, 3)))
            sz = sorted(ndimage.sum(op, lbl, range(1, n + 1)).astype(int).tolist(), reverse=True) if n else []
            holes = ndimage.binary_fill_holes(op) & ~op
            new = holes & ~ndimage.binary_dilation(idle_holes, iterations=3)
            odd = {tuple(v) for v in f[op][:, :3].tolist()} - allowed
            dk = op & (np.abs(f[..., :3].astype(int) - np.array(F.D.outline)).sum(-1) < 30)
            orphan = dk & ~ndimage.binary_dilation(op & ~dk, structure=R.CROSS)
            pieces_ok = len(sz) == 1 or (tag == "dead" and len(sz) <= 3)
            flag = (not pieces_ok) or new.sum() or (odd and "hit" not in tag) or orphan.sum() > base_orphan
            bad += bool(flag)
            print(f"{tag:10s} {i + 1}: pieces {sz[:4]} new holes {int(new.sum())} odd colours {len(odd)} "
                  f"orphan outline {int(orphan.sum())}{'  <--' if flag else ''}")
            show = f.copy()
            show[new] = (255, 0, 255, 255)
            show[orphan] = (255, 128, 0, 255)
            tiles.append(show)
        allc = np.stack(tiles)
        ys, xs = np.nonzero(allc[..., 3].max(0) > 0)
        y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
        z = 6
        sheet_ = Image.new("RGB", (len(tiles) * ((x1 - x0) * z + 8), (y1 - y0) * z + 16), (40, 40, 40))
        dr = ImageDraw.Draw(sheet_)
        for i, t in enumerate(tiles):
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]))
            sheet_.paste(bg.convert("RGB").resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST),
                         (i * ((x1 - x0) * z + 8), 16))
            dr.text((i * ((x1 - x0) * z + 8) + 2, 2), str(i + 1), fill=(255, 255, 0))
        sheet_.save(lp(os.path.join(out_dir, f"{HERO}_{tag}_6x.png")))
    print("frames flagged:", bad)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--audit")
    a = ap.parse_args()
    if not (a.audit or a.review or a.parts):
        F = form()
        # Q's muzzle flash, W's orange and R's flare drawn into his own frames (assets/source/native/gangplank_bake.json;
        # import_gangplank_fx.py first): they turn with him, the red side included
        F.rig.export(F.rig.bake(frames(F), hero=HERO.replace("league_", "")))
        return
    if a.audit or a.review:
        F = form()
        acts = frames(F)
        if a.audit:
            audit(F, acts, a.audit)
        else:
            F.rig.review(acts, a.review)
        return
    os.makedirs(a.parts, exist_ok=True)
    D = design()
    R.Design.ruler(D, os.path.join(a.parts, f"{HERO}_parts.png"), z=12)
    F = form()
    idle = F.pose()
    ref = F.rig.canvas()
    ref[F.rig.oy:F.rig.oy + D.H, F.rig.ox:F.rig.ox + D.W] = D.d
    print("idle vs design: squares differing", int((np.abs(idle.astype(int) - ref.astype(int)).sum(-1) > 0).sum()))
    tries = [F.pose(), F.pose(arm_rot=3, arm=(3, -3), gun_fwd=True, gun=(22, 10)), F.pose(sword=1, sword_at=(0, 4)),
             F.pose(gun_rot=3, gun=(0, -6), arm=(0, -4)), F.pose(crouch=2)]
    sheet([F.rig.finish(c) for c in tries], os.path.join(a.parts, f"{HERO}_tries.png"))


if __name__ == "__main__":
    main()
