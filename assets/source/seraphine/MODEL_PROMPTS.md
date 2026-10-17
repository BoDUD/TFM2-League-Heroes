# 萨勒芬妮：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画两版给用户挑。** 照用户选的原画（`seraphine/1_picture.png`，原画 A：3/4 朝右站在她的浮空小舞台上，画面右边那只手抬到耳边，左边那只手垂在胯旁，粉色长发往身后（画面左边）飘）在**游戏尺寸**重新画。
> - **大小**：从**呆毛顶到舞台底 46 格**，其中**舞台约 7 格**（青色线 = 靴底踩在台面上的那一行的下沿，红线 = 舞台底那一行的下沿，第 99 行）。也就是说人从呆毛顶到靴底约 39 格，和包里的风女（45 行，飘着）、娜美（50 行，骑在尾巴上）放在一起差不多。两版**全宽不超过 30 格**（头发 + 舞台）。大小、姿势和位置照 `seraphine/2_target_size.png`（原画直接缩到这个大小的灰剪影，浅灰的是舞台）；蓝线 = 中间那一列（x=512），绿线 = 呆毛顶，橙线 = 下巴（版本 1），紫线 = 下巴（版本 2）。
> - **头**：**版本 1** 呆毛顶到下巴 **12 格**（游戏 Q 版大头，脸约 8 格宽，大眼睛更清楚）；**版本 2** **10 格**（更接近原画，脸约 7 格宽，腿更长）。原画的头只有身高的五分之一，游戏里要大一些——下巴以下的身体、腿相应缩短。**少女身材**（参考 `3_quality_bar.png` 里的格温、娜美、风女、娑娜、莎弥拉的像素大小）。
> - **头发**：亮粉色，一大把往画面左边飘、发梢分成 4–5 绺尖尖的卷（每绺 2–3 格宽），头顶一撮卷起来的呆毛；**比原画收紧一点**，头发最远的地方离身体后沿不超过 10 格。四档粉（深玫红阴影、主色、亮粉、浅粉高光）分出一绺一绺，不要糊成一整块。
> - **水晶羽片**：背后左右各一组 2–3 片蓝青色的尖羽片（像小翅膀），每片 2–3 格宽、4–6 格长，从肩膀后面伸出来，亮蓝青色加一格浅色高光。
> - **舞台**：一块扁扁的金边浮空小舞台，**最宽 24 格左右、高 7 格**：最上面 1–2 格是**青色台面**（彩绘玻璃，一两格亮青），下面是**金色的船形底**；正面中间一个**圆形蓝花徽章**（约 6×6 格，蓝色花瓣 + 中心一个 2×2 的**亮粉色发光球**），两边各一个**金框水滴形蓝水晶**（各约 3×4 格）。两只靴子稳稳踩在台面上。
> - **干净、不要细节（最重要）**：最多 40 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。粉头发、紫上衣、粉色发光球容易糊在一起：**头发是亮粉（偏品红），上衣是偏蓝的紫色，泡泡袖和手套是亮白（阴影淡灰紫），金饰是最亮的金色，羽片是亮蓝青，舞台台面是青色**。去掉这个尺寸看不清的细节：袖口的金星 = 每只袖子 2 个 1–2 格的金点；皮带上的蓝宝石 = 2–3 个 1 格蓝点 + 胯边一个 2×3 的金色菱形扣；彩虹裙 = 深蓝底 + 竖着的 1 格青、粉、金条；裙摆白褶边 1 格；近侧亮片袜 = 浅银紫平涂加几格亮点 + 小腿上一道 1 格金色弯纹；远侧袜子浅紫白；靴子棕色 + 1 格金边。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，呆毛顶到舞台底只有 46 格**。
> - **脸**：两只**大蓝紫眼睛**（各 2 格宽 2–3 格高：深蓝 + 亮蓝紫 + 1 格白高光），上面一道深色睫毛线；嘴 = 1–2 格粉红，微笑；脸颊 1 格淡粉红晕。**眼睛的颜色只用在眼睛上**。抬到耳边的白手套不能挡住眼睛和嘴。
> - **直接按游戏尺寸画**，不要先画大再缩小。`seraphine/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 46 格时，把最接近的那一张也交来（不要超过 54 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 40 色，描边只用一种近黑色。交付到 `outputs/seraphine-model/`：`seraphine_design_1.png`、`seraphine_design_2.png`（1024×1024）和各自的原尺寸图 `seraphine_design_1_1x.png`、`seraphine_design_2_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来呆毛顶到靴底、到舞台底各是多少格、头是多少格、全宽多少格），最好再打成一个 zip（`seraphine_design_pack.zip`）。

## 附图（都在压缩包的 `seraphine/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：亮粉长发 + 呆毛、蓝紫大眼睛、背后蓝青水晶羽片、白泡泡袖 + 金星、紫上衣、白手套、棕皮带 + 蓝宝石 + 金菱形扣、彩虹深蓝短百褶裙 + 白褶边、两条不一样的长筒袜、棕短靴、脚下的浮空小舞台 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 46 行的灰剪影（浅灰 = 舞台）；红线 = 舞台底那一行的下沿，青线 = 靴底，蓝线 = 中间，绿线 = 呆毛顶，橙线 = 下巴（版本 1），紫线 = 下巴（版本 2） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的格温、娜美、风女、娑娜、莎弥拉，游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**（格温是最近通过的少女） |
| `4_head.png` | 原画的头，放大 | 眼睛、睫毛、嘴、呆毛、刘海、抬到耳边的手套 |
| `5_parts.png` | 原画的水晶羽片、上身（袖子、上衣、皮带、裙子）、腿和靴子、舞台，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到这个大小，同一画布、同一底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的这个站姿（模型渲染） | 只看服装和舞台结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：呆毛顶到舞台底 46 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 1/2 的格数，少女身材；3/4 正面朝右；两腿并拢站在舞台上、一前一后；画面右边那只手（戴白手套）抬到耳边，画面左边那只手垂在胯旁、手指微张；头发往画面左边飘、收紧；脸朝观众。
- **干净**：最多 40 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：头发的暗部是深玫红、白袖的暗部是淡灰紫、皮肤是粉褐），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#120A1E outline (the only near-black); hair #7A0E56 #C21A8C #F24AC0 #FD9AE4; skin #C8806E #F1C4B2 #FEE0CC; eyes #1E2A8A #5A6AF0 #FFFFFF (eyes only); lips and blush #E8607A; sleeves and gloves #9A9AC0 #DCDCEC #FAFBFB; top #2C0A5A #4A2A9A #8A5AE0; crystal fins #073472 #2A67C2 #54A9E7 #B0EEFF; gold #8C5A20 #E0A020 #F5C32D #FFE88A; belt #4D2225 #7A4A2A; skirt #161D77 #3A3ACA #6A4AD0, skirt sheen #40D0E0 #F070C0; near stocking #6A5A80 #A8A8C8 #DCDCF0; far stocking #C4BFE7 #F1EFFB; boots #2F150B #653217 #9A5A30; stage deck #0E6A8A #1EB6D1 #8AF0F8; medallion #1D40E4 #5A8AF0; orb #C050D0 #FFC8FF; stage crystals #3060E0 #90E0FF.
- **舞台底以下什么都不能有**（游戏在最低点下面画血条）：舞台底在第 99 行，下面一格都不能有，头发也不能低于舞台台面。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`seraphine_design_1.png` 和 `seraphine_design_2.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`seraphine/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Seraphine, a cheerful young singer with fair skin standing on her small FLOATING STAGE: a big mass of long wavy BRIGHT PINK hair streaming behind her (toward image left) in pointed curling locks, a curled strand sticking up on top; big BLUE-VIOLET eyes, pink smiling lips; a fan of BLUE-CYAN CRYSTAL FINS like small wings behind her shoulders; WHITE PUFFY OFF-SHOULDER SLEEVES with gold stars and gold arm bands, a VIOLET top with a small cyan gem necklace, WHITE GLOVES; a BROWN BELT with small blue gems and a big GOLD DIAMOND CLASP at her hip; a very short dark blue PLEATED SKIRT with an IRIDESCENT sheen (cyan, pink, gold) and a white frill; two DIFFERENT THIGH-HIGH STOCKINGS (the near one sparkly silver-lilac with a gold curl on the shin, the far one plain pale lavender-white); BROWN ANKLE BOOTS with gold trim; and under her boots the STAGE: a flat gold-rimmed hover board with a TEAL deck, a round BLUE FLOWER MEDALLION with a glowing PINK ORB on its front and a gold-framed teardrop BLUE CRYSTAL on each side. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the stage in lighter grey - use it for her SIZE, her POSE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: the FIRST image's head, big - the eyes, the lashes, the mouth, the curl, the bangs and the gloved hand at her ear. FIFTH: the FIRST image's crystal fins, her top with the sleeves, belt and skirt, her legs and boots, and the stage, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the costume and the stage are built, NOT its 3D shading.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 46 squares from the top of her curl to the bottom of the stage (her boots stand on the deck about 7 squares above the stage's bottom) and at most 30 squares across (hair and stage included). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 46 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing on the stage in 3/4 FRONT view facing image right, legs close together, one a little ahead of the other; the hand on image RIGHT (white glove) raised to her ear; the hand on image LEFT hanging at her hip, fingers slightly open; the hair streaming toward image left but TIGHTER than in the picture (its farthest point at most 10 squares behind her back); the face turned toward the viewer, never covered by the glove.
Game proportions: the HEAD line at the end says how many squares from the top of the curl to the chin; the body down to the soles shares the rest of the 39 squares above the deck. A slim girlish build; the eyes, the white sleeves, the gold clasp, the fins and the stage's orb drawn big enough to read. The hair in 4-5 pointed curling locks of 2-3 squares, told apart by four pinks; each crystal fin 2-3 squares wide and 4-6 long; the stage at most 24 squares wide and 7 tall: a 1-2 square teal deck on top, a gold boat-shaped hull, the round blue flower medallion about 6x6 squares with a 2x2 glowing pink orb in its middle, a 3x4 gold-framed blue crystal on each side.
Clean, not detailed (most important): at most 40 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the bright magenta-pink hair, the bluish violet top, the bright white sleeves and gloves with lilac-grey shadows, the warm skin, the brightest gold, the bright blue-cyan fins, the teal deck. Drop what does not read at this size: the sleeve stars are 2 gold dots of 1-2 squares a sleeve, the belt gems 2-3 single blue squares plus a 2x3 gold diamond clasp at the hip, the iridescent skirt dark blue with upright 1-square cyan, pink and gold stripes, the frill 1 white row, the near stocking flat light silver-lilac with a few lit squares and a 1-square gold curl on the shin, the far stocking pale lavender-white, the boots brown with a 1-square gold band.
Palette (from the FIRST image, adjust if needed): #120A1E outline (the only near-black); hair #7A0E56 #C21A8C #F24AC0 #FD9AE4; skin #C8806E #F1C4B2 #FEE0CC; eyes #1E2A8A #5A6AF0 #FFFFFF (eyes only); lips and blush #E8607A; sleeves and gloves #9A9AC0 #DCDCEC #FAFBFB; top #2C0A5A #4A2A9A #8A5AE0; crystal fins #073472 #2A67C2 #54A9E7 #B0EEFF; gold #8C5A20 #E0A020 #F5C32D #FFE88A; belt #4D2225 #7A4A2A; skirt #161D77 #3A3ACA #6A4AD0, skirt sheen #40D0E0 #F070C0; near stocking #6A5A80 #A8A8C8 #DCDCF0; far stocking #C4BFE7 #F1EFFB; boots #2F150B #653217 #9A5A30; stage deck #0E6A8A #1EB6D1 #8AF0F8; medallion #1D40E4 #5A8AF0; orb #C050D0 #FFC8FF; stage crystals #3060E0 #90E0FF.
Face (most important detail), as the FOURTH image: two BIG BLUE-VIOLET EYES, each 2 squares wide and 2-3 tall (dark blue, bright blue-violet and 1 white highlight square), a dark lash line just above each; a 1-2 square pink smiling mouth on the face's middle line; a 1-square soft pink blush on the cheek; the bangs never over the eyes. The eye colours are used only by the eyes.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the stage's lowest row at y=792-799 (square row 99, the red line), her soles on the deck at the cyan line, the stage's middle on the middle column (x=512, the blue line), the top of the curl on the green line, the chin on the orange line (version 1) or the purple line (version 2). Nothing below the stage (the game draws the health bar right under it); the hair stays above the deck.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 46 squares from the top of the curl to the bottom of the stage (compare with the SECOND image), about 7 of them the stage; the head as tall as the HEAD line says; at most 30 squares across; all squares 8x8 on one grid; at most 40 colours; one outline colour; both blue-violet eyes with lashes; the pink hair locks and the curl, the crystal fins, the white sleeves and gloves, the violet top, the belt with the gold clasp, the striped skirt with the white frill, the two different stockings, the brown boots and the stage with its teal deck, flower medallion, pink orb and two blue crystals all readable; nothing below the stage.
VERSION 1 (seraphine_design_1.png): HEAD 12 squares from the top of the curl to the chin (a game-size chibi head, the face about 8 squares wide); 46 squares in all.
VERSION 2 (seraphine_design_2.png): HEAD 10 squares from the top of the curl to the chin (closer to the picture, the face about 7 squares wide), longer legs; 46 squares in all; everything else as version 1.
```

## 交回前自查

- [ ] 呆毛顶到舞台底 46 格（最多 54），其中舞台约 7 格；版本 1 头 12 格、版本 2 头 10 格；全宽不超过 30 格；舞台底在第 99 行、舞台中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 40 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；粉头发、紫上衣、白袖子手套、皮肤、金饰、蓝青羽片、青色台面分得开；
- [ ] 两只大蓝紫眼睛和睫毛、微笑、呆毛；头发一绺一绺、往画面左边飘但收紧；
- [ ] 白泡泡袖 + 金点、紫上衣、棕皮带 + 金菱形扣、彩条深蓝短裙 + 白褶边、两条不一样的长筒袜、棕短靴；
- [ ] 舞台：青色台面、金色船形底、蓝花徽章 + 粉色发光球、两颗金框蓝水晶；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、底线、眼睛，只补缺的描边。
- 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。移动是踩着舞台滑行（英雄联盟的做法），动作帧里舞台一直在她脚下。
