#!/usr/bin/env python3
"""league_yorick's action frames: Yorick's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-25: 「动作帧用 Codex 骨架姿势包」, then 「codex全部交付了 你做到完美后喊我review」).

    python tools/art/rig_yorick.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_yorick.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_yorick_model.py, design_yorick_poses.py):
  hd/idle.png         Yorick, 3/4 front facing right, 74 x 83 at PPU 1.75 (48 game px shovel tip to boots): the idle, the
                      hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/yorick/POSE_PROMPTS.md): a_wind a_smash q_raise q_slam w_raise w_slam k_call e_wind
                      e_throw r_raise r_plant run1-4 d_drop d_float.
Placing a pose (league_illaoi's way): its head box (the design's head, pasted) stands where the design's head stands,
moved as far as League's head moves in that frame (the pose pack's skeleton: HEAD_DX, rounded) and dx squares more by
hand; its soles on the ground row (its lowest square: the boots, or the dropped shovel under the floating body), or
`lift` rows over it. The idle is the design alone (no breathing: hero_reels cuts the idle snippets from these actions).
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
import pack_yorick_poses as PK  # noqa: E402

HERO = "yorick"
PPU = 1.75
SRC = os.path.join(ROOT, "assets", "source", "yorick", "hd")
STAND = 42                     # the idle's standing column: under his belt buckle, between his boots
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
# how far League's head moves across in each pose (the pose pack's skeleton head against the design's own)
HEAD_DX = {n: int(round(PK.build(spec)["head"][0] - PK.REST["head"][0])) for n, (_, _, _, spec) in PK.POSES.items()}


# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): boxes and polygons in each pose picture's own
# squares. He grips the shovel with both hands across his body, so what turns is its free end past the nearer fist
# (inbetween.spin about that fist: the blade swung further back, bounced off the ground - the fist hides the bend);
# where the shaft stands upright through a fist, the end on the blade's side slides along itself toward the fist
# (driven down, planted); a forearm turns about the elbow; the shovel he lets go of in the death falls over about its
# blade, and his body floats up from it. The head and the rest of the body are in no part.
VPAD = 56                      # squares a moved part may leave its pose picture's box by (the shovel falling over)
PARTS = {
    "a_wind": {"blade": [(0, 0, 45, 38)]},
    "a_smash": {"blade": [(72, 51, 76, 51), (71, 52, 76, 52), (71, 53, 79, 53), (73, 54, 82, 54), (74, 55, 113, 57),
                          (73, 58, 113, 58), (74, 59, 113, 59), (76, 60, 113, 60), (78, 61, 113, 61),
                          (79, 62, 113, 62), (81, 63, 113, 72), (86, 49, 113, 54)]},
    "q_slam": {"blade": [(86, 54, 106, 58), (82, 59, 106, 60), (81, 61, 106, 64), (77, 65, 106, 75)]},
    "w_raise": {"top": [(28, 0, 52, 39)]},
    "w_slam": {"blade": [(49, 55, 53, 58), (47, 59, 54, 62), (47, 63, 56, 63), (48, 64, 54, 64), (43, 65, 58, 65),
                         (42, 66, 59, 66), (42, 67, 60, 67), (42, 68, 58, 74), (43, 75, 57, 76), (42, 77, 58, 77),
                         (44, 78, 56, 79), (45, 80, 56, 81), (45, 82, 55, 83), (48, 84, 54, 87)]},
    "k_call": {"arm": [(76, 0, 95, 26), (83, 27, 95, 29)]},
    "e_throw": {"arm": [(85, 44, 108, 56), (98, 37, 108, 43), (90, 43, 97, 43)]},
    "r_raise": {"blade": [(0, 0, 35, 27)]},
    "r_plant": {"blade": [(70, 48, 73, 64), (67, 65, 74, 69), (60, 70, 80, 95)]},
    "d_drop": {"shovel": [[(20, 0), (44, 0), (44, 24), (32, 24), (30, 30), (27, 36), (27, 40), (26, 46), (26, 52),
                           (0, 52), (0, 44), (12, 44), (18, 30)], (0, 52, 27, 84)]},
    "d_float": {"shovel": [(0, 79, 78, 95)]},
}
# the point each pose's part turns about: the fist the shovel's free end passes, an elbow, the fallen shovel's blade
AT = {("a_wind", "blade"): (50, 39), ("a_smash", "blade"): (71, 51), ("q_slam", "blade"): (82, 60),
      ("r_raise", "blade"): (41, 22), ("k_call", "arm"): (84, 29), ("e_throw", "arm"): (85, 45),
      ("d_drop", "shovel"): (12, 80)}


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
        self.rig = R.Rig(D, pad=(80, 80, 50, 12))      # room for the shovel swung out behind, raised, lying
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

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - parts of the pose (PARTS) moved by whole squares, "under" the rest of him or
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


# ms per frame; the kit's ticks (tools/kit/build_yorick.py) match these (a frame's start in ticks = ms x 0.06):
# attack 500 ms = atk_dur 30, the spade landing on the smash frame (a_hit 12 = 200 ms); Q 500 ms = q_dur 30, the heavy
# slam from 220 ms (q_hit 14 = 233 ms); the Awakening (Q with full graves, tag `awaken`) 500 ms: raised, driven down at
# 200 ms (the walkers and the wall at q_hit), the call; E 433 ms = e_dur 26, the mist thrown on e_rel 12 (200 ms); R
# 567 ms = r_dur 34, the shovel raised, planted as the Maiden rises on r_rel 16 (267 ms)
#
# The in-betweens (2026-11-14: his attack, Last Rites and the Awakening played 3 poses, Mourning Mist and the Eulogy 2,
# the death 2 and a flash): each span above is shared out over more frames (inbetween.spans: whole ms, none under
# 50), so every action is as long as it was and its strike still begins on its millisecond - the smash at 200, the
# slam at 220, the Awakening's drive at 200 and its call at 350, the throw at 200, the planting at 267, the float at
# 400. A frame that is only its neighbour moved whole is no new pose: one stays only where the move is the motion
# (the lunge of a strike), never more than two frames of one drawing in a row. The run is the four drawn steps as
# they were (his legs are under the robe).
MS = {"idle": [1000], "run": [150] * 4,
      "attack": IB.spans((200, 3), (200, 3, (6, 7, 7)), (100, 1)),
      "skill": IB.spans((220, 2), (220, 3, (7, 7, 8)), (60, 1)),
      "awaken": IB.spans((200, 2), (150, 2), (150, 2)),
      "skill2": IB.spans((200, 1), (233, 3, (7, 7, 9))),
      "ult": IB.spans((267, 2), (300, 3, (8, 8, 14))),
      "hit": [100, 100], "dead": IB.spans((400, 4, (7, 8, 11, 14)), (900, 3, (7, 8, 75)))}


def actions(C):
    f = C.frame

    def spin(name, part, degrees, how="under"):
        """The pose's part turned clockwise by `degrees` about its point (AT)."""
        return [(part, AT[(name, part)], degrees, how)]

    def under(**parts):
        return [(part, off, "under") for part, off in parts.items()]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run: contact, passing, contact on the other leg, passing; the shovel carried slanted at his side)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (Attack1: the shovel swung back behind him, smashed down before him, back): the blade swung further back,
    # back, starting over; smashed down a step ahead, the blade bounced off the ground, at rest; the idle
    out["attack"] = [f("a_wind", spins=spin("a_wind", "blade", -10)), f("a_wind"),
                     f("a_wind", dx=1, spins=spin("a_wind", "blade", 14)),
                     f("a_smash", dx=3), f("a_smash", dx=1, spins=spin("a_smash", "blade", -9)), f("a_smash"),
                     f("idle")]
    # Last Rites (Spell1: lifted high, slammed into the ground): the shovel coming up over his head (the Eulogy's
    # raise), level over his head; slammed a step ahead, the blade bounced, at rest; the idle
    out["skill"] = [f("r_raise"), f("q_raise"),
                    f("q_slam", dx=3), f("q_slam", dx=1, spins=spin("q_slam", "blade", -9)), f("q_slam"), f("idle")]
    # the Awakening (Spell2 + Spell1_Cast: the shovel raised upright, driven down - the spirit wall - the dead called
    # up): the shovel still coming up through his fists, upright; its blade a hand above the ground, driven in; his
    # arm coming up, the call
    out["awaken"] = [f("w_raise", moves=under(top=(0, 8))), f("w_raise"),
                     f("w_slam", moves=under(blade=(0, -8))), f("w_slam"),
                     f("k_call", spins=spin("k_call", "arm", 28)), f("k_call")]
    # Mourning Mist (Spell3: wound up, thrown): wound up; his arm coming round in two steps, thrown
    out["skill2"] = [f("e_wind"), f("e_throw", spins=spin("e_throw", "arm", 36)),
                     f("e_throw", spins=spin("e_throw", "arm", 15)), f("e_throw")]
    # Eulogy of the Isles (Spell4: the shovel raised to the sky, planted): the blade still coming up, raised; the
    # shovel coming down through his fist, nearly in, planted
    out["ult"] = [f("r_raise", lift=1, spins=spin("r_raise", "blade", -14)), f("r_raise", lift=3),
                  f("r_plant", moves=under(blade=(0, -9))), f("r_plant", moves=under(blade=(0, -3))), f("r_plant")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: he collapses, the shovel falling; his body floats up over it): struck, the shovel he let go of
    # falling over in three steps; his body rising off the ground over the fallen shovel in two steps, floating
    out["dead"] = [f("d_drop", flash=True), f("d_drop", spins=spin("d_drop", "shovel", -18, "over")),
                   f("d_drop", spins=spin("d_drop", "shovel", -36, "over")),
                   f("d_drop", spins=spin("d_drop", "shovel", -54, "over")),
                   f("d_float", lift=-8, moves=[("shovel", (0, -8), "under")]),
                   f("d_float", lift=-3, moves=[("shovel", (0, -3), "under")]), f("d_float")]
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
