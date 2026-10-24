# 北地之怒 瑟庄妮：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的两张原稿（`1_picture_A.png` 待机、`1_picture_B.png` 冲锋）**样子、颜色用户认可了，全照它们**。
> - 这一步要画成**游戏里的格子数**：**A 从冰角尖到蹄子底 54 格**，**B 同一个比例，从链枷顶到最低的獠牙 / 蹄子 56 格**。我把图直接缩到这个格子数（`2_target_A.png`、`2_target_B.png`）：**大小、位置、姿势对，细节是缩坏的**（脸只剩几个色块、铠甲的纹路和野猪的毛碎成杂斑）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 5.6 px 一格，A 约 187 格高）：这一步**每格画大**。画布用你平时的 **1254 × 1254**，**A、B 都是每格 18 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**：A-1 / A-2（待机，两稿），B-1 / B-2（冲锋，两稿），都是 3/4 正面朝右。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（待机，3/4 朝右）**：每格 **18 px**；照 `2_target_A.png` / `3_layout_A.png`：冰角尖 **y = 216**（橙线），她的眼睛约 **y = 468**（蓝线），蹄子底 **y = 1188**（红线）：**54 格高、约 60 格宽**（身后的链枷算在宽里）。
- **B（冲锋，3/4 朝右）**：每格 **18 px**；照 `2_target_B.png` / `3_layout_B.png`：扬起的链枷顶 **y = 180**（橙线），她的眼睛约 **y = 486**（蓝线），最低的獠牙 / 蹄子 **y = 1188**（红线）：**56 格高、约 62 格宽**。
- 全在画布里，冰角、链枷、獠牙、尾巴不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的她的头（8 倍），看位置和颜色。

- **瑟庄妮的脸**（最要紧）：Q 版，**头要大**（头盔连脸大约占她坐着身高的一半，比 `2_target` 里大一圈也可以，身子相应小一点）；**白皙的脸**（3 档），朝右前方；**两只冰蓝色的眼睛一样高**：近处的眼睛 **2 × 2 格**（一格亮蓝 + 一格白高光 + 一格深蓝），远处的眼睛 **至少 1 × 2 格**；眉毛 1 格、利落；嘴 1–2 格、抿着（冷峻）；**两缕浅金色头发**垂在脸两侧，不挡眼睛。
- **头盔和冰角**：**青铜金色的头盔**（3 档：暗棕描边、青铜、亮金高光成块），额前一颗**蓝色冰宝石**（2 × 2 格，带一格白高光）；两侧各一只**往后弯的蓝色冰角**（近的那只大，3–4 格粗、尖细的尾端；远的小一点）。
- **身体和铠甲**：**紫色皮甲**（3 档）；**青铜金色的大肩甲**（带尖角）和胸甲，甲片上镶**亮蓝色的冰宝石**（每颗 2 格，带白高光）；领口和肩上一圈**米白色的毛**（2–3 档，一簇簇的尖）；手套靴子深紫。
- **链枷**：她握着一根**棕黑相间缠绕的长链 / 长柄**（1–2 格粗，棕和黑一格一格交替），末端是**蓝色的大冰锤头**（3 档蓝 + 一圈**青色亮纹** 1 格宽）。A：冰锤头垂在钢鬃屁股后面（画面左下）；B：链枷高高扬在身后（画面左上）。
- **钢鬃（野猪）**：**灰蓝色的毛**（4 档，毛边用暗一档的锯齿表示一簇簇）；从头顶到背上一大片**白色竖起的鬃毛**（2–3 档，尖尖的一簇簇）；**两根大獠牙**（象牙色 3 档，各 2–3 格粗、往上弯，**最显眼**）；**粉红色的猪鼻子**（2 档，鼻孔 1 格暗粉）；张开的嘴里粉红、几颗白牙；**一只发青蓝光的眼睛**（2 × 1 格，最亮一格接近白）；**耳朵里面粉红**；**深灰的蹄子**（每只 2–3 格宽、分两瓣）；背上**橄榄绿 / 青铜的鞍甲**（3 档）+ 两块**大蓝宝石**（各 3–4 格，带高光）；**棕色皮带**（1 格宽）；身后一条尾巴，末端一撮毛。
- 近的腿（画面左）全亮，远的腿暗一档、稍高；**腿和腿之间、链子和身体之间空出来看得见背景**。
- **一圈 1 格的近黑外描边**，连续不断（链枷的链子也要描边）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的努努和威朗普、沃利贝尔、布隆，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（冰霜、冰风暴、套索都不画）。

## 附图（压缩包 `sejuani_model_pack.zip`）

| 文件 | 内容 |
|---|---|
| `1_picture_A.png` / `1_picture_B.png` | 第 0 步你画的两张原稿：**样子和颜色全照它们** |
| `2_target_A.png` / `2_target_B.png` | 直接缩到 54 / 56 格：**只看大小、位置、姿势**，细节是坏的 |
| `3_layout_A.png` / `3_layout_B.png` | 带网格和三条线（橙 = 冰角尖 / 链枷顶，蓝 = 她的眼睛，红 = 蹄子底 / 最低的獠牙） |
| `4_head.png` | 读回的她的头（8 倍）：位置和颜色 |
| `style/5_style_nunu.png` `6_style_volibear.png` `7_style_braum.png` | **只看风格** |

## 提示词 A（A-1、A-2 各画一次，同一段；附 1_picture_A、2_target_A、3_layout_A、4_head、style 三张）

```text
Attached: 1 the character's approved picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = the tip of her ice horn, blue = her eyes, red = the hooves), 4 her head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 18 px, aligned on one grid starting at the canvas corner (0, 0). THE WARRIOR WOMAN RIDING HER WAR BOAR at rest in 3/4 view facing right, exactly the pose of images 1-2: the boar standing on four short legs, head low, tusks forward; the woman seated on its back, one hand on the saddle front, the other holding the flail's chain so its ice head hangs behind the boar's rump on the image left; the tip of her ice horn at y 216, her eyes at about y 468, the hooves on y 1188 - 54 squares tall, about 60 squares wide. Every detail in whole 18-px squares - never smaller squares.
HER FACE (most important): chibi - her HEAD BIG (helm and face about half of her seated height; a little bigger than in image 2 is fine, the body a little smaller); a PALE FACE in 3 shades turned to the front-right; TWO ICE-BLUE EYES at the SAME height: the near eye 2x2 squares (one bright blue, one white highlight, one deep blue), the far eye at least 1x2 squares; a 1-square crisp brow; a small 1-2 square stern mouth; two locks of PALE BLONDE hair beside the face, never over the eyes.
THE HELM AND HORNS: a BRONZE-GOLD HELM (3 shades: a dark brown edge, bronze, light gold highlights in blocks) with a BLUE ICE GEM on the brow (2x2 squares with a white highlight); a CURVED BLUE ICE HORN sweeping back on each side (the near one big, 3-4 squares thick, tapering to a point; the far one smaller).
THE BODY: PURPLE LEATHER ARMOUR (3 shades); big pointed BRONZE-GOLD shoulder plates and breastplate set with BRIGHT BLUE ICE GEMS (2 squares each, a white highlight); CREAM-WHITE FUR in pointed tufts at the collar and shoulders (2-3 shades); dark purple gloves and boots.
THE FLAIL: a long BROWN-AND-BLACK WRAPPED CHAIN / HANDLE (1-2 squares thick, brown and black squares alternating) ending in a BIG BLUE ICE HEAD (3 blues with a 1-square CYAN glowing line round it).
THE BOAR: BLUE-GREY FUR in 4 shades (jagged darker edges for the tufts); a big crest of WHITE BRISTLY MANE from the head along the back (2-3 shades, pointed tufts); TWO BIG IVORY TUSKS curving up (3 shades, 2-3 squares thick, the most visible part); a PINK SNOUT (2 shades, a dark pink nostril square); a pink open mouth with a few white teeth; one GLOWING CYAN EYE (2x1 squares, the brightest almost white); pink inner ears; DARK GREY split HOOVES (2-3 squares wide each); OLIVE-GREEN / BRONZE SADDLE ARMOUR (3 shades) with two BIG BLUE GEMS (3-4 squares each, highlighted); BROWN straps (1 square wide); a tail with a tuft behind.
The near legs (image left) in full tone, the far ones a step darker and a little higher; the background visible between the legs and between the chain and the body.
A continuous 1-square near-black outline round the whole character (the chain too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects (no frost, no ice storm, no bola).
```

## 提示词 B（B-1、B-2 各画一次，同一段；附 1_picture_B、2_target_B、3_layout_B、4_head、style 三张）

```text
Attached: 1 the character's approved charging picture (THE LOOK AND COLOURS TO KEEP), 2 the same picture cut down to the target square count (ONLY its size, place and pose are right - its details are broken), 3 the layout with the grid and three lines (orange = the top of the raised flail, blue = her eyes, red = the lowest tusk / hoof), 4 her head read back 8x (where things are), 5-7 STYLE ONLY: other characters of the same game shown 8x, one square = one pixel.
Redraw image 1 as GAME-SIZE PIXEL ART like a pixel artist: a 1254x1254 PNG with a genuine transparent background (alpha only 0 or 255), every square 18 px, aligned on one grid starting at the canvas corner (0, 0). THE WARRIOR WOMAN ON HER WAR BOAR CHARGING to the image right in 3/4 view, exactly the pose of images 1-2: the boar lunging forward, front legs tucked, hind legs pushing, body leaning in, tusks thrust ahead; the woman crouching low over the saddle, the flail raised high behind her with its ice head up on the image left; the top of the raised flail at y 180, her eyes at about y 486, the lowest tusk / hoof on y 1188 - 56 squares tall, about 62 squares wide. Every detail in whole 18-px squares - never smaller squares.
HER FACE (most important): the SAME chibi head as her idle - BIG (helm and face about half of her height); a PALE FACE in 3 shades turned to the front-right; TWO ICE-BLUE EYES at the SAME height (the near eye 2x2 squares with a white highlight, the far eye at least 1x2); a 1-square brow; a small stern mouth; the pale blonde locks never over the eyes.
THE HELM AND HORNS: a BRONZE-GOLD HELM (3 shades) with a BLUE ICE GEM on the brow (2x2, highlighted) and a CURVED BLUE ICE HORN sweeping back on each side (3-4 squares thick near, smaller far).
THE BODY: PURPLE LEATHER ARMOUR (3 shades); BRONZE-GOLD pointed plates with BRIGHT BLUE GEMS (2 squares each); CREAM-WHITE FUR tufts at the collar (2-3 shades); dark purple gloves.
THE FLAIL: the BROWN-AND-BLACK WRAPPED CHAIN / HANDLE (1-2 squares thick, alternating) up behind her, the BIG BLUE ICE HEAD at its end (3 blues, a 1-square CYAN glowing line).
THE BOAR: BLUE-GREY FUR in 4 shades; the WHITE BRISTLY MANE crest (2-3 shades, pointed tufts) swept back; TWO BIG IVORY TUSKS thrust forward and up (3 shades, 2-3 squares thick); the PINK SNOUT and pink open mouth with white teeth; one GLOWING CYAN EYE (2x1); pink inner ears; DARK GREY split HOOVES; OLIVE-GREEN / BRONZE SADDLE ARMOUR with two BIG BLUE GEMS; BROWN straps; the tail flying back. The near legs in full tone, the far ones a step darker; the background visible between the legs.
A continuous 1-square near-black outline round the whole character (the chain too); inside it every material in its own 2-4 flat shades, the shadow of a material its own darkest shade; no stray single odd squares; no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No background, no grid lines, no text, no frame, no cast shadow, no ground, no spell effects (no frost, no ice trail, no dust).
```

## 交回前请检查

- 1254 × 1254，真透明（alpha 只有 0 / 255）；**A、B 都是每格 18 px**，对齐从 (0, 0) 开始的网格；A 冰角尖 y 216、蹄子底 y 1188（54 格）；B 链枷顶 y 180、最低处 y 1188（56 格）。
- **瑟庄妮的脸**：Q 版大头、白皙、**两只冰蓝色眼睛一样高（近眼 2×2 带白高光，远眼也看得见）**、冷峻的嘴；浅金头发不挡眼睛；青铜金头盔 + 额前蓝宝石 + 两只蓝冰角。
- 紫皮甲 + 青铜金尖肩甲 + 蓝宝石 + 米白毛领；棕黑相间的链子 + 蓝色冰锤头（青色亮纹）。
- 钢鬃：灰蓝毛、白鬃毛、**两根象牙色大獠牙最显眼**、粉鼻子、一只青蓝发光的眼睛、深灰蹄子、橄榄绿鞍甲 + 两块大蓝宝石。
- 1 格近黑外描边连续；没有零散杂色格、没有抖动和渐变。
- 交付：`outputs/sejuani-model/sejuani-A-1.png`、`sejuani-A-2.png`、`sejuani-B-1.png`、`sejuani-B-2.png`；原始生成图原样放进 `outputs/sejuani-model/raw/`；`generation-prompts.txt` 写实际提示词；**最后**写 `outputs/sejuani-model/HANDOFF.md`，再打包成 `outputs/sejuani_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sejuani/codex_model/`，在 8 倍下量 Codex 实际的格子（读 raw；Codex 常画得比要求的粗或细，按它自己的格子读回），A 裁到 54 行、B 裁到 56 行（keep_axis、脸框保留，`design_aurelionsol_model.py` / `design_taliyah_model.py` 的做法），12 倍下看两张脸（她的两只冰蓝眼睛、野猪的发光眼和獠牙），给用户挑稿 -> `hd/idle.png`（A，PPU 1.5，冰角尖到蹄子 36 游戏像素）、`hd/run.png`（B，同一比例：跑步和 Q）。
