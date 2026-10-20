# 虚空之眼 维克兹：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把 A 最近邻缩放交差。**
> - 第 0 步你画的 **A（触手向两边卷开的待机）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把他画成**游戏里的格子数**：**从头顶尖刺冠的顶端到最低那圈触手 54 格**，连两边的触手约 75 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（三只小眼睛、大眼睛的竖瞳、甲片的纹路、触手的品红尖端碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **只画 3/4 正面朝右**（和 A 一样；**不画侧面**）：游戏里的待机，所有动作也都从这张图来做。
> - **每格画大：15 px 一格**。画布用你平时的 **1254 × 1254**：**尖刺冠顶端 y = 360，大眼睛约 y = 735，最低的触手下沿 y = 1170**。每一格都是 15 × 15 px 的方块，不要用更小的格子画细节。**画三稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1254 × 1254**，**每格 15 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **尖刺冠顶端 y = 360**（绿线），**大眼睛约 y = 735**（蓝线），**最低的触手下沿 y = 1170**（红线）：顶端到最低处 **54 格**。
- 宽约 75 格（左边触手尖到右边触手尖），放在 `2_target.png` 的位置。

## 在 54 格里要画清楚的地方

- **大眼睛**（`4_head.png` 是第 0 步读回的甲壳和眼睛，8 倍）：品红色的大眼睛**至少 7–8 格宽**，中间亮（最亮一档接近白粉色，左上一个 2 格的高光），外圈深品红，**正中一条深色的竖瞳（1 格宽、3–4 格高）**，竖瞳旁边一圈浅粉色的亮边。
- **三只小眼睛**在大眼睛上方的甲壳里：品红色，**每只至少 2 格**（1 格亮心 + 深色边），周围一圈红色的肉边。
- **甲壳**：卡其金色 3–4 档（亮边浅黄，暗处橄榄褐，**不要糊成一团黑**），一层层叠起来的甲片，甲片之间用最暗一档的线隔开；头顶向后上方翘起的**尖刺冠**；两侧几根尖刺。大眼睛周围是**红紫色的肉质边缘**（红、深红、暗紫 2–3 档）。
- **触手**：深青黑色 3 档（亮边偏青绿，暗处深蓝黑），**粗细至少 3 格**，左上一条向上卷、左下一条绕成一个圈、右下一条往下卷；**每条的尖端和内侧是品红色**（2 档）。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的婕拉——**和维克兹同一个密度左右**——以及科加斯、玛尔扎哈、卡萨丁；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画等离子球、射线、发光的光晕）。

## 附图（压缩包 `velkoz_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | A 缩到游戏格子数、每格 15 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 尖刺冠顶端，蓝 = 大眼睛，红 = 最低的触手 | 对齐网格、54 格的高度 |
| `4_head.png` | 第 0 步读回的甲壳和眼睛（8 倍） | 大眼睛、三只小眼睛、肉边、甲片 |
| `style/7_style_zyra.png` … `10_style_kassadin.png` | 本包的婕拉（差不多同密度）、科加斯、玛尔扎哈、卡萨丁，8 倍放大 | **只看风格**：这么粗的格子里眼睛、甲壳、触手、深色的亮边怎么画 |

## 提示词：`velkoz-model-A-1.png`、`velkoz-model-A-2.png`、`velkoz-model-A-3.png`（3/4 正面，三稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a floating void eye with no legs: one huge glowing magenta eye with a dark slit pupil in a khaki-gold armoured carapace (overlapping plates, a crown of spikes sweeping up and back, red-violet fleshy rims round the eye, three small magenta eyes above it), long curling dark teal-black tentacles with magenta tips and undersides - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 54 squares from the top of the spike crown to the lowest tentacle, about 75 squares wide with the tentacles - shown with 15 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the small eyes, the pupil, the plates and the tentacle tips are specks); 3 the same with grid lines every 5 squares: green = the top of the crown, blue = the big eye, red = the lowest tentacle; 4 the carapace and eyes of image 1 enlarged; 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (7 at about this same square density) - how eyes, armour plates, tentacles and the lit edges of dark colours are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Every square exactly 15 px, aligned on one straight grid from the canvas corner; the top of the spike crown at y 360, the big eye at about y 735, the lowest tentacle's bottom edge on y 1170 - exactly 54 squares from the top of the crown to the lowest tentacle, about 75 squares wide, placed as in image 2. Every detail drawn with whole 15 px squares, never with smaller pixels.
With only 54 squares make every part READ: the BIG MAGENTA EYE at least 7-8 squares wide - bright in the middle (the brightest shade almost white-pink, a 2-square highlight top left), deep magenta outside, a DARK VERTICAL SLIT PUPIL (1 square wide, 3-4 squares tall) with a pale pink rim beside it; THREE SMALL MAGENTA EYES in the carapace above it, each at least 2 squares (a bright square and a dark edge) in a red fleshy rim; the RED-VIOLET FLESH round the big eye in 2-3 shades; the KHAKI-GOLD CARAPACE in 3-4 shades (pale yellow lit edges, olive-brown shadows - never one black mass), overlapping plates parted by their own darkest shade, the SPIKE CROWN sweeping up and back, a few spikes on the sides; the DARK TEAL-BLACK TENTACLES in 3 shades (teal-green lit edges, deep blue-black shadows), at least 3 squares thick - one curling up on the upper left, one coiled in a loop on the lower left, one curling down on the lower right - each with MAGENTA TIPS and undersides in 2 shades.
THE POSE as image 1: floating, the tentacles curling out to both sides; 3/4 view facing right (the big eye to the front-right), the NEAR side in full tone, the FAR side a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no plasma, no beam, no glow halo), no background, no ground, no shadow, no text, no grid lines. Make three takes.
```

## 交回前请检查

- **三张都是 image_gen 画的**（不是把 A 缩放出来的）；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 15 px**：尖刺冠顶端 y 360、最低的触手下沿 y 1170，**正好 54 格**（数一下台阶数：**如果是 80 格以上就是格子画小了，请重画**）。
- 3/4 正面朝右；大眼睛有竖瞳和高光；三只小眼睛都看得见；甲片分档；触手粗、尖端品红；外描边连续；没有任何特效。

## 交付（`outputs/velkoz-model/`）

- `velkoz-model-A-1.png`、`velkoz-model-A-2.png`、`velkoz-model-A-3.png`；原始生成图原样放 `outputs/velkoz-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/velkoz_model_done.zip`。中间不要停，三张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 15 px、顶端到最低触手 54 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过眼睛），在 12 倍下查眼睛（**优先用 Codex 原本画的眼睛，不要自己重画成方块**——薇古丝的教训），在游戏大小下和婕拉、玛尔扎哈、卡萨丁并排自查（PPU 1.5，36 游戏像素），给用户挑一张。
- 动作（只做 3/4）都在这张造型上摆，照英雄联盟的 Attack1–3 / Crit、Q Spell1、W Spell2、E Spell3、R Spell4_in / Channel、跑 run（整体飘、触手摆）、死亡 Death；所有帧同一只大眼睛。
