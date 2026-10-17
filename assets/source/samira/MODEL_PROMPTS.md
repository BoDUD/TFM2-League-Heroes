# 莎弥拉：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`samira/1_picture.png`，原画 A：站直、两手叉腰、手肘向外，大刀斜背在背后，两把手枪插在胯边的金色枪套里，长辫子垂在画面右边）在**游戏尺寸**重新画。
> - **红飘带剪短了**：原画里刀柄末端的红飘带往画面左边飘得很长，游戏里每一帧都会变宽，所以**只留 2–4 格挂在刀柄末端往下垂**。`1_picture.png`、`2_target_size.png`、`6_size_guide.png` 都已经是剪短后的样子（剪口有点毛，照提示画干净的一小截）。
> - **大小**：从**头发顶到脚底 40 格**、连刀最宽约 24 格。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 头发顶，橙线 = 下巴（A 版），紫线 = 下巴（B 版）。大小、姿势和位置照 `samira/2_target_size.png`（剪短飘带后的原画直接缩到这个大小的灰剪影）。
> - **头**：**版本 A** 头发顶到下巴 **14 格**（游戏 Q 版大头，脸约 8 格宽）；**版本 B** **12 格**（原画的比例，脸约 7 格宽，身体和腿更长）。两版都是 40 格高，身材**匀称、健美的女性**（参考 `3_quality_bar.png` 里的希维尔、卡莎），腿稍短。**大刀从刀柄末端到刀尖约 38 格**（斜着），刀身最宽 4 格（深钢色 + 一格亮银刃口），刀柄 2 格粗、末端一格红；**长辫子**从后脑垂到大腿中部，上面 3–4 个 1 格的金箍。
> - **干净、不要细节（最重要）**：最多 28 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。墨绿黑的上衣 / 长靴、深钢刀身、黑发容易糊成一片：**衣服和靴子用几档墨绿加一格亮边，刀身深钢加一格亮银刃口，头发近黑加几格青绿高光**，红色和金色是亮点。去掉这个尺寸看不清的细节：手臂纹身 = 1–2 格暗一点的肤色或去掉、肚脐的金链 = 一行 1–2 格金、靴子上的方形银钉 = 1–2 格、枪套的雕花 = 两档金、耳坠 = 1 格银白。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，头发顶到脚底只有 40 格**。
> - **脸**：**画面左边那只眼戴墨绿眼罩**（约 3 格宽 2 格高的深墨绿块），一条 1 格的**红色系带**从眼罩斜着横过额头；**画面右边那只眼睁着、亮绿色**（1–2 格，带 1 格白），上面一道深色眉线；嘴 = 1 格深红（红唇），在脸的中线上；额前一缕头发翘起，金色发饰 2–3 格。眼睛不能被头发挡住，**绿色只用在眼睛上**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`samira/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色，描边只用一种近黑色。交付到 `outputs/samira-model/`：`samira_design_A.png`、`samira_design_B.png`（1024×1024）和各自的原尺寸图 `samira_design_A_1x.png`、`samira_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来头发顶到脚底是多少格、头是多少格、连刀多宽），最好再打成一个 zip（`samira_design_pack.zip`）。

## 附图（都在压缩包的 `samira/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A（红飘带已剪短） | **长相和姿势**：墨绿黑头发和一根金箍长辫、金发饰、墨绿眼罩和红系带、亮绿眼睛、墨绿黑无袖高领上衣、红斜布带、露腹、黑露指手套、两手叉腰、胯边金色枪套和枪、墨绿过膝长靴（银钉、红内衬、小跟）、斜背的大刀 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），剪短飘带后的原画缩到 40 行的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 头发顶（40 格），橙线 = 下巴（A 版），紫线 = 下巴（B 版） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的希维尔（48×40）、卡莎（25×42）、伊芙琳（36×41）、韦鲁斯（27×40）、烬（29×41），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**；女性身材照希维尔、卡莎 |
| `4_head.png` | 原画的头，放大 | 眼罩和红系带、亮绿眼睛、眉毛、红唇、翘起的刘海、金发饰、银耳坠、辫子的起头 |
| `5_parts.png` | 原画的刀柄和刀柄末端（红头）、两侧的金色枪套和枪管、两只长靴，放大 | 刀柄、枪套、枪管、靴子的形状 |
| `6_size_guide.png` | 剪短飘带后的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看装备的结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：头发顶到脚底 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材匀称健美；3/4 正面朝右；站直、两脚稍分开；两只手叉在腰上、手肘向外（画面左右各一个尖角）；大刀斜背在背后：刀柄和红头在画面左上、从后肩上方露出来（差不多和头发顶一样高），刀身斜着往画面右下，刀尖在前腿的膝盖下面露出来；长辫子垂在画面右边、身体后面；两把枪插在胯边的金色枪套里，枪管往下露出来。
- **干净**：最多 28 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：墨绿衣服是更深的墨绿、皮肤是红褐），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0C0A10 outline (the only near-black); hair #16141C #252733 #2A5A66; skin #8A4A2E #C57649 #F0A060 #FEC890; dark green top, eyepatch, trousers and boots #1A201E #2E3833 #4C6256 #7A9686; red sash, strap, waist cloth and boot lining #6A0610 #B0000D #E8141E; gold hair ornaments, holsters and braid rings #9A5A06 #EE9601 #FCD009 #FEF2A0; steel blade, hilt, guns, studs and earrings #303446 #4A5068 #7A82A0 #C8CCDA #F2F4FA; lips #A01818; eye #3EC84A #F0F0EC (eyes only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，刀尖也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`samira_design_A.png` 和 `samira_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`samira/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Samira, a confident, athletic woman gunslinger with bronze-brown skin: dark teal-black hair with a lock curling up over the forehead, small GOLD hair ornaments and ONE LONG THICK BRAID with gold rings hanging down behind her at image right; a DARK GREEN EYEPATCH over the eye on image left with a RED strap running across her forehead, the other eye bright GREEN, red lips; a sleeveless high-collared fitted top in DARK GREEN-BLACK with a RED sash across it, the midriff bare; black fingerless gloves; a red waist cloth; two big ornate GOLD holsters at her hips with pistols in them, their silver barrels pointing down; dark green over-the-knee boots with silver studs, red lining at the cuffs and small heels; and a HUGE single-edged GREATSWORD slung across her back: a dark steel blade with a bright silver edge, a dark hilt with a gold guard and a red pommel. In the FIRST image the long red ribbon at the pommel is cut back: draw it as a short red ribbon of 2-4 squares hanging down from the pommel. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size - use it for her SIZE, her POSE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first and second for a woman's build). FOURTH: the FIRST image's head, big - the eyepatch and its strap, the green eye, the brow, the lips, the curling lock, the gold ornaments, the earring, the start of the braid. FIFTH: the FIRST image's sword hilt with its red pommel, the two gold holsters with the pistol barrels, and the two boots, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the costume is built, NOT its 3D shading.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of her hair to her soles and at most 26 squares across (the sword included). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing tall in 3/4 FRONT view facing image right, feet a little apart; BOTH HANDS ON HER HIPS, the elbows pointing out to both sides; the greatsword slung diagonally across her back: its hilt and red pommel up behind her back shoulder at image left (about as high as the top of her hair), the blade slanting down behind her to image right, its point showing below the knee of her front leg; the braid hanging behind her at image right down to mid-thigh; the pistols in the gold holsters at her hips; the head turned toward the viewer.
Game proportions: the HEAD line at the end says how many squares from the top of the hair to the chin; the rest shares the remaining squares. A fit, balanced feminine build (like the first and second heroes of the THIRD image), legs a little short; the eyepatch, the green eye, the gold ornaments, the gold holsters, the red sash and the sword's silver edge drawn big enough to read. The sword about 38 squares long on the diagonal from the pommel to the point: the blade at most 4 squares wide (dark steel with a 1-square bright silver edge), the hilt 2 squares thick with a 2-3 square gold guard and a 1-2 square red pommel; the braid 2-3 squares wide with 3-4 one-square gold rings.
Clean, not detailed (most important): at most 28 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the dark green top and boots (with a lit green edge), the bronze skin, the red sash, the gold holsters, the dark steel blade with its silver edge, the near-black hair with teal highlights. Drop what does not read at this size: the arm tattoos are 1-2 darker skin squares or nothing, the gold belly chain one row of 1-2 gold squares, the boot studs 1-2 squares, the holster engraving two golds, the earring 1 silver-white square.
Palette (from the FIRST image, adjust if needed): #0C0A10 outline (the only near-black); hair #16141C #252733 #2A5A66; skin #8A4A2E #C57649 #F0A060 #FEC890; dark green top, eyepatch, trousers and boots #1A201E #2E3833 #4C6256 #7A9686; red sash, strap, waist cloth and boot lining #6A0610 #B0000D #E8141E; gold ornaments, holsters and braid rings #9A5A06 #EE9601 #FCD009 #FEF2A0; steel blade, hilt, guns, studs and earring #303446 #4A5068 #7A82A0 #C8CCDA #F2F4FA; lips #A01818; eye #3EC84A #F0F0EC (eyes only).
Face (most important detail), as the FOURTH image: the eye on image LEFT covered by a dark green EYEPATCH (about 3 squares wide, 2 tall) with a 1-square RED strap running diagonally across the forehead; the eye on image RIGHT open, bright green (1-2 squares with 1 white square), a dark brow line just above it; a 1-square dark red mouth on the face's middle line; a lock of hair curling up over the forehead, 2-3 gold ornament squares in the hair. Nothing covers the open eye. The eye colours are used only by the eye.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between her feet on the middle column (x=512, the blue line), the top of the hair on the green line, the chin on the orange line (version A) or the purple line (version B). Nothing below the soles (the game draws the health bar right under them): the sword's point stays above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the top of the hair to the soles (compare with the SECOND image); the head as tall as the HEAD line says; the sword about 38 squares on the diagonal; all squares 8x8 on one grid; at most 28 colours; one outline colour; the eyepatch with its red strap and the open green eye with its brow; the braid with gold rings, the dark green top with the red sash, both hands on the hips, the gold holsters, the boots and the sword with its silver edge and red pommel all readable; nothing below the soles.
VERSION A (samira_design_A.png): HEAD 14 squares from the top of the hair to the chin (a game-size chibi head, the face about 8 squares wide); 40 squares in all.
VERSION B (samira_design_B.png): HEAD 12 squares from the top of the hair to the chin (the picture's proportions, the face about 7 squares wide), a longer body and legs; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 头发顶到脚底 40 格（最多 48），A 头 14 格、B 头 12 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 28 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；墨绿衣服靴子、古铜皮肤、红布带、金枪套、深钢刀身分得开；
- [ ] 画面左眼戴墨绿眼罩 + 红系带，画面右眼亮绿、有眉毛；金发饰、翘起的刘海、金箍长辫；
- [ ] 两手叉腰、手肘向外；胯边金色枪套和枪管；墨绿过膝长靴（银钉、红内衬、小跟）；
- [ ] 大刀约 38 格斜背在身后：红头刀柄在画面左上、刀尖在前腿膝盖下面；短红飘带 2–4 格；刀尖在脚底以上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
