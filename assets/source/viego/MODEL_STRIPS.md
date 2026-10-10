# 佛耶戈：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/viego_design.png`（放大 8 倍，1024×1024；51 行高、51 格宽，27 色；脚底在第 99 行，站位点在第 64 列）——从你上一轮的生图原稿 2 按格子取回、整行整列删到王冠顶到脚底 42 行（用户：「OK了 下一步」）。**造型图就是标准**：银白乱发、青绿荆棘王冠、苍白的脸 + 两只青绿眼睛、深藏青立领长风衣（敞开）、苍白胸口 + 青绿边的倒三角印记、棕红钉扣皮带、带刺的深藏青铠甲和尖头靴、近侧手握着扛在肩上的青绿破败王剑（大十字护手），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`viego_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/viego_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、剑和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **放技能时的身体就是待机的身体**（同一套像素）：风衣、胸口、皮带、腿的形状和大小不能变，只动手臂和剑；整个人可以前倾后仰、前冲、下蹲、跳起。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头大、身体短）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的银发、王冠、脸和青绿眼睛**，**不画背影**；③ **腿**：the legs are the design's own legs - the dark navy trousers, the silver-edged spiked knee guards and the pointed dark navy boots - square for square in every standing frame (the attack's wind-up, Q's start, hit): as in the design, never redrawn; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge or a lean of the whole body), never the upper body alone over still legs; the lunges (the attack's swing, Q's thrust, W's dash, R's landing, the possession's stab) bend the knees and step the front foot forward as in the THIRD image. In the run the legs CROSS: every half cycle the two feet swap front and back, the lifted foot 1-2 rows up passing BESIDE the other one; both legs in the design's own colours; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares)；④ **手臂和剑**：the arms are the design's arms: dark navy spiked armour with black pointed gauntlets, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); the near arm (image left) grips the greatsword; the GREATSWORD (the glowing teal blade with its light centre line and the big teal cross guard with four hooked arms) is ONE rigid piece with the gripping hand: turned whole about the hand, never bent, never shortened, never thinner, the guard always the same cross; where the animation swings it, draw it at the new angle with the same length and width; the gripping hand and the blade are NEVER hidden behind the body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours；⑤ the open dark navy coat with its high collar, the pale chest with the teal-edged triangle mark, the reddish-brown studded belt and the coat's split tails stay on him in every frame, the same shapes and sizes as in the design (the coat tails may swing behind him in the run and the casts, as one piece)；⑥ 剑尖、风衣下摆**永远不低于脚底线**（英雄联盟里剑插进地里，我们只画到地面为止）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/viego_now_<动作>.png`（骨架），图2 = `design/viego_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。**整条画糊了就一帧一帧单独生成**（每帧一张图，最后拼回格子）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/viego-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧握剑的手和剑尖的位置）和所有生图原稿（`raw/`，不要重采样），最好打成一个 zip（`viego_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/viego_palette.png`，或直接读 `design/viego_design_1x.png`）。
4. **贴头**：把造型图的头（`design/viego_head_1x.png` 里不透明的格子：银发、青绿王冠、脸和两只青绿眼睛；不含左边的十字护手和右上的剑身；在 128×128 画布上的范围 x 59–75、y 57–74，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡低头的几帧也只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `viego_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/viego_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/viego_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/viego_head.png`、`_1x.png` | 要贴进每一帧的头（银发、王冠、脸、眼睛） | 贴头 |
| `design/viego_palette.png` | 造型图的全部 27 色（暗到亮） | 色板 |
| `viego_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/viego_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、剑和身体的动作 |
| `guide/viego_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `viego_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/viego_picture.png`、`refs/viego_draft_codex.png` | 用户选的原画 A 和你上一轮的生图原稿 2（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 27 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：the legs are the design's own legs - the dark navy trousers, the silver-edged spiked knee guards and the pointed dark navy boots - square for square in every standing frame (the attack's wind-up, Q's start, hit): as in the design, never redrawn; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge or a lean of the whole body), never the upper body alone over still legs; the lunges (the attack's swing, Q's thrust, W's dash, R's landing, the possession's stab) bend the knees and step the front foot forward as in the THIRD image. In the run the legs CROSS: every half cycle the two feet swap front and back, the lifted foot 1-2 rows up passing BESIDE the other one; both legs in the design's own colours; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares)。
- **手臂和剑**：the arms are the design's arms: dark navy spiked armour with black pointed gauntlets, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); the near arm (image left) grips the greatsword; the GREATSWORD (the glowing teal blade with its light centre line and the big teal cross guard with four hooked arms) is ONE rigid piece with the gripping hand: turned whole about the hand, never bent, never shortened, never thinner, the guard always the same cross; where the animation swings it, draw it at the new angle with the same length and width; the gripping hand and the blade are NEVER hidden behind the body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours。
- **身上**：the open dark navy coat with its high collar, the pale chest with the teal-edged triangle mark, the reddish-brown studded belt and the coat's split tails stay on him in every frame, the same shapes and sizes as in the design (the coat tails may swing behind him in the run and the casts, as one piece)。
- **头每帧都是造型图的头**（银发、王冠、脸、青绿眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），剑尖和风衣下摆也不能低于这条线。
- **跑步循环**：剑一直扛在肩上；每帧头相对站位点的横向位置不变；两腿真正交叉（每半个周期两只脚交换前后）；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不趴在地上**。**只画角色本身**：黑雾、亡魂、灵魂、刺击光、冲击波都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/viego_design.png`，第二张 `now/viego_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `viego_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same messy silver-white hair, the glowing teal thorn crown, the pale face with two teal eyes, the open dark navy high-collared coat, the pale chest with the teal-edged triangle mark, the reddish-brown studded belt, the spiked dark navy armour and pointed boots, and the huge glowing teal greatsword with its big cross guard gripped in his near hand, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the sword and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own body and legs; every cast goes to the RIGHT of the image; never draw him from the back, upside down or lying flat on the ground.
The character: Viego, the Ruined King (a pale undead king with a huge glowing teal greatsword).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 27 colors of the FIRST image, no new colors: #04020E #1A1132 #042D31 #252739 #231E48 #5E1B27 #03615B #2F2C6A #81242D #037C70 #565066 #7C4C4B #03A188 #A26054 #0AB79C #677689 #7C909E #C78370 #39D7C1 #AFAC94 #DEA189 #B3ABB9 #60E7D6 #A6B9C3 #91F9F7 #FBD4B6 #EAE8EE. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every frame the coat, the chest, the belt and the legs keep the FIRST image's shapes and sizes square for square; only the arms and the sword move, and the whole figure may lean, lunge, crouch or jump.
Legs: the legs are the design's own legs - the dark navy trousers, the silver-edged spiked knee guards and the pointed dark navy boots - square for square in every standing frame (the attack's wind-up, Q's start, hit): as in the design, never redrawn; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge or a lean of the whole body), never the upper body alone over still legs; the lunges (the attack's swing, Q's thrust, W's dash, R's landing, the possession's stab) bend the knees and step the front foot forward as in the THIRD image. In the run the legs CROSS: every half cycle the two feet swap front and back, the lifted foot 1-2 rows up passing BESIDE the other one; both legs in the design's own colours; the hips stay under the body; the body bobs 1 row with each landing; the legs keep the design's own leg squares (never flattened, squashed or missing squares).
The arms and the sword: the arms are the design's arms: dark navy spiked armour with black pointed gauntlets, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); the near arm (image left) grips the greatsword; the GREATSWORD (the glowing teal blade with its light centre line and the big teal cross guard with four hooked arms) is ONE rigid piece with the gripping hand: turned whole about the hand, never bent, never shortened, never thinner, the guard always the same cross; where the animation swings it, draw it at the new angle with the same length and width; the gripping hand and the blade are NEVER hidden behind the body in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours.
The body parts: the open dark navy coat with its high collar, the pale chest with the teal-edged triangle mark, the reddish-brown studded belt and the coat's split tails stay on him in every frame, the same shapes and sizes as in the design (the coat tails may swing behind him in the run and the casts, as one piece).
The head (the silver-white hair, the teal crown, the pale face with its teal eyes) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there - the sword's tip and the coat's hem too. His place across the cell follows the SECOND image (each frame's standing point is in viego_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (mist, wraiths, souls, slashes, shockwaves, glows, sparks) - only the character. Every animation starts and ends near the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x128 squares (1024x1024 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the gripping hand and the sword never behind the body, the sword straight, full length and full width with its cross guard, the standing frames on the FIRST image's own body and legs, the run's feet swapping front and back, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、剑和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；身体和腿用图2自己的。
3. 长相、配色、细节全部换成图2：银白乱发、青绿荆棘王冠、苍白的脸和青绿眼睛、敞开的深藏青立领风衣、苍白胸口和倒三角印记、棕红钉扣皮带、带刺的深藏青铠甲和尖头靴、青绿发光的大剑和十字护手。
4. 手臂从肩膀外侧长出来，握剑的手和剑任何一帧都不能藏在身体后面，剑始终笔直、长度和宽度不变；剑尖不能低于脚底线。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `viego_idle.png`（待机） | 6 × 160 | — | 3 列 × 2 行，3072×2048 | 第 99 行 | **已做好，不用画** |
| `viego_run.png`（跑步（交叉步，剑扛肩上）） | 8 帧：108 108 108 108 108 108 108 109 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | `RUN, 8 frames, one seamless loop (League's run, 0.87 s): the greatsword stays ON HIS SHOULDER exactly as in the design (League keeps it there too), the far arm swinging a little; the legs CROSS: in frames 1 and 5 the feet are furthest apart (frame 1 the near leg in front, frame 5 the far leg in front), in frames 3 and 7 the lifted foot passes BESIDE the other 1-2 rows up; the body bobs 1 row with each landing; the coat tails swing a little behind; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `viego_attack.png`（普攻（双手跃斩）） | 6 帧：60 60 50 70 80 80 | 第 5 帧（tick 14） | 3 列 × 2 行，3072×2048 | 第 99 行 | `BASIC ATTACK (a two-handed slash), 6 frames: 1 the design's stance, the sword on the shoulder; 2 the sword lifting off the shoulder; 3 the sword raised high behind his head, the body leaning back; 4 the leap: the body springing forward, the blade coming over; 5 THE SLASH (the blow lands here): lunging forward, front knee bent, the blade swept down and forward to the image right, level at knee height (its tip above the feet line); 6 back toward the design's stance, the sword coming up to the shoulder.` |
| `viego_skill.png`（Q 破败王剑（突刺）） | 6 帧：50 50 40 60 50 50 | 第 4 帧（tick 8） | 3 列 × 2 行，3072×2048 | 第 99 行 | `BLADE OF THE RUINED KING (Q, a thrust), 6 frames: 1 the sword lifted off the shoulder; 2 the sword drawn back, the blade level pointing to the image LEFT behind him, the body coiled; 3 crouching low, the blade still back; 4 THE THRUST (it hits here): a deep lunge to the image right, the sword thrust straight forward and slightly down, the blade level to the right at hip height; 5 holding the lunge; 6 rising back to the design's stance.` |
| `viego_skill2.png`（E 茫茫焦土 + W 千载幽咽（起雾、蓄力、冲刺）） | 7 帧：70 80 120 130 120 120 130 | 第 5 帧（tick 24） | 4 列 × 2 行，4096×2048，最后 1 格空 | 第 99 行 | `HARROWED PATH + SPECTRAL MAW (E then W), 7 frames: 1 the sword swung down to his side, the far hand flicked out (the mist rises - an effect, do not draw it); 2 a small hop back, the sword low; 3 THE CHARGE: standing braced, the sword held upright before him in both hands; 4 the charge held, the body sinking a little; 5 THE DASH (the wraith leaves here): the whole body flung forward to the image right, low, the sword trailing; 6 landing, the blade level forward to the image right; 7 back toward the design's stance.` |
| `viego_ult.png`（R 痛贯天灵（跃起、下刺）） | 8 帧：60 60 60 70 60 80 100 110 | 第 6 帧（tick 19） | 4 列 × 2 行，4096×2048 | 第 99 行 | `HEARTBREAKER (R, a leap and a stab), 8 frames: 1 the design's stance, the sword coming off the shoulder; 2 crouching, the sword raised up behind; 3 springing up, the blade swinging low; 4 IN THE AIR (3-5 rows above the feet line), the sword held level over his head; 5 landing upright, the sword point DOWN in front of him; 6 THE STAB (it hits here): crouched, both hands driving the sword straight DOWN into the ground in front of him (the blade vertical, its tip ON the feet line - the part in the ground is not drawn); 7 holding the stab; 8 rising back to the design's stance.` |
| `viego_possess.png`（君命已决（吸魂下刺）） | 4 帧：80 80 120 120 | 第 3 帧（tick 10） | 4 列 × 1 行，4096×1024 | 第 99 行 | `SOVEREIGN'S DOMINATION (taking a soul), 4 frames: 1 the sword coming off the shoulder; 2 the sword trailing low behind him, the far hand reaching forward; 3 THE STAB (the soul is taken here): crouched, the sword driven down and forward into the ground before him (its tip on the feet line); 4 rising back toward the design's stance. The soul and the mist are effects.` |
| `viego_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×1024 | 第 99 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left); 2 recovering toward the design's stance. The design's legs.` |
| `viego_dead.png`（死亡（跪倒在插地的剑前）） | 8 帧：100 100 100 120 150 200 300 400 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit, the sword lifted; 2 staggering forward, the sword coming down; 3 falling to his knees, the blade planted in the ground before him; 4-6 kneeling, slumping over the planted sword, the head bowed; 7-8 the same, still. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样大；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（风衣、胸口、皮带、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩膀外侧长出来；握剑的手和剑没有藏在身体后面，剑笔直、没有变短变细，十字护手完整；
- [ ] 跑步剑一直扛在肩上，两腿真正交叉（每半个周期两只脚交换前后、抬起的脚从另一只旁边越过），腿的颜色和待机一样，没有缺格子；
- [ ] 脚底线以下没有任何像素（剑尖、衣摆也不行）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有趴在地上；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `viego_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂连剑整块转，整个人前倾、前冲、下蹲）。
- 放进 `assets/source/native/`，`viego_cells.json` 用包里这份，待机由 `import_native.py` 的 idle_breathe 从造型图生成。
- `import_native.py`：ORDER 待机，COMPLETE 补描边；红色方：有前后之分、贴在他身上的特效烘进动作帧（`viego_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick 14、Q tick 8、W 冲刺 tick 24、R 下刺 tick 19、吸魂 tick 10），量头像截取点，重跑模拟，做预览 GIF。
