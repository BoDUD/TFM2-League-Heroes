# 卡萨丁（虚空行者）：在格子上画造型——侧身版 + 待机正面版（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 A（`kassadin/2_picture.png`：两手张开垂在身体两侧、近侧掌心朝上，长袍拖地）。
> **为什么要画侧面**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面站着，被用户全部退回。所以这一轮**同一个造型画两个角度**：
> - **侧身版 `side`（最重要，所有动作都从它来）**：身体转向画面右边——胸口、肩甲、长袍都侧过来朝右（近侧肩甲在前、远侧肩甲大半藏在后面），背后的金属罐露在画面左边；近侧手臂垂在身前、手看得见，远侧手臂大半在身后；**长袍从侧面看是一个往后（画面左边）张开的斜三角**，前面（画面右边）的下摆直一些，后面的下摆尖角拖得更远；看不到腿脚。**头盔面具保持和正面版一样的 3/4 角度（两只橙色眼睛都看得见）**——本包的规矩是所有动作帧都用待机那一张脸，不另画侧脸。英雄联盟里他转过去的样子见 `8_league_side.png`（第一帧最像）。
> - **正面版 `front`（只用于待机和选人卡片）**：照原画 A 的 3/4 正面朝右站姿。
>
> **两个版本必须是同一个人**：同样的格子大小、同样的头身比、同样的颜色和细节，只是身体转了个角度；高度一样。

## 大小和位置（两个版本一样）——这次画成游戏尺寸的 2 倍

- 画布 **1024 × 1536，固定 13 × 13 px 的格子**（78 列 × 118 行，右边 10 px、下面 2 px 留透明）。**每个格子一个颜色，格子必须对齐画布左上角**——这是游戏尺寸的 2 倍：交回后我按 2×2 格子合成游戏里的 1 格，所以**不要先画大图再缩小**（上一个英雄古拉加斯就是这样：你自己缩出来的版本是糊的，原稿是清楚的，最后用的是原稿 2:1 逐格描的版本——见 `4_example_raw.png` 和 `5_example_sprite.png`）。
- **角尖到长袍最低点 80 行**：两只角的最高处在**第 20 行**（绿线），长袍下摆最低的尖在**第 99 行**（红线下沿）。长袍正中间在**第 39 列**（蓝线）。
- `1_guide_grid.png` 是原画 A 直接缩到这个大小、放在格子上的样子（糊的）：**只用来看大小、姿势和位置**，颜色和形状不要照它。侧身版画在空格子 `9_empty_grid.png` 上，同样的行和列。
- **宽度**：正面版连张开的两只手**不超过 56 格**（游戏里 28 格），侧身版**不超过 48 格**。
- **头按原画的比例，不要 Q 版**：头盔顶（不算角）到呼吸罩下沿约 16 行，角再往上约 5 行；两只**橙色眼睛各至少 2×2 格**、中间隔着面具的银灰竖条，要在缩到一半后还看得清（各 1 格亮橙）。参考 `6_quality_bar.png` 里本包的英雄（古拉加斯、泽拉斯、维克托、辛德拉、艾瑞莉娅）。

## 长相（照原画 A，头照英雄联盟的模型）

- **头**：**深紫色的头盔面具**，两边各一只**向上弯的深紫色大角**（亮暗三档，角上几道横纹），面具中间一条**银灰色金属竖条**（带两三个亮铆钉），竖条两边**一对发光的橙色眼睛**（全身最亮：中心亮黄白、外圈橙）；面具两侧各一根往外的尖刺；嘴的位置是**银灰色的金属呼吸罩**，从它垂下**四五根黑紫色的粗软管**（每根 2 格宽，亮暗两档），像胡子一样垂到胸口、两边弯到肩后。**面具照 `3_league_head.png` 和 `7_parts.png`**。
- **身体**：**赤裸的上身，青蓝色皮肤**（亮部浅青、暗部深青蓝），胸肌、腹肌用暗一档的线分块；**双手是更浅的发光青色**，手指细长张开（每根手指 1–2 格宽）；**两个深紫色肩甲**，每个上面竖着**一只大的银灰色弯骨刺**（像弯刀，带亮边）；前臂套着**深紫色护腕**，银灰镶边、外侧几根小银刺；**背后一排黑灰色金属罐**（从肩后露出来，带软管接口）。
- **下半身**：**很长的深紫色多层长袍**从腰拖到地，三四层往下张开，每层下摆是**尖角**，镶**银灰色的边**（2 格宽，亮暗两档）；腰上深色腰带，前面一块**带紫色宝石的尖角护片**；**看不到腿和脚**，长袍下摆的尖就是最低点。
- 去掉这个尺寸看不清的细节：每个细节至少一整格；不要小于一格的东西。

## 干净

- 每个 13 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光），一圈 2 格（缩小后 1 格）近黑描边，**里面少用黑**（内部分界用材质自己的暗色）；不要抖动、渐变、碎点；**最多约 24 色**。
- 颜色要分开：头盔、角、长袍、肩甲是**深紫**（亮紫高光 + 近黑紫暗部）；皮肤**青蓝**（浅青高光 + 深青蓝暗部）；手**更浅的发光青**；骨刺、镶边、竖条、呼吸罩**银灰**；眼睛**橙**；软管和金属罐**黑灰 / 黑紫**。**深紫长袍和黑紫软管、近黑描边要分得开**——长袍里多用亮一点的紫，暗部不要直接变成描边的颜色。
- **长袍最低点以下什么都不能有**（游戏在脚下画血条）。背景真透明。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `kassadin_model_pack.zip` 里；一次只能附五张时先附 1、2、3、8、4）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_guide_grid.png` | 原画 A 缩到 80 行放在 13 px 格子上（糊），黄线是量格子用的；绿线 = 角尖第 20 行，红线 = 下摆第 99 行下沿，蓝线 = 长袍中间第 39 列 | **大小、姿势、位置**（不要照它的颜色和形状，不要画线） |
| `2_picture.png` | 用户选的原画 A | **长相、配色、部件** |
| `3_league_head.png` | 英雄联盟模型的头（本地渲染） | **角、面具竖条、橙色眼睛、呼吸罩和软管——他的特色** |
| `4_example_raw.png` | 古拉加斯：你上次画的原稿（每格两倍大、清楚） | 怎么画：每格一个颜色，不要糊 |
| `5_example_sprite.png` | 古拉加斯定稿（就是那张原稿 2:1 逐格描的），放大 8 倍 | 缩成游戏尺寸后要达到的干净程度 |
| `6_quality_bar.png` | 用户认可的英雄（古拉加斯、泽拉斯、维克托、辛德拉、艾瑞莉娅），8 倍，同一条脚底线 | 像素大小、头身比、干净程度 |
| `7_parts.png` | 原画 A 的头和近侧的手，放大 | 角、面具、软管、手的形状和颜色 |
| `8_league_side.png` | 英雄联盟模型转到侧面朝右（待机、跑步两帧） | **侧身版怎么转**：肩甲一前一后、背后的罐子、长袍往后张开 |
| `9_empty_grid.png` | 空格子，同样的行列标线 | 侧身版的画布 |

## 提示词（四张图：正面 A、B 两稿，侧身 A、B 两稿；同一稿号的正面和侧身是同一个人）

```text
Attached images: 1 a blurry guide - the approved picture brought straight down to the drawing's size on a fixed grid of 13x13-pixel squares (a yellow measuring grid; green line = row 20, red line = the bottom of row 99, blue line = column 39) - use it ONLY for the size, the pose and the place, not for its colours or shapes; 2 the approved picture of this character (the user's pick) - copy his LOOK; 3 his head on his in-game 3D model - copy his HELMET MASK; 4 another character's drawing of yours on such a grid, approved - copy that way of working: every square one flat colour, crisp, no blur; 5 that drawing brought down 2:1 to game size, enlarged 8x - the clean look it must keep at game size; 6 heroes of this game at game size, approved - match their proportions and clean look; 7 the picture's head and near hand, big; 8 his 3D model turned to the side, facing right - how he looks SIDE-ON; 9 an empty grid with the same lines.
Draw him on a FIXED GRID of 13x13-pixel squares aligned to the canvas edges - TWICE the game size, so that every 2x2 block of squares later becomes one game pixel: one 1024x1536 PORTRAIT PNG per drawing with a real transparent background (78 columns x 118 rows; the right 10 px and the bottom 2 px transparent). Draw directly on this grid - do NOT draw a bigger picture and shrink it (that blurs). The figure is exactly 80 squares tall: the tips of his horns on row 20, the lowest point of his robe on row 99; the robe's middle on column 39. Nothing below row 99.
The character: Kassadin, the Void Walker, a tall, broad void mage. HEAD: a DARK-VIOLET HELMET MASK with TWO BIG DARK-VIOLET HORNS curving upward (three shades, a few ridges), a SILVER-GREY METAL STRIP down the middle of the mask with two or three bright rivets, on both sides of it a pair of GLOWING ORANGE EYES (each at least 2x2 squares, a pale yellow-white centre and orange round it - the brightest thing on him), a short spike out of each side of the mask, a SILVER-GREY METAL BREATHING GUARD over the mouth with four or five THICK BLACK-VIOLET HOSES (2 squares wide, two shades) hanging from it over his chest like a beard and curving back over the shoulders. BODY: a BARE MUSCULAR CHEST AND ARMS with CYAN-TEAL SKIN (pale cyan highlights, deep teal-blue shadows, the muscle blocks split by a darker shade), the HANDS a PALER GLOWING CYAN with long open fingers (1-2 squares wide each); two DARK-VIOLET SHOULDER PLATES, each with ONE BIG CURVED SILVER-GREY BONE SPIKE standing up like a scimitar (a bright edge); dark-violet bracers with silver trim and small silver spikes; a row of DARK-GREY METAL CANISTERS on his back showing over the shoulders. LOWER BODY: a VERY LONG DARK-VIOLET ROBE in three or four layers flaring down to the ground, every hem cut into POINTED TIPS and trimmed in SILVER-GREY (2 squares, two shades); a dark belt with a pointed front plate holding a violet gem; NO LEGS OR FEET SHOW - the robe's lowest tip is his lowest point.
Proportions: the picture's own proportions, NOT chibi: from the top of the helmet (without the horns) to the bottom of the breathing guard about 16 rows, the horns about 5 rows more above it; tall and broad like the heroes in image 6.
Clean like images 4 and 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black outline 2 squares thick round the silhouette and little black inside (inner edges in each material's own dark shade), every detail at least 2x2 squares, no specks, no dithering, no gradients, at most about 24 colours; the dark-violet robe, the black-violet hoses and the outline clearly apart (the robe mostly in its lighter violets). No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
TWO VIEWS of the SAME character (the same square size, proportions, colours and details, the same height):
FRONT (kassadin-front-<X>.png): the approved picture's pose (image 2): standing tall in 3/4 FRONT view facing image right, the mask toward the viewer with both eyes visible, both hands hanging open at his sides, the near one palm up with the fingers spread; at most 56 squares wide including the hands.
SIDE (kassadin-side-<X>.png) - the view every action of the game is drawn from: the BODY TURNED TO FACE THE IMAGE RIGHT, as his model in image 8 (the first frame): the chest, the shoulder plates and the robe side-on - the near shoulder plate in front, the far one mostly hidden behind, the canisters on his back on the image left; the near arm hanging in front of him with the hand visible, the far arm mostly hidden; the robe seen from the side as a slanting triangle flaring BACK to the image left (its front hem steeper, its back tips trailing further); no legs or feet. THE HEAD STAYS THE SAME 3/4 MASK AS IN THE FRONT VIEW, both orange eyes visible (every frame of this game keeps the idle's face - no separate profile face), only placed on the side-on body; at most 48 squares wide.
Make TWO takes, A and B, that differ mainly in small details of the mask and the robe; for each take draw both views (front A + side A, front B + side B). For every picture also deliver a game-size copy (every 2x2 block of squares one pixel: 39x59, nearest colour of the block, transparency kept) - but the 13-px drawing is the one that counts.
Before finishing, check every picture: exactly 80 rows from the horn tips (row 20) to the robe's lowest tip (row 99), the robe's middle on column 39, nothing below row 99; every 13x13 square one colour, aligned to the canvas edges; alpha only 0/255; at most ~24 colours; the horns, the orange eyes, the silver strip, the breathing guard and the hoses readable at half size; the SIDE view's body really turned to the right (shoulder plates one behind the other, robe flaring back, canisters on the image left) with the SAME 3/4 mask as the FRONT view.
```

## 交付（`outputs/kassadin-model/`）

- `kassadin-front-A.png`、`kassadin-side-A.png`、`kassadin-front-B.png`、`kassadin-side-B.png`（1024 × 1536，13 px 格子）和各自的 `_1x.png`（39 × 59）；
- `kassadin-model-compare.png`：四张并排，旁边放原画 A 的头；
- 生图原稿（`raw/`，**一定要交**：之前就是原稿最清楚）、`generation-prompts.txt`、色板、`HANDOFF.md`（**最后写**：每张的高度、宽度、色数、每格是否单色、哪里没做到）；最好再打成 `kassadin_model_pack_done.zip`。

## 交回前自查

- [ ] 四张都是 80 行（角尖第 20 行到长袍最低点第 99 行），长袍中间第 39 列，下摆下面没有像素；
- [ ] 每格（13 px）一个颜色、格子对齐画布、透明度只有 0/255、不超过约 24 色、只有一种近黑描边、里面少用黑；
- [ ] 头按原画比例（头盔顶到呼吸罩约 16 行，角再 5 行），橙色眼睛各至少 2×2，不要 Q 版；
- [ ] 正面版连手不超过 56 格宽，侧身版不超过 48 格；
- [ ] **侧身版身体真的转向右边**：肩甲一前一后、罐子在画面左边、长袍往后张开；**头还是正面版那张 3/4 面具**；和正面版是同一个人；
- [ ] 角、面具竖条、橙眼、呼吸罩和软管、青蓝赤裸上身、浅青手、肩甲骨刺、护腕、背后的罐子、多层尖角长袍 + 银灰镶边、腰前宝石护片；看不到腿脚；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读原稿 `raw/` 和 13 px 大图（核对每格单色），按 2×2 格子合成游戏尺寸（错开一格使平票最少，描边仍是一格；古拉加斯的 `trace_gragas.py` 的做法），40 行，放回 128 画布（下摆第 99 行，长袍中间第 64 列），一圈描边整理；正面和侧身并排、和原画 A、本包英雄一起给用户挑；只修用户指出的地方。**绝不靠删躯干行来缩小**；要缩小用 `addons/league_main/src/hd.rs` 的 SIZES（他是 1 倍，没有 PPU，需要时再问）。
- 第 2 步动作帧：**除待机外全部从侧身版画**（侧身朝右，同一张 3/4 面具；虚空刃是 W 的特效，不画在身体上；手臂不拉长；长袍飘着走，不画腿），待机用正面版。
