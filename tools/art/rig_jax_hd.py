#!/usr/bin/env python3
"""league_jax redone at PPU from Codex's picture (2026-10-16 jax_model_v1) made chibi (tools/art/chibi_warp.py; the user:
「贾克斯要做成Q版的 现在太逼真了」), the actions posed from the design itself (tools/art/ppu_rig.py; 「动作帧就不让codex做了
参照塔姆那样慢慢做就行了 特效还是老样子」).

    python tools/art/rig_jax_hd.py --parts DIR     # the design with its parts tinted (8x)
    python tools/art/rig_jax_hd.py --review DIR    # every tag at 3x + GIFs (nothing written to the repo)
    python tools/art/rig_jax_hd.py                 # orig strips + the 1x sheet; then ppu_restyle / ppu_hd

Parts (design squares at PPU 1.5, 36 game rows hood to soles): the lamp post (the lantern and the post above his fist,
the post and its foot below it - cut out of the picture with what they hid filled in, drawn from the picture at any
angle about his grip, the post itself a straight line), his fist drawn again over it, the two legs (league_braum's
walk), the upper body. The post turns in his hand (a turn about the shoulder put his fist up by his hood for the slam).
Every tag keeps the sheet's frame count and timing.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "jax"
PPU = 1.5
ROWS = 36
PIVOT_COL = 36
GRIP = (15.0, 30.5)                          # the post in his fist
SHOULDER = (25.5, 30.0)                      # his lamp arm's root under the robe
ARM = [(10, 26.5), (26.5, 25.5), (28, 34), (25, 35), (10, 34.5)]   # the arm and the fist (cut, drawn at any angle)
TORSO_BEHIND_ARM = [(19, 25), (28.5, 25), (28.5, 35.5), (19, 35.5)]
LAMP_TOP = [(5, -1), (16, -1), (16.5, 16), (16, 27.5), (11, 27.5), (11, 16), (5, 16)]
LAMP_LOW = [(13, 33.5), (18, 33.5), (21, 50), (23, 56.5), (16, 56.5), (16.5, 50)]
BAND = 45
SPLIT = 37
WALK = [((0, 0), (0, 3), 1), ((0, 0), (2, 5), 2), ((0, 0), (2, 2), 1), ((0, 0), (2, 0), 0),
        ((0, 3), (0, 0), 1), ((2, 5), (0, 0), 2), ((2, 2), (0, 0), 1), ((2, 0), (0, 0), 0)]


def design():
    D = R.Design(HERO, PPU, ROWS, chibi=True)
    D.px = PIVOT_COL
    D.cut_props({"lamp": LAMP_TOP, "foot": LAMP_LOW, "arm": ARM}, fills=[TORSO_BEHIND_ARM])
    # the post: a straight line at every angle, from his fist
    D.shaft("lamp", GRIP, (12.8, 14), 1.6)
    D.shaft("foot", GRIP, (18.8, 52), 1.6)
    yy, xx = np.mgrid[0:D.H, 0:D.W]
    op = D.d[..., 3] > 0
    D.part("far_leg", op & (yy > BAND) & (xx > SPLIT))
    D.part("near_leg", op & (yy > BAND) & (xx <= SPLIT))
    D.part("upper", D.rest(), take=False)
    return D


def turn_point(p, about, deg):
    th = np.radians(deg)
    ax, ay = about
    return (ax + (p[0] - ax) * np.cos(th) + (p[1] - ay) * np.sin(th),
            ay - (p[0] - ax) * np.sin(th) + (p[1] - ay) * np.cos(th))


def make_rig(D):
    """The rig, the cracks a step opens between the legs and the skirt closed (from BAND - 6 down)."""
    rig = R.Rig(D)
    rig.fill_rows = (BAND - 6, D.ground)
    rig.idle_canvas = pose(rig)
    return rig


def pose(rig, up=(0, 0), lamp=0, whole=(0, 0), near=(0, 0), far=(0, 0), back=None, arm=0):
    """up: the upper body (with the lamp) over the legs; arm: degrees his lamp arm turns about the shoulder
    (counter-clockwise swings it down and forward under him - League's sweep); lamp: degrees the post turns (about his
    fist, which the arm carries: clockwise brings the lantern over and down ahead of him); whole: the whole figure;
    near / far: (columns forward, rows lifted) of a leg; back: the lamp behind him (the far side of a twirl; None: when
    the arm hangs and the lantern goes over his hood)."""
    D = rig.D
    wx, wy = whole
    ux, uy = up[0] + wx, up[1] + wy
    layers = []
    if back is None:
        # on its way over (the lantern from straight up to low ahead) the post would cross his hood: behind him then;
        # the strike (the lantern low ahead) is in front
        back = arm == 0 and -150 < lamp < -15
    gx, gy = turn_point(GRIP, SHOULDER, arm)
    sx, sy = int(round(gx - GRIP[0])), int(round(gy - GRIP[1]))
    lp_ = [("lamp", dict(dx=ux + sx, dy=uy + sy, angle=lamp, about=GRIP)),
           ("foot", dict(dx=ux + sx, dy=uy + sy, angle=lamp, about=GRIP)),
           ("arm", dict(dx=ux, dy=uy, angle=arm, about=SHOULDER))]
    if back:
        layers += lp_
    for name, (dx, lift) in (("far_leg", far), ("near_leg", near)):
        img = D.layer(name)
        if lift:
            img = img.copy()
            img[:BAND + 1 + lift] = 0
        layers.append((img, dict(dx=wx + dx, dy=wy - lift)))
    layers.append(("upper", dict(dx=ux, dy=uy)))
    if not back:
        layers += lp_
    return R.compose(rig, layers)


def frames(rig):
    p = lambda **k: pose(rig, **k)
    out = {}
    out["idle"] = [p(up=(0, b)) for b in [0, 1, 1, 1, 0, 0]]
    out["run"] = [p(up=(1, 0), lamp=-10, whole=(0, -r), near=n, far=f) for n, f, r in WALK]
    # auto attacks after League's clips (tools/lol/native_pose.py assets/source/jax/poses.json; 「贾克斯平A姿势和英雄联盟
    # 不一样」): the lamp drawn back behind him, swept low and forward under him, the lantern ahead; the crit (W) brought
    # over his head and slammed down ahead of him. (whole move, arm angle, lantern angle: a lantern pointing along
    # the arm has lamp = arm + 83)
    # (whole move, arm angle, lantern angle; the lantern's direction on screen is 97 + lamp degrees, the arm's 180 + arm)
    # (the lantern kept at shoulder height ahead: raised by his hood it crowded his face)
    sweep = [((0, 0), 10, 13), ((-1, 0), -10, 53), ((-1, 0), 0, 83), ((1, 0), 150, -77), ((3, 0), 180, -97),
             ((1, 0), 120, -70)]
    out["attack"] = [p(whole=w, arm=a, lamp=b) for w, a, b in sweep]
    out["attack_e"] = [p(whole=w, arm=a, lamp=b) for w, a, b in sweep]
    out["attack_r"] = [p(whole=w, arm=a, lamp=b) for w, a, b in
                       [((0, 0), 10, 18), ((-1, 0), -10, 58), ((-1, 0), 0, 88), ((2, 0), 150, -77),
                        ((4, 0), 182, -99), ((1, 0), 120, -70)]]
    out["attack_w"] = [p(whole=w, arm=a, lamp=b) for w, a, b in
                       [((0, 0), -150, -87), ((-1, 0), -40, 40), ((-1, 0), -30, 70), ((2, 0), -205, -150),
                        ((2, 0), -210, -152), ((1, 0), -195, -120)]]
    # Q Leap Strike: up with the lantern raised, down on the target
    out["skill"] = [p(up=u, lamp=a, whole=w) for u, a, w in
                    [((0, 2), 10, (0, 0)), ((0, 0), 20, (0, -6)), ((0, 0), 0, (0, -9)), ((1, 0), -60, (0, -7)),
                     ((2, 3), -165, (0, 0)), ((1, 2), -160, (0, 0)), ((0, 0), -50, (0, 0))]]
    # E Counter Strike: the lamp twirled round him, behind him on the far half
    out["skill2"] = [p(lamp=a, back=b) for a, b in
                     [(-60, False), (-150, True), (-240, True), (-330, False), (-420, False), (-510, True)]]
    out["skill2_burst"] = [p(up=u, lamp=a) for u, a in
                           [((0, 0), -20), ((-1, 0), 20), ((2, 3), -160), ((2, 3), -165), ((1, 1), -80), ((0, 0), 0)]]
    # R Grandmaster's Might: the lantern raised high, brought down
    out["ult"] = [p(up=u, lamp=a) for u, a in
                  [((0, 0), 10), ((0, 0), 25), ((0, 0), 30), ((0, 0), 30), ((2, 2), -165), ((2, 2), -170),
                   ((1, 0), -40)]]
    out["hit"] = [R.flash(p(whole=(-2, 0), lamp=10)), p(whole=(-1, 0), lamp=5)]
    # lying: the lamp upright before the turn, so it lies along him
    lying = R.lie(rig, p(lamp=0, near=(4, 0), far=(-3, 0)), k=1, dx=-2)
    out["dead"] = [p(whole=(-1, 0), lamp=15), p(whole=(-2, 0), up=(-1, 1), lamp=25),
                   p(up=(0, 3), lamp=10, near=(2, 0), far=(-1, 0)), p(up=(0, 5), lamp=5, near=(3, 0), far=(-2, 0)),
                   R.lie(rig, p(up=(0, 5), lamp=0, near=(4, 0), far=(-3, 0)), k=1, dx=-1), lying, lying.copy(),
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
