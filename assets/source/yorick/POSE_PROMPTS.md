# 牧魂人 约里克：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 约里克的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A-2 修订稿：3/4 正面朝右的 Q 版掘墓人——深紫色大兜帽、兜帽里灰蓝色的脸、两只青色发光的眼睛、灰白山羊胡；肩后巨大的暗青绿钢肩甲、墨绿背心、胸前青色灯瓶、青钢带扣的宽腰带、深色长裤、黑靴钢护腿、垂到小腿的破烂深紫斗篷；灰蓝色的粗胳膊、深钢护腕；画面左边那只手竖握着**和他一样高的长柄铲子**——上端长矛一样的尖头带两条绿坠子，下端盾牌形的青钢铲头，铲头杵在地上；画面右边那只手空着、垂在大腿边）。
> - 英雄联盟里他抡铲子砸人、高举铲子砸地、把铲子插进地里召唤、扔出黑雾、举铲召唤室女，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **17 个姿势**（11 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个约里克**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 握铲子的那只手臂**（定稿里在画面左边），**橙线 = 空着的那只手臂**（定稿里在画面右边、垂着）；两条手臂上**大一点的圆点是手**；**灰框 = 头的位置**（兜帽连脸）；**棕色粗线 + 两头的青色形状 = 铲子**（大的盾形 = 铲头，小的 = 上端尖头）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的腿短——**每条腿从胯到脚底约 22 格**；**空着的手臂从肩膀到拳头约 30 格、握铲的约 29 格**；头（兜帽连脸）20 × 24 格；**铲子从尖头到铲头约 83 格长**（和定稿一样长，铲头约 16 格宽、24 格长，不放大不缩短）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；肩甲、斗篷跟着身子走。
> - **铲子**：照定稿的铲子画（深色木柄、青钢盾形铲头和尖头、两条绿坠子），**画在骨架上棕线和青色形状的位置，一样长、一样朝向**；手放在骨架的圆点上——**手就握在铲柄上**（两只手的圆点都在铲柄上时就是双手握着）。有几张铲柄从兜帽后面穿过去（`q_raise` 的尖头那一端），那就画在兜帽**后面**，被头挡住。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、兜帽、两只青色发光的眼睛一样高、灰白山羊胡）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、铲子**不要盖住脸**（眼睛、胡子）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右；原版的斗篷是布料模拟、渲染不出来，所以图里没有斗篷——**我们的要画斗篷**，跟着身子垂下、摆动），**动作照它**，长相照定稿。英雄联盟的约里克是高大的成年人、手臂长，能把铲子平着抡过头顶；我们的是 Q 版大头：手臂短、铲子很长，**照骨架的长短和铲子的位置画，不照原版的长短**（原版平着抡的地方，骨架把铲子斜着放，好让整把铲子留在画布里）。

## 17 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `yorick-pose-a_wind.png` | 抡铲起手：身子往左后方仰，两只手握着铲柄上段，把铲子往左上方高高抡到身后（铲头在画面左上方，不挡脸），两腿分开站稳（普攻起手） |
| 4 | `yorick-pose-a_smash.png` | 砸下：身子往前压，弓步蹲低，两只手握着铲柄中段，把铲头狠狠砸在身前（画面右边）的地上，铲柄从左上方斜下来（普攻砸中） |
| 5 | `yorick-pose-q_raise.png` | 高举铲子：身子挺直往后仰，两只手把铲子高高举过头顶，铲头甩到左后上方（画面左上，不挡脸），近侧腿往前迈一步（临终仪式起手） |
| 6 | `yorick-pose-q_slam.png` | 重重砸地：弓步蹲得更低，身子往前扑，两只手握在铲柄下段，把铲头整个砸进身前（画面右边）的地里（临终仪式砸中） |
| 7 | `yorick-pose-w_raise.png` | 竖举铲子：站直，两只手一上一下握住铲柄，把铲子竖着高高举在身前（铲头朝上、高过头顶，尖头朝下），准备往地上插（暗灵缠身 / 唤醒起手） |
| 8 | `yorick-pose-w_slam.png` | 插地蹲下：深深蹲下，两只手握着铲柄把铲头往下插进身前的地里（铲子竖直，铲头贴着地面线），头低一点往前看（暗灵缠身 / 唤醒） |
| 9 | `yorick-pose-k_call.png` | 召唤：空着的那只手高高举起、五指张开（召唤雾行者），握铲的手把铲子斜着垂在身后左下方（铲头在画面左下），身子挺直（唤醒雾行者） |
| 10 | `yorick-pose-e_wind.png` | 扔雾起手：身子往左后方扭，空着的那只手往后下方甩（准备扔出黑雾），握铲的手把铲子斜举在身后左上方，两腿分开（哀伤之雾起手） |
| 11 | `yorick-pose-e_throw.png` | 扔出黑雾：身子往前压，空着的那只手往前（画面右边）甩出去、手臂伸直、手掌张开，握铲的手把铲子斜在身后，后腿蹬直（哀伤之雾扔出） |
| 12 | `yorick-pose-r_raise.png` | 高举召唤：踮起脚、身子往上挺，两只手把铲子高高举过头顶（铲头朝左上、斜着），仰头（海屿悼词起手） |
| 13 | `yorick-pose-r_plant.png` | 立铲：站得笔直，空着的那只手握住铲柄，把铲子竖着立在身前右边（铲头着地），另一只手臂垂在身边（海屿悼词：室女升起） |
| 14 | `yorick-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，握铲的手拎着铲子斜在身侧（铲头在画面左下、离地），空着的手臂往后摆 |
| 15 | `yorick-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，铲子还斜拎在身侧，空着的手臂垂在身边 |
| 16 | `yorick-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子微微前倾，铲子斜拎在身侧，空着的手臂往前摆 |
| 17 | `yorick-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，铲子斜拎在身侧 |
| 18 | `yorick-pose-d_drop.png` | 倒下：被打得往左后方倒，膝盖发软，两只手臂往两边甩开，铲子从手里脱出去往左边倒（不挡脸）（死亡第一下） |
| 19 | `yorick-pose-d_float.png` | 飘起：身体离地飘在空中（脚离地约 12 格），身子微微往前弓，头低下，两只手臂软软垂着，两腿垂下、膝盖微弯；铲子平躺在他下方的地上（死亡：灵魂飘起） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (soles on y 1188) - a chibi HUGE GRIM GRAVEDIGGER with a BIG head: a deep purple HOOD, a grey-blue face inside it with TWO GLOWING CYAN EYES and a grey-white goatee; a giant dark teal-green coffin-lid steel PAULDRON rising behind both shoulders, a near-black dark green vest, a small glowing cyan vial on his chest, a wide belt with a teal steel buckle, dark trousers, black boots with steel shin plates, a ragged dark purple CLOAK hanging to his calves; thick bare grey-blue arms with dark steel bracers; the arm on the image left holding upright a LONG-HANDLED SHOVEL as tall as he is (a dark wooden haft, a spear-like steel point with two green tassels on top, a shield-shaped teal steel SPADE at the bottom, planted on the ground), the arm on the image right empty, hanging by his thigh; B its HEAD in the hood shown 8x (20 squares wide, 24 tall); C a SKELETON on the same 1254 canvas and 11 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the SHOVEL arm (on the image left in A), ORANGE = the FREE arm (on the image right in A), the bigger dot on each arm = the hand, GREY BOX = where the head goes, the BROWN THICK LINE with a TEAL SHAPE at each end = where the shovel goes (the big shield shape = the spade, the small one = the point), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long realistic arms; its cloak is missing in the render - ours has the cloak); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions - each leg only about 22 squares from the hip to the sole, the free arm about 30 squares from the shoulder to the fist and the shovel arm about 29, the shovel about 83 squares from the point to the spade's tip, exactly as in image A. Lay the body along the skeleton: the torso with the vest, the vial and the belt along the green line, the pauldron and the cloak riding on the shoulders and hanging with the body, each leg along its line (bending at the dots: the dark trousers, the black boot with its steel plate - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (thick bare grey-blue arms growing from the shoulders, never floating; the dark steel bracers). THE SHOVEL: the same shovel as in image A drawn exactly on the brown line, the spade on the big teal shape and the point on the small one, the same length; each hand on its dot grips the haft when the dot is on the brown line (both dots on it = both hands hold it). Where the brown line runs behind the grey box, the haft passes BEHIND his hood. Never stretch or shorten a limb or the shovel, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the hood, the face to the front-right, both glowing cyan eyes at the same height, the goatee) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or shovel covers the face (the eyes and the goatee).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing (the eyes and the vial are bright squares, not a halo).
No effects (no black mist, no ghosts, no walls of spirits, no graves, no dust, no shockwave, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no teal guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - leaning back toward the image left, BOTH hands on the upper haft swinging the shovel up behind him to the upper left (the spade high on the image left, never over the face), feet planted wide apart.`
- a_smash: `SMASH - pressing forward and down in a deep lunge, BOTH hands on the middle of the haft driving the spade into the ground in front of him (on the image right), the haft slanting down from the upper left.`
- q_raise: `BIG RAISE - straight and leaning back, BOTH hands lifting the shovel high over his head, the spade flung up behind him to the upper left (never over the face), the near leg stepping forward.`
- q_slam: `HEAVY SLAM - an even deeper lunge, the body thrown forward, BOTH hands low on the haft slamming the whole spade into the ground in front of him (on the image right).`
- w_raise: `RAISE UPRIGHT - standing straight, BOTH hands one above the other on the haft holding the shovel upright high in front of him (the spade up above his head, the point down), ready to drive it down.`
- w_slam: `DRIVE DOWN - squatting deep, BOTH hands on the haft driving the spade straight down into the ground in front of him (the shovel upright, the spade on the ground line), the head a little lower, looking ahead.`
- k_call: `SUMMON - the FREE hand raised high with the fingers spread (calling the dead up), the shovel hand holding the shovel slanting down behind him (the spade low on the image left), standing straight.`
- e_wind: `THROW WIND-UP - twisting back toward the image left, the FREE hand swung back and down behind him (about to throw), the shovel hand holding the shovel slanted up behind him to the upper left, feet apart.`
- e_throw: `THROW - pressing forward, the FREE arm flung straight out to the image right, the hand open (throwing), the shovel hand keeping the shovel slanted behind him, the back leg pushing straight.`
- r_raise: `RAISE TO THE SKY - up on his toes, the body stretched up, BOTH hands holding the shovel high above his head (the spade slanting up to the upper left), the head held high.`
- r_plant: `PLANT - standing tall, the FREE hand gripping the haft, holding the shovel upright on his front right (the spade on the ground), the other arm hanging at his side.`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back, leaning forward a little, the shovel hand carrying the shovel slanted at his side (the spade low on the image left, off the ground), the free arm swinging back.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, the shovel still carried slanted at his side, the free arm hanging close.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back, leaning forward a little, the shovel carried slanted at his side, the free arm swinging forward.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, the shovel carried slanted at his side.`
- d_drop: `COLLAPSE - knocked back toward the image left, the knees giving way, both arms flung out, the shovel slipping out of his hand and falling away to the image left (never over the face).`
- d_float: `FLOATING UP - his body lifted off the ground (the feet about 12 squares up), slightly hunched, the head low, both arms hanging limp, the legs dangling with the knees a little bent; the shovel lying flat on the ground under him.`

## 交回前请检查

- **17 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 22 格、空着的手臂约 30 格、握铲的约 29 格、铲子约 83 格长，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个约里克：**同一个头（照图 B，兜帽、脸朝右前方、两只青色眼睛一样高、山羊胡）**、同样粗的手臂和腿、同样的肩甲、斗篷、灯瓶；铲子在骨架棕线的位置、一样长、铲头在大的青色形状那一头，手握在铲柄上；手臂从肩膀长出来，手、铲子没有盖住脸；姿势沿着骨架；着地的脚在 y 1188。
- 所有图没有特效（黑雾、鬼魂、灵魂墙、坟墓都不画）、没有骨架线、没有网格线、没有青色辅助形状。

## 交付（`outputs/yorick-poses/`）

- `yorick-pose-a_wind.png`、`yorick-pose-a_smash.png`、`yorick-pose-q_raise.png`、`yorick-pose-q_slam.png`、`yorick-pose-w_raise.png`、`yorick-pose-w_slam.png`、`yorick-pose-k_call.png`、`yorick-pose-e_wind.png`、`yorick-pose-e_throw.png`、`yorick-pose-r_raise.png`、`yorick-pose-r_plant.png`、`yorick-pose-run1.png`、`yorick-pose-run2.png`、`yorick-pose-run3.png`、`yorick-pose-run4.png`、`yorick-pose-d_drop.png`、`yorick-pose-d_float.png`；
- 原始生成图原样放 `outputs/yorick-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/yorick_poses_done.zip`。中间不要停，17 张都画完再交。

## 附图（压缩包 `yorick_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，棕线 + 青色形状 = 铲子） |
| `1_head.png` | 定稿的头（8 倍，兜帽连脸）：每个姿势都照它逐格画 |
| `2_design.png` | 约里克定稿（每格 11 px，脚底 y 1188） |
| `3_a_wind_*` … `19_d_float_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_illaoi_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和铲子的长短，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_yorick.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（照英雄联盟，标签见 tools/kit/build_yorick.py）：普攻 attack = a_wind → a_smash → 定稿；临终仪式 skill = q_raise → q_slam；唤醒（坟墓满的 Q：雾行者 + 灵魂墙）= w_raise → w_slam → k_call；哀伤之雾 skill2 = e_wind → e_throw；海屿悼词 ult = r_raise → r_plant；死亡 dead = d_drop → d_float；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
