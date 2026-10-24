#!/usr/bin/env python3
"""league_belveth's action frames: Bel'Veth's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-24: 「动作帧和特效都交付了 做到完美了喊我review」).

    python tools/art/rig_belveth.py --parts DIR       # the design with its parts tinted (12x)
    python tools/art/rig_belveth.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_belveth.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_belveth_model.py, design_belveth_poses.py):
  hd/idle.png         Bel'Veth, 3/4 front facing right, 86 x 82 at PPU 1.75 (40 game px head top to claws): the idle,
                      the hit, the glide;
  hd/pose_<name>.png  Codex's key poses read back with the design's head, the bodies brought to the design's size
                      (assets/source/belveth/POSE_PROMPTS.md): a_wind a_slash q_dash w_coil w_slam e_spin1 e_spin2
                      r_curl r_rise d_reel d_down.
Placing a pose: across, its head box on the design's head box (one face that never jumps; she hovers on her claws, so
there is no planted foot to keep), moved dx squares (League's lunges); up and down, its lowest square on the ground
row, or `lift` rows over it (she flies in the dash, the storm and the rise) - the storm's two poses, played in turn every
75 ms, with their heads on one row instead (the highest either reaches standing; e_spin1's head sat 13 rows lower over
its claws than e_spin2's: the face jumped), so e_spin1 flies higher.
The idle is the design alone (no breathing: hero_reels cuts the idle and ban/pick snippets from these actions).
The move is her glide (League's RunClosed: she floats on, the claws trailing): the design whole, bobbing up and down a
row, the claws swinging a square back and forth under the hem and the tail's tip waving - no part turned or stretched.
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

HERO = "belveth"
PPU = 1.75
SRC = os.path.join(R.ROOT, "assets", "source", "belveth", "hd")


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


class CutDesign(_Cut):
    def __init__(self, d, px):
        super().__init__(d, px)
        self.hero, self.ppu = HERO, PPU


# ------------------------------------------------------------------------------------------------- the design's parts
STAND = 58                     # the column under her body's middle: the standing point
HEAD_X, HEAD_Y = 46, 11        # the head box's top-left square on hd/idle.png (pack_belveth_poses.HEAD)
CLAWS = (72, 43)               # the claws: rows from 72 down, columns from 43 right (under the hem)
TAIL = (66, 33)                # the tail: rows from 66 down, columns left of 33 (the near cloak's edge is right of it)


def design():
    d = load("idle.png")
    D = CutDesign(d, px=STAND)
    op = d[..., 3] > 0
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    D.part("claws", op & (yy >= CLAWS[0]) & (xx >= CLAWS[1]))
    D.part("tail", op & (yy >= TAIL[0]) & (xx < TAIL[1]))
    D.part("body", D.rest())
    return D


TINT = {"claws": (255, 220, 0), "tail": (0, 255, 120)}


def tinted(D, z=12):
    out = D.d.copy()
    for name, c in TINT.items():
        m = D.parts[name]
        out[m, :3] = (out[m, :3].astype(float) * 0.45 + np.array(c) * 0.55).astype(np.uint8)
    big = np.repeat(np.repeat(out, z, 0), z, 1)
    bg = Image.new("RGBA", (big.shape[1], big.shape[0]), (200, 205, 195, 255))
    bg.alpha_composite(Image.fromarray(big))
    return bg.convert("RGB")


def close_cracks(can, outline, most=12, slit=40):
    """Enclosed gaps a move opened: up to `most` squares, or up to `slit` squares but only one square across - the
    outline (gap-check; rig_warwick.close_cracks). The design's own gaps between the claws stay open."""
    op = can[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    out = can.copy()
    for j in range(1, n + 1):
        h = lab == j
        k = int(h.sum())
        if k <= most or (k <= slit and ndimage.distance_transform_edt(h).max() <= 1.5):
            out[h] = (*outline, 255)
    return out


def head_at(name):
    """The head box's top-left square in hd/pose_<name>.png (design_belveth_poses' json)."""
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)["head_at"]


class Form:
    """The design's layers and Codex's poses on one canvas."""

    def __init__(self, D, rig_pad=(70, 70, 60, 24)):
        self.D = D
        self.rig = R.Rig(D, pad=rig_pad)
        self.L = {k: pad(D.layer(k)) for k in D.order}

    def pose(self, whole=(0, 0), claws=(0, 0), tail=(0, 0)):
        """The design with its parts moved by whole squares: whole (dx, dy); the claws' and the tail's (dx, dy)."""
        wx, wy = whole
        L = self.L
        layers = [(L["tail"], dict(dx=wx + tail[0], dy=wy + tail[1])),
                  (L["claws"], dict(dx=wx + claws[0], dy=wy + claws[1])),
                  (L["body"], dict(dx=wx, dy=wy))]
        can = R.compose(self.rig, layers)
        can[self.rig.GY:] = 0
        return close_cracks(can, self.D.outline)

    def ground_head(self, name):
        """The canvas row of a pose's head box top when it stands on its lowest square, AT's lift over the ground."""
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        return self.rig.GY - (ys.max() + 1) - AT[name][1] + head_at(name)[1]

    def posed(self, name, dx=0, lift=0):
        """A Codex pose (hd/pose_<name>.png) with its head box on the design's, moved dx squares; its lowest square on
        the ground, `lift` rows above it in the air."""
        rig = self.rig
        d = load(f"pose_{name}.png")
        ys = np.nonzero((d[..., 3] > 0).any(1))[0]
        hx, hy = head_at(name)
        left = rig.ox + HEAD_X - hx + dx
        top = rig.GY - (ys.max() + 1) - lift
        if name in HEAD_UP:   # the group's heads on one row: the highest any of them stands with its claws grounded
            top = min(self.ground_head(g) for g in HEAD_UP) - hy
        can = rig.canvas()
        ys_, xs_ = np.nonzero(d[..., 3] > 0)
        ty, tx = ys_ + top, xs_ + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys_, xs_]
        return can


# ------------------------------------------------------------------------------------------------- the actions
# ms per frame; the kit's ticks (tools/kit/build_belveth.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 367 ms = atk_dur 22: the wing raised, the slash landing at a_hit 9 (150 ms), back to the idle;
# Q (skill, q_dur 18 = 300 ms): the dash from q_go 3 (50 ms) for q_t 7 ticks (10 in the true form), then the idle;
# W (skill2, w_dur 30 = 500 ms): the tail raised, slammed at w_rel 12 (200 ms);
# R (ult, r_dur 40 = 667 ms): curled round the coral, risen in the true form at r_hit 20 (333 ms);
# the maelstrom (skill_e, played e_t 90 ticks = 1500 ms by a CasterAnimation, which loops the tag: league_garen's
# whirl): the two storm poses in turn.
MS = {"idle": [1000], "run": [110] * 6,
      "attack": [133, 117, 117],
      "skill": [250, 50],
      "skill2": [200, 300],
      "skill_e": [75] * 4,
      "ult": [333, 334],
      "hit": [100, 100],
      "dead": [150, 250, 1000]}
# the glide: per frame the figure's rise, the claws' (dx, dy), the tail's (dx, dy)
GLIDE = [(0, (0, 0), (0, 0)), (1, (-1, 0), (0, -1)), (2, (-1, 0), (0, -1)),
         (2, (0, 0), (0, 0)), (1, (1, 0), (0, 1)), (0, (1, 0), (0, 0))]
# each pose moved dx squares from the design's head column (League's lunges), `lift` rows off the ground
AT = {"a_wind": (0, 0), "a_slash": (0, 0), "q_dash": (4, 6), "w_coil": (0, 0), "w_slam": (0, 0), "e_spin1": (0, 4),
      "e_spin2": (0, 4), "r_curl": (0, 0), "r_rise": (0, 5), "d_reel": (-2, 0), "d_down": (-3, 0)}


# poses played in turn fast (the storm): placed by the head's height, so the face does not jump between them
HEAD_UP = {"e_spin1", "e_spin2"}


def actions(F):
    p, q = F.pose, F.posed

    def at(name, ddx=0, dlift=0):
        dx, lift = AT[name]
        return q(name, dx + ddx, lift + dlift)
    out = {}
    out["idle"] = [p()]
    # the glide (League's RunClosed)
    out["run"] = [p(whole=(0, -r), claws=c, tail=t) for r, c, t in GLIDE]
    # auto attack (League's Attack_Slow1a: the near wing raised, then slashed down across her front)
    out["attack"] = [at("a_wind"), at("a_slash"), p()]
    # Q Void Surge (Q_spell1: level, rushing forward)
    out["skill"] = [at("q_dash"), p()]
    # W Above and Below (Spell2_0: the tail raised, slammed)
    out["skill2"] = [at("w_coil"), at("w_slam")]
    # E Royal Maelstrom (Spell3_attack_slow: the wings up, swept out, in turn)
    out["skill_e"] = [at("e_spin1") if k % 2 == 0 else at("e_spin2") for k in range(len(MS["skill_e"]))]
    # R Endless Banquet (Spell4: curled round the coral, risen)
    out["ult"] = [at("r_curl"), at("r_rise")]
    out["hit"] = [R.flash(p(whole=(-2, 0))), p(whole=(-1, 0))]
    # death (League's Death: reeling back, sunk to the ground)
    out["dead"] = [R.flash(at("d_reel")), at("d_reel"), at("d_down")]
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
        tinted(D).save(lp(os.path.join(a.parts, "belveth_parts.png")))
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
