# 大发明家 黑默丁格：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**（上一步的 fixed 版就是缩小的，糊了，没用上；用的是你 raw/ 里的原画）。
> - 第 0 步你画的三张（`1_picture_A.png` 黑默丁格 3/4、`1_picture_T.png` 小炮台正面、`1_picture_X.png` 巨型炮台正面）**样子、颜色用户认可了，全照它们**。注意：你上一步是照第一版包画的，两座炮台的名字反了——**四条腿、两根排气筒的是小炮台 T，两边大齿轮、三脚架的是巨型炮台 X**，本包里的图已经换好。
> - 这一步要画成**游戏里的格子数**：**黑默丁格从头发顶到鞋底 54 格**，**小炮台 30 格**，**巨型炮台 45 格**。我把三张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（护目镜、胡子、头发、扳手碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，撑满画布**。画布用你平时的 **1254 × 1254**，三张的格子大小不一样（为了都撑满画布）：**A 每格 20 px**，**T 每格 28 px**，**X 每格 24 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**四张**：**A 两稿**（A-1 / A-2）、**T 一稿**、**X 一稿**。只要 3/4 面，**不画侧面**。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（黑默丁格 3/4，朝右）**：每格 **20 px**；照 `2_target_A.png` / `3_layout_A.png`：头发顶 **y = 100**（橙线），护目镜约 **y = 520**（蓝线），鞋底 **y = 1180**（红线）：**54 格高、约 52 格宽**。
- **T（小炮台，正面）**：每格 **28 px**；照 `2_target_T.png` / `3_layout_T.png`：顶上红球 **y = 336**，脚底 **y = 1176**：**30 格高、约 38 格宽**。
- **X（巨型炮台，正面）**：每格 **24 px**；照 `2_target_X.png` / `3_layout_X.png`：顶上红球 **y = 96**，脚底 **y = 1176**：**45 格高、约 42 格宽**。
- 全在画布里，头发、扳手、排气筒、齿轮、腿不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **黑默丁格的脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：**两只红框护目镜一样大、一样高**，每只约 **5 × 5 格**：一圈红框（2 档），里面青蓝色镜片（2–3 档）带 **1–2 格白色高光**；两镜中间一个粉色小鼻子；下面**白色大八字胡**往两边翘（米白 2–3 档，一绺一绺分开）；**橙色尖耳朵**从头发左边伸出来（3 档）。
- **头发**：一大团金黄色头发往后炸开，**4 档**：暗处偏橙棕、亮处偏淡黄，一绺一绺卷起来分开，**不要糊成一团黄**；头顶两撮尖发角；右上方小支架顶着**红框放大镜**（镜片青蓝带白点）。
- **身体**：墨绿灰长外套（3 档），胸前一排小金扣，**黄铜 H 形带扣**（2 档）在棕色皮带上；左手**橙色多功能工具**（3 档，能看出是一个方块工具），右手**灰绿扳手**（3 档，扳手头开口清楚、红色小球）；**黑灰靴子**两只分开。
- **小炮台 T**：灰紫炮身（3 档），正中**大红八角形炮口**，炮口里面深色；两肩浅灰绿装甲板（3 档）和排气栅格；肩上两根斜伸的**浅灰绿粗排气筒**；顶上**红球**；**四条机械腿**往两边叉开，**红色方块脚**。左右对称。
- **巨型炮台 X**：灰炮身（3 档），正中**炮管和红色炮口**；两边**浅灰绿大齿轮**（齿一颗颗分开）；两根浅灰绿弯管套红环；顶上小杆和**红球**；下面**红色转盘**和**三条短腿**（浅灰绿圆关节，暗红脚）。左右对称。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的薇古丝、吉格斯、杰斯加农炮形态，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `heimerdinger_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_T.png` / `1_picture_X.png` | 你第 0 步画的三张（用户认可，炮台已换对） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_T.png` / `2_target_X.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_T.png` / `3_layout_X.png` | 加网格线：橙 = 最高点，蓝 = 护目镜，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的头部（8 倍） | 护目镜、胡子、耳朵、头发、放大镜 |
| `style/5_style_vex.png`、`6_style_ziggs.png`、`7_style_jayce_cannon.png` | 本包的薇古丝、吉格斯、杰斯加农炮形态，8 倍放大 | **只看风格**：这么粗的格子里约德尔人的大头和脸、海克斯机械怎么画 |

## 提示词（三种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A, 1T and 1X your own earlier pixel-art drawings - 1A an old yordle inventor in 3/4 view facing right: a huge spiky mane of golden-yellow hair, big pointed orange ears, red-rimmed goggles with cyan lenses, a bushy white moustache, a small red-rimmed magnifying lens on a stalk above his hair, a dark green-grey academy long coat with gold buttons and a brass H buckle on a brown belt, black boots, an orange hextech multitool in one hand and a grey-green wrench with a red ball in the other; 1T his SMALL TURRET from the front: a grey-purple block body with a big red octagonal muzzle, pale grey-green shoulder plates with vents, two thick pale green exhaust stacks angled up, a red ball on top, four mechanical legs splayed with red block feet; 1X his APEX TURRET from the front: a grey body with a barrel and a red muzzle, a big pale grey-green gear on each side, two pale green bent pipes with red bands, a red ball on a stalk, a red ring turntable and three short legs - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A, 2T and 2X the same pictures cut down to the RIGHT square count - the inventor 54 squares from the top of his hair to his soles, the small turret 30, the apex turret 45 - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A, 3T and 3X the same with grid lines every 5 squares: orange = the top, blue = the goggles, red = the ground; 4 the inventor's head enlarged; 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a big-headed yordle's face and hair and a hextech machine are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels. Do NOT shrink a bigger drawing: draw at this size.
With this few squares make every part READ. THE INVENTOR: TWO red-rimmed GOGGLES of the SAME size at the SAME height, each about 5x5 squares - a 2-shade red rim round a 2-3-shade cyan lens with 1-2 WHITE highlight squares; a small pink nose between them; the big WHITE MOUSTACHE curling out to both sides in 2-3 off-white shades, strand by strand; the orange pointed ear in 3 shades; the golden mane in 4 shades - ORANGE-BROWN shadows, PALE YELLOW lit curls, tuft by tuft, never one yellow mass - with two pointed tufts on top and the red-rimmed magnifying lens on its stalk; the dark green-grey coat in 3 shades with a row of small gold buttons and the brass H buckle; the orange multitool as a clear block; the grey-green wrench with its open jaw and red ball; two separate black-grey boots. THE TURRETS: grey bodies in 3 shades, pale grey-green plates, stacks, gears and pipes in 3, red muzzles and balls in 3, the legs and joints clear, the gear teeth separate; left-right symmetric.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`heimerdinger-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: the INVENTOR's idle exactly as images 1A, 2A and 3A - standing in 3/4 view facing right, the face to the front-right with both goggles visible, the multitool in his hand on the image left and the wrench in his hand on the image right, both boots on the ground line with a clear gap between them. Every square exactly 20 px; the top of his hair at y 100, his goggles at about y 520, his soles on y 1180 - exactly 54 squares tall, about 52 squares wide.
  ```
- **T（`heimerdinger-model-T.png`，一稿）**：
  ```text
  PICTURE T: the SMALL TURRET exactly as images 1T, 2T and 3T - seen from the FRONT, the big red octagonal muzzle pointing straight at the viewer, left-right symmetric, the two exhaust stacks angled up, the four legs splayed with their red feet on the ground line. Every square exactly 28 px; the red ball on top at y 336, the feet on y 1176 - exactly 30 squares tall, about 38 squares wide.
  ```
- **X（`heimerdinger-model-X.png`，一稿）**：
  ```text
  PICTURE X: the APEX TURRET exactly as images 1X, 2X and 3X - seen from the FRONT, the barrel and its red muzzle pointing straight at the viewer, left-right symmetric, a big gear on each side, the red ring turntable and the three short legs with their feet on the ground line. Every square exactly 24 px; the red ball on top at y 96, the feet on y 1176 - exactly 45 squares tall, about 42 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 20 px、54 格高；T 每格 28 px、30 格高；X 每格 24 px、45 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 黑默丁格：两只护目镜一样大、一样高、带白色高光；白胡子、耳朵、头发 4 档不糊、放大镜、扳手、工具清楚；两只靴子分开。
- 两座炮台：正面、左右对称；小炮台四条腿两根排气筒，巨型炮台两边齿轮三条腿。外描边连续；没有任何技能特效。

## 交付（`outputs/heimerdinger-model/`）

- `heimerdinger-model-A-1.png`、`heimerdinger-model-A-2.png`、`heimerdinger-model-T.png`、`heimerdinger-model-X.png`；原始生成图原样放 `outputs/heimerdinger-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/heimerdinger_model_done.zip`。中间不要停，四张都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 20 px / 54 行，T 约 28 px / 30 行，X 约 24 px / 45 行），从 raw/ 按格读回（regrid），在游戏大小下和薇古丝、吉格斯、提莫、维迦并排自查（PPU 1.5：他 36、炮台 20、巨型炮台 30 游戏像素），把 A 两稿给用户挑。
- 动作帧由 Claude 自己照英雄联盟的动作拼（`tools/lol/anim_graph.py Heimerdinger`，`pose_ref.py --champ Heimerdinger`；炮台 `--champ HeimerTYellow --wad Heimerdinger`，巨型炮台 `HeimerTBlue`）；腿和待机一致、不变形；一张脸用在所有帧。数据里的动作名见 `tools/kit/build_heimerdinger.py` 和 PICTURE_PROMPT.md 最后一节。
