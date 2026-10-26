#!/usr/bin/env python3
"""league_skarner's action frames: Skarner's approved 3/4 design and Codex's key poses after League's clips (the user,
2026-10-26: 「Codex 照骨架画」, then 「codex交付了动作帧 你做到完美后喊我review」).

    python tools/art/rig_skarner.py --review DIR      # every tag at 3x + a GIF per tag (nothing written)
    python tools/art/rig_skarner.py                   # his frames at PPU -> assets/source/ppu/orig + the 1x sheet

The pictures (tools/art/design_skarner_model.py, design_skarner_poses.py):
  hd/idle.png         Skarner, 3/4 front facing right, 80 x 59 at PPU 1.75 (33.7 game px stinger tips to feet): the
                      idle, the hit;
  hd/pose_<name>.png  Codex's key poses read back at the design's size with the design's head put in
                      (assets/source/skarner/POSE_PROMPTS.md): a_wind a_strike q_dig q_lift t_wind t_throw w_rear w_slam
                      e_charge e_grab r_lash r_hold run1-4 d_rear d_down.
Placing a pose (rig_trundle's way): its head box (the design's head, pasted) stands where the design's head stands, moved
as far as the pose pack's skeleton moves the head in that frame (HEAD_DX, rounded) and dx squares more by hand; its
soles on the ground row (its lowest square), or `lift` rows over it. The idle is the design alone. The boulder he
holds between Q's pickup and its last hit or throw is no frame of his: the kit's `rock` buff shows it over his back
(the effect q_held), so his idle and run stay the design's.
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
import pack_skarner_poses as PK  # noqa: E402
from design_skarner_poses import HEAD_BOX  # noqa: E402

HERO = "skarner"
PPU = 1.75
SRC = os.path.join(ROOT, "assets", "source", "skarner", "hd")
STAND = 40                     # the idle's standing column: the middle of his 80 squares (he turns about it)
HEAD = (HEAD_BOX[0], HEAD_BOX[1])          # the design's head box top-left (column, row) in hd/idle.png


def head_dx():
    """How far the pose pack's skeleton moves the head across in each pose (squares, rounded)."""
    rig = PK.Rig(r"D:\WeGameApps\lol")
    return {n: int(round(rig.pose(sk)[1][0])) for n, (_, _, _, sk) in PK.POSES.items()}


LIFT = {"w_rear": 6}           # rows off the ground: the quake's leap (the pack's skeleton lifts him 6 squares)
# the far pincer in hd/idle.png (right of the hood: from its wrist, column PINCER, down to its tip), moved whole for the
# attack while he holds the boulder (League's BaseAttack1_Rock: the tails keep the boulder up over his back - the kit's
# q_held picture - and the claw strikes): PINCER_ROWS its rows (ends exclusive), WRIST_ROWS the rows where its wrist
# meets the arm (a jab forward fills the opened columns with the wrist's own first column: the arm reaching out)
PINCER, PINCER_ROWS, WRIST_ROWS = 64, (33, 59), (36, 46)


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
        self.dx = head_dx()

        class D:                                        # what ppu_rig.Rig needs of a design
            hero, ppu, d0 = HERO, PPU, d
            H, W, px, ground = d.shape[0], d.shape[1], STAND, d.shape[0]
            outline = PD.edge_colour(d)
        self.rig = R.Rig(D, pad=(50, 60, 50, 14))      # room for the tails thrown forward, raised, laid out behind
        self.outline = D.outline

    def placed(self, name, dx=0, lift=0):
        """(picture, its top-left on the canvas)."""
        rig = self.rig
        if name == "idle":
            d, (hx, hy), ground, mv = self.d, HEAD, self.d.shape[0], 0
        else:
            (d, (hx, hy), ground), mv = load_pose(name), self.dx[name]
        return d, (rig.ox + HEAD[0] - hx + mv + dx, rig.GY - ground - lift)

    def rock_jab(self, body_dx, jab_dx, jab_dy):
        """The idle with its far pincer moved jab_dx squares forward / jab_dy down (the arm reaching out after it; its tip
        already on the ground row, so never lower than the idle's) and
        the whole figure body_dx squares forward: the boulder-holding attack's frames (the tails, the boulder over them,
        unmoved but for the figure's own step)."""
        rig = self.rig
        d = self.d
        r0, r1 = PINCER_ROWS
        top = 3                                         # room for a pincer raised in the wind-up
        pic = np.zeros((d.shape[0] + top + 2, d.shape[1] + 8, 4), np.uint8)
        body = d.copy()
        claw = d[r0:r1, PINCER:].copy()
        body[r0:r1, PINCER:] = 0
        pic[top:top + d.shape[0], :d.shape[1]] = body
        if jab_dx > 0:                                  # the wrist drawn on into the opened columns
            w0, w1 = WRIST_ROWS
            col = d[w0:w1, PINCER]
            for k in range(jab_dx):
                m = col[:, 3] > 0
                tgt = pic[top + w0:top + w1, PINCER + k]
                tgt[m] = col[m]
        m = claw[..., 3] > 0
        sub = pic[top + r0 + jab_dy:top + r1 + jab_dy, PINCER + jab_dx:PINCER + jab_dx + claw.shape[1]]
        sub[m] = claw[m]
        can = rig.canvas()
        ys, xs = np.nonzero(pic[..., 3] > 0)
        left = rig.ox + body_dx
        ground = top + d.shape[0]
        ty, tx = ys + rig.GY - ground, xs + left
        can[ty, tx] = pic[ys, xs]
        return can

    def frame(self, name, dx=0, lift=None, flash=False):
        rig = self.rig
        can = rig.canvas()
        d, (left, top) = self.placed(name, dx, LIFT.get(name, 0) if lift is None else lift)
        ys, xs = np.nonzero(d[..., 3] > 0)
        ty, tx = ys + top, xs + left
        ok = (ty >= 0) & (ty < rig.CH) & (tx >= 0) & (tx < rig.CW)
        if not ok.all():
            sys.exit(f"{name}: {int((~ok).sum())} squares off the canvas (pad the rig)")
        can[ty, tx] = d[ys, xs]
        return R.flash(can) if flash else can


# ms per frame; the kit's ticks (tools/kit/build_skarner.py) match these (a frame's start in ticks = ms x 0.06):
# attack 467 ms = atk_dur 28, the stingers landing on the strike frame (a_hit 12 = 200 ms); Shattered Earth's pickup
# (tag `skill`) 500 ms = q_dur 30, the boulder up on the lift frame; Upheaval's throw (tag `skill_toss`) 400 ms = q_toss
# 24, the boulder leaving on the throw frame (q_toss_rel 9 = 150 ms); Ixtal's Impact (tag `skill2`) 733 ms = e_anim +
# e_kb_t 44, the charge then the grab; Seismic Bastion's quake at the carry's end (tag `w`) 267 ms = w_dur 16, the
# earthquake on the slam frame (w_rel 7 = 117 ms); Impale (tag `ult`) 600 ms = r_dur 36, the tails lashing out on r_rel
# 14 (233 ms)
# The attack opens on the idle (33 ms): holding the boulder, the kit swaps in attack_rock at the effect's first tick
# (start_timing 1, 17 ms), before any tail of the stab could show. attack_rock 467 ms = atk_dur 28 from that tick, the
# jab landing on a_hit 12 (17 + 183 = 200 ms). Ixtal's Impact: the charge (skill2) held while he runs in, the grab (tag
# `grab`, e_kb_t 20 = 333 ms) from the contact, the bounce and slam (`w`) at the carry's end.
MS = {"idle": [1000], "run": [140] * 4, "attack": [33, 167, 200, 67], "attack_rock": [183, 200, 84],
      "skill": [250, 250], "skill_toss": [150, 250], "skill2": [400], "grab": [333], "w": [117, 150],
      "ult": [233, 200, 167], "hit": [100, 100], "dead": [140, 260, 300, 600]}


def actions(C):
    f = C.frame
    out = {}
    out["idle"] = [f("idle")]
    # run (League's Runbase: the legs stepping in two sets, the tails over his back)
    out["run"] = [f("run1"), f("run2"), f("run3"), f("run4")]
    # attack (BaseAttack1: the tails reared up and back, stabbing down before him, back)
    out["attack"] = [f("idle"), f("a_wind"), f("a_strike"), f("idle")]
    # holding the boulder (BaseAttack1_Rock: the tails keep it up; he rears a square back, the far pincer cocked, then
    # lunges, the pincer jabbing out)
    out["attack_rock"] = [C.rock_jab(-1, -1, -2), C.rock_jab(1, 4, 0), f("idle")]
    # Shattered Earth (Spell1_Pickup: the tails plunged into the ground on the boulder, the boulder torn up over his back)
    out["skill"] = [f("q_dig"), f("q_lift")]
    # Upheaval (Spell1_Toss: the boulder high over him, the tails snapping forward as it flies)
    out["skill_toss"] = [f("t_wind"), f("t_throw")]
    # Ixtal's Impact (Spell3: charging head first; Spell3_Grab: the claws clamped on the champion he carries)
    out["skill2"] = [f("e_charge")]
    out["grab"] = [f("e_grab")]
    # Seismic Bastion at the carry's end (Spell2: bouncing up, crashing down - the earthquake)
    out["w"] = [f("w_rear"), f("w_slam")]
    # Impale (Spell4: the tails reared back, lashing out far before him, arched over the impaled)
    out["ult"] = [f("a_wind"), f("r_lash"), f("r_hold")]
    out["hit"] = [f("idle", dx=-2, flash=True), f("idle", dx=-1)]
    # death (Death: jerking up, the tails stiff; collapsed flat, the tails laid out behind)
    out["dead"] = [f("d_rear", flash=True), f("d_rear"), f("d_down"), f("d_down")]
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
