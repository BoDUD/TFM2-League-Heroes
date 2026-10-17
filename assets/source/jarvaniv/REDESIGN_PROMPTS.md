# 嘉文四世：造型重画（第 1 步重做，给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> 用户采用的造型（`1_design_now.png`，10 倍放大，一格 = 一个像素；每个游戏像素 1.5 格，从头盔顶到鞋底 60 格）**整体不变**，这一轮在**同一个网格**上重画，只改三处：
> 1. **脸要清楚。** 在游戏尺寸下现在的脸太糊（`6_face_now.png`）：眼睛只有一两个暗格，看不出眼白和瞳孔。
> 2. **两条腿分开一点。** 近侧那条腿（画面左边）整条往左移 3 格，让两条小腿之间空出约 5 格。现在两腿只隔 2 格，走路时会叠成一条粗腿。远侧那条腿不动，因为骑枪立在它旁边。
> 3. **护膝离开裙甲。** 裙甲短 2 格（下沿从 y 732 提到 **y 708**），裙甲下面不再有垂在两膝之间的布片。裙甲下沿和两个护膝之间露出 **2 格深藏青色的护腿（大腿）**，英雄联盟原版就是这样（`5_league.png`）。护膝、胫甲、靴子的样子和大小都不变。
>
> 其余部分都和 `1_design_now.png` 一样：头盔、尖角、额前蓝宝石、羽冠、肩甲和银刺、胸甲、两只手臂、骑枪、配色、大小、站的位置。**画两稿。**

## 大小和位置（照 `2_target.png` / `3_layout.png`）

- 画布 **1024 × 1024**，**每格 12 px**，网格从画布左上角 (0, 0) 开始对齐（`3_layout.png` 的浅灰线每 5 格一条）。
- **头盔顶 y 240**（绿线），**下巴 y 420**（蓝线），**裙甲下沿 y 708**（橙线），**护膝上沿 y 732**（紫线），**两只鞋底 y 960**（红线）。
- 人和骑枪的位置、宽度照 `2_target.png`：**35 × 73 格**，骑枪竖在身前偏右，枪尖约在 y 84，杆尾落在远侧那只脚旁边的地面上。
- `2_target.png` 是我把三处改动直接按整格挪好的草图，**位置和大小都对，但接缝很粗糙**：护腿只是两条平涂的色块，裙甲少了两行，近侧腿是整条平移过去的。请按它的位置重新画顺。

## 三处改动的细节

- **脸**（`4_head.png` 是你第 0 步画的头，8 倍放大，照它的五官画）：
  - 头盔顶到下巴还是 15 格，但露出的脸**大一点、清楚一点**。头发和头盔两侧的护颊不要盖住眼睛和脸颊。
  - **两只眼睛一样大、一样高**：每只约 2 格宽，一格眼白、一格深色瞳孔，上面一条深色眼线；眉毛深色。
  - 鼻子一个阴影格，嘴 1–2 个暗格，下巴和脸颊的轮廓清楚；肉色 3 档（亮、中、暗）。
- **腿**：
  - 近侧腿（护膝、胫甲、靴子）和现在**一模一样**，只是整条往左移 3 格。
  - 两条小腿之间是**空的背景**（透明），没有布、没有描边连着。
- **裙甲和护腿**：
  - 裙甲还是现在的样子（金边、蓝宝石、深藏青的布、亮边），只是短 2 格，下沿是一条完整的近黑描边。
  - 裙甲下沿和护膝之间，每条腿露出 2 格高的**深藏青护腿**，宽度和护膝一样，带一格亮一点的边。护腿上端被裙甲盖住，下端插进护膝里。

## 干净

- 和附图 `style/7–9`（本包的潘森、斯维因、贾克斯，每游戏像素 1.5 格，和嘉文一样；8 倍放大，一格 = 一个像素）一样的像素画：大小一致的方块、对齐网格，3–4 档平涂，不要抖动、渐变、柔光。
- 只用 `1_design_now.png` 里的颜色（脸可以加一档肉色）。一圈近黑外描边，连续不断；描边里面每种材质用它自己最暗的一档，不要再一圈黑；没有孤立的杂色格。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效。

## 附图（压缩包 `jarvaniv_redesign_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_design_now.png` | 用户采用的造型（10 倍） | **样子、颜色、细节**全照它 |
| `2_target.png` | 三处改动按整格挪好的草图，1024 画布、每格 12 px | **大小、位置、比例、姿势**照它，接缝重新画顺 |
| `3_layout.png` | 同一张加网格线和五条横线（头盔顶、下巴、裙甲下沿、护膝上沿、地面） | 对齐网格和各条线的位置 |
| `4_head.png` | 你第 0 步画的头（8 倍） | **五官**照它画清楚 |
| `5_league.png` | 英雄联盟里嘉文的待机（3D 模型） | 裙甲下面露出的**深色护腿** |
| `6_face_now.png` | 现在造型的头（12 倍） | 太糊的样子，**不要照它** |
| `style/7–9` | 潘森、斯维因、贾克斯（每游戏像素 1.5 格，8 倍） | **只看风格**：这个密度下脸、眼睛、金甲怎么画 |

## 提示词：`jarvaniv-redesign-1.png`、`jarvaniv-redesign-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art sprite of this character, 10x enlarged so one square is one pixel - a young prince in gold plate armour: a gold crown-like helmet with upright spikes and bright blue gems, a dark-blue plume flowing back, a young face; two huge gold pauldrons edged with curved silver-grey spikes, a gold breastplate, a gold-trimmed armour skirt over dark navy-violet cloth, gold knee guards with blue gems, segmented gold greaves and gold boots; a very long lance standing upright in front of him on the image right (silver-white barbed spearhead far above the helmet, a silver guard with a blue gem, a dark shaft, the butt on the ground by his far foot), his far hand gripping the shaft (the LOOK, the COLOURS and the DETAILS to keep); 2 the same sprite on its final 1024x1024 canvas at 12 px a square with three changes roughly made by moving whole squares - the SIZE, the PLACE and the POSE are right but the seams are rough; 3 the same with grid lines every 5 squares and five lines: green = top of the helmet (y 240), blue = chin (y 420), orange = the skirt's new hem (y 708), purple = top of the knee guards (y 732), red = the ground (y 960); 4 his head as first painted, enlarged (the FACE to draw clearly); 5 the same character as a 3D model, standing: dark navy legs show between the armour skirt and the gold knee guards; 6 the current sprite's head, 12x - too muddy, do NOT copy its face; 7-9 STYLE ONLY: other characters from the same game at this same square density, 8x.
Redraw with the image generator ONE clean pixel-art sprite: a 1024x1024 PNG with a real transparent background (alpha only 0 or 255), every square 12 px on one straight grid starting at the canvas corner, EXACTLY the size, place and pose of image 2 (35 x 73 squares, helmet top y 240, chin y 420, soles on y 960, the lance's tip at about y 84), everything looking exactly like image 1 except three changes:
1 THE FACE CLEAR: the head still 15 squares from helmet top to chin, but more of the face showing (the hair and the helmet's cheek plates do not cover the eyes or cheeks); TWO EYES of the SAME size at the SAME height, each about 2 squares wide - one white square and one dark pupil square with a dark lash line above - dark eyebrows, one shadow square for the nose, a 1-2 square mouth, a clear jaw and chin; skin in 3 shades.
2 THE LEGS APART: the near leg (image left: knee guard, greave, boot) moved 3 squares further left, unchanged in shape and size, so about 5 squares of empty transparent background separate the two shins; the far leg stays where it is, next to the lance.
3 THE KNEE GUARDS CLEAR OF THE SKIRT: the armour skirt 2 squares shorter, its hem one clean near-black line at y 708, nothing of it hanging between the knees; between the hem and each knee guard 2 squares of dark navy leggings (as wide as the knee guard, with a lighter edge), their tops under the skirt, their bottoms into the knee guards; the knee guards, greaves and boots exactly as in image 1.
Keep every other square as in image 1: the helmet, spikes, gems, plume, pauldrons and spikes, breastplate, both arms, the lance, the colours. One continuous near-black outline round the figure; inside it every material's shadow in its own darkest shade (never a second black ring); no stray single squares, no dithering, no gradients, no soft glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张图都是 image_gen 画的**（不是脚本写的格子图）；1024 × 1024；真透明背景，**alpha 只有 0 / 255**；每格 12 px、对齐网格。
- 大小、位置和 `2_target.png` 一样：头盔顶 y 240、下巴 y 420、裙甲下沿 y 708、护膝上沿 y 732、鞋底 y 960；枪尖约 y 84。
- 脸清楚：两只眼睛一样大一样高、看得出眼白和瞳孔，鼻子、嘴、下巴分得出来。
- 两条小腿之间空出约 5 格透明背景；近侧腿和原来一样大、一样样子。
- 裙甲短 2 格、两膝之间没有垂下的布；每条腿露出 2 格深藏青护腿；护膝、胫甲、靴子和原来一样。
- 其余（头盔、肩甲、胸甲、手臂、骑枪、颜色）和 `1_design_now.png` 一样；外描边连续；没有任何特效。

## 交付（`outputs/jarvaniv-redesign/`）

- `jarvaniv-redesign-1.png`、`jarvaniv-redesign-2.png`；**image_gen 的原始生成图原样放 `outputs/jarvaniv-redesign/raw/`**（不要再处理成格子图）；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/jarvaniv_redesign_done.zip`，这样我这边知道已经交付完了。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 原稿在 8 倍下数描边台阶量格子大小，按它自己的格子读回（12 px；若交的是 1254 等别的画布，先量），和 `1_design_now.png` 逐格比：三处改动以外的格子应该基本不变；量两腿间距、护腿高度、眼睛。
- 两稿按游戏大小和旧造型、潘森、赵信、盖伦放在一起，加脸的放大图，给用户挑一稿（用户审核，不要自己判定）。
- 选定后：`hd/design.png` 换成新稿，`tools/art/rig_jarvaniv.py` 的部件坐标（腿、裙甲、手臂、骑枪）按新造型重量，所有动作重新摆（无损，塔姆的方式）；走路用造型自己的整条腿（内瑟斯被认可的走法：每条腿整块平移，近侧往前、远侧往后，抬脚只抬到护腿里，不碰护膝），**不再用 Codex 画腿**。
