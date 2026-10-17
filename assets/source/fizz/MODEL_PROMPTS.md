# 菲兹：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`fizz/fizz_source.png`，你上一轮画的：两手横握三叉戟，叉头朝右）在**游戏尺寸**重新画。两版只差头和眼睛：
> - **版本 A**：比例照原画，头（耳鳍顶到下巴）约 **13 格**；近处的眼睛（画面左边）3 格宽，远处的眼睛 2 格宽（在头的远边，被头的弧度挡住一点）；
> - **版本 B**：头画大一点，约 **15 格**，身体相应短一点；**两只眼睛都 3 格宽、一样大**（头稍微再转向正面一点）。
>
> 其余两版都一样：
> - **大小**：从耳鳍顶到脚底约 **34 格**（和崔丝塔娜一样，约德尔人大小；耳鳍算在内）。三叉戟比他还长（从杆尾鳍穗到叉尖约 54–58 格），横在腰间，叉头朝右。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；大小和位置看 `fizz/size_place.png`。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `fizz/quality_bar.png` 里 main 分支的小个子英雄（都是你画、用户认可的）。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小会把细节弄碎）。`fizz/size_guide.png` 是原画直接缩到 34 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 24 种。交付 `fizz_design_A.png`、`fizz_design_B.png`（1024×1024）和各自的原尺寸图 `fizz_design_A_1x.png`、`fizz_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板，最好打成一个 zip（`fizz_design_pack.zip`，放在 outputs 里）。

## 附图（都在压缩包的 `fizz/` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `fizz_source.png` / `fizz_source_white.png` | 用户选的原画 A（透明底 / 白底） | **长相**：大圆头、两片下垂的长耳鳍（内侧橙红褶边）、绿色大眼睛、坏笑、浅蓝斑点、奶黄肚皮、橙色鳍、蹼足、三叉戟、姿势、颜色 |
| `size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（34 格高），红线 = 脚底线下沿，蓝线 = 中间列 | 只看大小和位置 |
| `quality_bar.png` | main 里 5 位小个子英雄（崔丝塔娜 34 格、提莫、维迦、艾克、安妮），游戏尺寸 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `face_ref.png` | 原画 A 的头，放大（685×414） | 脸、眼睛、耳鳍的样子 |
| `tfm2_style_pole.png` | 团战经理2 原版拿长柄武器的英雄（枪兵、棍女、鱼叉手、忍者、鬼怪），×8 | 原版的像素画法、长杆在这个尺寸怎么画（枪兵把枪平端在腰间，和菲兹一样） |
| `size_guide.png` | 原画直接缩到 34 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：耳鳍顶到脚底约 34 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：小个子两栖约德尔人：头大圆、身子细短、腿短微蹲、两脚分开站，蹼足又大又扁；两片长耳鳍从头顶垂到肩膀以下；三叉戟比他还长，两手横握在肚子前面、腰的高度，叉头朝右。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；每个小方块都在画东西（头顶的浅色斑点、耳鳍的橙色褶边、脚趾、杆上的钢箍、叉齿的钢边、蓝宝石），不要随手撒的杂点，不要抖动、渐变、噪点；最多 24 色。
- **材质**：天蓝皮肤 3–4 档（耳鳍也是）+ 小腿和脚的深海军蓝 2 档；奶黄肚皮 2 档；橙红鳍 2–3 档；眼白、亮绿、黑；深红杆 2–3 档；浅钢色 2–3 档；叉头的翠绿 2–3 档（比眼睛的绿更暗、更偏蓝）；亮蓝宝石；金色（尾巴环、鳍穗）2 档。
- **脸（最重要的细节）**：照 `face_ref.png`：两只眼睛都看得见、**在同一行**，每只是一行厚厚的蓝色上眼皮，下面两行眼睛：眼白、亮绿虹膜、朝右的黑瞳孔（可以有一格白色高光）；眼睛的宽度按两版各自的要求；两眼之间 1–2 格蓝皮肤；**亮绿只用在眼睛上**（三叉戟的翠绿要更暗、更偏蓝）；嘴是一道细细的深色坏笑，约 3 格宽，在眼睛下面两行的吻部上；脸颊、下巴不要别的深色格；耳鳍框住脸，但不能盖住眼睛；手和三叉戟都不能挡住脸。
- **手**：两只小手都握在肚子前面的杆上，相隔 4–6 格，每只至少 2×2 格，连着手臂（手臂加描边至少 3 格宽），不能是飘着的手、1 格细的手臂。
- **三叉戟**：整根横在腰间（膝盖以上），叉头朝右；杆是 1 格粗的深红色，上下各一格描边（一共 3 行，和原版枪兵的枪一样），中间不断；叉头至少 7 格高、6 格长，三根叉齿清楚（中间最长、笔直，两边向前弯成钩）；左端的鳍穗约 4 格；整根都在脚底线以上。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：两只脚底在同一行，就是第 99 行，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`fizz_design_A.png` 和 `fizz_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`fizz/fizz_source.png`、`fizz/size_place.png`、`fizz/quality_bar.png`、`fizz/face_ref.png`；`fizz/tfm2_style_pole.png` 和 `fizz/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the big round head with two long drooping fin-ears, the big green eyes and the sly grin, the blue skin with pale spots, the cream belly, the orange fins, the webbed feet, the long trident, the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas. THIRD: five other small heroes of this game at game size, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head, big - the face, the eyes and the fin-ears to copy. (Optional: official heroes of the game with spears and staffs at 8x for the pixel style and how a long pole is drawn at this size - the spearman holds his spear level at the waist like this character; and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 34 pixels from the top of the fin-ears to the soles, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: a small yordle-sized amphibian - a big round head, a short slim body, short bent legs apart, big flat webbed feet; the trident longer than he is tall, held level across his waist with both hands and pointing straight to the RIGHT; the head as tall as the VERSION lines at the end say (two images).
The character: Fizz, a small mischievous amphibious trickster: smooth sky-blue/cyan skin with a few pale spots on the crown; a big round head with a short rounded snout, no nose, no hair; two long blue FIN-EARS hanging from the top of the head down past the shoulders, one on each side, their inner edges lined with ORANGE-RED frills, and two more blue fin-lobes falling behind his back; two BIG round eyes with heavy blue upper lids, white eyeballs, bright GREEN irises and black pupils, looking to the right; a thin sly grin; a pale CREAM-YELLOW throat and belly; thin arms, small three-fingered hands, small orange spines at the elbows; legs darkening to deep NAVY-BLUE from the knees down; big flat webbed navy feet with long splayed toes; a short tail low behind him with a small GOLD ring; and his TRIDENT held level across his waist with BOTH hands in front of his belly, pointing straight to the RIGHT: a dark CRIMSON-RED shaft with two or three pale steel bands, at the right end a JADE-GREEN trident head with three prongs (the middle one longest and straight, the two outer ones curving forward like hooks), pale steel edges and a small bright BLUE gem where the prongs meet the shaft, and at the left end a fan-shaped tuft of green and gold fins.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 24 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks - black is only the outline and the pupils; never a second black ring inside the outline); every square describes something (a spot on the crown, a frill of the fin-ear, a toe, a steel band on the shaft, a prong's steel edge, the blue gem) - no random specks, no dithering, no gradients, no noise.
Colours: sky-blue skin in 3-4 shades (the fin-ears included) and the navy legs and feet in 2; cream belly in 2; orange-red fins in 2-3; the eyes' white, bright green and black; crimson shaft in 2-3; pale steel in 2-3; the trident head's jade in 2-3 (a darker blue-green than the eyes' green); a bright blue gem; gold (the tail ring, the tuft) in 2.
Face (most important detail), as the FOURTH image: both eyes visible and on the SAME rows, each a heavy blue lid row over two rows of eye - white eyeball, a bright green iris and a black pupil toward the right (one white highlight square is welcome); the eyes as wide as the VERSION lines say; one or two squares of blue skin between the eyes; the bright green is used NOWHERE else (the trident's jade is darker and bluer); a thin dark sly grin two rows under the eyes, about 3 squares wide, on the snout; no other dark squares on the cheeks or the jaw; the fin-ears frame the face but never cover the eyes; neither the hands nor the trident cover the face.
Hands: both small hands on the shaft in front of his belly, about 4-6 squares apart, each at least 2x2 squares and joined to an arm at least 3 squares wide with the outline - no floating hands, no 1-square arms.
Trident: level at his waist (above his knees), pointing straight to the right; the shaft one square of crimson thick with the outline above and below it (three rows in all, like the official spearman's spear), unbroken; the trident head at least 7 squares tall and 6 long with three clear prongs; the fin tuft at the left end about 4 squares; the whole trident above the soles.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: both soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the middle between his feet on the middle column (x=512). Nothing below the soles (the game draws the health bar right under the feet).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 34 squares from the top of the fin-ears to the soles; all squares 8x8 on one grid; at most 24 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both eyes level and clearly visible; the bright green only in the eyes; the trident long, level and pointing right with three clear prongs; nothing below the soles.
VERSION A (fizz_design_A.png): the FIRST image's proportions - the head (top of the fin-ears to the chin) about 13 squares tall; the near eye (image left) 3 squares wide, the far eye 2 squares wide (it sits at the far edge of the head, partly behind the curve of the head).
VERSION B (fizz_design_B.png): a bigger head so the face reads at this small size - the head (top of the fin-ears to the chin) about 15 squares tall, the body a little shorter; BOTH eyes 3 squares wide, the same size (the head turned a little more toward the viewer so both fit).
```

## 交回前自查

- [ ] 两版都是耳鳍顶到脚底约 34 格（A 头约 13 格，B 约 15 格）；脚底最低一行在第 99 行，下面没有像素；两脚中间在 x=512；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 24 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块平涂；
- [ ] 两只眼睛在同一行、看得清（A：近 3 格远 2 格；B：两只都 3 格）；亮绿只在眼睛上；坏笑在眼睛下面两行；
- [ ] 三叉戟横在腰间、叉头朝右、三根叉齿清楚，杆是 1 格深红加上下描边、不断；整根在脚底线以上；
- [ ] 两只手都握在杆上、连着手臂；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
