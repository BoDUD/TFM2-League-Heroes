"""Write assets/source/sejuani/POSE_PROMPTS.md from tools/art/pack_sejuani_poses.py's POSES (run from the repo root): the
legs' and arms' lengths in squares for Codex to count; the flail a prop placed by the chain line and the ice disc; the two
head boxes (Sejuani's, Bristle's) pasted in every pose."""
import sys
sys.path.insert(0, 'tools/art')
import pack_sejuani_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.GROUND - P.REST["near_hind"][0][1])                         # hip to hoof, rows
ARM = round(sum(P.lengths("near_arm")))
ARM2 = round(sum(P.lengths("far_arm")))
CHAIN = round(sum(P.lengths("chain")))
ICE = round(P.ICE_R * 2)
L = []
a = L.append
a("# 北地之怒 瑟庄妮：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 瑟庄妮和钢鬃的造型用户已经定稿（`2_design.png` 是你上一轮重画的 A-2：3/4 正面朝右，Q 版的瑟庄妮——青铜金头盔、两只蓝冰角、"
  "冰蓝眼睛、浅金色头发、紫皮甲、青铜金尖肩甲上的蓝宝石、米白毛领，手里棕黑相间的链枷和蓝色冰锤头；骑在钢鬃背上——灰蓝毛、白鬃毛、"
  "两根象牙色大獠牙、粉鼻子、青蓝发光的眼睛、橄榄绿鞍甲和蓝宝石、深灰蹄子。`2_run_design.png` 是 B-1 冲锋定稿，跑步的骑法照它）。")
a(f"> - 英雄联盟里她甩链枷、横扫、砸地、甩套索，钢鬃冲锋挑飞、奔跑、人立、倒地，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**（{n - 4} 个动作 + 4 帧跑步），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张都是同一个瑟庄妮和钢鬃**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**最低的蹄子 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：**绿线 = 钢鬃的脊柱**（屁股到肩膀），**红线 = 钢鬃近侧的两条腿（画面左边那侧：近后腿、近前腿）**，"
  "**蓝线 = 钢鬃远侧的两条腿**；**青线 = 瑟庄妮的上身**（鞍上的屁股到脖子根），**橙线 = 她近侧的手臂（拿链枷的那只，定稿里在画面左边）**，"
  "**紫线 = 她远侧的手臂**，两条手臂上**大一点的圆点是拳头**；**棕线 = 链枷的链子**（从拳头出发），**浅蓝圆盘 = 冰锤头的位置和大小**；"
  "**两个灰框 = 两个头的位置**（小的是瑟庄妮的头，大的是钢鬃的头连獠牙）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：钢鬃 Q 版腿短——**每条腿从胯到蹄子约 {LEG} 格**；**瑟庄妮的手臂：近侧从肩膀到拳头约 {ARM} 格、远侧约 {ARM2} 格**；"
  f"**链子约 {CHAIN} 格长**，冰锤头约 {ICE} 格大。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**"
  "（之前一个英雄的腿画成了正常的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。")
a("> - **链枷**：棕黑相间的链子（2 格粗，棕黑一格一格交替）**沿着棕线画**，可以有一点弧度；末端的**蓝色冰锤头**（3 档蓝 + 青色亮纹）**画在浅蓝圆盘的位置**。"
  "链子从她近侧的拳头里出来。")
a("> - **两个灰框照 `1_heads.png` 一格一格画**：左边是瑟庄妮的头（头盔、两只冰角、额前宝石、朝右前方的脸、两只冰蓝眼睛、粉色小嘴、浅金头发），"
  "右边是钢鬃的头（耳朵、发光的眼睛、粉鼻子、张开的嘴、两根大獠牙、前面的白鬃毛）。每个姿势都是这两个头，只跟着身体移动，"
  "**不要转头、不要画成侧脸、不要重新设计**。**例外**写在姿势里：挑飞（钢鬃的头往上抬）、倒地（钢鬃的眼睛闭上）。拳头、链子、冰锤头**不要盖住她的脸**。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的钢鬃腿长、瑟庄妮是正常比例；"
  "我们的是 Q 版：两个头都大、腿短，**照骨架的长短画，不照原版的长短**。原版的链子很长（能甩出好几个身位），**我们的链子照棕线的长度**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `sejuani-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_heads.png`（两个头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，"
  "有余量再加 `0_design_skeleton.png`（跑步的四张换成 `2_run_design.png`）。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (the lowest hoof on "
  f"y {P.SOLE_Y}) - a chibi WARRIOR WOMAN riding a big WAR BOAR: she wears a bronze-gold helm with two curved blue ice horns and a blue gem on the "
  "brow, a pale face with two ice-blue eyes and a small pink mouth, pale blonde locks, purple leather armour under pointed bronze-gold plates with "
  "glowing blue gems, cream-white fur at the collar, and holds a FLAIL - a brown-and-black wrapped chain ending in a big blue ice head with cyan "
  "lines; the BOAR has blue-grey fur, a crest of white bristly mane, two huge ivory tusks curving up, a pink snout and a pink open mouth, a "
  "glowing cyan eye, pink inner ears, short legs with dark grey split hooves, olive-green bronze saddle armour with big blue gems; "
  f"B its two HEAD BOXES shown 8x: hers ({P.RHW} squares wide, {P.RHH} tall) and the boar's ({P.BHW} x {P.BHH}, with the tusks); "
  f"C a SKELETON on the same 1254 canvas and {P.PX} px grid: GREEN = the boar's spine (rump to shoulder), RED = the boar's NEAR legs (image left "
  "side), BLUE = its FAR legs, TEAL = the woman's upper body (hips in the saddle to the base of the neck), ORANGE = her NEAR arm (the flail arm, "
  "image left in A), PURPLE = her FAR arm, the bigger dot on each arm = the fist, BROWN = the flail's chain from her near fist, the LIGHT BLUE DISC "
  "= where the ice head goes and how big it is, the two GREY BOXES = where the two head boxes go (the small one hers, the big one the boar's), the "
  "red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its "
  "long realistic limbs or its very long chain); E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one "
  f"straight grid from the canvas corner; hooves that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - each of the boar's legs only about {LEG} squares from the hip to the hoof, her near arm about {ARM} squares "
  f"from the shoulder to the fist and the far arm about {ARM2}, the chain about {CHAIN} squares long, the ice head about {ICE} squares, exactly as in "
  "image A. Lay the bodies along the skeleton: the boar's bulky furry body along the green line, each short leg along its line (bending at the dots, "
  "the SAME thickness, length and colours as in image A, the dark grey hooves at the ends); her body in the saddle along the teal line, each arm "
  "from its shoulder along its line (the purple sleeve, the bronze bracer, the fist on the bigger dot; growing from the shoulders, never floating); "
  "the brown-and-black chain along the brown line out of her near fist, the blue ice head on the disc. Never stretch or shorten a limb, never paste "
  "a straight leg turned as one block. The near side in full tone, the far side a step darker.")
a("THE HEAD BOXES: copy image B SQUARE FOR SQUARE into the two grey boxes - her head with the helm, both ice horns, the gem, her face to the "
  "front-right with both ice-blue eyes and the pink mouth; the boar's head with the ear, the glowing eye, the pink snout, the open mouth and the "
  "two big ivory tusks - the same in every pose, only moved, never turned, never redrawn as a profile, except where THE POSE line below changes "
  "them. No fist, chain or ice head covers her face.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no frost, no ice storm, no flying bola, no snow, no dust, no motion trails), no background, no ground, no shadow, no text, no grid "
  "lines, no skeleton lines, no disc guide.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：钢鬃每条腿从胯到蹄子约 {LEG} 格、她近侧手臂约 {ARM} 格、远侧约 {ARM2} 格、链子约 {CHAIN} 格，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个瑟庄妮和钢鬃：**同样的两个头（照图 B：她的脸朝右前方、两只冰蓝眼睛、粉嘴；钢鬃的发光眼睛、粉鼻子、两根大獠牙）**、"
  f"同样粗的手臂和腿；链子沿着棕线、冰锤头在浅蓝圆盘上；手臂从肩膀长出来，拳头、链子、冰锤头没有盖住她的脸；姿势沿着骨架；着地的蹄子在 y {P.SOLE_Y}。")
a("- 瑟庄妮一直骑在钢鬃背上（人立那一张往后掉、倒地那一张摔在地上除外）。")
a("- 所有图没有特效、没有骨架线、没有网格线、没有圆盘辅助线。\n")
a("## 交付（`outputs/sejuani-poses/`）\n")
a("- " + "、".join(f"`sejuani-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/sejuani-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/sejuani_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `sejuani_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 拳头，灰框 = 两个头框，浅蓝圆盘 = 冰锤头） |")
a("| `1_heads.png` | 定稿的两个头框（8 倍：左边瑟庄妮、右边钢鬃）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` / `2_run_design.png` | 待机定稿 / 冲锋定稿（每格 {P.PX} px，最低的蹄子 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_aurelionsol_poses / design_nunu_poses 的做法：按头框的大小定比例，两个头框换成定稿的，"
  "挑飞 / 倒地除外），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、链子的长短粗细和冰锤头的大小，和定稿比**（codex-legs-need-skeletons），"
  "再拼进 rig_sejuani.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_sejuani.py）：普攻 attack = a_wind → a_smash → 定稿；极寒突袭 skill = 跑步帧加速冲 → q_toss；"
  "凛冬之怒 skill2 = w_sweep → w_raise → w_slam；极冰寒狱 ult = r_wind → r_throw；死亡 dead = d_rear → d_down；跑 run = run1–4；"
  "待机 = 定稿（hero_reels）；受击 hit = 定稿后退一格闪白。")
open('assets/source/sejuani/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM, ARM2, "chain", CHAIN, "ice", ICE)
