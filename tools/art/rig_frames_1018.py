#!/usr/bin/env python3
"""Akshan's and Wukong's actions from Codex's skin-swap frames (assets/source/<hero>/hd/act/<tag>_<i>.png,
tools/art/import_swap_1018.py; the user approved them 2026-10-18: 「三套都可以，接进游戏」) exported like a rig: each frame on
the hero's canvas with its soles on the ground row and its hips over the design's standing column, then ppu_rig's export
(orig strips at the design's own density + the 1x sheet with each tag's timing). ppu_restyle (RESTYLE ppu 1.2) and ppu_hd
take it from there.

    python tools/art/rig_frames_1018.py akshan|wukong [--review DIR]

The tags and their timing are the kit's (tools/kit/build_<hero>.py reads the tag names; the totals stay what the old rig
had, so the kit's hit ticks still fall inside the swing / shot frames).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import wukong_run_staff as WS  # noqa: E402
import wukong_idle_staff as WI  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source")


def lp(p):
    return R.lp(p)


def teal_x(a):
    a = a.astype(int)
    m = (a[..., 3] > 0) & (a[..., 2] > a[..., 0] + 40) & (a[..., 1] > a[..., 0] + 40)
    return float(np.nonzero(m)[1].mean()) if m.sum() > 4 else a.shape[1] / 2


def tabard_x(a):
    a = a.astype(int)
    h = a.shape[0]
    m = (a[..., 3] > 0) & (a[..., 0] > 200) & (a[..., 1] > 140) & (a[..., 2] < 90)
    m[:h // 2] = False
    return float(np.nonzero(m)[1].mean()) if m.sum() > 5 else a.shape[1] / 2


# tag -> [(source frame, ms[, op])]; op (2026-10-19 frame audit, every one lossless): rot - quarter turns
# counter-clockwise of the whole frame, centred on the standing column; up - rows above the ground; dx - columns moved;
# flash - the pack's hit flash (ppu_rig.flash); idle_staff - league_wukong's idle staff one straight rod through his fist
# (wukong_idle_staff, 2026-10-29: 「怎么感觉猴子后面的金箍棒又做歪了？」 -> 36 degrees); staff - league_wukong's run staff
# made one straight piece (wukong_run_staff,
# 2026-10-22: 「猴子跑步的时候感觉武器看起来是歪的」)
# the hit: flashed and knocked back two columns, then one (the pack's hit, ppu_rig.flash - the hit had no flash)
# the death: 8 frames as the pack's - the last fall lands from 3 rows up, lies, bounces a row, lies
DEAD = [("dead_0", 100), ("dead_1", 110), ("dead_2", 120), ("dead_3", 120), ("dead_4", 60, dict(up=3)),
        ("dead_4", 100), ("dead_4", 60, dict(up=1)), ("dead_5", 500)]
AKSHAN = {
    "idle": [(f"idle_{i}", 240) for i in range(5)],
    "run": [(f"run_{i}", 143) for i in range(7)],
    "attack": [("attack_0", 80), ("attack_1", 80), ("attack_2", 90), ("attack_3", 90), ("attack_4", 93)],
    "skill": [("skill1_0", 60), ("skill1_1", 70), ("skill1_2", 80), ("skill1_3", 80), ("skill1_4", 70)],
    "skill2": [("skill2_0", 70), ("skill2_1", 70)],
    "e_swing": [("skill2_2", 115), ("skill2_3", 115)],
    # the roll off the rope (League's Akshan_Spell3_Roll: a tumble, landing in a crouch; the kit springs him back,
    # e_back_t + 4 = 14 ticks): the curled swing frame turned a quarter, a half, three quarters counter-clockwise (a
    # backward roll) on an arc, the crouch, up (it was the crouch and the stand alone)
    "e_roll": [("skill2_2", 40, dict(rot=1, up=4)), ("skill2_2", 40, dict(rot=2, up=6)), ("skill2_2", 40, dict(rot=3, up=3)),
               ("skill2_4", 53), ("skill2_0", 60)],
    "ult": [("ult_0", 70), ("ult_1", 70)],
    "ult_ch": [("ult_2", 160), ("ult_1", 160)],
    "ult_shot": [("ult_3", 50), ("ult_2", 50)],
    "hit": [("hit_0", 100, dict(flash=True, dx=-2)), ("hit_0", 100, dict(dx=-1))],
    "dead": DEAD,
}
WUKONG = {
    "idle": [(f"idle_{i}", 171, dict(idle_staff=True)) for i in range(7)],
    "run": [(f"run_{i}", 89, dict(staff=True)) for i in range(9)],
    "attack": [(f"attack_{i}", ms) for i, ms in enumerate([70, 70, 80, 80, 80, 80])],
    "q_attack": [(f"skill_{i}", ms) for i, ms in enumerate([60, 70, 80, 80, 80, 70])],
    "skill": [("skill2_3", 60), ("skill2_4", 80), ("skill2_6", 80), ("skill2_7", 80)],
    "skill2": [("ult_0", 60), ("ult_2", 70), ("ult_4", 70)],
    "spin": [(f"spin_{i}", 38) for i in range(8)],
    "ult": [("attack_0", 50)],
    "hit": [("hit_0", 100, dict(flash=True, dx=-2)), ("hit_0", 100, dict(dx=-1))],
    "dead": DEAD,
}
HEROES = {
    "akshan": dict(design="akshan/hd/slim2.png", ppu=1.61, map=AKSHAN, hip=teal_x, outline=(16, 2, 9)),
    "wukong": dict(design="wukong/hd/redo2.png", ppu=1.53, map=WUKONG, hip=tabard_x, outline=(10, 1, 6)),
}


class FrameDesign:
    """What ppu_rig.Rig needs: the squares, the standing column and ground row, the outline colour."""

    def __init__(self, hero, cfg):
        d = np.asarray(Image.open(lp(os.path.join(SRC, cfg["design"]))).convert("RGBA")).copy()
        self.hero, self.ppu, self.d = hero, cfg["ppu"], d
        self.H, self.W = d.shape[:2]
        ys, xs = np.nonzero(d[..., 3])
        self.ground = ys.max() + 1
        self.px = int(round(cfg["hip"](d)))
        self.outline = cfg["outline"]


def frames(hero):
    cfg = HEROES[hero]
    D = FrameDesign(hero, cfg)
    rig = R.Rig(D, pad=(70, 70, 60, 30))
    act = os.path.join(SRC, hero, "hd", "act")
    staffed = [name for seq in cfg["map"].values() for name, _, *op in seq if op and op[0].get("staff")]
    straight = dict(zip(staffed, WS.straighten_all(
        [np.asarray(Image.open(lp(os.path.join(act, n + ".png"))).convert("RGBA")) for n in staffed]))) if staffed else {}
    idled = [name for seq in cfg["map"].values() for name, _, *op in seq if op and op[0].get("idle_staff")]
    idle_straight = dict(zip(idled, WI.straighten_all(
        [np.asarray(Image.open(lp(os.path.join(act, n + ".png"))).convert("RGBA")) for n in idled])[0])) if idled else {}
    out = {}
    for tag, seq in cfg["map"].items():
        fr = []
        for name, ms, *op in seq:
            op = op[0] if op else {}
            p = os.path.join(act, name + ".png")
            if not os.path.isfile(lp(p)):
                raise SystemExit(f"{tag}: {name}.png missing")
            f = np.asarray(Image.open(lp(p)).convert("RGBA"))
            hip = cfg["hip"](f)                 # (on Codex's frame as drawn: the staff moved changes no hip)
            if op.get("staff"):
                f, hip = straight[name], hip + WS.PAD
            if op.get("idle_staff"):
                f = idle_straight[name]                 # (rows added on top, columns on the right: the hip stays)
            h, w = f.shape[:2]
            if op.get("rot"):
                f = np.rot90(f, op["rot"]).copy()
                h, w = f.shape[:2]
            hx = (hip if (tag != "dead" or name.endswith(("_0", "_1"))) and not op.get("rot") else w / 2) \
                - op.get("dx", 0)
            if op.get("flash"):
                f = R.flash(f)
            x0 = rig.CX - int(round(hx))
            y0 = rig.GY - h - op.get("up", 0)
            can = rig.canvas()
            ys, xs = np.nonzero(f[..., 3] > 0)
            ok = (y0 + ys >= 0) & (x0 + xs >= 0) & (x0 + xs < can.shape[1])
            can[y0 + ys[ok], x0 + xs[ok]] = f[ys[ok], xs[ok]]
            fr.append((can, ms))
        out[tag] = fr
    return rig, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hero", choices=list(HEROES))
    ap.add_argument("--review")
    a = ap.parse_args()
    rig, acts = frames(a.hero)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts, hero=a.hero)


if __name__ == "__main__":
    main()
