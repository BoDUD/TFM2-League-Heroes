#!/usr/bin/env python3
"""league_aurora's action frames: her approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-23: 「Codex 照骨架画姿势」, then 「动作帧也交付了 你做到完美后喊我review」).

    python tools/art/rig_aurora.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_aurora.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_aurora_model.py, design_aurora_poses.py, design_aurora_legs.py):
  hd/idle.png             her, 3/4 front facing right, 53 x 104 at PPU 2.25 (38 game px hat top to soles, the ears
                          above): the idle, the hit;
  hd/pose_<name>.png      Codex's key poses read back at the design's size with the design's head put in
                          (assets/source/aurora/POSE_PROMPTS.md; the long-legged ones' legs drawn again in
                          LEGS_PROMPTS.md): a_wind a_point q_wind q_cast q_catch e_push e_hop r_reach r_leap r_land w_hop
                          run1-4 d_stagger d_slump.
Placing a pose (league_illaoi's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares, its soles on the ground row (its lowest square) or `lift` rows over it. The idle is the design alone
(no breathing: hero_reels cuts her idle snippets from these actions).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
import pack_aurora_poses as PK  # noqa: E402
from build_aurora import P as KIT  # noqa: E402

HERO = "aurora"
PPU = 2.25
SRC = os.path.join(ROOT, "assets", "source", "aurora", "hd")
STAND = 31                     # the idle's standing column: under her middle, between her boots
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
FEET = R.FEET


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(meta.get("ground", ys.max() + 1))


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(60, 90, 40, 12))      # room for the wand held out, the hops
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name)
        return d, (rig.ox + HEAD[0] - hx + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


def ms_of(tick):
    return round(tick * 1000 / 60)


# ms per frame; the kit's ticks (tools/kit/build_aurora.py) match these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27, the bolt off the wand pointed out (a_rel 10 = 167 ms; the point from 120 ms);
# Twofold Hex 500 ms = q_dur 30, the hex flung on the sweep (q_rel 12 = 200 ms; the cast from 150 ms), the recall after;
# The Weirding 500 ms = e_dur 30, the blast off the wand thrust out (e_rel 12 = 200 ms; the push to 220 ms), then the
# hop back (MoveBack 2 ticks after the release); Between Worlds 600 ms = r_dur 36, on her toes, the leap (the dash from
# r_rel 14 = 233 ms; the leap from 200 ms), the landing crouch; Across the Veil 200 ms = the veil's 12-tick animation
MS = {"idle": [1000], "run": [150] * 4,
      "attack": [120, ms_of(KIT["atk_dur"]) - 120 - 120, 120],
      "skill": [150, 200, ms_of(KIT["q_dur"]) - 350],
      "skill2": [220, ms_of(KIT["e_dur"]) - 220],
      "ult": [200, 250, ms_of(KIT["r_dur"]) - 450],
      "veil": [200],
      "hit": [100, 100], "dead": [140, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's run_new_4: contact, passing, contact on the other leg, passing; the wand on her shoulder)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (League's attack6: the wand raised by her head, then pointed out - the bolt - and back)
    out["attack"] = [f("a_wind"), f("a_point", dx=-1), f("idle")]
    # Twofold Hex (Spell1: a small hop with the wand up, the sweep - the hex flies - and the recall, the wand held up)
    out["skill"] = [f("q_wind", lift=3), f("q_cast", dx=1), f("q_catch", lift=2)]
    # The Weirding (Spell3: the deep squat thrusting the wand - the blast - then the hop back)
    out["skill2"] = [f("e_push", dx=1), f("e_hop", dx=-3, lift=8)]
    # Between Worlds (Spell4: up on her toes, the high leap - the dash - and the landing crouch with the wand down)
    out["ult"] = [f("r_reach", lift=2), f("r_leap", dx=2, lift=14), f("r_land", dx=2)]
    # Across the Veil (Spell2: curled up in the hop back)
    out["veil"] = [f("w_hop", dx=-3, lift=8)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: reeling back, the arms flung out; sitting down, the wand dropped)
    out["dead"] = [f("d_stagger", dx=-1, flash=True), f("d_stagger", dx=-2), f("d_slump", dx=-2), f("d_slump", dx=-2)]
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
