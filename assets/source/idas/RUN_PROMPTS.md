# 艾达丝：走路（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。** 这一包**代替**动作包里原来的 8 帧移动（`idas_pose_pack` 已经去掉了 run1–run8）。
> - **这次改成金铲铲原版的跑法**（用户：「走路最好改成像金铲铲里面那样的姿势」）。上一包直立走路交回来的 8 帧是用定稿的零件剪下来、再弯折拼起来的，用户说「非常的奇怪」。**这次每一帧都用 image_gen 照它自己的参考图整张画出来，不要从定稿上剪零件拼、不要把剪下来的腿/翅膀旋转弯折拉伸。**
> - **而且一定要看得出两条腿明显地前后交换**（用户：「走路要有明显的腿部交换啊」）。以前几个英雄的走路被退回过（「换腿不明显」「走路腿没有前后交换」）：八帧只画了半个循环、两条腿画成一样的颜色、腿被别的东西挡住。这次照下面做。
> - 金铲铲里她是这样跑的（`0_run_cycle.png`，8 帧是**一个完整的循环**，0.67 秒迈两步）：**身子压得很低、几乎和地面平行**，龙头往前低低地伸着，**长尾巴往后伸直**；两只翅膀手臂往前伸、**爪子在头前面点地**（像四条腿一样往前扑），前臂上的金翼跟着扇（第 2–3 帧往上扬，第 5–6 帧往下收在身前）；**两条反关节腿在身体下面轮流往后蹬**——第 2、3、4 帧远侧那条腿在前，第 1、5 帧两条腿交错经过（**换腿、交叉**），第 6、7、8 帧近侧那条腿在前。
> - 请你画 **8 帧走路**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例、尾巴缩到定稿的长度，和画布、格子、位置都对好了）。
> - 格子每格 **7 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**：这一包里多半是在头前面点地的翅膀爪，后脚不一定碰到地），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 7 px 放在这张画布上。**请严格用每格 7 px**。
> - **样子、颜色、画法全照定稿** `0_design.png`：有棱角的金鳞甲、深棕胸腹、青蓝宝石；青蓝鬃冠和角、发光的青蓝眼睛；翅膀手臂上的金色羽刃翼和深灰三指爪；长尾巴和尾刃。**八帧的身体一样大**（身子、头、翅膀、尾巴、腿的粗细和定稿一样，只是姿势不同）。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着脖子移动、稍微低一点，不要转头、不要重新设计。
> - **翅膀手臂和金翼不能挡住腿**：两条腿（从胯到脚）每帧都要整条看得见；翅膀照参考图往前伸、扇在身体上方或身前，不要盖住腿。

## 最要紧的：两条腿看得出谁在前、有交叉步

骨架里 **蓝线 = 近侧的腿**（她的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。腿是反关节的（像鸟腿：大腿往前，膝盖往后弯，下面是细长的跗骨和三趾的脚）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（金色腿甲 `#FCD612` / `#FABE0A` / `#F49802` / `#C96C01`、深紫褐色的脚踝和脚 `#442930` / `#241317`、灰色爪子 `#C0BEE3` / `#878AA3` / `#646481`），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：金色腿甲只用 `#C96C01` 和 `#9F5201`、脚踝和脚全用 `#241317`、爪子全用 `#646481`；**永远在近侧那条腿后面**。
- 两只脚每帧都要露出来，脚和爪子和定稿一样大。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 2、3、4 帧**暗的红腿在前**，第 6、7、8 帧**亮的蓝腿在前**，第 1、5 帧两只脚几乎上下对齐（换腿的那一刻，两条腿**交叉**：一条从另一条旁边经过，蓝腿盖在上面）。

**每一帧画完，数格子核对两只脚**：脚尖（爪子最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只脚尖之间的距离照表**。没有哪只脚是一直不动的：两只脚轮流蹬地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
| 1 | `idas-run-run1.png` | run@0 | 74 | 脚尖 (77, 157)，**低的那只**（蹬地） | 脚尖 (75, 148)，**抬起来**（比另一只高约 5 格） | 两只脚尖上下对齐（交叉） | **换腿的一帧**：两只脚几乎上下对齐，红腿（远侧、暗）抬着从蓝腿旁边往前收，蓝腿在下面蹬地 |
| 2 | `idas-run-run2.png` | run@80 | 93 | 脚尖 (63, 157)，**低的那只**（蹬地） | 脚尖 (92, 145)，**抬起来**（比另一只高约 9 格） | **红腿（远侧、暗）在前** 29 格 | 红腿往前伸出去（抬着），蓝腿在后面蹬地；两只翅膀往上扬 |
| 3 | `idas-run-run3.png` | run@160 | 92 | 脚尖 (53, 157)，**低的那只**（蹬地） | 脚尖 (101, 153)，**抬起来**（比另一只高约 4 格） | **红腿（远侧、暗）在前** 48 格 | **红腿在前**、两只脚分得最开：红脚在最前面，蓝腿在后面伸直 |
| 4 | `idas-run-run4.png` | run@240 | 67 | 脚尖 (53, 150)，**低的那只**（蹬地） | 脚尖 (94, 154)，**低的那只**（蹬地） | **红腿（远侧、暗）在前** 41 格 | 红腿还在前，蓝腿（近侧）开始往前收 |
| 5 | `idas-run-run5.png` | run@360 | 66 | 脚尖 (77, 155)，**低的那只**（蹬地） | 脚尖 (79, 157)，**抬起来**（比另一只高约 5 格） | 两只脚尖上下对齐（交叉） | **交叉的一帧**：蓝腿（近侧）从红腿旁边往前经过，两只脚上下对齐，蓝腿盖在红腿上面；两只翅膀往下收在身前 |
| 6 | `idas-run-run6.png` | run@440 | 76 | 脚尖 (90, 163)，**低的那只**（蹬地） | 脚尖 (66, 161)，**低的那只**（蹬地） | **蓝腿（近侧）在前** 24 格 | **蓝腿在前**踩地，红腿在后面踩地 |
| 7 | `idas-run-run7.png` | run@520 | 58 | 脚尖 (95, 161)，**低的那只**（蹬地） | 脚尖 (56, 152)，**抬起来**（比另一只高约 6 格） | **蓝腿（近侧）在前** 39 格 | **蓝腿在前**、两只脚分得最开：蓝脚在最前面，红腿在后面抬起来 |
| 8 | `idas-run-run8.png` | run@600 | 64 | 脚尖 (88, 161)，**低的那只**（蹬地） | 脚尖 (62, 151)，**抬起来**（比另一只高约 8 格） | **蓝腿（近侧）在前** 26 格 | 蓝腿还在前，红腿（远侧）抬起来往前收 |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, side view facing right, on a 1254x1254 canvas with 7 px squares (her feet on y 1176) - a GOLDEN DRAGON on two backward-bending (digitigrade) legs: angular faceted gold scale plates, a dark brown chest and belly, cyan gems; the head thrust forward with a cyan fan crest, swept-back cyan horns, a crescent pale-cyan cheek horn, a snout horn, a glowing cyan eye; her arms are her wings, each gold forearm carrying a golden feather-blade wing and ending in a dark grey three-taloned claw; a long gold tail with a dark grey-violet blade. Her LEGS: gold thigh plates, dark mauve-brown ankles and feet, grey claws. Image A stands idle - copy only her look. B her HEAD shown 8x. C a 3D RENDER of this same creature's own game model in THIS FRAME OF HER RUN (a low bound: the body almost level and low, the head stretched forward low, the long tail stretched straight back, the wing-arms reaching forward with the claws touching the ground in front of the head, the two legs pushing in turn under the body), on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the pose of the body, the wing-arms and the legs, never its 3D shading; the head already enlarged, the tail already shortened). D the SKELETON of that frame, exactly over C: green = the spine, PURPLE / ORANGE = the near / far wing-arm (the big dot = the claw), the BLUE line = her NEAR leg, the RED line = her FAR leg, BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D - drawn whole as one picture, NEVER assembled from pieces cut out of image A, never with cut pieces rotated, bent or stretched into place: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 7 px, aligned on one straight grid from the canvas corner; her lowest point on y 1176 (in this run mostly the wing-claws touching the ground in front of the head).
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A, in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design (the gold plates only #C96C01 and #9F5201, the ankles and feet all #241317, the claws all #646481), and always BEHIND the near one. Each leg bends BACKWARD at its knee like a bird's, along its line. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the PASSING / CROSSING frames the two legs cross: one passes beside the other, the near leg drawn over it. Each foot exactly where D puts it; one foot lower and pushing, the other lifted, unless the line says both are low. Both legs WHOLE and visible, from the hip to the claws - the wing-arms and the wings never cover them.
COUNT THE SQUARES: the same body size in every frame and the same as image A (the same thickness of the body, the head, the wing-arms, the tail and the legs - only the pose changes); the feet and claws as big as in A; legs never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved and tilted a little down with the neck, never turned, never redrawn; the mouth shut.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - THE PASSING: the two feet almost one above the other, the far (RED, darker) leg lifted and coming forward beside the near (BLUE) one, the blue leg pushing below. the BLUE leg's foot the LOWER one, pushing, its toe at square (77, 157), the RED leg's foot LIFTED, its toe at square (75, 148); the two toes 2 squares apart; about 74 squares tall.`
- run2: `RUN 2 of 8 - the far (RED) leg reaching forward, lifted; the near (BLUE) leg pushing off behind; both wings swept up. the BLUE leg's foot the LOWER one, pushing, its toe at square (63, 157), the RED leg's foot LIFTED, its toe at square (92, 145); the two toes 29 squares apart, the RED one ahead; about 93 squares tall.`
- run3: `RUN 3 of 8 - the far (RED) leg FORWARD - the widest split: the red foot far ahead, the blue leg stretched back. the BLUE leg's foot the LOWER one, pushing, its toe at square (53, 157), the RED leg's foot LIFTED, its toe at square (101, 153); the two toes 48 squares apart, the RED one ahead; about 92 squares tall.`
- run4: `RUN 4 of 8 - the far (RED) leg still ahead; the near (BLUE) leg starting to come forward. the BLUE leg's foot the LOWER one, pushing, its toe at square (53, 150), the RED leg's foot the LOWER one, pushing, its toe at square (94, 154); the two toes 41 squares apart, the RED one ahead; about 67 squares tall.`
- run5: `RUN 5 of 8 - THE CROSSING: the near (BLUE) leg passing forward beside the far (RED) one, the two feet one above the other, the blue leg drawn over it; both wings folded down in front. the BLUE leg's foot the LOWER one, pushing, its toe at square (77, 155), the RED leg's foot LIFTED, its toe at square (79, 157); the two toes 2 squares apart; about 66 squares tall.`
- run6: `RUN 6 of 8 - the near (BLUE) leg FORWARD, planted; the far (RED) foot planted behind. the BLUE leg's foot the LOWER one, pushing, its toe at square (90, 163), the RED leg's foot the LOWER one, pushing, its toe at square (66, 161); the two toes 24 squares apart, the BLUE one ahead; about 76 squares tall.`
- run7: `RUN 7 of 8 - the near (BLUE) leg FORWARD - the widest split: the blue foot far ahead, the red leg lifting behind. the BLUE leg's foot the LOWER one, pushing, its toe at square (95, 161), the RED leg's foot LIFTED, its toe at square (56, 152); the two toes 39 squares apart, the BLUE one ahead; about 58 squares tall.`
- run8: `RUN 8 of 8 - the near (BLUE) leg still ahead; the far (RED) leg lifted, coming forward. the BLUE leg's foot the LOWER one, pushing, its toe at square (88, 161), the RED leg's foot LIFTED, its toe at square (62, 151); the two toes 26 squares apart, the BLUE one ahead; about 64 squares tall.`

## 交回

- **交到新的文件夹** `outputs/idas-run2/`（上一次的 `idas-run/` 和 `idas_run_done.zip` 是直立走路，不要覆盖、也不要再用）。
- 每帧一张：`outputs/idas-run2/idas-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 7 px）；原始生成图原样放进 `outputs/idas-run2/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**交叉的帧两条腿真的交叉**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**、**两条腿整条露出来**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **8 帧都画完再交**，最后写 `outputs/idas-run2/HANDOFF.md`，再打包成 `outputs/idas_run2_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/idas/codex_run2/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头（八帧用同一个上半身时，每帧保留它自己的腿），逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；身体大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 720 ms 一个循环）：[86, 86, 86, 130, 86, 86, 86, 72]。
- 这份提示词和参考图由 `tools/art/pack_idas_run.py` 生成。
