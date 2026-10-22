# 海兽祭司 俄洛伊：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 俄洛伊和触手的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-2：3/4 正面朝右的 Q 版女祭司——深棕色皮肤、绿眼睛、浓眉、金鼻环、黑发高发髻套金环、辫子垂在背后，金护肩金领圈、青绿胸布、结实的手臂（画面右边那只有青绿螺旋纹身和大金护腕，拳头叉腰），金腰带、暗红腰布、灰绿布裙，墨绿高靴；画面左边那只手托着**扛在肩上的大金色神像**（圆盘，正面青绿螺旋眼，右边一排扇形金凸起）；`T0_tentacle.png` 是触手：正面、深海绿、浅青螺旋纹、背鳍、卷钩、根部碎石）。
> - 英雄联盟里她抡神像砸地、跳起来砸、把神像推出去扯灵魂、高高跃起跪地砸，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **15 个俄洛伊姿势**（11 个动作 + 4 帧跑步），再画 **7 个触手姿势**（正面），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张俄洛伊都是同一个俄洛伊**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1200**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**橙线 = 戴大金护腕、有纹身的那只手臂**（定稿里在画面右边、拳头叉腰），**紫线 = 托神像的那只手臂**（定稿里在画面左边、神像下面）；两条手臂上**大一点的圆点是手**；**灰框 = 头的位置**（头连发髻）；**半透明的金色圆盘 = 神像的位置和大小**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的腿短——**每条腿从胯到脚底约 22 格**；**戴护腕的手臂从肩膀到拳头约 19 格、托神像的约 17 格**；头连发髻 24 × 20 格；**神像直径约 21 格**（和定稿一样大，不放大不缩小）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。
> - **神像**：照定稿的神像画（金色 4 档、正面青绿螺旋眼、右边扇形凸起），**画在金色圆盘的位置，和圆盘一样大**；手放在骨架的圆点上——**手就抓在神像的边上**（两只手都碰到神像时就是双手抱着它）。神像可以按动作转一点角度，但还是那一个神像。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只绿眼睛都看得见、浓眉、金鼻环、高发髻、金环）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、神像**不要盖住脸**（眼睛、鼻环、嘴）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的俄洛伊是高大的成年人、手臂长；我们的是 Q 版大头：身子短、手臂短，**照骨架的长短和神像圆盘的位置画，不照原版的长短**（原版能把神像举过头顶，我们的手臂够不到，就照圆盘放在头旁边或身前）。原版有几帧神像上连着一条**大触手**（扯灵魂的特效），**不要画触手**，那是第 3 步的特效。

## 15 个俄洛伊姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `illaoi-pose-a_raise.png` | 抡起神像：身子往左后方仰，远侧手臂把神像高高抡到头顶后上方（神像在头的左上方，不挡脸），近侧手臂往前伸着保持平衡，前腿（远侧）往前迈一步（普攻起手） |
| 4 | `illaoi-pose-a_slam.png` | 砸下神像：身子往前压，两腿大大分开蹲下，两只手一起把神像砸在身前（画面右边）的地上，神像底边贴着地面线（普攻 / 灵魂试炼砸下） |
| 5 | `illaoi-pose-w_jump.png` | 跃起：往前上方跳起（脚离地约 12 格），两膝收起，身子前倾，两只手一起抱着神像举在胸前右边（准备砸下，神像不挡脸）（严酷训诫跳起） |
| 6 | `illaoi-pose-w_land.png` | 落地压住：深深蹲下，身子往前趴，两只手臂往前伸直，把神像按在身前（画面右边）的地上（严酷训诫落地） |
| 7 | `illaoi-pose-e_thrust.png` | 推出神像：弓步往前，两只手臂往前（画面右边）伸直，把神像举在胸前的高度推出去，神像正面的绿色螺旋眼朝着敌人；后腿（近侧）伸直，前腿（远侧）屈膝（灵魂试炼：扯出灵魂） |
| 8 | `illaoi-pose-e_yank.png` | 往回拽：身子往左后方仰，两只手把神像往胸前拽回来（手肘弯着，神像在胸口右前方），近侧腿往前撑住，像在把什么东西从敌人身上扯出来（灵魂试炼：拽出灵魂） |
| 9 | `illaoi-pose-r_crouch.png` | 蹲下蓄力：深深蹲下，两膝往外分开，身子往前弓，托神像的手把神像放低在身子左边（画面左边）靠近地面，另一只手臂垂在膝盖边，抬眼往前看（过界信仰起手） |
| 10 | `illaoi-pose-r_leap.png` | 高高跃起：往上跳得很高（脚离地约 16 格），两腿屈膝收在身下，身子微微后仰，托神像的手把神像高高举在头的左边（画面左边，不挡脸），另一只手臂往右上方扬起（过界信仰跳起） |
| 11 | `illaoi-pose-r_slam.png` | 跪地砸下：近侧膝盖跪在地上，远侧腿屈膝撑地，身子往前扑，两只手把神像狠狠砸进身前（画面右边）的地里（过界信仰落地） |
| 12 | `illaoi-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，远侧手拎着神像垂在身子左后方（画面左边、腰的高度），近侧手臂往后摆 |
| 13 | `illaoi-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，神像还拎在身侧，近侧手臂垂在身边 |
| 14 | `illaoi-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子微微前倾，神像拎在身侧，近侧手臂往前摆 |
| 15 | `illaoi-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，神像拎在身侧 |
| 16 | `illaoi-pose-d_stagger.png` | 踉跄：被打得往左后方倒，膝盖发软，两只手臂往两边甩开，神像从手里脱出去，飞在她左上方（画面左边，不挡脸）（死亡第一下） |
| 17 | `illaoi-pose-d_slump.png` | 瘫坐：一屁股坐在地上，两条腿往画面右边平伸在地上，身子往前趴下去，头低下来，两只手臂软软垂到地上；神像倒在她身后（画面左边）的地上（死亡） |

## 7 个触手姿势（正面）

| 图 | 文件 | 姿势 |
|---|---|---|
| T1 | `illaoi-tentacle-tn_rise.png` | 钻出地面：只露出下面一小截（约 25 格高），直直地往上顶，尖端还没卷，根部的石块往两边炸开（触手出现第一下） |
| T2 | `illaoi-tentacle-tn_grow.png` | 长高：长到约 50 格高，身子微微往一边弯，尖端开始卷（触手出现第二下） |
| T3 | `illaoi-tentacle-tn_sway.png` | 待机摇摆：和定稿一样高，但整条往另一边（画面右边）弯，卷钩朝画面右边卷（待机第二帧，和定稿来回摆） |
| T4 | `illaoi-tentacle-tn_rear.png` | 高高扬起：伸得又高又直（约 80 格高，比定稿高一截，粗细不变），尖端只微微弯，准备往下砸（触手抽打起手） |
| T5 | `illaoi-tentacle-tn_slam.png` | 朝前砸下：整条触手朝着看画的人砸下来——从正面看变成很矮很粗的一团（约 22 格高、比定稿宽一倍），尖端拍扁在身前的地上，根部石块被震起来（触手抽打：砸中） |
| T6 | `illaoi-tentacle-tn_recoil.png` | 弹回：从地上弹起来一半（约 40 格高），身子歪着，尖端卷起来（触手抽打收回） |
| T7 | `illaoi-tentacle-tn_sink.png` | 缩回地里：往下沉，只剩约 18 格露在地面上，尖端缩成一团，根部石块往里塌（触手消失） |

## 提示词 A：俄洛伊（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a chibi STRONG PRIESTESS with a BIG head: dark brown skin, green eyes, thick brows, a gold nose ring, black hair in a high bun with a gold ring and braids down her back; gold shoulder plates and a gold collar, a teal chest wrap with gold plates, strong bare arms - the arm on the image right with a teal spiral tattoo, a big gold bracer and its fist on her hip, the arm on the image left holding up a BIG ROUND GOLD IDOL resting on her shoulder (a thick carved gold disc with a teal spiral eye on its face and a fan of gold ridges on its right side); a gold belt, a dark red loincloth, a grey-green cloth skirt, dark green boots; B its HEAD with the bun shown 8x (24 squares wide, 20 tall); C a SKELETON on the same 1254 canvas and 12 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), ORANGE = the BRACER arm (the tattooed arm, on the image right in A), PURPLE = the IDOL arm (on the image left in A), the bigger dot on each arm = the hand, GREY BOX = where the head goes, the TRANSLUCENT GOLD DISC = where the idol goes and how big it is, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its long realistic arms and legs, or the big tentacle some of its frames show coming out of the idol); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1200.
COUNT THE SQUARES: chibi proportions - each leg only about 22 squares from the hip to the sole, the bracer arm about 19 squares from the shoulder to the fist and the idol arm about 17, the idol about 21 squares across, exactly as in image A. Lay the body along the skeleton: the torso with the chest wrap, the belt, the loincloth and the cloth skirt along the green line, each leg along its line (bending at the dots: the dark skin thigh, the dark green boot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (strong bare arms growing from the shoulders, never floating; the gold bracer on the orange one). THE IDOL: the same gold idol as in image A drawn exactly on the gold disc, the same size; each hand on its dot holds the idol's rim when the dot touches the disc (both dots on it = both hands hold it). Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both green eyes, the brows, the nose ring, the bun with its gold ring) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or idol covers the face (the eyes, the nose ring and the mouth); the braids follow the head.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no tentacles, no spirit, no shockwave, no dust, no glow, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no gold disc guide.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_raise: `WIND-UP - leaning back toward the image left, the FAR arm swinging the big gold idol up high behind and above her head (the idol over the image left, never over the face), the near arm reaching forward for balance, the front (far) leg stepping forward.`
- a_slam: `SMASH - pressing forward and down, the legs wide apart in a deep squat, BOTH hands smashing the idol into the ground in front of her (on the image right), the idol's lower edge on the ground line.`
- w_jump: `LEAP - jumping up and forward (the feet about 12 squares off the ground), both knees tucked, leaning forward, BOTH hands holding the idol up in front of her chest on the image right, ready to smash (never over the face).`
- w_land: `LAND - crouching very low, the body bent far forward, both arms stretched straight forward pressing the idol down on the ground in front of her (on the image right).`
- e_thrust: `THRUST - a lunge forward, BOTH arms stretched straight out to the image right holding the idol out at chest height, its green spiral eye facing the enemy; the back (near) leg straight, the front (far) knee bent.`
- e_yank: `YANK - leaning back toward the image left, both hands pulling the idol back toward her chest (elbows bent, the idol just in front of her chest on the image right), the near leg braced forward, as if tearing something out of the enemy.`
- r_crouch: `CROUCH - squatting deep, the knees spread apart, hunched forward, the IDOL hand holding the idol low at her side on the image left near the ground, the other arm hanging by her knee, looking ahead.`
- r_leap: `HIGH LEAP - jumping very high (the feet about 16 squares off the ground), both knees tucked under her, the body leaning back a little, the IDOL hand raising the idol high beside her head on the image left (never over the face), the other arm flung up to the upper right.`
- r_slam: `KNEELING SLAM - the near knee down on the ground, the far leg bent with its foot planted, the body lunging forward, BOTH hands slamming the idol hard into the ground in front of her (on the image right).`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back behind, leaning forward a little, the far hand carrying the idol low at her side behind her (image left, at hip height), the near arm swinging back.`
- run2: `RUN 2 - the near leg under the body carrying her, the FAR knee lifted forward, the body one square higher, the idol still carried low at her side, the near arm hanging close.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back behind, leaning forward a little, the idol carried low at her side, the near arm swinging forward.`
- run4: `RUN 4 - the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, the idol carried low at her side.`
- d_stagger: `STAGGER - knocked back toward the image left, the knees giving way, both arms flung out, the idol flying out of her hands up to the upper left (the image left, never over the face).`
- d_slump: `SLUMPED - sitting down hard on the ground, both legs stretched out flat to the image right along the ground, the body slumped forward, the head low, both arms hanging limp to the ground; the idol lying on the ground behind her on the image left.`

## 提示词 B：触手（每个姿势一次，换掉最后一段的姿势）

每次上传：`T0_tentacle.png`（定稿）、这个姿势的 `T*_league.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art TENTACLE seen from the FRONT, on a 1254x1254 canvas with 12 px squares (its root on y 1200) - a thick deep sea-green tentacle rising out of a ring of grey-brown stones, darker on its back and lighter teal-green on its belly, pale aqua spiral patterns of 1-square lines, a row of fin spikes along its back, the tip curled into a hook; B the original tentacle in this pose, seen from the front (copy the POSE from it, never its 3D look or its cyan colour).
Draw with the image generator ONE clean pixel-art picture of the tentacle of image A in the POSE of image B, still seen from the FRONT, standing in the middle of the canvas: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its root stones on y 1200. The SAME tentacle: the same thickness, colours, spiral patterns, fins and root stones, only bent, stretched or squashed as the pose says. Everything inside the canvas.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects (no splash, no dust, no shockwave, no cracks in the ground), no background, no ground, no shadow, no text, no grid lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- tn_rise: `RISING - only its lower part out of the ground (about 25 squares tall), pushing straight up, the tip not curled yet, the root stones bursting out to both sides.`
- tn_grow: `GROWING - about 50 squares tall, its body bending a little to one side, the tip starting to curl.`
- tn_sway: `SWAY - as tall as the design but the whole body bent the other way (to the image right), the hook curling to the image right (the idle's second frame, swinging with the design).`
- tn_rear: `REARING - stretched up very tall and straight (about 80 squares, taller than the design, the same thickness), the tip only a little bent, about to strike down.`
- tn_slam: `SLAMMED DOWN - the whole tentacle smashed down toward the viewer: seen from the front it is a short, thick mass (about 22 squares tall, twice the design's width), its tip flattened on the ground in front, the root stones jolted up.`
- tn_recoil: `RECOIL - springing halfway back up (about 40 squares tall), the body leaning, the tip curling up again.`
- tn_sink: `SINKING - sinking back into the ground, only about 18 squares left above it, the tip curled tight, the root stones caving in.`

## 交回前请检查

- **22 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- **数格子**：俄洛伊每条腿从胯到脚底约 22 格、戴护腕的手臂约 19 格、托神像的约 17 格、神像直径约 21 格，和定稿一样——腿画长了就重画。
- 每张俄洛伊都是定稿的同一个俄洛伊：**同一个头（照图 B，脸朝右前方、两只绿眼睛、浓眉、金鼻环、高发髻）**、同样粗的手臂和腿；神像在金色圆盘的位置、一样大，手抓在神像边上；手臂从肩膀长出来，手、神像没有盖住脸；姿势沿着骨架；着地的脚在 y 1200。
- 每张触手都是定稿的同一条触手，**正面**，粗细、颜色、螺旋纹、背鳍、根部石块都一样；不出画。
- 所有图没有特效、没有骨架线、没有网格线、没有金色圆盘辅助线。

## 交付（`outputs/illaoi-poses/`）

- `illaoi-pose-a_raise.png`、`illaoi-pose-a_slam.png`、`illaoi-pose-w_jump.png`、`illaoi-pose-w_land.png`、`illaoi-pose-e_thrust.png`、`illaoi-pose-e_yank.png`、`illaoi-pose-r_crouch.png`、`illaoi-pose-r_leap.png`、`illaoi-pose-r_slam.png`、`illaoi-pose-run1.png`、`illaoi-pose-run2.png`、`illaoi-pose-run3.png`、`illaoi-pose-run4.png`、`illaoi-pose-d_stagger.png`、`illaoi-pose-d_slump.png`；
- `illaoi-tentacle-tn_rise.png`、`illaoi-tentacle-tn_grow.png`、`illaoi-tentacle-tn_sway.png`、`illaoi-tentacle-tn_rear.png`、`illaoi-tentacle-tn_slam.png`、`illaoi-tentacle-tn_recoil.png`、`illaoi-tentacle-tn_sink.png`；
- 原始生成图原样放 `outputs/illaoi-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/illaoi_poses_done.zip`。中间不要停，22 张都画完再交。

## 附图（压缩包 `illaoi_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，金色圆盘 = 神像） |
| `1_head.png` | 定稿的头（8 倍，连发髻）：每个姿势都照它逐格画 |
| `2_design.png` | 俄洛伊定稿（每格 12 px，脚底 y 1200） |
| `3_a_raise_*` … `17_d_slump_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |
| `T0_tentacle.png` | 触手定稿（正面，每格 12 px，根部 y 1200） |
| `T1_tn_rise_league.png` … `T7_tn_sink_league.png` | 触手每个姿势的英雄联盟原版那一帧（正面） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（design_ivern_poses / design_hwei_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和神像的大小，和定稿比**（codex-legs-need-skeletons），腿长了就照艾翁的 legs 包重画腿，再拼进 rig_illaoi.py 的动作里，逐帧自查后才发合成 GIF。触手按它自己的格子读回（PPU 1.5），对到 hd/tentacle.png 的调色板。
- 动作安排（照英雄联盟，标签见 tools/kit/build_illaoi.py）：普攻 attack = a_raise → a_slam → 定稿；严酷训诫 skill = w_jump → w_land；灵魂试炼 skill2 = e_thrust → e_yank；过界信仰 ult = r_crouch → r_leap → r_slam；死亡 dead = d_stagger → d_slump；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。触手（特效图，正面）：出现 = tn_rise → tn_grow → 定稿，待机 = 定稿 ↔ tn_sway，抽打 = tn_rear → tn_slam → tn_recoil，消失 = tn_sink。
