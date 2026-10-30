# 石傲玉：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 石傲玉的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，按它自己的格子读回、缩到游戏大小：**侧身朝右、直立站着**；翡翠青绿的玉石皮肤，**浅玉色的大胡子**，胡子下面**金边的深青人字胸甲**；**深紫水晶肩甲**、前臂上的紫刺；**青绿眉盔、橙黄发光的眼睛、两根金角、紫色额角、古铜口鼻**；**珊瑚橙的爪子**；**背后两片收起来高高竖起的翅膀**（深紫翼骨、金到玫瑰色的翼膜、青蓝翼刺）；深藏青的反关节腿和黑爪；深紫尾巴往左下方拖，尾尖一片带刺的叶形尾鳍）。
> - 请你画 **20 个姿势**（普攻 6 个 + 技能 4 个 + 死亡 2 帧 + **跑步 8 帧**），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个石傲玉**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 8 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两条腿、两只手臂、两片翅膀、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，参考图里已经放大了。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 = 他的左臂，紫线 = 他的右臂**（大圆点是爪子），**红线 = 左腿，蓝线 = 右腿**，**粉线 = 左边的翅膀，青线 = 右边的翅膀**（从背上的翼根连到每一根翼骨的根部、一直到翼尖那根：翅膀就沿着这条线张开或收起），**棕线 = 尾巴**，**灰框 = 头的位置**。近处是哪只手臂，下表写了（近处的手臂、腿、翅膀用全亮的颜色，远处的暗一档）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（青绿眉盔、紫色额角、两根金角、橙黄发光的眼睛、古铜口鼻、胡子的上沿）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；眼睛一直在。
> - **翅膀**：一直是定稿那两片（深紫翼骨、金到玫瑰色的翼膜、青蓝翼刺），**大小和定稿一样，不要变长变大**。收着的姿势照定稿竖在背后；`r_roar` 照参考图向两边完全张开（翼膜一条条摊开）；扑倒、砸地的姿势照参考图贴在背上往后倒。
> - **爪子**：一直是定稿那两只珊瑚橙的爪子，大小不变；普攻是爪击（爪子张开），`q_dash`、`e_slam` 是握拳。
> - **跑步 8 帧（`run1`–`run8`）是一整个循环**：金铲铲里他弓着身子跑，**两条腿各往前迈一次**——左腿（红线）和右腿（蓝线）在不同的帧轮流在前面（`run4` 和 `run8` 是两腿交错经过的那一帧），**每一帧的两条腿都照骨架摆，换腿要看得出来**；身子、头、翅膀每帧都是同一个，只跟着骨架起伏。

## 20 个姿势

| 图 | 文件 | 片段 | 近处的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `shiohyu-pose-a1_wind.png` | attack1@200 | 左（橙线） | 龙爪第一下起手：身子压低，一只爪子收在身后蓄力（照骨架） |
| 3 | `shiohyu-pose-a1_hit.png` | attack1@300 | 右（紫线） | 龙爪第一下：往前低低扑出，爪子横扫过去（爪痕之后单独画） |
| 4 | `shiohyu-pose-a2_wind.png` | attack2@300 | 右（紫线） | 龙爪第二下起手：身子挺起往后仰，另一只爪子高高扬起 |
| 5 | `shiohyu-pose-a2_hit.png` | attack2@400 | 左（橙线） | 龙爪第二下：身子压下去，爪子往前下方劈下 |
| 6 | `shiohyu-pose-a3_wind.png` | attack3@200 | 左（橙线） | 龙爪第三下起手：两腿下蹲，身子缩起来蓄力 |
| 7 | `shiohyu-pose-a3_hit.png` | attack3@400 | 左（橙线） | 龙爪第三下（重击）：整个人往前长长地扑出去，爪子伸到最远 |
| 8 | `shiohyu-pose-q_dash.png` | crit@400 | 右（紫线） | 玉拳连打（扑到）：贴地往前猛扑，双拳伸在身前 |
| 9 | `shiohyu-pose-e_slam.png` | roll@449 | 右（紫线） | 震地：整个人砸下去趴到地上，拳头砸进地面（裂地和碎石之后单独画） |
| 10 | `shiohyu-pose-r_roar.png` | celebration@449 | 右（紫线） | 玉龙形态（开启）：两片翅膀向两边完全展开，一条手臂往前伸，仰头咆哮（玉光之后单独画） |
| 11 | `shiohyu-pose-r_wave.png` | crit@500 | 右（紫线） | 玉龙形态第三击：往前深深压低猛扑，双爪推出一道冲击波（冲击波之后单独画） |
| 12 | `shiohyu-pose-d_fall.png` | death@300 | 右（紫线） | 被打倒：往后一仰，手臂和尾巴乱扬 |
| 13 | `shiohyu-pose-d_down.png` | death@4166 | 右（紫线） | 倒地：跪倒在地，垂下头（金铲铲原样） |
| 14 | `shiohyu-pose-run1.png` | run@0 | 右（紫线） | 移动 第 1/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 15 | `shiohyu-pose-run2.png` | run@120 | 右（紫线） | 移动 第 2/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 16 | `shiohyu-pose-run3.png` | run@220 | 右（紫线） | 移动 第 3/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 17 | `shiohyu-pose-run4.png` | run@320 | 右（紫线） | 移动 第 4/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 18 | `shiohyu-pose-run5.png` | run@440 | 右（紫线） | 移动 第 5/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 19 | `shiohyu-pose-run6.png` | run@560 | 右（紫线） | 移动 第 6/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 20 | `shiohyu-pose-run7.png` | run@670 | 右（紫线） | 移动 第 7/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 21 | `shiohyu-pose-run8.png` | run@780 | 右（紫线） | 移动 第 8/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, turned near side-on facing right, on a 1254x1254 canvas with 8 px squares (his feet on y 1176) - a JADE DRAGON-MAN MARTIAL ARTIST standing upright on two legs: jade-green / teal crystal skin, a big PALE JADE BEARD over his neck and upper chest, dark teal chevron chest plates with thin gold edges below it, DARK PURPLE CRYSTAL PAULDRONS and purple spikes on the forearms; a TEAL BROW HELMET with a PURPLE FOREHEAD HORN, TWO CURVED GOLD HORNS, a bronze muzzle with GLOWING ORANGE-YELLOW EYES; CORAL-ORANGE CLAWS; two tall FOLDED WINGS rising behind his back (dark purple wing bones, gold-to-rose membranes, teal-blue spines along their edges); dark navy digitigrade legs with black claws; a dark purple tail to the lower left ending in a spiked leaf-shaped FLUKE; B his HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the two arms, the two wings, the body's and the head's angle from it - never its 3D shading; its head is already enlarged to image A's); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE = his LEFT arm, PURPLE = his RIGHT arm (the big dot = the claw), RED = his LEFT leg, BLUE = his RIGHT leg, PINK = the LEFT wing and CYAN = the RIGHT wing (from the wing's root on his back through the roots of its ribs out to the tip: the wing opens or folds along that line), BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 8 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the arms and the legs as thick as in A, where C shows them. Each leg along its line, bending at its knee, never stretched, never thinner than in A. The WINGS are always image A's two at image A's size, never bigger - standing folded behind his back where C shows them folded, spread wide (the membrane strips opened between the ribs) where C and D open them, laid back along his back where C lays them back. The CLAWS are always image A's two coral-orange claws, open in the claw strikes, clenched as fists where the pose says punch or slam. The tail along the brown line with its fluke at the end. The near side (the near arm, leg and wing) in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the teal brow helmet with its purple forehead horn, the two gold horns, the glowing orange-yellow eye, the bronze muzzle, the top of the jade beard) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eyes always visible.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no claw trails, no shock wave, no jade glow, no rocks, no cracks, no sparks, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a1_wind: `CLAW 1 WIND UP - crouched, one claw drawn back behind him, gathering (as in the skeleton).`
- a1_hit: `CLAW 1 STRIKE - lunging low and forward, the claw sweeping across (the claw trail is drawn separately later).`
- a2_wind: `CLAW 2 WIND UP - rearing up and back, the other claw raised high.`
- a2_hit: `CLAW 2 STRIKE - dropping down, the claw slashing forward and down.`
- a3_wind: `CLAW 3 WIND UP - legs bent low, the body coiled, gathering.`
- a3_hit: `CLAW 3 HEAVY STRIKE - the whole body lunging far forward, the claw reaching as far as it goes.`
- q_dash: `POUNCE - a low lunge forward along the ground, both fists out in front.`
- e_slam: `SLAM - thrown down flat, the fist smashed into the ground (the crack and the rocks are drawn separately later).`
- r_roar: `JADE FORM - both wings spread fully to the sides, one arm reaching forward, roaring (the jade glow is drawn separately later).`
- r_wave: `THIRD BLOW - a deep low lunge, both claws thrust forward to send out the wave (the wave is drawn separately later).`
- d_fall: `KNOCKED BACK - thrown back, the arms and the tail flung up.`
- d_down: `DOWN - fallen to his knees, the head hanging (as in TFT).`
- run1: `RUN frame 1 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run2: `RUN frame 2 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run3: `RUN frame 3 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run4: `RUN frame 4 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run5: `RUN frame 5 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run6: `RUN frame 6 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run7: `RUN frame 7 of 8 (TFT's run, one whole cycle: each leg swings forward once).`
- run8: `RUN frame 8 of 8 (TFT's run, one whole cycle: each leg swings forward once).`

## 交回

- 每个姿势一张：`outputs/shiohyu-poses/shiohyu-pose-<名字>.png`（1254 × 1254、真透明背景、每格 8 px）；原始生成图原样放进 `outputs/shiohyu-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **20 张都画完再交**，最后写 `outputs/shiohyu-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/shiohyu_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/shiohyu/codex_poses/`，**先量 Codex 实际的格子**（不一定是 8 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、翅膀和金角大小不变、腿没有被压扁或拉长、跑步 8 帧是同一个身体且换腿看得出来、远处的腿暗一档）。
- 骨架包：`tools/art/pack_shiohyu_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影，yaw 80；头放大 HEAD_SCALE 2.5；跑步是一整个 0.97 秒的循环，两次交错在 run4 / run8）；这份提示词由 `tools/art/gen_shiohyu_pose_md.py` 生成。
