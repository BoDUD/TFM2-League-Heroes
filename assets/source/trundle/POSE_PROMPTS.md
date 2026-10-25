# 巨魔之王 特朗德尔：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 特朗德尔的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A 第一版，按原样定稿：3/4 正面朝右的 Q 版冰霜巨魔——炸开的深红头发连着大红胡子围住整张脸、浅灰青色的脸、两只亮蓝色的眼睛、米黄色的骨头大鼻子、两颗獠牙、尖耳朵；脖子和背后一圈很大的白毛皮领子，领子里是深棕红皮披风；两肩大大的青绿宝石 + 金铜边圆肩甲；灰蓝色带斑点的皮肤、粗胳膊、金铜色护腕；深棕红皮裤、青绿圆护膝、白毛靴口、光脚米黄爪子；腰上金黄长腰布和青绿宝石扣；驼着背、两腿叉开蹲着，画面左边那只手举在肩甲下面、握着**一根和他身子差不多长的寒冰狼牙棒**（冰块拼成的棒子，越往下越粗，末端一大块多面体的冰疙瘩，冰疙瘩杵在地上）；画面右边那只手握拳垂在远侧膝盖边）。
> - 英雄联盟里他抡冰棒砸人、扑上去咬、蹲下跳起冻住地面、高举冰棒召出冰柱、站直伸手吸对手的力量，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **16 个姿势**（10 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个特朗德尔**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。（这次格子比别的英雄小，因为他和冰棒都很宽，11 px 放不下。）
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根；他驼背，头往前垂在两个肩甲中间），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 握冰棒的那只手臂**（定稿里在画面左边、从大肩甲下面伸出来），**橙线 = 空着的那只手臂**（定稿里在画面右边、握拳垂着）；手臂线的第一个点是肩膀（大肩甲的中间），**大一点的圆点是手**；**灰框 = 头的位置**（头发、脸、胡子）；**浅蓝色的长条 + 末端的大块 = 冰棒**（细的一头是手握的棒柄，大块 = 冰疙瘩）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的腿短——**每条腿从胯到脚底约 30 格**；**空着的手臂从肩膀到拳头约 26 格、握棒的约 28 格**（手臂很短，肩甲很大）；头（头发连脸连胡子）33 × 37 格；**冰棒从棒柄到冰疙瘩的尖约 62 格长**（和定稿一样长，冰疙瘩约 28 格宽、32 格长，不放大不缩短）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩甲下面长出来，不能悬空；白毛领、皮披风、肩甲跟着身子走。
> - **冰棒**：照定稿的冰棒画（浅蓝 / 天蓝的冰块、几道亮白的面、越往下越粗、末端多面体的冰疙瘩），**画在骨架上浅蓝长条的位置，一样长、一样朝向**；握棒的手就在紫线末端的圆点上，**握着棒柄那一头**。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、炸开的红头发和红胡子、两只亮蓝眼睛一样高、米黄大鼻子、獠牙）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（张嘴吼的几个姿势，只把胡子中间的嘴张开、露出獠牙）。手臂、手、冰棒**不要盖住脸**（眼睛、鼻子、獠牙）；冰棒从头附近经过时画在头**后面**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的特朗德尔手臂长、能把冰棒竖着举过头顶；我们的是 Q 版大头：手臂短、冰棒很长，**照骨架的长短和冰棒的位置画，不照原版的长短**（原版竖着举的地方，骨架把冰棒斜着放，好让整根冰棒留在画布里）。

## 16 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `trundle-pose-a_wind.png` | 抡棒起手：身子挺起来往后仰，握棒的手把冰棒高高举过头顶、往左后上方甩（冰疙瘩在画面左上方，不挡脸），另一只拳头收在胸前，两腿分开站稳（普攻起手） |
| 4 | `trundle-pose-a_smash.png` | 砸下：身子往前压、弓步蹲低，握棒的手把冰棒从头顶抡下来，冰疙瘩重重砸在身前（画面右边）的地上，另一只手臂垂在身侧（普攻砸中） |
| 5 | `trundle-pose-q_rear.png` | 仰头张嘴：身子往上挺、头往后仰，张开大嘴（准备咬），握棒的手把冰棒垂在身侧（冰疙瘩着地、在画面左边），另一只手臂张开（利齿撕咬起手） |
| 6 | `trundle-pose-q_chomp.png` | 扑咬：整个身子往前扑、压得很低，头往前伸到最前面（画面右边）一口咬下去，握棒的手把冰棒拖在身后（冰疙瘩在画面左下着地），另一只手往前抓（利齿撕咬咬中） |
| 7 | `trundle-pose-w_crouch.png` | 蹲下蓄力：深深蹲下、膝盖弯到底，两只手把冰棒横着抱在身前低处（冰疙瘩在画面左边），头低着往前看（冰封领域起手：要往上跳） |
| 8 | `trundle-pose-w_roar.png` | 跳起怒吼：整个人跳离地面（脚离地约 6 格），身子挺直，另一只拳头高高举起，张嘴吼，握棒的手把冰棒往左后方甩开（冰疙瘩在画面左边）（冰封领域：落下冻住地面） |
| 9 | `trundle-pose-e_swing.png` | 挥棒起手：身子扭向画面左边，握棒的手把冰棒横着抡到身前左边（冰疙瘩在画面左边、齐腰高），另一只拳头往前（寒冰之柱起手） |
| 10 | `trundle-pose-e_raise.png` | 高举冰棒：站直了，握棒的手把冰棒高高举起、冰疙瘩朝左上方（不挡脸），另一只拳头往前伸，张嘴吼（寒冰之柱：冰柱冒出来） |
| 11 | `trundle-pose-r_rise.png` | 起身拽：从驼背站起来一半，另一只手往前伸、像要抓住对手，握棒的手把冰棒拖在身侧（冰疙瘩在画面左下着地）（强权至上起手） |
| 12 | `trundle-pose-r_reach.png` | 伸手吸取：站得笔直、挺胸，另一只手臂往前（画面右边）伸直、手掌张开（把对手的力量吸过来），握棒的手把冰棒斜拖在身后（冰疙瘩在画面左下着地）（强权至上） |
| 13 | `trundle-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：驼着背往前冲，握棒的手把冰棒扛着往后平拖（冰疙瘩在画面左边、离地），另一只手臂往后摆 |
| 14 | `trundle-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，冰棒还往后拖着，另一只手臂垂在身边 |
| 15 | `trundle-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：驼着背往前冲，冰棒往后拖，另一只手臂往前摆 |
| 16 | `trundle-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，冰棒往后拖 |
| 17 | `trundle-pose-d_fall.png` | 被打倒：被打得往左后方仰倒，膝盖发软，两只手臂往两边甩开，冰棒从手里脱出去往左上方飞（不挡脸）（死亡第一下） |
| 18 | `trundle-pose-d_down.png` | 瘫坐在地：一屁股坐倒在地上，身子往前耷拉，头垂下，两只手臂软软垂在地上，两腿往前伸着、膝盖微弯；冰棒平躺在他身边左边的地上（死亡：倒地） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (soles on y 1188) - a chibi HUNCHED ICE TROLL with a BIG head: a wild crimson MANE joined to a big crimson BEARD framing a pale grey-teal face with TWO BRIGHT BLUE EYES, a big cream bone-like NOSE, two cream TUSKS and pointed ears; a huge spiky WHITE FUR COLLAR round his neck and back over a dark reddish-brown leather cape; BIG ROUND TEAL-GEM PAULDRONS in gold-bronze frames; spotted grey-blue skin, thick short arms with gold-bronze bracers; dark reddish-brown leather trousers, round teal knee guards, white fur boot rings, bare feet with cream claws; a long gold-yellow loincloth with a teal gem buckle; crouched with his legs wide apart; the hand on the image left raised under its pauldron gripping a HUGE ICE CLUB about as long as his legs and body (blocks of pale blue ice, wider toward the end, a big FACETED ICE HEAD resting on the ground), the fist on the image right hanging by the far knee; B its HEAD shown 8x (33 squares wide, 37 tall: the mane, face and beard); C a SKELETON on the same 1254 canvas and 9 px grid: green = the spine (pelvis to the base of the neck; he is hunched, the head hangs forward between the pauldrons), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the CLUB arm (on the image left in A), ORANGE = the FREE arm (on the image right in A), each arm line starting at the shoulder (the middle of its pauldron), the bigger dot on each arm = the hand, GREY BOX = where the head goes, the LIGHT BLUE LONG SHAPE with a BIG BLOCK at its end = where the ice club goes (its thin end is the handle in the hand, the big block the ice head), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long realistic arms); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions - each leg only about 30 squares from the hip to the sole, the free arm about 26 squares from the shoulder to the fist and the club arm about 28, the ice club about 62 squares from the handle to the tip of its ice head, exactly as in image A. Lay the body along the skeleton: the torso with the straps, the belt and the loincloth along the green line, the fur collar, the cape and the pauldrons riding on the shoulders and moving with the body, each leg along its line (bending at the dots: the leather trousers, the knee guard, the fur boot ring, the bare clawed foot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (thick short grey-blue arms growing from under the pauldrons, never floating; the gold-bronze bracers). THE CLUB: the same ice club as in image A drawn exactly on the light blue shape, the handle in the club hand on the purple dot, the ice head on the big block, the same length. Where the club passes the grey box it goes BEHIND his head. Never stretch or shorten a limb or the club, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the mane, the face to the front-right, both bright blue eyes at the same height, the bone nose, the tusks, the beard) - the same head in every pose, only moved, never turned, never redrawn as a profile (in a roaring pose only open the mouth in the middle of the beard, the tusks showing). No arm, hand or club covers the face (the eyes, the nose and the tusks).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing (the ice's highlights are bright squares, not a halo).
No effects (no ice pillar, no frozen ground, no frost mist, no bite marks, no dust, no shockwave, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no light blue guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - rearing up and leaning back, the CLUB hand swinging the ice club high over his head to the upper left (the ice head high on the image left, never over the face), the free fist pulled in at his chest, feet planted wide apart.`
- a_smash: `SMASH - pressing forward and down in a deep lunge, the CLUB hand swinging the ice club down from over his head, the ice head crashing on the ground in front of him (on the image right), the free arm hanging at his side.`
- q_rear: `REAR UP - the body straightening up, the head thrown back with the jaws open wide (about to bite), the club hand letting the club hang at his side (the ice head on the ground on the image left), the free arm spread out.`
- q_chomp: `CHOMP - lunging forward low, the head thrust out in front (to the image right) snapping its jaws shut, the club hand dragging the club behind him (the ice head on the ground on the image left), the free hand clawing forward.`
- w_crouch: `CROUCH - squatting deep, the knees fully bent, BOTH hands holding the club across in front of him low (the ice head on the image left), the head low, looking ahead (about to leap up).`
- w_roar: `LEAP AND ROAR - jumped off the ground (the feet about 6 squares up), the body straight, the free fist thrust high in the air, roaring, the club hand flinging the club out behind him to the left (the ice head on the image left).`
- e_swing: `SWING - twisting toward the image left, the CLUB hand swinging the club across in front of him to the left (the ice head at waist height on the image left), the free fist pushed forward.`
- e_raise: `RAISE - standing tall, the CLUB hand holding the club up high (the ice head to the upper left, never over the face), the free fist pushed out forward, roaring.`
- r_rise: `RISING GRAB - half straightening up from his hunch, the free hand reaching forward as if to seize the enemy, the club hand dragging the club at his side (the ice head on the ground on the image left).`
- r_reach: `DRAIN - standing up straight, chest out, the free arm stretched out straight to the image right with the palm open (pulling the enemy's strength in), the club hand dragging the club slanted behind him (the ice head on the ground on the image left).`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back, charging hunched forward, the club hand carrying the club trailing out behind him (the ice head on the image left, off the ground), the free arm swinging back.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, the club still trailing behind, the free arm hanging close.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back, charging hunched forward, the club trailing behind, the free arm swinging forward.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, the club trailing behind.`
- d_fall: `KNOCKED DOWN - thrown back toward the image left, the knees giving way, both arms flung out, the ice club flying out of his hand to the upper left (never over the face).`
- d_down: `SLUMPED DOWN - sat down hard on the ground, the body sagging forward, the head hanging, both arms limp on the ground, the legs stretched forward with the knees a little bent; the ice club lying flat on the ground beside him on the image left.`

## 交回前请检查

- **16 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 9 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 30 格、空着的手臂约 26 格、握棒的约 28 格、冰棒约 62 格长，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个特朗德尔：**同一个头（照图 B，红头发红胡子、脸朝右前方、两只亮蓝眼睛一样高、骨头鼻子、獠牙）**、同样粗的手臂和腿、同样的毛领、肩甲、腰布；冰棒在骨架浅蓝长条的位置、一样长、冰疙瘩在大块那一头，手握着棒柄；手臂从肩甲下面长出来，手、冰棒没有盖住脸；姿势沿着骨架；着地的脚在 y 1188。
- 所有图没有特效（冰柱、冰面、寒气、咬痕都不画）、没有骨架线、没有网格线、没有浅蓝辅助形状。

## 交付（`outputs/trundle-poses/`）

- `trundle-pose-a_wind.png`、`trundle-pose-a_smash.png`、`trundle-pose-q_rear.png`、`trundle-pose-q_chomp.png`、`trundle-pose-w_crouch.png`、`trundle-pose-w_roar.png`、`trundle-pose-e_swing.png`、`trundle-pose-e_raise.png`、`trundle-pose-r_rise.png`、`trundle-pose-r_reach.png`、`trundle-pose-run1.png`、`trundle-pose-run2.png`、`trundle-pose-run3.png`、`trundle-pose-run4.png`、`trundle-pose-d_fall.png`、`trundle-pose-d_down.png`；
- 原始生成图原样放 `outputs/trundle-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/trundle_poses_done.zip`。中间不要停，16 张都画完再交。

## 附图（压缩包 `trundle_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，浅蓝长条 + 大块 = 冰棒） |
| `1_head.png` | 定稿的头（8 倍，头发、脸、胡子）：每个姿势都照它逐格画 |
| `2_design.png` | 特朗德尔定稿（每格 9 px，脚底 y 1188） |
| `3_a_wind_*` … `18_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 9 px），按格读回（design_yorick_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和冰棒的长短，和定稿比**（codex-legs-need-skeletons），腿长了就重画腿，再拼进 rig_trundle.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（照英雄联盟，标签见 tools/kit/build_trundle.py）：普攻 attack = a_wind → a_smash → 定稿；利齿撕咬 skill = q_rear → q_chomp；冰封领域（被动里的 W，`w` 标签：Q 咬中英雄后跳起）= w_crouch → w_roar；寒冰之柱 skill2 = e_swing → e_raise；强权至上 ult = r_rise → r_reach；死亡 dead = d_fall → d_down；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
