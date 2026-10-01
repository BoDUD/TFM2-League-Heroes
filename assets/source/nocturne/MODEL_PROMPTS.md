# 魔腾：按游戏尺寸画造型（第 1 步，给 Codex 的提示词）

> **这一轮只画造型图，不画动作，画 A、B 两版给用户挑。** 照用户选的原画 A（`nocturne/nocturne_source.png`，你上一轮画的：英雄联盟的待机，弓身浮空、双拳在前、刀刃后扫、烟雾尾巴）在**游戏尺寸**重新画。两版只差头的大小和尾巴长短：
> - **版本 A**：头照原画，头骨（头冠根部到下巴）约 **9 格**，脸夹在两块肩甲之间约 **5 格宽**；两只眼睛各 **2 格宽、1 格高**的纯白细缝，外端高一格（上挑）；尾巴（腰布下沿到尾尖）约 **14 格**；
> - **版本 B**：头画大一点，头骨约 **11 格**、脸约 **7 格宽**，比肩甲稍微高出来；两只眼睛各 **2×2 格**纯白（外端上方一格深色眉）；尾巴短 3 格（约 11 格），总高还是 44 格；肩甲、拳头、刀、腰布和 A 一样。
>
> 其余两版都一样：
> - **大小**：从头冠尖到尾巴尖约 **44 格**，从刀到刀约 **32 格宽**（原画按 44 格高算出来的宽度）。尾巴尖在第 99 行（y=792–799）、在中间那一列（x=512，蓝线）；大小和位置看 `nocturne/size_place.png`。为什么是 44 格不是 40：他三分之一的高度是一条细尾巴，44 格时的像素面积（约 720）才和阿卡丽、李青、萨科差不多，40 格会是全包最小的。
> - **最重要：不糊、细节好**。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色；细节多而清楚，像 `nocturne/quality_bar.png` 里 main 分支的英雄（萨科、维迦、锤石、贾克斯、迦娜，都是现在游戏里的样子，用户认可的）。**他的身体很暗，所以要有亮边**：头骨、头冠、肩甲下的肩、拳头、尾巴转弯处描一道亮一点的蓝，暗色底上也看得清。
> - **直接按游戏尺寸画**，不要先画大再缩小（缩小会把细节弄碎）。`nocturne/size_guide.png` 是原画直接缩到 44 格的样子，只用来看这个尺寸能放下什么、各部分在哪，颜色和形状都是糊的，不要照它。
> - 原稿通常不在严格网格上（方块 7.4–8.6 px）。**交回前请整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 26 种。交付 `nocturne_design_A.png`、`nocturne_design_B.png`（1024×1024）和各自的原尺寸图 `nocturne_design_A_1x.png`、`nocturne_design_B_1x.png`，附 `HANDOFF.md`（用了哪段提示词、哪里没做到）和色板，最好打成一个 zip（`nocturne_design_pack.zip`，放在 outputs 里）。

## 附图（都在压缩包的 `nocturne/` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `nocturne_source.png` / `nocturne_source_white.png` | 用户选的原画 A（透明底 / 白底） | **长相**：深靛蓝暗影身体、向后扫的尖头冠、发白光的细眼、两块大圆肩甲（银灰钢板、暗紫内层、蓝紫圆环符文、钢刺）、带刺护手和灰色缠布、大拳头、前臂外侧的红银弯刃、红色腰布和圆环纹章、烟雾尾巴、颜色和姿势 |
| `size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 他的大小和位置（44 格高、32 格宽），红线 = 尾巴尖那一行的下沿，蓝线 = 尾巴尖所在的列 | 只看大小和位置 |
| `quality_bar.png` | main 里 5 位英雄（萨科 43 格、维迦 40、锤石 40、贾克斯 36、迦娜 45 —— 迦娜也是浮空的），游戏里现在的样子 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `face_ref.png` | 原画 A 的头、头冠和肩甲，放大（906×613） | 脸、眼睛、头冠、肩甲上的符文和刺 |
| `tfm2_style_dark.png` | 团战经理2 原版的暗色和幽灵类英雄（紫色梦魇、浮空的守护灵、幽灵、暗影法师、恶魔），×8 | 原版的像素画法：暗色身体、发光眼睛、浮空的身形在这个尺寸怎么画 |
| `size_guide.png` | 原画直接缩到 44 格，同一画布、同一尾尖线 | 只看能放下什么，不要照它的颜色和形状 |

## 规则

- **像素尺寸（最重要）**：头冠尖到尾巴尖约 44 格、刀到刀约 32 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例照原画**：弓着身子、头重脚轻的浮空身形：两块大肩甲是身体最宽的地方，头压在中间，双拳在胸前，红刀向后扫过手肘，腰布在拳头下面，烟雾尾巴越往下越细、卷成一个尖。
- **细节和明暗照 main 的英雄**：一圈 1 格的近黑描边，描边里每种材质有自己的暗、中、亮和一点高光（暗部带颜色：身体的暗部是深靛，钢的暗部是紫灰，红的暗部是酒红），**不要在描边里再画第二圈黑**（黑色只用于描边）；每个小方块都在画东西（钢刺、甲片边、符文圆环、指节、缠布、刀上的花纹、倒钩、腰布褶、烟雾的转折），不要随手撒的杂点，不要抖动、渐变、噪点；最多 26 色。
- **颜色**：靛蓝身体和尾巴 4 档（尾巴最下面用最暗的紫靛）；银灰钢 4 档（肩甲、护手、刺、刀刃边和花纹）；暗紫肩甲内层 2 档；红色 3 档（刀、腰布）；符文的蓝紫和它的淡蓝高光；眼睛的纯白。**纯白只用在眼睛上**（钢的高光用浅灰，符文的高光用淡蓝）。
- **脸（最重要的细节）**：照 `face_ref.png`：两只眼睛都看得见、**在同一行**，大小按两版各自的要求，纯白、外端上挑一格，每只上面一格深色眉；两眼之间露出靛蓝的头骨；**没有嘴**，眼睛下面不要有像嘴的深色方块；下巴是窄尖；拳头和肩甲都不能挡住眼睛。
- **拳头、护手和刀**：每只拳头至少 4×4 格，连着护手，护手连着肩甲下的手臂（有描边），不能是飘着的拳头；每把刀最宽处至少 3 格，银边 1 格，刀尖是 3–5 格的 1 格细线；刀都在尾尖那一行以上结束。
- **尾巴**：从腰布下面 3–4 格宽开始，越往下越细，尾尖 1–2 格；两三缕烟丝**连在尾巴上**（不能有飘着的碎块）；尾尖是整个精灵最低的一格。
- **尾尖以下什么都不能有**（游戏在脚下画血条）：尾尖在第 99 行、在中间那一列，下面一格都不能有。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`nocturne_design_A.png` 和 `nocturne_design_B.png`（同一段提示词，两版各按最后的 VERSION 那一行画）

附图：`nocturne/nocturne_source.png`、`nocturne/size_place.png`、`nocturne/quality_bar.png`、`nocturne/face_ref.png`；`nocturne/tfm2_style_dark.png` 和 `nocturne/size_guide.png` 可以一起附上。

```text
Attached images. FIRST: the approved illustration of this character - copy his look: the dark navy-indigo shadow body, the long hairless skull with the tall fin crest sweeping back, the two narrow glowing white eyes under a heavy brow, no mouth; the two HUGE rounded pauldrons (layered silver-grey steel plates, mauve-purple inner panels, a glowing blue-violet ring rune on top, short sharp steel spikes along the rims); the steel gauntlets with spikes and grey wrappings; the big navy fists held forward; the crimson-and-silver curved blades growing from the outside of both forearms; the crimson tabard with silver trim and a ring emblem; the smoke tail instead of legs; the colours and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for his size and his place in the canvas. THIRD: five heroes of this game at game size as they are in the game now, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents. FOURTH: the FIRST image's head, crest and pauldrons, big - the face, the eyes, the crest and the pauldron details to copy. (Optional: official heroes of the game at 8x - dark and ghostly figures: a purple wraith, a floating guardian spirit, a ghost, a shadow mage and a demon - for how dark bodies, glowing eyes and floating figures are drawn at this size; and a straight shrink of the FIRST image to game size - use that one ONLY to see what fits; it is blurry, do not copy its look.)
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 44 pixels from the tip of the crest to the tip of the smoke tail and about 32 pixels wide from blade to blade, drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Proportions: the FIRST image's - a hunched, top-heavy floating figure: the two huge pauldrons are the widest part of the body, the head sits low between them, the fists are forward at chest height, the crimson blades sweep back past the elbows, the tabard hangs below the fists and the smoke tail narrows and curls down to a point; the head as big as the VERSION lines at the end say (two images).
The character: Nocturne, a living shadow in spiked armour: a long bare skull of dark NAVY-INDIGO shadow-flesh with a few groove lines, a tall pointed FIN CREST rising from the top of the skull and sweeping back to the left; two narrow slanted EYES glowing pure WHITE under a dark heavy brow, NO mouth, a narrow pointed chin; two HUGE ROUNDED PAULDRONS of layered silver-grey steel plates with mauve-purple inner panels, each with a ring rune on top (a small ring of blue-violet with a pale-blue highlight and a dark centre) and 3-4 short sharp steel spikes along its rim; a dark steel collar; steel GAUNTLETS with 2 short spikes and grey wrappings round the wrists; big navy FISTS; a huge curved BLADE on the outside of each forearm - a broad crimson blade with silver-white edges, a wavy silver flame inlay, a hooked barb at the back and a long thin silver point; the near blade (image left) sweeps back and down past his near side, the far blade (image right) hangs down behind his far fist; a CRIMSON TABARD from the belt down with a silver trim, a small silver ring emblem and a jagged lower edge; below it NO LEGS: a dark navy-violet SMOKE TAIL that narrows and curls down to a point, with two or three short wisps curling off it.
CRISP, NOT BLURRY, WITH GOOD DETAIL - every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob. His body is dark, so it needs LIT EDGES: a lighter navy-blue rim on the skull, the crest, the shoulders under the pauldrons, the fists and the tail's turns, so the dark shapes still read on a dark background.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 26 colours; ONE 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks: deep indigo for the navy body, purple-grey for the steel, dark wine for the crimson - black is only the outline; never a second black ring inside the outline); every square describes something (a spike, a plate edge, a rune ring, a knuckle, a wrapping band, a blade inlay, a barb, a tabard fold, a turn of the smoke) - no random specks, no dithering, no gradients, no noise.
Colours: navy-indigo body and tail in 4 shades (the tail's lowest part in the darkest violet-navy); silver-grey steel in 4 (pauldron plates, gauntlets, spikes, blade edges and inlays); mauve-purple pauldron panels in 2; crimson in 3 (blades, tabard); the rune's blue-violet and its pale-blue highlight; the eyes' pure white. Pure white is used ONLY in the eyes (highlights on the steel are light grey, the rune's highlight is pale blue).
Face (most important detail), as the FOURTH image: both eyes visible, on the SAME row, the sizes the VERSION lines say, glowing pure white, slanted (the outer ends one square higher), a dark brow square above each; the skull's navy shows between them; no mouth, no nose line, no dark square under the eyes that reads as a mouth; the chin a narrow point; neither fist nor pauldron covers the eyes.
Fists, gauntlets and blades: each fist at least 4 squares wide and 4 tall, joined to its gauntlet and the gauntlet to the arm under the pauldron (with the outline) - no floating fists; each blade at least 3 squares thick at its widest, its silver edge one square, its point a 1-square line of 3-5 squares; the blades end above the tail's tip row.
Tail: it starts under the tabard 3-4 squares wide and narrows to a 1-2 square point; its wisps are joined to the tail (no loose pieces); its tip is the lowest square of the sprite.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: the tail tip's lowest row at y=792-799 (square row 99, 28 squares above the bottom of the image), the tail tip on the middle column (x=512). Nothing below the tail tip (the game draws the health bar right under it).
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 44 squares from the crest tip to the tail tip and about 32 from blade to blade; all squares 8x8 on one grid; at most 26 colours; one outline ring only; the detail and shading of the THIRD image, not flat areas; both eyes level and clearly visible; pure white only in the eyes; both fists and both blades whole and joined; the tail tip the lowest square and nothing below it.
VERSION A (nocturne_design_A.png): the FIRST image's head - the skull from the crest's base to the chin about 9 squares, the face about 5 squares wide between the pauldrons; each eye 2 squares wide and 1 tall (pure white), the outer end of each eye one square higher; the tail about 14 squares from the tabard's lower edge to its tip.
VERSION B (nocturne_design_B.png): a bigger head so the face reads at this small size - the skull from the crest's base to the chin about 11 squares and the face about 7 squares wide, rising a little higher above the pauldrons; each eye 2 squares wide and 2 tall (pure white, a dark brow square over the outer end); the tail 3 squares shorter (about 11) so the whole figure is still 44 squares tall; the pauldrons, the fists, the blades and the tabard the same as in version A.
```

## 交回前自查

- [ ] 两版都是头冠尖到尾巴尖约 44 格、刀到刀约 32 格（A 头骨约 9 格、尾巴约 14 格；B 头骨约 11 格、尾巴约 11 格）；尾尖最低一行在第 99 行、在 x=512，下面没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 26 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、亮边一个水平，不是大块平涂，暗色身体在暗底上也看得清；
- [ ] 两只白眼睛在同一行、看得清（A：各 2×1；B：各 2×2）；纯白只在眼睛上；没有嘴；
- [ ] 两块大肩甲有钢刺和符文圆环；两只拳头、两把刀完整并连着手臂；尾巴的烟丝连在尾巴上；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（`regrid.py`：颜色变化定格子边界，每格取中心的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、尾尖线、眼睛，只补缺的描边。
- A、B 两版和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户挑；通过后出动作帧包（第 2 步）。
