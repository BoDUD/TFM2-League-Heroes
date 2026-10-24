# 铸星龙王 奥瑞利安·索尔：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的两张原稿（`1_picture_A.png` 悬浮待机、`1_picture_B.png` 飞行）**样子、颜色用户认可了，全照它们**。
> - 这一步要画成**游戏里的格子数**：**A 从冠盔顶到尾尖 77 格**，**B 同一个比例，从鬃毛顶到最低的爪尖 51 格**。我把图直接缩到这个格子数（`2_target_A.png`、`2_target_B.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、金冠的纹路和胸口的鳞片碎成杂斑、星星糊成一片）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 8 px 一格，A 约 151 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**A 每格 14 px，B 每格 13 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**：A-1 / A-2（悬浮待机，两稿），B-1 / B-2（飞行，两稿），都是 3/4 正面朝右。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（悬浮待机，3/4 朝右）**：每格 **14 px**；照 `2_target_A.png` / `3_layout_A.png`：冠盔顶 **y = 112**（橙线），眼睛约 **y = 392**（蓝线），尾尖 **y = 1190**（红线）：**77 格高、约 56 格宽**（往前张开的爪子算在宽里）。
- **B（飞行，3/4 朝右）**：每格 **13 px**；照 `2_target_B.png` / `3_layout_B.png`：鬃毛顶 **y = 533**（橙线），眼睛约 **y = 780**（蓝线），最低的爪尖 **y = 1196**（红线）：**51 格高、约 84 格宽**（连星云尾巴）。
- 全在画布里，冠角、鬃毛、爪子、尾巴不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的头（8 倍），看位置和颜色。

- **脸**（最要紧）：**浅蓝白色的骨质龙脸**（3 档），长下颌朝右前方；**眼睛是青色发光的**：近处的眼睛 **2 × 2 格**（一格亮青 + 一格白高光 + 下面一格暗青），远处的眼睛 **至少 1 × 2 格**，也要看得出是亮青色；嘴闭着，**一排白色尖牙**（每颗 1 格宽、1–2 格高，牙缝用脸最暗的一档），下巴尖上 **1–2 格金色小尖**；眼睛上方金冠的边压着，但**不挡眼睛**。
- **金冠和角**：头上一顶**金色冠盔**（金黄 3 档：暗金描边、金、亮金高光成块），额前一个圆形纹（2–3 格的圈）；两侧一对**金色的角往后扫**（每只 2–3 格粗、尖细的尾端），角尖不出画。
- **鬃毛**：冠盔后面一大簇**洋红-紫色鬃毛**（3–4 档：深紫描边、紫红、洋红、亮粉高光），一簇簇往后、往上翻成尖角（每簇 3–5 格的尖）。
- **脖子和身体**：短一点的脖子；**深海军蓝的鳞甲身体**（3 档），胸口一排**亮蓝色的 V 形鳞片**（2 档，每片 2–3 格宽）；**青色发光细线**（亮青 1 格宽，连续不断）沿着身体爬；肩上一个**青色的圆环纹**（2–3 格的圈）和 1–2 颗**金色小圆钉**（各 1–2 格）；背上一排**深紫色的尖刺**（每根 2–3 格的三角）。
- **手臂**：**紫色的龙爪手臂**（3 档），手腕上**金色护腕**（2 档，2 格宽）；A：近手垂在身侧、爪子向下弯，远手往前张开**四根尖爪**（每根 1 格宽、2–3 格长，爪缝空出来看得见背景）；B：两只爪子往前下方伸。
- **星云尾巴**：胸口往下变成**深蓝 → 紫罗兰的星云尾巴**（3–4 档，边上深蓝、中间一条紫罗兰的亮带），A 往下卷一个 S 弯、尾尖在红线上；B 在身后（画面左）拉成长波浪。**星星**：白色 / 浅蓝的单格点或 3 × 3 的小十字，**间隔开**，A 大约 15–20 颗、B 大约 15 颗，不要密成一片。尾巴越往尾尖越细，**尾尖 1–2 格宽**。
- 近的手臂（画面左）全亮，远的暗一档；**手臂和身体之间、爪子之间空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断（尾巴也要描边）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格（星星除外）。

## 干净

- 和附图 5–7 一样的像素画（本包的维克兹、斯莫德、希瓦娜龙形，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、星空背景、技能特效。

## 附图（压缩包 `aurelionsol_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` / `1_picture_B.png` | 第 0 步你画的两张原稿：**样子和颜色全照它们** |
| `2_target_A.png` / `2_target_B.png` | 直接缩到 77 / 51 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_A.png` / `3_layout_B.png` | 带网格和三条线（橙 = 冠盔 / 鬃毛顶，蓝 = 眼睛，红 = 尾尖 / 最低的爪尖） |
| `4_head.png` | 读回的头（8 倍）：位置和颜色 |
| `style/5_style_velkoz.png` `6_style_smolder.png` `7_style_shyvana_dragon.png` | **只看风格** |

## 提示词 A（A-1、A-2 各画一次，同一段；附 1_picture_A、2_target_A、3_layout_A、4_head、style 三张）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = top of the crest, blue = the eyes, red = the tail tip), 4 his head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 14 px, aligned on one grid starting at the canvas corner (0, 0). THE STAR DRAGON hovering in 3/4 view facing right, exactly the pose of images 1-2: the top of his crest at y 112, the eyes at about y 392, the tip of his nebula tail on y 1190 - 77 squares tall, about 56 squares wide. Every detail in whole 14-px squares - never smaller squares.
THE FACE (most important): a PALE BLUE-WHITE BONY DRAGON FACE in 3 shades, the long jaw to the front-right; GLOWING CYAN EYES: the near eye 2x2 squares (one bright cyan, one white highlight, one darker cyan below), the far eye at least 1x2 squares, clearly bright cyan; the mouth closed with a row of WHITE SHARP TEETH (each 1 square wide, 1-2 tall, the gaps in the face's darkest shade); 1-2 GOLD squares at the chin's point; the edge of the gold helm above the eyes, never covering them.
THE HELM AND HORNS: a GOLD CROWN-HELM (gold in 3 shades: a dark gold edge, gold, light gold highlights in blocks) with a round mark of 2-3 squares on the brow; a pair of GOLD HORNS sweeping back on both sides (2-3 squares thick, tapering to points), the tips inside the picture.
THE MANE: a big MAGENTA-VIOLET MANE behind the helm (3-4 shades: a dark purple edge, plum, magenta, light pink highlights), flowing back and up in pointed tufts of 3-5 squares.
THE BODY: a short neck; a DEEP NAVY SCALED BODY (3 shades) with a row of BRIGHT BLUE V-SHAPED SCALES down the chest (2 shades, each 2-3 squares wide); thin GLOWING CYAN LINES (bright cyan, 1 square wide, unbroken) running over it; a cyan RING mark of 2-3 squares on the shoulder and 1-2 small GOLD STUDS (1-2 squares each); a row of DARK PURPLE SPIKES along the back (triangles of 2-3 squares).
THE ARMS: PURPLE CLAWED ARMS (3 shades) with GOLD BRACERS (2 shades, 2 squares wide); the near arm hanging at his side, its claws curled down; the far arm reaching forward with FOUR open pointed claws (each 1 square wide, 2-3 long, the background visible between them).
THE NEBULA TAIL: below the chest a DEEP BLUE to VIOLET NEBULA TAIL (3-4 shades, deep blue at its edges, a brighter violet band down its middle) curling down in one S curve, its tip on the red line, thinner toward the tip (1-2 squares wide at the end); WHITE / PALE BLUE STARS on it - single squares or small 3x3 plus shapes, spaced apart, about 15-20, never a dense spray.
The near arm (image left) in full tone, the far one a step darker; the background visible between the arms and the body and between the claws.
A continuous 1-square near-black outline round him (the tail too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares except the stars; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no starry sky behind him, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects.
```

## 提示词 B（B-1、B-2 各画一次，同一段；附 1_picture_B、2_target_B、3_layout_B、4_head、style 三张）

```text
Attached: 1 the character's approved flying picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = top of the mane, blue = the eyes, red = the lowest claw tip), 4 his head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 13 px, aligned on one grid starting at the canvas corner (0, 0). THE STAR DRAGON flying to the image right in 3/4 view, exactly the pose of images 1-2: his body level, the head first, both clawed arms reaching forward and down, the mane and the back spikes swept back, the nebula tail streaming behind him to the image left in one long wave; the top of the mane at y 533, the eyes at about y 780, the lowest claw tip on y 1196 - 51 squares tall, about 84 squares wide with the tail. Every detail in whole 13-px squares - never smaller squares.
THE FACE (most important): a PALE BLUE-WHITE BONY DRAGON FACE in 3 shades, the long jaw pointing right; GLOWING CYAN EYES: the near eye 2x2 squares (one bright cyan, one white highlight, one darker cyan), the far eye at least 1x2 squares, clearly bright cyan; the mouth closed with a row of WHITE SHARP TEETH (each 1 square wide, 1-2 tall, the gaps in the face's darkest shade); 1-2 GOLD squares at the chin's point; the gold helm's edge above the eyes, never covering them.
THE HELM AND HORNS: a GOLD CROWN-HELM (gold in 3 shades) with a round mark on the brow and a pair of GOLD HORNS sweeping back; THE MANE: a big MAGENTA-VIOLET MANE (3-4 shades) streaming back in pointed tufts of 3-5 squares.
THE BODY: a DEEP NAVY SCALED BODY (3 shades) with BRIGHT BLUE V-SHAPED SCALES on the chest (2 shades), thin unbroken GLOWING CYAN LINES (1 square wide), a cyan RING mark of 2-3 squares on the shoulder, small GOLD STUDS (1-2 squares) along the back and a row of DARK PURPLE SPIKES (triangles of 2-3 squares) swept back.
THE ARMS: PURPLE CLAWED ARMS (3 shades) with GOLD BRACERS (2 shades), both reaching forward and down, the claws open (each claw 1 square wide, 2-3 long, the background visible between them); the near arm (image left) in full tone, the far one a step darker.
THE NEBULA TAIL: from his back a DEEP BLUE to VIOLET NEBULA TAIL (3-4 shades, a brighter violet band down its middle) streaming to the image left in one long wave, thinner toward its tip (1-2 squares wide at the end); WHITE / PALE BLUE STARS on it - single squares or small 3x3 plus shapes, spaced apart, about 15, never a dense spray.
A continuous 1-square near-black outline round him (the tail too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares except the stars; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no starry sky behind him, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects.
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**A 每格 14 px、B 每格 13 px**，对齐从 (0, 0) 开始的网格；A 冠盔顶 y 112、尾尖 y 1190（77 格）；B 鬃毛顶 y 533、最低爪尖 y 1196（51 格）。
- **脸**：浅蓝白骨质龙脸、**亮青色眼睛（近眼 2×2 带白高光，远眼也看得见）**、一排白尖牙、下巴金尖；金冠不挡眼睛。
- 金冠金角、洋红-紫鬃毛、深蓝鳞甲 + 亮蓝 V 鳞 + 连续的青色发光线、肩上青色圆环、背刺；紫色龙爪 + 金护腕，爪缝空开。
- 星云尾巴深蓝 → 紫罗兰，星星间隔开不密；A 尾尖在红线上，B 尾巴在身后拉长。
- 1 格近黑外描边连续；没有零散杂色格（星星除外）、没有抖动和渐变。
- 交付：`outputs/aurelionsol-model/aurelionsol-A-1.png`、`aurelionsol-A-2.png`、`aurelionsol-B-1.png`、`aurelionsol-B-2.png`；原始生成图原样放进 `outputs/aurelionsol-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/aurelionsol-model/HANDOFF.md`，再打包成 `outputs/aurelionsol_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/aurelionsol/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；Codex 常画得比要求的粗或细，按它自己的格子读回），A 裁到 77 行、B 裁到 51 行（keep_axis、脸框保留，`design_taliyah_model.py` 的做法），12 倍下看脸（两只青色眼睛、牙、金冠不压眼），给用户挑稿 -> `hd/idle.png`（A，PPU 1.75，冠盔顶到尾尖 44 游戏像素）、`hd/run.png`（B，同一比例）。
- 浮空英雄：A 的尾尖在地面线上，游戏里的悬浮高度在拼动作时加（维克兹的 FLOAT）。
