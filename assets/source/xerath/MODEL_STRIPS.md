# 泽拉斯：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/xerath_design.png`（放大 8 倍，1024×1024；兜帽顶到腿尖 44 行，31 格宽，23 色；近侧腿尖在第 99 行，站位点在第 64 列）。它是你上一轮的生图原稿 B（`refs/xerath_draft_codex.png`）按格子读回、整行整列删到 44 行的版本（每一格都是原稿的像素），用户选的「B44 宽」。**造型图就是标准**：圆顶石兜帽和开口里两只白色三角眼、两块带尖刺的紫灰肩甲、胸前的铁链和金色五边形封印（橙色符文）、石板之间发光的青色能量身体、手臂石板和蓝色能量爪、两条一节节变细的尖腿（没有脚，悬浮），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`xerath_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/xerath_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **放技能时的身体就是待机的身体**（同一套像素）：石板、能量、肩甲、铁链、封印的形状和大小不能变，只动手臂；整个人可以前倾后仰、前后挪 1–2 格（不要太大）。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（44 行高，头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 兜帽和两只眼睛**，**不画背影**；③ **腿**：he has NO feet and floats: the two legs are the design's own stacked stone plates tapering to two points, square for square in every standing frame (idle, the attack, Q, E and W, R, hit) - never spread, crossed, shortened or given feet; the near leg's tip stays on the feet line, the far one two rows higher, as in the design; a cast may move the WHOLE figure, legs included, 1-2 squares forward or back (a lean of the whole body), never the upper body alone over still legs; only the run (gliding, the legs trailing a little back) and the death (the armour falls apart) change them；④ 手臂：the arms are the design's arms: a stone plate on the upper arm and on the forearm, the glowing energy between, and the azure-blue clawed hand of energy - the same thickness and the same hand size as in the design in every frame, never thinner, never 1-pixel sticks, never floating hands; the spiked pauldrons stay on his shoulders；⑤ the glowing energy between the stone plates, the iron chains and the gold pentagon seal with its orange rune stay on him in every frame; the energy keeps the design's bright cyan shades。
> - 出招方向：**甩法球、推光束都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/xerath_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/xerath_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/xerath-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧前手爪子的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`xerath_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/xerath_palette.png`，或直接读 `design/xerath_design_1x.png`）。
4. **贴头**：把造型图的头（`design/xerath_head_1x.png` 里不透明的格子：兜帽、竖棱、下沿亮边、开口里的能量脸和两只眼睛；不含两边的肩甲；在 128×128 画布上的范围 x 54–74、y 56–68，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `xerath_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），近侧腿尖落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/xerath_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/xerath_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/xerath_head.png`、`_1x.png` | 要贴进每一帧的头（兜帽、能量脸、两只眼睛） | 贴头 |
| `design/xerath_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `xerath_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/xerath_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/xerath_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `xerath_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/xerath_picture.png`、`refs/xerath_draft_codex.png` | 用户选的原画 A 和你的生图原稿 B（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（兜帽顶到腿尖 44 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：he has NO feet and floats: the two legs are the design's own stacked stone plates tapering to two points, square for square in every standing frame (idle, the attack, Q, E and W, R, hit) - never spread, crossed, shortened or given feet; the near leg's tip stays on the feet line, the far one two rows higher, as in the design; a cast may move the WHOLE figure, legs included, 1-2 squares forward or back (a lean of the whole body), never the upper body alone over still legs; only the run (gliding, the legs trailing a little back) and the death (the armour falls apart) change them。
- **手臂**：the arms are the design's arms: a stone plate on the upper arm and on the forearm, the glowing energy between, and the azure-blue clawed hand of energy - the same thickness and the same hand size as in the design in every frame, never thinner, never 1-pixel sticks, never floating hands; the spiked pauldrons stay on his shoulders。
- **身上**：the glowing energy between the stone plates, the iron chains and the gold pentagon seal with its orange rune stay on him in every frame; the energy keeps the design's bright cyan shades。
- **头每帧都是造型图的头**（兜帽、亮边、能量脸、两只眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条）。
- **跑步循环**：每帧头相对站位点的横向位置不变；悬浮滑行，两条尖腿一起往后飘，不迈步；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色本身**：法球、光束、毁灭之眼、炮击、飞升的符文和光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/xerath_design.png`，第二张 `now/xerath_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `xerath_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, armour and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same rounded purple-grey stone hood with the glowing face and the two white triangular eyes, the two spiked purple-grey pauldrons, the iron chains and the gold pentagon seal with its orange rune, the glowing cyan energy body between the stone plates, the stone plates on the arms with the azure-blue clawed hands, the two pointed stone legs with no feet, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms and the body from it, but keep the FIRST image's proportions (44 squares tall, a big hood) and, in every standing frame, the FIRST image's own body and legs; never draw him from the back or upside down.
The character: Xerath, the Magus Ascendant (a floating sorcerer of glowing arcane energy bound in purple-grey stone armour plates, with a hood, chains and a gold seal).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares from the top of the hood to the near leg's tip in the idle pose), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #040208 #023439 #000A6E #320F41 #003C59 #4D1E62 #016FA8 #755086 #B0A208 #8545A2 #838282 #0090F9 #019CEF #FBA802 #9A59BB #01B3FB #01D8FA #FEF204 #01F8FC #D5D4D4 #DFA9FA #E0B2F8 #FBFCFC. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every standing frame the stone plates, the energy between them, the pauldrons, the chains and the seal keep the FIRST image's shapes and sizes square for square; only the arms move, and the whole figure may lean or move 1-2 squares.
Legs: he has NO feet and floats: the two legs are the design's own stacked stone plates tapering to two points, square for square in every standing frame (idle, the attack, Q, E and W, R, hit) - never spread, crossed, shortened or given feet; the near leg's tip stays on the feet line, the far one two rows higher, as in the design; a cast may move the WHOLE figure, legs included, 1-2 squares forward or back (a lean of the whole body), never the upper body alone over still legs; only the run (gliding, the legs trailing a little back) and the death (the armour falls apart) change them.
The arms: the arms are the design's arms: a stone plate on the upper arm and on the forearm, the glowing energy between, and the azure-blue clawed hand of energy - the same thickness and the same hand size as in the design in every frame, never thinner, never 1-pixel sticks, never floating hands; the spiked pauldrons stay on his shoulders.
The armour: the glowing energy between the stone plates, the iron chains and the gold pentagon seal with its orange rune stay on him in every frame; the energy keeps the design's bright cyan shades.
The head (the hood with its ridge and rim, the glowing face and the two eyes) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell the near leg's tip is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in xerath_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every throw and every beam goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (orbs, beams, the eye, shells, runes, glows beyond the body's own energy) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms with their plates and claws in every frame, the standing frames on the FIRST image's own body and legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂和身体的方向和姿势照图1；身体和两条尖腿用图2自己的（悬浮，没有脚）。
3. 长相、配色、细节全部换成图2：圆顶石兜帽和两只白色三角眼、带尖刺的紫灰肩甲、铁链和金色五边形封印、石板之间发光的青色能量、手臂石板和蓝色能量爪、两条变细的尖腿。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `xerath_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `xerath_run.png`（跑步（悬浮滑行）） | 8 × 121 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, a 1.0 s glide): he floats forward, the body leaning a little forward, bobbing up and down at most 1 square; the two pointed legs trail a little back, swaying together (they never step); the arms hang a little back with the claws trailing; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `xerath_attack.png`（普攻（甩出法球）） | 6 帧：60 60 50 90 100 107 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (he flings an arcane orb), 6 frames: 1 the front arm (image right) drawn back and up beside his head, the claw open; 2 drawn further back, the body leaning back a little; 3 swinging forward; 4 THE THROW (the orb leaves here): the front arm thrust forward to the image right at chest height, the claw open, the body leaning forward 1 square; 5 holding the follow-through; 6 back toward the idle stance. The orb is an effect - do not draw it. Legs: the design's legs.` |
| `xerath_skill.png`（Q 奥能脉冲（完整蓄力）） | 7 帧：150 150 150 150 300 100 67 | 第 6 帧（tick 54） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `ARCANOPULSE, FULL CHARGE (Q), 7 frames: 1-4 the charge: both arms raised, the back arm high above his head with the claw open upward, the front arm raised forward-up, the body leaning back a little, holding it (frames 3 and 4 almost the same, a 1-square sway); 5 the longest frame, still charging, the arms at their highest; 6 THE RELEASE (the beam goes out here): the front arm thrust straight forward to the image right at chest height, the claw open, palm out, the body leaning forward 1-2 squares; 7 back toward the idle stance. The gathering light and the beam are effects. Legs: the design's legs.` |
| `xerath_skill_quick.png`（Q 奥能脉冲（快速蓄力）） | 5 帧：120 120 127 100 66 | 第 4 帧（tick 22） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `ARCANOPULSE, QUICK CHARGE (Q against minions), 5 frames: the same motion as the full charge, shorter: 1-2 the arms raised (back arm up, front arm forward-up), 3 the highest; 4 THE RELEASE: the front arm thrust straight forward to the image right; 5 back toward the idle stance. Legs: the design's legs.` |
| `xerath_skill2.png`（E 冲击法球 + W 毁灭之眼） | 6 帧：80 87 80 83 90 80 | 第 3 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `SHOCKING ORB then EYE OF DESTRUCTION (E then W), 6 frames: 1 the front arm pulled back beside his chest, the body turning a little back; 2 winding up; 3 THE THROW (the orb leaves here): the front arm swung forward to the image right, the claw open, the body leaning forward 1-2 squares; 4 the follow-through; 5 BOTH arms raised high above his head, the claws open upward (calling the eye down); 6 back toward the idle stance. The orb and the eye are effects. Legs: the design's legs.` |
| `xerath_ult.png`（R 奥术仪式（起手飞升）） | 5 × 100 | — | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `RITE OF THE ARCANE, the start (R, 0.5 s), 5 frames: 1 the arms coming up from his sides; 2-4 BOTH arms raised high above his head, the claws spread, the body stretching up a little (at most 1 square higher, the whole figure); 5 the arms coming down to the channel pose (see ult_loop frame 1). The rising runes and the floating armour shards are effects. Legs: the design's legs.` |
| `xerath_ult_loop.png`（R 引导循环） | 6 × 160 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | `RITE OF THE ARCANE, the channel loop (held while he calls the shells), 6 frames: the front arm stretched forward and a little up to the image right, the claw open, palm out; the back arm raised beside his head; the body still, swaying at most 1 square; frame 6 flows into frame 1. Legs: the design's legs.` |
| `xerath_ult_shot.png`（R 每一发炮击） | 3 帧：80 80 73 | 第 1 帧（tick 0） | 3 列 × 1 行，3072×768 | 第 81 行 | `RITE OF THE ARCANE, one shell (14 ticks), 3 frames: 1 THE SHOT: the front arm thrust forward-up to the image right, the claw spread, the body jolting forward 1 square; 2 holding it; 3 back to the channel pose of ult_loop frame 1. Legs: the design's legs.` |
| `xerath_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the arms flung a little out; 2 recovering toward the idle stance. The design's legs.` |
| `xerath_dead.png`（死亡（铠甲散落）） | 8 帧：100 110 120 130 150 200 300 400 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: the bound energy breaks free and the armour falls): 1 struck, he jerks back; 2-3 he rises a little and arches back, the arms flung out; 4 the energy flares, the plates starting to come apart; 5-6 the stone plates (the hood, the pauldrons, the arm and leg plates, the chains with the seal) fall to the ground as separate pieces, the energy body fading; 7-8 the empty armour lying in a heap of plates on the ground, the hood on top, its eyes dark; 7 and 8 the same. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（石板、能量、肩甲、铁链、封印）和造型图一样，两只手臂（石板 + 蓝爪）都在，和造型图一样粗；两条尖腿是造型图自己的腿；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `xerath_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂整块按 90° 转，整个人前倾后仰）。
- 放进 `assets/source/native/`，`xerath_cells.json` 用包里这份，`xerath_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 10、Q 完整蓄力 tick 54、E tick 10），量爪子出手点和头像截取点，重跑模拟，做预览 GIF。
