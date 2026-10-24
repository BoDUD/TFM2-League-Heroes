# 北地之怒 瑟庄妮：第 1 步补画，同样的造型画得更细（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把图平滑放大或缩小**。
> - 上一步你画的 **A-2（待机）和 B-1（冲锋）用户选中了**（`1_picture_A.png`、`1_picture_B.png`）：**样子、颜色、人和野猪的比例、姿势全照它们，一点都不要改**。
> - 用户要更高的像素密度：**同样大小的角色，格子再细一些**。上一步每格约 18 px（A 53 格高）；这一步 **每格 14 px**：**A 从冰角尖到蹄子底 72 格**，**B 同一个比例，从扬起的链枷顶到最低的獠牙 / 蹄子 76 格**。
> - `2_target_A.png`、`2_target_B.png` 是我把选中的两张放到这个格子数：**大小、位置对，但边缘是一格一格硬放大的，很粗糙**。请像一个像素画师照着 `1_picture` 在 14 px 的格子上**重新画一遍**：多出来的格子用来把细节画清楚（脸、头盔的纹路、宝石、毛领、鬃毛、獠牙、蹄子），不是把原图放大。
> - 一共画**四张**：A-1 / A-2（待机，两稿），B-1 / B-2（冲锋，两稿），都是 3/4 正面朝右。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。**每格 14 px**。
- **A（待机）**：照 `2_target_A.png` / `3_layout_A.png`：冰角尖 **y = 182**（橙线），她的眼睛约 **y = 406**（蓝线），蹄子底 **y = 1190**（红线）：**72 格高、约 82 格宽**。
- **B（冲锋）**：照 `2_target_B.png` / `3_layout_B.png`：链枷顶 **y = 126**（橙线），她的眼睛约 **y = 448**（蓝线），最低处 **y = 1190**（红线）：**76 格高、约 86 格宽**（冰锤头离画布左边只有 1 格，**不要出画**）。
- 全在画布里，冰角、链枷、獠牙、尾巴不出画。

## 一定要画清楚的地方

- **她的脸**（最要紧，上一稿太糊，用户看不清）：`4_face_A.png`、`4_face_B.png` 是我在上一稿上补好的脸（12 倍），**照它的位置**：**两只冰蓝色眼睛一样高**——近处的眼睛 **3 × 2 格**（一格白高光、亮蓝、深蓝），远处的眼睛 **2 × 2 格**；眼睛上面各一道深棕色的眉毛（1 格高）；**粉色的小嘴** 2 格；皮肤 3 档（亮的在额头和脸颊、暗的在下巴和侧脸）；两缕浅金色头发在脸两侧，**不挡眼睛**。
- **头盔**：青铜金 3–4 档，额前蓝色冰宝石（3 × 3 格带一格白高光）；两只**蓝色冰角**往后弯（近的大、远的小），冰角 3 档蓝 + 一条亮边。
- **铠甲和毛领**：紫色皮甲 3 档；青铜金尖肩甲上的**亮蓝宝石**（每颗 2–3 格、带白高光）；**米白毛领**一簇簇的尖。
- **链枷**：棕黑相间的链子（2 格粗，棕黑交替）+ 蓝色大冰锤头（3 档蓝 + 1 格青色亮纹）。
- **钢鬃**：灰蓝毛 4 档（毛边用暗一档的锯齿）；**白鬃毛**一簇簇竖起；**两根象牙色大獠牙**（3 档、轮廓清楚）；粉鼻子 + 两个暗粉鼻孔；张开的粉嘴和白牙；**一只青蓝发光的眼睛**（2 × 2 格，最亮一格接近白）；粉耳朵；深灰分瓣的蹄子；橄榄绿鞍甲 + 两块大蓝宝石；棕色皮带。
- 近的腿全亮、远的腿暗一档；腿和腿之间、链子和身体之间空出来看得见背景。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的努努和威朗普、沃利贝尔、布隆，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `sejuani_redraw_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` / `1_picture_B.png` | 用户选中的上一稿（A-2、B-1）：**样子、颜色、比例、姿势全照它们** |
| `2_target_A.png` / `2_target_B.png` | 放到 72 / 76 格：**只看大小和位置**，边缘粗糙 |
| `3_layout_A.png` / `3_layout_B.png` | 带网格和三条线（橙 = 顶，蓝 = 她的眼睛，红 = 地面） |
| `4_face_A.png` / `4_face_B.png` | 补好的脸（12 倍）：两只眼睛、眉毛、嘴的位置 |
| `style/5_style_nunu.png` `6_style_volibear.png` `7_style_braum.png` | **只看风格** |

## 提示词 A（A-1、A-2 各画一次；附 1_picture_A、2_target_A、3_layout_A、4_face_A、style 三张）

```text
Attached: 1 THE APPROVED PICTURE - the look, the colours, the rider-to-boar proportions and the pose to keep exactly; 2 the same picture brought to the new square count (ONLY its size and place are right - its edges are blocky), 3 the layout with the grid and three lines (orange = the tip of her ice horn, blue = her eyes, red = the hooves), 4 her face 12x (where both eyes, the brows and the mouth go), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 FINER as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 14 px, aligned on one grid starting at the canvas corner (0, 0). The SAME warrior woman on her war boar at rest in 3/4 view facing right, the SAME pose and proportions as image 1: the tip of her ice horn at y 182, her eyes at about y 406, the hooves on y 1190 - 72 squares tall, about 82 squares wide. Use the extra squares for clearer details, not for a different design. Every detail in whole 14-px squares.
HER FACE (most important): a pale face in 3 shades turned to the front-right; TWO ICE-BLUE EYES at the SAME height: the near eye 3x2 squares (a white highlight, bright blue, deep blue), the far eye 2x2; a 1-square dark brown brow over each eye; a small 2-square PINK mouth; two pale blonde locks beside the face, never over the eyes.
THE HELM: bronze-gold in 3-4 shades with a BLUE ICE GEM on the brow (3x3 squares, a white highlight); two CURVED BLUE ICE HORNS sweeping back (the near one big, the far one smaller; 3 blues with a light edge).
THE ARMOUR: purple leather in 3 shades; pointed bronze-gold shoulder plates set with BRIGHT BLUE GEMS (2-3 squares each, highlighted); CREAM-WHITE FUR in pointed tufts at the collar.
THE FLAIL: a BROWN-AND-BLACK WRAPPED CHAIN (2 squares thick, alternating) hanging down to a BIG BLUE ICE HEAD behind the boar's rump (3 blues with a 1-square cyan glowing line).
THE BOAR: BLUE-GREY FUR in 4 shades (jagged darker edges for the tufts); the WHITE BRISTLY MANE crest in pointed tufts; TWO BIG IVORY TUSKS curving up (3 shades, clear outlines); a PINK SNOUT with two dark pink nostrils; a pink open mouth with white teeth; one GLOWING CYAN EYE (2x2, the brightest almost white); pink inner ears; DARK GREY split HOOVES; OLIVE-GREEN / BRONZE SADDLE ARMOUR with two BIG BLUE GEMS; BROWN straps. The near legs in full tone, the far ones a step darker; the background visible between the legs and between the chain and the body.
A continuous 1-square near-black outline round the whole character; inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects.
```

## 提示词 B（B-1、B-2 各画一次；附 1_picture_B、2_target_B、3_layout_B、4_face_B、style 三张）

```text
Attached: 1 THE APPROVED CHARGING PICTURE - the look, the colours, the rider-to-boar proportions and the pose to keep exactly; 2 the same picture brought to the new square count (ONLY its size and place are right - its edges are blocky), 3 the layout with the grid and three lines (orange = the top of the raised flail, blue = her eyes, red = the lowest tusk / hoof), 4 her face 12x (where both eyes, the brows and the mouth go), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 FINER as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 14 px, aligned on one grid starting at the canvas corner (0, 0). The SAME warrior woman on her war boar CHARGING to the image right in 3/4 view, the SAME pose and proportions as image 1: the boar lunging forward, front legs tucked, tusks thrust ahead; the woman crouching low over the saddle, the flail raised high behind her, its ice head up on the image left (keep it inside the picture, one square from the left edge); the top of the raised flail at y 126, her eyes at about y 448, the lowest tusk / hoof on y 1190 - 76 squares tall, about 86 squares wide. Use the extra squares for clearer details, not for a different design. Every detail in whole 14-px squares.
HER FACE (most important): a pale face in 3 shades turned to the front-right; TWO ICE-BLUE EYES at the SAME height: the near eye 3x2 squares (a white highlight, bright blue, deep blue), the far eye 2x2; a 1-square dark brown brow over each eye; a small 2-square PINK mouth; the blonde locks never over the eyes.
THE HELM: bronze-gold in 3-4 shades with a BLUE ICE GEM on the brow (3x3, highlighted) and two CURVED BLUE ICE HORNS sweeping back.
THE ARMOUR: purple leather in 3 shades; pointed bronze-gold plates with BRIGHT BLUE GEMS (2-3 squares each); CREAM-WHITE FUR tufts at the collar.
THE FLAIL: the BROWN-AND-BLACK WRAPPED CHAIN (2 squares thick, alternating) up behind her, the BIG BLUE ICE HEAD at its end (3 blues, a 1-square cyan glowing line).
THE BOAR: BLUE-GREY FUR in 4 shades; the WHITE BRISTLY MANE crest swept back; TWO BIG IVORY TUSKS thrust forward and up (3 shades); the PINK SNOUT with dark pink nostrils and a pink open mouth with white teeth; one GLOWING CYAN EYE (2x2); pink inner ears; DARK GREY split HOOVES; OLIVE-GREEN / BRONZE SADDLE ARMOUR with two BIG BLUE GEMS; BROWN straps; the tail flying back. The near legs in full tone, the far ones a step darker; the background visible between the legs.
A continuous 1-square near-black outline round the whole character; inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects.
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**每格 14 px**，对齐从 (0, 0) 开始的网格；A 冰角尖 y 182、蹄子底 y 1190（72 格）；B 链枷顶 y 126、最低处 y 1190（76 格）。
- **和上一稿 A-2 / B-1 是同一个造型**：颜色、人和野猪的比例、姿势都没变，只是格子更细、细节更清楚。
- **她的脸清楚**：两只冰蓝眼睛一样高（近眼 3×2 带白高光、远眼 2×2）、眉毛、粉色小嘴；头发不挡眼睛。
- 钢鬃：两根象牙色大獠牙、粉鼻子、发光的青蓝眼睛、白鬃毛、灰蓝毛、深灰蹄子。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/sejuani-redraw/sejuani-A-1.png`、`sejuani-A-2.png`、`sejuani-B-1.png`、`sejuani-B-2.png`；原始生成图原样放进 `outputs/sejuani-redraw/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/sejuani-redraw/HANDOFF.md`，再打包成 `outputs/sejuani_redraw_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sejuani/codex_redraw/`，在 8 倍下量 Codex 实际的格子（读 raw），A 裁到 72 行、B 裁到 76 行（`design_sejuani_model.py` 的做法：keep_axis、脸框保留），12 倍下看脸，给用户挑稿 -> `hd/idle.png`（A，PPU 2.0，冰角尖到蹄子 36 游戏像素）、`hd/run.png`（B，同一比例）。
