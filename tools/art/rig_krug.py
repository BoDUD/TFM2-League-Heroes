#!/usr/bin/env python3
"""tft_krug's action frames: the Ancient Krug's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-28: sprites by Codex from written prompts).

    python tools/art/rig_krug.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_krug.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                  # (tft/champions/tft_krug), then ppu_restyle.py / ppu_hd.py --hero krug

The pictures (tools/art/design_krug_model.py, design_krug_poses.py):
  hd/idle.png         the Krug hunched on all fours, 3/4 facing right, 86 x 76 at PPU 2.0 (38 game px, the top of the
                      boulder to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses at the design's density (assets/source/krug/POSE_PROMPTS.md): a_rear a_slam
                      a_back q_ball q_unfold q_ram e_shell r_crouch run1-4 d_sink d_crack d_down.
Placing a pose: Codex drew every pose over its reference, and the references all stood on one pelvis column and one
ground line; design_krug_poses brought every pose down about that one canvas point (its json's pivot). So a pose's
pivot goes on the design's (DESIGN_PIVOT: a_back, back on all fours, then lies on the design column for column) and a
pose that stands on the ground has its lowest row on the design's ground line (Codex's soles drifted 1136-1202);
AIR poses keep their pivot's height (run4 springs up off the ground).
The roll (Rock and Roll) is q_ball turned a quarter at a time (a boulder: np.rot90, no squares lost) on the ground,
rolling to the image right, then it unfolds and rams. The ult springs up as the ball (lifted), unseen, and crashes as
the attack's slam. tft.dll's Shattered Rebirth plays `shatter` (falling to rubble) and `reform` (pulled back together)
as Animation CCs on him (addons/tft/src/krug.rs SHATTER / REFORM).
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

HERO = "krug"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "krug", "hd")
DESIGN_PIVOT = 43             # the design's pivot column (a_back's pivot, 41 of its 82, lies on the design's middle)
AIR = {"run4"}                # poses off the ground: placed by their pivot's height, not dropped onto the ground
POSES = ("a_rear", "a_slam", "a_back", "q_ball", "q_unfold", "q_ram", "e_shell", "r_crouch", "run1", "run2", "run3",
         "run4", "d_sink", "d_crack", "d_down")
LIFT_MAX = 34                 # the ult's highest lift (canvas rows): room above the design


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def pivot(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["pivot"]


def turned(p, k):
    """A pose turned k quarters clockwise (the ball rolling to the image right)."""
    return np.rot90(p, -k).copy()


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        lefts, rights, tops = [0], [d.shape[1]], [-LIFT_MAX]
        for n in POSES:
            p = load(f"pose_{n}.png")
            x, y = self.offset(n, p)
            lefts.append(x)
            rights.append(x + p.shape[1])
            tops.append(y)
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], DESIGN_PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def offset(self, name, p):
        """A pose's top-left square relative to the design's: its pivot column on the design's, its lowest row on the
        ground (AIR: its pivot on the ground line)."""
        px, py = pivot(name)
        x = DESIGN_PIVOT - px
        y = self.d.shape[0] - py if name in AIR else self.d.shape[0] - p.shape[0]
        return x, y

    def frame(self, name, dx=0, lift=0, flash=False, turn=0):
        """A pose on the canvas; turn = quarter turns clockwise about its bottom middle; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            p, (x, y) = self.d, (0, 0)
        else:
            p = load(f"pose_{name}.png")
            x, y = self.offset(name, p)
            if turn:
                q = turned(p, turn)
                x += (p.shape[1] - q.shape[1]) // 2
                y += p.shape[0] - q.shape[0]
                p = q
        left, top = rig.ox + x + dx, rig.oy + y - lift
        ys, xs = np.nonzero(p[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = p[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_krug.py) match these (a frame's start in ticks = ms x 0.06): attack
# 533 ms = atk_dur 32, the fists land on atk_st 16 (267 ms: inside the slam frame, from 250 ms); Rock and Roll 500 ms =
# q_dur 30: three quarter turns of the boulder, the unfold, the ram; Stone Shell 400 ms = e_dur 24: the crouch, then
# down in the shell; Ancient Landslide 1000 ms = r_dur 60: the crouch, the spring as the boulder (unseen from r_go 15 =
# 250 ms), the crash on r_at 36 (600 ms) as the slam; the rebirth's shatter 750 ms = krug.rs p_t 45, reform 400 ms =
# krug.rs REFORM 24
MS = {"idle": [1000], "run": [150] * 4, "attack": [250, 150, 133], "skill": [100, 100, 100, 100, 100],
      "skill2": [100, 300], "ult": [150, 100, 350, 250, 150], "hit": [100, 100], "dead": [100, 200, 300, 600],
      "shatter": [80, 170, 500], "reform": [150, 150, 100]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (his TFT slam: rearing up on the hind legs, both fists down, back on all fours)
    out["attack"] = [f("a_rear"), f("a_slam"), f("a_back")]
    # Rock and Roll (curled into the boulder, rolling, bursting open into the ram)
    out["skill"] = [f("q_ball"), f("q_ball", turn=1), f("q_ball", turn=2), f("q_unfold"), f("q_ram")]
    # Stone Shell (crouching, pulled down under the boulder)
    out["skill2"] = [f("r_crouch"), f("e_shell")]
    # Ancient Landslide (crouch, spring up as the boulder, out of sight, crash down with both fists)
    out["ult"] = [f("r_crouch"), f("q_ball", lift=12), f("q_ball", lift=LIFT_MAX, turn=1), f("a_slam"), f("a_back")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (sinking, the boulder cracking apart, a heap of rubble)
    out["dead"] = [f("d_sink", flash=True), f("d_sink"), f("d_crack"), f("d_down")]
    # the Shattered Rebirth (tft.dll): falling to rubble, then pulled back together
    out["shatter"] = [f("d_sink", flash=True), f("d_crack"), f("d_down")]
    out["reform"] = [f("d_crack"), f("d_sink"), f("r_crouch")]
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
