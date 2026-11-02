#!/usr/bin/env python3
"""tft_brock's action frames: Brock's approved design and Codex's key poses after his own TFT clips (the user,
2026-11-02: sprites by Codex from written prompts).

    python tools/art/rig_brock.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_brock.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_brock), then ppu_restyle.py / ppu_hd.py --hero brock

The pictures (tools/art/design_brock_model.py, design_brock_poses.py):
  hd/idle.png         the stone golem standing, 3/4 facing right, 69 x 51 at PPU 1.16 (44 game px, the bonsai top to his
                      soles): the idle, the hit and the walk;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/brock/
                      POSE_PROMPTS.md, design_brock_poses.py): a_raise a_slam q_wind q_throw e_plant e_reach r_crouch
                      r_leap r_air r_land d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: the point between its feet, carried by its face) on the
design's (design_brock_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground; LIFT rows up for the
leap.
The walk is the design's own: Codex's run frames drew the legs about 40% longer than the design's stubby ones (he would
grow a head taller each time he set off), so the walk keeps the design's upper body, face and fists and steps its own
two legs (PARTS: boxes of its own squares) - each foot in turn lifted and carried forward (WALK), the body sinking a
row as it comes down, the fists (PARTS) swinging a column against the legs. The near leg (image right) is drawn over
the far one.
The ult: he crouches, springs up (r_leap, then r_air lifted LIFT rows: the kit hides him from r_go to r_at - 6 and moves
him), comes down on the target (r_air falling) and lands in r_land, then stands up through r_crouch.
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
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_brock_poses import DESIGN_PIVOT  # noqa: E402

HERO = "brock"
PPU = 1.16
SRC = os.path.join(ROOT, "assets", "source", "brock", "hd")
POSES = ("a_raise", "a_slam", "q_wind", "q_throw", "e_plant", "e_reach", "r_crouch", "r_leap", "r_air", "r_land",
         "d_fall", "d_down")
SHIFT = {}
LIFT_MAX = 40
# the walk from the design: hd/idle.png's parts as unions of (col0, col1, row0, row1) boxes, read off its square map
# (the legs' edges and the fists' touch at rows 41-48: the boxes split them where its own outline does)
PARTS = {
    "far_fist": [(0, 19, 24, 49), (19, 22, 24, 43)],
    "far_leg": [(19, 33, 43, 51), (22, 33, 41, 43)],
    "near_leg": [(33, 48, 41, 51)],
    "near_fist": [(48, 69, 24, 51), (47, 48, 24, 41)],
}
# (the body sinks a row as each foot comes down: lifting it opened a gap at the hips; the feet move at most a column
# forward and the fists stay put - carried further, each part left its outline behind as a stray dark line)
WALK = [((1, 0), (0, 0), 0, 0, 0), ((3, 1), (0, 0), 0, 0, 0), ((1, 1), (0, 0), -1, 0, 0), ((0, 0), (0, 0), 0, 0, 0),
        ((0, 0), (1, 0), 0, 0, 0), ((0, 0), (3, 1), 0, 0, 0), ((0, 0), (1, 1), -1, 0, 0), ((0, 0), (0, 0), 0, 0, 0)]


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def part_mask(d, name):
    m = np.zeros(d.shape[:2], bool)
    for c0, c1, r0, r1 in PARTS[name]:
        m[r0:r1, c0:c1] = True
    return m & (d[..., 3] > 0)


def walk_frame(d, far, near, bob, ffist, nfist):
    """The design with its legs stepped and its fists swung; the upper body moved `bob` rows (negative: sunk). -> a
    figure 4 columns wider each side and 4 rows taller (the pivot moves 4 columns right; its bottom stays the ground)."""
    P = 4
    H, W = d.shape[:2]
    out = np.zeros((H + P, W + 2 * P, 4), np.uint8)
    masks = {n: part_mask(d, n) for n in PARTS}
    upper = d.copy()
    for m in masks.values():
        upper[m] = 0

    def paste(name, top, left):
        src = d.copy()
        if name != "upper":
            src[~masks[name]] = 0
        else:
            src = upper
        ys, xs = np.nonzero(src[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty < out.shape[0])                             # a sinking fist's lowest row stops on the ground
        out[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]
    paste("upper", P - bob, P)
    paste("far_fist", P - bob, P + ffist)                    # the fists swing with the body
    paste("near_fist", P - bob, P + nfist)
    for side, (up, fwd) in (("far_leg", far), ("near_leg", near)):   # the far leg first, the near over it
        paste(side, P - up, P + fwd)
    return out


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.pivot = DESIGN_PIVOT
        lefts, rights, tops = [-6], [d.shape[1] + 6], [-LIFT_MAX - 6]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - LIFT_MAX)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot on the design's, its lowest row on the
        ground."""
        x = self.pivot - meta(name)["pivot"][0]
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, flash=False, walk=None):
        """A pose on the canvas, lifted `lift` rows; flash = the hit's whitening; walk = a WALK row."""
        rig = self.rig
        can = rig.canvas()
        if walk is not None:
            p = walk_frame(self.d, *walk)
            x, y = -4, self.d.shape[0] - p.shape[0]
        elif name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_brock.py) match these (a frame's start in ticks = ms x 0.06): attack
# 633 ms = atk_dur 38, the fists come down on atk_st 20 (333 ms); Boulder Toss 533 ms = q_dur 32, the throw on q_st 18
# (300 ms); Moss Grip 533 ms = e_dur 32, the reach on e_st 16 (267 ms); Seismic Slam 1400 ms = r_dur 84: the crouch,
# the spring (r_leap, 200 ms in), out of sight from r_go 22 (367 ms) to 48 (800 ms) while r_air hangs high, falling
# 800-900 ms, the landing on r_at 54 (900 ms), standing up through r_crouch. The walk: one full cycle of both feet in
# 1.33 s (TFT's run clip).
MS = {"idle": [1000], "run": [167] * 8, "attack": [333, 300], "skill": [300, 233], "skill2": [267, 266],
      "ult": [200, 83, 84, 433, 50, 50, 300, 200], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(None, walk=w) for w in WALK]
    out["attack"] = [f("a_raise"), f("a_slam")]                               # Quake Fist
    out["skill"] = [f("q_wind"), f("q_throw")]                                # Boulder Toss
    out["skill2"] = [f("e_plant"), f("e_reach")]                              # Moss Grip
    out["ult"] = [f("r_crouch"), f("r_leap", lift=8), f("r_leap", lift=24), f("r_air", lift=LIFT_MAX),
                  f("r_air", lift=20), f("r_air", lift=6), f("r_land"), f("r_crouch")]   # Seismic Slam
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down")]
    return out


def frames(C, tags=None):
    out = {}
    for tag, cans in actions(C).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
