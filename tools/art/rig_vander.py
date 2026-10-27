#!/usr/bin/env python3
"""tft_vander's action frames: Vander's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-27: sprites by Codex from written prompts, then 「Codex交付了 你做到完美后喊我review」).

    python tools/art/rig_vander.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_vander.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_vander), then ppu_restyle.py / ppu_hd.py --hero vander

The pictures (tools/art/design_vander_model.py, design_vander_poses.py):
  hd/idle.png         Vander in his low fighting stance, the gauntlet low in front, the bandaged fist at his chin, 3/4
                      facing right, 81 x 80 at PPU 2.0 (40 game px, the hair to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head put in (assets/source/vander/POSE_PROMPTS.md): a_wind
                      a_punch a_back q_guard e_crouch e_upper r_air r_land r_slam d_fall d_down; and run1-8, his TFT
                      run redrawn (RUN_PROMPTS.md), upright, as tall as his model running (~125 rows to the design's 80).
Placing a pose (rig_loris's way): Codex drew every pose on the pack's 1254 canvas where its reference put it (the
references were placed by tools/art/pack_vander_poses.py: the design pose's pelvis on one column, the soles on y 1176,
the design itself at square (11, 18) of the 12 px grid), so each pose goes where Codex drew it: its grid_at
(design_vander_poses.py's json) less the design's square, on the design's place on the canvas. The pivot (the line he
stands on) is the middle of the design's wide stance (PIVOT).
The run (the user, 2026-10-27, on the Titan / Braum walk on the crouched design first put here: 「跑步姿势不像啊」):
Codex's eight frames of his TFT run (RUN_PROMPTS.md: upright, the legs taking turns), each on the ground, its pasted head
on one column (RUN_HEAD: the frames' middles on the pivot on average); RUN_DX steps two frames back where the boot on
the ground came forward of the frame before (run2, run6), so it only goes back while it stands.
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

HERO = "vander"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "vander", "hd")
DESIGN_AT = (11, 18)          # the design's top-left square on the pose pack's 12 px grid (pack_vander_poses: 0_design.png)
PIVOT = 40                    # the design's column between his boots (rows 72-79: 0-15 and 53-80)
POSES = ("a_wind", "a_punch", "a_back", "q_guard", "e_crouch", "e_upper", "r_air", "r_land", "r_slam", "d_fall", "d_down")


RUN = [f"run{k}" for k in range(1, 9)]
# the boot on the ground, its sole's middle from the head box (columns): run1-3 11.5 19 7.5, run4-8 22 19.5 24.5 15.5 10
RUN_DX = {"run2": -5, "run6": -5}
RUN_MS = 133                             # his TFT run: 1066 ms the cycle


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def grid_at(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["grid_at"]


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        # room on every side for the poses as Codex placed them
        self.run_head = self.run_head_column(d)
        lefts, rights, tops = [0], [d.shape[1]], [0]
        for n in RUN:
            p, at = load(f"pose_{n}.png"), self.head_at(n)
            left = self.run_head - at[0] + RUN_DX.get(n, 0)
            lefts.append(left)
            rights.append(left + p.shape[1])
            tops.append(d.shape[0] - p.shape[0])
        for n in POSES:
            x, y = grid_at(n)
            p = load(f"pose_{n}.png")
            lefts.append(round(x - DESIGN_AT[0]))
            rights.append(round(x - DESIGN_AT[0]) + p.shape[1])
            tops.append(round(y - DESIGN_AT[1]))
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    @staticmethod
    def head_at(name):
        with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
            return json.load(f)["head_at"]

    def run_head_column(self, d):
        """The design's column for the run's head boxes: the frames' middles on the pivot, on average."""
        mids = [load(f"pose_{n}.png").shape[1] / 2 - self.head_at(n)[0] for n in RUN]
        return round(PIVOT - sum(mids) / len(mids))

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas): where Codex drew it relative to the design; a run frame on the
        ground, its head on the run's column."""
        rig = self.rig
        if name == "idle":
            return self.d, (rig.ox + dx, rig.oy - lift)
        if name in RUN:
            d = load(f"pose_{name}.png")
            left = self.run_head - self.head_at(name)[0] + RUN_DX.get(name, 0)
            return d, (rig.ox + left + dx, rig.oy + self.d.shape[0] - d.shape[0] - lift)
        d = load(f"pose_{name}.png")
        x, y = grid_at(name)
        return d, (rig.ox + round(x - DESIGN_AT[0]) + dx, rig.oy + round(y - DESIGN_AT[1]) - lift)

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
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


# ms per frame; the kit's ticks (tools/kit/build_vander.py) match these (a frame's start in ticks = ms x 0.06):
# attack 433 ms = atk_dur 26, the punch lands on atk_st 12 (200 ms: inside the punch frame, from 150 ms); The Hound
# 500 ms = q_dur 30: the crouch, then the guard held; Iron Fist and Last Stand rush in with MoveToTarget, which takes
# as long as the way is, so their casts only hold the run-up (skill2: coiled; ult: coiled, then in the air) and the
# blow is its own tag, played by a CasterAnimation in the dash's end_effects on arrival with the hit: `upper` (the
# uppercut, e_up_t ticks) and `slam` (the landing with the gauntlet raised, the slam, r_slam_t ticks)
MS = {"idle": [1000], "run": [RUN_MS] * len(RUN), "attack": [150, 150, 133],
      "skill": [100, 400], "skill2": [433], "upper": [300], "ult": [100, 567], "slam": [67, 233],
      "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # the run: his TFT run, upright (RUN_PROMPTS.md)
    out["run"] = [f(n) for n in RUN]
    # attack (his TFT attack: reared back, the gauntlet driven down and forward on the lunge, back to the stance)
    out["attack"] = [f("a_wind"), f("a_punch"), f("a_back")]
    # The Hound of the Underground (dropped low, the guard up)
    out["skill"] = [f("e_crouch"), f("q_guard")]
    # Iron Fist (coiled for the rush; on arrival the uppercut)
    out["skill2"] = [f("e_crouch")]
    out["upper"] = [f("e_upper")]
    # Last Stand on the Bridge (coiled, the leap; on arrival the landing with the gauntlet raised and the slam)
    out["ult"] = [f("e_crouch"), f("r_air")]
    out["slam"] = [f("r_land"), f("r_slam")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (stumbling forward, face down)
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
