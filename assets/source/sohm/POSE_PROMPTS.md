# 索姆：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 索姆的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，按它自己的格子读回、游戏大小 1:1：**正侧面朝右、浮在空中，长身子在身下盘成一个圈**；浅水蓝的蛇形身子，背上一条**粉色软鳍**，尾巴上一片**深绿色海草状尾鳍**；后脑和肩上一大片**青绿到深紫的鬃毛**；**金橙头冠、额头紫色宝石、两根珊瑚红鹿角（一根上有金色小星星）、粉色内耳的尖耳朵、蓝色的杏仁眼、细长的浅蓝口鼻**；两只浅蓝小前爪、两条小后腿）。
> - 请你画 **15 个姿势**（普攻 2 个 + 技能 7 个 + 死亡 2 帧 + **游动 4 帧**），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个索姆**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 8 px**，画布 **1254 × 1254**，红线是最低点（**y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都一样**：身子拉长、往上冲、平着游的姿势，身体、头、鬃毛、爪子也**和定稿一样粗、一样大**，不要为了把长身子装进画面就把整个人缩小（参考图已经按同一个比例摆好了，照它的大小画就行）。
> - **参考图（每个姿势一张 `*_ref.png`）是她在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、身子怎么弯、尾巴、爪子、头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型的头和鬃毛比定稿小，参考图里头已经放大了；**鬃毛一直照定稿那么大、那么蓬**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：**绿线 = 身子**（从后腿那里沿着身子、脖子一直到头），**橙线 = 她的左小前爪，紫线 = 她的右小前爪**（大圆点是爪子），**红线 = 左后腿，蓝线 = 右后腿**，**棕线 = 尾巴**，**粉线 / 青线 = 海草尾鳍的左右两片**，**灰框 = 头的位置**。近处是哪只小前爪，下表写了（近处的爪子、腿用全亮的颜色，远处的暗一档）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（金橙头冠、紫宝石、两根珊瑚红鹿角和金星星、尖耳朵、蓝色杏仁眼、细长口鼻）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**；眼睛一直在。`a_spit` 和 `q_send` 嘴可以微微张开，其余的嘴照定稿。
> - **身子和尾巴**：粗细一直和定稿一样，**粉色背鳍一直沿着身子的背面连成一条**，海草尾鳍一直在尾巴上（照骨架的粉线 / 青线）。**游动 4 帧的尾巴比模型短**（参考图里已经缩短了，照参考图画）。
> - **游动 4 帧（`run1`–`run4`）**：金铲铲里她**平着身子在空中往前游**，头在最前面，鬃毛往后飘，小爪收在身下，尾巴拖在后面，从 `run1` 到 `run4` 尾巴从往上翘慢慢摆平（游戏里来回播放，像波浪一样）；身子、头每帧都是同一个，只跟着骨架起伏。

## 15 个姿势

| 图 | 文件 | 片段 | 近处的小前爪 | 姿势 |
|---|---|---|---|---|
| 2 | `sohm-pose-a_rear.png` | attack@266 | 右（紫线） | 水泡弹起手：身子往上一挺拉得很长，头高高抬起 |
| 3 | `sohm-pose-a_spit.png` | attack@400 | 右（紫线） | 水泡弹：头往前一甩吐出水弹，身子在下面弯成一个钩（水弹之后单独画） |
| 4 | `sohm-pose-q_rise.png` | coil@150 | 右（紫线） | 潮涌起手：挺身往上，两只小爪收在胸前蓄力 |
| 5 | `sohm-pose-q_send.png` | coil@750 | 左（橙线） | 潮涌：整个身子往前一送，弯成一个 S，头和小爪推向前方（水浪之后单独画） |
| 6 | `sohm-pose-e_gather.png` | idle@800 | 右（紫线） | 海潮护佑起手：身子盘紧，小爪合在胸前 |
| 7 | `sohm-pose-e_push.png` | attack@533 | 右（紫线） | 海潮护佑：头往前伸，两只小爪往前一推（水盾之后单独画） |
| 8 | `sohm-pose-r_coil.png` | spell@413 | 右（紫线） | 潮汐绽放起手：身子低低盘成一圈，蓄力 |
| 9 | `sohm-pose-r_rise.png` | spell@826 | 左（橙线） | 潮汐绽放：整个身子笔直地往上冲起，头在最高处，尾巴在下面甩开 |
| 10 | `sohm-pose-r_swirl.png` | spell@1653 | 右（紫线） | 潮汐绽放收尾：在空中转一圈，尾巴绕着身子甩成一个环 |
| 11 | `sohm-pose-d_fall.png` | death@200 | 左（橙线） | 被打倒：身子一扭往下掉，鬃毛和尾巴乱甩 |
| 12 | `sohm-pose-d_down.png` | death@1800 | 右（紫线） | 倒地：盘着身子侧躺在地上（金铲铲原样） |
| 13 | `sohm-pose-run1.png` | run@900 | 右（紫线） | 移动 第 1/4 帧（金铲铲的游动：身子平着往前游，尾巴从翘起慢慢摆平；来回播放） |
| 14 | `sohm-pose-run2.png` | run@1100 | 右（紫线） | 移动 第 2/4 帧（金铲铲的游动：身子平着往前游，尾巴从翘起慢慢摆平；来回播放） |
| 15 | `sohm-pose-run3.png` | run@1300 | 右（紫线） | 移动 第 3/4 帧（金铲铲的游动：身子平着往前游，尾巴从翘起慢慢摆平；来回播放） |
| 16 | `sohm-pose-run4.png` | run@1500 | 右（紫线） | 移动 第 4/4 帧（金铲铲的游动：身子平着往前游，尾巴从翘起慢慢摆平；来回播放） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, side-on facing right, on a 1254x1254 canvas with 8 px squares (her lowest point on y 1176) - an EASTERN SEA DRAGON who always FLOATS, a long slender light aqua SERPENT BODY coiled under her, ONE CONTINUOUS PINK SPINE FIN along her back, a DARK GREEN KELP-LIKE TAIL FIN on her tail; a BIG FLOWING MANE, TEAL-GREEN TO DEEP PURPLE, over the back of her head and her shoulders; a GOLD-ORANGE CROWN with a PURPLE GEM on her forehead, TWO CORAL-RED ANTLERS (a tiny gold star on one), POINTED EARS pink inside, a BLUE ALMOND EYE, a long slender light aqua SNOUT; two little pale blue front claws and two small hind legs; B her HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, how the body bends, the tail, the claws, the head's angle from it - never its 3D shading; its head is already enlarged to image A's, its mane is smaller than image A's: keep image A's big mane); D the SKELETON of that pose, exactly over C: GREEN = the body (from the hind legs along the body and up the neck to the head), ORANGE = her LEFT little front claw, PURPLE = her RIGHT little front claw (the big dot = the claws), RED = her LEFT hind leg, BLUE = her RIGHT hind leg, BROWN = the tail, PINK / CYAN = the two halves of the kelp tail fin, GREY BOX = where the head goes, the red horizontal line = her lowest point; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 8 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; her lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the head, the mane, the claws and the legs as big and as thick as in A, where C shows them - never shrink the whole creature to fit a long or tall pose in. The body as thick as in A all along the green line, never thinner; the PINK SPINE FIN one continuous edge along the back of the body; the tail along the brown line, the kelp tail fin where the pink and cyan lines are. The little front claws and the hind legs are image A's, never longer. The near side (the near claw and leg) in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the gold-orange crown, the purple gem, the coral antlers with the gold star, the pointed ear, the blue almond eye, the long snout) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; the eye always visible; the mane always as big and full as in image A, flowing back from the head.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no water, no waves, no bubbles, no splashes, no flowers, no sparkles, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_rear: `WATER BOLT WIND UP - rising tall, the long body stretched up, the head raised high.`
- a_spit: `WATER BOLT - the head flicked forward spitting, the body curled into a hook under her (the bolt is drawn separately later).`
- q_rise: `TIDEBLOSSOM WIND UP - rearing up tall, the two little claws drawn in to her chest, gathering.`
- q_send: `TIDEBLOSSOM - the whole body thrown forward in an S, the head and the little claws pushing out in front (the wave is drawn separately later).`
- e_gather: `TIDECALLER WIND UP - the body coiled tight, the little claws together at her chest.`
- e_push: `TIDECALLER - the head reaching forward, both little claws pushing out in front (the water shield is drawn separately later).`
- r_coil: `TIDAL BLOOM WIND UP - the body curled low into a ring, gathering.`
- r_rise: `TIDAL BLOOM - the whole body shooting straight up, the head at the very top, the tail flung out below.`
- r_swirl: `TIDAL BLOOM END - turning over in the air, the tail swung round her body in a ring.`
- d_fall: `KNOCKED DOWN - twisted and dropping, the mane and the tail flung about.`
- d_down: `DOWN - lying on her side on the ground, the body loosely coiled (as in TFT).`
- run1: `SWIM frame 1 of 4 (TFT's swim: the body laid out flat swimming forward, the tail sweeping from raised to level; played forward and back).`
- run2: `SWIM frame 2 of 4 (TFT's swim: the body laid out flat swimming forward, the tail sweeping from raised to level; played forward and back).`
- run3: `SWIM frame 3 of 4 (TFT's swim: the body laid out flat swimming forward, the tail sweeping from raised to level; played forward and back).`
- run4: `SWIM frame 4 of 4 (TFT's swim: the body laid out flat swimming forward, the tail sweeping from raised to level; played forward and back).`

## 交回

- 每个姿势一张：`outputs/sohm-poses/sohm-pose-<名字>.png`（1254 × 1254、真透明背景、每格 8 px）；原始生成图原样放进 `outputs/sohm-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **15 张都画完再交**，最后写 `outputs/sohm-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/sohm_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/sohm/codex_poses/`，**先量 Codex 实际的格子**（不一定是 8 px），读 raw 原稿、按同一个身体大小读（不要用 Codex 按框缩放的成品：长身子的姿势身体会变小），按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛还在、鹿角和鬃毛大小不变、身子粗细不变、粉色背鳍连着、游动 4 帧是同一个身体）。
- 骨架包：`tools/art/pack_sohm_poses.py`（骨架是她客户端模型自己的骨骼，按动作片段的那一帧投影，yaw 80；头放大 HEAD_SCALE 1.8；游动是金铲铲 run1 平游的 4 帧，来回播放，尾巴缩到 0.7）；这份提示词由 `tools/art/gen_sohm_pose_md.py` 生成。
