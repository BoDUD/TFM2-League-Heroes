# 纳什男爵：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一版的跑步（`0_old_run_wrong.png`）**两条腿从来不换**：八帧里都是同一只脚一直在前、另一只一直在后，没有一帧两条腿交错经过。这是我给的骨架的问题（不是你画错了），这一版骨架改好了。
> - 这一版（`0_run_cycle.png`，8 帧是**一个完整的循环**，迈两步）：**两条腿轮流往前迈**——第 6、7、8 帧亮的近侧那条腿在前，第 2、3、4 帧暗的远侧那条腿在前，第 1、5 帧两条腿交错经过（**换腿**）。
> - 请你画 **8 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（身体是纳什男爵模型自己的，腿只有骨架线：模型没有腿）。
> - 格子每格 **9 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 9 px 放在这张画布上。**请严格用每格 9 px**。
> - **样子、颜色、画法全照定稿** `0_design.png`；**上半身（头、头冠、两只小头、两只爪子、S 形身躯、腹甲）的大小和画法照上一版的跑步**（`0_old_run_wrong.png` 的上半身没问题），**八帧的上半身一样大、一样的姿势**，只跟着步子上下起伏 0–2 格；**要改的只是两条腿**。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体移动，不要转头。

## 最要紧的：两条腿看得出谁在前

骨架里 **蓝线 = 近侧的腿**（离镜头近），**红线 = 远侧的腿**。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（紫色粗腿：亮紫 `#8336E4`、主紫 `#5A117B`、暗紫 `#390D57`，象牙色三趾脚 `#F9D590` / `#D1AA65`），**永远画在另一条腿上面**（两条腿重叠的地方它盖住远侧那条）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：亮紫 `#8336E4` 换成 `#5A117B`，主紫 `#5A117B` 换成 `#390D57`，暗紫 `#390D57` 换成 `#200B38`，象牙色脚趾 `#F9D590` 换成 `#D1AA65`、`#D1AA65` 换成 `#907054`；**永远在近侧那条腿后面**。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 6、7、8 帧**亮的蓝腿在前**，第 2、3、4 帧**暗的红腿在前**，第 1、5 帧两只脚几乎上下对齐（换腿的那一刻）。

**每一帧画完，数格子核对两只脚**：脚尖（最前面那根脚趾的尖）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**谁在前照表**。没有哪只脚是一直在前的：两只脚轮流踩地、轮流抬起、轮流在前。

| 帧 | 文件 | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 |
|---|---|---|---|---|
| 1 | `baronnashor-run-run1.png` | 脚尖 (78, 128)，**踩在地上** | 脚尖 (79, 125)，**踩在地上** | **换腿**：两只脚尖几乎上下对齐，一只踩在身体下面，另一只抬着从旁边经过（相差 1 格） |
| 2 | `baronnashor-run-run2.png` | 脚尖 (74, 130)，**踩在地上** | 脚尖 (91, 127)，**抬起来**（比另一只高约 4 格） | **暗的红腿（远侧）在前**（相差 17 格） |
| 3 | `baronnashor-run-run3.png` | 脚尖 (73, 125)，**抬起来**（比另一只高约 6 格） | 脚尖 (89, 130)，**踩在地上** | **暗的红腿（远侧）在前**（相差 16 格） |
| 4 | `baronnashor-run-run4.png` | 脚尖 (68, 130)，**踩在地上** | 脚尖 (86, 129)，**踩在地上** | **暗的红腿（远侧）在前**（相差 18 格） |
| 5 | `baronnashor-run-run5.png` | 脚尖 (80, 130)，**踩在地上** | 脚尖 (80, 127)，**踩在地上** | **换腿**：两只脚尖几乎上下对齐，一只踩在身体下面，另一只抬着从旁边经过（相差 0 格） |
| 6 | `baronnashor-run-run6.png` | 脚尖 (88, 128)，**踩在地上** | 脚尖 (77, 130)，**踩在地上** | **亮的蓝腿（近侧）在前**（相差 11 格） |
| 7 | `baronnashor-run-run7.png` | 脚尖 (86, 130)，**踩在地上** | 脚尖 (76, 123)，**抬起来**（比另一只高约 8 格） | **亮的蓝腿（近侧）在前**（相差 10 格） |
| 8 | `baronnashor-run-run8.png` | 脚尖 (83, 130)，**踩在地上** | 脚尖 (72, 128)，**踩在地上** | **亮的蓝腿（近侧）在前**（相差 11 格） |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）、`0_old_run_wrong.png`（上半身照它，腿不要照它）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (its soles on y 1176) - a VOID SERPENT MONSTER on TWO SHORT THICK PURPLE LEGS with ivory three-toed feet: an S-curved purple body with a TEAL-GREEN SEGMENTED BELLY, a BLUE-VIOLET ARMOURED HEAD with yellow eyes, a red mouth and ivory tusks, a crown of PURPLE CREST FINS with MAGENTA TIPS, TWO SMALL SERPENT HEADS on thin arms, TWO BIG CURVED IVORY CLAWS. Image A stands - copy only its look. B its HEAD shown 8x. C a 3D RENDER of this same creature's own game model (its body only: the model has NO legs) in THIS FRAME OF ITS RUN, on the same 1254 canvas and grid, already placed where the picture must be, its two legs drawn as lines. D the SKELETON of that frame, exactly over C: green = the body, the BLUE line = its NEAR leg, the RED line = its FAR leg, PINK and CYAN = the small heads, YELLOW and ORANGE = the claws, GREY BOX = where the head goes, the red horizontal line = the ground. E its whole run cycle, 8 frames in a row. F its OLD run: copy its UPPER BODY - the head, the crest, the small heads, the claws, the body and the belly, their size and drawing; NOT its legs (crossed out: wrong).
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 9 px, aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (the purples #8336E4, #5A117B, #390D57, the ivory toes #F9D590, #D1AA65), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design (the light purple #8336E4 becomes #5A117B, the main purple #5A117B becomes #390D57, the dark purple #390D57 becomes #200B38, the ivory toes #F9D590 become #D1AA65 and #D1AA65 becomes #907054), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the two PASSING frames the toes are nearly one above the other: one foot planted under the body, the other lifted beside it. Each foot exactly where D puts it; one foot on the ground, the other lifted unless the line says both are down.
COUNT THE SQUARES: the same body size in every frame and the same as image F's upper body; the legs as thick and the feet as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned. Nothing covers the face.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - THE PASSING: the two toes nearly one above the other, one foot planted under the body, the other lifted and passing beside it. the BLUE leg's foot ON THE GROUND, its toe at square (78, 128), the RED leg's foot ON THE GROUND, its toe at square (79, 125); the two toes 1 square apart.`
- run2: `RUN 2 of 8 - the FAR (RED, darker) leg ahead. the BLUE leg's foot ON THE GROUND, its toe at square (74, 130), the RED leg's foot LIFTED, its toe at square (91, 127); the two toes 17 squares apart.`
- run3: `RUN 3 of 8 - the FAR (RED, darker) leg ahead. the BLUE leg's foot LIFTED, its toe at square (73, 125), the RED leg's foot ON THE GROUND, its toe at square (89, 130); the two toes 16 squares apart.`
- run4: `RUN 4 of 8 - the FAR (RED, darker) leg ahead. the BLUE leg's foot ON THE GROUND, its toe at square (68, 130), the RED leg's foot ON THE GROUND, its toe at square (86, 129); the two toes 18 squares apart.`
- run5: `RUN 5 of 8 - THE PASSING: the two toes nearly one above the other, one foot planted under the body, the other lifted and passing beside it. the BLUE leg's foot ON THE GROUND, its toe at square (80, 130), the RED leg's foot ON THE GROUND, its toe at square (80, 127); the two toes 0 squares apart.`
- run6: `RUN 6 of 8 - the NEAR (BLUE, light) leg ahead. the BLUE leg's foot ON THE GROUND, its toe at square (88, 128), the RED leg's foot ON THE GROUND, its toe at square (77, 130); the two toes 11 squares apart.`
- run7: `RUN 7 of 8 - the NEAR (BLUE, light) leg ahead. the BLUE leg's foot ON THE GROUND, its toe at square (86, 130), the RED leg's foot LIFTED, its toe at square (76, 123); the two toes 10 squares apart.`
- run8: `RUN 8 of 8 - the NEAR (BLUE, light) leg ahead. the BLUE leg's foot ON THE GROUND, its toe at square (83, 130), the RED leg's foot ON THE GROUND, its toe at square (72, 128); the two toes 11 squares apart.`

## 交回

- 每帧一张：`outputs/baronnashor-run/baronnashor-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/baronnashor-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**两帧换腿是不是真的交错**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**、**八帧上半身一样大**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **8 帧都画完再交**，最后写 `outputs/baronnashor-run/HANDOFF.md`，再打包成 `outputs/baronnashor_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/baronnashor/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的脸（design_baronnashor_poses.py 的读法），逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身八帧一致（必要时一个上半身用到八帧，design_sevika_run.py / design_steb_run.py 的做法）。
- 每帧在游戏里的时长（ms，按片段的间隔分 1270 ms 一个循环）：[165, 170, 165, 160, 155, 155, 150, 150]。
- 这份提示词和参考图由 `tools/art/pack_baronnashor_run.py` 生成。
