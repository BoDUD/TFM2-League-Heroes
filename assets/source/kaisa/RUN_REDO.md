# 卡莎：跑步重画（给 Codex，只画 1 张：`kaisa_run.png`）

> 用户看了跑步不满意。上一轮你交的跑步：**迈出去的那条腿整条涂成描边色 `#160722`，是一根深色细条，像尾巴**；而且**一个循环里同一条腿一直踩在地上**（从身前慢慢滑到身后再跳回身前），等于一个循环只迈一步，英雄联盟同样 0.93 秒迈两步。Claude 自己重画的腿用户也不满意：「不自然」（腿像两根管子拼在胯下）。两版都在 `wrong/` 里，**不要重复它们的问题**。
> 这一轮只重画跑步这一张：8 帧、每帧 116 毫秒，排版、格子、站位和上一轮完全一样（`kaisa_cells.json`、`guide/kaisa_guide_run.png`）。其他动作不用动。

## 附图

| 文件 | 内容 | 用法 |
|---|---|---|
| `design/kaisa_design.png` | 定稿造型 B44（8 倍） | 第一张附图：长相、翼舱、配色、像素风格 |
| `lol/kaisa_now_run.png` | 英雄联盟跑步按游戏尺寸取色（8 倍，4×2 格） | 第二张附图：帧数、大小、站位 |
| `lol/lol_run_side.png` | 英雄联盟跑步的 8 帧侧面渲染 | 第三张附图：**腿怎么迈**（大步、后脚往上踢、两腿交替交叉） |
| `legs/kaisa_idle_legs.png` | 定稿造型的腿（18 倍，带格子和颜色说明） | 第四张附图：**每条腿的部件和颜色** |
| `lol/lol_run_pose.png` | 英雄联盟跑步的 3/4 渲染（和 now 条同样的格子） | 需要时看身体和手臂的摆动 |
| `kaisa_idle.png` | 已做好的待机条 | 看大小和站位 |
| `guide/kaisa_guide_run.png`、`kaisa_cells.json` | 每格边框、站位点、脚底线（第 81 行方块，红线下面不能画） | 对位 |
| `design/kaisa_head_1x.png`、`kaisa_palette.png` | 贴头用的头、色板（34 色） | 整理用 |
| `wrong/1_codex_run.png` | ✗ 上一轮你交的跑步（3 倍）：摆动腿是一整块黑条，一条腿一直着地 | 反例 |
| `wrong/2_claude_fix.png` | ✗ Claude 重画的腿（3 倍）：腿像两根管子、不自然 | 反例 |

## 必须做到（逐条检查）

1. **两条腿都按第四张图画**：大腿 5 格宽（含 1 格描边），外侧深紫腿甲 `#352657`，上沿亮边 `#463970`/`#887CBF`，下沿暗部 `#2A1F46`，外侧一小段洋红发光纹 `#F408EA`，**大腿内侧上半截是浅钢蓝紧身衣** `#8F9FC6`/`#6778AB`；金色护膝 `#D7A965`+`#F7D896`；小腿 4 格宽（含描边）；淡紫色爪靴 `#887CBF`/`#6D5EA2` 约 5 格长。远处那条腿同样的部件和颜色（腿甲可以偏暗一阶）。**描边色 `#160722` 只能是腿外面那一圈，绝不能把整条腿涂成它。**
2. **一个循环迈两步**：第 1–4 帧近处的腿（屏幕上靠左的那条）在第 1 帧落在身前并一直踩地、往身后移；远处的腿第 1 帧在身后蹬地、第 2 帧脚跟往后上踢、第 3 帧膝盖往前越过近腿（两腿交叉）、第 4 帧往前伸；第 5–8 帧左右腿互换。第 8 帧接回第 1 帧。
3. **步子要大**（照第三张图）：前脚落在胯前 6–8 格、后脚在胯后 6–8 格。
4. **腿和身体连成一体**：腿从胯下长出来，没有缝、没有错位，紧身衣从小腹一直延续到大腿内侧（和造型图一样）。
5. **上半身是造型图的上半身**：头逐格贴造型图的头；两片翼舱抬在肩后、贴着背；稍微前倾；**手臂和腿反向摆**（近腿在前时近手在后）；爪手至少 2×2、手臂至少 3 格粗。
6. **一起起伏**：落地帧（1、5）整个上半身低 1 格，腾空/交叉帧（3、7）高 1 格；头、身体、头发、翼舱作为一个整体动；头相对站位点的横向位置每帧不变。
7. 落地的脚平踩在第 81 行方块（脚底线），抬起的脚在它上面，**脚底线以下什么都没有**。
8. 只用造型图的 34 种颜色；每个像素 8×8 方块对齐一个网格；背景透明（做不到用纯绿 `#00FF00`，**不要品红**）；不画特效、影子、尘土；不要网格线、边框、文字。

## 提示词（英文，生成时附四张图：`design/kaisa_design.png`、`lol/kaisa_now_run.png`、`lol/lol_run_side.png`、`legs/kaisa_idle_legs.png`）

```text
Four attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, the two raised wing-pods, the head, face, hair, clawed hands and pixel style exactly. SECOND: her running animation in the original game, sampled at game size at 8x, 8 frames in a 4x2 grid of cells - copy the number of frames, the size and where she stands in each cell, but NOT its blurry look. THIRD: the same 8 frames of the original 3D run seen from the side - copy the motion of the LEGS from it: long running strides, the back foot kicked up behind, the legs alternating and crossing. FOURTH: the design's legs at 18x with their colors named - every leg you draw is made of exactly these parts and colors.
Task: draw an 8-frame RUN loop of the character in the FIRST image, facing right in the same 3/4 front view, as clean pixel art identical in style and size to the FIRST image (44 squares tall from the pods' tips to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's colors.
The run (most important): TWO steps per loop, 116 ms a frame. Frames 1-4: her NEAR leg lands in front in frame 1 and stays planted on the ground while it moves back under and behind her; her FAR leg pushes off behind in frame 1, its heel kicks up behind her in frame 2, its knee swings forward past the near leg in frame 3 (the legs cross) and it reaches forward in frame 4. Frames 5-8: the same with the legs swapped (the far leg lands in front in frame 5, the near leg kicks up behind in 6, swings past in 7, reaches forward in 8). Frame 8 flows into frame 1. The stride is long like the THIRD image: the front foot about 6-8 squares ahead of the hips, the back foot 6-8 squares behind.
The legs (most important): BOTH legs are drawn like the FOURTH image, never as a dark silhouette: each thigh 5 squares wide including its 1-square outline - a dark violet plate (#352657) with a lighter violet rim (#463970 / #887CBF) on its upper edge and the darker shade (#2A1F46) on its lower edge, a short magenta slit (#F408EA) on the outer thigh, and the pale steel-blue bodysuit (#8F9FC6 / #6778AB) on the inner side of the upper thigh; a gold knee cap (#D7A965 with a #F7D896 highlight); each shin 4 squares wide including the outline, dark violet with a lighter rim; each boot a lavender (#887CBF / #6D5EA2) clawed boot about 5 squares long. The far leg uses the same parts and colors (its plates may use the darker shades). The outline color #160722 is ONLY the 1-square outline round each leg, never the inside of a leg.
The body: the upper body is the FIRST image's - the head (hair, face, eyes, marks) copied square for square in every frame, the two wing-pods raised behind her shoulders and joined to her back, the pale bodysuit and the armour - leaning slightly forward. The arms swing opposite to the legs (the near arm back when the near leg is in front), the clawed hands readable (at least 2x2 squares, arms at least 3 squares thick). The whole body bobs with the steps: one square lower on the landing frames (1 and 5), one square higher in the passing frames (3 and 7); the head, body, hair and pods move together as one block, the head keeping one horizontal place relative to the standing point. The legs join the hips with NO gap and NO seam: the bodysuit runs down from the belly into the inner thighs exactly as in the FIRST image.
Feet line: in every cell the lowest row of her boots is square row 81 from the top of the cell (pixels 648-655): the planted foot stands flat on it, the lifted foot is above it, NOTHING below it (the game draws the health bar there). Her standing point in each cell is in kaisa_cells.json (as in the SECOND image).
Do not draw effects, shadows or dust - only the character. Transparent background (if not possible: solid pure green #00FF00, never magenta).
Layout: exactly like the SECOND image - 4 columns x 2 rows of 96x96-square cells (768x768 px each), image 3072x1536, frame N in the same cell as in the SECOND image. No grid lines, no borders, no labels.
Before finishing, check every frame: both legs have the FOURTH image's colors (no leg filled with #160722), the legs alternate (frames 1-4 the near leg planted, 5-8 the far leg), the legs join the hips without a gap, the head is the FIRST image's head, both pods are there, nothing below the feet line, only the FIRST image's colors, every square 8x8 on one grid.
```

## 交付

`outputs/kaisa-run-redo/kaisa_run.png`（3072×1536，8 倍，4×2 格，和上一轮同样的排版）+ `HANDOFF.md`（用了哪段提示词、逐条自查结果）+ `manifest.json`（每帧格子矩形、站位点、不透明范围），最好再打一个 zip。

## Claude 收到后（给 Claude 看）

`fix_kaisa_strips.py` 里的跑步重建去掉，新的 `kaisa_run.png` 放进 assets/source/kaisa/codex_strips 和 native，`import_native.py --hero kaisa`；逐帧检查腿的颜色（没有整块描边色）、两腿交替、胯部接缝、头和翼舱；做跑步 GIF 给用户看。
