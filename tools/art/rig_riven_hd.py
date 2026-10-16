#!/usr/bin/env python3
"""league_riven redone at PPU from Codex's picture (2026-09-30 riven-ppu-model), the actions posed from the design
itself (tools/art/ppu_rig.py; the user, 2026-10-16: 「动作帧就不让codex做了 参照塔姆那样慢慢做就行了 特效还是老样子」,
and for her the picture's own proportions: 「就现在这样吧锐雯 不用改了」).

    python tools/art/rig_riven_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_riven_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_riven_hd.py                 # orig strips (+ effect layers) + the 1x sheet; then
                                                     # ppu_restyle / ppu_hd

Parts (design squares at PPU 1.5, 40 game rows): the sword arm (her right arm, fist and the broken blade, cut out of
the picture with the leg it hid filled in, drawn from the picture at any angle about her shoulder), the two legs
below the skirt (league_braum's walk: each lifted by losing its top rows, stepped forward), the upper body.
The R tags (attack_r, skill_r, q2_r, q3_r, skill2_r) are the same poses with the blade reforged - the picture's grey
steel turned into a green glow with a light rim. The effects baked into the old frames (assets/source/native/
riven_bake.json: Q slashes, E shield, R aura and wind slash) are laid on the new frames with their own timing.
"""
import argparse
import os
import sys

import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "riven"
PPU = 1.5
ROWS = 40
PIVOT_COL = 22                               # under her waist
SHOULDER = (28.5, 18.5)
SWORD_ARM = [(24, 13), (31, 13), (33, 20), (37, 25), (39, 30), (41, 33), (52, 40), (64, 44), (66, 50), (66, 61),
             (58, 61), (50, 56), (42, 50), (38, 46), (35, 41), (32, 40), (31, 35), (29, 30), (26, 25), (24, 20)]
BAND = 41                                    # legs start below this row
SPLIT = 21                                   # the column between her legs
# league_braum's WALK at PPU 1.5: (near leg (columns forward, rows lifted), far leg, the figure's rise)
WALK = [((0, 0), (0, 4), 1), ((0, 0), (3, 6), 3), ((0, 0), (3, 3), 1), ((0, 0), (3, 0), 0),
        ((0, 4), (0, 0), 1), ((3, 6), (0, 0), 3), ((3, 3), (0, 0), 1), ((3, 0), (0, 0), 0)]


def reforged(pic):
    """The picture with the blade's grey steel green and glowing (R): low-saturation light squares inside the sword
    arm's blade end turned to a green ramp by their brightness, the runes lit, a light green rim round the blade."""
    out = pic.copy()
    rgb = pic[..., :3].astype(int)
    H, W = pic.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    D = DESIGN
    # the blade: the sword arm's polygon right of the fist (design column 40 on)
    bx0 = D.d2p(40, 0)[0]
    from PIL import Image, ImageDraw
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).polygon([D.d2p(x, y) for x, y in SWORD_ARM], fill=1)
    arm = np.asarray(img, bool) & (pic[..., 3] > 0)
    blade = arm & (xx >= bx0)
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    steel = blade & (sat < 40) & (lum > 55)
    rune = blade & (rgb[..., 1] > rgb[..., 0] + 40)
    r, g_, b = rgb[steel, 0], rgb[steel, 1], rgb[steel, 2]
    out[steel, 0] = np.clip(r * 0.72, 0, 255)
    out[steel, 1] = np.clip(g_ * 1.0 + 28, 0, 255)
    out[steel, 2] = np.clip(b * 0.74, 0, 255)
    out[rune, :3] = (200, 255, 190)
    rim = ndimage.binary_dilation(blade, iterations=int(round(0.6 / D.k))) & ~(pic[..., 3] > 0)
    out[rim] = (150, 255, 150, 255)
    return out


DESIGN = None


def design():
    global DESIGN
    D = R.Design(HERO, PPU, ROWS)
    D.px = PIVOT_COL
    DESIGN = D
    # the chest and side the sword arm hid (the arm raised, they show)
    D.cut_props({"sword": SWORD_ARM}, fills=[[(22, 12), (27, 13), (28, 20), (27.5, 27), (27, 33), (22, 33)]])
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    op = D.d[..., 3] > 0
    D.part("far_leg", op & (yy > BAND) & (xx > SPLIT))
    D.part("near_leg", op & (yy > BAND) & (xx <= SPLIT))
    D.part("upper", D.rest(), take=False)
    D.green = reforged(D.pic)
    return D


def make_rig(D):
    """The rig, the cracks a step opens between the legs and the skirt closed (from BAND - 6 down)."""
    rig = R.Rig(D)
    rig.fill_rows = (BAND - 6, D.ground)
    rig.idle_canvas = pose(rig)
    return rig


def hip(D, leg):
    """A leg's top middle column (design squares): it is mirrored about it to close her stance for the fall."""
    ys, xs = np.nonzero(D.parts[leg])
    top = ys <= ys.min() + 2
    return (xs[top].min() + xs[top].max() + 1) / 2


def pose(rig, up=(0, 0), sword=0, whole=(0, 0), near=(0, 0), far=(0, 0), green=False, together=False):
    """up: the upper body (with the sword arm) over the legs; sword: degrees the sword arm turns about her shoulder
    (counter-clockwise raises it); whole: the whole figure; near / far: (columns forward, rows lifted) of a leg
    (league_braum's walk: it loses its top rows); green: the reforged blade; together: the far leg mirrored about
    its hip so both legs run the same way, side by side, slanting back (the fall: whole legs slid together crossed at
    the hips; turned to lie, legs slanting forward pointed up into the air)."""
    D = rig.D
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    layers = []
    for name, (dx, lift) in (("far_leg", far), ("near_leg", near)):
        img = D.layer(name)
        if lift:
            img = img.copy()
            img[:BAND + 1 + lift] = 0
        o = dict(dx=wx + dx, dy=wy - lift)
        if together and name == "far_leg":
            o.update(flip=True, about=(hip(D, "far_leg"), 0))
        layers.append((img, o))
    layers.append(("upper", dict(dx=ux, dy=uy)))
    layers.append(("sword", dict(dx=ux, dy=uy, angle=sword, about=SHOULDER, src=D.green if green else None)))
    return R.compose(rig, layers)


def frames(rig, green=False):
    p = lambda **k: pose(rig, green=green, **k)
    out = {}
    out["attack"] = [p(up=u, sword=s) for u, s in
                     [((-1, 0), 100), ((-1, 0), 140), ((2, 1), 40), ((3, 2), -10), ((2, 1), 0), ((0, 0), 0)]]
    out["skill"] = [p(up=u, sword=s) for u, s in
                    [((-1, 1), 60), ((-1, 1), 120), ((2, 1), 70), ((4, 2), 20), ((4, 2), -10), ((2, 1), 0), ((0, 0), 0)]]
    out["q2"] = [p(up=u, sword=s) for u, s in
                 [((0, 2), -15), ((1, 3), -20), ((2, 1), 40), ((3, 0), 110), ((2, 0), 130), ((1, 0), 60), ((0, 0), 0)]]
    out["q3"] = [p(up=u, sword=s, whole=w) for u, s, w in
                 [((0, 1), 60, (0, -2)), ((0, 0), 130, (0, -8)), ((0, 0), 150, (0, -10)), ((1, 0), 40, (0, -4)),
                  ((1, 3), -15, (0, 0)), ((1, 2), -10, (0, 0)), ((0, 0), 0, (0, 0))]]
    out["skill2"] = [p(up=u, sword=s) for u, s in
                     [((1, 1), -20), ((2, 2), -30), ((3, 2), -35), ((3, 2), -35), ((3, 2), -30), ((2, 1), -20),
                      ((1, 1), -10), ((0, 0), 0)]]
    if green:
        return out
    out["idle"] = [p(up=(0, b)) for b in [0, 0, 1, 1, 1, 1, 0, 0]]
    out["run"] = [p(up=(1, 0), sword=15, whole=(0, -r), near=n, far=f) for n, f, r in WALK]
    out["ult"] = [p(sword=s) for s in (40, 90, 123, 123, 90, 30)]
    out["r_slash"] = [p(up=u, sword=s) for u, s in
                      [((-1, 0), 130), ((-2, 0), 150), ((2, 1), 60), ((4, 2), 10), ((3, 1), 0), ((1, 0), 0)]]
    out["hit"] = [R.flash(p(whole=(-2, 0), sword=10)), p(whole=(-1, 0), sword=5)]
    # lying: her legs side by side first (her stance is wide), the blade up so it runs along her body
    lying = R.lie(rig, p(sword=123, together=True), k=1, dx=-2)
    out["dead"] = [p(whole=(-1, 0), sword=20), p(whole=(-2, 0), up=(-1, 1), sword=40),
                   p(up=(0, 2), sword=10, together=True), p(up=(0, 3), sword=-20, together=True),
                   R.lie(rig, p(up=(0, 3), sword=123, together=True), k=1, dx=-1), lying, lying.copy(), lying.copy()]
    return out


ORDER = ["idle", "run", "attack", "skill", "q2", "q3", "skill2", "ult", "r_slash", "hit", "dead",
         "attack_r", "skill_r", "q2_r", "q3_r", "skill2_r"]


def actions(rig):
    """{tag: [(canvas, ms)]} before the bake: the sheet's timing without the short tails the old bake added."""
    ms = {}
    for t, fr in R.sheet_of(HERO).items():
        m = [v for _, v in fr]
        while m and m[-1] < 10:
            m.pop()
        ms[t] = m
    base = frames(rig)
    green = {t + "_r": f for t, f in frames(rig, green=True).items()}
    acts = {**base, **green}
    out = {}
    for t in ORDER:
        if len(acts[t]) != len(ms[t]):
            sys.exit(f"{t}: {len(acts[t])} frames posed for {len(ms[t])} in the sheet")
        out[t] = list(zip(acts[t], ms[t]))
    return out


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
    acts = actions(rig)
    baked = rig.bake(acts)
    if a.review:
        rig.review(baked, a.review)
        return
    rig.export(baked)


if __name__ == "__main__":
    main()
