# 圣锤之毅 波比：第 1 步，游戏尺寸造型（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 第 0 步你画的 **B（锤子竖直立在脚边）**（`1_picture_B.png`）**用户选定了，样子、颜色、姿势全照它**。
> - 这一步要把她画成**游戏里的格子数**：**从马尾顶到鞋底 47 格**，锤柄和柄头再高出头顶约 8 格，**整个人连锤子共约 55 格高、约 44 格宽**。我把 B 直接缩到这个格子数（`2_target.png`）：**大小、位置、姿势对，细节是缩坏的**（脸、眼睛、甲片碎成杂点）。请像一个像素画师照着 `1_picture_B.png`，在这么粗的格子上**重新画一遍**，每个细节都用整格画清楚。
> - **每格画大：21 px 一格，人物撑满画布**。画布用你平时的 **1254 × 1254**：**柄头顶 y = 42，马尾顶 y = 210，眼睛约 y = 609，两只鞋底 y = 1197**。每一格都是 21 × 21 px 的大方块，不要用更小的格子画细节。**画两稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1254 × 1254**，**每格 21 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **柄头顶 y = 42**（橙线），**马尾顶 y = 210**（绿线），**眼睛约 y = 609**（蓝线），**鞋底 y = 1197**（红线）：马尾顶到鞋底 **47 格**。
- 宽约 44 格，从 x ≈ 147 到 x ≈ 1070：巨锤在画面左边（锤头约 x = 168–524、y = 924–1176，**锤柄竖直**，红布条在 x ≈ 294–335、从 y ≈ 230 到锤头），她站在右边。全在画布里。

## 在 47 格里要画清楚的地方

- **头**（马尾顶到下巴约 21 格，`4_head.png` 是第 0 步读回的头，8 倍）：两个蓬松大马尾，浅金色 3 档（亮黄、金、偏橙的暗部），**每个马尾一个 2 格的金色发环**；刘海盖住额头、两缕鬓发垂到肩。**浅蓝色的脸**（2–3 档），**两只紫红色眼睛：每只 2 格高、1–2 格宽，一样高，各带 1 格白色高光**，眉头微皱（1 格深色眉）；**两只长尖耳朵**伸向两边，**里面粉色**（2 档）；嘴 1 格深色。
- **身体**：红围巾 2 档；深紫褐皮甲 2–3 档（**要有偏亮的边**）；铜金甲片（两肩的护肩、胸前带金色徽记的护胸、腰带）3 档 + 1 格亮高光；暗橄榄绿衣裤 2 档 + 亮边；铜色护膝；深色靴子；深色手套。**近侧的手握在锤柄中间，远侧的手握拳收在腰边**，两脚稍分开、膝盖微弯。
- **巨锤**：**锤柄完全竖直、一条直线、粗细一致**（红布条 1–2 格宽，2 档红，外面 1 格描边），**不要歪、不要断**；柄头铜色方块 3 档；锤头着地：**两块浅灰钢色方锤头**（亮面、暗面分清楚，每块一圈浅色边）夹着**深棕木芯**和 **2×2 的圆钢钉帽**，接口处金色护片。锤子是一整块，左右对称地立着。
- **姿势**和 B 一样：3/4 正面朝右，**近侧在画面左边、颜色亮；远侧在右边、稍暗**。
- **一圈 1 格的近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的单个杂色格。

## 干净

- 和附图 5–8 一样的像素画（本包的卡西奥佩娅、茂凯——**和波比同一个密度 PPU 1.3**——吉格斯、崔丝塔娜两个约德尔人；8 倍放大，一格 = 一个像素）：大小一致的方块、对齐网格，2–3 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**，边缘不要半透明。不要网格线、文字、边框、影子、地面、特效（不画盾牌）。

## 附图（压缩包 `poppy_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture_B.png` | 你第 0 步画的 B（用户选定） | **样子、颜色、细节、姿势**全照它 |
| `2_target.png` | B 缩到游戏格子数、每格 21 px 放在画布上（细节是坏的） | **大小、位置、比例、姿势**照它，坏的地方照 1 重画 |
| `3_layout.png` | 同一张加网格线：橙 = 柄头顶，绿 = 马尾顶，蓝 = 眼睛，红 = 地面 | 对齐网格、47 格的高度、地面线 |
| `4_head.png` | 第 0 步读回的头（8 倍） | 马尾、发环、脸、眼睛、耳朵 |
| `style/5_style_cassiopeia.png` … `8_style_tristana.png` | 本包的卡西奥佩娅、茂凯（同密度）、吉格斯、崔丝塔娜，8 倍放大 | **只看风格**：这么粗的格子里脸、眼睛、头发、金甲怎么画 |

## 提示词：`poppy-model-B-1.png`、`poppy-model-B-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own earlier pixel-art drawing of this character - a small yordle girl warrior: pale blue skin, violet-pink eyes, long pointed ears pink inside, pale-blonde hair with a fringe and two big puffy pigtails tied with gold rings, a red scarf, dark purple-brown leather armour with copper-gold plates (pauldrons, a chest piece with a gold emblem, a belt), dark olive clothes, copper knee guards, dark boots, and a HUGE HAMMER standing UPRIGHT beside her near foot (two pale grey-steel square head blocks round a dark-brown wooden core with a round steel boss, gold flanges, a long red-wrapped haft held in her near hand, a copper pommel), her far fist at her waist - its LOOK, COLOURS and POSE are approved, but it is drawn with far too many small squares; 2 the same character cut down to the RIGHT square count - 47 squares from the top of her pigtails to her soles, the haft rising about 8 squares above her head, about 44 x 55 squares in all - shown with 21 px squares on a 1254x1254 canvas: its SIZE, PLACE, PROPORTIONS and POSE are right, but the cut broke its details (the face, the eyes and the armour plates are specks); 3 the same with grid lines every 5 squares: orange = the top of the pommel, green = the top of the pigtails, blue = the eyes, red = the ground; 4 the head of image 1 enlarged; 5-8 STYLE ONLY: other characters from the same game shown 8x so every square is one pixel (5 and 6 at this same square density) - how a face, eyes, hair and gold armour are drawn with this few squares, and yordles (7, 8).
Draw with the image generator ONE clean pixel-art picture of the character from image 1 at the square count of image 2: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). BIG SQUARES: every square exactly 21 px, aligned on one straight grid from the canvas corner; the top of the pommel at y 42, the top of the pigtails at y 210, the eyes at about y 609, both soles on y 1197 - exactly 47 squares from the pigtail top to the soles, about 44 x 55 squares in all, the figure filling the canvas as in image 2. Every detail drawn with whole 21 px squares, never with smaller pixels.
With only 47 squares make every part READ: the two big puffy pigtails in 3 pale-blonde shades (bright yellow, gold, a warmer dark shade), a 2-square GOLD RING on each; the fringe over the forehead and two locks down to the shoulders; the pale blue face in 2-3 shades; TWO VIOLET-PINK EYES, each 2 squares tall and 1-2 wide, at the SAME height, each with ONE white highlight square, a 1-square dark brow in a slight frown; two long pointed ears out to the sides, PINK inside in 2 shades; a 1-square dark mouth; the red scarf in 2 shades; the dark purple-brown armour in 2-3 shades with LIGHTER EDGES; the copper-gold pauldrons, chest piece with its emblem and belt in 3 golds with one bright highlight square; the dark olive clothes in 2 shades with a light edge; copper knee guards; dark boots; dark gloves; the NEAR hand gripping the middle of the haft, the FAR fist at her waist, feet a little apart, knees slightly bent.
THE HAMMER as ONE SOLID PIECE standing upright: the haft PERFECTLY VERTICAL, ONE STRAIGHT LINE of the same width all along (the red wrap 1-2 squares wide in 2 reds, a 1-square outline each side), never slanted or broken; the square copper pommel in 3 shades; the head on the ground: two pale grey-steel square blocks (lit and shaded faces clearly apart, each with a light rim) round the dark-brown wooden core with a 2x2 round steel boss, gold flanges at the neck, symmetric left and right.
THE VIEW: 3/4 view facing right, the NEAR arm and leg on the image left in full tone, the FAR ones on the image right a step darker.
One continuous 1-square near-black outline round the figure; inside it every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no shield), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **每格 21 px 的大方块**：柄头顶 y 42、马尾顶 y 210、鞋底 y 1197，**马尾顶到鞋底正好 47 格**（数一下台阶数：**如果是 70–90 格就是格子画小了，请重画**）。
- 两只紫红眼睛一样大、一样高、带白高光；耳朵里面粉色；**锤柄完全竖直、粗细一致、不断**；锤头两块灰钢方块 + 木芯 + 钉帽；外描边连续；没有任何特效、没有盾牌。

## 交付（`outputs/poppy-model/`）

- `poppy-model-B-1.png`、`poppy-model-B-2.png`；原始生成图原样放 `outputs/poppy-model/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/poppy_model_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 量格子（应约 21 px、马尾到鞋底 47 行），从 raw/ 按格读回（regrid），必要时删 1–3 行整行整列（不经过脸、不经过锤柄），在游戏大小下和吉格斯、崔丝塔娜、提莫、牛头、蕾欧娜并排自查（PPU 1.3，36 游戏像素）。
- 动作帧自己摆（rig_poppy.py，照 rig_wukong.py / rig_gangplank.py；**巨锤是刚体**：先把锤子单独剪出来、单独渲染检查是不是一整块、锤柄直，再只做整格平移和直角转；普攻 / Q 砸地 = 锤子转平再砸下，R = 锤子横着抡）。自查到完美（连通块、单帧闪烁、腿在胯下、脸不被挡）再给用户审。
