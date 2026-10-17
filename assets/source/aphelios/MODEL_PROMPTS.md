# 厄斐琉斯：游戏尺寸造型（第 1 步，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**（之前有个英雄的第 1 步是用脚本逐格写的，格子对了，但样子丢了很多，用户没有采用。）
> - 用户选了你第 0 步画的 **A**（`1_picked_A.png`），定的大小是：游戏里**从头顶（不算翘起的那撮头发）到脚底 40 行**，每个游戏像素 1.5 格，也就是他要画成 **60 格高**。
> - 用户还要求：**头放大到约四分之一**：从头顶到下巴约 **15 格**（全身 60 格的 25%；A 里只有 14%，在游戏里脸看不清）。下巴以下约 45 格，身体仍然清瘦修长。
> - 我把 A 按这个比例直接缩好了（`2_target_body.png`，每格 12 px），**大小、位置、姿势、头身比都对，但糊了**：脸和眼睛糊成几格，头发的高光没了，围巾和外套的分档、月牙扣、金珠手链、通碧的两片长刃都糊在一起，脖子那里还有一道接缝。
> - **这一轮就是在同样的格子上把它重画清楚**：同样大小、同样位置、同样姿势，**每块 12 px，横平竖直对齐网格**，就像一个像素画师照着 A，在 `2_target_body.png` 的格子里一格一格重画出来。
> - 另外，五把武器也要按同样的格子、和他同一个比例重画一张武器表（`5_picked_W.png` 是你第 0 步画的，`6_target_weapons.png` 是我缩好的，也是糊的）。
> - **人和武器表各画两稿。**

## 大小和位置（照 `2_target_body.png` / `3_layout.png` / `6_target_weapons.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **他**：**头顶在 y = 240**（绿线；翘起的那撮头发再往上几格），**下巴在 y ≈ 420**（蓝线），**脚底在 y = 960**（红线），两只脚底在同一条线上。左右位置、通碧靠在身后近侧肩上的样子、举到脸边的手、两腿站开的样子都照 `2_target_body.png`。
- **通碧**照 A 的样子：两片并排的长月牙刃 + 中间弯弯的握把，竖着靠在他身后，枪尖比头顶高出约 5 格。长度照 `2_target_body.png`（约 47 格）。
- **武器表**：单独一张 1024 × 1024 的图，五把武器和他**同一个比例**（通碧约 47 格长），摆法照 `6_target_weapons.png`：上排从左到右 通碧（竖着）、断魄、坠明（旁边浮着星星）、折镜，下排是宽宽的荧焰。每两把之间至少空 3 格。

## 要画清楚的地方（他）

- **头**（`4_head.png`，**画大**，约 15 格高）：
  - **黑发**，带几格蓝紫色的高光，**长刘海斜着盖住画面右边那只眼睛**，后脑一撮短短翘起的头发（3–4 格）。
  - **苍白的脸**，露出的那只**半闭的眼睛**至少 2 格宽，眼皮下垂，眼睛是淡紫色；眼下一点暗紫；**淡紫色的嘴唇**，下巴尖。
  - 淡紫色只用在眼睛和嘴唇上。
- **身体**：
  - **灰蓝色的高领长外套**，分 3 档，下摆到大腿；**紫色的里领**立在脖子两边。
  - **很宽的青绿色围巾**（亮青绿、青绿、深青绿 3 档）绕过脖子，两条长尾巴垂到膝盖下面，末端带一点紫。
  - 胸口的**金色月牙扣**（2–3 格），腰上的**紫色绳腰带**。
  - 举到脸边的手戴**黑手套**，手腕上一串**金色珠子手链**（2–3 颗，每颗约 2 格）。
  - **深藏青色的紧身裤**，**黑色尖头长靴**。
- **通碧**：冰蓝月石金属，亮白蓝、冰蓝、蓝紫 3 档，两片长刃之间留一条缝看得出是两片；握把和接口是深青灰色；刃口内侧一两格青绿。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。

## 要画清楚的地方（武器表）

- 五把都是冰蓝月石金属（亮白蓝、冰蓝、蓝紫 3 档），接口和握把深青灰色，每把只在刃口内侧一两格带自己的颜色：**通碧 青绿、断魄 红、坠明 紫、荧焰 蓝、折镜 白**。
- **通碧**：细长步枪，两片并排的长月牙刃 + 弯握把。**断魄**：镰刀形手枪，一片弯月刃包着小握把。**坠明**：开口朝上的月牙炮，旁边浮一颗星形小部件（单独一块，和炮之间空 1–2 格）。**折镜**：两片弯刃 + 中间圆环握把。**荧焰**：两片大翼刃向两边展开 + 中间弯握把。
- 每把一圈近黑外描边。

## 干净

- 和附图 7–10（本包的卡特琳娜、杰斯、斯莫德都是每游戏像素 1.5 格，卡莉丝塔 1.4 格；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 颜色照 A。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `aphelios_model_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A.png` | 你第 0 步画的 A（用户选定） | **样子、颜色、细节**全照它 |
| `2_target_body.png` | A 按新比例（头约四分之一）缩到游戏大小、每格 12 px 放在画布上（糊的） | **他的大小、位置、姿势、头身比**照它，糊的地方重画 |
| `3_layout.png` | 同一张加网格线：绿线 = 头顶 y 240，蓝线 = 下巴 y 420，红线 = 脚底 y 960 | 对齐网格、头和脚底的位置 |
| `4_head.png` | A 的头（读回后 8 倍放大） | 头发、刘海、脸、眼睛 |
| `5_picked_W.png` | 你第 0 步画的武器表 | 五把武器的**样子** |
| `6_target_weapons.png` | 武器表按他的比例缩好、每格 12 px 放在画布上（糊的） | 武器表的**大小和摆法** |
| `style/7_style_katarina.png` … `10_style_kalista.png` | 本包的卡特琳娜、杰斯、斯莫德（每游戏像素 1.5 格）、卡莉丝塔（1.4 格），8 倍放大 | **只看风格**：这个密度下一格有多大、脸怎么画、描边、分档 |

## 提示词 1：`aphelios-model-1.png`、`aphelios-model-2.png`（他，两稿）

附全部 10 张图。**用 image_gen 画。**

```text
Attached images: 1 an approved pixel-art picture of this character - a slender pale young man with black hair and a long fringe over one eye, a slate grey-blue high-collared long coat, a very wide teal scarf with long tails, a purple collar and rope belt, a small golden crescent clasp, dark navy trousers and pointed black boots, black gloves with a golden bead bracelet, and a long ice-blue moonstone rifle (two parallel crescent blades) resting upright behind his near shoulder (the LOOK, the COLOURS and the DETAILS to keep); 2 the same man shrunk to his final game size on a 1024x1024 canvas, 12 px a square, with his HEAD MADE BIGGER - about a quarter of his height - the SIZE, the PLACE, the POSE and the HEAD-TO-BODY PROPORTION are right, but it is muddy (the face and eye blurred, the hair highlights lost, the coat, scarf, clasp, bracelet and the rifle's two blades smeared together, a seam at the neck); 3 the same with grid lines every 5 squares: the green line = the top of his hair (y 240), the blue line = his chin (y 420), the red line = his soles (y 960); 4 the head of image 1 enlarged; 5 his five weapons as drawn before; 6 the weapon sheet at his scale (for the other picture); 7-10 STYLE ONLY: other characters from the same game at this same square density, shown 8x so every square is one pixel - copy their pixel-art look.
Draw with the image generator ONE clean pixel-art picture of the same man: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 12 px, aligned on one straight grid starting at the canvas corner, the top of his hair at y 240 (the short tuft a few squares above it), his chin at y 420 (the head from the hair's top to the chin about 15 squares, a quarter of his height - much bigger than in image 1, so the face reads at game size), his soles at y 960 on one ground line; the rifle upright behind his near shoulder, its tip about 5 squares above his head, about 47 squares long; the near hand raised beside his face, the far arm down - as if a pixel artist redrew image 1 square by square on image 2's grid.
Make it CRISP and READABLE at this size: BLACK HAIR with a few blue-violet highlight squares, the LONG FRINGE falling across the eye on the image right, the short tuft at the back; a PALE face, the one visible HALF-CLOSED pale violet eye at least 2 squares wide with a drooping lid, a touch of dark violet under it, pale violet lips, a pointed chin; the SLATE GREY-BLUE HIGH-COLLARED LONG COAT in 3 shades down to the thighs, the PURPLE inner collar standing up at the neck; the VERY WIDE TEAL SCARF in 3 teal shades round the neck, its two long tails hanging below the knees with violet ends; the GOLDEN CRESCENT CLASP on the chest (2-3 squares), the PURPLE ROPE BELT; the raised hand in a BLACK GLOVE with a bracelet of 2-3 GOLDEN BEADS (about 2 squares each); DARK NAVY tight trousers, POINTED BLACK BOOTS; the rifle CALIBRUM in ice-blue moonstone (bright white-blue, ice blue, blue-violet), a 1-square gap showing its TWO PARALLEL BLADES, a dark teal-grey curved grip, one or two teal-green squares on the blades' inner edge.
One continuous near-black outline round the figure and the rifle; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing; the pale violet only for the eye and lips.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 提示词 2：`aphelios-weapons-1.png`、`aphelios-weapons-2.png`（武器表，两稿）

附同样 10 张图。**用 image_gen 画。**

```text
Same attached images. Draw with the image generator ONE clean pixel-art picture of his FIVE WEAPONS alone (image 5's weapons, at the size and layout of image 6): a 1024x1024 PNG with a real transparent background (alpha only 0 or 255), every square 12 px aligned on one straight grid starting at the canvas corner, each weapon at the same scale as the rifle in image 2 (the rifle about 47 squares long), at least 3 empty squares between any two.
Top row, left to right: CALIBRUM upright - a slim rifle of two long parallel crescent blades with a curved grip between them; SEVERUM - a scythe-shaped pistol, one curved blade round a small grip; GRAVITUM - a moon cannon like a big crescent cup opening upward, with a small STAR-SHAPED piece floating beside it (a separate piece, 1-2 empty squares between); CRESCENDUM - a double-crescent chakram, two curved blades round a ring grip. Bottom row: INFERNUM - a wide flamethrower, two big wing blades spread to the sides with a curved grip in the middle.
All five of PALE ICE-BLUE MOONSTONE METAL in 3 shades (bright white-blue, ice blue, blue-violet), DARK TEAL-GREY joints and grips, each with one or two squares of its own colour on the inner edge of its blade: Calibrum teal-green, Severum red, Gravitum violet, Infernum blue, Crescendum white. One continuous near-black outline round each weapon; no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No character, no effects, no glow, no background, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **四张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**。
- 他：大小、位置、姿势和 `2_target_body.png` 一样：头顶 y 240、下巴约 y 420、脚底 y 960、每格 12 px、对齐网格；**头约占身高四分之一**，身体仍然清瘦；露出的那只眼睛清楚；围巾、外套、月牙扣、金珠手链、通碧的两片刃清楚；外描边连续。
- 武器表：五把都在，和他同一个比例（通碧约 47 格长），摆法照 `6_target_weapons.png`，彼此分开至少 3 格；坠明的星星单独一块；每把刃口内侧带自己的颜色。
- 颜色照 A；没有任何特效。
- 如果模型不肯画有名字的角色，提示词里本来就没有名字，只有外观描述。

## 交付（`outputs/aphelios-model/`）

- `aphelios-model-1.png`、`aphelios-model-2.png`、`aphelios-weapons-1.png`、`aphelios-weapons-2.png`；**image_gen 的原始生成图原样放 `outputs/aphelios-model/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/aphelios_model_done.zip`，这样我这边知道已经交付完了。中间不要停，四张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（regrid / k-means 调色板），和 `2_target_body.png` 并排、按游戏大小和金克丝、卡莎、卡莉丝塔、德莱厄斯放一起给用户挑一稿（用户审核，不要自己判定）。武器表两稿也一起给用户挑。
- 选定后写第 2 步动作包：**待机由 Codex 画**（潘森的教训：待机要和动作帧同一比例、同样的站姿），每帧在同样的格子上画（每游戏像素 1.5 格，不再缩放）；五把武器是刚体部件，动作里只平移、整块转直角，不变形；跑步照英雄联盟（aphelios_A_Run1，通碧）；普攻五套（aphelios_A..E_Attack1：通碧、断魄、坠明、荧焰、折镜）；Q 五套（A_Spell1_Attack1 / B_Spell1 / C_Spell1 / D_Spell1A / E_Spell1）；W 换枪（A_Spell2）；R（aphelios_spell4）；死亡（aphelios_death）。
