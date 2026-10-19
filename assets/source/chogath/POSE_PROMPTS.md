# 虚空恐惧 科加斯：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 科加斯的侧面造型用户已经定稿（`2_side_design.png`，你上一轮画的侧面-1，换上了待机的头）。他的普攻、技能、死亡在英雄联盟里都要**用后腿直立起来、再往前扑砸下去**，还要**侧躺倒地**——这些姿势造型本身给不出，所以请你按骨架画 **7 个姿势，每个一张图**。
> - **每张图都是同一只科加斯**：样子、颜色、粗细、长短全照 `2_side_design.png`，**格子和它一样大：每格 16 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1120**），网格从画布左上角对齐。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱和尾巴，深绿细线 = 背（甲壳顶，镰刀臂从它前端长出来），**红线 = 近侧的两条腿（在前面、颜色亮）**，**蓝线 = 远侧的两条腿（在后面、稍暗）**，**橙线 = 近侧镰刀臂**，**紫线 = 远侧镰刀臂（在后面、稍暗）**，**灰框 = 头的位置**。`0_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**四肢、尾巴、镰刀臂的长短和定稿一样**（骨架就是按定稿量的），关节处弯折，不要把直的腿整块转个方向贴上去，不要拉长或压短。
> - **头一格一格照 `1_idle_head.png` 画在灰框里**（24 × 21 格，同样朝右前方、两只青色眼睛都看得见、张开的大嘴、白牙、紫舌头、红獠牙）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`，侧面），**动作照它**，长相照定稿。

## 7 个姿势

| 图 | 文件 | 姿势 |
|---|---|---|
| 3 | `chogath-pose-crouch.png` | **蓄力**：四肢着地、身子压低，头往回缩，两条镰刀臂往后拉（要起身扑击之前） |
| 4 | `chogath-pose-rise.png` | **半起身**：后腿撑地、上身斜着抬起来约 45°，前爪离地，镰刀臂举高 |
| 5 | `chogath-pose-rear.png` | **直立**：只用两条后腿站着，身子竖直，前爪抬在胸前，两条镰刀臂高高举起、往两边张开，尾巴拖在身后的地上 |
| 6 | `chogath-pose-slam.png` | **下砸**：整个身子往前（画面右边）扑下去，头和前爪砸到地面，后腿往后蹬直，尾巴高高翘起，镰刀臂往前下方劈 |
| 7 | `chogath-pose-lunge.png` | **扑咬**：身子往前伸长，头往前探到半空、大嘴张到最大，两只前爪往前抓，后腿蹬地 |
| 8 | `chogath-pose-fall.png` | **瘫倒**：四条腿都软下去，肚子贴近地面，头垂到地上，镰刀臂往后耷拉 |
| 9 | `chogath-pose-lie.png` | **侧躺**：整个身子侧着躺在地上（肚子朝外），四条腿软软地伸出来，尾巴平放，镰刀臂瘫在背后的地上 |

## 提示词（每个姿势一次，换掉最后一段的姿势名和图号）

每次上传：`2_side_design.png`（定稿）、`1_idle_head.png`（头）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, side-on facing right, on a 1254x1254 canvas with 16 px squares (soles on y 1120) - a huge void beast on all fours: dark violet-purple carapace with wine-red plate edges, a big head with a wide open maw, white fangs, a purple tongue and two glowing cyan eyes, red tusks, two long scythe arms with red blade-claws growing from the top of the back, purple back spines, four thick legs with red hooked talons, a long segmented tail with a red spiked tip; B its HEAD shown 8x (24 squares wide, 21 tall); C a SKELETON on the same 1254 canvas and 16 px grid: green = spine and tail, thin dark green = the back (the top of the carapace; the scythe arms grow from its front end), RED = the two NEAR legs (in front, full tone), BLUE = the two FAR legs (behind, a step darker), ORANGE = the NEAR scythe arm, PURPLE = the FAR scythe arm (behind, darker), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose, side-on (copy the POSE from it, never its 3D look); E (if attached) the same skeleton drawn over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C (and image D): a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 16 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1120.
Lay the body along the skeleton: the spine and the back where the green lines are, each leg along its line (bending at the dots, the thigh, shin and foot the SAME thickness, length and colours as in image A, the red talons on the feet), the scythe arms along the orange and purple lines (as thick and long as in image A, the red blade-claw at the end), the tail along its green line with the red spiked tip. Never stretch or shorten a limb, never paste a straight leg turned as one block.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the face to the front-right, both cyan eyes, the open maw, the fangs, the tongue, the tusks) - the same head in every pose, only moved, never turned, never redrawn as a profile.
The same colours as image A: the carapace in its 3 violet-purples, the plate edges in its 3 wine-reds, the dark legs with lighter edges; one continuous 1-square near-black outline; the near parts in full tone, the far parts a step darker; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <crouch / rise / rear / slam / lunge / fall / lie - one line from the table, in English>
```

每个姿势的最后一行（英文）：

- crouch: `CROUCH - on all fours with the body pressed low, the head pulled back, both scythe arms drawn back over the back, ready to spring.`
- rise: `RISE - pushing up on the hind legs, the upper body lifted about 45 degrees, the front claws off the ground, the scythe arms raised high.`
- rear: `REAR - standing upright on the two hind legs only, the body vertical, the front claws held up in front of the chest, both scythe arms raised high and spread apart, the tail lying on the ground behind.`
- slam: `SLAM - the whole body thrown forward and down to the image right, the head and the front claws striking the ground, the hind legs kicked straight back, the tail raised high, the scythe arms slashing forward and down.`
- lunge: `LUNGE - the body stretched forward, the head thrust forward at mid height with the maw opened as wide as it goes, both front claws reaching forward, the hind legs pushing off.`
- fall: `FALL - collapsing: all four legs buckling, the belly sinking near the ground, the head drooping to the ground, the scythe arms sagging backward.`
- lie: `LIE - lying on his side on the ground (the belly toward the viewer), the four legs limp and stretched out, the tail flat, the scythe arms slumped on the ground behind the back.`

## 交回前请检查

- **7 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**每格 16 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- 每张都是定稿的同一只科加斯：**同一个头（照图 B）**、同样粗的腿、同样长的镰刀臂和尾巴；姿势沿着骨架；着地的脚在 y 1120。
- 没有特效、没有骨架线、没有网格线。

## 交付（`outputs/chogath-poses/`）

- `chogath-pose-crouch.png`、`-rise.png`、`-rear.png`、`-slam.png`、`-lunge.png`、`-fall.png`、`-lie.png`；原始生成图原样放 `outputs/chogath-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/chogath_poses_done.zip`。中间不要停，7 张都画完再交。

## 附图（压缩包 `chogath_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_idle_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_side_design.png` | 定稿的侧面（每格 16 px，脚底 y 1120） |
| `3_crouch_*` … `9_lie_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（应约 16 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量每条腿、镰刀臂、尾巴的长短粗细，和定稿比**（codex-legs-need-skeletons），头换成待机的头；再接进 rig_chogath.py 的动作里，逐帧自查后才发合成 GIF。
