#!/usr/bin/env python3
"""tft_sevika's action frames: Sevika's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-29: sprites by Codex from written prompts, then 「codex交付了 做到完美后喊我review」).

    python tools/art/rig_sevika.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_sevika.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_sevika), then ppu_restyle.py / ppu_hd.py --hero sevika

The pictures (tools/art/design_sevika_model.py, design_sevika_poses.py):
  hd/idle.png         Sevika's standing guard, the mechanical arm hanging in front of her, 3/4 facing right, 53 x 70 at
                      PPU 1.8 (38.9 game px, the hair to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head (assets/source/sevika/POSE_PROMPTS.md): a_wind a_punch
                      a2_raise a2_clamp q_flame q_flame2 e_wind e_punch e_back r_dash r_raise r_bite r_lift d_fall
                      d_down, and run1-8, her TFT run.
Placing a pose: Codex drew every pose on the pack's 12 px grid where its reference put it (tools/art/pack_sevika_poses.py:
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

HERO = "sevika"
PPU = 1.8
SRC = os.path.join(ROOT, "assets", "source", "sevika", "hd")
DESIGN_AT = (25, 28)          # the design's top-left square on the pose pack's 12 px grid (pack_sevika_poses: 0_design.png)
PIVOT = 26                    # the design's column between her boots (row 68: 4-14 and 35-49)
POSES = ("a_wind", "a_punch", "a2_raise", "a2_clamp", "q_flame", "q_flame2", "e_wind", "e_punch", "e_back", "r_dash",
         "r_raise", "r_bite", "r_lift", "d_fall", "d_down")
LIFT = {}                     # rows off the ground
# a pose moved across (squares) where Codex's place broke the sequence: the two boots' middle on the idle's (27: boots
# 5-13 and 35-48), measured on the boot colours of the lowest rows (2026-10-29); the chomp's frames by the back boot
# (the arm hides the front one): r_raise's 3-15
DX = {"a_wind": -2, "a_punch": 12, "a2_clamp": -15, "q_flame": 7, "q_flame2": 5, "e_wind": -10, "e_punch": 10,
      "e_back": -3, "r_dash": -3, "r_raise": -3, "r_bite": 11, "r_lift": -2}
RUN = [f"run{k}" for k in range(1, 9)]
RUN_DX = {}
RUN_MS = 117                  # her TFT run: 934 ms the cycle, 8 frames


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


# ms per frame; the kit's ticks (tools/kit/build_sevika.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the punch lands on atk_st 12 (200 ms: a_punch from 170); every third attack the kit's
# `attack2` (the clamp, the same 500 ms, landing at 200 ms: a2_clamp from 170); Flamethrower: `skill` then the kit's
# `flame` over q_dur 72 (1200 ms: the two flame frames by turns, the recoil); Extendo-Punch 667 ms = e_dur 40, the fist
# leaves on e_st 14 (233 ms: e_punch from 200); Chomp: `ult` then the kit's `dash` (r_dur 70) while she dashes, and on
# arrival `chomp` (r_chomp_t 40, 667 ms): the bites on r_first 8 and 8 + r_gap 18 (133 and 433 ms: r_bite from 120 and
# from 430)
MS = {"idle": [1000], "run": [RUN_MS] * len(RUN), "attack": [170, 330], "attack2": [170, 330], "skill": [100],
      "flame": [100] * 12, "skill2": [200, 250, 217], "ult": [100], "dash": [1167], "chomp": [120, 180, 130, 237],
      "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUN]
    # attack (the arm drawn back, the punch thrown); every third the claws raised and clamped down
    out["attack"] = [f("a_wind"), f("a_punch")]
    out["attack2"] = [f("a2_raise"), f("a2_clamp")]
    # Flamethrower (the arm levelled; the recoil by turns while the flame roars)
    out["skill"] = [f("q_flame")]
    out["flame"] = [f("q_flame"), f("q_flame2")] * 6
    # Extendo-Punch (the arm pulled back, thrown out - the fist flies as its own picture - and drawn back in)
    out["skill2"] = [f("e_wind"), f("e_punch"), f("e_back")]
    # Chomp (the low dive at the target; there the claws raised, bitten down, raised again, bitten down)
    out["ult"] = [f("r_dash")]
    out["dash"] = [f("r_dash")]
    out["chomp"] = [f("r_raise"), f("r_bite"), f("r_lift"), f("r_bite")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (thrown back, the arm flung out; down on her back)
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
