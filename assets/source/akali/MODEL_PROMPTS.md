> 造型第 1 步的重做（用户说上一版「细节还是糟糕」，要和 main 的英雄一样「不模糊细节好」）。Codex 拿到的是这份提示词之前的写法（A 直接按游戏尺寸、B 画 1.7 倍），它实际用的提示词在 `codex_model/design3_generation_prompts.json`，交付说明在 `codex_model/design3_HANDOFF.md`。它的 A 原稿（`codex_model/design3_generated_A.png`）按自己的格子是 66 格高；Claude 按原稿的格子取像素、逐行逐列删减到 47 格（`tools/art/design_akali.py`），用户选的就是这一版（「选1」）。动作帧的提示词在 [`MODEL_STRIPS.md`](MODEL_STRIPS.md)。

# 阿卡丽：按游戏尺寸重画造型（第 1 步重做，给 Codex 的提示词）

> **这一轮只画造型图，不画动作。** 用户看了上一版（B 大眼）说「细节还是糟糕」，而 main 分支里的英雄模型「都做的挺好的美术」。那些英雄（18 位重画）是你**从一整张原稿直接按游戏尺寸画**出来的；上一版阿卡丽走的是另一条路（你先画 80 格，Claude 按行列删减缩到 46 格，再把碎斑合并成平涂），细节在缩小和合并时丢了，也比所有英雄大一圈。所以这一轮照 main 那 18 位的做法来。
> - **最重要：不糊、细节好**（用户原话「主要是要不模糊细节好」）。每个方块都是清楚的一格颜色，材质之间是硬边，没有过渡色、没有糊成一片的暗色；细节多而清楚，像 main 里的英雄。
> - **长相照原图** `akali/akali_source.png`（用户给的图）：头发、脸、衣服、颜色、武器、姿势。
> - **质量照 main 里的英雄** `akali/quality_bar.png`（亚索、永恩、李青、贝蕾亚、莫甘娜、蕾欧娜，游戏尺寸放大 8 倍，都是你画、用户认可的）：同样的像素大小、同样的细节密度和明暗层次。
> - **大小和位置** `akali/size_place.png`：灰色剪影就是她站的位置和大小——头顶到脚底约 **38 格**，马尾再高出约 8 格，一共 **46 格**（和贝蕾亚、卢锡安、迦娜一样；亚索 47），脚底在第 99 行（y=792–799）。
> - 眼睛保留用户选的「大眼」（`akali/eyes_picked.png`），脸的其余部分照原图画得更精致。
> - **只画一版，直接按游戏尺寸画**，不要先画 1.7 倍再缩小（用户的要求；main 上卢锡安重做就是这样画的，薇恩这次也这样画，用户看了说「挺好」）。Claude 收到后只按你原稿自己的格子取像素，不缩小、不合并。
> - 生图原稿通常不在严格网格上（方块 7.4–8.6 px，脸会变窄）。**交回前请你自己整理好**：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，颜色不超过 28 种。附 `HANDOFF.md`（用了哪条提示词、哪里没做到）、原尺寸图 `akali_design_1x.png` 和用到的色板。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `akali/akali_source.png` | 用户给的原图 | **长相**：头发、脸、衣服、颜色、武器、姿势 |
| `akali/quality_bar.png` | main 里 6 位英雄（亚索、永恩、李青、贝蕾亚、莫甘娜、蕾欧娜），游戏尺寸 ×8，同一条脚底线 | **质量标准**：像素大小、细节、明暗 |
| `akali/size_place.png` | 1024×1024 画布（128×128 格 ×8），灰色剪影 = 她的大小和位置（一共 46 格） | 只看大小和位置 |
| `akali/eyes_picked.png` | 用户选的「大眼」：刘海到面罩上沿这一段，12 倍 | 眼睛的大小和结构 |
| `refs/not_this.png` | 反面例子：上一版 B（平、糊、头发粗糙、太大）和被否定的 v2（四肢细、马尾一根根、满身碎斑） | 看清楚哪些不能做 |

## 规则

- **像素尺寸（最重要）**：头顶到脚底约 38 格，马尾再高出约 8 格（一共 46 格）；按真正的低分辨率像素画来画，再整体放大 8 倍输出：每个像素一个清楚的 8×8 方块，所有方块对齐同一个 8 px 网格，没有比一个方块更小的东西，没有抗锯齿、模糊、柔光、半透明。
- **Q 版比例和 main 里的英雄一样**：头（头顶到下巴，不算马尾）约 12–13 格，约占头顶到脚底的三分之一，腿稍短。
- **细节和明暗照 main 里的英雄**：一圈 1 格的近黑描边，描边里面每种材质有自己的暗、中、亮和一点高光（暗部带颜色）；每一个小方块都在画东西（一缕头发、一道褶、一条边、一个金环），不要随手撒的杂点，不要抖动、渐变、噪点；最多 28 色。
- **深色的东西也要看得清**（她的主色都很暗）：黑发用蓝黑加蓝灰的发丝，顶上几格浅蓝灰高光；深绿上衣受光的一边和斜襟是明显亮一档的绿；深灰裤子有亮一档的褶；皮肤暖而亮。让她在这个尺寸下好认的是那些亮的小点缀：护臂和腰带上的金环、小腿绑带上的金菱形、腰布的金尖、米色腰带和绑带、苦无和镰刀的亮钢刃——都要留着。
- **脸**：蒙面只露眼睛，眼睛照 `eyes_picked.png` 的大小：上面一行黑色眼线（外侧上挑一点），下面两行——近眼（左）3 格宽（白、白、棕瞳孔），远眼（右）2 格宽（白、棕瞳孔），中间隔 1 格皮肤，两只眼睛同一高度；面罩上沿紧贴在眼睛下面（和 `eyes_picked.png` 一样）；刘海垂到眼线那一行。眼白和棕色瞳孔**只用在眼睛上**。面罩深绿，一道浅一档的褶，不画嘴。
- **头发**：马尾是一整团大的、有几个尖角的黑发（不是一根根细线），用深绿发带扎在后脑高处，往上往后散开；刘海一缕缕尖的，侧面有发丝垂到下巴。
- **苦无在近侧的手（图里左边），镰刀在远侧的手（右边）**；手臂 2–3 格颜色宽（加描边），不能只有 1 格。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：苦无和镰刀都在脚底以上结束。3/4 正面朝右，背景透明（做不到时用纯品红 `#FF00FF`），不要网格线、文字、边框、影子。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 提示词：`akali_design.png`

附四张图：`akali/akali_source.png`、`akali/size_place.png`、`akali/quality_bar.png`、`akali/eyes_picked.png`；`refs/not_this.png` 可以一起附上。

```text
Four attached images. FIRST: the approved design illustration of this character - copy its look: the hair, the face, the costume, the colours, the weapons and the pose. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - use it ONLY for her size and her place in the canvas. THIRD: six other heroes of this game at game size, shown at 8x, approved by the user - this is the standard to match: the same pixel size, the same level of detail, the same crisp shading with lit edges and small bright accents, the same chibi proportions. FOURTH: the eyes the user picked, at 12x - keep their size and structure.
Task: draw the character of the FIRST image as clean hand-made pixel art directly at game size (not bigger, nothing to be shrunk later): about 38 pixels from the crown of the head to the soles, the ponytail rising about 8 more (46 in all), drawn as true low-resolution pixel art and shown enlarged 8x, so every pixel is one crisp 8x8 square on a single 8-px grid. Chibi proportions like the THIRD image: the head (crown to chin, without the ponytail) about 12-13 squares, a third of the height from the crown to the soles.
The character: Akali as a chibi ninja: black hair drawn in blue-black with dark blue-grey strands and a few light blue-grey highlights, a big spiky high ponytail tied with a dark green band on the back of her head and fanning out up and behind her, a sharp side fringe sweeping across her forehead and locks framing her face; a dark green cloth mask over her nose and mouth; tan skin; big brown eyes with a black liner; a sleeveless dark green wrap top with a lighter green diagonal fold across the chest, cut above a bare midriff; a dark swirl tattoo on her near upper arm; black fingerless gloves and dark forearm guards with gold rings; a cream cloth sash with a gold ring at the hip and a hanging cream end; a green loincloth panel in front with a darker green arrow pattern and a small gold tip; baggy charcoal trousers gathered at the knees; cream shin wraps with small gold diamonds; dark sandals. Weapons: a steel kunai with a gold ring pommel held point-down in her near hand (image left), a kama (a short dark wrapped handle with gold fittings and a big curved steel blade) in her far hand (image right).
CRISP, NOT BLURRY, WITH GOOD DETAIL - this is what the user asks for above all: every square one clear colour, hard edges between materials, no blended in-between colours, no dark areas smeared into one blob.
Pixel rules (most important): true low-resolution pixel art - nothing smaller than one square, no anti-aliasing, no blur, no soft glow, no semi-transparency; at most 28 colours; a 1-square near-black outline around the whole silhouette, and inside it every material in its own dark, mid and light shade plus a small highlight (coloured, hue-shifted darks - black is only the outline); every single square describes something (a strand of hair, a fold, an edge, a gold ring) - no random specks, no dithering, no gradients, no noise.
Her main materials are dark, so make them read like the dark heroes of the THIRD image: the black hair in blue-black with blue-grey strands and a few light blue-grey highlights on top; the dark green top with a clearly lighter green lit edge and diagonal fold; the charcoal trousers with lighter folds; warm bright skin. The small bright accents are what make her readable at this size - keep them: the gold rings on the forearm guards and the sash, the gold diamonds on the shin wraps, the gold tip of the loincloth, the cream sash and wraps, the bright steel edges of the kunai and the kama.
Colours: from the FIRST image, but clean and distinct - every material's shades clearly apart, the accents bright; never a muddy in-between colour (the FIRST image is soft-edged: do not copy its blended edge colours).
Face (most important detail): the mask covers from under the eyes to the chin, so only the eyes show. Eyes as in the FOURTH image: a near-black liner row with a small wing at the outer end, then two rows - the near eye (left, she faces right) 3 squares wide (white, white, brown iris), the far eye 2 squares wide (white, brown iris), one skin square between them, both on the same rows; the mask's top edge right under the eyes (as in the FOURTH image); the fringe comes down to the liner row. The eye white and the iris brown are used nowhere else. The mask is dark green with one lighter fold, no mouth.
Hair: the ponytail is one big solid mass of black hair with a few spikes (not thin strings), tied high on the back of the head with the dark green band and fanning up and back; the fringe in pointed locks, a lock down to the jaw at the side.
Arms 2-3 squares of colour wide plus the outline, never 1. The kunai in the near hand (image left), the kama in the far hand (image right).
Pose and place: the pose of the FIRST image, 3/4 FRONT view facing right, where the SECOND image's shape stands: the lowest row of the soles at y=792-799 (square row 99, 28 squares above the bottom of the image). Nothing below the soles (the game draws the health bar right under the feet): the kunai and the kama end above that line.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no text, no border, no shadow.
Before finishing, check: about 38 squares from the crown to the soles and 46 from the top of the ponytail, all squares 8x8 on one grid, at most 28 colours, one outline ring only, the detail and shading of the THIRD image (not flat dark areas), both eyes level and clearly visible above the mask, the eye colours only in the eyes, nothing below the soles.
```

## 交回前自查

- [ ] 头顶到脚底约 38 格，算上马尾一共 46 格；脚底最低一行在第 99 行，脚底以下没有像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，不超过 28 色；
- [ ] 和 `quality_bar.png` 放在一起看：细节、明暗、高光一个水平，不是大块暗色平涂（`refs/not_this.png` 左边那种）；
- [ ] 头发有发丝和高光，马尾是一整团有尖角的黑发，刘海一缕缕；
- [ ] 两只眼睛同一高度，近眼 3 格、远眼 2 格，眼白和瞳孔色只在眼睛上；
- [ ] 苦无在左手、镰刀在右手，金环、金菱形、腰布金尖、米色腰带和绑带都在；
- [ ] 3/4 正面朝右，背景透明，没有网格、文字、影子。

## Claude 收到后（给 Claude 看）

- 只按原稿自己的格子取像素（颜色变化的峰值定格子边界，每格取中心 3×3 的中位色，一格对一个游戏像素），不缩小、不合并碎斑；检查色数、脚底线、眼睛，只补缺的描边（`tidy_codex18.one_outline` 先看色板再用：她的深色可能比它的「黑」阈值还暗，会被当成描边重涂）。
- 和 main 的英雄放在一起（竞技场底色和暗色卡片上，1× 和放大）给用户看；通过后按新造型重出动作帧包（第 3 版提示词里 v2 的教训保留）。
