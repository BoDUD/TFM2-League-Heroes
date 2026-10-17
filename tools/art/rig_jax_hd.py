#!/usr/bin/env python3
"""league_jax redone at PPU from Codex's picture of the chibi design turned 3/4 front-right like every hero
(assets/source/jax/PICTURE_PROMPT.md, 2026-10-16: the first picture faced the camera - 「你不应该学其他已经完美的英雄四分之三站姿
吗」, 「这是右前方？」 on the mirrored copy - and the user picked a Codex redraw), every action posed after League's own
clip, frame by frame (「锐雯诺手贾克斯还有曙光和娜美的动作极度没有还原LOL里面」): tools/lol/league_joints.py reads League's
skeleton through native_pose's camera and ppu_rig.Driver turns the design's parts with it.

    python tools/art/rig_jax_hd.py --prepare assets/source/jax/hd/codex.png        # assets/source/jax/hd/picture.png
    python tools/lol/league_joints.py assets/source/jax/poses.json --out <dir>     # League's joints (once)
    python tools/art/rig_jax_hd.py --joints <dir>/jax_joints.json --parts DIR      # the parts tinted (8x)
    python tools/art/rig_jax_hd.py --joints <dir>/jax_joints.json --review DIR     # every tag at 3x + GIFs
    python tools/art/rig_jax_hd.py --joints <dir>/jax_joints.json                  # orig strips + the 1x sheet

--prepare makes the design's picture from Codex's (assets/source/jax/hd/codex.png, its jax-A.png as delivered): its soft glow cut (alpha at one half) and the lantern set on the
post's axis - Codex drew it upright with the post going into its side (the user: 「贾克斯灯笼反了」): the lantern is cut
off, its foot spike dropped, and it is turned so its base sits on the post's collar and its roof points on along the
post, as a street lamp's head sits on its post.

Parts (design squares at PPU 1.5, 36 game rows hood to soles): the lamp (cap, post, collar and lantern; the post a
straight line) turned about his grip with League's weapon, his lamp arm with the fist turned about the shoulder with
League's shoulder-to-hand (carrying the grip, the fist over the post), both legs as thigh and shin turned with League's
(leg_masks: the shin overlaps the thigh over the knee), the upper body moved with League's pelvis and leaning with its
chest. The seven eye dots are set again square by square (a ring of six and one in the middle; read back from the
picture they ran together). The death ends lying: the figure a quarter turn. Every tag keeps the sheet's frame count
and timing.
"""
import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402

HERO = "jax"
PPU = 1.5
ROWS = 36
SPEC_HEIGHT = 34                             # assets/source/jax/poses.json "height"
PICTURE = os.path.join(R.ROOT, "assets", "source", HERO, "hd", "picture.png")

# --prepare, in Codex's picture pixels (1536 x 1024)
POST = ((430.0, 621.0), (1030.0, 853.5))     # two points on the post's centre line
LANTERN_BOX = (1108, 785, 1250, 1012)        # the lantern (with its foot spike and the collar's right ring)
COLLAR = (1117, 908)                         # left of x and above y in the box: the collar, kept on the post
SPIKE_Y = 959                                # the foot spike below this row, dropped
LANTERN_BASE = (1165.0, 958.0)               # the middle of the lantern's base plate
LANTERN_ROOF = (1175.0, 795.0)               # the roof's tip
SEAT_X = 1114.0                              # the base sits on the post here (the collar's right face)


def prepare(raw):
    """Codex's jax-A.png -> the design's picture (see the module's doc)."""
    a = np.asarray(Image.open(raw).convert("RGBA")).copy()
    a[..., 3] = np.where(a[..., 3] >= 128, 255, 0)
    a[a[..., 3] == 0] = 0
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    x0, y0, x1, y1 = LANTERN_BOX
    box = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1) & (a[..., 3] > 0)
    collar = box & (xx < COLLAR[0]) & (yy < COLLAR[1])
    old = box & ~collar
    lantern = old & (yy < SPIKE_Y)
    # the lantern alone on a square canvas, its base in the middle
    n = 480
    can = np.zeros((n, n, 4), np.uint8)
    bx, by = int(round(LANTERN_BASE[0])), int(round(LANTERN_BASE[1]))
    ys, xs = np.nonzero(lantern)
    can[ys - by + n // 2, xs - bx + n // 2] = a[ys, xs]
    # turned so base -> roof runs along the post (grip -> lantern)
    (px0, py0), (px1, py1) = POST
    post = R.heading((px1 - px0, py1 - py0))
    axis = R.heading((LANTERN_ROOF[0] - LANTERN_BASE[0], LANTERN_ROOF[1] - LANTERN_BASE[1]))
    rot = np.asarray(Image.fromarray(can).rotate(post - axis, resample=Image.BICUBIC, center=(n // 2, n // 2)))
    rot = rot.copy()
    rot[..., 3] = np.where(rot[..., 3] >= 128, 255, 0)
    a[old] = 0
    sx = SEAT_X
    sy = py0 + (py1 - py0) * (sx - px0) / (px1 - px0)
    ys, xs = np.nonzero(rot[..., 3])
    ty, tx = ys + int(round(sy)) - n // 2, xs + int(round(sx)) - n // 2
    ok = (ty >= 0) & (ty < H) & (tx >= 0) & (tx < W)
    a[ty[ok], tx[ok]] = rot[ys[ok], xs[ok]]
    Image.fromarray(a).save(PICTURE, optimize=True)
    print("written", PICTURE)


# the design (squares; the post's centre line y = POST_Y0 + POST_K x)
PIVOT_COL = 34                               # between his feet
POST_Y0, POST_K = 22.16, 0.3875


def on_post(x):
    return (x, POST_Y0 + POST_K * x)


GRIP = on_post(24.5)                         # his near fist round the post
LANTERN = (72.1, 50.1)                       # the lantern's roof tip, on the post's line
CAP = on_post(6.5)                           # the post's end under the cap
COLLAR = on_post(55.8)                       # the post's end in the collar
SHOULDER = (24.5, 20.5)                      # under the pauldron
CHEST = (34.0, 26.0)                         # League's chest joint on him
ARM = [(18.5, 22.5), (27.5, 22.5), (28, 27), (27.8, 34.8), (21.3, 34.8), (19, 31), (18, 27)]
TORSO_BEHIND_ARM = [(18.5, 22.5), (28, 22.5), (28, 35), (19, 35)]
LAMP = [(-1, 20.5), (8.5, 20.5), (8.5, 23.4), (55.5, 42.4), (57, 37.5), (68, 41), (74, 47), (74, 53), (66, 56),
        (57, 52), (55.5, 45.4), (8.5, 26.4), (8.5, 28.5), (-1, 28.5)]
# the legs below the robe: navy trousers, bronze greaves, brown boots
NEAR = dict(name="nl", side="near", rigid=True, hip=(25.0, 37.5), knee=(23.5, 40.0), sole=(22.0, 54.0),
            area=[(21, 39), (29, 39), (28.5, 44), (27.5, 50), (27, 55), (17, 55), (17.5, 50), (20.5, 44)])
FAR = dict(name="fl", side="far", rigid=True, hip=(44.5, 38.5), knee=(44.5, 43.0), sole=(45.0, 53.0),
           area=[(41, 38), (48.5, 38), (48.5, 44), (51, 49), (51, 54.5), (39, 54.5), (40, 49), (41.5, 44)])
# the seven eye dots (squares): a ring of six round one, a little right of the mask's middle (he looks front-right)
EYES = [(43, 15), (42, 13), (44, 13), (41, 15), (45, 15), (42, 17), (44, 17)]
EYE_BOX = (38, 11, 48, 20)                   # columns / rows the picture's eye squares are cleared in


def robe(rgb):
    """The robe's purples and pinks (not the navy trousers nor the brown boots)."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    return (b - g > 22) & (r - g > 12) & (rgb.sum(-1) > 150)


def eyes(D):
    """The eye squares the read-back ran together set again: the box's warm squares to the mask's dark, then the seven
    dots in the picture's brightest eye yellow."""
    d = D.d
    x0, y0, x1, y1 = EYE_BOX
    box = d[y0:y1, x0:x1]
    rgb = box[..., :3].astype(int)
    warm = (box[..., 3] > 0) & (rgb[..., 0] > 110) & (rgb[..., 1] > 70) & (rgb[..., 2] < rgb[..., 1] - 30)
    dark = (box[..., 3] > 0) & (rgb.sum(-1) < 90)
    mask_c = np.median(rgb[dark], 0).astype(np.uint8) if dark.any() else np.array((20, 12, 24), np.uint8)
    p = D.pic[..., :3].astype(int)
    eye = (p[..., 0] > 200) & (p[..., 1] > 160) & (p[..., 2] < 90)
    hx0, hy0 = (int(v) for v in D.d2p(x0, y0))
    hx1, hy1 = (int(v) for v in D.d2p(x1, y1))
    sub = eye[hy0:hy1, hx0:hx1]
    eye_c = np.median(D.pic[hy0:hy1, hx0:hx1, :3][sub], 0).astype(np.uint8)
    box[warm, :3] = mask_c
    for x, y in EYES:
        d[y, x, :3] = eye_c
        d[y, x, 3] = 255


def design():
    D = R.Design(HERO, PPU, ROWS)
    D.px = PIVOT_COL
    legs = {}
    for lg in (NEAR, FAR):
        # the knee at the greave's top: the greave and the boot one rigid shin (cut through the greave, the shin turned
        # apart from it broke the greave and twisted the boot - the user: 「贾克斯的脚有点变形」); the navy thigh only
        # just over it
        th, sh = R.leg_masks(D, lg["area"], lg["hip"], lg["knee"], keep_out=robe, over_knee=0.5, under_knee=1.0)
        legs[lg["name"] + "_thigh"], legs[lg["name"] + "_shin"] = th, sh
    D.cut_props({"arm": ARM, "lamp": LAMP, **legs}, fills=[TORSO_BEHIND_ARM], bare=set(legs), keep_out=robe)
    D.shaft("lamp", CAP, COLLAR, 1.2, rim=1.0)
    eyes(D)
    D.part("upper", D.rest(), take=False)
    return D


def make_rig(D):
    return R.Rig(D)


def driver(rig, joints):
    D = rig.D
    # his near arm turned by League's change from its idle (the picture is drawn after that idle); the lamp aimed at
    # League's lantern end (Weapon_Head) against the chest, its tip at most 2 squares into the ground
    return R.Driver(rig, joints, SPEC_HEIGHT, ROWS, legs=[NEAR, FAR],
                    arm=dict(name="arm", shoulder=SHOULDER, hand=GRIP, over_weapon=True, relative=True),
                    weapons=[dict(name="lamp", grip=GRIP, tip=LANTERN, league=("weapon", "weapon_head"), aim=True,
                                  relative=True, chest=CHEST, floor=2)], src=D.leg_src,
                    leg_max=25)


# the run's legs: league_nautilus's / league_braum's approved walk (the user: 「这走路步伐也不对啊」 - his shins swung at the
# knee by League's run kept the near foot planted in every frame, no stride). Both legs as drawn (the stub of trousers,
# the greave and the boot, never turned); in each frame one is lifted by losing its top rows under the robe and stepped
# forward, the legs take turns, the whole figure rises a little. The upper body, his arm and the lamp stay League's run.
# Per frame: the near leg's (columns forward, rows lifted), the far leg's, the figure's rise (league_nautilus's 1x
# steps x PPU 1.5)
RUN_LEAN = 3                                 # columns his upper body runs ahead of his hips
WALK = [((0, 0), (0, 3), 2), ((0, 0), (2, 5), 3), ((0, 0), (2, 2), 2), ((0, 0), (2, 0), 0),
        ((0, 3), (0, 0), 2), ((2, 5), (0, 0), 3), ((2, 2), (0, 0), 2), ((2, 0), (0, 0), 0)]


def leg_piece(D, lg):
    """A leg as drawn - its thigh and shin props at no angle, one padded array (compose takes it as a layer)."""
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


def walk(legs, step):
    """Driver `walk` for one WALK step: the far leg, then the near one, each lifted and moved."""
    near_step, far_step, _ = step

    def layers(hx, dy):
        out = []
        for lg, (dx, lift) in ((FAR, far_step), (NEAR, near_step)):
            a = legs[lg["name"]]
            if lift:
                a = a.copy()
                a[:np.nonzero(a[..., 3].any(1))[0].min() + lift] = 0
            out.append((a, dict(dx=hx + dx, dy=dy - lift)))
        return out
    return layers


def frames(rig, joints):
    drv = driver(rig, joints)
    legs = {lg["name"]: leg_piece(rig.D, lg) for lg in (NEAR, FAR)}
    ms = {t: [m for _, m in fr] for t, fr in R.sheet_of(HERO).items()}
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in ms:
            continue
        rows = R.fit_rows(rows, len(ms[tag]))
        if tag == "run":
            # the hips kept on the standing point and the upper body RUN_LEAN columns ahead of them in every frame
            # (League's pelvis rocks 4 columns to and fro over a run: the whole figure slid about); the steps one frame
            # on so each foot lands as League's does (the far one in frame 4, the near one in frame 0)
            fr = []
            for i, r in enumerate(rows):
                j = r["j"]
                pel = (j["pelvis"][0] - joints["design"]["pelvis"][0]) * drv.s * drv.lunge
                lean = ((j["chest"][0] - j["pelvis"][0]) -
                        (joints["design"]["chest"][0] - joints["design"]["pelvis"][0])) * drv.s * drv.lean
                st = WALK[(i - 1) % len(WALK)]
                fr.append(drv.frame(j, {"walk": walk(legs, st), "dy": -st[2], "dx": -pel,
                                        "lean": RUN_LEAN - int(round(max(-5, min(5, lean))))}))
        else:
            fr = [drv.frame(r["j"]) for r in rows]
        if tag == "hit":
            fr[0] = R.flash(fr[0])
        if tag == "dead":
            # the last frames lying: the figure as it falls (League's frame 4) a quarter turn onto the ground, his
            # head forward as League's falls
            lie = R.lie(rig, drv.frame(rows[3]["j"]), k=-1, dx=2)
            fr = fr[:4] + [lie] + [lie.copy() for _ in fr[5:]]
        out[tag] = fr
    for t in ms:
        if t not in out or len(out[t]) != len(ms[t]):
            sys.exit(f"{t}: {len(out.get(t, []))} frames for {len(ms[t])} in the sheet")
    return {t: list(zip(out[t], ms[t])) for t in ms}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare", help="Codex's jax-A.png")
    ap.add_argument("--joints", help="tools/lol/league_joints.py's jax_joints.json")
    ap.add_argument("--parts")
    ap.add_argument("--review")
    a = ap.parse_args()
    if a.prepare:
        prepare(a.prepare)
        return
    D = design()
    if a.parts:
        os.makedirs(a.parts, exist_ok=True)
        D.ruler(os.path.join(a.parts, f"{HERO}_parts.png"), z=12)
        return
    if not a.joints:
        sys.exit("--joints is needed")
    with open(a.joints, encoding="utf-8") as f:
        joints = json.load(f)
    rig = make_rig(D)
    acts = frames(rig, joints)
    if a.review:
        rig.review(acts, a.review)
        return
    rig.export(acts)


if __name__ == "__main__":
    main()
