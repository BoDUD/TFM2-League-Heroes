# 影哨 阿克尚：游戏尺寸造型补画（第 1 步第 2 轮，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 上一轮你画的 **A-1 样子很好**（`1_picked_A1.png`，用户要的就是这个样子），**但格子画小了、人画大了**：要求每格 15 px，你实际画的是**每格约 10 px**，于是人从头顶到鞋底有 **83 格**，而游戏要的是 **57 格**。
> - 我把 A-1 删行删列缩到 57 格（`2_target_A.png`，**每格 10 px**，放在 1254 × 1254 画布上）：**大小、位置、姿势都对**，脸也保住了，**但身体被切出了条纹**：橙红饰带和金箍断成几截，披风里一道道竖条，青绿布片歪了，枪身和两道弯钩缺了格子、成了碎块，靴子缺角。
> - **这一轮就用你自己习惯的每格 10 px，在同样的位置把这个 57 格的人重画清楚**：同样大小、同样位置、同样姿势，**人在画布上比上一轮小很多，这是对的，不要放大**。画两稿。

## 大小和位置（照 `2_target_A.png` / `3_layout_A.png`）

- 画布 **1254 × 1254**，**每格 10 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout_A.png` 的浅灰线每 5 格一条）。
- **头顶头发在 y = 630**（绿线），**两只鞋底在 y = 1200**（红线），中间正好 **57 格（570 px）**；**枪的最上端在 y ≈ 490**；人从 **x ≈ 390**（举起的枪）到 **x ≈ 860**（披风右下角），**约 47 格宽、71 格高（连枪）**。
- **人只占画布下面中间的一块，上面和两边大片透明是对的**。千万不要把人画大来占满画布（上一轮就是这样多出了 26 行）。

## 要画清楚的地方（格子少了，每样东西用的格子要精打细算）

- **脸**（`4_face.png` 是上一轮 A-1 的头，8 倍放大）：照它画，但这次整个头只有约 19 格高：
  - 深棕长卷发 3 档，头顶小发髻（2–3 格）；
  - **两只眼睛一样大、一样高、都看得见：每只 2 格宽**（1 格眼白 + 1 格深色瞳孔，上面一格深色眉毛），这是最重要的一点；
  - 短胡子比头发浅一档，沿下巴；嘴 1 行。
- **上身**：浅蓝白围巾（2 档）；灰护肩带 1 格金边；赤膊棕色胸口有亮边；**橙红饰带斜挎、宽 3 格、中间一块金箍连成一条完整的斜带**（不要断）。
- **手**：举枪的近侧手：金护腕 + 浅蓝手套；远侧手叉腰：金护腕 + 浅蓝手套。
- **下身**：青绿腰带和**一条直的青绿长布片**（3 格宽，中间 1 个金环）；深灰黑裤子 3 档有亮边；黑靴有亮边和 1 行金饰。
- **披风**：暗红长披风垂在两边，**3 档平涂、有亮边、没有竖条纹**，下摆金色卷边。
- **枪**：**完整、轮廓连续**：枪身直，暗红带青铜，前端两道弯钩朝上张开，每道 **2–3 格粗**、有亮边和橙色高光；握把青白。
- **一圈近黑外描边**，连续不断；描边里面每种材质用它自己最暗的一档；没有孤立的杂色格。

## 干净

- 和附图 5–7（本包的普朗克、赵信、悟空，**和阿克尚一样的格子密度**，8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**（上一轮大部分是 253，这次一定要 255）。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `akshan_model_pack2.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_picked_A1.png` | 你上一轮画的 A-1 | **样子、颜色、细节**全照它 |
| `2_target_A.png` | A-1 缩到 57 格、每格 10 px 放在画布上（有条纹、缺格） | **大小、位置、姿势**照它，条纹和缺格的地方重画 |
| `3_layout_A.png` | 同一张加网格线：绿线 = 头顶，红线 = 地面 | 对齐网格、头顶和地面线的位置 |
| `4_face.png` | A-1 的头，8 倍放大 | 卷发和发髻、脸、眼睛、胡子 |
| `style/5_style_gangplank.png` … `7_style_wukong.png` | 本包的普朗克、赵信、悟空，8 倍放大 | **只看风格**：这个格子密度下手枪、胡子、暗色衣服的亮边怎么画 |

## 提示词：`akshan-model2-A-1.png`、`akshan-model2-A-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 your own previous pixel-art take of a ROGUE GUNSLINGER (brown skin, long wavy dark-brown hair with a small topknot, a short beard; a pale blue-white scarf, grey gold-trimmed shoulder pads, a bare chest, a wide orange-red sash slung diagonally with a gold band, a long dark-red cape, a teal belt and a long teal front cloth with a gold ring, dark grey-black trousers, tall black boots, gold bracers, pale blue fingerless gloves; a big dark-crimson-and-bronze relic pistol with two curved boomerang-like hooks at its front; standing upright, the near hand raising the gun beside his head pointing up, the far hand on his hip) - the LOOK, the COLOURS and the DETAILS to keep; it was drawn too big; 2 that take cut down to its final game size on a 1254x1254 canvas with 10 px squares - the SIZE, the PLACE and the POSE are right, but the cut striped it (the sash and its gold band broken, vertical stripes in the cape, the teal cloth crooked, the gun and its hooks broken into pieces, the boots chipped); 3 the same with grid lines every 5 squares: the green line = the top of his hair, the red line = the ground; 4 his head enlarged; 5-7 STYLE ONLY: other characters from the same game at this SAME square density, shown 8x so every square is one pixel.
Draw with the image generator ONE clean pixel-art picture of the gunslinger: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255). EXACTLY the size, place and pose of image 2: every square 10 px, aligned on one straight grid starting at the canvas corner, the top of his hair at y 630, both soles on the ground line y 1200 (57 squares, 570 px, from the hair to the soles), the top of the raised gun at about y 490, the figure from about x 390 to about x 860 (about 47 squares wide, 71 tall with the gun). The figure is SMALL on the canvas, in the lower middle, with wide transparent space above and on both sides - that is right: do NOT enlarge it to fill the canvas. Redraw image 2 cleanly, as if a pixel artist redrew image 1 at this smaller size square by square.
Make it CRISP and READABLE at this size: the hair in 3 shades with the small topknot (2-3 squares); TWO EYES of the SAME size at the SAME height, both visible, EACH 2 SQUARES WIDE (one white square and one dark pupil square) with a dark brow above - the most important point; the beard a shade lighter than the hair; the pale blue-white scarf in 2 shades; the grey shoulder pads with a 1-square gold rim; the brown chest with lighter edges; the orange-red sash ONE UNBROKEN DIAGONAL BAND 3 squares wide with its gold band; gold bracers and pale blue gloves on both hands; the teal belt and ONE STRAIGHT teal front cloth 3 squares wide with a gold ring; the dark grey-black trousers in 3 shades with lighter edges; black boots with lit edges and one row of gold; the dark-red cape in 3 flat shades with lighter edges and NO vertical stripes, gold curled hems; the gun WHOLE with an unbroken outline: a straight body, dark crimson with bronze, two hooks spread at the top each 2-3 squares thick with a lit edge and orange highlights, the pale teal-white grip.
One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**。
- **人小**：头顶 y 630、鞋底 y 1200（57 格，每格 10 px），枪顶约 y 490，约 47 × 71 格；上面和两边大片透明。
- **两只眼睛一样大、一样高、每只 2 格宽**；小发髻；胡子。
- 饰带是一条完整的斜带；披风没有竖条纹；青绿布片是直的；枪完整、两道弯钩连续。
- 外描边连续；没有任何特效。

## 交付（`outputs/akshan-model2/`）

- `akshan-model2-A-1.png`、`akshan-model2-A-2.png`；**image_gen 的原始生成图原样放 `outputs/akshan-model2/raw/`**；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/akshan_model2_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小（这次应是 10 px），按它自己的格子读回；头顶到鞋底应该就是 57 行左右，最多删两三行（不经过脸和眼睛）。和 `2_target_A.png`、上一轮 A-1 并排检查饰带、披风、布片、枪是否完整，再做动作（茂凯 / 悟空 / 塔姆的方式）。
