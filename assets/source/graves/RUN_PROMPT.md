# 法外狂徒 格雷福斯：跑步重画腿（给 Codex 的提示词）

> 格雷福斯的移动要做成**跑步**（用户：「男枪应该是跑步吧？而且要确保跑步时腿部不变形」）。上半身用定稿不动，这一轮**只画腿**（用 image_gen 画，不要用脚本），一共 8 帧：
> - `now/graves_run_<n>.png`：这一帧的上半身（头、深红围巾、护肩、手臂、霰弹枪都画好了，**不要改**），**皮带以下的腿已经去掉了**。
> - `guide/graves_run_<n>.png`：同一张图，上面用**线**标出这一帧两条腿的位置：**红线 = 近侧腿（颜色亮、在前）**，**蓝线 = 远侧腿（暗一档、在后）**；每条线是 **髋 → 膝 → 脚踝 → 脚尖**（小圆圈是关节，实心大圆点是靴尖）。**红色横线 = 地面**（鞋底落在它上面），**蓝色叉 = 站位点**。线只是位置，**不要画进图里**。
> - 两条腿**轮流**在前：红腿第 1 帧在前方落地 → 第 2–3 帧到身体正下方 → 第 4 帧在身后蹬地 → 第 5–6 帧抬起、往后踢 → 第 7 帧屈膝从身体下面往前摆 → 第 8 帧向前伸；蓝腿一样，**比红腿晚半拍（差 4 帧）**。**第 1–4 帧和第 5–8 帧两条腿前后对调**；**第 3 帧和第 7 帧两条腿在身体下面交叉**（一条撑地，另一条屈膝从它旁边往前摆过去）——这就是交叉步。
> - 腿的样子照造型（`ref/graves_side_design.png`）：**从皮带下面开始画卡其色的宽松裤子**（大腿，带深一档的褶），**膝盖上卡其色的护膝**，**小腿是深灰色的裤管，堆在棕色的靴子上**；**粗细、长短每帧一样**，和造型一样敦实（不要画细、画长、画成木棍）；近侧腿全亮色，远侧腿暗一档、和近侧腿重叠的地方画在它后面；靴子朝右；落地的那只脚**鞋底平平地踩在红色地面线上**，抬起的脚离开地面。
> - 每格 16 × 16 px（1254×1254 的画布上），和上半身同一个格子；只用造型的颜色；外轮廓 1 格的近黑描边；**alpha 只能是 0 或 255**；不要抖动、渐变、半透明。
> - 交付到 `outputs/graves-run/`：`graves_run_1.png` … `graves_run_8.png`（1254×1254、透明背景，**上半身和 `now/` 那张一样**，加上你画的两条腿）+ 生图原稿原样放 `raw/`（不要自己整理、不要重采样）；**最后**写 `HANDOFF.md`，再打包成 `outputs/graves_run_done.zip`。
> - 一帧一次，画后一帧时附上前一帧（让腿的粗细、长度、靴子大小一样）。中间不要停，8 帧都画完再交。

## 附图（每帧按这个顺序附）

1. `guide/graves_run_<n>.png`（这一帧的腿线）
2. `now/graves_run_<n>.png`（这一帧去掉腿的上半身，要保留不动）
3. `ref/graves_side_design.png`（定稿的侧面：腿、护膝、靴子的样子和颜色）
4. 前一帧（你刚交付的那张；第 1 帧不附）
5. `ref/jayce_run_reference.png`（本包的杰斯，用户认可过的交叉步跑步，6 倍放大：只看两条腿怎么轮流、多粗）
6. `ref/caitlyn_run_reference.png`（本包的凯特琳，同上，只看腿）

## 提示词（每帧一次，用 image_gen）

```text
Image 2 is the upper body of a burly gunslinger running to the right, already finished (slicked-back black hair, a full black beard, a ragged crimson scarf trailing behind, a big gold-trimmed brown leather pauldron, a huge straight gold-and-black double-barrelled shotgun held level at the hip with both hands) with his legs taken away below the belt, on a 1254x1254 canvas on a grid of 16x16-pixel squares. Image 1 is the same picture with THIS FRAME'S LEGS marked as lines: the RED line is his NEAR leg (full tone, in front), the BLUE line his FAR leg (one shade darker, behind); each line runs hip - knee - ankle - toe (small circles are the joints, the big filled dot is the boot's toe); the red horizontal line is the ground, the blue cross the standing point. Image 3 is the character's approved design (his legs: loose khaki trousers with darker creases on the thighs, khaki knee pads, the shins in loose dark grey trouser legs bunched over brown boots). (Image 4, when attached, is the previous frame of this run: keep the legs exactly as thick and long, the boots as big.) Images 5 and 6 show how other characters' legs take turns in a cross-step run (only the leg motion and thickness).
Draw with the image generator ONE frame: Image 2 exactly as it is - the head, scarf, pauldron, arms and shotgun unchanged - plus his two legs placed exactly along the lines of Image 1: <WHAT>
Rules: the same 1254x1254 transparent canvas and the same 16-pixel grid as Image 2, every square one flat colour from the design's colours; the trousers start right under the belt; the knees bend the way the lines bend; the khaki knee pads on the knees, the brown boots pointing right; the NEAR (red-line) leg in full tone, the FAR (blue-line) leg one shade darker and drawn BEHIND the near one where they overlap; both legs as thick and as long as in the design, never thinner, longer or stiff like posts; a planted foot lies FLAT on the red ground line, a lifted foot is off the ground; nothing below the ground line; the same 1-square near-black outline as the design; alpha only 0 or 255; no dithering, no gradients, no anti-aliasing, no semi-transparency; no lines, crosses, dots or text from Image 1, no effects, no dust.
```

`<WHAT>`，按帧换成：

- 1：`the NEAR (red) leg planted far ahead, its boot flat on the ground in front of him, the knee a little bent; the FAR (blue) leg just pushed off behind, its boot lifting off the ground behind him, the heel up.`
- 2：`the NEAR (red) leg on the ground under the front of his body, the knee bent as he lands on it; the FAR (blue) leg kicked up behind him, the heel rising, the knee bent.`
- 3：`the NEAR (red) leg under his hips, its boot flat on the ground (carrying his weight); the FAR (blue) leg swinging FORWARD past it under his body, the knee bent high in front, the boot off the ground - the two legs cross under him.`
- 4：`the NEAR (red) leg behind him, pushing off the ground with the boot's front; the FAR (blue) leg reaching forward, the knee up in front, the boot just above the ground ready to land.`
- 5：`the NEAR (red) leg just pushed off behind, its boot lifting off the ground behind him, the heel up; the FAR (blue) leg planted far ahead, its boot flat on the ground in front of him, the knee a little bent.`
- 6：`the NEAR (red) leg kicked up behind him, the heel rising, the knee bent; the FAR (blue) leg on the ground under the front of his body, the knee bent as he lands on it.`
- 7：`the FAR (blue) leg under his hips, its boot flat on the ground (carrying his weight); the NEAR (red) leg swinging FORWARD past it under his body, the knee bent high in front, the boot off the ground - the two legs cross under him, the near leg in front.`
- 8：`the NEAR (red) leg reaching forward, the knee up in front, the boot just above the ground ready to land; the FAR (blue) leg behind him, pushing off the ground with the boot's front.`

## 交回前请检查

- 8 帧都在，每张 1254×1254 透明底、16 px 一格、alpha 只有 0 / 255；都是 image_gen 画的。
- **上半身和 `now/` 一样**（头、围巾、护肩、手臂、霰弹枪不改）。
- 两条腿沿着线：红 = 近侧亮色腿，蓝 = 远侧暗色腿；**第 1–4 帧和第 5–8 帧两条腿的位置对调**；**第 3、7 帧两条腿在身体下面交叉**。
- 腿的粗细、长短、护膝、靴子每帧一样（照造型，敦实，不细不长）；落地的脚平踩在地面线上，地面线以下没有东西；没有线、叉、点、文字、特效。
- 全部画完后最后写 `outputs/graves-run/HANDOFF.md`，再打包成 `outputs/graves_run_done.zip`。

## Claude 收到后（给 Claude 看）

- 读原稿（raw/），量格子、读回到设计格子；**只取 Codex 的腿**（皮带以下），贴回 `now/` 那一帧的上半身（定稿的上半身逐格不变），腿和皮带的接缝查缝隙（gap-check）；逐帧 8 倍自查腿是否变形、粗细和定稿一致、两腿交替交叉、靴子平踩地面，只改 run，其他动作逐字节不变（fix-only-what-is-reported），再做合成 GIF 给用户看。
