# 崔斯特：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`twistedfate/1_twistedfate_picture.png`，原画 A：站直，近侧手在腰边捏着蓝、红、金三张牌）在**游戏尺寸**重新画。
> - **大小**：从**帽顶到脚底 40 格**、最宽 26 格（帽檐约 20 格）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 帽顶，黄线 = 眼睛那一行，橙线 = 下巴（A 版；B 版这三条都低 2 行，脚底不变）。大小、姿势、头的大小和位置照 `twistedfate/2_target_size.png`（原画按游戏比例重新拼好再缩小的灰剪影：深一点的灰是帽子和头，中灰是身体，最深的灰是那把牌，比原画画大了）。
> - **原画是成人比例**（帽顶到下巴只占身高 14%），**游戏里是 Q 版大头**：**版本 A** 帽顶到下巴 **16 格**（帽子约 6 行、脸约 10 行 10 格宽，和原版的赌徒、枪手、瘟疫医生一个比例）；**版本 B** **14 格**（帽子约 5 行、脸约 9 行）。两版都是 40 格高，身材修长：窄肩、长腿、外套下摆在身后微微飘开。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。外套、帽子、裤子在游戏里是黑的，要用**深炭蓝灰的几档颜色加亮边**画出褶子和帽身，不要糊成一块黑；金边亮、红里衬和马甲暖。去掉这个尺寸看不清的细节：帽子上的金饰 = 1–2 格金色，纽扣 = 单格金色，立领花纹 = 平涂赭色加金边。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，帽顶到脚底只有 40 格**。
> - **脸**：帽檐的阴影下两只**淡青色的眼睛**在同一行（近侧眼在左、两眼之间隔 1–2 格皮肤，远侧眼窄一格），眼睛上面一道深色眉线，下面是脸颊、深色小胡子和一圈黑胡子；**帽檐在眼睛上面，不能挡住眼睛**；黑色长发在脸后面、披到肩后。眼睛的颜色只用在眼睛上。
> - **牌（标志道具）**：近侧手在腰边捏着扇开的三张竖牌，每张约 2 格宽 3 格高：**蓝、红、金**，每张带一圈亮一点的边，是全身最亮最饱和的地方（金边之外）；手（皮肤、金袖箍）从下面捏着，牌和手连在一起。
> - **直接按游戏尺寸画**，不要先画大再缩小。`twistedfate/7_size_guide.png` 是拼好的原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/twistedfate-model/`：`twistedfate_design_A.png`、`twistedfate_design_B.png`（1024×1024）和各自的原尺寸图 `twistedfate_design_A_1x.png`、`twistedfate_design_B_1x.png`，生图原稿，色板，`HANDOFF.md`（**最后写**，写明每张读回来帽顶到脚底是多少格、头是多少格），最好再打成一个 zip（`twistedfate_design_pack.zip`）。

## 附图（都在压缩包的 `twistedfate/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_twistedfate_picture.png` | 用户选的原画 A | **长相和姿势**：黑宽檐帽（金边、红帽檐底、金饰）、青色眼睛、胡子、长发、赭金立领、红里衬黑长外套、红马甲、金扣、棕靴、近侧手里的蓝红金三张牌 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画按游戏比例重新拼好再缩小的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 帽顶（40 格），黄线 = 眼睛，橙线 = 下巴（A 版） | **大小、姿势、头的大小和位置照它** |
| `3_quality_bar.png` | main 里的jhin（41×29）、caitlyn（45×31）、veigar（40×37）、leblanc（43×32）、ryze（41×25），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_tfm2_style.png` | 团战经理2 原版的gambler（36×22）、gunner（37×20）、illusionist（37×18）、plague_doctor（37×22）、hitman（35×18） ×8，都戴帽子、穿外套 | **宽檐帽怎么压在看得清的脸上、黑外套怎么画**：大块平涂、少色、形状清楚 |
| `5_head_ref.png` | 原画的头，放大（960×680） | 帽子、脸、青色眼睛、胡子、长发、立领 |
| `6_cards_ref.png` | 原画里的那把牌，放大，旁边是英雄联盟自己的蓝、红、金牌面 | 三张牌的颜色和样子 |
| `7_size_guide.png` | 按游戏比例拼好的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：帽顶到脚底 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材修长；3/4 正面朝右；近侧手在腰边捏着三张牌，远侧手臂自然下垂。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：外套是深炭蓝，红里衬是深红，靴子是深棕），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0D0B12 outline (the only near-black); the BLACK coat, hat and trousers in charcoal-navy #171925 #262A3A #3A4057 #5A6380 (lit edges); gold trims, brim edge, buckle and cuffs #7A4A0E #C08A1C #F2C23A #FFE58A; the collar's ochre brocade #4A2C14 #7A4A24 #A8743A; the red lining, waistcoat and the brim's underside #5C0C14 #A3141E #E0302A; skin #6B3B26 #A8643E #D58C5C; hair and beard #121017 #2A2630; white shirt #B8BCC8 #F2F2F6; brown boots #3A2214 #6B4224 #A06A3A; the cards: blue #1A3CD0 #5A9CFF, red (the lining's reds), gold (the trims' golds); eyes pale cyan #7AF4FF。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，外套下摆不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`twistedfate_design_A.png` 和 `twistedfate_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`twistedfate/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Twisted Fate, a roguish gambler and card master: a wide-brimmed BLACK hat (a flat round crown, the broad brim curling up at both sides, a GOLD edge round the brim, a dark RED underside, a small gold shell ornament on the front), long straight BLACK hair falling behind his shoulders, tanned skin, a short black beard along the jaw with a goatee and moustache, eyes glowing pale CYAN under the brim; the tall flared collar of his coat standing up behind his neck (ochre brocade, gold edges); a long BLACK duster coat to the ankles with GOLD trim on every edge and a deep RED lining that shows behind his legs; ornate gold cuffs and white shirt cuffs; a RED waistcoat with gold buttons and a round gold buckle, an open white shirt collar; a brown belt with a pouch; black trousers; brown knee boots with gold trims and pointed toes; and his signature prop: a FAN of THREE playing cards (BLUE, RED, GOLD) held between the fingers of his NEAR hand at his hip. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat shape in greys - the FIRST image recomposed at GAME proportions and shrunk to game size (dark-mid grey the hat and head, mid grey the body, the darkest grey the card fan, drawn bigger than in the picture) - use it for his SIZE, his POSE, his HEAD SIZE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: official heroes of this game at 8x, all wearing hats and coats (a gambler, a gunslinger, an illusionist, a plague doctor, a hitman) - copy how a WIDE HAT sits over a readable face at this size and how a black coat is drawn: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the hat, the face, the cyan eyes, the beard, the hair, the collar. SIXTH: the FIRST image's card fan, big, beside the game's own card designs (blue, red, gold). SEVENTH: the SECOND image's composition in the FIRST image's colours, shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of the hat to his soles and at most 26 squares across (the brim about 20). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing upright and relaxed in 3/4 FRONT view facing image right, the near foot a short step forward; the long coat hanging behind him, its red lining showing at the back hem; his NEAR hand a little out from the hip at waist height holding the fan of three cards (beside the body, not in front of it); the FAR arm hanging relaxed at his side; the head turned toward the viewer under the hat.
Game proportions: the HEAD line at the end says how many squares from the hat's top to the chin (the hat about a third of that); the rest shares the remaining squares. He is slim and tall: narrow shoulders under the collar, long legs in the boots, the coat's skirt flaring a little behind him; the hat and the cards drawn big enough to read.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The coat, the hat and the trousers are BLACK in the game: draw them in the charcoal-navy shades with lit edges (never one flat black mass - near-black is only the outline), so the coat's folds and the hat's crown read; the gold trims bright, the red lining and waistcoat warm. Drop what does not read at this size: the hat's ornament is 1-2 gold squares, the buttons single gold squares, the brocade a flat ochre with a gold edge.
Palette (from the FIRST image, adjust if needed): #0D0B12 outline (the only near-black); the BLACK coat, hat and trousers in charcoal-navy #171925 #262A3A #3A4057 #5A6380 (lit edges); gold trims, brim edge, buckle and cuffs #7A4A0E #C08A1C #F2C23A #FFE58A; the collar's ochre brocade #4A2C14 #7A4A24 #A8743A; the red lining, waistcoat and the brim's underside #5C0C14 #A3141E #E0302A; skin #6B3B26 #A8643E #D58C5C; hair and beard #121017 #2A2630; white shirt #B8BCC8 #F2F2F6; brown boots #3A2214 #6B4224 #A06A3A; the cards: blue #1A3CD0 #5A9CFF, red (the lining's reds), gold (the trims' golds); eyes pale cyan #7AF4FF.
Face (most important detail), as the FIFTH image: under the brim's shadow TWO pale-cyan eye squares on the SAME row (the near eye at image left of the far one, one or two squares of skin between them, the far eye one square narrower in 3/4 view), a dark brow line just above them under the brim, skin cheeks, a dark moustache line and the black beard round the jaw and chin; the brim sits ABOVE the eyes and never covers them; the black hair frames the face at the back and falls behind the shoulders. The eye colour is used only by the eyes.
The cards, as the SIXTH image: three upright cards fanned side by side in the near hand, each about 2 squares wide and 3 tall - BLUE, RED and GOLD, each with a 1-square lighter border feel - the brightest, most saturated spot of the sprite after the gold trims; the hand (skin, a gold cuff) holds them from below; they touch the hand.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the hat's top on the green line, the eye line on the yellow line and the chin on the orange line (version A; version B puts the hat's top, the eyes and the chin 2 rows lower and keeps the soles). Nothing below the soles (the game draws the health bar right under them): the coat's hem ends at or above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the hat's top to the soles (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; both eyes visible and level under the brim; three cards of three colours in the near hand; the coat's hem above the soles; nothing below the soles.
VERSION A (twistedfate_design_A.png): HEAD 16 squares from the hat's top to the chin (a game-size chibi head like the FOURTH image's heroes: the hat about 6 rows, the face about 10 rows and 10 squares wide); 40 squares in all.
VERSION B (twistedfate_design_B.png): HEAD 14 squares from the hat's top to the chin (the hat about 5 rows, the face about 9 rows and 9 squares wide), a longer body; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 帽顶到脚底 40 格（最多 48），A 头 16 格、B 头 14 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；黑外套有亮边和褶子，不是一块黑；
- [ ] 两只淡青色的眼睛同一行、在帽檐下面看得清，胡子在，脸没被挡住；
- [ ] 近侧手里蓝、红、金三张牌分得清，和手连着；外套下摆在脚底以上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
