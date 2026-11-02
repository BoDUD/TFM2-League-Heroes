#!/usr/bin/env python3
"""tft_cinderling's action frames: the Cinderling's (绯红树怪) approved design and Codex's key poses after its own TFT
clips (the user, 2026-11-02: sprites by Codex from written prompts).

    python tools/art/rig_cinderling.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_cinderling.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                        # (tft/champions/tft_cinderling), then ppu_restyle.py / ppu_hd.py --hero cinderling

The pictures (tools/art/design_cinderling_model.py, design_cinderling_poses.py):
  hd/idle.png         the critter crouched on all fours, 3/4 facing right, 94 x 70 at PPU 2.33 (30 game px, the
                      tallest leaf to its claws): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's mask (assets/source/cinderling/
                      POSE_PROMPTS.md, design_cinderling_poses.py): a_fling q_bristle q_throw e_dig e_pop r_rear r_roar,
                      the hop run1-4 and d_flip d_down.
Placing a pose: each pose stands by its pivot (its json: the point under its body, carried by its mask) on the
design's (design_cinderling_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground; LIFT[name]
rows above it for the poses in the air (the hops, the fling, the leap out of the ground: their clips' own heights,
the raw drawings' soles 9-11 squares over the pack's ground line; Codex drew e_pop on the ground, lifted here). e_dig
is cut at the ground already (its lower half under it).
Its run: TFT has none; the four hops of its own attack clip (crouch, spring, top, landing), a small critter bounding.
Burrow (skill2): it digs in (e_dig), is under the ground (only its leaf tips show: e_dig sunk SINK rows) while it moves, bursts out (e_pop) and lands.
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
from design_cinderling_poses import DESIGN_PIVOT  # noqa: E402

HERO = "cinderling"
PPU = 2.33
SRC = os.path.join(ROOT, "assets", "source", "cinderling", "hd")
WALK = ("run1", "run2", "run3", "run4")
POSES = ("a_fling", "q_bristle", "q_throw", "e_dig", "e_pop", "r_rear", "r_roar", "d_flip", "d_down") + WALK
SHIFT = {}
LIFT = {"a_fling": 9, "run2": 6, "run3": 9, "e_pop": 12}   # rows above the ground: in the air
LIFT_MAX = 4
SINK = 20                       # rows the dig sinks further while it moves under the ground


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
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - LIFT.get(n, 0) - LIFT_MAX)
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

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas, lifted `lift` rows (and its own LIFT); flash = the hit's whitening; "under" = e_dig
        sunk SINK rows more, cut at the ground (only its leaf tips show while it moves under it)."""
        rig = self.rig
        can = rig.canvas()
        sink = 0
        if name == "under":
            name, sink = "e_dig", SINK
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
            lift += LIFT.get(name, 0)
        left, top = rig.ox + x + dx, rig.oy + y - lift + sink
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        if sink:   # under the ground: nothing below it
            keep = ty < rig.oy + self.d.shape[0]
            ys, xs, ty, tx = ys[keep], xs[keep], ty[keep], tx[keep]
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_cinderling.py) match these (a frame's start in ticks = ms x 0.06):
# attack 400 ms = atk_dur 24, the leaf thrown on a_rel 11 (167 ms: a_fling); Razor Leaves 400 ms = q_dur 24, the leaves
# on q_rel 13 (200 ms: q_throw); Burrow 800 ms = e_dur 48: dug in by e_dig 12 (200 ms), under the ground e_move 12
# (the sunk frame, 200 ms), out at 400 ms (e_pop); Wildfire Leafstorm 500 ms = r_dur 30, the fire on r_rel 13 (200 ms:
# r_roar). The hop run: one cycle in 480 ms.
MS = {"idle": [1000], "run": [120] * 4, "attack": [167, 233], "skill": [200, 200], "skill2": [200, 200, 200, 200],
      "ult": [200, 300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in WALK]
    out["attack"] = [f("run1"), f("a_fling")]                                 # Ember Leaf
    out["skill"] = [f("q_bristle"), f("q_throw")]                             # Razor Leaves
    out["skill2"] = [f("e_dig"), f("under"), f("e_pop"), f("run4")]          # Burrow
    out["ult"] = [f("r_rear"), f("r_roar")]                                   # Wildfire Leafstorm
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("d_flip", flash=True), f("d_flip"), f("d_down")]
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
