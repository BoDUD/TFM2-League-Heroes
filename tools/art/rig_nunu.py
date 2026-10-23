#!/usr/bin/env python3
"""league_nunu's action frames: Nunu & Willump's approved 3/4 design and Codex's key poses after League's clips (the
user, 2026-10-23: 「Codex 照骨架画姿势」, then 「动作帧已经交付 做到完美后喊我review 有问题的话你顺便修复」).

    python tools/art/rig_nunu.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_nunu.py                   # their frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_nunu_model.py, design_nunu_poses.py):
  hd/idle.png         Nunu riding Willump, 3/4 front facing right, 51 x 63 at PPU 1.37 (46 game px pompom to soles):
                      the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's Nunu head put in
                      (assets/source/nunu/POSE_PROMPTS.md): a_wind a_swipe b_open b_bite w_pack w_push1 w_push2 w_hit
                      e_throw1 e_throw2 r_raise r_slam run1-4 d_fall d_lie.
Placing a pose: across, its body's middle (the mean column of its squares, the snowball left out) on the design's,
moved dx squares; up and down, its soles on the ground row (its lowest square) or `lift` rows over it. The idle is the
design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
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

HERO = "nunu"
PPU = 1.37
SRC = os.path.join(ROOT, "assets", "source", "nunu", "hd")
STAND = 24                     # the idle's standing column: under Willump's middle, between his feet
FEET = R.FEET


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


# the snowball's squares (pale, round, on the image right) left out of a pose's middle: the columns from which it is
# all ball, read on the readbacks
BALL_FROM = {"w_pack": 47, "w_push1": 60, "w_push2": 68}


def middle(d, name=None):
    """The mean column of a picture's squares (the snowball left out)."""
    op = d[..., 3] > 0
    if name in BALL_FROM:
        op = op.copy()
        op[:, BALL_FROM[name]:] = False
    return float(np.nonzero(op)[1].mean())


def load_pose(name):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, int(meta.get("ground", ys.max() + 1))


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.mid = middle(d)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(60, 70, 30, 12))      # room for the snowball pushed out, the arms flung, lying down
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, ground = self.d, self.d.shape[0]
        else:
            d, ground = load_pose(name)
        left = rig.ox + int(round(self.mid - middle(d, name))) + dx
        return d, (left, rig.GY - ground - lift)

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


# ms per frame; the kit's ticks (tools/kit/build_nunu.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the claws landing on the swipe frame (a_hit 11 = 183 ms; the swipe from 183 ms);
# the bite 500 ms = b_dur 30, the jaws shutting on b_bite (b_hit 14 = 233 ms; the bite from 233 ms);
# W: packing the snowball 300 ms = w_in 18, then skill_roll (pushing it, two frames, held while it rolls), skill_hit
# 233 ms = w_end 14; E 667 ms = e_dur 40: a snowball off one hand every 100 ms from e_rel 6 (100 ms), the two hands in
# turn; R: ult held while they channel (two frames of the blizzard call), ult_end 300 ms = r_end 18
MS = {"idle": [1000], "run": [150] * 4, "attack": [183, 117, 100, 67], "attack_bite": [233, 150, 117],
      "skill": [150, 150], "skill_roll": [150, 150], "skill_hit": [133, 100],
      "skill2": [100, 100, 100, 100, 100, 100, 67], "ult": [250, 250], "ult_end": [150, 150], "hit": [100, 100],
      "dead": [140, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run01: contact, passing, contact on the other leg, passing; the passing frames a row higher)
    out["run"] = [f("run1"), f("run2", lift=1), f("run3"), f("run4", lift=1)]
    # attack (League's Attack01: the far arm raised high, swiped down in front, back)
    out["attack"] = [f("a_wind"), f("a_swipe"), f("a_swipe"), f("idle")]
    # Consume's bite (Spell1: lunging with the jaws wide, snapping them shut)
    out["attack_bite"] = [f("b_open"), f("b_bite"), f("b_bite")]
    # Biggest Snowball Ever! (Spell2_In: packing the snowball and setting it rolling; Spell2: pushing it, held while it
    # rolls; Spell2_Release: the crash). The two push poses hold the ball 10 squares apart from Willump (one pushes with
    # the far hand, the other with the near), so they do not alternate - the ball would jump back and forth: w_push1
    # starts the roll, w_push2 is the roll, bobbing a row
    out["skill"] = [f("w_pack"), f("w_push1")]
    out["skill_roll"] = [f("w_push2"), f("w_push2", lift=1)]
    out["skill_hit"] = [f("w_hit"), f("w_hit")]
    # Snowball Barrage (Spell3: Nunu throwing with each hand in turn)
    out["skill2"] = [f("e_throw1"), f("e_throw2"), f("e_throw1"), f("e_throw2"), f("e_throw1"), f("e_throw2"),
                     f("idle")]
    # Absolute Zero (Spell4: the arms raised calling the blizzard, held; the slam that bursts it)
    out["ult"] = [f("r_raise"), f("r_raise", lift=1)]
    out["ult_end"] = [f("r_slam"), f("r_slam")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death01: collapsing forward, Nunu tumbling off; lying on his belly, Nunu sat by him)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_lie"), f("d_lie")]
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
