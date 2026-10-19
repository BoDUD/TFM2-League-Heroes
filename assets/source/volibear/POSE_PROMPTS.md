# 不灭狂雷 沃利贝尔：手臂姿势 + 走路（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。** 一共两件事，都画完再交付：
> - **A：同一个沃利贝尔，只重画两只手臂的姿势**（4 个姿势，每个两稿）。用户已经定下了他的造型（`A/1_design.png`，就是你上一轮画的 volibear-model-B-2，按它自己的格子读回）。造型里两只巨大的手臂都垂在身体两边；英雄联盟里他攻击、放技能时会**把手臂举过头顶、往前下方抓、两只爪子一起往前扑**。我用造型自己的格子拼过（整块转 90°、整块挪动、上下镜像），都很怪（`A/5_not_like_this.png`：手臂变成横着的一根“毛棍”、像耸肩、举起来的手臂底部是一刀切的平口）。造型里没有这些手臂姿势，所以请你画。
> - **B：走路换皮**：照图 `B/1` 的动作骨架（另一个大块头角色的走路，9 帧），换成沃利贝尔的样子。

---

## A：只重画手臂（`volibear-pose-*.png`，4 个姿势 × 2 稿 = 8 张）

**除了两只手臂（从肩膀往下：上臂、前臂、手掌、冰蓝爪子），其余每一格都和 `A/1_design.png` 一模一样**：头、脸、耳朵、毛辫和铁环、胸口、肚子上的闪电纹、两条腿、脚掌，位置和颜色都不变；画布、网格、人的位置都不变（叠在一起检查）。

### 格子和位置（照 `A/1_design.png` / `A/2_grid.png`）

- 画布 **1254 × 1254**，**每格 15 px**，和 `A/1_design.png` 同一个网格（`A/2_grid.png` 的浅灰线每 5 格一条，网格从 x = 210、y = 330 对齐）。
- 人还是 **51 × 54 格**，**耳朵顶 y = 330**（绿线），**两只脚底 y = 1140**（红线），左右位置不变。头顶上方留了约 22 格、右边留了约 18 格的空白，**举起来的手臂、往前伸的手臂画在这些空白里**，不出画。

### 手臂的画法（所有姿势都一样）

- 手臂**和造型里的手臂一样粗、一样长、一样的颜色**（`A/3_arms_closeup.png` 是造型里的两只手臂，10 倍）：上臂是白毛带冰蓝、有蓝色符文纹身；往下变成深灰紫的前臂和手掌；**每只手 3–4 根冰蓝水晶爪**。弯曲的手臂要画出手肘的弯折，**不能把垂着的手臂整块转个方向贴上去**（那样就成了横着的“毛棍”），要按新的方向重新画毛的走向和明暗（光从左上方来）。
- **近侧手臂（画面左边）比远侧手臂（画面右边）大一点、亮一点**（3/4 视角近大远小），但**两只手臂的长度和粗细要相称**，不要一只粗一只细得很明显。
- 手臂从**肩膀**长出来，和肩膀的毛连成一体（不能有一刀切的平口、不能像断开）；**手臂绝不能挡住脸**（眼睛、熊嘴、鼻子）；举起的手臂在头的两侧或稍后。
- 手臂原来垂着的地方（身体两边）变空后：**身体的两侧要画完整**（毛辫外侧的肩膀、胸侧、腰侧的白毛和深灰紫毛，一圈近黑描边），不能像被切掉一样。

### 4 个姿势

1. **`volibear-pose-up2-1.png` / `-2.png`：双手高举**（R 跳起、Q 扑起时）。两只手臂都**举过头顶**，手肘微弯，爪子朝上张开，像要往下砸；近侧手在头的左上方，远侧手在头的右上方，两只手的高度差不多；爪尖大约到耳朵顶上方 16–18 格。
2. **`volibear-pose-up1-1.png` / `-2.png`：近侧手单手高举**（E 召雷、普攻蓄力；照 `A/4a_lol_one_arm_up.png`）。**近侧手臂（画面左边）笔直举过头顶，爪子朝天张开**；远侧手臂和造型里一样垂着，一格不动。
3. **`volibear-pose-rake-1.png` / `-2.png`：近侧手往前下方抓**（普攻出手；照 `A/4b_lol_rake.png`）。**近侧手臂从肩膀往前（画面右边）、往下挥出**，在**胸口到肚子的高度**横过身体前面，**爪子伸到身体右边外面**、朝前下方张开；远侧手臂和造型里一样垂着。手臂在熊下巴下面，不挡脸。
4. **`volibear-pose-maul-1.png` / `-2.png`：双爪往前扑抓**（W 撕咬、Q 砸下、R 落地；照 `A/4c_lol_maul.png`）。**两只手臂都往前（画面右边）伸出**，在**胸口到腰的高度**，近侧手在前、远侧手在后稍高，两只手的**爪子都张开朝前**，伸到身体右边外面；手肘微弯，手臂在下巴下面，不挡脸。

### 干净

- 一圈连续的近黑外描边；每种材质用自己最暗的一档当阴影；没有零散杂色格；不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效（闪电、雷云、爪痕都不画）。

---

## B：走路换皮（`volibear-run.png`，1 张整图）

上传顺序：图1 = `B/1_动作骨架_oppi走路.png`，图2 = `B/2_角色_沃利贝尔定稿.png`，图3 = `B/3_英雄联盟沃利贝尔跑步.png`（只看动作）。

参考图1精灵图的动作序列和构图布局，将原有的角色替换为图2角色（沃利贝尔，用后腿站立的白色雷霆巨熊）。

1. 保留图1所有帧的位置、大小、排列顺序：5×2 排列共 9 帧（第二行最后一格空着），从左到右、从上到下；每帧角色在格子里的位置和脚底高度都不变。
2. 保留每帧的动作：弓着背往前走，**两条腿一前一后交叉迈步**，往后收的腿弯膝、脚跟抬起，两腿每半圈换一次前后；**两只手臂跟着步子前后摆**（和腿反着摆）；身体上下起伏、稍微前倾（图3 是英雄联盟原版的跑步，可以对照）。
3. 身体结构、配色、特征完全换成图2：白色带冰蓝的长毛（头、肩、胸、手臂），往下变成深灰紫色（肚子下半、腿、手掌、脚掌）；小熊头、黑鼻头、龇着的白牙、发青光的眼睛、额头蓝色闪电符文；两条白毛辫和深色铁环（青色符文）、白毛穗；上臂蓝色符文纹身、胸腹蓝色闪电纹；冰蓝水晶爪子。**图1 的蓝色头发、角、鼻环、腰布都不要画**。
4. **头和图2 一模一样**（同样的格子、同样朝右前方、两只眼睛都看得见），每一帧都是同一个头，只跟着身体上下动。
5. 体型和图2一样大（耳朵顶到脚底约 54 格），头和身体比例和图2一样，不要变大变小、变胖变瘦；两只手臂一样粗、和图2 一样大；两条腿的颜色一样（深灰紫），远处那条腿可以暗一档。
6. 像素画：方块大小和图2一样（每个像素方块一样大，整齐对格），1–2 像素深色描边，不要抗锯齿、不要渐变、不要模糊。

背景保持纯绿色 #00FF00（和角色差异最大的纯色），方便抠图。风格保持与原图一致。重点在于精准复刻原图的"动作骨架"，只是换了"皮囊"。

---

## 附图（压缩包 `volibear_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `A/1_design.png` | 定稿造型，每格 15 px 放在 1254 画布上 | **A：除两只手臂外，全部照抄** |
| `A/2_grid.png` | 同一张加网格线：绿线 = 耳朵顶，红线 = 地面 | A：对齐网格、大小、位置 |
| `A/3_arms_closeup.png` | 造型里的两只手臂（10 倍：左 = 近侧，右 = 远侧） | A：手臂、毛、符文、爪子的颜色和画法 |
| `A/4a_lol_one_arm_up.png` | 英雄联盟原版：E 时单手举向天空 | A 姿势 1、2：举起的手臂 |
| `A/4b_lol_rake.png` | 英雄联盟原版：普攻往前下方抓 | A 姿势 3 |
| `A/4c_lol_maul.png` | 英雄联盟原版：W 双爪往前扑 | A 姿势 4 |
| `A/5_not_like_this.png` | 被否掉的拼法（6 倍） | **不要这样**：整块转成横着的毛棍、耸肩、举起的手臂底部一刀切 |
| `B/1_动作骨架_oppi走路.png` | 动作骨架：另一个大块头角色的走路（9 帧） | B：每帧的姿势、步子、位置 |
| `B/2_角色_沃利贝尔定稿.png` | 沃利贝尔定稿，同样大小的格子 | B：皮囊（长相、颜色、大小） |
| `B/3_英雄联盟沃利贝尔跑步.png` | 英雄联盟原版跑步 | B：只看动作 |

## A 的英文提示词（每个姿势换最后一段，每个画两稿）

附 `A/` 里全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art design of this character on a 1254x1254 canvas, every square 15 px - a huge white bear standing on his hind legs: white fur with an ice-blue tint on the head, shoulders, chest and arms turning to dark slate-violet on the lower belly, the legs, the hands and the feet; a small bear head (black nose, bared white teeth, glowing cyan eyes, a blue lightning rune on the forehead); two braided white tresses in dark iron bands down his chest; blue rune tattoos on the upper arms; glowing ice-blue crystal claws; BOTH huge arms HANGING DOWN beside the body; 2 the same with a grid every 5 squares, the green line = the top of his ears, the red line = the ground; 3 the design's two arms enlarged 10x (left the near arm, right the far arm): their colours and how they are drawn; 4a-4c 3D renders of the original character in the poses below; 5 REJECTED attempts made by moving the design's own arm squares: an arm turned sideways into a horizontal log of fur, the arms shrugged up, raised arms with a flat cut at the shoulder - do NOT do this.
Draw with the image generator ONE pixel-art picture of the SAME character on the SAME 1254x1254 canvas with the SAME 15 px squares on the same grid, real transparent background (alpha only 0 or 255). EVERYTHING except the two arms is copied square by square from image 1, unchanged: the head, the face, the ears, the tresses and their bands, the chest, the belly with its lightning stripes, both legs and feet, the same place on the canvas (the top of the ears y 330, the soles y 1140).
THE ARMS are drawn AGAIN in the new pose: as thick, as long and in the same colours as in image 3 (white ice-blue fur with the blue rune tattoo on the upper arm, turning dark slate-violet on the forearm and the hand, 3-4 ice-blue crystal claws each), with a bent elbow where the pose bends, the fur and the light (from the upper left) drawn for the new direction - NEVER the hanging arm pasted turned. The near arm (image left) a little bigger and lighter than the far arm (image right), both in proportion - not one thick and one thin. Each arm grows out of its shoulder's fur in one piece (no flat cut, never looking broken off); the arms NEVER cover the face (eyes, muzzle, nose). Where an arm hung before, the side of the body is drawn whole (the shoulder outside the tress, the side of the chest and waist in their white and slate-violet fur, a near-black outline), never cut off.
One continuous near-black outline round the figure; every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects (no lightning, no claw trails), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

最后一段（每个姿势换这一段）：

- 姿势 1 `volibear-pose-up2`：`THE POSE: BOTH ARMS RAISED HIGH OVER HIS HEAD, the elbows slightly bent, the claws spread open pointing up as if to smash down; the near arm above the left side of the head, the far arm above the right side, the two hands at about the same height, the claw tips about 16-18 squares above the top of the ears.`
- 姿势 2 `volibear-pose-up1`：`THE POSE (image 4a): the NEAR arm (image left) raised STRAIGHT UP over his head, the claws spread open to the sky; the FAR arm (image right) hangs exactly as in image 1, unchanged.`
- 姿势 3 `volibear-pose-rake`：`THE POSE (image 4b): the NEAR arm (image left) swung FORWARD AND DOWN from the shoulder across the front of his body at chest-to-belly height, below the chin, the claws spread open reaching out past his right side, pointing forward and down; the FAR arm (image right) hangs exactly as in image 1, unchanged.`
- 姿势 4 `volibear-pose-maul`：`THE POSE (image 4c): BOTH arms thrust FORWARD (to the image right) at chest-to-waist height, below the chin, the near arm in front, the far arm behind it a little higher, the elbows slightly bent, both sets of claws spread open pointing forward, reaching out past his right side.`

## 交回前请检查

- **A 的 8 张、B 的 1 张都是 image_gen 画的**；A：1254 × 1254，真透明背景，**alpha 只有 0 / 255**，每格 15 px，和 `A/1_design.png` 同一网格；B：和图1 一样大小、5×2 排列、纯绿 #00FF00 背景。
- A：除两只手臂外，其余每一格都和 `A/1_design.png` 一样（叠在一起检查）；耳朵顶 y 330、脚底 y 1140；手臂和造型一样粗一样长、从肩膀连出来、不挡脸、没有一刀切的平口；身体两侧完整。
- B：每帧都是同一个头；两腿交叉迈步、手臂前后摆；体型和图2 一样大；没有图1 角色的头发、角、鼻环、腰布。
- 没有任何特效。

## 交付（`outputs/volibear-pose/`）

- `volibear-pose-up2-1.png`、`-up2-2.png`、`-up1-1.png`、`-up1-2.png`、`-rake-1.png`、`-rake-2.png`、`-maul-1.png`、`-maul-2.png`、`volibear-run.png`；**image_gen 的原始生成图原样放 `outputs/volibear-pose/raw/`**；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/volibear_pose_done.zip`。中间不要停，全部画完再交。

## Claude 收到后（给 Claude 看）

- A：照 `tools/art/design_akshan_poses.py`：在包的 15 px 网格上取每格中间的众数，套造型自己的调色板；用腿和头找 Codex 的偏移；只把手臂范围内变了的格子、和原来手臂的格子当印章 -> `hd/pose_<name>.png`。`rig_volibear.py` 里用印章替换原来的手臂，随上身一起动。逐帧检查：一块、没有新洞、手臂连着肩膀、脸没被挡、两手粗细相称。
- B：照 `tools/art/design_akshan_run.py`：抠绿、按格子读回、套造型调色板、头换成造型自己的头（一张脸），对齐脚底 -> run 的 8 帧（9 帧取 8 帧或全用）。
