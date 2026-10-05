# 韦鲁斯：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`varus/1_varus_picture.png`，原画 A：站着、微微驼背，近侧手提着大弓立在腿边，远侧手垂在身侧）在**游戏尺寸**重新画。
> - **大小**：从**头顶到脚底 40 格**、最宽 28 格（连弓）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；绿线 = 头顶，黄线 = 眼睛那一行，橙线 = 下巴（A 版；B 版这三条都低 2 行，脚底不变）。大小、姿势、头的大小和位置照 `varus/2_target_size.png`（原画按游戏比例重新拼好再缩小的灰剪影：深一点的灰是头，中灰是身体，最深的灰是弓）。
> - **原画是成人比例**（头顶到下巴只占身高 18%），**游戏里是 Q 版大头**：**版本 A** 头顶到下巴 **15 格**（眉毛以上的头发约 5 行、脸约 10 格宽）；**版本 B** **13 格**（头发约 4 行、脸约 9 格宽）。两版都是 40 格高，身材精瘦：细腰、胸口稍宽、腿长。弓约 26–30 格高、6–8 格宽，每边弓臂 3–4 根尖刺。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。腿甲、靴子、弓在游戏里是紫黑色的，要用**几档紫色加紫色亮边**画出甲片和尖刺，不要糊成一块黑；皮肤白、围巾鲜红、护符金边青心。去掉这个尺寸看不清的细节：红宝石 = 1 格红、铆钉 = 单格灰、纹身 = 2–3 格青、腿上的小光点 = 单格紫。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，头顶到脚底只有 40 格**。
> - **脸**：两只**粉紫色发光的眼睛**在同一行（近侧眼在左、两眼之间隔 1–2 格皮肤，远侧眼窄一格；原画里只露出一只眼，游戏尺寸要**两只都画出来**），每只眼睛上面一道往鼻梁压下来的深色眉线（表情阴沉），白皮肤、一道小嘴；头带在眉毛上面、中间一格红宝石；银白头发往后梳、在脑后扎起。眼睛不能被挡住，眼睛的颜色只用在眼睛上。
> - **直接按游戏尺寸画**，不要先画大再缩小。`varus/7_size_guide.png` 是拼好的原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/varus-model/`：`varus_design_A.png`、`varus_design_B.png`（1024×1024）和各自的原尺寸图 `varus_design_A_1x.png`、`varus_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来头顶到脚底是多少格、头是多少格），最好再打成一个 zip（`varus_design_pack.zip`）。

## 附图（都在压缩包的 `varus/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_varus_picture.png` | 用户选的原画 A | **长相和姿势**：银白后梳扎发、红宝石头带、粉紫色眼睛、红围巾、斜挎皮带和金边青色护符、紫红腐化的小臂和爪、紫黑甲裤和靴子、近侧手里的紫黑活体大弓 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画按游戏比例重新拼好再缩小的灰剪影；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 头顶（40 格），黄线 = 眼睛，橙线 = 下巴（A 版） | **大小、姿势、头的大小和位置照它** |
| `3_quality_bar.png` | main 里的jhin（41×29）、twistedfate（41×24）、kayn（40×40）、aatrox（40×40）、sivir（40×48），游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_tfm2_style.png` | 团战经理2 原版的archer（33×25）、hunter（34×22）、boomerang_hunter（35×27）、demon（32×25）、shadowmancer（33×17） ×8 | **弓和深色铠甲怎么画**：大块平涂、少色、形状清楚 |
| `5_head_ref.png` | 原画的头，放大（776×644） | 头发、头带和红宝石、脸、眼睛、围巾 |
| `6_bow_ref.png` | 原画的弓和握弓的手，放大 | 弓的形状、尖刺、紫光纹路 |
| `7_size_guide.png` | 按游戏比例拼好的原画直接缩到这个大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：头顶到脚底 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数，身材精瘦；3/4 正面朝右；近侧手提弓立在腿边，远侧手臂自然下垂。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：甲和弓是深紫，围巾是深红，皮肤是暖灰），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#120A14 outline (the only near-black); silver-white hair #5E5C8A #9C9CCB #CDD0F0 #F4F5FF; pale skin #8A5E58 #C99A88 #EBCAB6; the red scarf #6E0E12 #B5141C #E8302E; the dark harness strap #1E1A1E #3A3438 #6A6268 with steel studs #A8A8B0; the medallion: gold rim #8A5A10 #E0A820 #FFE070, dark teal disc #183C50 #2E7A8A; the shoulder tattoo #3A8A8A; the crimson corruption (forearms, belly, hips) #5A1028 #9A2048 #D0406E; the purple armour, boots and bow #1E1030 #3A2258 #5E3A88 #8A5CC0; the violet glow (hands, bow veins, leg dots) #A050F0 #E4A8FF; the headband's red gem #E01818; eyes glowing pink-violet #FF70F0 (eyes only)。
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，弓的下端不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`varus_design_A.png` 和 `varus_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`varus/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Varus, a lean corrupted archer: SILVER-WHITE hair swept back and tied behind his head (lavender shades), a thin dark headband with a small RED gem on the forehead, a narrow pale face with a stern brooding look and eyes glowing PINK-VIOLET; a bright RED SCARF round his neck with a long red tail hanging down in front of his far side to the knees; a bare pale lean chest with a teal tattoo on his far shoulder, a dark leather HARNESS strap across the chest holding a big round GOLD-rimmed MEDALLION with a dark teal disc, a small red pendant; both forearms and hands corrupted DARK CRIMSON to PURPLE with claw fingers glowing violet, the belly and hips fading into the same crimson; tight PURPLE-BLACK armoured leggings with plates, spikes and tiny violet dots; heavy purple boots; and his signature weapon: a huge spiked PURPLE-BLACK living BOW with glowing violet veins, held upright by its grip in his NEAR hand (image right), as tall as most of his body. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat shape in greys - the FIRST image recomposed at GAME proportions and shrunk to game size (dark-mid grey the head, mid grey the body, the darkest grey the bow) - use it for his SIZE, his POSE, his HEAD SIZE and his PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: official heroes of this game at 8x (an archer, a hunter, a boomerang hunter, a demon, a shadowmancer) - copy how a bow and dark armour are drawn at this size: big flat areas, few colours, bold readable shapes. FIFTH: the FIRST image's head, big - the hair, the headband and its gem, the face, the eyes, the scarf. SIXTH: the FIRST image's bow and the hand holding it, big. SEVENTH: the SECOND image's composition in the FIRST image's colours, shrunk straight to game size - use it ONLY to see what fits where; it is blurry, do not copy its look.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of his hair to his soles and at most 28 squares across (the bow included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD and FOURTH images. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: standing upright in 3/4 FRONT view facing image right, feet a little apart, shoulders slightly hunched; the FAR arm (image left) hanging at his side with its clawed violet hand; the NEAR arm (image right) lowered, the hand holding the bow's grip at hip height, the bow standing upright beside his near leg, its spiked tips pointing up and down; the scarf's tail hanging; the head turned toward the viewer.
Game proportions: the HEAD line at the end says how many squares from the hair's top to the chin; the rest shares the remaining squares. He is lean and athletic: a narrow waist, the chest a little broad, long legs in armoured leggings; the medallion, the scarf, the glowing hands and the bow drawn big enough to read. The bow about 26-30 squares tall, about 6-8 squares wide with 3-4 spikes on each limb.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The leggings, boots and bow are PURPLE-BLACK in the game: draw them in the purple shades with violet lit edges (never one flat black mass - near-black is only the outline), so their plates and spikes read; the skin pale, the scarf strong red, the medallion gold with a teal centre. Drop what does not read at this size: the gem is 1 red square, the studs single grey squares, the tattoo 2-3 teal squares, the leg dots single violet squares.
Palette (from the FIRST image, adjust if needed): #120A14 outline (the only near-black); silver-white hair #5E5C8A #9C9CCB #CDD0F0 #F4F5FF; pale skin #8A5E58 #C99A88 #EBCAB6; the red scarf #6E0E12 #B5141C #E8302E; the dark harness strap #1E1A1E #3A3438 #6A6268 with steel studs #A8A8B0; the medallion: gold rim #8A5A10 #E0A820 #FFE070, dark teal disc #183C50 #2E7A8A; the shoulder tattoo #3A8A8A; the crimson corruption (forearms, belly, hips) #5A1028 #9A2048 #D0406E; the purple armour, boots and bow #1E1030 #3A2258 #5E3A88 #8A5CC0; the violet glow (hands, bow veins, leg dots) #A050F0 #E4A8FF; the headband's red gem #E01818; eyes glowing pink-violet #FF70F0 (eyes only).
Face (most important detail), as the FIFTH image: TWO pink-violet eye squares on the SAME row (the near eye at image left of the far one, one or two squares of skin between them, the far eye one square narrower in 3/4 view), a dark brow line just above each eye angled down toward the nose (stern), pale skin cheeks, a small mouth line; the headband sits ABOVE the brows with its red gem in the middle; the silver hair swept back over the top of the head and tied at the back. Nothing covers the eyes. The eye colour is used only by the eyes.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the hair's top on the green line, the eye line on the yellow line and the chin on the orange line (version A; version B puts the hair's top, the eyes and the chin 2 rows lower and keeps the soles). Nothing below the soles (the game draws the health bar right under them): the bow's lower tip ends at or above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the hair's top to the soles (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; both eyes visible and level; the medallion, the red scarf and the bow in the near hand all readable; nothing below the soles.
VERSION A (varus_design_A.png): HEAD 15 squares from the hair's top to the chin (a game-size chibi head like the FOURTH image's heroes: the hair about 5 rows above the brows, the face about 10 squares wide); 40 squares in all.
VERSION B (varus_design_B.png): HEAD 13 squares from the hair's top to the chin (the hair about 4 rows, the face about 9 squares wide), a longer body; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 头顶到脚底 40 格（最多 48），A 头 15 格、B 头 13 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png`、`4_tfm2_style.png` 一个像素大小；紫黑甲和弓有亮边和甲片，不是一块黑；
- [ ] 两只粉紫色眼睛同一行、看得清，头带和红宝石在眉毛上面；
- [ ] 红围巾、金边青色护符、近侧手里的大弓都看得出来；弓的下端在脚底以上；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
