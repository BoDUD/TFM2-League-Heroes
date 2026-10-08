#!/usr/bin/env python3
"""Vladimir's action strips posed from the approved design's own parts (2026-10-08): the casting body = the idle's.

    python tools/art/rig_vladimir.py [--check] [--review DIR]

Codex's step-2 delivery (assets/source/vladimir/codex_strips/) drew every action anew: bodies 3-47% bigger than the
design, the pauldrons and clasps gone in the attack and Q, hands detached from the sleeves (attack 2-4, Q 2 and 4, R 4-5:
pieces of 64-100 squares), the legs not the design's, specks round every frame. The user: 「有奇怪的地方直接帮我修复 我要
完美的」. So, as for Xayah (rig_xayah.py): every frame is the design with only what the action moves moved, nothing ever
resampled (no-deformation rule: translation, quarter turns, mirrors, whole-row shifts, layering):
- each arm (NEAR = image right, FAR = image left) is cut square for square - the sleeve under the pauldron, the cuff
  with its gem, the gauntlet and the claws - with the outline squares that ring it alone; the pauldrons, the clasps,
  the coat, the head and the legs stay the design's;
- arm poses (rigid units turned about the shoulder): HANG (as drawn), OUT (a quarter turn: reaching straight out to
  the side at the shoulder's height), UP (mirrored about the shoulder: raised beside the head), IN (moved up and in:
  the hand pulled to the chest; the far arm goes behind the body);
- whole-figure moves: a lunge or recoil (columns), a sink of the upper body over the fixed legs (rows, layering);
- W: the body sinks into a pool of blood (the design moved down and cut at the pool's surface) - the pool is drawn
  here in the coat's own reds; the death: struck back, then the standing figure turned exactly a quarter
  counter-clockwise about the feet (lying on his back, the head to the left), falling the last rows;
- the run: the design's own legs swung about the hips (whole rows), the arms swinging a column, the body dropping a
  row at each contact (rig_xayah's run).
Each built frame is finished only round what moved (finish_near); the rest stays the design's square for square.
Writes assets/source/native/vladimir_<tag>.png (8x, 96x96 cells, soles on cell row 80) and vladimir_cells.json; then
tools/art/import_native.py. --check compares instead of writing; --review writes a review sheet and GIF.
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
DESIGN = os.path.join(NATIVE, "vladimir_native.png")
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OUT = (0x1D, 0x01, 0x0B)
CELL = (96, 96)
CELL_PIVOT = (49, 69)            # the soles on cell row 80 (the references' feet line)
N4 = ((1, 0), (-1, 0), (0, 1), (0, -1))
N8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)

# the arms' coloured squares, (row, col) on the design canvas
NEAR = {79: [68], 80: [68, 69], 81: [68, 69, 70], 82: [68, 69, 70, 71], 83: [68, 69, 70, 71, 72],
        84: [69, 70, 71, 72, 73], 85: [69, 70, 71, 72, 73], 86: [70, 71, 72, 73], 87: [71, 72, 73, 74, 75, 76],
        88: [72, 74], 89: [72, 75], 90: [75]}
FAR = {78: [57, 58], 79: [56, 57, 58], 80: [56, 57], 81: [55, 56, 57], 82: [54, 55, 56, 57],
       83: [52, 54, 55, 56, 57], 84: [53, 54, 55, 56, 57], 85: [53, 54, 55, 56, 57], 86: [52, 53, 54, 55, 56, 57],
       87: [51, 52, 53, 54, 55, 56], 88: [52, 53, 54, 55, 56], 89: [54, 56], 90: [54, 56]}
NEAR_SHOULDER = (69.0, 79.0)     # (x, y): the top of the near sleeve, under the pauldron
TAIL_FROM = 88                   # the coat-tails swing from here down (whole rows, the hem moving most)
FAR_SHOULDER = (57.5, 78.0)


def design():
    a = np.asarray(Image.open(K.lp(DESIGN)).convert("RGBA"))
    a = (a if a.shape[0] == 128 else a[Z // 2::Z, Z // 2::Z]).copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def squares(spec):
    m = np.zeros((128, 128), bool)
    for r, cols in spec.items():
        m[r, cols] = True
    return m


class Parts:
    def __init__(self):
        d = design()
        self.design = d
        op = d[..., 3] > 0
        ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
        near_c, far_c = squares(NEAR), squares(FAR)
        assert all(op[y, x] and not ink[y, x] for m in (near_c, far_c) for y, x in zip(*np.nonzero(m)))
        body_c = op & ~ink & ~near_c & ~far_c

        def ring(c):
            """The outline squares round the coloured squares c that no body colour square touches."""
            m = np.zeros_like(c)
            for y, x in zip(*np.nonzero(ink)):
                if any(c[y + a, x + b] for a, b in N8) and not any(body_c[y + a, x + b] for a, b in N4):
                    m[y, x] = True
            return m

        self.near_m = near_c | ring(near_c)
        self.far_m = far_c | ring(far_c)
        self.body = d.copy()
        self.body[self.near_m | self.far_m] = 0
        self.near = K.Part.from_canvas(d, self.near_m, NEAR_SHOULDER)
        self.far = K.Part.from_canvas(d, self.far_m, FAR_SHOULDER)
        # the coat-tails' lower halves (left of the trousers / right of them), swung by whole rows (tail flare)
        R_, C_ = np.mgrid[0:128, 0:128]
        body_op = self.body[..., 3] > 0
        self.ltail_m = body_op & (R_ >= TAIL_FROM) & (R_ <= 96) & (C_ <= 59)
        self.rtail_m = body_op & (R_ >= TAIL_FROM) & (R_ <= 96) & (C_ >= 68)
        assert np.array_equal(self.build("hang", "hang"), d)

    def arm(self, which, how):
        u = self.near if which == "near" else self.far
        if how == "hang":
            return u, (0, 0)
        if how == "out":         # reaching out to its side: the near arm to the right, the far arm to the left
            return (K.rot90(u, 3) if which == "near" else K.rot90(u, 1)), (0, 1)
        if how == "up":
            return u.flip_v(), (0, 0)
        if how == "in":          # the hand pulled up toward the chest
            return u, ((-3, -4) if which == "near" else (3, -3))
        raise ValueError(how)

    def build(self, near, far, base=None, near_dy=0, tails=(0, 0)):
        c = (self.body if base is None else base).copy()
        if any(tails):
            src = c.copy()
            c[self.ltail_m | self.rtail_m] = 0
            for m, t in ((self.ltail_m, tails[0]), (self.rtail_m, tails[1])):
                K.put(c, K.swing_leg(src, m, TAIL_FROM - 1, 97, t), 0, 0, under=True)
        u, (dx, dy) = self.arm("far", far)
        K.place(c, u, (FAR_SHOULDER[0] + dx, FAR_SHOULDER[1] + dy), under=(far == "in"))
        u, (dx, dy) = self.arm("near", near)
        K.place(c, u, (NEAR_SHOULDER[0] + dx, NEAR_SHOULDER[1] + dy + near_dy))
        return c


def finish_near(a, ref, pinholes=4):
    """rigkit.finish, but every square more than 2 from a square that differs from `ref` keeps ref's (the design's own
    gaps - the slit between the far sleeve and the coat - stay open)."""
    changed = (a != ref).any(-1)
    near = changed.copy()
    for _ in range(2):
        g = near.copy()
        for dy, dx in N8:
            g |= np.roll(np.roll(near, dy, 0), dx, 1)
        near = g
    out = K.finish(a, OUT, SOLES, keep=~near, pinholes=pinholes)
    out[~near] = a[~near]
    return out


# ------------------------------------------------------------------------------------------------ standing actions
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill_w", "ult", "hit", "dead"]
MS = {"idle": [200] * 6, "run": [120] * 8, "attack": [60, 60, 70, 70, 80, 80], "skill": [60, 60, 70, 70, 90, 90],
      "skill2": [80, 100, 120, 150, 60, 80, 90], "skill_w": [60, 60, 70, 600, 600, 70, 70, 80],
      "ult": [60, 60, 70, 80, 80, 80], "hit": [120, 120], "dead": [100, 100, 100, 120, 120, 150, 200, 500]}
# per frame: (near arm, far arm, whole-figure dx, sink of everything above the shoes, near arm dy, coat-tails' hem dx
# (left, right)); None = the design. The tails stream back on a throw / lunge, flare out on the wide casts.
POSES = {
    "attack": [("in", "hang", 0, 0, 0, (0, 0)), ("up", "hang", -1, 0, 0, (1, 0)), ("out", "hang", 0, 0, 0, (-2, 0)),
               ("out", "hang", 1, 0, 0, (-3, 0)), ("out", "out", 1, 0, 0, (-2, 1)), None],
    "skill": [("in", "hang", 0, 0, 0, (0, 0)), ("up", "hang", -1, 0, 0, (1, 0)), ("out", "hang", 1, 0, 0, (-2, 0)),
              ("out", "hang", 2, 0, 0, (-3, 0)), ("in", "hang", 1, 0, 0, (-2, 0)), None],
    "skill2": [("up", "hang", 0, 0, 0, (0, 0)), ("up", "hang", 0, 0, -1, (-1, 0)), ("up", "hang", 0, 0, 0, (0, 0)),
               ("up", "hang", 0, 0, -1, (-1, 0)), ("in", "in", 0, 1, 0, (0, 0)), ("out", "out", 0, 0, 0, (-2, 2)), None],
    "ult": [("in", "in", 0, 1, 0, (0, 0)), ("in", "in", 0, 2, 0, (1, -1)), ("out", "hang", 0, 1, 0, (-1, 1)),
            ("out", "out", 0, 0, 0, (-2, 2)), ("out", "out", 0, 0, -1, (-3, 3)), None],
    "hit": [("hang", "out", -2, 0, 0, (1, 1)), ("hang", "hang", -1, 0, 0, (0, 0))],
}
SHOE_ROW = 96                   # the shoes and the soles stay put when the body sinks


def sunk(a, n):
    """Everything above SHOE_ROW n rows lower, laid over the shoes (layering: nothing is taken out)."""
    if not n:
        return a
    low = np.zeros_like(a)
    low[SHOE_ROW:] = a[SHOE_ROW:]
    top = np.zeros_like(a)
    top[:SHOE_ROW] = a[:SHOE_ROW]
    return K.put(low, top, 0, n)


def standing(P, pose):
    if pose is None:
        return P.design.copy()
    near, far, dx, sink, ndy, tails = pose
    c = P.build(near, far, near_dy=ndy, tails=tails)
    c = sunk(c, sink)
    c = finish_near(c, sunk(P.design, sink) if (near, far) == ("hang", "hang") else P.design)
    return K.shifted(c, dx, 0) if dx else c


# ------------------------------------------------------------------------------------------------ W: the pool
COL = {k: K.rgb(v) for k, v in {"0": "#1D010B", "a": "#2E010D", "b": "#5D0315", "c": "#910419", "e": "#DA010F",
                                 "v": "#F3909F", "w": "#EC6C80"}.items()}
POOL_ROWS = (95, 99)
# per frame: (sink rows, pool width, bubble phase); None = the design / the build with arms in
POOL = [None, (12, 18, 0), (30, 22, 1), (99, 24, 0), (99, 24, 1), (24, 22, 1), (10, 18, 0), None]


def pool(width, phase):
    """A flat pool of blood on the ground in the coat's reds: an ellipse 5 rows tall (rows 95-99) and `width` wide round
    column 64, a near-black outline, a lit scarlet rim (row 96) with pink glints, mid red, a dark bottom; two bubbles
    whose places swap with `phase`."""
    c = np.zeros((128, 128, 4), np.uint8)
    half = width / 2.0
    spans = {95: half - 4, 96: half - 1.5, 97: half, 98: half - 0.5, 99: half - 3}
    m = np.zeros((128, 128), bool)
    for r, h in spans.items():
        x0, x1 = int(round(64 - h)), int(round(64 + h))
        m[r, x0:x1] = True
    for y, x in zip(*np.nonzero(m)):
        edge = (y in (95, 99)) or not m[y, x - 1] or not m[y, x + 1] or not m[y - 1, x] if y > 95 else True
        if y == 99 or not m[y, x - 1] or not m[y, x + 1] or (y == 95):
            k = "0"
        elif y == 96:
            k = "e"
        elif y == 97:
            k = "c"
        else:
            k = "b"
        c[y, x, :3], c[y, x, 3] = COL[k], 255
    # the rim's first lit squares and two bubbles
    x_left = int(round(64 - spans[96]))
    for x in (x_left + 2, x_left + 3):
        c[96, x, :3] = COL["v"]
    bubbles = [(97, 60), (97, 67)] if phase == 0 else [(97, 62), (98, 66)]
    for y, x in bubbles:
        if m[y, x]:
            c[y, x, :3] = COL["w"]
            if m[y - 1, x] and y - 1 > 95:
                c[y - 1, x, :3] = COL["v"]
    return c


def pool_frame(P, k):
    spec = POOL[k]
    if spec is None:
        return standing(P, ("in", "in", 0, 0, 0, (0, 0))) if k == 0 else P.design.copy()
    sink, width, phase = spec
    body = finish_near(P.build("in", "in"), P.design)
    body = K.shifted(body, 0, sink)
    body[POOL_ROWS[0] + 1:] = 0                      # under the pool's surface nothing of him shows
    c = body
    K.put(c, pool(width, phase), 0, 0)
    return K.finish(c, OUT, SOLES, keep=None, pinholes=2)


# ------------------------------------------------------------------------------------------------ the death
# per frame: (dx, sink, lying: None | rows above the ground)
DEAD = [(-1, 0, None), (-2, 1, None), (-3, 3, None), (-3, 0, 6), (-3, 0, 2), (-3, 0, 0), (-3, 0, 0), (-3, 0, 0)]


def dead(P, k):
    dx, sink, lying = DEAD[k]
    c = P.design.copy()
    if lying is not None:
        fig = K.Part.from_canvas(c, c[..., 3] > 0, (64.0, 100.0))
        t = K.turn(fig, 90)                          # an exact quarter turn: on his back, the head to the left
        c = np.zeros_like(c)
        K.place(c, t, (64.0 + dx + 6, 100.0))
        low = int(np.nonzero(c[..., 3].any(1))[0].max())
        return K.shifted(c, 0, SOLES - lying - low)
    c = sunk(c, sink)
    c = finish_near(c, P.design) if sink else c
    return K.shifted(c, dx, 0)


# ------------------------------------------------------------------------------------------------ the run
# League's pace (vladimir_run: two steps in 0.96 s -> 8 x 120 ms). The design's own lower legs (the knee cuffs, the shins,
# the steel ankle straps, the shoes) swing about the hips under the coat (rigkit.swing_leg: rows above the ankle moved in
# proportion, the shoe moved whole and lifted while it swings). The design stands with its feet 7 columns apart, so they
# could not cross within the ~12-column split the user accepts (run-crossing-root-causes): under the coat both legs come
# in (FAR_IN / NEAR_IN columns), then step 4 forward and 4 back (shoes at most 10 apart), the near foot passing behind the far one.
# The body drops a row at each contact, the arms swing two columns against the legs, the coat-tails sway a column.
FAR_LEG = {92: [60, 61, 62], 93: [60, 61, 62], 94: [60, 61], 96: [60, 61], 97: [59, 60, 61], 98: [59, 60, 61, 62]}
NEAR_LEG = {92: [65, 66, 67], 93: [65, 66, 67], 94: [65, 66], 96: [66, 67], 97: [66, 67, 68], 98: [66, 67, 69, 70]}
FAR_IN, NEAR_IN = 2, -3
HIP, ANKLE = 86, 96
STRIDE = [4, 3, 0, -3, -4, -3, 0, 3]
NEAR_LIFT = [0, 0, 0, 0, 0, 2, 3, 2]
FAR_LIFT = [0, 2, 3, 2, 0, 0, 0, 0]
DROP = [1, 0, 0, 0, 1, 0, 0, 0]
ARM_SWING = [-2, -1, 0, 1, 2, 1, 0, -1]
TAIL_SWAY = [-1, 0, 0, 0, 1, 0, 0, 0]          # the coat-tails' hems, against the body's drop
TAIL_TOP = 86


def run_frames(P):
    d = P.design
    op = d[..., 3] > 0
    ink = op & (d[..., :3] == np.array(OUT, np.uint8)).all(-1)
    far_c, near_c = squares(FAR_LEG), squares(NEAR_LEG)
    other = op & ~ink & ~far_c & ~near_c

    def ring(c):
        m = np.zeros_like(c)
        for y, x in zip(*np.nonzero(ink)):
            if any(c[y + a, x + b] for a, b in N8) and not any(other[y + a, x + b] for a, b in N4):
                m[y, x] = True
        return m

    far_m, near_m = far_c | ring(far_c), near_c | ring(near_c)
    base = P.body.copy()
    base[far_m | near_m] = 0
    R_, C_ = np.mgrid[0:128, 0:128]
    left_tail = (base[..., 3] > 0) & (R_ >= TAIL_TOP) & (C_ <= 59)
    right_tail = (base[..., 3] > 0) & (R_ >= TAIL_TOP) & (C_ >= 67)
    torso = base.copy()
    torso[left_tail | right_tail] = 0
    out = []
    for k in range(len(STRIDE)):
        dr = DROP[k]
        c = np.zeros_like(d)
        K.put(c, K.swing_leg(d, far_m, HIP, ANKLE, FAR_IN - STRIDE[k], FAR_LIFT[k]), 0, 0)
        K.put(c, K.swing_leg(d, near_m, HIP, ANKLE, NEAR_IN + STRIDE[k], NEAR_LIFT[k]), 0, 0)
        for tail in (left_tail, right_tail):
            K.put(c, K.shifted(K.swing_leg(base, tail, TAIL_TOP, 100, TAIL_SWAY[k]), 0, dr), 0, 0)
        K.put(c, K.shifted(torso, 0, dr), 0, 0)
        K.put(c, K.shifted(K.swing_leg(d, P.far_m, 78, 88, -ARM_SWING[k]), 0, dr), 0, 0, under=True)
        K.put(c, K.shifted(K.swing_leg(d, P.near_m, 79, 89, ARM_SWING[k]), 0, dr), 0, 0)
        keep = np.zeros((128, 128), bool)
        keep[:78 + dr] = True                        # the head and shoulders are the design's, a row lower or not
        out.append(K.finish(c, OUT, SOLES, keep=keep, pinholes=4))
    return out


def frames(P, tag):
    if tag == "idle":
        return [P.design.copy() for _ in MS["idle"]]
    if tag == "run":
        return run_frames(P)
    if tag == "skill_w":
        return [pool_frame(P, k) for k in range(len(POOL))]
    if tag == "dead":
        return [dead(P, k) for k in range(len(DEAD))]
    return [standing(P, p) for p in POSES[tag]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write a review sheet and GIF into this folder")
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    P = Parts()
    built = {tag: frames(P, tag) for tag in TAGS}
    for tag in TAGS:
        rows = K.audit(built[tag], P.design, OUT, SOLES)
        print(f"{tag:8s}", " ".join(f"{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}" for r in rows))
    if not a.no_write:
        bad = K.write_strips("vladimir", built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        if a.check:
            print("differs:", bad or "nothing")
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, built[t]) for t in TAGS], os.path.join(a.review, "vladimir_strips_review.png"), z=4,
                       soles=SOLES)
        K.review_gif([(t, built[t]) for t in TAGS], MS, os.path.join(a.review, "vladimir_strips_review.gif"), z=4)


if __name__ == "__main__":
    main()
