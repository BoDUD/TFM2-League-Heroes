# 异画师 彗：只重画腿·补充两张（给 Codex 的提示词）

> **和上一份 `hwei_legs_pack.zip` 一样的做法、一样的提示词**，只是又找出两张腿太长的弓步：**q_throw**（两条腿都长了）和 **qw_point**（往后伸的那条腿有 29 格，定稿从胯到脚尖最长约 20 格）。
> 每张上传：这个姿势的 `*_guide.png`、`*_first.png` 和 `0_design_legs.png`，用下面同一段英文提示词，只换最后一行的姿势名。**用 image_gen 画。**
> 交付：`outputs/hwei-legs/hwei-legs-q_throw.png`、`outputs/hwei-legs/hwei-legs-qw_point.png`（原始图放 `outputs/hwei-legs/raw/`），**最后**写 `HANDOFF2.md`，再打包成 `outputs/hwei_legs2_done.zip`。

## 规则

- **画布、格子和 guide 一模一样**：1254 × 1254，**每格 12 px**，网格从画布左上角 (0, 0) 对齐，红色横线是地面（**y = 1200**）。
- **上半身一格都不要动**：guide 里已经画好的部分（头、头发、脸、颈环、外套、袖子、手、画笔、背后的弯月墨痕）**照抄，位置、大小、颜色、每一格都不变**。只在它下面补腿。
- **腿沿着骨架画**：**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**。每条线的三段是**大腿、小腿、脚**，在圆点处弯折；大腿的上半截藏在外套下摆里。腿的**粗细和定稿一样**（裤腿约 5 格宽、小腿约 3 格，见 `0_design_legs.png`），**长度就是线的长度，绝对不要画长**。脚的末端碰到地面线的，鞋底就踩在 y = 1200 上；两张都是两只脚踩地。
- 腿是**墨绿色的七分裤**（2–3 档），裤脚上**青绿色的丝带结**，下面露一截**苍白的小腿**，**只有远侧（蓝线）的脚踝**戴**粉色的珠串**，脚上是**棕色的便鞋**（2 档）；**1 格近黑的外描边**，两条腿之间要有描边分开。
- 外套下摆、里衬、垂下来的衣角在腿附近被去掉的那一小段，**照 `*_first.png` 补齐**（跟着上半身一起往下挪了），和 guide 里的部分接上。
- **跑步四张**（run1–run4）是一个循环，两条腿**轮流**在前：run1 远侧腿（蓝）在前着地、近侧腿（红）往后抬；run2 近侧腿在身下撑地、远侧腿屈膝抬到前面；run3 近侧腿（红）在前着地、远侧腿往后抬；run4 远侧腿在身下撑地、近侧腿屈膝抬到前面。**四张的腿长都一样**，粉色珠串始终在远侧（蓝线）那条腿上。
- 真透明背景，**alpha 只有 0 / 255**；不要网格线、骨架线、文字、地面、投影、技能特效。

## 提示词（每张一次，换掉最后一行的姿势名）

每次上传：这个姿势的 `*_guide.png`、`*_first.png` 和 `0_design_legs.png`。**用 image_gen 画。**

```text
Attached images: A (the *_guide.png) a pixel-art picture on a 1254x1254 canvas with 12 px squares aligned from the canvas corner and a red ground line at y 1200: the UPPER BODY of a chibi character is already drawn - a slim young painter with a big head, messy dark green-black hair, an indigo painter's coat with a turquoise collar and gold trim, a red-orange shirt, a giant paintbrush in his hand and a crescent of paint floating behind him - and under it two LEG SKELETONS: RED = the NEAR leg (image left, in front, full tone), BLUE = the FAR leg (image right, a step darker), each line three bones (thigh, shin, foot) bending at the dots; B (the *_first.png) your own earlier picture of the same pose, with the same upper body but LEGS FAR TOO LONG; C (0_design_legs.png) the approved design's legs shown 8x: the short chibi legs - their thickness, length and colours.
Draw with the image generator ONE pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px, aligned on one straight grid from the canvas corner. COPY THE UPPER BODY OF IMAGE A SQUARE FOR SQUARE - the same place, size and colours, nothing moved, nothing redrawn - and add ONLY the two legs under it, along the red and blue skeletons: SHORT chibi legs exactly as long as the lines (never longer), as thick as in image C (the trouser leg about 5 squares wide, the shin about 3), bending at the dots, the tops of the thighs under the coat's hem; the near (red) leg in front in full tone, the far (blue) leg a step darker; dark green cropped trousers in 2-3 shades with a teal ribbon bow at each calf, a bit of pale shin below, a pink bead anklet on the FAR (blue) leg only, brown loafers in 2 shades; a foot whose line ends on the ground stands on y 1200, a foot whose line ends in the air hangs there. Also finish what the cut-away legs hid, as in image B but moved down with the body: the coat's lower hem and lining, the flaps next to the legs - joined to image A's parts.
One continuous 1-square near-black outline; the two legs kept apart by their outlines; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <pose name>: the same pose as image B, only with the short legs of image A's skeleton.
```

## 交回前请检查

- 2 张都是 image_gen 画的；1254 × 1254；真透明背景（alpha 只有 0 / 255）；每格 12 px，和 guide 对齐。
- **上半身和 guide 一格不差**（头、脸、头发、外套、手、画笔、墨痕的位置都没动；qw_point 的笔尖碰到地面线也不要动它）。
- **腿是短的**：和骨架线一样长，和 `0_design_legs.png` 一样粗；两只脚踩在 y = 1200 上；两条腿描边分开；粉色珠串只在远侧（蓝线）腿上。

## 附图（压缩包 `hwei_legs_pack2.zip` 里）

| 文件 | 内容 |
|---|---|
| `0_design_legs.png` | 定稿的腿（8 倍）：长度、粗细、颜色 |
| `12_q_throw_guide.png`、`13_qw_point_guide.png` | 上半身已画好、降到正确高度，红 / 蓝 = 新腿的骨架，红色横线 = 地面 |
| `12_q_throw_first.png`、`13_qw_point_first.png` | 你上一轮画的同一个姿势（腿太长） |

