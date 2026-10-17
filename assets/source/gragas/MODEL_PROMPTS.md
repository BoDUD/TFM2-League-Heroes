# 古拉加斯（酒桶）：在游戏格子上画造型——侧身版 + 待机正面版（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 A（`gragas/2_picture.png`：大酒桶用粗绳背在背上、桶盖朝画面左边，两只拳头垂在身旁）。
> **为什么要画侧面**：本包所有英雄除了待机，每个动作都是**侧身朝右**（和 oppi 的《League of Legends Reborn》一样）。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以这一轮**同一个造型画两个角度**：
> - **侧身版 `side`（最重要，所有动作都从它来）**：整个人转向画面右边——脸是朝右的 3/4 侧脸（近侧眼睛完整、远侧眼睛窄或看不见，大鼻子和胡子朝右翘），大肚子朝右挺出来；近侧手臂垂在肚子前面、拳头看得见，远侧手臂大半在身后；**两腿一前一后侧着站**（近侧腿在前、脚尖朝右，远侧腿在后），不是正面八字站；**酒桶背在背上**（画面左边，从肩膀到腰），绳子从近侧肩膀斜过胸口。英雄联盟里他转过去的样子见 `8_league_side.png`（第一帧最像）。
> - **正面版 `front`（只用于待机和选人卡片）**：照原画 A 的 3/4 正面朝右站姿，酒桶在背后画面左边。
>
> **两个版本必须是同一个人**：同样的格子大小、同样的头身比、同样的颜色和细节，只是转了个角度；高度一样。

## 大小和位置（两个版本一样）

- 画布 **1024 × 1536，固定 26 × 26 px 的格子**（39 列 × 59 行，右边 10 px、下面 2 px 留透明）——和你之前给格温画的一样（`4_example_picture.png` / `5_example_sprite.png`）。
- **头顶到脚底 36 行**：光头最高处在**第 15 行**（绿线），**脚底在第 50 行**（红线下沿）；酒桶最高到**第 14 行**（橙线），不能更高。两脚中间在**第 22 列**（蓝线）。
- `1_guide_grid.png` 是原画 A 直接缩到这个大小、放在格子上的样子（糊的）：**只用来看大小、姿势和位置**，颜色和形状不要照它。侧身版画在空格子 `9_empty_grid.png` 上，同样的行和列。
- **整体收窄**：缩出来的样子宽 36 格，太宽了。**酒桶画小一点、贴紧后背**（约 12 格宽、13 格高），正面版连酒桶**不超过 30 格宽**，侧身版**不超过 26 格**。他本人还是很胖：**肚子是全身最宽的地方**。
- **头略放大（游戏比例，但不要 Q 版）**：原画里头很小，缩到 36 行脸只有 5–6 格、看不清眼睛。请画成**头顶到胡子上沿（鼻子下面）约 8 行**：光头 3 行、橙红浓眉 1 行、眼睛 1–2 行（眼白 + 深色眼珠，眯着）、大鼻子 2×2；**胡子从脸下面一直垂到肚子上（约第 31 行）**，编成两三股辫子，辫梢一格银灰铁环。身体和腿相应短一点，总高度还是 36 行。参考 `6_quality_bar.png` 里本包的大块头英雄（诺提勒斯、蛮王、瑟提、慎）。

## 长相（照原画 A，头照英雄联盟的模型）

- **头**：**光头**（淡肤色，头顶一格亮高光），**粗浓的橙红眉毛**压着**眯着的小眼睛**，**大鼻子**，尖尖的耳朵；**一大把橙红胡子**（亮橙 + 深红棕暗部），两边鬓角像火焰往外翘，下面编成辫子、辫梢银灰铁环。**脸照 `3_league_face.png`**：凶里带醉的表情。
- **身体**：**超大的圆肚子**、很宽的肩、很粗的手臂，**淡米黄皮肤**（亮部奶白、暗部棕灰），肚子上一个**暗红 X 形疤**（2–3 格）、肩膀上几道浅色疤；前臂、手腕、膝盖下缠着**棕色粗麻绳**（1 格宽的一圈，亮暗两档）；**拳头又大又粗**（每只至少 4×4 格）；**一根粗麻绳从远侧肩膀斜过胸口**拴着酒桶；**深蓝短裤**，下摆撕成锯齿；**光着两只大脚**（脚趾 1 格亮线分开）。
- **酒桶**：**暖棕色木板**（亮暗三档，木板之间 1 格深色缝）、**两道铁灰色铁箍**（带一两个亮铆钉）、**八角形的桶盖**朝画面左边，中间**一个 2×2 的浅色方木塞**。
- 去掉这个尺寸看不清的细节：皮肤上的小疤 = 不画或 1 格；绳子每圈 1 格宽；不要小于一格的东西。

## 干净（和格温那次一样）

- 每个 26 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光），一圈 1 格近黑描边，**里面少用黑**（内部分界用材质自己的暗色）；不要抖动、渐变、碎点；**最多约 24 色**。
- 颜色要分开：皮肤淡米黄 + 奶白高光 + 棕灰暗部；胡子眉毛橙红 + 亮橙 + 深红棕；短裤深蓝（带一道亮边）；绳子棕色两档；酒桶暖棕三档 + 铁灰箍；铁环银灰。**皮肤和绳子、酒桶的棕色要分得开**。
- **脚底以下什么都不能有**（游戏在脚下画血条）。背景真透明。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `gragas_model_pack.zip` 的 `gragas/` 里；一次只能附五张时先附 1、2、3、8、4）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_guide_grid.png` | 原画 A 缩到 36 行放在 26 px 格子上（糊），黄线是量格子用的；绿线 = 头顶第 15 行，橙线 = 酒桶最高第 14 行，红线 = 脚底第 50 行下沿，蓝线 = 两脚中间第 22 列 | **大小、姿势、位置**（不要照它的颜色和形状，不要画线；它太宽，酒桶要收小） |
| `2_picture.png` | 用户选的原画 A | **长相、配色、部件** |
| `3_league_face.png` | 英雄联盟模型的头（本地渲染） | **光头、浓眉、眯眼、大鼻子、编辫胡子——他的特色** |
| `4_example_picture.png` | 格温：你上次在 26 px 格子上画的图（用户认可） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张 1 倍图放大 8 倍 | 干净程度 |
| `6_quality_bar.png` | 用户认可的英雄（诺提勒斯、蛮王、瑟提、慎、格温），8 倍，同一条脚底线 | 像素大小、头身比、干净程度 |
| `7_parts.png` | 原画 A 的头和酒桶，放大 | 胡子辫子、铁环、酒桶的形状和颜色 |
| `8_league_side.png` | 英雄联盟模型转到侧面朝右（待机、跑步两帧），酒桶在背上 | **侧身版怎么转**：侧脸、挺出的肚子、两腿一前一后 |
| `9_empty_grid.png` | 空格子，同样的行列标线 | 侧身版的画布 |

## 提示词（四张图：正面 A、B 两稿，侧身 A、B 两稿；同一稿号的正面和侧身是同一个人）

```text
Attached images: 1 a blurry guide - the approved picture brought straight down to game size on a fixed grid of 26x26-pixel squares (a yellow measuring grid; green line = row 15, orange line = row 14, red line = the bottom of row 50, blue line = column 22) - use it ONLY for the size, the pose and the place, not for its colours or shapes (it is too wide: the keg must be smaller); 2 the approved picture of this character (the user's pick) - copy his LOOK; 3 his head on his in-game 3D model - copy his FACE'S CHARACTER; 4 and 5 another character drawn correctly on such a grid and that sprite at 1x enlarged 8x - copy that way of working: every square one flat colour, big clean areas, no half squares; 6 heroes of this game at game size, approved - match their pixel size, proportions and clean look; 7 the picture's head and the keg, big; 8 his 3D model turned to the side, facing right with the keg on his back - how he looks SIDE-ON; 9 an empty grid with the same lines.
Draw him as a small game sprite on a FIXED GRID of 26x26-pixel squares aligned to the canvas edges: one 1024x1536 PORTRAIT PNG per drawing with a real transparent background (39 columns x 59 rows; the right 10 px and the bottom 2 px transparent). The figure is exactly 36 squares tall: the top of his bald head on row 15, the soles on row 50; the keg may reach up to row 14, never higher; the middle between his feet on column 22. Nothing below row 50.
The character: Gragas, the Rabble Rouser, a huge, jolly, drunken brawler. A BALD HEAD (pale skin, one bright highlight square on top), BUSHY ORANGE-RED BROWS over small SQUINTING EYES (white + a dark pupil), a BIG NOSE (2x2), pointed ears, and a LONG ORANGE-RED BEARD (bright orange highlights, dark red-brown shadows) falling from under his nose down over his belly to about row 31, the sideburns flaring out like flames, the lower beard BRAIDED into two or three plaits each tied with a one-square SILVER-GREY IRON RING. BODY: an ENORMOUS ROUND BELLY (the widest part of him), very broad shoulders, very thick arms, PALE BEIGE SKIN (creamy highlights, brown-grey shadows), a dark-red X-shaped scar on the belly (2-3 squares), BROWN ROPE wound round the forearms, wrists and below the knees (one-square bands, two shades), HUGE FISTS (each at least 4x4 squares), a THICK BROWN ROPE across his chest from the far shoulder holding the keg; SHORT DARK-BLUE RAGGED SHORTS (a zigzag hem, a lit edge), BARE BIG FEET (toes split by one-square light lines). THE KEG on his back: warm brown wooden staves (three shades, one-square dark seams), two IRON-GREY HOOPS with a bright rivet or two, an OCTAGONAL LID facing the image left with a 2x2 PALE SQUARE CORK in its middle; about 12 squares wide and 13 tall, tucked close against his back.
Proportions: game proportions, NOT chibi, but the head a little bigger than in the picture so the face reads: from the top of the head to the moustache (under the nose) about 8 rows - bald dome 3 rows, brows 1 row, eyes 1-2 rows, the nose 2 rows; the beard then hangs to about row 31; the body and legs shorter to keep the total of 36 rows; a big heavy figure like the heroes in image 6.
Clean like image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black 1-square outline round the silhouette and little black inside (inner edges in each material's own dark shade), every detail at least one whole square, no specks, no dithering, no gradients, at most about 24 colours; skin, rope and keg browns clearly apart. No effects, no beer, no glow, no background, no ground, no shadow, no text, no grid lines.
TWO VIEWS of the SAME character (the same square size, proportions, colours and details, the same height):
FRONT (gragas-front-<X>.png): the approved picture's pose (image 2): standing in 3/4 FRONT view facing image right, the face toward the viewer with both eyes visible, both fists hanging at his sides, legs apart, both feet flat on row 50, the keg on his back on the image-left side with its lid and cork showing; at most 30 squares wide including the keg.
SIDE (gragas-side-<X>.png) - the view every action of the game is drawn from: the WHOLE BODY TURNED TO FACE THE IMAGE RIGHT, as his model in image 8 (the first frame): a 3/4 profile facing right - the near eye whole, the far eye narrow or hidden, the big nose and the beard pointing right; the belly pushed out to the right; the near arm hanging in front of the belly with the fist visible, the far arm mostly hidden behind; the legs SIDE-ON, one in front of the other (the near leg in front, its toes pointing right; the far leg behind), both feet flat on row 50 - not the front view's wide stance; the keg on his back on the image left (from the shoulders to the waist), the rope across his chest; at most 26 squares wide including the keg.
Make TWO takes, A and B, that differ mainly in the face; for each take draw both views (front A + side A, front B + side B). For every picture also deliver its 1x copy (each 26x26 square one pixel: 39x59, nearest-neighbour, transparency kept) - the game reads the 1x file, so it must match the big one square for square.
Before finishing, check every picture: exactly 36 rows from the top of the head (row 15) to the soles (row 50), the keg not above row 14, the feet's middle on column 22, nothing below row 50; every 26x26 square one colour; alpha only 0/255; at most ~24 colours; the brows, the eyes, the nose and the braided beard readable at 1x and 2x; the SIDE view really turned to the right (profile face, belly out to the right, legs one in front of the other), the same person as the FRONT view.
```

## 交付（`outputs/gragas-model/`）

- `gragas-front-A.png`、`gragas-side-A.png`、`gragas-front-B.png`、`gragas-side-B.png`（1024 × 1536）和各自的 `_1x.png`（39 × 59）；
- `gragas-model-compare.png`：四张 1 倍图放大 8 倍并排，旁边放原画 A 的头；
- 生图原稿（`raw/`）、`generation-prompts.txt`、色板、`HANDOFF.md`（**最后写**：每张的高度、宽度、色数、每格是否单色、哪里没做到）；最好再打成 `gragas_model_pack_done.zip`。

## 交回前自查

- [ ] 四张都是 36 行（头顶第 15 行到脚底第 50 行），酒桶不高于第 14 行，两脚中间第 22 列，脚底下面没有像素；
- [ ] 每格一个颜色、透明度只有 0/255、不超过约 24 色、只有一种近黑描边、里面少用黑；
- [ ] 头顶到鼻子下面约 8 行，浓眉、眯眼、大鼻子、编辫胡子清楚；不要 Q 版；
- [ ] 正面版连酒桶不超过 30 格宽，侧身版不超过 26 格；肚子是最宽的地方；
- [ ] **侧身版真的转向右边**：侧脸、肚子朝右挺、两腿一前一后、脚尖朝右；酒桶在背上；和正面版是同一个人；
- [ ] 光头、橙红浓眉和长胡子（辫子 + 银灰铁环）、淡米黄皮肤 + X 形疤、棕绳（手臂、膝下、胸口斜挂）、深蓝锯齿短裤、光脚、木酒桶（铁箍、八角桶盖、方木塞）；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读 1 倍图（核对和大图逐格一致），放回 128 画布（脚底第 99 行，两脚中间第 64 列），一圈描边整理，正面和侧身并排、和原画 A、本包英雄一起给用户挑；只修用户指出的地方。
- 第 2 步动作帧：**除待机外全部从侧身版画**（侧身朝右，酒桶是整块刚性的部件，只平移 / 90° 整转 / 翻转；手臂不拉长；腿是交叉步，不滑不变形；头不贴正面），待机用正面版，两腿照 oppi 的做法（近腿在画面左全色、远腿在画面右暗一档高一行）。
