"""Write assets/source/zaahen/POSE_PROMPTS.md from tools/art/pack_zaahen_poses.py's POSES (run from the repo root).
gen_locke_pose_md.py's way: every limb's length in squares for Codex to count (Qiyana's adult-long legs, 2026-10-22);
his glaive and his wings are props, placed by the dark line with the gold end and the navy shapes on each skeleton."""
import sys
sys.path.insert(0, 'tools/art')
import pack_zaahen_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips
ARM2 = round(sum(P.lengths("far_arm")))
GL = P.G_BLADE + P.G_SPEAR
L = []
a = L.append
a("# 不落魔锋 亚恒：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 亚恒的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A 选定稿，缩到游戏大小定稿：3/4 正面朝右的 Q 版暗裔武士——"
  "浅蓝灰色皮肤、红眼睛、白金长发；金色头冠和两只高高的金角；白金板甲、金色腰带、深宝蓝长腰布；深蓝灰护腿、金护膝、光脚踩在金脚环里；"
  "**背后两只收拢的暗裔翅膀**（外面深海军蓝、里面浅白蓝带暗红纹、金色骨架）垂到小腿；"
  "**一把比他还长的金色暗裔长刀**斜在身前：近侧那只手（画面左上、胸口旁）握在刀杆上，刀刃一头在画面左上，矛头一头在画面右下，"
  "远侧那只手在画面右边腰旁握着刀杆）。`2b_wings.png` 是第 0 步的 B（同一个人展开翅膀、举刀），**翅膀张开的姿势照它的翅膀画**。")
a(f"> - 英雄联盟里他抡长刀横扫、两连斩、蹲下再往上挑、往前直刺再拽回来、压低身子冲刺后绕身一斩、展翼升空再落地插刀、倒下后单膝跪起复活，"
  f"这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **{n} 个姿势**（{n - 6} 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。"
  "待机、挨打、复活站起之后的样子我从定稿和 B 本身来做，不用画。")
a(f"> - **每张都是同一个亚恒**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆的金腰带到脖子根），"
  "**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 近侧的手臂（主要握刀的那只）**，"
  "**橙线 = 远侧的手臂**；手臂线的第一个点是肩膀，**大一点的圆点是手**；**灰框 = 头的位置**（金角、头冠、头发、脸）；"
  "**深色长线 = 长刀的刀杆**，**粗的金色一段 = 刀刃那一头**（弯弯的金色大刃），**细的金色一小段 = 矛头那一头**（没有手握着的时候它就是掉落 / 飞出去的长刀）；"
  "**深蓝半透明的形状 = 翅膀**（一块 = 收拢垂在背后；两块 = 向两边张开，后面那块暗一点）。"
  "`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版大头、高大宽肩——**每条腿从胯到脚底约 {LEG} 格**；**手臂从肩膀到手指尖约 {ARM}–{ARM2} 格**；"
  f"头（金角、头冠、头发连脸）{P.HW} × {P.HH} 格；**长刀从刀刃尖到矛头尖约 {GL} 格**（比他人还长，和定稿一样，不放大不缩短；手握在刀杆上的位置可以变）。"
  "骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，"
  "只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩甲里长出来，不能悬空；腰布、翅膀跟着身子走。")
a("> - **翅膀和腰布不能躺在地上**：收拢的翅膀最低到小腿、翅尖离地；跑和冲刺时翅膀往后掠；张开时照 `2b_wings.png`。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只金角、头冠、两只红眼睛一样高、冷脸）。"
  "每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、长刀**不要盖住脸**（眼睛和嘴）；"
  "从头附近经过时画在头**后面**。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作的感觉照它**，长相照定稿。英雄联盟的模型在空中的几个片段里长刀会掉在地上"
  "（渲染的问题），**长刀一律照骨架的深色长线画**；英雄联盟的他手臂长、大人比例，我们的是 Q 版大头：**照骨架的长短和长刀、翅膀的位置画，不照原版的长短**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `zaahen-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`；翅膀张开的姿势再加 `2b_wings.png`，"
  "有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi TALL PROUD DARKIN WARRIOR with a BIG head: PALE BLUE-GREY skin, RED eyes, long WHITE-BLOND hair, a GOLD CIRCLET with TWO TALL GOLDEN "
  "HORNS; WHITE-AND-GOLD plate armour on the chest, shoulders and forearms, a gold belt, a long DEEP ROYAL BLUE loincloth, dark blue-grey leggings "
  "with gold knee guards, bare feet in gold ankle bands; TWO FOLDED DARKIN WINGS hanging from his back to his calves (dark navy outside, pale "
  "white-blue inside with dark red veins, a gold bone edge); a GLAIVE LONGER THAN HE IS held diagonally in front of him: a dark shaft, a big "
  "CURVED GOLDEN BLADE at one end (upper left), a golden SPEAR POINT at the other (lower right), his NEAR hand on the shaft by his chest (upper "
  f"left of his body), his FAR hand on the shaft at his far hip; B its HEAD shown 8x ({P.HW} squares wide, {P.HH} tall: the horns, the circlet, "
  f"the hair, the face); C a SKELETON on the same 1254 canvas and {P.PX} px grid: green = the spine (the gold belt to the base of the neck), RED = "
  "the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the NEAR arm, ORANGE = the FAR arm, each arm line starting at the "
  "shoulder, the bigger dot on each arm = the hand, GREY BOX = where the head goes, the LONG DARK LINE = the glaive's shaft with its THICK GOLD "
  "END = the curved blade and its THIN GOLD END = the spear point (a glaive no hand holds is falling or flying), the TRANSLUCENT NAVY SHAPES = the "
  "wings (one shape = folded behind him; two shapes = spread out to both sides, the far one darker), the red horizontal line = the ground; D the "
  "original character in this pose, 3/4 view facing right (copy the feel of the POSE from it, never its 3D look or its long realistic limbs; "
  "where its glaive lies on the ground the skeleton's glaive line rules); E (if attached) the wings-spread picture of the same character: the "
  "shape and colours of his OPEN wings; F (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg about {LEG} squares from the hip to the sole, each arm about {ARM}-{ARM2} squares from the "
  f"shoulder to the fingertips, the glaive about {GL} squares from the blade's tip to the spear point, exactly as in image A. Lay the body along the "
  "skeleton: the armoured torso and the gold belt along the green line, the blue loincloth moving with the body (never lying on the ground), each "
  "leg along its line (bending at the dots: the dark leggings, the gold knee guard, the bare foot - the SAME thickness, length and colours as in "
  "image A), each arm from its shoulder plate along its line (the gold-and-white forearm armour and the hand, never floating). THE GLAIVE: the same "
  "glaive as in image A drawn exactly on the dark line - the curved golden blade on the thick gold end, the spear point on the thin gold end, "
  "the hands gripping the shaft where the hand dots are. THE WINGS: on the navy shapes - folded like image A when there is one shape, spread like "
  "image E when there are two. Where the glaive or an arm passes the grey box it goes BEHIND his head. Never stretch or shorten a limb or the "
  "glaive, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (both golden horns, the circlet, the white-blond hair, the face to the front-right, "
  "both red eyes at the same height) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or glaive "
  "covers the face (the eyes and the mouth).")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no blade trails, no dark red mist, no dash trail, no shockwave, no revive light, no dust, no motion lines), no background, no "
  "ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、手臂约 {ARM}–{ARM2} 格、长刀约 {GL} 格，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个亚恒：**同一个头（照图 B，两只金角、头冠、白金长发、两只红眼睛一样高、脸朝右前方）**、同样粗的手臂和腿、"
  "同样的白金板甲和深宝蓝腰布；长刀在骨架深色长线的位置（刀刃在粗金色那一头）；翅膀在深蓝形状的位置（收拢或照 B 张开）；"
  f"手和长刀没有盖住脸；翅膀和腰布不拖地；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a("- 所有图没有特效（刀光、暗红血雾、冲刺残影、冲击波、复活的光都不画）、没有骨架线、没有网格线、没有辅助形状。\n")
a("## 交付（`outputs/zaahen-poses/`）\n")
a("- " + "、".join(f"`zaahen-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/zaahen-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/zaahen_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `zaahen_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，深色长线 + 金色两头 = 长刀，深蓝形状 = 翅膀） |")
a("| `1_head.png` | 定稿的头（8 倍，金角、头冠、头发、脸）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 亚恒定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a("| `2b_wings.png` | 第 0 步的 B（8 倍）：翅膀张开的样子 |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_locke_poses / design_trundle_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂的长短粗细和长刀的长短，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_zaahen.py 的动作里，"
  "逐帧自查后才发合成 GIF（带技能的 GIF 也要）。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_zaahen.py）：普攻 attack = a_wind → a_sweep → 定稿；暗裔长刀 skill = q_cut1 → q_cut2（两连斩）；"
  "再按 skill_up = q_crouch → q_up（挑飞）；厄影回锋 skill2 = w_thrust → w_pull（主包末尾接 e_spin：并进 W 的绕身斩）；"
  "赤金突袭（附加包自己的 E，skill3 标签）= e_dash → e_spin；大赦 ult = r_crouch → r_rise → r_stab；死亡 dead = d_fall → d_down；"
  "被动复活（附加包：禁锢期间的画面 rv_rise）= d_down → rv_kneel → B（展翼举刀）；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。")
open('assets/source/zaahen/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, ARM2, "glaive", GL)
