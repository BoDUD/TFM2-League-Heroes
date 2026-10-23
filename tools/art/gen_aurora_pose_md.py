"""Write assets/source/aurora/POSE_PROMPTS.md from tools/art/pack_aurora_poses.py's POSES (run from the repo root).
The prompt gives every limb's length in squares and asks Codex to count them (Qiyana's adult-long legs, 2026-10-22)."""
import sys
sys.path.insert(0, 'tools/art')
import pack_aurora_poses as P
names = list(P.POSES)
n = len(names)
LEG = round(P.REST["near_leg"][-1][1] - P.REST["near_leg"][0][1])        # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips
L = []
a = L.append
a("# 双界灵兔 阿萝拉：动作姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 阿萝拉的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右的 Q 版兔子女巫——铜红卷发和两条麻花辫、圆金框眼镜后面的紫蓝眼睛、"
  "青绿宽檐女巫帽和金边、红羽毛、两只从帽子里竖起来的长兔耳朵、米白高领、浅蓝白毛边披肩、米白长外套和后摆、青绿胸布、棕色编织腰带、深棕过膝长袜、"
  "白毛边短靴，身后一团蓬松的橙色兔尾巴，远侧的手（画面右边）握着一根细长的魔杖扛在肩上，杖身从头的后面往左上方斜伸出去，杖头一格蓝光）。"
  "英雄联盟里她每个动作都挥着魔杖——举起来、往前点、甩出去、竖起来、往下指、两手握着推出去、跳起来、往后跳——这些靠挪动定稿本身的部件"
  f"摆不出来，所以请你按骨架画 **{n} 个姿势，每个一张图**（{n - 4} 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。")
a(f"> - **每张图都是同一个阿萝拉**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边，握魔杖的那只）**；"
  "**魔杖是一根直的细长条：黄色 = 杖身，青色 = 杖头的蓝光**；紫线的末端就在杖身上（那里是手握着魔杖的地方）；"
  "**灰框 = 头的位置（连帽子和兔耳朵）**；**半透明的橙色形状 = 身后的兔尾巴**（和定稿里一模一样，只跟着腰移动）。`0_design_skeleton.png` 是同样的骨架画在定稿上，"
  "看每条线对应身体的哪一部分。")
a(f"> - **长短要数格子**：Q 版的大头——**头连帽子和耳朵 {P.HW} × {P.HH} 格，占了一半多的身高**；身子和腿很短——**每条腿从胯到脚底只有约 {LEG} 格**，"
  f"**手臂从肩膀到指尖约 {ARM} 格**，**魔杖从杖尾到杖头 {round(P.WAND_L)} 格**（很长，比她的身子还长）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**"
  "（以前的英雄腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。"
  "**魔杖和定稿一样长、一样细**，只是换了方向。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、圆眼镜后两只紫蓝眼睛都看得见、帽子、羽毛、两只长兔耳朵、麻花辫）。每个姿势都是这一个头，"
  "只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、魔杖**不要盖住脸**（眼镜、眼睛和嘴）。她的手臂很短，举不过这么大的头："
  "**魔杖举起来时在头的右边，扛在肩上时从头的后面穿过去（和定稿一样，头挡住中间那一段）**。**兔尾巴照定稿画在半透明橙色的位置**，形状不变。")
a("> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的阿萝拉是正常比例；"
  "我们的是 Q 版大头：身子短、手臂短、腿短，**手臂往两边、往前、往后、往上伸，不要从脸前面横过去**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `aurora-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y {P.SOLE_Y}) - "
  "a chibi PETITE BUNNY WITCH with a VERY BIG head: curly copper-red hair with two short braids, round thin gold glasses over violet-blue eyes, a wide "
  "teal witch hat with a gold brim and red feathers, TWO LONG RABBIT EARS (orange-red outside, pale pink inside) rising through the hat, a cream high "
  "collar, a pale blue-white fur-trimmed shawl, a cream long coat with tails, a teal chest panel, a brown braided belt, dark brown thigh-high stockings, "
  "short boots with white fur trim, a FLUFFY ORANGE TAIL behind her, and a LONG SLIM WAND in her far hand (a dark brown shaft with gold fittings, a "
  f"blue glowing tip, a red butt) resting on her shoulder and passing BEHIND her head; B its HEAD with the hat and the ears shown 8x ({P.HW} squares "
  f"wide, {P.HH} tall); C a SKELETON on the same 1254 canvas and {P.PX} px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg "
  "(image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right, the one holding the "
  "wand), the WAND as one straight thin bar - YELLOW = the shaft, CYAN = the blue glowing tip - the purple arm ends on the shaft where the hand grips it, "
  "GREY BOX = where the head goes (with the hat and the ears), the TRANSLUCENT ORANGE shape = the tail behind her (exactly as in the design, only moved "
  "with her waist), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE and the wand's "
  "swing from it, never its 3D look or its realistic proportions); E (if attached) the same skeleton drawn over image A, showing which line is which part.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG "
  f"with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square size as image A - aligned on one straight "
  f"grid from the canvas corner; feet that touch the ground on y {P.SOLE_Y}.")
a(f"COUNT THE SQUARES: chibi proportions - the head with the hat and the ears {P.HW} x {P.HH} squares, more than half of her height; each leg only about "
  f"{LEG} squares from the hip to the sole, each arm about {ARM} squares from the shoulder to the fingertips, the wand {round(P.WAND_L)} squares from "
  "the butt to the tip, exactly as in image A. Lay the body along the skeleton: the torso, the shawl and the coat along the green line (the coat tails "
  "hanging behind), each leg along its line (bending at the dots: the dark brown stocking with its cream top, the boot with white fur trim - the SAME "
  "thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow from the shoulders, never floating; the cream "
  "sleeve and glove), the far hand GRIPPING the wand where the purple line ends. THE WAND drawn along the bar at the design's length and thickness: the "
  "dark brown shaft with gold fittings, one blue glowing square at the tip where the cyan part is, a red square at the butt. Where the wand's bar runs "
  "through the grey box it passes BEHIND the head (hidden by it), as in image A. Never stretch or shorten a limb, never paste a straight leg turned as "
  "one block. The near side in full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, the round gold glasses, both violet-blue eyes, the smile, the "
  "copper hair and braids, the teal hat with its gold brim and red feathers, the two long ears) - the same head in every pose, only moved, never turned, "
  "never redrawn as a profile. No arm, hand or part of the wand covers the face (the glasses and the mouth). THE TAIL drawn square for square as in "
  "image A where the translucent orange shape is.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing.")
a("No effects (no spirits, no magic trails, no shockwaves, no sparkles, no motion lines), no background, no ground, no shadow, no text, no grid lines, "
  "no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **{n} 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 {P.PX} px**（和定稿一样）。")
a(f"- **数格子**：头 {P.HW} × {P.HH} 格、每条腿从胯到脚底约 {LEG} 格、手臂约 {ARM} 格、魔杖 {round(P.WAND_L)} 格，和定稿一样——腿画长了就重画。")
a("- 每张都是定稿的同一个阿萝拉：**同一个头（照图 B，脸朝右前方、圆眼镜、两只紫蓝眼睛、帽子、两只长耳朵）**、同样粗的腿和手臂、同样的兔尾巴；"
  "**魔杖和定稿一样长、一样细**，杖头一格蓝光，握着它的手在杖身上；手臂从肩膀长出来，手和魔杖没有盖住脸；姿势沿着骨架；着地的脚在 "
  f"y {P.SOLE_Y}。")
a("- 所有图没有特效、没有骨架线、没有网格线。\n")
a("## 交付（`outputs/aurora-poses/`）\n")
a("- " + "、".join(f"`aurora-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/aurora-poses/raw/`；`generation-prompts.txt`；"
  f"**最后**写 `HANDOFF.md`，再打包成 `outputs/aurora_poses_done.zip`。中间不要停，{n} 张都画完再交。\n")
a("## 附图（压缩包 `aurora_pose_pack.zip` 里）\n")
a("请把压缩包解压到一个**新的文件夹**，只用里面的图。\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄 / 青 = 魔杖，半透明橙 = 尾巴） |")
a("| `1_head.png` | 定稿的头（连帽子和耳朵，8 倍）：每个姿势都照它逐格画 |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_{names[0]}_*` … `{n + 2}_{names[-1]}_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a(f"- 量格子（应约 {P.PX} px），按格读回（design_illaoi_poses 的做法：按头的大小定比例，头换成定稿的头——头框里魔杖穿过的那一段要留出来），"
  "颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂和魔杖的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就照 legs 包重画腿，"
  "再拼进 rig_aurora.py 的动作里，逐帧自查后才发合成 GIF。")
a("- 动作安排（照英雄联盟，标签见 tools/kit/build_aurora.py）：普攻 attack = a_wind → a_point；飞去来咒 skill = q_wind → q_cast → q_catch；"
  "怪奇喷涌 skill2 = e_push → e_hop；双界合一 ult = r_reach → r_leap → r_land；灵纱洞开 veil = w_hop；死亡 dead = d_stagger → d_slump；"
  "跑 run = run1–4；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。")
open('assets/source/aurora/POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM)
