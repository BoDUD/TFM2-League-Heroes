# 伊莉丝：人形跑步重画腿（给 Codex 的提示词）

> 上一轮的人形跑步（`run`，8 帧）里，**8 帧都是同一条腿在前面落地，另一条一直抬在后面，两条腿从来没有换位置**，用户说「交叉步都没 腿不换步的？」；我用造型的腿拼的那版又把斜着的腿拉直、变了形。这一轮**只重画腿**（用 image_gen 画，不要用脚本拼）：
> - `now/elise_run_<n>.png`：这一帧的上半身（就是造型本身：头、背后六条蜘蛛腿、手臂、紧身衣都画好了，**不要改**），**两条腿已经去掉了**（大腿根以下）。
> - `guide/elise_run_<n>.png`：同一张图，上面用**线**标出这一帧两条腿的位置：**红线 = 近侧腿（颜色亮、在前）**，**蓝线 = 远侧腿（暗一档、在后）**；每条线是 **髋 → 膝 → 脚踝 → 脚尖**（小圆圈是关节，实心大圆点是靴尖）。**红色横线 = 地面**（鞋底落在它上面），**蓝色叉 = 站位点**。线只是位置，**不要画进图里**。
> - 两条腿**轮流**在前：红腿第 1 帧在前方落地 → 第 2–3 帧到身体正下方 → 第 4 帧在身后蹬地 → 第 5–6 帧抬起、往后踢 → 第 7 帧屈膝从身体下面往前摆 → 第 8 帧向前伸；蓝腿一样，**比红腿晚半拍（差 4 帧）**。**第 1–4 帧和第 5–8 帧两条腿前后对调**；**第 3 帧和第 7 帧两条腿在身体下面交叉**（一条撑地，另一条屈膝从它旁边往前摆过去）——这就是交叉步。
> - 腿的样子照造型（`ref/elise_human_design.png`，腿的特写 `ref/elise_legs_design.png`）：大腿根露一点**苍白偏灰紫的皮肤**，下面是**黑紫色的过膝长靴**，靴子外侧和前面有**鲜红色的条纹**，**尖头高跟**、鞋尖朝右；**粗细、长短每帧一样**，和造型一样（不要画细、画长、画成木棍，也不要画粗）；近侧腿全亮色，远侧腿暗一档、和近侧腿重叠的地方画在它后面；落地的那只脚**鞋底平平地踩在红色地面线上**（踮着高跟），抬起的脚离开地面。背后的蜘蛛腿不要改，腿画在它们前面。
> - 每格 7 × 7 px（1536×1024 里 219 × 146 格），和上一轮同一个格子；只用造型的颜色；外轮廓近黑描边和造型一样粗；**alpha 只能是 0 或 255**；不要抖动、渐变、半透明。
> - 交付到 `outputs/elise-run/`：`elise_run_1.png` … `elise_run_8.png`（1536×1024、透明背景，**上半身和 `now/` 那张一样**，加上你画的两条腿）+ 生图原稿原样放 `raw/`（不要自己整理、不要重采样）；**最后**写 `HANDOFF.md`；最好打成 `elise_run_done.zip`。
> - 一帧一次，画后一帧时附上前一帧（让腿的粗细、长度、靴子大小一样）。

## 附图（每帧按这个顺序附）

1. `guide/elise_run_<n>.png`（这一帧的腿线）
2. `now/elise_run_<n>.png`（这一帧去掉腿的上半身，要保留不动）
3. `ref/elise_legs_design.png`（造型的腿放大 10 倍：靴子、红条纹、高跟的样子和颜色）
4. 同一套跑步的前一帧（你刚交付的那张；第 1 帧不附）
5. `ref/caitlyn_run_reference.png`（用户认可过的交叉步跑步，本包另一个英雄，6 倍放大：只看两条腿怎么轮流）

`ref/elise_human_design.png` 是整个造型（看比例）；`step2/` 是上一轮的跑步（要改掉的样子），只给你看。

## 提示词（每帧一次，用 image_gen）

```text
Image 2 is the upper body of a cold, beautiful spider priestess running to the right, already finished (dark red-black hair with horn-like points, a dark crown, red eyes, a black-purple gown with red trim, long black claws, six black spider legs with red claw tips on her back) with her legs taken away at the tops of her thighs, on a 1536x1024 canvas on a grid of 7x7-pixel squares. Image 1 is the same picture with THIS FRAME'S LEGS marked as lines: the RED line is her NEAR leg (full tone, in front), the BLUE line her FAR leg (one shade darker, behind); each line runs hip - knee - ankle - toe (small circles are the joints, the big filled dot is the boot's toe); the red horizontal line is the ground, the blue cross the standing point. Image 3 shows her approved legs from her design, 10x (a little pale grey-lilac skin at the top of the thighs, then black-purple thigh-high boots with bright red stripes down their outer side and front, pointed high heels). (Image 4, when attached, is the previous frame of this run: keep the legs exactly as thick and long, the boots as big.) Image 5 shows how another character's legs take turns in a cross-step run (only the leg motion).
Draw with the image generator ONE frame: Image 2 exactly as it is - the head, the spider legs on her back, the arms, the gown unchanged - plus her two legs placed exactly along the lines of Image 1: <WHAT>
Rules: the same 1536x1024 transparent canvas and the same 7-pixel grid as Image 2, every square one flat colour from the design's colours; the legs start right at the tops of the thighs under the gown; the knees bend the way the lines bend; the boots' red stripes as in Image 3, the pointed high heels pointing right; the NEAR (red-line) leg in full tone, the FAR (blue-line) leg one shade darker and drawn BEHIND the near one where they overlap; both legs as thick and as long as in Image 3, never thinner, longer or stiff like posts; the legs in front of the spider legs on her back; a planted foot stands on the red ground line on its toe and heel, a lifted foot is off the ground; nothing below the ground line; the same near-black outline as the design; alpha only 0 or 255; no dithering, no gradients, no anti-aliasing, no semi-transparency; no lines, crosses, dots or text from Image 1, no effects, no dust. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>`，按帧换成：

- 1：`the NEAR (red) leg planted far ahead, its boot on the ground in front of her, the knee nearly straight; the FAR (blue) leg just pushed off behind, its boot lifting off the ground behind her.`
- 2：`the NEAR (red) leg on the ground under the front of her body, the knee bent as she lands on it; the FAR (blue) leg kicked up behind her, the heel rising, the knee bent.`
- 3：`the NEAR (red) leg straight down under her hips, its boot on the ground (carrying her weight); the FAR (blue) leg swinging FORWARD past it under her body, the knee bent high in front, the boot off the ground - the two legs cross under her.`
- 4：`the NEAR (red) leg behind her, pushing off the ground with the boot's toe; the FAR (blue) leg reaching forward, the knee up in front, the boot just above the ground ready to land.`
- 5：`the NEAR (red) leg just pushed off behind, its boot lifting off the ground behind her; the FAR (blue) leg planted far ahead, its boot on the ground in front of her, the knee nearly straight.`
- 6：`the NEAR (red) leg kicked up behind her, the heel rising, the knee bent; the FAR (blue) leg on the ground under the front of her body, the knee bent as she lands on it.`
- 7：`the FAR (blue) leg straight down under her hips, its boot on the ground (carrying her weight); the NEAR (red) leg swinging FORWARD past it under her body, the knee bent high in front, the boot off the ground - the two legs cross under her, the near leg in front.`
- 8：`the NEAR (red) leg reaching forward, the knee up in front, the boot just above the ground ready to land; the FAR (blue) leg behind her, pushing off the ground with the boot's toe.`

## 交回前请检查

- 8 帧都在，每张 1536×1024 透明底、7 px 一格、alpha 只有 0 / 255，`_1x` 和大图逐格一致；都是 image_gen 画的。
- **上半身和 `now/` 一样**（头、背后的蜘蛛腿、手臂、紧身衣不改）。
- 两条腿沿着线：红 = 近侧亮色腿，蓝 = 远侧暗色腿；**第 1–4 帧和第 5–8 帧两条腿的位置对调**；**第 3、7 帧两条腿在身体下面交叉**。
- 腿的粗细、长短、红条纹、高跟每帧一样（照造型）；落地的脚踩在地面线上，地面线以下没有东西；没有线、叉、点、文字、特效。
- 全部画完后最后写 `outputs/elise-run/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读原稿（raw/），量格子、读回到设计格子；**只取 Codex 的腿**（大腿根以下、背后蜘蛛腿以外），贴回 `now/` 那一帧的上半身（同一颗头），腿和身体的接缝查缝隙；**逐帧量两只脚的 x**（前后脚每半个周期对调、第 3、7 帧交叉），8 倍下查腿是否变形、粗细一致；只改 run，其他动作逐字节不变，再做前后对比 GIF 给用户看。
