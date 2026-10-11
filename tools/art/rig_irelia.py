#!/usr/bin/env python3
"""Irelia's action strips posed from the approved design's own pixels (the user, 2026-10-11, on Codex's side-on
delivery: 「侧脸的五官每个都不一样 好奇怪 我们做的是这一版吧 起码要在这一版的动作上做动作帧吧 codex太蠢了 你完善吧」).

    python tools/art/rig_irelia.py [--check] [--review DIR] [--tags attack,run]

Codex's strips (assets/source/irelia/codex_strips, from tools/art/pack_irelia_strips.py) were side-on, but the face
was a different face in every frame and the attack, W, the R's wind-up, the Q's landing and the hit were drawn a fifth
smaller than the design. Every frame here is the design (assets/source/native/irelia_native.png, design42/irelia42.txt)
with only what the action moves moved, nothing resampled. The first rig was sent back (「你看不到模型有一堆问题吗 各种变形吗」):
the head moved alone over the body (the bundle broke at the neck, the chin off the collar), the far arm turned up lay
across her face, crouches pushed the body into the legs, the run stood her on Codex's thin legs, and the importer's
breathing bent the idle. Now:
- the head, the body and the bundle move only together, with the whole figure; nothing is lowered into the legs;
- the far arm (image right, nearer the target) is a rigid unit cut from the design (sleeve, white elbow plate, red
  guard, white wrist band, the hand with its finger tips): hanging as drawn or turned a quarter to point forward at
  shoulder height - never up across the face; the near arm always hangs;
- the blades: the bundle behind her back moved whole (lifted for the R, dropped in the death, gone while the R's volley
  flies, its top blade gone while the E's blades fly), single blades in flight a hand-drawn crescent in the blades'
  colours, the W's shield the design's own upright blade, always clear of the open hand (the user: 「刀妹没有单一的传统
  手持武器 她的武器是一组漂浮的致命飞刀」);
- the legs are the design's own: the run's cross steps move each boot whole and lean the leg above it to it from the
  hip (rigkit.swing_leg), lifting the passing boot, the whole figure a row up on the passing frames; the Q's dash stands
  on the widest step;
- the idle is the design, still (import_native.BREATHE_SKIP);
- the death: struck back, sinking to her knees (the boots' tops folded away), then lying (the figure turned a
  quarter), the bundle dropped behind her.
Each frame is finished round what moved (rigkit.finish: the outline closed on moved edges, pinholes filled, stray
outline squares dropped; the head never changes), then audited. Writes assets/source/native/irelia_<tag>.png (8x) and
irelia_cells.json; then tools/art/import_native.py --hero irelia.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rigkit as K  # noqa: E402

NATIVE = os.path.join(ROOT, "assets", "source", "native")
DESIGN = os.path.join(NATIVE, "irelia_native.png")
CODEX = os.path.join(ROOT, "assets", "source", "irelia", "codex_strips")
PAL = json.load(open(os.path.join(ROOT, "assets", "source", "irelia", "design42", "palette.json"), encoding="utf-8"))
HERO = "irelia"
OX, OY = 50, 58                  # table square (r, c) -> canvas (OX + c, OY + r)
PIVOT = (64, 88)                 # the design's standing point (the soles on row 99, the feet's middle on column 64)
SOLES = 99
CELL, CELL_PIVOT = (112, 84), (52, 66)
TAGS = ["idle", "run", "attack", "skill", "skill2", "skill2_w", "ult", "hit", "dead"]
MS = {"idle": [160] * 8, "run": [125] * 8, "attack": [60, 70, 80, 80, 80], "skill": [60, 70, 70, 70],
      "skill2": [70, 70, 80, 70, 80], "skill2_w": [80, 120, 160, 170, 100, 100], "ult": [70, 80, 90, 90, 100],
      "hit": [100, 100], "dead": [100, 100, 120, 150, 150, 200, 300, 400]}

# ------------------------------------------------------------------------------------------------ the parts (table)
# the far arm (image right, the one nearer the target): the sleeve under the shoulder guard down to the hand
FAR_ARM = {22: (16, 18), 23: (16, 18), 24: (17, 19), 25: (17, 19), 26: (17, 20), 27: (17, 20), 28: (17, 21),
           29: (17, 21), 30: (17, 21), 31: (17, 20)}
FAR_SHOULDER = (OX + 17.0, OY + 22.0)      # the corner the arm turns about (a square corner: quarter turns exact)
# the near arm (image left): the bare upper arm under the white hook down to the hand
NEAR_ARM = {20: (7, 10), 21: (7, 10), 22: (7, 10), 23: (7, 10), 24: (7, 10), 25: (7, 10), 26: (7, 10), 27: (7, 9),
            28: (6, 9), 29: (6, 9), 30: (6, 9), 31: (6, 9)}
NEAR_SHOULDER = (OX + 8.0, OY + 20.0)
# the blade bundle behind her back (with the hair squares showing between its blades)
BUNDLE = {0: (0, 11), 1: (0, 11), 2: (0, 11), 3: (0, 11), 4: (0, 11), 5: (0, 10), 6: (0, 8), 7: (0, 7), 8: (0, 7),
          9: (0, 7), 10: (0, 7), 11: (0, 7), 12: (0, 7), 13: (0, 7), 14: (0, 6), 15: (0, 5), 16: (0, 4), 17: (0, 4),
          18: (0, 4), 19: (0, 4), 20: (1, 5), 21: (1, 5), 22: (2, 5), 23: (2, 4), 24: (3, 4)}
# one blade: the design's tallest (the middle one), tip up, with its outline
BLADE = {0: (6, 6), 1: (5, 7), 2: (4, 7), 3: (4, 7), 4: (3, 7), 5: (3, 7), 6: (3, 7), 7: (3, 7), 8: (3, 7), 9: (5, 7)}
# a blade in flight (to the image right): drawn by hand in the design's blade colours - the design's upright blade
# turned a quarter is 10 x 5 and reads as a bar; this is the crescent seen from the side, the white edge on top
BLADE_FLY = ["....!!!!!!....",
             "..!!WWWWWW!!..",
             "!!RRRRRRRRRW!.",
             "!qqRRRRRRRRRW!",
             ".!!qqqqRRRR!!.",
             "...!!!!!!!!..."]
HAND_FWD = (OX + 25.0, OY + 19.0)   # the middle of the far hand with the arm forward
HEAD_ROWS = (5, 16)              # the head (hair dome, tiara, face, neck) - moved whole when she leans
CHEST_ROWS = (17, 22)
# the legs (the run puts Codex's under the body): the thighs' navy, the knees, the shins and the boots
LEGS = {27: [(10, 11)], 28: [(10, 11), (16, 16)], 29: [(10, 11), (16, 16)], 30: [(10, 11), (16, 16)],
        31: [(10, 11), (15, 16)], 32: [(8, 21)], 33: [(8, 21)], 34: [(8, 21)], 35: [(8, 21)], 36: [(7, 21)],
        37: [(7, 21)], 38: [(7, 21)], 39: [(7, 21)], 40: [(7, 21)], 41: [(7, 21)]}
SHIN_ROWS = (35, 38)             # the rows the knees fold away (the death's kneel)
# a blade of the bundle that leaves it (E: the top one flies as the effect)
BUNDLE_BLADES = {"right": {0: (10, 10), 1: (9, 11), 2: (8, 11), 3: (8, 11), 4: (8, 11), 5: (8, 9)}}
# the run: the design's own legs stepping (near boot columns, far boot columns, near lift, far lift, whole-figure rise)
RUN_STEPS = [(2, -2, 0, 0, 0), (1, -1, 0, 1, 0), (0, 0, 0, 2, 1), (-1, 1, 0, 1, 0),
             (-2, 2, 0, 0, 0), (-1, 1, 1, 0, 0), (0, 0, 2, 0, 1), (1, -1, 1, 0, 0)]


def table_mask(spec):
    m = np.zeros((128, 128), bool)
    for r, spans in spec.items():
        for c0, c1 in (spans if isinstance(spans, list) else [spans]):
            m[OY + r, OX + c0:OX + c1 + 1] = True
    return m


def letters_of(a):
    inv = {K.rgb(v): k for k, v in PAL.items()}
    L = np.full(a.shape[:2], ".", "<U1")
    for y, x in zip(*np.nonzero(a[..., 3])):
        L[y, x] = inv.get(tuple(int(v) for v in a[y, x, :3]), "?")
    return L


def codex_frames(tag):
    """Codex's 1x frames of a tag, each a 128x128 canvas with its own pivot moved onto PIVOT."""
    cells = json.load(open(os.path.join(CODEX, "irelia_cells.json"), encoding="utf-8"))
    cw, ch = cells["cell"]
    a = np.asarray(Image.open(K.lp(os.path.join(CODEX, f"irelia_{tag}_1x.png"))).convert("RGBA"))
    frs = cells["tags"][tag]
    cols, _ = K.layout(len(frs))
    out = []
    for k, fr in enumerate(frs):
        t = a[(k // cols) * ch:(k // cols + 1) * ch, (k % cols) * cw:(k % cols + 1) * cw].copy()
        out.append(K.shifted(t, PIVOT[0] - fr["pivot"][0], PIVOT[1] - fr["pivot"][1]))
    return out


class Rig:
    def __init__(self):
        self.D = K.Design(DESIGN)
        self.a = self.D.a
        self.out = self.D.outline
        op = self.a[..., 3] > 0
        self.far_m = table_mask(FAR_ARM) & op
        self.near_m = table_mask(NEAR_ARM) & op
        self.bundle_m = table_mask(BUNDLE) & op
        self.legs_m = table_mask(LEGS) & op
        self.blade = K.Part.from_canvas(self.a, table_mask(BLADE) & op, (OX + 5.5, OY + 9.5))
        self.far = K.Part.from_canvas(self.a, self.far_m, FAR_SHOULDER)
        self.near = K.Part.from_canvas(self.a, self.near_m, NEAR_SHOULDER)
        self.bundle = self.layer(self.bundle_m)
        hm = np.zeros((128, 128), bool)
        hm[OY + HEAD_ROWS[0]:OY + HEAD_ROWS[1] + 1, OX + 8:OX + 20] = True
        self.head_m = hm & op

    # ---------------------------------------------------------------------------------------- building blocks
    def layer(self, m):
        out = np.zeros_like(self.a)
        out[m] = self.a[m]
        return out

    def torso(self):
        """The design without the arms, the bundle and the legs."""
        return self.layer((self.a[..., 3] > 0) & ~self.far_m & ~self.near_m & ~self.bundle_m & ~self.legs_m)

    def arm(self, c, which, k, dx=0, dy=0):
        part = self.far if which == "far" else self.near
        joint = FAR_SHOULDER if which == "far" else NEAR_SHOULDER
        K.place(c, K.rot90(part, k), (joint[0] + dx, joint[1] + dy))
        return c

    def blade_at(self, k):
        """A single blade: 0 upright as drawn (tip up, white edge right), "r" flying to the image right (tip right,
        the white edge on top, lit from above), "l" the same to the left."""
        if k == 0:
            return self.blade
        a = np.zeros((len(BLADE_FLY), len(BLADE_FLY[0]), 4), np.uint8)
        for y, row in enumerate(BLADE_FLY):
            for x, ch in enumerate(row):
                if ch in PAL:
                    a[y, x, :3] = K.rgb(PAL[ch])
                    a[y, x, 3] = 255
        r = K.Part(a, (7.0, 3.0))
        return r if k == "r" else r.flip_h()

    def leg_layers(self):
        """The design's two legs (thigh, star knee guard, boot), split down the middle between them."""
        legs = self.layer(self.legs_m)
        near, far = legs.copy(), legs.copy()
        near[:, OX + 14:] = 0
        far[:, :OX + 14] = 0
        return near, far

    def walk_legs(self, d_near, d_far, lift_near=0, lift_far=0):
        """The design's legs stepping: each leg's boot moved whole d columns (lifted rows), the leg above it leaning
        to it from the hip (rigkit.swing_leg: whole rows moved in proportion, nothing redrawn)."""
        near, far = self.leg_layers()
        hip, ankle = OY + 27, OY + 35
        c = np.zeros_like(self.a)
        for layer, d, lift in ((far, d_far, lift_far), (near, d_near, lift_near)):
            m = layer[..., 3] > 0
            K.put(c, K.swing_leg(layer, m, hip, ankle, d, lift=lift), 0, 0)
        return c

    def pose(self, far=0, bundle=(0, 0), low=0, dx=0, legs=None, blades=(), drop_blades=()):
        """far: quarter turns of the far arm (0 hanging as drawn, 3 forward to the image right); bundle: (dx, dy) of the
        blade bundle or None (gone while its blades fly); low: rows the whole upper body sits lower (at most 1, over a
        wide stance); dx: the whole figure moved; legs: a canvas of legs (default the design's standing legs);
        blades: [(orientation, x, y)] single blades placed by their middle. The head never moves against the body."""
        up = np.zeros_like(self.a)
        if bundle is not None:
            K.put(up, self.bundle_without(drop_blades), bundle[0], bundle[1])
        K.put(up, self.torso(), 0, 0)
        self.arm(up, "near", 0)
        self.arm(up, "far", far)
        c = np.zeros_like(self.a)
        K.put(c, self.layer(self.legs_m) if legs is None else legs, 0, 0)
        K.put(c, up, 0, low)
        for k, x, y in blades:
            K.place(c, self.blade_at(k), (x, y))
        c = K.shifted(c, dx, 0)
        c[SOLES + 1:] = 0
        return c

    def bundle_without(self, names):
        b = self.bundle.copy()
        for n in names:
            b[table_mask(BUNDLE_BLADES[n])] = 0
        return b

    # ---------------------------------------------------------------------------------------- the run
    def run_frame(self, k):
        d_near, d_far, l_near, l_far, bob = RUN_STEPS[k]
        return self.pose(legs=self.walk_legs(d_near, d_far, l_near, l_far), low=bob)

    # ---------------------------------------------------------------------------------------- the death
    def kneel(self, n, dx=0, bundle=(0, 0)):
        legs = self.layer(self.legs_m)
        r_lo, r_hi = OY + SHIN_ROWS[0], OY + SHIN_ROWS[1]
        above = legs.copy()
        above[r_lo:] = 0
        below = legs.copy()
        below[:r_hi + 1] = 0
        c = np.zeros_like(self.a)
        K.put(c, below, 0, 0)
        K.put(c, above, 0, n)
        up = np.zeros_like(self.a)
        if bundle is not None:
            K.put(up, self.bundle, *bundle)
        K.put(up, self.torso(), 0, 0)
        self.arm(up, "near", 0)
        self.arm(up, "far", 0)
        K.put(c, up, 0, n)
        c = K.shifted(c, dx, 0)
        c[SOLES + 1:] = 0
        return c

    def lying(self):
        fig = self.pose(bundle=None)
        part = K.Part.from_canvas(fig, fig[..., 3] > 0, (PIVOT[0] + 0.5, SOLES + 0.5))
        turned = K.rot90(part, 1)
        c = np.zeros_like(self.a)
        K.place(c, turned, (PIVOT[0] - 20 + 0.5, SOLES + 0.5))
        ys, xs = np.nonzero(c[..., 3])
        c = K.shifted(c, 0, SOLES - ys.max())
        b = K.Part.from_canvas(self.bundle, self.bundle[..., 3] > 0, (OX + 4.0, OY + 12.0))
        tmp = np.zeros_like(self.a)
        K.place(tmp, K.rot90(b, 3), (40, 40))
        gy, gx = np.nonzero(tmp[..., 3])
        ys, xs = np.nonzero(c[..., 3])
        K.put(c, K.shifted(tmp, xs.min() - gx.max() + 3, SOLES - gy.max()), 0, 0, under=True)
        return c

    # ---------------------------------------------------------------------------------------- the strips
    def build(self, tag):
        P = self.pose
        hx, hy = HAND_FWD
        fly = lambda dx, dy=0: ("r", hx + dx, hy + dy)
        if tag == "idle":
            return [P() for _ in range(8)]
        if tag == "run":
            return [K.shifted(self.run_frame(k), 0, -RUN_STEPS[k][4]) for k in range(8)]
        if tag == "attack":
            return [P(), P(far=3), P(far=3, dx=1, blades=[fly(11)]), P(far=3, dx=1, blades=[fly(16)]), P()]
        if tag == "skill":
            wide = self.walk_legs(-2, 2)
            return [P(far=3), P(far=3, dx=1, legs=wide, blades=[fly(11, -3), fly(13, 3)]),
                    P(far=3, dx=2, legs=wide, blades=[fly(15, -3), fly(17, 3)]), P()]
        if tag == "skill2":
            return [P(), P(far=3), P(far=3, dx=1, drop_blades=["right"]), P(far=3, drop_blades=["right"]), P()]
        if tag == "skill2_w":
            shield = [(0, hx + 6, hy + 5), (0, hx + 9, hy + 3), (0, hx + 12, hy + 5)]
            return [P(), P(far=3, blades=shield), P(far=3, blades=shield),
                    P(far=3, blades=[(b[0], b[1], b[2] - 1) for b in shield]),
                    P(far=3, dx=1, blades=[fly(12, -5), fly(15, 0), fly(12, 5)]), P()]
        if tag == "ult":
            return [P(bundle=(1, -3)), P(far=3, bundle=(2, -6)), P(far=3, dx=1, bundle=None),
                    P(far=3, dx=1, bundle=None), P()]
        if tag == "hit":
            return [P(dx=-2), P(dx=-1)]
        if tag == "dead":
            return [P(dx=-1), P(dx=-1, bundle=(-1, 3)), self.kneel(2, dx=-1, bundle=(-2, 6)),
                    self.kneel(3, dx=-1, bundle=(-4, 9)), self.lying(), self.lying(), self.lying(), self.lying()]
        raise KeyError(tag)

    def head_keep(self, f):
        hm = self.head_m
        ys, xs = np.nonzero(hm)
        best = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
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
        for i, f in enumerate(frames):
            keep = None if tag == "dead" and i >= 4 else self.head_keep(f)
            g = K.finish(f, self.out, SOLES, keep=keep)
            if tag == "dead":                 # the dropped bundle over the hair leaves the hair's gaps between its blades
                g = K.fill_pinholes(g, 20, self.out)
            for h in K.holes(g):              # a slit between the lifted bundle and the hair: ink (between the boots it
                if len(h) <= 6 and max(y for y, _ in h) < OY + 32:      # stays clear, as in the design)
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
        print(f"{tag:9s}", " ".join(f"{i + 1}:{r['pieces']}p{r['holes']}h{r['orphans']}o{r['below']}b{r['area']}"
                                    for i, r in enumerate(rows)))
    if a.review:
        os.makedirs(a.review, exist_ok=True)
        K.review_sheet([(t, f) for t, f in built.items()], os.path.join(a.review, "irelia_rig_frames.png"), z=6,
                       soles=SOLES)
        K.review_gif([(t, f) for t, f in built.items()], MS, os.path.join(a.review, "irelia_rig_actions.gif"), z=6)
    if len(built) == len(TAGS):
        bad = K.write_strips(HERO, built, MS, NATIVE, CELL, CELL_PIVOT, PIVOT, check=a.check)
        print("check:", "identical" if a.check and not bad else (bad if a.check else "written"))


if __name__ == "__main__":
    main()
