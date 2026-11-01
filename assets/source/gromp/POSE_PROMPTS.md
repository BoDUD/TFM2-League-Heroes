# 魔沼蛙：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 魔沼蛙的造型用户已经定稿。`0_design.png` 是你第 0 步交的**第一版 A**（raw/gromp-A-initial.png），按它自己 12 px 的格子读回、1:1 定稿，这里放大成每格 7 px。它的样子：
>   - 3/4 朝右、**蹲着的大胖蛤蟆**；
>   - 前面（右下）一个**又圆又鼓的橄榄褐大肚子**，上面有一块块甲片褶皱和深色圆斑；
>   - **橙色的扁头**压在肚子上方：隆起的眉骨、**发黄绿色光的眼睛**、嘴角两根**淡黄绿色獠牙**往上翘；
>   - 背和四肢是**深紫色的疙瘩皮**，四条短粗的蛙腿，前脚是张开的蛙爪；
>   - 背上一丛**紫色和蓝色的大蘑菇**（伞盖上有浅色圆点），头后面一个**蓝蘑菇**。
>   每个姿势都照它。
> - 请你画 **18 个姿势**（8 个动作 + 8 帧蛙跳 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只蛤蟆**：样子、颜色、大小全照 `0_design.png`。**格子和它一样大：每格 7 px**，画布 **1254 × 1254**，网格从画布左上角对齐。红线是地面，**最低点 y = 1176**。
> - **身体大小每张都和定稿一样**：仰起身子、蛙跳伸长、翻倒、仰躺的时候，画面会变高、变宽或变矮，**但身子、头、腿不能因此画小**。按参考图的大小画，超出去就让它超出去，画布够大。**头每张都和定稿一样大**。
> - **只有两张肚子比定稿大**：`q_puff`（鼓起来）和 `r_belch`（鼓到最大，比 q_puff 还大）；`r_rear` 开始鼓一点。其他姿势的肚子和定稿一样大。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲 / 英雄联盟里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上，高度和位置都一样。死亡的两张是我把待机姿势往后翻倒做的（模型自己的死亡动作是直接沉进地里）。
>   - 姿势、四条腿、身体和头的角度**照参考图**。
>   - 长相和画法**照定稿**：像素格、描边、平涂，不要 3D 光影。
>   - 颜色分区（橄榄褐肚子、橙色扁头、深紫疙瘩皮、紫蓝蘑菇、淡黄獠牙）、头的大小**照定稿**。模型的头比定稿小，**以定稿为准**。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：
>   - 绿线 = 脊柱（屁股到肩膀），**棕线 = 大肚子**（喉囊的骨头）。
>   - **橙线 = 头**（到上嘴唇），**黄线 = 下巴**。
>   - **红线 / 蓝线 = 两条前腿**，**粉线 / 青线 = 两条后腿**。
>   - **灰框 = 脸（眼睛、嘴、獠牙）的位置**。
>   - **近处（离我们近）的始终是蓝线前腿、青线后腿**。蛙跳时也是这两条在近处。
>   - `0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，用来看清哪条线是哪个部位。
> - **头照 `1_head.png` 一格一格地画**（定稿的头，放大 8 倍）。每个姿势都是这个头，只跟着骨架移动和倾斜，**不要重新设计**。
>   - **张嘴的姿势**（a_spit、q_belch、e_spit、r_belch、d_fall）只把下巴按黄线往下打开，嘴里画成**深粉紫色**，獠牙还在嘴角；上半个头（眉骨、眼睛）不变。**舌头都不伸出来**（参考图里伸出来的舌头不要画）。
>   - 只有 `d_down` 的眼睛熄灭（暗灰色，不发光）。
> - **腿**：一直是定稿那四条深紫色的短粗蛙腿和张开的蛙爪，**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细。**近处的腿颜色正常、画在上面，远处的暗一档**。
> - **背上的蘑菇**跟着身子走，大小、颜色、位置（相对身子）和定稿一样；仰躺时压在地上那一侧。
> - **蛙跳 8 帧（run1–run8）是一整跳**：蹲 → 蹬地 → 腾空伸长 → 落地 → 蹲回去。身子、头、蘑菇都是同一个，**后腿按骨架蹬直再收回**，**一定要看得出是在跳**。
> - **死亡（d_fall、d_down）**：d_fall 往后翻倒、肚子朝上前方；d_down 肚皮朝天仰躺、四条腿朝上；身子、头、蘑菇的大小不变。

## 18 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `gromp-pose-a_back.png` | spit@133 | 普攻「毒涎吐射」起手：头往后一收，肚子吸气鼓起一点 |
| 3 | `gromp-pose-a_spit.png` | spit@266 | 吐出：头往前上方一探，嘴张开吐出一口（口水不画，只画张开的嘴） |
| 4 | `gromp-pose-q_puff.png` | puff@650 | 技能1「打嗝泡泡」起手：肚子鼓到很大，身子往后坐一点，嘴闭着 |
| 5 | `gromp-pose-q_belch.png` | roar@380 | 打嗝：仰起身子，嘴张到最大往前打一个嗝（舌头不伸出来，泡泡不画） |
| 6 | `gromp-pose-e_back.png` | attack@228 | 技能2「黏液沼泽」起手：身子往后缩、压低，头收回 |
| 7 | `gromp-pose-e_spit.png` | attack@380 | 往地上吐黏液：身子往前一扑，头往前下方伸，嘴张开（舌头不伸出来，黏液不画） |
| 8 | `gromp-pose-r_rear.png` | roar@228 | 大招「毒沼大嗝」起手：身子高高仰起，肚子开始鼓起来 |
| 9 | `gromp-pose-r_belch.png` | roar@456 | 大嗝：头高高仰起、嘴张到最大，肚子鼓到最大（比 q_puff 还大），往前喷出一大口（毒雾不画） |
| 10 | `gromp-pose-run1.png` | run@0 | 蛙跳 1/8：蹲着，准备起跳 |
| 11 | `gromp-pose-run2.png` | run@66 | 蛙跳 2/8：后腿开始蹬，身子抬起来 |
| 12 | `gromp-pose-run3.png` | run@133 | 蛙跳 3/8：蹬离地面，前爪伸向前方 |
| 13 | `gromp-pose-run4.png` | run@200 | 蛙跳 4/8：腾空，整个身子往前伸长，后腿在后面蹬直 |
| 14 | `gromp-pose-run5.png` | run@266 | 蛙跳 5/8：腾空最远，后腿拖在后面 |
| 15 | `gromp-pose-run6.png` | run@333 | 蛙跳 6/8：往下落，前爪先着地 |
| 16 | `gromp-pose-run7.png` | run@400 | 蛙跳 7/8：落地，身子压扁一点、后腿收回 |
| 17 | `gromp-pose-run8.png` | run@466 | 蛙跳 8/8：重新蹲好（8 接回 1，循环） |
| 18 | `gromp-pose-d_fall.png` | idle@0（往后翻 45°） | 被打倒：往后翻倒，前半身翘起，四条腿离地乱蹬，嘴张开 |
| 19 | `gromp-pose-d_down.png` | idle@0（往后翻 160°） | 倒地：肚皮朝天仰躺在地上，四条腿朝上，眼睛熄灭（画成暗灰色，不发光） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（头）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 7 px squares (its lowest point on y 1176) - a HUGE SQUAT FAT TOAD crouching: a GIANT ROUND OLIVE-BROWN BELLY at the front (lower right) with plate-like folds and dark spots, a FLAT ORANGE HEAD resting on top of it with a ridged brow, GLOWING YELLOW-GREEN EYES and two PALE YELLOW-GREEN TUSKS curving up at the corners of the mouth, DARK PURPLE WARTY SKIN on the back and the four short thick frog legs with splayed frog hands, a cluster of BIG PURPLE AND BLUE MUSHROOMS with light spots on its back and one blue mushroom behind the head; B its HEAD shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the body's and the head's angles from it - never its 3D shading, never its small head, never its tongue; keep A's colours and A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to shoulders), BROWN = the belly, ORANGE = the head (to the upper lip), YELLOW = the lower jaw, RED and BLUE = the two front legs, PINK and CYAN = the two hind legs, GREY BOX = where the face goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 7 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; its lowest point on y 1176.
THE SAME BULK AS IMAGE A: the body, the head and the legs exactly as big as in A in EVERY pose, also when it rears up, hops, tips over or lies on its back (the picture simply grows taller, wider or shorter - never shrink the body or the head to fit); the belly the same size as in A unless the pose line says it swells. Each leg along its line (a short thick dark purple frog leg, the splayed frog hand or foot at the end), bending at its joints, never stretched, never squashed, never thinner than in A; the NEAR legs (blue and cyan lines) in full tone and in front, the FAR ones a step darker. The mushrooms stay on its back, the same size and colours as in A.
THE HEAD: copy image B SQUARE FOR SQUARE onto the head line inside the grey box - the same head in every pose, only moved and tilted with it, never redrawn; where the pose opens the mouth, only the lower jaw swings down along the yellow line (dark pinkish purple inside, the tusks still at the corners); the TONGUE NEVER sticks out; the eyes go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no spit, no bubbles, no slime, no poison cloud, no dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_back: `GATHER - the head drawn back a little, the belly drawing breath.`
- a_spit: `SPIT - the head thrust up and forward, the mouth open (do NOT draw the spit itself).`
- q_puff: `SWELL - the belly blown up big and round, the body sitting back a little, the mouth shut.`
- q_belch: `BELCH - reared up, the mouth open as wide as it goes, belching forward (the tongue NOT out, do NOT draw the bubble).`
- e_back: `DRAW BACK - the body pulled back and low, the head pulled in.`
- e_spit: `SPIT DOWN - lunging forward, the head reaching forward and down, the mouth open (the tongue NOT out, do NOT draw the slime).`
- r_rear: `REAR UP - the body rearing up high, the belly starting to swell.`
- r_belch: `BIG BELCH - the head thrown up high, the mouth open as wide as it goes, the belly at its BIGGEST (even bigger than in q_puff), blasting forward (do NOT draw the poison cloud).`
- run1: `HOP 1 of 8 - crouched, about to spring.`
- run2: `HOP 2 of 8 - the hind legs starting to push, the body rising.`
- run3: `HOP 3 of 8 - pushing off the ground, the front hands reaching forward.`
- run4: `HOP 4 of 8 - in the air, the whole body stretched forward, the hind legs kicked out straight behind.`
- run5: `HOP 5 of 8 - at the farthest, the hind legs trailing behind.`
- run6: `HOP 6 of 8 - coming down, the front hands touching first.`
- run7: `HOP 7 of 8 - landing, the body squashed a little, the hind legs drawn in.`
- run8: `HOP 8 of 8 - crouched again (8 runs on into 1: the loop).`
- d_fall: `KNOCKED OVER - tipping over backwards, the front half up in the air, all four legs off the ground kicking, the mouth open.`
- d_down: `DOWN - lying on its back, the belly up, all four legs in the air, the eyes gone dark (a dull dark grey, no glow).`

## 交回

- 每个姿势一张：`outputs/gromp-poses/gromp-pose-<名字>.png`（1254 × 1254、真透明背景、每格 7 px）。
- 原始生成图原样放进 `outputs/gromp-poses/raw/`。
- `generation-prompts.txt` 写明实际用的提示词。
- **不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **18 张都画完再交**。最后写 `outputs/gromp-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/gromp_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/gromp/codex_poses/`，**先量 Codex 实际的格子**（不一定是 7 px），读 raw。
- **每张按定稿的身体大小读**：仰起、腾空时 Codex 容易把身体画小（codex-fit-shrinks-bodies）。头对齐定稿的头（hd/idle.png）。
- 每帧放大 8 倍检查：
  - 头是定稿的头（眉骨、黄绿眼睛、獠牙），没有伸舌头；
  - 肚子只在 q_puff / r_rear / r_belch 变大；
  - 腿没有被压扁或拉长；
  - 蛙跳 8 帧真的是一跳；
  - 远处的腿暗一档。
- 骨架包：`tools/art/pack_gromp_poses.py`。骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影（金铲铲的 7 段 + 峡谷魔沼蛙的 spit / roar）；死亡两张是待机往后翻 45° / 160°；蛙跳按 0.53 s 一整跳均匀取 8 帧 (0, 66, 133, 200, 266, 333, 400, 466) ms。这份提示词由 `tools/art/gen_gromp_pose_md.py` 生成。
