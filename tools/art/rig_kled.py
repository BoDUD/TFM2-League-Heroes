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
import inbetween as IB  # noqa: E402
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


# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): boxes in each pose picture's own squares.
# The axe turns about the fist that holds it (inbetween.spin: the head and the shaft past the fist); the axe knocked
# out of his hand in the death tumbles on by itself; the bear trap's rope is a line one square thick, so it only
# slides along itself by whole squares, back in under his hand (the trap on its way out, reeled in); the pistol arm
# turns about the elbow. Kled's head, Skaarl and the rest of the body are in no part.
VPAD = 34                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "a_wind": {"axe": [(0, 0, 19, 33)]},
    "a_chop": {"axe": [(86, 22, 109, 22), (83, 23, 109, 25), (86, 26, 109, 39), (87, 40, 109, 40), (85, 41, 109, 41),
                       (88, 42, 109, 43), (89, 44, 109, 44), (90, 45, 109, 45), (91, 46, 109, 46), (92, 47, 109, 47),
                       (93, 48, 109, 48), (96, 49, 109, 50)]},
    "q_throw": {"rope": [(65, 24, 107, 42)]},
    "q_yank": {"rope": [(47, 37, 56, 37), (47, 38, 62, 38), (47, 39, 72, 39), (56, 40, 80, 40), (63, 41, 83, 41),
                        (73, 42, 83, 42), (84, 36, 97, 47)]},
    "e_lunge": {"axe": [(91, 8, 114, 40)]},
    "e_slash": {"axe": [(0, 18, 23, 46)]},
    "r_charge": {"axe": [(90, 16, 105, 40)]},
    "d_fall": {"axe": [(55, 0, 98, 32)]},
    "f_wind": {"axe": [(0, 38, 29, 61)]},
    "f_chop": {"axe": [(50, 38, 78, 59)]},
    "f_recoil": {"gun": [(65, 22, 80, 41)]},
}
# the point each pose's part turns about: the fist on the axe, the flying axe's middle, the pistol arm's elbow
AT = {("a_wind", "axe"): (17, 35), ("a_chop", "axe"): (84, 22), ("e_lunge", "axe"): (90, 28),
      ("e_slash", "axe"): (25, 36), ("r_charge", "axe"): (89, 33), ("d_fall", "axe"): (76, 16),
      ("f_wind", "axe"): (31, 44), ("f_chop", "axe"): (47, 46), ("f_recoil", "gun"): (66, 40)}


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

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - parts of the pose (PARTS) moved by whole squares, "under" the rest of them or
        "over" it; spins [(part, point, degrees, how)] - a part turned clockwise by any angle about a point, then
        moved if `moves` names it too. Everything of the pose that is in none of its parts is checked unchanged."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        if moves or spins:
            d = IB.vary(d, PARTS[name], self.outline, moves, (), None, None, VPAD, name, (), spins)
            left, top = left - VPAD, top - VPAD
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
#
# The in-betweens (2026-11-14: the attacks played 3 poses, the trap, Jousting and the pistol 2, the charge 3, the death
# 2 and a flash): each span above is shared out over more frames (inbetween.spans: whole ms, none under 50), so every
# action is as long as it was and its strike still begins on its millisecond - the chop at 183, the trap leaving at
# 133 and yanked from 233, the dash at 83 and the back-slash at 233, the charge at 200, the shot at 133, the slump at
# 340. A frame that is only its neighbour moved whole is no new pose: one stays only where the move is the motion
# (the lunge of a strike, the recoil, the fall), never more than two frames of one drawing in a row. The runs are
# the drawn steps as they were.
CHOP = IB.spans((183, 3), (150, 3), (100, 1))
MS = {"idle": [1000], "run": [140] * 4, "attack": CHOP,
      "skill": IB.spans((133, 2), (100, 1), (167, 3)),
      "skill2": IB.spans((83, 1), (150, 2), (167, 3)),
      "ult": IB.spans((200, 2), (156, 1), (156, 1), (155, 1)), "hit": [100, 100],
      "dead": IB.spans((340, 4, (7, 8, 9, 10)), (900, 2, (8, 82))),
      "f_idle": [1000], "f_run": [130] * 3, "f_attack": CHOP,
      "f_skill": IB.spans((133, 1), (150, 2, (6, 9)), (117, 1)), "f_hit": [100, 100]}


def actions(C):
    f = C.frame

    def spin(name, part, degrees, how="under"):
        """The pose's part turned clockwise by `degrees` about its point (AT)."""
        return [(part, AT[(name, part)], degrees, how)]

    def under(**parts):
        return [(part, off, "under") for part, off in parts.items()]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run1_base: Skaarl's bird-like stride, the near leg then the far one)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack1: Kled rising with the axe up, chopping down in front of Skaarl, back): the axe swung further back,
    # up, Skaarl already down under him with the axe still coming over; chopped a step ahead, the axe bounced, at
    # rest; the idle
    out["attack"] = [f("a_wind", spins=spin("a_wind", "axe", -14)), f("a_wind"),
                     f("a_chop", dx=-1, spins=spin("a_chop", "axe", -40)),
                     f("a_chop", dx=2), f("a_chop", spins=spin("a_chop", "axe", -10)), f("a_chop"), f("idle")]
    # Bear Trap on a Rope (Spell1 -> Spell1_2: the trap thrown on its rope, the rope yanked in): the trap leaving his
    # hand, half way out; out; the rope yanked - the trap coming back in two steps
    out["skill"] = [f("q_throw", moves=under(rope=(-24, -1))), f("q_throw", moves=under(rope=(-11, 0))),
                    f("q_throw"),
                    f("q_yank"), f("q_yank", moves=under(rope=(-14, -1))), f("q_yank", moves=under(rope=(-28, -3)))]
    # Jousting (Spell3: Skaarl dashing, Kled's back-slash): the axe raised as Skaarl springs; levelled, held ahead in
    # the dash; the back-slash - the axe coming over his head in two steps, slashed back
    out["skill2"] = [f("e_lunge", spins=spin("e_lunge", "axe", -28)),
                     f("e_lunge", spins=spin("e_lunge", "axe", -10)), f("e_lunge"),
                     f("e_slash", spins=spin("e_slash", "axe", 60)), f("e_slash", spins=spin("e_slash", "axe", 25)),
                     f("e_slash")]
    # Chaaaaaaaarge!!! (Spell4: Skaarl sprinting flat out, Kled yelling with the axe ahead): the axe swung up and
    # brought down ahead as he yells; then the sprint
    out["ult"] = [f("r_charge", spins=spin("r_charge", "axe", -32)), f("r_charge", spins=spin("r_charge", "axe", -12)),
                  f("run2"), f("r_charge"), f("run4")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Rider_Death, mounted too: Kled hit and losing the axe, slumped on the ground): struck, knocked back with
    # the axe tumbling on away from him; dropping, slumped
    out["dead"] = [f("d_fall", flash=True),
                   f("d_fall", dx=-2, lift=2, spins=spin("d_fall", "axe", 40, "over"), moves=[("axe", (5, -4), "over")]),
                   f("d_fall", dx=-4, lift=3, spins=spin("d_fall", "axe", 85, "over"), moves=[("axe", (10, -6), "over")]),
                   f("d_fall", dx=-5, lift=1, spins=spin("d_fall", "axe", 135, "over"), moves=[("axe", (14, -3), "over")]),
                   f("d_down", lift=3), f("d_down")]
    # on foot (Skaarl fled)
    out["f_idle"] = [f("foot")]
    out["f_run"] = [f("f_run1"), f("f_run2"), f("f_run3")]
    # the axe swung further back, back, his body already in the chop with the axe still coming over; chopped a step
    # ahead, the axe bounced, at rest; the idle
    out["f_attack"] = [f("f_wind", spins=spin("f_wind", "axe", 14)), f("f_wind"),
                       f("f_chop", dx=-1, spins=spin("f_chop", "axe", -45)),
                       f("f_chop", dx=2), f("f_chop", spins=spin("f_chop", "axe", -10)), f("f_chop"), f("foot")]
    # Pocket Pistol (Rider_Spell1_1: the gun out and fired, the recoil blowing him back): aimed; fired with the gun
    # still level, kicked up as he is blown back; further back
    out["f_skill"] = [f("f_aim"), f("f_recoil", dx=1, spins=spin("f_recoil", "gun", 22)), f("f_recoil", dx=-1),
                      f("f_recoil", dx=-3)]
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
