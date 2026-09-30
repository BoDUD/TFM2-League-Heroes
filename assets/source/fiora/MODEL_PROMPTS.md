# 无双剑姬 菲奥娜：按用户选的图在游戏尺寸画造型（给 Codex，第 1 步）

> **这一轮只画造型图（A、B 两版），不画动作。** 用户确认后，下一轮再按它画动作（待机、移动、普攻、夺命连刺的暴击、Q 破空斩、W 劳伦特心眼刀、R 无双挑战、受击、死亡）。
> - 照 `fiora_source.png`（用户选的 A 图：起手式，细剑平举向右）画：剑姬的长相、深靛紫波波头和深红刘海、白衣金甲、青绿紧身裤和靴子、酒红披风、细剑和站姿。
> - **直接画游戏尺寸**（头顶到鞋底约 39 格），8 倍放大，每个像素一个 8×8 方块。你画的每一格就是游戏里的一个像素，Claude 只按格子读回，不再缩小（这是卢锡安、薇恩成功的做法；先画大再缩会把细节缩成碎点）。
> - 交回时附 `HANDOFF.md`（用了哪段提示词、颜色表、没做到的地方）和 `manifest.json`（尺寸、鞋底行、站位点、不透明区域、眼睛青色的中心、颜色数）。文件名 `fiora_design_A.png`、`fiora_design_B.png`，最好打成一个 zip（放在 outputs 里）。

## 附图（都在压缩包里）

| 文件 | 内容 | 用法 |
|---|---|---|
| `fiora_source.png` / `fiora_source_white.png` | 用户选的设定图 A（透明底 / 白底） | **照它画**：脸、发型、服装、颜色、披风、细剑、起手式 |
| `tfm2_style_ref_melee.png` | 团战经理2 原版的 8 个近战英雄，8 倍 | 像素大小、干净程度、脸的画法（女骑士、魔剑士的剑，枪兵的细长枪） |
| `pack_quality_ref.png` | 本包已有的女英雄（锐雯、薇恩、阿卡丽、阿狸、厄运小姐）游戏造型，8 倍 | **要达到的质量**：小细节清楚，不糊 |
| `size_ref_riven.png` | 本包锐雯的游戏造型（40 格高），8 倍，1024×1024 | 只看**大小和脚底线**（鞋底在第 99 行方块，y = 792–799，红线上面），不要照她的样子 |
| `fiora_size_guide.png` | 图 A 直接缩到游戏尺寸（头顶到鞋底 39 格，约 63 格宽），8 倍，同一张画布、同一条脚底线 | 只看**这个尺寸能放下多少、各部分在哪**（身体在左半边，细剑伸向右边）；颜色和形状都是糊的，不要照它 |

## 规则（含之前的英雄学到的）

- **游戏尺寸**：头顶到鞋底约 39 格，真正的低分辨率像素画放大 8 倍：每个像素一个 8×8 的纯色方块，全部对齐同一个 8 px 网格，没有比一格小的东西，没有抗锯齿、模糊、柔光、半透明。
- **干净**：最多 24 种颜色；每种材质 2–3 个平涂色阶（靛紫头发、深红刘海、皮肤、白布、金、天蓝宝石、青绿紧身裤和靴、酒红披风、银色剑身）；大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。
- **只有一圈描边**：整个剪影外面一圈 1 格宽的近黑描边（细剑剑身除外）；描边里面的边缘和褶皱用那种材质自己最暗的色阶，**不要再画第二圈黑**。白布用冷灰色做阴影，里面不要黑线。
- **细剑**：金色护手包住拳头（至少 3×3 格，带 1 格天蓝宝石）；剑身是一条 **1 格粗的亮银色直线**，从护手向右、稍微向上，约 26 格长，**两侧不描边**（游戏里补描边的规则会跳过 1 格细线）；剑身一条不断的线。
- **脸**（最重要）：A 头（头顶到下巴）至少 11 格高，B 约 13 格（身高的三分之一）；两只眼睛都看得见、一样大、在同一行：每只 2 格宽 2 格高（上行一格白色高光 + 一格深色瞳孔，下行青色），上面各一行深色睫毛；两眼之间 2 格皮肤，近处眼睛（画面左边，她朝右）前面留一列脸颊；青色**只用在眼睛上**（宝石用更浅的天蓝色）；细眉毛用头发最深的靛紫色，贴在眼睛上方、朝鼻子方向稍微往下斜；深红刘海和额发都在眉毛上方，中间隔一行皮肤，**绝不盖住眼睛**；一格深粉红的嘴在脸中线上、眼睛下面两行；脸颊、下巴不要别的深色格（之前的英雄出现过下巴两角的阴影连成歪嘴笑）；头坐在白色高领上。
- **两版**：A 照原图比例（只把头画大到至少 11 格，脸才看得清）；B 按原版英雄的 Q 版比例（头约 13 格，占身高三分之一，身体短一点），站姿、披风、细剑、颜色不变。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：鞋底最低一行正好在第 99 行方块，下面一格都不能有；披风的尖角在鞋底以上。
- 3/4 正面朝右（照原图），看得到脸和胸口，不画背影。
- 身体在画布左半边（照 `fiora_size_guide.png` 的位置），细剑伸向右边，所有格子都在画布里。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，就不提名字，只保留外观描述（下面的提示词里已经没有名字）。

## 提示词（A、B 各生成一张，只把 Face 里 [HEAD] 那句换成对应的一版）

### 方案 A：`fiora_design_A.png`

```text
Five attached images. FIRST: the look of this character - copy her face, hair, clothes, colors, cape, rapier and her en-garde stance from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size, cleanliness and their way of drawing faces. THIRD: heroes of this game's pack at 8x - the quality to reach: crisp small details, no mush. FOURTH: another hero of this pack at game size on the same canvas, 8x - use it ONLY for the size and the ground line. FIFTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: about 39 pixels from the top of the hair to the soles, true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine filigree.
The character: an elegant duelist woman in the en-garde stance of the FIRST image: side-on, feet wide apart on one ground line, the near sword arm stretched forward to the RIGHT at shoulder height, the other arm low behind her hip with an open gloved hand, the cape hanging behind her to the lower left. A short sleek DARK INDIGO bob cut at the jaw with pointed ends, a broad CRIMSON streak from the parting across the forehead and down the near cheek; fair skin; a white high collar and a white blouse-coat with gold piping, split at the lower front; big curled GOLD pauldrons with small sky-blue gems; a gold armoured gauntlet on the whole sword forearm; gold waist and hip plates with a sky-blue gem; dark TEAL fitted leggings and teal heeled boots with gold toe caps and trims; the cape wine-red outside, white inside with a gold border and a sky-blue gem at its lower point. The RAPIER: a swept GOLD guard round her fist (at least 3x3 squares with one sky-blue square) and a long straight blade pointing RIGHT and slightly up, about 26 squares long from the guard to the tip, drawn as ONE square thick bright silver line with no outline along it (a bare 1-square line; only the guard and the fist are outlined).
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (hair indigo, crimson streak, skin, white cloth, gold, sky-blue gems, teal suit and boots, wine cape, silver blade); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. ONE 1-square near-black outline around the whole silhouette only (except along the bare blade): inside it, edges and folds use the material's own darkest shade - never a second ring of black inside the outline. The white cloth is shaded with a cool light grey, never outlined in black inside.
Face (most important detail): A: the FIRST image's proportions, only the head bigger than in the FIRST image so the face reads: the head (top of the hair to the chin) at least 11 squares tall; both eyes visible, the same size and on the same rows: each eye 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row TEAL - with a dark lash row over each eye; 2 squares of skin between the eyes and one cheek column before the near eye (left, she faces right); the teal is used NOWHERE else (the gems are a lighter sky-blue); thin brows in the hair's darkest indigo just above the eyes, sloping slightly down toward the nose; the crimson streak and the fringe stay ABOVE the brows with one row of skin between, never over an eye; one dark pink-red mouth square on the face's middle line two rows under the eyes; no other dark squares on the cheeks or the jaw (a shadow joining the jaw corners to the chin reads as a grin); the head sits on the white collar.
Pose and place: 3/4 FRONT view facing right as the FIRST image, face and chest visible, never her back. The soles on block row 99 (y 792-799) - the same ground as the FOURTH image - and NOTHING on or below row 100 (the game draws the health bar under the soles): the cape's point ends above the soles. Horizontally as the FIFTH image: her body on the left half, the rapier reaching to the right; keep every square inside the canvas.
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 39 squares from the top of the hair to the soles; every square 8x8 on one grid; at most 24 colors; both eyes 2x2, level and visible, the teal only in the eyes; the outline one square wide everywhere with no black ring inside it; the blade one unbroken 1-square line; nothing below the soles.
```

### 方案 B：`fiora_design_B.png`

```text
Five attached images. FIRST: the look of this character - copy her face, hair, clothes, colors, cape, rapier and her en-garde stance from it. SECOND: official heroes of the game Teamfight Manager 2 at 8x (every game pixel an 8x8 block) - match their pixel size, cleanliness and their way of drawing faces. THIRD: heroes of this game's pack at 8x - the quality to reach: crisp small details, no mush. FOURTH: another hero of this pack at game size on the same canvas, 8x - use it ONLY for the size and the ground line. FIFTH: a straight shrink of the FIRST image to game size at 8x - use it ONLY to see what fits at this size and where; it is blurry and broken, do not copy its look.
Task: redraw the FIRST image as clean hand-made pixel art AT GAME SIZE: about 39 pixels from the top of the hair to the soles, true low-resolution pixel art shown enlarged 8x - every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency. Keep the big readable shapes of the FIRST image and drop its fine filigree.
The character: an elegant duelist woman in the en-garde stance of the FIRST image: side-on, feet wide apart on one ground line, the near sword arm stretched forward to the RIGHT at shoulder height, the other arm low behind her hip with an open gloved hand, the cape hanging behind her to the lower left. A short sleek DARK INDIGO bob cut at the jaw with pointed ends, a broad CRIMSON streak from the parting across the forehead and down the near cheek; fair skin; a white high collar and a white blouse-coat with gold piping, split at the lower front; big curled GOLD pauldrons with small sky-blue gems; a gold armoured gauntlet on the whole sword forearm; gold waist and hip plates with a sky-blue gem; dark TEAL fitted leggings and teal heeled boots with gold toe caps and trims; the cape wine-red outside, white inside with a gold border and a sky-blue gem at its lower point. The RAPIER: a swept GOLD guard round her fist (at least 3x3 squares with one sky-blue square) and a long straight blade pointing RIGHT and slightly up, about 26 squares long from the guard to the tip, drawn as ONE square thick bright silver line with no outline along it (a bare 1-square line; only the guard and the fist are outlined).
Pixel rules (most important): at most 24 colors in total, every material 2-3 flat shades (hair indigo, crimson streak, skin, white cloth, gold, sky-blue gems, teal suit and boots, wine cape, silver blade); big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. ONE 1-square near-black outline around the whole silhouette only (except along the bare blade): inside it, edges and folds use the material's own darkest shade - never a second ring of black inside the outline. The white cloth is shaded with a cool light grey, never outlined in black inside.
Face (most important detail): B: the base game's chibi proportions: the head (top of the hair to the chin) about 13 squares, a third of the height, a shorter torso; the same stance, cape, rapier and colors as A; both eyes visible, the same size and on the same rows: each eye 2 squares wide and 2 tall - top row a white highlight square and a dark pupil square, bottom row TEAL - with a dark lash row over each eye; 2 squares of skin between the eyes and one cheek column before the near eye (left, she faces right); the teal is used NOWHERE else (the gems are a lighter sky-blue); thin brows in the hair's darkest indigo just above the eyes, sloping slightly down toward the nose; the crimson streak and the fringe stay ABOVE the brows with one row of skin between, never over an eye; one dark pink-red mouth square on the face's middle line two rows under the eyes; no other dark squares on the cheeks or the jaw (a shadow joining the jaw corners to the chin reads as a grin); the head sits on the white collar.
Pose and place: 3/4 FRONT view facing right as the FIRST image, face and chest visible, never her back. The soles on block row 99 (y 792-799) - the same ground as the FOURTH image - and NOTHING on or below row 100 (the game draws the health bar under the soles): the cape's point ends above the soles. Horizontally as the FIFTH image: her body on the left half, the rapier reaching to the right; keep every square inside the canvas.
Layout: one 1024x1024 image per version (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 39 squares from the top of the hair to the soles; every square 8x8 on one grid; at most 24 colors; both eyes 2x2, level and visible, the teal only in the eyes; the outline one square wide everywhere with no black ring inside it; the blade one unbroken 1-square line; nothing below the soles.
```

## Claude 收到后（给 Claude 看）

- 按原稿自己的格子取像素（skill 的 `scripts/regrid.py`：颜色变化的峰值定格子边界，每格取中心 3×3 的中位色），**不缩小**；压色板到 24 色以内，只留一圈描边（剑身除外），青色只用在眼睛；手修脸（两眼同高同大、嘴在中线）；右邻同色比例、颜色数和原版英雄比。游戏尺寸预览（和原版英雄、包里英雄比大小，在对战场地色和深色头像卡上各看一遍）给用户挑 A/B。
