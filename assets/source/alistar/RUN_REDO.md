# 阿利斯塔：跑步的腿重画（给 Codex 的提示词）

> 用户看了游戏里的跑步：**「牛头走路没有交叉步」「单脚走路的」「走路和待机的体型不一样？？走路还会变大？？」**（`rejected/codex_run.png`：每帧只看得到一条腿，身体比待机大一圈）。
> **这一轮只画两条腿。** 上半身已经做好：`alistar_run_base.png` 的 8 格里，每格都是**定稿待机造型本身**（去掉了两条腿，只在着地帧往下沉一格），大小、形状、颜色一格都不能改；导入时我会把上半身原样贴回去，所以你画的上半身会被覆盖，**只有腿会用上**。
> - **在 `alistar_run_base.png` 上，给每一格画上两条腿**：从皮围裙下面、胯部（`alistar_run_guide.png` 里的两个圆圈：青色 = 近腿的胯，洋红 = 远腿的胯）一直画到蹄子，蹄子落在同一格里的十字上（青色十字 = 近腿的蹄子，洋红十字 = 远腿的蹄子；十字在红线上 = 踩在地上，在红线上面 = 抬起来）。
> - **交叉步**：第 1、2、8 帧近腿在前、远腿在后；第 3 帧两腿交错；第 4–6 帧远腿在前、近腿在后；第 7 帧再交错；第 8 帧接回第 1 帧。**每一帧两条腿都要看得见**（近腿压在远腿前面，远腿露出它在后面或前面的那一截），不能只剩一条腿。两只蹄子最远相距约 12 格。
> - **腿就是待机的腿**（`design/alistar_legs.png`）：短粗的蓝紫色毛腿、脚踝一圈蓬松的毛、深棕色的偶蹄，**两条腿一样的颜色**，粗细和待机一样，不能变细变长。往前迈的腿膝盖微弯、蹄尖朝前；往后蹬的腿伸直、蹄子在后面；抬起的那条离地 1–3 格。腿的上端藏进皮围裙和肚子下面，和身体连在一起，不能有缝。
> - 像素和造型一样：每个像素一个严格对齐的 8×8 色块，只用造型图里的颜色，外轮廓 1 格近黑描边，腿里面不要黑线和杂点。**红线以下什么都不能有**。
> - 动作参考：`refs/lol_run_now.png` / `refs/lol_run_pose.png`（英雄联盟原版的跑步）、`refs/sett_run_approved.png`（包里瑟提的跑步，用户认可过的壮汉交叉步，只看腿怎么交替）。
> - 交付到 `outputs/alistar-run/`：`alistar_run.png`（4096×1536，和 `alistar_run_base.png` 同样的 8 格、同样的位置）、生图原稿 `raw/`、`HANDOFF.md`（**最后写**），最好打成 `alistar_run_done.zip`。

## 附图

| 文件 | 内容 |
|---|---|
| `alistar_run_base.png` | **在这张上画腿**：8 格（4 列 × 2 行，每格 128×96 格 ×8），每格是待机的上半身，站位点 (60, 70)，蹄底在每格第 81 行 |
| `alistar_run_guide.png` | 同样的 8 格加上标记：胯部圆圈、蹄子十字（青 = 近腿，洋红 = 远腿）、脚底红线和下面的禁区、帧号、哪条腿在前 |
| `alistar_run_cells.json` | 每帧站位点和时长（8 × 125 毫秒） |
| `design/alistar_design.png` | 定稿造型（8 倍） |
| `design/alistar_legs.png` | 定稿造型的两条腿单独切出来（8 倍） |
| `refs/lol_run_now.png`、`refs/lol_run_pose.png` | 英雄联盟原版跑步（游戏尺寸 / 渲染） |
| `refs/sett_run_approved.png` | 瑟提的跑步（用户认可的交叉步） |
| `rejected/codex_run.png` | 被退回的版本：单脚、身体变大 |

## 每帧蹄子的位置（游戏像素，相对站位点：x 往右为正；抬起 = 离地几格）

| 帧 | 近腿蹄子 x | 近腿抬起 | 远腿蹄子 x | 远腿抬起 | 谁在前 |
|---|---|---|---|---|---|
| 1 | +2.5 | 0 | -8.0 | 1 | 近腿在前 |
| 2 | +0.0 | 0 | -6.5 | 3 | 近腿在前 |
| 3 | -2.5 | 0 | -3.0 | 3 | 交叉 |
| 4 | -5.0 | 0 | +0.0 | 1 | 远腿在前 |
| 5 | -7.0 | 1 | +1.5 | 0 | 远腿在前 |
| 6 | -5.5 | 3 | -1.0 | 0 | 远腿在前 |
| 7 | -2.0 | 3 | -3.5 | 0 | 近腿在前 |
| 8 | +1.0 | 1 | -6.0 | 0 | 近腿在前 |

## 英文提示词（附图：`alistar_run_base.png`、`alistar_run_guide.png`、`design/alistar_legs.png`、`refs/sett_run_approved.png`、`refs/lol_run_pose.png`，按顺序）

```text
Five attached images. FIRST: a sprite sheet of 8 run frames of a pixel-art character (4 columns x 2 rows of cells, each 128x96 squares at 8x - every pixel an 8x8 block): in every cell the character's upper body is already drawn and final - a huge hunched violet minotaur with a cyan mane, ivory horns, wide iron shackles on both hanging arms and a brown loincloth - but it has NO LEGS yet. SECOND: the same sheet with guides: in each cell two circles mark the hips (cyan = the near leg, magenta = the far leg), two crosses mark where each hoof must be in that frame (cyan = near hoof, magenta = far hoof; a cross on the red line = planted on the ground, above it = lifted), the red line is the ground. THIRD: the character's own two legs from its idle sprite, at 8x - short thick violet furry legs, shaggy fur round the ankles, dark brown cloven hooves; both legs the same colours. FOURTH: another character's approved run (a heavy brawler) - only to see how the two legs alternate and cross. FIFTH: the original 3D run at the same frames.
Task: in every cell of the FIRST image draw the TWO legs, and nothing else: each leg from its hip circle down to its hoof cross of that frame, the legs exactly as thick and coloured as the THIRD image's, the near leg (cyan) in front of the far leg (magenta), both legs visible in every frame. A running stride with crossing legs: frames 1, 2 and 8 the near hoof ahead and the far hoof behind, frame 3 the legs pass each other, frames 4-6 the far hoof ahead and the near hoof behind, frame 7 they pass again, frame 8 flows into frame 1. The forward leg's knee a little bent, the back leg pushing off straight, the lifted hoof 1-3 squares above the ground. The tops of the legs disappear under the loincloth and the belly with no gap. Do not change the upper body at all - not its size, shape, colours or place; it will be pasted back unchanged.
Pixel rules: every pixel an exact 8x8 block on one grid, only the colours of the FIRST and THIRD images, a 1-square near-black outline round each leg, no dithering, no stray specks, no black lines inside the legs. NOTHING below the red line (the game draws the health bar there).
Layout: exactly the FIRST image's size and cells (4096x1536), frame N in the same cell. Transparent background (if not possible: solid #00FF00 green). No grid lines, no guides, no labels.
```

## 骨架 + 皮囊的短提示词（生图画不准时用；图1 = `alistar_run_guide.png`，图2 = `design/alistar_legs.png`）

```text
图1是一张8格的跑步精灵图，每格上半身已经画好（紫色牛头人），但还没有腿；圆圈是胯部，十字是这一帧两只蹄子要落的位置（青色=近腿，洋红=远腿，红线是地面）。
请在每一格里画上两条腿：从胯部圆圈画到同色十字，腿就是图2的腿（短粗的蓝紫色毛腿、黑棕色牛蹄，两条腿颜色一样，粗细不变）。
近腿在前、远腿在后，两条腿每帧都要看得见，前后交替交叉。上半身一点都不要改。每个像素是8×8纯色方块，红线以下不能有像素。
背景保持纯绿色 #00FF00。
```

## Claude 导入时（给 Claude 看）

- 按格子读回（每格取多数色），每帧只取腿（红线以上、身体轮廓以外和皮围裙以下的部分），上半身用造型原样贴回（`tools/art/run_alistar.py` 的 `split` 给出上半身），量每帧两只蹄子的 x，确认近减远每个周期变号两次；补描边、清杂点、检查空洞和碎块，做审核 GIF（统一画布）。
