# 法外狂徒 格雷福斯：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 格雷福斯的侧面造型用户已经定稿（`2_side_design.png`，你上一轮画的 side-2，换上了待机的头）。他的普攻、技能、死亡在英雄联盟里有这些造型本身给不出的姿势：**开枪后枪口往上翘**、**低身前冲**、**把枪端到肩高**、**被后坐力震得往后跳**，死的时候**枪脱手、跪倒、趴在地上**——所以请你按骨架画 **7 个姿势，每个一张图**。走路和站着开枪的动作我从定稿本身来做，不用画。
> - **每张图都是同一个格雷福斯**：样子、颜色、粗细、长短全照 `2_side_design.png`，**格子和它一样大：每格 16 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1168**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到脖子），**红线 = 前腿（画面右边那条）**，**蓝线 = 后腿**，**橙线 = 握枪托后握把的手臂**，**紫线 = 握前握把的手臂**，**粗金线 = 霰弹枪**（三个点：枪托末端、弹仓、枪口），品红线 = 围巾往后飘的尾巴，**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来、手握在枪上，不能悬空。
> - **霰弹枪必须笔直**：沿着金线画，枪托、圆弹仓、两根黑枪管、金箍、前握把的样子和大小照定稿；枪斜的时候也是一把直的枪整体斜过去，**枪管不弯、不断、不变短**。死亡的三个姿势**不画枪**（枪已经掉在地上，我这边单独放）。
> - **头一格一格照 `1_idle_head.png` 画在灰框里**（21 × 18 格，同样朝右前方、两只眼睛都看得见、黑络腮胡）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，侧面），**动作照它**，长相照定稿。

## 7 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `graves-pose-tilt.png` | **枪口往上翘**：开枪后的后坐力和拉枪栓，枪管往上斜约 30°，**腿和定稿一模一样** |
| 4 | `graves-pose-lunge.png` | **低身前冲**：前腿弓步、后腿往后蹬直，身子前倾压低，枪平端在腰间朝前 |
| 5 | `graves-pose-shoulder.png` | **端到肩高**：两腿前后叉开站稳，身子微微后仰，两只手把枪举到胸口 / 肩膀的高度，枪管水平朝前 |
| 6 | `graves-pose-hop.png` | **往后跳**：被后坐力震得两脚离地、膝盖弯起，身子后仰，枪口朝上斜约 55°，围巾往上飘 |
| 7 | `graves-pose-stagger.png` | **中枪后仰**：枪已经脱手（不画枪），身子往后仰，两只手甩开，一只脚往前踏 |
| 8 | `graves-pose-kneel.png` | **跪倒**：两个膝盖着地、小腿平贴地面往后，上身直着、头微微低下，两只手垂在身前（不画枪） |
| 9 | `graves-pose-lie.png` | **趴倒**：整个人脸朝下趴在地上（头在右边、下巴贴地），两腿伸直往左，一只手往前伸（不画枪） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_side_design.png`（定稿）、`1_idle_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, side-on facing right, on a 1254x1254 canvas with 16 px squares (soles on y 1168) - a burly gunslinger: slicked-back black hair, a full black beard, a ragged crimson scarf trailing behind, a big gold-trimmed brown leather pauldron, a brown vest, a navy shirt, khaki-and-dark-grey baggy trousers, brown boots, and a HUGE STRAIGHT DOUBLE-BARRELLED SHOTGUN of black steel and polished gold (a two-pronged gold stock, a round gold drum, two parallel black barrels with gold rings, a gold fore-grip) held level at the hip; B its HEAD shown 8x (21 squares wide, 18 tall); C a SKELETON on the same 1254 canvas and 16 px grid: green = the spine (pelvis to neck), RED = the FRONT leg (image right), BLUE = the BACK leg, ORANGE = the arm holding the gun's back grip, PURPLE = the arm holding the fore-grip, the thick GOLD line = the shotgun (stock end, drum, muzzle - one straight gun), magenta = the scarf's trailing end, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, side-on (copy the POSE from it, never its 3D look); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1168.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots; the thigh, shin and boot the SAME thickness, length and colours as in image A), each arm from its shoulder along its line to a hand closed on the gun (the arms grow from the shoulders, never floating). Never stretch or shorten a limb, never paste a straight leg turned as one block.
THE SHOTGUN along the gold line: the SAME gun as in image A, the same size and parts, perfectly STRAIGHT - when it tilts the whole straight gun tilts, the barrels never bend, break or get shorter.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both eyes, the black beard, the slicked-back hair) - the same head in every pose, only moved, never turned, never redrawn as a profile.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no muzzle flash, no smoke), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- tilt: `TILT - right after a shot: the shotgun tipped up about 30 degrees by the recoil (the muzzle up to the image right, the stock down behind his hip), both hands still on it; the legs EXACTLY as in image A.`
- lunge: `LUNGE - a low forward lunge: the front leg bent forward, the back leg pushed straight back, the body leaning forward and low, the shotgun held level at the hip pointing right.`
- shoulder: `SHOULDER - braced with the legs apart front and back, the body leaning back a little, both hands lifting the shotgun to chest / shoulder height, the barrels level pointing right.`
- hop: `HOP - thrown back off the ground by the recoil: both feet in the air with the knees bent, the body leaning back, the shotgun pointing up about 55 degrees, the scarf flying up.`
- stagger: `STAGGER - shot: NO gun (he has dropped it), the body bending back, both arms flung out, one foot stepping forward.`
- kneel: `KNEEL - down on both knees with the shins flat on the ground behind, the body upright, the head bowed a little, both hands hanging in front of him; NO gun.`
- lie: `LIE - lying face down on the ground, the head at the image right with the chin on the ground, the legs stretched out straight to the left, one arm reaching forward; NO gun.`

## 交回前请检查

- **7 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 16 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个格雷福斯：**同一个头（照图 B）**、同样粗的腿和手臂；手臂从肩膀长出来、手握在枪上；**枪是直的、和定稿一样长**；姿势沿着骨架；着地的脚在 y 1168。
- 死亡的三张没有枪；所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/graves-poses/`）

- `graves-pose-tilt.png`、`-lunge.png`、`-shoulder.png`、`-hop.png`、`-stagger.png`、`-kneel.png`、`-lie.png`；原始生成图原样放 `outputs/graves-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/graves_poses_done.zip`。中间不要停，7 张都画完再交。

## 附图（压缩包 `graves_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_idle_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_side_design.png` | 定稿的侧面（每格 16 px，脚底 y 1168） |
| `3_tilt_*` … `9_lie_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂、枪的长短粗细，和定稿比**（codex-legs-need-skeletons），枪不直、变短就换回定稿的枪整块（只整块平移，不转半格），头换成待机的头；再接进 rig_graves.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排：普攻 = 定稿开枪（枪口火光烤进帧）→ tilt（拉枪栓）→ 定稿；第二发后的装弹 attack2 = tilt 停久一点；Q = lunge 开火 → tilt；E = lunge 冲刺；R = shoulder 开火 → hop 往后跳；走路 = 布隆 / 诺提勒斯的走法（定稿的腿整块抬起、小步，`rig_braum.walk_frame`）；受击 = 定稿白闪后退；死亡 = stagger（枪掉在地上：定稿的枪整块放倒在地面）→ kneel → lie。
