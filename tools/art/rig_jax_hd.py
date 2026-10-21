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
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ppu_rig as R  # noqa: E402
import rigkit as K  # noqa: E402

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


# The run (2026-10-21, the user: 「贾克斯的走路也改一改 非常奇怪」). Until then his legs stepped league_nautilus's /
# league_braum's way (「这走路步伐也不对啊」 had turned down shins swung at the knee): each lifted a few rows under the
# robe and moved two columns at most, under an upper body that rocked with League's run and a lamp aimed each frame at
# League's lantern - pointing up-right in six frames, level in two, so it swung as he slid. Now:
# - the legs stride after League's feet (assets/source/jax/run_joints.json from tools/lol/pose_joints.py; League's R leg
#   is the near one), straight from the hip under the robe to the ankle, the way the pack's ranged runs stride
#   (league_zeri's scissor legs): League's knees bend the back foot up behind, and under a robe to the knees a bent leg
#   hid whole, one leg left showing; straight, both feet stay under the hem. Each foot as far ahead of its hip as
#   League's (RUN_SCALE squares a game px), lifted RUN_LIFT of League's height over the lower foot (at most RUN_LIFT_MAX
#   rows); the trousers down to RUN_KNEE_AT, the greave below in the design's own colours, one outline, his own boot on
#   the ankle; the far leg in the design's darker golds and a row higher (its sole on row 52, as drawn);
# - the lamp held steady as League's (level before him at the waist): his arm as drawn and the lamp turned RUN_WEAPON
#   degrees up about the fist in every frame (Driver keep);
# - the figure bobs with League's hips (rigkit.hip_bobs, 0-2 rows), his upper body RUN_LEAN columns ahead of his hips.
RUN_LEAN = 3                                 # columns his upper body runs ahead of his hips
RUN_JOINTS = os.path.join(R.ROOT, "assets", "source", HERO, "run_joints.json")
RUN_HIPS = {"near": (26.0, 34.0), "far": (42.0, 34.0)}        # under the robe
RUN_BOOT = {"near": (50, 53, 17, 28), "far": (49, 52, 39, 51)}    # rows, columns (inclusive): each boot in its leg
RUN_ANKLE = {"near": (21.5, 50.0), "far": (44.5, 49.5)}       # each boot's top middle
RUN_SCALE = 1.5                              # design squares a League game px
RUN_LIFT, RUN_LIFT_MAX = 0.5, 3
RUN_KNEE_AT = 0.55                           # the trousers end, the greave begins this far down the leg
RUN_HW = (2.4, 1.9)                          # greave half widths at the knee and the ankle
RUN_THW = 2.6                                # trousers half width
RUN_SHADES = {"near": [(-0.45, "E2AA29"), (0.05, "C6821A"), (0.5, "9F6213"), (9, "7B4E10")],
              "far": [(-0.45, "C6821A"), (0.05, "9F6213"), (0.5, "7B4E10"), (9, "5F3E12")]}
RUN_TROUSERS = {"near": [(-0.35, "5A4F59"), (9, "252639")], "far": [(9, "252639")]}
RUN_OUTLINE = (0, 0, 6, 255)
RUN_WEAPON, RUN_ARM = 20, 0                  # the lamp's turn (degrees up about the fist), the arm's


def leg_piece(D, lg):
    """A leg as drawn - its thigh and shin props at no angle, one padded array (compose takes it as a layer)."""
    th = D.turn(lg["name"] + "_thigh", 0, tuple(lg["hip"]), D.leg_src)
    sh = D.turn(lg["name"] + "_shin", 0, tuple(lg["knee"]), D.leg_src)
    out = sh.copy()
    m = th[..., 3] > 0
    out[m] = th[m]
    return out


def run_bone(can, off, p0, p1, hw0, hw1, shades):
    """A tapered segment p0 -> p1 (design squares) drawn into a padded layer (pad off), coloured across it by
    `shades` from its back to its front; -> its mask."""
    H, W = can.shape[:2]
    ys, xs = np.mgrid[0:H, 0:W]
    px, py = xs + 0.5 - off, ys + 0.5 - off
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0
    l2 = max(dx * dx + dy * dy, 1e-6)
    t = ((px - x0) * dx + (py - y0) * dy) / l2
    tc = np.clip(t, 0, 1)
    d = np.hypot(px - (x0 + tc * dx), py - (y0 + tc * dy))
    hw = hw0 + (hw1 - hw0) * tc
    m = (d <= hw) & (t >= -0.15) & (t <= 1.1)
    s = -((px - x0) * dy - (py - y0) * dx) / math.sqrt(l2) / np.maximum(hw, 1e-6)
    for up, col in reversed(shades):
        can[m & (s <= up)] = tuple(int(col[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
    return m


def run_leg(D, side, hip, ank):
    """One straight leg hip -> ankle (trousers, then the greave, one outline) with its own boot on the ankle."""
    lg = NEAR if side == "near" else FAR
    whole = leg_piece(D, lg)
    off = (whole.shape[0] - D.H) // 2
    y0, y1, x0, x1 = RUN_BOOT[side]
    boot = np.zeros_like(whole)
    boot[off + y0:off + y1 + 1, off + x0:off + x1 + 1] = whole[off + y0:off + y1 + 1, off + x0:off + x1 + 1]
    can = np.zeros_like(whole)
    knee = (hip[0] + (ank[0] - hip[0]) * RUN_KNEE_AT, hip[1] + (ank[1] - hip[1]) * RUN_KNEE_AT)
    tm = run_bone(can, off, hip, knee, RUN_THW, RUN_HW[0], RUN_TROUSERS[side])
    sm = run_bone(can, off, knee, ank, *RUN_HW, RUN_SHADES[side])
    ring = ndimage.binary_dilation(tm | sm, np.ones((3, 3), bool)) & ~(tm | sm)
    can[ring] = RUN_OUTLINE
    ax, ay = RUN_ANKLE[side]
    return R.put(can, K.shifted(boot, int(round(ank[0] - ax)), int(round(ank[1] - ay))))


def run_legs(D, j):
    """Driver `walk` for one League run frame: both legs, the far one first."""
    low = max(j["L_Foot"][1], j["R_Foot"][1])
    step = {}
    for side, s in (("near", "R"), ("far", "L")):
        ahead = (j[f"{s}_Foot"][0] - j[f"{s}_Hip"][0]) * RUN_SCALE
        lift = min(RUN_LIFT_MAX, max(0, int(round((low - j[f"{s}_Foot"][1]) * RUN_SCALE * RUN_LIFT))))
        step[side] = (ahead, lift)

    def layers(hx, dy):
        out = []
        for side in ("far", "near"):
            ahead, lift = step[side]
            hip = (RUN_HIPS[side][0] + hx, RUN_HIPS[side][1] + dy)
            out.append((run_leg(D, side, hip, (hip[0] + ahead, RUN_ANKLE[side][1] - lift)), {}))
        return out
    return layers


def frames(rig, joints):
    drv = driver(rig, joints)
    with open(R.lp(RUN_JOINTS), encoding="utf-8") as f:
        run_j = json.load(f)
    bobs = K.hip_bobs([fr["joints"]["Pelvis"][1] for fr in run_j], 2)
    ms = {t: [m for _, m in fr] for t, fr in R.sheet_of(HERO).items()}
    out = {}
    for tag, rows in joints["tags"].items():
        if tag not in ms:
            continue
        rows = R.fit_rows(rows, len(ms[tag]))
        if tag == "run":
            # the hips kept on the standing point and the upper body RUN_LEAN columns ahead of them in every frame
            # (League's pelvis rocks 4 columns to and fro over a run: the whole figure slid about)
            if len(rows) != len(run_j):
                sys.exit(f"run: {len(rows)} frames against {len(run_j)} of League's run joints")
            fr = []
            for i, r in enumerate(rows):
                j = r["j"]
                pel = (j["pelvis"][0] - joints["design"]["pelvis"][0]) * drv.s * drv.lunge
                lean = ((j["chest"][0] - j["pelvis"][0]) -
                        (joints["design"]["chest"][0] - joints["design"]["pelvis"][0])) * drv.s * drv.lean
                fr.append(drv.frame(j, {"walk": run_legs(rig.D, run_j[i]["joints"]), "dy": bobs[i], "dx": -pel,
                                        "lean": RUN_LEAN - int(round(max(-5, min(5, lean)))),
                                        "keep": True, "weapon": RUN_WEAPON, "arm": RUN_ARM}))
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
