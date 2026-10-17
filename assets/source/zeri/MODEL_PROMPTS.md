# 泽丽：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`zeri/1_picture.png`：英雄联盟的待机，站着，电击步枪竖着举在画面右侧的肩旁、枪口朝上，另一只手垂在身侧；两个尖刺发髻、宽大的青蓝外套、黄色背心、深紫红紧身裤、棕色短靴）在**游戏尺寸**重新画。
> - **大小**：**版本 A** 从**发髻尖（她最高的地方，枪口也到这一行）到鞋底 40 格**，**版本 B** 42 格。鞋底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿 / 橙线 = 最高点。姿势和位置照 `zeri/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是步枪）。**不要超过 42 格**：本包的萨勒芬妮、格温画到 45–46 行，在游戏里太大，后来都缩了。
> - **宽度**：整个造型连枪、外套**不能超出两条紫线**：A 最宽 **30 格**，B 最宽 **32 格**（原画缩下来约 20 格，头放大后会宽一些）。
> - **头大一点（游戏比例）**：照原画的比例，脸只有 5–6 格高，**看不清眼睛**。请把头画大：**额头（刘海顶）到下巴 9–10 格**（黄绿色的眼睛、嘴、脸颊的创可贴要清楚），**两个尖刺发髻在头顶上再高 4–5 格**、每个发髻大约和脸一样宽（比原画小一点）；身体相应短一点（腿稍短，像 `3_quality_bar.png` 里的卡尔玛、霞），总高度还是 40 / 42 格。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。颜色分开：**外套青蓝（亮青高光 + 深蓝暗部）；头发柠檬黄绿，发髻外圈深青蓝的尖刺；背心暖黄 + 一道洋红绿闪电（2–3 格）；皮带红棕 + 一个银扣；裤子深紫红；靴子棕色 + 橙色袜口；步枪柠檬黄 + 橙色 + 深灰金属；皮肤暖小麦色；银色的管子和扣子用两档浅灰**。去掉这个尺寸看不清的细节：外套上的扣子 = 最多 3 个 2×2 银点；胸前的管子 = 1 格宽的银线；外套下摆的心形挂件 = 不画或 1 个 2×2；枪上的零件 = 枪口 2 根 1 格宽的电极 + 一块橙色；护膝 = 一个 3×3 的浅棕圆块；背包 = 外套后面露一角黄色。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，最高点到鞋底只有 40（B 42）格**。
> - **头和脸**：3/4 朝右，**两只黄绿色的大眼睛**（各 2 格，带 1 格深色瞳孔）清楚看得见，小嘴（1–2 格），左脸颊一个 1–2 格的白色创可贴；两个发髻在头顶两侧炸开（外圈深青蓝尖刺、里面柠檬黄绿）；黄绿色的刘海和两侧的发丝。脸不能被挡住，枪也不能挡脸。
> - **身体**：站着，画面右侧那只手握着竖起的步枪（枪口朝上，枪在肩旁、头的右边），**握枪的手看得见**；画面左侧那只手自然垂下，**手也看得见**（紫红半指手套）；两腿分开站，两只靴子平平地踩在鞋底线上。
> - **直接按游戏尺寸画**，不要先画大再缩小。`zeri/6_size_guide.png` 是原画直接缩到 40 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 / 42 格时，把最接近的那一张也交来（不要超过 44 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/zeri-model/`：`zeri_design_A.png`、`zeri_design_B.png`（1024×1024）和各自的原尺寸图 `zeri_design_A_1x.png`、`zeri_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来最高点到鞋底是多少格、整个造型多宽），最好再打成一个 zip（`zeri_design_pack.zip`）。

## 附图（都在压缩包的 `zeri/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：尖刺发髻、黄绿眼睛 + 创可贴、青蓝外套 + 银管、黄背心闪电、红棕皮带、深紫红裤 + 护膝、棕靴 + 橙袜口、柠檬黄步枪、紫红半指手套 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（发髻尖到鞋底 40 格）的灰剪影（浅灰 = 步枪）；红线 = 鞋底那一行的下沿，蓝线 = 两脚中间，绿 / 橙线 = 最高点，两条紫线 = 最宽的范围（30 格） | **A 的大小、姿势和位置照它** |
| `2_target_B.png` | 同上，B 的大小（42 格），紫线 = 32 格 | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的萨勒芬妮、莎弥拉、辛德拉、霞、卡尔玛，游戏里现在的样子 ×8，同一条脚底线 | **像素大小、头身比和干净程度照它们** |
| `4_head.png` | 原画的头（发髻、眼睛、创可贴），放大 | 头和脸 |
| `5_parts.png` | 原画的步枪和握枪的手、垂下的手、胸口和管子、背包、两只靴子，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：最高点到鞋底 A 40 格、B 42 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、头放大**：3/4 正面朝右；站立；步枪竖举在画面右侧的肩旁；另一只手垂下；**脸、两只手都看得见**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#100C14 outline (the only near-black); coat #0E3E66 #1670A0 #22A0C8 #6ADCF0; hair #6A9A10 #B4E01E #E8FA5A, hair spikes #12305A #1E5A8A #3A8AB8; tank top #D88A10 #F6C21E #FFE66A; print #E0287A #6AD02A; belt #8A1E1E #C8382E; leggings #3E1838 #5E2A52 #7E3E6C; glove #5A2040 #7E3058; boots #5A2E1E #8A4A30 #B46A44; socks #E08A10 #F6B428; rifle #6A8A10 #C8E828 #F08A18 #3A3A44 #6A6A78; skin #A8603A #D8925E #F2BE88; silver #8A8E9A #C8CCD6 #F2F4F8; eyes #3A6A10 #9AD82A.
- **鞋底以下什么都不能有**（游戏在脚下画血条）：鞋底在第 99 行，下面一格都不能有。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`zeri_design_A.png` 和 `zeri_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`zeri/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Zeri, a lively street girl crackling with electricity: two big SPIKY HAIR BUNS on top of her head (an outer ring of dark teal-blue spikes around bright LIME YELLOW-GREEN hair), lime bangs and side strands, warm tan skin, big YELLOW-GREEN EYES, a small white plaster on her left cheek; an OVERSIZED TEAL-BLUE COAT reaching her thighs with wide rolled sleeves, silver clasps and a silver tube across her chest, a bit of a yellow battery backpack behind her shoulder; a YELLOW TANK TOP with a magenta-and-green lightning print; a red-brown belt with a silver buckle; tight DARK MAROON LEGGINGS with a round knee pad; BROWN ANKLE BOOTS with orange socks; maroon fingerless gloves; an ELECTRIC RIFLE (lime yellow and orange body, dark metal, two small electrodes at the muzzle). SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the rifle in lighter grey - use it for her SIZE, her POSE and her PLACE in the canvas; everything must fit between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size, their head-to-body proportions and their crisp, clean look (all women of this size). FOURTH: the FIRST image's head, big - the hair buns, the eyes, the plaster. FIFTH: the FIRST image's rifle with the hand holding it, the hanging hand, the chest with the tube, the backpack and the boots, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the TOTAL number of squares (the VERSION line) from her highest point (the tips of the hair buns; the rifle's muzzle reaches the same row) to her soles, and at most the WIDTH number of squares across (rifle and coat included). Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose: standing in 3/4 FRONT view facing image right; the image-RIGHT hand holds the rifle UPRIGHT beside her shoulder, muzzle up, the rifle beside her head (not covering the face), the hand on its grip clearly visible; the image-LEFT arm hanging relaxed at her side, the gloved hand clearly visible; legs apart, both boots flat on the soles line; the face turned toward the viewer, both eyes visible.
Game proportions: a BIGGER HEAD than the picture - from the top of the bangs to the chin 9-10 squares, the two hair buns 4-5 squares more above the head, each about as wide as her face (smaller than in the picture) - and a slightly shorter body (shorter legs), like the women in the THIRD image, the total height still TOTAL squares; the yellow-green eyes (2 squares each with a 1-square dark pupil), the mouth, the plaster and the lightning print drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the colours apart: the coat teal-blue with bright cyan highlights and deep blue shadows; the hair lime yellow-green with dark teal-blue spikes around the buns; the tank top warm yellow with a 2-3 square magenta-and-green lightning; the belt red-brown with one silver buckle; the leggings dark maroon; the boots brown with orange socks; the rifle lime yellow and orange with dark grey metal; the skin warm tan; the silver tube and clasps two light greys. Drop what does not read at this size: the coat's clasps at most three 2x2 silver dots, the tube a 1-square silver line, the heart charms at the hem none or one 2x2, the rifle's parts two 1-square electrodes at the muzzle and one orange block, the knee pad one 3x3 light brown round patch, the backpack one yellow corner behind the coat.
Palette (from the FIRST image, adjust if needed): #100C14 outline (the only near-black); coat #0E3E66 #1670A0 #22A0C8 #6ADCF0; hair #6A9A10 #B4E01E #E8FA5A, hair spikes #12305A #1E5A8A #3A8AB8; tank top #D88A10 #F6C21E #FFE66A; print #E0287A #6AD02A; belt #8A1E1E #C8382E; leggings #3E1838 #5E2A52 #7E3E6C; glove #5A2040 #7E3058; boots #5A2E1E #8A4A30 #B46A44; socks #E08A10 #F6B428; rifle #6A8A10 #C8E828 #F08A18 #3A3A44 #6A6A78; skin #A8603A #D8925E #F2BE88; silver #8A8E9A #C8CCD6 #F2F4F8; eyes #3A6A10 #9AD82A.
Face (most important detail), as the FOURTH image: the head in 3/4, lime bangs over the brow, two big YELLOW-GREEN eyes clearly visible, a small nose, a small smiling mouth, a white plaster on her left cheek; the two hair buns bursting on both sides of the top of the head. Nothing covers the face.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' row at y=792-799 (square row 99, the red line), the middle between her feet on the middle column (x=512, the blue line), the highest point on the green/orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: TOTAL squares from the highest point to the soles (compare with the SECOND image); at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the hair buns, the yellow-green eyes, the plaster, the coat, the tank top's lightning, the belt, both hands, the rifle and the boots all readable; nothing below the soles.
VERSION A (zeri_design_A.png): TOTAL 40, WIDTH 30 (use the SECOND image 2_target_A).
VERSION B (zeri_design_B.png): TOTAL 42, WIDTH 32 (use the SECOND image 2_target_B); everything else as version A.
```

## 交回前自查

- [ ] 最高点到鞋底 A 40 格、B 42 格（最多 44）；A 不超过 30 格宽、B 不超过 32 格宽；鞋底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；刘海顶到下巴 9–10 格，发髻再高 4–5 格；
- [ ] 尖刺发髻 + 黄绿眼睛 + 创可贴；青蓝外套 + 银管；黄背心闪电；红棕皮带；深紫红裤 + 护膝；棕靴 + 橙袜口；竖举的步枪和握枪的手、垂下的手都看得见；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；用 design_tryndamere 的方法（自己的 24 色、keep_axis 整行整列删、脸不删、只补描边）删到目标，给用户看几个高度的选项。
- 通过后出动作帧包（第 2 步：idle run attack skill(W) skill2(E 冲刺) skill2_back ult hit dead）。手臂 + 步枪是一整块，只做 90° 整转 / 翻转；施法身体 = 待机身体。
