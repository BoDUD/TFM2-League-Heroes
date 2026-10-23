# 沙漠皇帝 阿兹尔：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的四张（`1_picture_A.png` 阿兹尔 3/4、`1_picture_T.png` 黄沙士兵正面、`1_picture_US.png` 禁军侧面、`1_picture_D.png` 太阳圆盘）**样子、颜色用户认可了，全照它们**。只改一处：**权杖短一些**（杖头比冠羽高约 14 格，第 0 步高了 23 格），`2_target_A.png` 已经截短了杖身。
> - 这一步要画成**游戏里的格子数**：**阿兹尔从鹰盔冠羽顶到脚底 57 格**（权杖头再高约 14 格，整个人约 71 格高）；**沙兵从矛尖到脚底 54 格**；**禁军（侧面）从盾顶到脚底 48 格**；**太阳圆盘从徽章顶到底座尖 72 格**。我把四张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、宝石、鹰嘴、盾上刻纹、徽章花纹碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，撑满画布**。画布用你平时的 **1254 × 1254**；每张的格子大小不一样（见下面），每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**五张**：**A 两稿**（A-1 / A-2）、**T、US、D 各一稿**。只要 3/4 面，**阿兹尔不画侧面**。禁军只画**朝右**的侧面（朝左的我自己翻）。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（阿兹尔 3/4，朝右）**：每格 **16 px**；照 `2_target_A.png` / `3_layout_A.png`：权杖头顶 **y = 54**（橙线），鹰盔冠羽顶约 **y = 278**，眼睛约 **y = 470**（蓝线），脚底 **y = 1190**（红线）：**约 71 格高、约 50 格宽**（权杖算在里面）。
- **T（黄沙士兵，正面）**：每格 **20 px**；矛尖 **y = 110**（橙线），脚底 **y = 1190**（红线）：**54 格高、约 30 格宽**。
- **US（禁军，侧面朝右）**：每格 **22 px**；盾顶 **y = 132**（橙线），脚底 **y = 1188**（红线）：**48 格高、约 36 格宽**。
- **D（太阳圆盘，正面）**：每格 **16 px**；徽章顶 **y = 32**（橙线），底座尖 **y = 1184**（红线）：**72 格高、约 48 格宽**。
- 全在画布里，权杖、矛尖、盾、弯角不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **阿兹尔的头**（`4_head.png` 是第 0 步读回的鹰盔，8 倍）：**没有人脸**，就是一顶**鹰首金盔**：前面一个**清楚的鹰嘴**（尖朝右下），头顶**冠羽**，两颊各一片**金色翅膀**；**发光的青蓝眼睛**在鹰嘴后面，**至少 2 × 2 格**（亮青 + 1 格近白高光），远处那只窄一点也要看得出；盔下面露出一点**深紫色兜帽**。
- **权杖**：竖着拿在**画面左边**那只手里，**不挡脸**；杖头**分叉成两片金色尖刃**，中间夹一颗**青蓝宝石**，下面一道金色横档两端各一颗小宝石；杖身金色带一颗宝石；杖头比冠羽高约 **14 格**。
- **身体**：金色铠甲 4 档（暗处古铜棕，亮处浅黄），**肩甲、胸口、腰两侧各一颗大的青蓝宝石**（每颗 3 × 3 格左右，带高光）；**深紫色**的袍子、披风和**短飘带**（3 档，飘带只到小腿、往后不超过 8 格）；胸前垂下**紫红色的布**；**小腿灰蓝色**；**金色护胫**；**两条腿分开站稳**，近的（画面左）全亮、远的（画面右）暗一档；另一只手张开放在身侧（金色爪状手甲）。
- **沙兵 T**：深棕皮肤（3 档）、**金色鹰首盔遮住整张脸**（盔顶尖角、面甲上一道暗缝）、**金色肩甲**、光着胸口、**深橄榄色披风**、腰上金色护片、**金色护胫**；**长矛竖在身旁**，**金色叶形矛头**在头盔上面；正对看画的人，左右大致对称。
- **禁军 US**：同样的士兵，**侧面朝右**，弓着身子，**肩膀顶在一面比他高的金色塔盾后面**，一条腿在前一条在后；**塔盾在画面右边**，长圆形、上圆下尖、中间一道竖脊、刻着弧形纹（暗一档的线）；头盔在盾的上半段旁边；深橄榄色的布裙。
- **太阳圆盘 D**：正面、左右对称；顶上一面**圆形徽章**（**紫红色圆面**，正中一只**金色鹰 / 太阳纹**，金边）；下面一个 **U 形金色托架**，两边伸出**弯角**；托架下面一段金色饰柱带**两颗紫红宝石**；最下面一块**倒三角的金色岩石底座**（暗金到棕 2–3 档），尖朝下踩在地面线上。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的泽拉斯、内瑟斯、奎桑提，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（沙子、光）。

## 附图（压缩包 `azir_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `_T` / `_US` / `_D` | 你第 0 步画的阿兹尔、沙兵、禁军侧面、太阳圆盘（用户认可） | **样子、颜色、细节、姿势**全照它们（A 的权杖照 2A 截短） |
| `2_target_A.png` / `_T` / `_US` / `_D` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `_T` / `_US` / `_D` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的鹰盔（8 倍） | 鹰嘴、冠羽、金翅膀、青蓝眼睛 |
| `style/5_style_xerath.png`、`6_style_nasus.png`、`7_style_ksante.png` | 本包的泽拉斯、内瑟斯、奎桑提，8 倍放大 | **只看风格**：这么粗的格子里恕瑞玛的金色、发光的青蓝、兽首、深肤色和金甲怎么画 |

## 提示词（四种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A, 1T, 1US and 1D your own earlier pixel-art drawings - 1A a tall regal emperor in 3/4 view facing right: his head a FALCON-HEADED GOLD HELMET (a beak, a crest, a gold wing on each cheek, glowing teal eyes, no human face), gold armour with big teal gems on the shoulders, the chest and the hips, a deep purple robe, cape and short ribbons, a magenta cloth down his front, grey-blue lower legs, gold greaves, a long gold sceptre with a forked head round a teal gem held upright in the hand on the image left; 1T a dark-skinned SAND SOLDIER from the front: a gold falcon helmet covering the face, gold shoulder plates, a bare chest, a dark olive cape, gold greaves, a long spear with a gold leaf-shaped blade upright beside him; 1US the same soldier as an IMPERIAL GUARD from the side facing right, crouched with his shoulder behind a tall gold tower shield on the image right; 1D the SUN DISC from the front: a round magenta emblem with a gold falcon-sun in a gold rim, on a U-shaped gold cradle with curved horns, a gold column with two magenta gems, an inverted-triangle gold rock base - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A, 2T, 2US and 2D the same pictures cut down to the RIGHT square count - the emperor 57 squares from his helmet's crest to his soles (the sceptre's head about 14 more above it: its shaft shortened), the soldier 54 from the spear tip to his soles, the guard 48 from the shield's top to his soles, the disc 72 from the emblem's top to the base's tip - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A, 3T, 3US and 3D the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the emperor's helmet enlarged; 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how gold armour, glowing teal, an animal head, dark skin are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels. Do NOT shrink a bigger drawing: draw at this size.
With this few squares make every part READ. THE EMPEROR: no human face - the FALCON HELMET with a clear BEAK pointing down-right, the CREST on top and a gold WING on each cheek; the GLOWING TEAL EYE behind the beak at least 2x2 squares with one near-white highlight square, the far eye narrower but readable; a little deep purple hood under the helmet; the SCEPTRE upright in the hand on the image left, never over the face, its head two gold blades forked round a teal gem with a gold crossbar and a small gem at each end, its head about 14 squares above the crest; gold armour in 4 shades (bronze-brown shadows, pale yellow lit) with BIG TEAL GEMS (about 3x3 squares each, with a highlight) on the shoulders, the chest and the hips; the deep purple robe, cape and SHORT ribbons (down to his calves, no more than 8 squares behind him) in 3 shades; the magenta cloth down his front; grey-blue lower legs; gold greaves; the two legs APART, the near one (image left) full tone, the far one (image right) one shade darker; the other hand open at his side in a gold clawed gauntlet. THE SOLDIER: dark brown skin in 3 shades, the gold falcon helmet covering his whole face (a pointed top, a dark slit), gold shoulder plates, a bare chest, a dark olive cape, a gold plate at the waist, gold greaves, the long spear upright beside him with its gold leaf blade above the helmet; facing the viewer, about symmetric. THE GUARD: the same soldier seen from the side facing right, crouched, his shoulder pressed behind a TALL GOLD TOWER SHIELD on the image right (long and rounded, round top and pointed bottom, a vertical ridge, curved carved lines one shade darker), one leg forward and one back, a dark olive cloth skirt. THE DISC: from the front, symmetric left and right: the round MAGENTA EMBLEM with a GOLD FALCON-SUN in the middle and a gold rim on top, the U-shaped gold cradle with a curved horn on each side under it, a gold column with two magenta gems, the inverted-triangle gold rock base (dark gold to brown in 2-3 shades) with its tip on the ground line.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects (no sand, no light), no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`azir-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: the EMPEROR's idle exactly as images 1A, 2A and 3A - standing tall in 3/4 view facing right, the helmet's beak to the front-right with the near eye glowing, the shortened sceptre upright in the hand on the image left, the other hand open at his side, the short ribbons behind him, both feet on the ground line with a clear gap between the legs. Every square exactly 16 px; the top of the sceptre at y 54, the top of the helmet's crest at about y 278, the eyes at about y 470, his soles on y 1190 - about 71 squares tall in all (57 from the crest to the soles), about 50 squares wide.
  ```
- **T（`azir-model-T.png`，一稿）**：
  ```text
  PICTURE T: the SAND SOLDIER exactly as images 1T, 2T and 3T - seen from the FRONT, standing ready in the middle of the canvas, the spear upright beside him with its gold blade above his helmet, both feet on the ground line. Every square exactly 20 px; the spear's tip at y 110, his soles on y 1190 - exactly 54 squares tall, about 30 squares wide.
  ```
- **US（`azir-model-US.png`，一稿）**：
  ```text
  PICTURE US: the IMPERIAL GUARD exactly as images 1US, 2US and 3US - seen from the SIDE facing right, crouched behind the tall gold tower shield on the image right, pushing with his shoulder, one leg forward and one back, the shield's bottom and both feet on the ground line. Every square exactly 22 px; the top of the shield at y 132, the ground on y 1188 - exactly 48 squares tall, about 36 squares wide.
  ```
- **D（`azir-model-D.png`，一稿）**：
  ```text
  PICTURE D: the SUN DISC exactly as images 1D, 2D and 3D - seen from the FRONT, symmetric, the round emblem at the top, the horned cradle, the gemmed column and the rock base with its tip on the ground line. Every square exactly 16 px; the top of the emblem at y 32, the base's tip on y 1184 - exactly 72 squares tall, about 48 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 16 px、约 71 格高（冠羽到脚底 57 格）；T 每格 20 px、54 格；US 每格 22 px、48 格；D 每格 16 px、72 格（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 阿兹尔：鹰盔有清楚的鹰嘴、冠羽、两颊金翅膀；**发光的青蓝眼睛**至少 2 × 2 带高光；**权杖短了**（杖头比冠羽高约 14 格）、在画面左边、不挡脸；大青蓝宝石带高光；深紫袍子披风、**飘带短**；灰蓝小腿、金护胫；两条腿分开，近亮远暗，脚踩地。
- 沙兵正面、长矛竖着；禁军侧面朝右、塔盾在右、人弓身顶在盾后；圆盘正面左右对称。外描边连续；没有任何技能特效。

## 交付（`outputs/azir-model/`）

- `azir-model-A-1.png`、`azir-model-A-2.png`、`azir-model-T.png`、`azir-model-US.png`、`azir-model-D.png`；原始生成图原样放 `outputs/azir-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/azir_model_done.zip`。中间不要停，五张都画完再交。**不要另做平滑缩小的"修复版"**，也不要另做 `logical/` 缩小图。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 16 px / 71 行，T 20 / 54，US 22 / 48，D 16 / 72），从 raw/ 按格读回（regrid，尺寸给得比实际格子略大），鹰盔在 12 倍下看（鹰嘴、眼睛），在游戏大小下和泽拉斯、阿萝拉、彗并排自查（PPU 1.5：冠羽到脚底 38、沙兵 36、禁军 32、圆盘 48 游戏像素），把 A 两稿给用户挑；US 左右翻一份做朝左的禁军。
- 动作帧：用户决定是 Claude 照英雄联盟的动作拼，还是 Codex 照骨架画姿势（`tools/lol/anim_graph.py Azir`，`pose_ref.py --champ Azir`；召唤物 `--champ AzirSoldier / AzirUltSoldier / AzirSunDisc --wad Azir`）；一个鹰盔用在所有帧。数据里的动作名见 PICTURE_PROMPT.md 最后一节。
