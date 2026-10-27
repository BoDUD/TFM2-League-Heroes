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
right-facing one), and the soldier from the side (league_azir_soldier_side: stand, rise and stab, each right and left,
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

    def frame(self, name, dx=0, lift=0, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, lift)
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
MS = {"idle": [1000], "run": [150] * 4,
      "attack": [120, ms_of(KIT["atk_dur"]) - 120 - 120, 120],
      "skill": [120, ms_of(KIT["q_dur"]) - 120],
      "skill2": [260, ms_of(KIT["e_dur"]) - 260],
      "ult": [100, 170, ms_of(KIT["r_dur"]) - 270],
      "hit": [100, 100], "dead": [140, 200, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Run_Slow: contact, passing, contact on the other leg, passing; the sceptre upright in his near hand)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (League's Attack_Command: the clawed hand raised, then pointed - the soldiers stab - and back)
    out["attack"] = [f("c_wind"), f("c_point", dx=1), f("idle")]
    # Conquering Sands (Attack1's swing: the sceptre cocked back, then thrust out level - the soldiers rush)
    out["skill"] = [f("q_wind"), f("q_thrust", dx=2)]
    # Shifting Sands (Spell3_Dash: flying ahead behind the sceptre, then the landing crouch)
    out["skill2"] = [f("e_dash", lift=5), f("e_land", dx=2)]
    # Emperor's Divide (spell4: the far arm spread, the sceptre lifted high, then swept down - the guards charge)
    out["ult"] = [f("r_raise"), f("r_lift", lift=2), f("r_sweep", dx=2)]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (League's Death: reeling back, the sceptre tipping; down on his knees, the sceptre dropped before him)
    out["dead"] = [f("d_stagger", dx=-1, flash=True), f("d_stagger", dx=-2), f("d_kneel", dx=-2), f("d_kneel", dx=-2)]
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
