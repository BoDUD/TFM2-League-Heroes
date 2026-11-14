#!/usr/bin/env python3
"""league_azir's action frames and his summons' sheets: his approved 3/4 design and Codex's key poses after League's clips
(the user, 2026-10-23: 「Codex 照骨架画姿势」, then 「动作帧交付了 做到完美后喊我review」「有问题的地方你直接修复」).

    python tools/art/rig_azir.py --review DIR      # every tag at 3x + a GIF per tag, the summons' too (nothing written)
    python tools/art/rig_azir.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet; the
                                                   # summons' dense sheets -> league/effects/league_azir_soldier,
                                                   # league_azir_guard, league_azir_disc, league_azir_soldier_side
    python tools/art/rig_azir.py --summons         # the summons' sheets only (his frames untouched)

The pictures (tools/art/design_azir_model.py, design_azir_poses.py, design_azir_summons.py):
  hd/idle.png             him, 3/4 front facing right, 50 x 73 at PPU 1.5 (38 game px crest to soles, the sceptre above):
                          the idle, the hit;
  hd/pose_<name>.png      Codex's key poses read back at the design's size (the bodies at their skeletons' heights) with
                          the design's helmet put in (assets/source/azir/POSE_PROMPTS.md): c_wind c_point q_wind q_thrust
                          e_dash e_land r_raise r_lift r_sweep run1-4 d_stagger d_kneel;
  hd/soldier.png, soldier_lift.png, soldier_stab.png   the sand soldier from the front (29 x 54, 24 x 45, 31 x 44);
  hd/guard.png, guard_push1.png, guard_push2.png       the Imperial Guard from the side facing right (36 x 45, 38 x 45);
  hd/soldier_side_<pose>.png  the sand soldier from the side, spear to the right (design_azir_side_soldier.py: stand, wind,
                          thrust, hold, recover; hd/soldier_side.json their roots) - the add-on's soldiers;
  hd/disc.png             the Sun Disc from the front (46 x 68).
Placing a pose (league_aurora's way): its head box (the design's helmet, pasted) stands where the design's helmet stands,
moved dx squares, its soles on the ground row (its lowest square, or GROUND's row where the sceptre lies lower in front
of him) or `lift` rows over it. The idle is the design alone (no breathing: hero_reels cuts his idle snippets from these
actions).
The summons are effect pictures (tools/kit/build_azir.py's views; league_illaoi's tentacle): each a dense sheet holding
1x tags and their hd_ twins (PPU 1.5, league_main hd.rs EFFECTS), drawn as stored on both sides (the client never
mirrors an effect): the soldier from the front, the disc from the front, the guard from the side in a right-facing and a
mirrored left-facing tag (the add-on picks one by the wall's direction; the main pack's data cannot see it and draws the
right-facing one) - three guards a stamp (charge_<r|l>_<a|b>, the main pack's hops) and one guard alone (one_<r|l>_<a|b>:
league_azir 0.2.4 lines them up across the charge itself, the user 2026-11-11: 「沙皇R的大招推起来像是有三排士兵」), and the soldier from the side (league_azir_soldier_side: stand, rise and stab, each right and left,
ss_stand / ss_rise / ss_stab ticks long - the add-on stamps them where the data's soldier stands, facing the nearest
enemy, the stab when it strikes).
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
import strips as G  # noqa: E402
import pack_azir_poses as PK  # noqa: E402
from build_azir import P as KIT  # noqa: E402

HERO = "azir"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "azir", "hd")
MOD = os.path.join(ROOT, "league")
STAND = 32                     # the idle's standing column: under his middle, between his boots
HEAD = (PK.HEAD[2], PK.HEAD[0])            # the design's helmet box top-left (column, row) in hd/idle.png
GROUND = {"r_sweep": 55, "d_kneel": 51}    # the soles' / knees' row where the sceptre lies lower, in front of him
S_PPU = 1.5                    # the summons' sheets (the user's picks: soldier 36, guard 32, disc 48 game px, as drawn)
# the sand soldiers (front and the add-on's side view) shown at 70 % (the user, 2026-10-25: 「沙皇的沙兵游戏里这么大？得缩小
# 一点吧」 - drawn 36 game px against Azir's 30 crest to soles at his SIZES 0.80): the same pixels at a denser 1.5 / 0.7, so
# league.dll draws them smaller (hd.rs rows), their feet laid FEET game px under the pivot at that density
SOLDIER_PPU = 1.429            # 2026-10-27: 70 % of the 54 game px league.dll drew them at (a square a pixel) until its
                               # effect draw shrank them (hd.rs DRAWN_EFFECTS); their 1x frames at this size too
FEET = R.FEET

# The parts of the key poses that move on their own in the in-between frames (tools/art/inbetween.py; the user,
# 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」): polygons / boxes in each pose picture's own
# squares. An arm held out or the sceptre thrust out slides along itself back under the shoulder guard / the fist, so
# it is seen shorter - reaching out, drawing back; the sashes trailing behind him wave by their columns; the sceptre
# dropped before him in the death falls there. The helmet and the body are in no part: every frame checks them.
VPAD = 30                      # squares a moved part may leave its pose picture's box by
PARTS = {
    "c_wind": {"arm": [[(43, 17), (58, 17), (58, 50), (45, 50), (45, 31), (43, 31)]]},
    "c_point": {"arm": [[(56, 38), (81, 38), (81, 50), (56, 50)]]},
    "q_wind": {"spear": [[(0, 0), (24, 0), (24, 26), (21, 34), (22, 38), (18, 38), (14, 30), (0, 26)]]},
    "q_thrust": {"spear": [[(58, 14), (99, 14), (99, 37), (58, 37)]]},
    "e_dash": {"sash": [[(3, 10), (19, 10), (19, 29), (3, 29)]]},
    "e_land": {"sash": [[(18, 44), (33, 44), (33, 50), (27, 56), (22, 62), (14, 70), (3, 70), (3, 53), (18, 53)]]},
    "r_raise": {"arm": [[(50, 40), (73, 40), (73, 54), (50, 54)]]},
    "r_lift": {"spear": [[(2, 0), (21, 0), (21, 29), (18, 29), (18, 37), (9, 37), (2, 30)]]},
    "r_sweep": {"spear": [[(53, 44), (75, 44), (75, 67), (53, 67)]],
                "sash": [[(3, 30), (16, 30), (16, 45), (3, 45)]]},
    "run1": {"sash": [[(0, 44), (19, 44), (19, 61), (0, 61)]]},
    "run2": {"sash": [[(0, 48), (13, 48), (13, 64), (0, 64)]]},
    "run3": {"sash": [[(0, 44), (19, 44), (19, 61), (0, 61)]]},
    "run4": {"sash": [[(0, 48), (13, 48), (13, 64), (0, 64)]]},
    "d_stagger": {"sash": [[(12, 50), (29, 50), (29, 66), (12, 66)]],
                  "arm": [[(62, 36), (81, 36), (81, 51), (62, 51)]]},
    "d_kneel": {"spear": [(0, 52, 82, 61), (67, 47, 82, 51)],
                "sash": [[(10, 38), (30, 38), (30, 52), (10, 52)]]},
}
# where each pose's sashes are tied on: the column their wave starts from (nothing moves there; the tips the most)
SASH = {"e_dash": 18, "e_land": 30, "r_sweep": 15, "run1": 18, "run2": 12, "run3": 18, "run4": 12, "d_stagger": 28,
        "d_kneel": 29}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, name))).convert("RGBA")).copy()


def load_pose(name):
    d = load(f"pose_{name}.png")
    with open(lp(os.path.join(SRC, f"pose_{name}.json")), encoding="utf-8") as f:
        meta = json.load(f)
    ys = np.nonzero((d[..., 3] > 0).any(1))[0]
    return d, tuple(meta["head_at"]), int(GROUND.get(name, meta.get("ground", ys.max() + 1)))


class Canvas:
    def __init__(self):
        self.d = load("idle.png")
        d = self.d

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(50, 100, 50, 24))      # room for the sceptre thrust out, the dash, the sweep in front
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
        """The helmet's squares in the head box: what every key pose holds of the design's there."""
        if getattr(self, "_head", None) is None:
            self._head = IB.shared_head(self.d, HEAD, (PK.HW, PK.HH), [load_pose(n)[:2] for n in PARTS])
        return self._head

    def frame(self, name, dx=0, lift=0, flash=False, moves=(), sway=()):
        """A pose placed (see placed). The in-betweens (tools/art/inbetween.py vary), the pose placed as it is whole:
        moves [(part, (dx, dy), how)] - parts of the pose (PARTS) moved by whole squares, "under" the rest of him or
        "over" it; sway [(part, x0, x1, k, attach)] - a part's columns lifted 0..k rows along its length."""
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
        if moves or sway:
            hx, hy = load_pose(name)[1]
            head = np.zeros(d.shape[:2], bool)
            head[hy:hy + PK.HH, hx:hx + PK.HW] = self.head()
            d = IB.vary(d, PARTS[name], self.outline, moves, sway, None, head, VPAD, name)
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


# ms per frame; the kit's ticks (tools/kit/build_azir.py) match these (a frame's start in ticks = ms x 0.06):
# attack 450 ms = atk_dur 27: the claws raised, then the command - the soldiers stab at a_rel 10 = 167 ms (the point from
# 120 ms) - and back; Conquering Sands 400 ms = q_dur 24: the sceptre cocked, then thrust out - the sand rush leaves at
# q_rel 8 = 133 ms (the thrust from 120 ms); Shifting Sands 400 ms = e_dur 24: the dash (it starts at e_go_at 6 = 100 ms
# and lasts up to 11 ticks) then the landing; Emperor's Divide 600 ms = r_dur 36: the arm spread (the rush behind the
# champion at r_rush_at 6 = 100 ms), the sceptre lifted, then swept down - the wall charges at r_at 16 = 267 ms (the
# sweep from 270 ms)
#
# The in-betweens (2026-11-14: his attack played 3 different pictures, Q and E 2, R 3, the run 4, the death 3): each
# span above is shared out over more frames (inbetween.spans: whole ms, none under 50), so every action is as long as
# it was and its strike still begins on its millisecond - the point at 120, the thrust at 120, the landing at 260, the
# lift at 100 and the sweep at 270, the kneel at 340.
A, Q, E, R_ = ms_of(KIT["atk_dur"]), ms_of(KIT["q_dur"]), ms_of(KIT["e_dur"]), ms_of(KIT["r_dur"])
MS = {"idle": [1000], "run": IB.spans(*[(150, 2)] * 4),
      "attack": IB.spans((120, 2), (A - 240, 3, (5, 8, 8)), (120, 2)),
      "skill": IB.spans((120, 2), (Q - 120, 4, (5, 7, 7, 9))),
      "skill2": IB.spans((260, 4, (5, 7, 7, 7)), (E - 260, 2, (6, 8))),
      "ult": IB.spans((100, 2), (170, 3, (5, 6, 6)), (R_ - 270, 4, (6, 8, 9, 10))),
      "hit": [100, 100], "dead": IB.spans((340, 4, (7, 8, 9, 10)), (900, 4, (7, 9, 14, 60)))}


def actions(C):
    f = C.frame

    def under(**parts):
        return [(part, off, "under") for part, off in parts.items()]

    def sash(name, k):
        """The pose's sashes waved: their tips k rows up (negative: down), nothing where they are tied on."""
        return [("sash", 0, SASH[name], k, "right")]
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run_Slow: contact, passing, contact on the other leg, passing; the sceptre upright in his near hand):
    # each of the four drawn steps twice - landed and sunk into the step, then risen through the passing pose - with
    # the sashes waving behind him (no new legs drawn: they still change four times a cycle)
    out["run"] = [f("run1"), f("run1", sway=sash("run1", -3)), f("run2", lift=1, sway=sash("run2", 2)),
                  f("run2", lift=2, sway=sash("run2", 4)), f("run3"), f("run3", sway=sash("run3", -3)),
                  f("run4", lift=1, sway=sash("run4", 2)), f("run4", lift=2, sway=sash("run4", 4))]
    # attack (League's Attack_Command: the clawed hand raised, then pointed - the soldiers stab - and back): the hand
    # coming up beside him, raised; the arm shooting out, pointed a step ahead (as the soldiers stab), held; drawn
    # back in; the idle
    out["attack"] = [f("c_wind", dx=-1, moves=under(arm=(0, 5))), f("c_wind", dx=-2),
                     f("c_point", dx=1, moves=under(arm=(-7, 0))), f("c_point", dx=3), f("c_point", dx=1),
                     f("c_point", moves=under(arm=(-6, 0))), f("idle")]
    # Conquering Sands (Attack1's swing: the sceptre cocked back, then thrust out level - the soldiers rush): the
    # sceptre drawn back through his fist, cocked; shot out through it, at full reach a step ahead, held, drawn back
    out["skill"] = [f("q_wind", moves=under(spear=(2, 5))), f("q_wind", dx=-2),
                    f("q_thrust", moves=under(spear=(-12, 0))), f("q_thrust", dx=5), f("q_thrust", dx=3),
                    f("q_thrust", dx=2, moves=under(spear=(-4, 0)))]
    # Shifting Sands (Spell3_Dash: flying ahead behind the sceptre, then the landing crouch): taking off low, level,
    # stretched out higher, coming down, the sashes streaming; landing a step long, the crouch
    out["skill2"] = [f("e_dash", dx=-3, lift=3, sway=sash("e_dash", -3)), f("e_dash", lift=5),
                     f("e_dash", dx=2, lift=6, sway=sash("e_dash", 3)), f("e_dash", dx=3, lift=3, sway=sash("e_dash", 4)),
                     f("e_land", dx=4, sway=sash("e_land", 4)), f("e_land", dx=2)]
    # Emperor's Divide (spell4: the far arm spread, the sceptre lifted high, then swept down - the guards charge): the
    # arm going out, spread; the sceptre pushed up through his fist as he rises, lifted; swept down a step long with
    # the sceptre still coming round, down, the sashes settling, held
    out["ult"] = [f("r_raise", moves=under(arm=(-8, 0))), f("r_raise", dx=-1),
                  f("r_lift", moves=under(spear=(0, 8))), f("r_lift", lift=2, moves=under(spear=(0, 3))),
                  f("r_lift", lift=3),
                  f("r_sweep", dx=5, moves=under(spear=(-6, -3))), f("r_sweep", dx=3),
                  f("r_sweep", dx=2, sway=sash("r_sweep", 3)), f("r_sweep", dx=2)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: reeling back, the sceptre tipping; down on his knees, the sceptre dropped before him):
    # struck, reeling back step by step - the arm flung out, the sashes thrown up; on his knees with the sceptre still
    # falling before him, landing, the sashes settling, still
    out["dead"] = [f("d_stagger", dx=-1, flash=True), f("d_stagger", dx=-3, moves=under(arm=(-6, 0))),
                   f("d_stagger", dx=-5, sway=sash("d_stagger", 3)), f("d_stagger", dx=-6, sway=sash("d_stagger", -2)),
                   f("d_kneel", dx=-3, moves=[("spear", (0, -9), "over")], sway=sash("d_kneel", 4)),
                   f("d_kneel", dx=-2, moves=[("spear", (0, -3), "over")], sway=sash("d_kneel", 3)),
                   f("d_kneel", dx=-2, sway=sash("d_kneel", 1)), f("d_kneel", dx=-2)]
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


# ------------------------------------------------------------------------------------------------------- summons
STEP = KIT["s_step"] * 1000 // 60          # a soldier's picture is stamped again every s_step ticks (667 ms)
SLOT_AT = {"a": (0, 0), "b": (-8, -3), "c": (8, 3)}   # game px each slot's soldier stands off the spot (three on one spot)
GUARDS = [(-6, -14), (0, 0), (6, 14)]                 # game px the wall's three guards stand off the stamp (back to front)
G_STEP = 1000 * (KIT["r_len"] // KIT["r_stamps"]) // KIT["r_speed"] // 60   # ms a wall stamp shows (one hop)


class Summon:
    """A summon's frames as dense canvases: pictures placed about the pivot (a ground spot's soles are FEET under it,
    like a unit's), each `sink` rows under the ground clipped (rising out of the sand)."""

    def __init__(self, W=150, H=200, ppu=S_PPU):
        self.W, self.H, self.ppu = W, H, ppu
        self.px = W / 2.0
        self.soles = H - 30
        self.py = self.soles - FEET * ppu

    def frame(self, items):
        """items: [(picture, (dx, dy) game px off the pivot, sink rows, mirrored[, root column])] drawn back to front:
        centred on the pivot, or with its root column (its feet) there."""
        can = np.zeros((self.H, self.W, 4), np.uint8)
        for d, (dx, dy), sink, mirror, *root in items:
            if mirror:
                d = d[:, ::-1]
                root = [d.shape[1] - 1 - r for r in root]
            x0 = int(round(self.px + dx * self.ppu - d.shape[1] / 2)) if not root else int(round(self.px + dx * self.ppu)) - root[0]
            ground = self.soles + int(round(dy * self.ppu))
            y0 = ground - d.shape[0] + sink
            ys, xs = np.nonzero(d[..., 3] > 0)
            ty, tx = ys + y0, xs + x0
            ok = (ty >= 0) & (ty < min(self.H, ground)) & (tx >= 0) & (tx < self.W)
            if not ok.all() and not sink:
                sys.exit(f"summon: {int((~ok).sum())} squares off its canvas")
            can[ty[ok], tx[ok]] = d[ys[ok], xs[ok]]
        return can


def ms_split(ticks, parts):
    """`ticks` in ms (rounded) shared out in the proportions `parts` (whole ms, the last takes the rest)."""
    total = round(ticks * 1000 / 60)
    out = [round(total * p / sum(parts)) for p in parts[:-1]]
    return out + [total - sum(out)]


def side_soldier(S):
    """The add-on's soldier from the side: {tag: [(canvas, ms)]} - stand (one stamp), rise (out of the sand) and stab
    (wind, thrust, hold, recover), each facing right (_r) and mirrored left (_l), its feet on the pivot."""
    with open(lp(os.path.join(SRC, "soldier_side.json")), encoding="utf-8") as f:
        meta = json.load(f)
    pose = {n: (load(f"soldier_side_{n}.png"), meta[n]["root"][0]) for n in ("stand", "wind", "thrust", "hold", "recover")}
    out = {}
    for side, mirror in (("r", False), ("l", True)):
        at = lambda n, sink=0: S.frame([(pose[n][0], (0, 0), sink, mirror, pose[n][1])])
        h = pose["stand"][0].shape[0]
        out[f"stand_{side}"] = [(at("stand"), ms_split(KIT["ss_stand"], [1])[0])]
        out[f"rise_{side}"] = list(zip([at("stand", h * 2 // 3), at("stand", h // 3), at("stand")],
                                       ms_split(KIT["ss_rise"], [27, 27, 46])))
        out[f"stab_{side}"] = list(zip([at("wind"), at("thrust"), at("hold"), at("recover")],
                                       ms_split(KIT["ss_stab"], [3, 6, 3, 4])))
    return out


def summon_tags():
    """{sheet: {tag: [(canvas, ms)]}}: the soldier (each slot's standing stamp and its rise), the guard wall (a hop's
    stamp, two steps, right and left), the disc (its rise and its standing stamp) and the add-on's soldier from the
    side."""
    sol, lift, stab = load("soldier.png"), load("soldier_lift.png"), load("soldier_stab.png")
    g1, g2 = load("guard_push1.png"), load("guard_push2.png")
    disc = load("disc.png")
    S = Summon(ppu=SOLDIER_PPU)
    soldier = {}
    for s, at in SLOT_AT.items():
        soldier[f"soldier_{s}"] = [(S.frame([(sol, at, 0, False)]), STEP)]
        soldier[f"soldier_{s}_rise"] = [(S.frame([(sol, at, 36, False)]), 80), (S.frame([(sol, at, 18, False)]), 80),
                                        (S.frame([(lift, at, 0, False)]), 160), (S.frame([(stab, at, 0, False)]), 160),
                                        (S.frame([(sol, at, 0, False)]), STEP - 480)]
    W = Summon(220, 240)
    guard = {}
    for side, mirror in (("r", False), ("l", True)):
        for k, pic in (("a", g1), ("b", g2)):
            sign = -1 if mirror else 1
            guard[f"charge_{side}_{k}"] = [(W.frame([(pic, (sign * dx, dy), 0, mirror) for dx, dy in GUARDS]), G_STEP)]
    # one guard alone on the pivot (league_azir 0.2.4): the add-on stands them in one line across the charge, whatever
    # its direction - its three stamps of three overlapped into three ranks (「推起来像是有三排士兵」)
    for side, mirror in (("r", False), ("l", True)):
        for k, pic in (("a", g1), ("b", g2)):
            guard[f"one_{side}_{k}"] = [(W.frame([(pic, (0, 0), 0, mirror)]), G_STEP)]
    D = Summon(120, 160)
    disc_tags = {"disc_rise": [(D.frame([(disc, (0, 0), n, False)]), 90) for n in (60, 45, 30, 15)]
                 + [(D.frame([(disc, (0, 0), 0, False)]), 200)],
                 "disc": [(D.frame([(disc, (0, 0), 0, False)]), STEP)]}
    # every dense effect sheet leads with idle / hd_idle (league_main src/lookup.rs densify_table tells a dense table by
    # them): its standing picture
    soldier = {"idle": soldier["soldier_a"], **soldier}
    guard = {"idle": guard["charge_r_a"], **guard}
    disc_tags = {"idle": disc_tags["disc"], **disc_tags}
    SS = Summon(216, 120, ppu=SOLDIER_PPU)
    side = side_soldier(SS)
    side = {"idle": side["stand_r"], **side}
    return {"league_azir_soldier": (S, soldier), "league_azir_guard": (W, guard), "league_azir_disc": (D, disc_tags),
            "league_azir_soldier_side": (SS, side)}


def summon_sheets():
    """{sheet: {tag: [(1x frame, ms)], hd_<tag>: [(dense frame, ms)]}} cut about each sheet's pivot (league_illaoi's
    tentacle_tags)."""
    out = {}
    for sheet, (S, tags) in summon_tags().items():
        tt = {}
        for tag, seq in tags.items():
            ones, hds = [], []
            for can, ms in seq:
                ys, xs = np.nonzero(can[..., 3] > 0)
                hw = int(np.ceil(max(S.px - xs.min(), xs.max() + 1 - S.px) / S.ppu - 0.5))
                hh = int(np.ceil(max(S.py - ys.min(), ys.max() + 1 - S.py) / S.ppu - 0.5))
                hh = max(hh, int(np.ceil(FEET)) + 1)
                ones.append((R.one_of(can, S.px, S.py, hw, hh, S.ppu), ms))
                Wd, Hd = round((2 * hw + 1) * S.ppu), round((2 * hh + 1) * S.ppu)
                hds.append((R.crop_dense(can, S.px, S.py, Wd, Hd), ms))
            tt[tag] = ones
            tt[f"hd_{tag}"] = hds
        out[sheet] = tt
    return out


def review_summons(out_dir):
    """The summons' tags at 3x as GIFs (their hd frames), on the arena colour."""
    os.makedirs(out_dir, exist_ok=True)
    for sheet, tt in summon_sheets().items():
        for tag, fr in tt.items():
            if not tag.startswith("hd_"):
                continue
            H = max(c.shape[0] for c, _ in fr)
            W = max(c.shape[1] for c, _ in fr)
            ims = []
            for c, ms in fr:
                bg = Image.new("RGBA", (W, H), (104, 112, 72, 255))
                bg.alpha_composite(Image.fromarray(c), ((W - c.shape[1]) // 2, (H - c.shape[0]) // 2))
                ims.append(bg.convert("RGB").resize((W * 3, H * 3), Image.NEAREST))
            ims[0].save(os.path.join(out_dir, f"{sheet}_{tag[3:]}.gif"), save_all=True, append_images=ims[1:],
                        duration=[int(ms) for _, ms in fr], loop=0)
            print(sheet, tag[3:], len(fr), "frames", sum(ms for _, ms in fr), "ms")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    ap.add_argument("--summons", action="store_true", help="write the summons' sheets only")
    a = ap.parse_args()
    if a.summons:
        write_summons()
        return
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    if a.review:
        C.rig.review(acts, a.review)
        review_summons(os.path.join(a.review, "summons"))
        return
    C.rig.export(acts)
    write_summons()


def write_summons():
    for sheet, tt in summon_sheets().items():
        w, h = G.write_sheet(lp(os.path.join(MOD, "effects", sheet)), tt, share=True)
        print(f"league/effects/{sheet}#sheet.png {w}x{h}: " + ", ".join(f"{t} {len(v)}" for t, v in tt.items()))


if __name__ == "__main__":
    main()
