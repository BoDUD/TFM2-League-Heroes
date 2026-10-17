# 卡兹克：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 B（`khazix/1_picture.png`：最终形态——锯齿大镰爪、背上一对绿黄虫翼、青蓝背甲；身子压低半蹲、两腿一前一后大大分开、两只镰刀爪垂在身前）在**游戏尺寸**重新画。
> - **大小**：**版本 A** 从**背甲顶到脚底 40 格**，**版本 B** 44 格；触角可以再往上伸最多 5 格（橙线）。脚底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿线 = 背甲顶。姿势和位置照 `khazix/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是翅膀）。
> - **画窄一点（重要）**：原画的站姿很宽，缩到 40 格会有约 65 格宽（本包最宽的赵信 65 格，太宽了）。整个造型连翅膀、镰刀爪**不能超出两条紫线**：A 最宽 **56 格**，B 最宽 **60 格**。办法：**后腿（画面左边）收近一些**，两只脚爪的外沿相距不超过 A 34 格 / B 37 格；**前面（画面右边）那只镰刀爪往下收**、爪尖不超过前脚外 8 格；**翅膀画短**，翅尖只伸到背甲左边 8–10 格、往左上斜。
> - **干净、不要细节（最重要）**：最多 30 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。紫色甲壳容易糊成一片：**甲壳用亮一点的蓝紫，边上一格青蓝高光；软肉锈橙；镰刀刃口骨白是最亮的；眼睛黄白、红色下颚和护肩上的红斑点是亮点；翅膀浅黄绿（不透明平涂）加深绿翅脉**。去掉这个尺寸看不清的细节：护肩上的红斑点 = 2–3 个 2×2 的红圈白点；锯齿 = 刃口外 3–4 个 1 格的尖；翅脉 = 每片 2 道 1 格深绿线；脚爪 = 每只脚 2–3 个 1–2 格的棕爪尖。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，背甲顶到脚底只有 40（B 44）格**。
> - **头和脸**：昆虫的头，3/4 朝右，**一只发黄白光的眼睛**（2×2 亮黄白，外圈 1 格暗色）看得见，眼睛下面是**红色下颚、几颗 1 格的白牙**；头顶两根**细长的青蓝触角**向后上方翘（1 格宽，各 8–12 格长）；头后一圈棕色刺状颈饰。眼睛不能被挡住，**黄白色只用在眼睛上**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`khazix/6_size_guide.png` 是原画直接缩到 40 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 40 / 44 格时，把最接近的那一张也交来（不要超过 50 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（脸不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 30 色，描边只用一种近黑色。交付到 `outputs/khazix-model/`：`khazix_design_A.png`、`khazix_design_B.png`（1024×1024）和各自的原尺寸图 `khazix_design_A_1x.png`、`khazix_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来背甲顶到脚底是多少格、触角高出几格、整个造型多宽），最好再打成一个 zip（`khazix_design_pack.zip`）。

## 附图（都在压缩包的 `khazix/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 B | **长相和姿势**：紫色甲壳 + 青蓝高光、锈橙软肉、昆虫头 + 黄白眼睛 + 红下颚、两根青蓝触角、护肩红斑点、锯齿大镰爪、绿黄虫翼、青蓝背甲、反关节腿、棕色脚爪 |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到 A 的大小（背甲顶到脚底 40 格）的灰剪影（浅灰 = 翅膀）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 背甲顶，橙线 = 触角最高点，两条紫线 = 最宽的范围（56 格） | **A 的大小、姿势和位置照它**；剪影比紫线宽的部分要收进来 |
| `2_target_B.png` | 同上，B 的大小（44 格），紫线 = 60 格 | **B 的大小、姿势和位置照它** |
| `3_quality_bar.png` | 本包里的凯隐、赵信、伊芙琳、派克、牛头，游戏里现在的样子 ×8，同一条脚底线 | **像素大小和干净程度照它们**（派克也是半蹲） |
| `4_head.png` | 原画的头，放大 | 昆虫头、眼睛、红下颚和牙、触角根、头后的棕色颈饰 |
| `5_parts.png` | 原画的两只锯齿镰刀爪、护肩的红斑点、青蓝背甲、一片翅膀、一只脚，放大 | 镰刀爪、红斑点、背甲、翅膀、脚爪的形状 |
| `6_size_guide.png` | 原画直接缩到 A 的大小，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league_evolved.png` | 英雄联盟原版的这个形态（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：背甲顶到脚底 A 40 格、B 44 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画、宽度收窄**：3/4 正面朝右；身子压低半蹲；前腿（画面右边）在前、膝盖往后弯，后腿（画面左边）往后撑但比原画收近；两只镰刀爪垂在身前、爪尖朝下朝前，**两只都看得见、不藏在身体后面**；翅膀在背后往左上斜、比原画短；背甲盖住后背。
- **干净**：最多 30 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色：甲壳是更深的靛紫），**不要在描边里再画第二圈黑**；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0B0814 outline (the only near-black); violet carapace #2A1A5C #46309A #6A4ED0 #9478F0; blue-teal highlights, antennae and back shell #1A3E8A #2A78D0 #4EB8F0 #A0EAFF; rust flesh and neck frill #5A2410 #9A4A1E #CC7632; claw edges and teeth #C8A8A8 #F2DCD4 #FFF6F0; red jaw and shoulder spots #6A0A14 #C41E22 #F2503C; eyes #E6EE5A #FFFFC0 (eyes only); wings #5E6E1C #9CB83A #D2E47A #F2FAC0; toe claws #6A3010 #B4662A #E89A50.
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，镰刀爪也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`khazix_design_A.png` 和 `khazix_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`khazix/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Kha'Zix, a mantis-like insect predator from the Void, in his evolved form: PURPLE / INDIGO-VIOLET chitin with BLUE-TEAL lit edges; RUSTY ORANGE flesh at the joints, the belly and under the shoulders; an insect head with ONE GLOWING YELLOW-WHITE EYE seen in 3/4, a RED JAW with a few small white teeth, two long thin BLUE-TEAL ANTENNAE sweeping up and back, a brown spiky frill behind the head; big purple SHOULDER PLATES with RED-RINGED SPOTS; two big curved SCYTHE CLAWS with SERRATED BONE-WHITE edges; a pair of PALE YELLOW-GREEN INSECT WINGS with dark green veins on the back; a big BLUE-TEAL BACK SHELL; backward-bending insect legs with BROWN TOE CLAWS. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the wings in lighter grey - use it for his SIZE, his POSE and his PLACE in the canvas; it is TOO WIDE: everything must fit between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size and their crisp, clean look (the fourth is also crouched). FOURTH: the FIRST image's head, big - the eye, the red jaw and teeth, the antennae roots, the frill. FIFTH: the FIRST image's two serrated scythe claws, a shoulder plate with its red spots, the back shell, a wing and a foot, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this form - ONLY for how the body is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: only the TOTAL number of squares (the VERSION line) from the top of his back shell to his soles, the antennae at most 5 squares higher, and at most the WIDTH number of squares across (wings and claws included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose, NARROWER: crouched low in 3/4 FRONT view facing image right; the front leg (image right) forward, knee bent backward the insect way; the back leg (image left) braced behind but CLOSER than in the picture (the outer edges of the two feet no more than the FEET number of squares apart); both scythe claws held low in front of the body, points down and forward, both fully visible and never hidden behind the body; the front claw's point at most 8 squares beyond the front foot; the wings SHORTER than in the picture, angled up and back to image left, their tips only 8-10 squares left of the back shell; the head turned toward the viewer, the eye visible.
Game proportions: keep the picture's build - a big head and shoulders, thin waist, long thin legs; the eye, the red jaw, the red spots, the white serrated edges and the antennae drawn big enough to read.
Clean, not detailed (most important): at most 30 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines. Keep the materials apart: the brighter blue-violet carapace with a 1-square blue-teal lit edge, the rusty orange flesh, the bone-white serrated edges, the red jaw and spots, the pale yellow-green wings (opaque flat shades) with dark green veins, the blue-teal back shell, the brown toe claws. Drop what does not read at this size: the shoulder spots 2-3 red 2x2 rings with a white centre, the serrations 3-4 one-square points along each edge, the wing veins 2 one-square dark green lines a wing, the toe claws 2-3 small brown points a foot.
Palette (from the FIRST image, adjust if needed): #0B0814 outline (the only near-black); violet carapace #2A1A5C #46309A #6A4ED0 #9478F0; blue-teal highlights, antennae and back shell #1A3E8A #2A78D0 #4EB8F0 #A0EAFF; rust flesh and neck frill #5A2410 #9A4A1E #CC7632; claw edges and teeth #C8A8A8 #F2DCD4 #FFF6F0; red jaw and shoulder spots #6A0A14 #C41E22 #F2503C; eyes #E6EE5A #FFFFC0 (eyes only); wings #5E6E1C #9CB83A #D2E47A #F2FAC0; toe claws #6A3010 #B4662A #E89A50.
Face (most important detail), as the FOURTH image: the insect head in 3/4, ONE glowing eye of 2x2 yellow-white squares in a 1-square dark rim, the red jaw under it with 2-3 one-square white teeth, the antennae 1 square wide rising up and back from the top of the head. Nothing covers the eye. The yellow-white is used only by the eye.
Size and place: exactly where the SECOND image's grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the top of the back shell on the green line, the antennae at most up to the orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them): the scythes stay above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: TOTAL squares from the top of the back shell to the soles (compare with the SECOND image); the antennae at most 5 above; at most WIDTH squares across; all squares 8x8 on one grid; at most 30 colours; one outline colour; the glowing eye, the red jaw, the antennae, the red spots, both serrated claws, the wings, the back shell and the toe claws all readable; nothing below the soles.
VERSION A (khazix_design_A.png): TOTAL 40, WIDTH 56, FEET 34 (use the SECOND image 2_target_A).
VERSION B (khazix_design_B.png): TOTAL 44, WIDTH 60, FEET 37 (use the SECOND image 2_target_B); everything else as version A.
```

## 交回前自查

- [ ] 背甲顶到脚底 A 40 格、B 44 格（最多 50），触角最多再高 5 格；A 不超过 56 格宽、B 不超过 60 格宽；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 30 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；蓝紫甲壳、青蓝高光、锈橙软肉、骨白锯齿、红下颚和斑点、黄绿翅膀、青蓝背甲、棕色脚爪分得开；
- [ ] 发黄白光的眼睛 + 红下颚 + 白牙；两根触角；两只锯齿镰刀爪都看得见；翅膀比原画短；后腿收近；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时整行整列删到目标（脸、眼睛那几行几列不删），检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
