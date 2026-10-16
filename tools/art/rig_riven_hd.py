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
# her legs jointed (「锐雯腿部有点变形」: stepped league_braum's way they lost their top rows and slid under the skirt):
# thigh and lower leg drawn from the picture, turned about hip and knee, the knee solved at her own lengths
# her legs, each one rigid piece drawn from the picture and turned about her hip (「锐雯的腿还是变形吧」: bent at the
# knee - a thigh and a lower leg turned apart - the knee showed a step). (hip, knee, sole) in design squares
NEAR = ((15.5, 33.2), (9, 44.2), (3.5, 58.8))
FAR = ((27.5, 34.5), (34.5, 45.5), (42, 59.3))
# the run after League's (tools/lol/native_pose.py assets/source/riven/poses.json run). Straight legs swung from the
# hips (「你觉得对吗 两个腿这样走路的？」) and a wide stance barely moved (「锐雯走路姿势不对啊」) were both wrong: a run bends
# the knees - the front leg reaching with the knee nearly straight, the back leg pushing off and the foot kicked up
# behind with the shin folded. Both legs are her far (right) leg cut from the picture in two - the thigh (its top
# carried on up under the skirt) and the shin with the boot, the knee's wrap shared so the joint never opens - because
# its boot points forward (the near boot in the picture points out to the left: running right, that foot pointed back).
# Per phase (thigh, shin) in degrees from straight down, positive = the foot forward; the near leg in phase i, the far
# leg 4 phases on; the body set so the lower sole stands on the ground; hips 3 columns in each under the skirt.
RUN_GAIT = [(28, 6), (16, -6), (2, -10), (-14, -24), (-26, -56), (-14, -96), (14, -74), (32, -22)]
RUN_HIPS = (3, -3)
RUN_LEAN = 2                                 # columns her upper body leans ahead of her hips
RUN_SWORD = [26, 24, 22, 24, 26, 24, 22, 24]
# the run leg in picture pixels (the far leg): its outline region, the knee line, the sword's lower edge to keep out
RUN_LEG_AREA = [(312, 405), (402, 405), (428, 468), (472, 540), (478, 600), (525, 640), (600, 676), (600, 756),
                (440, 756), (432, 700), (392, 640), (372, 580), (336, 520), (306, 468)]
SWORD_EDGE = ((420, 476), (600, 640))       # picture pixels above this line (right of x 420) are the sword's


def vertical(leg):
    """Degrees that turn the leg (hip to sole) straight down."""
    (hx, hy), _, (sx, sy) = leg
    return -float(np.degrees(np.arctan2(sx - hx, sy - hy)))


def leg_props(name, leg):
    """The thigh and the lower leg (with the boot, a square past the sole) as polygons for Design.cut_props - both
    turned alike about the hip, one rigid leg."""
    hip, knee, sole = (np.array(v, float) for v in leg)
    d = sole - knee
    end = sole + d / np.hypot(*d) * 1.2
    return {name + "_thigh": R.band(tuple(hip), tuple(knee), 3.3, 3.0),
            name + "_lower": R.band(tuple(knee), tuple(end), 3.3, 4.6)}


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
    # the chest and side the sword arm hid (the arm raised, they show); the legs hide nothing (close=0: closed over,
    # the gap between them came back as body)
    D.cut_props({"sword": SWORD_ARM, **leg_props("n", NEAR), **leg_props("f", FAR)}, close=0,
                fills=[[(22, 12), (27, 13), (28, 20), (27.5, 27), (27, 33), (22, 33)]])
    D.part("upper", D.rest(), take=False)
    D.green = reforged(D.pic)
    run_legs(D)
    return D


def make_rig(D):
    """The rig (her jointed legs open no cracks to close)."""
    return R.Rig(D)


def pose(rig, up=(0, 0), sword=0, whole=(0, 0), near=0, far=0, green=False, lift=(0, 0), hips=(0, 0), lean=0):
    """up: the upper body moved - sideways with her hips and legs (a lunge slides her feet), down at most a row over
    them (breath; lower, the body sank into the legs); sword: degrees the sword arm turns about her shoulder
    (counter-clockwise raises it); whole: the whole figure; near / far: degrees a leg turns about its hip
    (counter-clockwise on screen); green: the reforged blade; lift: rows the near / far leg goes up (its top under
    her skirt); hips: columns the near / far leg moves sideways under her skirt; lean: columns the upper body moves
    ahead of the hips (the legs' tops stay under the skirt)."""
    D = rig.D
    wx, wy = whole[0] + up[0], whole[1]
    layers = []
    for name, leg, ang, up_, hx in (("f", FAR, far, lift[1], hips[1]), ("n", NEAR, near, lift[0], hips[0])):
        for piece in ("_thigh", "_lower"):
            layers.append((name + piece, dict(dx=wx + hx, dy=wy - up_, angle=ang, about=leg[0])))
    ux, uy = wx + lean, wy + min(up[1], 1)
    layers.append(("upper", dict(dx=ux, dy=uy)))
    layers.append(("sword", dict(dx=ux, dy=uy, angle=sword, about=SHOULDER, src=D.green if green else None)))
    return R.compose(rig, layers)


def run_legs(D):
    """The run's thigh and shin (Design props "run_thigh", "run_shin") from the far leg in the picture: the leg's own
    pixels (skin, wraps, leather, boot, outline; not the skirt's greens, not the sword), split across the knee with an
    overlap (the thigh to 1.6 squares below the knee, the shin from 1.8 above it); the thigh's top row carried on up
    along the thigh to 2 squares above the hip, under the skirt, so no gap opens there when it turns. D.run_src is the
    picture with that extension painted in."""
    from PIL import Image, ImageDraw
    pic = D.pic
    H, W = pic.shape[:2]
    img = Image.new("L", (W, H), 0)
    ImageDraw.Draw(img).polygon(RUN_LEG_AREA, fill=1)
    area = np.asarray(img, bool) & (pic[..., 3] > 0)
    yy, xx = np.mgrid[0:H, 0:W]
    (sx0, sy0), (sx1, sy1) = SWORD_EDGE
    area &= ~((xx > sx0) & (yy < sy0 + (xx - sx0) * (sy1 - sy0) / (sx1 - sx0)))
    rgb = pic[..., :3].astype(int)
    skirt = (rgb[..., 1] >= rgb[..., 0] - 12) & (rgb[..., 2] < rgb[..., 1] - 12) & (rgb.sum(-1) > 90)
    leg = area & ~skirt
    # the leg is the biggest piece of that (skirt crumbs and strap ends off)
    lbl, n = ndimage.label(leg, structure=np.ones((3, 3)))
    sz = ndimage.sum(leg, lbl, range(1, n + 1))
    leg = lbl == (1 + int(np.argmax(sz)))
    leg = ndimage.binary_fill_holes(leg) & (pic[..., 3] > 0)
    hip, knee = (np.array(D.d2p(*v)) for v in (FAR[0], FAR[1]))
    u = (knee - hip) / np.hypot(*(knee - hip))
    along = (xx - knee[0]) * u[0] + (yy - knee[1]) * u[1]       # picture px past the knee, along the thigh
    sq = 1 / D.k
    thigh = leg & (along <= 1.6 * sq)
    shin = leg & (along >= -1.8 * sq)
    # the thigh carried up: each picture row above its top visible row copies that row, moved along the thigh
    src = pic.copy()
    rows = np.nonzero(thigh.any(1))[0]
    top = rows.min() + 2
    ref = np.nonzero(thigh[top])[0]
    for y in range(int(hip[1] - 2 * sq), top):
        dx = int(round((y - top) * u[0] / u[1]))
        xs = ref + dx
        ok = (xs >= 0) & (xs < W)
        src[y, xs[ok]] = pic[top, ref[ok]]
        thigh[y, xs[ok]] = True
    for name, m in (("run_thigh", thigh), ("run_shin", shin)):
        D.props.add(name)
        D.prop_masks[name] = m
        D.polys[name] = RUN_LEG_AREA
    D.run_src = src


def turned_point(p, about, deg):
    """p turned deg counter-clockwise on screen about `about` (design squares)."""
    th = np.radians(deg)
    ax, ay = about
    return np.array((ax + (p[0] - ax) * np.cos(th) + (p[1] - ay) * np.sin(th),
                     ay - (p[0] - ax) * np.sin(th) + (p[1] - ay) * np.cos(th)))


def heading(v):
    """Degrees from straight down of a design vector, positive = toward +x (forward)."""
    return float(np.degrees(np.arctan2(v[0], v[1])))


def run_leg(hip_to, t1, t2, dx, dy):
    """compose() layers (shin first, then the thigh over the knee) for a run leg with its hip at hip_to (design
    squares, before the whole move dx, dy), the thigh at t1 and the shin at t2 degrees from straight down. -> (layers,
    sole design position)."""
    hip, knee, sole = (np.array(v, float) for v in FAR)
    r1 = round((t1 - heading(knee - hip)) / 2) * 2
    r2 = round((t2 - heading(sole - knee)) / 2) * 2
    hx, hy = int(round(hip_to[0] - hip[0])), int(round(hip_to[1] - hip[1]))
    k_at = turned_point(knee, hip, r1) + (hx, hy)
    kx, ky = int(round(k_at[0] - knee[0])), int(round(k_at[1] - knee[1]))
    s_at = turned_point(sole, knee, r2) + (kx, ky)
    src = DESIGN.run_src
    return [("run_shin", dict(dx=kx + dx, dy=ky + dy, angle=r2, about=tuple(knee), src=src)),
            ("run_thigh", dict(dx=hx + dx, dy=hy + dy, angle=r1, about=tuple(hip), src=src))], s_at


def run_frame(rig, i):
    D = rig.D
    up = (1, 0)
    legs, soles = [], []
    for leg, ph, hx in ((FAR, (i + 4) % 8, RUN_HIPS[1]), (NEAR, i, RUN_HIPS[0])):
        hip_to = (leg[0][0] + hx, leg[0][1])
        lay, sole = run_leg(hip_to, *RUN_GAIT[ph], 0, 0)
        legs.append(lay)
        soles.append(sole)
    drop = int(round(FAR[2][1] - max(s[1] for s in soles)))    # the lower sole on the ground
    wx, wy = up[0], drop
    layers = []
    for lay in legs:
        for name, o in lay:
            o = dict(o)
            o["dx"] += wx
            o["dy"] += wy
            layers.append((name, o))
    layers.append(("upper", dict(dx=wx + RUN_LEAN, dy=wy)))
    layers.append(("sword", dict(dx=wx + RUN_LEAN, dy=wy, angle=RUN_SWORD[i], about=SHOULDER)))
    return R.compose(rig, layers)


def lying(rig, sword=123):
    """Lying: her legs turned straight down first, then the whole figure a quarter turn (lossless)."""
    return R.lie(rig, pose(rig, sword=sword, near=vertical(NEAR), far=vertical(FAR)), k=1, dx=-2)


def frames(rig, green=False):
    p = lambda **k: pose(rig, green=green, **k)
    out = {}
    # after League's clip (tools/lol/native_pose.py assets/source/riven/poses.json; 「锐雯的平A也不太一样」): the blade
    # held up, raised, a lunging cut down ahead of her (she slides in), low, back up level.
    # Sword angles: 0 hanging as drawn, +48 level ahead, +138 upright
    out["attack"] = [p(up=u, sword=s) for u, s in
                     [((0, 0), 100), ((-1, 0), 130), ((4, 2), 30), ((6, 3), -12), ((5, 3), -18), ((2, 1), 48)]]
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
    out["run"] = [run_frame(rig, i) for i in range(8)]
    out["ult"] = [p(sword=s) for s in (40, 90, 123, 123, 90, 30)]
    out["r_slash"] = [p(up=u, sword=s) for u, s in
                      [((-1, 0), 130), ((-2, 0), 150), ((2, 1), 60), ((4, 2), 10), ((3, 1), 0), ((1, 0), 0)]]
    out["hit"] = [R.flash(p(whole=(-2, 0), sword=10)), p(whole=(-1, 0), sword=5)]
    # lying: her legs turned straight down first (her stance is wide), the blade up so it runs along her body
    lie = lying(rig) if not green else None
    out["dead"] = [p(whole=(-1, 0), sword=20), p(whole=(-2, 0), sword=40), p(whole=(-3, 0), sword=10, up=(0, 1)),
                   p(whole=(-3, 0), sword=-20, up=(0, 1)), lie, lie.copy(), lie.copy(), lie.copy()]
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
