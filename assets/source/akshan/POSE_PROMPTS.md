# 影哨 阿克尚：拿枪那条胳膊端枪朝前（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户已经定下了阿克尚的造型（`1_design.png`，就是你上一轮画的 akshan-model2-A-1，按它自己的格子读回、缩到 57 行）。
> - 造型里拿枪的那条胳膊（画面**左边**：金护腕、浅蓝手套）把回旋镖手枪**举在头边、枪口朝天**。英雄联盟里他**普攻、E 荡索开枪、R 连射时都是手臂伸直、把枪平端在胸前朝前开枪**（`5_lol_aim.png`）。
> - 我用造型自己的格子拼过（只能整块平移、直角转动）：枪横在胸前和橙红饰带糊成一团；把上臂藏起来让前臂伸过去，又像**手从胸口中间断开**一样（`6_not_like_this.png`，用户说「手都断了？」）。造型里根本没有朝前的胳膊，所以请你画。
> - **这一轮只画一个姿势、两稿：同一个阿克尚，除了拿枪那条胳膊和枪，其余每一格都和 `1_design.png` 一模一样**（头发、脸、胡子、围巾、护肩、饰带、叉腰的远侧手、披风、腰带、布片、裤子、靴子，位置和颜色都不变）。

## 姿势：端枪朝前（照 `5_lol_aim.png`）

- 拿枪那条胳膊从**画面左边的肩膀**（灰色护肩那里）出发，**整条伸直朝前（画面右边）**，横在**胸口高度**：在**胡子下面**，**绝不能挡住脸和胡子**；上臂、手肘、前臂、金护腕、浅蓝手套是**连着的一整条**，粗细和造型里的手臂一样（不变胖也不变细）。
- 浅蓝手套握着枪柄，**枪平端、枪口朝前（朝画面右边）**，前端的两道回旋镖弯钩**朝前张开**（一上一下）。枪**和造型里的枪一样大、一样的颜色**（暗红 + 青铜、橙色高光、青白握把），只是方向从朝上变成朝前；整把枪伸到身体前面，**超出身体右边**一截（画布右边留了空间）。
- 原来举在头边的枪和手臂的位置（头的左上方）**清空、透明**；手臂原来挡住的**左肩和披风左边要画完整**（灰护肩、暗红披风的侧边和浅蓝内衬），不能像被切掉一样。
- 叉腰的远侧手、腿、披风下摆、站姿全都不动。

## 格子和位置（照 `1_design.png` / `2_grid.png`）

- 画布 **1254 × 1254**，**每格 15 px**，和 `1_design.png` 同一个网格（`2_grid.png` 的浅灰线每 5 格一条，从 x = 90、y = 165 开始）。
- 人还是 **46 × 69 格**，**头顶头发 y = 345**（绿线），**两只鞋底 y = 1200**（红线），左右位置不变；**伸出去的枪画在人右边的空白里**（最远到 x ≈ 1150，不出画）。
- 只有拿枪那条胳膊和枪是新画的，**其余部分照抄 `1_design.png`，一格都不要动**（可以把两张叠在一起检查）。

## 要画清楚的地方

- 手臂：棕色皮肤（3 档、有亮边）、金护腕（金 2–3 档 + 高光）、浅蓝无指手套，和 `3_arm_closeup.png` 里一样的颜色和画法。
- 枪：暗红带青铜的枪身、两道回旋镖弯钩（每道 2–3 格粗，有亮边和橙色高光）、青白握把；**轮廓完整连续**，和造型里的枪一样大。
- 一圈连续的近黑外描边；每种材质用自己最暗的一档当阴影；没有零散杂色格；不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**（上一轮大部分是 253，这次一定要 255）。不要网格线、文字、边框、影子、地面、特效（枪口火光、子弹、钩索都不画）。

## 附图（压缩包 `akshan_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_design.png` | 定稿造型，每格 15 px 放在 1254 画布上 | **除拿枪胳膊和枪外，全部照抄** |
| `2_grid.png` | 同一张加网格线：绿线 = 头顶，红线 = 地面 | 对齐网格、大小、位置 |
| `3_arm_closeup.png` | 拿枪那条胳膊和枪（10 倍） | 手臂、护腕、手套、枪的颜色和画法 |
| `4_lol_idle.png` | 英雄联盟原版待机（3/4 朝右） | 对照：平时枪举在头边 |
| `5_lol_aim.png` | 英雄联盟原版普攻开枪的一帧 | **手臂姿势**：伸直朝前，枪平端在胸前 |
| `6_not_like_this.png` | 被否掉的拼法（8 倍） | **不要这样**：枪横在胸口糊成一团；手从胸口中间断开 |

## 提示词：`akshan-pose-aim-1.png`、`akshan-pose-aim-2.png`（两稿）

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art design of this character on a 1254x1254 canvas, every square 15 px - a rogue gunslinger: brown skin, long wavy dark-brown hair with a small topknot, a short beard, a pale blue-white scarf, grey gold-trimmed shoulder pads, a bare chest with a wide orange-red sash and a gold band, the far hand on his hip, a long dark-red cape, a teal belt and a long teal front cloth with a gold ring, dark grey-black trousers, black boots; his NEAR arm (image left, gold bracer, pale blue fingerless glove) raises a big dark-crimson-and-bronze relic pistol beside his head, its two boomerang-like hooks pointing up; 2 the same with a grid every 5 squares, the green line = the top of his hair, the red line = the ground; 3 the near arm and the pistol enlarged 10x (their colours and how they are drawn); 4 a 3D render of the original character's idle; 5 a 3D render of his attack: the arm held STRAIGHT OUT FORWARD at chest height, the pistol level, pointing forward; 6 two REJECTED attempts: the pistol lying across the chest in a jumble of red and gold, and a forearm starting in the middle of the chest as if the arm were broken - do NOT do this.
Draw with the image generator ONE pixel-art picture of the SAME character on the SAME 1254x1254 canvas with the SAME 15 px squares on the same grid, real transparent background (alpha only 0 or 255). EVERYTHING except the near arm and the pistol is copied square by square from image 1, unchanged: the hair, the face, the beard, the scarf, the shoulder pads, the sash, the far hand on the hip, the cape, the belt, the cloth, the trousers, the boots, the stance, the same place on the canvas (the top of the hair y 345, the soles y 1200).
THE NEAR ARM, like image 5: it comes from the near shoulder (the grey pad on the image left) and is held STRAIGHT OUT FORWARD to the image right at chest height, BELOW the beard - never over the face or the beard; upper arm, elbow, forearm, gold bracer and pale blue glove are ONE CONTINUOUS ARM, as thick as the design's arm. The glove holds the pistol's grip; the pistol is LEVEL with its MUZZLE POINTING FORWARD (image right), its two boomerang hooks spread forward (one up, one down), the SAME SIZE and colours as in image 1 (dark crimson and bronze with orange highlights, the pale teal-white grip), reaching out in front of him past his right side into the empty space (up to about x 1150). Where the raised pistol and arm were (left of and above the head) is now empty and transparent; the near shoulder and the cape's side under the old arm are drawn whole (the grey pad, the dark-red cape's edge with its pale blue lining), never cut off.
One continuous near-black outline round the figure; every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects (no muzzle flash, no bullet, no rope), no background, no ground, no shadow, no text, no grid lines. Make two takes.
```

## 交回前请检查

- **两张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；每格 15 px，和 `1_design.png` 同一网格。
- 除了拿枪那条胳膊和枪，其余每一格都和 `1_design.png` 一样（叠在一起检查）；头顶 y 345、鞋底 y 1200。
- 手臂从左肩出发、连成一整条、伸直朝前，在胡子下面，不挡脸；枪平端朝前，和造型里一样大，两道弯钩完整。
- 原来举枪的地方是透明的；左肩和披风左边完整。
- 没有任何特效。

## 交付（`outputs/akshan-pose/`）

- `akshan-pose-aim-1.png`、`akshan-pose-aim-2.png`；**image_gen 的原始生成图原样放 `outputs/akshan-pose/raw/`**；`generation-prompts.txt` 写明实际用的提示词；**最后**写 `HANDOFF.md`（列出交付的文件），再打包成 `outputs/akshan_pose_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- `tools/art/design_akshan_poses.py`：在包的 15 px 网格上取每格中间 7 × 7 的众数，套造型自己的调色板；下半身（腿、披风下摆）用来找 Codex 的偏移；只把手臂和枪范围内（不含头和脸）变了的格子、和原来手臂和枪的格子当印章 -> `hd/pose_aim.png` + `_edit.png`。`rig_akshan.py` 里端枪的帧把原来的枪臂拿掉，印章盖在上面，随上身一起动。逐帧检查：一块、没有新洞、手臂连着肩膀、枪完整、脸没被挡。
