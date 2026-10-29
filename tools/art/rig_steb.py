#!/usr/bin/env python3
"""tft_steb's action frames: Steb's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-29: sprites by Codex from written prompts, then 「codex交付了 你做到完美后喊我review」).

    python tools/art/rig_steb.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_steb.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                  # (tft/champions/tft_steb), then ppu_restyle.py / ppu_hd.py --hero steb

The pictures (tools/art/design_steb_model.py, design_steb_poses.py, design_steb_run.py):
  hd/idle.png         Steb's idle, a baton on his shoulder, the other pointing down, 3/4 facing right, 80 x 106 at PPU
                      2.6 (40.8 game px, the quiff to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head (assets/source/steb/POSE_PROMPTS.md): a_wind a_hit
                      a2_wind a2_hit q_dose q_raise e_raise e_point r_cross r_squat d_fall d_down, and run1-8, his TFT
                      run on one upper body (RUN_PROMPTS.md).
Placing a pose: Codex drew every pose on the pack's 9 px grid where its reference put it (tools/art/pack_steb_poses.py:
the design pose's pelvis on one column, the soles on the ground, the design itself from column DESIGN_X), so each pose
goes across where Codex drew it (its grid_at, less the design's column) and stands on the ground. The pivot (the line
he stands on) is the middle of the design's stance (PIVOT). The run: every frame on the ground, its head on one column
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

HERO = "steb"
PPU = 2.6
SRC = os.path.join(ROOT, "assets", "source", "steb", "hd")
DESIGN_X = 29                 # the design's first column on the pose pack's 9 px grid (pack_steb_poses: 0_design.png)
PIVOT = 49                    # the design's column between his boots (row 102: 28-41 and 56-70)
POSES = ("a_wind", "a_hit", "a2_wind", "a2_hit", "q_dose", "q_raise", "e_raise", "e_point", "r_cross", "r_squat",
         "d_fall", "d_down")
LIFT = {}                     # rows off the ground
DX = {}                       # a pose moved across (squares) where Codex's place broke the sequence
RUN = [f"run{k}" for k in range(1, 9)]
RUN_DX = {}
# his TFT run: one cycle is 1.30 s (two steps); the eight frames (design_steb_run.py: Codex's whole-cycle run on one
# upper body) at pack_steb_run.RUN's clip times, each its share of an 880 ms loop (pack_steb_run.MS)
RUN_MS = [135, 102, 102, 102, 102, 102, 102, 135]


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
            left = round(meta(name)["grid_at"][0] - DESIGN_X) + DX.get(name, 0)
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


# ms per frame; the kit's ticks (tools/kit/build_steb.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the baton lands on atk_st 14 (233 ms: a_hit from 200); every other attack the kit's
# `attack2` (the other baton, the same 500 ms: a2_hit from 200); Field Medicine 600 ms = q_dur 36: the dose on
# q_heal_at 8 (133 ms, q_dose from 0), the baton raised from 250 and the strike on q_st 22 (367 ms: a_hit from 360);
# Wanted 400 ms = e_dur 24, the mark on e_st 10 (167 ms: e_point from 170); Medic's Pack 700 ms = r_dur 42, the pack
# opened on r_at 24 (400 ms: r_squat from 400)
MS = {"idle": [1000], "run": RUN_MS, "attack": [200, 300], "attack2": [200, 300], "skill": [250, 110, 240],
      "skill2": [170, 230], "ult": [400, 300], "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUN]
    # attack: one baton raised and brought down; every other attack the other baton wound back and swept across
    out["attack"] = [f("a_wind"), f("a_hit")]
    out["attack2"] = [f("a2_wind"), f("a2_hit")]
    # Field Medicine: the dose at his chest, the baton raised, the strike (the attack's own blow)
    out["skill"] = [f("q_dose"), f("q_raise"), f("a_hit")]
    # Wanted: the call, both batons upright; the aim, both batons levelled at the target
    out["skill2"] = [f("e_raise"), f("e_point")]
    # Medic's Pack: the batons crossed over his head, then the squat as the pack opens
    out["ult"] = [f("r_cross"), f("r_squat")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death: knocked to his knees, the batons slipping; down on his front
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
