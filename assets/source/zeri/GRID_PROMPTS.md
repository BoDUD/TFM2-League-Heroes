# 泽丽：在游戏格子上整张重画（给 Codex 的提示词）

> 现在的泽丽（`zeri/1_current_grid.png`）是把用户自己的原图（`2_picture.png`，72 格高）按格子缩到 40 格再手修出来的，脸用了上一轮你画的 C 方案。用户的意见：**「模型整体还是太糊」「眼睛我还是挺不满意的，没有泽丽的特色」**。以前的英雄（格温、莉莉娅、劫）碰到同样的问题，都是你**直接在游戏格子上整张重画**后变干净的（`4_example_picture.png` / `5_example_sprite.png` 是格温那次你交的图）。这一轮请照那次的做法，把泽丽在格子上重画一遍。
>
> - **大小、比例、姿势、位置照 `1_current_grid.png`**（用户认可了）：40 格高（发髻尖第 12 行到鞋底第 51 行），最宽约 24 格，两脚中间在第 19 列；右手竖握步枪靠在画面右侧肩旁，左手垂下；头（发髻尖到下巴）约 15 行。
> - **长相照用户原图 `2_picture.png`**：两个尖刺发髻（青蓝 + 紫 + 橙，底下一圈柠檬绿尖刺）、藏青发带带橙红边、柠檬绿头发夹几缕青蓝、超大青蓝外套 + 白毛领 + 方扣/银管/心形扣、黄色短背心 + 粉绿闪电印花、红腰带 + 白圆扣、斜挎带、紫红紧身裤 + 膝盖补丁 + 橙护膝、棕靴 + 银扣 + 黄鞋头、右靴橙黄袜口；柠檬绿 + 深灰 + 橙的步枪，两根电极、银钉、两个圆座。
> - **脸要有泽丽的特色（这一轮最重要）**，照 `3_league_face.png`（英雄联盟里她的模型）：**又粗又深的弯眉**、**黑色上眼线带一点外挑**、**黄绿色的大眼睛**（眼白 + 黄绿瞳 + 一格白高光）、**珊瑚色饱满的嘴唇带一点笑**、左脸颊（画面左侧）白色创可贴；自信、俏皮。3/4 朝画面右。
> - **干净（和格温那次一样）**：每格一个颜色，大块平涂，每种材质 3–4 档，一圈近黑描边，里面少用黑；不要小于一格的细节、不要碎点；最多约 24 色。
> - `7_rejected_faces.png` 是用户不要的三版脸。

## 附图（压缩包 `zeri_grid_pack.zip` 的 `zeri/` 里，按顺序附上；一次最多附五张就先附 1、2、3、4、5）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_current_grid.png` | 现在的泽丽，每格 26 px，黄线是量格子用的 | 大小、比例、姿势、位置（不要画黄线） |
| `2_picture.png` | 用户自己的泽丽原图 | 长相、配色、部件 |
| `3_league_face.png` | 英雄联盟里泽丽模型的脸（本地渲染） | **眉毛、眼线、眼睛颜色、嘴唇——她的特色** |
| `4_example_picture.png` | 格温：你上次在 26 px 格子上重画的图（用户认可） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张的 1 倍图放大 8 倍 | 干净程度 |
| `6_quality_bar.png` | 用户认可过的英雄（格温、阿卡丽、莎弥拉、辛德拉、萨勒芬妮）8 倍 | 质量标准 |
| `7_rejected_faces.png` | 用户不要的三版脸 | 不要这样 |
| `current_1x.png` | 现在的 1 倍图（39 × 59） | 对位置 |

## 提示词

```text
Five attached images (more references in the pack: a quality bar and three rejected faces). Image 1 is this character's CURRENT game sprite, each square drawn 26x26 px with a yellow measuring grid: the SIZE, PROPORTIONS, POSE and PLACE to keep (the user approved them) - but its colours are muddy and its face lacks the character's look. Image 2 is the user's own picture of her: the LOOK to copy (costume, colours, parts). Image 3 is the character's face on her in-game 3D model: copy her FACE'S CHARACTER from it. Image 4 is another character redrawn correctly on such a grid, and image 5 that sprite at 1x enlarged - copy that way of working: every square one flat colour, big clean areas, no half squares, no soft edges.
Create ONE pixel-art picture of Zeri, a lively Zaun street girl, a 1024x1536 PORTRAIT PNG with a real transparent background, drawn on a FIXED GRID of 26x26-pixel squares aligned to the canvas edges (39 columns x 59 rows; the right 10 px and the bottom 2 px transparent). The figure is exactly 40 squares tall: the tips of her hair buns on row 12, the soles on row 51; about 24 squares wide; the middle between her feet on column 19; the same pose and layout as image 1: standing 3/4 facing image right, her image-right hand holding an upright electric rifle beside her shoulder (the rifle's two electrodes at the top, rows 12-14), the other arm hanging, feet apart; the head from bun tips to chin about 15 rows.
Her look (image 2): two spiky hair buns (teal-blue spikes with a violet spike and an orange core, a ring of lime spikes at their base), a navy headband with an orange-red edge, bright lime hair with a few teal-blue strands; an oversized teal coat with a white fur trim along the collar, a white toggle with a thin tan tube down to a white heart-shaped clasp, a yellow crop top with a small pink-and-green lightning print, a red belt with a white ring buckle, a tan diagonal strap; tight maroon leggings with a tan knee patch on the near leg and an orange knee pad on the far leg; brown boots with a silver buckle each and yellow toe caps, an orange-yellow sock cuff on the far boot; maroon fingerless gloves with white cuffs; the rifle lime-yellow with dark grey parts, an orange piece, silver studs and two round sockets, two electrodes with tan tips.
Her FACE (image 3) - the most important part: THICK DARK ARCHED EYEBROWS, a black upper eyeliner with a small flick at the outer corner, big eyes with white and a YELLOW-GREEN iris (a white glint in the near eye), the near eye (image left) the bigger and the far eye narrower, a cheeky confident look, CORAL full lips in a small smile, a white plaster on her cheek on the image-left side under the near eye; the face about 8 squares wide and 7 rows from the brows to the chin.
Clean like image 5: every square one flat colour, 3-4 flat shades per material lit from the upper left, ONE near-black 1-square outline round the silhouette and little black inside (inner edges in each material's own dark shade), details at least one whole square, no specks, no dithering, no gradients, at most about 24 colours. No effects, no glow, no background, no ground, no shadow, no text, no grid lines.
Make THREE takes (A, B, C) that differ mainly in the face. Deliver for each: zeri-grid-<X>.png (the 1024x1536 picture) and zeri-grid-<X>_1x.png, the same picture reduced so that each 26x26 square becomes one pixel (39x59, nearest-neighbour, transparency kept) - the game reads the 1x file, so it must match the big one square for square.
Before finishing, check each take: exactly 40 rows from bun tips (row 12) to soles (row 51); every 26x26 square one colour; alpha only 0/255; at most ~24 colours; the eyebrows, the eyeliner, the yellow-green eyes, the coral lips and the plaster readable at 1x and 2x; both hands and the rifle visible.
```

## 交付（`outputs/zeri-grid/`）

- `zeri-grid-A.png` / `-B.png` / `-C.png`（1024 × 1536）和 `zeri-grid-A_1x.png` …（39 × 59）；
- `zeri-grid-compare.png`：三个方案 1 倍放大 8 倍并排，旁边放 `1_current_grid.png` 的 1 倍图和原图的脸；
- 生图原稿（raw/）、`generation-prompts.txt`、色板、`HANDOFF.md`（**最后写**：高度、宽度、色数、每格是否单色）；最好再打一个 `zeri_grid_pack.zip`。

## Claude 收到后（给 Claude 看）

- 读 1 倍图（核对和大图逐格一致），放回 128 画布（鞋底第 99 行，两脚中间第 64 列），整理（tidy_codex18 的做法：去描边毛刺、内圈黑改材质暗色、去碎点），和现在的、原图、格温并排给用户挑；选定后重做动作帧（rig_zeri.py）。
