#!/usr/bin/env python3
"""tft_thex's action frames: T-Hex's approved design and Codex's key poses after its own TFT clips (the user,
2026-11-02: sprites by Codex from written prompts).

    python tools/art/rig_thex.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_thex.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                  # (tft/champions/tft_thex), then ppu_restyle.py / ppu_hd.py --hero thex

The pictures (tools/art/design_thex_model.py, design_thex_poses.py):
  hd/idle.png         the mech rex standing, 3/4 facing right, 101 x 76 at PPU 1.9 (40 game px, the ear spikes to its
                      soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/thex/
                      POSE_PROMPTS.md, design_thex_poses.py): a_aim a_recoil q_fire e_charge e_bite r_open r_fire
                      run1-8 d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: between its planted feet; the run's carried by its face) on
the design's (design_thex_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground.
The run is Codex's eight frames of TFT's run clip (one full 1.27 s cycle: the far foot's swing in run1-4, the near
foot's in run5-8), the head steady over them.
The gatling kicks: the attack's bullets (kit atk_st + k x a_gap) kick a_aim a column back, the last rears it up in
a_recoil; the ult's three laser beats (r_st + k x r_every) each kick r_fire a column back.
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
from design_thex_poses import DESIGN_PIVOT  # noqa: E402

HERO = "thex"
PPU = 1.9
SRC = os.path.join(ROOT, "assets", "source", "thex", "hd")
RUNS = tuple(f"run{i}" for i in range(1, 9))
POSES = ("a_aim", "a_recoil", "q_fire", "e_charge", "e_bite", "r_open", "r_fire", "d_fall", "d_down") + RUNS
SHIFT = {}


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
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

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


# ms per frame; the kit's ticks (tools/kit/build_thex.py, 1 tick = 16.7 ms) match these: attack 500 ms = atk_dur 30,
# its four bullets at atk_st 10 + k x a_gap 3 (167, 217, 267, 317 ms): the first and third kick a_aim a column back,
# the last (the fourth attack's bonus) rears it up in a_recoil (a_aim <-> a_recoil every 50 ms flickered: the two
# stand a head apart); Homing Missiles
# 600 ms = q_dur 36, the pods half open, then wide open at q_st 14 (233 ms) as the missiles fly; Rex Charge 500 ms =
# e_dur 30, low through the charge, the jaws thrown open for the bite on arrival; Hex Armory 3333 ms = r_dur 200: the
# pods open, then the three beats at r_st 20 + k x r_every 60 (333, 1333, 2333 ms) each kick the body back a column.
# The run: TFT's 1.27 s cycle in eight steps.
MS = {"idle": [1000], "run": [159, 159, 159, 159, 159, 159, 159, 159],
      "attack": [167, 50, 50, 50, 183], "skill": [233, 367], "skill2": [267, 233],
      "ult": [333, 100, 900, 100, 900, 100, 900], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUNS]
    out["attack"] = [f("a_aim"), f("a_aim", dx=-1), f("a_aim"), f("a_aim", dx=-1), f("a_recoil")]   # Gatling
    out["skill"] = [f("r_open"), f("q_fire")]                                 # Homing Missiles
    out["skill2"] = [f("e_charge"), f("e_bite")]                              # Rex Charge
    out["ult"] = [f("r_open")] + [f("r_fire", dx=-1), f("r_fire")] * 3       # Hex Armory
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
