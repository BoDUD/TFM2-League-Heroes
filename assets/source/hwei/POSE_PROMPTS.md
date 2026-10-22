# 异画师 彗：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 彗的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右的 Q 版年轻画师——墨绿近黑的乱发、半垂的墨绿眼睛、彩色耳饰、深紫颈环、靛蓝画师外套和宽大的青绿翻领加金纹、红橙袖口、橙衬衫和棕马甲、墨绿七分裤和青绿丝带、粉色珠串、棕色便鞋，远侧的手（画面右边）握着一支斜指地面的大画笔——深色笔杆、红色和深蓝的笔头、木色笔尖，背后浮着一道弯月形的墨痕和三滴墨）。英雄联盟里他每个动作都把画笔挥起来——收到身前、往前甩、举过头顶、指向地面、插进地里、往身后扫、张开双臂、掉在地上——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **21 个姿势，每个一张图**（17 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个彗**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1200**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边，握画笔的那只）**；**画笔是一根直的长条：黄色 = 笔杆，粉色粗段 = 红蓝色的笔头，青色 = 木色笔尖**；紫线的末端就在笔杆上（那里是手握着笔的地方）；**灰框 = 头的位置**；**淡蓝色的形状 = 背后的弯月墨痕**（和定稿里一模一样，只跟着脖子移动）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底只有约 18 格**，**手臂从肩膀到指尖约 18 格**，**画笔从笔杆尾到笔尖 33 格**，头连头发 29 × 24 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（上一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。**画笔和定稿一样长、一样粗**，只是换了方向。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只墨绿眼睛都看得见、耳饰、颈环）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、画笔**不要盖住脸**（眼睛和嘴）。**弯月墨痕照定稿画在淡蓝色的位置**，形状不变、不挡脸。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的彗是正常比例、墨痕会飞来飞去；我们的是 Q 版大头、墨痕固定在背后：身子短、手臂短、腿短，**画笔不要举到脸前面，手臂往两边、往前、往后、往上伸，不要从脸前面横过去**。

## 21 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `hwei-pose-a_wind.png` | 甩笔蓄势：身子往左拧，远侧手臂把画笔横着收到身前左边（笔尖朝画面左边、腰的高度），近侧手臂往左后方垂着，两腿分开站（普攻起手） |
| 4 | `hwei-pose-a_flick.png` | 甩笔：身子往前倾，远侧手臂往前平伸，画笔往右前方甩出去（笔尖朝右、略往上，肩的高度），近侧手臂往后甩，前腿（远侧）屈膝（普攻出手） |
| 5 | `hwei-pose-q_wind.png` | 举笔蓄势：身子微微后仰，远侧手臂把画笔高高举到远侧肩膀上方（笔尖朝上、略往右，不挡脸），近侧手臂往前伸开，近侧腿在前（灾·没骨火起手） |
| 6 | `hwei-pose-q_throw.png` | 甩笔掷出：大步往前，身子前倾，远侧手臂把画笔从上往前下方甩下来（笔尖朝右下方），近侧手臂往后张开，后腿（近侧）往后伸（灾·没骨火打出） |
| 7 | `hwei-pose-qw_raise.png` | 引雷：踮起脚跳起来（脚离地约 4 格），两膝弯着，远侧手臂把画笔笔直举过头顶（笔尖朝上），近侧手臂往左上方张开（灾·攒聚雷起手） |
| 8 | `hwei-pose-qw_point.png` | 指地落雷：低低的大弓步，身子前倾，远侧手臂把画笔往右前方指向地面（笔尖朝右下方、快碰到地），近侧手臂往后伸，后腿（近侧）往后伸直（灾·攒聚雷落下） |
| 9 | `hwei-pose-qe_raise.png` | 跃起竖笔：跳起来（脚离地约 6 格），两膝收起，远侧手把画笔竖着握在身前右边（笔尖朝下），近侧手臂往左张开（灾·连皴山起跳） |
| 10 | `hwei-pose-qe_slam.png` | 落地插笔：深深蹲下（低弓步），远侧手把画笔往前下方插进地里（笔尖碰到右前方的地面），近侧手臂往左后方张开（灾·连皴山落地） |
| 11 | `hwei-pose-ew_low.png` | 低扫：两腿大开站低，身子前倾，远侧手臂把画笔往左下方扫到身后（笔尖朝左下、贴近地面），近侧手臂往左张开（悚·滞涩幽瞳起手） |
| 12 | `hwei-pose-ew_high.png` | 高举：站直，远侧手臂把画笔往右上方高高举起（笔尖朝右上方，不挡脸），近侧手臂垂在身边，近侧腿在前（悚·滞涩幽瞳睁眼） |
| 13 | `hwei-pose-ee_wind.png` | 横笔蓄势：弓步，身子往左拧，远侧手臂把画笔横着拉到身后左边（笔尖朝画面左边，胸口的高度，不挡脸），近侧手臂往左后方张开（悚·双钩血喉起手） |
| 14 | `hwei-pose-ee_swing.png` | 下劈：往前压低，远侧手臂把画笔从左往右前下方劈下来（笔尖朝右下方），近侧手臂往后甩，前腿（远侧）屈膝（悚·双钩血喉咬合） |
| 15 | `hwei-pose-r_open.png` | 张开双臂：站直，两只手臂往两边张开，远侧手把画笔平平地伸向右边（笔尖朝右），近侧手掌朝上张在左边（大招起手） |
| 16 | `hwei-pose-r_fling.png` | 甩出画卷：身子前倾，远侧手臂把画笔往前用力甩出去（笔尖朝右、略往下），近侧手臂往后张开，大步往前（大招打出） |
| 17 | `hwei-pose-r_hop.png` | 跃起：轻轻跳起（脚离地约 6 格），两膝收起，远侧手臂把画笔横着收到身后左边（笔尖朝画面左边、腰的高度），近侧手臂收在胸前（大招收尾） |
| 18 | `hwei-pose-run1.png` | 跑 1（远侧腿在前着地，近侧腿往后抬起）：身子微微前倾，远侧手握着画笔斜拖在右下方（和定稿一样），近侧手臂往后摆 |
| 19 | `hwei-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，画笔一样斜拖着 |
| 20 | `hwei-pose-run3.png` | 跑 3（近侧腿在前着地，远侧腿往后抬起） |
| 21 | `hwei-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格 |
| 22 | `hwei-pose-d_stagger.png` | 踉跄：身子往左后方倒，膝盖弯下去，近侧手捂着胸口，远侧手臂垂下张开，画笔从手里掉落、平躺在他右前方的地上（死亡第一下） |
| 23 | `hwei-pose-d_kneel.png` | 跪倒：近侧膝盖跪在地上，远侧腿立着膝盖，身子往前弯，近侧手撑在地上，远侧手搭在膝盖上，头低着；画笔平躺在他右前方的地上（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a chibi SLIM YOUNG PAINTER with a BIG head: messy dark green-black hair with teal lights, half-closed dark green eyes, small coloured earrings, a dark purple choker, an indigo painter's coat with a wide turquoise collar, gold trim and red-orange cuffs, a red-orange shirt and a brown vest, dark green cropped trousers with teal ribbon ties, a pink anklet, brown loafers, a GIANT PAINTBRUSH in his far hand (a dark shaft, a red and navy brush head, a wooden point) and a FLOATING CRESCENT OF PAINT STROKES behind him (navy with orange, teal and gold, three ink drops); B its HEAD with the hair shown 8x (29 squares wide, 24 tall); C a SKELETON on the same 1254 canvas and 12 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right, the one holding the brush), the BRUSH as one straight bar - YELLOW = the shaft, the thick MAGENTA part = the red-and-navy brush head, CYAN = the wooden point - the purple arm ends on the shaft where the hand grips it, GREY BOX = where the head goes, the PALE BLUE shape = the crescent behind him (exactly as in the design, only moved with his neck), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE and the brush's swing from it, never its 3D look, its realistic proportions or its flying crescent); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1200.
COUNT THE SQUARES: chibi proportions - each leg only about 18 squares from the hip to the sole, each arm about 18 squares from the shoulder to the fingertips, the brush 33 squares from the butt of the shaft to the point, exactly as in image A. Lay the body along the skeleton: the torso and the coat along the green line, each leg along its line (bending at the dots: the dark green cropped trousers with the teal ribbon bow, the bare shin, the brown loafer - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow from the shoulders, never floating; the indigo sleeve with its red-orange cuff), the far hand GRIPPING the brush where the purple line ends. THE BRUSH drawn along the bar at the design's length and thickness: the dark shaft with its coloured bands, the red and navy head where the magenta part is, the wooden point where the cyan part is. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both dark green eyes under their heavy lids, the mouth, the earrings, the choker, the messy hair) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or part of the brush covers the face (the eyes and the mouth). THE CRESCENT of paint drawn square for square as in image A where the pale blue shape is.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no paint splashes, no fire, no lightning, no eyes, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - the body twisting to the image left, the FAR arm drawing the brush across in front of his waist so it lies level with its point to the image left, the near arm hanging back to the left, the feet apart.`
- a_flick: `FLICK - leaning forward, the FAR arm stretched forward level, the brush flicked out to the image right (the point to the right and a little up, at shoulder height), the near arm flung back, the front (far) knee bent.`
- q_wind: `RAISE - leaning back a little, the FAR arm lifting the brush high above his far shoulder (the point up and a little to the right, never over the face), the near arm reaching forward, the near leg in front.`
- q_throw: `THROW - a big step forward, leaning forward, the FAR arm swinging the brush down forward (the point to the lower right), the near arm flung back, the back (near) leg stretched out behind.`
- qw_raise: `CALL THE BOLT - hopping up on his toes (the feet about 4 squares up), the knees bent, the FAR arm holding the brush straight up above his head (the point up), the near arm flung up and out to the upper left.`
- qw_point: `POINT DOWN - a deep low lunge, leaning forward, the FAR arm pointing the brush forward and down at the ground (the point to the lower right, nearly touching the ground), the near arm stretched back, the back (near) leg straight out behind.`
- qe_raise: `LEAP WITH THE BRUSH - leaping up (the feet about 6 squares up), both knees tucked, the FAR hand holding the brush upright in front of him on the image right (the point DOWN), the near arm flung out to the left.`
- qe_slam: `STAB DOWN - landed in a deep low crouch, the FAR hand driving the brush down in front of him, its point touching the ground at the image right, the near arm flung back to the left.`
- ew_low: `LOW SWEEP - a wide low stance, leaning forward, the FAR arm sweeping the brush down to the lower left behind him (the point to the lower left, near the ground), the near arm flung out to the left.`
- ew_high: `HIGH POINT - standing tall, the FAR arm raising the brush high to the upper right (the point to the upper right, never over the face), the near arm hanging at his side, the near leg in front.`
- ee_wind: `DRAW BACK - in a lunge, twisting to the image left, the FAR arm pulling the brush back level behind him to the image left (the point to the left, at chest height, below the face), the near arm flung back to the left.`
- ee_swing: `CHOP - pressing forward low, the FAR arm chopping the brush down forward (the point to the lower right), the near arm flung back, the front (far) knee bent.`
- r_open: `ARMS WIDE - standing tall, both arms spread wide, the FAR hand holding the brush out level to the image right (the point to the right), the near hand open, palm up, out to the left.`
- r_fling: `FLING - leaning forward, the FAR arm flinging the brush forward hard (the point to the right and a little down), the near arm flung back, a big step forward.`
- r_hop: `HOP - a light hop (the feet about 6 squares up), both knees tucked, the FAR arm drawing the brush back level behind him at his waist (the point to the image left), the near arm bent before his chest.`
- run1: `RUN 1 - the FAR leg forward with its foot landing, the NEAR leg kicked up behind him, leaning forward a little, the FAR hand trailing the brush down to the lower right as in the design, the near arm swinging back.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, the brush trailing to the lower right as before, the near arm swinging down.`
- run3: `RUN 3 - the NEAR leg forward with its foot landing, the FAR leg kicked up behind him, leaning forward a little, the brush trailing to the lower right, the near arm swinging forward.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, the brush trailing to the lower right, the near arm swinging down.`
- d_stagger: `STAGGER - reeling back toward the image left, the knees buckling, the near hand clutching his chest, the far arm hanging open, the brush dropped from his hand and lying flat on the ground in front of him on the image right.`
- d_kneel: `DOWN - kneeling on the near knee, the far knee raised, bent forward, the near hand propped on the ground, the far hand on the raised knee, the head low; the brush lying flat on the ground in front of him on the image right.`

## 交回前请检查

- **21 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- **数格子**：每条腿从胯到脚底约 18 格、手臂约 18 格、画笔 33 格，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个彗：**同一个头（照图 B，脸朝右前方、两只墨绿眼睛、耳饰、颈环、乱发）**、同样粗的腿和手臂、同样的弯月墨痕；**画笔和定稿一样长、一样粗**，红蓝笔头和木色笔尖清楚，握着它的手在笔杆上；手臂从肩膀长出来，手和画笔没有盖住脸；姿势沿着骨架；着地的脚在 y 1200。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/hwei-poses/`）

- `hwei-pose-a_wind.png`、`hwei-pose-a_flick.png`、`hwei-pose-q_wind.png`、`hwei-pose-q_throw.png`、`hwei-pose-qw_raise.png`、`hwei-pose-qw_point.png`、`hwei-pose-qe_raise.png`、`hwei-pose-qe_slam.png`、`hwei-pose-ew_low.png`、`hwei-pose-ew_high.png`、`hwei-pose-ee_wind.png`、`hwei-pose-ee_swing.png`、`hwei-pose-r_open.png`、`hwei-pose-r_fling.png`、`hwei-pose-r_hop.png`、`hwei-pose-run1.png`、`hwei-pose-run2.png`、`hwei-pose-run3.png`、`hwei-pose-run4.png`、`hwei-pose-d_stagger.png`、`hwei-pose-d_kneel.png`；原始生成图原样放 `outputs/hwei-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/hwei_poses_done.zip`。中间不要停，21 张都画完再交。

## 附图（压缩包 `hwei_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄 / 粉 / 青 = 画笔，淡蓝 = 墨痕） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 12 px，脚底 y 1200） |
| `3_a_wind_*` … `23_d_kneel_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（design_udyr_poses / design_qiyana_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂和画笔的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就照奇亚娜的 legs 包重画腿，再拼进 rig_hwei.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_hwei.py）：普攻 attack = a_wind → a_flick → 定稿；悚·阴沉变意 skill2_q 同普攻的两帧加大幅度；灾·没骨火 skill = q_wind → q_throw；灾·攒聚雷 skill_w = qw_raise → qw_point；灾·连皴山 skill_e = qe_raise → qe_slam；悚·滞涩幽瞳 skill2 = ew_low → ew_high；悚·双钩血喉 skill2_e = ee_wind → ee_swing；大招 ult = r_open → r_fling → r_hop；死亡 dead = d_stagger → d_kneel；跑 run = run1–4；待机 = 定稿一帧（hero_reels 做呼吸）；受击 hit = 定稿后退一格闪白。
