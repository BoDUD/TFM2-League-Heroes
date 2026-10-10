#!/usr/bin/env python3
"""Viego's action strips posed from the approved design's own parts (tools/art/rigkit.py; the casting body = the idle's).

    python tools/art/rig_viego.py [--check] [--review DIR] [--tags attack,skill] [--parts DIR]

Codex's step-2 delivery (assets/source/viego/codex_strips/) cut the design into parts but turned them by any angle with
nearest-neighbour sampling (the torso leant 8-18 degrees, the arm 20-150, the legs 12-35): the blade breaks into teeth,
the coat and the legs lose and double squares - the pack's rule is that a re-posed frame keeps every square of the
design (「不要有任何模型变形的问题」「像素缺失也是」, tools/art/rig_xayah.py; Tryndamere's rigid units, rig_tryndamere.py).
The user: 「codex交付了 有问题的地方你帮我修复 完美版了喊我review 灵活运用工具」. Every frame here is the design
(tools/art/design_viego.py, 42 rows crown to soles) with only what the action moves moved, by lossless moves only:
- the greatsword, the near hand gripping it and the near forearm are ONE rigid unit, turned about the elbow by the
  eight exact symmetries of the square grid (the quarter turns, the two mirrors and the two diagonal transposes): the
  blade at 27 or 63 degrees in every quadrant, never resampled; the stretch of blade the head hides in the design is
  restored from the blade's own squares (two visible columns' slices carried on down its line, TEMPLATE);
- the body leans by whole-row shifts (rows above the hips, the head moved whole with its chin row), crouches by sinking
  the body over the standing legs (layering), jumps by moving the whole figure;
- the run: the boots step in their own lanes (moved whole, drawn over the coat's hem), the body leans into it and the
  greatsword rests on his shoulder pointing back (run_frame);
- the head, the far arm and the coat stay square for square;
- at 90% (SCALE): the body loses whole lines once before posing, the blade two of its own repeating steps.
League's renders (assets/source/viego/poses.json, pose_n) and Codex's frames give the poses.
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
DESIGN = os.path.join(NATIVE, "viego_native.png")
HERO = "viego"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 128), (64, 88)

# ---------------------------------------------------------------------------------------------- parts (canvas rows)
# the head: the silver hair, the teal thorn crown, the pale face and its teal eyes (rows: (first, last) column)
HEAD = {56: (64, 66), 57: (63, 67), 58: (60, 68), 59: (60, 69), 60: (57, 69), 61: (57, 70), 62: (56, 72),
        63: (56, 73), 64: (56, 75), 65: (57, 75), 66: (56, 74), 67: (57, 73), 68: (57, 74), 69: (57, 74),
        70: (58, 72), 71: (58, 71), 72: (59, 72), 73: (59, 71), 74: (59, 71)}
TEAL = ["#042D31", "#03615B", "#037C70", "#03A188", "#0AB79C", "#39D7C1", "#60E7D6", "#91F9F7"]
# the sword's two clusters: the hooked guard / pommel left of the head and the blade right of it (boxes r0, r1, c0, c1)
SWORD_LEFT = (55, 79, 42, 57)
SWORD_RIGHT = (48, 63, 69, 96)
# the near hand on the grip (the dark glove) and the near arm under it (rows: (first, last))
HAND = {66: (51, 53), 67: (50, 54), 68: (49, 54), 69: (49, 55), 70: (49, 54), 71: (50, 52)}
ARM = {72: (50, 55), 73: (50, 57), 74: (50, 58), 75: (50, 58), 76: (50, 58), 77: (50, 58), 78: (52, 58),
       79: (57, 59), 80: (56, 58)}
SHOULDER = (58.5, 76.5)               # the near arm's root
ELBOW = (53.0, 77.5)                   # the near elbow: the forearm, the fist and the sword turn about it
FOREARM_COLS = 54                      # arm squares up to this column are the forearm (it turns); the upper arm stays
GRIP = (52.5, 69.5)                    # the gloved fist on the grip
TEMPLATE = (76, 75)                    # two visible columns of the blade whose slices restore the hidden stretch
RESTORE = (56, 72)                     # the columns the head hides it in (the hand's grip at 49-55)
OVERRIDE = 59                          # from this column the restored slices replace what the cut left

# the far arm hanging at his side (rows: (first, last)), its root, and the coat's tail behind the far leg
FAR_ARM = {74: (72, 75), 75: (71, 74), 76: (69, 75), 77: (73, 76), 78: (72, 77), 79: (71, 76), 80: (71, 77),
           81: (71, 77), 82: (72, 77), 83: (73, 77), 84: (74, 77), 85: (75, 77), 86: (75, 78), 87: (74, 77),
           88: (75, 77)}
FAR_SHOULDER = (72.5, 76.5)
HIP_ROW = 86                           # the belt's bottom: rows above lean / sink, the legs below stand
NECK_ROW = 74                          # the chin: the head moves whole with this row's shift

# 90% (the user, 2026-10-11: 「佛耶戈的模型在游戏里有点大了 稍微缩小一点 你选一套最合适的」; 42 rows crown to soles ->
# 38, Senna's and Shen's heights): the body loses whole rows and columns ONCE (tools/art/shrink_frames.py, never through
# his face), before any action is posed from it - cut from the finished frames, a line runs through a different part of
# him in every frame (rig_xinzhao.py's SCALE). The sword unit stays as drawn (whole lines out of its 1:2 blade would
# leave uneven steps) and turns about the elbow's new place; the coordinates below the parts are read with are the
# design's, the posing ones (HIP_ROW, NECK_ROW, NEAR_LOW, FAR_LOW, the elbow) move with the cut (Parts._shrink).
SCALE = 0.9
SHRINK_KEEP = ["!91F9F7+6,4,11,4"]     # his face (grown from the glint in his eye): no line crosses it
# the boots' rows (from the pivot) stay: the cheapest row was the near boot's ankle (a boot one row shorter); a column
# through a boot is the same in every frame (the boots move whole after the cut)
BOOT_ROWS = tuple(range(95 - PIVOT[1], 100 - PIVOT[1]))
PLAN = None
# the blade 10% shorter too, by whole steps of its own 1:2 line: the stretch the head hides in the design is restored
# from two of its columns (TEMPLATE), so there it repeats exactly every two columns and a row - BLADE_STEPS of those
# steps taken out at column BLADE_CUT leave no seam (whole rows or columns through the blade would leave uneven steps)
BLADE_CUT, BLADE_STEPS = 70, 2


def shortened(unit):
    """The sword unit (a canvas) with BLADE_STEPS of the blade's steps taken out at BLADE_CUT: the blade beyond the cut
    moved two columns in and a row down per step, over the removed stretch."""
    out = unit.copy()
    out[:, BLADE_CUT - 2 * BLADE_STEPS:] = 0
    tip = unit.copy()
    tip[:, :BLADE_CUT] = 0
    K.put(out, tip, -2 * BLADE_STEPS, BLADE_STEPS)
    return out


def _pivot_frame(c):
    f = np.zeros((2 * PIVOT[1] + 1, 2 * PIVOT[0] + 1) + c.shape[2:], c.dtype)
    f[:c.shape[0], :c.shape[1]] = c
    return f


def map_x(x):
    """A canvas column (or point) on the shrunk design: the removed columns between it and the pivot close in."""
    cs = [PIVOT[0] + c for c in PLAN["cols"]]
    if x < PIVOT[0]:
        return x + sum(1 for c in cs if x < c < PIVOT[0])
    return x - sum(1 for c in cs if PIVOT[0] < c <= x)


def map_y(y):
    """A canvas row (or point): down one for every removed row under it (all above the soles, which stay)."""
    return y + sum(1 for r in PLAN["rows"] if PIVOT[1] + r > y)


def shrunk(c):
    """A 128x128 canvas (image or mask) without the plan's rows and columns, the soles on their row."""
    gone_r = {PIVOT[1] + r for r in PLAN["rows"]}
    gone_c = {PIVOT[0] + q for q in PLAN["cols"]}
    out = np.zeros_like(c)
    for y in range(c.shape[0]):
        if y in gone_r:
            continue
        ny = map_y(y)
        for x in range(c.shape[1]):
            if x not in gone_c and 0 <= ny < c.shape[0]:
                nx = map_x(x)
                if 0 <= nx < c.shape[1]:
                    out[ny, nx] = c[y, x]
    return out


def map_rows(spec):
    m = shrunk(K.mask_rows(spec))
    out = {}
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        if len(xs):
            out[y] = (int(xs.min()), int(xs.max()))
    return out


def hexrgb(h):
    return tuple(int(h[k:k + 2], 16) for k in (1, 3, 5))


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a
        op = a[..., 3] > 0
        self.head_m = K.mask_rows(HEAD) & op
        teal = K.colour_mask(a, [hexrgb(c) for c in TEAL])
        outl = op & (a[..., :3] == np.array(D.outline, np.uint8)).all(-1)
        sword = np.zeros_like(op)
        for r0, r1, c0, c1 in (SWORD_LEFT, SWORD_RIGHT):
            box = K.mask_box(r0, r1, c0, c1)
            t = teal & box & ~self.head_m
            # the outline squares that touch the sword's teal (and no other colour) belong to it
            near = np.zeros_like(op)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    near |= np.roll(np.roll(t, dy, 0), dx, 1)
            sword |= t | (near & outl & box & ~self.head_m)
        self.hand_m = K.mask_rows(HAND) & op & ~sword & ~self.head_m
        self.arm_m = K.mask_rows(ARM) & op & ~sword & ~self.head_m & ~self.hand_m
        self.arm_m[:, FOREARM_COLS + 1:] = False      # the forearm only: the upper arm stays on the shoulder
        self.sword_m = sword
        self.far_m = K.mask_rows(FAR_ARM) & op & ~self.head_m
        # the blade restored under the head: the visible blade's own vertical slices (columns TEMPLATE, a pair: the
        # blade drops a row every two columns) carried on down its line to the hilt, only where nothing is drawn
        restored = np.zeros_like(a)
        for x in range(RESTORE[0], RESTORE[1] + 1):
            src = TEMPLATE[0] if (TEMPLATE[0] - x) % 2 == 0 else TEMPLATE[1]
            drop = (src - x) // 2
            ys = np.nonzero(sword[:, src])[0]
            for y in ys:
                restored[y + drop, x] = a[y, src]
        unit = np.zeros_like(a)
        for m in (self.sword_m, self.hand_m, self.arm_m):
            unit[m] = a[m]
        # left of OVERRIDE only where nothing is drawn (the guard's bar stays in front); from it on the slices replace
        # what the cut left there (the head's outline squares that touched the blade)
        left = restored.copy()
        left[:, OVERRIDE:] = 0
        right = restored.copy()
        right[:, :OVERRIDE] = 0
        K.put(unit, left, 0, 0, under=True)
        K.put(unit, right, 0, 0)
        if SCALE != 1:
            unit = shortened(unit)
        self.unit_canvas = unit
        self.unit = K.Part.from_canvas(unit, unit[..., 3] > 0, ELBOW)
        # as drawn (on his shoulder) the unit is the design's own cut: the head hides the blade there anyway
        cut = np.zeros_like(a)
        for m in (self.sword_m, self.hand_m, self.arm_m):
            cut[m] = a[m]
        self.unit_drawn = K.Part.from_canvas(cut, cut[..., 3] > 0, ELBOW)
        self.body = a.copy()
        for m in (self.sword_m, self.hand_m, self.arm_m):
            self.body[m] = 0
        self.far = K.Part.from_canvas(a, self.far_m, FAR_SHOULDER)
        self.elbow = ELBOW
        if SCALE != 1:
            self._shrink()

    def _shrink(self):
        """The body, the head's and the far arm's masks and the posing rows on the 90% design (the plan chosen once, on
        the body without the sword unit); the design becomes the shrunk body with the unit on its shoulder (the blade
        the head hid restored: the smaller head need not hide all of it) and the head over it."""
        global PLAN, HIP_ROW, NECK_ROW, NEAR_LOW, FAR_LOW
        import shrink_frames as SF
        if PLAN is None:
            frame = [(_pivot_frame(self.body), 0)]
            PLAN = SF.plan_tag(frame, SF.body_of(frame), SCALE, SHRINK_KEEP, edge_rows=BOOT_ROWS)
            HIP_ROW, NECK_ROW = map_y(HIP_ROW), map_y(NECK_ROW)
            NEAR_LOW, FAR_LOW = map_rows(NEAR_LOW), map_rows(FAR_LOW)
        self.body = shrunk(self.body)
        self.head_m = shrunk(self.head_m)
        self.far_m = shrunk(self.far_m)
        self.elbow = (map_x(ELBOW[0]), map_y(ELBOW[1]))
        self.unit_drawn = self.unit
        a = self.body.copy()
        head = np.zeros_like(a)
        head[self.head_m] = a[self.head_m]
        K.place(a, self.unit, self.elbow)
        K.put(a, head, 0, 0)
        self.D.a = a

    def orient(self, name):
        """The sword unit in one of the eight exact symmetries, named by where the blade points."""
        u = self.unit
        return {"idle": self.unit_drawn,        # blade up-right 27, the fist up at the shoulder (the design's cut)
                "down_steep": K.rot90(u, 1),    # blade down-right 63, the fist forward-up: a stab down in front
                "trail": K.rot90(u, 2),         # blade down-left 27, the fist forward-down: trailing behind him
                "back_steep": K.rot90(u, 3),    # blade up-left 63, the fist back-down
                "raised_back": u.flip_h(),      # blade up-left 27, the fist forward-up: raised back over the head
                "low": u.flip_v(),              # blade down-right 27, the fist back-down
                "behind_steep": u.transpose(),  # blade down-left 63, the fist back-up
                "upright": K.rot90(u.flip_h(), 1),  # blade up-right 63, the fist forward-down: held up before him
                }[name]


ORIENTS = ["idle", "down_steep", "trail", "back_steep", "raised_back", "low", "behind_steep", "upright"]


# ---------------------------------------------------------------------------------------------- posing
MS = {"idle": [140] * 8, "run": [108] * 7 + [109], "attack": [60, 60, 50, 70, 80, 80], "skill": [50, 50, 40, 60, 50, 50],
      "skill2": [70, 80, 120, 130, 120, 120, 130], "ult": [60, 60, 60, 70, 60, 80, 100, 110],
      "possess": [80, 80, 120, 120], "hit": [100, 100], "dead": [100, 100, 100, 120, 150, 200, 300, 400]}
TAGS = list(MS)


def lean_shift(row, lean):
    """Columns a row moves for a lean (+ forward): 0 at the hips, the head with its chin row."""
    if not lean or row >= HIP_ROW:
        return 0
    v = (HIP_ROW - max(row, NECK_ROW)) * lean
    return int(math.floor(abs(v) + 0.5)) * (1 if v > 0 else -1)


def upper_lower(a):
    up = a.copy()
    up[HIP_ROW:] = 0
    low = a.copy()
    low[:HIP_ROW] = 0
    return up, low


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


def as_rgba(m):
    return np.where(m[..., None], 255, 0).astype(np.uint8).repeat(4, -1)


# a pose: (sword orientation, layer "front" (over the body, under the head) / "behind" / "over" (over the head too),
# whole-figure (dx, dy), lean (+ forward, whole-row shifts above the hips), sink (rows the upper body sits down over
# the standing legs), legs: None or (near dx, far dx) - the boots and shins moved whole)
POSES = {
    # the two-handed slash (release frame 5, tick 14): up off the shoulder, raised behind, over the top, down low
    "attack": [("idle", "front", (0, 0), 0.0, 0, None),
               ("upright", "front", (-1, 0), -0.05, 0, None),
               ("back_steep", "behind", (-1, 0), -0.10, 0, None),
               ("upright", "front", (1, -2), 0.05, 0, None),
               ("low", "front", (3, 0), 0.12, 2, (-1, 2)),
               ("idle", "front", (1, 0), 0.03, 0, None)],
    # Q, the thrust (release frame 4, tick 8): drawn back behind him, coiled, thrust forward and low
    "skill": [("upright", "front", (0, 0), 0.0, 0, None),
              ("trail", "front", (-1, 0), -0.08, 0, None),
              ("trail", "front", (-1, 0), -0.05, 2, (-1, 1)),
              ("low", "front", (4, 0), 0.12, 1, (-1, 3)),
              ("low", "front", (4, 0), 0.12, 1, (-1, 3)),
              ("idle", "front", (1, 0), 0.03, 0, None)],
    # E's mist then W (release frame 5, tick 24): the sword down at his side, a hop back, the charge, the dash
    "skill2": [("behind_steep", "behind", (0, 0), 0.0, 0, None),
               ("behind_steep", "behind", (-2, -2), -0.05, 0, None),
               ("upright", "front", (-1, 0), -0.03, 0, None),
               ("upright", "front", (-1, 0), -0.03, 1, (-1, 1)),
               ("trail", "front", (6, 0), 0.15, 1, (-2, 3)),
               ("low", "front", (5, 0), 0.08, 1, (-1, 2)),
               ("idle", "front", (2, 0), 0.03, 0, None)],
    # R (release frame 6, tick 19): crouch, spring up, in the air, land, the stab down in front
    "ult": [("upright", "front", (0, 0), 0.0, 0, None),
            ("back_steep", "behind", (0, 0), -0.05, 2, (-1, 1)),
            ("trail", "front", (1, -3), 0.05, 0, None),
            ("idle", "front", (2, -5), 0.0, 0, None),
            ("down_steep", "front", (2, 0), 0.05, 0, None),
            ("down_steep", "front", (2, 0), 0.10, 3, (-1, 2)),
            ("down_steep", "front", (2, 0), 0.10, 3, (-1, 2)),
            ("idle", "front", (1, 0), 0.03, 0, None)],
    # taking the soul (release frame 3, tick 10): the sword off the shoulder, trailing low, the stab down
    "possess": [("upright", "front", (0, 0), 0.0, 0, None),
                ("trail", "front", (-1, 0), -0.03, 0, None),
                ("down_steep", "front", (1, 0), 0.10, 3, (-1, 2)),
                ("idle", "front", (0, 0), 0.0, 0, None)],
    "hit": [("idle", "front", (-2, 0), -0.08, 0, None),
            ("idle", "front", (-1, 0), -0.04, 0, None)],
    # the death: struck, the sword down, onto his knees over the planted sword
    "dead": [("idle", "front", (-2, 0), -0.08, 0, None),
             ("down_steep", "front", (1, 0), 0.05, 0, None),
             ("down_steep", "front", (1, 0), 0.10, 3, (-1, 2)),
             ("down_steep", "front", (1, 0), 0.12, 4, (-1, 2)),
             ("down_steep", "front", (1, 0), 0.14, 5, (-1, 2)),
             ("down_steep", "front", (1, 0), 0.15, 5, (-1, 2)),
             ("down_steep", "front", (1, 0), 0.15, 5, (-1, 2)),
             ("down_steep", "front", (1, 0), 0.15, 5, (-1, 2))],
}

# the boots (rows: (first, last)): the coat's long flaps hide the shins down to row 94 - only the boots show under the
# hem, so only they move (moving rows 92-94 with them tore the flaps' hem)
NEAR_LOW = {95: (51, 60), 96: (51, 60), 97: (51, 60), 98: (51, 60)}
FAR_LOW = {95: (68, 77), 96: (68, 77), 97: (68, 77), 98: (68, 77), 99: (68, 77)}


def posed(P, orient, layer, lean, sink=0, near=(0, 0), far=(0, 0), over=False):
    """The body leant (whole rows above the hips), lowered `sink` rows over the boots (each moved (dx, lift): behind the
    hem, or `over` it), the sword unit in `orient` at the elbow: behind the body, or in front of it and under the head
    ("front") or over everything ("over"). Returns the canvas and the head's mask."""
    up, low = upper_lower(P.body)
    headm = leaned(as_rgba(P.head_m), lean)[..., 3] > 0
    base = np.zeros_like(P.body)
    K.put(base, low, 0, 0)
    K.put(base, leaned(up, lean), 0, 0)
    # a crouch lowers everything but the boots (the coat's hem over them): never the body over the coat
    c = lowered(P, base, sink, near=near, far=far, over=over)
    headm = np.roll(headm, sink, 0)
    sh = (P.elbow[0] + lean_shift(int(P.elbow[1]), lean), P.elbow[1] + sink)
    if layer == "behind":
        K.place(c, P.orient(orient), sh, under=True)
    else:
        head = np.zeros_like(c)
        head[headm] = c[headm]
        K.place(c, P.orient(orient), sh)
        if layer == "front":
            K.put(c, head, 0, 0)
    c[P.D.soles + 1:] = 0
    return c, headm


def compose(P, pose):
    orient, layer, (dx, dy), lean, sink, legs = pose
    c, keep = posed(P, orient, layer, lean, sink, near=(legs[0], 0) if legs else (0, 0),
                    far=(legs[1], 0) if legs else (0, 0))
    if dx or dy:
        c = K.shifted(c, dx, dy)
        keep = K.shifted(as_rgba(keep), dx, dy)[..., 3] > 0
        if dy > 0:
            c[P.D.soles + 1:] = 0
    return c, keep


# legs that stand: the boots (NEAR_LOW / FAR_LOW). A bob or a breath moves everything ELSE down over them -
# the coat's hem then hides a little more of the shins, like knees bending - so neither the coat nor the belt is ever
# squashed (the user: 「上下摆动造成模型变形」 on the first idle, which sank the upper body over the coat)
def lowered(P, a, n, near=(0, 0), far=(0, 0), over=False):
    """`a` with everything but the boots moved down n rows; the near / far boot moved (dx, lift), behind the coat (a
    crouch: the hem hides their tops) or, `over`, drawn whole over it (a step: the boot keeps its shape)."""
    nm = K.mask_rows(NEAR_LOW) & (a[..., 3] > 0)
    fm = K.mask_rows(FAR_LOW) & (a[..., 3] > 0)
    nl, fl = np.zeros_like(a), np.zeros_like(a)
    nl[nm], fl[fm] = a[nm], a[fm]
    body = a.copy()
    body[nm | fm] = 0
    boots = [K.shifted(fl, far[0], -far[1]), K.shifted(nl, near[0], -near[1])]       # the near boot in front
    body = K.shifted(body, 0, n)
    c = np.zeros_like(a)
    for layer in ([body] + boots if over else boots + [body]):
        K.put(c, layer, 0, 0)
    c[P.D.soles + 1:] = 0
    return c


# the run: each boot steps in its own lane - planted, sliding back a column a frame, then lifted and carried forward -
# the far leg half a cycle later; the body dips a row as a foot lands. The first run brought both boots in under the
# hips (IN): the coat's flaps hung over nothing - 「走路姿势太怪了」. The boots are drawn whole over the hem: a lifted boot
# behind it lost its top rows but for its outline column, left standing beside the hem like a hook
# (「脚移动时看起来有点变形」). Then, in game: 「佛耶戈待机的姿势和走路时应该是不一样的 你想办法补一套的 现在的姿势走路
# 太怪了」 - the run had the idle's upright stance, the blade forward over his shoulder. Now he leans into the run
# (RUN_LEAN, whole rows above the hips) with the greatsword resting on his shoulder the other way, its blade pointing
# back ("raised_back": the unit mirrored, the grip where the idle holds it). Of the eight ways the unit turns this one
# keeps the blade off the ground: dragged behind him ("trail") it ran 8-9 rows under the feet line, cut there, and
# the cut moved along the blade with the bob (a tip changing length from frame to frame)
STRIDE = [(2, 0), (1, 0), (0, 0), (-1, 0), (-1, 1), (0, 2), (1, 2), (2, 1)]      # (dx from the boot's place, lift)
BOB = [1, 0, 0, 0, 1, 0, 0, 0]
RUN_POSE = ("raised_back", "front")
RUN_LEAN = 0.25


def run_frame(P, k):
    return posed(P, *RUN_POSE, RUN_LEAN, sink=BOB[k], near=STRIDE[k], far=STRIDE[(k + 4) % 8], over=True)


# the idle: his own breath (import_native's shared cut costs 18 visible squares through the coat and the trousers): the
# whole figure but the boots and shins sinks 0 0 1 1 1 1 0 0 rows over them (lowered)
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]


def idle_frame(P, k):
    n = BREATH[k]
    return lowered(P, P.D.a, n), np.roll(P.head_m, n, 0)


def frames(P, tag):
    if tag == "idle":
        out = [idle_frame(P, k) for k in range(8)]
    elif tag == "run":
        out = [run_frame(P, k) for k in range(8)]
    else:
        out = [compose(P, p) for p in POSES[tag]]
    return [K.finish(c, P.D.outline, P.D.soles, keep=keep) for c, keep in out]


def parts_review(P, path):
    """The design with its parts tinted, and the sword unit in its eight orientations, at 6x."""
    a = P.D.a
    tint = a.copy()
    for m, c in ((P.sword_m, (0, 255, 170)), (P.hand_m, (255, 60, 60)), (P.arm_m, (255, 150, 0)),
                 (P.head_m, (255, 255, 0)), (P.far_m, (170, 0, 255))):
        tint[m, :3] = (tint[m, :3] * 0.4 + np.array(c) * 0.6).astype(np.uint8)
    tiles = [a, tint, P.unit_canvas, P.body]
    for o in ORIENTS:
        c = np.zeros((128, 128, 4), np.uint8)
        K.put(c, P.body, 0, 0)
        K.place(c, P.orient(o), P.elbow, under=o in ("back_steep", "behind_steep", "raised_back"))
        tiles.append(c)
    z = 5
    W = 128 * z
    img = Image.new("RGB", (4 * (W + 6), 3 * (W + 18)), (40, 40, 40))
    d = ImageDraw.Draw(img)
    names = ["design", "parts", "unit", "body"] + ORIENTS
    for i, (t, nm) in enumerate(zip(tiles, names)):
        tile = Image.new("RGBA", (W, W), (110, 120, 108, 255))
        tile.alpha_composite(Image.fromarray(t).resize((W, W), Image.NEAREST))
        X, Y = (i % 4) * (W + 6), (i // 4) * (W + 18)
        img.paste(tile.convert("RGB"), (X, Y + 16))
        d.text((X + 4, Y + 2), nm, fill=(255, 255, 255))
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
        parts_review(P, os.path.join(a.parts, "viego_parts.png"))
        print("sword", int(P.sword_m.sum()), "hand", int(P.hand_m.sum()), "arm", int(P.arm_m.sum()),
              "head", int(P.head_m.sum()), "far", int(P.far_m.sum()))
        return
    tags = a.tags.split(",") if a.tags else TAGS
    built = {t: frames(P, t) for t in tags}
    for t in tags:
        rows = K.audit(built[t], P.D.a, P.D.outline, P.D.soles)
        print(f"{t:8s}", " ".join(f"[{r['pieces']}p {r['holes']}h {r['orphans']}o {r['area']}]" for r in rows))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, [P.D.a] + built[t]) for t in tags], os.path.join(a.review, "rig_sheet.png"), z=4,
                       soles=P.D.soles)
        return
    bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differ:", bad or "none")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
