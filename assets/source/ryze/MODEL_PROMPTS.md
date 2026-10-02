# 瑞兹：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照原画 A（`ryze/ryze_source.png`，你上一轮画的：英雄联盟的待机，双手张开垂在身侧）在**游戏尺寸**重新画。两版只差头的大小：
> - **版本 A**：头（头顶到下巴，不算胡子）约 **10 格**、脸约 **8 格宽**，胡子再往下约 5 格；两只眼睛各 **2 格宽、2 格高**（上面一行是皱着的深色眉毛，下面一行是发光的眼睛：一格白 + 一格浅紫，没有黑瞳孔）；卷轴顶端比头顶高约 5 格；
> - **版本 B**：头画大一点，约 **12 格**、脸约 **9 格宽**，眼睛一样 2×2；胡子短一点（下巴下约 4 格）；腿短 2 格，总高还是 40 格；卷轴顶端比头顶高约 3–4 格；衣服、手臂、卷轴和 A 一样。
>
> 其余两版都一样：
> - **大小**：从卷轴顶端到靴底 **正好 40 格**（光头的头顶比卷轴顶端低约 5 格），从卷轴后沿到前面那只手约 **27 格宽**（原画按 40 格高算出来的宽度）。靴底最下一行在第 99 行（y=792–799）、两脚中间在中间那一列（x=512，蓝线），卷轴顶端在第 60 行（绿线）；大小和位置看 `ryze/size_place.png`。40 格是现在的规矩（锐雯、薇恩 46–48 格在游戏里太大）。
> - **你前几轮的造型图常常画大了**（乐芙兰的第一版 86 格、卡莎的 79 格，要求都是 40 格左右）。这次请交之前**数一下行数**：画大了就重画小，不要缩小（缩小会把细节弄碎）。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `ryze/quality_bar.png` 里 main 分支的英雄（德莱厄斯、盖伦、塔里克、李青、维迦，都是现在游戏里的样子，用户认可的）。要有亮的点缀：发光的眼睛是脸上最亮的格子，头皮、眉骨、手臂上浅薰衣草色的高光，铜扣、护膝、肩甲铜钉的亮点，羊皮纸的浅米色边，蓝色符文徽章。
> - **手臂要粗、手要大**：手臂描边里面 3 格粗（蓝紫皮肤 + 符文线），手腕棕色护腕，手是 3×3 张开的大手，连着手臂；不要 1–2 格的细棍手臂（之前娑娜的动作帧就出过这个问题）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`ryze/size_guide.png` 是原画直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 28 种。交付 `ryze_design_A.png`、`ryze_design_B.png`（1024×1024）和各自的原尺寸图 `ryze_design_A_1x.png`、`ryze_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到、每版实际多少行）和色板，最好打成一个 zip（`ryze_design_pack.zip`，放在 outputs 里），HANDOFF.md 最后写。

## 附图（都在压缩包的 `ryze/` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `ryze_source.png` / `ryze_source_white.png` | 原画 A（透明底 / 白底） | **长相**：光头、蓝紫皮肤、符文纹身、皱眉、发光的眼睛、棕色长胡子（末端小金扣）、粗壮的手臂和护腕、深海军蓝无袖上衣、交叉皮带、棕色皮肩甲、圆形大铜扣腰带、深青布条、灯笼裤和铜扣、高筒靴和圆铜护膝、背上的卷轴（羊皮纸、铁帽、卷轴筒、铜箍、蓝色徽章），颜色和姿势 |
| `size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（40 格高、27 格宽）；绿线 = 卷轴顶端（第 60 行），红线 = 靴底最下一行的下沿，蓝线 = 两脚中间那一列 | 只看大小和位置 |
| `quality_bar.png` | main 里 5 位英雄（德莱厄斯 42 格、盖伦 37、塔里克 40、李青 41、维迦 40），游戏里现在的样子 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `face_ref.png` | 原画 A 的头和胡子放大（456×532） | 光头、符文、皱眉、发光的眼睛、鼻子、胡子 |
| `scroll_ref.png` | 原画 A 的卷轴放大（418×810） | 羊皮纸、铁帽、卷轴筒、铜箍、蓝色徽章 |
| `tfm2_style_bald.png` | 团战经理2 原版的武僧（光头大胡子）、大力士（粗壮手臂）、道士（长胡子），×8 | 原版的像素画法：光头、胡子、手臂在这个尺寸怎么画 |
| `size_guide.png` | 原画直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：卷轴顶端到靴底正好 40 格、宽约 27 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例是 Q 版**，像 `quality_bar.png` 的英雄：头按两版各自的大小，身体结实宽厚，手臂粗、手大，卷轴在头的上方和身后。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色：皮肤的暗部是深紫，上衣和裤子的暗部是深海军蓝，皮革和胡子的暗部是深棕，铜的暗部是琥珀棕），**不要在描边里再画第二圈黑**（黑色只用于描边）；每个小方块都在画东西（符文线、胡须、皮带、铜扣、褶、铜钉、铜箍），不要随手撒的杂点，不要抖动、渐变、噪点；最多 28 色。
- **脸（最重要的细节）**：照 `face_ref.png`，3/4 正面朝右；两只眼睛都看得见、**在同一行**，各 2 格宽 2 格高：上面一行是向鼻子斜下去的深靛色眉毛（皱眉），下面一行是发光的眼睛（一格白 + 一格浅紫，没有黑瞳孔）；**白色和浅紫只用在眼睛上**；近眼和脸的边缘之间留一列皮肤，两眼之间两列皮肤，远眼靠近远处的脸颊；眼睛下面是鼻子和一行脸，然后是八字胡和胡子；什么都不挡眼睛；近处的脸颊边缘是圆的，不是一刀切的直边。
- **手和手臂**：每只手是护腕末端 3×3 张开的皮肤色大手，连着手臂，不能飘着，不能是 1 格的细棍；两条手臂像原画一样稍微离开身体垂着，手在膝盖上方。
- **靴底以下什么都不能有**（游戏在脚下画血条）：靴底最下一行在第 99 行、两脚中间在 x=512，下面一格都不能有；卷轴、布条、手都在这一行上面。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`ryze_design_A.png` 和 `ryze_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`ryze/ryze_source.png`、`ryze/size_place.png`、`ryze/quality_bar.png`、`ryze/face_ref.png`、`ryze/scroll_ref.png`；`ryze/tfm2_style_bald.png` 和 `ryze/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the completely bald head with blue-violet skin and the darker indigo rune tattoo lines on the scalp and temples, the heavy frowning brow, the two glowing pale violet-white eyes, the broad nose, the small stern mouth, the long dark-brown beard with a moustache hanging over the upper chest to a point with a small gold clasp near its end; the broad shoulders, the thick bare blue-violet arms with rune lines, the brown leather wrist bracers, the big open hands hanging a little away from his sides; the sleeveless dark navy tunic, the brown leather straps with bronze buckles crossing his chest, the big brown leather pauldron with a bronze stud on the shoulder at image right, the wide brown belt with the big round bronze buckle disc, the short dark-teal cloth strips hanging from the belt, the very baggy dark slate-blue trousers with a row of small bronze toggles, the tall brown boots with the big round bronze knee guards; THE SCROLL on his back: a huge rolled cream parchment in a brown leather case with bronze bands and a round blue rune medallion, slanted, its top end with the frayed parchment edge and the dark iron cap rising above his head at image left, its lower end behind his hips; the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas (the green line is the top of the scroll, the red line the soles' lowest row, the blue line the middle between his feet). THIRD: five heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head and beard big and FIFTH: its scroll big. (Optional: official heroes of the game at 8x - a bald bearded monk, a strongman with bare muscular arms, an old taoist with a long beard - for how a bald head, a beard and bare arms are drawn at this size; and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): exactly 40 pixels from the top of the scroll to the soles (the crown of his bald head about 5 pixels lower than the scroll's top) and about 27 pixels wide from the scroll's back edge to his front hand, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: chibi like the THIRD image's heroes - the head as big as the VERSION lines at the end say (two images), a sturdy broad body, strong arms, big hands, the scroll above and behind him.
The character: Ryze, the rune mage: SKIN - blue-violet in 4 shades (deep violet, periwinkle blue, light lavender, a pale lavender highlight) on the head, the face and the bare arms, with thin darker indigo rune lines (1 square wide) on the scalp, the temples and the upper arms; HEAD - completely bald and round on top, a heavy brow ridge, a small ear at the near side; FACE - stern: a dark-indigo brow line over each eye slanting down toward the nose (a frown), the glowing eyes as the VERSION lines say, a broad nose drawn with the skin's shades, a small dark mouth line under it; BEARD - dark brown in 3 shades with a light-brown highlight: a moustache joining a long full beard from the cheeks and the chin down over the upper chest to a point, a small gold clasp near its end; BODY - broad shoulders; a sleeveless dark navy-slate tunic (3 shades) with a small stand-up collar; two brown leather straps crossing the chest with small bronze buckles; a big brown leather PAULDRON (4 squares wide) with a bronze stud on the shoulder at image right; ARMS - thick, bare, in the skin's shades with rune lines, 3 squares thick inside the outline, brown leather bracers at the wrists, big open HANDS (3x3 squares, the fingers spread) hanging a little away from his sides; BELT - wide brown leather with a big round BRONZE BUCKLE disc (3x3) in the middle, short dark-teal cloth strips hanging below it; TROUSERS - very baggy dark slate-blue (3 shades), gathered at the knees, a row of small bronze toggles down the front; BOOTS - tall brown leather boots (3 shades), a big round BRONZE KNEE GUARD (3x3, with a bright glint) on each knee, the feet planted apart; THE SCROLL (his signature - big and clear): a rolled cream parchment (3 cream shades and a light highlight) about 6 squares wide with a frayed top edge and a small dark-iron cap in its middle, held in a brown leather case with two bronze bands and a round BLUE rune medallion (2x2) on its side, slanted on his back, its top 5 squares above his crown at image left, the case showing beside his body on that side.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours. Bright accents so he reads on the dark battlefield: the glowing eyes the brightest squares of the face, pale lavender highlights on the scalp, the brow and the arms, glints on the bronze buckle, the knee guards and the stud, the parchment's light cream edge, the blue medallion.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 28 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks: deep violet for the skin, deep navy for the tunic and the trousers, dark brown for the leather and the beard, amber-brown for the bronze - black is only the outline; never a second black ring inside the outline); every square describes something (a rune line, a beard strand, a strap, a buckle, a fold, a toggle, a band) - no random specks, no dithering, no gradients, no noise.
Face (most important detail), as the FOURTH image: 3/4 front view facing right; both eyes visible, on the SAME rows, the sizes the VERSION lines say; the glowing eye colours (white and light lilac) used ONLY in the eyes; one skin column between the near eye and the face's edge, two skin columns between the two eyes, the far eye near the far cheek; under the eyes the nose and one row of face, then the moustache and the beard; nothing covers the eyes; the near cheek's edge rounded, not a straight cut.
Hands and arms: each hand a 3x3 open skin hand at the end of a bracer, joined to the arm - no floating hands, no 1-square stick arms; both arms hang a little away from the body as in the FIRST image, the hands above the knees.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: the soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the middle between his feet on the middle column (x=512), the top of the scroll on square row 60 (y=480). Nothing below the soles (the game draws the health bar right under them): the scroll, the cloth strips and the hands all end above that row.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: COUNT the rows - 40 squares from the top of the scroll to the soles, not more (if your drawing came out bigger, draw it again smaller - never shrink it); about 27 squares from the scroll's back edge to his front hand; all squares 8x8 on one grid; at most 28 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both glowing eyes level and clearly visible; the beard, the pauldron, the bronze buckle and both knee guards there; the scroll whole with its case, bands and blue medallion; both hands joined to the arms; the soles the lowest row and nothing below them.
VERSION A (ryze_design_A.png): the head from the crown to the chin about 10 squares (the beard hangs about 5 squares lower) and the face about 8 squares wide; each eye 2 squares wide and 2 tall: the top row part of the dark frowning brow, the bottom row the glowing eye - a white square beside a light-lilac square (no dark pupil); the scroll's top about 5 squares above the crown.
VERSION B (ryze_design_B.png): a bigger chibi head so the face reads at this small size - the head from the crown to the chin about 12 squares and the face about 9 squares wide; each eye 2 squares wide and 2 tall as in version A; the beard a little shorter (about 4 squares under the chin); the legs 2 squares shorter so the whole figure is still 40 squares tall; the scroll's top about 3-4 squares above the crown; the clothes, the arms and the scroll the same as in version A.
```

## 交回前自查

- [ ] **数行数**：两版都是卷轴顶端到靴底正好 40 格（A 头约 10 格、卷轴高出头顶约 5 格；B 头约 12 格、卷轴高出约 3–4 格）、宽约 27 格；靴底最下一行在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、亮点一个水平，不是大块平涂；
- [ ] 两只发光的眼睛在同一行、各 2×2（眉 + 眼）、看得清；白色和浅紫只在眼睛上；胡子、肩甲、圆铜扣、两个护膝都在；
- [ ] 手臂 3 格粗、手 3×3、连着手臂；卷轴完整（羊皮纸、铁帽、卷轴筒、铜箍、蓝色徽章），斜背在背上、顶端在画面左侧高过头顶；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛、手臂粗细，只补缺的描边。画大了就按整行整列删到 40 行（不删脸上的行）。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
