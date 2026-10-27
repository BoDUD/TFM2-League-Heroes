# 洛里斯：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 洛里斯的造型用户已经定稿（`0_design.png` 是你第 0 步画的 B，缩到游戏大小定稿：3/4 朝右，**画面左边的手握着巨型塔盾竖在身侧、画面右边的手握拳放在胸前**；深棕乱发、蓝头巾、浓密络腮胡；宝蓝镶铜边的厚盔甲、铜金肩甲；黑手套、蓝灰裤子、深蓝铜边护腿、黑靴子；巨盾铜金框、深藏青竖条、V 字盾底、十字星徽章 + 青蓝宝石）。
> - 请你画 **16 个姿势**（9 个动作 + 4 帧跑步 + 3 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个洛里斯**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、手、巨盾照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。
> - **巨盾**：3D 模型的盾常常被透视压扁或转成侧面；**盾的样子、颜色、大小照定稿**（约 57 格高，正面朝外时约 26 格宽），只按参考图的位置和角度移动、转动。盾正面朝镜头时要画出盾面（深藏青竖条、中间铜脊、十字星徽章和青蓝宝石、V 字盾底），侧着时画成一条厚厚的铜边。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 握拳的那只手臂**，**紫线 = 拿盾的那只手臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 两条腿；**金色轮廓 = 巨盾**（模型的盾在这一帧占的地方），**金圈 = 盾的上端**（有十字星徽章的那一头）；**灰框 = 头的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **死亡的三帧（`d_fall`、`d_kneel`、`d_down`）参考图里没有盾**（那段动画把盾甩得很远，已经藏掉）：盾照每帧的说明画在他身后（画面左边）、离他很近。
> - **`e_plant` 就是你第 0 步画的 A**（巨盾立在身前、双臂搭在盾沿上），照那张的样子画，只是格子大小要和定稿一样。
> - **头一格一格照 `1_head.png` 画在灰框里**（深棕乱发、蓝头巾、浓眉、两只眼睛、络腮胡、脸朝右前方）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**（`d_kneel` 低着头、`d_down` 趴在地上时，头跟着身体倾斜或放倒，但还是这个头）。手臂、拳头、巨盾**不要盖住脸**（两只眼睛和胡子里的嘴）；举盾挡在身前时，盾在脸的右边或下面，头从盾的上沿露出来。
> - **长短要数格子**：和定稿一样，手臂从肩膀到拳头约 15 格，头（含头发）约 28 × 22 格。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。他是壮汉：肩宽、胸厚，不要画瘦。

## 16 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `loris-pose-a_wind.png` | attack2@199 | 紫（拿盾的手） | 普攻起手：半蹲，远处的手把巨盾从身侧提到身前举起来，准备抡出去 |
| 3 | `loris-pose-a_bash.png` | attack@385 | 紫（拿盾的手） | 盾击：巨盾横着抡过头顶砸向右边，近处的拳头同时往右（画面右边）打出去 |
| 4 | `loris-pose-a_back.png` | attack2@1599 | 紫（拿盾的手） | 收势：站直，巨盾回到身侧竖着，拳头收回胸前（和定稿差不多） |
| 5 | `loris-pose-q_raise.png` | spell@600 | 紫（拿盾的手） | 皮城争斗起手：压低重心，把巨盾举到身前（画面右边）挡住，准备冲锋 |
| 6 | `loris-pose-q_charge1.png` | charge@0 | 紫（拿盾的手） | 冲锋 1：顶着巨盾往右猛冲，前脚迈出，身子压在盾后面 |
| 7 | `loris-pose-q_charge2.png` | charge@237 | 紫（拿盾的手） | 冲锋 2：两脚交错，盾还顶在身前 |
| 8 | `loris-pose-e_plant.png` | idle@0 | 紫（拿盾的手） | 盾卫 / 嘲讽：巨盾立在身前的地上、双臂交叉搭在盾沿上（金铲铲的待机，第 0 步的 A） |
| 9 | `loris-pose-r_lift.png` | spell@277 | 紫（拿盾的手） | 钢铁防线举盾：双手把巨盾高高举过头顶（盾在头的右上方，不挡脸） |
| 10 | `loris-pose-r_slam.png` | spell@450 | 紫（拿盾的手） | 砸地：巨盾狠狠砸进身前的地里，人半蹲在盾后面压住 |
| 11 | `loris-pose-run1.png` | run@0 | 紫（拿盾的手） | 跑步 1：盾提在身侧沉重地小跑（金铲铲原样），前脚迈出 |
| 12 | `loris-pose-run2.png` | run@283 | 紫（拿盾的手） | 跑步 2：两脚交错 |
| 13 | `loris-pose-run3.png` | run@566 | 橙（握拳的手） | 跑步 3：另一只脚迈出 |
| 14 | `loris-pose-run4.png` | run@850 | 橙（握拳的手） | 跑步 4：两脚交错 |
| 15 | `loris-pose-d_fall.png` | death@170 | 紫（拿盾的手） | 被击倒：人被打得往后一仰、仰头，巨盾脱手、竖着往他身后（画面左边）倒 |
| 16 | `loris-pose-d_kneel.png` | death@511 | 紫（拿盾的手） | 跪倒：双膝跪地、低着头，巨盾平躺在他身后（画面左边）的地上 |
| 17 | `loris-pose-d_down.png` | death@1362 | 紫（拿盾的手） | 倒地：整个人扑倒在地上（头朝画面右边），巨盾平躺在他身后的地上 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (his soles on y 1176) - a big, burly bearded POLICEMAN with a GIANT TOWER SHIELD held upright at his side in his far hand (image left) and his near hand a fist at his chest; messy dark brown hair, a blue headband, a thick full beard; heavy royal blue armour with bronze-gold trim, bronze pauldrons; black gloves, blue-grey trousers, dark blue bronze-edged shin guards, black boots; the shield a bronze-gold frame, dark navy vertical panels, a bronze central ridge, a V-shaped bottom and a bronze four-pointed star emblem with a glowing CYAN GEM on its upper middle; B its HEAD shown 8x (about 28 squares wide, 22 tall: the hair, the headband, the brows, two eyes, the beard); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the hands and where the shield is from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = his FIST arm, PURPLE = his SHIELD arm (each line from the shoulder, the big dot = the hand), red / blue = his legs, GOLD outline = where the shield is, GOLD ring = the TOP end of the shield (the end with the star emblem), GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - each arm about 15 squares from the shoulder to the fist, the head with the hair about 28 x 22, the shield about 57 squares tall and about 26 wide seen from the front (the 3D render may squash it: keep its real size), a broad, strong body. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. The same shield as image A, only moved and turned: seen from the front show its face (the navy panels, the bronze ridge, the star emblem with the cyan gem, the V bottom), seen edge-on a thick bronze rim. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the messy hair, the blue headband, the heavy brows, both eyes, the full beard, the face to the front-right) - the same head in every pose, only moved (tilted with the body when he kneels or lies down), never turned, never redrawn as a profile. No arm, fist or shield covers the face (the eyes and the mouth in the beard): with the shield held up in front, the head shows over its top edge.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no shield bubble, no shockwave, no dust, no sparkles, no motion lines, no marks), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - dropping into a half crouch, the far arm lifting the great shield from his side up in front of him, about to swing it.`
- a_bash: `SHIELD BASH - the shield swung flat over his head toward the image right, the near fist punching out to the image right at the same time, legs braced wide.`
- a_back: `RECOVER - standing up again, the shield back upright at his side, the fist back at his chest (close to the design).`
- q_raise: `BRACE - crouching low, the great shield raised in front of him to the image right like a wall, ready to charge.`
- q_charge1: `CHARGE 1 - rushing to the image right behind the raised shield, the front foot stepping out, his weight thrown behind the shield.`
- q_charge2: `CHARGE 2 - the legs passing, the shield still held up in front.`
- e_plant: `PLANTED - the great shield standing on the ground in front of him, both forearms crossed on its top edge, his head and shoulders over it (step 0's picture A).`
- r_lift: `LIFT - both arms heaving the great shield up high above his head, the shield above the right of his head (never over the face).`
- r_slam: `SLAM - the shield driven down into the ground in front of him, he crouches behind it pressing it down.`
- run1: `RUN 1 - a heavy jog with the shield carried upright at his side (as in the game), the front foot stepping out.`
- run2: `RUN 2 - the legs passing.`
- run3: `RUN 3 - the other foot stepping out.`
- run4: `RUN 4 - the legs passing again.`
- d_fall: `STRUCK - he reels back, his head thrown up, the shield slipping from his hand and tipping over upright behind him (image left).`
- d_kneel: `KNEEL - down on his knees, head bowed, the shield lying flat on the ground just behind him (image left).`
- d_down: `DOWN - lying face down on the ground, his head to the image right, the shield lying flat on the ground just behind him (image left).`

## 交回

- 每个姿势一张：`outputs/loris-poses/loris-pose-<名字>.png`（1254 × 1254、真透明背景、每格 12 px）；原始生成图原样放进 `outputs/loris-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **16 张都画完再交**，最后写 `outputs/loris-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/loris_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/loris/codex_poses/`，**先量 Codex 实际的格子**（不一定是 12 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、眼睛和嘴还在、拳头和盾不挡脸、盾大小不变、没有被压扁的身体）。
- 骨架包：`tools/art/pack_loris_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_loris_pose_md.py` 生成。
