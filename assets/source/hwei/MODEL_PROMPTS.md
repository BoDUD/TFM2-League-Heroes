# 异画师 彗：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的原始图（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 用户定了：**只做 3/4 正面朝右，不要侧面**；**从头发顶到脚底 60 格**，背后的弯月墨痕在头顶上方另算（连墨痕一共 75 格高）。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、眉毛、耳饰、翻领的金纹、画笔的箍碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，**每格 15 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（同一个彗、同样的颜色）：`A-1` / `A-2`。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（待机）**：每格 **15 px**；照 `2_target_A.png` / `3_layout_A.png`：弯月墨痕的顶约 **y = 75**，**头发顶 y = 300**（橙线），眼睛约 **y = 450**（蓝线），脚底 **y = 1200**（红线）：**头发顶到脚底 60 格**，连墨痕 **75 格高、约 62 格宽**。
- 全在画布里，墨痕、头发、画笔不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head_A.png`，第 0 步读回的头，8 倍）：苍白的脸（2–3 档，暗处淡紫灰）；**两只墨绿色的眼睛都看得见：每只约 2 × 2 格（一格深色瞳孔、一格亮绿或白色高光），一样高**；每只眼睛上面**一道深色的眼皮线**（整格），眼皮半垂，一副疲惫忧郁的样子；细眉；小嘴，不笑；**墨绿近黑的乱发**斜着盖住额头和一边眼角，但**两只眼睛都露出来**（头发 **3–4 档**，亮处青绿，和脸之间有清楚的描边，**不要糊成一片黑**）；耳朵上**一两格彩色耳饰**；脖子上**深紫色的颈环**（整格一圈）。
- **身体**：**靛蓝色的画师外套**（3 档），**宽大的青绿色翻领**（2–3 档）上**金色的花纹**（整格线条），**红橙色的袖口**；外套里**红橙色的衬衫**（2–3 档）和**棕色的马甲**；一只手（画面左边、近处）插在外套口袋附近；**墨绿色的七分裤**（2 档），小腿上**青绿色的丝带结**；一只脚踝**粉色的珠串**；**棕色的便鞋**踩在地面线上；**两条腿之间要有空隙和描边分开**；近处的腿（画面左边）全亮，远处的腿暗一档。
- **画笔**：画面右边的手握着笔杆，笔头**斜着朝前下方**，笔尖靠近地面但不躺在地上；笔杆**深棕近黑**（至少 2 格粗），握手下面几道**彩色的箍**；笔头**红色 + 深蓝色**（各 2 档），末端收成**木色的笔尖**（2 档）。
- **弯月墨痕**：从他身后（画面左边）绕过头顶的一道弯月，**只在头发顶上方和身后，绝不挡脸**；**深蓝色**为主（3 档），夹**橙色、青绿、金色**的笔触，墨痕至少 4 格粗；末端在画面左边**滴下三滴墨**（各自分开，各有描边）。墨痕是平涂的笔触，**不发光**。
- **一圈 1 格的近黑外描边**，连续不断（墨痕、墨滴、画笔都有）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–8 一样的像素画（本包的塞拉斯、玛尔扎哈、佐伊、妮蔻，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（颜料飞溅、火、雷、岩浆、眼睛、画卷、发光都不画）。

## 附图（压缩包 `hwei_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的原始图（用户认可） | **样子、颜色、细节、姿势**全照它 |
| `2_target_A.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` | 加网格线：橙 = 头发顶，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_A.png` | 第 0 步读回的头（8 倍） | 脸、眼睛、眉毛、乱发、耳饰、颈环 |
| `style/5_style_sylas.png`、`6_style_malzahar.png`、`7_style_zoe.png`、`8_style_neeko.png` | 本包的塞拉斯、玛尔扎哈、佐伊、妮蔻，8 倍放大 | **只看风格**：这么粗的格子里男性的脸、眼睛、头发、长外袍怎么画 |

## 提示词（两稿用同一段，各画一张）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of one character - a SLIM YOUNG PAINTER with pale skin, MESSY DARK GREEN-BLACK HAIR with teal lights over one eye, DARK GREEN EYES with heavy half-closed lids (tired, brooding), small colourful earrings, a DARK PURPLE CHOKER, an INDIGO PAINTER'S COAT with a WIDE TURQUOISE COLLAR, GOLD ORNAMENTAL TRIM and RED-ORANGE CUFFS over a RED-ORANGE SHIRT and a BROWN VEST, DARK GREEN CROPPED TROUSERS with TEAL RIBBON TIES, a pink bead anklet, BROWN LOAFERS, a GIANT PAINTBRUSH (dark shaft, red and navy brush head, wooden point) slanting down in his hand, and a FLOATING CRESCENT OF PAINT STROKES (navy with orange, teal and gold) curling behind him over his head, dripping three ink drops - his LOOK and COLOURS are approved, but he is drawn with far too many small squares; 2A the same picture cut down to the RIGHT square count - 60 squares from the top of his hair to the soles, 75 with the crescent - shown with big squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke the details; 3A the same with grid lines every 5 squares: orange = the top of the hair, blue = the eyes, red = the ground; 4A his head enlarged; 5-8 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a man's face, eyes, hair and a long coat are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES, every square exactly 15 px, aligned on one straight grid from the canvas corner; the top of the crescent at about y 75, the top of his hair at y 300, his eyes at about y 450, his soles on y 1200 - exactly 60 squares from hair top to soles, 75 squares tall with the crescent, about 62 squares wide; at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ: the pale face in 2-3 shades with lavender-grey shadows; BOTH DARK GREEN EYES visible, each about 2x2 squares (one dark pupil square, one bright highlight square), at the SAME height, a dark lid line of whole squares above each, the lids half closed; thin brows; a small unsmiling mouth; the messy dark green-black hair in 3-4 shades with teal lights, falling over the forehead and the corner of one eye but leaving BOTH eyes visible, kept apart from the face by the outline - never one black mass; one or two coloured earring squares; the dark purple choker. The indigo coat in 3 shades, the wide turquoise collar in 2-3 shades with gold trim lines of whole squares, red-orange cuffs; the red-orange shirt in 2-3 shades and the brown vest; the NEAR hand (image left) near his coat pocket; the dark green cropped trousers in 2 shades with teal ribbon bows at the calves, a pink anklet, brown loafers on the ground line, a clear gap and outline between his legs, the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker. THE PAINTBRUSH held in his hand on the image right, slanting forward and down, its point near the ground but never lying on it: the shaft dark brown-black at least 2 squares thick with a few coloured bands below the hand, the brush head red and navy (2 shades each) ending in a wooden point (2 shades). THE CRESCENT behind him on the image left and over his head, NEVER over his face: at least 4 squares thick, navy in 3 shades with orange, teal and gold strokes, three separate ink drops falling from its end on the image left, flat painted strokes, not glowing.
One continuous 1-square near-black outline round the figure, the brush, the crescent and each drop; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects (no paint splashes, no fire, no lightning, no lava, no eyes, no scrolls, no glow), no background, no ground, no cast shadow, no text, no grid lines.
PICTURE A: his loose idle exactly as images 1A, 2A and 3A - standing in 3/4 view facing right, the face to the front-right and a little lowered, the near hand near his pocket, the paintbrush slanting down in the hand on the image right, the crescent behind him.
```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：每格 15 px，头发顶到脚底 60 格、连墨痕 75 格（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 两只墨绿眼睛看得见、一样高、眼皮半垂；乱发和脸分得开，不糊成一片黑；颈环、耳饰清楚；靛蓝外套、青绿翻领和金纹、红橙袖口、橙衬衫、棕马甲、墨绿七分裤和丝带、便鞋清楚；两条腿分开。
- 画笔斜指前下方，笔头红 + 深蓝、木色笔尖清楚；**弯月墨痕在身后和头顶上方，不挡脸**，三滴墨分开。外描边连续；没有任何技能特效。

## 交付（`outputs/hwei-model/`）

- `hwei-model-A-1.png`、`hwei-model-A-2.png`；原始生成图原样放 `outputs/hwei-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/hwei_model_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（约 15 px / 75 行），从 raw/ 按格读回（regrid，按读回误差最小的格子；量出来的格子比要求的小时，按身子和头的大小读，不按整张的包围盒），切到头发顶到脚底 60 行，在游戏大小下和塞拉斯、玛尔扎哈、佐伊、妮蔻并排自查（PPU 1.5：40 游戏像素），把两稿给用户挑。脸放大 12 倍检查，眼睛 / 嘴的格子不清楚就在设计脚本里重画（`codex-face-half-squares` 的做法）。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py Hwei`，片段名小写：idle_base、runslow、attack01、spell1q / spell1w / spell1e、spell3w / spell3e、spell4_alex、death）；一张脸用在所有帧；墨痕跟着身子走。数据里的动作名见 `tools/kit/build_hwei.py`：idle run attack hit dead；skill / skill_w / skill_e（灾：没骨火 / 攒聚雷 / 连皴山）；skill2 / skill2_q / skill2_e（悚：滞涩幽瞳 / 阴沉变意 / 双钩血喉）；ult。
