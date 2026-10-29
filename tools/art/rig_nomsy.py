#!/usr/bin/env python3
"""tft_nomsy's action frames: Nomsy's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-29: sprites by Codex from written prompts).

    python tools/art/rig_nomsy.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_nomsy.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_nomsy), then ppu_restyle.py / ppu_hd.py --hero nomsy

The pictures (tools/art/design_nomsy_model.py, design_nomsy_poses.py):
  hd/idle.png         Nomsy sitting on all fours, 3/4 facing right, 129 x 94 at PPU 2.6 (36 game px, the top of the far
                      wing to her feet): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's density (assets/source/nomsy/POSE_PROMPTS.md): a_rear a_spit
                      q_rise q_roar e_back e_breath r_up r_fly1 r_fly2 r_land run1-8 d_fall d_down.
Placing a pose: the pack drew every reference with her root on one canvas column and her lowest point on the ground
line, and Codex placed each pose by its body over its reference; so a pose's pivot (its json: that column) goes on the
design's root column (DESIGN_PIVOT) and its lowest row on the design's ground line. The poses in the air were drawn
standing on the line too (the pack's rule) and are lifted here: Fireballs!'s leap (q_roar) and the ult's take-off and
hover (r_up, r_fly1, r_fly2) - the hover flaps UP -> LEVEL -> DOWN -> LEVEL, bobbing a row.
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

HERO = "nomsy"
PPU = 2.6
SRC = os.path.join(ROOT, "assets", "source", "nomsy", "hd")
DESIGN_PIVOT = 61             # the design's root column (pack_nomsy_poses' pelvis column 61.3)
POSES = ("a_rear", "a_spit", "q_rise", "q_roar", "e_back", "e_breath", "r_up", "r_fly1", "r_fly2", "r_land", "run1",
         "run2", "run3", "run4", "run5", "run6", "run7", "run8", "d_fall", "d_down")
Q_LIFT = 14                   # the leap's height (design rows; 5 game px)
HOVER = 30                    # the hover's height (design rows; 11.5 game px over the ground)
LIFT_MAX = HOVER + 2


# the walk stands every frame by its pink belly's middle column: Codex's run frames slid 29 columns back and forth by
# their pivots (the belly at 118.8 - 142.6 against the idle's 128.3), a walk in place does not
BELLY_ALIGN = tuple(f"run{k}" for k in range(1, 9))


def lp(path):
    return R.lp(path)


def belly_x(p):
    """The middle column of the pink belly and face (the design's light pinks)."""
    c = p[..., :3].astype(int)
    pink = (p[..., 3] > 0) & (c[..., 0] > 200) & (c[..., 1] > 110) & (c[..., 2] > 130)
    return float(np.nonzero(pink)[1].mean())


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def pivot(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["pivot"]


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
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
        self.outline = D.outline

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot column on the design's (the walk: its belly's
        middle on the design's, BELLY_ALIGN), its lowest row on the ground."""
        if name in BELLY_ALIGN:
            return round(belly_x(self.d) - belly_x(p)), self.d.shape[0] - p.shape[0]
        px, _ = pivot(name)
        return DESIGN_PIVOT - px, self.d.shape[0] - p.shape[0]

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_nomsy.py) match these (a frame's start in ticks = ms x 0.06): attack
# 400 ms = atk_dur 24, the bolt leaves on a_rel 9 (150 ms: the spit frame); Fireballs! 600 ms = q_dur 36, thrown on
# q_rel 18 (300 ms: the leap); Dragon Breath 500 ms = e_dur 30, the flame on e_rel 12 (200 ms: the breath); Dragon
# Ascension 2900 ms = its 174 ticks: the take-off rising over r_rel 24 (400 ms), the hover through the rain (2300 ms,
# the flap's four frames 150 ms each), the landing 200 ms (r_land 12)
FLAP = ("r_up", "r_fly1", "r_fly2", "r_fly1")
HOVER_MS = [150] * 14 + [200]
MS = {"idle": [1000], "run": [75] * 8, "attack": [150, 250], "skill": [300, 300], "skill2": [200, 300],
      "ult": [133, 133, 134] + HOVER_MS + [200], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(f"run{k}") for k in range(1, 9)]
    # attack (rearing back, then the head thrust forward spitting the bolt)
    out["attack"] = [f("a_rear"), f("a_spit")]
    # Fireballs! (rising with a roar, the leap throwing the fireball)
    out["skill"] = [f("q_rise"), f("q_roar", lift=Q_LIFT)]
    # Dragon Breath (the breath drawn in, the head forward breathing fire)
    out["skill2"] = [f("e_back"), f("e_breath")]
    # Dragon Ascension (wings up off the ground, the hover flapping with a one-row bob, down on all fours)
    up = [f("r_up", lift=HOVER * k // 3) for k in (1, 2, 3)]
    hover = [f(FLAP[k % 4], lift=HOVER + (1 if k % 4 == 0 else 0) - (1 if k % 4 == 2 else 0))
             for k in range(len(HOVER_MS))]
    out["ult"] = up + hover + [f("r_land")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (knocked back, rolled over on her back)
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
