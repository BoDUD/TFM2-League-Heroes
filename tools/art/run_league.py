#!/usr/bin/env python3
"""League's run as the motion of our own art: a hero's run cycle rebuilt from its design, posed frame by frame on
League's run clip (the user, 2026-11-15, on the oppi mod's hand-drawn runs: 「怎么样做到走路时也和oppi模组也这样自然的动的
你想想办法」「用aseprite手绘的是吗 我们不能做到像手绘那样流畅？」「你要承认动画的差距 然后追赶上去 想个办法」).

    python tools/art/run_league.py motion --hero jinx [--lol D:\\WeGameApps\\lol]   # League's clip -> hd/<hero>_run_motion.json
    python tools/art/run_league.py parts --hero vi --review DIR                    # the part map over the design
    python tools/art/run_league.py build --hero jinx --review DIR [--legs]         # the frames at 4x + a GIF, nothing written
    python tools/art/run_league.py build --hero jinx                               # the run tags into the sheet (+ strips)
    python tools/art/jinx_excited_run.py                                           # (league_jinx: run_x is made from run)
    python -I tools/art/thin_outline.py --hero jinx                                # then the outline pass, as after any redraw

The motion (`motion`): the clip `Run` plays at base move speed (tools/lol/anim_graph.py), sampled SAMPLES times over
one stride cycle on the chibi model (the hero's poses.json proportions), seen from the side: every joint of the
hero's table as (forward, up, across) game px, up from League's floor. Numbers only (no render): committed beside
the design, so `build` runs without the client.

The build (`build`): N frames of one cycle, every frame the hero's design cut into parts and posed - no square
drawn anew but the thighs (the design's own rows laid along the bone), and nothing turned but the boots:
- timing: League's own cycle (Jinx_minigun_run 0.933 s, Vi_Run1 0.839 s) in N_FRAMES even frames (67 / 60 ms) -
  the user on the first drafts' 8 frames of ~70 ms over 0.55 s: 「太快，像小碎步」「帧太少，不够顺」「帧和帧之间跳」;
  the planted foot slides some (cadence over foot-lock), the stride a set share wider than League's;
- the legs: League's sole path relative to its hip (forward x the stride, up as League; both x our leg length /
  League's); the boot put down by its sole (Boot): turned only by multiples of STEP, one RotSprite picture per angle
  made once, upright (the design's own squares) while planted unless the shin leans HOLD or more, lifted where a
  turned heel or toe would go under the ground; the knee follows from the boot and the thigh is drawn to it;
- the body: League's pelvis bob (kept to a square a frame at most) by whole squares, the upper body leant from the
  hips by the same whole rows in every frame (a lean that changed each frame shimmered);
- the upper body from League's joints, by whole squares only (a part turned a little more each frame is re-pixelled
  each frame and shimmers; the user on v3: 「露露还做的不如旧版 而且手和武器严重脱节」): the head bobbing less than the
  hips; what holds a weapon moving with it as one piece (league_jinx's gun, both hands and arms; league_vi's gauntlets
  are her hands) - a gun a frame behind the body by a square at most -, gauntlets pumping with League's gloves;
  braids bent through League's hair chain (its middle and tip) by whole rows, hair trailing the body by a beat, a
  prop on the back a frame behind.
The dense frames are all one size, centred on the pivot as the hero's other frames (hd_idle_base), the outline grown
to the hero's KEEP (thin_outline.json) as its other frames have it; the 1x frames come from them the way
tools/art/ppu_one.py makes them, the lo_ frames the way tools/art/ppu_hd.py does. The sheet keeps every other tag's
frames where they are (the run's old squares are cleared, the new frames put in the free room).
"""
import argparse
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

G = R.G
SAMPLES = 48
N_FRAMES = 14           # frames a cycle (the user, on 8 of ~70 ms: 「帧太少，不够顺」「帧和帧之间跳」「太快，像小碎步」)
CYCLE_HEIGHTS = 0.85    # (a cycle covering this many body heights - the first drafts' pace, too quick: unused now)
STEP = 15               # degrees: a boot is only ever turned by a multiple of this (one picture each, held)
HOLD = 12               # degrees: a planted boot turned less than this stands upright (the design's own boot)
TICKS = 60              # game ticks a second
DARK = 26               # luminance under which a square is outline (inbetween.DARK)

# hero -> League's clip and the joints the build reads. cycle: one stride cycle in clip seconds (a clip may hold several:
# Lulu_Run.anm four in its 2 s); tick: the graph's mTickDuration over the clip's own frame time (Lulu's 0.05 s a frame
# at 30 fps plays her cycle 1.5 times as long). (league_lulu was tried and dropped from the pilot - her robe, hat and
# staff came out deformed: 「露露还被你做变形了」 - her old run stays.)
HEROES = {
    "jinx": dict(clip="Jinx_minigun_run", cycle=0.9333, tick=1.0,
                 joints=dict(pelvis="Pelvis", chest="Spine3", neck="Neck", head="Head",
                             l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                             r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                             l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                             r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                             gun="Minigun", gun_front="Minigun_Handle_Front", gun_back="Minigun_Handle_Back",
                             rocket="Rocket_Launcher", rocket_front="Rocket_Launcher_Front",
                             l_hair1="L_Hair1", l_hair3="L_Hair3", l_hair6="L_Hair6",
                             r_hair1="R_Hair1", r_hair3="R_Hair3", r_hair6="R_Hair6")),
    "vi": dict(clip="Vi_Run1", cycle=0.8387, tick=1.0,
               joints=dict(pelvis="Root", spine="Spine1", chest="Spine3", neck="Neck", head="Head",
                           l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                           r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                           l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_GloveHand",
                           l_forearm="L_GloveForarm",
                           r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_GloveHand",
                           r_forearm="R_GloveForarm",
                           hair1="Hair1", hair2="Hair2", l_flap="L_JacketFlap", r_flap="R_JacketFlap")),
    # (the clips the character runs - tools/art/run_body_anim.py's `char` variants - read: what each hero's own Run
    # does with its hands, weapon, head, shoulders and hair against the chest; League's base-speed clip, the one our
    # drawn run's cycle matches)
    "fiora": dict(clip="fiora_runwalk", cycle=1.0, tick=0.909,
                  joints=dict(pelvis="Pelvis", chest="Spine2", neck="Neck", head="Head",
                              l_hip="L_Hip", l_knee="L_Knee", l_foot="L_Foot", l_toe="L_Toe",
                              r_hip="R_Hip", r_knee="R_Knee", r_foot="R_Foot", r_toe="R_Toe",
                              l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                              r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                              weapon="Weapon", weapon_tip="Weapon_gleam", l_pauldron="L_Pauldron",
                              r_pauldron="R_Pauldron", cape_a="Back_CapeA", cape_c="Back_CapeC", cape_f="Back_CapeF",
                              l_hair="L_Head_HairA", r_hair="R_Head_HairA")),
    "zyra": dict(clip="Zyra_run", cycle=1.0667, tick=1.0,
                 joints=dict(pelvis="Pelvis", chest="Chest", neck="Neck", head="Head",
                             l_hip="L_Hip", l_knee="L_Knee", l_foot="L_Foot", l_toe="L_Toe",
                             r_hip="R_Hip", r_knee="R_Knee", r_foot="R_Foot", r_toe="R_Toe",
                             l_shoulder="L_Shoulder", l_elbow="L_ForeArm", l_hand="L_Hand",
                             r_shoulder="R_Shoulder", r_elbow="R_ForeArm", r_hand="R_Hand",
                             hair1="Hair_M_1", hair3="Hair_M_3", hair5="Hair_M_5", bang1="Hair_R_bang_1",
                             bang4="Hair_R_bang_4", l_vine1="L_Vine_1", l_vine4="L_Vine_4", l_vine8="L_Vine_8",
                             r_vine1="R_Vine_1", r_vine4="R_Vine_4", r_vine8="R_Vine_8")),
    "leesin": dict(clip="Run_Base", cycle=1.5333, tick=0.6,
                   joints=dict(pelvis="Pelvis", chest="Chest", neck="Neck1", head="Head",
                               l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                               r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                               l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                               r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                               hair1="Hair1", hair6="Hair6", hair12="Hair12", tie="HeadBandTie1",
                               f_cloth="F_ClothA3", b_cloth="B_Cloth3")),
    "ezreal": dict(clip="ezreal_run", cycle=1.0, tick=1.0,
                   joints=dict(pelvis="Pelvis", chest="Spine2", neck="Neck", head="Head",
                               l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                               r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                               l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand", gauntlet="L_Gauntlet",
                               r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                               cape1="R_Cape1", cape4="R_Cape4", hair_a2="Hair_A2", hair_b2="Hair_B2",
                               l_jacket3="L_Jacket3", r_jacket3="R_Jacket3", goggles="C_Goggles")),
    # (lux_run.anm holds six strides in its 4.8 s: one is 0.8 s of clip; the graph plays it at mTickDuration 0.0323)
    "lux": dict(clip="lux_run", cycle=0.8, tick=0.969,
                joints=dict(pelvis="hip", spine="spine", chest="chest", neck="neck", head="head",
                            l_hip="L_Thigh", l_knee="L_Knee", l_foot="L_Foot", l_toe="L_Toe",
                            r_hip="R_Thigh", r_knee="R_Knee", r_foot="R_Foot", r_toe="R_Toe",
                            l_shoulder="L_UpArm", l_elbow="L_ForeArm", l_hand="L_Hand",
                            r_shoulder="R_UpArm", r_elbow="R_ForeArm", r_hand="R_Hand",
                            weapon="WEAPON", weapon_b="WEAPON_b", hair="hair", hair_b="hair_b", f_hair="F_hair",
                            f_belt="F_Belt_b", b_l_cloth="B_L_Cloth_b", b_r_cloth="B_R_Cloth_b",
                            f_l_cloth="F_L_Cloth", f_r_cloth="F_R_Cloth", l_cloth="L_Cloth", r_cloth="R_Cloth")),
    # (`Run` at her base move speed is run_base: seraphin_Run.anm, one 1.067 s cycle on her floating stage)
    "seraphine": dict(clip="seraphin_Run", cycle=1.0667, tick=1.0,
                      joints=dict(pelvis="Pelvis", chest="Chest", neck="Neck", head="Head",
                                  l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                                  r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                                  l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                                  r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                                  platform="Platform", c_hair1="C_Hair1", c_hair2="C_Hair2", c_hair4="C_Hair4",
                                  l_hair4="L_Hair4", r_hair4="R_Hair4", front_hair="R_Front_Hair3",
                                  ribbon="L_Bottom_Ribon2", l_speaker="L_Speaker", c_speaker="C_Speaker",
                                  r_speaker="R_Speaker")),
    # (Syndra_run.anm holds two floats in its 1.867 s: one is 0.933 s; she has no pelvis joint - Spine1 is hers)
    "syndra": dict(clip="Syndra_run", cycle=0.9333, tick=1.0,
                   joints=dict(pelvis="Spine1", spine="Spine2", chest="Spine3", neck="Neck", head="Head",
                               l_hip="L_Hip", l_knee="L_Knee", l_foot="L_Foot", l_toe="L_Toe",
                               r_hip="R_Hip", r_knee="R_Knee", r_foot="R_Foot", r_toe="R_Toe",
                               l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                               r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                               hair1="Hair1", hair3="Hair3", hair5="Hair5", l_hair1="L_Hair1", l_hair3="L_Hair3",
                               r_hair1="R_Hair1", r_hair3="R_Hair3", l_cloth1="L_Cloth1", l_cloth3="L_Cloth3",
                               r_cloth1="R_Cloth1", r_cloth3="R_Cloth3")),
    # (`Run` is run_base when not homeguard: Run.anm holds eight strides in its 8.533 s, one is 1.067 s)
    "viktor": dict(clip="Run", cycle=1.0667, tick=1.0,
                   joints=dict(pelvis="Pelvis", spine="Spine2", chest="Chest", neck="Neck", head="Head",
                               l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                               r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                               l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                               r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                               weapon="Weapon1", staff1="Staff1", staff6="Staff6", sphere="WeaponSphere",
                               backarm="C_BackArmMain", backarm4="C_Backarm4", claw="C_ClawMain",
                               l_armor="L_ShoulderArmor", r_armor="R_ShoulderArmor", l_cape3="L_Cape3",
                               l_cape6="L_Cape6", r_cape3="R_Cape3", r_cape6="R_Cape6", jacket3="C_Jacket3",
                               l_jacket3="L_Jacket3", r_jacket3="R_Jacket3", hair4="Hair4")),
    # (vladimir_run.anm holds two strides in its 1.6 s: one is 0.8 s of clip; the graph plays it at mTickDuration 0.04)
    "vladimir": dict(clip="vladimir_run", cycle=0.8, tick=1.2,
                     joints=dict(pelvis="C_Hip", spine="C_Waist", chest="C_Chest", neck="C_Neck", head="C_Head",
                                 l_hip="L_Thigh", l_knee="L_Knee", l_foot="L_Foot", l_toe="L_Toe",
                                 r_hip="R_Thigh", r_knee="R_Knee", r_foot="R_Foot", r_toe="R_Toe",
                                 l_shoulder="L_UpArm", l_elbow="L_ForeArm", l_hand="L_Hand",
                                 r_shoulder="R_UpArm", r_elbow="R_ForeArm", r_hand="R_Hand",
                                 collar="Collar_b", l_collar="L_Collar_b", r_collar="R_Collar_b",
                                 l_sleeve="L_Sleeves", r_sleeve="R_Sleeves", l_armor="L_Armor_b", r_armor="R_Armor_b",
                                 b_cloth="B_Cloth_e", b_cloth_c="B_Cloth_c", l_cloth="L_Cloth_c", r_cloth="R_Cloth_c")),
}
# (character runs, round 2 - the clip each hero plays at base move speed, its length read from the .anm: league_jax's
# run_base is Jax_Run2.anm, 1.067 s; his topknot - Hair1-6 - and cloak strips - Cape*, C / L / R_Cape* - lead his run)
HEROES.update({
    "jax": dict(clip="Jax_Run2", cycle=1.0667, tick=1.0,
                joints=dict(pelvis="Pelvis", spine="Spine1", chest="Chest", neck="Neck", head="Head",
                            l_hip="L_Hip", l_knee="L_KneeLower", l_foot="L_Foot", l_toe="L_Toe",
                            r_hip="R_Hip", r_knee="R_KneeLower", r_foot="R_Foot", r_toe="R_Toe",
                            l_shoulder="L_Shoulder", l_elbow="L_Elbow", l_hand="L_Hand",
                            r_shoulder="R_Shoulder", r_elbow="R_Elbow", r_hand="R_Hand",
                            weapon="Weapon", weapon_top="Weapon_Top", weapon_head="Weapon_Head",
                            weapon_bottom="Weapon_Bottom", weapon_end="Weapon_End", hat="Hat",
                            hair1="Hair1", hair3="Hair3", hair6="Hair6", cape1="Cape1", cape3="Cape3",
                            cape_end="Cape_end", c_cape_end="C_Cape_end", l_cape_end="L_Cape_end",
                            r_cape_end="R_Cape_end", l_tassel="L_Hood_Tassel_end", r_tassel="R_Hood_Tassel_end")),
    # (league_graves has no poses.json: `spec` says his model - the run's graph plays graves_run.anm's 1.0 s at a tick of
    # 0.037 s a frame, so a cycle is 1.111 s)
    "graves": dict(clip="graves_run", cycle=1.0, tick=1.1111,
                   spec=dict(champ="Graves", chibi={"head": 1.0, "legs": 1.0}, design="graves_idle1@0", height=39),
                   joints=dict(pelvis="hip", spine="spine", chest="chest", neck="neck", head="head",
                               l_hip="l_thigh", l_knee="l_knee", l_foot="l_foot", l_toe="l_toe",
                               r_hip="r_thigh", r_knee="r_knee", r_foot="r_foot", r_toe="r_toe",
                               l_shoulder="l_shoulder", l_elbow="l_forearm", l_hand="l_hand",
                               r_shoulder="r_shoulder", r_elbow="r_forearm", r_hand="r_hand",
                               weapon="weapon", barrels="barrels", tip="buffbone_cstm_tipa",
                               mantle_a="mantle_a", mantle_b="mantle_b", mantle_c="mantle_c", mantle_d="mantle_d",
                               mantle_e="mantle_e", mantle_f="mantle_f", mantle_g="mantle_g", mantle_h="mantle_h",
                               mantle_i="mantle_i", mantle_j="mantle_j", mantle_k="mantle_k", mantle_l="mantle_l")),
})


def lp(path):
    return R.lp(path)


def motion_path(hero):
    return os.path.join(ROOT, "assets", "source", hero, "hd", f"{hero}_run_motion.json")


# ================================================================================================== League's motion
def extract(hero, lol):
    """League's run clip sampled over one cycle, side view, chibi proportions -> the motion table (see the module)."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "lol"))
    import native_pose as N
    cfg = HEROES[hero]
    poses = os.path.join(ROOT, "assets", "source", hero, "poses.json")
    if cfg.get("spec") and not os.path.isfile(lp(poses)):
        spec = cfg["spec"]                               # (a hero without a poses.json: its entry says the model)
    else:
        with open(lp(poses), encoding="utf-8") as f:
            spec = json.load(f)
    chibi = dict(spec["chibi"])
    keep = chibi.pop("keep", None)
    # (the spec's `head_joint` too, as native_pose.py passes it: league_vladimir's mesh rides C_Head, not head)
    ch = N.Champ(lol, spec["champ"], keep, spec.get("weapon", r"^weapon$"), spec.get("hide", ()),
                 spec.get("hair_part", False), spec.get("crown"), spec.get("parts", ()),
                 spec.get("hide_submeshes", False), spec.get("submesh_textures"), spec.get("glue"), spec.get("legs"),
                 spec.get("head_joint", "head"))
    rot = N.camera({"yaw": 90, "pitch": 0})              # the model's +Z (its front) to +x: facing right
    by = {j["name"].lower(): i for i, j in enumerate(ch.joints)}
    pv, glob, _ = ch.posed(spec["design"], chibi)
    cv = pv @ rot.T
    unit = spec["height"] / (cv[ch.headv, 1].max() - cv[ch.legv, 1].min())   # game px per world unit
    floor = cv[ch.legv, 1].min()

    def point(g, name):
        p = rot @ g[by[name.lower()]][:3, 3]
        return [round(float(p[0] * unit), 3), round(float((p[1] - floor) * unit), 3), round(float(p[2] * unit), 3)]

    design = {k: point(glob, n) for k, n in cfg["joints"].items()}
    rows, low = [], []
    for k in range(SAMPLES):
        t = cfg["cycle"] * k / SAMPLES
        pv, glob, _ = ch.posed(f"{cfg['clip']}@{t * 1000:.3f}", chibi)
        rows.append({n: point(glob, j) for n, j in cfg["joints"].items()})
        low.append(round(float(((pv @ rot.T)[ch.legv, 1].min() - floor) * unit), 3))
    return {"champ": spec["champ"], "clip": cfg["clip"], "cycle_s": cfg["cycle"] * cfg["tick"], "unit": unit,
            "height": spec["height"], "chibi": spec["chibi"], "design": design, "low": low, "frames": rows}


def write_motion(hero, m):
    with open(lp(motion_path(hero)), "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n" + ",\n".join(f' "{k}": ' + json.dumps(v, separators=(",", ":"))
                                   for k, v in m.items() if k != "frames"))
        f.write(',\n "frames": [\n' + ",\n".join("  " + json.dumps(r, separators=(",", ":"))
                                               for r in m["frames"]) + "\n ]\n}\n")


class Motion:
    """The motion table, read at any phase (0..1 over the cycle, linear between samples, wrapping)."""

    def __init__(self, hero):
        with open(lp(motion_path(hero)), encoding="utf-8") as f:
            m = json.load(f)
        self.m = m
        self.n = len(m["frames"])
        self.cycle_s = m["cycle_s"]
        self.names = list(m["frames"][0])
        self.arr = {k: np.array([r[k] for r in m["frames"]], float) for k in self.names}   # (n, 3)
        self.low = np.array(m["low"], float)

    def at(self, name, ph):
        a = self.arr[name]
        x = (ph % 1.0) * self.n
        i = int(math.floor(x)) % self.n
        t = x - math.floor(x)
        return a[i] * (1 - t) + a[(i + 1) % self.n] * t

    def mean(self, name):
        return self.arr[name].mean(0)

    def sole(self, side):
        """(n, 2): the foot joint's forward and height over League's floor, the height less its lowest (the sole on
        the floor when planted)."""
        f = self.arr[f"{side}_foot"]
        return np.c_[f[:, 0], f[:, 1] - f[:, 1].min()]

    def stance(self, side, tol=0.5):
        """Samples where the foot is planted: within tol px of its lowest."""
        f = self.arr[f"{side}_foot"][:, 1]
        return f <= f.min() + tol

    def stance_speed(self, side):
        """How fast the planted foot goes back under the hip (px a second of League's cycle): the slope of its x
        relative to the hip over the planted samples."""
        st = self.stance(side)
        x = self.arr[f"{side}_foot"][:, 0] - self.arr[f"{side}_hip"][:, 0]
        dt = self.cycle_s / self.n
        sp = [(x[i] - x[(i + 1) % self.n]) / dt for i in range(self.n) if st[i] and st[(i + 1) % self.n]]
        return float(np.median(sp)) if sp else 0.0

    def contact(self, side):
        """The phase the foot lands (the first planted sample after a lifted one)."""
        st = self.stance(side)
        for i in range(self.n):
            if st[i] and not st[i - 1]:
                return i / self.n
        return 0.0


# ================================================================================================== geometry
def ik(hip, target, l1, l2, bend=1.0):
    """The knee of a two-bone leg from `hip` to `target` (design squares, y down), bending forward (+x) for bend > 0.
    A target out of reach: the leg straight toward it. -> (knee, the reached end)."""
    h, t = np.asarray(hip, float), np.asarray(target, float)
    v = t - h
    d = float(np.hypot(*v))
    if d < 1e-6:
        v, d = np.array([0.0, 1.0]), 1e-6
    u = v / d
    if d >= l1 + l2 - 1e-6:
        return h + u * l1, h + u * (l1 + l2)
    d = max(d, abs(l1 - l2) + 1e-6)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    hgt = math.sqrt(max(0.0, l1 * l1 - a * a))
    n = np.array([u[1], -u[0]])                       # the side of the line: (down -> +x) ... see bend
    if n[0] * bend < 0:
        n = -n
    return h + u * a + n * hgt, t


def angle_down(v):
    """Degrees of a vector (x, y down) from straight down, + toward +x (forward)."""
    return math.degrees(math.atan2(v[0], v[1]))


def _scale2x(a):
    H, W = a.shape
    p = np.pad(a, 1)
    A, B, C, D = p[:-2, 1:-1], p[1:-1, 2:], p[1:-1, :-2], p[2:, 1:-1]
    out = np.empty((H * 2, W * 2), a.dtype)
    out[0::2, 0::2] = np.where((C == A) & (C != D) & (A != B), A, a)
    out[0::2, 1::2] = np.where((A == B) & (A != C) & (B != D), B, a)
    out[1::2, 0::2] = np.where((D == C) & (D != B) & (C != A), C, a)
    out[1::2, 1::2] = np.where((B == D) & (B != A) & (D != C), D, a)
    return out


def turned(img, at, src, dst, degrees, outline, tidy=True):
    """A part's picture `img` (its top-left at design square `at`) turned `degrees` counter-clockwise on screen about
    its point `src` and put with that point on `dst` (design squares, any fraction), RotSprite's way (inbetween.spin:
    Scale2x three times, turned, each square the commonest colour of its 8 x 8 block) - only its own colours, the
    outline tidied. -> (picture, its top-left square)."""
    H, W = img.shape[:2]
    m = img[..., 3] > 0
    packed = np.zeros((H, W), np.uint32)
    c = img.astype(np.uint32)
    packed[m] = (c[m][:, 0] << 16) | (c[m][:, 1] << 8) | c[m][:, 2] | np.uint32(0xFF000000)
    if not degrees and abs(dst[0] - src[0] - round(dst[0] - src[0])) < 1e-9 and \
            abs(dst[1] - src[1] - round(dst[1] - src[1])) < 1e-9:
        return img.copy(), (at[0] + int(round(dst[0] - src[0])), at[1] + int(round(dst[1] - src[1])))
    big = _scale2x(_scale2x(_scale2x(packed)))
    K = 8
    th = math.radians(degrees)
    co, si = math.cos(th), math.sin(th)
    # the turned picture's box (design squares): the corners of img turned
    corners = np.array([[at[0], at[1]], [at[0] + W, at[1]], [at[0], at[1] + H], [at[0] + W, at[1] + H]], float) - src
    tx = corners[:, 0] * co + corners[:, 1] * si + dst[0]
    ty = -corners[:, 0] * si + corners[:, 1] * co + dst[1]
    x0, y0 = int(math.floor(tx.min())) - 1, int(math.floor(ty.min())) - 1
    x1, y1 = int(math.ceil(tx.max())) + 1, int(math.ceil(ty.max())) + 1
    Wo, Ho = x1 - x0, y1 - y0
    Y, X = np.mgrid[0:Ho * K, 0:Wo * K]
    px = x0 + (X + 0.5) / K - dst[0]
    py = y0 + (Y + 0.5) / K - dst[1]
    sx = (px * co - py * si) + src[0]                  # back through the turn
    sy = (px * si + py * co) + src[1]
    fx = np.floor((sx - at[0]) * K).astype(int)
    fy = np.floor((sy - at[1]) * K).astype(int)
    ok = (fx >= 0) & (fx < W * K) & (fy >= 0) & (fy < H * K)
    rot = np.zeros((Ho * K, Wo * K), np.uint32)
    rot[ok] = big[fy[ok], fx[ok]]
    blocks = rot.reshape(Ho, K, Wo, K).transpose(0, 2, 1, 3).reshape(Ho, Wo, K * K)
    filled = (blocks != 0).sum(-1)
    out = np.zeros((Ho, Wo, 4), np.uint8)
    for y, x in zip(*np.nonzero(filled * 2 > K * K)):
        v = blocks[y, x]
        vals, cnt = np.unique(v[v != 0], return_counts=True)
        col = int(vals[cnt.argmax()])
        out[y, x] = ((col >> 16) & 255, (col >> 8) & 255, col & 255, 255)
    if tidy:
        out = G.complete_outline(out, color=tuple(outline), dark=DARK)[0]
        out = G.clean_outline(out, tuple(outline), dark=DARK)[0]
        lab, n = ndimage.label(out[..., 3] > 0, structure=np.ones((3, 3)))
        if n > 1:
            sz = ndimage.sum(out[..., 3] > 0, lab, range(1, n + 1))
            for j in range(1, n + 1):
                if sz[j - 1] < max(4, 0.05 * sz.max()):
                    out[lab == j] = 0
    return out, (x0, y0)


def sheared(img, at, k, pivot_row, profile=1.5):
    """A hanging part (a braid, a tail) swung by whole rows: each row below `pivot_row` (design rows) shifted
    k x ((r - pivot) / (last - pivot)) ** profile columns, nothing above it. -> (picture, top-left)."""
    H, W = img.shape[:2]
    x0, y0 = at
    p = pivot_row - y0
    s = [0 if r <= p else int(round(k * ((r - p) / max(1, H - 1 - p)) ** profile)) for r in range(H)]
    lo, hi = min(s), max(s)
    out = np.zeros((H, W + hi - lo, 4), np.uint8)
    for r in range(H):
        out[r, s[r] - lo:s[r] - lo + W] = img[r]
    return out, (x0 + lo, y0)


def lifted(img, at, k, x_free, x_root, profile=1.5):
    """A part streaming sideways (hair behind the head, a cape) waved by whole columns: each column lifted
    k x (distance from x_root / reach) ** profile rows toward its free end x_free, nothing at the root.
    -> (picture, top-left)."""
    H, W = img.shape[:2]
    x0, y0 = at
    reach = max(1, abs(x_free - x_root))
    s = []
    for c in range(W):
        x = x0 + c
        t = (x - x_root) / (x_free - x_root) if x_free != x_root else 0.0
        t = min(1.0, max(0.0, t))
        s.append(-int(round(k * t ** profile)))
    lo, hi = min(s), max(s)
    out = np.zeros((H + hi - lo, W, 4), np.uint8)
    for c in range(W):
        out[s[c] - lo:s[c] - lo + H, c] = img[:, c]
    return out, (x0, y0 + lo)


def bent(img, at, root_row, k_mid, k_tip, tip_row=None):
    """A hanging part (a braid) bent by whole rows through three points: nothing at `root_row`, k_mid columns
    half way down, k_tip at its last row (a smooth curve through them) - League's hair chain's middle and tip.
    -> (picture, top-left)."""
    H, W = img.shape[:2]
    x0, y0 = at
    last = (tip_row if tip_row is not None else y0 + H - 1)
    span = max(1.0, last - root_row)
    s = []
    for r in range(H):
        t = min(1.0, max(0.0, (y0 + r - root_row) / span))
        # the quadratic through (0, 0), (0.5, k_mid), (1, k_tip)
        a = 2 * k_tip - 4 * k_mid
        b = 4 * k_mid - k_tip
        s.append(int(round(a * t * t + b * t)))
    lo, hi = min(s), max(s)
    out = np.zeros((H, W + hi - lo, 4), np.uint8)
    for r in range(H):
        out[r, s[r] - lo:s[r] - lo + W] = img[r]
    return out, (x0 + lo, y0)


def angle_up(v):
    """Degrees of a vector (x, y down) from straight up, + leaning toward +x."""
    return math.degrees(math.atan2(v[0], -v[1]))


def rot_pt(p, about, degrees):
    """A point turned `degrees` counter-clockwise on screen about `about` (y down)."""
    th = math.radians(degrees)
    dx, dy = p[0] - about[0], p[1] - about[1]
    return np.array([about[0] + dx * math.cos(th) + dy * math.sin(th),
                     about[1] - dx * math.sin(th) + dy * math.cos(th)])


def wrap180(a):
    return (a + 180.0) % 360.0 - 180.0


def leant(img, at, k, hip_row):
    """The upper body leant forward from the hips: each row above `hip_row` (design rows) moved round(k x its
    height over the hips) columns forward (jinx_excited_run's lean, gentler). -> (picture, top-left)."""
    if not k:
        return img, at
    H, W = img.shape[:2]
    x0, y0 = at
    s = [int(round(k * max(0.0, hip_row - (y0 + r)))) for r in range(H)]
    lo, hi = min(s), max(s)
    out = np.zeros((H, W + hi - lo, 4), np.uint8)
    for r in range(H):
        out[r, s[r] - lo:s[r] - lo + W] = img[r]
    return out, (x0 + lo, y0)


class Canvas:
    """A frame being composed in design squares, PAD squares round the design."""

    def __init__(self, shape, pad):
        self.pad = pad
        self.a = np.zeros((shape[0] + 2 * pad, shape[1] + 2 * pad, 4), np.uint8)
        self.z = np.full(self.a.shape[:2], -1e9)

    def stamp(self, img, at, z):
        """img's squares at design square `at`, over what is lower (z) and under what is higher."""
        ys, xs = np.nonzero(img[..., 3] > 0)
        Y, X = ys + int(at[1]) + self.pad, xs + int(at[0]) + self.pad
        ok = (Y >= 0) & (Y < self.a.shape[0]) & (X >= 0) & (X < self.a.shape[1])
        Y, X, ys, xs = Y[ok], X[ok], ys[ok], xs[ok]
        up = self.z[Y, X] <= z
        Y, X, ys, xs = Y[up], X[up], ys[up], xs[up]
        self.a[Y, X] = img[ys, xs]
        self.z[Y, X] = z


class Boot:
    """A shin and boot (the design's own picture, its knee and its sole's contact point) put down by its sole: turned
    only by multiples of STEP (each turn one RotSprite picture, made once - consecutive frames at one angle show the
    very same squares, no shimmer), upright while planted unless the shin leans HOLD or more; the knee then follows
    from the boot, and the thigh is drawn to it."""

    def __init__(self, img, at, knee, contact, outline):
        self.img, self.at = img, at
        self.k0, self.c0 = np.array(knee, float), np.array(contact, float)
        self.rest = angle_down(self.c0 - self.k0)
        self.outline = outline
        self.cache = {}

    def turned_by(self, q):
        if q not in self.cache:
            self.cache[q] = turned(self.img, self.at, tuple(self.c0), tuple(self.c0), q, self.outline) if q else \
                (self.img.copy(), self.at)
        return self.cache[q]

    def place(self, hip, l1, l2, target, ground, planted):
        """-> (knee, boot picture, its top-left): the shin's angle from IK toward `target`, held to a multiple of
        STEP, the boot's contact on the target (whole squares; on the ground row when planted), lifted where a turned
        heel or toe would go under the ground."""
        knee_ik, end = ik(hip, target, l1, l2)
        theta = wrap180(angle_down(end - knee_ik) - self.rest)
        q = 0 if planted and abs(theta) < HOLD else int(round(theta / STEP)) * STEP
        img, at = self.turned_by(q)
        sx = int(round(end[0] - self.c0[0]))
        sy = int(round((ground if planted else end[1]) - self.c0[1]))
        ys = np.nonzero((img[..., 3] > 0).any(1))[0]
        under = (at[1] + sy + ys.max() + 1) - math.ceil(ground)
        if under > 0:
            sy -= under
        sole = self.c0 + np.array([sx, sy])
        knee = rot_pt(self.k0, self.c0, q) + np.array([sx, sy])
        return np.round(knee), img, (at[0] + sx, at[1] + sy), sole


def piece(d, m):
    ys, xs = np.nonzero(m)
    sub = d[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()
    sub[~m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]] = 0
    return sub, (int(xs.min()), int(ys.min()))


# ================================================================================================== the cycle
def move_speed(hero):
    with open(lp(os.path.join(ROOT, "league", "champion", f"league_{hero}.data_champion")), encoding="utf-8-sig") as f:
        return float(json.load(f)["stat"]["move_speed"])


class Gait:
    """Our run from League's: per frame the hip height, the body's sway, each leg's hip / knee / sole, and League's
    other joints at that phase (for what follows through).

    rig: the hero's numbers (design squares, y down): ground (the soles' bottom edge), hips {near, far} (x, y),
    thigh {near, far}, shin {near, far} (knee to the sole's contact point), sides {near: "l"|"r", far: ...} (which
    of League's legs drives ours), stride (forward scale of the sole path over the vertical), bob (share of League's
    pelvis bob kept), reach (the stance leg straight at most this share of its length), sway (share of League's
    pelvis sway kept)."""

    def __init__(self, hero, rig, ppu, n=None, cycle_s=None):
        self.m = Motion(hero)
        n = n or rig.get("frames", N_FRAMES)
        self.rig, self.ppu, self.n = rig, ppu, n
        v_px = move_speed(hero) / 1000.0 * TICKS                       # game px a second
        self.v = v_px * ppu                                            # squares a second
        height = rig["height"] / ppu                                   # game px tall
        # the cycle: League's own clip time (the run's cadence as League plays it), else CYCLE_HEIGHTS of ground
        self.cycle_s = cycle_s or (self.m.cycle_s * rig.get("cycle_k", 1.0) if rig.get("cycle") == "league"
                                   else round(CYCLE_HEIGHTS * height / v_px, 3))
        ms = int(round(self.cycle_s * 1000 / n))
        self.ms = [ms] * n
        self.cycle_s = ms * n / 1000.0
        m = self.m
        # League's leg (hip height over its floor, standing in the design pose) -> ours
        dsg = m.m["design"]
        lg_hip = np.mean([dsg[f"{s}_hip"][1] for s in "lr"])
        our_hip = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        self.s = our_hip / lg_hip                                      # squares per League px, up and down
        # forward: as far as the ground goes by while a foot is planted
        lg_v = np.mean([m.stance_speed(s) for s in "lr"])              # League px a second, at League's timing
        want = self.v * self.cycle_s                                   # squares of ground a cycle
        got = self.s * lg_v * m.cycle_s                                # League's planted sweep at our scale
        self.stride = rig.get("stride") or want / max(1e-6, got)
        self.stride = min(self.stride, rig.get("stride_max", 9.0))
        near_side = rig["sides"]["near"]
        self.ph0 = m.contact(near_side) + rig.get("phase", 0.0)       # frame 0: the near foot lands
        pel = m.arr["pelvis"][:, 1]
        self.pel_mean = pel.mean()
        self.sway_mean = m.arr["pelvis"][:, 0].mean()
        # the hip height: League's bob (x bob) about a middle chosen so every planted foot reaches the ground
        self.h_mid = self._fit_height()

    def phase(self, i):
        return (self.ph0 + i / self.n) % 1.0

    def _sole(self, key, ph, hip):
        """Our sole target for leg `key` at phase ph, its hip at `hip` (design squares)."""
        m, rig, side = self.m, self.rig, self.rig["sides"][key]
        f = m.at(f"{side}_foot", ph)
        h = m.at(f"{side}_hip", ph)
        lowest = m.arr[f"{side}_foot"][:, 1].min()
        dx = (f[0] - h[0]) * self.s * self.stride
        up = (f[1] - lowest) * self.s * rig.get("lift", 1.0)          # the sole's height over the ground
        return np.array([hip[0] + dx, rig["ground"] - up])

    def _bob(self, ph):
        return (self.m.at("pelvis", ph)[1] - self.pel_mean) * self.s * self.rig.get("bob", 1.0)

    def _fit_height(self):
        """The hip's middle height: the planted foot reaches the ground through the middle of its stance (REACH_Q of
        the planted samples; at landing and push-off it may hang a square over it, the heel or the toe down)."""
        rig = self.rig
        hs = []
        for k in range(self.m.n):
            ph = k / self.m.n
            for key in ("near", "far"):
                side = rig["sides"][key]
                if not self.m.stance(side)[k]:
                    continue
                hx = rig["hips"][key][0]
                sole = self._sole(key, ph, (hx, 0.0))
                reach = rig.get("reach", 0.97) * (rig["thigh"][key] + rig["shin"][key])
                dx = sole[0] - hx
                need = math.sqrt(max(0.0, reach * reach - dx * dx))     # hip at most this high over the sole
                hs.append(need - self._bob(ph))
        stand = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        return min(float(np.percentile(hs, rig.get("reach_q", 30))), stand + rig.get("rise", 0.0))

    def pose_dy_f(self, i, lag):
        """The body's sink (squares, down +) `lag` of a cycle before frame i (what trails it is where it was)."""
        rig = self.rig
        ph = (self.phase(i) - lag) % 1.0
        stand = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        return float(stand - (self.h_mid + self._bob(ph)))

    def pose(self, i):
        """-> {"ph", "dy": the body's rows (down +), "dx", "legs": {key: (hip, knee, sole)}}."""
        rig = self.rig
        ph = self.phase(i)
        h = self.h_mid + self._bob(ph)
        stand = rig["ground"] - np.mean([rig["hips"][k][1] for k in ("near", "far")])
        dy = stand - h                                                 # the body sinks this many squares
        dx = (self.m.at("pelvis", ph)[0] - self.sway_mean) * self.s * rig.get("sway", 1.0)
        legs = {}
        for key in ("near", "far"):
            hx, hy = rig["hips"][key]
            hip = np.array([hx + dx, hy + dy])
            sole = self._sole(key, ph, hip)
            planted = sole[1] >= rig["ground"] - 0.5
            sole[1] = min(sole[1], rig["ground"])
            knee, end = ik(hip, sole, rig["thigh"][key], rig["shin"][key])
            legs[key] = (hip, knee, end, planted)
        return {"ph": ph, "dy": dy, "dx": dx, "legs": legs}


# ================================================================================================== the heroes
class JinxRun:
    """league_jinx from her design's parts (tools/art/rig_jinx_hd.py masks): the stocking thighs laid along the bone
    as her rig lays them, the boots turned with the shin, the braids and Fishbones following through."""
    hero = "jinx"
    ppu = 2.2

    def __init__(self):
        import rig_jinx_hd as JX
        self.JX = JX
        self.d = np.asarray(Image.open(lp(os.path.join(ROOT, "assets", "source", "jinx", "hd", "design.png")))
                            .convert("RGBA")).copy()
        d = self.d
        self.M = JX.masks(d)
        self.pieces = {n: piece(d, m) for n, m in self.M.items()}
        self.legs = JX.Legs(d, self.M)
        self.outline = JX.O
        self.pivot = (JX.PIVOT_COL, JX.GROUND)          # the pivot column, the soles' bottom edge
        # the sole's contact point of each boot (its middle on the ground) and the knee it hangs from
        self.contact = {"near": (28.0, JX.GROUND), "far": (58.0, JX.GROUND)}
        hip_y = JX.RUN_HIP_Y
        self.rig = dict(ground=JX.GROUND, height=JX.GROUND - 0.0,
                        hips={"near": (JX.RUN_HIP_X["near"], hip_y), "far": (JX.RUN_HIP_X["far"], hip_y)},
                        thigh={"near": JX.RUN_LT["near"], "far": JX.RUN_LT["far"]},
                        shin={k: float(np.hypot(*np.subtract(self.contact[k], JX.KNEE[k]))) for k in ("near", "far")},
                        sides={"near": "l", "far": "r"}, bob=0.4, reach=0.98, sway=0.0,
                        # League's own cycle (0.933 s) in `frames` frames, the stride a set share wider than League's;
                        # the bob kept to a square a frame at most and no sideways sway: a whole-body shift of 2
                        # squares between frames is a jump (「帧和帧之间跳」)
                        frames=14, cycle="league", stride=1.45,
                        # the lean: columns a row over the hips, the same in every frame; the head bobs
                        # (1 - head_counter) of the hips; the gun unit stays gun_lag of where the body was a frame
                        # ago (a square at most); the braids (middle, tip) stream back by braid_base and swing
                        # braid_gain x League's chain
                        lean=0.06, head_counter=0.45, gun_lag=1.0,
                        braid_base={"n": (-3, -8), "f": (-5, -14)}, braid_gain=2.8, fish_lag=1.0)
        self.boots = {k: Boot(*self.legs.boot[k], JX.KNEE[k], self.contact[k], self.outline) for k in ("near", "far")}

    # what holds the gun moves with it: the gun, both hands, forearms and arms are one rigid unit (the user on v3:
    # 「手和武器严重脱节」) - nothing in it slides on another
    GUN_UNIT = ("gun", "arm_lo", "arm_f", "arm_n")

    def signals(self, g, pose, i):
        """The upper body's moves at this frame from League's joints, all by whole squares (no part is turned: a
        small turn re-pixelled every frame shimmers, 「帧和帧之间跳」): the head bobbing less than the hips, the
        gun unit a frame behind the body (at most one square), Fishbones a frame behind, the braids bent through
        League's hair chains (their middle and tip under the head, about their mean)."""
        m, ph, s = g.m, pose["ph"], g.s
        rig = self.rig
        head_dy = int(round(-rig["head_counter"] * pose["dy"]))
        late = g.pose_dy_f(i, 1.0 / g.n) - pose["dy"]           # where the body was a frame ago
        gun_dy = int(max(-1, min(1, round(rig["gun_lag"] * late))))
        braids = {}
        for key, side in (("n", "r"), ("f", "l")):
            def off(j):
                v = m.at(f"{side}_{j}", ph) - m.at("head", ph)
                v0 = m.mean(f"{side}_{j}") - m.mean("head")
                return (v[1] - v0[1]) * s
            base_mid, base_tip = rig["braid_base"][key]
            braids[key] = (int(round(base_mid - rig["braid_gain"] * 0.5 * off("hair3"))),
                           int(round(base_tip - rig["braid_gain"] * off("hair6"))))
        return dict(head_dy=head_dy, gun_dy=gun_dy, fish_dy=int(round(rig["fish_lag"] * late)), braids=braids)

    def frame(self, g, pose, i, only=None):
        JX = self.JX
        d = self.d
        can = Canvas(d.shape, 50)
        Z = JX.Z
        bdx, bdy = int(round(pose["dx"])), int(round(pose["dy"]))
        sg = self.signals(g, pose, i)
        hip_row = self.rig["hips"]["near"][1]
        lean = self.rig["lean"]                                   # the same rows shifted in every frame
        kn, kf = sg["braids"]["n"], sg["braids"]["f"]
        items = []
        for name in JX.PARTS:
            if name in ("leg_r", "leg_f") or (only is not None and name not in only):
                continue
            img, at = self.pieces[name]
            x, y = at
            dy = 0
            if name == "braid_n":
                img, (x, y) = bent(img, at, at[1] + 5, kn[0], kn[1])
                dy = sg["head_dy"]
            elif name == "braid_f":
                img, (x, y) = bent(img, at, at[1] + 3, kf[0], kf[1])
                dy = sg["head_dy"]
            elif name == "curl":
                x, y = x + JX.CURL_ON[0] + kf[1], y + JX.CURL_ON[1]
                dy = sg["head_dy"]
            elif name == "head":
                dy = sg["head_dy"]
            elif name in self.GUN_UNIT:
                dy = sg["gun_dy"]
            elif name == "fish":
                dy = sg["fish_dy"]
            img, (x, y) = leant(img, (x, y), lean, hip_row)
            items.append((Z[name], img, (x + bdx, y + bdy + dy)))
        for z, img, at in sorted(items, key=lambda t: t[0]):
            can.stamp(img, at, z)
        # the legs: the boot down on its sole at a held angle, the stocking thigh from the hip to the knee it gives
        for key, zname in (("far", "leg_f"), ("near", "leg_r")):
            hip, _, end, planted = pose["legs"][key]
            knee, out, oat, _ = self.boots[key].place(hip, self.rig["thigh"][key], self.rig["shin"][key], end,
                                                     self.rig["ground"], planted)
            cells = JX.fold(self.legs.thigh(key, tuple(hip), tuple(knee)))
            timg, tx, ty = JX.cells_img(cells)
            can.stamp(timg, (tx, ty), Z[zname])
            can.stamp(out, oat, Z[zname] + 0.1)
        return can


def poly_mask(shape, pts):
    """Squares whose centre lies inside the polygon pts [(x, y), ...] (square edges)."""
    img = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(img).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=1, outline=1)
    return np.asarray(img, bool)


def colour_mask(d, cols, tol=0):
    rgb = d[..., :3].astype(int)
    m = np.zeros(d.shape[:2], bool)
    for c in cols:
        m |= (np.abs(rgb - np.array(c)).sum(-1) <= tol)
    return m & (d[..., 3] > 0)


class LegArt:
    """A leg drawn from the design: the thigh's rows (cross-sections of a thigh the design shows whole) laid along
    hip -> knee (league_jinx's Legs.thigh), the shin and boot the design's own, turned with the shin about the knee.
    rows: (mask, row0, row1) the thigh's squares; shin: (mask) the shin + boot squares; knee, contact: the shin's top
    and its sole's middle on the ground (design squares, edges)."""

    def __init__(self, d, thigh_mask, rows, shin_mask, knee, contact, outline):
        self.outline = outline
        self.slices = []
        dark = (IB_lum(d[..., :3]) < DARK)
        for y in range(rows[0], rows[1] + 1):
            xs = np.nonzero(thigh_mask[y] & ~dark[y])[0]
            if len(xs):
                self.slices.append(d[y, xs.min():xs.max() + 1].copy())
        self.shin = piece(d, shin_mask)
        self.knee = np.array(knee, float)
        self.contact = np.array(contact, float)
        self.rest = angle_down(self.contact - self.knee)
        self.boot = Boot(*self.shin, knee, contact, outline)

    def thigh(self, H, K):
        """{(x, y): rgba} the thigh along H -> K (design squares, edges), its rows along it, the outline round it."""
        H, K = np.asarray(H, float), np.asarray(K, float)
        v = K - H
        L = max(1e-6, float(np.hypot(*v)))
        u = v / L
        n = np.array((u[1], -u[0]))
        cells = {}
        for y in range(int(math.floor(min(H[1], K[1]))) - 8, int(math.ceil(max(H[1], K[1]))) + 8):
            for x in range(int(math.floor(min(H[0], K[0]))) - 8, int(math.ceil(max(H[0], K[0]))) + 8):
                q = np.array((x + 0.5, y + 0.5)) - H
                t, s_ = float(q @ u), float(q @ n)
                if t < -1.5 or t > L + 1.0:
                    continue
                row = self.slices[int(round(min(1.0, max(0.0, t / L)) * (len(self.slices) - 1)))]
                xi = int(math.floor(len(row) / 2 + s_))
                if 0 <= xi < len(row) and row[xi][3]:
                    cells[(x, y)] = row[xi]
        out = dict(cells)
        for (x, y) in list(cells):
            for ddx, ddy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (x + ddx, y + ddy) not in cells:
                    out.setdefault((x + ddx, y + ddy), np.array((*self.outline, 255), np.uint8))
        xs = [x for x, _ in out]
        ys = [y for _, y in out]
        x0, y0 = min(xs), min(ys)
        img = np.zeros((max(ys) - y0 + 1, max(xs) - x0 + 1, 4), np.uint8)
        for (x, y), c in out.items():
            img[y - y0, x - x0, :3] = np.asarray(c)[:3]
            img[y - y0, x - x0, 3] = 255
        return img, (x0, y0)

def IB_lum(rgb):
    rgb = rgb.astype(np.float32)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


class PartRun:
    """A hero cut into parts by polygons (and colours) on the design: the body moved by whole squares (bob, sway,
    lean), parts with moves of their own (an arm's swing, a beat late), what hangs waved, the legs LegArt. A square a
    moved part bares inside the figure is filled from round it (ppu_rig.fill_under); the outline closed again."""
    hero = None
    ppu = None
    outline = None
    PARTS = []          # [(name, polygon | box (x0, y0, x1, y1), colours to leave out or None)] in claiming order
    Z = {}
    REST = "body"

    def __init__(self):
        self.d = np.asarray(Image.open(lp(os.path.join(ROOT, "assets", "source", self.hero, "hd", "design.png")))
                            .convert("RGBA")).copy()
        d = self.d
        op = d[..., 3] > 0
        taken = np.zeros(op.shape, bool)
        self.M = {}
        for name, shape, leave in self.PARTS:
            if len(shape) == 4 and all(isinstance(v, (int, float)) for v in shape):
                x0, y0, x1, y1 = shape
                m = np.zeros(op.shape, bool)
                m[max(0, y0):y1 + 1, max(0, x0):x1 + 1] = True
            else:
                m = poly_mask(op.shape, shape)
            m &= op & ~taken
            if isinstance(leave, dict):
                m &= colour_mask(d, leave["keep"])
            elif leave:
                m &= ~colour_mask(d, leave)
            self.M[name] = m
            taken |= m
        self.M[self.REST] = op & ~taken
        self.pieces = {n: piece(d, m) for n, m in self.M.items() if m.any()}
        self.holes0 = ndimage.binary_fill_holes(op) & ~op

    def parts_png(self, path, z=8):
        tints = [(255, 0, 0), (0, 160, 255), (0, 200, 0), (255, 200, 0), (200, 0, 255), (255, 120, 0), (0, 255, 200),
                 (120, 60, 0), (255, 0, 160)]
        img = np.zeros(self.d.shape[:2] + (3,), np.uint8) + 230
        for k, (name, m) in enumerate(self.M.items()):
            img[m] = (self.d[m, :3] * 0.45 + np.array(tints[k % len(tints)]) * 0.55).astype(np.uint8)
        Image.fromarray(img).resize((img.shape[1] * z, img.shape[0] * z), Image.NEAREST).save(path)
        print(path, {n: int(m.sum()) for n, m in self.M.items()})

    def frame(self, g, pose, i, only=None):
        """The parts put down in their order, each: waved (`wave`: ("lift", k, x_free, x_root) by columns,
        ("shear", k, pivot_row) or ("bent", root_row, k_mid, k_tip) by rows), turned about a joint (`rot`: (joint,
        degrees counter-clockwise), RotSprite's way), moved (`dx`, `dy`), leant with the upper body and moved with
        it; then the legs."""
        d = self.d
        can = Canvas(d.shape, 50)
        bdx, bdy = int(round(pose["dx"])), int(round(pose["dy"]))
        spec = self.pose_parts(g, pose, i)
        lean = spec.pop("_lean", None)
        if lean is None:
            lean = self.lean(g, pose["ph"])
        hip_row = np.mean([self.rig["hips"][k][1] for k in ("near", "far")])
        items = []
        for name, (img, at) in self.pieces.items():
            if name.startswith("leg_") or (only is not None and name not in only):
                continue
            t = spec.get(name, {})
            x, y = at
            w = t.get("wave")
            if w and w[0] == "lift" and w[1]:
                img, (x, y) = lifted(img, (x, y), w[1], w[2], w[3])
            elif w and w[0] == "shear" and w[1]:
                img, (x, y) = sheared(img, (x, y), w[1], w[2])
            elif w and w[0] == "bent":
                img, (x, y) = bent(img, (x, y), w[1], w[2], w[3])
            r = t.get("rot")
            if r and abs(r[1]) >= 0.5:
                img, (x, y) = turned(img, (x, y), r[0], r[0], r[1], self.outline)
            if not t.get("still"):
                img, (x, y) = leant(img, (x, y), lean, hip_row)
                x, y = x + bdx, y + bdy
            items.append((self.Z[name], img, (x + int(round(t.get("dx", 0))), y + int(round(t.get("dy", 0))))))
        for z, img, at in sorted(items, key=lambda q: q[0]):
            can.stamp(img, at, z)
        for key in ("far", "near"):
            hip, _, end, planted = pose["legs"][key]
            art = self.legs[key]
            knee, shin, sat, _ = art.boot.place(hip, self.rig["thigh"][key], self.rig["shin"][key], end,
                                                self.rig["ground"], planted)
            z = self.Z[f"leg_{key}"]
            if self.rig.get("thighs", True):
                timg, tat = art.thigh(hip, knee)
                can.stamp(timg, tat, z)
            can.stamp(shin, sat, z + 0.1)
        return can

    def pose_parts(self, g, pose, i):
        """{part: {"dx", "dy", "rot", "wave", "still"}} and "_lean" (the hero's own)."""
        return {}

    # ---- League's joints as moves (shared by the heroes)
    @staticmethod
    def spine_lean(g, ph, base, gain):
        """Columns a row over the hips: `base` plus `gain` of League's spine swing (pelvis -> chest) about its mean."""
        m = g.m
        mean = float(np.mean([angle_up(r) for r in m.arr["chest"] - m.arr["pelvis"]]))
        return base + math.tan(math.radians(gain * wrap180(angle_up(m.at("chest", ph) - m.at("pelvis", ph)) - mean)))

    @staticmethod
    def swing(g, ph, a, b, gain):
        """Degrees counter-clockwise on screen: `gain` of League's a -> b (an arm, a staff) turn about its mean."""
        m = g.m
        mean = float(np.mean([angle_up(r) for r in m.arr[b] - m.arr[a]]))
        return -gain * wrap180(angle_up(m.at(b, ph) - m.at(a, ph)) - mean)

    @staticmethod
    def rel(g, ph, name, to, k):
        """A joint's offset from another (League px x the scale -> squares, axis k: 0 forward, 1 up) about its mean."""
        m = g.m
        v = m.at(name, ph) - m.at(to, ph)
        v0 = m.mean(name) - m.mean(to)
        return (v[k] - v0[k]) * g.s

    def lean(self, g, ph):
        return self.spine_lean(g, ph, self.rig.get("lean", 0.0), self.rig.get("lean_gain", 0.0))

    def finish(self, can):
        """Holes the moves bared inside the figure (not the design's own gaps) filled from round them; the outline
        closed (ppu_rig.tidy)."""
        a = can.a
        p = can.pad
        op = a[..., 3] > 0
        own = np.zeros(op.shape, bool)
        own[p:p + self.d.shape[0], p:p + self.d.shape[1]] = self.holes0
        holes = ndimage.binary_fill_holes(op) & ~op & ~ndimage.binary_dilation(own, iterations=1)
        lab, n = ndimage.label(holes)
        for j in range(1, n + 1):
            h = lab == j
            if h.sum() <= self.FILL_MAX:
                a = R.fill_under(a, h)
        return R.tidy(a, self.outline)

    FILL_MAX = 60


VI_HAIR = [(232, 54, 124), (249, 100, 164), (205, 40, 105), (170, 27, 83), (141, 19, 67), (116, 16, 56),
           (176, 60, 102), (91, 17, 47)]


class ViRun(PartRun):
    """league_vi: the design cut into her two gauntlets (the near one low at her hip, the far one raised), the head
    (her hair streaming back), the body and the legs; the gauntlets pump with League's hands, the hair waves."""
    hero = "vi"
    ppu = 73 / 40
    outline = (26, 12, 16)
    PARTS = [
        ("fist_near", [(0, 25), (11, 20), (21, 20), (23, 28), (23, 52), (20, 58), (0, 58)], VI_HAIR),
        ("fist_far", [(36, 13), (53, 13), (53, 43), (37, 43), (33, 38), (33, 24), (35, 21)], None),
        ("leg_far", [(29, 45), (46, 45), (47, 55), (53, 61), (53, 74), (31, 74), (31, 56)], None),
        ("leg_near", [(0, 56), (17, 56), (17, 74), (0, 74)], None),
        ("head", [(0, 0), (40, 0), (40, 13), (36, 22), (33, 26), (24, 29), (14, 29), (0, 29)], None),
    ]
    Z = {"leg_far": 1, "body": 2, "head": 3, "fist_far": 4, "leg_near": 5, "fist_near": 6}

    def __init__(self):
        super().__init__()
        d = self.d
        o = self.outline
        far, near = self.M["leg_far"], self.M["leg_near"]
        self.legs = {
            "far": LegArt(d, far, (46, 55), far & (np.arange(d.shape[0])[:, None] >= 55), (39.0, 55.5), (43.0, 73.0), o),
            "near": LegArt(d, far, (46, 55), near & (np.arange(d.shape[0])[:, None] >= 57), (9.0, 58.0), (6.0, 73.0), o),
        }
        ground = 73.0
        hips = {"far": (34.0, 47.0), "near": (22.0, 47.0)}
        total = (ground - hips["far"][1]) * 1.04
        shin = {k: float(np.hypot(*(self.legs[k].contact - self.legs[k].knee))) for k in ("far", "near")}
        self.rig = dict(ground=ground, height=ground, hips=hips, shin=shin,
                        thigh={k: total - shin[k] for k in ("far", "near")},
                        sides={"near": "l", "far": "r"}, bob=0.45, reach=0.98, sway=0.0,
                        frames=14, cycle="league", stride=1.5,
                        lean=0.05, head_counter=0.45, hair_trail=1.6,
                        # squares of gauntlet move per League px of glove move against the chest (forward, up)
                        pump={"near": (0.45, 0.55), "far": (0.35, 0.45)})

    def pose_parts(self, g, pose, i):
        """By whole squares only (no turn: 「帧和帧之间跳」): each gauntlet - the hand itself, with its forearm -
        pumping with League's glove against her chest, the head bobbing less than the hips, her hair's free end
        trailing the body by a beat."""
        ph, rig = pose["ph"], self.rig
        out = {}
        for part, side, (gx, gy) in (("fist_near", "l", rig["pump"]["near"]), ("fist_far", "r", rig["pump"]["far"])):
            out[part] = {"dx": int(round(gx * self.rel(g, ph, f"{side}_hand", "chest", 0))),
                         "dy": int(round(-gy * self.rel(g, ph, f"{side}_hand", "chest", 1)))}
        trail = pose["dy"] - g.pose_dy_f(i, 1.5 / g.n)          # how far the body went down since 1.5 frames ago
        out["head"] = {"dy": int(round(-rig["head_counter"] * pose["dy"])),
                       "wave": ("lift", int(round(rig["hair_trail"] * trail)), 3, 21)}
        out["_lean"] = rig["lean"]
        return out


RUNS = {"jinx": JinxRun, "vi": ViRun}


# ================================================================================================== the sheet
TAGS = ("run", "hd_run", "lo_run")


def rect_of(f):
    return tuple(int(round(f["data"][k])) for k in ("x", "y", "w", "h"))


def read_sheet(hero):
    import ppu_hd
    stem = ppu_hd.stem_of(hero)
    with open(lp(stem + "#anim.fanim"), encoding="utf-8-sig") as f:
        an = json.load(f)
    px = np.array(Image.open(lp(stem + "#sheet.png")).convert("RGBA"))
    return stem, an, px


def frame_px(px, f):
    x, y, w, h = rect_of(f)
    return px[y:y + h, x:x + w].copy()


def idle_frame(hero):
    """The hero's dense standing frame as the game draws it (hd_idle_base[0]: the design held still)."""
    _, an, px = read_sheet(hero)
    return frame_px(px, an["anims"]["hd_idle_base"]["frames"][0])


def pivot_of(hero, d):
    """The pivot (every frame's centre) in design squares (edges): where the hero's own dense idle_base frame (the
    design held still) has it - the run's frames stand exactly where the rest of the hero's do."""
    _, an, px = read_sheet(hero)
    b = frame_px(px, an["anims"]["hd_idle_base"]["frames"][0])
    m = d[..., 3] > 0
    best = None
    for oy in range(0, b.shape[0] - d.shape[0] + 1):
        for ox in range(0, b.shape[1] - d.shape[1] + 1):
            sub = b[oy:oy + d.shape[0], ox:ox + d.shape[1]]
            same = int((sub[m] == d[m]).all(-1).sum())
            if best is None or same > best[0]:
                best = (same, ox, oy)
    same, ox, oy = best
    if same < 0.97 * m.sum():
        sys.exit(f"{hero}: hd_idle_base[0] does not hold the design ({same} of {int(m.sum())} squares)")
    return b.shape[1] / 2 - ox, b.shape[0] / 2 - oy


def dense_frames(frames, pad, pivot, ppu):
    """The composed canvases (design squares + pad) cut to one size about the pivot: every frame centred on it, as
    wide and tall as the widest reach of any of them (so no frame's centre falls half a square off another's).
    -> ([dense frames], (w1, h1) the 1x size)."""
    px, py = pivot[0] + pad, pivot[1] + pad
    allop = np.stack([f[..., 3] > 0 for f in frames]).any(0)
    ys, xs = np.nonzero(allop)
    hw = max(px - xs.min(), xs.max() + 1 - px)
    hh = max(py - ys.min(), ys.max() + 1 - py)
    hw1 = int(math.ceil(hw / ppu - 0.5))
    hh1 = max(int(math.ceil(hh / ppu - 0.5)), int(math.ceil(R.FEET)) + 1)
    w1, h1 = 2 * hw1 + 1, 2 * hh1 + 1
    W, H = round(w1 * ppu), round(h1 * ppu)
    while abs((px - W / 2) - round(px - W / 2)) > 1e-6 or W / 2 < hw:
        W += 1
    while abs((py - H / 2) - round(py - H / 2)) > 1e-6 or H / 2 < hh:
        H += 1
    x0, y0 = int(round(px - W / 2)), int(round(py - H / 2))
    out = []
    for f in frames:
        b = np.zeros((H, W, 4), np.uint8)
        sx0, sy0 = max(0, x0), max(0, y0)
        sub = f[sy0:min(f.shape[0], y0 + H), sx0:min(f.shape[1], x0 + W)]
        b[sy0 - y0:sy0 - y0 + sub.shape[0], sx0 - x0:sx0 - x0 + sub.shape[1]] = sub
        out.append(b)
    return out, (w1, h1)


def one_frames(hero, dense, size, ppu):
    """The 1x frames from the dense ones as tools/art/ppu_one.py brings them down (pixel_down.pixelate, centred),
    on a rect of the 1x size grown alike at both ends where the drawing needs it."""
    import ppu_one
    w1, h1 = size
    out = []
    for b in dense:
        ws = [w1 + 2 * k for k in range(0, 6)]
        hs = [h1 + 2 * k for k in range(0, 6)]
        f, off = ppu_one.one_frame(b, w1, h1, 1.0 / ppu, ws, hs)
        if off:
            sys.exit(f"{hero}: a 1x run frame loses {off} squares off its rect")
        out.append(f)
    W = max(f.shape[1] for f in out)
    H = max(f.shape[0] for f in out)
    same = []
    for f in out:                                       # one size for all, grown alike at both ends
        g_ = np.zeros((H, W, 4), np.uint8)
        oy, ox = (H - f.shape[0]) // 2, (W - f.shape[1]) // 2
        g_[oy:oy + f.shape[0], ox:ox + f.shape[1]] = f
        same.append(g_)
    return same


def lo_frames(hero, ones, dense, ms):
    """lo_run the way tools/art/ppu_hd.py makes every lo_ tag (add_lo) from the hd_ one."""
    import ppu_hd
    mini = {"run": list(zip(ones, ms)), "hd_run": list(zip(dense, ms))}
    ppu_hd.add_lo(hero, mini)
    return [f for f, _ in mini["lo_run"]]


def strip(frames):
    Hm = max(h.shape[0] for h in frames)
    out = np.zeros((Hm, sum(h.shape[1] + 1 for h in frames) - 1, 4), np.uint8)
    x = 0
    for h in frames:
        out[:h.shape[0], x:x + h.shape[1]] = h
        x += h.shape[1] + 1
    return out


def write_strips(hero, dense, ppu, orig=None):
    """assets/source/ppu/<hero>_run.png (+ .json sizes): the strip tools/art/ppu_hd.py reads for hd_run (so its run
    writes these frames again); `orig`: the frames before the outline pass, into ppu/orig/ for tools/art/ppu_restyle.py
    (a restyle run then starts from these, not the old run)."""
    for folder, fr in ((os.path.join(ROOT, "assets", "source", "ppu"), dense),
                       (os.path.join(ROOT, "assets", "source", "ppu", "orig"), orig)):
        if fr is None:
            continue
        Image.fromarray(strip(fr), "RGBA").save(lp(os.path.join(folder, f"{hero}_run.png")), optimize=True)
        with open(lp(os.path.join(folder, f"{hero}_run.json")), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"sizes": [[h.shape[1], h.shape[0]] for h in fr], "ppu": ppu}, f)


def place(px, anims, drop, new):
    """The sheet with the tags in `drop` taken off (their squares cleared where no other tag uses them) and `new`
    ({tag: [(frame, ms)]}) put in the free room - top-left first, 1 clear square between frames, no wider than the
    sheet; every other tag's frames stay exactly where they are. -> (sheet, anims)."""
    keep = {rect_of(f) for t, a in anims.items() if t not in drop for f in a["frames"]}
    gone = {rect_of(f) for t in drop if t in anims for f in anims[t]["frames"]} - keep
    px = px.copy()
    for x, y, w, h in gone:
        px[y:y + h, x:x + w] = 0
    Ws = px.shape[1]
    total_h = px.shape[0] + sum(f.shape[0] + 1 for fr in new.values() for f, _ in fr)
    occ = np.zeros((total_h, Ws), bool)
    for x, y, w, h in keep:
        occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
    out_px = np.zeros((total_h, Ws, 4), np.uint8)
    out_px[:px.shape[0]] = px
    anims = {t: a for t, a in anims.items()}
    for tag, fr in new.items():
        rows = []
        for f, ms in fr:
            h, w = f.shape[:2]
            ii = np.pad(np.cumsum(np.cumsum(occ.astype(np.int32), 0), 1), ((1, 0), (1, 0)))
            s_ = ii[h:, w:] - ii[:-h, w:] - ii[h:, :-w] + ii[:-h, :-w]       # occupied squares in each h x w box
            free = np.argwhere(s_ == 0)
            if not len(free):
                sys.exit(f"{tag}: no room for a {w}x{h} frame")
            y, x = free[0]
            out_px[y:y + h, x:x + w] = f
            occ[max(0, y - 1):y + h + 1, max(0, x - 1):x + w + 1] = True
            rows.append({"duration": round(ms / 1000.0, 6), "data": {"x": float(x), "y": float(y), "w": float(w),
                                                                     "h": float(h)}})
        anims[tag] = {"frames": rows}
    used = [rect_of(f) for a in anims.values() for f in a["frames"]]
    H = max(y + h for x, y, w, h in used)
    W = max(x + w for x, y, w, h in used)
    return out_px[:H, :W], anims


def write_sheet(hero, new, drop=TAGS):
    """The run tags into the hero's sheet (place); the fanim keeps every other tag as it was, in its order."""
    stem, an, px = read_sheet(hero)
    order = list(an["anims"])
    sheet, anims = place(px, an["anims"], drop, new)
    for t in drop:                                      # (dropped tags not made again leave the table)
        if t not in new:
            anims.pop(t, None)
    an["anims"] = {t: anims[t] for t in order if t in anims}
    for t in anims:
        if t not in an["anims"]:
            an["anims"][t] = anims[t]
    Image.fromarray(sheet, "RGBA").save(lp(stem + "#sheet.png"), optimize=True)
    with open(lp(stem + "#anim.fanim"), "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(an, ensure_ascii=False, separators=(",", ":")))
    return sheet.shape[1], sheet.shape[0]


# ================================================================================================== frames
LOOSE = 20              # squares: a piece apart from the figure smaller than this is a crumb a turn left (Pix is ~115)


def finish(rig, can):
    """The composed squares: stray outline squares (a turned corner) gone, the outline closed round what moved, crumbs
    a turn or a wave cut loose dropped."""
    if hasattr(rig, "finish"):
        a = rig.finish(can)
    else:
        a = R.tidy(rig.JX.drop_stray_outline(can.a), rig.outline)
    lab, n = ndimage.label(a[..., 3] > 0, structure=np.ones((3, 3)))
    if n > 1:
        sz = ndimage.sum(a[..., 3] > 0, lab, range(1, n + 1))
        for j in range(1, n + 1):
            if sz[j - 1] < LOOSE:
                a[lab == j] = 0
    return a


def build(hero, n=N_FRAMES, cycle_s=None, only=None):
    run = RUNS[hero]()
    g = Gait(hero, run.rig, run.ppu, n, cycle_s)
    frames = []
    for i in range(n):
        pose = g.pose(i)
        can = run.frame(g, pose, i, only)
        frames.append(finish(run, can))
    return run, g, frames


def review(hero, out_dir, n=N_FRAMES, cycle_s=None, legs=False):
    run, g, frames = build(hero, n, cycle_s)
    rows = [frames]
    if legs:                                            # the legs alone under the frames (to read their poses)
        rows.append(build(hero, n, cycle_s, only=())[2])
    os.makedirs(out_dir, exist_ok=True)
    pad = 50
    allop = np.stack([f[..., 3] > 0 for f in frames]).any(0)
    ys, xs = np.nonzero(allop)
    y0, y1, x0, x1 = ys.min() - 2, ys.max() + 3, xs.min() - 2, xs.max() + 3
    gy = int(run.rig["ground"]) + pad
    z = 4
    grid = []
    for fr in rows:
        tiles = []
        for f in fr:
            bg = Image.new("RGBA", (x1 - x0, y1 - y0), (96, 112, 96, 255))
            bg.alpha_composite(Image.fromarray(f[y0:y1, x0:x1]))
            dr = ImageDraw.Draw(bg)
            dr.line([(0, gy - y0), (x1 - x0, gy - y0)], fill=(70, 86, 70, 255))
            tiles.append(bg.resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
        grid.append(tiles)
    tw, th = grid[0][0].width, grid[0][0].height
    sheet = Image.new("RGB", (n * (tw + 6), len(grid) * (th + 6)), (40, 40, 40))
    for r, tiles in enumerate(grid):
        for i, t in enumerate(tiles):
            sheet.paste(t, (i * (tw + 6), r * (th + 6)))
    sheet.save(os.path.join(out_dir, f"{hero}_run_new.png"))
    tiles = grid[0]
    gif = [t.convert("RGB").quantize(255) for t in tiles]
    gif[0].save(os.path.join(out_dir, f"{hero}_run_new.gif"), save_all=True, append_images=gif[1:],
                duration=g.ms, loop=0)
    print(f"{hero}: {n} frames of {g.ms[0]} ms ({g.cycle_s:.3f} s), stride x{g.stride:.2f}, scale {g.s:.3f} sq/px, "
          f"hip middle {g.h_mid:.1f}")
    for i in range(n):
        p = g.pose(i)
        print(f"  {i}: ph {p['ph']:.3f} dy {p['dy']:+.1f} dx {p['dx']:+.1f} " + " ".join(
            f"{k}: sole ({v[2][0]:.1f},{v[2][1]:.1f}) knee ({v[1][0]:.1f},{v[1][1]:.1f})" for k, v in p["legs"].items()))


def pinholes(a, most=3):
    """Labels of the enclosed clear holes of at most `most` squares."""
    op = a[..., 3] > 0
    lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
    return [lab == j for j in range(1, n + 1) if (lab == j).sum() <= most]


def filled(a, most=3):
    """Pinholes filled with the commonest colour round them (ppu_rig.tidy's way) - for a hero whose design has none:
    the downscale to the UI's density (ppu_hd.add_lo) leaves one where two edges come within a square."""
    out = a.copy()
    for h in pinholes(a, most):
        ring = ndimage.binary_dilation(h, structure=np.ones((3, 3))) & (out[..., 3] > 0)
        cols, cnt = np.unique(out[ring][:, :3], axis=0, return_counts=True)
        out[h, :3] = cols[cnt.argmax()]
        out[h, 3] = 255
    return out


def outlined(hero, frames, kind):
    """The hero's outline round the frames as its other frames have it: grown to KEEP squares (thin_outline.json,
    the restyle's edge did it for the rest - the design's own outline is a square thinner); thin_outline.py then
    finds nothing to change (or only what it changes everywhere)."""
    import thin_outline as T
    with open(lp(T.STATE), encoding="utf-8") as f:
        st = json.load(f)[f"league_{hero}"]
    oc, keep, colour = st["outline"], st[kind]["keep"], st["grow"]
    out = []
    for a in frames:
        b = T.grow_ring(a, oc, keep, colour)[0]
        # a notch's mouth or an opening (the inside of a curl) the new ring closed down to a pinhole inside the
        # figure: outline, as the ring round it - the drawing's own pinholes (league_jinx's design has some) stay
        ah = ndimage.binary_fill_holes(a[..., 3] > 0) & ~(a[..., 3] > 0)
        al, an_ = ndimage.label(ah)
        before = np.zeros(ah.shape, bool)
        for j in range(1, an_ + 1):
            if (al == j).sum() <= 6:
                before |= al == j
        op = b[..., 3] > 0
        lab, n = ndimage.label(ndimage.binary_fill_holes(op) & ~op)
        for j in range(1, n + 1):
            h = lab == j
            if h.sum() <= 6 and not (h & before).any():
                b[h, :3] = colour
                b[h, 3] = 255
        out.append(b)
    return out


def export(hero, n=N_FRAMES, cycle_s=None, dry=False):
    """The run tags made and written (unless dry) -> {"run", "hd_run", "lo_run": frames, "ms", "gait", "pivot"}."""
    run, g, frames = build(hero, n, cycle_s)
    pad = (frames[0].shape[0] - run.d.shape[0]) // 2
    pivot = pivot_of(hero, run.d)
    drawn, size = dense_frames(frames, pad, pivot, run.ppu)
    dense = outlined(hero, drawn, "hd")
    ones = one_frames(hero, dense, size, run.ppu)
    lo = outlined(hero, lo_frames(hero, ones, dense, g.ms), "lo")
    if not pinholes(idle_frame(hero)):                  # (a hero whose standing frame has no pinholes: none here)
        lo = [filled(a) for a in lo]
        ones = [filled(a) for a in ones]
    out = {"run": ones, "hd_run": dense, "lo_run": lo, "ms": g.ms, "gait": g, "pivot": pivot}
    if dry:
        return out
    write_strips(hero, dense, run.ppu, orig=drawn)
    w, h = write_sheet(hero, {t: list(zip(out[t], g.ms)) for t in TAGS})
    print(f"league_{hero}#sheet.png {w}x{h}: run / hd_run / lo_run {n} frames of {g.ms[0]} ms "
          f"(1x {ones[0].shape[1]}x{ones[0].shape[0]}, hd {dense[0].shape[1]}x{dense[0].shape[0]}, "
          f"lo {lo[0].shape[1]}x{lo[0].shape[0]})")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["motion", "build", "parts"])
    ap.add_argument("--hero", action="append", required=True)
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--review")
    ap.add_argument("--frames", type=int, default=N_FRAMES)
    ap.add_argument("--cycle", type=float)
    ap.add_argument("--legs", action="store_true", help="--review: the legs alone in a second row")
    ap.add_argument("--dry", action="store_true", help="make the frames, write nothing")
    a = ap.parse_args()
    for hero in a.hero:
        if a.what == "motion":
            m = extract(hero, a.lol)
            write_motion(hero, m)
            print(f"{hero}: {m['clip']} {SAMPLES} samples over {m['cycle_s']:.3f} s -> {motion_path(hero)}")
        elif a.what == "parts":
            RUNS[hero]().parts_png(os.path.join(a.review or ".", f"{hero}_run_parts.png"))
        elif a.review:
            review(hero, a.review, a.frames, a.cycle, a.legs)
        else:
            export(hero, a.frames, a.cycle, a.dry)


if __name__ == "__main__":
    main()
