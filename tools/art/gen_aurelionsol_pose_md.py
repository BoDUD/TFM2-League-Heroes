"""Write assets/source/aurelionsol/POSE_PROMPTS.md from tools/art/pack_aurelionsol_poses.py's POSES (run from the repo
root). The prompt gives every part's length in squares and asks Codex to count them (Qiyana's adult-long legs,
2026-10-22)."""
import sys
sys.path.insert(0, 'tools/art')
import pack_aurelionsol_poses as P
names = list(P.POSES)
n = len(names)
ARM = round(sum(P.lengths("near_arm")))      # shoulder to the claw tip
TAIL = round(sum(P.lengths("tail")))         # root under the chest to the tip
L = []
a = L.append
a("# 铸星龙王 奥瑞利安·索尔：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 奥瑞利安·索尔的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右——浅蓝白骨质龙脸、两只亮青色眼睛、一排白尖牙、"
  "金色冠盔和往后扫的金角、洋红-紫鬃毛、深海军蓝鳞甲身体和胸口亮蓝 V 鳞、青色发光细线、背上的深紫尖刺、紫色龙爪手臂和金护腕、"
  "胸口以下深蓝到紫罗兰的星云尾巴和白色星点）。英雄联盟里他扬爪甩出星星、吸气后张嘴吐出龙息、伸爪召唤黑洞、高举爪子从天上拽下星星——"
  f"这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **{n} 个姿势，每个一张图**。待机、移动（他是飞行，用你上一轮画的 B）、挨打我从定稿本身来做，不用画。")
a(f"> - **每张图都是同一个奥瑞利安·索尔**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**最低的一点——通常是尾尖——在 y = {P.SOLE_Y}**；他是浮空的，游戏里我再把他整体抬高），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 身体的中线（胸口下沿中间到脖子根），**橙线 = 近侧的手臂（画面左边那只，在前面、颜色全亮）**，"
  "从肩膀经过手肘、手腕到最长那根爪尖；**紫线 = 远侧的手臂（画面右边那只，暗一档）**；**品红线 = 星云尾巴**（从胸口下面的根到尾尖）；"
  "**灰框 = 头的位置**。背上的深紫尖刺长在身体上，跟着身体走。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：**头 {P.HW} × {P.HH} 格**（连鬃毛和金角）；**每只手臂从肩到爪尖约 {ARM} 格**，**尾巴从根到尖约 {TAIL} 格**。"
  "骨架就是按定稿量的：**手臂、尾巴沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄四肢画错了只能重画——请画完数一数）。"
  "手臂从肩膀长出来，不能悬空；尾巴从胸口下面长出来，越往尾尖越细，星点间隔开。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、浅蓝白骨质脸、亮青色眼睛、白尖牙、金冠金角、洋红鬃毛）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**——**只有 q_breath 一张例外：下颌张大**（嘴里露出上下两排牙和一点亮光），"
  "其余地方照样。手臂、爪子、尾巴**不要盖住脸**。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右；渲染里尾巴是一截没上色的黑色网格，看它怎么摆就行），**动作照它**，长相照定稿。"
  "英雄联盟里他有时会把头低下去、转过身或者头朝下——**我们的永远是这个造型、3/4 正面朝右、头照定稿**，只照它的手臂、尾巴和身体的动作。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `aurelionsol-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (the tail tip on y {P.SOLE_Y}) - "
  "THE STAR DRAGON, floating, no legs: a PALE BLUE-WHITE BONY DRAGON FACE with two GLOWING CYAN EYES and a row of WHITE SHARP TEETH, a GOLD CROWN-HELM "
  "with GOLD HORNS sweeping back, a big MAGENTA-VIOLET MANE, a DEEP NAVY SCALED BODY with BRIGHT BLUE V-SCALES down the chest and thin GLOWING CYAN "
  "LINES, DARK PURPLE SPIKES along the back, PURPLE CLAWED ARMS with GOLD BRACERS, and below the chest a DEEP BLUE to VIOLET NEBULA TAIL dotted with "
  f"white stars; B its HEAD shown 8x ({P.HW} x {P.HH} squares, the mane and horns included); C a SKELETON on the same 1254 canvas and {P.PX} px grid: "
  "green = his body's middle line (the bottom of the chest to the base of the neck), ORANGE = the NEAR arm (image left, in front) from the shoulder "
  "through the elbow and the wrist to the longest claw's tip, PURPLE = the FAR arm (image right), MAGENTA = the nebula tail from its root under the "
  "chest to its tip, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose (copy the POSE, the "
  "arms' and the tail's swing from it - its tail is an untextured black shape there - never its 3D look, its realistic proportions or a lowered, "
  "turned or upside-down head); E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; the lowest point (usually the tail tip) on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: the head {P.HW} x {P.HH} squares; each arm about {ARM} squares from the shoulder to the claw tip, the tail about {TAIL} "
  "squares from root to tip, exactly as in image A. Lay the body along the skeleton: the navy scaled chest with its blue V-scales and cyan lines along "
  "the green line, the back spikes on the back; each ARM from its shoulder along its line (bending at the dots, the gold bracer at the wrist, the "
  "claws open or clenched as the pose says, the background visible between them); the NEBULA TAIL along the magenta line (the SAME thickness as in "
  "image A, thinner toward the tip, the stars spaced apart). Never stretch or shorten an arm or the tail. The near arm in full tone, the far one a "
  "step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both glowing cyan eyes, the teeth, the gold helm and horns, "
  "the magenta mane) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind (only in the breath pose the "
  "jaw opens, as the pose line says). No arm, claw or tail covers the face.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares except the stars, no dithering, no gradients, no "
  "glow, no blur, no anti-aliasing.")
a("No effects (no breath beam, no star, no black hole, no shockwave, no motion lines), no background, no starry sky, no ground, no shadow, no text, no "
  "grid lines, no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：头 {P.HW} × {P.HH} 格、手臂从肩到爪尖约 {ARM} 格、尾巴约 {TAIL} 格，和定稿一样——画长了、画短了就重画。")
a("- 每张都是定稿的同一个奥瑞利安·索尔：**同一个头（照图 B，脸朝右前方、两只亮青色眼睛、白尖牙、金冠金角、洋红鬃毛）**，只有 q_breath 张嘴；"
  f"同样颜色的鳞甲、发光线、背刺、爪子和星云尾巴；手臂从肩膀长出来，手臂、爪子、尾巴没有盖住脸；姿势沿着骨架；最低点在 y {P.SOLE_Y}；"
  "没有一张是背影、侧脸、低头或头朝下。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/aurelionsol-poses/`）\n")
a("- " + "、".join(f"`aurelionsol-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/aurelionsol-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/aurelionsol_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `aurelionsol_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |")
a("| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，尾尖 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_taliyah_poses 的做法：按头的大小定比例，头换成定稿的头；q_breath 保留 Codex 张开的下颌），"
  "颜色对到定稿的调色板；**先在 8 倍下量手臂和尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_aurelionsol.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_aurelionsol.py）：普攻 attack = a_wind → a_throw；星河冲荡 skill = q_wind → q_breath（吐息时循环）；"
  "星芒凝汇 skill2 = e_reach → e_hold；星落 / 天瀑 ult = r_call → r_pull；死亡 dead = d_rear → d_down；"
  "移动 run = 第 1 步 B 的飞行（hd/run.png，身子和尾巴波动）；待机 = 定稿悬浮（上下浮动、尾巴摆动，hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。")
open('assets/source/aurelionsol/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; arm", ARM, "tail", TAIL)
