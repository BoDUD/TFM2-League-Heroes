# 迷失之牙 纳尔：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 纳尔的两个造型用户已经定稿：**巨型纳尔侧面**（`2_mega_design.png`，你上一轮的 SM-2）和**迷你纳尔 3/4**（`2_mini_design.png`，你上一轮的 A-2）。他的动作帧已经做好了，但普攻和技能在英雄联盟里要**举拳、站起来、砸下去、举石头、扑出去、跳起来**，手臂要动，这些姿势造型本身给不出，所以请你按骨架补画 **11 个关键姿势，每个一张图**：巨型 7 个、迷你 4 个（我再把它们接进现有的动作里）。
> - **每张图都是定稿的同一个纳尔**：样子、颜色、粗细、长短全照定稿，**格子和定稿一样大**：**巨型每格 10 px，迷你每格 20 px**，画布 **1254 × 1254**，红线是地面（**脚底 y = 1180**），网格从画布左上角对齐。
> - **体型不要变瘦变细**（上一个英雄这一步画细了要返工）：`3_mega_design_8x.png` / `3_mini_design_8x.png` 是定稿的 8 倍图，**粗细照它数**：
>   - **巨型**：躯干从肚子到背（不算蓝毛刺）约 **25 格厚**，站起来时这就是身子的**宽度**，不要画成细杆；**前臂和大拳头约 10 格粗**（他的拳头比头还大）；后腿约 **6–7 格粗**、从胯到脚底约 **18 格**；头（灰框）**30 × 36 格**。
>   - **迷你**：头连耳朵和骨头头盔（灰框）**40 × 27 格**，占身高一半多；身子约 **14 格宽**；腿约 **4 格粗**、胯到脚底约 **9 格**；胳膊约 **3 格粗**；大尾巴和定稿一样大。
> - **骨架**（每个姿势一张 `*_skeleton.png`）：绿线 = 脊柱和尾巴，**红线 = 近侧的腿（在前面、颜色亮）**，**蓝线 = 远侧的腿（在后面、稍暗）**，**橙线 = 近侧的手臂**，**紫线 = 远侧的手臂（在后面、稍暗）**，**金色 = 迷你的骨头回力标 / 巨型举着的大石头（框）**，**灰框 = 头的位置**。`0_mega_design_skeleton.png` / `0_mini_design_skeleton.png` 是同样的骨架画在定稿上，看每条线对应身体的哪一部分。**四肢、尾巴的长短和定稿一样**（骨架就是按定稿量的），关节处弯折，不要把直的腿整块转个方向贴上去，不要拉长或压短。
> - **手臂永远不要画在脸上**：举起来的手臂从头的**后面**（画面左边、头的后脑勺那一侧）上去，往前伸的拳头从头的**下面**出来；骨架就是这样摆的，照着画。**远侧的手臂和远侧的后腿和近侧的一样长、一样粗**（定稿里它们被头和身子挡住了一截，看起来短）。
> - **头一格一格照 `1_mega_head.png` / `1_mini_head.png` 画在灰框里**，每个姿势都是这一个头，只跟着身体移动，**不要转头、不要重新设计**（巨型：黄橙眼睛、獠牙、满嘴尖牙、额头上的小头骨；迷你：两只大圆眼睛带白高光、大耳朵、骨头头盔）。
> - 每个姿势附一张英雄联盟原版的那一帧（`*_league.png`），**动作参考它，以骨架为准**（有几张骨架故意和原版不同，比如巨型举石是举过头顶），长相照定稿。

## 11 个姿势

| 图 | 文件 | 形态 | 姿势 |
|---|---|---|---|
| 4 | `gnar-pose-m_crouch.png` | 巨型 | **蓄力**：整个身子往下压、头缩回来贴近地面、两只大拳头收在胸前撑地、后腿弯着准备蹬 |
| 5 | `gnar-pose-m_swing.png` | 巨型 | **挥拳**：上半身抬起一半、近侧的大拳头**从头的后面**高高举起准备往前砸、远侧的拳头**从头下面**往前伸 |
| 6 | `gnar-pose-m_rear.png` | 巨型 | **直立**：只用两条后腿站起来、身子竖直、头在胸口前面、两只大拳头**从头的后面**高高举过头顶、尾巴拖在地上 |
| 7 | `gnar-pose-m_slam.png` | 巨型 | **下砸**：整个身子往前压平、两只大拳头伸直一起砸在**头下面**的地上、后腿离地往后蹬、尾巴翘起 |
| 8 | `gnar-pose-m_lunge.png` | 巨型 | **前扑横扫**：身子往前上方伸长、近侧的拳头**从头顶上方**往前挥出去、远侧的拳头**从头下面**往前伸、后腿蹬地、尾巴往后甩 |
| 9 | `gnar-pose-m_leap.png` | 巨型 | **跳在半空**：整个身子离地很高（脚离地约 20 格）、后腿收在肚子下面、两只拳头**从头下面**往前下方准备砸地 |
| 10 | `gnar-pose-m_lift.png` | 巨型 | **举石**：两条后腿站直、头在胸口前面、两只大拳头**从头的后面**举上去，一起把一块**灰色大石头**（金框的位置）举过头顶 |
| 11 | `gnar-pose-a_windup.png` | 迷你 | **蓄力**：拿回力标的近侧那只手往后拉到身体后面（画面左边、**头的下面**），回力标往后上方翘在左耳旁边，身子微微后仰 |
| 12 | `gnar-pose-a_throw.png` | 迷你 | **扔出**：近侧的手往前（画面右边）甩直、**手里空了**、身子往前倾、后腿蹬地 |
| 13 | `gnar-pose-a_hop.png` | 迷你 | **跳起**：整个人离地（脚离地约 9 格）、膝盖收到肚子前、两只手**往两边张开**、尾巴翘起、回力标还在手里 |
| 14 | `gnar-pose-a_crouch.png` | 迷你 | **落地蹲下**：膝盖弯着蹲低（比站着低 3 格）、两只手张开撑着平衡、回力标还在手里 |

## 提示词（每个姿势一次）

每次上传 4 张：这个形态的定稿 8 倍图（`3_mega_design_8x.png` 或 `3_mini_design_8x.png`）、这个形态的头（`1_mega_head.png` 或 `1_mini_head.png`）、这个姿势的 `*_skeleton.png`、这个姿势的 `*_league.png`；有余量再加 `0_*_design_skeleton.png`。**用 image_gen 画。** 巨型用第一段，迷你用第二段，最后一行换成下面那个姿势的英文。

**巨型（第 4–10 张）：**

```text
Attached images: A the APPROVED pixel-art character shown 8x (every 8x8 block is one square), side-on facing right: a huge hunched beast - deep crimson-red fur with rows of spiky electric-blue fur crests along the back, head and arms, two big curved ivory tusks, a wide mouth full of ivory fangs, yellow-orange eyes, a small bone skull on the brow, two HUGE clawed fists with dark grey-violet knuckles and ivory claws, thick hind legs, a spiky blue-and-red tail; B its HEAD shown 8x (30 squares wide, 36 tall); C a SKELETON on a 1254x1254 canvas with a 10 px grid: green = spine and tail, RED = the NEAR hind leg (in front, full tone), BLUE = the FAR hind leg (behind, a step darker), ORANGE = the NEAR arm with its fist, PURPLE = the FAR arm with its fist (behind, darker), a GOLD box (only in the lifting pose) = a big grey boulder held overhead, GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose (copy the idea of the POSE from it, never its 3D look; where it differs, follow the skeleton C); E (if attached) the same skeleton drawn over the approved design, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 10 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet or fists that touch the ground on y 1180.
Lay the body along the skeleton, keeping image A's BUILD: the torso about 25 squares thick from belly to back (not counting the crests) - when he stands up that thickness is the body's WIDTH, never a thin stalk; each arm along its line, the forearm and the huge fist about 10 squares thick (bigger than the head); each hind leg along its line, about 6-7 squares thick and about 18 squares from hip to sole; the tail along its green line with its blue crests. Never stretch or shorten a limb, never paste a straight limb turned as one block, never make him slimmer.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (30 x 36 squares: the yellow-orange eyes, the blue brow crests, the tusks, the fangs, the skull on the brow) - the same head in every pose, only moved, never turned, never redrawn.
The same colours as image A: the crimson fur in its 3-4 reds with lit edges, the crests in its electric blues with cyan edges, the ivory tusks and claws, the grey-violet knuckles; one continuous 1-square near-black outline; the near parts in full tone, the far parts a step darker; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line below>
```

**迷你（第 11–14 张）：**

```text
Attached images: A the APPROVED pixel-art character shown 8x (every 8x8 block is one square), 3/4 view facing right: a tiny orange furry chibi cub - huge pointed ears (orange outside, violet-pink inside, blue tips), big round dark eyes with white highlights, a pink nose, a bone skull cap on his head, a dark brown fur wrap and loincloth, a big bushy orange tail with a blue tip, small clawed feet, a big ivory bone boomerang wrapped with brown leather in his near hand; B its HEAD shown 8x (40 squares wide with the ears, 27 tall); C a SKELETON on a 1254x1254 canvas with a 20 px grid: green = spine and tail, RED = the NEAR leg (in front, full tone), BLUE = the FAR leg (behind, a step darker), ORANGE = the NEAR arm, PURPLE = the FAR arm (behind, darker), GOLD = the boomerang (where it is drawn he holds it; where there is no gold line his hand is EMPTY), GREY BOX = where the head goes, the red horizontal line = the ground; D the original character in this pose (copy the idea of the POSE from it, never its 3D look; where it differs, follow the skeleton C); E (if attached) the same skeleton drawn over the approved design.
Draw with the image generator ONE clean pixel-art picture of the character of image A in the POSE of the skeleton C: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 20 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; feet that touch the ground on y 1180.
Lay the body along the skeleton, keeping image A's BUILD: the head with its ears and skull cap 40 x 27 squares, more than half of his height; the body about 14 squares wide; each leg along its line, about 4 squares thick and about 9 squares from hip to sole; each arm along its line, about 3 squares thick; the bushy tail along its green line as big as in image A; the boomerang along the gold line as long as in image A. Never stretch or shorten a limb, never make him slimmer.
THE HEAD: copy image B SQUARE FOR SQUARE into the grey box (the big round dark eyes with their white highlights, the pink nose, the ears, the skull cap) - the same head in every pose, only moved, never turned, never redrawn.
The same colours as image A: the orange fur in its 3-4 oranges with yellow lit edges, violet-pink ears with blue tips, the ivory bone, the dark brown wrap; one continuous 1-square near-black outline; the near parts in full tone, the far parts a step darker; no stray single squares, no dithering, no gradients, no glow, no blur, no anti-aliasing.
No effects, no background, no ground, no shadow, no text, no grid lines, no skeleton lines.
THE POSE: <one line below>
```

每个姿势的最后一行（英文）：

- m_crouch: `CROUCH - the whole body pressed low, the head pulled back near the ground, both huge fists drawn in under the chest on the ground (the far fist showing under the head), the hind legs bent ready to spring.`
- m_swing: `SWING - the upper body half raised, the NEAR fist lifted high BEHIND the head (at the image left of it) ready to smash forward, the far fist reaching forward from UNDER the head, standing on the hind legs.`
- m_rear: `REAR - standing upright on the two hind legs only, the thick body vertical, the head in front of the chest, both huge fists raised high over the head with the arms going up BEHIND the head (never over the face), the tail lying on the ground behind.`
- m_slam: `SLAM - the whole body flattened forward, both huge fists smashing the ground UNDER the head with the arms straight, the hind legs kicked up off the ground behind, the tail raised.`
- m_lunge: `LUNGE - the body stretched forward and up, the NEAR fist swinging forward OVER the top of the head (never across the face), the far fist reaching forward from UNDER the head, the hind legs pushing off, the tail flung back.`
- m_leap: `LEAP - the whole body high in the air (the feet about 20 squares above the ground), the hind legs tucked under the belly, both fists reaching forward and down from UNDER the head to smash the ground.`
- m_lift: `LIFT - standing upright on the two hind legs, the head in front of the chest, both huge fists holding a big GREY BOULDER (in the gold box) over the head, the arms going up BEHIND the head (never over the face), ready to throw it forward.`
- a_windup: `WINDUP - the NEAR hand holding the boomerang pulled back behind the body (to the image left, BELOW the head), the boomerang sticking up and back beside the left ear, the body leaning back a little.`
- a_throw: `THROW - the NEAR arm flung straight forward to the image right, the hand EMPTY (the boomerang is gone), the body leaning forward, the back leg pushing off.`
- a_hop: `HOP - the whole body in the air (the feet about 9 squares above the ground), the knees tucked up in front of the belly, both arms spread out to the sides, the tail raised, the boomerang in the near hand.`
- a_crouch: `CROUCH - landing: the knees bent, the body 3 squares lower than standing, both arms spread out for balance, the boomerang still in the near hand.`

## 交回前请检查

- **11 张都是 image_gen 画的**；1254 × 1254；真透明背景，**alpha 只有 0 / 255**；**巨型每格 10 px、迷你每格 20 px**（和定稿一样，数一数腿的粗细：和定稿一样宽）。
- **手臂没有画在脸上**（举起的手臂在头的后面，伸出的拳头在头的下面）。
- 每张都是定稿的同一个纳尔：**同一个头**、同样粗的四肢和身子、同样长的尾巴；姿势沿着骨架；着地的脚在 y 1180。巨型举石的石头是灰色的大石头；迷你扔出时手里没有回力标。
- 没有特效、没有骨架线、没有网格线。

## 交付（`outputs/gnar-poses/`）

- `gnar-pose-<名字>.png` 共 11 张（名字见上表）；原始生成图原样放 `outputs/gnar-poses/raw/`；`generation-prompts.txt`；**最后**写 `HANDOFF.md`，再打包成 `outputs/gnar_poses_done.zip`。中间不要停，11 张都画完再交。

## 附图（压缩包 `gnar_pose_pack.zip` 里）

请把压缩包解压到一个**新的文件夹**，只用里面的图。

| 文件 | 内容 |
|---|---|
| `0_mega_design_skeleton.png` / `0_mini_design_skeleton.png` | 定稿上画着它自己的骨架（每条线对应哪一部分） |
| `1_mega_head.png` / `1_mini_head.png` | 定稿的头（8 倍）：每个姿势都照它逐格画 |
| `2_mega_design.png` / `2_mini_design.png` | 定稿放在画布网格上（巨型每格 10 px、迷你每格 20 px，脚底 y 1180） |
| `3_mega_design_8x.png` / `3_mini_design_8x.png` | 定稿的 8 倍图：粗细照它数 |
| `4_m_crouch_*` … `14_a_crouch_*` | 每个姿势的骨架（`_skeleton`）和英雄联盟原版那一帧（`_league`） |

## Claude 收到后（给 Claude 看）

- 量格子（巨型约 10 px、迷你约 20 px），按格读回（regrid），颜色对到定稿的调色板；**先在 8 倍下量四肢、尾巴、躯干的长短粗细，和定稿比**（codex-legs-need-skeletons、科加斯第 2 轮的教训），头换成定稿的头；再接进 rig_gnar.py 的动作里（巨型普攻 = 挥拳 → 下砸，投掷顽石 = 举石，痛殴 = 直立 → 下砸，呐啊！ = 前扑横扫，猛踏 = 蓄力 → 跳 → 下砸；迷你普攻和 Q = 蓄力 → 扔出，E = 蹲 → 跳 → 蹲；死亡不动），逐帧自查后才发合成 GIF（英雄联盟在左、我们在右）。
