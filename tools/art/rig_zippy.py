#!/usr/bin/env python3
"""tft_zippy's action frames: Zippy's approved design and Codex's key poses after its own TFT clips (the user,
2026-10-31: sprites by Codex from written prompts).

    python tools/art/rig_zippy.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_zippy.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_zippy), then ppu_restyle.py / ppu_hd.py --hero zippy

The pictures (tools/art/design_zippy_model.py, design_zippy_poses.py):
  hd/idle.png         Zippy standing upright at 3/4 facing right, 52 x 83 at PPU 2.2 (37.7 game px, the head spikes to
                      its soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size and density with the design's face where the head is
                      not turned (assets/source/zippy/POSE_PROMPTS.md, design_zippy_poses.py): a_wind a_kick q_crouch
                      q_flip q_kick q_land e_curl e_ball r_crouch r_spring r_open r_land d_fall d_down and the run run1-8
                      (TFT's own sprint: one full 0.8 s cycle, the legs passing in run3 and run8).
Placing a pose: the pack drew every reference with its root on one canvas column and its lowest point on the ground
line, and Codex drew each pose over its reference; so a pose's pivot (its json: that column) goes on the design's root
column (DESIGN_PIVOT) plus SHIFT[name] (columns, read off the review GIFs), and its lowest row on the design's ground,
lifted `lift` rows for the poses in the air (Codex drew them standing on the line: the pack's rule). The feather ball
(e_ball) rolls by quarter turns (np.rot90, clockwise = rolling right), its middle kept where it stands.
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

HERO = "zippy"
PPU = 2.2
SRC = os.path.join(ROOT, "assets", "source", "zippy", "hd")
DESIGN_PIVOT = 20             # the design's root column (pack_zippy_poses' pelvis column 20.5)
RUNS = tuple(f"run{k}" for k in range(1, 9))
POSES = ("a_wind", "a_kick", "q_crouch", "q_flip", "q_kick", "q_land", "e_curl", "e_ball", "r_crouch", "r_spring",
         "r_open", "r_land", "d_fall", "d_down") + RUNS
# extra columns per pose (+ = forward). The run: each frame's face (its json: where the design's face went) put on the
# frames' mean - Codex drew the heads 18 columns apart over the cycle (run1 10 ahead of the mean, run8 8 behind), which
# jumped back and forth in the loop
SHIFT = {"run1": -10, "run2": -4, "run3": 0, "run4": 4, "run5": 0, "run6": 2, "run7": 0, "run8": 8}
# heights in the air (design rows; 2.2 a game px): the backflip, the spring, the ball's arc, the burst
Q_FLIP, Q_KICK = 14, 16
R_SPRING, R_BALL, R_OPEN = 10, (22, 30, 30, 22), 12
LIFT_MAX = 32


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def turned(p, quarters):
    """The ball turned `quarters` quarter turns clockwise (rolling right), padded square so its middle stays put."""
    n = max(p.shape[:2])
    sq = np.zeros((n, n, 4), np.uint8)
    y0, x0 = (n - p.shape[0]) // 2, (n - p.shape[1]) // 2
    sq[y0:y0 + p.shape[0], x0:x0 + p.shape[1]] = p
    return np.rot90(sq, -quarters).copy()


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
            if n == "e_ball":
                p = turned(p, 0)
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - LIFT_MAX)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its root column (its json's pivot) on the design's,
        its lowest row on the ground (the ball: its middle over the root)."""
        if name == "e_ball":
            return DESIGN_PIVOT - p.shape[1] // 2 + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]
        m = meta(name)
        return DESIGN_PIVOT - m["pivot"][0] + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, roll=None, flash=False):
        """A pose on the canvas, lifted `lift` rows (the ball turned `roll` quarters); flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            if roll is not None:
                p = turned(p, roll)
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_zippy.py) match these (a frame's start in ticks = ms x 0.06): attack
# 500 ms = atk_dur 30, the kick on atk_st 12 (200 ms); Backflip Kick 667 ms = q_dur 40, the kick on q_st 16 (267 ms: the
# feet up); Rolling Charge 500 ms = e_dur 30, the roll from e_st 8 (133 ms: the ball turning a quarter every 92 ms);
# Somersault Assault 833 ms = r_dur 50: the crouch and the spring until r_go 12 (200 ms), the ball spinning through the
# leap (tft.dll lands it within r_t 20 ticks: 333 ms), the burst, the crash. The run: TFT's 0.8 s cycle at its own
# spacing (pack_zippy_poses.RUN_MS 0 120 260 360 480 560 660 740).
MS = {"idle": [1000], "run": [120, 140, 100, 120, 80, 100, 80, 60], "attack": [200, 300],
      "skill": [133, 134, 200, 200], "skill2": [133, 92, 92, 92, 91], "ult": [100, 100, 75, 75, 75, 75, 133, 200],
      "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUNS]
    out["attack"] = [f("a_wind"), f("a_kick")]                                     # Claw Kick
    out["skill"] = [f("q_crouch"), f("q_flip", lift=Q_FLIP), f("q_kick", lift=Q_KICK), f("q_land")]   # Backflip Kick
    out["skill2"] = [f("e_curl")] + [f("e_ball", roll=k) for k in range(4)]       # Rolling Charge
    out["ult"] = ([f("r_crouch"), f("r_spring", lift=R_SPRING)]                    # Somersault Assault
                  + [f("e_ball", lift=h, roll=k) for k, h in enumerate(R_BALL)]
                  + [f("r_open", lift=R_OPEN), f("r_land")])
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
