# 伦妮：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 伦妮的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，缩到游戏大小定稿：3/4 朝右，**战斗架势，双手端着链锯、两条黄铜导板平平朝右前方**；橘红背头（两侧剃短）、苍白脸、深色烟熏眼妆、灰色金属鼻夹、两条荧光绿导管、洋红高领；**画面左边（背后）一大团墨绿羽毛披肩**、紫色无袖上衣、深蓝紫长手套、棕色腰带和发绿光的药剂罐、紫色宽裤（小腿扎紧）、深色绑带靴；**链锯：洋红引擎 + 荧光绿转子 + 灰蓝握把 + 两条黄铜导板（深色槽、一排灰色圆孔）**）。
> - 请你画 **19 个姿势**（9 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个伦妮**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**身体的姿势照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **链锯的大小照定稿，不照参考图**：模型的链锯比定稿长。骨架图里**紫线 = 链锯（圆点那头 = 引擎，金色三角那头 = 导板尖）**，链锯沿紫线的方向画，**大小、粗细和定稿一样（引擎约 15 × 14 格，从引擎后沿到导板尖约 56 格）**，紫线比这长时链锯画到定稿的长度就停。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线、青线 = 两只胳膊**（每条线第一个点是肩膀，**大圆点是手**）；红线 / 蓝线 = 两条腿；**紫线 + 金三角 = 链锯**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **握锯的手照定稿**：双手端锯时一只手握引擎上的握把、一只手扶在引擎前面的把手上；单手拿锯时（跑步）用骨架图里离锯最近的那只手。
> - **头一格一格照 `1_head.png` 画在灰框里**（橘红背头、苍白脸朝右前方、深色眼妆、灰色鼻夹、两条绿导管、下撇的嘴）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_fall` / `d_down` 倒下时头跟着身体放倒，但还是这个头）。链锯和手**不要挡住脸**（眼睛、鼻夹、嘴）。
> - **羽毛披肩**跟着肩膀走：一直在她远处的肩膀和背后（画面左），大小和定稿一样，羽毛往外、往下炸开。
> - **长短要数格子**：和定稿一样，头（含头发）约 24 × 29 格，手臂从肩膀到拳头约 16 格。**手臂沿着骨架画，长短和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。她身材结实。
> - **跑步 8 帧要有交叉步**：两条腿照红线 / 蓝线**前后交换**，中间几帧两条腿**交叉经过**，不要每帧都是两腿大大叉开；**远处的那条腿暗一档**，近处的腿完整亮色，这样看得出哪条腿在前。
> - **举起的姿势**（`r_heave`、`r_hold`）：链锯举过头顶，**画布上方要放得下**，导板尖别出画；目标不画。
> - **`d_down`**：参考图是她翻倒在地，**照它的大小和位置，把她画成仰面平躺在地上**（身体贴着地面线），链锯掉在身边地上。

## 19 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `renni-pose-a_push.png` | stance@320 | 橙 | 普攻（链锯研磨）：定稿的架势，身体往前压，链锯往前一顶，导板尖顶在最前面 |
| 3 | `renni-pose-a_grind.png` | stance@640 | 橙 | 研磨：链锯顶在前面上下颠一下（锯着目标），身体随之一沉 |
| 4 | `renni-pose-q_charge.png` | lift@0 | 青 | 链锯冲撞：大弓步往前冲，身体压得很低，链锯平端顶在最前面 |
| 5 | `renni-pose-e_guard.png` | idle@860 | 青 | 锯刃格挡：两脚叉开站稳，链锯竖起来挡在身前（导板朝上，引擎在胸前），像一面盾 |
| 6 | `renni-pose-r_ram.png` | lift@330 | 青 | 泥奔者重击 1：链锯往前上方一顶，把目标挑起来（不画目标） |
| 7 | `renni-pose-r_heave.png` | lift@600 | 橙 | 举起：链锯往头顶上抡，导板朝上 |
| 8 | `renni-pose-r_hold.png` | hold@0 | 橙 | 举在头顶：双手把链锯直直举过头顶，导板朝天（目标挂在上面，不画） |
| 9 | `renni-pose-r_slam.png` | slam@470 | 青 | 砸地：整个人往前扑，链锯狠狠砸在面前的地上 |
| 10 | `renni-pose-r_after.png` | slam@940 | 青 | 砸完：链锯拖在地上，慢慢回到架势 |
| 11 | `renni-pose-run1.png` | run@0 | 青 | 跑 1：弓着身子跑（金铲铲原样），链锯低低地拎在身侧 |
| 12 | `renni-pose-run2.png` | run@141 | 青 | 跑 2 |
| 13 | `renni-pose-run3.png` | run@283 | 青 | 跑 3 |
| 14 | `renni-pose-run4.png` | run@424 | 青 | 跑 4 |
| 15 | `renni-pose-run5.png` | run@566 | 青 | 跑 5 |
| 16 | `renni-pose-run6.png` | run@707 | 青 | 跑 6 |
| 17 | `renni-pose-run7.png` | run@849 | 青 | 跑 7 |
| 18 | `renni-pose-run8.png` | run@990 | 青 | 跑 8 |
| 19 | `renni-pose-d_fall.png` | death@333 | 橙 | 被击倒：被打得往上往后飞，链锯脱手 |
| 20 | `renni-pose-d_down.png` | death@1000 | 青 | 倒地：仰面平躺在地上，链锯掉在身边 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (her soles on y 1176) - a STURDY WOMAN with an ORANGE-RED pompadour (shaved sides), a PALE face with dark smoky eye make-up, a GREY METAL NOSE CLIP and two GLOWING NEON-GREEN TUBES across her cheeks, a magenta high collar; a big RUFF OF DARK GREEN FEATHERS over her far shoulder and back, a purple sleeveless top, long dark blue-purple gloves, a brown belt with glowing green vials, baggy purple trousers gathered at the calf, dark strapped boots; holding a CHAINSAW level in both hands, the bars forward to the right (a round MAGENTA ENGINE with a NEON-GREEN ROTOR DISC, a grey-blue handle, TWO PARALLEL BRASS GUIDE BARS with a dark slot and grey round holes); B its HEAD shown 8x (about 24 squares wide, 29 tall: the hair, the face, the nose clip, the tubes); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the BODY POSE from it - never its 3D shading, and NOT its saw size: the model's saw is longer); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE / CYAN = her arms (each line from the shoulder, the big dot = the hand), red / blue = her legs, the PURPLE line = the chainsaw (the round dot = the ENGINE end, the GOLD TRIANGLE = the BAR TIPS), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - the head with the hair about 24 x 29, each arm about 16 squares from the shoulder to the fist, a sturdy body. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. THE CHAINSAW along the purple line of D, the engine at the dot end and the bar tips toward the gold triangle, EXACTLY AS BIG AS IN IMAGE A (engine about 15 x 14 squares, about 56 squares from the back of the engine to the bar tips) - stop at that length even if the purple line runs longer; held in her hands as in image A. The feather ruff stays on her far shoulder and back, as big as in A. The near side in full tone, the far side a step darker (the far leg a step darker than the near leg).
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the pale face to the front-right, the eye make-up, the grey nose clip, the green tubes, the orange-red hair) - the same head in every pose, only moved (tilted with the body when she falls or lies down), never turned, never redrawn as a profile. Neither the saw nor a hand covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no sparks, no sawdust, no green shimmer smoke, no ground cracks, no motion lines, no marks), no target character, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_push: `GRIND PUSH - the design's stance leaning in, the chainsaw shoved forward, the BAR TIPS leading.`
- a_grind: `GRIND - the saw held out in front, jolting as it bites, her body dipping with it.`
- q_charge: `CHARGE - a deep forward lunge, body low, the chainsaw level and thrust out ahead.`
- e_guard: `SAW GUARD - feet planted wide, the chainsaw raised UPRIGHT in front of her body (the bars up, the engine at her chest) like a shield.`
- r_ram: `RAM - the saw driven forward and upward to hook the target (do NOT draw the target).`
- r_heave: `HEAVE - swinging the saw up over her head, the bars rising.`
- r_hold: `HOLD - both arms straight up, the chainsaw held high overhead, the bars pointing to the sky (the target hangs on it: do NOT draw it).`
- r_slam: `SLAM - lunging forward, the chainsaw smashed down onto the ground in front of her.`
- r_after: `AFTER THE SLAM - the saw dragging on the ground, rising back toward the stance.`
- run1: `RUN 1 - a hunched run (as in the game), the chainsaw carried low at her side.`
- run2: `RUN 2`
- run3: `RUN 3`
- run4: `RUN 4`
- run5: `RUN 5`
- run6: `RUN 6`
- run7: `RUN 7`
- run8: `RUN 8`
- d_fall: `KNOCKED BACK - thrown up and back, the saw flying from her hands.`
- d_down: `DOWN - lying flat on her back, the saw dropped beside her.`

## 交回

- 每个姿势一张：`outputs/renni-poses/renni-pose-<名字>.png`（1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/renni-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **19 张都画完再交**，中间不要停，最后写 `outputs/renni-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/renni_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/renni/codex_poses/`，**先量 Codex 实际的格子**（不一定是 12 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、脸上眼睛鼻夹导管还在、链锯不挡脸、链锯大小和方向对、羽毛披肩在背后、没有被压扁的身体、腿不变形、跑步有交叉步、远近腿深浅分得开）。
- 骨架包：`tools/art/pack_renni_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的；链锯按它子网格顶点的主轴画）；这份提示词由 `tools/art/gen_renni_pose_md.py` 生成。
