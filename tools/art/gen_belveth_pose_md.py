"""Write assets/source/belveth/POSE_PROMPTS.md from tools/art/pack_belveth_poses.py's POSES (run from the repo root).
The prompt gives every part's length in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22)."""
import sys
sys.path.insert(0, 'tools/art')
import pack_belveth_poses as P
names = list(P.POSES)
n = len(names)
WING = round(sum(P.lengths("near_wing")))     # shoulder to the wing tip along the edge
TAIL = round(sum(P.lengths("tail")))          # root to tip
CLAW = round(sum(P.lengths("near_claw")))     # under the hem to the claw tip
L = []
a = L.append
a("# 虚空女皇 卑尔维斯：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 卑尔维斯的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右——深紫色的脸、两只发光的品红眼睛、头顶品红的冠和金黄饰片、"
  "两肩高高的深紫长刺、灰青象牙色的胸口花饰和淡紫钩片、肩上的品红圆珠、两只收拢像斗篷一样裹着身体的深灰青膜翼、下面粉紫色的爪子、"
  "左边拖在地上的长尾巴）。英雄联盟里她用膜翼像刀一样劈砍、整个身子放平往前冲、扬起尾巴砸地、张开膜翼旋转、缩成一团再展开成真身——"
  f"这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **{n} 个姿势，每个一张图**。待机、移动（她是贴地滑行）、挨打我从定稿本身来做，不用画。")
a(f"> - **每张图都是同一个卑尔维斯**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**爪尖着地在 y = {P.SOLE_Y}**；骨架说离地的姿势她飘在地面上方），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 身体的中线（下摆中间到脖子根），**橙线 = 近侧膜翼（画面左边那只，在前面、颜色全亮）的前缘**，"
  "**紫线 = 远侧膜翼（画面右边那只，暗一档）的前缘**，**半透明的青色面 = 膜翼的翼膜**（从前缘一直连到身体下摆），**品红线 = 尾巴**（从下摆后面的根到尾尖），"
  "**粉线 = 爪子**（近侧、远侧各一束）；**灰框 = 头的位置**；**半透明的紫色形状 = 两根肩刺和高领**（和定稿里一模一样，只跟着脖子移动；身子放平时跟着身子斜过去）。"
  "`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分——**定稿里两只膜翼收拢垂下，就是她身上的斗篷**，"
  "举起来、张开的时候斗篷就变成翅膀，身子底下露出深紫黑的躯体。")
a(f"> - **长短要数格子**：**头 {P.HW} × {P.HH} 格**；**每只膜翼从肩到翼尖约 {WING} 格**（翼膜很宽，从前缘一直连到身体），"
  f"**尾巴从根到尖约 {TAIL} 格**，**爪子约 {CLAW} 格**。骨架就是按定稿量的：**膜翼、尾巴沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**"
  "（以前的英雄四肢画错了只能重画——请画完数一数）。膜翼从肩膀长出来，不能悬空。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、深紫的脸、两只发光的品红眼睛、品红的冠和金黄饰片）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**。膜翼、尾巴、爪子**不要盖住脸**。**肩刺和高领照定稿画在半透明紫色的位置**，形状不变。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟里她有时会转过身去背对镜头、"
  "或者变成巨大的真身——**我们的永远是这个造型、3/4 正面朝右**，只照它的膜翼、尾巴和身体的动作。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `belveth-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (claws on y {P.SOLE_Y}) - "
  "THE VOID EMPRESS: a DARK VIOLET face with two GLOWING MAGENTA EYES, a MAGENTA CREST and a GOLD-YELLOW ornament on her head, two TALL DARK PURPLE "
  "SPIKES rising from her shoulders round a high collar, a pale teal-ivory spiky fan on her chest with pale violet hooks beside it, a glowing magenta "
  "orb on each shoulder, her two ARMS are HUGE BAT-LIKE WING MEMBRANES (dark slate-teal, magenta edges) - in image A FOLDED DOWN round her like a long "
  "CLOAK - pink-magenta CLAWS under the cloak, a LONG TAIL (dark plum on top, magenta underneath) lying on the ground on the left; "
  f"B its HEAD shown 8x ({P.HW} x {P.HH} squares); C a SKELETON on the same 1254 canvas and {P.PX} px grid: green = her body's middle line (the hem's "
  "middle to the base of the neck), ORANGE = the leading edge of the NEAR wing (image left, in front) with its translucent teal membrane, PURPLE = the "
  "leading edge of the FAR wing (image right) with its membrane, MAGENTA = the tail from its root at the back of the hem to its tip, PINK = the claws, "
  "GREY BOX = where the head goes, the TRANSLUCENT VIOLET shape = the shoulder spikes and the high collar (exactly as in the design, only moved with "
  "her neck), the red horizontal line = the ground; D the original character in this pose (copy the POSE, the wings' and the tail's swing from it - "
  "never its 3D look, its realistic proportions, a turned back or its giant true form); E (if attached) the same skeleton drawn over image A, showing "
  "which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; claws that touch the ground on y {P.SOLE_Y}, or the body floating above it where the skeleton is lifted.")
a(f"COUNT THE SQUARES: the head {P.HW} x {P.HH} squares; each wing about {WING} squares from the shoulder to the tip along its edge, the tail about "
  f"{TAIL} squares from root to tip, the claws about {CLAW} squares, exactly as in image A. Lay the body along the skeleton: the dark carapace, the "
  "collar fan and the hooks along the green line; each WING from its shoulder along its line (its bones bending at the dots, magenta at the edge and "
  "the tip), its dark slate-teal MEMBRANE spread from that edge to her body where the translucent teal sheet is (where the wings open, her dark "
  "plum-black body shows below the collar); the TAIL along the magenta line (the SAME thickness as in image A, magenta underneath); the claws along the "
  "pink lines. THE SHOULDER SPIKES AND COLLAR drawn square for square as in image A where the translucent violet shape is. Never stretch or shorten a "
  "wing or the tail. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both glowing magenta eyes, the magenta crest, the gold "
  "ornament) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind. No wing, tail or claw covers the face.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no slash trails, no void dash, no shockwave, no coral, no motion lines), no background, no ground, no shadow, no text, no grid lines, "
  "no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：头 {P.HW} × {P.HH} 格、膜翼从肩到翼尖约 {WING} 格、尾巴约 {TAIL} 格、爪子约 {CLAW} 格，和定稿一样——画长了、画短了就重画。")
a("- 每张都是定稿的同一个卑尔维斯：**同一个头（照图 B，脸朝右前方、两只品红眼睛、品红冠）**、同样的肩刺和高领、同样颜色的膜翼和尾巴；"
  f"膜翼从肩膀长出来，膜翼、尾巴没有盖住脸；姿势沿着骨架；着地的爪子在 y {P.SOLE_Y}；没有一张是背影、侧脸或巨大的真身。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/belveth-poses/`）\n")
a("- " + "、".join(f"`belveth-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/belveth-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/belveth_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `belveth_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，半透明紫 = 肩刺和高领，半透明青 = 翼膜） |")
a("| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，爪尖 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_singed_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量膜翼和尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_belveth.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_belveth.py）：普攻 attack = a_wind → a_slash；虚空激流 skill = q_dash；"
  "上觐沉渊 skill2 = w_coil → w_slam；搠面皇锋 skill_e = e_spin1 ↔ e_spin2 循环；万载豪筵 ult = r_curl → r_rise；死亡 dead = d_reel → d_down；"
  "移动 run = 定稿贴地滑行（上下浮动、膜翼下摆摆动）；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。")
open('assets/source/belveth/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; wing", WING, "tail", TAIL, "claw", CLAW)
