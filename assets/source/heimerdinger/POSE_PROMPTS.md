# 大发明家 黑默丁格：A 包 全身动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写，也不要把大图平滑缩小。**
> - 黑默丁格的造型用户已经定稿（`0_design.png`：3/4 正面朝右的约德尔老教授，一大团金黄色头发、红框青蓝镜片护目镜、白色八字胡、墨绿灰长外套配黄铜 H 带扣、黑靴子，近侧手（画面左）拿橙色多功能工具，远侧手（画面右）拿灰绿扳手）。
> - 英雄联盟里他的跑步、普攻、待机里摆弄工具、死亡都是**全身动作**——一蹦一跳地跑、抬腿踢一下再用扳手往前戳、把工具拿到胸前摆弄、背包炸开往后倒——这些靠挪动定稿本身的部件摆不出来，所以请你画 **15 个姿势，每个一张图**。
> - **每张图都是同一个黑默丁格**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1200**），网格从画布左上角对齐。
> - **粗稿**（每个姿势一张 `b*_rough.png`）是我用定稿自己的部件按英雄联盟那一帧摆出来的：**头、身体、两只手和工具、两只靴子的大小和位置都是对的**，但接缝是坏的——袖子和腿只是一条色带，工具是粗糙转过去的。请照粗稿的大小和位置、照英雄联盟那一帧（`b*_league.png`）的动作，**重新画干净**。
> - **头一格一格照 `1_head.png` 画在粗稿里头的位置**（连头发、耳朵、护目镜、胡子、放大镜支架 50 × 38 格，同样朝右前方、两只护目镜都看得见）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手、工具**不要盖住护目镜**。
> - **他的腿很短**：外套下摆下面直接就是靴子（从外套下摆到鞋底只有 5 格左右）。跑步腾空时膝盖收起来，靴子往上提到外套下摆附近；**不要画出比定稿长的腿**，不要把腿拉长成英雄联盟模型的比例。
> - 两件工具的大小、颜色和定稿一样（多功能工具约 9 × 11 格，扳手约 13 × 10 格），**工具的朝向照英雄联盟那一帧**。手臂从肩膀长出来，袖子是外套的墨绿灰，袖口橙色，紫色手套握着工具，不能悬空。
> - 近侧（画面左边）的腿和手全亮，远侧（画面右边）暗一档。

## 15 个姿势

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| b2 | `heimerdinger-pose-run1.png` | **跑步 1**：腾空，一侧膝盖抬到身前，两只手往两边甩开 | 跑 |
| b3 | `heimerdinger-pose-run2.png` | **跑步 2**：落地，身子压低，前脚着地、后脚在身后 | 跑 |
| b4 | `heimerdinger-pose-run3.png` | **跑步 3**：蹬地往上跳，另一侧膝盖往前提 | 跑 |
| b5 | `heimerdinger-pose-run4.png` | **跑步 4**：腾空最高点，扳手往前平指，多功能工具甩到身后下方 | 跑 |
| b6 | `heimerdinger-pose-run5.png` | **跑步 5**：往下落，前脚往前伸准备着地 | 跑 |
| b7 | `heimerdinger-pose-run6.png` | **跑步 6**：另一只脚落地，身子压低 | 跑 |
| b8 | `heimerdinger-pose-run7.png` | **跑步 7**：蹬地往上跳，膝盖往前提 | 跑 |
| b9 | `heimerdinger-pose-run8.png` | **跑步 8**：腾空，两手张开 | 跑 |
| b10 | `heimerdinger-pose-attack1.png` | **普攻 1**：蓄力，远侧腿往前抬起，扳手举到肩膀高，多功能工具往后下方拉 | 普攻 |
| b11 | `heimerdinger-pose-attack2.png` | **普攻 2**：远侧脚往前一跨踩地，身子往前，扳手往前一戳（放电） | 普攻出手 |
| b12 | `heimerdinger-pose-attack3.png` | **普攻 3**：顺势往前探身压低，扳手指着前方，近侧腿往后伸 | 普攻收势 |
| b13 | `heimerdinger-pose-tinker.png` | **待机 摆弄工具**：多功能工具拿到胸前（在胡子下面，不挡脸），扳手往上抬一点 | 待机 |
| b14 | `heimerdinger-pose-death1.png` | **死亡 1**：中招一缩，头往前低，两手往两边张开；**背包炸开**：身后左边露出背包的大圆引擎（橄榄绿圆筒、红色边、一个喷口），头顶后面弹出机械臂抓着火箭（照 `b14_death1_league.png`） | 死亡 |
| b15 | `heimerdinger-pose-death2.png` | **死亡 2**：整个人往后仰倒约 45 度，脚离地，两手往上甩；机械臂的零件和火箭往上飞散 | 死亡 |
| b16 | `heimerdinger-pose-death3.png` | **死亡 3**：仰面躺在地上，头朝画面左边、靴子朝右上翘起，背后压着背包的大圆引擎；旁边地上散着两三个机械臂零件和多功能工具 | 死亡（最后一帧） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `b*_rough.png`、这个姿势的 `b*_league.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a short old yordle inventor seen 3/4 from the front, facing right: a huge spiky mane of golden-yellow hair, a big pointed orange ear, red-rimmed goggles with cyan lenses, a bushy white moustache, a small red-rimmed magnifying lens on a stalk above the mane, a dark green-grey academy long coat with gold buttons and a brass H buckle, short black boots right under the coat, an orange hextech multitool in his near hand (image left) and a grey-green wrench with a red ball in his far hand (image right), purple gloves; B his HEAD (the mane, the ear, the goggles, the moustache, the lens on its stalk) shown 8x, 50 squares wide and 38 tall; C a ROUGH of this pose on the same canvas and grid: the design's own pieces moved to the pose - the SIZE and the PLACE of the head, the coat, each hand with its tool and each boot are right, but the joins are broken (the sleeves and the legs are plain bands, the tools roughly turned); D the original character in this pose, 3/4 view facing right (copy the POSE from it - the bends of the arms and the legs, the tools' angles - never its 3D look or its proportions).
Draw with the image generator ONE clean pixel-art picture of the character of image A in this pose: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; the boots that touch the ground on y 1200.
Put everything where the rough C has it and redraw it clean in the look of image A: the coat with its buttons, buckle and orange hem; each arm from its shoulder (dark green-grey sleeve, orange cuff, purple glove) holding its tool at the angle of image D, the tools the SAME size and colours as in image A; the legs SHORT like image A - the boots right under the coat's hem (about 5 squares from the hem to the sole), the knees tucked up when he jumps - never longer legs than image A. The near side (image left) in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE where the rough has the head (the face to the front-right, both goggles visible) - the same head in every pose, only moved, never turned, never redrawn; no hand or tool covers the goggles.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no sparks, no lightning, no smoke, no explosion glow), no background, no ground, no shadow, no text, no grid lines.
THE POSE: <one line from the list below>
```

最后一段，按姿势换（英文）：

- run1: `THE POSE: running, in the air - one knee tucked up in front, the other leg pushing back, both arms swung out to his sides.`
- run2: `THE POSE: running, landing - the front boot on the ground, the body low, the back leg behind.`
- run3: `THE POSE: running, pushing off upward - the other knee lifting in front.`
- run4: `THE POSE: running, at the top of the hop - the wrench pointed straight forward, the multitool swung down behind him.`
- run5: `THE POSE: running, coming down - the front boot reaching forward to land.`
- run6: `THE POSE: running, landing on the other boot - the body low.`
- run7: `THE POSE: running, pushing off upward - the knee lifting in front.`
- run8: `THE POSE: running, in the air - both arms open.`
- attack1: `THE POSE: the attack's wind-up - his far leg lifted forward, the wrench raised to shoulder height, the multitool pulled back and down.`
- attack2: `THE POSE: the attack's jab - the far boot planted a step forward, the body forward, the wrench jabbed straight forward.`
- attack3: `THE POSE: following through - leaning forward and low, the wrench pointing ahead, the near leg stretched behind.`
- tinker: `THE POSE: tinkering - the multitool held up at his chest under the moustache (never over the goggles), the wrench raised a little.`
- death1: `THE POSE: hit and recoiling - the head ducked forward, both arms flung out; his backpack bursts open: behind him on the image left the backpack's big round engine shows (an olive drum with a red rim and a nozzle), and above the back of his head a mechanical crane arm pops up holding a rocket (as image D).`
- death2: `THE POSE: falling over backwards, tipped back about 45 degrees, the boots off the ground, both arms flung up; pieces of the crane arm and the rocket flying up and away.`
- death3: `THE POSE: lying on his back on the ground, the head to the image left, the boots up to the image right, the backpack's big round engine under his back; two or three broken crane parts and the multitool lying on the ground beside him.`

## 交回前请检查

- **全部是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px，和 `0_design.png` 一样大**（站着的姿势从头发顶到鞋底约 54 格）。
- 头和 `1_head.png` 一格一格一样，两只护目镜都看得见，没被手或工具挡住。
- 腿和定稿一样短，靴子就在外套下摆下面；工具大小颜色和定稿一样，朝向照英雄联盟那一帧。
- 外描边连续；没有任何特效。

## 交付（`outputs/heimerdinger-poses/`）

- 15 张 `heimerdinger-pose-<名字>.png`（run1–run8、attack1–attack3、tinker、death1–death3）；原始生成图原样放 `outputs/heimerdinger-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/heimerdinger_poses_done.zip`。中间不要停，15 张都画完再交。**不要另做平滑缩小的"修复版"**。

## Claude 收到后（给 Claude 看）

- 量格子（约 12 px），从 raw/ 按格读回（regrid），**把 `hd/idle.png` 的头一格一格贴回 Codex 的头的位置**（一张脸用在所有帧），颜色收回定稿的调色板，腿长和靴子在 8 倍下和定稿逐帧对照（`codex-legs-need-skeletons`），再拼进 `rig_heimerdinger.py` 的 run / attack / idle / dead；Q、E、R、W 的身体用定稿，机械臂和 R 道具来自 B 包（`CRANE_PROMPTS.md`）。
