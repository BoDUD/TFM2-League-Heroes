# 双界灵兔 阿萝拉：只重画腿（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 你上一轮画的姿势，**头、帽子、兔耳朵、脸、眼镜、手臂、披肩、外套、腰带、尾巴、魔杖都很好**。只有一个问题：有几张**腿太长了**。阿萝拉是 **Q 版大头** 的造型：定稿里从胯（裙子下面）到脚底只有 **约 26 格**（大腿约 10 格、大半藏在裙子和外套下面，小腿约 8 格，带白毛边的短靴约 8 格，见 `0_design_legs.png`）。a_wind、q_cast、e_hop、r_reach 和跑步的腿画长了 6–10 格，她一做动作就整个人变高、步子跨得特别大。
> - 这一轮**只画腿**。每个姿势给你一张 `*_guide.png`：**上半身已经画好放在画布上**（就是你上一轮那一张的上半身，一格不差，**已经挪到了正确的高度**，旧的腿已经去掉了），下面的**红线 / 蓝线是新腿的骨架**，按定稿的腿长量好的。请照着骨架把两条腿补上，画成一张完整的图。
> - `*_first.png` 是你上一轮画的同一个姿势，**腿的样子、颜色、深棕长袜、袜口、短靴、金扣、白毛边、膝盖怎么弯**照它，**只是长度和方向照骨架**。
> - 一共 **8 张**：a_wind、q_cast、e_hop、r_reach、run1、run2、run3、run4。

## 规则

- **画布、格子和 guide 一模一样**：1254 × 1254，**每格 9 px**，网格从画布左上角 (0, 0) 对齐，红色横线是地面（**y = 1197**）。
- **上半身一格都不要动**：guide 里已经画好的部分（头、帽子、耳朵、脸、手臂、披肩、外套和后摆、腰带、裙子、尾巴、魔杖）**照抄，位置、大小、颜色、每一格都不变**。只在它下面补腿。
- **腿沿着骨架画**：**红线 = 近侧的腿（画面左边那条，颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**。每条线的三段是**大腿、小腿、短靴的脚**，在圆点处弯折；大腿的上头藏在裙子和外套下摆下面。腿的**粗细和定稿一样**（深棕长袜的腿约 4–5 格宽，短靴约 6 格宽，见 `0_design_legs.png`），**长度就是线的长度，绝对不要画长**。脚的末端碰到地面线的，靴底就踩在 y = 1197 上；离地的姿势（e_hop 往后跳、run2 / run4 身子高一格）脚照线悬空。
- 腿是**深棕色的过膝长袜**（2–3 档），袜口一圈米白、上面露一小截浅肤色的大腿；脚上是**带白毛边的短靴**（浅蓝 + 藏青，金扣，鞋尖米白、一道红）；**1 格近黑的外描边**，两条腿之间要有描边分开。裙子、外套下摆和尾巴**在腿前面**，挡住大腿的上头。
- 裙子、外套下摆在腿附近被去掉的那一小段，**照 `*_first.png` 补齐**，和 guide 里的部分接上。
- **跑步四张**（run1–run4）是一个循环，两条腿**轮流**在前：run1 远侧腿（蓝）在前着地、近侧腿（红）往后蹬；run2 近侧腿在身下撑地、远侧腿屈膝抬到前面；run3 近侧腿（红）在前着地、远侧腿往后蹬；run4 远侧腿在身下撑地、近侧腿屈膝抬到前面。**四张的腿长都一样**。
- 真透明背景，**alpha 只有 0 / 255**；不要网格线、骨架线、文字、地面、投影、技能特效。

## 提示词（每张一次，换掉最后一行的姿势名）

每次上传：这个姿势的 `*_guide.png`、`*_first.png` 和 `0_design_legs.png`。**用 image_gen 画。**

```text
Attached images: A (the *_guide.png) a pixel-art picture on a 1254x1254 canvas with 9 px squares aligned from the canvas corner and a red ground line at y 1197: the UPPER BODY of a chibi character is already drawn - a petite bunny witch with a very big head: a wide teal witch hat, two long rabbit ears, copper-red curly hair, round gold glasses, a pale blue-white fur shawl, a cream long coat with tails, a brown braided belt, a short teal skirt, a fluffy orange tail and a long slim wand - and under it two LEG SKELETONS: RED = the NEAR leg (image left, full tone), BLUE = the FAR leg (image right, a step darker), each line three bones (thigh, shin, boot foot) bending at the dots; B (the *_first.png) your own earlier picture of the same pose, with the same upper body but the LEGS TOO LONG; C (0_design_legs.png) the approved design's legs shown 8x: the short chibi legs - their thickness, length and colours.
Draw with the image generator ONE pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px, aligned on one straight grid from the canvas corner. COPY THE UPPER BODY OF IMAGE A SQUARE FOR SQUARE - the same place, size and colours, nothing moved, nothing redrawn - and add ONLY the two legs under it, along the red and blue skeletons: SHORT chibi legs exactly as long as the lines (never longer), as thick as in image C (dark brown thigh-high stockings about 4-5 squares wide, short boots about 6 wide), bending at the dots, the tops of the thighs under the skirt and the coat's tails; the near (red) leg in full tone, the far (blue) leg a step darker; dark brown stockings in 2-3 shades with cream tops and a little light skin above them, then short boots - pale blue and navy with gold buckles, white fur trim, a cream toe cap with a red stripe; a foot whose line ends on the ground stands on y 1197, a foot whose line ends in the air hangs there. Also finish what the cut-away legs hid, as in image B: the skirt's and the coat tails' lower edges next to the legs - joined to image A's parts.
One continuous 1-square near-black outline; the two legs kept apart by their outlines; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <pose name>: the same pose as image B, only with the short legs of image A's skeleton.
```

## 交回前请检查

- 8 张都是 image_gen 画的；1254 × 1254；真透明背景（alpha 只有 0 / 255）；每格 9 px，和 guide 对齐。
- **上半身和 guide 一格不差**（头、帽子、耳朵、脸、手臂、尾巴、魔杖的位置都没动）。
- **腿是短的**：和骨架线一样长，和 `0_design_legs.png` 一样粗；站着的靴底踩在 y = 1197 上；两条腿描边分开；跑步四张两条腿轮流在前，腿长一样。

## 交付（`outputs/aurora-legs/`）

- `aurora-legs-a_wind.png`、`aurora-legs-q_cast.png`、`aurora-legs-e_hop.png`、`aurora-legs-r_reach.png`、`aurora-legs-run1.png`、`aurora-legs-run2.png`、`aurora-legs-run3.png`、`aurora-legs-run4.png`；原始生成图原样放 `outputs/aurora-legs/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/aurora_legs_done.zip`。中间不要停，8 张都画完再交。

## 附图（压缩包 `aurora_legs_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `0_design_legs.png` | 定稿的腿（8 倍）：长度、粗细、颜色 |
| `1_a_wind_guide.png` … `8_run4_guide.png` | 每个姿势：上半身已画好、放到正确高度，红 / 蓝 = 新腿的骨架，红色横线 = 地面 |
| `1_a_wind_first.png` … `8_run4_first.png` | 你上一轮画的同一个姿势（腿太长） |

## Claude 收到后（给 Claude 看）

- 按 guide 的 9 px 网格从 (0, 0) 读回（每格取多数颜色），颜色对到定稿的调色板；**上半身用 guide 里自己的那一份逐格贴回**（`assets/source/aurora/codex_legs_guides.json` 记着每个上半身在画布上的位置），只有切掉的腿区和骨架附近取 Codex 新画的（design_illaoi_legs.py 的做法）；在 8 倍下量每条腿的长度、粗细，和定稿比；跑步四帧检查两腿交替、头的高度差不超过 1 格。
