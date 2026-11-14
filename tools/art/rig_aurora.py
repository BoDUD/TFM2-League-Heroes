#!/usr/bin/env python3
"""league_aurora's action frames: her approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-23: 「Codex 照骨架画姿势」, then 「动作帧也交付了 你做到完美后喊我review」).

    python tools/art/rig_aurora.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_aurora.py                   # her frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_aurora_model.py, design_aurora_poses.py, design_aurora_legs.py):
  hd/idle.png             her, 3/4 front facing right, 53 x 104 at PPU 2.25 (38 game px hat top to soles, the ears
                          above): the idle, the hit;
  hd/pose_<name>.png      Codex's key poses read back at the design's size with the design's head put in
                          (assets/source/aurora/POSE_PROMPTS.md; the eight long-legged ones' legs shortened to the
                          design's by tools/art/design_aurora_legfix.py): a_wind a_point q_wind q_cast q_catch e_push e_hop
                          r_reach r_leap r_land w_hop run1-4 d_stagger d_slump.
Placing a pose (league_illaoi's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares, its soles on the ground row (its lowest square) or `lift` rows over it. The idle is the design alone
(no breathing: hero_reels cuts her idle snippets from these actions).
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
sys.path.insert(0, os.path.join(ROOT, "tools", "kit"))
import ppu_rig as R  # noqa: E402
import inbetween as IB  # noqa: E402
import pixel_down as PD  # noqa: E402
import pack_aurora_poses as PK  # noqa: E402
from build_aurora import P as KIT  # noqa: E402

HERO = "aurora"
PPU = 2.25
SRC = os.path.join(ROOT, "assets", "source", "aurora", "hd")
STAND = 31                     # the idle's standing column: under her middle, between her boots
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
FEET = R.FEET


# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): boxes and polygons in each pose picture's own
# squares. Her wand is a line one square thick, which breaks up when it is turned by any angle, so it only slides
# along itself by whole squares: back through her fist behind the hand (a thrust half out), on out of her hand (let
# go in the death). Her free arm turns about the shoulder (inbetween.spin). The head - the hat and the ears with it -
# and the rest of the body are in no part.
VPAD = 30                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "a_point": {"wand": [(77, 44, 120, 64)]},
    "q_cast": {"wand": [(73, 68, 110, 98)]},
    "e_push": {"wand": [[(57, 70), (89, 86), (89, 94), (80, 94), (57, 79)]]},
    "r_reach": {"wand": [(58, 70, 78, 95)]},
    "r_land": {"wand": [(58, 68, 80, 93)]},
    "d_stagger": {"wand": [(59, 64, 86, 92)], "arm": [(0, 54, 19, 65)]},
    "d_slump": {"wand": [(0, 84, 4, 85), (0, 86, 53, 90)]},
}


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
        self.rig = R.Rig(D, pad=(60, 90, 40, 12))      # room for the wand held out, the hops
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name)
        return d, (rig.ox + HEAD[0] - hx + dx, rig.GY - ground - lift)

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.d, HEAD, (PK.HW, PK.HH), [load_pose(n)[:2] for n in PK.POSES])
        return self._head

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - parts of the pose (PARTS) moved by whole squares, "under" the rest of her or
        "over" it; spins [(part, point, degrees, how)] - a part turned clockwise by any angle about a point."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        if moves or spins:
            hx, hy = load_pose(name)[1]
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + PK.HH, hx:hx + PK.HW] = self.head()
            d = IB.vary(d, PARTS[name], self.outline, moves, (), None, head, VPAD, name, (), spins)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


def ms_of(tick):
    return round(tick * 1000 / 60)


# ms per frame; the kit's ticks (tools/kit/build_aurora.py) match these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27, the bolt off the wand pointed out (a_rel 10 = 167 ms; the point from 120 ms);
# Twofold Hex 500 ms = q_dur 30, the hex flung on the sweep (q_rel 12 = 200 ms; the cast from 150 ms), the recall after;
# The Weirding 500 ms = e_dur 30, the blast off the wand thrust out (e_rel 12 = 200 ms; the push to 220 ms), then the
# hop back (MoveBack 2 ticks after the release); Between Worlds 600 ms = r_dur 36, on her toes, the leap (the dash from
# r_rel 14 = 233 ms; the leap from 200 ms), the landing crouch; Across the Veil 200 ms = the veil's 12-tick animation
#
# The in-betweens (2026-11-14: her attack, Twofold Hex and Between Worlds played 3 poses, The Weirding 2, the veil 1,
# the death 2 and a flash): each span above is shared out over more frames (inbetween.spans: whole ms, none under
# 50), so every action is as long as it was and its strike still begins on its millisecond - the point at 120, the
# sweep at 150 and the recall at 350, the hop back at 220, the leap at 200 and the landing at 450, the slump at 340.
# A frame that is only its neighbour moved whole is no new pose: one stays only where the move is the motion (a
# hop's rise, the leap, the fall), never more than two frames of one drawing in a row. The run is the four drawn
# steps as they were.
ATK, QD, ED, RD = (ms_of(KIT[k]) for k in ("atk_dur", "q_dur", "e_dur", "r_dur"))
MS = {"idle": [1000], "run": [150] * 4,
      "attack": IB.spans((120, 1), (ATK - 240, 3, (5, 9, 7)), (120, 1)),
      "skill": IB.spans((150, 2, (7, 8)), (200, 2, (6, 14)), (QD - 350, 1)),
      "skill2": IB.spans((220, 2, (7, 15)), (ED - 220, 3, (9, 10, 9))),
      "ult": IB.spans((200, 2), (250, 2, (9, 16)), (RD - 450, 2, (6, 9))),
      "veil": IB.spans((200, 3, (6, 8, 6))),
      "hit": [100, 100], "dead": IB.spans((340, 4, (7, 8, 9, 10)), (900, 2, (8, 82)))}


def actions(C):
    f = C.frame

    def under(**parts):
        return [(part, off, "under") for part, off in parts.items()]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's run_new_4: contact, passing, contact on the other leg, passing; the wand on her shoulder)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (League's attack6: the wand raised by her head, then pointed out - the bolt - and back): raised; the wand
    # shooting out through her fist, pointed, drawn back a hand; the idle
    out["attack"] = [f("a_wind"), f("a_point", dx=-1, moves=under(wand=(-14, 3))), f("a_point", dx=-1),
                     f("a_point", dx=-1, moves=under(wand=(-5, 1))), f("idle")]
    # Twofold Hex (Spell1: a small hop with the wand up, the sweep - the hex flies - and the recall, the wand held up):
    # the wand coming up (the attack's raise), the hop; the sweep with the wand still coming through her fist, swept;
    # the recall
    out["skill"] = [f("a_wind"), f("q_wind", lift=3),
                    f("q_cast", dx=1, moves=under(wand=(-14, -7))), f("q_cast", dx=1), f("q_catch")]
    # The Weirding (Spell3: the deep squat thrusting the wand - the blast - then the hop back): the wand half out,
    # thrust; hopping back - rising, at the top, curling up as she comes down (the veil's hop)
    out["skill2"] = [f("e_push", dx=1, moves=under(wand=(-10, -6))), f("e_push", dx=1),
                     f("e_hop", dx=-1, lift=4), f("e_hop", dx=-3, lift=8), f("w_hop", dx=-4, lift=6)]
    # Between Worlds (Spell4: up on her toes, the high leap - the dash - and the landing crouch with the wand down): up
    # on her toes with the wand still drawn in, reached; leaping - rising, at the top; landing with the wand not yet
    # down, the crouch
    out["ult"] = [f("r_reach", moves=under(wand=(-8, -9))), f("r_reach"),
                  f("r_leap", dx=1, lift=7), f("r_leap", dx=2, lift=14),
                  f("r_land", dx=2, lift=4, moves=under(wand=(-8, -8))), f("r_land", dx=2)]
    # Across the Veil (Spell2: curled up in the hop back): pushing off (The Weirding's hop), curled up at the top,
    # coming down
    out["veil"] = [f("e_hop", dx=-1, lift=3), f("w_hop", dx=-3, lift=8), f("w_hop", dx=-4, lift=5)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: reeling back, the arms flung out; sitting down, the wand dropped): struck, reeling back
    # with her free arm flung up and down again and the wand slipping out of her hand; dropping onto the ground where
    # the wand lies, still
    out["dead"] = [f("d_stagger", dx=-1, flash=True),
                   f("d_stagger", dx=-2, spins=[("arm", (20, 66), 16, "under")]),
                   f("d_stagger", dx=-2, spins=[("arm", (20, 54), -12, "under")], moves=[("wand", (5, 4), "over")]),
                   f("d_stagger", dx=-3, moves=[("wand", (11, 9), "over")]),
                   f("d_slump", dx=-2, lift=4, moves=[("wand", (0, 4), "under")]), f("d_slump", dx=-2)]
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
