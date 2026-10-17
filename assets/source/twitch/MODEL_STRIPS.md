# 图奇：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/twitch_design.png`（放大 8 倍，1024×1024；38 行高、44 格宽，24 色；脚底在第 99 行，站位点在第 64 列）——是按你上一轮 B 的生图原稿自己的格子取回、整行整列删到 38 行的版本（用户：「B 38（我读回的）」）。**造型图就是标准**：大耳朵（里面粉色）、黄铜护目镜、红鼻头、黄白尖牙、橙围巾、绿背包和铜铆钉青色药瓶、青蓝斗篷和浅棕褐边、绿手臂和绿爪子、灰紫反关节鼠腿和白爪尖、一节一节的尾巴、两手横端的黄铜弩和翠绿宝石，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`twitch_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/twitch_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。英雄联盟的 W 是空翻扔桶、E 是跳起来喷毒、死亡是翻跟头，**我们不照这些翻滚**：扔桶站着扔，E 只小跳一下，死亡照表里写的向后倒、仰躺。
> - **放技能时的身体就是待机的身体**（同一套像素）：背包、斗篷、围巾、尾巴、腿的形状和大小不能变，只动手臂和弩；整个人可以前倾后仰、前后挪 1–3 格。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的耳朵、护目镜、鼻子和牙**，**不画背影**（只有死亡仰躺时整个人连头转 90°）；③ **腿**：the legs are the design's own rat legs - grey-purple, bending BACKWARD at the knee, white toe claws - square for square in every standing frame (idle, the attack, Q, W's throw, R, hit): apart as in the design, never redrawn as human legs; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's hop and the death change them. In the run the legs CROSS: every half cycle the two feet swap front and back, the lifted foot 2-3 rows up passing BESIDE the other one (not only meeting under the body and parting again); the far leg one shade darker so the two do not melt together; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares) and the white toe claws；④ **手臂和弩**：the arms are the design's arms: green, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest), the near arm over the body, the far arm drawn under it; the brass crossbow stays in his hands and moves with them as ONE piece - the arms and the crossbow turned whole in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the hands and the crossbow are NEVER hidden behind the body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours；⑤ the green backpack with its brass rivets and teal vials, the blue-teal coat with its tan trim, the orange scarf and the banded tail stay on him in every frame, the same shapes and sizes as in the design (the tail may swing with the steps in the run and lift in E's hop, as one piece)。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/twitch_now_<动作>.png`（骨架），图2 = `design/twitch_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/twitch-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧弩尖 / 手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`twitch_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/twitch_palette.png`，或直接读 `design/twitch_design_1x.png`）。
4. **贴头**：把造型图的头（`design/twitch_head_1x.png` 里不透明的格子：两只耳朵、护目镜、鼻子和牙；不含耳朵上面背包的药瓶和下巴下的围巾；在 128×128 画布上的范围 x 59–77、y 66–79，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡仰躺的帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `twitch_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/twitch_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/twitch_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/twitch_head.png`、`_1x.png` | 要贴进每一帧的头（耳朵、护目镜、鼻子、牙） | 贴头 |
| `design/twitch_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `twitch_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/twitch_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、弩和身体的动作 |
| `guide/twitch_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `twitch_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/twitch_picture.png`、`refs/twitch_draft_codex.png` | 用户选的原画 B 和你上一轮的生图原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：the legs are the design's own rat legs - grey-purple, bending BACKWARD at the knee, white toe claws - square for square in every standing frame (idle, the attack, Q, W's throw, R, hit): apart as in the design, never redrawn as human legs; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's hop and the death change them. In the run the legs CROSS: every half cycle the two feet swap front and back, the lifted foot 2-3 rows up passing BESIDE the other one (not only meeting under the body and parting again); the far leg one shade darker so the two do not melt together; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares) and the white toe claws。
- **手臂和弩**：the arms are the design's arms: green, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest), the near arm over the body, the far arm drawn under it; the brass crossbow stays in his hands and moves with them as ONE piece - the arms and the crossbow turned whole in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the hands and the crossbow are NEVER hidden behind the body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours。
- **身上**：the green backpack with its brass rivets and teal vials, the blue-teal coat with its tan trim, the orange scarf and the banded tail stay on him in every frame, the same shapes and sizes as in the design (the tail may swing with the steps in the run and lift in E's hop, as one piece)。
- **头每帧都是造型图的头**（耳朵、护目镜、鼻子、牙逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），尾巴和斗篷下摆也不能低于这条线。
- **跑步循环**：每帧头相对站位点的横向位置不变；两腿真正交叉（每半个周期两只脚交换前后）；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不翻跟头**。**只画角色本身**：飞出去的弩箭和毒桶、枪口火光、毒烟、隐身的烟雾、大招的绿光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/twitch_design.png`，第二张 `now/twitch_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `twitch_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same big rat ears pink inside, the brass goggle, the red nose, the yellow-white teeth, the orange scarf, the green backpack with brass rivets and teal vials, the blue-teal coat with its tan trim, the green arms and clawed hands, the grey-purple backward-bending rat legs with white toe claws, the banded tail, the brass crossbow with the emerald gem held in both hands, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the crossbow and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own body and legs; every shot and throw goes to the RIGHT of the image; never draw him from the back, upside down or somersaulting.
The character: Twitch, the Plague Rat (a big rat standing on two legs with a crossbow).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #020201 #3F231F #193B43 #00407A #8F141D #7A3F2E #336B5E #70435E #615C5B #066BAC #B9661D #DA3633 #F94714 #18E283 #F5A934 #29EACA #FCBF2B #FC836D #B6B69A #E0B292 #FEEE4F #91DAF9 #FDF6D0 #FBFDF7. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every standing frame the backpack, the coat, the scarf, the tail and the legs keep the FIRST image's shapes and sizes square for square; only the arms and the crossbow move, and the whole figure may lean or move 1-3 squares.
Legs: the legs are the design's own rat legs - grey-purple, bending BACKWARD at the knee, white toe claws - square for square in every standing frame (idle, the attack, Q, W's throw, R, hit): apart as in the design, never redrawn as human legs; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's hop and the death change them. In the run the legs CROSS: every half cycle the two feet swap front and back, the lifted foot 2-3 rows up passing BESIDE the other one (not only meeting under the body and parting again); the far leg one shade darker so the two do not melt together; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares) and the white toe claws.
The arms and the crossbow: the arms are the design's arms: green, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest), the near arm over the body, the far arm drawn under it; the brass crossbow stays in his hands and moves with them as ONE piece - the arms and the crossbow turned whole in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the hands and the crossbow are NEVER hidden behind the body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours.
The body parts: the green backpack with its brass rivets and teal vials, the blue-teal coat with its tan trim, the orange scarf and the banded tail stay on him in every frame, the same shapes and sizes as in the design (the tail may swing with the steps in the run and lift in E's hop, as one piece).
The head (both ears, the brass goggle, the snout with the red nose, the teeth) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the death frames where he lies on his back is it turned 90 degrees with the whole body). Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in twitch_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every shot and throw goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (the flying bolt or cask, the muzzle flash, poison clouds, the stealth smoke, the green glow) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the hands and the crossbow never behind the body, the standing frames on the FIRST image's own body and legs, the run's feet swapping front and back, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、弩和身体的方向和姿势照图1（射击、扔桶都朝图的右边，不翻跟头）；站着的帧身体和腿用图2自己的。
3. 长相、配色、细节全部换成图2：大耳朵、黄铜护目镜、红鼻头、黄白尖牙、橙围巾、绿背包、青蓝斗篷和浅棕褐边、绿手臂、灰紫鼠腿和白爪尖、一节一节的尾巴、黄铜弩和翠绿宝石。
4. 手臂从肩膀外侧长出来，手和弩任何一帧都不能藏在身体后面。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `twitch_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `twitch_run.png`（跑步（交叉步）） | 8 × 100 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 0.8 s): a hunched scurry, the body leaning a little forward, the crossbow held level in both hands at the hip as in the design; the legs CROSS: in frames 1 and 5 the feet are furthest apart (frame 1 the near leg in front, frame 5 the far leg in front), in frames 3 and 7 the lifted foot passes BESIDE the other 2-3 rows up; the body bobs 1 row with each landing (down in 1 and 5, up in 3 and 7); the tail swings a little against the steps; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `twitch_attack.png`（普攻（弩射击）） | 5 帧：60 60 80 80 80 | 第 3 帧（tick 7） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `BASIC ATTACK (a crossbow shot), 5 frames: 1 the design's stance, the crossbow level; 2 aiming: the crossbow lifted one step, the whole figure leaning 1 square forward; 3 THE SHOT (the bolt leaves here): the arms and the crossbow kicked back 1-2 squares by the recoil, the tip tilted up one step (the bolt and the muzzle flash are separate effects - do not draw them); 4 lowering it; 5 back to the design's stance. Legs: the design's legs.` |
| `twitch_skill.png`（Q 埋伏（压低身子潜行）） | 3 × 100 | 第 2 帧（tick 6） | 3 列 × 1 行，3072×768 | 第 81 行 | `AMBUSH (Q), 3 frames: 1 hunching down 1-2 rows, the coat pulled round him, the crossbow held close; 2 the deepest crouch, sneaking, grinning (he turns invisible here: the smoke is an effect); 3 back toward the design's stance. Legs: the design's legs, the whole figure lower.` |
| `twitch_skill2.png`（W 剧毒之桶（单手扔桶）） | 4 帧：80 70 100 100 | 第 3 帧（tick 9） | 4 列 × 1 行，4096×768 | 第 81 行 | `VENOM CASK (W, the throw), 4 frames: 1 the near hand lets go of the crossbow (the far hand keeps it at the hip) and takes a small round green-brown cask (3x3 squares) from his belt; 2 the near arm wound back and up behind the head with the cask, the body leaning back; 3 THE THROW (the cask leaves here): the near arm flung forward and up to the image right, the hand open and EMPTY (the flying cask is a separate effect - do NOT draw it here); 4 back to the design's stance, both hands on the crossbow. Legs: the design's legs. Never his back.` |
| `twitch_skill2_e.png`（E 毒性爆发（小跳、张臂）） | 5 帧：80 80 100 80 80 | 第 3 帧（tick 10） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `CONTAMINATE (E), 5 frames: 1 crouching a little; 2 crouching lower, about to spring; 3 THE BURST (the venom bursts here): a small hop 2-3 rows up, the near arm flung wide and up to the image left with the claws spread, the mouth wide open, the crossbow held out in the other hand to the image right; 4 landing; 5 back to the design's stance. The venom clouds are effects.` |
| `twitch_ult.png`（R 火力全开（举弩上肩）） | 3 × 100 | 第 2 帧（tick 6） | 3 列 × 1 行，3072×768 | 第 81 行 | `SPRAY AND PRAY (R), 3 frames: 1 lifting the crossbow; 2 THE CAST: the crossbow raised to the shoulder and aimed level to the image right, the near arm flung back and up to the image left with the claws spread, the mouth open in a laugh; 3 back toward the design's stance. The green glow is an effect.` |
| `twitch_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left); 2 recovering toward the design's stance. The design's legs.` |
| `twitch_dead.png`（死亡（向后倒、仰躺）） | 8 帧：100 110 120 130 150 200 300 400 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 knocked back 2-3 squares; 3 the WHOLE body (legs, crossbow, backpack and tail included, as one piece) tipping over backwards, turned 45 degrees (falling to the image left); 4 turned 90 degrees, lying on his back on the ground (the head to the image left, the feet to the image right); 5-8 the same as 4, still. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样大；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（背包、斗篷、围巾、尾巴、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩膀外侧长出来；手和弩没有藏在身体后面；
- [ ] 跑步两腿真正交叉（每半个周期两只脚交换前后、抬起的脚从另一只旁边越过）、远侧腿暗一档、腿的颜色和爪尖和待机一样，腿没有缺格子；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有翻跟头；射击和扔桶都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；扔桶那一帧手里是空的；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `twitch_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂和弩整块按 45° / 90° 转，整个人前倾后仰）。
- 放进 `assets/source/native/`，`twitch_cells.json` 用包里这份，`twitch_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；红色方：朝向特效（枪口火光）烘进动作帧（`twitch_bake.json`）。
- 按出手帧核对技能数据的时机（普攻 tick 7、Q tick 6、W 扔桶 tick 9、E tick 10、R tick 6），量弩箭出手点和头像截取点，重跑模拟，做预览 GIF。
