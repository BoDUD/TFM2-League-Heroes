# 诺拉与悠米：诺拉的动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 诺拉的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A 第一版，缩到游戏大小定稿：3/4 正面朝右的约德尔小法师——全身米黄 / 浅杏色绒毛，两只长长的垂耳；高高的青绿色礼帽（红头巾、米白骨珠环、一蓝一粉两根羽毛）；粉框大圆眼镜；红围巾、白色圆骨扣；长到脚面的蓝紫长袍，中间垂着一条红腰带；**近侧那只手（画面左边）握着一个金色小圆环**（金边、里面是紫色的次元门），这是用户新加的，金铲铲里她一直拿着它；远侧那只手（画面右边）垂在长袍旁）。
> - 她的动作照视频来做（金铲铲官方介绍里的棋子动作、英雄联盟手游里的诺拉），靠挪动定稿的部件摆不出来，所以请你按骨架画 **13 个姿势**（7 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个诺拉**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 14 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子根，红围巾下面），**红线 = 近侧的腿（画面左边那条）**，**蓝线 = 远侧的腿（画面右边那条）**——腿很短，大部分藏在长袍里，**长袍下摆跟着腿动**，只露出深色的小鞋；**紫线 = 远侧的手臂（画面右边，指人、抛球的那只）**，**橙线 = 近侧的手臂（画面左边，拿金环的那只）**；手臂线的第一个点是肩膀，**大一点的圆点是手**；**灰框 = 头的位置**（帽子、头巾、眼镜、脸）；**金色圆圈 = 金环**（没有金色圆圈 = 手里没有金环）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：约德尔人，头和帽子很大、手脚很短——**每条手臂从肩膀到手指尖约 13 格**，**腿从胯到脚底约 10 格**（藏在长袍里）；头（帽子连脸）37 × 47 格；**金环直径约 7 格**（都和定稿一样，不放大不缩短）。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**（之前一个英雄的手脚画成了正常人的长度，只能重画——请画完数一数）。手臂从长袍宽袖里长出来，袖口的金色小穗子跟着手；长袍、红腰带、背后的小背包跟着身子走。
> - **两只垂耳跟着头**：从头的两边垂下来，近侧那只（画面左边）在前面、远侧那只暗一档；跑和被打倒时往后甩。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、高礼帽、两片粉框圆镜片一样高）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、金环**不要盖住脸**（眼镜和嘴）；举起来的手臂从脸的旁边过去，可以挡住垂耳和帽子边，不能挡眼镜。
> - 每个姿势附一张视频里的那几帧（`*_video.png`，金铲铲的是从上往下看的棋盘镜头，手游的是峡谷镜头），**动作照它**，长相照定稿；视频里没有的细节（比如拿金环的是哪只手）照骨架；视频里没有死亡，最后两张（被打倒、坐倒）只照文字和骨架。

## 13 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `norra-pose-a_wind.png` | 普攻起手：身子微微往后收，指人的那只手（远侧，画面右边）弯起来收到胸前、食指竖起，拿金环的手（近侧，画面左边）往身后摆开，两脚稍稍分开（普攻蓄力） |
| 4 | `norra-pose-a_point.png` | 普攻指向：远侧那只手往前上方（画面右上）伸直，食指指着目标（魔法弹从这里飞出去，手在头的右边，不挡脸），拿金环的手往身后下方摆，身子往前倾一点，前脚往前迈（普攻打出） |
| 5 | `norra-pose-q_swirl.png` | 开门蓄力：膝盖微弯、身子缩一点，两只手捧在胸前（在下巴下面，不挡脸），金环举在两手之间，帽子和垂耳跟着往下压（次元门狂欢起手：次元门在她身边打开，特效以后画） |
| 6 | `norra-pose-q_throw.png` | 抛球：踮起脚、身子往上伸直，远侧那只手笔直举过头顶、在头的右边往前上方一扬（次元球从手里抛出去了，手张开），拿金环的手放在身侧（次元门狂欢抛出） |
| 7 | `norra-pose-e_open.png` | 举环开门：拿金环的手（近侧，画面左边）高高举向左上方，把金环举在头的左边（不挡脸），远侧那只手往身侧（画面右边）张开、手掌朝外，身子挺直（异界来物：开出次元门） |
| 8 | `norra-pose-r_raise.png` | 双手高举：整个人往上浮起（脚离地约 3 格），两只手臂在头的两边高高举起成 V 字（不挡脸），金环举在近侧那只手里，长袍下摆往下垂、往外扬（门槛之书：头顶打开大门） |
| 9 | `norra-pose-r_cast.png` | 往下压：落回地面、身子往前倾，两只手一起往前下方（画面右下）推出去，手掌朝下（把书页从门里压下去），金环在近侧手里（门槛之书：落下） |
| 10 | `norra-pose-run1.png` | 跑 1（远侧脚往前迈、着地，近侧脚在后面蹬）：小碎步，身子往前倾，长袍下摆往后飘，两只垂耳往后甩，两只手稍稍张开在身侧（拿金环的近侧手往后、远侧手往前摆） |
| 11 | `norra-pose-run2.png` | 跑 2（近侧脚在身下撑地，远侧脚抬起来往前收）：身子高一格，两只手摆回身边 |
| 12 | `norra-pose-run3.png` | 跑 3（近侧脚往前迈、着地，远侧脚在后面蹬）：身子往前倾，拿金环的近侧手往前摆，远侧手往后摆 |
| 13 | `norra-pose-run4.png` | 跑 4（远侧脚在身下撑地，近侧脚抬起来往前收）：身子高一格，两只手摆回身边 |
| 14 | `norra-pose-d_fall.png` | 被打倒：被打得往后（画面左边）仰倒、膝盖发软，两只手臂往上甩开（不挡脸），金环从手里飞出去（手里空了），帽子跟着头往后仰（死亡第一下） |
| 15 | `norra-pose-d_down.png` | 坐倒在地：一屁股坐在地上，长袍铺在身下，两条短腿往前伸，两只手撑在身后的地上，头微微垂下，金环掉在她身前的地上（死亡：倒地） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_video.png`（死亡两张没有），有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 14 px squares (soles on y 1176) - a chibi YORDLE MAGE GIRL covered in cream / sandy-peach fur with TWO LONG FLOPPY EARS hanging beside her face, a VERY TALL TEAL TOP HAT (a red head wrap, a ring of bone-white beads, a blue and a magenta feather), BIG ROUND PINK-FRAMED GLASSES, a red scarf with a white bone clasp, a long BLUE-PURPLE ROBE down to her feet with a red sash hanging down the front, wide sleeves with little gold tassels; her NEAR hand (image left) holding a SMALL GOLD RING with a purple portal inside, her far hand (image right) by the robe; B its HEAD shown 8x (37 squares wide, 47 tall: the hat, the head wrap, the glasses, the face); C a SKELETON on the same 1254 canvas and 14 px grid: green = the spine (pelvis to the base of the neck, under the scarf), RED = the NEAR leg (image left), BLUE = the FAR leg (image right) - both short and mostly hidden by the robe, PURPLE = the FAR arm (image right, the arm that points and throws), ORANGE = the NEAR arm (image left, the arm holding the ring), each arm line starting at the shoulder, the bigger dot on each arm = the hand, GREY BOX = where the head goes, the GOLD CIRCLE = where the gold ring goes (no gold circle: no ring in her hand), the red horizontal line = the ground; D frames of this character doing this move, cut from game videos (copy the POSE from them, never their 3D look or their camera); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 14 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1176.
COUNT THE SQUARES: yordle proportions - each arm about 13 squares from the shoulder to the fingertips, the legs about 10 squares from the hip to the sole (inside the robe), the gold ring about 7 squares across, exactly as in image A. Lay the body along the skeleton: the robe and the red sash along the green line, the robe's hem moving with the legs (only the small dark shoes showing under it), each arm from its wide sleeve along its line (the furry forearm and small hand, the gold tassels at the cuff, never floating), the two floppy ears hanging from the head and swinging with the move, the little backpack on her back. THE RING: the same gold ring as in image A drawn exactly on the gold circle, held in the near hand. Never stretch or shorten an arm, a leg or the ring, never paste a straight limb turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the tall teal hat with its feathers and bead ring, the red head wrap, the face to the front-right, both pink-framed lenses at the same height) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand or the ring covers the face (the glasses and the mouth); a raised arm passes beside the face, over an ear or the hat's brim at most.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no portals, no magic bolts, no portal ball, no paint, no light, no dust, no motion lines), no Yuumi, no book, no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - leaning back a little, the POINT hand (the far one, image right) drawn in to her chest with the index finger up, the RING hand (the near one, image left) swung out behind her, the feet a little apart.`
- a_point: `POINT - the POINT arm (far, image right) stretched straight out to the upper right (up 40 degrees, beside her head, never over the face), the index finger pointing at the target, the RING arm (near) swung down and back, the body leaning a little forward, the front foot forward.`
- q_swirl: `GATHER - the knees a little bent, the body drawn in, BOTH hands held together before her chest under her chin (never over the face) with the RING held between them, the hat and the ears dipping with her.`
- q_throw: `THROW UP - on tiptoe and stretching tall, the POINT arm (far) thrust straight UP beside the right of her head and a little forward (the hand open: the portal ball has just left it; never over the face), the RING hand (near) down at her side.`
- e_open: `RAISE THE RING - the RING arm (near, image left) lifted high to the upper left, the ring held up beside the left of her head (never over the face), the POINT arm (far) spread out to her side on the image right with the palm open, the body straight.`
- r_raise: `BOTH ARMS UP - floating up off the ground (the feet about 3 squares up), BOTH arms raised high on either side of her head in a V (never over the face; the ring in the near hand), the robe's hem hanging and flaring.`
- r_cast: `PUSH DOWN - landed again and leaning forward, BOTH arms thrust out together to the lower right (the palms down, pushing the page down through the gate), the ring in the near hand.`
- run1: `RUN 1 - little steps: the FAR foot reaching forward and landing, the NEAR foot pushing off behind, the body leaning forward, the robe's hem and both ears swinging back, the arms a little out at her sides (the near one with the ring back, the far one forward).`
- run2: `RUN 2 - the near foot under her carrying her, the FAR foot lifted and coming forward, the body one square higher, both arms passing close to her sides.`
- run3: `RUN 3 - little steps: the NEAR foot reaching forward and landing, the FAR foot pushing off behind, the body leaning forward, the near arm with the ring swinging forward, the far arm back.`
- run4: `RUN 4 - the far foot under her carrying her, the NEAR foot lifted and coming forward, the body one square higher, both arms passing close to her sides.`
- d_fall: `KNOCKED BACK - thrown back toward the image left, the knees giving way, both arms flung up (never over the face), the RING flying out of her hand (the hand empty), the hat going back with her head.`
- d_down: `SAT DOWN - sat down on the ground, the robe spread under her, the short legs stuck out in front, both hands propped on the ground behind her, the head hanging a little, the RING lying on the ground in front of her.`

## 交回前请检查

- **13 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 14 px**（和定稿一样）。
- **数格子**：每条手臂约 13 格、腿约 10 格（藏在长袍里）、金环直径约 7 格，和定稿一样——手臂画长了就重画。
- 每张都是定稿的同一个诺拉：**同一个头（照图 B：高礼帽、红头巾、骨珠环、两根羽毛、两片粉框圆镜片一样高、脸朝右前方）**、同样短的手臂、同样的蓝紫长袍和红腰带、两只垂耳；金环在金色圆圈的位置、握在近侧手里（被打倒和坐倒两张没有拿在手里）；手、金环没有盖住脸；姿势沿着骨架；着地的脚在 y 1176。
- 所有图没有特效（次元门、魔法弹、次元球、纸画颜料、光都不画）、没有悠米、没有书、没有骨架线、没有网格线、没有辅助形状。

## 交付（`outputs/norra-poses/`）

- `norra-pose-a_wind.png`、`norra-pose-a_point.png`、`norra-pose-q_swirl.png`、`norra-pose-q_throw.png`、`norra-pose-e_open.png`、`norra-pose-r_raise.png`、`norra-pose-r_cast.png`、`norra-pose-run1.png`、`norra-pose-run2.png`、`norra-pose-run3.png`、`norra-pose-run4.png`、`norra-pose-d_fall.png`、`norra-pose-d_down.png`；
- 原始生成图原样放 `outputs/norra-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/norra_poses_done.zip`。中间不要停，13 张都画完再交。

## 附图（压缩包 `norra_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分，大圆点 = 手，金色圆圈 = 金环） |
| `1_head.png` | 定稿的头（8 倍，帽子、头巾、眼镜、脸）：每个姿势都照它逐格画 |
| `2_design.png` | 诺拉定稿（每格 14 px，脚底 y 1176，近侧手里握着金环） |
| `3_a_wind_*` … `15_d_down_*` | 每个姿势的骨架（`_skeleton`）和视频里的那几帧（`_video`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 14 px），按格读回（design_locke_poses 的做法：按头的大小定比例，头换成定稿的头），颜色对到定稿的调色板；**先在 8 倍下量每条手臂的长短粗细、金环的大小，和定稿比**（codex-legs-need-skeletons），手臂长了就重画，再拼进 rig_norra.py 的动作里，逐帧自查后才发合成 GIF（带技能的 GIF 也要）。
- 动作安排（标签见 tools/kit/build_norra.py）：普攻 attack = a_wind → a_point → 定稿；次元门狂欢 skill = q_swirl → q_throw；异界来物 skill2 = e_open；门槛之书 ult = r_raise → r_cast；死亡 dead = d_fall → d_down；跑 run = run1–4；待机 = 定稿一帧（hero_reels）；受击 hit = 定稿后退一格闪白。
- 视频来源（只在本地，不提交）：C:/t/nr_work/video_refs（YouTube 1RTOUNxqAA4 金铲铲官方介绍、wpwNeNiKPz0 手游 Wild Rift presents: Norra）。
