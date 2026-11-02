#!/usr/bin/env python3
"""tft_mightymech's action frames: the Mighty Mech's approved design and Codex's key poses after its own TFT clips (the
user, 2026-11-03: sprites by Codex from written prompts).

    python tools/art/rig_mightymech.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_mightymech.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                        # (tft/champions/tft_mightymech), then ppu_restyle.py / ppu_hd.py --hero mightymech

The pictures (tools/art/design_mightymech_model.py, design_mightymech_poses.py):
  hd/idle.png         the mech in its Ultimate form, crouched with the giant sword gripped forward, 3/4 facing right,
                      94 x 80 at PPU 2.0 (40 game px, the spike tips to its soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face where it fits (assets/source/
                      mightymech/POSE_PROMPTS.md, design_mightymech_poses.py): a_up a_down q_brace e_crouch e_air e_land
                      r_flare r_slash run1-8 d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: between its planted feet or its torso's middle; the run's
carried by its face) on the design's (design_mightymech_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on
the ground; e_air LIFT rows up (it is in the air).
The run is Codex's eight frames of TFT's sword walk (one full 2.13 s cycle), one upper body over them
(design_mightymech_poses.one_upper), played faster (the game's move speed, not TFT's stroll).
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
from design_mightymech_poses import DESIGN_PIVOT  # noqa: E402

HERO = "mightymech"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "mightymech", "hd")
RUNS = tuple(f"run{i}" for i in range(1, 9))
POSES = ("a_up", "a_down", "q_brace", "e_crouch", "e_air", "e_land", "r_flare", "r_slash", "d_fall", "d_down") + RUNS
SHIFT = {}
LIFT = {"e_air": 14}         # rows over the ground: the leap's top (the native hop carries it across)


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
        self.poses = {n: load(f"pose_{n}.png") for n in POSES}
        lefts, rights, tops = [-6], [d.shape[1] + 6], [-6]
        for n, p in self.poses.items():
            x, y = self.offset(n, p)
            lefts.append(x - 2)
            rights.append(x + p.shape[1])
            tops.append(y)
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
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0] - LIFT.get(name, 0)

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas, moved dx columns; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = self.poses[name]
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_mightymech.py, 1 tick = 16.7 ms) match these: attack 500 ms = atk_dur
# 30, the sword raised, chopping down at atk_st 15 (250 ms); Gravity Matrix 400 ms = q_dur 24, from its stance the wings
# spread and the sword planted at q_st 10 (167 ms) - the stance itself is a buff (q_stance's field) while it fights on; Mecha Leap
# 667 ms = e_dur 40: crouched, in the air from e_st 8 (133 ms) for e_air 24 ticks (400 ms), landing; Ultimate Form 1500 ms
# = r_dur 90: the wings flare, the blade blazes at r_sword 30 (500 ms) with the sword raised, the slash at r_st 50
# (833 ms) held to the end. The run: TFT's 2.13 s cycle played in 8 x 130 ms.
MS = {"idle": [1000], "run": [130] * 8,
      "attack": [250, 250], "skill": [167, 233], "skill2": [133, 400, 134],
      "ult": [500, 333, 667], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUNS]
    out["attack"] = [f("a_up"), f("a_down")]                                  # Piston Slash
    out["skill"] = [f("idle"), f("q_brace")]                                  # Gravity Matrix
    out["skill2"] = [f("e_crouch"), f("e_air"), f("e_land")]                  # Mecha Leap
    out["ult"] = [f("r_flare"), f("a_up"), f("r_slash")]                      # Ultimate Form: Super Blade
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
