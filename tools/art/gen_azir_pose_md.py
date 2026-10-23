"""Write assets/source/azir/POSE_PROMPTS.md from tools/art/pack_azir_poses.py's POSES (run from the repo root).
The prompt gives every limb's length in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22).
The summons' poses (the soldier's stab, the guard's charge) have no skeleton: drawn from their approved designs."""
import sys
sys.path.insert(0, 'tools/art')
import pack_azir_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.REST["near_leg"][-1][1] - P.REST["near_leg"][0][1])        # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips (near)
FAR = round(sum(P.lengths("far_arm")))
SUMMONS = {   # name -> (design, squares wide x tall, px a square, soles y, Chinese, English)
    "s_lift": ("30_soldier.png", (29, 54), 20, 1190,
               "沙兵举矛：正面，两只手把长矛举到胸前、矛尖朝下对着前面的地面，膝盖微弯准备刺",
               "LIFT - the sand soldier from the FRONT, both hands raising the spear before his chest, the gold blade "
               "pointing down at the ground in front of him, the knees a little bent, ready to stab."),
    "s_stab": ("30_soldier.png", (29, 54), 20, 1190,
               "沙兵刺下：正面，往前跨半步，两只手把长矛往前下方狠狠刺进地面（矛尖在他脚前），身子前压",
               "STAB - the sand soldier from the FRONT, half a step forward, both hands driving the spear down hard "
               "into the ground in front of his feet, the body pressing forward."),
    "g_push1": ("31_guard.png", (36, 45), 24, 1188,
                "禁军冲锋 1：侧面朝右，肩膀顶着塔盾往右冲，近侧腿往前迈、远侧腿往后蹬，塔盾稍稍前倾",
                "CHARGE 1 - the guard from the SIDE facing right, his shoulder behind the tower shield charging to the "
                "right, the near leg striding forward, the far leg pushing off behind, the shield leaning a little "
                "forward."),
    "g_push2": ("31_guard.png", (36, 45), 24, 1188,
                "禁军冲锋 2：同上，两腿换过来（远侧腿往前、近侧腿往后蹬），塔盾直立往前撞",
                "CHARGE 2 - the same charge with the legs swapped (the far leg forward, the near leg pushing off "
                "behind), the shield upright, ramming forward."),
}
L = []
a = L.append
a("# 沙漠皇帝 阿兹尔：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 阿兹尔的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右的 Q 版沙漠皇帝——鹰首金盔（鹰嘴、冠羽、两颊金翅膀、发光的青蓝眼睛，"
  "没有人脸）、金甲上的大青蓝宝石、深紫袍子和披风、身后几条短的紫色飘带、胸前紫红色的布、灰蓝小腿、金护胫，近侧的手（画面左边）握着一根竖直的长权杖，"
  "杖头是分叉的金色尖刃夹一颗青蓝宝石，远侧的手（画面右边）是金色爪状手甲）。"
  "英雄联盟里他每个动作都在挥权杖、号令——举手、指出去、挥杖、刺出去、化沙冲刺、高举权杖——这些靠挪动定稿本身的部件"
  f"摆不出来，所以请你按骨架画 **{n} 个姿势，每个一张图**（{n - 4} 个动作姿势 + 4 帧跑步），另外照沙兵和禁军的定稿画 **{len(SUMMONS)} 个召唤物姿势**。"
  "待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张阿兹尔都是同一个阿兹尔**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边，握权杖的那只）**，**紫线 = 远侧的手臂（画面右边，金爪手甲）**；"
  "**权杖是一根直的长条：黄色 = 杖身，青色 = 分叉的金色杖头**；橙线的末端就在杖身上（那里是手握着权杖的地方）；"
  "**灰框 = 头的位置（鹰首金盔）**；**半透明的橙色形状 = 身后的紫色飘带**（和定稿里一模一样，只跟着腰移动）。`0_design_skeleton.png` 是同样的骨架画在定稿上，"
  "看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的大头——**鹰盔 {P.HW} × {P.HH} 格**；身子和腿很短——**每条腿从胯到脚底只有约 {LEG} 格**，"
  f"**近侧手臂从肩膀到指尖约 {ARM} 格，远侧约 {FAR} 格**，**权杖从杖尾到杖头 {round(P.WAND_L)} 格**（很长，和他整个人一样高）。"
  "骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**"
  "（以前的英雄腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。"
  "**权杖和定稿一样长、一样粗，杖身是直的**（用户特别要求：权杖要直，不能歪），只是换了方向。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、鹰嘴、冠羽、两颊金翅膀、发光的青蓝眼睛 2 × 2 带高光）。每个姿势都是这一个鹰盔，"
  "只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、权杖**不要盖住鹰嘴和眼睛**。他的手臂很短，举不过这么大的头："
  "**权杖举高时在头的左边**。**飘带照定稿画在半透明橙色的位置**，形状不变。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的阿兹尔是正常比例；"
  "我们的是 Q 版大头：身子短、手臂短、腿短，**手臂往两边、往前、往后、往上伸，不要从脸前面横过去**。\n")
a(f"## 阿兹尔的 {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `azir-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词：阿兹尔（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（鹰盔）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi DESERT EMPEROR with a BIG head that is a FALCON-HEADED GOLD HELMET (a beak, a crest, a gold wing on each cheek, a glowing teal eye, no human "
  "face), gold armour with big teal gems on the shoulders, the chest and the hips, a deep purple robe and cape with a few short purple ribbons behind "
  "him, a magenta cloth down his front, grey-blue lower legs, gold greaves, a gold clawed gauntlet on his far hand, and a LONG STRAIGHT GOLD SCEPTRE "
  f"in his NEAR hand (a straight gold shaft with a teal gem, a forked gold head round a teal gem); B its HELMET shown 8x ({P.HW} squares wide, {P.HH} "
  f"tall); C a SKELETON on the same 1254 canvas and {P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, "
  "in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left, the one holding the sceptre), PURPLE = the FAR arm (image right, the "
  "clawed hand), the SCEPTRE as one straight bar - YELLOW = the shaft, CYAN = the forked gold head - the orange arm ends on the shaft where the hand "
  "grips it, GREY BOX = where the head goes (the helmet), the TRANSLUCENT ORANGE shape = the purple ribbons behind him (exactly as in the design, only "
  "moved with his waist), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE and the "
  "sceptre's swing from it, never its 3D look or its realistic proportions); E (if attached) the same skeleton drawn over image A, showing which line "
  "is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - the helmet {P.HW} x {P.HH} squares; each leg only about {LEG} squares from the hip to the sole, the near arm "
  f"about {ARM} squares from the shoulder to the fingertips and the far arm about {FAR}, the sceptre {round(P.WAND_L)} squares from its foot to its tip, "
  "exactly as in image A. Lay the body along the skeleton: the torso with its armour, gems, robe and the magenta cloth along the green line, each leg "
  "along its line (bending at the dots: the grey-blue leg and the gold greave - the SAME thickness, length and colours as in image A), each arm from its "
  "shoulder along its line (the arms grow from the big gold shoulder plates, never floating), the near hand GRIPPING the sceptre where the orange line "
  "ends. THE SCEPTRE drawn along the bar at the design's length and thickness, PERFECTLY STRAIGHT: the gold shaft with its teal gem, the forked gold head "
  "with its teal gem where the cyan part is. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, "
  "the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the beak to the front-right, the crest, the cheek wings, the glowing teal eye 2x2 with a "
  "highlight) - the same helmet in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or part of the sceptre covers the beak "
  "or the eye. THE RIBBONS drawn square for square as in image A where the translucent orange shape is.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no sand, no dust, no light, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a(f"## 召唤物的 {len(SUMMONS)} 个姿势（没有骨架，照定稿画）\n")
a("沙兵和禁军是地面上的特效图，游戏里不会左右翻转：**沙兵一直是正面**，**禁军一直是朝右的侧面**（朝左的我自己翻）。样子、颜色、粗细、"
  "**格子数**全照它们的定稿（`30_soldier.png` 沙兵 29 × 54 格、`31_guard.png` 禁军 36 × 45 格，都是 8 倍放大），只换姿势。\n")
a("| 文件 | 定稿 | 格子 | 姿势 |")
a("|---|---|---|---|")
for name, (des, (w, h), px, sole, zh, en) in SUMMONS.items():
    a(f"| `azir-pose-{name}.png` | `{des}` | 每格 {px} px，约 {w} × {h} 格，脚底 y {sole} | {zh} |")
a("")
a("```text")
a("Attached image: A an APPROVED pixel-art figure shown 8x (every 8x8 block is one square) - the SAND SOLDIER from the front (a dark-skinned soldier in "
  "a gold falcon helmet that covers his face, gold shoulder plates, a bare chest, a dark olive cape, gold greaves, a long spear with a gold leaf blade) "
  "or the IMPERIAL GUARD from the side facing right (the same soldier crouched behind a tall gold tower shield).")
a("Draw with the image generator ONE clean pixel-art picture of the SAME figure in a new pose: a 1254x1254 PNG with a real transparent background "
  "(alpha only 0 or 255), BIG squares of the size given below aligned on one straight grid from the canvas corner, the SAME number of squares as image A "
  "(the same height, thickness and colours - count them), standing in the middle of the canvas with the feet on the ground line given below. The soldier "
  "stays seen from the FRONT, the guard from the SIDE facing right. One continuous 1-square near-black outline; no stray single squares, no dithering, "
  "no gradients, no glow, no blur, no anti-aliasing. No effects (no sand, no dust, no motion lines), no background, no ground, no shadow, no text.")
a("THE POSE: <one line below, with its square size and ground line>")
a("```\n")
for name, (des, (w, h), px, sole, zh, en) in SUMMONS.items():
    a(f"- {name}（{des}）: `{en} Every square exactly {px} px, about {w} x {h} squares, the feet on y {sole}.`")
a("")
a("## 交回前请检查\n")
a(f"- **{n + len(SUMMONS)} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；阿兹尔**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：鹰盔 {P.HW} × {P.HH} 格、每条腿从胯到脚底约 {LEG} 格、手臂约 {ARM} / {FAR} 格、权杖 {round(P.WAND_L)} 格，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个阿兹尔：**同一个鹰盔（照图 B，鹰嘴朝右前方、发光的青蓝眼睛）**、同样粗的腿和手臂、同样的飘带；"
  "**权杖和定稿一样长、一样粗、杖身笔直**，握着它的手在杖身上；手臂从肩膀长出来，手和权杖没有盖住鹰嘴和眼睛；姿势沿着骨架；着地的脚在 "
  f"y {P.SOLE_Y}。")
a("- 沙兵正面、禁军朝右侧面，格子数和它们的定稿一样。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/azir-poses/`）\n")
a("- " + "、".join(f"`azir-pose-{x}.png`" for x in names + list(SUMMONS)) + "；原始生成图原样放 `outputs/azir-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/azir_poses_done.zip`。中间不要停，{n + len(SUMMONS)} 张都画完再交。\n")
a("## 附图（压缩包 `azir_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄 / 青 = 权杖，半透明橙 = 飘带） |")
a("| `1_head.png` | 定稿的鹰盔（8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |")
a("| `30_soldier.png` / `31_guard.png` | 沙兵（正面）和禁军（朝右侧面）的定稿，8 倍 |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_aurora_poses 的做法：按头的大小定比例，头换成定稿的鹰盔——头框里权杖穿过的那一段要留出来），"
  "颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂和权杖的长短粗细，和定稿比，权杖要直**（codex-legs-need-skeletons），腿长了就照 legs 包重画腿，"
  "再拼进 rig_azir.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_azir.py）：普攻 attack = c_wind → c_point；狂沙猛攻 skill = q_wind → q_thrust；"
  "流沙移形 skill2 = e_dash → e_land；禁军之墙 ult = r_raise → r_lift → r_sweep；死亡 dead = d_stagger → d_kneel；"
  "跑 run = run1–4；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。"
  "沙兵 = 定稿（站）→ s_lift → s_stab；禁军 = g_push1 ↔ g_push2（朝左的左右翻一份）；太阳圆盘 = 定稿（光效第 3 步画）。")
open('assets/source/azir/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses +", len(SUMMONS), "summons; leg", LEG, "arm", ARM, FAR)
