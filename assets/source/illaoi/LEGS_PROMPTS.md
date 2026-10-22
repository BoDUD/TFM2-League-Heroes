# 海兽祭司 俄洛伊：只重画腿（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 你上一轮画的姿势，**头、脸、发髻、手臂、护腕、神像、胸布、腰布都很好**。只有两个问题：
>   1. 有几张**腿太长了**。俄洛伊是 **Q 版大头** 的造型：定稿里从胯（布裙下面）到脚底只有 **约 22 格**（大腿约 8 格、小腿约 8 格，墨绿高靴的脚约 8 格长，见 `0_design_legs.png`）。e_yank、w_jump、e_thrust 和跑步的腿画长了，她一做动作就变高、步子跨得特别大。
>   2. **跑步四张两条腿没有轮流**：run1 和 run3 都是同一条腿在前，run2 和 run4 都是同一条腿撑地，跑起来像一条腿一直在前面。
> - 这一轮**只画腿**。每个姿势给你一张 `*_guide.png`：**上半身已经画好放在画布上**（就是你上一轮那一张的上半身，一格不差，**已经挪到了正确的高度**，旧的腿已经去掉了），下面的**红线 / 蓝线是新腿的骨架**，按定稿的腿长量好的。请照着骨架把两条腿补上，画成一张完整的图。
> - `*_first.png` 是你上一轮画的同一个姿势，**腿的样子、颜色、肌肉、高靴、金色绑带、膝盖怎么弯**照它，**只是长度和方向照骨架**。
> - 一共 **7 张**：w_jump、e_thrust、e_yank、run1、run2、run3、run4。

## 规则

- **画布、格子和 guide 一模一样**：1254 × 1254，**每格 12 px**，网格从画布左上角 (0, 0) 对齐，红色横线是地面（**y = 1200**）。
- **上半身一格都不要动**：guide 里已经画好的部分（头、发髻、脸、手臂、护腕、神像、胸布、腰带、暗红腰布、灰绿布裙）**照抄，位置、大小、颜色、每一格都不变**。只在它下面补腿。
- **腿沿着骨架画**：**红线 = 近侧的腿（画面左边那条，颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**。每条线的三段是**大腿、小腿、高靴的脚**，在圆点处弯折；大腿的上头藏在布裙下面。腿的**粗细和定稿一样**（结实的深棕色大腿约 5–6 格宽，墨绿高靴约 5 格宽，见 `0_design_legs.png`），**长度就是线的长度，绝对不要画长**。脚的末端碰到地面线的，靴底就踩在 y = 1200 上；离地的姿势（w_jump 跳起来、run2 / run4 身子高一格）脚照线悬空。
- 大腿是**深棕色的皮肤**（3–4 档，亮的一边暖橙棕），膝盖往下是**墨绿色高靴**（3 档）带**金色绑带**；**1 格近黑的外描边**，两条腿之间要有描边分开。暗红腰布和布裙**在腿前面**，挡住大腿的上头。
- 布裙、腰布在腿附近被去掉的那一小段，**照 `*_first.png` 补齐**，和 guide 里的部分接上。
- **跑步四张**（run1–run4）是一个循环，两条腿**轮流**在前：run1 远侧腿（蓝）在前着地、近侧腿（红）往后蹬；run2 近侧腿在身下撑地、远侧腿屈膝抬到前面；run3 近侧腿（红）在前着地、远侧腿往后蹬；run4 远侧腿在身下撑地、近侧腿屈膝抬到前面。**四张的腿长都一样**。
- 真透明背景，**alpha 只有 0 / 255**；不要网格线、骨架线、文字、地面、投影、技能特效。

## 提示词（每张一次，换掉最后一行的姿势名）

每次上传：这个姿势的 `*_guide.png`、`*_first.png` 和 `0_design_legs.png`。**用 image_gen 画。**

```text
Attached images: A (the *_guide.png) a pixel-art picture on a 1254x1254 canvas with 12 px squares aligned from the canvas corner and a red ground line at y 1200: the UPPER BODY of a chibi character is already drawn - a strong priestess with a big head: dark brown skin, green eyes, a black high bun with a gold ring, gold shoulder plates, a teal chest wrap, strong arms with a big gold bracer, a big round gold idol, a gold belt, a dark red loincloth and a grey-green cloth skirt - and under it two LEG SKELETONS: RED = the NEAR leg (image left, full tone), BLUE = the FAR leg (image right, a step darker), each line three bones (thigh, shin, boot foot) bending at the dots; B (the *_first.png) your own earlier picture of the same pose, with the same upper body but the LEGS TOO LONG (and in the runs, not alternating); C (0_design_legs.png) the approved design's legs shown 8x: the short chibi legs - their thickness, length and colours.
Draw with the image generator ONE pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px, aligned on one straight grid from the canvas corner. COPY THE UPPER BODY OF IMAGE A SQUARE FOR SQUARE - the same place, size and colours, nothing moved, nothing redrawn - and add ONLY the two legs under it, along the red and blue skeletons: SHORT chibi legs exactly as long as the lines (never longer), as thick as in image C (strong dark brown thighs about 5-6 squares wide, dark green tall boots about 5 wide), bending at the dots, the tops of the thighs under the cloth skirt and the loincloth; the near (red) leg in full tone, the far (blue) leg a step darker; dark brown skin in 3-4 shades (warm orange-brown lit) to the knees, then dark green boots in 3 shades with gold straps; a foot whose line ends on the ground stands on y 1200, a foot whose line ends in the air hangs there. Also finish what the cut-away legs hid, as in image B: the skirt's and the loincloth's lower edges next to the legs - joined to image A's parts.
One continuous 1-square near-black outline; the two legs kept apart by their outlines; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <pose name>: the same pose as image B, only with the short legs of image A's skeleton.
```

## 交回前请检查

- 7 张都是 image_gen 画的；1254 × 1254；真透明背景（alpha 只有 0 / 255）；每格 12 px，和 guide 对齐。
- **上半身和 guide 一格不差**（头、脸、发髻、手臂、护腕、神像的位置都没动）。
- **腿是短的**：和骨架线一样长，和 `0_design_legs.png` 一样粗；站着的靴底踩在 y = 1200 上；两条腿描边分开；跑步四张两条腿轮流在前，腿长一样。

## 交付（`outputs/illaoi-legs/`）

- `illaoi-legs-w_jump.png`、`illaoi-legs-e_thrust.png`、`illaoi-legs-e_yank.png`、`illaoi-legs-run1.png`、`illaoi-legs-run2.png`、`illaoi-legs-run3.png`、`illaoi-legs-run4.png`；原始生成图原样放 `outputs/illaoi-legs/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/illaoi_legs_done.zip`。中间不要停，7 张都画完再交。

## 附图（压缩包 `illaoi_legs_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `0_design_legs.png` | 定稿的腿（8 倍）：长度、粗细、颜色 |
| `1_w_jump_guide.png` … `7_run4_guide.png` | 每个姿势：上半身已画好、放到正确高度，红 / 蓝 = 新腿的骨架，红色横线 = 地面 |
| `1_w_jump_first.png` … `7_run4_first.png` | 你上一轮画的同一个姿势（腿太长 / 跑步没轮流） |

## Claude 收到后（给 Claude 看）

- 按 guide 的 12 px 网格从 (0, 0) 读回（每格取多数颜色），颜色对到定稿的调色板；**上半身用 guide 里自己的那一份逐格贴回**（`assets/source/illaoi/codex_legs_guides.json` 记着每个上半身在画布上的位置），只有切掉的腿区和骨架附近取 Codex 新画的（design_ivern_legs.py 的做法）；在 8 倍下量每条腿的长度、粗细，和定稿比；跑步四帧检查两腿交替、头的高度差不超过 1 格。
