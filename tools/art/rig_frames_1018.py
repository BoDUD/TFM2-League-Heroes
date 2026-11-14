#!/usr/bin/env python3
"""Akshan's and Wukong's actions from Codex's skin-swap frames (assets/source/<hero>/hd/act/<tag>_<i>.png,
tools/art/import_swap_1018.py; the user approved them 2026-10-18: 「三套都可以，接进游戏」) exported like a rig: each frame on
the hero's canvas with its soles on the ground row and its hips over the design's standing column, then ppu_rig's export
(orig strips at the design's own density + the 1x sheet with each tag's timing). ppu_restyle (RESTYLE: both at their
frames' own density - Wukong 1.53 since 2026-10-29, Akshan 1.61 since 2026-11-14, the eyes) and ppu_hd take it from there.

    python tools/art/rig_frames_1018.py akshan|wukong [--review DIR]

The tags and their timing are the kit's (tools/kit/build_<hero>.py reads the tag names; the totals stay what the old rig
had, so the kit's hit ticks still fall inside the swing / shot frames).

Akshan's in-betweens (tools/art/inbetween.py; the user, 2026-11-14: 「还有有的动画感觉只有一帧 不如oppi的地方都要补 参考联盟的动画」):
a frame with its cape or coat tail waved by whole columns (op parts / sway: inbetween.vary, placed where the frame
stands; every square outside the part checked unchanged).
Wukong's (2026-11-14, 「能改就想办法改 全都要改」): Codex's own frames of the delivery that had been left out for time back in
E and W, and his tail swung by whole rows on the death's two moved copies (op parts / rows). His idle and run staffs,
the spin, the hit, the attacks and the R cast are as they were.

Akshan's eyes (2026-11-14, 「还有阿克尚的眼睛也调清晰一点」「现在看起来和两个黑洞一样」): AK_EYES puts back the eye squares
Codex drew in every action, in his design's eye white (AK_EYE), before anything else is done to the frame.
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
import inbetween as IB  # noqa: E402
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
# Akshan's in-betweens (2026-11-14: E's swing and R's channel, the loops the kit plays after the 0.14 s hook throw and
# aim, were two drawings each): op parts / sway - the cape streaming off his back (the swing) and the coat tail flaring
# at his far side (the channel) waved by whole columns, nothing where it leaves him, the tip 5 rows: the cape on its way
# down to the next drawing's lower cape and back up after it, the coat tail fluttering (5 squares, in the game as they
# are: his frames go in at their own 1.61 since 2026-11-14). Each loop's halves keep their
# milliseconds (115 / 160); the hook throw and the aim themselves (`skill2`, `ult`: 140 ms, the kit's 8-tick animations)
# stay two frames - a third would be under 50 ms.
VPAD = 30
AK_PARTS = {"skill2_2": {"cape": [(0, 12, 15, 31)]}, "skill2_3": {"cape": [(0, 33, 25, 49)]},
            "ult_2": {"coat": [(0, 30, 12, 50)]}, "ult_1": {"coat": [(0, 33, 12, 53)]}}


# Akshan's eyes: his design (Codex's picture, assets/source/akshan/codex_slim/akshan-slim-2-clean.png) has a white square
# in each eye beside a dark pupil. design_redo_1018.py keyed every near-white square out of the design as background, so
# the skin-swap pack showed Codex holes there - the key's green - and Codex drew the eyes in that green in every action;
# import_swap_1018.py / import_fix_1018.py then filled each small enclosed green speck with the darkest colour next to
# it: black eyes (and on the 1.2 grid black blocks with the brows over them). AK_EYES: the squares of each act frame that
# were Codex's green specks in his face (re-read from the two deliveries with the importers' own readers: every speck
# filled in each frame listed and marked, the face's picked by eye; the others are gaps between hair strands, under the
# arm and in the gun and stay filled); no frame gets a square Codex did not draw. A frame without one (idle_2, the falls)
# has its eyes drawn dark. AK_EYE: the median of the picture's eye-white pixels.
AK_EYE = (249, 249, 248)
AK_EYES = {
    "idle_0": [(27, 15), (31, 15)], "idle_1": [(27, 15), (31, 15)], "idle_3": [(30, 15), (34, 15)],
    "idle_4": [(29, 14), (33, 14)],
    "run_0": [(27, 15), (28, 15), (33, 15)], "run_1": [(27, 16)], "run_2": [(26, 16), (31, 16)], "run_3": [(29, 16)],
    "run_4": [(30, 15), (35, 15)], "run_5": [(28, 15)], "run_6": [(26, 15), (27, 15), (32, 15)],
    "attack_0": [(30, 12)], "attack_1": [(23, 12), (29, 14)], "attack_2": [(23, 11), (28, 11)], "attack_3": [(28, 11)],
    "attack_4": [(22, 10), (22, 11), (27, 11)],
    "skill1_0": [(25, 16)], "skill1_1": [(30, 14), (34, 14)], "skill1_2": [(29, 14), (30, 14)],
    "skill1_3": [(24, 11), (25, 11)], "skill1_4": [(22, 12)],
    "skill2_0": [(25, 18), (29, 18)], "skill2_1": [(46, 11), (46, 12), (50, 12)], "skill2_2": [(36, 13), (40, 14)],
    "skill2_3": [(41, 18), (45, 18)], "skill2_4": [(38, 15), (39, 15), (43, 15)],
    "ult_0": [(24, 11), (29, 11)], "ult_1": [(24, 14), (28, 14)], "ult_2": [(27, 11), (32, 11)],
    "ult_3": [(23, 10), (28, 10)],
    "hit_0": [(23, 15)], "dead_0": [(40, 11)], "dead_1": [(54, 11)],
}


def eyes_back(f, name):
    """An act frame with its eye squares (AK_EYES) in the eye white; each must be the importers' dark fill."""
    f = f.copy()
    for x, y in AK_EYES.get(name, ()):
        p = f[y, x]
        if p[3] == 0 or int(p[0]) + int(p[1]) + int(p[2]) > 15:
            raise SystemExit(f"{name}: ({x}, {y}) is {tuple(int(v) for v in p)}, not the importers' dark fill")
        f[y, x] = (*AK_EYE, 255)
    return f


def waved(name, x1, k):
    """op: the frame's part (AK_PARTS, the box in its own squares) waved by whole columns, nothing at column x1 where
    it leaves him, k rows (negative: lowered) at column 0, its free end."""
    (part, items), = AK_PARTS[name].items()
    return dict(parts={part: items}, sway=[(part, 0, x1, k, "right")])


# Wukong's death (2026-11-14): the two moved copies of his landing (the last 3 rows of the fall, the bounce) were the
# landing drawing itself - now his tail, standing up off his back (WK_PARTS: its box in dead_4's squares, the row it
# leaves him, the row of its curled tip), swings sideways by whole rows: trailing 4 squares back as he drops, flung 4
# forward on the bounce
WK_PARTS = {"dead_4": ("tail", [(5, 0, 23, 18)], 18, 0)}


def rows_wave(shape, y1, y0, k):
    """The moves of a part standing up across the rows: its whole rows shifted sideways, nothing on row y1 where it
    leaves him and k columns (negative: to the left) on row y0 at its tip, the rows past the tip going with it -
    inbetween.wave on its side (rig_zac's rows_wave). -> (dx, dy) arrays for inbetween.vary's moves."""
    H, W = shape[:2]
    dx = np.zeros((H, W), int)
    for y in range(H):
        t = min(max((y1 - y) / (y1 - y0), 0.0), 1.0)
        dx[y, :] = int(round(k * t))
    return dx, np.zeros((H, W), int)


def tailed(name, k, **op):
    """op: the frame's part (WK_PARTS) swung sideways by whole rows, k columns at its tip (rows_wave)."""
    part, items, y1, y0 = WK_PARTS[name]
    return dict(op, parts={part: items}, rows=[(part, y1, y0, k)])


WK_DEAD = DEAD[:4] + [("dead_4", 60, tailed("dead_4", -4, up=3)), ("dead_4", 100),
                      ("dead_4", 60, tailed("dead_4", 4, up=1)), ("dead_5", 500)]


AKSHAN = {
    "idle": [(f"idle_{i}", 240) for i in range(5)],
    "run": [(f"run_{i}", 143) for i in range(7)],
    "attack": [("attack_0", 80), ("attack_1", 80), ("attack_2", 90), ("attack_3", 90), ("attack_4", 93)],
    "skill": [("skill1_0", 60), ("skill1_1", 70), ("skill1_2", 80), ("skill1_3", 80), ("skill1_4", 70)],
    "skill2": [("skill2_0", 70), ("skill2_1", 70)],
    "e_swing": [("skill2_2", 58), ("skill2_2", 57, waved("skill2_2", 15, -5)), ("skill2_3", 58),
                ("skill2_3", 57, waved("skill2_3", 25, 5))],
    # the roll off the rope (League's Akshan_Spell3_Roll: a tumble, landing in a crouch; the kit springs him back,
    # e_back_t + 4 = 14 ticks): the curled swing frame turned a quarter, a half, three quarters counter-clockwise (a
    # backward roll) on an arc, the crouch, up (it was the crouch and the stand alone)
    "e_roll": [("skill2_2", 40, dict(rot=1, up=4)), ("skill2_2", 40, dict(rot=2, up=6)), ("skill2_2", 40, dict(rot=3, up=3)),
               ("skill2_4", 53), ("skill2_0", 60)],
    "ult": [("ult_0", 70), ("ult_1", 70)],
    "ult_ch": [("ult_2", 80), ("ult_2", 80, waved("ult_2", 12, 5)), ("ult_1", 80), ("ult_1", 80, waved("ult_1", 12, -5))],
    "ult_shot": [("ult_3", 50), ("ult_2", 50)],
    "hit": [("hit_0", 100, dict(flash=True, dx=-2)), ("hit_0", 100, dict(dx=-1))],
    "dead": DEAD,
}
WUKONG = {
    "idle": [(f"idle_{i}", 171, dict(idle_staff=True)) for i in range(7)],
    "run": [(f"run_{i}", 89, dict(staff=True)) for i in range(9)],
    "attack": [(f"attack_{i}", ms) for i, ms in enumerate([70, 70, 80, 80, 80, 80])],
    "q_attack": [(f"skill_{i}", ms) for i, ms in enumerate([60, 70, 80, 80, 80, 70])],
    # Wukong's in-betweens (2026-11-14, 「能改就想办法改 全都要改」): E and W take back Codex's own frames of the same
    # delivery that were left out to fit the kit's time - E's leap skill2_5 (the staff swung steeper between the two
    # overhead frames; the slam still from 220 ms), W's ult_3 (the staff tipping from upright toward ult_4's slant;
    # 4 x 50 ms in its 200, W has no hit). ult_1 (the staff half way up) is not used: its staff bends at the raised
    # fist (the piece above it some 25 degrees steeper)
    "skill": [("skill2_3", 55), ("skill2_4", 55), ("skill2_5", 55), ("skill2_6", 55), ("skill2_7", 80)],
    "skill2": [("ult_0", 50), ("ult_2", 50), ("ult_3", 50), ("ult_4", 50)],
    "spin": [(f"spin_{i}", 38) for i in range(8)],
    "ult": [("attack_0", 50)],
    "hit": [("hit_0", 100, dict(flash=True, dx=-2)), ("hit_0", 100, dict(dx=-1))],
    "dead": WK_DEAD,
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
            if hero == "akshan":
                f = eyes_back(f, name)
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
            pad = 0
            if op.get("parts"):                 # (an in-between: the picture VPAD bigger on every side, placed as drawn)
                rows = [(part, rows_wave(f.shape, y1, y0, k), "under") for part, y1, y0, k in op.get("rows", ())]
                f = IB.vary(f, op["parts"], cfg["outline"], sway=op.get("sway", ()), moves=rows, pad=VPAD,
                            name=f"{tag} {name}")
                pad = VPAD
            if op.get("flash"):
                f = R.flash(f)
            x0 = rig.CX - int(round(hx)) - pad
            y0 = rig.GY - h - op.get("up", 0) - pad
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
