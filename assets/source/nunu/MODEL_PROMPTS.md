# 雪原双子 努努和威朗普：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的 3/4 待机（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 这一步要画成**游戏里的格子数**：**从努努的毛球顶到威朗普脚底 69 格**。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（两张脸、螺旋纹、鹿角分叉碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 4–5 px 一格，整个角色约 190 格高）：这一步**每格画大，撑满画布**。画布用你平时的 **1254 × 1254**，**每格 16 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（A-1 / A-2），都是 3/4 正面朝右。**不画侧面**。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（努努和威朗普 3/4，朝右）**：每格 **16 px**；照 `2_target_A.png` / `3_layout_A.png`：毛球顶 **y = 80**（橙线），努努的眼睛约 **y = 320**（蓝线），威朗普脚底 **y = 1184**（红线）：**69 格高、约 60 格宽**（鹿角、尾巴算在宽里）。
- 全在画布里，鹿角、尾巴、爪子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_heads.png` 是第 0 步读回的两张脸（8 倍），看位置和颜色。

- **努努的脸**（最要紧，他很小）：肤色 3 档；**两只蓝眼睛一样大、一样高、都露出来**，每只约 **2 × 2 格**（深蓝瞳 + 1 格白高光）；**咧嘴笑**：一道深红嘴线里 1–2 格白牙；**棕色刘海**盖在额头；脸不要被兜帽毛边或鹿角挡住。
- **努努的兜帽**：蓝 3 档，**两只猫耳朵里面粉红**（1–2 档），顶上**米白色毛球**（2 档），帽子正面两颗深蓝圆点（雪人眼睛）；**白色毛边**围着脸。
- **努努的身子**：**橙色斗篷**（3–4 档）+ **白毛边**，胸前**一格亮蓝宝石扣**；棕色手套抓着鹿角；橄榄绿裤子；背后**棕色背包**上一块蓝色。他**坐在威朗普头顶**，不挡威朗普的脸。
- **鹿角**：棕色木头 3–4 档，一对，**从威朗普头顶往两边张开**，每边 3–4 个分叉，分叉之间空出来看得见。
- **威朗普的脸**：**两只发蓝光的眼睛**，每只约 **2 × 2 格**，最亮一格接近白色的青白，**两只都露出来**；**棕色鼻头**（2 档）；**大笑嘴**：一排白牙（三角形的尖牙一格一格）、嘴里深红、**两颗小獠牙**；**粉红耳朵**（2 档）在头两侧。
- **威朗普的毛**：淡蓝 4 档（亮处冰白，暗处中蓝），头顶、胸前、前臂是**白色蓬松长毛**（2–3 档，边缘一格一格的锯齿），身上 **2–3 个蓝色螺旋纹**（1 格宽的线，连贯成螺旋，不要碎点）。
- **身体和腿**：身子圆滚滚；**前臂长、爪子大**，每只手 **3–4 个深蓝爪尖**；**下半身和两条短腿是深蓝**（2–3 档）；**两只脚分开踩在地面线上**；**近的腿和手臂（画面左）全亮，远的（画面右）暗一档**；身后一截**蓬松的尾巴**露在画面左边。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的沃利贝尔、布隆、奥恩，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `nunu_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的努努和威朗普（用户认可） | **样子、颜色、细节、姿势**全照它 |
| `2_target_A.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` | 加网格线：橙 = 最高点（毛球），蓝 = 努努的眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_heads.png` | 第 0 步读回的努努和威朗普的脸（8 倍） | 两张脸、兜帽、鹿角根 |
| `style/5_style_volibear.png`、`6_style_braum.png`、`7_style_ornn.png` | 本包的沃利贝尔、布隆、奥恩，8 倍放大 | **只看风格**：这么粗的格子里白蓝的毛、爪子、笑脸、角怎么画 |

## 提示词（两稿用同一段）

附全部图。**用 image_gen 画。** A-1、A-2 各画一次（两次独立生成，挑好的）。

```text
Attached images: 1A your own earlier pixel-art drawing - ONE character in 3/4 view facing right: a BIG ROUND PALE-BLUE YETI with white fluffy fur on the head, chest and forearms, blue swirl markings, two GLOWING BLUE EYES, a brown nose, a WIDE GRIN with a row of white pointed teeth and two small tusks, pink ears, long arms with big DARK BLUE CLAWS, deep blue short legs, a fluffy tail behind; a pair of BIG BROWN WOODEN ANTLERS spreading from his head; and a BOY sitting on top of his head holding the antlers: a blue furry hood with pink-lined cat ears and a cream pompom, a brown fringe, big blue eyes, a big grin, an orange cape with white fur trim and a blue gem clasp, brown gloves, olive trousers, a brown satchel on his back - its LOOK and COLOURS are approved, but it is drawn with far too many small squares; 2A the same picture cut down to the RIGHT square count - 69 squares from the top of the boy's pompom to the yeti's soles - shown with big squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke the details; 3A the same with grid lines every 5 squares: orange = the top, blue = the boy's eyes, red = the ground; 4 the two faces enlarged; 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how white and blue fur, claws, a grin and horns are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner, every square exactly 16 px; the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels. Do NOT shrink a bigger drawing: draw at this size.
With this few squares make every part READ. THE BOY (small, so draw him with care): skin in 3 shades; TWO BLUE EYES of the SAME size at the SAME height, BOTH visible, each about 2x2 squares - dark blue with one white highlight square; a big grin (a dark red mouth line with 1-2 white teeth squares); the brown fringe on his forehead; the face never covered by the hood's fur or the antlers; the hood blue in 3 shades with two cat ears lined pink and the cream pompom on top, two dark blue dots on its front, white fur round the face; the orange cape in 3-4 shades with white fur trim and ONE bright blue gem square on the chest; brown gloves holding the antlers; the brown satchel on his back. He sits on top of the yeti's head and never covers the yeti's face. THE ANTLERS: brown wood in 3-4 shades, a pair spreading to both sides from the yeti's head, 3-4 tines each with clear gaps between them. THE YETI'S FACE: TWO GLOWING BLUE EYES, each about 2x2 squares with the brightest square almost white cyan, both visible; the brown nose in 2 shades; a BIG GRIN - a row of white pointed teeth drawn square by square, a dark red mouth, two small tusks; pink ears at the sides of the head. THE FUR: pale blue in 4 shades (icy white lit, mid blue in the shadows), the long white fur on the head, chest and forearms in 2-3 shades with jagged square-by-square tufts, 2-3 blue SWIRLS of 1-square lines that read as spirals. THE BODY: round; long forearms with big hands, 3-4 dark blue claw tips each; the lower body and the two short legs deep blue in 2-3 shades; the two feet APART on the ground line; the near leg and arm (image left) full tone, the far ones (image right) one shade darker; the fluffy tail showing behind on the image left.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no snowballs, no background, no ground, no cast shadow, no text, no grid lines.
PICTURE A: the idle exactly as images 1A, 2A and 3A - the yeti standing happy in 3/4 view facing right, a little hunched, both faces to the front-right with both eyes of each visible, the boy on his head holding the antlers. Every square exactly 16 px; the top of the pompom at y 80, the boy's eyes at about y 320, the soles on y 1184 - exactly 69 squares tall, about 60 squares wide.
```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：每格 16 px、**69 格高**（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**——第 0 步就是画小了）。
- 努努：两只蓝眼睛一样大、一样高、带白高光；咧嘴笑；棕刘海；蓝兜帽 + 粉猫耳 + 米白毛球；橙斗篷白毛边、一格蓝宝石；坐在威朗普头上，不挡威朗普的脸。
- 威朗普：两只发蓝光的眼睛都露出来；棕鼻头；大笑嘴的白牙一格一格、两颗小獠牙；粉耳朵；白色长毛 + 蓝螺旋纹（干净的线）；深蓝爪子和短腿；两脚分开踩在地面线上；尾巴。
- 鹿角一对，分叉之间空出来。外描边连续；没有任何技能特效。

## 交付（`outputs/nunu-model/`）

- `nunu-model-A-1.png`、`nunu-model-A-2.png`；原始生成图原样放 `outputs/nunu-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/nunu_model_done.zip`。中间不要停，两稿都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（约 16 px / 69 行），从 raw/ 按格读回（regrid），两张脸在 12 倍下看（努努的眼睛是最容易糊的），在游戏大小下和沃利贝尔、拉莫斯、奥恩并排自查（PPU 1.5：毛球到脚底 46 游戏像素），把两稿给用户挑。
- 动作帧：用户决定是 Claude 照英雄联盟的动作拼，还是 Codex 照骨架画姿势（`tools/lol/anim_graph.py Nunu`；`pose_ref.py --champ Nunu` 必须带 `pack_nunu_picture.py` 的 `SKIN` 参数）；两张脸用在所有帧。数据里要的动作：idle run attack attack_bite skill skill_roll skill_hit skill2 ult ult_end hit dead（`tools/kit/build_nunu.py`）。
