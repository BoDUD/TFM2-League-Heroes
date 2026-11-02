# 岩宝：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 岩宝的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（最终版），按它自己 14 px 的格子读回，1:1 定稿，两只眼睛我重画成了清楚的圆环，这里放大成每格 12 px：3/4 朝右，**深青灰板岩色的大块头岩石魔像**；**两只巨大的石拳**垂在身体两侧；棕色树根缠满肩膀、手臂和腰；肩上的亮绿叶丛和**小盆景树**、一根弯木刺；**小头缩在两肩之间：灰蓝色尖顶石兜帽、发光的橙色脸板、两只黄色圆环眼睛**；胸口紫色三角水晶纹章）。每个姿势都照它。
> - 请你画 **20 个姿势**（10 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个岩宝**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：拳头举过头顶、两臂张开、蹲下、趴倒在地的时候，画面会变高、变宽或变矮，**但身子、头、拳头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**两只巨拳每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置（模型的头很小，头的位置看骨架图的灰框）——**姿势、两只手臂和拳头、两条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的宽窄、石块和拳头的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条手臂（肩膀到拳头）**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。**每张骨架图旁边的表里写了这个姿势哪条手臂、哪条腿离我们近**（近处的画在上面）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（灰蓝石兜帽、橙色脸板、两只黄色圆环眼睛）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 脸板和眼睛熄灭（暗橙褐色，不发光）。
> - **手臂和拳头**：一直是定稿那两条缠着树根的粗石臂和两只巨拳，**照骨架的粉线 / 青线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的手臂颜色正常、画在上面，远处的暗一档**。腿同理（短粗石墩，照红线 / 蓝线）。
> - **跑步 8 帧（run1–run8）是一整圈**：红线的腿迈一步、蓝线的腿迈一步；**每帧的身子、头、拳头都是同一个**，只有两条腿按骨架换位置、两只拳头跟着前后摆。**一定要看得出两条腿在交替迈步**。
> - **大招跳起的两帧（r_leap、r_air）也画在地面线上**（最低点 y = 1176），离地的高度我在游戏里加。
> - **扔石头（q_wind、q_throw）不要画石头**，石头是后面单独画的特效；拳头空着就好。
> - **死亡（d_fall、d_down）**：d_down 脸朝下趴倒在地；石块、拳头、盆景树的大小不变，只是躺平。

## 20 个姿势

| 图 | 文件 | 片段 | 近处（画在上面） | 姿势 |
|---|---|---|---|---|
| 2 | `brock-pose-a_raise.png` | attack@420 | 青线手臂、蓝线腿 | 普攻「震地拳」起手：两只巨拳并在一起高高举过头顶，身子往后挺，腿叉开站稳 |
| 3 | `brock-pose-a_slam.png` | attack@650 | 青线手臂、蓝线腿 | 砸下：两只拳头一起狠狠砸到身前地上，身子往前压低、弓着背，膝盖弯下去 |
| 4 | `brock-pose-q_wind.png` | attack2@330 | 粉线手臂、红线腿 | 技能1「巨岩投掷」起手：上身往后拧，一只巨拳往身后高高抡起（等会儿扔出大石头），另一只拳头在身前 |
| 5 | `brock-pose-q_throw.png` | attack2@570 | 青线手臂、红线腿 | 扔出：抡起的拳头往前狠狠甩出去，手臂伸到身前，上身跟着往前拧 |
| 6 | `brock-pose-e_plant.png` | attack3@330 | 青线手臂、红线腿 | 技能2「苔藤缠握」起手：侧过身子，一只巨拳收到胸前蓄力 |
| 7 | `brock-pose-e_reach.png` | attack3@630 | 粉线手臂、红线腿 | 伸出：那只拳头往前下方猛地捅出去（树根会从地下钻向敌人），身子压低 |
| 8 | `brock-pose-r_crouch.png` | spell@0 | 粉线手臂、红线腿 | 大招「震地猛击」起跳前：深深蹲下蓄力，两只巨拳垂在身前 |
| 9 | `brock-pose-r_leap.png` | spell@360 | 青线手臂、红线腿 | 跃起：双腿蹬直往上跳，两只巨拳往两侧张开（画在地面线上，离地的高度我来加） |
| 10 | `brock-pose-r_air.png` | spell@540 | 青线手臂、蓝线腿 | 空中最高点：两只巨拳并在一起高高举过头顶，准备砸下来，两腿收起（同样画在地面线上） |
| 11 | `brock-pose-r_land.png` | spell@1080 | 青线手臂、蓝线腿 | 落地猛砸：重重落地蹲下，两只拳头一起砸进身前地面，身子深深弓下去 |
| 12 | `brock-pose-run1.png` | run@0 | 青线手臂、蓝线腿 | 跑 1：红线那条腿刚从后面抬起来往前迈，蓝线那条腿踩地；两只巨拳一前一后摆 |
| 13 | `brock-pose-run2.png` | run@166 | 青线手臂、蓝线腿 | 跑 2：红线的腿抬着往前送，到半空 |
| 14 | `brock-pose-run3.png` | run@333 | 青线手臂、红线腿 | 跑 3：红线的腿在前面落地，重心压上去 |
| 15 | `brock-pose-run4.png` | run@500 | 青线手臂、蓝线腿 | 跑 4：两脚都踩地，蓝线的腿在后面开始抬（换脚） |
| 16 | `brock-pose-run5.png` | run@666 | 青线手臂、蓝线腿 | 跑 5：蓝线的腿从后面抬起来，抬到最高 |
| 17 | `brock-pose-run6.png` | run@833 | 青线手臂、蓝线腿 | 跑 6：蓝线的腿抬着往前送，到半空 |
| 18 | `brock-pose-run7.png` | run@1000 | 青线手臂、蓝线腿 | 跑 7：蓝线的腿在前面落地 |
| 19 | `brock-pose-run8.png` | run@1166 | 青线手臂、蓝线腿 | 跑 8：两脚踩地，红线的腿在后面开始抬（8 接回 1，循环） |
| 20 | `brock-pose-d_fall.png` | death@1928 | 青线手臂、蓝线腿 | 被打倒：身子往前倒下去，两只拳头撑不住 |
| 21 | `brock-pose-d_down.png` | death@2571 | 青线手臂、蓝线腿 | 倒地：整个人脸朝下趴在地上不动，两只巨拳摊在两边，脸板和眼睛熄灭（画成暗橙褐色、不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (his soles on y 1176) - a big chunky STONE GOLEM of dark slate-teal rock blocks: TWO HUGE BOULDER FISTS on thick stone arms, BROWN ROOTS wound round his shoulders, arms and waist, BRIGHT GREEN LEAF TUFTS and a SMALL BONSAI TREE on his shoulders, a curved bark thorn, a VIOLET TRIANGULAR CRYSTAL EMBLEM on the chest, short thick stone legs, a SMALL HEAD sunk between the shoulders: a pointed GREY-BLUE STONE HOOD round a glowing ORANGE FACE PLATE with TWO YELLOW RING EYES; B his HEAD shown 8x; C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two arms and fists, the two legs, the body's and the head's angle from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two arms (shoulder to fist), RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the head, the two HUGE FISTS and the legs exactly as big as in A in EVERY pose, also when the fists go up over his head, the arms spread, he squats or he lies on the ground (the picture simply grows taller, wider or shorter - never shrink the body or the fists to fit). Each arm along its line (thick root-wound stone upper arm and forearm, the huge boulder fist at the end), bending at the elbow, never stretched, never squashed, never thinner than in A; each leg along its line (short thick stone pillar); the NEAR arm and leg in full tone and in front, the FAR ones a step darker. The leaf tufts, the bonsai tree and the thorn stay on his shoulders; the roots and the violet chest emblem stay where they are on the body.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the grey-blue hood, the orange face plate, the two yellow ring eyes) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the face plate and the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no boulder in the hand, no roots from the ground, no shockwave, no cracks in the ground, no shield, no falling rocks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_raise: `RAISE - both huge fists held together high over his head, the body leaning back, the legs apart and planted.`
- a_slam: `SLAM - both fists smashed together onto the ground in front, the body bent forward and low, the back hunched, the knees bent.`
- q_wind: `WIND-UP - the upper body twisted back, one huge fist swung far back and up behind him (about to hurl a boulder), the other fist in front.`
- q_throw: `THROW - the swung fist hurled forward, the arm reaching out in front, the upper body twisting forward after it.`
- e_plant: `GATHER - turned sideways, one huge fist drawn in before the chest, gathering.`
- e_reach: `REACH - that fist thrust forward and down (his roots will burst from the ground toward the enemy), the body low.`
- r_crouch: `CROUCH - squatting deep to jump, both huge fists hanging in front, gathering.`
- r_leap: `LEAP - the legs pushing straight up off the ground, both huge fists flung out to the sides (draw it standing on the ground line: the height of the jump is added later).`
- r_air: `TOP OF THE JUMP - both huge fists held together high over his head, ready to come down, the legs drawn up (also drawn on the ground line).`
- r_land: `LANDING SLAM - landed hard in a deep squat, both fists smashed together into the ground in front, the body bent far down.`
- run1: `RUN 1 - the RED-line leg just lifting from behind to step forward, the BLUE-line leg planted; the two huge fists swinging one forward, one back.`
- run2: `RUN 2 - the RED-line leg lifted, swinging forward, in mid-air.`
- run3: `RUN 3 - the RED-line leg coming down in front, the weight onto it.`
- run4: `RUN 4 - both feet on the ground, the BLUE-line leg starting to lift behind (the change of feet).`
- run5: `RUN 5 - the BLUE-line leg lifted from behind, at its highest.`
- run6: `RUN 6 - the BLUE-line leg lifted, swinging forward, in mid-air.`
- run7: `RUN 7 - the BLUE-line leg coming down in front.`
- run8: `RUN 8 - both feet on the ground, the RED-line leg starting to lift behind (8 runs on into 1: the loop).`
- d_fall: `FALLING - toppling forward, both fists no longer holding him up.`
- d_down: `DOWN - lying flat on his face on the ground, still, both huge fists sprawled at his sides, the face plate and the eyes gone dark (a dull dark orange-brown, no glow).`

## 交回

- 每个姿势一张：`outputs/brock-poses/brock-pose-<名字>.png`（1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/brock-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **20 张都画完再交**，最后写 `outputs/brock-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/brock_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/brock/codex_poses/`，**先量 Codex 实际的格子**（不一定是 12 px），读 raw，**每张按定稿的身体大小读**（拳头举高、两臂张开时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、两只圆环眼还在、拳头和定稿一样大、手臂和腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的手臂和腿暗一档）。
- 骨架包：`tools/art/pack_brock_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影；灰框 = 定稿的头跟着 Head 关节走；跑步按 C:/t/br_work/s/gait.py 量的一整圈取 8 帧 (0, 166, 333, 500, 666, 833, 1000, 1166) ms）；这份提示词由 `tools/art/gen_brock_pose_md.py` 生成。
