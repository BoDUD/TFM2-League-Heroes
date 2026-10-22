#!/usr/bin/env python3
"""Ivern's pose pack for Codex (assets/source/ivern/POSE_PROMPTS.md): the whole-body poses his League clips go through,
and Daisy's front-view poses (the user, 2026-10-22: 「动作帧让gpt做吧」, pack_hwei_poses.py's way).

    python tools/art/pack_ivern_poses.py [--out C:/t/iv_work/ivern_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at PX px a square, soles on y SOLE_Y - the design hd/idle.png (Codex's step-1 A-2, 61 x
60) sits at squares (DX + shift, DY) on it. The skeletons are set by hand after League's frames (tools/lol/pose_ref.py
at the 3/4 camera): every bone at the design's OWN length (measured on hd/idle.png at 14x: REST), only its direction set
per pose (POSES), the lowest foot on the ground unless the pose lifts it. The prompt gives the legs' and arms' lengths
in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22). His props are small and stay in his
hands: the leafy twig in the near hand, the apple in the far one (a dot on the skeleton marks each hand).
DAISY (R) is drawn from the front (an effect picture, never mirrored) on her own design hd/daisy.png (95 x 76, PPU 1.9)
at the same PX: no skeleton (blocky stone limbs), League's front frame and a line of text for each (DAISY).
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton.png (the design on the grid with its own skeleton);
1_head.png (the design's head with its horns and mushroom, 8x: every pose wears it); 2_design.png (the design on the
grid); per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local);
D0_daisy.png (her design on the grid) and per Daisy pose D<k>_<name>_league.png (her front frame).
--check DIR: each skeleton beside League's frame, and the design's own skeleton over the design (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left, the twig), PURPLE = the FAR arm (image right, the apple); grey box = the
head (the design's head with its horns, never redrawn).
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
from design_ivern_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ivern")
PX, CANVAS, SOLE_Y = 12, 1254, 1200
GREY = (225, 225, 225)
GROUND = 60                        # the design's soles' bottom edge (rows)
DX, DY = 21, SOLE_Y // PX - GROUND  # the design's (0, 0) on the canvas grid (its soles on row 100)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200)}
HEAD = (0, 25, 8, 61)              # rows / columns of the mushroom, the horns and the face in hd/idle.png (ends exclusive)
HW, HH = HEAD[3] - HEAD[2], HEAD[1] - HEAD[0]   # the head box, 53 x 25 squares
FACE = (31, 47, 12, 26)            # the face (brows, eyes, nose, grin): x0, x1, y0, y1 in design squares

# the design's own skeleton, measured on hd/idle.png (61 x 60, square edges): the head box's middle; the spine pelvis ->
# the base of the neck; each arm shoulder, elbow, wrist, the fingers' tips (the near hand up by the horn holding the
# twig, the far hand holding the apple); each leg hip, knee, ankle, toes
REST = {
    "head": (34.5, 12.5),
    "spine": [(33.0, 43.0), (33.0, 24.0)],
    "near_arm": [(24.0, 30.0), (17.0, 36.0), (11.0, 25.0), (7.0, 22.0)],
    "far_arm": [(44.0, 31.0), (49.0, 38.0), (54.0, 36.0), (56.5, 33.0)],
    "near_leg": [(29.0, 44.0), (27.0, 50.0), (26.0, 55.0), (31.0, 59.0)],
    "far_leg": [(40.0, 44.0), (42.0, 50.0), (42.0, 55.0), (47.0, 59.0)],
}

# the poses: name -> (League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton: the
# pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), "shift" (squares the whole
# figure is moved on the canvas), the spine's direction and every limb (degrees: 0 straight down, 90 to the image right,
# 180 up, -90 to the image left) - each bone at the design's own length (REST). A limb is "rest" (the design's own,
# turned with the spine), three angles, or (target, side, last angle): the wrist / ankle at the target with the elbow /
# knee solved at the design's lengths (side -1 bends a downward limb's middle joint to the image right, +1 to the image
# left), then the hand / foot at the last angle.
POSES = {
    "a_wind": ("ivern_attack01@250",
               "扔种子蓄势：身子往左后方微微仰，远侧手臂（拿苹果那只，这里手里是一颗种子）往左后下方甩到身后（手在腰后），近侧手臂往前伸，两腿分开（普攻起手）",
               "WIND-UP - leaning back a little toward the image left, the FAR arm (the apple hand, here holding a "
               "seed) swung down and back behind his waist, the near arm reaching forward, the legs apart.",
               dict(pelvis=(33.0, 43.0), lift=None, shift=2, spine=-174, far_arm=(-30, -60, -80),
                    near_arm=(60, 80, 100), near_leg=((26.0, 59.0), 1, 70), far_leg=((42.0, 59.0), -1, 70))),
    "a_throw": ("ivern_attack01@700",
                "扔出种子：身子往前倾，远侧手臂往右前方甩出去伸直（手在肩的高度），近侧手臂往后甩，前腿（远侧）屈膝（普攻出手）",
                "THROW - leaning forward, the FAR arm flung out straight to the front right (the hand at shoulder "
                "height), the near arm swung back, the front (far) knee bent.",
                dict(pelvis=(33.0, 44.0), lift=None, shift=-3, spine=168, far_arm=(110, 100, 95),
                     near_arm=(-60, -40, -30), near_leg=((24.0, 59.0), 1, 60), far_leg=((44.0, 59.0), -1, 70))),
    "e_gather": ("ivern_spell3_idle_fwd@0",
                 "蹲下聚力：两膝弯下去蹲低，身子往前弓，两只手臂收在胸前（手心相对，像捧着一颗种子），头低一点（种豆得瓜起手）",
                 "GATHER - crouching low on bent knees, hunched forward, both arms drawn in before his chest, hands "
                 "facing as if cupping a seed.",
                 dict(pelvis=(32.0, 48.0), lift=None, shift=0, spine=168, far_arm=(30, -40, -60),
                      near_arm=(40, 70, 90), near_leg=((25.0, 59.0), 1, 40), far_leg=((42.0, 59.0), -1, 40))),
    "e_give": ("ivern_spell3_idle_fwd@900",
               "抛给队友：站起来，远侧手臂往右上方伸直、手掌张开（把种子护盾抛给队友），近侧手臂往左张开，近侧腿在前（种豆得瓜放出）",
               "GIVE - standing up, the FAR arm reaching up to the upper right with the palm open (tossing the seed "
               "shield to an ally), the near arm spread out to the left, the near leg in front.",
               dict(pelvis=(33.0, 43.0), lift=None, shift=-2, spine=176, far_arm=(140, 135, 130),
                    near_arm=(-110, -100, -100), near_leg=((26.0, 59.0), 1, 60), far_leg=((41.0, 59.0), -1, 70))),
    "q_wind": ("ivern_spell1@100",
               "拧身蓄力：身子往左后方拧，近侧手臂（拿小树枝那只）往左后上方高高扬起，远侧手臂收在胸前，膝盖微弯（根深敌固起手）",
               "COIL - twisting back toward the image left, the NEAR arm (the twig hand) swung high up and back to the "
               "upper left, the far arm drawn in before his chest, the knees a little bent.",
               dict(pelvis=(34.0, 45.0), lift=None, shift=4, spine=-170, far_arm=(-30, -70, -90),
                    near_arm=(-140, -160, -170), near_leg=((26.0, 59.0), 1, 50), far_leg=((43.0, 59.0), -1, 50))),
    "q_fling": ("ivern_spell1@330",
                "甩出荆棘：大步往前，身子前倾，近侧手臂从左往右前方甩出去伸直（手在腰的高度，荆棘从这里甩出），远侧手臂往后张开，后腿（近侧）往后伸直（根深敌固打出）",
                "FLING - a big step forward, leaning forward, the NEAR arm whipped across to the front right and "
                "stretched out at waist height (the vine flies from it), the far arm flung back, the back (near) leg "
                "stretched out behind.",
                dict(pelvis=(33.0, 46.0), lift=None, shift=-4, spine=160, far_arm=(-90, -110, -120),
                     near_arm=(80, 90, 95), near_leg=((18.0, 59.0), 1, -60), far_leg=((46.0, 59.0), -1, 70))),
    "r_crouch": ("ivern_spell4@0",
                 "蹲下蓄力：深深蹲下，两膝往外分开，身子往前弓，两只手臂往下垂到膝盖边（大招起手）",
                 "CROUCH - squatting deep, the knees spread apart, hunched forward, both arms hanging down beside his "
                 "knees.",
                 dict(pelvis=(33.0, 50.0), lift=None, shift=0, spine=172, far_arm=(10, -10, -20),
                      near_arm=(-10, 10, 20), near_leg=((24.0, 59.0), 1, 30), far_leg=((43.0, 59.0), -1, 30))),
    "r_leap": ("ivern_spell4@400",
               "跃起召唤：往上跳起（脚离地约 8 格），远侧腿往下伸直、近侧腿屈膝收起，近侧手臂笔直举过头顶（召唤小菊），远侧手臂往右张开（大招跳起）",
               "LEAP - jumping up (the feet about 8 squares off the ground), the far leg stretched down, the near knee "
               "tucked, the NEAR arm thrust straight up above his head (calling Daisy), the far arm out to the right.",
               dict(pelvis=(33.0, 42.0), lift=8, shift=0, spine=178, far_arm=(110, 120, 130),
                    near_arm=(-170, 180, 180), near_leg=((27.0, 49.0), 1, 80), far_leg=((41.0, 58.0), -1, 30))),
    "r_call": ("ivern_spell4@1200",
               "落地举手：站直，近侧手臂高高举起（小树枝朝上），远侧手臂垂在身边，两腿并拢站稳（大招收尾：小菊出来了）",
               "CALL - standing tall, the NEAR arm raised high (the twig pointing up), the far arm hanging at his side, "
               "the legs close together.",
               dict(pelvis=(33.0, 43.0), lift=None, shift=0, spine=178, far_arm=(20, 10, 0),
                    near_arm=(-170, -175, 180), near_leg=((30.0, 59.0), 1, 70), far_leg=((38.0, 59.0), -1, 70))),
    "run1": ("ivern_run_base@0", "跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，近侧手臂往后摆，远侧手臂往前摆",
             "RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back "
             "behind, leaning forward a little, the near arm swinging back, the far arm forward.",
             dict(pelvis=(33.0, 45.0), lift=None, shift=0, spine=172, far_arm=(60, 40, 30),
                  near_arm=(-40, -20, -10), near_leg=((20.0, 58.0), 1, -40), far_leg=((46.0, 59.0), -1, 70))),
    "run2": ("ivern_run_base@420", "跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两臂垂在身边",
             "RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square "
             "higher, both arms hanging close.",
             dict(pelvis=(33.0, 43.0), lift=1, shift=0, spine=174, far_arm=(20, 10, 0),
                  near_arm=(-10, 0, 10), near_leg=((31.0, 59.0), 1, 60), far_leg=((42.0, 52.0), -1, 70))),
    "run3": ("ivern_run_base@840", "跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：近侧手臂往前摆，远侧手臂往后摆",
             "RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back "
             "behind, leaning forward a little, the near arm swinging forward, the far arm back.",
             dict(pelvis=(33.0, 45.0), lift=None, shift=0, spine=172, far_arm=(-40, -20, -10),
                  near_arm=(40, 60, 70), near_leg=((44.0, 59.0), -1, 70), far_leg=((22.0, 57.0), 1, -40))),
    "run4": ("ivern_run_base@1260", "跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格",
             "RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square "
             "higher, both arms hanging close.",
             dict(pelvis=(33.0, 43.0), lift=1, shift=0, spine=174, far_arm=(10, 0, -10),
                  near_arm=(0, 10, 20), near_leg=((38.0, 52.0), -1, 80), far_leg=((36.0, 59.0), -1, 60))),
    "d_stagger": ("ivern_death@600",
                  "踉跄：身子往左后方倒，膝盖发软，近侧手臂往左后方甩开，远侧手臂往右伸着（苹果从手里掉下来，落在他右前方的地上）（死亡第一下）",
                  "STAGGER - toppling back toward the image left, the knees giving way, the near arm flung back to the "
                  "left, the far arm reaching out to the right, the apple dropped and lying on the ground in front of "
                  "him on the image right.",
                  dict(pelvis=(32.0, 46.0), lift=None, shift=2, spine=-160, far_arm=(100, 80, 70),
                       near_arm=(-100, -120, -130), near_leg=((26.0, 59.0), 1, 50), far_leg=((40.0, 59.0), -1, 60))),
    # League's death ends lying flat; the head is pasted upright in every pose, so ours slumps sitting instead
    "d_slump": ("ivern_death@2000",
                "瘫坐：一屁股坐在地上，两条腿往画面右边平伸在地上，身子往前趴下去，头低下来，两只手臂软软地垂到地上；苹果在他右前方的地上（死亡）",
                "SLUMPED - sitting down hard on the ground, both legs stretched out flat to the image right along the "
                "ground, the body slumped forward, the head low, both arms hanging limp to the ground; the apple lying "
                "in front of him on the image right.",
                dict(pelvis=(30.0, 58.0), lift=None, shift=-2, spine=150, far_arm=(70, 60, 50),
                     near_arm=(50, 70, 80), near_leg=(95, 90, 100), far_leg=(85, 92, 100))),
}

# Daisy's poses, front view: name -> (League's frame, Chinese, English)
DAISY = {
    "dz_rise": ("ivernminion_spawn@900",
                "钻出地面：从地里跳出来（脚离地约 6 格），两只大拳头往两边举起张开，身上掉着土块（召唤登场）",
                "RISE - leaping up out of the ground (the feet about 6 squares up), both huge fists raised and spread "
                "to the sides, a few clods falling off her."),
    "dz_wind": ("ivernminion_attack1@400",
                "举拳：画面左边那只大拳头高高举过头顶，另一只拳头垂在身边，身子微微往左歪（第一、二拳起手）",
                "RAISE ONE FIST - the fist on the image left raised high above her head, the other fist hanging at her "
                "side, leaning a little to the image left."),
    "dz_punch": ("ivernminion_attack1@600",
                 "砸拳：那只拳头往前下方砸下来，砸在她身前正中的地上，身子往前压（第一、二拳）",
                 "SMASH ONE FIST - that fist smashed down to the ground in front of her middle, the body pressing "
                 "forward and down."),
    "dz_up": ("ivernminion_attack3@400",
              "双拳举起：两只大拳头一起高高举过头顶，身子挺直（第三拳起手）",
              "BOTH FISTS UP - both huge fists raised high above her head together, the body upright."),
    "dz_slam": ("ivernminion_attack3@800",
                "双拳砸地：两只拳头一起砸在身前的地上，深深蹲下（第三拳：震飞敌人）",
                "SLAM - both fists slammed into the ground in front of her together, crouching deep."),
    "dz_wave": ("ivernminion_despawn@600",
                "挥手告别：画面左边那只手抬到肩膀上方挥手（手掌张开），另一只拳头垂着，身子开始往下沉（小菊离开）",
                "WAVE GOODBYE - the hand on the image left raised above her shoulder, open, waving, the other fist "
                "hanging, the body starting to sink."),
}


def ang(a, b):
    """The direction a -> b in degrees (0 = straight down, 90 = to the image right; y down)."""
    return math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))


def along(p, deg, length):
    r = math.radians(deg)
    return (p[0] + length * math.sin(r), p[1] + length * math.cos(r))


def turned(v, deg):
    """A vector turned the way ang() counts: +deg turns straight down towards the image right."""
    r = math.radians(deg)
    x, y = v
    return (x * math.cos(r) + y * math.sin(r), -x * math.sin(r) + y * math.cos(r))


def lengths(name):
    pts = REST[name]
    return [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]


def bend(H, A, l1, l2, side):
    """The middle joint of a two-bone limb from H towards A (A pulled in or pushed out to what the bones reach): side +1
    puts it to the image left of a limb pointing down, -1 to the image right (pack_shyvana_poses.bend)."""
    vx, vy = A[0] - H[0], A[1] - H[1]
    d = math.hypot(vx, vy) or 1e-9
    d2 = max(abs(l1 - l2) + 0.3, min(l1 + l2 - 0.05, d))
    ux, uy = vx / d, vy / d
    a = (l1 * l1 - l2 * l2 + d2 * d2) / (2 * d2)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    px, py = -uy, ux
    if side < 0:
        px, py = -px, -py
    M = (H[0] + ux * a + px * h, H[1] + uy * a + py * h)
    return M, (H[0] + ux * d2, H[1] + uy * d2)


def build(spec):
    """A skeleton from a pose spec: the bones at the design's own lengths; the shoulders where the design has them on
    its spine, turned with the spine, the hips turned half as much; the head box upright over the neck (the head is
    pasted, never turned). The lowest foot or knee on the ground, or `lift` rows over it."""
    rs = REST["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths("spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + REST["head"][0] - rs[1][0], neck[1] + REST["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("near_arm", neck, rs[1], 1.0), ("far_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5)):
        sp = spec[name]
        if sp == "rest":
            sk[name] = [(base[0] + o[0], base[1] + o[1]) for o in
                        (turned((x - base_rest[0], y - base_rest[1]), turn * k) for x, y in REST[name])]
            continue
        off = turned((REST[name][0][0] - base_rest[0], REST[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(name)
        if len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    low = max(y for leg in ("near_leg", "far_leg", "spine") for _, y in sk[leg])
    dy = GROUND - (spec["lift"] or 0) - low
    return {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}


def to_canvas(sk, shift=0):
    return {k: ((v[0] + DX + shift, v[1] + DY) if k == "head" else [(x + DX + shift, y + DY) for x, y in v])
            for k, v in sk.items()}


def canvas_grid():
    can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    dr = ImageDraw.Draw(can)
    for x in range(0, CANVAS, PX * 5):
        dr.line([(x, 0), (x, CANVAS)], fill=(215, 215, 215, 255))
    for y in range(SOLE_Y % (PX * 5), CANVAS, PX * 5):
        dr.line([(0, y), (CANVAS, y)], fill=(215, 215, 215, 255))
    dr.line([(0, SOLE_Y), (CANVAS, SOLE_Y)], fill=(230, 40, 40, 255), width=3)
    return can


def c(p):
    """A point in design square edges, already on the canvas grid, in canvas px."""
    return (p[0] * PX, p[1] * PX)


def skeleton(can, s, label, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it);
    a bigger dot on each hand (the twig / the apple)."""
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - HW / 2) * PX, (hy - HH / 2) * PX, (hx + HW / 2) * PX, (hy + HH / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    for name in ("far_leg", "far_arm", "spine", "near_leg", "near_arm"):
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=7, joint="curve")
        for k, p in enumerate(pts):
            rr = 11 if name.endswith("arm") and k == 2 else 6
            dr.ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=COL[name] + (alpha,))
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, work, champ="Ivern", yaw=35):
    """League's frame (Ivern at the 3/4 camera, Daisy from the front)."""
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", champ,
           "--wad", "Ivern", "--hide-submeshes", "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels",
           "--size", "900", "--fit", "0.4", "--ground", "0.8", "--width", "2.0", "--yaw", str(yaw), "--name", "f",
           "--out", work, "--frame", frame]
    if champ == "Ivern":
        cmd.append("--mirror")
    subprocess.run(cmd, check=True, capture_output=True)
    im = Image.open(os.path.join(work, "f.png")).convert("RGB")
    a = np.asarray(im).astype(int)
    fg = np.abs(a - GREY).sum(2) > 12
    ys, xs = np.nonzero(fg)
    m = 40
    return im.crop((max(0, xs.min() - m), max(0, ys.min() - m), min(im.width, xs.max() + m), min(im.height, ys.max() + m)))


def big(a, z=8):
    im = Image.fromarray(up(a, z))
    bg = Image.new("RGBA", im.size, GREY + (255,))
    bg.alpha_composite(im)
    return bg.convert("RGB")


def poses_built():
    return {name: (to_canvas(build(spec), spec.get("shift", 0)), frame, zh, en)
            for name, (frame, zh, en, spec) in POSES.items()}


def problems(name, s):
    """Every bone and the head box on the canvas; no hand over the face."""
    out = []
    pts = [p for k in ("spine", "near_arm", "far_arm", "near_leg", "far_leg") for p in s[k]]
    if any(x < 1 or x > CANVAS / PX - 1 or y < 1 or y > SOLE_Y / PX + 0.6 for x, y in pts):
        out.append("off the canvas / below the ground")
    hx, hy = s["head"]
    if hy - HH / 2 < 1 or hx - HW / 2 < 0 or hx + HW / 2 > CANVAS / PX:
        out.append("head off the canvas")
    ox, oy = hx - HW / 2 - HEAD[2], hy - HH / 2 - HEAD[0]   # the design's (0, 0) as the head box has it
    fx0, fx1, fy0, fy1 = FACE[0] + ox, FACE[1] + ox, FACE[2] + oy, FACE[3] + oy
    face = [p for p in s["near_arm"][2:] + s["far_arm"][2:] if fx0 <= p[0] <= fx1 and fy0 <= p[1] <= fy1]
    if face and name != "d_fall":
        out.append(f"hand over the face at {[(round(x), round(y)) for x, y in face[:3]]}")
    return out


def tile_sheet(tiles, path, cols=3):
    W = max(t.width for t in tiles)
    H = max(t.height for t in tiles)
    rows_ = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (W * cols, H * rows_), (255, 255, 255))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % cols) * W, (k // cols) * H))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/iv_work/ivern_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated poses (with --check)")
    a = ap.parse_args()
    idle = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "idle.png"))).convert("RGBA"))
    daisy = np.asarray(Image.open(lp(os.path.join(SRC, "hd", "daisy.png"))).convert("RGBA"))
    poses = poses_built()
    rest = to_canvas(build(dict(pelvis=REST["spine"][0], lift=None, spine=ang(*REST["spine"]), far_arm="rest",
                                near_arm="rest", near_leg="rest", far_leg="rest")))
    for name, (s, *_) in poses.items():
        for p in problems(name, s):
            print("PROBLEM", name, p)
    r0, r1, c0, c1 = HEAD
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
            hx, hy = s["head"]                       # the design's head in its box, to judge the chibi proportions
            can.alpha_composite(Image.fromarray(up(idle[r0:r1, c0:c1], PX)),
                                (round((hx - HW / 2) * PX), round((hy - HH / 2) * PX)))
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
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    base = canvas_grid()
    base.alpha_composite(on_grid(idle, DX, DY))
    clean = base.copy()
    skeleton(base, rest, "0: the approved design with its own skeleton (what each coloured line stands for)", 200)
    base.convert("RGB").save(os.path.join(out, "0_design_skeleton.png"))
    clean.convert("RGB").save(os.path.join(out, "2_design.png"))
    big(idle[r0:r1, c0:c1]).save(os.path.join(out, "1_head.png"))
    for k, (name, (s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, s, f"{k}: {name} - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(name, frame)
    dz = canvas_grid()
    dz.alpha_composite(on_grid(daisy, (CANVAS // PX - daisy.shape[1]) // 2, SOLE_Y // PX - daisy.shape[0]))
    dz.convert("RGB").save(os.path.join(out, "D0_daisy.png"))
    for k, (name, (frame, zh, en)) in enumerate(DAISY.items(), 1):
        lol_frame(a.lol, frame, out + "_work", "IvernMinion", 0).save(os.path.join(out, f"D{k}_{name}_league.png"))
        print(name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
