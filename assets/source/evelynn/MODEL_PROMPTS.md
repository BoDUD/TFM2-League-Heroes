# 伊芙琳：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`evelynn/1_evelynn_picture.png`，原画 A：英雄联盟的待机，近侧爪子抬到下巴旁，两条鞭子在身后膝盖高度弯曲）在**游戏尺寸**重新画。
> - **大小**：从**发顶到脚底 40 格**、最宽 34 格（连鞭子）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 发顶，黄线 = 眼睛那一行，橙线 = 下巴（A 版；B 版这三条都低 2 行，脚底不变）。大小、姿势、头的大小和位置照 `evelynn/2_target_size.png`（原画按游戏比例重新拼好再缩小的灰剪影：深一点的灰是头发和头，中灰是身体，最深的灰是两条鞭子）。
> - **原画是成人比例**（发顶到下巴只占身高 20%），**游戏里是 Q 版大头**：**版本 A** 发顶到下巴 **15 格**（额头以上的头发约 5 行、脸约 9 行 9 格宽，和原版的舞娘、恶魔、鞭子师一个比例）；**版本 B** **13 格**（头发约 4 行、脸约 8 行）。两版都是 40 格高，身材修长：窄肩、细腰、踩高跟的长腿。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。紧身衣和鞭子在游戏里是深色的，要用**靛蓝、紫色的几档颜色加亮边**画出手臂、腿和鞭子，不要糊成一块黑；皮肤淡而冷、头发白配亮粉、前臂和大腿亮品红。去掉这个尺寸看不清的细节：每只手的爪子 2–3 格淡粉、胸前的 V 几格品红、高跟鞋的尖刺一格。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，发顶到脚底只有 40 格**。
> - **脸**：两只**亮黄色的眼睛**在同一行（近侧眼在左、两眼之间隔 1–2 格淡色皮肤，远侧眼窄一格），每只眼睛上面一道深色睫毛，刘海就在睫毛上面，淡色脸颊，**一格品红色的嘴**；头发包住脸（往后飘的大团在后上方、两缕在肩前），**不能挡住眼睛**。眼睛的颜色只用在眼睛上。
> - **两条鞭子（标志）**：两条紫色长触手，2–3 格粗，上沿一道亮紫色，末端 3–4 格长的尖刃；从后腰长出来、在腿后膝盖高度弯曲，**和后背连在一起**，**不能低于脚底那一行**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`evelynn/7_size_guide.png` 是拼好的原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，我按格子取回再整行整列删到目标（脸不删）。**生图的原稿也一起交来**（不要只交脚本拼出来的图）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/evelynn-model/`：`evelynn_design_A.png`、`evelynn_design_B.png`（1024×1024）和各自的原尺寸图 `evelynn_design_A_1x.png`、`evelynn_design_B_1x.png`，生图原稿，色板，`HANDOFF.md`（**最后写**，写明每张读回来发顶到脚底是多少格、头是多少格），最好再打成一个 zip（`evelynn_design_pack.zip`）。

## 附图（都在压缩包的 `evelynn/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_evelynn_picture.png` | 用户选的原画 A | **长相和姿势**：白发粉挑染、黄眼睛、淡紫皮肤、靛蓝紧身衣、品红前臂和大腿、淡粉长爪、高跟、两条紫鞭 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画按游戏比例重新拼好再缩小的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 发顶（40 格），黄线 = 眼睛，橙线 = 下巴（A 版） | **大小、姿势、头的大小和位置照它** |
| `3_quality_bar.png` | main 里的leblanc（43×32）、kaisa（42×25）、ahri（40×32）、camille（46×23）、diana（43×27），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_tfm2_style.png` | 团战经理2 原版的whip_master（34×22）、dancer（34×23）、demon（32×25）、shadowmancer（33×17）、spirit_caller（35×17） ×8 | **女性的脸、大头发、鞭子和爪子在这个尺寸怎么画**：大块平涂、少色、形状清楚 |
| `5_head_ref.png` | 原画的头，放大（840×820） | 头发、刘海、黄眼睛、嘴、两缕前垂的头发 |
| `6_lashers_ref.png` | 原画的两条鞭子和两只带爪的手，放大 | 鞭子的粗细、亮边、尖刃；爪子 |
| `7_size_guide.png` | 按游戏比例拼好的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：发顶到脚底 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材修长；3/4 正面朝右；近侧爪子抬到下巴旁，远侧手臂垂在身侧，两条鞭子在身后。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：紧身衣是深靛蓝，鞭子是深紫，品红是深品红），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#120C1C outline (the only near-black); the DARK INDIGO suit #1E1646 #2E2470 #463C9E #6A62C8 (lit edges); the lashers violet #2A0E5C #4A1C96 #7A34D2 #B070FF (a bright violet edge); magenta-pink (forearms, thighs, the V, heels) #6E1240 #B81E6A #EE3C8C #FF86BC; pale icy-lavender skin #6C6C9E #9C9CCC #CACAEE #ECECFF; hair white and pink #B8B8D8 #F4F4FF #F05AA0 #FF9ACA; claws pale pink #FFC0DC; lips #C0306A; eyes bright yellow #FFD21E with a dark slit。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，鞭子不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`evelynn_design_A.png` 和 `evelynn_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`evelynn/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Evelynn, a slender demon woman: big WHITE hair streaked with HOT PINK swept straight back from the forehead like a flame (pink at the tips), a short fringe above the eyes and two long locks curling forward in front of her shoulders; pale icy-LAVENDER skin, glowing YELLOW eyes with dark violet eye shadow, magenta lips with a sly smile; a DARK INDIGO bodysuit with long sleeves and a deep V neckline (pale skin showing), a magenta V at its bottom; the hips and thighs MAGENTA-PINK in panels fading to dark indigo below the knees; dark indigo high heels with spikes; the forearms and hands bright MAGENTA-PINK with long pale-pink CLAWS; and her signature: two long VIOLET LASHERS (whip tendrils) growing from her lower back, curling behind her at knee height with sharp blade tips (one tip poking out in front of her knees). SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat shape in greys - the FIRST image recomposed at GAME proportions and shrunk to game size (dark-mid grey the hair and head, mid grey the body, the darkest grey the two lashers) - use it for her SIZE, her POSE, her HEAD SIZE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: official women heroes of this game at 8x (a whip master, a dancer, a demon, a shadowmancer, a spirit caller) - copy how a woman's face, big hair, a whip and claws are drawn at this size: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the hair, the fringe, the yellow eyes, the lips, the two locks. SIXTH: the FIRST image's lashers and clawed hands, big. SEVENTH: the SECOND image's composition in the FIRST image's colours, shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of the hair to her soles and at most 34 squares across (the lashers included). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing upright in 3/4 FRONT view facing image right, her weight on the back leg, the hip cocked, the near foot a short step forward on its heel; her NEAR hand raised beside her chin, the clawed fingers curled; her FAR arm hanging at her side, the claws by the thigh; the two lashers curving out behind her from the lower back at knee height, their blade tips curled up, one tip showing in front of her knees.
Game proportions: the HEAD line at the end says how many squares from the hair's top to the chin (the swept-back hair about a third of that); the rest shares the remaining squares. She is slim and tall: narrow shoulders, a small waist, long legs on the heels; the hair, the claws and the lashers drawn big enough to read.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The suit and the lashers are DARK in the game: draw them in their indigo and violet shades with lit edges (never one flat black mass - near-black is only the outline), so the arms, the legs and the lashers read; the skin pale and cool, the hair white with bright pink, the forearms and thighs bright magenta. Drop what does not read at this size: the claws are 2-3 pale-pink squares per hand, the V on the chest a few magenta squares, the heels' spikes one square each.
Palette (from the FIRST image, adjust if needed): #120C1C outline (the only near-black); the DARK INDIGO suit #1E1646 #2E2470 #463C9E #6A62C8 (lit edges); the lashers violet #2A0E5C #4A1C96 #7A34D2 #B070FF (a bright violet edge); magenta-pink (forearms, thighs, the V, heels) #6E1240 #B81E6A #EE3C8C #FF86BC; pale icy-lavender skin #6C6C9E #9C9CCC #CACAEE #ECECFF; hair white and pink #B8B8D8 #F4F4FF #F05AA0 #FF9ACA; claws pale pink #FFC0DC; lips #C0306A; eyes bright yellow #FFD21E with a dark slit.
Face (most important detail), as the FIFTH image: TWO bright-yellow eye squares on the SAME row (the near eye at image left of the far one, one or two squares of pale skin between them, the far eye one square narrower in 3/4 view), a dark lash line above each eye, the fringe just above the lashes, pale cheeks, one magenta square for the lips; the hair frames the face (the swept-back mass behind and above, the two locks in front of the shoulders) and never covers the eyes. The eye colour is used only by the eyes.
The lashers, as the SIXTH image: two long violet tendrils 2-3 squares thick, each with a bright violet edge on top and a sharp blade tip 3-4 squares long; they leave her lower back, curl behind her legs at knee height and stay ABOVE the soles' row; they are part of her body, joined to her back, never loose.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between her feet on the middle column (x=512, the blue line), the hair's top on the green line, the eye line on the yellow line and the chin on the orange line (version A; version B puts the hair's top, the eyes and the chin 2 rows lower and keeps the soles). Nothing below the soles (the game draws the health bar right under them): the lashers end above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the hair's top to the soles (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; both yellow eyes visible and level; both lashers joined to her back and above the soles; nothing below the soles.
VERSION A (evelynn_design_A.png): HEAD 15 squares from the hair's top to the chin (a game-size chibi head like the FOURTH image's women: the hair above the forehead about 5 rows, the face about 9 rows and 9 squares wide); 40 squares in all.
VERSION B (evelynn_design_B.png): HEAD 13 squares from the hair's top to the chin (the hair above the forehead about 4 rows, the face about 8 rows and 8 squares wide), a longer body; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 发顶到脚底 40 格（最多 48），A 头 15 格、B 头 13 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；紧身衣和鞭子有亮边，不是一块黑；
- [ ] 两只黄眼睛同一行、看得清，脸没被头发挡住；
- [ ] 两条鞭子和后背连着、在脚底以上；最后写 `HANDOFF.md`，生图原稿也交来。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
