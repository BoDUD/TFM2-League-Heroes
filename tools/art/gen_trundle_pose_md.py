"""Write assets/source/trundle/POSE_PROMPTS.md from tools/art/pack_trundle_poses.py's POSES (run from the repo root).
gen_yorick_pose_md.py's way: every limb's length in squares for Codex to count (Qiyana's adult-long legs, 2026-10-22);
his ice club is a big prop, placed by the light-blue shaft and head on each skeleton."""
import sys
sys.path.insert(0, 'tools/art')
import pack_trundle_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.GROUND - P.REST["near_leg"][0][1])                          # hip to sole, rows
ARM = round(sum(P.lengths("free_arm")))                                  # shoulder to fist
ARM2 = round(sum(P.lengths("club_arm")))
L = []
a = L.append
a("# 巨魔之王 特朗德尔：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 特朗德尔的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A 第一版，按原样定稿：3/4 正面朝右的 Q 版冰霜巨魔——"
  "炸开的深红头发连着大红胡子围住整张脸、浅灰青色的脸、两只亮蓝色的眼睛、米黄色的骨头大鼻子、两颗獠牙、尖耳朵；"
  "脖子和背后一圈很大的白毛皮领子，领子里是深棕红皮披风；两肩大大的青绿宝石 + 金铜边圆肩甲；灰蓝色带斑点的皮肤、粗胳膊、"
  "金铜色护腕；深棕红皮裤、青绿圆护膝、白毛靴口、光脚米黄爪子；腰上金黄长腰布和青绿宝石扣；驼着背、两腿叉开蹲着，"
  "画面左边那只手举在肩甲下面、握着**一根和他身子差不多长的寒冰狼牙棒**（冰块拼成的棒子，越往下越粗，末端一大块多面体的冰疙瘩，"
  "冰疙瘩杵在地上）；画面右边那只手握拳垂在远侧膝盖边）。")
a(f"> - 英雄联盟里他抡冰棒砸人、扑上去咬、蹲下跳起冻住地面、高举冰棒召出冰柱、站直伸手吸对手的力量，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**（{n - 6} 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张都是同一个特朗德尔**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。（这次格子比别的英雄小，因为他和冰棒都很宽，11 px 放不下。）")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根；他驼背，头往前垂在两个肩甲中间），"
  "**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 握冰棒的那只手臂**（定稿里在画面左边、"
  "从大肩甲下面伸出来），**橙线 = 空着的那只手臂**（定稿里在画面右边、握拳垂着）；手臂线的第一个点是肩膀（大肩甲的中间），"
  "**大一点的圆点是手**；**灰框 = 头的位置**（头发、脸、胡子）；**浅蓝色的长条 + 末端的大块 = 冰棒**（细的一头是手握的棒柄，"
  "大块 = 冰疙瘩）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的腿短——**每条腿从胯到脚底约 {LEG} 格**；**空着的手臂从肩膀到拳头约 {ARM} 格、握棒的约 {ARM2} 格**"
  f"（手臂很短，肩甲很大）；头（头发连脸连胡子）{P.HW} × {P.HH} 格；**冰棒从棒柄到冰疙瘩的尖约 {P.CLUB_L} 格长**（和定稿一样长，"
  f"冰疙瘩约 {P.CLUB_HEAD[1]} 格宽、{P.CLUB_HEAD[0]} 格长，不放大不缩短）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，"
  "关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。"
  "手臂从肩甲下面长出来，不能悬空；白毛领、皮披风、肩甲跟着身子走。")
a("> - **冰棒**：照定稿的冰棒画（浅蓝 / 天蓝的冰块、几道亮白的面、越往下越粗、末端多面体的冰疙瘩），**画在骨架上浅蓝长条的位置，"
  "一样长、一样朝向**；握棒的手就在紫线末端的圆点上，**握着棒柄那一头**。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、炸开的红头发和红胡子、两只亮蓝眼睛一样高、米黄大鼻子、獠牙）。"
  "每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（张嘴吼的几个姿势，只把胡子中间的嘴张开、露出獠牙）。"
  "手臂、手、冰棒**不要盖住脸**（眼睛、鼻子、獠牙）；冰棒从头附近经过时画在头**后面**。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的特朗德尔手臂长、"
  "能把冰棒竖着举过头顶；我们的是 Q 版大头：手臂短、冰棒很长，**照骨架的长短和冰棒的位置画，不照原版的长短**"
  "（原版竖着举的地方，骨架把冰棒斜着放，好让整根冰棒留在画布里）。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `trundle-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi HUNCHED ICE TROLL with a BIG head: a wild crimson MANE joined to a big crimson BEARD framing a pale grey-teal face with TWO BRIGHT BLUE "
  "EYES, a big cream bone-like NOSE, two cream TUSKS and pointed ears; a huge spiky WHITE FUR COLLAR round his neck and back over a dark reddish-brown "
  "leather cape; BIG ROUND TEAL-GEM PAULDRONS in gold-bronze frames; spotted grey-blue skin, thick short arms with gold-bronze bracers; dark "
  "reddish-brown leather trousers, round teal knee guards, white fur boot rings, bare feet with cream claws; a long gold-yellow loincloth with a teal "
  "gem buckle; crouched with his legs wide apart; the hand on the image left raised under its pauldron gripping a HUGE ICE CLUB about as long as his "
  "legs and body (blocks of pale blue ice, wider toward the end, a big FACETED ICE HEAD resting on the ground), the fist on the image right hanging by "
  f"the far knee; B its HEAD shown 8x ({P.HW} squares wide, {P.HH} tall: the mane, face and beard); C a SKELETON on the same 1254 canvas and {P.PX} px "
  "grid: green = the spine (pelvis to the base of the neck; he is hunched, the head hangs forward between the pauldrons), RED = the NEAR leg (image "
  "left), BLUE = the FAR leg (image right), PURPLE = the CLUB arm (on the image left in A), ORANGE = the FREE arm (on the image right in A), each arm "
  "line starting at the shoulder (the middle of its pauldron), the bigger dot on each arm = the hand, GREY BOX = where the head goes, the LIGHT BLUE "
  "LONG SHAPE with a BIG BLOCK at its end = where the ice club goes (its thin end is the handle in the hand, the big block the ice head), the red "
  "horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long "
  "realistic arms); E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each leg only about {LEG} squares from the hip to the sole, the free arm about {ARM} squares from the "
  f"shoulder to the fist and the club arm about {ARM2}, the ice club about {P.CLUB_L} squares from the handle to the tip of its ice head, exactly as in "
  "image A. Lay the body along the skeleton: the torso with the straps, the belt and the loincloth along the green line, the fur collar, the cape and "
  "the pauldrons riding on the shoulders and moving with the body, each leg along its line (bending at the dots: the leather trousers, the knee guard, "
  "the fur boot ring, the bare clawed foot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (thick "
  "short grey-blue arms growing from under the pauldrons, never floating; the gold-bronze bracers). THE CLUB: the same ice club as in image A drawn "
  "exactly on the light blue shape, the handle in the club hand on the purple dot, the ice head on the big block, the same length. Where the club "
  "passes the grey box it goes BEHIND his head. Never stretch or shorten a limb or the club, never paste a straight leg turned as one block. The near "
  "side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the mane, the face to the front-right, both bright blue eyes at the same height, the "
  "bone nose, the tusks, the beard) - the same head in every pose, only moved, never turned, never redrawn as a profile (in a roaring pose only open "
  "the mouth in the middle of the beard, the tusks showing). No arm, hand or club covers the face (the eyes, the nose and the tusks).")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing (the ice's highlights are bright squares, not a halo).")
a("No effects (no ice pillar, no frozen ground, no frost mist, no bite marks, no dust, no shockwave, no motion trails), no background, no ground, no "
  "shadow, no text, no grid lines, no skeleton lines, no light blue guide shapes.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：每条腿从胯到脚底约 {LEG} 格、空着的手臂约 {ARM} 格、握棒的约 {ARM2} 格、冰棒约 {P.CLUB_L} 格长，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个特朗德尔：**同一个头（照图 B，红头发红胡子、脸朝右前方、两只亮蓝眼睛一样高、骨头鼻子、獠牙）**、"
  "同样粗的手臂和腿、同样的毛领、肩甲、腰布；冰棒在骨架浅蓝长条的位置、一样长、冰疙瘩在大块那一头，手握着棒柄；"
  f"手臂从肩甲下面长出来，手、冰棒没有盖住脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a("- 所有图没有特效（冰柱、冰面、寒气、咬痕都不画）、没有骨架线、没有网格线、没有浅蓝辅助形状。\n")
a("## 交付（`outputs/trundle-poses/`）\n")
a("- " + "、".join(f"`trundle-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/trundle-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/trundle_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `trundle_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，浅蓝长条 + 大块 = 冰棒） |")
a("| `1_head.png` | 定稿的头（8 倍，头发、脸、胡子）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 特朗德尔定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_yorick_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；"
  "**先在 8 倍下量每条腿、手臂的长短粗细和冰棒的长短，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_trundle.py 的动作里，"
  "逐帧自查后才发合成 GIF（带技能的 GIF 也要）。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_trundle.py）：普攻 attack = a_wind → a_smash → 定稿；利齿撕咬 skill = q_rear → q_chomp；"
  "冰封领域（被动里的 W，`w` 标签：Q 咬中英雄后跳起）= w_crouch → w_roar；寒冰之柱 skill2 = e_swing → e_raise；强权至上 ult = r_rise → r_reach；"
  "死亡 dead = d_fall → d_down；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。")
open('assets/source/trundle/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, ARM2, "club", P.CLUB_L)
