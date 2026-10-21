# 奥莉安娜：Q 版重画（游戏尺寸造型，给 Codex 的提示词）

> 现在游戏里的奥莉安娜（`refs/8_current_rejected.png`）用户不满意：「我要的是Q版的 现在明显质量不行啊」——她是细长的成人人偶比例，头小、脸看不清，金色糊成一片黄。
> 这一轮请**直接在游戏格子上**画一个 **Q 版奥莉安娜**（不要画大图再缩小，缩小会糊）：
> - **Q 版比例**：大头、短身子、短腿，像附图 9 里团战经理 2 原版英雄、附图 10 泽丽那样**敦实可爱**，不要细长。
> - **长相、配色照英雄联盟原版**（附图 1、4、5、6、7）：**古铜金色的金属齐耳短发 + 头顶圆发髻**（像附图 1 那种古铜金，不要柠檬黄），**瓷蓝灰色的脸**，**青蓝色发光的大眼睛**，银白金属胸甲 + 脖子前一枚金色齿轮，一节一节的银灰金属手臂和腿、**深棕色小圆球关节**，银白色的手、**细长尖爪一样的手指**，腰上一圈**古铜金齿轮刀片短裙**，银灰金属腿 + 尖头小靴。
> - **两个角度**，同一个设计：**A = 3/4 正面朝右**（待机用），**B = 正侧面朝右**（动作帧都按侧面做）。
> - **球单独画一张**（游戏里球是单独的图）。
> - **画两稿**：Q1 头约占身高 1/3（原版英雄的比例），Q2 头再大一点（约 2/5，更 Q）。用户从中挑一稿，下一步再按它和英雄联盟的骨架画动作帧。

## 尺寸和格子（照 `layout/12a`、`12b`、`12c`）

- 画布 **1536 × 1536**，**每格 12 px**，网格从画布左上角 (0, 0) 开始，128 × 128 格。
- **发髻顶在第 33 行（y = 396，绿线），脚底在第 117 行（y = 1404，红线）：从发髻顶到脚底正好 84 格**。两只脚底在同一条线上。
- 宽度：**身体比 12a / 12b 里的渲染图更敦实**（渲染图是英雄联盟原模型把头放大，身子还是细的）——躯干、手臂、腿都画粗一些，像附图 9、10。站姿、手的位置照 12a / 12b。
- **球**：单独一张 1536 × 1536，直径约 **20 格**，放在画布正中（12c）。

## 要画清楚的地方

- **头**（附图 4）：古铜金金属齐耳短发，刘海斜着盖住一点额头，两侧包到下巴；头顶圆发髻；金色分 3–4 档（亮金、古铜金、暗铜、棕），看得出发片的走向。瓷蓝灰色的脸（冷色，亮面浅灰蓝、暗面灰紫），**两只青蓝色发光的大眼睛一样大、在同一行**（每只至少 3 格宽、2 格高，带 1 格亮白），小小的深色嘴，下巴尖，脸颊边上一道细细的人偶接缝。
- **身体**：脖子前一枚金色齿轮徽章（3–4 格）；银白金属胸甲分 3 档；分节的银灰金属手臂，**肩膀、手肘、手腕的深棕色小圆球关节**（每个约 2–3 格）；银白色的手，手指细长带尖。
- **短裙**：一圈古铜金的齿轮刀片向外张开，**每一片尖刺都数得出来**，里层深棕。
- **腿**：短而结实的银灰金属腿，**膝盖、脚踝的小圆球关节**，小腿外侧银白护甲片，尖头小靴。
- **侧面 B**：脸朝画面右边，能看到一只眼睛、鼻尖、下巴；发髻在头顶偏后；近侧手臂在身前，远侧手臂只露一点、颜色暗一档；裙子的刀片前后都伸出去。
- **球**（附图 6）：钢银色球面分 3–4 档，左上亮右下暗；球面上深色和亮银的刻纹；**腰上两道古铜色的环**（各 1–2 格宽，中间一道深缝），一道古铜色的弧形脊从顶上绕过去。

## 干净（和附图 10、11 一样）

- 每格一个颜色，大块平涂，每种材质 3–4 档，光从左上来。
- **一圈 1 格的近黑外描边**，连续不断；描边里面用每种材质自己最暗的一档，不要再一圈黑。
- 细节至少一整格，没有碎点、抖动、渐变、柔光、半透明；最多约 28 色；**青蓝色只用在眼睛上**。
- 真透明背景，alpha 只有 0 / 255。不要网格线、文字、地面、影子、特效。

## 附图（压缩包 `orianna_chibi_pack.zip`，解压到一个新的文件夹，只用里面的图）

**一次只能附几张时，按这个顺序附：12a、12b、4、1、10、9、6、12c。**

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_league_idle.png` | 英雄联盟原版奥莉安娜的待机，3/4 朝右，带球 | 长相、**配色**、部件 |
| `refs/2_q_front.png` | 同一帧，头放大、腿缩短（Q 版比例），不带球 | A 的比例和角度 |
| `refs/3_q_side.png` | 同上，正侧面朝右 | B 的比例和角度 |
| `refs/4_q_head.png` | Q 版比例的头部特写 | 发型、发髻、脸、眼睛 |
| `refs/5_q_back.png` | 背后 | 发髻、背后的裙子 |
| `refs/6_ball.png` | 球 | 球的花纹、两道环、弧脊 |
| `refs/7_splash.png` | 官方加载画面 | 气质 |
| `refs/8_current_rejected.png` | 现在游戏里的她（6 倍）——**用户不要的** | **不要这样**：细长、头小、黄色糊 |
| `style/9_base_heroes.png` | 团战经理 2 原版法师英雄，8 倍 | **Q 版比例**、脸怎么画 |
| `style/10_zeri.png` | 本包的泽丽（用户认可的 Q 版样板），8 倍 | **这个密度下的 Q 版**、干净程度 |
| `style/11_gwen.png` | 格温在格子上重画的 1 倍图，8 倍 | 每格一个颜色、描边 |
| `layout/12a_layout_front.png` | A：Q 版渲染图放在 12 px 网格上，绿线 = 发髻顶第 33 行，红线 = 脚底第 117 行 | A 的**大小、位置** |
| `layout/12b_layout_side.png` | B：同样的网格和线 | B 的**大小、位置** |
| `layout/12c_layout_ball.png` | 球：约 20 格，画布正中 | 球的大小、位置 |

## 提示词 1：她（A / B 两个角度 × Q1 / Q2 两稿，共四张）

**用 image_gen 画**，不要用脚本逐格写。

```text
Attached images (in this order): 12a and 12b are LAYOUT GUIDES on a 12-px grid - a 3D render of this character with a big chibi head, 3/4 front facing right (12a) and side-on facing right (12b); the green line is the top of her bun (row 33, y 396), the red line her soles (row 117, y 1404); copy ONLY the size, the place, the stance and the angle - her body there is still too thin. Image 4 is her head close-up, image 1 her original look and colours with her ball, image 6 the ball. Image 10 and image 9 are STYLE: other characters from the same game shown 8x so every square is one pixel - copy their CHIBI proportions and their clean pixel-art look. Copy shapes and colours from the renders, NOT their 3D shading.
Draw with the image generator ONE pixel-art picture of a CHIBI CLOCKWORK DOLL GIRL, a 1536x1536 PNG with a real transparent background (alpha only 0 or 255), on a FIXED GRID of 12x12-px squares aligned to the canvas corner (128 x 128 squares); every square one flat colour. She is exactly 84 squares tall: the top of her bun on row 33 (y 396), both soles on row 117 (y 1404) on one ground line; centred like the layout guide.
CHIBI PROPORTIONS: a big head, a short sturdy body, short legs - cute and chunky like images 9 and 10, never slender: the torso, arms and legs clearly thicker than in the layout guide.
HER LOOK (images 1 and 4): a BRONZE-GOLD METAL BOB (antique bronze gold like image 1, not lemon yellow), the fringe sweeping across the forehead, the sides wrapping to the jaw, a ROUND BUN on top, the metal in 3-4 shades (bright gold, bronze, dark copper, brown) showing the hair plates; a PORCELAIN face in cool blue-grey (light grey-blue, grey-violet in shadow), TWO BIG GLOWING CYAN EYES the same size on the same row (each at least 3 squares wide and 2 tall, with a 1-square white glint), a small dark mouth, a pointed chin, a thin doll seam on the cheek; a small GOLDEN GEAR at the throat; a SILVER-WHITE METAL BODICE in 3 shades; segmented SILVER-GREY metal arms with small DARK-BROWN BALL JOINTS at the shoulders, elbows and wrists (2-3 squares each); silver-white hands with long thin CLAW-LIKE pointed fingers; a SHORT SKIRT of BRONZE-GOLD GEAR BLADES flaring out with every pointed blade countable, dark brown under it; short sturdy silver-grey metal legs with ball joints at the knees and ankles, silver-white shin plates, small pointed boots.
Clean: 3-4 flat shades per material lit from the upper left, ONE continuous near-black 1-square outline round the silhouette, inside it each material's own darkest shade (never a second black ring), details at least one whole square, no specks, no dithering, no gradients, no soft glow, no blur, no anti-aliasing, at most about 28 colours; the cyan ONLY in the eyes.
No ball, no effects, no background, no ground, no shadow, no text, no grid lines.
VIEW A (front): 3/4 front facing image right like 12a - the near arm and leg on the image left in full tone, the far ones on the image right one shade darker; standing with the feet a little apart, one hand down at her side with the fingers spread, the other before her chest.
VIEW B (side): side-on facing image right like 12b - one eye, the nose tip and the chin seen in profile, the bun on top toward the back, the near arm before her body, the far arm barely showing and one shade darker, the skirt blades reaching out front and back; the same design, colours and size as view A.
TAKE Q1: the head from the top of the bun to the chin about 28 rows (a third of her height). TAKE Q2: the head about 34 rows (two fifths), the body shorter to keep 84 rows in all.
```

## 提示词 2：球（一张）

```text
Same attached images. Draw with the image generator ONE pixel-art picture of the character's BALL alone (image 6, sized like image 12c): a 1536x1536 PNG with a real transparent background (alpha only 0 or 255), the ball about 20 squares across in the middle of the canvas, every square 12 px on one grid starting at the canvas corner, every square one flat colour. A STEEL-SILVER metal sphere in 3-4 shades, lit from the upper left (a bright side and a dark side), dark and bright-silver engraved swirls on it; TWO BRONZE BANDS round its middle (1-2 squares each, a dark seam between them) and a bronze curved ridge over its top; one continuous near-black 1-square outline; no specks, no dithering, no gradients, no glow, no blur, no anti-aliasing. No girl, no effects, no background, no shadow, no text, no grid lines.
```

## 交付（`outputs/orianna-chibi/`）

- `orianna-q1-front.png`、`orianna-q1-side.png`、`orianna-q2-front.png`、`orianna-q2-side.png`、`orianna-ball.png`（都是 1536 × 1536）；
- 每张再交一个 **1 倍图** `*_1x.png`（128 × 128：每个 12 × 12 的格子变成一个像素，最近邻，透明保留）——游戏读的是 1 倍图，**必须和大图逐格一致**；
- `orianna-chibi-compare.png`：四张的 1 倍图放大 8 倍并排，旁边放 `refs/8_current_rejected.png`；
- 生图原稿原样放进 `raw/`；`generation-prompts.txt`（实际用的提示词）；
- **最后**写 `HANDOFF.md`（每张的高度行数、宽度、色数、每格是否单色、alpha 是否只有 0/255），再打包成 `outputs/orianna_chibi_done.zip`。中间不要停，五张都画完再交。

## 交回前请检查

- 1536 × 1536，真透明背景，alpha 只有 0 / 255；每个 12 px 格子一个颜色；1 倍图和大图一致。
- **发髻顶第 33 行、脚底第 117 行（84 格）**；两只脚底在同一行。
- **Q 版**：大头、敦实、短腿；Q1 头约 28 行，Q2 约 34 行；不是细长的人偶。
- 古铜金头发（不是柠檬黄）；瓷蓝灰的脸；**两只青蓝大眼睛一样大、同一行**，1 倍下也看得清；齿轮徽章、关节小球、裙子的刀片都数得出来。
- A 是 3/4 正面朝右，B 是正侧面朝右，两张是同一个设计、同样大小和颜色。
- 一圈连续的近黑描边，里面没有第二圈黑；没有碎点、渐变、柔光。
- 如果模型不肯画有名字的角色，提示词里本来就没写名字，只用外观描述。

## Claude 收到后（给 Claude 看）

- 原稿和交付放进 `assets/source/orianna/codex_chibi/`；先在 8 倍下数描边台阶量出实际格子大小（`scripts/regrid.py`），用 1 倍图前先和大图逐格核对。
- 整理（tidy_codex18 的规则：描边毛刺、内圈黑改材质暗色、碎点）、12 倍下看脸（眼睛、嘴落在整格上）、`rigkit.holes` 数封闭透明格；和现在的她、泽丽、原版英雄按游戏大小并排，给用户挑 Q1 / Q2。
- 选定后第 2 步动作包：Codex 照英雄联盟的骨架画（`pose_ref.py --head 2.2 --legs 0.75` 渲染每个动作的关键帧 + 骨架图，腿按骨架画、8 倍下逐帧查变形），每个动作约 8 帧：待机、跑步（交叉迈步）、普攻（手一挥）、Q（手向前指把球扔出去）、W（张开双臂）、E（指向队友）、R（下蹲后双手上扬）、受击、死亡（倒地）；动作帧里不画球。
