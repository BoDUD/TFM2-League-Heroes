# 暗影狼：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 暗影狼的造型用户已经定稿。`0_design.png` 是你第 0 步交的 A（murkwolf-A.png），按它自己 9 px 的格子读回、1:1 定稿，这里放大成每格 10 px。它的样子：
>   - 3/4 朝右、**四条腿压低身子的双头狼**，灰蓝色的毛；
>   - 背上一大片**紫色鬃毛**，鬃毛里一排**墨绿尖刺**；
>   - **蓬松的大尾巴**往左上方翘，尾尖发黑；
>   - **两个一样大的狼头**并排：粉色内耳的尖耳朵、**发光的青色眼睛**、张开的**粉色大嘴和黄色尖牙**、**白色腮毛**；
>   - 四只爪子是**黑色弯钩爪**。
>   每个姿势都照它。
> - 请你画 **19 个姿势**（9 个动作 + 8 帧跑步 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只狼**：样子、颜色、大小全照 `0_design.png`。**格子和它一样大：每格 10 px**，画布 **1254 × 1254**，网格从画布左上角对齐。红线是地面，**最低点 y = 1176**。
> - **身体大小每张都和定稿一样**：起跳竖起、仰头嚎叫、被掀翻、侧躺的时候，画面会变高、变宽或变矮，**但身子、头、腿不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**两个头每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都一样，头已经放大了一些。
>   - 姿势、四条腿、尾巴、身体和两个头的角度**照参考图**。
>   - 长相和画法**照定稿**：像素格、描边、平涂，不要 3D 光影。
>   - 毛色分区（灰蓝身子、紫色鬃毛和墨绿尖刺、白色腮毛）、头的大小**照定稿**。
>   - 嚎叫（e_gather、e_howl）和号令（r_growl、r_bark）这几张，两个脖子是我按骨架抬起或压低的，**以骨架的橙线 / 黄线为准**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 脊柱（屁股到肩膀），**棕线 = 尾巴**。
>   - **橙线 / 黄线 = 两条脖子和两个头**（最后一段是下巴）。
>   - **红线 / 蓝线 = 两条前腿**，**粉线 / 青线 = 两条后腿**。
>   - **灰框 = 两个头的位置**。
>   - **近处（离我们近）的始终是黄线头、蓝线前腿、青线后腿**。跑步时腿前后交错，也还是这几条在近处。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **头照 `1_head.png` 一格一格地画**（定稿的两个头，放大 8 倍）。近处的头在前、在下，远处的头在后、略高。每个姿势都是这两个头，只跟着脖子移动和倾斜，**不要重新设计**。
>   - **张嘴的姿势**（a_bite、q_leap、e_howl、r_bark、d_fall）只把下巴按橙线 / 黄线的最后一段往下打开，嘴里粉色、黄色尖牙，上半个头不变。
>   - 只有 `d_down` 的眼睛熄灭（暗灰色，不发光）。
> - **腿**：一直是定稿那四条灰蓝色的腿和黑色弯钩爪，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细。**近处的腿颜色正常、画在上面，远处的暗一档**。
> - **跑步 8 帧（run1–run8）是一整圈**：每帧的身子、头、鬃毛都是同一个，只有四条腿按骨架换位置，身子跟着上下一点点。**一定要看得出腿在交替迈步**。
> - **死亡（d_fall、d_down）**：d_down 侧躺在地上；身子、头、鬃毛的大小不变，只是躺倒。

## 19 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `murkwolf-pose-a_back.png` | attack@333 | 普攻「双头撕咬」起手：身子往后一缩、压低，两个头收回、准备扑咬 |
| 3 | `murkwolf-pose-a_bite.png` | attack@416 | 咬下：往前一扑，两个头一起往前上方探出，两张嘴张到最大（粉色嘴里、黄色尖牙） |
| 4 | `murkwolf-pose-q_crouch.png` | attack2@167 | 技能1「撕裂之爪」起手：后腿蹲下蓄力，前身压低，准备起跳 |
| 5 | `murkwolf-pose-q_leap.png` | attack2@333 | 起跳扑向目标：整只狼用后腿蹬起、身子竖起来，两只前爪张开举高，两张嘴张开 |
| 6 | `murkwolf-pose-q_rend.png` | attack2@500 | 落下撕扯：整个身子扑落压低，两只前爪往前下方狠狠抓下去，两个头低着咬 |
| 7 | `murkwolf-pose-e_gather.png` | idle@0（脖子 +15°） | 技能2「狂战士之嚎」起手：两个头低下来吸气，身子绷紧 |
| 8 | `murkwolf-pose-e_howl.png` | idle@0（脖子 -55°） | 嚎叫：两个头一起高高仰起、嘴朝天张开长嚎，前腿撑住 |
| 9 | `murkwolf-pose-r_growl.png` | crouch@500（脖子 +20°） | 大招「狼群攻击」起手：身子伏低，两个头压低龇牙低吼 |
| 10 | `murkwolf-pose-r_bark.png` | attack@834（脖子 -25°） | 号令狼群：站高、尾巴竖起，两个头朝前上方张嘴大吼 |
| 11 | `murkwolf-pose-run1.png` | run@0 | 跑 1/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 12 | `murkwolf-pose-run2.png` | run@100 | 跑 2/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 13 | `murkwolf-pose-run3.png` | run@200 | 跑 3/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 14 | `murkwolf-pose-run4.png` | run@300 | 跑 4/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 15 | `murkwolf-pose-run5.png` | run@400 | 跑 5/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 16 | `murkwolf-pose-run6.png` | run@500 | 跑 6/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 17 | `murkwolf-pose-run7.png` | run@600 | 跑 7/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点 |
| 18 | `murkwolf-pose-run8.png` | run@700 | 跑 8/8：四条腿照骨架的位置（红 / 蓝 = 前腿，粉 / 青 = 后腿），身子随步子上下一点点（8 接回 1，循环） |
| 19 | `murkwolf-pose-d_fall.png` | death@150 | 被打倒：被掀翻，身子扭着往后仰，四条腿离地乱蹬，嘴张开 |
| 20 | `murkwolf-pose-d_down.png` | death@1333 | 倒地：侧躺在地上不动，眼睛熄灭（画成暗灰色，不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 10 px squares (its lowest point on y 1176) - a LOW-CROUCHED FOUR-LEGGED TWO-HEADED WOLF: SLATE-BLUE FUR with a lighter belly, a big DARK PURPLE MANE down its back with a ROW OF DARK GREEN-BLACK THORN SPIKES in it, a THICK BUSHY TAIL raised up and back to the left with a near-black tip, and TWO EQUAL WOLF HEADS side by side at the front (the near one lower and in front, the far one behind and a little higher), each with upright pointed ears with pink insides, GLOWING CYAN EYES, an open PINK SNARLING MOUTH with YELLOW FANGS and a fluffy WHITE CHEEK RUFF; four strong legs with HOOKED BLACK CLAWS; B its TWO HEADS shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the tail, the body's and the heads' angles from it - never its 3D shading; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to shoulders), BROWN = the tail, ORANGE and YELLOW = the two necks and heads (the last stretch of each is the lower jaw), RED and BLUE = the two front legs, PINK and CYAN = the two hind legs, GREY BOX = where the heads go, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the two heads and the legs exactly as big as in A in EVERY pose, also when it rears up, leaps, throws its heads back or lies on its side (the picture simply grows taller, wider or shorter - never shrink the body or the heads to fit). Each leg along its line (a strong slate-blue wolf leg, the hooked black claws at the end), bending at its joints, never stretched, never squashed, never thinner than in A; the NEAR legs (blue and cyan lines) in full tone and in front, the FAR ones a step darker. The purple mane and its green-black thorns stay along the back, the bushy tail follows the brown line.
THE HEADS: copy image B SQUARE FOR SQUARE onto the two neck lines inside the grey box (the near head on the YELLOW line, the far head on the ORANGE line) - the same two heads in every pose, only moved and tilted with their necks, never redrawn, never merged into one, never a third head; where the pose opens the mouths, only the lower jaw swings down along its line's last stretch (pink inside, yellow fangs); the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no claw slashes, no wolf pups, no sound rings, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_back: `GATHER - the body drawn back and low, both heads pulled in, ready to snap.`
- a_bite: `BITE - lunging forward, both heads thrust forward and up, both jaws open as wide as they go (pink mouths, yellow fangs).`
- q_crouch: `CROUCH - the hind legs coiled, the chest low, about to spring.`
- q_leap: `LEAP - springing up off the hind legs, the body reared upright, both front paws raised with the claws spread, both mouths open.`
- q_rend: `REND - crashing down low, both front paws raking forward and down hard, both heads low and biting.`
- e_gather: `BREATHE IN - both heads lowered, the body tense.`
- e_howl: `HOWL - both heads thrown back, muzzles pointing at the sky, mouths open howling, the front legs braced.`
- r_growl: `GROWL - crouched low, both heads down, baring the fangs.`
- r_bark: `COMMAND - standing tall, the tail raised high, both heads up and forward, mouths open barking.`
- run1: `RUN 1 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run2: `RUN 2 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run3: `RUN 3 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run4: `RUN 4 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run5: `RUN 5 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run6: `RUN 6 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run7: `RUN 7 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride.`
- run8: `RUN 8 of 8 - each of the four legs exactly where its line in the skeleton puts it (red / blue the front legs, pink / cyan the hind legs), the body bobbing slightly with the stride (8 runs on into 1: the loop).`
- d_fall: `THROWN - flipped up and twisting backwards, all four legs kicking off the ground, the mouths open.`
- d_down: `DOWN - lying still on its side, the eyes gone dark (a dull dark grey, no glow).`

## 交回

- 每个姿势一张：`outputs/murkwolf-poses/murkwolf-pose-<名字>.png`（1254 × 1254、真透明背景、每格 10 px）。
- 原始生成图原样放进 `outputs/murkwolf-poses/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **19 张都画完再交**。最后写 `outputs/murkwolf-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/murkwolf_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/murkwolf/codex_poses/`，**先量 Codex 实际的格子**（不一定是 10 px），读 raw。
- **每张按定稿的身体大小读**：竖起、腾空时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。两个头对齐定稿的头（hd/idle.png）。
- 每帧放大 8 倍检查：
  - 还是两个头，没有合成一个；
  - 青色眼睛还在；
  - 腿没有被压扁或拉长；
  - 跑步 8 帧的腿真的在交替；
  - 远处的腿暗一档。
- 骨架包：`tools/art/pack_murkwolf_poses.py`。骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；两个头放大 1.3 倍；嚎叫和号令的脖子按 lift 转；跑步按 0.8 s 一整圈均匀取 8 帧 (0, 100, 200, 300, 400, 500, 600, 700) ms。这份提示词由 `tools/art/gen_murkwolf_pose_md.py` 生成。
