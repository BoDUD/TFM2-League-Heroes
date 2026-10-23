# 炼金术士 辛吉德：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 辛吉德的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右——光头、一只发白的眼睛、灰绿蒙脸布、灰蓝围巾、红夹克和金扣带、带刺的大护肩、背上发光的亮绿药罐（顶上深灰盖子）、近侧手臂上一块高高的灰绿金属盾板（边上有尖刺）、远侧手里一个亮绿药瓶、破布条、深蓝细腿、大红棕带刺靴子）。英雄联盟里他抡着盾板砸人、把敌人从肩膀上扔到身后、扔药瓶、喝药剂——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **11 个姿势，每个一张图**。待机、跑步、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个辛吉德**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边，拿盾板的那只）**，**紫线 = 远侧的手臂（画面右边，拿药瓶的那只）**；**盾板是一块直的长板：黄色宽条 = 盾板，青色那一头 = 盾板的上端（带尖刺的那头）**，黑圈 = 手抓着盾板的地方（橙线的末端就在那里）；**灰框 = 头的位置**；**半透明的绿色形状 = 背上的药罐**（和定稿里一模一样，只跟着脖子移动）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：**头 12 × 12 格**；**每条腿从胯到脚底约 19 格**（又细又长，靴子很大），**手臂从肩膀到指尖约 22 格**，**盾板从下端到上端约 46 格、宽约 8 格**（比他的身子还高）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄腿画错了只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。**盾板和定稿一样大**，只是换了方向和位置。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、光头、两只眼睛都看得见——近的发白、远的有小黑瞳孔——蒙脸布盖住鼻子以下）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸或背影、不要重新设计**。手臂、手、药瓶、盾板**不要盖住脸**。**药罐照定稿画在半透明绿色的位置**，形状不变，永远在他背后（头的后上方）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟里他有时会转过身去背对镜头——**我们的永远是 3/4 正面朝右**，只照它的手臂、盾板和身体的动作。

## 11 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `singed-pose-a_wind.png` | 抡盾：身子往后（画面左边）仰，近侧手臂把盾板高高举起竖在头的左边（尖刺那头朝上、高过头顶，不挡脸），远侧手拿着药瓶往前伸，弓步（普攻起手） |
| 4 | `singed-pose-a_smash.png` | 砸下：身子往前（画面右边）扑、压低，近侧手臂把盾板从上往下砸到身前右下方（盾板斜着横在身前，尖刺那头朝右下），远侧手臂甩到身后，弓步：远侧腿在前弯着（普攻打中） |
| 5 | `singed-pose-e_grab.png` | 抓人：身子前倾，远侧手臂往前（画面右边）伸到胸口高度、手张开抓住敌人，近侧手臂把盾板往后收在身体左边，两腿弯着（过肩摔：抓住） |
| 6 | `singed-pose-e_heave.png` | 举过肩：身子使劲往后（画面左边）仰，两只手臂一起高高举到头顶左后方（像把一个人从肩膀上扔到身后），盾板跟着举到头的左上方斜着（尖刺朝左上，不挡脸），两腿撑开（过肩摔：甩过去） |
| 7 | `singed-pose-e_throw.png` | 甩完：身子弯向左后方，两只手臂一起甩到左下方身后（刚把人扔出去），盾板斜在身体左下方，尖刺朝左，两腿弯着（过肩摔：扔出） |
| 8 | `singed-pose-w_wind.png` | 扬手：身子往后仰，远侧手把药瓶举到头的右后上方（准备往前扔，手在头的右上方，不挡脸），近侧手臂挂着盾板垂在身边，两腿站稳（强力粘胶：起手） |
| 9 | `singed-pose-w_throw.png` | 扔出：身子往前（画面右边）压，远侧手臂往前上方甩出去、手张开（药瓶刚扔出去，手里空了），近侧手臂挂着盾板往后摆，远侧腿往前迈（强力粘胶：扔出） |
| 10 | `singed-pose-r_drink.png` | 举起药剂：挺直站高、微微后仰，远侧手把一大瓶亮绿药剂高高举在头的右上方（不挡脸），近侧手臂挂着盾板垂在身边（疯狂药剂：喝之前） |
| 11 | `singed-pose-r_rage.png` | 发狂：喝完了，身子往前弓、微蹲，两只手臂往两边张开攥紧拳头（像全身充满力量在发抖），盾板在左边斜着，两腿大大分开（疯狂药剂：生效） |
| 12 | `singed-pose-d_stagger.png` | 踉跄：身子往后（画面左边）倒，膝盖弯下去，远侧手臂往右上方甩开、药瓶从手里掉下去，近侧手臂和盾板往左下方垂（死亡第一下） |
| 13 | `singed-pose-d_down.png` | 坐倒：一屁股坐在地上，两腿往前（画面右边）伸，身子往后仰，远侧手撑在身后的地上，近侧手松开，盾板平躺在他左边的地上（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1188) - THE MAD CHEMIST: a tall lanky hunched old man, BALD, one MILKY white eye, a GREY-GREEN CLOTH MASK over his mouth and nose, a grey-blue scarf, a RED JACKET with GOLD STRAPS and buckles, big SPIKED SHOULDER PADS, a big GLOWING BRIGHT GREEN TANK on his back (a dark grey cap on top, rivets), a TALL GREY-GREEN METAL SHIELD PLATE with spikes on its edge on his NEAR arm (image left), a round BRIGHT GREEN FLASK in his FAR hand (image right), torn cloth strips at the belt, THIN DARK BLUE legs and HUGE RED-BROWN SPIKED BOOTS; B its HEAD shown 8x (12 x 12 squares); C a SKELETON on the same 1254 canvas and 12 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left, holding the plate), PURPLE = the FAR arm (image right, the flask hand), the SHIELD PLATE as one straight wide YELLOW band - its CYAN end is the plate's top, the spiked end - a dark ring where the hand grips it, GREY BOX = where the head goes, the TRANSLUCENT GREEN shape = the tank on his back (exactly as in the design, only moved with his neck), the red horizontal line = the ground; D the original character in this pose (copy the POSE, the arms and the plate's swing from it - never its 3D look, its realistic proportions or a turned back); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: the head 12 x 12 squares; each leg about 19 squares from the hip to the sole, each arm about 22 squares from the shoulder to the fingertips, the shield plate about 46 squares from end to end and 8 wide, exactly as in image A. Lay the body along the skeleton: the red jacket, the straps and the pads along the green line, each leg along its line (bending at the dots: the thin dark blue leg and the big red-brown spiked boot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow from the shoulders, never floating), the near hand GRIPPING the plate at the dark ring, the far hand holding the flask (empty and open where the pose says it was thrown, a big potion bottle where the pose says so). THE PLATE drawn along the band at the design's size: grey-green riveted metal, a wooden pole down its middle, silver spikes on its edge, the spiked end where the cyan part is. THE TANK drawn square for square as in image A where the translucent green shape is, behind him. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, the bald head, both eyes - the near one milky white, the far one with a small dark pupil - the cloth mask below the nose) - the same head in every pose, only moved, never turned, never redrawn as a profile or from behind. No arm, hand, flask or part of the plate covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no poison cloud, no glue, no potion glow, no motion lines, no thrown enemy), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - leaning back to the image left, the NEAR arm lifting the shield plate high over his head to the upper left (the plate raised up beside the head on the image left, its spiked end high above, never over the face), the far hand with the flask reaching forward; a lunge.`
- a_smash: `SMASH - lunging forward and low to the image right, the NEAR arm bringing the shield plate down in front of him to the lower right (the plate slanted, its spiked end to the lower right), the far arm swung back; a lunge with the far leg bent in front.`
- e_grab: `THE GRAB - leaning forward, the FAR arm reaching forward to the image right at chest height, the hand open grabbing, the NEAR arm pulling the shield plate back at his left side, the legs bent.`
- e_heave: `THE HEAVE - leaning far back to the image left, BOTH ARMS raised high up and back over his near shoulder (as if hurling someone over his shoulder to behind him), the shield plate lifted with them, slanted up beside the head on the image left (its spiked end to the upper left, never over the face), the legs braced wide.`
- e_throw: `THE FOLLOW-THROUGH - bent toward the back left, both arms swung down and back to the lower left (the enemy just thrown), the shield plate slanted at his lower left, its spiked end to the left, the legs bent.`
- w_wind: `WIND-UP - leaning back, the FAR hand lifting the flask up behind and above the head on the image right (ready to throw, the hand above the head on the right, never over the face), the NEAR arm with the shield plate hanging at his side, the legs planted.`
- w_throw: `THE THROW - leaning forward to the image right, the FAR arm flung forward and up with the hand open (the flask just thrown, the hand empty), the NEAR arm with the shield plate swinging back, the far leg stepping forward.`
- r_drink: `THE POTION - standing tall and leaning back a little, the FAR hand holding a big bright green potion bottle high up above the head on the image right (never over the face), the NEAR arm with the shield plate hanging at his side.`
- r_rage: `THE RUSH - the potion drunk, hunched forward in a half crouch, BOTH ARMS spread out to the sides with the fists clenched (shaking with power), the shield plate slanted at his left, the legs wide apart.`
- d_stagger: `STAGGER - reeling back to the image left, the knees buckling, the FAR arm flung out to the upper right, the flask dropping from the hand, the NEAR arm and the shield plate sagging to the lower left.`
- d_down: `DOWN - sitting down on the ground, both legs stretched forward to the image right, leaning back, the far hand propped on the ground behind him, the near hand let go; the shield plate lying flat on the ground at his left.`

## 交回前请检查

- **11 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- **数格子**：头 12 × 12 格、每条腿从胯到脚底约 19 格、手臂约 22 格、盾板约 46 × 8 格，和定稿一样——腿画长了、盾板画小了就重画。
- 每张都是定稿的同一个辛吉德：**同一个头（照图 B，脸朝右前方、两只眼睛、蒙脸布）**、同样粗的腿和手臂、背上同样的药罐；盾板在近侧手里、和定稿一样大；手臂从肩膀长出来，手、药瓶和盾板没有盖住脸；姿势沿着骨架；着地的脚在 y 1188；没有一张是背影或侧脸。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/singed-poses/`）

- `singed-pose-a_wind.png`、`singed-pose-a_smash.png`、`singed-pose-e_grab.png`、`singed-pose-e_heave.png`、`singed-pose-e_throw.png`、`singed-pose-w_wind.png`、`singed-pose-w_throw.png`、`singed-pose-r_drink.png`、`singed-pose-r_rage.png`、`singed-pose-d_stagger.png`、`singed-pose-d_down.png`；原始生成图原样放 `outputs/singed-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/singed_poses_done.zip`。中间不要停，11 张都画完再交。

## 附图（压缩包 `singed_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄 / 青 = 盾板，半透明绿 = 药罐） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 12 px，脚底 y 1188） |
| `3_a_wind_*` … `13_d_down_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（design_aurora_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂和盾板的长短粗细，和定稿比**（codex-legs-need-skeletons），再拼进 rig_singed.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_singed.py）：普攻 attack = a_wind → a_smash；过肩摔 skill = e_grab → e_heave → e_throw；强力粘胶 skill2 = w_wind → w_throw；疯狂药剂 ult = r_drink → r_rage；死亡 dead = d_stagger → d_down；跑 run = 定稿的腿走路（英雄联盟的跑是背影，不用）；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。
