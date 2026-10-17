# 希维尔：照首稿重画小一号（第 1 步第二轮，给 Codex 的提示词）

> 上一轮你的生图首稿（`sivir_design_A_generated.png`，按格子读回来 63×80 格）**用户选定了**：「用这张」。但你自己缩成 38 行的 A/B，还有我整行整列删到 38/42/46 行的版本，用户都说「太胖 太丑」——缩小或删行删列会把腿、手臂、身体压短压粗，脸变成一块平色。
> 这一轮请**照首稿一模一样重画，只是小一号**：头发顶到脚底 **46 格**（首稿 63 格），和卢锡安差不多高。
> - **直接按 46 格的格子一格一格画**，像像素画师画同一个角色的小一号版本；**不要先画大再缩小，不要删首稿的行列**。画出来比 46 格大，就重画，别缩。
> - **比例完全照首稿**：头（头发顶到下巴）约 14 格、围巾和身体约 14 格、腿约 18 格；四肢细长（大腿连描边 4–5 格宽、小腿 3–4、手臂 3），细腰，蹲伏的姿势、弯腿的角度都和首稿一样；整体从十字刃左边刃尖到前伸的手套约 58 格宽，不要更宽。要苗条好看，不要矮胖。
> - 姿势、颜色、脸、头发、头冠、围巾、盔甲、腰布、展开的十字刃（圆环镂空 + 四片带钩的刃）都照首稿；色板就是你上一轮的 24 色。
> - 脸照首稿放大图：两眼同一行、各 2×2（上行高光 + 深色瞳孔，下行薄荷青 `#4FE6D2`，上面一行深色睫毛），两眼间 2 格皮肤，薄荷青只在眼睛上；细眉用头发最深的藏青；脸的中线上 1 格深红的嘴。
> - 交付：`sivir_design_v2.png`（1024×1024，8×8 严格网格、透明度 0/255、≤24 色、一种近黑描边）、`sivir_design_v2_1x.png`，**生图原稿也一起交（不要缩放或重采样过的）**，最后写 `HANDOFF.md`（写明头发顶到脚底多少格、头多少格），打成 `sivir_design_v2_pack.zip`。

## 附图（都在 `sivir/` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `1_draft_approved.png` | 你的首稿，按它自己的格子读回来（63×80 格，×8） | **照它画**：样子、姿势、比例、颜色、脸，全都一样 |
| `2_target_size.png` | 1024×1024 画布，首稿等比缩到 46 格的灰色剪影；红线 = 脚底下沿，蓝线 = 两脚中间，绿线 = 头发顶（46 格），橙线 = 下巴 | **大小和位置照它** |
| `3_quality_bar.png` | 包里的卢锡安（46）、凯特琳、卡莎、烬、薇恩，游戏里的样子 ×8 | 像素大小和干净程度；她和卢锡安差不多高 |
| `4_rejected_too_fat.png` | 被用户否掉的 5 版（你缩的 A/B、我删行删列的 38/42/46 行） | **反例：太胖太丑，不要画成这样** |
| `5_size_guide.png` | 首稿等比缩到 46 格（彩色，糊的） | 只看能放下什么，不要照它的样子 |
| `6_face_ref.png` | 首稿的头 ×16 | 脸照它画 |

## 提示词：`sivir_design_v2.png`

附图：`sivir/` 里的 1–6 号图，按顺序。

```text
Six attached images. FIRST: YOUR OWN earlier draft of this character, approved by the user - copy it EXACTLY: the same woman, the same pose (the low wide fighting crouch, the near hand holding the open gold crossblade with its ring behind her back hip, the far arm reaching forward with a brown clawed glove), the same PROPORTIONS (a slim athletic figure, long legs, the head about 30% of her height, the crossblade about as wide as her torso and legs), the same colours, the same face, hair, tiara, scarf, armour and loincloth. Only its SIZE changes. SECOND: a 1024x1024 canvas (128x128 squares at 8x) with a flat grey shape - the FIRST image scaled evenly to its new size: use it for her SIZE and her PLACE in the canvas. THIRD: heroes of this game at game size as they are in the game now, at 8x, approved by the user - she should be about as tall as the first of them (46 squares) and match their crisp, clean pixel look. FOURTH: REJECTED versions - the user said they are "too fat and too ugly": they were made by shrinking the FIRST image (squashing it, deleting rows and columns), which made the legs, arms and body short and thick and the face a flat blob. Do NOT draw her like them. FIFTH: the FIRST image scaled evenly to the new size in colour - use it ONLY to see what fits where; it is blurry, do not copy its look. SIXTH: the FIRST image's head, big - copy the face exactly.
Task: REDRAW the FIRST image a size smaller as a crisp game sprite - a low-resolution pixel-art character shown enlarged 8x, every pixel one 8x8 square on a single 8-px grid: 46 squares from the top of her hair to her soles (the FIRST image has 63). Draw it directly at that size, square by square, like a pixel artist making a smaller version of the same sprite - do NOT draw it bigger and shrink or resample it, do NOT delete rows or columns from the FIRST image: that is what made the FOURTH image fat and ugly. If your drawing comes out bigger than 46 squares, draw it again smaller instead of shrinking it.
Proportions (most important): exactly those of the FIRST image: the head (top of the hair to the chin) about 14 of the 46 squares, the scarf and the torso about 14, the legs about 18; slender limbs - the thighs about 4-5 squares wide with their outline, the shins 3-4, the arms 3; the long legs bent in the crouch exactly as in the FIRST image; a narrow waist; the whole figure about 58 squares wide from the crossblade's left tip to the reaching glove (the SECOND image), never wider. A slim, elegant warrior, not stocky.
Clean (as the FIRST image): at most 24 colours, every material 2-4 flat shades, big solid areas, no dithering, no gradients, no noise; ONE 1-square near-black outline around the whole silhouette and inside the outline the materials' own darker shades, never a second black ring.
Palette (the FIRST image's colours): #14101A #1B2236 #2C3A58 #46597E #9A5434 #D58A5C #F4B888 #A0302A #4FE6D2 #F6F0DC #CBBFA4 #5C3410 #A8691E #E8A830 #FFE27A #FFF4C0 #0C5E58 #18A890 #1A2440 #2C3E66 #2E2438 #4E3F5E #3E2416 #7A4A28 (the first is the outline; #4FE6D2 the eyes only).
Face, as the SIXTH image: both eyes visible, the same size and on the same rows, each 2 squares wide and 2 tall (a light highlight square and a dark pupil on top, TEAL-MINT #4FE6D2 below, a dark lash row above), 2 squares of skin between them; the mint only in the eyes (the gems are a deeper teal); thin calm brows in the hair's darkest navy; one dark-red mouth square on the face's middle line; the gold tiara with its teal gem on the forehead; the black hair framing the face and flowing down her back.
Pose and place: 3/4 FRONT view facing right exactly as the FIRST image, where the SECOND image's grey shape stands and as big: the soles' lowest row at y=792-799 (square row 99), the point between her feet on the middle column (x=512, the blue line); the green line is the top of the hair (46 squares over the soles), the orange line the chin. Nothing below the soles.
Layout: one single square image, 1024x1024 (a 128x128-square canvas at 8x). Transparent background (if not possible: solid pure green #00FF00). No grid lines, no text, no border, no shadow.
Before finishing, check: 46 squares from the top of the hair to the soles; the same proportions and the same slim limbs as the FIRST image (compare them side by side); all squares 8x8 on one grid; at most 24 colours; one outline colour; both eyes 2x2 and level; the crossblade open with its ring and four hooked blades; nothing below the soles.
```

## 交回前自查

- [ ] 头发顶到脚底 46 格；脚底在第 99 行、两脚中间在 x=512，下面没有像素；
- [ ] 和首稿放在一起比：比例一样、腿和手臂一样细长，没有变矮变胖；脸和首稿一样；
- [ ] 严格 8×8 网格、透明度 0/255、不超过 24 色、描边只有一种近黑；
- [ ] 十字刃展开，圆环镂空和四片带钩的刃都清楚；两眼 2×2 同一行；最后写 `HANDOFF.md`。
