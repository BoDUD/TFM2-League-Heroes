# 塔里克：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`taric/taric_source.png`，你上一轮画的：武器垂在身侧）在**游戏尺寸**重新画。两版只差头的大小：
> - **版本 A**：比例照原画，头（发顶到下巴）约占总高的**三分之一**（约 13 格）；
> - **版本 B**：头稍大一点，约 **15 格**，脸更清楚；省下来的行数从躯干和腿里扣（肩甲、腰带、前摆、靴子都要留着）。
>
> 其余两版都一样：
> - **大小**：从发顶到脚底约 **40 格**。用户觉得 46–48 格的锐雯、薇恩、阿卡丽在游戏里太大，都缩到了 40 格；塔里克肩甲宽、身材壮，但高度也按 40 格。脚底在第 99 行（y=792–799），大小和位置看 `taric/size_place.png`（原画缩到 40 格的剪影，约 28 格宽）。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `taric/quality_bar.png` 里 main 分支的英雄（盖伦、德莱厄斯、贾克斯、蕾欧娜、卢锡安、锐雯，都是你画、用户认可的）。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小的办法把细节全弄碎了）。`taric/size_guide.png` 是原画直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 26 种。交付 `taric_design_A.png`、`taric_design_B.png`（1024×1024）和各自的原尺寸图 `taric_design_A_1x.png`、`taric_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `taric/taric_source.png` | 用户选的原画 A | **长相**：头发、脸、衣服、肩甲、宝石、披风、斧锤、姿势、颜色 |
| `taric/quality_bar.png` | main 里 6 位英雄（盖伦、德莱厄斯、贾克斯、蕾欧娜、卢锡安、锐雯），游戏尺寸 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `taric/tfm2_style_warriors.png` | 团战经理2 原版战士 | 原版的像素画法 |
| `taric/size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（40 格高） | 只看大小和位置 |
| `taric/size_guide.png` | 原画直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：发顶到脚底约 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：结实的英雄 Q 版，照原画：肩甲把肩膀撑得很宽，胳膊粗短，腿短而结实，两脚分开；版本 A 头约三分之一（约 13 格），版本 B 约 15 格。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；每个小方块都在画东西（一缕头发、一道褶、一条边、一颗铆钉、宝石的一点高光），不要随手撒的杂点，不要抖动、渐变、噪点；最多 26 色。
- **材质**：棕红头发 4 档（几缕亮一点的发丝）；暖色皮肤 3 档；青蓝上衣 4 档（有受光边）；深棕皮革 3 档；银白金属（肩甲、护手、腰带、护腿、钢箍）4 档，高光要亮；宝石是深蓝宝石 / 紫蓝色，3 档饱和色，各有一格白色高光；深蓝紫披风和前摆 3–4 档；深紫裤子 3 档；灰绿靴子 3 档；斧锤的银紫刃 3 档，刃边一格亮色。
- **脸（最重要的细节）**：3/4 正面朝右。两只眼睛**一样大、一样高**，各 2 格宽：每只眼睛上面一行深棕色的眉毛，下面是眼白 + 蓝色瞳孔；两眼之间隔 2 格皮肤，远侧的眼睛和脸的远侧边缘之间留 1 列皮肤；眼睛的蓝是亮的天蓝色，**只用在眼睛上**（宝石是更深的蓝宝石色 / 紫蓝色）。嘴是 2 格深红棕色的一小道，闭着，在下巴上面一行，嘴角不要连到下颌线上；方下巴，下面一行下巴阴影。两缕前发在脸两边，不挡眼睛。
- **手臂**：近侧手臂（图里左边，深色袖子 + 银护手）和远侧光着的手臂都至少 3 格宽（加描边），和身体之间有描边隔开，不能是一条细线。
- **斧锤在近侧的手（图里左边），垂在身侧**（照原画）：握柄在拳头里，斧头（两片银紫刃包着紫蓝宝珠）在膝盖旁、刃尖朝左下；整把武器在脚底线以上结束。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：两只靴底在同一行，就是第 99 行，下面一格都不能有；披风下摆、武器都在这一行以上。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`taric_design_A.png` 和 `taric_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`taric/taric_source.png`、`taric/size_place.png`、`taric/quality_bar.png`；`taric/tfm2_style_warriors.png` 和 `taric/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the hair, the face with the two blue eyes, the tunic, the pauldrons, the belt, the cape, the mace-axe, the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas. THIRD: six other heroes of this game at game size, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. (Optional: official warriors of the game at 8x for the pixel style, and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 40 pixels from the top of the hair to the soles, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Sturdy heroic chibi like the FIRST image: broad shoulders made wider by the pauldrons, thick short arms, short sturdy legs, feet apart; the head's size as the VERSION lines at the end say (two images).
The character: Taric, a heroic gem knight: long auburn-brown hair parted in the middle, two front locks framing his face down to the jaw, the rest falling behind his shoulders; a handsome square-jawed face, thick dark brown brows, two bright blue eyes, a small confident smile, warm fair skin; a thin dark necklace with a small triangular sapphire at the throat; a teal-blue tunic wrapped diagonally across his chest with a deep V neck, a dark brown leather half-vest over his far shoulder; HUGE angular silver-white pauldrons on both shoulders, each set with a big round sapphire; the near arm (image left) in a dark brown sleeve with a silver gauntlet and a small sapphire at the elbow; the far arm (image right) bare and muscular, the hand open at his side; a heavy silver-grey belt with a round violet-blue gem buckle, a navy tabard panel with a silver rim hanging to his knees; dark plum trousers; grey-green armoured greaves and boots; a long navy-violet cape behind him. In the near hand (image left) a short crystal mace-axe hangs at his side: a dark wrapped grip in the fist, a steel collar, and a head of two curved lilac-silver blades round a glowing violet-blue orb, beside his knee, blades pointing down-left.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 26 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks - black is only the outline; never a second black ring inside the outline); every square describes something (a strand of hair, a fold, an edge, a rivet, a gem glint) - no random specks, no dithering, no gradients, no noise.
Colours: auburn-brown hair in 4 shades with a few lighter strands; warm fair skin in 3; teal-blue tunic in 4 with a lit edge; dark brown leather in 3; silver-white metal (pauldrons, gauntlet, belt plates, greave plates, the steel collar) in 4 with bright highlights; the gems deep sapphire / violet-blue in 3 saturated shades with one white glint square each; navy-violet cape and tabard in 3-4; dark plum trousers in 3; grey-green boots in 3; the mace's lilac-silver blades in 3 with a bright edge.
Face (most important detail): 3/4 front facing right. Both eyes the SAME size and on the SAME rows, each 2 squares wide: a dark brown brow square row above each eye, then white + blue iris; 2 skin squares between the eyes and one skin column between the far eye and the far cheek edge; the eye blue is a bright sky blue used ONLY in the eyes (the gems are a deeper sapphire / violet). A small closed mouth - 2 squares of dark warm red-brown - one row above the chin, the mouth corners never joined to the jaw line; a square jaw with one row of chin shade. The front locks frame the face on both sides without covering the eyes.
Arms: the near arm (image left, dark sleeve + silver gauntlet) and the bare far arm each at least 3 squares wide with the outline, separated from the body by the outline, never 1-square lines.
The mace-axe in the near hand (image left), hanging at his side as in the FIRST image: grip in the fist, the head of two lilac-silver blades round the violet-blue orb beside his knee, pointing down-left; the whole weapon ends ABOVE the soles.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: both soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image). Nothing below the soles (the game draws the health bar right under the feet): the weapon, the cape hem and everything else end at or above that row.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 40 squares from the top of the hair to the soles; all squares 8x8 on one grid; at most 26 colours; one outline ring only; the detail and shading of the THIRD image, not flat dark areas; both eyes the same size, level and clearly visible; the eye blue only in the eyes; the weapon and the cape above the soles.
VERSION A (taric_design_A.png): the head as in the FIRST image - from the top of the hair to the chin about one third of the height (about 13 squares).
VERSION B (taric_design_B.png): a slightly bigger head for a clearer face - about 15 squares from the top of the hair to the chin; the rows saved come out of the torso and the legs (keep the pauldrons, the belt, the tabard and the boots).
```

## 交回前自查

- [ ] 两版都是发顶到脚底约 40 格（A 的头约 13 格，B 约 15 格）；脚底最低一行在第 99 行，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块平涂；
- [ ] 两只蓝眼睛一样大、一样高、看得清；眼睛的天蓝只在眼睛上；嘴是 2 格一小道，嘴角没连到下颌；
- [ ] 两边肩甲各有一颗蓝宝石；腰带圆扣是紫蓝宝石；斧锤在左手、垂在身侧、在脚底以上；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（skill 的 `scripts/regrid.py`），不缩小、不合并碎斑；检查色数、脚底线、眼睛（一样大、一样高），补描边（`strips.complete_outline`）。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；超过 40 行时给出按整行整列删减到 40 行的版本（不穿过脸）；通过后出动作帧包（第 2 步）。
