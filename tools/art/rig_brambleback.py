#!/usr/bin/env python3
"""tft_brambleback's action frames: the Crimson Brambleback's approved design and Codex's key poses after its own TFT
clips (the user, 2026-10-31: sprites by Codex from written prompts).

    python tools/art/rig_brambleback.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_brambleback.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                         # (tft/champions/tft_brambleback), then ppu_restyle.py / ppu_hd.py --hero brambleback

The pictures (tools/art/design_brambleback_model.py, design_brambleback_poses.py):
  hd/idle.png         the beast crouched on all fours, 3/4 facing right, 104 x 68 at PPU 1.7 (40 game px, the back
                      branches to its claws): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/brambleback/
                      POSE_PROMPTS.md, design_brambleback_poses.py): a_raise a_swipe q_jump q_reach q_land e_crouch
                      e_rear r_rear r_slam, the gallop run1-8 and d_rear d_down.
Placing a pose: each pose stands by its pivot (its json: the point under its body, carried by its face) on the
design's (design_brambleback_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground; q_jump is
in the air (LIFT rows above the ground, as its clip springs).
The gallop: Codex's eight frames, one full cycle of TFT's knuckle-walk (the near claw swings in run1-4, the far one in
run5-8), at the clip's own 133 ms a frame.
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
from design_brambleback_poses import DESIGN_PIVOT  # noqa: E402

HERO = "brambleback"
PPU = 1.7
SRC = os.path.join(ROOT, "assets", "source", "brambleback", "hd")
WALK = ("run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8")
POSES = ("a_raise", "a_swipe", "q_jump", "q_reach", "q_land", "e_crouch", "e_rear", "r_rear", "r_slam", "d_rear",
         "d_down") + WALK
SHIFT = {}
LIFT = {"q_jump": 14}          # rows above the ground: the pounce in the air
LIFT_MAX = 4


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.pivot = DESIGN_PIVOT
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - LIFT.get(n, 0) - LIFT_MAX)
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

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows (and its own LIFT); flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
            lift += LIFT.get(name, 0)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_brambleback.py) match these (a frame's start in ticks = ms x 0.06):
# attack 533 ms = atk_dur 32, the rake on atk_st 16 (267 ms: the claw comes down); Bramble Pounce 500 ms = q_dur 30
# (the spring, the reach while it flies, the landing; MoveToTarget lands it on the target as it comes); Crimson Roar
# 600 ms = e_dur 36, the roar on e_st 14 (233 ms: it rears up); Crimson Fury 500 ms = r_dur 30, the slam on r_st 12
# (200 ms). The gallop: one full cycle in 1.07 s (TFT's own). tft.dll's leap on to the next plays `skill` too.
MS = {"idle": [1000], "run": [133] * 8, "attack": [267, 266], "skill": [150, 150, 200], "skill2": [233, 367],
      "ult": [200, 300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in WALK]
    out["attack"] = [f("a_raise"), f("a_swipe")]                              # Bramble Claw
    out["skill"] = [f("q_jump"), f("q_reach"), f("q_land")]                   # Bramble Pounce
    out["skill2"] = [f("e_crouch"), f("e_rear")]                              # Crimson Roar
    out["ult"] = [f("r_rear"), f("r_slam")]                                   # Crimson Fury
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("d_rear", flash=True), f("d_rear"), f("d_down")]
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
