#!/usr/bin/env python3
"""Udyr's pose pack for Codex (assets/source/udyr/POSE_PROMPTS.md): the key poses of League's clips, drawn on the four
approved stance designs (the user, 2026-10-22: the first rig, made by moving the designs' own parts, 「好多地方都很奇怪」
「我看到了很多手臂变形的地方」 - then picked 「Codex 照骨架画姿势」; the Naafiri / Shyvana way).

    python tools/art/pack_udyr_poses.py [--out C:/t/ud_work/udyr_pose_pack] [--lol D:/WeGameApps/lol]

Each pose's guide is League's own frame (pose_ref.py --frame, 3/4 facing right: yaw 30, the stance's own spirit meshes
only) brought to the design's size: one factor per stance, from League's idle height to the design's rows, and widened
by the design's own bulk against League's (our designs are squat and broad: WIDEN = the idle's width-to-height against
League's idle's), so the guide's shape is close to what Codex should draw. Feet on the red ground line unless League's
frame lifts them (the jumps keep League's height above the ground).
Every pose is ONE 1254 picture on the stance design's squares: the plain guard 18 px (60 rows), the bear and the ram 15 px
(61 / 69 rows), the phoenix 13 px (73 rows) - the step-1 sizes.
Writes <out>/ (and <out>.zip): POSE_PROMPTS.md; 0_design_<stance>.png (each design on its grid, where it stands);
1_head_<stance>.png (the heads, 8x: every pose wears its stance's head); per pose <k>_<name>_guide.png (League's frame on
the grid at the size to draw, the ground red) and <k>_<name>_league.png (the frame large: Riot's, kept local).
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pack_udyr_picture as PK  # noqa: E402
from design_udyr_model import lp  # noqa: E402
from pack_gangplank_model import up  # noqa: E402

SRC = os.path.join(ROOT, "assets", "source", "udyr")
CANVAS = 1254
GREY = (225, 225, 225)
SIZE, WIDTH, FIT, GROUND = 1000, 1.6, 0.45, 0.8      # the render cell (the idle's soles are the ground)
YAW, HEAD, LEGS = 30, 1.4, 0.85
# stance -> (League's idle frame, design, rows, px a square, the ground's y, the head box in the design (rows, columns,
# ends exclusive), the stance's name in the prompts)
STANCES = {"A": ("spell2_idle@0", "idle.png", 60, 18, 1188, (0, 27, 16, 38), "the plain guard"),
           "Q": ("spell1_idle@0", "q_idle.png", 61, 15, 1185, (9, 36, 32, 52), "the BEAR stance"),
           "E": ("spell3_idle@0", "e_idle.png", 69, 15, 1185, (17, 42, 37, 56), "the RAM stance"),
           "R": ("spell4_idle@0", "r_idle.png", 73, 13, 1183, (21, 46, 54, 73), "the PHOENIX stance")}
# the poses in order: name -> (stance, League's frame, what it is for (Chinese), the pose line (English))
POSES = {
    "a_punch": ("A", "spell2_attack@0",
                "出拳：远侧（画面右边）的拳头往前（右）直直打出去，手臂几乎伸直、和肩膀一样高，身子跟着往前转一点；近侧的拳头还举在脸旁边护着（普攻命中）",
                "PUNCH - the FAR fist (image right) driven straight forward to the right at shoulder height, the arm "
                "nearly straight, the body turned a little into the blow; the NEAR fist stays up beside his face as a "
                "guard (not over the face)."),
    "run1": ("A", "spell2_run@0", "跑步 1：近侧（左）腿往前迈、脚跟着地，远侧腿在后面蹬地；两只拳头仍举在胸前护着",
             "RUN 1 - the NEAR leg (image left) stepping forward with its heel down, the FAR leg behind pushing off; "
             "both fists still up before his chest in the guard."),
    "run2": ("A", "spell2_run@235", "跑步 2：两腿交错、近侧腿在身下撑地，远侧腿抬起往前收（膝盖抬高）；拳头护着",
             "RUN 2 - passing: the near leg under him on the ground, the far leg lifted and swinging forward (its knee "
             "raised); the fists up in the guard."),
    "run3": ("A", "spell2_run@470", "跑步 3：远侧（右）腿往前迈、脚跟着地，近侧腿在后面蹬地；拳头护着",
             "RUN 3 - the FAR leg (image right) stepping forward with its heel down, the NEAR leg behind pushing off; "
             "the fists up in the guard."),
    "run4": ("A", "spell2_run@706", "跑步 4：两腿交错、远侧腿在身下撑地，近侧腿抬起往前收；拳头护着",
             "RUN 4 - passing: the far leg under him on the ground, the near leg lifted and swinging forward (its knee "
             "raised); the fists up in the guard."),
    "d_hit": ("A", "death@333", "中招后仰：被打得往后仰，胸口挺出、头往后甩，两臂往后甩开，两腿还站着（阵亡第一下）",
              "STRUCK - thrown back by the killing blow: the chest pushed out, the head thrown back, both arms flung "
              "out behind him, still on his feet (the death's first moment)."),
    "d_kneel": ("A", "death@1333", "跪倒：两膝跪在地上，上身往前垂、头低下（看得见脸的上半部分），两只拳头撑在膝前的地上（阵亡）",
                "KNEEL - fallen to both knees on the ground, the upper body slumped forward, the head bowed (the brows "
                "and eyes still visible), both fists resting on the ground before his knees (death)."),
    "q_wind": ("Q", "spell1_attack1@367", "熊爪蓄力：两只爪子张开甩到身后两边，身子微微往后仰，熊头护臂在远侧手臂上（熊姿态普攻的起手）",
               "CLAWS BACK - both clawed paws flung out wide to the sides and back, the body rocked back a little, the "
               "bear's head still over the far fist (the bear's swipe winding up)."),
    "q_swipe": ("Q", "spell1_attack1@105", "熊爪横扫：两只爪子从身后往前一起扫到身前（远侧爪子在前、往前下方抓），身子往前扑、压低（熊姿态普攻命中）",
                "SWIPE - both clawed paws raked from behind to in front of him, the far paw (with the bear's head) "
                "clawing forward and down, the body lunging forward and low (the bear's swipe landing)."),
    "q_roar": ("Q", "spell1_activate@84", "熊之怒吼：整个人直立起来、挺胸，两只爪子高高举过头顶，熊皮在背后（Q 狂暴爪击的施放）",
               "ROAR - risen upright to his full height, the chest out, both clawed paws raised high over his head, "
               "the bear hide hanging down his back (casting Wilding Claw)."),
    "q_run1": ("Q", "spell1_run@0", "熊跑 1：近侧腿往前迈，身子弓着往前冲，两只爪子垂在身前摆动",
               "BEAR RUN 1 - the near leg stepping forward, the body hunched and charging forward, both paws hanging "
               "low before him."),
    "q_run2": ("Q", "spell1_run@267", "熊跑 2：两腿交错、远侧腿抬起往前收，两只爪子往后摆",
               "BEAR RUN 2 - passing, the far leg lifted and swinging forward, both paws swinging back."),
    "q_run3": ("Q", "spell1_run@534", "熊跑 3：远侧腿往前迈，近侧腿在后面蹬，两只爪子往前摆",
               "BEAR RUN 3 - the far leg stepping forward, the near leg pushing off behind, both paws swinging forward."),
    "q_run4": ("Q", "spell1_run@800", "熊跑 4：两腿交错、近侧腿抬起往前收，两只爪子往后摆",
               "BEAR RUN 4 - passing, the near leg lifted and swinging forward, both paws swinging back."),
    "e_hook": ("E", "spell3_attack1@340", "公羊冲拳：往前大步弓步，身子往前探，远侧的拳头往前上方勾出去，头低着、两只羊角朝前（公羊姿态普攻命中）",
               "HOOK - a long lunge forward, the body thrust ahead, the FAR fist hooking forward and up at the target, "
               "the head down with both great horns pointing forward (the ram's punch landing)."),
    "e_leap": ("E", "spell3_enhanced_attack@175", "跃起：整个人跳离地面，两腿收起，两只拳头举过头，头低着准备往下撞（晕眩那一击的起跳）",
               "LEAP - sprung up off the ground, the legs tucked under him, both fists raised over his head, the head "
               "lowered to ram down (the stunning blow taking off)."),
    "e_slam": ("E", "spell3_enhanced_attack@467", "砸下：落地蹲得很低，头和羊角往前下方撞下去，两只拳头砸在地上（晕眩那一击命中）",
               "SLAM - landed in a deep crouch, the head and the horns driven forward and down, both fists smashed on "
               "the ground (the stunning blow landing)."),
    "e_stomp": ("E", "spell3@0", "跺脚：近侧的膝盖抬高准备往下跺，头往后一甩，两只拳头握在身前（E 踏火蛮冲的施放）",
                "STAMP - the near knee raised high to stamp down, the head tossed back, both fists clenched before "
                "him (casting Blazing Stampede)."),
    "e_run1": ("E", "spell3_run@0", "冲锋 1：近侧腿往前大步迈，身子前倾、头低着用羊角对着前面，两只拳头摆动",
               "CHARGE 1 - the near leg striding far forward, the body leaning ahead, the head down with the horns "
               "aimed forward, the fists pumping."),
    "e_run2": ("E", "spell3_run@267", "冲锋 2：两腿交错、远侧腿抬起往前收，身子前倾",
               "CHARGE 2 - passing, the far leg lifted and swinging forward, the body leaning ahead."),
    "e_run3": ("E", "spell3_run@534", "冲锋 3：远侧腿往前大步迈，近侧腿在后面蹬，头低着",
               "CHARGE 3 - the far leg striding forward, the near leg pushing off behind, the head down."),
    "e_run4": ("E", "spell3_run@800", "冲锋 4：两腿交错、近侧腿抬起往前收，身子前倾",
               "CHARGE 4 - passing, the near leg lifted and swinging forward, the body leaning ahead."),
    "r_thrust": ("R", "spell4_attack1@367", "凤凰掌击：往前弓步，远侧手臂带着羽刃往前直推出去，近侧手臂往后伸，像展翅一扫（凤凰姿态普攻命中）",
                 "WING THRUST - a lunge forward, the FAR arm with its feather blades thrust straight out ahead, the "
                 "near arm stretched back behind him, like a wing sweeping forward (the phoenix's strike landing)."),
    "r_crouch": ("R", "spell4@150", "蓄势：蹲低，两臂带着羽刃往后下方收，像收拢翅膀（R 极凌飓风的起手）",
                 "GATHER - crouched low, both arms with their feather blades swept back and down like folded wings "
                 "(Wingborne Storm winding up)."),
    "r_flap": ("R", "spell4@300", "振翅腾空：整个人跳到空中，两臂带着羽刃高高举起张开，像凤凰展翅，头发往上飘（R 极凌飓风的施放）",
               "TAKE WING - leapt into the air, both arms with their feather blades raised high and spread like a "
               "phoenix's wings, the hair streaming up (casting Wingborne Storm)."),
    "r_run1": ("R", "spell4_run@0", "凤凰跑 1：近侧腿往前迈，两臂带着羽刃往后张开，像滑翔的翅膀",
               "PHOENIX RUN 1 - the near leg stepping forward, both arms with their blades spread back like gliding "
               "wings."),
    "r_run2": ("R", "spell4_run@267", "凤凰跑 2：两腿交错、远侧腿抬起往前收，两臂往后张开",
               "PHOENIX RUN 2 - passing, the far leg lifted and swinging forward, the arms spread back."),
    "r_run3": ("R", "spell4_run@534", "凤凰跑 3：远侧腿往前迈，近侧腿在后面蹬，两臂往后张开",
               "PHOENIX RUN 3 - the far leg stepping forward, the near leg pushing off behind, the arms spread back."),
    "r_run4": ("R", "spell4_run@800", "凤凰跑 4：两腿交错、近侧腿抬起往前收，两臂往后张开",
               "PHOENIX RUN 4 - passing, the near leg lifted and swinging forward, the arms spread back."),
}
# poses whose lowest point keeps League's height above the ground (None) - the rest stand on it
LIFT = {"e_leap": None, "r_flap": None}
PX, GROUND_Y = {}, {}           # each pose's square size and ground row (filled by main())


LOOK = {
    "A": "his PLAIN GUARD design (image 0A): the burly bare-chested monk with dark red tattoos, long dark dreadlocks, a "
         "thick beard, one bright blue feather braid by his face, white-bandaged fists with orange bracers, a belt of "
         "big orange-red beads with a teal stone plaque and two orange ropes, baggy dark brown trousers, teal stone knee "
         "guards over grey-blue fur, dark teal leg wraps and sandals",
    "Q": "his BEAR stance design (image 0Q): the same monk with a brown BEAR HIDE draped over his back and the BEAR'S "
         "HEAD (ears, long snout, teeth) over his far fist like a gauntlet, both hands clawed",
    "E": "his RAM stance design (image 0E): the same monk with two huge curled RAM HORNS (tan-brown with dark rings and a "
         "white-grey wrapping) growing from his shoulders and back over his head",
    "R": "his PHOENIX stance design (image 0R): the same monk with rows of dark blue FEATHER BLADES with orange-red roots "
         "along both arms and his back, his dreadlocks swept up",
}
ZH = {"A": "平常护头的造型", "Q": "熊姿态的造型", "E": "公羊姿态的造型", "R": "凤凰姿态的造型"}


def document():
    L = []
    a = L.append
    a("# 兽灵行者 乌迪尔：动作关键姿势（给 Codex 的提示词）\n")
    a("> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
    a(f"> - 乌迪尔四个姿态的造型用户已经定了（`0_design_A.png` 平常、`0_design_Q.png` 熊、`0_design_E.png` 公羊、`0_design_R.png` "
      f"凤凰，就是你上一步画的 A-1 / Q-1 / E-1 / R-1 缩到游戏格子数）。这一步照**英雄联盟的动作**画 **{len(POSES)} 个关键姿势**，"
      "Claude 再用它们拼成动作帧。")
    a("> - 每个姿势附一张**参考图**（`<编号>_<名字>_guide.png`）：英雄联盟里那一帧，按我们的大小放在画布上，格子和地面线（红线）都画好了。"
      "**姿势、位置、大小照参考图**；**样子、颜色、格子、身材照造型**（参考图是 3D 渲染、身材比我们的瘦，不要照它的光影和细节，"
      "**要画得和造型一样壮、一样宽**）。")
    a("> - **一张图只画一个乌迪尔**，用这个姿势所属姿态的造型（编号后面写着 A / Q / E / R）。每格多少像素写在每个姿势里（大多和造型一样，"
      "几个特别高或特别宽的姿势格子小一点，好放进画布）。画布 **1254 × 1254**，网格从左上角 (0, 0) 对齐。")
    a("> - **头和脸照造型**（`1_head_*.png` 是四个头放大 8 倍）：两只冷蓝色的眼睛、浓眉、深色络腮胡、脸左边的蓝羽毛发辫、脏辫。"
      "头可以低、可以抬，但**脸的画法和颜色不变**，**不要比造型的头大或小**；**手臂、爪子、拳头、羊角、羽刃都不要挡住脸**。")
    a("> - **手臂和腿不能变形**：每条手臂、每条腿的粗细、长短和造型一样，关节往正确的方向弯（肘往后、膝盖往前），近处的腿全亮、"
      "远处的暗一档，两条腿分得开；**身子不要压扁到腿上**；兽灵部件（熊皮熊头、羊角、羽刃）的形状、颜色和造型一样，跟着手臂、身子动。\n")
    a("## 附图（压缩包 `udyr_pose_pack.zip` 里）\n")
    a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
    a("| 文件 | 内容 |")
    a("|---|---|")
    a("| `0_design_A.png` / `_Q` / `_E` / `_R` | 四个造型（用户定的），在网格上，脚踩红线：**样子、颜色、格子、身材** |")
    a("| `1_head_A.png` / `_Q` / `_E` / `_R` | 四个头放大 8 倍：**脸** |")
    a("| `<编号>_<名字>_guide.png` | 每个姿势的参考图（英雄联盟那一帧，按要画的大小放好）：**姿势、位置、大小** |")
    a("| `<编号>_<名字>_league.png` | 同一帧的大图：看清楚手臂、腿、头怎么摆 |\n")
    a("## 姿势\n")
    a("| 参考图 | 名字 | 造型 | 每格 | 画什么 |")
    a("|---|---|---|---|---|")
    for n, (name, (st, _, zh, _)) in enumerate(POSES.items(), start=2):
        where = "离地（照参考图的高度）" if LIFT.get(name, 0) is None else f"脚踩红线（y = {GROUND_Y[name]}）"
        a(f"| `{n}_{name}_guide.png` | **{name}** | {st} {ZH[st]} | {PX[name]} px | {zh}；{where} |")
    a("")
    a("## 提示词（同一段，每个姿势换最后一句）\n")
    a("附这个姿势所属姿态的 `0_design_*`、`1_head_*`，和这个姿势的 `guide`、`league` 两张图。**用 image_gen 画。**\n")
    a("```text")
    a("Attached images: 0 the character's approved pixel-art design at game size in the stance this pose belongs to (see the "
      "last line); 1 his head enlarged 8x; the GUIDE: League's own frame of the pose, a 3D render placed at exactly the size "
      "and place to draw it on the grid, the red line the ground (the render's body is slimmer than ours); the LEAGUE image: "
      "the same frame large, to read the arms, the legs and the head.")
    a("Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha "
      "only 0 or 255), BIG SQUARES aligned on one straight grid from the canvas corner (the square size is given in the last "
      "line), ONE character. Copy the POSE, the PLACE and the SIZE from the guide; copy the LOOK, the COLOURS, the BUILD "
      "(as burly and broad as the design, never as slim as the render) and the HEAD from the design - never the render's 3D "
      "shading or extra detail.")
    a("The head and face exactly as the design's: both cold blue eyes, the heavy brows, the dark beard, the bright blue "
      "feather braid by the left of his face, the dreadlocks (the head lowered or raised as the pose needs, never bigger or "
      "smaller); the arms, fists, claws, horns and blades NEVER cover his face. Every arm and leg as thick and as long as the "
      "design's, the joints bending the right way (elbows back, knees forward), the legs clearly apart, the near leg in full "
      "tone and the far leg a step darker, the body never squashed onto the legs; the spirit parts (the bear hide and head, "
      "the ram horns, the feather blades) the same shape and colours as the design's, moving with the arms and the body. One "
      "continuous 1-square near-black outline round the figure; every material in its own 2-4 flat shades; no stray single "
      "squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No spell effects (no lightning, no fire, no "
      "ice, no shield glow, no ghostly spirit animals, no motion trails), no background, no ground, no cast shadow, no text, "
      "no grid lines.")
    a("```\n")
    a("最后一句，按要画的那一个姿势换：\n")
    for n, (name, (st, _, _, en)) in enumerate(POSES.items(), start=2):
        where = ("his lowest point as high off the ground as in the guide" if LIFT.get(name, 0) is None
                 else f"his soles on the red line (y {GROUND_Y[name]})")
        a(f"- **{name}**（`udyr-pose-{name}.png`）：")
        a("  ```text")
        a(f"  POSE {name.upper()}: {en} Draw {LOOK[st]} - in exactly the pose of guide image {n}, at the guide's place and "
          f"size, every square exactly {PX[name]} px, {where}.")
        a("  ```")
    a("")
    a("## 交回前请检查\n")
    a("- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；每个姿势的格子大小照表。")
    a("- 用对了姿态的造型（A 平常、Q 熊、E 公羊、R 凤凰）；身材和造型一样壮；脸照造型、两只眼睛看得见、蓝羽毛发辫在；**手臂、爪子、羊角、羽刃不挡脸**。")
    a("- 手臂和腿的粗细长短和造型一样、关节方向对、两条腿分开；兽灵部件和造型一样；外描边连续；没有任何技能特效。\n")
    a("## 交付（`outputs/udyr-poses/`）\n")
    a(f"- {len(POSES)} 张 `udyr-pose-<名字>.png`；原始生成图原样放 `outputs/udyr-poses/raw/`；`generation-prompts.txt`；**最后**写 "
      "`HANDOFF.md`，再打包成 `outputs/udyr_poses_done.zip`。中间不要停，全部画完再交。\n")
    a("## Claude 收到后（给 Claude 看）\n")
    a("- 读回（design_shyvana_poses.py 的做法）：每张按造型的头匹配出 Codex 实际的格子和身体比例，按造型的格子取样、颜色贴到造型的色板、"
      "把造型的头原样贴在 Codex 的头上（一张脸用在所有帧），描边闭合；8 倍检查手臂和腿。")
    a("- 拼帧（rig_udyr.py）：普攻 = 待机 → a_punch；q_attack = q_wind → q_swipe；skill = q_roar；e_attack = e_hook；e_stun = "
      "e_leap → e_slam；skill2 = e_stomp；r_attack = r_thrust；ult = r_crouch → r_flap；跑步各 4 张；死亡 = 姿态受击 → d_hit → "
      "d_kneel；时长照英雄联盟的动作。")
    return "\n".join(L) + "\n"


def render(lol, frame, stance, name, out):
    cmd = [sys.executable, os.path.join(ROOT, "tools", "lol", "pose_ref.py"), "--lol", lol, "--champ", "Udyr", "--mirror",
           "--hq", "--bg", ",".join(map(str, GREY)), "--no-labels", "--head", str(HEAD), "--legs", str(LEGS),
           "--size", str(SIZE), "--width", str(WIDTH), "--fit", str(FIT), "--ground", str(GROUND), "--yaw", str(YAW),
           "--frame", frame, "--name", name, "--out", out, *PK.parts(stance)]
    subprocess.run(cmd, check=True, capture_output=True)
    return Image.open(os.path.join(out, name + ".png")).convert("RGB")


def keyed(im):
    a = np.asarray(im.convert("RGBA")).copy()
    a[np.abs(a[..., :3].astype(int) - GREY).sum(axis=2) < 20] = 0
    return Image.fromarray(a)


def grid(can, px, ground, label):
    d = ImageDraw.Draw(can)
    for k in range(0, CANVAS // px + 1):
        c = (150, 150, 150, 255) if k % 5 == 0 else (205, 205, 205, 255)
        d.line([(k * px, 0), (k * px, CANVAS)], fill=c)
        d.line([(0, k * px), (CANVAS, k * px)], fill=c)
    d.line([(0, ground), (CANVAS, ground)], fill=(220, 40, 40, 255), width=3)
    d.text((10, 10), label, fill=(30, 30, 30, 255))
    return can


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="C:/t/ud_work/udyr_pose_pack")
    ap.add_argument("--lol", default=r"D:\WeGameApps\lol")
    a = ap.parse_args()
    out, work = a.out, a.out + "_render"
    for d in (out, work):
        if os.path.isdir(d):
            shutil.rmtree(d)
        os.makedirs(d)
    fit = {}
    for st, (idle, design, rows, px, ground, (r0, r1, c0, c1), _) in STANCES.items():
        im = keyed(render(a.lol, idle, st, f"idle_{st}", work))
        x0, y0, x1, y1 = im.getbbox()
        d = np.asarray(Image.open(lp(os.path.join(SRC, "hd", design))).convert("RGBA"))
        k = rows * px / (y1 - y0)                       # League's idle height -> the design's rows
        widen = 1.0          # League's figure kept as it is (widened by the bulk, the spread arms ran off the canvas)
        fit[st] = (k, widen, y1)
        can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
        grid(can, px, ground, f"{st}: the design, {d.shape[1]} x {d.shape[0]} squares of {px} px, soles on the red line")
        big = Image.fromarray(up(d, px))
        can.alpha_composite(big, ((CANVAS - big.width) // 2 // px * px, ground - big.height))
        can.convert("RGB").save(os.path.join(out, f"0_design_{st}.png"))
        h = d[r0:r1, c0:c1]
        hb = Image.new("RGBA", (h.shape[1] * 8, h.shape[0] * 8), GREY + (255,))
        hb.alpha_composite(Image.fromarray(up(h, 8)))
        hb.convert("RGB").save(os.path.join(out, f"1_head_{st}.png"))
        print(st, "scale", round(k, 3), "widen", round(widen, 3))
    report = []
    PX.clear()
    for n, (name, (st, frame, _, _)) in enumerate(POSES.items(), start=2):
        _, _, rows, px0, ground0, _, _ = STANCES[st]
        im = keyed(render(a.lol, frame, st, name, work))
        x0, y0, x1, y1 = im.getbbox()
        k0, widen, idle_y1 = fit[st]
        lift = LIFT.get(name, 0)
        up_sq = (idle_y1 - y1) * k0 / px0 if lift is None else lift        # squares off the ground
        w_sq, h_sq = (x1 - x0) * k0 * widen / px0, (y1 - y0) * k0 / px0
        # the stance's square size, or smaller when the pose would not fit the canvas (the ground 3 squares up)
        px = px0
        while px > 6 and (w_sq * px > CANVAS - 4 * px or (h_sq + up_sq + 5) * px > CANVAS):
            px -= 1
        PX[name] = px
        ground = (CANVAS // px - 3) * px
        k = k0 * px / px0
        fig = im.crop((x0, y0, x1, y1))
        fig = fig.resize((round(fig.width * k * widen), round(fig.height * k)), Image.LANCZOS)
        bottom = ground - round(up_sq * px)
        can = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
        grid(can, px, ground, f"{name}: League's frame at the size to draw ({px} px a square, {fig.width / px:.0f} x "
                              f"{fig.height / px:.0f} squares), the ground red (y {ground})")
        GROUND_Y[name] = ground
        left = max(px, min(CANVAS - fig.width - px, (CANVAS - fig.width) // 2))
        top = max(px, bottom - fig.height)
        can.alpha_composite(fig, (left, top))
        can.convert("RGB").save(os.path.join(out, f"{n}_{name}_guide.png"))
        im.crop((x0, y0, x1, y1)).convert("RGB").save(os.path.join(out, f"{n}_{name}_league.png"))
        report.append(f"{n:2d} {name:9s} {st} {px:2d} px {fig.width / px:5.1f} x {fig.height / px:5.1f} squares, "
                      f"ground y {ground}, bottom y {bottom}"
                      + ("  TOO WIDE" if fig.width > CANVAS - 2 * px else "")
                      + ("  TOO TALL" if bottom - fig.height < px else ""))
    doc = document()
    for path in (os.path.join(SRC, "POSE_PROMPTS.md"), os.path.join(out, "POSE_PROMPTS.md")):
        with open(lp(path), "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
    zp = shutil.make_archive(out, "zip", out)
    print("\n".join(report), "\n->", zp)


if __name__ == "__main__":
    main()
