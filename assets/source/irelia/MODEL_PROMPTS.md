# 艾瑞莉娅：在游戏格子上画造型——侧身版 + 待机正面版（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画 B（`irelia/2_picture.png`：飞刃收成一束竖在背后，两手自然垂下）。
> **为什么要画侧面**：本包所有英雄除了待机，每个动作都是**侧身朝右**（和 oppi 的《League of Legends Reborn》一样）。上一个英雄诺提勒斯的造型只画了正面，动作帧全成了正面站着、头盔贴上去把身体盖住，被用户全部退回（用户：「我现在完成的所有英雄都是侧面吧 除了待机姿势」「你得做侧面的吧」）。所以这一轮**同一个造型画两个角度**：
> - **侧身版 `side`（最重要，所有动作都从它来）**：身体转向画面右边——脸是朝右的 3/4 侧脸（近侧眼睛完整、远侧眼睛窄或看不见，鼻尖和下巴朝右），近侧肩甲在前、远侧肩甲一半在身后；**两腿一前一后侧着站**（近侧腿在前、靴尖朝右，远侧腿在后），不是正面八字站；两只手臂垂在身侧（近侧手臂在身体前面看得见）；**飞刃那一束竖在背后**（画面左侧，从肩膀上方到大腿），长马尾垂在背后。英雄联盟里她转过去的样子见 `8_league_side.png`（第一帧最像）。
> - **正面版 `front`（只用于待机和选人卡片）**：照原画 B 的 3/4 正面朝右站姿，飞刃一束在背后。
>
> **两个版本必须是同一个人**：同样的格子大小、同样的头身比、同样的颜色和细节，只是转了个角度；高度一样。

## 大小和位置（两个版本一样）

- 画布 **1024 × 1536，固定 26 × 26 px 的格子**（39 列 × 59 行，右边 10 px、下面 2 px 留透明）——和你之前给格温画的一样（`4_example_picture.png` / `5_example_sprite.png`）。
- **头顶尖饰到鞋底 37 行**：头顶那根深红尖角发饰的尖在**第 15 行**（绿线），**鞋底在第 51 行**（红线下沿）；飞刃尖最高到**第 12 行**（橙线），不能更高。两脚中间在**第 19 列**（蓝线）。
- `1_guide_grid.png` 是原画 B 直接缩到这个大小、放在格子上的样子（糊的）：**只用来看大小、姿势和位置**，颜色和形状不要照它。侧身版画在空格子 `9_empty_grid.png` 上，同样的行和列。
- **头大一点（游戏比例，但不要 Q 版）**：原画里头只有身高的 1/5，缩到 37 行脸只有 5 格、看不清眼睛。请画成**头顶尖饰到下巴 11 行左右**（尖饰 2 行 + 头发到下巴 9 行；脸 6–7 行高，眼睛清楚），身体和腿相应短一点，总高度还是 37 行。参考 `6_quality_bar.png` 里本包的英雄（泽丽也是 37 行）。
- 宽度：正面版不超过 **24 格**，侧身版不超过 **22 格**（飞刃束包括在内）。

## 长相（照原画 B，脸照英雄联盟的模型）

- **头**：很长的**深靛蓝头发**（亮蓝紫高光），前额一条**银色头冠**（中间一个 V 形尖），**头顶一根深红色、银边的尖角发饰**，两侧各一个小的银色角饰；长发在背后垂到腰下。**脸（这一轮最重要的细节）照 `3_league_face.png`**：**粗而有棱角的深靛蓝眉毛**（坚定、冷静）、**青蓝色的眼睛**（眼白 + 青蓝瞳 + 一格白高光，上眼线是深色）、**红色的嘴唇**（2 格）、白皙偏暖的皮肤。
- **身体**：**银白色的肩甲**（边缘向外卷成钩），深红紧身衣 + **银色胸甲**（胸口一个深红心形），**领口一颗青蓝宝石**；腰前垂下一条**深红长前摆**（到大腿，下端银色尖角）；深红护臂 + 银色护腕；**深藏青紧身裤**；**深红长靴**，膝盖上一个**银色尖角护膝**，靴口和鞋跟是银色。
- **飞刃**：几把**弯月形的长刃收成一束**竖在背后（刃面深藏青 + 深红、刀背和刃尖银白、刃根一颗青蓝宝石），刃尖朝上，在肩膀旁边露出来。
- 去掉这个尺寸看不清的细节：盔甲上的花纹 = 不画或 1 格深红线；每把飞刃最少 2 格宽；宝石 = 2×2 青蓝块（一格亮）；不要小于一格的东西。

## 干净（和格温那次一样）

- 每个 26 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光），一圈 1 格近黑描边，**里面少用黑**（内部分界用材质自己的暗色）；不要抖动、渐变、碎点；**最多约 24 色**。
- 颜色要分开：头发深靛蓝 + 亮蓝紫高光；衣服深红 + 洋红高光；盔甲和刀背银白 + 冷灰蓝暗部；飞刃深藏青 + 深红；裤子深藏青（带一道亮边，不要糊成黑块）；眼睛和宝石青蓝（青蓝只用在眼睛和宝石上）；皮肤白皙偏暖。
- **鞋底以下什么都不能有**（游戏在脚下画血条）。背景真透明。不要网格线、文字、编号、边框、影子、特效。

## 附图（压缩包 `irelia_model_pack.zip` 的 `irelia/` 里；一次只能附五张时先附 1、2、3、8、4）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_guide_grid.png` | 原画 B 缩到 37 行放在 26 px 格子上（糊），黄线是量格子用的；绿线 = 尖饰尖第 15 行，橙线 = 飞刃最高第 12 行，红线 = 鞋底第 51 行下沿，蓝线 = 两脚中间第 19 列 | **大小、姿势、位置**（不要照它的颜色和形状，不要画线） |
| `2_picture.png` | 用户选的原画 B | **长相、配色、部件** |
| `3_league_face.png` | 英雄联盟模型的脸（本地渲染） | **眉毛、眼睛、嘴唇、头冠——她的特色** |
| `4_example_picture.png` | 格温：你上次在 26 px 格子上画的图（用户认可） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张 1 倍图放大 8 倍 | 干净程度 |
| `6_quality_bar.png` | 用户认可的英雄（格温、泽丽、辛德拉、萨勒芬妮、莎弥拉），8 倍，同一条脚底线 | 像素大小、头身比、干净程度 |
| `7_parts.png` | 原画 B 的头和背后的飞刃束，放大 | 头冠、发饰、飞刃的形状和颜色 |
| `8_league_side.png` | 英雄联盟模型转到侧面（待机、跑步两帧、普攻） | **侧身版怎么转**：脸、肩甲、腿一前一后 |
| `9_empty_grid.png` | 空格子，同样的行列标线 | 侧身版的画布 |

## 提示词（四张图：正面 A、B 两稿，侧身 A、B 两稿；同一稿号的正面和侧身是同一个人）

```text
Attached images: 1 a blurry guide - the approved picture brought straight down to game size on a fixed grid of 26x26-pixel squares (a yellow measuring grid; green line = row 15, orange line = row 12, red line = the bottom of row 51, blue line = column 19) - use it ONLY for the size, the pose and the place, not for its colours or shapes; 2 the approved picture of this character (the user's pick) - copy her LOOK; 3 her face on her in-game 3D model - copy her FACE'S CHARACTER; 4 and 5 another character drawn correctly on such a grid and that sprite at 1x enlarged 8x - copy that way of working: every square one flat colour, big clean areas, no half squares; 6 heroes of this game at game size, approved - match their pixel size, head-to-body proportions and clean look; 7 the picture's head and the blade bundle, big; 8 her 3D model turned to the side - how she looks SIDE-ON; 9 an empty grid with the same lines.
Draw her as a small game sprite on a FIXED GRID of 26x26-pixel squares aligned to the canvas edges: one 1024x1536 PORTRAIT PNG per drawing with a real transparent background (39 columns x 59 rows; the right 10 px and the bottom 2 px transparent). The figure is exactly 37 squares tall: the tip of the crimson crest on top of her head on row 15, the soles on row 51; the folded blades may reach up to row 12, never higher; the middle between her feet on column 19. Nothing below row 51.
The character: Irelia, the Blade Dancer, a calm, resolute warrior woman. Very long DARK INDIGO-BLUE hair (bright blue-violet highlights) falling down her back past her waist, a SILVER TIARA band across her forehead with a V point, a tall CRIMSON CREST SPIKE edged in silver on top of her head and a small silver horn ornament at each side; SILVER-WHITE SHOULDER GUARDS curling outward into hooks; a crimson bodysuit with a SILVER BREASTPLATE (a crimson heart shape on the chest) and a CYAN GEM at the collar; a long CRIMSON TABARD hanging in front to her thighs with a silver pointed tip; crimson bracers with silver cuffs; DARK NAVY LEGGINGS (with a lit edge, not a black block); CRIMSON BOOTS with a pointed SILVER KNEE GUARD, silver tops and heels. Her floating BLADES are FOLDED INTO ONE UPRIGHT BUNDLE BEHIND HER BACK (crescent blades, the flats dark navy and crimson, the spines and tips silver-white, a cyan gem at each root), the tips pointing up beside her shoulder; she holds no weapon.
Her FACE (image 3) - the most important detail: THICK, ANGULAR DARK INDIGO EYEBROWS (determined, calm), CYAN eyes with white, a cyan iris and a one-square white glint under a dark upper liner, RED lips (2 squares), fair warm skin. Game proportions, NOT chibi: from the crest tip to the chin about 11 rows (the crest 2 rows, the face about 6-7 rows tall so the eyes read clearly), the body and legs a little shorter to keep the total of 37 rows, slim and tall like the heroes in image 6.
Clean like image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black 1-square outline round the silhouette and little black inside (inner edges in each material's own dark shade), every detail at least one whole square (each blade at least 2 squares wide, the gems 2x2), no specks, no dithering, no gradients, at most about 24 colours; cyan only in the eyes and the gems. No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
TWO VIEWS of the SAME character (the same square size, proportions, colours and details, the same height):
FRONT (irelia-front-<X>.png): the approved picture's pose (image 2): standing in 3/4 FRONT view facing image right, the face toward the viewer with both eyes visible, both arms hanging relaxed with the hands visible, legs slightly apart, both boots flat on row 51, the blade bundle behind her back on the image-left side; at most 24 squares wide.
SIDE (irelia-side-<X>.png) - the view every action of the game is drawn from: the WHOLE BODY TURNED TO FACE THE IMAGE RIGHT, as her model in image 8 (the first frame): a 3/4 profile facing right - the near eye whole, the far eye narrow or hidden, the nose and chin pointing right, the tiara and crest turned with the head; the near shoulder guard in front, the far one partly behind her; the near arm hanging in front of her body with the hand visible, the far arm mostly hidden behind; the legs SIDE-ON, one in front of the other (the near leg in front, its boot pointing right; the far leg behind), both boots flat on row 51 - not the front view's wide stance; the blade bundle upright behind her back (image left), the long hair hanging behind; at most 22 squares wide.
Make TWO takes, A and B, that differ mainly in the face; for each take draw both views (front A + side A, front B + side B). For every picture also deliver its 1x copy (each 26x26 square one pixel: 39x59, nearest-neighbour, transparency kept) - the game reads the 1x file, so it must match the big one square for square.
Before finishing, check every picture: exactly 37 rows from the crest tip (row 15) to the soles (row 51), the blades not above row 12, the feet's middle on column 19, nothing below row 51; every 26x26 square one colour; alpha only 0/255; at most ~24 colours; the eyebrows, the cyan eyes and the red lips readable at 1x and 2x; the SIDE view really turned to the right (profile face, legs one in front of the other), the same person as the FRONT view.
```

## 交付（`outputs/irelia-model/`）

- `irelia-front-A.png`、`irelia-side-A.png`、`irelia-front-B.png`、`irelia-side-B.png`（1024 × 1536）和各自的 `_1x.png`（39 × 59）；
- `irelia-model-compare.png`：四张 1 倍图放大 8 倍并排，旁边放原画 B 的头；
- 生图原稿（`raw/`）、`generation-prompts.txt`、色板、`HANDOFF.md`（**最后写**：每张的高度、宽度、色数、每格是否单色、哪里没做到）；最好再打成 `irelia_model_pack_done.zip`。

## 交回前自查

- [ ] 四张都是 37 行（尖饰尖第 15 行到鞋底第 51 行），飞刃不高于第 12 行，两脚中间第 19 列，鞋底下面没有像素；
- [ ] 每格一个颜色、透明度只有 0/255、不超过约 24 色、只有一种近黑描边、里面少用黑；
- [ ] 头冠尖到下巴约 11 行，眉毛、青蓝眼睛、红唇清楚；不要 Q 版；
- [ ] **侧身版真的转向右边**：侧脸、近侧肩甲在前、两腿一前一后、靴尖朝右；和正面版是同一个人；
- [ ] 深靛蓝长发、银头冠 + 深红尖角发饰、银卷钩肩甲、银胸甲 + 青蓝宝石、深红前摆、深藏青裤、深红长靴 + 银尖角护膝、背后一束飞刃；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读 1 倍图（核对和大图逐格一致），放回 128 画布（鞋底第 99 行，两脚中间第 64 列），一圈描边整理（tidy_codex18 的规则），正面和侧身并排、和原画 B、本包英雄一起给用户挑；只修用户指出的地方。
- 第 2 步动作帧：**除待机外全部从侧身版画**（侧身朝右，飞刃是整块刚性的部件，只平移 / 90° 整转 / 翻转；手臂不拉长；腿是交叉步，不滑不变形；头不贴正面），待机用正面版；照诺提勒斯的 MODEL_STRIPS2.md 的规则。
