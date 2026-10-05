# 泽拉斯：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画（`xerath/1_picture.png`，原画 A：悬浮站立，两臂垂在身侧略张开，蓝色能量爪半张）在**游戏尺寸**重新画。
> - **大小**：从**兜帽顶到腿尖 40 格**、最宽约 30 格（连两只爪子）。两个腿尖在第 99 行（y=792–799），两腿尖中间在中间那一列（x=512，蓝线）；绿线 = 兜帽顶，橙线 = 兜帽下沿（A 版），紫线 = 兜帽下沿（B 版）。大小、姿势和位置照 `xerath/2_target_size.png`（原画直接缩到这个大小的灰剪影）。
> - **原画的头比较小**（兜帽只占身高约 15%），**游戏里要大很多**：**版本 A** 兜帽顶到兜帽下沿 **13 格**（兜帽约 11 格宽，开口里两只眼睛清楚）；**版本 B** **11 格**（兜帽约 10 格宽，身体更长）。两版都是 40 格高：宽肩（两块带尖刺的大肩甲）、胸前铁链和金色五边形封印、手臂石板和蓝色爪子、两条一节节变细的尖腿（没有脚，悬浮）。
> - **干净、不要细节（最重要）**：最多 26 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。铠甲是深紫灰色的，要用**几档紫灰加亮紫灰的边缘高光**画出石板，不要糊成一块黑；石板之间的能量身体用**亮青、浅青、白**几档平涂（看起来在发光，但不要柔光）。去掉这个尺寸看不清的细节：石板上的回纹 = 一两条深色线或干脆不画、铁链 = 一串 1 格宽的灰色格子（亮暗交替）、金色封印 = 3×3 格（中间 1 格橙色）、肩甲尖刺 = 1–2 格的小尖。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，兜帽顶到腿尖只有 40 格**。
> - **脸**：兜帽是圆顶、中间一道竖棱、下沿一圈亮边；**开口里是发光的能量脸**，两只**白色三角眼**在同一行（近侧眼在左、2 格宽，远侧眼 1–2 格宽），眼睛周围一圈亮青。眼睛不能被挡住，眼睛的白色只用在眼睛上（能量身体最亮的那档用浅青，不要用眼睛的纯白）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`xerath/6_size_guide.png` 是原画直接缩到这个大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 格时，把最接近的那一张也交来（不要超过 48 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色，描边只用一种近黑色。交付到 `outputs/xerath-model/`：`xerath_design_A.png`、`xerath_design_B.png`（1024×1024）和各自的原尺寸图 `xerath_design_A_1x.png`、`xerath_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来兜帽顶到腿尖是多少格、头是多少格），最好再打成一个 zip（`xerath_design_pack.zip`）。

## 附图（都在压缩包的 `xerath/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：圆顶石兜帽和两只白色三角眼、两块带尖刺的肩甲、胸前交叉的铁链和金色五边形封印（橙色符文）、石板之间发光的青色能量身体、手臂石板、两只蓝色能量爪、两条一节节变细的尖腿 |
| `2_target_size.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 40 行的灰剪影；红线 = 腿尖那一行的下沿，蓝线 = 两腿尖中间，绿线 = 兜帽顶（40 格），橙线 = 兜帽下沿（A 版），紫线 = 兜帽下沿（B 版） | **大小、姿势和位置照它**（头要按 A/B 的格数画大） |
| `3_quality_bar.png` | 本包里的丽桑卓（27×42）、瑞兹（25×41）、崔斯特（24×41）、剑魔（40×40）、蛮王（53×37），游戏里现在的样子 ×8，同一条地面线 | **像素大小和干净程度照它们**；悬浮没有脚的身体照丽桑卓，深色铠甲的亮边照剑魔、蛮王 |
| `4_head.png` | 原画的兜帽和眼睛，放大 | 兜帽形状、竖棱、亮边、两只三角眼 |
| `5_hands.png` | 原画的两只能量爪，放大 | 爪子的形状和蓝色几档 |
| `6_size_guide.png` | 原画直接缩到这个大小，同一画布、同一地面线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_idle.png` | 英雄联盟原版的待机（模型渲染） | 只看铠甲的结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：兜帽顶到腿尖 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照游戏、长相照原画**：头按版本 A/B 的格数；3/4 正面朝右；悬浮站立，两臂垂在身侧略张开，两只爪子半张；两条尖腿并在一起往下变细，两个尖头落在第 99 行。
- **干净**：最多 26 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：石甲是深紫、能量是深一点的青蓝），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。能量身体露出来的地方是成片的亮青，不要碎成很多单格。
- **色板**（从原画取，可以微调）：#0A0A12 outline (the only near-black); purple-grey stone armour #241C34 #3A2E4E #54446C #76628E #A48AB0 #CDBFD6 (lit edges); arcane energy body #1890E8 #18B4FC #59ECFC #A8FAFD #E4FEFF; azure claws #1E6CD8 #2FA4F4 #8EDCFF; steel chains #2C3448 #56627A #9AA6B8; gold seal #8A5410 #E09A1C #FFD040 with an orange rune #FF6A10; eyes #FFFFFF (eyes only).
- **腿尖以下什么都不能有**（游戏在这条线下画血条）：腿尖在第 99 行，下面一格都不能有。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`xerath_design_A.png` 和 `xerath_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`xerath/` 里的 1、2、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Xerath, an ancient sorcerer whose body is pure glowing ARCANE ENERGY (bright cyan, pale cyan and white) bound inside separate DARK PURPLE-GREY STONE ARMOUR PLATES, the energy showing in every gap between them: a rounded stone HOOD with a ridge down its middle and a light rim, and in its opening a glowing face with TWO white TRIANGULAR EYES; a big stone PAULDRON with small spikes on each shoulder; two iron CHAINS crossing the chest and meeting at a GOLD PENTAGON SEAL with an orange rune; stone plates on the upper arms and forearms; two bright AZURE-BLUE CLAWED HANDS of energy; NO FEET - two legs of stacked stone plates tapering down to two SHARP POINTS; he floats. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size - use it for his SIZE, his POSE and his PLACE in the canvas (but draw the head bigger, as the HEAD line says). THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the first one floats without feet; the fourth and fifth show dark armour drawn with lit edges). FOURTH: the FIRST image's hood and eyes, big. FIFTH: the FIRST image's two clawed hands, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in the same idle - ONLY for how the armour is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 40 squares from the top of his hood to the tips of his legs and at most 32 squares across (the claws included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares: 40 squares tall, no more.
Pose: the FIRST image's pose and the SECOND image's shape: floating upright in 3/4 FRONT view facing image right; the arms hanging at his sides held a little away from the body, the clawed hands half open; the two pointed legs close together under him, their two tips on the lowest row; the hood's opening turned toward the viewer.
Game proportions: the HEAD line at the end says how many squares from the top of the hood to its lower rim; the rest shares the remaining squares. Broad spiked shoulders, a slimmer waist, the legs tapering to points; the eyes, the gold seal, the chains, the claws and the shoulder spikes drawn big enough to read.
Clean, not detailed (most important): at most 26 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. The armour is DARK PURPLE-GREY stone: draw it in the purple-grey shades with light lilac-grey lit edges (never one flat black mass - near-black is only the outline), so the separate plates read; the energy between the plates in solid patches of bright cyan with pale cyan highlights (not broken into single squares); the claws azure blue. Drop what does not read at this size: the carved patterns on the plates are one or two dark lines or nothing, the chains a row of 1-square grey links (light and dark alternating), the seal 3x3 gold squares with 1 orange square in the middle, the shoulder spikes 1-2 square points.
Palette (from the FIRST image, adjust if needed): #0A0A12 outline (the only near-black); purple-grey stone armour #241C34 #3A2E4E #54446C #76628E #A48AB0 #CDBFD6 (lit edges); arcane energy body #1890E8 #18B4FC #59ECFC #A8FAFD #E4FEFF; azure claws #1E6CD8 #2FA4F4 #8EDCFF; steel chains #2C3448 #56627A #9AA6B8; gold seal #8A5410 #E09A1C #FFD040 with an orange rune #FF6A10; eyes #FFFFFF (eyes only).
Face (most important detail), as the FOURTH image: the rounded hood with its middle ridge and a light rim along its lower edge; inside its opening a glowing face: TWO white triangular EYES on the SAME row (the near eye at image left, two squares wide, the far eye 1-2 squares wide), a ring of bright cyan around them, darker energy between. Nothing covers the eyes. The pure white #FFFFFF is used only by the eyes.
Size and place: exactly where the SECOND image's grey shape stands: the leg tips' lowest row at y=792-799 (square row 99, the red line), the point between the two tips on the middle column (x=512, the blue line), the top of the hood on the green line, the lower rim of the hood on the orange line (version A) or the purple line (version B). Nothing below the leg tips (the game draws the health bar right under them).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 40 squares from the top of the hood to the leg tips (compare with the SECOND image); the head as tall as the HEAD line says; all squares 8x8 on one grid; at most 26 colours; one outline colour; both eyes visible and level; the hood, the spiked pauldrons, the chains and gold seal, the glowing energy between the plates, the blue claws and the two pointed legs all readable; nothing below the tips.
VERSION A (xerath_design_A.png): HEAD 13 squares from the top of the hood to its lower rim (a game-size chibi head: the hood about 11 squares wide); 40 squares in all.
VERSION B (xerath_design_B.png): HEAD 11 squares from the top of the hood to its lower rim (the hood about 10 squares wide), a longer body; 40 squares in all; everything else as version A.
```

## 交回前自查

- [ ] 兜帽顶到腿尖 40 格（最多 48），A 头 13 格、B 头 11 格；腿尖在第 99 行、两腿尖中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 26 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；石甲有亮紫灰边、不是一块黑；能量是成片的亮青；
- [ ] 两只白色三角眼同一行、看得清；
- [ ] 带尖刺的肩甲、铁链和金色封印、蓝色爪子、两条尖腿都看得出来；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、地面线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
