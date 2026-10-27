#!/usr/bin/env python3
"""tft_vander's action frames: Vander's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-27: sprites by Codex from written prompts, then 「Codex交付了 你做到完美后喊我review」).

    python tools/art/rig_vander.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_vander.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_vander), then ppu_restyle.py / ppu_hd.py --hero vander

The pictures (tools/art/design_vander_model.py, design_vander_poses.py):
  hd/idle.png         Vander in his low fighting stance, the gauntlet low in front, the bandaged fist at his chin, 3/4
                      facing right, 81 x 80 at PPU 2.0 (40 game px, the hair to the soles): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head put in (assets/source/vander/POSE_PROMPTS.md): a_wind
                      a_punch a_back q_guard e_crouch e_upper r_air r_land r_slam run1-4 d_fall d_down.
Placing a pose (rig_loris's way): Codex drew every pose on the pack's 1254 canvas where its reference put it (the
references were placed by tools/art/pack_vander_poses.py: the design pose's pelvis on one column, the soles on y 1176,
the design itself at square (11, 18) of the 12 px grid), so each pose goes where Codex drew it: its grid_at
(design_vander_poses.py's json) less the design's square, on the design's place on the canvas. The pivot (the line he
stands on) is the middle of the design's wide stance (PIVOT).
The run is the Titan / Braum walk on the design (rig_loris.walk_frame, the walk the user approved for heavy heroes:
「你按照泰坦布隆那种走路方式这种腿就不会变形」): Codex's run1-4 kept the front boot planted in all four frames while the
back one hopped (a slide, Loris's 「左脚看起来完全不动吧」), so the design as it is - body, head, gauntlet, fist - with its
own two legs under the hips (row WALK_BAND), the image-left one (WALK_FAR) and the image-right one (WALK_NEAR); in each
frame a leg is lifted by losing its top rows and moved forward, the legs take turns, the whole figure rises a little.
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
sys.path.insert(0, os.path.join(ROOT, ".claude", "skills", "tfm2-hero-mod", "scripts"))
import ppu_rig as R  # noqa: E402
import pixel_down as PD  # noqa: E402

HERO = "vander"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "vander", "hd")
DESIGN_AT = (11, 18)          # the design's top-left square on the pose pack's 12 px grid (pack_vander_poses: 0_design.png)
PIVOT = 40                    # the design's column between his boots (rows 72-79: 0-15 and 53-80)
POSES = ("a_wind", "a_punch", "a_back", "q_guard", "e_crouch", "e_upper", "r_air", "r_land", "r_slam", "d_fall", "d_down")


WALK_BAND = 55                           # the design's row over the legs (the crotch opens at row 55, under the gauntlet)
WALK_FAR = ((56, 80, 0, 38),)                       # the image-left (back) leg: design rows, columns (ends exclusive)
WALK_NEAR = ((56, 80, 48, 81),)                     # the image-right (front) leg, its boot to the design's right edge
# per frame: the near leg's (columns forward, rows lifted), the far leg's, the figure's rise (canvas squares:
# league_nautilus's 1x steps x PPU, rig_galio's at PPU 1.65)
WALK = [((0, 0), (0, 4), 2), ((0, 0), (2, 6), 4), ((0, 0), (2, 2), 2), ((0, 0), (2, 0), 0),
        ((0, 4), (0, 0), 2), ((2, 6), (0, 0), 4), ((2, 2), (0, 0), 2), ((2, 0), (0, 0), 0)]
WALK_MS = 115
CRACK = 3                                # bare squares a step opens, this many columns wide at most: a crack


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def grid_at(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["grid_at"]


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        # room on every side for the poses as Codex placed them
        lefts, rights, tops = [0], [d.shape[1]], [0]
        for n in POSES:
            x, y = grid_at(n)
            p = load(f"pose_{n}.png")
            lefts.append(round(x - DESIGN_AT[0]))
            rights.append(round(x - DESIGN_AT[0]) + p.shape[1])
            tops.append(round(y - DESIGN_AT[1]))
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4), 8)

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], PIVOT, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas): where Codex drew it relative to the design."""
        rig = self.rig
        if name == "idle":
            return self.d, (rig.ox + dx, rig.oy - lift)
        d = load(f"pose_{name}.png")
        x, y = grid_at(name)
        return d, (rig.ox + round(x - DESIGN_AT[0]) + dx, rig.oy + round(y - DESIGN_AT[1]) - lift)

    def frame(self, name, dx=0, lift=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
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


def walk_frame(C, near_step, far_step, rise):
    """The idle canvas with the legs stepping: each leg's squares moved (dx, -lift) after losing their top `lift` rows;
    the far leg first, the near one over it, the body over both; the whole frame `rise` rows up (rig_galio.walk_frame)."""
    idle = C.frame("idle")
    x0, y0 = C.rig.ox, C.rig.oy
    H, W = idle.shape[:2]
    op = idle[..., 3] > 0

    def mask(boxes):
        m = np.zeros((H, W), bool)
        for r0, r1, c0, c1 in boxes:
            m[y0 + r0:y0 + r1, x0 + c0:x0 + c1] = True
        return m & op
    far, near = mask(WALK_FAR), mask(WALK_NEAR)
    body = idle.copy()
    body[far | near] = 0
    out = np.zeros_like(idle)
    for m, (dx, lift) in ((far, far_step), (near, near_step)):
        leg = np.where(m[..., None], idle, 0).astype(np.uint8)
        ys, xs = np.nonzero(leg[..., 3] > 0)
        keep = ys > ys.min() - 1 + lift                 # the leg's top `lift` rows go (the thigh turned toward us)
        ys, xs = ys[keep], xs[keep]
        ok = (ys - lift >= 0) & (xs + dx < W)
        out[ys[ok] - lift, xs[ok] + dx] = leg[ys[ok], xs[ok]]
    m = body[..., 3] > 0
    out[m] = body[m]
    # cracks a step opens between a leg and the body: enclosed gaps at most CRACK columns wide take the outline
    opq = out[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(opq) & ~opq)
    for j in range(1, n + 1):
        hole = lab == j
        xs = np.nonzero(hole.any(0))[0]
        if xs.max() - xs.min() < CRACK:
            out[hole] = (*C.outline, 255)
    return np.roll(out, -rise, axis=0)


# ms per frame; the kit's ticks (tools/kit/build_vander.py) match these (a frame's start in ticks = ms x 0.06):
# attack 433 ms = atk_dur 26, the punch lands on atk_st 12 (200 ms: inside the punch frame, from 150 ms); The Hound
# 500 ms = q_dur 30: the crouch, then the guard held; Iron Fist and Last Stand rush in with MoveToTarget, which takes
# as long as the way is, so their casts only hold the run-up (skill2: coiled; ult: coiled, then in the air) and the
# blow is its own tag, played by a CasterAnimation in the dash's end_effects on arrival with the hit: `upper` (the
# uppercut, e_up_t ticks) and `slam` (the landing with the gauntlet raised, the slam, r_slam_t ticks)
MS = {"idle": [1000], "run": [WALK_MS] * len(WALK), "attack": [150, 150, 133],
      "skill": [100, 400], "skill2": [433], "upper": [300], "ult": [100, 567], "slam": [67, 233],
      "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # the run: the Titan / Braum walk on the design (Codex's run1-4 kept the front boot planted: a slide)
    out["run"] = [walk_frame(C, n_, f_, r_) for n_, f_, r_ in WALK]
    # attack (his TFT attack: reared back, the gauntlet driven down and forward on the lunge, back to the stance)
    out["attack"] = [f("a_wind"), f("a_punch"), f("a_back")]
    # The Hound of the Underground (dropped low, the guard up)
    out["skill"] = [f("e_crouch"), f("q_guard")]
    # Iron Fist (coiled for the rush; on arrival the uppercut)
    out["skill2"] = [f("e_crouch")]
    out["upper"] = [f("e_upper")]
    # Last Stand on the Bridge (coiled, the leap; on arrival the landing with the gauntlet raised and the slam)
    out["ult"] = [f("e_crouch"), f("r_air")]
    out["slam"] = [f("r_land"), f("r_slam")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (stumbling forward, face down)
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
