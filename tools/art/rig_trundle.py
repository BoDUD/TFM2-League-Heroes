#!/usr/bin/env python3
"""league_trundle's action frames: Trundle's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-25: 「都交给 Codex」, then 「Codex已经全部交付了 你做到完美后喊我review」).

    python tools/art/rig_trundle.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_trundle.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_trundle_model.py, design_trundle_poses.py):
  hd/idle.png         Trundle, 3/4 front facing right, hunched, 104 x 85 at PPU 2.0 (42.5 game px mane to feet): the
                      idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/trundle/POSE_PROMPTS.md): a_wind a_smash q_rear q_chomp w_crouch w_roar e_swing
                      e_raise r_rise r_reach run1-4 d_fall d_down.
Placing a pose (rig_yorick's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as League's head moves in that frame (the pose pack's skeleton: HEAD_DX, rounded) and dx squares more by hand;
its soles on the ground row (its lowest square: the feet, or the ice club's head when it hangs lower), or `lift` rows
over it. The idle is the design alone (no breathing: hero_reels cuts the idle snippets from these actions).
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
import inbetween as IB  # noqa: E402
import pixel_down as PD  # noqa: E402
import pack_trundle_poses as PK  # noqa: E402

HERO = "trundle"
PPU = 2.0
SRC = os.path.join(ROOT, "assets", "source", "trundle", "hd")
STAND = 58                     # the idle's standing column: under his belt's gem buckle, between his feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far League's head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}
LIFT = {"w_roar": 12}          # rows off the ground: the leap (the pack's 6 squares of 9 px, PPU 2 rows a game px)

# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): polygons in each pose picture's own squares.
# The ice club turns about his grip - a quarter turn is one of the grid's exact turns (the same club square for
# square); any other angle is turned RotSprite's way (inbetween.spin: only the club's own colours, its outline tidied
# after); an arm turns the same way about the corner where it leaves the shoulder guard or the body, so its root stays
# hidden under them; the club flung away in the death tumbles on by itself, and comes down under his hand a beat
# after he slumps (turned about its butt end); the two legs of a contact step turn about the hips toward each other
# (the run's half strides). The head and the rest of the body are in no part.
VPAD = 60                      # squares a moved part may leave its pose picture's box by (the club turned about his grip)
PARTS = {
    "a_wind": {"club": [[(0, 0), (58, 0), (63, 36), (63, 40), (62, 40), (62, 49), (48, 49), (40, 46), (0, 46)]]},
    "a_smash": {"club": [[(88, 58), (137, 58), (137, 96), (81, 96), (81, 77), (85, 77), (85, 70), (88, 66)]]},
    "q_rear": {"arm": [[(106, 44), (138, 44), (138, 76), (106, 76)]]},
    "w_roar": {"arm": [[(115, 0), (138, 0), (138, 36), (130, 38), (124, 44), (120, 48), (115, 48), (115, 46), (116, 46),
                        (116, 40), (117, 40), (117, 35), (116, 35), (116, 31), (115, 31)]],
               "club": [(0, 52, 43, 52), (0, 53, 47, 54), (0, 55, 46, 57), (0, 58, 49, 105)]},
    "q_chomp": {"club": [[(0, 22), (48, 22), (48, 30), (53, 30), (53, 36), (50, 36), (50, 49), (47, 50), (40, 56),
                          (30, 68), (20, 76), (0, 76)]]},
    "e_swing": {"club": [[(0, 12), (53, 12), (53, 26), (48, 34), (42, 60), (0, 60)]]},
    "e_raise": {"club": [[(12, 0), (70, 0), (70, 47), (30, 50), (24, 53), (20, 54), (17, 54), (17, 50), (12, 47)]],
                "butt": [(0, 56, 7, 66)]},
    "r_rise": {"arm": [[(107, 34), (118, 34), (118, 28), (138, 28), (138, 62), (108, 62), (107, 56)]]},
    "r_reach": {"arm": [[(104, 14), (138, 14), (138, 50), (104, 50)]]},
    "d_fall": {"club": [[(0, 0), (64, 0), (64, 54), (52, 54), (52, 50), (44, 46), (0, 46)]]},
    "d_down": {"club": [(0, 43, 35, 57), (0, 58, 37, 58), (0, 59, 38, 59), (0, 60, 39, 60), (0, 61, 41, 61),
                        (0, 62, 42, 62), (0, 63, 46, 63), (0, 64, 51, 64), (0, 65, 56, 65), (0, 66, 59, 66),
                        (0, 67, 61, 70), (0, 71, 58, 74)]},
    "run1": {"back": [[(60, 44), (92, 44), (100, 46), (113, 46), (113, 52), (104, 54), (104, 62), (96, 70), (86, 74),
                       (60, 74)]],
             "front": [[(128, 46), (140, 44), (152, 46), (153, 62), (170, 64), (170, 84), (128, 84), (124, 70),
                        (124, 58)]]},
    "run3": {"back": [[(44, 44), (66, 44), (72, 42), (80, 44), (84, 48), (84, 54), (80, 60), (76, 66), (60, 70),
                       (44, 70)]],
             "front": [[(96, 48), (104, 46), (118, 50), (120, 60), (132, 66), (132, 80), (98, 80), (94, 66),
                        (94, 56)]]},
}
# the point each pose's part turns about: the corner in his fist for a club; for an arm or a leg the corner where it
# leaves the body on the side it turns away from, so the rest of its root swings in under the body and no gap opens
AT = {("a_wind", "club"): (63, 44), ("a_smash", "club"): (85, 72), ("q_rear", "arm"): (106, 48),
      ("w_roar", "arm"): (114, 22), ("w_roar", "club"): (48, 54),
      ("q_chomp", "club"): (50, 26), ("e_swing", "club"): (54, 20), ("e_raise", "club"): (17, 52),
      ("r_rise", "arm"): (107, 56), ("r_reach", "arm"): (104, 27), ("d_fall", "club"): (30, 26),
      ("d_down", "club"): (60, 67),
      ("run1", "back"): (108, 48), ("run1", "front"): (130, 48), ("run3", "back"): (84, 48), ("run3", "front"): (97, 50)}


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
        self.rig = R.Rig(D, pad=(70, 70, 100, 14))     # room for the club swung overhead, out behind, flung away
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), HEAD_DX[name]
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.d, HEAD, (PK.HW, PK.HH), [load_pose(n)[:2] for n in PK.POSES])
        return self._head

    def frame(self, name, dx=0, lift=None, flash=False, moves=(), turns=(), spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - parts of the pose (PARTS) moved by whole squares, "under" the rest of him or
        "over" it; turns [(part, corner, quarters, how)] - a part turned by quarter turns about a square corner;
        spins [(part, point, degrees, how)] - a part turned clockwise by any angle about a point (RotSprite's way),
        then moved if `moves` names it too."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, LIFT.get(name, 0) if lift is None else lift)
        if moves or turns or spins:
            hx, hy = load_pose(name)[1]
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + PK.HH, hx:hx + PK.HW] = self.head()
            d = IB.vary(d, PARTS[name], self.outline, moves, (), None, head, VPAD, name, turns, spins)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_trundle.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the club landing on the smash frame (a_hit 11 = 183 ms); Chomp 467 ms = q_dur 28, the bite
# from 200 ms (q_hit 12); the Frozen Domain's hop (tag `w`) 233 ms = w_dur 14; Pillar of Ice 400 ms = e_dur 24, the club
# raised as the pillar rises on e_rel 10 (167 ms); Subjugate 500 ms = r_dur 30, the hand reaching out on r_rel 14 (233 ms)
#
# The in-betweens (2026-11-14: his attack and Chomp played 3 different poses, the hop, the Pillar and Subjugate 2, the
# death 2 and a flash, the run 4): each span above is shared out over more frames (inbetween.spans: whole ms, none
# under 50), so every action is as long as it was and its strike still begins on its millisecond - the smash at 183,
# the bite at 200, the leap at 100, the raise at 167, the reach at 233, the slump at 400; the run's four steps each
# keep their 150 ms, the second half of each a half stride. A frame that is only its neighbour moved whole is no new
# pose: one stays only where the move is the motion (the lunge of a strike, the knock-back, the fall), and never more
# than two frames of one drawing follow each other.
MS = {"idle": [1000], "run": IB.spans(*[(150, 2)] * 4),
      "attack": IB.spans((183, 3), (200, 3, (6, 7, 7)), (84, 1)),
      "skill": IB.spans((200, 3), (200, 2, (6, 14)), (67, 1)),
      "w": IB.spans((100, 1), (133, 2)),
      "skill2": IB.spans((167, 2), (233, 3)),
      "ult": IB.spans((233, 2), (267, 3, (6, 7, 14))),
      "hit": [100, 100], "dead": IB.spans((400, 4, (7, 8, 11, 14)), (900, 3, (7, 8, 75)))}


def actions(C):
    f = C.frame

    def spin(name, part, degrees, how="under"):
        """The pose's part turned clockwise by `degrees` about its point (AT)."""
        return [(part, AT[(name, part)], degrees, how)]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run: contact, passing, contact on the other leg, passing; the club trailing out behind him): the
    # four drawn steps, and between each two a half stride - the contact step next to it with its legs closing (after
    # a contact) or not yet open (before one), at a height between the two steps'
    def stride(name, k, lift):
        """A contact pose with both legs turned k degrees toward each other about the hips and drawn up under him as
        far as they would reach under the ground, the figure `lift` rows up: a half stride."""
        d, _, ground = load_pose(name)
        up = {}
        for part, sign in (("front", 1), ("back", -1)):
            layer = IB.spin(d, IB.part_mask(d.shape, PARTS[name][part]), AT[(name, part)], sign * k, C.outline, VPAD)
            low = int(np.nonzero((layer[..., 3] > 0).any(1))[0].max()) + 1 - VPAD
            up[part] = max(0, low - ground - lift)
        return f(name, lift=lift, spins=spin(name, "front", k) + spin(name, "back", -k),
                 moves=[("front", (0, -up["front"]), "under"), ("back", (0, -up["back"]), "under")])
    out["run"] = [f("run1"), stride("run1", 12, 1), f("run2"), stride("run3", 20, 4),
                  f("run3"), stride("run3", 12, 2), f("run4"), stride("run1", 20, 2)]
    # attack (Attack1: the club swung up over his head, smashed down before him, back): the club up behind him, turned
    # a quarter up over his head, coming down before him as he steps in; smashed down a step ahead, bounced, at rest;
    # the idle
    out["attack"] = [f("a_wind"), f("a_wind", dx=-1, turns=[("club", AT[("a_wind", "club")], 1, "under")]),
                     f("a_smash", dx=-1, spins=spin("a_smash", "club", -45)),
                     f("a_smash", dx=3), f("a_smash", dx=1, spins=spin("a_smash", "club", -15)), f("a_smash"),
                     f("idle")]
    # Chomp (Spell1 bite: rearing up, lunging in with the jaws, back): rising out of the hunch (the ult's first pose),
    # rearing with the arm still coming up, reared; lunging in a step long with the club thrown up behind him, bitten;
    # the idle
    out["skill"] = [f("r_rise"), f("q_rear", spins=spin("q_rear", "arm", 28)), f("q_rear"),
                    f("q_chomp", dx=4, spins=spin("q_chomp", "club", 14)), f("q_chomp"), f("idle")]
    # the Frozen Domain (Spell2 cast_hop, the passive's hop after a bite on a champion: crouched, leaping up roaring):
    # crouched; off the ground with his fist on its way up and the club still swinging down behind him; at the top of
    # the leap
    out["w"] = [f("w_crouch"),
                f("w_roar", lift=5, spins=spin("w_roar", "arm", 35) + spin("w_roar", "club", 22)), f("w_roar")]
    # Pillar of Ice (Spell3 cast_wave: the club swung across, raised high): the club on its way across, swung; his arm
    # up with the club a quarter turn behind, half way up, raised
    out["skill2"] = [f("e_swing", spins=spin("e_swing", "club", -32)), f("e_swing"),
                     f("e_raise", turns=[("club", AT[("e_raise", "club")], 3, "under")], moves=[("butt", (0, 0), "gone")]),
                     f("e_raise", spins=spin("e_raise", "club", -42), moves=[("butt", (0, 0), "gone")]), f("e_raise")]
    # Subjugate (Spell4: rising out of the hunch, reaching out to drain): rising, the hand coming up; the arm on its
    # way out in two steps, reached
    out["ult"] = [f("r_rise"), f("r_rise", spins=spin("r_rise", "arm", -24)),
                  f("r_reach", spins=spin("r_reach", "arm", 38)), f("r_reach", spins=spin("r_reach", "arm", 17)),
                  f("r_reach")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: knocked back, the club flung away; slumped on the ground): struck, flung back and up with the club
    # tumbling on away from him; dropping with the club's head still up, nearly down, still
    out["dead"] = [f("d_fall", flash=True),
                   f("d_fall", dx=-3, lift=3, spins=spin("d_fall", "club", -25, "over"), moves=[("club", (-4, -3), "over")]),
                   f("d_fall", dx=-5, lift=4, spins=spin("d_fall", "club", -55, "over"), moves=[("club", (-9, -5), "over")]),
                   f("d_fall", dx=-6, lift=1, turns=[("club", AT[("d_fall", "club")], 3, "over")], moves=[("club", (-13, -4), "over")]),
                   f("d_down", lift=4, spins=spin("d_down", "club", 18)),
                   f("d_down", lift=1, spins=spin("d_down", "club", 8)), f("d_down")]
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
