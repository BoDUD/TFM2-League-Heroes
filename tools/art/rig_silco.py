#!/usr/bin/env python3
"""tft_silco's action frames: Silco's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-27: sprites by Codex from written prompts, then 「Codex交付了 你做到完美后喊我review」).

    python tools/art/rig_silco.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_silco.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                   # (tft/champions/tft_silco), then ppu_restyle.py / ppu_hd.py --hero silco

The pictures (tools/art/design_silco_model.py, design_silco_poses.py):
  hd/idle.png         Silco leaning on his cane, a Shimmer vial raised, 3/4 facing right, 44 x 80 at PPU 2.0 (40 game
                      px, the hair to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/silco/POSE_PROMPTS.md): a_wind a_throw a_back q_wind q_throw e_show e_toss r_raise
                      r_throw run1-4 d_fall d_down.
Placing a pose: Codex put each figure a little differently on its canvas (the walk's heads 1-6 squares apart from frame
to frame), so every pose stands on his BOOTS: the middle of the boots' squares in the lowest FEET_ROWS rows (the boot
browns; the cane, the outline and the trouser shadow not counted) goes on the idle's (STAND), the lowest square on the
ground row - the feet stay put through the throws and the walk sways over them as his clips do. The idle is the design alone (hero_reels cuts the idle snippets from these actions; the
user, 2026-10-22: no up-and-down in idles).
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
import design_silco_poses as DP  # noqa: E402

HERO = "silco"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "silco", "hd")
HEAD = (DP.HEAD[2], DP.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
FEET_ROWS = 6                              # the boots' rows counted from the lowest square up


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def boots_x(d):
    """The middle column of the boots: brown squares (red over blue by 15+, not near-black) in the lowest FEET_ROWS
    rows of the figure."""
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    low = d[max(0, ys.max() + 1 - FEET_ROWS):ys.max() + 1].astype(int)
    r, g, b = low[..., 0], low[..., 1], low[..., 2]
    brown = (low[..., 3] > 0) & (r - b >= 15) & (r >= g) & (r > 40)
    _, xs = np.nonzero(brown)
    return float(xs.mean())


STAND = None                                # the idle's boots_x, set by Canvas


def load_pose(name):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(ys.max() + 1)


class Canvas:
    def __init__(self):
        global STAND
        self.d = load("idle.png")
        d = self.d
        STAND = boots_x(d)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], int(round(STAND)), d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(56, 56, 24, 8))       # room for the cane swung out, the fling and the kneel
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0, feet=None):
        """(picture, its top-left on the canvas): its boots (or `feet`'s) on the idle's."""
        rig = self.rig
        d, ground = (self.d, self.d.shape[0]) if name == "idle" else load_pose(name)[::2]
        bx = boots_x(d if feet is None else load_pose(feet)[0])
        return d, (rig.ox + int(round(STAND - bx)) + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False, feet=None):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift, feet)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_silco.py) match these (a frame's start in ticks = ms x 0.06):
# attack 400 ms = atk_dur 24, the vial let fly on a_rel 10 (167 ms: the fling's frame); Canister 600 ms = q_dur 36, the
# canister thrown on q_rel 16 (267 ms: the arm flung up); Shimmer Shot 400 ms = e_dur 24, the dose on e_rel 10 (167 ms:
# the toss); Flood 667 ms = r_dur 40, the giant canister thrown on r_rel 24 (400 ms: the arm thrust up)
MS = {"idle": [1000], "run": [150] * 4, "attack": [167, 133, 100], "skill": [267, 233, 100], "skill2": [167, 133, 100],
      "ult": [200, 200, 267], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # the walk (his run clip: leaning on the cane, the vial still raised)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (his TFT knife throw, a Shimmer vial in its place: drawn back over the shoulder, flung, back)
    out["attack"] = [f("a_wind"), f("a_throw"), f("a_back")]
    # Canister (his spell: crouched with the canister at his side, the arm flung high - the canister flies)
    out["skill"] = [f("q_wind"), f("q_throw"), f("a_back")]
    # Shimmer Shot (the vial held up at his face, tossed back to an ally)
    out["skill2"] = [f("e_show"), f("e_toss"), f("a_back")]
    # Flood (the knee raised, the giant canister heaved up, held, thrown)
    out["ult"] = [f("r_raise"), f("r_raise", lift=1), f("r_throw")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (his death: doubled back, the cane flying, down on one knee)
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
