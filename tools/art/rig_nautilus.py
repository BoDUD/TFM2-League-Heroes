#!/usr/bin/env python3
"""Nautilus's action strips posed from the approved design's own parts (tools/art/rigkit.py; the casting body = the idle's).

    python tools/art/rig_nautilus.py [--check] [--review DIR] [--tags attack,skill] [--parts DIR]

Codex's step-2 delivery (assets/source/nautilus/codex_strips/) re-posed the design from parts, but drew the arms as
thick lines at any angle (a dark slab for the far arm in the run and W+E), left holes where it cut the near arm out
(attack, Q, R), slid the body into the ground for the death and broke the run's legs into overlapping scraps. The user:
「codex交付了 奇怪的地方你帮我修复吧 完美版本了喊我review」. Every frame here is the design (tools/art/design_nautilus.py
p35: 39 x 48, the helmet 37 rows over the soles, the anchor 11 above it) with only what the action moves moved, by
lossless moves only (the user's rules: never rotate a design piece by an arbitrary angle - draw limbs in the design's
colours instead; fix only what is reported):
- the ANCHOR (the crown and both flukes, the shank with its rope and red band) and the near hand gripping it are ONE
  rigid unit, turned by the exact quarter turns of the square grid about the grip; the chain hangs from that hand,
  always straight down (cut at the feet line);
- the near arm, where the hand leaves the shoulder, is drawn shoulder -> elbow -> wrist in the design's own suit
  colours with its bronze bracer (rigkit.bone_arm); the far arm likewise for W+E's punch, its own glove as the fist;
- what the anchor and the hand covered in the design (the hood's top-left, the gap between the near shoulder plate
  and the helmet) is restored once in the bare body (the hood mirrored from its right half, the near arm's suit);
- the body leans by whole-row shifts above the hips, crouches by sinking over the standing boots, hops by moving whole;
- the run: the legs stride on League's run (assets/source/nautilus/run_joints.json, tools/lol/pose_joints.py), drawn
  thigh and shin in the design's suit colours with its own knee guards and boots, the body bobbing with League's hips.
League's renders (assets/source/nautilus/poses.json, %TEMP%/nt_work/pose_n) give the poses.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "nautilus_native.png")
HERO = "nautilus"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 128), (64, 88)


def spans(spec):
    """{row: [(first, last), ...]} -> bool mask."""
    m = np.zeros((128, 128), bool)
    for r, ranges in spec.items():
        for c0, c1 in ranges:
            m[r, c0:c1 + 1] = True
    return m


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[k:k + 2], 16) for k in (0, 2, 4))


# ---------------------------------------------------------------------------------------------- parts (canvas rows)
# the anchor: the crown bar over his hood with the rope round its right end, the left fluke hanging to row 75, the right
# fluke to row 67, the shank from the crown down past the near shoulder to the red band over the hand
ANCHOR = {52: [(58, 61)], 53: [(57, 70)], 54: [(54, 55), (57, 73)], 55: [(53, 74)], 56: [(53, 75)], 57: [(51, 75)],
          58: [(50, 76)], 59: [(49, 77)], 60: [(48, 78)], 61: [(47, 61), (70, 78)], 62: [(46, 61), (73, 78)],
          63: [(45, 59), (74, 78)], 64: [(45, 50), (52, 57), (75, 77)], 65: [(45, 49), (51, 56), (75, 77)],
          66: [(45, 48), (52, 56), (76, 76)], 67: [(44, 48), (52, 55), (76, 76)], 68: [(44, 47), (52, 55)],
          69: [(43, 47), (52, 54)], 70: [(43, 48), (51, 54)], 71: [(43, 47), (51, 54)], 72: [(43, 46), (51, 54)],
          73: [(44, 46), (52, 54)], 74: [(44, 46), (52, 53)], 75: [(45, 45), (52, 53)], 76: [(52, 54)],
          77: [(52, 54)], 78: [(52, 54)], 79: [(51, 54)], 80: [(51, 53)]}
# the near hand on the shank (the grey glove, the bracer's bronze on its left)
HAND = {81: [(49, 54)], 82: [(47, 54)], 83: [(47, 52)], 84: [(47, 52)], 85: [(47, 53)]}
# the chain hanging from that hand down beside the near boot
CHAIN = {86: [(48, 53)], 87: [(50, 53)], 88: [(49, 53)], 89: [(49, 53)], 90: [(49, 53)], 91: [(49, 53)],
         92: [(49, 53)], 93: [(49, 53)], 94: [(49, 53)], 95: [(49, 52)], 96: [(49, 52)], 97: [(49, 52)],
         98: [(49, 52)]}
GRIP = (51.0, 83.5)                    # the near fist's middle: the unit turns about it
WRIST = (48.0, 82.0)                   # where the near forearm meets the glove (the bracer's side)
SHOULDER = (50.5, 76.5)                # the near arm's root under the shoulder plate
CHAIN_TOP = (51.0, 86.0)               # the chain hangs from here (under the fist)

# the far arm hanging at his side: the shoulder plate's lower half, the bronze bracer and the grey glove
FAR_ARM = {80: [(75, 79)], 81: [(75, 79)], 82: [(74, 80)], 83: [(75, 80)], 84: [(73, 80)], 85: [(75, 81)],
           86: [(76, 81)], 87: [(76, 81)], 88: [(76, 80)], 89: [(77, 80)], 90: [(78, 78)]}
FAR_GLOVE = {85: [(75, 81)], 86: [(76, 81)], 87: [(76, 81)], 88: [(76, 80)], 89: [(77, 80)], 90: [(78, 78)]}
FAR_SHOULDER = (76.5, 79.5)
FAR_FIST = (78.5, 87.5)
# the far forearm with its glove (under the shoulder plate): ONE rigid piece turned about the elbow by quarter turns
# (the user: 「手臂不要有这种严重变形的 长手怪的东西」 - no drawn arm longer than the design's own)
FAR_FORE = {82: [(75, 80)], 83: [(75, 80)], 84: [(75, 80)], 85: [(75, 81)], 86: [(76, 81)], 87: [(76, 81)],
            88: [(76, 80)], 89: [(77, 80)], 90: [(78, 78)]}
FAR_ELBOW = (78.0, 82.0)
NEAR_REACH = 9.5                       # the near fist stays this close to the shoulder (the far arm's own length)

# the legs below the hip band (row 90): the knee guards, the shins and the boots
NEAR_LEG = {91: [(53, 62)], 92: [(54, 61)], 93: [(54, 59)], 94: [(53, 59)], 95: [(53, 58)], 96: [(53, 58)],
            97: [(53, 59)], 98: [(53, 59)], 99: [(50, 57)]}
FAR_LEG = {91: [(68, 77)], 92: [(69, 77)], 93: [(70, 77)], 94: [(70, 77)], 95: [(70, 77)], 96: [(71, 78)],
           97: [(70, 79)], 98: [(70, 79)], 99: [(71, 79)]}
NEAR_BOOT = {96: [(53, 58)], 97: [(53, 59)], 98: [(53, 59)], 99: [(50, 57)]}
FAR_BOOT = {96: [(71, 78)], 97: [(70, 79)], 98: [(70, 79)], 99: [(71, 79)]}
HIP_ROW = 90                           # the hip band's bottom row: rows above lean / sink, the legs below stand
NECK_ROW = 63                          # the hood's top: the head moves whole with this row's shift

# the design's suit and bracer colours (dark to light) for the drawn limbs
SUIT = ("#3D4150", "#2D3041", "#0B021A")       # lit, mid, dark
BRACER = ("#FAAC2A", "#DC741C", "#A84217")


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a
        op = a[..., 3] > 0
        self.anchor_m = spans(ANCHOR) & op
        self.hand_m = spans(HAND) & op & ~self.anchor_m
        self.chain_m = spans(CHAIN) & op
        self.far_m = spans(FAR_ARM) & op
        self.far_glove_m = spans(FAR_GLOVE) & op
        self.far_fore_m = spans(FAR_FORE) & op
        self.near_leg_m = spans(NEAR_LEG) & op & ~self.chain_m
        self.far_leg_m = spans(FAR_LEG) & op
        unit = np.zeros_like(a)
        for m in (self.anchor_m, self.hand_m):
            unit[m] = a[m]
        self.unit_canvas = unit
        self.unit = K.Part.from_canvas(unit, unit[..., 3] > 0, GRIP)
        chain = np.zeros_like(a)
        chain[self.chain_m] = a[self.chain_m]
        self.chain = K.Part.from_canvas(chain, chain[..., 3] > 0, CHAIN_TOP)
        bare = a.copy()
        for m in (self.anchor_m, self.hand_m, self.chain_m):
            bare[m] = 0
        self.bare = bare


# ---------------------------------------------------------------------------------------------- the bare body
# what the anchor's shank and the near hand covered: between the near shoulder plate (cols 49-51) and the helmet's rust
# rim (col 55) the shank ran down cols 52-54; under it, the near upper arm in the suit's colours (lit, mid, dark)
SHOULDER_FILL = {r: [(52, 54)] for r in range(73, 81)}


def bare_body(P):
    """The design without the anchor, the near hand and the chain, the near shoulder joined to the helmet again."""
    a = P.bare.copy()
    lit, mid, dark = (hexrgb(h) for h in SUIT)
    for r, ranges in SHOULDER_FILL.items():
        for c0, c1 in ranges:
            for c in range(c0, c1 + 1):
                if a[r, c, 3] == 0 or tuple(int(v) for v in a[r, c, :3]) == P.D.outline:
                    a[r, c] = (*(lit if c == c0 else mid if c < c1 else dark), 255)
    return a


# ---------------------------------------------------------------------------------------------- the anchor unit
# the eight exact symmetries, named by where the crown is from the fist: "up" as drawn (the crown over the fist, its
# bar reaching 28 to the right), "up_l" mirrored (reaching left), "fwd" a quarter turn clockwise (the crown to the
# right, hanging 28 below the shank), "fwd_up" its mirror top to bottom (the crown to the right, rising 28 above it),
# "down" the design upside down (the crown under the fist reaching right), "down_l" a half turn (reaching left),
# "back" a quarter turn anticlockwise (the crown to the left, rising above the shank), "back_dn" its mirror
def orient(part, name):
    return {"up": part, "up_l": part.flip_h(), "fwd": K.rot90(part, 1), "fwd_up": K.rot90(part, 1).flip_v(),
            "down": part.flip_v(), "down_l": K.rot90(part, 2), "back": K.rot90(part, 3),
            "back_dn": K.rot90(part, 3).flip_v()}[name]


def turned_offset(name, off):
    """A point given relative to the fist on the design (dx, dy) in the orientation `name`."""
    x, y = off
    return {"up": (x, y), "up_l": (-x, y), "fwd": (-y, x), "fwd_up": (-y, -x), "down": (x, -y), "down_l": (-x, -y),
            "back": (y, -x), "back_dn": (y, x)}[name]


def arm_mats(bracer_from=0.5):
    suit = tuple(hexrgb(h) for h in SUIT)
    br = tuple(hexrgb(h) for h in BRACER)
    return {"upper": [(0, 1, suit)], "fore": [(0, bracer_from, suit), (bracer_from, 1, br)]}


def draw_arm(c, shoulder, wrist, outline):
    """The near arm's short stretch from under the shoulder plate to the glove: one thick straight bone in the suit's
    colours with the bracer's bronze at the glove end - only as long as the fist is from the shoulder (NEAR_REACH)."""
    arm = np.zeros_like(c)
    d = math.hypot(wrist[0] - shoulder[0], wrist[1] - shoulder[1])
    if d < 1.5:
        return arm
    mid = ((shoulder[0] + wrist[0]) / 2, (shoulder[1] + wrist[1]) / 2)
    K.bone_arm(arm, shoulder, mid, wrist, arm_mats(), width=(4.4, 4.0), outline=outline)
    return arm


# ---------------------------------------------------------------------------------------------- posing
BELT_ROW = 86                            # rows above move whole with a lean; from here to HIP_ROW the shift runs out


def lean_shift(row, lean):
    """Columns a row moves for a lean of `lean` columns: the whole upper body (the helmet is most of it and is never
    sheared), running out over the hip band (rows BELT_ROW..HIP_ROW), the legs standing."""
    if not lean or row > HIP_ROW:
        return 0
    if row < BELT_ROW:
        return lean
    return int(math.floor(lean * (HIP_ROW + 1 - row) / (HIP_ROW + 1 - BELT_ROW) + 0.5))


def leaned(a, lean):
    out = np.zeros_like(a)
    for y in range(a.shape[0]):
        d = lean_shift(y, lean)
        if d > 0:
            out[y, d:] = a[y, :-d]
        elif d < 0:
            out[y, :d] = a[y, -d:]
        else:
            out[y] = a[y]
    return out


def take(a, m):
    p = np.zeros_like(a)
    p[m] = a[m]
    return p


class Rig:
    """The parts once: the bare body, its boots, the anchor unit (with the fist), the anchor alone (its ring end
    drawn where the fist hid it), the fist alone, the chain, the far arm."""

    def __init__(self, P):
        self.P = P
        self.out = tuple(int(v) for v in P.D.outline)
        self.bare = bare_body(P)
        op = self.bare[..., 3] > 0
        self.near_boot_m = spans(NEAR_BOOT) & op
        self.far_boot_m = spans(FAR_BOOT) & op
        self.near_leg_m = spans(NEAR_LEG) & op
        self.far_leg_m = spans(FAR_LEG) & op
        a = P.D.a
        self.hand = K.Part.from_canvas(take(a, P.hand_m), P.hand_m, GRIP)
        anchor = take(a, P.anchor_m)
        # the shank's end the fist hid: the shank's two columns carried on down to a ring of the anchor's iron
        g = tuple(int(v) for v in a[76, 52, :3])
        s_ = tuple(int(v) for v in a[73, 52, :3])
        for r in range(81, 86):
            anchor[r, 51] = (*g, 255)
            anchor[r, 52] = (*s_, 255)
        for (r, c) in ((86, 50), (86, 53), (87, 50), (87, 53), (88, 51), (88, 52)):
            anchor[r, c] = (*g, 255)
        self.anchor = K.Part.from_canvas(anchor, anchor[..., 3] > 0, GRIP)
        self.unit = P.unit
        self.chain = P.chain
        self.far_fore_m = P.far_fore_m
        self.far_fore = K.Part.from_canvas(a, P.far_fore_m, FAR_ELBOW)

    def body(self, lean=0, sink=0, steps=(0, 0), far_off=False):
        """The bare body leant, its legs stepped (near / far leg moved whole, dx) and sunk `sink` rows over the
        boots."""
        a = self.bare.copy()
        if far_off:
            a[self.far_fore_m] = 0
        legs_m = self.near_leg_m | self.far_leg_m
        up = a.copy()
        up[legs_m] = 0
        # a step moves the whole leg (knee guard, shin, boot) sideways, never shears it (the run's way)
        near = K.shifted(take(a, self.near_leg_m & ~self.near_boot_m), steps[0], 0)
        far = K.shifted(take(a, self.far_leg_m & ~self.far_boot_m), steps[1], 0)
        nb = K.shifted(take(a, self.near_boot_m), steps[0], 0)
        fb = K.shifted(take(a, self.far_boot_m), steps[1], 0)
        top = np.zeros_like(a)
        K.put(top, far, 0, 0)
        K.put(top, leaned(up, lean), 0, 0)
        K.put(top, near, 0, 0)
        c = np.zeros_like(a)
        K.put(c, fb, 0, 0)
        K.put(c, nb, 0, 0)
        K.put(c, K.shifted(top, 0, sink), 0, 0)
        return c

    def hang_chain(self, c, top, under=False, length=13):
        ch = self.chain.s.copy()
        ch = ch[:max(3, min(length, ch.shape[0]))]
        K.place(c, K.Part(ch, self.chain.j), top, under=under)


# a pose (body coordinates: the design's canvas before the lean, the sink and the whole move):
#   unit: (orientation, fist (x, y), layer "behind" / "front" (over the body, under the helmet) / "over") or None
#   hand: (orientation, fist (x, y)) - the fist alone (the anchor thrown)
#   free: (orientation, fist-end (x, y)) - the anchor alone, not held (the death)
#   chain: "hang" (from the fist, straight down), "short" (5 links), "taut" (out to the right), None
#   far: the far fist (x, y) - the far arm drawn from its shoulder (W+E's punch)
#   lean (columns, + forward), sink (rows over the boots), steps (near, far boot dx), move (dx, dy) of the whole
#   dim: the eyes dimmed (the death's last frames)
def pose(**kw):
    d = dict(unit=None, hand=None, free=None, chain="hang", far=None, lean=0, sink=0, steps=(0, 0), move=(0, 0),
             dim=False, design=False)
    d.update(kw)
    return d


DESIGN_POSE = dict(design=True)
EYES_ON = ("#F94102", "#FDCC31", "#E4221F")
EYES_DIM = ("#8C3815", "#A84217", "#6F2610")


def compose(R, p):
    P = R.P
    if p.get("design"):
        c = P.D.a.copy()
        dx, dy = p.get("move", (0, 0))
        lean = p.get("lean", 0)
        if lean:
            c = leaned(c, lean)
        return K.shifted(c, dx, dy) if (dx or dy) else c
    lean, sink = p["lean"], p["sink"]
    c = R.body(lean, sink, p["steps"], far_off=p["far"] is not None)
    off = lambda pt: (pt[0] + lean_shift(int(pt[1]), lean), pt[1] + sink)
    head_m = K.mask_box(63 + sink, 86 + sink, 56 + lean, 74 + lean) & (c[..., 3] > 0)
    head = take(c, head_m)
    plate_m = K.mask_box(73 + sink, 80 + sink, 48 + lean, 51 + lean) & (c[..., 3] > 0)
    plate = take(c, plate_m)
    held = p["unit"] or p["hand"]
    if held:
        name, fist0 = held[0], held[1]
        reach = math.hypot(fist0[0] - SHOULDER[0], fist0[1] - SHOULDER[1])
        if reach > NEAR_REACH:
            raise SystemExit(f"the near fist {fist0} is {reach:.1f} from the shoulder (at most {NEAR_REACH})")
        fist = off(fist0)
        wrist_o = turned_offset(name, (WRIST[0] - GRIP[0], WRIST[1] - GRIP[1]))
        wrist = (fist[0] + wrist_o[0], fist[1] + wrist_o[1])
        layer = p["unit"][2] if p["unit"] else "front"
        if p["chain"] == "hang":
            R.hang_chain(c, (fist[0], fist[1] + 2.5), under=True)
        elif p["chain"] == "short":
            R.hang_chain(c, (fist[0], fist[1] + 2.5), under=True, length=6)
        # the near arm (where the fist left the shoulder): over the body, under the shoulder plate
        arm = draw_arm(c, off(SHOULDER), wrist, R.out)
        part = orient(R.unit if p["unit"] else R.hand, name)
        if layer == "behind":
            K.place(c, part, fist, under=True)
            K.put(c, arm, 0, 0)
            K.put(c, plate, 0, 0)
        else:
            K.put(c, arm, 0, 0)
            K.put(c, plate, 0, 0)
            K.place(c, part, fist)
            if layer == "front":
                K.put(c, head, 0, 0)
    if p["free"]:
        # the anchor alone: "behind" him (dropped beside him), or "front": planted before him over the body and the
        # legs, under the helmet (the far fist grips its shank, drawn after it)
        name, at = p["free"][0], p["free"][1]
        layer = p["free"][2] if len(p["free"]) > 2 else "behind"
        K.place(c, orient(R.anchor, name), off(at), under=layer == "behind")
        if layer == "front":
            K.put(c, head, 0, 0)
    if p["far"] is not None:
        # the far forearm and glove turned whole about the elbow (k quarter turns clockwise), slid `ext` rows down its
        # length (a punch reaching down: the gap under the shoulder plate filled with the suit's short stretch)
        k, ext = p["far"]
        el = off(FAR_ELBOW)
        fore = K.rot90(R.far_fore, k)
        if ext:
            seg = np.zeros_like(c)
            K.bone_arm(seg, (el[0], el[1] - 1), (el[0], el[1] + ext / 2), (el[0], el[1] + ext + 0.5), arm_mats(1.0),
                       width=(4.4, 4.4), outline=R.out)
            K.put(c, seg, 0, 0)
        K.place(c, fore, (el[0], el[1] + ext))
    if p["dim"]:
        for on, off_ in zip(EYES_ON, EYES_DIM):
            m = K.colour_mask(c, [hexrgb(on)]) & K.mask_box(70, 90, 50, 80)
            c[m] = (*hexrgb(off_), 255)
    dx, dy = p["move"]
    if dx or dy:
        c = K.shifted(c, dx, dy)
    c[P.D.soles + 1:] = 0
    return c


POSES = {
    # the anchor swung over (release frame 4, tick 13): drawn back low behind him, raised over his head, slammed down
    # before him (handed to the far fist, which grips the shank; the crown on the ground, the flukes up; the near fist
    # lets go), swung back over his shoulder, onto his back
    "attack": [DESIGN_POSE,
               pose(unit=("back", (47, 81), "behind"), lean=-1),
               pose(unit=("up", (48, 70), "behind")),
               pose(hand=("up", GRIP), free=("down", (85, 67.5), "front"), far=(3, 0), lean=1, sink=1, steps=(0, 2),
                    move=(2, 0)),
               pose(unit=("up", (48, 72), "behind"), lean=1, move=(1, 0)),
               dict(design=True, move=(1, 0))],
    # Q, the throw (release frame 5, tick 14): lifted, raised high, drawn back behind his head, swung over, thrown
    # (the anchor flies as the effect: the empty fist left high where it let go), held
    "skill": [pose(unit=("up", (50, 80), "front")),
              pose(unit=("up", (48, 70), "behind"), lean=-1),
              pose(unit=("back", (47, 70), "behind"), lean=-2, sink=1),
              pose(unit=("up", (51, 68), "behind"), move=(1, 0)),
              pose(hand=("up", (49, 69)), chain=None, lean=2, sink=1, steps=(0, 2), move=(1, 0)),
              pose(hand=("up", (49, 72)), chain=None, lean=1, sink=1, steps=(0, 2), move=(1, 0))],
    # Q, pulled in along the chain (played when the anchor hooks): leaning far forward, the anchor back in his fist on
    # landing, his stance again
    "skill_pull": [pose(hand=("fwd", (56, 70)), chain=None, lean=3, sink=1, steps=(-2, -1), move=(2, 0)),
                   pose(hand=("fwd", (56, 71)), chain=None, lean=3, sink=2, steps=(-2, -1), move=(2, 0)),
                   pose(unit=("up", (50, 79), "front"), sink=1, move=(1, 0)),
                   DESIGN_POSE],
    # W + E (release frame 3, tick 8): the far fist raised beside his helmet, slammed down onto the ground beside him in
    # a crouch (the riptide bursts), rising, his stance
    "skill2": [DESIGN_POSE,
               pose(unit=("up", GRIP, "front"), far=(2, -5), lean=-1),
               pose(unit=("up", GRIP, "front"), far=(0, 3), lean=2, sink=4, steps=(0, 1)),
               pose(unit=("up", GRIP, "front"), far=(0, 2), lean=1, sink=3, steps=(0, 1)),
               pose(unit=("up", GRIP, "front"), far=(0, 1), sink=1),
               DESIGN_POSE],
    # R (release frame 5, tick 16): lifted, raised high, drawn back behind him, swung over in a hop, slammed down before
    # him (the far fist on the shank, the crown driven into the ground), held, pulled up out of it, his stance
    "ult": [pose(unit=("up", (50, 80), "front")),
            pose(unit=("up", (48, 69), "behind")),
            pose(unit=("back", (47, 70), "behind"), lean=-2),
            pose(unit=("up", (51, 68), "behind"), move=(1, -3)),
            pose(hand=("up", GRIP), free=("down", (86, 65.5), "front"), far=(3, 0), lean=2, sink=2, steps=(0, 2),
                 move=(1, 0)),
            pose(hand=("up", GRIP), free=("down", (86, 65.5), "front"), far=(3, 0), lean=2, sink=2, steps=(0, 2),
                 move=(1, 0)),
            pose(hand=("up", GRIP), free=("down", (86, 61.5), "front"), far=(3, 0), lean=1, sink=1, move=(1, 0)),
            DESIGN_POSE],
    "hit": [dict(design=True, move=(-2, 0), lean=-1), dict(design=True, move=(-1, 0))],
    # the death: struck, the anchor slipping off his back and standing on its crown beside him, his fist letting go,
    # sinking down beside it, the eyes dimming
    "dead": [dict(design=True, move=(-2, 0), lean=-1),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", sink=1),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", lean=1, sink=2),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", lean=1, sink=3),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", lean=2, sink=4),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", lean=2, sink=5, dim=True),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", lean=2, sink=5, dim=True),
             pose(hand=("up", GRIP), free=("down_l", (46, 66)), chain="short", lean=2, sink=5, dim=True)],
}
MS = {"idle": [160] * 8, "run": [116] * 8, "attack": [70, 80, 60, 90, 80, 80], "skill": [60, 60, 60, 60, 80, 140],
      "skill_pull": [100, 120, 100, 80], "skill2": [70, 70, 100, 90, 90, 90],
      "ult": [60, 70, 60, 70, 100, 110, 90, 90], "hit": [100, 100],
      "dead": [100, 100, 120, 150, 200, 150, 200, 400]}
TAGS = list(MS)


# the run: the legs stride on League's run (RUN_JOINTS: tools/lol/pose_joints.py on poses.json's 8 run frames, the hip
# joint is League's "Thigh"): each leg League's thigh and shin angles on our short bones (RUN_LEG), a foot League has on
# the ground planted flat on the soles (rigkit.leg_chain solves the knee), thigh and shin drawn in the suit's three
# colours, the design's own knee guard on the knee and its own boot as the foot (moved whole, never turned); the body
# bobs with League's hips (0-2 rows), the far forearm swings a column with the near leg; the anchor stays on his back
RUN_JOINTS = os.path.join(ROOT, "assets", "source", "nautilus", "run_joints.json")
RUN_HIPS = {"near": 57.0, "far": 73.5}  # the hips' columns on HIP_ROW: near = League's R (nearer the camera)
RUN_LEG = (3.4, 3.2)                    # thigh and shin lengths (the hip row to the boots' top)
RUN_PLANT_TOE = 7.0                     # a League toe this low (game px under its pivot) stands on the ground
KNEE_BOXES = {"near": (89, 93, 53, 57), "far": (89, 93, 73, 77)}   # the knee guards (r0, r1, c0, c1)
BRONZE = ("#FAAC2A", "#DC741C", "#A84217", "#8C3815", "#6F2610", "#FDCC31")


def run_joints():
    with open(RUN_JOINTS, encoding="utf-8") as f:
        return json.load(f)


def top_mid(part):
    ys, xs = np.nonzero(part[..., 3] > 0)
    top = ys.min()
    row = xs[ys == top]
    return (row.min() + row.max() + 1) / 2.0, float(top)


def run_pieces(R):
    """The body without its legs (the hip band kept), the boots, the knee guards. Cached on R."""
    if getattr(R, "_run", None) is not None:
        return R._run
    a = R.bare
    legs = R.near_leg_m | R.far_leg_m
    rest = a.copy()
    rest[legs] = 0
    chain = np.zeros_like(a)
    chain[R.P.chain_m] = R.P.D.a[R.P.chain_m]
    hand = np.zeros_like(a)
    for m in (R.P.anchor_m, R.P.hand_m):
        hand[m] = R.P.D.a[m]
    boots, knees = {}, {}
    for leg, m in (("near", R.near_boot_m), ("far", R.far_boot_m)):
        b = take(a, m)
        tp = top_mid(b)
        boots[leg] = (b, tp, float(np.nonzero(b[..., 3].any(1))[0].max() + 1) - tp[1])
    bronze = K.colour_mask(a, [hexrgb(h) for h in BRONZE])
    for leg in ("near", "far"):
        r0, r1, c0, c1 = KNEE_BOXES[leg]
        kp = take(a, bronze & K.mask_box(r0, r1, c0, c1) & (R.near_leg_m | R.far_leg_m))
        ys, xs = np.nonzero(kp[..., 3] > 0)
        knees[leg] = K.Part.from_canvas(kp, kp[..., 3] > 0, ((xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2))
    R._run = dict(rest=rest, chain=chain, hand=hand, boots=boots, knees=knees)
    return R._run


def run_steps():
    """Per frame (near dx, near lift, far dx, far lift): each foot's way along the floor in League's run, centred on
    its own mean and scaled to RUN_STRIDE columns either way; a foot League has off the floor (its toe above
    RUN_PLANT_TOE) lifted a row per RUN_LIFT game px, at most two."""
    J = run_joints()
    out = {}
    for leg, side in (("near", "R"), ("far", "L")):
        xs = [f["joints"][f"{side}_Foot"][0] for f in J]
        mid, half = (max(xs) + min(xs)) / 2, max(1e-6, (max(xs) - min(xs)) / 2)
        toes = [f["joints"][f"{side}_Toe"][1] for f in J]
        top = max(toes)
        out[leg] = [(int(math.floor((x - mid) / half * RUN_STRIDE + 0.5)),
                     0 if t >= RUN_PLANT_TOE else min(2, int(math.floor((top - t) / RUN_LIFT + 0.5))))
                    for x, t in zip(xs, toes)]
    bobs = K.hip_bobs([(f["joints"]["L_Thigh"][1] + f["joints"]["R_Thigh"][1]) / 2 for f in J], 1)
    return [(out["near"][k][0], out["near"][k][1], out["far"][k][0], out["far"][k][1], bobs[k]) for k in range(len(J))]


RUN_STRIDE = 2                          # columns a foot moves either way of where it stands
RUN_LIFT = 3.0


def run_frame(R, k):
    """The legs (knee guard, shin, boot: the design's own pieces from under the hip band) stepping whole on League's
    run, both tucked under the hip band (a lifted leg's top goes behind it); the body bobbing a row; the far forearm
    swinging a column against the far leg; the anchor on his back, the near fist and the chain as in the design."""
    a = R.P.D.a
    nd, nl, fd, fl, bob = run_steps()[k]
    legs = R.near_leg_m | R.far_leg_m
    near, far = take(a, R.near_leg_m), take(a, R.far_leg_m)
    body = a.copy()
    body[legs] = 0
    chain = take(a, R.P.chain_m)
    body[R.P.chain_m] = 0
    fore = take(body, R.far_fore_m)
    body[R.far_fore_m] = 0
    swing = -1 if fd > 0 else (1 if fd < 0 else 0)
    c = np.zeros_like(a)
    K.put(c, K.shifted(far, fd, -fl), 0, 0)
    K.put(c, K.shifted(near, nd, -nl), 0, 0)
    K.put(c, K.shifted(body, 0, bob), 0, 0)
    K.put(c, K.shifted(fore, swing, bob), 0, 0)
    K.put(c, K.shifted(chain, 0, bob), 0, 0)
    c[R.P.D.soles + 1:] = 0
    return c


# the idle: the whole figure but the boots sinks 0 0 1 1 1 1 0 0 rows over them (the shins' tops go behind the hip band:
# knees bending), never a row cut through the helmet or the anchor (import_native's shared breath would)
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]


def idle_frame(R, n):
    a = R.P.D.a
    boots = R.near_boot_m | R.far_boot_m
    body = a.copy()
    body[boots] = 0
    c = np.zeros_like(a)
    K.put(c, take(a, boots), 0, 0)
    K.put(c, K.shifted(body, 0, n), 0, 0)
    c[R.P.D.soles + 1:] = 0
    return c


def frames(R, tag):
    if tag == "idle":
        out = [idle_frame(R, n) for n in BREATH]
    elif tag == "run":
        out = [run_frame(R, k) for k in range(8)]
    else:
        out = [compose(R, p) for p in POSES[tag]]
    keep = K.mask_box(63, 86, 56, 74)
    return [K.finish(c, R.P.D.outline, R.P.D.soles, keep=keep & (c[..., 3] > 0)) for c in out]


def parts_review(P, path):
    a = P.D.a
    tint = a.copy()
    for m, c in ((P.anchor_m, (0, 255, 170)), (P.hand_m, (255, 60, 60)), (P.chain_m, (255, 150, 0)),
                 (P.far_m, (170, 0, 255)), (P.far_glove_m, (255, 0, 255)), (P.near_leg_m, (0, 120, 255)),
                 (P.far_leg_m, (0, 200, 255))):
        tint[m, :3] = (tint[m, :3] * 0.35 + np.array(c) * 0.65).astype(np.uint8)
    tiles = [("design", a), ("parts", tint), ("unit", P.unit_canvas), ("bare", P.bare)]
    x0, x1, y0, y1 = 38, 86, 48, 102
    z = 10
    W, H = (x1 - x0) * z, (y1 - y0) * z
    img = Image.new("RGB", (len(tiles) * (W + 8), H + 22), (40, 40, 40))
    d = ImageDraw.Draw(img)
    for i, (nm, t) in enumerate(tiles):
        tile = Image.new("RGBA", (W, H), (150, 160, 150, 255))
        tile.alpha_composite(Image.fromarray(t[y0:y1, x0:x1]).resize((W, H), Image.NEAREST))
        g = ImageDraw.Draw(tile)
        for x in range(x0, x1):
            if x % 5 == 0:
                g.line([((x - x0) * z, 0), ((x - x0) * z, H)], fill=(255, 255, 255, 90))
        for y in range(y0, y1):
            if y % 5 == 0:
                g.line([(0, (y - y0) * z), (W, (y - y0) * z)], fill=(255, 255, 255, 90))
        img.paste(tile.convert("RGB"), (i * (W + 8), 20))
        d.text((i * (W + 8) + 4, 4), nm, fill=(255, 255, 255))
    img.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", help="write the parts review to this folder")
    ap.add_argument("--review", help="write review sheets to this folder")
    ap.add_argument("--tags", help="comma-separated tags")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    P = Parts()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        parts_review(P, os.path.join(a.parts, "nautilus_parts.png"))
        print("anchor", int(P.anchor_m.sum()), "hand", int(P.hand_m.sum()), "chain", int(P.chain_m.sum()),
              "far", int(P.far_m.sum()), "legs", int(P.near_leg_m.sum()), int(P.far_leg_m.sum()))
        return
    R = Rig(P)
    tags = a.tags.split(",") if a.tags else TAGS
    built = {t: frames(R, t) for t in tags}
    for t in tags:
        rows = K.audit(built[t], P.D.a, P.D.outline, P.D.soles)
        print(f"{t:10s}", " ".join(f"[{r['pieces']}p {r['holes']}h {r['orphans']}o {r['area']}]" for r in rows))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        for t in tags:
            K.review_sheet([(t, [P.D.a] + built[t])], os.path.join(a.review, f"rig_{t}.png"), z=5, soles=P.D.soles)
        return
    bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differ:", bad or "none")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
