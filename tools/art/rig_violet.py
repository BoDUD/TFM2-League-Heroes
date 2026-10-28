#!/usr/bin/env python3
"""tft_violet's action frames: Violet's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-28: sprites by Codex from written prompts, then 「Codex交付了 做到完美后喊我review」).

    python tools/art/rig_violet.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_violet.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_violet), then ppu_restyle.py / ppu_hd.py --hero violet

The pictures (tools/art/design_violet_model.py, design_violet_poses.py):
  hd/idle.png         Violet in her fighting stance, both gauntlets up at her chest, 3/4 facing right, 68 x 76 at PPU
                      2.0 (38 game px, the hair to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head put in (assets/source/violet/POSE_PROMPTS.md): a_wind
                      a_punch a_back q_jab1 q_jab2 q_coil q_upper q_land e_dash e_punch r_air r_land r_slam d_fall d_down,
                      and run1-8, her TFT jog
                      redrawn (assets/source/violet/RUN_PROMPTS.md).
Placing a pose: Codex drew every pose on the pack's 1254 canvas about where its reference put it (the references were
placed by tools/art/pack_violet_poses.py: the design pose's pelvis on one column, the soles on y 1176, the design itself
at square (18, 22) of the 12 px grid), so each pose goes across where Codex drew it (its grid_at, design_violet_poses.py's
json, less the design's square). Its soles did NOT keep to the ground line (y 1104-1215 against 1176), so up and down
every pose stands on the ground, and the two in the air are lifted by LIFT. The pivot (the line she stands on) is the
middle of the design's stance (PIVOT). The run (Vander's way): every frame on the ground, its pasted head on one column
(the frames' middles on the pivot on average).
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

HERO = "violet"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "violet", "hd")
DESIGN_AT = (18, 22)          # the design's top-left square on the pose pack's 12 px grid (pack_violet_poses: 0_design.png)
PIVOT = 32                    # the design's column between her boots (rows 72-75: 0-10 and 52-67)
POSES = ("a_wind", "a_punch", "a_back", "q_jab1", "q_jab2", "q_coil", "q_upper", "q_land", "e_dash", "e_punch",
         "r_air", "r_land", "r_slam", "d_fall", "d_down")
LIFT = {"q_upper": 6, "r_air": 14}      # rows off the ground: the uppercut's hop, the leap
DX = {}                                 # a pose moved across (rows) where Codex's place broke the sequence
RUN = [f"run{k}" for k in range(1, 9)]
# the run redrawn by Codex (design_violet_poses.RUN_SRC): her TFT run at eight even times, played in order; the near
# (navy) leg leads in run1-5, the far one in run6-8
RUN_DX = {}
RUN_MS = 117                            # her TFT run: 933 ms the cycle, 8 frames


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
        """The design's column for the run's head boxes: the frames' middles on the pivot, on average."""
        mids = [load(f"pose_{n}.png").shape[1] / 2 - meta(n)["head_at"][0] for n in RUN]
        return round(PIVOT - sum(mids) / len(mids))

    def place(self, name):
        """(picture, its top-left relative to the design's): across where Codex drew it (a run frame: its head on the
        run's column), its lowest square on the ground less its lift."""
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


# ms per frame; the kit's ticks (tools/kit/build_violet.py) match these (a frame's start in ticks = ms x 0.06):
# attack 367 ms = atk_dur 22, the punch lands on atk_st 10 (167 ms: inside the punch frame, from 117 ms); the 1-2-3
# Combo 900 ms = q_dur 54: the jabs land on q_j1 8 / q_j2 20 (133 / 333 ms: inside q_jab1, q_jab2), the uppercut on
# q_j3 36 (600 ms: inside q_upper, from 583 ms). The Rush and the Undercity Fist rush in with MoveToTarget, which takes
# as long as the way is, so their casts only hold the run-up (skill2: flung forward; ult: crouched, then in the air)
# and the blow is its own tag, played by a CasterAnimation in the dash's end_effects on arrival with the hit: `punch`
# (e_hit_t ticks) and `slam` (the landing and the slam, r_slam_t ticks)
MS = {"idle": [1000], "run": [RUN_MS] * len(RUN), "attack": [117, 150, 100],
      "skill": [250, 200, 133, 200, 117], "skill2": [400], "punch": [267], "ult": [100, 567], "slam": [67, 233],
      "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUN]
    # attack (her TFT attack: wound up, the lunging straight punch, back toward the stance)
    out["attack"] = [f("a_wind"), f("a_punch"), f("a_back")]
    # 1-2-3 Combo (TFT's spell: a jab, the other jab, the coil, the jumping uppercut, landing)
    out["skill"] = [f("q_jab1"), f("q_jab2"), f("q_coil"), f("q_upper"), f("q_land")]
    # Gauntlet Rush (flung forward; on arrival the punch)
    out["skill2"] = [f("e_dash")]
    out["punch"] = [f("e_punch")]
    # Undercity Fist (crouched, the leap; on arrival the landing and the slam)
    out["ult"] = [f("q_land"), f("r_air")]
    out["slam"] = [f("r_land"), f("r_slam")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (knocked back, down on her back)
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
