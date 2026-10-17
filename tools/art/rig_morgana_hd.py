#!/usr/bin/env python3
"""league_morgana redone at PPU from Codex's picture, the actions posed from the design itself (tools/art/ppu_rig.py;
the user, 2026-10-16: 「动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」).

    python tools/art/rig_morgana_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_morgana_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_morgana_hd.py                 # orig strips + the 1x sheet; then ppu_restyle / ppu_hd

Parts (design squares at PPU 1.5, 45 game rows horns to hem): the raised arm (shoulder to the open hand), the far wing
(teal, folded behind her), the train (the pink tail of the skirt on the ground), the upper body (head, horns, torso,
the near hand at her chest) and the skirt. Every tag keeps the sheet's frame count and timing.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "morgana"
PPU = 1.5
ROWS = 45
WAIST = 42                                   # first skirt row (the belt's bottom)


def design():
    D = R.Design(HERO, PPU, ROWS, coarse=True, foot_x=31.5 / 0.08016627)
    # the raised arm: from the shoulder (36, 31) down to the elbow (39, 37) and the forearm up to the open hand
    D.part("arm", [(36, 30), (40, 29), (49, 28), (49, 38), (43, 40), (38, 40), (35, 37), (35, 33)])
    D.part("wing", [(13, 29), (19, 27), (23, 31), (24, 40), (23, 47), (19, 53), (13, 53)])
    D.part("train", [(0, 55), (24, 55), (24, 69), (0, 69)])
    yy = np.arange(D.H)[:, None] + np.zeros((1, D.W), int)
    D.part("skirt", D.rest() & (yy >= WAIST), take=False)
    D.part("upper", D.rest(), take=False)
    return D


SHOULDER = (36.5, 31.5)
MS = {"idle": [140] * 8, "run": [143] * 8, "attack": [60, 70, 80, 90, 100, 100], "skill": [70, 70, 80, 90, 110, 150],
      "skill2": [60, 60, 80, 100, 100, 100], "ult": [80, 80, 80, 90, 100, 100, 110, 120], "hit": [120, 120],
      "dead": [100, 100, 120, 120, 120, 150, 150, 500]}


def pose(rig, up=(0, 0), arm=0, wing=(0, 0), train=0, hem=0, whole=(0, 0), spread=None):
    """up: the upper body (and the arm, the wing) moved over the skirt; arm: degrees the raised arm turns about the
    shoulder (counter-clockwise lifts the hand); wing: the wing's own move; train: rows the train's tip lifts; hem:
    columns the skirt's lowest 8 rows swing; whole: the whole figure; spread: (dx, dy) of a second wing, the far one
    mirrored to her front side (R)."""
    D = rig.D
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    skirt = R.row_shift(D.layer("skirt"), D.ground - 8, D.ground - 1, hem)
    layers = [("wing", dict(dx=ux + wing[0], dy=uy + wing[1]))]
    if spread is not None:
        layers.append(("wing", dict(dx=ux + spread[0], dy=uy + spread[1], flip=True, about=(31.5, 40))))
    layers += [("train", dict(dx=wx, dy=wy, sway=(0, 24, train, "right"))),
               (skirt, dict(dx=wx, dy=wy)),
               ("upper", dict(dx=ux, dy=uy)),
               ("arm", dict(dx=ux, dy=uy, angle=arm, about=SHOULDER))]
    return R.compose(rig, layers, fill=[("arm", (ux, uy))])


def frames(rig):
    out = {}
    out["idle"] = [pose(rig, up=(0, b), wing=(0, w)) for b, w in zip([0, 0, 1, 1, 1, 1, 0, 0], [0, 0, 0, 1, 1, 1, 0, 0])]
    out["run"] = [pose(rig, up=(1, b), wing=(0, w), train=t, hem=h) for b, w, t, h in
                  zip([0, 1, 1, 0, 0, 1, 1, 0], [0, -1, -2, -1, 0, 1, 1, 0], [0, 1, 2, 1, 0, 1, 2, 1],
                      [0, 1, 1, 0, 0, -1, -1, 0])]
    out["attack"] = [pose(rig, up=u, arm=a) for u, a in
                     [((-1, 0), 25), ((1, 0), -5), ((2, 0), -15), ((2, 0), -15), ((1, 0), -5), ((0, 0), 0)]]
    out["skill"] = [pose(rig, up=u, arm=a) for u, a in
                    [((-1, 1), 35), ((-2, 1), 45), ((2, 0), -10), ((3, 0), -20), ((2, 0), -15), ((1, 0), 0)]]
    out["skill2"] = [pose(rig, up=u, arm=a) for u, a in
                     [((0, 0), 35), ((0, 0), 45), ((1, 1), -40), ((1, 1), -40), ((0, 0), -20), ((0, 0), 0)]]
    out["ult"] = [pose(rig, arm=a, wing=w, spread=s, whole=wh) for a, w, s, wh in
                  [(20, (0, -2), None, (0, 0)), (35, (-1, -4), (1, -4), (0, -1)), (45, (-2, -6), (2, -6), (0, -2)),
                   (45, (-2, -6), (2, -6), (0, -2)), (40, (-2, -5), (2, -5), (0, -2)), (35, (-1, -4), (1, -4), (0, -1)),
                   (20, (0, -2), (0, -2), (0, 0)), (0, (0, 0), None, (0, 0))]]
    out["hit"] = [R.flash(pose(rig, whole=(-2, 0), arm=15)), pose(rig, whole=(-1, 0), arm=5)]
    lying = R.lie(rig, pose(rig, arm=-30), k=1, dx=-4)
    out["dead"] = [pose(rig, whole=(-1, 0), arm=30), pose(rig, whole=(-2, 0), up=(-1, 2), arm=10),
                   pose(rig, up=(0, 4), arm=-30), pose(rig, up=(0, 7), arm=-40, wing=(0, 2)),
                   R.lie(rig, pose(rig, up=(0, 7), arm=-40), k=1, dx=-2, sink=0), lying, lying.copy(), lying.copy()]
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
