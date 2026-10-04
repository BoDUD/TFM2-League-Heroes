#!/usr/bin/env python3
"""Ryze's second design posed for every action after the first design's strips (2026-10-03).

    python tools/art/rig_ryze.py --cells assets/source/native/ryze_cells.json --out assets/source/native
    python tools/art/rig_ryze.py --cells ... --out ... --check            # compare with the files in --out
    python tools/art/rig_ryze.py --cells ... --out DIR --review DIR --v1 <the first design's assets/source/native>

The first design's strips (Codex's raw drawings re-read by fix_ryze_strips.py) carry its bulk: arms 6 squares thick,
one block of trousers. Here every frame is put together from the second design's own parts
(assets/source/ryze/design_v2, tools/art/design_ryze_v2.py), as Caitlyn's second design is (tools/art/rig_caitlyn.py):
- the upper body as drawn: the head (the first design's), the scroll, the beard, the vest, the shoulder pads, the belt
  and the teal flap - without the arms (UPPER);
- the arms drawn from the shoulder through the elbow to the hand, three squares thick: the bare blue-violet arm lit
  on its outer side, the brown and gold bracer, the open hand (ARM, HAND);
- the legs drawn as pixel art row by row (column by column where a bone lies flat): the navy trousers, the gold-trimmed
  boot cuff at the knee, the brown boot and its foot (THIGH, CUFF, SHIN, FOOT);
- in the idle frames the design itself, square for square;
- turned poses (the falls) RotSprite the upper body about the hips (tools/art/rig_nocturne.py) and lay it on the
  ground.
The poses follow the first design's strips (assets/source/native/ryze_<tag>.png on main before this design), frame
for frame on the cells table's standing points, so the kit's hit ticks stay.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))

DESIGN = os.path.join(ROOT, "assets", "source", "ryze", "design_v2", "ryze_design_v2_1x.png")
PIVOT = (64, 88)
Z = 8

PAL = {
    "a": "0F0213", "b": "10041C", "c": "494560", "d": "6B44CC", "e": "A88CFB", "f": "C8B5FD", "g": "511AC4",
    "h": "9B592D", "i": "9270F2", "j": "51261D", "k": "C4A68D", "l": "141743", "m": "B59CFC", "n": "F4EEEA",
    "o": "18235D", "p": "23148D", "q": "663322", "r": "321721", "s": "FBFBFD", "t": "B368FD", "u": "431F20",
    "v": "40CCFC", "w": "233D98", "x": "E79845", "y": "FBCE84", "z": "112A70", "A": "097999", "B": "329498",
    "C": "014C78", "D": "7F4226",
}
RING = "a"
SKIN = set("defgim")
TEAL = set("ABC")


def rgba(ch):
    h = PAL[ch]
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255], np.uint8)


CODE = {tuple(int(PAL[k][i:i + 2], 16) for i in (0, 2, 4)): k for k in PAL}


def lp(p):
    p = os.path.abspath(p)
    pre = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(pre) else pre + p


# ---------------------------------------------------------------------------------------------------------------
# the design's parts, squares relative to the standing point

def design():
    return np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))


def code(c):
    return CODE.get(tuple(int(v) for v in c[:3]), "?")


def upper_part(d):
    """The upper body without the arms: everything over the shoulder pads; the pads' rows without the skin of the
    arms' tops; under them the torso's columns only; the teal flap and its outline under the belt."""
    out = {}
    for y in range(-30, 2):
        for x in range(-16, 12):
            c = d[PIVOT[1] + y, PIVOT[0] + x]
            if not c[3]:
                continue
            ch = code(c)
            if y <= -16:
                keep = True
            elif y <= -14:
                keep = -10 <= x <= 6 and ch not in SKIN
            elif y <= -4:
                keep = -5 <= x <= 4 and ch not in SKIN
            else:
                keep = -2 <= x <= 3 and (ch in TEAL or (ch == RING and teal_next(d, x, y)))
            if keep and (x, y) not in SEAMS:
                out[(x, y)] = c.copy()
    return out


# the seams the design fills between its hanging arms and the coat (design_ryze_v2.WINDOW) belong to the hanging arms:
# an arm moved away leaves the coat's own outline
from design_ryze_v2 import WINDOW as SEAMS  # noqa: E402


def teal_next(d, x, y):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if code(d[PIVOT[1] + y + dy, PIVOT[0] + x + dx]) in TEAL:
            return True
    return False


# the legs as drawn, from the hip (row -3, under the belt) to the sole (row 11): the far leg's columns -7..-2 (not
# its hand's, by it over row 1), the near leg's 1..7 (not its hand's over row 2), the teal flap left to the body
LEG_ROWS = (-3, 11)
FOOT_X = {"back": -4.5, "front": 4.0}           # the design's feet


def leg_parts(d):
    legs = {"back": {}, "front": {}}
    for y in range(LEG_ROWS[0], LEG_ROWS[1] + 1):
        for x in range(-8, 9):
            c = d[PIVOT[1] + y, PIVOT[0] + x]
            if not c[3] or code(c) in TEAL:
                continue
            if -7 <= x <= -2 and not (y <= 0 and x <= -7):
                legs["back"][(x, y)] = c.copy()
            elif 1 <= x <= 7 and not (y <= 1 and x >= 6):
                legs["front"][(x, y)] = c.copy()
    return legs


# the arms as drawn, cut in two at the elbow (the bracer's top): the upper arm from under the shoulder pad, the
# forearm with the bracer and the open hand; joints: the shoulder (S), the elbow (E), the hand's middle (H)
ARMS = {
    "back": {"S": (-7.0, -14.0), "E": (-8.0, -6.5), "H": (-8.5, -1.0),
             "upper": lambda x, y: -11 <= x <= -5 and -14 <= y <= -7,
             "fore": lambda x, y: -12 <= x <= -6 and -6 <= y <= 1},
    "front": {"S": (6.0, -13.5), "E": (6.5, -6.5), "H": (8.0, -1.0),
              "upper": lambda x, y: (5 <= x <= 8 and -13 <= y <= -7) or (x == 4 and -10 <= y <= -7),
              "fore": lambda x, y: (5 <= x <= 10 and -6 <= y <= 1) or (x == 4 and -6 <= y <= -3)},
}
ARM_KEEP = set("abdefgimhjqxyu")                # skin, outline, the bracer's leathers and golds


def arm_parts(d):
    out = {}
    for side, spec in ARMS.items():
        for seg in ("upper", "fore"):
            cells = {}
            for y in range(-16, 3):
                for x in range(-13, 12):
                    c = d[PIVOT[1] + y, PIVOT[0] + x]
                    if c[3] and spec[seg](x, y) and code(c) in ARM_KEEP:
                        cells[(x, y)] = c.copy()
            out[(side, seg)] = cells
    return out


# the hips where the idle's hands hang over them: the design shows the trousers one or two squares wide there between
# the teal flap and the hands' outlines (a double outline down each side); with the hands raised the hips pinched in
# under the belt and the legs looked cut off from the body (the user: 「还有腿部和身体分离」). The trousers drawn whole
# from the belt to the thighs, as wide as the legs under them (rows -4..1, (x, y) from the standing point)
HIP_FILL = {                            # = design_ryze_v2.HIPS since it draws the hips (its step 5)
    (-6, -4): "a", (-5, -4): "z", (-4, -4): "o", (-3, -4): "w", (-2, -4): "o", (4, -4): "w", (5, -4): "a",
    (-6, -3): "a", (-5, -3): "w", (-4, -3): "o", (-3, -3): "o", (3, -3): "z", (4, -3): "w", (5, -3): "o", (6, -3): "a",
    (-6, -2): "a", (-5, -2): "w", (-4, -2): "o", (-3, -2): "z", (4, -2): "o", (5, -2): "w", (6, -2): "a",
    (-6, -1): "a", (-5, -1): "w", (-4, -1): "o", (-3, -1): "w", (4, -1): "w", (5, -1): "z", (6, -1): "a",
    (-6, 0): "a", (-5, 0): "w", (-4, 0): "o", (-3, 0): "z", (4, 0): "w", (5, 0): "z", (6, 0): "a",
    (-6, 1): "a", (-5, 1): "w", (-4, 1): "w", (5, 1): "a",
}


def hips_filled(legs):
    """The legs with HIP_FILL over their top rows and nothing of the hands' outlines beside the hips."""
    out = {"back": {}, "front": {}}
    for side in ("back", "front"):
        for (x, y), c in legs[side].items():
            if -4 <= y <= 1 and not -6 <= x <= 6:
                continue
            out[side][(x, y)] = c
    for (x, y), ch in HIP_FILL.items():
        out["back" if x <= 0 else "front"][(x, y)] = rgba(ch)
    return out


def parts(d):
    full = {}
    for y in range(-31, 13):
        for x in range(-18, 14):
            c = d[PIVOT[1] + y, PIVOT[0] + x]
            if c[3]:
                full[(x, y)] = c.copy()
    return {"upper": upper_part(d), "full": full, "legs": hips_filled(leg_parts(d)), "arms": arm_parts(d)}


def turn_cells(cells, joint, deg):
    """A part's squares turned about its joint (RotSprite, + counter-clockwise on screen; exact for 0): the squares
    relative to the joint."""
    import rig_nocturne as RN
    if not cells:
        return {}
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    x0, y0 = min(xs), min(ys)
    a = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
    for (x, y), c in cells.items():
        a[y - y0, x - x0] = c
    j = (joint[0] - x0, joint[1] - y0)
    if abs(deg) < 0.5:
        return {(x - joint[0], y - joint[1]): c for (x, y), c in cells.items()}
    r, (jx, jy) = RN.rotsprite(a, j, deg)
    return {(xx - jx, yy - jy): r[yy, xx].copy() for yy, xx in zip(*np.nonzero(r[..., 3]))}


def angle(v):
    return math.degrees(math.atan2(v[1], v[0]))


# the arm drawn as pixel art after the design's arms, row by row along a steep bone (column by column along a flat
# one), each step one string of colours across the limb from its lit outer side to the inner side: the dark shoulder
# cap and the bare upper arm (three squares), the bracer (four: gold bands round the brown leather), the hand (three,
# then two); one outline round the whole arm
# each arm's rows as the design draws them (outer side first: the far arm's left, the near arm's right): the upper arm
# dark under the shoulder pad and lit along its outer edge, the bracer's leathers and gold, the hand
# (the upper arm wide at the shoulder and narrowing to the elbow; the hands as design_ryze_v2.py's HANDS redraws them:
# three squares, lit outside, the fingertips a square lower)
ARM_TEX = {
    "back": {"upper": ["ddd", "fedd", "feid", "feid", "fei", "fei", "fei"],
             "fore": ["hqxx", "jhjj", "qhjj", "hxj"], "hand": ["fei", "eid", "idg", "g"]},
    "front": {"upper": ["ddd", "fedd", "feid", "feid", "fei", "fei", "fei"],
              "fore": ["uhxh", "jhjj", "jhjq", "uhx"], "hand": ["fei", "eid", "idg", "g"]},
}


def run_mats(n, mats, keep_end=True):
    """n strings from mats: a longer run repeats the middle string, a shorter one drops from the middle."""
    if n <= 0:
        return []
    if n >= len(mats):
        mid = len(mats) // 2
        return mats[:mid] + [mats[mid]] * (n - len(mats) + 1) + mats[mid + 1:]
    keep = list(mats)
    while len(keep) > n:
        keep.pop(len(keep) // 2)
    return keep


def limb(a, b, mats, outer_x, cells, first=True):
    """The bone a -> b drawn step by step (rows if steep, else columns), each step's string centred on the line, its
    first character on the lit outer side: on a steep bone the screen-left side (outer_x -1) or right (+1), on a flat
    one the top (the light comes from above); first: draw the step at a too."""
    if steep(a, b):
        s = 1 if b[1] >= a[1] else -1
        y0, y1 = int(math.floor(a[1] + 0.5)), int(math.floor(b[1] + 0.5))
        steps = span(y0 if first else y0 + s, y1)
        ms = run_mats(len(steps), mats)
        for i, y in enumerate(steps):
            t = (y - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 1.0
            x = a[0] + (b[0] - a[0]) * min(1.0, max(0.0, t))
            m = ms[i] if outer_x < 0 else ms[i][::-1]
            c0 = int(math.floor(x - len(m) / 2 + 0.5))
            for j, ch in enumerate(m):
                cells[(c0 + j, y)] = rgba(ch)
    else:
        s = 1 if b[0] >= a[0] else -1
        x0, x1 = int(math.floor(a[0] + 0.5)), int(math.floor(b[0] + 0.5))
        steps = span(x0 if first else x0 + s, x1)
        ms = run_mats(len(steps), mats)
        for i, x in enumerate(steps):
            t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 1.0
            y = a[1] + (b[1] - a[1]) * min(1.0, max(0.0, t))
            m = ms[i]
            r0 = int(math.floor(y - len(m) / 2 + 0.5))
            for j, ch in enumerate(m):
                cells[(x, r0 + j)] = rgba(ch)


# the leg drawn the same way after the design's legs: the navy trousers (three squares) down to the gold band at the
# knee, the boot's cuff (four), the boot (two), the foot forward under a standing shin or hanging under a raised one
THIGH_MATS = ["ozw", "ozw", "ozw", "wwo", "wwz", "xxo"]
SHIN_MATS = ["hhhj", "jxjj", "jj", "hj", "hj", "xj"]


def pixel_leg(hip, knee_pt, ankle, toe=1):
    cells = {}
    limb(hip, knee_pt, THIGH_MATS, -1, cells)
    limb(knee_pt, ankle, SHIN_MATS, -1, cells, first=False)
    ax, ay = int(math.floor(ankle[0] + 0.5)), int(math.floor(ankle[1] + 0.5))
    if steep(knee_pt, ankle) and ankle[1] > knee_pt[1]:
        foot = "jDhj" if toe > 0 else "jhDj"
        x0 = ax - 1 if toe > 0 else ax - 2
        for j, ch in enumerate(foot):
            cells[(x0 + j, ay + 1)] = rgba(ch)
    else:                                   # a raised foot hangs under the ankle
        for (dx, dy), ch in (((0, 1), "j"), ((1, 1), "D"), ((0, 2), "h"), ((1, 2), "j")):
            cells[(ax + dx, ay + dy)] = rgba(ch)
    return cells


# ---------------------------------------------------------------------------------------------------------------
# poses from League's own clips: tools/lol/pose_joints.py measured Ryze's joints at game size frame by frame
# (assets/source/ryze/poses_v2.json: the cells' clip times, head 2.2, legs 0.85, 41 px) into lol_joints_v2.json;
# League's left side is the near one (front), the right the far one (back)
LOL = os.path.join(ROOT, "assets", "source", "ryze", "lol_joints_v2.json")
S_LEG, S_ARM = 0.855, 0.88
STAND_ANKLE = 9.0
SIDE = {"front": "L", "back": "R"}


def lol_table():
    with open(lp(LOL), encoding="utf-8") as f:
        return json.load(f)


def lol_pose(tag, k, table=None, ref=None, keep_x=0.8, **extra):
    """The pose of League's frame k of tag: the hips moved by League's pelvis (keep_x of it sideways), the upper body
    leaning as League's spine leans, each foot and knee where League has them from its hip (scaled to these legs), each
    hand where League has it from its shoulder (scaled to these arms), the elbow on League's side; the lowest ankle on
    the ground unless League's frame is in the air."""
    table = table or lol_table()
    D = table["idle"][0]["joints"]
    J = table[tag][k]["joints"]
    air = table[tag][k].get("air", 0)
    ref = ref or D["Pelvis"]
    bx = (J["Pelvis"][0] - ref[0]) * keep_x
    lean = ((J["Neck"][0] - J["Pelvis"][0]) - (D["Neck"][0] - D["Pelvis"][0])) / (D["Pelvis"][1] - D["Neck"][1])
    legs = {}
    lowest = -99.0
    for side in ("back", "front"):
        s = SIDE[side]
        hip = (HIPS[side] + bx, HIP_Y)
        kn = (hip[0] + (J[s + "_KneeLower"][0] - J[s + "_Hip"][0]) * S_LEG,
              hip[1] + (J[s + "_KneeLower"][1] - J[s + "_Hip"][1]) * S_LEG)
        an = (hip[0] + (J[s + "_Foot"][0] - J[s + "_Hip"][0]) * S_LEG,
              hip[1] + (J[s + "_Foot"][1] - J[s + "_Hip"][1]) * S_LEG)
        legs[side] = [kn, an]
        lowest = max(lowest, an[1])
    by = STAND_ANKLE - air - lowest
    for side in legs:
        kn, an = legs[side]
        legs[side] = {"knee": (kn[0], kn[1] + by), "ankle": (an[0], an[1] + by)}
    pose = {"body": (bx, by), "lean": lean, "legs": legs}
    for side in ("back", "front"):
        s = SIDE[side]
        S = (ARMS[side]["S"][0] + bx + lean_x(lean, ARMS[side]["S"][1]), ARMS[side]["S"][1] + by)
        hand = (S[0] + (J[s + "_Hand"][0] - J[s + "_Shoulder"][0]) * S_ARM,
                S[1] + (J[s + "_Hand"][1] - J[s + "_Shoulder"][1]) * S_ARM)
        el = (S[0] + (J[s + "_Elbow"][0] - J[s + "_Shoulder"][0]) * S_ARM,
              S[1] + (J[s + "_Elbow"][1] - J[s + "_Shoulder"][1]) * S_ARM)
        # the elbow on League's side of the shoulder -> hand line
        cross = (hand[0] - S[0]) * (el[1] - S[1]) - (hand[1] - S[1]) * (el[0] - S[0])
        best = None
        for d in (-1, 1):
            e = knee(S, hand, 6.5, 7.0, forward=d)
            c2 = (hand[0] - S[0]) * (e[1] - S[1]) - (hand[1] - S[1]) * (e[0] - S[0])
            score = (c2 * cross > 0, -math.hypot(e[0] - el[0], e[1] - el[1]))
            if best is None or score > best[0]:
                best = (score, d)
        pose[side] = hand
        pose[side + "_elbow"] = best[1]
        if J[s + "_Hand"][2] > J["Spine2"][2] + 6 and side == "back":
            pose["back_z"] = "front"            # the far hand swung in front of the body
    pose.update(extra)
    return pose


# the hands drawn square by square (interior squares, the ring adds the outline; W = the wrist square, one step past
# the bracer's end), the near hand's: opened toward the target with the fingers up (open: r the forearm level, ur
# raised halfway, u upright), closed (fist), or hanging as the design draws it (relaxed: d, the hand of
# design_ryze_v2.HANDS; a relaxed hand on a forearm that is level or raised is the fist); a forearm pointing left
# takes them mirrored. The user on the hand laid along the bone as three squares narrowing to one (a claw at the
# end of a straight arm): 「太僵硬了手臂」 - the first design's strips and oppi's Brand cast with a big open palm at the
# end of a bent arm
FIST = {"r": [".ffe", "Weei", ".idd"], "ur": [".fe", "fei", "Wid"], "u": ["ffe", "fei", "eid", ".W."]}
HANGING = ["iWf", "die", "gdi", ".g."]
HAND_DRAWN = {
    # the open hand a solid palm, the fingers up, lit along the top (gaps between the fingers read as a fork at game
    # size: 「手还是有点怪」)
    "open": {"r": [".ff.", "ffee", "feei", "Weid", ".dd."],
             "ur": ["..ff", ".ffe", "ffei", "Weid", ".d.."],
             "u": [".ff.", "ffee", "feei", "eeid", ".W.."], "d": HANGING},
    "fist": dict(FIST, d=HANGING),
    "relaxed": dict(FIST, d=HANGING),
}


def drawn_hand(kind, wrist, f):
    """The drawn hand `kind` at the wrist of a forearm pointing along f."""
    fl = math.hypot(f[0], f[1]) or 1e-9
    th = math.degrees(math.atan2(-f[1], f[0]))          # up positive
    mirror = abs(th) > 90
    if mirror:
        th = 180 - th if th > 0 else -180 - th
    rows = HAND_DRAWN[kind]["d" if th < -45 else "r" if th <= 30 else "ur" if th <= 65 else "u"]
    wy = next(i for i, r in enumerate(rows) if "W" in r)
    wx = rows[wy].index("W")
    x0, y0 = int(round(wrist[0] + f[0] / fl)), int(round(wrist[1] + f[1] / fl))
    cells = {}
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch != ".":
                cells[(x0 + (x - wx) * (-1 if mirror else 1), y0 + y - wy)] = rgba("e" if ch == "W" else ch)
    return cells


REACH = 0.93                                  # the farthest a hand gets from its shoulder (of the arm's length): the
                                              # elbow bent at least ~135 degrees


def pixel_arm(shoulder, hand, elbow_dir, outer, kind=None):
    """The arm from the shoulder through the elbow (two-bone reach, the elbow toward elbow_dir) to the hand's middle,
    its rows the design's own (ARM_TEX: the far arm when outer is -1, the near arm when +1): the upper arm, the
    forearm's bracer and the hand on the forearm's line."""
    tex = ARM_TEX["back" if outer < 0 else "front"]
    lu, lf, lh = 6.6, 4.3, 2.4                  # the design's arm: shoulder to the hand's middle 13.1
    dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
    reach = math.hypot(dx, dy) or 1e-9
    full = (lu + lf + lh) * REACH          # never stretched straight: an arm at full length reads as a rod
    if reach > full:
        hand = (shoulder[0] + dx * full / reach, shoulder[1] + dy * full / reach)
    # of the two ways the arm can bend, the elbow that hangs lower and points back (elbow_dir -1) or forward (+1)
    mx, my = (shoulder[0] + hand[0]) / 2, (shoulder[1] + hand[1]) / 2
    e = max((knee(shoulder, hand, lu, lf + lh, forward=d) for d in (-1, 1)),
            key=lambda q: (q[0] - mx) * 0.6 * elbow_dir + (q[1] - my))
    fx, fy = hand[0] - e[0], hand[1] - e[1]
    fl = math.hypot(fx, fy) or 1e-9
    w = (e[0] + fx * lf / fl, e[1] + fy * lf / fl)      # the wrist: the bracer's end
    cells = {}
    limb(shoulder, e, tex["upper"], outer, cells)
    limb(e, w, tex["fore"], outer, cells, first=False)
    cells.update(drawn_hand(kind or "relaxed", w, (fx, fy)))
    return cells


def design_arm(P, side, shoulder, hand, elbow_dir):
    """The arm as drawn, posed: the upper arm turned about the shoulder toward the elbow, the forearm about the elbow
    toward the hand (two-bone reach, the elbow bent toward elbow_dir: -1 left of the shoulder->hand line on screen,
    +1 right); a hand out of reach stops at the arm's length."""
    sp = ARMS[side]
    S0, E0, H0 = sp["S"], sp["E"], sp["H"]
    lu = math.hypot(E0[0] - S0[0], E0[1] - S0[1])
    lf = math.hypot(H0[0] - E0[0], H0[1] - E0[1])
    dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
    reach = math.hypot(dx, dy) or 1e-9
    if reach > lu + lf - 0.05:
        k = (lu + lf - 0.05) / reach
        hand = (shoulder[0] + dx * k, shoulder[1] + dy * k)
    e = knee(shoulder, hand, lu, lf, forward=elbow_dir)
    d1 = angle((E0[0] - S0[0], E0[1] - S0[1])) - angle((e[0] - shoulder[0], e[1] - shoulder[1]))
    d2 = angle((H0[0] - E0[0], H0[1] - E0[1])) - angle((hand[0] - e[0], hand[1] - e[1]))
    up = turn_cells(P["arms"][(side, "upper")], S0, d1)
    fo = turn_cells(P["arms"][(side, "fore")], E0, d2)
    cells = {}
    for (x, y), c in up.items():
        cells[(int(round(shoulder[0] + x)), int(round(shoulder[1] + y)))] = c
    for (x, y), c in fo.items():
        cells[(int(round(e[0] + x)), int(round(e[1] + y)))] = c
    return cells


DROP_ORDER = [2, 7, 5, 0, 8, 1, 6, -1, 9, -2]   # the rows a shorter leg loses first (never the cuff's top or the foot)


def design_leg(part, hip_dx, hip_dy, foot_dx, lift, kick=0):
    """The leg as drawn, its top moved with the hips, its sole on the ground lift rows up: hip_dy + lift rows taken
    out (DROP_ORDER), the rows shifted along the line from the hip to the foot (foot_dx: the foot's move from the
    design's), the boot (rows from the cuff down) kick more squares back (a lifted foot folds behind the knee)."""
    rows = list(range(LEG_ROWS[0], LEG_ROWS[1] + 1))
    drop = set(DROP_ORDER[:max(0, min(len(DROP_ORDER), hip_dy + lift))])
    kept = [r for r in rows if r not in drop]
    n = len(kept)
    out = {}
    for i, r in enumerate(kept):
        ny = LEG_ROWS[0] + hip_dy + i
        t = i / (n - 1)
        sx = hip_dx + (foot_dx - hip_dx) * t - (kick * min(1.0, max(0.0, (r - 3) / 6.0)))
        for (x, y), c in part.items():
            if y == r:
                out[(x + int(round(sx)), ny)] = c
    return out


# ---------------------------------------------------------------------------------------------------------------
# limbs drawn along a line

def seg(p, a, b):
    """(distance, t along a -> b, side: + right of the direction) of point p to segment a -> b."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    n = math.hypot(vx, vy) or 1e-9
    ux, uy = vx / n, vy / n
    t = max(0.0, min(n, (p[0] - ax) * ux + (p[1] - ay) * uy))
    qx, qy = ax + ux * t, ay + uy * t
    side = (p[0] - qx) * uy - (p[1] - qy) * ux
    return math.hypot(p[0] - qx, p[1] - qy), t, side


def chain(points, half, colour):
    """Squares within half(t) of the polyline; colour(t, side) -> rgba. t runs along the whole polyline."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    lens = [math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1]) for i in range(len(points) - 1)]
    out = {}
    for y in range(int(math.floor(min(ys))) - 3, int(math.ceil(max(ys))) + 4):
        for x in range(int(math.floor(min(xs))) - 3, int(math.ceil(max(xs))) + 4):
            best = None
            acc = 0.0
            for i in range(len(points) - 1):
                dist, t, side = seg((x, y), points[i], points[i + 1])
                if best is None or dist < best[0] - 1e-9:
                    best = (dist, acc + t, side)
                acc += lens[i]
            if best[0] <= half(best[1]):
                out[(x, y)] = colour(best[1], best[2])
    return out


def ring(cells):
    r = set()
    for x, y in cells:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in cells:
                r.add(q)
    return r


def knee(hip, ankle, lt, ls, forward=1):
    hx, hy = hip
    ax, ay = ankle
    dx, dy = ax - hx, ay - hy
    dist = math.hypot(dx, dy)
    if dist >= lt + ls - 1e-6:
        return hx + dx * lt / (lt + ls), hy + dy * lt / (lt + ls)
    a = (lt * lt - ls * ls + dist * dist) / (2 * dist)
    h = math.sqrt(max(0.0, lt * lt - a * a))
    mx, my = hx + dx * a / dist, hy + dy * a / dist
    nx, ny = -dy / dist, dx / dist
    if nx * forward < 0:
        nx, ny = -nx, -ny
    return mx + nx * h, my + ny * h


# the arm from the shoulder, after the design's arms: (length along the arm, half width, the colours across it from
# the lit outer side to the inner side): the shoulder's dark top, the bare upper arm (three squares), the bracer (four:
# a gold band, the brown leather, a gold band), the wrist
ARM = [(1.5, 1.5, "dde"), (5.0, 1.45, "fei"), (0.8, 1.85, "xxhj"), (2.4, 1.85, "hhjq"), (0.8, 1.85, "xxhj"),
       (1.0, 1.4, "fei")]
ARM_UP, ARM_LOW = 6.5, 5.0                     # shoulder -> elbow, elbow -> the wrist (the hand beyond it)
HAND_R = 1.45


def arm(shoulder, hand, elbow_dir=-1, outer=-1):
    """The arm's squares from the shoulder to the wrist and the open hand round `hand`; the elbow bends toward
    elbow_dir (-1 left of the shoulder->hand line on screen, +1 right); outer: the lit side (-1 left, +1 right of the
    arm going from the shoulder)."""
    dx, dy = hand[0] - shoulder[0], hand[1] - shoulder[1]
    reach = math.hypot(dx, dy) or 1e-9
    full = ARM_UP + ARM_LOW + HAND_R
    if reach > full:                            # never a stretched stick: the hand stops at the arm's reach
        hand = (shoulder[0] + dx * full / reach, shoulder[1] + dy * full / reach)
        dx, dy, reach = hand[0] - shoulder[0], hand[1] - shoulder[1], full
    wrist = (hand[0] - dx / reach * HAND_R, hand[1] - dy / reach * HAND_R)
    e = knee(shoulder, wrist, ARM_UP, ARM_LOW, forward=elbow_dir)

    def seg_at(t):
        acc = 0.0
        for n, half, cs in ARM:
            if t <= acc + n:
                return half, cs
            acc += n
        return ARM[-1][1], ARM[-1][2]

    def colour(t, side):
        half, cs = seg_at(t)
        u = side * outer                        # + on the lit outer side
        i = int((half - u) / (2 * half) * len(cs))
        return rgba(cs[min(len(cs) - 1, max(0, i))])
    cells = chain([shoulder, e, wrist], lambda t: seg_at(t)[0], colour)
    hx, hy = hand
    for y in range(int(math.floor(hy - 3)), int(math.ceil(hy + 3)) + 1):
        for x in range(int(math.floor(hx - 3)), int(math.ceil(hx + 3)) + 1):
            if math.hypot(x - hx, y - hy) <= HAND_R:
                lit = (x - hx) * outer + (hy - y) * 0.6
                cells[(x, y)] = rgba("f" if lit > 0.7 else ("e" if lit > -0.7 else "i"))
    return cells


# the leg: rows of its materials from the hip down, one string per row (left to right), the bands kept whole when a
# bone is drawn shorter or longer (the trousers' middle row repeats or drops first)
HIP_Y, KNEE_Y, ANKLE_Y = -3.0, 3.0, 9.0
LT, LS = KNEE_Y - HIP_Y, ANKLE_Y - KNEE_Y
THIGH = ["ozw", "ozw", "wzo", "ozw", "ozw", "xxo"]      # the trousers, the cuff's gold band under the knee
CUFF = ["hhhj", "jxjj"]                                   # the boot's cuff
SHIN = ["jj", "hj", "hj", "xj"]
FOOT = ["jDhj"]                                            # the foot's row, the toe forward (right)


def bands(n, rows, repeat):
    if n <= 0:
        return []
    if n >= len(rows):
        out = list(rows)
        while len(out) < n:
            out.insert(repeat, rows[repeat])
        return out
    keep = list(rows)
    while len(keep) > n:
        keep.pop(repeat if repeat < len(keep) - 1 else 0)
    return keep


def by_rows(a, b, rows, mats, out):
    for i, y in enumerate(rows):
        t = (y - a[1]) / (b[1] - a[1]) if b[1] != a[1] else 1.0
        x = a[0] + (b[0] - a[0]) * min(1.0, max(0.0, t))
        m = mats[i]
        c0 = int(math.floor(x - len(m) / 2 + 0.5))
        for j, ch in enumerate(m):
            out[(c0 + j, y)] = rgba(ch)


def by_cols(a, b, cols, mats, out):
    for i, x in enumerate(cols):
        t = (x - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 1.0
        y = a[1] + (b[1] - a[1]) * min(1.0, max(0.0, t))
        m = mats[i]
        r0 = int(math.floor(y - len(m) / 2 + 0.5))
        for j, ch in enumerate(m):
            out[(x, r0 + j)] = rgba(ch)


def span(p0, p1):
    s = 1 if p1 >= p0 else -1
    return list(range(p0, p1 + s, s))


def steep(a, b):
    return abs(b[1] - a[1]) >= abs(b[0] - a[0])


def leg(hip, ankle, kneel=None, out_dir=1, toe=1):
    """One leg as pixel art: the thigh hip -> knee in the trousers, the cuff and the boot knee -> ankle, the foot
    toe forward (toe +1 right, -1 left) under a standing shin."""
    k = kneel if kneel is not None else knee(hip, ankle, LT, LS, forward=out_dir)
    cells = {}
    kr = int(math.floor(k[1] + 0.5))
    if steep(hip, k):
        rows = span(int(math.floor(hip[1])) + 1, kr)
        by_rows(hip, k, rows, bands(len(rows), THIGH, 2), cells)
    else:
        cols = span(int(math.floor(hip[0] + 0.5)), int(math.floor(k[0] + 0.5)))
        by_cols(hip, k, cols, [m[:3] for m in bands(len(cols), THIGH, 2)], cells)
    sh = CUFF + SHIN
    if steep(k, ankle):
        ar = int(math.floor(ankle[1] + 0.5))
        rows = span(kr + 1, ar)
        by_rows(k, ankle, rows, bands(len(rows), sh, 3), cells)
        c0 = int(math.floor(ankle[0] - 0.5))
        foot = FOOT[0] if toe > 0 else FOOT[0][::-1]
        x0 = c0 if toe > 0 else c0 - (len(foot) - 2)
        for j, ch in enumerate(foot):
            cells[(x0 + j, ar + 1)] = rgba(ch)
    else:
        s = 1 if ankle[0] > k[0] else -1
        cols = span(int(math.floor(k[0] + 0.5)) + s, int(math.floor(ankle[0] + 0.5)))
        by_cols(k, ankle, cols, [m[:2] if len(m) > 2 else m for m in bands(len(cols), sh, 3)], cells)
        r0 = int(math.floor(ankle[1] - 0.5))
        for j, ch in enumerate("jD"):
            cells[(cols[-1] + s, r0 + j)] = rgba(ch)
    return cells


# ---------------------------------------------------------------------------------------------------------------
# a frame

class Canvas:
    def __init__(self, w, h, pivot):
        self.a = np.zeros((h, w, 4), np.uint8)
        self.p = pivot

    def put(self, cells, dx=0, dy=0, outline=True, behind=False):
        if outline:
            for x, y in ring(cells):
                self._set(x + dx, y + dy, rgba(RING), behind)
        for (x, y), c in cells.items():
            self._set(x + dx, y + dy, c, behind)

    def _set(self, x, y, c, behind):
        tx, ty = self.p[0] + int(round(x)), self.p[1] + int(round(y))
        if 0 <= tx < self.a.shape[1] and 0 <= ty < self.a.shape[0]:
            if behind and self.a[ty, tx, 3]:
                return
            self.a[ty, tx] = c


def shift(cells, dx, dy):
    return {(x + dx, y + dy): c for (x, y), c in cells.items()}


SHOULDER = {"back": (-7.0, -13.5), "front": (5.5, -13.0)}
HANDS = {"back": (-8.5, -1.0), "front": (7.5, -0.5)}       # the idle's hands
HIPS = {"back": -3.5, "front": 3.5}
STAND = {"back": (-4.5, 0), "front": (4.0, 0)}


def place_rotated(dst, layer, about, deg):
    """RotSprite the layer (an RGBA canvas) about the point about (canvas squares) and lay it over dst."""
    import rig_nocturne as RN
    ys, xs = np.nonzero(layer[..., 3])
    if not len(ys):
        return
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    crop = layer[y0:y1, x0:x1]
    j = (about[0] - x0, about[1] - y0)
    r, (jx, jy) = RN.rotsprite(crop, j, deg)
    ox, oy = int(round(about[0] - jx)), int(round(about[1] - jy))
    for yy, xx in zip(*np.nonzero(r[..., 3])):
        ty, tx = oy + yy, ox + xx
        if 0 <= ty < dst.shape[0] and 0 <= tx < dst.shape[1]:
            dst[ty, tx] = r[yy, xx]


NECK_Y = -20                                  # the head's lowest row: a lean moves the rows above it as one block


def lean_x(k, y):
    """A lean of k squares per row (+ forward): the column shift of row y (rows over the hips move, the head as one)."""
    return int(round(k * (HIP_Y - max(y, NECK_Y))))


def figure(P):
    """The design's whole figure as an RGBA array and its standing point inside it."""
    xs = [x for x, _ in P["full"]]
    ys = [y for _, y in P["full"]]
    x0, y0 = min(xs), min(ys)
    a = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
    for (x, y), c in P["full"].items():
        a[y - y0, x - x0] = c
    return a, (-x0, -y0)


def whole(P, pose, cell, pivot):
    """The design's whole figure turned (a quarter turn exactly, else RotSprite) and laid with its lowest square
    `lift` over the feet line, its middle `mid` columns from the standing point."""
    import rig_nocturne as RN
    a, _ = figure(P)
    deg = pose["whole"]
    if deg % 90 == 0:
        t = np.rot90(a, int(deg // 90) % 4).copy()
    else:
        t, _ = RN.rotsprite(a, (a.shape[1] / 2, a.shape[0] / 2), deg)
    ys, xs = np.nonzero(t[..., 3])
    t = t[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    out = np.zeros((cell[1], cell[0], 4), np.uint8)
    top = pivot[1] + 11 - pose.get("lift", 0) - t.shape[0] + 1
    left = pivot[0] + pose.get("mid", 0) - t.shape[1] // 2
    for yy, xx in zip(*np.nonzero(t[..., 3])):
        ty, tx = top + yy, left + xx
        if 0 <= ty < cell[1] and 0 <= tx < cell[0]:
            out[ty, tx] = t[yy, xx]
    return out


HEAD_BOX = (-7, 8, -30, -18)                  # the head and the beard's top (x0, x1, y0, y1), the scroll left of it


# down on the front as oppi's heroes lie at the end of their deaths (Ezreal, Brand; Caitlyn's the same), drawn square
# by square: the scroll lying on the back with its grey caps and brown straps, the navy back with the gold strap
# across it, the belt and the teal flap at the hips, the trousers and the boots flat behind, the near arm along the
# ground with its hand by the face; (first column, rows from LYING_Y)
LYING_X0, LYING_Y = -24, 5
LYING = [
    "..............acknnnnnnkca......",
    ".............ackhnnnnnnhkca.....",
    "..........aaaaozzzzzxzzzzzwa....",
    "........aaozzzzzzzzzxxzzzzzwa...",
    "aaaa..aaowwhhozzzzzzzzxzzzzzwa..",
    "ajDhaaowwwwhyozzzzzzzzzzzzzzza..",
    "aajjjjoooooohhoooooooooooafeidfa",
]
LYING_HEAD = (11, 29)                         # the head's move from standing: upright, the beard on the ground
HEAD_BOX = (-7, 8, -30, -18)                  # the head and the beard's top (x0, x1, y0, y1), the scroll left of it


def lying(P, pose, cell, pivot):
    """The lying frames (LYING): the body flat behind, the head upright with its chin on the ground, never turned
    (Caitlyn's turned face: 「还是看了怪」)."""
    cv = Canvas(cell[0], cell[1], pivot)
    dx = pose.get("dx", 0)
    body = {}
    for i, row in enumerate(LYING):
        for j, ch in enumerate(row):
            if ch != ".":
                body[(LYING_X0 + j + dx, LYING_Y + i)] = rgba(ch)
    cv.put(body, outline=False)
    x0, x1, y0, y1 = HEAD_BOX
    head = {(x, y): c for (x, y), c in P["upper"].items() if x0 <= x <= x1 and y0 <= y <= y1}
    cv.put(shift(head, LYING_HEAD[0] + dx, LYING_HEAD[1]), outline=False)
    cv.a[pivot[1] + 12:] = 0
    return cv.a


def compose(P, pose, cell, pivot):
    """One frame of a pose:
    full: the design as drawn (the idle frames), moved by body; whole (degrees): the design turned whole (the falls);
    body (dx, dy): the upper body, the shoulders and the hips; lean: squares per row the upper body leans forward
      (rows shifted, the head moved as one block, never turned);
    back / front: the hand's point (x, y) or absent (the idle's hand); back_elbow / front_elbow: -1 / +1;
      back_z "front": the far arm drawn over the body (raised in front of the scroll);
    legs: back / front as (ankle x, lift, knee side) or {"ankle": (x, y), "knee": (x, y)}."""
    if "whole" in pose:
        return whole(P, pose, cell, pivot)
    if "lying" in pose:
        return lying(P, pose, cell, pivot)
    cv = Canvas(cell[0], cell[1], pivot)
    bx, by = pose.get("body", (0, 0))
    if pose.get("full"):
        cv.put(shift(P["full"], bx, by), outline=False)
        return cv.a
    k = pose.get("lean", 0.0)
    legs = pose.get("legs", STAND)
    if legs is STAND_LEGS or legs.get("stand"):  # the idle's own legs, square for square
        for name in ("back", "front"):
            cv.put(shift(P["legs"][name], bx, 0), outline=False)
        legs = {}
    elif "kneel" in legs:                       # drawn square by square (KNEEL)
        cv.put(kneel_cells(legs["kneel"], bx), outline=False)
        legs = {}
    for name in [n for n in ("back", "front") if n in legs]:
        spec = legs[name]
        hip = (HIPS[name] + bx, HIP_Y + by)
        if isinstance(spec, dict):              # drawn along its bones: hip -> knee -> ankle
            cv.put(pixel_leg(hip, spec["knee"], spec["ankle"], spec.get("toe", 1)))
        else:                                   # (foot x, lift, kick): the design's own leg
            kick = spec[3] if len(spec) > 3 else 0
            cv.put(design_leg(P["legs"][name], bx, by, spec[0] - FOOT_X[name], spec[1], kick), outline=False)
    sh = {n: (ARMS[n]["S"][0] + bx + lean_x(k, ARMS[n]["S"][1]), ARMS[n]["S"][1] + by) for n in ARMS}
    hb = pose.get("back", (ARMS["back"]["H"][0] + bx, ARMS["back"]["H"][1] + by))
    hf = pose.get("front", (ARMS["front"]["H"][0] + bx, ARMS["front"]["H"][1] + by))
    back_arm = pixel_arm(sh["back"], hb, pose.get("back_elbow", -1), -1, pose.get("back_hand"))
    up = Canvas(cell[0], cell[1], pivot) if "rot" in pose else cv
    if pose.get("back_z") != "front":
        up.put(back_arm)
    upper = {(x + bx + lean_x(k, y), y + by): c for (x, y), c in P["upper"].items()}
    up.put(upper, outline=False)
    up.put(pixel_arm(sh["front"], hf, pose.get("front_elbow", -1), 1, pose.get("front_hand")))
    if pose.get("back_z") == "front":
        up.put(back_arm)
    if "rot" in pose:                           # the upper body turned about a point (the legs not)
        deg_r, (ax, ay) = pose["rot"]
        lay = np.zeros_like(cv.a)
        place_rotated(lay, up.a, (pivot[0] + ax, pivot[1] + ay), deg_r)
        if pose.get("ground"):                  # brought down until its lowest square is on the feet line
            ys = np.nonzero(lay[..., 3].any(1))[0]
            move = pivot[1] + 10 - ys.max()
            if move > 0:
                lay = np.roll(lay, move, 0)
        m = lay[..., 3] > 0
        cv.a[m] = lay[m]
    cv.a[pivot[1] + 12:] = 0
    return cv.a


# ---------------------------------------------------------------------------------------------------------------
# the poses, after the first design's strips (its eye, feet and hands measured frame by frame, work/ks2/old_poses.py):
# the body moves by the first design's eye (a little less: this body is narrower), the feet keep its stance's spread
# round this design's narrower one, the hands where its hands were (the palms of the release frames on the effects'
# spots)

LEG_LEN = 12.5                                 # hip (row -3) to ankle (row 9) standing


def stance_legs(body, feet, lifts=(0, 0)):
    """Both legs bent at the knee for a stance: each hip moves with the body, each ankle on its foot's x (lift rows up);
    a leg shorter than standing bends its knee outward (the far leg's to the left, the near leg's to the right), the
    more the shorter, the knee about halfway down."""
    bx, by = body
    legs = {}
    for side, fx, lift, out in (("back", feet[0], lifts[0], -1), ("front", feet[1], lifts[1], 1)):
        hip = (HIPS[side] + bx, HIP_Y + by)
        ankle = (fx, ANKLE_Y - lift)
        d = math.hypot(ankle[0] - hip[0], ankle[1] - hip[1])
        bend = max(0.5, (LEG_LEN - d) * 0.7)
        t = 0.48
        kn = (hip[0] + (ankle[0] - hip[0]) * t + out * bend, hip[1] + (ankle[1] - hip[1]) * t)
        legs[side] = {"knee": kn, "ankle": ankle, "toe": 1}
    return legs


STAND_LEGS = {"stand": True}

# kneeling, square by square after oppi's kneel (as Caitlyn's is): the near knee on the ground under its hip, its shin
# flat behind with the boot at its end; the far thigh level forward, its shin upright, the foot planted ahead. Rows
# from the hips (the body 6 rows down: hips on row 3) to the ground (row 10); (first column, string) per row
KNEEL_DY = 6
KNEEL = {
    "far": {3: (-3, "ozzzzzzzzxh"), 4: (-3, "wwwwwwwwzxh"), 5: (-2, "oooooooohj"), 6: (6, "hj"), 7: (6, "xj"),
            8: (6, "hj"), 9: (6, "hj"), 10: (5, "jDhj")},
    "near": {3: (2, "ozw"), 4: (2, "ozw"), 5: (2, "wzo"), 6: (2, "ozw"), 7: (2, "ozw"), 8: (2, "xxo"),
             9: (-7, "jDhhjjjjjhxh"), 10: (-7, "jjjjhhhjjjxj")},
    # both knees down (falling forward onto the hands): both shins flat behind
    "near2": {3: (2, "ozw"), 4: (2, "ozw"), 5: (2, "wzo"), 6: (2, "ozw"), 7: (2, "ozw"), 8: (2, "xxo"),
              9: (-7, "jDhhjjjjjhxh"), 10: (-7, "jjjjhhhjjjxj")},
    "far2": {3: (-3, "ozw"), 4: (-3, "ozw"), 5: (-3, "wzo"), 6: (-3, "ozw"), 7: (-3, "ozw"), 8: (-3, "xxo"),
             9: (-11, "jDhhjjjjhxh"), 10: (-11, "jjjjhhjjjxj")},
}


def kneel_cells(kind, dx):
    """The kneeling legs (KNEEL: "one" = the near knee down and the far foot planted ahead, "two" = both knees down),
    the far leg first so the near one lies over it."""
    parts = ("far", "near") if kind == "one" else ("far2", "near2")
    cells = {}
    for part in parts:
        leg = {}
        for y, (x0, row) in KNEEL[part].items():
            for j, ch in enumerate(row):
                leg[(x0 + j + dx, y)] = rgba(ch)
        for q in ring(leg):                     # each leg its own outline, the near one over the far one
            if q not in cells or part.startswith("near"):
                cells[q] = rgba(RING)
        cells.update(leg)
    return cells


def P(body=(0, 0), back=None, front=None, legs=None, lifts=(0, 0), knees=(1, 1), kicks=(0, 0), **kw):
    """A standing pose (attacks, spells, the hit): the idle's own legs square for square, moved sideways with the body
    and never bent, spread or sunk (Caitlyn's rule from the user: 「这里腿各种脱节」「怎么释放技能全外八字啊」); the upper
    body sideways by body[0] and a row lower at most (body[1] <= 1); the hand points (None: the idle's hands)."""
    bx, by = body
    p = {"body": (bx, min(1, by)), "legs": STAND_LEGS}
    if back is not None:
        p["back"] = back
    if front is not None:
        p["front"] = front
    p.update(kw)
    return p


IDLE = {"full": True}


def squat(bx, dy, back, front, lean=0.3, spread=0.0):
    """The deep wide squat of R's channel and the landing (the first design's): the knees high and wide, the hips
    sunk between them, the upper body leaning over the hands on the ground in front."""
    hb, hf = HIPS["back"] + bx, HIPS["front"] + bx
    legs = {"back": {"knee": (hb - 7.5 - spread, 2.5), "ankle": (hb - 9.0 - spread, 9.0), "toe": 1},
            "front": {"knee": (hf + 5.5 + spread, 2.5), "ankle": (hf + 6.5 + spread, 9.0), "toe": 1}}
    return {"body": (bx, dy), "lean": lean, "legs": legs, "back": back, "front": front, "back_z": "front"}


def kneel_pose(dy, lean, back, front, bx=2):
    """Down on the far knee (its shin lying back along the ground), the near foot planted ahead with its knee up,
    the upper body leaning forward over them."""
    hb = HIPS["back"] + bx
    hf = HIPS["front"] + bx
    hy = HIP_Y + dy
    return {"body": (bx, dy), "lean": lean, "back": back, "front": front,
            "legs": {"back": {"ankle": (hb - 6.0, 9.5), "knee": (hb + 2.5, 9.5)},
                     "front": {"ankle": (hf + 4.0, 9.0), "knee": (hf + 4.5, hy + 1.5)}}}

def K(bx, back, front, lean=0.1, kind="one", **kw):
    """A kneeling pose (KNEEL): the body KNEEL_DY rows down onto the kneeling legs."""
    p = {"body": (bx, KNEEL_DY), "lean": lean, "legs": {"kneel": kind}, "back": back, "front": front}
    p.update(kw)
    return p


POSES = {
    "idle": [IDLE for _ in range(6)],
    # the bolt from the near hand, standing on the idle's legs (the first design's strips frame by frame): the far
    # fist in front of the chest, the near hand drawn back to the hip, the open palm thrust out on a bent arm (3, the
    # release) with the far fist at the back hip (its elbow tucked behind the body), held, lowered, the idle; the far
    # arm never flung out (a long thin arm off the body read as a stick)
    "attack": [
        P((1, 1), back=(4, -7), front=(11, -3), back_z="front", lean=0.05),
        P((0, 1), back=(-6, -4), front=(3, -7), back_elbow=1, front_elbow=-1, lean=-0.05),
        P((2, 1), back=(-6, -3), front=(19, -10), back_elbow=1, front_hand="open", lean=0.15),
        P((2, 1), back=(-6, -3), front=(18, -12), back_elbow=1, front_hand="open", lean=0.12),
        P((1, 1), back=(-7, -2), front=(13, -3), back_elbow=1, lean=0.05),
        IDLE,
    ],
    # Q (Overload): the hands out low, wound up (the far hand raised behind, the near one at the hip), the open palm
    # thrust out (3, the release), raised forward with the far fist at the chest, lowered, the idle
    "skill": [
        P((1, 0), back=(3, -6), front=(12, -3), back_z="front", front_hand="open", lean=0.05),
        P((1, 1), back=(-6, -10), front=(4, -6), front_elbow=-1, lean=-0.05),
        P((3, 1), back=(-6, -3), front=(20, -9), back_elbow=1, front_hand="open", lean=0.2),
        P((2, 0), back=(3, -7), front=(17, -16), back_z="front", front_hand="open", lean=0.1),
        P((1, 1), back=(-7, -2), front=(13, -2), back_elbow=1, lean=0.05),
        IDLE,
    ],
    # the combo E -> W -> Q: arms spread with open hands, E's palm out and up (2), wound up, the far arm raised with
    # the hand open over the head (4-5, in front of the scroll), W thrust forward low (6), down on one knee (7), up,
    # Q's palm out (9), raised, lowered, the idle
    "skill2": [
        P((1, 1), back=(-12, -9), front=(14, -9), back_hand="open", front_hand="open"),
        P((2, 1), back=(-6, -4), front=(18, -14), back_elbow=1, front_hand="open", lean=0.1),
        P((1, 0), back=(3, -7), front=(10, -8), back_z="front", front_elbow=-1),
        P((2, 0), back=(-8, -24), front=(13, -5), back_z="front", back_hand="open"),
        P((1, 0), back=(-7, -25), front=(13, -3), back_z="front", back_hand="open"),
        P((3, 1), back=(-6, -3), front=(19, -6), back_elbow=1, front_hand="open", lean=0.15),
        K(2, back=(-9, 1), front=(11, 5), lean=0.2),
        P((2, 1), back=(-11, -8), front=(7, -2)),
        P((3, 1), back=(-6, -3), front=(20, -8), back_elbow=1, front_hand="open", lean=0.15),
        P((2, 0), back=(3, -7), front=(17, -15), back_z="front", front_hand="open"),
        P((1, 0), back=(-8, -2), front=(12, -1), back_elbow=1),
        IDLE,
    ],
    # R (Realm Warp): arms spread with open hands, down on one knee with both hands toward the ground in front (2-4),
    # standing with the far arm raised, the hand open (5-6), both fists raised high
    "ult": [
        P((0, 0), back=(-14, -11), front=(15, -12), back_hand="open", front_hand="open"),
        K(2, back=(4, 8), front=(11, 5), lean=0.25, back_z="front"),
        K(2, back=(4, 9), front=(11, 5), lean=0.3, back_z="front"),
        K(1, back=(3, 8), front=(10, 5), lean=0.25, back_z="front"),
        P((1, 1), back=(-7, -25), front=(15, -5), back_z="front", back_hand="open"),
        P((1, 0), back=(-7, -26), front=(15, -6), back_z="front", back_hand="open"),
        P((1, 1), back=(-13, -20), front=(15, -20), back_hand="fist", front_hand="fist"),
        P((1, 1), back=(-13, -20), front=(15, -20), back_hand="fist", front_hand="fist"),
    ],
    # landing out of the portal: on one knee with a hand down, up, the idle
    "ult_land": [
        K(2, back=(4, 8), front=(11, 5), lean=0.25, back_z="front"),
        P((2, 1), back=(-11, -2), front=(15, 2)),
        P((1, 0), back=(-11, -3), front=(13, 0)),
        IDLE,
    ],
    # struck: thrown back on the idle's legs, the arms flung with the hands open; caught again
    "hit": [
        P((-3, 0), back=(-14, -8), front=(11, -11), lean=-0.15, back_hand="open", front_hand="open"),
        P((1, 1), back=(-8, -2), front=(13, -1), back_elbow=1),
    ],
}


def run_cycle():
    """Two steps in eight frames (League's walk under the scroll): contact, down, passing, up, then the other leg;
    the near foot's x minus the far foot's changes sign twice a cycle; the arms swing against the legs."""
    # (body dy, back foot (x, lift), front foot (x, lift), back hand dx, front hand dx): the first design's run spread
    # its feet up to 24 squares apart in a 17-square stance; this narrower body steps about 12
    steps = [
        (1, (-7.0, 0), (5.0, 0), 5, -5),        # contact: the near (front) foot ahead
        (1, (-6.0, 2), (2.0, 0), 3, -3),        # down: the far foot lifts off behind
        (0, (-2.0, 3), (-1.0, 0), 0, 0),        # passing
        (0, (3.0, 1), (-4.0, 0), -3, 3),        # up: the far foot reaches forward
        (1, (5.0, 0), (-7.0, 0), -5, 5),        # contact: the far foot ahead
        (1, (2.0, 0), (-6.0, 2), -3, 3),
        (0, (-1.0, 0), (-2.0, 3), 0, 0),
        (0, (-4.0, 0), (3.0, 1), 3, -3),
    ]
    out = []
    for dy, (bx, bl), (fx, fl), bh, fh in steps:
        p = P((1, dy), back=(-8.0 + 0.6 * bh + 1, -1 + dy), front=(7.5 + 0.6 * fh + 1, -1 + dy),
              legs=(bx, fx), lifts=(bl, fl), kicks=(min(2, bl), min(2, fl)), lean=0.1)
        out.append(p)
    return out


def death():
    """The death as Caitlyn's second design's (oppi's): struck back, down on one knee with the hands hanging, slumping
    over them, down on both knees bent forward, then flat on the front with the head upright (LYING) - never the
    upper body turned on its side (「死亡的时候姿势也是很奇怪」)."""
    return [
        P((-3, 0), back=(-15, -8), front=(11, -11), lean=-0.15, back_hand="open", front_hand="open"),
        K(1, back=(-9, 0), front=(10, 1), lean=0.1),
        K(1, back=(-7, 3), front=(10, 4), lean=0.25),
        K(2, back=(-4, 6), front=(12, 7), lean=0.35, kind="two", back_elbow=1),
        {"body": (3, KNEEL_DY + 2), "legs": {"kneel": "two"}, "lean": 0.55, "back": (0, 9), "front": (13, 9),
         "back_elbow": 1},
        {"lying": True, "dx": 2},
        {"lying": True, "dx": 2},
        {"lying": True, "dx": 2},
    ]


def lol_tag(tag, keep_x=0.8, **extra):
    """Every frame of a tag posed after League's (lol_pose), the hips' sideways move measured from the tag's mean."""
    table = lol_table()
    xs = [f["joints"]["Pelvis"][0] for f in table[tag]]
    ref = (sum(xs) / len(xs), 0.0)
    return [lol_pose(tag, k, table, ref, keep_x, **extra) for k in range(len(table[tag]))]


def run_steps():
    """The run in the first design's approved run's order (work/ks2 oldrun sheets: the swinging foot kicked up behind
    in 1-2, passing under the body in 3, the wide stride in 4), its legs alternating as League's do: the far leg swings
    in 1-4, the near leg in 5-8. The arms swing against the legs along the body, the elbows bent back: a hand forward
    sits in front at the belt, a hand back by the hip. Hips at +-3.5 under the belt (each leg keeps 0.4 of that side);
    knee and ankle per leg from the standing point; the body's bob (lowest in the stride) and a slight forward lean."""
    # (support (knee, ankle), swing (knee, ankle), body dy)
    phases = [
        (((1.5, 3.5), (2.0, 9.0)), ((-4.0, 4.0), (-10.0, 3.5)), 0),     # 1: the swing foot kicked up behind
        (((0.5, 3.5), (0.0, 9.0)), ((-3.0, 4.5), (-9.0, 5.0)), 1),      # 2: still behind, coming down
        (((-1.5, 3.5), (-3.0, 9.0)), ((1.0, 4.0), (-2.0, 7.0)), 0),     # 3: passing under the body, tucked
        (((-5.5, 4.0), (-8.5, 8.5)), ((6.0, 3.5), (8.5, 9.0)), 1),      # 4: the stride, the swing foot lands ahead
    ]
    near_fwd, near_back, near_mid = (10.5, -7.5), (4.5, -3.0), (8.0, -3.0)     # forward: the elbow bent square
    far_fwd, far_back, far_mid = (-5.0, -4.0), (-11.5, -1.0), (-7.5, -1.0)    # forward: behind the body
    # far leg swinging (1-4): the far arm forward while that leg is back, back when it lands ahead
    arms_far_swing = [(far_fwd, near_back), (far_fwd, near_back), (far_mid, near_mid), (far_back, near_fwd)]
    arms_near_swing = [(far_back, near_fwd), (far_back, near_fwd), (far_mid, near_mid), (far_fwd, near_back)]
    lean = 0.12
    out = []
    for k in range(8):
        ph = k % 4
        (sk, sa), (wk, wa), dy = phases[ph]
        swing = "back" if k < 4 else "front"
        support = "front" if k < 4 else "back"
        legs = {}
        for side, (kn, an) in ((support, (sk, sa)), (swing, (wk, wa))):
            off = HIPS[side] * 0.4
            legs[side] = {"knee": (kn[0] + off, kn[1] + dy * 0.5), "ankle": (an[0] + off, an[1]), "toe": 1}
        back, front = (arms_far_swing if k < 4 else arms_near_swing)[ph]
        out.append({"body": (0, dy), "lean": lean, "legs": legs,
                    "back": (back[0], back[1] + dy), "front": (front[0], front[1] + dy),
                    # the far arm swung forward or passing folds its elbow in behind the body, never out to the left
                    # (bent out it walls a window of ground against the coat)
                    "front_elbow": -1, "back_elbow": 1 if back in (far_fwd, far_mid) else -1})
    return out


POSES["run"] = run_steps()
POSES["dead"] = death()


def pinholes(a, most=4, feet=None, slit=(14, 2)):
    """Clear pockets walled in all round once the importer has closed the outline (strips.complete_outline: the notch
    two limbs leave against a body becomes a window of ground, a hole at game size) take their walls' commonest colour:
    pockets of up to `most` squares, and slits (up to slit[0] squares, no row wider than slit[1]: a hanging arm a
    square off the coat) - their walls are the two outlines, so the arm lies against the coat with one dark seam."""
    from collections import Counter, deque
    import strips as G
    b = G.complete_outline(a, feet=feet)[0]
    a = a.copy()
    op = b[..., 3] > 0
    h, w = op.shape
    seen = np.zeros(op.shape, bool)
    for y0, x0 in zip(*np.nonzero(~op)):
        if seen[y0, x0]:
            continue
        comp, q, edge = [], deque([(y0, x0)]), False
        seen[y0, x0] = True
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if not (0 <= yy < h and 0 <= xx < w):
                    edge = True
                elif not op[yy, xx] and not seen[yy, xx]:
                    seen[yy, xx] = True
                    q.append((yy, xx))
        if edge:
            continue
        rows = Counter(y for y, _ in comp)
        if len(comp) > most and (len(comp) > slit[0] or max(rows.values()) > slit[1]):
            continue
        walls = Counter()
        for y, x in comp:
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                c = b[y + dy, x + dx]
                if c[3]:
                    walls[tuple(int(v) for v in c)] += 1
        for y, x in comp:
            a[y, x] = walls.most_common(1)[0][0]
    return a


def build(tag, P, cells):
    cell = cells["cell"][:2]
    return [pinholes(compose(P, POSES[tag][k], cell, fr["pivot"]), feet=fr["pivot"][1] + 11)
            for k, fr in enumerate(cells["tags"][tag])]


def strip(frames, cell, cols):
    rows = (len(frames) + cols - 1) // cols
    a = np.zeros((rows * cell[1], cols * cell[0], 4), np.uint8)
    for k, c in enumerate(frames):
        a[(k // cols) * cell[1]:(k // cols + 1) * cell[1], (k % cols) * cell[0]:(k % cols + 1) * cell[0]] = c
    return a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    cells = json.load(open(lp(a.cells), encoding="utf-8"))
    P = parts(design())
    tags = a.only.split(",") if a.only else [t for t in POSES if t != "test"]
    os.makedirs(lp(a.out), exist_ok=True)
    for tag in tags:
        frames = build(tag, P, cells)
        n = len(frames)
        cols = {1: 1, 2: 2, 3: 3, 4: 4, 5: 3, 6: 3}.get(n, 4)
        s1 = np.repeat(np.repeat(strip(frames, cells["cell"][:2], cols), Z, 0), Z, 1)
        path = os.path.join(a.out, "ryze_%s.png" % tag)
        if a.check:
            same = np.array_equal(np.asarray(Image.open(lp(path)).convert("RGBA")), s1)
            print(tag, "same" if same else "DIFFERENT")
            continue
        Image.fromarray(s1).save(lp(path))
        print(tag, n, "frames")


if __name__ == "__main__":
    main()
