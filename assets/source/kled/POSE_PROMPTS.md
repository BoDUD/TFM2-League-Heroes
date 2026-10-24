# 暴怒骑士 克烈：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 克烈的两张造型用户已经定稿：`2_design.png` 是骑乘（你上一轮的 A-1：Q 版的约德尔老兵——大尖耳朵、青绿红边帽子上的钢尖刺、红头带、米白毛和大胡子、一只乳白的瞎眼和一只琥珀黄的好眼、咧嘴狂笑露白色尖牙、青绿上衣、红腰带、棕背带；一只手拿小双刃斧，一只手拎着绳子拴的捕熊夹；骑在斯嘎尔背上——橙黄鳞片、紫肚子、青蓝头刺、一只黄绿大眼睛、两条细长的紫腿和金星护腿、一条尾巴），`2_foot_design.png` 是下马步行（B-1 身子换上了 A-1 的头：同一张脸；双手握大双刃斧，深灰条纹裤、黑靴）。
> - 英雄联盟里他扔捕熊夹、拽人、骑着斯嘎尔冲刺、冲锋、挥斧，下马后挥大斧、掏枪被后坐力掀飞、倒下，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **20 个姿势**（骑乘 11 个、步行 9 个），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **骑乘的姿势都是同一个克烈和斯嘎尔**（照 `2_design.png`），**步行的都是同一个克烈**（照 `2_foot_design.png`）：样子、颜色、粗细、长短全照定稿，**格子和定稿一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**着地的脚 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：骑乘——**绿线 = 斯嘎尔的脊柱**（屁股到脖子根，它是两条腿直立走的），**红线 = 斯嘎尔近侧的腿（画面左边）**，**蓝线 = 远侧的腿**，**黄线 = 尾巴**；**青线 = 克烈的上身**（鞍上的屁股到脖子根），**橙线 = 克烈近侧的手臂（拿斧头的那只，定稿里在画面左边）**，**紫线 = 远侧的手臂**（拎绳子的那只），两条手臂上**大一点的圆点是拳头**；**灰蓝线 = 斧柄，浅灰圆盘 = 斧刃的位置和大小**；**棕线 = 绳子**（从远侧拳头出发），**深灰圆盘 = 捕熊夹**；步行——**暗红线 = 近侧的腿、深蓝线 = 远侧的腿**，其余颜色同上（灰蓝线是大斧的长柄，浅灰大圆盘是两片斧刃）。**灰框 = 头的位置**（大的是克烈的头，骑乘图里小一点的是斯嘎尔的头）。`0_mounted_skeleton.png` / `0_foot_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：斯嘎尔 Q 版腿短——**每条腿从胯到脚约 15 格**，尾巴约 21 格；**克烈骑乘时的手臂：近侧从肩膀到拳头约 12 格、远侧约 13 格**，**绳子约 22 格长**；**步行时克烈的腿从胯到脚底约 12 格、手臂约 10 格，大斧从手到斧刃约 28 格**。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。
> - **道具**：小斧头（骑乘）/ 大双刃斧（步行）**沿着灰蓝线画斧柄、斧刃画在浅灰圆盘的位置**；绳子（棕色 1 格宽、一格一格的结）**沿着棕线画**，末端的**钢灰色捕熊夹画在深灰圆盘的位置**。掏枪那两张远侧的手里拿一把**短粗的黑色火枪**（枪管 2–3 格粗，枪口朝右），大斧拖在近侧的手里。
> - **灰框照 `1_heads.png` 一格一格画**：左边是克烈的头（帽子、钢尖刺、两只大耳朵、红头带、瞎眼 + 好眼、狂笑的尖牙、大胡子），右边是斯嘎尔的头（青蓝头刺、黄绿大眼睛和紫眼睑、宽嘴）。每个姿势都是这两个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。**例外**写在姿势里：死亡瘫倒那张克烈闭眼、头耷拉。拳头、斧头、绳子、夹子**不要盖住克烈的脸**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的斯嘎尔脖子和腿很长、克烈是正常比例；我们的是 Q 版：头大、腿短，**照骨架的长短画，不照原版的长短**。

## 20 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `kled-pose-a_wind.png` | 举斧：斯嘎尔站稳；克烈在鞍上**站起来往上一窜**（上身挺直、整个人比待机高 2 格），近侧（画面左边）的手把**小斧头高高举过头顶往后**，远侧的手拎着捕熊夹的绳子（普攻起手） |
| 4 | `kled-pose-a_chop.png` | 砍下：克烈往前（画面右边）扑，近侧的手把**斧头从头顶劈到斯嘎尔头的右前方**（斧刃朝下、比斯嘎尔的头低一点），身子压低；斯嘎尔脖子往前伸（普攻打中） |
| 5 | `kled-pose-q_throw.png` | 扔夹子：克烈身子往前送，**远侧的手往前（画面右边）伸直，刚把拴绳的捕熊夹扔出去**（绳子拉直往右、夹子飞在最前面）；斧头垂在身侧（飞索捕熊器：扔出） |
| 6 | `kled-pose-q_yank.png` | 拽回来：克烈往后（画面左边）仰，**远侧的手攥着绳子往怀里猛拽**（拳头拉到胸前），绳子绷直往右前方；斯嘎尔也往后仰（飞索捕熊器：把敌人拽过来） |
| 7 | `kled-pose-e_lunge.png` | 冲刺：斯嘎尔**往前猛冲**，身子往前倾、脖子伸直、嘴张开，**近腿往后蹬直、远腿往前迈**；克烈伏低，斧头往前顶（比武：冲过去） |
| 8 | `kled-pose-e_slash.png` | 回身一砍：斯嘎尔刚冲过去、两腿着地刹住；克烈在鞍上**扭身把斧头往后（画面左边）横着抡**，身子侧扭（比武：第二下冲回来） |
| 9 | `kled-pose-r_charge.png` | 冲锋：斯嘎尔**压低身子往前狂奔**（身子几乎平着、脖子往前伸直、嘴张大），一条腿往前一条腿往后；克烈**站在鞍上往前探身大吼**，斧头往前指（冲啊——！！） |
| 10 | `kled-pose-run1.png` | 跑 1：斯嘎尔往前跑（像鸟一样两条腿），**近腿往前迈、远腿往后蹬**，身子稍往前倾；克烈随着颠一下 |
| 11 | `kled-pose-run2.png` | 跑 2：近腿落地撑住，远腿往前收到身子下面，身子抬高 1 格 |
| 12 | `kled-pose-run3.png` | 跑 3：和跑 1 反过来：**远腿往前迈、近腿往后蹬** |
| 13 | `kled-pose-run4.png` | 跑 4：远腿落地撑住，近腿往前收到身子下面，身子抬高 1 格 |
| 14 | `kled-pose-f_wind.png` | （步行）抡斧：克烈身子往后（画面左边）仰，**双手把大斧往后下方抡开**（斧刃在他身后左下方、离地不远），重心在后脚（下马后的普攻起手） |
| 15 | `kled-pose-f_chop.png` | （步行）横扫：克烈**压低身子往前（画面右边）弓步**，双手把大斧**从后面往前横着扫过去**，斧刃在他右前方、膝盖那么高 |
| 16 | `kled-pose-f_aim.png` | （步行）掏枪：克烈**远侧的手掏出一把短粗的火枪往前（画面右边）平举**，枪口朝右；近侧的手把大斧拖在身后（随身手枪：瞄准） |
| 17 | `kled-pose-f_recoil.png` | （步行）后坐：开枪的后坐力把克烈**往后（画面左边）掀飞**，身子往后仰、两脚离地，举枪的手被震得往上翘（随身手枪：开火后弹开） |
| 18 | `kled-pose-f_run1.png` | （步行）跑 1：克烈往前跑，**近腿往前迈、远腿往后蹬**，大斧扛在身侧斜着 |
| 19 | `kled-pose-f_run2.png` | （步行）跑 2：两腿交叉到身子下面、身子抬高 1 格 |
| 20 | `kled-pose-f_run3.png` | （步行）跑 3：和跑 1 反过来：**远腿往前、近腿往后** |
| 21 | `kled-pose-d_fall.png` | （死亡）挨了一下：克烈被打得**往后（画面左边）仰**，一条腿往前踢起来，手一松，**大斧脱手往右上方飞出去** |
| 22 | `kled-pose-d_down.png` | （死亡）瘫倒：克烈**跪坐着瘫在地上**，身子往前趴、头耷拉下来，眼睛闭上（画成一道线），两只手垂在地上；大斧掉在他右边的地上 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：定稿（骑乘的姿势传 `2_design.png`，步行的传 `2_foot_design.png`）、`1_heads.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加对应的 `0_*_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (the feet on y 1188) - a chibi GRUMPY LITTLE BIG-EARED WARRIOR: HUGE POINTED EARS, a teal hat with a red brim and a big steel spike on top, a red headband, cream-white fur and a big shaggy beard, ONE milky-white BLIND EYE with a pink scar and one amber GOOD EYE, a MANIC GRIN with white pointed teeth, a teal-green coat, a red sash, brown straps; MOUNTED (the riding pictures) he holds a small two-bladed axe and a bear trap on a brown rope and sits on a big UPRIGHT LIZARD - amber-orange scales, a purple belly, teal-blue head spines, one big yellow-green eye with a purple lid, two thin purple bird-like legs with brown shin guards and gold stars, a tail; ON FOOT (the on-foot pictures) he stands alone on short legs (dark grey striped trousers, black boots) holding a BIG two-bladed axe in both hands; B the HEAD BOXES shown 8x: his head (40 squares wide, 39 tall) and the lizard's (24 x 19); C a SKELETON on the same 1254 canvas and 11 px grid: GREEN = the lizard's spine (rump to the base of the neck), RED = its NEAR leg (image left), BLUE = its FAR leg, YELLOW = its tail, TEAL = the warrior's upper body (hips to the base of the neck), ORANGE = his NEAR arm (the axe arm, image left), PURPLE = his FAR arm, the bigger dot on each arm = the fist, GREY-BLUE = the axe's haft with a LIGHT GREY DISC where the blade goes, BROWN = the rope from his far fist with a DARK GREY DISC where the bear trap goes; on foot DARK RED = his near leg and NAVY = his far leg; the GREY BOXES = where the head boxes go; the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long realistic limbs); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions exactly as in image A - the lizard's legs only about 15 squares from the hip to the toe, its tail about 21; the mounted warrior's near arm about 12 squares from the shoulder to the fist and the far arm about 13, the rope about 22; on foot his legs about 12 squares from the hip to the sole, his arms about 10, the big axe about 28 from his hand to the blades. Lay the bodies along the skeleton: the lizard's scaly body along the green line, each thin leg along its line (bending at the dots, the SAME thickness, length and colours as in image A, the claws at the ends), the tail along the yellow line; his body along the teal line, each arm from its shoulder along its line (the teal sleeve, the brown glove on the bigger dot; growing from the shoulders, never floating); the axe's haft along the grey-blue line and its steel blades on the light grey disc; the brown rope along the brown line out of his far fist, the steel bear trap on the dark grey disc. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD BOXES: copy image B SQUARE FOR SQUARE into the grey boxes - his head with the hat, the steel spike, both big ears, the red headband, the blind eye and the good eye, the grin with white teeth and the beard; the lizard's head with the teal spines, the big yellow-green eye and the wide mouth - the same in every pose, only moved, never turned, never redrawn as a profile, except where THE POSE line below changes them. No fist, axe, rope or trap covers his face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no dust, no speed lines, no shield, no muzzle flash, no smoke, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no disc guides.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `AXE UP - the lizard standing still; the rider RISING UP out of the saddle (upper body straight, the whole rider two squares higher), his NEAR arm (image left) swinging the small AXE HIGH above and behind his head, the far hand still holding the bear trap's rope.`
- a_chop: `CHOP - the rider lunging forward to the image right, his NEAR arm bringing the AXE DOWN from over his head to in front of the lizard's head (the blade down, a little lower than the lizard's head), his body low; the lizard stretching its neck forward.`
- q_throw: `THROW THE TRAP - the rider leaning forward, his FAR arm thrust straight forward to the image right having just flung the BEAR TRAP on its rope: the rope STRAIGHT out to the right, the trap flying at its end; the axe hanging at his side.`
- q_yank: `YANK - the rider leaning back to the image left, his FAR fist YANKING the rope back to his chest, the rope taut and straight out to the front-right; the lizard leaning back too.`
- e_lunge: `JOUST - the lizard DASHING forward, body tilted forward, neck stretched, mouth open, its NEAR leg kicked straight back, the FAR leg striding forward; the rider crouched low, the axe thrust forward.`
- e_slash: `BACK-SLASH - the lizard landing from the dash with both feet braced; the rider TWISTING in the saddle and swinging the axe BACK to the image left in a wide level slash.`
- r_charge: `CHARGE - the lizard SPRINTING forward, body almost level, neck stretched straight out, mouth wide open, one leg reaching forward and one kicked back; the rider STANDING UP in the saddle leaning forward and yelling, the axe pointed forward.`
- run1: `RUN 1 - the lizard running forward on its two bird-like legs, the NEAR leg striding forward, the FAR leg pushing back, the body leaning a little forward; the rider bobbing with it.`
- run2: `RUN 2 - the near leg landing and bracing under the body, the far leg swinging forward under it, the body one square higher.`
- run3: `RUN 3 - the opposite of run 1: the FAR leg striding forward, the NEAR leg pushing back.`
- run4: `RUN 4 - the far leg landing and bracing, the near leg swinging forward under the body, the body one square higher.`
- f_wind: `(ON FOOT) SWING BACK - the rider leaning back to the image left, swinging the BIG AXE back and down in both hands (the blades behind him on the lower left, near the ground), his weight on the back foot.`
- f_chop: `(ON FOOT) SWEEP - the rider crouching low in a lunge to the image right, sweeping the BIG AXE in both hands from behind to the FRONT in a low level arc, the blades out in front of him on the right at knee height.`
- f_aim: `(ON FOOT) AIM - the rider pulling out a short, stubby BLUNDERBUSS PISTOL in his FAR hand and pointing it straight forward to the image right; his near hand dragging the big axe behind him.`
- f_recoil: `(ON FOOT) RECOIL - the shot's recoil BLOWING the rider BACK to the image left, leaning far back, both feet off the ground, the pistol hand kicked up.`
- f_run1: `(ON FOOT) RUN 1 - the rider running forward, the NEAR leg striding forward, the FAR leg pushing back, the big axe carried slanted at his side.`
- f_run2: `(ON FOOT) RUN 2 - the legs passing under the body, the body one square higher.`
- f_run3: `(ON FOOT) RUN 3 - the opposite of run 1: the FAR leg forward, the NEAR leg back.`
- d_fall: `(DEATH) HIT - the rider knocked back to the image left, one leg kicked up in front, his hands letting go, the BIG AXE flying out of them up to the right.`
- d_down: `(DEATH) COLLAPSED - the rider slumped on his knees on the ground, his body folded forward, his head drooping, his eyes closed (drawn as lines), his hands hanging to the ground; the big axe lying on the ground on his right.`

## 交回前请检查

- **20 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：斯嘎尔每条腿从胯到脚约 15 格；骑乘的克烈近侧手臂约 12 格、远侧约 13 格、绳子约 22 格；步行的克烈腿约 12 格、手臂约 10 格——腿画长了就重画。
- 每张都是定稿的同一个克烈（和斯嘎尔）：**同样的头（照图 B：瞎眼 + 琥珀好眼一样高、狂笑尖牙、大耳朵、帽子钢尖刺；斯嘎尔的黄绿大眼）**、同样粗的手臂和腿；斧头、绳子、夹子在各自的线和圆盘上；手臂从肩膀长出来，没有东西盖住克烈的脸；姿势沿着骨架；着地的脚在 y 1188。
- 骑乘的那几张克烈一直在斯嘎尔背上（举斧那张从鞍上站起来一点）；步行的那几张没有斯嘎尔。
- 所有图没有特效、没有骨架线、没有网格线、没有圆盘辅助线。

## 交付（`outputs/kled-poses/`）

- `kled-pose-a_wind.png`、`kled-pose-a_chop.png`、`kled-pose-q_throw.png`、`kled-pose-q_yank.png`、`kled-pose-e_lunge.png`、`kled-pose-e_slash.png`、`kled-pose-r_charge.png`、`kled-pose-run1.png`、`kled-pose-run2.png`、`kled-pose-run3.png`、`kled-pose-run4.png`、`kled-pose-f_wind.png`、`kled-pose-f_chop.png`、`kled-pose-f_aim.png`、`kled-pose-f_recoil.png`、`kled-pose-f_run1.png`、`kled-pose-f_run2.png`、`kled-pose-f_run3.png`、`kled-pose-d_fall.png`、`kled-pose-d_down.png`；
- 原始生成图原样放 `outputs/kled-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/kled_poses_done.zip`。中间不要停，20 张都画完再交。

## 附图（压缩包 `kled_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_mounted_skeleton.png` / `0_foot_skeleton.png` | 两张定稿上画着它们自己的骨架（每条线对应哪一部分，大圆点 = 拳头，灰框 = 头框，圆盘 = 斧刃 / 捕熊夹） |
| `1_heads.png` | 定稿的两个头框（8 倍：左边克烈、右边斯嘎尔）：每个姿势都照它逐格画 |
| `2_design.png` / `2_foot_design.png` | 骑乘定稿 / 步行定稿（每格 11 px，脚底 y 1188） |
| `3_a_wind_*` … `22_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_sejuani_poses / design_nunu_poses 的做法：按头框的大小定比例，头框换成定稿的，瘫倒那张除外），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、绳子的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_kled.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_kled.py）：骑乘 attack = a_wind → a_chop；skill（Q）= q_throw → q_yank；skill2（E）= e_lunge → e_slash；ult（R）= r_charge + 跑步帧；run = run1–4；idle = 定稿；hit = 定稿后退一格闪白。步行 f_attack = f_wind → f_chop；f_skill（手枪）= f_aim → f_recoil；f_run = f_run1–3；f_idle = 步行定稿；dead = d_fall → d_down（死亡都是步行的克烈：英雄联盟里骑乘死也是 Rider_Death）。
