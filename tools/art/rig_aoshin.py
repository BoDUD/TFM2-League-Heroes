#!/usr/bin/env python3
"""tft_aoshin's action frames: Ao Shin's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-28: sprites by Codex from written prompts).

    python tools/art/rig_aoshin.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_aoshin.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_aoshin), then ppu_restyle.py / ppu_hd.py --hero aoshin

The pictures (tools/art/design_aoshin_model.py, design_aoshin_poses.py):
  hd/idle.png         the storm dragon hovering upright, 3/4 facing right, 74 x 76 at PPU 2.0 (38 game px, the horns
                      to the lowest curl of the tail): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's density (assets/source/aoshin/POSE_PROMPTS.md): a_coil a_lunge
                      a_back q_rear q_breath e_rise r_call r_storm run1-4 d_hit d_back d_away.
Placing a pose: the pack put every pose's hips (Tail0) on one canvas column and its lowest point on one ground line, so
a pose's hips go on the design's (DESIGN_HIPS) and its lowest row on the design's (his tail's lowest curl hangs there).
He hovers: the idle bobs a game pixel; the run (his TFT fly, four frames) rides LIFT_RUN higher, as the flight does.
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

HERO = "aoshin"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "aoshin", "hd")
DESIGN_HIPS = 39.75           # the design's hip column (pack_aoshin_poses: Tail0 placed by the box ratio)
PIVOT = 40                    # the sprite's pivot column in the design
POSES = ("a_coil", "a_lunge", "a_back", "q_rear", "q_breath", "e_rise", "r_call", "r_storm", "run1", "run2", "run3",
         "run4", "d_hit", "d_back", "d_away")
BOB = 2                       # the idle's hover (canvas rows: 1 game px)
LIFT_RUN = 4                  # the flight above the idle's ground line (canvas rows)
LIFT_MAX = 8                  # the highest lift used (room above the poses)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def hips(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["hips"]


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
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
            H, W, px, ground = d.shape[0], d.shape[1], PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its hips on the design's, its lowest row on the
        ground."""
        return round(DESIGN_HIPS - hips(name)), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
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


# ms per frame; the kit's ticks (tools/kit/build_aoshin.py) match these (a frame's start in ticks = ms x 0.06): attack
# 400 ms = atk_dur 24, the ball leaves on a_rel 9 (150 ms: inside the lunge, from 133 ms); Breath 500 ms = q_dur 30, the
# bolt leaves on q_rel 12 (200 ms: the breath frame from 183 ms); Cloud Ride 300 ms = e_dur 18 (off on e_rel 4 = 67 ms:
# the rise); Lightning Storm 1700 ms = r_dur 102 (r_rel 24 + 12 x 6 + 6): the call to r_rel (400 ms), then the storm
# held with arms wide, swaying, while the bolts fall
MS = {"idle": [600, 600], "run": [133] * 4, "attack": [133, 150, 117], "skill": [183, 217, 100],
      "skill2": [67, 233], "ult": [400, 325, 325, 325, 325], "hit": [100, 100], "dead": [100, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle"), f("idle", lift=BOB)]
    out["run"] = [f(f"run{k}", lift=LIFT_RUN) for k in (1, 2, 3, 4)]
    # attack (his TFT lunge: coiled back, thrown forward spitting the ball, back upright)
    out["attack"] = [f("a_coil"), f("a_lunge"), f("a_back")]
    # Thunder Breath (rearing up drawing breath, the neck thrust out breathing the bolt, back)
    out["skill"] = [f("q_rear"), f("q_breath"), f("a_back")]
    # Cloud Ride (pulled back, leaning back and rising away)
    out["skill2"] = [f("a_back"), f("e_rise", lift=LIFT_RUN)]
    # Lightning Storm (claws raised, then arms flung wide calling the storm, swaying a pixel while it rains)
    out["ult"] = [f("r_call"), f("r_storm"), f("r_storm", lift=BOB), f("r_storm"), f("r_storm", lift=BOB)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (struck upright, thrown face-up, turned away hanging limp)
    out["dead"] = [f("d_hit", flash=True), f("d_hit"), f("d_back"), f("d_away")]
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
