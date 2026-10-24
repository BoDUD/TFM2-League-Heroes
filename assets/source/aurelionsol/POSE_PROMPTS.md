# 铸星龙王 奥瑞利安·索尔：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 奥瑞利安·索尔的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右——浅蓝白骨质龙脸、两只亮青色眼睛、一排白尖牙、金色冠盔和往后扫的金角、洋红-紫鬃毛、深海军蓝鳞甲身体和胸口亮蓝 V 鳞、青色发光细线、背上的深紫尖刺、紫色龙爪手臂和金护腕、胸口以下深蓝到紫罗兰的星云尾巴和白色星点）。英雄联盟里他扬爪甩出星星、吸气后张嘴吐出龙息、伸爪召唤黑洞、高举爪子从天上拽下星星——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **10 个姿势，每个一张图**。待机、移动（他是飞行，用你上一轮画的 B）、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个奥瑞利安·索尔**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**最低的一点——通常是尾尖——在 y = 1188**；他是浮空的，游戏里我再把他整体抬高），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 身体的中线（胸口下沿中间到脖子根），**橙线 = 近侧的手臂（画面左边那只，在前面、颜色全亮）**，从肩膀经过手肘、手腕到最长那根爪尖；**紫线 = 远侧的手臂（画面右边那只，暗一档）**；**品红线 = 星云尾巴**（从胸口下面的根到尾尖）；**灰框 = 头的位置**。背上的深紫尖刺长在身体上，跟着身体走。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：**头 35 × 32 格**（连鬃毛和金角）；**每只手臂从肩到爪尖约 23 格**，**尾巴从根到尖约 44 格**。骨架就是按定稿量的：**手臂、尾巴沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄四肢画错了只能重画——请画完数一数）。手臂从肩膀长出来，不能悬空；尾巴从胸口下面长出来，越往尾尖越细，星点间隔开。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、浅蓝白骨质脸、亮青色眼睛、白尖牙、金冠金角、洋红鬃毛）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**——**只有 q_breath 一张例外：下颌张大**（嘴里露出上下两排牙和一点亮光），其余地方照样。手臂、爪子、尾巴**不要盖住脸**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右；渲染里尾巴是一截没上色的黑色网格，看它怎么摆就行），**动作照它**，长相照定稿。英雄联盟里他有时会把头低下去、转过身或者头朝下——**我们的永远是这个造型、3/4 正面朝右、头照定稿**，只照它的手臂、尾巴和身体的动作。

## 10 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `aurelionsol-pose-a_wind.png` | 扬爪：身子往上挺、微微后仰（画面左边），远侧的爪子（画面右边）抬到头的右边、高过肩膀（爪心里握着一颗小星星的位置，不挡脸），近侧的爪子收在胸前下方，尾巴在身下垂着（普攻起手） |
| 4 | `aurelionsol-pose-a_throw.png` | 甩出：身子往前（画面右边）探，脖子往前伸，远侧的爪子往前用力甩出去（手臂伸直、爪子张开朝右），近侧的爪子往后摆，尾巴往身后左边甩（普攻甩出星星） |
| 5 | `aurelionsol-pose-q_wind.png` | 吸气：脖子往后缩、胸口挺起来（像深吸一口气），头抬高一点，两只爪子收在胸前两侧，尾巴往身后卷起（星河冲荡：起手） |
| 6 | `aurelionsol-pose-q_breath.png` | 吐息：身子往前（画面右边）压，脖子往前伸，嘴巴张大（下颌往下张开，露出上下两排牙和嘴里的亮光；龙息本身不画，后面单画），两只爪子张开在身前两侧，尾巴在身后卷着（星河冲荡：吐息） |
| 7 | `aurelionsol-pose-e_reach.png` | 伸爪：身子往前倾，远侧的爪子往前上方伸出去、爪子张开（在前方召唤黑洞），近侧的爪子往后下方摆，尾巴往身后上方扬起（星芒凝汇：召唤） |
| 8 | `aurelionsol-pose-e_hold.png` | 捧星：两只爪子在胸前下方合拢、爪心相对（像官方原画里捧着一颗星星，中间留空，黑洞后面单画），身子微微前弓，尾巴照定稿卷在身下（星芒凝汇：凝聚） |
| 9 | `aurelionsol-pose-r_call.png` | 召星：身子挺直往上，远侧的爪子在头的右边高高举起、朝天张开（从天上拽星星，不挡脸），近侧的爪子往下张开，尾巴在身下摆向右边（星落：召唤） |
| 10 | `aurelionsol-pose-r_pull.png` | 拽下：身子往前下方猛地一弓，远侧的爪子从头顶往下拽到身前右下方（爪子握紧），近侧的爪子往后，尾巴往身后上方甩起（星落：砸下） |
| 11 | `aurelionsol-pose-d_rear.png` | 仰倒：身子往后（画面左边）仰，头往后抬，两只爪子往两边无力地张开，尾巴在身下松松地垂着（死亡第一下） |
| 12 | `aurelionsol-pose-d_down.png` | 倒下：身子瘫软地沉到地上、往后斜躺，两只爪子摊在地上，星云尾巴平平地拖在身后左边的地上（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (the tail tip on y 1188) - THE STAR DRAGON, floating, no legs: a PALE BLUE-WHITE BONY DRAGON FACE with two GLOWING CYAN EYES and a row of WHITE SHARP TEETH, a GOLD CROWN-HELM with GOLD HORNS sweeping back, a big MAGENTA-VIOLET MANE, a DEEP NAVY SCALED BODY with BRIGHT BLUE V-SCALES down the chest and thin GLOWING CYAN LINES, DARK PURPLE SPIKES along the back, PURPLE CLAWED ARMS with GOLD BRACERS, and below the chest a DEEP BLUE to VIOLET NEBULA TAIL dotted with white stars; B its HEAD shown 8x (35 x 32 squares, the mane and horns included); C a SKELETON on the same 1254 canvas and 11 px grid: green = his body's middle line (the bottom of the chest to the base of the neck), ORANGE = the NEAR arm (image left, in front) from the shoulder through the elbow and the wrist to the longest claw's tip, PURPLE = the FAR arm (image right), MAGENTA = the nebula tail from its root under the chest to its tip, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose (copy the POSE, the arms' and the tail's swing from it - its tail is an untextured black shape there - never its 3D look, its realistic proportions or a lowered, turned or upside-down head); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; the lowest point (usually the tail tip) on y 1188.
COUNT THE SQUARES: the head 35 x 32 squares; each arm about 23 squares from the shoulder to the claw tip, the tail about 44 squares from root to tip, exactly as in image A. Lay the body along the skeleton: the navy scaled chest with its blue V-scales and cyan lines along the green line, the back spikes on the back; each ARM from its shoulder along its line (bending at the dots, the gold bracer at the wrist, the claws open or clenched as the pose says, the background visible between them); the NEBULA TAIL along the magenta line (the SAME thickness as in image A, thinner toward the tip, the stars spaced apart). Never stretch or shorten an arm or the tail. The near arm in full tone, the far one a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both glowing cyan eyes, the teeth, the gold helm and horns, the magenta mane) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind (only in the breath pose the jaw opens, as the pose line says). No arm, claw or tail covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares except the stars, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no breath beam, no star, no black hole, no shockwave, no motion lines), no background, no starry sky, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - rearing up tall and leaning back a little to the image left, the FAR clawed arm (image right) raised up beside his head on the image right, above the shoulder, as if holding a small star, the near arm drawn in below his chest, the nebula tail hanging down beneath him.`
- a_throw: `THE THROW - lunging forward to the image right, the neck stretched forward, the FAR clawed arm flung out straight to the image right with the claws open (the star let go), the near arm swung back, the tail swept out behind him to the image left.`
- q_wind: `THE BREATH IN - the neck drawn back and the chest puffed out (a deep breath in), the head held a little higher, both clawed arms drawn in at the sides of his chest, the tail curling up behind him.`
- q_breath: `THE BREATH - leaning forward to the image right with the neck stretched out and the JAW WIDE OPEN (the lower jaw dropped, both rows of teeth showing and a glow inside the mouth; the breath beam itself is NOT drawn), both clawed arms spread at the front sides of his body, the tail curled behind him.`
- e_reach: `THE REACH - leaning forward, the FAR clawed arm reaching forward and up with the claws spread (calling the black hole in front of him), the near arm swung back and down, the tail raised up behind him.`
- e_hold: `THE CUPPED CLAWS - both clawed arms brought together in front of his lower chest, the palms facing each other with a gap between them (as in the official art, holding a star; the black hole is drawn later), hunched forward a little, the tail curled under him as in the design.`
- r_call: `THE CALL - upright and stretched tall, the FAR clawed arm raised high on the image right of his head, up with the claws open (never over the face) (pulling a star down from the sky), the near arm spread down, the tail swinging under him to the image right.`
- r_pull: `THE PULL DOWN - hunched sharply forward and down, the FAR clawed arm yanked down from above to the front lower right (the claws clenched), the near arm back, the tail whipped up behind him.`
- d_rear: `REARING BACK - falling back to the image left, the head thrown back, both clawed arms flung limply open to the sides, the tail hanging loose beneath him.`
- d_down: `DOWN - sunk limp to the ground and lying tilted back, both clawed arms spread on the ground, the nebula tail lying flat on the ground behind him to the image left.`

## 交回前请检查

- **10 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：头 35 × 32 格、手臂从肩到爪尖约 23 格、尾巴约 44 格，和定稿一样——画长了、画短了就重画。
- 每张都是定稿的同一个奥瑞利安·索尔：**同一个头（照图 B，脸朝右前方、两只亮青色眼睛、白尖牙、金冠金角、洋红鬃毛）**，只有 q_breath 张嘴；同样颜色的鳞甲、发光线、背刺、爪子和星云尾巴；手臂从肩膀长出来，手臂、爪子、尾巴没有盖住脸；姿势沿着骨架；最低点在 y 1188；没有一张是背影、侧脸、低头或头朝下。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/aurelionsol-poses/`）

- `aurelionsol-pose-a_wind.png`、`aurelionsol-pose-a_throw.png`、`aurelionsol-pose-q_wind.png`、`aurelionsol-pose-q_breath.png`、`aurelionsol-pose-e_reach.png`、`aurelionsol-pose-e_hold.png`、`aurelionsol-pose-r_call.png`、`aurelionsol-pose-r_pull.png`、`aurelionsol-pose-d_rear.png`、`aurelionsol-pose-d_down.png`；原始生成图原样放 `outputs/aurelionsol-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/aurelionsol_poses_done.zip`。中间不要停，10 张都画完再交。

## 附图（压缩包 `aurelionsol_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 11 px，尾尖 y 1188） |
| `3_a_wind_*` … `12_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_taliyah_poses 的做法：按头的大小定比例，头换成定稿的头；q_breath 保留 Codex 张开的下颌），颜色对到定稿的调色板；**先在 8 倍下量手臂和尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_aurelionsol.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_aurelionsol.py）：普攻 attack = a_wind → a_throw；星河冲荡 skill = q_wind → q_breath（吐息时循环）；星芒凝汇 skill2 = e_reach → e_hold；星落 / 天瀑 ult = r_call → r_pull；死亡 dead = d_rear → d_down；移动 run = 第 1 步 B 的飞行（hd/run.png，身子和尾巴波动）；待机 = 定稿悬浮（上下浮动、尾巴摆动，hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。
