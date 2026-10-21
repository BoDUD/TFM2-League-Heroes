# 万花通灵 妮蔻：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 `1_picture_A.png`（妮蔻 3/4 朝右）**样子、颜色、服装用户认可了，全照它**。侧面这一步不画（用户只要 3/4）。
> - **用户要她的头画大一点**（Q 版：头发连脸约占身高的三分之一，羽刺另算），身子保持苗条。`2_target_A.png` 已经按新比例拼好（头放大了 1.35 倍）：**比例、大小、位置、姿势照它**。
> - 这一步要把她画成**游戏里的格子数**：**从最高的羽刺尖到脚底 100 格**。`2_target_A.png` 是直接缩到这个格子数的：**细节是缩坏的**（眼睛、嘴、百合花、贝壳腰带、腿上的螺旋纹碎成杂点）。请像一个像素画师照着第 0 步的图，在这个格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，**每格 11 px**。每一格都是一个完整的方块，不要用更小的格子画细节。
> - 一共画**两稿**：A-1 / A-2。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- 每格 **11 px**；照 `2_target_A.png` / `3_layout_A.png`：最高的羽刺尖 **y = 110**（橙线），眼睛约 **y = 418**（蓝线），脚底 **y = 1210**（红线）：**100 格高、约 47 格宽**。
- 全在画布里，羽刺、头发、尾巴不出画，四周留至少 1 格空。

## 要画清楚的地方

- **脸**（`4_head.png` 是第 0 步读回的头部，8 倍）：浅桃色的小脸，额头和两颊几格青绿色小鳞片；**两只黄色的大眼睛**：近处那只约 **4 × 4 格**，远处那只至少 **3 × 4 格**，**一样高**，深色竖瞳、各带 **1–2 格白色高光**；粉色的小嘴（2 格宽）；紫蓝色的刘海盖住额头，两边头发往外翘。
- **头**：紫蓝色头发 3–4 档加几缕品红；**品红紫的羽刺**一根根分开（中段亮粉、根部青绿），**不挡脸**；太阳穴的**珊瑚粉百合花**（花瓣分得清）、另一边耳下一朵小的。
- **身体**：青绿色皮肤（手臂、肩）3 档，亮边偏薄荷绿；青蓝宝石项链；**珊瑚橙抹胸**带金色叶脉花纹；**两只手在胸前合着**，紫色手指；**白色贝壳珠的棕色腰带**（一颗颗珠子分开）；深棕短裤；橙色叶子形腰布垂在前面。
- **腿**：浅桃色大腿上**紫色螺旋纹**，小腿往下变青绿鳞片；深棕绑带加**金色环**；光脚、紫色脚趾。**近处的腿（画面左）全亮，远处的腿（画面右）暗一档**，两腿之间有空隙和描边分开，两只脚都踩在地面线上。
- **尾巴**：在身后（画面左边）**往上弯成一个钩，尾尖离地**；青绿色，背上一排紫色鳞，尾尖紫粉色。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的佐伊、萨勒芬妮、婕拉，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效。

## 附图（压缩包 `neeko_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的妮蔻（用户认可） | **样子、颜色、服装、细节**全照它 |
| `2_target_A.png` | 头放大后缩到游戏格子数、放大放在画布上（细节是坏的） | **比例（大头）、大小、位置、姿势** |
| `3_layout_A.png` | 加网格线：橙 = 最高点，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 眼睛、鳞片、嘴、百合花、羽刺 |
| `style/5_style_zoe.png`、`6_style_seraphine.png`、`7_style_zyra.png` | 本包的佐伊、萨勒芬妮、婕拉，8 倍放大 | **只看风格**：Q 版大头女孩的脸、眼睛、头发在格子上怎么画 |

## 提示词（A-1、A-2 用同一段，各画一次）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of a character in 3/4 view facing right - a curious chameleon-like lizard girl with green-teal scaled skin, a fluffy mop of violet-blue hair with magenta streaks, a crest of long thin magenta-violet quills (bright pink middle, teal root), coral-pink lilies at her temple and below the other ear, big yellow slit-pupil eyes, a small pale-peach face with a few teal scales, pink lips, a teal-blue gem necklace, a coral-orange woven top with gold leaf patterns, both hands held together in front of her chest with violet fingers, a brown belt of white shell beads, dark brown shorts, an orange leaf-shaped loincloth, pale peach thighs with violet swirls turning into teal scales down the shins, dark brown ankle wraps with gold rings, bare feet with violet toes and a long teal tail curling up behind her - its LOOK, COLOURS and OUTFIT are approved, but it is drawn with far too many small squares and its head is too small; 2 the same picture with the HEAD ENLARGED (chibi: hair and face about a third of her height) and cut down to the RIGHT square count - 100 squares from her highest quill tip to her soles - shown with big squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details; 3 the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5-7 STYLE ONLY: other characters from the same game, shown 8x so every square is one pixel - how a chibi girl's big head, face, eyes and hair are drawn on the grid.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). Squares of exactly 11 px aligned on one straight grid from the canvas corner; her highest quill tip at y 110, her eyes at about y 418, her soles on y 1210 - exactly 100 squares tall, about 47 squares wide, standing where image 2 shows her, with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
THE PROPORTIONS OF IMAGE 2: a BIG chibi head (hair and face about a third of her height, the quills on top), a slim short body, slim legs.
Make every part READ: the pale-peach face with a few teal scale squares on the forehead and cheeks; TWO BIG YELLOW EYES at the SAME height, the near one about 4x4 squares and the far one at least 3x4, each with a dark slit pupil and 1-2 WHITE highlight squares; a small pink mouth 2 squares wide; violet-blue bangs; the hair in 3-4 shades with magenta strands; the magenta-violet quills clearly separate (bright pink middle, teal root), NEVER covering the face; the coral-pink lilies with distinct petals; the green-teal skin of the arms and shoulders in 3 shades with MINT-GREEN lit edges; the teal-blue gem; the coral-orange top with gold patterns; both hands together in front of the chest, violet fingers; the brown belt with SEPARATE white shell beads; the dark brown shorts; the orange leaf loincloth; the pale peach thighs with violet swirls, teal scales down the shins; dark brown ankle wraps with gold rings; bare feet with violet toes; the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker, a clear gap and outline between the legs, both soles on the ground line; the long teal tail with violet top scales behind her on the image left, CURLING UP into a hook, its tip OFF the ground.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no background, no ground, no cast shadow, no text, no grid lines, no other characters.
```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：每格 11 px、**100 格高**（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）；脚底在 y 1210。
- **大头 Q 版**（头发连脸约占身高三分之一）；两只黄眼睛一样高、竖瞳、白色高光；粉色小嘴；羽刺一根根分开、不挡脸；百合花清楚。
- 贝壳珠一颗颗分开；腿上的紫色螺旋纹；近腿亮、远腿暗、两腿分开；尾巴往上弯、尾尖离地。外描边连续；没有任何技能特效。

## 交付（`outputs/neeko-model/`）

- `neeko-model-A-1.png`、`neeko-model-A-2.png`；原始生成图原样放 `outputs/neeko-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/neeko_model_done.zip`。中间不要停，两张都画完再交。

## 后面要用到的（这一步不画，心里有数就行）

动作帧由 Claude 照英雄联盟的动作逐帧拼：普攻（手里射出一颗魔法弹）、Q 扔种子、E 甩出一团倒刺、R 蓄力后跳起再落地、跑、挨打、倒下。所以**两只手臂、头、尾巴、两条腿要画得分得开**（手在胸前时和身体之间有描边分开），一张脸会用在所有帧。

## Claude 收到后（给 Claude 看）

- 量格子（约 11 px / 100 行），从 raw/ 按格读回（regrid），在游戏大小下和佐伊、薇古丝、辛德拉、婕拉并排自查（PPU 2.5：40 游戏像素高），脸在 12 倍下检查（眼睛、嘴是不是整格），把两稿给用户挑。
- PPU 2.5 要登记：ppu_hd PPU + 列表、ppu_restyle、hd.rs 一行（纳亚菲利 / 希瓦娜的行）。动作帧自己照英雄联盟拼（`tools/lol/anim_graph.py Neeko`，`pose_ref.py --champ Neeko --hide-submeshes`）。
