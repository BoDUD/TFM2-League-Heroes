#!/usr/bin/env python3
"""league_trundle's action frames: Trundle's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-25: 「都交给 Codex」, then 「Codex已经全部交付了 你做到完美后喊我review」).

    python tools/art/rig_trundle.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_trundle.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_trundle_model.py, design_trundle_poses.py):
  hd/idle.png         Trundle, 3/4 front facing right, hunched, 104 x 85 at PPU 2.0 (42.5 game px mane to feet): the
                      idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/trundle/POSE_PROMPTS.md): a_wind a_smash q_rear q_chomp w_crouch w_roar e_swing
                      e_raise r_rise r_reach run1-4 d_fall d_down.
Placing a pose (rig_yorick's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as League's head moves in that frame (the pose pack's skeleton: HEAD_DX, rounded) and dx squares more by hand;
its soles on the ground row (its lowest square: the feet, or the ice club's head when it hangs lower), or `lift` rows
over it. The idle is the design alone (no breathing: hero_reels cuts the idle snippets from these actions).
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
import pack_trundle_poses as PK  # noqa: E402

HERO = "trundle"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "trundle", "hd")
STAND = 58                     # the idle's standing column: under his belt's gem buckle, between his feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far League's head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}
LIFT = {"w_roar": 12}          # rows off the ground: the leap (the pack's 6 squares of 9 px, PPU 2 rows a game px)


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
        self.rig = R.Rig(D, pad=(70, 70, 70, 14))      # room for the club swung overhead, out behind, flung away
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX[name]
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=None, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, LIFT.get(name, 0) if lift is None else lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_trundle.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the club landing on the smash frame (a_hit 11 = 183 ms); Chomp 467 ms = q_dur 28, the bite
# from 200 ms (q_hit 12); the Frozen Domain's hop (tag `w`) 233 ms = w_dur 14; Pillar of Ice 400 ms = e_dur 24, the club
# raised as the pillar rises on e_rel 10 (167 ms); Subjugate 500 ms = r_dur 30, the hand reaching out on r_rel 14 (233 ms)
MS = {"idle": [1000], "run": [150] * 4, "attack": [183, 200, 84], "skill": [200, 200, 67], "w": [100, 133],
      "skill2": [167, 233], "ult": [233, 267], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run: contact, passing, contact on the other leg, passing; the club trailing out behind him)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack1: the club swung up over his head, smashed down before him, back)
    out["attack"] = [f("a_wind"), f("a_smash"), f("idle")]
    # Chomp (Spell1 bite: rearing up, lunging in with the jaws, back)
    out["skill"] = [f("q_rear"), f("q_chomp"), f("idle")]
    # the Frozen Domain (Spell2 cast_hop, the passive's hop after a bite on a champion: crouched, leaping up roaring)
    out["w"] = [f("w_crouch"), f("w_roar")]
    # Pillar of Ice (Spell3 cast_wave: the club swung across, raised high)
    out["skill2"] = [f("e_swing"), f("e_raise")]
    # Subjugate (Spell4: rising out of the hunch, reaching out to drain)
    out["ult"] = [f("r_rise"), f("r_reach")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: knocked back, the club flung away; slumped on the ground)
    out["dead"] = [f("d_fall", flash=True), f("d_fall"), f("d_down"), f("d_down")]
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
