# 雷克顿：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`renekton/1_picture.png`：英雄联盟的待机，弓背前倾、两腿岔开，近侧的手握着月牙大弯刀低低地拖在身侧、刀尖朝后，另一只手爪张开在前面，带背棘的尾巴拖在身后）在**游戏尺寸**重新画。
> - **大小**：**版本 A** 从**头盔顶（他最高的地方）到脚底 38 格**，**版本 B** 40 格。脚底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿 / 橙线 = 头盔顶。姿势和位置照 `renekton/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是尾巴）。这次一开始就按本包蛮王（37 行、拖着大剑 53 格宽）的个子画。
> - **画窄一点（重要）**：原画缩到 38 格会有约 67 格宽。整个造型连刀、尾巴**不能超出两条紫线**：A 最宽 **54 格**，B 最宽 **56 格**。办法：**刀画短一点、握得离身体近一点**，刀尖离握刀的手不超过 14 格，刀可以稍微斜向下（刀尖低于手）；**尾巴画短一点**，尾巴尖离后脚跟不超过 10 格，可以往上翘一点，尾巴和刀上下错开、互不遮挡；前面那只手爪收近身体一点。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。**鳞皮是亮青绿（背、手臂、腿、尾巴上面），喉咙、胸口、肚皮和尾巴下面是亮橙黄；头盔是象牙白（骨头一样的颜色）+ 一颗亮绿宝石；护肩、护膝是亮银灰；手腕、腰、脚踝的布条是深蓝；腰上一个金色圆扣 + 下面一片浅土黄的长布、两边棕色皮裙；刀刃是最亮的象牙白、刀框金色 + 一颗亮绿宝石、握柄深蓝**。去掉这个尺寸看不清的细节：鳞片的纹路 = 不画（只用 2–3 档青绿平涂）；背棘 = 尾巴上面一排 4–5 个 2 格的尖；刀刃内侧锯齿 = 2–3 个缺口；脚爪 / 手爪 = 每只 3 个 1–2 格的深灰爪尖；肩上的银球 = 2–3 个 2×2 的灰点。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，头盔顶到脚底只有 38（B 40）格**。
> - **头和脸**：鳄鱼头，3/4 朝右，**长长的嘴伸向右边**（嘴从眼睛往前约 7–8 格），**张着**：上下两排 **1 格的白牙**（各 3–4 颗）、嘴里**粉红色**；**一只橙黄的眼睛**（2×2，中间 1 格深色瞳孔）在头盔边下面看得见；头顶盖着**象牙白的头盔**（往后翘的两三个尖角），额头上一颗 **2×2 的亮绿宝石**。脸不能被挡住，**亮白只用在牙和刀刃上**。
> - **刀的形状照原画 B 的刀（`renekton/5b_blade_shape.png`，用户指定：「鳄鱼的斧头应该是这形状的」）**：一整把**宽的月牙**——外弧是一圈**象牙白、带 4–5 个尖齿的刃**，里面是**金色的刀框**（框中间一颗 **2×2 亮绿宝石**、上下两端各一个金色的弯钩），内弧上一根**深蓝缠布的握柄**从一端通到另一端，手爪握在握柄中间。**不是原画 A 那种细长的刀**。姿势仍是 A 的：握柄在手里、月牙横躺着低低地拖在身侧、尖端朝后（左），刃口朝下（`5b` 右边那张转过来的样子），**握刀的手爪看得见**，刀任何一部分都不藏在身体后面。
> - **直接按游戏尺寸画**，不要先画大再缩小。`renekton/6_size_guide.png` 是原画直接缩到 38 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 38 / 40 格时，把最接近的那一张也交来（不要超过 42 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/renekton-model/`：`renekton_design_A.png`、`renekton_design_B.png`（1024×1024）和各自的原尺寸图 `renekton_design_A_1x.png`、`renekton_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来头盔顶到脚底是多少格、整个造型多宽），最好再打成一个 zip（`renekton_design_pack.zip`）。

## 附图（都在压缩包的 `renekton/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：长鳄鱼嘴、白牙、橙眼、象牙白头盔 + 绿宝石、青绿鳞皮 + 橙黄肚皮、银灰护肩护膝、深蓝布条、金扣 + 土黄长布 + 棕皮裙、带背棘的尾巴、低持朝后的月牙刀 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（头盔顶到脚底 38 格）的灰剪影（浅灰 = 尾巴）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿 / 橙线 = 头盔顶，两条紫线 = 最宽的范围（54 格） | **A 的大小、姿势和位置照它**；剪影比紫线宽的部分（刀、尾巴）要收进来 |
| `2_target_B.png` | 同上，B 的大小（40 格），紫线 = 56 格 | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的蛮王、德莱厄斯、图奇、卡兹克、格温，游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**（蛮王 37 行、拖着大剑，就是这次的个子） |
| `4_head.png` | 原画的头，放大 | 头盔、眼睛、长嘴、牙 |
| `5_parts.png` | 原画的刀（连握刀的手）、护肩和手臂、尾巴、腰带和皮裙、一只脚，放大 | 这些部件的形状和颜色 |
| `5b_blade_shape.png` | **刀的形状**：原画 B 的刀（左）和把它转过来横躺的样子（右，刃口朝下） | **刀照这个形状画**（用户指定），按 A 的姿势横着拖在身侧 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：头盔顶到脚底 A 38 格、B 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、宽度收窄**：3/4 正面朝右；弓背前倾；两腿岔开弯着；近侧的手握刀低低地拖在身侧、刀尖朝后（左）；另一只手爪张开在前面；尾巴拖在身后、比原画短；**刀和握刀的手都看得见、不藏在身体后面**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0A0605 outline (the only near-black); scales #005A53 #018576 #01A08D #16BF97; belly and tail underside #C46916 #F18812 #FDB928; helmet and blade #B7A181 #DCBD91 #FAEBC3 #FBF8F3 (#FBF8F3 teeth and blade edge only); gold frame and buckle #8A5A10 #CB8426 #F7D88B; gems #0A7A2A #2ED84A #B4FAB0; silver armour #70675D #BFBBB7 #E2DAD0; blue cloth #111323 #17448A #3A6AC8; kilt leather #4A2410 #8A411E; tan cloth #DCBD91 #F7D88B; mouth #8A1428 #E04A6A; eye #C83A0A #FDB928; claws #2A2626 #70675D.
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，尾巴和刀也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`renekton_design_A.png` 和 `renekton_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`renekton/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7、5b 号图，按顺序（5b 放最后，第八张）。

```text
Eight attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Renekton, a big muscled CROCODILE standing on two legs: TEAL-GREEN scales, an ORANGE-YELLOW throat, chest and belly, a LONG CROCODILE SNOUT with open jaws, white teeth and a pink mouth, an AMBER EYE, an IVORY bone HELMET with a GREEN GEM on the forehead, big SILVER pauldrons and knee guards, DARK BLUE cloth wraps on the wrists, the waist and the ankles, a GOLD round buckle with a long pale tan cloth flap and a brown leather kilt, a thick TAIL with a row of spikes on top (teal above, orange below), black-grey claws; a huge CRESCENT BLADE held low in his near hand and trailing behind him - its SHAPE as the EIGHTH image, not as the FIRST image's thinner blade. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the tail in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas; it is TOO WIDE: everything must fit between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first one, a warrior dragging a greatsword, is this size). FOURTH: the FIRST image's head, big - the helmet, the eye, the snout, the teeth. FIFTH: the FIRST image's blade with its hand, the pauldron and arm, the tail, the belt and kilt, and a foot, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading. EIGHTH: THE BLADE'S SHAPE (the user's choice): a WIDE full CRESCENT - the outer curve a spiked IVORY edge with 4-5 points, inside it a GOLD frame with a green gem in the middle and a gold hook at each end, along the inner curve a DARK BLUE wrapped grip running from end to end, the hand gripping its middle; left as drawn upright, right turned to lie flat with the edge DOWN - draw the blade with THIS shape, lying like the right one (low at his side, the edge down, the ends pointing back and forward).
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the TOTAL number of squares (the VERSION line) from the top of his helmet (his highest point) to his soles, and at most the WIDTH number of squares across (blade and tail included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose, NARROWER: hunched forward in 3/4 FRONT view facing image right; the legs apart and bent; the NEAR hand gripping the middle of the crescent's blue grip low at his side, the crescent lying flat with its spiked ivory edge DOWN (the EIGHTH image's right one), trailing backward (image left), held CLOSE to the body (its far end at most 14 squares from the gripping hand); the other arm forward with the claws open, a little closer to the body; the tail lying out behind him, SHORTER than in the picture (its tip at most 10 squares behind the back heel, it may curve up a little), the blade and the tail one above the other without covering each other; the head turned toward the viewer, the eye, the snout and the teeth visible; the blade and the gripping hand fully visible, never hidden behind the body.
Game proportions: keep the picture's build - a big head with a long snout, broad shoulders with big pauldrons, a heavy body, strong bent legs; the eye, the teeth, the gems, the gold buckle and the blade's ivory edge drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no scale patterns, no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the bright teal scales, the bright orange belly and tail underside, the ivory helmet, the bright silver armour, the dark blue wraps, the gold buckle and blade frame, the bright green gems, the brightest ivory blade edge, the white teeth, the pink mouth. Drop what does not read at this size: the scales no pattern at all, the tail's spikes 4-5 points of 2 squares, the blade's outer edge 4-5 ivory points, its frame one gold band with the gem and a hook at each end, the claws 3 small dark points a hand or foot, the pauldron's balls 2-3 grey 2x2 dots.
Palette (from the FIRST image, adjust if needed): #0A0605 outline (the only near-black); scales #005A53 #018576 #01A08D #16BF97; belly and tail underside #C46916 #F18812 #FDB928; helmet and blade #B7A181 #DCBD91 #FAEBC3 #FBF8F3 (#FBF8F3 teeth and blade edge only); gold #8A5A10 #CB8426 #F7D88B; gems #0A7A2A #2ED84A #B4FAB0; silver #70675D #BFBBB7 #E2DAD0; blue cloth #111323 #17448A #3A6AC8; kilt leather #4A2410 #8A411E; tan cloth #DCBD91 #F7D88B; mouth #8A1428 #E04A6A; eye #C83A0A #FDB928; claws #2A2626 #70675D.
Face (most important detail), as the FOURTH image: the crocodile head in 3/4, the long snout reaching image right (about 7-8 squares in front of the eye), the jaws OPEN with a row of one-square white teeth top and bottom (3-4 each) and a pink mouth, one AMBER eye (2x2 with a 1-square dark pupil) visible under the helmet's rim, the ivory helmet on top with two or three backward spikes and a 2x2 bright green gem on the forehead. Nothing covers the face.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the top of the helmet on the green/orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them): the tail and the blade stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: TOTAL squares from the top of the helmet to the soles (compare with the SECOND image); at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the eye, the teeth, the open snout, the helmet gem, the gripping hand, the whole crescent blade in the EIGHTH image's shape and the spiked tail all readable; nothing below the soles.
VERSION A (renekton_design_A.png): TOTAL 38, WIDTH 54 (use the SECOND image 2_target_A).
VERSION B (renekton_design_B.png): TOTAL 40, WIDTH 56 (use the SECOND image 2_target_B); everything else as version A.
```

## 交回前自查

- [ ] 头盔顶到脚底 A 38 格、B 40 格（最多 42）；A 不超过 54 格宽、B 不超过 56 格宽；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；青绿鳞皮、橙黄肚皮、象牙白头盔、银灰护甲、深蓝布条、金扣、亮绿宝石、象牙白刀刃分得开；
- [ ] 张开的长嘴 + 白牙 + 橙眼 + 头盔绿宝石；刀是 `5b` 的宽月牙形状（外弧象牙白尖齿、金框 + 绿宝石、深蓝握柄沿内弧），横躺刃口朝下，握刀的手看得见、刀没被挡住、握得近；尾巴比原画短；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- 先给用户看 Codex 自己整理好的 A、B，再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
