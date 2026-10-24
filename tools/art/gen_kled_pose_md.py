"""Write assets/source/kled/POSE_PROMPTS.md from tools/art/pack_kled_poses.py's POSES (run from the repo root): the limbs'
lengths in squares for Codex to count; the axe, the rope and the bear trap as props placed by their lines and discs; the
head boxes (Kled's, Skaarl's) pasted in every pose; the mounted poses on hd/idle.png, the on-foot ones on hd/foot.png."""
import sys
sys.path.insert(0, 'tools/art')
import pack_kled_poses as P
names = list(P.POSES)
mounted = [x for x in names if P.POSES[x][0] == "m"]
foot = [x for x in names if P.POSES[x][0] == "f"]
n = len(names)
L_LEG = round(P.GROUND_M - P.REST_M["near_leg"][0][1])                  # Skaarl hip to toe, rows
F_LEG = round(P.GROUND_F - P.REST_F["f_near_leg"][0][1])                # Kled hip to sole on foot
ARM = round(sum(P.lengths(P.REST_M, "near_arm")))
ARM2 = round(sum(P.lengths(P.REST_M, "far_arm")))
F_ARM = round(sum(P.lengths(P.REST_F, "f_near_arm")))
ROPE = round(sum(P.lengths(P.REST_M, "rope")))
TAIL = round(sum(P.lengths(P.REST_M, "tail")))
AXE = round(sum(P.lengths(P.REST_F, "f_axe")))
KHW, KHH = P.K_HEAD_M[3] - P.K_HEAD_M[2], P.K_HEAD_M[1] - P.K_HEAD_M[0]
SHW, SHH = P.S_HEAD[3] - P.S_HEAD[2], P.S_HEAD[1] - P.S_HEAD[0]
L = []
a = L.append
a("# 暴怒骑士 克烈：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 克烈的两张造型用户已经定稿：`2_design.png` 是骑乘（你上一轮的 A-1：Q 版的约德尔老兵——大尖耳朵、青绿红边帽子上的钢尖刺、红头带、"
  "米白毛和大胡子、一只乳白的瞎眼和一只琥珀黄的好眼、咧嘴狂笑露白色尖牙、青绿上衣、红腰带、棕背带；一只手拿小双刃斧，一只手拎着绳子拴的捕熊夹；"
  "骑在斯嘎尔背上——橙黄鳞片、紫肚子、青蓝头刺、一只黄绿大眼睛、两条细长的紫腿和金星护腿、一条尾巴），"
  "`2_foot_design.png` 是下马步行（B-1 身子换上了 A-1 的头：同一张脸；双手握大双刃斧，深灰条纹裤、黑靴）。")
a(f"> - 英雄联盟里他扔捕熊夹、拽人、骑着斯嘎尔冲刺、冲锋、挥斧，下马后挥大斧、掏枪被后坐力掀飞、倒下，这些靠挪动定稿的部件摆不出来，"
  f"所以请你按骨架画 **{n} 个姿势**（骑乘 {len(mounted)} 个、步行 {len(foot)} 个），**每个一张图**。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **骑乘的姿势都是同一个克烈和斯嘎尔**（照 `2_design.png`），**步行的都是同一个克烈**（照 `2_foot_design.png`）：样子、颜色、粗细、长短全照定稿，"
  f"**格子和定稿一样大：每格 {P.PX} px**，画布 **1254 × 1254**，红线是地面（**着地的脚 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：骑乘——**绿线 = 斯嘎尔的脊柱**（屁股到脖子根，它是两条腿直立走的），"
  "**红线 = 斯嘎尔近侧的腿（画面左边）**，**蓝线 = 远侧的腿**，**黄线 = 尾巴**；**青线 = 克烈的上身**（鞍上的屁股到脖子根），"
  "**橙线 = 克烈近侧的手臂（拿斧头的那只，定稿里在画面左边）**，**紫线 = 远侧的手臂**（拎绳子的那只），两条手臂上**大一点的圆点是拳头**；"
  "**灰蓝线 = 斧柄，浅灰圆盘 = 斧刃的位置和大小**；**棕线 = 绳子**（从远侧拳头出发），**深灰圆盘 = 捕熊夹**；"
  "步行——**暗红线 = 近侧的腿、深蓝线 = 远侧的腿**，其余颜色同上（灰蓝线是大斧的长柄，浅灰大圆盘是两片斧刃）。"
  "**灰框 = 头的位置**（大的是克烈的头，骑乘图里小一点的是斯嘎尔的头）。`0_mounted_skeleton.png` / `0_foot_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：斯嘎尔 Q 版腿短——**每条腿从胯到脚约 {L_LEG} 格**，尾巴约 {TAIL} 格；**克烈骑乘时的手臂：近侧从肩膀到拳头约 {ARM} 格、远侧约 {ARM2} 格**，"
  f"**绳子约 {ROPE} 格长**；**步行时克烈的腿从胯到脚底约 {F_LEG} 格、手臂约 {F_ARM} 格，大斧从手到斧刃约 {AXE} 格**。骨架就是按定稿量的："
  "**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常的长腿，只能重画——请画完数一数），"
  "**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。")
a("> - **道具**：小斧头（骑乘）/ 大双刃斧（步行）**沿着灰蓝线画斧柄、斧刃画在浅灰圆盘的位置**；绳子（棕色 1 格宽、一格一格的结）**沿着棕线画**，"
  "末端的**钢灰色捕熊夹画在深灰圆盘的位置**。掏枪那两张远侧的手里拿一把**短粗的黑色火枪**（枪管 2–3 格粗，枪口朝右），大斧拖在近侧的手里。")
a("> - **灰框照 `1_heads.png` 一格一格画**：左边是克烈的头（帽子、钢尖刺、两只大耳朵、红头带、瞎眼 + 好眼、狂笑的尖牙、大胡子），"
  "右边是斯嘎尔的头（青蓝头刺、黄绿大眼睛和紫眼睑、宽嘴）。每个姿势都是这两个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。"
  "**例外**写在姿势里：死亡瘫倒那张克烈闭眼、头耷拉。拳头、斧头、绳子、夹子**不要盖住克烈的脸**。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的斯嘎尔脖子和腿很长、克烈是正常比例；"
  "我们的是 Q 版：头大、腿短，**照骨架的长短画，不照原版的长短**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `kled-pose-{name}.png` | {P.POSES[name][2]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：定稿（骑乘的姿势传 `2_design.png`，步行的传 `2_foot_design.png`）、`1_heads.png`（头）、这个姿势的 `*_skeleton.png`、"
  "这个姿势的 `*_league.png`，有余量再加对应的 `0_*_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (the feet on "
  f"y {P.SOLE_Y}) - a chibi GRUMPY LITTLE BIG-EARED WARRIOR: HUGE POINTED EARS, a teal hat with a red brim and a big steel spike on top, a red "
  "headband, cream-white fur and a big shaggy beard, ONE milky-white BLIND EYE with a pink scar and one amber GOOD EYE, a MANIC GRIN with white "
  "pointed teeth, a teal-green coat, a red sash, brown straps; MOUNTED (the riding pictures) he holds a small two-bladed axe and a bear trap on a "
  "brown rope and sits on a big UPRIGHT LIZARD - amber-orange scales, a purple belly, teal-blue head spines, one big yellow-green eye with a "
  "purple lid, two thin purple bird-like legs with brown shin guards and gold stars, a tail; ON FOOT (the on-foot pictures) he stands alone on "
  "short legs (dark grey striped trousers, black boots) holding a BIG two-bladed axe in both hands; "
  f"B the HEAD BOXES shown 8x: his head ({KHW} squares wide, {KHH} tall) and the lizard's ({SHW} x {SHH}); "
  f"C a SKELETON on the same 1254 canvas and {P.PX} px grid: GREEN = the lizard's spine (rump to the base of the neck), RED = its NEAR leg (image "
  "left), BLUE = its FAR leg, YELLOW = its tail, TEAL = the warrior's upper body (hips to the base of the neck), ORANGE = his NEAR arm (the axe "
  "arm, image left), PURPLE = his FAR arm, the bigger dot on each arm = the fist, GREY-BLUE = the axe's haft with a LIGHT GREY DISC where the "
  "blade goes, BROWN = the rope from his far fist with a DARK GREY DISC where the bear trap goes; on foot DARK RED = his near leg and NAVY = his "
  "far leg; the GREY BOXES = where the head boxes go; the red horizontal line = the ground; D the original character in this pose, 3/4 view "
  "facing right (copy the POSE from it, never its 3D look or its long realistic limbs); E (if attached) the same skeleton drawn over image A, "
  "showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one "
  f"straight grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions exactly as in image A - the lizard's legs only about {L_LEG} squares from the hip to the toe, its tail about "
  f"{TAIL}; the mounted warrior's near arm about {ARM} squares from the shoulder to the fist and the far arm about {ARM2}, the rope about {ROPE}; on "
  f"foot his legs about {F_LEG} squares from the hip to the sole, his arms about {F_ARM}, the big axe about {AXE} from his hand to the blades. Lay the "
  "bodies along the skeleton: the lizard's scaly body along the green line, each thin leg along its line (bending at the dots, the SAME thickness, "
  "length and colours as in image A, the claws at the ends), the tail along the yellow line; his body along the teal line, each arm from its "
  "shoulder along its line (the teal sleeve, the brown glove on the bigger dot; growing from the shoulders, never floating); the axe's haft along "
  "the grey-blue line and its steel blades on the light grey disc; the brown rope along the brown line out of his far fist, the steel bear trap on "
  "the dark grey disc. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a "
  "step darker.")
a("THE HEAD BOXES: copy image B SQUARE FOR SQUARE into the grey boxes - his head with the hat, the steel spike, both big ears, the red headband, "
  "the blind eye and the good eye, the grin with white teeth and the beard; the lizard's head with the teal spines, the big yellow-green eye and "
  "the wide mouth - the same in every pose, only moved, never turned, never redrawn as a profile, except where THE POSE line below changes them. "
  "No fist, axe, rope or trap covers his face.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no dust, no speed lines, no shield, no muzzle flash, no smoke, no motion trails), no background, no ground, no shadow, no text, no "
  "grid lines, no skeleton lines, no disc guides.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][3]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：斯嘎尔每条腿从胯到脚约 {L_LEG} 格；骑乘的克烈近侧手臂约 {ARM} 格、远侧约 {ARM2} 格、绳子约 {ROPE} 格；"
  f"步行的克烈腿约 {F_LEG} 格、手臂约 {F_ARM} 格——腿画长了就重画。")
a("- 每张都是定稿的同一个克烈（和斯嘎尔）：**同样的头（照图 B：瞎眼 + 琥珀好眼一样高、狂笑尖牙、大耳朵、帽子钢尖刺；斯嘎尔的黄绿大眼）**、"
  f"同样粗的手臂和腿；斧头、绳子、夹子在各自的线和圆盘上；手臂从肩膀长出来，没有东西盖住克烈的脸；姿势沿着骨架；着地的脚在 y {P.SOLE_Y}。")
a("- 骑乘的那几张克烈一直在斯嘎尔背上（举斧那张从鞍上站起来一点）；步行的那几张没有斯嘎尔。")
a("- 所有图没有特效、没有骨架线、没有网格线、没有圆盘辅助线。\n")
a("## 交付（`outputs/kled-poses/`）\n")
a("- " + "、".join(f"`kled-pose-{x}.png`" for x in names) + "；")
a("- 原始生成图原样放 `outputs/kled-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/kled_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `kled_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_mounted_skeleton.png` / `0_foot_skeleton.png` | 两张定稿上画着它们自己的骨架（每条线对应哪一部分，大圆点 = 拳头，灰框 = 头框，圆盘 = 斧刃 / 捕熊夹） |")
a("| `1_heads.png` | 定稿的两个头框（8 倍：左边克烈、右边斯嘎尔）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` / `2_foot_design.png` | 骑乘定稿 / 步行定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_sejuani_poses / design_nunu_poses 的做法：按头框的大小定比例，头框换成定稿的，"
  "瘫倒那张除外），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、绳子的长短粗细，和定稿比**（codex-legs-need-skeletons），"
  "再拼进 rig_kled.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_kled.py）：骑乘 attack = a_wind → a_chop；skill（Q）= q_throw → q_yank；skill2（E）= e_lunge → e_slash；"
  "ult（R）= r_charge + 跑步帧；run = run1–4；idle = 定稿；hit = 定稿后退一格闪白。步行 f_attack = f_wind → f_chop；f_skill（手枪）= f_aim → f_recoil；"
  "f_run = f_run1–3；f_idle = 步行定稿；dead = d_fall → d_down（死亡都是步行的克烈：英雄联盟里骑乘死也是 Rider_Death）。")
open('assets/source/kled/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; legs", L_LEG, F_LEG, "arms", ARM, ARM2, F_ARM, "rope", ROPE, "tail", TAIL, "axe", AXE)
