#!/usr/bin/env python3
"""Zeri's action strips posed from the approved design's own parts: the casting body = the idle's.

    python tools/art/rig_zeri.py [--check] [--review DIR] [--tags attack,run]

Codex's step-2 delivery on the 40-row design (assets/source/zeri/codex_strips_v2/) cut the design into parts and moved
them by translations and quarter turns, but it turned the free arm a quarter turn in the attack, W, E and R (the
hanging arm stuck out to the image left), fired the rifle from the hip (a quarter turn about the elbow), slid whole
legs to and fro for the run and laid the death down in one jump. The user: 「有问题的地方你帮我修复 模型穿模 色素多
模型变形之类的 完美了再喊我review」. Every frame here is the design (assets/source/native/zeri_native.png,
tools/art/design_zeri.py) with only what the action moves moved, nothing resampled:
- the arm unit (RIFLE: the rifle with the hand gripping it, FOREARM: the glove, the cuff and the elbow under it) is one
  rigid piece: upright as drawn, or a quarter turn clockwise about the elbow (ELBOW) so the forearm reaches forward and
  the rifle lies level at the hip, clear of the hair and the face (League's Q fires from the hip); the free arm at the
  image left never moves.
- the whole figure moves: a column back for the recoil and the hit; the upper body lowered a row over the legs for the
  crouches and the landings (lowered(): everything above the hips comes down over them); lifted for E's hop and R's
  spring; leant by moving the head rows and the chest rows whole (lean()).
- the run (8 frames): the upper body the idle's with the rifle held level at the hip (as League's Zeri runs), still;
  under it the design's own two legs moved whole in a stride (STRIDE, walk_legs); E's lunge and R's hop are strides
  of it.
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
import json as _json
# the design table on the canvas (design40/zeri40_final.txt, its soles on row 99). The constants below are written in
# the 40-row table's rows; the 37-row design took whole rows out (design40/shrink37.json): Rw() maps them
_KEPT = _json.load(open(os.path.join(ROOT, "assets", "source", "zeri", "design40", "shrink37.json")))["rows"]


def Rw(r):
    """A 40-row table row (int or float) -> the design's row (a row taken out -> the next one kept)."""
    base = int(r // 1)
    frac = r - base
    nxt = next((k for k, v in enumerate(_KEPT) if v >= base), len(_KEPT) - 1)
    return nxt + frac


OX, OY = 53, 100 - len(_KEPT)
CELL, CELL_PIVOT = (96, 80), (48, 64)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_back", "ult", "hit", "dead"]
MS = {"idle": [125] * 8, "run": [107] * 7 + [106], "attack": [67, 66, 100, 84, 83], "skill": [90, 90, 87, 117, 116],
      "skill2": [75] * 4, "skill2_back": [75] * 4, "ult": [75, 75, 90, 93], "hit": [100, 100],
      "dead": [100, 100, 100, 120, 150, 200, 300, 400]}


def T(r, c):
    """Table square (row, column, 40-row coordinates) -> canvas (x, y)."""
    return OX + c, OY + Rw(r)


# ------------------------------------------------------------------------------------------------ the parts (table)
# the rifle with the hand on its grip, by table rows: (first, last column); the glove under the hand stays
RIFLE_ROWS = {0: (19, 21), 1: (19, 22), 2: (19, 23), 3: (19, 23), 4: (18, 23), 5: (18, 22), 6: (18, 22), 7: (18, 23),
              8: (17, 23), 9: (17, 23), 10: (16, 22), 11: (16, 21), 12: (16, 20), 13: (16, 21), 14: (16, 22),
              15: (16, 18), 16: (16, 18), 17: (16, 18)}
RIFLE_EXTRA = [(15, 20), (15, 21), (15, 22), (16, 21), (16, 22), (16, 23)]   # the hand's knuckles, the grip's end
GRIP = (T(14, 20)[0] + 0.5, T(14, 20)[1] + 0.5)   # the middle of the hand (the rifle alone turns about it)
# the forearm under the hand (the maroon glove, the white cuff, the elbow out of the coat's sleeve): with the rifle and
# the hand it makes the arm unit, turned a quarter turn clockwise about the elbow so the rifle lies level at the hip
FOREARM = [(15, 19), (16, 19), (16, 20), (17, 19), (17, 20), (18, 18), (18, 19), (18, 20), (19, 18), (19, 19), (20, 18)]
# levelled, the forearm is one maroon band from the elbow to the hand: the white cuff (the design's, under the hand)
# would sit in the middle of it as a white blot (the user: 「这里多余的色素是什么？？」)
LEVEL_RECOLOUR = {"#F4F4F8": "#73234B", "#C0BAD3": "#45183A"}
ELBOW = (T(20, 18)[0] + 0.5, T(20, 18)[1] + 0.5)
HEAD_BOX = (0, 16, 0, 15)        # table rows r0..r1, columns c0..c1: the buns, the hair, the face, the neck
LEG_TOP = 28                     # the legs: the table rows from here down
BODY_KEEP = {28: [(0, 3)], 29: [(0, 2)]}          # the free hand's fingers stay with the body
SHIN_ROWS = (30, 32)             # the rows the knees fold away (the death's kneel)
# the run (the user: 「这跑动姿势对吗 交叉步都没？？」「跑步时腿别变形 之前慎什么都发生过最后处理完美的吧」, then
# 「泽丽走路时候模型怪」「应该是腿部完全变形的原因」「codex实在太笨了 泽丽你也自己修吧」): the legs used to be drawn as
# bones on League's 3/4 run (thin rubber legs, knotting, a boot on the other one, the body thrown 3 rows by League's
# hops), and Codex's redraw came back thin and splayed. As league_nautilus's approved run: the run body still, under
# it the design's own two legs whole (walk_legs: the straight one and the bent one with the knee patch), each moved
# whole (STRIDE) - the planted leg near, sliding back a stride on the soles, the other one a step darker behind, lifted
# a row or two and swinging forward past it; the straight leg plants in frames 1-4, the bent one in 5-8. Nothing
# turned, stretched or redrawn.
LEG_BOXES = {"S": (85, 99, 63, 75), "B": (88, 99, 56, 62)}    # rows, columns (canvas) of the design's two legs
STRIDE = {"planted": [3, 1, -1, -3], "swing": [(-4, 1), (-2, 2), (2, 2), (4, 1)]}   # columns moved (, rows lifted)
FAR_TONES = {"#73234B": "#45183A", "#9E493D": "#5A2418", "#F8C00C": "#F48C06", "#F48C06": "#A44B10",
             "#F2CC8F": "#AC8157", "#AC8157": "#5A2418"}
# what stays of the design under the belt in the run (table rows: (first, last) columns): the coat's two panels and
# the hanging hand; the boots (rows 33-39) are cut whole with their outline
RUN_KEEP = {25: [(0, 9), (17, 19)], 26: [(0, 9), (17, 20)], 27: [(0, 9)], 28: [(0, 3)], 29: [(0, 2)]}
RUN_BOOTS = {"near": (33, 39, 0, 8), "far": (33, 39, 13, 22)}
# the idle: her own breath (import_native's shared cut would run through the upright rifle): everything above the legs
# sinks 0 0 1 1 1 1 0 0 rows over them (lowered), as league_viego's
BREATH = [0, 0, 1, 1, 1, 1, 0, 0]


def table_mask(rows=None, box=None, cells=None):
    m = np.zeros((128, 128), bool)
    if rows:
        for r, (c0, c1) in rows.items():
            if r in _KEPT:
                m[OY + int(Rw(r)), OX + c0:OX + c1 + 1] = True
    if box:
        r0, r1, c0, c1 = box
        m[OY + int(Rw(r0)):OY + int(Rw(r1)) + 1, OX + c0:OX + c1 + 1] = True
    for r, c in cells or []:
        if r in _KEPT:
            m[OY + int(Rw(r)), OX + c] = True
    return m


class Rig:
    def __init__(self):
        self.D = K.Design(DESIGN)
        self.a = self.D.a
        self.out = self.D.outline
        op = self.a[..., 3] > 0
        self.rifle_m = table_mask(rows=RIFLE_ROWS, cells=RIFLE_EXTRA) & op
        self.forearm_m = table_mask(cells=FOREARM) & op & ~self.rifle_m
        self.arm_m = self.rifle_m | self.forearm_m
        self.head_m = table_mask(box=HEAD_BOX) & op & ~self.rifle_m
        legs = np.zeros((128, 128), bool)
        legs[OY + int(Rw(LEG_TOP)):] = True
        for r, spans in BODY_KEEP.items():
            for c0, c1 in spans:
                legs[OY + int(Rw(r)), OX + c0:OX + c1 + 1] = False
        self.legs_m = legs & op
        self.rifle = K.Part.from_canvas(self.a, self.rifle_m, GRIP)
        self.arm = K.Part.from_canvas(self.a, self.arm_m, ELBOW)

    # ---------------------------------------------------------------------------------------- building blocks
    def layer(self, m):
        out = np.zeros_like(self.a)
        out[m] = self.a[m]
        return out

    def body(self, rifle=True):
        m = (self.a[..., 3] > 0) & ~self.legs_m
        if not rifle:
            m &= ~self.arm_m
        return self.layer(m)

    def level_arm(self, c, dy=0):
        """The arm unit a quarter turn clockwise about the elbow (dy rows lower), its forearm one maroon band: the
        cuff's squares (each forearm square (r, c) of the table lands on (c + 2, 38 - r) about ELBOW) recoloured."""
        K.place(c, K.rot90(self.arm, 1), (ELBOW[0], ELBOW[1] + dy))
        sw = {K.rgb(a_): K.rgb(b_) for a_, b_ in LEVEL_RECOLOUR.items()}
        er, ec = int(Rw(20)), 18                       # the elbow's square (the turn's centre)
        for r, col in FOREARM:
            if r not in _KEPT:
                continue
            y, x = OY + er + (col - ec) + dy, OX + ec + (er - int(Rw(r)))
            got = tuple(int(v) for v in c[y, x, :3])
            if c[y, x, 3] and got in sw:
                c[y, x, :3] = sw[got]
        return c

    def rifle_level(self):
        """The rifle alone, level (the death's rifle on the ground)."""
        return K.rot90(self.rifle, 1)

    def lowered(self, upper, legs, dy):
        c = np.zeros_like(self.a)
        K.put(c, legs, 0, 0)
        K.put(c, upper, 0, dy)
        return c

    def lean(self, upper, dx_head, dx_chest):
        out = np.zeros_like(upper)
        r_head = OY + int(Rw(HEAD_BOX[1]))
        for y in range(upper.shape[0]):
            dx = dx_head if y <= r_head else (dx_chest if OY + 17 <= y <= OY + 22 else 0)
            out[y] = np.roll(upper[y], dx, 0) if dx else upper[y]
        return out

    def pose(self, rifle="up", dx=0, dy=0, low=0, lean=(0, 0)):
        upper = self.body(rifle=False)
        if rifle == "up":
            K.put(upper, self.layer(self.arm_m), 0, 0)
        elif rifle == "level":
            self.level_arm(upper)
        if lean != (0, 0):
            upper = self.lean(upper, *lean)
        c = self.lowered(upper, self.layer(self.legs_m), low)
        return K.shifted(c, dx, dy)

    # ---------------------------------------------------------------------------------------- the run
    def run_pieces(self):
        """The body above the legs (the design under the belt cut away but the coat's panels and the hand), the two
        boots with their tops' middles and heights. Cached."""
        if getattr(self, "_run", None) is not None:
            return self._run
        op = self.a[..., 3] > 0
        low = np.zeros((128, 128), bool)
        low[OY + int(Rw(25)):] = True
        for r, spans in RUN_KEEP.items():
            for c0, c1 in spans:
                low[OY + int(Rw(r)), OX + c0:OX + c1 + 1] = False
        body = self.layer(op & ~low & ~self.arm_m)      # the arm unit goes on level (League's run holds the rifle forward)
        boots = {}
        for leg, (r0, r1, c0, c1) in RUN_BOOTS.items():
            b = self.layer(table_mask(box=(r0, r1, c0, c1)) & op)
            ys, xs = np.nonzero(b[..., 3] > 0)
            top = ys.min()
            row = xs[ys == top]
            boots[leg] = (b, ((row.min() + row.max() + 1) / 2.0, float(top)), float(ys.max() + 1 - top))
        self._run = (body, boots)
        return self._run

    def walk_legs(self):
        """The design's two whole legs under the run body: "S" the straight one (image right: hips, two-square leggings,
        its boot) and "B" the bent one (image left, the knee patch, stepping back) - the design's squares in LEG_BOXES
        the run body leaves out. Cached."""
        if getattr(self, "_walk", None) is not None:
            return self._walk
        body, _ = self.run_pieces()
        legs = {}
        for name, (r0, r1, c0, c1) in LEG_BOXES.items():
            m = np.zeros((128, 128), bool)
            m[r0:r1 + 1, c0:c1 + 1] = True
            legs[name] = self.layer(m & (self.a[..., 3] > 0) & (body[..., 3] == 0))
        self._walk = legs
        return self._walk

    def far(self, leg):
        out = leg.copy()
        for y, x in zip(*np.nonzero(leg[..., 3])):
            h = "#%02X%02X%02X" % tuple(int(v) for v in leg[y, x, :3])
            if h in FAR_TONES:
                out[y, x, :3] = K.rgb(FAR_TONES[h])
        return out

    def run_frame(self, k):
        """The run body still over the two legs moved whole (STRIDE): the planted leg near, sliding back on the
        soles; the other one a step darker behind, lifted and swinging forward; the straight leg plants in frames
        1-4 and the bent one in 5-8."""
        body, _ = self.run_pieces()
        legs = self.walk_legs()
        i, second = k % 4, k >= 4
        planted, swing = ("B", "S") if second else ("S", "B")
        dx, lift = STRIDE["swing"][i]
        c = np.zeros_like(self.a)
        K.put(c, K.shifted(self.far(legs[swing]), dx, -lift), 0, 0)
        K.put(c, K.shifted(legs[planted], STRIDE["planted"][i], 0), 0, 0)
        K.put(c, body, 0, 0)
        self.level_arm(c, 0)
        c[SOLES + 1:] = 0
        return c

    # ---------------------------------------------------------------------------------------- the death
    def kneel(self, n, dx=0):
        legs = self.layer(self.legs_m)
        r_hi = OY + int(Rw(SHIN_ROWS[1]))
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
            return [P(low=n) for n in BREATH]
        if tag == "run":
            return [self.run_frame(k) for k in range(8)]
        if tag == "attack":
            return [P(), P(rifle="level"), P(rifle="level", dx=-1), P(rifle="level"), P()]
        if tag == "skill":
            return [P(low=1), P(rifle="level", low=1), P(rifle="level", low=1, dx=-1),
                    P(rifle="level", dx=-2, low=1), P()]
        R = lambda k, dx, dy: K.shifted(self.run_frame(k), dx, dy)     # a stride of the run, moved whole
        if tag == "skill2":                   # E forward: crouch, the run's long stride lunging forward, its landing
            return [P(low=1), R(0, 2, -1), R(1, 1, 0), P()]
        if tag == "skill2_back":              # E back: crouch, the run's tucked hop back, the landing
            return [P(low=1), R(3, -2, -1), P(dx=-1, low=1), P()]
        if tag == "ult":                      # R: crouch, a hop (the run's tucked frame), the nova fired level
            return [P(low=1), R(3, 0, -1), P(low=1, rifle="level", dx=-1), P()]
        if tag == "hit":
            return [P(dx=-2), P(dx=-1)]
        if tag == "dead":
            return [P(dx=-1), P(dx=-1, low=1), self.kneel(2, dx=-1), self.kneel(3, dx=-1),
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
            g = K.finish(f, self.out, SOLES, keep=keep)
            # finish leaves the kept head's light edges open (complete_outline skips light squares it may not touch):
            # the outline goes outside them too - only clear squares are filled
            g, _, _ = K.strips.complete_outline(g, color=tuple(self.out), feet=SOLES)
            for h in K.holes(g):
                if len(h) <= 6:
                    for y, x in h:
                        g[y, x] = (*self.out, 255)
            out.append(g)
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
