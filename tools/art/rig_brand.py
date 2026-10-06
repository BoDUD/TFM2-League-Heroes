#!/usr/bin/env python3
"""Brand's action strips posed from the approved design's own parts (tools/art/rigkit.py; the casting body = the idle's).

    python tools/art/rig_brand.py [--check] [--review DIR] [--tags attack,skill]

Codex's step-2 delivery (assets/source/brand/codex_strips/) rigged the design itself, but turned the arms by any angle
(ragged nearest-neighbour arms), pressed both legs into one column in five run frames and spread them flat in W's slam
and R's leap, and laid the dead body diagonally with the feet in the air. The user: 「有问题的地方你帮忙修复就行了」.
Every frame here is the design (tools/art/design_brand.py, 「A 37」) with only what the action moves moved, League's
clips (assets/source/brand/poses.json) and Codex's frames giving the poses:
- each arm with its fire hand is the design's own squares cut out below the shoulder as ONE rigid unit and turned whole
  about the shoulder by exact quarter turns (rigkit.rot90) - never drawn along bones, sheared or resampled
  (rigid-limb rule, Tryndamere); the shoulders stay on the body;
- the head, the torso, the trousers and both legs stay square for square in every standing frame; a crouch takes leg
  rows out above the feet (everything above lowered onto them), a hop lifts the whole figure;
- the run: both legs below the hips swung in turn under the body (rigkit.swing_leg), the far (back) leg a shade
  darker, a crossing stride, the body bobbing a row;
- the death (league_sivir's): struck, knocked back, the whole figure turned 45 degrees about the feet (RotSprite), then
  lying flat at 90 degrees, the head to the left.
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
DESIGN = os.path.join(NATIVE, "brand_native.png")
HERO = "brand"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 96), (64, 70)
MS = {"idle": [200] * 6, "run": [167, 167, 166, 167, 167, 166], "attack": [60, 60, 60, 70, 80, 100], "skill": [50, 60, 70, 80, 80, 100],
      "skill2": [40, 60, 70, 60, 60, 70, 80, 100], "ult": [50, 60, 70, 80, 100, 120], "hit": [100, 100],
      "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
TAGS = list(MS)

# ---------------------------------------------------------------------------------------------- parts (canvas rows)
# the back arm (image left) below the shoulder: the forearm and the fire hand hanging down-left
BACK_ARM = {76: (52, 56), 77: (50, 55), 78: (49, 54), 79: (49, 53), 80: (48, 53), 81: (48, 51), 82: (47, 52),
            83: (47, 52), 84: (46, 54), 85: (46, 53), 86: (47, 52), 87: (47, 50)}
# the front arm (image right) below the shoulder: the forearm and the fire hand hanging down-right
FRONT_ARM = {77: (71, 74), 78: (70, 75), 79: (69, 75), 80: (69, 76), 81: (71, 77), 82: (71, 79), 83: (71, 79),
             84: (73, 80), 85: (77, 82), 86: (76, 82), 87: (76, 82), 88: (79, 81), 89: (80, 80)}
BACK_SHOULDER = (55.0, 76.0)
FRONT_SHOULDER = (71.5, 77.0)
# the legs: each a rigid unit from the hip (the trousers' thigh) to the sole, turned about its hip (RotSprite)
BACK_LEG = {89: (51, 57), 90: (51, 56), 91: (51, 57), 92: (50, 57), 93: (51, 57), 94: (51, 55), 95: (51, 55),
            96: (51, 53), 97: (50, 53), 98: (48, 53), 99: (48, 53)}
FRONT_LEG = {89: (64, 77), 90: (64, 77), 91: (68, 76), 92: (67, 77), 93: (66, 77), 94: (66, 78), 95: (70, 77),
             96: (72, 76), 97: (72, 77), 98: (71, 78), 99: (70, 79)}
BACK_HIP, FRONT_HIP = (55.0, 89.0), (70.0, 89.0)
BACK_TILT, FRONT_TILT = -24.0, 29.0    # the design's legs from the vertical (+ = the foot forward, to the right)
KNEES = 94                             # a crouch takes rows out above it


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a
        self.back_m, self.front_m = K.mask_rows(BACK_ARM), K.mask_rows(FRONT_ARM)
        self.back = K.Part.from_canvas(a, self.back_m, BACK_SHOULDER)
        self.front = K.Part.from_canvas(a, self.front_m, FRONT_SHOULDER)
        self.body = a.copy()
        self.body[self.back_m | self.front_m] = 0
        self.back_leg_m, self.front_leg_m = K.mask_rows(BACK_LEG), K.mask_rows(FRONT_LEG)
        self.back_leg = K.Part.from_canvas(a, self.back_leg_m, BACK_HIP)
        self.front_leg = K.Part.from_canvas(a, self.front_leg_m, FRONT_HIP)
        self.trunk = a.copy()
        self.trunk[self.back_leg_m | self.front_leg_m] = 0
        op = a[..., 3] > 0
        arms = self.back_m | self.front_m
        rows = np.arange(128)[:, None]
        cols = np.arange(128)[None, :]
        low = op & ~arms & (rows >= LEG_ROWS[0])
        front = low & (cols >= LEG_COLS[0]) & (cols <= LEG_COLS[1])
        back = low & (cols <= 58)
        self.run_trunk = a.copy()
        self.run_trunk[front | back] = 0
        self.leg = np.zeros_like(a)               # the upright leg, its hip on column LEG_HIP
        for rr, d in UPRIGHT.items():
            for y in rr:
                xs = np.nonzero(front[y])[0]
                self.leg[y, xs + d] = a[y, xs]


def figure(P, back, front, dx=0, dy=0, crouch=0):
    """The body with the arms turned by quarter turns (None = as drawn); raised arms go behind the body."""
    c = K.put(np.zeros((128, 128, 4), np.uint8), P.body, 0, 0)
    for part, k, at in ((P.back, back, BACK_SHOULDER), (P.front, front, FRONT_SHOULDER)):
        K.place(c, K.rot90(part, k or 0), at, under=k in (1, 2))
    c = crouched(c, crouch)
    return K.shifted(c, dx, dy) if (dx or dy) else c


def crouched(c, n):
    """n rows of the legs above KNEES taken out, everything above them lowered onto the feet."""
    if not n:
        return c
    out = np.zeros_like(c)
    out[KNEES:] = c[KNEES:]
    out[n:KNEES] = c[:KNEES - n]
    return out


# (back arm quarter turns clockwise, front arm quarter turns, dx, dy, crouch rows): 1 turns a hanging arm up and
# back, 2 over the head, 3 forward; dy < 0 lifts the whole figure (a hop)
STAND = {
    # the fireball throw (release frame 4): the front hand raised high, then whipped down and forward
    "attack": [(None, None, 0, 0, 0), (None, 3, -1, 0, 0), (None, 3, -1, 0, 0), (None, None, 2, 0, 0),
               (None, None, 1, 0, 0), (None, None, 0, 0, 0)],
    # W: both hands raised high, then slammed down to the ground in a crouch (release frame 4)
    "skill": [(None, None, 0, 0, 0), (1, 3, 0, -1, 0), (1, 3, 0, -1, 0), (None, None, 1, 0, 3), (None, None, 1, 0, 3),
              (None, None, 0, 0, 0)],
    # E -> Q: the hands gathered, flung wide (E, frame 3); the front hand drawn back and thrust out (Q, frame 6)
    "skill2": [(None, None, 0, 0, 0), (3, 1, 0, 0, 0), (1, 3, 0, 0, 0), (None, 2, -1, 0, 0), (None, 2, -1, 0, 0),
               (None, 3, 1, 0, 0), (None, None, 1, 0, 0), (None, None, 0, 0, 0)],
    # R: a crouch, a leap with the hands gathered, flung wide in the air (frame 4), down again
    "ult": [(None, None, 0, 0, 1), (3, 1, 0, -2, 0), (3, 1, 0, -3, 0), (1, 3, 0, -4, 0), (1, 3, 0, -2, 0),
            (None, None, 0, 0, 0)],
    "hit": [(None, None, -2, 0, 0), (None, None, -1, 0, 0)],
}


def stand(P, pose):
    back, front, dx, dy, cr = pose
    return figure(P, back, front, dx, dy, cr)


# the run (League's 1.0 s cycle): a CROSSING stride on ONE leg - the design's front leg (the trouser thigh with the seat
# above it, the torn hem at the knee, the shin and the bare foot) stood upright by moving whole row blocks sideways
# (never turned or resampled: RotSprite bent the knee's hem, 「裤子膝盖那里严重模型变形」) - used for both legs, the far
# one a shade darker; both hips under the body, the feet swung forward and back in turn so they cross at the half
# cycles (「不是交叉步」), the knee, shin and foot blocks moved whole (thigh 0, knee 0.4, shin 0.7, foot 1.0 of the
# foot's offset), the swinging foot lifted, the trunk a row lower on the passing frames
LEG_ROWS = (85, 99)
LEG_COLS = (64, 79)                    # the front leg (and the seat above it) on the design, the arm left out
UPRIGHT = {range(85, 91): 0, range(91, 95): -1, range(95, 97): -2, range(97, 100): -3}
BLOCKS = {range(85, 91): 0.0, range(91, 95): 0.4, range(95, 97): 0.7, range(97, 100): 1.0}
LEG_HIP = 70                           # the upright leg's hip column on the design
HIPS = (61, 67)                        # the far and near hips' columns in the run
FOOT = [5, 3, 0, -3, -5, -3, 0, 3]     # the near foot's offset (+ = forward); the far foot's is the opposite
NEAR_LIFT = [0, 0, 0, 0, 0, 1, 2, 1]
FAR_LIFT = [0, 1, 2, 1, 0, 0, 0, 0]
BOB = [0, 0, 1, 0, 0, 0, 1, 0]
RUN_UP = 0
IN = 4.0                               # the death's straightened legs: the hips brought in


def darker(part, P):
    """The far leg one shade darker: every colour to the nearest darker colour of the palette (the outline kept)."""
    pal = P.D.palette
    lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    out = part.copy()
    op = part[..., 3] > 0
    for c in {tuple(int(v) for v in p[:3]) for p in part[op]}:
        if c == tuple(P.D.outline):
            continue
        cand = [q for q in pal if lum(q) < lum(c) and q != tuple(P.D.outline)]
        if cand:
            q = min(cand, key=lambda q: sum((int(q[i]) - c[i]) ** 2 for i in range(3)))
            out[op & (part[..., :3] == np.array(c, np.uint8)).all(-1), :3] = q
    return out


def legs_at(P, back_deg, front_deg, inn, dy=0, dark=True, arms_down=False, trunk=None):
    """The trunk on two legs at these angles from the vertical (+ = foot forward), the hips moved `inn` inward; the
    lowest foot on the soles' row. arms_down: both arms turned to hang straight along the body (the death)."""
    c = np.zeros((128, 128, 4), np.uint8)
    trunk = P.trunk if trunk is None else trunk
    if arms_down:
        trunk = trunk.copy()
        trunk[P.back_m | P.front_m] = 0
        K.place(trunk, K.turn(P.back, 40), BACK_SHOULDER)
        K.place(trunk, K.turn(P.front, -40), FRONT_SHOULDER)
    bl = K.turn(P.back_leg, back_deg - BACK_TILT)
    fl = K.turn(P.front_leg, front_deg - FRONT_TILT)
    legs = np.zeros_like(c)
    K.place(legs, bl, (BACK_HIP[0] + inn, BACK_HIP[1]))
    if dark:
        legs = darker(legs, P)
    K.place(legs, fl, (FRONT_HIP[0] - inn, FRONT_HIP[1]))
    # the lowest COLOURED row + 1 on the soles' row (RotSprite leaves stray outline corners below the feet)
    col = (legs[..., 3] > 0) & ~(legs[..., :3] == np.array(P.D.outline, np.uint8)).all(-1)
    low = int(np.nonzero(col.any(1))[0].max()) + 1
    legs = K.shifted(legs, 0, P.D.soles - low)
    legs[P.D.soles + 1:] = 0
    K.put(c, legs, 0, 0)
    # the trunk at the idle's height (the straightened legs are longer: their thigh tops go under the trousers' seat),
    # dy rows lower
    K.put(c, K.shifted(trunk, 0, RUN_UP + dy), 0, 0)
    return c


def placed_leg(P, hip, foot, lift):
    """The upright leg with its hip on column `hip`, its blocks moved toward the foot's offset, the foot lifted."""
    out = np.zeros_like(P.leg)
    for rr, f in BLOCKS.items():
        d = int(round(foot * f)) + hip - LEG_HIP
        up = lift if f >= 0.7 else (lift // 2 if f > 0 else 0)
        for y in rr:
            xs = np.nonzero(P.leg[y, :, 3])[0]
            if len(xs):
                out[y - up, xs + d] = P.leg[y, xs]
    return out


# the run that went in (the user: 「换腿包给 Codex」): Codex's leg redraw on oppi's Brand run as the skeleton
# (tools/art/pack_brand_run.py, assets/source/brand/RUN_SWAP.md), the design's upper body pasted unchanged by Codex,
# 6 frames over League's 1.0 s; the near trouser leg's main colour (Codex's copper #CD7D2B) back to the idle's
# trousers #AA784B (run legs in the idle's colours)
CODEX_RUN = os.path.join(ROOT, "assets", "source", "brand", "codex_run", "brand_run_1x.png")
RUN_RECOLOUR = {(205, 125, 43): (170, 120, 75)}


# Codex's legs started right under the belt, 9-10 squares wide against the belt's 15 and 2-3 squares right of its middle:
# the wide upper body sat on two thin legs (「移动时身体和腿完全分离」). The join is the idle's own: its trouser seat
# (SEAT_ROWS under the belt, the hips with the copper flap) under the belt in every frame, riding the bob, and Codex's
# legs below it, moved whole under the seat's middle
SEAT_ROWS = (85, 86)
SEAT_COLS = (54, 72)
SEAT = {85: (55, 69), 86: (56, 68)}    # the belt spans columns 55-69: wider, the seat's ends stuck out like the strip
SEAT_MID = 62.5
# the arms swing with the stride (「上半身太僵」): each arm the design's own unit moved whole, opposite to the leg on its
# side - Codex's frame 1 has the near (front) leg forward, frame 4 the far one -, never turned or stretched
# the right edge from the waist to the legs one straight line (Varus's 「对齐」): the waist (rows 79-82) ends on column 67,
# the belt and the seat stuck out to 68-69 over the straight legs - trimmed to it, the outline on column EDGE
EDGE, EDGE_ROWS = 67, (83, 86)
# moved whole sideways an arm tore off its shoulder or sank into the body (「右手臂有点变形 走动的时候」), turned a few
# degrees its forearm went jagged (「修这里啊」): each arm, the design's own squares untouched, is only lifted a row
# while it swings forward (its top then lies over the shoulder, never off it)
FRONT_LIFT = [0, 0, 0, 1, 1, 0]        # rows up (Codex's frame 4: the far leg forward, the near arm forward)
BACK_LIFT = [1, 1, 0, 0, 0, 0]


def run(P, k):
    from PIL import Image
    sheet = np.asarray(Image.open(K.lp(CODEX_RUN)).convert("RGBA"))
    cw, ch = CELL
    cell = sheet[(k // 4) * ch:(k // 4 + 1) * ch, (k % 4) * cw:(k % 4 + 1) * cw]
    c = np.zeros((128, 128, 4), np.uint8)
    c[PIVOT[1] - CELL_PIVOT[1]:PIVOT[1] - CELL_PIVOT[1] + ch] = cell
    c[c[..., 3] < 128] = 0
    for src, dst in RUN_RECOLOUR.items():
        m = (c[..., 3] > 0) & (c[..., :3] == np.array(src, np.uint8)).all(-1)
        m[:86] = False
        c[m, :3] = dst
    bob = int(np.nonzero(c[..., 3].any(1))[0].min()) - P.D.top      # the upper body's drop this frame (0 / 1)
    from design_brand import CHIN                                       # Codex pasted the design before the chin fix
    for (y, x), rgb in CHIN.items():
        c[y + bob, x, :3] = rgb
    arms = np.roll(P.back_m | P.front_m, bob, axis=0)
    rows = np.arange(128)[:, None]
    cols = np.arange(128)[None, :]
    legs_m = (c[..., 3] > 0) & ~arms & (rows >= SEAT_ROWS[0] + bob) & (cols >= SEAT_COLS[0] - 6)
    legs = np.zeros_like(c)
    legs[legs_m] = c[legs_m]
    body = c.copy()
    body[legs_m] = 0
    legs[:SEAT_ROWS[1] + bob + 1] = 0                                   # the seat takes their top rows
    top = SEAT_ROWS[1] + bob + 1
    xs = np.nonzero(legs[top:top + 2, :, 3].any(0))[0]
    d = int(round(SEAT_MID - (xs.min() + xs.max() + 1) / 2.0))
    out = K.put(body, K.shifted(legs, d, 0), 0, 0)
    seat = np.zeros_like(c)
    sm = np.zeros(c.shape[:2], bool)
    for r, (c0, c1) in SEAT.items():                                   # as wide as the belt, the lower row a column in
        sm[r, c0:c1 + 1] = True
    sm &= (P.D.a[..., 3] > 0) & ~(P.back_m | P.front_m)
    seat[sm] = P.D.a[sm]
    K.put(out, K.shifted(seat, 0, bob), 0, 0)
    arms_now = np.roll(P.back_m | P.front_m, bob, axis=0)
    for r in range(EDGE_ROWS[0] + bob, EDGE_ROWS[1] + bob + 1):
        for x in range(EDGE, 128):
            if out[r, x, 3] and not arms_now[r, x]:
                if x == EDGE:
                    out[r, x, :3] = P.D.outline
                else:
                    out[r, x] = 0
    # the arms swung: cut from the frame (the design's, dropped by the bob) and put back a row higher, over the body
    for m, up in ((np.roll(P.back_m, bob, axis=0), BACK_LIFT[k]), (np.roll(P.front_m, bob, axis=0), FRONT_LIFT[k])):
        if not up:
            continue
        m = m & (out[..., 3] > 0)
        arm = np.zeros_like(out)
        arm[m] = out[m]
        out[m] = 0
        K.put(out, K.shifted(arm, 0, -up), 0, 0)
    return out


# the death (league_sivir's): struck, knocked back, 45 degrees about the feet, then lying flat (90), the head left
def dead(P, k):
    if k == 0:
        return stand(P, STAND["hit"][0])
    if k == 1:
        return K.shifted(figure(P, 1, 3, 0, 0), -3, 0)
    # the falling and lying body: straight legs under him, the arms hanging along his sides
    body = legs_at(P, 0.0, 0.0, IN, dark=False, arms_down=True)
    ys, xs = np.nonzero(body[..., 3] > 0)
    feet = (float(xs[ys == ys.max()].mean()) + 0.5, float(P.D.soles + 1))
    deg = {2: 45}.get(k, 90)              # one turned (RotSprite) frame only: it bends the trousers a little
    t = K.turn(K.Part(body, feet), deg)
    c = np.zeros((128, 128, 4), np.uint8)
    K.place(c, t, (feet[0] - 4 - (4 if deg == 90 else 2), feet[1]))
    low = int(np.nonzero(c[..., 3].any(1))[0].max())
    return K.shifted(c, 0, P.D.soles - low)


def crumbs(a, least=6):
    """Loose bits a RotSprite turn left beside the figure (a flame tip) taken away."""
    for comp in K.pieces(a)[1:]:
        if len(comp) < least:
            for y, x in comp:
                a[y, x] = 0
    return a


# the fire lives (「火男移动时起码身上火焰要有点效果吧 不然太僵硬了」): in the idle and the run the head flames and the fire
# hands flicker through three states - as drawn, the flame crown a row taller (its rows moved up one, the lowest kept:
# the face never moves), every fire square a shade brighter
FIRE = ["350607", "4D090A", "A30806", "B80402", "F01D09", "F95307", "FA7406", "FC9103", "FBC302", "FCCC02", "FADA03"]
CROWN = (57, 62)                       # the flame crown's rows over the bald skull (the design's)
FLICKER = {"idle": [0, 1, 2, 0, 1, 2], "run": [0, 1, 2, 0, 1, 2]}


def flicker(P, f, state, tag):
    if not state:
        return f
    out = f.copy()
    top = int(np.nonzero(f[..., 3].any(1))[0].min())
    dy = top - P.D.top                                                  # the bob: the crown moved with the body
    r0, r1 = CROWN[0] + dy, CROWN[1] + dy
    if state == 1:
        out[r0 - 1:r1] = f[r0:r1 + 1]
        out[r1] = f[r1]
        return out
    ramp = [tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) for h in FIRE]
    nxt = {c: ramp[min(i + 1, len(ramp) - 1)] for i, c in enumerate(ramp)}
    region = np.zeros(f.shape[:2], bool)
    region[r0:r1 + 1] = True
    arms = np.roll(P.back_m | P.front_m, dy, axis=0)
    if tag == "run":                                                    # the run's lifted arms: their squares over
        for d in (1, 2):
            arms |= np.roll(arms, -d, axis=0)
    region |= arms
    for y, x in zip(*np.nonzero(region & (f[..., 3] > 0))):
        c = tuple(int(v) for v in f[y, x, :3])
        if c in nxt:
            out[y, x, :3] = nxt[c]
    return out


def frames(P, tag):
    n = len(MS[tag])
    if tag == "run":
        return [flicker(P, K.finish(run(P, k), P.D.outline, P.D.soles), FLICKER["run"][k], tag) for k in range(n)]
    if tag == "idle":
        return [flicker(P, P.D.a.copy(), FLICKER["idle"][k], tag) for k in range(n)]
    if tag == "dead":
        return [crumbs(K.finish(dead(P, k), P.D.outline, P.D.soles)) for k in range(n)]
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
