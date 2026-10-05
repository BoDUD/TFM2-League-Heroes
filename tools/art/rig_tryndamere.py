#!/usr/bin/env python3
"""Tryndamere's action strips posed from the approved design's own parts (tools/art/rigkit.py; the casting body = the idle's).

    python tools/art/rig_tryndamere.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 delivery (assets/source/tryndamere/codex_strips/) drew the moving parts itself and lost the model: thin
plank arms when he lifts the sword, a stick arm in E, a broken body in the death; its own HANDOFF calls it "未通过视觉验收".
The user: 「codex实在太笨了 ... 我们自己来修复」「修复codex的这些东西」. Every frame here is the design
(tools/art/design_tryndamere.py) with only what the action moves moved - Codex's frames and League's renders (poses.json)
give the poses:
- the back arm with the greatsword in its fist: the design's own squares cut out as ONE rigid unit and turned whole
  about the shoulder by exact quarter turns (rigkit.rot90: raised back, over the head, chopped down in front) - never
  drawn along bones, sheared or resampled, so neither the arm nor the curved blade changes shape (bone-drawn arms and
  a sheared arm: 「左手右手释放技能都变形」); raised back or over the head it goes behind the body;
- the front arm: the design's own arm, a quarter turn up (the raised fist of Q, W and R) or flipped to point
  forward-up (W's thrust), its root under the pauldron;
- the body, the head, the pauldron and both legs stay square for square in every standing frame.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "tryndamere_native.png")
HERO = "tryndamere"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 96), (64, 70)
MS = {"idle": [200] * 6, "run": [125] * 8, "attack": [50, 50, 50, 50, 100, 100], "skill": [44, 44, 44, 44, 44, 47],
      "skill2": [60, 60, 50, 80, 80, 70], "skill_q": [80, 80, 80, 80, 80], "ult": [80, 80, 90, 90, 80, 80],
      "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
TAGS = list(MS)

# ---------------------------------------------------------------------------------------------- parts (canvas rows)
# the greatsword: guard, orb and blade, the hand's squares left out (rows 83-99; right of col 54 below row 90 is the
# near leg)
SWORD = {83: (51, 55), 84: (52, 57), 85: (49, 57), 86: (48, 57), 87: (49, 57), 88: (46, 56), 89: (46, 56),
         90: (46, 55), 91: (44, 54), 92: (45, 54), 93: (44, 53), 94: (43, 52), 95: (42, 51), 96: (41, 50),
         97: (40, 49), 98: (39, 48), 99: (39, 45)}
GRIP = (55.5, 83.5)                    # where the fist holds the sword (x, y)
# the back arm: wraps, bracer and the fist on the grip (the upper arm is behind the shoulder in the idle)
BACK_ARM = {77: (57, 59), 78: (57, 61), 79: (56, 62), 80: (55, 61), 81: (55, 61), 82: (55, 61), 83: (56, 60),
            84: (58, 59)}                 # (rows 81-82 to col 61: the hair's tip that hung in front of the arm)
# the front arm under the pauldron: skin, wraps, bracer and the open clawed hand
FRONT_ARM = {78: (84, 89), 79: (84, 90), 80: (83, 91), 81: (84, 92), 82: (85, 93), 83: (86, 94), 84: (87, 95),
             85: (87, 95), 86: (88, 94)}

SHOULDER = (59.5, 78.0)                # the back arm's root at the torso: the arm + sword unit turns about it
FRONT_PIVOT = (85.0, 78.5)             # the front arm's root under the pauldron


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a
        sword_m = K.mask_rows(SWORD)
        arm_m = K.mask_rows(BACK_ARM)
        front_m = K.mask_rows(FRONT_ARM)
        self.sword_m, self.arm_m, self.front_m = sword_m, arm_m, front_m
        # the sword on its own (thrown in the death) in its four exact diagonal directions, the grip as the joint
        self.dirs = K.orientations(K.Part.from_canvas(a, sword_m, GRIP))
        # the back arm with the sword in its fist as one rigid unit, and the arm alone; the front arm alone
        self.unit = K.Part.from_canvas(a, sword_m | arm_m, SHOULDER)
        self.arm = K.Part.from_canvas(a, arm_m, SHOULDER)
        self.front = {"up": K.rot90(K.Part.from_canvas(a, front_m, FRONT_PIVOT), 3),
                      "fwd": K.Part.from_canvas(a, front_m, FRONT_PIVOT).flip_v()}
        self.body = a.copy()
        self.body[sword_m | arm_m] = 0


# the standing actions, per frame: (back arm + sword: quarter turns clockwise about SHOULDER or None = as drawn,
# front arm: "up" (a quarter turn up) / "fwd" (pointing forward-up) or None, whole-figure shift (dx, dy)) - only exact
# quarter turns / a flip, so neither arm nor blade changes shape (drawn bones and sheared arms looked bent:
# 「左手右手释放技能都变形」); turned back (1) or over the head (2) the unit goes behind the body
STAND = {
    # the overhead chop (release tick 12, frame 5): raised back, over the head, chopped down in front of him
    "attack": [(None, None, (0, 0)), (1, None, (0, 0)), (1, None, (0, 0)), (2, None, (0, 0)), (3, None, (0, 0)),
               (3, None, (0, 0))],
    # E: one turn of the sword round him
    "skill": [(1, None, (0, 0)), (2, None, (0, 0)), (3, None, (0, 0)), (None, None, (0, 0)), (1, None, (0, 0)),
              (None, None, (0, 0))],
    # W: the free fist raised, then thrust at the enemy as he shouts (release frame 4)
    "skill2": [(None, None, (0, 0)), (None, None, (0, 0)), (None, "up", (0, 0)), (None, "fwd", (0, 0)),
               (None, "fwd", (0, 0)), (None, None, (0, 0))],
    # Q: the fist raised as he drinks the fury
    "skill_q": [(None, None, (0, 0)), (None, "up", (0, 0)), (None, "up", (0, 0)), (None, "up", (0, 0)),
                (None, None, (0, 0))],
    # R: the roar - the sword raised back and the fist up
    "ult": [(None, None, (0, 0)), (1, "up", (0, 0)), (1, "up", (0, 0)), (1, "up", (0, 0)), (1, "up", (0, 0)),
            (None, None, (0, 0))],
    "hit": [(None, None, (-1, 0)), (None, None, (0, 0))],
}


def stand(P, pose):
    k, front, (dx, dy) = pose
    c = np.zeros((128, 128, 4), np.uint8)
    K.put(c, P.D.a if k is None else P.body, 0, 0)
    if front:
        c[P.front_m] = 0
        K.place(c, P.front[front], FRONT_PIVOT, under=True)
    if k is not None:
        K.place(c, K.rot90(P.unit, k), SHOULDER, under=k in (1, 2))
    # the pose's shift moves the WHOLE figure, legs included (moving the body over still legs broke the waist)
    return K.shifted(c, dx, dy) if (dx or dy) else c


# the run: the near and far legs (rows: (first, last)) swung about the hips, the boots lifted in turn
NEAR_LEG = {92: (55, 63), 93: (56, 63), 94: (55, 62), 95: (55, 61), 96: (54, 61), 97: (54, 61), 98: (54, 62),
            99: (54, 62)}
FAR_LEG = {92: (81, 88), 93: (81, 88), 94: (81, 88), 95: (82, 86), 96: (81, 86), 97: (80, 88), 98: (80, 89),
           99: (80, 89)}
HIP, ANKLE = 89, 96
# the stance's feet are 26 columns apart: in the run both boots come in under the hips (IN), then swing about there
IN = 7.0
SWING = [5.0, 3.0, 0.0, -3.0, -5.0, -3.0, 0.0, 3.0]
NEAR_LIFT = [0, 0, 0, 0, 0, 2, 3, 2]
FAR_LIFT = [0, 2, 3, 2, 0, 0, 0, 0]
DROP = [1, 0, 0, 0, 1, 0, 0, 0]


def run(P, k):
    a = P.D.a
    near, far = K.mask_rows(NEAR_LEG), K.mask_rows(FAR_LEG)
    trunk = a.copy()
    trunk[near | far] = 0
    s, d = SWING[k], DROP[k]
    c = np.zeros((128, 128, 4), np.uint8)
    K.put(c, K.swing_leg(a, far, HIP, ANKLE, -IN - s, FAR_LIFT[k]), 0, 0)
    K.put(c, K.shifted(trunk, 0, d), 0, 0)
    K.put(c, K.swing_leg(a, near, HIP, ANKLE, IN + s, NEAR_LIFT[k]), 0, 0)
    c[P.D.soles + 1:] = 0
    return c


# the death (League's: the sword flung up, he goes down): no turning, no shearing and no upper body moved over the
# legs (「死亡动画整个模型变形」) - the whole figure staggers back, the sword (the unit turned back, then the blade alone)
# leaves his hand and sticks in the ground behind him, and his knees give a little (CROUCH: leg rows above the boots
# taken out, everything above lowered onto them - a few rows, as Varus kneels)
KNEES = 96                             # the boots' first row: crouching takes leg rows out above it
DEAD = [  # (crouch rows, whole-figure dx, sword: a quarter-turn count = still in the hand, or (grip, direction) free)
    None,
    (0, -1, 1),
    (0, -1, ((47.0, 60.0), "ur")),
    (1, -1, ((44.0, 72.0), "ul")),
    (2, -1, ((45.0, 84.0), "dl")),
    (3, -1, ((45.0, 84.0), "dl")),
    (4, -1, ((45.0, 84.0), "dl")),
    (4, -1, ((45.0, 84.0), "dl")),
]


def crouched(c, n):
    """n rows of the legs above KNEES taken out, everything above them lowered onto the boots."""
    if not n:
        return c
    out = np.zeros_like(c)
    out[KNEES:] = c[KNEES:]
    out[n:KNEES] = c[:KNEES - n]
    return out


def dead(P, k):
    if DEAD[k] is None:
        return stand(P, STAND["hit"][0])
    n, dx, sword = DEAD[k]
    c = K.put(np.zeros((128, 128, 4), np.uint8), P.body, 0, 0)
    if isinstance(sword, int):
        K.place(c, K.rot90(P.unit, sword), SHOULDER, under=True)
    else:
        K.place(c, P.arm, SHOULDER)
    c = crouched(c, n)
    if not isinstance(sword, int):
        K.place(c, P.dirs[sword[1]], sword[0], under=True)
    c[P.D.soles + 1:] = 0
    return K.shifted(c, dx, 0)


def frames(P, tag):
    n = len(MS[tag])
    if tag == "run":
        return [K.finish(run(P, k), P.D.outline, P.D.soles) for k in range(n)]
    if tag == "dead":
        return [K.finish(dead(P, k), P.D.outline, P.D.soles) for k in range(n)]
    if tag in STAND:
        return [K.finish(stand(P, p), P.D.outline, P.D.soles) for p in STAND[tag]]
    return [P.D.a.copy() for _ in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets / GIF to this folder")
    ap.add_argument("--tags", help="comma-separated tags to build (review only)")
    a = ap.parse_args()
    P = Parts()
    tags = a.tags.split(",") if a.tags else TAGS
    built = {t: frames(P, t) for t in tags}
    for t in tags:
        rows = K.audit(built[t], P.D.a, P.D.outline, P.D.soles)
        print(t, " ".join(f"[{r['pieces']}p {r['holes']}h {r['orphans']}o {r['area']}]" for r in rows))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, [P.D.a] + built[t]) for t in tags], os.path.join(a.review, "rig_sheet.png"), z=4,
                       soles=P.D.soles)
        K.review_gif([(t, built[t]) for t in tags], MS, os.path.join(a.review, "rig.gif"), z=4)
        return
    bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differ:", bad or "none")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
