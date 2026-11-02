# 绯红树怪：动作姿势（给 Codex 的提示词）

> **这一轮必须用画图模型（image_gen）画，不要用 Python 脚本逐格写。**
> - 绯红树怪的造型用户已经定稿（`0_design.png` 是你第 0 步画的 A 的第一稿，按它自己 8 px 的格子读回，原样定稿（30 像素高，PPU 2.33），这里每格 8 px：3/4 朝右，**四脚着地蹲着的矮胖小树皮兽**；**深紫褐的树皮身子**，**前腿外面的暖褐木头甲片和青苔**，**深紫黑的尖爪**；背上**一排浅绿色的高尖叶**、脖子一圈深绿叶；脸是**圆圆的木头面具：左边一只发光的大眼睛（黄色亮芯），右边一个发光的 G 形螺旋纹，下面一排尖牙**）。每个姿势都照它。
> - 请你画 **13 个姿势**（7 个动作 + 4 帧蹦跳着跑 + 2 帧死亡），**每个一张图**。待机、挨打我从定稿本身来做，不用画。
> - **每张都是同一只绯红树怪**：样子、颜色、大小全照 `0_design.png`，**格子和它一样大：每格 8 px**，画布 **1254 × 1254**，红线是地面（**站在地上的姿势最低点 y = 1176**），网格从画布左上角对齐。
> - **身体大小每张都和定稿一样**：站起来、蹦到空中、翻倒、躺下的时候，画面会变高、变宽或变矮，**但身子、面具、腿、叶子不能因此画小**（按参考图的大小画，超出去就让它超出去，画布够大）。**面具每张都和定稿一样大**。
> - **参考图（每个姿势一张 `*_ref.png`）是它在金铲铲里自己的动作**：同一个 3D 模型、同一段动画里的那一帧，摆在同一张画布、同一个格子上、同样的高度和位置，面具已经放大了一些——**姿势、四条腿、身体和面具的角度、叶子鬃毛的方向照它，长相和画法照定稿**（像素格、描边、平涂，不要 3D 光影）。模型比定稿瘦，**身子的胖瘦、木头甲片、叶子的大小照定稿**。
> - **蹦在空中的姿势**（a_fling、run2、run3、e_pop）参考图里离地多高就画多高，**脚不要落到红线上**；**钻地的 e_dig 红线以下什么都不画**（下半身在地里）。
> - **骨架（每个姿势一张 `*_skeleton.png`，和参考图完全重合）**：绿线 = 脊柱（屁股到头），**粉线 / 青线 = 两条前腿（肩膀到爪子）**，**红线 / 蓝线 = 两条后腿**，**黄线 = 背上最高那片叶子**；**灰框 = 面具的位置**。`0_design_skeleton.png` 是定稿姿势的骨架画在定稿上，看清哪条线是哪个部位。
> - **面具一格一格照 `1_head.png` 画在灰框里**（木板、左边的大眼睛和黄色亮芯、右边的螺旋纹、下面的尖牙）。每个姿势都是这一个面具，只跟着身体移动和倾斜，**不要转头、不要重新设计**。只有 `d_down` 眼睛和螺旋纹熄灭（暗褐色，不发光）。
> - **腿**：一直是定稿那四条短粗的腿（前腿包着暖褐木甲和青苔，爪子深紫黑），**照骨架的线弯折**，不要拉长、不要压扁、不要比定稿细；**近处的腿颜色正常、画在上面，远处的暗一档**。
> - **背上的叶子鬃毛**每张都在：竖起、甩动、往后飘都照参考图和黄线；**叶子的数量、颜色、大小照定稿**。
> - **蹦跳 4 帧（run1–run4）是一整圈**：小兽往前一蹦一蹦地跑——蹲紧、蹬起、空中、前爪落地；**每帧的身子、面具、叶子都是同一个**，只有身体高度、四条腿和叶子的方向按参考图变。
> - **死亡（d_flip、d_down）**：d_down 四脚朝天躺在地上；身子、面具的大小不变。

## 13 个姿势

| 图 | 文件 | 片段 | 姿势 |
|---|---|---|---|
| 2 | `cinderling-pose-a_fling.png` | attack@520 | 普攻「余烬叶」：往前一蹦（脚离地），背上的叶子往后上方甩起（甩出去的叶子是特效，这里只画身体和鬃毛） |
| 3 | `cinderling-pose-q_bristle.png` | rear@120 | 技能1「刃叶」蓄力：身子往后缩、压低，背上的叶子鬃毛全部高高竖起、张开 |
| 4 | `cinderling-pose-q_throw.png` | rear@180 | 刃叶甩出：身子往前一探，前爪往前伸，叶子鬃毛往前甩（飞出去的叶刃是特效） |
| 5 | `cinderling-pose-e_dig.png` | spawn@1180 | 技能2「钻土突袭」钻地：下半身已经钻进地里（红线以下什么都不画），只露出面具、前爪和背上的叶子 |
| 6 | `cinderling-pose-e_pop.png` | spawn@1320 | 钻出：从地里一跃而出，整个身子腾空（脚离地），四肢往下伸、准备落地 |
| 7 | `cinderling-pose-r_rear.png` | rear@540 | 大招「燎原叶暴」：用后腿站起来，身子挺直，两只前爪往前张开，面具抬起 |
| 8 | `cinderling-pose-r_roar.png` | rear@660 | 站立怒吼：后腿站立，身子往后仰到最高，前爪收在胸前，叶子鬃毛竖在背后（叶子着火是特效） |
| 9 | `cinderling-pose-run1.png` | attack@312 | 蹦 1：四肢收拢、身子压低蹲紧，准备往前蹦 |
| 10 | `cinderling-pose-run2.png` | attack@468 | 蹦 2：后腿一蹬往前上方蹦起（脚离地），前爪往前伸，叶子往后飘 |
| 11 | `cinderling-pose-run3.png` | attack@624 | 蹦 3：在空中最高处，四肢舒展，叶子往后飘 |
| 12 | `cinderling-pose-run4.png` | attack@780 | 蹦 4：前爪先落地，身子往前压，后腿跟上（4 接回 1，循环） |
| 13 | `cinderling-pose-d_flip.png` | death@250 | 被打倒：往后一翻，身子竖起来翻过去，四肢乱蹬 |
| 14 | `cinderling-pose-d_down.png` | death@1000 | 倒地：四脚朝天仰面躺在地上不动，眼睛和螺旋纹熄灭（画成暗褐色） |

## 提示词（每个姿势一次，换掉最后一段的姿势）

每次上传：`0_design.png`（定稿）、`1_head.png`（面具）、这个姿势的 `*_ref.png` 和 `*_skeleton.png`，有余量再加 `0_design_skeleton.png`。**用 image_gen 画。**

```text
Attached images: A the APPROVED pixel-art creature, 3/4 view facing right, on a 1254x1254 canvas with 8 px squares (its lowest point on y 1176) - a SMALL SQUAT FOUR-LEGGED BARK CRITTER: a DARK PURPLE-BROWN BARK body, SHORT THICK LEGS, the front legs covered by WARM BROWN WOOD PLATES with MOSS-GREEN PATCHES, DARK PURPLE-BLACK CLAWS, a row of TALL POINTED PALE GREEN LEAVES standing on its back and a collar of darker green leaves, and for a face a ROUND WOODEN MASK of upright brown planks with ONE BIG GLOWING ORANGE EYE (yellow centre) on its left, a GLOWING ORANGE G-SHAPED SPIRAL on its right and a ROW OF DARK WOODEN FANGS below; B its MASK shown 8x; C a 3D RENDER of this same creature's own game model in THIS POSE, on the same 1254 canvas and grid, already scaled and placed where the picture must be (copy the POSE, the four legs, the body's and the mask's angle and the leaves' direction from it - never its 3D shading; the model is slimmer than A: keep A's bulk); D the SKELETON of that pose, exactly over C: green = the spine (rump to head), PINK and CYAN = its two front legs (shoulder to paw), RED and BLUE = its two back legs, YELLOW = the tallest leaf on its back, GREY BOX = where the mask goes, the red horizontal line = the ground; E (if attached) the design pose's skeleton over image A, showing which line is which part.
Draw with the image generator ONE clean pixel-art picture of the creature of image A in the POSE of images C and D: a 1254x1254 PNG with a real transparent background (alpha only 0 or 255), every square exactly 8 px - the SAME square size as image A - aligned on one straight grid from the canvas corner; standing poses with their lowest point on y 1176; poses in the air exactly as high as in image C (feet NOT on the red line); a pose sunk into the ground shows NOTHING below the red line.
THE SAME BULK AS IMAGE A: the body, the mask, the four legs and the leaves exactly as big as in A in EVERY pose, also when it stands up, hops into the air, flips over or lies on its back (the picture simply grows taller, wider or shorter - never shrink the body or the mask to fit). Each leg along its line (short and thick, the front ones with their wood plates and moss, dark claws at the end), bending at the joints, never stretched, never squashed, never thinner than in A; the NEAR legs in full tone and in front, the FAR ones a step darker. The leaf mane stays on its back, raised, flung or streaming as image C shows, the same leaves as in A.
THE MASK: copy image B SQUARE FOR SQUARE into the grey box (the wooden planks, the big glowing eye with its yellow centre on the left, the orange spiral on the right, the fangs below) - the same mask in every pose, only moved and tilted with the body, never turned, never redrawn; the eye and the spiral go dark only where the pose says so.
The same colours as image A; one continuous near-black outline; no stray single squares, no dithering, no gradients, no blur, no anti-aliasing.
No effects (no flying leaves, no fire, no burn, no dirt or dust, no motion lines, no glow halo), no background, no ground, no shadow, no text, no grid lines, no skeleton lines, no guide shapes.
THE POSE: <one line from the list below>
```

每个姿势的最后一行（英文）：

- a_fling: `FLING - hopping forward off the ground, the leaf mane flung up and back as it throws a leaf (draw the body and the mane only, no flying leaf).`
- q_bristle: `BRISTLE - drawing back and crouching low, the whole leaf mane raised tall and fanned open.`
- q_throw: `THROW - lunging forward, the front paws reaching ahead, the leaf mane whipped forward (no flying leaves: they are separate effects).`
- e_dig: `DIG - half sunk into the ground: everything below the red ground line is hidden (draw nothing below it), only the mask, the front paws and the leaf mane above the ground.`
- e_pop: `POP OUT - bursting up out of the ground into the air (feet off the ground), the legs reaching down to land.`
- r_rear: `REAR UP - standing up on its back legs, the body upright, both front paws spread forward, the mask raised.`
- r_roar: `ROAR - standing on its back legs, leaning back at its tallest, the front paws drawn to the chest, the leaf mane standing behind it (the fire is a separate effect).`
- run1: `HOP 1 - crouched low and tight on all fours, gathering to hop forward.`
- run2: `HOP 2 - the back legs kicking off, springing up and forward (feet off the ground), the front paws reaching ahead, the leaves streaming back.`
- run3: `HOP 3 - at the top of the hop in the air, the legs stretched, the leaves streaming back.`
- run4: `HOP 4 - landing on the front paws first, the body pressed forward, the back legs coming down (4 runs on into 1: the loop).`
- d_flip: `FLIP - knocked over backwards, the body flipping up and over, the legs flailing.`
- d_down: `DOWN - lying still on its back, legs up, the eye and the spiral gone dark (a dull dark brown, no glow).`

## 交回

- 每个姿势一张：`outputs/cinderling-poses/cinderling-pose-<名字>.png`（1254 × 1254、真透明背景、每格 8 px）；原始生成图原样放进 `outputs/cinderling-poses/raw/`；`generation-prompts.txt` 写明实际用的提示词。**不要再把画好的图缩放或重新取样**（原图我自己按格子读）。
- **13 张都画完再交**，最后写 `outputs/cinderling-poses/HANDOFF.md`（列出交付的文件），再打包成 `outputs/cinderling_poses_done.zip`。

## Claude 收到后（给 Claude 看）

- 放进 `assets/source/cinderling/codex_poses/`，**先量 Codex 实际的格子**（不一定是 8 px），读 raw，**每张按定稿的身体大小读**（站起、蹦起、翻倒时 Codex 容易把身体画小：codex-fit-shrinks-bodies），面具对齐定稿的面具（hd/idle.png）；每帧 8 倍检查（面具不动、大眼睛和螺旋纹还在、腿没有被压扁或拉长、远处的腿暗一档、空中的姿势真的离地）。
- 骨架包：`tools/art/pack_cinderling_poses.py`（骨架是它客户端模型自己的骨骼，按动作片段的那一帧投影；面具放大 1.3 倍；它没有跑步动作，蹦跳 4 帧取自它普攻的往前一蹦）；这份提示词由 `tools/art/gen_cinderling_pose_md.py` 生成。
