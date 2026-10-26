#!/usr/bin/env python3
"""league_taliyah's action frames: Taliyah's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-24: 「动作包和特效都交付了 做到完美后喊我review」).

    python tools/art/rig_taliyah.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_taliyah.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_taliyah_model.py, design_taliyah_poses.py):
  hd/idle.png         Taliyah, 3/4 front facing right, 33 x 70 at PPU 1.75 (40 game px hair top to soles): the idle and
                      the hit;
  hd/pose_<name>.png  Codex's key poses read back at the body's scale with the design's head
                      (assets/source/taliyah/POSE_PROMPTS.md): a_wind a_throw q_raise q_cast e_raise e_sweep w_crouch
                      w_push r_call surf1 d_stagger d_down (surf2 / surf3 are not used: each stood on its own boulder, a
                      different size and shape from surf1's, and the run loops one boulder - see the run below).
Placing a pose: across, the middle of its planted soles (FEET) on the design's (DESIGN_FEET), so a stance widens or
narrows round one point and no planted boot slides from frame to frame; up and down, its lowest row on the ground.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The run is the passive's rock surf (League's Run_Passive; the user's picks, 2026-10-24: the move is the surf): surf1 -
the girl crouched on her boulder, the boulder's bottom middle on the design's feet middle - looped with whole-square
moves only: the girl's upper body (rows above BOB_ROW, the head, the arms, the coat) sinks a row and rises (her legs
lose / keep their top row, league_braum's way), and the two coat panels flying behind her flutter (ppu_rig.sway: whole
columns lifted step by step toward the free end, attached at the body). The boulder never changes.
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

HERO = "taliyah"
PPU = 1.75
SRC = os.path.join(R.ROOT, "assets", "source", "taliyah", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design
STAND = 18                     # the column between her feet: the standing point


def design():
    D = CutDesign(load("idle.png"), px=STAND)
    D.part("body", D.rest())
    return D


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


# ------------------------------------------------------------------------------------------------- the run (surf1)
# surf1 (hd/pose_surf1.png, 83 x 85): the girl crouched on her boulder; the boulder's bottom middle (BOULDER_FOOT) on
# the design's feet middle. Rows above BOB_ROW are her upper body (the head, the arms, the coat's top, the thighs' tops)
# - sunk by whole rows over the rest; PANELS: the two coat panels flying behind her - boxes (x0, y0, x1, y1) whose
# union is the panel, and the columns (x0, x1) it sways over (its free end at the left) - the near hand resting on the
# boulder (HAND) is never moved, nor the boulder's red wrap under the lower panel (it starts at column 22, row 56).
BOULDER_FOOT = 50              # the boulder's bottom middle column on surf1
BOB_ROW = 44
PANELS = [([(0, 30, 33, 45)], (0, 33)),
          ([(8, 46, 21, 62), (22, 46, 30, 55)], (8, 30))]
HAND = (29, 47, 41, 57)
# per frame: (the upper body's rows sunk, the panels' sway: rows their free ends are lifted)
SURF = [(0, 0), (1, 1), (1, 0), (0, -1)]
RIDE_UP = 36                   # R far: her boulder riding on the wall's pillars (24 game px tall: 42 squares), a little sunk in


def surf_frame(sunk, lift):
    a = load("pose_surf1.png")
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    op = a[..., 3] > 0
    hand = (xx >= HAND[0]) & (xx <= HAND[2]) & (yy >= HAND[1]) & (yy <= HAND[3])
    masks = []
    for rects, _ in PANELS:
        m = np.zeros((H, W), bool)
        for x0, y0, x1, y1 in rects:
            m |= (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        masks.append(m & op & ~hand)
    panel = np.any(masks, axis=0)
    upper = op & (yy < BOB_ROW) & ~panel & ~hand
    rest = op & ~upper & ~panel
    out = np.zeros_like(a)
    out[rest] = a[rest]
    up_l = np.zeros_like(a)
    up_l[upper] = a[upper]
    up_l = np.roll(up_l, sunk, axis=0)
    m = up_l[..., 3] > 0
    out[m] = up_l[m]
    for pm, (_, (x0, x1)) in zip(masks, PANELS):
        box = np.zeros_like(a)
        box[pm] = a[pm]
        box = R.sway(np.roll(box, sunk, axis=0), x0, x1, lift, attach="right")
        bm = (box[..., 3] > 0) & (out[..., 3] == 0)
        out[bm] = box[bm]
    return out


# ------------------------------------------------------------------------------------------------- the canvas
def feet(name):
    """The middle of a pose's planted soles: (FEET[name]) on hd/pose_<name>.png."""
    n0, n1 = FEET[name]
    return (n0 + n1) / 2


class Form:
    """The design and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(70, 60, 60, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0)):
        """The design moved by whole squares."""
        wx, wy = whole
        can = R.compose(self.rig, [(self.L["body"], dict(dx=wx, dy=wy))])
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def left_of(self, name):
        """The canvas column of a pose's first column: its soles' middle on the design's (FEET), or the head of the pose
        it follows (HEAD_BACK)."""
        if name in HEAD_BACK:
            prev, back = HEAD_BACK[name]
            hx_prev = self.left_of(prev) + head_at(prev)[0]
            return hx_prev + back - head_at(name)[0]
        return self.rig.ox + int(round((DESIGN_FEET[0] + DESIGN_FEET[1]) / 2 - feet(name)))

    def place(self, d, left, lift=0):
        rig = self.rig
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        top = rig.GY - (ys.max() + 1) - lift
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can

    def posed(self, name, dx=0, lift=0):
        """A Codex pose standing where the design stands (left_of), moved dx squares, `lift` rows over the ground."""
        return self.place(load(f"pose_{name}.png"), self.left_of(name) + dx, lift)

    def running(self, name):
        """A run pose (run1-run4): the head box on the same column in every frame (RUN_DX squares ahead of the design's
        head: she leans into the run), so the body does not sway sideways as the planted foot changes; its lowest row
        (the foot on the ground) on the ground line."""
        left = self.rig.ox + PK_HEAD_C0 + RUN_DX - head_at(name)[0]
        return self.place(load(f"pose_{name}.png"), left)

    def surf(self, sunk, lift, up=0):
        """A surf frame (the run), its boulder `up` rows over the ground (the ride on top of her wall)."""
        left = self.rig.ox + int(round((DESIGN_FEET[0] + DESIGN_FEET[1]) / 2 - BOULDER_FOOT))
        return self.place(surf_frame(sunk, lift), left, lift=up)


def head_at(name):
    """The head box's top-left square in hd/pose_<name>.png (design_taliyah_poses' json)."""
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_taliyah.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27: a stone called up over the far hand, flicked at a_rel 10 (167 ms), back to the idle;
# Q (skill, q_dur 16 = 267 ms): the call, the first rock at q_rel 8 (133 ms) - she walks on, the other four following
# q_gap 12 apart (League's volley over about a second);
# W + E (skill2's CasterAnimation, w_dur 36 = 600 ms): both hands up, the mines swept out in front of her (e_rel 14 =
# 233 ms), the press on the ground and W's warning crack (w_rel 21 = 350 ms), the shove;
# R near (ult, r_dur 40 = 667 ms): the crouch, the upright wall called up (r_rel 16 = 267 ms); R far (ult_ride): the
# wall called, then she rides her boulder along it (the surf);
# the run: on her feet, run1-run4 (one stride of League's Run1, two steps in RUN_MS x 4); the surf (out of fights,
# league_taliyah's view.rs swaps run -> surf): the boulder, 4 frames.
RUN_MS = 125
MS = {"idle": [1000], "run": [RUN_MS] * 4, "surf": [120] * 4,
      "attack": [167, 183, 100],
      "skill": [133, 134],
      "skill2": [100, 133, 117, 250],
      "ult": [167, 500],
      "ult_ride": [133, 70, 70, 70, 70],
      "hit": [100, 100],
      "dead": [150, 250, 1000]}
# where each pose stands: its planted soles' outer columns on hd/pose_<name>.png (the near sole's left, the far sole's
# right; a pose on one foot: that sole's two edges - read from the boots' brown squares in the lowest rows) round the
# design's (9 and 27); d_down (sitting, the legs out to the right) keeps the stagger's head column moved HEAD_BACK
# squares back.
DESIGN_FEET = (9, 27)
# the run poses line up on their heads: the design's head box starts at column PK_HEAD_C0 (pack_taliyah_poses.HEAD), the
# runner's RUN_DX squares further on
PK_HEAD_C0 = 2
RUN_DX = 1
FEET = {"a_wind": (10, 30), "a_throw": (19, 54), "q_raise": (23, 27), "q_cast": (14, 61), "e_raise": (13, 18),
        "e_sweep": (7, 44), "w_crouch": (26, 33), "w_push": (8, 33), "r_call": (10, 35), "d_stagger": (23, 52)}
HEAD_BACK = {"d_down": ("d_stagger", -3)}
# and moved dx squares from there (League's lunges), `lift` rows off the ground
AT = {k: (0, 0) for k in list(FEET) + list(HEAD_BACK)}


def actions(F):
    p = F.pose

    def at(name, ddx=0, dlift=0):
        dx, lift = AT[name]
        return F.posed(name, dx + ddx, lift + dlift)
    out = {}
    out["idle"] = [p()]
    # run: on her feet (League's taliyah_run1; the user, 2026-10-26: 「塔利亚怎么是飞着走路的 不对吧」)
    out["run"] = [F.running(f"run{k}") for k in range(1, 5)]
    # surf: the passive's rock surf (League's taliyah_run_passive), surf1 looped - out of fights (league_taliyah)
    out["surf"] = [F.surf(s, k) for s, k in SURF]
    # auto attack (League's taliyah_attack1: a stone called up over the far hand, flicked forward)
    out["attack"] = [at("a_wind"), at("a_throw"), p()]
    # Q Threaded Volley (taliyah_spell1_0: the far arm up calling the rocks, then pushed forward with the volley)
    out["skill"] = [at("q_raise"), at("q_cast")]
    # W Seismic Shove with E Unraveled Earth (taliyah_spell3: both hands up, the mines swept out; taliyah_spell2_0: the
    # palm on the ground, the shove)
    out["skill2"] = [at("e_raise"), at("e_sweep"), at("w_crouch"), at("w_push")]
    # R Weaver's Wall (taliyah_spell4: the crouch, the far arm raised calling the wall)
    out["ult"] = [at("w_crouch"), at("r_call")]
    # R far: the wall called, then riding it on her boulder (the surf frames)
    out["ult_ride"] = [at("r_call")] + [F.surf(s, k, up=RIDE_UP) for s, k in SURF]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's taliyah_death: reeling back, sitting down on the ground)
    out["dead"] = [R.flash(at("d_stagger")), at("d_stagger"), at("d_down")]
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
