# 阿利斯塔：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/alistar_design.png`（放大 8 倍，1024×1024；鬃毛顶到蹄底 44 行，41 格宽，25 色；蹄底在第 99 行，两蹄中间在第 64 列）。它是你上一轮生图原稿 A-first（`refs/alistar_draft_codex.png`）按格子读回、2×2 减半的版本（只把两只红眼放到同一行、补了 2 格银鼻环）。**造型图就是标准**：蓝紫色皮肤和淡紫胸腹、粉色伤疤、青色尖鬃毛、象牙白大弯角（画面左边那只有铁箍）、红眼睛、银鼻环、两只很宽的断铁镣铐和断链、大手、棕色皮围裙和金扣、短粗的毛腿和黑色牛蹄，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`alistar_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/alistar_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（44 行高、头连角约占三分之一）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**，**不画背影**（死亡躺倒那几帧整头跟身体转 90°）；③ **腿**：in every standing frame (idle, attack, Q, W's headbutt, R, hit) he stands on the design's OWN short furry legs and dark hooves square for square - the same bent stance and width as the design, never spread wider, never crossed, never longer; the shoulders, the hump, the arms and the head move, the legs stay (a blow may move the WHOLE figure, legs included, 1-3 squares forward or back, never the upper body alone sliding over still legs); only the run steps, and only W's charge leans the whole body forward low (the design's legs bent a little more, the hips joined)；④ 装备：both very wide broken iron shackles stay on his wrists in every frame (dark iron, the bronze rim, the zig-zag line, the design's size), each with its broken chain; the silver nose ring, both ivory horns (the image-left one with its iron band), the cyan mane on his head and back and the brown loincloth with its gold stud stay on him in every frame；⑤ 手臂：the arms are the design's huge purple arms: as thick as in the design in every frame (the upper arms and forearms 5-7 squares wide, the hands big with 2-3 square fingers and grey nails) - never thinner, never 1-pixel sticks, never floating hands; a raised arm keeps its shackle at the wrist。
> - 出招方向：**拳头、冲撞都朝图的右边**（游戏里朝左时会整张镜像）。
> - **W 的第 5–6 帧会被剪出来单独播**（冲到敌人身上那一下头槌），**Q 的第 3–6 帧也会被剪出来单独播**（头槌之后接的砸地），所以这几帧要能直接接在待机后面。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/alistar_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/alistar_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/alistar-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧拳头的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`alistar_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/alistar_palette.png`，或直接读 `design/alistar_design_1x.png`）。
4. **贴头**：把造型图的头（`design/alistar_head_1x.png` 里不透明的格子：两只牛角、两角之间的鬃毛、脸、红眼、口鼻和鼻环；在 128×128 画布上的范围 x 62–84、y 66–83，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的角、鬃毛或描边。
5. 对位：每帧按 `alistar_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），蹄底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/alistar_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/alistar_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/alistar_head.png`、`_1x.png` | 要贴进每一帧的头（两只角、鬃毛、脸、红眼、口鼻、鼻环） | 贴头 |
| `design/alistar_palette.png` | 造型图的全部 25 色（暗到亮） | 色板 |
| `alistar_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/alistar_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/alistar_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `alistar_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/alistar_picture.png`、`refs/alistar_draft_codex.png` | 用户选的原画 A 和你的生图原稿 A-first（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（鬃毛顶到蹄底 44 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 25 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every standing frame (idle, attack, Q, W's headbutt, R, hit) he stands on the design's OWN short furry legs and dark hooves square for square - the same bent stance and width as the design, never spread wider, never crossed, never longer; the shoulders, the hump, the arms and the head move, the legs stay (a blow may move the WHOLE figure, legs included, 1-3 squares forward or back, never the upper body alone sliding over still legs); only the run steps, and only W's charge leans the whole body forward low (the design's legs bent a little more, the hips joined)。
- **装备**：both very wide broken iron shackles stay on his wrists in every frame (dark iron, the bronze rim, the zig-zag line, the design's size), each with its broken chain; the silver nose ring, both ivory horns (the image-left one with its iron band), the cyan mane on his head and back and the brown loincloth with its gold stud stay on him in every frame。
- **手臂**：the arms are the design's huge purple arms: as thick as in the design in every frame (the upper arms and forearms 5-7 squares wide, the hands big with 2-3 square fingers and grey nails) - never thinner, never 1-pixel sticks, never floating hands; a raised arm keeps its shackle at the wrist。
- **头每帧都是造型图的头**（两只角、鬃毛、脸、红眼、鼻环逐格一样），只平移。
- **蹄底线以下什么都不能有**（游戏在脚下画血条）。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的蹄子踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：冲击波、尘土、裂地、怒吼光环、眩晕星星都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/alistar_design.png`，第二张 `now/alistar_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `alistar_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, horns, mane, shackles and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same violet-purple skin with the lavender chest and the pink scars, the spiky cyan mane over the head and down the back, the two big ivory horns (the image-left one with an iron band), the red eyes, the silver nose ring, the two very wide broken iron shackles with their chains, the huge hands, the brown loincloth with the gold stud, the short furry legs and dark hooves, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the head and the body from it, but keep the FIRST image's proportions (44 squares tall, the head with the horns about a third of it) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Alistar, the Minotaur (a huge hunched bull-headed minotaur with violet skin, a cyan mane, ivory horns, a nose ring and broken iron shackles on his wrists).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares from the mane's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 25 colors of the FIRST image, no new colors: #120319 #150B4B #421714 #443A3F #3B1888 #873E28 #FB120D #0153D9 #5526C3 #C8672F #048AFC #A8826E #733DF5 #8E96A2 #18B8FB #F5B743 #9A63F3 #F47589 #E1B590 #56E1FD #BB88FB #FBD59B #D8DCE4 #C3FAFD #FAF1D6. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, attack, Q, W's headbutt, R, hit) he stands on the design's OWN short furry legs and dark hooves square for square - the same bent stance and width as the design, never spread wider, never crossed, never longer; the shoulders, the hump, the arms and the head move, the legs stay (a blow may move the WHOLE figure, legs included, 1-3 squares forward or back, never the upper body alone sliding over still legs); only the run steps, and only W's charge leans the whole body forward low (the design's legs bent a little more, the hips joined).
Gear: both very wide broken iron shackles stay on his wrists in every frame (dark iron, the bronze rim, the zig-zag line, the design's size), each with its broken chain; the silver nose ring, both ivory horns (the image-left one with its iron band), the cyan mane on his head and back and the brown loincloth with its gold stud stay on him in every frame.
The arms: the arms are the design's huge purple arms: as thick as in the design in every frame (the upper arms and forearms 5-7 squares wide, the hands big with 2-3 square fingers and grey nails) - never thinner, never 1-pixel sticks, never floating hands; a raised arm keeps its shackle at the wrist.
The head (both horns, the mane between them, the face, the red eyes, the snout and the nose ring) is COPIED from the FIRST image in every frame, square for square, and only moved (turned a quarter with the body only while he lies dead); never redraw, squash or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra horn, mane or outline is left beside it.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in alistar_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 front view like the FIRST image; every blow and the charge go to the RIGHT of the image; never his back, never upside down. Do not draw effects (shockwaves, cracks, dust, the roar aura, stun stars) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both shackles, both hands, the loincloth and both hooves in every frame, the arms as thick as in the FIRST image, the standing frames on the FIRST image's own legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、头、身体的方向和姿势照图1；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：蓝紫色皮肤和淡紫胸腹、青色尖鬃毛、象牙白大弯角、红眼睛、银鼻环、两只很宽的断铁镣铐和断链、大手、棕色皮围裙、短粗毛腿和黑色牛蹄。手臂和图2一样粗。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `alistar_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `alistar_run.png`（跑步） | 8 × 125 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.0 s a cycle): the heavy bull trots, the design's legs swing from the hips, left and right alternate (the leading hoof changes every half cycle, the hooves at most 12 squares apart), the planted hoof on the feet line; the body hunched as in the design, bobbing at most 1 square; the big arms swing a little forward and back opposite the legs, the chains swinging; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `alistar_attack.png`（普攻（单拳锤下）） | 6 帧：70 70 60 90 80 63 | 第 4 帧（tick 12） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (a hammer blow), 6 frames: 1 he rears up, both arms swinging out to the sides; 2 the near arm (image right) raised high, the fist clenched, the body twisting back; 3 the fist at the top of the swing behind his head; 4 THE HIT (the damage lands here): the near fist hammered down in front of him to the right at knee height, the whole figure lunging forward 2 squares; 5 the follow-through, the fist low; 6 back toward the idle stance. Legs: the design's legs.` |
| `alistar_skill.png`（Q 践踏接大地粉碎（双拳砸地）） | 6 帧：70 80 83 90 90 87 | 第 4 帧（tick 14） | 3 列 × 2 行，3072×1536 | 第 81 行 | `TRAMPLE + PULVERIZE (Q), 6 frames: 1 a stomp, he lifts the near hoof a little and rears up, both arms starting to rise; 2 both arms going up, the fists coming together; 3 BOTH FISTS clenched together high above his head, his chest open, the head up snorting; 4 THE SLAM (the knock-up lands here): both fists smashed down into the ground in front of him to the right, the body bent forward low, the head down between the shoulders; 5 holding the slam, the fists on the ground; 6 rising back toward the idle stance. The shockwave, the cracks and the dust are effects - do not draw them. Legs: the design's legs (frame 4-5 the knees bent a little more, the hooves where they are).` |
| `alistar_skill2.png`（W 野蛮冲撞（1–4 冲锋循环，5 一头顶上去）） | 6 帧：80 80 80 80 100 100 | 第 5 帧（tick 19） | 3 列 × 2 行，3072×1536 | 第 81 行 | `HEADBUTT (W), 6 frames: 1-4 THE CHARGE (played while he rushes at the enemy, looping on frames 1-4): the whole body leaning forward low, the head down and forward at the right with the horns pointing at the enemy, both arms swept back at his sides, the hooves digging in and alternating a little; 5 THE HEADBUTT (the enemy is knocked back here): the head and horns thrust up and forward to the right, the neck stretched, the arms flung back; 6 recovering toward the idle stance. Frames 5-6 are also played alone on the landing, so 5 must work right after 4 and right after the idle.` |
| `alistar_ult.png`（R 坚定意志（张臂怒吼）） | 6 帧：80 80 80 100 80 80 | 第 4 帧（tick 14） | 3 列 × 2 行，3072×1536 | 第 81 行 | `UNBREAKABLE WILL (R, a roar), 6 frames: 1 he crouches, gathering himself, the arms close; 2 the arms pulled in, the head lowered; 3 rising, the chest swelling; 4 THE ROAR: standing tall, both huge arms flung wide to the sides with the shackles and broken chains swinging, the head thrown back with the mouth open, the chest out; 5 holding the roar; 6 back toward the idle stance. The aura and the shockwave are effects. Legs: the design's legs.` |
| `alistar_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the chains swinging; 2 recovering toward the idle stance. The design's legs.` |
| `alistar_dead.png`（死亡（仰面倒地）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: he topples onto his back): 1 struck, he rears up; 2-3 staggering back, the arms flung out, the head thrown back; 4-5 falling backward to the left; 6-8 lying on his back on the ground (the body a quarter turned, flat along the feet line, the arms and legs limp, the head and horns at the left, still the design's head turned with the body, never upside down); 7 and 8 the same pose. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的角、鬃毛、描边；
- [ ] 每帧都有两只镣铐和断链、两只大手、皮围裙、两只牛蹄；手臂和造型图一样粗；站着的动作是造型图自己的腿（逐格一样）；
- [ ] 蹄底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；W 第 5 帧、Q 第 3 帧单独接在待机后面也不突兀；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `alistar_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`alistar_cells.json` 用包里这份，`alistar_idle.png` 用包里已做好的那张；剪出 `butt`（W 第 5–6 帧）和 `slam`（Q 第 3–6 帧）两个标签。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 12、Q 砸地 tick 14、W 落地的 slam 第 2 帧），量头像截取点，重跑模拟，做预览 GIF。
