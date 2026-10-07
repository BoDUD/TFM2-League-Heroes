# 萨勒芬妮：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/seraphine_design.png`（放大 8 倍，1024×1024；52 行高、38 格宽，44 色；舞台底在第 99 行，站位点在第 64 列）——是按你上一轮 design_1 生图原稿自己的格子取回、分区整行整列删到 52 行、再把脸和腿照格温的画法重画过的版本（用户：「可以 没问题了」）。**造型图就是标准**：亮粉长发和呆毛、头两侧的蓝色水晶羽片、蓝紫大眼睛和腮红、白泡泡袖、紫上衣、白手套、棕皮带和金菱形扣、深蓝彩条短裙和白褶边、银紫亮片袜（金弯纹）和白袜、棕靴金边、脚下金边青台面的浮空小舞台（蓝花徽章、粉色发光球、两颗蓝水晶），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`seraphine_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/seraphine_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。英雄联盟的 Q、W 是跳离舞台、死亡是被甩下舞台、舞台翻过来，**我们不照这些**：放技能一直站在舞台上，死亡照表里写的向后倒、仰躺在舞台上。
> - **舞台每一帧都在她脚下**：大小、形状、颜色和造型图一样，底边落在脚底线上，水平，不倾斜、不翻转。**跑步就是踩着舞台滑行**（英雄联盟就是这样），腿不迈步，只有头发和裙摆往后飘、整个人连舞台上下浮 1 格。
> - **放技能时的身体就是待机的身体**（同一套像素）：腿、靴子、舞台、裙子、上衣、袖子的形状和大小不能变，只动手臂、头发和身体的前倾后仰；整个人连舞台可以前后挪 1–3 格。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（Q 版大头）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的呆毛、刘海、脸和两侧蓝羽片**，**不画背影**（只有死亡仰躺时整个人连头转 90°）；③ **腿和舞台**：she always stands on her floating STAGE (the gold-rimmed hover board with the teal deck, the blue flower medallion, the pink orb and the two blue crystals): the stage is in EVERY frame, the same shape and size as in the design, its bottom on the feet line, level (never tilted, never flipped, never left behind); her legs are the design's own legs - the silver-lilac near stocking with the gold curl, the white far stocking, the brown boots with gold cuffs - square for square in every frame but the death, both boots on the deck; she never leaps off the stage (League's Q and W jumps are drawn on the stage: only the arms, the hair and the body's lean move); a cast may move the WHOLE figure with its stage 1-3 squares forward or back, never the upper body alone over still legs；④ **手臂**：the arms are the design's arms: fair skin with WHITE GLOVES, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder under the white puffy sleeve (never from the chest); the near arm over the body, the far arm drawn under it; an arm turns WHOLE from the shoulder in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the white gloves are NEVER hidden behind the body, the head or the hair; where an arm moves away, the body behind it is filled with the body's own colours (the violet top, the white sleeve, the hair)；⑤ the long pink hair, the curl, the two blue crystal fins beside her head, the white puffy sleeves, the violet top, the belt with the gold clasp and the striped dark-blue skirt with its white frill stay on her in every frame, the same shapes, colours and sizes as in the design; the long back hair is one mass that may stream and swing with the motion (further back in the run, flung up in the casts) but never splits into loose strands or specks。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/seraphine_now_<动作>.png`（骨架），图2 = `design/seraphine_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/seraphine-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`seraphine_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/seraphine_palette.png`，或直接读 `design/seraphine_design_1x.png`）。
4. **贴头**：把造型图的头（`design/seraphine_head_1x.png` 里不透明的格子：呆毛、刘海、脸、两侧蓝羽片；不含抬到耳边的白手套和身后的长发；在 128×128 画布上的范围 x 50–80、y 48–67，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡仰躺的帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. **贴舞台**：舞台（造型图最下面 10 行：青色台面、金色船底、蓝花徽章和粉球、两颗蓝水晶）每帧原样贴在脚下（只平移），不要自己重画。
6. 对位：每帧按 `seraphine_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），舞台底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/seraphine_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，舞台底在第 99 行 | 每张动作图的第一张附图 |
| `design/seraphine_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头、贴舞台 |
| `design/seraphine_head.png`、`_1x.png` | 要贴进每一帧的头（呆毛、刘海、脸、两侧蓝羽片） | 贴头 |
| `design/seraphine_palette.png` | 造型图的全部 44 色（暗到亮） | 色板 |
| `seraphine_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/seraphine_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、头发和身体的动作 |
| `guide/seraphine_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `seraphine_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/seraphine_picture.png`、`refs/seraphine_draft_codex.png` | 用户选的原画 A 和你上一轮的生图原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 44 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿和舞台**：she always stands on her floating STAGE (the gold-rimmed hover board with the teal deck, the blue flower medallion, the pink orb and the two blue crystals): the stage is in EVERY frame, the same shape and size as in the design, its bottom on the feet line, level (never tilted, never flipped, never left behind); her legs are the design's own legs - the silver-lilac near stocking with the gold curl, the white far stocking, the brown boots with gold cuffs - square for square in every frame but the death, both boots on the deck; she never leaps off the stage (League's Q and W jumps are drawn on the stage: only the arms, the hair and the body's lean move); a cast may move the WHOLE figure with its stage 1-3 squares forward or back, never the upper body alone over still legs。
- **手臂**：the arms are the design's arms: fair skin with WHITE GLOVES, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder under the white puffy sleeve (never from the chest); the near arm over the body, the far arm drawn under it; an arm turns WHOLE from the shoulder in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the white gloves are NEVER hidden behind the body, the head or the hair; where an arm moves away, the body behind it is filled with the body's own colours (the violet top, the white sleeve, the hair)。
- **身上**：the long pink hair, the curl, the two blue crystal fins beside her head, the white puffy sleeves, the violet top, the belt with the gold clasp and the striped dark-blue skirt with its white frill stay on her in every frame, the same shapes, colours and sizes as in the design; the long back hair is one mass that may stream and swing with the motion (further back in the run, flung up in the casts) but never splits into loose strands or specks。
- **头每帧都是造型图的头**（呆毛、刘海、眼睛、腮红、嘴、两侧蓝羽片逐格一样），只平移。
- **脚底线（舞台底）以下什么都不能有**（游戏在这条线下画血条），头发也不能低于舞台台面。
- **滑行循环**：每帧头相对站位点的横向位置不变；腿不迈步；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不跳离舞台**。**只画角色本身**：飞出去的音符、声波、护盾光圈、大招的音箱和音波都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/seraphine_design.png`，第二张 `now/seraphine_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `seraphine_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same long pink hair and curl, the blue crystal fins beside the head, the big blue-violet eyes with blush, the white puffy sleeves, the violet top, the white gloves, the brown belt with the gold clasp, the striped dark-blue skirt with the white frill, the silver-lilac near stocking with the gold curl and the white far stocking, the brown boots with gold cuffs, and her floating STAGE under the boots (gold-rimmed hover board, teal deck, blue flower medallion with a pink orb, two blue crystals), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the hair and the body from it, but keep the FIRST image's proportions and, in every frame but the death, the FIRST image's own legs standing on the stage; every cast goes to the RIGHT of the image; never draw her from the back, upside down or leaping off the stage.
The character: Seraphine, the Starry-Eyed Songstress (a young singer standing on a floating stage).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 44 colors of the FIRST image, no new colors: #0D0222 #160F11 #031723 #130327 #17093C #001D45 #071F44 #4A2412 #5F0033 #13136E #5E0333 #8B0545 #444959 #8A4A24 #C81260 #D11563 #0483C4 #D31865 #D61565 #BC7B25 #B87040 #E62574 #E8506E #FB2F7D #FB327E #FC3280 #FC3380 #FC3480 #FC3581 #01BFFA #FC4187 #F7BD3A #A8A0C8 #FCBA5F #F8A0A8 #F2B89A #80D4F2 #FCCF8A #CFCBE4 #FDDAB8 #D8D2EE #EEE5E5 #FCF9FA #FDFCFE. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every frame but the death the stage, the boots, the legs, the skirt, the top and the sleeves keep the FIRST image's shapes and sizes square for square; only the arms, the hair and the body's lean move, and the whole figure with its stage may move 1-3 squares.
Legs and stage: she always stands on her floating STAGE (the gold-rimmed hover board with the teal deck, the blue flower medallion, the pink orb and the two blue crystals): the stage is in EVERY frame, the same shape and size as in the design, its bottom on the feet line, level (never tilted, never flipped, never left behind); her legs are the design's own legs - the silver-lilac near stocking with the gold curl, the white far stocking, the brown boots with gold cuffs - square for square in every frame but the death, both boots on the deck; she never leaps off the stage (League's Q and W jumps are drawn on the stage: only the arms, the hair and the body's lean move); a cast may move the WHOLE figure with its stage 1-3 squares forward or back, never the upper body alone over still legs.
The arms: the arms are the design's arms: fair skin with WHITE GLOVES, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder under the white puffy sleeve (never from the chest); the near arm over the body, the far arm drawn under it; an arm turns WHOLE from the shoulder in steps of 45 degrees, never bent like a rubber hose, never shifted row by row; the white gloves are NEVER hidden behind the body, the head or the hair; where an arm moves away, the body behind it is filled with the body's own colours (the violet top, the white sleeve, the hair).
The body parts: the long pink hair, the curl, the two blue crystal fins beside her head, the white puffy sleeves, the violet top, the belt with the gold clasp and the striped dark-blue skirt with its white frill stay on her in every frame, the same shapes, colours and sizes as in the design; the long back hair is one mass that may stream and swing with the motion (further back in the run, flung up in the casts) but never splits into loose strands or specks.
The head (the curl, the bangs, the face with the eyes, blush and mouth, the two blue fins beside it) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the death frames where she lies on her back is it turned with the whole body). Erase your own head before pasting it, so no extra outline is left beside it. The stage is COPIED from the FIRST image the same way.
Feet line: in every cell the stage's bottom is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in seraphine_cells.json). In the glide her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every cast goes to the RIGHT of the image; never her back, never upside down, never off the stage. Do not draw effects (notes, sound waves, shield rings, the ult's speakers and wave) - only the character and her stage. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x88 squares (896x704 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head and the stage identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the gloves never behind the body or the hair, the legs and boots of the FIRST image on the stage in every frame but the death, no loose pieces of hair, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、头发和身体的方向和姿势照图1（出招都朝图的右边，不跳离舞台）；腿、靴子和脚下的浮空舞台用图2自己的，每帧都在。
3. 长相、配色、细节全部换成图2：亮粉长发和呆毛、两侧蓝羽片、蓝紫大眼睛和腮红、白泡泡袖、紫上衣、白手套、棕皮带和金扣、深蓝彩条短裙和白褶边、银紫亮片袜和白袜、棕靴金边、金边青台面的浮空小舞台。
4. 手臂从肩膀外侧长出来，白手套任何一帧都不能藏在身体或头发后面。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `seraphine_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1408 | 第 75 行 | **已做好，不用画** |
| `seraphine_run.png`（滑行（踩着舞台，不迈步）） | 8 × 133 | — | 4 列 × 2 行，3584×1408 | 第 75 行 | `GLIDE (the run), 8 frames, one seamless loop (League's run, 1.07 s): she does NOT walk - she stands on her floating stage, which carries her forward; the stage and her legs stay as in the design in all 8 frames; the whole figure with the stage bobs 1 row up and down twice in the loop (up in frames 2-3 and 6-7, down in 4 and 8); the long pink hair streams back to the image left and waves (its tips lift and fall a row or two from frame to frame), the skirt's frill flutters back by one square; the raised hand stays at her ear as in the design; her head keeps the same place across the cell relative to the standing point in all frames; frame 8 flows into frame 1.` |
| `seraphine_attack.png`（普攻（抬手甩出音符）） | 6 帧：60 60 60 80 80 80 | 第 4 帧（tick 11） | 3 列 × 2 行，2688×1408 | 第 75 行 | `BASIC ATTACK (a note sung at the target), 6 frames: 1 the design's stance; 2 the near arm lifts from the hip, palm up; 3 the near arm raised high above the head, the body leaning a little back; 4 THE NOTE (the sound bolt leaves here): the near arm flung forward to the image right, the glove open, the body leaning 1 square forward, the hair swinging back; 5 the arm coming back; 6 back to the design's stance. The flying note is a separate effect - do not draw it.` |
| `seraphine_skill.png`（Q 清籁穿云（举手高唱再甩出）） | 6 帧：60 60 70 80 80 80 | 第 4 帧（tick 11） | 3 列 × 2 行，2688×1408 | 第 75 行 | `HIGH NOTE (Q), 6 frames: 1 the design's stance; 2 the near arm sweeps up and back; 3 both arms raised, the body arching back, the face up (singing the high note); 4 THE CAST (the note is thrown here): the near arm flung forward and up to the image right, the body leaning forward 1-2 squares, the hair flung up behind her; 5 coming back; 6 back to the design's stance. Both boots stay on the stage (League leaps - we do not).` |
| `seraphine_skill2.png`（E→W 增幅节拍→聚和心声（前甩声波，再张开双臂唱）） | 8 帧：60 60 80 80 60 80 80 80 | 第 3 帧（tick 7）；第 6 帧（tick 20） | 4 列 × 2 行，3584×1408 | 第 75 行 | `BEAT DROP then SURROUND SOUND (E -> W), 8 frames: 1 the design's stance; 2 bending forward a little, the near arm drawn back; 3 THE WAVE (E's sound wave leaves here): the near arm swept forward low to the image right, palm out, the body leaning forward 1-2 squares, the hair whipping forward over the shoulder; 4 straightening up; 5 both arms lowered to her sides, palms out; 6 THE SONG (W's shield goes out here): both arms spread wide and up to both sides, the face up, singing, the hair lifted behind her; 7 the arms coming down; 8 back to the design's stance. Both boots stay on the stage.` |
| `seraphine_ult.png`（R 炫音返场（蹲下蓄力，起身甩手高唱）） | 4 帧：80 100 120 120 | 第 3 帧（tick 11） | 4 列 × 1 行，3584×704 | 第 75 行 | `ENCORE (R), 4 frames: 1 crouching a little on the stage, the near arm drawn back, gathering; 2 the deepest crouch, the head down, both arms close; 3 THE ENCORE (the great sound wave leaves here): standing up tall, the near arm flung forward and up to the image right, the glove open, the far arm back, the face up singing loudly, the hair streaming back; 4 coming back toward the design's stance. The wave and the speakers are effects.` |
| `seraphine_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1792×704 | 第 75 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left), the stage under her; 2 recovering toward the design's stance.` |
| `seraphine_dead.png`（死亡（照希维尔：向后倒、仰躺在舞台上）） | 8 帧：100 110 120 130 150 200 300 400 | — | 4 列 × 2 行，3584×1408 | 第 75 行 | `DEATH, 8 frames (Sivir's fall): 1 struck: jolted back as in the hit; 2 knocked back 1-2 squares, staggering on the stage; 3 the WHOLE body (legs, arms, hair and head as one piece) tipping over backwards, turned about 20 degrees (falling to the image left); 4 turned about 45 degrees; 5 turned 90 degrees, lying on her back on the stage's deck (the head to the image left, the feet to the image right), the hair spread under her; 6-8 the same as 5, still. The stage stays level under her, its bottom on the feet line, in all 8 frames.` |

## 交回前自查

- [ ] 每张和 now 条同样大小、同样格子，帧 N 在同一格；舞台底都在 `[R]` 行，下面没有像素；
- [ ] 严格 8×8 网格、透明度 0/255、只用造型图的 44 色、描边只有一种近黑；
- [ ] 每帧的头（呆毛、刘海、脸、两侧蓝羽片）和舞台都是造型图原样平移的；
- [ ] 除死亡外，每帧的腿和靴子都是造型图的、站在舞台上；滑行不迈步、上下浮最多 1 格、首尾接得上；
- [ ] 两只手臂都从肩膀外侧长出来，白手套没有藏在身体或头发后面；长发没有散成碎块；
- [ ] 出招朝右；没有画音符、声波、光圈等特效；不画背影、不跳离舞台；最后写 `HANDOFF.md`。

## Claude 收到后（给 Claude 看）

- 用 `tools/art/import_native.py` 按 `seraphine_cells.json` 切帧；造型的头和舞台再按 HEAD_BOXES / 最下面 10 行贴回去核对；腿、手臂不对的地方照格温 / 布兰德的做法自己修（rig_seraphine.py），用户审。
- 按出手帧改技能时机：普攻、Q、R 的出手 tick 和 E→W 的两个 tick（build_seraphine.py 的 a_st、q_rel、e_rel、w_rel、r_rel、各动作时长）。
