# 暴怒骑士 克烈：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的两张原稿（`1_picture_A.png` 骑乘、`1_picture_B.png` 下马步行）**样子、颜色用户认可了，全照它们**。
> - 这一步要画成**游戏里的格子数**：**A 从帽子尖刺顶到斯嘎尔的爪子底 80 格**，**B 同一个比例，从帽子尖刺顶到靴底 58 格**。我把图直接缩到这个格子数（`2_target_A.png`、`2_target_B.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、毛和鳞片碎成杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 5 px 一格，A 约 244 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**A、B 都是每格 14 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**：A-1 / A-2（骑乘，两稿），B-1 / B-2（下马步行，两稿），都是 3/4 正面朝右。
> - **A 和 B 里克烈的头是同一个头**（同样大小、同样的帽子、耳朵、脸），后面所有动作都用这一张脸。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（骑乘待机，3/4 朝右）**：每格 **14 px**；照 `2_target_A.png` / `3_layout_A.png`：帽子尖刺顶 **y = 70**（橙线），他的眼睛约 **y = 392**（蓝线），斯嘎尔的爪子底 **y = 1190**（红线）：**80 格高、约 56 格宽**（斧头和捕熊夹算在宽里）。
- **B（下马步行，3/4 朝右）**：每格 **14 px**；照 `2_target_B.png` / `3_layout_B.png`：帽子尖刺顶 **y = 378**（橙线），他的眼睛约 **y = 686**（蓝线），靴底 **y = 1190**（红线）：**58 格高、约 62 格宽**（斧头算在宽里）。
- 全在画布里，帽子尖刺、耳朵、斧头、捕熊夹、尾巴不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的他的头（8 倍），看位置和颜色。

- **克烈的脸**（最要紧）：Q 版**大头**（帽子连脸大约占他自己身高的一半，比 `2_target` 里大一点也可以，身子相应小一点）；脸上是**米白色的毛**（3 档），朝右前方；**两只眼睛一样高**：**瞎的那只**（画面左边、离我们近）乳白色 **2 × 2 格**、带一格浅灰和一道 **1 格宽的粉红疤痕**竖着穿过；**好的那只**（画面右边）**2 × 2 格**，一格亮琥珀黄 + 一格黑；眉毛 1 格、凶；**咧到耳根的狂笑**：嘴里深红（2 档），**一排白色尖牙**（每颗 1 × 2 格，上下各一排）；**米白色大胡子**一簇簇的尖往下垂，不挡眼睛。
- **耳朵**：**又大又尖的长耳朵**往两边伸（近的那只大，耳内粉色 2 档，外面米白），轮廓清楚。
- **帽子**：**青绿色帽身**（3 档）+ **红色帽边**（2 档），帽顶竖着一根**钢灰色的大尖刺**（3 档 + 1 格白高光，最高点就是这根刺的尖）；帽下一条**红色头带**；两侧**棕色皮护耳**（2 档）。
- **身体**：**青绿色上衣**（3 档），**红色腰带**（2 档、打结垂下），**棕色皮背带**（1 格宽），**深灰裤子**带暗绿竖条，**黑靴**（2 档）；手是棕色手套。
- **武器**：A——一只手拿**小双刃斧**（钢灰 3 档 + 1 格亮边，棕柄），另一只手拎着**拴在绳子上的捕熊夹**（棕绳 1 格宽、一格一格的结，钢灰的夹子带尖齿）。B——双手握一把**大双刃斧**斜在身前（两片弯月形钢刃，3 档钢灰 + 亮边，棕柄）。
- **斯嘎尔（A）**：**橙黄 / 琥珀色鳞片**（4 档，亮处金黄、暗处红棕，鳞片用暗一档的小块表示）；**紫色的肚子和喉咙**（3 档，横纹）；头顶和后脑一排**青蓝色的尖刺**（3 档，尖尖的一簇）；脖子两侧**橙紫两色的颈鳍**；**一只大眼睛**：**黄绿色 3 × 3 格**、黑色竖瞳 1 格、一格白高光，**紫色眼睑**一圈；宽嘴、嘴角上扬；**两条深紫色的细长后腿**（3 档），膝下**棕色皮护腿 + 一颗金色星星**（2 档）；**深紫黑的爪子**（每只 3–4 格宽、分三趾）；身后**一条尾巴**（橙色、青蓝尖）；背上**棕色皮鞍和皮带**。
- 近的腿（画面左）全亮，远的腿暗一档、稍高；**腿和腿之间、绳子和身体之间、斧柄和身体之间空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断（绳子、斧柄也要描边）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的瑟庄妮、努努和威朗普、吉格斯，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（冲锋的尘土、护盾、枪火都不画）。

## 附图（压缩包 `kled_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` / `1_picture_B.png` | 第 0 步你画的两张原稿：**样子和颜色全照它们** |
| `2_target_A.png` / `2_target_B.png` | 直接缩到 80 / 58 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_A.png` / `3_layout_B.png` | 带网格和三条线（橙 = 帽子尖刺顶，蓝 = 他的眼睛，红 = 爪子底 / 靴底） |
| `4_head.png` | 读回的他的头（8 倍）：位置和颜色 |
| `style/5_style_sejuani.png` `6_style_nunu.png` `7_style_ziggs.png` | **只看风格** |

## 提示词 A（A-1、A-2 各画一次，同一段；附 1_picture_A、2_target_A、3_layout_A、4_head、style 三张）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = the tip of his hat spike, blue = his eyes, red = the lizard's claws), 4 his head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 14 px, aligned on one grid starting at the canvas corner (0, 0). THE GRUMPY LITTLE BIG-EARED WARRIOR RIDING HIS BIG UPRIGHT LIZARD at rest in 3/4 view facing right, exactly the pose of images 1-2: the lizard standing on its two legs, its big head and eye forward; the rider seated behind and above its head, a small two-bladed axe in one hand on the image left, a bear trap hanging on a rope from his other raised hand on the image right; the tip of his hat spike at y 70, his eyes at about y 392, the lizard's claws on y 1190 - 80 squares tall, about 56 squares wide. Every detail in whole 14-px squares - never smaller squares.
HIS FACE (most important): chibi - a BIG HEAD (the hat and face about half of his own height; a little bigger than in image 2 is fine, the body a little smaller); CREAM-WHITE FUR in 3 shades turned to the front-right; TWO EYES at the SAME height: the BLIND EYE (image left) milky white 2x2 squares with one light grey square and a 1-square-wide PINK SCAR running down through it, the GOOD EYE (image right) 2x2 squares, one bright amber-yellow and one black; a 1-square fierce brow; a MANIC GRIN from ear to ear, dark red inside (2 shades), a row of WHITE POINTED TEETH above and below (each 1x2 squares); a big CREAM-WHITE BEARD hanging in pointed tufts, never over the eyes.
THE EARS: HUGE POINTED EARS sticking out sideways (the near one big, pink inside in 2 shades, cream outside), clear outlines.
THE HAT: a TEAL hat (3 shades) with a RED brim (2 shades) and a BIG STEEL-GREY SPIKE standing on top (3 shades and one white highlight square; its tip is the highest point); a RED headband under it; BROWN leather ear flaps (2 shades).
THE BODY: a TEAL-GREEN coat (3 shades), a RED sash (2 shades, knotted, hanging), BROWN leather straps (1 square wide), dark grey trousers with dark green stripes, black boots (2 shades), brown gloves.
THE WEAPONS: the small TWO-BLADED STEEL AXE (3 greys and a 1-square bright edge, a brown haft); the BEAR TRAP on a BROWN ROPE (1 square wide, knotted squares), the trap steel grey with pointed teeth.
THE LIZARD: AMBER-ORANGE SCALES in 4 shades (gold lit, red-brown in the shadows, scales as small blocks a shade darker); a PURPLE belly and throat (3 shades, banded); a row of TEAL-BLUE SPINES on the head and nape (3 shades, pointed); ORANGE-AND-PURPLE neck FRILLS; ONE BIG EYE: YELLOW-GREEN 3x3 squares with a 1-square black slit pupil and one white highlight, a PURPLE lid round it; a wide upturned mouth; two thin DARK PURPLE legs (3 shades) with BROWN LEATHER SHIN GUARDS bearing a GOLD STAR (2 shades); PURPLE-BLACK three-toed CLAWS (3-4 squares wide each); an orange tail with a teal tip behind; a brown leather saddle and straps.
The near leg (image left) in full tone, the far one a step darker and a little higher; the background visible between the legs, between the rope and the body and between the axe haft and the body.
A continuous 1-square near-black outline round the whole character (the rope and the haft too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects (no dust, no shield, no gun blast).
```

## 提示词 B（B-1、B-2 各画一次，同一段；附 1_picture_B、2_target_B、3_layout_B、4_head、style 三张）

```text
Attached: 1 the character's approved picture on foot (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = the tip of his hat spike, blue = his eyes, red = his boots), 4 his head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 14 px, aligned on one grid starting at the canvas corner (0, 0). THE GRUMPY LITTLE BIG-EARED WARRIOR ON FOOT in 3/4 view facing right, exactly the pose of images 1-2: standing on his short legs, feet apart, a BIG TWO-BLADED AXE held in both hands across his front, its blades on the image right; the tip of his hat spike at y 378, his eyes at about y 686, his boots on y 1190 - 58 squares tall, about 62 squares wide. Every detail in whole 14-px squares - never smaller squares.
HIS FACE (most important): the SAME chibi head as when he rides - BIG (the hat and face about half of his height); CREAM-WHITE FUR in 3 shades turned to the front-right; TWO EYES at the SAME height: the BLIND EYE milky white 2x2 with a 1-square PINK SCAR through it, the GOOD EYE 2x2 amber-yellow and black; a 1-square fierce brow; the MANIC GRIN, dark red inside, rows of WHITE POINTED TEETH (1x2 squares each); the big CREAM-WHITE BEARD in pointed tufts, never over the eyes.
THE EARS: HUGE POINTED EARS sideways (pink inside in 2 shades), clear outlines.
THE HAT: TEAL (3 shades) with a RED brim (2 shades) and the BIG STEEL-GREY SPIKE on top (3 shades, a white highlight; the highest point); a RED headband; BROWN leather ear flaps.
THE BODY: a TEAL-GREEN coat (3 shades), a RED sash (2 shades) knotted and hanging, BROWN straps (1 square), dark grey trousers with dark green stripes, black boots (2 shades), brown gloves on the haft.
THE AXE: a long BROWN haft (1-2 squares thick) and TWO big CRESCENT STEEL BLADES (3 greys with a 1-square bright edge, the inner curve dark), clear outlines.
The near leg (image left) in full tone, the far one a step darker; the background visible between the legs and between the haft and the body.
A continuous 1-square near-black outline round the whole character (the haft too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects (no gun blast, no dust).
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**A、B 都是每格 14 px**，对齐从 (0, 0) 开始的网格；A 帽尖 y 70、爪子底 y 1190（80 格）；B 帽尖 y 378、靴底 y 1190（58 格）。
- **克烈的脸**：Q 版大头、米白毛；**瞎眼（乳白 + 粉疤）和好眼（琥珀黄）一样高、各 2×2**；咧嘴狂笑露白色尖牙；大胡子不挡眼睛；大尖耳朵；青绿红边帽子 + 钢尖刺 + 红头带。**A 和 B 是同一个头**。
- 青绿上衣 + 红腰带 + 棕背带 + 深灰条纹裤 + 黑靴；A 小双刃斧 + 绳子拴的捕熊夹，B 大双刃斧。
- 斯嘎尔：橙黄鳞片、紫肚子、青蓝头刺、**一只 3×3 的黄绿大眼睛**（紫眼睑）、细长紫腿 + 棕护腿金星、紫黑爪子、尾巴、棕鞍。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/kled-model/kled-A-1.png`、`kled-A-2.png`、`kled-B-1.png`、`kled-B-2.png`；原始生成图原样放进 `outputs/kled-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/kled-model/HANDOFF.md`，再打包成 `outputs/kled_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/kled/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；Codex 常画得比要求的粗或细，按它自己的格子读回），A 裁到 80 行、B 裁到 58 行（keep_axis、脸框保留，`design_sejuani_model.py` 的做法），12 倍下看脸（瞎眼 + 好眼一样高、牙、斯嘎尔的大眼），给用户挑稿 -> `hd/idle.png`（A，PPU 2.0，帽尖到爪子 40 游戏像素）、`hd/foot.png`（B，同一比例：下马后的待机 / 跑 / 攻击 / 手枪）。两张挑中的稿子头要统一成一个（挑定后以 A 的头为准贴到 B）。
