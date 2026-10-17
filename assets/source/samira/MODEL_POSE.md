# 莎弥拉：定稿换站姿（第 1b 步，给 Codex 的提示词）

> **模型（人物）已经定了，这一轮只换站姿。** 用户的原话：「站立的姿势换一换 模型已经可以了」，并附了另一个模组（oppi 的 Reborn 包）里莎弥拉的待机作参考。
> - **皮囊 = `1_design.png`（定稿，40 行）**：头、脸、眼罩、绿眼睛、头发、金发饰、墨绿上衣和红布带、露腹、黑手套、金色枪套、墨绿长靴、斜背的大刀（左上的红刀柄头和刀柄、右下伸出来的银刃刀身）、颜色、明暗、像素大小**全部照它**，不改长相、不加新颜色。
> - **骨架 = `2_pose.png`（oppi 的待机，已经放在我们的格子上：脚底第 99 行、两脚中间第 64 列）**：只学它的**站姿和拿武器的方式**——两脚分开站稳（比我们的定稿宽）、膝盖微弯；**两只手各拿一把枪垂在身体两侧，枪口斜着朝下朝外**（画面右边那只手拿长管转轮手枪、枪口朝右下；画面左边那只手拿短一点的手枪、枪口朝左下），枪管是浅灰 / 银白、黑描边，**伸出身体轮廓外，一眼能看到**；大刀照我们定稿斜背在身后（刀柄和红头在画面左上、刀身从右下伸出来），刀柄末端的红飘带往画面左边飘一小段。**不要照它的长相和颜色。**
> - **头逐格贴**：`4_head.png` / `4_head_1x.png` 是定稿的头（头发顶第 60 行），原样贴在新姿势里同一个位置（只平移，不转、不压扁、不重画），画面左眼的眼罩、右边的绿眼睛逐格一样。长辫子接在后脑往右下垂。
> - **大小**：头发顶到脚底仍然 **40 格**（绿线到红线，照 `3_guide.png`），宽度随姿势变（约 40 格，枪伸出去）；脚底在第 99 行，两脚中间在第 64 列；脚底线以下什么都不能有。
> - **手臂和手**：两条手臂都是定稿的手臂（古铜色皮肤、黑露指手套、一样粗），从肩膀垂下来、手肘微弯，**两只手和枪都在身体两侧看得见，不藏到身体后面**；胯边的金色枪套变空（枪拿在手里了）。
> - 交回前请整理好：每个像素一个严格对齐的 8×8 纯色块，透明度只有 0 和 255，**只用定稿的颜色**（`5_palette.png`），描边只用一种近黑色。交付到 `outputs/samira-pose/`：`samira_pose.png`（1024×1024）、`samira_pose_1x.png`（128×128）、生图原稿（`raw/`），**最后写** `HANDOFF.md`（写明头发顶到脚底多少格、宽多少格、头是否逐格贴回），最好再打成 `samira_pose_pack.zip`。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_design.png` / `1_design_1x.png` | **定稿**（皮囊），放大 8 倍 / 原尺寸 | 长相、颜色、像素大小、刀 |
| `2_pose.png` | oppi 的莎弥拉待机，放在同一个画布上（脚底第 99 行，两脚中间第 64 列），放大 8 倍 | **只学站姿和拿枪的方式** |
| `3_guide.png` | 画布：红线 = 脚底，蓝线 = 两脚中间，绿线 = 头发顶（40 格），橙框 = 头的位置；灰色是定稿现在的剪影 | 大小和位置 |
| `4_head.png` / `4_head_1x.png` | 要逐格贴回的头 | 贴头 |
| `5_palette.png` | 定稿的全部颜色 | 色板 |

## 提示词：`samira_pose.png`

附图顺序：`1_design.png`、`2_pose.png`、`3_guide.png`、`4_head.png`。

```text
Four attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block, 40 squares from the top of her hair to her soles) - this is the SKIN: copy her head, face, eyepatch with its red strap on the image-left eye, the bright green eye, the dark teal-black hair with gold ornaments, the braid, the dark green-black top with the red sash, the bare midriff, the bronze skin, the black fingerless gloves, the gold hip holsters, the dark green over-the-knee boots, the greatsword slung across her back (its red pommel and hilt up at image left, its blade with a silver edge showing at the lower right), every color, the shading and the pixel size EXACTLY; do not redesign anything. SECOND: another game's sprite of the same character in her idle stance, on the same canvas - this is the SKELETON: copy ONLY its stance and how she holds her weapons, NOT its look or colors. THIRD: the canvas guide - the red line is the bottom of the soles' row (row 99), the blue line the middle between her feet (column 64), the green line the top of her hair (40 squares above the soles), the orange box where her head goes. FOURTH: her head from the FIRST image.
Task: redraw the FIRST image's character in the SECOND image's stance, as one 1024x1024 image (a 128x128-square canvas at 8x), every pixel a crisp 8x8 square on one 8-px grid, nothing smaller, no anti-aliasing, no blur, no semi-transparency.
The stance: feet planted wider apart than in the FIRST image, knees slightly bent; BOTH ARMS hanging down at her sides, elbows a little bent, a PISTOL IN EACH HAND held low and pointing down and OUT: in the hand on the image right the long-barrelled revolver, its muzzle toward the lower right; in the hand on the image left the shorter pistol, its muzzle toward the lower left; the guns dark steel with gold fittings and LIGHT GREY / SILVER barrels with a near-black outline, sticking out past the body's outline so they read at once; the hip holsters empty. The greatsword stays slung across her back exactly as in the FIRST image (the red pommel and hilt above her shoulder at image left, the blade with its silver edge showing at the lower right past her front leg); the short red ribbon at the pommel streams out a little to the image left. The braid hangs down behind her at image right.
The head: paste the FOURTH image square for square at the orange box (the top of the hair on the green line), only moved if the body needs it; never redraw, turn or squash it.
Rules: ONLY the colors of the FIRST image, no new colors; a 1-square near-black outline around the silhouette; the arms the FIRST image's arms (same skin, gloves and thickness), both hands and both guns in sight beside the body, never behind it; 40 squares from the top of the hair to the soles; the soles on the red line, the middle of the feet on the blue line; NOTHING below the soles. Transparent background (if not possible: solid #00FF00 green). No grid lines, no text, no border, no shadow, no effects.
Before finishing, check: 40 squares tall; the head identical to the FOURTH image; both pistols in her hands pointing down and out, their silver barrels outside the body's outline; the greatsword on her back as in the FIRST image; only the FIRST image's colors; one outline color; nothing below the soles.
```

## 骨架 + 皮囊的短提示词（生图画不准时用；附图1 = `2_pose.png`，图2 = `1_design.png`）

```text
参考图1的站姿和拿武器的方式，把图1里的角色换成图2的角色。
1. 画布和图1一样（1024×1024，128×128 格，每格 8×8 纯色方块），脚底在第 99 行，两脚中间在第 64 列，头发顶到脚底 40 格。
2. 姿势照图1：两脚分开站稳，两只手各拿一把枪垂在身侧，枪口斜朝下朝外，银灰色枪管伸出身体轮廓外。
3. 长相、配色、细节全部是图2：头逐格照图2（画面左眼墨绿眼罩和红系带、右边绿眼睛、墨绿黑头发和金发饰、长辫子）、墨绿黑上衣和红布带、露腹、黑手套、空的金色枪套、墨绿长靴、斜背的大刀（左上红刀柄头、右下银刃刀身）。只用图2的颜色。
背景纯绿色 #00FF00，方便抠图。
```

## 交回前自查

- [ ] 头发顶到脚底 40 格，脚底第 99 行、两脚中间第 64 列，脚底线以下没有像素；
- [ ] 头和定稿逐格一样（眼罩、绿眼睛、金发饰）；
- [ ] 两只手各拿一把枪，垂在身侧、枪口斜朝下朝外，银灰枪管伸出轮廓外；枪套空了；
- [ ] 大刀照定稿斜背在身后，红飘带往左飘一小段；
- [ ] 只用定稿的颜色、一种描边色、严格 8×8 方块、透明度 0/255；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 按格子读回，查头是否逐格一样（不一样就贴回定稿的头）、色板、脚底线、两只手和枪；新站姿通过后就是待机和所有动作的身体标准，再出第 2 步动作条包。
