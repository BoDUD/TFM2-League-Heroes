# 普朗克：游戏尺寸造型重画（第 1 步第二轮，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一轮你画的 A-1（`1_round1_A1.png`）**样子很好，用户和我都要它的样子**。问题只在**格子太小、太多**：我们要的是**从帽子顶到鞋底 50 格**，你画的是约 **78 格**（每格约 12–13 px）。我把它删到 50 行后，手炮、弯刀、皮带、脸都碎成了杂点（`2_target_50.png` 就是删完的样子：**大小、位置、姿势对，细节是坏的**）。
> - **这一轮：每格画大，21 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**，**帽子顶在 y = 126，鞋底在 y = 1176**，中间正好 **50 格**。也就是说：**每一格都是 21 × 21 px 的大方块**，整个人只有 50 格高、约 52 格宽。请像一个像素画师照着 `1_round1_A1.png`，在这么粗的格子上重新画一遍，**每个细节都用整格画清楚**（不要用更小的格子画细节）。**画两稿。**

## 大小和位置（照 `2_target_50.png` / `3_layout_50.png`）

- 画布 **1254 × 1254**，**每格 21 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_50.png` 的浅灰线每 5 格一条）。
- **帽子顶 y = 126**（绿线），**胡子扎红布的地方约 y = 441**（蓝线），**两只鞋底 y = 1176**（红线）：**50 格高**。
- 宽约 52 格：外套下摆左边约从 x = 63 开始，扛在近侧肩上的金色手炮约在 x = 190–440、y = 250–440，弯刀刀尖约到 x = 1155、y = 880–1040。全在画布里。

## 在 50 格里要画清楚的地方

- **头**（约 15 格高，`4_head.png` 是上一轮读回的头，8 倍）：黑色月牙帽（2–3 档黑灰、**上沿一条亮灰边**）；**两只眼睛各 1 格深色（近黑）、一样高**，上面 1 格浓眉，**不要红色**；1 格鼻子高光；八字胡和花白偏棕的长胡子 2–3 档，下巴下 1 格**红布**。
- **手炮**：金色 3 档 + 1 格亮高光，炮口 1 格深色圈，扛在近侧肩上，**近侧手在脸旁边、不挡脸**。手炮要是**一整块**，不要断开。
- **身体**：赤膊的胸口和圆肚子（肉色 3 档，**纹身最多 2–3 条深色短线**，不要乱点）；青绿护肩 2 档；交叉的深色皮带 1 格宽、连续；红布缠小臂；红腰带 2–3 档 + 棕皮带 + **2×2 的金扣**；背后深紫外套下摆 2 档 + **1 格金边**、破成 3 条；深灰绿裤子 2 档 + 亮边；棕色翻口靴子，翻口 1 格金边。
- **弯刀**：远侧手握着、朝前下方伸出，**刀身 2 格宽、深灰 2 档、连续不断**，刀背 2–3 个锯齿，**刀尖 3–4 格橙红发亮**（橙、黄、红）。
- **姿势**和上一轮一样：站得很稳、两脚分开、3/4 正面朝右，近侧在画面左边颜色亮，远侧在右边稍暗。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；**黑帽子、深紫外套、深灰绿裤子要有偏亮的边**；没有孤立的单个杂色格。

## 干净

- 和附图 5–8（本包的内瑟斯、塔姆，和普朗克同一个密度；斯维因；厄运小姐；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `gangplank_model_pack2.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_round1_A1.png` | 你上一轮画的 A-1 | **样子、颜色、细节**全照它 |
| `2_target_50.png` | A-1 删到 50 格、每格 21 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout_50.png` | 同一张加网格线：绿线 = 帽子顶，蓝线 = 胡子红布，红线 = 地面 | 对齐网格、50 格的高度、地面线 |
| `4_head.png` | 上一轮读回的头（8 倍） | 帽子、脸、眼睛、胡子、手炮 |
| `style/5_style_nasus.png` … `8_style_missfortune.png` | 本包的内瑟斯、塔姆（同密度）、斯维因、厄运小姐，8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、深色衣服怎么画 |

## 提示词：`gangplank-model2-A-1.png`、`gangplank-model2-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a burly pirate captain: a black crescent pirate hat, a frowning face, a moustache and a long greyish-brown beard tied with a red cloth, a bare tattooed belly under a teal-green collar and crossed straps, red forearm wraps, a red sash with a gold buckle, a dark-purple coat behind him in torn tails with gold trim, dark grey-green trousers, brown cuffed boots, a GOLDEN HAND CANNON resting on his near shoulder (the hand beside the face) and a DARK SERRATED CUTLASS down and forward with an orange-hot tip - its LOOK and COLOURS are approved, but it was drawn with TOO MANY SMALL SQUARES (about 78 squares tall); 2 the same character cut down to the RIGHT square count, 50 squares tall, shown with 21 px squares on a 1254x1254 canvas - its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the cannon, the blade, the straps and the face are specks); 3 the same with grid lines every 5 squares: green = the top of the hat, blue = the beard's red tie, red = the ground; 4 the head of image 1 enlarged; 5-8 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (5 and 6 at this same square count per body) - how a face, eyes, a beard and dark clothes are drawn with this few squares.
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 21 px, aligned on one straight grid from the canvas corner; the top of the hat at y 126, the beard's red tie at about y 441, both soles on y 1176 - exactly 50 squares tall and about 52 squares wide, the figure filling the canvas as in image 2. Every detail drawn with whole 21 px squares, never with smaller pixels.
With only 50 squares make every part READ: the black crescent hat in 2-3 dark shades with a LIGHT GREY TOP EDGE; TWO EYES, ONE near-black square each at the SAME height (NOT red) under a 1-square heavy brow, a 1-square nose highlight; the moustache and beard greyish-brown in 2-3 shades with ONE red square of cloth at the tie; the GOLDEN HAND CANNON as ONE SOLID PIECE on the near shoulder, 3 golds, one bright highlight square, a dark muzzle ring, the near hand beside the face; the bare belly in 3 skin shades with at most 2-3 short dark tattoo strokes; the teal collar in 2 shades; the crossed dark straps 1 square wide and continuous; red forearm wraps; the red sash, a brown belt and a 2x2 gold buckle; the dark-purple coat tails in 2 purples with a 1-square GOLD edge, torn into 3 strips; dark grey-green trousers with a light edge; brown boots with 1-square gold cuffs; the cutlass blade 2 squares wide, 2 dark greys, ONE CONTINUOUS blade with 2-3 saw teeth, its tip 3-4 squares glowing orange, yellow and red.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; the hat, the coat and the trousers with LIGHTER EDGES; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 21 px 的大方块**，帽子顶 y 126、鞋底 y 1176，**正好 50 格高**、约 52 格宽（数一下：从帽子顶到鞋底的台阶数应是 50 左右，**如果是 70–80 格就是格子画小了，请重画**）。
- 两只眼睛各 1 格、深色、一样高；手炮一整块、手不挡脸；弯刀连续、刀尖橙红；外描边连续；没有任何特效。

## 交付（`outputs/gangplank-model2/`）

- `gangplank-model2-A-1.png`、`gangplank-model2-A-2.png`；原始生成图原样放 `outputs/gangplank-model2/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/gangplank_model2_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 21 px、50 行），regrid 读回，必要时删 1–3 行整行整列（不经过脸）；按游戏大小和内瑟斯、塔姆、斯维因、德莱厄斯、奥拉夫并排自查。用户把动作帧交给我自己做（「动作帧参考塔姆那种做法 不用依赖codex 然后做完了你自己review 完美了再喊我review」）：设计定下后直接 rig_gangplank.py 摆动作，自查到满意再给用户审。
