#!/usr/bin/env python3
"""Heimerdinger's pose packs for Codex (assets/source/heimerdinger/POSE_PROMPTS.md, CRANE_PROMPTS.md): what his actions
need that the approved 3/4 design cannot give by moving its own squares (the user, 2026-10-21, on the first rig:
「身体背后的机械的动作帧呢？没有 还有头和身体不协调 走路也怪」「你觉得这个动作帧和英雄联盟一样吗 我觉得差的很大」「做不出来就让
codex帮忙」):
  * pack A, BODY poses - the whole body in League's run (a bouncing skip: knees up, both tools swinging), the attack (a
    kick and a jab of the wrench), the idle's tinkering (the multitool brought up to his chest) and the death (he
    recoils as the backpack bursts open, tips over backwards, lies on his back on the backpack's engine);
  * pack B, PROPS - the backpack crane his Q, E and W lift out from under his mane (hidden in the idle) in every
    position League's clips put it, its rocket held in the red claw or gone, and R's UPGRADE!!! gear (the drum, two springy
    antennas with red balls, the red-rimmed ring round the top of his head).

    python tools/lol/league_joints.py assets/source/heimerdinger/poses.json --out C:/t/hd_work/joints
    (and the same spec with "weapon_joint": "L_Weapon" / "R_Weapon" into C:/t/hd_work/joints_l / joints_r: each
    tool's two ends)
    python tools/art/pack_heimerdinger_poses.py --joints C:/t/hd_work/joints/heimerdinger_joints.json --check DIR
    python tools/art/pack_heimerdinger_poses.py --joints C:/t/hd_work/joints/heimerdinger_joints.json [--out DIR]

Skeleton lines alone did not hold (his legs are short boots, League's joints laid on them bent the wrong way), so every
BODY pose comes as a ROUGH: the design's own pieces (the head with the mane, the coat, each glove with its tool, each
boot) moved to League's frame - the head and the coat by League's neck and pelvis, each hand by League's hand (its tool
turned by League's turn of it, rough), each boot by League's foot, all at 1.5 squares a game pixel from the design's own
rest place, the run's and the death's vertical moves scaled (BOUNCE), sleeves and legs drawn as plain bands - its size
and place right, its joins broken: Codex redraws it clean (the step-1 way: 2_target). The crane (no design yet) is
League's own: its joints at 1.5 squares a game pixel from the pivot (the design and League's model are both 36 game px
tall), drawn as a rough olive arm with a red claw and the rocket where it is held: Codex draws the crane alone on a
transparent picture (the design shown in grey only to place it); it goes behind him in the frames.
Writes <out>_body/ and <out>_props/ (and their zips): the prompts; 0_design.png (the design on the grid), 1_head.png
(the head, 8x); per body pose b<k>_<name>_rough.png + b<k>_<name>_league.png; per prop p<k>_<name>_guide.png +
p<k>_<name>_league.png. League's frames are Riot's, kept local, never committed.
"""
import argparse
import json
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
from design_heimerdinger_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "heimerdinger")
PX, CANVAS, SOLE_Y = 12, 1254, 1200
GREY = (225, 225, 225)
GROUND = 54                         # the design's soles' bottom edge (rows)
PIVOT = 25.5                        # the design's standing point (columns)
DX, DY = 40, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 100)
S = 1.5                             # design squares a game pixel (PPU 1.5, both 36 game px tall)

# the design's pieces (hd/idle.png, 50 x 54; boxes x0, y0, x1, y1, ends exclusive)
TOOL = [(7, 34, 16, 45), (13, 45, 16, 47)]          # the multitool and the near glove holding it
WRENCH = [(38, 33, 50, 46), (34, 41, 38, 45)]       # the wrench and the far glove
NBOOT = (16, 49, 22, 54)
FBOOT = (24, 49, 35, 54)
HEAD_ROWS = 38                                      # the head with the mane, the goggles and the moustache: rows above
# rest points (square edges): wrists (where each glove holds its tool), shoulders, hips, ankles
REST = {"r_hand": (14.0, 45.0), "l_hand": (35.5, 43.0), "r_shoulder": (18.5, 37.5), "l_shoulder": (31.0, 37.5),
        "r_hip": (20.0, 45.5), "l_hip": (28.5, 45.5), "r_foot": (19.0, 51.0), "l_foot": (28.0, 50.5),
        "pelvis": (25.0, 46.0), "neck": (26.0, 37.0)}
ARM_REACH, LEG_REACH = 8.5, 6.0
SLEEVE, SLEEVE_DARK, TROUSER, INK = (52, 74, 72), (34, 46, 46), (40, 36, 52), (10, 6, 14)
CRANE_C, CRANE_D, CLAW, ROCKET, ROCKET_R = (120, 128, 70), (78, 84, 44), (200, 40, 30), (236, 206, 110), (205, 50, 40)
RING, RING_R = (48, 54, 50), (205, 50, 40)
CRANE_K = 1.3       # the crane (and R's gear) scaled up about its base: the design's head is bigger than League's

# BODY poses: name -> (tag, League ms, vertical bounce scale, the pose in words for the prompt)
BODY = {
    "run1": ("run", 0, 0.5, "跑步 1：腾空，一侧膝盖抬到身前，两只手往两边甩开"),
    "run2": ("run", 100, 0.5, "跑步 2：落地，身子压低，前脚着地、后脚在身后"),
    "run3": ("run", 200, 0.5, "跑步 3：蹬地往上跳，另一侧膝盖往前提"),
    "run4": ("run", 300, 0.5, "跑步 4：腾空最高点，扳手往前指，多功能工具甩到身后下方"),
    "run5": ("run", 400, 0.5, "跑步 5：往下落，前脚往前伸准备着地"),
    "run6": ("run", 500, 0.5, "跑步 6：另一只脚落地，身子压低"),
    "run7": ("run", 600, 0.5, "跑步 7：蹬地往上跳，膝盖往前提"),
    "run8": ("run", 700, 0.5, "跑步 8：腾空，两手张开"),
    "attack1": ("attack", 60, 1.0, "普攻 1：蓄力，远侧腿往前抬起，扳手举到肩膀高，多功能工具往后下方拉"),
    "attack2": ("attack", 180, 1.0, "普攻 2：远侧脚往前一跨踩地，身子往前，扳手往前一戳（放电）"),
    "attack3": ("attack", 260, 0.6, "普攻 3：顺势往前探身压低，扳手指着前方，近侧腿往后伸"),
    "tinker": ("idle", 667, 1.0, "待机 摆弄工具：多功能工具拿到胸前（在胡子下面，不挡脸），扳手往上抬一点"),
    "death1": ("dead", 300, 1.0, "死亡 1：中招一缩，头往前低，两手往两边张开（背包炸开，机械臂另画）"),
    "death2": ("dead", 600, 0.7, "死亡 2：往后仰倒（整个人往后倒下约 45 度），脚离地，两手往上甩"),
    "death3": ("dead", 1100, 0.7, "死亡 3：仰面躺在地上（头朝画面左边，靴子朝右上翘起），背后压着背包的大圆引擎"),
}
TILT = {"death2": 40, "death3": 90}     # the rough turned back (counter-clockwise) about the soles, degrees: he falls


def load_design():
    return np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA")).copy()


def mask(d, boxes):
    m = np.zeros(d.shape[:2], bool)
    for x0, y0, x1, y1 in boxes:
        m[y0:y1, x0:x1] = True
    return m & (d[..., 3] > 0)


def pieces(d):
    tool, wrench = mask(d, TOOL), mask(d, WRENCH)
    nboot, fboot = mask(d, [NBOOT]), mask(d, [FBOOT])
    op = d[..., 3] > 0
    head = op.copy()
    head[HEAD_ROWS:] = False
    head &= ~tool & ~wrench
    torso = op & ~head & ~tool & ~wrench & ~nboot & ~fboot
    lay = lambda m: np.where(m[..., None], d, 0).astype(np.uint8)
    return {"head": lay(head), "torso": lay(torso), "tool": lay(tool), "wrench": lay(wrench), "nboot": lay(nboot),
            "fboot": lay(fboot)}


def xy(j, k):
    x, y, _ = j[k]
    return (PIVOT + x * S, GROUND + y * S)


def moved(j, j0, k, bounce):
    a, b = xy(j, k), xy(j0, k)
    return (b[0] - a[0]) * -1, (a[1] - b[1]) * bounce


def ang(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def paste(can, layer, dx, dy, about=None, deg=0.0):
    """A design-sized layer onto the canvas (design squares; the design's (0, 0) at DX, DY), moved by (dx, dy) and
    turned deg about `about` (rough: nearest neighbour)."""
    img = Image.fromarray(layer)
    if deg and about is not None:
        img = img.rotate(-deg, resample=Image.NEAREST, center=about)
    can.alpha_composite(img, (int(round(DX + dx)), int(round(DY + dy))))


def band(can_d, a, b, width, col):
    """A plain band of squares from a to b (design squares, canvas-grid image of one pixel a square)."""
    d = ImageDraw.Draw(can_d)
    pa, pb = (DX + a[0], DY + a[1]), (DX + b[0], DY + b[1])
    d.line([pa, pb], fill=col + (255,), width=width)


def reach(root, p, r):
    v = (p[0] - root[0], p[1] - root[1])
    n = math.hypot(*v)
    return p if n <= r else (root[0] + v[0] * r / n, root[1] + v[1] * r / n)


def similar(a0, b0):
    """The 2-D similarity (turn + scale) taking League's rest offset a0 onto the design's rest offset b0."""
    za, zb = complex(*a0), complex(*b0)
    return zb / za if abs(za) > 1e-6 else 1


def apply(z, v):
    w = z * complex(*v)
    return (w.real, w.imag)


def place(j, j0, bounce):
    """Where League's frame puts the design's neck and pelvis (design squares, standing = REST), the hands and the feet:
    rough_body's arithmetic. -> neck, pelvis, hands {side: (shoulder, hand)}, feet {side: (hip, ankle)}."""
    off = lambda jj, a, b: (jj[b][0] - jj[a][0], jj[b][1] - jj[a][1])      # game px, y down (the export's)
    flip = lambda v: (v[0] * S, v[1] * S)                                # -> design squares
    dp = ((j["pelvis"][0] - j0["pelvis"][0]) * S, (j["pelvis"][1] - j0["pelvis"][1]) * S * bounce)
    pel = (REST["pelvis"][0] + dp[0], REST["pelvis"][1] + dp[1])
    z = similar(flip(off(j0, "pelvis", "neck")), (REST["neck"][0] - REST["pelvis"][0], REST["neck"][1] - REST["pelvis"][1]))
    v = apply(z, flip(off(j, "pelvis", "neck")))
    neck = (pel[0] + v[0], pel[1] + v[1])
    dn = (neck[0] - REST["neck"][0], neck[1] - REST["neck"][1])
    hands, feet = {}, {}
    for side in ("r", "l"):
        sh = (REST[f"{side}_shoulder"][0] + dn[0], REST[f"{side}_shoulder"][1] + dn[1])
        z = similar(flip(off(j0, "neck", f"{side}_hand")), (REST[f"{side}_hand"][0] - REST["neck"][0],
                                                              REST[f"{side}_hand"][1] - REST["neck"][1]))
        v = apply(z, flip(off(j, "neck", f"{side}_hand")))
        hands[side] = (sh, reach(sh, (neck[0] + v[0], neck[1] + v[1]), ARM_REACH))
        hip = (REST[f"{side}_hip"][0] + pel[0] - REST["pelvis"][0], REST[f"{side}_hip"][1] + pel[1] - REST["pelvis"][1])
        z = similar(flip(off(j0, "pelvis", f"{side}_foot")), (REST[f"{side}_foot"][0] - REST["pelvis"][0],
                                                               REST[f"{side}_foot"][1] - REST["pelvis"][1]))
        v = apply(z, flip(off(j, "pelvis", f"{side}_foot")))
        feet[side] = (hip, reach(hip, (pel[0] + v[0], pel[1] + v[1]), LEG_REACH))
    # standing frames stand on the ground: the lowest boot's sole on it; nothing sinks into it
    foot = max(j[k][1] for k in ("l_foot", "r_foot", "l_toe", "r_toe"))      # the lowest foot (y down)
    foot0 = max(j0[k][1] for k in ("l_foot", "r_foot", "l_toe", "r_toe"))
    low = max(feet["r"][1][1] + 3.0, feet["l"][1][1] + 3.5)
    shift = (GROUND - low) if (foot >= foot0 - 1.0 or low > GROUND) else 0.0
    sh_ = lambda p: (p[0], p[1] + shift)
    return (sh_(neck), sh_(pel), {k: (sh_(a), sh_(b)) for k, (a, b) in hands.items()},
            {k: (sh_(a), sh_(b)) for k, (a, b) in feet.items()})


def rough_body(P, j, j0, bounce):
    """One BODY rough at one pixel a square on the canvas grid ((W, H) = CANVAS / PX). League's pose re-proportioned to
    the design: the pelvis moved by League's (the vertical x bounce), the neck from the pelvis, each hand from the neck
    and each foot from the pelvis by League's offsets, every limb through the similarity that lays League's rest offset
    on the design's (so League's rest gives the design back); each tool turned by League's turn of it."""
    n = CANVAS // PX
    can = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    off = lambda jj, a, b: (jj[b][0] - jj[a][0], jj[b][1] - jj[a][1])      # game px, y down (the export's)
    flip = lambda v: (v[0] * S, v[1] * S)                                # -> design squares
    dp = ((j["pelvis"][0] - j0["pelvis"][0]) * S, (j["pelvis"][1] - j0["pelvis"][1]) * S * bounce)
    pel = (REST["pelvis"][0] + dp[0], REST["pelvis"][1] + dp[1])
    z = similar(flip(off(j0, "pelvis", "neck")), (REST["neck"][0] - REST["pelvis"][0], REST["neck"][1] - REST["pelvis"][1]))
    v = apply(z, flip(off(j, "pelvis", "neck")))
    neck = (pel[0] + v[0], pel[1] + v[1])
    dn = (neck[0] - REST["neck"][0], neck[1] - REST["neck"][1])
    hands, feet = {}, {}
    for side in ("r", "l"):
        sh = (REST[f"{side}_shoulder"][0] + dn[0], REST[f"{side}_shoulder"][1] + dn[1])
        z = similar(flip(off(j0, "neck", f"{side}_hand")), (REST[f"{side}_hand"][0] - REST["neck"][0],
                                                              REST[f"{side}_hand"][1] - REST["neck"][1]))
        v = apply(z, flip(off(j, "neck", f"{side}_hand")))
        hands[side] = (sh, reach(sh, (neck[0] + v[0], neck[1] + v[1]), ARM_REACH))
        hip = (REST[f"{side}_hip"][0] + pel[0] - REST["pelvis"][0], REST[f"{side}_hip"][1] + pel[1] - REST["pelvis"][1])
        z = similar(flip(off(j0, "pelvis", f"{side}_foot")), (REST[f"{side}_foot"][0] - REST["pelvis"][0],
                                                               REST[f"{side}_foot"][1] - REST["pelvis"][1]))
        v = apply(z, flip(off(j, "pelvis", f"{side}_foot")))
        feet[side] = (hip, reach(hip, (pel[0] + v[0], pel[1] + v[1]), LEG_REACH))
    # standing frames stand on the ground: the lowest boot's sole on it; nothing sinks into it
    foot = max(j[k][1] for k in ("l_foot", "r_foot", "l_toe", "r_toe"))      # the lowest foot (y down)
    foot0 = max(j0[k][1] for k in ("l_foot", "r_foot", "l_toe", "r_toe"))
    low = max(feet["r"][1][1] + 3.0, feet["l"][1][1] + 3.5)
    shift = (GROUND - low) if (foot >= foot0 - 1.0 or low > GROUND) else 0.0
    sh_ = lambda p: (p[0], p[1] + shift)
    neck, pel = sh_(neck), sh_(pel)
    dn = (neck[0] - REST["neck"][0], neck[1] - REST["neck"][1])
    dpl = (pel[0] - REST["pelvis"][0], pel[1] - REST["pelvis"][1])
    hands = {k: (sh_(a), sh_(b)) for k, (a, b) in hands.items()}
    feet = {k: (sh_(a), sh_(b)) for k, (a, b) in feet.items()}
    # each tool turned by League's turn of the tool itself (its two ends, the exports with weapon_joint L / R_Weapon)
    tturn = lambda side: ang(xy(j, f"{side}_tb"), xy(j, f"{side}_ta")) - ang(xy(j0, f"{side}_tb"), xy(j0, f"{side}_ta"))
    # back to front: far leg + boot, far sleeve + wrench, torso, head, near leg + boot, near sleeve + multitool
    hip, ank = feet["l"]
    band(can, hip, ank, 3, TROUSER)
    paste(can, P["fboot"], ank[0] - REST["l_foot"][0], ank[1] - REST["l_foot"][1])
    sh, hd = hands["l"]
    band(can, sh, hd, 4, SLEEVE_DARK)
    paste(can, P["wrench"], hd[0] - REST["l_hand"][0], hd[1] - REST["l_hand"][1], REST["l_hand"], tturn("l"))
    paste(can, P["torso"], (dn[0] + dpl[0]) / 2, (dn[1] + dpl[1]) / 2)
    paste(can, P["head"], dn[0], dn[1])
    hip, ank = feet["r"]
    band(can, hip, ank, 3, TROUSER)
    paste(can, P["nboot"], ank[0] - REST["r_foot"][0], ank[1] - REST["r_foot"][1])
    sh, hd = hands["r"]
    band(can, sh, hd, 4, SLEEVE)
    paste(can, P["tool"], hd[0] - REST["r_hand"][0], hd[1] - REST["r_hand"][1], REST["r_hand"], tturn("r"))
    return can


def tilt(rough, deg):
    """The rough turned deg counter-clockwise about the standing point (he falls back), then set down so its lowest
    square lies on the ground; lying (90), the backpack's engine drawn under his back."""
    img = rough.rotate(deg, resample=Image.NEAREST, center=(DX + PIVOT, DY + GROUND))
    ys = np.nonzero(np.asarray(img)[..., 3] > 0)[0]
    lie = deg >= 80
    up_ = 12 if lie else 0                         # lying, he rests on the engine: his back 12 squares up
    out = Image.new("RGBA", rough.size, (0, 0, 0, 0))
    if lie:   # the engine (an olive drum with a red rim) under his back, behind him
        d = ImageDraw.Draw(out)
        cx, cy = DX + PIVOT - 4, DY + GROUND - 7
        d.ellipse([cx - 9, cy - 7, cx + 9, cy + 7], fill=CRANE_C + (255,), outline=INK + (255,), width=1)
        d.ellipse([cx - 5, cy - 4, cx + 5, cy + 4], outline=RING_R + (255,), width=2)
    out.alpha_composite(img, (6 if lie else -4, DY + GROUND - up_ - (ys.max() + 1)))
    return out


def rough_crane(j, held):
    """The crane along League's joints at one pixel a square: the base and the long boom, the elbow, the short arm, the
    wrist, the red claw, the rocket (held) from the claw along League's rocket."""
    n = CANVAS // PX
    can = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(can)
    raw = [xy(j, k) for k in ("crane0", "crane1", "crane2", "crane3", "payload")]
    base = raw[0]
    big = [(base[0] + (p[0] - base[0]) * CRANE_K, base[1] + (p[1] - base[1]) * CRANE_K) for p in raw]
    pts = [(DX + p[0], DY + p[1]) for p in big[:4]]
    for (a, b), w in zip(zip(pts, pts[1:]), (6, 5, 4)):
        d.line([a, b], fill=INK + (255,), width=w + 2)
    for (a, b), w in zip(zip(pts, pts[1:]), (6, 5, 4)):
        d.line([a, b], fill=CRANE_C + (255,), width=w)
    for p, r in zip(pts[:3], (3.5, 3, 2.5)):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=CRANE_D + (255,), outline=INK + (255,))
    c = pts[3]
    pay = (DX + big[4][0], DY + big[4][1])
    v = (pay[0] - c[0], pay[1] - c[1])
    nv = math.hypot(*v) or 1.0
    u = (v[0] / nv, v[1] / nv)
    if held:   # the rocket across the claw: 11 squares long, its red-finned tail and its pale nose
        a, b = (c[0] - u[0] * 4, c[1] - u[1] * 4), (c[0] + u[0] * 7, c[1] + u[1] * 7)
        d.line([a, b], fill=INK + (255,), width=7)
        d.line([a, b], fill=ROCKET + (255,), width=5)
        for t in (-4.0, -2.5):
            m = (c[0] + u[0] * t, c[1] + u[1] * t)
            d.line([(m[0] - u[1] * 4, m[1] + u[0] * 4), (m[0] + u[1] * 4, m[1] - u[0] * 4)], fill=ROCKET_R + (255,), width=2)
        m = (c[0] + u[0] * 1.0, c[1] + u[1] * 1.0)
        d.line([(m[0] - u[1] * 2.5, m[1] + u[0] * 2.5), (m[0] + u[1] * 2.5, m[1] - u[0] * 2.5)], fill=ROCKET_R + (255,), width=2)
    # the red claw: two jaws round the grip
    for side in (-1, 1):
        q = (c[0] + u[1] * 2.5 * side, c[1] - u[0] * 2.5 * side)
        d.line([c, (q[0] + u[0] * 2.5, q[1] + u[1] * 2.5)], fill=INK + (255,), width=4)
        d.line([c, (q[0] + u[0] * 2.5, q[1] + u[1] * 2.5)], fill=CLAW + (255,), width=2)
    d.ellipse([c[0] - 2.5, c[1] - 2.5, c[0] + 2.5, c[1] + 2.5], fill=CLAW + (255,), outline=INK + (255,))
    return can


# PROPS: name -> (tag, League ms, rocket held, what the crane does) - the crane's 15 positions over Q, E and W
# (League's joints clustered within 2.5 squares; Q, E and W lift the same rocket in League) and R's three
PROPS = {
    "crane_peek": ("skill", 0, True, "机械臂刚从头发后面（背包里）伸出来，折着，爪子抓着火箭竖在头顶后面"),
    "crane_peek2": ("skill2", 0, True, "机械臂刚伸出来，往上抬，爪子抓着火箭朝右上"),
    "crane_up": ("skill", 100, True, "机械臂高高举起，爪子抓着火箭竖在最上面"),
    "crane_up_empty": ("skill", 800, False, "机械臂高高举起，爪子空着（火箭已经放出去了）"),
    "crane_up_back": ("skill", 200, True, "机械臂举高，稍往后仰，抓着火箭"),
    "crane_up_high": ("skill", 300, True, "机械臂举到最高，抓着火箭"),
    "crane_place": ("skill", 400, True, "机械臂从头顶往前弯下来，把火箭（炮台套件）放到他身前右边的地上"),
    "crane_lift": ("skill", 500, False, "放完往回抬，爪子空着，机械臂在头顶前方"),
    "crane_return": ("skill", 600, False, "机械臂竖回头顶，爪子空着往右"),
    "crane_fold": ("skill", 1050, False, "机械臂折回背包里，只露出一小截在头发后面"),
    "crane_cock": ("skill2", 300, True, "机械臂往前上方伸，抓着火箭（准备甩出去）"),
    "crane_throw": ("skill2", 400, False, "机械臂往前一甩，爪子空着（手雷刚扔出去）"),
    "crane_recoil": ("skill2", 500, False, "甩完往回收，爪子空着"),
    "crane_aim": ("attack_w", 142, True, "机械臂举高，抓着火箭准备发射"),
    "crane_fire": ("attack_w", 283, False, "火箭刚发射，机械臂往后一震，爪子空着张开"),
    "crane_recover": ("attack_w", 425, False, "发射后往回收，爪子空着"),
    "crane_aim_empty": ("attack_w", 700, False, "机械臂举高，爪子空着"),
}
R_GEAR = {
    "gear_drum": ("ult", 200, "背包顶上弹出一个橄榄绿的圆鼓（在头发顶上偏后），还没有弹簧"),
    "gear_burst": ("ult", 333, "两根带红球的弹簧天线从头顶两边高高弹起，头顶外面张开一圈红边的深色圆环"),
    "gear_settle": ("ult", 467, "弹簧天线回弹，矮一点，红球还在顶上；圆环还在"),
}


def grid(img_px):
    d = ImageDraw.Draw(img_px)
    for x in range(0, CANVAS, PX * 5):
        d.line([(x, 0), (x, CANVAS)], fill=(205, 205, 205, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        d.line([(0, y), (CANVAS, y)], fill=(205, 205, 205, 255))
    d.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)


def on_canvas(layer_1x, under=None, label=""):
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    grid(can)
    if under is not None:
        can.alpha_composite(under.resize((under.width * PX, under.height * PX), Image.NEAREST))
    can.alpha_composite(layer_1x.resize((layer_1x.width * PX, layer_1x.height * PX), Image.NEAREST))
    if label:
        ImageDraw.Draw(can).text((12, 12), label, fill=(40, 40, 40, 255))
    return can


def ghost(d):
    """The design in grey, one pixel a square, on the canvas grid (only to place a prop)."""
    n = CANVAS // PX
    can = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    g = d.copy()
    op = g[..., 3] > 0
    v = (g[..., :3].mean(-1) * 0.35 + 150).astype(np.uint8)
    g[..., 0] = g[..., 1] = g[..., 2] = v
    g[..., 3] = np.where(op, 255, 0)
    can.alpha_composite(Image.fromarray(g), (DX, DY))
    return can


def league_frame(lol, frame, out, name):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Heimerdinger",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "1000", "--fit", "0.42",
           "--ground", "0.92", "--width", "1.0", "--yaw", "35", "--name", name, "--out", out, "--frame", frame]
    subprocess.run(cmd, check=True, capture_output=True)
    path = os.path.join(out, name + ".png")
    im = Image.open(path).convert("RGB")
    g = np.abs(np.asarray(im).astype(int) - GREY).sum(-1) > 30
    yy, xx = np.nonzero(g)
    m = 40
    im.crop((max(0, xx.min() - m), max(0, yy.min() - m), min(im.width, xx.max() + m), min(im.height, yy.max() + m))).save(path)
    return path


def row(J, tag, ms):
    for r in J["tags"][tag]:
        if int(r["frame"].split("@")[1]) == ms:
            return r
    raise KeyError((tag, ms))


def build(J, lol, out_body, out_props, check=None):
    d = load_design()
    P = pieces(d)
    j0 = J["design"]
    for o in (out_body, out_props):
        if os.path.isdir(o):
            shutil.rmtree(o)
        os.makedirs(o)
    # the design on the grid and the head, 8x (both packs)
    n = CANVAS // PX
    full = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    full.alpha_composite(Image.fromarray(d), (DX, DY))
    for o in (out_body, out_props):
        on_canvas(full, label="0: the approved design, 12 px a square, soles on y 1200").convert("RGB").save(
            os.path.join(o, "0_design.png"))
    head = P["head"]
    ys, xs = np.nonzero(head[..., 3] > 0)
    h = head[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
    hb.alpha_composite(Image.fromarray(up(h, 8)))
    hb.convert("RGB").save(os.path.join(out_body, "1_head.png"))
    rows_check = []
    for k, (name, (tag, ms, bounce, _)) in enumerate(BODY.items(), 2):
        r = row(J, tag, ms)
        # lying, League's body has slid far off (it lands 24 game px back): the standing design is laid down instead
        rough = rough_body(P, j0 if TILT.get(name, 0) >= 80 else r["j"], j0, bounce)
        if name in TILT:
            rough = tilt(rough, TILT[name])
        img = on_canvas(rough, label=f"b{k} {name}: ROUGH - size and place right, joins broken; redraw it clean")
        img.convert("RGB").save(os.path.join(out_body, f"b{k}_{name}_rough.png"))
        lf = league_frame(lol, r["frame"], out_body, f"b{k}_{name}_league")
        rows_check.append((name, img, lf))
    gh = ghost(d)
    for k, (name, (tag, ms, held, _)) in enumerate(PROPS.items(), 2):
        r = row(J, tag, ms)
        img = on_canvas(rough_crane(r["j"], held), gh, f"p{k} {name}: draw ONLY the crane (olive), rocket {'HELD' if held else 'GONE'}")
        img.convert("RGB").save(os.path.join(out_props, f"p{k}_{name}_guide.png"))
        lf = league_frame(lol, r["frame"], out_props, f"p{k}_{name}_league")
        rows_check.append((name, img, lf))
    k0 = len(PROPS) + 2
    for k, (name, (tag, ms, _)) in enumerate(R_GEAR.items(), k0):
        r = row(J, tag, ms)
        lay = gear_guide(r["j"])
        img = on_canvas(lay, gh, f"p{k} {name}: draw ONLY R's gear round his head")
        img.convert("RGB").save(os.path.join(out_props, f"p{k}_{name}_guide.png"))
        lf = league_frame(lol, r["frame"], out_props, f"p{k}_{name}_league")
        rows_check.append((name, img, lf))
    if check:
        os.makedirs(check, exist_ok=True)
        tiles = []
        for name, img, lf in rows_check:
            L = Image.open(lf).convert("RGB")
            c = img.convert("RGB").crop((0, 200, CANVAS, CANVAS))
            L = L.resize((round(L.width * c.height / L.height), c.height))
            pair = Image.new("RGB", (L.width + c.width, c.height), (255, 255, 255))
            pair.paste(L, (0, 0))
            pair.paste(c, (L.width, 0))
            tiles.append(pair.resize((pair.width // 3, pair.height // 3)))
        per = 3
        W = max(t.width for t in tiles)
        H = tiles[0].height
        for page in range(0, len(tiles), 12):
            sub = tiles[page:page + 12]
            sheet = Image.new("RGB", (per * W, ((len(sub) + per - 1) // per) * H), (255, 255, 255))
            for i, t in enumerate(sub):
                sheet.paste(t, ((i % per) * W, (i // per) * H))
            sheet.save(os.path.join(check, f"check_{page // 12}.png"))


def gear_guide(j):
    """R's gear at one pixel a square: the antennas from their roots to their tips (League's joints), a ring round the
    top of the mane, the drum on top behind."""
    n = CANVAS // PX
    can = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(can)
    # the drum on top of the mane, behind (League shows it from the cast on), the ring round the top of the mane once
    # the antennas are out (their tips over 8 game px above their roots)
    d.rounded_rectangle([DX + 14, DY - 5, DX + 24, DY + 4], radius=2, fill=CRANE_C + (255,), outline=INK + (255,), width=1)
    out = xy(j, "l_ant_tip")[1] < xy(j, "l_antenna")[1] - 8 * S
    if out:
        d.ellipse([DX - 3, DY + 3, DX + 53, DY + 17], outline=INK + (255,), width=4)
        d.ellipse([DX - 2, DY + 4, DX + 52, DY + 16], outline=RING_R + (255,), width=2)
    for a, b in (("l_antenna", "l_ant_tip"), ("r_antenna", "r_ant_tip")):
        pa, pb = xy(j, a), xy(j, b)
        pb = (pa[0] + (pb[0] - pa[0]) * CRANE_K, pa[1] + (pb[1] - pa[1]) * CRANE_K)
        pa, pb = (DX + pa[0], DY + pa[1]), (DX + pb[0], DY + pb[1])
        d.line([pa, pb], fill=INK + (255,), width=4)
        d.line([pa, pb], fill=CRANE_C + (255,), width=2)
        d.ellipse([pb[0] - 2.5, pb[1] - 2.5, pb[0] + 2.5, pb[1] + 2.5], fill=CLAW + (255,), outline=INK + (255,))
    return can


def merge_tools(J, path):
    """Each tool's two ends (l_ta / l_tb the wrench's, r_ta / r_tb the multitool's) from the exports made with
    "weapon_joint" L_Weapon / R_Weapon (<joints dir>_l / _r, same frames) into J's rows."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    for side in ("l", "r"):
        T = json.load(open(os.path.join(base, f"joints_{side}", "heimerdinger_joints.json"), encoding="utf-8"))
        J["design"][f"{side}_ta"], J["design"][f"{side}_tb"] = T["design"]["weapon_a"], T["design"]["weapon_b"]
        for tag, rows in J["tags"].items():
            for r, t in zip(rows, T["tags"][tag]):
                assert r["frame"] == t["frame"]
                r["j"][f"{side}_ta"], r["j"][f"{side}_tb"] = t["j"]["weapon_a"], t["j"]["weapon_b"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--joints", required=True)
    ap.add_argument("--out", default="C:/t/hd_work/heimerdinger_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    a = ap.parse_args()
    J = json.load(open(a.joints, encoding="utf-8"))
    merge_tools(J, a.joints)
    out_body, out_props = a.out + "_body", a.out + "_props"
    build(J, a.lol, out_body, out_props, a.check)
    if a.check:
        return
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out_body, "POSE_PROMPTS.md"))
    shutil.copyfile(lp(os.path.join(SRC, "CRANE_PROMPTS.md")), os.path.join(out_props, "CRANE_PROMPTS.md"))
    for o in (out_body, out_props):
        print("written", shutil.make_archive(o, "zip", o))


if __name__ == "__main__":
    main()
