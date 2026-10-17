# 瑞兹：只重画移动（跑步）这一条（给 Codex 的提示词）

> **其余 7 条动作已经定了，不用动。** 上一轮你的生图原稿（`generation_sources/`）我按它自己的格子重新读了、贴回定稿的头，用户通过了攻击、Q、连招、大招、落地、受击、死亡。**只有移动这条要重画**：上一轮的 8 帧里**一直是同一条腿（近腿，亮铜护膝那条）在前**，第 2 帧和第 6 帧几乎一样，手臂也从不换边，看起来像跛着走，没有交叉步（`current/ryze_run_legs_now.png` 里标出来了）。
> - **这次的要求只有一个重点：两条腿轮流在前。** 第 1–4 帧近腿（画在前面、离镜头近的那条）在前，第 5–8 帧远腿（画在后面那条）在前；第 3 帧远腿的膝盖从近腿后面摆过去，第 7 帧近腿的膝盖从远腿前面摆过去（两膝交错）；手臂和腿反着摆（近腿在前时近手在后）。**`legs/ryze_run_legs.png` 每格画好了腿和手臂的位置：橙色 = 近腿、近手，蓝色 = 远腿、远手**，照它摆，但**成品里不要出现橙色、蓝色**——两条腿都是待机的颜色（石板蓝灯笼裤、铜护膝、棕靴子），不要一条亮一条暗。
> - **画法和上一轮一样**：用内置 image_gen 生图，附图顺序：① `design/ryze_design.png`（定稿造型，放大 8 倍）② `legs/ryze_run_legs.png`（腿位图）③ `pose/lol_pose_run.png`（英雄联盟原版跑步的高清渲染）。大小和像素风格照上一轮的原稿（`refs/ryze_run_raw_prev.png`，1846×852，4 列 × 2 行，人物约 40 格高、每格约 6 像素）——**只看它的大小和画风，它的腿是错的，不要照抄腿**。
> - **这次不用你自己转像素格、不用贴头、不用对位**：直接交生图原稿（透明底 PNG，8 帧按 4 列 × 2 行排，帧和帧之间留空，不要跨格），转换、贴头、放进格子由 Claude 来做。可以多生几张，挑两条腿真的轮流在前的那张；挑不出来就都交。
> - 交回：`ryze_run_raw.png`（选中的那张）、其余候选 `ryze_run_raw_B.png` 等、`generation_prompts.json`、最后写 `HANDOFF.md`（每张是哪条提示词、第几次生成、你检查到哪一帧哪条腿在前），打成 `ryze_run_redo_done.zip` 放在 outputs 里。

## 每帧的腿和手（和腿位图一样）

| 帧 | 近腿（橙） | 远腿（蓝） | 手臂 | 身体 |
|---|---|---|---|---|
| 1 | 在前，脚跟着地 | 在后，脚刚离地 | 近手在后、远手在前 | 正常 |
| 2 | 踩在身体下面 | 在后，脚跟踢起 | 近手在后、远手在前 | 下沉 1 格 |
| 3 | 踩在身体下面偏后 | **膝盖从近腿后面往前摆过去** | 两手经过身体两侧 | 正常 |
| 4 | 在后蹬地，脚跟抬起 | 在前，抬起往前伸 | 近手往前、远手往后 | 上升 1 格 |
| 5 | 在后，脚刚离地 | **在前，脚跟着地** | **近手在前、远手在后** | 正常 |
| 6 | 在后，脚跟踢起 | 踩在身体下面 | 近手在前、远手在后 | 下沉 1 格 |
| 7 | **膝盖从远腿前面往前摆过去** | 踩在身体下面偏后 | 两手经过身体两侧 | 正常 |
| 8 | 在前，抬起往前伸 | 在后蹬地，脚跟抬起 | 近手往后、远手往前 | 上升 1 格 |

- 第 2 帧和第 6 帧、第 4 帧和第 8 帧**是反的**：前面那条腿换了，手臂也换了；
- 两只靴子最多相距约 10 格；着地的靴子踩在脚底线上，抬起的最多离地 2 格；
- 头每帧在同一个横向位置（相对站位点），身体只上下 1 格；卷轴在背上跟着身体；
- 8 帧 × 133 毫秒，第 8 帧能接回第 1 帧；朝右跑，3/4 正面，看得见脸。

## 附图

| 文件 | 内容 |
|---|---|
| `design/ryze_design.png`、`_1x.png`、`ryze_palette.png`、`ryze_head.png` | 定稿造型（放大 8 倍 / 原尺寸）、30 色色板、贴回的头 |
| `ryze_idle.png` | 已做好的待机条（造型图本身，站在站位点上） |
| `legs/ryze_run_legs.png` | **腿位图**：每格的近腿/近手（橙）、远腿/远手（蓝）、站位点（黑十字）、脚底线（红），底下淡灰是英雄联盟原版那一帧 |
| `pose/lol_pose_run.png` | 英雄联盟原版跑步的高清渲染（同样的格子） |
| `now/ryze_now_run.png`、`guide/ryze_guide_run.png` | 原版按游戏尺寸取样、格子和站位点 |
| `current/ryze_run_now.png`、`current/ryze_run_legs_now.png` | 现在的跑步（错的：近腿一直在前） |
| `refs/ryze_run_raw_prev.png` | 你上一轮的原稿：只看大小和画风 |
| `ryze_cells.json` | 每帧站位点（格子 104×96 方块，脚底线第 81 行）和时长 |
| `style/quality_bar.png` | main 里英雄的像素大小和干净程度 |

## 提示词（英文，生图用）

```text
Three attached images. FIRST: the approved pixel-art design of this character at 8x (every pixel an 8x8 block) - copy
its colors, head, face, clothes, scroll and pixel style exactly. SECOND: a leg-and-arm chart with 8 frames in a grid
of 4 columns and 2 rows: in each cell the NEAR leg and NEAR arm (the ones closer to the viewer, drawn in front) are
ORANGE and the FAR leg and FAR arm are BLUE; the black cross is where he stands, the red line is the ground. THIRD: the
original 3D run at the same 8 frames. Draw the character of the FIRST image running to the right in 8 frames placed
like the SECOND image, posing each frame's legs and arms EXACTLY as the colored limbs of the SECOND image - but in the
FIRST image's colors only (both legs the same slate-blue baggy trousers, bronze knee guards and brown boots; both arms
the same blue-violet skin with brown bracers): never orange or blue limbs.
The legs MUST alternate: in frames 1-4 the near leg is the forward one, in frames 5-8 the far leg is the forward one.
Frame 2 and frame 6 are opposite (the other leg in front, the other arm forward); frame 3: the far knee swings forward
past the near standing leg; frame 7: the near knee swings forward past the far standing leg. The arms swing against
the legs. The boots at most about 10 squares apart, the planted boot on the ground line, the lifted one at most 2
squares up; the head keeps the same horizontal place in all 8 frames, the body bobs at most 1 square (down in frames
2 and 6, up in 4 and 8); the scroll rides on his back; 3/4 front view facing right, the face visible; frame 8 flows
into frame 1.
The character: Ryze, the rune mage (a sturdy bald man with blue-violet skin covered in rune tattoos, glowing eyes and a
long brown beard; a sleeveless navy tunic, brown leather straps and a big bronze buckle, baggy trousers, bronze knee
guards; a huge parchment scroll carried on his back). Keep the FIRST image's proportions: big head, thick short arms,
big 3x3 hands, sturdy body, short legs.
Pixel art exactly like the FIRST image: about 40 squares from the top of the scroll to the soles, every pixel one crisp
square on one grid, no anti-aliasing, no blur, a 1-square near-black outline, only the FIRST image's colors, no
dithering or noise. Transparent background (if not possible: solid #FF00FF magenta). One frame per cell, nothing
crossing into the next cell; no grid lines, labels, numbers or guide marks.
```

## 交回前自查

- [ ] 第 1–4 帧近腿在前、第 5–8 帧远腿在前（逐帧看前面那条腿是哪条：近腿画在远腿前面）；
- [ ] 第 2/6 帧、第 4/8 帧前后腿相反，手臂也相反；第 3、7 帧两膝交错；
- [ ] 两条腿颜色一样（待机的颜色），没有橙色、蓝色；
- [ ] 靴距不超过约 10 格，着地的脚在地上，头的横向位置每帧一样；
- [ ] 造型、颜色、卷轴、脸和上一轮一样（定稿），朝右、看得见脸；
- [ ] 每帧在自己的格子里，没有跨格；透明底；HANDOFF.md 最后写。

## Claude 导入时

- `ry/tools/art/fix_ryze_strips.py`：原稿放进 `assets/source/ryze/codex_strips/raw/ryze_run_raw.png`（旧的那张改名留档），量格子大小（TRUE["run"]），按待机的头顶到靴底高度缩、贴头、放进格子；
- 逐帧核对两腿交替（第 2/6 帧前腿相反）、两膝交错、靴距、腿的颜色一致、头的横向位置；`import_native.py --hero ryze` 后出动图给用户审核。
