# 迷失之牙 纳尔：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（迷你纳尔 3/4）**、**M（巨型纳尔 3/4）**、**SM（巨型纳尔侧面）**（`1_picture_A.png`、`1_picture_M.png`、`1_picture_SM.png`）**用户选定了，样子、颜色全照它们**。迷你纳尔**只要 3/4**，不画侧面。
> - 这一步要把他画成**游戏里的格子数**：**迷你纳尔从头盔顶到脚底 48 格**，**巨型纳尔从最高的毛刺到脚底 66 格**。我把三张图直接缩到这个格子数（`2_target_A.png`、`2_target_M.png`、`2_target_SM.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、牙齿、骨头碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，三张的格子大小不一样（为了都撑满画布）：**A 每格 20 px**，**M 每格 12 px**，**SM 每格 10 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**三种**（同一个纳尔、同样的颜色），**每种两稿**：A-1 / A-2、M-1 / M-2、SM-1 / SM-2。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（迷你 3/4）**：每格 **20 px**；照 `2_target_A.png` / `3_layout_A.png`：头盔顶 **y = 220**（橙线），眼睛约 **y = 520**（蓝线），脚底 **y = 1180**（红线）：**48 格高、约 50 格宽**。
- **M（巨型 3/4）**：每格 **12 px**；照 `2_target_M.png` / `3_layout_M.png`：最高的毛刺 **y = 396**，眼睛约 **y = 804**，脚底和拳头 **y = 1188**：**66 格高、约 94 格宽**。
- **SM（巨型侧面朝右）**：每格 **10 px**；照 `2_target_SM.png` / `3_layout_SM.png`：最高的毛刺 **y = 520**，眼睛约 **y = 810**，脚底 **y = 1180**：**66 格高、约 112 格宽**。
- 全在画布里，耳朵、尾巴、回力标、獠牙、毛刺不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **迷你的脸**（`4_head_mini.png` 是第 0 步读回的头部，8 倍）：橙色小脸；**两只大大的深色圆眼睛：每只约 4 × 4 格，一样高、一样大**，深紫黑色、各带 **1–2 格白色高光**；粉色小鼻子 1 格；嘴边 1 格小獠牙。**一对大耳朵**（外面橙色、里面紫粉色、耳尖蓝色）清楚地往两边伸出去；**头上的骨头头盔**（小头骨 + 横着的一根骨头，象牙色 3 档）。
- **迷你的身体**：深棕色**毛披肩和腰布**；**蓬松的大尾巴**（橙色 3–4 档、尾尖蓝色，一绺一绺分清）在身后；**骨头回力标**（象牙色、中间缠棕色皮条）拿在身侧；两只小脚踩在地面线上，**两条腿之间要有空隙和描边分开**。
- **巨型的脸**（`4_head_mega.png`）：深红色，**两只黄橙色的眼睛**（每只约 2 × 2 格，一样高）、蓝色的眉毛毛刺；宽嘴里**一排象牙色尖牙**（每颗至少 2 格高，分开画）；**两根大獠牙**从嘴角往外往上弯（象牙色 3 档）；额头上的**小骨头头盔**。
- **巨型的身体**：深红毛 3–4 档（**不要糊成一团红**，毛的一绺绺用亮边分清），背上、头上、手臂上**一排排电光蓝毛刺**（3 档、亮边偏青、尖端清楚）；**两只大拳头**和爪子是深灰紫色 3 档，象牙色的爪尖；尾巴蓝红相间。**M 和 SM 是同一个巨型纳尔**：头、獠牙、头盔、毛刺、颜色一样。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的悠米、古拉加斯、科加斯，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `gnar_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_M.png` / `1_picture_SM.png` | 你第 0 步画的三张（用户选定） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_M.png` / `2_target_SM.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_M.png` / `3_layout_SM.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_mini.png` / `4_head_mega.png` | 第 0 步读回的两个头（8 倍） | 脸、眼睛、耳朵、头盔、獠牙、牙齿 |
| `style/5_style_yuumi.png`、`6_style_gragas.png`、`7_style_chogath.png` | 本包的悠米、古拉加斯、科加斯，8 倍放大 | **只看风格**：这么粗的格子里小动物的大眼睛、大块头的毛、怪兽的尖牙怎么画 |

## 提示词（三种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A, 1M and 1SM your own earlier pixel-art drawings of one character in two forms - MINI (1A): a tiny orange furry chibi cub with huge pointed ears (orange outside, violet-pink inside, blue tips), big round dark eyes with white highlights, a pink nose, a small fang, a bone skull cap (a small animal skull with a bone across it), a dark brown fur wrap and loincloth, a big bushy orange tail with a blue tip and a big ivory bone boomerang wrapped with brown leather held at his side (3/4 view facing right); MEGA (1M 3/4 view facing right, 1SM side-on facing right): the same character as a huge hunched crimson beast on its knuckles with rows of spiky electric-blue fur crests, two big curved ivory tusks, a wide mouth of ivory fangs, yellow-orange eyes, the same small skull cap on his brow, huge dark grey-violet fists and claws, a blue-and-red tail - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A, 2M and 2SM the same pictures cut down to the RIGHT square count - Mini 48 squares from the top of his skull cap to his soles, Mega 66 squares from his highest crest to his soles - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A, 3M and 3SM the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the two heads enlarged (Mini, Mega); 5-7 STYLE ONLY: other characters from the same game at a similar square density, shown 8x so every square is one pixel - how a small furry creature's big eyes, a big body's fur and a monster's fangs are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ. MINI: his small orange face; TWO BIG ROUND DARK EYES, each about 4x4 squares, at the SAME height and the SAME size, dark violet-black each with 1-2 WHITE highlight squares; a 1-square pink nose and a 1-square fang; the huge ears clearly spread out (orange, violet-pink inside, blue tips); the ivory skull cap with its bone; the dark brown wrap and loincloth; the bushy tail in 3-4 orange shades with a blue tip, tuft by tuft; the boomerang ivory with brown leather; a clear gap and outline between his two little legs. MEGA: the crimson fur in 3-4 shades with lit edges tuft by tuft, never one red mass; the electric-blue crests in 3 shades with CYAN LIT EDGES and clear points; TWO YELLOW-ORANGE EYES about 2x2 squares at the same height under blue brow crests; a row of separate ivory fangs (each at least 2 squares tall) in the wide mouth; the two big curved tusks in 3 ivory shades; the small skull cap on his brow; the huge dark grey-violet fists with ivory claw tips; the blue-and-red tail.
One continuous 1-square near-black outline round him; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`gnar-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: MINI's idle exactly as images 1A, 2A and 3A - he stands in 3/4 view facing right, the face to the front-right, the boomerang held at his side, the tail curling behind him; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both feet on the ground line. Every square exactly 20 px; the top of his skull cap at y 220, his eyes at about y 520, his soles on y 1180 - exactly 48 squares tall, about 50 squares wide.
  ```
- **M（`gnar-model-M-1.png`、`-M-2.png`，两稿）**：
  ```text
  PICTURE M: MEGA's idle exactly as images 1M, 2M and 3M - hunched on his knuckles in 3/4 view facing right, the head low at the front (image right), the face to the front-right with both eyes and both tusks visible, the tail up behind him. Every square exactly 12 px; his highest crest at y 396, his eyes at about y 804, his fists and feet on y 1188 - exactly 66 squares tall, about 94 squares wide.
  ```
- **SM（`gnar-model-SM-1.png`、`-SM-2.png`，两稿）**：
  ```text
  PICTURE SM: the SAME Mega exactly SIDE-ON, FACING RIGHT, as images 1SM, 2SM and 3SM - the head at the front (image right) with one eye and the near tusk in front, the far tusk a little behind; the crests along his back; the near front arm and the near hind leg in full tone, the far ones a step darker and a little behind, all four on the ground line; the tail behind him (image left). The SAME head, tusks, skull cap and colours as picture M. Every square exactly 10 px; his highest crest at y 520, his eyes at about y 810, his fists and feet on y 1180 - exactly 66 squares tall, about 112 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 20 px、48 格高；M 每格 12 px、66 格高；SM 每格 10 px、66 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 迷你：两只大圆眼睛一样大、一样高、带白色高光；大耳朵、头盔、尾巴、回力标清楚；两条腿分开。
- 巨型：两只眼睛一样高；尖牙一颗颗分开；两根獠牙、头盔、蓝毛刺清楚；M 和 SM 是同一个巨型纳尔。外描边连续；没有任何技能特效。

## 交付（`outputs/gnar-model/`）

- `gnar-model-A-1.png`、`gnar-model-A-2.png`、`gnar-model-M-1.png`、`gnar-model-M-2.png`、`gnar-model-SM-1.png`、`gnar-model-SM-2.png`；原始生成图原样放 `outputs/gnar-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/gnar_model_done.zip`。中间不要停，六张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 20 px / 48 行，M 约 12 px / 66 行，SM 约 10 px / 66 行），从 raw/ 按格读回（regrid），在游戏大小下和提莫、吉格斯、科加斯、沃利贝尔并排自查（PPU 1.5：迷你 32、巨型 44 游戏像素），把两稿给用户挑。
- 迷你的动作全用 3/4 造型（用户：不做侧面）；巨型的动作可以用侧面造型。动作照英雄联盟的骨骼摆（`tools/lol/anim_graph.py Gnar` / `GnarBig --wad Gnar`、`pose_ref.py --champ Gnar` / `--champ GnarBig --wad Gnar`）；腿和待机一致、不变形；一张脸用在所有帧。
