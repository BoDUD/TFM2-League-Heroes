# 呲呲：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「感觉走路换腿有点问题」**。上一版（`0_old_run_wrong.png`）的毛病：① **八帧都是两条腿一前一后分开**，没有一帧两条腿交错经过（换腿）；② **亮的近侧那条腿七帧都在前面**，远侧那条腿也没有明显变暗——看起来像同一条腿一直在前，两条腿从不交换。
> - 金铲铲里它是这样跑的（`0_run_cycle.png`，这 8 帧是**一个完整的循环**，迈两步）：身子前倾、尾巴往后伸直，**两条腿轮流往前迈**——第 1、2 帧近侧那条腿在前，第 4、5、6、7 帧远侧那条腿在前，第 3、8 帧两条腿交错经过（**换腿**）。
> - 请你画 **8 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（它金铲铲模型自己的跑步动画那一帧，和画布、格子、位置都对好了）。
> - 格子每格 **10 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 10 px 放在这张画布上。**请严格用每格 10 px**。
> - **样子、颜色、画法全照定稿** `0_design.png`；**上半身（头、玫红长羽毛、紫色围兜、马鞍、身子、尾巴）的大小和画法照上一版的跑步**（`0_old_run_wrong.png`：用户没有意见的就是上半身），**八帧的上半身一样大**、跟着步子上下起伏 0–2 格；要改的只是两条腿。像素格、近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体移动，不要转头。

## 最要紧的：两条腿看得出谁在前

骨架里 **蓝线 = 近侧的腿**（它的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（橙褐色大腿带亮面 `#EF7528` / `#B44E1C`、紫色脚踝绑带带高光 `#992CA8`、深褐色脚、三根黑色大弯爪），**永远画在另一条腿上面**（两条腿在胯下或交错时重叠的地方，它盖住远侧那条腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：大腿和小腿全用 `#883713`、暗面 `#66250A`，脚踝绑带用 `#5F1868`、暗面 `#3D0942`，黑爪不变；**永远在近侧那条腿后面**。

**哪条腿在前（脚更靠画面右边）每半个循环换一次**：第 1、2 帧**亮的蓝腿在前**，第 4、5、6、7 帧**暗的红腿在前**，第 3、8 帧两只脚几乎上下对齐（换腿的那一刻：一只脚踩在身体正下方，另一只抬起来从旁边经过）。

**每一帧画完，数格子核对两只脚**：脚尖（爪子最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只脚尖之间的距离和谁在前照表**（上一版的毛病就是谁在前不对、从没有交错）。没有哪只脚是一直在前的：两只脚轮流踩地、轮流抬起、轮流在前。

| 帧 | 文件 | 片段 | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|
| 1 | `zippy-run-run1.png` | run@0 | 脚尖 (53, 100)，**抬起来**（比另一只高约 9 格） | 脚尖 (45, 109)，**踩在地上** | **蓝腿（近侧）在前** 8 格 | 蓝腿（近侧）**在空中往前伸**、快要落地，红腿（远侧、暗）在后面踩地往后蹬 |
| 2 | `zippy-run-run2.png` | run@120 | 脚尖 (59, 110)，**踩在地上** | 脚尖 (45, 108)，**踩在地上** | **蓝腿（近侧）在前** 14 格 | 蓝腿（近侧）**在前面踩地**（近侧这一步迈得最开），红腿在后面脚跟抬起、刚要离地 |
| 3 | `zippy-run-run3.png` | run@255 | 脚尖 (55, 112)，**踩在地上** | 脚尖 (55, 97)，**抬起来**（比另一只高约 15 格） | **两只脚尖上下对齐（换腿）** | **换腿的一帧**：蓝腿踩在身体正下方，红腿（远侧、暗）抬起来、膝盖往前，红脚从蓝腿**后面**经过，两只脚尖上下对齐 |
| 4 | `zippy-run-run4.png` | run@360 | 脚尖 (45, 112)，**踩在地上** | 脚尖 (62, 99)，**抬起来**（比另一只高约 13 格） | **红腿（远侧、暗）在前** 17 格 | **红腿（远侧、暗）在前**：红腿在空中往前伸，蓝腿踩在身体后下方往后蹬 |
| 5 | `zippy-run-run5.png` | run@440 | 脚尖 (37, 108)，**踩在地上** | 脚尖 (64, 99)，**抬起来**（比另一只高约 9 格） | **红腿（远侧、暗）在前** 27 格 | 红腿在空中伸得更远，蓝腿在后面蹬地、脚跟抬起 |
| 6 | `zippy-run-run6.png` | run@520 | 脚尖 (34, 111)，**踩在地上** | 脚尖 (64, 111)，**踩在地上** | **红腿（远侧、暗）在前** 30 格 | 红腿**在最前面落地**（远侧这一步迈得最开，两只脚分得最开），蓝腿在后面刚离地 |
| 7 | `zippy-run-run7.png` | run@620 | 脚尖 (38, 97)，**抬起来**（比另一只高约 14 格） | 脚尖 (58, 112)，**踩在地上** | **红腿（远侧、暗）在前** 20 格 | 红腿踩在前面、往身体下方收，蓝腿（近侧）在后面抬起、膝盖往前摆 |
| 8 | `zippy-run-run8.png` | run@740 | 脚尖 (47, 102)，**抬起来**（比另一只高约 10 格） | 脚尖 (47, 111)，**踩在地上** | **两只脚尖上下对齐（换腿）** | **换腿的一帧**：红腿踩在身体正下方，蓝腿（近侧）抬着从红腿**前面**往前迈，两只脚尖上下对齐，蓝腿盖在上面 |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）、`0_old_run_wrong.png`（上半身照它，腿不要照它）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (its soles on y 1176) - a small BIPEDAL RAPTOR: a ROUND ORANGE-BROWN HEAD with HOT-PINK SPIKES on top, a frill of BLACK SHARDS round the face, BIG HALF-CLOSED PURPLE EYES; one DEEP PURPLE BIB down the front of the neck; LONG HOT-PINK FEATHER LOCKS at both sides of the neck; a MAGENTA SADDLE with gold trim and a gold ring; orange-brown body and thighs, PURPLE ANKLE BANDS, three-toed BLACK CLAWS; an orange-brown tail with PINK SPINES. Image A stands - copy only its look. B its HEAD shown 8x. C a 3D RENDER of this same creature's own game model in THIS FRAME OF ITS RUN, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the pose of the legs, never its 3D shading). D the SKELETON of that frame, exactly over C: green = the spine, the BLUE line = its NEAR leg, the RED line = its FAR leg, BROWN = the tail, PINK and CYAN = the feather locks, GREY BOX = where the head goes, the red horizontal line = the ground. E its whole run cycle, 8 frames in a row. F its OLD run: copy its UPPER BODY - the head, the feathers, the bib, the saddle, the body and the tail, their size and drawing; NOT its legs (crossed out: wrong).
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 10 px, aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (the orange-brown thigh with its light orange, the purple ankle band with its light purple, the dark brown foot, the black claws), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design (the thigh and shin all #883713 with #66250A in the shade, the ankle band #5F1868 with #3D0942, the claws unchanged), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the two PASSING frames the toes are one above the other: one foot planted under the body, the other lifted beside it. Each foot exactly where D puts it; one foot on the ground, the other lifted unless the line says both are down.
COUNT THE SQUARES: the same body size in every frame and the same as image F's upper body; the feet as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned. Nothing covers the face.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - the near (BLUE) leg swinging forward in the air, reaching ahead, about to land; the far (RED, darker) foot planted behind, pushing off. the BLUE leg's foot LIFTED, its toe at square (53, 100), the RED leg's foot ON THE GROUND, its toe at square (45, 109); the two toes 8 squares apart, the BLUE one ahead.`
- run2: `RUN 2 of 8 - the near (BLUE) foot planted ahead - the near leg's widest stride; the far (RED) foot behind, its heel up, just leaving the ground. the BLUE leg's foot ON THE GROUND, its toe at square (59, 110), the RED leg's foot ON THE GROUND, its toe at square (45, 108); the two toes 14 squares apart, the BLUE one ahead.`
- run3: `RUN 3 of 8 - THE PASSING: the near (BLUE) foot planted right under the body; the far (RED, darker) leg lifted, knee forward, its foot passing BEHIND the blue leg - the two toes one above the other, the blue leg drawn over it. the BLUE leg's foot ON THE GROUND, its toe at square (55, 112), the RED leg's foot LIFTED, its toe at square (55, 97); the two toes 0 squares apart.`
- run4: `RUN 4 of 8 - the far (RED, darker) leg now FORWARD, swinging ahead in the air; the near (BLUE) foot planted under the back of the body, pushing back. the BLUE leg's foot ON THE GROUND, its toe at square (45, 112), the RED leg's foot LIFTED, its toe at square (62, 99); the two toes 17 squares apart, the RED one ahead.`
- run5: `RUN 5 of 8 - the far (RED) leg reaching further ahead in the air; the near (BLUE) foot pushing off behind, its heel up. the BLUE leg's foot ON THE GROUND, its toe at square (37, 108), the RED leg's foot LIFTED, its toe at square (64, 99); the two toes 27 squares apart, the RED one ahead.`
- run6: `RUN 6 of 8 - the far (RED) foot landing far ahead - the widest split of the cycle; the near (BLUE) foot just leaving the ground behind. the BLUE leg's foot ON THE GROUND, its toe at square (34, 111), the RED leg's foot ON THE GROUND, its toe at square (64, 111); the two toes 30 squares apart, the RED one ahead.`
- run7: `RUN 7 of 8 - the far (RED) foot planted ahead, sliding back under the chest; the near (BLUE) leg lifted behind, its knee swinging forward. the BLUE leg's foot LIFTED, its toe at square (38, 97), the RED leg's foot ON THE GROUND, its toe at square (58, 112); the two toes 20 squares apart, the RED one ahead.`
- run8: `RUN 8 of 8 - THE PASSING: the far (RED) foot planted under the body; the near (BLUE) leg lifted, passing IN FRONT of it, the two toes one above the other, the blue leg drawn over the red. the BLUE leg's foot LIFTED, its toe at square (47, 102), the RED leg's foot ON THE GROUND, its toe at square (47, 111); the two toes 0 squares apart.`

## 交回

- 每帧一张：`outputs/zippy-run/zippy-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 10 px）；原始生成图原样放进 `outputs/zippy-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只脚尖的格子和距离（上表）、**谁在前**、**两帧换腿是不是真的交错**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**，不对就重画那一帧；`validation.json` 里写下每帧两只脚尖实际在哪一格、谁在前。
- **8 帧都画完再交**，最后写 `outputs/zippy-run/HANDOFF.md`，再打包成 `outputs/zippy_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/zippy/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的脸（design_zippy_poses.py 的读法），逐帧对 `feet.json` 量两只脚尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身大小八帧一致（必要时一个上半身用到八帧，design_sevika_run.py 的做法）。
- 每帧在游戏里的时长（ms，按片段的间隔分 800 ms 一个循环）：[120, 135, 105, 80, 80, 100, 120, 60]。
- 这份提示词和参考图由 `tools/art/pack_zippy_run.py` 生成。
