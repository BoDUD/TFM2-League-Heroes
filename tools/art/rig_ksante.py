#!/usr/bin/env python3
"""league_ksante's action frames, posed on the approved 3/4 designs and Codex's key poses after League's own clips
(the user, 2026-10-22: 「普通用 A-2，全盛用 O-1」「全盛裁到 56 格，和普通姿态身体一样大」「动作帧请做到完美后喊我review」).

    python tools/art/rig_ksante.py --review DIR      # every tag at 3x + a GIF per tag (nothing written to the repo)
    python tools/art/rig_ksante.py                   # the frames at PPU -> assets/source/ppu/orig + the 1x sheet

The designs (one palette, PPU 1.5; tools/art/design_ksante_model.py):
  hd/idle.png     the base stance, 3/4 front, 65 x 72 (48 game px from the ntofo tops to the soles): the idle (one
                  frame: no breathing, the reels cut its moments from his actions - tools/art/hero_reels.py, #450 / #453)
                  and the hit.
  hd/ao_idle.png  All Out, 81 x 56, the same body size: ao_idle and ao_hit.
The key poses: Codex's (assets/source/ksante/codex_poses, on skeletons built from the designs' own bones -
tools/art/pack_ksante_poses.py), read back at the design's size with the design's head (tools/art/design_ksante_poses.py:
hd/pose_<name>.png + .json). Each is placed with its head's middle where its skeleton put it from the stance's standing
point, its lowest square on the ground or `lift` rows over it (placed by the feet the torso jumps from frame to frame:
rig_shyvana's lesson). Both stances stand on the same pivot; the forward pictures (the swing arcs, Q's crack and
burst, W's dust) are drawn into the frames from league_ksante_fx / _big (assets/source/native/ksante_bake.json).
Timings: MS (ms per frame); the kit's ticks (tools/kit/build_ksante.py: a_hit, q_at, q3_rel, w_charge, w_dash_dur,
r_at, r_chase, r_dash_dur) are these frames' starts (a frame's start in ticks = ms x 0.06).
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
import pixel_down as PD  # noqa: E402
import pack_ksante_poses as PK  # noqa: E402

HERO = "ksante"
PPU = 1.5
SRC = os.path.join(ROOT, "assets", "source", "ksante")
# each stance: its design, the column it stands on (between the feet, the pelvis over it) and the head box's half width
# (design_ksante_poses.STANCES' head boxes: base 22 wide, All Out 26)
FORMS = {"base": ("idle.png", 34, 11.0), "ao": ("ao_idle.png", 44, 13.0)}


def lp(path):
    return R.lp(path)


def load(name):
    return np.asarray(Image.open(lp(os.path.join(SRC, "hd", name))).convert("RGBA")).copy()


def hit_white(can, k=0.45):
    """rig_shyvana.hit_white: the flash keeps the outline dark (flashed whole, the export drew a new outline round it)."""
    import strips
    out = can.copy()
    m = (out[..., 3] > 0) & (strips.lum(out[..., :3]) >= 70)
    out[m, :3] = (out[m, :3].astype(float) * (1 - k) + 255 * k).astype(np.uint8)
    return out


class Canvas:
    """Every frame of both stances on one canvas: the pivot column CX, the ground row GY (ppu_rig.Rig's), each stance
    standing with its own standing column on the pivot."""

    def __init__(self):
        self.designs = {st: load(f) for st, (f, _, _) in FORMS.items()}
        base = self.designs["base"]

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, base
            H, W = base.shape[:2]
            px, ground = FORMS["base"][1], base.shape[0]
            outline = PD.edge_colour(base)
        # room for the ntofos: thrust 90 squares ahead, swung 80 behind, raised 70 over his head
        self.rig = R.Rig(D, pad=(84, 96, 72, 12))
        self.outline = D.outline
        self.poses, self.head_at = {}, {}
        for n in PK.POSES:
            png = os.path.join(SRC, "hd", f"pose_{n}.png")
            if os.path.isfile(lp(png)):
                self.poses[n] = load(f"pose_{n}.png")
                with open(lp(os.path.join(SRC, "hd", f"pose_{n}.json")), encoding="utf-8") as fh:
                    self.head_at[n] = json.load(fh)["head_at"]

    def blank(self):
        return self.rig.canvas()

    def put(self, can, a, ox, oy):
        ys, xs = np.nonzero(a[..., 3] > 0)
        ty, tx = ys + oy, xs + ox
        ok = (ty >= 0) & (ty < can.shape[0]) & (tx >= 0) & (tx < can.shape[1])
        can[ty[ok], tx[ok]] = a[ys[ok], xs[ok]]
        return can

    def design(self, st, dx=0, flash=False):
        """A stance's design standing on the pivot (moved dx)."""
        d = self.designs[st]
        can = self.put(self.blank(), d, self.rig.CX - FORMS[st][1] + dx, self.rig.GY - d.shape[0])
        return hit_white(can) if flash else can

    def plan_head(self, name):
        """Where the pose's skeleton put the head box's middle, squares right of the stance's standing point."""
        st, _, _, _, spec = PK.POSES[name]
        return PK.build(st, spec)["head"][0] - FORMS[st][1]

    def pose(self, name, dx=0, lift=0, flash=False):
        """Codex's key pose standing on the pivot (moved dx), its lowest square on the ground or `lift` rows over it."""
        if name not in self.poses:
            sys.exit(f"pose {name} not delivered yet (assets/source/ksante/codex_poses)")
        a = self.poses[name]
        st = PK.POSES[name][0]
        stand = self.head_at[name][0] + FORMS[st][2] - self.plan_head(name)
        can = self.put(self.blank(), a, int(round(self.rig.CX - stand)) + dx, self.rig.GY - a.shape[0] - lift)
        can[self.rig.GY:] = 0
        return hit_white(can) if flash else can


# ms per frame; the kit's ticks come from these (a frame's start in ticks = ms x 0.06)
MS = {
    # the runs 150 ms a frame (2026-10-22, 「走路跳动频率太高 和之前索拉卡一样」: 110 made a 0.44 s cycle; Soraka's fix was 150)
    "idle": [1000], "hit": [100, 100], "run": [150, 150, 150, 150],
    "attack": [80, 87, 100, 100, 100],              # the strike at 167 ms = a_hit 10
    "skill": [80, 87, 120, 80, 66],                 # Q1: the slam at 167 ms = q_at 10; 433 ms = q_dur 26
    "skill_b": [80, 87, 120, 80, 66],               # Q2: the same timing
    "skill_c": [90, 110, 150, 80, 70],              # Q3: the slam at 200 ms = q3_rel 12; 500 ms = q3_dur 30
    "skill2": [100, 650],                           # W's brace: 750 ms = w_charge 45
    "skill2_dash": [75, 75, 75, 75],                # W's ram: 300 ms = w_dash_dur 18
    "ult": [90, 110, 150, 217],                     # R's bash at 200 ms = r_at 12; 567 ms = r_dur 34
    "ult_dash": [120, 120, 127],                    # the chase: 367 ms = r_dash_dur 22
    "dead": [150, 150, 250, 600],
    "ao_idle": [1000], "ao_hit": [100, 100], "ao_run": [150, 150, 150, 150],
    "ao_attack": [80, 87, 120, 100, 80],            # the sweep at 167 ms = a_hit 10
    "ao_skill": [80, 87, 150, 50, 66],              # the smash at 167 ms = q_at 10
    "ao_skill_b": [80, 87, 150, 50, 66],
    "ao_skill_c": [90, 110, 150, 80, 70],           # the smash at 200 ms = q3_rel 12
    "ao_skill2": [100, 300],                        # the brace: 400 ms = ao_w_charge 24
    "ao_skill2_dash": [75, 75, 75, 75],             # the ram: 300 ms = w_dash_dur 18
}


def frames(C, tags=None):
    q, d = C.pose, C.design
    out = {
        # the idle: the design (the reels pop his actions' moments over it)
        "idle": [d("base")],
        "hit": [d("base", dx=-2, flash=True), d("base", dx=-1)],
        # the run (League's Run1: the ntofos carried upright; the near foot landing, carried by it with the far knee
        # up, the far foot landing, carried by it)
        "run": [q("run1"), q("run2"), q("run3"), q("run4")],
        # the attack (League's Attack1: the near ntofo pulled back behind him, both thrust forward in a lunge - the
        # hit - and back to standing; the swing's arc drawn in at the thrust)
        "attack": [q("a_back"), q("a_back", dx=-1), q("a_strike"), q("a_strike", dx=-1), d("base")],
        # Q1 (League's Spell1_A: a hop with the far ntofo raised level over his head, slammed down in front - the
        # crack runs on from it)
        "skill": [q("q_up", lift=3), q("q_up", lift=8), q("q_down"), q("q_down", dx=-1), d("base")],
        # Q2 (League's Spell1_B: the other ntofo, raised behind him after Q1, slammed down in front)
        "skill_b": [q("q_down", dx=-1), q("q_down"), q("q2_down"), q("q2_down", dx=-1), d("base")],
        # Q3 (League's Spell1_C: a jump with both ntofos raised level over his head, slammed down together - the
        # ground bursts and the shockwave rolls out)
        "skill_c": [q("q3_up", lift=4), q("q3_up", lift=10), q("q3_slam"), q("q3_slam", dx=-1), d("base")],
        # W's brace (League's Spell2_Enter / Loop: both ntofos set before him as a wall, leaning into it)
        "skill2": [q("w_wall", dx=-1), q("w_wall")],
        # W's ram (League's Spell2_Dash: the same wall, charging with long strides; the dust drawn in behind him)
        "skill2_dash": [q("w_dash"), q("w_dash", dx=1), q("w_dash"), q("w_dash", dx=1)],
        # R's bash (League's Spell4_A: braced behind the ntofos, lunging, both shoved forward - the kick: the ntofos
        # break in All Out's burst (ao_on, 450 ms from the kick) and he crouches All Out to go after the champion)
        "ult": [q("w_wall"), q("w_dash"), q("r_bash"), q("ao_charge")],
        # R's chase (League's Spell4_dash, All Out from the kick on: launched after the champion, a club raised in
        # the air, slammed down on it as he lands)
        "ult_dash": [q("ao_charge", lift=4), q("ao_leap", lift=8), q("ao_smash")],
        # death (League's Death: pitching forward, the ntofos toppling, down on one knee with them on the ground)
        "dead": [q("d_slump"), q("d_slump", dx=1), q("d_kneel"), q("d_kneel")],
        # All Out
        "ao_idle": [d("ao")],
        "ao_hit": [d("ao", dx=-2, flash=True), d("ao", dx=-1)],
        # the run (League's Run1_AllOut: hunched, the clubs trailing; the legs as the base run's)
        "ao_run": [q("ao_run1"), q("ao_run2"), q("ao_run3"), q("ao_run4")],
        # the attack (League's Attack1_AllOut: the near club swung up behind him, both swept out wide - the hit)
        "ao_attack": [q("ao_swing_back"), q("ao_swing_back", dx=-1), q("ao_swing"), q("ao_swing", dx=1), d("ao")],
        # Q (League's Spell1_A_AllOut: a leap with a club raised over his head, smashed down in front)
        "ao_skill": [q("ao_leap", lift=4), q("ao_leap", lift=10), q("ao_smash"), q("ao_smash", dx=-1), d("ao")],
        "ao_skill_b": [q("ao_leap", lift=4), q("ao_leap", lift=10), q("ao_smash"), q("ao_smash", dx=-1), d("ao")],
        # Q3 (League's Spell1_C_AllOut: the same leap, higher, the smash bursting the ground)
        "ao_skill_c": [q("ao_leap", lift=6), q("ao_leap", lift=12), q("ao_smash"), q("ao_smash", dx=-1), d("ao")],
        # W's brace (League's Spell2_AllOut: the clubs crossed over his head) and ram (both clubs thrust low ahead,
        # charging; the dust drawn in behind him)
        "ao_skill2": [q("ao_cross", dx=-1), q("ao_cross")],
        "ao_skill2_dash": [q("ao_charge"), q("ao_charge", dx=1), q("ao_charge"), q("ao_charge", dx=1)],
    }
    res = {}
    for tag, cans in out.items():
        if tags and tag not in tags:
            continue
        ms = MS[tag]
        if len(cans) != len(ms):
            sys.exit(f"{tag}: {len(cans)} frames for {len(ms)}")
        res[tag] = [(c, m) for c, m in zip(cans, ms)]
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review")
    ap.add_argument("--tags", help="only these tags (comma-separated)")
    ap.add_argument("--no-bake", action="store_true", help="review without the effects drawn in")
    a = ap.parse_args()
    C = Canvas()
    acts = frames(C, a.tags.split(",") if a.tags else None)
    bake = not a.no_bake and os.path.isfile(lp(os.path.join(ROOT, "assets", "source", "native", f"{HERO}_bake.json")))
    if a.review:
        C.rig.review(C.rig.bake(acts) if bake else acts, a.review)
        return
    C.rig.export(C.rig.bake(acts) if bake else acts)


if __name__ == "__main__":
    main()
