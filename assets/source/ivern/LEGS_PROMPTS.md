# 翠神 艾翁：只重画腿（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 你上一轮画的姿势，**头、羊角、蘑菇、树叶胡子、手臂、小树枝、苹果、种子都很好**。只有一个问题：**腿太长了**。艾翁是 **Q 版大头** 的造型：他的腿很短——定稿里从胯（树叶裙下面）到脚底只有 **约 16 格**（大腿约 6 格、小腿约 5 格，分叉的树根脚约 6 格长，见 `0_design_legs.png`）。你画的腿是英雄联盟原版那样的长高跷（站直的腿 21–25 格），所以他一做动作就突然变高、步子跨得特别大。
> - 这一轮**只画腿**。每个姿势给你一张 `*_guide.png`：**上半身已经画好放在画布上**（就是你上一轮那一张的上半身，一格不差，**已经往下挪到了正确的高度**，旧的长腿已经去掉了），下面的**红线 / 蓝线是新腿的骨架**，按定稿的腿长量好的。请照着骨架把两条**短腿**补上，画成一张完整的图。
> - `*_first.png` 是你上一轮画的同一个姿势，**腿的样子、颜色、树皮纹、红浆果、树根脚、膝盖怎么弯**照它，**只是长度照骨架（短得多）**。
> - 一共 **11 张**：a_wind、a_throw、e_give、q_wind、q_fling、r_call、r_leap、run1、run2、run3、run4。

## 规则

- **画布、格子和 guide 一模一样**：1254 × 1254，**每格 12 px**，网格从画布左上角 (0, 0) 对齐，红色横线是地面（**y = 1200**）。
- **上半身一格都不要动**：guide 里已经画好的部分（头、羊角、蘑菇、脸、树叶胡子、木头身子、树叶裙、白布条、手臂、小树枝、苹果、种子）**照抄，位置、大小、颜色、每一格都不变**。只在它下面补腿。
- **腿沿着骨架画**：**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**。每条线的三段是**大腿、小腿、树根脚**，在圆点处弯折；大腿的上头藏在树叶裙下面。腿的**粗细和定稿一样**（细细的树皮腿约 3 格宽，脚是往两边分叉的树根，见 `0_design_legs.png`），**长度就是线的长度，绝对不要画长**。脚的末端碰到地面线的，根脚就踩在 y = 1200 上；离地的姿势（r_leap 跳起来、run2 / run4 身子高一格）脚照线悬空。
- 腿是**深红棕色的树皮**（3 档，亮的一边浅一档，几道深色的树皮纹），**只有近侧（红线）的小腿**上长着**两三颗红浆果**，脚是**分叉的树根**；**1 格近黑的外描边**，两条腿之间要有描边分开。
- 树叶裙、垂下来的叶子在腿附近被去掉的那一小段，**照 `*_first.png` 补齐**（跟着上半身一起往下挪了），和 guide 里的部分接上。
- **跑步四张**（run1–run4）是一个循环，两条腿**轮流**在前：run1 远侧腿（蓝）在前着地、近侧腿（红）往后抬；run2 近侧腿在身下撑地、远侧腿屈膝抬到前面；run3 近侧腿（红）在前着地、远侧腿往后抬；run4 远侧腿在身下撑地、近侧腿屈膝抬到前面。**四张的腿长都一样**，红浆果始终在近侧（红线）那条腿上。
- 真透明背景，**alpha 只有 0 / 255**；不要网格线、骨架线、文字、地面、投影、技能特效。

## 提示词（每张一次，换掉最后一行的姿势名）

每次上传：这个姿势的 `*_guide.png`、`*_first.png` 和 `0_design_legs.png`。**用 image_gen 画。**

```text
Attached images: A (the *_guide.png) a pixel-art picture on a 1254x1254 canvas with 12 px squares aligned from the canvas corner and a red ground line at y 1200: the UPPER BODY of a chibi character is already drawn - a walking tree-man with a big head: pale bark face, amber eyes, a big nose, a grin, a huge leaf beard, two pale sage-green ram's horns, a red spotted mushroom on top, a brown wooden body with a leaf skirt, thin branch arms holding a twig and an apple - and under it two LEG SKELETONS: RED = the NEAR leg (image left, in front, full tone), BLUE = the FAR leg (image right, a step darker), each line three bones (thigh, shin, root foot) bending at the dots; B (the *_first.png) your own earlier picture of the same pose, with the same upper body but LEGS FAR TOO LONG; C (0_design_legs.png) the approved design's legs shown 8x: the short chibi legs - their thickness, length and colours.
Draw with the image generator ONE pixel-art picture: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px, aligned on one straight grid from the canvas corner. COPY THE UPPER BODY OF IMAGE A SQUARE FOR SQUARE - the same place, size and colours, nothing moved, nothing redrawn - and add ONLY the two legs under it, along the red and blue skeletons: SHORT chibi legs exactly as long as the lines (never longer), as thin as in image C (bark legs about 3 squares wide), bending at the dots, the tops of the thighs under the leaf skirt; the near (red) leg in front in full tone, the far (blue) leg a step darker; dark red-brown bark in 3 shades with a few dark grain lines, two or three red berries on the NEAR (red) shin only, forked ROOT FEET; a foot whose line ends on the ground stands on y 1200, a foot whose line ends in the air hangs there. Also finish what the cut-away legs hid, as in image B but moved down with the body: the leaf skirt's lower leaves next to the legs - joined to image A's parts.
One continuous 1-square near-black outline; the two legs kept apart by their outlines; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <pose name>: the same pose as image B, only with the short legs of image A's skeleton.
```

## 交回前请检查

- 11 张都是 image_gen 画的；1254 × 1254；真透明背景（alpha 只有 0 / 255）；每格 12 px，和 guide 对齐。
- **上半身和 guide 一格不差**（头、脸、羊角、蘑菇、胡子、手臂、小树枝、苹果、种子的位置都没动）。
- **腿是短的**：和骨架线一样长，和 `0_design_legs.png` 一样细；站着的根脚踩在 y = 1200 上；两条腿描边分开；红浆果只在近侧腿上；跑步四张两条腿轮流在前，腿长一样。

## 交付（`outputs/ivern-legs/`）

- `ivern-legs-a_wind.png`、`ivern-legs-a_throw.png`、`ivern-legs-e_give.png`、`ivern-legs-q_wind.png`、`ivern-legs-q_fling.png`、`ivern-legs-r_call.png`、`ivern-legs-r_leap.png`、`ivern-legs-run1.png`、`ivern-legs-run2.png`、`ivern-legs-run3.png`、`ivern-legs-run4.png`；原始生成图原样放 `outputs/ivern-legs/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ivern_legs_done.zip`。中间不要停，11 张都画完再交。

## 附图（压缩包 `ivern_legs_pack.zip` 里）

| 文件 | 内容 |
|---|---|
| `0_design_legs.png` | 定稿的腿（8 倍）：长度、粗细、颜色 |
| `1_a_wind_guide.png` … `11_run4_guide.png` | 每个姿势：上半身已画好、降到正确高度，红 / 蓝 = 新腿的骨架，红色横线 = 地面 |
| `1_a_wind_first.png` … `11_run4_first.png` | 你上一轮画的同一个姿势（腿太长） |

## Claude 收到后（给 Claude 看）

- 按 guide 的 12 px 网格从 (0, 0) 读回（每格取多数颜色），颜色对到定稿的调色板；**上半身用 guide 里自己的那一份逐格贴回**（`assets/source/ivern/codex_legs_guides.json` 记着每个上半身在画布上的位置），只有切掉的腿区和骨架附近取 Codex 新画的（design_hwei_legs.py 的做法）；在 8 倍下量每条腿的长度、粗细，和定稿比；跑步四帧检查两腿交替、头的高度差不超过 1 格。
