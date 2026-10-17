# 诺提勒斯：把头盔画小一点（第 1b 步，给 Codex 的提示词）

> **这一轮只重画一张造型图，不画动作。** 用户选了 `nautilus/1_current.png`（p35：你上一轮第二次生图原稿 `A_simple` 按格子取回、整行整列删到 39×48 格，锚高出头盔 11 格），但说**「头适当的小一点 学这张图」**，指的是你上一轮**第一次的生图原稿 `A_first`**（`nautilus/2_head_reference.png`，按它自己的格子取回）：那里**头盔比肩膀窄得多，两边和下面露出铜色的胸甲、肩甲**，人更像一个穿潜水服的壮汉，而不是一个大头盔长了腿。直接把 A_first 删到游戏尺寸会糊（红眼睛和锚都看不清），所以请**在游戏尺寸直接重画一张**。
> - **以 p35 为准的**：整体大小和位置、姿势、背上的锚（形状、大小、高出头盔 11 格）、近侧手握锚杆 + 垂下的铁链、远侧握拳的手、腿和靴子、全部颜色（只用下面 23 色）、像素大小和干净程度。
> - **照 A_first 改的只有头盔和它周围**：
>   - 头盔（铜管兜帽顶到护颌下沿那条海绿缝线）从现在的 **23 行 × 21 列缩到约 18 行 × 14 列**（绿线到青线之间）；
>   - 头盔两边露出**铜色的胸甲和大肩甲**（像 A_first 那样，肩甲比头盔宽出一截），胸甲上的海绿缝线照 A_first 的走向；
>   - 头盔省下来的高度给身体和腿：腿从现在的 13 行变成 **15–17 行**，头盔顶还是在绿线（第 63 行），脚底还是在红线（第 99 行）；
>   - 头盔照样要有：顶上**三个 1 格的黑色通气孔**（竖着一列，中间隔 1 格），**黑色观察窗**里**两只红橙色的方眼睛**（各 2×2 或 3×3 格，中间 1 格最亮的黄），下面方形的铜护颌（3–4 道竖条），外面一圈锈红色的铜管兜帽。
> - **大小**：头盔顶到脚底 37 行（绿线到红线），锚最高到橙线（第 52 行），整个造型**不超出两条紫线（最宽 40 格）**；两脚中间在中间那一列（x=512，蓝线）；脚底以下什么都不能有。
> - **直接按游戏尺寸画**，不要先画大再缩小；画不准时把最接近的那张也交来，生图原稿全部放进 `raw/`。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，**只用下面 23 色**，描边只用一种近黑色。交付到 `outputs/nautilus-refine/`：`nautilus_refine.png`（1024×1024）、`nautilus_refine_1x.png`（128×128，和 p35 同一个画布、同一条脚底线），`raw/`，`HANDOFF.md`（**最后写**，写明头盔多少行多少列、头盔顶到脚底多少行、锚高出几格、整个造型多宽），最好再打成一个 zip（`nautilus_refine_pack.zip`）。

## 附图（都在压缩包的 `nautilus/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_current.png` | 现在的造型 p35，放大 8 倍（1024×1024，白底）；`1_current_1x.png` 是原尺寸 | **大小、姿势、锚、手、腿、颜色照它** |
| `2_head_reference.png` | 你上一轮第一次的生图原稿 A_first，按它自己的格子取回（71×78 格）×8 | **头盔和身体的比例照它**：头盔窄、肩甲宽、露出胸甲 |
| `3_picture.png` | 用户选的原画 A | 长相参考 |
| `4_quality_bar.png` | 包里的阿利斯塔、布里茨、蕾欧娜、慎、佛耶戈 ×8 | 像素大小和干净程度 |
| `5_target.png` | p35 淡色剪影 + 参考线：红 = 脚底（第 99 行下沿），蓝 = 两脚中间，绿 = 头盔顶（第 63 行），青 = 护颌最低到这里（第 81 行），橙 = 锚最高（第 52 行），紫 = 最宽 40 格 | **头盔画在绿线和青线之间** |

## 提示词：`nautilus_refine.png`

五张图都附上，顺序同上表。

```text
Five attached images. FIRST: the approved game-size pixel-art design of this character at 8x (every pixel an 8x8 block) - keep its size, its place, its pose, the anchor on his back, the near hand holding the anchor's shank with the iron chain hanging, the far fist, the legs and boots, all its colours and its clean pixel style. SECOND: an earlier draft of the same character, read back square for square at 8x - learn ONLY its proportions: a SMALLER helmet, much narrower than his shoulders, with the bronze CHEST PLATES and BIG SHOULDER PLATES showing on both sides of it and below it. THIRD: the approved full picture of the character - for his look. FOURTH: heroes of this game at game size at 8x - match their pixel size and their clean look. FIFTH: the FIRST image faded on the canvas with guide lines.
The character: Nautilus, a silent, heavy giant in an ancient rusted bronze diving suit: a round bronze diving helmet (three small black vent holes in a column on top, a black viewing slit with two glowing red-orange square eyes, a square bronze jaw guard of vertical bars, a rusty-red pipe hood round it), rusted bronze chest and shoulder plates with glowing sea-green seams, dark grey-black suit arms and legs, big grey gloves, bronze knee guards, huge diving boots with thick bronze soles, a thick grey iron chain, and a grey stone-iron anchor carried on his back, its crown and flukes arching over the back of his helmet.
Task: redraw the FIRST image as ONE game sprite with a SMALLER HEAD, the way the SECOND image is built: the helmet (from the top of its pipe hood to the sea-green seam under the jaw guard) only about 18 squares tall and 14 squares wide (between the FIFTH image's green and cyan lines), the bronze shoulder plates wider than the helmet on both sides, the bronze chest plates with their sea-green seams showing beside and below the jaw guard, and the height the helmet gives up going to the body and the legs (the legs 15-17 squares instead of 13). Keep everything else of the FIRST image: the helmet's top on the green line (square row 63), the soles on square row 99 (the red line), the point between his feet on the middle column (x=512, the blue line), the anchor exactly as in the FIRST image (its top on the orange line, square row 52), the chain, the hands, the boots, the hunched 3/4 front view facing image right; nothing outside the two purple lines (40 squares wide); nothing below the soles.
Pixel rules (most important): a SMALL game sprite, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency; ONLY these 23 colours of the FIRST image, no new colours: #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8; one 1-square near-black outline around the silhouette (#070211 only); big flat areas in 2-3 shades per material as in the FIRST image; no dithering, no noise, no lone specks.
The helmet must still read: three 1-square black vent holes in a column on top with a bronze square between them, the black viewing slit with two red-orange square eyes (2x2 or 3x3 squares each, the middle square the brightest yellow), the square bronze jaw guard of 3-4 vertical bars, the rusty-red pipe hood round it. Nothing covers the slit or the eyes.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x), the same canvas and the same place as the FIRST image. Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow.
Before finishing, check: the helmet about 18 squares tall and 14 wide, narrower than the shoulder plates, the chest plates showing; the helmet's top on row 63, the soles on row 99, nothing below; the anchor as in the FIRST image, its top on row 52; at most 40 squares wide; only the 23 colours; every square 8x8 on one grid; the three vent holes, the two red eyes, the jaw guard, both hands, the chain and the anchor's flukes readable.
```

## 交回前自查

- [ ] 头盔约 18 行 × 14 列，比肩甲窄，两边和下面露出胸甲；头盔顶在第 63 行，脚底在第 99 行，下面没有像素；
- [ ] 锚和 p35 一样（顶在第 52 行），铁链、两只手、靴子都在；最宽 40 格；
- [ ] 严格 8×8 网格、透明度 0/255、只用那 23 色、描边只有 #070211；
- [ ] 三个通气孔、两只红眼、护颌、铜管兜帽看得清；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按格子取回（交回的 1x 图优先，不在网格上的按格取多数色重读），核对色板、脚底线、宽度；和 p35、A_first 并排给用户看（8× 和包里的英雄 1×、4×）；用户通过后写进 `assets/source/native/nautilus_native.png`（`design_nautilus.py` 记下来源），再出第 2 步动作帧包。
