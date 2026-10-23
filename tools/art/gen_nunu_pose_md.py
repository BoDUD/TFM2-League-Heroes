"""Write assets/source/nunu/POSE_PROMPTS.md from tools/art/pack_nunu_poses.py's POSES (run from the repo root): every
limb's length in squares for Codex to count (Qiyana's adult-long legs, 2026-10-22); the snowball a prop placed by the
white disc on the skeletons that have it; the head box (Nunu, the antlers, Willump's head) pasted in every pose."""
import sys
sys.path.insert(0, 'tools/art')
import pack_nunu_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to claw tips
ARM2 = round(sum(P.lengths("far_arm")))
BALLS = sorted({round(s[3]["ball_r"] * 2) for s in P.POSES.values() if "ball_r" in s[3]})
L = []
a = L.append
a("# 雪原双子 努努和威朗普：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 努努和威朗普的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-2：3/4 正面朝右的 Q 版大雪人威朗普——淡蓝白毛、蓝色螺旋纹、"
  "发蓝光的眼睛、棕鼻头、大笑嘴、粉耳朵、深蓝爪子和短腿、身后蓬松的尾巴，头上一对棕色大鹿角；他头上骑着小男孩努努——蓝兜帽、粉猫耳、"
  "米白毛球、橙斗篷白毛边、蓝宝石扣、棕手套扶着鹿角）。")
a(f"> - 英雄联盟里威朗普拍爪子、张大嘴扑上去咬、推着大雪球冲、举手召唤暴风雪、砸地，努努在他头上扔雪球，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**（{n - 4} 个动作 + 4 帧跑步），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张都是同一个努努和威朗普**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架是威朗普的**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，"
  "**蓝线 = 远侧的腿（画面右边那条）**，**橙线 = 近侧的手臂（定稿里在画面左边）**，**紫线 = 远侧的手臂（定稿里在画面右边）**；"
  "两条手臂上**大一点的圆点是手（爪子）**；**灰框 = 头的位置**（威朗普的头连鹿角，再加上骑在上面的努努）；**白色圆盘 = 雪球的位置和大小**（只有推雪球的几个姿势有）。"
  "`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底约 {LEG} 格**；**手臂长：近侧的从肩膀到爪尖约 {ARM} 格、远侧的约 {ARM2} 格**；"
  f"灰框（头 + 鹿角 + 努努）{P.HW} × {P.HH} 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**"
  "（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。")
a(f"> - **雪球**：一个**压实的大白雪球**（白色 3–4 档，背光面淡冰蓝，上面几处凹凸和雪块），**画在白色圆盘的位置，和圆盘一样大**"
  f"（直径约 {' / '.join(str(b) for b in BALLS)} 格）；威朗普的两只手放在骨架的圆点上——**爪子按在雪球边上**推着它。")
a("> - **灰框里照 `1_head.png` 一格一格画**：威朗普的头（两只发蓝光的眼睛、棕鼻头、大笑嘴、粉耳朵）、两边张开的鹿角、骑在上面的努努"
  "（朝右前方、两只蓝眼睛、咧嘴笑）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。"
  "**例外**写在姿势里：张大嘴扑 / 咬（威朗普的嘴）、扔雪球 / 举手（努努的手臂）、趴倒（努努从头上掉下来）。手臂、爪子、雪球**不要盖住两张脸**。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的威朗普是高大的雪人、手臂腿都长；"
  "我们的是 Q 版：头大、身子圆、腿短，**照骨架的长短画，不照原版的长短**。原版有几帧努努飞到威朗普头上方去了（扔雪球、推雪球、大招），"
  "**我们的努努一直骑在威朗普头上**（趴倒那一下除外）。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `nunu-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi BIG ROUND PALE-BLUE YETI with white fluffy fur on the head, chest and forearms, blue swirl markings, two glowing blue eyes, a brown nose, a "
  "wide grin with white pointed teeth and two small tusks, pink ears, long arms with big dark blue claws, short deep blue legs, a fluffy tail behind, "
  "a pair of big brown wooden antlers spreading from his head; and a BOY riding on his head holding the antlers - a blue furry hood with pink-lined cat "
  "ears and a cream pompom, a brown fringe, big blue eyes, a grin, an orange cape with white fur trim and a blue gem clasp, brown gloves; B its HEAD BOX "
  f"shown 8x ({P.HW} squares wide, {P.HH} tall): the yeti's head with the antlers and the boy on it; C a SKELETON of the YETI on the same 1254 canvas and "
  f"{P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), ORANGE = the "
  "NEAR arm (image left in A), PURPLE = the FAR arm (image right in A), the bigger dot on each arm = the clawed hand, GREY BOX = where the head box "
  "goes, the WHITE DISC (only in some poses) = where the big snowball goes and how big it is, the red horizontal line = the ground; D the original "
  "character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its long realistic limbs, or the boy flying off the yeti); "
  "E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg only about {LEG} squares from the hip to the sole, the near arm about {ARM} squares from the "
  f"shoulder to the claw tips and the far arm about {ARM2}, exactly as in image A. Lay the body along the skeleton: the yeti's round furry body along "
  "the green line, each short deep blue leg along its line (bending at the dots, the SAME thickness, length and colours as in image A), each long arm "
  "from its shoulder along its line (the white fur on the forearm, the dark blue claws on the hand dot; growing from the shoulders, never floating). "
  "THE SNOWBALL (only where the white disc is): a big packed white snowball exactly on the disc, the same size, white in 3-4 shades with pale icy-blue "
  "shading on its far side and a few lumps of snow; the claws on the hand dots press on its rim. Never stretch or shorten a limb, never paste a "
  "straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD BOX: copy image B SQUARE FOR SQUARE into the grey box - the yeti's face to the front-right with both glowing eyes, the nose and the grin, "
  "the antlers, the boy riding on top with his face and both eyes - the same in every pose, only moved, never turned, never redrawn as a profile, "
  "except where THE POSE line below changes the yeti's mouth or the boy's arms. No arm, claw or snowball covers either face.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no snow powder, no flying snowballs except the one the pose names, no blizzard, no ice, no dust, no motion trails), no background, no "
  "ground, no shadow, no text, no grid lines, no skeleton lines, no disc guide.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、近侧手臂约 {ARM} 格、远侧约 {ARM2} 格，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个努努和威朗普：**同一个头框（照图 B：威朗普的脸朝右前方、两只发光的眼睛、大笑嘴；鹿角；努努两只蓝眼睛）**、"
  f"同样粗的手臂和腿；雪球在白色圆盘的位置、一样大，爪子按在雪球边上；手臂从肩膀长出来，爪子、雪球没有盖住脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a("- 努努一直骑在威朗普头上（趴倒那一张坐在地上）；扔雪球的两张里努努的手臂按姿势那一行画。")
a("- 所有图没有特效、没有骨架线、没有网格线、没有圆盘辅助线。\n")
a("## 交付（`outputs/nunu-poses/`）\n")
a("- " + "、".join(f"`nunu-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/nunu-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/nunu_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `nunu_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 爪子，灰框 = 头框） |")
a("| `1_head.png` | 定稿的头框（8 倍：威朗普的头、鹿角、努努）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 努努和威朗普定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_illaoi_poses 的做法：按头框的大小定比例，头框换成定稿的头框，张嘴 / 扔雪球 / 趴倒除外），"
  "颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和雪球的大小，和定稿比**（codex-legs-need-skeletons），腿长了就照俄洛伊的 legs 包重画腿，"
  "再拼进 rig_nunu.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_nunu.py）：普攻 attack = a_wind → a_swipe → 定稿；咬 attack_bite = b_open → b_bite；"
  "史上最大雪球 skill = w_pack，skill_roll = w_push1 ↔ w_push2，skill_hit = w_hit；雪球飞射 skill2 = e_throw1 ↔ e_throw2；"
  "绝对零度 ult = r_raise（引导，轻轻晃），ult_end = r_slam；死亡 dead = d_fall → d_lie；跑 run = run1–4；"
  "待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。")
open('assets/source/nunu/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, ARM2, "balls", BALLS)
