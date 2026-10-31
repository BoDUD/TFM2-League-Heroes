# 远古巨龙：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 远古巨龙的造型用户已经定稿（`0_design.png` 是你第 0 步画的**第一版 A**（细格子、脸最清楚的那版），按它自己约 7.5 px 的格子读回，1:1 定稿，这里放大成每格 6 px：3/4 朝右，**四条腿压低站着的翼龙**；**两只深紫色大蝙蝠翼**半张开往上举，翼骨和翼指尖是**青色发光的爪尖**；背上、尾巴上一排排**青色水晶尖刺**；**白色晶体鬃毛**盖住脖子和胸口；**深色尖嘴、两只往后弯的蓝色大角、发青光的嘴、青色眼睛**；尾巴往上卷，末端一把尖刺扇）。每个姿势都照它。
> - 请你画 **18 个姿势**（8 个动作 + 8 帧飞行 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **远古巨龙移动时是低空飞行**（英雄联盟里的远古巨龙没有跑步动作），所以 8 帧「飞」是**原地振翅飞**的一整圈：翅膀从最高扇到最低再提回来。大招飞上天也用这 8 帧。
> - **每张都是同一条龙**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 6 px**，画布 **1254 × 1254**，红线是地面（**最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：翅膀张开举高、腾空、倒地的时候，画面会变高、变宽或变矮，**但身子、头、腿、翅膀不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**头每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是同一个 3D 模型做那个动作的那一帧**，摆在同一张画布、同一个格子上、同样的高度和位置，头已经放大了一些——**姿势、四条腿、两只翅膀、尾巴、身体和头的角度照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。**颜色分区（深紫翼膜、青色尖刺、白色鬃毛、蓝角）、头的大小照定稿**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱和脖子（屁股到头，最后一段是下颚），**棕线 = 尾巴**，**粉线 / 青线 = 两只翅膀**（从肩膀到翼尖），**橙线 / 紫线 = 两条前腿**，**红线 / 蓝线 = 两条后腿**；**灰框 = 头的位置**。**近处（画面右边、离我们近）的始终是青线翅膀、紫线前腿、蓝线后腿**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **头一格一格照 `1_head.png` 画在灰框里**（深色尖嘴、两只蓝色弯角、青色眼睛、发光的嘴、下巴的白晶刺）。每个姿势都是这一个头，只跟着身体移动和倾斜，**不要转头、不要重新设计**。**张嘴的姿势**（a_bite、q_rear、q_breath）只把下颚按绿线最后一段往下打开，嘴里画亮青光和白牙，上半个头不变。只有 `d_down` 眼睛和嘴的青光熄灭（暗灰蓝色，不发光）。
> - **腿**：一直是定稿那四条腿和黑色弯钩爪，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿颜色正常、画在上面，远处的暗一档**。**翅膀**照粉线 / 青线张开或收拢，翼膜是大块深紫色平涂，翼骨深一档，每根翼指尖一个青色发光爪尖；近处的翅膀在前面、完整，远处的翅膀在身后、暗一档。
> - **飞行 8 帧（run1–run8）是一整圈振翅**：**每帧的身子、头、尾巴都是同一个**，只有两只翅膀按骨架上下扇、身子跟着上下一点点、四条腿收在身下。**一定要看得出翅膀在一下一下地扇**。
> - **死亡（d_fall、d_down）**：d_down 侧翻倒在地上；身子、头、翅膀的大小不变，只是躺倒。

## 18 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `elderdragon-pose-a_back.png` | bite@600 | 普攻「龙焰撕咬」起手：脑袋往后上方一缩，脖子弯起来，嘴微张，蓄力 |
| 3 | `elderdragon-pose-a_bite.png` | bite@950 | 咬：脑袋猛地往前下方一探，嘴张大咬下去（嘴里青光），前身压低前冲 |
| 4 | `elderdragon-pose-q_rear.png` | breath@800 | 技能1「烈焰吐息」起手：前身稍抬，脑袋往后仰，嘴张开，胸口和嘴里的青光变亮（吸气） |
| 5 | `elderdragon-pose-q_breath.png` | breath@1150 | 喷火：脖子往前伸直、脑袋压低朝前，嘴张到最大（嘴里亮青光）——火焰之后单独画，这里不画 |
| 6 | `elderdragon-pose-e_rear.png` | wings@300 | 技能2「龙翼风暴」起手：前身立起来，两只大翅膀高高举过头顶完全张开 |
| 7 | `elderdragon-pose-e_slam.png` | wings@600 | 扇下：两只翅膀猛地往下往前拍到底，前爪落地，身子压低 |
| 8 | `elderdragon-pose-r_jump.png` | leap@856 | 大招「绝伦火热」起飞：后腿一蹬跃上天空，翅膀张开往上举，四条腿收在身下 |
| 9 | `elderdragon-pose-r_land.png` | leap@1284 | 砸落：从天上砸回地面，四条腿重重着地、身子压到最低，翅膀往两边撑开 |
| 10 | `elderdragon-pose-run1.png` | hover@0 | 飞 1：两只翅膀举到最高，往上张开 |
| 11 | `elderdragon-pose-run2.png` | hover@291 | 飞 2：翅膀开始往下扇 |
| 12 | `elderdragon-pose-run3.png` | hover@583 | 飞 3：翅膀扇到一半，平着往两边伸 |
| 13 | `elderdragon-pose-run4.png` | hover@875 | 飞 4：翅膀扇到最低，身子被托起 |
| 14 | `elderdragon-pose-run5.png` | hover@1166 | 飞 5：翅膀从最低处收拢往回提 |
| 15 | `elderdragon-pose-run6.png` | hover@1458 | 飞 6：翅膀往上提到一半 |
| 16 | `elderdragon-pose-run7.png` | hover@1750 | 飞 7：翅膀快要举到最高 |
| 17 | `elderdragon-pose-run8.png` | hover@2041 | 飞 8：翅膀回到最高（8 接回 1，循环） |
| 18 | `elderdragon-pose-d_fall.png` | death@1070 | 被打倒：身子一沉，翅膀垂下，脑袋往下耷拉，腿开始发软 |
| 19 | `elderdragon-pose-d_down.png` | death@2497 | 倒地：侧翻倒在地上不动，翅膀摊开，眼睛和嘴的青光熄灭（画成暗灰蓝色，不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 6 px squares (its lowest point on y 1176) - a FOUR-LEGGED WINGED DRAGON standing low: TWO HUGE DARK PURPLE BAT WINGS, every wing bone and finger ending in a GLOWING CYAN CLAW TIP, rows of GLOWING CYAN CRYSTAL SPIKES along its back and tail, a MANE OF WHITE CRYSTAL SHARDS over its neck and chest, a DARK POINTED BEAK-LIKE JAW, TWO BIG BLUE HORNS curving back, a GLOWING CYAN MOUTH, a CYAN EYE, four legs with BLACK HOOKED TALONS, the tail curled up ending in a fan of spikes; B its HEAD shown 8x; C a 3D RENDER of this same creature's game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the two wings, the tail, the body's and the head's angle from it - never its 3D shading; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine and neck (rump to head, its last stretch the lower jaw), BROWN = the tail, PINK and CYAN = its two wings (shoulder to wing tip), ORANGE and PURPLE = its two front legs, RED and BLUE = its two hind legs, GREY BOX = where the head goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 6 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the head, the legs and the wings exactly as big as in A in EVERY pose, also when the wings rise and spread, it leaps into the air, flies or lies on its side (the picture simply grows taller, wider or shorter - never shrink the body or the head to fit). Each leg along its line (lean dragon leg, the black hooked talons at the end), bending at its joints, never stretched, never squashed, never thinner than in A; the NEAR legs (purple and blue lines) in full tone and in front, the FAR ones a step darker. Each wing along its line: big flat dark purple membranes, darker lines for the bones, a glowing cyan claw tip on every finger; the NEAR wing (cyan line) whole and in front, the FAR wing behind the body a step darker. The cyan crystal spikes and the white crystal mane stay where they are on the body, as big pointed triangles.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the dark beak-like jaw, the two blue horns, the cyan eye, the glowing mouth, the white chin spikes) - the same head in every pose, only moved and tilted with the body, never turned, never redrawn; where the pose opens the jaws, only the lower jaw swings down along the green line's last stretch with the bright cyan glow and white fangs inside; the glow goes out only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no fire, no breath, no flames, no wind, no dust, no motion lines, no glow halo outside the body), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_back: `GATHER - the head drawn back and up, the neck arched, the jaws a little open, winding up.`
- a_bite: `BITE - the head thrust forward and down, the jaws wide open biting (the cyan glow inside), the front of the body low and lunging.`
- q_rear: `INHALE - the front of the body lifting a little, the head tipped back, the jaws open, the cyan glow in the chest and mouth brightening.`
- q_breath: `BREATHE - the neck stretched straight forward, the head low facing front, the jaws open as wide as they go (bright cyan inside) - the fire itself is drawn later, NOT here.`
- e_rear: `REAR UP - the front of the body rearing up, both big wings raised high over the head, fully spread.`
- e_slam: `BEAT DOWN - both wings beaten hard down and forward to the bottom, the front paws back on the ground, the body low.`
- r_jump: `TAKE OFF - springing up into the sky off the hind legs, the wings spread and raised, all four legs tucked under it.`
- r_land: `SLAM DOWN - crashing back onto the ground, all four legs landing hard, the body pressed down as low as it goes, the wings braced out to both sides.`
- run1: `FLY 1 - both wings raised to the top, spread upward.`
- run2: `FLY 2 - the wings starting the downstroke.`
- run3: `FLY 3 - the wings half way down, stretched out level to both sides.`
- run4: `FLY 4 - the wings at the bottom of the stroke, the body lifted.`
- run5: `FLY 5 - the wings folding in from the bottom, drawn back up.`
- run6: `FLY 6 - the wings half way up.`
- run7: `FLY 7 - the wings nearly at the top.`
- run8: `FLY 8 - the wings back at the top (8 runs on into 1: the loop).`
- d_fall: `SINKING - the body sagging, the wings drooping, the head hanging down, the legs giving way.`
- d_down: `DOWN - collapsed onto its side, lying still, the wings sprawled, the glow of the eyes and mouth gone out (a dull dark grey-blue, no glow).`

## 交回

- 每个姿势一张：`outputs/elderdragon-poses/elderdragon-pose-<名字>.png`（1254 × 1254、真透明背景、每格 6 px）；原始生成图原样放进 `outputs/elderdragon-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **18 张都画完再交**，最后写 `outputs/elderdragon-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/elderdragon_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/elderdragon/codex_poses/`，**先量 Codex 实际的格子**（不一定是 6 px），读 raw，**每张按定稿的身体大小读**（翅膀张开、腾空时 Codex 容易把身体画小：codex-fit-shrinks-bodies），头对齐定稿的头（hd/idle.png）；每帧 8 倍检查（头不动、眼睛和发光的嘴还在、腿没有被压扁或拉长、飞行 8 帧翅膀真的在扇、远处的腿和翅膀暗一档）。
- 骨架包：`tools/art/pack_elderdragon_poses.py`（骨架是英雄联盟远古巨龙的骨骼（金铲铲模型同一套），按动作片段的那一帧投影；头放大 1.6 倍；飞行按 2.33 s 一整圈振翅均匀取 8 帧 (0, 291, 583, 875, 1166, 1458, 1750, 2041) ms）；这份提示词由 `tools/art/gen_elderdragon_pose_md.py` 生成。
