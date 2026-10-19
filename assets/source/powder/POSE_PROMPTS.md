# 爆爆（金铲铲之战 · 双城之战）：动作部件包（给 Codex 的提示词）

> **这一步必须用画图模型（image_gen）画。** 一共三张图：
> - **H 干净的头**：待机造型（用户选定的 A-2）的头，**去掉托下巴的手**。以后每一帧都用这张脸。
> - **P 七个动作姿势**：每个姿势照一具**骨架**画（红 = 近侧的手脚，蓝 = 远侧的手脚，灰 = 身体和头的圆）。**骨架每一段的长度就是造型自己的长度**：腿和手臂必须照线画，不能画长、画短、画粗。
> - **R 跑步 8 帧**：同样照骨架画。
>
> 样子、颜色、衣服全照 `3_look_idle.png`（待机造型，8 倍）和 `3_look_side.png`（侧面造型，8 倍）。`4_tft_poses.png` / `4_tft_run.png` 是金铲铲里她做同样动作的样子，**只看动作的感觉**（每格对应的姿势按顺序：wind、throw、crouch、toss、slam、hop、hit；跑步 8 帧）。

## H：干净的头（`powder-head.png`）

- `0_head_fix.png` 是待机造型的头和肩（33 × 27 格，**每格 22 px**）。**洋红色的格子是托下巴的拳头和护臂**：只重画这些格子，画成**下巴**（第 19–20 行：下巴的肉色和下面一格近黑描边）、**脖子**（2–3 格宽的肉色，暗面深一档）和**青绿上衣的领口**（照 `3_look_side.png` 的领口：青绿色，里面露一点粉色衬衣）。
- **其他所有格子一格都不改**：头发、两个金色 X 发夹、眼睛、眉毛、嘴、脸颊、小辫子、肩膀、伸出去的手都原样保留。
- 同样大小（726 × 594，每格 22 px），对齐同一个网格；真透明背景（alpha 只有 0 / 255）。

## P：七个动作姿势（`powder-poses.png`）

- `1_poses_guide.png`：8 个格子里画了 7 具骨架（最后一格空），**每一小格 = 7 px 一格像素**，浅绿线每 5 格一条，棕线是地面。画好的图**和这张图一样大、格子摆放一样**，每个姿势画在它自己的格子里、站在地面线上（hop 在空中）。
- 每个人物**从头顶到脚底约 53 格**（和造型一样；hop、crouch 这种弯着的当然矮一些），**每格 7 px**，像素块大小一致、对齐网格。
- **头**：画在灰色圆圈上，**和 H 一样的头**——3/4 朝右前方、两只眼睛都看得见，头发、发夹、小辫子都一样，大小就是圆圈的大小（直径约 22 格）。**头不跟着身体歪，也不转成只有一只眼的侧脸。**
- **身体**：照灰线（脖子到胯）画青绿上衣、粉色袖子、棕色皮带和银扣、身后的蓝色小炸弹皮袋。
- **手臂**：照红线 / 蓝线的每一段画（上臂、前臂、手），深棕色护臂、手指露出来；**近侧（红）在身体前面，颜色正常；远侧（蓝）在身体后面，暗一档**。手里不拿东西。手臂不能挡住脸。
- **腿**：照红线 / 蓝线的每一段画（大腿、小腿、脚），紫色裤袜、棕色短靴，**靴子和造型里一样大、一样的形状**；近侧（红）颜色正常、画在前面，远侧（蓝）暗一档。膝盖就在骨架的膝盖点上。
- **骨架线、圆圈、网格线、地面线、文字一律不要留在画好的图里**；背景用真透明（或者整片纯绿 #00FF00）。

## R：跑步 8 帧（`powder-run.png`）

- `2_run_guide.png`：8 个格子，每格一具骨架（顺序从左到右、从上到下）。要求和 P 完全一样：同样大小、同样格子、每格 7 px、约 53 格高、H 的头、照骨架画手和腿。
- 跑的时候头和身子是一样的，**只有腿和手臂在变**；8 帧里头、上衣、皮袋的样子保持一致。

## 附图（压缩包 `powder_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 | 用在 |
|---|---|---|
| `0_head_fix.png` | 待机造型的头，洋红 = 要重画的手 | **H** |
| `1_poses_guide.png` | 七具骨架（每格 7 px） | **P** 的位置、姿势、每一段的长度 |
| `2_run_guide.png` | 跑步 8 具骨架 | **R** |
| `3_look_idle.png` | 待机造型（用户选定，8 倍） | 样子、颜色、脸、头发 |
| `3_look_side.png` | 侧面造型（用户选定，8 倍） | 侧面的身体、衣服、皮袋、靴子、领口 |
| `4_tft_poses.png` | 金铲铲里的同样七个动作 | 只看动作感觉 |
| `4_tft_run.png` | 金铲铲里的跑步 | 只看动作感觉 |

## 提示词

每张图附全部图片。**用 image_gen 画。**

### H（`powder-head.png`）

```text
Attached: 0_head_fix - a pixel-art head and shoulders of a small chibi girl (bright blue messy hair, two gold X-shaped hair clips, big blue eyes, two thin braids), 33 x 27 squares of 22 px each; the MAGENTA squares are a fist and a brown arm wrap held at her chin. 3_look_idle and 3_look_side - the approved character, 8x (one square = one pixel): her look, her neck and the teal tunic's collar.
Redraw ONLY the magenta squares, with the image generator, as the parts the hand was hiding: the chin (light warm skin with a near-black outline square row under it), a short neck 2-3 squares wide (skin, its shadow side one shade darker) and the collar of the teal tunic with a little pink shirt showing, as in 3_look_side. Every other square stays EXACTLY as it is: the hair, the clips, the eyes, the brows, the mouth, the cheeks, the braids, the shoulders and the held-out hand. Same size (726 x 594), every square 22 px on the same grid, a real transparent background (alpha only 0 or 255), no glow, no blur, no new colours.
```

### P（`powder-poses.png`）和 R（`powder-run.png`）

```text
Attached: 1_poses_guide (or 2_run_guide) - stick-figure skeletons, one per cell on green: RED = the NEAR arm and leg, BLUE = the FAR arm and leg, GREY = the body line (neck to hip) and a circle for the head; one small grid square = one pixel-art square of 7 px, the brown line is the ground. powder-head (or 0_head_fix with the hand removed) - her head, the SAME head in every pose. 3_look_idle and 3_look_side - the approved character, 8x: a small chibi girl with bright blue messy hair, two gold X-shaped hair clips, big blue eyes, two thin braids, a teal tunic with short pink striped sleeves, dark brown fingerless arm wraps, a brown belt with a silver buckle, a brown pouch of small blue bombs at her hip, purple tights and brown laced boots. 4_tft_poses / 4_tft_run - the same character in another game doing these moves: the FEEL of each pose only.
Draw with the image generator ONE pixel-art picture the SAME SIZE as the guide with the SAME cells: in every cell, the girl posed EXACTLY on that cell's skeleton, every square 7 px on one straight grid, about 53 squares from the top of her head to her soles when standing, the soles on the cell's ground line (the hop in the air above it).
THE HEAD: on the grey circle, the size of the circle (about 22 squares across), the SAME head as powder-head in every cell - turned to the front-right with BOTH eyes visible, never tilted with the body, never a one-eyed profile.
THE LIMBS follow the lines segment for segment - upper arm, forearm and hand; thigh, shin and boot - EXACTLY as long as the lines, the joints on the dots: never longer, shorter or thicker. The arm wraps and the boots the same size and shape as in 3_look_side. The NEAR (red) arm and leg in front of the body in full tone, the FAR (blue) ones behind it one shade darker. Nothing in her hands; no arm over her face.
THE BODY along the grey line: the teal tunic, the pink sleeves, the brown belt and silver buckle, the pouch of blue bombs behind her hip.
Clean pixel art like 3_look_side: a 1-square near-black outline, 2-3 flat shades a material, no dithering, no gradients, no glow, no blur, no anti-aliasing. NO stick lines, circles, grid lines, ground lines or text left in the picture; a real transparent background (or one flat pure green #00FF00). No effects, no props, no shadows.
```

（R 用同一段提示词，把 1_poses_guide 换成 2_run_guide；跑步时头和身子 8 帧都一样，只有手臂和腿在变。）

## 交回前请检查

- **全部是 image_gen 画的**。H：只改了洋红格子，其他格子一格没动；下巴、脖子、领口自然。
- P / R：和骨架图一样大、格子一样摆；每个人物照自己格子里的骨架，**手臂、腿每一段和线一样长**、膝盖肘部在点上；靴子和造型一样大；头是 H 的同一个头、两只眼睛都看得见、和圆圈一样大；近侧亮、远侧暗；没留下任何骨架线、圆圈、网格、文字；真透明或纯绿背景。
- 中间不要停，三张都画完再交。

## 交付（`outputs/powder-poses/`）

- `powder-head.png`、`powder-poses.png`、`powder-run.png`；原始生成图原样放 `outputs/powder-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/powder_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- H 从 raw 按 22 px 读回，和 idle.png 逐格比：洋红以外的格子要一样（不一样的用原格子），得到 `hd/head.png`（每一帧贴的头）。
- P / R 按格子切开，各自按格读回、和骨架比长度（腿、手臂每段误差不超过 1 格），8 倍逐格自查（rig-deformation-checks、codex-legs-need-skeletons）；头换成 head.png（下巴对准脖子、脸中线对准），颜色吸到 idle / side 的调色板；再在 `rig_powder.py` 里排成每个动作的帧（姿势之间只整格平移、四分之一转、镜像）。
