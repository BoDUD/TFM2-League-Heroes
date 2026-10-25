"""Write assets/source/rumble/POSE_PROMPTS.md from tools/art/pack_rumble_poses.py's POSES (run from the repo root).
gen_yorick_pose_md.py's way: every limb's length in squares for Codex to count; his mech is one rigid body (the hull, the
pilot, the rocket pods) set by the tan / red-brown boxes, the mace and the cannon placed by the dark circle and the gold
bar on each skeleton."""
import sys
sys.path.insert(0, 'tools/art')
import pack_rumble_poses as P
names = list(P.POSES)
n = len(names)
run = [x for x in names if x.startswith("run")]
dead = [x for x in names if x.startswith("d_")]
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths(P.REST["mace_arm"])))                            # shoulder to the mechanical hand
UP = round(P.lengths(P.REST["cannon_arm"])[0])                             # shoulder to the cannon's elbow
CAN = round(P.CANNON_L)
BALL = round(2 * P.BALL_R)
L = []
a = L.append
a("# 机械公敌 兰博：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 兰博的造型用户已经定稿（`2_design.png` 是你第 1 步画的 B-1：3/4 正面朝右的 Q 版约德尔人坐在机甲里——蓝毛大头、亮蓝莫西干、"
  "额头上推着的红镜片金框护目镜、黄眼睛、坏笑；黄铜色带锈的敞口驾驶舱、往画面右边伸的长喷火炮管（红箍、绕着黑管子）、"
  "画面左边那条机械手臂握着的**带刺黑铁球**、背上两个红头火箭舱、短粗的黑色关节腿和红色圆盘脚）。")
a(f"> - 英雄联盟里他抡铁球砸人、端着喷火炮喷火、射鱼叉、蹲下发射火箭、翻倒，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**（{n - len(run) - len(dead)} 个动作 + {len(run)} 帧跑步 + {len(dead)} 帧死亡），**每个一张图**。"
  "待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张都是同一个兰博**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：**棕黄色的框 = 驾驶舱**（机甲的身子，连同坐在里面的兰博）、**红棕色的框 = 背上的火箭舱**、"
  "**灰框 = 兰博的头**；绿线 = 机身的中轴（驾驶舱底部中间往上）；**机甲是一整块硬的**：驾驶舱、驾驶员、火箭舱一起倾斜、一起移动，不变形。"
  "**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，扁的椭圆 = 红色圆盘脚；"
  "**紫线 = 握铁球的机械手臂**（定稿里在画面左边），**深色圆 = 带刺铁球**；**橙线 = 拿喷火炮的那条手臂**（定稿里在画面右边），"
  "**金色粗条 = 喷火炮管**（圆圈那头是炮口）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线、每个框对应机甲的哪一部分。")
a(f"> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底约 {LEG} 格**；**机械手臂从肩膀到手约 {ARM} 格**，铁球连尖刺约 {BALL} 格宽；"
  f"**拿炮的手臂从肩膀到炮的后端约 {UP} 格**，**喷火炮管约 {CAN} 格长、{round(P.CANNON_W)} 格粗**；头（连耳朵和莫西干）{P.HW} × {P.HH} 格。"
  "骨架就是按定稿量的：**腿、手臂、炮管沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，"
  "只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从机身长出来，不能悬空。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只黄眼睛一样高、坏笑、护目镜推在额头上、莫西干往后翘）。每个姿势都是这一个头，"
  "只跟着机身移动，**不要转头、不要画成侧脸、不要重新设计**。机甲歪了头也不歪。手臂、铁球、炮管**不要盖住脸**（眼睛、嘴）。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。原版是写实比例，铁球拿在**身前**、喷火炮横在**近侧**；"
  "我们的定稿铁球在**画面左边（身后）**、炮管往**画面右边（身前）**伸——**照骨架上的位置画，不照原版的左右**，只学原版的动势"
  "（机身怎么前倾后仰、腿怎么迈、铁球怎么举起砸下、炮口指向哪里）。原版死亡时驾驶员会消失，我们的**头一直在驾驶舱上面**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 原版那一帧 | 姿势 |")
a("|---|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `rumble-pose-{name}.png` | `{P.POSES[name][0]}` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi blue-furred YORDLE with a BIG head riding a junkyard MECH: a bright blue mohawk swept back, big pointed ears, red-lensed gold-rimmed goggles "
  "pushed up on the forehead, yellow eyes, a cheeky grin, a brown leather jacket; he sits in an open rusty BRASS COCKPIT; a LONG FLAMETHROWER CANNON "
  "(brass with red bands, black hoses wound round it, a black muzzle) reaching forward to the image right; on the image left a black jointed "
  "MECHANICAL ARM with brass plates gripping a SPIKED BLACK IRON BALL (silver spikes); two ROCKET PODS with red tips on its back; short thick black "
  f"jointed legs with gold gears and RED DISC FEET; B its HEAD shown 8x ({P.HW} squares wide, {P.HH} tall); C a SKELETON on the same 1254 canvas and "
  f"{P.PX} px grid: the TAN BOX = the cockpit hull (with the pilot in it), the RED-BROWN BOX = the rocket pods, the GREY BOX = where the head goes, "
  "green = the hull's middle axis - the mech is ONE RIGID BODY: hull, pilot and pods tilt and move together, never bent; RED = the NEAR leg (image "
  "left), BLUE = the FAR leg (image right), the flat ellipses = the red disc feet; PURPLE = the MECHANICAL ARM (on the image left in A) with the DARK "
  "CIRCLE = the spiked iron ball; ORANGE = the CANNON ARM (on the image right in A) with the THICK GOLD BAR = the flamethrower cannon (the ring = its "
  "muzzle); the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the MOTION from it - how the "
  "body pitches, the legs stride, the ball rises and falls, where the muzzle points - never its 3D look, its realistic proportions or its sides: in "
  "it the ball is held in front and the cannon across the near side, ours follow the skeleton C); E (if attached) the same skeleton drawn over image "
  "A, showing which line and box is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg only about {LEG} squares from the hip to the sole, the mechanical arm about {ARM} squares from "
  f"the shoulder to the hand, the spiked ball about {BALL} squares across, the cannon arm about {UP} squares to the cannon and the cannon about {CAN} "
  "squares long, exactly as in image A. Draw the cockpit hull with the pilot and the rocket pods as ONE rigid piece in the tan and red-brown boxes "
  "(tilted as the boxes are, the same shape and size as in image A); each leg along its line (bending at the dots: the black joints, the gold gears, "
  "the red disc foot on its ellipse - the SAME thickness, length and colours as in image A); the mechanical arm from its shoulder along the purple "
  "line with the spiked ball on the dark circle; the cannon arm along the orange line and the cannon exactly on the gold bar, its muzzle at the ring. "
  "Never stretch or shorten a limb or the cannon, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the mohawk, the ears, the goggles on the forehead, the face to the front-right, both "
  "yellow eyes at the same height, the grin) - the same head in every pose, only moved, never turned, never tilted, never redrawn as a profile. No arm, "
  "ball or cannon covers the face (the eyes and the grin).")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no fire, no flames, no smoke, no sparks, no electricity, no harpoon, no rockets in the air, no rocket trails, no shield, no dust, no "
  "motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide boxes.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、机械手臂约 {ARM} 格、喷火炮管约 {CAN} 格长，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个兰博：**同一个头（照图 B，脸朝右前方、两只黄眼睛一样高、坏笑、护目镜、莫西干）**、同一个驾驶舱和火箭舱（整块跟着框倾斜，不变形）、"
  f"同样粗的腿和手臂、红色圆盘脚；铁球在深色圆上、炮管在金色粗条上；手臂从机身长出来，铁球、炮管没有盖住脸；着地的脚在 y {P.SOLE_Y}。")
a("- 所有图没有特效（火焰、烟、电光、鱼叉、飞出去的火箭、护盾都不画）、没有骨架线、没有网格线、没有辅助框。\n")
a("## 交付（`outputs/rumble-poses/`）\n")
a("- " + "、".join(f"`rumble-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/rumble-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/rumble_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `rumble_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线、每个框对应哪一部分） |")
a("| `1_head.png` | 定稿的头（8 倍，连耳朵和莫西干）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 兰博定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂、炮管的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_rumble.py 的动作里，"
  "逐帧自查后才发合成 GIF（带技能的 GIF 也要）。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_rumble.py）：普攻 attack = a_wind → a_smash → 定稿；纵火盛宴 skill = q_aim → q_spray"
  "（喷火时保持 q_spray，火焰由 rig_rumble.py 画进他自己的帧里）；电子鱼叉 skill2 = e_aim → e_recoil；恒温灼烧 ult = r_crouch → r_launch；"
  "破碎护盾（W）没有自己的动作（护盾是贴在他身上的图）；死亡 dead = " + " → ".join(dead) + "；跑 run = " + "–".join(run) +
  "；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。")
open('assets/source/rumble/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, "cannon arm", UP, "cannon", CAN, "ball", BALL)
