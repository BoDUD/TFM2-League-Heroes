# 深红锋喙鸟：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 锋喙鸟的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A（加了红冠的那版），按它自己 11 px 的格子读回，1:1 定稿，这里放大成每格 10 px：3/4 朝右，**压低身子蹲着的圆胖鸟**；**红色背羽和尾羽**往后上方翘；**紫色尖刺鬃毛**围着脖子；**棕色骨质鸟头、厚厚的弯钩喙、两只发光的橙色眼睛**，嘴里透橙光；头顶一个红色尖冠；**两条短棕腿、深藏青弯钩大爪**）。每个姿势都照它。
> - 请你画 **18 个姿势**（8 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只鸟**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 10 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：翅膀和羽冠张开、腾空、仰头、侧翻倒地的时候，画面会变高、变宽或变矮，**但身子、头、腿不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**头每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、两条腿、翅膀、尾巴、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。**羽毛的颜色分区（红色背羽尾羽、紫色鬃毛）、头和喙的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头，最后一段是下喙），**棕线 = 尾巴**，**粉线 / 青线 = 两只小翅膀**，**红线 / 蓝线 = 两条腿**；**灰框 = 头的位置**。**近处（画面右边、离我们近）的始终是蓝线腿和青线翅膀**（跑步时两条腿前后交错，也还是蓝线那条在近处）。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（棕色骨质鸟头、弯钩喙、两只橙色眼睛）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**张嘴的姿势**（a_jab、q_spread、e_land、r_call、d_fall）只把下喙按绿线最后一段往下打开，嘴里画橙光，上半个头不变。只有 `d_down` 眼睛熄灭（暗褐色，不发光）。
> - **腿**：一直是定稿那两条短棕腿和深藏青弯钩大爪，**照骨架的红线 / 蓝线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿颜色正常、画在上面，远处的暗一档**。翅膀平时收在身侧看不见，**只有 q_rear、q_spread 张开**（照粉线 / 青线，红紫尖羽）。
> - **跑步 8 帧（run1–run8）是一整圈**：近处的腿迈一步、远处的腿迈一步；**每帧的身子、头、羽毛都是同一个**，只有两条腿按骨架换位置、身子跟着上下一点点。**一定要看得出两条腿在交替迈步**。
> - **死亡（d_fall、d_down）**：d_down 翻倒侧躺在地上；身子、头、羽毛的大小不变，只是躺倒。

## 18 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `raptor-pose-a_back.png` | attack@333 | 普攻「锋羽射击」起手：羽冠和背羽一下竖起炸开，脑袋往后上方缩、蓄力 |
| 3 | `raptor-pose-a_jab.png` | attack@666 | 射出：脑袋猛地往前一探、嘴张开（嘴里橙光），身子压低前冲，尾羽往后拉直 |
| 4 | `raptor-pose-q_rear.png` | attack2@350 | 技能1「羽刃扇射」起手：身子往后仰，两只小翅膀开始张开，羽冠竖起 |
| 5 | `raptor-pose-q_spread.png` | attack2@500 | 甩出：两只翅膀和羽冠全部张开成一大圈扇形（红紫两色尖羽），嘴张大朝前 |
| 6 | `raptor-pose-e_hop.png` | spawn@200 | 技能2「惊飞跃退」：受惊往后一跳，整只鸟腾在空中，两条腿收在身下、爪子张开 |
| 7 | `raptor-pose-e_land.png` | spawn@600 | 落地：两脚着地蹲低，嘴张开尖叫（嘴里橙光），羽毛还炸着 |
| 8 | `raptor-pose-r_rear.png` | roar@200 | 大招「鸟群之家」起手：两条腿站直、身子挺高，脑袋往后仰 |
| 9 | `raptor-pose-r_call.png` | roar@400 | 召唤：仰头张大嘴大叫（嘴张到最大，嘴里橙光），羽冠竖起，呼唤小鸟 |
| 10 | `raptor-pose-run1.png` | run@0 | 跑 1：近处的腿往前伸、准备落地，远处的腿在后面蹬地 |
| 11 | `raptor-pose-run2.png` | run@150 | 跑 2：近处的腿落地，身子压低 |
| 12 | `raptor-pose-run3.png` | run@300 | 跑 3：近处的腿撑住、往后蹬，远处的腿收起往前 |
| 13 | `raptor-pose-run4.png` | run@450 | 跑 4：近处的腿蹬到最后，远处的腿抬到最高（腾空） |
| 14 | `raptor-pose-run5.png` | run@600 | 跑 5：远处的腿往前伸、准备落地，近处的腿在后面 |
| 15 | `raptor-pose-run6.png` | run@750 | 跑 6：远处的腿落地，身子压低 |
| 16 | `raptor-pose-run7.png` | run@900 | 跑 7：远处的腿往后蹬，近处的腿收起往前 |
| 17 | `raptor-pose-run8.png` | run@1050 | 跑 8：远处的腿蹬到最后，近处的腿抬到最高（8 接回 1，循环） |
| 18 | `raptor-pose-d_fall.png` | death@150 | 被打倒：猛地往后仰、踉跄，嘴张开，两条腿离地乱蹬 |
| 19 | `raptor-pose-d_down.png` | death@1000 | 倒地：翻倒侧躺在地上不动，两条腿朝天，眼睛熄灭（画成暗褐色，不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (its lowest point on y 1176) - a ROUND, PLUMP, LOW-CROUCHED BIRD-RAPTOR: CRIMSON / ORANGE-RED BACK AND TAIL FEATHERS sweeping back and up into a fan of spiky tail feathers, a RUFF OF DEEP PURPLE SPIKE FEATHERS round the neck, a BIG BROWN BONY BIRD HEAD with a THICK HOOKED BEAK and TWO GLOWING ORANGE EYES, an orange glow in the mouth, ONE RED POINT of crest on top of the head, TWO SHORT BROWN LEGS with BIG HOOKED DARK NAVY TALONS, two tiny wings folded and hidden at its sides; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the two legs, the wings, the tail, the body's and the head's angle from it - never its 3D shading; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head, its last stretch the lower beak), BROWN = the tail, PINK and CYAN = its two little wings, RED and BLUE = its two legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when the wings and crest spread, it hops into the air, rears up or lies on its side (the picture simply grows taller, wider or shorter - never shrink the body or the head to fit). Each leg along its line (short brown bird leg, the big hooked dark navy talons at the end), bending at the knee, never stretched, never squashed, never thinner than in A; the NEAR leg in full tone and in front, the FAR one a step darker. The wings stay folded and hidden unless the pose says they open; open, each wing follows its line as a fan of red and purple pointed feathers. The red back and tail feathers and the purple ruff stay where they are on the body, as big pointed triangles.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the brown bony head, the hooked beak, the two orange eyes) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; where the pose opens the beak, only the lower beak swings down along the green line's last stretch with the orange glow inside; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no flying feathers, no little birds, no marks, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_back: `GATHER - the crest and back feathers bristling up, the head drawn back and up, winding up.`
- a_jab: `JAB - the head thrust sharply forward, the beak open (the orange glow inside), the body low and lunging, the tail stretched straight back.`
- q_rear: `REAR - the body rearing back, the two small wings starting to open, the crest raised.`
- q_spread: `FAN OUT - both wings and the crest spread wide into a big fan of red and purple spiky feathers, the beak wide open facing front.`
- e_hop: `HOP - startled, hopping backwards: the whole bird up in the air, both legs tucked under it, the talons spread.`
- e_land: `LAND - landed on both feet, crouched low, the beak open screeching (the orange glow inside), the feathers still bristling.`
- r_rear: `RISE - standing up tall on straight legs, the body raised, the head tipped back.`
- r_call: `CALL - the head up, the beak open as wide as it goes (the orange glow inside), the crest raised, calling the flock.`
- run1: `RUN 1 - the near leg reaching forward to land, the far leg pushing off behind.`
- run2: `RUN 2 - the near leg landing, the body dipping low.`
- run3: `RUN 3 - the near leg planted and pushing back, the far leg tucking up and swinging forward.`
- run4: `RUN 4 - the near leg pushed back to the end, the far leg at its highest (in the air).`
- run5: `RUN 5 - the far leg reaching forward to land, the near leg behind.`
- run6: `RUN 6 - the far leg landing, the body dipping low.`
- run7: `RUN 7 - the far leg pushing back, the near leg tucking up and swinging forward.`
- run8: `RUN 8 - the far leg pushed back to the end, the near leg at its highest (8 runs on into 1: the loop).`
- d_fall: `HIT DOWN - thrown back rearing and staggering, the beak open, both legs kicking off the ground.`
- d_down: `DOWN - toppled over onto its side, lying still, the legs up, the eyes gone dark (a dull dark brown, no glow).`

## 交回

- 每个姿势一张：`outputs/raptor-poses/raptor-pose-<名字>.png`（1254 × 1254、真透明背景、每格 10 px）；原始生成图原样放进 `outputs/raptor-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **18 张都画完再交**，最后写 `outputs/raptor-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/raptor_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/raptor/codex_poses/`，**先量 Codex 实际的格子**（不一定是 10 px），读 raw，**每张按定稿的身体大小读**（翅膀张开、腾空时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、两只橙眼还在、腿没有被压扁或拉长、跑步 8 帧两条腿真的交替、远处的腿暗一档）。
- 骨架包：`tools/art/pack_raptor_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；头放大 1.3 倍；跑步按 1.2 s 一整圈均匀取 8 帧 (0, 150, 300, 450, 600, 750, 900, 1050) ms）；这份提示词由 `tools/art/gen_raptor_pose_md.py` 生成。
