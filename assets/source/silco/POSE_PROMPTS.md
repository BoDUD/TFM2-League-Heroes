# 希尔科：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 希尔科的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A，缩到游戏大小定稿：3/4 朝右，**拄着黑色手杖、举着一支发紫光的微光药剂瓶**；往后梳的黑发、远处那只眼睛是发光的橙红伤疤眼；洋红衬衫、白领巾、金边棕马甲、腰间一排紫色药剂管、深棕长裤高筒靴；黑手杖绿握柄）。
> - 请你画 **15 个姿势**（9 个动作 + 4 帧走路 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个希尔科**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 13 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**姿势、手、手杖照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。金铲铲里他普攻甩的是飞刀，我们改成**甩微光药剂瓶**，参考图里的飞刀已经藏掉了。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 = 他的左臂**，**紫线 = 他的右臂**（哪只在前面每个姿势写明了），每条手臂线第一个点是肩膀，**大圆点是手**；红线 / 蓝线 = 左腿 / 右腿；**金线 = 手杖**（两头），**金圈 = 模型里药剂瓶的位置**（只当参考，药剂瓶拿在哪只手照每个姿势的说明）；**灰框 = 头的位置**。`0_design_skeleton.png` 是待机的骨架画在定稿上，看每条线对应身体的哪一部分。
> - **头一格一格照 `1_head.png` 画在灰框里**（往后梳的黑发和翘起的一撮、橙红伤疤眼、脸朝右前方）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。手臂、手、药剂瓶、储罐、手杖**不要盖住脸**（两只眼睛和嘴）；举起来的手从脸的旁边过去。
> - **道具**：手杖照定稿的样子和长短（黑杆、绿握柄、灰球头），只照参考图换位置和角度；药剂瓶就是定稿手里那支（紫色发光、铜盖）；**储罐**是一个小铁皮罐（铜色箍、一扇发绿光的玻璃窗，约 6 × 8 格），**巨型储罐**一样的样子、约 14 × 18 格。
> - **长短要数格子**：和定稿一样，手臂从肩膀到指尖约 22 格，头（含头发）约 28 × 22 格，手杖约 36 格长。**手臂沿着骨架画，长短粗细和定稿一样，关节处弯折，不要拉长**；腿沿着红线 / 蓝线，靴子和定稿一样大。

## 15 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `silco-pose-a_wind.png` | attack@167 | 橙（左臂） | 普攻起手：身子往后一拧，近侧的手把一支微光药剂瓶举到肩膀后面（准备甩出去），另一只手夹着手杖 |
| 3 | `silco-pose-a_throw.png` | attack@333 | 紫（右臂） | 甩出药剂：身子往前探，近侧的手往前（画面右边）一甩，药剂瓶刚离手 |
| 4 | `silco-pose-a_back.png` | attack@667 | 紫（右臂） | 收势：站直，甩完的手收回身侧 |
| 5 | `silco-pose-q_wind.png` | spell@247 | 紫（右臂） | 罐装畸变体起手：身子压低，近侧的手垂在身侧下方握着一个小铁皮储罐（发绿光的玻璃窗），另一只手拄杖 |
| 6 | `silco-pose-q_throw.png` | spell@617 | 紫（右臂） | 扔出储罐：近侧的手臂高高往前上方甩起（在头的右上方，不挡脸），身子往后仰，另一只手拄着手杖 |
| 7 | `silco-pose-e_show.png` | idle2@0 | 紫（右臂） | 微光注射起手：把药剂瓶举到脸旁边端详（瓶子在脸的右边，不挡眼睛） |
| 8 | `silco-pose-e_toss.png` | attack2@500 | 紫（右臂） | 抛给队友：远侧的手往身后（画面左边）一伸、把药剂瓶抛给后面的队友，近侧的手拄着手杖 |
| 9 | `silco-pose-r_raise.png` | spell@123 | 橙（左臂） | 炼金狂潮起手：抬起一条腿、把手杖挥起来，另一只手托着一个巨大的储罐（比他的头大，发绿光） |
| 10 | `silco-pose-r_throw.png` | spell@740 | 紫（右臂） | 扔出巨型储罐：手臂笔直举过头顶往前（画面右边）一挥，巨型储罐已经脱手，身子往后仰，拄着手杖 |
| 11 | `silco-pose-run1.png` | run@0 | 紫（右臂） | 走路 1：拄着手杖往前走（金铲铲原样），前脚迈出 |
| 12 | `silco-pose-run2.png` | run@533 | 紫（右臂） | 走路 2：两脚交错，手杖点地 |
| 13 | `silco-pose-run3.png` | run@1067 | 紫（右臂） | 走路 3：另一只脚迈出 |
| 14 | `silco-pose-run4.png` | run@1600 | 紫（右臂） | 走路 4：两脚交错，手杖往前提 |
| 15 | `silco-pose-d_fall.png` | death@200 | 紫（右臂） | 被击倒：身子往后一弓、双手往上甩开（不挡脸），手杖脱手飞起 |
| 16 | `silco-pose-d_down.png` | death@900 | 紫（右臂） | 倒地：单膝跪倒、一只手撑地、低着头，手杖掉在身边地上 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 13 px squares (his soles on y 1176) - a slim, cold CRIME LORD leaning on a long BLACK CANE with a GREEN GRIP, a glowing MAGENTA-PURPLE SHIMMER VIAL raised in his other hand; black hair slicked back with a spiky tuft, his far eye a GLOWING ORANGE-RED scarred eye; a magenta shirt, a white cravat, a brown waistcoat with gold trim, four glowing purple vials at his belt, dark brown trousers and tall boots; B its HEAD shown 8x (about 28 squares wide, 22 tall: the hair, the face, the scarred eye); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the hands and the cane from it - never its 3D shading); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE = his LEFT arm, PURPLE = his RIGHT arm (each line from the shoulder, the big dot = the hand), red / blue = his left / right leg, GOLD line = the cane, GOLD ring = where the model keeps its vial, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the idle skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 13 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - each arm about 22 squares from the shoulder to the fingertips, the head with the hair about 28 x 22, the cane about 36 squares long; the body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched; the legs along the red / blue lines, the boots as big as in A. PROPS: the same cane as image A (black shaft, green grip, grey knob), only moved and turned as in C; the same glowing vial as in A; a CANISTER = a small metal can with copper bands and one glowing green glass window (about 6 x 8 squares), the HUGE CANISTER the same, about 14 x 18 squares. The near side in full tone, the far side a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the slicked-back hair with its tuft, the face to the front-right, the glowing scarred far eye) - the same head in every pose, only moved, never turned, never redrawn as a profile. No arm, hand, vial, canister or cane covers the face (the eyes and the mouth).
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no smoke, no gas, no monsters, no sparkles, no motion lines), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_wind: `WIND-UP - twisting back, his near hand lifting a glowing SHIMMER VIAL back over his shoulder, ready to fling it; the cane tucked under the other arm.`
- a_throw: `FLING - leaning forward, the near arm whipped out to the image right, the vial just leaving his hand.`
- a_back: `RECOVER - standing straight again, the throwing hand coming back to his side.`
- q_wind: `CANISTER WIND-UP - crouching a little, his near hand low at his side gripping a small metal CANISTER with a glowing green window, the other hand on the cane.`
- q_throw: `CANISTER THROW - his near arm flung high and forward above the right of his head (never over the face), leaning back, the other hand leaning on the cane.`
- e_show: `SHOW THE DOSE - the glowing vial raised beside his face, looking at it (the vial right of the face, never over the eyes).`
- e_toss: `TOSS THE DOSE - his far arm swept back to the image left tossing the vial to an ally behind him, the near hand on the cane.`
- r_raise: `FLOOD WIND-UP - one knee raised, the cane swung up, the other hand heaving up a HUGE CANISTER (bigger than his head, glowing green) at his side.`
- r_throw: `FLOOD THROW - his arm thrust straight up and forward over his head (to the image right), the huge canister already gone, leaning back on the cane.`
- run1: `WALK 1 - walking forward leaning on the cane (as in the game), the front foot stepping out.`
- run2: `WALK 2 - the legs passing, the cane planted.`
- run3: `WALK 3 - the other foot stepping out.`
- run4: `WALK 4 - the legs passing, the cane lifted forward.`
- d_fall: `STRUCK DOWN - doubled back, both arms flung up (never over the face), the cane flying out of his hand.`
- d_down: `DOWN - fallen to one knee, one hand on the ground, his head hanging, the cane lying beside him.`

## 交回

- 每个姿势一张：`outputs/silco-poses/silco-pose-<名字>.png`（1254 × 1254、真透明背景、每格 13 px）；原始生成图原样放进 `outputs/silco-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **15 张都画完再交**，最后写 `outputs/silco-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/silco_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/silco/codex_poses/`，**先量 Codex 实际的格子**（不一定是 13 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、伤疤眼还在、手不挡脸、手杖不断、没有被压扁的身体）。
- 骨架包：`tools/art/pack_silco_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_silco_pose_md.py` 生成。
