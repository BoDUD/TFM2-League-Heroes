#!/usr/bin/env python3
"""tft_sohm's action frames: Sohm's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-30: sprites by Codex from written prompts).

    python tools/art/rig_sohm.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_sohm.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                  # (tft/champions/tft_sohm), then ppu_restyle.py / ppu_hd.py --hero sohm

The pictures (tools/art/design_sohm_model.py, design_sohm_poses.py):
  hd/idle.png         Sohm floating coiled, side-on facing right, 58 x 72 at PPU 1.8 (40 game px, the antler tips to the
                      bottom of her coil): the idle (a slow float, one square up and down) and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's body size and density with the design's face or head
                      (assets/source/sohm/POSE_PROMPTS.md, design_sohm_poses.py): a_rear a_spit q_rise q_send e_gather
                      e_push r_coil r_rise r_swirl d_fall d_down and TFT's flat swim run1-4.
Placing a pose: the pack drew every reference with her neck root on the design's column and her lowest point on the
ground line, and Codex drew each pose over its reference; so a pose's pivot (its json: the design's middle column
PIVOT_COL) goes on the design's (DESIGN_PIVOT) plus SHIFT[name] (columns, read off the review GIFs), and its lowest
row on the design's ground plus LIFT[name] rows up (she floats: the swim at the coil's middle height, not on the ground).
The swim: Codex's four frames were drawn 115 to 152 squares long (the tail grew from frame to frame: played forward
and back she would stretch like a rubber band), so the move is ONE of them (SWIM_BASE, its face the design's) with
a wave running down her body from the mane to the tail fin (swim(): each column lifted by a sine travelling tailwards,
nothing at the neck growing to SWIM_AMP squares at the tail, SWIM_LEN squares to a wave, SWIM_FRAMES phases).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "sohm"
PPU = 1.8
SRC = os.path.join(ROOT, "assets", "source", "sohm", "hd")
DESIGN_PIVOT = 29             # the design's middle column (design_sohm_poses.PIVOT_COL)
POSES = ("a_rear", "a_spit", "q_rise", "q_send", "e_gather", "e_push", "r_coil", "r_rise", "r_swirl", "d_fall",
         "d_down", "run2")
SWIM_BASE = "run2"            # Codex's swim frame the move is made of (its face matched the design's best: 90%)
SWIM_FRAMES = 8
SWIM_AMP = 2.6                # squares up and down at the tail fin
SWIM_LEN = 54                 # squares to one wave
SWIM_NECK = 40                # squares behind the snout where the wave starts (the mane rides still)
# extra columns per pose (+ = forward)
SHIFT = {}
# poses mirrored: d_down was drawn (as TFT's death ends) with her head to the left, after d_fall's to the right - the
# head would jump across her body on the last frame
FLIP = ("d_down",)
# rows up off the ground (she floats): the swim at about her coil's middle
LIFT = {"run2": 12}


def lp(path):
    return R.lp(path)


def load(name):
    a = np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()
    return a[:, ::-1].copy() if name[5:-4] in FLIP else a


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def swim(p, k):
    """Phase k of SWIM_FRAMES of the swim: every column of `p` (facing right) lifted by a sine travelling from the neck
    to the tail, its height growing from nothing SWIM_NECK squares behind the snout to SWIM_AMP at the tail's end;
    the frame one square taller on each side of the wave."""
    H, W = p.shape[:2]
    pad = int(math.ceil(SWIM_AMP)) + 1
    out = np.zeros((H + 2 * pad, W, 4), np.uint8)
    xs = np.nonzero((p[..., 3] > 0).any(0))[0]
    head = xs.max()
    ph = 2 * math.pi * k / SWIM_FRAMES
    for x in range(W):
        t = head - x - SWIM_NECK
        a = 0.0 if t <= 0 else SWIM_AMP * min(1.0, t / (head - SWIM_NECK - xs.min()))
        dy = int(round(a * math.sin(2 * math.pi * t / SWIM_LEN - ph))) if t > 0 else 0
        out[pad + dy:pad + dy + H, x] = p[:, x]
    return out, pad


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        lefts, rights, tops = [0], [d.shape[1]], [-2]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y - 4)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot column (its json's) on the design's, its
        lowest row on the ground, LIFT rows up."""
        px = meta(name)["pivot"][0]
        if name in FLIP:
            px = p.shape[1] - 1 - px
        return (DESIGN_PIVOT - px + SHIFT.get(name, 0),
                self.d.shape[0] - p.shape[0] - LIFT.get(name, 0))

    def frame(self, name, dx=0, dy=0, flash=False, phase=None):
        """A pose on the canvas; flash = the hit's whitening; phase = the swim's."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
            if phase is not None:
                p, pad = swim(p, phase)
                y -= pad
        left, top = rig.ox + x + dx, rig.oy + y + dy
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_sohm.py) match these (a frame's start in ticks = ms x 0.06): Water Bolt
# 400 ms = atk_dur 24, the bolt on a_rel 10 (167 ms: the spit); Tideblossom 600 ms = q_dur 36, the wave on q_rel 18
# (300 ms: the S-thrust); Tidecaller's Guard 500 ms = e_dur 30, the shield on e_rel 14 (233 ms: the push); Tidal Bloom
# 800 ms = r_dur 48: the coil, the rise, the bloom on r_rel 24 (400 ms: the swirl at the top). The idle floats a square
# up and down; the swim's wave runs once round in 8 x 100 ms.
MS = {"idle": [700, 700], "run": [100] * SWIM_FRAMES, "attack": [167, 233], "skill": [300, 300],
      "skill2": [233, 267], "ult": [200, 200, 400], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle"), f("idle", dy=-1)]
    out["run"] = [f(SWIM_BASE, phase=k) for k in range(SWIM_FRAMES)]
    out["attack"] = [f("a_rear"), f("a_spit")]          # Water Bolt
    out["skill"] = [f("q_rise"), f("q_send")]           # Tideblossom
    out["skill2"] = [f("e_gather"), f("e_push")]        # Tidecaller's Guard
    out["ult"] = [f("r_coil"), f("r_rise"), f("r_swirl")]   # Tidal Bloom: the coil, the rise, the swirl (the bloom)
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
