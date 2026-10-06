# 格温：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画两版给用户挑。** 照用户选的原画（`gwen/1_picture.png`，原画 A：3/4 朝右站着，画面左边那只手在胯边握着张开的大剪刀，两片刀刃斜斜朝身后下方拖着，另一只手叉在腰上）在**游戏尺寸**重新画。
> - **剪刀已经剪短了**：原画里两片刀刃很长，游戏里每一帧都会太宽，所以 `1_picture.png`、`2_target_size.png`、`6_size_guide.png` 里刀刃已经**沿刀刃方向压短到约六成**（刀尖的收尖还在）。照这个长度画，不要画回原画的长度。
> - **大小**：从**呆毛顶到鞋底 40 格**、连剪刀最宽约 32 格。鞋底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 呆毛顶，橙线 = 下巴（版本 1），紫线 = 下巴（版本 2）。大小、姿势和位置照 `gwen/2_target_size.png`（剪短后的原画直接缩到这个大小的灰剪影）。
> - **头**：**版本 1** 呆毛顶到下巴 **12 格**（游戏 Q 版大头，脸约 8 格宽，大眼睛更清楚）；**版本 2** **10 格**（更接近原画的比例，脸约 7 格宽，裙子和腿更长）。两版都是 40 格高，**娇小的少女身材**（参考 `3_quality_bar.png` 里的莎弥拉、伊芙琳、卡莎的像素大小，但格温更娇小），腿稍短。**头两侧上方两个黑蝴蝶结**各约 4–5 格宽（位置照原画）；**两边的螺旋卷**各 3 圈左右，每圈 2–3 格高，用几档天蓝分出一圈一圈。
> - **剪刀**：两个银蓝色的**圆环把手**（每个环约 4–5 格外径、中间透空 1–2 格），一个握在她手里、一个在下面；两片**青蓝水晶刀刃**各约 3 格宽、往画面左下收成尖，刃口一格近白亮边；环上的小尖刺 1–2 格。剪刀整体在脚底以上。
> - **干净、不要细节（最重要）**：最多 28 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。白裙子和白皙皮肤容易糊在一起：**裙子用冷白 + 淡紫灰阴影，皮肤用暖一点的肉粉**；深紫前片、深藏青荷叶边、黑泡泡袖、紫手套、紫菱格长袜要分得开。去掉这个尺寸看不清的细节：裙底金菱形饰钉 = 一排 4–5 个 1–2 格的金点、裙身金色竖条 = 1 格金线、长袜的菱格 = 两档紫交错几格（或者一档平涂加一两格亮）、耳坠和颈饰 = 1 格。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，呆毛顶到鞋底只有 40 格**。
> - **脸**：两只**大蓝眼睛**（各 2 格宽 2–3 格高：深蓝 + 亮蓝 + 1 格白高光），上面一道深色眉线；嘴 = 1–2 格粉红，微笑；齐刘海盖到眉毛，不能挡住眼睛。**蓝眼睛的颜色只用在眼睛上**（头发用别的天蓝）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`gwen/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色，描边只用一种近黑色。交付到 `outputs/gwen-model/`：`gwen_design_1.png`、`gwen_design_2.png`（1024×1024）和各自的原尺寸图 `gwen_design_1_1x.png`、`gwen_design_2_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来呆毛顶到鞋底是多少格、头是多少格、连剪刀多宽），最好再打成一个 zip（`gwen_design_pack.zip`）。

## 附图（都在压缩包的 `gwen/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A（剪刀已压短） | **长相和姿势**：天蓝齐刘海和呆毛、两边螺旋卷、头两侧的黑蝴蝶结、大蓝眼睛、白皙皮肤、深紫抹胸、黑泡泡袖、紫手套、白裙 + 深紫前片 + 金竖条、腰间紫条纹大蝴蝶结和金星、深藏青荷叶边裙摆和金菱形饰钉、紫菱格长袜和金色腿饰、白色高跟短靴、张开的剪刀 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），剪短后的原画缩到 40 行的灰剪影；红线 = 鞋底那一行的下沿，蓝线 = 两脚中间，绿线 = 呆毛顶（40 格），橙线 = 下巴（版本 1），紫线 = 下巴（版本 2） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的莎弥拉、卡莎、伊芙琳、韦鲁斯、希维尔，游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_head.png` | 原画的头，放大 | 眼睛、眉毛、嘴、刘海和呆毛、蝴蝶结、螺旋卷的起头、金耳坠 |
| `5_parts.png` | 原画的剪刀（已压短）、腰间蝴蝶结和金星胸针、两只鞋，放大 | 剪刀、蝴蝶结、鞋的形状 |
| `6_size_guide.png` | 剪短后的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看服装结构，**不要照它的 3D 光影**，剪刀长度照 1 号图 |

## 规则

- **像素尺寸（最重要）**：呆毛顶到鞋底 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 1/2 的格数，娇小的少女身材；3/4 正面朝右；两脚并拢站着、一前一后；画面左边那只手垂在胯边握着剪刀的一个环把手，剪刀张开、两片刀刃斜着朝画面左下；画面右边那只手叉在腰上（手肘向外）；脸朝观众。
- **干净**：最多 28 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：白裙的暗部是淡紫灰、皮肤是粉褐、头发是深蓝），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0E0B1E outline (the only near-black); hair #0E3A8C #1F6FD0 #2C9BEA #7CE1EC; head bows, puffed sleeves #181F40 #2C3468; skin #C98F86 #F2C2B0 #FEE4D0; eyes #1A2C8A #3AA8F0 #F8FCFF (eyes only); lips #E0607A; dress white #A88FA8 #D8C8DC #FEFDFE; front panel, bodice #2A1E4A #4A3270; waist bow #3A0E8A #6112C9 #9A5AE8; gold brooch, studs, stripes, garter #9A6A20 #E0B050 #F8E090; petticoat hem #12102E #26245A #3A3A80; gloves #2A1C40 #4E3A6E; stockings #2E2042 #4F3768 #75528D; shoes #6E5C80 #C8B8DA #F4EEF8; scissor blades #12407A #1A7FD0 #22B8F0 #A8F4FE; ring handles #3A3A6A #7A84B8 #C8D0EE #F4F6FF.
- **鞋底以下什么都不能有**（游戏在脚下画血条）：鞋底在第 99 行，下面一格都不能有，剪刀尖也不能低于鞋底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`gwen_design_1.png` 和 `gwen_design_2.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`gwen/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Gwen, a cheerful living doll girl with fair skin: bright SKY-BLUE hair with straight bangs and a little cowlick on top, big SPIRAL DRILL CURLS on both sides down past her shoulders, TWO BIG BLACK RIBBON BOWS at both sides of the top of her head (where the FIRST image has them); big BLUE eyes, pink smiling lips; a dark purple bodice, BLACK puffed short sleeves, PURPLE gloves; a puffy knee-length WHITE dress with a dark purple front panel and thin gold stripes, a BIG PURPLE STRIPED BOW at the waist with a GOLD STAR brooch, a ruffled DARK NAVY petticoat hem with a row of small GOLD diamond studs; purple diamond-pattern stockings with a gold garter charm; white high-heeled ankle boots; and a GIANT pair of OPEN SCISSORS held in her hand at her side: two silvery-blue RING HANDLES with small spikes and two cyan-blue CRYSTAL BLADES. In the FIRST image the blades are already SHORTENED (pressed to about 60% of their length along their own line): draw them that short. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size - use it for her SIZE, her POSE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: the FIRST image's head, big - the eyes, the brows, the mouth, the bangs and the cowlick, the bows, the start of the curls, the gold earring. FIFTH: the FIRST image's scissors, the waist bow with the star brooch, and the two boots, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the costume is built, NOT its 3D shading and NOT its scissor length.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of her cowlick to her soles and at most 32 squares across (the scissors included). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing in 3/4 FRONT view facing image right, feet close together, one a little ahead of the other; the hand on image LEFT hangs at her hip holding one ring handle of the OPEN scissors, the two blades slanting down and back toward image left, both points above the soles; the hand on image RIGHT on her hip, elbow out; the face turned toward the viewer.
Game proportions: the HEAD line at the end says how many squares from the top of the cowlick to the chin; the rest shares the remaining squares. A small, girlish build, legs a little short; the bows, the eyes, the curls, the gold star, the gold studs and the blades' bright edges drawn big enough to read. Each black bow about 4-5 squares wide; each drill curl 3 coils, every coil 2-3 squares tall, told apart by sky-blue shades; each ring handle about 4-5 squares across with a 1-2 square hole; each blade about 3 squares wide at its base, tapering to a point, with a 1-square near-white edge.
Clean, not detailed (most important): at most 28 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the cool white dress with lilac-grey shadows, the warmer pinkish skin, the dark purple front panel, the dark navy hem, the black sleeves and bows, the purple gloves and stockings, the sky-blue hair, the cyan blades, the silvery-blue rings. Drop what does not read at this size: the hem studs are a row of 4-5 gold dots of 1-2 squares, the dress stripes 1-square gold lines, the stocking diamonds a few squares of two purples (or flat with one or two lit squares), the earring and the necklace 1 square each.
Palette (from the FIRST image, adjust if needed): #0E0B1E outline (the only near-black); hair #0E3A8C #1F6FD0 #2C9BEA #7CE1EC; head bows and puffed sleeves #181F40 #2C3468; skin #C98F86 #F2C2B0 #FEE4D0; eyes #1A2C8A #3AA8F0 #F8FCFF (eyes only); lips #E0607A; dress white #A88FA8 #D8C8DC #FEFDFE; front panel and bodice #2A1E4A #4A3270; waist bow #3A0E8A #6112C9 #9A5AE8; gold brooch, studs, stripes and garter #9A6A20 #E0B050 #F8E090; petticoat hem #12102E #26245A #3A3A80; gloves #2A1C40 #4E3A6E; stockings #2E2042 #4F3768 #75528D; boots #6E5C80 #C8B8DA #F4EEF8; scissor blades #12407A #1A7FD0 #22B8F0 #A8F4FE; ring handles #3A3A6A #7A84B8 #C8D0EE #F4F6FF.
Face (most important detail), as the FOURTH image: two BIG BLUE EYES, each 2 squares wide and 2-3 tall (dark blue, bright blue and 1 white highlight square), a dark brow line just above each; a 1-2 square pink smiling mouth on the face's middle line; the straight bangs down to the brows, never over the eyes. The eye colours are used only by the eyes.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between her feet on the middle column (x=512, the blue line), the top of the cowlick on the green line, the chin on the orange line (version 1) or the purple line (version 2). Nothing below the soles (the game draws the health bar right under them): the scissor points stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the top of the cowlick to the soles (compare with the SECOND image); the head as tall as the HEAD line says; at most 32 squares across with the scissors; all squares 8x8 on one grid; at most 28 colours; one outline colour; both blue eyes with brows; the two black bows, the drill curls, the white dress with the purple bow and gold star, the navy hem with gold dots, the purple stockings, the white boots and the open scissors with two rings and two shortened cyan blades all readable; nothing below the soles.
VERSION 1 (gwen_design_1.png): HEAD 12 squares from the top of the cowlick to the chin (a game-size chibi head, the face about 8 squares wide); 40 squares in all.
VERSION 2 (gwen_design_2.png): HEAD 10 squares from the top of the cowlick to the chin (closer to the picture, the face about 7 squares wide), a longer dress and legs; 40 squares in all; everything else as version 1.
```

## 交回前自查

- [ ] 呆毛顶到鞋底 40 格（最多 48），版本 1 头 12 格、版本 2 头 10 格；鞋底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 28 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；白裙、皮肤、深紫前片、深藏青裙摆、紫长袜、天蓝头发、青蓝刀刃分得开；
- [ ] 两只大蓝眼睛和眉毛、齐刘海、呆毛、两个黑蝴蝶结、两边螺旋卷；
- [ ] 腰间紫蝴蝶结 + 金星、裙摆一排金点、白色高跟短靴；
- [ ] 剪刀：两个银蓝环把手 + 两片压短的青蓝刀刃、刃口亮边，一只手握着；刀尖在鞋底以上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
