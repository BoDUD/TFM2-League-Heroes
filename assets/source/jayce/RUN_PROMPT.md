# 杰斯：两套跑步重画腿（给 Codex 的提示词）

> 上一轮的两套跑步（锤形 `run`、炮形 `c_run`，各 8 帧）里，两只脚一直停在差不多同一个位置，**两条腿没有明显地轮流往前**，用户说「跑步时腿没感觉到明显换位置啊」。这一轮**只重画腿**（用 image_gen 画，不要用脚本）：
> - `now/jayce_<动作>_<n>.png`：这一帧的上半身（头、手臂、外套、武器、身后的海军蓝长衣摆都画好了，**不要改**），**皮带以下的腿已经去掉了**。
> - `guide/jayce_<动作>_<n>.png`：同一张图，上面用**线**标出这一帧两条腿的位置：**红线 = 近侧腿（颜色亮、在前）**，**蓝线 = 远侧腿（暗一档、在后）**；每条线是 **髋 → 膝 → 脚踝 → 脚尖**（小圆圈是关节，实心大圆点是靴尖）。**红色横线 = 地面**（鞋底落在它上面），**蓝色叉 = 站位点**。线只是位置，**不要画进图里**。
> - 两条腿**轮流**在前：红腿第 1 帧在前方落地 → 第 2–3 帧到身体正下方 → 第 4 帧在身后蹬地 → 第 5–6 帧抬起、往后踢 → 第 7 帧屈膝从身体下面往前摆 → 第 8 帧向前伸；蓝腿一样，**比红腿晚半拍（差 4 帧）**。**第 1–4 帧和第 5–8 帧两条腿前后对调**；**第 3 帧和第 7 帧两条腿在身体下面交叉**（一条竖直撑地，另一条屈膝从它旁边往前摆过去）——这就是交叉步。
> - 腿的样子照造型（`ref/jayce_hammer_side_design.png`、`ref/jayce_cannon_side_design.png`）：**从皮带下面开始画灰蓝色的裤子**（大腿），**米金色的尖角护膝和护胫**、**深棕色的靴子**，**粗细、长短每帧一样**，和造型一样敦实（不要画细、画长、画成木棍）；近侧腿全亮色，远侧腿暗一档、和近侧腿重叠的地方画在它后面；靴子朝右；落地的那只脚**鞋底平平地踩在红色地面线上**，抬起的脚离开地面。身后的长衣摆不要改，腿画在衣摆前面。
> - 每格 5 × 5 px（1536×1024 里 307 × 204 格），和上一轮同一个格子；只用造型的颜色；外轮廓近黑描边约 2 格；**alpha 只能是 0 或 255**；不要抖动、渐变、半透明。
> - 交付到 `outputs/jayce-run/`：`jayce_run_1.png` … `jayce_run_8.png`、`jayce_c_run_1.png` … `jayce_c_run_8.png`（1536×1024、透明背景，**上半身和 `now/` 那张一样**，加上你画的两条腿）+ 生图原稿原样放 `raw/`（不要自己整理、不要重采样）；**最后**写 `HANDOFF.md`；最好打成 `jayce_run_done.zip`。
> - 一帧一次，画后一帧时附上前一帧（让腿的粗细、长度、靴子大小一样）。

## 附图（每帧按这个顺序附）

1. `guide/jayce_<动作>_<n>.png`（这一帧的腿线）
2. `now/jayce_<动作>_<n>.png`（这一帧去掉腿的上半身，要保留不动）
3. 这个形态的侧身造型：锤形跑步附 `ref/jayce_hammer_side_design.png`，炮形跑步附 `ref/jayce_cannon_side_design.png`（腿、护膝、靴子的样子和颜色）
4. 同一套跑步的前一帧（你刚交付的那张；第 1 帧不附）
5. `ref/caitlyn_run_reference.png`（用户认可过的交叉步跑步，本包另一个英雄，6 倍放大：只看两条腿怎么轮流）

`step2/` 是上一轮的跑步（要改掉的样子），只给你看。

## 提示词（每帧一次，用 image_gen）

```text
Image 2 is the upper body of a confident young man running to the right, already finished (short dark brown hair, a red scarf, a brown leather coat with cream-gold armour, his weapon, long dark navy coat tails flowing behind him) with his legs taken away below the belt, on a 1536x1024 canvas on a grid of 5x5-pixel squares. Image 1 is the same picture with THIS FRAME'S LEGS marked as lines: the RED line is his NEAR leg (full tone, in front), the BLUE line his FAR leg (one shade darker, behind); each line runs hip - knee - ankle - toe (small circles are the joints, the big filled dot is the boot's toe); the red horizontal line is the ground, the blue cross the standing point. Image 3 is the character's approved design (his legs: slate-blue trousers, cream-gold pointed knee guards and shin plates, dark brown boots). (Image 4, when attached, is the previous frame of this run: keep the legs exactly as thick and long, the boots as big.) Image 5 shows how another character's legs take turns in a cross-step run (only the leg motion).
Draw with the image generator ONE frame: Image 2 exactly as it is - the head, arms, coat, armour, weapon and coat tails unchanged - plus his two legs placed exactly along the lines of Image 1: <WHAT>
Rules: the same 1536x1024 transparent canvas and the same 5-pixel grid as Image 2, every square one flat colour from the design's colours; the trousers start right under the belt; the knees bend the way the lines bend; the cream-gold knee guards on the knees, the dark brown boots pointing right; the NEAR (red-line) leg in full tone, the FAR (blue-line) leg one shade darker and drawn BEHIND the near one where they overlap; both legs as thick and as long as in the design, never thinner, longer or stiff like posts; the legs in front of the coat tails; a planted foot lies FLAT on the red ground line, a lifted foot is off the ground; nothing below the ground line; the same near-black outline as the design (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no anti-aliasing, no semi-transparency; no lines, crosses, dots or text from Image 1, no effects, no dust. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>`，按帧换成（两套跑步一样）：

- 1：`the NEAR (red) leg planted far ahead, its boot flat on the ground in front of him, the knee nearly straight; the FAR (blue) leg just pushed off behind, its boot lifting off the ground behind him.`
- 2：`the NEAR (red) leg on the ground under the front of his body, the knee bent as he lands on it; the FAR (blue) leg kicked up behind him, the heel rising, the knee bent.`
- 3：`the NEAR (red) leg straight down under his hips, its boot flat on the ground (carrying his weight); the FAR (blue) leg swinging FORWARD past it under his body, the knee bent high in front, the boot off the ground - the two legs cross under him.`
- 4：`the NEAR (red) leg behind him, pushing off the ground with the boot's front; the FAR (blue) leg reaching forward, the knee up in front, the boot just above the ground ready to land.`
- 5：`the NEAR (red) leg just pushed off behind, its boot lifting off the ground behind him; the FAR (blue) leg planted far ahead, its boot flat on the ground in front of him, the knee nearly straight.`
- 6：`the NEAR (red) leg kicked up behind him, the heel rising, the knee bent; the FAR (blue) leg on the ground under the front of his body, the knee bent as he lands on it.`
- 7：`the FAR (blue) leg straight down under his hips, its boot flat on the ground (carrying his weight); the NEAR (red) leg swinging FORWARD past it under his body, the knee bent high in front, the boot off the ground - the two legs cross under him, the near leg in front.`
- 8：`the NEAR (red) leg reaching forward, the knee up in front, the boot just above the ground ready to land; the FAR (blue) leg behind him, pushing off the ground with the boot's front.`

## 交回前请检查

- 16 帧都在（`run` 8、`c_run` 8），每张 1536×1024 透明底、5 px 一格、alpha 只有 0 / 255，`_1x` 和大图逐格一致；都是 image_gen 画的。
- **上半身和 `now/` 一样**（头、手臂、外套、武器、长衣摆不改）。
- 两条腿沿着线：红 = 近侧亮色腿，蓝 = 远侧暗色腿；**第 1–4 帧和第 5–8 帧两条腿的位置对调**；**第 3、7 帧两条腿在身体下面交叉**。
- 腿的粗细、长短、护膝、靴子每帧一样（照造型）；落地的脚平踩在地面线上，地面线以下没有东西；没有线、叉、点、文字、特效。
- 全部画完后最后写 `outputs/jayce-run/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读原稿（raw/），量格子、读回到设计格子；**只取 Codex 的腿**（皮带以下、衣摆以外），贴回 `now/` 那一帧的上半身（rig_jayce 再贴同一颗头），腿和皮带、衣摆的接缝查缝隙（gap-check）；逐帧 8 倍自查腿是否变形、粗细一致、两腿交替交叉，只改 run / c_run，其他动作逐字节不变（fix-only-what-is-reported），再做前后对比 GIF 给用户看。
