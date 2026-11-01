#!/usr/bin/env python3
"""tft_scuttlecrab's action frames: the Scuttle Crab's approved design and Codex's key poses after League's river-crab
clips (the user, 2026-11-01: sprites by Codex from written prompts).

    python tools/art/rig_scuttlecrab.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_scuttlecrab.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                         # (tft/champions/tft_scuttlecrab), then ppu_restyle.py / ppu_hd.py --hero scuttlecrab

The pictures (tools/art/design_scuttlecrab_model.py, design_scuttlecrab_poses.py):
  hd/idle.png         the river crab, 3/4 facing right, 120 x 80 at PPU 2.667 (30 game px, the antenna tops to the lowest
                      leg tips): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's stone face plate (assets/source/
                      scuttlecrab/POSE_PROMPTS.md): a_rise a_hop a_stomp q_raise q_call e_tuck e_shell e_pop r_up1-3 (the
                      first two cut at the ground: climbing out), the scuttle run1-8 (one full cycle) and d_down.
Placing a pose: each pose stands by its pivot (its json: the root between its legs, carried by its face) on the
design's (design_scuttlecrab_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground; LIFT[name] rows
up in the air (the dance's hop). The ult's burrow sinks the closed shell into the ground (SINK rows, what goes under the
ground line cut away) until only the top of its back shows in the earth mound (r_dig, drawn under it).
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
from design_scuttlecrab_poses import DESIGN_PIVOT  # noqa: E402

HERO = "scuttlecrab"
PPU = 80 / 30
SRC = os.path.join(ROOT, "assets", "source", "scuttlecrab", "hd")
WALK = ("run1", "run2", "run3", "run4", "run5", "run6", "run7", "run8")
POSES = ("a_rise", "a_hop", "a_stomp", "q_raise", "q_call", "e_tuck", "e_shell", "e_pop", "r_up1", "r_up2", "r_up3",
         "d_down") + WALK
SHIFT = {}
LIFT = {"a_hop": 8}                   # the dance's hop in design squares (30 game px tall: 3 game px)
SINK = (20, 40, 58, 66)               # the burrow: the closed shell (71 rows) sunk this many rows, 66 = only its back
LIFT_MAX = max(LIFT.values())


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
            tops.append(y - LIFT_MAX)
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
        """A pose on the canvas, lifted `lift` rows (negative: sunk, what goes under the ground cut away); flash = the
        hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        left, top = rig.ox + x + dx, rig.oy + y - lift - LIFT.get(name, 0)
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        if lift < 0:                                    # sunk into the ground: nothing under the ground line
            under = ty >= rig.oy + self.d.shape[0]
            ys, xs, ty, tx = ys[~under], xs[~under], ty[~under], tx[~under]
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_scuttlecrab.py) match these (a frame's start in ticks = ms x 0.06):
# the dance 500 ms = atk_dur 30, the stomp on atk_st 15 (250 ms); Speed Shrine 500 ms = q_dur 30, the shrine on q_st 12
# (200 ms: the antennae up); Shell Shield 600 ms = e_dur 36, the shield on e_st 8 (133 ms: shut); Can You Dig It? 2900 ms
# = r_t 150 + r_out 24: dug in by 500 ms, under the earth to 2500 ms (r_t: the burst at tick 149), out in 400 ms. The
# scuttle: League's 0.53 s cycle of all six legs, eight equal frames.
MS = {"idle": [1000], "run": [70] * 8, "attack": [125, 125, 250], "skill": [200, 300], "skill2": [133, 333, 134],
      "ult": [100, 150, 100, 100, 100, 1950, 100, 150, 150], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in WALK]
    out["attack"] = [f("a_rise"), f("a_hop"), f("a_stomp")]                   # Crab Dance
    out["skill"] = [f("q_raise"), f("q_call")]                                # Speed Shrine
    out["skill2"] = [f("e_tuck"), f("e_shell"), f("e_pop")]                   # Shell Shield
    out["ult"] = ([f("e_tuck"), f("e_shell")] + [f("e_shell", lift=-k) for k in SINK]   # Can You Dig It?
                  + [f("r_up1"), f("r_up2"), f("r_up3")])
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("e_tuck", flash=True), f("e_shell"), f("d_down")]
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
