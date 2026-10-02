# 布里茨：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`blitzcrank/blitzcrank_source.png`，你上一轮画的：英雄联盟的待机，两只大拳垂在身侧）在**游戏尺寸**重新画。两版只差头和眼睛：
> - **版本 A**：头照原画，圆顶（顶到领口）约 **7 格高、7 格宽**；两只眼睛各 **2×2 格**（左上一格白，其余三格浅粉）；
> - **版本 B**：头画大一点，圆顶约 **9 格高、9 格宽**，在两根烟囱之间稍微高出来一点；两只眼睛各 **3×3 格**（中间一格白，周围浅粉）；身体、手臂、脚和 A 一样。
>
> 其余两版都一样：
> - **大小**：从烟囱顶到脚底约 **44 格**，从左拳到右拳约 **46 格宽**（原画按 44 格高算是 50 格宽，所以两只拳头比原画稍微靠近身体一点）。脚底在第 99 行（y=792–799），两脚中间在中间那一列（x=512，蓝线）；大小和位置看 `blitzcrank/size_place.png`。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `blitzcrank/quality_bar.png` 里 main 分支的大块头英雄（石头人、诺手、蕾欧娜、塔里克、贾克斯，都是现在游戏里的样子，用户认可的）。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小会把细节弄碎）。`blitzcrank/size_guide.png` 是原画直接缩到 44 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 24 种。交付 `blitzcrank_design_A.png`、`blitzcrank_design_B.png`（1024×1024）和各自的原尺寸图 `blitzcrank_design_A_1x.png`、`blitzcrank_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板，最好打成一个 zip（`blitzcrank_design_pack.zip`，放在 outputs 里）。

## 附图（都在压缩包的 `blitzcrank/` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `blitzcrank_source.png` / `blitzcrank_source_white.png` | 用户选的原画 A（透明底 / 白底） | **长相**：金色锅炉大圆身子、胸口大钢圈炉门和闪电纹、金色圆顶小脑袋和两只粉白发光眼、钢领口、两根烟囱、黑色软管、带钢刺的肩块、巨大的方块手臂和拳头、短腿、大扁脚、颜色和姿势 |
| `size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（44 格高、46 格宽），红线 = 脚底线下沿，蓝线 = 中间列 | 只看大小和位置 |
| `quality_bar.png` | main 里 5 位大块头英雄（石头人 47 格、诺手 42、蕾欧娜 41、塔里克 40、贾克斯 36），游戏里现在的样子 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `face_ref.png` | 原画 A 的头，放大（396×265） | 圆顶、眼睛、领口、烟囱的样子 |
| `tfm2_style_big.png` | 团战经理2 原版的大块头和机器人（食人魔、机器人、大力士、持盾者、攻城者），×8 | 原版的像素画法：大身体、金属、大手在这个尺寸怎么画 |
| `size_guide.png` | 原画直接缩到 44 格，同一画布、同一脚底线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：烟囱顶到脚底约 44 格、拳到拳约 46 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：头重脚轻的大蒸汽机器人：锅炉大圆身子占了大部分高度，短腿，大扁脚分开站；两条巨大的手臂垂在身体两侧，大拳头垂到膝盖高度（比原画稍微靠近身体一点）。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色：金色的暗部是棕金，钢的暗部是蓝灰），**不要在描边里再画第二圈黑**（黑色只用于描边和软管最暗的一档）；每个小方块都在画东西（铆钉、螺丝头、钢刺、手臂方块之间的缝、指节螺栓、软管的箍、闪电纹），不要随手撒的杂点，不要抖动、渐变、噪点；最多 24 色。
- **材质**：金黄 4 档（身体、头、肩、手臂、拳头、脚）+ 锈色 1 档；枪灰钢 3 档（炉门钢圈、领口、烟囱、腿、关节）；黑灰软管 2 档；银色钢刺、螺丝、指节螺栓 2 档；眼睛的浅粉和白。
- **脸（最重要的细节）**：照 `face_ref.png`：两只眼睛都看得见、**并排在同一行**，大小按两版各自的要求，各在一个深色眼窝里，两眼之间隔一格金色；**眼睛的浅粉和白不用在别的地方**；圆顶中间那道竖棱在两眼之间或上面；领口在圆顶下面；手和软管都不能挡住眼睛。
- **拳头和手臂**：每只拳头至少 9 格高、8 格宽，手指是 3 块叠着的方块，侧面 2–3 个钢指节螺栓；每条手臂是 2–3 块大金色方块，块之间有深色缝和几个钢螺丝，连着肩块和拳头（有描边），不能是飘着的拳头或细胳膊；近处的拳头在近处的腿前面一点，远处的拳头在远侧；两只拳头最低一行都至少在脚底线上方 2 格。
- **胸口炉门**：钢圈直径约 12 格、2 格粗，里面是青铜金色圆盘和深色闪电纹，在两条手臂之间清楚露出来。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：两只脚底在同一行，就是第 99 行，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`blitzcrank_design_A.png` 和 `blitzcrank_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`blitzcrank/blitzcrank_source.png`、`blitzcrank/size_place.png`、`blitzcrank/quality_bar.png`、`blitzcrank/face_ref.png`；`blitzcrank/tfm2_style_big.png` 和 `blitzcrank/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the huge round gold steam-boiler body with the big round chest port (a thick steel ring round a bronze-gold disc with a zigzag lightning seam), the small gold dome head with two glowing pale pink-white eyes sitting low in a steel collar, the two steel smokestacks behind the head, the black ribbed hoses, the spiked gold shoulder blocks, the enormous blocky gold arms and fists with steel screws, the short dark piston legs and the big flat gold feet with riveted rims, the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas. THIRD: five big heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head, big - the dome, the eyes, the collar and the smokestacks to copy. (Optional: official heroes of the game at 8x - a big ogre, an android robot, a strongman, a shield bearer and a siege breaker - for the pixel style and how big bodies, metal and huge hands are drawn at this size; and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 44 pixels from the top of the smokestacks to the soles and about 46 pixels wide from fist to fist, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: a huge top-heavy steam robot - the round boiler body takes most of his height, short legs, big flat feet apart, two enormous arms hanging at his sides with the giant fists down at about knee height (the fists a little closer to the body than in the FIRST image, to fit the width); the head as big as the VERSION lines at the end say (two images).
The character: Blitzcrank, the great steam golem: a huge round, egg-shaped GOLD-YELLOW boiler body (warm ochre gold, deeper brown-gold shading, a few small rust patches and rivet dots); on the chest and belly a LARGE ROUND PORT - a thick gunmetal STEEL ring round a bronze-gold disc with a zigzag LIGHTNING-BOLT seam across it; a small rounded GOLD DOME head with one raised ridge down its middle, sitting low and forward between the shoulders in a thick steel collar, a dark ribbed neck under it; two round GLOWING EYES side by side on the front of the dome, pale pink-white with a white centre, in dark sockets; no mouth, no nose, no hair; two short steel SMOKESTACKS (cones with gold-rimmed open tops) rising behind the head - their tops are the highest point of the sprite; big blocky GOLD SHOULDER blocks with small silver pyramid spikes; thick BLACK ribbed rubber HOSES looping from the back over the shoulders into the arms; ENORMOUS arms made of chunky stacked gold blocks with dark seams and steel screw heads; giant blocky FISTS whose fingers are square gold blocks with steel knuckle bolts; short dark steel piston legs with round joints; big flat GOLD FEET like plough plates with a row of rivets along the rim.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 24 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks: brown-gold for the gold, blue-grey for the steel - black is only the outline and the hoses' darkest shade; never a second black ring inside the outline); every square describes something (a rivet, a screw head, a spike, a seam between two arm blocks, a knuckle bolt, a band of a hose, the lightning seam) - no random specks, no dithering, no gradients, no noise.
Colours: gold-yellow in 4 shades (body, dome, shoulders, arms, fists, feet) and 1 rust; gunmetal steel in 3 (the port's ring, the collar, the smokestacks, the legs, the joints); black-grey hoses in 2; silver spikes, screws and knuckle bolts in 2; the eyes' pale pink and white.
Face (most important detail), as the FOURTH image: both eyes visible, side by side on the SAME rows, the sizes the VERSION lines say, each in a dark socket, with one square of gold dome between them; the eye colours (pale pink, white) are used NOWHERE else; the dome's middle ridge between or above the eyes; the collar under the dome; neither hand nor hose covers the eyes.
Fists and arms: each fist at least 9 squares tall and 8 wide, its fingers 3 stacked square blocks with 2-3 steel knuckle bolts on the side; each arm 2-3 big gold blocks with dark seams and a few steel screws, joined to the shoulder block and to the fist with the outline - no floating fists, no thin arms; the near fist a little in front of the near leg, the far fist at the far side; the lowest row of both fists at least 2 squares above the soles.
Chest port: the steel ring about 12 squares across, 2 squares thick, the bronze disc inside with a dark zigzag seam; it shows clearly between the arms.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: both soles' lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the middle between his feet on the middle column (x=512). Nothing below the soles (the game draws the health bar right under the feet).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 44 squares from the top of the smokestacks to the soles and about 46 from fist to fist; all squares 8x8 on one grid; at most 24 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both eyes level and clearly visible; the eye colours only in the eyes; the round chest port clear; both fists whole and above the soles; nothing below the soles.
VERSION A (blitzcrank_design_A.png): the FIRST image's head - the dome (its top to the collar) about 7 squares tall and 7 wide; each eye 2x2 squares (a white square at the top left, pale pink in the other three).
VERSION B (blitzcrank_design_B.png): a bigger head so the face reads at this small size - the dome about 9 squares tall and 9 wide, rising a little higher between the smokestacks; each eye 3x3 squares (a white centre square, pale pink round it); the body, the arms and the feet the same as in version A.
```

## 交回前自查

- [ ] 两版都是烟囱顶到脚底约 44 格、拳到拳约 46 格（A 圆顶约 7 格，B 约 9 格）；脚底最低一行在第 99 行，下面没有像素；两脚中间在 x=512；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 24 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块平涂；
- [ ] 两只眼睛并排在同一行、看得清（A：各 2×2；B：各 3×3）；眼睛的颜色只在眼睛上；
- [ ] 胸口钢圈炉门清楚；两只拳头完整、在脚底线上方，连着手臂；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛，只补缺的描边。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
