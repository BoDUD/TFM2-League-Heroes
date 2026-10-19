# 不灭狂雷 沃利贝尔：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **B（两臂垂下）**（`1_picture_B.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把他画成**游戏里的格子数**：**从耳朵顶到脚底 53 格**，约 48 格宽。我把 B 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（脸、眼睛、符文碎成杂点）。请像一个像素画师照着 `1_picture_B.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **要画两个角度**（同一只熊、同样的格子、同样的颜色）：
>   - **3/4 正面朝右**（和 B 一样）：游戏里的待机。
>   - **侧面朝右**（附图 5、6）：身体转成侧面，**熊嘴朝画面右边**，近侧的肩膀和手臂在前面（画面中间偏右），远侧的手臂大部分被身体挡住、只露一点；两条腿一前一后（近侧腿在前、颜色亮，远侧腿在后、稍暗），脚掌朝右。**头保持和 3/4 正面一样**（脸朝右前方、两只眼睛都看得见，同样的格子），只把身体转成侧面。他的跑步和攻击动作都从这张侧面图来做。
> - **每格画大：21 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**：**耳朵顶 y = 84，眼睛约 y = 252，两只脚底 y = 1197**。每一格都是 21 × 21 px 的大方块，不要用更小的格子画细节。**每个角度画两稿，一共四张。**

## 大小和位置（照 `2_target.png` / `3_layout.png` / `6_side_layout.png`）

- 画布 **1254 × 1254**，**每格 21 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **耳朵顶 y = 84**（绿线），**眼睛约 y = 252**（蓝线），**脚底 y = 1197**（红线）：耳朵顶到脚底 **53 格**。
- 3/4 正面：宽约 48 格，从 x ≈ 105 到 x ≈ 1113，全在画布里。侧面：照 `6_side_layout.png` 的淡色剪影的大小和地面线（宽约 35–40 格），放在画布中间。

## 在 53 格里要画清楚的地方

- **头**（耳朵顶到下巴约 14 格，`4_head.png` 是第 0 步读回的头，8 倍）：白毛 3 档（纯白、浅冰蓝、灰蓝暗部）；长熊嘴、**2 格的黑鼻头**、**龇着的白牙（1 行）**；**两只发光的青蓝色眼睛：每只 1–2 格，一样高**，压着的深色眉毛（1 格）；额头一道蓝色闪电符文（3–4 格）；两只小圆耳朵（里面深色 1 格），一只耳朵上 1–2 格的蓝宝石。
- **身体**：白毛带冰蓝 3 档（头、肩、胸、手臂），往下变成**深灰紫色 3 档**（肚子下半、腿、手掌、脚掌），中间一档过渡，平涂色块；**深色的腿要有偏亮的边**。上臂各一块**蓝色符文纹身**（2 档蓝），胸腹 2–3 道**蓝色闪电纹**。
- **两条毛辫**：从肩膀垂到肚子，白毛 2 档，套着 2 个**深色铁环**（每个 2–3 格高，上面 1 格发光的青色符文），末端白毛穗 2–3 格。
- **爪子**：手上各 3–4 根、脚上各 3 根**冰蓝色水晶爪**（2 档青蓝，每根 1 格宽、1–2 格长）。
- **姿势**（3/4 正面）和 B 一样：两脚稍分开、膝盖微弯，**两只手臂竖直垂在身体两侧**，爪尖在膝盖上下；**近侧在画面左边、颜色亮；远侧在右边、稍暗**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 7–10 一样的像素画（本包的内瑟斯、塔姆、孙悟空、厄加特——**和沃利贝尔同一个密度 PPU 1.2**；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画闪电、雷云）。

## 附图（压缩包 `volibear_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_B.png` | 你第 0 步画的 B（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | B 缩到游戏格子数、每格 21 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：绿 = 耳朵顶，蓝 = 眼睛，红 = 地面 | 对齐网格、53 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 熊嘴、黑鼻头、牙、发光的眼睛、额头符文、耳朵和宝石 |
| `5_side_ref.png` | 英雄联盟原版的待机，接近侧面、朝右 | **侧面图的身体**：肩膀、胸口和肚子的厚度、手臂在身体前面怎么垂、两腿一前一后 |
| `6_side_layout.png` | 5 缩到同样的 53 格高放在网格上（淡色，只看大小） | 侧面图的大小、位置、地面线 |
| `style/7_style_nasus.png` … `10_style_urgot.png` | 本包的内瑟斯、塔姆、孙悟空、厄加特，8 倍放大（同密度） | **只看风格**：这么粗的格子里毛发、脸、眼睛、暗色身体的亮边怎么画 |

## 提示词 1：`volibear-model-B-1.png`、`volibear-model-B-2.png`（3/4 正面，两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a huge bear standing on his hind legs: white fur with a pale ice-blue tint on the head, shoulders, chest and arms turning to dark slate-violet fur on the lower belly, the legs, the hands and the feet; a small bear head (a long muzzle, a black nose, a snarling mouth with white teeth, glowing cyan eyes, a blue lightning rune on the forehead, small round ears, a blue jewel in one ear); two braided white fur tresses from the shoulders down his chest in dark iron bands with glowing cyan runes and white tassels; blue rune tattoos on the upper arms, blue lightning stripes across the chest and belly; crystalline glowing ice-blue claws; BOTH ARMS HANGING STRAIGHT DOWN beside the body - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 53 squares from the top of his ears to his soles, about 48 squares wide - shown with 21 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the face, the eyes and the runes are specks); 3 the same with grid lines every 5 squares: green = the top of the ears, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5 and 6 are for the side view (not this picture); 7-10 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel, at this same square density - how fur, a face, eyes and the lit edges of a dark body are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 21 px, aligned on one straight grid from the canvas corner; the top of the ears at y 84, the eyes at about y 252, both soles on y 1197 - exactly 53 squares from the ear top to the soles, about 48 squares wide, the figure filling the canvas as in image 2. Every detail drawn with whole 21 px squares, never with smaller pixels.
With only 53 squares make every part READ: the head (about 14 squares, ears to chin) in 3 whites (pure white, pale ice-blue, a greyish-blue shade); the long muzzle, a 2-square BLACK NOSE, one row of bared WHITE TEETH; TWO GLOWING CYAN EYES, each 1-2 squares, at the SAME height, under a 1-square dark angry brow; the blue lightning rune on the forehead (3-4 squares); two small round ears, a 1-2 square blue jewel on one; the white ice-blue fur of the shoulders, chest and arms in 3 shades turning through one in-between shade to the DARK SLATE-VIOLET fur of the lower belly, legs, hands and feet in 3 shades with LIGHTER EDGES; a blue rune tattoo on each upper arm (2 blues) and 2-3 blue lightning stripes across the chest and belly; the two braided white tresses down to the belly, each with 2 dark iron bands (2-3 squares tall, one glowing cyan rune square each) and a 2-3 square white tassel; 3-4 ICE-BLUE CRYSTAL CLAWS on each hand and 3 on each foot (2 cyan-blues, each 1 square wide, 1-2 long).
THE POSE as image 1: feet a little apart, knees slightly bent, BOTH ARMS HANGING STRAIGHT DOWN beside the body, the claw tips about knee height; 3/4 view facing right (the face to the front-right), the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no lightning, no storm cloud), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`volibear-model-side-1.png`、`volibear-model-side-2.png`（侧面朝右，两稿）

附全部图。**用 image_gen 画。**

```text
Same attached images and the SAME character, colours, square size (21 px) and square count as prompt 1 - now SIDE-ON, FACING RIGHT. Image 5 is the original character nearly from the side, facing right: copy from it the BODY seen side-on - the depth of the shoulders, chest and belly, the near arm hanging in front of the body, the legs one in front of the other; image 6 is that view brought to the same 53 squares on the grid (faded: size, place and ground line only).
Draw with the image generator ONE clean pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 21 px on one straight grid from the canvas corner; the top of the ears at y 84, the eyes at about y 252, both soles on y 1197 - exactly 53 squares from the ear top to the soles, about 35-40 squares wide, in the middle of the canvas.
THE BODY SIDE-ON: the muzzle pointing to the image right; the NEAR shoulder and NEAR ARM in front (hanging straight down, the claws at about knee height), full tone; the FAR arm mostly hidden behind the body, a step darker; the chest and the round belly in profile; the two legs one in front of the other (the NEAR leg in front in full tone, the FAR leg behind a step darker), the feet with their claws pointing right; the near tress hanging down the front of the chest.
THE HEAD stays the SAME as the 3/4 view of prompt 1 (the face to the front-right, BOTH glowing cyan eyes visible, the same squares, the black nose, the bared teeth, the forehead rune, the ears and the jewel) - only the body is turned side-on.
The same colours and details as prompt 1: white ice-blue fur turning to dark slate-violet with lighter edges, the blue rune tattoo on the near upper arm, the lightning stripes, the dark iron bands with cyan runes, the ice-blue crystal claws; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 21 px 的大方块**：耳朵顶 y 84、脚底 y 1197，**耳朵顶到脚底正好 53 格**（数一下台阶数：**如果是 80–110 格就是格子画小了，请重画**）。
- 两只发光的眼睛一样高；黑鼻头、白牙；额头符文；两条毛辫和铁环；冰蓝爪子；外描边连续；没有任何特效。
- 3/4 正面：两臂竖直垂下；侧面：熊嘴朝右、近侧手臂在前、两腿一前一后、**头和 3/4 正面一样**。

## 交付（`outputs/volibear-model/`）

- `volibear-model-B-1.png`、`volibear-model-B-2.png`、`volibear-model-side-1.png`、`volibear-model-side-2.png`；原始生成图原样放 `outputs/volibear-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/volibear_model_done.zip`。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 21 px、耳朵到脚底 53 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸），在游戏大小下和内瑟斯、塔姆、厄加特、孙悟空并排自查（PPU 1.2，44 游戏像素），给用户挑 3/4 和侧面各一张。
- 动作帧自己摆（rig_volibear.py，照 rig_maokai.py / rig_nasus.py / rig_jarvaniv.py / rig_poppy.py：只整格平移、绕半格枢轴的四分之一转、镜像；一张脸用在所有帧）。英雄联盟的动作：普攻 Volibear_Attack_1 / _2；W Volibear_Spell2_Slash；Q volibear_spell1_run（四脚着地冲）+ volibear_spell1_attack（扑上去砸）；E volibear_spell3（举爪召雷）；R Volibear_Spell4_Ground_Pound（跳起砸地）；跑 volibear_run；死亡 volibear_death（8 帧带落地回弹）；挨打第 1 帧白闪并后退。
