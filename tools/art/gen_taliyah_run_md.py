"""Write assets/source/taliyah/RUN_POSE_PROMPTS.md: Codex's prompt for Taliyah's run on her feet (the four run poses of
tools/art/pack_taliyah_poses.py; run from the repo root).

The user, 2026-10-26: 「塔利亚怎么是飞着走路的 不对吧」 - her run was the rock surf in every frame; League runs her on foot
in a fight and surfs only out of it. Picked: the League way (surf when out of combat), the foot run drawn by Codex.

    python tools/art/gen_taliyah_run_md.py
    python tools/art/pack_taliyah_poses.py --only run1,run2,run3,run4 --prompts RUN_POSE_PROMPTS.md \
        --out C:/t/ta_work/taliyah_run_pack
"""
import sys

sys.path.insert(0, 'tools/art')
import pack_taliyah_poses as P  # noqa: E402

names = ["run1", "run2", "run3", "run4"]
n = len(names)
LEG = round(P.REST["near_leg"][-1][1] - P.REST["near_leg"][0][1])        # hip to sole, rows
ARM = round(sum(P.lengths("near_arm")))                                  # shoulder to fingertips
L = []
a = L.append
a("# 岩雀 塔莉垭：用脚跑步的 4 个姿势（给 Codex 的提示词）\n")
a("> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**")
a("> - 塔莉垭的造型已经定稿（`2_design.png`，3/4 正面朝右）。上一轮你画的姿势里，她移动时一直蹲在大石头上冲浪；"
  "英雄联盟里她打架时是**用脚跑**的，只有脱战后才踩石头。这一轮只画**用脚跑步的一个循环：4 个姿势，每个一张图**，不要石头。")
a(f"> - **每张图都是同一个塔莉垭**：样子、颜色、粗细、长短全照 `2_design.png`，**每格 {P.PX} px**，画布 **1254 × 1254**，"
  f"红线是地面（**脚底 y = {P.SOLE_Y}**），网格从画布左上角对齐。")
a("> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，"
  "**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂**，**紫线 = 远侧的手臂**；**灰框 = 头的位置**。"
  "`0_design_skeleton.png` 是同样的骨架画在定稿上。")
a(f"> - **长短要数格子**：**头 {P.HW} × {P.HH} 格**；**每条腿从胯到脚底约 {LEG} 格**，**手臂从肩膀到指尖约 {ARM} 格**。"
  "腿、手臂沿着骨架画，长短粗细和定稿一样，**在关节处弯折**（膝盖往前弯，踢到身后的小腿折到大腿后面），不要拉长或压短，"
  "不要把直的腿整块转个方向贴上去。")
a("> - **头一格一格照 `1_head.png` 画在灰框里**（朝右前方、盘起的棕色大头发、金色发饰、两只琥珀色眼睛、小红嘴），四张都是这一个头，"
  "只跟着身体移动，不转头、不画侧脸。手臂不盖住脸。")
a("> - **四张连起来是一个跑步循环**：1 远侧脚着地、近侧腿往后踢 → 2 两腿交错、近侧膝盖往前提 → 3 近侧脚着地、远侧腿往后踢 → "
  "4 两腿交错、远侧膝盖往前提。**四张的身体高度、前倾角度、头的位置几乎一样**（只上下差一两格），这样连起来播放才不会跳。")
a("> - **红外套、两条红垂带和末端的灰石头往身后飘**（像英雄联盟里那样拖在身后），四张里飘的样子略有不同，但长短、石头的数量和定稿一样；"
  "**米白石片披肩**在肩膀上。")
a("> - 每个姿势附一张英雄联盟原版那一帧（`*_league.png`），**动作照它**（身子明显前倾、两手往两侧后下方张开），长相照定稿；"
  "**我们的永远是 3/4 正面朝右**。\n")
a(f"## {n} 个姿势\n")
a("| 图 | 文件 | 姿势 |")
a("|---|---|---|")
for k, name in enumerate(names, 3):
    a(f"| {k} | `taliyah-pose-{name}.png` | {P.POSES[name][1]} |")
a("")
a("## 提示词（每个姿势一次，换掉最后一段的姿势）\n")
a("每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`；"
  "有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**\n")
a("```text")
a(f"Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with {P.PX} px squares (soles on y "
  f"{P.SOLE_Y}) - THE STONEWEAVER GIRL: TANNED skin, a BIG SWEPT-UP MASS OF BROWN HAIR with a ROUND GOLD ORNAMENT, amber eyes, a CREAM "
  "STONE-PLATE MANTLE, a DARK INDIGO TUNIC with GOLD trim, a long RED COAT whose TWO RED PANELS end in GREY STONES, PURPLE SLEEVES with CREAM "
  f"CUFFS, dark indigo leggings and BROWN BOOTS; B its HEAD shown 8x ({P.HW} x {P.HH} squares); C a SKELETON on the same canvas and grid: green "
  "= the spine, RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm, PURPLE = the FAR arm, GREY "
  "BOX = where the head goes, the red horizontal line = the ground; D the original character in this frame of her RUN (copy the POSE, the arms "
  "and the coat's streaming from it - never its 3D look or realistic proportions); E (if attached) the skeleton drawn over image A.")
a("Draw with the image generator ONE clean pixel-art picture of the character of image A RUNNING ON HER FEET in the pose of the skeleton C "
  f"(and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly {P.PX} px - the SAME square "
  f"size as image A - on one straight grid from the canvas corner; the foot on the ground on y {P.SOLE_Y}. NO BOULDER, no rock under her.")
a(f"COUNT THE SQUARES: the head {P.HW} x {P.HH} squares; each leg about {LEG} squares from the hip to the sole, each arm about {ARM} squares "
  "from the shoulder to the fingertips, exactly as in image A. Lay the body along the skeleton: the tunic and coat along the green line, the "
  "mantle on the shoulders, each leg along its line bending at the dots (the knee bends forward; a leg kicked back folds its shin up behind "
  "the thigh) with the SAME thickness, length and colours as in image A, each arm from its shoulder along its line. The red coat and the two "
  "panels with their grey stones stream back behind her, keeping their length and stones. Never stretch or shorten a limb. The near side in "
  "full tone, the far side a step darker.")
a("THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every pose, only moved, never turned. No arm covers the face.")
a("The same colours as image A; one continuous 1-square near-black outline; no stray squares, no dithering, no gradients, no glow, no blur, "
  "no anti-aliasing. No effects, no dust, no motion lines, no background, no shadow, no text, no grid lines, no skeleton lines.")
a("THE POSE: <one line from the list below>")
a("```\n")
a("每个姿势的最后一行（英文）：\n")
for name in names:
    a(f"- {name}: `{P.POSES[name][2]}`")
a("")
a("## 交回前请检查\n")
a(f"- **4 张都是 image_gen 画的**；1254 × 1254；真透明背景，alpha 只有 0 / 255；**每格 {P.PX} px**。")
a(f"- 数格子：头 {P.HW} × {P.HH} 格、腿约 {LEG} 格、手臂约 {ARM} 格，和定稿一样。")
a(f"- 四张连起来像一个跑步循环：身体高度和前倾几乎一样，着地的脚在 y {P.SOLE_Y}；同一个头；没有石头、没有特效、没有骨架线。\n")
a("## 交付（`outputs/taliyah-run/`）\n")
a("- " + "、".join(f"`taliyah-pose-{x}.png`" for x in names) + "；原始生成图原样放 `outputs/taliyah-run/raw/`；`generation-prompts.txt`；"
  "**最后**写 `HANDOFF.md`，再打包成 `outputs/taliyah_run_done.zip`。4 张都画完再交。\n")
a("## 附图（压缩包 `taliyah_run_pack.zip` 里）\n")
a("| 文件 | 内容 |")
a("|---|---|")
a("| `0_design_skeleton.png` | 定稿上画着它自己的骨架 |")
a("| `1_head.png` | 定稿的头（8 倍） |")
a(f"| `2_design.png` | 定稿（每格 {P.PX} px，脚底 y {P.SOLE_Y}） |")
a(f"| `3_run1_*` … `6_run4_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |\n")
a("## Claude 收到后（给 Claude 看）\n")
a("- 按 design_taliyah_poses.py 的做法读回（按头的大小定比例、头换成定稿的头、颜色对到调色板），8 倍下量腿和手臂的长短，"
  "再拼进 rig_taliyah.py：`run` = run1 → run4（用脚跑），原来的冲浪 4 帧改名 `surf`（脱战时附加包把 run 换成 surf）。")
open('assets/source/taliyah/RUN_POSE_PROMPTS.md', 'w', encoding='utf-8', newline='\n').write("\n".join(L) + "\n")
print(n, "poses; leg", LEG, "arm", ARM)
