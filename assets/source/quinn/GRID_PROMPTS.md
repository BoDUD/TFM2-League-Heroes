# 奎因：在更细的格子上整张重画定稿（PPU 2.0；给 Codex 的提示词）

> 奎因的动作已经定稿，但她现在是**每个游戏像素 1.3 格**（待机 45 × 49 格），用户觉得「像素有点太低了，太多模糊的了」，要调到 **PPU 2.0**：同样的 38 个游戏像素高，要画成 **75 格高**。按格子放大或缩小原图都会糊；以前的英雄（格温、玛尔扎哈）碰到同样的问题，都是你**直接在新格子上整张重画**以后变干净的（`5_example_picture.png` / `6_example_sprite.png` 是格温那次你交的图）。这一轮请照那次的做法，重画两张：
>
> - **A 待机**：把定稿的待机（`2_look_idle.png`）在 **13 × 13 px 的固定格子**上重画一遍。**大小、比例、姿势、位置完全照 `1_layout_idle.png`**（就是定稿本身，已经放大放到新格子上）：**鹰翼面甲的顶在第 21 行，靴底在第 95 行（共 75 格高）**，披风最左边在第 4 列，弩的最右端在第 72 列附近。格子比原来细了一半多，**多出来的格子用来把细节画清楚**（不是把原来的大方块放大）。画两稿（A-1、A-2），主要在脸上有区别。
> - **B 骑乘**：把定稿的骑乘（`8_look_ride.png`，她骑在华洛背上）在 **同样 13 × 13 px 的格子**上重画，横版画布，**大小、姿势、位置照 `7_layout_ride.png`**：**最高点在第 3 行，最低点在第 73 行（共 71 格高）**，最左第 7 列，最右第 109 列附近。她的头、脸**照你画好的 A-1 逐格照抄**。
> - **脸最重要**（照 `2_look_idle.png`、`3_picture_A.png` 和 `4_league_head.png`）：大眼睛，**每只眼至少 3 × 3 格**，琥珀棕色的虹膜、深色的瞳孔、白色高光，细眉毛，小鼻子一点阴影，红唇；黑发从面甲下垂到脸两边。
> - **要画清楚的细节**：金色鹰翼面甲（中间的冠、两侧的翼）、深蓝兜帽的褶子、金色羽毛肩甲（一片一片的羽毛）、蓝紫披风和金边、棕色皮胸甲的系带和金扣、手腕上的金钢色弩（金色的弩翼、钢色的弩身和弦、箭槽）、紫色护腿和金色护膝、尖头棕靴；B 里华洛的每片大羽毛（深蓝紫色、亮蓝的羽尖）、金色的喙和爪。
> - **干净**（和格温那次一样）：每格一个颜色，大块平涂，每种材质 3–4 档、光从左上来；外轮廓一圈 **2 格宽的近黑描边**（`#090013`），里面少用黑；**不要小于一格的细节、不要碎点、不要半格**；最多约 32 色，颜色照定稿；真透明背景（全硬 alpha，不要半透明雾）。
> - 不画任何特效、地面、影子、文字；**不要画黄色量格线和红线**。

## 附图（压缩包 `quinn_grid_pack.zip` 里；一次最多附五张就先附 1、2、3、4、5，画 B 时附 7、8、9 和你画好的 A-1）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_layout_idle.png` | 定稿待机放到 13 px 格子上（黄线量格子用，红线 = 第 21 行面甲顶、第 95 行靴底） | **A 的大小、比例、姿势、位置** |
| `2_look_idle.png` | 定稿待机（12 倍放大，一格 = 一个方块） | 部件、配色（要保留的一切） |
| `3_picture_A.png` | 第 0 步你画的大图 A | 更多细节：脸、面甲、弩、羽毛 |
| `4_league_head.png` | 英雄联盟里她的头（本地渲染） | 脸的特点 |
| `5_example_picture.png` | 格温：你上次在格子上重画的图（用户认可） | 怎么画：每格一个颜色 |
| `6_example_sprite.png` | 同一张的 1 倍图放大 8 倍 | 干净程度 |
| `7_layout_ride.png` | 定稿骑乘放到 13 px 横版格子上（红线 = 第 3 行、第 73 行） | **B 的大小、姿势、位置** |
| `8_look_ride.png` | 定稿骑乘（10 倍放大） | 华洛和她的部件、配色 |
| `9_picture_R.png` | 第 0 步你画的骑乘大图 | 华洛的羽毛、喙、爪 |
| `10_style_braum.png` … `12_style_mordekaiser.png` | 包里密度约 2 的英雄（6 倍放大，一格 = 一个像素） | 质量标准、描边粗细 |

## 提示词 A：`quinn-grid-A-1.png`、`quinn-grid-A-2.png`

附图 1、2、3、4、5（还能附就加 6）。各画一次。

```text
Five attached images. Image 1 is the approved pixel-art sprite of this character enlarged onto a measuring grid of 13x13-pixel squares (yellow lines; red lines mark row 21 and row 95): its SIZE, PROPORTIONS, POSE and PLACE are exactly what to keep - but it was drawn on a coarse grid (its big blocks are about 1.5 grid squares each) and must now be drawn again on the FINE 13-pixel grid, using the extra squares for clear detail. Image 2 is the same approved sprite enlarged without the grid: every part and colour to keep. Image 3 is an earlier big painting of her: more detail for the face, the visor, the crossbow and the feathers. Image 4 is her head on her in-game 3D model: the face's character. Image 5 is another character redrawn correctly on such a grid - copy that way of working: every square one flat colour, big clean areas, no half squares, no soft edges.
Create ONE pixel-art picture of Quinn, a 1024x1536 PORTRAIT PNG with a real, fully transparent background (hard alpha only, no haze), drawn on a FIXED GRID of 13x13-pixel squares aligned to the canvas's top-left corner (78 columns x 118 rows; the right 10 px and the bottom 2 px transparent). Every square is exactly one flat colour. The figure is exactly 75 squares tall: the top of the golden winged visor on row 21, the boot soles on row 95; the cape's left edge at column 4, the crossbow's front tip at about column 72; the same pose, layout and place as image 1 - standing in a 3/4 view facing image right, the crossbow on her far wrist held straight out to the right at shoulder height, the near arm down, the cape hanging behind on the left, the near leg on the image left, the far leg on the image right, both boots on row 95.
Her look (images 2 and 3): a golden winged visor (a tall central crest and swept golden wings on both sides) over long black hair falling beside the face; a deep blue hood and collar; a big golden feather pauldron made of separate layered feathers; a blue-violet cape with a gold edge; a brown leather corset with laces and a gold buckle, a gold-trimmed blue skirt; dark violet greaves with golden knee plates and gold stripes down the shins; pointed brown boots; the wrist crossbow in gold and steel (golden swept limbs like wings, a steel stock and string, a bolt in the groove). Her face (image 4): big eyes, EACH AT LEAST 3x3 SQUARES with an amber-brown iris, a dark pupil and a white highlight, thin dark brows, a small nose with a little shadow, red lips.
Clean: big flat areas, every material in 3-4 flat shades lit from the upper left, a TWO-SQUARE-THICK near-black (#090013) outline around the silhouette, little black inside, nothing smaller than one square, no specks, at most about 32 colours taken from image 2. No yellow or red lines, no effects, no ground, no shadow, no text.
```

## 提示词 B：`quinn-grid-B.png`

附图 7、8、9，以及你画好的 `quinn-grid-A-1.png`（作为第 4 张）。

```text
Four attached images. Image 1 is the approved pixel-art sprite of this character riding her giant eagle, enlarged onto a measuring grid of 13x13-pixel squares (yellow lines; red lines mark row 3 and row 73): its SIZE, PROPORTIONS, POSE and PLACE are exactly what to keep, drawn again on the FINE 13-pixel grid with the extra squares used for clear detail. Image 2 is the same approved sprite enlarged without the grid: every part and colour to keep. Image 3 is an earlier big painting of the ride: the eagle's feathers, beak and talons. Image 4 is the rider you just redrew on the same grid: copy her head and face from it square for square.
Create ONE pixel-art picture, a 1536x1024 LANDSCAPE PNG with a real, fully transparent background (hard alpha only), drawn on a FIXED GRID of 13x13-pixel squares aligned to the top-left corner (118 columns x 78 rows; the right 2 px and the bottom 10 px transparent). Every square is exactly one flat colour. The group is exactly 71 squares tall: the highest point on row 3, the lowest on row 73; the leftmost point at column 7, the rightmost at about column 109; the same pose and place as image 1 - the giant eagle Valor gliding to the right with wide wings (deep blue-violet feathers, bright blue feather tips, every big feather a clear shape, a golden beak, golden talons), Quinn riding on his back leaning forward with her wrist crossbow pointing ahead, her cape flying back.
Clean: big flat areas, every material in 3-4 flat shades lit from the upper left, a two-square-thick near-black (#090013) outline around the silhouette, little black inside, nothing smaller than one square, no specks, at most about 32 colours. No yellow or red lines, no effects, no ground, no shadow, no text.
```

## 交回前请检查

- A：1024 × 1536；B：1536 × 1024；真透明背景（全硬 alpha，没有半透明雾）；**每 13 × 13 px 一个颜色，格子从左上角对齐**（可以自己按格子取色检查）。
- A 面甲顶在第 21 行、靴底在第 95 行；B 最高点第 3 行、最低点第 73 行；姿势、位置和 `1_layout_idle.png` / `7_layout_ride.png` 一致。
- 眼睛每只至少 3 × 3 格，清楚；B 里她的头和 A-1 逐格相同。
- 外轮廓 2 格近黑描边；没有小于一格的细节、碎点、黄线、红线、特效。
- 交付：`outputs/quinn-grid/quinn-grid-A-1.png`、`quinn-grid-A-2.png`、`quinn-grid-B.png`，每张再附一张 **1 倍读回图**（`*_1x.png`，一格一个像素：A 是 78 × 118，B 是 118 × 78）；`generation-prompts.txt`；**所有原始生成稿原样放 `raw/`**；**最后**写 `HANDOFF.md`，打包成 `outputs/quinn_grid_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/quinn/codex_grid/`；先看 raw/，用 regrid.py 按原稿自己的格子读回（不信 Codex 的 1x 读回），和 Codex 的读回并排；面甲顶到靴底应为 75 格。
- 在游戏实际大小（PPU 2.0 → 约 38 游戏像素高）和 4× 下，和现在的 1.3 版、密度约 2 的英雄并排给用户挑 A-1 / A-2。
- 选定后：hd/idle.png、hd/ride.png 换成新稿（`ride_design` 照样把待机的头贴到骑乘上），rig_quinn.py / quinn_legs.py 的部位常数在新稿上重新量（肩、手腕、腿的行、靴子、披风下摆），PPU 1.3 → 2.0（ppu_restyle ORIG_PPU / RESTYLE、ppu_hd PPU、hd.rs），动作照原样重出，8 倍自查后给用户看合并 GIF。
