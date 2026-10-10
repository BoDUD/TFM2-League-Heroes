# 辛德拉：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`syndra/1_picture.png`：英雄联盟的待机，悬浮着，两臂向下张开、爪子张着，一个膝盖弯起、另一条腿垂直，脚尖朝下，两片长裙摆往身后（画面左边）飘，紫色弯角头盔）在**游戏尺寸**重新画。
> - **大小**：**版本 A** 从**角尖（她最高的地方）到脚尖 40 格**，**版本 B** 42 格。脚尖在第 99 行（y=792–799，红线），最低的脚尖在中间那一列（x=512，蓝线），绿 / 橙线 = 最高点。姿势和位置照 `syndra/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是裙摆）。**不要超过 42 格**：本包的萨勒芬妮、格温画到 45–46 行，在游戏里太大，后来都缩了。
> - **宽度**：整个造型连爪子、裙摆**不能超出两条紫线**：A 最宽 **32 格**，B 最宽 **34 格**（原画缩下来约 30 格）。
> - **头大一点（游戏比例）**：照原画的比例，头盔加脸只有 6 格高，**看不清眼睛和嘴**。请把头画大：**头盔顶到下巴 10–11 格**（洋红色眼睛、红唇、脸要清楚），**两根弯角在头盔上面再高 3–4 格**（比原画的角短一点）；身体相应短一点（腿稍短，像 `3_quality_bar.png` 里的卡尔玛、霞），总高度还是 40 / 42 格。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。她浑身是紫色，**几种紫要分开**：**头盔、护肩、护臂用偏蓝的紫 + 浅紫高光；胸甲、裙摆、长靴用更深的黑紫；金边用最亮的金色（只画最主要的几条：头盔边、护肩边、裙摆边、靴口）；皮肤暖小麦色；头发带一点青的银白；眼睛、手套、角尖的光是亮洋红**。去掉这个尺寸看不清的细节：卷纹 = 不画（护肩上最多一个 2×2 的金点）；胸甲的金线 = 两条；腰带 = 一条亮紫 + 一个金扣；爪子 = 每只手 3 根 1 格宽的黑紫尖爪 + 2×2 洋红手套；头发 = 两档银白 + 一档阴影。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，最高点到脚尖只有 40（B 42）格**。
> - **头和脸**：3/4 朝右，头盔正面一颗洋红色菱形宝石，**两只亮洋红色的眼睛**（各 1–2 格）清楚看得见，**红唇**（1–2 格），下巴尖；两根弯角向上弯成新月形，角尖亮洋红；**银白长发**从头盔两侧垂到腰（在手臂后面，不能盖住手）。脸不能被挡住。
> - **身体**：两臂向下张开，**两只手（爪子）都看得见**，在身体两侧；一条腿弯起（膝盖往画面右上），另一条腿垂直，**最低点是垂直那条腿的脚尖**；两片长裙摆从腰两侧往画面左边飘，金边。
> - **直接按游戏尺寸画**，不要先画大再缩小。`syndra/6_size_guide.png` 是原画直接缩到 40 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 / 42 格时，把最接近的那一张也交来（不要超过 44 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/syndra-model/`：`syndra_design_A.png`、`syndra_design_B.png`（1024×1024）和各自的原尺寸图 `syndra_design_A_1x.png`、`syndra_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来最高点到脚尖是多少格、整个造型多宽），最好再打成一个 zip（`syndra_design_pack.zip`）。

## 附图（都在压缩包的 `syndra/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：紫色弯角头盔 + 洋红眼睛 + 红唇、银白长发、紫护肩、黑紫胸甲 + 亮紫腰带、小麦色皮肤、两片长裙摆、黑紫长靴、紫护臂 + 洋红手套 + 黑紫爪子 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（角尖到脚尖 40 格）的灰剪影（浅灰 = 裙摆）；红线 = 脚尖那一行的下沿，蓝线 = 最低的脚尖，绿 / 橙线 = 最高点，两条紫线 = 最宽的范围（32 格） | **A 的大小、姿势和位置照它** |
| `2_target_B.png` | 同上，B 的大小（42 格），紫线 = 34 格 | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的维克托、萨勒芬妮、霞、卡尔玛、赛娜，游戏里现在的样子 ×8，同一条脚底线 | **像素大小、头身比和干净程度照它们**（维克托 42 行、卡尔玛 38 行、赛娜 39 行） |
| `4_head.png` | 原画的头（弯角、头盔、眼睛、红唇、银发），放大 | 头和脸 |
| `5_parts.png` | 原画的两只爪子、护肩和胸甲、飘起的裙摆、长靴，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：最高点到脚尖 A 40 格、B 42 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、头放大**：3/4 正面朝右；悬浮；两臂向下张开；一膝弯起；裙摆往画面左边飘；**脸、两只手都看得见**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#120A18 outline (the only near-black); helmet / pauldrons / bracers #3A2466 #5C3A94 #8A62C8 #B898E8; corset / skirt / boots #24143A #3C2460 #5A3A86; gold #8A5A14 #D6972A #F6CC5A #FFF0A8; skin #A8683C #D89A62 #F2C08A; hair #8EA4AE #C8D8DE #F4FAFA; magenta glow #B0108A #F030D0 #FF9CF2; lips #A01830 #D83A50; belt #7A2AD0 #A858F0.
- **脚尖以下什么都不能有**（游戏在脚下画血条）：最低的脚尖在第 99 行，下面一格都不能有，裙摆也不能低于脚尖。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`syndra_design_A.png` 和 `syndra_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`syndra/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Syndra, a proud dark sorceress who floats: a VIOLET HELMET with two TALL CURVED HORNS rising into a crescent (glowing magenta tips) and a magenta gem on its front, TWO GLOWING MAGENTA EYES, RED LIPS, warm tan skin, LONG STRAIGHT SILVER-WHITE HAIR falling from the helmet to her waist, pointed VIOLET PAULDRONS with gold edges, a tight DARK VIOLET CORSET with gold lines and a bright violet belt with a gold buckle, a bare midriff and bare thighs, two very LONG DARK VIOLET SKIRT PANELS with gold edges trailing behind her, THIGH-HIGH black-violet BOOTS with pointed toes, violet BRACERS, glowing MAGENTA GLOVES and sharp black-violet CLAWS. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the skirt panels in lighter grey - use it for her SIZE, her POSE and her PLACE in the canvas; everything must fit between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size, their head-to-body proportions and their crisp, clean look (the 4th and 5th are women of this size). FOURTH: the FIRST image's head, big - the horns, the helmet, the eyes, the lips, the hair. FIFTH: the FIRST image's two clawed hands, a pauldron with the chest, the trailing skirt panel and the boots, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the TOTAL number of squares (the VERSION line) from her highest point (the horn tips) to her lowest toe, and at most the WIDTH number of squares across (claws and skirt panels included). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose: floating in 3/4 FRONT view facing image right; both arms spread down and out from her sides with the claws open, both hands clearly visible; one knee bent (toward image right), the other leg hanging straight with the toes pointing down - its toe is the lowest point; the two skirt panels trailing behind her toward image left; the face turned toward the viewer, both eyes visible; the hair behind the arms.
Game proportions: a BIGGER HEAD than the picture - from the top of the helmet to the chin 10-11 squares, the horns only 3-4 squares more above the helmet (shorter than in the picture) - and a slightly shorter body (shorter legs), like the women in the THIRD image, the total height still TOTAL squares; the magenta eyes (1-2 squares each), the red lips, the helmet's gem and the gold edges drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no scroll ornaments, no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the violets apart: the helmet, pauldrons and bracers a bluish violet with lilac highlights; the corset, skirt panels and boots a darker black-violet; the gold edges the brightest gold (only the main ones: the helmet's rim, the pauldrons' edges, the skirt panels' edges, the boot tops); the skin a warm tan; the hair silver-white with a slight cyan tint; the eyes, gloves and horn tips bright magenta. Drop what does not read at this size: the pauldron scrolls (at most one 2x2 gold dot), the corset two gold lines, the belt one bright violet band with one gold buckle, each hand a 2x2 magenta glove with three 1-square-wide black-violet claws, the hair two silver shades and one shadow.
Palette (from the FIRST image, adjust if needed): #120A18 outline (the only near-black); helmet / pauldrons / bracers #3A2466 #5C3A94 #8A62C8 #B898E8; corset / skirt / boots #24143A #3C2460 #5A3A86; gold #8A5A14 #D6972A #F6CC5A #FFF0A8; skin #A8683C #D89A62 #F2C08A; hair #8EA4AE #C8D8DE #F4FAFA; magenta glow #B0108A #F030D0 #FF9CF2; lips #A01830 #D83A50; belt #7A2AD0 #A858F0.
Face (most important detail), as the FOURTH image: the head in 3/4, the violet helmet over the brow with a magenta gem in the middle, two bright MAGENTA eyes clearly visible under it, a small nose, RED LIPS, a pointed chin; the two horns curving up into a crescent; the silver hair on both sides. Nothing covers the face.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the lowest toe's row at y=792-799 (square row 99, the red line), that toe on the middle column (x=512, the blue line), the highest point on the green/orange line, nothing outside the two purple lines. Nothing below the lowest toe (the game draws the health bar right under it): the skirt panels stay above it.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: TOTAL squares from the highest point to the lowest toe (compare with the SECOND image); at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the horns, the helmet's gem, the magenta eyes, the red lips, the silver hair, both clawed hands, the belt, the skirt panels and the boots all readable; nothing below the lowest toe.
VERSION A (syndra_design_A.png): TOTAL 40, WIDTH 32 (use the SECOND image 2_target_A).
VERSION B (syndra_design_B.png): TOTAL 42, WIDTH 34 (use the SECOND image 2_target_B); everything else as version A.
```

## 交回前自查

- [ ] 最高点到脚尖 A 40 格、B 42 格（最多 44）；A 不超过 32 格宽、B 不超过 34 格宽；最低的脚尖在第 99 行、x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；头盔顶到下巴 10–11 格，角再高 3–4 格；
- [ ] 弯角头盔 + 洋红宝石 + 两只洋红眼睛 + 红唇；银白长发；紫护肩、黑紫胸甲 + 亮紫腰带金扣；两只爪子都看得见；裙摆往左飘；黑紫长靴；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚尖线、眼睛，只补缺的描边。
- 先给用户看 Codex 自己整理好的 A、B，再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步：idle run attack skill(Q) skill2(W) skill2_e(E) ult hit dead）。
- 她是悬浮的：游戏里的锚点（脚下）= 最低的脚尖；待机的上下浮动在 import 时由 idle_breathe 做。
