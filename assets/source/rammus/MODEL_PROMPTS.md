# 披甲龙龟 拉莫斯：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（待机）** 和 **B（刺球）**（`1_picture_A.png`、`1_picture_B.png`）**用户选定了，样子、颜色全照它们**。
> - 这一步要把他画成**游戏里的格子数**：**从最高的尖刺尖到鞋底 43 格**。我把 A、B 直接缩到这个格子数（`2_target_A.png`、`2_target_B.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、甲板、挽具碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大：26 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**：**最高的尖刺尖 y = 78，两只鞋底 y = 1196**。每一格都是 26 × 26 px 的大方块，不要用更小的格子画细节。
> - 一共画**四种**（同一个拉莫斯、同样的格子、同样的颜色）：**A 待机（3/4 正面）**、**S 侧面朝右**、**B 刺球**、**W 尖刺防御（蜷起来防御，侧面）**。A 和 S 各画**两稿**，B 和 W 各一稿。

## 大小和位置

- 画布 **1254 × 1254**，**每格 26 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A**：照 `2_target_A.png` / `3_layout_A.png`：最高尖刺尖 **y = 78**（橙线），眼睛约 **y = 728**（蓝线），鞋底 **y = 1196**（红线）：**43 格高、约 42 格宽**。
- **S**：同样 **43 格高**（尖刺尖 y = 78、鞋底 y = 1196），**侧面朝右**：`3_side_ref.png` 是英雄联盟模型的侧面按这个格子数摆好的（淡色，只看**轮廓、位置和大小**，约 46 格宽）。
- **B**：照 `2_target_B.png`：圆球约 **44 × 43 格**，球顶 y = 78、球底 y = 1196。
- **W**：同样 **43 格高**，侧面朝右：`3_curl_ref.png` 是英雄联盟的尖刺防御那一帧（淡色，只看轮廓、位置和大小，约 41 格宽）。
- 全在画布里，尖刺、爪子不出画。

## 在 43 格里要画清楚的地方

- **头**（`4_head.png` 是第 0 步读回的头部，8 倍）：小小的绿色乌龟头，从甲壳前缘的帽檐下面探出；**两只红色的眼睛：每只 2 格，一样高，各带 1 格亮高光**；嘴 1 格深色。**S 和 W 里头也是同一个头**：**脸朝右前方、两只眼睛都看得见**（和 A 一样的脸，不要另画一个只有一只眼的侧脸）。
- **甲壳**：橙金鳞片甲板 3 档 + 1 格亮高光，每块甲板一圈浅色边；**深棕色皮带**清楚；**浅黄尖刺**（亮面奶白、背光面偏橙，2–3 档），最高的几根在背脊上，边缘一圈小刺；甲壳前缘是一道金色的**帽檐**。
- **身体**：青绿鳞皮 3 档 + **深绿色斑点**；**米白爪子**（2 档）；**黄褐色肚子**；**暗红挽具** 2 档 + **灰钢钉**（肚子下面一根大钢刺朝下）。
- **A 的姿势**和第 0 步的 A 一样：3/4 正面朝右，两只长手臂垂在两侧，爪子快到地面，两条短腿分开站稳；**近侧（画面左边）颜色亮，远侧（画面右边）稍暗**。
- **S 的姿势**：**完全侧面、朝右**：甲壳拱在背上，头在画面右边从帽檐下探出，**近侧的手臂垂在身前（画面右边、肚子前面）**，远侧手臂只露一点、稍暗；**两条腿一前一后**站在地面线上，脚尖朝右。所有动作都从这张画出来，所以**手臂、腿要清楚地和身体分开**（手臂外面一圈描边）。
- **B 的球**和第 0 步的 B 一样：头和四肢都收进去，外面一圈橙金甲板和深棕皮带，**尖刺朝四面八方**；**尽量圆、左右上下大致对称**（游戏里靠整张图转 90° 做滚动）。
- **W（尖刺防御）**，侧面朝右（`3_curl_ref.png`）：他**压低身子缩进甲壳**（膝盖弯、甲壳更低更圆），**两只前臂抬起挡在胸前、爪子朝上**，头缩在帽檐下，**两只红眼睛从手臂上面露出来**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的雷克塞、悟空、波比，**和拉莫斯同一个密度 PPU 1.2**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `rammus_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1_picture_B.png` | 你第 0 步画的 B（用户选定） | 刺球的样子 |
| `2_target_A.png` | A 缩到游戏格子数、每格 26 px 放在画布上（细节是坏的） | A 的**大小、位置、比例、姿势** |
| `2_target_B.png` | B 缩到同样的比例 | B 的大小、位置 |
| `3_layout_A.png` | A 加网格线：橙 = 尖刺尖，蓝 = 眼睛，红 = 地面 | 对齐网格、43 格的高度、地面线 |
| `3_side_ref.png` | 英雄联盟模型的侧面，按格子数摆好（淡色） | **S** 的轮廓、位置、大小 |
| `3_curl_ref.png` | 英雄联盟的尖刺防御（淡色） | **W** 的轮廓、位置、大小 |
| `4_head.png` | 第 0 步读回的头部（8 倍） | 帽檐、乌龟头、红眼睛 |
| `style/5_style_reksai.png` … `7_style_poppy.png` | 本包的雷克塞、悟空、波比（同密度），8 倍放大 | **只看风格**：这么粗的格子里甲壳、鳞片、眼睛、金甲怎么画 |

## 提示词（四种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1B your own earlier pixel-art drawings of this character - a squat armadillo-turtle creature under a huge domed shell of orange-gold scale plates bound by dark-brown leather straps, pale-yellow cone spikes along its crest and smaller ones round its rim, the front edge of the shell overhanging like a golden hood, a small green turtle head with two glowing red eyes peeking out under it, teal-green scaly arms and legs with dark-green spots, long arms, cream claws, a yellow-tan belly crossed by a dark-red harness with grey steel studs and one big steel spike pointing down (1A his idle, 3/4 view facing right; 1B the same creature curled into a round spiked ball) - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A and 2B the same two cut down to the RIGHT square count - 43 squares from the tallest spike tip to the soles - shown with 26 px squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A the same with grid lines every 5 squares: orange = the tallest spike tip, blue = the eyes, red = the ground; 3-side and 3-curl: the game's 3D model at the same count (faded) seen from the side, standing and curled up in defence - only their OUTLINE, PLACE and SIZE; 4 the head of image 1A enlarged; 5-7 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - how a carapace, scales, eyes and gold armour are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 26 px, aligned on one straight grid from the canvas corner; the top at y 78 and the bottom on y 1196 - exactly 43 squares tall, the figure filling the canvas. Every detail drawn with whole 26 px squares, never with smaller pixels.
With only 43 squares make every part READ: the orange-gold shell plates in 3 shades with one bright highlight square and a light rim on each plate; the dark-brown straps; the pale-yellow spikes (cream lit side, warmer orange shaded side); the golden hood at the front of the shell; the small green turtle head under it with TWO RED EYES, each 2 squares, at the SAME height, each with ONE bright highlight square; the teal-green scaly skin in 3 shades with dark-green spots; cream claws in 2 shades; the yellow-tan belly; the dark-red harness in 2 shades with grey steel studs and the big steel spike pointing down.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`rammus-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  POSE A: his idle exactly as images 1A, 2A and 3A - 3/4 view facing right, the shell domed over his back and head, the head under the front hood looking to the front-right, the two long arms hanging at his sides with the claws near the ground, the two short legs apart and planted; the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker; about 42 squares wide.
  ```
- **S（`rammus-model-S-1.png`、`-S-2.png`，两稿）**：
  ```text
  POSE S: the SAME character SIDE-ON, FACING RIGHT (outline and size of image 3-side, about 46 squares wide): the shell domed over his back, the hood at the right; the head under the hood is the SAME head as in image 1A - turned to the front-right with BOTH red eyes visible (not a one-eyed profile); the NEAR arm hanging in front of his belly on the image right, clearly separated from the body by its outline, the far arm only a little visible and a step darker; the two legs one in front of the other on the ground line, the feet pointing right.
  ```
- **B（`rammus-model-B.png`，一稿）**：
  ```text
  POSE B: the SAME character CURLED UP INTO A ROUND SPIKED BALL as image 1B, size and place of image 2B (about 44 x 43 squares): the head, arms and legs all tucked in and NOT visible, the whole outside made of the orange-gold plates and the dark-brown straps, the spikes pointing outward ALL ROUND; the ball as ROUND as possible and roughly symmetric left-right and top-bottom (it will be turned by quarter turns to roll); resting on the ground line.
  ```
- **W（`rammus-model-W.png`，一稿）**：
  ```text
  POSE W: the SAME character SIDE-ON, FACING RIGHT, HUNKERED DOWN IN DEFENCE (outline and size of image 3-curl, about 41 squares wide): knees bent, the shell lower and rounder over him, BOTH forearms raised in front of his chest with the claws pointing up, the head pulled in under the hood with BOTH red eyes visible just above the arms; the feet on the ground line.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 26 px 的大方块**：顶 y 78、底 y 1196，**正好 43 格高**（数一下台阶数：**如果是 70–110 格就是格子画小了，请重画**）。
- 两只红眼睛一样大、一样高、带高光（A、S、W）；S 和 W 里是同一个朝右前方的头、两只眼睛都看得见；B 是完整的圆球、看不到头和四肢；外描边连续；没有任何特效。

## 交付（`outputs/rammus-model/`）

- `rammus-model-A-1.png`、`rammus-model-A-2.png`、`rammus-model-S-1.png`、`rammus-model-S-2.png`、`rammus-model-B.png`、`rammus-model-W.png`；原始生成图原样放 `outputs/rammus-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/rammus_model_done.zip`。中间不要停，六张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 26 px、43 行），从 raw/ 按格读回（regrid），在游戏大小下和雷克塞、悟空、阿木木、塔姆并排自查（PPU 1.2，36 游戏像素），把 A / S 的两稿给用户挑。
- 动作帧自己摆（`rig_rammus.py`，照 rig_maokai.py / rig_nasus.py / rig_jarvaniv.py / rig_poppy.py：只整格平移、绕半格点的四分之一转、镜像；滚动 = 整颗球 B 的四分之一转）。每个动作对照英雄联盟（`tools/lol/anim_graph.py Rammus`、`pose_ref.py`）：普攻 rammus_attack1 / attack2 / crit；Q rammus_spell1_windup（缩成球）、滚动、撞击；W Rammus_channel；E rammus_spell3；R rammus_spell4 / Spell4_Jump；跑 rammus_run；死亡 rammus_death（8 帧带回弹）。自查到完美（8 倍逐帧：不挡脸、不错切、不留透光缝）再给用户审。
