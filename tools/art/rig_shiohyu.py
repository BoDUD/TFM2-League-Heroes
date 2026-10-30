#!/usr/bin/env python3
"""tft_shiohyu's action frames: Shi Oh Yu's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-30: sprites by Codex from written prompts).

    python tools/art/rig_shiohyu.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_shiohyu.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                     # (tft/champions/tft_shiohyu), then ppu_restyle.py / ppu_hd.py --hero shiohyu

The pictures (tools/art/design_shiohyu_model.py, design_shiohyu_poses.py):
  hd/idle.png         Shi Oh Yu standing upright, turned near side-on facing right, 74 x 103 at PPU 2.46 (42 game px,
                      the wing tips to his feet): the idle and the hit;
  hd/pose_<name>.png  Codex's poses at the design's body size and density with the design's face where the head is the
                      design's (assets/source/shiohyu/POSE_PROMPTS.md): a1_wind a1_hit a2_wind a2_hit a3_wind a3_hit
                      q_dash e_slam r_roar r_wave d_fall d_down, and TFT's run in 8 frames (run1-run8, one full cycle).
Placing a pose: the pack drew every reference with his root on one canvas column and his lowest point on the ground
line, and Codex drew each pose over its reference; so a pose's pivot (its json: that column) goes on the design's root
column (DESIGN_PIVOT) and its lowest row on the design's ground line. The run's eight frames are placed by the design's
face pasted on them (its json's face) where they have it - their root columns, read through Codex's drawings, wander a
few squares from frame to frame while the head should glide - and by the mean of their neighbours' where they do not.
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

HERO = "shiohyu"
PPU = 2.46
SRC = os.path.join(ROOT, "assets", "source", "shiohyu", "hd")
DESIGN_PIVOT = 46             # the design's root column (pack_shiohyu_poses' pelvis column 46.4)
POSES = ("a1_wind", "a1_hit", "a2_wind", "a2_hit", "a3_wind", "a3_hit", "q_dash", "e_slam", "r_roar", "r_wave",
         "d_fall", "d_down")
RUN = tuple(f"run{k}" for k in range(1, 9))
RUN_FACE_X = 17               # the run's face column, squares ahead of the design's root (their mean over the frames)
POSE_DX = {}                  # a pose's columns moved after its pivot is placed (none so far)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


FACE_C0 = 44                  # design_shiohyu_poses.FACE_COLS[0]: a face offset's column 0 in the design


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.run_x = self.run_columns()
        lefts, rights, tops = [0], [d.shape[1]], [0]
        for n in POSES + RUN:
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
        self.outline = D.outline

    def run_columns(self):
        """Each run frame's left column relative to the design's: its face on RUN_FACE_X (the face's column in the
        frame + FACE_C0 = the eye's place); a frame without the face: the mean of its neighbours' face-placed root
        offsets."""
        out, root_off = {}, {}
        for n in RUN:
            m = meta(n)
            if m["face"] is not None:
                out[n] = DESIGN_PIVOT + RUN_FACE_X - FACE_C0 - m["face"][0]
                root_off[n] = out[n] + m["pivot"][0] - DESIGN_PIVOT
        for k, n in enumerate(RUN):
            if n not in out:
                near = [root_off[RUN[(k + s) % len(RUN)]] for s in (-1, 1) if RUN[(k + s) % len(RUN)] in root_off]
                out[n] = DESIGN_PIVOT - meta(n)["pivot"][0] + round(np.mean(near))
        return out

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its root column (its json's pivot) on the design's (the
        run: run_columns), its lowest row on the ground."""
        if name in RUN:
            return self.run_x[name], self.d.shape[0] - p.shape[0]
        m = meta(name)
        return DESIGN_PIVOT - m["pivot"][0] + POSE_DX.get(name, 0), self.d.shape[0] - p.shape[0]

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


# ms per frame; the kit's ticks (tools/kit/build_shiohyu.py) match these (ms x 0.06 = ticks): each attack 500 ms =
# atk_dur 30, the claw lands on atk_st 12 (200 ms: the strike); the dash held while he rushes (q_dur), then the flurry
# (skill) held over the four punches; Earthshaker 600 ms = e_dur 36, the fist in the ground on e_st 14 (233 ms); Jade
# Form 667 ms = r_dur 40 (the roar from 167 ms); the third blow's wave (r_wave) 500 ms, the line out at 200 ms
RUN_MS = [120, 100, 100, 120, 120, 110, 110, 187]   # pack_shiohyu_poses.RUN_MS: 0 120 220 320 440 560 670 780 of 967
MS = {"idle": [1000], "run": RUN_MS, "attack": [200, 300], "attack2": [200, 300], "attack3": [200, 300],
      "dash": [1000], "skill": [80, 80, 80, 80], "skill2": [233, 367], "ult": [167, 500], "r_wave": [200, 300],
      "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f(n) for n in RUN]
    # the three claw swipes (TFT's attack1-3: wind up, strike)
    out["attack"] = [f("a1_wind"), f("a1_hit")]
    out["attack2"] = [f("a2_wind"), f("a2_hit")]
    out["attack3"] = [f("a3_wind"), f("a3_hit")]
    # Jade Fist Barrage: the low pounce while he rushes, then the flurry (the pounce's fists pumping: back a square,
    # out two)
    out["dash"] = [f("q_dash")]
    out["skill"] = [f("q_dash"), f("q_dash", dx=2), f("q_dash", dx=-1), f("q_dash", dx=2)]
    # Earthshaker (the claw raised, then down flat with the fist in the ground)
    out["skill2"] = [f("a2_wind"), f("e_slam")]
    # Jade Form (gathered, then the wings spread and the roar); the third blow's lunge sending the wave
    out["ult"] = [f("a3_wind"), f("r_roar")]
    out["r_wave"] = [f("a3_wind"), f("r_wave")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (knocked back, down on his knees)
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
