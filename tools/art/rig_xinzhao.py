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
HEAD_BOX = (80, 93, 14, 46)            # rows r0..r1, columns c0..c1: the spear's head group, nothing of his body in it
BUTT_BOX = (63, 73, 74, 86)            # the butt group right of his head
BUTT_SHAFT = {69: (72, 73), 70: (72, 73), 71: (72, 73), 72: (72, 73)}   # the shaft's squares beside the head
TIP, BUTT_TIP = (15.5, 91.0), (85.5, 64.5)     # the blade's tip and the butt's tip (the spear's axis)
GRIP = (47.5, 82.5)                    # where the back hand holds it
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
        # the whole spear: the shaft drawn along the axis, both groups over it (their outline never across the shaft)
        sp = np.zeros_like(a)
        lit, dark, out = (*K.rgb(SHAFT_LIT), 255), (*K.rgb(SHAFT_DARK), 255), (*D.outline, 255)
        for x in range(int(GRIP[0]) - 6, BUTT_BOX[2] + 2):
            yt = int(math.floor(axis_y(x + 0.5) - 0.5))          # the shaft's two rows: yt (lit), yt + 1 (dark)
            for yy, c in ((yt - 1, out), (yt, lit), (yt + 1, dark), (yt + 2, out)):
                if sp[yy, x, 3] == 0 or c is not out:
                    sp[yy, x] = c
        groups = np.where((head_m | butt_m)[..., None], a, 0).astype(np.uint8)
        ink = (groups[..., :3] == np.array(D.outline, np.uint8)).all(-1) & (groups[..., 3] > 0)
        shaft = (sp[..., 3] > 0) & ~(sp[..., :3] == np.array(D.outline, np.uint8)).all(-1)
        groups[ink & shaft] = 0
        K.put(sp, groups, 0, 0)
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


# the standing actions, per frame: ((quarter turns, mirrored) of the back arm + spear unit about the shoulder, behind
# the body?), front arm None / "up" / "fwd", whole-figure shift (dx, dy; dy -1 = off the ground), lean (+ forward)
K0 = ((0, False, 0), True)             # as drawn, behind him
K0M = ((0, True, 8), False)            # the head low in front (a low sweep)
K1 = ((1, False, 10), False)           # upright, the head up, in front
K1B = ((1, False, 10), True)           # upright behind
K2 = ((2, False, 16), False)           # the thrust: the head forward, held near the butt
K2M = ((2, True, 8), True)             # the head up behind him
STAND = {
    # the thrust (Attack 4, the hit on frame 4): drawn back, the low sweep forward, the thrust out, held, back
    "attack": [(K0, None, (-1, 0), -0.04), (K0M, None, (0, 0), 0.02), (K0M, None, (1, 0), 0.06),
               (K2, None, (2, 0), 0.1), (K2, None, (1, 0), 0.06), (K0, None, (0, 0), 0.0)],
    # Determination's third hit: lifted behind, swung up, over, brought down in front (frame 4), held low, back
    "attack_p": [(K1B, None, (-1, 0), -0.05), (K1B, "up", (-1, 0), -0.08), (K2M, "up", (0, 0), -0.04),
                 (K0M, None, (2, 0), 0.1), (K0M, None, (1, 0), 0.06), (K0, None, (0, 0), 0.0)],
    # Q1: raised up, over, the thrust (frame 4), held, upright, back
    "q1": [(K1B, None, (0, 0), -0.04), (K2M, "up", (0, 0), -0.06), (K2, None, (1, 0), 0.05),
           (K2, "fwd", (2, 0), 0.1), (K2, "fwd", (2, 0), 0.08), (K1, None, (0, 0), 0.0)],
    # Q2: level, twirled upright, swept low forward, swung up in front (frame 4), up behind, back
    "q2": [(K2, None, (0, 0), 0.02), (K1, "up", (0, 0), 0.0), (K0M, None, (1, 0), 0.06),
           (K2, "fwd", (2, 0), 0.1), (K2M, "up", (1, 0), 0.0), (K0, None, (0, 0), 0.0)],
    # Q3: a crouch upright, level, swept up, the lift (frame 4), held up high, back
    "q3": [(K1, None, (0, 1), 0.04), (K2, None, (1, 0), 0.05), (K2, "up", (1, -1), -0.02),
           (K1, "up", (1, -1), -0.06), (K2M, "up", (0, 0), -0.04), (K2M, "up", (0, 0), -0.04), (K0, None, (0, 0), 0.0)],
    # E: the crouch, the leap with the spear level ahead (off the ground), the landing strike (frame 4), the thrust, back
    "skill": [(K0, None, (0, 1), 0.06), (K2, "fwd", (2, -2), 0.12), (K2, "fwd", (3, -2), 0.12),
              (K0M, None, (2, 0), 0.1), (K2, "fwd", (1, 0), 0.06), (K0, None, (0, 0), 0.0)],
    # W: swung back, spun upright in front, upright at his side, the slash (frame 4), the thrust (5-6), back
    "skill2": [(K2M, None, (-1, 0), -0.05), (K1, "up", (0, 0), 0.0), (K1B, None, (0, 0), 0.0), (K2, "fwd", (1, 0), 0.06),
               (K2, "fwd", (3, 0), 0.12), (K2, "fwd", (2, 0), 0.1), (K0, None, (0, 0), 0.0)],
    # R: low across, swung behind, the sweep (frame 3), round to the left and the right, upright at his side
    "ult": [(K0, None, (0, 0), 0.04), (K2M, None, (-1, 0), -0.05), (K2, "fwd", (1, 0), 0.08),
            (((0, True, 8), True), None, (0, 0), -0.04), (K2, "fwd", (1, 0), 0.08), (K0M, None, (1, 0), 0.04),
            (K1, None, (0, 0), 0.0)],
    "hit": [(K0, None, (-1, 0), -0.08), (K0, None, (0, 0), -0.04)],
}


def stand(P, pose):
    ((k, mirror, slide), under), front, (dx, dy), lean = pose
    c = leaned(P.core, lean)
    fs = lean_shift(int(FRONT_PIVOT[1]), lean)
    K.place(c, P.front[front], (FRONT_PIVOT[0] + fs, FRONT_PIVOT[1]), under=front is not None)
    bs = lean_shift(int(SHOULDER[1]), lean)
    K.place(c, unit_as(P, k, mirror, slide), (SHOULDER[0] + bs, SHOULDER[1]), under=under)
    c = K.shifted(c, dx, dy) if (dx or dy) else c
    c[P.D.soles + 1:] = 0
    return c


# the run: the legs swung about the hips, the boots lifted in turn (rig_tryndamere's numbers: the stance's feet are 26
# columns apart as his)
LEG_L = {r: (44, 59) for r in range(89, 100)}
LEG_R = {r: (68, 83) for r in range(89, 100)}
HIP, ANKLE = 89, 94
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


# the death (League's: he sinks to one knee on the spear, then goes down): the whole figure staggers, the knees give
# (crouch: leg rows above the boots taken out, rig_tryndamere), the spear upright in his hand, then dropped flat
KNEES = 94
DEAD = [None, (0, -1, K1), (1, -1, K1), (2, -1, K1), (3, -1, K1), (4, -1, None), (5, -1, None), (5, -1, None)]


def crouched(c, n):
    if not n:
        return c
    out = np.zeros_like(c)
    out[KNEES:] = c[KNEES:]
    out[n:KNEES] = c[:KNEES - n]
    return out


def dead(P, k):
    if DEAD[k] is None:
        return stand(P, STAND["hit"][0])
    n, dx, sp = DEAD[k]
    c = K.put(np.zeros((128, 128, 4), np.uint8), P.core, 0, 0)
    K.place(c, P.front[None], FRONT_PIVOT)
    if sp is not None:
        (kk, m, sl), under = sp
        K.place(c, unit_as(P, kk, m, sl), SHOULDER, under=under)
    c = crouched(c, n)
    if sp is None:           # the spear dropped: lying on the ground in front of him
        K.place(c, P.spears["dl"], (76.0, float(P.D.soles) - 1), under=False)
    c[P.D.soles + 1:] = 0
    return K.shifted(c, dx, 0)


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
    else:
        out = [P.D.a.copy() for _ in range(n)]
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
