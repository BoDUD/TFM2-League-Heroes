# 泽丽：按精修后的大小重新画干净（第 1b 步，给 Codex 的提示词）

> 上一轮你交的 `zeri_design_B`（32×42）用户选了，但说：**「头太大了」「整体模型尺寸也太大了」「还有好多模糊的地方」**。我把它整行整列删成了 `zeri/1_target.png`（**28 格宽、36 格高；发髻尖到下巴只有 15 行**，原来 21 行），大小和头身比用户认可，但**头发和外套里有很多深色 / 黑色的碎线条和杂色块**，看起来又花又糊。这一轮请**照 1_target 的大小、比例、姿势和位置，重新画一张干净的**。
> - **大小和位置完全照 `1_target.png`**：最高点（发髻尖）到鞋底 **36 格**，最宽 **28 格**（两条紫线以内），鞋底在第 99 行（y=792–799，红线），两脚中间在 x=512（蓝线），最高点在绿线。`5_target_rows.png` 是 1_target 放大 12 倍、每行编了号：**第 0–4 行是两个发髻（第 0 行只有枪口），第 5–14 行是头（刘海到下巴，脸 7–8 行高），第 15 行起是身体**，请保持这个分配。
> - **长相照 `2_look.png`（用户选的那张）和原画 `3_picture.png`**：两个尖刺发髻（外圈深青蓝尖刺 + 里面柠檬黄绿）、黄绿色大眼睛、脸颊创可贴、宽大的青蓝外套 + 银管、黄色背心 + 洋红绿闪电、红棕皮带、深紫红紧身裤、棕色短靴 + 橙色袜口、画面右侧竖举的柠檬黄 + 橙色步枪和握枪的手、画面左侧垂下的紫红手套。
> - **干净（这一轮最重要）**：质量照 `4_quality_bar.png` 里的**金克丝、凯特琳、辛德拉、萨勒芬妮**：大块平涂、每种材质 2–3 档、形状一眼看清。
>   - **头发**：柠檬黄绿用 3 档（亮 / 中 / 暗）画成几大绺清楚的尖刺，**头发里面不要黑线、不要深蓝碎点**；发髻外圈的深青蓝尖刺是几根完整的尖，不是散点。
>   - **外套**：青蓝 3 档（亮青高光、中青、深蓝暗部）大块，**外套里面的折痕用深蓝，不用黑色**；银管 = 一条 1 格宽的浅灰线，扣子最多 2–3 个。
>   - **整个造型只有最外一圈是近黑描边**；里面的分界（外套和背心、手臂和外套、裤子两条腿）用该材质自己的暗色，尽量少用黑。
>   - **不要任何单个的杂色格子**（一个格子周围八个都不是它的颜色就不要留）；最多 **20 色**。
> - **脸照 2_look 的样子缩小**：两只黄绿眼睛（各 1×2 格 + 白色高光）、小鼻子 1 格、小嘴 1–2 格、左脸颊白色创可贴 1 格；脸不能被头发或枪挡住。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，描边只用一种近黑色。交付到 `outputs/zeri-refine/`：`zeri_refine.png`（1024×1024）、`zeri_refine_1x.png`（128×128，鞋底在第 99 行），**生图原稿（raw/ 文件夹）**、色板、`HANDOFF.md`（**最后写**，写明读回来多高多宽、几种颜色），最好再打一个 zip（`zeri_refine_pack.zip`）。**画不到正好 36 格时也交最接近的（34–38 格）和原稿**，我按格子读回再整行整列删。

## 附图（压缩包 `zeri_pack1b.zip` 的 `zeri/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_target.png` | 精修后的大小（28×36）放在 1024×1024 画布上（128×128 格 ×8）；红线 = 鞋底那一行的下沿，蓝线 = 两脚中间，绿线 = 最高点，紫线 = 最宽 28 格 | **大小、头身比、姿势、位置照它**（颜色和线条太花，不要照它的杂线） |
| `2_look.png` | 用户选的上一版造型（32×42）×8 | **长相、颜色** |
| `3_picture.png` | 用户选的原画 A | 部件的形状 |
| `4_quality_bar.png` | 金克丝、凯特琳、辛德拉、萨勒芬妮，游戏里现在的样子 ×8，同一条脚底线 | **干净程度照它们** |
| `5_target_rows.png` | 1_target 放大 12 倍，每行编号 | 发髻 0–4 行、头 5–14 行、身体 15–35 行 |

## 提示词：`zeri_refine.png`

附图：`zeri/` 里的 1–5 号图，按顺序。

```text
Five attached images. FIRST: a 1024x1024 canvas (128x128 squares at 8x) with this character at her FINAL game size - 36 squares from the tips of her hair buns to her soles, 28 squares wide - this is the SIZE, the HEAD-TO-BODY PROPORTION, the POSE and the PLACE to keep exactly; but its colours are noisy (dark specks and black lines inside the hair and the coat) - do NOT copy that noise. SECOND: the approved look of the character at a larger size - copy her look and colours. THIRD: the approved illustration - the shapes of her parts. FOURTH: heroes of this game as they are in the game now, at 8x - match their CLEAN look: big flat areas, 2-3 shades a material, readable shapes. FIFTH: the FIRST image at 12x with every row numbered: rows 0-4 are the two hair buns (row 0 only the rifle muzzle), rows 5-14 the head (bangs to chin; the face 7-8 rows), rows 15-35 the body - keep this split.
The character: Zeri, a lively street girl crackling with electricity: two SPIKY HAIR BUNS on top of her head (an outer ring of dark teal-blue spikes around bright LIME YELLOW-GREEN hair), lime bangs and side strands, warm tan skin, big YELLOW-GREEN EYES, a white plaster on her left cheek; an OVERSIZED TEAL-BLUE COAT with a silver tube across her chest; a YELLOW TANK TOP with a small magenta-and-green lightning print; a red-brown belt; tight DARK MAROON LEGGINGS; BROWN ANKLE BOOTS with orange socks; the image-RIGHT hand holds an upright LIME YELLOW AND ORANGE ELECTRIC RIFLE beside her head (not covering the face), the image-LEFT arm hangs with a maroon fingerless glove.
Task: redraw her as a SMALL, CLEAN game sprite - a low-resolution pixel-art character shown enlarged 8x, every pixel one crisp 8x8 square on a single 8-px grid, exactly where the FIRST image's figure stands and as big: 36 squares tall, at most 28 wide, the soles' row at y=792-799 (the red line), the middle between her feet on x=512 (the blue line), the top on the green line, nothing outside the purple lines, nothing below the soles.
Clean (most important): at most 20 colours; ONE 1-square near-black outline round the whole silhouette and almost no black inside it - inner edges (coat against tank top, arm against coat, one leg against the other, coat folds) in each material's own dark shade; the HAIR as a few clear lime spikes in 3 shades (light, mid, dark) with NO black lines and NO dark-blue specks inside, the buns' outer ring a few whole dark teal spikes; the COAT in 3 teal shades (bright cyan highlight, mid teal, deep blue shadow) in big areas, folds in deep blue not black, the silver tube one 1-square light grey line, at most 2-3 silver clasps; NO lone square whose eight neighbours are all other colours; no dithering, no gradients, no noise.
Face, as the SECOND image but smaller: two yellow-green eyes (1x2 squares each with a white highlight), a 1-square nose, a 1-2 square mouth, a 1-square white plaster on her left cheek; nothing covers the face.
Palette (adjust if needed): #100C14 outline (the only near-black); hair #7A9A08 #B4E01E #E8FA5A, bun spikes #12305A #2A6A9A; coat #0E3E66 #1670A0 #22A0C8 #6ADCF0; tank top #D88A10 #F6C21E; print #E0287A #6AD02A; belt #A8261E; leggings #3E1838 #6A2A5A; glove #6A2448; boots #5A2E1E #8A4A30; socks #F6A418; rifle #6A8A10 #C8E828 #F08A18 #3A3A44; skin #C8784A #F2B47E; silver #C8CCD6 #F2F4F8; eyes #3A8A10 #9AD82A.
Layout: one square image, 1024x1024 (128x128 squares at 8x). Transparent background (if not possible: solid #00FF00). No grid lines, no text, no border, no shadow.
Before finishing, check: 36 squares tall (34-38 at most), at most 28 wide, soles on row 99; at most 20 colours; one outline colour and almost no black inside; the hair, the coat and the face clean and readable; both hands, the rifle, the buns, the plaster and the lightning print visible.
```

## 交回前自查

- [ ] 36 格高（34–38）、最宽 28 格、鞋底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 20 色、描边只有一种近黑；
- [ ] 发髻 0–4 行、头 5–14 行（脸 7–8 行高）、身体 15–35 行；
- [ ] 头发里没有黑线和深蓝碎点；外套折痕用深蓝；没有单个杂色格；
- [ ] 眼睛、创可贴、闪电图案、握枪的手、垂下的手、步枪、靴子都清楚；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按格子读回（`regrid.py`），检查高度 / 宽度 / 色数 / 杂色格 / 内部黑线，和 p35c、codex_B、包里的英雄并排给用户看；用户通过后才出动作帧包（第 2 步）。
