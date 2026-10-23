# 雪原双子 努努和威朗普：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 努努和威朗普的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-2：3/4 正面朝右的 Q 版大雪人威朗普——淡蓝白毛、蓝色螺旋纹、发蓝光的眼睛、棕鼻头、大笑嘴、粉耳朵、深蓝爪子和短腿、身后蓬松的尾巴，头上一对棕色大鹿角；他头上骑着小男孩努努——蓝兜帽、粉猫耳、米白毛球、橙斗篷白毛边、蓝宝石扣、棕手套扶着鹿角）。
> - 英雄联盟里威朗普拍爪子、张大嘴扑上去咬、推着大雪球冲、举手召唤暴风雪、砸地，努努在他头上扔雪球，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **18 个姿势**（14 个动作 + 4 帧跑步），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个努努和威朗普**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1200**），网格从画布左上角对齐。
> - **骨架是威朗普的**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**橙线 = 近侧的手臂（定稿里在画面左边）**，**紫线 = 远侧的手臂（定稿里在画面右边）**；两条手臂上**大一点的圆点是手（爪子）**；**灰框 = 头的位置**（威朗普的头连鹿角，再加上骑在上面的努努）；**白色圆盘 = 雪球的位置和大小**（只有推雪球的几个姿势有）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底约 11 格**；**手臂长：近侧的从肩膀到爪尖约 17 格、远侧的约 16 格**；灰框（头 + 鹿角 + 努努）43 × 46 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。
> - **雪球**：一个**压实的大白雪球**（白色 3–4 档，背光面淡冰蓝，上面几处凹凸和雪块），**画在白色圆盘的位置，和圆盘一样大**（直径约 10 / 22 格）；威朗普的两只手放在骨架的圆点上——**爪子按在雪球边上**推着它。
> - **灰框里照 `1_head.png` 一格一格画**：威朗普的头（两只发蓝光的眼睛、棕鼻头、大笑嘴、粉耳朵）、两边张开的鹿角、骑在上面的努努（朝右前方、两只蓝眼睛、咧嘴笑）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。**例外**写在姿势里：张大嘴扑 / 咬（威朗普的嘴）、扔雪球 / 举手（努努的手臂）、趴倒（努努从头上掉下来）。手臂、爪子、雪球**不要盖住两张脸**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的威朗普是高大的雪人、手臂腿都长；我们的是 Q 版：头大、身子圆、腿短，**照骨架的长短画，不照原版的长短**。原版有几帧努努飞到威朗普头上方去了（扔雪球、推雪球、大招），**我们的努努一直骑在威朗普头上**（趴倒那一下除外）。

## 18 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `nunu-pose-a_wind.png` | 抬爪：威朗普身子往左后方仰，远侧（画面右边）的手臂高高举过头顶、爪子张开准备拍下去，近侧手臂垂在身边；努努扶着鹿角往后仰（普攻起手） |
| 4 | `nunu-pose-a_swipe.png` | 拍下：身子往前（画面右边）压，远侧手臂往右下方狠狠拍下去、爪子在身前下方，近侧手臂往后甩；前腿（远侧）往前跨一步（普攻拍中） |
| 5 | `nunu-pose-b_open.png` | 张大嘴扑过去：威朗普往前（画面右边）扑，**嘴张得特别大**（上下牙分开，嘴里深红），两只手臂往前张开，后腿蹬地；努努抱紧鹿角（吞噬：咬之前） |
| 6 | `nunu-pose-b_bite.png` | 咬下：威朗普的头压低往前，**嘴猛地合上咬住**（牙齿咬紧），身子往前趴，两只手臂垂在身下、爪子撑地；努努被甩得往前倾（吞噬：咬中） |
| 7 | `nunu-pose-w_pack.png` | 搓雪球：威朗普弯腰蹲下，远侧（画面右边）的手在身前地上拍一个**小雪球**（白色圆盘的位置和大小），近侧的手撑在膝盖上；努努探头往下看（史上最大雪球：起手） |
| 8 | `nunu-pose-w_push1.png` | 推雪球 1（远侧腿在前）：身子往前倾，远侧（画面右边）的手臂伸直推着身前一个**大雪球**（白色圆盘），近侧手臂往后摆，近侧腿往后蹬直，远侧腿在身下；努努抱着鹿角大笑（史上最大雪球：滚动） |
| 9 | `nunu-pose-w_push2.png` | 推雪球 2（近侧腿在前）：和推雪球 1 一样推着大雪球，两条腿换过来——近侧腿在身下，远侧腿往后蹬，近侧手臂往前摆（滚动的另一帧） |
| 10 | `nunu-pose-w_hit.png` | 撞上：雪球撞碎了（不画雪球），威朗普被震得往左后方仰，两只手臂往两边甩开，嘴张着；努努往后仰（史上最大雪球：撞上） |
| 11 | `nunu-pose-e_throw1.png` | 扔雪球 1：威朗普站稳（两脚分开，手臂微微张开），**努努在他头上用近侧的手臂往前（画面右边）扔出一个雪球**——手臂伸直在前，手里刚飞出一个白色小雪球（3 格大），另一只手扶着鹿角（雪球飞射） |
| 12 | `nunu-pose-e_throw2.png` | 扔雪球 2：威朗普同样站稳，身子往另一边晃一点；**努努换另一只手**：这只手举到脑后拿着一个雪球准备扔，刚扔完的手臂往前收回来（雪球飞射的另一帧） |
| 13 | `nunu-pose-r_raise.png` | 举手召唤暴风雪：两腿大大分开站稳，**两只手臂高高举起往两边张开**，嘴张大像在吼；努努也两只手举过头顶（绝对零度：引导） |
| 14 | `nunu-pose-r_slam.png` | 砸地爆发：深深蹲下，身子往前弓，**两只拳头一起砸在身前的地上**；努努往前探身（绝对零度：结束爆发） |
| 15 | `nunu-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，近侧手臂往前摆，远侧手臂往后摆 |
| 16 | `nunu-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两只手臂垂在身边 |
| 17 | `nunu-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子微微前倾，远侧手臂往前摆，近侧手臂往后摆 |
| 18 | `nunu-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两只手臂垂在身边 |
| 19 | `nunu-pose-d_fall.png` | 往前倒：威朗普膝盖一软往前扑倒，两只手臂垂在身下，头往下垂；努努从他头上往前翻下来（死亡第一下） |
| 20 | `nunu-pose-d_lie.png` | 趴倒：威朗普**趴在地上**（肚子贴地，身子横着朝画面右边），两只手臂往前平伸在地上，腿往后伸平，眼睛闭上（画成 X 或一道线），头搁在地上；努努坐在他头前面的地上晕乎乎的（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a chibi BIG ROUND PALE-BLUE YETI with white fluffy fur on the head, chest and forearms, blue swirl markings, two glowing blue eyes, a brown nose, a wide grin with white pointed teeth and two small tusks, pink ears, long arms with big dark blue claws, short deep blue legs, a fluffy tail behind, a pair of big brown wooden antlers spreading from his head; and a BOY riding on his head holding the antlers - a blue furry hood with pink-lined cat ears and a cream pompom, a brown fringe, big blue eyes, a grin, an orange cape with white fur trim and a blue gem clasp, brown gloves; B its HEAD BOX shown 8x (43 squares wide, 46 tall): the yeti's head with the antlers and the boy on it; C a SKELETON of the YETI on the same 1254 canvas and 12 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left in A), PURPLE = the FAR arm (image right in A), the bigger dot on each arm = the clawed hand, GREY BOX = where the head box goes, the WHITE DISC (only in some poses) = where the big snowball goes and how big it is, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its long realistic limbs, or the boy flying off the yeti); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1200.
COUNT THE SQUARES: chibi proportions - each leg only about 11 squares from the hip to the sole, the near arm about 17 squares from the shoulder to the claw tips and the far arm about 16, exactly as in image A. Lay the body along the skeleton: the yeti's round furry body along the green line, each short deep blue leg along its line (bending at the dots, the SAME thickness, length and colours as in image A), each long arm from its shoulder along its line (the white fur on the forearm, the dark blue claws on the hand dot; growing from the shoulders, never floating). THE SNOWBALL (only where the white disc is): a big packed white snowball exactly on the disc, the same size, white in 3-4 shades with pale icy-blue shading on its far side and a few lumps of snow; the claws on the hand dots press on its rim. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD BOX: copy image B SQUARE FOR SQUARE into the grey box - the yeti's face to the front-right with both glowing eyes, the nose and the grin, the antlers, the boy riding on top with his face and both eyes - the same in every pose, only moved, never turned, never redrawn as a profile, except where THE POSE line below changes the yeti's mouth or the boy's arms. No arm, claw or snowball covers either face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no snow powder, no flying snowballs except the one the pose names, no blizzard, no ice, no dust, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no disc guide.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - the yeti leaning back toward the image left, his FAR arm (image right) raised high above his head with the claws spread, ready to swipe down, the near arm hanging at his side; the boy holding on to the antlers, leaning back.`
- a_swipe: `SWIPE - pressing forward to the image right, the FAR arm swiping hard down and forward, its claws low in front of him, the near arm swinging back; the front (far) leg stepping forward.`
- b_open: `LUNGE, JAWS WIDE - the yeti lunging forward to the image right with his MOUTH OPEN VERY WIDE (the upper and lower teeth far apart, dark red inside), both arms reaching forward and apart, the back leg pushing off; the boy hugging the antlers.`
- b_bite: `BITE - the yeti's head thrust low and forward, his JAWS SNAPPED SHUT (teeth clenched), the body bent far forward, both arms hanging down under him, the claws on the ground; the boy thrown forward, holding on.`
- w_pack: `PACKING THE SNOWBALL - the yeti bent down in a crouch, his FAR hand patting a SMALL SNOWBALL on the ground in front of him (image right; the white disc's place and size), the near hand on his knee; the boy leaning over to look.`
- w_push1: `PUSHING THE SNOWBALL 1 - leaning forward, the FAR arm stretched out pushing a BIG SNOWBALL rolling in front of him (image right; the white disc), the near arm swinging back, the near leg pushing back straight, the far leg under the body; the boy holding the antlers, laughing.`
- w_push2: `PUSHING THE SNOWBALL 2 - the same push of the big snowball with the far arm, the legs the other way: the NEAR leg under the body, the FAR leg pushing back straight, the near arm swinging forward.`
- w_hit: `IMPACT - the snowball has burst (no snowball drawn), the yeti thrown back toward the image left by the crash, both arms flung out wide, his mouth open; the boy leaning back.`
- e_throw1: `THROW 1 - the yeti standing firm (feet apart, arms a little out), and ON HIS HEAD THE BOY throwing a snowball forward with one arm - that arm stretched out to the image right, a small white snowball (3 squares) just leaving his hand - the other hand on an antler.`
- e_throw2: `THROW 2 - the yeti standing firm, swaying a little the other way; THE BOY switching hands: his other arm cocked back behind his head holding a snowball ready to throw, the first arm following through forward.`
- r_raise: `CALLING THE BLIZZARD - the legs planted wide apart, BOTH ARMS RAISED HIGH and spread to the sides, his mouth wide open as if roaring; the boy also raising both arms above his head.`
- r_slam: `SLAM - squatting deep, hunched forward, BOTH FISTS smashing the ground in front of him together; the boy leaning forward.`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back behind, leaning forward a little, the near arm swinging forward, the far arm back.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, both arms hanging close.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back behind, leaning forward a little, the far arm swinging forward, the near arm back.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, both arms hanging close.`
- d_fall: `COLLAPSING - the yeti's knees giving way, falling forward, both arms hanging down under him, his head drooping; the boy tumbling forward off his head.`
- d_lie: `LYING FLAT - the yeti lying on his belly on the ground, the body stretched out toward the image right, both arms flat on the ground in front, the legs stretched out flat behind, his eyes closed (drawn as X or a line), his head resting on the ground; the boy sitting dazed on the ground in front of his head.`

## 交回前请检查

- **18 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 11 格、近侧手臂约 17 格、远侧约 16 格，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个努努和威朗普：**同一个头框（照图 B：威朗普的脸朝右前方、两只发光的眼睛、大笑嘴；鹿角；努努两只蓝眼睛）**、同样粗的手臂和腿；雪球在白色圆盘的位置、一样大，爪子按在雪球边上；手臂从肩膀长出来，爪子、雪球没有盖住脸；姿势沿着骨架；着地的脚在 y 1200。
- 努努一直骑在威朗普头上（趴倒那一张坐在地上）；扔雪球的两张里努努的手臂按姿势那一行画。
- 所有图没有特效、没有骨架线、没有网格线、没有圆盘辅助线。

## 交付（`outputs/nunu-poses/`）

- `nunu-pose-a_wind.png`、`nunu-pose-a_swipe.png`、`nunu-pose-b_open.png`、`nunu-pose-b_bite.png`、`nunu-pose-w_pack.png`、`nunu-pose-w_push1.png`、`nunu-pose-w_push2.png`、`nunu-pose-w_hit.png`、`nunu-pose-e_throw1.png`、`nunu-pose-e_throw2.png`、`nunu-pose-r_raise.png`、`nunu-pose-r_slam.png`、`nunu-pose-run1.png`、`nunu-pose-run2.png`、`nunu-pose-run3.png`、`nunu-pose-run4.png`、`nunu-pose-d_fall.png`、`nunu-pose-d_lie.png`；
- 原始生成图原样放 `outputs/nunu-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/nunu_poses_done.zip`。中间不要停，18 张都画完再交。

## 附图（压缩包 `nunu_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 爪子，灰框 = 头框） |
| `1_head.png` | 定稿的头框（8 倍：威朗普的头、鹿角、努努）：每个姿势都照它逐格画 |
| `2_design.png` | 努努和威朗普定稿（每格 12 px，脚底 y 1200） |
| `3_a_wind_*` … `20_d_lie_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（design_illaoi_poses 的做法：按头框的大小定比例，头框换成定稿的头框，张嘴 / 扔雪球 / 趴倒除外），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和雪球的大小，和定稿比**（codex-legs-need-skeletons），腿长了就照俄洛伊的 legs 包重画腿，再拼进 rig_nunu.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_nunu.py）：普攻 attack = a_wind → a_swipe → 定稿；咬 attack_bite = b_open → b_bite；史上最大雪球 skill = w_pack，skill_roll = w_push1 ↔ w_push2，skill_hit = w_hit；雪球飞射 skill2 = e_throw1 ↔ e_throw2；绝对零度 ult = r_raise（引导，轻轻晃），ult_end = r_slam；死亡 dead = d_fall → d_lie；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
