# 虚空女皇 卑尔维斯：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的 A（收翼待机，`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 这一步要画成**游戏里的格子数**：**从肩刺尖到最低的爪尖 82 格**（其中头顶到爪尖 70 格）。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、眼睛只剩 1 格、翼膜的纹路碎成杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子约 9.8 px 一格（整个角色约 91 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**每格 14 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（A-1 / A-2），都是 3/4 正面朝右，收翼。**不画张翼、不画侧面**。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（卑尔维斯 3/4，朝右，收翼）**：每格 **14 px**；照 `2_target_A.png` / `3_layout_A.png`：肩刺尖 **y = 42**（橙线），眼睛约 **y = 322**（蓝线），爪尖 **y = 1190**（红线）：**82 格高、约 82 格宽**（左边拖在地上的尾巴算在宽里）。
- 全在画布里，肩刺、尾巴、爪子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的头（8 倍），看位置和颜色——**眼睛在那里只剩 1 格，这一步一定要画大、画清楚**。

- **脸**（最要紧）：深紫色的脸约 **8–9 格宽**（3 档，亮面偏紫蓝），脸尖、下巴尖；**两只眼睛一样高、都露出来**，每只 **2 × 2 格**：**发光的品红色**，各带 **1 格粉白高光**，没有瞳孔；近处（画面左）的眼睛和远处（画面右）的眼睛中间隔 2 格；眉骨一道深色；头顶**品红色的冠**往后扫（3 档，约 4–5 格宽，冠上 1 格小黄点）；冠后面那块**金黄色的饰片**照第 0 步保留。脸和两边的高领 / 肩刺之间一格描边分开，**肩刺和高领都不挡脸**。
- **肩刺**：两根又高又尖的**深紫色长刺**从两肩竖起（3 档，亮边偏品红），刺尖比头顶高约 12 格；近的（画面左）亮一档。
- **上身**：深紫黑的高领甲壳（3–4 档）；胸口中间**灰青 / 象牙色的尖刺花饰**（约 4 × 4 格，3 档，像扇子张开）；花饰两边两块**淡紫色的弯钩甲片**；两肩各一颗**发光的品红圆珠**（约 2 × 2 格，1 格高光）；近侧肩头那块**金黄色的饰片**照第 0 步保留。
- **收拢的膜翼**：两只膜翼**垂下裹住身体像长斗篷**：翼膜**深灰青**（3 档，几道清楚的深色翼骨线，**少而大的整块**，不要碎斑），下摆裂成几片尖角；近侧（画面左）的翼亮一档，画面左边露出一截翼尖（深青 + 品红边）；远侧（画面右）暗一档。
- **下身和爪子**：斗篷形躯体下面**4–5 根粉紫色的弯爪**撑在地面线上（3 档，最亮接近粉白，每根 2–3 格宽、尖朝下），爪子之间看得见背景；**长尾巴**从画面左下拖出去平放在地上（上面深紫黑，**下面一面品红**），尾尖在画面最左。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的卡莎、卡萨丁、维克兹，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明（第 0 步的图几乎每个像素都是 253，这一步不行）。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `belveth_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` | 第 0 步你画的 A（收翼）原稿：**样子和颜色全照它** |
| `2_target_A.png` | 直接缩到 82 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_A.png` | 带网格和三条线（橙 = 肩刺尖，蓝 = 眼睛，红 = 地面） |
| `4_head.png` | 读回的头（8 倍）：位置和颜色；眼睛要画大 |
| `style/5_style_kaisa.png` `6_style_kassadin.png` `7_style_velkoz.png` | **只看风格** |

## 提示词（A-1、A-2 各画一次，同一段）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = the shoulder-spike tips, blue = the eyes, red = the ground), 4 her head read back 8x (where things are; the eyes shrank to one square there and must be drawn bigger), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 14 px, aligned on one grid starting at the canvas corner (0, 0). THE VOID EMPRESS in 3/4 view facing right, her wing-arms FOLDED DOWN like a long cloak, exactly the pose of images 1-2: the shoulder-spike tips at y 42, the eyes at about y 322, the lowest claw tips on y 1190 - 82 squares tall (70 from the top of her head to the claws), about 82 squares wide with the tail. Every detail in whole 14-px squares - never smaller squares.
THE FACE (most important): a dark violet face about 8-9 squares wide in 3 shades, sharp with a pointed chin; BOTH EYES at the same height and both clearly visible, each 2x2 squares, GLOWING MAGENTA with one pink-white highlight square each, no pupils, two squares apart; a dark brow line; a MAGENTA CREST sweeping back over the head (3 shades, about 4-5 squares wide, one small yellow square on it) and the GOLD-YELLOW ornament behind it as in image 1; one outline square between the face and the high collar and spikes - the spikes and the collar NEVER cover the face.
THE SHOULDER SPIKES: two tall sharp DARK PURPLE spikes rising from her shoulders (3 shades, the lit edge towards magenta), their tips about 12 squares above the head top; the near one (image left) a step lighter.
THE CHEST: a high dark plum-black carapace collar (3-4 shades); in the middle a PALE TEAL-IVORY spiky fan ornament (about 4x4 squares, 3 shades); two pale violet hooked plates beside it; a GLOWING MAGENTA ORB on each shoulder (about 2x2 squares, one highlight square); the gold-yellow piece on the near shoulder as in image 1.
THE FOLDED WINGS: both wing membranes hanging down round her body like a long cloak, DARK SLATE-TEAL in 3 shades with a few clear dark wing-bone lines - FEW LARGE flat areas, no speckles - the hem splitting into a few sharp points; the near wing (image left) a step lighter with its tip showing on the image left (teal with a magenta edge); the far wing (image right) a step darker.
BELOW: under the cloak-like body 4-5 curved PINK-MAGENTA CLAWS standing on the ground line (3 shades, the lightest almost pink-white, each 2-3 squares wide, points down), the background visible between them; a LONG TAIL lying flat on the ground out to the image left (dark plum-black on top, MAGENTA on its underside), its tip at the far left.
A continuous 1-square near-black outline round her; inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects.
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**每格 14 px**，对齐从 (0, 0) 开始的网格；肩刺尖 y 42、爪尖 y 1190（82 格）。
- **两只眼睛都看得见、一样高、各 2 × 2 格**（品红 + 粉白高光）；深紫的脸清楚；品红的冠；肩刺和高领不挡脸。
- 两根深紫肩刺；胸口灰青象牙花饰 + 淡紫钩片 + 肩上品红圆珠；收拢的深灰青膜翼像斗篷（大块、不碎）；粉紫爪子着地、爪间透空；长尾巴平放在左边地上，下面品红。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/belveth-model/belveth-A-1.png`、`belveth-A-2.png`；原始生成图原样放进 `outputs/belveth-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/belveth-model/HANDOFF.md`，再打包成 `outputs/belveth_model_done.zip`。中间不要停，两稿都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/belveth/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；辛吉德那次比要求的粗，阿萝拉那次要按它更细的半格读），按它的格子读回，裁到 82 行（keep_axis、脸框保留，`design_singed_model.py` 的做法），12 倍下看脸（两只眼睛、冠），给用户挑稿 -> `hd/idle.png`。
