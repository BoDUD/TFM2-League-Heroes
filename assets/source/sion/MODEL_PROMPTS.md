# 赛恩：游戏尺寸造型，正面 + 侧面在格子上重画（第 1 步，给 Codex 的提示词）

> 用户选了 **A（斧头垂在近侧腿边）**、**44 行**（光头顶到脚底）。你上次的原始稿 A（附图 2，按格子读回）很好看，
> 但缩到 44 行后（附图 1，以及你自己的 85×56 读回）脸太小、到处是零碎杂色格，糊了。这一步请**直接在游戏格子上一格一格重画**：
> 一格 = 游戏里一个像素，画布横版 1536×1024，**每格 19 像素**，网格从 (0,0) 开始（80 列 × 53 行）。
> - **正面（3/4 朝右，待机 + 选人卡用）**：**大小、比例、姿势、位置照附图 1**（光头顶第 7 行，脚底第 50 行，两只靴子、斧头、肩甲的位置都按它），
>   **样子和细节照附图 2**（你自己的原始稿），**用更少更大的色块**把它画清楚：可以为了清楚挪动一两格，但总尺寸不变。
> - **侧面（朝右，之后所有动作都从它画）**：同一个人从正侧面看，**同样 44 行高**（光头顶第 7 行、脚底第 50 行，附图 10 的红线、绿线），
>   脚的中间在第 40 列（蓝线）。参考附图 5（英雄联盟待机的侧面）：**和正面一样，近侧是拿斧头的手臂，肩甲在远侧**。
> - 交付到 `outputs/sion-model/`：`sion-front-1.png`、`sion-front-2.png`（两稿，主要在脸和斧头的画法上不同）、`sion-side-1.png`、`sion-side-2.png`
>   （都是 1536×1024、真透明背景、按 19 像素格子），以及每张的**一格一像素**读回 `*_1x.png`（80×53，逐格一致）；`generation-prompts.txt`，原始稿放 `raw/`，**最后**写 `HANDOFF.md`。

## 附图（压缩包 `sion_model_pack.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_current_grid.png` | 现在的 44 行造型（你的原始稿 A 缩下来的），每格 19 像素 + 黄色量尺格子 + 行列号 | 正面的**大小、比例、姿势、位置**（不是样子：它糊了） |
| `2_look_draft.png` | 你的原始稿 A，按格子读回放大 8 倍 | **样子、颜色、细节**（正面和侧面都照它） |
| `3_league_head.png` | 英雄联盟头部特写 | 光头、红眼、下颌笼尖刺、头顶断剑 + 红飘带 |
| `4_league_front.png` | 英雄联盟待机 3/4 正面 | 结构 |
| `5_league_side.png` | 英雄联盟待机的侧面（朝右） | **侧面**的姿势和结构 |
| `6_league_axe.png` | 斧头举起来的样子 | 斧头形状 |
| `7_style_darius.png`、`8_style_nautilus.png`、`9_style_alistar.png` | 包里已经在游戏里的 1 倍英雄，8 倍放大 | **只看干净程度**：大色块、少杂色、1 格描边 |
| `10_side_canvas.png` | 侧面用的空格子：红线 = 光头顶（第 7 行），绿线 = 脚底下沿（第 50 行底），蓝线 = 第 40 列 | 侧面的位置 |

## 提示词 1：正面 `sion-front-1.png` / `sion-front-2.png`

十张图都附上，顺序同上表。两稿各画一次。

```text
Ten attached images. Image 1 is the CURRENT game sprite of this character, every game pixel drawn as a 19x19 square on a 1536x1024 canvas with a yellow measuring grid and row/column numbers: it fixes the SIZE, the PROPORTIONS, the POSE and the PLACE - but it is muddy (a tiny face, specks), do NOT copy its look. Image 2 is your own earlier full picture of this character read back on its grid and shown 8x: copy its LOOK - the shapes, the colours, the details. Images 3-6 are 3D renders from the game (3 the head close-up: the small bald head, the two red glowing eyes, the black iron jaw cage with outward spikes, the broken blade stuck in the top of the head with a red ribbon tied to its hilt; 4 the idle in 3/4 view; 5 the idle from the side - not used for this picture; 6 the axe raised: the axe's shape). Images 7-9 are other characters from the same game at game size shown 8x: copy their CLEANLINESS - big flat areas of colour, few stray squares, a one-square outline. Image 10 is not used for this picture.
Redraw the character at GAME SIZE, square by square: a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha) on the grid of image 1 - squares of 19x19 px from the top-left corner (0,0), 80 columns x 53 rows, every square ONE flat colour, no half squares. Keep image 1's layout: the top of the bald head on row 7, the soles on row 50 (44 rows), the boots, the axe, the pauldron and the far hand where image 1 has them (a square or two of change for clarity is fine, the overall size is not).
The character, as in image 2: a huge HUNCHED undead warrior - an enormous pale grey-lilac muscular upper body, a SMALL bald head, short thick legs in a half crouch. THE FACE MUST READ AT GAME SIZE: the bald head about 9-10 squares wide including its outline; TWO RED EYE squares on the same row with one dark square between them (that red used nowhere else), a dark brow line above them; the lower face a BLACK IRON JAW CAGE 2-3 rows tall with 2-3 light grey SPIKE squares sticking out of its edge and one yellow tooth square; the broken blade on top of the head 1 square wide, a RED RIBBON 2 squares thick fluttering back to the upper left. THE BODY: pale grey-lilac muscles in 3-4 flat shades (light grey-blue on the lit left side, purple-grey in the shadows) shaped as a few big muscle masses, not speckles; two or three DARK RED SCAR lines one square thick; two BLACK IRON DIAMOND PLATES on the chest; on the far shoulder (image right) the HUGE BLACK-IRON SPIKED PAULDRON with three horns pointing up, lit edges in mid grey, two lighter rivet squares; the far forearm in a black iron GAUNTLET with brown straps, its bare hand pale grey-lilac with fingers spread; the near arm bare, a brown leather wrap on the forearm, its hand gripping the haft; the GLOWING RED FURNACE in the middle of the belly (about 4x2 squares, bright red with a pink highlight square - the brightest spot) on the WIDE BLACK IRON BELT with two round iron buckles; BROWN and DARK PLUM-BROWN trousers, a ragged OLIVE loin cloth hanging in front; BIG BLACK IRON BOOTS, one spike on the far boot; the near leg on the image left in full tone, the far leg on the image right a shade darker. THE AXE hanging from the near hand beside the near leg, the blade pointing down and its edge outward: a BROAD CURVED STEEL BLADE at least 9 squares wide in 2-3 cold grey-blue shades with a bright edge line, a leather-wrapped HAFT 2 squares thick, the black iron collar and the small pale grey-green square block where blade and haft meet.
Style: crisp game-size pixel art like images 7-9 - every material in its own 3-4 flat shades lit from the upper left, BIG FLAT AREAS, at most about 24 colours, a ONE-SQUARE near-black outline around the silhouette and between the axe and the body, no black ring inside the outline, no isolated single squares except eyes, rivets, highlights and spike tips; no dithering, no gradients, no glow, no blur, no anti-aliasing, no half-transparent edges.
No effects, no background, no ground, no shadow, no text, no grid lines in the picture.
Also deliver the same picture read back ONE PIXEL PER SQUARE (80x53 PNG, transparent), exactly square for square.
```

## 提示词 2：侧面 `sion-side-1.png` / `sion-side-2.png`

十张图都附上，顺序同上表。两稿各画一次。

```text
Ten attached images. Image 1 is the CURRENT game sprite of this character in 3/4 view, every game pixel drawn as a 19x19 square with a yellow measuring grid: it fixes the SIZE and the PROPORTIONS (44 rows from the top of the bald head to the soles) - but it is muddy, do NOT copy its look. Image 2 is your own earlier full picture of this character read back on its grid and shown 8x: copy its LOOK - the shapes, the colours, the details. Images 3-6 are 3D renders from the game (3 the head close-up; 4 the idle in 3/4 view; 5 THE IDLE SEEN FROM THE SIDE, facing right - the pose and construction of THIS picture; 6 the axe's shape). Images 7-9 are other characters from the same game at game size shown 8x: copy their CLEANLINESS - big flat areas of colour, few stray squares, a one-square outline. Image 10 is the empty grid for this picture: the red line is the top of the bald head (row 7), the green line is the bottom of the soles (row 50), the blue line is column 40, the middle between the feet.
Draw the SAME character SIDE-ON, FACING IMAGE RIGHT, at GAME SIZE, square by square: a 1536x1024 LANDSCAPE PNG with a genuine transparent background (real alpha) on the grid of image 10 - squares of 19x19 px from (0,0), 80 columns x 53 rows, every square ONE flat colour. The top of the bald head on row 7, the soles on row 50 (44 rows, the same height as the front view), the middle between the feet on column 40.
Side-on facing right (image 5): the huge HUNCHED upper body leaning forward, the small bald head jutting FORWARD (to the right) low in front of the shoulders, seen in profile: ONE RED EYE square, a dark brow, the BLACK IRON JAW CAGE in profile with 2-3 light grey SPIKES pointing forward and down, the broken blade on top of the head and the RED RIBBON fluttering back to the left. The same side faces us as in the front view and image 5: the AXE ARM is the NEAR arm - bare pale grey-lilac with a brown leather wrap on the forearm, hanging in front of the body, its hand gripping the haft so the AXE HANGS DOWN in front of the near leg, the BROAD CURVED STEEL BLADE (at least 9 squares wide, cold grey-blue, a bright edge) low by the near boot, the leather-wrapped haft 2 squares thick, the black iron collar and the pale grey-green block above the blade. The HUGE BLACK-IRON SPIKED PAULDRON sits on the FAR shoulder: it shows behind the head and above the back of the shoulders, its horns pointing up and back. The far arm in its black iron GAUNTLET with brown straps reaches forward a little to the right of the body, a shade darker, its pale hand with spread fingers. The GLOWING RED FURNACE shows at the front of the belly as a bright red sliver on the WIDE BLACK IRON BELT; BROWN and DARK PLUM-BROWN trousers, the ragged OLIVE loin cloth hanging at the front; legs in a heavy half crouch ONE IN FRONT OF THE OTHER: the near leg in front (to the right), the far leg behind (to the left) a shade darker, BIG BLACK IRON BOOTS pointing right, flat on the ground line, one spike on a boot. The back is broad and rounded, pale muscles with a few dark red scars.
The same materials, colours and level of detail as the front view: pale grey-lilac muscles in 3-4 flat shades lit from the upper left as a few big masses, black iron with mid grey lit edges, bright red furnace and eye, brown and plum trousers, olive cloth, cold steel axe, brown haft.
Style: crisp game-size pixel art like images 7-9 - BIG FLAT AREAS, at most about 24 colours, a ONE-SQUARE near-black outline around the silhouette and between the axe and the body, no black ring inside the outline, no isolated single squares except the eye, rivets, highlights and spike tips; no dithering, no gradients, no glow, no blur, no anti-aliasing, no half-transparent edges.
No effects, no background, no ground, no shadow, no text, no grid lines in the picture.
Also deliver the same picture read back ONE PIXEL PER SQUARE (80x53 PNG, transparent), exactly square for square.
```

## 交回前请检查

- 真透明背景，1536×1024 横版，**每格 19×19 像素、一格一个颜色、对齐从 (0,0) 开始的 80×53 网格**；1 倍读回 80×53 和大图逐格一致；网格线不画进图里。
- 光头顶第 7 行、脚底第 50 行（正面、侧面一样高）；正面的位置和附图 1 一致，侧面两脚中间在第 40 列。
- 脸在游戏大小下看得清：两只红眼同一行（侧面一只）、黑铁下颌笼 + 灰色尖刺、头顶断剑 + 2 格粗的红飘带。
- 大块平涂、少零碎杂色格，最多约 24 种颜色；1 格近黑外描边，斧头和身体之间有描边，描边里面不套黑圈。
- 带三根尖角的大黑铁肩甲 + 铁护手都在远侧（正面在画面右边；侧面肩甲露在头后、背上方，护手的手臂向右前方伸）；侧面近侧是拿斧头的光手臂，斧头垂在近侧腿前；肚子上发光的红色熔炉；斧刃至少 9 格宽、柄 2 格粗。
- 正面近侧腿在画面左边亮、远侧在右边稍暗；侧面两腿一前一后、靴子朝右平踩在地面线上。
- 全部画完后最后写 `outputs/sion-model/HANDOFF.md`（列出交付的文件）。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sion/codex_model/`；核对 1 倍读回与大图逐格一致、高度 44 行、颜色数、封闭描边（`strips.complete_outline`）、没有被包住的透明缝（`rigkit.holes`）；正面和侧面并排、和达瑞斯/诺提勒斯/阿利斯塔在 1x、2x、4x 下给用户挑。
- 选定后：正面 = 待机 + 选人卡，侧面 = 第 2 步所有动作的底子（MODEL_STRIPS.md）；跑步用诺提勒斯/布隆的走法（rig_galio.walk_frame）。
