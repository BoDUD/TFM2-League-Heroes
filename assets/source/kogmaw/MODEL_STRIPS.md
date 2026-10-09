# 克格莫：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/kogmaw_design.png`（放大 8 倍，1024×1024）：触角尖到脚底 38 行，43 格宽，20 色；脚底在第 99 行，两脚中间在第 64 列。这张是在你上一轮生图原稿（`refs/kogmaw_draft_codex.png`）的基础上按格子读回、整行整列删到 38 行整理出来的，**造型图就是标准**：四根青蓝触角、象牙白骷髅骨板（两只大琥珀眼带白高光、右边缘一只小眼、骨喙）、獠牙大嘴（深红嘴唇和喉咙、橄榄黄边）、蓝色分节背甲和骨刺、青绿肚子、骨质小前爪、两只蓝色大爪脚、带骨刺的短尾巴。颜色、明暗每一帧都照它，只改姿势。
> - **待机条已经做好**（`kogmaw_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - **跑步单独做，用「骨架 + 皮囊」**：`run_swap/` 里 图1 = oppi 画的克格莫跑步（同一个英雄，动作骨架，8 帧），图2 = 定稿造型（皮囊），照 `run_swap/PROMPT.md` 的中文提示词画，交 `kogmaw_run.png`，排版和图1一样。**两只脚一定要轮流抬起，两只脚颜色一样**。
> - 其余 6 张动作图按下面的表画：帧数、每帧时长、出手帧和站位照 `now/kogmaw_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体、头和嘴的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。`refs/oppi/` 里有 oppi 画的同一个英雄的动作（游戏尺寸），想看小尺寸下怎么画时参考，**只看动作，不要照它的长相和颜色**（特别是普攻的嘴管、R 的站起来朝天）。
> - **和参考图不一样、以造型图为准的地方**：① 照造型图的比例（骷髅脸和大嘴大、身体圆、腿短脚大）；② 头（触角 + 骨板 + 眼睛 + 骨喙）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**（只有 R 站起来朝天那几帧骨板向后仰），**不画背影**——英雄联盟的 E 是背对镜头趴下，我们不要；③ **嘴**：the MOUTH is the only part that changes shape: in the idle stance it is the design's round open mouth (a ring of ivory fangs, crimson lips, a dark crimson throat, the thin olive rim); when he spits it STRETCHES into a fleshy crimson-magenta TUBE (2-4 squares thick, the design's crimson shades, a ring of small fang squares at its wide open end) that pushes forward out of the mouth, as in League and in refs/oppi/；④ **腿和脚**：in every frame where he squats or stands (attack, Q, E, hit) he stands on the design's OWN two stubby legs and BIG blue clawed feet square for square: the same place, the same width apart, the same plated toes - never spread, never longer, never thinner (a cast may move the WHOLE figure, feet included, 1-2 squares forward or back, never the body alone sliding over still feet). In R (rearing up on his hind legs) the legs straighten under the raised body but stay the design's legs: the same blue plates, the same big feet flat on the feet line；⑤ 身体：the blue segmented pill-bug shell with its bone-tan spikes (the dome at the image left), the teal belly under it, the two little bony fore-claws under the jaw, and the short thick tail with its bone spikes sticking out at the image left stay in every frame。
> - 出招方向：**普攻、Q 的嘴管都朝图的右边**，E 朝右下方的地面喷，R 嘴管朝正上方（游戏里朝左时会整张镜像）。
> - **死亡**：趴倒在地、触角耷拉、眼睛闭上；虚空形态离体和紫绿光是第 3 步的特效，不要画（见表）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/kogmaw_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/kogmaw_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/kogmaw-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧嘴管口的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`kogmaw_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/kogmaw_palette.png`，或直接读 `design/kogmaw_design_1x.png`）。眼睛的橙色（#FD5001）和白高光（#FCFBFC）**只用在眼睛上**。
4. **贴头**：把造型图的头（`design/kogmaw_head_1x.png` 里不透明的格子：四根触角、骷髅骨板和骨刺、两只大眼和右边的小眼、骨喙；在 128×128 画布上的范围 x 60–85、y 62–81，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；R 第 3–7 帧和死亡第 3–8 帧除外）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的触角或描边。**嘴不贴**（它要张合、伸成管子），嘴要接在骨板下面，不留空隙。
5. 对位：每帧按 `kogmaw_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/kogmaw_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/kogmaw_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/kogmaw_head.png`、`_1x.png` | 要贴进每一帧的头（触角、骨板、眼睛、骨喙；不含嘴） | 贴头 |
| `design/kogmaw_palette.png` | 造型图的全部 20 色（暗到亮） | 色板 |
| `kogmaw_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `run_swap/` | 跑步的骨架（oppi 的克格莫跑步，已按我们的大小放好）、皮囊（定稿）和中文提示词 | **跑步照这里画** |
| `now/kogmaw_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体、头和嘴的动作 |
| `guide/kogmaw_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `kogmaw_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/oppi/oppi_<动作>.png` | oppi 画的同一个英雄的动作（游戏尺寸 ×6）：普攻、Q、R、死亡 | **只看小尺寸下的动作**，长相颜色以定稿为准 |
| `refs/kogmaw_picture.png`、`refs/kogmaw_draft_codex.png` | 用户选的原画 A 和你上一轮的生图原稿（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 20 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **嘴**：the MOUTH is the only part that changes shape: in the idle stance it is the design's round open mouth (a ring of ivory fangs, crimson lips, a dark crimson throat, the thin olive rim); when he spits it STRETCHES into a fleshy crimson-magenta TUBE (2-4 squares thick, the design's crimson shades, a ring of small fang squares at its wide open end) that pushes forward out of the mouth, as in League and in refs/oppi/。
- **腿和脚**：in every frame where he squats or stands (attack, Q, E, hit) he stands on the design's OWN two stubby legs and BIG blue clawed feet square for square: the same place, the same width apart, the same plated toes - never spread, never longer, never thinner (a cast may move the WHOLE figure, feet included, 1-2 squares forward or back, never the body alone sliding over still feet). In R (rearing up on his hind legs) the legs straighten under the raised body but stay the design's legs: the same blue plates, the same big feet flat on the feet line。
- **身体**：the blue segmented pill-bug shell with its bone-tan spikes (the dome at the image left), the teal belly under it, the two little bony fore-claws under the jaw, and the short thick tail with its bone spikes sticking out at the image left stay in every frame。
- **头每帧都是造型图的头**（触角、骨板、眼睛、骨喙逐格一样），只平移（R 站起来朝天、死亡趴倒时例外）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），**不画背影、不画倒立**。**只画角色**：口水弹、淤泥、炮弹、虚空形态、光效都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`，他身上有青绿色，不能用绿底）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（普攻、Q、E、R、受击、死亡都用这一段，只替换中括号）

每张附三张图：第一张 `design/kogmaw_design.png`，第二张 `now/kogmaw_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `kogmaw_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the four cyan-tipped antennae, the ivory skull plate with its spikes, the two big amber eyes with white glints and the small eye at the skull's right edge, the beak-snout, the big fanged mouth with crimson lips and the olive rim, the blue segmented shell with bone spikes, the teal belly, the little bony fore-claws, the two big blue clawed feet, the short spiky tail, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the head and the mouth from it, but keep the FIRST image's proportions (the big skull and mouth, the round body, short legs, big feet) and the FIRST image's own feet; never draw him from the back or upside down.
The character: Kog'Maw, the Mouth of the Abyss (a round void creature with an ivory skull face, a huge fanged mouth, four antennae and a blue shell).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (38 squares from the antennae's tips to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 20 colors of the FIRST image, no new colors: #030312 #130B0A #440917 #600125 #404805 #025A6B #950132 #1931EA #15979F #FD5001 #A3A708 #FB124C #155FFC #1A83FD #BC9972 #00E4FD #E7C18D #D2E2FC #FDEEC9 #FCFBFC. The eye colors (the orange #FD5001 and the white glint #FCFBFC) only in the eyes. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The mouth: the MOUTH is the only part that changes shape: in the idle stance it is the design's round open mouth (a ring of ivory fangs, crimson lips, a dark crimson throat, the thin olive rim); when he spits it STRETCHES into a fleshy crimson-magenta TUBE (2-4 squares thick, the design's crimson shades, a ring of small fang squares at its wide open end) that pushes forward out of the mouth, as in League and in refs/oppi/.
Legs and feet: in every frame where he squats or stands (attack, Q, E, hit) he stands on the design's OWN two stubby legs and BIG blue clawed feet square for square: the same place, the same width apart, the same plated toes - never spread, never longer, never thinner (a cast may move the WHOLE figure, feet included, 1-2 squares forward or back, never the body alone sliding over still feet). In R (rearing up on his hind legs) the legs straighten under the raised body but stay the design's legs: the same blue plates, the same big feet flat on the feet line.
The body: the blue segmented pill-bug shell with its bone-tan spikes (the dome at the image left), the teal belly under it, the two little bony fore-claws under the jaw, and the short thick tail with its bone spikes sticking out at the image left stay in every frame.
The head (the four antennae, the skull plate with its spikes, the eyes and the beak-snout - NOT the mouth) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash or tilt it, or it flickers when the frames play - except in R frames 3-7, where he rears up and the skull is tipped back so the mouth points up, and the death frames 3-8, where he lies flat. Erase your own head before pasting it, so no extra antenna or outline is left beside it; the mouth hangs right under the skull - no gap.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in kogmaw_cells.json).
3/4 front view like the FIRST image; the attack's and Q's tube points to the RIGHT of the image, E's spew at the ground in front of him on the right, R's tube straight UP; never his back, never upside down. Do not draw effects (the spit glob, the spittle, the ooze, the artillery shell, the void form, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame (except R 3-7 and death 3-8), the mouth or the tube under it, the shell, belly, fore-claws, both feet and the tail in every frame, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：身体、头和嘴的方向和姿势照图1，不转成背影；脚用图2自己的两只蓝色大爪脚，平放在脚底线上。
3. 长相、配色、细节全部换成图2：四根青蓝触角、象牙白骷髅骨板（两只大琥珀眼带白高光、右边小眼、骨喙）、獠牙大嘴（深红嘴唇、橄榄黄边，吐东西时伸成深红色肉管）、蓝色分节背甲和骨刺、青绿肚子、骨质小前爪、带骨刺的短尾巴。头（触角 + 骨板 + 眼睛）每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯品红色 #FF00FF，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `kogmaw_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1280 | 第 65 行 | **已做好，不用画** |
| `kogmaw_run.png`（跑步（在 run_swap/ 换皮）） | 8 × 89 | — | 4 列 × 2 行，3072×1280 | 第 65 行 | **不用这一行：用 `run_swap/` 的换皮画** |
| `kogmaw_attack.png`（普攻（伸出嘴管吐一口）） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1280 | 第 65 行 | `BASIC ATTACK (League's: he rears back, then thrusts his head forward and his mouth stretches into a tube that spits a glob), 6 frames: 1 the head and body pulled back a little, the mouth closing; 2 rearing, the head drawn back and up, the antennae swept back; 3 THE SPIT (the glob leaves here): the head thrust forward and down to the right, the mouth stretched into the crimson TUBE pointing forward-right, 6-9 squares long, its open end at the right; 4 the tube still out, a little shorter; 5 the tube pulled back into the mouth; 6 back toward the idle stance. The glob is an effect - do not draw it.` |
| `kogmaw_skill.png`（Q 腐蚀唾液（后仰再长长地伸管喷出）） | 8 帧：70 70 60 70 80 80 80 80 | 第 5 帧（tick 16） | 4 列 × 2 行，3072×1280 | 第 65 行 | `CAUSTIC SPITTLE (Q; League's Q: a bigger, harder spit), 8 frames: 1 he rears up, the skull turned toward the viewer, the mouth wide open; 2 the head drawn back, the cheeks puffed, the antennae swept back; 3 the body coiling, the head low; 4 lunging forward; 5 THE SPIT (the spittle leaves here): the head thrust forward, the mouth stretched into a LONG crimson TUBE straight forward to the right, 9-12 squares long; 6 the tube still out, recoiling; 7 the tube pulled back, the mouth open; 8 back toward the idle stance. The spittle is an effect - do not draw it.` |
| `kogmaw_skill2.png`（E 虚空淤泥（趴低朝地面喷淤泥）） | 8 帧：70 70 80 80 90 90 90 80 | 第 4 帧（tick 13） | 4 列 × 2 行，3072×1280 | 第 65 行 | `VOID OOZE (E; League's E: he hunches low and spews a stream of ooze along the ground), 8 frames: 1 hunching, the head lowered; 2 crouching lower, the shell arched up; 3 pressed low to the ground, the skull tipped DOWN toward the ground at the right, the mouth open wide toward the ground in front of him; 4 THE SPEW (the ooze leaves here): the same low pose, the mouth gaping at the ground, the whole body pushed 1 square forward; 5 still low, spewing; 6 rising, the head coming up; 7 the head up, the mouth open; 8 back toward the idle stance. Keep his skull, both amber eyes and the mouth visible in 3/4 view in every frame - League's model turns its back to the camera here, do NOT draw his back. The ooze is an effect - do not draw it.` |
| `kogmaw_ult.png`（R 活体大炮（后腿站起、嘴管朝天开炮）） | 8 帧：70 70 70 70 80 90 90 80 | 第 5 帧（tick 17） | 4 列 × 2 行，3072×1280 | 第 65 行 | `LIVING ARTILLERY (R; League's R: he rears up on his hind legs and fires a shell straight up out of a long tube), 8 frames: 1 lifting the head; 2 rising, the chest and belly turned toward the viewer; 3 rearing up on the hind legs, the body upright, the skull tipped BACK so the mouth points UP; 4 the mouth stretched into the crimson TUBE pointing straight UP, 8-12 squares tall (its top may touch the top of the cell); 5 THE SHOT (the shell leaves here): the tube at its tallest; 6 the tube shrinking back; 7 coming down, the skull turning forward again; 8 back toward the idle stance. Here the skull is the design's skull TILTED back (the eyes still visible), not the pasted head; the shell, belly, legs and tail as in the design. The shell is an effect - do not draw it.` |
| `kogmaw_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×640 | 第 65 行 | `HIT, 2 frames: 1 jolted back by a blow: the whole body pushed back 1-2 squares (to the left), the head flinching back a little, the antennae swept back, the mouth open; 2 recovering toward the idle stance. The design's legs and feet.` |
| `kogmaw_dead.png`（死亡（趴倒在地，虚空形态离体是特效）） | 8 帧：100 100 120 120 150 150 200 500 | — | 4 列 × 2 行，3072×1280 | 第 65 行 | `DEATH (Icathian Surprise: he collapses, then his void form leaves the body - the form and its glow are effects drawn separately), 8 frames: 1 struck, he jolts back, the mouth gaping; 2 his legs buckle, the body sinking; 3 collapsed flat on his belly on the ground, the skull resting on the ground at the right, the antennae drooping forward; 4 the same, the antennae limp and bent down, the eyes half closed (one row of each eye dark); 5-8 the same lying pose, still (the eyes closed: a dark line). Nothing below the feet line. Never his back, never on his back.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样（跑步和 `run_swap/1_动作骨架_oppi克格莫跑步.png` 一样），帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；眼睛的橙色和白高光只在眼睛里；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；R 站起来和死亡趴倒除外），头旁边没有多余的触角和描边，嘴紧接在骨板下面；
- [ ] 每帧都有背甲和骨刺、青绿肚子、小前爪、两只大爪脚、尾巴；吐东西的帧嘴伸成深红肉管；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；普攻和 Q 的嘴管朝图的右边，E 朝右下方地面，R 朝正上方；
- [ ] 跑步：两只脚轮流抬起、颜色一样，头的横向位置每帧差不多，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `kogmaw_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、脚和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`kogmaw_cells.json` 用包里这份（跑步用 `run_swap/run_layout.json`，8 × 89 毫秒），`kogmaw_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 7、Q tick 16、E tick 13、R tick 17），量头像截取点，重跑模拟，做预览 GIF。
