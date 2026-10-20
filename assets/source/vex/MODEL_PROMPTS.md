# 愁云使者 薇古丝：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **A（影子站起来）**（`1_picture_A.png`）**用户选定了，样子、颜色全照它**；`1_picture_SA.png` 是你画的侧面，侧面的身体照它。
> - 这一步要把她画成**游戏里的格子数**：**整张从影子的耳尖到她的脚底 63 格，她本人从兜帽耳尖到脚底 51 格**。我把 A、SA 直接缩到这个格子数（`2_target_A.png`、`2_target_SA.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、吊坠、影子的螺旋眼碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大：17 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**：**影子的耳尖 y = 119，她的兜帽耳尖 y = 323，两只脚底 y = 1190**。每一格都是 17 × 17 px 的大方块，不要用更小的格子画细节。
> - 一共画**两种**（同一个薇古丝和同一只影子、同样的格子、同样的颜色）：**A 待机（3/4 正面）**、**SA 侧面朝右**，各画**两稿**。

## 大小和位置

- 画布 **1254 × 1254**，**每格 17 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` / `3_layout_SA.png` 的浅灰线每 5 格一条）。
- **A**：照 `2_target_A.png` / `3_layout_A.png`：影子的耳尖 **y = 119**，她的兜帽耳尖 **y = 323**（橙线），她的眼睛约 **y = 697**（蓝线），脚底 **y = 1190**（红线）：**整张 63 格高、约 50 格宽**，她在画面右边、影子在她左后方。
- **SA**：照 `2_target_SA.png` / `3_layout_SA.png`：同样的高度和地面线，**侧面朝右**，约 50 格宽。
- 全在画布里，耳朵、袖子、影子的爪子不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：灰白的小脸；**两只品红色的眼睛：每只约 2 × 3 格，一样高、一样大**，各带 1 格白色高光，**上眼皮是一道深色的厚眼线**（半睁、没精神）；小嘴 1–2 格，往下撇；**青绿色的头发**（3 档）盖住额头、从兜帽两边露出来。
- **兜帽**：深青黑色 3 档，**偏青的亮边**让它和背景、和影子分开；**两只又高又尖的耳朵**，耳朵里面紫色 2 档、耳根一撮浅色绒毛（2 格左右的浅灰白）。
- **身体**：胸口**金色吊坠**（2 档、约 2 × 3 格）；**长到小腿的袖子**，袖口是**品红色的交叉绑带**（一个清楚的 X）；**品红紫色的灯笼裤** 3 档；深色的鞋，两只脚踩在地面线上。
- **影子**：墨一样的**深蓝黑**（2–3 档深靛蓝），外边一圈**靛紫色的亮边**（1 格）；**两只浅蓝白色的线条眼，每只约 4 × 4 格，中间是螺旋瞳孔**（在这么少的格子里画成一个清楚的 @ 形状就行）；两只尖耳朵；一只**大爪子手**举在她身后（不碰她的脸）；身子往下收成一缕烟连在她身后的地上。**影子在这么小的格子里要简单、轮廓清楚**：比第 0 步少一些零碎的烟丝，不要碎成很多小块。**影子和她之间要有她自己的近黑描边隔开**，一眼看出是两个东西。
- **A 的姿势**和第 0 步的 A 一样：她 3/4 正面朝右站着，两只长袖垂在身体两边，脸朝右前方；**近侧的腿（画面左边）颜色亮，远侧的腿（画面右边）稍暗**；影子从她左后方立起来，比她高 12 格。
- **SA 的姿势**：**她完全侧面、朝右站直**（身体照 `1_picture_SA.png`），**但头是和 A 一样的那颗头**：**脸朝右前方、两只品红色的眼睛都看得见**（不要另画一个只有一只眼的侧脸：所有动作都用同一张脸）；**近侧的长袖垂在身体前侧，外面一圈描边、和身体分开**；远侧的袖子只露一点、稍暗；**两条腿一前一后**站在地面线上，鞋尖朝右。影子同样从她身后（画面左边）立起来。所有动作都从这张画出来，所以袖子、腿、头、影子都要清楚地分开。
- **一圈 1 格的近黑外描边**（她和影子各一圈），连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的佐伊、悠米，**和薇古丝同一个密度 PPU 1.5**；魔腾只看深色暗影怎么分档、怎么留亮边；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `vex_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `1_picture_SA.png` | 你第 0 步画的侧面 | SA 的身体、袖子、腿（头用 A 的） |
| `2_target_A.png` / `2_target_SA.png` | 缩到游戏格子数、每格 17 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_SA.png` | 加网格线：橙 = 她的兜帽耳尖，蓝 = 她的眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的头部（8 倍） | 兜帽、耳朵、脸、眼睛、头发 |
| `style/5_style_zoe.png`、`6_style_yuumi.png` | 本包的佐伊、悠米（同密度），8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、头发怎么画 |
| `style/7_style_nocturne.png` | 本包的魔腾（8 倍） | **只看风格**：深色的暗影怎么分档、留亮边 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of this character - a small sullen chibi yordle girl in a big dark teal-black hoodie whose hood has two tall pointed ears (violet inside, a pale tuft at the base), messy teal hair over grey-pale skin, magenta eyes under heavy lids, a small down-turned mouth, a gold pendant, sleeves far too long hanging to her shins with magenta cross-laces at the cuffs, puffy magenta-purple trousers, dark shoes; behind her (on the image left) her living SHADOW risen from the ground: an ink-dark blue-black creature with an indigo-violet rim, two pointed ears, two pale blue-white line-drawn eyes with spiral pupils, a big clawed hand, its body narrowing into a wisp joined to the ground behind her (3/4 view facing right) - its LOOK and COLOURS are approved, but it is drawn with far too many small squares; 1SA your earlier side view of the same (only for her side-on body); 2A and 2SA images 1A and 1SA cut down to the RIGHT square count - 63 squares from the Shadow's ear tips to her soles, her own 51 squares from her hood's ear tips to her soles - shown with 17 px squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A and 3SA the same with grid lines every 5 squares: orange = her hood's ear tips, blue = her eyes, red = the ground; 4 her head of image 1A enlarged; 5-6 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - how a face, eyes and hair are drawn with this few squares; 7 STYLE ONLY: a dark shadowy character of the same game, how its dark shades and lit edges are drawn.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 17 px, aligned on one straight grid from the canvas corner; the Shadow's ear tips at y 119, her hood's ear tips at y 323 and her soles on y 1190 - exactly 63 squares tall in all, she herself 51; the figure filling the canvas with at least one empty square on every side. Every detail drawn with whole 17 px squares, never with smaller pixels.
With this few squares make every part READ: her small grey-pale face; TWO MAGENTA EYES, each about 2x3 squares, at the SAME height and the SAME size, each with ONE white highlight square and a thick dark upper lid (half-closed, bored); a small down-turned mouth; the teal hair in 3 shades over her forehead and out of both sides of the hood; the dark teal-black hood and hoodie in 3 shades with LIGHTER TEAL EDGES; the two tall hood ears, violet inside, a pale tuft at the base; the gold pendant; the long sleeves with a clear magenta X of laces at each cuff; the puffy magenta-purple trousers; dark shoes. THE SHADOW kept SIMPLE with a clear silhouette (fewer loose wisps than image 1A, never broken into many small bits): ink-dark blue-black in 2-3 very dark indigo shades with a 1-square INDIGO-VIOLET RIM; TWO pale blue-white line-drawn eyes, each about 4x4 squares with a spiral pupil (a clear @ shape); two pointed ears; one big clawed hand raised behind her that never touches her face; its body narrowing into a wisp joined to the ground behind her. Her own near-black outline always runs between her and the Shadow: at a glance they are two beings.
One continuous 1-square near-black outline round her and round the Shadow; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`vex-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  POSE A: her idle exactly as images 1A, 2A and 3A - she stands in 3/4 view facing right, both long sleeves hanging at her sides, the face to the front-right; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, both feet on the ground line; the Shadow risen behind her on the image left, 12 squares taller than her; about 50 squares wide.
  ```
- **SA（`vex-model-SA-1.png`、`-SA-2.png`，两稿）**：
  ```text
  POSE SA: the SAME character SIDE-ON, FACING RIGHT (size and place of images 2SA and 3SA, her body as in image 1SA), standing upright; her head is the SAME head as in image 1A - turned to the front-right with BOTH magenta eyes visible (not a one-eyed profile); the NEAR long sleeve hanging a little in front of her body, separated from the body by its own outline; the far sleeve only a little visible and a step darker; the two legs one in front of the other on the ground line, the shoes pointing right; the Shadow risen behind her on the image left, the same as in A.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 17 px 的大方块**：影子耳尖 y 119、她的耳尖 y 323、脚底 y 1190，**整张正好 63 格高、她本人 51 格**（数一下台阶数：**如果是 90–130 格就是格子画小了，请重画**）。
- 两只品红色眼睛一样大、一样高、带高光、厚眼皮（A、SA 都是）；SA 里是和 A 同一个朝右前方的头、两只眼睛都看得见；SA 身子直立、近侧袖子和身体分开、两条腿一前一后。
- 影子简单、轮廓清楚、深蓝黑带靛紫亮边、两只螺旋眼看得清；不挡她的脸；她和影子之间有描边隔开。外描边连续；没有任何技能特效。

## 交付（`outputs/vex-model/`）

- `vex-model-A-1.png`、`vex-model-A-2.png`、`vex-model-SA-1.png`、`vex-model-SA-2.png`；原始生成图原样放 `outputs/vex-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/vex_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 17 px、63 行），从 raw/ 按格读回（regrid），在游戏大小下和佐伊、悠米、波比、安妮并排自查（PPU 1.5，她本人 34 游戏像素），把 A / SA 的两稿给用户挑。
- 动作照英雄联盟的骨骼摆（`tools/lol/anim_graph.py Vex`、`pose_ref.py`，渲染要藏掉 Shadow 子网格、Shadow_* / VFXUlt 骨骼和备用的眼睛）：普攻 Attack_1 / Attack_2，W Spell2，Q Spell1，E Spell3，R Spell4_Cast（扔出飞弹）、Spell4_Dash（冲过去）、Spell4_Attack（落地一击），跑 Run，死亡 Death。造型摆不出的姿势让 Codex 照带骨架的包画；腿和待机一致、不变形；一张脸用在所有帧；影子跟着她（站在身后），技能里伸出去的影子画在特效里。
