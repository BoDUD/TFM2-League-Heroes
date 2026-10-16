#!/usr/bin/env python3
"""league_darius redone at PPU from Codex's picture (2026-10-16 darius_model_v3), the actions posed from the design
itself (tools/art/ppu_rig.py; the user, 2026-10-16: 「动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」).

    python tools/art/rig_darius_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_darius_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_darius_hd.py                 # orig strips + the 1x sheet; then ppu_restyle / ppu_hd

Parts (design squares at PPU 1.5, 42 game rows): the axe arm (the bare arm under the pauldron, the gauntlet and the axe,
cut out of the picture with the leg it hid filled in, drawn from the picture at any angle about his shoulder), the
two legs below the tabard (league_braum's walk), the upper body (head, pauldrons, torso, the other fist, the cape).
Every tag keeps the sheet's frame count and timing.
"""
import argparse
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "darius"
PPU = 1.5
ROWS = 42
PIVOT_COL = 33                               # under his belt
SHOULDER = (22.5, 22.5)
AXE_ARM = [(17, 23), (27, 23), (28, 30), (27, 38), (24, 43), (26, 46), (28, 48), (28, 57), (25, 59), (15, 63), (3, 63),
           (0, 55), (1, 42), (9, 36), (12, 36), (12, 25), (15, 24)]
LEG_EDGE = [(25.5, 45), (29, 45), (29, 59), (25.5, 59)]     # his near leg's edge the axe blade hid
BAND = 46                                    # legs start below this row
SPLIT = 33
WALK = [((0, 0), (0, 4), 1), ((0, 0), (3, 6), 3), ((0, 0), (3, 3), 1), ((0, 0), (3, 0), 0),
        ((0, 4), (0, 0), 1), ((3, 6), (0, 0), 3), ((3, 3), (0, 0), 1), ((3, 0), (0, 0), 0)]


def design():
    D = R.Design(HERO, PPU, ROWS, coarse=True)
    D.px = PIVOT_COL
    # the cape's red behind the arm stays with the body
    D.cut_props({"axe": AXE_ARM}, fills=[LEG_EDGE],
                keep_out=lambda rgb: (rgb[..., 0] > rgb[..., 1] + 50) & (rgb[..., 0] > rgb[..., 2] + 40))
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    rgb = D.d[..., :3].astype(int)
    # the cape hangs from his shoulders: its red stays with the upper body when a leg steps
    cape = (rgb[..., 0] > rgb[..., 1] + 40) & (rgb[..., 0] > rgb[..., 2] + 30)
    cape = ndimage.binary_dilation(cape) & ~(np.abs(rgb[..., 0] - rgb[..., 1]) < 25)
    op = (D.d[..., 3] > 0) & ~cape
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


def pose(rig, up=(0, 0), axe=0, whole=(0, 0), near=(0, 0), far=(0, 0), axe_back=False):
    """up: the upper body (with the axe arm) over the legs; axe: degrees the axe arm turns about his shoulder
    (counter-clockwise swings the axe forward: 90 points it ahead, 180 up); whole: the whole figure; near / far:
    (columns forward, rows lifted) of a leg; axe_back: the axe drawn behind him (the far side of a spin)."""
    D = rig.D
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    layers = []
    ax = ("axe", dict(dx=ux, dy=uy, angle=axe, about=SHOULDER))
    if axe_back:
        layers.append(ax)
    for name, (dx, lift) in (("far_leg", far), ("near_leg", near)):
        img = D.layer(name)
        if lift:
            img = img.copy()
            img[:BAND + 1 + lift] = 0
        layers.append((img, dict(dx=wx + dx, dy=wy - lift)))
    layers.append(("upper", dict(dx=ux, dy=uy)))
    if not axe_back:
        layers.append(ax)
    return R.compose(rig, layers)


def frames(rig):
    p = lambda **k: pose(rig, **k)
    out = {}
    out["idle"] = [p(up=(0, b)) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    out["run"] = [p(up=(1, 0), axe=10, whole=(0, -r), near=n, far=f) for n, f, r in WALK]
    # swings: the axe raised behind him (clockwise, so his arm never crosses his face), over the top and down ahead
    out["attack"] = [p(up=u, axe=a) for u, a in
                     [((-1, 0), -110), ((-1, 0), -165), ((2, 1), 100), ((3, 2), 40), ((2, 1), 15), ((0, 0), 0)]]
    # Q Decimate: the axe swung all the way round him, behind him on the far half
    out["skill"] = [p(up=u, axe=a, axe_back=b) for u, a, b in
                    [((0, 1), -40, False), ((0, 2), -100, True), ((0, 2), -170, True), ((0, 2), -240, False),
                     ((0, 2), -300, False), ((0, 2), -380, False), ((0, 1), -420, False), ((0, 0), -360, False)]]
    out["w_attack"] = [p(up=u, axe=a) for u, a in
                       [((-1, 0), -140), ((-1, 0), -175), ((2, 1), 110), ((3, 3), 45), ((2, 2), 20), ((0, 0), 0)]]
    # E Apprehend: the axe thrown forward, the hook pulled back
    out["skill2"] = [p(up=u, axe=a) for u, a in
                     [((-1, 0), 50), ((1, 0), 110), ((3, 0), 135), ((3, 0), 135), ((1, 0), 105), ((-1, 0), 60),
                      ((-1, 0), 25), ((0, 0), 0)]]
    # R Noxian Guillotine: leap, the axe over his head, the slam
    out["ult"] = [p(up=u, axe=a, whole=w) for u, a, w in
                  [((0, 2), -120, (0, 0)), ((0, 0), -170, (0, -6)), ((0, 0), -185, (0, -10)), ((1, 0), 160, (0, -10)),
                   ((2, 2), 90, (0, -3)), ((2, 3), 30, (0, 0)), ((1, 2), 20, (0, 0)), ((0, 0), 0, (0, 0))]]
    out["hit"] = [R.flash(p(whole=(-2, 0), axe=10)), p(whole=(-1, 0), axe=5)]
    lying = R.lie(rig, p(axe=180, near=(4, 0), far=(-4, 0)), k=1, dx=-2)
    out["dead"] = [p(whole=(-1, 0), axe=20), p(whole=(-2, 0), up=(-1, 1), axe=40),
                   p(up=(0, 4), axe=60, near=(2, 0), far=(-2, 0)),
                   R.lie(rig, p(up=(0, 6), axe=180, near=(4, 0), far=(-4, 0)), k=1, dx=-1), lying, lying.copy(),
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
