# 上古领主 斯卡纳：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 斯卡纳的造型用户已经定稿（`2_design.png` 是你第 0 步画的 A，按原样定稿：3/4 正面朝右的 Q 版水晶蝎子——又宽又厚的青绿 / 深石板蓝甲壳身体，甲片上橙红镶白边的部族花纹；身体最前面、甲壳下沿是一张**骨白色的骷髅小脸**（两只亮青色的小眼睛、几道橙色纹），上面罩着**银白色的头甲**；身前两只**很大的青绿钳子**（钳口内侧骨白色，橙白花纹）；背上**三根长长的分节尾巴**，末端三枚**青绿水晶毒刺 + 橙红核心**；身下**六条节肢腿**，深紫黑的钩爪）。`2b_rock.png` 是同一个他把**灰绿色的大巨石**举在尾巴上（第 0 步的 B）。
> - 英雄联盟里他用尾巴扎人、从地里掘出巨石举着再扔出去、蹦起来砸地、冲锋夹人、三根尾巴一起往前贯穿压制，这些靠挪动定稿的部件摆不出来，所以请你按骨架画 **18 个姿势**（12 个动作 + 4 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个斯卡纳**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1188**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：**绿线 = 身体**（从尾巴根到脸）；**三根青色系的线 = 三根尾巴**（青色 = 最后面那根、浅青 = 中间那根、钢蓝 = 最前面那根），每根末端的**三角块 = 毒刺**（尖朝三角的尖）；**橙线 = 近侧的钳子**（定稿里脸左下方那只），**紫线 = 远侧的钳子**（定稿里脸右边那只），线末端的大圆点 = 钳子尖；**红线 = 近侧的三条腿**，**蓝线 = 远侧的三条腿**（每条：腿根 → 膝 → 脚尖）；**灰框 = 头的位置**（银白头甲 + 骷髅脸）；**灰绿椭圆 = 巨石**（只在举石的几个姿势里）。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **长短要数格子**：骨架就是按定稿量的，每一节都和定稿一样长——**三根尾巴从根到毒刺底分别约 42 / 37 / 36 格**（毒刺另加约 9 格），**近侧钳子约 20 格、远侧约 23 格**，**腿很短：从腿根到脚尖约 16 格**；头（头甲连脸）24 × 26 格。**尾巴、钳子、腿沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长或压短**（之前一个英雄的腿画成了正常的长腿，只能重画——请画完数一数），**不要把直的一截整块转个方向贴上去**；尾巴一节一节的甲片照定稿的大小，转弯处甲片跟着弯。
> - **头一格一格照 `1_head.png` 画在灰框里**（同样朝右前方、银白头甲、骷髅脸、两只亮青眼睛一样高）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。尾巴、钳子**不要盖住脸**；尾巴从头上方经过时画在头**后面**。
> - **巨石**照 `2b_rock.png` 的巨石画（灰绿色多面体、几道裂缝），画在灰绿椭圆的位置、一样大；毒刺扎在巨石上抓住它。没有椭圆的姿势不画巨石。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。英雄联盟的斯卡纳尾巴和腿都长；我们的是 Q 版：腿短、脸大，**照骨架的长短和位置画，不照原版的长短**。

## 18 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `skarner-pose-a_wind.png` | 普攻起手：前半身抬起、身子往后坐，三根尾巴往后上方高高扬起蓄力，两只钳子张开 |
| 4 | `skarner-pose-a_strike.png` | 普攻扎下：身子往前压低，三根尾巴从头顶往前下方扎下去（毒刺在身前右边），钳子往前夹 |
| 5 | `skarner-pose-q_dig.png` | 掘石：身子压到最低，三根尾巴从背上往前弯下去插进地里，抓住身前地上的大巨石（巨石在身前地上） |
| 6 | `skarner-pose-q_lift.png` | 举石：三根尾巴把巨石从地里拔起来、举到背上头顶，身子往上挺 |
| 7 | `skarner-pose-t_wind.png` | 扔石起手：三根尾巴把巨石往后上方高高举起，身子往后仰，准备扔 |
| 8 | `skarner-pose-t_throw.png` | 扔出巨石：三根尾巴猛地往前甩直（毒刺朝身前右边），巨石已经扔出去了（不画巨石），身子往前冲 |
| 9 | `skarner-pose-w_rear.png` | 震地起跳：整个身子往上蹦起来（六条腿离地），尾巴蜷在背上，钳子往上张开 |
| 10 | `skarner-pose-w_slam.png` | 砸地：身子重重砸回地面、压得很低，六条腿往外撑开，钳子砸在地上（震地壁垒的地震） |
| 11 | `skarner-pose-e_charge.png` | 冲锋：身子压低往前冲，头和钳子在最前面，尾巴往后上方拖着（以绪塔尔冲击） |
| 12 | `skarner-pose-e_grab.png` | 夹住拖走：两只钳子在身前夹紧（夹着一个敌人，不画敌人），身子低着往前推，尾巴竖起来 |
| 13 | `skarner-pose-r_lash.png` | 毒刺贯体：三根尾巴从背上往前上方一起甩出去、伸得很长（毒刺在身前右边最远处），身子往前探 |
| 14 | `skarner-pose-r_hold.png` | 压制拖行：三根尾巴从高处往前弯下来（扎住敌人，不画敌人），身子低着站稳 |
| 15 | `skarner-pose-run1.png` | 跑 1：六条腿交替迈步（照骨架），身子平着往前，尾巴竖在背上 |
| 16 | `skarner-pose-run2.png` | 跑 2：一组腿抬起往前（照骨架），身子高一格 |
| 17 | `skarner-pose-run3.png` | 跑 3：照骨架换另一组腿往前迈 |
| 18 | `skarner-pose-run4.png` | 跑 4：另一组腿抬起往前（照骨架），身子高一格 |
| 19 | `skarner-pose-d_rear.png` | 被打倒：身子往上一挺、尾巴往上僵直，腿发软（死亡第一下） |
| 20 | `skarner-pose-d_down.png` | 倒地：整个身子趴平在地上，六条腿瘫开，三根尾巴软软地平摊在身后地上（死亡：倒地） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`；举石的姿势（q_dig、q_lift、t_wind）再加 `2b_rock.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (soles on y 1188) - a chibi CRYSTAL SCORPION: a broad thick armoured body of teal-green / dark slate-blue carapace plates with orange-red tribal markings edged in white; at the very front, under the edge of the carapace, a small BONE-WHITE SKULL-LIKE FACE with two small bright cyan eyes under a SILVER-WHITE HEAD PLATE; two BIG teal PINCERS in front (bone-white inner jaws, orange and white markings); THREE LONG SEGMENTED TAILS rising from his back, each ending in a big TEAL CRYSTAL STINGER with an orange-red core; SIX short jointed legs underneath with dark purple-black hooked claws; B its HEAD shown 8x (the silver head plate and the face); C a SKELETON on the same 1254 canvas and 9 px grid: GREEN = the body (the tails' root to the face), the THREE CYAN-ISH LINES = the three tails (cyan = the back one, light cyan = the middle one, steel blue = the front one), the TRIANGLE at the end of each = its stinger (pointing where the triangle points), ORANGE = the NEAR claw (below left of the face in A), PURPLE = the FAR claw (right of the face in A), the bigger dot at the end = the claw's tip, RED = the three NEAR legs, BLUE = the three FAR legs (each: the leg's root -> knee -> claw tip), GREY BOX = where the head goes, the GREY-GREEN ELLIPSE (only in some poses) = the BOULDER, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look or its long limbs); E (if attached) the same skeleton drawn over image A, showing which line is which part; F (if attached) the same character holding the boulder - the look of the boulder.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1188.
COUNT THE SQUARES: chibi proportions exactly as in image A - the tails about 42, 37 and 36 squares from the root to the stinger's base (each stinger about 9 more), the near claw about 20 squares and the far claw about 23, the legs SHORT, about 16 squares from the root to the claw tip. Lay the body along the green line with the same carapace plates and markings; each tail along its line, plate after plate of the same size as in image A, bending with the line, its crystal stinger on the triangle; each claw along its line (the same big pincer at its tip); each leg along its line, bending at the knee dot. Never stretch or shorten a tail, a claw or a leg, never paste a straight piece turned as one block. Where a tail passes the grey box it goes BEHIND the head. The near side in full tone, the far side a step darker. THE BOULDER (only where the ellipse is): the grey-green faceted boulder of image F on the ellipse, the same size, the stingers gripping it.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the silver head plate, the skull face to the front-right, both cyan eyes at the same height) - the same head in every pose, only moved, never turned, never redrawn as a profile. No tail or claw covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing (the crystals' highlights are bright squares, not a halo).
No effects (no shockwave, no dust, no rock debris, no charge trail, no motion lines, no enemies), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - rearing back, the front of his body lifted, the THREE TAILS raised high up and back, ready to strike, both claws spread open.`
- a_strike: `STRIKE - lunging forward and low, the THREE TAILS whipping over his head and stabbing down in front of him (the stingers on the image right), the claws snapping forward.`
- q_dig: `DIG - pressing his body down low, the THREE TAILS bending over his back and plunging down in front of him, their stingers gripping the BOULDER lying on the ground before him.`
- q_lift: `LIFT - the THREE TAILS tearing the BOULDER up out of the ground and swinging it up over his back, his body rising.`
- t_wind: `TOSS WIND-UP - the THREE TAILS lifting the BOULDER high up and back over him, his body leaning back, about to throw.`
- t_throw: `THROW - the THREE TAILS snapping forward straight out in front of him (the stingers to the image right), the boulder already thrown (no boulder), his body thrusting forward.`
- w_rear: `QUAKE LEAP - his whole body bouncing up off the ground (all six legs off the ground), the tails curled over his back, the claws raised wide open.`
- w_slam: `SLAM - crashing back down on the ground, pressed very low, all six legs braced out wide, the claws slamming down on the ground (the earthquake).`
- e_charge: `CHARGE - his body low, rushing forward head first, the claws pushed out in front, the tails streaming up and back behind him.`
- e_grab: `GRAB - both claws clamped together in front of him (holding an enemy - do NOT draw the enemy), his body low pushing forward, the tails raised up.`
- r_lash: `IMPALE - the THREE TAILS lashing forward together over his back, stretched far out in front (the stingers far out on the image right), his body leaning forward.`
- r_hold: `HOLD - the THREE TAILS arched high and bending down in front of him (impaling the enemies - do NOT draw them), his body low and braced.`
- run1: `RUN 1 - scuttling forward, the six legs stepping as the skeleton shows, the body level, the tails up over his back.`
- run2: `RUN 2 - one set of legs lifted swinging forward, as the skeleton shows, the body a square higher.`
- run3: `RUN 3 - the other legs reaching forward, as the skeleton shows.`
- run4: `RUN 4 - the other set of legs lifted swinging forward, as the skeleton shows, the body a square higher.`
- d_rear: `STRUCK DOWN - his body jerking up, the tails stiff straight up, the legs buckling.`
- d_down: `DEAD - lying flat on the ground, the six legs sprawled out, the three tails limp along the ground behind him.`

## 交回前请检查

- 真透明背景（不是画出来的棋盘格，也不是黑底）；1254×1254；**每格 9 px、对齐网格**；脚底在 y = 1188（蹦起来的 w_rear 离地，照骨架）。
- **数格子**：三根尾巴、两只钳子、六条腿和定稿一样长（尾巴约 42 / 37 / 36 格 + 毒刺，钳子约 20 / 23 格，腿约 16 格），没有被拉长或压短；关节处弯折，不是整块转过去。
- 头和 `1_head.png` 一格一格一样，没转、没变侧脸；尾巴、钳子没盖住脸。
- 颜色、描边、甲片花纹和定稿一样；举石的三张巨石和 `2b_rock.png` 一样；没有特效、没有敌人、没有地面和影子。
- 文件名：`outputs/skarner-poses/skarner-pose-<名字>.png`（名字见上表），原始生成图原样放进 `outputs/skarner-poses/raw/`；附一个 `generation-prompts.txt`；**最后**写 `outputs/skarner-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/skarner_poses_done.zip`。中间不要停，全部画完再交。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/skarner/codex_poses/`，先在 8 倍下量 Codex 实际的格子（读 raw 原稿），按它自己的格子读回，再把每张和骨架、定稿逐一比：尾巴 / 钳子 / 腿的长短、头的位置、脸、巨石。
- 骨架：`tools/art/pack_skarner_poses.py`（POSES 手调，长短来自 hd/idle.png；`--check DIR` 把骨架和英雄联盟那一帧并排）。
