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
import inbetween as IB  # noqa: E402
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

    def posed(self, name, dx=0, lift=0, moves=(), spins=(), turns=()):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands (left_of), moved dx squares; its soles on
        the ground (SOLE_UP rows over its lowest row), `lift` rows above it in the air.
        The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole: moves [(part, (dx, dy), how)] -
        parts of the pose (PARTS) moved by whole squares, "under" the rest of him or "over" it; spins [(part, point,
        degrees, how)] - a part turned clockwise by any angle about a point, then moved if `moves` names it too; turns
        [(part, corner, quarters, how)] - by exact quarter turns. The head and everything of the pose in none of its
        parts are checked unchanged."""
        rig = self.rig
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        left = self.left_of(name) + dx
        top = rig.GY - (ys.max() + 1 - SOLE_UP.get(name, 0)) - lift
        if moves or spins or turns:
            hx, hy = head_at(name)
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + HEAD_H, hx:hx + HEAD_W] = self.head()
            d = IB.vary(d, PARTS[name], self.D.outline, moves, (), None, head, VPAD, name, turns, spins)
            left, top = left - VPAD, top - VPAD
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.D.d, (HEAD_X, HEAD_Y), (HEAD_W, HEAD_H),
                                        [(load(f"pose_{n}.png"), head_at(n)) for n in AT])
        return self._head


# ------------------------------------------------------------------------------------------------- the in-betweens
# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): polygons in each pose picture's own squares.
# The plate with the near arm that holds it turns about the shoulder (inbetween.spin: the join hidden under the
# shoulder pad), the far arm - the flask hand - about its shoulder; the far arm reaching for the grab slides along
# itself in under the shoulder; the flask flung out of his hand in the death flies on by itself. The head (HEAD_X ..,
# pack_singed_poses.HEAD), the tank and the rest of the body are in no part: they never change.
HEAD_X, HEAD_Y, HEAD_W, HEAD_H = 21, 13, 12, 12
VPAD = 30                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "a_wind": {"plate": [[(0, 0), (31, 0), (31, 43), (32, 43), (32, 49), (28, 49), (28, 61), (0, 61)]]},
    "a_smash": {"plate": [[(44, 28), (49, 26), (53, 29), (59, 33), (67, 40), (76, 50), (76, 62), (60, 62),
                           (51, 53), (50, 44), (50, 36), (46, 34), (43, 32)]]},
    "e_grab": {"farm": [(41, 19, 60, 34)]},
    "e_heave": {"farm": [[(17, 9), (28, 9), (28, 26), (32, 28), (32, 34), (28, 34), (24, 29), (18, 22)]]},
    "e_throw": {"farm": [[(13, 11), (34, 11), (35, 15), (35, 24), (30, 24), (13, 22)]]},
    "w_wind": {"farm": [[(45, 0), (59, 0), (59, 20), (55, 22), (52, 25), (49, 22), (49, 16), (45, 8)]]},
    "w_throw": {"farm": [[(50, 3), (70, 3), (70, 19), (50, 19)]]},
    "r_drink": {"farm": [[(42, 0), (56, 0), (56, 17), (46, 22), (43, 27), (40, 27), (40, 21), (42, 13)]]},
    "r_rage": {"farm": [[(48, 17), (61, 17), (61, 33), (52, 31), (48, 27)]]},
    "d_stagger": {"farm": [[(44, 0), (61, 0), (61, 10), (50, 12), (46, 16), (43, 16), (43, 10)]],
                  "flask": [(53, 12, 63, 26)]},
}
# the point each part turns about (square corners): a limb about the corner where it leaves the body on the side it
# turns away from (so its root swings in under the body and no gap opens), the flask about its middle
PIVOT = {("a_wind", "plate", "cw"): (32, 50), ("a_wind", "plate", "ccw"): (32, 43),
         ("a_smash", "plate", "ccw"): (44, 33),
         ("e_heave", "farm", "cw"): (28, 29), ("e_throw", "farm", "cw"): (35, 24),
         ("w_wind", "farm", "cw"): (49, 21), ("w_throw", "farm", "ccw"): (50, 19), ("w_throw", "farm", "cw"): (50, 13),
         ("r_drink", "farm", "cw"): (41, 21), ("r_rage", "farm", "ccw"): (48, 27),
         ("d_stagger", "farm", "ccw"): (43, 16), ("d_stagger", "flask", "q"): (58, 19)}


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_singed.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28: the plate raised, the smash landing at a_hit 11 (183 ms), back to the idle;
# E (skill, e_dur 30 = 500 ms): the grab at e_grab 10 (167 ms), heaved over the shoulder, thrown behind (e_fly 16 in the
# air from the grab);
# W (skill2, w_dur 30 = 500 ms): the flask raised, thrown at w_rel 12 (200 ms);
# R (ult, r_dur 40 = 667 ms): the potion raised, the rush;
# the walk (league_braum / league_zac): per frame the near leg's (dx, dy, lift), the far leg's, the figure's rise, the
# arms' swing (columns: the plate arm, the flask arm - against the legs)
#
# The in-betweens (2026-11-14: the attack played 3 poses, E 3, W and R 2 each, the death 2 and a flash): each span
# above is shared out over more frames (inbetween.spans: whole ms, none under 50), so every action is as long as it was
# and its strike still begins on its millisecond - the smash at 183, the grab at 167 and the throw at 334, the flask
# let go at 200, the rage at 333, the slump at 400. A frame that is only its neighbour moved whole is no new pose: one
# stays only where the move is the motion (the lunge of the smash, the knock-back), never more than two frames of one
# drawing in a row. The walk and the hit are as they were.
MS = {"idle": [1000], "run": [100] * 8,
      "attack": IB.spans((183, 3), (167, 3), (117, 1)),
      "skill": IB.spans((167, 2), (167, 2), (166, 2)),
      "skill2": IB.spans((200, 3), (300, 4, (3, 4, 4, 4))),
      "ult": IB.spans((333, 3), (334, 3)),
      "hit": [100, 100],
      "dead": IB.spans((400, 4, (7, 8, 9, 10)), (1000, 2, (8, 92)))}
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

    def at(name, ddx=0, dlift=0, **how):
        dx, lift = AT[name]
        return q(name, dx + ddx, lift + dlift, **how)

    def spin(name, part, degrees, how="under"):
        """The pose's part turned clockwise by `degrees` (negative: counter-clockwise) about its pivot (PIVOT)."""
        return [(part, PIVOT[(name, part, "cw" if degrees > 0 else "ccw")], degrees, how)]
    out = {}
    out["idle"] = [p()]
    # run (League's singed_run shows his back): league_braum's walk on the design's own legs
    out["run"] = [p(whole=(0, -r), near_leg=n, far_leg=f, near_at=(sw[0], 0), far_at=(sw[1], 0)) for n, f, r, sw in WALK]
    # auto attack (League's singed_attack1: the plate swung up, then smashed down in front): the plate coming up, raised
    # back over his shoulder, his body already in the smash with the plate still coming over; smashed a step ahead,
    # the plate bounced, at rest; the idle
    out["attack"] = [at("a_wind", spins=spin("a_wind", "plate", 25)), at("a_wind"),
                     at("a_smash", spins=spin("a_smash", "plate", -65)),
                     at("a_smash", 2), at("a_smash", spins=spin("a_smash", "plate", -10)), at("a_smash"), p()]
    # E Fling (singed_spell3: the grab, the heave over the shoulder, the follow-through): the hand shooting out, the
    # grab; the far arm coming up with the heave, heaved; the arm still up as he throws, thrown behind
    out["skill"] = [at("e_grab", moves=[("farm", (-8, 0), "under")]), at("e_grab"),
                    at("e_heave", spins=spin("e_heave", "farm", 45)), at("e_heave"),
                    at("e_throw", spins=spin("e_throw", "farm", 40)), at("e_throw")]
    # W Mega Adhesive (singed_spell2: the flask raised, thrown): the flask brought up from before him in two steps,
    # raised; let go with the arm still high, thrown, the arm swinging on down, back
    out["skill2"] = [at("w_wind", spins=spin("w_wind", "farm", 70)), at("w_wind", spins=spin("w_wind", "farm", 30)),
                     at("w_wind"),
                     at("w_throw", spins=spin("w_throw", "farm", -35)), at("w_throw"),
                     at("w_throw", spins=spin("w_throw", "farm", 12)), at("w_throw")]
    # R Insanity Potion (singed_spell4: the potion raised, the rush): the potion brought up to his mouth in two steps,
    # drunk; the arm coming down and out in two steps as he hunches into the rage
    out["ult"] = [at("r_drink", spins=spin("r_drink", "farm", 50)), at("r_drink", spins=spin("r_drink", "farm", 20)),
                  at("r_drink"),
                  at("r_rage", spins=spin("r_rage", "farm", -45)), at("r_rage", spins=spin("r_rage", "farm", -18)),
                  at("r_rage")]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's singed_death: staggering back, down on the ground): struck; knocked back in three steps with the
    # flung arm going on back and the flask he lost tumbling away; dropping, down
    flask = PIVOT[("d_stagger", "flask", "q")]
    out["dead"] = [R.flash(at("d_stagger")),
                   at("d_stagger", -2, 1, spins=spin("d_stagger", "farm", -12), moves=[("flask", (4, -3), "over")]),
                   at("d_stagger", -4, 2, spins=spin("d_stagger", "farm", -25), moves=[("flask", (8, -5), "over")],
                      turns=[("flask", flask, 1, "over")]),
                   at("d_stagger", -5, 1, spins=spin("d_stagger", "farm", -35), moves=[("flask", (12, -4), "over")],
                      turns=[("flask", flask, 2, "over")]),
                   at("d_down", 0, 3), at("d_down")]
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
