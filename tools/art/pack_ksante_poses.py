#!/usr/bin/env python3
"""K'Sante's pose pack for Codex (assets/source/ksante/POSE_PROMPTS.md): the whole-body poses his two stances go through
in League's clips that the 3/4 designs cannot give by moving their own parts - the overhead ntofo swings and slams, the
wall of ntofos he braces behind, the shield bash and the dive, the fall, the run with the ntofos carried upright; All
Out's swings, leaps, crossed clubs, charge and hunched run (Shyvana's skeleton way, pack_shyvana_poses.py, plus the
ntofos as bones; the user, Shyvana 2026-10-21: 「做到完美后喊我review 如果有动作实在做不出 就让codex帮忙」).

    python tools/art/pack_ksante_poses.py [--out C:/t/ks_work/ksante_pose_pack] [--lol D:/WeGameApps/lol] [--check DIR]

Every pose is ONE 1254 picture at 10 px a square, soles on y 1180 - the stance's design (hd/idle.png 65 x 72, hd/ao_idle.png
81 x 56: the same body size, ao_idle cut to 56 rows for it) sits at squares (DX, DY) on it. The skeletons are set by
hand after League's frames: every bone at the design's OWN length (measured on the design: REST), only its direction set
per pose (POSES), the feet on the ground unless the pose lifts them. Each ntofo is a rigid bone through the fist: its
long end (the base stance: the top, 45 squares above the grip, the short end 23 below; All Out: the club's head, 23
squares out, the butt 4 behind) at the angle the pose gives.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_skeleton_{base,ao}.png (each design on the grid with its own
skeleton); 1_head_{base,ao}.png (each design's head, 8x: every pose of that stance wears it); 2_design_{base,ao}.png;
per pose <k>_<name>_skeleton.png and <k>_<name>_league.png (League's frame, 3/4 facing right: Riot's, kept local).
--check DIR: each skeleton beside League's frame, and each design's own skeleton over it (nothing else written).
Skeleton colours: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg
(image right), ORANGE = the NEAR arm (image left) to the fist, PURPLE = the FAR arm (image right), TEAL = the near
ntofo, CYAN = the far ntofo (a thick line, its long end marked with a ring); grey box = the head (the design's head,
never redrawn).
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
from design_ksante_hd import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "ksante")
PX, CANVAS, SOLE_Y = 10, 1254, 1180
GREY = (225, 225, 225)
COL = {"spine": (0, 170, 60), "near_leg": (230, 30, 30), "far_leg": (40, 90, 230), "near_arm": (255, 140, 0),
       "far_arm": (150, 60, 200), "near_wpn": (0, 140, 130), "far_wpn": (0, 200, 230)}
PARTS = ("near_arm", "far_arm", "near_leg", "far_leg")
PARTS_LOL = ["--submesh-texture", "Weapon=Weapons_TX", "--submesh-texture", "RWeaponShield=Weapons_TX",
             "--submesh-texture", "LWeaponShield=Weapons_TX"]
for _s in ("RWeaponShieldSmearTop", "RWeaponShieldSmearBot", "LWeaponShieldSmearTop", "LWeaponShieldSmearBot",
           "RWeaponBlade", "LWeaponBlade"):
    PARTS_LOL += ["--hide-submesh", _s]

# each stance's design and its own skeleton, measured on the design (square edges): the head box's middle; the spine
# pelvis -> the base of the neck; each arm shoulder, elbow, wrist, the fist; each leg hip, knee, ankle, toes; each ntofo
# [short end, grip (= the fist), long end]
STANCES = {
    "base": dict(
        file="idle.png", ground=72, dx=30, head=(7, 26, 22, 45), yaw=35,
        rest={
            "head": (33.5, 16.5),
            "spine": [(34.0, 48.0), (34.0, 25.0)],
            "near_arm": [(20.0, 27.0), (17.0, 36.0), (13.0, 44.0), (12.0, 47.0)],
            "far_arm": [(47.0, 27.0), (51.0, 36.0), (54.0, 42.0), (55.0, 46.0)],
            "near_leg": [(27.0, 49.0), (25.0, 57.0), (23.0, 66.0), (21.0, 70.0)],
            "far_leg": [(40.0, 49.0), (42.0, 57.0), (44.0, 66.0), (49.0, 70.0)],
            "near_wpn": [(8.0, 69.0), (12.0, 47.0), (10.0, 1.0)],
            "far_wpn": [(59.0, 69.0), (55.0, 46.0), (54.0, 2.0)],
        }),
    "ao": dict(
        file="ao_idle.png", ground=56, dx=22, head=(0, 21, 35, 61), yaw=15,
        rest={
            "head": (48.0, 10.0),
            "spine": [(44.0, 36.0), (47.0, 18.0)],
            "near_arm": [(31.0, 17.0), (21.0, 24.0), (16.0, 31.0), (14.0, 33.0)],
            "far_arm": [(58.0, 19.0), (63.0, 26.0), (67.0, 32.0), (68.0, 34.0)],
            "near_leg": [(31.0, 37.0), (26.0, 43.0), (25.0, 50.0), (19.0, 54.0)],
            "far_leg": [(54.0, 38.0), (58.0, 44.0), (56.0, 50.0), (63.0, 54.0)],
            "near_wpn": [(15.0, 29.0), (14.0, 33.0), (4.0, 54.0)],
            "far_wpn": [(67.0, 30.0), (68.0, 34.0), (76.0, 55.0)],
        }),
}
for _st in STANCES.values():
    _st["dy"] = SOLE_Y // PX - _st["ground"]

# the poses: name -> (stance, League's frame (clip@ms), what it is for (Chinese), the pose line (English), the skeleton:
# the pelvis (design squares), "lift" (rows the lowest foot is off the ground; None: on it), the spine's direction, each
# limb as (wrist / ankle target, side, last bone's angle) or three angles, each ntofo's long end angle (degrees: 0
# straight down, 90 to the image right, 180 up, -90 to the image left)
POSES = {
    # ---------------------------------------------------------------- the base stance
    "a_back": ("base", "attack1@0", "普攻蓄力：两腿分开站稳，身子微微后仰，近侧手把陀斧往身后拉（陀斧斜着指向左上方），远侧手的陀斧斜着伸向前下方",
               "WIND-UP - standing with the legs apart, leaning back a little, the NEAR arm pulling its ntofo back behind "
               "him (the ntofo slanting up to the image left), the FAR arm's ntofo slanting forward and down.",
               dict(shift=-4, pelvis=(34.0, 48.0), lift=None, spine=-172, near_arm=((16.0, 36.0), 1, -120),
                    far_arm=((56.0, 40.0), 1, 70), near_leg=((20.0, 65.0), -1, -30), far_leg=((48.0, 65.0), -1, 40),
                    near_wpn=-130, far_wpn=60)),
    "a_strike": ("base", "attack1@350", "普攻命中：弓步压低前冲，身子往前倾，两把陀斧一起往前横推到腰前（陀斧水平指向右边）",
                 "STRIKE - a low forward lunge, the body leaning forward, BOTH ntofos thrust forward together, held "
                 "level at waist height pointing to the image right.",
                 dict(shift=-6, pelvis=(34.0, 52.0), lift=None, spine=150, near_arm=((44.0, 45.0), 1, 90),
                      far_arm=((50.0, 43.0), 1, 90), near_leg=((20.0, 66.0), -1, -40), far_leg=((48.0, 66.0), -1, 30),
                      near_wpn=95, far_wpn=88)),
    "q_up": ("base", "spell1_a@120", "Q 起跳：整个人跳离地面（脚离地约 8 格），远侧手高高举起，把陀斧横着举在头顶上方（陀斧水平指向左边），近侧手提着另一把陀斧竖在身旁，两膝收起",
             "LEAP UP - jumping off the ground (the feet about 8 squares up), the FAR arm raised high holding its "
             "ntofo LEVEL above his head (pointing to the image left), the NEAR arm low carrying the other ntofo "
             "upright beside him, both knees drawn up.",
             dict(pelvis=(34.0, 46.0), lift=8, spine=178, near_arm=((14.0, 42.0), 1, -10),
                  far_arm=((42.0, 6.0), 1, 175), near_leg=((26.0, 60.0), -1, 20), far_leg=((42.0, 61.0), -1, 30),
                  near_wpn=180, far_wpn=-95)),
    "q_down": ("base", "spell1_a@400", "Q 砸下：落地蹲低，身子前倾，远侧手的陀斧砸到身前地面（陀斧斜着指向右下，末端着地），近侧手的陀斧举在身后",
               "SLAM - landed in a low crouch leaning forward, the FAR arm's ntofo slammed down in front of him (slanting "
               "down to the image right, its end on the ground), the NEAR arm's ntofo held up behind him.",
               dict(shift=-8, pelvis=(32.0, 54.0), lift=None, spine=145, near_arm=((24.0, 32.0), 1, -165),
                    far_arm=((54.0, 50.0), 1, 70), near_leg=((18.0, 66.0), -1, -40), far_leg=((46.0, 66.0), -1, 30),
                    near_wpn=-165, far_wpn=75)),
    "q2_down": ("base", "spell1_b@400", "Q 第二下砸下：和上一个相反——近侧手的陀斧砸到身前地面，远侧手把另一把陀斧斜着举向右上方（在头的右边，不挡脸）",
                "SLAM 2 - the other side: landed low, the NEAR arm's ntofo slammed down in front of him (its end on the "
                "ground at the image right), the FAR arm holding the other ntofo raised and slanting up to the image "
                "right (to the right of his head, never over the face).",
                dict(pelvis=(32.0, 54.0), lift=None, spine=145, near_arm=((46.0, 52.0), 1, 70),
                     far_arm=((60.0, 32.0), 1, 160), near_leg=((18.0, 66.0), -1, -40), far_leg=((46.0, 66.0), -1, 30),
                     near_wpn=75, far_wpn=150)),
    "q3_up": ("base", "spell1_c@60", "Q 三段起跳：跳离地面（脚离地约 10 格），两只手都高高举起，两把陀斧一上一下横着举在头顶上方（都水平指向左边）",
              "BIG LEAP - jumping high (the feet about 10 squares up), BOTH arms raised high, BOTH ntofos held LEVEL "
              "above his head one over the other (both pointing to the image left).",
              dict(pelvis=(34.0, 44.0), lift=10, spine=178, near_arm=((25.0, 6.0), 1, 175),
                   far_arm=((42.0, 5.0), 1, -175), near_leg=((28.0, 60.0), -1, 10), far_leg=((40.0, 60.0), -1, 20),
                   near_wpn=-98, far_wpn=-90)),
    "q3_slam": ("base", "spell1_c@450", "Q 三段砸地：深蹲，身子压得很低，两把陀斧一起砸在身前地面上（都指向右边，末端着地）",
                "GROUND SLAM - a deep crouch, the body very low, BOTH ntofos slammed together onto the ground in front of "
                "him (both pointing to the image right, their ends on the ground).",
                dict(shift=-7, pelvis=(32.0, 57.0), lift=None, spine=130, near_arm=((46.0, 54.0), 1, 80),
                     far_arm=((52.0, 52.0), 1, 80), near_leg=((16.0, 66.0), -1, -45), far_leg=((44.0, 66.0), -1, 30),
                     near_wpn=82, far_wpn=78)),
    "w_wall": ("base", "spell2_loop@300", "W 蓄力：两把陀斧并在一起斜着顶在身前（往前倾约 30 度），像一面往前推的墙，他在后面用肩膀顶住，近侧腿往后蹬；墙在头的右边，不挡脸",
               "BRACE - BOTH ntofos side by side held before him like a wall LEANING FORWARD about 30 degrees, he "
               "pushes into it from behind with his shoulders, the near leg braced back; the wall stays to the right "
               "of his face.",
               dict(pelvis=(32.0, 50.0), lift=None, spine=170, near_arm=((42.0, 36.0), 1, 150),
                    far_arm=((48.0, 38.0), 1, 150), near_leg=((16.0, 66.0), -1, -45), far_leg=((40.0, 66.0), -1, 20),
                    near_wpn=150, far_wpn=148)),
    "w_dash": ("base", "spell2_dash@200", "W 冲撞：和蓄力一样把两把陀斧并成墙顶在身前，墙往前倾得更多（约 40 度），身子更往前倾、迈开大步往前冲；墙在头的右边，不挡脸",
               "RAM - the same wall of both ntofos held before him, leaning further forward (about 40 degrees), "
               "charging with a long stride (the near leg far back, the far leg forward); the wall stays to the right "
               "of his face.",
               dict(pelvis=(32.0, 49.0), lift=None, spine=158, near_arm=((44.0, 38.0), 1, 142),
                    far_arm=((50.0, 40.0), 1, 142), near_leg=((12.0, 63.0), -1, -60), far_leg=((44.0, 66.0), -1, 20),
                    near_wpn=142, far_wpn=140)),
    "r_bash": ("base", "spell4_a@1000", "R 盾击：整个人压低往前猛冲，身子几乎平着，两把陀斧一起往前平推出去（指向右边）",
               "SHIELD BASH - lunging forward very low, the body almost level, BOTH ntofos shoved forward together "
               "(level, pointing to the image right), the near leg stretched far back.",
               dict(shift=-12, pelvis=(28.0, 56.0), lift=None, spine=125, near_arm=((48.0, 58.0), 1, 90),
                    far_arm=((54.0, 56.0), 1, 90), near_leg=((8.0, 66.0), -1, -70), far_leg=((40.0, 66.0), -1, 30),
                    near_wpn=92, far_wpn=88)),
    "r_fly": ("base", "spell4_dash@300", "R 飞扑：整个人平着往前扑在空中（离地约 8 格），远侧手的陀斧伸向前方，近侧手的陀斧扬在身后上方，两腿拖在后面",
              "DIVE - flying forward level through the air (about 8 squares off the ground), the FAR arm's ntofo "
              "reaching forward, the NEAR arm's ntofo swung up behind him, both legs trailing behind.",
              dict(shift=-12, pelvis=(26.0, 52.0), lift=8, spine=100, near_arm=((30.0, 38.0), 1, -150),
                   far_arm=((56.0, 50.0), 1, 90), near_leg=((10.0, 56.0), -1, -80), far_leg=((12.0, 60.0), -1, -80),
                   near_wpn=-140, far_wpn=95)),
    "d_slump": ("base", "death@0", "倒下 1：身子往前栽、弯下腰，头垂下，两只手垂到膝盖前，近侧的陀斧往左上方歪倒，远侧的陀斧往右下方倒向地面",
                "SLUMP - pitching forward, bent at the waist, the head dropping, both hands sagging down before his "
                "knees, the near ntofo toppling over to the image left (leaning up-left), the far ntofo falling "
                "forward and down to the ground at the image right.",
                dict(pelvis=(34.0, 51.0), lift=None, spine=140, near_arm=((26.0, 50.0), 1, -10),
                     far_arm=((48.0, 50.0), 1, 10), near_leg=((24.0, 66.0), -1, -10), far_leg=((44.0, 66.0), -1, 30),
                     near_wpn=-130, far_wpn=68)),
    "d_kneel": ("base", "death@2000", "倒下 2：单膝跪地（近侧膝盖着地），身子往前塌，两只空手往前垂，两把陀斧已经脱手、平躺在地上（一把在身后、一把在身前）",
                "KNEEL - down on one knee (the near knee on the ground), slumped forward, both empty hands hanging "
                "forward; the two ntofos have dropped and lie FLAT on the ground (one behind him, one in front).",
                dict(pelvis=(34.0, 58.0), lift=None, spine=150, near_arm=((42.0, 60.0), 1, 30),
                     far_arm=((48.0, 58.0), 1, 30), near_leg=((24.0, 68.0), -1, -90), far_leg=((44.0, 66.0), -1, 30),
                     near_wpn=-90, far_wpn=90, near_drop=(28.0, 69.0), far_drop=(42.0, 68.0))),
    "run1": ("base", "run1@0", "跑步 1（近侧腿在前着地）：身子微微前倾，两把陀斧竖着提在身体两侧，远侧手往前摆、近侧手往后摆",
             "RUN 1 - running leaning a little forward, both ntofos carried upright at his sides: the NEAR leg forward "
             "landing, the far leg pushing off behind, the far arm swinging forward, the near arm swinging back.",
             dict(pelvis=(34.0, 48.0), lift=None, spine=168, near_arm=((14.0, 42.0), 1, -10),
                  far_arm=((58.0, 38.0), 1, 30), near_leg=((44.0, 65.0), -1, 30), far_leg=((22.0, 63.0), -1, -60),
                  near_wpn=-172, far_wpn=170)),
    "run2": ("base", "run1@267", "跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，陀斧竖在两侧",
             "RUN 2 - running: the near leg under the body carrying him, the far knee lifted forward, the body one "
             "square higher, both ntofos upright at his sides.",
             dict(pelvis=(34.0, 47.0), lift=None, spine=168, near_arm=((14.0, 44.0), 1, 0),
                  far_arm=((55.0, 41.0), 1, 10), near_leg=((32.0, 66.0), -1, 0), far_leg=((46.0, 58.0), -1, 40),
                  near_wpn=180, far_wpn=-178)),
    "run3": ("base", "run1@533", "跑步 3（远侧腿在前着地）：近侧手往前摆、远侧手往后摆，陀斧竖在两侧，不挡脸",
             "RUN 3 - running: the FAR leg forward landing, the near leg pushing off behind, the near arm swinging "
             "forward (its ntofo upright, never over the face), the far arm swinging back.",
             dict(pelvis=(34.0, 48.0), lift=None, spine=168, near_arm=((22.0, 42.0), 1, 30),
                  far_arm=((56.0, 44.0), 1, -10), near_leg=((20.0, 63.0), -1, -60), far_leg=((48.0, 65.0), -1, 35),
                  near_wpn=-176, far_wpn=-172)),
    "run4": ("base", "run1@800", "跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，陀斧竖在两侧",
             "RUN 4 - running: the far leg under the body carrying him, the near knee lifted forward, the body one "
             "square higher, both ntofos upright at his sides.",
             dict(pelvis=(34.0, 47.0), lift=None, spine=168, near_arm=((14.0, 44.0), 1, 0),
                  far_arm=((55.0, 44.0), 1, 10), near_leg=((38.0, 58.0), -1, 40), far_leg=((38.0, 66.0), -1, 10),
                  near_wpn=180, far_wpn=-178)),
    # ---------------------------------------------------------------- All Out
    "ao_swing_back": ("ao", "attack1_allout@200", "全盛普攻蓄力：身子稍微直起来，近侧手把长棍高高抡到身后上方（指向左上），远侧手的长棍垂向右下方",
                      "ALL OUT WIND-UP - rising a little out of the crouch, the NEAR arm swinging its club high up "
                      "behind him (pointing up to the image left), the FAR arm's club hanging down to the image right.",
                      dict(pelvis=(44.0, 35.0), lift=None, spine=175, near_arm=((34.0, 4.0), 1, -160),
                           far_arm=((66.0, 34.0), 1, 20), near_leg=((24.0, 50.0), -1, -30), far_leg=((58.0, 50.0), -1, 30),
                           near_wpn=-150, far_wpn=25)),
    "ao_swing": ("ao", "attack1_allout@450", "全盛普攻横扫：蹲低，两只手把两根长棍往左右两边横着甩开（近侧指向左、远侧指向右，几乎水平）",
                 "ALL OUT SWEEP - crouched low, both arms swinging both clubs out wide to the sides (the near one to "
                 "the image left, the far one to the image right, almost level).",
                 dict(pelvis=(44.0, 37.0), lift=None, spine=168, near_arm=((16.0, 24.0), 1, -100),
                      far_arm=((74.0, 24.0), 1, 100), near_leg=((22.0, 50.0), -1, -35), far_leg=((60.0, 50.0), -1, 35),
                      near_wpn=-105, far_wpn=105)),
    "ao_leap": ("ao", "spell1_a_allout@200", "全盛跳起：整个人跳离地面（脚离地约 10 格），两膝收起，远侧手举起长棍横在头顶上方（指向左边），近侧手的长棍横在腰前（指向右边）",
                "ALL OUT LEAP - jumping off the ground (the feet about 10 squares up), the knees drawn up, the FAR arm "
                "raised holding its club level over his head (pointing to the image left), the NEAR arm's club held "
                "level before his waist (pointing to the image right).",
                dict(pelvis=(44.0, 34.0), lift=10, spine=176, near_arm=((26.0, 28.0), 1, 60),
                     far_arm=((54.0, 0.0), 1, 175), near_leg=((36.0, 46.0), -1, 20), far_leg=((52.0, 47.0), -1, 30),
                     near_wpn=95, far_wpn=-95)),
    "ao_smash": ("ao", "spell1_a_allout@600", "全盛砸地：落地蹲低，远侧手的长棍砸到身前地面（几乎水平指向右边，棍头着地），近侧手的长棍举在头顶后上方（指向左上）",
                 "ALL OUT SMASH - landed low, the FAR arm's club slammed down in front of him (almost level, pointing "
                 "to the image right, its head on the ground), the NEAR arm's club raised up behind his head "
                 "(pointing up to the image left).",
                 dict(pelvis=(42.0, 40.0), lift=None, spine=150, near_arm=((34.0, 6.0), 1, -150),
                      far_arm=((66.0, 42.0), 1, 80), near_leg=((22.0, 50.0), -1, -40), far_leg=((56.0, 50.0), -1, 30),
                      near_wpn=-135, far_wpn=82)),
    "ao_cross": ("ao", "spell2_enter_allout@300", "全盛 W 蓄力：直起身子，两根长棍在头顶交叉成 X 字（近侧指向右上、远侧指向左上）",
                 "ALL OUT BRACE - standing up tall, both clubs crossed in an X over his head (the near one pointing up "
                 "to the image right, the far one up to the image left).",
                 dict(pelvis=(44.0, 30.0), lift=None, spine=180, near_arm=((33.0, -2.0), 1, 170),
                      far_arm=((58.0, -2.0), 1, -170), near_leg=((30.0, 50.0), -1, -20), far_leg=((56.0, 50.0), -1, 20),
                      near_wpn=150, far_wpn=-150)),
    "ao_charge": ("ao", "spell2_dash_allout@150", "全盛 W 冲撞：压低身子往前冲，身子前倾，两根长棍斜着伸向前下方，近侧腿往后蹬",
                  "ALL OUT CHARGE - charging forward low, the body leaning forward, both clubs reaching forward and "
                  "down, the near leg pushing off far behind.",
                  dict(pelvis=(42.0, 38.0), lift=None, spine=140, near_arm=((56.0, 34.0), 1, 60),
                       far_arm=((64.0, 32.0), 1, 60), near_leg=((16.0, 48.0), -1, -60), far_leg=((56.0, 50.0), -1, 30),
                       near_wpn=60, far_wpn=55)),
    "ao_run1": ("ao", "run_allout@0", "全盛跑步 1（近侧腿在前着地）：弓着背往前冲，两根长棍拖在身体两侧，棍头贴近地面",
                "ALL OUT RUN 1 - running hunched forward, both clubs trailing at his sides with their heads near the "
                "ground: the NEAR leg forward landing, the far leg pushing off behind.",
                dict(pelvis=(44.0, 36.0), lift=None, spine=165, near_arm=((16.0, 32.0), 1, -20),
                     far_arm=((68.0, 32.0), 1, 20), near_leg=((52.0, 50.0), -1, 30), far_leg=((30.0, 48.0), -1, -60),
                     near_wpn=-40, far_wpn=40)),
    "ao_run2": ("ao", "run_allout@267", "全盛跑步 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，长棍拖在两侧",
                "ALL OUT RUN 2 - running hunched: the near leg under the body carrying him, the far knee lifted "
                "forward, the body one square higher, both clubs trailing at his sides.",
                dict(pelvis=(44.0, 35.0), lift=None, spine=165, near_arm=((18.0, 31.0), 1, -20),
                     far_arm=((66.0, 31.0), 1, 20), near_leg=((40.0, 50.0), -1, 0), far_leg=((56.0, 42.0), -1, 40),
                     near_wpn=-25, far_wpn=22)),
    "ao_run3": ("ao", "run_allout@533", "全盛跑步 3（远侧腿在前着地）：弓着背往前冲，长棍拖在两侧",
                "ALL OUT RUN 3 - running hunched forward: the FAR leg forward landing, the near leg pushing off behind, "
                "both clubs trailing at his sides.",
                dict(pelvis=(44.0, 36.0), lift=None, spine=165, near_arm=((16.0, 32.0), 1, -20),
                     far_arm=((68.0, 32.0), 1, 20), near_leg=((26.0, 48.0), -1, -60), far_leg=((60.0, 50.0), -1, 35),
                     near_wpn=-30, far_wpn=25)),
    "ao_run4": ("ao", "run_allout@800", "全盛跑步 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，长棍拖在两侧",
                "ALL OUT RUN 4 - running hunched: the far leg under the body carrying him, the near knee lifted forward, "
                "the body one square higher, both clubs trailing at his sides.",
                dict(pelvis=(44.0, 35.0), lift=None, spine=165, near_arm=((18.0, 31.0), 1, -20),
                     far_arm=((66.0, 31.0), 1, 20), near_leg=((44.0, 42.0), -1, 40), far_leg=((48.0, 50.0), -1, 10),
                     near_wpn=-25, far_wpn=22)),
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


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def lengths(rest, name):
    pts = rest[name]
    return [dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]


def bend(H, A, l1, l2, side):
    """The middle joint of a two-bone limb from H towards A (A pulled in or pushed out to what the bones reach), bulging
    to `side` (rig_zyra.knee's `forward`)."""
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


def build(stance, spec):
    """A skeleton from a pose spec on its stance's REST: the bones at the design's own lengths; the shoulders turned with
    the spine, the hips half as much; the head box upright over the neck (pasted, never turned); each limb either three
    angles or (target, side, last angle) solved at the design's lengths; each ntofo a rigid bone through the fist at
    its long end's angle (or, dropped, lying with its grip at `<side>_drop`). The lowest foot or knee on the ground, or
    `lift` rows over it."""
    rest = STANCES[stance]["rest"]
    rs = rest["spine"]
    turn = (spec["spine"] - ang(rs[0], rs[1]) + 180.0) % 360.0 - 180.0
    pel = spec["pelvis"]
    neck = along(pel, spec["spine"], lengths(rest, "spine")[0])
    sk = {"spine": [pel, neck], "head": (neck[0] + rest["head"][0] - rs[1][0], neck[1] + rest["head"][1] - rs[1][1])}
    for name, base, base_rest, k in (("near_arm", neck, rs[1], 1.0), ("far_arm", neck, rs[1], 1.0),
                                     ("near_leg", pel, rs[0], 0.5), ("far_leg", pel, rs[0], 0.5)):
        off = turned((rest[name][0][0] - base_rest[0], rest[name][0][1] - base_rest[1]), turn * k)
        pts = [(base[0] + off[0], base[1] + off[1])]
        ls = lengths(rest, name)
        sp = spec[name]
        if len(sp) == 3 and isinstance(sp[0], tuple):
            target, side, last = sp
            M, A = bend(pts[0], target, ls[0], ls[1], side)
            pts += [M, A, along(A, last, ls[2])]
        else:
            for a_, l_ in zip(sp, ls):
                pts.append(along(pts[-1], a_, l_))
        sk[name] = pts
    for side in ("near", "far"):
        short_end, grip, long_end = rest[f"{side}_wpn"]
        g = spec.get(f"{side}_drop") or sk[f"{side}_arm"][-1]   # a dropped ntofo lies where the pose puts it
        deg = spec[f"{side}_wpn"]
        sk[f"{side}_wpn"] = [along(g, deg + 180, dist(grip, short_end)), g, along(g, deg, dist(grip, long_end))]
    low = max(y for leg in ("near_leg", "far_leg") for _, y in sk[leg])
    dy = rest["near_leg"][-1][1] - (spec["lift"] or 0) - low
    return {k: ((v[0], v[1] + dy) if k == "head" else [(x, y + dy) for x, y in v]) for k, v in sk.items()}


def to_canvas(stance, sk, shift=0.0):
    """Design squares -> canvas squares; `shift` moves a pose sideways (an ntofo thrust forward would leave the canvas)."""
    dx, dy = STANCES[stance]["dx"] + shift, STANCES[stance]["dy"]
    return {k: ((v[0] + dx, v[1] + dy) if k == "head" else [(x + dx, y + dy) for x, y in v]) for k, v in sk.items()}


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


def skeleton(can, stance, s, label, alpha=255):
    """The skeleton drawn on a clear layer laid over `can` (a translucent head box shows the design's head under it)."""
    r0, r1, c0, c1 = STANCES[stance]["head"]
    hw, hh = c1 - c0, r1 - r0
    lay = Image.new("RGBA", can.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay, "RGBA")
    hx, hy = s["head"]
    box = [(hx - hw / 2) * PX, (hy - hh / 2) * PX, (hx + hw / 2) * PX, (hy + hh / 2) * PX]
    dr.rectangle(box, fill=(150, 150, 150, 70 if alpha < 255 else 120), outline=(90, 90, 90, alpha), width=3)
    order = [("far_wpn", 16), ("far_leg", 7), ("far_arm", 7), ("spine", 7), ("near_leg", 7), ("near_wpn", 16),
             ("near_arm", 7)]
    for name, w in order:
        pts = [c(p) for p in s[name]]
        dr.line(pts, fill=COL[name] + (alpha,), width=w, joint="curve")
        for p in pts:
            r = 6
            dr.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=COL[name] + (alpha,))
        if name.endswith("_wpn"):
            e = pts[-1]
            dr.ellipse([e[0] - 14, e[1] - 14, e[0] + 14, e[1] + 14], outline=COL[name] + (alpha,), width=5)
    dr.text((12, 12), label, fill=(30, 30, 30, 255))
    can.alpha_composite(lay)
    return can


def on_grid(d, dx, dy):
    lay = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    lay.paste(Image.fromarray(up(d, PX)), (dx * PX, dy * PX))
    return lay


def lol_frame(lol, frame, yaw, work):
    os.makedirs(work, exist_ok=True)
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "KSante",
           "--hq", "--mirror", "--bg", ",".join(map(str, GREY)), "--no-labels", "--size", "900", "--fit", "0.3",
           "--ground", "0.85", "--width", "2.0", "--yaw", str(yaw), "--name", "f", "--out", work, "--frame", frame,
           *PARTS_LOL]
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


def design(stance):
    return np.asarray(Image.open(lp(os.path.join(SRC, "hd", STANCES[stance]["file"]))).convert("RGBA"))


def poses_built():
    return {name: (st, to_canvas(st, build(st, spec), spec.get("shift", 0.0)), frame, zh, en)
            for name, (st, frame, zh, en, spec) in POSES.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ks_work/ksante_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    ap.add_argument("--check")
    ap.add_argument("--only", help="comma-separated pose names (with --check)")
    a = ap.parse_args()
    poses = poses_built()
    if a.check:
        os.makedirs(a.check, exist_ok=True)
        for st, cfg in STANCES.items():
            base = canvas_grid()
            base.alpha_composite(on_grid(design(st), cfg["dx"], cfg["dy"]))
            skeleton(base, st, to_canvas(st, cfg["rest"]), f"{st}: the design's own skeleton (REST)", 200)
            base.convert("RGB").save(os.path.join(a.check, f"rest_check_{st}.png"))
        only = set(a.only.split(",")) if a.only else None
        tiles = []
        for name, (st, s, frame, zh, en) in poses.items():
            if only and name not in only:
                continue
            can = canvas_grid()
            skeleton(can, st, s, name)
            lf = lol_frame(a.lol, frame, STANCES[st]["yaw"], os.path.join(a.check, "_work"))
            pts = [p for k, v in s.items() if k != "head" for p in v] + [s["head"]]
            x0 = max(0, int(min(p[0] for p in pts) - 14) * PX)
            x1 = min(CANVAS, int(max(p[0] for p in pts) + 14) * PX)
            y0 = max(0, int(min(p[1] for p in pts) - 14) * PX)
            sk = can.convert("RGB").crop((x0, y0, x1, SOLE_Y + 20))
            sk = sk.resize((round(sk.width * 480 / sk.height), 480))
            lf = lf.resize((round(lf.width * sk.height / lf.height), sk.height))
            t = Image.new("RGB", (sk.width + lf.width, sk.height), (255, 255, 255))
            t.paste(sk, (0, 0))
            t.paste(lf, (sk.width, 0))
            tiles.append(t)
        W = max(t.width for t in tiles)
        cols = 3
        rows_ = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (W * cols, tiles[0].height * rows_), (255, 255, 255))
        for k, t in enumerate(tiles):
            sheet.paste(t, ((k % cols) * W, (k // cols) * t.height))
        sheet.save(os.path.join(a.check, "poses_check.png"))
        shutil.rmtree(os.path.join(a.check, "_work"), ignore_errors=True)
        return
    out = a.out
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)
    for st, cfg in STANCES.items():
        d = design(st)
        base = canvas_grid()
        base.alpha_composite(on_grid(d, cfg["dx"], cfg["dy"]))
        clean = base.copy()
        skeleton(base, st, to_canvas(st, cfg["rest"]),
                 f"0: the approved {st} design with its own skeleton (what each coloured line stands for)", 200)
        base.convert("RGB").save(os.path.join(out, f"0_design_skeleton_{st}.png"))
        clean.convert("RGB").save(os.path.join(out, f"2_design_{st}.png"))
        r0, r1, c0, c1 = cfg["head"]
        big(d[r0:r1, c0:c1]).save(os.path.join(out, f"1_head_{st}.png"))
    for k, (name, (st, s, frame, zh, en)) in enumerate(poses.items(), 3):
        can = canvas_grid()
        skeleton(can, st, s, f"{k}: {name} ({st}) - skeleton on the {PX} px grid, red line = the ground (soles on y {SOLE_Y})")
        can.convert("RGB").save(os.path.join(out, f"{k}_{name}_skeleton.png"))
        lol_frame(a.lol, frame, STANCES[st]["yaw"], out + "_work").save(os.path.join(out, f"{k}_{name}_league.png"))
        print(k, name, frame)
    shutil.rmtree(out + "_work", ignore_errors=True)
    shutil.copyfile(lp(os.path.join(SRC, "POSE_PROMPTS.md")), os.path.join(out, "POSE_PROMPTS.md"))
    zp = shutil.make_archive(out, "zip", out)
    print(zp)


if __name__ == "__main__":
    main()
