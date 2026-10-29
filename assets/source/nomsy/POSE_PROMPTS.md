# 诺姆希：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 诺姆希的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，按它自己的格子读回，1:1 定稿：3/4 朝右，**四肢着地蹲坐**；粉色大圆肚子、粉色的脸、额头深紫花纹带、绿眼睛、微张的地包天大嘴和白獠牙、头顶三根紫刺；深紫蓝的背鳞和紫色背刺、四条短粗腿；**近处的翅膀从背上往画面左边伸出去，末端是月牙形的紫红翼膜；远处的翅膀在头后面往右上方翘起；短粗的尾巴带四根小刺，在后腿后面**——这是你第 0 步纠正过的结构，每个姿势都照它）。
> - 请你画 **20 个姿势**（10 个动作 + 8 帧移动 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个诺姆希**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 7 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。**在空中的姿势（q_roar、r_up、r_fly1、r_fly2）也画在地面线上**，游戏里我再抬高。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、四条腿、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。参考图里**舌头已经收回嘴里**（金铲铲的普攻会把舌头甩出去一个身子长，我们不要）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**橙线 / 紫线 = 两条前腿**（大圆点是前爪；**紫线是近处的那条**），红线 / 蓝线 = 两条后腿（**蓝线是近处的**），**棕线 = 短尾巴**，**青线 = 近处的翅膀，粉线 = 远处的翅膀**；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（三根紫刺、额头花纹带、绿眼睛、白獠牙、地包天的嘴）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**只有嘴可以变**：`a_spit`、`q_rise`、`q_roar`、`e_breath` 张大嘴（里面橙红色，舌头在嘴里），`e_back` 闭嘴鼓气；眼睛和獠牙不动。
> - **翅膀**：一直是定稿那两只翅膀（深紫的翼骨、紫红的翼膜、月牙形的末端），**长度和定稿一样，不要变长**。收着的姿势照定稿收在背上；`q_roar` 照参考图张开一点；**`r_up`、`r_fly1`、`r_fly2` 三个盘旋姿势参考图里没有翅膀**（模型的翅膀在这个角度会缩到身后）：**按骨架的青线 / 粉线把定稿的两只翅膀展开**——`r_up` 两只都高高往上扬，`r_fly1` 向两边平平展开，`r_fly2` 往下扇到最低；三张的身体一样，只有翅膀不同（连起来就是扇翅膀）。
> - **移动 8 帧（run1–run8）是一整个循环**：身体每帧都是同一个，只有四条腿和身体高低按参考图变；**近处的腿（紫、蓝）颜色正常，远处的腿（橙、红）暗一档**，前后两对腿要看得出交替。

## 20 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `nomsy-pose-a_rear.png` | attack@335 | 普攻起手：后腿撑着、上身抬起往后仰，头抬高，嘴巴闭着蓄力 |
| 3 | `nomsy-pose-a_spit.png` | attack@558 | 吐小火团：头猛地往前伸，嘴张大（舌头留在嘴里，不要伸出来；火团之后单独画） |
| 4 | `nomsy-pose-q_rise.png` | spell@120 | 火球！起手：后腿蹬地、整个身子立起来，头朝天张嘴大吼 |
| 5 | `nomsy-pose-q_roar.png` | spell@362 | 火球！跳在空中：身子蜷着、翅膀张开，张嘴朝前上方喷出火球（画在地面线上，游戏里会抬高） |
| 6 | `nomsy-pose-e_back.png` | attack@223 | 龙息起手：上身抬起、头往后仰到最高，胸口鼓起来吸气 |
| 7 | `nomsy-pose-e_breath.png` | attack@670 | 龙息：头低下来往前伸，嘴张到最大往前喷（火焰之后单独画） |
| 8 | `nomsy-pose-r_up.png` | celebration@3250 | 龙神飞升起飞 / 扇翅 1：在空中，两只翅膀高高举起（往上扬到最高），四条小短腿垂着（画在地面线上，游戏里会抬高） |
| 9 | `nomsy-pose-r_fly1.png` | celebration@3550 | 盘旋 / 扇翅 2：两只翅膀向两边平平展开 |
| 10 | `nomsy-pose-r_fly2.png` | celebration@4000 | 盘旋 / 扇翅 3：两只翅膀往下扇到最低（扇翅 1→2→3→2 循环就是扇翅膀） |
| 11 | `nomsy-pose-r_land.png` | celebration@4162 | 落地：四脚落地、身子一沉，翅膀正在收起 |
| 12 | `nomsy-pose-run1.png` | run@0 | 移动 1：摇摇摆摆地往前蹦 |
| 13 | `nomsy-pose-run2.png` | run@75 | 移动 2 |
| 14 | `nomsy-pose-run3.png` | run@150 | 移动 3 |
| 15 | `nomsy-pose-run4.png` | run@225 | 移动 4 |
| 16 | `nomsy-pose-run5.png` | run@300 | 移动 5 |
| 17 | `nomsy-pose-run6.png` | run@375 | 移动 6 |
| 18 | `nomsy-pose-run7.png` | run@450 | 移动 7 |
| 19 | `nomsy-pose-run8.png` | run@525 | 移动 8 |
| 20 | `nomsy-pose-d_fall.png` | death@249 | 被打倒：被打得往后一仰、身子立起来、两只前爪乱抓 |
| 21 | `nomsy-pose-d_down.png` | death@749 | 倒地：翻倒、四脚朝天躺在地上（金铲铲原样） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 7 px squares (her feet on y 1176) - a CHUBBY BABY DRAGON sitting on all fours: a HUGE ROUND PINK BELLY, a pink face with a dark purple forehead band, green eyes, a wide underbite mouth slightly open with white tusks, three purple spikes on her head; dark violet-blue scaly back with purple spikes, four short stubby legs; her NEAR WING reaches from her back out to the image left, ending in a crescent magenta membrane; her FAR WING rises behind her head to the upper right; a SHORT THICK TAIL with four small spikes behind the hind legs; B her HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the body's and the head's angle from it - never its 3D shading; its tongue is pulled back into the mouth; in the three hover poses it shows no wings); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), ORANGE and PURPLE = her front legs (the big dot = the front paw; purple is the NEAR one), red / blue = her hind legs (blue is the NEAR one), BROWN = the short tail, CYAN = the NEAR WING, PINK = the FAR WING, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 7 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her lowest point on y 1176 (a pose in the air is drawn standing on that line too).
THE SAME BULK AS IMAGE A: the belly as big and round as in A, the legs as short and thick, the body where C shows it. Each leg along its line, bending at the knee, never stretched, never thinner than in A. The WINGS are always image A's two wings at image A's length (dark violet bones, magenta membranes, crescent ends) - folded on her back where C shows them folded, spread along the CYAN and PINK lines where D draws them (never longer than in A). The short spiky tail along the brown line. The near side in full tone, the far side (the far legs, the far wing) a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the three head spikes, the forehead band, the green eyes, the white tusks) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; only the MOUTH may open wider where the pose says so (orange-red inside, the tongue inside the mouth).
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no fire, no fireball, no smoke, no sparks, no wind, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_rear: `REAR BACK - on her hind legs, the upper body lifted and leaning back, the head high, the mouth shut, gathering a breath.`
- a_spit: `SPIT - the head thrust forward, the mouth WIDE OPEN (the tongue stays inside the mouth, not lashed out; the fire is drawn separately later).`
- q_rise: `RISE - pushing off the hind legs, the whole body upright, the head up to the sky, the mouth open in a roar.`
- q_roar: `LEAP - up in the air, the body curled, the wings open, the mouth open towards the upper front throwing the fireball (drawn standing on the ground line: the game lifts it).`
- e_back: `INHALE - the upper body raised, the head thrown back as far as it goes, the chest puffed up.`
- e_breath: `BREATHE - the head lowered and stretched forward, the mouth open as wide as it goes, breathing forward (the flame is drawn separately later).`
- r_up: `WINGS UP - in the air, both wings raised high (the top of the beat), the four stubby legs hanging (drawn on the ground line: the game lifts it).`
- r_fly1: `WINGS LEVEL - the same hover, both wings spread out level to the sides.`
- r_fly2: `WINGS DOWN - the same hover, both wings beaten down to the bottom (UP -> LEVEL -> DOWN -> LEVEL loops the flapping).`
- r_land: `LANDING - down on all fours, the body sinking with the impact, the wings folding.`
- run1: `WADDLE 1 - hopping forward in a waddle.`
- run2: `WADDLE 2.`
- run3: `WADDLE 3.`
- run4: `WADDLE 4.`
- run5: `WADDLE 5.`
- run6: `WADDLE 6.`
- run7: `WADDLE 7.`
- run8: `WADDLE 8.`
- d_fall: `KNOCKED BACK - thrown back, the body upright, the front claws flailing.`
- d_down: `DOWN - rolled over, lying on her back with all four feet in the air (as in TFT).`

## 交回

- 每个姿势一张：`outputs/nomsy-poses/nomsy-pose-<名字>.png`（1254 × 1254、真透明背景、每格 7 px）；原始生成图原样放进 `outputs/nomsy-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **20 张都画完再交**，最后写 `outputs/nomsy-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/nomsy_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/nomsy/codex_poses/`，**先量 Codex 实际的格子**（不一定是 7 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、翅膀长度不变、肚子大小不变、腿没有被压扁或拉长、移动 8 帧是同一个身体、远处的腿暗一档）。
- 骨架包：`tools/art/pack_nomsy_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影；舌头收回，盘旋三帧的身体用待机的朝向、翅膀是按定稿长度画的方向线 WING_LINES）；这份提示词由 `tools/art/gen_nomsy_pose_md.py` 生成。
