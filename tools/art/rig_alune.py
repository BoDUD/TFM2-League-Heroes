#!/usr/bin/env python3
"""tft_alune's action frames: Alune's approved design and Codex's key poses after her own TFT clips (the user,
2026-10-26: sprites by Codex from written prompts, then 「拉露恩交付了codex 做到完美后喊我review」).

    python tools/art/rig_alune.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_alune.py                  # her frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_alune), then ppu_restyle.py / ppu_hd.py --hero alune

The pictures (tools/art/design_alune_model.py, design_alune_poses.py):
  hd/idle.png         Alune riding her crescent glaive, 3/4 facing right, 60 x 90 at PPU 2.0 (46 game px, the horns to
                      the crescent's foot): the idle, the glide (the run), Moonlight's seat, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/alune/POSE_PROMPTS.md): a_wind a_throw a_catch q_raise q_call e_bless r_raise r_call
                      d_fall d_down (run1-4 are not used: Codex redrew the crescent differently in each, so the glide
                      shimmered; the glide is the design itself, floating).
Placing a pose (rig_zaahen's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far across as her skeleton's head moves in that pose (the pose pack's grey head boxes, their middles: HEAD_DX), its
lowest square on the ground row - the crescent's foot when she rides it, the robe's hem when she stands: in TFT she steps
down off the floating crescent to stand and fling the ring (her clips put the standing head ~a fifth of her height lower
than the seated one), and so here. The idle is the design alone (hero_reels cuts the idle snippets from these actions;
the user, 2026-10-22: no up-and-down in idles). The glide bobs a row or two like the other floating heroes' runs
(league_kassadin, league_velkoz, league_karthus).
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
import design_alune_poses as DP  # noqa: E402

HERO = "alune"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "alune", "hd")
STAND = 34                     # the idle's standing column: under her seat on the crescent (the skeleton's pelvis, 31-34)
HEAD = (DP.HEAD[2], DP.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far her skeleton's head moves across in each pose, in squares (the pose pack's grey head boxes' middles against
# the idle's, both skeletons on the idle's pelvis column; pack_alune_poses); the seated poses stay on the design's own;
# d_down: Codex laid her head to the LEFT, on from d_fall's fall backwards (the skeleton had it on the right), so her
# head a little further left than in d_fall
HEAD_DX = {"a_wind": 2, "a_throw": -1, "a_catch": 1, "q_raise": -2, "q_call": -4, "e_bless": 0, "r_raise": -2,
           "r_call": -6, "d_fall": -9, "d_down": -12}
GLIDE = [0, 1, 2, 1]           # the glide's rows off the ground, frame by frame (dense rows: 2 = one game pixel)
# Moonlight's seat: Codex's e_bless is the design re-drawn with a hand swept up, its crescent redrawn a little off the
# design's (the cast and the idle after it shimmered there); the rows over SEAT_ROW (the head, the raised arm, the one
# arm left across the chest) are e_bless's, the rows from it down (the seat, the robe, the whole crescent - its arc
# rises to row 34) the design's own. Both carry the design's head on the same squares (head_at (19, 0)).
SEAT_ROW = 34


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name):
    if name == "e_bless":
        return bless()
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(ys.max() + 1)


def bless():
    """Moonlight's seat: e_bless over SEAT_ROW, the design from it down (both on the design's head squares)."""
    e = load("pose_e_bless.png")
    with open(lp(os.path.join(SRC, "pose_e_bless.json")), encoding="utf-8") as f:
        hx, hy = json.load(f)["head_at"]
    d = load("idle.png")
    ox, oy = HEAD[0] - hx, HEAD[1] - hy                 # e_bless's (0, 0) in the design's squares
    left = min(0, ox)
    out = np.zeros((d.shape[0], max(d.shape[1], ox + e.shape[1]) - left, 4), np.uint8)
    out[SEAT_ROW:, -left:-left + d.shape[1]] = d[SEAT_ROW:]
    top = e[:max(0, SEAT_ROW - oy)]
    out[oy:oy + top.shape[0], ox - left:ox - left + top.shape[1]] = top
    return out, (HEAD[0] - left, HEAD[1]), d.shape[0]


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(48, 64, 24, 8))       # room for the ring flung out, the fall back and the body lying
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX.get(name, 0)
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


# ms per frame; the kit's ticks (tools/kit/build_alune.py) match these (a frame's start in ticks = ms x 0.06):
# attack 400 ms = atk_dur 24, the ring let fly on a_rel 9 (150 ms: the fling's frame); Moonfall 600 ms = q_dur 36, the
# shards called on q_rel 15 (250 ms: the fist raised); Moonlight 400 ms = e_dur 24, the blessing on e_rel 9 (150 ms);
# Moon Descends 667 ms = r_dur 40, the moon called on r_rel 25 (417 ms: the arm thrust at the sky)
MS = {"idle": [1000], "run": [125] * 4, "attack": [150, 150, 100], "skill": [250, 250, 100], "skill2": [300, 100],
      "ult": [217, 200, 250], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # the glide (TFT's run stands her on the crescent far above it - taller than the design: here she rides it, floating)
    out["run"] = [f("idle", lift=k) for k in GLIDE]
    # attack (TFT's attack: off the crescent, the glaive held flat like a disc, the spiral ring flung, caught back)
    out["attack"] = [f("a_wind"), f("a_throw"), f("a_catch")]
    # Moonfall (her spell: the ring raised at her side like a shield, the fist thrust up - the shards fall - the ring)
    out["skill"] = [f("q_raise"), f("q_call"), f("q_raise")]
    # Moonlight (her second idle's wave: still seated, a hand swept up over her allies, back)
    out["skill2"] = [f("e_bless"), f("idle")]
    # Moon Descends (her dance's two calls: the ring lifted over her head, held, then the arm at the sky - the moon falls)
    out["ult"] = [f("r_raise"), f("r_raise", lift=1), f("r_call")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (her death: thrown back off the crescent, the glaive breaking into rings; down)
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
