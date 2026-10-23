#!/usr/bin/env python3
"""league_singed's action frames: Singed's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-23: 「动作包交付了 你做到完美后喊我review」, then 「有问题的地方你直接修复」).

    python tools/art/rig_singed.py --parts DIR       # the design with its parts tinted (12x)
    python tools/art/rig_singed.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_singed.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_singed_model.py, design_singed_poses.py):
  hd/idle.png         Singed, 3/4 front facing right, 45 x 62 at PPU 1.39 (36 game px head top to soles): the idle, the
                      hit, the run;
  hd/pose_<name>.png  Codex's key poses read back with the design's head, the bodies brought to the design's size
                      (assets/source/singed/POSE_PROMPTS.md): a_wind a_smash e_grab e_heave e_throw w_wind w_throw
                      r_drink r_rage d_stagger d_down.
Placing a pose: across, the middle of its squares (the mean column) on the design's, moved dx squares (League's lunges);
up and down, its soles on the ground row (its lowest square) or `lift` rows over it.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The run is league_braum's / league_zac's walk for the heroes League shows from behind (League's Singed runs with his back
to the camera, the plate over him): the design's own legs under the hip band, one lifted per frame by losing its top rows
and stepped forward, the body floating a little, the plate arm and the flask arm swinging a square against the legs, the
tank bobbing with the body (no part turned or stretched).
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
from rig_wukong import CutDesign as _Cut, pad  # noqa: E402

HERO = "singed"
PPU = 1.39
SRC = os.path.join(R.ROOT, "assets", "source", "singed", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 24                     # the column between his feet: the standing point
LEG_BAND = 46                  # the legs: the rows under it (the torn cloth strips end there)
LEG_SPLIT = 23                 # the column between the near leg and the far leg
# the plate with the near hand behind it: rows -> the columns it covers (its spikes reach column 0 on the left; the
# shoulder pad starts at column 15, the near boot's outline at column 11 from row 46)
PLATE = {(9, 14): (7, 14), (15, 39): (0, 14), (40, 44): (0, 15), (45, 45): (0, 14), (46, 51): (0, 10), (52, 55): (2, 9)}
FAR_ARM = (28, 46, 31, 44)     # rows / columns of the far forearm, the hand and the flask


def rows_mask(d, table):
    m = np.zeros(d.shape[:2], bool)
    for (y0, y1), (x0, x1) in table.items():
        m[y0:y1 + 1, x0:x1 + 1] = True
    return m & (d[..., 3] > 0)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    legs = op & (yy > LEG_BAND)
    D.part("near_leg", legs & (xx <= LEG_SPLIT))
    D.part("far_leg", legs & (xx > LEG_SPLIT))
    r0, r1, c0, c1 = FAR_ARM
    D.part("far_arm", op & (yy >= r0) & (yy <= r1) & (xx >= c0) & (xx <= c1))
    D.part("near_arm", rows_mask(d, PLATE))
    D.part("body", D.rest())
    return D


TINT = {"far_arm": (255, 220, 0), "near_arm": (0, 255, 120), "near_leg": (255, 0, 255), "far_leg": (255, 120, 0)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


# ------------------------------------------------------------------------------------------------- lossless moves
def lifted(layer, lift):
    """A leg layer lifted `lift` rows by losing its top rows (the thigh turned toward us): league_braum's walk."""
    if not lift:
        return layer
    out = layer.copy()
    ys = np.nonzero(layer[..., 3].any(1))[0]
    out[:ys.min() + lift] = 0
    return np.roll(out, -lift, axis=0)


def close_cracks(can, outline, most=12, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across - the
    outline (gap-check; rig_warwick.close_cracks). The design's own armpit and leg gaps stay open."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


# ------------------------------------------------------------------------------------------------- the canvas
def middle(d):
    """The mean column of a picture's squares."""
    return float(np.nonzero(d[..., 3] > 0)[1].mean())


def head_at(name):
    """The head box's top-left square in hd/pose_<name>.png (design_singed_poses' json)."""
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


class Form:
    """The design's layers and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(60, 60, 60, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.mid = middle(D.d)

    def pose(self, whole=(0, 0), near_at=(0, 0), far_at=(0, 0), near_leg=(0, 0, 0), far_leg=(0, 0, 0)):
        """The design with its parts moved by whole squares: whole (dx, dy); an arm's (dx, dy); a leg's (dx, dy, lift)
        - lifted by losing its top rows (league_braum)."""
        wx, wy = whole
        L = self.L
        layers = [(lifted(L["far_leg"], far_leg[2]), dict(dx=wx + far_leg[0], dy=wy + far_leg[1])),
                  (L["body"], dict(dx=wx, dy=wy)),
                  (lifted(L["near_leg"], near_leg[2]), dict(dx=wx + near_leg[0], dy=wy + near_leg[1])),
                  (L["far_arm"], dict(dx=wx + far_at[0], dy=wy + far_at[1])),
                  (L["near_arm"], dict(dx=wx + near_at[0], dy=wy + near_at[1]))]
        can = R.compose(self.rig, layers)
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def left_of(self, name):
        """The canvas column of a pose's first column: its soles' middle on the design's (FEET), or the head of the pose
        it follows (HEAD_BACK)."""
        if name in HEAD_BACK:
            prev, back = HEAD_BACK[name]
            hx_prev = self.left_of(prev) + head_at(prev)[0]
            return hx_prev + back - head_at(name)[0]
        n0, n1 = FEET[name]
        return self.rig.ox + int(round((DESIGN_FEET[0] + DESIGN_FEET[1]) / 2 - (n0 + n1) / 2))

    def posed(self, name, dx=0, lift=0):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands (left_of), moved dx squares; its soles on
        the ground (SOLE_UP rows over its lowest row), `lift` rows above it in the air."""
        rig = self.rig
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        left = self.left_of(name) + dx
        top = rig.GY - (ys.max() + 1 - SOLE_UP.get(name, 0)) - lift
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_singed.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28: the plate raised, the smash landing at a_hit 11 (183 ms), back to the idle;
# E (skill, e_dur 30 = 500 ms): the grab at e_grab 10 (167 ms), heaved over the shoulder, thrown behind (e_fly 16 in the
# air from the grab);
# W (skill2, w_dur 30 = 500 ms): the flask raised, thrown at w_rel 12 (200 ms);
# R (ult, r_dur 40 = 667 ms): the potion raised, the rush;
# the walk (league_braum / league_zac): per frame the near leg's (dx, dy, lift), the far leg's, the figure's rise, the
# arms' swing (columns: the plate arm, the flask arm - against the legs)
MS = {"idle": [1000], "run": [100] * 8,
      "attack": [183, 167, 117],
      "skill": [167, 167, 166],
      "skill2": [200, 300],
      "ult": [333, 334],
      "hit": [100, 100],
      "dead": [150, 250, 1000]}
WALK = [((0, 0, 0), (0, 0, 2), 1, (0, 0)), ((0, 0, 0), (2, 0, 4), 2, (1, -1)),
        ((0, 0, 0), (2, 0, 2), 1, (1, -1)), ((0, 0, 0), (2, 0, 0), 0, (0, 0)),
        ((0, 0, 2), (0, 0, 0), 1, (0, 0)), ((2, 0, 4), (0, 0, 0), 2, (-1, 1)),
        ((2, 0, 2), (0, 0, 0), 1, (-1, 1)), ((2, 0, 0), (0, 0, 0), 0, (0, 0))]
# where each pose stands: the middle of its two soles (the near sole's left column, the far sole's right column on
# hd/pose_<name>.png, read at 7x) on the design's (10 and 41), so a stance widens or narrows round one point and no
# planted foot slides from frame to frame; up and down its soles on the ground - SOLE_UP rows over the picture's lowest
# row where something else reaches lower (a_smash: the plate's tip 9 rows under the soles, lying in front of him).
# d_down (sitting, the legs out to the right) keeps the stagger's head column moved HEAD_BACK squares back.
DESIGN_FEET = (10, 41)
FEET = {"a_wind": (24, 68), "a_smash": (1, 51), "e_grab": (5, 44), "e_heave": (19, 64), "e_throw": (37, 71),
        "w_wind": (16, 59), "w_throw": (12, 55), "r_drink": (11, 46), "r_rage": (9, 61), "d_stagger": (27, 64)}
SOLE_UP = {"a_smash": 9}
HEAD_BACK = {"d_down": ("d_stagger", -3)}
# and moved dx squares from there (League's lunges), `lift` rows off the ground
AT = {"a_wind": (0, 0), "a_smash": (0, 0), "e_grab": (0, 0), "e_heave": (0, 0), "e_throw": (0, 0),
      "w_wind": (0, 0), "w_throw": (0, 0), "r_drink": (0, 0), "r_rage": (0, 0), "d_stagger": (0, 0), "d_down": (0, 0)}


def actions(F):
    p, q = F.pose, F.posed

    def at(name, ddx=0, dlift=0):
        dx, lift = AT[name]
        return q(name, dx + ddx, lift + dlift)
    out = {}
    out["idle"] = [p()]
    # run (League's singed_run shows his back): league_braum's walk on the design's own legs
    out["run"] = [p(whole=(0, -r), near_leg=n, far_leg=f, near_at=(sw[0], 0), far_at=(sw[1], 0)) for n, f, r, sw in WALK]
    # auto attack (League's singed_attack1: the plate swung up, then smashed down in front)
    out["attack"] = [at("a_wind"), at("a_smash"), p()]
    # E Fling (singed_spell3: the grab, the heave over the shoulder, the follow-through)
    out["skill"] = [at("e_grab"), at("e_heave"), at("e_throw")]
    # W Mega Adhesive (singed_spell2: the flask raised, thrown)
    out["skill2"] = [at("w_wind"), at("w_throw")]
    # R Insanity Potion (singed_spell4: the potion raised, the rush)
    out["ult"] = [at("r_drink"), at("r_rage")]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's singed_death: staggering back, down on the ground)
    out["dead"] = [R.flash(at("d_stagger")), at("d_stagger"), at("d_down")]
    return out


def frames(F, tags=None):
    out = {}
    for tag, cans in actions(F).items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        out[tag] = list(zip(cans, ms))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(lp(a.parts), exist_ok=True)
        tinted(D).save(lp(os.path.join(a.parts, "singed_parts.png")))
        return
    F = Form(D)
    F.rig.idle_canvas = F.pose()
    acts = frames(F, a.tags.split(",") if a.tags else None)
    if a.review:
        F.rig.review(acts, a.review)
        return
    F.rig.export(acts)


if __name__ == "__main__":
    main()
