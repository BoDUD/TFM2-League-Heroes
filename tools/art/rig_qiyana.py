#!/usr/bin/env python3
"""league_qiyana's action frames: her approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-22: 「Codex 照骨架画姿势」, then 「请好好做吧 做到完美了喊我review」).

    python tools/art/rig_qiyana.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_qiyana.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (PPU 1.5, one palette; tools/art/design_qiyana_model.py and design_qiyana_poses.py):
  hd/idle.png         her, 3/4 front facing right, 52 x 60 (40 game px): the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head pasted on
                      (assets/source/qiyana/POSE_PROMPTS.md, the legs drawn again short in LEGS_PROMPTS.md): a_wind
                      a_strike q_wind q_sweep q_end e_dash e_hit r_leap r_slam run1-4 d_fall d_lie.
Placing a pose (league_udyr's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares (a lunge carries her forward), its soles on the ground row - the pose's json "ground" (the row its
soles rest on: the ring may dip lower, a slam's blade striking in front of her) or its lowest square - or `lift` rows
over it in the air. The idle is the design alone (no breathing: hero_reels cuts her idle snippets from these actions).
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

HERO = "qiyana"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "qiyana", "hd")
STAND = 34                     # the idle's standing column: under her belt's middle, between her feet
HEAD = (20, 0)                 # the design's head box top-left (column, row) in hd/idle.png (design_qiyana_poses.HEAD)


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
        self.rig = R.Rig(D, pad=(70, 70, 60, 12))      # room for the ring swung behind and before her, the leap
        self.outline = D.outline

    def frame(self, name, dx=0, lift=0, flash=False):
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name)
        left = rig.ox + HEAD[0] - hx + dx
        top = rig.GY - ground - lift
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_qiyana.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 420 ms = atk_dur 25, the blow on the strike frame (a_hit 10 = 167 ms; the strike from 140 ms); skill 400 ms =
# q_dur 24, the sweep from 150 ms (q_at 10 = 167 ms); skill2 333 ms = e_dur 20, the dash then the slash (the hit comes at
# the kit's landing); ult 667 ms = r_dur 40, the slam from 250 ms (r_at 16 = 267 ms, the shockwave)
MS = {"idle": [1000], "run": [130] * 4, "attack": [140, 110, 90, 80], "skill": [150, 110, 140],
      "skill_w": [150, 110, 140], "skill_r": [150, 110, 140], "skill_g": [150, 110, 140],
      "skill2": [110, 90, 133], "ult": [120, 130, 200, 217], "hit": [100, 100], "dead": [140, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run: contact, passing, contact on the other leg, passing; the ring slung across her back)
    out["run"] = [f("run1"), f("run2", lift=1), f("run3"), f("run4", lift=1)]
    # attack (League's Attack1: the ring swung back on one leg, springing forward to strike, held, back)
    out["attack"] = [f("a_wind", dx=-1), f("a_strike", dx=2, lift=3), f("a_strike", dx=2, lift=1), f("idle")]
    # Q Edge of Ixtal (League's Spell1: the ring dragged low behind her, swept round to the front, the follow-through)
    out["skill"] = [f("q_wind", dx=-1), f("q_sweep", dx=2), f("q_end", dx=2)]
    # the same cast once per element on her ring, each with its own sweep drawn in (qiyana_bake.json): river, rock, grass
    for x in ("skill_w", "skill_r", "skill_g"):
        out[x] = [c.copy() for c in out["skill"]]
    # E Audacity (League's Spell3 -> Spell3_Hit: the low dash with the ring trailing, the landing slash)
    out["skill2"] = [f("e_dash", dx=1, lift=2), f("e_dash", dx=3, lift=2), f("e_hit", dx=2)]
    # R Supreme Display of Talent (League's Spell4: up with the ring raised behind her, the slam forward, held)
    out["ult"] = [f("r_leap", lift=4), f("r_leap", lift=10), f("r_slam", dx=2), f("r_slam", dx=2)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: the stagger with the ring slipping from her hand, down to sit)
    out["dead"] = [f("d_fall", dx=-1, flash=True), f("d_fall", dx=-2), f("d_lie", dx=-2), f("d_lie", dx=-2)]
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
    ap.add_argument("--no-bake", action="store_true", help="leave the forward effects out (assets/source/native/qiyana_bake.json)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if not a.no_bake and os.path.isfile(lp(os.path.join(ROOT, "assets", "source", "native", "qiyana_bake.json"))):
        acts = C.rig.bake(acts)
    if a.review:
        C.rig.review(acts, a.review)
        return
    C.rig.export(acts)


if __name__ == "__main__":
    main()
