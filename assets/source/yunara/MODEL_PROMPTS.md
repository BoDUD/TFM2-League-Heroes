# 芸阿娜：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户选了你第 0 步画的 **A**（`1_picked_A.png`），定的大小是：游戏里**从金色发饰顶端到脚底 40 行**，每个游戏像素 1.5 格，也就是她要画成 **60 格高**。
> - 用户还要求：
>   - **头放大到约四分之一**：从头发顶到下巴约 **14 格**（A 里只有 18%，在游戏里脸看不清）。金色发饰在头发上面再高约 7 格，下巴以下约 39 格，身体仍然清瘦。
>   - **念珠画小一点**：每颗铜念珠约 **5 格宽**（A 里的念珠比她的头还大，到游戏里太挤）。紫水晶龙头珠也跟着画小：龙头约 **6 格宽**，光尾约 **10 格长**。
> - 我把 A 按这个比例直接缩好了（`2_target_body.png`，每格 12 px）。**大小、位置、姿势、头身比、念珠的位置都对，但是糊了**：脸和闭着的眼睛糊成几格，头发的高光没了；发饰、上衣、领扣、护腕、围布上的铜扣都糊在一起；脖子那里还有一道接缝。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，就像一个像素画师照着 A，在 `2_target_body.png` 的格子里一格一格重画出来。
> - 另外，念珠表也要按同样的格子、和她同一个比例重画一张（`5_picked_W.png` 是你第 0 步画的，`6_target_beads.png` 是我缩好的，也是糊的）。
> - **人和念珠表各画两稿。**

## 大小和位置（照 `2_target_body.png` / `3_layout.png` / `6_target_beads.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **她**：
  - **金色发饰顶端在 y = 240**（橙线），**头发顶在 y ≈ 324**（绿线），**下巴在 y ≈ 492**（蓝线），**脚底在 y = 960**（红线），两只脚底在同一条线上。
  - 左右位置、两只手在身前一高一低的样子、宽裤落到脚踝的样子，都照 `2_target_body.png`。
- **念珠**：六颗铜念珠漂在她身边，位置照 `2_target_body.png`：左边三颗，右边两颗，近侧手下面一颗；每颗约 5 格宽，和身体之间至少空 1 格。龙头珠在近侧手的下方，光尾连到手边。
- **念珠表**：单独一张 1024 × 1024 的图，摆法照 `6_target_beads.png`：八颗铜念珠排成一排，**每两颗之间空 3 格**；龙头珠和它的光尾在下面一排。

## 要画清楚的地方（她）

- **头**（`4_head.png`，**画大**，头发顶到下巴约 14 格）：
  - **淡紫色头发**，分 3–4 档，带几格亮白紫的高光，前额分开；**两条粗辫子**垂到胸前，辫子末端有金色环扣和紫色穗子。
  - 头顶两侧各一个**金色弯角发饰**（亮金、金、暗金三档），根部带一点棕红色，从头发后面往上翘，约 7 格高。
  - **白皙的脸**：**闭着的眼睛**是一道约 3 格宽的深色弧线，睫毛下垂；额头正中一格**银色额饰**；淡粉色的嘴唇；下巴尖。
- **身体**：
  - **深藏青色的长袖短上衣**，分 3 档，袖子和肩头的边缘要有亮一档的藏青，免得在深色背景上看不清。
  - 胸前一枚**金色的圆形领扣**（2–3 格），露出一截**腰腹**。
  - 前臂戴**金色宽护腕**，手是**蓝色的露指手套**。
  - **金色腰带**，前面垂一块**深紫色围布**，上面一排**铜色圆扣**（每颗约 1 格），侧面一道金边；腰侧挂一个**铜色螺旋小饰物**。
  - **很宽的淡紫色纱裤**，分 3 档，下摆偏蓝，落到脚踝。
  - **深紫色绑腿**，**棕色木头厚底凉鞋**。
- **念珠**：铜金色（亮金、铜色、暗棕三档），上面 2–3 格**深色圆钉**；龙头珠是紫水晶（亮淡紫、紫、深紫三档，带一格白色高光），光尾是两道 1 格宽的紫线。
- **一圈近黑外描边**，连续不断，每颗念珠也有；描边里面每种材质用它自己最暗的一档，不要再画一圈黑；没有孤立的杂色格。

## 要画清楚的地方（念珠表）

- 八颗铜念珠，每颗约 5 格宽，同一个样子（圆钉的角度可以稍有不同），每颗一圈近黑外描边，**每两颗之间空 3 格**。
- 龙头珠：龙头约 6 格宽，两道光尾约 10 格长，和念珠同一个比例。

## 干净

- 像素画的样子和附图 7–10 一样（本包的卡特琳娜、厄斐琉斯是每游戏像素 1.5 格，卡莉丝塔 1.4 格，尼菈；8 倍放大，一格 = 一个像素）：大小一致的方块，对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照 A。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `yunara_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它 |
| `2_target_body.png` | A 按新比例（头约四分之一、念珠变小）缩到游戏大小，每格 12 px 放在画布上（糊的） | **她的大小、位置、姿势、头身比、念珠的位置**照它，糊的地方重画 |
| `3_layout.png` | 同一张加网格线：橙线 = 发饰顶 y 240，绿线 = 头发顶 y 324，蓝线 = 下巴 y 492，红线 = 脚底 y 960 | 对齐网格，头和脚底的位置 |
| `4_head.png` | A 的头（读回后 8 倍放大） | 头发、发饰、辫子、脸、闭着的眼睛 |
| `5_picked_W.png` | 你第 0 步画的念珠表 | 念珠和龙头珠的**样子** |
| `6_target_beads.png` | 念珠表按她的比例缩好，每格 12 px 放在画布上（糊的） | 念珠表的**大小和摆法** |
| `style/7_style_katarina.png` … `10_style_nilah.png` | 本包的卡特琳娜、厄斐琉斯（每游戏像素 1.5 格）、卡莉丝塔（1.4 格）、尼菈，8 倍放大 | **只看风格**：这个密度下一格有多大，脸怎么画，描边，分档 |

## 提示词 1：`yunara-model-1.png`、`yunara-model-2.png`（她，两稿）

附全部 10 张图。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art picture of this character - a slim calm young woman martial artist with lilac hair in two long braids, two golden horn-like hair ornaments, a small silver forehead jewel, closed eyes, a dark navy long-sleeved cropped top with a round golden clasp, golden bracers and blue fingerless gloves, a golden belt with a dark purple front panel and bronze studs, very wide lavender gauze trousers, dark purple leg wraps and wooden platform sandals, with bronze prayer beads and a violet crystal dragon-head bead floating around her (the LOOK, the COLOURS and the DETAILS to keep); 2 the same woman shrunk to her final game size on a 1024x1024 canvas, 12 px a square, with her HEAD MADE BIGGER - about a quarter of her height - and the BEADS MADE SMALLER: the SIZE, the PLACE, the POSE, the HEAD-TO-BODY PROPORTION and where the beads float are right, but it is muddy (the face and closed eyes blurred, the hair highlights lost, the ornaments, top, clasp, bracers and the studs on the front panel smeared together, a seam at the neck); 3 the same with grid lines every 5 squares: the orange line = the top of her golden ornaments (y 240), the green line = the top of her hair (y 324), the blue line = her chin (y 492), the red line = her soles (y 960); 4 the head of image 1 enlarged; 5 the bead sheet as drawn before; 6 the bead sheet at her scale (for the other picture); 7-10 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture of the same woman: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of her golden ornaments at y 240, the top of her hair at y 324, her chin at y 492 (the head from the hair's top to the chin about 14 squares, about a quarter of her height - much bigger than in image 1, so the face reads at game size), her soles at y 960 on one ground line; both hands held in front of her body at different heights, the wide trousers falling to the ankles - as if a pixel artist redrew image 1 square by square on image 2's grid.
THE BEADS SMALL: six bronze beads floating where image 2 shows them (three on the left, two on the right, one below the near hand), each about 5 squares wide, at least 1 empty square from her body; the violet crystal dragon-head bead below her near hand, its head about 6 squares wide, its two streamers about 10 squares long reaching up to the hand.
Make it CRISP and READABLE at this size: LILAC HAIR in 3-4 shades with a few bright white-lilac highlight squares, parted at the forehead, TWO THICK BRAIDS over her chest ending in golden rings and purple tassels; TWO GOLDEN HORN-LIKE ORNAMENTS (bright gold, gold, dark gold) rising from behind her head about 7 squares, a touch of red-brown at their roots; a FAIR face, the CLOSED EYE a dark arc about 3 squares wide with drooping lashes, ONE silver square for the forehead jewel, pale pink lips, a pointed chin; the DARK NAVY CROPPED TOP in 3 shades with a lighter navy edge on the sleeves and shoulders so it reads on a dark background, the ROUND GOLDEN CLASP on the chest (2-3 squares), the bare midriff; WIDE GOLDEN BRACERS, BLUE FINGERLESS GLOVES; the GOLDEN BELT with the DARK PURPLE FRONT PANEL, a row of BRONZE STUDS (about 1 square each) and a golden edge, a small bronze spiral at the hip; the VERY WIDE LAVENDER TROUSERS in 3 shades, bluer at the hem; DARK PURPLE leg wraps, BROWN WOODEN PLATFORM SANDALS; the beads BRONZE-GOLD in 3 shades with 2-3 dark round studs each; the dragon bead VIOLET CRYSTAL in 3 shades with one white highlight square, its streamers two 1-square violet lines.
One continuous near-black outline round the figure and round every bead; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`yunara-beads-1.png`、`yunara-beads-2.png`（念珠表，两稿）

附同样 10 张图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of her BEADS alone (image 5's beads, at the size and layout of image 6): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255), every square 12 px aligned on one straight grid starting at the canvas corner, at the same scale as the beads in image 2.
Top row: EIGHT BRONZE PRAYER BEADS in a row, each about 5 squares wide, bronze-gold in 3 shades (bright gold, bronze, dark brown) with 2-3 dark round studs (the studs may sit at slightly different angles from bead to bead), EXACTLY 3 empty squares between any two beads. Bottom row, centred: the VIOLET CRYSTAL DRAGON-HEAD BEAD, its head about 6 squares wide in 3 violet shades with one white highlight square, two thin 1-square violet streamers about 10 squares long trailing up from it.
One continuous near-black outline round each bead; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No character, no effects, no glow, no background, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 她：
  - 大小、位置、姿势和 `2_target_body.png` 一样：发饰顶 y 240，头发顶约 y 324，下巴约 y 492，脚底 y 960，每格 12 px，对齐网格。
  - **头约占身高四分之一**，身体仍然清瘦。
  - 闭着的眼睛、额饰、两条辫子、金色发饰、领扣、护腕、围布上的铜扣都清楚。
  - **念珠每颗约 5 格宽**，比 A 小；外描边连续。
- 念珠表：八颗一排，每两颗之间空 3 格，龙头珠在下面，和她同一个比例。
- 颜色照 A；没有任何特效。
- 如果模型不肯画有名字的角色：提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/yunara-model/`）

- 四张图：`yunara-model-1.png`、`yunara-model-2.png`、`yunara-beads-1.png`、`yunara-beads-2.png`。
- **image_gen 的原始生成图原样放进 `outputs/yunara-model/raw/`**，不要再处理成格子图。
- `generation-prompts.txt`：写明实际用的提示词。
- **最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/yunara_model_done.zip`，这样我这边才知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 读回：
  - 原稿在 8 倍下数描边台阶，量出格子大小，按它自己的格子读回（regrid / k-means 调色板）。
  - 和 `2_target_body.png` 并排，再按游戏大小和卡莉丝塔、厄斐琉斯、金克丝、卡莎、德莱厄斯放在一起，给用户挑一稿（用户审核，不要自己判定）。
  - 念珠表两稿也一起给用户挑。
- 超凡形态版本（给附加包 R 期间换待机 / 跑步用）：等造型选定后再画。做法是同一个造型，头发和衣服边缘泛金白色的光，身后一圈淡金光环。
- 动作帧：念珠是刚体部件，只平移，不变形。动作对应英雄联盟的：
  - 跑步：run
  - 普攻：attack1 / attack2（掌击，念珠飞出）
  - Q 期间的强化普攻：Spell1_Attack1
  - W 念珠：Spell2
  - R 射线：Spell4_W
  - R 冲刺：Spell4_E
  - R 开启：Spell4_Nomove
  - 死亡：Death
