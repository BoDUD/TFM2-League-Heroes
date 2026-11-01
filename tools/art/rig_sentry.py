#!/usr/bin/env python3
"""tft_sentry's action frames: the Sentry's approved design and Codex's key poses laid out from its three parts (the
user, 2026-11-02: sprites by Codex from written prompts).

    python tools/art/rig_sentry.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_sentry.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_sentry), then ppu_restyle.py / ppu_hd.py --hero sentry

The pictures (tools/art/design_sentry_model.py, design_sentry_poses.py):
  hd/idle.png         two floating crystal shards and the azure core, a slight 3/4 facing right, 28 x 44 at PPU 1.29
                      (34 game px, the left tip to the bottom points): the idle, the glide and the hit;
  hd/pose_<name>.png  Codex's poses at the design's stone size, each with its json (`x`: its left column in design
                      squares, `lift`: rows above the design's ground): a_rise a_fire q_open q_beam1 q_beam2 e_split
                      e_close r_open r_blast d_split d_down.
It floats: every frame but the death's sits HOVER rows above the ground (the shadow stays on it). The idle bobs (BOB
rows, the design as it is). The glide is the design leaned GLIDE_LEAN forward (a row shear: whole squares, the outline
kept) and bobbing - not Codex's run1-4, whose shards came back a different size in each frame (42-45 rows tall: the
glide would wobble).
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
from design_sentry_model import CORE, CORE_BOX  # noqa: E402

HERO = "sentry"
PPU = 1.29
SRC = os.path.join(ROOT, "assets", "source", "sentry", "hd")
POSES = ("a_rise", "a_fire", "q_open", "q_beam1", "q_beam2", "e_split", "e_close", "r_open", "r_blast", "d_split",
         "d_down")
HOVER = 3                       # rows it floats over the ground (about 2.3 game px)
BOB = (0, 1, 2, 1)              # the idle's rows up, a frame each
GLIDE = (0, 1, 2, 1)            # the glide's
GLIDE_LEAN = 0.12               # columns forward per row up the glide's shear (~7 degrees)
DEAD = {"d_split", "d_down"}    # on their way down / on the ground: no hover
HOLE = (19, 29, 54, 255)        # the hole's dark inside round the core (hd/idle.png)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def lean(d, k):
    """The design sheared forward: each row k columns right per row above the lowest (whole columns, rounded); the
    core put back unsheared, carried with its middle row (its "+" stays upright)."""
    h, w = d.shape[:2]
    top = int(np.ceil(k * h)) + 1
    out = np.zeros((h, w + top, 4), np.uint8)
    for y in range(h):
        s = int(round(k * (h - 1 - y)))
        out[y, s:s + w] = d[y]
    x0, y0, x1, y1 = CORE_BOX
    box = d[y0:y1, x0:x1]
    r, g, b = (box[..., c].astype(int) for c in range(3))
    core = (box[..., 3] > 0) & (((b > 110) & (b - r > 40)) | ((r > 190) & (g > 220) & (b > 220)))
    ys, xs = np.nonzero(core)
    ys, xs = ys + y0, xs + x0
    out[ys, xs + np.round(k * (h - 1 - ys)).astype(int)] = HOLE        # the sheared core -> the hole's dark inside
    s = int(round(k * (h - 1 - CORE[1])))
    out[ys, xs + s] = d[ys, xs]
    return out


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.glide = lean(d, GLIDE_LEAN)
        lefts, rights, tops = [-2], [self.glide.shape[1] + 2], [-HOVER - max(BOB) - 4]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], CORE[0], d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: where its json puts it, its lowest row `lift` rows
        above the ground, plus the hover."""
        m = meta(name)
        up = m["lift"] + (0 if name in DEAD else HOVER)
        return m["x"], self.d.shape[0] - p.shape[0] - up

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

    def frame(self, name, up=0, dx=0, flash=False):
        """A pose on the canvas (`up` more rows for the bob); flash = the hit's whitening."""
        if name == "idle":
            p, (x, y) = self.d, (0, -HOVER)
        elif name == "glide":
            p, (x, y) = self.glide, (0, -HOVER)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        can = self.place(p, x + dx, y - up, name)
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_sentry.py) match these (a frame's start in ticks = ms x 0.06): the bolt
# 400 ms = atk_dur 24, the bolt on a_rel 8 (133 ms: a_fire showing); Azure Laser: skill 200 ms = q_anim 12 (q_open,
# q_beam1), the laser from q_rel 10, then skill_loop (q_beam1 / q_beam2 pulsing) for the channel; Rift Leap 300 ms =
# e_dur 18 (e_split, the blink back from e_rel 4, e_close); Prism Sweep 667 ms = r_dur 40, the sweep on r_rel 18
# (300 ms: r_blast showing). The idle bobs over 1.2 s, the glide over 0.48 s.
MS = {"idle": [300] * 4, "run": [120] * 4, "attack": [133, 267], "skill": [100, 100], "skill_loop": [100, 100],
      "skill2": [150, 150], "ult": [300, 367], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle", up=u) for u in BOB]
    out["run"] = [f("glide", up=u) for u in GLIDE]
    out["attack"] = [f("a_rise"), f("a_fire")]                               # Shard Bolt
    out["skill"] = [f("q_open"), f("q_beam1")]                               # Azure Laser
    out["skill_loop"] = [f("q_beam1"), f("q_beam2")]
    out["skill2"] = [f("e_split"), f("e_close")]                             # Rift Leap
    out["ult"] = [f("r_open"), f("r_blast")]                                 # Prism Sweep
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    out["dead"] = [f("d_split", flash=True), f("d_split"), f("d_down")]
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
