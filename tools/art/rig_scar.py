#!/usr/bin/env python3
"""tft_scar's action frames: Scar's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-28: sprites by Codex from written prompts, then 「codex交付了 做到完美后喊我review」).

    python tools/art/rig_scar.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_scar.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                  # (tft/champions/tft_scar), then ppu_restyle.py / ppu_hd.py --hero scar

The pictures (tools/art/design_scar_model.py, design_scar_poses.py):
  hd/idle.png         Scar in his spear guard, the point forward, 3/4 facing right, 84 x 76 at PPU 2.0 (38 game px,
                      the mohawk to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head (assets/source/scar/POSE_PROMPTS.md): a_wind a_thrust
                      a_back surf surf_hit q_wind q_throw q_hold e_wind e_sweep r_jump r_land d_fall d_down, and run1-8,
                      his TFT walk.
Placing a pose: Codex drew every pose on the pack's 12 px grid where its reference put it (tools/art/pack_scar_poses.py:
the design pose's pelvis on one column, the soles on y 1176, the design itself at square DESIGN_AT), so each pose goes
across where Codex drew it (its grid_at, less the design's square) and stands on the ground; the hop and the two board
frames are lifted by LIFT (the board floats 3 squares up, as Codex drew it). The pivot (the line he stands on) is the
middle of the design's stance (PIVOT). The walk: every frame on the ground, its head on one column (the frames' middles
on the pivot on average).
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "scar"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "scar", "hd")
DESIGN_AT = (10, 22)          # the design's top-left square on the pose pack's 12 px grid (pack_scar_poses: 0_design.png)
PIVOT = 30                    # the design's column between his boots (rows 72-75: 4-16 and 42-59)
POSES = ("a_wind", "a_thrust", "a_back", "surf", "surf_hit", "q_wind", "q_throw", "q_hold", "e_wind", "e_sweep",
         "r_jump", "r_land", "d_fall", "d_down")
LIFT = {"r_jump": 10, "surf": 3, "surf_hit": 3}   # rows off the ground: the hop onto the board, the board's float
DX = {}                                 # a pose moved across (rows) where Codex's place broke the sequence
RUN = [f"run{k}" for k in range(1, 9)]
RUN_DX = {}
RUN_MS = 133                            # his TFT walk: 1067 ms the cycle, 8 frames


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
        # room on every side for the poses as placed
        self.run_head = self.run_head_column()
        lefts, rights, tops = [0], [d.shape[1]], [0]
        for n in RUN + list(POSES):
            p, (left, top) = self.place(n)
            lefts.append(left)
            rights.append(left + p.shape[1])
            tops.append(top)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def run_head_column(self):
        """The design's column for the walk's head boxes: the frames' middles on the pivot, on average."""
        mids = [load(f"pose_{n}.png").shape[1] / 2 - meta(n)["head_at"][0] for n in RUN]
        return round(PIVOT - sum(mids) / len(mids))

    def place(self, name):
        """(picture, its top-left relative to the design's): across where Codex drew it (a walk frame: its head on the
        walk's column), its lowest square on the ground less its lift."""
        d = load(f"pose_{name}.png")
        if name in RUN:
            left = self.run_head - meta(name)["head_at"][0] + RUN_DX.get(name, 0)
        else:
            left = round(meta(name)["grid_at"][0] - DESIGN_AT[0]) + DX.get(name, 0)
        return d, (left, self.d.shape[0] - d.shape[0] - LIFT.get(name, 0))

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            d, (left, top) = self.d, (dx, 0)
        else:
            d, (left, top) = self.place(name)
            left += dx
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top + rig.oy, xs + left + rig.ox
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_scar.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the thrust lands on atk_st 14 (233 ms: inside a_thrust, from 133 ms); Puddle Jumper
# Surprise 667 ms = q_dur 40, the bombs fly on q_rel 18 (300 ms: inside q_throw, from 250 ms); the Spear Sweep 433 ms =
# e_dur 26, the sweep hits on e_st 12 (200 ms: inside e_sweep, from 150 ms). The Firelight Dash and the Raid move with
# MoveToTarget, as long as the way is, so they are tags of their own the kit plays by CasterAnimation: `surf` (p_surf_t
# 24 ticks: on the board, then the strike), `ride` (r_dur 50: the hop, then on the board; `ult` is the same) and `land`
# (r_land_t 18: off the board on arrival)
MS = {"idle": [1000], "run": [RUN_MS] * len(RUN), "attack": [133, 167, 200], "surf": [200, 200],
      "skill": [250, 200, 217], "skill2": [150, 283], "ult": [133, 700], "ride": [133, 700], "land": [300],
      "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUN]
    # attack (the guard drawn back, the thrust, back toward the guard)
    out["attack"] = [f("a_wind"), f("a_thrust"), f("a_back")]
    # Firelight Dash (crouched on the board, the strike from it)
    out["surf"] = [f("surf"), f("surf_hit")]
    # Puddle Jumper Surprise (leaning back, the throw, the fist up after it)
    out["skill"] = [f("q_wind"), f("q_throw"), f("q_hold")]
    # Spear Sweep (swung back, swept out)
    out["skill2"] = [f("e_wind"), f("e_sweep")]
    # Firelight Raid (the hop, on the board while he rides; off it on arrival)
    out["ult"] = [f("r_jump"), f("surf")]
    out["ride"] = [f("r_jump"), f("surf")]
    out["land"] = [f("r_land")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (thrown back, the spear flying; down on his back)
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
