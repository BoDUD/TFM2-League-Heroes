# 艾达丝：走路（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。** 这一包**代替**动作包里原来的 8 帧移动（`idas_pose_pack` 已经去掉了 run1–run8）。
> - **走路一定要看得出两条腿明显地前后交换**（用户：「走路要有明显的腿部交换啊」）。以前几个英雄的走路被退回过（「换腿不明显」「走路腿没有前后交换」）：八帧只画了半个循环、两条腿画成一样的颜色、腿被别的东西挡住。这次照下面做。
> - 她这样走（`0_run_cycle.png`，8 帧是**一个完整的循环**，迈两步；金铲铲原版是趴着往前扑、看不出换腿，所以用她自己的模型做了直立走路）：身子和待机一样微微前倾，两只翅膀手臂垂在身前，长尾巴在身后，**两条反关节腿轮流迈步**——第 2、3、4、5 帧远侧那条腿在前，第  帧两条腿交错经过（**换腿、交叉**），第 1、6、7、8 帧近侧那条腿在前。
> - 请你画 **8 帧走路**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型摆出的这一帧走路，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **7 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 7 px 放在这张画布上。**请严格用每格 7 px**。
> - **样子、颜色、画法全照定稿** `0_design.png`：有棱角的金鳞甲、深棕胸腹、青蓝宝石；青蓝鬃冠和角、发光的青蓝眼睛；翅膀手臂上的金色羽刃翼和深灰三指爪；长尾巴和尾刃。**八帧的身体一样大**、跟着步子上下起伏 0–2 格。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体移动，不要转头。
> - **翅膀手臂和金翼不能挡住腿**：两条腿（从胯到脚）每帧都要整条看得见；翅膀照参考图放在身前、腿的上方。

## 最要紧的：两条腿看得出谁在前、有交叉步

骨架里 **蓝线 = 近侧的腿**（她的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。腿是反关节的（像鸟腿：大腿往前，膝盖往后弯，下面是细长的跗骨和三趾的脚）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（金色腿甲 `#FCD612` / `#FABE0A` / `#F49802` / `#C96C01`、深紫褐色的脚踝和脚 `#442930` / `#241317`、灰色爪子 `#C0BEE3` / `#878AA3` / `#646481`），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：金色腿甲只用 `#C96C01` 和 `#9F5201`、脚踝和脚全用 `#241317`、爪子全用 `#646481`；**永远在近侧那条腿后面**。
- 两只脚每帧都要露出来，脚和爪子和定稿一样大。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 2、3、4、5 帧**暗的红腿在前**，第 1、6、7、8 帧**亮的蓝腿在前**，第  帧两只脚几乎上下对齐（换腿的那一刻，两条腿**交叉**：一条从另一条旁边经过，蓝腿盖在上面）。

**每一帧画完，数格子核对两只脚**：脚尖（爪子最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只脚尖之间的距离照表**。没有哪只脚是一直不动的：两只脚轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
| 1 | `idas-run-run1.png` | walk@0 | 99 | 脚尖 (74, 161)，**踩在地上** | 脚尖 (68, 138)，**抬起来**（比另一只高约 24 格） | **蓝腿（近侧）在前** 6 格 | **换腿的一帧**：红腿（远侧、暗）抬着从蓝腿**后面**往前迈过去，两只脚几乎上下对齐，蓝腿踩在身体下方、盖在上面 |
| 2 | `idas-run-run2.png` | walk@1 | 94 | 脚尖 (64, 161)，**踩在地上** | 脚尖 (79, 153)，**抬起来**（比另一只高约 10 格） | **红腿（远侧、暗）在前** 15 格 | 红腿往前伸、快落地，蓝腿踩在后面 |
| 3 | `idas-run-run3.png` | walk@2 | 92 | 脚尖 (60, 161)，**踩在地上** | 脚尖 (96, 162)，**踩在地上** | **红腿（远侧、暗）在前** 36 格 | **红腿在前**、两只脚分得最开，两只脚都踩在地上 |
| 4 | `idas-run-run4.png` | walk@3 | 92 | 脚尖 (57, 151)，**抬起来**（比另一只高约 10 格） | 脚尖 (91, 163)，**踩在地上** | **红腿（远侧、暗）在前** 34 格 | 红腿踩在前面，蓝腿（近侧）在后面**抬起来**、准备往前摆 |
| 5 | `idas-run-run5.png` | walk@4 | 90 | 脚尖 (62, 153)，**抬起来**（比另一只高约 8 格） | 脚尖 (80, 163)，**踩在地上** | **红腿（远侧、暗）在前** 18 格 | 蓝腿抬着往前摆、膝盖弯着，红腿踩在身体下方 |
| 6 | `idas-run-run6.png` | walk@5 | 92 | 脚尖 (73, 161)，**踩在地上** | 脚尖 (69, 157)，**抬起来**（比另一只高约 6 格） | **蓝腿（近侧）在前** 4 格 | **交叉的一帧**：蓝腿（近侧）从红腿**前面**经过，两只脚上下对齐，蓝腿盖在红腿上面 |
| 7 | `idas-run-run7.png` | walk@6 | 99 | 脚尖 (90, 161)，**踩在地上** | 脚尖 (65, 147)，**抬起来**（比另一只高约 16 格） | **蓝腿（近侧）在前** 25 格 | **蓝腿在前**往前伸，红腿在后面抬起来 |
| 8 | `idas-run-run8.png` | walk@7 | 100 | 脚尖 (85, 161)，**踩在地上** | 脚尖 (63, 136)，**抬起来**（比另一只高约 26 格） | **蓝腿（近侧）在前** 22 格 | 蓝腿踩在前面，红腿（远侧）在后面**抬得最高**、开始往前摆 |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, side view facing right, on a 1254x1254 canvas with 7 px squares (her feet on y 1176) - a GOLDEN DRAGON on two backward-bending (digitigrade) legs: angular faceted gold scale plates, a dark brown chest and belly, cyan gems; the head thrust forward with a cyan fan crest, swept-back cyan horns, a crescent pale-cyan cheek horn, a snout horn, a glowing cyan eye; her arms are her wings, each gold forearm carrying a golden feather-blade wing and ending in a dark grey three-taloned claw; a long gold tail with a dark grey-violet blade. Her LEGS: gold thigh plates, dark mauve-brown ankles and feet, grey claws. Image A stands idle - copy only her look. B her HEAD shown 8x. C a 3D RENDER of this same creature's own game model in THIS FRAME OF HER WALK, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the pose of the body, the wing-arms and the legs, never its 3D shading; the head already enlarged). D the SKELETON of that frame, exactly over C: green = the spine, PURPLE / ORANGE = the near / far wing-arm (the big dot = the claw), the BLUE line = her NEAR leg, the RED line = her FAR leg, BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole walk cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 7 px, aligned on one straight grid from the canvas corner; her lowest point on y 1176.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A, in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design (the gold plates only #C96C01 and #9F5201, the ankles and feet all #241317, the claws all #646481), and always BEHIND the near one. Each leg bends BACKWARD at its knee like a bird's, along its line. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the PASSING / CROSSING frames the two legs cross: one passes beside the other, the near leg drawn over it. Each foot exactly where D puts it; one foot on the ground, the other lifted unless the line says both are down. Both legs WHOLE and visible, from the hip to the claws - the wing-arms and the wings never cover them.
COUNT THE SQUARES: the same body size in every frame and the same as image A; the feet and claws as big as in A; legs never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - THE PASSING: the far (RED, darker) leg lifted, swinging forward BEHIND the planted near (BLUE) one, the two feet almost one above the other, the blue leg drawn over it. the BLUE leg's foot ON THE GROUND, its toe at square (74, 161), the RED leg's foot LIFTED, its toe at square (68, 138); the two toes 6 squares apart, the BLUE one ahead; about 99 squares tall.`
- run2: `RUN 2 of 8 - the far (RED) leg reaching forward, about to land; the near (BLUE) foot planted behind. the BLUE leg's foot ON THE GROUND, its toe at square (64, 161), the RED leg's foot LIFTED, its toe at square (79, 153); the two toes 15 squares apart, the RED one ahead; about 94 squares tall.`
- run3: `RUN 3 of 8 - the far (RED) leg FORWARD - the widest split, both feet on the ground. the BLUE leg's foot ON THE GROUND, its toe at square (60, 161), the RED leg's foot ON THE GROUND, its toe at square (96, 162); the two toes 36 squares apart, the RED one ahead; about 92 squares tall.`
- run4: `RUN 4 of 8 - the far (RED) foot planted ahead; the near (BLUE) leg LIFTED behind, about to swing forward. the BLUE leg's foot LIFTED, its toe at square (57, 151), the RED leg's foot ON THE GROUND, its toe at square (91, 163); the two toes 34 squares apart, the RED one ahead; about 92 squares tall.`
- run5: `RUN 5 of 8 - the near (BLUE) leg lifted and swinging forward, its knee bent; the far (RED) foot planted under her. the BLUE leg's foot LIFTED, its toe at square (62, 153), the RED leg's foot ON THE GROUND, its toe at square (80, 163); the two toes 18 squares apart, the RED one ahead; about 90 squares tall.`
- run6: `RUN 6 of 8 - THE CROSSING: the near (BLUE) leg passing in front of the far (RED) one, the two feet one above the other, the blue leg drawn over it. the BLUE leg's foot ON THE GROUND, its toe at square (73, 161), the RED leg's foot LIFTED, its toe at square (69, 157); the two toes 4 squares apart, the BLUE one ahead; about 92 squares tall.`
- run7: `RUN 7 of 8 - the near (BLUE) leg FORWARD, reaching out; the far (RED) leg lifting behind. the BLUE leg's foot ON THE GROUND, its toe at square (90, 161), the RED leg's foot LIFTED, its toe at square (65, 147); the two toes 25 squares apart, the BLUE one ahead; about 99 squares tall.`
- run8: `RUN 8 of 8 - the near (BLUE) foot planted ahead; the far (RED) leg LIFTED high behind, starting to swing forward. the BLUE leg's foot ON THE GROUND, its toe at square (85, 161), the RED leg's foot LIFTED, its toe at square (63, 136); the two toes 22 squares apart, the BLUE one ahead; about 100 squares tall.`

## 交回

- 每帧一张：`outputs/idas-run/idas-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 7 px）；原始生成图原样放进 `outputs/idas-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**交叉的帧两条腿真的交叉**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**、**两条腿整条露出来**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **8 帧都画完再交**，最后写 `outputs/idas-run/HANDOFF.md`，再打包成 `outputs/idas_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/idas/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头，逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；身体大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 720 ms 一个循环）：[90, 90, 90, 90, 90, 90, 90, 90]。
- 这份提示词和参考图由 `tools/art/pack_idas_run.py` 生成。
