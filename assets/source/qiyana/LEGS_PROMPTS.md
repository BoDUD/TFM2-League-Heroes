# 元素女皇 奇亚娜：只重画腿（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 你上一轮画的 15 个姿势，**头、上半身、手臂、圆环都很好，用户认可**。只有一个问题：**腿太长了**。奇亚娜是 **Q 版大头** 的造型：她的腿很短——定稿里从裙摆到脚底只有 **18 格**（大腿约 9 格、小腿约 6 格、脚约 4 格，见 `0_design_legs.png`）。你画的腿是正常人的长腿（站着的腿 30 多格、弓步的后腿 25–38 格），所以她一做动作就突然变高、步子跨得特别大。
> - 这一轮**只画腿**。每个姿势给你一张 `*_guide.png`：**上半身已经画好放在画布上**（就是你上一轮那一张的上半身，一格不差，**已经往下挪到了正确的高度**，旧的长腿已经去掉了），下面的**红线 / 蓝线是新腿的骨架**，按定稿的腿长量好的。请照着骨架把两条**短腿**补上，画成一张完整的图。
> - `*_first.png` 是你上一轮画的同一个姿势，**腿的样子、颜色、紧身裤的金色三角花纹、凉鞋、膝盖怎么弯**照它，**只是长度照骨架（短得多）**。
> - 一共 **13 张**：a_wind、a_strike、q_wind、q_sweep、q_end、e_dash、e_hit、r_leap、r_slam、run1、run2、run3、run4。

## 规则

- **画布、格子和 guide 一模一样**：1254 × 1254，**每格 13 px**，网格从画布左上角 (0, 0) 对齐，红色横线是地面（**y = 1196**）。
- **上半身一格都不要动**：guide 里已经画好的部分（头、王冠、头发、脸、身体、手臂、圆环、裙子的上半截）**照抄，位置、大小、颜色、每一格都不变**。只在它下面补腿。
- **腿沿着骨架画**：**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**。每条线的三段是**大腿、小腿、脚**，在圆点处弯折；腿的**粗细和定稿一样**（大腿约 6 格宽、小腿约 4 格，见 `0_design_legs.png`），**长度就是线的长度，绝对不要画长**。脚的末端碰到地面线的，脚底就踩在 y = 1196 上；离地的姿势（a_strike、e_dash、r_leap 跳起来）脚照线悬空。
- 腿是**深棕近黑的紧身裤**（2–3 档）加**金色的三角花纹**（整格），脚上是**紫棕色的凉鞋**带金扣、露一点暖棕色的脚趾；**1 格近黑的外描边**，两条腿之间要有描边分开。
- 裙子下摆、身后的墨绿裙摆、垂下来的头发、圆环在腿附近被去掉的那一小段，**照 `*_first.png` 补齐**（跟着上半身一起往下挪了），和 guide 里的部分接上。
- **跑步四张**（run1–run4）是一个循环，两条腿**轮流**在前：run1 远侧腿（蓝）在前着地、近侧腿（红）往后抬；run2 近侧腿在身下撑地、远侧腿屈膝抬到前面；run3 近侧腿（红）在前着地、远侧腿往后抬；run4 远侧腿在身下撑地、近侧腿屈膝抬到前面。**四张的腿长都一样**。
- 真透明背景，**alpha 只有 0 / 255**；不要网格线、骨架线、文字、地面、投影、技能特效。

## 提示词（每张一次，换掉最后一行的姿势名）

每次上传：这个姿势的 `*_guide.png`、`*_first.png` 和 `0_design_legs.png`。**用 image_gen 画。**

```text
Attached images: A (the *_guide.png) a pixel-art picture on a 1254x1254 canvas with 13 px squares aligned from the canvas corner and a red ground line at y 1196: the UPPER BODY of a chibi character is already drawn - a proud young empress with a big head, warm tan-brown skin, long silver-white hair, a gold tiara with a white-jade crest, a turquoise-teal strapless dress, gold jewellery and a huge ring blade in her hand - and under it two LEG SKELETONS: RED = the NEAR leg (image left, in front, full tone), BLUE = the FAR leg (image right, a step darker), each line three bones (thigh, shin, foot) bending at the dots; B (the *_first.png) your own earlier picture of the same pose, with the same upper body but LEGS FAR TOO LONG; C (0_design_legs.png) the approved design's legs shown 8x: the short chibi legs - their thickness, length and colours.
Draw with the image generator ONE pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 13 px, aligned on one straight grid from the canvas corner. COPY THE UPPER BODY OF IMAGE A SQUARE FOR SQUARE - the same place, size and colours, nothing moved, nothing redrawn - and add ONLY the two legs under it, along the red and blue skeletons: SHORT chibi legs exactly as long as the lines (never longer), as thick as in image C (the thigh about 6 squares wide, the shin about 4), bending at the dots; the near (red) leg in front in full tone, the far (blue) leg a step darker; dark brown-black leggings in 2-3 shades with a few gold triangle markings drawn with whole squares, purple-brown sandals with gold and a little warm-brown toe; a foot whose line ends on the ground stands on y 1196, a foot whose line ends in the air hangs there. Also finish what the cut-away legs hid, as in image B but moved down with the body: the dress's lower hem, the dark green flap behind, hair ends, the bit of the ring next to the legs - joined to image A's parts.
One continuous 1-square near-black outline; the two legs kept apart by their outlines; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <pose name>: the same pose as image B, only with the short legs of image A's skeleton.
```

## 交回前请检查

- 13 张都是 image_gen 画的；1254 × 1254；真透明背景（alpha 只有 0 / 255）；每格 13 px，和 guide 对齐。
- **上半身和 guide 一格不差**（头、脸、头发、手臂、圆环的位置都没动）。
- **腿是短的**：和骨架线一样长，和 `0_design_legs.png` 一样粗；站着的脚踩在 y = 1196 上；两条腿描边分开；跑步四张两条腿轮流在前，腿长一样。

## 交付（`outputs/qiyana-legs/`）

- `qiyana-legs-a_wind.png`、`qiyana-legs-a_strike.png`、`qiyana-legs-q_wind.png`、`qiyana-legs-q_sweep.png`、`qiyana-legs-q_end.png`、`qiyana-legs-e_dash.png`、`qiyana-legs-e_hit.png`、`qiyana-legs-r_leap.png`、`qiyana-legs-r_slam.png`、`qiyana-legs-run1.png`、`qiyana-legs-run2.png`、`qiyana-legs-run3.png`、`qiyana-legs-run4.png`；原始生成图原样放 `outputs/qiyana-legs/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/qiyana_legs_done.zip`。中间不要停，13 张都画完再交。

## 附图（压缩包 `qiyana_legs_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `0_design_legs.png` | 定稿的腿（8 倍）：长度、粗细、颜色 |
| `1_a_wind_guide.png` … `13_run4_guide.png` | 每个姿势：上半身已画好、降到正确高度，红 / 蓝 = 新腿的骨架，红色横线 = 地面 |
| `1_a_wind_first.png` … `13_run4_first.png` | 你上一轮画的同一个姿势（腿太长） |

## Claude 收到后（给 Claude 看）

- 按 guide 的 13 px 网格从 (0, 0) 读回（每格取多数颜色），颜色对到定稿的调色板；**上半身用 guide 里自己的那一份逐格贴回**（`assets/source/qiyana/codex_legs_guides.json` 记着每个上半身在画布上的位置），只有切掉的腿区和骨架附近取 Codex 新画的；在 8 倍下量每条腿的长度、粗细，和定稿比；跑步四帧检查两腿交替、头的高度差不超过 1 格。
