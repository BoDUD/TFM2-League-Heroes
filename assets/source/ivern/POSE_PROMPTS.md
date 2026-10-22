# 翠神 艾翁：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 艾翁和小菊的造型用户已经定稿（`2_design.png` 是你上一轮画的 A-2：3/4 正面朝右的 Q 版树人——浅灰白树皮色的小圆脸、琥珀色眼睛、大鼻子、咧嘴笑，一大把亮绿树叶胡子，两只浅灰绿羊角，头顶红色白点蘑菇，左耳边挂个小木环，棕色木头身子和树叶裙、身前一道白布条，画面左边的手举着带两片叶子的小树枝（手腕两道金环），画面右边的手托着红苹果，两条深红棕树皮腿、分叉的根脚、近侧小腿上长着红浆果；`D0_daisy.png` 是小菊：正面的青苔岩石傀儡）。
> - 英雄联盟里他扔种子、甩荆棘、蹲下跳起召唤小菊，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **15 个艾翁姿势**（11 个动作 + 4 帧跑步），再画 **6 个小菊姿势**（正面），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张艾翁都是同一个艾翁**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1200**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根，被树叶胡子盖着），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边，拿小树枝的那只）**，**紫线 = 远侧的手臂（画面右边，拿苹果的那只）**；两条手臂上**大一点的圆点是手**（小树枝 / 苹果就在那里）；**灰框 = 头的位置**（头连羊角、蘑菇，很宽）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：Q 版的腿很短——**每条腿从胯到脚底只有约 16 格**；手臂是细长的树枝，**拿树枝的手臂从肩膀到指尖约 27 格、拿苹果的约 18 格**；头连羊角 53 × 25 格。骨架就是按定稿量的：**腿、手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（上一个英雄的腿画成了正常人的长腿，只能重画——请画完数一数），**不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空。树叶胡子和定稿一样大，盖在胸前，跟着身子走。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、两只琥珀色眼睛都看得见、大鼻子、笑脸、羊角、蘑菇、小木环）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、树枝、苹果**不要盖住脸**（眼睛、鼻子、嘴）；手臂举高时从羊角旁边或羊角前面过去。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的艾翁是细长的高个子、腿占一半身高；我们的是 Q 版大头：身子短、腿短，**照骨架的长短画，不照原版的长短**。

## 15 个艾翁姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `ivern-pose-a_wind.png` | 扔种子蓄势：身子往左后方微微仰，远侧手臂（拿苹果那只，这里手里是一颗种子）往左后下方甩到身后（手在腰后），近侧手臂往前伸，两腿分开（普攻起手） |
| 4 | `ivern-pose-a_throw.png` | 扔出种子：身子往前倾，远侧手臂往右前方甩出去伸直（手在肩的高度），近侧手臂往后甩，前腿（远侧）屈膝（普攻出手） |
| 5 | `ivern-pose-e_gather.png` | 蹲下聚力：两膝弯下去蹲低，身子往前弓，两只手臂收在胸前（手心相对，像捧着一颗种子），头低一点（种豆得瓜起手） |
| 6 | `ivern-pose-e_give.png` | 抛给队友：站起来，远侧手臂往右上方伸直、手掌张开（把种子护盾抛给队友），近侧手臂往左张开，近侧腿在前（种豆得瓜放出） |
| 7 | `ivern-pose-q_wind.png` | 拧身蓄力：身子往左后方拧，近侧手臂（拿小树枝那只）往左后上方高高扬起，远侧手臂收在胸前，膝盖微弯（根深敌固起手） |
| 8 | `ivern-pose-q_fling.png` | 甩出荆棘：大步往前，身子前倾，近侧手臂从左往右前方甩出去伸直（手在腰的高度，荆棘从这里甩出），远侧手臂往后张开，后腿（近侧）往后伸直（根深敌固打出） |
| 9 | `ivern-pose-r_crouch.png` | 蹲下蓄力：深深蹲下，两膝往外分开，身子往前弓，两只手臂往下垂到膝盖边（大招起手） |
| 10 | `ivern-pose-r_leap.png` | 跃起召唤：往上跳起（脚离地约 8 格），远侧腿往下伸直、近侧腿屈膝收起，近侧手臂笔直举过头顶（召唤小菊），远侧手臂往右张开（大招跳起） |
| 11 | `ivern-pose-r_call.png` | 落地举手：站直，近侧手臂高高举起（小树枝朝上），远侧手臂垂在身边，两腿并拢站稳（大招收尾：小菊出来了） |
| 12 | `ivern-pose-run1.png` | 跑 1（远侧腿往前迈大步着地，近侧腿往后伸）：身子微微前倾，近侧手臂往后摆，远侧手臂往前摆 |
| 13 | `ivern-pose-run2.png` | 跑 2（近侧腿在身下撑地，远侧腿屈膝抬到前面）：身子高一格，两臂垂在身边 |
| 14 | `ivern-pose-run3.png` | 跑 3（近侧腿往前迈大步着地，远侧腿往后伸）：近侧手臂往前摆，远侧手臂往后摆 |
| 15 | `ivern-pose-run4.png` | 跑 4（远侧腿在身下撑地，近侧腿屈膝抬到前面）：身子高一格 |
| 16 | `ivern-pose-d_stagger.png` | 踉跄：身子往左后方倒，膝盖发软，近侧手臂往左后方甩开，远侧手臂往右伸着（苹果从手里掉下来，落在他右前方的地上）（死亡第一下） |
| 17 | `ivern-pose-d_slump.png` | 瘫坐：一屁股坐在地上，两条腿往画面右边平伸在地上，身子往前趴下去，头低下来，两只手臂软软地垂到地上；苹果在他右前方的地上（死亡） |

## 6 个小菊姿势（正面）

| 图 | 文件 | 姿势 |
|---|---|---|
| D1 | `ivern-daisy-dz_rise.png` | 钻出地面：从地里跳出来（脚离地约 6 格），两只大拳头往两边举起张开，身上掉着土块（召唤登场） |
| D2 | `ivern-daisy-dz_wind.png` | 举拳：画面左边那只大拳头高高举过头顶，另一只拳头垂在身边，身子微微往左歪（第一、二拳起手） |
| D3 | `ivern-daisy-dz_punch.png` | 砸拳：那只拳头往前下方砸下来，砸在她身前正中的地上，身子往前压（第一、二拳） |
| D4 | `ivern-daisy-dz_up.png` | 双拳举起：两只大拳头一起高高举过头顶，身子挺直（第三拳起手） |
| D5 | `ivern-daisy-dz_slam.png` | 双拳砸地：两只拳头一起砸在身前的地上，深深蹲下（第三拳：震飞敌人） |
| D6 | `ivern-daisy-dz_wave.png` | 挥手告别：画面左边那只手抬到肩膀上方挥手（手掌张开），另一只拳头垂着，身子开始往下沉（小菊离开） |

## 提示词 A：艾翁（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1200) - a chibi WALKING TREE-MAN with a BIG head: a small round face of pale grey-white bark, small amber eyes, a big nose, a wide grin, a huge beard of bright green leaves over his chest, two pale sage-green ram's horns curling out wide to the sides, a red white-spotted mushroom on his crown, a small wooden ring hanging by his ear, a brown wooden body with a leaf skirt and a white cloth strip, a thin branch arm on the image left holding a twig with two leaves (two gold rings at the wrist), a thin branch arm on the image right holding a red apple, two short dark red-brown bark legs on forked root feet, red berries on the near shin; B its HEAD with the horns and the mushroom shown 8x (53 squares wide, 25 tall); C a SKELETON on the same 1254 canvas and 12 px grid: green = the spine (pelvis to the base of the neck, under the leaf beard), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left, the twig hand), PURPLE = the FAR arm (image right, the apple hand), the bigger dot on each arm = the hand, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long realistic legs); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1200.
COUNT THE SQUARES: chibi proportions - each leg only about 16 squares from the hip to the sole, the twig arm about 27 squares from the shoulder to the fingertips and the apple arm about 18, exactly as in image A. Lay the body along the skeleton: the wooden body, the leaf skirt and the big leaf beard along the green line, each leg along its line (bending at the dots: the dark red-brown bark, the root foot - the SAME thickness, length and colours as in image A), each arm from its shoulder along its line (thin brown branches growing from the shoulders, never floating), the twig with its two leaves in the orange hand, the red apple in the purple hand (unless the pose says the hand holds a seed or drops the apple). Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both amber eyes, the big nose, the grin, both horns, the mushroom, the wooden ring) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand, twig or apple covers the face (the eyes, the nose and the mouth); a raised arm passes beside or in front of a horn.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no vines, no seeds flying, no bushes, no glow, no motion trails), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - leaning back a little toward the image left, the FAR arm (the apple hand, here holding a seed) swung down and back behind his waist, the near arm reaching forward, the legs apart.`
- a_throw: `THROW - leaning forward, the FAR arm flung out straight to the front right (the hand at shoulder height), the near arm swung back, the front (far) knee bent.`
- e_gather: `GATHER - crouching low on bent knees, hunched forward, both arms drawn in before his chest, hands facing as if cupping a seed.`
- e_give: `GIVE - standing up, the FAR arm reaching up to the upper right with the palm open (tossing the seed shield to an ally), the near arm spread out to the left, the near leg in front.`
- q_wind: `COIL - twisting back toward the image left, the NEAR arm (the twig hand) swung high up and back to the upper left, the far arm drawn in before his chest, the knees a little bent.`
- q_fling: `FLING - a big step forward, leaning forward, the NEAR arm whipped across to the front right and stretched out at waist height (the vine flies from it), the far arm flung back, the back (near) leg stretched out behind.`
- r_crouch: `CROUCH - squatting deep, the knees spread apart, hunched forward, both arms hanging down beside his knees.`
- r_leap: `LEAP - jumping up (the feet about 8 squares off the ground), the far leg stretched down, the near knee tucked, the NEAR arm thrust straight up above his head (calling Daisy), the far arm out to the right.`
- r_call: `CALL - standing tall, the NEAR arm raised high (the twig pointing up), the far arm hanging at his side, the legs close together.`
- run1: `RUN 1 - a long stride: the FAR leg reaching forward with its foot landing, the NEAR leg stretched back behind, leaning forward a little, the near arm swinging back, the far arm forward.`
- run2: `RUN 2 - the near leg under the body carrying him, the FAR knee lifted forward, the body one square higher, both arms hanging close.`
- run3: `RUN 3 - a long stride: the NEAR leg reaching forward with its foot landing, the FAR leg stretched back behind, leaning forward a little, the near arm swinging forward, the far arm back.`
- run4: `RUN 4 - the far leg under the body carrying him, the NEAR knee lifted forward, the body one square higher, both arms hanging close.`
- d_stagger: `STAGGER - toppling back toward the image left, the knees giving way, the near arm flung back to the left, the far arm reaching out to the right, the apple dropped and lying on the ground in front of him on the image right.`
- d_slump: `SLUMPED - sitting down hard on the ground, both legs stretched out flat to the image right along the ground, the body slumped forward, the head low, both arms hanging limp to the ground; the apple lying in front of him on the image right.`

## 提示词 B：小菊（每个姿势一次，换掉最后一段的姿势）

每次上传：`D0_daisy.png`（定稿）、这个姿势的 `D*_league.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art ROCK GOLEM seen from the FRONT, on a 1254x1254 canvas with 12 px squares (feet on y 1200) - a big hunched golem of mossy green stones and pale violet-grey stone faces with carved dark green spirals, two small white flowers and a small green crystal on the chest, a small dark grey pointed stone head sunk between the shoulders with a green clover sprout on top, two huge stone fists, short thick legs; B the original golem in this pose, seen from the front (copy the POSE from it, never its 3D look).
Draw with the image generator ONE clean pixel-art picture of the golem of image A in the POSE of image B, still seen from the FRONT: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1200. The SAME golem: the same size, the same stones, colours, spirals, flowers, crystal, head and sprout; the arms are chains of stone blocks ending in the huge fists, the same thickness as in image A, only moved. Everything inside the canvas (a raised fist too).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects (no dust, no shockwave, no cracks in the ground), no background, no ground, no shadow, no text, no grid lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- dz_rise: `RISE - leaping up out of the ground (the feet about 6 squares up), both huge fists raised and spread to the sides, a few clods falling off her.`
- dz_wind: `RAISE ONE FIST - the fist on the image left raised high above her head, the other fist hanging at her side, leaning a little to the image left.`
- dz_punch: `SMASH ONE FIST - that fist smashed down to the ground in front of her middle, the body pressing forward and down.`
- dz_up: `BOTH FISTS UP - both huge fists raised high above her head together, the body upright.`
- dz_slam: `SLAM - both fists slammed into the ground in front of her together, crouching deep.`
- dz_wave: `WAVE GOODBYE - the hand on the image left raised above her shoulder, open, waving, the other fist hanging, the body starting to sink.`

## 交回前请检查

- **21 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样）。
- **数格子**：艾翁每条腿从胯到脚底约 16 格、拿树枝的手臂约 27 格、拿苹果的约 18 格，和定稿一样——腿画长了就重画。
- 每张艾翁都是定稿的同一个艾翁：**同一个头（照图 B，脸朝右前方、两只琥珀色眼睛、大鼻子、笑脸、羊角、蘑菇）**、同样大的树叶胡子、同样粗的腿和树枝手臂；手臂从肩膀长出来，手、树枝、苹果没有盖住脸；姿势沿着骨架；着地的脚在 y 1200。
- 每张小菊都是定稿的同一个小菊，**正面**，大小、石块、花纹、白花、水晶、头顶嫩芽都一样；举起的拳头不出画。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/ivern-poses/`）

- `ivern-pose-a_wind.png`、`ivern-pose-a_throw.png`、`ivern-pose-e_gather.png`、`ivern-pose-e_give.png`、`ivern-pose-q_wind.png`、`ivern-pose-q_fling.png`、`ivern-pose-r_crouch.png`、`ivern-pose-r_leap.png`、`ivern-pose-r_call.png`、`ivern-pose-run1.png`、`ivern-pose-run2.png`、`ivern-pose-run3.png`、`ivern-pose-run4.png`、`ivern-pose-d_stagger.png`、`ivern-pose-d_slump.png`；
- `ivern-daisy-dz_rise.png`、`ivern-daisy-dz_wind.png`、`ivern-daisy-dz_punch.png`、`ivern-daisy-dz_up.png`、`ivern-daisy-dz_slam.png`、`ivern-daisy-dz_wave.png`；
- 原始生成图原样放 `outputs/ivern-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/ivern_poses_done.zip`。中间不要停，21 张都画完再交。

## 附图（压缩包 `ivern_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手） |
| `1_head.png` | 定稿的头（8 倍，连羊角和蘑菇）：每个姿势都照它逐格画 |
| `2_design.png` | 艾翁定稿（每格 12 px，脚底 y 1200） |
| `3_a_wind_*` … `17_d_slump_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |
| `D0_daisy.png` | 小菊定稿（正面，每格 12 px，脚底 y 1200） |
| `D1_dz_rise_league.png` … `D6_dz_wave_league.png` | 小菊每个姿势的英雄联盟原版那一帧（正面） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（design_hwei_poses / design_qiyana_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），腿长了就照奇亚娜的 legs 包重画腿，再拼进 rig_ivern.py 的动作里，逐帧自查后才发合成 GIF。小菊按她自己的格子读回（PPU 1.9），对到 hd/daisy.png 的调色板。
- 动作安排（照英雄联盟，标签见 tools/kit/build_ivern.py）：普攻 attack = a_wind → a_throw → 定稿；种豆得瓜 skill = e_gather → e_give；根深敌固 skill2 = q_wind → q_fling；大招 ult = r_crouch → r_leap → r_call；死亡 dead = d_stagger → d_slump；跑 run = run1–4；待机 = 定稿一帧（hero_reels 做呼吸）；受击 hit = 定稿后退一格闪白。小菊（特效图，正面）：r_drop = dz_rise，r_punch = dz_wind → dz_punch，r_slam = dz_up → dz_slam，离开 = dz_wave。
