# 泰拉：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 泰拉的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己 14 px 的格子读回，1:1 定稿，这里放大成每格 9 px：3/4 朝右，**四条腿着地趴伏**；头、脖子、肩膀和背上是**灰绿色的大块岩石甲板**（几片苔藓绿），黄色发光的眼睛，**张开的嘴和两排米白石牙**；**米白色石骨翅膀 + 橙色翼膜收在背上往后折**；红褐色的肚子、四条粗腿和深色大爪；细长的红褐色尾巴拖在左后方，**末端一簇灰绿石刺**）。每个姿势都照它。
> - 请你画 **18 个姿势**（10 个动作 + 6 帧移动 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个泰拉**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。**在空中的姿势（q_pounce、run1–run6）也画在地面线上**，游戏里我再抬高。
> - **身体大小每张都和定稿一样**：翅膀张开、尾巴翘起的时候，画面会变宽变高，**但身子、头、腿不能因此画小**（按参考图的大小画，翅膀和尾巴超出去就让它超出去，画布够大）。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置，头已经按定稿的比例放大——**姿势、四条腿、翅膀、尾巴、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 / 紫线 = 两条前腿**（大圆点是前爪；**紫线是近处的那条**），红线 / 蓝线 = 两条后腿（**蓝线是近处的**），**棕线 = 尾巴**，**青线 = 近处的翅膀，粉线 = 远处的翅膀**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（岩石眉骨、黄眼睛、两排石牙、两颊石片）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**只有嘴可以变**：`a_hit`、`q_bite`、`e_roar`、`r_roar` 张到最大（嘴里深色，石牙一颗颗分开）；眼睛不动。
> - **翅膀**：一直是定稿那两只翅膀（米白石骨、橙色翼膜），**收着的时候照定稿收在背上**；张开的姿势**照骨架的青线 / 粉线展开**：石骨一节节顺着线，翼膜挂在石骨之间，**不要比参考图更长**。近处的翅膀颜色正常，远处的暗一档。
> - **移动 6 帧（run1–run6）是一次扇翅膀**：她贴地低飞，**身体每帧都是同一个（和定稿一样的 3/4 朝右）**，四条腿收在身下，只有两只翅膀按参考图从最高扇到最低再收回来（6 接回 1）。

## 18 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `terra-pose-a_wind.png` | attack@850 | 普攻「岩爪」起手：前身抬起、头往后上方仰，翅膀半张，蓄力 |
| 3 | `terra-pose-a_hit.png` | attack@1000 | 岩爪落下：头和前身猛地往前下方压，近处的前爪往前拍下，嘴张开咬 |
| 4 | `terra-pose-q_crouch.png` | bite@150 | 技能1「裂地咬」起手：身子压低蹲伏，头贴近地面，翅膀张开，准备扑出去 |
| 5 | `terra-pose-q_pounce.png` | spell@875 | 扑出：整个身子腾空往前扑，前爪伸向前方，翅膀往后扬（画在地面线上，游戏里会抬高） |
| 6 | `terra-pose-q_bite.png` | spell@1250 | 落地猛咬：前爪落地，头低低地往前伸，嘴张到最大咬下去 |
| 7 | `terra-pose-e_spread.png` | celebration@500 | 技能2「龙威咆哮」起手：前身抬起，两只翅膀往上张开 |
| 8 | `terra-pose-e_roar.png` | celebration@1250 | 咆哮：头仰起来、嘴张到最大朝天咆哮，翅膀高高张开 |
| 9 | `terra-pose-r_rear.png` | spell@500 | 大招「地震」抬身：后腿撑地、前身高高立起，前爪离地，翅膀往上扬（三踏每一踏都从这里开始） |
| 10 | `terra-pose-r_stomp.png` | spell@1125 | 重踏：前爪重重踏在地上，身子往下一沉，头低下，翅膀往下压 |
| 11 | `terra-pose-r_roar.png` | spell@1625 | 地震结束：蹲伏着张大嘴咆哮，翅膀收拢一半（之后岩甲发光） |
| 12 | `terra-pose-run1.png` | run@0 | 移动（贴地低飞）1：翅膀高高往上扬，身子保持待机的 3/4 朝右，四条腿收在身下 |
| 13 | `terra-pose-run2.png` | run@146 | 飞 2：翅膀在最高处 |
| 14 | `terra-pose-run3.png` | run@292 | 飞 3：翅膀往两边平平展开 |
| 15 | `terra-pose-run4.png` | run@438 | 飞 4：翅膀往下扇 |
| 16 | `terra-pose-run5.png` | run@584 | 飞 5：翅膀扇到最低 |
| 17 | `terra-pose-run6.png` | run@876 | 飞 6：翅膀收回往上抬（6 接回 1，循环就是扇翅膀） |
| 18 | `terra-pose-d_fall.png` | death@1000 | 被打倒：身子往一边歪倒砸向地面，一只翅膀翘起 |
| 19 | `terra-pose-d_down.png` | death@7500 | 倒地：趴在地上，头垂在地面，翅膀瘫在背上（金铲铲原样） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (her soles on y 1176) - a big FOUR-LEGGED EARTH DRAGON crouched on all fours: her head, neck, shoulders and back covered in BIG GREY-GREEN ROCK PLATES (a few moss-green patches), GLOWING YELLOW EYES, an open mouth with TWO ROWS OF CREAM STONE FANGS; CREAM STONE-BONED WINGS with ORANGE MEMBRANES folded back over her back; a reddish-brown belly, four thick reddish-brown legs with big dark claws; a thin reddish-brown tail trailing to the back left, ending in a fan of grey-green STONE SPIKES; B her HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be, its head already grown to image A's share (copy the POSE, the four legs, the wings, the tail, the body's and the head's angle from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE and PURPLE = her front legs (the big dot = the front paw; purple is the NEAR one), red / blue = her hind legs (blue is the NEAR one), BROWN = the tail, CYAN = the NEAR WING, PINK = the FAR WING, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her lowest point on y 1176 (a pose in the air is drawn standing on that line too).
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when the wings spread or the tail rises (the picture simply grows wider or taller - never shrink the body to fit). Each leg along its line, bending at the joints, never stretched, never thinner than in A. The WINGS are always image A's two wings (cream stone bones, orange membranes) - folded on her back where C shows them folded, spread along the CYAN and PINK lines where D draws them, the stone bones jointed along the line and the membrane between them (never longer than in C). The tail along the brown line with its stone-spike fan at the end. The near side in full tone, the far side (the far legs, the far wing) a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the rock brow plates, the yellow eye, the two rows of stone fangs, the cheek shards) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; only the MOUTH may open wider where the pose says so (dark inside, every fang a separate square).
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no quake, no cracks, no flying rocks, no dust, no wind, no motion lines, no glow), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND UP - the front of the body lifted, the head drawn back and up, the wings half open, gathering.`
- a_hit: `STRIKE - the head and the front of the body slammed forward and down, the near front claw raking forward, the jaw open snapping.`
- q_crouch: `CROUCH - the body pressed low, the head down near the ground, the wings open, about to pounce.`
- q_pounce: `POUNCE - the whole body leaping forward off the ground, the front claws reaching ahead, the wings swept back (drawn standing on the ground line: the game lifts it).`
- q_bite: `BITE - landing on the front claws, the head low and thrust forward, the jaw open as wide as it goes, biting down.`
- e_spread: `SPREAD - the front of the body rising, both wings opening upwards.`
- e_roar: `ROAR - the head thrown up, the jaw wide open roaring at the sky, the wings spread high.`
- r_rear: `REAR UP - on the hind legs, the front of the body raised high, the front claws off the ground, the wings up (every one of the three stomps starts here).`
- r_stomp: `STOMP - the front claws slammed down hard on the ground, the body sinking, the head low, the wings pushed down.`
- r_roar: `QUAKE ROAR - crouched, the jaw wide open roaring, the wings half folded (her rock armour glows after it).`
- run1: `FLY 1 - the wings raised high, the body as in the idle (3/4 facing right), the four legs tucked under her.`
- run2: `FLY 2 - the wings at the top of the beat.`
- run3: `FLY 3 - the wings spread out level.`
- run4: `FLY 4 - the wings beating down.`
- run5: `FLY 5 - the wings at the bottom of the beat.`
- run6: `FLY 6 - the wings coming back up (6 runs on into 1: the beat loops).`
- d_fall: `FALLING - the body crashing over to one side onto the ground, one wing sticking up.`
- d_down: `DOWN - lying flat on the ground, the head resting on the ground, the wings slumped on her back (as in TFT).`

## 交回

- 每个姿势一张：`outputs/terra-poses/terra-pose-<名字>.png`（1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/terra-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **18 张都画完再交**，最后写 `outputs/terra-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/terra_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/terra/codex_poses/`，**先量 Codex 实际的格子**（不一定是 9 px），读 raw，**每张按定稿的身体大小读**（翅膀张开时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛还在、翅膀石骨和翼膜连着、身体大小不变、腿没有被压扁或拉长、移动 6 帧是同一个身体、远处的腿和翅膀暗一档）。
- 骨架包：`tools/art/pack_terra_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影；头放大 1.7 倍到定稿的比例；飞行 6 帧的身体用待机的变换，翅膀和腿是飞行的；张开的翅膀缩到 0.6）；这份提示词由 `tools/art/gen_terra_pose_md.py` 生成。
