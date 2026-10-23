# 生化魔人 扎克：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小**。
> - 第 0 步你画的 3/4 待机原稿（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 这一步要画成**游戏里的格子数**：**从头顶触须的圆疙瘩顶到脚底 66 格**。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（身上的高光碎成迷彩一样的杂斑、眼睛和牙齿糊了）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - 第 0 步你的格子画得太细了（约 10–11 px 一格，整个角色约 79 格高）：这一步**每格画大，撑满画布**。画布用你平时的 **1254 × 1254**，**每格 13 px**（扎克很宽，约 88 格宽，13 px 才放得下）。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（A-1 / A-2），都是 3/4 正面朝右。**不画侧面**。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（扎克 3/4，朝右）**：每格 **13 px**；照 `2_target_A.png` / `3_layout_A.png`：触须顶 **y = 325**（橙线），眼睛约 **y = 624**（蓝线），脚底 **y = 1183**（红线）：**66 格高、约 88 格宽**（两只大手算在宽里）。
- 全在画布里，触须、两只大手不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

`4_head.png` 是第 0 步读回的头（8 倍），看位置和颜色。

- **眼睛**（最要紧）：**两只发黄光的眼睛一样大、一样高、都露出来**，每只约 **2 × 2 格**：橙黄 + 1 格近白的高光，外面一圈深色眼窝；眼睛上面一道深绿眉骨。
- **大嘴**：咧开的坏笑，嘴里**近黑的深绿**，上下各一排**深灰绿的尖牙**（三角形，一格一格，4–6 颗看得清），嘴角往上翘。
- **触须**：从头顶长出来，**1–2 格粗的深蓝绿弯茎**，往后上方卷一个弯，末端一个**约 4 × 3 格的圆疙瘩**（最深的一档）；茎和身体之间空出来看得见。
- **黏液身体**：亮绿 4 档；**高光是少而大的整块**（每块 2–4 格的黄绿亮斑，顺着肌肉的形状，像果冻反光），**不要满身迷彩一样的碎斑**；身体里面 **2–3 块深绿的内脏/纹路影子**（成块的，不是杂点）。
- **身体和四肢**：**宽大驼背**，头埋在两个大肩膀中间；**两条粗长的手臂**垂到膝盖附近，**三根粗手指的大手**（指头之间一格深色缝）；**短粗的腿**，**两只脚分开踩在地面线上**，脚趾 3 个圆圆的；**近的手臂和腿（画面左）全亮，远的（画面右）暗一档**；两条腿中间和腋下空出来看得见背景。
- **一圈 1 格的近黑（深墨绿黑）外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–7 一样的像素画（本包的科加斯、蒙多、沃利贝尔，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、黏液水洼、技能特效。

## 附图（压缩包 `zac_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的扎克原稿（用户认可） | **样子、颜色、细节、姿势**全照它 |
| `2_target_A.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` | 加网格线：橙 = 最高点（触须顶），蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head.png` | 第 0 步读回的头、触须、眼睛和嘴（8 倍） | 脸、牙、触须根 |
| `style/5_style_chogath.png`、`6_style_drmundo.png`、`7_style_volibear.png` | 本包的科加斯、蒙多、沃利贝尔，8 倍放大 | **只看风格**：这么粗的格子里大块头的肌肉、尖牙大嘴、大手怎么画 |

## 提示词（两稿用同一段）

附全部图。**用 image_gen 画。** A-1、A-2 各画一次（两次独立生成，挑好的）。

```text
Attached images: 1A your own earlier pixel-art drawing - ONE character in 3/4 view facing right: a HULKING, HUNCHED brute made of TRANSLUCENT BRIGHT GREEN SLIME, a small head sunk between huge shoulders with TWO GLOWING YELLOW EYES and a WIDE MISCHIEVOUS GRIN full of dark jagged teeth, a DARK BLUE-GREEN TENDRIL with a round knob curling up and back from the top of his head, HUGE LONG ARMS hanging near his knees with big three-fingered hands, SHORT THICK LEGS with round toes - its LOOK and COLOURS are approved, but it is drawn with far too many small squares; 2A the same picture cut down to the RIGHT square count - 66 squares from the top of the tendril's knob to the soles - shown with big squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke the details (the highlights turned into camouflage noise, the eyes and teeth blurred); 3A the same with grid lines every 5 squares: orange = the top, blue = the eyes, red = the ground; 4 his head enlarged; 5-7 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a big monster's muscles, a toothy grin and big hands are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES aligned on one straight grid from the canvas corner, every square exactly 13 px; the figure filling its place on the canvas with at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels. Do NOT shrink a bigger drawing: draw at this size.
With this few squares make every part READ. THE EYES: TWO GLOWING YELLOW EYES of the SAME size at the SAME height, BOTH visible, each about 2x2 squares - orange-yellow with one near-white highlight square, a dark socket round each, a dark green brow ridge above. THE GRIN: a wide mouth, very dark green inside, a row of dark grey-green POINTED TEETH top and bottom drawn square by square (4-6 clear teeth), the corners turned up. THE TENDRIL: a 1-2 square thick dark blue-green stalk growing from the top of the head, curling up and back, ending in a round knob of about 4x3 squares in the darkest shade, with clear gaps between the stalk and the body. THE SLIME BODY: bright green in 4 shades; FEW BIG HIGHLIGHTS (yellow-green blocks of 2-4 squares following the muscles, like light on jelly) - NOT camouflage-like scattered spots; 2-3 dark green blobs of veins or organs showing inside, as solid shapes. THE BODY: broad and hunched, the head sunk between the two big shoulders; two THICK LONG ARMS hanging near the knees with BIG HANDS of three thick fingers (a dark 1-square gap between the fingers); SHORT THICK LEGS, the two feet APART on the ground line with three round toes each; the near arm and leg (image left) full tone, the far ones (image right) one shade darker; the background showing between the legs and under the arms.
One continuous 1-square near-black (very dark green-black) outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects, no slime puddle, no flying blobs, no background, no ground, no cast shadow, no text, no grid lines.
PICTURE A: the idle exactly as images 1A, 2A and 3A - standing hunched and ready in 3/4 view facing right, the face to the front-right with both eyes visible, the big hands hanging loose near the knees, the tendril curling up and back. Every square exactly 13 px; the top of the tendril's knob at y 325, the eyes at about y 624, the soles on y 1183 - exactly 66 squares tall, about 88 squares wide.
```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：每格 13 px、**66 格高**（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**——第 0 步就是画小了）。
- 两只黄眼睛一样大、一样高、带近白高光；咧嘴坏笑、尖牙一格一格；触须是一根干净的弯茎 + 圆疙瘩；身上高光是少而大的整块，不是满身碎斑；三指大手、短粗腿、两脚分开踩在地面线上。外描边连续；没有任何技能特效。

## 交付（`outputs/zac-model/`）

- `zac-model-A-1.png`、`zac-model-A-2.png`；原始生成图原样放 `outputs/zac-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/zac_model_done.zip`。中间不要停，两稿都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（约 13 px / 66 行），从 raw/ 按格读回（regrid），脸在 12 倍下看（眼睛、牙最容易糊），在游戏大小下和努努、科加斯、狼人并排自查（PPU 1.5：触须顶到脚底 44 游戏像素），把两稿给用户挑。
- 动作帧：问用户是 Claude 照英雄联盟的动作拼，还是 Codex 照骨架画姿势（`tools/lol/anim_graph.py Zac`；`pose_ref.py --champ Zac` 要带 `--hide-submeshes`）；一张脸用在所有帧。数据里要的动作：idle run attack skill skill_slam skill2 skill2_fly skill2_land ult ult_land hit dead（`tools/kit/build_zac.py`）。
