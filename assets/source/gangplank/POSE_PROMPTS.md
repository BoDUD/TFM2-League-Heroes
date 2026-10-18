# 普朗克：拿枪那只手的两个姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 用户已经定下了普朗克的造型（`1_design.png`，就是你上一轮画的 A-2，按它自己的格子读回，靴子修过）。其他动作都已经用这个造型做好了。
> - 只差两个动作：造型里拿枪的那只手（画面**左边**，红色灯笼袖、金护腕、棕手套）把金色手炮扛在肩上、手在脸旁边。英雄联盟里 **Q（枪火谈判）是手臂伸直、把枪端在胸前朝前开枪**，**R（加农炮幕）是手臂整条举过头顶、枪口朝天**。这两种手臂在造型里没有，我用造型里的格子怎么拼都不像（`7_not_q.png`、`8_not_r.png` 是被用户否掉的样子：胸前一团红金色、袖子和肩膀脱开）。
> - **这一轮只画两张图：同一个普朗克，除了拿枪那条胳膊和手炮，其余每一格都和 `1_design.png` 一模一样**（帽子、脸、胡子、身体、腰带、外套、裤子、靴子、右边拿弯刀的手和弯刀，位置和颜色都不变）。

## 两张图

- **`gangplank-pose-Q.png`：Q 端枪（照 `5_lol_q_aim.png`）**
  - 拿枪那条胳膊从**画面左边的肩膀**出发，伸直朝前（画面右边），手臂横在胸口高度，**在胡子下面，绝不能挡住脸和胡子**。
  - 棕手套握着金色手炮，**炮口朝前（朝画面右边）**，手炮整个伸出到身体前面一些。
  - 手臂原来扛炮的位置空出来后，**左边的肩膀和外套侧面要画完整**（青绿色领子的肩膀、深色外套的侧面），不能像被切掉一样。
- **`gangplank-pose-R.png`：R 举枪朝天（照 `6_lol_r_up.png`）**
  - 拿枪那条胳膊从**画面左边的肩膀**举起来，**整条手臂伸直朝上**，在帽子左边（**不挡脸、不挡帽子**），红袖子和金护腕跟着手臂，棕手套握着金色手炮，**炮口竖直朝天**，比帽子高。
  - 手臂下面的肩膀和外套侧面画完整。

## 格子和位置（照 `1_design.png` / `2_grid.png`）

- 画布 **1254 × 1254**，**每格 17 px**，和 `1_design.png` 同一个网格（`2_grid.png` 的浅灰线每 5 格一条）。
- 人还是 **57 × 62 格**，**帽子顶 y = 160**（绿线），**两只鞋底 y = 1214**（红线），左右位置不变；帽子上面留了约 9 格空间，**R 举起来的手炮就画在这里**（炮口最高到 y ≈ 30，不出画）。
- 只有拿枪那条胳膊和手炮是新画的，**其余部分照抄 `1_design.png`，一格都不要动**。

## 要画清楚的地方

- 红色灯笼袖（红 3 档）、金护腕（金 2–3 档 + 高光）、棕手套，和 `3_arm_closeup.png` 里一样的颜色和画法。
- 金色燧发手炮：粗短的炮身、炮口一圈喇叭口、雕花的金环，和造型里的手炮一样大、一样的颜色（只是朝向变了）。
- 一圈连续的近黑外描边；每种材质用自己最暗的一档当阴影；没有零散杂色格；不要抖动、渐变、柔光。
- **真透明背景，alpha 只能是 0 或 255**。不要网格线、文字、边框、影子、地面、特效（枪口火光、烟都不画）。

## 附图（压缩包 `gangplank_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_design.png` | 定稿造型，每格 17 px 放在 1254 画布上 | **除拿枪胳膊和手炮外，全部照抄** |
| `2_grid.png` | 同一张加网格线：绿线 = 帽子顶，红线 = 地面 | 对齐网格、大小、位置 |
| `3_arm_closeup.png` | 拿枪那条胳膊和手炮（10 倍） | 袖子、护腕、手套、手炮的颜色和画法 |
| `4_lol_idle.png` | 英雄联盟原版待机（3/4 朝右） | 对照：手炮平时扛在肩上 |
| `5_lol_q_aim.png` | 英雄联盟原版 Q 开枪的一帧 | **Q 的手臂姿势**：伸直朝前，枪端在胸前 |
| `6_lol_r_up.png` | 英雄联盟原版 R 的一帧 | **R 的手臂姿势**：整条举直，枪口朝天 |
| `7_not_q.png` / `8_not_r.png` | 被否掉的拼法 | **不要这样**：胸前一团、袖子和肩膀脱开、左半边像被切掉 |

## 提示词：`gangplank-pose-Q.png`、`gangplank-pose-R.png`

附全部图。**用 image_gen 画。**

```text
Attached images: 1 the approved pixel-art design of this character on a 1254x1254 canvas, every square 17 px - a burly pirate captain: a black crescent pirate hat, a frowning face, a long greyish-brown beard tied with a red cloth, a bare chest under a teal-green collar, a red sash with a gold buckle, a dark-purple coat behind him with gold trim, dark grey-green trousers, brown boots with gold cuffs; in the FAR hand (image right) a dark cutlass with an orange-hot tip; the NEAR arm (image left: a red puffy sleeve, a gold bracer, a brown glove) rests a GOLDEN FLINTLOCK HAND CANNON on his near shoulder; 2 the same with grid lines every 5 squares (green = the hat's top, red = the ground); 3 the near arm and the cannon enlarged; 4-6 3D renders of the same character from the game: 4 his idle, 5 his pistol shot (the arm held straight out forward, the pistol at chest height aimed forward), 6 his signal (the arm raised straight up, the pistol pointing at the sky); 7 and 8 rejected attempts (a jumble on the chest, the sleeve apart from the shoulder) - do NOT draw it like those.
Draw with the image generator TWO pixel-art pictures of the SAME character on the SAME 1254x1254 canvas with the SAME 17 px squares on the same grid, real transparent background (alpha only 0 or 255). In both, EVERYTHING except the near arm and the cannon is copied square by square from image 1, unchanged: the hat, the face, the beard, the body, the sash, the coat, the trousers, the boots, the far hand and the cutlass, same places, same colours; the hat's top at y 160, the soles at y 1214 (the room above the hat is for R's raised cannon, its muzzle no higher than y 30). Only the near arm (red puffy sleeve, gold bracer, brown glove, the same colours and style as image 3) and the golden hand cannon (the same size, colours and carving as in image 1, only turned) are drawn anew, and where the arm used to rest on the shoulder the near shoulder and the side of the coat are drawn whole (the teal collar's shoulder, the coat's dark side) - never a straight cut down his side.
PICTURE Q (gangplank-pose-Q.png), his pistol shot like image 5: the near arm comes from the near shoulder and is held straight out forward (to the image right) across the chest at chest height, BELOW the beard (never over the face or the beard); the glove holds the golden hand cannon with its MUZZLE POINTING FORWARD (image right), the cannon out in front of his body.
PICTURE R (gangplank-pose-R.png), his signal like image 6: the near arm is raised STRAIGHT UP from the near shoulder, beside the hat on its left (never over the face or the hat), the red sleeve and the gold bracer along the raised arm, the glove holding the golden hand cannon with its MUZZLE POINTING STRAIGHT UP at the sky, above the hat.
One continuous near-black outline round the figure; every material's shadow in its own darkest shade; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing. No effects (no muzzle flash, no smoke), no background, no ground, no shadow, no text, no grid lines.
```

## 交回前请检查

- **两张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；每格 17 px，和 `1_design.png` 同一网格。
- 除了拿枪那条胳膊和手炮，其余每一格都和 `1_design.png` 一样（可以把两张叠在一起检查）。
- Q：胳膊从左肩伸直朝前，枪在胸口高度、胡子下面，炮口朝右；左肩和外套侧面完整。
- R：胳膊从左肩举直朝上，在帽子左边，炮口竖直朝天；左肩和外套侧面完整。
- 没有任何特效。

## 交付（`outputs/gangplank-poses/`）

- `gangplank-pose-Q.png`、`gangplank-pose-R.png`；原始生成图原样放 `outputs/gangplank-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/gangplank_poses_done.zip`。中间不要停，两张都画完再交。

## Claude 收到后（给 Claude 看）

- 按 17 px 格读回（regrid，必要时量实际格子），和设计稿逐格比，只取变了的那块（拿枪胳膊 + 手炮 + 补出来的肩膀和外套侧面）当 Q / R 的零件，其余用设计稿自己的格子；Q：待机 → 端枪（几帧带身体后坐）→ 回到肩上；R：待机 → 举枪 → 停住（信号弹是特效）→ 放下。做完自查再给用户审。
