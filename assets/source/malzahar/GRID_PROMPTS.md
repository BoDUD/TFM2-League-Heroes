# 玛尔扎哈：在游戏格子上整张重画 A-02，并按它补画 B（给 Codex 的提示词）

> 上一轮（第 0 步）你交了 A 的两稿，用户选了 **A-02**（`2_look_A02.png`）。它的长相、配色、姿势都对，但它是约 **8 px 一格、130 格高**，游戏里要的是 **52 格高**（高清 PPU 1.5）；我按格子把它缩下来以后，**眼睛、四颗菱形、手、匕首全糊了**。以前的英雄（格温、泽丽）碰到同样的问题，都是你**直接在游戏格子上整张重画**后变干净的（`4_example_picture.png` / `5_example_sprite.png` 是格温那次你交的图）。这一轮请照那次的做法：
>
> - **A**：把 A-02 在 **19 × 19 px 的固定格子**上重画一遍。**大小、比例、姿势、位置完全照 `1_layout_grid.png`**（就是 A-02 本身，已经放到格子上）：**兜帽尖在第 12 行，长袍下摆最低点在第 63 行（共 52 格高）**，近侧（画面左边）手指尖在第 2 列附近，最宽约 46 格。画面大小不变，只是**每 19 × 19 px 一个颜色**（原来是 8 px 一格，现在格子大了一倍多，细节要按新格子重新安排，不是缩小）。
> - **B**：在 A 重画完以后，用**同一个格子、同一个位置、同一个上半身**（兜帽、脸、围巾、手臂、护腕、手、匕首、腰带、布尾**逐格照抄 A**），只改下半身：袍子只到膝盖，下面露出**蓬松的宝蓝色灯笼裤 → 深灰护胫 → 尖头深洋红靴子**，**两只脚脚尖朝下垂着**、一前一后微微错开（近侧腿在画面左、亮；远侧腿在画面右、稍暗），**靴尖最低点也在第 63 行**（附图 10、11 是英雄联盟原版的悬浮姿势）。
> - **最重要的是头**（照 `3_league_head.png` 和 A-02）：洋红尖顶兜帽，额头**四颗发光的浅蓝白菱形**（排成菱形：上 1、中 2、下 1），每颗**至少 2 × 2 格**、中间有白色亮心；面巾下**两只发白光的眼睛**，每只**至少 2 × 1 格**，看得清。
> - **干净**（和格温那次一样）：每格一个颜色，大块平涂，每种材质 3–4 档；外轮廓一圈 **2 格宽的近黑描边**，里面少用黑；**不要小于一格的细节、不要碎点、不要半格**；最多约 28 色；真透明背景（全硬 alpha，不要半透明雾）。
> - 不画任何特效、地面、影子、文字；**不要画黄色量格线**。

## 附图（压缩包 `malzahar_grid_pack.zip` 里，按顺序附上；一次最多附五张就先附 1、2、3、4、5，B 时再附 1、10、11 和你画好的 A）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_layout_grid.png` | A-02 放在 19 px 格子上（黄线量格子用，红线 = 第 12 行兜帽尖、第 63 行最低点） | **大小、比例、姿势、位置**（不要画黄线、红线） |
| `2_look_A02.png` | A-02 原稿（用户选的） | 长相、配色、部件 |
| `3_league_head.png` | 英雄联盟里他的头和上身（本地渲染） | 兜帽、四颗菱形、眼睛、围巾 |
| `4_example_picture.png` | 格温：你上次在格子上重画的图（用户认可，26 px 一格） | 怎么画：每格一个颜色 |
| `5_example_sprite.png` | 同一张的 1 倍图放大 8 倍 | 干净程度 |
| `6_style_galio.png` … `9_style_nidalee.png` | 包里 1.5 密度的英雄（8 倍放大，一格 = 一个像素） | 质量标准、描边粗细 |
| `10_league_front.png` | 英雄联盟原版待机 3/4 朝右 | **B 的下半身**：灯笼裤、护胫、尖头靴、脚尖朝下 |
| `11_league_side.png` | 英雄联盟原版待机侧面 | B 悬浮时腿的样子 |

## 提示词 A：`malzahar-grid-A.png`

附图 1、2、3、4、5。

```text
Five attached images. Image 1 is the approved picture of this character placed on a measuring grid of 19x19-pixel squares (yellow lines; red lines mark row 12 and row 63): its SIZE, PROPORTIONS, POSE and PLACE are exactly what to keep - but it was drawn on small ~8-pixel squares and must now be drawn again on the BIG 19-pixel grid. Image 2 is the same picture without the grid: the LOOK to copy (shapes, colours, parts). Image 3 is the character's head on his in-game 3D model: the hood, the four glowing diamond marks, the glowing eyes. Image 4 is another character redrawn correctly on such a grid, and image 5 that sprite at 1x enlarged - copy that way of working: every square one flat colour, big clean areas, no half squares, no soft edges.
Create ONE pixel-art picture of Malzahar, a 1024x1536 PORTRAIT PNG with a real, fully transparent background (hard alpha only, no haze), drawn on a FIXED GRID of 19x19-pixel squares aligned to the canvas's top-left corner (53 columns x 80 rows; the right 17 px and the bottom 16 px transparent). Every square is exactly one flat colour. The figure is exactly 52 squares tall: the tip of the hood on row 12, the lowest point of the floating robe on row 63; the near hand's fingertips at about column 2; about 46 squares wide; the same pose, layout and place as image 1 - floating, 3/4 view facing image right, the near arm (image left) spread out and down with the palm up, the far arm (image right) raised out to shoulder height with the palm up, the curved dagger across the belt pointing left, the magenta cloth tail fluttering down on the image right, the royal-blue robe covering the legs, its hem floating.
His look (image 2): a tall pointed magenta hood with its tip bending back; on its front FOUR GLOWING PALE BLUE-WHITE DIAMOND MARKS arranged as a diamond (one on top, two in the middle, one below), EACH AT LEAST 2x2 SQUARES with a white centre; the face in shadow under the hood, a magenta face cloth, TWO GLOWING WHITE EYES, EACH AT LEAST 2x1 SQUARES; a big thick magenta scarf in heavy folds round the neck and shoulders; an open royal-blue robe over a bare greyish-tan chest with abs, a magenta inner tunic, a dark belt; big flared lilac-grey metal bracers; big dark navy gloved hands with spread fingers; the dagger's blue-grey sheath with golden scrolls and a golden hilt guard; the long magenta cloth tail with a violet pattern.
Clean: big flat areas, every material in 3-4 flat shades, a TWO-SQUARE-THICK near-black outline around the silhouette, little black inside, nothing smaller than one square, no specks, at most about 28 colours. No yellow or red lines, no effects, no ground, no shadow, no text.
```

## 提示词 B：`malzahar-grid-B.png`

附图 1、10、11，以及你刚画好的 `malzahar-grid-A.png`（作为第 4 张）。

```text
Four attached images. Image 4 is the character you just redrew on a fixed grid of 19x19-pixel squares (version A). Draw version B on THE SAME GRID, in THE SAME PLACE: copy A's upper body square for square - the hood with its four diamond marks, the eyes, the scarf, both arms, bracers and hands, the dagger, the belt, the cloth tail - and change only the lower body, the way the character floats in his game (images 2 and 3, his in-game model from the front and from the side): the royal-blue robe ends at the knees; under it PUFFY ROYAL-BLUE TROUSERS gathered into DARK GREY SHIN GUARDS, then POINTED DARK MAGENTA BOOTS; both feet HANG WITH THE TOES POINTING DOWN, one a little in front of the other, the near leg on the image left in full tone, the far leg on the image right a shade darker; the lowest point (the boot tips) on row 63, as A's hem. Image 1 shows the grid and the place.
A 1024x1536 PORTRAIT PNG with a real, fully transparent background (hard alpha only), 53 x 80 squares of 19x19 px aligned to the top-left corner, every square one flat colour, a two-square-thick near-black outline, nothing smaller than one square, no specks, no lines, no effects, no ground, no shadow, no text.
```

## 交回前请检查

- 1024×1536、真透明背景（全硬 alpha，没有半透明雾）；**每 19×19 px 一个颜色，格子从左上角对齐**（可以自己按格子取色检查）。
- 兜帽尖在第 12 行，最低点（A 下摆 / B 靴尖）在第 63 行；姿势、位置和 `1_layout_grid.png` 一致。
- 四颗菱形每颗至少 2×2 格、有白心；两只眼睛每只至少 2×1 格，清楚。
- B 的上半身和 A 逐格相同，只有下半身不同。
- 外轮廓 2 格近黑描边；没有小于一格的细节、碎点、黄线、红线、特效。
- 交付：`outputs/malzahar-grid/malzahar-grid-A.png`、`malzahar-grid-B.png`，每张再附一张 **1 倍读回图**（`malzahar-grid-A_1x.png`、`malzahar-grid-B_1x.png`，53 × 80，一格一个像素）；`generation-prompts.txt`；**所有原始生成稿原样放 `raw/`**；**最后**写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/malzahar/codex_grid/`；先看 raw/，用 regrid.py 按原稿自己的格子读回（不信 Codex 的 1x 读回），和 Codex 的读回并排；兜帽尖到最低点应为 52 格。
- 在游戏实际大小（PPU 1.5 → 约 35 游戏像素高）和 2×/6× 下，与加里奥 hd_idle、布隆/泽丽 lo_idle 并排给用户挑 A / B。
- 选定后写第 1 步：正面（就是这张）+ 侧面（朝右）；或者用户像巴德/赛恩那样决定只用 3/4 正面做所有动作——先问。
