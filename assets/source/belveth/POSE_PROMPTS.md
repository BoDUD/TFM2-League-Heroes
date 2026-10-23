# 虚空女皇 卑尔维斯：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 卑尔维斯的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右——深紫色的脸、两只发光的品红眼睛、头顶品红的冠和金黄饰片、两肩高高的深紫长刺、灰青象牙色的胸口花饰和淡紫钩片、肩上的品红圆珠、两只收拢像斗篷一样裹着身体的深灰青膜翼、下面粉紫色的爪子、左边拖在地上的长尾巴）。英雄联盟里她用膜翼像刀一样劈砍、整个身子放平往前冲、扬起尾巴砸地、张开膜翼旋转、缩成一团再展开成真身——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **11 个姿势，每个一张图**。待机、移动（她是贴地滑行）、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个卑尔维斯**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 11 px**，画布 **1254 × 1254**，红线是地面（**爪尖着地在 y = 1188**；骨架说离地的姿势她飘在地面上方），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 身体的中线（下摆中间到脖子根），**橙线 = 近侧膜翼（画面左边那只，在前面、颜色全亮）的前缘**，**紫线 = 远侧膜翼（画面右边那只，暗一档）的前缘**，**半透明的青色面 = 膜翼的翼膜**（从前缘一直连到身体下摆），**品红线 = 尾巴**（从下摆后面的根到尾尖），**粉线 = 爪子**（近侧、远侧各一束）；**灰框 = 头的位置**；**半透明的紫色形状 = 两根肩刺和高领**（和定稿里一模一样，只跟着脖子移动；身子放平时跟着身子斜过去）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分——**定稿里两只膜翼收拢垂下，就是她身上的斗篷**，举起来、张开的时候斗篷就变成翅膀，身子底下露出深紫黑的躯体。
> - **长短要数格子**：**头 21 × 20 格**；**每只膜翼从肩到翼尖约 45 格**（翼膜很宽，从前缘一直连到身体），**尾巴从根到尖约 44 格**，**爪子约 15 格**。骨架就是按定稿量的：**膜翼、尾巴沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄四肢画错了只能重画——请画完数一数）。膜翼从肩膀长出来，不能悬空。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、深紫的脸、两只发光的品红眼睛、品红的冠和金黄饰片）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**。膜翼、尾巴、爪子**不要盖住脸**。**肩刺和高领照定稿画在半透明紫色的位置**，形状不变。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟里她有时会转过身去背对镜头、或者变成巨大的真身——**我们的永远是这个造型、3/4 正面朝右**，只照它的膜翼、尾巴和身体的动作。

## 11 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `belveth-pose-a_wind.png` | 举翼：身子微微往后（画面左边）仰，近侧的膜翼（画面左边）高高举到头的左上方、翼尖朝上像一把刀（翼膜张开，不挡脸），远侧的膜翼照定稿垂着裹在身上（普攻起手） |
| 4 | `belveth-pose-a_slash.png` | 劈下：身子往前（画面右边）压，近侧的膜翼从上往下劈到身前右下方（翼尖朝右下，从胸口下面扫过去，不挡脸），远侧的膜翼收在身后（普攻打中） |
| 5 | `belveth-pose-q_dash.png` | 突进：整个身子几乎放平往前（画面右边）冲，头在最前面（脸照样朝右前方），两只膜翼往后收紧贴着身子、翼尖拖在身后左边，尾巴在身后拉直，爪子往后拖，离地飘着（虚空激流） |
| 6 | `belveth-pose-w_coil.png` | 扬尾：身子往后（画面左边）仰，尾巴从身后高高扬起、绕过她背后翘到头的左上方（尾尖朝右，不挡脸），两只膜翼照定稿裹在身上（上觐沉渊：起手） |
| 7 | `belveth-pose-w_slam.png` | 砸地：身子往前（画面右边）压，尾巴从她身下甩到身前右边、平平地砸在地上（尾尖在最右边），两只膜翼往身后上方张开保持平衡（近侧的在左上、远侧的在右上，都不挡脸）（上觐沉渊：砸地） |
| 8 | `belveth-pose-e_spin1.png` | 旋风·收：微微离地，两只膜翼在身体两边竖直举起、翼尖朝上高过肩刺（像两把竖起的刀，不挡脸），尾巴绕在身下（搠面皇锋：旋转） |
| 9 | `belveth-pose-e_spin2.png` | 旋风·扫：微微离地，两只膜翼往两边斜向下张开横扫（翼尖在左下和右下），身子挺直，尾巴绕在身下（搠面皇锋：横扫） |
| 10 | `belveth-pose-r_curl.png` | 蜷缩：身子往前弓、压低，两只膜翼收拢交叉裹在身前腰下（不挡脸），爪子弯着（万载豪筵：吞下珊瑚、蜕变前） |
| 11 | `belveth-pose-r_rise.png` | 展开：离地升起、挺直，两只膜翼往两边高高张开（翼尖在头的左上和右上，不挡脸），尾巴在身后扬起（万载豪筵：化为真身） |
| 12 | `belveth-pose-d_reel.png` | 踉跄：身子往后（画面左边）倒，两只膜翼无力地往两边垂下张开，尾巴软软地拖在地上（死亡第一下） |
| 13 | `belveth-pose-d_down.png` | 倒下：身子瘫软沉到地上、往后仰，两只膜翼摊平铺在地上两边，尾巴软软地拖在地上（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 11 px squares (claws on y 1188) - THE VOID EMPRESS: a DARK VIOLET face with two GLOWING MAGENTA EYES, a MAGENTA CREST and a GOLD-YELLOW ornament on her head, two TALL DARK PURPLE SPIKES rising from her shoulders round a high collar, a pale teal-ivory spiky fan on her chest with pale violet hooks beside it, a glowing magenta orb on each shoulder, her two ARMS are HUGE BAT-LIKE WING MEMBRANES (dark slate-teal, magenta edges) - in image A FOLDED DOWN round her like a long CLOAK - pink-magenta CLAWS under the cloak, a LONG TAIL (dark plum on top, magenta underneath) lying on the ground on the left; B its HEAD shown 8x (21 x 20 squares); C a SKELETON on the same 1254 canvas and 11 px grid: green = her body's middle line (the hem's middle to the base of the neck), ORANGE = the leading edge of the NEAR wing (image left, in front) with its translucent teal membrane, PURPLE = the leading edge of the FAR wing (image right) with its membrane, MAGENTA = the tail from its root at the back of the hem to its tip, PINK = the claws, GREY BOX = where the head goes, the TRANSLUCENT VIOLET shape = the shoulder spikes and the high collar (exactly as in the design, only moved with her neck), the red horizontal line = the ground; D the original character in this pose (copy the POSE, the wings' and the tail's swing from it - never its 3D look, its realistic proportions, a turned back or its giant true form); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 11 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; claws that touch the ground on y 1188, or the body floating above it where the skeleton is lifted.
COUNT THE SQUARES: the head 21 x 20 squares; each wing about 45 squares from the shoulder to the tip along its edge, the tail about 44 squares from root to tip, the claws about 15 squares, exactly as in image A. Lay the body along the skeleton: the dark carapace, the collar fan and the hooks along the green line; each WING from its shoulder along its line (its bones bending at the dots, magenta at the edge and the tip), its dark slate-teal MEMBRANE spread from that edge to her body where the translucent teal sheet is (where the wings open, her dark plum-black body shows below the collar); the TAIL along the magenta line (the SAME thickness as in image A, magenta underneath); the claws along the pink lines. THE SHOULDER SPIKES AND COLLAR drawn square for square as in image A where the translucent violet shape is. Never stretch or shorten a wing or the tail. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both glowing magenta eyes, the magenta crest, the gold ornament) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind. No wing, tail or claw covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no slash trails, no void dash, no shockwave, no coral, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - leaning back a little to the image left, the NEAR wing-arm (image left) raised high up beside her head on the image left, its tip pointing up like a blade, the membrane opened (never over the face); the far wing still folded round her as in the design.`
- a_slash: `THE SLASH - leaning forward to the image right, the NEAR wing-arm brought down across her front to the lower right (its tip to the lower right, sweeping below her chest, never over the face); the far wing drawn back behind her.`
- q_dash: `THE DASH - the whole body almost level, rushing forward to the image right with the head in front (the face still to the front-right), both wing-arms swept back tight along her body with their tips trailing behind on the image left, the tail stretched straight out behind, the claws trailing back; flying low off the ground.`
- w_coil: `THE COIL - leaning back to the image left, the TAIL raised high from behind her, arching up past her back to above her head on the image left (its tip curling to the right, never over the face); both wings folded round her as in the design.`
- w_slam: `THE SLAM - leaning forward to the image right, the TAIL swung under her to the front and SLAMMED flat on the ground on the image right (its tip furthest right), both wing-arms opened up behind her for balance (the near one to the upper left, the far one to the upper right, never over the face).`
- e_spin1: `THE STORM, UP - lifted a little off the ground, BOTH wing-arms raised straight up along her sides, their tips above the shoulder spikes (two blades standing up, never over the face), the tail curled under her.`
- e_spin2: `THE STORM, OUT - lifted a little off the ground, BOTH wing-arms spread out and down to the sides, slashing (the tips to the lower left and the lower right), the body upright, the tail curled under her.`
- r_curl: `THE CURL - hunched forward and low, both wing-arms drawn in and crossed round the front of her lower body (below the face), the claws bent.`
- r_rise: `THE RISE - rising off the ground, tall and upright, BOTH wing-arms spread high and wide (the tips above her head to the upper left and upper right, never over the face), the tail raised behind her.`
- d_reel: `REELING - falling back to the image left, both wing-arms drooping open to the sides, the tail limp on the ground.`
- d_down: `DOWN - sunk limp to the ground and leaning back, both wing-arms spread flat on the ground at her sides, the tail lying limp.`

## 交回前请检查

- **11 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 11 px**（和定稿一样）。
- **数格子**：头 21 × 20 格、膜翼从肩到翼尖约 45 格、尾巴约 44 格、爪子约 15 格，和定稿一样——画长了、画短了就重画。
- 每张都是定稿的同一个卑尔维斯：**同一个头（照图 B，脸朝右前方、两只品红眼睛、品红冠）**、同样的肩刺和高领、同样颜色的膜翼和尾巴；膜翼从肩膀长出来，膜翼、尾巴没有盖住脸；姿势沿着骨架；着地的爪子在 y 1188；没有一张是背影、侧脸或巨大的真身。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/belveth-poses/`）

- `belveth-pose-a_wind.png`、`belveth-pose-a_slash.png`、`belveth-pose-q_dash.png`、`belveth-pose-w_coil.png`、`belveth-pose-w_slam.png`、`belveth-pose-e_spin1.png`、`belveth-pose-e_spin2.png`、`belveth-pose-r_curl.png`、`belveth-pose-r_rise.png`、`belveth-pose-d_reel.png`、`belveth-pose-d_down.png`；原始生成图原样放 `outputs/belveth-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/belveth_poses_done.zip`。中间不要停，11 张都画完再交。

## 附图（压缩包 `belveth_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，半透明紫 = 肩刺和高领，半透明青 = 翼膜） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 11 px，爪尖 y 1188） |
| `3_a_wind_*` … `13_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 11 px），按格读回（design_singed_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量膜翼和尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_belveth.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_belveth.py）：普攻 attack = a_wind → a_slash；虚空激流 skill = q_dash；上觐沉渊 skill2 = w_coil → w_slam；搠面皇锋 skill_e = e_spin1 ↔ e_spin2 循环；万载豪筵 ult = r_curl → r_rise；死亡 dead = d_reel → d_down；移动 run = 定稿贴地滑行（上下浮动、膜翼下摆摆动）；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。
