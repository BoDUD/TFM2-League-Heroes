#!/usr/bin/env python3
"""Xayah's action strips posed from the approved design's own parts (2026-10-08): the casting body = the idle's.

    python tools/art/rig_xayah.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/xayah/codex_strips/) built every frame by moving the design's parts by script, but
the arms came out as flat slabs (a 1-square skin row between two outline rows, 「白棍」), the far arm a plank floating
beside the body, the feather cloak turned whole into a level bar at head height in standing frames (attack 3-4, E 1-2,
W 2, R 6-7), and the death laid the body flat under an upright head. The user: 「完成下一步 有奇怪的地方你帮忙修复」,
then on the first rebuild 「仔细排查问题 做到完美后联系我」「不要有任何模型变形的问题」「像素缺失也是」. So every frame
here is the design (tools/art/design_xayah.py) with only what the action moves moved, and nothing ever resampled:
- the near arm (image right) is cut off the design square for square (ARM: the skin from the shoulder under the skull,
  the bracer, the hand - 14 squares; BLADES: the two feather blades under the hand - 11 squares; each with the outline
  squares that ring it alone), so the body keeps every square of the tabard and the belt beside it (a box cut took the
  tabard's edge along: 「像素缺失」). Two poses only, both exact: HANG (as drawn) and OUT - the unit transposed about
  the shoulder (a quarter turn and a mirror: the arm reaches out to the side and a little down, the hand at the hip's
  height to the right; a plain quarter turn pointed it up across the bird skull). A wind-up pointing back hid the whole
  arm behind the body and a raised arm covered the face: neither is used. After a throw the blades are off the hand.
- the cloak, the legs and the head are the design's in every standing frame; only the arm and whole-figure moves (a
  column back or forward, Q's hop and R's leap - up to 9 rows, inside the cell - the hit's recoil) change a frame.
- the death never turns her by other than a quarter turn (RotSprite at 30-60 degrees broke the face and the outline):
  struck back three columns, then she lies on her back - the standing figure turned exactly a quarter counter-clockwise
  about her feet, the head to the left (league_rakan's lying death) - falling the last 5 rows onto the ground; the
  blades stay in her hand (dropped beside her they were a loose piece). A kneel (league_varus's: the thighs' rows taken
  out) was tried and cut the blades and the cloak's hem in the same rows.
- the run: Codex's skin swap on oppi's Vayne run (assets/source/xayah/codex_strips/xayah_run.png) bent the legs out of
  shape and left loose cloak squares by them (「腿部还有变形 还有多余的像素」); it is built here from the design's own
  legs (see run_frames()).
Each built frame is finished only round what moved (rigkit.finish with every other square kept): the outline closed on
the moved edges, pinholes filled, stray outline squares dropped; the rest stays the design's square for square (checked).
Writes assets/source/native/xayah_<tag>.png (8x, 128x96 cells) and xayah_cells.json; then tools/art/import_native.py.
--check compares instead of writing; --review writes a review sheet and GIF.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
SRC = os.path.join(ROOT, "assets", "source", "xayah", "codex_strips")
DESIGN = os.path.join(NATIVE, "xayah_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OUT = (0x0B, 0x04, 0x0E)
CELL = (128, 96)
CELL_PIVOT = (64, 69)            # the soles on cell row 80 (the references' feet line)
SHOULDER = (75.5, 80.5)          # the centre of the arm's top square, under the bird skull
# (row, column) on the design canvas
ARM = [(80, 75), (81, 75), (81, 76), (82, 76), (82, 77), (83, 77), (84, 77), (84, 78), (85, 78), (86, 78), (86, 79),
       (87, 78), (87, 79), (88, 79)]
BLADES = [(89, 79), (89, 80), (89, 81), (90, 79), (90, 80), (90, 82), (91, 79), (91, 80), (91, 82), (92, 80), (93, 80)]
HIP = 88                         # the kneel takes rows out from HIP + 1 down (the thighs)
TAGS = ["idle", "run", "attack", "skill", "skill_e", "skill2", "ult", "hit", "dead"]
MS = {"idle": [140] * 8, "run": [109] * 8, "attack": [70, 70, 80, 70, 60, 50], "skill": [70, 70, 80, 80],
      "skill_e": [80, 80, 90, 83], "skill2": [100] * 4, "ult": [120, 130, 150, 200, 200, 150, 120, 97],
      "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
# per frame: (arm "hang" | "out", blades in the hand, dx, lift); None = the design itself
POSES = {
    "attack": [("hang", True, 0, 0), ("hang", True, -1, 0), ("out", False, 1, 0), ("out", False, 1, 0),
               ("hang", True, 0, 0), None],
    "skill": [("hang", True, 0, 0), ("hang", True, 0, 2), ("out", False, 1, 1), None],
    "skill_e": [("out", False, 0, 0), ("hang", False, 0, 0), ("hang", True, 0, 0), None],
    "skill2": [("hang", True, 0, 0), ("out", True, 1, 0), ("hang", True, 0, 0), None],
    "ult": [("hang", True, 0, 0), ("hang", True, 0, 3), ("hang", True, 0, 7), ("hang", True, 0, 9),
            ("hang", True, 0, 9), ("out", False, 1, 5), ("hang", False, 0, 2), None],
    "hit": [("hang", True, -2, 0), ("hang", True, -1, 0)],
}
# per frame: (dx, blades in the hand, kneel rows, lying: None | rows above the ground)
DEAD = [(-1, True, 0, None), (-2, True, 0, None), (-3, True, 0, None), (-3, True, 0, 5), (-3, True, 0, 2),
        (-3, True, 0, 0), (-3, True, 0, 0), (-3, True, 0, 0)]
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)


def lp(p):
    return K.lp(p)


def design():
    a = np.asarray(Image.open(lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
        arm_c = np.zeros((128, 128), bool)
        blade_c = np.zeros((128, 128), bool)
        for y, x in ARM:
            arm_c[y, x] = True
        for y, x in BLADES:
            blade_c[y, x] = True
        assert all(op[y, x] and not ink[y, x] for y, x in ARM + BLADES)
        body_c = op & ~ink & ~arm_c & ~blade_c

        def ring(c):
            """The outline squares round the coloured squares c that no body colour square touches."""
            m = np.zeros_like(c)
            for y, x in zip(*np.nonzero(ink)):
                if any(c[y + a, x + b] for a, b in N8) and not any(body_c[y + a, x + b] for a, b in N4):
                    m[y, x] = True
            return m

        blade_ring = ring(blade_c) & ~ring(arm_c)
        self.arm_m = arm_c | (ring(arm_c) & ~blade_ring)
        self.blade_m = blade_c | blade_ring
        self.unit_m = self.arm_m | self.blade_m
        self.body = d.copy()
        self.body[self.unit_m] = 0
        self.with_blades = K.Part.from_canvas(d, self.unit_m, SHOULDER)
        self.bare = K.Part.from_canvas(d, self.arm_m, SHOULDER)
        self.blades = K.Part.from_canvas(d, self.blade_m, (80.0, 91.0))
        assert np.array_equal(self.put_arm("hang", True), d)


    def put_arm(self, how, blades, base=None):
        u = self.with_blades if blades else self.bare
        if how == "out":
            u = K.rot90(u, 3).flip_v()
        c = (self.body if base is None else base).copy()
        K.place(c, u, SHOULDER)
        return c


def finish_near(a, ref, pinholes=4):
    """rigkit.finish, but every square more than 2 from a square that differs from `ref` (the design, or the frame's
    unmoved source) is kept as it is."""
    changed = (a != ref).any(-1)
    near = changed.copy()
    for _ in range(2):
        g = near.copy()
        for dy, dx in N8:
            g |= np.roll(np.roll(near, dy, 0), dx, 1)
        near = g
    return K.finish(a, OUT, SOLES, keep=~near, pinholes=pinholes)


def standing(P, pose):
    if pose is None:
        return P.design.copy()
    how, blades, dx, lift = pose
    c = finish_near(P.put_arm(how, blades), P.design)
    return K.shifted(c, dx, -lift) if dx or lift else c


def kneeled(a, n):
    """Everything above the thighs n rows lower, rows HIP+1 .. HIP+n taken out (league_varus's kneel)."""
    if not n:
        return a
    out = np.zeros_like(a)
    out[HIP + 1 + n:] = a[HIP + 1 + n:]
    top = np.zeros_like(a)
    top[:HIP + 1] = a[:HIP + 1]
    return K.put(out, top, 0, n)


def dead(P, k):
    dx, blades, kneel, lying = DEAD[k]
    c = finish_near(P.put_arm("hang", blades), P.design)
    if lying is not None:
        fig = K.Part.from_canvas(c, c[..., 3] > 0, (64.0, 100.0))
        t = K.turn(fig, 90)                                   # an exact quarter turn
        c = np.zeros_like(c)
        K.place(c, t, (64.0 + dx + 4, 100.0))
        low = int(np.nonzero(c[..., 3].any(1))[0].max())
        c = K.shifted(c, 0, SOLES - lying - low)
    else:
        c = K.shifted(kneeled(c, kneel), dx, 0)
        if kneel:
            c = finish_near(c, K.shifted(kneeled(P.put_arm("hang", blades), kneel), dx, 0))
    return c


# ----------------------------------------------------------------------------------------------- the run
# League's pace (Xayah_run, 0.87 s: 8 x 109 ms). The design stands with its hips 7.5 columns apart and the far leg
# slanting 4 columns out (run-crossing-root-causes: a front-ish stance whose feet cannot cross without slanting the legs
# into stairs), so the run walks on two copies of the design's own NEAR leg (LEG_C: its navy and mauve squares from row
# 89 down, columns 71-77, with its own outline ring and the talon tip) - the far one FAR_DX columns left of it, behind it
# and one shade darker (FAR_DARK, the leg's own darker colours; league_taric's far leg) - each leg sheared about its top
# row (every row moved whole, the boot from the ankle down moved whole and lifted while it swings: league_varus's and
# league_twistedfate's walk). Feet: STRIDE (near; the far leg the opposite), the near foot 12 ahead at the widest and 4
# behind when they cross, never more than 12 apart. The body (cloak, torso, head) drops a row at each contact (DROP);
# the near arm swings a column against the near leg (ARM_SWING: its rows sheared about the shoulder, the blades with it).
TOP, ANKLE = 89, 97
LEG_COLOURS = {(0x1A, 0x12, 0x36), (0x28, 0x25, 0x5F), (0x71, 0x47, 0x59), (0x98, 0x64, 0x71)}
FAR_DARK = {(0x28, 0x25, 0x5F): (0x1A, 0x12, 0x36), (0x98, 0x64, 0x71): (0x71, 0x47, 0x59)}
TALON = (98, 78)
FAR_DX = -4
STRIDE = [4, 2, 0, -2, -4, -2, 0, 2]
NEAR_LIFT = [0, 0, 0, 0, 0, 1, 2, 1]
FAR_LIFT = [0, 1, 2, 1, 0, 0, 0, 0]
DROP = [1, 0, 0, 0, 1, 0, 0, 0]
ARM_SWING = [-1, -1, 0, 1, 1, 1, 0, -1]


def leg_masks(P):
    d = P.design
    op = d[..., 3] > 0
    ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
    R, C = np.mgrid[0:128, 0:128]
    leg_c = np.zeros((128, 128), bool)
    for y, x in zip(*np.nonzero(op & ~ink)):
        if tuple(int(v) for v in d[y, x, :3]) in LEG_COLOURS:
            leg_c[y, x] = True
    near_c = leg_c & ~P.unit_m & (R >= TOP) & (C >= 71) & (C <= 77)
    far_c = leg_c & (R >= 88) & (C >= 62) & (C <= 69)
    other = op & ~ink & ~near_c & ~far_c & ~P.unit_m

    def ring(c):
        m = np.zeros_like(c)
        for y, x in zip(*np.nonzero(ink & ~P.unit_m)):
            if any(c[y + a, x + b] for a, b in N8) and not any(other[y + a, x + b] for a, b in N4):
                m[y, x] = True
        return m

    near_m = near_c | ring(near_c)
    near_m[TALON] = True
    return near_m, far_c | ring(far_c)


def sheared(src, dx, off, lift, drop, top=TOP, ankle=ANKLE):
    """A leg: rows top..ankle moved off * (row - top) / (ankle - top) (whole rows) and down `drop`; the boot under the
    ankle moved off whole and up `lift`."""
    shin = np.zeros_like(src)
    boot = np.zeros_like(src)
    for y, x in zip(*np.nonzero(src[..., 3] > 0)):
        if y <= ankle:
            sh = int(np.floor(off * (y - top) / (ankle - top) + 0.5))
            yy, tgt = y + drop, shin
        else:
            sh, yy, tgt = off, y - lift, boot
        if 0 <= yy < 128 and 0 <= x + dx + sh < 128:
            tgt[yy, x + dx + sh] = src[y, x]
    return K.put(shin, boot, 0, 0)


# ----------------------------------------------------------------------------------------------- the idle's breath
# idle_breathe (import_native's last step) sinks the body by taking rows out of the shins wherever a row is (nearly)
# like the one under it; Xayah's leg wraps are striped every 2-3 rows, so its cut changed 11 squares and its 1-column
# lean 9: the legs came out shorter, their stripes out of step (「腿部还有变形」). Her breath here leaves both legs as
# drawn and lays everything above them - torso, head, arms, the cloak down to CLOAK_ROW - a row lower over them in
# BREATH_SINK (the tabard covers a row more of the thighs; nothing is taken out); the cloak's hem from CLOAK_ROW down
# rests on the ground (its tips touch the soles' row) and only drifts back a column in BREATH_CLOAK (whole rows moved),
# the cloak above it sinking over its top row. 8 x 140 ms, the base game's pace. import_native skips its own breath for her.
BREATH_SINK = [0, 0, 1, 1, 1, 1, 0, 0]
BREATH_CLOAK = [0, 0, 0, -1, -1, -1, 0, 0]
CLOAK_ROW = 90


def layers(P):
    """(the cloak below the hips, both legs, the rest) of the design: the legs as leg_masks cuts them."""
    d = P.design
    near_m, far_m = leg_masks(P)
    legs = np.zeros_like(d)
    legs[near_m | far_m] = d[near_m | far_m]
    upper = d.copy()
    upper[near_m | far_m] = 0
    R, C = np.mgrid[0:128, 0:128]
    cloak_m = (upper[..., 3] > 0) & (C <= 63) & (R >= 84)
    cloak = upper.copy()
    cloak[~cloak_m] = 0
    rest = upper.copy()
    rest[cloak_m] = 0
    return cloak, legs, rest


def breath_frames(P):
    cloak, legs, rest = layers(P)
    out = []
    for sink, drift in zip(BREATH_SINK, BREATH_CLOAK):
        if not sink and not drift:
            out.append(P.design.copy())
            continue
        c = np.zeros_like(P.design)
        hem = cloak.copy()
        hem[:CLOAK_ROW] = 0
        top = cloak.copy()
        top[CLOAK_ROW:] = 0
        K.put(c, K.shifted(hem, drift, 0), 0, 0)          # the hem rests on the ground: it never sinks
        K.put(c, legs, 0, 0)
        K.put(c, K.shifted(top, 0, sink), 0, 0)           # the rest of the cloak sinks over the hem's top row
        K.put(c, K.shifted(rest, 0, sink), 0, 0)
        ref = np.zeros_like(c)
        K.put(ref, hem, 0, 0)
        K.put(ref, legs, 0, 0)
        K.put(ref, K.shifted(top, 0, sink), 0, 0)
        K.put(ref, K.shifted(rest, 0, sink), 0, 0)
        out.append(finish_near(c, ref))
    return out


def run_frames(P):
    d = P.design
    near_m, far_m = leg_masks(P)
    upper = d.copy()
    upper[near_m | far_m | P.unit_m] = 0
    R, C = np.mgrid[0:128, 0:128]
    cloak_m = (upper[..., 3] > 0) & (C <= 63) & (R >= 84)
    cloak = upper.copy()
    cloak[~cloak_m] = 0
    torso = upper.copy()
    torso[cloak_m] = 0
    near = np.zeros_like(d)
    near[near_m] = d[near_m]
    far = near.copy()
    for a, b in FAR_DARK.items():
        m = (near[..., :3] == np.array(a, np.uint8)).all(-1) & (near[..., 3] > 0)
        far[m, :3] = b
    arm = np.zeros_like(d)
    arm[P.unit_m] = d[P.unit_m]
    out = []
    for k in range(len(STRIDE)):
        dr = DROP[k]
        c = np.zeros_like(d)
        hem = cloak.copy()
        hem[:CLOAK_ROW] = 0
        top = cloak.copy()
        top[CLOAK_ROW:] = 0
        K.put(c, hem, 0, 0)                               # the hem rests on the ground
        K.put(c, sheared(far, FAR_DX, -STRIDE[k], FAR_LIFT[k], dr), 0, 0)
        K.put(c, sheared(near, 0, STRIDE[k], NEAR_LIFT[k], dr), 0, 0)
        K.put(c, K.shifted(top, 0, dr), 0, 0)
        K.put(c, K.shifted(torso, 0, dr), 0, 0)
        swing = sheared(arm, 0, ARM_SWING[k], 0, 0, top=80, ankle=93)
        K.put(c, K.shifted(swing, 0, dr), 0, 0)
        keep = np.zeros((128, 128), bool)
        keep[:80 + dr] = True                            # the head and shoulders are the design's, a row lower or not
        keep[TALON[0] - NEAR_LIFT[k], TALON[1] + STRIDE[k]] = True     # the talon tip rides the near foot
        out.append(K.finish(c, OUT, SOLES, keep=keep))
    return out


def frames(P, tag):
    if tag == "idle":
        return breath_frames(P)
    if tag == "run":
        return run_frames(P)
    if tag == "dead":
        return [dead(P, k) for k in range(len(MS[tag]))]
    return [standing(P, p) for p in POSES[tag]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    a = ap.parse_args()
    P = Parts()
    built = {tag: frames(P, tag) for tag in TAGS}
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['area']}" for r in rows))
    bad = K.write_strips("xayah", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
    if a.check:
        print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "xayah_strips_review.png"), z=3,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], MS, os.path.join(a.review, "xayah_strips_review.gif"), z=3)
    sys.exit(1 if a.check and bad else 0)


if __name__ == "__main__":
    main()
