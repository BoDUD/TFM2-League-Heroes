#!/usr/bin/env python3
"""tft_gromp's action frames: Gromp's approved design and Codex's key poses after its own TFT / Rift clips (the user,
2026-11-01: sprites by Codex from written prompts).

    python tools/art/rig_gromp.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_gromp.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_gromp), then ppu_restyle.py / ppu_hd.py --hero gromp

The pictures (tools/art/design_gromp_model.py, design_gromp_poses.py):
  hd/idle.png         the toad crouched, 3/4 facing right, 105 x 54 at PPU 1.69 (32 game px, the mushroom caps to its
                      feet): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size (levelled by the belly) with the design's face where
                      it matches (assets/source/gromp/POSE_PROMPTS.md): a_back a_spit q_puff q_belch e_back e_spit
                      r_rear r_belch run1-8 d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: its belly's middle carried to the root column) on the design's
(design_gromp_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground (LIFT[name] rows above it
for the hop in the air).
The run is Codex's own hop (run1-8, one 0.53 s hop of its TFT clip): unlike the wolf's, its eight frames keep one body
(the belly, the head and the mushrooms the same), so they are used as drawn, each by its belly, RUN_MS each.
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
from design_gromp_poses import DESIGN_PIVOT  # noqa: E402

HERO = "gromp"
PPU = 1.69
SRC = os.path.join(ROOT, "assets", "source", "gromp", "hd")
POSES = ("a_back", "a_spit", "q_puff", "q_belch", "e_back", "e_spit", "r_rear", "r_belch",
         *(f"run{k}" for k in range(1, 9)), "d_fall", "d_down")
SHIFT = {}
# rows a pose is lifted off the ground: the hop in the air (its clip lifts it ~20 design rows at 266-333 ms; Codex drew
# run6 with the front hands already down, so a lower arc that follows its drawings)
LIFT = {"run4": 6, "run5": 8, "run6": 3}


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
        lefts, rights, tops = [-2], [d.shape[1] + 2], [-2]
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
        """A pose's top-left square relative to the design's: its pivot on the design's, its lowest row on the
        ground."""
        x = self.pivot - meta(name)["pivot"][0]
        return x + SHIFT.get(name, 0), self.d.shape[0] - p.shape[0] - LIFT.get(name, 0)

    def place(self, p, x, y, name):
        rig = self.rig
        can = rig.canvas()
        left, top = rig.ox + x, rig.oy + y
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return can

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        can = self.place(p, x + dx, y, name)
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_gromp.py) match these (a frame's start in ticks = ms x 0.06): the spit
# 400 ms = atk_dur 24, the glob on a_rel 8 (133 ms: a_spit showing); Belchy Bubble 500 ms = q_dur 30, the bubble on
# q_rel 14 (233 ms: q_belch showing); Slime Swamp 400 ms = e_dur 24, the glob on e_rel 8 (133 ms: e_spit showing); Swamp
# Belch 600 ms = r_dur 36, the cone on r_rel 18 (300 ms: r_belch showing). The run: the hop's eight frames, 0.6 s.
RUN_MS = 75
MS = {"idle": [1000], "run": [RUN_MS] * 8, "attack": [133, 267], "skill": [233, 267], "skill2": [133, 267],
      "ult": [300, 300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(f"run{k}") for k in range(1, 9)]
    out["attack"] = [f("a_back"), f("a_spit")]                               # Toxic Spit
    out["skill"] = [f("q_puff"), f("q_belch")]                               # Belchy Bubble
    out["skill2"] = [f("e_back"), f("e_spit")]                               # Slime Swamp
    out["ult"] = [f("r_rear"), f("r_belch")]                                 # Swamp Belch
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
