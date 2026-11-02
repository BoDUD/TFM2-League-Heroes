# 海克斯霸龙：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 海克斯霸龙的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（第一版 `thex-A-initial`），按它自己 10 px 的格子读回，1:1 定稿，这里放大成每格 9 px：3/4 朝右，**机械霸王龙**：深藏青的机械身体盖着**铜色装甲板**、嵌着蓝色发光面板，背上一排**蓝色水晶尖刺**；**铜色恐龙头盔**（两根尖耳）、**蓝色面罩**、**白眼红眶**、钢灰紫的大下颌和白色三角牙；**近处的前爪是六管加特林**，远处是机械爪；两条鸟腿、铜色三趾爪脚；**长长的机械尾巴**）。每个姿势都照它。
> - 请你画 **17 个姿势**（7 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只海克斯霸龙**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：背甲翻开、低头冲撞、侧身倒地的时候，画面会变高、变宽或变矮，**但身子、头、加特林、腿、尾巴不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**加特林每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（头的位置看骨架图的灰框）——**姿势、加特林和爪子、两条腿、尾巴、背甲、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头比定稿小，**头、身子和加特林的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），紫线 = 下颌，**青线 = 加特林那只前爪**，**粉线 = 机械爪那只前爪**，**红线 / 蓝线 = 两条腿**，**棕线 = 尾巴**，**黄线 / 橙线 = 背上两块铜甲（导弹舱）**；**灰框 = 头的位置**。每个姿势都是**青线（加特林）和蓝线的腿在近处**，画在上面。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（铜色头盔、蓝色面罩、白眼红眶、下颌和牙齿）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；`e_bite` 和 `r_fire` 下颌张得更大（照紫线），牙齿还是那些牙齿。只有 `d_down` 面罩和蓝色面板熄灭（暗蓝灰，不发光）。
> - **背甲（导弹舱）**：平时两块铜甲合在背上（像定稿那样，背上是蓝色尖刺）；`q_fire`、`r_open`、`r_fire` 照黄线 / 橙线**往上翻开竖起**，像一对铜框翅膀，里面是蓝色面板（你第 0 步 B 图画的那样）。
> - **前爪和腿**：一直是定稿那只六管加特林和那只机械爪，**照青线 / 粉线摆**，不要拉长、不要压扁、不要比定稿细；**近处的颜色正常、画在上面，远处的暗一档**。鸟腿同理（照红线 / 蓝线，膝盖往后折）。
> - **跑步 8 帧（run1–run8）是一整圈**：红线的腿迈一步、蓝线的腿迈一步；**每帧的身子、头、加特林、尾巴都是同一个**，只有两条腿按骨架换位置、尾巴跟着微微摆。**一定要看得出两条腿在交替迈步**。
> - **不画特效**：没有子弹、枪口火光、导弹、激光、烟。

## 17 个姿势

| 图 | 文件 | 片段 | 近处（画在上面） | 姿势 |
|---|---|---|---|---|
| 2 | `thex-pose-a_aim.png` | attack@100 | 青（加特林）、蓝线腿 | 普攻「加特林弹幕」：弓身站稳，加特林平端朝前瞄准 |
| 3 | `thex-pose-a_recoil.png` | attack@500 | 青（加特林）、蓝线腿 | 开火的后坐：加特林被震得往后一缩，身子跟着微微后仰 |
| 4 | `thex-pose-q_fire.png` | channel2@722 | 青（加特林）、蓝线腿 | 技能1「追踪导弹」：背上两块铜甲翻开竖起（导弹舱打开），加特林平端，头往前探 |
| 5 | `thex-pose-e_charge.png` | rise@0 | 青（加特林）、蓝线腿 | 技能2「霸龙冲撞」：压低身子往前冲，头低着往前顶，尾巴绷直 |
| 6 | `thex-pose-e_bite.png` | roar@233 | 青（加特林）、蓝线腿 | 咬：头往前猛地一伸，大嘴张到最大咬下去 |
| 7 | `thex-pose-r_open.png` | channel@900 | 青（加特林）、蓝线腿 | 大招「海克斯军械库」起手：背甲正在往上翻开，加特林抬起来 |
| 8 | `thex-pose-r_fire.png` | channel@3177 | 青（加特林）、蓝线腿 | 大招持续开火：背甲完全翻开竖起，加特林平端朝前，张大嘴（激光从嘴里射出，我后面画） |
| 9 | `thex-pose-run1.png` | run@0 | 青（加特林）、蓝线腿 | 跑 1：红线那条腿在后面刚要抬起来往前迈，蓝线那条腿踩地；身子前倾、尾巴放平，加特林端在胸前 |
| 10 | `thex-pose-run2.png` | run@159 | 青（加特林）、蓝线腿 | 跑 2：红线的腿抬起来往前送 |
| 11 | `thex-pose-run3.png` | run@317 | 青（加特林）、蓝线腿 | 跑 3：红线的腿抬到最高，在身子下面往前摆 |
| 12 | `thex-pose-run4.png` | run@476 | 青（加特林）、蓝线腿 | 跑 4：红线的腿在前面落下来 |
| 13 | `thex-pose-run5.png` | run@635 | 青（加特林）、蓝线腿 | 跑 5：红线的腿踩地，蓝线的腿在后面开始抬（换脚） |
| 14 | `thex-pose-run6.png` | run@794 | 青（加特林）、蓝线腿 | 跑 6：蓝线的腿抬起来往前送 |
| 15 | `thex-pose-run7.png` | run@952 | 青（加特林）、蓝线腿 | 跑 7：蓝线的腿抬到最高，在身子下面往前摆 |
| 16 | `thex-pose-run8.png` | run@1111 | 青（加特林）、蓝线腿 | 跑 8：蓝线的腿在前面落下来（8 接回 1，循环） |
| 17 | `thex-pose-d_fall.png` | death@2619 | 青（加特林）、蓝线腿 | 被打倒：踉跄着侧身倒下去 |
| 18 | `thex-pose-d_down.png` | death@3666 | 青（加特林）、蓝线腿 | 倒地：侧躺在地上不动，面罩和蓝色发光面板熄灭（画成暗蓝灰、不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (its soles on y 1176) - a MECHANICAL T-REX: a dark navy robot body under COPPER ARMOUR PLATES with glowing BLUE PANELS, a row of BLUE CRYSTAL SPIKES down its back, a COPPER DINOSAUR HELMET with two ear spikes, a BLUE VISOR, a white eye with a red rim, a big steel-lavender jaw with white triangle teeth, the NEAR forelimb a SIX-BARREL GATLING GUN, the far one a mechanical claw, two bird-like legs with copper three-toed clawed feet, a LONG ARMOURED TAIL; B its HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the gatling and the claw, the two legs, the tail, the back plates, the body's and the head's angle from it - never its 3D shading; the model's head is smaller than A's: keep A's proportions); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), purple = the jaw, CYAN = the gatling forelimb, PINK = the claw forelimb, RED and BLUE = its two legs, BROWN = the tail, YELLOW and ORANGE = its two back plates (the missile pods), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the head, the GATLING, the legs and the tail exactly as big as in A in EVERY pose, also when the back plates rise, it lunges low or it lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body to fit). The gatling and the claw along the cyan and pink lines, never stretched, never squashed, never thinner than in A; each leg along its line (a bird leg, the knee bending back); the tail along the brown line; the NEAR (cyan, blue) parts in full tone and in front, the FAR ones a step darker. The back plates lie closed on its back (as in A) unless the yellow and orange lines lift them: then they stand up open like a pair of copper-framed wings with blue panels inside.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the copper helmet, the blue visor, the eye, the jaw and teeth) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the jaw opens wider only where the purple line says so; the visor and the panels go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no bullets, no muzzle flash, no missiles, no laser, no smoke, no dust, no motion lines, no glow halo), no pilot, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_aim: `AIM - crouched and planted, the gatling levelled forward, aiming.`
- a_recoil: `RECOIL - the gatling kicked back by its fire, the body rocking back a little.`
- q_fire: `PODS OPEN - the two copper back plates flipped up (the missile pods open), the gatling levelled, the head pushed forward.`
- e_charge: `CHARGE - the body low and lunging forward, the head down and driving ahead, the tail stiff behind.`
- e_bite: `BITE - the head snapping forward, the jaws opened wide to bite.`
- r_open: `PODS RISING - the back plates halfway up, opening, the gatling coming up.`
- r_fire: `FULL FIRE - the back plates fully raised, the gatling levelled forward, the mouth wide open (the laser comes out of it later, not drawn).`
- run1: `RUN 1 - the RED-line leg behind, just about to lift and step forward, the BLUE-line leg planted; the body leaning forward, the tail level, the gatling held at the chest.`
- run2: `RUN 2 - the RED-line leg lifted, swinging forward.`
- run3: `RUN 3 - the RED-line leg at its highest, swinging forward under the body.`
- run4: `RUN 4 - the RED-line leg coming down in front.`
- run5: `RUN 5 - the RED-line leg planted, the BLUE-line leg starting to lift behind (the change of feet).`
- run6: `RUN 6 - the BLUE-line leg lifted, swinging forward.`
- run7: `RUN 7 - the BLUE-line leg at its highest, swinging forward under the body.`
- run8: `RUN 8 - the BLUE-line leg coming down in front (8 runs on into 1: the loop).`
- d_fall: `FALLING - staggering and toppling over sideways.`
- d_down: `DOWN - lying on its side on the ground, still, the visor and the blue panels gone dark (a dull dark blue-grey, no glow).`

## 交回

- 每个姿势一张：`outputs/thex-poses/thex-pose-<名字>.png`（1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/thex-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **17 张都画完再交**，最后写 `outputs/thex-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/thex_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/thex/codex_poses/`，**先量 Codex 实际的格子**（不一定是 9 px），读 raw，**每张按定稿的身体大小读**（背甲翻开、低头冲撞时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛和面罩还在、加特林和定稿一样大、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的爪子和腿暗一档）。
- 骨架包：`tools/art/pack_thex_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；灰框 = 定稿的头跟着 Head 关节走；跑步按量出来的一整圈取 8 帧 (0, 159, 317, 476, 635, 794, 952, 1111) ms）；这份提示词由 `tools/art/gen_thex_pose_md.py` 生成。
