# 泰达米尔（蛮王）：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`tryndamere/1_picture.png`，原画 A：前倾弓步，后面那只手握着大弯刀拖在身后，前面那只手张开在身前）在**游戏尺寸**重新画。
> - **大小**：从**盔角尖到脚底 42 格**、最宽约 38 格（连刀）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 盔角尖，橙线 = 下巴（A 版），紫线 = 下巴（B 版）。大小、姿势和位置照 `tryndamere/2_target_size.png`（原画直接缩到这个大小的灰剪影）。
> - **原画的头已经比较大**（盔角到下巴占身高约 26%），**游戏里再大一点**：**版本 A** 盔角尖到下巴 **14 格**（盔顶以上的角约 2 行、脸约 8 格宽）；**版本 B** **12 格**（脸约 7 格宽，身体更长）。两版都是 42 格高，**身材魁梧**（和 `3_quality_bar.png` 里的瑟提、德莱厄斯一样壮）：宽肩、厚胸、粗手臂、腿短而有力。**大刀约 22–26 格长、5–7 格宽**，刀背 4–5 个锯齿，护手处一颗 **2×2 的青色宝珠**，刀柄末端一颗 1 格的青珠。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。头盔、甲裙、靴子和刀在游戏里是深灰黑色的，要用**几档深灰蓝加银白亮边**画出甲片、刀刃和锯齿，不要糊成一块黑；皮肤古铜色、缠手白布、鳞甲裙深青、宝石亮青。去掉这个尺寸看不清的细节：额头宝石 = 1–2 格亮青、肩甲上的宝石 = 1 格、甲裙的花纹 = 一两条深色线、鳞片 = 两档深青交错的几格、兽首护裆 = 2×3 格加 1 格青。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，盔角尖到脚底只有 42 格**。
> - **脸**：头盔护住头顶和两颊，**脸露出来**：两只眼睛在同一行（近侧眼在左、两格宽，远侧眼一格宽贴着右边的脸颊；原画里只露出一只眼，游戏尺寸要**两只都画出来**），每只眼睛上面一道往鼻梁压下来的深色眉线（凶狠），**下巴一圈短黑胡子**，张开的嘴是 1–2 格深红。额头正中一格亮青宝石。盔后一大把**黑色长发**披到背上（比原画短一点，别盖住刀柄）。眼睛不能被挡住，眼睛的颜色只用在眼睛上。
> - **直接按游戏尺寸画**，不要先画大再缩小。`tryndamere/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 42 格时，把最接近的那一张也交来（不要超过 50 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/tryndamere-model/`：`tryndamere_design_A.png`、`tryndamere_design_B.png`（1024×1024）和各自的原尺寸图 `tryndamere_design_A_1x.png`、`tryndamere_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来盔角尖到脚底是多少格、头是多少格），最好再打成一个 zip（`tryndamere_design_pack.zip`）。

## 附图（都在压缩包的 `tryndamere/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：角盔和额头青宝石、黑胡子、黑色长发、古铜色赤膊、左肩深灰大肩甲、白布缠手、斜挎皮带、白布腰带和兽首护裆、层叠甲裙和深青鳞甲裙、深灰靴子、后手拖着的锯齿大弯刀和两颗青珠 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 42 行的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 盔角尖（42 格），橙线 = 下巴（A 版），紫线 = 下巴（B 版） | **大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的瑟提（26×42）、德莱厄斯（36×42）、剑魔（40×40）、凯隐（40×40）、盖伦（35×37），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**；壮汉的身材照瑟提、德莱厄斯，大兵器照剑魔、凯隐 |
| `4_head.png` | 原画的头，放大 | 角盔、额头宝石、脸、胡子、黑发、肩甲 |
| `5_sword.png` | 原画的大刀和握刀的手、空着张开的手，放大 | 刀的形状、锯齿、银白刃口、两颗青珠，两只手 |
| `6_size_guide.png` | 原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看装备的结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：盔角尖到脚底 42 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材魁梧；3/4 正面朝右；前倾弓步、两脚分开；后手（画面左边）握刀柄、刀身斜着拖在身后，刀尖在后脚后面、不低于脚底；前手（画面右边）张开在身前。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：皮肤是红褐、钢甲是深灰蓝、鳞甲是深青），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0E0E16 outline (the only near-black); bronze skin #8C4A2C #C8784A #E8955C #FFB97A; black hair and beard #141420 #2A3044 #44506A; dark steel (helmet, pauldron, skirt plates, boots, sword) #1C1E2C #303A52 #4C5C78 #7A8AA6 #C8D2E4; grey-white cloth wraps and sash #6E6E7C #B0AEBC #E2DEE8; brown leather strap and belt #3A2418 #6A4630; dark teal scale skirt #0C2A36 #145060 #2A7A86; teal-cyan gems and sword orbs #00A89C #3CF0DC #C8FFF8; the mouth #A0302C; eyes #E8F4FF (eyes only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，刀尖不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`tryndamere_design_A.png` 和 `tryndamere_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`tryndamere/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Tryndamere, a huge barbarian warrior: a dark grey-black iron HELMET with a pair of short curved HORNS, a bright TEAL gem on the forehead, cheek guards framing the face; the face visible with fierce eyes, a short black BEARD and an open snarling mouth; a big mane of long BLACK HAIR falling down his back; bare bronze-tanned skin, a massive chest and thick arms; a big dark grey PAULDRON on his front shoulder (image right) with teal gems; both forearms WRAPPED in grey-white cloth with dark bracers; a brown leather strap across the chest; a grey-white cloth SASH with a dark BEAST-HEAD belt plate set with a teal gem; a layered skirt of dark grey iron PLATES over a dark TEAL SCALE-MAIL skirt with a jagged hem; heavy dark grey armoured boots; and his signature weapon: a HUGE dark grey curved GREATSWORD with a SERRATED back, a silver-white edge, a big glowing TEAL ORB at the guard and a small one at the pommel, held low by its grip in his BACK hand (image left) and trailing behind him. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size - use it for his SIZE, his POSE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first two for a big muscular body, the third and fourth for a huge weapon). FOURTH: the FIRST image's head, big - the horned helmet, the gem, the face, the beard, the hair, the pauldron. FIFTH: the FIRST image's greatsword with the hand holding it, and the open free hand, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the armour is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 42 squares from the tips of his helmet horns to his soles and at most 40 squares across (the sword included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 42 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: a wide low stance in 3/4 FRONT view facing image right, leaning forward, feet apart, knees bent; the BACK arm (image left) reaching down behind him, its hand gripping the sword's hilt at hip height, the blade slanting down and back with its tip just behind his back foot, at or above the soles' row; the FRONT arm (image right) forward and a little raised, the hand open with clawed fingers; the black hair hanging behind the helmet; the head turned toward the viewer.
Game proportions: the HEAD line at the end says how many squares from the horn tips to the chin; the rest shares the remaining squares. He is big and powerful like the first two heroes of the THIRD image: broad shoulders, a thick chest and arms, short strong legs; the horns, the forehead gem, the white wraps, the pauldron and the sword's orbs drawn big enough to read. The sword about 22-26 squares long and 5-7 squares wide, 4-5 serrations along its back, a 2x2 teal orb at the guard and a 1-square orb at the pommel.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The helmet, the skirt plates, the boots and the sword are DARK GREY in the game: draw them in the steel shades with silver-white lit edges (never one flat black mass - near-black is only the outline), so their plates, the edge and the serrations read; the skin bronze, the wraps grey-white, the scale skirt dark teal, the gems bright teal. Drop what does not read at this size: the forehead gem is 1-2 bright teal squares, the pauldron gem 1 square, the skirt's engravings one or two dark lines, the scales two dark teal shades in a few staggered squares, the beast-head plate 2x3 squares with 1 teal square.
Palette (from the FIRST image, adjust if needed): #0E0E16 outline (the only near-black); bronze skin #8C4A2C #C8784A #E8955C #FFB97A; black hair and beard #141420 #2A3044 #44506A; dark steel (helmet, pauldron, skirt plates, boots, sword) #1C1E2C #303A52 #4C5C78 #7A8AA6 #C8D2E4; grey-white cloth wraps and sash #6E6E7C #B0AEBC #E2DEE8; brown leather strap and belt #3A2418 #6A4630; dark teal scale skirt #0C2A36 #145060 #2A7A86; teal-cyan gems and sword orbs #00A89C #3CF0DC #C8FFF8; the mouth #A0302C; eyes #E8F4FF (eyes only).
Face (most important detail), as the FOURTH image: the helmet covers the top of the head and frames the cheeks, the face is open: TWO eyes on the SAME row (the near eye at image left, two squares wide, the far eye one square wide against the right cheek), a dark brow line just above each eye angled down toward the nose (fierce), a short black BEARD round the jaw and chin, the open mouth 1-2 dark red squares; one bright teal gem square in the middle of the forehead; the long black hair spilling from the back of the helmet. Nothing covers the eyes. The eye colour is used only by the eyes.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the horn tips on the green line, the chin on the orange line (version A) or the purple line (version B). Nothing below the soles (the game draws the health bar right under them): the sword's tip ends at or above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 42 squares from the horn tips to the soles (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; both eyes visible and level, the beard; the horned helmet, the white wraps, the pauldron and the greatsword with its teal orbs all readable; nothing below the soles.
VERSION A (tryndamere_design_A.png): HEAD 14 squares from the horn tips to the chin (a game-size chibi head: the horns about 2 rows above the helmet's crown, the face about 8 squares wide); 42 squares in all.
VERSION B (tryndamere_design_B.png): HEAD 12 squares from the horn tips to the chin (the face about 7 squares wide), a longer, bigger body; 42 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 盔角尖到脚底 42 格（最多 50），A 头 14 格、B 头 12 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；头盔、甲裙、靴子和刀有银白亮边和甲片，不是一块黑；
- [ ] 两只眼睛同一行、看得清，短黑胡子、额头青宝石；
- [ ] 角盔、白布缠手、肩甲、兽首护裆、深青鳞甲裙、后手拖着的锯齿大刀和两颗青珠都看得出来；刀尖在脚底以上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
