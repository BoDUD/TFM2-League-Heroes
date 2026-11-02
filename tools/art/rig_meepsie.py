#!/usr/bin/env python3
"""tft_meepsie's action frames: Meepsie's approved design and Codex's key poses after its own TFT clips (the user,
2026-11-01: sprites by Codex from written prompts).

    python tools/art/rig_meepsie.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_meepsie.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                     # (tft/champions/tft_meepsie), then ppu_restyle.py / ppu_hd.py --hero meepsie

The pictures (tools/art/design_meepsie_model.py, design_meepsie_poses.py):
  hd/idle.png         the moon-rock golem, 3/4 facing right, 137 x 115 at PPU 2.875 (40 game px, the mushroom tops to its
                      soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's pilot face (assets/source/meepsie/
                      POSE_PROMPTS.md, design_meepsie_poses.py): a_raise a_punch q_raise q_smash e_ready e_call r_jump
                      r_air r_land r_slam, the walk run1-8 (one full cycle of TFT's 1.3 s walk, both passings) and d_fall
                      d_down.
Placing a pose: each pose stands by its pivot (its json: the point between its feet, carried by its face) on the
design's (design_meepsie_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground; LIFT[name] rows
up in the air (the ult's leap: tft.dll moves it over the ground, the picture rises and falls).
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
from design_meepsie_poses import DESIGN_PIVOT  # noqa: E402

HERO = "meepsie"
PPU = 2.875
SRC = os.path.join(ROOT, "assets", "source", "meepsie", "hd")
WALK = ("run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8")
POSES = ("a_punch", "q_raise", "q_smash", "e_ready", "e_call", "r_jump", "r_air", "r_land", "r_slam", "d_fall",
         "d_down") + WALK
SHIFT = {}
LIFT = {"r_jump": 10, "r_air": 26}    # the leap's height in design squares (40 game px tall: 3.5 and 9 game px)
LIFT_MAX = max(LIFT.values())


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

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift - LIFT.get(name, 0)
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_meepsie.py) match these (a frame's start in ticks = ms x 0.06): attack
# 500 ms = atk_dur 30, the blow on atk_st 15 (250 ms: the fist comes down); Moon-Dust Quake 600 ms = q_dur 36, the quake
# on q_st 18 (300 ms); Healing Meeps 500 ms = e_dur 30, the meeps on e_st 14 (233 ms: the arm up); The Big Bang 900 ms =
# r_dur 54: tft.dll's leap lands r_air 30 ticks after the cast (500 ms: r_jump + r_air in the air), then the slam. The
# walk: one full cycle of both feet in 1.3 s (TFT's own, RUN_MS's shares).
MS = {"idle": [1000], "run": [160, 160, 170, 180, 200, 160, 140, 130], "attack": [250, 250], "skill": [300, 300],
      "skill2": [233, 267], "ult": [150, 350, 150, 250], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in WALK]
    # Moon-Rock Punch: Codex's a_raise lifts the near (image-left) fist, but its a_punch brings down the far one (the
    # near arm flung back): the wind-up is q_raise's far fist instead, the same fist a_punch lands
    out["attack"] = [f("q_raise"), f("a_punch")]
    out["skill"] = [f("q_raise"), f("q_smash")]                               # Moon-Dust Quake
    out["skill2"] = [f("e_ready"), f("e_call")]                               # Healing Meeps
    out["ult"] = [f("r_jump"), f("r_air"), f("r_land"), f("r_slam")]          # The Big Bang
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
