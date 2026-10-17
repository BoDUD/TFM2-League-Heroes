# 娑娜：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照原画 A（`sona/sona_source.png`，你上一轮画的：英雄联盟的待机，琴平浮在腰前、双手抚弦）在**游戏尺寸**重新画。两版只差头的大小：
> - **版本 A**：头（头顶到下巴，不算马尾）约 **10 格**、脸约 **7 格宽**；两只眼睛各 **2 格宽、3 格高**（睫毛一行、高光 + 瞳孔一行、虹膜一行）；双马尾高出头顶约 5 格；裙摆（琴底尖到下摆）约 11 格；
> - **版本 B**：头画大一点，约 **12 格**、脸约 **8 格宽**，眼睛一样 2×3；双马尾小一点、低一点（高出头顶约 3–4 格）；裙摆短 2 格（约 9 格），总高还是 40 格；衣服、琴、飘带和 A 一样。
>
> 其余两版都一样：
> - **大小**：从双马尾最高处到裙摆下沿 **正好 40 格**，从琴后端的弯角到前端的卷翼约 **28 格宽**（原画按 40 格高算出来的宽度）。裙摆最下一行在第 99 行（y=792–799）、裙摆中间在中间那一列（x=512，蓝线），马尾最高处在第 60 行（绿线）；大小和位置看 `sona/size_place.png`。40 格是现在的规矩（锐雯、薇恩 46–48 格在游戏里太大）。
> - **你前几轮的造型图都画大了**（乐芙兰的第一版 86 格、卡莎的 79 格，要求都是 40 多格）。这次请交之前**数一下行数**：画大了就重画小，不要缩小（缩小会把细节弄碎）。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `sona/quality_bar.png` 里 main 分支的英雄（迦娜、莫甘娜、凯特琳、阿狸、娜美，都是现在游戏里的样子，用户认可的）。要有亮的点缀：金边、发饰、卷翼上白金色的亮点，头发和裙片上浅青高光，琴弦是亮青色。
> - **上衣在这个尺寸画成盖住胸口的蓝色上衣**（露肩、锁骨是皮肤色），胸口不要画深色的线（这么小的尺寸会像一道褶）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`sona/size_guide.png` 是原画直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 28 种。交付 `sona_design_A.png`、`sona_design_B.png`（1024×1024）和各自的原尺寸图 `sona_design_A_1x.png`、`sona_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到、每版实际多少行）和色板，最好打成一个 zip（`sona_design_pack.zip`，放在 outputs 里），HANDOFF.md 最后写。

## 附图（都在压缩包的 `sona/` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `sona_source.png` / `sona_source_white.png` | 原画 A（透明底 / 白底） | **长相**：双马尾和金色发梢、两个金发饰、刘海、温柔的脸、宝蓝长裙、金边高领、宽袖金袖口、金腰带、浅青裙片和金色卷纹、金色下摆、平浮在腰前的金色叶琴（青色琴弦、小木码、琴底尖、前端大卷翼、后端弯角）、两条青色飘带、双手抚弦，颜色和姿势 |
| `size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 她的大小和位置（40 格高、28 格宽）；绿线 = 马尾最高处（第 60 行），红线 = 裙摆最下一行的下沿，蓝线 = 裙摆中间那一列 | 只看大小和位置 |
| `quality_bar.png` | main 里 5 位英雄（迦娜 45 格、莫甘娜 45、凯特琳 41、阿狸 40、娜美 50），游戏里现在的样子 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `face_ref.png` | 原画 A 的头部放大（480×371） | 脸、眼睛、刘海、发饰 |
| `etwahl_ref.png` | 原画 A 的琴和双手放大（999×585） | 琴身、琴弦、木码、两头的卷饰、飘带、手 |
| `tfm2_style_gentle.png` | 团战经理2 原版的吟游诗人（抱着琴）、魔导师、牧师、白魔法师，×8 | 原版的像素画法：温柔的施法者和乐器在这个尺寸怎么画 |
| `size_guide.png` | 原画直接缩到 40 格，同一画布、同一裙摆线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：马尾最高处到裙摆正好 40 格、琴从头到尾约 28 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例是 Q 版**，像 `quality_bar.png` 的英雄：头按两版各自的大小，双马尾在头的上方和两侧，肩和手臂小，琴平着横在腰前，裙摆在琴下面展开到下摆。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色：蓝裙的暗部是深海军蓝，青色的暗部是深青，金色的暗部是琥珀棕），**不要在描边里再画第二圈黑**（黑色只用于描边）；每个小方块都在画东西（发丝、金色发梢、金边、卷纹、褶、琴弦、木码），不要随手撒的杂点，不要抖动、渐变、噪点；最多 28 色。
- **脸（最重要的细节）**：照 `face_ref.png`，3/4 正面朝右；两只眼睛都看得见、**在同一行**，各 2 格宽 3 格高：最上一行深色睫毛，第二行白色高光挨着深青瞳孔，第三行青色虹膜；近眼和刘海/鬓发之间留一列皮肤，两眼之间两列皮肤，远眼靠近远处的脸颊；眼睛下面两行脸，嘴是一格玫红色、在脸的中线上；下巴下面一格浅一点的皮肤阴影；刘海停在眼睛上面，什么都不挡脸；近处的脸颊边缘是圆的，不是一刀切的直边。
- **手和琴**：每只手是袖子（带金袖口）末端一个 2×2 的皮肤色小手，放在琴弦上，连着手臂，不能飘着；琴完整、平着，不低于裙子的中部；两条飘带的末端至少比裙摆那一行高 2 格。
- **裙摆以下什么都不能有**（游戏在脚下画血条）：裙摆最下一行在第 99 行、中间在 x=512，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`sona_design_A.png` 和 `sona_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`sona/sona_source.png`、`sona/size_place.png`、`sona/quality_bar.png`、`sona/face_ref.png`、`sona/etwahl_ref.png`；`sona/tfm2_style_gentle.png` 和 `sona/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy her look: the two big cyan twin tails with golden-yellow tips sweeping up and out on both sides of her head, the two gold hair ornaments at their roots, the side-swept fringe, the gentle face with teal eyes and a small smile; the royal-blue gown with the tall gold-edged collar behind her shoulders, the wide blue sleeves with gold cuffs, the gold sash, the flared skirt with light-cyan gold-edged panels and gold swirls, the gold hem; the floating golden instrument (the Etwahl) LEVEL in front of her hips with its cyan strings, small brown bridges, the pointed keel under its middle, the big gold wing-scroll finial rising at its front end (image right) and the slim curved horn at its back end (image left), and the two cyan ribbons hanging from it; both her small hands resting on the strings; the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for her size and her place in the canvas (the green line is the top of her hair tails, the red line the hem's lowest row, the blue line the hem's middle). THIRD: five heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head big (the face, the eyes, the fringe, the ornaments) and FIFTH: its instrument and hands big. (Optional: official heroes of the game at 8x - a bard with a lute, an enchantress with golden orbs, a priestess and a white mage - for how a gentle caster and an instrument are drawn at this size; and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): exactly 40 pixels from the top of the twin tails to the hem and about 28 pixels wide from the back of the instrument to its front finial, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: chibi like the THIRD image's heroes - the head as big as the VERSION lines at the end say (two images), the twin tails above and beside it, the shoulders and arms small, the instrument level across her hips, the skirt flaring out below it to the hem.
The character: Sona, a gentle musician: HAIR - two big TWIN TAILS of bright cyan-blue hair in 4 shades, each ending in a GOLDEN-YELLOW tip (2 shades), tied high at the back of the head and sweeping up and out to both sides (each tail about 7 squares across), a side-swept cyan fringe over the forehead that stops above the eyes, a cyan lock beside each cheek, two small GOLD hair ornaments (each 2-3 squares, curved like little horns) at the roots of the tails; FACE - fair skin in 3 shades, two teal eyes, ONE small rose-red square for the mouth; GOWN - bare shoulders in skin, a royal-blue bodice that covers the chest (at this size no cleavage line: a dark line there reads as a crease), a TALL STAND-UP COLLAR in blue with a gold edge rising behind each shoulder, wide blue SLEEVES with gold cuffs, the skin hands small (2x2) resting on the strings; INSTRUMENT (the Etwahl, her signature - big and clear) - a long floating zither of golden carved wood in 3-4 gold/amber shades with a highlight, LEVEL in front of her hips, its body 3-4 squares thick with a pointed keel 2 squares deep under its middle, along its top a 1-square row of bright cyan strings with 2-3 small brown bridges; its FRONT end (image right) curls up into a big gold WING-SCROLL finial 5-6 squares tall, its BACK end (image left) rises into a slim curved gold horn 4-5 squares tall; two light-cyan RIBBONS with gold edges, 2 squares wide, hang from under both ends; SKIRT - from under the instrument it flares out to about 20 squares wide at the hem, royal blue with long light-cyan front and side panels edged in gold, a small gold diamond on the blue middle panel, a gold hem; the skirt hides her feet.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours. Bright accents so she reads on the dark battlefield: white-gold glints on the gold trim, the ornaments and the finials; light-cyan highlights on the hair and the panels; the strings bright cyan.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 28 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks: deep navy for the blue gown, teal for the cyan, amber-brown for the gold - black is only the outline; never a second black ring inside the outline); every square describes something (a hair strand, a golden tip, a gold edge, a swirl, a fold, a string, a bridge) - no random specks, no dithering, no gradients, no noise.
Face (most important detail), as the FOURTH image: 3/4 front view facing right; both eyes visible, on the SAME rows, the sizes the VERSION lines say: each eye a dark lash square-row on top, then a white highlight beside a dark teal pupil, then the teal iris; one skin column between the near eye and the fringe or lock, two skin columns between the two eyes, the far eye near the far cheek; two rows of face under the eyes, the rose-red mouth square on the face's middle line under them, a soft skin shade under the chin; the fringe stops above the eyes and nothing covers the face; the near cheek's edge rounded, not a straight cut.
Hands and instrument: each hand a 2x2 skin shape at the end of a sleeve (with its gold cuff), resting on the strings, joined to the arm - no floating hands; the instrument whole, level, nothing of it below the skirt's middle; the ribbons end at least 2 squares above the hem's row.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: the hem's lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the hem's middle on the middle column (x=512), the tops of the twin tails on square row 60 (y=480). Nothing below the hem (the game draws the health bar right under it).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: COUNT the rows - 40 squares from the tops of the twin tails to the hem, not more (if your drawing came out bigger, draw it again smaller - never shrink it); about 28 squares from the instrument's back horn to its front finial; all squares 8x8 on one grid; at most 28 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both eyes level and clearly visible; the instrument level with its cyan strings, both finials and both ribbons; both hands on the strings; the hem the lowest row and nothing below it.
VERSION A (sona_design_A.png): the head from the crown of the head (under the tails' roots) to the chin about 10 squares and the face about 7 squares wide; each eye 2 squares wide and 3 tall (lashes, highlight + pupil, iris); the twin tails rise about 5 squares above the crown; the skirt from the instrument's keel to the hem about 11 squares.
VERSION B (sona_design_B.png): a bigger chibi head so the face reads at this small size - the head from the crown to the chin about 12 squares and the face about 8 squares wide; each eye 2 squares wide and 3 tall; the twin tails a little smaller and lower, rising about 3-4 squares above the crown; the skirt 2 squares shorter (about 9 from the keel to the hem) so the whole figure is still 40 squares tall; the gown, the instrument and the ribbons the same as in version A.
```

## 交回前自查

- [ ] **数行数**：两版都是马尾最高处到裙摆正好 40 格（A 头约 10 格、马尾高出头顶约 5 格；B 头约 12 格、马尾高出约 3–4 格）、琴约 28 格宽；裙摆最下一行在第 99 行、中间在 x=512，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、亮点一个水平，不是大块平涂；
- [ ] 两只眼睛在同一行、各 2×3、看得清；嘴是一格玫红；刘海和琴都没挡脸；胸口是盖住的蓝色上衣；
- [ ] 琴平着、完整：青色琴弦、木码、琴底尖、前端卷翼、后端弯角、两条飘带；两只手在琴弦上、连着袖子；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、裙摆线、眼睛，只补缺的描边。画大了就按整行整列删到 40 行（不删脸上的行）。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
