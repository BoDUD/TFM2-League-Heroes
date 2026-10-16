#!/usr/bin/env python3
"""league_leona redone at PPU from Codex's picture (2026-10-16 leona_model_v2), the actions posed from the design
itself (tools/art/ppu_rig.py; the user, 2026-10-16: 「动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」).

    python tools/art/rig_leona_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_leona_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_leona_hd.py                 # orig strips + the 1x sheet; then ppu_restyle / ppu_hd

Parts (design squares at PPU 1.5, 41 game rows): the sword arm (her right arm and the sun sword, drawn from the picture
at any angle about her shoulder), the shield (moved whole: the bash, the guard), both cut out of the picture with the
body they hid filled in; the two legs (league_braum's walk) and the upper body.
Every tag keeps the sheet's frame count and timing.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "leona"
PPU = 1.5
ROWS = 41
PIVOT_COL = 36
SHOULDER = (26.5, 21.5)
SWORD_ARM = [(20, 20), (28, 19), (29, 24), (25, 30), (22, 36), (17, 41), (5, 55), (0, 57), (0, 51), (10, 42), (13, 35),
             (16, 28), (19, 23)]
SHIELD = [(43, 13), (52, 13), (61, 19), (61, 41), (57, 56), (46, 57), (42, 46), (41, 30)]
BAND = 44
SPLIT = 37
WALK = [((0, 0), (0, 4), 1), ((0, 0), (3, 6), 3), ((0, 0), (3, 3), 1), ((0, 0), (3, 0), 0),
        ((0, 4), (0, 0), 1), ((3, 6), (0, 0), 3), ((3, 3), (0, 0), 1), ((3, 0), (0, 0), 0)]


def design():
    D = R.Design(HERO, PPU, ROWS)
    D.px = PIVOT_COL
    D.cut_props({"sword": SWORD_ARM, "shield": SHIELD})
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    op = D.d[..., 3] > 0
    D.part("far_leg", op & (yy > BAND) & (xx > SPLIT))
    D.part("near_leg", op & (yy > BAND) & (xx <= SPLIT))
    D.part("upper", D.rest(), take=False)
    return D


def make_rig(D):
    """The rig, the cracks a step opens between the legs and the skirt closed (from BAND - 6 down)."""
    rig = R.Rig(D)
    rig.fill_rows = (BAND - 6, D.ground)
    rig.idle_canvas = pose(rig)
    return rig


def pose(rig, up=(0, 0), sword=0, shield=(0, 0), whole=(0, 0), near=(0, 0), far=(0, 0)):
    """up: the upper body (with sword and shield) over the legs; sword: degrees the sword arm turns about her shoulder
    (clockwise swings it up behind her and over); shield: its own move; whole: the whole figure; near / far: (columns
    forward, rows lifted) of a leg."""
    D = rig.D
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    layers = []
    for name, (dx, lift) in (("far_leg", far), ("near_leg", near)):
        img = D.layer(name)
        if lift:
            img = img.copy()
            img[:BAND + 1 + lift] = 0
        layers.append((img, dict(dx=wx + dx, dy=wy - lift)))
    layers.append(("upper", dict(dx=ux, dy=uy)))
    layers.append(("sword", dict(dx=ux, dy=uy, angle=sword, about=SHOULDER)))
    layers.append(("shield", dict(dx=ux + shield[0], dy=uy + shield[1], about=SHOULDER)))
    return R.compose(rig, layers)


def frames(rig):
    p = lambda **k: pose(rig, **k)
    out = {}
    out["idle"] = [p(up=(0, b)) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    out["run"] = [p(up=(1, 0), whole=(0, -r), near=n, far=f) for n, f, r in WALK]
    out["attack"] = [p(up=u, sword=s) for u, s in
                     [((-1, 0), -70), ((-1, 0), -140), ((1, 0), -180), ((3, 2), -250), ((1, 1), -30)]]
    # Q Shield of Daybreak: the shield bashed forward
    # (the shield never leaves her arm - moved apart it came off her hand: 「蕾欧娜我都看到手断了」; the bash is her
    # whole upper body lunging)
    out["skill"] = [p(up=u, shield=sh, sword=s) for u, sh, s in
                    [((0, 0), (0, 0), -20), ((-1, 0), (0, 0), -30), ((3, 0), (0, 0), -20), ((4, 1), (0, 0), -10),
                     ((4, 1), (0, 0), -10), ((2, 0), (0, 0), 0), ((1, 0), (0, 0), 0)]]
    # W Eclipse: the shield up before her, braced
    out["skill2"] = [p(up=u, shield=sh) for u, sh in
                     [((1, 1), (0, 0)), ((1, 2), (0, 0)), ((2, 2), (0, 0)), ((2, 2), (0, 0)), ((1, 1), (0, 0)),
                      ((0, 0), (0, 0))]]
    out["e_dash"] = [p(up=(4, 1), sword=-40), p(up=(4, 1), sword=-45)]
    # R Solar Flare: the sword up, brought down
    out["ult"] = [p(up=u, sword=s) for u, s in
                  [((0, 0), -60), ((0, 0), -120), ((-1, 0), -150), ((-1, 0), -170), ((2, 1), -250), ((2, 1), -250),
                   ((1, 0), -20)]]
    out["hit"] = [R.flash(p(whole=(-2, 0), sword=-10)), p(whole=(-1, 0), sword=-5)]
    lying = R.lie(rig, p(sword=0, near=(5, 0), far=(-4, 0)), k=1, dx=-2)
    out["dead"] = [p(whole=(-1, 0), sword=-20), p(whole=(-2, 0), up=(-1, 1), sword=-30),
                   p(up=(0, 4), sword=-10, near=(2, 0), far=(-2, 0)), p(up=(0, 6), sword=0, near=(4, 0), far=(-3, 0)),
                   R.lie(rig, p(up=(0, 6), sword=0, near=(5, 0), far=(-4, 0)), k=1, dx=-1), lying, lying.copy(),
                   lying.copy()]
    ms = {t: [m for _, m in fr] for t, fr in R.sheet_of(HERO).items()}
    for t in out:
        if len(out[t]) != len(ms[t]):
            sys.exit(f"{t}: {len(out[t])} frames posed for {len(ms[t])} in the sheet")
    return {t: list(zip(out[t], ms[t])) for t in ms}


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
    rig = make_rig(D)
    acts = frames(rig)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
