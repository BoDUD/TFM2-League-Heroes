# 塞薇卡：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「走路感觉换腿不明显」**。上一版（`0_old_run_wrong.png`）有两个问题：① 八帧只画了金铲铲跑步动画的**前半个循环**（她的跑步一个循环 1.87 秒、迈两步），所以几乎每帧都是同一条腿在前，播放到最后一帧又一下子跳回第一帧；② **两条腿画成一样的颜色**，看不出哪条腿在前。
> - 金铲铲里她是这样跑的（`0_run_cycle.png`，这次 8 帧是**一个完整的循环**）：机械臂沉沉地垂在身前，**两条腿轮流迈步**——第 1、2、3、8 帧远侧那条腿在前，第 4、7 帧两条腿交错经过（**换腿**），第 5、6 帧近侧那条腿在前。
> - 请你画 **8 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（她金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - 格子每格 **12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 12 px 放在这张画布上。**请严格用每格 12 px**。
> - **样子、颜色、画法全照定稿** `0_design.png`，**上半身（头、躯干、两条胳膊、机械臂、老虎机）的大小和画法照上一版的跑步**（`0_old_run_wrong.png` 上面一排：用户看过、没有意见的就是上半身），**八帧的上半身一样大**、跟着步子上下起伏 0–2 格；要改的只是腿。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。机械臂不要挡住脸。

## 最要紧的：两条腿看得出谁在前

骨架里 **蓝线 = 近侧的腿**（她的右腿，离镜头近），**红线 = 远侧的腿**（左腿）。这两条腿的画法**每一帧都固定**：

- **蓝腿（近侧）**：**完全照定稿的腿的颜色**（深棕裤子 `#604345` 带暗面、藏青护膝 `#454E77` 带高光、小腿露出的浅肤色、深色靴子和金色靴头），**永远画在另一条腿上面**（两条腿在胯下或交叉时重叠的地方，它盖住远侧的腿）。
- **红腿（远侧）**：**整条腿暗一档**，只用定稿里已有的暗色：裤子全用 `#3D2629`、护膝全用 `#292C48`、露出的小腿用 `#CE6F51`、靴子不变；**永远在近侧那条腿后面**。
- 机械臂垂在身前，会挡住一部分腿：照参考图挡，**但两只靴子每帧都要露出来**。

**哪条腿在前（靴子更靠画面右边）每半个循环换一次**：第 1、2、3、8 帧**暗的红腿在前**，第 5、6 帧**亮的蓝腿在前**，第 4、7 帧两只靴子几乎上下对齐（换腿的那一刻）。第 7 帧是**交叉**：暗的红腿从亮的蓝腿后面往前迈，蓝腿盖在上面。

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以），**两只靴尖之间的距离照表**（上一版的毛病就是距离不对、谁在前不对）。没有哪只靴子是一直不动的：两只靴子轮流踩地、轮流抬起。

| 帧 | 文件 | 片段 | 高（格） | 蓝腿（近侧） | 红腿（远侧、暗） | 谁在前 | 腿是什么样子 |
|---|---|---|---|---|---|---|---|
| 1 | `sevika-run-run1.png` | run@0 | 76 | 靴尖 (28, 85)，**抬起来**（比另一只高约 10 格） | 靴尖 (64, 94)，**踩在地上** | **红腿（远侧、暗）在前** 36 格 | 红腿（远侧、暗）在前面踩地，蓝腿（近侧）在后面**向后踢起**、小腿折起来，两只靴子分得最开 |
| 2 | `sevika-run-run2.png` | run@234 | 67 | 靴尖 (32, 85)，**抬起来**（比另一只高约 11 格） | 靴尖 (57, 96)，**踩在地上** | **红腿（远侧、暗）在前** 25 格 | 红腿还踩在前面（往身体下方收），蓝腿在后面抬着、开始往前摆 |
| 3 | `sevika-run-run3.png` | run@468 | 75 | 靴尖 (39, 93)，**踩在地上** | 靴尖 (51, 95)，**踩在地上** | **红腿（远侧、暗）在前** 12 格 | 红腿踩在身体前下方，蓝腿（近侧）膝盖往前摆、靴子低低地从后面往前 |
| 4 | `sevika-run-run4.png` | run@702 | 76 | 靴尖 (46, 95)，**踩在地上** | 靴尖 (45, 93)，**踩在地上** | 两只靴尖上下对齐 | **换腿的一帧**：蓝靴（近侧）落地、和红靴几乎上下对齐，红腿开始抬起 |
| 5 | `sevika-run-run5.png` | run@936 | 77 | 靴尖 (53, 95)，**踩在地上** | 靴尖 (41, 86)，**抬起来**（比另一只高约 9 格） | **蓝腿（近侧）在前** 12 格 | **蓝腿（近侧）在前**踩地，红腿（远侧、暗）在后面向后踢起、小腿折起 |
| 6 | `sevika-run-run6.png` | run@1092 | 71 | 靴尖 (53, 95)，**踩在地上** | 靴尖 (43, 84)，**抬起来**（比另一只高约 11 格） | **蓝腿（近侧）在前** 10 格 | 蓝腿踩在身体下方，红腿（远侧）在后面抬得最高、开始往前摆 |
| 7 | `sevika-run-run7.png` | run@1248 | 71 | 靴尖 (49, 95)，**踩在地上** | 靴尖 (49, 88)，**抬起来**（比另一只高约 8 格） | 两只靴尖上下对齐 | **交叉的一帧**：红腿（远侧、暗）抬着从蓝腿**后面**往前迈过去，两只靴尖上下对齐，蓝腿在上面盖住它 |
| 8 | `sevika-run-run8.png` | run@1560 | 75 | 靴尖 (38, 94)，**踩在地上** | 靴尖 (56, 94)，**踩在地上** | **红腿（远侧、暗）在前** 18 格 | 红腿（远侧）往前伸、快落地，蓝腿在后面蹬地、脚跟抬起 |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）、`0_old_run_wrong.png`（上半身照它，腿不要照它）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (her soles on y 1176) - a BROAD-SHOULDERED, STURDY WOMAN with dark brown hair combed back, a warm square face, thick dark brows, grey eyes; a dark navy short-sleeved top with gold diamond shoulder badges, a brown leather cropped vest (bare midriff), a brown belt with a small grey pouch, dark brown trousers ending at mid-calf with NAVY KNEE PADS, a strip of bare calf, dark boots with GOLD TOE CAPS; her LEFT ARM a HUGE BRASS MECHANICAL ARM (a slot machine on its shoulder, teal plates with magenta spikes, bright cyan claws). Image A stands in a guard - copy only her look. B her HEAD shown 8x. C a 3D RENDER of this same character's own game model in THIS FRAME OF HER RUN, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the pose of the legs, never its 3D shading). D the SKELETON of that frame, exactly over C: green = the spine, ORANGE = her flesh right arm, CYAN = the mechanical arm (the PURPLE line with a GOLD TRIANGLE = its claws, the PURPLE RING = the slot machine), the BLUE line = her NEAR leg, the RED line = her FAR leg, GREY BOX = where the head goes, the red horizontal line = the ground. E her whole run cycle, 8 frames in a row. F her OLD run (top row): copy its UPPER BODY - the head, torso, both arms and the mechanical arm, their size and drawing; NOT its legs (crossed out: wrong).
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square EXACTLY 12 px, aligned on one straight grid from the canvas corner; her lowest point on y 1176.
THE LEGS: the NEAR leg (BLUE line) is drawn in the design's own leg colours exactly as in image A (brown trousers, navy knee pad with its light shade, the bare calf, the boot with its gold toe cap), in full tone, and OVER the far leg wherever they overlap. The FAR leg (RED line) is a step darker all over using only darker colours of the design (trousers all #3D2629, knee pad all #292C48, the bare calf #CE6F51, the boot unchanged), and always BEHIND the near one. Which leg is FORWARD changes from frame to frame: follow C and D and this frame's line below - its toe squares and the gap between the two toes. Each boot exactly where D puts it; one boot on the ground, the other lifted unless the line says both are down. Both boots always visible below the mechanical arm.
COUNT THE SQUARES: the same body size in every frame and the same as image F's upper body; the boots as big as in A; legs bending at the knees along their lines, never stretched or squashed.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. Nothing covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - the far (RED, darker) leg planted far ahead, the near (BLUE) leg kicked up behind, its shin folded - the widest split. the BLUE leg's boot LIFTED, its toe at square (28, 85), the RED leg's boot ON THE GROUND, its toe at square (64, 94); the two toes 36 squares apart, the RED one ahead; about 76 squares tall.`
- run2: `RUN 2 of 8 - the far (RED) foot still planted ahead, sliding back under her; the near (BLUE) leg lifted behind, starting to swing forward. the BLUE leg's boot LIFTED, its toe at square (32, 85), the RED leg's boot ON THE GROUND, its toe at square (57, 96); the two toes 25 squares apart, the RED one ahead; about 67 squares tall.`
- run3: `RUN 3 of 8 - the far (RED) foot planted a little ahead; the near (BLUE) knee swinging forward, its boot low, coming through from behind. the BLUE leg's boot ON THE GROUND, its toe at square (39, 93), the RED leg's boot ON THE GROUND, its toe at square (51, 95); the two toes 12 squares apart, the RED one ahead; about 75 squares tall.`
- run4: `RUN 4 of 8 - THE PASSING: the near (BLUE) boot lands right beside the far (RED) one, the red heel lifting. the BLUE leg's boot ON THE GROUND, its toe at square (46, 95), the RED leg's boot ON THE GROUND, its toe at square (45, 93); the two toes 1 square apart; about 76 squares tall.`
- run5: `RUN 5 of 8 - the near (BLUE) leg FORWARD, planted; the far (RED, darker) leg kicked up behind, folded. the BLUE leg's boot ON THE GROUND, its toe at square (53, 95), the RED leg's boot LIFTED, its toe at square (41, 86); the two toes 12 squares apart, the BLUE one ahead; about 77 squares tall.`
- run6: `RUN 6 of 8 - the near (BLUE) foot planted under her; the far (RED) leg lifted high behind, starting to swing forward. the BLUE leg's boot ON THE GROUND, its toe at square (53, 95), the RED leg's boot LIFTED, its toe at square (43, 84); the two toes 10 squares apart, the BLUE one ahead; about 71 squares tall.`
- run7: `RUN 7 of 8 - THE CROSSING: the far (RED) leg swinging forward BEHIND the planted near (BLUE) leg, the two toes one above the other, the blue leg drawn over it. the BLUE leg's boot ON THE GROUND, its toe at square (49, 95), the RED leg's boot LIFTED, its toe at square (49, 88); the two toes 0 squares apart; about 71 squares tall.`
- run8: `RUN 8 of 8 - the far (RED) leg reaching forward, about to land; the near (BLUE) leg pushing off behind, its heel up. the BLUE leg's boot ON THE GROUND, its toe at square (38, 94), the RED leg's boot ON THE GROUND, its toe at square (56, 94); the two toes 18 squares apart, the RED one ahead; about 75 squares tall.`

## 交回

- 每帧一张：`outputs/sevika-run/sevika-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/sevika-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对**：两只靴尖的格子和距离（上表）、**谁在前**、**蓝腿用定稿的亮色并画在上面、红腿暗一档在后面**，不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格、谁在前。
- **8 帧都画完再交**，最后写 `outputs/sevika-run/HANDOFF.md`，再打包成 `outputs/sevika_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sevika/codex_run/`，按它实际的格子读回、换成定稿的颜色、贴定稿的头（下巴对下巴，design_sevika_poses.py），逐帧对 `feet.json` 量两只靴尖的距离、看谁在前、远侧那条腿是不是暗一档，连起来播放看有没有滑步、两条腿有没有轮流在前；上半身大小八帧一致。
- 每帧在游戏里的时长（ms，按片段的间隔分 936 ms 一个循环）：[117, 117, 117, 117, 78, 78, 156, 155]。
- 这份提示词和参考图由 `tools/art/pack_sevika_run.py` 生成。
