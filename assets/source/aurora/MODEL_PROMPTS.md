# 双界灵兔 阿萝拉：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的原始图（`1_picture_A.png`）**样子、颜色用户认可了，全照它**。
> - 用户定了：**只做 3/4 正面朝右，不要侧面**；**从帽顶（帽子的尖，不算耳朵）到脚底 57 格**，兔耳朵在帽顶上方另算（连耳朵一共 72 格高）。我把图直接缩到这个格子数（`2_target_A.png`）：**大小、位置、姿势对，细节是缩坏的**（眼镜、眼睛、嘴、帽子的金边和符文、羽毛、披肩的毛边、腰带碎成杂点）。请像一个像素画师照着第 0 步的图，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大，人物撑满画布**。画布用你平时的 **1254 × 1254**，**每格 16 px**。每一格都是一个完整的大方块，不要用更小的格子画细节。
> - 一共画**两稿**（同一个阿萝拉、同样的颜色）：`A-1` / `A-2`。

## 大小和位置

- 画布 **1254 × 1254**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **A（待机）**：每格 **16 px**；照 `2_target_A.png` / `3_layout_A.png`：兔耳朵尖约 **y = 48**，**帽顶 y = 288**（橙线），眼睛约 **y = 528**（蓝线），脚底 **y = 1200**（红线）：**帽顶到脚底 57 格**，连耳朵 **72 格高、约 38 格宽**（魔杖、尾巴另算）。
- 全在画布里，耳朵、魔杖、尾巴不出画，四周留至少 1 格空。

## 在这么少的格子里要画清楚的地方

- **脸**（`4_head_A.png`，第 0 步读回的头，8 倍）：浅暖色皮肤 2–3 档；**圆眼镜**：金色细框（整格），每个镜片约 **4 × 4 格**的圆圈，框一圈连续，不能断成半格；镜片里**两只紫蓝色的眼睛都看得见，每只约 2 × 2 格（一格深色瞳孔、一格亮色高光），一样高**；小鼻子一格；**小嘴带一点好奇的笑**（一两格，嘴里一格粉红）；脸颊一格淡粉。
- **头发**：**铜红色的卷发**（3–4 档，亮处橙），刘海从帽檐下露出来，两侧各一条**短麻花辫**垂到肩上，辫尾一格金色小环；头发和脸之间有清楚的描边。
- **帽子**：**宽檐的青绿色女巫帽**（3 档），帽檐一圈**金边**（整格），帽身上一两道金色符文线；帽尖往后（画面左边）弯；帽带上**一簇红色羽毛**（2–3 档）和一串金色坠子。
- **兔耳朵**：两只**长兔耳朵**从帽子里竖起来，**外侧橙红色**（3 档），**里面浅粉白**（2 档），每只至少 4 格宽，耳朵尖收圆；近处的耳朵（画面右边）直一点，远处的（画面左边）往后斜一点。
- **身体**：**米白色的高领毛衣**（一圈粗粗的领子，3 档）；肩上**浅蓝白的毛边披肩**（3 档，边缘一格一格的蓬松毛边）；里面**米白色的长外套**（3 档），后摆长长地垂到画面左边，里子浅蓝；胸前一块**青绿色的布**带一格金色符文；腰上**棕色的编织腰带**和一颗金扣；外套下面一截青绿短裙；**深棕色的过膝长袜**（2–3 档），袜口一圈米白；**带白毛边的短靴**（深蓝灰 + 金扣）踩在地面线上；**两条腿之间要有空隙和描边分开**；近处的腿（画面左边）全亮，远处的腿暗一档。
- **手和魔杖**：近处的手（画面左边）垂在身侧，戴米白手套；远处的手（画面右边）握着**细长的魔杖**扛在肩上，杖身**深棕**（至少 1 格粗，整格连续），**金色装饰**，往后上方斜指到画面左上，**杖头一格蓝光**，杖尾一格红；魔杖**不挡脸**。
- **尾巴**：身后（画面左边）一团**蓬松的橙色兔尾巴**（3 档），边缘一格一格的毛。
- **一圈 1 格的近黑外描边**，连续不断（耳朵、魔杖、尾巴都有）；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–8 一样的像素画（本包的妮蔻、佐伊、悠米、彗，8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、投影、地面、技能特效（灵物、诅咒、冲击波、发光都不画）。

## 附图（压缩包 `aurora_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_A.png` | 你第 0 步画的原始图（用户认可） | **样子、颜色、细节、姿势**全照它 |
| `2_target_A.png` | 缩到游戏格子数、放大放在画布上（细节是坏的） | **大小、位置、比例、姿势** |
| `3_layout_A.png` | 加网格线：橙 = 帽顶，蓝 = 眼睛，红 = 地面 | 对齐网格、高度、地面线 |
| `4_head_A.png` | 第 0 步读回的头（8 倍） | 脸、眼镜、眼睛、刘海、麻花辫、帽檐 |
| `style/5_style_neeko.png`、`6_style_zoe.png`、`7_style_yuumi.png`、`8_style_hwei.png` | 本包的妮蔻、佐伊、悠米、彗，8 倍放大 | **只看风格**：这么粗的格子里女孩的脸、大眼睛、毛边、长外套怎么画 |

## 提示词（两稿用同一段，各画一张）

附全部图。**用 image_gen 画。**

```text
Attached images: 1A your own earlier pixel-art drawing of one character - a PETITE BUNNY WITCH with CURLY COPPER-RED HAIR and two short braids, ROUND THIN GOLD GLASSES over VIOLET-BLUE EYES, a curious little smile, a WIDE-BRIMMED TEAL WITCH HAT with a gold brim edge and gold rune lines, its tip bending back, RED FEATHERS and a gold charm at the band, TWO LONG RABBIT EARS (orange-red outside, pale pink-white inside) rising through the hat, a CREAM cable-knit high collar, a PALE BLUE-WHITE FUR-TRIMMED SHAWL, a CREAM LONG COAT with long tails and pale blue lining, a TEAL chest panel with a gold rune, a BROWN BRAIDED BELT with a gold buckle, a short teal skirt, DARK BROWN THIGH-HIGH STOCKINGS, short boots with white fur trim, a FLUFFY ORANGE BUNNY TAIL behind her, and a SLIM WAND (dark brown shaft, gold fittings, a blue glowing tip) resting on her shoulder pointing up and back - her LOOK and COLOURS are approved, but she is drawn with far too many small squares; 2A the same picture cut down to the RIGHT square count - 57 squares from the top of the hat (not the ears) to the soles, 72 with the ears - shown with big squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke the details; 3A the same with grid lines every 5 squares: orange = the top of the hat, blue = the eyes, red = the ground; 4A her head enlarged; 5-8 STYLE ONLY: other characters from the same game at the same square density, shown 8x so every square is one pixel - how a girl's face, big eyes, fluffy fur trim and a long coat are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of this character at this square count: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES, every square exactly 16 px, aligned on one straight grid from the canvas corner; the ear tips at about y 48, the top of the hat at y 288, her eyes at about y 528, her soles on y 1200 - exactly 57 squares from hat top to soles, 72 squares tall with the ears, about 38 squares wide (the wand and the tail beyond); at least one empty square on every side. Every detail drawn with whole squares, never with smaller pixels.
With this few squares make every part READ: the light warm face in 2-3 shades; ROUND GOLD GLASSES, each lens a closed ring of whole squares about 4x4, never broken into half squares; inside them BOTH VIOLET-BLUE EYES visible, each about 2x2 squares (one dark pupil square, one bright highlight square), at the SAME height; a one-square nose; a small curious smile with one pink square; one soft pink square on each cheek. The copper-red curly hair in 3-4 shades (orange lit), bangs under the brim, a short braid on each side down to the shoulders with a gold ring at the end, kept apart from the face by the outline. The teal hat in 3 shades with a gold brim edge of whole squares and one or two gold rune lines, its tip bending back to the image left, a tuft of red feathers and a gold charm at the band. The TWO LONG RABBIT EARS rising through the hat, orange-red in 3 shades outside and pale pink-white in 2 inside, each at least 4 squares wide with rounded tips, the near ear (image right) straighter, the far ear (image left) leaning back. The cream high collar in 3 shades; the pale blue-white shawl in 3 shades with a stepped fluffy edge; the cream long coat in 3 shades, its tails hanging down on the image left with pale blue lining; the teal chest panel with a gold rune square; the brown braided belt with a gold buckle; a short teal skirt; dark brown thigh-high stockings in 2-3 shades with cream tops; short boots, dark blue-grey with gold buckles and white fur trim, on the ground line; a clear gap and outline between her legs, the NEAR leg on the image left in full tone, the FAR leg on the image right a step darker. The NEAR hand (image left) hanging at her side in a cream glove; the FAR hand (image right) holding the SLIM WAND on her shoulder, its dark brown shaft at least 1 square thick and continuous, gold fittings, pointing up and back to the upper left, one blue glowing square at its tip and one red square at its end, NEVER over her face. The FLUFFY ORANGE TAIL behind her on the image left in 3 shades with a stepped furry edge.
One continuous 1-square near-black outline round the figure, the ears, the wand and the tail; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No spell effects (no spirits, no curses, no shockwaves, no glow, no sparkles), no background, no ground, no cast shadow, no text, no grid lines.
PICTURE A: her light playful idle exactly as images 1A, 2A and 3A - standing in 3/4 view facing right, the face to the front-right, the near hand at her side, the wand on her shoulder in the far hand, the coat tails and the tail behind her, the two long ears up through the hat.
```

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- 格子：每格 16 px，帽顶到脚底 57 格、连耳朵 72 格（数一下台阶数：**格子数多出一半以上就是格子画小了，请重画**）。
- 圆眼镜两个镜片都是**连续的圆圈**；镜片里两只紫蓝眼睛看得见、一样高、带高光；小嘴在笑；铜红卷发和两条麻花辫和脸分得开；青绿帽子的金边、红羽毛清楚；两只长兔耳朵外橙里粉；米白高领、浅蓝白毛边披肩、米白长外套和后摆、青绿胸布、棕腰带、深棕长袜、毛边短靴清楚；两条腿分开。
- 魔杖扛在肩上往后上方斜指，**不挡脸**，杖头一格蓝光；橙色尾巴在身后。外描边连续；没有任何技能特效。

## 交付（`outputs/aurora-model/`）

- `aurora-model-A-1.png`、`aurora-model-A-2.png`；原始生成图原样放 `outputs/aurora-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/aurora_model_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（约 16 px / 72 行），从 raw/ 按格读回（regrid：给的格子要比真实格子略大，否则会多切行；量出来的格子比要求的小时，按身子和头的大小读，不按整张的包围盒），切到帽顶到脚底 57 行，在游戏大小下和彗、佐伊、薇古丝、妮蔻、辛德拉、维克托并排自查（PPU 1.5：38 游戏像素），把两稿给用户挑。脸放大 12 倍检查，眼镜 / 眼睛 / 嘴的格子不清楚就在设计脚本里重画（`codex-face-half-squares` 的做法）。
- 动作帧：`tools/lol/anim_graph.py Aurora`（片段名是 .anm 文件名：idle、run_new_4、attack6、attack8、spell1、spell1_recast、spell2、spell3_reblock3、spell4_e、death）；一张脸用在所有帧；帽子和耳朵跟着头走，尾巴跟着腰走。数据里的动作名见 `tools/kit/build_aurora.py`：idle run attack hit dead skill（Q 飞去来咒）skill2（E 怪奇喷涌）ult（R 双界合一）veil（W 灵纱洞开，残血时的后跳）。
