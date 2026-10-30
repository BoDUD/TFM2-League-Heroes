# 迭嘉：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 迭嘉的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己的格子读回，1:1 定稿：**3/4 朝右、直立站着**；冰蓝水晶皮肤、深蓝紫的人字形胸甲、肩膀和前臂上古铜 / 银灰的尖刺；**古铜面甲、品红发光的眼睛、浅青蓝的大团鬃毛、头后两撮青蓝鬃冠**；**两只发光的青色水晶拳**；**背后两片收起来高高竖起的翅膀**（深紫翼骨、青到紫的扇形翼膜、锯齿边）；深紫黑的腿和黑爪；尾巴往左下方拖，尾尖一片古铜叶形尾鳍）。
> - 请你画 **21 个姿势**（普攻 2 个 + 技能 9 个 + 死亡 2 帧 + **跑步 8 帧**），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个迭嘉**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 10 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、两条腿、两只手臂、两片翅膀、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，参考图里已经放大了。他的金铲铲动作里**没有普攻**，`a_wind`、`a_punch` 两张是待机把近处那只手臂转过去做出来的（只有那只手臂和待机不一样）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 = 他的左臂，紫线 = 他的右臂**（大圆点是拳头），**红线 = 左腿，蓝线 = 右腿**，**粉线 = 左边的翅膀，青线 = 右边的翅膀**（从背上的翼根连到每一根翼骨的根部、一直到翼尖那根：翅膀就沿着这条线张开或收起），**棕线 = 尾巴**，**灰框 = 头的位置**。近处是哪只手臂，下表写了（近处的手臂、腿、翅膀用全亮的颜色，远处的暗一档）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（古铜面甲、额头小尖角、品红发光的眼睛、浅青鬃毛、头后两撮鬃冠）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；眼睛一直在。
> - **翅膀**：一直是定稿那两片（深紫翼骨、青到紫的扇形翼膜、锯齿边），**大小和定稿一样，不要变长变大**。收着的姿势照定稿竖在背后；`q_raise`、`e_beat`、`e_hop`、`r_up`、`r_fly1`、`r_fly2` 照参考图张开（扇子打开，翼膜一条条摊开）；`q_sweep`、`r_blast` 照参考图往前扫到身前。
> - **拳头**：一直是定稿那两只发光的青色水晶拳，大小不变。
> - **跑步 8 帧（`run1`–`run8`）是一整个循环**：金铲铲里他弓着身子跑，**两条腿各往前迈一次**——左腿（红线）和右腿（蓝线）在不同的帧轮流在前面，**每一帧的两条腿都照骨架摆，换腿要看得出来**；身子、头、翅膀每帧都是同一个，只跟着骨架起伏。

## 21 个姿势

| 图 | 文件 | 片段 | 近处的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `daeja-pose-a_wind.png` | idle@0 | 左（橙线） | 风弹起手：橙线那只（近处的）拳头弯起来收到胸前蓄力（照骨架） |
| 3 | `daeja-pose-a_punch.png` | idle@0 | 左（橙线） | 风弹：橙线那只（近处的）拳头平平地往前猛推出去（风弹之后单独画），紫线那只留在身边 |
| 4 | `daeja-pose-q_raise.png` | spell@0 | 右（紫线） | 罡风轰击起手：两片翅膀张开往后上方高高扬起，身子前倾蓄力 |
| 5 | `daeja-pose-q_sweep.png` | spell@250 | 右（紫线） | 罡风轰击：两片翅膀猛地往前扫到身前（冲击波之后单独画） |
| 6 | `daeja-pose-e_beat.png` | celebration@0 | 左（橙线） | 振翼退风：两片翅膀向两边完全展开猛扇一下 |
| 7 | `daeja-pose-e_hop.png` | spell@583 | 右（紫线） | 振翼退风（跳起）：借风离地，腿收起，翅膀张着 |
| 8 | `daeja-pose-r_up.png` | intro@361 | 右（紫线） | 苍穹罡风（起飞）：蹲低蓄力，翅膀向两边张开，准备飞起 |
| 9 | `daeja-pose-r_fly1.png` | celebration@0 | 左（橙线） | 苍穹罡风（飞行·平展）：翅膀平平展开（之后整体抬离地面） |
| 10 | `daeja-pose-r_fly2.png` | spell@0 | 右（紫线） | 苍穹罡风（飞行·上扬）：翅膀扬到最高（之后整体抬离地面） |
| 11 | `daeja-pose-r_blast.png` | spell@250 | 右（紫线） | 苍穹罡风（轰出）：在空中把翅膀往前扫（之后整体抬离地面） |
| 12 | `daeja-pose-r_land.png` | intro@541 | 左（橙线） | 苍穹罡风（落地）：落地蹲下，翅膀半张 |
| 13 | `daeja-pose-d_fall.png` | death@416 | 右（紫线） | 被打倒：往后一仰，身子立起来，翅膀乱扬 |
| 14 | `daeja-pose-d_down.png` | death@4166 | 右（紫线） | 倒地：跪倒在地，垂下头（金铲铲原样） |
| 15 | `daeja-pose-run1.png` | run@0 | 左（橙线） | 移动 第 1/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 16 | `daeja-pose-run2.png` | run@121 | 右（紫线） | 移动 第 2/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 17 | `daeja-pose-run3.png` | run@242 | 右（紫线） | 移动 第 3/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 18 | `daeja-pose-run4.png` | run@362 | 右（紫线） | 移动 第 4/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 19 | `daeja-pose-run5.png` | run@483 | 右（紫线） | 移动 第 5/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 20 | `daeja-pose-run6.png` | run@604 | 右（紫线） | 移动 第 6/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 21 | `daeja-pose-run7.png` | run@724 | 右（紫线） | 移动 第 7/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |
| 22 | `daeja-pose-run8.png` | run@845 | 右（紫线） | 移动 第 8/8 帧（金铲铲的跑步，一整个循环，两条腿各往前迈一次） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (his feet on y 1176) - a BLUE CRYSTAL DRAGON-MAN standing upright on two legs: ice-blue / cyan crystal skin, layered dark blue-violet chevron plates on the chest and belly, bronze / silver-grey spikes on the shoulders and forearms; a BRONZE SKULL MASK over his face with GLOWING MAGENTA EYES, a big PALE CYAN MANE hanging from the chin, two cyan crests behind the head; two GLOWING CYAN CRYSTAL FISTS; two big FOLDED WINGS rising high behind his back (dark violet spiked wing bones, cyan-to-violet fan membranes, saw-toothed edges); dark violet-black legs with black claws; a blue tail to the lower left ending in a bronze leaf-shaped FLUKE; B his HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the two arms, the two wings, the body's and the head's angle from it - never its 3D shading; its head is already enlarged to image A's); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE = his LEFT arm, PURPLE = his RIGHT arm (the big dot = the fist), RED = his LEFT leg, BLUE = his RIGHT leg, PINK = the LEFT wing and CYAN = the RIGHT wing (from the wing's root on his back through the roots of its ribs out to the tip: the wing opens or folds along that line), BROWN = the tail, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the arms and the legs as thick as in A, where C shows them. Each leg along its line, bending at its knee, never stretched, never thinner than in A. The WINGS are always image A's two at image A's size, never bigger - standing folded behind his back where C shows them folded, opened like a fan (the membrane strips spread between the ribs) where C and D open them, swept in front of him where C sweeps them. The FISTS are always image A's two glowing crystal fists. The tail along the brown line with its fluke at the end. The near side (the near arm, leg and wing) in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the bronze mask with its forehead spike, the glowing magenta eyes, the pale cyan mane, the two crests) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eyes always visible.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no wind, no air streaks, no shock wave, no bolts, no glow beyond the fists' own colour, no sparks, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND UP - the near fist on the ORANGE line bent and drawn back to his chest, gathering (as in the skeleton).`
- a_punch: `PUNCH - the near fist on the ORANGE line thrust straight out forward at chest height (the wind bolt is drawn separately later), the arm on the PURPLE line at his side.`
- q_raise: `WINGS BACK - both wings opened and raised high behind him, the body leaning forward, gathering.`
- q_sweep: `SWEEP - both wings swept hard forward in front of him (the shock wave is drawn separately later).`
- e_beat: `WINGBEAT - both wings spread fully to the sides in one hard beat.`
- e_hop: `HOP - lifted off the ground by the wind, the legs drawn up, the wings spread.`
- r_up: `TAKE OFF - crouched low, the wings spread to the sides, about to fly up.`
- r_fly1: `FLY, WINGS LEVEL - the wings spread level (lifted off the ground later).`
- r_fly2: `FLY, WINGS UP - the wings raised to the top of the beat (lifted off the ground later).`
- r_blast: `BLAST - in the air, the wings swept forward (lifted off the ground later).`
- r_land: `LAND - landed, crouched, the wings half open.`
- d_fall: `KNOCKED BACK - thrown back, the body upright, the wings flung up.`
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

- 每个姿势一张：`outputs/daeja-poses/daeja-pose-<名字>.png`（1254 × 1254、真透明背景、每格 10 px）；原始生成图原样放进 `outputs/daeja-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **21 张都画完再交**，最后写 `outputs/daeja-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/daeja_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/daeja/codex_poses/`，**先量 Codex 实际的格子**（不一定是 10 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、翅膀大小不变、腿没有被压扁或拉长、跑步 8 帧是同一个身体且换腿看得出来、远处的腿暗一档）。
- 骨架包：`tools/art/pack_daeja_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影，yaw 35；头放大 HEAD_SCALE 2.0；普攻两帧是待机把左臂按 ARM 转过去）；这份提示词由 `tools/art/gen_daeja_pose_md.py` 生成。
