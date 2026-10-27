# 范德尔：重画跑步（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户看了上一版的跑步，说**「跑步姿势不像啊」**：不像他在金铲铲里的跑法。上一版（`0_old_run_wrong.png`）**弓着背缩着身子，像格斗架势**，而且**前面那只靴子四帧都钉在地上不动**，看起来是在滑。
> - 金铲铲里他是这样跑的（`0_run_cycle.png`，8 帧一个完整循环）：**身子直起来、微微前倾地小跑**，拳套举在胸口 / 肩前（画面左边），缠绷带的拳头在身前（画面右边），**两条腿一前一后轮流迈大步，后面那只脚抬起来往后踢，脚跟离地很高**。
> - 请你画 **8 帧跑步**，每帧一张图，**每帧照它自己的参考图 `*_ref.png` 和骨架 `*_skeleton.png`**（他金铲铲模型自己的跑步动画那一帧，头已经放大到定稿的比例，和画布、格子、位置都对好了）。
> - **这一包的格子是每格 9 px**（不是上一包的 12 px：直起身子跑他比蹲着的定稿高很多，12 px 放不下）。画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。`0_design.png` 是定稿按同样每格 9 px 放在这张画布上。
> - **样子、颜色、画法全照定稿** `0_design.png`：往后梳的深色头发、粗黑浓眉、短络腮胡；焦橙色皮夹克、米白竖条纹马甲、青绿领口、暗红腰带黄铜扣、深藏青牛仔裤、黑工装靴；**画面左边那只手戴着铁拳套**（黄铜八角框、两块红面板、金色六角螺栓，接紫色护臂），另一只手是缠灰白绷带的拳头。像素格、一格粗的近黑描边、平涂，不要 3D 光影。
> - **头一格一格照 `0_head.png` 画在骨架的灰框里**，每帧都是这一个头，只跟着身体上下移动，不要转头、不要画成侧脸。
> - **身高照参考图**：他直着身子跑，**下表「高」那一列是每帧从头顶到脚底的格数**（约 98–117 格），**不要缩成定稿那样的蹲姿**（定稿只有 80 格高）。头（含头发）约 26 × 22 格、拳套约 12 × 12 格、靴子和定稿一样大——这些和定稿一样，变高的是**腿伸直了、背直起来了**。

## 最要紧的：两只靴子

**每一帧画完，数格子核对两只靴子**：靴尖（鞋头最前面那一格）要落在下表写的格子上（x 向右数、y 向下数，从画布左上角第 0 格算起；差 2 格以内可以）。骨架里**红线 = 一条腿，蓝线 = 另一条腿**，「前面的腿」是离镜头近、要画在另一条腿上面的那条（颜色亮一档），后面那条暗一档。

- 第 1–3 帧：**蓝腿踩地**撑着身体往后蹬，**红腿抬起来**从后面往前收；
- 第 4 帧：红腿往前落地，蓝腿在后面脚尖点地；
- 第 5–7 帧：**红腿踩地**，**蓝腿抬起来**从后面往前收；
- 第 8 帧：两腿交错，回到第 1 帧。
- **没有哪只靴子是一直不动的**：两只靴子轮流踩地、轮流抬起，每帧都照下表的格子换位置。

| 帧 | 文件 | 片段 | 高（格） | 红腿 | 蓝腿 | 前面的腿 | 前面的手臂 |
|---|---|---|---|---|---|---|---|
| 1 | `vander-run-run1.png` | run@0 | 117 | 红腿靴尖 (48, 106)，**抬起来**（比另一只高约 21 格） | 蓝腿靴尖 (73, 127)，**踩在地上** | 蓝腿 | 青（绷带拳） |
| 2 | `vander-run-run2.png` | run@133 | 115 | 红腿靴尖 (49, 96)，**抬起来**（比另一只高约 30 格） | 蓝腿靴尖 (78, 126)，**踩在地上** | 蓝腿 | 青（绷带拳） |
| 3 | `vander-run-run3.png` | run@266 | 101 | 红腿靴尖 (56, 102)，**抬起来**（比另一只高约 27 格） | 蓝腿靴尖 (66, 128)，**踩在地上** | 蓝腿 | 青（绷带拳） |
| 4 | `vander-run-run4.png` | run@400 | 110 | 红腿靴尖 (76, 126)，**踩在地上** | 蓝腿靴尖 (46, 125)，**踩在地上** | 红腿 | 橙（拳套） |
| 5 | `vander-run-run5.png` | run@533 | 114 | 红腿靴尖 (85, 128)，**踩在地上** | 蓝腿靴尖 (37, 114)，**抬起来**（比另一只高约 14 格） | 红腿 | 橙（拳套） |
| 6 | `vander-run-run6.png` | run@666 | 116 | 红腿靴尖 (89, 123)，**踩在地上** | 蓝腿靴尖 (37, 104)，**抬起来**（比另一只高约 19 格） | 红腿 | 橙（拳套） |
| 7 | `vander-run-run7.png` | run@800 | 98 | 红腿靴尖 (72, 128)，**踩在地上** | 蓝腿靴尖 (45, 109)，**抬起来**（比另一只高约 19 格） | 红腿 | 橙（拳套） |
| 8 | `vander-run-run8.png` | run@933 | 110 | 红腿靴尖 (59, 122)，**踩在地上** | 蓝腿靴尖 (57, 123)，**踩在地上** | 蓝腿 | 青（绷带拳） |

## 提示词（每帧一次，换掉最后一段）

每次上传：`0_design.png`（定稿）、`0_head.png`（头）、这一帧的 `*_ref.png` 和 `*_skeleton.png`、`0_run_cycle.png`（整个循环）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (his soles on y 1176) - a big, burly middle-aged BRAWLER: swept-back dark hair, thick black brows, a short grey-brown beard; a burnt-orange leather jacket, a cream striped waistcoat, a teal collar, a dark red belt with brass buckles, dark navy jeans, black work boots; on the image-left hand a big IRON GAUNTLET (an octagonal brass frame, two red panels, gold hexagonal bolts) joined to a purple bracer, the other hand a fist wrapped in grey-white bandages. Image A is crouched in a fighting stance - DO NOT copy that crouch, copy only his look. B his HEAD shown 8x (about 26 squares wide, 22 tall). C a 3D RENDER of this same character's own game model in THIS FRAME OF HIS RUN, on the same 1254 canvas and grid, already scaled and placed where the picture must be. D the SKELETON of that frame, exactly over C: green = the spine, ORANGE = the GAUNTLET arm, CYAN = the BANDAGED arm (the big dot = the hand), RED and BLUE = his two legs, GOLD ring = the gauntlet, GREY BOX = where the head goes, the red line = the ground. E his whole run cycle, 8 frames in a row.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px, aligned on one straight grid from the canvas corner; his lowest point on y 1176.
HE IS RUNNING UPRIGHT: the back straight and leaning slightly forward, the legs long and striding, as tall as C (not crouched, not hunched). Copy C's pose exactly: where the hips are, where each knee and each boot is, which boot is on the ground and which is lifted high behind him, where the gauntlet and the bandaged fist are.
THE BOOTS: the RED leg's boot and the BLUE leg's boot exactly where C and D put them (the frame's line below gives each toe's square). One boot on the ground, the other lifted off it unless the line says both are down. The nearer leg in full tone drawn over the other, the far leg a step darker.
COUNT THE SQUARES: the head with the hair about 26 x 22, the gauntlet about 12 x 12, each arm about 16 squares from the shoulder to the fist, the boots as big as in A; a broad, strong body. The gauntlet always on the ORANGE arm's hand; the CYAN arm's hand always the bandaged fist.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box - the same head in every frame, only moved, never turned, never a profile. No fist or gauntlet covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no dust, no motion lines, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THIS FRAME: <the frame's line below>
```

每帧的最后一行（英文）：

- run1: `RUN 1 of 8 - the RED leg's boot LIFTED high behind him, its toe at square (48, 106), the BLUE leg's boot ON THE GROUND, its toe at square (73, 127); the BLUE leg nearer; about 117 squares tall.`
- run2: `RUN 2 of 8 - the RED leg's boot LIFTED high behind him, its toe at square (49, 96), the BLUE leg's boot ON THE GROUND, its toe at square (78, 126); the BLUE leg nearer; about 115 squares tall.`
- run3: `RUN 3 of 8 - the RED leg's boot LIFTED high behind him, its toe at square (56, 102), the BLUE leg's boot ON THE GROUND, its toe at square (66, 128); the BLUE leg nearer; about 101 squares tall.`
- run4: `RUN 4 of 8 - the RED leg's boot ON THE GROUND, its toe at square (76, 126), the BLUE leg's boot ON THE GROUND, its toe at square (46, 125); the RED leg nearer; about 110 squares tall.`
- run5: `RUN 5 of 8 - the RED leg's boot ON THE GROUND, its toe at square (85, 128), the BLUE leg's boot LIFTED high behind him, its toe at square (37, 114); the RED leg nearer; about 114 squares tall.`
- run6: `RUN 6 of 8 - the RED leg's boot ON THE GROUND, its toe at square (89, 123), the BLUE leg's boot LIFTED high behind him, its toe at square (37, 104); the RED leg nearer; about 116 squares tall.`
- run7: `RUN 7 of 8 - the RED leg's boot ON THE GROUND, its toe at square (72, 128), the BLUE leg's boot LIFTED high behind him, its toe at square (45, 109); the RED leg nearer; about 98 squares tall.`
- run8: `RUN 8 of 8 - the RED leg's boot ON THE GROUND, its toe at square (59, 122), the BLUE leg's boot ON THE GROUND, its toe at square (57, 123); the BLUE leg nearer; about 110 squares tall.`

## 交回

- 每帧一张：`outputs/vander-run/vander-run-<名字>.png`（`run1` … `run8`，1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/vander-run/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **画完每帧先自己核对两只靴子的格子**（上表），不对就重画那一帧；`validation.json` 里写下每帧两只靴尖实际在哪一格。
- **8 帧都画完再交**，最后写 `outputs/vander-run/HANDOFF.md`，再打包成 `outputs/vander_run_done.zip`。中间不要停。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/vander/codex_run/`，按 9 px 的格子读回、换成定稿的颜色、贴定稿的头（design_vander_poses.py），逐帧对 `feet.json` 量两只靴尖，连起来播放看有没有滑步。
- 这份提示词和参考图由 `tools/art/pack_vander_run.py` 生成。
