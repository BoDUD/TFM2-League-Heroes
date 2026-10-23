# 双界灵兔 阿萝拉：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 阿萝拉的造型用户已经定稿（`2_design.png`，你上一轮画的 A-2：3/4 正面朝右的 Q 版兔子女巫——铜红卷发和两条麻花辫、圆金框眼镜后面的紫蓝眼睛、青绿宽檐女巫帽和金边、红羽毛、两只从帽子里竖起来的长兔耳朵、米白高领、浅蓝白毛边披肩、米白长外套和后摆、青绿胸布、棕色编织腰带、深棕过膝长袜、白毛边短靴，身后一团蓬松的橙色兔尾巴，远侧的手（画面右边）握着一根细长的魔杖扛在肩上，杖身从头的后面往左上方斜伸出去，杖头一格蓝光）。英雄联盟里她每个动作都挥着魔杖——举起来、往前点、甩出去、竖起来、往下指、两手握着推出去、跳起来、往后跳——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **17 个姿势，每个一张图**（13 个动作姿势 + 4 帧跑步）。待机、挨打我从定稿本身来做，不用画。
> - **每张图都是同一个阿萝拉**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1197**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边）**，**紫线 = 远侧的手臂（画面右边，握魔杖的那只）**；**魔杖是一根直的细长条：黄色 = 杖身，青色 = 杖头的蓝光**；紫线的末端就在杖身上（那里是手握着魔杖的地方）；**灰框 = 头的位置（连帽子和兔耳朵）**；**半透明的橙色形状 = 身后的兔尾巴**（和定稿里一模一样，只跟着腰移动）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的大头——**头连帽子和耳朵 48 × 56 格，占了一半多的身高**；身子和腿很短——**每条腿从胯到脚底只有约 24 格**，**手臂从肩膀到指尖约 23 格**，**魔杖从杖尾到杖头 62 格**（很长，比她的身子还长）。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（以前的英雄腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。**魔杖和定稿一样长、一样细**，只是换了方向。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、圆眼镜后两只紫蓝眼睛都看得见、帽子、羽毛、两只长兔耳朵、麻花辫）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、魔杖**不要盖住脸**（眼镜、眼睛和嘴）。她的手臂很短，举不过这么大的头：**魔杖举起来时在头的右边，扛在肩上时从头的后面穿过去（和定稿一样，头挡住中间那一段）**。**兔尾巴照定稿画在半透明橙色的位置**，形状不变。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的阿萝拉是正常比例；我们的是 Q 版大头：身子短、手臂短、腿短，**手臂往两边、往前、往后、往上伸，不要从脸前面横过去**。

## 17 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `aurora-pose-a_wind.png` | 举杖：站直，远侧手把魔杖举到头的右边（杖头朝右上方，不挡脸），近侧手臂往左边张开（普攻起手） |
| 4 | `aurora-pose-a_point.png` | 点出：身子往前倾，远侧手臂往前平伸，魔杖往右前方点出去（杖头朝右、略往上，肩的高度），近侧手臂往后甩，两腿分开（普攻出手） |
| 5 | `aurora-pose-q_wind.png` | 蓄力：轻轻跳起（脚离地约 3 格），身子往后仰，远侧手把魔杖竖着举在头的右边（杖头朝上，不挡脸），近侧手臂往左上方扬起（飞去来咒起手） |
| 6 | `aurora-pose-q_cast.png` | 甩出：大步往前，身子前倾，远侧手臂把魔杖往右前下方甩出去（杖头朝右下方），近侧手臂往左张开，两腿大大分开（飞去来咒放出） |
| 7 | `aurora-pose-q_catch.png` | 收回：踮脚站高（脚离地约 2 格），远侧手把魔杖笔直举在身子右边（杖头朝上，不挡脸），近侧手臂往左张开、手掌朝上，像在接住飞回来的东西（飞去来咒收回） |
| 8 | `aurora-pose-e_push.png` | 蹲下推出：两膝往外分开深深蹲下，身子前倾，两只手一起握着魔杖往右前下方推出去（杖头朝右下方），尾巴翘在身后（怪奇喷涌放出） |
| 9 | `aurora-pose-e_hop.png` | 向后跳：往后（画面左边）跳起（脚离地约 10 格），两膝收起，身子往后仰，远侧手把魔杖扛回肩上（和定稿一样），近侧手臂往前伸（怪奇喷涌后跳） |
| 10 | `aurora-pose-r_reach.png` | 踮脚张开：踮起脚站得高高的，近侧手臂往左边平平张开，远侧手把魔杖往右下方斜指（杖头朝右下方），像要往前一跃（双界合一起手） |
| 11 | `aurora-pose-r_leap.png` | 高高跃起：往右上方跳得很高（脚离地约 12 格），两膝收在身下，远侧手把魔杖扛在肩上（和定稿一样），近侧手臂往左后方张开（双界合一跳起） |
| 12 | `aurora-pose-r_land.png` | 落地：两膝并拢蹲下落地，身子前倾，远侧手把魔杖往右前下方指向地面（杖头快碰到地），近侧手臂往左张开保持平衡（双界合一落地、冲击波） |
| 13 | `aurora-pose-w_hop.png` | 翻身后跳：往后（画面左边）高高跳起（脚离地约 10 格），整个人缩成一团，两膝收到胸前，远侧手把魔杖抱在肩上，近侧手臂抱住膝盖，尾巴甩在身后（灵纱洞开） |
| 14 | `aurora-pose-run1.png` | 跑 1（远侧腿往前迈出着地，近侧腿往后伸）：身子微微前倾，魔杖扛在肩上（和定稿一样），近侧手臂往后摆 |
| 15 | `aurora-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，魔杖一样扛在肩上 |
| 16 | `aurora-pose-run3.png` | 跑 3（近侧腿往前迈出着地，远侧腿往后伸） |
| 17 | `aurora-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格 |
| 18 | `aurora-pose-d_stagger.png` | 踉跄：身子往左后方倒，膝盖弯下去，两只手臂往两边张开，魔杖从手里松开、斜斜地往右下方垂着（死亡第一下） |
| 19 | `aurora-pose-d_slump.png` | 坐倒：一屁股坐在地上，两腿往前（画面右边）伸，膝盖微微弯，身子往后仰，近侧手撑在身后的地上，远侧手搭在腿上；魔杖平躺在她身下的地上，杖头朝左（死亡） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (soles on y 1197) - a chibi PETITE BUNNY WITCH with a VERY BIG head: curly copper-red hair with two short braids, round thin gold glasses over violet-blue eyes, a wide teal witch hat with a gold brim and red feathers, TWO LONG RABBIT EARS (orange-red outside, pale pink inside) rising through the hat, a cream high collar, a pale blue-white fur-trimmed shawl, a cream long coat with tails, a teal chest panel, a brown braided belt, dark brown thigh-high stockings, short boots with white fur trim, a FLUFFY ORANGE TAIL behind her, and a LONG SLIM WAND in her far hand (a dark brown shaft with gold fittings, a blue glowing tip, a red butt) resting on her shoulder and passing BEHIND her head; B its HEAD with the hat and the ears shown 8x (48 squares wide, 56 tall); C a SKELETON on the same 1254 canvas and 9 px grid: green = the spine (pelvis to the base of the neck), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left), PURPLE = the FAR arm (image right, the one holding the wand), the WAND as one straight thin bar - YELLOW = the shaft, CYAN = the blue glowing tip - the purple arm ends on the shaft where the hand grips it, GREY BOX = where the head goes (with the hat and the ears), the TRANSLUCENT ORANGE shape = the tail behind her (exactly as in the design, only moved with her waist), the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE and the wand's swing from it, never its 3D look or its realistic proportions); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1197.
COUNT THE SQUARES: chibi proportions - the head with the hat and the ears 48 x 56 squares, more than half of her height; each leg only about 24 squares from the hip to the sole, each arm about 23 squares from the shoulder to the fingertips, the wand 62 squares from the butt to the tip, exactly as in image A. Lay the body along the skeleton: the torso, the shawl and the coat along the green line (the coat tails hanging behind), each leg along its line (bending at the dots: the dark brown stocking with its cream top, the boot with white fur trim - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (the arms grow from the shoulders, never floating; the cream sleeve and glove), the far hand GRIPPING the wand where the purple line ends. THE WAND drawn along the bar at the design's length and thickness: the dark brown shaft with gold fittings, one blue glowing square at the tip where the cyan part is, a red square at the butt. Where the wand's bar runs through the grey box it passes BEHIND the head (hidden by it), as in image A. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, the round gold glasses, both violet-blue eyes, the smile, the copper hair and braids, the teal hat with its gold brim and red feathers, the two long ears) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or part of the wand covers the face (the glasses and the mouth). THE TAIL drawn square for square as in image A where the translucent orange shape is.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no spirits, no magic trails, no shockwaves, no sparkles, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `RAISE - standing tall, the FAR hand lifting the wand up beside her head on the image right (the tip to the upper right, never over the face), the near arm opened out to the left.`
- a_point: `POINT - leaning forward, the FAR arm stretched forward level, the wand thrust out to the image right (the tip to the right and a little up, at shoulder height), the near arm flung back, the feet apart.`
- q_wind: `WIND-UP - a small hop (the feet about 3 squares up), leaning back, the FAR hand holding the wand upright beside her head on the image right (the tip UP, never over the face), the near arm flung up to the upper left.`
- q_cast: `CAST - a big step forward, leaning forward, the FAR arm sweeping the wand out to the lower right (the tip to the lower right), the near arm flung out to the left, the legs wide apart.`
- q_catch: `RECALL - up on her toes (the feet about 2 squares up), the FAR hand holding the wand straight up at her side on the image right (the tip UP, never over the face), the near arm open to the left, palm up, as if catching something flying back.`
- e_push: `BLAST - squatting deep with the knees spread apart, leaning forward, BOTH hands holding the wand and thrusting it out to the lower right (the tip to the lower right), the tail up behind her.`
- e_hop: `HOP BACK - jumping back toward the image left (the feet about 10 squares up), both knees tucked, leaning back, the FAR hand resting the wand on her shoulder again as in the design, the near arm reaching forward.`
- r_reach: `REACH - standing tall on her toes, the near arm spread out level to the left, the FAR hand pointing the wand down to the lower right (the tip to the lower right), about to leap.`
- r_leap: `LEAP - jumping high to the upper right (the feet about 12 squares up), both knees tucked under her, the FAR hand resting the wand on her shoulder as in the design, the near arm flung back to the left.`
- r_land: `LAND - landing in a crouch with the knees together, leaning forward, the FAR hand pointing the wand down at the ground to the lower right (the tip nearly touching the ground), the near arm out to the left for balance.`
- w_hop: `VEIL HOP - leaping high back toward the image left (the feet about 10 squares up), curled up in a ball, both knees pulled up to the chest, the FAR hand holding the wand on her shoulder, the near arm hugging the knees, the tail flung out behind her.`
- run1: `RUN 1 - a stride: the FAR leg forward with its foot landing, the NEAR leg stretched back, leaning forward a little, the wand resting on her shoulder as in the design, the near arm swinging back.`
- run2: `RUN 2 - the near leg under the body carrying her, the FAR knee lifted forward, the body one square higher, the wand on her shoulder as before, the near arm swinging down.`
- run3: `RUN 3 - the NEAR leg forward with its foot landing, the FAR leg stretched back, leaning forward a little, the wand on her shoulder, the near arm swinging forward.`
- run4: `RUN 4 - the far leg under the body carrying her, the NEAR knee lifted forward, the body one square higher, the wand on her shoulder, the near arm swinging down.`
- d_stagger: `STAGGER - reeling back toward the image left, the knees buckling, both arms flung out to the sides, the wand slipping in the far hand, hanging down to the lower right.`
- d_slump: `DOWN - sitting down on the ground, both legs stretched forward to the image right with the knees a little bent, leaning back, the near hand propped on the ground behind her, the far hand resting on her leg; the wand lying flat on the ground under her, its tip to the image left.`

## 交回前请检查

- **17 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 9 px**（和定稿一样）。
- **数格子**：头 48 × 56 格、每条腿从胯到脚底约 24 格、手臂约 23 格、魔杖 62 格，和定稿一样——腿画长了就重画。
- 每张都是定稿的同一个阿萝拉：**同一个头（照图 B，脸朝右前方、圆眼镜、两只紫蓝眼睛、帽子、两只长耳朵）**、同样粗的腿和手臂、同样的兔尾巴；**魔杖和定稿一样长、一样细**，杖头一格蓝光，握着它的手在杖身上；手臂从肩膀长出来，手和魔杖没有盖住脸；姿势沿着骨架；着地的脚在 y 1197。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/aurora-poses/`）

- `aurora-pose-a_wind.png`、`aurora-pose-a_point.png`、`aurora-pose-q_wind.png`、`aurora-pose-q_cast.png`、`aurora-pose-q_catch.png`、`aurora-pose-e_push.png`、`aurora-pose-e_hop.png`、`aurora-pose-r_reach.png`、`aurora-pose-r_leap.png`、`aurora-pose-r_land.png`、`aurora-pose-w_hop.png`、`aurora-pose-run1.png`、`aurora-pose-run2.png`、`aurora-pose-run3.png`、`aurora-pose-run4.png`、`aurora-pose-d_stagger.png`、`aurora-pose-d_slump.png`；原始生成图原样放 `outputs/aurora-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/aurora_poses_done.zip`。中间不要停，17 张都画完再交。

## 附图（压缩包 `aurora_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，黄 / 青 = 魔杖，半透明橙 = 尾巴） |
| `1_head.png` | 定稿的头（连帽子和耳朵，8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 9 px，脚底 y 1197） |
| `3_a_wind_*` … `19_d_slump_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 9 px），按格读回（design_illaoi_poses 的做法：按头的大小定比例，头换成定稿的头——头框里魔杖穿过的那一段要留出来），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂和魔杖的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就照 legs 包重画腿，再拼进 rig_aurora.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟，标签见 tools/kit/build_aurora.py）：普攻 attack = a_wind → a_point；飞去来咒 skill = q_wind → q_cast → q_catch；怪奇喷涌 skill2 = e_push → e_hop；双界合一 ult = r_reach → r_leap → r_land；灵纱洞开 veil = w_hop；死亡 dead = d_stagger → d_slump；跑 run = run1–4；待机 = 定稿（hero_reels 做待机和 BP 动画）；受击 hit = 定稿后退一格闪白。
