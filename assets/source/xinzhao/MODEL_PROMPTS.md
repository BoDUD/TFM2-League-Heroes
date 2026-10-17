# 赵信：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`xinzhao/1_picture.png`，原画 A：两脚分开站稳，后手握枪斜架在身后，紫色枪头在画面左下，前手张开在身前）在**游戏尺寸**重新画。
> - **长枪缩短了（用户选的）**：原画里枪是身高的 1.6 倍，游戏里**只要约 1.2 倍**——枪头（紫刃）和月牙钩**保持原画的大小**，只把枪杆变短：枪尾的金箍和尖锥往回收，**刚好从他头后、前肩上方露出来一小截**。`1_picture.png`、`2_target_size.png`、`6_size_guide.png` 都已经是缩短后的样子，照它们画。
> - **大小**：从**发髻顶到脚底 42 格**、连枪最宽约 57 格。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 发髻顶，橙线 = 下巴（A 版），紫线 = 下巴（B 版）。大小、姿势和位置照 `xinzhao/2_target_size.png`（缩短后的原画直接缩到这个大小的灰剪影）。
> - **头**：**版本 A** 发髻顶到下巴 **15 格**（发髻和金发冠约占上面 4–5 行，脸约 8 格宽）；**版本 B** **13 格**（脸约 7 格宽，身体更长）。两版都是 42 格高，身材**匀称结实**（比 `3_quality_bar.png` 里的瑟提瘦、比韦鲁斯壮），腿稍短。**长枪约 50 格长**（从紫刃尖到枪尾尖锥），**紫色枪刃约 14–16 格长、最宽 3 格**，**银色月牙钩约 6–7 格高**，枪杆 2 格粗（深棕 + 一格亮边），枪杆上 2–3 道 1 格宽的金箍，枪尾尖锥 3–4 格。
> - **干净、不要细节（最重要）**：最多 28 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。紫色战袍、金边、银甲、浅紫裤子要分得开。去掉这个尺寸看不清的细节：金耳饰 = 1 格金、前肩护肩上的蓝饰 = 2–3 格亮蓝、胸甲的鳞片 = 两档银灰交错的几格、战袍前襟的金纹 = 一两条金线、枪刃上的星形 = 1 格亮紫或去掉。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，发髻顶到脚底只有 42 格**。
> - **脸**：剑眉、凌厉的眼神。**两只眼睛在同一行**（近侧眼在左、两格宽，远侧眼一格宽贴着右边的脸颊），每只眼睛上面一道往鼻梁压下来的深色眉线（严肃），**不画嘴或只画 1 格暗色的嘴**，嘴在脸的中线上。**黑发往后梳，额前和鬓角的银白挑染 2–3 格**，头顶**黑色发髻 + 金色发冠（2–3 格金）**，后面飘**两条深紫发带**。眼睛不能被头发、发带挡住，眼睛的颜色只用在眼睛上。
> - **直接按游戏尺寸画**，不要先画大再缩小。`xinzhao/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 42 格时，把最接近的那一张也交来（不要超过 50 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色，描边只用一种近黑色。交付到 `outputs/xinzhao-model/`：`xinzhao_design_A.png`、`xinzhao_design_B.png`（1024×1024）和各自的原尺寸图 `xinzhao_design_A_1x.png`、`xinzhao_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来发髻顶到脚底是多少格、头是多少格、连枪多宽），最好再打成一个 zip（`xinzhao_design_pack.zip`）。

## 附图（都在压缩包的 `xinzhao/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A（长枪已缩短到约 1.2 倍身高） | **长相和姿势**：黑发银白挑染、黑发髻金发冠、两条深紫发带、银白胸甲、紫金战袍、后肩金护肩、前肩蓝饰银护肩、棕色护臂和腰带、浅紫裤子、胯边银甲片、钢色护胫靴子、斜架在身后的长枪 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），缩短后的原画缩到 42 行的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 发髻顶（42 格），橙线 = 下巴（A 版），紫线 = 下巴（B 版） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的韦鲁斯（27×40）、凯隐（40×40）、贾克斯（44×36）、剑魔（40×40）、瑟提（26×42），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**；长兵器照凯隐、贾克斯、剑魔 |
| `4_head.png` | 原画的头，放大 | 发髻和金发冠、银白挑染、脸、金耳饰、两条发带 |
| `5_spear.png` | 原画的枪头（紫刃 + 月牙钩 + 发带）和握枪的后手、枪尾尖锥、空着张开的前手，放大 | 枪的形状、金箍、两只手 |
| `6_size_guide.png` | 缩短后的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看装备的结构，**不要照它的 3D 光影，头顶那团是渲染坏了的发髻** |

## 规则

- **像素尺寸（最重要）**：发髻顶到脚底 42 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材匀称结实；3/4 正面朝右；两脚分开、膝盖微弯；后手（画面左边）在肩膀高度握枪，长枪斜着架在身后：紫刃枪头在画面左下、枪尾尖锥在画面右上，刚好从头后露出来；前手（画面右边）张开在身前腰腹高度。
- **干净**：最多 28 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：紫袍是深紫、银甲是灰蓝、皮肤是红褐），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0E0A14 outline (the only near-black); hair #1A1620 #3A3448; skin #8C4E34 #C88458 #F0B486; royal purple coat, ribbons and spear blade #250A55 #421368 #5B18D1 #8A55F0; gold trim, shoulder guard, crown and rings #8A5A10 #EF9F14 #F8D060; silver armour, silver hair streaks, hook and steel boots #433C50 #5C6F8B #83A2C2 #C4CCDC #F4F6FA; blue insets #2E7BE0 #7CC8FF; brown leather and spear shaft #3A1E14 #6A3A22 #9A5E34; lavender trousers #7E68A8 #A88CD2 #CEB8EE; eyes #FFFFFF (eyes only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，枪也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`xinzhao_design_A.png` 和 `xinzhao_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`xinzhao/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Xin Zhao, a fit, stern spear warrior: black hair combed back with SILVER-WHITE streaks at the temples and the front, a high black TOPKNOT held by a GOLD crown clasp, two long DARK PURPLE RIBBONS trailing back from it; a stern face with sharp brows; a dark high collar; a SILVER-WHITE breastplate; a long ROYAL PURPLE war coat with GOLD trim on every edge, its front panel hanging between his legs; a flaring GOLD shoulder guard on his back shoulder (image left) and a big SILVER-WHITE PAULDRON with BRIGHT BLUE insets on his front shoulder (image right); brown leather forearm guards and dark fingerless gloves; a brown leather belt with a gold buckle; silver-white plates at the hips; loose pale LAVENDER trousers; dark steel greaves and boots with gold trim; and his signature weapon: a long SPEAR with a dark brown shaft and gold rings, its HEAD a long PURPLE blade with a SILVER CRESCENT HOOK and a purple streamer, its BUTT a short dark iron spike. In the FIRST image the spear is already shortened to about 1.2 times his height (the butt slid back so its spike just shows behind his head, over his front shoulder): keep it that length. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size - use it for his SIZE, his POSE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the second, third and fourth for a long weapon). FOURTH: the FIRST image's head, big - the topknot and its gold crown, the silver streaks, the face, the gold earring, the ribbons. FIFTH: the FIRST image's spear head with the crescent hook and the back hand holding the shaft, the butt spike, and the open front hand, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the armour is built, NOT its 3D shading (the dark lump above its head is a broken topknot: ignore it).
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 42 squares from the top of his topknot to his soles and at most 58 squares across (the spear included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 42 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: a wide stance in 3/4 FRONT view facing image right, feet apart, knees slightly bent; the BACK arm (image left) holding the spear at shoulder height, the spear slanting across behind his shoulders, its purple-bladed head low behind him at image left, its butt spike just showing behind his head over his front shoulder at image right; the FRONT arm (image right) in front of his belly, the hand open with clawed fingers; the ribbons hanging behind the topknot; the head turned toward the viewer.
Game proportions: the HEAD line at the end says how many squares from the top of the topknot to the chin; the rest shares the remaining squares. A fit, balanced body (slimmer than the fifth hero of the THIRD image, sturdier than the first), legs a little short; the topknot with its gold crown, the silver streaks, the blue-inlaid pauldron, the gold shoulder guard and the spear's head drawn big enough to read. The spear about 50 squares long from the blade's tip to the butt spike: the purple blade 14-16 squares long and at most 3 wide, the silver crescent hook 6-7 squares tall, the shaft 2 squares thick (dark brown with a lit edge) with 2-3 gold rings one square wide, the butt spike 3-4 squares.
Clean, not detailed (most important): at most 28 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the royal purple coat, the gold trim, the silver armour, the pale lavender trousers, the brown leather. Drop what does not read at this size: the earring is 1 gold square, the pauldron's blue insets 2-3 bright blue squares, the breastplate's scales two silver shades in a few staggered squares, the coat's gold pattern one or two gold lines, the star on the blade 1 light purple square or nothing.
Palette (from the FIRST image, adjust if needed): #0E0A14 outline (the only near-black); hair #1A1620 #3A3448; skin #8C4E34 #C88458 #F0B486; royal purple coat, ribbons and spear blade #250A55 #421368 #5B18D1 #8A55F0; gold trim, shoulder guard, crown and rings #8A5A10 #EF9F14 #F8D060; silver armour, silver hair streaks, hook and steel boots #433C50 #5C6F8B #83A2C2 #C4CCDC #F4F6FA; blue insets #2E7BE0 #7CC8FF; brown leather and spear shaft #3A1E14 #6A3A22 #9A5E34; lavender trousers #7E68A8 #A88CD2 #CEB8EE; eyes #FFFFFF (eyes only).
Face (most important detail), as the FOURTH image: TWO eyes on the SAME row (the near eye at image left, two squares wide, the far eye one square wide against the right cheek), a dark brow line just above each eye angled down toward the nose (stern), no mouth or a 1-square dark mouth on the face's middle line, the jaw clean; black hair combed back with 2-3 silver-white streak squares at the front and the temple; the black topknot with a 2-3 square gold crown on top of the head, two purple ribbons trailing from it. Nothing covers the eyes. The eye colour is used only by the eyes.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the top of the topknot on the green line, the chin on the orange line (version A) or the purple line (version B). Nothing below the soles (the game draws the health bar right under them): the spear stays above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 42 squares from the top of the topknot to the soles (compare with the SECOND image); the head as tall as the HEAD line says; the spear about 50 squares long; all squares 8x8 on one grid; at most 28 colours; one outline colour; both eyes visible and level, the brows; the topknot with its gold crown and ribbons, the silver streaks, both shoulder pieces, the purple coat with gold trim, the lavender trousers and the spear with its purple blade and crescent hook all readable; nothing below the soles.
VERSION A (xinzhao_design_A.png): HEAD 15 squares from the top of the topknot to the chin (a game-size chibi head: the topknot and crown about 4-5 rows above the crown of the head, the face about 8 squares wide); 42 squares in all.
VERSION B (xinzhao_design_B.png): HEAD 13 squares from the top of the topknot to the chin (the face about 7 squares wide), a longer body; 42 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 发髻顶到脚底 42 格（最多 50），A 头 15 格、B 头 13 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 28 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；紫袍、金边、银甲、浅紫裤子分得开；
- [ ] 两只眼睛同一行、看得清，剑眉；黑发髻和金发冠、两条紫发带、银白挑染；
- [ ] 后肩金护肩、前肩蓝饰银护肩、银白胸甲、棕色护臂和腰带、钢色靴子都看得出来；
- [ ] 长枪约 50 格：紫刃枪头和银月牙钩在画面左下、枪尾尖锥刚好从头后露出来；枪在脚底以上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
