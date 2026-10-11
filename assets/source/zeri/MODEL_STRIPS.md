# 泽丽：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/zeri_design.png`（放大 8 倍，1024×1024；38 行高、28 格宽，19 色；鞋底在第 99 行，站位点在第 64 列）。**造型图就是标准**：两个尖刺发髻（深青蓝尖刺 + 柠檬黄绿）、黄绿眼睛、脸颊创可贴、青蓝外套 + 银管、黄背心 + 闪电、红棕皮带、深紫红紧身裤 + 护膝、棕靴 + 橙袜口、画面右侧竖举的柠檬黄 + 橙色步枪和握枪的手、画面左侧垂下的紫红手套，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`zeri_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/zeri_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **放技能时的身体就是待机的身体**（同一套像素）：外套、背心、皮带、发髻、腿的形状和大小不能变，只动手臂；整个人可以前倾后仰、上下前后挪 1–3 格。
> - **握枪的手臂和步枪是一整块**：开枪时**整块转 90°**（枪口从朝上变成朝右、端平在胸口高度），不能弯、不能转奇怪的角度、不能逐行错开；另一只手可以整块抬起来托住枪。**手任何一帧都不能被身体、外套或步枪挡住。**
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的发髻、脸和刘海**，**不画背影**（只有死亡倒地时整个人连头转 90°）；③ **腿**：the legs are the design's own legs - the dark maroon leggings with the round knee pad, the brown ankle boots with orange socks, legs apart - square for square in every frame but the run, E's hop and the death; a cast may move the WHOLE figure 1-2 squares forward, back or up (a lean or a step of the whole body), never the upper body alone over still legs. In the run she RUNS with clear steps (League's run): the legs move as rigid pieces (thigh+shin+boot), one forward while the other is back, the boots on the feet line when planted; the legs keep the design's own leg squares and colours (never flattened, squashed or missing squares)；④ **手臂**：the arms are the design's arms, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest). The image-RIGHT arm and the RIFLE it holds are ONE rigid piece: upright beside her head in the idle; to shoot it turns as a whole by a QUARTER TURN (the rifle level, pointing to the image right at chest height) - never bent, never turned by an odd angle, never shifted row by row; the image-LEFT arm hangs as in the design or comes up as one rigid piece to steady the rifle. The hands (the maroon fingerless glove) are NEVER hidden behind the body, the coat or the rifle in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours. The bullets, the laser and the sparks are effects；⑤ the oversized teal-blue coat with its silver tube, the yellow tank top with the lightning print, the red-brown belt, the two spiky hair buns and the bit of yellow battery backpack stay on her in every frame, the same shapes and sizes as in the design (the coat's hem may swing behind her in the run and the hop, as one piece, its shape the same)。
> - **子弹、电脉冲、激光、电光都是特效（第 3 步单独画）**：枪口不画火光。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**，或者像上次辛德拉那样**把造型图切成部件（头、握枪手臂 + 步枪、另一只手臂、外套身体、两条腿）再拼动作**——但部件只能平移和 90° 整转 / 翻转，不能按任意角度转（会出锯齿和缺格）。生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/zeri-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧枪口的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`zeri_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词，或者用造型图的部件拼。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/zeri_palette.png`，或直接读 `design/zeri_design_1x.png`）。
4. **贴头**：把造型图的头（`design/zeri_head_1x.png` 里不透明的格子：两个发髻、刘海、脸、眼睛、创可贴；在 128×128 画布上的范围 x 50–70、y 64–78，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；跳起的帧整块往上挪；死亡倒地的帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `zeri_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/zeri_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/zeri_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头、切部件 |
| `design/zeri_head.png`、`_1x.png` | 要贴进每一帧的头（发髻、刘海、脸） | 贴头 |
| `design/zeri_palette.png` | 造型图的全部 19 色（暗到亮） | 色板 |
| `zeri_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/zeri_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/zeri_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `zeri_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/zeri_picture.png`、`refs/zeri_draft_codex.png` | 用户选的原画 A 和你上一轮的造型（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 19 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点，**不要在脸上和身上留零散的黑格**；外轮廓 1 格近黑描边。
- **腿**：the legs are the design's own legs - the dark maroon leggings with the round knee pad, the brown ankle boots with orange socks, legs apart - square for square in every frame but the run, E's hop and the death; a cast may move the WHOLE figure 1-2 squares forward, back or up (a lean or a step of the whole body), never the upper body alone over still legs. In the run she RUNS with clear steps (League's run): the legs move as rigid pieces (thigh+shin+boot), one forward while the other is back, the boots on the feet line when planted; the legs keep the design's own leg squares and colours (never flattened, squashed or missing squares)。
- **手臂**：the arms are the design's arms, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest). The image-RIGHT arm and the RIFLE it holds are ONE rigid piece: upright beside her head in the idle; to shoot it turns as a whole by a QUARTER TURN (the rifle level, pointing to the image right at chest height) - never bent, never turned by an odd angle, never shifted row by row; the image-LEFT arm hangs as in the design or comes up as one rigid piece to steady the rifle. The hands (the maroon fingerless glove) are NEVER hidden behind the body, the coat or the rifle in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours. The bullets, the laser and the sparks are effects。
- **身上**：the oversized teal-blue coat with its silver tube, the yellow tank top with the lightning print, the red-brown belt, the two spiky hair buns and the bit of yellow battery backpack stay on her in every frame, the same shapes and sizes as in the design (the coat's hem may swing behind her in the run and the hop, as one piece, its shape the same)。
- **头每帧都是造型图的头**（发髻、刘海、脸逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条）。
- **跑动循环**：每帧头相对站位点的横向位置不变；迈步跑，腿整块摆动；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不趴在地上**。**只画角色本身**：子弹、脉冲、激光、电光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/zeri_design.png`，第二张 `now/zeri_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `zeri_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same two spiky hair buns (dark teal-blue spikes, lime yellow-green hair), the yellow-green eyes and the cheek plaster, the oversized teal-blue coat with the silver tube, the yellow tank top with the lightning print, the red-brown belt, the dark maroon leggings with the knee pad, the brown boots with orange socks, the maroon fingerless glove, the lime yellow and orange rifle, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms and the body from it, but keep the FIRST image's proportions and, in every frame but the run, E's hop and the death, the FIRST image's own body and legs; every cast goes to the RIGHT of the image; never draw her from the back, upside down or lying flat on the ground (except the death).
The character: Zeri, the Spark of Zaun (a lively street girl with spiky hair buns, an oversized coat and an electric rifle).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 19 colors of the FIRST image, no new colors: #100C14 #3E1838 #5A2E1E #0E3E66 #A8261E #6A2A5A #8A4A30 #7A9A08 #1670A0 #E0287A #22A0C8 #C8784A #B4E01E #F6A418 #F6C21E #F2B47E #E8FA5A #C8CCD6 #F2F4F8. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added, no stray black squares on the face or the body.
The body is the idle body: in every frame but the run, E's hop and the death the coat, the tank top and belt, the hair buns and the legs keep the FIRST image's shapes and sizes square for square; only the arms move, and the whole figure may lean or move 1-3 squares.
Legs: the legs are the design's own legs - the dark maroon leggings with the round knee pad, the brown ankle boots with orange socks, legs apart - square for square in every frame but the run, E's hop and the death; a cast may move the WHOLE figure 1-2 squares forward, back or up (a lean or a step of the whole body), never the upper body alone over still legs. In the run she RUNS with clear steps (League's run): the legs move as rigid pieces (thigh+shin+boot), one forward while the other is back, the boots on the feet line when planted; the legs keep the design's own leg squares and colours (never flattened, squashed or missing squares).
The arms: the arms are the design's arms, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest). The image-RIGHT arm and the RIFLE it holds are ONE rigid piece: upright beside her head in the idle; to shoot it turns as a whole by a QUARTER TURN (the rifle level, pointing to the image right at chest height) - never bent, never turned by an odd angle, never shifted row by row; the image-LEFT arm hangs as in the design or comes up as one rigid piece to steady the rifle. The hands (the maroon fingerless glove) are NEVER hidden behind the body, the coat or the rifle in any frame and keep the design's size and colours; where an arm moves away, the body behind it is filled with the body's own colours. The bullets, the laser and the sparks are effects.
The body parts: the oversized teal-blue coat with its silver tube, the yellow tank top with the lightning print, the red-brown belt, the two spiky hair buns and the bit of yellow battery backpack stay on her in every frame, the same shapes and sizes as in the design (the coat's hem may swing behind her in the run and the hop, as one piece, its shape the same).
The head (the hair buns, the bangs, the face with the yellow-green eyes and the plaster) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the death frames where she lies on her back is it turned 90 degrees with the whole body). Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell her soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in zeri_cells.json). In the run her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (bullets, muzzle flashes, the pulse, the laser, lightning, sparks, glows) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 80x72 squares (640x576 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the rifle arm one rigid piece turned only by quarter turns, the hands never behind the body, the coat or the rifle, the frames but the run, E's hop and the death on the FIRST image's own body and legs, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；握枪的手臂和步枪是一整块，开枪时整块转 90° 端平。
3. 长相、配色、细节全部换成图2：两个尖刺发髻（深青蓝尖刺 + 柠檬黄绿）、黄绿眼睛、创可贴、青蓝外套和银管、黄背心闪电、红棕皮带、深紫红紧身裤和护膝、棕靴橙袜口、紫红半指手套、柠檬黄 + 橙色步枪。
4. 手臂从肩膀外侧长出来，手任何一帧都不能藏在身体、外套或步枪后面；枪口不画火光（子弹、电光是特效）；脸上身上不要零散的黑格。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `zeri_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，1920×1152 | 第 59 行 | **已做好，不用画** |
| `zeri_run.png`（跑动（迈步）） | 8 帧：107 107 107 107 107 107 107 106 | — | 4 列 × 2 行，2560×1152 | 第 59 行 | `RUN, 8 frames, one seamless loop (League's run, 0.85 s): she runs to the image right, the body leaning a little forward, the rifle held upright beside her head (the rifle arm as in the design), the other arm swinging as one rigid piece; clear steps: frames 1 and 5 the two strides (one leg forward, one back), frames 3 and 7 the legs passing; the coat's hem swings behind; the whole figure bobs 1 row (up in the passing frames); her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into 1.` |
| `zeri_attack.png`（普攻 电火迸射（枪整块转平、连射）） | 5 帧：67 66 100 84 83 | 第 3 帧（tick 8） | 3 列 × 2 行，1920×1152，最后 1 格空 | 第 59 行 | `BURST FIRE (her attack: seven rounds from the rifle), 5 frames: 1 the design's stance; 2 the rifle arm turned a QUARTER TURN as one piece so the rifle is level, pointing to the image right at chest height, the other hand coming up under it; 3 THE BURST (the rounds leave here): the rifle level, the whole figure pushed back 1 square by the recoil; 4 the rifle level, the figure back in place; 5 the rifle turned back upright: the design's stance. The rounds and the muzzle flash are effects.` |
| `zeri_skill.png`（W 强穿激光（端平、蓄力、发射）） | 5 帧：90 90 87 117 116 | 第 4 帧（tick 16） | 3 列 × 2 行，1920×1152，最后 1 格空 | 第 59 行 | `ULTRASHOCK LASER (W, an electric pulse), 5 frames: 1 the rifle raised a little higher, charging; 2 the rifle arm turned a QUARTER TURN as one piece, the rifle level at the image right, the other hand under it, the legs braced 1 square wider; 3 holding the aim, the body leaning back 1 square; 4 THE PULSE (fired here): the rifle level, the whole figure jolted back 1-2 squares; 5 back to the design's stance. The pulse and the laser are effects.` |
| `zeri_skill2.png`（E 灿丽花火（向前冲刺）） | 4 × 75 | — | 4 列 × 1 行，2560×576 | 第 59 行 | `SPARK SURGE (E, a short electric dash forward), 4 frames: 1 crouching 1 row, the rifle upright; 2 THE DASH: the whole figure leaning forward low, both legs pushed back (a sprint pose, legs as rigid pieces), the coat streaming behind; 3 landing, one leg forward; 4 back to the design's stance. The electric trail is an effect.` |
| `zeri_skill2_back.png`（E 向后跳开） | 4 × 75 | — | 4 列 × 1 行，2560×576 | 第 59 行 | `SPARK SURGE BACK (E, a short hop backward away from a threat), 4 frames: 1 crouching 1 row; 2 THE HOP: the whole figure 2 rows up and leaning back, the knees bent, the rifle upright; 3 landing 1 row low, one leg back; 4 back to the design's stance. The trail is an effect.` |
| `zeri_ult.png`（R 超限爆闪（跃起、落地电新星）） | 4 帧：75 75 90 93 | 第 3 帧（tick 9） | 4 列 × 1 行，2560×576 | 第 59 行 | `LIGHTNING CRASH (R), 4 frames: 1 crouching 1 row, the rifle upright, the free hand clenched; 2 springing 1-2 rows up, both arms flung out (the rifle arm as one piece, the rifle upright), the coat flaring; 3 THE NOVA (the burst of electricity goes here): landing in a wide stance, the free arm thrust down, the hair buns standing up; 4 back to the design's stance. The nova and the electricity are effects.` |
| `zeri_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1280×576 | 第 59 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left); 2 recovering toward the design's stance. The design's legs.` |
| `zeri_dead.png`（死亡（后仰倒地）） | 8 帧：100 100 100 120 150 200 300 400 | — | 4 列 × 2 行，2560×1152 | 第 59 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 her knees giving way, sinking 2 rows, the rifle arm falling; 3 the WHOLE body (legs and hair buns included, as one piece) tipping over backward, turned 45 degrees; 4 turned 90 degrees, lying on her back on the ground, the rifle beside her; 5-8 the same as 4, still. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点和零散黑格；
- [ ] 待机姿态时和造型图一样大；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（外套、背心皮带、发髻、腿）和造型图一样；两只手臂都在、和造型图一样粗、从肩膀外侧长出来；握枪手臂 + 步枪整块、只做 90° 整转；手没有被挡住；
- [ ] 跑动迈步、腿整块摆、颜色和待机一样、没有缺格子；
- [ ] 脚底线以下没有任何像素；黑边干净；
- [ ] 没有背影、没有倒立、没有趴在地上；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效（子弹、火光、激光、电光）、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `zeri_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂 + 步枪整块 90° 转，整个人前倾后仰）。
- 放进 `assets/source/native/`，`zeri_cells.json` 用包里这份，`zeri_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；红色方：有前后之分、贴在她身上的特效（枪口火光）烘进动作帧（`zeri_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick 8、W tick 16、R tick 9），量头像截取点，重跑模拟，做预览 GIF。
