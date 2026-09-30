# 九尾妖狐 阿狸：只重画尾巴（给 Codex 的返修包）

> 用户反馈：选人卡片上阿狸"尾巴太多，都拖到地面了，看起来很冗杂"（比赛里 1 倍大小还好）。
> 现在的 8 条动作条（`now/`，你上一轮画的）里，九条白尾巴围成一圈扇形：从狐耳上方一直到脚边，身后、身前两边都有，最下面的尾尖碰到脚底线。卡片把待机放大约 2.2 倍（黑底），整个人被一团白色包住（见 `guide/compare_now_round1_league.png` 左边和 `guide/card_now.png`）。
> **这一轮只重画尾巴**，其他所有像素（头、脸、眼睛、黑长发、狐耳、红白衣服、皮肤、腿、姿势、每帧的位置）逐格保持不变。

## 要的样子（照英雄联盟原版）

- 尾巴是**一束**，从她的后腰（背对的那一侧：她朝右，所以尾巴在左边）长出来，往后、往上扬开，像一把半开的扇子；看得见 5～6 条（九条互相叠着），每条是白色的大毛尾，尾尖略带淡紫。
- 尾尖的高度在**腰到头顶之间**；**膝盖以下不要有尾巴**，绝对不碰脚底线。
- **身前（右边）不要有尾巴**，头顶上方也不要有；尾巴永远在身体和黑长发**后面**（被身体、头发挡住）。
- 整束尾巴的大小：待机时约 16～20 格宽、18～22 格高（现在的扇形约 34 格宽、38 格高，要小一半左右）。
- 参考 `guide/compare_now_round1_league.png`：中间「第一版」和右边「英雄联盟原版（游戏尺寸）」的尾巴就是要的方向（第一版的尾巴是按英雄联盟的动画逐帧渲染的，位置对，但画风粗糙；请用你这一版的画风画）。

## 每帧放在哪

- `league/ahri_league_<动作>.png`：第一版的动作条，**同样的格子、同样的站位点**，每帧尾巴的位置和朝向就是英雄联盟原版在这一帧里的样子（跑步时往后拖、普攻和技能时跟着身体甩动、受击往后仰、死亡倒地）。
- `guide/tails_guide_<动作>.png`：你现在的帧（灰色）叠上英雄联盟尾巴在这一帧的位置（**橙色 = 尾巴该在的地方**）。每帧照橙色的位置和方向画尾巴，可以比橙色稍大一点（第一版的尾巴偏小），但不要超出上面「要的样子」的范围。
- 跑步等动作里，原版尾巴大部分被身体挡住，露出来的不多：照样只画露出来的部分，**不要为了显眼再加一圈**。

## 规则

- 格子和排版完全照 `now/`：每张动作条 72×64 格一帧（1 倍图 `now/ahri_<动作>_1x.png`，8 倍图 `now/ahri_<动作>.png`），帧数、顺序、每帧位置不变，站位点见 `ahri_cells.json`。
- 8×8 方块、硬边、没有抗锯齿、透明度只有 0/255。
- 颜色只用现在这套：毛色 `#F9F4FC`（亮白）、`#CFCEFD`、`#BCBCFC`、`#B6B6FD`（淡紫阴影）、`#B8B6CA`（灰紫暗部），描边 `#06010C`（一格黑边，尾巴和身体之间也要有）。
- 去掉旧尾巴后露出来的地方：原来被尾巴挡住的身体、腿、裙摆、头发要补画完整（照相邻帧和定稿 `design/ahri_native.png`），其余的变成透明背景。
- 头、脸、眼睛不要动（这些是用户定过的）。

## 交付

- `ahri_<动作>.png`（8 倍）和 `ahri_<动作>_1x.png`（1 倍），8 个动作：idle、run、attack、skill、skill2、ult、hit、dead，文件名和排版同 `now/`。
- 待机 6 帧用同一张（和现在一样都是定稿这一帧），所以**先把待机画好**，再按它的尾巴画其他动作。
- 另交一张检查图：待机放大 2.2 倍放在黑底（`#18161E`）上，看尾巴是不是清爽、不碰地、身前没有尾巴。
- `HANDOFF.md`：每个动作改了哪些帧、有没有没做到的地方；`manifest.json`（每帧的格子位置）。

```text
Pixel art sprite REVISION for a small tactics game, chunky 8x8 squares, hard edges, no anti-aliasing, 1-square dark outline #06010C. Character: Ahri, a fox-girl mage (black long hair, fox ears, red-and-white outfit), facing right. Redraw ONLY her nine fox tails in every frame of the attached sprite strips; keep every other square (head, face, eyes, hair, ears, outfit, skin, legs, pose, position in the cell) exactly as it is. The tails must be ONE bundle growing from her lower back on the side she faces away from (the left), fanning backward and upward like a half-open fan: 5 to 6 tails visible (the nine overlap), big white fluffy tails (#F9F4FC) shaded with pale lavender (#CFCEFD, #BCBCFC, #B6B6FD, darkest #B8B6CA), each tip slightly lavender. The tail tips stay between her waist and the top of her head; nothing below her knees, never touching the ground line; no tail in front of her body (right side) and none above her head; the tails are always behind her body and her hair. In the idle the bundle is about 16-20 squares wide and 18-22 squares tall (the current fan is about 34 x 38: half that size). Follow the tails' placement and direction in each frame from the League reference strips (orange areas in the guide images); in motion the tails trail and swing with the body. Where removing the old tails uncovers her body, legs, skirt or hair, complete them; everything else there becomes transparent. Same cell grid, frame count and order as the attached strips (72x64 squares per frame).
```

## 附件

| 文件 | 内容 |
|---|---|
| `now/ahri_<动作>.png`、`now/ahri_<动作>_1x.png` | 现在的 8 条动作条（8 倍 / 1 倍）：在这上面只改尾巴 |
| `league/ahri_league_<动作>.png` | 第一版（按英雄联盟动画渲染）的同一套格子：每帧尾巴的位置和方向 |
| `guide/tails_guide_<动作>.png` | 现在的帧（灰）+ 英雄联盟尾巴的位置（橙） |
| `guide/compare_now_round1_league.png` | 现在 / 第一版 / 英雄联盟原版的尾巴对比（上排放大 5 倍，下排是卡片的 2.2 倍） |
| `guide/card_now.png` | 现在的待机在选人卡片上的样子（问题所在） |
| `design/ahri_native.png` | 定稿（待机这一帧，8 倍），补画被尾巴挡住的部分时参考 |
| `ahri_cells.json` | 每帧的站位点和英雄联盟头部骨骼的位置（格子坐标） |
