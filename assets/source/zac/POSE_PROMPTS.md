# 生化魔人 扎克：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 扎克的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-1：3/4 正面朝右的扎克——半透明亮绿色黏液做的大块头，身体里深绿色的纹路，驼着背，小小的头埋在两个大肩膀中间，两只发黄光的眼睛，咧开的大嘴和一排深色尖牙，头顶一根深蓝绿的弯触须（末端一个圆疙瘩），两条又粗又长的手臂垂到地上、三根粗手指的大手，两条短粗的腿）。
> - 英雄联盟里扎克出拳、把手臂像橡皮一样拉长去抓人、举起来砸地、按地拉成弹弓飞出去、弹跳压扁、死时化成一滩，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **17 个姿势**，**每个一张图**。待机、跑步、挨打我从定稿本身来做，不用画。
> - **每张都是同一个扎克**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1197**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到头的底部），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**橙线 = 近侧的手臂（定稿里在画面左边、垂到地上的那条大手臂）**，**紫线 = 远侧的手臂（定稿里在画面右边）**；两条手臂上**大一点的圆点是手腕**，线的末端是指尖；**灰框 = 头的位置**（头连触须）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。扎克的身体很宽：两个大肩膀、厚厚的胸口和后背都要画出来，脊柱只是中线。
> - **长短要数格子**：腿很短——**每条腿从胯到脚底约 20 格**；**手臂很长：近侧的从肩膀到指尖约 46 格、远侧的约 42 格**；灰框（头 + 触须）24 × 42 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折**（之前一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。
> - **只有姿势那一行写了“拉长”的手臂**才像橡皮一样拉长（扎克的能力）：那条手臂沿着骨架变长，**粗细和定稿一样或稍细一点**，颜色、纹路照定稿，大手照定稿的大小；其他手臂、腿一律照定稿的长短。
> - **灰框里照 `1_head.png` 一格一格画**：扎克的头（两只发黄光的眼睛、咧开的大嘴和尖牙、触须）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、大手**不要盖住脸**。
> - **绿色方框**（r_splat、d_melt、d_puddle 这 3 张没有骨架）：扎克被压扁 / 融化了，**整个身体画在绿框里、填满它**，框的底边就是地面；头按姿势那一行画（压扁时眼睛和嘴照样露出来；融化时眼睛半闭 / 闭成一道线），颜色照定稿。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的扎克腿长、头小；我们的是定稿的比例：头埋在肩膀中间、身子宽、腿短，**照骨架的长短画，不照原版的长短**。

## 17 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `zac-pose-a_wind.png` | 抡臂：身子扭着往后仰，近侧（画面左边）的手臂往后平甩到肩膀高度、拳头往下垂，远侧手臂垂在身前，弓步：近侧腿往后蹬直、远侧腿在前弯着（普攻起手） |
| 4 | `zac-pose-a_punch.png` | 出拳：身子往前（画面右边）压低扑出去，远侧的手臂像橡皮一样**伸长一点**往前平平打出去（拳头在最前面，和肩膀一样高），近侧手臂甩到身后，弓步：近侧腿往后蹬直、远侧腿往前弯（普攻打中） |
| 5 | `zac-pose-q_wind.png` | 甩手蓄力：身子挺高往后仰，近侧（画面左边）的手臂**拉长三成**高高甩到头顶后上方，远侧手臂垂在身前，两腿站稳（延伸打击：起手） |
| 6 | `zac-pose-q_reach.png` | 长臂抓出：身子压低前倾，远侧手臂像橡皮一样**拉长三成**，贴着地面往前（画面右边）伸出去，张开的大手在最前面抓东西；近侧手臂垂在身后，两腿弯着（延伸打击：伸手） |
| 7 | `zac-pose-q_lift.png` | 举起：挺直站高，**两只手臂一起高高举过头顶**（像举着一个人准备往下砸），两腿大大分开站稳（延伸打击：甩人） |
| 8 | `zac-pose-q_slam.png` | 砸地：深深蹲成大马步，身子往前弓，**两只大拳头一起砸在身前两边的地上**（延伸打击：砸中） |
| 9 | `zac-pose-e_plant.png` | 按地：弯腰往前，**两只手臂一起往前伸到地上按住**（两只大手撑在身前的地上，手臂比平时长一点），近侧腿往后撤一步、两腿弯着（橡筋弹弓：起手） |
| 10 | `zac-pose-e_pull.png` | 拉弹弓：身子使劲往后（画面左边）拉、弓着背，两只手还按在前面的地上，**两只手臂被拉得很长**（比平时长一半，像拉开的橡皮筋），两腿弯着蓄力（橡筋弹弓：蓄力） |
| 11 | `zac-pose-e_fly.png` | 飞出去：整个人**横着飞在空中**（身子朝画面右边伸直、比平时拉长一点），两只手臂往前伸，两条腿往后拖，头照样朝右前方（橡筋弹弓：飞行） |
| 12 | `zac-pose-e_land.png` | 落地：重重落下蹲成大马步，**两只手臂往两边张开**（肩膀高、手掌张开），两腿大大分开（橡筋弹弓：落地） |
| 13 | `zac-pose-r_crouch.png` | 下蹲蓄力：身子缩起来深深蹲下、背弓着，两只手臂垂到脚边的地上，准备往上弹（动感弹球：起跳前） |
| 14 | `zac-pose-r_jump.png` | 跳在空中：整个人在空中（脚离地），**两只手臂往两边张开**、手垂着，两条腿弯着悬在身下（动感弹球：弹起） |
| 15 | `zac-pose-r_ball.png` | 团成球：在空中把自己**缩成一个圆球**——两膝抱到胸前，两只手臂抱住小腿，脸照样朝右前方露在最上面（动感弹球：最高点） |
| 16 | `zac-pose-r_splat.png` | 压扁落地：砸在地上**整个身子被压扁**——又矮又宽（高度只有平时一半多，宽度宽两成），手臂和腿往四周摊开贴着地，头也被压低但两只眼睛和咧开的嘴照样露在上面（动感弹球：落地） |
| 17 | `zac-pose-d_stagger.png` | 摇晃：身子直起来摇摇晃晃，远侧手臂往前伸着、手掌张开像要抓什么，近侧手臂往前下方垂着，腿开始发软（死亡第一下） |
| 18 | `zac-pose-d_melt.png` | 融化：身子**软塌下去开始融化**，变成一大团往下淌的黏液，腿弯折陷进去，手臂软软地垂到地上，头往前耷拉（眼睛半闭）（死亡） |
| 19 | `zac-pose-d_puddle.png` | 化成一滩：完全化成**地上扁扁的一大滩绿色黏液**（只有十几格高），触须软软地倒在上面，两只眼睛闭着（画成一道线）露在黏液上（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (soles on y 1197) - a HULKING, HUNCHED brute made of TRANSLUCENT BRIGHT GREEN SLIME with dark green veins inside, a small head sunk between huge shoulders with two glowing yellow eyes and a wide grin of dark jagged teeth, a dark blue-green tendril with a round knob curling up from the top of his head, two huge long arms hanging to the ground with big three-fingered hands, two short thick legs; B its HEAD BOX shown 8x (24 squares wide, 42 tall): his head with the tendril; C a SKELETON (or, for a squashed / melted pose, a GREEN BOX) on the same 1254 canvas and 9 px grid: green line = the spine (pelvis to the base of the head), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left in A, the big arm hanging to the ground), PURPLE = the FAR arm (image right in A), the bigger dot on each arm = the wrist (the line ends at the finger tips), GREY BOX = where the head box goes, GREEN BOX = the space his whole squashed or melted body fills, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long realistic legs and small head); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1197.
COUNT THE SQUARES: each leg only about 20 squares from the hip to the sole, the near arm about 46 squares from the shoulder to the finger tips and the far arm about 42, exactly as in image A - EXCEPT an arm THE POSE line says is STRETCHED: that arm follows its longer line like rubber, the same thickness as in A or a little thinner, its big hand the same size. Lay the body along the skeleton: his broad hunched body, the huge shoulders and back round the green line (the spine is only its middle), each short thick leg along its line (bending at the dots, the SAME thickness, length and colours as in A), each long arm from its shoulder along its line (the big three-fingered hand at the end; growing from the shoulders, never floating). Never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD BOX: copy image B SQUARE FOR SQUARE into the grey box - his face to the front-right with both glowing yellow eyes, the grin and the teeth, the tendril - the same in every pose, only moved, never turned, never redrawn as a profile. No arm or hand covers the face. With a GREEN BOX instead: draw his whole body squashed / melted inside the box and filling it, the face as THE POSE line says.
The same colours as image A (the bright green slime in 4 shades with few big yellow-green highlights and dark green veins inside, the yellow eyes, the dark teeth, the dark blue-green tendril); one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no flying slime blobs, no splashes, no puddle under him except the pose that IS a puddle, no dust, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no box guide.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - his body twisted back, the NEAR arm (image left) swung back level with the shoulder, its fist hanging down, the FAR arm hanging in front of him; a lunge: the near leg pushed back straight, the far leg bent in front.`
- a_punch: `PUNCH - lunging forward and low to the image right, the FAR arm STRETCHING a little like rubber and punching straight forward (the fist out in front at shoulder height), the near arm swung behind him; a lunge: the near leg pushed back straight, the far leg bent forward.`
- q_wind: `WIND-UP - standing tall and leaning back, his NEAR arm (image left) STRETCHED a third longer and swung high up and back over his head, the far arm hanging in front, the legs planted.`
- q_reach: `THE LONG GRAB - crouched low and leaning forward, his FAR arm STRETCHED a third longer like rubber, reaching forward low along the ground to the image right, the big open hand at its end grabbing; the near arm hanging behind him, the legs bent.`
- q_lift: `LIFTING - standing up tall, BOTH ARMS RAISED HIGH above his head together (as if holding someone up to slam him down), the legs planted wide apart.`
- q_slam: `SLAM - squatting deep in a wide stance, hunched forward, BOTH BIG FISTS smashing the ground in front of him on either side.`
- e_plant: `PLANTING THE ARMS - bending forward, BOTH ARMS reaching forward to the ground and pressing on it (both big hands flat on the ground in front of him, the arms a little longer than usual), the near leg stepped back, the legs bent.`
- e_pull: `PULLING THE SLINGSHOT - his body pulled far back to the image left, hunched, both hands still planted on the ground in front, BOTH ARMS STRETCHED LONG between them (half as long again, like a drawn rubber band), the legs bent, ready to spring.`
- e_fly: `FLYING - his whole body FLYING THROUGH THE AIR stretched out toward the image right (a little longer than usual), both arms reaching forward, both legs trailing behind, the head facing the front-right as always.`
- e_land: `LANDING - crashing down into a deep wide crouch, BOTH ARMS FLUNG OUT to the sides (at shoulder height, the hands open), the legs wide apart.`
- r_crouch: `CROUCH - curling down into a deep squat, hunched, both arms hanging down to the ground by his feet, ready to bounce up.`
- r_jump: `IN THE AIR - his whole body up in the air (the feet off the ground), BOTH ARMS SPREAD OUT to the sides with the hands hanging, both legs bent, dangling under him.`
- r_ball: `BALLED UP - high in the air, CURLED INTO A ROUND BALL: both knees pulled up to his chest, both arms wrapped round the shins, the face still showing on top to the front-right.`
- r_splat: `SPLAT - landing with his WHOLE BODY SQUASHED: short and wide (a little over half his usual height, a fifth wider), the arms and legs sprawled out flat on the ground, the head pressed down low with both eyes and the grin still showing on top.`
- d_stagger: `STAGGERING - standing up swaying, the far arm reaching forward with the hand open as if clutching at something, the near arm hanging forward and down, the legs starting to give way.`
- d_melt: `MELTING - his body SAGGING AND MELTING into a big heap of dripping slime, the legs buckled and sinking into it, the arms hanging limp to the ground, the head drooping forward (the eyes half closed).`
- d_puddle: `A PUDDLE - fully melted into a FLAT POOL OF GREEN SLIME on the ground (only a dozen squares tall), the tendril lying limp on it, his two eyes closed (drawn as lines) showing on the puddle.`

## 交回前请检查

- **17 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 9 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 20 格、近侧手臂约 46 格、远侧约 42 格，和定稿一样——只有姿势里写了“拉长”的那条手臂更长；腿画长了就重画。
- 每张都是定稿的同一个扎克：**同一个头框（照图 B：脸朝右前方、两只发黄光的眼睛、咧开的大嘴和尖牙、触须）**、同样宽的身体、同样粗的手臂和腿；手臂从肩膀长出来，大手没有盖住脸；姿势沿着骨架；着地的脚在 y 1197。
- 绿框那 3 张（r_splat、d_melt、d_puddle）：整个身体在绿框里、填满它，底边贴地。
- 所有图没有特效、没有骨架线、没有网格线、没有框线。

## 交付（`outputs/zac-poses/`）

- `zac-pose-a_wind.png`、`zac-pose-a_punch.png`、`zac-pose-q_wind.png`、`zac-pose-q_reach.png`、`zac-pose-q_lift.png`、`zac-pose-q_slam.png`、`zac-pose-e_plant.png`、`zac-pose-e_pull.png`、`zac-pose-e_fly.png`、`zac-pose-e_land.png`、`zac-pose-r_crouch.png`、`zac-pose-r_jump.png`、`zac-pose-r_ball.png`、`zac-pose-r_splat.png`、`zac-pose-d_stagger.png`、`zac-pose-d_melt.png`、`zac-pose-d_puddle.png`；
- 原始生成图原样放 `outputs/zac-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/zac_poses_done.zip`。中间不要停，17 张都画完再交。

## 附图（压缩包 `zac_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手腕，灰框 = 头框） |
| `1_head.png` | 定稿的头框（8 倍：头、眼睛、嘴、触须）：每个姿势都照它逐格画 |
| `2_design.png` | 扎克定稿（每格 9 px，脚底 y 1197） |
| `3_a_wind_*` … `19_d_puddle_*` | 每个姿势的骨架或绿框（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 9 px），按格读回（design_nunu_poses 的做法：按头框的大小定比例，头框换成定稿的头框，绿框的三张除外），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_zac.py，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_zac.py）：普攻 attack = a_wind → a_punch → 定稿；延伸打击 skill = q_wind → q_reach（伸着），skill_slam = q_lift → q_slam；橡筋弹弓 skill2 = e_plant → e_pull（蓄力），skill2_fly = e_fly，skill2_land = e_land → 定稿；动感弹球 ult（每一跳）= r_crouch → r_jump → r_ball → r_jump，ult_land = r_splat → r_crouch；死亡 dead = d_stagger → d_melt → d_puddle；待机 = 定稿一帧（hero_reels）；跑 run = 定稿自己的腿（布隆 / 沃里克的走法）；受击 hit = 定稿后退一格闪白。
