# 蔚奥莱：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「走路腿没有前后交换啊」**。上一版（`0_old_run_wrong.png`）**四帧在前面的那条腿都画成同一个样子**：都是近侧那条（颜色亮、画在另一条腿上面、大腿有藏青补丁），所以看起来永远是同一条腿在前，两条腿从来没有交换过。
> - 金铲铲里她是这样跑的（`0_run_cycle.png`，8 帧一个完整循环）：双拳套举在胸前小跑，**两条腿一前一后轮流迈步**：前半个循环一条腿在前，后半个循环换另一条腿在前。
> - 请你画 **8 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 12 px 放在这张画布上。**请严格用每格 12 px**（上一版实际画成了 9–11 px，大小每帧都不一样）。
> - **样子、颜色、画法全照定稿** `0_design.png`：洋红色斜垂的头发、上挑的眉毛、浅蓝眼睛；酒红短马甲、红兜帽、浅灰绿衬衫和胸前绷带、深棕腰带、深紫褐宽裤、橄榄绿绑腿、深棕短靴；**两只手都戴着大铁拳套**（蓝灰钢板、金黄方框拳头），跑步时举在胸前。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。
> - **大小照参考图**：下表「高」那一列是每帧从头顶到脚底的格数；头（含头发）约 28 × 27 格、每只拳套连前臂约 20 × 18 格、靴子和定稿一样大。**八帧的身体大小要一样**。

## 最要紧的：两条腿轮流在前

骨架里 **红腿 = 近侧的腿**（离镜头近），**蓝腿 = 远侧的腿**。这两条腿的画法**每一帧都固定**：

- **红腿（近侧）**：**大腿上是深藏青色的补丁**（和定稿画面右边那条腿一样），绑腿亮一档，**永远画在另一条腿上面**（两条腿在胯下交叉、重叠的地方，它盖住远侧的腿）。
- **蓝腿（远侧）**：**整条腿暗一档**（深紫褐色，没有藏青补丁），绑腿也暗一档，**永远在近侧那条腿后面**。

**哪条腿在前（靴子更靠画面右边）每半个循环换一次**：

- 第 1、2、3、4、5 帧：**红腿（近侧、藏青大腿）在前**，远侧的暗腿在后面；
- 第 6、7、8 帧：**蓝腿（远侧、暗腿）在前**，近侧的藏青大腿那条在后面——**这几帧在前面的是暗的那条腿，藏青补丁那条在后面，但胯下重叠的地方仍然是藏青那条盖在上面**。上一版就是这几帧画错了。

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以）。**没有哪只靴子是一直不动的**：两只靴子轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 红腿 | 蓝腿 | 在前的腿 |
|---|---|---|---|---|---|---|
| 1 | `violet-run-run1.png` | run@0 | 67 | 靴尖 (50, 76)，**抬起来**（比另一只高约 20 格） | 靴尖 (42, 96)，**踩在地上** | 红腿（近侧，藏青大腿） |
| 2 | `violet-run-run2.png` | run@117 | 67 | 靴尖 (60, 93)，**踩在地上** | 靴尖 (32, 94)，**踩在地上** | 红腿（近侧，藏青大腿） |
| 3 | `violet-run-run3.png` | run@233 | 75 | 靴尖 (68, 95)，**踩在地上** | 靴尖 (30, 70)，**抬起来**（比另一只高约 25 格） | 红腿（近侧，藏青大腿） |
| 4 | `violet-run-run4.png` | run@350 | 77 | 靴尖 (64, 96)，**踩在地上** | 靴尖 (31, 71)，**抬起来**（比另一只高约 25 格） | 红腿（近侧，藏青大腿） |
| 5 | `violet-run-run5.png` | run@466 | 68 | 靴尖 (53, 96)，**踩在地上** | 靴尖 (37, 77)，**抬起来**（比另一只高约 19 格） | 红腿（近侧，藏青大腿） |
| 6 | `violet-run-run6.png` | run@583 | 71 | 靴尖 (41, 94)，**踩在地上** | 靴尖 (47, 93)，**踩在地上** | 蓝腿（远侧，暗一档） |
| 7 | `violet-run-run7.png` | run@700 | 79 | 靴尖 (38, 73)，**抬起来**（比另一只高约 22 格） | 靴尖 (55, 96)，**踩在地上** | 蓝腿（远侧，暗一档） |
| 8 | `violet-run-run8.png` | run@816 | 75 | 靴尖 (42, 68)，**抬起来**（比另一只高约 28 格） | 靴尖 (51, 96)，**踩在地上** | 蓝腿（远侧，暗一档） |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (her soles on y 1176) - a lean TEENAGE GIRL street fighter: magenta-pink hair swooping over the far side of her face, dark brown brows tilted up, pale blue eyes; a short wine-red vest with a red hood behind the neck, a pale grey-green shirt with chest wraps, a dark brown belt, baggy dark purple-brown trousers, a DARK NAVY PATCH on the NEAR thigh, olive leg wraps, dark brown boots; a HUGE IRON GAUNTLET on EACH hand (blue-grey steel plates, a square gold-yellow fist frame). Image A stands in a fighting stance - copy only her look. B her HEAD shown 8x (about 28 squares wide, 27 tall). C a 3D RENDER of this same character's own game model in THIS FRAME OF HER RUN, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the pose, never its 3D shading or its small gauntlets). D the SKELETON of that frame, exactly over C: green = the spine, ORANGE and CYAN = the arms (the big dots = the hands, the GOLD rings = the gauntlets), the RED line = her NEAR leg, the BLUE line = her FAR leg, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 12 px, aligned on one straight grid from the canvas corner; her lowest point on y 1176.
THE LEGS: the NEAR leg (RED line) always has the dark NAVY thigh patch, light olive wraps, full tone, and is drawn OVER the far leg where they cross at the hips. The FAR leg (BLUE line) is a step darker all over (dark purple-brown, no navy, dark wraps) and always BEHIND the near one. Which leg is FORWARD changes: follow C and D - in this frame the {LEAD} leg is the forward one. Each boot exactly where C and D put it (the frame's line below gives each toe's square); one boot on the ground, the other lifted unless the line says both are down.
COUNT THE SQUARES: the head with the hair about 28 x 27, each gauntlet with its forearm about 20 x 18, the boots as big as in A, the same body size in every frame. Both gauntlets up at her chest as in C.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. No gauntlet covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文，`{LEAD}` 换成这一行写的那条腿）：

- run1: `RUN 1 of 8 - the RED leg (the NEAR one, navy thigh) is FORWARD; the RED leg's boot LIFTED, its toe at square (50, 76), the BLUE leg's boot ON THE GROUND, its toe at square (42, 96); about 67 squares tall.`
- run2: `RUN 2 of 8 - the RED leg (the NEAR one, navy thigh) is FORWARD; the RED leg's boot ON THE GROUND, its toe at square (60, 93), the BLUE leg's boot ON THE GROUND, its toe at square (32, 94); about 67 squares tall.`
- run3: `RUN 3 of 8 - the RED leg (the NEAR one, navy thigh) is FORWARD; the RED leg's boot ON THE GROUND, its toe at square (68, 95), the BLUE leg's boot LIFTED, its toe at square (30, 70); about 75 squares tall.`
- run4: `RUN 4 of 8 - the RED leg (the NEAR one, navy thigh) is FORWARD; the RED leg's boot ON THE GROUND, its toe at square (64, 96), the BLUE leg's boot LIFTED, its toe at square (31, 71); about 77 squares tall.`
- run5: `RUN 5 of 8 - the RED leg (the NEAR one, navy thigh) is FORWARD; the RED leg's boot ON THE GROUND, its toe at square (53, 96), the BLUE leg's boot LIFTED, its toe at square (37, 77); about 68 squares tall.`
- run6: `RUN 6 of 8 - the BLUE leg (the FAR, darker one - the navy-thigh near leg is BEHIND it but still drawn over it at the hips) is FORWARD; the RED leg's boot ON THE GROUND, its toe at square (41, 94), the BLUE leg's boot ON THE GROUND, its toe at square (47, 93); about 71 squares tall.`
- run7: `RUN 7 of 8 - the BLUE leg (the FAR, darker one - the navy-thigh near leg is BEHIND it but still drawn over it at the hips) is FORWARD; the RED leg's boot LIFTED, its toe at square (38, 73), the BLUE leg's boot ON THE GROUND, its toe at square (55, 96); about 79 squares tall.`
- run8: `RUN 8 of 8 - the BLUE leg (the FAR, darker one - the navy-thigh near leg is BEHIND it but still drawn over it at the hips) is FORWARD; the RED leg's boot LIFTED, its toe at square (42, 68), the BLUE leg's boot ON THE GROUND, its toe at square (51, 96); about 75 squares tall.`

## 交回

- 每帧一张：`outputs/violet-run/violet-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/violet-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只靴尖的格子（上表）、**哪条腿在前**、**藏青补丁在近侧那条腿上并且画在上面**，不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格、哪条腿在前。
- **8 帧都画完再交**，最后写 `outputs/violet-run/HANDOFF.md`，再打包成 `outputs/violet_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/violet/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头（design_violet_poses.py），逐帧对 `feet.json` 量两只靴尖、看哪条腿在前，连起来播放看有没有滑步、两条腿有没有轮流在前。
- 这份提示词和参考图由 `tools/art/pack_violet_run.py` 生成。
