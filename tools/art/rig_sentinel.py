#!/usr/bin/env python3
"""tft_sentinel's action frames: the Blue Sentinel's approved design and Codex's key poses after its own TFT clips (the
user, 2026-10-31: sprites by Codex from written prompts).

    python tools/art/rig_sentinel.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_sentinel.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                      # (tft/champions/tft_sentinel), then ppu_restyle.py / ppu_hd.py --hero sentinel

The pictures (tools/art/design_sentinel_model.py, design_sentinel_poses.py):
  hd/idle.png         the golem hunched, 3/4 facing right, 101 x 68 at PPU 1.7 (40 game px, the shoulder boulders to its
                      soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/sentinel/
                      POSE_PROMPTS.md, design_sentinel_poses.py): a_raise a_slam q_raise q_slam e_brace e_roar r_raise
                      r_slam, the walk run1-8 and d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: the point between its feet, carried by its face) on the
design's (design_sentinel_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground.
The walk: one full cycle of both feet. Codex's eight frames lift only the image-right foot (run2 and run6 both: the
other foot never leaves the ground, so the walk would read as one leg stepping twice), so the cycle is Codex's run1-4
(the right foot lifts, swings, comes down, both planted) and then the left foot's step made from run4 (STEP: its left
shin and foot, LEG_COLS / LEG_ROWS, lifted and carried forward a few squares, its own outline kept), then run8 (both
planted). Each frame stands by its pivot, which its face carries, so the head and the torso stay put.
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
from design_sentinel_poses import DESIGN_PIVOT  # noqa: E402

HERO = "sentinel"
PPU = 1.7
SRC = os.path.join(ROOT, "assets", "source", "sentinel", "hd")
WALK = ("run1", "run2", "run3", "run4", "step1", "step2", "step3", "run8")
STEP_BASE = "run4"
LEG_COLS, LEG_ROWS = (15, 36), 13       # run4's left shin and foot: columns, rows up from its lowest
STEP = {"step1": (4, 2), "step2": (8, 4), "step3": (4, 6)}   # (rows up, columns forward): lifting, highest, coming down
POSES = ("a_raise", "a_slam", "q_raise", "q_slam", "e_brace", "e_roar", "r_raise", "r_slam", "d_fall", "d_down", "run1",
         "run2", "run3", "run4", "run8")
SHIFT = {}
LIFT_MAX = 4


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def stepped(name):
    """run4 with its left shin and foot lifted STEP[name] rows and carried forward (right) that many columns; the
    figure keeps run4's height (the other foot stays on the ground row)."""
    up, fwd = STEP[name]
    p = np.pad(load(f"pose_{STEP_BASE}.png"), ((0, 0), (0, fwd), (0, 0)))
    (c0, c1), r0 = LEG_COLS, p.shape[0] - LEG_ROWS
    block = p[r0:, c0:c1].copy()
    on = block[..., 3] > 0
    p[r0:, c0:c1][on] = 0
    ys, xs = np.nonzero(on)
    p[ys + r0 - up, xs + c0 + fwd] = block[ys, xs]
    return p


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
        elif name in STEP:
            p = stepped(name)
            x, y = self.offset(STEP_BASE, p)
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


# ms per frame; the kit's ticks (tools/kit/build_sentinel.py) match these (a frame's start in ticks = ms x 0.06): attack
# 600 ms = atk_dur 36, the blow on atk_st 18 (300 ms: the fist comes down); Twin Slam 567 ms = q_dur 34, the slam on
# q_st 16 (267 ms); Carved Skin 500 ms = e_dur 30, the runes on e_st 10 (167 ms: the spread); Azure Shockwave 800 ms =
# r_dur 48, the smash on r_st 24 (400 ms). The walk: one full cycle of both feet in 1.28 s (TFT's 1.3).
MS = {"idle": [1000], "run": [160] * 8, "attack": [300, 300], "skill": [267, 300], "skill2": [167, 333],
      "ult": [400, 400], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in WALK]
    out["attack"] = [f("a_raise"), f("a_slam")]                               # Rock Fist
    out["skill"] = [f("q_raise"), f("q_slam")]                                # Twin Slam
    out["skill2"] = [f("e_brace"), f("e_roar")]                               # Carved Skin
    out["ult"] = [f("r_raise"), f("r_slam")]                                  # Azure Shockwave
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
