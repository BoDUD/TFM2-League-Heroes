# 诺提勒斯：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`nautilus/1_picture.png`：英雄联盟的待机，圆铜潜水头盔 + 黑色观察窗里两只红眼、锈铜胸甲肩甲 + 发光的海绿缝线、深灰黑潜水服、大手套、铜护膝、厚底潜水靴，灰色石铁大锚背在背上、锚冠和两只锚爪在头盔后上方拱起，近侧手握着垂下的粗铁链）在**游戏尺寸**重新画。A、B 只差**锚的大小和高度**。
> - **大小**：两版都是**从头盔顶到脚底 35 格**（他矮壮驼背，比包里其他坦克略矮，用户要求「注意模型不要过大」）。脚底在第 99 行（y=792–799，红线），两脚中间在中间那一列（x=512，蓝线），绿线 = 头盔顶。姿势和位置照 `nautilus/2_target_A.png` / `2_target_B.png`（原画直接缩到这个大小的灰剪影，浅灰的是锚）。**人不要超过 35 格高**。
> - **锚要画小、画低**：原画的锚缩下来会比头盔高 13–14 格，游戏里太高。**A：锚冠最多比头盔顶高 7 格（橙线）**，锚整体比原画小一点（约 0.7 倍），还是从远侧肩后斜上来、锚冠和两只锚爪在头盔后上方拱起；**B：锚更小（约 0.5 倍），最多比头盔顶高 3 格**，两只锚爪在头盔两侧后面（像一对弯角），锚杆斜在背后。两版都不能挡住观察窗和眼睛。
> - **宽度**：整个造型连锚和锁链**不能超出两条紫线**：**A 最宽 42 格，B 最宽 38 格**。
> - **头盔不要再放大**：原画的头盔（顶到护颌下沿）已经占身高约 4 成，按原画比例画（约 13–15 格高），**不要像别的英雄那样把头放大**。身体矮壮、肩很宽、腿短粗，像 `3_quality_bar.png` 里的阿利斯塔、布里茨那种厚重感。
> - **干净、不要细节（最重要）**：最多 32 色，每种材质 2–3 档平涂加一点高光，大块纯色，一圈近黑描边。**头盔和铠甲是锈铜（亮橙铜 / 铜褐 / 深棕）；潜水服是深灰黑；手套中灰；缝线是亮海绿；眼睛红橙；锚和锁链冷灰 + 一圈红箍 + 棕绳；锚冠上的花纹是一个浅米色的小记号**。深色部分之间一定要有亮边（不能糊成一团黑）。去掉这个尺寸看不清的细节：铜绿锈斑 = 最多两三个 1 格的青灰点；铆钉 = 每块甲 1–2 个 1 格亮点；头盔顶上的三个孔 = 三个 1 格黑点排成一列；锁链 = 一串 2×3 格的空心环（灰 + 暗灰），4–5 个；绳子 = 1 格宽的棕色线；靴子 = 每只 6–7 格宽的铜褐厚鞋底 + 1 格亮边。以前好几个英雄第一稿都画成了两倍大，**这次请画大方块，头盔顶到脚底只有 35 格**。
> - **头盔（就是他的脸）**：3/4 朝右，圆铜头盔，顶上三个小黑孔，前面一道**黑色观察窗**，里面**两只发红橙光的方眼睛（各 2×2 格左右，中间 1 格最亮）**，清楚看得见；观察窗下面一块方形铜护颌（3–4 道竖向的铜条）；头盔外面一圈锈红色的铜管兜帽（从头顶绕到背后）；没有脖子，头盔和胸甲连在一起。
> - **手和锁链**：近侧（画面左边那只）手握着锚杆下端（红箍下面），粗铁链从那只手垂下来到脚边；远侧手握拳在腰旁。**两只手都看得见**。
> - **直接按游戏尺寸画**，不要先画大再缩小。`nautilus/6_size_guide.png` 是原画直接缩到 35 格的样子，只用来看能放下什么，颜色和形状都是糊的，不要照它。
> - **画不到正好 35 格时，把最接近的那一张也交来（不要超过 40 格）**，生图原稿也全部交来，我按格子取回再整行整列删到目标（眼睛那几行几列不删）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 32 色，描边只用一种近黑色。交付到 `outputs/nautilus-model/`：`nautilus_design_A.png`、`nautilus_design_B.png`（1024×1024）和各自的原尺寸图 `nautilus_design_A_1x.png`、`nautilus_design_B_1x.png`，**生图原稿（raw/ 文件夹）**，色板，`HANDOFF.md`（**最后写**，写明每张读回来头盔顶到脚底是多少格、锚冠高出头盔几格、整个造型多宽），最好再打成一个 zip（`nautilus_design_pack.zip`）。

## 附图（都在压缩包的 `nautilus/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picture.png` | 用户选的原画 A | **长相和姿势**：圆铜头盔（三个孔、观察窗、红眼、护颌、铜管兜帽）、锈铜胸甲肩甲、海绿发光缝线、深灰黑潜水服、大手套、铜护臂护膝、厚底潜水靴、粗铁链、背在背上的灰色大锚（红箍、棕绳、锚冠花纹、两只弯钩锚爪） |
| `2_target_A.png` | 1024×1024 画布（128×128 格 ×8），原画缩到头盔顶到脚底 35 格的灰剪影（浅灰 = 锚）；红线 = 脚底那一行的下沿，蓝线 = 两脚中间，绿线 = 头盔顶，橙线 = 锚最高能到哪（+7 格），两条紫线 = 最宽的范围（42 格） | **A 的身体大小、姿势和位置照它；锚比剪影低、小，放进橙线和紫线以内** |
| `2_target_B.png` | 同一个剪影，橙线 = +3 格，紫线 = 38 格 | **B：身体同 A，锚约一半大，放进橙线和紫线以内** |
| `3_quality_bar.png` | 本包里的阿利斯塔、布里茨、蕾欧娜、慎、佛耶戈，游戏里现在的样子 ×8，同一条脚底线 | **像素大小、厚重感和干净程度照它们**（阿利斯塔、布里茨是同类坦克辅助，佛耶戈是最近通过的） |
| `4_head.png` | 原画的头盔，放大 | 三个孔、观察窗、红眼、护颌、铜管兜帽 |
| `5_parts.png` | 原画的锚冠和锚爪、近侧手 + 红箍 + 锁链、胸甲和肩甲、远侧手、两条腿和靴子，放大 | 这些部件的形状和颜色 |
| `6_size_guide.png` | 原画直接缩到 35 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `7_league.png` | 英雄联盟原版的待机（模型渲染） | 只看结构，**不要照它的 3D 光影** |

## 规则

- **像素尺寸（最重要）**：头盔顶到脚底 35 格（锚冠 A 最多再高 7 格、B 最多 3 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例和长相照原画**：3/4 正面朝右；矮壮驼背、身体前倾、两腿岔开，两脚踩在地面线上；锚背在背上；近侧手握锚杆下端、铁链垂下；远侧手握拳在腰旁；**观察窗里的两只红眼、两只手都看得见**。
- **干净**：最多 32 色；一圈 1 格的近黑描边（只用一种近黑），描边里每种材质 2–3 档平涂加一点高光（暗部带颜色），**不要在描边里再画第二圈黑**（观察窗本身是黑的，这是唯一的大块黑）；不要抖动、渐变、噪点，不要大块里夹单个异色方块。
- **色板**（从原画取，可以微调）：#0E0908 outline (the only near-black, also the viewing slit); bronze #48261A #7A3A1C #B25226 #D07031 #EFA654 (#EFA654 highlight only); hood pipe #622D17 #8B2E19; patina #6A9C98; suit #16161A #2B2C33 #3C4142 #555858; gloves #3C4142 #6B6F6C #909288; anchor and chain #303237 #4D5050 #6B6F6C #909288 #C4C6BC; emblem #F3DEB3; seams #1E8C78 #5ED3B6 #C0FFF0; eyes #8B1A10 #FF4020 #FFB060; red band #7A1A12 #D83A2A; rope #6D4D3A #967356 #C09060.
- **脚底以下什么都不能有**（游戏在脚下画血条）：脚底在第 99 行，下面一格都不能有，锁链也不能低于脚底。背景透明（做不到时用纯绿 `#00FF00`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`nautilus_design_A.png` 和 `nautilus_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`nautilus/` 里的 1、2（A 用 2_target_A，B 用 2_target_B）、3、4、5、6、7 号图，按顺序。

```text
Seven attached images. FIRST: the approved picture of this character (the user's pick) - copy his look: Nautilus, a silent, heavy giant in an ancient RUSTED BRONZE DIVING SUIT, NO FACE: a ROUND BRONZE DIVING HELMET fused with the chest (no neck) with THREE SMALL BLACK HOLES on top, a BLACK VIEWING SLIT with TWO GLOWING RED-ORANGE SQUARE EYES, a SQUARE BRONZE JAW GUARD below it and a rusty-red PIPE HOOD round the helmet; big RUSTED BRONZE CHEST AND SHOULDER PLATES with GLOWING SEA-GREEN SEAMS; DARK GREY-BLACK rubber suit arms and legs, BIG GREY GLOVES, bronze bracers and knee guards, HUGE DIVING BOOTS with thick bronze soles; a THICK GREY IRON CHAIN hanging from his near hand; a GREY STONE-IRON ANCHOR (a red band and brown rope on the shank, a pale emblem on the crown, two hooked flukes) CARRIED ON HIS BACK, its crown and flukes arching over the back of his helmet. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image shrunk to game size, the anchor in lighter grey - use it for his BODY'S SIZE, POSE and PLACE in the canvas; the anchor must be drawn SMALLER and LOWER than in that shape, everything below the orange line and between the two purple lines. THIRD: heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - match their pixel size, their heavy build and their crisp, clean look (the first two are tanks like him). FOURTH: the FIRST image's helmet, big - the holes, the slit, the red eyes, the jaw guard, the hood. FIFTH: the FIRST image's anchor crown, the near hand with the red band and the chain, the chest and shoulders, the far hand, the legs and boots, big. SIXTH: the FIRST image shrunk straight to game size on the same canvas - use it ONLY to see what fits where; it is blurry, do not copy its look. SEVENTH: the character's 3D model in this stance - ONLY for how the body is built, NOT its 3D shading.
Task: draw him as a SMALL game sprite - a low-resolution pixel-art character, shown enlarged 8x so every pixel is one crisp 8x8 square on a single 8-px grid: exactly 35 squares from the top of his helmet to his soles (the anchor may rise at most ANCHOR squares above the helmet), and at most the WIDTH number of squares across (anchor and chain included). Each square is BIG compared with his body. This is NOT an illustration: think of a sprite in a small pixel game, as in the THIRD image. Earlier drafts of other heroes came back two times too big because the image generator drew tiny squares - draw BIG squares.
Pose: the FIRST image's pose: hunched and leaning forward in 3/4 FRONT view facing image right, legs apart, both feet on the ground line; the anchor on his back, the shank slanting up behind his far shoulder, the crown and flukes behind and above the helmet; the NEAR hand (image left) holding the lower shank under the red band with the chain hanging down to his feet; the far hand a fist at his waist; the viewing slit turned toward the viewer, both red eyes visible; both hands visible.
Proportions: keep the FIRST image's proportions - the helmet (top to the jaw guard's bottom) about 13-15 squares, do NOT enlarge it; a very broad, stocky, hunched body on short thick legs, as heavy as the tanks in the THIRD image; the red eyes, the three holes, the sea-green seams, the chain links and the anchor's flukes drawn big enough to read.
Clean, not detailed (most important): at most 32 colours; every material 2-3 flat shades (light, mid, dark) plus a small highlight; big solid areas; no dithering, no gradients, no noise, no lone square of a different colour inside an area; ONE 1-square near-black outline around the whole silhouette (one near-black colour only) and very few inner dark lines; the viewing slit is the only big black area. Keep the dark parts apart with clear light edges - never one black blob: the rusty bronze helmet and plates (orange-copper light, copper-brown mid, dark brown shadow), the dark grey-black suit, the mid-grey gloves, the bright sea-green seams, the red-orange eyes, the cool grey anchor and chain with the red band and brown rope. Drop what does not read at this size: the patina = at most two or three 1-square blue-grey specks; the rivets = 1-2 light squares per plate; the three helmet holes = three 1-square black dots in a row; the chain = 4-5 hollow 2x3-square grey links; the rope = 1-square brown lines; each boot a 6-7-square-wide thick bronze sole with a 1-square light edge; the anchor's emblem one small pale mark.
Palette (from the FIRST image, adjust if needed): #0E0908 outline (the only near-black, also the viewing slit); bronze #48261A #7A3A1C #B25226 #D07031 #EFA654 (#EFA654 highlight only); hood pipe #622D17 #8B2E19; patina #6A9C98; suit #16161A #2B2C33 #3C4142 #555858; gloves #3C4142 #6B6F6C #909288; anchor and chain #303237 #4D5050 #6B6F6C #909288 #C4C6BC; emblem #F3DEB3; seams #1E8C78 #5ED3B6 #C0FFF0; eyes #8B1A10 #FF4020 #FFB060; red band #7A1A12 #D83A2A; rope #6D4D3A #967356 #C09060.
Helmet (most important detail), as the FOURTH image: round, in 3/4, three small black holes on top, a black viewing slit across the front with two glowing red-orange square eyes (about 2x2 squares each, the brightest square in the middle) clearly visible, a square bronze jaw guard of 3-4 vertical bronze bars below the slit, the rusty-red pipe hood round the helmet's top and back. Nothing covers the slit or the eyes.
Size and place: the body exactly where the SECOND image's darker grey shape stands, as tall as it: the soles' lowest row at y=792-799 (square row 99, the red line), the point between his feet on the middle column (x=512, the blue line), the helmet's top on the green line, the anchor no higher than the orange line, nothing outside the two purple lines. Nothing below the soles (the game draws the health bar right under them): the chain stays above them.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: 35 squares from the helmet's top to the soles (compare with the SECOND image); the anchor at most ANCHOR squares above the helmet; at most WIDTH squares across; all squares 8x8 on one grid; at most 32 colours; one outline colour; the helmet holes, the slit, the two red eyes, the jaw guard, the seams, both hands, the chain and the anchor's flukes all readable; nothing below the soles.
VERSION A (nautilus_design_A.png): ANCHOR 7, WIDTH 42 (use the SECOND image 2_target_A): the anchor about 0.7 times the FIRST image's size, its crown and flukes arching over the back of the helmet.
VERSION B (nautilus_design_B.png): ANCHOR 3, WIDTH 38 (use the SECOND image 2_target_B): the anchor about half the FIRST image's size, its two flukes standing behind both sides of the helmet like a pair of hooked horns, the shank slanting behind his far shoulder; everything else as version A.
```

## 交回前自查

- [ ] 头盔顶到脚底 35 格（最多 40）；锚冠 A 最多高出头盔 7 格、B 最多 3 格；A 不超过 42 格宽、B 不超过 38 格宽；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 32 色、描边只有一种近黑；
- [ ] 大块平涂、干净，和 `3_quality_bar.png` 一个像素大小；头盔按原画比例（约 13–15 格），没有放大；深色部分之间有亮边；
- [ ] 圆铜头盔 + 三个孔 + 黑色观察窗 + 两只红橙眼 + 方护颌 + 铜管兜帽；锈铜胸甲肩甲 + 海绿缝线；深灰黑潜水服、大手套、铜护膝、厚底靴；握锚杆的手和垂下的铁链；背上的灰色大锚（红箍、棕绳、两只锚爪）；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（`regrid.py`），一格对一个游戏像素，不缩小、不合并碎斑；太大时按 design_tryndamere 的办法（自己的 24 色、keep_axis 整行整列删、眼睛那几行几列不删、只补描边），检查色数、脚底线、眼睛。
- 先给用户看 Codex 自己整理好的 A、B，再附我按格子读回的版本；和包里的英雄放在一起（1× 和放大）给用户挑；通过后出动作帧包（第 2 步：idle run attack skill(Q 抛锚) skill2(W 护盾 + E 暗流) ult(R 深海冲击) hit dead）。锚和握锚的手是一整块部件，只平移和 90° 整转。
