#!/usr/bin/env python3
"""league_aurelionsol's action frames: Aurelion Sol's approved 3/4 designs and Codex's key poses after League's clips
(the user, 2026-10-24: 「codex都交付了 做到完美后喊我review」).

    python tools/art/rig_aurelionsol.py --parts DIR       # the designs with their parts tinted (12x)
    python tools/art/rig_aurelionsol.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_aurelionsol.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_aurelionsol_model.py, design_aurelionsol_poses.py):
  hd/idle.png         Aurelion Sol hovering, 3/4 front facing right, 56 x 77 at PPU 1.75 (44 game px crest to tail tip):
                      the idle and the hit;
  hd/run.png          his flight (step 1's B), 85 x 51 on the idle's scale: the move (League's Astral Flight - he flies
                      everywhere), the idle's head pasted on it (one face in all frames);
  hd/pose_<name>.png  Codex's key poses read back with the design's head, the bodies brought to the design's size
                      (assets/source/aurelionsol/POSE_PROMPTS.md): a_wind a_throw q_wind q_breath e_reach e_hold r_call
                      r_pull d_rear d_down.
He floats: every frame stands FLOAT rows above the ground line (Vel'Koz's way), except the dead one lying on it.
Placing a pose: across, its head box on the design's head box (one face that never jumps), moved dx squares (League's
lunges); up and down, its lowest square FLOAT rows over the ground, or `lift` rows more.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The move is his flight: the flying design whole, bobbing up and down a row or two, the nebula tail's far half waving a
row up and down - no part turned or stretched.
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

HERO = "aurelionsol"
PPU = 1.75
SRC = os.path.join(R.ROOT, "assets", "source", "aurelionsol", "hd")
FLOAT = 4                      # rows between his lowest square and the ground line (he hovers)


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU
        self.ground += FLOAT


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 22                     # the column under his body's middle (the tail's root): the standing point
HEAD_X, HEAD_Y = 3, 0          # the head box's top-left square on hd/idle.png (pack_aurelionsol_poses.HEAD)
RUN_HEAD = (45, 0)             # where the idle's head (design_aurelionsol_poses.POLY) lies best on hd/run.png
RUN_TAIL = 16                  # hd/run.png: the tail's far half, columns left of this, waves


def head_squares():
    """The idle's head squares (design_aurelionsol_poses.POLY) -> (rows, cols, colours)."""
    import design_aurelionsol_poses as DP
    d = load("idle.png")
    ys, xs = np.nonzero(DP.head_mask(d))
    return ys, xs, d[ys, xs]


def run_design():
    """hd/run.png with the idle's head pasted on its own (one face in all frames)."""
    r = load("run.png")
    ys, xs, c = head_squares()
    r[ys + RUN_HEAD[1], xs + RUN_HEAD[0]] = c
    return r


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    D.part("body", D.rest())
    return D


def close_cracks(can, outline, most=12, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across - the
    outline (gap-check; rig_belveth.close_cracks)."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


def head_at(name):
    """The head box's top-left square in hd/pose_<name>.png (design_aurelionsol_poses' json)."""
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


class Form:
    """The designs and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(72, 40, 40, 12)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.run = run_design()

    def pose(self, whole=(0, 0)):
        """The idle design moved by whole squares (dx, dy)."""
        can = R.compose(self.rig, [(self.L["body"], dict(dx=whole[0], dy=whole[1]))])
        can[self.rig.GY:] = 0
        return can

    def place(self, d, left, top):
        rig = self.rig
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can

    def flying(self, rise=0, wave=0):
        """The flight: hd/run.png (the idle's head on it) with its head box over the idle's, its lowest square FLOAT +
        rise rows over the ground; the tail's far half (columns left of RUN_TAIL) `wave` rows up."""
        rig = self.rig
        r = self.run.copy()
        if wave:
            tail = np.zeros_like(r)
            tail[:, :RUN_TAIL] = r[:, :RUN_TAIL]
            r[:, :RUN_TAIL] = 0
            tail = np.roll(tail, -wave, 0)
            m = tail[..., 3] > 0
            r[m & (r[..., 3] == 0)] = tail[m & (r[..., 3] == 0)]
        ys = np.nonzero((r[..., 3] > 0).any(1))[0]
        left = rig.ox + HEAD_X - RUN_HEAD[0]
        top = rig.GY - FLOAT - rise - (ys.max() + 1)
        return close_cracks(self.place(r, left, top), self.D.outline)

    def posed(self, name, dx=0, lift=None):
        """A Codex pose (hd/pose_<name>.png) with its head box on the design's, moved dx squares; its lowest square
        `lift` rows over the ground (FLOAT unless given)."""
        rig = self.rig
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        hx, hy = head_at(name)
        left = rig.ox + HEAD_X - hx + dx
        top = rig.GY - (ys.max() + 1) - (FLOAT if lift is None else lift)
        return self.place(d, left, top)


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_aurelionsol.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27: the claw raised, the star let go at a_rel 10 (167 ms), back to the idle;
# Q (skill, held by a CasterAnimation for q_t 90 ticks = 1500 ms): the breath in, then the breath (the jaw open), the
# body rising and settling a row while the beam pulses from q_rel 8 (133 ms);
# E (skill2, e_dur 30 = 500 ms): the claw reaching out, the claws cupped as the orb flies at e_rel 12 (200 ms);
# R (ult, r_dur 36 = 600 ms): the claw raised high, yanked down at r_rel 14 (233 ms) as the star starts to fall.
MS = {"idle": [1000], "run": [120] * 6,
      "attack": [167, 150, 133],
      "skill": [133] + [152] * 9,
      "skill2": [200, 300],
      "ult": [233, 367],
      "hit": [100, 100],
      "dead": [150, 250, 1000]}
# the flight: per frame the figure's rise and the tail's far half's wave (rows up)
FLIGHT = [(0, 0), (1, 1), (2, 1), (2, 0), (1, -1), (0, -1)]
# each pose moved dx squares from the design's head column (League's lunges), `lift` rows off the ground (None: FLOAT)
AT = {"a_wind": (0, None), "a_throw": (2, None), "q_wind": (0, None), "q_breath": (1, None), "e_reach": (1, None),
      "e_hold": (0, None), "r_call": (0, None), "r_pull": (2, None), "d_rear": (-2, 2), "d_down": (-4, 0)}


def actions(F):
    p, q = F.pose, F.posed

    def at(name, ddx=0, dlift=0):
        dx, lift = AT[name]
        return q(name, dx + ddx, (FLOAT if lift is None else lift) + dlift)
    out = {}
    out["idle"] = [p()]
    # the flight (League's run: he swims through the air)
    out["run"] = [F.flying(r, w) for r, w in FLIGHT]
    # auto attack (League's Attack1: reared up, the far claw drawn back, then flung forward)
    out["attack"] = [at("a_wind"), at("a_throw"), p()]
    # Q Breath of Light (Spell1: the breath in, then the jaw open on the target; the body rises and settles)
    out["skill"] = [at("q_wind")] + [at("q_breath", dlift=k % 2) for k in range(len(MS["skill"]) - 1)]
    # E Singularity (Spell3: the claw reaching out, the claws cupped round the black hole)
    out["skill2"] = [at("e_reach"), at("e_hold")]
    # R Falling Star (Spell4_Calamity: the claw raised to the sky, yanked down)
    out["ult"] = [at("r_call"), at("r_pull")]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's Death: rearing back, sunk to the ground)
    out["dead"] = [R.flash(at("d_rear")), at("d_rear"), at("d_down")]
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
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    D = design()
    F = Form(D)
    F.rig.idle_canvas = F.pose()
    acts = frames(F, a.tags.split(",") if a.tags else None)
    if a.review:
        F.rig.review(acts, a.review)
        return
    F.rig.export(acts)


if __name__ == "__main__":
    main()
