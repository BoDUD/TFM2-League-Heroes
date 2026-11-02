#!/usr/bin/env python3
"""tft_raptor's action frames: the Crimson Raptor's approved design and Codex's key poses after its own TFT clips (the
user, 2026-10-31: sprites by Codex from written prompts).

    python tools/art/rig_raptor.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_raptor.py                  # its frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_raptor), then ppu_restyle.py / ppu_hd.py --hero raptor

The pictures (tools/art/design_raptor_model.py, design_raptor_poses.py):
  hd/idle.png         the raptor crouched, 3/4 facing right, 75 x 56 at PPU 1.56 (36 game px, the crest to its talons):
                      the idle, the hit and the run;
  hd/pose_<name>.png  Codex's key poses at the design's body size with the design's face where its head is level
                      (assets/source/raptor/POSE_PROMPTS.md, design_raptor_poses.py): a_back a_jab q_rear q_spread e_hop
                      e_land r_rear r_call d_fall d_down.
Placing a pose: each pose stands by its pivot (its json: the point between its feet, carried by its face or its talons)
on the design's (design_raptor_poses.DESIGN_PIVOT), plus SHIFT[name] columns, its lowest row on the ground, LIFT[name]
rows up (the hop is in the air).
The run is the design's own idle walking (rig_galio.walk_frame's way, after league_nautilus / league_braum: the user's
rule for squat heroes, and every Codex run frame here was a body of its own - codex-walk-drafts-differ): the body, the
ruff, the head and the tail exactly the idle's; its two legs cut out under the feathers - the hind leg (HIND, image left)
and the fore leg (FORE, the talons under its chin) - and in each frame one leg is lifted by losing its top rows and set
forward, the legs taking turns (WALK), the whole bird rising a row or two as a foot pushes off. One full cycle of both
legs in RUN_MS x 8 (TFT's run is 1.2 s).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402
from design_raptor_poses import DESIGN_PIVOT  # noqa: E402

HERO = "raptor"
PPU = 1.56
SRC = os.path.join(ROOT, "assets", "source", "raptor", "hd")
POSES = ("a_back", "a_jab", "q_rear", "q_spread", "e_hop", "e_land", "r_rear", "r_call", "d_fall", "d_down")
SHIFT = {}
LIFT = {"e_hop": 6}            # the hop back: in the air
LIFT_MAX = 6
# the legs in hd/idle.png (rows, columns; ends exclusive): the hind leg under the rear feathers, the fore leg's talons
# under its chin (the chin's own squares above row 47 stay with the head)
HIND = (41, 56, 22, 41)
FORE = (47, 56, 48, 71)
# per frame: the hind leg's (columns forward, rows lifted), the fore leg's, the bird's rise
WALK = [((0, 3), (0, 0), 1), ((2, 4), (0, 0), 2), ((2, 2), (0, 0), 1), ((2, 0), (0, 0), 0),
        ((0, 0), (0, 3), 1), ((0, 0), (2, 4), 2), ((0, 0), (2, 2), 1), ((0, 0), (2, 0), 0)]
CRACK = 3                       # bare squares a step opens, this many columns wide at most: a crack
SPECK = 6                       # loose parts smaller than this are dropped


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def walk_frame(d, hind_step, fore_step, rise):
    """The idle with its legs stepping: each leg's squares moved (dx, -lift) after losing their top `lift` rows, the
    body over both, on the idle's rows (4 more columns for a leg set forward); Canvas.walk sets it `rise` rows up."""
    H, W = d.shape[:2]
    op = d[..., 3] > 0

    def part(box):
        r0, r1, c0, c1 = box
        m = np.zeros((H, W), bool)
        m[r0:r1, c0:c1] = True
        return m & op

    hind, fore = part(HIND), part(FORE)
    body = d.copy()
    body[hind | fore] = 0
    pad = 4
    out = np.zeros((H, W + pad, 4), np.uint8)
    for m, (dx, lift) in ((hind, hind_step), (fore, fore_step)):
        leg = np.where(m[..., None], d, 0).astype(np.uint8)
        top = np.nonzero(m.any(1))[0].min()
        leg[:top + lift] = 0
        ys, xs = np.nonzero(leg[..., 3] > 0)
        out[ys - lift, xs + dx] = leg[ys, xs]
    b = body[..., 3] > 0
    out[:, :W][b] = body[b]
    # the cracks a step opens (the slit under the feathers where a leg lost its top rows) take the outline: runs of at
    # most CRACK columns that the idle covered and the moved legs left bare - only in those top rows, never lower down a
    # leg's old place (the ground a lifted or stepped foot left: filled, its outline squares stood as specks)
    ground = np.zeros((H, W + pad), bool)
    for m, (dx, lift) in ((hind, hind_step), (fore, fore_step)):
        top = np.nonzero(m.any(1))[0].min()
        ground[:, :W] |= m
        ground[:top + max(lift, 1), :W] &= False
    opw = np.zeros((H, W + pad), bool)
    opw[:, :W] = op
    own = ndimage.binary_fill_holes(opw) & ~opw
    outline = PD.edge_colour(d)
    wop = out[..., 3] > 0
    crack = (opw & ~wop & ~ground) | (ndimage.binary_fill_holes(wop) & ~wop & ~own)
    for y in np.nonzero(crack.any(1))[0]:
        xs = np.nonzero(crack[y])[0]
        for run in np.split(xs, np.nonzero(np.diff(xs) > 1)[0] + 1):
            if len(run) <= CRACK:
                out[y, run] = (*outline[:3], 255)
    lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3), bool))   # loose specks
    sizes = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
    for j in range(1, n + 1):
        if sizes[j - 1] < SPECK:
            out[lab == j] = 0
    return out


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.pivot = DESIGN_PIVOT
        lefts, rights, tops = [0], [d.shape[1] + 4], [-LIFT_MAX]
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
        """A pose on the canvas (LIFT[name] rows up); flash = the hit's whitening."""
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
        can = self.place(p, x + dx, y - LIFT.get(name, 0), name)
        return R.flash(can) if flash else can

    def walk(self, k):
        hind, fore, rise = WALK[k]
        return self.place(walk_frame(self.d, hind, fore, rise), 0, -rise, f"run{k + 1}")


# ms per frame; the kit's ticks (tools/kit/build_raptor.py) match these (a frame's start in ticks = ms x 0.06): attack
# 400 ms = atk_dur 24, the feather on a_rel 8 (133 ms: the jab); Feather Fan 500 ms = q_dur 30, the fan on q_rel 12
# (200 ms: the wings spread); Startled Hop 300 ms = e_dur 18, the hop on e_rel 4 (67 ms, the hop frame showing);
# Flock Family 500 ms = r_dur 30, the call on r_rel 12 (200 ms). The run: one full cycle of both legs in 1.2 s (TFT's).
RUN_MS = 150
MS = {"idle": [1000], "run": [RUN_MS] * 8, "attack": [133, 267], "skill": [200, 300], "skill2": [167, 133],
      "ult": [200, 300], "hit": [100, 100], "dead": [100, 200, 700]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [C.walk(k) for k in range(8)]
    out["attack"] = [f("a_back"), f("a_jab")]                                # Feather Shot
    out["skill"] = [f("q_rear"), f("q_spread")]                              # Feather Fan
    out["skill2"] = [f("e_hop"), f("e_land")]                                # Startled Hop
    out["ult"] = [f("r_rear"), f("r_call")]                                  # Flock Family
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
