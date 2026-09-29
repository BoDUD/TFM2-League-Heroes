# 堕落天使 莫甘娜：按新立绘重做造型（给 Codex 的提示词）

> **这一轮只做造型图（静态待机一张）。** 用户给了一张新的莫甘娜立绘（`refs/morgana_target.png`），莫甘娜的样子改成这张图：弯角王冠、长卷发、黑紫羽翼、开衩长裙。造型定稿后，再按它画 8 张动作图。
> - 立绘是 6 头身的修长比例，细节很多，直接缩到游戏尺寸脸会看不清（以前的英雄出过这个问题）。所以要**按游戏的 Q 版比例重画**：头约占身高 1/3，长相、服装、配色都照立绘。
> - 生图原稿通常不在严格网格上（方块大小不一、有半透明边），交原稿也可以：Claude 会按原稿自己的像素网格取色、缩到游戏尺寸再整理。但请尽量画成干净的像素画（方块清楚、色块平涂）。
> - 交回时附 `HANDOFF.md`（用了哪条提示词、有没有没做到的地方）和 `generation_prompts.json`（实际用的提示词）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/morgana_target.png` | **用户给的新立绘**：长相、服装、颜色、姿势都以它为准（比例除外） | 造型图 |
| `refs/tfm2_style_ref_mage.png`、`refs/tfm2_style_ref_healer.png` | 团战经理2 原版法师和辅助，放大 8 倍：像素大小、头身比例、干净程度、眼睛画法照它们 | 造型图 |
| `design/morgana_current_design.png` | 现在游戏里的莫甘娜造型（旧的样子，**不要照它的长相**），1024×1024、放大 8 倍：只用来对照大小和站位，脚底在 y=792–799 | 造型图（大小、站位） |

## 规则

- **像素尺寸（最重要）**：游戏里她从头顶（不算角）到脚底约 36 像素高，连角约 44 像素；按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素一个清楚的 8×8 方块，对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光、半透明。
- **比例**：团战经理2 的 Q 版，头（头发顶到下巴）约占身高 1/3，和附图的原版法师、辅助一样。身体、手臂、腿相应缩短，长裙照样拖到脚边。
- **脸（用户最在意）**：脸要在游戏里看得清。两只眼睛都看得见：近处的眼睛（画面左边）2 格宽、2 格高，远处的眼睛 1–2 格宽、同样高，两只眼睛在同一行；眼睛是立绘里的粉紫色，上面一格深色睫毛；两眼之间一格皮肤；眼睛下面一到两行皮肤，再一格深梅红色的嘴。头发和角**不能盖住眼睛**。
- **眼睛的颜色只用在眼睛上**（头发、翅膀、裙子、特效都不用这个颜色），导入时按这个颜色找眼睛来对齐每一帧。
- **描边只有一圈**：整个轮廓外面一格近黑色描边 `#120C15`；描边里面紧挨着的一圈**用材质自己的暗色**（头发的暗紫、裙子的暗紫、皮肤的暗粉），不要再画一圈黑，也不要拿黑色当阴影。内部线条越少越好。
- **干净**：整个造型最多 28 种颜色；每种材质 3–4 个平涂色阶（亮、中、暗、最暗）；大块纯色，不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块。细节看不清就省掉。
- **脚底线以下什么都不能有**：游戏在脚下画血条。鞋底和裙摆最低处正好踩在脚底线上（y=792–799 那一行），下面不能有任何像素。
- 3/4 正面朝右（和立绘一样脸朝右），看得到脸和胸口。
- **背景透明**。做不到透明时用纯品红 `#FF00FF`。不要网格线、边框、文字、编号。
- 如果模型不肯画有名字的角色，把 "Morgana" / "League of Legends" 删掉，只保留外观描述。

## 她的样子（照 `refs/morgana_target.png`）

- **头**：黑紫色的长卷发，从头顶披下来、一直垂到腰后，有几缕在胸前；尖尖的精灵耳朵；淡紫白色的皮肤；粉紫色的眼睛，眼尾上挑、深色眼影；深梅红色的嘴。
- **王冠**：头顶两侧各一只向上、向后弯的黑色大角，角的内侧镶金边；正中一个竖起的金色尖饰，中间一颗深紫宝石。角是她最好认的头部剪影，要画出来，但不挡脸。
- **身体**：黑紫色的露肩紧身胸衣，金色描边和 V 形金饰；脖子上一圈金色项圈；长裙黑紫色，层层叠叠、下摆散开拖到脚边，左腿从高开衩里露出来；裙上几枚金色菱形饰片。
- **手臂**：光着的淡紫白色手臂，上臂和手腕有金色臂环；右手（画面右边）向前摊开、掌心向上；左手垂在身边。
- **翅膀**：一对大的黑紫色羽翼，在身后半张开，从肩后向上、向两侧伸出，下半截的羽毛带洋红紫色；翅膀比身体宽一些，但**不挡脸和胸口**，左右总宽不超过约 44 个方块。
- **鞋**：紫色尖头高跟鞋。
- **颜色**（从立绘取的，可按立绘微调，合计不超过 28 色）：描边 `#120C15`；皮肤 `#E8D3E1` `#C0AABF` `#A98CA3`；头发 `#483056` `#33263C` `#1E1526`；眼睛 粉紫 `#D04A9C`（只用在眼睛上）+ 睫毛用头发最深色；嘴 `#7A3050`；胸衣和长裙 `#35283F` `#291734` `#17111C`，裙摆的紫色褶 `#5C2F61` `#462048`；翅膀 `#3C3044` `#291734` `#17111C`，下半截羽毛 `#6B3066` `#8A3A80`；金饰 `#C8A878` `#9C7C6D` `#614B47`；角 `#1E1526` `#120C15`（内侧金边用金饰色）；鞋 `#5C2F61` `#33263C`。

---

## 造型图：`morgana_design_A.png`、`morgana_design_B.png`

两个方案长相、服装、颜色都照立绘，只有翅膀不同，交回给用户挑：

| 方案 | 翅膀 |
|---|---|
| A | 半张开（像立绘），从肩后向上、向两侧伸出，羽尖到头的高度 |
| B | 收拢在背后，只从肩后露出上半截，整个造型更窄 |

每个方案附四张图：`refs/morgana_target.png`、`refs/tfm2_style_ref_mage.png`、`refs/tfm2_style_ref_healer.png`、`design/morgana_current_design.png`。

```text
Four attached images. FIRST: the character to draw - copy her look: face, hair, horned crown, wings, gown, colors and pose, but NOT her tall proportions. SECOND and THIRD: official heroes of the game Teamfight Manager 2 at 8x - match their chibi proportions (the head about one third of the height), their pixel size and cleanliness, and their way of drawing eyes. FOURTH: our current game sprite of this character at 8x on the target canvas - use it ONLY for the size and the place in the canvas (her soles on y 792-799, the standing point in the middle column); ignore its look.
Task: redraw the character of the FIRST image as a clean hand-made pixel-art game sprite: about 36 pixels tall from the top of her hair to her soles (about 44 with the horns), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency.
Morgana, a fallen angel sorceress, chibi (the head about one third of her height), 3/4 FRONT view facing right, standing calmly: her right hand (on the right of the image) held forward, palm up, as if holding dark magic; the other arm down at her side. Long wavy black-violet hair falling from the top of her head down to her waist behind her, a few locks over her shoulder - never over her eyes; long pointed elf ears; pale lilac-white skin; pink-violet eyes with upswept dark lashes; dark plum lips. A crown of two large black horns curving up and back from the sides of her head, gold-edged on the inside, and a tall gold spike with a dark violet gem in the middle - her most recognizable head shape, never over her face. A strapless black-violet corset with gold trim and a gold V ornament, a gold collar at the throat, gold armlets and bracelets; a long black-violet layered gown flaring to the floor with violet folds and a few gold diamond ornaments, a high slit showing her left leg; violet pointed high heels. [A: large black-violet feathered wings HALF-SPREAD behind her, rising from behind her shoulders up and out to both sides, their lower feathers tinged magenta-violet, the tips reaching about the height of her head.] [B: large black-violet feathered wings FOLDED on her back, only their upper part showing above and beside her shoulders, lower feathers tinged magenta-violet.] The wings never cover her face or chest; the whole sprite at most about 44 squares wide.
Face (most important): both eyes clearly visible and readable at game size - the near eye (left of the face's middle) 2 squares wide and 2 squares tall, the far eye 1-2 squares wide and just as tall, both on the same rows; each eye pink-violet with a dark lash square on top; one square of skin between the eyes; one or two rows of skin under the eyes, then one dark plum mouth square. The pink-violet eye color #D04A9C is used ONLY in the eyes, nowhere else.
Pixel rules (most important): at most 28 colors in total, every material 3-4 flat shades; ONE outline: a 1-square near-black outline #120C15 around the whole silhouette, and right inside it each material's OWN darkest shade, never a second black ring and never black used as shading; very few inner dark lines. Palette: outline #120C15; skin #E8D3E1 #C0AABF #A98CA3; hair #483056 #33263C #1E1526; eyes #D04A9C; mouth #7A3050; corset and gown #35283F #291734 #17111C with violet folds #5C2F61 #462048; wings #3C3044 #291734 #17111C with lower feathers #6B3066 #8A3A80; gold #C8A878 #9C7C6D #614B47; horns #1E1526 #120C15 with gold inner edges; heels #5C2F61 #33263C. Big solid areas; no dithering, no gradients, no noise, no lone square of a different color inside an area. Drop details that do not read at this size.
Place: her soles and the gown's lowest edge on the line 28 squares (224 px) above the bottom of the image (the lowest drawn row is y 792-799); nothing below y 800 (the game draws the health bar under her feet); her standing point in the middle column.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 36 squares from the top of the hair to the soles (about 44 with the horns), the head about one third of that, all squares 8x8 on one grid, at most 28 colors, both eyes visible, 2 squares tall and on the same rows, the eye color only in the eyes, one outline with each material's dark shade inside it, nothing below y 800.
```

中括号里是两个方案各自的一段，每张只保留自己那一段。

## 选定：方案 A（Claude 整理到游戏尺寸）

Codex 交回 A（翅膀半张开）和 B（收拢）两张（交接说明、实际提示词在 `codex_model/redesign_*`）：都是生图原稿，1254×1254，四万多种颜色、半透明边，不在严格网格上。用户让 Claude 选，选了 A（剪影最像立绘，翅膀不挡脸）。整理成 `design/morgana_native.png`（也就是 `assets/source/native/morgana_native.png`）的做法：
- 按原稿自己的像素网格取色：按颜色突变的位置找出方块的边界，每个方块取中间 3×3 的中位色，得到 59×76 格的图，映射到 24 色。
- 头发、翅膀、长裙的暗紫色用 3×3 多数色压平（周围至少 4 格同色才换，做 4 遍）；脸、金饰、皮肤、洋红羽尖和描边保持原样。
- 按阿狸那一轮（18 个英雄重画）的做法缩到游戏尺寸：每组里删掉和相邻最像的一行（列），缩到 44 行（不按颜色投票，投票会把脸糊掉），外面补一圈描边，描边里面的黑圈换成材质自己的暗色，角尖保留。
- 眼睛：第一版远处的眼睛只有 1 格，用户说"怎么就一个眼睛"。改成两只眼睛一样大、在同一行：各 2×2，左上一格白色高光、其余 `#C83CA6`，上面一行深色睫毛，两眼之间 2 格皮肤；脸加宽到 7 格，眼睛不再贴着头发。用户看过说"使用新改的 做的很好"。

结果：连角 35×45 格，26 色，眼睛的 `#C83CA6` 只用在 6 格眼睛上；脚底在 y=792–799。
