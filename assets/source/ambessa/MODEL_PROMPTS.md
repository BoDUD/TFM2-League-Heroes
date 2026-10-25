# 战争女族长 安蓓萨：第 1 步，游戏尺寸的 Q 版造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的两张原稿（`1_picture_A.png` 3/4 待机、`1_picture_SA.png` 侧面）**样子、颜色很好，全照它们**：青绿色的毛领、银白波浪短发、深棕皮肤、黑铁甲加铜色接缝、红围巾和红腰布、黑色大护臂、两把带镂空的钩形龙犬刃和铁链。
> - **要改的是比例**：原稿接近真人比例，头只占身高的约 1/6，缩到游戏大小后脸只剩几个色块。这一步要 **Q 版：头（连头发）约占身高的三分之一**，身子相应变矮。`2_target_A.png` / `2_target_SA.png` 是我把原稿的头放大到三分之一、再缩到游戏格子数的样子：**大小、位置、姿势、头的比例对，细节是缩坏的**（脸、甲片、刀都碎成了杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上、按目标图的比例**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细（约 5 px 一格，A 约 196 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**A、SA 都是每格 13 px**，**都是 84 格高**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**：A-1 / A-2（3/4 待机，两稿），SA-1 / SA-2（侧面，两稿），都朝右。
> - **A 和 SA 是同一个头**（同样大小、同样的头发和脸），后面所有动作都用这一张脸。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（待机，3/4 朝右）**：每格 **13 px**；照 `2_target_A.png` / `3_layout_A.png`：发顶 **y = 117**（橙线），她的眼睛约 **y = 325**（蓝线），脚底 **y = 1209**（红线）：**84 格高、约 82 格宽**（两把刀算在宽里，最多 84 格）。
- **SA（侧面，朝右）**：每格 **13 px**；照 `2_target_SA.png` / `3_layout_SA.png`：发顶 **y = 117**，眼睛约 **y = 312**，脚底 **y = 1209**：**84 格高、约 66 格宽**。
- 全在画布里，头发、毛领、刀尖、铁链不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的她的头（8 倍），看位置和颜色。

- **脸**（最要紧）：Q 版**大头**；**深棕色皮肤** 3 档（亮处暖橙棕）；脸朝右前方，下巴微抬，表情冷峻；A：**两只眼睛一样高、一样大**，每只 **2 × 2 格**（深色 + 一格红棕色虹膜 / 一格亮高光），**眉毛 1 格**、压低、凶；SA：一只眼睛 2 × 2，鼻尖和下巴朝右突出；**深红色的嘴唇** 2 格宽；颧骨高；**一格金色耳环**。
- **头发**：**银白色、往后梳的波浪短发**（3 档：白、浅灰、灰紫的暗处），蓬松地堆在头顶和脑后，不遮眼睛。
- **毛领**：肩上一圈**深青绿色、尖尖的毛**（3 档：亮青绿、青绿、墨绿），近的肩膀那一大簇最显眼，**和头发、皮肤之间有清楚的描边分开**。
- **甲**：**黑铁胸甲**（3 档：近黑、深灰、一格亮灰的高光边），甲片之间**一格铜色接缝**（2 档）；**深红色的围巾**绕在领口、**红色腰布**从腰间垂到膝下（3 档）；露出来的**粗壮上臂**是深棕皮肤；**黑色大护臂**（棱角分明，3 档 + 亮边）；腿上黑铁腿甲、黑靴（2–3 档）。**黑甲不要糊成一片**：每块甲片用亮一档的边和暗一档的阴影分开。
- **两把龙犬刃**（A：近的那把垂在画面左边、远的那把在画面右边，各握在一只手里；SA：近的那把在身前偏右，远的那把暗一档在身后偏左）：每把是**带钩的月牙形大刃**，**亮银色的外刃边**（2 档 + 1 格白高光），**深色的平板刃身**，刃上的**三角形镂空**看得见背景，几个**长长的尖角**；刀柄连着**粗铁链**（深铁灰 2 档，一节 1–2 格），在手和刀之间垂成一个弯。
- 近的腿全亮，远的腿暗一档；**两腿之间、刀和身体之间、铁链和身体之间空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断（铁链、刀尖也要描边）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的俄洛伊、德莱厄斯、奎桑提，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（刀光、冲刺残影、冲击波都不画）。

## 附图（压缩包 `ambessa_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` / `1_picture_SA.png` | 第 0 步你画的两张原稿：**样子和颜色全照它们**（比例不照） |
| `2_target_A.png` / `2_target_SA.png` | 头放大到三分之一、缩到 84 格：**只看大小、位置、姿势、头的比例**，细节是坏的 |
| `3_layout_A.png` / `3_layout_SA.png` | 带网格和三条线（橙 = 发顶，蓝 = 她的眼睛，红 = 脚底） |
| `4_head.png` | 读回的她的头（8 倍）：位置和颜色 |
| `style/5_style_illaoi.png` `6_style_darius.png` `7_style_ksante.png` | **只看风格** |

## 提示词 A（A-1、A-2 各画一次，同一段；附 1_picture_A、2_target_A、3_layout_A、4_head、style 三张）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP - not its proportions), 2 the same picture made CHIBI (the head blown up to a third of the height) and cut down to the target square count (ONLY its size, place, pose and the head's share are right - its details are broken), 3 the layout with the grid and three lines (orange = the top of her hair, blue = her eyes, red = her soles), 4 her head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as CHIBI GAME-SIZE PIXEL ART like a pixel artist, in the proportions of image 2: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 13 px, aligned on one grid starting at the canvas corner (0, 0). THE TALL, POWERFUL WARLORD WOMAN at rest in 3/4 view facing right, exactly the pose of images 1-2: standing firm, feet apart, a hooked crescent blade hanging from each hand (the near one on the image left, the far one on the image right), chains between her hands and the blades; the top of her hair at y 117, her eyes at about y 325, her soles on y 1209 - 84 squares tall, about 82 squares wide (never more than 84). Every detail in whole 13-px squares - never smaller squares.
HER FACE (most important): CHIBI - a BIG HEAD (hair and face about a third of her height, as in image 2); DARK BROWN SKIN in 3 shades (warm orange-brown lit), turned to the front-right, the chin a little up, a stern look; TWO EYES at the SAME height and of the SAME size, each 2x2 squares (dark, with one red-brown iris square and one light highlight square); 1-square low fierce brows; DARK RED LIPS 2 squares wide; high cheekbones; one GOLD earring square.
HER HAIR: SILVER-WHITE, SHORT, WAVY and SWEPT BACK (3 shades: white, light grey, grey-violet shadow), heaped on top and behind, never over the eyes.
THE MANTLE: SPIKY DARK TEAL-GREEN FUR round her shoulders (3 shades: bright teal, teal, dark green), the big tuft on the near shoulder the clearest, outlined apart from the hair and the skin.
THE ARMOUR: a BLACK IRON breastplate (3 shades: near-black, dark grey, a light grey edge square) with 1-square BRONZE seams (2 shades); a DEEP RED SCARF round the collar and a RED SASH hanging from the waist below the knees (3 shades); bare MUSCULAR upper arms of dark brown skin; huge ANGULAR BLACK GAUNTLETS (3 shades and a light edge); black iron leg plates and black boots (2-3 shades). The black armour must NOT read as one smear: every plate separated by its lighter edge and its darker shadow.
THE TWO DRAKEHOUND BLADES: each a HOOKED CRESCENT with long sharp horns, a BRIGHT SILVER outer edge (2 shades and a white highlight square), a DARK FLAT inner plate, TRIANGULAR HOLES through it showing the background; THICK IRON CHAINS (dark iron in 2 shades, links of 1-2 squares) from the handles to her hands, hanging in a loop.
The near leg (image left) in full tone, the far one a step darker; the background visible between the legs, between the blades and the body and between the chains and the body.
A continuous 1-square near-black outline round the whole character (the chains and the blade horns too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects (no blade trails, no afterimages, no shockwaves).
```

## 提示词 SA（SA-1、SA-2 各画一次，同一段；附 1_picture_SA、2_target_SA、3_layout_SA、4_head、style 三张）

```text
Attached: 1 the character's approved side picture (THE LOOK AND COLOURS TO KEEP - not its proportions), 2 the same picture made CHIBI (the head blown up to a third of the height) and cut down to the target square count (ONLY its size, place, pose and the head's share are right - its details are broken), 3 the layout with the grid and three lines (orange = the top of her hair, blue = her eyes, red = her soles), 4 her head read back 8x (from the 3/4 view: the colours), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as CHIBI GAME-SIZE PIXEL ART like a pixel artist, in the proportions of image 2: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 13 px, aligned on one grid starting at the canvas corner (0, 0). THE SAME WARLORD WOMAN seen exactly from the SIDE, FACING RIGHT, exactly the pose of images 1-2: the face, the chest and the toes pointing right, the near blade in front of her body to the right, the far blade a step darker behind her to the left, chains between her hands and the blades; the top of her hair at y 117, her eye at about y 312, her soles on y 1209 - 84 squares tall, about 66 squares wide. Every detail in whole 13-px squares - never smaller squares.
HER FACE (most important): the SAME chibi head as in the 3/4 view - BIG (hair and face about a third of her height); DARK BROWN SKIN in 3 shades; in profile: ONE EYE 2x2 squares (dark, a red-brown iris square, a highlight), a 1-square fierce brow, the nose and the chin pointing right, DARK RED LIPS, one GOLD earring square.
HER HAIR: SILVER-WHITE, SHORT, WAVY, SWEPT BACK (3 shades), heaped behind her head.
THE MANTLE: SPIKY DARK TEAL-GREEN FUR on her shoulder (3 shades), outlined apart from the hair and the skin.
THE ARMOUR: the BLACK IRON breastplate seen from the side (3 shades and a light edge) with 1-square BRONZE seams; the DEEP RED SCARF at the collar and the RED SASH hanging down (3 shades); a bare MUSCULAR upper arm of dark brown skin; the huge ANGULAR BLACK GAUNTLET; black leg plates and boots. Every plate separated by its lighter edge and its darker shadow - never one black smear.
THE TWO DRAKEHOUND BLADES: HOOKED CRESCENTS with long sharp horns, BRIGHT SILVER outer edges (2 shades and a white highlight), DARK FLAT inner plates with TRIANGULAR HOLES showing the background; THICK IRON CHAINS (2 shades, links of 1-2 squares) hanging in loops.
The near leg in full tone, the far one a step darker; the background visible between the legs, between the blades and the body.
A continuous 1-square near-black outline round the whole character (the chains and the horns too); inside it every material in its own 2-4 flat shades; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects.
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**A、SA 都是每格 13 px**，对齐从 (0, 0) 开始的网格；发顶 y 117、脚底 y 1209（84 格）。
- **Q 版**：头（连头发）约占身高的三分之一，和 `2_target` 一样；**A 两只眼睛一样高、各 2×2**、深红嘴唇、金耳环；银白波浪短发不遮眼睛。**A 和 SA 是同一个头**。
- 青绿尖毛领、黑铁胸甲 + 铜色接缝、红围巾 + 红腰布、黑色大护臂、粗壮的上臂；**黑甲分得清一块块**，不糊。
- 两把**带钩的月牙形龙犬刃**：亮银刃边、深色刃身、**三角镂空看得见背景**；粗铁链。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/ambessa-model/ambessa-A-1.png`、`ambessa-A-2.png`、`ambessa-SA-1.png`、`ambessa-SA-2.png`；原始生成图原样放进 `outputs/ambessa-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/ambessa-model/HANDOFF.md`，再打包成 `outputs/ambessa_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/ambessa/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；Codex 常画得比要求的粗或细，按它自己的格子读回），裁到 84 行（keep_axis、脸框保留，`design_sejuani_model.py` 的做法），12 倍下看脸（两眼一样高、嘴唇、头发不遮眼）和黑甲分不分得开，给用户挑稿 -> `hd/idle.png`（A，PPU 1.75，发顶到脚底 48 游戏像素）、`hd/side.png`（SA，同一比例）。两张挑中的稿子头要统一成一个（挑定后以 A 的头为准）。
- 然后第 2 步：照英雄联盟的动作出姿势包（`pack_ambessa_poses.py`，参考克烈 / 约里克）：待机、跑、普攻、Q 横扫、Q2 裂地重击、E 抡铁链、W 交叉格挡和砸地、R 闪现按住和砸下、龙犬之步的冲刺（`step`）、受击、死亡。
