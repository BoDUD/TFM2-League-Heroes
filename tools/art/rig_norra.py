#!/usr/bin/env python3
"""tft_norra's action frames: Norra's approved 3/4 design and Codex's key poses after the videos (the user, 2026-10-26:
actions and effects by Codex, 「按视频做骨架包和特效包」, then 「动作帧和特效codex都交付了 你做到完美后喊我review」).

    python tools/art/rig_norra.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_norra.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_norra_model.py, design_norra_poses.py):
  hd/idle.png         Norra, 3/4 front facing right, 46 x 72 at PPU 2.0 (36 game px hat to soles), the gold ring in her
                      near hand: the idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/norra/POSE_PROMPTS.md): a_wind a_point q_swirl q_throw e_open r_raise r_cast run1-4
                      d_fall d_down.
Placing a pose (rig_locke's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as the pose pack's skeleton moves the head (HEAD_DX, rounded) and dx squares more by hand; its soles on the ground
row (its lowest square), or `lift` rows over it (r_raise floats). The idle is the design alone (no breathing:
hero_reels cuts the idle snippets from these actions).
The moves follow the videos (assets/source/norra/POSE_PROMPTS.md): TFT's attack points a finger at the target (the bolt
flies from it), TFT's cast gathers a purple swirl, then flings the ball; the ring raised for the portals of E (TFT's
gold flash that summons Yuumi); Wild Rift's ult raises both arms under the gold rings, then pushes down; Wild Rift's
little-step walk.
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
import pack_norra_poses as PK  # noqa: E402

HERO = "norra"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "norra", "hd")
STAND = 27                     # the idle's standing column: under the red sash, between her feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far the pose pack's skeleton moves the head across in each pose (against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}
LIFT = {"r_raise": 3}          # rows off the ground: floating under the gate


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
        self.rig = R.Rig(D, pad=(40, 40, 20, 10))      # room for the ears flying back, the ring thrown off, the float
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


# ms per frame; the kit's ticks (tools/kit/build_norra.py) match these (a frame's start in ticks = ms x 0.06):
# attack 400 ms = atk_dur 24, the bolt off her finger at the point's start (133 ms: a_rel 9 -> tick 8); Portalpalooza
# 600 ms = q_dur 36, the ball flung at the throw's start (233 ms: q_rel 15 -> tick 14); Otherworld Delivery 433 ms =
# e_dur 26, the portals at the ring raised (133 ms: e_rel 9); the Book of Thresholds 667 ms = r_dur 40, the gate sent
# as she pushes down (400 ms: r_rel 25)
MS = {"idle": [1000], "run": [125] * 4, "attack": [133, 200, 67], "skill": [233, 267, 100], "skill2": [133, 200, 100],
      "ult": [400, 267], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (Wild Rift's walk: little steps, the robe and the ears swinging back; contact, passing, contact, passing)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (TFT's: the hand drawn in, the finger pointed at the target - the bolt flies - back)
    out["attack"] = [f("a_wind"), f("a_point"), f("idle")]
    # Portalpalooza (TFT's cast: gathered in the purple swirl, the ball flung, back)
    out["skill"] = [f("q_swirl"), f("q_throw"), f("idle")]
    # Otherworld Delivery (the ring raised: TFT's gold flash), held, back
    out["skill2"] = [f("idle"), f("e_open"), f("idle")]
    # the Book of Thresholds (Wild Rift's ult: rising, both arms up under the gate; pushing the page down)
    out["ult"] = [f("r_raise"), f("r_cast")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (knocked back, the ring flying; sat down)
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
