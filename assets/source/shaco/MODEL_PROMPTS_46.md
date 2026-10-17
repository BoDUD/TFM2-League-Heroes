# 萨科：照用户喜欢的图在 46 格上手画（第 1 步第四轮，给 Codex 的提示词）

> **用户喜欢的是 `shaco/shaco_target.png` 这张**（你画的，按它自己的格子读回是 **76 格高**，每格约 7 px）。它的质量就是目标：干净的大块像素、白面具、冰蓝眼、大咧嘴笑、深蓝/红双角帽、金铃、银刺肩甲、红外套、黑白格灯笼裤、带刺靴子、红翘鞋、两把匕首，**瘦长的身材**。
> - 上一轮的 40 格（`compare/v3_40.png`）用户说"缩小后质量太差了"：它变成了矮胖的 Q 版，帽子变小、腿变短，不像这张了。直接删行缩到 46 格（`layout/shaco_layout_46.png`）也不行：格子裤和面具碎成杂点。
> - 用户选了**稍微放大：46 格**（比其他英雄的 40 格高约 15%）。请**在 46 格上一格一格画**这张图，**比例照这张图**（瘦长、帽角高、腿长），只是按 46 格的尺寸简化，不是缩小。可以用脚本按格子放像素（像你的 `redraw_shaco40_v3.py`），但形状和比例必须照 `shaco/shaco_target.png`，不要照 v3。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 22 色，脚底在第 99 行。交付 `shaco_native46_A.png`、`shaco_native46_B.png`（1024×1024）和 `_1x`（128×128），附 `HANDOFF.md`、`generation_prompts.json`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `shaco/shaco_target.png` | 用户喜欢的图（原文件） | **长相和比例**：每个部件的形状、颜色、位置 |
| `shaco/shaco_target_grid.png` | 同一张图读回到它自己的格子（76 格高），放大 6 倍 | 看清每一块怎么画的 |
| `layout/shaco_layout_46.png` | 直接删行缩到 46 格，放在 128×128 画布上（×8，脚底第 99 行） | **只看大小、站位、部件落在哪几格**；是花的，不要照它的样子 |
| `compare/v3_40.png` | 上一轮的 40 格（用户不满意） | **反例**：不要变成这种矮胖比例 |
| `quality/main_clean_heroes.png` | main 里用户认可的阿卡丽、维迦、塔里克，游戏尺寸 ×8 | 干净程度和像素大小 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄 ×8 | 像素大小和干净程度 |

## 规则

- **46 格高**（帽子最高处到脚底），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、半透明。
- **比例照目标图**：帽子（两只角，含铃铛）约 9 格，面具约 9 格（版本 B 约 11 格），领圈 2 格，上身约 9 格，灯笼裤约 9 格，靴子和鞋约 8 格；瘦长，腿不要缩短；整体宽度照目标图（近侧匕首向后伸出）。
- **干净**：大块平涂，每种材质 2–3 个色阶；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；1 格近黑外描边，内部深色线条尽量少；最多 22 色（建议色板取自目标图，见下）。**金色只用在铃铛、领圈、扣子、腰带、肩甲边、靴口**。
- **帽子**：深蓝角向后（图左）弯下来，红角向上再向右弯，各 3–4 格粗、实心，角尖各一个 2×2 金铃（一格亮黄高光）；帽子像兜帽框住面具，近侧深蓝、远侧红。
- **面具（最重要）**：一大块白色面具，帽檐到下巴尖约 9 格（B 约 11 格）。两只冰蓝眼睛**每只 2 格宽、2 格高**，一样大、同一行，中间隔 1–2 格白；每只有一格青白亮芯，四周深色眼窝（和目标图一样凶）；冰蓝只用在眼睛。眼睛下面**大咧嘴笑**：2 格高的深色嘴横贯面具大半，里面一排 4–5 颗白牙（牙与牙之间隔一格深色），嘴角上翘。白色鸟嘴鼻 2 格宽往右下；下巴窄而尖。
- **身体**：金色锯齿领圈；银色肩甲各一根向上的银刺；红色外套前片一大块、深蓝侧片、2 颗金菱形扣、金腰带；深蓝上臂、**大红泡泡袖口**（至少 4 格宽）；淡蓝灰的手（至少 2 格宽）。
- **灯笼裤**：**2×2 的大黑白格**（每条腿 3 列左右），暗面的白格稍灰；不要 1 格碎格。
- **靴子和鞋**：深蓝靴子、金色靴口、左右各一根银刺；红色尖头翘鞋，鞋尖在脚底线以上。
- **匕首**：近侧手（图左）的匕首在胯部高度水平朝后，刃约 6 格（亮白/银灰锯齿边）、金色护手 1 格；远侧手（图右）的匕首朝下，刃约 5 格；都握在手里。
- **脚底线以下什么都不能有**：两只鞋底在同一行，第 99 行（y=792–799），下面一格都不能有。3/4 正面朝右，姿势照目标图。
- 背景透明（做不到用纯品红 `#FF00FF`），不要网格、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

建议色板（取自目标图，共 22 色以内）：#0F0419 outline (the only black); navy #1D264A #334782 #475C75; crimson #9C0D29 #B3112D #FC2D3F; gold #8A5D25 #F3BF27 (+ one pale-gold highlight); mask, checks and steel #F7F7F8 #D1CBDE #AAA3BE #2F2E40; hands #475C75 and a lighter blue-grey; eyes #03A7E9 and a bright cyan-white core (eyes only)。

## 提示词：`shaco_native46_A.png` 和 `shaco_native46_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`shaco/shaco_target.png`、`layout/shaco_layout_46.png`、`quality/main_clean_heroes.png`、`style/tfm2_style_ref.png`；`shaco/shaco_target_grid.png` 和 `compare/v3_40.png` 可以一起附上。

```text
Attached images. FIRST: the picture the user wants - its look AND its proportions are the target: the lanky jester with the two-horned hat (navy horn curling back to the left, crimson horn up and to the right, a gold bell on each tip), the white mask with two glowing ice-cyan eyes, a huge toothy grin and a beak nose, the gold ruff collar, the silver spiked pauldrons, the crimson jacket with gold buttons and belt, the navy upper arms, the big puffy crimson cuffs, the pale blue-grey hands, the black-and-white checkered pantaloons, the navy boots with silver spikes, the crimson curled shoes and the two serrated silver daggers. It is 76 squares tall. SECOND: the FIRST image cut straight to 46 squares on a 1024x1024 canvas at 8x - use it ONLY for the size, the place in the canvas and where each part lands; it is mottled - do not copy its look. THIRD: heroes of this game at game size, 8x, approved by the user - match their cleanliness. FOURTH: official heroes of the game at 8x - the pixel size and cleanliness.
Task: REDRAW the FIRST image square by square as a 46-pixel-tall game sprite (from the top of the hat to the soles), true low-resolution pixel art shown enlarged 8x, every pixel one crisp 8x8 square on a single 8-px grid. Keep the FIRST image's proportions (lanky, tall hat horns, long legs) and every part's shape and colors, simplified for 46 squares - a redraw at game size, not a shrink, and NOT a stubby chibi.
Pixel rules (most important): nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency; at most 22 colors; every material 2-3 flat shades; big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area; a 1-square near-black outline around the silhouette and very few inner dark lines. Gold ONLY on the bells, the collar, the buttons, the belt, the pauldron rims and the boot rims.
Palette (taken from the FIRST image): #0F0419 outline (the only black); navy #1D264A #334782 #475C75; crimson #9C0D29 #B3112D #FC2D3F; gold #8A5D25 #F3BF27 (+ one pale-gold highlight); mask, checks and steel #F7F7F8 #D1CBDE #AAA3BE #2F2E40; hands #475C75 and a lighter blue-grey; eyes #03A7E9 and a bright cyan-white core (eyes only).
Proportions in squares: the hat with its horns and bells about 9, the mask about 9 from the hat brim to the chin tip (VERSION B: 11), the collar 2, the upper body about 9, the pantaloons about 9, the boots and shoes about 8.
Mask (most important): one big white mask (white and pale lavender-grey, shadow only on the far edge). Two ice-cyan eyes, EACH 2 squares wide and 2 squares tall, the same size and on the same rows, 1-2 white squares apart, each with one brighter cyan-white core square, dark sockets round them as in the FIRST image; the cyan used for nothing else; never merged into a bar, never blurred. Under them a HUGE GRIN: a dark mouth 2 squares tall across most of the mask with a row of 4-5 white teeth (one dark square between teeth), the corners curving up - readable as a grin at 1x. A white beak nose 2 squares wide down to the right; a narrow pointed chin.
Hat: each horn solid, 3-4 squares thick, a 2x2 gold bell with a bright highlight at each tip; the hat frames the mask like a hood (navy near side, crimson far side).
Body: a 2-square-tall gold zigzag collar; silver pauldrons with one silver spike up and gold rims; one big crimson jacket front with 2 gold diamond buttons and a gold belt; navy upper arms; BIG round puffy crimson cuffs (at least 4 squares wide); pale blue-grey hands at least 2 squares wide. Pantaloons in BIG 2x2 black and white checks (about 3 columns of checks per leg), never 1-square checks. Navy boots with a gold rim and one silver spike on each side; crimson curled shoes whose tips stay above the soles. Daggers: the near hand's (left) blade horizontal at hip height pointing straight back, about 6 squares with a serrated white/silver edge and a 1-square gold guard; the far hand's (right) blade pointing down, about 5 squares; both held in the hands.
Pose, size and place: the FIRST image's idle pose, 46 squares tall, where the SECOND image stands: the soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom), nothing below it (the game draws the health bar there). 3/4 FRONT view facing right.
Layout: one square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF). No grid lines, no text, no border, no shadow.
Before finishing, check: 46 squares tall, all squares 8x8 on one grid, at most 22 colors, the FIRST image's lanky proportions, both eyes 2x2 and clear, the grin readable at 1x, the hat's two horns and bells, 2x2 checks, two daggers in the hands, gold only where listed, nothing below the soles, and side by side with the FIRST image it is clearly the same picture, only with bigger squares.
VERSION A (shaco_native46_A.png): the mask about 9 squares from the brim to the chin tip.
VERSION B (shaco_native46_B.png): the mask 2 squares bigger (about 11 squares, bigger eyes area and grin), everything else the same, still lanky.
```

## Claude 收到后（给 Claude 看）

- 按格读回，检查 46 格、色数、脚底线、眼睛（2×2、一样大、同一行）、笑容、帽角、格子裤、孤立方块；补齐描边。
- A、B 和目标图、main 英雄放一起（1×、3×、深色卡片）给用户挑；通过后出动作帧包（第 2 步，动作帧也按 46 格画）。
