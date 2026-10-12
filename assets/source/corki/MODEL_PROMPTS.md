# 库奇（英勇投弹手）：在游戏格子上画造型——侧面版 + 待机正面版（第 1 步，给 Codex 的提示词）

> **这一轮只画造型，不画动作。** 用户选了原画第 2 张（`corki/2_picture.png`：库奇坐在钢蓝色怪兽头陀螺机里，3/4 正面朝右悬停，两副木螺旋桨，嘴里伸出格林机枪，下面两个黄红格子炸弹，左下机翼带锯齿）。
> **为什么要画侧面**：本包所有英雄除了待机，每个动作都是**侧身朝右**。之前一个英雄的造型只画了正面，动作帧全成了正面，被用户全部退回。所以这一轮**同一个造型画两个角度**：
> - **侧面版 `side`（最重要，所有动作都从它来）**：整架飞机转向画面右边——机头和格林机枪朝正右，机身侧面完整露出来，近侧机翼在前、远侧机翼大半被机身挡住，两副螺旋桨在机身后上方（侧面看桨叶是横的一条），推进器在画面左边，两个炸弹在机身下面一前一后。英雄联盟里他转过去的样子见 `8_league_side.png`（第一帧最像）。**飞行员的头和正面版完全一样**（同一张 3/4 脸：两片护目镜都看得到、八字胡两边都翘出来），只有飞机转了；本包的规矩是所有动作帧都用待机那一张脸。
> - **正面版 `front`（只用于待机和选人卡片）**：照原画第 2 张的 3/4 正面朝右。
>
> **两个版本必须是同一个角色**：同样的格子大小、同样的比例、同样的颜色和细节，只是飞机转了个角度；高度一样。

## 大小和位置（两个版本一样）

- 画布 **1536 × 1024 横版，固定 26 × 26 px 的格子**（59 列 × 39 行，右边 2 px、下面 10 px 留透明）——格子和你之前给格温画的一样（`4_example_picture.png` / `5_example_sprite.png`），只是画布横过来（他比人宽）。
- **螺旋桨最高处到炸弹最低处 30 行**：螺旋桨顶在**第 5 行**（绿线），炸弹底在**第 34 行**（红线下沿）。**第 35–37 行留空**——他**悬停在空中**，棕线（第 37 行下沿）是地面，游戏会在那里画一块小影子，你不要画影子。机身中间在**第 29 列**（蓝线），**整体不超过 40 格宽**（两条紫线之间）。
- `1_guide_grid.png` 是原画直接缩到这个大小、放在格子上的样子（糊的）：**只用来看大小、姿势和位置**，颜色和形状不要照它。侧面版画在空格子 `9_empty_grid.png` 上，同样的行和列。
- **飞行员放大（游戏比例，不要变成大头娃娃）**：原画缩到 30 行，飞行员的头只有 5 行，护目镜和胡子看不清。请把**飞行员画大**：**头盔顶（不算尖刺）到八字胡下沿约 9 行**——皮头盔 3 行、两片圆护目镜 2 行（每片约 3 × 2 格，黄色发光镜片 + 棕色镜框）、粉鼻子 1–2 格、**八字胡左右张开约 13 格宽**（白色 + 浅灰暗部，两端往上翘）；红围巾和绿衣服在胡子下面露 2 行。**螺旋桨和机翼相应收小**，总高度还是 30 行、宽度不超过 40 格。参考 `6_quality_bar.png` 里本包的英雄（格温、泽丽、泽拉斯、维克托、凯南、图奇）：像素大小、干净程度。

## 长相（照原画第 2 张，飞行员的头照英雄联盟的模型）

- **飞行员**（`7_parts.png` 左、`3_league_head.png`）：**棕色皮飞行头盔**（亮暗三档，一圈铜色铆钉带），头盔顶一格**银灰小尖刺**，脑后一根**红羽毛 / 红飘带**往后飘；**两片大圆护目镜**，**黄色发光镜片**（全身最亮的地方之一）；**粉色大鼻子**；**一大把白色八字胡**往两边张开、两端上翘（他的招牌）；脖子上**红围巾**往后飘；**橄榄绿飞行服**，**棕色手套**搭在机舱边。只露胸口以上。
- **飞机**（`7_parts.png` 右）：**钢蓝色、像张着嘴的怪兽头**——机头上下两排**锯齿状金属牙**（亮部浅蓝灰、暗部深蓝灰，铆钉 1 格）；嘴里伸出**深灰色多管格林机枪**（4 根枪管，枪口一圈 2×2 的孔），朝画面右边；机头上方两盏**金黄色六角灯**（像眼睛，发光）；机舱边一圈**棕色皮护垫**（圆滚的一条）；机身后上方**两根钢灰杆子**各顶一副**木头螺旋桨**（四片桨叶，黄褐色带浅色条纹，**静止**）；两侧**后掠的钢蓝机翼**（下面那片边缘带锯齿）；机尾**两个红色喷口的推进器**，用**黄铜管子**连到机身；机身下挂**两个黄红格子花纹的炸弹**，**棕色金属尖头**，尾巴上**黄铜小尾翼**。
- 去掉这个尺寸看不清的细节：铆钉 1 格或不画；格子花纹每格 1 格（黄红相间）；桨叶条纹 1 格；不要小于一格的东西。

## 干净（和格温那次一样）

- 每个 26 px 格子一个颜色，大块平涂，每种材质 3–4 档（左上方打光），一圈 1 格近黑描边，**里面少用黑**（内部分界用材质自己的暗色）；不要抖动、渐变、碎点；**最多约 28 色**。
- 颜色要分开：机身钢蓝（浅蓝灰 / 中蓝灰 / 深蓝灰）；机枪和牙的暗部深灰；灯和镜片金黄；头盔、护垫、手套棕色；胡子白 + 浅灰；围巾、羽毛、喷口红；衣服橄榄绿；螺旋桨黄褐木色；炸弹黄红 + 棕尖头；管子和尾翼黄铜。**头盔的棕和护垫的棕要分得开，胡子的白和机身的浅蓝灰要分得开**。
- **第 34 行以下什么都不能有**（他悬停，游戏在下面画影子和血条）。背景真透明。不要网格线、文字、编号、边框、影子、特效（枪口火光、喷口火焰、螺旋桨模糊圈都不要）。

## 附图（压缩包 `corki_model_pack.zip` 的 `corki/` 里；一次只能附五张时先附 1、2、3、8、4）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_guide_grid.png` | 原画第 2 张缩到 30 行放在 26 px 格子上（糊），黄线是量格子用的；绿线 = 螺旋桨顶第 5 行，红线 = 炸弹底第 34 行下沿，棕线 = 地面第 37 行下沿，蓝线 = 机身中间第 29 列，两条紫线 = 最宽 40 格 | **大小、姿势、位置**（不要照它的颜色和形状，不要画线；飞行员要比它大） |
| `2_picture.png` | 用户选的原画第 2 张 | **长相、配色、部件** |
| `3_league_head.png` | 英雄联盟模型的飞行员（本地渲染） | **头盔、护目镜、八字胡——他的特色** |
| `4_example_picture.png` | 格温：你上次在 26 px 格子上画的图（用户认可） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张 1 倍图放大 8 倍 | 干净程度 |
| `6_quality_bar.png` | 用户认可的英雄（格温、泽丽、泽拉斯、维克托、凯南、图奇），8 倍，同一条脚底线 | 像素大小、干净程度 |
| `7_parts.png` | 原画的飞行员（放大）和机头 + 格林机枪 | 头盔、护目镜、胡子；牙、灯、枪管 |
| `8_league_side.png` | 英雄联盟模型转到侧面朝右（待机、飞行两帧） | **侧面版怎么转**：机头朝右、机翼、螺旋桨、推进器、炸弹的位置 |
| `9_empty_grid.png` | 空格子，同样的行列标线 | 侧面版的画布 |

## 提示词（四张图：正面 A、B 两稿，侧面 A、B 两稿；同一稿号的正面和侧面是同一个角色）

```text
Attached images: 1 a blurry guide - the approved picture brought straight down to game size on a fixed grid of 26x26-pixel squares (a yellow measuring grid; green line = row 5, red line = the bottom of row 34, brown line = the ground under row 37, blue line = column 29, two purple lines = at most 40 squares wide) - use it ONLY for the size, the pose and the place, not for its colours or shapes (the pilot must be BIGGER than in it); 2 the approved picture of this character (the user's pick) - copy his LOOK; 3 the pilot's head on his in-game 3D model - copy the PILOT'S CHARACTER; 4 and 5 another character drawn correctly on such a grid and that sprite at 1x enlarged 8x - copy that way of working: every square one flat colour, big clean areas, no half squares; 6 heroes of this game at game size, approved - match their pixel size and clean look; 7 the picture's pilot and the craft's nose with the gatling gun, big; 8 his 3D model turned to the side, facing right - how the craft looks SIDE-ON; 9 an empty grid with the same lines.
Draw him as a small game sprite on a FIXED GRID of 26x26-pixel squares aligned to the canvas edges: one 1536x1024 LANDSCAPE PNG per drawing with a real transparent background (59 columns x 39 rows; the right 2 px and the bottom 10 px transparent). The figure is exactly 30 squares tall: the top of the propellers on row 5, the bottom of the bombs on row 34; rows 35-37 EMPTY (he hovers above the ground line under row 37; draw no shadow); the middle of the craft on column 29; at most 40 squares wide. Nothing below row 34.
The character: Corki, the Daring Bombardier, a small yordle pilot SITTING IN A LITTLE GYROCOPTER that hovers (no legs, no wheels). THE PILOT, shown from the chest up in the cockpit: a BROWN LEATHER FLYING HELMET (three shades, a band of copper rivets) with a one-square SILVER SPIKE on top and a RED PLUME streaming back; BIG ROUND GOGGLES with GLOWING YELLOW LENSES in brown frames; a big PINK NOSE; a HUGE WHITE HANDLEBAR MOUSTACHE (white, pale grey shadow) sweeping out wide on both sides with upturned ends - his trademark; a RED SCARF streaming back; an OLIVE-GREEN FLIGHT SUIT; BROWN GLOVES on the cockpit rim. THE CRAFT: a STEEL-BLUE body shaped like an OPEN-MOUTHED MONSTER HEAD - JAGGED METAL TEETH top and bottom at the nose, a DARK-GREY FOUR-BARREL GATLING GUN poking out of the mouth toward image right, two GOLDEN HEXAGONAL LAMPS on top of the nose like glowing eyes, a ROUND BROWN LEATHER PAD around the cockpit rim; behind and above, TWO STEEL POLES each holding a WOODEN FOUR-BLADED PROPELLER (ochre blades with pale stripes, STILL); SWEPT STEEL-BLUE WINGS on both sides, the lower one with a saw-toothed edge; two THRUSTERS with RED NOZZLES at the back joined by BRASS PIPES; under the body TWO YELLOW-AND-RED CHECKERED BOMBS with BROWN METAL NOSE CONES and small BRASS FINS.
Proportions: game proportions, NOT chibi, but the PILOT BIGGER than in the guide so his face reads: from the top of the helmet (not counting the spike) to the bottom of the moustache about 9 rows - helmet 3 rows, the two round goggles 2 rows (each lens about 3x2 squares), the nose 1-2 squares, the moustache spread about 13 squares wide; the scarf and the suit 2 rows below it; the propellers and the wings smaller to keep the total of 30 rows and at most 40 squares wide.
Clean like image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black 1-square outline round the silhouette and little black inside (inner edges in each material's own dark shade), every detail at least one whole square, no specks, no dithering, no gradients, at most about 28 colours; the helmet brown and the pad brown clearly apart, the moustache white and the hull's pale blue-grey clearly apart. No effects (no muzzle flash, no exhaust flame, no propeller blur), no background, no ground, no shadow, no text, no grid lines.
TWO VIEWS of the SAME character (the same square size, proportions, colours and details, the same height):
FRONT (corki-front-<X>.png): the approved picture's pose (image 2): hovering in 3/4 FRONT view facing image right, the nose and the gun toward the right front, the pilot's face toward the viewer with both goggles and both sides of the moustache visible, nothing covering the face.
SIDE (corki-side-<X>.png) - the view every action of the game is drawn from: the WHOLE CRAFT TURNED TO FACE THE IMAGE RIGHT, as his model in image 8 (the first frame): the nose, the teeth and the gatling gun pointing straight right, the craft's flank fully showing, the near wing in front and the far wing mostly hidden behind the hull, the two propellers on their poles behind and above the cockpit (seen edge-on their blades read as flat bars), the thrusters on the image left, the two bombs under the hull one ahead of the other. THE PILOT'S HEAD IS EXACTLY THE FRONT VIEW'S - the same 3/4 face, square for square (both goggles, both sides of the moustache); only the craft turns.
Make TWO takes, A and B, that differ mainly in the pilot's face and the hull's shading; for each take draw both views (front A + side A, front B + side B). For every picture also deliver its 1x copy (each 26x26 square one pixel: 59x39, nearest-neighbour, transparency kept) - the game reads the 1x file, so it must match the big one square for square. Draw directly on the 26-px grid; do NOT draw a bigger picture and shrink it down (that comes out muddy). Keep your raw generations in raw/.
Before finishing, check every picture: exactly 30 rows from the propellers' top (row 5) to the bombs' bottom (row 34), rows 35-37 empty, the craft's middle on column 29, at most 40 squares wide, nothing below row 34; every 26x26 square one colour; alpha only 0/255; at most ~28 colours; the goggles, the nose and the moustache readable at 1x and 2x; the SIDE view really turned to the right (nose and gun pointing right, flank showing) with the very same pilot's head as the FRONT view.
```

## 交付（`outputs/corki-model/`）

- `corki-front-A.png`、`corki-side-A.png`、`corki-front-B.png`、`corki-side-B.png`（1536 × 1024）和各自的 `_1x.png`（59 × 39）；
- `corki-model-compare.png`：四张 1 倍图放大 8 倍并排，旁边放原画第 2 张的飞行员；
- 生图原稿（`raw/`）、`generation-prompts.txt`、色板、`HANDOFF.md`（**最后写**：每张的高度、宽度、色数、每格是否单色、哪里没做到）；最好再打成 `corki_model_pack_done.zip`。

## 交回前自查

- [ ] 四张都是 30 行（螺旋桨顶第 5 行到炸弹底第 34 行），第 35–37 行空着，机身中间第 29 列，不超过 40 格宽，第 34 行以下没有像素；
- [ ] 每格一个颜色、透明度只有 0/255、不超过约 28 色、只有一种近黑描边、里面少用黑；
- [ ] 飞行员头盔顶到八字胡下沿约 9 行，两片黄色护目镜、粉鼻子、左右张开的白八字胡清楚；不要 Q 版；
- [ ] **侧面版真的转向右边**：机头和机枪朝正右、机身侧面露出、近侧机翼在前、螺旋桨在后上方、推进器在左、炸弹在下；**飞行员的头和正面版一模一样**；
- [ ] 棕皮头盔（尖刺、红羽毛）、黄护目镜、白八字胡、红围巾、绿衣服、棕手套；钢蓝怪兽头机身（牙、金灯、格林机枪）、棕护垫、两副木螺旋桨、后掠机翼（锯齿边）、红喷口推进器 + 黄铜管、两个黄红格子炸弹；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读 1 倍图（核对和大图逐格一致）；**如果 1 倍图是 Codex 先画大再缩的（糊、碎点），改用 `raw/` 的原稿按 2:1 逐格描（古拉加斯的教训），不靠删行缩小**。放回 128 画布：炸弹底离地 3 行（悬停），机身中间在第 64 列，一圈描边整理；正面和侧面并排、和原画第 2 张、本包英雄一起给用户挑；只修用户指出的地方。
- 第 2 步动作帧：**除待机外全部从侧面版画**（机头朝右，飞机是整块刚性的部件，只做平移、上下浮动；不旋转、不拉伸），飞行员的头每帧都是待机那一张 3/4 脸；待机 / 移动是整架飞机上下浮动 1–2 格 + 螺旋桨换角度 + 喷口闪动，移动时机身稍前倾（用户已确认）；地面加一块小影子标落点。
