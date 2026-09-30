# 维迦：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`veigar/veigar_source.png`，你上一轮画的）在**游戏尺寸**重新画。两版只差帽子的大小：
> - **版本 A**：比例照原画，帽子（帽檐到最高点）约占总高的 **44%**（约 17–18 格）；
> - **版本 B**：帽子收小到约 **三分之一**（约 13–14 格），帽尖照样向后弯垂，省下来的行数给身体（长袍、铁手套、腿更清楚）。
>
> 其余两版都一样：
> - **大小**：从帽子最高点到脚底约 **40 格**（帽子算在内；帽尖向后、向左垂下，不往上长）。用户觉得 46–48 格的锐雯、薇恩、阿卡丽在游戏里太大，都缩到了 40 格，维迦的尖帽子很高，所以帽子也要算进这 40 格。脚底在第 99 行（y=792–799），大小和位置看 `veigar/size_place.png`。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `veigar/quality_bar.png` 里 main 分支的英雄（都是你画、用户认可的）。
> - **直接按游戏尺寸画**，不要先画大再缩小（上一次缩小的办法把细节全弄碎了）。`veigar/size_guide.png` 是原画直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 26 种。交付 `veigar_design_A.png`、`veigar_design_B.png`（1024×1024）和各自的原尺寸图 `veigar_design_A_1x.png`、`veigar_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `veigar/veigar_source.png` | 用户选的原画 A | **长相**：帽子、黑脸黄眼、长袍、铁手套、法杖、姿势、颜色 |
| `veigar/quality_bar.png` | main 里 6 位英雄（安妮、提莫、拉克丝、莫甘娜、阿卡丽、娜美），游戏尺寸 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `veigar/tfm2_style_mages.png` | 团战经理2 原版法师（持杖的、戴高帽的），×8 | 原版的像素画法、法杖怎么画 |
| `veigar/size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（40 格高） | 只看大小和位置 |
| `veigar/size_guide.png` | 原画直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |
| `veigar/eyes_guide.png` | 帽檐下的脸，游戏尺寸 ×12（带格线） | 脸和眼睛的画法 |

## 规则

- **像素尺寸（最重要）**：帽子最高点到脚底约 40 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：版本 A 帽子约占 44%（照原画），版本 B 约占三分之一；两版的帽尖都向后弯、垂在左边，不往上长；帽檐下是黑脸；身体是矮胖的约德尔人，长袍下摆宽，腿短。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色），**不要在描边里再画第二圈黑**；每个小方块都在画东西（帽带的一个铆钉、一道褶、一条边），不要随手撒的杂点，不要抖动、渐变、噪点；最多 26 色。
- **材质**：蓝紫色帽子和长袍（暗、中、亮、受光边 4 档），帽尖渐成紫色（2 档）；银色金属（帽带、铆钉、领口、护肩、护腕、下摆的银边和尖刺、靴子，4 档，亮的高光）；棕色皮带（3 档）；品红色的挂布（3 档）；深灰色的腿；法杖是灰色金属杆 + 银色双叉刃，中间一颗**橙色**的水晶（2–3 档，偏橙，不能和眼睛的黄一样）。
- **脸（最重要的细节）**：帽檐下没有皮肤，是一块近黑的脸，只露两只发光的黄眼睛（照 `eyes_guide.png`）：两只眼睛**一样大、一样高**，每只 2 格宽 2 格高，靠鼻子一侧的上角是黑的（眼睛斜着、凶），靠鼻子一侧的下角是一格更亮的眼芯；两只眼睛靠得近，中间只隔 1 格黑（照原画 A）；眼睛的黄色和亮芯**只用在眼睛上**。不画鼻子、不画嘴。铁手套和法杖都不能挡住眼睛。
- **法杖在近侧的手（图里左边），竖在身旁**，杖头的双叉刃和橙水晶在帽檐高度附近（照原画 A，不高过帽子最高点）；杖身 1–2 格宽，有方形的钢箍；杖的下端在脚底线以上结束。
- **远侧的手（图里右边）戴大铁手套，举到头边**，手指弯成爪；手臂和手套至少 3 格宽（加描边），和身体之间有描边隔开，不能是一条细线。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：两只靴底在同一行，就是第 99 行，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`veigar_design_A.png` 和 `veigar_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`veigar/veigar_source.png`、`veigar/size_place.png`、`veigar/quality_bar.png`、`veigar/eyes_guide.png`；`veigar/tfm2_style_mages.png` 和 `veigar/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the hat, the black face with the yellow eyes, the robe, the gauntlet, the staff, the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas. THIRD: six other heroes of this game at game size, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: his face at game size, 12x, with a grid - copy the face and the eyes square for square. (Optional: official mages of the game at 8x for the pixel style and the staffs, and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 40 pixels from the highest point of the hat to the soles, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: the hat's tip bent backward and drooping to the left, not rising; a short stocky yordle body in a wide flared robe; short legs; the hat's size as the VERSION lines at the end say (two images).
The character: Veigar, a tiny evil yordle wizard: a huge royal blue-violet pointed wizard hat whose tip bends backward to the left and droops, turning purple toward the tip, a wide flat brim, and a band of silver metal plates with small spikes and one square silver buckle round the crown; under the brim no skin at all - a pitch-black face with two slanted glowing yellow eyes, no nose, no mouth; a blue-violet robe with a wide flared skirt whose hem is a silver rim with small spikes, a silver spiked collar plate at the neck, a brown leather belt with silver studs and a silver buckle, a magenta cloth hanging at the far hip; silver spiked shoulder guards and bracers; the near hand (image left) in a steel glove holding a grey metal staff upright at his side - square steel collars, its head two long silver fork blades round a glowing orange crystal; the far hand (image right) in a HUGE silver spiked gauntlet raised beside his head, claw fingers curled; short dark legs, silver pointed boots with spikes.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 26 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks - black is only the outline and the face; never a second black ring inside the outline); every square describes something (a stud on the hat band, a fold, an edge, a spike) - no random specks, no dithering, no gradients, no noise.
Colours: blue-violet hat and robe in 4 shades with a lit edge, the hat tip turning purple; silver metal (hat band, studs, collar, shoulder guards, bracers, the skirt's rim and spikes, boots, the staff's blades) in 4 shades with bright highlights; brown belt in 3; magenta hip cloth in 3; dark grey legs; the staff's crystal ORANGE in 2-3 shades, clearly warmer than the eyes.
Face (most important detail): no skin under the brim, a near-black face showing only two glowing yellow eyes, exactly as the FOURTH image: both eyes the SAME size and on the SAME rows, each 2 squares wide and 2 tall with the top square on the nose side left black (slanted, evil), a brighter core square at the eye's inner bottom, the two eyes close together with ONE black square between them (as in the FIRST image); the eye yellows are used nowhere else. No nose, no mouth. Neither the gauntlet nor the staff covers the eyes.
The staff in the near hand (image left), upright at his side: its fork blades and orange crystal near the height of the hat brim as in the FIRST image, never above the hat's highest point; the shaft 1-2 squares wide with square steel collars; its lower end stops above the soles. The far hand (image right) in the huge spiked gauntlet, raised beside his head with curled claw fingers; the arm and gauntlet at least 3 squares wide with the outline, separated from the body by the outline.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: both soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image). Nothing below the soles (the game draws the health bar right under the feet).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 40 squares from the top of the hat to the soles; all squares 8x8 on one grid; at most 26 colours; one outline ring only; the detail and shading of the THIRD image, not flat dark areas; both eyes the same size, level and clearly visible; the eye yellow only in the eyes; the crystal orange; nothing below the soles.
VERSION A (veigar_design_A.png): the hat as big as in the FIRST image - from the brim to its highest point about 44% of the height (17-18 squares).
VERSION B (veigar_design_B.png): a smaller hat - from the brim to its highest point about one third of the height (13-14 squares), the tip still bent back and drooping; the rows saved go to the body, the gauntlet and the legs.
```

## 交回前自查

- [ ] 两版都是帽子最高点到脚底约 40 格（A 的帽子约 44%，B 约三分之一）；脚底最低一行在第 99 行，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块平涂；
- [ ] 帽尖向后向左垂下；帽带有银铆钉和方扣；
- [ ] 黑脸上两只黄眼睛一样大、一样高，斜着，各有一格亮芯；眼睛的黄只在眼睛上；水晶是橙色；
- [ ] 法杖在左手、竖在身旁、不高过帽子；右手的大铁手套举在头边，不挡眼睛；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛（一样大、一样高），只补缺的描边。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
