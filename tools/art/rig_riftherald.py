#!/usr/bin/env python3
"""tft_riftherald's action frames: the Rift Herald's approved design and Codex's key poses after its own TFT clips (the
user, 2026-11-02: sprites by Codex from written prompts; 「有问题的地方你帮忙修复 完美后喊我review」).

    python tools/art/rig_riftherald.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_riftherald.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                        # (tft/champions/tft_riftherald), then ppu_restyle.py / ppu_hd.py --hero riftherald

The pictures (tools/art/design_riftherald_model.py, design_riftherald_poses.py):
  hd/idle.png         the void beast hunched under its shell, 3/4 facing right, 102 x 88 at PPU 2.0 (44 game px, the
                      shell's top to its soles): the idle, the hit and the scuttle;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/riftherald/
                      POSE_PROMPTS.md): a_raise a_strike q_wind q_spin q_end e_rear e_flip e_charge r_crouch r_slam
                      d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: the point between its hind feet, carried by its face) on the
design's (design_riftherald_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground; LIFT[name] rows
up for the flip into the charge.
The scuttle is the design's own: Codex's six run frames differ from each other in body size and style (run1 a head
taller), so the scuttle keeps the design's shell, face and pincer and steps its own two hind feet (PARTS: boxes of its own
squares) - each foot in turn lifted and set a column forward (WALK), the body sinking a row as it comes down, the pincer
still. The near foot (image right) is drawn over the far one.
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
from design_riftherald_poses import DESIGN_PIVOT  # noqa: E402

HERO = "riftherald"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "riftherald", "hd")
POSES = ("a_raise", "a_strike", "q_wind", "q_spin", "q_end", "e_rear", "e_flip", "e_charge", "r_crouch", "r_slam",
         "d_fall", "d_down")
SHIFT = {}
LIFT = {"e_flip": 12}         # the flip is off the ground (TFT's charge clip at 340 ms: 82 raw px over the ground line)
LIFT_MAX = 16
# the scuttle from the design: hd/idle.png's parts as unions of (col0, col1, row0, row1) boxes, read off its square map
# (C:/t/rh_work/design_low.png, 10x): the far hind foot, the near hind foot, the big near pincer
PARTS = {
    "far_leg": [(36, 52, 74, 88)],
    "near_leg": [(57, 74, 77, 88)],
    "pincer": [(74, 102, 52, 88)],
}
# (far foot (up, forward), near foot (up, forward), body bob (negative: sunk), pincer swing): one full cycle, each foot
# lifted and set down once (the tft run rule: both passings in the loop)
# (the pincer stays put: swung a column, its box left a dark seam down the claw - Brock's fists did the same)
WALK = [((2, 1), (0, 0), 0, 0), ((1, 1), (0, 0), -1, 0), ((0, 0), (0, 0), 0, 0),
        ((0, 0), (2, 1), 0, 0), ((0, 0), (1, 1), -1, 0), ((0, 0), (0, 0), 0, 0)]


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


def walk_frame(d, far, near, bob, pin):
    """The design with its hind feet stepped and its pincer swung; the upper body moved `bob` rows (negative: sunk). ->
    a figure 4 columns wider each side and 4 rows taller (the pivot moves 4 columns right; its bottom stays the
    ground)."""
    P = 4
    H, W = d.shape[:2]
    out = np.zeros((H + P, W + 2 * P, 4), np.uint8)
    masks = {n: part_mask(d, n) for n in PARTS}
    upper = d.copy()
    for m in masks.values():
        upper[m] = 0

    def paste(name, top, left):
        src = upper if name == "upper" else np.where(masks[name][..., None], d, 0).astype(np.uint8)
        ys, xs = np.nonzero(src[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = ty < out.shape[0]                               # a sinking part's lowest row stops on the ground
        out[ty[ok], tx[ok]] = src[ys[ok], xs[ok]]
    paste("upper", P - bob, P)
    for side, (up, fwd) in (("far_leg", far), ("near_leg", near)):   # the far foot first, the near over it
        paste(side, P - up, P + fwd)
    paste("pincer", P - bob, P + pin)                        # the pincer in front of both feet
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
            tops.append(y - LIFT.get(n, 0))
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

    def frame(self, name, dx=0, flash=False, walk=None):
        """A pose on the canvas (LIFT rows up where it has one); flash = the hit's whitening; walk = a WALK row."""
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
        left, top = rig.ox + x + dx, rig.oy + y - LIFT.get(name, 0)
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_riftherald.py) match these (a frame's start in ticks = ms x 0.06):
# attack 667 ms = atk_dur 40, the pincer comes down on atk_st 22 (367 ms); Spin Sweep 667 ms = q_dur 40, the sweep on q_st
# 20 (333 ms: q_spin); Void Charge 1000 ms = e_dur 60: reared up for e_wind 24 ticks (400 ms), then the kit's own
# CasterAnimation `charge` (40 ticks: the flip, then shell first) holds over the MoveToTarget; Warp Armor 1167 ms =
# r_dur 70: the crouch, the roar reared up (the kit's roar picture), the slam on r_st 48 (800 ms). The scuttle: one full
# cycle of both feet in 1.17 s (TFT's run clip).
MS = {"idle": [1000], "run": [195] * 6, "attack": [367, 300], "skill": [333, 167, 167],
      "skill2": [400, 100, 500], "charge": [117, 550], "ult": [250, 550, 367], "hit": [100, 100],
      "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(None, walk=w) for w in WALK]
    out["attack"] = [f("a_raise"), f("a_strike")]                          # Rending Pincer
    out["skill"] = [f("q_wind"), f("q_spin"), f("q_end")]                  # Spin Sweep
    out["skill2"] = [f("e_rear"), f("e_flip"), f("e_charge")]              # Void Charge
    out["charge"] = [f("e_flip"), f("e_charge")]                           # its run (the kit's CasterAnimation)
    out["ult"] = [f("r_crouch"), f("e_rear"), f("r_slam")]                 # Warp Armor
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
