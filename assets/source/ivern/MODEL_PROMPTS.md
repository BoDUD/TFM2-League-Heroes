# 翠神 艾翁：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的两张（`1_picture_A.png` 艾翁 3/4、`1_picture_D.png` 小菊）**样子、颜色用户认可了，全照它们**。
> - 这一步要画成**游戏里的格子数**：**艾翁从蘑菇顶到脚底 60 格**，**小菊从头顶嫩芽到脚底 60 格**。我把两张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、鼻子、笑脸、树叶胡子、花纹碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，撑满画布**。画布用你平时的 **1254 × 1254**，两张的格子大小不一样（为了都撑满画布）：**A 每格 18 px**，**D 每格 15 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**三张**：**A 两稿**（A-1 / A-2）、**D 一稿**。只要 3/4 面，**不画侧面**。**小菊要画成正面、左右对称**（第 0 步她稍微侧转了，这一步扶正）。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（艾翁 3/4，朝右）**：每格 **18 px**；照 `2_target_A.png` / `3_layout_A.png`：蘑菇顶 **y = 108**（橙线），眼睛约 **y = 378**（蓝线），脚底 **y = 1188**（红线）：**60 格高、约 64 格宽**（羊角、树枝、苹果算在宽里）。
- **D（小菊，正面）**：每格 **15 px**；照 `2_target_D.png` / `3_layout_D.png`：头顶嫩芽 **y = 285**，脚底 **y = 1185**：**60 格高、约 78 格宽**。
- 全在画布里，羊角、树枝、苹果、拳头不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **艾翁的脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：浅灰白树皮色的小圆脸（3 档，暗处偏灰绿）；**两只琥珀色眼睛一样大、一样高、都露出来**，每只约 **3 × 3 格**（深色瞳孔 + 1 格亮黄高光，上面一道深色眉弓）——远的那只**不要被鼻子挡住一半**；**大鼻子**从两眼中间往下伸（浅白 2 档）；**咧嘴笑**，露 2–3 格白牙。
- **头上**：**红色蘑菇带白点**（红 2 档 + 白点）；两只**浅灰绿羊角**往两边伸再往上卷（3 档，角上的纹路用最暗一档画 2–3 道，不要碎点）；左耳边挂一个**小木环**。
- **树叶胡子**：一大把亮绿叶子从嘴下面垂到腰，**4 档**：暗处墨绿、亮处黄绿，**一片一片叶子的尖朝下分开**，不要糊成一片绿。
- **身体**：棕色木头身子（3–4 档，亮处橙棕），腰上树叶裙（绿 3 档），身前一道白色布条；画面左边的手臂举着一根**带两片叶子的小树枝**，手腕上**两道金色木环**；画面右边的手托着一个**红苹果**（红 2 档 + 1 格高光 + 绿叶梗）。
- **两条腿分开站**：深红棕树皮（3 档），**近的腿（画面左）全亮、远的腿（画面右）暗一档**；近的小腿上长着**两三颗红浆果**；脚是**分叉的树根**，两只根脚都踩在地面线上。
- **小菊 D**：**正面、左右对称**；弓着背，大块的**青苔绿石头**（3–4 档）和**淡紫灰石面**（2–3 档），石面上刻着**螺旋纹**（最暗的绿 1 档，每个螺旋 1 格宽的线）；头是**深灰色的尖石块**嵌在两肩中间，头顶冒一株**三叶草嫩芽**（绿 2 档，画清楚，在最高处）；胸口**两朵小白花**（白 2 档 + 黄心）对称地开在两边，正中一颗**绿色小水晶**（亮绿 2 档 + 高光）；两只**巨大的石拳**垂到膝盖两边；两条**短粗的石头腿**分开站。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的茂凯、婕拉、加里奥，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `ivern_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_D.png` | 你第 0 步画的艾翁和小菊（用户认可） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_D.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_D.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的艾翁头部（8 倍） | 脸、眼睛、鼻子、蘑菇、羊角、胡子 |
| `style/5_style_maokai.png`、`6_style_zyra.png`、`7_style_galio.png` | 本包的茂凯、婕拉、加里奥，8 倍放大 | **只看风格**：这么粗的格子里树人的木头和叶子、植物、石头大块头怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1D your own earlier pixel-art drawings - 1A a walking tree-man in 3/4 view facing right: a small round face of pale grey-white bark with small amber eyes, a big nose and a wide grin, a huge beard of bright green leaves, two pale sage-green ram's horns curling out to the sides, a red white-spotted mushroom on his crown, a brown wooden body with a leaf skirt, a branch arm holding up a twig with two leaves, the other holding a red apple, two dark red-brown bark legs apart on forked root feet, red berries on one shin; 1D his ROCK GOLEM DAISY: a big hunched golem of mossy green stones and pale violet-grey stone faces with carved spirals, two small white flowers and a small green crystal on the chest, a dark grey pointed stone head sunk between the shoulders with a clover sprout on top, two huge stone fists, short thick legs - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A and 2D the same pictures cut down to the RIGHT square count - the tree-man 60 squares from the top of his mushroom to his soles, the golem 60 from her sprout to her feet - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A and 3D the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the tree-man's head enlarged; 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a tree creature's wood and leaves, a plant creature and a big stone figure are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels. Do NOT shrink a bigger drawing: draw at this size.
With this few squares make every part READ. THE TREE-MAN: the pale bark face in 3 shades; TWO AMBER EYES of the SAME size at the SAME height, BOTH fully visible (the far one NOT half hidden behind the nose), each about 3x3 squares - a dark pupil, one bright yellow highlight square, a dark brow line above; a BIG pale NOSE between and below them; a GRIN showing 2-3 white tooth squares; the red mushroom with white spots; the pale sage horns in 3 shades with 2-3 clean dark grooves; the leaf beard in 4 greens - DEEP GREEN shadows, YELLOW-GREEN lit - leaf by leaf with the tips pointing down, never one green mass; the brown wooden body in 3-4 shades; the leaf skirt; the twig with two leaves and two gold rings at the wrist; the red apple with one highlight square and a green leaf; two bark legs APART, the near one (image left) full tone, the far one (image right) one shade darker, berries on the near shin, forked root feet on the ground line. THE GOLEM: seen from the FRONT, LEFT-RIGHT SYMMETRIC; mossy green stones in 3-4 shades and pale violet-grey stone faces in 2-3 with 1-square dark green spiral grooves; the small dark grey pointed head between the shoulders with a clear green clover sprout at the very top; two white flowers with yellow centres placed symmetrically on the chest and the bright green crystal in the middle; two huge stone fists hanging at her sides; two short thick legs apart.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`ivern-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: the TREE-MAN's idle exactly as images 1A, 2A and 3A - standing in 3/4 view facing right, the face to the front-right with both eyes visible, the twig raised in his hand on the image left and the apple in his hand on the image right, both root feet on the ground line with a clear gap between the legs. Every square exactly 18 px; the top of his mushroom at y 108, his eyes at about y 378, his soles on y 1188 - exactly 60 squares tall, about 64 squares wide.
  ```
- **D（`ivern-model-D.png`，一稿）**：
  ```text
  PICTURE D: the ROCK GOLEM exactly as images 1D, 2D and 3D but turned to face the viewer straight on - seen from the FRONT, LEFT-RIGHT SYMMETRIC, hunched, the head and sprout in the middle, both fists hanging at her sides, both legs on the ground line. Every square exactly 15 px; the top of the sprout at y 285, the feet on y 1185 - exactly 60 squares tall, about 78 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 18 px、60 格高；D 每格 15 px、60 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 艾翁：两只琥珀色眼睛一样大、一样高、都露出来、带高光；大鼻子、笑脸露牙；蘑菇、羊角、树叶胡子 4 档不糊；树枝、苹果清楚；两条腿分开，近亮远暗，根脚踩地。
- 小菊：正面、左右对称；头顶三叶草嫩芽清楚；两朵白花 + 绿水晶；螺旋纹是干净的线；两只大石拳。外描边连续；没有任何技能特效。

## 交付（`outputs/ivern-model/`）

- `ivern-model-A-1.png`、`ivern-model-A-2.png`、`ivern-model-D.png`；原始生成图原样放 `outputs/ivern-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ivern_model_done.zip`。中间不要停，三张都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 18 px / 60 行，D 约 15 px / 60 行），从 raw/ 按格读回（regrid），脸在 12 倍下看，在游戏大小下和沃里克、乌迪尔、奇亚娜并排自查（PPU 1.5：他和小菊都是 40 游戏像素），把 A 两稿给用户挑。
- 动作帧：用户决定是 Claude 照英雄联盟的动作拼，还是 Codex 照骨架画姿势（`tools/lol/anim_graph.py Ivern`，`pose_ref.py --champ Ivern --hide-submeshes`；小菊 `--champ IvernMinion --wad Ivern`）；一张脸用在所有帧。数据里的动作名见 `tools/kit/build_ivern.py` 和 PICTURE_PROMPT.md 最后一节。
