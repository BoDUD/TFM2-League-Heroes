# 炼金术士 辛吉德：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的 3/4 待机原稿（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 这一步要画成**游戏里的格子数**：**从药罐的盖子顶到脚底 66 格**（其中光头顶到脚底 54 格）。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、夹克和盾板碎成杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 7.5–8 px 一格，整个角色约 105 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**每格 16 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（A-1 / A-2），都是 3/4 正面朝右。**不画侧面**。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（辛吉德 3/4，朝右）**：每格 **16 px**；照 `2_target_A.png` / `3_layout_A.png`：药罐盖子顶 **y = 128**（橙线），眼睛约 **y = 416**（蓝线），脚底 **y = 1184**（红线）：**66 格高、约 50 格宽**（盾板和拿药瓶的手算在宽里）。
- 全在画布里，药罐、盾板、靴子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的头（8 倍），看位置和颜色——**远处那只眼睛在那里几乎看不见了，这一步一定要画出来**。

- **脸**（最要紧）：光头约 **9–10 格宽**，苍白偏粉 3 档，头顶一块 2–3 格的亮高光，暗面偏紫灰；**两只眼睛一样高、都露出来**：近处（画面左）的眼睛 **2 × 2 格**，**近白的灰色眼珠**（发白的那只）加 1 格深色眼窝；远处（画面右）的眼睛 **2 格宽 × 1–2 格高**，小黑瞳孔，也要清楚；眉头一道深色皱着；**鼻子以下全被灰绿蒙脸布盖住**（3 档，1–2 道深色褶），蒙脸布上缘一条清楚的边；小尖耳朵 1–2 格在画面左侧。
- **药罐**：在他远侧肩膀后面往上冒，**圆滚滚的荧光亮绿**（4 档，亮面带黄，**少而大的整块高光**），一圈 4–5 颗深灰铆钉（每颗 1 格），**顶上深灰金属盖**（2–3 档，约 4 × 3 格）；药罐和头之间一格描边分开。
- **盾板**：在近侧（画面左）竖着，**灰绿金属 3 档**，几颗 1 格铆钉，**左边缘 3–4 根银灰尖刺**（每根 2–3 格长的三角形），中间一条木杆；**不挡脸**，只挡住近侧手臂和一点身体。
- **上身**：**红夹克**（3–4 档）+ **两条金色扣带**交叉在胸前（金黄 3 档，方扣用 2 × 2 格带深色中心）；**两个带刺的大护肩**（红底金边，各 1–2 根银灰刺）；脖子上**灰蓝围巾**（3 档），挡住脖子。
- **远侧的手**：又长又瘦，暗红棕手套，握着**圆圆的亮绿药瓶**（约 4 × 4 格，1 格高光，瓶口深灰）。近侧的手在盾板后面露出几根指头。
- **腰和腿**：棕色皮带 + 2–3 根小绿药管，下面一圈破布条（2–3 条尖的布片）；**深蓝细长腿**（3 档）；**大红棕靴子**（3 档，靴口一圈 2–3 根银灰尖刺，金色带扣），**两只脚分开踩在地面线上**；近的腿（画面左）全亮，远的（画面右）暗一档；**两腿中间、腋下空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的蒙多医生、厄加特、普朗克，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、毒雾、技能特效。

## 附图（压缩包 `singed_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` | 第 0 步你画的待机原稿：**样子和颜色全照它** |
| `2_target_A.png` | 直接缩到 66 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_A.png` | 带网格和三条线（橙 = 药罐顶，蓝 = 眼睛，红 = 地面） |
| `4_head.png` | 读回的头（8 倍）：位置和颜色；远眼要补画 |
| `style/5_style_drmundo.png` `6_style_urgot.png` `7_style_gangplank.png` | **只看风格** |

## 提示词（A-1、A-2 各画一次，同一段）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = top of the tank cap, blue = the eyes, red = the ground), 4 his head read back 8x (where things are; the far eye is lost there and must be drawn), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 16 px, aligned on one grid starting at the canvas corner (0, 0). THE MAD CHEMIST in 3/4 view facing right, exactly the pose of images 1-2: the top of the tank cap at y 128, the eyes at about y 416, the soles on y 1184 - 66 squares tall (54 from the top of his bald head to the soles), about 50 squares wide. Every detail in whole 16-px squares - never smaller squares.
THE FACE (most important): a bald head about 9-10 squares wide, pale pink in 3 shades with a 2-3 square highlight on the scalp, purplish grey in the shadows; BOTH EYES at the same height and both clearly visible: the near eye (image left) 2x2 squares, a MILKY near-white grey eyeball with a dark socket square; the far eye (image right) 2 squares wide, a small dark pupil, clearly drawn; a dark frowning brow; everything below the nose under a GREY-GREEN CLOTH MASK (3 shades, 1-2 dark folds, a clear top edge); a small pointed ear on the image left.
THE TANK: rising behind his far shoulder, round and bulging, GLOWING BRIGHT GREEN in 4 shades (the light side a little yellow, FEW LARGE flat highlight blocks), a ring of 4-5 dark grey one-square rivets, a dark grey metal cap on top (about 4x3 squares); one outline square between the tank and the head.
THE SHIELD PLATE: standing on his near side (image left), grey-green metal in 3 shades, a few one-square rivets, 3-4 silver-grey spikes on its left edge (triangles 2-3 squares long), a wooden pole down its middle; it never covers the face, only his near arm and a little of the body.
THE BODY: a RED JACKET in 3-4 shades with TWO GOLD STRAPS crossing the chest (gold in 3, square buckles of 2x2 with a dark centre); two big SPIKED SHOULDER PADS (red with gold rims, 1-2 silver spikes each); a GREY-BLUE SCARF round the neck; the far hand long and thin in a dark red-brown glove holding a ROUND BRIGHT GREEN FLASK (about 4x4 squares, one highlight square, a dark grey neck); the near hand's fingers showing behind the shield; a brown belt with 2-3 little green vials and torn cloth strips below it; THIN DARK BLUE legs in 3 shades; BIG RED-BROWN BOOTS in 3 shades with silver spikes round the cuffs and gold buckles, the two feet apart on the ground line; the near leg (image left) in full tone, the far one a step darker; the background visible between the legs and under the arms.
A continuous 1-square near-black outline round him; inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no poison cloud, no spell effects.
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**每格 16 px**，对齐从 (0, 0) 开始的网格；药罐顶 y 128、脚底 y 1184（66 格）。
- **两只眼睛都看得见、一样高**（近的发白，远的有小黑瞳孔）；蒙脸布盖住鼻子以下；光头有高光。
- 药罐亮绿圆滚、铆钉和盖子清楚；盾板在近侧不挡脸、有尖刺；红夹克 + 金扣带 + 带刺护肩 + 灰蓝围巾；绿药瓶；深蓝细腿 + 大红棕带刺靴子，两脚分开站在地面线上。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/singed-model/singed-A-1.png`、`singed-A-2.png`；原始生成图原样放进 `outputs/singed-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/singed-model/HANDOFF.md`，再打包成 `outputs/singed_model_done.zip`。中间不要停，两稿都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/singed/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw），按它的格子读回，裁到 66 行（keep_axis、脸框保留，`design_zac_model.py` 的做法），12 倍下看脸（两只眼睛、蒙脸布上缘），给用户挑稿 -> `hd/idle.png`。
