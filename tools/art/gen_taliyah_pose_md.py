"""Write assets/source/taliyah/POSE_PROMPTS.md from tools/art/pack_taliyah_poses.py's POSES (run from the repo root).
The prompt gives every limb's length in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22)."""
import sys
sys.path.insert(0, 'tools/art')
import pack_taliyah_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.REST["near_leg"][-1][1] - P.REST["near_leg"][0][1])        # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips
L = []
a = L.append
a("# 岩雀 塔莉垭：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 塔莉垭的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右——小麦色皮肤、往上盘起的棕色大头发和金色发饰（中间奶白石头）、"
  "米白石片披肩、深靛紫上衣和金边、红色长外套和两条挂灰石头的垂带、紫袖子米白护腕、棕色长靴）。英雄联盟里她召石头扔、推出一串石子、撒石雷、"
  "按地掀人、唤石墙、蹲在大石头上冲浪——这些靠挪动定稿本身的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势，每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张图都是同一个塔莉垭**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边）**；"
  "**灰框 = 头的位置**；**棕色圆角框 = 冲浪的大石头**（只在冲浪的三个姿势里）。`0_design_skeleton.png` 是同样的骨架画在定稿上，"
  "看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：**头 {P.HW} × {P.HH} 格**（Q 版，盘起的大头发占了很多）；**每条腿从胯到脚底约 {LEG} 格**，**手臂从肩膀到指尖约 {ARM} 格**"
  f"（手臂很短，比头的宽度还短）；**冲浪的大石头约 {round(P.ROCK_W)} 格宽、{round(P.ROCK_H)} 格高**。骨架就是按定稿量的：**腿、手臂沿着骨架画，"
  "长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄腿画错了只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。"
  "手臂从肩膀（披肩下面）长出来，不能悬空。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、盘起的棕色大头发、金色发饰、两只琥珀色眼睛都看得见、小红嘴）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**。手臂和手**不要盖住脸**（举起来的手臂画在头发两边的外面或前面，但不挡眼睛和嘴）。")
a("> - **两条红垂带和末端的灰石头是布**：跟着动作甩动（往后飘、往上扬、摊在地上），但长短、宽窄、石头的数量和定稿一样。"
  "**米白石片披肩**永远在肩膀上，跟着身体走。")
a("> - **冲浪的石头**照 `2b_surf_picture.png`（第 0 步你画的 B：一块棕色大岩石，裹着红布，布上有金边）：画在棕色圆角框的位置，"
  "**她两只脚踩在石头顶上**，石头底在地面线上；石头本身不动，只有她的身子和手臂在三张里换姿势。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟里她有时跳起来、转过身——"
  "**我们的永远是 3/4 正面朝右**，只照它的手臂、身体和垂带的动作。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `taliyah-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`；冲浪的三个姿势再加 "
  "`2b_surf_picture.png`；有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "THE STONEWEAVER GIRL: a young desert girl with TANNED skin, a BIG SWEPT-UP MASS OF BROWN HAIR piled high with a ROUND GOLD ORNAMENT (a cream stone "
  "in it), amber eyes, a CREAM STONE-PLATE MANTLE over her shoulders, a DARK INDIGO TUNIC with GOLD trim, a long RED COAT whose TWO RED PANELS hang to "
  "her shins each ending in GREY STONES, PURPLE SLEEVES with CREAM CUFFS, dark indigo leggings and BROWN BOOTS; B its HEAD shown 8x "
  f"({P.HW} x {P.HH} squares); C a SKELETON on the same 1254 canvas and {P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = the "
  "NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right), GREY BOX = "
  "where the head goes, a BROWN ROUNDED BOX (surf poses only) = her big boulder, the red horizontal line = the ground; D the original character in this "
  "pose (copy the POSE, the arms and the panels' swing from it - never its 3D look, its realistic proportions or a turned back); E (surf poses) her "
  "boulder as drawn before: a big brown rock wrapped in RED CLOTH with a gold edge; F (if attached) the same skeleton drawn over image A, showing which "
  "line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y} (in the surf poses the boulder's bottom is on that line and her feet stand "
  "on its top).")
a(f"COUNT THE SQUARES: the head {P.HW} x {P.HH} squares; each leg about {LEG} squares from the hip to the sole, each arm about {ARM} squares from the "
  f"shoulder to the fingertips (short chibi arms), the boulder about {round(P.ROCK_W)} x {round(P.ROCK_H)} squares, exactly as in images A and E. Lay "
  "the body along the skeleton: the indigo tunic with its gold trim and the red coat along the green line, the stone mantle on the shoulders, each leg "
  "along its line (bending at the dots: the indigo legging and the brown boot - the SAME thickness, length and colours as in image A), each arm from its "
  "shoulder along its line (the arms grow from under the mantle, never floating; purple sleeve, cream cuff, tanned hand). The two red panels and their "
  "grey end stones are cloth: they swing with the pose but keep their length, width and stones. Never stretch or shorten a limb, never paste a straight "
  "leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, the piled brown hair and its gold ornament, both amber eyes "
  "at the same height, the small red mouth) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind. No arm "
  "or hand covers the face (raised arms go outside or in front of the hair's sides, never over the eyes or the mouth).")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no flying rocks, no rising stones, no mines, no wall, no dust, no motion lines), no background, no ground, no shadow, no text, no grid "
  "lines, no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：头 {P.HW} × {P.HH} 格、每条腿从胯到脚底约 {LEG} 格、手臂约 {ARM} 格、冲浪石约 {round(P.ROCK_W)} × {round(P.ROCK_H)} 格，"
  "和定稿一样——腿或手臂画长了就重画。")
a("- 每张都是定稿的同一个塔莉垭：**同一个头（照图 B，脸朝右前方、两只眼睛、金色发饰）**、同样粗的腿和手臂、同样的披肩和垂带；手臂从肩膀长出来，"
  f"手没有盖住脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}（冲浪：石头底在 y {P.SOLE_Y}，脚踩在石头顶上）；没有一张是背影或侧脸。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/taliyah-poses/`）\n")
a("- " + "、".join(f"`taliyah-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/taliyah-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/taliyah_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `taliyah_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |")
a("| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a("| `2b_surf_picture.png` | 第 0 步的 B：冲浪的大石头长什么样（只照石头，她的大小照定稿） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_singed_poses / design_aurora_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿和手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_taliyah.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_taliyah.py）：普攻 attack = a_wind → a_throw；石穿 skill = q_raise → q_cast；"
  "岩突 + 撒石阵 skill2 = e_raise → e_sweep → w_crouch → w_push；墙幔 ult = r_call → surf1-3（踩墙冲浪）；移动 run = surf1 → surf2 → surf3（被动冲浪）；"
  "死亡 dead = d_stagger → d_down；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。")
open('assets/source/taliyah/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM)
