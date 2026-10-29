# 史密奇：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 史密奇的造型用户已经定稿（`0_design.png` 是你第 0 步画的 **B 伏击蹲姿（精修版）**，按你自己的格子原样读回定稿：3/4 朝右，**两腿叉开蹲低、两只机械爪向两边张开**；青绿高礼帽（紫补丁、黄铜护目镜、粉金镜片）、金橙尖发、灰褐绒毛宽脸、淡黄眼睛黑瞳孔暗红眼眶、粉鼻子、**两只横着的大尖耳（里面红色）**；紫马甲、淡黄领巾、红棕腰带、深蓝短裤；**两条橄榄绿机械手臂（黄铜箍、荧光绿菱形灯）+ 细长弯钩的黄铜爪**；黄铜机械高跷腿、深紫尖头鞋）。
> - 请你画 **20 个姿势**（10 个动作 + 8 帧走路 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一个史密奇**：样子、颜色、粗细、长短全照 `0_design.png`，**格子和它一样大：每格 9 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1176**），网格从画布左上角对齐。
> - **参考图（每个姿势一张 `*_ref.png`）是他在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，头（连礼帽和耳朵）已经放大到定稿的比例、摆在同一张画布、同一个格子上、同样的大小和位置——**身体的姿势照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。参考图里耳朵放大后像一块红色披风，**那是耳朵**，照定稿画成横着的尖耳。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（骨盆到脖子根），**橙线 / 青线 = 两条机械手臂**（两条一模一样，只分远近），每条手臂线第一个点是肩膀，**大圆点是手腕（爪子的根）**，**线的最后一段 + 空心圈 = 爪子，空心圈是中指爪尖**——爪子要画到空心圈那么长；红线 / 蓝线 = 两条腿；**灰框 = 头的位置（连礼帽和耳朵）**。`0_design_skeleton.png` 是模型的蹲姿骨架叠在定稿上：定稿的姿势和模型不完全一样（定稿的头更靠右、爪子张得更开），**只用来看每条线对应身体的哪一部分**。
> - **头一格一格照 `1_head.png` 画在灰框里**（礼帽、护目镜、金橙头发、两只横着的红尖耳、脸：两只眼睛同高、黑瞳孔、粉鼻子、往下撇的嘴）。每个姿势都是这一个头，只跟着身体移动，**不要转头、不要画成侧脸、不要重新设计**。爪子**不要挡住脸**（眼睛和鼻子）。`d_fall` / `d_down` 倒下时头跟着身体放倒，**礼帽掉了**（落在地上，照参考图的位置），头上不再戴帽子，其余还是这个头。
> - **长短要数格子**：和定稿一样，头（含礼帽和耳朵）约 61 × 51 格；机械手臂粗、爪子细长（每根爪指至少 2 格粗，不要断成单格）。**手臂沿着骨架画，长短和定稿一样，关节处弯折，不要拉长**；高跷腿沿着红线 / 蓝线，又细又长，鞋子和定稿一样大。他身体本身矮小。
> - **远近**：每张图里离镜头远的那条手臂和那条腿**暗一档**，近的完整亮色；下面的表里写了哪条手臂在前。
> - **走路 8 帧要有交叉步**：两条腿照红线 / 蓝线**前后交换**，中间几帧两条腿**交叉经过**，不要每帧都两腿大大叉开；远处那条腿暗一档。
> - **跳在半空的姿势**（`q_air`、`q_dive`）：参考图里最低的点已经放在地面线上，**照着画就行**，离地多高我在动画里再抬。
> - **`d_down`**：参考图是他翻倒的半途（腿朝天），**照它的大小和位置，把他画成仰面平躺在地上**（头在画面左、脚在右，身体贴着地面线），礼帽掉在头旁边的地上。

## 20 个姿势

| 图 | 文件 | 片段 | 前面的手臂 | 姿势 |
|---|---|---|---|---|
| 2 | `smeech-pose-a_rake.png` | slash@0 | 橙 | 爪击 1：身体猛地往前扑低，两只爪子往右前下方抓出去，爪指张开 |
| 3 | `smeech-pose-a_back.png` | slash@120 | 橙 | 爪击收回：蹲回去，爪子收到身前地面附近 |
| 4 | `smeech-pose-a_wind2.png` | stabs@250 | 橙 | 爪击 2 起手：一只爪子往后拉到身后，另一只护在身前 |
| 5 | `smeech-pose-a_thrust.png` | stabs@700 | 橙 | 爪击 2 / 连斩：蹲着把一只爪子笔直往前（画面右）刺出去，爪指朝前张开 |
| 6 | `smeech-pose-q_crouch.png` | leap@90 | 橙 | 废铁黑客起跳前：趴得很低、像要扑出去，爪子撑在身前地上 |
| 7 | `smeech-pose-q_air.png` | leap@450 | 橙 | 腾空：跳在半空，两只爪子高高张开举过头，腿缩起来 |
| 8 | `smeech-pose-q_dive.png` | pounce@280 | 橙 | 扑下：在半空往前下方扑，两只爪子伸在最前面往下抓 |
| 9 | `smeech-pose-q_land.png` | pounce@490 | 橙 | 落地：弓步落地，身子压低往前，一只爪子刺在前面 |
| 10 | `smeech-pose-e_wind.png` | arms@500 | 青 | 拆解起手：两只爪子大大张开高举在两边，爪指朝上 |
| 11 | `smeech-pose-e_rip.png` | spread@900 | 青 | 拆解：蹲低，两只爪子往两边狠狠撕开（一只往前一只往后，几乎平伸） |
| 12 | `smeech-pose-run1.png` | run@0 | 橙 | 走路 1：长腿大步走（金铲铲原样），弓着背，两只爪子在身前甩 |
| 13 | `smeech-pose-run2.png` | run@125 | 橙 | 走路 2 |
| 14 | `smeech-pose-run3.png` | run@250 | 橙 | 走路 3 |
| 15 | `smeech-pose-run4.png` | run@375 | 橙 | 走路 4 |
| 16 | `smeech-pose-run5.png` | run@500 | 橙 | 走路 5 |
| 17 | `smeech-pose-run6.png` | run@625 | 橙 | 走路 6 |
| 18 | `smeech-pose-run7.png` | run@750 | 橙 | 走路 7 |
| 19 | `smeech-pose-run8.png` | run@875 | 橙 | 走路 8 |
| 20 | `smeech-pose-d_fall.png` | death@900 | 橙 | 被击倒：身体一僵往后倒，礼帽从头上掉了，落在他身后（画面左）的地上，照参考图 |
| 21 | `smeech-pose-d_down.png` | death@1160 | 橙 | 倒地：仰面平躺在地上，礼帽掉在头旁边的地上 |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art character, 3/4 view facing right, on a 1254x1254 canvas with 9 px squares (his soles on y 1176) - a SMALL HUNCHED GREMLIN in a low wide crouch: a TALL TEAL-GREEN TOP HAT (a purple patch, brass goggles with pink-to-gold lenses), spiky GOLDEN-ORANGE hair, a wide flat face of GREY-TAUPE fur (pale yellow eyes with black pupils and dark red rims, a pink nose, a grumpy mouth), TWO HUGE POINTED EARS sticking out sideways (red inside); a purple waistcoat, a pale yellow cravat, a red-brown belt, dark blue shorts; TWO BIG OLIVE-GREEN MECHANICAL ARMS (brass rings, glowing neon-green diamond lights) ending in LONG THIN HOOKED BRASS CLAWS; thin brass mechanical stilt legs, small dark purple pointed shoes; B its HEAD shown 8x (about 61 squares wide, 51 tall: the hat, the ears, the face); C a 3D RENDER of this same character's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the BODY POSE from it - never its 3D shading; its enlarged ears look like a red cape: they are the ears); D the SKELETON of that pose, exactly over C: green = the spine (pelvis to the base of the neck), ORANGE and CYAN = his two mechanical arms (identical arms; each line from the shoulder, the big dot = the wrist where the claw starts, the last stretch ending in a HOLLOW RING = the claw, the ring = the tip of the middle claw finger), red / blue = his legs, GREY BOX = where the head (with the hat and the ears) goes, the red horizontal line = the ground; E (if attached) the model's crouch skeleton over image A, only to show which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 9 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; his soles (or the lowest point) on y 1176.
COUNT THE SQUARES: the same proportions as image A - the head with the hat and the ears about 61 x 51, the mechanical arms thick, the claws long and thin (every claw finger at least 2 squares thick inside the outline, never broken into single squares), the body itself small. The body exactly where C shows it. Each arm along its line, bending at the elbow, never stretched, the claw reaching to the hollow ring; the stilt legs along the red / blue lines, thin and long, the shoes as big as in A. The near arm and leg in full tone, the far arm and leg a step darker.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the top hat with its goggles, the golden-orange hair, both red ears sticking out sideways, the face: both eyes at the same height with black pupils, the pink nose, the grumpy mouth) - the same head in every pose, only moved (tilted with the body when he falls or lies down, and then without the hat, which lies on the ground as in C), never turned, never redrawn as a profile. No claw covers the face.
The same colours as image A; one continuous 1-square near-black outline; no stray single squares, no dithering, no gradients, no glow halo, no blur, no anti-aliasing.
No effects (no claw slashes, no shimmer, no sparks, no motion lines, no dust), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_rake: `RAKE - lunging forward and low, both claws raked out to the lower front-right, the claw fingers spread.`
- a_back: `RECOVER - crouched back down, the claws pulled in near the ground in front of him.`
- a_wind2: `WIND-UP - one claw drawn far back behind him, the other held in front.`
- a_thrust: `THRUST - crouched, one claw driven straight forward (image right), the claw fingers spread forward.`
- q_crouch: `GATHER - crouched very low like a cat about to pounce, the claws planted on the ground in front.`
- q_air: `IN THE AIR - leaping, both claws spread high above his head, the legs tucked up.`
- q_dive: `DIVE - in mid-air pouncing down and forward, both claws reaching out in front, raking down.`
- q_land: `LAND - landing in a low lunge, leaning forward, one claw stabbed out in front.`
- e_wind: `RIP WIND-UP - both claws thrown wide and high to the sides, the claw fingers up.`
- e_rip: `RIP - crouched low, both claws torn apart to the sides (one forward, one back, almost level).`
- run1: `WALK 1 - a long-legged loping stride (as in the game), hunched, the claws swinging in front of him.`
- run2: `WALK 2`
- run3: `WALK 3`
- run4: `WALK 4`
- run5: `WALK 5`
- run6: `WALK 6`
- run7: `WALK 7`
- run8: `WALK 8`
- d_fall: `KNOCKED DOWN - stiff, falling over backwards, the TOP HAT knocked off his head and lying on the ground behind him (image left), as in the reference.`
- d_down: `DOWN - lying flat on his back on the ground, the top hat fallen on the ground beside his head.`

## 交回

- 每个姿势一张：`outputs/smeech-poses/smeech-pose-<名字>.png`（1254 × 1254、真透明背景、每格 9 px）；原始生成图原样放进 `outputs/smeech-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。
- **20 张都画完再交**，中间不要停，最后写 `outputs/smeech-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/smeech_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/smeech/codex_poses/`，**先量 Codex 实际的格子**（不一定是 9 px），读 raw，按定稿的头（hd/idle.png）对齐、缩到定稿的密度；每帧 8 倍检查（头不动、两只眼睛和鼻子还在、爪子不挡脸、爪子长短对、没有被压扁的身体、高跷腿不变形、走路有交叉步、远近手脚深浅分得开、倒地时礼帽掉了）。
- 骨架包：`tools/art/pack_smeech_poses.py`（骨架是他客户端模型自己的骨骼，按动作片段的那一帧投影：不是手摆的）；这份提示词由 `tools/art/gen_smeech_pose_md.py` 生成。
