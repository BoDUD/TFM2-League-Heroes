#!/usr/bin/env python3
"""tft_renni's action frames: Renni's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-29: sprites by Codex from written prompts, then 「Codex交付了 做到完美后喊我review」).

    python tools/art/rig_renni.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_renni.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_renni), then ppu_restyle.py / ppu_hd.py --hero renni

The pictures (tools/art/design_renni_model.py, design_renni_poses.py):
  hd/idle.png         Renni in her stance, the chainsaw level forward, 3/4 facing right, 86 x 77 at PPU 2.0 (38 game px,
                      the hair to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head (assets/source/renni/POSE_PROMPTS.md): a_push a_grind
                      q_charge e_guard r_ram r_heave r_hold r_slam r_after d_fall d_down, and run1-8, her TFT run.
Placing a pose: Codex drew every pose on the pack's 12 px grid where its reference put it (tools/art/pack_renni_poses.py:
the design pose's pelvis on one column, the soles on y 1176, the design itself at square DESIGN_AT), so each pose goes
across where Codex drew it (its grid_at, less the design's square) and stands on the ground. The pivot (the line she
stands on) is the middle of the design's stance (PIVOT). The run: every frame on the ground, its head on one column
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

HERO = "renni"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "renni", "hd")
DESIGN_AT = (9, 21)           # the design's top-left square on the pose pack's 12 px grid (pack_renni_poses: 0_design.png)
PIVOT = 29                    # the design's column between her boots (row 76: 0-8 and 50-60)
POSES = ("a_push", "a_grind", "q_charge", "e_guard", "r_ram", "r_heave", "r_hold", "r_slam", "r_after", "d_fall",
         "d_down")
LIFT = {}                     # rows off the ground
DX = {}                       # a pose moved across (rows) where Codex's place broke the sequence
RUN = [f"run{k}" for k in range(1, 9)]
RUN_DX = {}
RUN_MS = 141                  # her TFT run: 1133 ms the cycle, 8 frames


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


# ms per frame; the kit's ticks (tools/kit/build_renni.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the saw bites on atk_st 12, 18 and 24 (200, 300 and 400 ms: the first and the last in
# a_grind, the middle in a_push - it jolts as it bites); Chainsaw Charge: `skill` (q_dur 50, 833 ms) and the kit's
# `charge` while she runs at the target (MoveToTarget), then `grind` (q_grind_t 30, 500 ms) on arrival, the cone bitten
# at 0, 167 and 333 ms; Saw Guard 333 ms = e_dur 20; Mudrunner Slam 1500 ms = r_dur 90: the ram, the target lifted on
# r_st 14 (233 ms: from r_heave on), held overhead, then the kit's `slam` (r_slam_t 16, 267 ms) from r_slam 74 (1233 ms)
MS = {"idle": [1000], "run": [RUN_MS] * len(RUN), "attack": [190, 100, 100, 110], "skill": [833], "charge": [833],
      "grind": [120, 120, 130, 130], "skill2": [333], "ult": [233, 200, 1067], "slam": [150, 117],
      "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUN]
    # attack (the saw shoved in, jolting as it bites: three bites)
    out["attack"] = [f("a_push"), f("a_grind"), f("a_push"), f("a_grind")]
    # Chainsaw Charge (the lunge while she runs at it; on arrival the cone ground as the attack does)
    out["skill"] = [f("q_charge")]
    out["charge"] = [f("q_charge")]
    out["grind"] = [f("a_push"), f("a_grind"), f("a_push"), f("a_grind")]
    # Saw Guard (the saw raised upright in front of her)
    out["skill2"] = [f("e_guard")]
    # Mudrunner Slam (the ram, the heave, held overhead; then the slam and up from it)
    out["ult"] = [f("r_ram"), f("r_heave"), f("r_hold")]
    out["slam"] = [f("r_slam"), f("r_after")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (thrown up and back, the saw flying; down on her back)
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
