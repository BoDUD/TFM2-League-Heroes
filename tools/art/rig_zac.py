#!/usr/bin/env python3
"""league_zac's action frames: Zac's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-23: 「不行你做不出的地方让codex帮忙 做的太奇怪了」「不用参照oppi 参照英雄联盟」, then 「扎克的动作帧交付了 你做到完美后喊我review」).

    python tools/art/rig_zac.py --parts DIR       # the design with its parts tinted (12x)
    python tools/art/rig_zac.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_zac.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_zac_model.py, design_zac_poses.py):
  hd/idle.png         Zac, 3/4 front facing right, 87 x 66 at PPU 1.5 (44 game px tendril top to soles): the idle, the
                      hit, the run;
  hd/pose_<name>.png  Codex's key poses read back on their own grid with the design's head (assets/source/zac/
                      POSE_PROMPTS.md): a_wind a_punch q_wind q_reach q_lift q_slam e_plant e_pull e_fly e_land r_crouch
                      r_jump r_ball r_splat d_stagger d_melt d_puddle.
Placing a pose: across, the middle of its squares (MEAN: the mean column) on the design's, moved dx squares (League's
lunges and pulls); up and down, its soles on the ground row (its lowest square) or `lift` rows over it (in the air).
A pose's arm can be drawn longer like rubber (RUBBER: a stretch of it with level edges, each column repeated in turn so
its shading is drawn out, the hand pushed out; the body stays where it stands): the attack's arm swung far back and the
fist thrown out on a long arm, as League's Zac_attack1 does.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The run is league_braum's / league_warwick's approved walk for big heroes: the design's own legs under the hip band, one
lifted per frame by losing its top rows and stepped forward, the body floating a little, the arms swinging a square
against the legs, the tendril swaying (no part turned or stretched: 「有点变形了吧？手」).
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
from rig_wukong import CutDesign as _Cut, P, pad  # noqa: E402

HERO = "zac"
PPU = 1.5
SRC = os.path.join(R.ROOT, "assets", "source", "zac", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 44                     # the column between his feet: the standing point
TENDRIL_ROWS = 12              # the tendril: rows above this (over the head)
NEAR_ARM = {(19, 29): (0, 25), (30, 33): (0, 24), (34, 65): (0, 22)}   # rows -> columns of the near arm
LEG_BAND = 47                  # the legs: the rows under it
LEG_SPLIT = 44                 # the column between the near leg and the far leg


def dark(d):
    return (d[..., 3] > 0) & (d[..., :3].astype(int).sum(-1) < 70)


def far_arm_mask(d):
    """The far arm: the fill right of the face bounded by its own outline (the outline-bounded region reaching the right
    edge), with every outline square touching it."""
    op = d[..., 3] > 0
    fill = op & ~dark(d)
    lbl, n = ndimage.label(fill)
    best, size = 0, 0
    for k in range(1, n + 1):
        m = lbl == k
        xs = np.nonzero(m.any(0))[0]
        if xs.min() >= 58 and m.sum() > size:
            best, size = k, int(m.sum())
    core = lbl == best
    ring = ndimage.binary_dilation(core, structure=np.ones((3, 3))) & dark(d)
    return core | ring


def near_arm_mask(d):
    m = np.zeros(d.shape[:2], bool)
    for (y0, y1), (x0, x1) in NEAR_ARM.items():
        m[y0:y1 + 1, x0:x1 + 1] = True
    return m & (d[..., 3] > 0)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    far = far_arm_mask(d)
    D.part("tendril", op & (yy < TENDRIL_ROWS))
    D.part("far_arm", far & (yy >= TENDRIL_ROWS))
    D.part("near_arm", near_arm_mask(d))
    legs = op & (yy > LEG_BAND) & ~far
    D.part("near_leg", legs & (xx <= LEG_SPLIT) & (xx > NEAR_ARM[(34, 65)][1]))
    D.part("far_leg", legs & (xx > LEG_SPLIT))
    D.part("body", D.rest())
    return D


TINT = {"tendril": (60, 200, 255), "far_arm": (255, 220, 0), "near_arm": (0, 255, 120), "near_leg": (255, 0, 255),
        "far_leg": (255, 120, 0)}


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


def sway(layer, k):
    """The tendril's knob swung k columns (negative: back): its rows from the root up moved by an amount growing to k
    at the top (whole squares)."""
    if not k:
        return layer
    out = np.zeros_like(layer)
    ys = np.nonzero(layer[..., 3].any(1))[0]
    if not len(ys):
        return layer
    y0, y1 = ys.min(), ys.max()
    for y in range(y0, y1 + 1):
        t = (y1 - y) / max(1, y1 - y0)
        out[y] = np.roll(layer[y], int(round(k * t)), axis=0)
    return out


def stretch(d, x0, x1, k, rows, side):
    """An arm drawn k columns longer like rubber: its columns x0..x1 in `rows` (a stretch of it with level edges and no
    other part in those rows) drawn n + k wide, each column repeated in turn (nearest: the shading drawn out, no square
    made up), the part beyond pushed out - side +1 to the right, -1 to the left (the picture grows k columns there)."""
    H, W = d.shape[:2]
    out = np.zeros((H, W + k, 4), d.dtype)
    r0, r1 = rows
    n = x1 - x0 + 1
    cols = [x0 + j * n // (n + k) for j in range(n + k)]
    if side > 0:
        out[:, :W] = d
        out[r0:r1, x0:] = 0
        out[r0:r1, x0:x0 + n + k] = d[r0:r1][:, cols]
        out[r0:r1, x0 + n + k:] = d[r0:r1, x1 + 1:]
    else:
        out[:, k:] = d
        out[r0:r1, :x1 + 1 + k] = 0
        out[r0:r1, :x0] = d[r0:r1, :x0]
        out[r0:r1, x0:x0 + n + k] = d[r0:r1][:, cols]
    return out


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
MEAN = None                    # the design's mean column (set by Form)


def middle(d):
    """The mean column of a picture's squares."""
    return float(np.nonzero(d[..., 3] > 0)[1].mean())


class Form:
    """The design's layers and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(70, 70, 70, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}
        self.mid = middle(D.d)

    def pose(self, whole=(0, 0), near_at=(0, 0), far_at=(0, 0), near_leg=(0, 0, 0), far_leg=(0, 0, 0), tendril=0):
        """The design with its parts moved by whole squares: whole (dx, dy); an arm's (dx, dy); a leg's (dx, dy, lift)
        - lifted by losing its top rows (league_braum); the tendril's knob swung (columns)."""
        wx, wy = whole
        L = self.L
        layers = [(lifted(L["far_leg"], far_leg[2]), dict(dx=wx + far_leg[0], dy=wy + far_leg[1])),
                  (sway(L["tendril"], tendril), dict(dx=wx, dy=wy)),
                  (L["body"], dict(dx=wx, dy=wy)),
                  (lifted(L["near_leg"], near_leg[2]), dict(dx=wx + near_leg[0], dy=wy + near_leg[1])),
                  (L["near_arm"], dict(dx=wx + near_at[0], dy=wy + near_at[1])),
                  (L["far_arm"], dict(dx=wx + far_at[0], dy=wy + far_at[1]))]
        can = R.compose(self.rig, layers)
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def posed(self, name, dx=0, lift=0, rubber=0):
        """A Codex pose (hd/pose_<name>.png) standing where the design stands: the middle of its squares on the
        design's, moved dx squares; its lowest row on the ground, `lift` rows above it in the air. `rubber`: its RUBBER
        arm that many squares longer, the body left where the pose stands."""
        rig = self.rig
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        left = rig.ox + int(round(self.mid - middle(d))) + dx
        top = rig.GY - (ys.max() + 1) - lift
        if rubber:
            x0, x1, rows, side = RUBBER[name]
            d = stretch(d, x0, x1, rubber, rows, side)
            left -= rubber if side < 0 else 0
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_zac.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28: the wind-up, the arm stretched back, the lunge, the fist out on the long arm landing at
# a_hit 11 (183 ms), the arm snapping back, the idle;
# Q (skill, q_dur 24 = 400 ms): the wind-up, the long grab from q_rel 8 (133 ms) held; skill_slam (q_slam 18 = 300 ms):
# lifting him, the slam landing at q_slam_at 8 (133 ms);
# E: skill2 (e_wind 36 = 600 ms) the arms planted, then pulled back; skill2_fly (held while he flies); skill2_land
# (e_land 16 = 267 ms);
# R: ult (one hop, r_air 25 = 417 ms): the crouch, up, balled at the top, coming down; ult_land (r_land 12 = 200 ms): the
# splat, back up into the crouch;
# the walk (league_braum / league_warwick): per frame the near leg's (dx, dy, lift), the far leg's, the figure's rise, the
# arms' swing (columns: the near arm, the far arm - against the legs), the tendril's sway
MS = {"idle": [1000], "run": [110] * 8,
      "attack": [67, 67, 49, 100, 50, 50, 84],
      "skill": [133, 267], "skill_slam": [133, 167],
      "skill2": [200, 400], "skill2_fly": [100, 100], "skill2_land": [167, 100],
      "ult": [83, 83, 167, 84], "ult_land": [117, 83],
      "hit": [100, 100],
      "dead": [200, 300, 800],
      "split_in": [150, 150], "split": [1000], "reform": [150, 150], "split_idle": [1000], "split_hit": [100, 100]}
WALK = [((0, 0, 0), (0, 0, 2), 1, (0, 0), 0), ((0, 0, 0), (2, 0, 4), 2, (1, -1), 1),
        ((0, 0, 0), (2, 0, 2), 1, (1, -1), 1), ((0, 0, 0), (2, 0, 0), 0, (0, 0), 0),
        ((0, 0, 2), (0, 0, 0), 1, (0, 0), -1), ((2, 0, 4), (0, 0, 0), 2, (-1, 1), -1),
        ((2, 0, 2), (0, 0, 0), 1, (-1, 1), 0), ((2, 0, 0), (0, 0, 0), 0, (0, 0), 0)]
# where each pose stands (dx squares from the design's middle) and how high (rows off the ground)
AT = {"a_wind": (0, 0), "a_punch": (2, 0), "q_wind": (-1, 0), "q_reach": (2, 0), "q_lift": (4, 0), "q_slam": (1, 0),
      "e_plant": (1, 0), "e_pull": (-4, 0), "e_fly": (0, 12), "e_land": (0, 0),
      "r_crouch": (0, 0), "r_jump": (0, 10), "r_ball": (6, 22), "r_splat": (0, 0),
      "d_stagger": (0, 0), "d_melt": (0, 0), "d_puddle": (0, 0)}
# the arm a pose can stretch (stretch()): its columns x0..x1 and rows (the pose's own squares), the side the hand is on -
# a_wind's near arm swung back (its upper arm, level along the top), a_punch's far arm (the forearm, shoulder to fist)
RUBBER = {"a_wind": (18, 36, (0, 41), -1), "a_punch": (84, 99, (0, 47), +1)}


def actions(F):
    p, q = F.pose, F.posed

    def at(name, ddx=0, dlift=0, rubber=0):
        dx, lift = AT[name]
        return q(name, dx + ddx, lift + dlift, rubber)
    out = {}
    out["idle"] = [p()]
    # run (League's Zac_run_Slow, a heavy waddle): league_braum's walk on the design's own legs
    out["run"] = [p(whole=(0, -r), near_leg=n, far_leg=f, near_at=(sw[0], 0), far_at=(sw[1], 0), tendril=t)
                  for n, f, r, sw, t in WALK]
    # auto attack (League's Zac_attack1: the near arm swung back and stretched far behind him, the lunge, the punch
    # thrown out on an arm stretched like rubber and snapping back; the user, 2026-10-31: 「扎克的平A动作有点奇怪」 - it
    # was the wind-up and the lunge held 183 / 167 ms each, then the idle, three pictures popping in turn)
    out["attack"] = [at("a_wind"), at("a_wind", rubber=10), at("a_punch"), at("a_punch", rubber=12),
                     at("a_punch", rubber=6), at("a_punch"), p()]
    # Q Stretching Strikes (Zac_Spell1_max: the arm swung up and back, then shot out along the ground; Zac_Spell1_Slam:
    # both arms up with the catch, then the slam)
    out["skill"] = [at("q_wind"), at("q_reach")]
    out["skill_slam"] = [at("q_lift"), at("q_slam")]
    # E Elastic Slingshot (Zac_spell3_windup: the arms planted, the body pulled back; Zac_spell3_flying; the landing)
    out["skill2"] = [at("e_plant"), at("e_pull")]
    out["skill2_fly"] = [at("e_fly"), at("e_fly", dlift=1)]
    out["skill2_land"] = [at("e_land"), at("r_crouch")]
    # R Let's Bounce! (Zac_Revert_spell4: the crouch, up, balled; Zac_Spell4_SnapCastRun: arms spread in the air;
    # Zac_Spell4_3: squashed on the ground)
    out["ult"] = [at("r_crouch"), at("r_jump"), at("r_ball"), at("r_jump", dlift=-2)]
    out["ult_land"] = [at("r_splat"), at("r_crouch")]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's Zac_death2: staggering, melting down, a puddle)
    out["dead"] = [R.flash(at("d_stagger")), at("d_melt"), at("d_puddle")]
    # Cell Division's split (league_zac's add-on; its copy of the kit plays split_in, split and reform, and league_zac's
    # view hook draws idle / hit as split_idle / split_hit while he is a puddle): melted down to the puddle, held, and
    # back up through the melt and the crouch - the death's own frames
    out["split_in"] = [at("d_melt"), at("d_puddle")]
    out["split"] = [at("d_puddle")]
    out["reform"] = [at("d_melt"), at("r_crouch")]
    out["split_idle"] = [at("d_puddle")]
    out["split_hit"] = [R.flash(at("d_puddle")), at("d_puddle")]
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
        tinted(D).save(lp(os.path.join(a.parts, "zac_parts.png")))
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
