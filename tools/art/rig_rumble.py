#!/usr/bin/env python3
"""league_rumble's action frames: Rumble's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-25: 「动作帧用 Codex 骨架姿势包」 - the skeletons set after League's own frames: 「用英雄联盟本地客户端的动作帧重做兰博的
姿势包」 - then 「codex的动作帧也交付了 你做到完美后喊我review」).

    python tools/art/rig_rumble.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_rumble.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_rumble_model.py, design_rumble_poses.py):
  hd/idle.png         Rumble in his mech, 3/4 front facing right, 92 x 62 at PPU 1.75 (36 game px mohawk to the red
                      feet): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/rumble/POSE_PROMPTS.md): a_wind a_smash q_aim q_spray e_aim e_recoil r_crouch
                      r_launch run1-4 d_drop d_down.
Placing a pose (rig_yorick's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as the pose pack's skeleton moves the head in that frame (HEAD_DX, rounded) and dx squares more by hand; its
lowest square on the ground row (the red feet; the ball smashed down or the toppled hull where those are lowest), or
`lift` rows over it. The idle is the design alone (no breathing: hero_reels cuts the idle snippets from these actions).
Flamespitter's fire is drawn into the skill frames by the bake (assets/source/native/rumble_bake.json: league_rumble_fx
q_flame from q_spray's first moment on, its nozzle on the cannon's muzzle: tools/art/import_rumble_fx.py).
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
import pack_rumble_poses as PK  # noqa: E402

HERO = "rumble"
PPU = 1.75
SRC = os.path.join(ROOT, "assets", "source", "rumble", "hd")
STAND = 46                     # the idle's standing column: under the hull's bottom middle, between the red feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far the head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(meta.get("ground", ys.max() + 1))


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(40, 130, 40, 12))      # room for the ball swung up, the cannon raised, the fire poured
        self.outline = D.outline
        # pinholes the read-back left where two outlines meet (gap-check): enclosed holes of at most 3 squares anywhere
        # in the frame that the standing frame does not have take the outline (the gaps between the ball, the arm and
        # the legs are bigger and stay)
        self.rig.fill_rows, self.rig.CRACK = (-40, D.H), 3
        self.rig.idle_canvas = self.frame("idle")

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX[name]
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_rumble.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the ball landing on the smash frame (a_hit 11 = 183 ms); Flamespitter 1500 ms = q_t 90,
# the cannon levelled, the fire from q_first 8 (133 ms) to the end; Electro-Harpoon 400 ms = e_dur 24, fired on e_rel 8
# (133 ms); The Equalizer 600 ms = r_dur 36, the rockets off on r_rel 14 (233 ms)
MS = {"idle": [1000], "run": [150] * 4, "attack": [183, 184, 100], "skill": [133, 1367], "skill2": [133, 267],
      "ult": [233, 367], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's run: a long stomping stride on each leg, the passing frames a square higher)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack2: the ball raised over his head, smashed down before him, back)
    out["attack"] = [f("a_wind"), f("a_smash"), f("idle")]
    # Flamespitter (Spell1: the cannon levelled, then held spraying while the fire pours: the bake)
    out["skill"] = [f("q_aim"), f("q_spray")]
    # Electro-Harpoon (Spell3: aimed, the kick of the shot)
    out["skill2"] = [f("e_aim"), f("e_recoil")]
    # The Equalizer (Spell4: crouched with the pods to the sky, the kick of the rockets going off)
    out["ult"] = [f("r_crouch"), f("r_launch")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: knocked back, toppled onto his back with the legs in the air)
    out["dead"] = [f("d_drop", flash=True), f("d_drop"), f("d_down"), f("d_down")]
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


def baked(C, acts):
    """The bake's effects laid into their tags (Flamespitter's fire), when the effect sheet is there."""
    path = os.path.join(ROOT, "assets", "source", "native", f"{HERO}_bake.json")
    sheet = os.path.join(ROOT, "league", "effects", "league_rumble_fx#sheet.png")
    if not (os.path.isfile(lp(path)) and os.path.isfile(lp(sheet))):
        return acts
    return C.rig.bake(acts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = baked(C, frames(C, a.tags.split(",") if a.tags else None))
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
