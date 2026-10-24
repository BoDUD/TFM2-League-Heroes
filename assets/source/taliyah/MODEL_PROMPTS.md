# 岩雀 塔莉垭：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的 A 站立待机原稿（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 这一步要画成**游戏里的格子数**：**从头发顶到脚底 70 格**。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、披肩的石片和外套的金边碎成杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 9.8 px 一格，整个角色约 110 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**每格 16 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（A-1 / A-2），都是 3/4 正面朝右。**不画冲浪（B）**，后面再用。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（塔莉垭 3/4，朝右）**：每格 **16 px**；照 `2_target_A.png` / `3_layout_A.png`：头发顶 **y = 64**（橙线），眼睛约 **y = 368**（蓝线），脚底 **y = 1184**（红线）：**70 格高、约 34 格宽**（两条垂带和末端的石头算在宽里）。
- 全在画布里，头发、垂带、靴子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的头（8 倍），看位置和颜色。

- **脸**（最要紧）：小麦色皮肤 3 档，脸约 **8–9 格宽**；**两只眼睛一样高、都露出来**：近处（画面左）的眼睛 **2 格宽 × 2–3 格高**，一格白眼白 + **琥珀 / 深棕色眼珠** + 1 格黑色上眼线；远处（画面右）的眼睛 **2 格宽 × 2 格高**，同样颜色，**也要清楚**（不能只剩一条线）；浓一点的深棕眉毛各 2–3 格；小鼻子 1 格暗肤色；**嘴 1–2 格暗红**；下巴尖。
- **头发**：一大团往上盘起的**棕色大头发**（3–4 档：深棕描边、中棕、亮棕高光成块），发尾往上、往后一簇簇翘起（每簇 3–5 格的尖角）；额前几缕刘海压在眉毛上方，**不挡眼睛**；脸两侧各垂一缕头发到下巴。
- **发饰**：头发正前方偏右一个**金色的圆形发饰**（金黄 2–3 档，约 5 × 4 格），中间一颗**奶白色的圆石头**（2 档 + 1 格高光，约 3 × 3 格）。
- **披肩**：两肩上**米白 / 沙色的石片披肩**（3 档），一片片石片用最暗一档的格子分开，像叠起来的羽毛；领子立在下巴两侧，**不挡脸**；披肩宽过肩膀。
- **上身和腿**：**深靛紫色长上衣**（3 档），胸前和腰上**金色的边线**（金黄 2 档，1 格宽）组成 V 形和一圈腰带；**红色长外套**（3 档）+ 1 格金边，从披肩下面垂下；**两条红色垂带**垂到小腿外侧，**末端各挂 3–4 块灰色石头**（灰 3 档，每块 2–3 格）；**紫色袖子 + 米白护腕**（各 2 档），手是小麦色、手指微微张开，在身体两侧；**深靛紫紧身裤**；**棕色长靴**（3 档，靴口翻边），两只脚分开踩在地面线上。
- 近的腿和垂带（画面左）全亮，远的（画面右）暗一档；**两腿中间、手臂和身体之间空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的奇亚娜、佐伊、阿萝拉，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、飞石、技能特效。

## 附图（压缩包 `taliyah_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` | 第 0 步你画的站立原稿：**样子和颜色全照它** |
| `2_target_A.png` | 直接缩到 70 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_A.png` | 带网格和三条线（橙 = 头发顶，蓝 = 眼睛，红 = 地面） |
| `4_head.png` | 读回的头（8 倍）：位置和颜色 |
| `style/5_style_qiyana.png` `6_style_zoe.png` `7_style_aurora.png` | **只看风格** |

## 提示词（A-1、A-2 各画一次，同一段）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = top of the hair, blue = the eyes, red = the ground), 4 her head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 16 px, aligned on one grid starting at the canvas corner (0, 0). THE STONEWEAVER GIRL standing in 3/4 view facing right, exactly the pose of images 1-2: the top of her hair at y 64, the eyes at about y 368, the soles on y 1184 - 70 squares tall, about 34 squares wide. Every detail in whole 16-px squares - never smaller squares.
THE FACE (most important): tanned skin in 3 shades, the face about 8-9 squares wide; BOTH EYES at the same height and both clearly visible: the near eye (image left) 2 squares wide and 2-3 tall, one white square, an AMBER / DARK BROWN iris and a one-square black upper lash line; the far eye (image right) 2x2 squares, the same colours, clearly drawn (never just a line); thick dark brown eyebrows of 2-3 squares; a one-square nose in dark skin; a 1-2 square dark red mouth; a pointed chin.
THE HAIR: a BIG SWEPT-UP MASS OF BROWN HAIR piled high (3-4 shades: a dark brown edge, mid brown, light brown highlights in blocks), its ends curling up and back in tufts (pointed tips of 3-5 squares); a few locks of fringe above the brows, never covering the eyes; one lock down each side of the face to the chin. A ROUND GOLD ORNAMENT at the front of the hair, a little right of centre (gold in 2-3 shades, about 5x4 squares) with a CREAM ROUND STONE in its middle (2 shades and one highlight square, about 3x3).
THE MANTLE: a CREAM / SAND STONE-PLATE MANTLE over both shoulders (3 shades), the plates parted by its darkest shade like overlapping feathers, the collar standing up beside the chin without covering the face, wider than the shoulders.
THE BODY: a long DARK INDIGO-PURPLE TUNIC (3 shades) with one-square GOLD lines making a V on the chest and a belt at the waist; a long RED COAT (3 shades) with a one-square gold edge hanging from under the mantle; TWO LONG RED PANELS hanging to the outer shins, each ending in 3-4 GREY STONES (grey in 3, 2-3 squares each); PURPLE SLEEVES with CREAM CUFFS (2 shades each), tanned hands with the fingers a little spread at her sides; dark indigo leggings; BROWN BOOTS in 3 shades with turned-down cuffs, the two feet apart on the ground line; the near leg and panel (image left) in full tone, the far ones a step darker; the background visible between the legs and between the arms and the body.
A continuous 1-square near-black outline round her; inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no flying rocks, no spell effects.
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**每格 16 px**，对齐从 (0, 0) 开始的网格；头发顶 y 64、脚底 y 1184（70 格）。
- **两只眼睛都看得见、一样高**（琥珀 / 深棕眼珠、白眼白、黑眼线）；眉毛、小嘴清楚；刘海不挡眼睛。
- 棕色大盘发 + 金色发饰和奶白石头；米白石片披肩不挡脸；深靛紫上衣 + 金边；红外套 + 两条挂灰石头的垂带；紫袖子米白护腕；棕色靴子，两脚分开站在地面线上。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/taliyah-model/taliyah-A-1.png`、`taliyah-A-2.png`；原始生成图原样放进 `outputs/taliyah-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/taliyah-model/HANDOFF.md`，再打包成 `outputs/taliyah_model_done.zip`。中间不要停，两稿都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/taliyah/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；Codex 常画得比 16 px 粗或带半格细节，阿萝拉那次按它的细格读），按它的格子读回，裁到 70 行（keep_axis、脸框保留，`design_zac_model.py` 的做法），12 倍下看脸（两只眼睛、眉毛、嘴），给用户挑稿 -> `hd/idle.png`（PPU 1.75，头发顶到鞋底 40 游戏像素）。
