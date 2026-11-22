# 锤石的灯笼重画：给 Codex 的提示词（2 张特效图）

> 用户 2026-11-22：「锤石的灯笼是不是完全没有 我是没见过」「你这个灯笼重做吧」「让codex画吧」。
>
> - 现在游戏里扔出去的灯笼（附图 3）是黄绿色、灰白栏杆的方笼子，和锤石手里提的那盏（附图 1）对不上。**这次照附图 1 重画**：
>   宝塔式的翘檐顶、顶上一个小提环和一簇绿火、灯身上下两层、每层左右两扇发翠绿光的窗、中间一道横带、底座往下收成尖；
>   铁框是骨白到褐色的金属，最外面一圈近黑的描边。**附图 3 只是告诉你要换掉的是哪个，不要照它画。**
> - 灯笼现在会落在地上停 6 秒（附加包 `league_thresh_lantern` 0.2.0），所以要两张：**飞的灯笼**、**落在地上的灯笼**。
> - 只画这两张。锤石本人、护盾、别的特效都不画、不改。
> - 生图原稿（边是半透明的、格子不准）也可以一起交：Claude 会按原图自己的格子读回。交付里要有 `manifest.json`，写明每帧在图里的
>   区域（`assets[].frames[].rect` = [x, y, 宽, 高]）。
> - 交回时附 `HANDOFF.md`：每张用了哪条提示词、画了几帧、有没有没做到的地方。

## 两张图都要守的规矩

- **像素画**：方块清楚、硬边、没有抗锯齿、没有模糊、没有柔光和渐变。
- **格子**：**一格 4 像素**（游戏里半个像素，特效图的高清密度），所有方块一样大、对齐在同一张网格上。下面说的「格」都是游戏像素
  = 2×2 个小方块 = 8×8 像素。
- **颜色**（照附图 1 锤石手里那盏取的，别加别的颜色）：
  - 描边（只给灯笼本体，1 个小方块宽）：`#050206`；暗处 `#1D0F20`。
  - 铁框（骨白到褐，左上亮、右下暗）：`#E3C5B0`、`#C5A390`、`#B18C7B`、`#89685C`、`#58403E`。
  - 灵魂绿（窗、顶上的火、尾巴、地上的光圈、魂火）：`#ECFFF0`、`#C3FBCF`、`#10F348`、`#029D33`、`#065E36`。
- **只有灯笼本体有描边**；光、尾巴、光圈、魂火都不描边，也画成实心方块。
- **背景真透明**：每个像素透明度只有 0 或 255；做不到时用纯黑 `#000000` 背景。不要网格线、边框、文字、编号、阴影。
- 每帧里灯笼的造型、大小、颜色完全一样（只有附图写的那几样在动）。

## 1. `thresh_fx_w_ground.png`：落在地上的灯笼，4 帧，无缝循环

灯笼立着，离地浮着轻轻上下晃；窗里的绿光一明一暗；地上一圈绿光一涨一缩；几点魂火从灯笼旁边往上飘。
排版照附图 4：**4 格一排，每格 256×256 像素（32×32 格）**，整张 **1024×256**。每格里：

- 浅灰十字是格子正中（游戏里落点就是这里，**不要挪**）；**深灰横线是地面**（正中往下 11 格）。
- **橙框是灯笼本体**：宽 10 格、高 15 格，底尖离地面 3 格。4 帧里灯笼整体往上浮 0、1、1、0 格（0、2、2、0 个小方块），左右不动。
- **绿椭圆是地上的光圈**：宽约 26 格、高约 8 格，以地面线为中心；4 帧大小在 24–28 格之间一涨一缩，前半圈（下沿）亮、后半圈暗。
- 魂火：2–3 点小方块（1–2 格），在灯笼两侧，每帧往上飘 2 格，飘到灯笼顶附近就消失。
- 第 4 帧要能接回第 1 帧（循环）。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels on ONE strict grid where every square is exactly 4x4 px (two squares = one game pixel), hard edges, no anti-aliasing, no blur, no soft glow, no gradients.
Image 1 is THE lantern to draw: the green soul lantern the spectral jailer carries. A pagoda-like lantern: a small ring on top with a little green soul flame, a flared pagoda roof with upturned eaves, a body of two tiers, each with two windows glowing bright emerald green with pale mint highlights, a metal band between the tiers, and a base narrowing down to a point. The metal frame is bone-white to brown (#E3C5B0, #C5A390, #B18C7B, #89685C, #58403E), lit from the top left; a 1-square near-black outline (#050206, shadows #1D0F20) around the lantern only. Soul green: #ECFFF0, #C3FBCF, #10F348, #029D33, #065E36. Use only these colours. Image 3 is an OLD lantern that must NOT be copied.
Effect: THE LANTERN RESTING ON THE GROUND, 4 frames, a seamless loop. The lantern stands upright, floating just above the ground and bobbing gently (up 0, 2, 2, 0 squares), its windows pulsing brighter and dimmer; on the ground under it a flat oval ring of soul-green light (about 52 squares wide, 16 tall) swelling and shrinking slightly, its front half brighter; two or three tiny soul motes drifting upward beside the lantern. The glow, ring and motes are solid squares with no outline.
Layout exactly as image 4: one row of 4 cells, each 256x256 px, image 1024x256. In every cell the light grey cross is the cell centre (keep it), the dark grey line 88 px below the centre is the ground, the orange box (80 px wide, 120 px tall, its bottom 24 px above the ground) is where the lantern stands, the green ellipse (about 208 px wide, 64 px tall, centred on the ground line) is the ring. Transparent background (every pixel fully transparent or fully opaque; if impossible pure black #000000), no grid lines, no borders, no labels, no shadow.
```

## 2. `thresh_fx_w_lantern.png`：飞出去的灯笼，4 帧，循环

锤石甩出去、飞向队友的灯笼。**横着朝右飞**：灯笼本体（和第 1 张同一盏、同样大小）**转成横放**，**顶上的提环朝左（后面）**，
**底尖朝右（前面）**；后面拖一道翠绿的魂火尾巴，几点魂火。**整张图上下对称**（游戏会把它转到飞的方向，往左飞时整张转 180°）。
排版照附图 5：**4 格一排，每格 384×128 像素（48×16 格）**，整张 **1536×128**。每格里：

- 浅灰横线是正中（上下对称轴）。**橙框是横放的灯笼本体**（长 15 格、高 10 格，**中心就在格子正中**）。
- **绿框是尾巴的范围**：灯笼后面（左边）约 15 格长、8 格高，越往后越细越淡（淡 = 方块更稀，不是半透明）。
- 4 帧：尾巴的火苗一节节往后流动，窗里的光一明一暗；灯笼本体不动、不转。第 4 帧能接回第 1 帧。

```text
Pixel art game VFX sprite sheet for a small tactics game: chunky square pixels on ONE strict grid where every square is exactly 4x4 px (two squares = one game pixel), hard edges, no anti-aliasing, no blur, no soft glow, no gradients.
Image 1 is THE lantern to draw (the same lantern as the other sheet, the same size and colours): pagoda roof with upturned eaves, a small ring and green soul flame on top, two tiers of two emerald-green glowing windows, a metal band between them, a base narrowing to a point; bone-white to brown metal (#E3C5B0, #C5A390, #B18C7B, #89685C, #58403E), a 1-square near-black outline (#050206, shadows #1D0F20) around the lantern only; soul green #ECFFF0, #C3FBCF, #10F348, #029D33, #065E36. Use only these colours. Image 3 is an OLD lantern that must NOT be copied.
Effect: THE LANTERN FLYING TO THE RIGHT, 4 frames, a seamless loop. The lantern is laid on its side: its ring and top pointing LEFT (backward), its pointed base pointing RIGHT (forward), its windows pulsing brighter and dimmer; behind it to the left a tapering trail of emerald soul fire (about 30 squares long, 16 tall at the lantern, thinning to nothing), its flames flowing backward frame by frame, with three tiny soul motes. The trail and motes are solid squares with no outline. The whole picture is MIRROR-SYMMETRIC about its horizontal middle line.
Layout exactly as image 5: one row of 4 cells, each 384x128 px, image 1536x128. In every cell the light grey line is the middle line (the axis of symmetry); the orange box (120 px long, 80 px tall, centred in the cell) is the lantern on its side; the green box to its left (120 px long, 64 px tall) is where the trail goes. Transparent background (every pixel fully transparent or fully opaque; if impossible pure black #000000), no grid lines, no borders, no labels.
```

## 附图（在压缩包 `thresh_lantern_pack.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_lantern_in_his_hand.png` | 锤石手里提的灯笼（12 倍，游戏里的高清帧） | **要画的就是它**：造型、配色、比例 |
| `refs/2_thresh_now.png` | 锤石现在的样子（5 倍） | 看灯笼和他整个人的画风、颜色 |
| `refs/3_old_effect_lantern_REPLACE.png` | 现在游戏里的旧特效灯笼（8 倍） | **要换掉的**，不要照它 |
| `refs/4_layout_on_the_ground.png` | 第 1 张的排版（1024×256） | 格子、正中、地面线、灯笼框、光圈 |
| `refs/5_layout_flying.png` | 第 2 张的排版（1536×128） | 格子、对称轴、灯笼框、尾巴范围 |

## 交回前请检查

- 两张图的尺寸：`thresh_fx_w_ground.png` 1024×256、`thresh_fx_w_lantern.png` 1536×128；真透明背景（或纯黑），没有缩放、裁剪。
- 一格 4 像素、对齐网格；没有抗锯齿、柔光、渐变、零散杂色格。
- 灯笼像附图 1：宝塔翘檐、顶上提环和绿火、上下两层各两扇翠绿窗、中间横带、底座收尖；骨白到褐的铁框，近黑描边。
- 地上的灯笼：底尖离地 3 格、正中的十字没挪、光圈以地面线为中心、只有附图写的几样在动。
- 飞的灯笼：横放、提环朝左、底尖朝右、上下对称、尾巴在左边。
- 交付放 `outputs/thresh-lantern/`：两张 PNG、`manifest.json`、原始生成图放 `raw/`、`generation-prompts.txt`（实际用的提示词），
  最后写 `HANDOFF.md`，打包成 `outputs/thresh_lantern_done.zip`。

## Claude 收到后（给 Claude 看）

- 按原图自己的格子读回（4 像素一格），得到 `hd_w_ground`、`hd_w_lantern`（密度 2）；1x 的 `w_ground`、`w_lantern` 由高清帧缩出来。
- 只换 `league/effects/league_thresh_fx` 里这两段（`w_lantern` 换新、`w_ground` 新加），别的标签逐像素对比不变。
- `w_ground` 的时长：4 × 125 ms，再接一帧和第 1 帧一样的 100 ms（附加包每 0.5 秒重播一段，接缝看不出来）；`w_lantern` 4 × 70 ms。
- 地上灯笼的锚点：格子正中 = 落点，地面在正中往下 11 格（`tools/art/import_thresh.py` 的 FEET）。
