"""Write assets/source/ivern/POSE_PROMPTS.md from tools/art/pack_ivern_poses.py's POSES and DAISY (run from the repo
root). Qiyana's poses (2026-10-22) came back with adult-long legs: this prompt gives every limb's length in squares and
asks Codex to count them."""
import sys
sys.path.insert(0, 'tools/art')
import pack_ivern_poses as P
names = list(P.POSES)
dz = list(P.DAISY)
n, nd = len(names), len(dz)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips (the twig arm)
ARM2 = round(sum(P.lengths("far_arm")))
L = []
a = L.append
a("# 翠神 艾翁：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 艾翁和小菊的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-2：3/4 正面朝右的 Q 版树人——浅灰白树皮色的小圆脸、琥珀色眼睛、"
  "大鼻子、咧嘴笑，一大把亮绿树叶胡子，两只浅灰绿羊角，头顶红色白点蘑菇，左耳边挂个小木环，棕色木头身子和树叶裙、身前一道白布条，"
  "画面左边的手举着带两片叶子的小树枝（手腕两道金环），画面右边的手托着红苹果，两条深红棕树皮腿、分叉的根脚、近侧小腿上长着红浆果；"
  "`D0_daisy.png` 是小菊：正面的青苔岩石傀儡）。")
a(f"> - 英雄联盟里他扔种子、甩荆棘、蹲下跳起召唤小菊，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **{n} 个艾翁姿势**"
  f"（{n - 4} 个动作 + 4 帧跑步），再画 **{nd} 个小菊姿势**（正面），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张艾翁都是同一个艾翁**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根，被树叶胡子盖着），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边，拿小树枝的那只）**，**紫线 = 远侧的手臂（画面右边，拿苹果的那只）**；"
  "两条手臂上**大一点的圆点是手**（小树枝 / 苹果就在那里）；**灰框 = 头的位置**（头连羊角、蘑菇，很宽）。`0_design_skeleton.png` 是同样的骨架画在定稿上，"
  "看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底只有约 {LEG} 格**；手臂是细长的树枝，**拿树枝的手臂从肩膀到指尖约 {ARM} 格、"
  f"拿苹果的约 {ARM2} 格**；头连羊角 {P.HW} × {P.HH} 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，"
  "不要拉长或压短**（上一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。"
  "树叶胡子和定稿一样大，盖在胸前，跟着身子走。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只琥珀色眼睛都看得见、大鼻子、笑脸、羊角、蘑菇、小木环）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、树枝、苹果**不要盖住脸**（眼睛、鼻子、嘴）；手臂举高时从羊角旁边或羊角前面过去。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的艾翁是细长的高个子、腿占一半身高；"
  "我们的是 Q 版大头：身子短、腿短，**照骨架的长短画，不照原版的长短**。\n")
a(f"## {n} 个艾翁姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `ivern-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a(f"## {nd} 个小菊姿势（正面）\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(dz, 1):
    a(f"| D{k} | `ivern-daisy-{name}.png` | {P.DAISY[name][1]} |")
a("")
a("## 提示词 A：艾翁（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi WALKING TREE-MAN with a BIG head: a small round face of pale grey-white bark, small amber eyes, a big nose, a wide grin, a huge beard of bright "
  "green leaves over his chest, two pale sage-green ram's horns curling out wide to the sides, a red white-spotted mushroom on his crown, a small wooden "
  "ring hanging by his ear, a brown wooden body with a leaf skirt and a white cloth strip, a thin branch arm on the image left holding a twig with two "
  "leaves (two gold rings at the wrist), a thin branch arm on the image right holding a red apple, two short dark red-brown bark legs on forked root "
  f"feet, red berries on the near shin; B its HEAD with the horns and the mushroom shown 8x ({P.HW} squares wide, {P.HH} tall); C a SKELETON on the "
  f"same 1254 canvas and {P.PX} px grid: green = the spine (pelvis to the base of the neck, under the leaf beard), RED = the NEAR leg (image left, in "
  "front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left, the twig hand), PURPLE = the FAR arm (image right, the apple hand), the "
  "bigger dot on each arm = the hand, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 "
  "view facing right (copy the POSE from it, never its 3D look or its long realistic legs); E (if attached) the same skeleton drawn over image A, "
  "showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg only about {LEG} squares from the hip to the sole, the twig arm about {ARM} squares from the "
  f"shoulder to the fingertips and the apple arm about {ARM2}, exactly as in image A. Lay the body along the skeleton: the wooden body, the leaf skirt "
  "and the big leaf beard along the green line, each leg along its line (bending at the dots: the dark red-brown bark, the root foot - the SAME "
  "thickness, length and colours as in image A), each arm from its shoulder along its line (thin brown branches growing from the shoulders, never "
  "floating), the twig with its two leaves in the orange hand, the red apple in the purple hand (unless the pose says the hand holds a seed or drops the "
  "apple). Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both amber eyes, the big nose, the grin, both horns, the "
  "mushroom, the wooden ring) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand, twig or apple covers "
  "the face (the eyes, the nose and the mouth); a raised arm passes beside or in front of a horn.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no vines, no seeds flying, no bushes, no glow, no motion trails), no background, no ground, no shadow, no text, no grid lines, no "
  "skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 提示词 B：小菊（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`D0_daisy.png`（定稿）、这个姿势的 `D*_league.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art ROCK GOLEM seen from the FRONT, on a 1254x1254 canvas with {P.PX} px squares (feet on y {P.SOLE_Y}) - a big "
  "hunched golem of mossy green stones and pale violet-grey stone faces with carved dark green spirals, two small white flowers and a small green "
  "crystal on the chest, a small dark grey pointed stone head sunk between the shoulders with a green clover sprout on top, two huge stone fists, short "
  "thick legs; B the original golem in this pose, seen from the front (copy the POSE from it, never its 3D look).")
a("Draw with the image generator ONE clean pixel-art picture of the golem of image A in the POSE of image B, still seen from the FRONT: a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}. The SAME golem: the same size, the same stones, colours, spirals, flowers, "
  "crystal, head and sprout; the arms are chains of stone blocks ending in the huge fists, the same thickness as in image A, only moved. Everything "
  "inside the canvas (a raised fist too).")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing. No effects (no dust, no shockwave, no cracks in the ground), no background, no ground, no shadow, no text, no grid lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in dz:
    a(f"- {name}: `{P.DAISY[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n + nd} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：艾翁每条腿从胯到脚底约 {LEG} 格、拿树枝的手臂约 {ARM} 格、拿苹果的约 {ARM2} 格，和定稿一样——腿画长了就重画。")
a("- 每张艾翁都是定稿的同一个艾翁：**同一个头（照图 B，脸朝右前方、两只琥珀色眼睛、大鼻子、笑脸、羊角、蘑菇）**、同样大的树叶胡子、"
  "同样粗的腿和树枝手臂；手臂从肩膀长出来，手、树枝、苹果没有盖住脸；姿势沿着骨架；着地的脚在 "
  f"y {P.SOLE_Y}。")
a("- 每张小菊都是定稿的同一个小菊，**正面**，大小、石块、花纹、白花、水晶、头顶嫩芽都一样；举起的拳头不出画。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/ivern-poses/`）\n")
a("- " + "、".join(f"`ivern-pose-{x}.png`" for x in names) + "；")
a("- " + "、".join(f"`ivern-daisy-{x}.png`" for x in dz) + "；")
a("- 原始生成图原样放 `outputs/ivern-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/ivern_poses_done.zip`。中间不要停，{n + nd} 张都画完再交。\n")
a("## 附图（压缩包 `ivern_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手） |")
a("| `1_head.png` | 定稿的头（8 倍，连羊角和蘑菇）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 艾翁定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |")
a(f"| `D0_daisy.png` | 小菊定稿（正面，每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `D1_{dz[0]}_league.png` … `D{nd}_{dz[-1]}_league.png` | 小菊每个姿势的英雄联盟原版那一帧（正面） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_hwei_poses / design_qiyana_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就照奇亚娜的 legs 包重画腿，再拼进 rig_ivern.py 的动作里，"
  "逐帧自查后才发合成 GIF。小菊按她自己的格子读回（PPU 1.9），对到 hd/daisy.png 的调色板。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_ivern.py）：普攻 attack = a_wind → a_throw → 定稿；种豆得瓜 skill = e_gather → e_give；"
  "根深敌固 skill2 = q_wind → q_fling；大招 ult = r_crouch → r_leap → r_call；死亡 dead = d_stagger → d_slump；跑 run = run1–4；"
  "待机 = 定稿一帧（hero_reels 做呼吸）；受击 hit = 定稿后退一格闪白。小菊（特效图，正面）：r_drop = dz_rise，r_punch = dz_wind → dz_punch，"
  "r_slam = dz_up → dz_slam，离开 = dz_wave。")
open('assets/source/ivern/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses +", nd, "Daisy; leg", LEG, "arm", ARM, ARM2)
