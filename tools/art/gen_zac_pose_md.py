"""Write assets/source/zac/POSE_PROMPTS.md from tools/art/pack_zac_poses.py's POSES (run from the repo root): every
limb's length in squares for Codex to count (Qiyana's adult-long legs, 2026-10-22); the arms League stretches like rubber
named per pose; the head box (the head with the tendril) pasted in every pose but the squashed / melted ones, which get a
box for the whole body."""
import sys
sys.path.insert(0, 'tools/art')
import pack_zac_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to finger tips
ARM2 = round(sum(P.lengths("far_arm")))
BOXED = [x for x in names if "box" in P.POSES[x][3]]
L = []
a = L.append
a("# 生化魔人 扎克：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 扎克的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-1：3/4 正面朝右的扎克——半透明亮绿色黏液做的大块头，身体里深绿色的纹路，"
  "驼着背，小小的头埋在两个大肩膀中间，两只发黄光的眼睛，咧开的大嘴和一排深色尖牙，头顶一根深蓝绿的弯触须（末端一个圆疙瘩），"
  "两条又粗又长的手臂垂到地上、三根粗手指的大手，两条短粗的腿）。")
a(f"> - 英雄联盟里扎克出拳、把手臂像橡皮一样拉长去抓人、举起来砸地、按地拉成弹弓飞出去、弹跳压扁、死时化成一滩，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**，**每个一张图**。待机、跑步、挨打我从定稿本身来做，不用画。")
a(f"> - **每张都是同一个扎克**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到头的底部），**红线 = 近侧的腿（画面左边那条）**，"
  "**蓝线 = 远侧的腿（画面右边那条）**，**橙线 = 近侧的手臂（定稿里在画面左边、垂到地上的那条大手臂）**，**紫线 = 远侧的手臂（定稿里在画面右边）**；"
  "两条手臂上**大一点的圆点是手腕**，线的末端是指尖；**灰框 = 头的位置**（头连触须）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。"
  "扎克的身体很宽：两个大肩膀、厚厚的胸口和后背都要画出来，脊柱只是中线。")
a(f"> - **长短要数格子**：腿很短——**每条腿从胯到脚底约 {LEG} 格**；**手臂很长：近侧的从肩膀到指尖约 {ARM} 格、远侧的约 {ARM2} 格**；"
  f"灰框（头 + 触须）{P.HW} × {P.HH} 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折**"
  "（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。")
a("> - **只有姿势那一行写了“拉长”的手臂**才像橡皮一样拉长（扎克的能力）：那条手臂沿着骨架变长，**粗细和定稿一样或稍细一点**，"
  "颜色、纹路照定稿，大手照定稿的大小；其他手臂、腿一律照定稿的长短。")
a("> - **灰框里照 `1_head.png` 一格一格画**：扎克的头（两只发黄光的眼睛、咧开的大嘴和尖牙、触须）。每个姿势都是这一个头，只跟着身体移动，"
  "**不要转头、不要画成侧脸、不要重新设计**。手臂、大手**不要盖住脸**。")
a(f"> - **绿色方框**（{'、'.join(BOXED)} 这 {len(BOXED)} 张没有骨架）：扎克被压扁 / 融化了，**整个身体画在绿框里、填满它**，框的底边就是地面；"
  "头按姿势那一行画（压扁时眼睛和嘴照样露出来；融化时眼睛半闭 / 闭成一道线），颜色照定稿。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的扎克腿长、头小；"
  "我们的是定稿的比例：头埋在肩膀中间、身子宽、腿短，**照骨架的长短画，不照原版的长短**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `zac-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a HULKING, HUNCHED brute made of TRANSLUCENT BRIGHT GREEN SLIME with dark green veins inside, a small head sunk between huge shoulders with two "
  "glowing yellow eyes and a wide grin of dark jagged teeth, a dark blue-green tendril with a round knob curling up from the top of his head, two "
  "huge long arms hanging to the ground with big three-fingered hands, two short thick legs; B its HEAD BOX shown 8x "
  f"({P.HW} squares wide, {P.HH} tall): his head with the tendril; C a SKELETON (or, for a squashed / melted pose, a GREEN BOX) on the same 1254 "
  f"canvas and {P.PX} px grid: green line = the spine (pelvis to the base of the head), RED = the NEAR leg (image left), BLUE = the FAR leg (image "
  "right), ORANGE = the NEAR arm (image left in A, the big arm hanging to the ground), PURPLE = the FAR arm (image right in A), the bigger dot on "
  "each arm = the wrist (the line ends at the finger tips), GREY BOX = where the head box goes, GREEN BOX = the space his whole squashed or melted "
  "body fills, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never "
  "its 3D look or its long realistic legs and small head); E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of C (and image D): a 1254x1254 PNG with a "
  f"real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: each leg only about {LEG} squares from the hip to the sole, the near arm about {ARM} squares from the shoulder to the finger "
  f"tips and the far arm about {ARM2}, exactly as in image A - EXCEPT an arm THE POSE line says is STRETCHED: that arm follows its longer line like "
  "rubber, the same thickness as in A or a little thinner, its big hand the same size. Lay the body along the skeleton: his broad hunched body, the "
  "huge shoulders and back round the green line (the spine is only its middle), each short thick leg along its line (bending at the dots, the SAME "
  "thickness, length and colours as in A), each long arm from its shoulder along its line (the big three-fingered hand at the end; growing from the "
  "shoulders, never floating). Never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD BOX: copy image B SQUARE FOR SQUARE into the grey box - his face to the front-right with both glowing yellow eyes, the grin and the "
  "teeth, the tendril - the same in every pose, only moved, never turned, never redrawn as a profile. No arm or hand covers the face. "
  "With a GREEN BOX instead: draw his whole body squashed / melted inside the box and filling it, the face as THE POSE line says.")
a("The same colours as image A (the bright green slime in 4 shades with few big yellow-green highlights and dark green veins inside, the yellow "
  "eyes, the dark teeth, the dark blue-green tendril); one continuous 1-square near-black outline; no stray single squares, no dithering, no "
  "gradients, no glow, no blur, no anti-aliasing.")
a("No effects (no flying slime blobs, no splashes, no puddle under him except the pose that IS a puddle, no dust, no motion trails), no "
  "background, no ground, no shadow, no text, no grid lines, no skeleton lines, no box guide.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、近侧手臂约 {ARM} 格、远侧约 {ARM2} 格，和定稿一样——只有姿势里写了“拉长”的那条手臂更长；腿画长了就重画。")
a("- 每张都是定稿的同一个扎克：**同一个头框（照图 B：脸朝右前方、两只发黄光的眼睛、咧开的大嘴和尖牙、触须）**、同样宽的身体、同样粗的手臂和腿；"
  f"手臂从肩膀长出来，大手没有盖住脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a(f"- 绿框那 {len(BOXED)} 张（{'、'.join(BOXED)}）：整个身体在绿框里、填满它，底边贴地。")
a("- 所有图没有特效、没有骨架线、没有网格线、没有框线。\n")
a("## 交付（`outputs/zac-poses/`）\n")
a("- " + "、".join(f"`zac-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/zac-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/zac_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `zac_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手腕，灰框 = 头框） |")
a("| `1_head.png` | 定稿的头框（8 倍：头、眼睛、嘴、触须）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 扎克定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架或绿框（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_nunu_poses 的做法：按头框的大小定比例，头框换成定稿的头框，绿框的三张除外），"
  "颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_zac.py，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_zac.py）：普攻 attack = a_wind → a_punch → 定稿；延伸打击 skill = q_wind → q_reach（伸着），"
  "skill_slam = q_lift → q_slam；橡筋弹弓 skill2 = e_plant → e_pull（蓄力），skill2_fly = e_fly，skill2_land = e_land → 定稿；"
  "动感弹球 ult（每一跳）= r_crouch → r_jump → r_ball → r_jump，ult_land = r_splat → r_crouch；死亡 dead = d_stagger → d_melt → d_puddle；"
  "待机 = 定稿一帧（hero_reels）；跑 run = 定稿自己的腿（布隆 / 沃里克的走法）；受击 hit = 定稿后退一格闪白。")
open('assets/source/zac/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, ARM2, "boxed", BOXED)
