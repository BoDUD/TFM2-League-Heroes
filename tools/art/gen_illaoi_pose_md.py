"""Write assets/source/illaoi/POSE_PROMPTS.md from tools/art/pack_illaoi_poses.py's POSES and TENTACLE (run from the repo
root). Qiyana's poses (2026-10-22) came back with adult-long legs: this prompt gives every limb's length in squares and
asks Codex to count them; her idol is a big prop, placed by the gold disc on each skeleton."""
import sys
sys.path.insert(0, 'tools/art')
import pack_illaoi_poses as P
names = list(P.POSES)
tn = list(P.TENTACLE)
n, nt = len(names), len(tn)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips (the bracer arm)
ARM2 = round(sum(P.lengths("far_arm")))
IDOL = round(P.IDOL_R * 2)
L = []
a = L.append
a("# 海兽祭司 俄洛伊：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 俄洛伊和触手的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-2：3/4 正面朝右的 Q 版女祭司——深棕色皮肤、绿眼睛、浓眉、金鼻环、"
  "黑发高发髻套金环、辫子垂在背后，金护肩金领圈、青绿胸布、结实的手臂（画面右边那只有青绿螺旋纹身和大金护腕，拳头叉腰），金腰带、"
  "暗红腰布、灰绿布裙，墨绿高靴；画面左边那只手托着**扛在肩上的大金色神像**（圆盘，正面青绿螺旋眼，右边一排扇形金凸起）；"
  "`T0_tentacle.png` 是触手：正面、深海绿、浅青螺旋纹、背鳍、卷钩、根部碎石）。")
a(f"> - 英雄联盟里她抡神像砸地、跳起来砸、把神像推出去扯灵魂、高高跃起跪地砸，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 "
  f"**{n} 个俄洛伊姿势**（{n - 4} 个动作 + 4 帧跑步），再画 **{nt} 个触手姿势**（正面），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张俄洛伊都是同一个俄洛伊**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，"
  "**橙线 = 戴大金护腕、有纹身的那只手臂**（定稿里在画面右边、拳头叉腰），**紫线 = 托神像的那只手臂**（定稿里在画面左边、神像下面）；"
  "两条手臂上**大一点的圆点是手**；**灰框 = 头的位置**（头连发髻）；**半透明的金色圆盘 = 神像的位置和大小**。"
  "`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的腿短——**每条腿从胯到脚底约 {LEG} 格**；**戴护腕的手臂从肩膀到拳头约 {ARM} 格、托神像的约 {ARM2} 格**；"
  f"头连发髻 {P.HW} × {P.HH} 格；**神像直径约 {IDOL} 格**（和定稿一样大，不放大不缩小）。骨架就是按定稿量的：**腿、手臂沿着骨架画，"
  "长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。"
  "手臂从肩膀长出来，不能悬空。")
a("> - **神像**：照定稿的神像画（金色 4 档、正面青绿螺旋眼、右边扇形凸起），**画在金色圆盘的位置，和圆盘一样大**；手放在骨架的圆点上——"
  "**手就抓在神像的边上**（两只手都碰到神像时就是双手抱着它）。神像可以按动作转一点角度，但还是那一个神像。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只绿眼睛都看得见、浓眉、金鼻环、高发髻、金环）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、神像**不要盖住脸**（眼睛、鼻环、嘴）。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的俄洛伊是高大的成年人、手臂长；"
  "我们的是 Q 版大头：身子短、手臂短，**照骨架的长短和神像圆盘的位置画，不照原版的长短**（原版能把神像举过头顶，我们的手臂够不到，"
  "就照圆盘放在头旁边或身前）。原版有几帧神像上连着一条**大触手**（扯灵魂的特效），**不要画触手**，那是第 3 步的特效。\n")
a(f"## {n} 个俄洛伊姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `illaoi-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a(f"## {nt} 个触手姿势（正面）\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(tn, 1):
    a(f"| T{k} | `illaoi-tentacle-{name}.png` | {P.TENTACLE[name][1]} |")
a("")
a("## 提示词 A：俄洛伊（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi STRONG PRIESTESS with a BIG head: dark brown skin, green eyes, thick brows, a gold nose ring, black hair in a high bun with a gold ring and "
  "braids down her back; gold shoulder plates and a gold collar, a teal chest wrap with gold plates, strong bare arms - the arm on the image right with a "
  "teal spiral tattoo, a big gold bracer and its fist on her hip, the arm on the image left holding up a BIG ROUND GOLD IDOL resting on her shoulder "
  "(a thick carved gold disc with a teal spiral eye on its face and a fan of gold ridges on its right side); a gold belt, a dark red loincloth, a "
  f"grey-green cloth skirt, dark green boots; B its HEAD with the bun shown 8x ({P.HW} squares wide, {P.HH} tall); C a SKELETON on the same 1254 canvas "
  f"and {P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), ORANGE = "
  "the BRACER arm (the tattooed arm, on the image right in A), PURPLE = the IDOL arm (on the image left in A), the bigger dot on each arm = the hand, "
  "GREY BOX = where the head goes, the TRANSLUCENT GOLD DISC = where the idol goes and how big it is, the red horizontal line = the ground; D the "
  "original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its long realistic arms and legs, or the big "
  "tentacle some of its frames show coming out of the idol); E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg only about {LEG} squares from the hip to the sole, the bracer arm about {ARM} squares from the "
  f"shoulder to the fist and the idol arm about {ARM2}, the idol about {IDOL} squares across, exactly as in image A. Lay the body along the skeleton: the "
  "torso with the chest wrap, the belt, the loincloth and the cloth skirt along the green line, each leg along its line (bending at the dots: the dark "
  "skin thigh, the dark green boot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (strong bare arms "
  "growing from the shoulders, never floating; the gold bracer on the orange one). THE IDOL: the same gold idol as in image A drawn exactly on the gold "
  "disc, the same size; each hand on its dot holds the idol's rim when the dot touches the disc (both dots on it = both hands hold it). Never stretch or "
  "shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both green eyes, the brows, the nose ring, the bun with its "
  "gold ring) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or idol covers the face (the eyes, the "
  "nose ring and the mouth); the braids follow the head.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no tentacles, no spirit, no shockwave, no dust, no glow, no motion trails), no background, no ground, no shadow, no text, no grid lines, "
  "no skeleton lines, no gold disc guide.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 提示词 B：触手（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`T0_tentacle.png`（定稿）、这个姿势的 `T*_league.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art TENTACLE seen from the FRONT, on a 1254x1254 canvas with {P.PX} px squares (its root on y {P.SOLE_Y}) - a "
  "thick deep sea-green tentacle rising out of a ring of grey-brown stones, darker on its back and lighter teal-green on its belly, pale aqua spiral "
  "patterns of 1-square lines, a row of fin spikes along its back, the tip curled into a hook; B the original tentacle in this pose, seen from the front "
  "(copy the POSE from it, never its 3D look or its cyan colour).")
a("Draw with the image generator ONE clean pixel-art picture of the tentacle of image A in the POSE of image B, still seen from the FRONT, standing in "
  f"the middle of the canvas: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square "
  f"size as image A - aligned on one straight grid from the canvas corner; its root stones on y {P.SOLE_Y}. The SAME tentacle: the same thickness, "
  "colours, spiral patterns, fins and root stones, only bent, stretched or squashed as the pose says. Everything inside the canvas.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing. No effects (no splash, no dust, no shockwave, no cracks in the ground), no background, no ground, no shadow, no text, no grid lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in tn:
    a(f"- {name}: `{P.TENTACLE[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n + nt} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：俄洛伊每条腿从胯到脚底约 {LEG} 格、戴护腕的手臂约 {ARM} 格、托神像的约 {ARM2} 格、神像直径约 {IDOL} 格，和定稿一样——腿画长了就重画。")
a("- 每张俄洛伊都是定稿的同一个俄洛伊：**同一个头（照图 B，脸朝右前方、两只绿眼睛、浓眉、金鼻环、高发髻）**、同样粗的手臂和腿；"
  f"神像在金色圆盘的位置、一样大，手抓在神像边上；手臂从肩膀长出来，手、神像没有盖住脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a("- 每张触手都是定稿的同一条触手，**正面**，粗细、颜色、螺旋纹、背鳍、根部石块都一样；不出画。")
a("- 所有图没有特效、没有骨架线、没有网格线、没有金色圆盘辅助线。\n")
a("## 交付（`outputs/illaoi-poses/`）\n")
a("- " + "、".join(f"`illaoi-pose-{x}.png`" for x in names) + "；")
a("- " + "、".join(f"`illaoi-tentacle-{x}.png`" for x in tn) + "；")
a("- 原始生成图原样放 `outputs/illaoi-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/illaoi_poses_done.zip`。中间不要停，{n + nt} 张都画完再交。\n")
a("## 附图（压缩包 `illaoi_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，金色圆盘 = 神像） |")
a("| `1_head.png` | 定稿的头（8 倍，连发髻）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 俄洛伊定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |")
a(f"| `T0_tentacle.png` | 触手定稿（正面，每格 {P.PX} px，根部 y {P.SOLE_Y}） |")
a(f"| `T1_{tn[0]}_league.png` … `T{nt}_{tn[-1]}_league.png` | 触手每个姿势的英雄联盟原版那一帧（正面） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_ivern_poses / design_hwei_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂的长短粗细和神像的大小，和定稿比**（codex-legs-need-skeletons），腿长了就照艾翁的 legs 包重画腿，再拼进 rig_illaoi.py 的动作里，"
  "逐帧自查后才发合成 GIF。触手按它自己的格子读回（PPU 1.5），对到 hd/tentacle.png 的调色板。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_illaoi.py）：普攻 attack = a_raise → a_slam → 定稿；严酷训诫 skill = w_jump → w_land；"
  "灵魂试炼 skill2 = e_thrust → e_yank；过界信仰 ult = r_crouch → r_leap → r_slam；死亡 dead = d_stagger → d_slump；跑 run = run1–4；"
  "待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。触手（特效图，正面）：出现 = tn_rise → tn_grow → 定稿，待机 = 定稿 ↔ tn_sway，"
  "抽打 = tn_rear → tn_slam → tn_recoil，消失 = tn_sink。")
open('assets/source/illaoi/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses +", nt, "tentacle; leg", LEG, "arm", ARM, ARM2, "idol", IDOL)
