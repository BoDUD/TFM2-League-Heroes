#!/usr/bin/env python3
"""league_ivern's action frames and Daisy's sheets: his approved 3/4 design and Codex's key poses after League's clips
(the user, 2026-10-22: 「动作帧让gpt做吧」, then 「你处理吧 完美了喊我review」).

    python tools/art/rig_ivern.py --review DIR      # every tag at 3x + a GIF per tag, Daisy's too (nothing written)
    python tools/art/rig_ivern.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet;
                                                    # Daisy's dense sheets -> league/effects/league_ivern_daisy_*

The pictures (tools/art/design_ivern_model.py, design_ivern_poses.py):
  hd/idle.png          him, 3/4 front facing right, 61 x 60 at PPU 1.5 (40 game px mushroom to soles): the idle, the hit;
  hd/pose_<name>.png   Codex's key poses read back at the design's size with the design's head put in
                       (assets/source/ivern/POSE_PROMPTS.md; the standing ones' legs drawn again short in LEGS_PROMPTS.md):
                       a_throw e_gather e_give q_wind q_fling r_crouch r_leap r_call run1-4 d_stagger d_slump (a_wind
                       not used: the twig in the far hand);
  hd/daisy.png         Daisy from the front, 95 x 76 at PPU 1.9 (40 game px sprout to feet, the user's pick: uncut);
  hd/daisy_<name>.png  her poses the same way: dz_rise dz_wind dz_punch dz_up dz_slam dz_wave.
Placing a pose (league_hwei's way): its head box (the design's head, pasted) stands where the design's head stands,
moved dx squares, its soles on the ground row (its lowest square) or `lift` rows over it. The idle is the design alone
(no breathing: hero_reels cuts his idle snippets from these actions).
Daisy is an effect picture riding on the champion she fights (tools/kit/build_ivern.py: views r_drop, r_punch, r_slam,
r_bye; league_annie's Tibbers way, z -1): each a dense sheet holding idle (1x) and hd_idle (PPU 1.9, league_main hd.rs
EFFECTS) - a dense effect sheet holds only those two (league_main src/lookup.rs densify_table). She stands BEHIND the
champion: her feet DAISY_BACK game px over its soles. Her punch and slam land on DAISY_MS's impact frames, which the
kit's r_hit_at / r_slam_at follow (a frame's start in ticks = ms x 0.06).
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
import inbetween as IB  # noqa: E402
import pixel_down as PD  # noqa: E402
import strips as G  # noqa: E402
import pack_ivern_poses as PK  # noqa: E402

HERO = "ivern"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "ivern", "hd")
MOD = os.path.join(ROOT, "league")
STAND = 34                     # the idle's standing column: under his middle, between his root feet
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's head box top-left (column, row) in hd/idle.png
D_PPU = 1.333                  # Daisy's sheets: 76 rows for 57 game px - league.dll drew her a square a game pixel (76 px)
                               # until its effect draw shrank her (hd.rs DRAWN_EFFECTS, 2026-10-27: 「大小按我看到的再缩一点」
                               # -> 75 % of 76); her 1x frames at this size too, or league.dll leaves her table alone
                               # (「我怎么在游戏里看不到了」); league_main hd.rs EFFECTS the same
D_HEAD = (27, 0)               # her head box top-left in hd/daisy.png (design_ivern_poses FIG["daisy"])
DAISY_BACK = 9                 # game px her feet stand behind (over) the champion's soles (league_annie's Tibbers: 9; the
                               # user tried her beside him on 2026-10-23 and kept her behind: 「还是放在后面吧」)
DAISY_SIDE = 0                 # game px from the champion's middle to hers (0: right behind him)
FEET = R.FEET


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name, prefix="pose_"):
    d = load(f"{prefix}{name}.png")
    with open(lp(os.path.join(SRC, f"{prefix}{name}.json")), encoding="utf-8") as f:
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
        self.rig = R.Rig(D, pad=(60, 60, 40, 12))      # room for the arms flung out, the twig raised, the leap
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground = self.d, HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name)
        return d, (rig.ox + HEAD[0] - hx + dx, rig.GY - ground - lift)

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), spins=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - a part of the pose (PARTS) moved by whole squares (the apple he drops);
        spins [(part, point, degrees, how)] - an arm turned clockwise by any angle about its shoulder. The head and
        everything of the pose in none of its parts are checked unchanged."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        if moves or spins:
            hx, hy = load_pose(name)[1]
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + HEAD_H, hx:hx + HEAD_W] = self.head()
            d = IB.vary(d, parts_of(name, d, head), self.outline, moves, (), None, head, VPAD, name, (), spins)
            left, top = left - VPAD, top - VPAD
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can

    def head(self):
        """The head's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.d, HEAD, (HEAD_W, HEAD_H), [load_pose(n)[:2] for n in VARIED])
        return self._head


# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): an arm held out clear of his horns, turned about
# its shoulder (inbetween.spin: the join hidden under his leaves), polygons in the pose picture's own squares less the
# head's squares; the apple he drops in the death (APPLE_AT: a square of it - the piece of the picture it is). The
# arms raised in front of his horns (Rootcaller's wind-up, the ult) are not turned: the horn under them is not drawn.
# His head (the mushroom, the horns, the face: pack_ivern_poses.HEAD) and the rest of him are in no part.
HEAD_W, HEAD_H = PK.HEAD[3] - PK.HEAD[2], PK.HEAD[1] - PK.HEAD[0]
VPAD = 30                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "a_throw": {"arm": [[(61, 23), (76, 23), (76, 17), (91, 17), (91, 38), (61, 38)]]},
    "q_fling": {"arm": [[(50, 24), (81, 24), (81, 45), (50, 45)]]},
    "e_give": {"arm": [[(64, 0), (78, 0), (78, 26), (58, 30), (53, 28), (54, 20), (63, 18)]]},
}
APPLE_AT = {"d_stagger": (87, 57)}
VARIED = ("a_throw", "q_fling", "e_give", "d_stagger")
# the point each arm turns about (square corners): the corner of its root on the side it turns away from
PIVOT = {("a_throw", "arm", "ccw"): (61, 34), ("a_throw", "arm", "cw"): (61, 22),
         ("q_fling", "arm", "ccw"): (50, 41), ("q_fling", "arm", "cw"): (50, 30),
         ("e_give", "arm", "cw"): (54, 21), ("e_give", "arm", "ccw"): (58, 29)}


def runs(m):
    """A mask as row runs (x0, y, x1, y) - boxes for inbetween.part_mask."""
    out = []
    for y in range(m.shape[0]):
        xs = np.nonzero(m[y])[0]
        if not len(xs):
            continue
        cut = np.nonzero(np.diff(xs) > 1)[0]
        out += [(int(a), y, int(b), y) for a, b in zip(np.r_[xs[0], xs[cut + 1]], np.r_[xs[cut], xs[-1]])]
    return out


def parts_of(name, d, head):
    """PARTS of a pose as masks less the head's squares, with the dropped apple (APPLE_AT) as the piece of the picture
    it is - as row runs for inbetween.vary."""
    out = {k: runs(IB.part_mask(d.shape, v) & ~head) for k, v in PARTS.get(name, {}).items()}
    if name in APPLE_AT:
        lab, _ = ndimage.label(d[..., 3] > 0, structure=np.ones((3, 3)))
        x, y = APPLE_AT[name]
        if not lab[y, x]:
            sys.exit(f"{name}: APPLE_AT is not on the apple")
        out["apple"] = runs(lab == lab[y, x])
    return out


# ms per frame; the kit's ticks (tools/kit/build_ivern.py) come from these (a frame's start in ticks = ms x 0.06):
# attack 440 ms = atk_dur 26, the seed thrown on the throw frame (a_rel 10 = 167 ms; the throw from 120 ms);
# Triggerseed 400 ms = e_dur 24, the seed given on the give frame (e_rel 9 = 150 ms; from 140 ms); Rootcaller 440 ms =
# q_dur 26, the vine on the fling (q_rel 10 = 167 ms; from 130 ms); Daisy! 570 ms = r_dur 34, the call on the leap
# (r_rel 14 = 233 ms; the leap from 120 ms)
#
# The in-betweens (2026-11-14: the attack, Triggerseed and Rootcaller each played their wind-up and the throw shown
# twice; the death 2 poses and a flash): each span above is shared out over more frames (inbetween.spans: whole ms,
# none under 50), so every action is as long as it was and its throw still begins on its millisecond (the throw at
# 120, the gift at 140, the fling at 130, the slump at 340). The ult, the run and the hit are as they were.
MS = {"idle": [1000], "run": [140] * 4, "attack": IB.spans((120, 1), (150, 2), (100, 1), (70, 1)),
      "skill": IB.spans((140, 1), (160, 2), (100, 1)), "skill2": IB.spans((130, 1), (170, 2), (140, 1)),
      "ult": [120, 130, 170, 150], "hit": [100, 100], "dead": IB.spans((340, 3), (900, 2, (8, 92)))}


def actions(C):
    f = C.frame

    def spin(name, degrees):
        """The pose's arm turned clockwise by `degrees` (negative: counter-clockwise) about its shoulder (PIVOT)."""
        return [("arm", PIVOT[(name, "arm", "cw" if degrees > 0 else "ccw")], degrees, "under")]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run_base: contact, passing, contact on the other leg, passing)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (League's Attack01: wound up - the twig arm raised, the apple hand drawn in - then the far hand thrown
    # forward - the seed - held, back). Codex's a_wind put the twig in the far hand: the twig would jump hands
    # (wound up; the throw with the far arm still high, thrown, following through; back)
    out["attack"] = [f("q_wind", dx=-1), f("a_throw", dx=1, spins=spin("a_throw", -25)), f("a_throw", dx=1),
                     f("a_throw", dx=1, spins=spin("a_throw", 12)), f("idle")]
    # Triggerseed (Spell3: crouched cupping the seed, then up tossing it to the ally)
    # (crouched; the arm coming up, the seed given, the hand on up)
    out["skill"] = [f("e_gather"), f("e_give", dx=1, spins=spin("e_give", 30)), f("e_give", dx=1),
                    f("e_give", dx=1, spins=spin("e_give", -10))]
    # Rootcaller (Spell1: coiled with the twig arm high, then the big step whipping it across - the vine)
    # (coiled; the twig coming across still high, whipped across, following through)
    out["skill2"] = [f("q_wind", dx=-1), f("q_fling", dx=2, spins=spin("q_fling", -30)), f("q_fling", dx=2),
                     f("q_fling", dx=2, spins=spin("q_fling", 12))]
    # Daisy! (Spell4: the crouch, the leap with the twig thrust up - the call - landing with it raised)
    out["ult"] = [f("r_crouch"), f("r_leap"), f("r_call"), f("r_call")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: the stagger, the apple dropped; slumped down sitting)
    # (struck; the apple still falling from his hand in two steps; dropping, slumped)
    out["dead"] = [f("d_stagger", dx=-1, flash=True), f("d_stagger", dx=-2, moves=[("apple", (-5, -12), "over")]),
                   f("d_stagger", dx=-2, moves=[("apple", (-2, -5), "over")]), f("d_slump", dx=-2, lift=3),
                   f("d_slump", dx=-2)]
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


# ------------------------------------------------------------------------------------------------------- Daisy
# her four sheets: [(pose, lift / sink rows (sink: under the ground, clipped), ms)]; the punch lands at 350 ms (the
# kit's r_hit_at 21), the slam at 400 ms (r_slam_at 24); each swing is one r_per (60 ticks = 1 s) so she never stands
# blank between them
DAISY_MS = {
    "drop": [("idle", -44, 90), ("idle", -24, 90), ("dz_rise", 6, 200), ("dz_rise", 2, 120), ("idle", 0, 400)],
    "punch": [("idle", 0, 150), ("dz_wind", 0, 200), ("dz_punch", 0, 200), ("dz_punch", 0, 150), ("idle", 0, 300)],
    "slam": [("idle", 0, 100), ("dz_up", 0, 300), ("dz_slam", 0, 250), ("dz_slam", 0, 150), ("idle", 0, 200)],
    "bye": [("dz_wave", 0, 300), ("dz_wave", -10, 150), ("idle", -34, 120), ("idle", -58, 130)],
}


class Daisy:
    """Her frames as dense canvases: the design (or a pose, its head box on the design's) standing on the canvas'
    ground row, DAISY_BACK game px over the champion's soles under the pivot; a negative lift sinks her under the ground
    (clipped there: rising out of it, sinking back)."""

    def __init__(self):
        self.d = load("daisy.png")
        h, w = self.d.shape[:2]
        # wide enough for her step aside (DAISY_SIDE) on either side of the pivot, so no column of her is cut off
        self.W, self.H = w + 120 + 2 * int(np.ceil(abs(DAISY_SIDE) * D_PPU)), h + 90
        self.px = self.W / 2.0
        self.soles = self.H - 20                          # the champion's soles' row
        self.py = self.soles - FEET * D_PPU               # the pivot (the champion) FEET game px over its soles
        self.ground = self.soles - int(round(DAISY_BACK * D_PPU))

    def frame(self, name, lift):
        can = np.zeros((self.H, self.W, 4), np.uint8)
        if name == "idle":
            d, (hx, hy), ground = self.d, D_HEAD, self.d.shape[0]
        else:
            d, (hx, hy), ground = load_pose(name, "daisy_")
        x0 = int(round(self.px - self.d.shape[1] / 2 + DAISY_SIDE * D_PPU)) + D_HEAD[0] - hx
        y0 = self.ground - ground - lift
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + y0, xs + x0
        ok = (ty >= 0) & (ty < self.ground if lift < 0 else ty < self.H) & (tx >= 0) & (tx < self.W)
        can[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]
        return can

    def tags(self):
        out = {}
        for sheet, seq in DAISY_MS.items():
            ones, hds = [], []
            for name, lift, ms in seq:
                can = self.frame(name, lift)
                ys, xs = np.nonzero(can[..., 3] > 0)
                hw = int(np.ceil(max(self.px - xs.min(), xs.max() + 1 - self.px) / D_PPU - 0.5))
                hh = int(np.ceil(max(self.py - ys.min(), ys.max() + 1 - self.py) / D_PPU - 0.5))
                hh = max(hh, int(np.ceil(FEET)) + 1)
                ones.append((R.one_of(can, self.px, self.py, hw, hh, D_PPU), ms))
                W, H = round((2 * hw + 1) * D_PPU), round((2 * hh + 1) * D_PPU)
                hds.append((R.crop_dense(can, self.px, self.py, W, H), ms))
            out[f"league_ivern_daisy_{sheet}"] = {"idle": ones, "hd_idle": hds}
        return out


def review_daisy(out_dir):
    """Daisy's four sheets at 3x as GIFs (her hd frames), on the arena colour with the champion's soles marked."""
    os.makedirs(out_dir, exist_ok=True)
    for sheet, tt in Daisy().tags().items():
        fr = tt["hd_idle"]
        H = max(c.shape[0] for c, _ in fr)
        W = max(c.shape[1] for c, _ in fr)
        ims = []
        for c, ms in fr:
            bg = Image.new("RGBA", (W, H), (104, 112, 72, 255))
            bg.alpha_composite(Image.fromarray(c), ((W - c.shape[1]) // 2, (H - c.shape[0]) // 2))
            ims.append(bg.convert("RGB").resize((W * 3, H * 3), Image.NEAREST))
        ims[0].save(os.path.join(out_dir, f"{sheet}.gif"), save_all=True, append_images=ims[1:],
                    duration=[int(ms) for _, ms in fr], loop=0)
        print(sheet, len(fr), "frames", sum(ms for _, ms in fr), "ms")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        review_daisy(os.path.join(a.review, "daisy"))
        return
    C.rig.export(acts)
    for sheet, tt in Daisy().tags().items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tt, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(v)}" for t, v in tt.items()))


if __name__ == "__main__":
    main()
