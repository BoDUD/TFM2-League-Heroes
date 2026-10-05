#!/usr/bin/env python3
"""Xin Zhao's action strips posed from the approved design's own parts (tools/art/rigkit.py; rig_tryndamere.py's way).

    python tools/art/rig_xinzhao.py [--check] [--review DIR] [--tags attack,q1] [--parts DIR]

Codex's step-2 delivery (assets/source/xinzhao/codex_strips/) drew every action 1.3-1.7 times the design's area (a bigger
head and body whenever he moves) with its own head and legs; its HANDOFF calls it "未达到可导入标准". The user: 「你学习
蛮王刚才怎么修复的 使用了各种工具」 - so, as rig_tryndamere.py: every frame is the design (tools/art/design_xinzhao.py) with
only what the action moves moved; Codex's frames and League's renders (assets/source/xinzhao/poses.json) give the poses.

The spear crosses his whole figure behind the body, so it is rebuilt as one rigid part first: the head group (purple
blade, silver crescent hook, streamer, collar) and the butt group (gold ring, iron spike) cut from the design, the
hidden shaft between them drawn straight in the design's own shaft colours (lit / dark, one outline square each side).
With the back arm (the hand on the grip, the forearm under the gold shoulder guard) it is ONE rigid unit that turns
about the shoulder only by exact quarter turns and mirrors (rigkit: never RotSprite, never sheared):
  k0 as drawn (the head low behind him), k1 upright (head up), k2 the head forward and a little up (the thrust), k3
  upright (head down); mirrored: k0m the head low in front (a low sweep), k1m upright, k2m the head up behind him.
The front arm is the design's own, as drawn, a quarter turn up ("up") or flipped forward ("fwd"); the head, body and legs
stay square for square; a pose's shift moves the whole figure; a lean shears the upper body over the hips (rig_tryndamere).
"""
import argparse
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
DESIGN = os.path.join(NATIVE, "xinzhao_native.png")
HERO = "xinzhao"
PIVOT = (64, 88)                       # the standing point on the 128 canvas (the soles on row 99)
CELL, CELL_PIVOT = (128, 96), (64, 70)

# ---------------------------------------------------------------------------------------------- parts (canvas)
HEAD_BOX = (80, 93, 14, 46)            # rows r0..r1, columns c0..c1: the spear's head end, nothing of his body in it
HEAD_KEEP = 42                         # of it the blade, hook, streamer and gold collar (columns up to 42); right of
                                       # that the design's own shaft stub, dropped (it is drawn again, straight)
BUTT_BOX = (63, 73, 74, 86)            # the butt end right of his head
BUTT_SHAFT = {69: (72, 73), 70: (72, 73), 71: (72, 73), 72: (72, 73)}   # the shaft's squares beside the head
BUTT_KEEP = 79                         # of it the gold ring and the iron spike (columns from 79)
BUTT_ROW = 68                          # the design's shaft enters the ring on row 68 (its lit row)
# the shaft: from the collar (column 43, lit row 83) up to the ring, a clean 1:2 step (one row every two columns: the
# design's own shaft runs 0.46; an exact 0.38 line mixed steps of 2 and 3 and the shaft wobbled - 「枪有变形的部分」)
SHAFT_X0, SHAFT_Y0, SHAFT_RUN = 43, 83, 2
TIP, BUTT_TIP = (15.5, 91.0), (85.5, 63.5)     # the spear's axis (the slide through the hand follows it)
GRIP = (47.5, 82.0)                    # where the back hand holds it (on the drawn shaft)
SHAFT_LIT, SHAFT_DARK = "#86523F", "#613231"
# the back arm: the hand on the grip and the forearm up to the gold shoulder guard; it turns about SHOULDER
BACK_ARM = {80: (47, 51), 81: (46, 52), 82: (47, 52), 83: (47, 50), 84: (47, 50), 85: (48, 50)}
SHOULDER = (52.5, 80.5)
# the front arm under the silver pauldron: the bracer, the forearm and the open hand
FRONT_ARM = {82: (71, 77), 83: (71, 76), 84: (72, 78), 85: (74, 78), 86: (76, 79), 87: (76, 79), 88: (77, 80)}
FRONT_PIVOT = (73.0, 82.0)
HIP_ROW, NECK_ROW = 88, 75


def axis_y(x):
    (x0, y0), (x1, y1) = TIP, BUTT_TIP
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


class Parts:
    def __init__(self):
        D = K.Design(DESIGN)
        self.D = D
        a = D.a
        r0, r1, c0, c1 = HEAD_BOX
        head_m = K.mask_box(r0, r1, c0, c1) & (a[..., 3] > 0)
        r0, r1, c0, c1 = BUTT_BOX
        butt_m = (K.mask_box(r0, r1, c0, c1) | K.mask_rows(BUTT_SHAFT)) & (a[..., 3] > 0)
        self.head_m, self.butt_m = head_m, butt_m
        # the whole spear: the head end and the butt end (their own shaft stubs dropped), the shaft drawn between them
        cols = np.arange(128)[None, :].repeat(128, 0)
        head_keep = head_m & (cols <= HEAD_KEEP)
        butt_keep = butt_m & (cols >= BUTT_KEEP)
        sp = np.zeros_like(a)
        lit, dark, out = (*K.rgb(SHAFT_LIT), 255), (*K.rgb(SHAFT_DARK), 255), (*D.outline, 255)

        def top(x):
            return SHAFT_Y0 - (x - SHAFT_X0) // SHAFT_RUN

        for x in range(SHAFT_X0 - 1, BUTT_KEEP + 2):
            yt = top(x)
            for yy, c in ((yt - 1, out), (yt, lit), (yt + 1, dark), (yt + 2, out)):
                if sp[yy, x, 3] == 0 or c is not out:
                    sp[yy, x] = c
        K.put(sp, np.where(head_keep[..., None], a, 0).astype(np.uint8), 0, 0)
        # the butt end moved along so the shaft enters its ring on the drawn shaft's row
        butt = np.where(butt_keep[..., None], a, 0).astype(np.uint8)
        K.put(sp, butt, 0, top(BUTT_KEEP) - BUTT_ROW)
        self.spear = K.Part.from_canvas(sp, sp[..., 3] > 0, GRIP)
        s = self.spear
        self.spears = {"dl": s, "ul": K.rot90(s, 1), "ur": K.rot90(s, 2), "dr": K.rot90(s, 3),
                       "dl_m": s.flip_h(), "ul_m": s.flip_v(), "ur_m": s.flip_h().flip_v(), "dr_m": K.rot90(s, 3).flip_h()}
        self.body = a.copy()
        self.body[head_m | butt_m] = 0
        # the back arm with the whole spear in its hand: one rigid unit about the shoulder
        arm_m = K.mask_rows(BACK_ARM) & (a[..., 3] > 0)
        unit = np.zeros_like(a)
        K.place(unit, self.spear, GRIP)
        unit[arm_m] = a[arm_m]
        self.unit = K.Part.from_canvas(unit, unit[..., 3] > 0, SHOULDER)
        self.arm_m = arm_m
        self._units = {}
        front_m = K.mask_rows(FRONT_ARM) & (a[..., 3] > 0)
        self.front_m = front_m
        rest = K.Part.from_canvas(a, front_m, FRONT_PIVOT)
        self.front = {None: rest, "up": K.rot90(rest, 3), "fwd": rest.flip_v()}
        self.core = self.body.copy()          # without either arm: the part that leans
        self.core[arm_m | front_m] = 0


def unit_as(P, k, mirror=False, slide=0):
    """The back arm + spear unit: the spear slid `slide` squares through the hand toward its head (+: more of it ahead
    of the hand - the thrusts hold it near the butt), then k quarter turns clockwise about the shoulder, then mirrored
    left-right about it."""
    if slide not in P._units:
        (x0, y0), (x1, y1) = TIP, BUTT_TIP
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x0 - x1) / L, (y0 - y1) / L          # toward the head
        dx, dy = int(round(ux * slide)), int(round(uy * slide))
        unit = np.zeros_like(P.D.a)
        K.place(unit, P.spear, (GRIP[0] + dx, GRIP[1] + dy))
        unit[P.arm_m] = P.D.a[P.arm_m]
        P._units[slide] = K.Part.from_canvas(unit, unit[..., 3] > 0, SHOULDER)
    u = K.rot90(P._units[slide], k)
    return u.flip_h() if mirror else u


def lean_shift(row, lean):
    """Columns the row moves for a lean (+ forward): 0 at the hips, the head as its chin row (rig_tryndamere)."""
    if not lean or row >= HIP_ROW:
        return 0
    v = (HIP_ROW - max(row, NECK_ROW)) * lean
    return int(math.floor(abs(v) + 0.5)) * (1 if v > 0 else -1)


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


# the spear's holds: ((quarter turns clockwise about the shoulder, mirrored, slid through the hand), behind the body?)
K0 = ((0, False, 0), True)             # as drawn, behind him
K0M = ((0, True, 8), False)            # the head low in front (a low sweep)
K0B = ((0, True, 8), True)             # the head low in front, the shaft behind him
K1 = ((1, False, 10), False)           # upright, the head up, in front
K1B = ((1, False, 10), True)           # upright behind
K2 = ((2, False, 16), False)           # the thrust: the head forward, held near the butt
K2M = ((2, True, 8), True)             # the head up behind him

# the legs: the image-left (back) leg and the image-right (front) leg, each turned about the hips (rigkit.swing_leg:
# the boot moved whole) - L / R columns (+ forward = right) and the boots' lifts
LEG_L = {r: (44, 59) for r in range(89, 100)}
LEG_R = {r: (68, 83) for r in range(89, 100)}
HIP, ANKLE = 89, 94


def pose(sp=K0, front=None, shift=(0, 0), lean=0.0, legs=(0, 0, 0, 0)):
    """One standing frame: the spear's hold, the front arm (None / "up" / "fwd"), the whole figure's shift (dx, dy;
    dy < 0 off the ground), the lean (+ forward), the legs (back leg dx, front leg dx, back lift, front lift)."""
    return dict(sp=sp, front=front, shift=shift, lean=lean, legs=legs)


# League's poses (poses.json renders and Codex's drawings of them): he lunges into every thrust - the front foot a
# step forward, the back leg pushed back, the whole figure forward - and E leaves the ground
LUNGE = (-2, 4, 0, 0)
STEP = (-1, 2, 0, 0)
STAND = {
    # the thrust (Attack 4, the hit on frame 4): drawn back, the low sweep forward, the thrust out, held, back
    "attack": [pose(K0, None, (-1, 0), -0.04), pose(K0M, None, (0, 0), 0.04, STEP), pose(K0M, None, (1, 0), 0.06, STEP),
               pose(K2, "fwd", (3, 0), 0.1, LUNGE), pose(K2, "fwd", (2, 0), 0.06, LUNGE), pose(K0, None, (0, 0), 0.0)],
    # Determination's third hit: lifted behind, swung up, over, brought down in front (frame 4), held low, back
    "attack_p": [pose(K1B, None, (-1, 0), -0.05), pose(K1B, "up", (-1, -1), -0.08, (0, 0, 0, 1)),
                 pose(K2M, "up", (0, -1), -0.04, (0, 0, 0, 1)), pose(K0M, None, (3, 0), 0.1, LUNGE),
                 pose(K0M, None, (2, 0), 0.06, LUNGE), pose(K0, None, (0, 0), 0.0)],
    # Q1: raised up, over, the thrust (frame 4), held, upright, back
    "q1": [pose(K1B, None, (0, 0), -0.04), pose(K2M, "up", (0, 0), -0.06), pose(K2, None, (1, 0), 0.05, STEP),
           pose(K2, "fwd", (3, 0), 0.1, LUNGE), pose(K2, "fwd", (3, 0), 0.08, LUNGE), pose(K1, None, (1, 0), 0.0, STEP)],
    # Q2: level, twirled upright, swept low forward, swung up in front (frame 4), up behind, back
    "q2": [pose(K2, None, (0, 0), 0.02), pose(K1, "up", (0, 0), 0.0), pose(K0M, None, (1, 0), 0.06, STEP),
           pose(K2, "fwd", (3, 0), 0.1, LUNGE), pose(K2M, "up", (2, 0), 0.0, STEP), pose(K0, None, (0, 0), 0.0)],
    # Q3: a crouch upright, level, swept up, the lift (frame 4, on his toes), held up high, back
    "q3": [pose(K1, None, (0, 1), 0.04), pose(K2, None, (1, 0), 0.05, STEP), pose(K2, "up", (1, -1), -0.02, STEP),
           pose(K1, "up", (1, -2), -0.06, (-1, 1, 0, 1)), pose(K2M, "up", (0, -1), -0.04), pose(K2M, "up", (0, 0), -0.04),
           pose(K0, None, (0, 0), 0.0)],
    # E: the crouch, the leap with the spear level ahead (off the ground, the back leg trailing, the front knee up),
    # the landing strike (frame 4), the thrust, back
    "skill": [pose(K0, None, (0, 1), 0.06, (0, 0, 0, 0)), pose(K2, "fwd", (3, -4), 0.12, (-4, 3, 3, 2)),
              pose(K2, "fwd", (5, -3), 0.12, (-4, 3, 2, 2)), pose(K0M, None, (4, 0), 0.1, LUNGE),
              pose(K2, "fwd", (2, 0), 0.06, STEP), pose(K0, None, (0, 0), 0.0)],
    # W: swung back, spun upright in front, upright at his side, the slash (frame 4), the thrust (5-6), back
    "skill2": [pose(K2M, None, (-1, 0), -0.05), pose(K1, "up", (0, 0), 0.0), pose(K1B, None, (0, 0), 0.0),
               pose(K2, "fwd", (1, 0), 0.06, STEP), pose(K2, "fwd", (4, 0), 0.12, LUNGE), pose(K2, "fwd", (3, 0), 0.1, LUNGE),
               pose(K0, None, (0, 0), 0.0)],
    # R: low across, swung behind, the sweep (frame 3), round to the left and the right, upright at his side
    "ult": [pose(K0, None, (0, 0), 0.04), pose(K2M, None, (-1, 0), -0.05, (1, -1, 0, 0)), pose(K2, "fwd", (2, 0), 0.08, STEP),
            pose(K0B, None, (1, 0), -0.04, STEP), pose(K2, "fwd", (2, 0), 0.08, STEP), pose(K0M, None, (1, 0), 0.04, STEP),
            pose(K1, None, (0, 0), 0.0)],
    "hit": [pose(K0, None, (-2, 0), -0.08, (1, -1, 0, 0)), pose(K0, None, (-1, 0), -0.04)],
}


def legs_apart(P, legs):
    """The trunk without the legs, and the two legs turned about the hips (back leg drawn behind the trunk)."""
    a = P.core
    left, right = K.mask_rows(LEG_L) & (a[..., 3] > 0), K.mask_rows(LEG_R) & (a[..., 3] > 0)
    trunk = a.copy()
    trunk[left | right] = 0
    dl, dr, ll, lr = legs
    return trunk, K.swing_leg(a, left, HIP, ANKLE, dl, ll), K.swing_leg(a, right, HIP, ANKLE, dr, lr)


def stand(P, p):
    (k, mirror, slide), under = p["sp"]
    lean, (dx, dy), front = p["lean"], p["shift"], p["front"]
    trunk, leg_l, leg_r = legs_apart(P, p["legs"])
    c = np.zeros((128, 128, 4), np.uint8)
    K.put(c, leg_l, 0, 0)
    K.put(c, leaned(trunk, lean), 0, 0)
    K.put(c, leg_r, 0, 0)
    fs = lean_shift(int(FRONT_PIVOT[1]), lean)
    K.place(c, P.front[front], (FRONT_PIVOT[0] + fs, FRONT_PIVOT[1]), under=front is not None)
    bs = lean_shift(int(SHOULDER[1]), lean)
    K.place(c, unit_as(P, k, mirror, slide), (SHOULDER[0] + bs, SHOULDER[1]), under=under)
    c = K.shifted(c, dx, dy) if (dx or dy) else c
    c[P.D.soles + 1:] = 0
    return c


# the run: the legs swung about the hips, the boots lifted in turn (rig_tryndamere's numbers: the stance's feet are 26
# columns apart as his)
IN = 7.0
SWING = [5.0, 3.0, 0.0, -3.0, -5.0, -3.0, 0.0, 3.0]
NEAR_LIFT = [0, 0, 0, 0, 0, 2, 3, 2]
FAR_LIFT = [0, 2, 3, 2, 0, 0, 0, 0]
DROP = [1, 0, 0, 0, 1, 0, 0, 0]


def run(P, k):
    a = P.D.a
    left, right = K.mask_rows(LEG_L) & (a[..., 3] > 0), K.mask_rows(LEG_R) & (a[..., 3] > 0)
    trunk = a.copy()
    trunk[left | right] = 0
    s, d = SWING[k], DROP[k]
    c = np.zeros((128, 128, 4), np.uint8)
    K.put(c, K.swing_leg(a, right, HIP, ANKLE, -IN - s, FAR_LIFT[k]), 0, 0)
    K.put(c, K.shifted(trunk, 0, d), 0, 0)
    K.put(c, K.swing_leg(a, left, HIP, ANKLE, IN + s, NEAR_LIFT[k]), 0, 0)
    c[P.D.soles + 1:] = 0
    return c


# the death (League's: he sinks to one knee on the upright spear, then falls forward on his face): the knees give
# (crouch: leg rows above the boots taken out, rig_tryndamere) with the spear upright in his hand; then he tips forward
# (the whole figure turned 45 degrees about his front foot - rigkit.turn, a whole figure only) and lies face down (an
# exact quarter turn: no squares change), the spear dropped beside him
KNEES = 94
LIE_X = 70.0                           # the fallen body's middle column (a little ahead of the standing point)
DEAD = [("hit",), ("crouch", 1, K1), ("crouch", 2, K1), ("crouch", 3, K1), ("crouch", 4, K1), ("tip", 45),
        ("lie",), ("lie",)]


def crouched(c, n):
    if not n:
        return c
    out = np.zeros_like(c)
    out[KNEES:] = c[KNEES:]
    out[n:KNEES] = c[:KNEES - n]
    return out


def kneeling(P, n, sp):
    c = K.put(np.zeros((128, 128, 4), np.uint8), P.core, 0, 0)
    K.place(c, P.front[None], FRONT_PIVOT)
    if sp is not None:
        (kk, m, sl), under = sp
        K.place(c, unit_as(P, kk, m, sl), SHOULDER, under=under)
    return crouched(c, n)


def on_ground(c, soles):
    """The figure moved down so its lowest square is on the soles' row."""
    low = int(np.nonzero(c[..., 3].any(1))[0].max())
    return K.shifted(c, 0, soles - low)


def dead(P, k):
    kind = DEAD[k]
    soles = P.D.soles
    if kind[0] == "hit":
        return stand(P, STAND["hit"][0])
    if kind[0] == "crouch":
        c = K.shifted(kneeling(P, kind[1], kind[2]), -1, 0)
    else:
        body = kneeling(P, 4, None)
        part = K.Part.from_canvas(body, body[..., 3] > 0, (80.0, float(soles)))
        part = K.turn(part, -kind[1]) if kind[0] == "tip" else K.rot90(part, 1)
        c = np.zeros((128, 128, 4), np.uint8)
        K.place(c, part, (64.0, 70.0))
        xs = np.nonzero(c[..., 3].any(0))[0]
        c = K.shifted(on_ground(c, soles), int(round(LIE_X - (xs.min() + xs.max()) / 2)), 0)
        K.place(c, P.spears["dl"], (LIE_X - 6.0, float(soles) - 1), under=True)
    c[soles + 1:] = 0
    return c


MS = {"idle": [200] * 6, "run": [130] * 8, "attack": [60, 60, 60, 100, 100, 120], "attack_p": [70, 70, 70, 100, 100, 100],
      "q1": [60, 60, 60, 100, 100, 100], "q2": [60, 60, 60, 100, 100, 100], "q3": [70, 70, 70, 100, 100, 100, 100],
      "skill": [50, 50, 50, 80, 80, 80], "skill2": [70, 70, 70, 70, 70, 80, 100], "ult": [80, 80, 90, 90, 90, 90, 100],
      "hit": [100, 100], "dead": [100, 110, 110, 120, 130, 150, 200, 300]}
TAGS = list(MS)


def frames(P, tag):
    n = len(MS[tag])
    if tag == "run":
        out = [run(P, k) for k in range(n)]
    elif tag == "dead":
        out = [dead(P, k) for k in range(n)]
    elif tag in STAND:
        out = [stand(P, p) for p in STAND[tag]]
    else:                    # idle: the design with the rebuilt straight spear, as every other strip holds it
        out = [stand(P, pose()) for _ in range(n)]
    return [K.finish(f, P.D.outline, P.D.soles) for f in out]


def parts_sheet(P, path):
    """The spear in every orientation, its grip marked, at 6x - for checking the cut."""
    tiles = []
    for name, sp in P.spears.items():
        t = np.zeros((sp.s.shape[0] + 2, sp.s.shape[1] + 2, 4), np.uint8)
        t[1:-1, 1:-1] = sp.s
        im = Image.new("RGBA", (t.shape[1], t.shape[0]), (110, 120, 108, 255))
        im.alpha_composite(Image.fromarray(t))
        im.putpixel((int(sp.j[0]) + 1, int(sp.j[1]) + 1), (255, 0, 0, 255))
        tiles.append((name, im.resize((im.width * 6, im.height * 6), Image.NEAREST)))
    sheet = Image.new("RGB", (sum(t.width + 12 for _, t in tiles), max(t.height for _, t in tiles) + 20), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    x = 0
    for name, t in tiles:
        sheet.paste(t.convert("RGB"), (x, 20))
        d.text((x + 2, 2), name, fill=(255, 255, 255))
        x += t.width + 12
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review", help="write review sheets / GIF to this folder")
    ap.add_argument("--tags", help="comma-separated tags to build (review only)")
    ap.add_argument("--parts", help="write the parts sheet to this folder")
    a = ap.parse_args()
    P = Parts()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        parts_sheet(P, os.path.join(a.parts, "xinzhao_spears.png"))
        Image.fromarray(np.repeat(np.repeat(P.body, 6, 0), 6, 1)).save(os.path.join(a.parts, "xinzhao_body.png"))
        return
    tags = a.tags.split(",") if a.tags else TAGS
    built = {t: frames(P, t) for t in tags}
    for t in tags:
        rows = K.audit(built[t], P.D.a, P.D.outline, P.D.soles)
        print(t, " ".join(f"[{r['pieces']}p {r['holes']}h {r['orphans']}o {r['below']}b {r['area']}]" for r in rows))
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
