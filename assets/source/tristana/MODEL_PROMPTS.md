# 崔丝塔娜：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 B（`tristana/tristana_source.png`，你上一轮画的：炮身整根朝右）在**游戏尺寸**重新画。两版只差头顶护目镜筒的高度：
> - **版本 A**：比例照原画，两只护目镜筒约 **5 格**高；
> - **版本 B**：护目镜筒收矮到约 **3 格**，省下来的行数给脸和身体（脸、眼睛、手、腿更清楚）。
>
> 其余两版都一样：
> - **大小**：从护目镜筒顶到脚底约 **40 格**（护目镜算在内）。用户觉得 46–48 格的锐雯、薇恩、阿卡丽在游戏里太大，都缩到了 40 格；维迦的高帽子也算在 40 格里。大炮很长（从炮尾到炮口约 48–52 格），整根朝右，画面约 56 格宽。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；大小和位置看 `tristana/size_place.png`。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `tristana/quality_bar.png` 里 main 分支的英雄（都是你画、用户认可的）。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小会把细节弄碎）。`tristana/size_guide.png` 是原画直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 26 种。交付 `tristana_design_A.png`、`tristana_design_B.png`（1024×1024）和各自的原尺寸图 `tristana_design_A_1x.png`、`tristana_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板，最好打成一个 zip。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `tristana/tristana_source.png` | 用户选的原画 B | **长相**：护目镜、白发、大耳朵、琥珀色大眼睛、服装、大炮、姿势、颜色 |
| `tristana/quality_bar.png` | main 里 6 位英雄（提莫、维迦、金克丝、薇恩、娜美、阿卡丽），游戏尺寸 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `tristana/tfm2_style_ranged.png` | 团战经理2 原版的 6 个射手，×8 | 原版的像素画法、枪炮怎么画 |
| `tristana/size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 她的大小和位置（40 格高），红线 = 脚底线下沿，蓝线 = 中间列 | 只看大小和位置 |
| `tristana/size_guide.png` | 原画直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `tristana/eyes_guide.png` | 脸，游戏尺寸 ×12（带格线） | 脸和眼睛的画法 |

## 规则

- **像素尺寸（最重要）**：护目镜筒顶到脚底约 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：约德尔人：头大（护目镜顶到下巴约占总高的 40%），身子矮，腿短，半蹲、两脚分开站；耳朵很大，往两边伸；大炮和她差不多长，平端在腰间，整根朝右。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；每个小方块都在画东西（护目镜的镜片、铜箍上的 X 纹、炮口的八角边、皮带上的红色小包、腿上的菱格绑带），不要随手撒的杂点，不要抖动、渐变、噪点；最多 26 色。
- **材质**：淡紫皮肤（暗、中、亮 3 档）；白发（白、浅蓝灰、深一点的蓝灰 3 档）；耳朵里面粉色（2 档）；护目镜筒深红皮（2–3 档）+ 一道紫色细带 + 暗铜边 + 浅蓝镜片；橄榄绿背心和短裤（3 档）；棕色皮革（袖子、手套、绑腿、炮托，3–4 档）；红色（袖口、红包、握把，2–3 档）；大炮的青铜棕炮管（3–4 档，受光边）、两道暗铜色的箍（刻 X 纹）、钢蓝色的八角炮口和炮尾（4 档，亮高光）。
- **脸（最重要的细节）**：照 `eyes_guide.png`：两只眼睛都看得见、**一样大、在同一行**：每只 2 格宽 2 格高（上行一格白色高光 + 一格深色瞳孔，下行琥珀色），上面各一行深色睫毛；两眼之间 2 格皮肤，近处眼睛（画面左边，她朝右）前面留一列脸颊；琥珀色**只用在眼睛上**（护目镜和炮箍的铜色要更暗、更棕）；嘴是一道 2 格的深红色笑（在两眼中间下面两行）；脸颊、下巴不要别的深色格；白色刘海盖住额头，但不能盖住眼睛；大耳朵、手套、大炮都不能挡住脸。
- **手**：远侧的手（画面右边）握在炮身上面的钢把手上，手套至少 3×3 格；近侧的手（画面左边）在腰后握住炮尾；两只手都连着手臂（手臂加描边至少 3 格宽），不能是飘着的手。
- **大炮**：整根朝右，平端在腰间（炮身比脚高，炮尾也在脚底线以上）；从炮尾到炮口约和她一样长；炮口是一个明显的钢蓝八角喇叭口（至少 7 格高），炮身上两道铜箍；炮身、炮尾、炮口都要有暗、中、亮三档和高光，不能是一条平涂的棕带。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：两只脚底在同一行，就是第 99 行，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`tristana_design_A.png` 和 `tristana_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`tristana/tristana_source.png`、`tristana/size_place.png`、`tristana/quality_bar.png`、`tristana/eyes_guide.png`；`tristana/tfm2_style_ranged.png` 和 `tristana/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy her look: the goggles, the white hair, the huge ears, the amber eyes and grin, the clothes, the long cannon, the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for her size and her place in the canvas. THIRD: six other heroes of this game at game size, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: her face at game size, 12x, with a grid - copy the face and the eyes square for square. (Optional: official marksmen of the game at 8x for the pixel style and the guns, and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 40 pixels from the top of the goggle cups to the soles, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: a yordle - a big head (goggle top to chin about 40% of the height), huge ears, a short body, short legs apart in a slight crouch; the cannon about as long as she is tall, held level at her hip and pointing straight to the right; the goggle cups as tall as the VERSION lines at the end say (two images).
The character: Tristana, a small cheerful yordle gunner: lavender-violet skin; short fluffy WHITE hair shaded pale blue-grey with a side-swept fringe over the forehead and a fluffy mane behind; HUGE pointed ears sticking out sideways and a little up, lavender outside and PINK inside, a small dull brass ring on the near ear; on top of her head two tall CYLINDRICAL aviator goggle cups pushed up (crimson-red leather cups with a thin purple band, dull brass rims, pale blue glass facing up) joined by a brown strap across the forehead; big amber eyes and a confident grin; an olive-green sleeveless vest over a tan shirt with a brown shoulder strap; the near arm (image left) in a quilted brown leather sleeve with brass rings and a RED cuff, its hand holding the rear of the cannon at her hip; the far arm (image right) reaching forward, its hand in a big padded brown glove gripping a steel handle with a red grip on top of the cannon; a brown belt with small red pouches; olive shorts; quilted brown leather wraps on the lower legs; bare lavender yordle feet with dark claws; and her huge cannon held level at her hip, pointing straight to the RIGHT: a bronze-brown barrel with two dull-brass bands engraved with an X, a wide flared octagonal steel-blue muzzle at the right end, a steel-blue cap at the rear end (left), a brown leather-wrapped lower stock and a small steel frame on top.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 26 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks - black is only the outline, the lashes and the pupils; never a second black ring inside the outline); every square describes something (a goggle lens, the X on a brass band, the octagonal muzzle's edge, a red pouch, the diamond pattern of the leg wraps) - no random specks, no dithering, no gradients, no noise.
Colours: lavender skin in 3 shades; white hair in 3 (white, pale blue-grey, a deeper blue-grey); pink inner ears in 2; crimson goggle cups in 2-3 with a thin purple band, dull brass rims and pale blue glass; olive vest and shorts in 3; brown leather (sleeve, glove, leg wraps, stock) in 3-4; red (cuff, pouches, grip) in 2-3; the cannon's bronze-brown barrel in 3-4 with a lit edge, two dull-brass bands, a steel-blue octagonal muzzle and rear cap in 4 with bright highlights.
Face (most important detail), exactly as the FOURTH image: both eyes visible, the SAME size and on the SAME rows: each eye 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row amber - with a dark lash row over each eye; 2 squares of skin between the eyes and one cheek column before the near eye (image left, she faces right); the amber is used NOWHERE else (the goggles' and the bands' brass is darker and browner); a 2-square dark-red grin two rows under the eyes, between them; no other dark squares on the cheeks or the jaw; the white fringe covers the forehead but never the eyes; neither the ears, the glove nor the cannon covers the face.
Hands: the far hand (image right) in the padded glove on the steel handle on top of the cannon, the glove at least 3x3 squares; the near hand (image left) holding the rear of the cannon at her hip; both hands joined to arms at least 3 squares wide with the outline - no floating hands, no 1-square arms.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: both soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the middle between her feet on the middle column (x=512). The cannon's rear end stays above the soles. Nothing below the soles (the game draws the health bar right under the feet).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 40 squares from the top of the goggles to the soles; all squares 8x8 on one grid; at most 26 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both eyes the same size, level and clearly visible; the amber only in the eyes; the cannon long, level and pointing right with a clear octagonal muzzle; nothing below the soles.
VERSION A (tristana_design_A.png): the goggle cups as tall as in the FIRST image - about 5 squares from the top of the cups to the strap.
VERSION B (tristana_design_B.png): lower goggle cups - about 3 squares tall; the rows saved go to the face and the body (the face, the eyes, the hands and the legs clearer).
```

## 交回前自查

- [ ] 两版都是护目镜筒顶到脚底约 40 格（A 的镜筒约 5 格，B 约 3 格）；脚底最低一行在第 99 行，下面没有像素；两脚中间在 x=512；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块平涂；
- [ ] 两只眼睛一样大、一样高，各 2×2 带一行睫毛；琥珀色只在眼睛上；嘴是 2 格深红的笑；
- [ ] 大炮整根朝右、平端在腰间，炮口是清楚的钢蓝八角喇叭口，炮尾在脚底线以上；
- [ ] 远侧的手套握在炮身的钢把手上，近侧的手握炮尾；手都连着手臂；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛（一样大、一样高），只补缺的描边。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
