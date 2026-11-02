#!/usr/bin/env python3
"""tft_elderdragon's action frames: the Elder Dragon's approved design and Codex's key poses after League's Elder Dragon
clips (the user, 2026-11-01: sprites by Codex from written prompts).

    python tools/art/rig_elderdragon.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_elderdragon.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                         # (tft/champions/tft_elderdragon), then ppu_restyle.py / ppu_hd.py --hero elderdragon

The pictures (tools/art/design_elderdragon_model.py, design_elderdragon_poses.py):
  hd/idle.png         the dragon low on all four legs, wings half raised, 3/4 facing right, 167 x 125 at PPU 2.84 (44
                      game px, the highest wing tip to its claws): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face (assets/source/elderdragon/
                      POSE_PROMPTS.md, design_elderdragon_poses.py): a_back a_bite q_rear q_breath e_rear e_slam r_jump
                      r_land, the flight run1-8 and d_fall d_down.
Placing a pose: on the ground, each pose stands by its pivot (its json: the point under its body, carried by its face)
on the design's (design_elderdragon_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground.
In the air (the flight - League's Elder Dragon has no run, it moves flying low - and the ult), a pose is placed by its
FACE on the design's face (the head holds still while the wings beat; Codex's eight frames each hold the body a little
differently), lifted FLY rows above the design's head plus the beat's own bob BOB[k]; with no face (none) by its pivot.
The flight: a shallow beat of five of Codex's eight frames (FLAP: wings top, half way down, level, half way up, top
again) at 150 ms a frame: run4 (the bottom of the stroke) hangs its wing tips 55 rows under the head-aligned ground and
run7 / run8 lift the wings back up a second time (the clip's double beat read as a judder), so the low flight leaves
them; the ult's flight, high in the sky, plays all eight.
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
from design_elderdragon_poses import DESIGN_PIVOT  # noqa: E402

HERO = "elderdragon"
PPU = 2.84
SRC = os.path.join(ROOT, "assets", "source", "elderdragon", "hd")
WALK = ("run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8")
FLAP = ("run1", "run2", "run3", "run6", "run5")   # the low flight's beat (the module docstring)
POSES = ("a_back", "a_bite", "q_rear", "q_breath", "e_rear", "e_slam", "r_jump", "r_land", "d_fall", "d_down") + WALK
SHIFT = {}
FLY = 16                       # rows the flight holds its head above the design's: low flight (5.6 game px; run1's
                               # dangling claws 13 rows under the head-aligned ground clear it)
BOB = (0, 2, 4, 2, 0)          # FLAP's rows up as the wings beat down
SKY_BOB = (0, 2, 4, 5, 4, 2, 0, -1)   # the ult's: all eight frames
SKY = (36, 80, 112, 128, 128, 108, 72, 30)   # the ult's flight: rows over FLY, up into the sky (46 game px at the
                                            # top) and down again
LIFT = {"r_jump": 20}          # rows above the ground: the take-off spring
TOP = 200                      # rows of headroom over the design for the ult's flight


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
        lefts, rights, tops, bottoms = [0], [d.shape[1]], [-TOP], [d.shape[0]]
        for n in POSES:
            p = load(f"pose_{n}.png")
            for air in ((False, True) if n in WALK else (False,)):
                x, y = self.offset(n, p, air)
                lefts.append(x)
                rights.append(x + p.shape[1])
                tops.append(y - LIFT.get(n, 0) - (FLY + max(SKY) + max(SKY_BOB) if air else 0))
                low = FLY + min(BOB) if n in FLAP else FLY + min(s + b for s, b in zip(SKY, SKY_BOB))
                bottoms.append(y + p.shape[0] - (low if air else 0))
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4),
               max(8, max(bottoms) - d.shape[0] + 4))

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p, air=False):
        """A pose's top-left square relative to the design's: in the air its face on the design's face; on the ground
        its pivot on the design's, its lowest row on the ground."""
        m = meta(name)
        if air and m["face"] is not None:
            return -m["face"][0] + SHIFT.get(name, 0), -m["face"][1]
        x = self.pivot - m["pivot"][0]
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, flash=False, air=False):
        """A pose on the canvas, lifted `lift` rows (and its own LIFT); flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p, air)
            lift += LIFT.get(name, 0)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_elderdragon.py) match these (a frame's start in ticks = ms x 0.06):
# attack 600 ms = atk_dur 36, the bite on atk_st 18 (300 ms: the jaws snap); Flame Breath 600 ms = q_dur 36, the fire on
# q_st 16 (267 ms: the jaws open wide); Wing Storm 600 ms = e_dur 36, the gust on e_st 16 (267 ms: the wings come down);
# Heat Without Equal 1833 ms = r_air 90 + q_st 16 + 4: the spring (250), up and down through the sky (8 x 150), the
# slam on r_air (1500 ms, inside r_land), the breath again on r_air + q_st (1767 ms: q_breath). The flight: a beat in
# 750 ms.
MS = {"idle": [1000], "run": [150] * 5, "attack": [300, 300], "skill": [267, 333], "skill2": [267, 333],
      "ult": [250] + [150] * 8 + [150, 117, 116], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n, lift=FLY + b, air=True) for n, b in zip(FLAP, BOB)]
    out["attack"] = [f("a_back"), f("a_bite")]                                # Dragonfire Bite
    out["skill"] = [f("q_rear"), f("q_breath")]                               # Flame Breath
    out["skill2"] = [f("e_rear"), f("e_slam")]                                # Wing Storm
    out["ult"] = ([f("r_jump")] + [f(n, lift=FLY + s + b, air=True) for n, s, b in zip(WALK, SKY, SKY_BOB)]
                  + [f("r_land"), f("q_rear"), f("q_breath")])               # Heat Without Equal
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
