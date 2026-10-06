#!/usr/bin/env python3
"""Kha'Zix's action strips: Codex's step-2 delivery (assets/source/khazix/codex_strips/) with the death redone.

    python tools/art/fix_khazix_strips.py [--check]

Codex re-posed the design's own parts (its HANDOFF: arms and claws cut out and turned whole by 45-degree steps, the
torso and legs square for square the design's, the head pasted in every frame) - the casting body is the idle's, as
the user's rule asks - and those strips go in as delivered. Its death did not: frames 3-4 tipped the body but kept the
head upright and left a leg hanging under it, and frames 5-8 stood the 90-degree figure on one leg instead of lying it
down (the user: 「完成下一步 有问题的地方你要灵活运用已有的工具来收尾」). DEAD rebuilds them as league_sivir's accepted
death (rig_samira.py's): frames 1-2 Codex's (struck, knocked back), then the WHOLE design turned 45 degrees back
(rigkit.turn, RotSprite, about the back foot), then a quarter turn counter-clockwise - on his back, the head to the
image left, the bent insect legs up at the right - first a row above the ground (the bounce), then on it.
The run was Codex's rows of the legs shifted in place - the feet slid, the legs never crossed, and the two scythe
claws that hang to the ground in the design (they read as two more legs) stood still: the user, 「走路时腿有点奇怪啊 这是
交叉步？」, then 「腿部移动时缺失模型看不到？」 and 「修一下吧 还有问题」 on a version that only lifted the claws in turn (the legs
still hid behind them and their gaps were filled into a dark blob). RUN builds it as League's run: both claws raised at
his sides, the blades up - Codex's own arm units (its masks and shoulder joints) turned whole by 135 degrees (FA, NA) -
so the two insect legs show; the legs (Codex's masks, the image-left one tucked TUCK columns in under the body) swung
from their hips by row shear with the foot whole (CYCLE: the feet cross, each lifted while it passes under the body,
mapped target row -> source row so a stretched leg never breaks), in the design's own colours (the mid leg is already
a shade darker than the lit left one), the body a row up between the landings; the gaps between the legs stay open.
Reads codex_strips/khazix_<tag>.png (8x) and khazix_cells.json, writes assets/source/native/khazix_<tag>.png (8x) and
khazix_cells.json for tools/art/import_native.py. --check only prints what would change.
"""
import argparse
import math
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "khazix", "codex_strips")
OUT = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(OUT, "khazix_native.png")
HEAD = os.path.join(OUT, "khazix_head_1x.png")     # the head pasted in every frame (the strips pack's)
TAGS = ["idle", "run", "attack", "skill", "skill2", "ult", "hit", "dead"]
Z = 8
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99)
SOLES = 99
BACK_FOOT = (50.0, 99.0)         # the turn's joint: the back foot's heel on the ground
# the death, per frame: Codex's frame, ("tilt", degrees counter-clockwise, dx), ("lying", rows above the ground, dx);
# dx = where the box's centre lies from the standing point (he falls back: to the image left)
DEAD = ["codex", "codex", ("tilt", 45, -6), ("lying", 1, -8), ("lying", 0, -8), ("lying", 0, -8), ("lying", 0, -8),
        ("lying", 0, -8)]


# ---- the run (the design's canvas: soles on row 99; the masks are Codex's, codex_strips/raw/build_khazix_strips.py)
def _rows(spec, op):
    m = np.zeros(op.shape, bool)
    for y, (x0, x1) in spec.items():
        m[y, x0:x1 + 1] = True
    return m & op


ARM_FAR = {**{y: (55, 60) for y in range(75, 77)}, **{y: (55, 61) for y in range(77, 80)},
           **{y: (56, 62) for y in range(80, 82)}, **{y: (57, 64) for y in range(82, 84)},
           **{y: (57, 65) for y in range(84, 86)}, **{y: (57, 64) for y in range(86, 88)}, 88: (58, 65), 89: (58, 64),
           90: (58, 63), 91: (58, 62), 92: (57, 62), 93: (58, 61), 94: (57, 61), 95: (57, 60), 96: (57, 60),
           97: (56, 59), 98: (56, 59), 99: (56, 58)}          # the image-left arm with its claw, from the shoulder
ARM_NEAR = {**{y: (78, 84) for y in range(75, 78)}, **{y: (79, 87) for y in range(78, 82)},
            **{y: (81, 87) for y in range(82, 85)}, **{y: (77, 86) for y in range(85, 88)}, 88: (77, 85), 89: (77, 84),
            90: (79, 84), 91: (80, 85), 92: (80, 86), 93: (81, 86), 94: (81, 87), 95: (82, 87), 96: (83, 88),
            97: (84, 88), 98: (85, 88), 99: (86, 88)}         # the image-right arm with its claw
LEG_LEFT = {**{y: (56, 61) for y in range(83, 86)}, **{y: (52, 59) for y in range(86, 90)},
            **{y: (50, 56) for y in range(90, 95)}, **{y: (47, 54) for y in range(95, 100)}}
LEG_MID = {83: (68, 75), **{y: (68, 77) for y in range(84, 89)}, **{y: (64, 77) for y in range(89, 94)},
           **{y: (64, 81) for y in range(94, 100)}}
# the hips the image-left arm covered in the design: kept on the body (without the claw's edge colour) so the raised
# arm leaves no notch and the left leg joins the body
HIP_BRIDGE = {**{y: (61, 67) for y in range(81, 84)}, **{y: (59, 67) for y in range(83, 87)}}
SHOULDER_FAR, SHOULDER_NEAR = (56.5, 75.5), (79.5, 75.5)
FA, NA = -135, 135        # the claws raised at his sides, the blades up (League's run): each arm turned whole
TUCK = 3                  # the image-left leg's hip moved in under the body (the idle's stance is wide)
LEGS = {"left": (LEG_LEFT, 84, 95), "mid": (LEG_MID, 84, 94)}   # mask, hip row, ankle row
# per frame: left (dx, lift), mid (dx, lift), the body up (rows): the feet cross - the left (lit) foot back in frame 1
# and forward in frame 5, the mid (shaded) one the other way, each lifted while it passes under the body; the body a
# row up between the landings
CYCLE = [((0, 0), (0, 0), 0), ((6, 2), (-5, 0), 1), ((12, 3), (-10, 0), 1), ((17, 2), (-15, 0), 1),
         ((20, 0), (-20, 0), 0), ((15, 0), (-14, 2), 1), ((10, 0), (-8, 3), 1), ((5, 0), (-3, 2), 1)]
BONE = [(200, 168, 168), (242, 220, 212), (255, 246, 240)]       # the claws' edge colours
WING_GREEN = [(94, 110, 28), (156, 184, 58), (210, 228, 122)]


def _colours(a, cols):
    m = np.zeros(a.shape[:2], bool)
    for c in cols:
        m |= (a[..., :3] == np.array(c, np.uint8)).all(-1) & (a[..., 3] > 0)
    return m


class Run:
    def __init__(self, d, head, ink):
        op = d[..., 3] > 0
        self.d, self.ink = d, ink
        hm = head[..., 3] > 0
        far, near = _rows(ARM_FAR, op) & ~hm, _rows(ARM_NEAR, op) & ~hm
        left = _rows(LEG_LEFT, op) & ~(far | near | hm)
        mid = _rows(LEG_MID, op) & ~(far | near | hm | left)
        self.legs = {"left": (left, LEGS["left"][1], LEGS["left"][2]), "mid": (mid, LEGS["mid"][1], LEGS["mid"][2])}
        bridge = _rows(HIP_BRIDGE, op) & ~hm & ~_colours(d, BONE)
        base = d.copy()
        base[far | near | left | mid] = 0
        base[bridge] = d[bridge]
        green = _colours(d, WING_GREEN)
        ring = np.zeros_like(green)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                ring |= np.roll(np.roll(green, dy, 0), dx, 1)
        wing = green | (ring & _colours(d, [tuple(ink)]))
        wing[69:] = False
        wing[:, 61:] = False
        self.wing = np.where(wing[..., None], base, 0).astype(np.uint8)
        self.torso = base.copy()
        self.torso[wing] = 0
        self.far = K.turn(K.Part.from_canvas(d, far, SHOULDER_FAR), FA)
        self.near = K.turn(K.Part.from_canvas(d, near, SHOULDER_NEAR), NA)
        self.hm = hm

    def leg(self, name, dx, lift, up, shift=0):
        """The leg sheared from its hip (the foot whole), the hip rising `up` with the body and the foot `lift` off the
        ground; each target row takes its source row (a stretched leg repeats a row instead of breaking)."""
        mask, hip, ankle = self.legs[name]
        ys, _ = np.nonzero(mask)
        r0, r1 = int(ys.min()), int(ys.max())
        t = lambda r: min(1.0, max(0.0, (r - hip) / max(1, ankle - hip)))
        target = {r: r - int(math.floor(up * (1 - t(r)) + lift * t(r) + 0.5)) for r in range(r0, r1 + 1)}
        out = np.zeros_like(self.d)
        for y in range(min(target.values()), max(target.values()) + 1):
            src = [r for r in range(r0, r1 + 1) if target[r] <= y]
            r = max(src) if src else r0
            sh = int(math.floor(dx * t(r) + 0.5)) + shift
            for c in np.nonzero(mask[r])[0]:
                if 0 <= c + sh < out.shape[1]:
                    out[y, c + sh] = self.d[r, c]
        return out

    def frame(self, k):
        """Back to front: the shaded mid leg, the lit left leg, the wings, the raised far arm (over the wings, under
        the torso), the torso with the pasted head, the raised near arm."""
        (ldx, llift), (mdx, mlift), up = CYCLE[k]
        out = np.zeros_like(self.d)
        K.put(out, self.leg("mid", mdx, mlift, up), 0, 0)
        K.put(out, self.leg("left", ldx, llift, up, TUCK), 0, 0)
        K.put(out, K.shifted(self.wing, 0, -up), 0, 0)
        K.place(out, self.far, (SHOULDER_FAR[0], SHOULDER_FAR[1] - up))
        K.put(out, K.shifted(self.torso, 0, -up), 0, 0)
        K.place(out, self.near, (SHOULDER_NEAR[0], SHOULDER_NEAR[1] - up))
        out[SOLES + 1:] = 0
        head = np.zeros_like(self.hm)
        head[:head.shape[0] - up] = self.hm[up:]
        # pinholes of one square only: the gaps between the legs stay open (rigkit.finish would fill 2-3)
        return K.finish(out, self.ink, SOLES, keep=head, pinholes=1)


def at1x(path):
    a = np.asarray(Image.open(path).convert("RGBA"))
    a = a[Z // 2::Z, Z // 2::Z].copy()
    a[a[..., 3] < 128] = 0
    a[a[..., 3] > 0, 3] = 255
    return a


def outline_colour(a):
    op = a[..., 3] > 0
    cols, n = np.unique(a[op][:, :3], axis=0, return_counts=True)
    return min(cols, key=lambda c: int(c.sum())).tolist()


def on_ground(a, rise, dx):
    """On the ground line (rise rows above it), its box centred dx columns from the standing point."""
    ys, xs = np.nonzero(a[..., 3] > 0)
    return K.shifted(a, PIVOT[0] + dx - (xs.min() + xs.max() + 1) // 2, SOLES - rise - ys.max())


def dead_frame(design, what):
    kind, amount, dx = what
    ys, xs = np.nonzero(design[..., 3] > 0)
    part = K.Part(design[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy(),
                  (BACK_FOOT[0] - xs.min(), BACK_FOOT[1] - ys.min()))
    turned = K.turn(part, amount if kind == "tilt" else 90)
    out = np.zeros_like(design)
    K.place(out, turned, BACK_FOOT)
    return on_ground(out, 0 if kind == "tilt" else amount, dx)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(SRC, "khazix_cells.json"), encoding="utf-8") as f:
        cells = json.load(f)
    cw, ch = cells["cell"]
    design = at1x(DESIGN) if Image.open(DESIGN).size[0] != 128 else np.asarray(Image.open(DESIGN).convert("RGBA")).copy()
    ink = outline_colour(design)
    head = np.asarray(Image.open(HEAD).convert("RGBA"))
    for tag in TAGS:
        sheet = at1x(os.path.join(SRC, f"khazix_{tag}.png"))
        if tag == "run":
            cols = sheet.shape[1] // cw
            run = Run(design, head, ink)
            for i in range(len(CYCLE)):
                fig = run.frame(i)
                X, Y = (i % cols) * cw, (i // cols) * ch
                px, py = cells["tags"][tag][i]["pivot"]
                cell = np.zeros((ch, cw, 4), np.uint8)
                K.put(cell, fig, px - PIVOT[0], py - PIVOT[1])
                sheet[Y:Y + ch, X:X + cw] = cell
            print("run: 8 frames rebuilt from the design (claws raised, crossing legs)")
        if tag == "dead":
            cols = sheet.shape[1] // cw
            for i, what in enumerate(DEAD):
                if what == "codex":
                    continue
                fig = K.finish(dead_frame(design, what), ink, SOLES)
                X, Y = (i % cols) * cw, (i // cols) * ch
                px, py = cells["tags"][tag][i]["pivot"]
                cell = np.zeros((ch, cw, 4), np.uint8)
                K.put(cell, fig, px - PIVOT[0], py - PIVOT[1])
                sheet[Y:Y + ch, X:X + cw] = cell
            print(f"dead: frames {[i + 1 for i, w in enumerate(DEAD) if w != 'codex']} rebuilt from the design")
        if a.check:
            continue
        big = Image.fromarray(np.repeat(np.repeat(sheet, Z, 0), Z, 1))
        big.save(os.path.join(OUT, f"khazix_{tag}.png"))
    if not a.check:
        shutil.copyfile(os.path.join(SRC, "khazix_cells.json"), os.path.join(OUT, "khazix_cells.json"))
        print("wrote", ", ".join(f"khazix_{t}.png" for t in TAGS), "and khazix_cells.json to assets/source/native")


if __name__ == "__main__":
    main()
