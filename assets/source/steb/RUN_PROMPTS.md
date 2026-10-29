# 斯特卜：跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - **跑步一定要有交叉步、看得出两条腿轮流在前**。以前几个英雄的跑步被用户退回过（「换腿不明显」「走路腿没有前后交换」）：八帧只画了半个循环、两条腿画成一样的颜色。这次照下面做。
> - 金铲铲里他是这样跑的（`0_run_cycle.png`，8 帧是**一个完整的循环**，1.30 秒迈两步）：身体前倾，两手握着警棍随步子摆，**两条腿轮流迈步**——第 1、2、3、8 帧远侧那条腿在前，第 4、7 帧两条腿交错经过（**换腿、交叉**），第 5、6 帧近侧那条腿在前。
> - 请你画 **8 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（他金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 9 px 放在这张画布上。**请严格用每格 9 px**。
> - **样子、颜色、画法全照定稿** `0_design.png`：浅海绿皮肤、青绿飞机头、鱼鳍耳、蓝色执法官制服、胸前药包、背后的大棕皮背包、两根蓝钢警棍（跑的时候两只手各握一根，照参考图随步子摆）。**八帧的上半身一样大**、跟着步子上下起伏 0–2 格。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。警棍不要挡住脸。

## 最要紧的：两条腿看得出谁在前、有交叉步

骨架里 **蓝线 = 近侧的腿**（他的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（灰紫裤子 `#564A68` 带暗面 `#2E2A4A`、墨绿靴子 `#364A42` / `#17282F`、靴口和脚踝的金环），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：裤子全用 `#2E2A4A`、靴子全用 `#17282F`、金环全用 `#A46222`；**永远在近侧那条腿后面**。
- 两只靴子每帧都要露出来。

**哪条腿在前（靴子更靠画面右边）每半个循环换一次**：第 1、2、3、8 帧**暗的红腿在前**，第 5、6 帧**亮的蓝腿在前**，第 4、7 帧两只靴子几乎上下对齐（换腿的那一刻，两条腿**交叉**：一条从另一条后面经过，蓝腿盖在上面）。

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只靴尖之间的距离照表**。没有哪只靴子是一直不动的：两只靴子轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
| 1 | `steb-run-run1.png` | run@0 | 95 | 靴尖 (66, 122)，**踩在地上** | 靴尖 (102, 125)，**踩在地上** | **红腿（远侧、暗）在前** 36 格 | 红腿（远侧、暗）大步迈在前面，蓝腿（近侧）在后面蹬地，两只靴子分得最开 |
| 2 | `steb-run-run2.png` | run@200 | 90 | 靴尖 (62, 116)，**抬起来**（比另一只高约 11 格） | 靴尖 (94, 127)，**踩在地上** | **红腿（远侧、暗）在前** 32 格 | 红腿踩在前面（往身体下方收），蓝腿在后面**抬起来**、小腿折起 |
| 3 | `steb-run-run3.png` | run@350 | 98 | 靴尖 (67, 121)，**抬起来**（比另一只高约 6 格） | 靴尖 (86, 127)，**踩在地上** | **红腿（远侧、暗）在前** 19 格 | 红腿踩在身体前下方，蓝腿（近侧）膝盖往前摆、靴子从后面往前 |
| 4 | `steb-run-run4.png` | run@500 | 105 | 靴尖 (78, 125)，**踩在地上** | 靴尖 (79, 120)，**抬起来**（比另一只高约 5 格） | 两只靴尖上下对齐（交叉） | **换腿的一帧**：蓝靴（近侧）从红腿旁边经过、和红靴几乎上下对齐，两条腿**交叉**在一起 |
| 5 | `steb-run-run5.png` | run@650 | 98 | 靴尖 (85, 126)，**踩在地上** | 靴尖 (74, 119)，**抬起来**（比另一只高约 6 格） | **蓝腿（近侧）在前** 11 格 | **蓝腿（近侧）在前**踩地，红腿（远侧、暗）在后面 |
| 6 | `steb-run-run6.png` | run@800 | 89 | 靴尖 (84, 127)，**踩在地上** | 靴尖 (73, 111)，**抬起来**（比另一只高约 16 格） | **蓝腿（近侧）在前** 11 格 | 蓝腿踩在身体下方，红腿（远侧）在后面**抬得最高**、开始往前摆 |
| 7 | `steb-run-run7.png` | run@950 | 97 | 靴尖 (79, 127)，**踩在地上** | 靴尖 (78, 115)，**抬起来**（比另一只高约 12 格） | 两只靴尖上下对齐（交叉） | **交叉的一帧**：红腿（远侧、暗）抬着从蓝腿**后面**往前迈过去，两只靴尖上下对齐，蓝腿在上面盖住它 |
| 8 | `steb-run-run8.png` | run@1100 | 101 | 靴尖 (72, 124)，**踩在地上** | 靴尖 (88, 124)，**踩在地上** | **红腿（远侧、暗）在前** 16 格 | 红腿（远侧）往前伸、快落地，蓝腿在后面蹬地、脚跟抬起 |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (his soles on y 1176) - a TALL, LEAN BUT STURDY YOUNG FISH-FOLK MAN: pale sea-green skin, a teal quiff, pointed green fin ears, pale cyan eyes; a BLUE ENFORCER UNIFORM with gold trim, brown leather medicine pouches on crossed straps, a dark brown belt, GREY-PURPLE TROUSERS, DARK BOTTLE-GREEN TALL BOOTS with GOLD RINGS at the top and the ankle; a BIG BROWN LEATHER BACKPACK on his back; TWO blue steel SIDE-HANDLE BATONS with brass heads (while running one in each hand, swinging as in C). Image A stands idle - copy only his look. B his HEAD shown 8x. C a 3D RENDER of this same character's own game model in THIS FRAME OF HIS RUN, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the pose of the body and legs, never its 3D shading). D the SKELETON of that frame, exactly over C: green = the spine, ORANGE = his right arm, CYAN = his left arm, PURPLE bars = the batons (GOLD DOT = the brass head), BROWN outline = the backpack, the BLUE line = his NEAR leg, the RED line = his FAR leg, GREY BOX = where the head goes, the red horizontal line = the ground. E his whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 9 px, aligned on one straight grid from the canvas corner; his lowest point on y 1176.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (grey-purple trousers with their shade, the bottle-green boot with its gold rings), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design (trousers all #2E2A4A, boots all #17282F, the gold rings all #A46222), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. In the PASSING / CROSSING frames the two legs cross: one passes behind the other, the near leg drawn over it. Each boot exactly where D puts it; one boot on the ground, the other lifted unless the line says both are down. Both boots always visible.
COUNT THE SQUARES: the same body size in every frame and the same as image A; the boots as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. Nothing covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - the far (RED, darker) leg striding far ahead, the near (BLUE) leg pushing off behind - the widest split. the BLUE leg's boot ON THE GROUND, its toe at square (66, 122), the RED leg's boot ON THE GROUND, its toe at square (102, 125); the two toes 36 squares apart, the RED one ahead; about 95 squares tall.`
- run2: `RUN 2 of 8 - the far (RED) foot planted ahead, sliding back under him; the near (BLUE) leg LIFTED behind, its shin folded. the BLUE leg's boot LIFTED, its toe at square (62, 116), the RED leg's boot ON THE GROUND, its toe at square (94, 127); the two toes 32 squares apart, the RED one ahead; about 90 squares tall.`
- run3: `RUN 3 of 8 - the far (RED) foot planted a little ahead; the near (BLUE) knee swinging forward, its boot coming through. the BLUE leg's boot LIFTED, its toe at square (67, 121), the RED leg's boot ON THE GROUND, its toe at square (86, 127); the two toes 19 squares apart, the RED one ahead; about 98 squares tall.`
- run4: `RUN 4 of 8 - THE PASSING: the near (BLUE) boot passes right beside the far (RED) one, the toes one above the other, the legs crossing. the BLUE leg's boot ON THE GROUND, its toe at square (78, 125), the RED leg's boot LIFTED, its toe at square (79, 120); the two toes 1 square apart; about 105 squares tall.`
- run5: `RUN 5 of 8 - the near (BLUE) leg FORWARD, planted; the far (RED, darker) leg behind. the BLUE leg's boot ON THE GROUND, its toe at square (85, 126), the RED leg's boot LIFTED, its toe at square (74, 119); the two toes 11 squares apart, the BLUE one ahead; about 98 squares tall.`
- run6: `RUN 6 of 8 - the near (BLUE) foot planted under him; the far (RED) leg LIFTED high behind, starting to swing forward. the BLUE leg's boot ON THE GROUND, its toe at square (84, 127), the RED leg's boot LIFTED, its toe at square (73, 111); the two toes 11 squares apart, the BLUE one ahead; about 89 squares tall.`
- run7: `RUN 7 of 8 - THE CROSSING: the far (RED) leg swinging forward BEHIND the planted near (BLUE) leg, the two toes one above the other, the blue leg drawn over it. the BLUE leg's boot ON THE GROUND, its toe at square (79, 127), the RED leg's boot LIFTED, its toe at square (78, 115); the two toes 1 square apart; about 97 squares tall.`
- run8: `RUN 8 of 8 - the far (RED) leg reaching forward, about to land; the near (BLUE) leg pushing off behind, its heel up. the BLUE leg's boot ON THE GROUND, its toe at square (72, 124), the RED leg's boot ON THE GROUND, its toe at square (88, 124); the two toes 16 squares apart, the RED one ahead; about 101 squares tall.`

## 交回

- 每帧一张：`outputs/steb-run/steb-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/steb-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只靴尖的格子和距离（上表）、**谁在前**、**交叉的帧两条腿真的交叉**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**，不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格、谁在前。
- **8 帧都画完再交**，最后写 `outputs/steb-run/HANDOFF.md`，再打包成 `outputs/steb_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/steb/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头，逐帧对 `feet.json` 量两只靴尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 880 ms 一个循环）：[135, 102, 102, 102, 102, 102, 102, 135]。
- 这份提示词和参考图由 `tools/art/pack_steb_run.py` 生成。
