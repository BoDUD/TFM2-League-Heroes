# 麦迪：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 麦迪的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**把粗长的海克斯步枪扛在近处的肩上、枪口朝后**；橙红短发齐刘海、灰蓝眼睛；歪戴的深色贝雷帽 + 金帽徽；白立领、金边宝蓝制服、胸前金徽章蓝宝石、金腰带；黑手套、淡紫灰马裤、黑长靴金护膝；步枪深藏青金箍、握把前一颗蓝水晶）。
> - 请你画 **15 个姿势**（9 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个麦迪**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 18 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、手、步枪照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的步枪贴图是乱的，**步枪的样子和颜色照定稿**。
> - **步枪的方向**：3D 模型是斜着朝镜头的，枪身常常被透视压短；我们的画面是 3/4 朝右，**端平开枪时枪口一律朝画面右边、整杆枪画全长**，后坐力把枪顶起来时枪口朝上（在头的左上方）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 她的左臂**，**紫线 = 她的右臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 左腿 / 右腿；**金线 = 步枪**（两头），**金圈 = 枪口那一头**；**灰框 = 头的位置**。`0_design_skeleton.png` 是待机的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **「通缉令」（`e_point`）没有自己的动画**：参考图是她庆祝动作里伸手指人的那一帧，步枪在那段动画里是飘着的，已经藏掉了——**这一张她把步枪照定稿扛在近处的肩上**，远处的手伸出去指着右边。
> - **头一格一格照 `1_head.png` 画在灰框里**（歪戴的贝雷帽和金帽徽、橙红短发齐刘海、灰蓝眼睛、脸朝右前方；左边那一点金色和蓝色是头后面的步枪，不是头）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、步枪**不要盖住脸**（两只眼睛和嘴）；枪托抵肩、脸贴枪的姿势里，步枪从脸的下面过去。
> - **长短要数格子**：和定稿一样，手臂从肩膀到指尖约 16 格，头（含贝雷帽）约 28 × 20 格，步枪约 26 格长。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。

## 15 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `maddie-pose-a_aim.png` | attack@0 | 橙（左臂） | 普攻起手：两脚前后分开、膝盖微弯，双手把步枪端平在腰间，枪口朝右（画面右边） |
| 3 | `maddie-pose-a_fire.png` | attack@250 | 橙（左臂） | 开枪：身子微微前压，枪口朝右，后坐力刚到（这一帧枪还平着） |
| 4 | `maddie-pose-a_kick.png` | attack@450 | 橙（左臂） | 后坐力：步枪被顶得枪口朝上竖起来（在头的左上方，不挡脸），双手还握着枪 |
| 5 | `maddie-pose-a_back.png` | attack@900 | 紫（右臂） | 放平：步枪重新端平在胸前，准备下一枪 |
| 6 | `maddie-pose-q_crouch.png` | spell@0 | 橙（左臂） | 连拨击锤起手：压低重心半蹲，枪托抵肩，枪口朝右 |
| 7 | `maddie-pose-q_fire.png` | spell@600 | 橙（左臂） | 连开 6 枪：半蹲、枪托抵肩、脸贴着枪，枪口朝右稳稳地连开（这一帧是开枪的瞬间） |
| 8 | `maddie-pose-e_point.png` | dance@1200 | 紫（右臂） | 通缉令：步枪扛在近处的肩上（和待机一样），远处的手往前（画面右边）一伸、食指指向目标 |
| 9 | `maddie-pose-r_aim.png` | spell@1100 | 橙（左臂） | 执法狙杀瞄准：蹲得更低更稳，枪托抵肩、眼睛贴着瞄具，枪口朝右，一动不动 |
| 10 | `maddie-pose-r_fire.png` | attack2@600 | 橙（左臂） | 狙击开火：巨大的后坐力把步枪顶得往后上方扬起（在头的左上方，不挡脸），身子往后一仰 |
| 11 | `maddie-pose-run1.png` | run@0 | 橙（左臂） | 跑步 1：端着步枪低姿小跑（金铲铲原样），前脚迈出 |
| 12 | `maddie-pose-run2.png` | run@190 | 橙（左臂） | 跑步 2：两脚交错 |
| 13 | `maddie-pose-run3.png` | run@380 | 橙（左臂） | 跑步 3：另一只脚迈出 |
| 14 | `maddie-pose-run4.png` | run@570 | 橙（左臂） | 跑步 4：两脚交错 |
| 15 | `maddie-pose-d_fall.png` | death@150 | 紫（右臂） | 被击倒：被打得往后仰、双手往上甩开（不挡脸），步枪脱手 |
| 16 | `maddie-pose-d_down.png` | death@650 | 橙（左臂） | 倒地：仰面倒在地上，步枪掉在身边 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 18 px squares (her soles on y 1176) - a young POLICEWOMAN SHARPSHOOTER with a big LONG HEXTECH RIFLE resting on her near shoulder, muzzle back; short orange-ginger bob with a fringe, grey-blue eyes; a dark beret tilted right with a gold badge; a white high collar, a royal blue uniform jacket with gold trim, a gold crest with a blue gem on her chest, a gold belt; black gloves, lavender-grey riding trousers, black knee boots with gold knee guards; the rifle dark navy with gold bands and a glowing BLUE CRYSTAL in front of the grip; B its HEAD shown 8x (about 28 squares wide, 20 tall: the beret, the hair, the face; the bit of gold and blue at its left edge is the rifle behind her head, not the head); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE and the hands from it - never its 3D shading; its rifle texture is broken: the rifle looks like image A's); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = her LEFT arm, PURPLE = her RIGHT arm (each line from the shoulder, the big dot = the hand), red / blue = her left / right leg, GOLD line = the rifle, GOLD ring = its MUZZLE end, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the idle skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 18 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - each arm about 16 squares from the shoulder to the fingertips, the head with the beret about 28 x 20, the rifle about 26 squares long, ALWAYS drawn at its full length (the 3D render foreshortens it): held level it points to the IMAGE RIGHT, kicked up by the recoil it points UP above the left of her head. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. The same rifle as image A (dark navy, gold bands, the blue crystal), only moved and turned. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the tilted beret with its gold badge, the orange bob and fringe, the grey-blue eyes, the face to the front-right) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or rifle covers the face (the eyes and the mouth): aiming with the stock at her shoulder, the rifle passes BELOW the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no muzzle flash, no bullets, no smoke, no sparkles, no motion lines, no target marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_aim: `AIM - feet apart one before the other, knees a little bent, both hands holding the rifle level at her waist, the muzzle to the image right.`
- a_fire: `FIRE - leaning a little into the shot, the rifle level, the muzzle to the image right, the kick just starting.`
- a_kick: `RECOIL - the kick throws the rifle up, the muzzle pointing up above the left of her head (never over the face), both hands still on it.`
- a_back: `BACK DOWN - the rifle brought level again at her chest, ready for the next shot.`
- q_crouch: `FAN WIND-UP - dropping into a half crouch, the stock at her shoulder, the muzzle to the image right.`
- q_fire: `FAN THE HAMMER - half crouched, the stock at her shoulder, her cheek on the rifle, the muzzle steady to the image right, firing shot after shot (this frame: a shot going off).`
- e_point: `WANTED - the rifle resting on her near shoulder as in the idle, her far arm thrust out to the image right, the index finger pointing at the target.`
- r_aim: `SNIPE AIM - crouched lower and steadier, the stock at her shoulder, her eye at the sight, the muzzle to the image right, holding perfectly still.`
- r_fire: `SNIPE SHOT - the huge kick throws the rifle up and back above the left of her head (never over the face), her body rocked back.`
- run1: `RUN 1 - jogging low with the rifle held across her hips (as in the game), the front foot stepping out.`
- run2: `RUN 2 - the legs passing.`
- run3: `RUN 3 - the other foot stepping out.`
- run4: `RUN 4 - the legs passing again.`
- d_fall: `STRUCK DOWN - thrown backwards, both arms flung up (never over the face), the rifle leaving her hands.`
- d_down: `DOWN - lying on her back on the ground, the rifle fallen beside her.`

## 交回

- 每个姿势一张：`outputs/maddie-poses/maddie-pose-<名字>.png`（1254 × 1254、真透明背景、每格 18 px）；原始生成图原样放进 `outputs/maddie-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **15 张都画完再交**，最后写 `outputs/maddie-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/maddie_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/maddie/codex_poses/`，**先量 Codex 实际的格子**（不一定是 18 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛和嘴还在、手和枪不挡脸、步枪不断、全长、没有被压扁的身体）。
- 骨架包：`tools/art/pack_maddie_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_maddie_pose_md.py` 生成。
