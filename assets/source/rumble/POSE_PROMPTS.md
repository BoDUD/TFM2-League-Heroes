# 机械公敌 兰博：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 兰博的造型用户已经定稿（`2_design.png` 是你第 1 步画的 B-1：3/4 正面朝右的 Q 版约德尔人坐在机甲里——蓝毛大头、亮蓝莫西干、额头上推着的红镜片金框护目镜、黄眼睛、坏笑；黄铜色带锈的敞口驾驶舱、往画面右边伸的长喷火炮管（红箍、绕着黑管子）、画面左边那条机械手臂握着的**带刺黑铁球**、背上两个红头火箭舱、短粗的黑色关节腿和红色圆盘脚）。
> - 英雄联盟里他抡铁球砸人、端着喷火炮喷火、射鱼叉、蹲下发射火箭、翻倒，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **14 个姿势**（8 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个兰博**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：**棕黄色的框 = 驾驶舱**（机甲的身子，连同坐在里面的兰博）、**红棕色的框 = 背上的火箭舱**、**灰框 = 兰博的头**；绿线 = 机身的中轴（驾驶舱底部中间往上）；**机甲是一整块硬的**：驾驶舱、驾驶员、火箭舱一起倾斜、一起移动，不变形。**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，扁的椭圆 = 红色圆盘脚；**紫线 = 握铁球的机械手臂**（定稿里在画面左边），**深色圆 = 带刺铁球**；**橙线 = 拿喷火炮的那条手臂**（定稿里在画面右边），**金色粗条 = 喷火炮管**（圆圈那头是炮口）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线、每个框对应机甲的哪一部分。
> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底约 15 格**；**机械手臂从肩膀到手约 19 格**，铁球连尖刺约 19 格宽；**拿炮的手臂从肩膀到炮的后端约 7 格**，**喷火炮管约 30 格长、6 格粗**；头（连耳朵和莫西干）31 × 27 格。骨架就是按定稿量的：**腿、手臂、炮管沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从机身长出来，不能悬空。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只黄眼睛一样高、坏笑、护目镜推在额头上、莫西干往后翘）。每个姿势都是这一个头，只跟着机身移动，**不要转头、不要画成侧脸、不要重新设计**。机甲歪了头也不歪。手臂、铁球、炮管**不要盖住脸**（眼睛、嘴）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。原版是写实比例，铁球拿在**身前**、喷火炮横在**近侧**；我们的定稿铁球在**画面左边（身后）**、炮管往**画面右边（身前）**伸——**照骨架上的位置画，不照原版的左右**，只学原版的动势（机身怎么前倾后仰、腿怎么迈、铁球怎么举起砸下、炮口指向哪里）。原版死亡时驾驶员会消失，我们的**头一直在驾驶舱上面**。

## 14 个姿势

| 图 | 文件 | 原版那一帧 | 姿势 |
|---|---|---|---|
| 3 | `rumble-pose-a_wind.png` | `rumble_attack2@240` | 抡锤起手：机械手臂把带刺铁球举过头顶（铁球在头的左上方、在头后面，不挡脸），机甲微微往后仰，喷火炮管往前下方端着，两脚分开站稳（普攻起手） |
| 4 | `rumble-pose-a_smash.png` | `rumble_attack2@400` | 砸下：机甲往前压、膝盖弯下，机械手臂往下猛砸、伸直，带刺铁球砸到地上（近侧脚前面），喷火炮管往上往后收（普攻砸中） |
| 5 | `rumble-pose-q_aim.png` | `rumble_spell1_60fps@100` | 端平喷火炮：两腿大大分开、膝盖弯下、机甲压低一格，喷火炮管端平朝正右方（准备喷火），铁球垂在左下（纵火盛宴起手） |
| 6 | `rumble-pose-q_spray.png` | `rumble_spell1_60fps@400` | 喷火中：同上，身子再往前压一点，炮管稍微往下斜（火往前喷），铁球往后摆（纵火盛宴持续） |
| 7 | `rumble-pose-e_aim.png` | `rumble_spell3@160` | 瞄准射鱼叉：机甲站直，喷火炮管抬起来，朝右方稍微往上指（射电子鱼叉），铁球垂在左边（电子鱼叉起手） |
| 8 | `rumble-pose-e_recoil.png` | `rumble_spell3@320` | 鱼叉射出的后坐：机甲往后一仰，炮管被震得往上翘，近侧脚往后退半步，铁球往前甩（电子鱼叉射出） |
| 9 | `rumble-pose-r_crouch.png` | `rumble_spell4_60fps@200` | 蓄力：机甲蹲低、往前弓，背上的火箭舱翘起来朝天，喷火炮管往前下方指着地面，铁球垂在身边（恒温灼烧起手） |
| 10 | `rumble-pose-r_launch.png` | `rumble_spell4_60fps@400` | 发射火箭：火箭射出去的后坐，机甲往上一顶、比蓄力高一格，火箭舱仍然朝天，炮管仍然指着地面，铁球往外甩，脚还踩在地上（恒温灼烧发射） |
| 11 | `rumble-pose-run1.png` | `rumble_run_60fps@0` | 跑 1（远侧腿往前迈一大步着地，近侧腿往后蹬）：机甲往前倾，炮管朝前端着，铁球往后摆 |
| 12 | `rumble-pose-run2.png` | `rumble_run_60fps@240` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬起往前）：机甲高一格，铁球垂着，炮管朝前 |
| 13 | `rumble-pose-run3.png` | `rumble_run_60fps@480` | 跑 3（近侧腿往前迈一大步着地，远侧腿往后蹬）：机甲往前倾，铁球往前摆，炮管稍微往后 |
| 14 | `rumble-pose-run4.png` | `rumble_run_60fps@720` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬起往前）：机甲高一格，铁球垂着 |
| 15 | `rumble-pose-d_drop.png` | `rumble_death@2000` | 倒下：机甲被打得往左后方仰，两腿膝盖发软，炮管朝右上方翘起，铁球甩在左边（死亡第一下） |
| 16 | `rumble-pose-d_down.png` | `rumble_death@3500` | 翻倒：机甲往左后方翻倒、仰面躺在地上（驾驶舱底朝右下、开口朝左上），两条短腿僵直地翘离地面朝右，机械手臂瘫在左边地上、铁球落在地上，炮管斜着朝右上方，驾驶员的头还在驾驶舱上面（死亡倒地） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1188) - a chibi blue-furred YORDLE with a BIG head riding a junkyard MECH: a bright blue mohawk swept back, big pointed ears, red-lensed gold-rimmed goggles pushed up on the forehead, yellow eyes, a cheeky grin, a brown leather jacket; he sits in an open rusty BRASS COCKPIT; a LONG FLAMETHROWER CANNON (brass with red bands, black hoses wound round it, a black muzzle) reaching forward to the image right; on the image left a black jointed MECHANICAL ARM with brass plates gripping a SPIKED BLACK IRON BALL (silver spikes); two ROCKET PODS with red tips on its back; short thick black jointed legs with gold gears and RED DISC FEET; B its HEAD shown 8x (31 squares wide, 27 tall); C a SKELETON on the same 1254 canvas and 12 px grid: the TAN BOX = the cockpit hull (with the pilot in it), the RED-BROWN BOX = the rocket pods, the GREY BOX = where the head goes, green = the hull's middle axis - the mech is ONE RIGID BODY: hull, pilot and pods tilt and move together, never bent; RED = the NEAR leg (image left), BLUE = the FAR leg (image right), the flat ellipses = the red disc feet; PURPLE = the MECHANICAL ARM (on the image left in A) with the DARK CIRCLE = the spiked iron ball; ORANGE = the CANNON ARM (on the image right in A) with the THICK GOLD BAR = the flamethrower cannon (the ring = its muzzle); the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the MOTION from it - how the body pitches, the legs stride, the ball rises and falls, where the muzzle points - never its 3D look, its realistic proportions or its sides: in it the ball is held in front and the cannon across the near side, ours follow the skeleton C); E (if attached) the same skeleton drawn over image A, showing which line and box is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions - each leg only about 15 squares from the hip to the sole, the mechanical arm about 19 squares from the shoulder to the hand, the spiked ball about 19 squares across, the cannon arm about 7 squares to the cannon and the cannon about 30 squares long, exactly as in image A. Draw the cockpit hull with the pilot and the rocket pods as ONE rigid piece in the tan and red-brown boxes (tilted as the boxes are, the same shape and size as in image A); each leg along its line (bending at the dots: the black joints, the gold gears, the red disc foot on its ellipse - the SAME thickness, length and colours as in image A); the mechanical arm from its shoulder along the purple line with the spiked ball on the dark circle; the cannon arm along the orange line and the cannon exactly on the gold bar, its muzzle at the ring. Never stretch or shorten a limb or the cannon, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the mohawk, the ears, the goggles on the forehead, the face to the front-right, both yellow eyes at the same height, the grin) - the same head in every pose, only moved, never turned, never tilted, never redrawn as a profile. No arm, ball or cannon covers the face (the eyes and the grin).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no fire, no flames, no smoke, no sparks, no electricity, no harpoon, no rockets in the air, no rocket trails, no shield, no dust, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide boxes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - the MACE arm raising the spiked iron ball high OVER the head (just above and behind it, on the upper left, never over the face), the mech leaning back a little, the cannon held forward and down, the feet planted apart.`
- a_smash: `SMASH - the mech pitching forward with bent knees, the MACE arm slammed down and straight so the spiked ball hits the ground by the near foot, the cannon pulled up and back.`
- q_aim: `FLAMETHROWER UP - the feet set wide apart with bent knees, the mech one square lower, the CANNON held LEVEL pointing straight to the image right (about to spray fire), the ball hanging low on the left.`
- q_spray: `SPRAYING - as above, leaning a little further forward, the cannon tipped slightly down (the fire pouring forward), the ball swung back.`
- e_aim: `HARPOON AIM - the mech upright, the CANNON raised pointing to the image right and a little up (to fire the electro-harpoon), the ball hanging on the left.`
- e_recoil: `HARPOON RECOIL - the mech kicked back, the cannon jolted up, the near foot sliding half a step back, the ball swinging forward.`
- r_crouch: `ROCKET WIND-UP - the mech crouching low and hunched forward so the rocket pods on its back point up at the sky, the CANNON pointing down at the ground ahead, the ball hanging by its side.`
- r_launch: `ROCKET LAUNCH - the kick of the rockets going off: the mech jolted up one square from the crouch, the rocket pods still pointing at the sky, the cannon still pointing at the ground ahead, the ball swung out, the feet still on the ground.`
- run1: `RUN 1 - a long stomping stride: the FAR leg reaching forward with its foot landing, the NEAR leg pushing back, the mech leaning forward, the cannon carried forward, the ball swinging back.`
- run2: `RUN 2 - the near leg under the body carrying it, the FAR knee lifted forward, the mech one square higher, the ball hanging, the cannon forward.`
- run3: `RUN 3 - a long stomping stride: the NEAR leg reaching forward with its foot landing, the FAR leg pushing back, the mech leaning forward, the ball swinging forward, the cannon a little back.`
- run4: `RUN 4 - the far leg under the body carrying it, the NEAR knee lifted forward, the mech one square higher, the ball hanging.`
- d_drop: `COLLAPSE - the mech knocked back toward the image left, both knees giving way, the cannon tipped up to the right, the ball flung out on the left.`
- d_down: `TOPPLED - the mech tipped over backward onto its back on the ground (the hull's bottom toward the lower right, its open top toward the upper left), both short legs stiff and lifted off the ground toward the right, the mace arm flopped out on the ground on the left with the ball lying there, the cannon slanting up to the right, the pilot's head still on top of the cockpit.`

## 交回前请检查

- **14 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 15 格、机械手臂约 19 格、喷火炮管约 30 格长，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个兰博：**同一个头（照图 B，脸朝右前方、两只黄眼睛一样高、坏笑、护目镜、莫西干）**、同一个驾驶舱和火箭舱（整块跟着框倾斜，不变形）、同样粗的腿和手臂、红色圆盘脚；铁球在深色圆上、炮管在金色粗条上；手臂从机身长出来，铁球、炮管没有盖住脸；着地的脚在 y 1188。
- 所有图没有特效（火焰、烟、电光、鱼叉、飞出去的火箭、护盾都不画）、没有骨架线、没有网格线、没有辅助框。

## 交付（`outputs/rumble-poses/`）

- `rumble-pose-a_wind.png`、`rumble-pose-a_smash.png`、`rumble-pose-q_aim.png`、`rumble-pose-q_spray.png`、`rumble-pose-e_aim.png`、`rumble-pose-e_recoil.png`、`rumble-pose-r_crouch.png`、`rumble-pose-r_launch.png`、`rumble-pose-run1.png`、`rumble-pose-run2.png`、`rumble-pose-run3.png`、`rumble-pose-run4.png`、`rumble-pose-d_drop.png`、`rumble-pose-d_down.png`；
- 原始生成图原样放 `outputs/rumble-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/rumble_poses_done.zip`。中间不要停，14 张都画完再交。

## 附图（压缩包 `rumble_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线、每个框对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍，连耳朵和莫西干）：每个姿势都照它逐格画 |
| `2_design.png` | 兰博定稿（每格 12 px，脚底 y 1188） |
| `3_a_wind_*` … `16_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、炮管的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_rumble.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（照英雄联盟，标签见 tools/kit/build_rumble.py）：普攻 attack = a_wind → a_smash → 定稿；纵火盛宴 skill = q_aim → q_spray（喷火时保持 q_spray，火焰由 rig_rumble.py 画进他自己的帧里）；电子鱼叉 skill2 = e_aim → e_recoil；恒温灼烧 ult = r_crouch → r_launch；破碎护盾（W）没有自己的动作（护盾是贴在他身上的图）；死亡 dead = d_drop → d_down；跑 run = run1–run2–run3–run4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
