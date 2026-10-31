# 呲呲：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 呲呲的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己 17 px 的格子读回，1:1 定稿，这里放大成每格 10 px：3/4 朝右，**两条腿站得笔直的小迅猛龙**；圆圆的橙褐色脑袋，头顶玫红尖刺，脸周围一圈黑色尖片，**半闭的大紫眼**；**喉咙到肚子一整块紫色围兜**；**脖子两侧垂着玫红长羽毛**；背上洋红马鞍（金边、金环、钢蓝小钩，没有骑手）；橙褐色的身子和腿，脚踝紫色绑带，黑色大弯爪；尾巴在左后方，上面一排粉色尖鳍）。每个姿势都照它。
> - 请你画 **22 个姿势**（12 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个呲呲**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 10 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。**在空中的姿势（q_flip、q_kick、r_spring、r_open）也画在地面线上**，游戏里我再抬高。
> - **身体大小每张都和定稿一样**：腿踢起来、羽毛张开、身子蜷成球的时候，画面会变宽变矮，**但身子、头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置，头已经放大了一些——**姿势、两条腿、尾巴、羽毛、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**红线 / 蓝线 = 两条腿（蓝线是近处的那条）**，**棕线 = 尾巴**，**粉线 / 青线 = 脖子两侧的玫红长羽毛（青线是近处的）**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（玫红尖刺、黑色尖片、半闭的紫眼、嘴线）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**只有嘴可以变**：`q_kick`、`r_open` 张大（嘴里深蓝色，露几颗白牙）；`d_down` 眼睛闭上；别的眼睛不动。
> - **腿**：一直是定稿那两条腿（橙褐色大腿、紫色脚踝绑带、黑色三趾大爪），**照骨架的红线 / 蓝线弯折**，不要拉长、不要压扁、不要比定稿细；**近处（蓝线）的腿颜色正常、画在上面，远处（红线）的腿暗一档**。
> - **羽毛球（e_ball、d_down）**：整个身子缩成一个圆球，外面是玫红长羽毛一缕一缕包着，露出一点马鞍金边和爪子；球的大小照参考图，**不要比定稿的身子小**。
> - **跑步 8 帧（run1–run8）是一整圈**：两条腿各在前面一次，run3 和 run7 是两腿交错的那一帧；**每帧的身子、头、尾巴都是同一个**（身子前倾、尾巴往后伸直），只有两条腿按骨架换位置。**一定要看得出两条腿在前后交换**：近处（蓝）的腿正常颜色、远处（红）的腿暗一档。

## 22 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `zippy-pose-a_wind.png` | celebration@633 | 普攻「利爪踢」起手：一条腿高高抬起、膝盖往前收，另一条腿站稳 |
| 3 | `zippy-pose-a_kick.png` | death@916 | 踢出：抬起的那条腿往前猛地蹬直，大爪朝前，身子和头往后仰（脸还是定稿那张，只是跟着往后倾） |
| 4 | `zippy-pose-q_crouch.png` | attack@64 | 技能1「后空翻踢」起手：身子压低、两腿弯曲蓄力，头往后仰 |
| 5 | `zippy-pose-q_flip.png` | attack@258 | 后空翻：身子往后翻，一条腿高高踢过头顶（画在地面线上，游戏里会抬高） |
| 6 | `zippy-pose-q_kick.png` | attack@387 | 踢中：翻到一半，两只脚往前上方踢出去，头在后下方 |
| 7 | `zippy-pose-q_land.png` | attack@516 | 落地：两脚落回地上，身子蹲低，头抬起来 |
| 8 | `zippy-pose-e_curl.png` | leap@670 | 技能2「翻滚冲锋」起手：身子蜷起来，两侧的玫红长羽毛往身前包，快要缩成一个球 |
| 9 | `zippy-pose-e_ball.png` | spell@0 | 羽毛球：整个身子缩成一个圆球，外面是玫红长羽毛包着，露出一点马鞍和爪子（游戏里会让它转起来滚） |
| 10 | `zippy-pose-r_crouch.png` | leap@95 | 大招「翻滚突袭」起手：身子压低，两腿深蹲蓄力准备起跳 |
| 11 | `zippy-pose-r_spring.png` | leap@574 | 跃起：腾空往上跳，两腿收在身下，两侧的玫红长羽毛像翅膀一样张开（画在地面线上，游戏里会抬高） |
| 12 | `zippy-pose-r_open.png` | curl@412 | 空中张开：从球里一下张开，羽毛像翅膀一样大张，嘴张大，两腿往下伸准备砸下去 |
| 13 | `zippy-pose-r_land.png` | curl@962 | 砸地落下：两腿着地、身子蹲低前倾，羽毛往后扬 |
| 14 | `zippy-pose-run1.png` | run@0 | 跑 1：身子前倾平伸，尾巴往后伸直；近处（蓝）的腿在前、远处（红）的腿在后 |
| 15 | `zippy-pose-run2.png` | run@120 | 跑 2：近处的腿伸到最前 |
| 16 | `zippy-pose-run3.png` | run@260 | 跑 3：两腿交错（近处的腿踩地往后蹬，远处的腿抬起往前收） |
| 17 | `zippy-pose-run4.png` | run@360 | 跑 4：远处的腿到前面 |
| 18 | `zippy-pose-run5.png` | run@480 | 跑 5：远处的腿伸到最前 |
| 19 | `zippy-pose-run6.png` | run@560 | 跑 6：远处的腿落地 |
| 20 | `zippy-pose-run7.png` | run@660 | 跑 7：两腿交错（远处的腿往后蹬，近处的腿往前收） |
| 21 | `zippy-pose-run8.png` | run@740 | 跑 8：近处的腿回到前面（8 接回 1，循环） |
| 22 | `zippy-pose-d_fall.png` | death@1166 | 被打倒：一条腿站着摇晃，身子往后仰，头往后甩（脸还是定稿那张，跟着往后倾） |
| 23 | `zippy-pose-d_down.png` | leap@862 | 倒地：缩成一个羽毛球躺在地上不动，眼睛闭上（画成 X 或一条线） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (its soles on y 1176) - a small BIPEDAL RAPTOR standing upright on two legs: a ROUND ORANGE-BROWN HEAD with HOT-PINK SPIKES on top, a frill of BLACK SHARDS round the face, BIG HALF-CLOSED PURPLE EYES; one DEEP PURPLE BIB from under the eyes to the belly; LONG HOT-PINK FEATHER LOCKS hanging at both sides of the neck; a MAGENTA SADDLE with gold trim, a gold ring and steel-blue hooks on its back (no rider); orange-brown body and thighs, PURPLE ANKLE BANDS, big three-toed BLACK CLAWS; an orange-brown tail to the back left with a row of PINK SPINES; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the tail, the feathers, the body's and the head's angle from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), RED and BLUE = its two legs (BLUE is the NEAR one), BROWN = the tail, PINK and CYAN = the long feather locks at the two sides of the neck (CYAN is the NEAR one), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176 (a pose in the air is drawn standing on that line too).
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when a leg kicks high, the feathers spread or the body curls into a ball (the picture simply grows wider or shorter - never shrink the body to fit). Each leg along its line (orange-brown thigh, purple ankle band, black three-toed claws), bending at the joints, never stretched, never squashed, never thinner than in A; the NEAR leg (blue line) in full tone and in front, the FAR leg (red line) a step darker. The tail along the brown line with its pink spines. The long pink feathers along the pink and cyan lines (hanging, swept back, spread like wings or wrapped round the body as C shows). The saddle stays on its back.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the pink spikes, the black shards, the half-closed purple eye, the mouth line) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; only the MOUTH may open where the pose says so (deep blue inside, a few small white fangs), and the eyes shut only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no wind, no spin trails, no motion lines, no dust, no shield, no impact, no stars, no glow), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND UP - one leg raised high, the knee drawn up in front, standing firm on the other.`
- a_kick: `KICK - the raised leg thrust straight forward, the big claws first, the body and the head leaning back (still image A's face, only tilted back with the body).`
- q_crouch: `CROUCH - the body low, both legs bent to spring, the head tipping back.`
- q_flip: `FLIP - the body flipping over backwards, one leg kicked high over its head (drawn standing on the ground line: the game lifts it).`
- q_kick: `KICK - halfway through the flip, both feet kicking up and forward, the head low behind.`
- q_land: `LAND - both feet back on the ground, the body crouched, the head coming up.`
- e_curl: `CURL - the body curling up, the long pink feathers at both sides wrapping round it, almost a ball.`
- e_ball: `BALL - the whole body curled into a round ball wrapped in the pink feathers, a bit of the saddle and the claws showing (the game spins it to roll).`
- r_crouch: `CROUCH - the body low, both legs deeply bent, about to spring.`
- r_spring: `SPRING - leaping up into the air, both legs tucked under the body, the long pink feathers at both sides spread like wings (drawn standing on the ground line: the game lifts it).`
- r_open: `BURST OPEN - bursting out of the ball in the air, the feathers spread wide like wings, the mouth wide open, both legs reaching down to crash.`
- r_land: `LAND - crashing down on both feet, the body crouched low and leaning forward, the feathers swept back.`
- run1: `RUN 1 - the body leaning forward level, the tail stretched straight back; the near (blue) leg ahead, the far (red) leg behind.`
- run2: `RUN 2 - the near leg at its furthest forward.`
- run3: `RUN 3 - PASSING: the legs cross (the near leg pushing back on the ground, the far leg lifted and coming forward).`
- run4: `RUN 4 - the far leg now in front.`
- run5: `RUN 5 - the far leg at its furthest forward.`
- run6: `RUN 6 - the far leg coming down.`
- run7: `RUN 7 - PASSING: the legs cross again (the far leg pushing back, the near leg coming forward).`
- run8: `RUN 8 - the near leg in front again (8 runs on into 1: the loop).`
- d_fall: `FALLING - staggering on one leg, the body tipping back, the head thrown back (still image A's face, tilted back with the body).`
- d_down: `DOWN - curled up in a feather ball lying still on the ground, the eyes shut (an X or a line).`

## 交回

- 每个姿势一张：`outputs/zippy-poses/zippy-pose-<名字>.png`（1254 × 1254、真透明背景、每格 10 px）；原始生成图原样放进 `outputs/zippy-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **22 张都画完再交**，最后写 `outputs/zippy-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/zippy_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/zippy/codex_poses/`，**先量 Codex 实际的格子**（不一定是 10 px），读 raw，**每张按定稿的身体大小读**（腿踢高、羽毛张开时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛还在、腿没有被压扁或拉长、身体大小不变、跑步 8 帧两条腿真的前后交换、远处的腿暗一档）。
- 骨架包：`tools/art/pack_zippy_poses.py`（骨架是它客户端模型自己的骨骼 Mount_*，按动作片段的那一帧投影；头放大 1.5 倍；跑步按 C:/t/zz_work/gait.py 量的一整圈取 8 帧 (0, 120, 260, 360, 480, 560, 660, 740) ms）；这份提示词由 `tools/art/gen_zippy_pose_md.py` 生成。
