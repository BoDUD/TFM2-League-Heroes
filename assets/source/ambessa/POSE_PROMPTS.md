# 战争女族长 安蓓萨：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 安蓓萨的造型用户已经定稿（`2_design.png` 是你第 1 步画的 A-1，头按用户要求缩小到约四分之一、身子更清楚：3/4 正面朝右的 Q 版女军阀——银白色往后梳的波浪短发、深棕色皮肤、红唇、金耳环；肩上一圈深青绿色的尖毛领；黑铁胸甲带铜色接缝、红围巾、红腰布垂到膝下；粗壮的上臂、黑色的大护臂；黑铁腿甲、黑靴；**两只手各握一把带钩的月牙形龙犬刃**（亮银刃边、深色刃身、三角镂空），刀柄连着粗铁链，两把刀垂在身体两侧）。
> - 英雄联盟里她左右开弓地砍、横扫半圈、跳起来砸地、交叉双刀格挡再砸地、抡着铁链甩刀、闪过去按住敌人砸下、冲刺突进，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **21 个姿势**（15 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个安蓓萨**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 8 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1200**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**，**紫线 = 近侧的手臂**（定稿里在画面左边），**橙线 = 远侧的手臂**（定稿里在画面右边）；两条手臂末端**大一点的圆点是拳头**；**灰框 = 头的位置**（头发连脸）；**青绿色的月牙 = 近侧那只手的刀**，**浅蓝色的月牙 = 远侧那只手的刀**（月牙上的小圆圈 = 刀柄）；**深灰直线 = 铁链**（刀被甩出去、不在手里的时候，从拳头连到刀柄）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：**每条腿从胯到脚底约 44 格**；**近侧的手臂从肩膀到拳头约 34 格、远侧的约 32 格**；头（头发连脸）32 × 27 格；**每把刀从刀柄到刀尖约 34 格、最宽处约 18 格**（和定稿一样大，不放大不缩小）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画长了，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；毛领、围巾、腰布跟着身子走、摆动。
> - **两把刀**：照定稿的刀画（带钩的月牙、亮银刃边、深色刃身、三角镂空），**画在骨架上同颜色月牙的位置、一样大、刀尖朝同一个方向**；刀柄在拳头里（月牙的小圆圈就在拳头上）。铁链从护臂的手腕垂下来连到刀柄，平时垂成一个弯；骨架上有深灰直线的姿势，刀是被铁链甩出去的，**铁链沿着深灰线拉直**，刀飞在月牙的位置。月牙只表示刀的位置、大小和朝向，**刀的样子照定稿画，不照月牙的形状**。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、银白波浪短发、两只眼睛、红唇、金耳环）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、拳头、刀**不要盖住脸**（眼睛、嘴）。
> - 这一包**没有附英雄联盟原版的帧**（这次没有游戏客户端），**动作照骨架和每个姿势的文字**画。

## 21 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `ambessa-pose-a1_wind.png` | 普攻一起手：身子往左后方扭，近侧（画面左边）那只手把刀高高抡到左肩后上方（刀尖朝左上，不挡脸），远侧那只手的刀垂在身侧，两腿分开站稳 |
| 4 | `ambessa-pose-a1_slash.png` | 普攻一砍下：身子往前压、弓步，近侧那只手的刀从左上方斜着砍到身前右下方（刀尖朝右下），远侧那只手往后收 |
| 5 | `ambessa-pose-a2_wind.png` | 普攻二起手：身子往右前方扭，远侧（画面右边）那只手把刀举到右肩上方（刀尖朝上，在头的右上方，不挡脸），近侧那只手的刀垂在身前 |
| 6 | `ambessa-pose-a2_slash.png` | 普攻二横扫：远侧那只手的刀从右上方往前横扫到身前（刀尖朝右、略朝下），身子往前压，近侧的刀往后摆 |
| 7 | `ambessa-pose-q_wind.png` | 狡诈横扫起手：身子往左后方扭到底，两只手把两把刀都拉到身体左边腰高的位置（刀尖朝左后方），膝盖弯、重心压低 |
| 8 | `ambessa-pose-q_sweep.png` | 狡诈横扫：两只手臂往前伸直、两把刀在身前横扫成半圈（近侧的刀尖朝右前方、远侧的刀尖朝右下方），弓步往前压 |
| 9 | `ambessa-pose-q2_leap.png` | 裂地重击起跳：双脚离地跳起（脚离地约 10 格），两只手把两把刀一起高高举过头顶（刀尖朝左后上方，不挡脸），膝盖收起 |
| 10 | `ambessa-pose-q2_slam.png` | 裂地重击砸下：落地深蹲，两只手把两把刀一起往身前（画面右边）的地上狠狠砸下（刀尖砸在地面线上），身子往前扑 |
| 11 | `ambessa-pose-w_guard.png` | 拒斥格挡：两把刀在身前交叉成 X 挡着（刀身竖着、刀尖朝上，交叉点在胸口下面，刀尖在脸的两边、不挡脸），两只拳头在肚子前，膝盖弯、站稳 |
| 12 | `ambessa-pose-w_slam.png` | 拒斥砸地：深深蹲下，两只手把两把刀往两边的地上砸下去（近侧的刀在画面左下、远侧的刀在画面右下，刀尖着地） |
| 13 | `ambessa-pose-e_lash1.png` | 割裂一：两只手臂往两边张开，两把刀被铁链甩出去、飞在身体两侧（近侧的刀在画面左边齐腰高、远侧的刀在画面右边齐肩高），铁链从拳头拉直连到刀柄，身子微微往右转 |
| 14 | `ambessa-pose-e_lash2.png` | 割裂二：转了半圈，手臂换个方向，两把刀被铁链甩到另一边（近侧的刀在画面右下、远侧的刀在画面左上方、高过头，不挡脸），铁链拉直 |
| 15 | `ambessa-pose-step.png` | 龙犬之步：往前（画面右边）冲刺的一步，身子往前倾得很厉害，前腿弓、后腿蹬直，两把刀都拖在身后（刀尖朝左下、离地） |
| 16 | `ambessa-pose-r_grab.png` | 公开处决抓人：远侧那只手往前（画面右边）伸出去、五指张开抓住敌人（齐肩高，刀从手腕垂下），近侧那只手把刀高高举到左后上方（不挡脸），弓步 |
| 17 | `ambessa-pose-r_slam.png` | 公开处决砸下：几乎单膝跪地的深蹲，远侧那只手往前下方猛按（把敌人按进画面右边的地里），近侧那只手的刀从上往下砍到身前地面（刀尖着地） |
| 18 | `ambessa-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子前倾，两把刀拖在身后两侧（刀尖朝左下、离地），手臂往后摆 |
| 19 | `ambessa-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两把刀还拖在身后 |
| 20 | `ambessa-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：身子前倾，两把刀拖在身后 |
| 21 | `ambessa-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格，两把刀拖在身后 |
| 22 | `ambessa-pose-d_kneel.png` | 倒下一：被打得跪倒，双膝着地（小腿平贴地面、往后伸），身子往后仰，两只手松开垂着，两把刀掉在身体两侧的地上（平躺） |
| 23 | `ambessa-pose-d_slump.png` | 倒下二：跪着往前瘫下去，身子前弓，头低下（头不转），两只手臂软软垂到地上，两把刀平躺在地上 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 8 px squares (soles on y 1200) - a chibi POWERFUL WARLORD WOMAN: SILVER-WHITE short wavy swept-back hair, DARK BROWN skin, dark red lips, a gold earring; a spiky DARK TEAL-GREEN FUR MANTLE round her shoulders; a BLACK IRON breastplate with bronze seams, a deep red scarf at the collar and a RED SASH hanging below her knees; bare muscular upper arms, huge angular BLACK GAUNTLETS; black iron leg plates and black boots; in EACH fist a HOOKED CRESCENT DRAKEHOUND BLADE (a bright silver edge, a dark flat inner plate with triangular holes), a thick iron CHAIN from each gauntlet to its blade's handle, both blades hanging at her sides; B its HEAD shown 8x (32 squares wide, 27 tall); C a SKELETON on the same 1254 canvas and 8 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left), BLUE = the FAR leg (image right), PURPLE = the NEAR arm (on the image left in A), ORANGE = the FAR arm (on the image right in A), the bigger dot at the end of each arm = the fist, GREY BOX = where the head goes, a TEAL CRESCENT = where the near fist's blade goes, a LIGHT BLUE CRESCENT = where the far fist's blade goes (the small circle on a crescent = its handle), a DARK GREY LINE = a chain pulled straight from a fist to a blade flung out on it, the red horizontal line = the ground; D (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 8 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1200.
COUNT THE SQUARES: each leg about 44 squares from the hip to the sole, the near arm about 34 squares from the shoulder to the fist and the far arm about 32, each blade about 34 squares from the handle to the tip and 18 across, exactly as in image A. Lay the body along the skeleton: the torso with the breastplate, the scarf and the sash along the green line, the fur mantle riding on the shoulders, each leg along its line (bending at the dots: the black leg plates and boots - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (bare muscular upper arms growing from the shoulders, never floating; the black gauntlets). THE BLADES: the same blades as in image A, each drawn where its crescent is - the same size, its tip pointing the same way - its handle in the fist on the crescent's small circle; the crescents only show place, size and direction: draw the blades' real shape from image A. Each chain hangs in a loop from the gauntlet to its blade's handle; where a dark grey line is drawn, that blade is flung out on its chain: the chain runs straight along the line. Never stretch or shorten a limb or a blade, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the silver hair, the face to the front-right, the eyes, the red lips, the earring) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, fist or blade covers the face (the eyes and the lips).
The same colours as image A; one continuous 1-square near-black outline; every plate of the black armour separated by its lighter edge and its darker shadow; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no blade trails, no afterimages, no shockwaves, no dust, no sparks, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide crescents.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a1_wind: `ATTACK 1 WIND-UP - twisting back toward the image left, the NEAR fist raised behind her near shoulder with its blade swung up to the upper left (never over the face), the far blade hanging at her side, feet planted apart.`
- a1_slash: `ATTACK 1 SLASH - pressing forward in a lunge, the NEAR blade cut down from the upper left to the lower right in front of her belly (its tip low on the image right), the far arm pulled back.`
- a2_wind: `ATTACK 2 WIND-UP - twisting toward the image right, the FAR fist raised above her far shoulder with its blade pointing up (above her head on the right, never over the face), the near blade hanging in front of her.`
- a2_slash: `ATTACK 2 SWEEP - the FAR blade swept across in front of her from the upper right (its tip pointing to the image right and a little down), the body pressing forward, the near blade swung back.`
- q_wind: `CUNNING SWEEP WIND-UP - twisted all the way back toward the image left, BOTH fists pulled to her left at waist height with both blades trailing back to the image left, knees bent, low.`
- q_sweep: `CUNNING SWEEP - BOTH arms swung straight out in front of her, the two blades sweeping a half circle at her front (the near blade's tip forward to the image right, the far blade's to the lower right), a deep lunge forward.`
- q2_leap: `SUNDERING SLAM LEAP - jumping (the feet about 10 squares off the ground), BOTH blades raised high over her head together (their tips up and back to the upper left, never over the face), knees drawn up.`
- q2_slam: `SUNDERING SLAM - landing in a deep crouch, BOTH blades slammed down together onto the ground in front of her (on the image right, their tips on the ground line), the body thrown forward.`
- w_guard: `REPUDIATION BRACE - the two blades CROSSED in an X in front of her body (upright, tips up, crossing below her chest, the tips beside her face, never over it), both fists in front of her belly, knees bent, braced.`
- w_slam: `REPUDIATION SLAM - squatting deep, BOTH blades slammed down onto the ground on either side of her (the near one low on the image left, the far one low on the image right, their tips on the ground).`
- e_lash1: `LACERATE 1 - both arms flung out to the sides, the two blades WHIRLED OUT ON THEIR CHAINS and flying at her sides (the near blade out on the image left at waist height, the far blade out on the image right at shoulder height), each chain pulled straight from the fist to the blade's handle, turning a little to the right.`
- e_lash2: `LACERATE 2 - half a turn on, the arms swapped over, the blades whirled round on their chains to the other side (the near blade low on the image right, the far blade high on the image left above her head, never over the face), the chains pulled straight.`
- step: `DRAKEHOUND'S STEP - a dashing lunge forward to the image right, the body leaning far forward, the front leg bent, the back leg pushing straight, both blades trailing behind her (their tips low on the image left, off the ground).`
- r_grab: `PUBLIC EXECUTION GRAB - the FAR hand thrust forward to the image right at shoulder height, open, seizing her victim (its blade hanging from the wrist), the NEAR blade raised high behind her to the upper left (never over the face), a lunge.`
- r_slam: `PUBLIC EXECUTION SLAM - dropping into a deep crouch, almost kneeling, the FAR hand driven down in front of her (pinning her victim into the ground on the image right), the NEAR blade hewn down onto the ground in front of her (its tip on the ground).`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back, leaning forward, both blades trailing behind at her sides (tips low on the image left, off the ground).`
- run2: `RUN 2 - the near leg under the body carrying her, the FAR knee lifted forward, the body one square higher, both blades still trailing behind.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back, leaning forward, both blades trailing behind.`
- run4: `RUN 4 - the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, both blades trailing behind.`
- d_kneel: `COLLAPSE - struck down onto both knees (the shins flat on the ground behind), the body sagging back, both hands opening and hanging, the two blades dropped flat on the ground at her sides.`
- d_slump: `SLUMP - still kneeling, slumping forward, the body bent over, the head low (never turned), both arms hanging limp to the ground, the two blades lying flat on the ground.`

## 交回前请检查

- **21 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 8 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 44 格、手臂约 32–34 格、每把刀约 34 格长，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个安蓓萨：**同一个头（照图 B：银白短发、脸朝右前方、红唇、金耳环）**、同样粗的手臂和腿、同样的毛领、甲、围巾和腰布；两把刀在骨架上同颜色月牙的位置、一样大、刀尖朝向一样，刀柄在拳头里，铁链连着；手臂从肩膀长出来，拳头和刀没有盖住脸；姿势沿着骨架；着地的脚在 y 1200。
- 所有图没有特效（刀光、残影、冲击波都不画）、没有骨架线、没有网格线、没有辅助月牙。

## 交付（`outputs/ambessa-poses/`）

- `ambessa-pose-a1_wind.png`、`ambessa-pose-a1_slash.png`、`ambessa-pose-a2_wind.png`、`ambessa-pose-a2_slash.png`、`ambessa-pose-q_wind.png`、`ambessa-pose-q_sweep.png`、`ambessa-pose-q2_leap.png`、`ambessa-pose-q2_slam.png`、`ambessa-pose-w_guard.png`、`ambessa-pose-w_slam.png`、`ambessa-pose-e_lash1.png`、`ambessa-pose-e_lash2.png`、`ambessa-pose-step.png`、`ambessa-pose-r_grab.png`、`ambessa-pose-r_slam.png`、`ambessa-pose-run1.png`、`ambessa-pose-run2.png`、`ambessa-pose-run3.png`、`ambessa-pose-run4.png`、`ambessa-pose-d_kneel.png`、`ambessa-pose-d_slump.png`；
- 原始生成图原样放 `outputs/ambessa-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ambessa_poses_done.zip`。中间不要停，21 张都画完再交。

## 附图（压缩包 `ambessa_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 拳头，月牙 = 刀） |
| `1_head.png` | 定稿的头（8 倍，头发连脸）：每个姿势都照它逐格画 |
| `2_design.png` | 安蓓萨定稿（每格 8 px，脚底 y 1200） |
| `3_a1_wind_skeleton.png` … `23_d_slump_skeleton.png` | 每个姿势的骨架 |

## Claude 收到后（给 Claude 看）

- 量格子（应约 8 px），按格读回（design_illaoi_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细和刀的大小，和定稿比**，腿长了就重画腿，再拼进 rig_ambessa.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（标签见 tools/kit/build_ambessa.py）：普攻 attack = a1_wind → a1_slash（和 a2_wind → a2_slash 交替）；狡诈横扫 skill = q_wind → q_sweep；裂地重击 slam = q2_leap → q2_slam；割裂 skill2 = e_lash1 → e_lash2；拒斥 w = w_guard → w_slam；公开处决 ult = r_grab → r_slam；龙犬之步 step = step；死亡 dead = d_kneel → d_slump；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
