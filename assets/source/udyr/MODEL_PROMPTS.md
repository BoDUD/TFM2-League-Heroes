# 兽灵行者 乌迪尔：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的原始图（`1_picture_A.png` 平常、`1_picture_Q.png` 熊、`1_picture_E.png` 公羊、`1_picture_R.png` 凤凰）**样子、颜色用户认可了，全照它们**。
> - 用户定了：**只做 3/4 正面朝右，不要侧面**；**平常姿态从举起的拳头顶到脚底 60 格**；熊 **61 格**、公羊 **69 格**、凤凰 **73 格**（同一个人、同一个比例，只是姿势和兽灵部件不同）。我把四张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、胡子、纹身、羽刃碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，四张的格子大小不一样（为了都撑满画布）：**A 每格 18 px**，**Q 每格 15 px**，**E 每格 15 px**，**R 每格 13 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**八张**（同一个乌迪尔、同样的颜色）：**每种两稿**（A-1 / A-2、Q-1 / Q-2、E-1 / E-2、R-1 / R-2）。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（平常护头待机）**：每格 **18 px**；照 `2_target_A.png` / `3_layout_A.png`：拳头顶 **y = 108**（橙线），眼睛约 **y = 270**（蓝线），脚底 **y = 1188**（红线）：**60 格高、约 52 格宽**。
- **Q（熊姿态）**：每格 **15 px**；最高点 **y = 270**，眼睛约 **y = 525**，脚底 **y = 1185**：**61 格高、约 74 格宽**。
- **E（公羊姿态）**：每格 **15 px**；羊角顶 **y = 150**，眼睛约 **y = 555**，脚底 **y = 1185**：**69 格高、约 62 格宽**。
- **R（凤凰姿态）**：每格 **13 px**；最高的羽刃 **y = 234**，眼睛约 **y = 624**，脚底 **y = 1183**：**73 格高、约 90 格宽**。
- 全在画布里，拳头、熊皮、羊角、羽刃、头发不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head_A.png`、`4_head_Q.png`、`4_head_E.png`、`4_head_R.png`，第 0 步读回的头，8 倍）：暖棕色的脸（2–3 档）；**两只眼睛都看得见：每只约 2 × 1 格，冷蓝色，一样高**；浓眉皱着；**深色络腮胡包住下巴**，胡子、头发、脸**用不同的深色分开**（不要糊成一整块深棕）；嘴巴在胡子里看得见；脏辫从头顶垂到肩上；**脸左边一根亮蓝色的羽毛发辫**（2 档，从耳边垂到胸口）；头发边上一小块白色的发饰。
- **身体**：晒黑的暖棕皮肤（3 档，亮面偏橙）；胸口、肩膀、手臂上的**暗红色纹身**（用整格的暗红画出几道粗纹，不要碎点）；两只拳头的**白色绷带**（2 档）和**橙色护腕**；腰上**一圈大颗橙红念珠**（每颗至少 2 × 2 格，带一格亮点）；**青灰色石头腰牌**；**两根橙色粗绳**垂到膝盖；**深棕色宽裤子**；**青灰色石头护膝**（圆形符文）和下面一圈**灰蓝色毛皮**；**深青色绑腿**；露脚趾的**凉鞋**踩在地面线上，**两条腿之间要有空隙和描边分开**；近处的腿全亮，远处的腿暗一档。
- **兽灵部件**：Q 的**熊皮**（棕色 3 档带深色条纹）披在背上，**熊头**（耳朵、长吻、牙）盖在前面那只拳头上；E 的**两只大卷公羊角**（棕褐 3 档、深色环纹、中间一段白灰的缠布）从肩背绕过头顶；R 两臂张开，胳膊和背上一排排**深蓝色羽刃**（3 档，根部橙红 2 档），**头发往上飘起**。**兽灵部件和拳头都不挡脸**。
- **四张是同一个人**：脸、胡子、头发、纹身、裤子、颜色一样，只有姿势和兽灵部件不同。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–8 一样的像素画（本包的沃利贝尔、格雷福斯、塞拉斯、奥恩，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（闪电、火焰、冰风暴、护盾光、兽灵虚影都不画）。

## 附图（压缩包 `udyr_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `_Q` / `_E` / `_R` | 你第 0 步画的原始图（用户认可） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `_Q` / `_E` / `_R` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `_Q` / `_E` / `_R` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_A.png` / `_Q` / `_E` / `_R` | 第 0 步读回的四个头（8 倍） | 脸、眼睛、胡子、头发、羽毛发辫 |
| `style/5_style_volibear.png`、`6_style_graves.png`、`7_style_sylas.png`、`8_style_ornn.png` | 本包的沃利贝尔、格雷福斯、塞拉斯、奥恩，8 倍放大 | **只看风格**：这么粗的格子里壮汉的脸、胡子、光膀子、皮毛、羊角怎么画 |

## 提示词（四种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A, 1Q, 1E and 1R your own earlier pixel-art drawings of one character - a HUGE BARE-CHESTED MONK BRAWLER with tanned warm-brown skin and DARK RED TRIBAL TATTOOS on the chest, shoulders and arms, long dark brown dreadlocks, a thick dark beard, ONE BRIGHT BLUE FEATHER BRAID by the left side of his face, white bandage wraps on both fists, orange bracers, a belt of BIG ORANGE-RED PRAYER BEADS with a teal-grey stone plaque and two thick orange ropes, baggy dark brown trousers, teal-grey stone knee guards with a ruff of grey-blue fur, dark teal leg wraps and open sandals; 1A his plain guard idle (fists raised beside his face), 1Q his BEAR stance (a bear hide over his back, the bear's head over his front fist), 1E his RAM stance (two huge curled ram horns from his shoulders), 1R his PHOENIX stance (arms spread, dark blue feather blades along them, the hair swept up) - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A, 2Q, 2E and 2R the same pictures cut down to the RIGHT square count - 60 squares from the raised fists to the soles in the guard, 61 for the bear, 69 for the ram, 73 for the phoenix - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A-3R the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4A-4R the four heads enlarged; 5-8 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a big man's face, beard, bare arms, fur and horns are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ: the warm-brown face in 2-3 shades; BOTH EYES visible, each about 2x1 squares, cold blue, at the SAME height; heavy frowning brows; the DARK BEARD wrapping the jaw with the mouth visible in it; the beard, the dreadlocks and the face kept apart by their own dark shades (never one brown mass); the BRIGHT BLUE FEATHER BRAID in 2 shades hanging from beside his left ear to his chest. The tanned skin in 3 shades with an orange lit edge and a few bold DARK RED tattoo stripes drawn with whole squares (no speckles); the white bandaged fists in 2 shades and the orange bracers; the BIG ORANGE-RED BEADS round the waist, each at least 2x2 squares with one lit square; the teal-grey stone plaque and the two orange ropes; the dark brown trousers; the teal-grey stone knee guards with the grey-blue fur under them; the dark teal leg wraps; sandals on the ground line with a clear gap and outline between his legs, the near leg in full tone and the far leg a step darker. The spirit parts (the bear hide and head, the ram horns, the feather blades) and the fists NEVER cover his face.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects (no lightning, no fire, no ice storm, no shield glow, no ghostly animals), no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`udyr-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: his PLAIN GUARD idle exactly as images 1A, 2A and 3A - a wide low horse stance in 3/4 view facing right, the knees bent, BOTH BANDAGED FISTS RAISED beside his face (not over it), the body leaning a little forward, no spirit parts; the face to the front-right, stern; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both sandals on the ground line. Every square exactly 18 px; the top of his fists at y 108, his eyes at about y 270, his soles on y 1188 - exactly 60 squares tall, about 52 squares wide.
  ```
- **Q（`udyr-model-Q-1.png`、`-Q-2.png`，两稿）**：
  ```text
  PICTURE Q: his BEAR stance idle exactly as images 1Q, 2Q and 3Q - the SAME man as picture A, HUNCHED FORWARD like a bear about to pounce in 3/4 view facing right, the knees bent, both hands low and open like paws; the BEAR HIDE (brown in 3 shades with dark stripes) draped over his back, the BEAR'S HEAD (ears, long snout, white teeth) over his front fist like a gauntlet; the face to the front-right under the hide, fierce. Every square exactly 15 px; his highest point at y 270, his eyes at about y 525, his soles on y 1185 - exactly 61 squares tall, about 74 squares wide.
  ```
- **E（`udyr-model-E-1.png`、`-E-2.png`，两稿）**：
  ```text
  PICTURE E: his RAM stance idle exactly as images 1E, 2E and 3E - the SAME man as picture A, the head lowered and the shoulders forward in 3/4 view facing right, ready to charge, the knees bent, the fists low; TWO HUGE CURLED RAM HORNS (tan-brown in 3 shades with dark rings and a band of white-grey wrapping) growing from his shoulders and back, sweeping up over his head and curling round; the face to the front-right under the horns, which frame it and never cover it. Every square exactly 15 px; the horn tops at y 150, his eyes at about y 555, his soles on y 1185 - exactly 69 squares tall, about 62 squares wide.
  ```
- **R（`udyr-model-R-1.png`、`-R-2.png`，两稿）**：
  ```text
  PICTURE R: his PHOENIX stance idle exactly as images 1R, 2R and 3R - the SAME man as picture A, a wide half-squat in 3/4 view facing right, BOTH ARMS SPREAD OUT to the sides like wings with the fingers open; rows of DARK BLUE FEATHER BLADES (3 shades) with ORANGE-RED roots (2 shades) standing along both arms and his back, his DREADLOCKS SWEPT UP and flaring behind his head; the face to the front-right, calm and fierce. Every square exactly 13 px; the highest feather tip at y 234, his eyes at about y 624, his soles on y 1183 - exactly 73 squares tall, about 90 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 18 px、60 格高；Q 每格 15 px、61 格高；E 每格 15 px、69 格高；R 每格 13 px、73 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 两只眼睛看得见、一样高；胡子、头发、脸分得开；**蓝羽毛发辫**清楚；暗红纹身、白绷带、橙护腕、大颗橙红念珠、青石腰牌和橙绳、深棕裤子、青石护膝和灰蓝毛皮、深青绑腿、凉鞋清楚；两条腿分开。
- 熊皮熊头 / 羊角 / 羽刃清楚，不挡脸。四张是同一个人。外描边连续；没有任何技能特效。

## 交付（`outputs/udyr-model/`）

- `udyr-model-A-1.png`、`-A-2.png`、`-Q-1.png`、`-Q-2.png`、`-E-1.png`、`-E-2.png`、`-R-1.png`、`-R-2.png`；原始生成图原样放 `outputs/udyr-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/udyr_model_done.zip`。中间不要停，八张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 18 px / 60 行，Q 15 / 61，E 15 / 69，R 13 / 73），从 raw/ 按格读回（regrid），在游戏大小下和沃里克、沃利贝尔、格雷福斯、塞拉斯并排自查（PPU 1.5：A 40 游戏像素），把两稿给用户挑。脸放大 12 倍检查，眼睛 / 嘴的格子不清楚就在设计脚本里重画（`codex-face-half-squares` 的做法）。四张用同一套颜色（k-means 一起切）、同一张脸。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py Udyr`，`pose_ref.py --champ Udyr` 带 `pack_udyr_picture.py` 的 STANCES 只留该姿态的兽灵部件）；腿和待机一致、不变形；一张脸用在所有帧。数据里的动作名见 `tools/kit/build_udyr.py`：idle run attack skill skill2 e_run e_stun ult hit dead，姿态 q_attack e_attack r_attack，附加包的视图切换要 q_idle q_run e_idle e_run r_idle r_run（英雄联盟：spell2_idle / Spell2_run / Spell2_attack，Spell1_*，Spell3_*，Spell4_*）。
