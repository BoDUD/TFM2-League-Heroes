# 可酷伯：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 可酷伯的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**画面右边（近处）的爪子抬到下巴捋白胡子、画面左边（远处）的手臂垂在身侧**；金橙色猫毛、大尖耳、雪白鬃毛和胡子、蓝发带扎的白发髻；火焰纹的粗手臂、黑爪、掌心金色漩涡；蓝色无袖短褂（白交领、白云纹）、木念珠、深红棕绳腰带、铜金大铜钱、两个金铃铛；深灰功夫裤、红棕绑腿、光脚）。
> - 请你画 **16 个姿势**（9 个动作 + 4 帧跑步 + 3 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个可酷伯**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、手臂、腿照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 / 紫线 = 两条手臂**（哪条在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 两条腿；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上：**紫线是定稿里抬到下巴的那只近处的手**，橙线是垂在身侧的远处的手。
> - **头一格一格照 `1_head.png` 画在灰框里**（大白发髻和蓝发带、两只大尖耳、白眉毛、青绿色的眼睛、深紫红鼻子、白八字胡和大胡子，脸朝右前方、微微抬着下巴）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_fall`、`d_down` 扑倒时，头跟着身体倾斜或放倒，但还是这个头）。手臂、爪子**不要盖住脸**（眼睛、鼻子和胡子）。
> - **长短要数格子**：和定稿一样，头（含耳朵和发髻）约 64 × 36 格，手臂又粗又大：从肩膀到爪尖约 28 格、粗约 12 格。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长、不要画细**；腿沿着红线 / 蓝线，又短又粗，光脚和定稿一样大。他矮壮圆滚：肚子圆、腰带和两个铃铛一直挂在肚子前面，不要画瘦。
> - **手臂的火焰纹**照定稿（橙红 / 橙 / 金黄的火舌形色块），**掌心朝外时画出金色漩涡**。

## 16 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `kobuko-pose-a_wind.png` | attack@100 | 橙 | 普攻起手：侧身压低，近处的大爪子收到腰前蓄力 |
| 3 | `kobuko-pose-a_strike.png` | attack@533 | 紫（定稿里捋胡子的那只） | 猫爪掌：近处的手臂猛地往右（画面右边）推出一掌，掌心朝前 |
| 4 | `kobuko-pose-a_back.png` | attack@1333 | 紫（定稿里捋胡子的那只） | 收势：站直，手收回（接近定稿） |
| 5 | `kobuko-pose-q_raise.png` | spell@400 | 橙 | 金爪真言起手：半蹲，双臂往上抬起，两只大爪子张开、掌心朝前（金色漩涡朝外） |
| 6 | `kobuko-pose-q_spread.png` | spell@929 | 橙 | 金爪真言：双臂向两边大大张开，挺胸（护盾套上的一刻） |
| 7 | `kobuko-pose-q_claw.png` | attack2@533 | 橙 | 金爪重掌：大步上前，近处的手掌往右前方狠狠拍出（发光的金色掌心朝外） |
| 8 | `kobuko-pose-e_crouch.png` | spell@190 | 紫（定稿里捋胡子的那只） | 猛虎扑 / 游戏结束起跳：深蹲，双爪垂到身前，准备一跃而起 |
| 9 | `kobuko-pose-e_leap.png` | leap@60 | 橙 | 腾空：整个人向上弹起，身体伸直，一条腿收起 |
| 10 | `kobuko-pose-e_land.png` | attack3@533 | 紫（定稿里捋胡子的那只） | 落地猛击：落地扎稳，双掌一起往前下方猛推（砸向敌人） |
| 11 | `kobuko-pose-run1.png` | run@0 | 紫（定稿里捋胡子的那只） | 跑步 1：圆滚滚地小跑，前脚迈出，手臂前后摆 |
| 12 | `kobuko-pose-run2.png` | run@267 | 紫（定稿里捋胡子的那只） | 跑步 2：两脚交错 |
| 13 | `kobuko-pose-run3.png` | run@533 | 橙 | 跑步 3：另一只脚迈出 |
| 14 | `kobuko-pose-run4.png` | run@800 | 紫（定稿里捋胡子的那只） | 跑步 4：两脚交错 |
| 15 | `kobuko-pose-d_hit.png` | death@60 | 紫（定稿里捋胡子的那只） | 被击中：往后一仰，双臂甩开 |
| 16 | `kobuko-pose-d_fall.png` | death@200 | 紫（定稿里捋胡子的那只） | 踉跄扑倒：身子往前栽下去 |
| 17 | `kobuko-pose-d_down.png` | death@1000 | 紫（定稿里捋胡子的那只） | 倒地：整个人趴在地上（头朝画面右边），手臂摊开 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (his soles on y 1176) - a big, round, stocky old KUNG-FU MASTER CAT: golden-orange fur, two huge pointed ears, a snow-white mane, brows, moustache and beard, a big fluffy white topknot tied with a blue ribbon, small teal-green eyes, a dark plum nose; HUGE THICK ARMS with FLAME-PATTERN fur (red-orange, orange, golden yellow), black claws, a glowing golden spiral on each palm; a sleeveless royal-blue vest with a white crossed collar and white cloud swirls, dark wooden prayer beads, a thick dark red-brown rope belt with a big bronze coin medallion and two golden bells; charcoal baggy trousers, red-brown shin wraps, bare orange cat feet; in A his near paw (image right) strokes his beard and his far arm (image left) hangs at his side; B his HEAD shown 8x (about 64 squares wide, 36 tall: the topknot, the ears, the brows, the eyes, the nose, the beard); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the arms and the legs from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE and PURPLE = his two arms (each line from the shoulder, the big dot = the hand), red / blue = his legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - the head with the ears and the topknot about 64 x 36, each arm about 28 squares from the shoulder to the claw tips and about 12 thick, short thick legs, a round belly with the belt, the coin and the two bells in front. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched, never thinner than in A; the legs along the red / blue lines, the feet as big as in A. The flame-pattern fur on the arms as in A, the golden spiral drawn on a palm that faces out. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the white topknot with the blue ribbon, both big ears, the white brows, the teal eye, the plum nose, the white moustache and beard, the face to the front-right) - the same head in every pose, only moved (tilted with the body when he falls or lies down), never turned, never redrawn as a profile. No arm or paw covers the face (the eyes, the nose, the beard).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no shield, no golden light, no shockwave, no dust, no sparkles, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - turning and crouching a little, the near big paw drawn back low at his waist, gathering force.`
- a_strike: `PALM STRIKE - the near arm thrust out hard to the image right, the open palm facing forward.`
- a_back: `RECOVER - standing up again, the arms coming back (close to the design).`
- q_raise: `MANTRA - half crouching, both huge arms lifting, the paws open with the palms (the golden spirals) facing out.`
- q_spread: `SPREAD - both arms flung wide open to the sides, chest out (the moment the shield comes on).`
- q_claw: `GOLDEN CLAW - a big step forward, the near open palm slammed out to the front-right, its glowing golden spiral facing out.`
- e_crouch: `CROUCH - squatting deep, both paws hanging low in front, coiled to spring up.`
- e_leap: `LEAP - springing up off the ground, body stretched, one leg tucked.`
- e_land: `CRASH - landed in a wide stance, both palms driven forward and down together (onto the enemy).`
- run1: `RUN 1 - a waddling jog, the front foot stepping out, the arms swinging.`
- run2: `RUN 2 - the legs passing.`
- run3: `RUN 3 - the other foot stepping out.`
- run4: `RUN 4 - the legs passing again.`
- d_hit: `STRUCK - reeling back, the arms flung out.`
- d_fall: `FALLING - pitching forward, going down.`
- d_down: `DOWN - lying face down on the ground, his head to the image right, the arms sprawled.`

## 交回

- 每个姿势一张：`outputs/kobuko-poses/kobuko-pose-<名字>.png`（1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/kobuko-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **16 张都画完再交**，最后写 `outputs/kobuko-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/kobuko_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/kobuko/codex_poses/`，**先量 Codex 实际的格子**（不一定是 12 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛鼻子还在、爪子不挡脸、手臂粗细不变、没有被压扁的身体）。
- 骨架包：`tools/art/pack_kobuko_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_kobuko_pose_md.py` 生成。
