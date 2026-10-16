#!/usr/bin/env python3
"""league_nami redone at PPU from Codex's picture, the actions posed from the design itself (tools/art/ppu_rig.py;
the user, 2026-10-16: 「动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」).

    python tools/art/rig_nami_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_nami_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_nami_hd.py                 # orig strips + the 1x sheet; then ppu_restyle / ppu_hd

Parts (design squares at PPU 1.5, 50 game rows crown to the fin's tip): the staff (head and shaft, turned about her
grip from the picture itself), the fin (the tail's end, its columns lifted to swish), the upper body (head, hair, torso,
both hands) and the tail. She floats: the upper body bobs over the tail, the whole figure rises for the wave.
Every tag keeps the sheet's frame count and timing.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "nami"
PPU = 1.5
ROWS = 50
PIVOT_COL = 31                               # the tail's root under her waist: the line she stands on
GRIP = (46.5, 31.5)                          # the staff in her far hand
MS = {"idle": [140] * 8, "run": [125] * 8, "attack": [60, 60, 70, 70, 90, 110], "skill": [60, 70, 80, 90, 100, 100],
      "skill2": [60, 70, 60, 70, 100, 120], "ult": [60, 70, 80, 80, 100, 120, 140], "hit": [100, 100],
      "dead": [100, 100, 120, 120, 120, 150, 150, 500]}


def design():
    D = R.Design(HERO, PPU, ROWS, coarse=True)
    D.px = PIVOT_COL
    D.cut_props({"staff": [(40, 1), (57, 1), (57, 24), (49, 24), (49, 50), (51, 50), (51, 68), (42, 68), (42, 50),
                           (44, 50), (44, 24), (40, 24)]})
    D.shaft("staff", (46.5, 23), (46.5, 51), 1.2)       # the shaft: a straight line at every angle
    D.part("hand", [(38, 26), (46, 26), (46, 35), (38, 35)])   # her hand, drawn over the staff it holds
    D.part("fin", [(0, 43), (26, 43), (26, 76), (0, 76)])
    D.part("upper", D.poly([(0, 0), (57, 0), (57, 42), (24, 42), (24, 46), (0, 46)]) & D.rest(), take=False)
    D.part("tail", D.rest(), take=False)
    return D


def pose(rig, up=(0, 0), staff=0, fin=0, whole=(0, 0)):
    """up: the upper body (with the staff) moved over the tail; staff: degrees the staff turns about her grip
    (counter-clockwise tips it back, clockwise forward); fin: rows the fin's tip lifts; whole: the whole figure."""
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    # the staff turned goes behind her (its shaft across her body hidden, the head out in front; tilted back, its head
    # never over her face); upright or barely forward it is in front as drawn
    st = ("staff", dict(dx=ux, dy=uy, angle=staff, about=GRIP))
    behind = staff < -25 or staff > 5
    layers = [("fin", dict(dx=wx, dy=wy, sway=(0, 26, fin, "right"))),
              ("tail", dict(dx=wx, dy=wy))] + \
        ([st] if behind else []) + [("upper", dict(dx=ux, dy=uy))] + ([] if behind else [st]) + \
        [("hand", dict(dx=ux, dy=uy))]
    return R.compose(rig, layers)


def frames(rig):
    out = {}
    out["idle"] = [pose(rig, up=(0, b), fin=f) for b, f in zip([0, 0, 1, 1, 1, 1, 0, 0], [0, 1, 1, 2, 2, 1, 1, 0])]
    out["run"] = [pose(rig, up=(1, b), fin=f, whole=(0, -w)) for b, f, w in
                  zip([0, 1, 1, 0, 0, 1, 1, 0], [0, 2, 4, 3, 1, 0, 1, 0], [1, 2, 2, 1, 1, 2, 2, 1])]
    out["attack"] = [pose(rig, up=u, staff=s) for u, s in
                     [((0, 0), -15), ((-1, 0), 15), ((1, 0), -45), ((2, 0), -70), ((1, 0), -40), ((0, 0), 0)]]
    out["skill"] = [pose(rig, up=u, staff=s) for u, s in
                    [((-1, 0), 20), ((-1, 0), 30), ((1, 0), -55), ((2, 0), -80), ((1, 0), -60), ((0, 0), -20)]]
    out["skill2"] = [pose(rig, up=u, staff=s) for u, s in
                     [((0, 0), -10), ((1, 0), -30), ((1, 0), -45), ((1, 0), -45), ((0, 0), -30), ((0, 0), 0)]]
    out["ult"] = [pose(rig, up=u, staff=s, whole=(0, -w), fin=f) for u, s, w, f in
                  [((0, 0), 10, 1, 1), ((-1, 0), 25, 3, 2), ((-1, 0), 35, 4, 3), ((2, 0), -60, 2, 1),
                   ((2, 0), -80, 1, 0), ((1, 0), -40, 0, 0), ((0, 0), 0, 0, 0)]]
    out["hit"] = [R.flash(pose(rig, whole=(-2, 0), staff=10)), pose(rig, whole=(-1, 0), staff=5)]
    # lying: the staff upright before the turn, so it lies along her body
    lying = R.lie(rig, pose(rig, staff=0), k=1, dx=-2)
    out["dead"] = [pose(rig, whole=(-1, 0), staff=10), pose(rig, whole=(-2, 0), up=(-1, 1), staff=15),
                   pose(rig, up=(0, 3), staff=-20), pose(rig, up=(0, 6), staff=-40),
                   R.lie(rig, pose(rig, up=(0, 6), staff=0), k=1, dx=-1), lying, lying.copy(), lying.copy()]
    return {t: list(zip(f, MS[t])) for t, f in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D.ruler(os.path.join(a.parts, f"{HERO}_parts.png"), z=8)
        return
    rig = R.Rig(D)
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
