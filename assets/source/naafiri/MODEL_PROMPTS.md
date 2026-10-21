# 百裂冥犬 纳亚菲利：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的两张（`1_picture_A.png` 纳亚菲利 3/4、`1_picture_P.png` 狗群伙伴 3/4）**样子、颜色用户认可了，全照它们**。侧面这一步不画（用户只要 3/4）。
> - 这一步要把她们画成**游戏里的格子数**：**纳亚菲利从最高的刀刃尖到爪底 45 格**，**伙伴从头盔顶到爪底 24 格**。我把两张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、白色斑纹、牙齿、刀刃的薄荷绿边碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，两张的格子大小不一样（为了都撑满画布）：**A 每格 14 px**，**P 每格 26 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**：**A 两稿**（A-1 / A-2）、**P 两稿**（P-1 / P-2）。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（纳亚菲利 3/4）**：每格 **14 px**；照 `2_target_A.png` / `3_layout_A.png`：最高的刀刃尖 **y = 560**（橙线），眼睛约 **y = 952**（蓝线），爪底 **y = 1190**（红线）：**45 格高、约 78 格宽**。
- **P（伙伴 3/4）**：每格 **26 px**；照 `2_target_P.png` / `3_layout_P.png`：头盔顶 **y = 572**，眼睛约 **y = 832**，爪底 **y = 1196**：**24 格高、约 42 格宽**。
- 全在画布里，刀刃、尾巴、爪子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **纳亚菲利的脸**（`4_head_naafiri.png` 是第 0 步读回的头部，8 倍）：深红色的狼脸，口鼻上一道**白色斑纹**（2 档）；**两只黄色的眼睛**：近处那只约 **2 × 2 格**，远处那只至少 **2 × 1 格**，一样高，各带 **1 格白色高光**；尖耳朵；张开的嘴里**一排白牙**（一颗颗分开）、深红色的嘴里；嘴角**匕首的米黄色骨柄**往下伸出 2–3 格。
- **纳亚菲利的身体**：**石板蓝 / 青灰色甲壳**（3 档）盖在背和肩上，上面几道**深红纹路**；脖子和肩上**一大圈深紫色刀刃**（3 档），每片刀刃**镶 1 格薄荷绿边**，往后张开，**一片片分得开，不糊成一团**，也**不挡脸**；背脊一排短**青色尖刺**；**深红色的四条腿**，近处的腿全亮、远处的腿暗一档，**腿和腿之间要有空隙和描边分开**；**黑色爪子**踩在地面线上；**长长的鞭子尾巴**拖在身后（画面左边），尾巴末端红色。
- **伙伴的脸**（`4_head_packmate.png`）：深红色的脸，**石板灰的骨头盔**（3 档、亮边偏青白）从额头往前伸出**一片弯刀刃**罩在口鼻上方；**一只黄色的眼睛**约 **2 × 2 格**，带 1 格白色高光；嘴里一排小白牙。
- **伙伴的身体**：精瘦的深红色身体（3–4 档，**不要糊成一团红**，肌肉用亮边分清）；脖子上几根短灰刺；四条细腿，近处全亮、远处暗一档，腿之间有空隙；**黑色爪子**；细长的尾巴，**尾尖灰蓝**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的奈德丽豹形、沃里克、巨型纳尔，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `naafiri_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_P.png` | 你第 0 步画的两张（用户认可） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_P.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_P.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_naafiri.png` / `4_head_packmate.png` | 第 0 步读回的两个头（8 倍） | 眼睛、白色斑纹、牙、匕首骨柄；伙伴的头盔、刀刃、眼睛 |
| `style/5_style_nidalee_cougar.png`、`6_style_warwick.png`、`7_style_gnar_mega.png` | 本包的奈德丽豹形、沃里克、巨型纳尔，8 倍放大 | **只看风格**：这么粗的格子里四足野兽的身体、狼脸、大野兽怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1P your own earlier pixel-art drawings of two characters, both in 3/4 view facing right - 1A THE LEADER: a big lean hound on four legs with a crimson-red wolf head, a white blaze on the snout, yellow eyes, a grinning mouth of white fangs holding a bone dagger hilt, a slate blue-teal armoured hide with crimson veins over the back and shoulders, a big fan of curved dark-purple blades rimmed in mint green rising from the neck and shoulders, teal spikes down the spine, crimson legs, black claws and a long whip tail; 1P THE PACKMATE: a smaller lean crimson hound with a slate-grey bony helmet whose curved blade juts forward over the snout, one yellow eye, short grey neck spikes, black claws and a thin tail with a grey-blue end - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A and 2P the same pictures cut down to the RIGHT square count - the leader 45 squares from her highest blade tip to her paws, the packmate 24 squares from its helmet to its paws - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A and 3P the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the two heads enlarged (leader, packmate); 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a four-legged beast, a wolf's face and a big beast's body are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ. LEADER: the crimson wolf face with a 2-shade WHITE BLAZE on the snout; TWO YELLOW EYES at the SAME height, the near one about 2x2 squares and the far one at least 2x1, each with 1 WHITE highlight square; pointed ears; a row of SEPARATE white fangs; the bone-beige dagger hilt 2-3 squares below the corner of the mouth; the slate blue-teal hide in 3 shades with crimson veins; the fan of dark-purple blades in 3 shades, EACH blade with a 1-square MINT-GREEN edge, the blades clearly separate and NEVER covering the face; teal spine spikes; crimson legs with a clear gap and outline between every two legs, the near legs in full tone and the far legs a step darker; black claws; the long tail. PACKMATE: the crimson body in 3-4 shades with lit edges, never one red mass; the slate-grey helmet in 3 shades with PALE CYAN-WHITE lit edges and its curved blade over the snout; ONE YELLOW EYE about 2x2 squares with a white highlight; small white teeth; thin legs with gaps, the far ones a step darker; black claws; the thin tail with a grey-blue end.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines, ONE hound in the picture.
```

最后一段，按要画的那一张换：

- **A（`naafiri-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: THE LEADER's idle exactly as images 1A, 2A and 3A - low on her four legs in 3/4 view facing right, the head at the front (image right) with both eyes, the blaze and the fangs visible, the blade mane fanned back, the tail trailing behind to the image left; all four paws on the ground line. Every square exactly 14 px; her highest blade tip at y 560, her eyes at about y 952, her paws on y 1190 - exactly 45 squares tall, about 78 squares wide.
  ```
- **P（`naafiri-model-P-1.png`、`-P-2.png`，两稿）**：
  ```text
  PICTURE P: THE PACKMATE's idle exactly as images 1P, 2P and 3P - on its four legs in 3/4 view facing right, the head at the front (image right) with the helmet blade and the eye visible, the tail behind to the image left; all four paws on the ground line. Every square exactly 26 px; the top of its helmet at y 572, its eye at about y 832, its paws on y 1196 - exactly 24 squares tall, about 42 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 14 px、45 格高；P 每格 26 px、24 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 纳亚菲利：两只黄眼睛一样高、带白色高光；白色口鼻斑纹；白牙一颗颗分开；匕首骨柄；刀刃鬃毛一片片分开、薄荷绿边清楚、不挡脸；腿之间有空隙。
- 伙伴：骨头盔和刀刃清楚；黄眼睛看得清；身体不糊成一团红。外描边连续；没有任何技能特效。

## 交付（`outputs/naafiri-model/`）

- `naafiri-model-A-1.png`、`naafiri-model-A-2.png`、`naafiri-model-P-1.png`、`naafiri-model-P-2.png`；原始生成图原样放 `outputs/naafiri-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/naafiri_model_done.zip`。中间不要停，四张都画完再交。

## 后面要用到的（这一步不画，心里有数就行）

狗群会**直接画进纳亚菲利自己的每一帧动作里**：平时两只伙伴跟在她身边，暴吼（大招起手）时变成四只。所以伙伴这一张要和她的颜色、描边、格子密度一致，能和她放在同一张图里。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 14 px / 45 行，P 约 26 px / 24 行），从 raw/ 按格读回（regrid），在游戏大小下和奈德丽豹形、沃里克、男枪并排自查（PPU 1.5：纳亚菲利 30、伙伴 16 游戏像素），把两稿给用户挑。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py Naafiri` / `NaafiriPackmate --wad Naafiri`，`pose_ref.py --champ Naafiri --hide-submeshes` / `--champ NaafiriPackmate --wad Naafiri`）；狗群画进她的帧（两只，`p4_*` 标签四只，附加包的显示钩子在 `pack4` 时换过去）；腿和待机一致、不变形；一张脸用在所有帧。
