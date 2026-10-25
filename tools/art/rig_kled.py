#!/usr/bin/env python3
"""league_kled's action frames: Kled's approved designs (mounted on Skaarl and on foot) and Codex's key poses after
League's clips (the user, 2026-10-24: 「Codex 照骨架画」, then 2026-10-25 「Codex都交付了 做到完美后喊我review」).

    python tools/art/rig_kled.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_kled.py                   # their frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_kled_model.py, design_kled_poses.py):
  hd/idle.png         Kled on Skaarl, 3/4 front facing right, 63 x 80 at PPU 2.0 (40 game px hat spike to claws): the
                      mounted idle, the hit;
  hd/foot.png         Kled on foot with the big axe, 58 x 60 on the same scale (A-1's head): the on-foot idle and hit;
  hd/pose_<name>.png  Codex's key poses read back at the designs' size with the design's head put in
                      (assets/source/kled/POSE_PROMPTS.md): a_wind a_chop q_throw q_yank e_lunge e_slash r_charge run1-4
                      (mounted), f_wind f_chop f_aim f_recoil f_run1-3 d_fall d_down (on foot).
Placing a pose: up and down, the lowest square on the ground row (or `lift` rows over it); across, a mounted pose by
Skaarl's eye (the yellow-green squares: his head leads the body, so his feet stay under him whatever Kled swings), an
on-foot pose by Kled's head (its json head_at against the foot design's), moved dx squares. The foot design stands with
its feet's middle (FOOT_STAND) on the mounted design's pivot column (STAND: between Skaarl's feet).
Tags: the mounted set (idle run attack skill skill2 ult hit dead) and the on-foot set the kit and the add-on play while
Skaarl has fled (f_idle f_run f_attack f_skill f_hit); death is always on foot (League's Rider_Death, mounted too).
The idles are the designs alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
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

HERO = "kled"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "kled", "hd")
STAND = 27                     # the mounted idle's standing column: between Skaarl's feet
FOOT_STAND = 22                # the foot design's: between Kled's boots
HEAD_X_FOOT = 11               # the head box's left column in hd/foot.png (design_kled_poses.HEAD 15 in hd/idle.png,
                               # moved 4 by design_kled_model.head_swap: found by matching)
DX_HAND = {}                   # squares a pose is moved by hand after its anchor
FOOT = {"f_wind", "f_chop", "f_aim", "f_recoil", "f_run1", "f_run2", "f_run3", "d_fall", "d_down", "foot"}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def eye_x(d):
    """The middle column of Skaarl's eye: the yellow-green squares (bright green, red under it, little blue)."""
    rgb = d[..., :3].astype(int)
    m = (d[..., 3] > 0) & (rgb[..., 1] > 170) & (rgb[..., 0] > 120) & (rgb[..., 0] < rgb[..., 1]) & (rgb[..., 2] < 90)
    xs = np.nonzero(m.any(0))[0]
    if not len(xs):
        return None
    return float(np.nonzero(m)[1].mean())


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        self.foot = load("foot.png")
        d = self.d
        self.eye = eye_x(d)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(60, 60, 40, 12))       # room for the axe swung out, the rope thrown, the dash
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d = self.d
        elif name == "foot":
            d = self.foot
        else:
            d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        ground = int(ys.max()) + 1
        if name == "idle":
            left = rig.ox
        elif name in FOOT:
            foot_left = rig.CX - FOOT_STAND
            if name == "foot":
                left = foot_left
            else:
                at = json.load(open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8"))["head_at"]
                left = foot_left + HEAD_X_FOOT - at[0]
        else:
            ex = eye_x(d)
            if ex is None:
                sys.exit(f"{name}: no Skaarl eye found")
            left = rig.ox + round(self.eye - ex)
        left += DX_HAND.get(name, 0) + dx
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


# ms per frame; the kit's ticks (tools/kit/build_kled.py) match these (a frame's start in ticks = ms x 0.06):
# attack 433 ms = atk_dur 26, the axe landing on the chop (a_hit 11 = 183 ms); Q 400 ms = q_dur 24, the trap leaving on
# q_rel 8 (133 ms), then the rope pulled in; E 400 ms = e_dur 24, the dash starting on e_go 5 (83 ms), the back-slash;
# R 667 ms = r_dur 40, the charge starting on r_go 12 (200 ms), Skaarl sprinting; on foot: the axe swing as the attack's,
# Pocket Pistol 400 ms = p_dur 24, fired on p_rel 8 (133 ms) and blown back
MS = {"idle": [1000], "run": [140] * 4, "attack": [183, 150, 100], "skill": [133, 100, 167], "skill2": [83, 150, 167],
      "ult": [200, 156, 156, 155], "hit": [100, 100], "dead": [140, 200, 300, 600],
      "f_idle": [1000], "f_run": [130] * 3, "f_attack": [183, 150, 100], "f_skill": [133, 150, 117], "f_hit": [100, 100]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run1_base: Skaarl's bird-like stride, the near leg then the far one)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack1: Kled rising with the axe up, chopping down in front of Skaarl, back)
    out["attack"] = [f("a_wind"), f("a_chop"), f("idle")]
    # Bear Trap on a Rope (Spell1 -> Spell1_2: the trap thrown on its rope, the rope yanked in)
    out["skill"] = [f("q_throw"), f("q_throw"), f("q_yank")]
    # Jousting (Spell3: Skaarl dashing, Kled's back-slash)
    out["skill2"] = [f("e_lunge"), f("e_lunge"), f("e_slash")]
    # Chaaaaaaaarge!!! (Spell4: Skaarl sprinting flat out, Kled yelling with the axe ahead)
    out["ult"] = [f("r_charge"), f("run2"), f("r_charge"), f("run4")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Rider_Death, mounted too: Kled hit and losing the axe, slumped on the ground)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down"), f("d_down")]
    # on foot (Skaarl fled)
    out["f_idle"] = [f("foot")]
    out["f_run"] = [f("f_run1"), f("f_run2"), f("f_run3")]
    out["f_attack"] = [f("f_wind"), f("f_chop"), f("foot")]
    # Pocket Pistol (Rider_Spell1_1: the gun out and fired, the recoil blowing him back)
    out["f_skill"] = [f("f_aim"), f("f_recoil"), f("f_recoil", dx=-2)]
    out["f_hit"] = [f("foot", dx=-2, flash=True), f("foot", dx=-1)]
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
