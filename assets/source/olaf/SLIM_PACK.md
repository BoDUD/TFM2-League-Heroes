# 奥拉夫：瘦一点、肌肉明显一点（造型小改，给 Codex）

用户看完动作和特效后说：「奥拉夫稍微瘦一点 肌肉明显点」。这一轮只改**造型图的身体**：在已定稿的造型上画两版，用户挑一版；之后动作条会照新造型再改。

## 附图

| 文件 | 内容 |
|---|---|
| `design/olaf_design.png` / `_1x.png` | **现在的定稿**（8 倍 / 原尺寸 128×128）：42 行高，39 格宽（含两把斧），脚底第 99 行，两脚中间第 64 列 |
| `design/olaf_head_1x.png` | 头（双角、角盔、头顶橙发、脸）——**两版都逐格保留，一格都不改** |
| `design/olaf_palette.png` | 全部 21 色 |
| `guide/olaf_width_guide.png` | 定稿 + 绿框（头，不动）+ 蓝线 A 版大约宽度、红线 B 版大约宽度 |
| `refs/lol_olaf.png` | 英雄联盟奥拉夫模型（看肌肉：圆的肩膀、鼓起的二头肌、粗前臂、大腿的肌肉块） |
| `refs/olaf_picture.png` | 用户选的原画 A |
| `refs/pack_heroes.png` | 同一个包里的其他壮汉（德莱厄斯、盖伦、泰达米尔、瑟提）的待机，同样 8 倍：肌肉画法和胖瘦对照 |

## 要改什么

- **瘦一点**：身体（背心、腰带、围腰）窄 2–4 格，两只手臂各细 1–2 格（离我们近的左臂现在约 10 格粗），两条腿各细约 1 格。是**壮而结实**，不是胖：从「宽厚的一大块」变成「倒三角的肌肉身材」——肩膀还是宽的，腰收进去。
  - **A 版**：稍微瘦一点，全身约 36 格宽（含斧）；
  - **B 版**：再瘦一点，全身约 32–33 格宽。
- **肌肉明显**：光着的手臂、肩膀、大腿要看得出肌肉块——圆的三角肌（肩）、鼓起的二头肌、粗壮的前臂（护腕照旧），大腿前面的肌肉隆起。用皮肤的三档颜色画体积：亮面 `#FCB870`、中间 `#D47C48`、暗面 `#A4542E`，肌肉之间用暗面画 1 格的分界，亮面落在每块肌肉鼓起的地方（光从左上来，和定稿一样）；**肌肉里面不要画黑描边**。
- **不改的**：头（逐格保留）、高度（42 行，脚底第 99 行）、站姿（两脚的位置）、两把斧的大小和样子、胡子、鬃发、肩上白毛、背心/腰带/围腰/护胫/靴子的样子和颜色；只用定稿的 21 种颜色；外轮廓 1 格近黑描边。

## 怎么画

- 从 `design/olaf_design_1x.png` 开始**逐格改**（游戏尺寸，一格一个像素），或者在 8 倍的格子上一格一格重画身体；不要整体压缩、不要删整行整列、不要用脚本拼色块。
- 每个像素是对齐网格的 8×8 方块（8 倍图），透明度只有 0 和 255。

## 交付

`outputs/olaf-slim/`：`olaf_design_slim_A.png`、`olaf_design_slim_B.png`（8 倍，1024×1024，和定稿同一张画布、同一个站位）、各自的 `_1x.png`（128×128）、一张 A / 现在 / B 并排的对比图、`HANDOFF.md`（最后写；哪里没做到）。最好打成 zip（`olaf_slim_done.zip`）。

## 提示词（生图时用；附图：定稿 8 倍、英雄联盟模型、壮汉对照）

```text
Edit this approved pixel-art game sprite (FIRST image, 8x: every pixel an 8x8 block) into two slimmer, more muscular versions. Keep EXACTLY, square for square: the head (horned blue-grey helmet, face, orange hair crest), the height (42 squares from the horn tip to the soles), the soles' row, the stance, both axes, the braided orange beard, the orange mane, the white shoulder fur, the dark brown vest, the studded steel belt, the fur loincloth, the spiky greaves and the brown boots - only the body's width and the muscles change.
Slimmer: the torso 2-4 squares narrower, each bare arm 1-2 squares thinner, each leg about 1 square thinner - a strong V-shaped warrior (broad shoulders, the waist drawn in), not a fat block. Version A a little slimmer (about 36 squares wide with the axes), version B slimmer still (about 32).
Clear muscles on the bare arms, shoulders and thighs: round deltoids, a bulging biceps, thick forearms (the leather wraps kept), a bulging thigh - shaped with the skin's three shades (light #FCB870 on each bulge, mid #D47C48, shadow #A4542E as 1-square lines between muscles), light from the upper left; no black lines inside the muscles.
Only the FIRST image's 21 colors, one 1-square near-black outline round the silhouette, no anti-aliasing, no blur, no semi-transparency, same canvas and same standing point as the FIRST image.
```
