# 米利欧（明烛）：跑步重画腿（给 Codex 的提示词）

> 上一轮的跑步 8 帧里，**近侧（亮色）腿一直在前、远侧（暗色）腿一直在后**，两条腿从来没有交替、也没有从身体下面互相经过，用户说「走路没有交叉步，步伐没有变化」。这一轮**只重画腿**：
> - `now/milio_run_<n>.png`：这一帧的上半身（头、手臂、上衣、裙子都画好了，**不要改**），腿已经去掉了。
> - `guide/milio_run_<n>.png`：同一张图，上面用**线**标出这一帧两条腿的位置：**红线 = 近侧腿（亮色皮肤）**，**蓝线 = 远侧腿（暗一档）**；每条线是 **髋 → 膝 → 脚踝 → 脚尖**（小圆圈是关节，实心大圆点是脚尖）。**红色横线 = 地面**（鞋底落在它上面），**蓝色叉 = 站位点**。线只是位置，**不要画进图里**。
> - 两条腿**轮流**在前：红腿第 1 帧在前方落地 → 第 2–3 帧到身体正下方 → 第 4 帧在身后蹬地 → 第 5–6 帧抬起、往后踢 → 第 7 帧屈膝从身体下面往前摆 → 第 8 帧向前伸；蓝腿一样，**比红腿晚半拍（差 4 帧）**。**第 3 帧和第 7 帧两条腿在身体下面交叉**（一条竖直撑地，另一条屈膝从它旁边往前摆过去）——这就是交叉步。
> - 腿的样子照造型和上一轮你画的腿（`ref/`）：**光着的棕色小腿（膝盖到脚踝）、脚踝上红 + 青绿的布绑腿、棕色凉鞋**，**粗细、长短每帧一样**，大腿从裙子下面伸出来（裙子挡住大腿上半）；近侧腿亮色皮肤，远侧腿暗一档；凉鞋朝右；落地的那只脚**鞋底平平地踩在红色地面线上**，抬起的脚离开地面。
> - 每格 6 × 6 px（1536×1024 里 256 × 170 格），和上一轮同一个格子；只用造型的颜色；外轮廓近黑描边约 2 格；**alpha 只能是 0 或 255**；不要抖动、渐变、半透明。
> - 交付到 `outputs/milio-run/`：`milio_run_1.png` … `milio_run_8.png`（1536×1024、透明背景，**上半身和 `now/` 那张逐格一样**，加上你画的两条腿）+ 生图原稿原样放 `raw/`（不要自己整理、不要重采样）；**最后**写 `HANDOFF.md`；最好打成 `milio_run_done.zip`。
> - 一帧一次，画后一帧时附上前一帧（让腿的粗细、长度、凉鞋大小一样）。

## 附图（每帧按这个顺序附）

1. `guide/milio_run_<n>.png`（这一帧的腿线）
2. `now/milio_run_<n>.png`（这一帧去掉腿的上半身，要保留不动）
3. `ref/milio_side_design.png`（造型：腿、绑腿、凉鞋的样子和颜色）
4. `ref/milio_leg_from_codex_run.png`（你上一轮画的腿，红框里那条：照它的粗细、绑腿、凉鞋）
5. 同一个动作的前一帧（你刚交付的那张；第 1 帧不附）

另外 `ref/caitlyn_run_reference.png` 是用户认可过的交叉步跑步（本包另一个英雄，6 倍放大），只看两条腿怎么轮流；`step2/` 是上一轮读回的跑步（要改掉的样子）。

## 提示词（每帧一次）

```text
Image 2 is the upper body of a cheerful young boy running to the right, already finished (curly dark hair, a big grin, a red tunic with golden shoulder pads, a magenta kilt) with his legs taken away, on a 1536x1024 canvas on a grid of 6x6-pixel squares. Image 1 is the same picture with THIS FRAME'S LEGS marked as lines: the RED line is his NEAR leg (the light-skinned one), the BLUE line his FAR leg (one shade darker); each line runs hip - knee - ankle - toe (small circles are the joints, the big filled dot is the toe); the red horizontal line is the ground, the blue cross the standing point. Image 3 is the character's approved design (his legs: bare brown shins, red-and-teal cloth wraps round the ankles, brown sandals). Image 4 is a leg you drew for him before (the one in the red box): copy its thickness, its wrap and its sandal. (Image 5, when attached, is the previous frame of this run: keep the legs exactly as thick and long, the sandals as big.)
Draw ONE frame: Image 2 exactly as it is - the head, arms, tunic and kilt unchanged, square for square - plus his two legs placed exactly along the lines of Image 1: <WHAT>
Rules: the same 1536x1024 transparent canvas and the same 6-pixel grid as Image 2, every square one flat colour from the design's colours; the thighs come out from under the kilt (the kilt hides their tops), the knees bend the way the lines bend, bare brown shins, the red-and-teal ankle wraps, brown sandals pointing right; the NEAR (red-line) leg in the light skin, the FAR (blue-line) leg one shade darker and drawn BEHIND the near one where they overlap; both legs as thick and as long as in Image 4 and the design, never thinner, longer or stiff like posts; a planted foot lies FLAT on the red ground line, a lifted foot is off the ground; nothing below the ground line; the same near-black outline as the design (about 2 squares); alpha only 0 or 255; no dithering, no gradients, no anti-aliasing, no semi-transparency; no lines, crosses, dots or text from Image 1, no effects, no dust, no fire spirit. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

`<WHAT>`，按帧换成：

- 1：`the NEAR (red) leg planted far ahead, its foot flat on the ground in front of him, the knee nearly straight; the FAR (blue) leg just pushed off behind, its foot lifting off the ground behind him.`
- 2：`the NEAR (red) leg on the ground under the front of his body, the knee bent as he lands on it; the FAR (blue) leg kicked up behind him, the heel rising toward his bottom, the knee bent.`
- 3：`the NEAR (red) leg straight down under his hips, its foot flat on the ground (carrying his weight); the FAR (blue) leg swinging FORWARD past it under his body, the knee bent high in front, the foot off the ground - the two legs cross under him.`
- 4：`the NEAR (red) leg behind him, pushing off the ground with the foot's front; the FAR (blue) leg reaching forward, the knee up in front, the foot just above the ground ready to land.`
- 5：`the NEAR (red) leg just pushed off behind, its foot lifting off the ground behind him; the FAR (blue) leg planted far ahead, its foot flat on the ground in front of him, the knee nearly straight.`
- 6：`the NEAR (red) leg kicked up behind him, the heel rising toward his bottom, the knee bent; the FAR (blue) leg on the ground under the front of his body, the knee bent as he lands on it.`
- 7：`the FAR (blue) leg straight down under his hips, its foot flat on the ground (carrying his weight); the NEAR (red) leg swinging FORWARD past it under his body, the knee bent high in front, the foot off the ground - the two legs cross under him, the near leg in front.`
- 8：`the NEAR (red) leg reaching forward, the knee up in front, the foot just above the ground ready to land; the FAR (blue) leg behind him, pushing off the ground with the foot's front.`

## 交回前请检查

- 8 帧都在，每张 1536×1024 透明底、6 px 一格、alpha 只有 0 / 255，`_1x` 和大图逐格一致。
- **上半身和 `now/` 逐格一样**（头、手臂、上衣、裙子不改）。
- 两条腿沿着线：红 = 近侧亮色腿，蓝 = 远侧暗色腿；**第 1–4 帧和第 5–8 帧两条腿的位置对调**；**第 3、7 帧两条腿在身体下面交叉**。
- 腿的粗细、长短、绑腿、凉鞋每帧一样（照 `ref/`）；落地的脚平踩在地面线上，地面线以下没有东西；没有线、叉、点、文字、特效。
- 全部画完后最后写 `outputs/milio-run/HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 读原稿（raw/），按 import_milio_strips 的办法量比例、切到设计格子；**只取 Codex 的腿**（裙摆下沿以下 + 裙子外面的腿），贴回 `now/` 那一帧的上半身（同一张脸、同样的手臂），腿和裙摆接缝查缝隙（gap-check）；8 帧顺序就是这个顺序（不再换深浅）；逐帧 8 倍自查腿是否变形、粗细一致、两腿交替交叉，再做 GIF 给用户看。
