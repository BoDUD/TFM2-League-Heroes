# 海兽祭司 俄洛伊：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的两张（`1_picture_A.png` 俄洛伊 3/4、`1_picture_T.png` 触手）**样子、颜色用户认可了，全照它们**。
> - 这一步要画成**游戏里的格子数**：**俄洛伊从发髻顶到脚底 63 格**（肩上的神像再高出约 4 格，整个人 67 格高），**触手从卷钩顶到根部石块底 66 格**。我把两张图直接缩到这个格子数（`2_target_*.png`）：**大小、位置、姿势对，细节是缩坏的**（眼睛、鼻环、神像花纹、触手螺旋纹碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，撑满画布**。画布用你平时的 **1254 × 1254**，两张都是 **每格 17 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**三张**：**A 两稿**（A-1 / A-2）、**T 一稿**。只要 3/4 面，**不画侧面**。**触手画正面**，站直居中，卷钩可以往一边卷。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_*.png` 的浅灰线每 5 格一条）。
- **A（俄洛伊 3/4，朝右）**：每格 **17 px**；照 `2_target_A.png` / `3_layout_A.png`：神像顶 **y = 51**（橙线），发髻顶约 **y = 119**，眼睛约 **y = 289**（蓝线），脚底 **y = 1190**（红线）：**67 格高、约 50 格宽**（神像算在宽里）。
- **T（触手，正面）**：每格 **17 px**；照 `2_target_T.png` / `3_layout_T.png`：卷钩顶 **y = 68**（橙线），根部石块底 **y = 1190**（红线）：**66 格高、约 34 格宽**。
- 全在画布里，神像、卷钩、背鳍不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **俄洛伊的脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：深棕色皮肤（3 档，亮处暖橙棕）；**两只绿眼睛一样大、一样高、都露出来**，每只约 **2 × 2 到 3 × 2 格**（亮绿 + 1 格浅色高光），上面一道**浓黑眉**；眼睛周围**不要糊一片绿色光**，绿只在眼睛里，最多眼角一格；**金鼻环**一格亮金在鼻尖下；嘴一道深色短线，抿着或带一点自信的笑；**金耳环**一格。
- **头发**：黑色（2–3 档，亮处深蓝灰），**发髻高高扎在头顶**，套一个**金环**（2 格），几缕辫子从后脑垂到肩后。
- **神像**：一个**大的金色圆盘**扛在**远处的肩上**（画面左边、她的头后面），**不挡脸**；金 4 档（暗处橄榄棕，亮处浅黄）；正面刻着**青绿色的螺旋眼**（亮绿 2 档，螺旋线 1 格宽、连贯，不要碎点）；右侧一排**扇形的金色凸起**。一只手从下面托着它。
- **身体**：宽肩、结实；**金色护肩、金领圈**；胸口**青绿色的布**（3 档）上面几道金色饰片；**露出的手臂肌肉结实**（皮肤 3–4 档），近处（画面右）的手臂上有**青绿色螺旋纹身**，前臂套着**大的金色护腕**，拳头叉在腰上；**金色腰带** + **暗红色腰布**（2–3 档）从中间垂下；腰两边一圈**灰绿色的布裙**。
- **两条腿分开站稳**：粗壮的大腿（皮肤深棕），**近的腿（画面左）全亮、远的腿（画面右）暗一档**；**墨绿色高靴**（3 档）带金色绑带，两只脚都踩在地面线上。
- **触手 T**：**深海绿**（背上暗、肚子亮青绿，3–4 档），身上**浅青色发光的螺旋纹**（1–2 档，每道 1 格宽、连贯成螺旋，不要碎点）；**背上一排鳍状尖齿**（深一档）；**尖端卷成一个钩**，钩的里面空出来看得见；根部一圈**灰褐色的碎石块**（2 档），在地面线上。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的奎桑提、尼菈、娜美，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `illaoi_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` / `1_picture_T.png` | 你第 0 步画的俄洛伊和触手（用户认可） | **样子、颜色、细节、姿势**全照它们 |
| `2_target_A.png` / `2_target_T.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` / `3_layout_T.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的俄洛伊头部（8 倍） | 脸、眼睛、鼻环、发髻、金环 |
| `style/5_style_ksante.png`、`6_style_nilah.png`、`7_style_nami.png` | 本包的奎桑提、尼菈、娜美，8 倍放大 | **只看风格**：这么粗的格子里深肤色和金甲、Q 版女战士的脸、海洋青绿怎么画 |

## 提示词（两种，每种换最后一段）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A and 1T your own earlier pixel-art drawings - 1A a tall strong priestess in 3/4 view facing right: dark brown skin, black hair in a high bun with a gold ring and braids down her back, green eyes, thick brows, a gold nose ring and a gold earring; gold shoulder plates and a gold collar, a teal chest wrap with gold plates, bare muscular arms (a teal spiral tattoo on the near one), big gold bracers, a gold belt and a dark red loincloth over a grey-green cloth skirt, dark green tall boots; a BIG ROUND CARVED GOLD IDOL with a glowing teal spiral eye resting on her FAR shoulder behind her head, one hand under it, the other fist on her hip; 1T her TENTACLE: a thick deep sea-green tentacle rising out of a ring of grey-brown stones, its tip curled into a hook, a row of fin spikes along its back, pale aqua spiral patterns on its lighter belly - their LOOK and COLOURS are approved, but they are drawn with far too many small squares; 2A and 2T the same pictures cut down to the RIGHT square count - the priestess 63 squares from the top of her hair bun to her soles (the idol 4 more above), the tentacle 66 from its hook to its root - shown with big squares on a 1254x1254 canvas: their SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke their details; 3A and 3T the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the priestess's head enlarged; 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how dark skin and gold armour, a chibi woman's face and sea-green shades are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner (the square size and lines are given below); the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels. Do NOT shrink a bigger drawing: draw at this size.
With this few squares make every part READ. THE PRIESTESS: the dark brown skin in 3-4 shades (warm orange-brown lit); TWO GREEN EYES of the SAME size at the SAME height, BOTH visible, each about 2x2 to 3x2 squares - bright green with one light highlight square - and a thick black brow above each; NO green glow smeared round the eyes (the green only in the eyes); the gold nose ring one bright gold square under the nose tip; a short dark mouth line; one gold earring square; the black hair in 2-3 shades with the HIGH BUN on top and its gold ring; the big round GOLD IDOL on her far shoulder behind her head (never over the face) in 4 golds - olive-brown shadows, pale yellow lit - with a clean TEAL SPIRAL EYE of 1-square lines and the fan of gold ridges on its side, her hand under it; gold shoulder plates and collar; the teal chest wrap in 3 shades with gold plates; strong bare arms, the teal spiral tattoo on the near arm, the big gold bracer, the fist on her hip; the gold belt, the dark red loincloth hanging in the middle, the grey-green cloth skirt; two strong legs APART, the near one (image left) full tone, the far one (image right) one shade darker; dark green boots with gold straps, both feet on the ground line. THE TENTACLE: seen from the FRONT, standing straight up in the middle; deep sea-green in 3-4 shades - dark on its back, lighter teal-green on its belly - with pale aqua spiral patterns of 1-square lines that read as spirals; the fin spikes along its back one shade darker; the tip curled into a clear HOOK with the open space inside it; a ring of grey-brown stones at its root on the ground line.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines.
```

最后一段，按要画的那一张换：

- **A（`illaoi-model-A-1.png`、`-A-2.png`，两稿）**：
  ```text
  PICTURE A: the PRIESTESS's idle exactly as images 1A, 2A and 3A - standing in 3/4 view facing right, the face to the front-right with both eyes visible, the gold idol on her far shoulder (image left, behind her head) held from below, the near fist on her hip, both feet on the ground line with a clear gap between the legs. Every square exactly 17 px; the top of the idol at y 51, the top of her hair bun at about y 119, her eyes at about y 289, her soles on y 1190 - exactly 67 squares tall in all (63 from the bun to the soles), about 50 squares wide.
  ```
- **T（`illaoi-model-T.png`，一稿）**：
  ```text
  PICTURE T: the TENTACLE exactly as images 1T, 2T and 3T - seen from the FRONT, standing straight up out of its root stones in the middle of the canvas, the tip curled into a hook at the top, the fin spikes along its back, the root stones on the ground line. Every square exactly 17 px; the top of the hook at y 68, the bottom of the root stones on y 1190 - exactly 66 squares tall, about 34 squares wide.
  ```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：A 每格 17 px、67 格高（发髻到脚底 63 格）；T 每格 17 px、66 格高（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 俄洛伊：两只绿眼睛一样大、一样高、都露出来、带高光，**眼睛周围不糊绿光**；浓眉、金鼻环、金耳环；高发髻 + 金环；神像扛在远处肩上、不挡脸，螺旋眼是干净的线；手臂结实、纹身、金护腕；暗红腰布；两条腿分开，近亮远暗，靴子踩地。
- 触手：正面站直；深海绿背暗肚亮；螺旋纹是干净的线；背鳍；卷钩里面空出来；根部石块。外描边连续；没有任何技能特效。

## 交付（`outputs/illaoi-model/`）

- `illaoi-model-A-1.png`、`illaoi-model-A-2.png`、`illaoi-model-T.png`；原始生成图原样放 `outputs/illaoi-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/illaoi_model_done.zip`。中间不要停，三张都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（A 约 17 px / 67 行，T 约 17 px / 66 行），从 raw/ 按格读回（regrid），脸在 12 倍下看，在游戏大小下和奎桑提、德莱厄斯、格温并排自查（PPU 1.5：她发髻到脚底 42、触手 44 游戏像素），把 A 两稿给用户挑。
- 动作帧：用户决定是 Claude 照英雄联盟的动作拼，还是 Codex 照骨架画姿势（`tools/lol/anim_graph.py Illaoi`，`pose_ref.py --champ Illaoi`，**不要** `--hide-submeshes`；触手 `--champ IllaoiMinion --wad Illaoi`）；一张脸用在所有帧。数据里的动作名见 PICTURE_PROMPT.md 最后一节。
