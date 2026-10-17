# 基兰：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照原画 A（`zilean/zilean_source.png`，你上一轮画的：英雄联盟的待机，悬浮、两手向两边张开掌心向上、背着大金色时钟）在**游戏尺寸**重新画。原画的脸太小（按 40 格算，眉毛到下巴只有约 2 格，放不下眼睛鼻子），所以两版都把**脸放大**，只差头的大小：
> - **版本 A**：头（头发顶到下巴）约 **11 格**：尖刺头发在眉毛上面约 4 格，脸（眉毛到下巴）约 **6 格高、7 格宽**；两只眼睛各 **2 格宽、2 格高**（上面一行是往鼻子压下去的浓蓝眉毛，下面一行是发光的眼睛：一格淡青白 + 一格深蓝瞳孔）；胡子在下巴下约 6 格，往前卷；
> - **版本 B**：头画大一点，约 **13 格**：头发约 4 格，脸约 **7 格高、8 格宽**，眼睛一样 2×2；胡子短一点（下巴下约 5 格）；长袍短 2 格，总高还是 40 格；衣服、手臂、时钟和 A 一样。
>
> 其余两版都一样：
> - **大小**：从时钟顶上木屋的屋顶到最低的脚趾 **正好 40 格**（头发顶比屋顶低约 4 格），从时钟左边的小齿轮到右边的小齿轮约 **27 格宽**（原画按 40 格高算出来的宽度）。最低的脚趾在第 99 行（y=792–799）、两脚中间在中间那一列（x=512，蓝线），屋顶在第 60 行（绿线）；大小和位置看 `zilean/size_place.png`。40 格是现在的规矩（锐雯、薇恩 46–48 格在游戏里太大）。
> - **你前几轮的造型图常常画大了**（乐芙兰的第一版 86 格、卡莎的 79 格，要求都是 40 格左右）。这次请交之前**数一下行数**：画大了就重画小，不要缩小（缩小会把细节弄碎）。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `zilean/quality_bar.png` 里 main 分支的英雄（维迦、娑娜、乐芙兰、塔里克、凯南，都是现在游戏里的样子，用户认可的）。要有亮的点缀：发光的眼睛是脸上最亮的格子，头发和胡子里的天蓝高光，金色钟框、时针、齿轮、腰扣的亮点，象牙白的钟面和青绿色的数字，红色披带和下摆，长袍褶子的浅灰亮边。
> - **眼睛的颜色只给眼睛用**：眼睛是淡青白色（发光），时钟上的数字用更深的青绿色，不能和眼睛同一个颜色（导入时要靠眼睛的颜色找脸）。
> - **手和手臂**：宽大的深灰袖子（描边里面 3–4 格粗），红色袖口，袖口伸出掌心向上的小手（3 格宽、2 格高的肤色），连着袖子；不要 1–2 格的细棍手臂。
> - **时钟是他的标志**：圆钟面约 15 格宽（象牙白、4 个青绿数字记号、一圈青绿内环），2 格厚的金色齿边框（方齿、铆钉），一根 2 格宽、约 8 格长的金色时针从中心往右上方伸出、越过远侧肩膀，左右两边各飘一个 3×3 的小金齿轮（中间一个黑孔），左下挂一个金色钟摆（1 格的杆 + 3×3 的圆球），顶上一个约 5×3 的小木屋（金边尖顶，全身最高的地方）。
> - **直接按游戏尺寸画**，不要先画大再缩小。`zilean/size_guide.png` 是原画直接缩到 40 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它（它的脸太小了）。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 30 种。交付 `zilean_design_A.png`、`zilean_design_B.png`（1024×1024）和各自的原尺寸图 `zilean_design_A_1x.png`、`zilean_design_B_1x.png`；**另外请把你用图像模型画出来的原始草稿（整理之前的）放在 `outputs/zilean_design_sources/` 里**（瑞兹那一轮，草稿比用代码整理过的成品好）。附 `HANDOFF.md`（用了哪段提示词、哪里没做到、每版实际多少行、成品是图像模型画的还是代码拼的）和色板，最好打成一个 zip（`zilean_design_pack.zip`，放在 outputs 里），HANDOFF.md 最后写。

## 附图（都在压缩包的 `zilean/` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `zilean_source.png` / `zilean_source_white.png` | 原画 A（透明底 / 白底） | **长相**：蓝色尖刺头发、尖耳朵、浓眉、发光的青色眼睛、大鼻子、往前卷的蓝色长胡子、深灰长袍和宽袖、带圆环花纹的浅灰前片、印数字的红边、红色长披带、金扣绳腰带、光脚，背上的大时钟（木屋顶、象牙钟面、青绿数字、金齿框、时针、小齿轮、钟摆），颜色和姿势 |
| `size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（40 格高、27 格宽）；绿线 = 时钟屋顶（第 60 行），红线 = 最低脚趾那一行的下沿，蓝线 = 两脚中间那一列 | 只看大小和位置 |
| `quality_bar.png` | main 里 5 位英雄（维迦 40 格、娑娜、乐芙兰、塔里克 40、凯南），游戏里现在的样子 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `face_ref.png` | 原画 A 的头放大（440×535） | 头发、尖耳朵、眉毛、发光的眼睛、鼻子、胡子 |
| `clock_ref.png` | 原画 A 的时钟放大（999×832） | 木屋顶、钟面、数字、金齿框、时针、小齿轮 |
| `tfm2_style_old.png` | 团战经理2 原版的道士（白发长胡子、黑袍红饰）、武僧（大胡子）、占星师（长袍），×8 | 原版的像素画法：老人的脸、胡子、长袍在这个尺寸怎么画 |
| `size_guide.png` | 原画直接缩到 40 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：时钟屋顶到最低的脚趾正好 40 格、宽约 27 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例是 Q 版**，像 `quality_bar.png` 的英雄：头和脸按两版各自的大小（比原画的脸大），身体在长袍里偏瘦，手和时钟稍大。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色：头发和胡子的暗部是深海军蓝，长袍是深石板灰，披带和红边是暗红，金色的暗部是暗铜，皮肤是暖棕），**不要在描边里再画第二圈黑**（黑色只用于描边）；每个小方块都在画东西（一绺头发、一缕胡子、褶子、数字记号、齿轮的齿、铆钉），不要随手撒的杂点，不要抖动、渐变、噪点；最多 30 色。
- **脸（最重要的细节）**：照 `face_ref.png`，3/4 正面朝右；两只眼睛都看得见、**在同一行**，各 2 格宽 2 格高：上面一行是向鼻子斜下去的浓蓝眉毛（皱眉），下面一行是发光的眼睛（一格淡青白 + 一格深蓝瞳孔）；**淡青白只用在眼睛上**；近眼和脸的边缘之间留一列皮肤，两眼之间两列皮肤，远眼靠近远处的脸颊；眼睛下面是鼻子和一行脸，然后是八字胡和胡子；头发在眉毛上面、胡子在鼻子下面，什么都不挡眼睛；尖耳朵在近侧脸颊外面；近处的脸颊边缘是圆的，不是一刀切的直边。
- **手和手臂**：每只手是红袖口末端掌心向上的小手，连着袖子，不能飘着，不能是 1 格的细棍；两条手臂像原画一样向两边张开，手在胸口高度。
- **脚趾以下什么都不能有**（游戏在脚下画血条）：最低的脚趾在第 99 行、两脚中间在 x=512，下面一格都不能有；长袍下摆、披带、钟摆都在这一行上面。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`zilean_design_A.png` 和 `zilean_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`zilean/zilean_source.png`、`zilean/size_place.png`、`zilean/quality_bar.png`、`zilean/face_ref.png`、`zilean/clock_ref.png`；`zilean/tfm2_style_old.png` 和 `zilean/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the tall mane of BLUE hair standing up in big spiky locks like blue flames, the pointed ear, the bushy blue brows over the glowing cyan eyes (a stern old man), the big nose, the long BLUE beard with a moustache flowing forward and curling out in front of his chest toward image right; the long dark charcoal-grey robe with wide sleeves, the lighter grey front panel with a pattern of small rings, the RED bands with dark clock numerals on the hem and the sleeve ends, the long RED stole hanging from both shoulders, the gold belt buckle with a knotted gold rope belt, the bare tan feet hanging down (he floats); both arms held out to his sides at chest height with the palms OPEN and turned UP; THE CLOCK on his back: a big round ivory clock face with turquoise numerals in a thick gold toothed rim, a big gold clock hand pointing up and to the right past his far shoulder, small gold gears floating beside it, a gold pendulum with a round bob hanging below it at image left, a little dark-wood house with a gold-trimmed peaked roof on top; the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas (the green line is the top of the clock's roof, the red line the lowest toe's row, the blue line the middle between his feet). THIRD: five heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head big and FIFTH: its clock big. (Optional: official heroes of the game at 8x - an old taoist with white hair, a long beard and a black robe with red, a bearded monk, a robed astrologer - for how an old face, a beard and a robe are drawn at this size; and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look: its face is far too small.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): exactly 40 pixels from the top of the clock's roof to his lowest toe (the top of his hair about 4 pixels lower than the roof) and about 27 pixels wide from the clock's left gear to its right gear, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: chibi like the THIRD image's heroes - the head and the face as big as the VERSION lines at the end say (two images; the illustration's face is too small for this size: ENLARGE THE FACE, keep the hair crest a little lower), a slim body in the long robe, the hands and the clock a little oversized.
The character: Zilean, the time mage, an old man who floats: HAIR - a mane of spiky locks standing up and back, BLUE in 4 shades (deep navy shadows, mid blue, sky blue, a pale sky-blue highlight), lighter than the robe; FACE - tan skin in 3 shades, a POINTED EAR at the near side (image left of the face), bushy blue BROWS sloping down toward the nose (a stern frown), the glowing eyes as the VERSION lines say, a big nose drawn with the skin's shades; BEARD - blue like the hair: a moustache over the mouth joining a long full beard from the cheeks and the chin that flows forward and curls out toward image right in front of his chest; ROBE - long, dark charcoal-grey in 3 shades with light grey edge highlights on the folds, down to his ankles, the front panel of the lower robe lighter grey with a few small light rings, a RED band (2 squares) with dark numeral marks along the hem; the RED STOLE - two red strips (2 squares wide) from both shoulders down the front, their ends fluttering; BELT - a gold buckle (2x2, bright glint) with a gold rope belt; ARMS - in WIDE dark grey sleeves (3-4 squares thick inside the outline) with red cuffs, held out to his sides at chest height, elbows bent; HANDS - open tan hands with the palms turned UP (3 squares wide, 2 tall), joined to the sleeves; FEET - bare tan feet hanging down under the hem, the toes pointing down; THE CLOCK (his signature - big and clear, behind his head and shoulders): a round CLOCK FACE about 15 squares across, ivory with 4 turquoise numeral marks and a turquoise inner ring, inside a thick GOLD rim (2 squares, square teeth, a few rivets) with 4-5 gold shades and bright glints; a big gold CLOCK HAND (2 squares wide, about 8 long) from the face's centre up and to the right past his far shoulder; two small gold GEARS (3x3 with a dark hole) floating at the clock's left and right edges; a gold PENDULUM (a 1-square rod and a round 3x3 bob) hanging below the clock at image left behind the robe; a little dark-wood HOUSE (about 5 wide, 3 tall) with a gold-trimmed peaked roof on top of the clock - the highest thing.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours. Bright accents so he reads on the dark battlefield: the glowing eyes the brightest squares of the face, sky-blue highlights in the hair and the beard, glints on the gold rim, the clock hand, the gears and the buckle, the ivory clock face, the red stole and bands, light grey edges on the robe.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 30 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks: deep navy for the hair and the beard, dark slate for the robe, dark red for the stole and bands, dark bronze for the gold, warm brown for the skin - black is only the outline; never a second black ring inside the outline); every square describes something (a lock of hair, a beard strand, a fold, a numeral mark, a gear tooth, a rivet) - no random specks, no dithering, no gradients, no noise.
Face (most important detail), as the FOURTH image: 3/4 front view facing right; both eyes visible, on the SAME rows, the sizes the VERSION lines say; the eye colour (a pale glowing cyan-white) used ONLY in the eyes - the clock's numerals are a stronger turquoise, a different colour; one skin column between the near eye and the face's edge, two skin columns between the two eyes, the far eye near the far cheek; under the eyes the nose and one row of face, then the moustache and the beard; nothing covers the eyes (the hair stays above the brows, the beard below the nose); the pointed ear outside the near cheek; the near cheek's edge rounded, not a straight cut.
Hands and arms: each hand a small open tan hand at the end of a red cuff, joined to the sleeve - no floating hands, no 1-square stick arms; both arms held out to his sides as in the FIRST image, the hands at chest height.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: the lowest toe's row at y=792-799 (square row 99, 28 squares above the bottom of the image), the middle between his feet on the middle column (x=512), the top of the clock's roof on square row 60 (y=480). Nothing below the toes (the game draws the health bar right under them): the robe's hem, the stole and the pendulum all end above that row.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: COUNT the rows - 40 squares from the top of the clock's roof to the lowest toe, not more (if your drawing came out bigger, draw it again smaller - never shrink it); about 27 squares wide; all squares 8x8 on one grid; at most 30 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both glowing eyes level and clearly visible; the pointed ear, the beard, the red stole, the gold buckle there; the clock whole with its roof, ivory face, turquoise numerals, gold rim, clock hand, both gears and the pendulum; both hands joined to the sleeves; the toes the lowest row and nothing below them.
VERSION A (zilean_design_A.png): the head from the top of the hair to the chin about 11 squares - the spiky hair crest about 4 squares above the brows, the face from the brows to the chin about 6 squares tall and 7 squares wide; each eye 2 squares wide and 2 tall: the top row part of the bushy blue brow, the bottom row the glowing eye - a pale cyan-white square beside a dark-navy pupil square; the beard about 6 squares below the chin, curling forward.
VERSION B (zilean_design_B.png): a bigger chibi head so the face reads at this small size - the head from the top of the hair to the chin about 13 squares, the hair crest about 4 squares, the face about 7 squares tall and 8 squares wide; each eye 2 squares wide and 2 tall as in version A; the beard about 5 squares below the chin; the robe 2 squares shorter so the whole figure is still 40 squares tall; the clothes, the arms and the clock the same as in version A.
```

## 交回前自查

- [ ] **数行数**：两版都是时钟屋顶到最低的脚趾正好 40 格（A 头约 11 格、脸 6×7；B 头约 13 格、脸 7×8）、宽约 27 格；最低的脚趾在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 30 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、亮点一个水平，不是大块平涂；
- [ ] 两只发光的眼睛在同一行、各 2×2（眉 + 眼）、看得清；淡青白只在眼睛上；尖耳朵、胡子、红披带、金腰扣都在；
- [ ] 宽袖子 3–4 格粗、掌心向上的手连着袖子；时钟完整（屋顶、钟面、数字、金齿框、时针、两个小齿轮、钟摆），在头和肩膀后面；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子；草稿放在 `zilean_design_sources/`。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛、手臂粗细，只补缺的描边。画大了就按整行整列删到 40 行（不删脸上的行）。也看草稿，草稿更好就用草稿。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
