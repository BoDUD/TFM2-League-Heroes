# 祖安怒兽 沃里克：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 沃里克的造型用户已经定稿（`2_design.png`，你上一轮画的 A-1：3/4 正面朝右、弓着背的狼人）。英雄联盟里他的普攻、技能、死亡有很多**全身动作**——蹲伏、后仰张嘴、空中飞扑、落地撕咬、直立嚎叫、扑下抓、举爪、中招后仰、侧躺倒地——这些靠挪动定稿本身的部件摆不出来，所以请你按骨架画 **9 个姿势，每个一张图**。待机、跑步我从定稿本身来做，不用画。
> - **每张图都是同一个沃里克**：样子、颜色、粗细、长短全照 `2_design.png`，**格子和它一样大：每格 12 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱（骨盆到背上隆起的地方），**红线 = 近侧的腿（画面左边那条，在前面、颜色全亮）**，**蓝线 = 远侧的腿（画面右边那条，暗一档）**，**橙线 = 近侧的手臂（画面左边，戴着嵌绿药剂的铜护臂）**，**紫线 = 远侧的手臂（画面右边）**，**粗金线 = 背上的炼金装置**（绿药瓶的底座到铜尖刺的尖），品红线 = 尾巴，**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**腿、手臂的长短粗细和定稿一样**（骨架就是按定稿量的），关节处弯折，**不要拉长或压短，不要把直的腿整块转个方向贴上去**。手臂从肩膀长出来，不能悬空；狼腿是反关节的（大腿、往后折的小腿、长脚掌、爪子），和定稿一样。
> - **头一格一格照 `1_head.png` 画在灰框里**（连耳朵和脸上的白鬃毛 38 × 35 格，同样朝右前方、两只黄眼睛都看得见、张着嘴露出白牙）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂和爪子**不要盖住脸**（眼睛、鼻子、嘴）。
> - **尾巴不碰地**（除了最后的侧躺）。每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，3/4 朝右），**动作照它**，长相照定稿。

## 9 个姿势

| 图 | 文件 | 姿势 | 用在 |
|---|---|---|---|
| 3 | `warwick-pose-crouch.png` | **蹲伏**：压得很低、身子前倾、头往前探，两条胳膊张开到身体两侧、爪子低低地张着，两腿深蹲 | 普攻、大招的蓄力 |
| 4 | `warwick-pose-rear.png` | **后仰张嘴**：身子直起来往后仰、胸口挺出，两只爪子抬到胸前，张开大嘴 | Q 起手、E |
| 5 | `warwick-pose-leap.png` | **空中飞扑**：整个人腾空（脚离地约 8 格），身子斜着往前上方，两条胳膊张开举起、爪子张开，两腿收在身下往后，尾巴往后飘 | Q、R 的飞扑 |
| 6 | `warwick-pose-bite.png` | **落地撕咬**：落地后压成很宽的深蹲，头低低地往前咬下去，两条胳膊往两边撑开、爪子朝下 | Q 落地 |
| 7 | `warwick-pose-howl.png` | **直立嚎叫**：整个人站直、站高，胸口挺出，两条胳膊垂在身体两侧、拳头握紧，头抬得很高 | E 的嚎叫 |
| 8 | `warwick-pose-strike.png` | **扑下抓**：身子往前压低扑下去，头在前面低处，两只爪子一起往前下方抓下去，后腿往后蹬 | 普攻出手、R 压住时抓下去 |
| 9 | `warwick-pose-raise.png` | **举爪**：身子立起来，远侧那只手臂高高举过头顶、爪子朝上，近侧手臂往外甩开，张嘴 | R 压住时抬爪、普攻蓄力 |
| 10 | `warwick-pose-stagger.png` | **中招后仰**：身子往后仰，两条胳膊往两边甩开，一只脚往前踏稳 | 死亡第一下 |
| 11 | `warwick-pose-lie.png` | **侧躺倒地**：整个人侧躺在地上，头在画面右边、下巴贴地，身子和两腿往左伸，两只手软软地搭在身前，尾巴平放在身后地上 | 死亡 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`2_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 12 px squares (soles on y 1176) - a hunched werewolf: blue-violet fur, a shaggy white mane on his chest and cheeks, huge pointed ears (pink inside), a snarling open jaw with white fangs and a red mouth, yellow eyes; a green glowing vial with a copper spike standing up on his upper back; copper gauntlets on both forearms (green vials in the near one), long dark claws; olive cargo shorts with a belt; digitigrade wolf legs with clawed feet; a long bushy dark blue tail; B its HEAD with the ears and the face's mane shown 8x (38 squares wide, 35 tall); C a SKELETON on the same 1254 canvas and 12 px grid: green = the spine (pelvis to the hump of the back), RED = the NEAR leg (image left, in front), BLUE = the FAR leg (image right), ORANGE = the NEAR arm (image left, the gauntlet with the green vials), PURPLE = the FAR arm (image right), the thick GOLD line = the back rig (the green vial's base to the copper spike's tip), magenta = the tail, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, 3/4 view facing right (copy the POSE from it, never its 3D look); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 12 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1176.
Lay the body along the skeleton: the torso along the green line, each leg along its line (bending at the dots: the thigh, the backward-bent shin, the long foot and the claws the SAME thickness, length and colours as in image A), each arm from its shoulder along its line to its claws (the arms grow from the shoulders, never floating), the back rig along the gold line, the tail along the magenta line. Never stretch or shorten a limb, never paste a straight leg turned as one block. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both yellow eyes, the open jaw with white fangs, the huge ears, the white mane) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm or claw covers the face.
The tail never lies on the ground (except in the lying pose). The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects (no claw trails, no blood, no shockwave), no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- crouch: `CROUCH - crouched very low and leaning forward, the head pushed out in front, both arms spread out to his sides with the claws open low, both legs deeply bent.`
- rear: `REAR - reared up and leaning back with the chest thrown out, both claws raised in front of the chest, the jaws wide open.`
- leap: `LEAP - in the air (the feet about 8 squares above the ground), the body stretched diagonally forward and up, both arms spread and raised with the claws open, both legs tucked under and back, the tail streaming behind.`
- bite: `BITE - landed in a very wide deep crouch, the head low and forward biting down, both arms braced out to the sides with the claws down.`
- howl: `HOWL - standing upright and tall, the chest thrown out, both arms hanging at his sides with the fists clenched, the head held high.`
- strike: `STRIKE - lunging forward and down, the head low in front, both claws raking forward and down together, the back leg pushed back.`
- raise: `RAISE - reared up, the FAR arm raised high over his head with the claws up, the near arm flung out to the side, the jaws open.`
- stagger: `STAGGER - struck: the body bending back, both arms flung out to the sides, one foot stepping forward to stay up.`
- lie: `LIE - lying on his side on the ground, the head at the image right with the chin on the ground, the body and both legs stretched out to the left, both arms limp in front of him, the tail lying flat behind him on the ground.`

## 交回前请检查

- **9 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 12 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一个沃里克：**同一个头（照图 B，脸朝右前方、两只黄眼睛、张嘴白牙）**、同样粗的腿和手臂、铜护臂和绿药剂、背上的药瓶和尖刺；手臂从肩膀长出来，没有盖住脸；姿势沿着骨架；着地的脚在 y 1176；尾巴不碰地（侧躺除外）。
- 所有图没有特效、没有骨架线、没有网格线。

## 交付（`outputs/warwick-poses/`）

- `warwick-pose-crouch.png`、`-rear.png`、`-leap.png`、`-bite.png`、`-howl.png`、`-strike.png`、`-raise.png`、`-stagger.png`、`-lie.png`；原始生成图原样放 `outputs/warwick-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/warwick_poses_done.zip`。中间不要停，9 张都画完再交。

## 附图（压缩包 `warwick_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_design.png` | 定稿（每格 12 px，脚底 y 1176） |
| `3_crouch_*` … `11_lie_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 12 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、手臂的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成定稿的头（每帧同一张脸，脸不重画），再接进 rig_warwick.py 的动作里，逐帧自查后才发合成 GIF。
- 动作安排（照英雄联盟）：普攻 = crouch → strike（出手）→ 定稿；Q = rear → leap（飞过去）→ bite（落地咬）→ 定稿；E = rear（护体）；嚎叫 = crouch → howl；R = crouch → leap（ult_dash）→ 压住时 raise / strike 交替三次；死亡 = stagger → lie；跑 = 布隆 / 加里奥的大块头走法（定稿的腿整块抬起、小步）；待机 = 定稿呼吸。
