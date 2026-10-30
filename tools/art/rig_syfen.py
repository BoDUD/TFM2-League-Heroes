#!/usr/bin/env python3
"""tft_syfen's action frames: Sy'fen's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-30: sprites by Codex from written prompts).

    python tools/art/rig_syfen.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_syfen.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_syfen), then ppu_restyle.py / ppu_hd.py --hero syfen

The pictures (tools/art/design_syfen_model.py, design_syfen_poses.py):
  hd/idle.png         Sy'fen standing hunched, side-on facing right, 128 x 101 at PPU 2.52 (40 game px, the horn tips to
                      his feet): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size and density with the design's face where the head is
                      not turned (assets/source/syfen/POSE_PROMPTS.md, design_syfen_poses.py): a1_wind a1_hit a2_wind
                      a2_hit q_rear q_bite e_spread e_sweep r_roar r_charge r_bite d_fall d_down and the run on all fours
                      run1-8 (TFT's own: one full cycle, the hind legs passing in run2 and run6).
Placing a pose: the pack drew every reference with his root on one canvas column and his lowest point on the ground
line, and Codex drew each pose over its reference; so a pose's pivot (its json: that column) goes on the design's root
column (DESIGN_PIVOT) plus SHIFT[name] (columns, read off the review GIFs), and its lowest row on the design's ground.
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
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "syfen"
PPU = 2.52
SRC = os.path.join(ROOT, "assets", "source", "syfen", "hd")
DESIGN_PIVOT = 56             # the design's root column (pack_syfen_poses' pelvis column 56.0)
RUNS = tuple(f"run{k}" for k in range(1, 9))
POSES = ("a1_wind", "a1_hit", "a2_wind", "a2_hit", "q_rear", "q_bite", "e_spread", "e_sweep", "r_roar", "r_charge",
         "r_bite", "d_fall", "d_down") + RUNS
# extra columns per pose (+ = forward). The run: each frame's horns where its reference's head is against the idle's
# (pack_syfen_poses' heads, root-relative: run1-8 60.2 58.5 56.6 58.5 59.2 53.9 53.3 58.5 squares, the idle 41.8) -
# Codex drew run1, run2 and run6 further forward than their references (10-16 squares), which jumped in the loop
SHIFT = {"run1": -10, "run2": -16, "run3": -4, "run4": -2, "run5": -6, "run6": -10, "run7": -8, "run8": -3}


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
        lefts, rights, tops = [0], [d.shape[1]], [0]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its root column (its json's pivot) on the design's,
        its lowest row on the ground."""
        m = meta(name)
        return DESIGN_PIVOT - m["pivot"][0] + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_syfen.py) match these (a frame's start in ticks = ms x 0.06): attack
# 500 ms = atk_dur 30, the blow on atk_st 12 (200 ms: the strike); Bite 667 ms = q_dur 40, the lunge on q_st 14 (233 ms);
# Wing Sweep 600 ms = e_dur 36, the sweep on e_st 16 (267 ms); Rampage 900 ms = r_dur 54: the roar until r_go 14 (233 ms),
# the charge until r_bite_t 34 (567 ms), the bite. The run: TFT's 0.667 s cycle at its own spacing, a little slower.
MS = {"idle": [1000], "run": [60, 90, 90, 100, 100, 100, 100, 110], "attack": [200, 300], "attack2": [200, 300],
      "skill": [233, 434], "skill2": [267, 333], "ult": [233, 334, 333], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUNS]
    out["attack"] = [f("a1_wind"), f("a1_hit")]        # the wing claw
    out["attack2"] = [f("a2_wind"), f("a2_hit")]       # the tail lash
    out["skill"] = [f("q_rear"), f("q_bite")]          # Bite
    out["skill2"] = [f("e_spread"), f("e_sweep")]      # Wing Sweep
    out["ult"] = [f("r_roar"), f("r_charge"), f("r_bite")]   # Rampage: the roar, the charge, the bite
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
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
