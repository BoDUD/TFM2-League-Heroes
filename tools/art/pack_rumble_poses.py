#!/usr/bin/env python3
"""Rumble's pose pack for Codex (assets/source/rumble/POSE_PROMPTS.md): the whole-body poses his actions go through
(pack_yorick_poses.py's way, the user: 「动作帧用 Codex 骨架姿势包」).

    python tools/art/pack_rumble_poses.py [--out outputs/rumble_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square (B-1's own 12), soles on y SOLE_Y - the design hd/idle.png (step 1's
B-1 as drawn, 92 x 62) sits at squares (DX + shift, DY) on it.
The skeletons are set by hand after League's frames (tools/lol/pose_ref.py on the local client's Rumble.wad.client, the
3/4 camera facing right; 2026-10-25, the user: 「用英雄联盟本地客户端的动作帧重做兰博的姿势包」 - the cloud draft had none).
League's mech carries the mace in front on its far side and the flamethrower across its near side; ours (the approved
design) hangs the mace behind on the image left and pushes the cannon forward on the image right, so each pose copies
League's MOTION (how the body pitches, the legs stride, the mace rises and falls, where the cannon points) onto our sides.
THE MECH is one rigid BODY (the cockpit hull, the pilot in it and the two rocket pods on its back) turned about the
hull's bottom middle (`tilt`, + leans forward to the image right) and set down by `pelvis`; the pilot's head box rides on
it UPRIGHT (pasted, never turned). On it hang the MACE arm (image left: shoulder, elbow, the mechanical hand, the
spiked ball carried on past the hand along the forearm), the CANNON arm (image right: shoulder, elbow, then the
flamethrower cannon as one rigid tube at the design's length) and the two short legs (hip, knee, ankle; the red disc
foot kept flat under the ankle). Every bone at the design's OWN length (measured on hd/idle.png at 13x: REST), only its
direction set per pose (POSES), the lowest sole on the ground unless the pose lifts it.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the pilot's head, 8x: every pose wears it); 2_design.png (the design on the grid); per pose
<k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton (the head pasted) beside League's frame, and the design's own skeleton over the design.
Skeleton colours: tan box = the hull (cockpit), red-brown box = the rocket pods, grey box = the pilot's head; green = the
body's axis (the hull's bottom middle up to the pilot); RED = the NEAR leg (image left), BLUE = the FAR leg (image
right), the flat ellipses = the red disc feet; PURPLE = the MACE arm (image left) with the dark circle = the spiked
ball; ORANGE = the CANNON arm (image right) with the thick gold bar = the cannon (the ring = its muzzle).
"""
import argparse
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from design_rumble_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402
from pack_illaoi_poses import ang, along, turned, bend, canvas_grid as _grid, tile_sheet  # noqa: E402
import pack_illaoi_poses as IP  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "rumble")
PX, CANVAS, SOLE_Y = 12, 1254, 1188
GREY = (225, 225, 225)
GROUND = 62                        # the design's soles' bottom edge (rows)
DX, DY = 6, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 99)
COL = {"axis": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "mace_arm": (150, 60, 200),
       "cannon_arm": (255, 140, 0)}
HEAD = (0, 27, 33, 64)             # rows / columns of the pilot's head in hd/idle.png (mohawk, ears, goggles, chin)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 31 x 27 squares
FACE = (41, 60, 14, 26)            # the face (eyes, nose, grin): x0, x1, y0, y1 in design squares
PIVOT = (48.0, 48.0)               # the hull's bottom middle: the body turns about it
HULL = (30, 24, 68, 49)            # the hull box x0, y0, x1, y1 (design squares)
PODS = (15, 4, 40, 22)             # the rocket pods box
BALL_R = 9.5                       # the spiked ball's radius with its spikes
BALL_OFF = 9.5                     # hand -> ball centre, along the forearm
CANNON_L = 30.0                    # elbow -> muzzle
CANNON_W = 6.0
FOOT = {"near_leg": ((-4.0, 3.5), 16.0), "far_leg": ((2.0, 3.5), 17.0)}   # ankle -> foot centre, foot width
FOOT_H = 6.5                       # the disc foot's height (its sole 3 rows under the centre)

# the design's own skeleton, measured on hd/idle.png (92 x 62, square edges)
REST = {
    "head": (48.5, 13.5),
    "mace_arm": [(28.0, 26.0), (21.0, 33.0), (17.0, 41.0)],
    "cannon_arm": [(62.0, 31.0), (66.0, 37.0)],
    "cannon_dir": 58.0,
    "near_leg": [(39.0, 47.0), (36.0, 51.0), (35.0, 55.0)],
    "far_leg": [(56.0, 47.0), (59.0, 51.0), (60.0, 55.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: "pelvis" (where PIVOT goes),
# "tilt" (degrees, + forward), "rest_on": "all" (lying down: the lowest of everything on the ground), "lift" (rows the lowest sole is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the mace arm ("rest", two angles, or (hand target, side)), "cannon" (upper arm angle,
# cannon direction - ang(): 0 straight down, 90 to the image right, 180 up, -90 to the image left) and each leg
# ("rest", "body" - stiff and turned with the body - or (ankle target, side)).
POSES = {
    "a_wind": ("rumble_attack2@240",
               "抡锤起手：机械手臂把带刺铁球举过头顶（铁球在头的左上方、在头后面，不挡脸），机甲微微往后仰，喷火炮管往前下方端着，两脚分开站稳（普攻起手）",
               "WIND-UP - the MACE arm raising the spiked iron ball high OVER the head (just above and behind it, on the upper "
               "left, never over the face), the mech leaning back a little, the cannon held forward and down, the feet "
               "planted apart.",
               dict(pelvis=(48.0, 48.0), tilt=-6, lift=None, shift=0, mace_arm=(-160, -178), cannon=(30, 70),
                    near_leg=((34.0, 55.0), 1), far_leg=((61.0, 55.0), -1))),
    "a_smash": ("rumble_attack2@400",
                "砸下：机甲往前压、膝盖弯下，机械手臂往下猛砸、伸直，带刺铁球砸到地上（近侧脚前面），喷火炮管往上往后收（普攻砸中）",
                "SMASH - the mech pitching forward with bent knees, the MACE arm slammed down and straight so the spiked "
                "ball hits the ground by the near foot, the cannon pulled up and back.",
                dict(pelvis=(48.0, 50.0), tilt=14, lift=None, shift=-6, mace_arm=(25, 15), cannon=(95, 120),
                     near_leg=((33.0, 55.0), 1), far_leg=((63.0, 55.0), -1))),
    "q_aim": ("rumble_spell1_60fps@100",
              "端平喷火炮：两腿大大分开、膝盖弯下、机甲压低一格，喷火炮管端平朝正右方（准备喷火），铁球垂在左下（纵火盛宴起手）",
              "FLAMETHROWER UP - the feet set wide apart with bent knees, the mech one square lower, the CANNON held "
              "LEVEL pointing straight to the image right (about to spray fire), the ball hanging low on the left.",
              dict(pelvis=(48.0, 50.0), tilt=4, lift=None, shift=-6, mace_arm=(-25, -30), cannon=(70, 90),
                   near_leg=((32.0, 55.0), 1), far_leg=((64.0, 55.0), -1))),
    "q_spray": ("rumble_spell1_60fps@400",
                "喷火中：同上，身子再往前压一点，炮管稍微往下斜（火往前喷），铁球往后摆（纵火盛宴持续）",
                "SPRAYING - as above, leaning a little further forward, the cannon tipped slightly down (the fire "
                "pouring forward), the ball swung back.",
                dict(pelvis=(48.0, 50.0), tilt=9, lift=None, shift=-7, mace_arm=(-50, -40), cannon=(65, 80),
                     near_leg=((31.0, 55.0), 1), far_leg=((65.0, 55.0), -1))),
    "e_aim": ("rumble_spell3@160",
              "瞄准射鱼叉：机甲站直，喷火炮管抬起来，朝右方稍微往上指（射电子鱼叉），铁球垂在左边（电子鱼叉起手）",
              "HARPOON AIM - the mech upright, the CANNON raised pointing to the image right and a little up (to fire "
              "the electro-harpoon), the ball hanging on the left.",
              dict(pelvis=(48.0, 48.0), tilt=0, lift=None, shift=-4, mace_arm=(-20, -30), cannon=(85, 100),
                   near_leg=((34.0, 55.0), 1), far_leg=((61.0, 55.0), -1))),
    "e_recoil": ("rumble_spell3@320",
                 "鱼叉射出的后坐：机甲往后一仰，炮管被震得往上翘，近侧脚往后退半步，铁球往前甩（电子鱼叉射出）",
                 "HARPOON RECOIL - the mech kicked back, the cannon jolted up, the near foot sliding half a step back, "
                 "the ball swinging forward.",
                 dict(pelvis=(47.0, 48.0), tilt=-10, lift=None, shift=0, mace_arm=(40, 70), cannon=(105, 125),
                      near_leg=((31.0, 55.0), 1), far_leg=((59.0, 55.0), -1))),
    "r_crouch": ("rumble_spell4_60fps@200",
                 "蓄力：机甲蹲低、往前弓，背上的火箭舱翘起来朝天，喷火炮管往前下方指着地面，铁球垂在身边（恒温灼烧起手）",
                 "ROCKET WIND-UP - the mech crouching low and hunched forward so the rocket pods on its back point up at "
                 "the sky, the CANNON pointing down at the ground ahead, the ball hanging by its side.",
                 dict(pelvis=(48.0, 51.0), tilt=14, lift=None, shift=-4, mace_arm=(-35, -25), cannon=(35, 64),
                      near_leg=((33.0, 55.0), 1), far_leg=((62.0, 55.0), -1))),
    "r_launch": ("rumble_spell4_60fps@400",
                 "发射火箭：火箭射出去的后坐，机甲往上一顶、比蓄力高一格，火箭舱仍然朝天，炮管仍然指着地面，铁球往外甩，脚还踩在地上（恒温灼烧发射）",
                 "ROCKET LAUNCH - the kick of the rockets going off: the mech jolted up one square from the crouch, the "
                 "rocket pods still pointing at the sky, the cannon still pointing at the ground ahead, the ball swung "
                 "out, the feet still on the ground.",
                 dict(pelvis=(48.0, 49.0), tilt=8, lift=None, shift=-2, mace_arm=(-55, -50), cannon=(35, 60),
                      near_leg=((34.0, 55.0), 1), far_leg=((61.0, 55.0), -1))),
    "run1": ("rumble_run_60fps@0",
             "跑 1（远侧腿往前迈一大步着地，近侧腿往后蹬）：机甲往前倾，炮管朝前端着，铁球往后摆",
             "RUN 1 - a long stomping stride: the FAR leg reaching forward with its foot landing, the NEAR leg pushing "
             "back, the mech leaning forward, the cannon carried forward, the ball swinging back.",
             dict(pelvis=(48.0, 48.0), tilt=8, lift=None, shift=-4, mace_arm=(-40, -30), cannon=(60, 75),
                  near_leg=((30.0, 55.0), 1), far_leg=((66.0, 55.0), -1))),
    "run2": ("rumble_run_60fps@240",
             "跑 2（近侧腿在身下撑地，远侧腿屈膝抬起往前）：机甲高一格，铁球垂着，炮管朝前",
             "RUN 2 - the near leg under the body carrying it, the FAR knee lifted forward, the mech one square "
             "higher, the ball hanging, the cannon forward.",
             dict(pelvis=(48.0, 47.0), tilt=5, lift=None, shift=-4, mace_arm=(-20, -35), cannon=(55, 70),
                  near_leg=((40.0, 55.0), 1), far_leg=((63.0, 51.0), -1))),
    "run3": ("rumble_run_60fps@480",
             "跑 3（近侧腿往前迈一大步着地，远侧腿往后蹬）：机甲往前倾，铁球往前摆，炮管稍微往后",
             "RUN 3 - a long stomping stride: the NEAR leg reaching forward with its foot landing, the FAR leg "
             "pushing back, the mech leaning forward, the ball swinging forward, the cannon a little back.",
             dict(pelvis=(48.0, 48.0), tilt=8, lift=None, shift=-4, mace_arm=(15, 25), cannon=(45, 60),
                  near_leg=((44.0, 55.0), -1), far_leg=((49.0, 55.0), 1))),
    "run4": ("rumble_run_60fps@720",
             "跑 4（远侧腿在身下撑地，近侧腿屈膝抬起往前）：机甲高一格，铁球垂着",
             "RUN 4 - the far leg under the body carrying it, the NEAR knee lifted forward, the mech one square "
             "higher, the ball hanging.",
             dict(pelvis=(48.0, 47.0), tilt=5, lift=None, shift=-4, mace_arm=(-25, -35), cannon=(55, 70),
                  near_leg=((42.0, 51.0), -1), far_leg=((56.0, 55.0), -1))),
    "d_drop": ("rumble_death@2000",
               "倒下：机甲被打得往左后方仰，两腿膝盖发软，炮管朝右上方翘起，铁球甩在左边（死亡第一下）",
               "COLLAPSE - the mech knocked back toward the image left, both knees giving way, the cannon tipped up to "
               "the right, the ball flung out on the left.",
               dict(pelvis=(47.0, 51.0), tilt=-20, lift=None, shift=10, mace_arm=(-95, -115), cannon=(100, 130),
                    near_leg=((32.0, 55.0), 1), far_leg=((60.0, 55.0), -1))),
    "d_down": ("rumble_death@3500",
               "翻倒：机甲往左后方翻倒、仰面躺在地上（驾驶舱底朝右下、开口朝左上），两条短腿僵直地翘离地面朝右，机械手臂瘫在左边地上、铁球落在地上，炮管斜着朝右上方，驾驶员的头还在驾驶舱上面（死亡倒地）",
               "TOPPLED - the mech tipped over backward onto its back on the ground (the hull's bottom toward the lower "
               "right, its open top toward the upper left), both short legs stiff and lifted off the ground toward the "
               "right, the mace arm flopped out on the ground on the left with the ball lying there, the cannon "
               "slanting up to the right, the pilot's head still on top of the cockpit.",
               dict(pelvis=(48.0, 48.0), tilt=-80, lift=None, rest_on="all", shift=24, mace_arm=(-95, -85),
                    cannon=(150, 120), near_leg="body", far_leg="body")),
}


def lengths(pts):
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def build(spec):
    """A skeleton from a pose spec: the body (hull, pods, head, the shoulders and the hips) turned about PIVOT by -tilt
    and set at `pelvis`; the limbs at the design's own lengths; the feet flat; the lowest sole on the ground (or
    `lift` rows over it)."""
    t = -spec["tilt"]
    pel = spec["pelvis"]
    on_body = lambda q: (lambda o: (pel[0] + o[0], pel[1] + o[1]))(turned((q[0] - PIVOT[0], q[1] - PIVOT[1]), t))
    sk = {"axis": [on_body(PIVOT), on_body((PIVOT[0], 20.0))], "head": on_body(REST["head"]),
          "hull": [on_body(p) for p in ((HULL[0], HULL[1]), (HULL[2], HULL[1]), (HULL[2], HULL[3]), (HULL[0], HULL[3]))],
          "pods": [on_body(p) for p in ((PODS[0], PODS[1]), (PODS[2], PODS[1]), (PODS[2], PODS[3]), (PODS[0], PODS[3]))]}
    # the mace arm and its ball
    ms = on_body(REST["mace_arm"][0])
    l1, l2 = lengths(REST["mace_arm"])
    sp = spec["mace_arm"]
    if sp == "rest":
        el, ha = on_body(REST["mace_arm"][1]), on_body(REST["mace_arm"][2])
    elif isinstance(sp[0], tuple):
        el, ha = bend(ms, sp[0], l1, l2, sp[1])
    else:
        el = along(ms, sp[0], l1)
        ha = along(el, sp[1], l2)
    sk["mace_arm"] = [ms, el, ha]
    sk["ball"] = along(ha, ang(el, ha), BALL_OFF)
    # the cannon arm and the cannon
    cs = on_body(REST["cannon_arm"][0])
    cl = lengths(REST["cannon_arm"])[0]
    up_a, c_dir = spec["cannon"]
    ce = along(cs, up_a, cl)
    sk["cannon_arm"] = [cs, ce]
    sk["cannon"] = [ce, along(ce, c_dir, CANNON_L)]
    # the legs and the flat feet
    for name in ("near_leg", "far_leg"):
        hip = on_body(REST[name][0])
        a1, a2 = lengths(REST[name])
        lg = spec[name]
        if lg == "body":                # stiff, turned with the body (the toppled mech's legs in the air)
            kn, an = on_body(REST[name][1]), on_body(REST[name][2])
        elif lg == "rest":
            kn = (hip[0] + REST[name][1][0] - REST[name][0][0], hip[1] + REST[name][1][1] - REST[name][0][1])
            an = (hip[0] + REST[name][2][0] - REST[name][0][0], hip[1] + REST[name][2][1] - REST[name][0][1])
        else:
            kn, an = bend(hip, lg[0], a1, a2, lg[1])
        (fx, fy), _ = FOOT[name]
        sk[name] = [hip, kn, an]
        sk[name + "_foot"] = (an[0] + fx, an[1] + fy)
    low = max(sk[n + "_foot"][1] + FOOT_H / 2 for n in ("near_leg", "far_leg"))
    if spec.get("rest_on") == "all":   # lying down: whatever is lowest (the hull, the ball, the cannon) is on the ground
        low = max([low, sk["ball"][1] + BALL_R, sk["cannon"][1][1] + CANNON_W / 2] + [y for _, y in sk["hull"]])
    dy = GROUND - (spec["lift"] or 0) - low
    out = {}
    for k, v in sk.items():
        out[k] = (v[0], v[1] + dy) if isinstance(v, tuple) else [(x, y + dy) for x, y in v]
    return out


def to_canvas(sk, shift=0):
    return {k: (v[0] + DX + shift, v[1] + DY) if isinstance(v, tuple) else [(x + DX + shift, y + DY) for x, y in v]
            for k, v in sk.items()}


def c(p):
    return (p[0] * PX, p[1] * PX)


def skeleton(can, s, label, alpha=255):
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    dr.polygon([c(p) for p in s["pods"]], fill=(170, 60, 50, 60), outline=(150, 40, 30, alpha))
    dr.polygon([c(p) for p in s["hull"]], fill=(200, 160, 80, 70), outline=(150, 110, 40, alpha))
    hx, hy = s["head"]
    dr.rectangle([(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX],
                 fill=(150, 150, 150, 70 if alpha < 255 else 110), outline=(90, 90, 90, alpha), width=3)
    dr.line([c(p) for p in s["axis"]], fill=COL["axis"] + (alpha,), width=5)
    for name in ("far_leg", "near_leg"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for p in pts:
            dr.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=COL[name] + (alpha,))
        (fx, fy), w = s[name + "_foot"], FOOT[name][1]
        dr.ellipse([(fx - w / 2) * PX, (fy - FOOT_H / 2) * PX, (fx + w / 2) * PX, (fy + FOOT_H / 2) * PX],
                   outline=COL[name] + (alpha,), width=4)
    # the cannon: a thick gold bar from the elbow, a ring at the muzzle
    e, m = s["cannon"]
    dr.line([c(e), c(m)], fill=(210, 170, 40, 150 if alpha == 255 else 110), width=round(CANNON_W * PX))
    dr.ellipse([m[0] * PX - CANNON_W * PX / 2, m[1] * PX - CANNON_W * PX / 2, m[0] * PX + CANNON_W * PX / 2,
                m[1] * PX + CANNON_W * PX / 2], outline=(120, 80, 10, alpha), width=4)
    for name in ("cannon_arm", "mace_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if k == len(pts) - 1 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    bx, by = s["ball"]
    dr.ellipse([(bx - BALL_R) * PX, (by - BALL_R) * PX, (bx + BALL_R) * PX, (by + BALL_R) * PX],
               fill=(40, 40, 50, 90), outline=(20, 20, 30, alpha), width=4)
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def canvas_grid():
    IP.PX, IP.CANVAS, IP.SOLE_Y = PX, CANVAS, SOLE_Y
    return _grid()


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def rest_spec():
    return dict(pelvis=PIVOT, tilt=0, lift=None, mace_arm="rest", cannon=(ang(*REST["cannon_arm"]), REST["cannon_dir"]),
                near_leg="rest", far_leg="rest")


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def lol_frame(lol, frame, work):
    """League's frame, Rumble at the 3/4 camera facing right, cropped round him (and anything he fires)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Rumble",
           "--fit-all", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.4",
           "--ground", "0.8", "--width", "2.0", "--yaw", "35", "--name", "f", "--out", work, "--frame", frame, "--mirror"]
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def problems(name, s):
    """Every bone, the ball, the cannon and the head box on the canvas; nothing over the pilot's face."""
    out = []
    pts = [p for k in ("mace_arm", "cannon_arm", "cannon", "near_leg", "far_leg") for p in s[k]] + [s["ball"]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    bx, by = s["ball"]
    if bx - BALL_R < 0 or bx + BALL_R > CANVAS / PX or by + BALL_R > SOLE_Y / PX + 0.6:
        out.append("ball off the canvas / below the ground")
    mx, my = s["cannon"][1]
    if mx - CANNON_W / 2 < 0 or mx + CANNON_W / 2 > CANVAS / PX or my + CANNON_W / 2 > SOLE_Y / PX + 0.6:
        out.append("muzzle off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    near = lambda x, y, r=0.0: fx0 - r <= x <= fx1 + r and fy0 - r <= y <= fy1 + r
    if near(bx, by, BALL_R * 0.8):
        out.append("ball over the face")
    (x0, y0), (x1, y1) = s["cannon"]
    if any(near(x0 + (x1 - x0) * k / 30, y0 + (y1 - y0) * k / 30, CANNON_W / 2) for k in range(31)):
        out.append("cannon over the face")
    if any(near(x, y) for x, y in s["mace_arm"][1:] + s["cannon_arm"][1:]):
        out.append("arm over the face")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "rumble_pose_pack"))
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(rest_spec()))
    bad = 0
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
            bad += 1
    r0, r1, c0, c1 = HEAD
    head = idle[r0:r1, c0:c1]
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        base = canvas_grid()
        base.alpha_composite(on_grid(idle, DX, DY))
        skeleton(base, rest, "the design's own skeleton (REST)", 200)
        base.convert("RGB").save(os.path.join(a.check, "rest_check.png"))
        names = a.only.split(",") if a.only else list(poses)
        cache = os.path.join(a.check, "_league")
        os.makedirs(cache, exist_ok=True)
        tiles = []
        for name in names:
            s, frame, zh, en = poses[name]
            can = canvas_grid()
            hx, hy = s["head"]
            can.alpha_composite(Image.fromarray(up(head, PX)), (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
            skeleton(can, s, name)
            fpath = os.path.join(cache, name + ".png")
            if not os.path.isfile(fpath):
                lol_frame(a.lol, frame, os.path.join(a.check, "_work")).save(fpath)
            lf = Image.open(fpath).convert("RGB")
            sk = can.convert("RGB").resize((CANVAS * 2 // 5, CANVAS * 2 // 5))
            lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
            t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(lf, (sk.width, 0))
            tiles.append(t)
        tile_sheet(tiles, os.path.join(a.check, "poses_check.png"))
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        print("checked", len(poses), "poses,", bad, "problems")
        return
    if bad:
        sys.exit("fix the problems first")
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line and box stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    big(head).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
