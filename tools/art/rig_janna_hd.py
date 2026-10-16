#!/usr/bin/env python3
"""league_janna redone at PPU from Codex's picture, the actions posed from the design itself (tools/art/ppu_rig.py;
the user, 2026-10-16: 「动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」).

    python tools/art/rig_janna_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_janna_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_janna_hd.py                 # orig strips + the 1x sheet; then ppu_restyle / ppu_hd

The picture (Codex 2026-10-09, janna-ai-source) is drawn on squares of ~21 px: read back square for square
(scripts/regrid.py) it is 68 rows, PPU 1.5 at her 45 game rows, so the design is the picture itself, nothing resampled.
Parts: the staff (turned about her grip from the picture), the ribbons at her hip (their columns lifted to flutter),
the upper body (hair, head, arms) and the legs. She floats: idle and run bob the whole figure.
Every tag keeps the sheet's frame count and timing.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "janna"
PPU = 1.5
ROWS = 45
PIVOT_COL = 22                               # between her legs
GRIP = (33.5, 43.5)                          # the staff in her far hand
HAND = [(28, 40), (36, 40), (36, 46), (28, 46)]
STAFF = [(29, 12), (42, 12), (42, 34), (38.5, 34), (36, 46), (34, 64), (29, 64), (29, 46), (33, 34), (29, 34)]


def design():
    D = R.Design(HERO, PPU, ROWS, regrid=21)
    D.px = PIVOT_COL
    D.cut_props({"staff": STAFF})
    D.shaft("staff", (35.5, 34), (30.8, 61), 1.2)       # the shaft: a straight line at every angle
    D.part("hand", HAND)                                 # her glove, drawn over the staff it holds
    D.part("ribbons", [(0, 50), (17, 47), (18, 69), (0, 69)])
    D.part("upper", D.poly([(0, 0), (42, 0), (42, 50), (0, 50)]) & D.rest(), take=False)
    D.part("legs", D.rest(), take=False)
    return D


def pose(rig, up=(0, 0), staff=0, rib=0, whole=(0, 0), lift=0):
    """up: the upper body (with the staff) over the legs; staff: degrees about her grip (clockwise points it forward);
    rib: rows the ribbons' ends lift; whole: the whole figure (she floats: negative dy rises); lift: rows the staff
    slides up through her hand (raised high)."""
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    st = ("staff", dict(dx=ux, dy=uy - lift, angle=staff, about=GRIP))
    behind = staff < -25 or staff > 5
    layers = [("ribbons", dict(dx=wx, dy=wy, sway=(0, 18, rib, "right"))),
              ("legs", dict(dx=wx, dy=wy))] + \
        ([st] if behind else []) + [("upper", dict(dx=ux, dy=uy))] + ([] if behind else [st]) + \
        [("hand", dict(dx=ux, dy=uy))]
    return R.compose(rig, layers)


def frames(rig):
    out = {}
    out["idle"] = [pose(rig, whole=(0, -w), rib=r) for w, r in zip([0, 1, 1, 2, 2, 1, 1, 0], [0, 1, 2, 2, 1, 0, 0, 0])]
    out["run"] = [pose(rig, up=(1, 0), whole=(0, -w), rib=r) for w, r in
                  zip([1, 2, 2, 1, 1, 2, 2, 1], [1, 2, 3, 2, 1, 2, 3, 2])]
    out["attack"] = [pose(rig, up=u, staff=s) for u, s in
                     [((0, 0), -20), ((-1, 0), 10), ((1, 0), -50), ((2, 0), -70), ((1, 0), -40), ((0, 0), 0)]]
    out["skill"] = [pose(rig, up=u, staff=s, rib=r) for u, s, r in
                    [((-1, 0), 10, 1), ((-1, 0), 15, 2), ((1, 0), -40, 2), ((2, 0), -70, 3), ((1, 0), -50, 2),
                     ((0, 0), -10, 1)]]
    out["skill2"] = [pose(rig, up=u, staff=s) for u, s in
                     [((0, 0), -15), ((1, 0), -35), ((1, 0), -55), ((1, 0), -55), ((0, 0), -30), ((0, 0), 0)]]
    out["ult"] = [pose(rig, staff=s, lift=l, whole=(0, -w), rib=r) for s, l, w, r in
                  [(-5, 2, 1, 1), (-10, 4, 2, 2), (-15, 6, 3, 3), (-15, 7, 3, 3), (-15, 7, 3, 2), (-15, 6, 2, 2)]]
    out["ult_loop"] = [pose(rig, staff=-15, lift=6, whole=(0, -w), rib=r) for w, r in
                       zip([3, 3, 4, 4, 3, 3], [2, 3, 3, 2, 2, 3])]
    out["hit"] = [R.flash(pose(rig, whole=(-2, 0), staff=10)), pose(rig, whole=(-1, 0), staff=5)]
    # lying: the staff upright before the turn, so it lies along her body
    lying = R.lie(rig, pose(rig, staff=0), k=1, dx=-2)
    out["dead"] = [pose(rig, whole=(-1, 0), staff=10), pose(rig, whole=(-2, 0), up=(-1, 2), staff=-15),
                   pose(rig, up=(0, 5), staff=-35), R.lie(rig, pose(rig, up=(0, 5), staff=0), k=1, dx=-1),
                   lying, lying.copy()]
    ms = {t: [m for _, m in fr] for t, fr in R.sheet_of(HERO).items()}
    return {t: list(zip(f, ms[t])) for t, f in out.items()}


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
