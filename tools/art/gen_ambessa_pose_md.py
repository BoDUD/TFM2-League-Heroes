"""Write assets/source/ambessa/POSE_PROMPTS.md from tools/art/pack_ambessa_poses.py's POSES (run from the repo root).
gen_yorick_pose_md.py's way: every limb's length in squares for Codex to count; her two blades are big props, placed
by the teal / light-blue crescents on each skeleton. No League frames (the pack was built without the client): each
pose is described in words."""
import sys
sys.path.insert(0, 'tools/art')
import pack_ambessa_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                         # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                 # shoulder to fist
ARM2 = round(sum(P.lengths("far_arm")))
L = []
a = L.append
a("# 战争女族长 安蓓萨：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 安蓓萨的造型用户已经定稿（`2_design.png` 是你第 1 步画的 A-1，头按用户要求缩小到约四分之一、身子更清楚：3/4 正面朝右的 Q 版女军阀——"
  "银白色往后梳的波浪短发、深棕色皮肤、红唇、金耳环；肩上一圈深青绿色的尖毛领；黑铁胸甲带铜色接缝、红围巾、红腰布垂到膝下；"
  "粗壮的上臂、黑色的大护臂；黑铁腿甲、黑靴；**两只手各握一把带钩的月牙形龙犬刃**（亮银刃边、深色刃身、三角镂空），"
  "刀柄连着粗铁链，两把刀垂在身体两侧）。")
a(f"> - 英雄联盟里她左右开弓地砍、横扫半圈、跳起来砸地、交叉双刀格挡再砸地、抡着铁链甩刀、闪过去按住敌人砸下、冲刺突进，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**（{n - 6} 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张都是同一个安蓓萨**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，"
  "**紫线 = 近侧的手臂**（定稿里在画面左边），**橙线 = 远侧的手臂**（定稿里在画面右边）；两条手臂末端**大一点的圆点是拳头**；"
  "**灰框 = 头的位置**（头发连脸）；**青绿色的月牙 = 近侧那只手的刀**，**浅蓝色的月牙 = 远侧那只手的刀**（月牙上的小圆圈 = 刀柄）；"
  "**深灰直线 = 铁链**（刀被甩出去、不在手里的时候，从拳头连到刀柄）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：**每条腿从胯到脚底约 {LEG} 格**；**近侧的手臂从肩膀到拳头约 {ARM} 格、远侧的约 {ARM2} 格**；"
  f"头（头发连脸）{P.HW} × {P.HH} 格；**每把刀从刀柄到刀尖约 {P.BLADE_L} 格、最宽处约 {P.BLADE_W} 格**（和定稿一样大，不放大不缩小）。"
  "骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画长了，只能重画——请画完数一数），"
  "**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；毛领、围巾、腰布跟着身子走、摆动。")
a("> - **两把刀**：照定稿的刀画（带钩的月牙、亮银刃边、深色刃身、三角镂空），**画在骨架上同颜色月牙的位置、一样大、刀尖朝同一个方向**；"
  "刀柄在拳头里（月牙的小圆圈就在拳头上）。铁链从护臂的手腕垂下来连到刀柄，平时垂成一个弯；骨架上有深灰直线的姿势，刀是被铁链甩出去的，"
  "**铁链沿着深灰线拉直**，刀飞在月牙的位置。月牙只表示刀的位置、大小和朝向，**刀的样子照定稿画，不照月牙的形状**。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、银白波浪短发、两只眼睛、红唇、金耳环）。每个姿势都是这一个头，只跟着身体移动，"
  "**不要转头、不要画成侧脸、不要重新设计**。手臂、拳头、刀**不要盖住脸**（眼睛、嘴）。")
a("> - 这一包**没有附英雄联盟原版的帧**（这次没有游戏客户端），**动作照骨架和每个姿势的文字**画。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `ambessa-pose-{name}.png` | {P.POSES[name][0]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi POWERFUL WARLORD WOMAN: SILVER-WHITE short wavy swept-back hair, DARK BROWN skin, dark red lips, a gold earring; a spiky DARK TEAL-GREEN "
  "FUR MANTLE round her shoulders; a BLACK IRON breastplate with bronze seams, a deep red scarf at the collar and a RED SASH hanging below her knees; "
  "bare muscular upper arms, huge angular BLACK GAUNTLETS; black iron leg plates and black boots; in EACH fist a HOOKED CRESCENT DRAKEHOUND BLADE "
  "(a bright silver edge, a dark flat inner plate with triangular holes), a thick iron CHAIN from each gauntlet to its blade's handle, both "
  f"blades hanging at her sides; B its HEAD shown 8x ({P.HW} squares wide, {P.HH} tall); C a SKELETON on the same 1254 canvas and {P.PX} px grid: "
  "green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the NEAR arm (on "
  "the image left in A), ORANGE = the FAR arm (on the image right in A), the bigger dot at the end of each arm = the fist, GREY BOX = where the head "
  "goes, a TEAL CRESCENT = where the near fist's blade goes, a LIGHT BLUE CRESCENT = where the far fist's blade goes (the small circle on a crescent "
  "= its handle), a DARK GREY LINE = a chain pulled straight from a fist to a blade flung out on it, the red horizontal line = the ground; D (if "
  "attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C: a 1254x1254 PNG with a real "
  f"transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight grid "
  f"from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: each leg about {LEG} squares from the hip to the sole, the near arm about {ARM} squares from the shoulder to the fist and the "
  f"far arm about {ARM2}, each blade about {P.BLADE_L} squares from the handle to the tip and {P.BLADE_W} across, exactly as in image A. Lay the body "
  "along the skeleton: the torso with the breastplate, the scarf and the sash along the green line, the fur mantle riding on the shoulders, each leg "
  "along its line (bending at the dots: the black leg plates and boots - the SAME thickness, length and colours as in image A), each arm from its "
  "shoulder along its line (bare muscular upper arms growing from the shoulders, never floating; the black gauntlets). THE BLADES: the same blades "
  "as in image A, each drawn where its crescent is - the same size, its tip pointing the same way - its handle in the fist on the crescent's small "
  "circle; the crescents only show place, size and direction: draw the blades' real shape from image A. Each chain hangs in a loop from the "
  "gauntlet to its blade's handle; where a dark grey line is drawn, that blade is flung out on its chain: the chain runs straight along the line. "
  "Never stretch or shorten a limb or a blade, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the silver hair, the face to the front-right, the eyes, the red lips, the earring) - "
  "the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, fist or blade covers the face (the eyes and the lips).")
a("The same colours as image A; one continuous 1-square near-black outline; every plate of the black armour separated by its lighter edge and its "
  "darker shadow; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.")
a("No effects (no blade trails, no afterimages, no shockwaves, no dust, no sparks, no motion lines), no background, no ground, no shadow, no text, "
  "no grid lines, no skeleton lines, no guide crescents.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][1]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、手臂约 {ARM2}–{ARM} 格、每把刀约 {P.BLADE_L} 格长，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个安蓓萨：**同一个头（照图 B：银白短发、脸朝右前方、红唇、金耳环）**、同样粗的手臂和腿、同样的毛领、甲、围巾和腰布；"
  f"两把刀在骨架上同颜色月牙的位置、一样大、刀尖朝向一样，刀柄在拳头里，铁链连着；手臂从肩膀长出来，拳头和刀没有盖住脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a("- 所有图没有特效（刀光、残影、冲击波都不画）、没有骨架线、没有网格线、没有辅助月牙。\n")
a("## 交付（`outputs/ambessa-poses/`）\n")
a("- " + "、".join(f"`ambessa-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/ambessa-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/ambessa_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `ambessa_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 拳头，月牙 = 刀） |")
a("| `1_head.png` | 定稿的头（8 倍，头发连脸）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 安蓓萨定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_skeleton.png` … `{n + 2}_{names[-1]}_skeleton.png` | 每个姿势的骨架 |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_illaoi_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂的长短粗细和刀的大小，和定稿比**，腿长了就重画腿，再拼进 rig_ambessa.py 的动作里，"
  "逐帧自查后才发合成 GIF（带技能的 GIF 也要）。")
a("- 动作安排（标签见 tools/kit/build_ambessa.py）：普攻 attack = a1_wind → a1_slash（和 a2_wind → a2_slash 交替）；"
  "狡诈横扫 skill = q_wind → q_sweep；裂地重击 slam = q2_leap → q2_slam；割裂 skill2 = e_lash1 → e_lash2；拒斥 w = w_guard → w_slam；"
  "公开处决 ult = r_grab → r_slam；龙犬之步 step = step；死亡 dead = d_kneel → d_slump；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；"
  "受击 hit = 定稿后退一格闪白。")
open('assets/source/ambessa/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, ARM2, "blade", P.BLADE_L)
