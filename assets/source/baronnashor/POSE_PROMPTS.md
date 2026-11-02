# 纳什男爵：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 纳什男爵的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（带腿的那张 `baronnashor-A.png`），按它自己 11 px 的格子读回，1:1 定稿，这里放大成每格 9 px：3/4 朝右，**虚空巨蛇**：S 形的紫色鳞甲身躯，正面一整条**青绿色分节腹甲**；**蓝紫硬甲头**、正中黄色菱形大眼和两边的小黄眼、**红色大嘴白牙**、**象牙白獠牙**；头后一圈**紫色鳍刺头冠、洋红鳍尖**；头两侧细臂上的**两只小蛇头**；身子下部两只**象牙白大弯爪**；**两条紫色短粗后腿、象牙色三趾脚**）。每个姿势都照它。
> - 请你画 **19 个姿势**（10 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只纳什男爵**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：立起来、往下砸、侧身倒地的时候，画面会变高、变宽或变矮，**但头、身子、爪子、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（头的位置看骨架图的灰框）——**身躯怎么弯、头往哪探、两只小头和两只爪子、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。**金铲铲的模型没有腿**（它是从地里钻出来的），所以参考图上**腿只有骨架线（红线 / 蓝线）**，模型身躯在腿那里的部分不用管：**腿照骨架线、照定稿的腿画**。模型的头比定稿小，**头和身子的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 身躯（屁股到头），紫线 = 下颌，**粉线 / 青线 = 两只小蛇头（连在细臂上）**，**黄线 / 橙线 = 两只大弯爪**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。每个姿势都是**青线小头、橙线爪子、蓝线腿在近处**，画在上面、颜色正常；另一边的暗一档。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（蓝紫硬甲头、黄眼睛、红嘴白牙、白獠牙）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；`a_rear`、`a_bite`、`q_breath`、`r_rear`、`r_spit` 嘴张得更大（照紫线），牙齿还是那些牙齿。只有 `d_down` 眼睛熄灭（暗黄，不发光）。头冠的鳍刺跟着头走。
> - **爪子和腿**：一直是定稿那两只象牙白大弯爪和那两条紫色短腿、三趾脚，**照骨架线摆**，不要拉长、不要压扁、不要比定稿细；腿的膝盖照线弯。
> - **`e_dig`（在地下穿行）只画头冠的几根鳍刺尖露在地面线上面**，地面线以下什么都不画（土堆、地洞是特效，我后面画）。
> - **跑步 8 帧（run1–run8）是一整圈**：红线的腿迈一步、蓝线的腿迈一步；**每帧的头、身躯、爪子、小头都是同一个**，只有两条腿按骨架换位置、身子跟着微微起伏。**一定要看得出两条腿在交替迈步**。
> - **不画特效**：没有酸液、尖刺、土块、尘土、光。

## 19 个姿势

| 图 | 文件 | 身体的片段 | 腿的片段 | 姿势 |
|---|---|---|---|---|
| 2 | `baronnashor-pose-a_rear.png` | attack@416 | idle@0 | 普攻「腐蚀撕咬」起手：身子往后一仰，头高高抬起、嘴张开，准备咬下去 |
| 3 | `baronnashor-pose-a_bite.png` | attack@560 | idle@0 | 咬下去：头往前下方猛地一咬，大嘴张到最大 |
| 4 | `baronnashor-pose-q_breath.png` | spell2@957 | idle@0 | 技能1「腐蚀吐息」：头往前低低探出、大嘴张开朝前喷（酸液我后面画），两只爪子张开 |
| 5 | `baronnashor-pose-e_dive.png` | burrow@300 | rise@0 | 技能2「钻地突袭」：压低身子蹲下、头往下扎，准备钻进地里 |
| 6 | `baronnashor-pose-e_dig.png` | burrowed@400 | （在地下） | 在地下穿行：整个身子都在地下，只有头冠的几根鳍刺露在地面上（地面和土堆是特效，不画） |
| 7 | `baronnashor-pose-e_rise.png` | unburrow@300 | rise@200 | 破土而出：从地里猛地蹿出来，身子挺直往上，头高高抬起 |
| 8 | `baronnashor-pose-r_rear.png` | spell@478 | idle@0 | 大招「虚空之怒」起手：伸直身子高高立起，头抬高、嘴大张，头冠鳍刺全竖起（你第 0 步 B 图那样） |
| 9 | `baronnashor-pose-r_slam.png` | spell@957 | idle@0 | 猛砸：整个身子往前下方砸下去，头和两只爪子砸向地面（尖刺我后面画） |
| 10 | `baronnashor-pose-r_spit.png` | spell2@1436 | idle@0 | 连续吐酸：头往前伸、嘴张开往前吐（酸液我后面画），身子微微前倾 |
| 11 | `baronnashor-pose-run1.png` | idle@0 | run@0 | 跑 1：红线那条腿在后面刚要抬起来往前迈，蓝线那条腿踩地；身子微微前倾，头往前探 |
| 12 | `baronnashor-pose-run2.png` | idle@159 | run@159 | 跑 2：红线的腿抬起来往前送 |
| 13 | `baronnashor-pose-run3.png` | idle@317 | run@317 | 跑 3：红线的腿抬到最高，在身子下面往前摆 |
| 14 | `baronnashor-pose-run4.png` | idle@476 | run@476 | 跑 4：红线的腿在前面落下来 |
| 15 | `baronnashor-pose-run5.png` | idle@635 | run@635 | 跑 5：红线的腿踩地，蓝线的腿在后面开始抬（换脚） |
| 16 | `baronnashor-pose-run6.png` | idle@794 | run@794 | 跑 6：蓝线的腿抬起来往前送 |
| 17 | `baronnashor-pose-run7.png` | idle@952 | run@952 | 跑 7：蓝线的腿抬到最高，在身子下面往前摆 |
| 18 | `baronnashor-pose-run8.png` | idle@1111 | run@1111 | 跑 8：蓝线的腿在前面落下来（8 接回 1，循环） |
| 19 | `baronnashor-pose-d_fall.png` | death@1100 | death@2619 | 被打倒：摇晃着往前侧身倒下去 |
| 20 | `baronnashor-pose-d_down.png` | death@1165 | death@3666 | 倒地：侧躺在地上不动，眼睛熄灭（画成暗黄、不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (its soles on y 1176) - a VOID SERPENT MONSTER: an S-curved body of PURPLE SCALE ARMOUR with ONE TEAL-GREEN SEGMENTED BELLY down its front, a hard BLUE-VIOLET ARMOURED HEAD with a YELLOW DIAMOND EYE in the middle and small yellow eyes beside it, a RED MOUTH with white teeth, IVORY TUSKS, a crown of PURPLE CREST FINS with MAGENTA TIPS behind the head, TWO SMALL SERPENT HEADS on thin arms beside the head, TWO BIG CURVED IVORY CLAWS low on the body, and TWO SHORT THICK PURPLE LEGS with ivory three-toed feet; B its HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE from it: how the body curves, where the head goes, the two small heads, the two claws, the body's and the head's angle - never its 3D shading; the model's head is smaller than A's: keep A's proportions). THE MODEL HAS NO LEGS (in its game it rises out of the ground): its legs are only the RED and BLUE lines drawn on C - draw A's own legs along them and ignore the model's body where the legs are; D the SKELETON of that pose, exactly over C: green = the body (hips to head), purple = the jaw, PINK and CYAN = the two small heads on their thin arms, YELLOW and ORANGE = the two big claws, RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the head, the crest, the body, the claws and the legs exactly as big as in A in EVERY pose, also when it rears up, slams down or lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body to fit). The claws along the yellow and orange lines and the small heads along the pink and cyan lines, never stretched, never squashed, never thinner than in A; each leg along its line, the knee bending as the line bends, the three-toed foot at its end; the NEAR parts (the CYAN small head, the ORANGE claw, the BLUE leg) in full tone and in front, the far ones a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the blue-violet armoured head, the yellow eyes, the red mouth and teeth, the ivory tusks) with the crest fins behind it - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the mouth opens wider only where the purple line says so; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no acid, no spikes, no rocks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_rear: `REAR BACK - the neck drawn back and up, the head high, the mouth open, about to strike.`
- a_bite: `BITE - the head snapping down and forward, the jaws opened wide.`
- q_breath: `BREATH - the head thrust low and forward, the mouth wide open toward the front (the acid comes out of it later, not drawn), both low claws spread.`
- e_dive: `DIVE - crouched low on bent legs, the head ducking down toward the ground, about to burrow.`
- e_dig: `UNDERGROUND - the whole body under the ground: only the tips of the crest fins stick up above the ground line (the earth itself is drawn later, not here).`
- e_rise: `BURST OUT - springing up out of the ground, the body shooting straight up, the head held high.`
- r_rear: `REAR UP - the body stretched straight up and tall, the head raised high, the mouth wide open, every crest fin standing up (like your picture B of step 0).`
- r_slam: `SLAM - the whole body crashing down and forward, the head and both low claws driving into the ground (the spikes come later, not drawn).`
- r_spit: `SPIT - the head pushed forward, the mouth open, spitting forward (the acid comes later, not drawn), the body leaning forward a little.`
- run1: `RUN 1 - the RED-line leg behind, just about to lift and step forward, the BLUE-line leg planted; the body leaning forward a little, the head pushed forward.`
- run2: `RUN 2 - the RED-line leg lifted, swinging forward.`
- run3: `RUN 3 - the RED-line leg at its highest, swinging forward under the body.`
- run4: `RUN 4 - the RED-line leg coming down in front.`
- run5: `RUN 5 - the RED-line leg planted, the BLUE-line leg starting to lift behind (the change of feet).`
- run6: `RUN 6 - the BLUE-line leg lifted, swinging forward.`
- run7: `RUN 7 - the BLUE-line leg at its highest, swinging forward under the body.`
- run8: `RUN 8 - the BLUE-line leg coming down in front (8 runs on into 1: the loop).`
- d_fall: `FALLING - swaying and toppling over sideways to the front.`
- d_down: `DOWN - lying on its side on the ground, still, the eyes gone dark (a dull dark yellow, no glow).`

## 交回

- 每个姿势一张：`outputs/baronnashor-poses/baronnashor-pose-<名字>.png`（1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/baronnashor-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **19 张都画完再交**，最后写 `outputs/baronnashor-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/baronnashor_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/baronnashor/codex_poses/`，**先量 Codex 实际的格子**（不一定是 9 px），读 raw，**每张按定稿的身体大小读**（立起来、往下砸时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、黄眼睛和红嘴还在、爪子和定稿一样大、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的爪子和腿暗一档）。
- 骨架包：`tools/art/pack_baronnashor_poses.py`（身体的骨架是纳什男爵客户端模型自己的骨骼，腿是海克斯霸龙的腿，两者在定稿的屁股（第 70 行）接上；灰框 = 定稿的头跟着 Head 关节走；跑步按海克斯霸龙量出来的一整圈取 8 帧 (0, 159, 317, 476, 635, 794, 952, 1111) ms）；这份提示词由 `tools/art/gen_baronnashor_pose_md.py` 生成。
