# 迅捷蟹：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 迅捷蟹的造型用户已经定稿：`0_design.png` 是你第 0 步画的 **A 原稿**（`raw/scuttle-A-original.png`），按它自己 8 px 的格子读回，1:1 定稿（120 × 80 格），这里放大成每格 8 px。3/4 朝右，**背着一大块青绿色叠片甲壳的河蟹**：甲片一片片往后叠，边缘柠檬黄绿，后沿一排黄绿尖刺；正前方一块**灰色石头面甲**；面甲两边**两只发光的柠檬黄绿眼睛**（短眼柄）；**两根一节一节的深青长触角**往后弯，末端黄绿弯钩；甲壳下面一圈**深青色尖叶形的短腿和小钳子**。每个姿势都照它画。
> - **你上一轮自己缩的 46 × 32 小图这次不用**（太糊）。这一轮全部照 `0_design.png` 的格子和大小画。
> - 请你画 **20 个姿势**：3 帧普攻、2 帧技能1、3 帧技能2、3 帧大招、8 帧跑步、1 帧死亡，**每个姿势一张图**。待机和挨打我直接用定稿做，不用画。
> - **每张都是同一只迅捷蟹**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 8 px**。画布 **1254 × 1254**，红线是地面（**最低点 y = 1100**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：站高、跳起、缩壳的时候，画面会变高、变宽或变矮，**但甲壳、面甲、眼睛、腿都不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**甲壳每张都和定稿一样大。**
> - **参考图（每个姿势一张 `*_ref.png`）是它自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都对好了，脸已经放大了一些。**姿势照参考图**：腿、钳子、触角、甲壳的角度。**长相和画法照定稿**：像素格、描边、平涂，不要 3D 光影。模型的脸比定稿小，**脸、甲片和腿的大小照定稿**。
> - **跳在空中的姿势（a_hop）也把最低点画在红线上**，离地的高度我自己加。**例外：`r_up1`、`r_up2` 是从土里钻出来，红线以下在地下，红线以下的部分不画**（从红线处整齐切掉）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 身体（甲壳中心）；**黄线 / 橙线 = 两根触角**
>   - **粉线 / 青线 = 两只钳子**；**红线 = 一边三条腿，蓝线 = 另一边三条腿**
>   - **灰框 = 脸在哪里**（石头面甲和两只眼睛）
>   - **蓝线的腿和青线的钳子是靠我们这一侧的**：颜色正常。红线的腿和粉线的钳子在另一侧，暗一档。哪个在上面挡住哪个，照参考图。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **脸一格一格照 `1_head.png` 画，大小和定稿一样（每格 8 px，不缩放），脸的中心对准灰框的中心**（灰色石头面甲和裂纹、两只发光眼睛和眼柄）。每个姿势都是这一张脸，只跟着身体移动和倾斜，**不要转方向、不要重新设计**。例外：
>   - `e_shell` 缩进壳里，脸、腿、钳子都看不见，只剩甲壳（触角也收进去）
>   - `d_down` 缩在壳里，只有两根触角软软地瘫在地上，眼睛暗下去（看不见或变成暗绿）
> - **腿和钳子**：一直是定稿那些深青色尖叶形的短腿和小钳子，**照骨架的线弯折**。不要拉长、不要变细。**触角**：一直是定稿那两根一节一节的深青长条，末端黄绿弯钩，照黄线 / 橙线的形状弯。
> - **跑步 8 帧（run1–run8）是一整圈**：甲壳、脸、触角每帧都是同一个，只有腿按骨架换位置，甲壳跟着一颠一颠。**一定要看得出腿在飞快地倒腾。**
> - **不画任何特效**：舞蹈的冲击、神龛的水纹、护盾的光、钻地的土，之后单独画。

## 20 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `scuttle-pose-a_rise.png` | dance@913 | 普攻「螃蟹舞」起手：用腿撑着整个站高，两只小钳子高高举起，触角竖直 |
| 3 | `scuttle-pose-a_hop.png` | dance@1370 | 跳：一蹦跳离地面，腿在身下收起来，钳子往两边摆（舞步） |
| 4 | `scuttle-pose-a_stomp.png` | dance@685 | 落地踩：重重落回地面，身子压低，腿往外撑开（这一下打到身边一圈的敌人） |
| 5 | `scuttle-pose-q_raise.png` | idle_up@500 | 技能1「疾行神龛」起手：身子挺起来，两根触角往上举 |
| 6 | `scuttle-pose-q_call.png` | idle_up@913 | 召唤神龛：两根触角高高竖直、黄绿尖朝天，像在召唤什么（地上的神龛之后单独画） |
| 7 | `scuttle-pose-e_tuck.png` | tuck@266 | 技能2「蟹壳护盾」起手：触角和腿往回收，身子往下缩 |
| 8 | `scuttle-pose-e_shell.png` | shell@0 | 缩进壳里：腿、钳子、脸和触角全缩进甲壳，只剩一个圆鼓鼓的甲壳趴在地上（护盾的光之后单独画） |
| 9 | `scuttle-pose-e_pop.png` | pop@79 | 弹出来：从壳里一下弹出，腿伸开，触角甩起来 |
| 10 | `scuttle-pose-r_up1.png` | rise@699 | 大招「你挖得动吗？」钻出地面 1：甲壳和脸从土里拱出来一半（红线以下在地下，不画），触角往两边甩 |
| 11 | `scuttle-pose-r_up2.png` | rise@932 | 钻出地面 2：整只蟹从土里蹦出来，腿还垂在身下 |
| 12 | `scuttle-pose-r_up3.png` | rise@1165 | 钻出地面 3：整只蟹落回地面，腿撑开站稳，触角往后甩（之后接回待机） |
| 13 | `scuttle-pose-run1.png` | run@0 | 跑 1：小短腿飞快地倒腾（一圈 8 帧里的第 1 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 14 | `scuttle-pose-run2.png` | run@66 | 跑 2：小短腿飞快地倒腾（一圈 8 帧里的第 2 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 15 | `scuttle-pose-run3.png` | run@133 | 跑 3：小短腿飞快地倒腾（一圈 8 帧里的第 3 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 16 | `scuttle-pose-run4.png` | run@199 | 跑 4：小短腿飞快地倒腾（一圈 8 帧里的第 4 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 17 | `scuttle-pose-run5.png` | run@265 | 跑 5：小短腿飞快地倒腾（一圈 8 帧里的第 5 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 18 | `scuttle-pose-run6.png` | run@331 | 跑 6：小短腿飞快地倒腾（一圈 8 帧里的第 6 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 19 | `scuttle-pose-run7.png` | run@398 | 跑 7：小短腿飞快地倒腾（一圈 8 帧里的第 7 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠 |
| 20 | `scuttle-pose-run8.png` | run@464 | 跑 8：小短腿飞快地倒腾（一圈 8 帧里的第 8 帧，左右两边的腿轮流抬起落下），甲壳跟着一颠一颠；8 接回 1，循环 |
| 21 | `scuttle-pose-d_down.png` | shell@0 | 死亡：缩进壳里不动，两根触角软软地瘫在地上，眼睛暗下去 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（脸）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 8 px squares (its lowest leg tips on y 1100) - a round RIVER CRAB under a BIG TEAL-GREEN SHELL of overlapping plates (lime-yellow plate edges, a row of lime spikes along the rear rim), a GREY STONE FACE PLATE at the front, TWO GLOWING LIME EYES on short dark stalks at its sides, TWO LONG SEGMENTED DARK TEAL ANTENNAE curving back over the shell with lime hooked tips, and a ring of SHORT DARK TEAL LEAF-SHAPED LEGS and two small claws under the shell; B its FACE (the stone face plate and the two eyes) shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE - the legs, the claws, the antennae and the shell's angle - from it, never its 3D shading; the model's face is smaller than A's: keep A's face and bulk); D the SKELETON of that pose, exactly over C: green = the body (the shell's centre), YELLOW and ORANGE = its two antennae, PINK and CYAN = its two claws, RED = the three legs of one side, BLUE = the three legs of the other side, GREY BOX = where the face is, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 8 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1100 (also when it is in the air), unless the pose says it is climbing out of the earth.
THE SAME BULK AS IMAGE A: the shell, the face, the legs and the claws exactly as big as in A in EVERY pose, also when it stands up tall, hops or pulls into its shell (the picture simply grows taller, wider or shorter - never shrink the shell to fit). Each leg and claw along its line (dark teal pointed leaf-shaped plates), never stretched, never thinner than in A; each antenna along its line (a segmented dark teal strip with a lime hooked tip). The BLUE legs and the CYAN claw are on the side nearer to us: full tone; the RED legs and the PINK claw are on the far side: a step darker; which one overlaps which as in image C.
THE FACE: copy image B SQUARE FOR SQUARE at image A's size (never scaled), centred on the grey box (the grey stone face plate with its cracks, the two glowing lime eyes on their stalks) - the same face in every pose, only moved and tilted with the body, never turned, never redrawn; the face changes only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no shockwave, no water ring, no shield glow, no dirt or dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_rise: `UP ON ITS LEGS - standing up tall on all its legs, both little claws raised high, the antennae straight up.`
- a_hop: `HOP - bounced off the ground, the legs tucked under it, the claws swinging out to the sides (a dance step).`
- a_stomp: `STOMP - landing back hard, the body pressed low, the legs splayed out (this beat strikes everyone round it).`
- q_raise: `RISE - the body lifting up, both antennae swinging upward.`
- q_call: `CALL - both antennae raised straight up, the lime tips to the sky, as if calling something up (the shrine on the ground is drawn later, NOT here).`
- e_tuck: `TUCK - the antennae and the legs pulling in, the body sinking down.`
- e_shell: `IN ITS SHELL - legs, claws, face and antennae all pulled in: only the round plated shell sitting on the ground (the shield's glow is drawn later, NOT here).`
- e_pop: `POP OUT - springing back out of the shell, the legs out, the antennae flicking up.`
- r_up1: `BURST OUT 1 - the shell and the face pushing half out of the earth (what is under the red line is underground: do NOT draw it), the antennae flung out to the sides.`
- r_up2: `BURST OUT 2 - the whole crab springing out of the earth, the legs still dangling under it.`
- r_up3: `BURST OUT 3 - the whole crab landing back on the ground, the legs spread wide to stand firm, the antennae swinging back (then it runs on into its idle).`
- run1: `SCUTTLE 1 - the short legs pattering fast (frame 1 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run2: `SCUTTLE 2 - the short legs pattering fast (frame 2 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run3: `SCUTTLE 3 - the short legs pattering fast (frame 3 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run4: `SCUTTLE 4 - the short legs pattering fast (frame 4 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run5: `SCUTTLE 5 - the short legs pattering fast (frame 5 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run6: `SCUTTLE 6 - the short legs pattering fast (frame 6 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run7: `SCUTTLE 7 - the short legs pattering fast (frame 7 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them.`
- run8: `SCUTTLE 8 - the short legs pattering fast (frame 8 of an 8-frame cycle: the legs of each side lifting and setting down in turn, as in its reference), the shell bobbing with them. 8 runs on into 1: the loop.`
- d_down: `DEAD - curled up in its shell and still, the two antennae lying limp on the ground, the eyes dark.`

## 交回

- 每个姿势一张：`outputs/scuttle-poses/scuttle-pose-<名字>.png`（1254 × 1254、真透明背景、每格 8 px）。
- 原始生成图原样放进 `outputs/scuttle-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**，原图我自己按格子读。
- **20 张都画完再交**。最后写 `outputs/scuttle-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/scuttle_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/scuttlecrab/codex_poses/`，**先量 Codex 实际的格子**（不一定是 8 px），读 raw。
- **每张按定稿的身体大小读**：站高、跳起时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。脸对齐定稿的脸（hd/idle.png）。
- 每帧 8 倍检查：脸不动、两只眼睛还在、甲壳和定稿一样大、腿没有被压扁或拉长、跑步 8 帧腿真的在换、远处的腿暗一档、r_up1 / r_up2 在红线处切齐。
- 骨架包由 `tools/art/pack_scuttlecrab_poses.py` 生成：骨架是英雄联盟河蟹的骨骼（金铲铲的模型用同一套），按动作片段的那一帧投影；脸放大 1.4 倍；跑步取一整圈 8 帧 (0, 66, 133, 199, 265, 331, 398, 464) ms。这份提示词由 `tools/art/gen_scuttlecrab_pose_md.py` 生成。
