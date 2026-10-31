# 绯红印记树怪：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 树怪的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A 的原稿，按它自己 6 px 的格子读回，缩到游戏大小定稿（40 像素高，PPU 1.7），这里放大成每格 8 px：3/4 朝右，**四肢着地弓背蹲着的深红褐树皮巨兽**；**两条又长又粗的前臂，前爪是三根红橙大爪**；脖子上一圈**绿叶领子**；背上**弯曲的深色树枝（内侧红）和发光的红橙核心**；**楔子形树皮脑袋低在领子下，两只红眼（黄色亮芯）和额头的橙色螺旋**；树皮上发光的红色裂纹）。每个姿势都照它。
> - 请你画 **19 个姿势**（9 个动作 + 8 帧奔跑 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个树怪**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 8 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：人立起来、爪子举过头顶、跳到空中、趴倒在地的时候，画面会变高、变宽或变矮，**但身子、头、手臂、爪子、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**三根红爪每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、两条手臂和爪子、两条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的宽窄、树皮甲片、树叶领子和背上树枝的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条前臂（肩膀到爪子）**，**红线 / 蓝线 = 两条后腿**；**灰框 = 头的位置**。**大多数姿势近处（画面右边、离我们近）的是青线前臂和蓝线后腿**（奔跑里有几帧近处的是红线后腿或粉线前臂，照骨架）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（楔子形树皮脑袋、两只红眼和黄色亮芯、额头的橙色螺旋、压在上面的绿叶）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 眼睛熄灭（暗红褐色，不发光）。
> - **手臂和爪子**：一直是定稿那两条粗长的树皮前臂和三根红橙大爪（前臂上的红色裂纹），**照骨架的粉线 / 青线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的手臂颜色正常、画在上面，远处的暗一档**。后腿同理（短粗，脚上小红爪，照红线 / 蓝线）。
> - **背上的树枝、红核和绿叶领子**每张都在，跟着身子倾斜；人立起来时在背上最高处，趴下时压低往前倾。
> - **奔跑 8 帧（run1–run8）是一整圈**：像大猩猩一样用前爪撑地往前跑，**粉线前爪抡一步、青线前爪抡一步**，两条后腿跟着交替；**每帧的身子、头、爪子都是同一个**，只有四肢按骨架换位置。**一定要看得出两只前爪在交替往前撑**。
> - **死亡（d_rear、d_down）**：d_down 整个趴平在地上；身子、爪子的大小不变，只是躺平。

## 19 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `brambleback-pose-a_raise.png` | attack@208 | 普攻「荆爪横扫」起手：用后腿立起身子，一只长臂把大爪高高举起，另一只撑着 |
| 3 | `brambleback-pose-a_swipe.png` | attack@416 | 横扫：举起的大爪往前往下狠狠扫到身前地上，身子往前扑低 |
| 4 | `brambleback-pose-q_jump.png` | leap@170 | 技能1「荆棘飞扑」跃起：四肢收在身下，整个身子腾空往前扑（脚离地） |
| 5 | `brambleback-pose-q_reach.png` | leap@312 | 扑到最高：身子挺直，一只长臂把大爪高高举过头顶，准备扑下 |
| 6 | `brambleback-pose-q_land.png` | leap@470 | 扑落：大爪砸在身前地上，四肢着地压低，身子往前压 |
| 7 | `brambleback-pose-e_crouch.png` | roar@179 | 技能2「绯红咆哮」蓄力：四肢收拢、身子缩起来压低，背上的红核亮起 |
| 8 | `brambleback-pose-e_rear.png` | roar@537 | 怒吼：用后腿人立起来，挺起胸口，两只长臂张开，抬头怒吼 |
| 9 | `brambleback-pose-r_rear.png` | slam@400 | 大招「猩红之怒」起手：人立到最高，两只大爪一起高高举过头顶 |
| 10 | `brambleback-pose-r_slam.png` | slam@540 | 双爪砸地：两只大爪一起狠狠砸在身前地上，身子深深压低，背上的树枝往前倾 |
| 11 | `brambleback-pose-run1.png` | run@0 | 跑 1：粉线前爪刚离地往前抡，青线前爪撑在最前面；蓝线后腿抬起往前 |
| 12 | `brambleback-pose-run2.png` | run@133 | 跑 2：粉线前爪抡起往前送，蓝线后腿在空中往前 |
| 13 | `brambleback-pose-run3.png` | run@266 | 跑 3：粉线前爪抡到最高最前，蓝线后腿落到身子下面，红线后腿撑地 |
| 14 | `brambleback-pose-run4.png` | run@400 | 跑 4：粉线前爪在最前面落地撑住；红线后腿抬起 |
| 15 | `brambleback-pose-run5.png` | run@533 | 跑 5：青线前爪离地往前抡，红线后腿往前送 |
| 16 | `brambleback-pose-run6.png` | run@666 | 跑 6：青线前爪抡起往前送，红线后腿落地 |
| 17 | `brambleback-pose-run7.png` | run@800 | 跑 7：青线前爪抡到最高最前，两条后腿撑地 |
| 18 | `brambleback-pose-run8.png` | run@933 | 跑 8：青线前爪在最前面落地撑住（8 接回 1，循环） |
| 19 | `brambleback-pose-d_rear.png` | death@300 | 被打倒：猛地往后人立起来，两臂无力地垂着 |
| 20 | `brambleback-pose-d_down.png` | death@2050 | 倒地：整个趴平在地上不动，背上的红核和眼睛熄灭（画成暗红褐色） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 8 px squares (its lowest point on y 1176) - a HUNCHED FOUR-LIMBED BARK BEAST built like a gorilla, of DARK REDDISH-BROWN BARK PLATES with GLOWING RED VEINS: TWO LONG THICK FRONT ARMS each ending in THREE BIG RED-ORANGE CLAWS, short thick back legs with small red claws, a COLLAR OF GREEN LEAVES round its neck and shoulders, CURLING DARK BRANCHES with red insides and a GLOWING RED-ORANGE CORE on its back, a WEDGE-SHAPED BARK HEAD set low under the leaf collar with TWO RED EYES with yellow-hot centres and an ORANGE SPIRAL on its forehead; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two arms and claws, the two back legs, the body's and the head's angle from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two front arms (shoulder to claws), RED and BLUE = its two back legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 8 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176 (in the air only where the pose says so).
THE SAME BULK AS IMAGE A: the body, the head, the two LONG ARMS with their BIG CLAWS and the back legs exactly as big as in A in EVERY pose, also when it rears up, lifts its claws over its head, leaps or lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body or the claws to fit). Each front arm along its line (thick bark upper arm and forearm with red veins, the three big red-orange claws at the end), bending at the elbow, never stretched, never squashed, never thinner than in A; each back leg along its line (short and thick); the NEAR arm and leg in full tone and in front, the FAR ones a step darker. The leaf collar, the curling branches and the red core stay on its neck and back, tilting with the body.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the wedge of bark, the two red eyes with yellow centres, the orange forehead spiral, the leaves over it) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no fire, no burn, no red aura, no claw trails, no leap trail, no roar waves, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_raise: `RAISE - rising on its back legs, one long arm lifting its big claws high, the other arm supporting.`
- a_swipe: `SWIPE - the raised claws raked down and forward onto the ground in front, the body lunging low.`
- q_jump: `JUMP - springing into the air, all four limbs tucked under the body, flying forward (feet off the ground).`
- q_reach: `REACH - at the top of the pounce, the body stretched up, one long arm lifting its claws high over its head, about to strike down.`
- q_land: `LAND - the claws crashing down onto the ground in front, landing low on all fours, the body pressed forward.`
- e_crouch: `CROUCH - gathering itself, limbs drawn in, the body crouched low and tight, the red core on its back glowing.`
- e_rear: `REAR AND ROAR - standing up on its back legs, chest thrust out, both long arms spread, the head up, roaring.`
- r_rear: `BOTH CLAWS HIGH - reared up at its tallest on its back legs, both claws raised together high over its head.`
- r_slam: `SLAM - both claws smashed together into the ground in front, the body bent far down, the back branches tipped forward.`
- run1: `GALLOP 1 - the PINK front arm just leaving the ground to swing forward, the CYAN front claw planted far ahead; the BLUE back leg lifting forward.`
- run2: `GALLOP 2 - the PINK front arm swinging up and forward, the BLUE back leg forward in the air.`
- run3: `GALLOP 3 - the PINK front arm at its highest and furthest forward, the BLUE back leg landing under the body, the RED back leg planted.`
- run4: `GALLOP 4 - the PINK front claw landing far ahead, the weight onto it; the RED back leg lifting.`
- run5: `GALLOP 5 - the CYAN front arm leaving the ground to swing forward, the RED back leg swinging forward.`
- run6: `GALLOP 6 - the CYAN front arm swinging up and forward, the RED back leg landing.`
- run7: `GALLOP 7 - the CYAN front arm at its highest and furthest forward, both back legs planted.`
- run8: `GALLOP 8 - the CYAN front claw landing far ahead (8 runs on into 1: the loop).`
- d_rear: `STAGGER - jerking up onto its back legs, both arms hanging limp.`
- d_down: `DOWN - collapsed flat on the ground, lying still, the red core and the eyes gone dark (a dull dark red-brown, no glow).`

## 交回

- 每个姿势一张：`outputs/brambleback-poses/brambleback-pose-<名字>.png`（1254 × 1254、真透明背景、每格 8 px）；原始生成图原样放进 `outputs/brambleback-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **19 张都画完再交**，最后写 `outputs/brambleback-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/brambleback_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/brambleback/codex_poses/`，**先量 Codex 实际的格子**（不一定是 8 px），读 raw，**每张按定稿的身体大小读**（人立、举爪、跳起时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、两只红眼和螺旋还在、爪子和定稿一样大、手臂和腿没有被压扁或拉长、奔跑 8 帧两只前爪真的交替、远处的手臂和腿暗一档）。
- 骨架包：`tools/art/pack_brambleback_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；头放大 1.4 倍；奔跑按爪子和脚尖的高度量的一整圈取 8 帧 (0, 133, 266, 400, 533, 666, 800, 933) ms）；这份提示词由 `tools/art/gen_brambleback_pose_md.py` 生成。
