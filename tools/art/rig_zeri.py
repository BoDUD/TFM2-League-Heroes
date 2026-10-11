#!/usr/bin/env python3
"""Zeri's action strips posed from the approved design's own parts: the casting body = the idle's.

    python tools/art/rig_zeri.py [--check] [--review DIR] [--tags attack,run]

Codex's step-2 delivery on the 40-row design (assets/source/zeri/codex_strips_v2/) cut the design into parts and moved
them by translations and quarter turns, but it turned the free arm a quarter turn in the attack, W, E and R (the
hanging arm stuck out to the image left), fired the rifle from the hip (a quarter turn about the elbow), slid whole
legs to and fro for the run and laid the death down in one jump. The user: 「有问题的地方你帮我修复 模型穿模 色素多
模型变形之类的 完美了再喊我review」. Every frame here is the design (assets/source/native/zeri_native.png,
tools/art/design_zeri.py) with only what the action moves moved, nothing resampled:
- the rifle unit (RIFLE: the rifle with the hand gripping it) is one rigid piece: upright as drawn, or a quarter turn
  clockwise about the grip (GRIP) so the rifle lies level to the image right at shoulder height (League's Q holds it
  across the chest); the glove and the forearm under the hand and the free arm at the image left never move.
- the whole figure moves: a column back for the recoil and the hit; the upper body lowered a row over the legs for the
  crouches and the landings (lowered(): everything above the hips comes down over them); lifted for E's hop and R's
  spring; leant by moving the head rows and the chest rows whole (lean()).
- the run (League's, 8 frames): the upper body the idle's (the rifle upright as in League's run), a row lower at each
  contact; each leg the design's own squares swung about its hip (rigkit.swing_leg: rows moved in proportion, the boot
  moved whole and lifted on the back swing), the far leg under the near one.
- the death (League's): struck back, sinking to her knees (whole shin rows out, the boots kept), then down on her face:
  the figure without the rifle a quarter turn clockwise (League falls forward), the rifle lying level by her.
Each frame is finished round what moved (rigkit.finish: the outline closed on moved edges, pinholes filled, stray
outline squares dropped; the head never changes), then audited: pieces, holes, orphan outline squares, nothing under the
soles, the head the design's in every standing frame.
Writes assets/source/native/zeri_<tag>.png (8x, 96 x 80 cells) and zeri_cells.json; then tools/art/import_native.py.
--check compares instead of writing; --review writes a review sheet and GIF.
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
DESIGN = os.path.join(NATIVE, "zeri_native.png")
HERO = "zeri"
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
OX, OY = 53, 60                  # the 24 x 40 design table on the canvas (design40/zeri40_final.txt)
CELL, CELL_PIVOT = (96, 80), (48, 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_back", "ult", "hit", "dead"]
MS = {"idle": [200] * 6, "run": [107] * 7 + [106], "attack": [67, 66, 100, 84, 83], "skill": [90, 90, 87, 117, 116],
      "skill2": [75] * 4, "skill2_back": [75] * 4, "ult": [75, 75, 90, 93], "hit": [100, 100],
      "dead": [100, 100, 100, 120, 150, 200, 300, 400]}


def T(r, c):
    """Table square (row, column) -> canvas (x, y)."""
    return OX + c, OY + r


# ------------------------------------------------------------------------------------------------ the parts (table)
# the rifle with the hand on its grip, by table rows: (first, last column); the glove under the hand stays
RIFLE_ROWS = {0: (19, 21), 1: (19, 22), 2: (19, 23), 3: (19, 23), 4: (18, 23), 5: (18, 22), 6: (18, 22), 7: (18, 23),
              8: (17, 23), 9: (17, 23), 10: (16, 22), 11: (16, 21), 12: (16, 20), 13: (16, 21), 14: (16, 22),
              15: (16, 18), 16: (16, 18), 17: (16, 18)}
RIFLE_EXTRA = [(15, 20), (15, 21), (15, 22), (16, 21), (16, 22), (16, 23)]   # the hand's knuckles, the grip's end
GRIP = (T(14, 20)[0] + 0.5, T(14, 20)[1] + 0.5)   # the middle of the hand: the quarter turn's centre
LEVEL_AT = (1, 0)                # the levelled rifle set this far off the grip, its stock clear of the face
HEAD_BOX = (0, 16, 0, 15)        # table rows r0..r1, columns c0..c1: the buns, the hair, the face, the neck
LEG_TOP = 28                     # the legs: the table rows from here down
BODY_KEEP = {28: [(0, 3)], 29: [(0, 2)]}          # the free hand's fingers stay with the body
SHIN_ROWS = (30, 32)             # the rows the knees fold away (the death's kneel)
# the run: each leg's columns (table) and its hip / ankle rows for rigkit.swing_leg; the boot moved whole
LEGS = {"near": (0, 9, 28, 33), "far": (12, 22, 28, 33)}
SWING = [2, 1, 0, -1, -2, -1, 1, 2]                  # near leg's boot offset per frame (+ forward); the far leg opposite
LIFT = [0, 0, 0, 0, 1, 2, 1, 0]
BOB = [1, 0, 0, 1, 1, 0, 0, 1]


def table_mask(rows=None, box=None, cells=None):
    m = np.zeros((128, 128), bool)
    if rows:
        for r, (c0, c1) in rows.items():
            m[OY + r, OX + c0:OX + c1 + 1] = True
    if box:
        r0, r1, c0, c1 = box
        m[OY + r0:OY + r1 + 1, OX + c0:OX + c1 + 1] = True
    for r, c in cells or []:
        m[OY + r, OX + c] = True
    return m


class Rig:
    def __init__(self):
        self.D = K.Design(DESIGN)
        self.a = self.D.a
        self.out = self.D.outline
        op = self.a[..., 3] > 0
        self.rifle_m = table_mask(rows=RIFLE_ROWS, cells=RIFLE_EXTRA) & op
        self.head_m = table_mask(box=HEAD_BOX) & op & ~self.rifle_m
        legs = np.zeros((128, 128), bool)
        legs[OY + LEG_TOP:] = True
        for r, spans in BODY_KEEP.items():
            for c0, c1 in spans:
                legs[OY + r, OX + c0:OX + c1 + 1] = False
        self.legs_m = legs & op
        self.leg_m = {}
        for side, (c0, c1, hip, ankle) in LEGS.items():
            m = np.zeros((128, 128), bool)
            m[OY + LEG_TOP:, OX + c0:OX + c1 + 1] = True
            self.leg_m[side] = m & self.legs_m
        self.rifle = K.Part.from_canvas(self.a, self.rifle_m, GRIP)

    # ---------------------------------------------------------------------------------------- building blocks
    def layer(self, m):
        out = np.zeros_like(self.a)
        out[m] = self.a[m]
        return out

    def body(self, rifle=True):
        m = (self.a[..., 3] > 0) & ~self.legs_m
        if not rifle:
            m &= ~self.rifle_m
        return self.layer(m)

    def rifle_level(self):
        return K.rot90(self.rifle, 1)

    def lowered(self, upper, legs, dy):
        c = np.zeros_like(self.a)
        K.put(c, legs, 0, 0)
        K.put(c, upper, 0, dy)
        return c

    def lean(self, upper, dx_head, dx_chest):
        out = np.zeros_like(upper)
        r_head = OY + HEAD_BOX[1]
        for y in range(upper.shape[0]):
            dx = dx_head if y <= r_head else (dx_chest if OY + 17 <= y <= OY + 22 else 0)
            out[y] = np.roll(upper[y], dx, 0) if dx else upper[y]
        return out

    def legs(self, swing=0, lift=0):
        """Both legs: the near one's boot `swing` columns forward (lifted `lift` rows), the far one's the other way."""
        c = np.zeros_like(self.a)
        for side, sw, lf in (("far", -swing, 0 if swing >= 0 else lift), ("near", swing, lift if swing < 0 else 0)):
            c0, c1, hip, ankle = LEGS[side]
            leg = K.swing_leg(self.a, self.leg_m[side], OY + hip, OY + ankle, sw, lift=lf)
            K.put(c, leg, 0, 0)
        return c

    def pose(self, rifle="up", dx=0, dy=0, low=0, lean=(0, 0), legs=None):
        upper = self.body(rifle=False)
        if rifle == "up":
            K.put(upper, self.layer(self.rifle_m), 0, 0)
        elif rifle == "level":
            K.place(upper, self.rifle_level(), (GRIP[0] + LEVEL_AT[0], GRIP[1] + LEVEL_AT[1]))
        if lean != (0, 0):
            upper = self.lean(upper, *lean)
        leg_layer = self.layer(self.legs_m) if legs is None else legs
        c = self.lowered(upper, leg_layer, low)
        return K.shifted(c, dx, dy)

    # ---------------------------------------------------------------------------------------- the run
    def run_frame(self, k):
        legs = self.legs(SWING[k], LIFT[k])
        c = self.lowered(self.body(rifle=True), legs, BOB[k])
        c[SOLES + 1:] = 0
        return c

    # ---------------------------------------------------------------------------------------- the death
    def kneel(self, n, dx=0):
        legs = self.layer(self.legs_m)
        r_hi = OY + SHIN_ROWS[1]
        cut0 = r_hi - n + 1
        upper_legs = legs.copy()
        upper_legs[cut0:] = 0
        boots = legs.copy()
        boots[:r_hi + 1] = 0
        c = np.zeros_like(self.a)
        K.put(c, boots, 0, 0)
        K.put(c, upper_legs, 0, n)
        up = self.body(rifle=True)
        K.put(c, up, 0, n)
        return K.shifted(c, dx, 0)

    def lying(self):
        fig = self.layer((self.a[..., 3] > 0) & ~self.rifle_m)
        part = K.Part.from_canvas(fig, fig[..., 3] > 0, (PIVOT[0] + 0.5, SOLES + 0.5))
        turned = K.rot90(part, 1)
        c = np.zeros_like(self.a)
        K.place(c, turned, (PIVOT[0] - 18 + 0.5, SOLES + 0.5))
        ys, xs = np.nonzero(c[..., 3])
        c = K.shifted(c, 0, SOLES - ys.max())
        tmp = np.zeros_like(self.a)
        K.place(tmp, self.rifle_level(), (40, 40))
        gy, gx = np.nonzero(tmp[..., 3])
        ys, xs = np.nonzero(c[..., 3])
        K.put(c, K.shifted(tmp, xs.max() - gx.min() - 8, SOLES - gy.max()), 0, 0, under=True)
        return c

    # ---------------------------------------------------------------------------------------- the strips
    def build(self, tag):
        P = self.pose
        if tag == "idle":
            return [P() for _ in range(6)]
        if tag == "run":
            return [self.run_frame(k) for k in range(8)]
        if tag == "attack":
            return [P(), P(rifle="level"), P(rifle="level", dx=-1), P(rifle="level"), P()]
        if tag == "skill":
            return [P(low=1), P(rifle="level", low=1), P(rifle="level", low=1, dx=-1),
                    P(rifle="level", dx=-2, low=1), P()]
        if tag == "skill2":
            return [P(low=1), P(dx=2, dy=-1, legs=self.legs(-2, 1)), P(dx=1, low=1, legs=self.legs(1, 0)), P()]
        if tag == "skill2_back":
            return [P(low=1), P(dx=-2, dy=-2, legs=self.legs(1, 1)), P(dx=-1, low=1), P()]
        if tag == "ult":
            return [P(low=1), P(dy=-2, rifle="level", legs=self.legs(-1, 1)), P(low=1, rifle="level"), P()]
        if tag == "hit":
            return [P(dx=-2, lean=(-1, 0)), P(dx=-1)]
        if tag == "dead":
            return [P(dx=-1, lean=(-1, 0)), P(dx=-1, low=1), self.kneel(2, dx=-1), self.kneel(3, dx=-1),
                    self.lying(), self.lying(), self.lying(), self.lying()]
        raise KeyError(tag)

    def head_keep(self, f):
        hm = self.head_m
        ys, xs = np.nonzero(hm)
        best = None
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                yy, xx = ys + dy, xs + dx
                ok = (yy >= 0) & (yy < 128) & (xx >= 0) & (xx < 128)
                same = (f[yy[ok], xx[ok]] == self.a[ys[ok], xs[ok]]).all(-1).sum()
                if best is None or same > best[0]:
                    best = (same, dy, dx)
        _, dy, dx = best
        keep = np.zeros(hm.shape, bool)
        yy, xx = ys + dy, xs + dx
        ok = (yy >= 0) & (yy < 128) & (xx >= 0) & (xx < 128)
        keep[yy[ok], xx[ok]] = True
        return keep

    def finished(self, frames, tag):
        out = []
        for f in frames:
            keep = None if tag == "dead" else self.head_keep(f)
            out.append(K.finish(f, self.out, SOLES, keep=keep))
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--review")
    ap.add_argument("--tags", default=",".join(TAGS))
    a = ap.parse_args()
    rig = Rig()
    built = {}
    for tag in a.tags.split(","):
        built[tag] = rig.finished(rig.build(tag), tag)
    for tag, frs in built.items():
        rows = K.audit(frs, rig.a, rig.out, SOLES)
        print(f"{tag:12s}", " ".join(f"{i + 1}:{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}"
                                     for i, r in enumerate(rows)))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, f) for t, f in built.items()], os.path.join(a.review, "zeri_rig_frames.png"), z=6,
                       soles=SOLES)
        K.review_gif([(t, f) for t, f in built.items()], MS, os.path.join(a.review, "zeri_rig_actions.gif"), z=6)
    if len(built) == len(TAGS):
        bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        print("check:", "identical" if a.check and not bad else (bad if a.check else "written"))


if __name__ == "__main__":
    main()
