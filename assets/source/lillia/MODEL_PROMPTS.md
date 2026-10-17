# 莉莉娅：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`lillia/1_picture.png`：英雄联盟的待机，半人半鹿，四条鹿腿站着，两只手把紫色长枝条竖着抱在胸前，枝头金钩下吊着藤编灯笼、在头的右上方）在**游戏尺寸**重新画。
> - **大小**：两版都是**从枝条顶端（青蓝小花，她最高的地方）到蹄底 42 格**。**版本 A** = 枝条照原画的长度（花苞顶到蹄底约 34 格）；**版本 B** = **枝条短一截**：整根枝条连灯笼往下移，枝条顶端只比花苞高 4 格，人就能画大一些（花苞顶到蹄底约 38 格）。蹄底在第 99 行（y=792–799，红线），四只蹄子的中间在中间那一列（x=512，蓝线），绿线 = 枝条顶端，橙线 = 花苞顶。姿势和位置照 `lillia/2_target_A.png` / `2_target_B.png`（原画缩到这个大小的灰剪影，浅灰 = 枝条上段和灯笼；B 里它们已经往下移好了）。
> - **宽度**：A 约 30 格、B 约 34 格宽，**不要超过 36 格**。鹿身、尾巴、灯笼都不要往外伸。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。**鹿身是亮橙（背上 3–4 个 1–2 格的紫色斑点），肚皮、胸前的毛和尾巴是奶油白；头发是亮洋红 + 浅粉高光 + 深玫红阴影；皮肤是浅蜜桃色；叶子（耳边的叶卷、叶片上衣、手腕的叶子）是亮绿 2–3 档；花苞是蓝紫；眼睛是紫色；枝条是深紫（带一条亮紫高光）；枝头是金色的钩 + 一朵青蓝小花；灯笼是暖橙 / 金黄的圆球，外面几道深棕绿的藤条，下面一个金色小流苏；蹄子是亮蓝紫**。去掉这个尺寸看不清的细节：鹿毛的毛刺 = 只在胸前和腿弯留 2–3 个 1 格的小尖；灯笼的藤编 = 2–3 道深色竖线；耳边叶卷 = 一个 3×3 的绿色小卷。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，枝条顶到蹄底只有 42 格**。
> - **头和脸**：3/4 朝右、脸朝观众；**大大的紫色眼睛**（每只 2×2，左上一格亮白高光），小嘴 1 格，脸颊一格淡粉；头顶一个**蓝紫色的花苞**（约 4×3），两边耳朵旁各一个绿色叶卷；洋红长发从头顶披到背后、盖住鹿背的前半段。**脸不能被头发或枝条挡住，亮白只用在眼睛高光上**。
> - **枝条和手**：两只手（浅蜜桃色，各 2×2 左右）一上一下握着枝条，**手看得见**；枝条从她胸前斜着往上伸到头的右上方，顶端弯成金钩、开一朵青蓝小花；灯笼吊在钩下、在头的右边；枝条的下端到她鹿身前胸那里为止。
> - **四条腿**：细长的鹿腿，下半截深一点的橙红，**蹄子亮蓝紫**，四只都看得见、都踩在同一条蹄底线上；后腿在左、前腿在右，近侧的两条颜色亮一点、远侧的两条暗一点。
> - **直接按游戏尺寸画**，不要先画大再缩小。`lillia/6_size_guide.png` 是原画直接缩到 A 的大小的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 42 格时，把最接近的那一张也交来（不要超过 44 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/lillia-model/`：`lillia_design_A.png`、`lillia_design_B.png`（1024×1024）和各自的原尺寸图 `lillia_design_A_1x.png`、`lillia_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来枝条顶到蹄底、花苞顶到蹄底各是多少格、整个造型多宽），最好再打成一个 zip（`lillia_design_pack.zip`）。

## 附图（都在压缩包的 `lillia/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：洋红长发、蓝紫花苞、绿叶卷、紫色大眼睛、绿叶上衣、橙色鹿身 + 奶油白肚皮和尾巴、紫斑、四条鹿腿、蓝紫蹄子、深紫枝条 + 金钩 + 青蓝花 + 藤编灯笼 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（枝条顶到蹄底 42 格）的灰剪影（浅灰 = 枝条上段和灯笼）；红线 = 蹄底那一行的下沿，蓝线 = 四蹄中间，绿线 = 枝条顶，橙线 = 花苞顶 | **A 的大小、姿势和位置照它** |
| `2_target_B.png` | 同上，B：枝条连灯笼往下移，人画大（花苞顶到蹄底约 38 格） | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的萨勒芬妮、格温、雷克顿、卡兹克、图奇，游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们** |
| `4_head.png` | 原画的头，放大 | 花苞、叶卷、头发、眼睛、脸 |
| `5_parts.png` | 原画的枝条上段和灯笼、握枝条的两只手、尾巴和鹿背、四条腿和蹄子，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一蹄底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：枝条顶到蹄底 42 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画**：3/4 正面朝右；四条腿站着；两只手竖抱枝条在胸前；灯笼在头的右边；尾巴翘在身后（左）；**手、脸、枝条、灯笼都看得见**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#140808 outline (the only near-black); fawn #9A2A08 #D84A0A #FF7F00 #FFA840; belly, chest fur and tail #E8C890 #FFF0C8; spots #7A3CC8; hair #6E0A40 #B8075E #F00480 #FF6EB8; skin #D88C68 #F8C8A0 #FFE4CC; leaves #036A2E #3E8A2A #68A22C #B1DC43; bud #3A2C9A #5A5AE0 #9499FC; eyes #4A1AA0 #8A4AF0; bough #2A0838 #5A1078 #9A3AD8; gold hook and tassel #8A5A10 #E8A010 #FBD70B; blossom #1E5AE8 #56C8FE #ABF6FE; lantern #8A3A08 #FF7F00 #FFE16F, its strands #2E4A10 #5C3D04; hooves #2A2080 #4A45C8 #9499FC; highlight #FFFFFF (eyes only).
- **蹄底以下什么都不能有**（游戏在脚下画血条）：蹄底在第 99 行，下面一格都不能有，尾巴和灯笼也不能低于蹄底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`lillia_design_A.png` 和 `lillia_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`lillia/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy her look: Lillia, a shy FAWN CENTAUR: a timid girl from the waist up on the body of a young deer standing on FOUR slender legs: long MAGENTA HAIR, a BLUE-VIOLET FLOWER BUD on top of her head, a small GREEN LEAF CURL by each ear, big PURPLE EYES, pale peach skin, a top of GREEN LEAVES, leaves round the wrists; an ORANGE fawn body with a few PURPLE SPOTS on the back, a CREAM belly, chest fur and short fluffy tail, darker orange-red lower legs, BLUE-VIOLET HOOVES; a long DARK PURPLE BOUGH held upright in both hands in front of her chest, its top bent into a GOLD HOOK with a small CYAN-BLUE BLOSSOM, a round wicker DREAM LANTERN (warm orange-gold with dark woven strands and a small gold tassel) hanging from the hook beside her head. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the bough's top and the lantern in lighter grey - use it for her SIZE, her POSE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look. FOURTH: the FIRST image's head, big - the bud, the leaf curls, the hair, the eyes. FIFTH: the FIRST image's bough top with the lantern, the hands on the bough, the tail and back, the legs and hooves, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading.
Task: draw her as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only 42 squares from the top of the bough (the blossom, her highest point) to the bottom of the hooves, and at most 36 squares across. Each square is BIG compared with her body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose: standing on all four legs in 3/4 FRONT view facing image right, the girl's face and chest turned toward the viewer, the deer body pointing right, the hind legs at image left, the forelegs at image right, the near legs brighter, the far legs darker, all four hooves on one ground line; both hands gripping the bough one above the other in front of her chest, the bough rising diagonally up past the right side of her head to the gold hook, the lantern hanging from the hook at the right of her head; the tail sticking up behind (image left); the hair falling down her back over the front of the deer back. The hands, the face, the bough and the lantern fully visible, never hidden.
Game proportions: keep the picture's build - a big head with big eyes and the bud, a slim girl's body, a compact fawn body, slender legs; the eyes, the bud, the leaf curls, the hands, the hook with the blossom and the lantern drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no fur strokes, no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the bright orange fawn, the cream belly and tail, the bright magenta hair, the pale peach skin, the bright green leaves, the blue-violet bud and hooves, the purple eyes, the dark purple bough, the gold hook, the cyan blossom, the warm orange lantern. Drop what does not read at this size: the fur only 2-3 one-square points on the chest and behind the knees, the lantern's weave 2-3 dark lines, each leaf curl one 3x3 green curl, the spots 3-4 purple dots of 1-2 squares.
Palette (from the FIRST image, adjust if needed): #140808 outline (the only near-black); fawn #9A2A08 #D84A0A #FF7F00 #FFA840; belly, chest fur and tail #E8C890 #FFF0C8; spots #7A3CC8; hair #6E0A40 #B8075E #F00480 #FF6EB8; skin #D88C68 #F8C8A0 #FFE4CC; leaves #036A2E #3E8A2A #68A22C #B1DC43; bud #3A2C9A #5A5AE0 #9499FC; eyes #4A1AA0 #8A4AF0; bough #2A0838 #5A1078 #9A3AD8; gold #8A5A10 #E8A010 #FBD70B; blossom #1E5AE8 #56C8FE #ABF6FE; lantern #8A3A08 #FF7F00 #FFE16F, strands #2E4A10 #5C3D04; hooves #2A2080 #4A45C8 #9499FC; #FFFFFF eye highlights only.
Face (most important detail), as the FOURTH image: in 3/4 turned toward the viewer, two big PURPLE eyes of 2x2 squares each with a one-square white highlight at the top left, a one-square mouth, a pale pink square on the cheek, the blue-violet bud (about 4x3 squares) on top of the head, a green leaf curl at each side by the ears, the magenta hair framing the face. Nothing covers the face.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the hooves' lowest row at y=792-799 (square row 99, the red line), the middle of the four hooves on the middle column (x=512, the blue line), the top of the bough on the green line, the top of the bud on the orange line. Nothing below the hooves (the game draws the health bar right under them): the tail and the lantern stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 42 squares from the top of the bough to the hooves and the bud's top on the orange line (compare with the SECOND image); at most 36 squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the eyes, the bud, the leaf curls, both hands on the bough, the gold hook with the blossom, the lantern, the tail and four hooves all readable; nothing below the hooves.
VERSION A (lillia_design_A.png): the bough as long as in the picture (use the SECOND image 2_target_A): the bud's top about 34 squares above the hooves.
VERSION B (lillia_design_B.png): the bough SHORTER - its top only 4 squares above the bud, the lantern lower beside her head (use the SECOND image 2_target_B): the girl and the deer drawn bigger, the bud's top about 38 squares above the hooves; everything else as version A.
```

## 交回前自查

- [ ] 枝条顶到蹄底 42 格（最多 44）；A 花苞顶约 34 格、B 约 38 格；不超过 36 格宽；蹄底在第 99 行、四蹄中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；橙色鹿身、奶油白肚皮尾巴、洋红头发、蜜桃色皮肤、亮绿叶子、蓝紫花苞和蹄子、深紫枝条、金钩、青蓝花、暖橙灯笼分得开；
- [ ] 紫色大眼睛 + 白高光、花苞、两个叶卷；两只手握着枝条看得见；四条腿四只蹄子；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、蹄底线、眼睛，只补缺的描边。
- 先给用户看 Codex 自己整理好的 A、B，再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
