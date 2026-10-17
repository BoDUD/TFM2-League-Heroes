> 娜美造型的第一步（第三轮交给 Codex 的原样提示词在下面）。Codex 的交付在 `codex_model/`（A、B 的 1 倍和 8 倍图、`HANDOFF.md`、`manifest.json`、`generation_prompts.json`）；Claude 用 `tools/art/design_nami.py` 把 A 整理成游戏里的造型 `assets/source/native/nami_native.png`（每次都能逐字节重建）。
>
> - **第一轮**（约 80 格，游戏尺寸的 1.7 倍，A 头约 1/4、B 头约 1/3、B 的尾巴要求卷紧）：Codex 把尾巴画短了（B 成了 J 形钩），用户："尾巴最好还原一下吧"。把原图的尾巴描上去、再缩到游戏尺寸，用户："都不满意 看起来太奇怪了"，"主要是要不模糊细节好"——缩小会把细节切碎。
> - **第三轮**（照 main 上卢锡安重做的做法，由薇恩会话转达："照main分支成功的方式重做造型包"）：直接在游戏尺寸画，不再缩小。Codex 的 A 画成了 42×64（要求约 50），B 60×87；A 清楚（右邻同色 38%，20 色）、尾巴照原图，用户选 A。
> - **脸**（用户："用A修一下脸部 太奇怪了"、"怎么方形的脸？"）：Codex 的脸是一块 8×7 的直边方块。四个方案里用户选 **D**：近侧脸颊从第 48 行起挡在一缕头发后面，远侧脸颊斜着收到尖下巴，下巴下面一行阴影；眼睛 2×2，左上一格白色高光、其余琥珀色（莫甘娜过审的画法，琥珀色 `#F2B233` 只用在眼睛上），各有一行睫毛；一格深红色的嘴在中线上；远侧脸颊和刘海下面加皮肤暗色。
> - **大小**（用户："体型还是太大 能不能尽量和别的英雄一个尺寸"）：整体按行列删减（每组删和邻行最像的一行，不混色），脸的行列和法杖那一列不删，用户选 **W**：36×50，面积 918，和迦娜一样；鱼鳍里原来用皮肤色的浅色格换成原图的淡黄绿 `#E8E6A8`。21 色，最低一行在第 96 行方块（比脚底第 99 行高 3 格，和迦娜一样飘着）。

# 唤潮鲛姬 娜美：按用户的图在游戏尺寸画造型（给 Codex，第三版）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户确认后，下一轮再按它画动作。
> - 照 `nami_source.png` 画：娜美的长相、王冠、头发、服装、颜色、法杖、姿势，特别是**长长的鱼尾和大鱼鳍**都照它来。
> - **这次直接画游戏尺寸**（王冠顶到尾巴最低点约 50 格，法杖顶再高约 4 格），8 倍放大，每个像素一个 8×8 方块。第一轮画成了约 1.7 倍（80 格），Claude 缩小后细节都糊了，用户要细节清楚、不模糊，所以这次不再缩小：**你画的每一格就是游戏里的一个像素**。
> - 这就是卢锡安重做那次成功的做法（直接在游戏尺寸画，Claude 只按格子读回像素）。
> - 第一轮的问题（用户看过）：尾巴被画短、卷成一团（要照原图：往下、向右弯出，再甩向左下，接一个和上半身差不多大的扇形鱼鳍）；头发太大（这次 3–4 束粗发，不超过全宽的三分之一）。
> - 交回时附 `HANDOFF.md`（用了哪段提示词、颜色表、没做到的地方）和 `manifest.json`（尺寸、最低一行、站位点、不透明区域、眼睛琥珀色的中心、颜色数）。文件名 `nami_design_A.png`、`nami_design_B.png`，最好打成一个 zip。

## 附图（都在压缩包里）

| 文件 | 内容 | 用法 |
|---|---|---|
| `nami_source.png` / `nami_source_white.png` | 用户给的造型图（透明底 / 白底） | **照它画**：脸、橘红长发、金冠和蓝宝石、淡海绿皮肤、深蓝胸衣、金腰带和金带、护腕、青绿鱼尾和大鱼鳍、腰鳍、法杖、姿势 |
| `tfm2_style_ref_support.png` | 团战经理2 原版的 8 个辅助和法师，8 倍 | 像素大小、干净程度、脸的画法 |
| `size_ref_janna.png` | 本包迦娜的游戏造型（约 46 格高，同样是飘着的），8 倍，1024×1024 | 只看**大小、脚底线和飘起的高度**（脚底线是第 99 行方块，y = 792–799，红线；她飘在上面 3 格），不要照她的样子 |
| `nami_size_guide.png` | 用户的图直接缩到游戏尺寸（王冠到尾巴 50 格），8 倍，同一张画布、同一条脚底线 | 只看**这个尺寸能放下多少、各部分在哪**；颜色和形状都是糊的，不要照它 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，8 倍 | 干净程度：大块平涂、颜色少、形状清楚 |

## 规则（含之前的英雄学到的）

- **游戏尺寸**：王冠顶到尾巴最低点约 50 格（法杖顶再高约 4 格），真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净**：最多 24 种颜色；每种材质 2–3 个平涂色阶（皮肤、头发、金、蓝宝石、深蓝胸衣和法杖杆、青绿尾巴、淡色鱼鳍）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块，头发里不能有洞。
- **只有一圈描边**：整个剪影外面一圈 1 格宽的近黑描边；描边里面的边缘、褶皱、发束之间、鳞片和鳍骨用那种材质自己最暗的色阶，**不要再画第二圈黑**。
- **脸**（最重要）：A 头（王冠顶到下巴）至少 11 格高，B 约 15 格；两只眼睛都看得见、一样大、在同一行：每只 2 格宽 2 格高（上行一格白色高光 + 一格深色瞳孔，下行琥珀色），上面各一行深色睫毛；两眼之间 2 格皮肤，近处眼睛（画面左边，她朝右）前面留一列脸颊；琥珀色**只用在眼睛上**；一格深红色的嘴在脸中线上、眼睛下面两行；脸颊、下巴不要别的深色格（之前的英雄出现过下巴两角的阴影连成歪嘴笑）；头直接坐在肩上，脖子很短。
- **尾巴照原图**：从金腰带（前面一个旋涡，两条金带搭在尾巴上）往下、向右弯出，再弯回、甩向**左下**，接一个和上半身差不多大的扇形鱼鳍（淡黄绿色，3–4 根深蓝鳍骨，深蓝边，三个参差的鳍尖）；尾巴青绿色，正面一条亮带，3–4 排鳞纹（短的浅色弧）；腰两侧各一片带褶的小青色腰鳍。
- **法杖**：杆是一条 1 格宽的深蓝直线（像原版弓箭手那样细），2 格的金环；顶上金色新月包着 3×3 的蓝宝珠（带白色高光），旁边青色鳍片，杖头至少 7×8 格；底端小小的金色枪尖；杆从王冠上方一直到约尾巴最低点，**一条不断的线**。
- **头发**：3–4 束粗的橘红波浪发束往左后方飘，束与束之间用深红色，不盖住脸，总宽不超过全身宽度的三分之一。
- **飘着**（人鱼没有脚，像迦娜）：脚底线是第 99 行方块（y 792–799）；她最低的像素比它高 3 格（最低一行 y 768–775），第 99 行和下面**什么都不能有**，鱼鳍和法杖尖也不行（游戏在脚下画血条）。腰（尾巴开始的地方）在中间那列（x 512）。
- 3/4 正面朝右（照原图），不画背影。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，就不提名字，只保留外观描述（下面的提示词里已经没有名字）。

## 提示词（A、B 各生成一张，只把 Face 里 [HEAD] 那句换成对应的一版）

### 方案 A：`nami_design_A.png`

```text
Four attached images. FIRST: the look of this character - copy her face, crown, hair, clothes, colors, staff, pose and above all her long fish TAIL and big fin from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size, cleanliness and their way of drawing faces. THIRD: another floating hero of this game's pack at game size, 8x - use it ONLY for the size, the ground line and how high she floats over it. FOURTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: about 50 pixels from the top of her crown to the lowest point of her tail (the staff's top about 4 more), true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine texture.
The character: a young mermaid sea-sorceress. Red-orange hair in 3-4 thick wavy locks flowing behind her to the left, dark red between the locks, never over her face, the hair not wider than a third of the whole figure. A golden crown: a tall central spike, two side spikes and a round blue gem on the front, a small teal fin like an ear on each side. Pale sea-green skin. A deep-blue bikini top with gold trim; bare arms with gold bracers (a blue gem on each). A gold belt with a gold spiral in front and two gold straps running down over the top of the tail. NO legs: the TAIL exactly like the FIRST image - from the belt it runs down and bows out to the right, then curves back and sweeps to the LOWER LEFT into a big fan-shaped fin as big as her upper body: pale yellow-green with 3-4 deep-blue ribs and a deep-blue edge, three ragged tips; the tail teal-green with a lighter band down its front and 3-4 rows of scale marks (short light arcs); two small frilled teal fins at her hips. In her far hand (right of the image) a long staff held upright: a straight deep-blue shaft one square wide with 2-square gold rings (thin like the base archer's bow), on top a gold crescent round a glowing blue orb (3x3 squares with a white highlight) with teal fins beside it - the staff's head at least 7x8 squares - and a small gold spear tip at the bottom; the shaft runs from above her crown down to about the tail's lowest point.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (skin, hair, gold, blue gems, deep-blue top and shaft, teal tail, pale fin); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area, no holes in the hair. ONE 1-square near-black outline around the whole silhouette only: inside it, edges, folds, the gaps between locks, scales and ribs use the material's own darkest shade - never a second ring of black inside the outline.
Face (most important detail): A: the FIRST image's slender body and long tail, only the head bigger than in the FIRST image so the face reads: the head (crown top to chin) at least 11 squares tall; both eyes visible, the same size and on the same rows: each eye 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row amber - with a dark lash row over each eye; 2 squares of skin between the eyes and one cheek column before the near eye (left, she faces right); the amber is used NOWHERE else (hair and gold are other colors); one dark-red mouth square on the face's middle line two rows under the eyes; no other dark squares on the cheeks or the jaw (a shadow joining the jaw corners to the chin reads as a grin); the head sits on her shoulders with a short neck.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, upright upper body, the near arm (left of the image) held out and down with an open hand, the far hand holding the staff. She floats like the THIRD image: the ground line is block row 99 (y 792-799) of the image; her lowest pixel is 3 squares ABOVE it (the lowest drawn row y 768-775) and NOTHING is on or below row 99 - neither the fin nor the staff's tip (the game draws the health bar there). Her hips (where the tail starts) on the middle column (x 512).
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 50 squares from the crown to the tail's lowest point with the long S tail and the big fin at the lower left; every square 8x8 on one grid; at most 24 colors; both eyes 2x2, level and visible, the amber only in the eyes; the outline one square wide everywhere with no black ring inside it; the staff's shaft one unbroken line; nothing on or below row 99.
```

### 方案 B：`nami_design_B.png`

```text
Four attached images. FIRST: the look of this character - copy her face, crown, hair, clothes, colors, staff, pose and above all her long fish TAIL and big fin from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size, cleanliness and their way of drawing faces. THIRD: another floating hero of this game's pack at game size, 8x - use it ONLY for the size, the ground line and how high she floats over it. FOURTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: about 50 pixels from the top of her crown to the lowest point of her tail (the staff's top about 4 more), true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine texture.
The character: a young mermaid sea-sorceress. Red-orange hair in 3-4 thick wavy locks flowing behind her to the left, dark red between the locks, never over her face, the hair not wider than a third of the whole figure. A golden crown: a tall central spike, two side spikes and a round blue gem on the front, a small teal fin like an ear on each side. Pale sea-green skin. A deep-blue bikini top with gold trim; bare arms with gold bracers (a blue gem on each). A gold belt with a gold spiral in front and two gold straps running down over the top of the tail. NO legs: the TAIL exactly like the FIRST image - from the belt it runs down and bows out to the right, then curves back and sweeps to the LOWER LEFT into a big fan-shaped fin as big as her upper body: pale yellow-green with 3-4 deep-blue ribs and a deep-blue edge, three ragged tips; the tail teal-green with a lighter band down its front and 3-4 rows of scale marks (short light arcs); two small frilled teal fins at her hips. In her far hand (right of the image) a long staff held upright: a straight deep-blue shaft one square wide with 2-square gold rings (thin like the base archer's bow), on top a gold crescent round a glowing blue orb (3x3 squares with a white highlight) with teal fins beside it - the staff's head at least 7x8 squares - and a small gold spear tip at the bottom; the shaft runs from above her crown down to about the tail's lowest point.
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (skin, hair, gold, blue gems, deep-blue top and shaft, teal tail, pale fin); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area, no holes in the hair. ONE 1-square near-black outline around the whole silhouette only: inside it, edges, folds, the gaps between locks, scales and ribs use the material's own darkest shade - never a second ring of black inside the outline.
Face (most important detail): B: the base game's chibi head and short torso: the head (crown top to chin) about 15 squares tall; the same long tail, fin, hair and staff as A; both eyes visible, the same size and on the same rows: each eye 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row amber - with a dark lash row over each eye; 2 squares of skin between the eyes and one cheek column before the near eye (left, she faces right); the amber is used NOWHERE else (hair and gold are other colors); one dark-red mouth square on the face's middle line two rows under the eyes; no other dark squares on the cheeks or the jaw (a shadow joining the jaw corners to the chin reads as a grin); the head sits on her shoulders with a short neck.
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, upright upper body, the near arm (left of the image) held out and down with an open hand, the far hand holding the staff. She floats like the THIRD image: the ground line is block row 99 (y 792-799) of the image; her lowest pixel is 3 squares ABOVE it (the lowest drawn row y 768-775) and NOTHING is on or below row 99 - neither the fin nor the staff's tip (the game draws the health bar there). Her hips (where the tail starts) on the middle column (x 512).
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 50 squares from the crown to the tail's lowest point with the long S tail and the big fin at the lower left; every square 8x8 on one grid; at most 24 colors; both eyes 2x2, level and visible, the amber only in the eyes; the outline one square wide everywhere with no black ring inside it; the staff's shaft one unbroken line; nothing on or below row 99.
```

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（颜色变化的峰值定格子边界，每格取中心 3×3 的中位色），**不缩小**；压色板到 24 色以内，只留一圈描边，琥珀色只用在眼睛；手修脸（两眼同高同大、嘴在中线）；右邻同色比例、颜色数和原版英雄比。游戏尺寸预览（和原版辅助、包里英雄比大小，在对战场地色和深色头像卡上各看一遍）给用户挑 A/B。
