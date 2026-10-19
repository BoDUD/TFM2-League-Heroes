# 德玛西亚之翼 奎因：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（举着连弩的待机）**（`1_picture_A.png`）**用户选定了，样子、颜色、姿势照它**；华洛照 `1b_picture_V.png`，骑华洛照 `1c_picture_R.png`。
> - 这一步要画成**游戏里的格子数**：**从头盔尖到脚底 49 格**，约 42 格宽。我把 A 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（脸、眼睛、金边碎成杂点）。请像一个像素画师照着 `1_picture_A.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **用户要求头画大一点**，照本包的射手（附图 7：凯特琳、阿克尚缩到同样 49 格）：**头（头盔尖到下巴）约 15 格**（第 0 步只有约 12 格），脸宽一些、两只眼睛清楚；身子相应短一点（腿短 2–3 格），总高还是 49 格。
> - **一共四种图，每种两稿，八张**（同一个奎因、同样的格子密度、同样的颜色）：
>   - **Q：3/4 正面朝右**（和 A 一样举着连弩）：游戏里的待机。
>   - **S：侧面朝右**（附图 5、6）：身体转成侧面，近侧的肩膀和手臂在前，**举着连弩的右手臂朝右平伸**，两条腿一前一后（近侧腿在前、颜色亮，远侧腿在后、稍暗），靴尖朝右。**头保持和 3/4 正面一样**（脸朝右前方、两只眼睛都看得见，同样的格子），只把身体转成侧面。她的跑步和攻击动作都从这张侧面图来做。
>   - **V：华洛单独**（附图 1b、8）：侧面朝右展翅滑翔，**翼尖到翼尖 34 格**，同样的格子密度。游戏里他在奎因头顶盘旋。
>   - **R：奎因骑在华洛背上**（附图 1c、9）：侧面朝右滑翔，**整张约 64 格宽、49 格高**；**奎因的头和 Q 一样大（约 15 格、同样的脸）**，所以华洛相对她比第 0 步小一些——像骑着坐骑的 Q 版人物；翅膀可以往上扬，别横向铺得太宽。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，每张图的格子大小不同（见下表），每一格都是一个整齐的大方块，不要用更小的格子画细节。

## 大小和位置

| 图 | 每格 | 位置（照附图） |
|---|---|---|
| Q / S | **22 px** | **头盔尖 y = 132，眼睛约 y = 308，两只脚底 y = 1210**：头盔尖到脚底 **49 格**。Q 宽约 42 格（`2_target.png` / `3_layout.png`）；S 照 `6_side_layout.png` 的淡色剪影的大小和地面线，放在画布中间 |
| V | **30 px** | 翼尖到翼尖 **34 格**、约 29 格高，放在画布中间（`8_valor_target.png`） |
| R | **18 px** | 约 **64 格宽、49 格高**，放在画布中间（`9_ride_target.png`；那张里她的头太小，按上面的要求画大） |

网格从画布左上角 (0, 0) 开始对齐（布局图的浅灰线每 5 格一条）。

## 在 49 格里要画清楚的地方

- **头**（头盔尖到下巴约 15 格，`4_head.png` 是第 0 步读回的头，8 倍）：金色鹰翼面甲（3 档金色，两边往上翘的翼尖各 2–3 格）、深蓝兜帽（2–3 档）、面甲下露一点深紫色头发；**两只琥珀色的眼睛：每只 1–2 格，一样高**，深色的眉 1 格；肤色 2–3 档；红色嘴唇 1 格。
- **身体**：深紫蓝作战服（3 档）、棕色皮革胸甲和皮带（2–3 档）、**近侧（画面左边）的大块金色羽毛肩甲**（3 档）、腰两侧金边的羽毛护甲片、背后蓝紫色的羽毛披风（2–3 档，要有偏亮的边）、银灰色的手套。
- **连弩**：绑在右前臂上，金色和钢灰色（各 2 档），横着的弩臂两端各 1–2 格，弩身朝右。
- **腿**：深紫色护腿（要有偏亮的边，不然在深色背景上糊成一团），膝盖和小腿前面的金色护板，尖头深棕靴子（2 档），两只脚底都在地面线上。
- **华洛**（V 和 R）：蓝色、蓝紫色的羽毛（3 档，翼尖更紫），每根飞羽的边分得开；金色的弯嘴、金色胸甲、翅膀上的金色护带；浅棕色的腿羽、深色的爪子；看得见的那只眼睛 1 格。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 11–14 一样的像素画（本包的凯特琳、阿克尚、薇恩、艾尼维亚；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画弩箭、风痕、光）。

## 附图（压缩包 `quinn_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1b_picture_V.png` | 你第 0 步画的华洛 | V、R 的华洛 |
| `1c_picture_R.png` | 你第 0 步画的骑华洛 | R 的姿势 |
| `2_target.png` | A 缩到游戏格子数、每格 22 px 放在画布上（细节是坏的） | Q 的**大小、位置、姿势**照它，坏的地方照 1 重画（头要画大） |
| `3_layout.png` | 同一张加网格线：绿 = 头盔尖，蓝 = 眼睛，红 = 地面 | 对齐网格、49 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 面甲、兜帽、头发、眼睛、嘴唇 |
| `5_side_ref.png` | 英雄联盟原版的待机，接近侧面、朝右 | **S 的身体**：侧面的厚度、平伸的连弩手臂、两腿一前一后 |
| `6_side_layout.png` | 5 缩到同样的 49 格高放在网格上（淡色，只看大小） | S 的大小、位置、地面线 |
| `7_proportions.png` | 本包的凯特琳、阿克尚缩到同样 49 格（蓝线 = 从顶上数 15 格） | **头身比例**：头约 15 格 |
| `8_valor_target.png` | 华洛缩到 34 格宽、每格 30 px（细节是坏的） | V 的大小、位置 |
| `9_ride_target.png` | 骑华洛缩到 64 格宽、每格 18 px（细节是坏的） | R 的大小、位置（她的头要画大） |
| `style/11_style_caitlyn.png` … `14_style_anivia.png` | 本包的凯特琳、阿克尚、薇恩、艾尼维亚，8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、披风、暗色身体的亮边、大鸟的羽毛怎么画 |

## 提示词 1：`quinn-model-Q-1.png`、`quinn-model-Q-2.png`（3/4 正面，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a young woman ranger: a dark navy-violet bodysuit, a brown leather corset and straps, a deep-blue hood under a GOLD WINGED VISOR HELM (a gold brow plate whose two sides sweep up into eagle-wing points), a little dark purple hair, AMBER EYES, red lips; a BIG GOLD FEATHER PAULDRON on the near shoulder, gold-edged feathered tassets at the hips, a blue-violet feathered cape, silver-grey gloves, a GOLD AND STEEL REPEATING CROSSBOW strapped on her right forearm, dark violet greaves with gold knee and shin plates, pointed dark brown boots; her RIGHT ARM RAISED holding the crossbow forward to the right - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 1b and 1c your earlier eagle and her riding it (for other pictures); 2 the same character cut down to the RIGHT square count - 49 squares from the visor crest to her soles, about 42 squares wide - shown with 22 px squares on a 1254x1254 canvas: its SIZE, PLACE and POSE are right, but the cut broke its details (the face, the eyes and the gold trims are specks); 3 the same with grid lines every 5 squares: green = the visor crest, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5 and 6 are for the side view (not this picture); 7 two other characters of the same game brought to the same 49 squares - copy their HEAD SIZE: the head (visor crest to chin) about 15 squares, bigger than image 2's; 8 and 9 are for other pictures; 11-14 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel - how a face, eyes, a cape, the lit edges of a dark body and a big bird's feathers are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 22 px, aligned on one straight grid from the canvas corner; the visor crest at y 132, the eyes at about y 308, both soles on y 1210 - exactly 49 squares from the crest to the soles, about 42 squares wide, the figure filling the canvas as in image 2. Every detail drawn with whole 22 px squares, never with smaller pixels.
THE HEAD BIGGER than image 2: about 15 squares from the visor crest to the chin (as the heads of image 7), the face wider; the body a little shorter to keep 49 squares in all (the legs 2-3 squares shorter).
With only 49 squares make every part READ: the gold winged visor in 3 golds with its two upswept wing points (2-3 squares each), the deep-blue hood (2-3 shades), a little dark purple hair; TWO AMBER EYES, each 1-2 squares, at the SAME height, a 1-square dark brow; the skin in 2-3 shades, 1 square of red lips; the navy-violet bodysuit (3 shades), the brown leather corset and straps (2-3 shades); the BIG GOLD FEATHER PAULDRON on the near shoulder (image left, 3 golds), the gold-edged tassets at the hips, the blue-violet feathered cape behind her with LIGHTER EDGES; silver-grey gloves; the gold and steel crossbow on the right forearm (2 golds, 2 steels), its bow arms 1-2 squares each side, pointing right; the dark violet greaves with LIGHTER EDGES, gold knee and shin plates, pointed dark brown boots, both soles on the ground line.
THE POSE as image 1: feet apart one in front of the other, knees a little bent, the RIGHT ARM RAISED holding the crossbow forward to the right, the near (left) arm down at her side; 3/4 view facing right (the face to the front-right), the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no bolts, no wind lines, no glow), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`quinn-model-S-1.png`、`quinn-model-S-2.png`（侧面朝右，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images and the SAME character, colours, square size (22 px), square count (49 squares crest to soles) and the SAME BIGGER HEAD (about 15 squares) as prompt 1 - now SIDE-ON, FACING RIGHT. Image 5 is the original character nearly from the side, facing right: copy from it the BODY seen side-on - the depth of the body, the right arm stretched forward with the crossbow, the legs one in front of the other; image 6 is that view brought to the same 49 squares on the grid (faded: size, place and ground line only).
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 22 px on one straight grid from the canvas corner; the visor crest at y 132, the eyes at about y 308, both soles on y 1210 - exactly 49 squares from the crest to the soles, in the middle of the canvas.
THE BODY SIDE-ON: the NEAR shoulder in front, the RIGHT ARM STRETCHED FORWARD horizontally to the image right holding the crossbow (the crossbow pointing right); the other arm mostly behind the body, a step darker; the cape hanging behind her back; the chest and the corset in profile; the two legs one in front of the other (the NEAR leg in front in full tone, the FAR leg behind a step darker), the boot tips pointing right.
THE HEAD stays the SAME as the 3/4 view of prompt 1 (the face to the front-right, BOTH amber eyes visible, the same squares, the gold winged visor, the hood, the lips) - only the body is turned side-on.
The same colours and details as prompt 1: the navy-violet bodysuit, the brown leather, the gold pauldron and tassets, the blue-violet cape with lighter edges, the gold and steel crossbow, the dark violet greaves with lighter edges and gold plates, the pointed boots; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 3：`valor-model-V-1.png`、`valor-model-V-2.png`（华洛，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images. Image 1b is your own earlier pixel-art drawing of her EAGLE - a blue and blue-violet eagle, a crest on its blue head, a GOLD HOOKED BEAK, a GOLD BREASTPLATE, GOLD BANDS round its wings, light-brown feathered legs and dark talons, gliding side-on to the right with the wings spread - its LOOK, COLOURS and POSE are approved, drawn with far too many small squares; image 8 is it cut down to the RIGHT square count - 34 squares from wing tip to wing tip, about 29 squares tall - with 30 px squares on a 1254x1254 canvas: SIZE, PLACE and POSE right, details broken.
Draw with the image generator ONE clean pixel-art picture of that eagle at the square count of image 8: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 30 px on one straight grid from the canvas corner, 34 squares from wing tip to wing tip, in the middle of the canvas, as in image 8. Every detail drawn with whole 30 px squares.
With only 34 squares make every part READ: the blue head with its crest (2-3 squares) and ONE visible eye (1 square), the gold hooked beak (2-3 squares) pointing right; the blue and blue-violet feathers in 3 shades, the wing tips more violet, the edges of the big flight feathers readable as separate steps; the gold breastplate and the gold band on each wing (2 golds); light-brown leg feathers and dark talons tucked under the body; the near wing in front in full tone, the far wing behind a step darker.
One continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 4：`quinn-model-R-1.png`、`quinn-model-R-2.png`（骑华洛，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images. Image 1c is your own earlier pixel-art drawing of HER RIDING THE EAGLE (side-on, gliding to the right, the woman astride its back, leaning forward, her crossbow pointing forward); image 9 is it cut down to about 64 squares wide and 49 tall with 18 px squares on a 1254x1254 canvas: the SIZE and PLACE of the whole picture are right, details broken - and HER figure in it is TOO SMALL.
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 18 px on one straight grid from the canvas corner, about 64 squares wide and 49 squares tall, in the middle of the canvas.
THE RIDER is the SAME character as prompt 1 at the SAME square count: HER HEAD about 15 squares from the visor crest to the chin, the SAME face (the gold winged visor, the hood, both amber eyes, the lips), the same colours; she sits astride / crouches on the eagle's back behind its shoulders, leaning forward, her near hand holding the eagle's gold wing band, her right arm with the crossbow pointing forward (right); the cape blowing back.
THE EAGLE is the SAME eagle as prompt 3 (blue and blue-violet feathers, the gold beak, the gold breastplate and wing bands, the talons), gliding side-on to the right, carrying her - smaller next to her than in image 1c, like a cartoon rider on her mount; its wings raised up and back rather than spread flat, so the whole picture stays about 64 squares wide.
One continuous 1-square near-black outline round the whole group; every material in its own 2-3 flat shades; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects (no wind lines), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **八张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- Q、S：**每格 22 px**，头盔尖 y 132、脚底 y 1210，**头盔尖到脚底正好 49 格**（数一下台阶数：**如果是 80–110 格就是格子画小了，请重画**）；**头约 15 格**，两只琥珀色的眼睛一样高。
- V：每格 30 px，翼尖到翼尖 34 格；R：每格 18 px，约 64 × 49 格，**奎因的头和 Q 一样大**。
- 金色鹰翼面甲、深蓝兜帽、近侧的大金肩甲、披风、连弩、金色护板、尖头靴；华洛的金嘴、金胸甲、金护带；外描边连续；没有任何特效。
- Q：举着连弩朝右；S：侧面、连弩手臂平伸朝右、两腿一前一后、**头和 Q 一样**。

## 交付（`outputs/quinn-model/`）

- `quinn-model-Q-1.png`、`quinn-model-Q-2.png`、`quinn-model-S-1.png`、`quinn-model-S-2.png`、`valor-model-V-1.png`、`valor-model-V-2.png`、`quinn-model-R-1.png`、`quinn-model-R-2.png`；原始生成图原样放 `outputs/quinn-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/quinn_model_done.zip`。中间不要停，八张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（Q / S 应约 22 px、头盔尖到脚底 49 行；V 30 px；R 18 px），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在游戏大小下和凯特琳、阿克尚、薇恩、提莫并排自查（PPU 1.3，38 游戏像素），给用户挑每种一张。
- 动作帧自己摆（rig_quinn.py，照 rig_volibear.py / rig_rammus.py：只整格平移、绕半格枢轴的四分之一转、镜像；一张脸用在所有帧）。英雄联盟的动作：普攻 Quinn_attack1–4（连弩开火）；Q quinn_spell1（挥手放鹰）；E Quinn_spell3_dash + Quinn_spell3_flip；R Quinn_Spell4_Channel（召鹰）+ 骑乘（quinnvalor_run_glide / run_flap）；跑 Quinn_run；死亡 quinn_death（8 帧带落地回弹）；挨打第 1 帧白闪并后退。
