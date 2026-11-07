#!/usr/bin/env python3
"""tft_baronnashor's action frames: Baron Nashor's approved design and Codex's key poses after its own TFT clips (its
body) and T-Hex's (its legs) (the user, 2026-11-03: sprites by Codex from written prompts).

    python tools/art/rig_baronnashor.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_baronnashor.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                         # (tft/champions/tft_baronnashor), then ppu_restyle.py / ppu_hd.py
                                                         # --hero baronnashor

The pictures (tools/art/design_baronnashor_model.py, design_baronnashor_poses.py):
  hd/idle.png         the serpent on its six spider legs (L6), 3/4 facing right, 80 x 94 at PPU 2.04 (46 game px, the
                      crest tips to the leg tips): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/baronnashor/
                      POSE_PROMPTS.md): a_rear a_bite q_breath e_dive e_dig e_rise r_rear r_slam r_spit run1-8 d_fall
                      d_down.
Placing a pose: each pose stands by its pivot (its json: between its planted feet; the run's carried by its face) on
the design's (design_baronnashor_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground.
The run is Codex's redrawn eight frames (assets/source/baronnashor/codex_run, pack_baronnashor_run.py: the legs take
turns - crossing in run1 and run5, the far leg ahead in run2-4, the near one in run6-8 - over one 1.27 s cycle, each frame
its share of it, pack_baronnashor_run.MS), one upper body, the head within two rows of the idle's.
Beyond the slots' tags the kit plays two of its own (CasterAnimation, tools/kit/build_baronnashor.py's Burrow Strike):
`dig` while it travels under the ground (only its crest above it) and `rise` as it bursts out.
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
from design_baronnashor_poses import DESIGN_PIVOT  # noqa: E402
from pack_baronnashor_run import MS as RUN_MS  # noqa: E402

HERO = "baronnashor"
PPU = 2.04
SRC = os.path.join(ROOT, "assets", "source", "baronnashor", "hd")
RUNS = tuple(f"run{i}" for i in range(1, 9))
POSES = ("a_rear", "a_bite", "q_breath", "e_dive", "e_dig", "e_rise", "r_rear", "r_slam", "r_spit", "d_fall",
         "d_down") + RUNS
SHIFT = {}


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
        self.pivot = DESIGN_PIVOT
        self.poses = {n: load(f"pose_{n}.png") for n in POSES}
        lefts, rights, tops = [-6], [d.shape[1] + 6], [-6]
        for n, p in self.poses.items():
            x, y = self.offset(n, p)
            lefts.append(x - 2)
            rights.append(x + p.shape[1] + 2)
            tops.append(y)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot on the design's, its lowest row on the
        ground."""
        x = self.pivot - meta(name)["pivot"][0]
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas, moved dx columns; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = self.poses[name]
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_baronnashor.py, 1 tick = 16.7 ms) match these: the bite 667 ms =
# atk_dur 40, rearing back until it strikes at atk_st 24 (400 ms); Corrosive Breath 600 ms = q_dur 36, drawing back,
# then the breath at q_st 18 (300 ms); Burrow Strike 667 ms = e_dur 40, crouching until it dives at e_st 12 (200 ms),
# then `dig` (held while it travels: its crest shifting a column every 120 ms) and `rise` on arrival (e_rise 30 = 500
# ms); Void's Wrath 3600 ms = 216 ticks (r_st 30 + 10 x r_every 18 + 6): it rears up, slams at r_st (500 ms), then
# spits ten acid balls 300 ms apart, each a jolt forward and back. The run: its 1.27 s cycle in eight steps.
MS = {"idle": [1000], "run": list(RUN_MS),
      "attack": [400, 267], "skill": [300, 300], "skill2": [200, 467], "dig": [120, 120], "rise": [250, 250],
      "ult": [500, 400] + [150, 150] * 9, "hit": [100, 100], "dead": [100, 250, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUNS]
    out["attack"] = [f("a_rear"), f("a_bite")]                                # Corrosive Bite
    out["skill"] = [f("a_rear"), f("q_breath")]                               # Corrosive Breath
    out["skill2"] = [f("e_dive"), f("e_dig")]                                 # Burrow Strike: down it goes
    out["dig"] = [f("e_dig"), f("e_dig", dx=1)]                               # ... under the ground
    out["rise"] = [f("e_rise"), f("idle")]                                    # ... and out
    out["ult"] = [f("r_rear"), f("r_slam")] + [f("r_spit", dx=1), f("r_spit")] * 9   # Void's Wrath
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
