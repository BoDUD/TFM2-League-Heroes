# 图奇：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 B（`twitch/1_picture.png`：身子较直、两只手一起把弩横端在腰前、弩口朝前，长尾巴在身后卷起来）在**游戏尺寸**重新画。
> - **大小**：**版本 A** 从**背包顶（他最高的地方，耳朵在它下面）到脚底 36 格**，**版本 B** 38 格。脚底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿 / 橙线 = 背包顶。姿势和位置照 `twitch/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是尾巴）。这次一开始就按本包德莱厄斯（36 行）的个子画——卡兹克之前画到 45 行，用户在游戏里嫌大，后来缩到了 37 行。
> - **画窄一点（重要）**：原画缩到 36 格会有约 50 格宽。整个造型连弩、尾巴**不能超出两条紫线**：A 最宽 **44 格**，B 最宽 **46 格**。办法：**尾巴卷得更紧**，尾巴最远的地方离斗篷后沿不超过 6 格，往上卷；**弩画短一点**，弩尖离前面那只手不超过 9 格。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。深青、深绿、灰紫容易糊成一片：**斗篷是亮一点的青蓝，边上一格浅棕褐色滚边；手臂和背包是绿色；腿和尾巴是灰紫（尾巴一节浅一节深）；毛是灰绿；护目镜、弩身、铜扣是最亮的黄铜色；宝石是亮翠绿；牙是黄白；鼻头是一个红色亮点；围巾是橙色**。去掉这个尺寸看不清的细节：背包上的铆钉和药瓶 = 3–4 个 2×2 的铜点和青色圆点；皮带只画一道棕色 + 一个铜扣；斗篷下摆的碎布 = 3–4 个 2–3 格的尖；脚爪 = 每只脚 2–3 个 1–2 格的白爪尖。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，背包顶到脚底只有 36（B 38）格**。
> - **头和脸**：老鼠的头，3/4 朝右，**一对大耳朵**（外面灰绿、里面粉色，各 5–6 格高）；**黄铜护目镜**（一个 3×3 的铜圈，中间 1 格亮白镜片 + 1 格黑瞳孔）看得见，铜带子绕过头；**尖鼻子前端一个 2×2 的红鼻头**；张开的嘴里一排 **1 格的黄白尖牙**（3–4 颗）；脖子上**橙色围巾**。脸不能被挡住，**亮白只用在镜片上**。
> - **弩**：黄铜色的弩身 + 浅青蓝的弩臂 + 弩身上一颗**亮翠绿宝石**（3×3）+ 金色箭头，**两只绿色手爪都握在弩上、看得见**，弩任何一部分都不藏在身体后面。
> - **直接按游戏尺寸画**，不要先画大再缩小。`twitch/6_size_guide.png` 是原画直接缩到 36 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 36 / 38 格时，把最接近的那一张也交来（不要超过 46 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/twitch-model/`：`twitch_design_A.png`、`twitch_design_B.png`（1024×1024）和各自的原尺寸图 `twitch_design_A_1x.png`、`twitch_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来背包顶到脚底是多少格、整个造型多宽），最好再打成一个 zip（`twitch_design_pack.zip`）。

## 附图（都在压缩包的 `twitch/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 B | **长相和姿势**：大耳朵、黄铜护目镜、红鼻头、黄白尖牙、橙围巾、绿背包、青蓝破斗篷 + 浅棕褐边、绿手臂、灰紫鼠腿、一节一节的尾巴、两手横端的黄铜弩 + 翠绿宝石 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（背包顶到脚底 36 格）的灰剪影（浅灰 = 尾巴）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿 / 橙线 = 背包顶，两条紫线 = 最宽的范围（44 格） | **A 的大小、姿势和位置照它**；剪影比紫线宽的部分（尾巴、弩尖）要收进来 |
| `2_target_B.png` | 同上，B 的大小（38 格），紫线 = 46 格 | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的德莱厄斯、卡兹克、布兰德、派克、莎弥拉，游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**（德莱厄斯 36 行就是这次的个子） |
| `4_head.png` | 原画的头，放大 | 耳朵、护目镜、鼻子、牙、围巾 |
| `5_parts.png` | 原画的弩（连两只手）、背包、尾巴、斗篷和皮带、一只脚，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的这个站姿（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：背包顶到脚底 A 36 格、B 38 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、宽度收窄**：3/4 正面朝右；身子较直、微微前倾；两腿分开、鼠腿膝盖往后弯；两只手在腰前横端弩、弩口朝右；尾巴在身后往上卷、比原画卷得紧；**弩和两只手都看得见、不藏在身体后面**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0A0806 outline (the only near-black); fur #3A4440 #6A746A #9AA394; ears inside #B85A5A #F09A92; nose #8A1418 #E02A3A; teeth and toe claws #C8B48C #F6EAC8; brass (goggles, crossbow, rivets, trim) #7A4A10 #C88A1C #FCC23A #FFE68A; lens #FFFFFF (lens only); scarf #8A2A0C #D24A1A #F28030; coat #0A3A5A #10689A #3296C8; coat trim #A87A3C #D8AE68; arms and backpack #163A32 #2C6252 #4A9070; leather #3A1C10 #7A3C24; legs and tail #3A2838 #6A4A60 #9A7A8E #C8B0B8; crossbow limbs #3E6E98 #9ACDEB; gem #0E6A4A #2EC882 #B4FAD4.
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，尾巴和斗篷下摆也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`twitch_design_A.png` 和 `twitch_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`twitch/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Twitch, a big rat standing on two legs: GREY-GREEN fur, two BIG RAT EARS pink inside, BRASS GOGGLES, a RED NOSE, a grin of sharp YELLOW-WHITE TEETH, an ORANGE SCARF; a big GREEN BACKPACK with brass rims and teal vials; a ragged BLUE-TEAL COAT with a tan trim; GREEN ARMS with clawed green hands; digitigrade GREY-PURPLE RAT LEGS with white toe claws; a long RINGED TAIL (light and dark grey-purple bands); a BRASS CROSSBOW with LIGHT BLUE-TEAL limbs, an EMERALD GEM on top and a gold arrowhead, held level in BOTH hands at the hip. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the tail in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas; it is TOO WIDE: everything must fit between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first one is exactly this size). FOURTH: the FIRST image's head, big - the ears, the goggles, the nose, the teeth, the scarf. FIFTH: the FIRST image's crossbow with both hands, the backpack, the tail, the coat with the belt, and a foot, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the TOTAL number of squares (the VERSION line) from the top of his backpack (his highest point; the ears stay below it) to his soles, and at most the WIDTH number of squares across (crossbow and tail included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose, NARROWER: standing fairly upright, leaning a little forward, in 3/4 FRONT view facing image right; the legs apart, the knees bent backward the rat way; BOTH hands holding the crossbow level in front of the hips, its tip pointing image right, the crossbow SHORTER than in the picture (its tip at most 9 squares beyond the front hand); the tail curling UP behind him, TIGHTER than in the picture (its farthest point at most 6 squares behind the coat's back edge); the head turned toward the viewer, the goggles and the grin visible; the crossbow and both hands fully visible, never hidden behind the body.
Game proportions: keep the picture's build - a big head with big ears, a hunched backpack, a wiry body, thin rat legs; the goggles, the red nose, the teeth, the gem and the brass drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the brighter blue-teal coat with a 1-square tan trim, the green arms and backpack, the grey-purple legs and banded tail, the grey-green fur, the brightest brass for the goggles, crossbow and rivets, the bright emerald gem, the yellow-white teeth, the red nose, the orange scarf. Drop what does not read at this size: the backpack's rivets and vials 3-4 brass 2x2 dots and teal round dots, the belt one brown band with a brass buckle, the coat's torn hem 3-4 points of 2-3 squares, the toe claws 2-3 small white points a foot.
Palette (from the FIRST image, adjust if needed): #0A0806 outline (the only near-black); fur #3A4440 #6A746A #9AA394; ears inside #B85A5A #F09A92; nose #8A1418 #E02A3A; teeth and toe claws #C8B48C #F6EAC8; brass #7A4A10 #C88A1C #FCC23A #FFE68A; lens #FFFFFF (lens only); scarf #8A2A0C #D24A1A #F28030; coat #0A3A5A #10689A #3296C8; coat trim #A87A3C #D8AE68; arms and backpack #163A32 #2C6252 #4A9070; leather #3A1C10 #7A3C24; legs and tail #3A2838 #6A4A60 #9A7A8E #C8B0B8; crossbow limbs #3E6E98 #9ACDEB; gem #0E6A4A #2EC882 #B4FAD4.
Face (most important detail), as the FOURTH image: the rat head in 3/4, two big ears (grey-green outside, pink inside, 5-6 squares tall each), the brass goggle on the near eye as a 3x3 brass ring with a 1-square bright white lens and a 1-square black pupil, the brass strap round the head, a pointed snout ending in a 2x2 red nose, an open grin with 3-4 one-square yellow-white teeth, the orange scarf under it. Nothing covers the face. The bright white is used only by the lens.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the top of the backpack on the green/orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them): the tail and the coat hem stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: TOTAL squares from the top of the backpack to the soles (compare with the SECOND image); at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the ears, the goggle, the red nose, the teeth, the scarf, the gem, both hands on the crossbow and the banded tail all readable; nothing below the soles.
VERSION A (twitch_design_A.png): TOTAL 36, WIDTH 44 (use the SECOND image 2_target_A).
VERSION B (twitch_design_B.png): TOTAL 38, WIDTH 46 (use the SECOND image 2_target_B); everything else as version A.
```

## 交回前自查

- [ ] 背包顶到脚底 A 36 格、B 38 格（最多 46）；A 不超过 44 格宽、B 不超过 46 格宽；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；青蓝斗篷 + 浅棕褐边、绿手臂和背包、灰紫腿和一节一节的尾巴、灰绿毛、黄铜护目镜和弩、翠绿宝石、红鼻头、橙围巾分得开；
- [ ] 大耳朵 + 护目镜 + 红鼻头 + 尖牙；两只手都握在弩上、弩没被挡住；尾巴卷得比原画紧；弩比原画短；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、护目镜那几行几列不删），检查色数、脚底线、护目镜，只补缺的描边。
- 先给用户看 Codex 自己整理好的 A、B（卡兹克那次用户选的是 Codex 自己的版本），再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
