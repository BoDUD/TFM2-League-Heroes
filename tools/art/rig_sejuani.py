#!/usr/bin/env python3
"""league_sejuani's action frames: Sejuani's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-24: 「Codex 照骨架画」, then 「codex已经全部交付了 做到完美后喊我review」).

    python tools/art/rig_sejuani.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_sejuani.py                   # their frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_sejuani_model.py, design_sejuani_poses.py):
  hd/idle.png         Sejuani on Bristle, 3/4 front facing right, 82 x 72 at PPU 2.0 (36 game px horn tip to hooves):
                      the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/sejuani/POSE_PROMPTS.md): a_wind a_smash q_toss w_sweep w_raise w_slam r_wind
                      r_throw run1-4 d_rear d_down.
Placing a pose: across, Bristle's tusk tip (the rightmost ivory square in the lowest TUSK_ROWS rows) on the design's,
moved dx squares - the boar stands where he stood while she swings the flail, whatever the flail reaches; up and down,
the lowest square on the ground row, or `lift` rows over it. d_rear / d_down (the tusks thrown up / lying) by DX_HAND.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import inbetween as IB  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "sejuani"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "sejuani", "hd")
STAND = 41                     # the idle's standing column: under Bristle's middle
TUSK_ROWS = 16
# placed by hand (squares the tusk tip lands right of the design's): the boar reared up / lying
DX_HAND = {"d_rear": -6, "d_down": 8}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def tusk_tip(d):
    """The rightmost ivory square (the tusks: light, warm) in the lowest TUSK_ROWS rows."""
    rgb = d[..., :3].astype(int)
    ivory = (d[..., 3] > 0) & (rgb[..., 0] > 200) & (rgb[..., 1] > 170) & (rgb[..., 0] - rgb[..., 2] > 25)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    ivory[:ys.max() + 1 - TUSK_ROWS] = False
    xs = np.nonzero(ivory.any(0))[0]
    return int(xs.max()) if len(xs) else d.shape[1] - 1


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.tip = tusk_tip(d)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(50, 50, 50, 12))       # room for the flail swung out and raised, lying down
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        d = self.d if name == "idle" else load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        ground = int(ys.max()) + 1
        if name in DX_HAND:
            left = rig.ox + self.tip - d.shape[1] + 1 + DX_HAND[name] + dx
        else:
            left = rig.ox + self.tip - tusk_tip(d) + dx
        return d, (left, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False, spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        spins [(part, point, degrees, how)] - the flail's ice head (PARTS) turned clockwise by any angle about the end
        of its chain. Everything of the pose in no part is checked unchanged (her head and Bristle's lie far from the
        ice head: no head box helper here, as league_kled)."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        if spins:
            d = IB.vary(d, PARTS[name], self.outline, (), (), None, None, VPAD, name, (), spins)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_sejuani.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the flail landing on the lash (a_hit 11 = 183 ms); Q 400 ms = q_dur 24: the charge's gallop
# (q_go 6 = 100 ms, the rush q_t 8 = 133 ms) then the tusk toss; W 667 ms = w_dur 40: the wind-up, the sweep on w_rel1 10
# (167 ms), the flail raised, the slam on w_rel2 26 (433 ms); R 500 ms = r_dur 30: the bola whirled, flung on r_rel 14
# (233 ms)
#
# The in-betweens (2026-11-14: the attack played 3 poses, the ult 2, the death 2 and a flash; the user:
# 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): the flail's ice head turned about the end of its chain
# (inbetween.spin) - the head swinging on its chain; the chain (a square or two thick), Sejuani and Bristle never
# change. Each span above is shared out over more frames (inbetween.spans: whole ms, none under 50), so every action
# is as long as it was and its strike still begins on its millisecond (the lash at 183, the bola at 233, the fall at
# 340).
VPAD = 30
PARTS = {"a_wind": {"head": [(0, 41, 15, 63)]}, "a_smash": {"head": [(92, 7, 112, 24)]},
         "r_wind": {"head": [(60, 0, 79, 16)]}, "r_throw": {"head": [(79, 45, 93, 64)]},
         "d_rear": {"head": [(10, 62, 30, 80)]}}
HOLD = {"a_wind": (12, 44), "a_smash": (94, 18), "r_wind": (60, 4), "r_throw": (83, 48), "d_rear": (14, 64)}
MS = {"idle": [1000], "run": [150] * 4, "attack": IB.spans((183, 2), (217, 3), (67, 1)), "skill": [100, 67, 66, 167],
      "skill2": [167, 133, 133, 234], "ult": IB.spans((233, 3), (267, 3)), "hit": [100, 100],
      "dead": IB.spans((340, 3), (900, 2, (8, 92)))}


def actions(C):
    f = C.frame

    def swing(name, degrees):
        """The pose's ice head turned clockwise by `degrees` (negative: counter-clockwise) about its chain's end."""
        return [("head", HOLD[name], degrees, "under")]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run: stretched, the front feet landing, gathered, the hind legs pushing off)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack1: the flail flung behind, lashed out forward, back)
    # (the head swinging behind, flung back; lashed out with the head still lagging, out, whipping past; back)
    out["attack"] = [f("a_wind", spins=swing("a_wind", 40)), f("a_wind"), f("a_smash", spins=swing("a_smash", -35)),
                     f("a_smash"), f("a_smash", spins=swing("a_smash", 20)), f("idle")]
    # Arctic Assault (Spell1 -> Spell1_Hit: the charge at a gallop, the tusks tossed up)
    out["skill"] = [f("run1"), f("run2"), f("run3"), f("q_toss")]
    # Winter's Wrath (Spell2_A: the wind-up and the sweep; Spell2_B: raised, slammed down ahead)
    out["skill2"] = [f("a_wind"), f("w_sweep"), f("w_raise"), f("w_slam")]
    # Glacial Prison (Spell4: the bola whirled overhead, flung)
    # (the bola whirling over her head in three turns of its head; flung with the head still swinging round, out,
    # swinging on)
    out["ult"] = [f("r_wind", spins=swing("r_wind", 60)), f("r_wind", spins=swing("r_wind", 120)), f("r_wind"),
                  f("r_throw", spins=swing("r_throw", -40)), f("r_throw"), f("r_throw", spins=swing("r_throw", 25))]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: Bristle rearing, Sejuani thrown off; both down)
    # (struck; the flail flying loose, its head tumbling on its chain; down)
    out["dead"] = [f("d_rear", flash=True), f("d_rear", spins=swing("d_rear", 40)),
                   f("d_rear", spins=swing("d_rear", 80)), f("d_down", lift=3), f("d_down")]
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
