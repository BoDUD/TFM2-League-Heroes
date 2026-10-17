# 戴安娜：按原图在游戏尺寸画造型（给 Codex）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户确认后，下一轮再按它画动作（待机、移动、普攻、第三下顺劈、Q 新月打击、E 月神冲刺、R 月之降临、受击、死亡）。
> - 照 `diana_source.png` 画（你上一轮画的 A 版原图，用户选的）：戴安娜的长相、额头的月亮、发型、月银色盔甲、深蓝紧身衣、金色腰扣和护膝、紫色披风、弯刀、站姿都照它来。
> - **直接画游戏尺寸**：头顶到脚底 39 格（第 61 到第 99 行方块），刀尖再高出 3–4 格，8 倍放大，每个像素一个 8×8 方块。你画的每一格就是游戏里的一个像素，Claude 不再缩小（以前先画大再缩小，细节都碎成了点）。
> - **大小要数格子**：以前几次画出来都比要求大（要 38 格，画了 53–66 格），锐雯、薇恩在游戏里 46–48 行都被用户说太大，最后改成 40 行。`size_ref_riven.png` 就是 40 行的锐雯，蓝色短线是头顶那一行（第 61 行），红线是脚底。
> - 交回时附 `HANDOFF.md`（用了哪段提示词、颜色表、没做到的地方）和 `manifest.json`（尺寸、脚底行、头顶行、站位点、不透明区域、眼睛颜色的中心、颜色数）。文件名 `diana_design_A.png`、`diana_design_B.png`，打成一个 zip。

## 附图（都在压缩包里）

| 文件 | 内容 | 用法 |
|---|---|---|
| `diana_source.png` | 原图（A 版） | **照它画**：脸、额头的月亮圆盘、白金色头发和青绿发带、马尾、月银色盔甲、深蓝紧身衣、金色月牙腰扣、青绿垂甲、紫色披风、金色护膝和银色护胫、深蓝高跟靴、弯刀、站姿 |
| `style/tfm2_style_ref_swordsman.png` 等 | 团战经理2 原版英雄，8 倍 | 像素大小、干净程度、三行眼睛的画法 |
| `size_ref_riven.png` | 本包锐雯的游戏造型，8 倍，1024×1024 | 只看**大小和脚底线**（头顶第 61 行=蓝色短线，脚底第 99 行，y = 792–799，红线上面），不要照它的样子 |
| `diana_size_guide.png` | 原图直接缩到游戏尺寸（头顶到脚底 39 格，整张 42×22 格），8 倍，同一张画布、同一条脚底线 | 只看**这个尺寸能放下多少、各部分在哪**；颜色和形状都是糊的，不要照它 |
| `quality_bar_pack.png` | 本包画得好的女英雄（锐雯、薇恩、阿狸、贝蕾亚），8 倍 | **细节和清晰度要达到这个水平**：小方块就是细节，不要抹成大平块，也不要糊 |
| `league_diana_head.png` | 英雄联盟原版的头部 | 脸、额头月亮、眼下细线、发带的位置 |

## 规则（含之前的英雄学到的）

- **游戏尺寸**：头顶到鞋底 39 格（刀尖再高 3–4 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净**：最多 26 种颜色；每种材质 2–3 个平涂色阶（头发、发带、皮肤、眼睛、月亮圆盘、深蓝紧身衣、银甲加一个淡紫反光、金、青绿垂甲、紫披风、弯刀的青银）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **只有一圈描边**：整个剪影外面一圈 1 格宽的近黑描边；描边里面的边缘和褶皱用那种材质自己最暗的色阶，**不要再画第二圈黑**。深蓝紧身衣用带颜色的深蓝，要比描边亮，分得开。
- **脸**（最重要）：头约占头顶到脚底的三分之一（B 版约 13 格，A 版至少 11 格）；三行眼：一行深紫棕的睫毛，下面一行高光+深色瞳孔，再下面眼白+紫色虹膜；近处的眼睛（画面左边，她朝右）2 格宽，远处的 1 格宽贴着右脸颊，中间隔 1–2 格皮肤；两只眼睛一样高；眼睛的紫色**只用在眼睛上**（披风是更深、更灰的紫）；眼睛上面隔一行皮肤是额头的月亮圆盘（2×2，淡紫白，里面一格紫色月牙，在脸中线上），不能看起来像第三只眼；头发不盖住眼睛。英雄联盟里眼下的黑色细线：不画，或者近处眼睛下面最多一格暗紫。嘴：脸中线上一格暗玫瑰色，在眼睛下面两行；脸颊、下巴不要有别的深色格（下巴两角的阴影连到下巴会像歪嘴笑）。
- **弯刀**：照原图，右手（画面左边）在胯部高度握着刀柄，长长的新月刀身往上弯到肩膀后面、高过头顶，手下面露出一小截尖刺；刀身至少 2 格粗，有亮色刃口；刀和手臂、头发、马尾、披风之间都有描边隔开；看得到握刀的拳头。
- **两版**：A 照原图比例（头至少 11 格高）；B 按原版英雄的 Q 版比例（头约 13 格，占头顶到脚底的三分之一），弯刀、盔甲、脸和颜色不变。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：鞋底最低一行正好在第 99 行方块，下面一格都不能有；弯刀下面的尖刺、垂甲、披风都在脚底线以上。
- 3/4 正面朝右（照原图），不画背影。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，就不提名字，只保留外观描述（下面的提示词里已经没有名字）。

## 提示词（A、B 各生成一张，只把 Two versions 那句换成对应的一版）

```text
Five attached images. FIRST: the look of this character - copy her face, hair, armour, clothes, colors, crescent blade and stance from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size and cleanliness and their three-row eyes. THIRD: another hero of this game's pack at game size, 8x - use it ONLY for the size and the ground line. FOURTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look. FIFTH: this pack's best heroines at game size, 8x - the level of detail and clarity to reach (small crisp squares ARE the detail; never smear them into flat blobs, never blur).
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: 39 pixels from the top of the hair to the soles (block rows 61 to 99; the blade's tip rises about 3-4 more), true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine filigree.
The character: a moon warrior with pale cool skin and a calm, serious face. Platinum ash-blonde hair combed back from the face, two teal bands over the top of the head, one lock beside the near cheek, a long ponytail falling behind her back (left of the image). A small glowing moon disc in the middle of the forehead: pale lavender-white, 2x2 squares, with a violet crescent square in it. Moonsilver armour - pale silver plates with teal and lavender sheen: pauldrons with sharp upswept crescent spikes, a round crescent collar piece on the upper chest, lavender-silver forearm guards; a high dark collar. A dark navy bodysuit; a gold crescent-moon belt buckle; hanging dark teal-green hip tassets with thin gold-green edges; a dark purple mantle behind the shoulders. Legs: dark navy with gold knee guards over silver greaves, dark navy heeled boots. Dark fingerless gloves. The Moonsilver Blade: a long pale cyan-silver crescent with a brighter edge and a short grip, held in her right hand - the hand on the image-left, at hip height - its long curve rising up behind her shoulder past her head on the image-left, a short spike below the hand; exactly as in the FIRST image.
Pixel rules (most important): at most 26 colors in total, every material 2-3 flat shades (hair, teal bands, skin, eyes, moon disc, navy suit, silver armour with one lavender sheen, gold, teal tassets, purple mantle, blade cyan-silver); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. ONE 1-square near-black outline around the whole silhouette only: inside it, edges and folds use the material's own darkest shade - never a second ring of black inside the outline. The navy suit is a colored dark blue, clearly lighter than the outline.
Face (most important detail): the head about a third of the height from the crown to the soles; three-row eyes like the SECOND image, both visible and level: a row of dark violet-brown lashes, then a light highlight beside a dark pupil, then white beside a violet iris; the near eye (left, she faces right) 2 squares wide, the far eye 1 square wide against the right cheek, one or two squares of skin between them; the eye violet used NOWHERE else (the mantle is a deeper, greyer purple); one row of skin between the eyes and the moon disc, the disc on the face's middle line and smaller than the eyes read together, so it never looks like a third eye; the hair never covers the eyes. League's dark streaks under the eyes: leave them out, or at most one muted violet square under the near eye. The mouth: one square of muted rose on the face's middle line, two rows under the eyes; no other dark squares on the cheeks or the jaw (a shadow joining the jaw corners to the chin reads as a grin).
The blade: a clear crescent at least 2 squares thick with its bright edge, separated from the arm, hair, ponytail and mantle by the outline; the hand's fist visible on its grip.
Two versions: A: the FIRST image's proportions, the head at least 11 squares tall so the face reads. B: official-hero chibi proportions - the head about 13 squares, a third of the height from the crown to the soles; the same blade, armour, face and colors.
Pose and place: the stance of the FIRST image, 3/4 FRONT view facing right; the soles on the line 28 squares (224 px) above the bottom of the image, the same ground as the THIRD image, and NOTHING below it (the game draws the health bar there): the blade's lower spike, the tassets and the mantle all end above the soles; horizontally where the THIRD image stands.
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: 39 squares from the top of the hair to the soles (count them); every square 8x8 on one grid; at most 26 colors; both eyes visible and level, their violet used only in the eyes; the moon disc not read as an eye; the outline one square wide everywhere with no black ring inside it; nothing below the soles.
```

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`.claude/skills/tfm2-hero-mod/scripts/regrid.py`），**不缩小**；数行数（39 行左右）；压色板到 26 色以内，只留一圈描边，眼睛的紫只用在眼睛；看脸（两只眼睛同高、月亮圆盘不像第三只眼、嘴在中线）。游戏尺寸预览（和原版英雄、包里英雄比大小，在对战场地色和深色头像卡上各看一遍）给用户挑 A/B。
