# 北地之怒 瑟庄妮：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 瑟庄妮和钢鬃的造型用户已经定稿（`2_design.png` 是你上一轮重画的 A-2：3/4 正面朝右，Q 版的瑟庄妮——青铜金头盔、两只蓝冰角、冰蓝眼睛、浅金色头发、紫皮甲、青铜金尖肩甲上的蓝宝石、米白毛领，手里棕黑相间的链枷和蓝色冰锤头；骑在钢鬃背上——灰蓝毛、白鬃毛、两根象牙色大獠牙、粉鼻子、青蓝发光的眼睛、橄榄绿鞍甲和蓝宝石、深灰蹄子。`2_run_design.png` 是 B-1 冲锋定稿，跑步的骑法照它）。
> - 英雄联盟里她甩链枷、横扫、砸地、甩套索，钢鬃冲锋挑飞、奔跑、人立、倒地，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **14 个姿势**（10 个动作 + 4 帧跑步），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个瑟庄妮和钢鬃**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**最低的蹄子 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：**绿线 = 钢鬃的脊柱**（屁股到肩膀），**红线 = 钢鬃近侧的两条腿（画面左边那侧：近后腿、近前腿）**，**蓝线 = 钢鬃远侧的两条腿**；**青线 = 瑟庄妮的上身**（鞍上的屁股到脖子根），**橙线 = 她近侧的手臂（拿链枷的那只，定稿里在画面左边）**，**紫线 = 她远侧的手臂**，两条手臂上**大一点的圆点是拳头**；**棕线 = 链枷的链子**（从拳头出发），**浅蓝圆盘 = 冰锤头的位置和大小**；**两个灰框 = 两个头的位置**（小的是瑟庄妮的头，大的是钢鬃的头连獠牙）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：钢鬃 Q 版腿短——**每条腿从胯到蹄子约 18 格**；**瑟庄妮的手臂：近侧从肩膀到拳头约 24 格、远侧约 12 格**；**链子约 22 格长**，冰锤头约 12 格大。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。
> - **链枷**：棕黑相间的链子（2 格粗，棕黑一格一格交替）**沿着棕线画**，可以有一点弧度；末端的**蓝色冰锤头**（3 档蓝 + 青色亮纹）**画在浅蓝圆盘的位置**。链子从她近侧的拳头里出来。
> - **两个灰框照 `1_heads.png` 一格一格画**：左边是瑟庄妮的头（头盔、两只冰角、额前宝石、朝右前方的脸、两只冰蓝眼睛、粉色小嘴、浅金头发），右边是钢鬃的头（耳朵、发光的眼睛、粉鼻子、张开的嘴、两根大獠牙、前面的白鬃毛）。每个姿势都是这两个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。**例外**写在姿势里：挑飞（钢鬃的头往上抬）、倒地（钢鬃的眼睛闭上）。拳头、链子、冰锤头**不要盖住她的脸**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的钢鬃腿长、瑟庄妮是正常比例；我们的是 Q 版：两个头都大、腿短，**照骨架的长短画，不照原版的长短**。原版的链子很长（能甩出好几个身位），**我们的链子照棕线的长度**。

## 14 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `sejuani-pose-a_wind.png` | 甩到身后：钢鬃站稳不动；瑟庄妮身子往后仰，近侧（画面左边）的手臂往左后方抡开，链枷被甩到钢鬃屁股后面、冰锤头低低地拖在左后方（普攻起手） |
| 4 | `sejuani-pose-a_smash.png` | 抽出：瑟庄妮身子往前（画面右边）压，近侧手臂往前伸，**链枷从身后抡上来往前抽直**，冰锤头甩到钢鬃头的右前上方、比她肩膀稍高（普攻打中） |
| 5 | `sejuani-pose-q_toss.png` | 撞飞上挑：钢鬃冲到头猛地抬头，**獠牙往上一挑**（头框往上抬），前腿离地收起，后腿蹬地；瑟庄妮压低身子抓紧，链枷甩在身后（极寒突袭：撞上把敌人挑飞） |
| 6 | `sejuani-pose-w_sweep.png` | 横扫：瑟庄妮身子扭向右边，近侧手臂往前伸平，**链枷拉直往右横着扫出去**（冰锤头在钢鬃头的右前方、和她肩膀差不多高）（凛冬之怒：第一下） |
| 7 | `sejuani-pose-w_raise.png` | 举高：瑟庄妮挺直身子，近侧手臂高高举过头顶，**链枷甩到头顶上方往后弯**，冰锤头在她头的左上方（凛冬之怒：第二下抡起） |
| 8 | `sejuani-pose-w_slam.png` | 猛砸：瑟庄妮整个身子往前扑，近侧手臂往前下方砸到底，**链枷甩直、冰锤头重重砸在钢鬃前方很远的地上**（凛冬之怒：往前砸一条线） |
| 9 | `sejuani-pose-r_wind.png` | 举起套索：瑟庄妮挺身，近侧手臂举到头顶，**链枷在头顶上方抡圈**（冰锤头在她头的右上方）（极冰寒狱：甩之前） |
| 10 | `sejuani-pose-r_throw.png` | 甩出：瑟庄妮身子往前送，**近侧手臂往前（画面右边）伸直，刚把套索甩出去**（手张开），链枷垂在手下面晃（极冰寒狱：扔出） |
| 11 | `sejuani-pose-run1.png` | 跑 1（伸展）：钢鬃往前奔，**两条前腿往前伸、两条后腿往后蹬**，身子拉长、离地 1 格；瑟庄妮压低身子，链枷扬在身后（和跑步定稿 `2_run_design.png` 一样骑法） |
| 12 | `sejuani-pose-run2.png` | 跑 2（前脚着地）：前腿落地撑住，后腿往前收到身子下面，身子往前倾一点；瑟庄妮随着往前压 |
| 13 | `sejuani-pose-run3.png` | 跑 3（收拢）：四条腿都收在身子下面，后腿着地、前腿抬起，身子弓起来高 1 格；瑟庄妮微微抬身 |
| 14 | `sejuani-pose-run4.png` | 跑 4（后腿蹬地）：后腿用力往后蹬，前腿往前伸准备落地，身子前倾；瑟庄妮压低 |
| 15 | `sejuani-pose-d_rear.png` | 人立：钢鬃痛得**后腿站起来、前腿在空中乱蹬**，头往上仰；瑟庄妮被甩得往后（画面左边）仰倒、快从背上掉下去，链枷脱手往后飞（死亡第一下） |
| 16 | `sejuani-pose-d_down.png` | 倒地：钢鬃**侧身倒在地上**（肚子朝画面外，四条腿往画面右边伸着），眼睛闭上（画成一道线）；瑟庄妮摔在钢鬃左边的地上，链枷落在她身边（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_heads.png`（两个头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`（跑步的四张换成 `2_run_design.png`）。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (the lowest hoof on y 1188) - a chibi WARRIOR WOMAN riding a big WAR BOAR: she wears a bronze-gold helm with two curved blue ice horns and a blue gem on the brow, a pale face with two ice-blue eyes and a small pink mouth, pale blonde locks, purple leather armour under pointed bronze-gold plates with glowing blue gems, cream-white fur at the collar, and holds a FLAIL - a brown-and-black wrapped chain ending in a big blue ice head with cyan lines; the BOAR has blue-grey fur, a crest of white bristly mane, two huge ivory tusks curving up, a pink snout and a pink open mouth, a glowing cyan eye, pink inner ears, short legs with dark grey split hooves, olive-green bronze saddle armour with big blue gems; B its two HEAD BOXES shown 8x: hers (32 squares wide, 24 tall) and the boar's (26 x 34, with the tusks); C a SKELETON on the same 1254 canvas and 11 px grid: GREEN = the boar's spine (rump to shoulder), RED = the boar's NEAR legs (image left side), BLUE = its FAR legs, TEAL = the woman's upper body (hips in the saddle to the base of the neck), ORANGE = her NEAR arm (the flail arm, image left in A), PURPLE = her FAR arm, the bigger dot on each arm = the fist, BROWN = the flail's chain from her near fist, the LIGHT BLUE DISC = where the ice head goes and how big it is, the two GREY BOXES = where the two head boxes go (the small one hers, the big one the boar's), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look, its long realistic limbs or its very long chain); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; hooves that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions - each of the boar's legs only about 18 squares from the hip to the hoof, her near arm about 24 squares from the shoulder to the fist and the far arm about 12, the chain about 22 squares long, the ice head about 12 squares, exactly as in image A. Lay the bodies along the skeleton: the boar's bulky furry body along the green line, each short leg along its line (bending at the dots, the SAME thickness, length and colours as in image A, the dark grey hooves at the ends); her body in the saddle along the teal line, each arm from its shoulder along its line (the purple sleeve, the bronze bracer, the fist on the bigger dot; growing from the shoulders, never floating); the brown-and-black chain along the brown line out of her near fist, the blue ice head on the disc. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD BOXES: copy image B SQUARE FOR SQUARE into the two grey boxes - her head with the helm, both ice horns, the gem, her face to the front-right with both ice-blue eyes and the pink mouth; the boar's head with the ear, the glowing eye, the pink snout, the open mouth and the two big ivory tusks - the same in every pose, only moved, never turned, never redrawn as a profile, except where THE POSE line below changes them. No fist, chain or ice head covers her face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no frost, no ice storm, no flying bola, no snow, no dust, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no disc guide.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - the boar standing still; the woman leaning back, her NEAR arm (image left) swung out back to the image left, the flail flung behind the boar's rump, its ice head low at the back on the image left.`
- a_smash: `LASH - the woman lunging forward to the image right, her NEAR arm reaching forward, the flail whipped up from behind and LASHED STRAIGHT OUT forward, its ice head far in front of and above the boar's head, a little higher than her shoulder.`
- q_toss: `TUSK TOSS - the boar at the end of its charge throwing its head UP, the TUSKS flicking upward, its front legs off the ground and tucked, the hind legs pushing; the woman crouched low holding on, the flail flying behind.`
- w_sweep: `SWEEP - the woman twisting to the image right, her NEAR arm stretched straight forward, the flail pulled STRAIGHT OUT to the right in a level sweep, its ice head far in front of the boar's head at about her shoulder height.`
- w_raise: `RAISE - the woman sitting up straight, her NEAR arm raised high above her head, the flail swung up OVER her head and curling back, its ice head above her on the upper left.`
- w_slam: `SLAM - the woman throwing her whole body forward, her NEAR arm swung all the way down and forward, the flail stretched straight, its ice head crashing onto the ground FAR in front of the boar.`
- r_wind: `WIND THE BOLA - the woman sitting up, her NEAR arm raised above her head, whirling the flail in a circle OVER her head, its ice head up on the upper right.`
- r_throw: `THROW - the woman leaning forward, her NEAR arm thrust straight forward to the image right, the hand open having just flung the bola; the flail hanging down from her hand, swinging.`
- run1: `RUN 1 (STRETCHED) - the boar galloping to the image right, BOTH FRONT LEGS reaching forward and BOTH HIND LEGS kicking back, its body long and one square off the ground; the woman crouched low, the flail raised behind her (ridden like the run design).`
- run2: `RUN 2 (FRONT LANDING) - the front legs landing and bracing under the chest, the hind legs swinging forward under the body, leaning forward a little; the woman pressing forward with it.`
- run3: `RUN 3 (GATHERED) - all four legs gathered under the body, the hind legs on the ground, the front legs lifted and tucked, the back arched one square higher; the woman rising a little.`
- run4: `RUN 4 (PUSH-OFF) - the hind legs pushing hard back, the front legs reaching forward to land, the body tilted forward; the woman crouched low.`
- d_rear: `REARING - the boar rearing up on its HIND LEGS in pain, the front legs pawing the air, its head thrown up; the woman thrown back to the image left, falling off its back, the flail slipping from her hand.`
- d_down: `DOWN - the boar lying on its side on the ground, its four legs stretched out to the image right, its eye closed (drawn as a line); the woman fallen on the ground on its left, the flail lying beside her.`

## 交回前请检查

- **14 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：钢鬃每条腿从胯到蹄子约 18 格、她近侧手臂约 24 格、远侧约 12 格、链子约 22 格，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个瑟庄妮和钢鬃：**同样的两个头（照图 B：她的脸朝右前方、两只冰蓝眼睛、粉嘴；钢鬃的发光眼睛、粉鼻子、两根大獠牙）**、同样粗的手臂和腿；链子沿着棕线、冰锤头在浅蓝圆盘上；手臂从肩膀长出来，拳头、链子、冰锤头没有盖住她的脸；姿势沿着骨架；着地的蹄子在 y 1188。
- 瑟庄妮一直骑在钢鬃背上（人立那一张往后掉、倒地那一张摔在地上除外）。
- 所有图没有特效、没有骨架线、没有网格线、没有圆盘辅助线。

## 交付（`outputs/sejuani-poses/`）

- `sejuani-pose-a_wind.png`、`sejuani-pose-a_smash.png`、`sejuani-pose-q_toss.png`、`sejuani-pose-w_sweep.png`、`sejuani-pose-w_raise.png`、`sejuani-pose-w_slam.png`、`sejuani-pose-r_wind.png`、`sejuani-pose-r_throw.png`、`sejuani-pose-run1.png`、`sejuani-pose-run2.png`、`sejuani-pose-run3.png`、`sejuani-pose-run4.png`、`sejuani-pose-d_rear.png`、`sejuani-pose-d_down.png`；
- 原始生成图原样放 `outputs/sejuani-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/sejuani_poses_done.zip`。中间不要停，14 张都画完再交。

## 附图（压缩包 `sejuani_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 拳头，灰框 = 两个头框，浅蓝圆盘 = 冰锤头） |
| `1_heads.png` | 定稿的两个头框（8 倍：左边瑟庄妮、右边钢鬃）：每个姿势都照它逐格画 |
| `2_design.png` / `2_run_design.png` | 待机定稿 / 冲锋定稿（每格 11 px，最低的蹄子 y 1188） |
| `3_a_wind_*` … `16_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_aurelionsol_poses / design_nunu_poses 的做法：按头框的大小定比例，两个头框换成定稿的，挑飞 / 倒地除外），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、链子的长短粗细和冰锤头的大小，和定稿比**（codex-legs-need-skeletons），再拼进 rig_sejuani.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_sejuani.py）：普攻 attack = a_wind → a_smash → 定稿；极寒突袭 skill = 跑步帧加速冲 → q_toss；凛冬之怒 skill2 = w_sweep → w_raise → w_slam；极冰寒狱 ult = r_wind → r_throw；死亡 dead = d_rear → d_down；跑 run = run1–4；待机 = 定稿（hero_reels）；受击 hit = 定稿后退一格闪白。
