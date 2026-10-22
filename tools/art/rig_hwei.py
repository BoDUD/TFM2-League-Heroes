#!/usr/bin/env python3
"""league_hwei's action frames: his approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-22: 「动作帧让 Codex 照骨架画姿势」, then 「动作帧做到完美后再喊我review」).

    python tools/art/rig_hwei.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_hwei.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (PPU 1.5, one palette; tools/art/design_hwei_model.py and design_hwei_poses.py):
  hd/idle.png         him, 3/4 front facing right, 62 x 76 (40 game px hair to soles, the crescent above): the idle, the
                      hit, and the attack's cocked frame (the brush turned up in his hand, brush_hwei.normalize);
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head and brush put in
                      (assets/source/hwei/POSE_PROMPTS.md; the legs drawn again short in LEGS_PROMPTS.md): a_flick q_wind
                      q_throw qw_raise qw_point qe_raise qe_slam ew_high ee_swing r_open r_fling run1-4 d_stagger d_kneel.
                      Not used: a_wind (the brush across both hands), ew_low, ee_wind, r_hop (the brush in the near hand:
                      the brush would jump hands within an action).
Placing a pose (league_qiyana's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares (a lunge carries him forward), its soles on the ground row - the pose's json "ground" (the row its
soles rest on: the brush may dip lower in front of him) or its lowest square - or `lift` rows over it in the air. The
idle is the design alone (no breathing: hero_reels cuts his idle snippets from these actions).
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
import brush_hwei as BR  # noqa: E402
import design_hwei_poses as DP  # noqa: E402  the design's head to paste
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "hwei"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "hwei", "hd")
STAND = 28                     # the idle's standing column: under his middle, between his feet
HEAD = (17, 14)                # the design's head box top-left (column, row) in hd/idle.png (design_hwei_poses.HEAD)
DESIGN_BRUSH = dict(grip=(40.5, 54.5), tip=(60.0, 72.5), butt=None)   # the design's brush (read at 16x)
COCK = 150                     # the attack's cocked brush: turned up and forward in his hand (degrees, 0 = down)
# poses whose head Codex drew tipped (kept by design_hwei_poses: its own face, no earrings, the clutching hand at its
# chin like a moustache): the design's head pasted on upright here, after the legs redo's join
REHEAD = {"d_stagger"}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name, meta_too=False):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    hx, hy = meta["head_at"]
    if name in REHEAD:
        dd = load("idle.png")
        r0, r1, c0, c1 = DP.HEAD
        my, mx = np.nonzero(DP.head_mask(dd))
        d[my - r0 + hy, mx - c0 + hx] = dd[my, mx]
    out = d, (hx, hy), int(meta.get("ground", ys.max() + 1))
    return out + (meta,) if meta_too else out


def cocked(d):
    """The design with its brush turned up in his hand (the hand, the arm and everything else as drawn) -> (picture,
    head box top-left, ground row)."""
    fig, _, (ox, oy) = BR.normalize(d, dict(DESIGN_BRUSH, to_deg=COCK))
    ys = np.nonzero((fig[..., 3] > 0).any(1))[0]
    feet = d.shape[0] + oy                         # the design's soles moved with the crop
    return fig, (HEAD[0] + ox, HEAD[1] + oy), int(feet)


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.cock = cocked(d)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(70, 80, 60, 12))      # room for the brush swung behind and before him, the leaps
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas, its json or None)."""
        rig = self.rig
        meta = None
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        elif name == "cocked":
            d, (hx, hy), ground = self.cock
        else:
            d, (hx, hy), ground, meta = load_pose(name, meta_too=True)
        return d, (rig.ox + HEAD[0] - hx + dx, rig.GY - ground - lift), meta

    def frame(self, name, dx=0, lift=0, flash=False, brush=None):
        """A pose on the canvas; brush: (grip on the canvas, direction) of a brush lying on the ground, drawn behind him."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top), _ = self.placed(name, dx, lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        if brush is not None:
            layer, m = BR.render(can.shape[:2], brush[0], brush[1])
            m &= can[..., 3] == 0
            can[m] = layer[m]
        return R.flash(can) if flash else can

    def dropped(self, name, dx=0):
        """Where a pose's lying brush is on the canvas: (grip, direction)."""
        _, (left, top), meta = self.placed(name, dx)
        b = meta["brush"]
        return (b["grip"][0] + left, b["grip"][1] + top), b["deg"]


# ms per frame; the kit's ticks (tools/kit/build_hwei.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27, the ink flicked on the flick frame (a_rel 10 = 167 ms; the flick from 100 ms);
# Disaster's three and Torment's three 500 ms = q_dur / e_dur 30, the paint released on the swing (q_rel / e_rel 12 =
# 200 ms; the swing from 140 ms); ult 600 ms = r_dur 36, the canvas flung on the fling (r_rel 14 = 233 ms, from 220 ms)
MS = {"idle": [1000], "run": [140] * 4, "attack": [100, 120, 130, 100],
      "skill": [140, 160, 200], "skill_w": [140, 160, 200], "skill_e": [140, 160, 200],
      "skill2": [140, 160, 200], "skill2_q": [140, 160, 200], "skill2_e": [140, 160, 200],
      "ult": [120, 100, 180, 200], "hit": [100, 100], "dead": [140, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's RunSlow: contact, passing, contact on the other leg, passing; the brush trailing in his hand)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]     # each on its support foot: the passing frames stand taller
    # attack (League's Attack01: the brush cocked up in his hand, flicked forward - the ink - held, back)
    out["attack"] = [f("cocked", dx=-1), f("a_flick", dx=1), f("a_flick", dx=1), f("idle")]
    # Subject: Disaster - Devastating Fire (Spell1Q: the brush raised high, swung down and forward - the fireball)
    out["skill"] = [f("q_wind", dx=-1), f("q_throw", dx=2), f("q_throw", dx=2)]
    # Severing Bolt (Spell1W: up on his toes with the brush raised straight up, then the deep lunge pointing down)
    out["skill_w"] = [f("qw_raise", lift=2), f("qw_point", dx=2), f("qw_point", dx=2)]
    # Molten Fissure (Spell1E: a leap with the brush held point down, the crouch stabbing it into the ground)
    out["skill_e"] = [f("qe_raise", lift=4), f("qe_slam", dx=1), f("qe_slam", dx=1)]
    # Subject: Torment - Gaze of the Abyss (Spell3W: the brush raised high, held while the eye opens over the target)
    out["skill2"] = [f("ew_high", dx=-1), f("ew_high"), f("ew_high")]
    # Grim Visage (Spell3Q: the brush raised, then flicked forward - the visage flies)
    out["skill2_q"] = [f("q_wind", dx=-1), f("a_flick", dx=1), f("a_flick", dx=1)]
    # Crushing Maw (Spell3E: the brush raised, chopped down forward - the jaws snap)
    out["skill2_e"] = [f("ew_high", dx=-1), f("ee_swing", dx=2), f("ee_swing", dx=2)]
    # Spiraling Despair (Spell4: arms spread wide with the brush out, the canvas flung forward, held)
    out["ult"] = [f("r_open", dx=-1), f("r_open"), f("r_fling", dx=2), f("r_fling", dx=2)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: the stagger with the brush dropped, down on one knee); the brush lies where it lies in the
    # kneel in every frame (the stagger's own was cut by the legs redo)
    lying = C.dropped("d_kneel", dx=-2)
    out["dead"] = [f("d_stagger", dx=-1, flash=True, brush=lying), f("d_stagger", dx=-2, brush=lying),
                   f("d_kneel", dx=-2), f("d_kneel", dx=-2)]
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
