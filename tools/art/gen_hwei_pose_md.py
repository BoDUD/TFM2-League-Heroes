"""Write assets/source/hwei/POSE_PROMPTS.md from tools/art/pack_hwei_poses.py's POSES (run from the repo root).
Qiyana's poses (2026-10-22) came back with adult-long legs: this prompt gives every limb's length in squares and asks
Codex to count them."""
import sys
sys.path.insert(0, 'tools/art')
import pack_hwei_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.REST["near_leg"][-1][1] - P.REST["near_leg"][0][1])        # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips
L = []
a = L.append
a("# 异画师 彗：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 彗的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右的 Q 版年轻画师——墨绿近黑的乱发、半垂的墨绿眼睛、彩色耳饰、"
  "深紫颈环、靛蓝画师外套和宽大的青绿翻领加金纹、红橙袖口、橙衬衫和棕马甲、墨绿七分裤和青绿丝带、粉色珠串、棕色便鞋，"
  "远侧的手（画面右边）握着一支斜指地面的大画笔——深色笔杆、红色和深蓝的笔头、木色笔尖，背后浮着一道弯月形的墨痕和三滴墨）。"
  "英雄联盟里他每个动作都把画笔挥起来——收到身前、往前甩、举过头顶、指向地面、插进地里、往身后扫、张开双臂、掉在地上——这些靠挪动定稿本身的部件"
  f"摆不出来，所以请你按骨架画 **{n} 个姿势，每个一张图**（{n - 4} 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张图都是同一个彗**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边，握画笔的那只）**；"
  "**画笔是一根直的长条：黄色 = 笔杆，粉色粗段 = 红蓝色的笔头，青色 = 木色笔尖**；紫线的末端就在笔杆上（那里是手握着笔的地方）；"
  "**灰框 = 头的位置**；**淡蓝色的形状 = 背后的弯月墨痕**（和定稿里一模一样，只跟着脖子移动）。`0_design_skeleton.png` 是同样的骨架画在定稿上，"
  "看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底只有约 {LEG} 格**，**手臂从肩膀到指尖约 {ARM} 格**，**画笔从笔杆尾到笔尖 {round(P.BRUSH_L)} 格**，"
  f"头连头发 {P.HW} × {P.HH} 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**"
  "（上一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。"
  "**画笔和定稿一样长、一样粗**，只是换了方向。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只墨绿眼睛都看得见、耳饰、颈环）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、画笔**不要盖住脸**（眼睛和嘴）。**弯月墨痕照定稿画在淡蓝色的位置**，"
  "形状不变、不挡脸。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的彗是正常比例、墨痕会飞来飞去；"
  "我们的是 Q 版大头、墨痕固定在背后：身子短、手臂短、腿短，**画笔不要举到脸前面，手臂往两边、往前、往后、往上伸，不要从脸前面横过去**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `hwei-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi SLIM YOUNG PAINTER with a BIG head: messy dark green-black hair with teal lights, half-closed dark green eyes, small coloured earrings, a dark "
  "purple choker, an indigo painter's coat with a wide turquoise collar, gold trim and red-orange cuffs, a red-orange shirt and a brown vest, dark green "
  "cropped trousers with teal ribbon ties, a pink anklet, brown loafers, a GIANT PAINTBRUSH in his far hand (a dark shaft, a red and navy brush head, a "
  "wooden point) and a FLOATING CRESCENT OF PAINT STROKES behind him (navy with orange, teal and gold, three ink drops); B its HEAD with the hair shown 8x "
  f"({P.HW} squares wide, {P.HH} tall); C a SKELETON on the same 1254 canvas and {P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = "
  "the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right, the one "
  "holding the brush), the BRUSH as one straight bar - YELLOW = the shaft, the thick MAGENTA part = the red-and-navy brush head, CYAN = the wooden point "
  "- the purple arm ends on the shaft where the hand grips it, GREY BOX = where the head goes, the PALE BLUE shape = the crescent behind him (exactly as "
  "in the design, only moved with his neck), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy "
  "the POSE and the brush's swing from it, never its 3D look, its realistic proportions or its flying crescent); E (if attached) the same skeleton "
  "drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg only about {LEG} squares from the hip to the sole, each arm about {ARM} squares from the shoulder "
  f"to the fingertips, the brush {round(P.BRUSH_L)} squares from the butt of the shaft to the point, exactly as in image A. Lay the body along the "
  "skeleton: the torso and the coat along the green line, each leg along its line (bending at the dots: the dark green cropped trousers with the teal "
  "ribbon bow, the bare shin, the brown loafer - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the "
  "arms grow from the shoulders, never floating; the indigo sleeve with its red-orange cuff), the far hand GRIPPING the brush where the purple line "
  "ends. THE BRUSH drawn along the bar at the design's length and thickness: the dark shaft with its coloured bands, the red and navy head where the "
  "magenta part is, the wooden point where the cyan part is. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near "
  "side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both dark green eyes under their heavy lids, the mouth, the "
  "earrings, the choker, the messy hair) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or part of "
  "the brush covers the face (the eyes and the mouth). THE CRESCENT of paint drawn square for square as in image A where the pale blue shape is.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no paint splashes, no fire, no lightning, no eyes, no motion trails), no background, no ground, no shadow, no text, no grid lines, no "
  "skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、手臂约 {ARM} 格、画笔 {round(P.BRUSH_L)} 格，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个彗：**同一个头（照图 B，脸朝右前方、两只墨绿眼睛、耳饰、颈环、乱发）**、同样粗的腿和手臂、同样的弯月墨痕；"
  "**画笔和定稿一样长、一样粗**，红蓝笔头和木色笔尖清楚，握着它的手在笔杆上；手臂从肩膀长出来，手和画笔没有盖住脸；姿势沿着骨架；着地的脚在 "
  f"y {P.SOLE_Y}。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/hwei-poses/`）\n")
a("- " + "、".join(f"`hwei-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/hwei-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/hwei_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `hwei_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄 / 粉 / 青 = 画笔，淡蓝 = 墨痕） |")
a("| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_udyr_poses / design_qiyana_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂和画笔的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就照奇亚娜的 legs 包重画腿，再拼进 rig_hwei.py 的动作里，"
  "逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_hwei.py）：普攻 attack = a_wind → a_flick → 定稿；悚·阴沉变意 skill2_q 同普攻的两帧加大幅度；"
  "灾·没骨火 skill = q_wind → q_throw；灾·攒聚雷 skill_w = qw_raise → qw_point；灾·连皴山 skill_e = qe_raise → qe_slam；"
  "悚·滞涩幽瞳 skill2 = ew_low → ew_high；悚·双钩血喉 skill2_e = ee_wind → ee_swing；大招 ult = r_open → r_fling → r_hop；"
  "死亡 dead = d_stagger → d_kneel；跑 run = run1–4；待机 = 定稿一帧（hero_reels 做呼吸）；受击 hit = 定稿后退一格闪白。")
open('assets/source/hwei/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM)
