# 萨科：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原图 A（`shaco/shaco_source.png`，你上一轮画的，红色一半在前）在**游戏尺寸**重新画。两版只差头（面具）的大小：
> - **版本 A**：面具（帽檐到下巴尖）约 **8 格**高，帽子的两只角约 7 格，身体约 25 格；
> - **版本 B**：面具约 **10 格**高（更 Q 版，笑容和眼睛更大更清楚），帽子的角约 6 格，身体约 24 格。
> 原图里面具只占身高的约 13%，直接照比例缩到 40 格只有 5 格高，眼睛和笑容会糊成一团，所以两版的面具都要比原图大。
>
> 其余两版都一样：
> - **大小**：从帽子最高点（角尖或铃铛）到脚底约 **40 格**（帽子算在内）。用户觉得 46–48 格的锐雯、薇恩、阿卡丽在游戏里太大，都缩到了 40 格。脚底在第 99 行（y=792–799），大小和位置看 `shaco/size_place.png`。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `shaco/quality_bar.png` 里 main 分支的英雄（都是你画、用户认可的，同样 40 格高）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`shaco/size_guide.png` 是原图直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 28 种。交付 `shaco_design_A.png`、`shaco_design_B.png`（1024×1024）和各自的原尺寸图 `shaco_design_A_1x.png`、`shaco_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `shaco/shaco_source.png` | 用户选的原图 A | **长相**：面具、帽子、领圈、肩甲、外套、灯笼裤、靴子、匕首、姿势、颜色 |
| `shaco/face_ref.png` | 原图 A 的头部（放大 2 倍） | 面具、眼睛、笑容、帽子的形状 |
| `shaco/quality_bar.png` | main 里 6 位英雄（阿卡丽、锐雯、薇恩、维迦、塔里克、贾克斯），游戏尺寸 ×8，同一条脚底线，都是 40 格左右 | **质量标准**：像素大小、细节、明暗 |
| `shaco/tfm2_style_martial.png` | 团战经理2 原版的武者/刺客（有拿匕首的忍者），×8 | 原版的像素画法、匕首怎么画 |
| `shaco/size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（40 格高） | 只看大小和位置 |
| `shaco/size_guide.png` | 原图直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：帽子最高点到脚底约 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：版本 A 面具约 8 格、版本 B 约 10 格（帽檐到下巴尖）；两版的帽角都在面具上方，深蓝角向后（图左）弯垂、红角向上再向右弯，角尖各挂一个金色菱形铃铛（2×2 或 3×3 格）；身体瘦长，灯笼裤和带刺的靴子要大而清楚。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；每个小方块都在画东西（一颗金扣、一道褶、一根刺、一条边），不要随手撒的杂点，不要抖动、渐变、噪点；最多 28 色。
- **材质**：红色（帽角、外套前片、袖口泡泡、鞋，4 档，亮红受光边）；深蓝（帽角、外套侧片、上臂、靴子，4 档）；金色（铃铛、领圈、扣子、腰带、肩甲边、护腕箍，3–4 档，一点亮黄高光）；银色金属（肩甲、刺、护胫、匕首刃，4 档，亮白高光）；面具白（白、淡紫灰、紫灰阴影 3 档）；手是淡蓝灰（2–3 档）；灯笼裤是黑白格。
- **面具（最重要的细节）**：
  - 两只冰蓝色眼睛**一样大、一样高**：每只眼睛 2 格宽，在深蓝的眼窝里，眼窝朝鼻子一侧往下斜（凶）；每只眼睛有一格更亮的青白色亮芯；两只眼睛之间隔 1–2 格白色面具；**冰蓝色只用在眼睛上**。
  - **大笑**：眼睛下面横贯面具的一排白牙，至少 4 颗牙，牙与牙之间用深色隔开，上下是深色的嘴线，嘴角往上翘；笑容是萨科最重要的特征，缩小后也要看得出是咧嘴笑。
  - 长鼻子像鸟嘴：从两眼之间往右下方伸出、压在笑容上方，1–2 格宽、3–4 格长，白色带一格阴影；下巴窄而尖。
  - 帽子像兜帽一样框住面具：近侧（图左）深蓝、远侧（图右）红；帽子、肩甲和匕首都不能挡住眼睛和笑容。
- **灯笼裤的黑白格**：用 2×2 格一块的大格子（黑和淡灰白交替，暗面的白格稍灰），不要 1 格一块的碎格（缩小后会变成噪点）。
- **匕首**：近侧手（图左）的匕首在胯部高度水平朝后（图左），刃 4–5 格长，一侧边缘锯齿（亮白和银灰交替），金色护手 1 格，握把深色；远侧手（图右）的匕首朝下，刃 3–4 格；两把刀都要连在手里，不能飘在空中。
- **手臂**：上臂深蓝 + 金箍，前臂是很大的红色泡泡袖口（至少 4 格宽），手淡蓝灰，至少 2 格宽加描边，不能是一条细线。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：两只鞋底在同一行，就是第 99 行，下面一格都不能有；翘起的鞋尖在脚底线以上。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`shaco_design_A.png` 和 `shaco_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`shaco/shaco_source.png`、`shaco/size_place.png`、`shaco/quality_bar.png`、`shaco/face_ref.png`；`shaco/tfm2_style_martial.png` 和 `shaco/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the mask, the hat, the collar, the pauldrons, the jacket, the pantaloons, the boots, the daggers, the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas. THIRD: six other heroes of this game at game size, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head enlarged - the mask, the eyes, the grin and the hat to keep. (Optional: official fighters of the game at 8x for the pixel style and the daggers, and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 40 pixels from the highest point of the hat (a horn tip or a bell) to the soles, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. The mask is BIGGER than in the FIRST image (there it is only about 13% of his height, which would be 5 squares here - too small to read): its size is given by the VERSION lines at the end (two images).
The character: Shaco, a lanky menacing jester: a white porcelain MASK (white, pale lavender-grey and lavender shadow) with a long hooked nose-beak pointing down to the image right and a narrow pointed chin; two narrow slanted glowing ICE-CYAN eyes inside dark navy sockets; a HUGE grin under the eyes showing a row of white teeth; a two-horned jester hat that frames the mask like a hood, navy on the near side (image left) and crimson red on the far side (image right): the NAVY horn curls back and down to the image left ending in a GOLD diamond bell, the RED horn stands up and bends to the image right ending in a GOLD diamond bell; a jagged GOLD ruff collar under the chin; two SILVER-STEEL pauldrons with gold rims, a gold stud and one sharp silver spike pointing up each; a crimson red jacket front with a navy far side, gold diamond buttons down the middle and a gold belt with a diamond buckle, its red and navy tails hanging to mid-thigh in jagged points with tiny gold bells; navy upper arms with gold bands and BIG puffy crimson forearm cuffs; pale blue-grey hands; very puffy knee-length pantaloons in a black-and-white CHECKERBOARD; dark navy-charcoal boots with silver spiked shin guards (a spike out to each side) and gold rims; pointed crimson jester shoes whose toes curl up; one dagger in EACH hand - a silver blade with a serrated (zig-zag) edge, a gold cross-guard and a dark grip: the near hand's (image left) dagger points straight back to the image left at hip height, the far hand's (image right) dagger points down.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 28 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks - black is only the outline, the gaps between the teeth and the mouth line; never a second black ring inside the outline); every square describes something (a gold button, a fold, a spike, an edge) - no random specks, no dithering, no gradients, no noise.
Colours: crimson red (hat horn, jacket front, puffy cuffs, shoes) in 4 shades with a lit edge; dark navy (hat horn, jacket side, upper arms, boots) in 4; gold (bells, collar, buttons, belt, rims, bands) in 3-4 with a bright yellow highlight; silver steel (pauldrons, spikes, shin guards, blades) in 4 with white highlights; the mask white, pale lavender-grey and lavender shadow; pale blue-grey hands; the pantaloons black and pale grey-white.
Mask (most important detail): two ICE-CYAN eyes of the SAME size on the SAME rows, each 2 squares wide inside a dark navy socket slanting down toward the nose (menacing), each with one brighter cyan-white core square, 1-2 white squares between them; the cyan is used nowhere else. Under them a HUGE GRIN across the mask: one row of white teeth, at least 4 teeth with dark gaps between them, a dark mouth line above and below, the corners turned up - the grin must still read as a grin at 1x. A long white hooked nose like a beak from between the eyes down to the image right over the grin, 1-2 squares wide and 3-4 long; a narrow pointed chin. The hat frames the mask like a hood (navy on the image left, red on the image right); nothing covers the eyes or the grin.
Pantaloons: the checkerboard in BIG 2x2-square checks (black and pale grey-white, the white checks a little greyer in the shadow) - never 1-square checks, they turn into noise. Daggers: the near hand's (image left) blade horizontal at hip height pointing straight back to the image left, 4-5 squares long with a zig-zag (serrated) edge in white and silver, a 1-square gold guard and a dark grip; the far hand's (image right) blade pointing down, 3-4 squares; both held in the hands. Arms: navy upper arms with gold bands, BIG puffy crimson forearm cuffs (at least 4 squares wide), pale blue-grey hands at least 2 squares wide with the outline - never a thin line.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: both soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image). The curled shoe tips stay above that row. Nothing below the soles (the game draws the health bar right under the feet).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 40 squares from the top of the hat to the soles; all squares 8x8 on one grid; at most 28 colours; one outline ring only; the detail and shading of the THIRD image, not flat dark areas; both eyes the same size, level and clearly visible; the cyan only in the eyes; the grin readable; 2x2 checks on the pantaloons; two daggers held in the hands; nothing below the soles.
VERSION A (shaco_design_A.png): the mask from the cap band to the tip of the chin about 8 squares tall, the hat horns with their bells about 7 squares above it, the body about 25 squares.
VERSION B (shaco_design_B.png): a bigger, more chibi mask - about 10 squares from the cap band to the tip of the chin (bigger eyes and a bigger grin), the hat horns about 6 squares above it, the body about 24 squares.
```

## 交回前自查

- [ ] 两版都是帽子最高点到脚底约 40 格（A 面具约 8 格，B 约 10 格）；脚底最低一行在第 99 行，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块平涂；
- [ ] 两只冰蓝眼睛一样大、一样高、各有一格亮芯；冰蓝只在眼睛上；咧嘴笑的一排白牙看得出来；鸟嘴鼻往右下；
- [ ] 帽子：深蓝角向后弯垂、红角向上，两个金铃铛；金领圈、银肩甲带刺；
- [ ] 灯笼裤是 2×2 的大黑白格；两把匕首拿在手里，近侧朝后、远侧朝下；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛（一样大、一样高）、笑容，补齐描边（`strips.complete_outline`）。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
