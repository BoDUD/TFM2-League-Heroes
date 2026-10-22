# 纳祖芒荣耀 奎桑提：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的原始图（`1_picture_A.png` 普通姿态 3/4、`1_picture_O.png` 全盛姿态 3/4）**样子、颜色用户认可了，全照它们**。注意：你上次自己导出的 11 px 版本把脸和红外套弄丢了，这次**照原始图**画（深红外套要清楚，不要变成一身金）。
> - 用户定了：**只做 3/4 正面朝右，不要侧面**；**普通姿态从陀斧顶到脚底 72 格**，**全盛姿态 73 格**（同一个人、同一个比例）。我把两张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、胡子、花纹、水晶碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，两张的格子大小不一样（为了都撑满画布）：**A 每格 15 px**，**O 每格 11 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**（同一个奎桑提、同样的颜色）：**A 两稿**（A-1 / A-2）、**O 两稿**（O-1 / O-2）。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（普通姿态 3/4）**：每格 **15 px**；照 `2_target_A.png` / `3_layout_A.png`：陀斧顶 **y = 105**（橙线），眼睛约 **y = 405**（蓝线），脚底 **y = 1185**（红线）：**72 格高、约 68 格宽**。
- **O（全盛姿态 3/4）**：每格 **11 px**；照 `2_target_O.png` / `3_layout_O.png`：最高点 **y = 385**，眼睛约 **y = 561**，脚底 **y = 1188**：**73 格高、约 104 格宽**。
- 全在画布里，陀斧、护肩、头发不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head_base.png` 普通、`4_head_allout.png` 全盛，都是第 0 步读回的头，8 倍）：深棕色的脸（2–3 档，亮面偏暖）；**两只眼睛都看得见：每只约 2 × 1 或 2 × 2 格，一格白、一格深色瞳孔，一样高**；浓眉；**黑色络腮胡包住下巴**，和脸、头发**用不同的深色分开**（胡子近黑、头发深棕黑，不要糊成一整块黑）；嘴巴在胡子里看得见（全盛时咧嘴露出一排白牙）；头顶一簇往上翘的黑色小脏辫；左耳一个金色小耳环。
- **身体**：**深红色厚外套**（3 档，**胸口两侧和两臂上要大片看得见**），袖子上**金色和紫色的菱形花纹**；**巨大的古铜金护肩**、护腕、护膝（3 档，亮边浅金）；胸前**粗金绳和几块圆形金徽章**；**蓝紫色围巾**；**紫色锯齿围裙**；**深紫裤子**；**棕色靴子**踩在地面线上，**两条腿之间要有空隙和描边分开**；近处的腿全亮，远处的腿暗一档。
- **陀斧**：两把**青灰色石头**陀斧（3 档），嵌着**亮青色水晶**（2 档，一格一格清楚），**金色边纹**和**金色圆徽章**；A 里竖在身体两侧、顶端高过头；O 里甩开成长棍、末端搁在地面上。**陀斧不挡脸**。
- **A 和 O 是同一个人**：脸、胡子、头发、外套、颜色一样，只有姿势不同。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的布隆、奥恩、加里奥，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `ksante_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_O.png` | 你第 0 步画的原始图（用户认可） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_O.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_O.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_base.png` / `4_head_allout.png` | 第 0 步读回的两个头（8 倍） | 脸、眼睛、胡子、头发、耳环；全盛的咧嘴 |
| `style/5_style_braum.png`、`6_style_ornn.png`、`7_style_galio.png` | 本包的布隆、奥恩、加里奥，8 倍放大 | **只看风格**：这么粗的格子里大块头的脸、胡子、盔甲、石头怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1O your own earlier pixel-art drawings of one character - a HUGE BROAD-SHOULDERED TANK WARRIOR with dark brown skin, short black twists of hair standing up, a black full beard, a small gold earring, a blue-violet scarf, a thick padded CRIMSON COAT with gold-and-violet diamond patterns on the sleeves, huge bronze-gold pauldrons, bracers and knee guards, thick gold ropes and round gold medallions over his chest, a violet tabard with a jagged hem, dark plum trousers, brown boots, and two giant teal-grey STONE SHIELD-TONFAS set with bright teal crystals, gold trim and a round gold medallion; 1A his normal stance (the tonfas held upright beside him), 1O his ALL OUT stance (hunched, the tonfas swung out as long clubs) - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A and 2O the same pictures cut down to the RIGHT square count - 72 squares from the tonfa tops to the soles in the normal stance, 73 squares in All Out - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A and 3O the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the two heads enlarged (normal, All Out); 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a big man's face, beard, armour and stone are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ: the dark brown face in 2-3 warm shades; BOTH EYES visible, each about 2x1 or 2x2 squares (one white square and a dark pupil) at the SAME height; heavy brows; the BLACK BEARD wrapping the jaw, the mouth visible in it, the beard, the hair and the face kept apart by their own dark shades (never one black mass); the black twists standing up on top; a gold earring square. The CRIMSON COAT in 3 shades CLEARLY VISIBLE on the chest sides and both arms (NOT turned into all-gold), its sleeves with gold and violet diamond patterns; the bronze-gold pauldrons, bracers and knee guards in 3 shades with pale-gold lit edges; the gold ropes and round medallions; the blue-violet scarf; the violet jagged tabard; the dark plum trousers; brown boots on the ground line with a clear gap and outline between his legs, the near leg in full tone and the far leg a step darker. The two teal-grey stone tonfas in 3 shades with bright teal crystal squares in 2 shades, gold trim and a gold medallion; they NEVER cover his face.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`ksante-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: his NORMAL idle exactly as images 1A, 2A and 3A - standing tall and steady in 3/4 view facing right, each fist holding a tonfa UPRIGHT beside his body, their tops above his head, the face to the front-right, calm and confident; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both boots on the ground line. Every square exactly 15 px; the tonfa tops at y 105, his eyes at about y 405, his soles on y 1185 - exactly 72 squares tall, about 68 squares wide.
  ```
- **O（`ksante-model-O-1.png`、`-O-2.png`，两稿）**：
  ```text
  PICTURE O: his ALL OUT idle exactly as images 1O, 2O and 3O - the SAME man as picture A, hunched forward in 3/4 view facing right, the back bent, the knees bent in a wide half-squat, both fists low, the two tonfas swung out as long clubs whose ends REST ON THE GROUND beside and in front of his boots; the face to the front-right, fierce, a row of white teeth showing. Every square exactly 11 px; his highest point at y 385, his eyes at about y 561, his boots AND the tonfa ends on y 1188 - exactly 73 squares tall, about 104 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 15 px、72 格高；O 每格 11 px、73 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 两只眼睛看得见、一样高；胡子、头发、脸分得开；**深红外套大片看得见**；金色护甲、金绳徽章、蓝紫围巾、紫色围裙、深紫裤子、棕靴清楚；两条腿分开。
- 两把青石陀斧带水晶、金边、金徽章，不挡脸；O 的靴子和陀斧末端都在地面线上。A 和 O 是同一个人。外描边连续；没有任何技能特效。

## 交付（`outputs/ksante-model/`）

- `ksante-model-A-1.png`、`ksante-model-A-2.png`、`ksante-model-O-1.png`、`ksante-model-O-2.png`；原始生成图原样放 `outputs/ksante-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ksante_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 15 px / 72 行，O 约 11 px / 73 行），从 raw/ 按格读回（regrid），在游戏大小下和布隆、奥恩、加里奥、沃利贝尔并排自查（PPU 1.5：A 48、O 约 49 游戏像素），把两稿给用户挑。脸放大 12 倍检查，眼睛 / 嘴的格子不清楚就在设计脚本里重画（`codex-face-half-squares` 的做法）。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py KSante`，`pose_ref.py --champ KSante` 带 `pack_ksante_picture.py` 的 PARTS）；腿和待机一致、不变形；一张脸用在所有帧。数据里的动作名见 `tools/kit/build_ksante.py`：idle run attack skill skill_b skill_c skill2 skill2_dash ult ult_dash hit dead，全盛 ao_idle ao_run ao_attack ao_skill ao_skill_b ao_skill_c ao_skill2 ao_skill2_dash（全盛的待机和跑由附加包的视图切换换上）。
