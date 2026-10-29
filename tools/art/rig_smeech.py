#!/usr/bin/env python3
"""tft_smeech's action frames: Smeech's approved design and Codex's key poses after his own TFT clips (the user,
2026-10-29: sprites by Codex from written prompts, then 「codex交付了 做到完美后喊我review」).

    python tools/art/rig_smeech.py --review DIR     # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_smeech.py                  # his frames at PPU -> assets/source/ppu/orig + the 1x sheet
                                                    # (tft/champions/tft_smeech), then ppu_restyle.py / ppu_hd.py

The pictures (tools/art/design_smeech_model.py, design_smeech_poses.py):
  hd/idle.png         Smeech in his ambush crouch, claws spread, 3/4 facing right, 128 x 87 at PPU 2.4 (36 game px,
                      the hat to the claws' tips): the idle and the hit;
  hd/pose_<name>.png  Codex's key poses with the design's head (assets/source/smeech/POSE_PROMPTS.md): a_rake a_back
                      a_wind2 a_thrust q_crouch q_air q_dive q_land e_wind e_rip d_fall d_down (its run1-8 are not used:
                      the walk below).
Placing a pose: Codex drew every pose on the pack's 9 px grid where its reference put it (tools/art/pack_smeech_poses.py:
the design pose's pelvis on one column, the lowest point on the ground line, the design itself from square DESIGN_AT),
so each pose goes across where Codex drew it (its grid_at, less the design's square). Up and down every standing pose
stands on its SOLES (the lowest row of his shoes' purples, SHOES), on the design's soles - the design's claws reach
6 rows lower than its shoes (the near claw in front), and Codex put each pose's lowest square, claw or shoe, on the
line - so a claw never pushes him up, and nothing goes lower than the design's claw tips (a_rake's raised back foot
would sink him); the leap's frames are lifted by LIFT, the falls lie on the ground (their lowest
square on the design's soles' row). The pivot (the line he stands on) is the middle of the design's stance (PIVOT).
The walk is the pack's approved walk on the idle (league_braum / league_galio: 「你按照泰坦布隆那种走路方式这种腿就不会变形」),
not Codex's run1-8: those eight drafts were drawn one by one, the body, the arms and the stilts a different size and
bend in every frame (the user, 2026-10-29: 「走路时身体和头有点不协调」, then 「还是变形吧 你能好好修吗」). So the design walks as it
stands - his ambush crouch creeping forward: the head, the coat, both claws as they are, and the design's own two stilt
legs (WALK_BACK, the image-left one, and WALK_FRONT, cut round the near arm's bracer and claw); in each frame a leg is
lifted and swung forward or slides back planted (WALK, whole squares: never turned, sheared or redrawn), the legs take
turns, the figure bobs a square or two; the slits a step opens take the outline. No height pop between the idle and the
walk either (Codex's run stood 127 rows tall on straight stilts, the crouch 87).
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

HERO = "smeech"
PPU = 2.4
SRC = os.path.join(ROOT, "assets", "source", "smeech", "hd")
DESIGN_AT = (5, 44)           # the design's top-left square on the pose pack's 9 px grid (pack_smeech_poses: 0_design.png)
PIVOT = 56                    # the design's column between his shoes (rows 76-80: 9-19 and 86-102)
SHOES = ((82, 43, 107), (54, 28, 71))     # his shoes' purples (the coat wears them higher up)
POSES = ("a_rake", "a_back", "a_wind2", "a_thrust", "q_crouch", "q_air", "q_dive", "q_land", "e_wind", "e_rip",
         "d_fall", "d_down")
FALLS = ("d_fall", "d_down")
LIFT = {"q_air": 14, "q_dive": 8}         # rows his soles leave the ground in the leap
RUN_MS = 125                              # his TFT walk: 1000 ms the cycle, 8 frames
# the design's two stilt legs: where to look for each (design rows r0-r1, columns c0-c1, ends exclusive; read at 18-22x,
# 2026-10-29) - the back (image-left) leg from the knob under the shorts down to its shoe, clear of the far claw's
# finger tips (rows <= 60, columns <= 30) and the coat's tail (columns >= 48); the front leg from under the shorts down
# to its shoe, below the near arm's bracer (columns >= 89 down to row 69). In those boxes a leg is its coloured squares
# joined to its shoe (a claw's tip inside a box is not) and the outline squares that border only it: an outline square
# it shares with the bracer, a claw or the shorts stays with the body (leg_mask)
WALK_BACK = ((53, 59, 36, 46), (59, 82, 31, 48), (61, 82, 8, 31))
WALK_FRONT = ((60, 62, 79, 89), (62, 82, 76, 89), (67, 70, 89, 92), (70, 82, 89, 102))
# per frame: the back leg's (squares forward, squares lifted), the front leg's, the figure's rise. A leg swings forward
# lifted (3 / 5 / 3 squares) for three frames and lands, then slides back planted for four as he moves on; the front leg
# four frames after the back one. Each leg moves only on the side its top hides under the shorts - the back leg from
# its design place up to 5 squares forward, the front leg up to 5 back - so no slit opens at a hip. Strides of 5 squares
# (2 game px at PPU 2.4), league_braum's and league_galio's walk scale (league_nautilus's 1x steps x PPU)
WALK_BACK_LEG = [(1, 3), (3, 5), (5, 3), (5, 0), (4, 0), (2, 0), (1, 0), (0, 0)]
WALK_FRONT_LEG = [(dx - 5, lift) for dx, lift in WALK_BACK_LEG]
WALK = [(WALK_BACK_LEG[i], WALK_FRONT_LEG[(i + 4) % 8], (1, 2, 1, 0, 1, 2, 1, 0)[i]) for i in range(8)]
CRACK = 2                                 # enclosed bare squares a step leaves between a leg and the body, at most


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def meta(name):
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        return json.load(f)


def soles(d):
    """The row under his shoes: the lowest row with a shoe purple, plus its outline."""
    m = np.zeros(d.shape[:2], bool)
    for c in SHOES:
        m |= np.all(d[..., :3] == c, axis=-1) & (d[..., 3] > 0)
    return int(np.nonzero(m.any(1))[0].max()) + 2


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d
        self.sole = soles(d)
        lefts, rights, tops, bottoms = [-4], [d.shape[1] + 4], [-8], [d.shape[0]]
        for n in POSES:
            p, (left, top) = self.place(n)
            lefts.append(left)
            rights.append(left + p.shape[1])
            tops.append(top)
            bottoms.append(top + p.shape[0])
        pad = (max(4, -min(lefts) + 4), max(4, max(rights) - d.shape[1] + 4), max(4, -min(tops) + 4),
               max(8, max(bottoms) - d.shape[0] + 8))

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], PIVOT, self.sole
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=pad)
        self.outline = D.outline

    def place(self, name):
        """(picture, its top-left relative to the design's): across where Codex drew it, its soles on the design's (a
        fall: its lowest square there) less its lift."""
        p = load(f"pose_{name}.png")
        left = round(meta(name)["grid_at"][0] - DESIGN_AT[0])
        foot = p.shape[0] if name in FALLS else soles(p)
        top = self.sole - foot - LIFT.get(name, 0)
        # nothing lower than the design's claw tips: a_rake lunges on a raised back foot, its soles would sink him
        return p, (left, min(top, self.d.shape[0] - p.shape[0]))

    def frame(self, name, dx=0, flash=False):
        """A pose on the canvas; flash = the hit's whitening."""
        rig = self.rig
        can = rig.canvas()
        if name == "idle":
            d, (left, top) = self.d, (dx, 0)
        else:
            d, (left, top) = self.place(name)
            left += dx
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top + rig.oy, xs + left + rig.ox
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can

    def leg_mask(self, idle, boxes):
        """(the leg's squares, its coloured squares) on the idle canvas: in `boxes`, the coloured (not outline)
        squares joined to the shoe's purples, and the outline squares that touch them and no other coloured square."""
        rig = self.rig
        H, W = idle.shape[:2]
        box = np.zeros((H, W), bool)
        for r0, r1, c0, c1 in boxes:
            box[rig.oy + r0:rig.oy + r1, rig.ox + c0:rig.ox + c1] = True
        op = idle[..., 3] > 0
        ink = op & np.all(idle[..., :3] == self.outline[:3], axis=-1)
        colour = op & ~ink
        lb, n = ndimage.label(colour & box, np.ones((3, 3)))
        shoe = np.zeros((H, W), bool)
        for c in SHOES:
            shoe |= np.all(idle[..., :3] == c, axis=-1)
        core = np.isin(lb, [k for k in range(1, n + 1) if ((lb == k) & shoe).any()])
        touch = lambda m: ndimage.binary_dilation(m, np.ones((3, 3)))
        rim = ink & box & touch(core) & ~touch(colour & ~core)
        return core | rim, core

    def walk(self, back_step, front_step, rise):
        """The idle canvas with the legs stepping: each leg's squares moved (dx, -lift), the back leg first, the front
        one over it, the body over both; then the outline closed round the moved legs (a square of background touching
        a leg's coloured square across or up and down takes the outline) and the few enclosed bare squares a step
        leaves between a leg and the body filled with it; the whole frame `rise` rows up."""
        idle = self.frame("idle")
        legs = [(self.leg_mask(idle, WALK_BACK), back_step), (self.leg_mask(idle, WALK_FRONT), front_step)]
        body = idle.copy()
        for (m, _), _ in legs:
            body[m] = 0
        out = np.zeros_like(idle)
        moved = np.zeros(idle.shape[:2], bool)
        for (m, core), (dx, lift) in legs:
            ys, xs = np.nonzero(m)
            out[ys - lift, xs + dx] = idle[ys, xs]
            cy, cx = np.nonzero(core)
            moved[cy - lift, cx + dx] = True
        mb = body[..., 3] > 0
        out[mb] = body[mb]
        moved &= ~mb
        ink = (*[int(v) for v in self.outline[:3]], 255)
        bare = out[..., 3] == 0
        cross = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
        out[bare & ndimage.binary_dilation(moved, cross)] = ink
        own = ndimage.binary_fill_holes(idle[..., 3] > 0) & ~(idle[..., 3] > 0)
        wop = out[..., 3] > 0
        lab, n = ndimage.label(ndimage.binary_fill_holes(wop) & ~wop & ~own)
        for k in range(1, n + 1):
            if (lab == k).sum() <= CRACK:
                out[lab == k] = ink
        return np.roll(out, -rise, axis=0)


# ms per frame; the kit's ticks (tools/kit/build_smeech.py) match these (a frame's start in ticks = ms x 0.06):
# attack / attack2 367 ms = atk_dur 22, the rake lands on atk_st 10 (167 ms: inside a_rake / a_thrust, from 100 ms);
# the leap 233 ms = q_jump 14 (gathered, up, diving; tft.dll lands him on tick 13), then `stabs` 667 ms (q_dur - q_jump
# 40 ticks): landed, then the three slashes on q_s1 / q_s2 / q_s3 (8 / 16 / 24 ticks = 133 / 267 / 400 ms after the
# landing: each on a thrust or a rake's first frame); Scrap Rip 400 ms = e_dur 24, the rip on e_st 10 (167 ms: e_rip's
# first frame); Scrap Frenzy 1200 ms = r_dur 72, a hop every r_gap 12 ticks from r_st 6 (100, 300 ... 900 ms: each a
# dive's first frame, then a rake and a thrust), landed at the end
HOP = [("q_dive", 67), ("a_rake", 67), ("a_thrust", 66)]
MS = {"idle": [1000], "run": [RUN_MS] * len(WALK), "attack": [100, 150, 117], "attack2": [100, 150, 117],
      "leap": [83, 83, 67], "skill": [83, 83, 67], "stabs": [133, 133, 134, 133, 134], "skill2": [167, 233],
      "ult": [100] + [ms for _ in range(5) for _, ms in HOP] + [100], "hit": [100, 100], "dead": [140, 260, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    out["run"] = [C.walk(b, fr, r) for b, fr, r in WALK]
    # the near claw's rake (gathered, raked out, pulled in) and the far claw's thrust (drawn back, driven out)
    out["attack"] = [f("a_back"), f("a_rake"), f("a_back")]
    out["attack2"] = [f("a_wind2"), f("a_thrust"), f("a_back")]
    # Scrap Hacker: gathered low, up with the claws high, diving; landed, then thrust / rake / thrust
    out["leap"] = [f("q_crouch"), f("q_air"), f("q_dive")]
    out["skill"] = out["leap"]          # the skill action's own tag (its CasterAnimations play leap, then stabs)
    out["stabs"] = [f("q_land"), f("a_thrust"), f("a_rake"), f("a_thrust"), f("a_back")]
    # Scrap Rip (claws thrown wide, torn apart)
    out["skill2"] = [f("e_wind"), f("e_rip")]
    # Scrap Frenzy (gathered, five dives each with a rake and a thrust, landed)
    out["ult"] = [f("q_crouch")] + [f(n) for _ in range(5) for n, _ in HOP] + [f("q_land")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (stiff, falling back, the hat off; down on his back)
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
