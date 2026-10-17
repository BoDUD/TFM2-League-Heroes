# 嘉文四世：跑步只画两条腿（给 Codex 的提示词）

> 嘉文四世跑步的 8 帧（`now/jarvaniv_run_<n>.png`）里，**裙甲下沿以上全部是定好的**：头盔、羽冠、脸、肩甲、胸甲、手臂、扛在肩上的骑枪、腰带和裙甲，**一格都不要动**（绿线以上）。
> `now/` 里每一帧的腿还是站着时那两条直腿（只给你看腿的样子）。这一轮**只画绿线以下的两条腿**（护膝、胫甲、靴子），照英雄联盟原版跑步每一帧的腿部骨架，8 帧连起来是一个跑步循环：
> - **腿的姿势照骨架线**（`guide/jarvaniv_run_<n>.png`）：**红线 = 近侧的腿**（离看画的人近），**蓝线 = 远侧的腿**。线上的点从上到下是：胯（在裙甲里面）、膝盖、脚踝、脚尖。
> - **两条腿轮流在前**：英雄联盟的跑步是一条腿往前迈、另一条往后蹬，后面那条腿膝盖弯曲、小腿往上踢；中间那帧两腿在身体下面交错而过。
> - 踩地的那只脚**脚底贴在红色地面线上**；抬起的脚离开地面。
> - **腿的样子完全照造型**（`design/jarvaniv_design.png`，10 倍放大，一格 = 一个像素）：金色的圆形**护膝中间一颗蓝宝石**、分节的**金色胫甲**（亮金、金、暗金、棕金）、**金色靴子**。**两条腿和造型一样粗、一样长**；护膝、胫甲、靴子的大小和形状都和造型一样，只是跟着骨架弯曲、倾斜。不要画细、不要画长、不要画成别的样子。
> - **近侧腿画在远侧腿前面**（重叠时挡住它），远侧腿用造型里远侧那条腿自己的颜色（稍暗一点的金和棕），**不要换成别的颜色**。
> - 腿的上端都从**裙甲下沿里面**伸出来（大腿被裙甲挡住），不要在裙甲外面另画一截大腿。
> - 和之前一样：1536×1536 透明画布，**每格 12 px、对齐同一个网格**（和 `now/` 的图同一个网格），只用造型里的颜色，近黑外描边，不要抖动、渐变、半透明、特效；地面线以下什么都不能有；**骨架线、绿线、地面线、文字都不要画进图里**。

## 附图（压缩包 `jarvaniv_run_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `now/jarvaniv_run_<n>.png` | 跑步第 n 帧现在的样子 | **绿线以上原样保留**（一格都不动） |
| `guide/jarvaniv_run_<n>.png` | 同一帧，裙甲下沿（绿线）以下淡化，叠上这一帧的腿部骨架（红 = 近侧腿，蓝 = 远侧腿，红横线 = 地面） | **两条腿的姿势照它** |
| `design/jarvaniv_design.png` | 造型（10 倍放大） | 护膝、胫甲、靴子的样子、大小和颜色 |
| `refs/jarvanIV_run.png` | 英雄联盟里嘉文的跑步（3D 模型，8 帧） | 跑步的感觉 |
| `legs.json` | 每帧两只脚的位置（格子坐标） | 对照用 |

## 提示词（每帧一次，n = 1…8）

附图顺序：1 `now/jarvaniv_run_<n>.png`，2 `guide/jarvaniv_run_<n>.png`，3 `design/jarvaniv_design.png`，4 你刚画好的第 n−1 帧（第 1 帧不附）。

```text
Image 1 is a pixel-art running frame of this knight (frame <n> of an 8-frame run loop), drawn on a grid of 12x12-pixel squares on a 1536x1536 transparent canvas. Everything ABOVE the skirt's bottom edge is final and must stay exactly as it is, square for square: the gold crown helmet, the blue plume, the face, the pauldrons, the breastplate, the arms, the lance carried level on the shoulder, the belt and the skirt. Its LEGS are still the standing legs (shown only as the look of the legs): this frame needs running legs. Image 2 is the same frame with everything under the skirt's hem (the green line) faded and a SKELETON drawn over the legs: the RED line is the NEAR leg (closer to the viewer), the BLUE line is the FAR leg; the dots on each line are hip (inside the skirt), knee, ankle, toe; the red horizontal line is the ground. Image 3 is the approved design (10x enlarged: one square = one pixel): exactly how the legs look - a round GOLD KNEE GUARD with a BLUE GEM in the middle, segmented GOLD GREAVES (bright gold, gold, dark gold, brown-gold), GOLD BOOTS. (Image 4, when attached, is the frame before this one: keep the legs exactly as thick and long.)
Draw ONLY THE TWO LEGS below the skirt's hem, following Image 2's skeleton exactly: the near leg along the red line, the far leg along the blue line, each foot where its ankle and toe dots are, the knee where the knee dot is. A foot on the ground stands with its sole ON the red ground line; a lifted foot is off the ground; a leg kicked back bends at the knee with the lower leg raised behind. Both legs as thick and as long as in Image 3, never thinner or longer; the knee guards, greaves and boots the SAME size and shape as Image 3's, only bent and tilted with the skeleton; the near leg drawn OVER the far leg where they overlap; the far leg in the design's own far-leg colours. The tops of both legs go up INSIDE the skirt (no thigh drawn outside it). Keep EVERYTHING above the green line of Image 2 exactly as in Image 1, square for square - do not move, redraw or reshape the body, the arms, the lance or the skirt.
Same rules as before: the 1536x1536 transparent canvas and the SAME 12-pixel grid as Image 1, every square one flat colour from the design's colours, a near-black outline, no dithering, no gradients, no semi-transparency, no effects; nothing below the ground line; do NOT draw the skeleton lines, the green line, the ground line or any text. Also deliver a 1x copy (one pixel per square, 128x128) that matches square for square.
```

## 交付（`outputs/jarvaniv-run/`）

- `jarvaniv_run_1.png` … `jarvaniv_run_8.png`（1536×1536）+ 各自的 `_1x.png`（128×128）；原始生成图放 `raw/`；`HANDOFF.md`（最后写）；打包 `outputs/jarvaniv_run_done.zip`。中间不要停，8 帧都画完再交。

## 交回前请检查

- 8 帧里两条腿**轮流在前**，后面那条腿弯膝往后踢；不是 8 帧同一条腿在前，也不是两条直腿左右挪。
- 踩地的脚贴着地面线；两条腿和造型一样粗、一样长；护膝是圆的、中间有蓝宝石；胫甲、靴子和造型一样。
- 绿线以上（头盔、身体、手臂、骑枪、腰带、裙甲）和 `now/` 那帧一格不差。
- 没有画进骨架线、绿线、地面线、文字。

## Claude 收到后（给 Claude 看）

- 读回：每格 12 px 对格（或按 1x 副本），颜色对到造型的调色板；**裙甲下沿以下只取 Codex 的腿**，以上一律用我自己的帧（`tools/art/rig_jarvaniv.py` 的 walk），在接缝处查描边。
- 逐帧量：两条腿都在、每排宽度和造型的腿差不超过 1 格、护膝有蓝宝石、靴子大小一样、近侧 / 远侧轮流在前；有坏的帧就重排或请 Codex 重画那几帧（潘森的做法：重画坏了的两帧用 7 帧重排）。
