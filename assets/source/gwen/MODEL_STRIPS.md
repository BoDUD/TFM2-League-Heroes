# 格温：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/gwen_design.png`（放大 8 倍，1024×1024；呆毛顶到鞋底 44 行，53 格宽（连剪刀），25 色；鞋底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿 bd82（`refs/gwen_draft_codex.png`）按格子读回、缩到 44 行的版本，脸照 oppi 的画法重描（2×2 大蓝眼、腮红、一格小嘴），剪刀照英雄联盟原版改成**合着的一整片长刃 + 两个带刺的大环**，脖子和上身照原稿重描，用户一处一处确认过的。**造型图就是标准**：亮天蓝头发和呆毛、两边的螺旋卷、头两侧的黑蝴蝶结、大蓝眼睛和腮红、青色项圈、黑泡泡袖、白裙和深紫前片、紫蝴蝶结和金星胸针、深藏青荷叶边裙摆和金饰钉、紫菱格长袜和金色腿饰、白色高跟短靴、身后那把大剪刀（青蓝长刃、带刺的环），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`gwen_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/gwen_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、剪刀和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（44 行高、头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸**，**不画背影**（参考渲染里旋转时身体会转过去，我们的头不转）；两边的螺旋卷你自己画，跟着动作晃；③ **腿**：in the standing frames (idle, the wind-ups, the hit) she stands on the design's OWN legs square for square - the same stance, the same purple diamond stockings with the gold garter charm and the white heeled boots, never spread wider, never shorter; in the thrusts, the snips, the dash and the throw she may step, lunge, rise on her toes or crouch as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls；④ 剪刀：her weapon is the design's own: the GIANT SCISSORS - one long cyan crystal blade (the two blades closed together, a light top edge, a blue lower edge) and two silvery-cyan RING HANDLES with small spikes - at the design's length in every frame (about 1.1 times her height from the rings to the point), never shrunk, never bent, never broken into pieces; she holds them by a ring handle; when she snips, the long blade opens into TWO blades (a V) and closes again; when she does not use them they rest behind her hip as in the design, the blade trailing down and back; they are never dropped except in the death；⑤ 手臂：the arms are the design's arms: fair skin, purple gloves, black puffed sleeves, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands - and the hand holding the scissors is always in sight in front of or beside her body, never hidden behind it; the white dress with the purple front, the purple bow with the gold star, the cyan choker and the navy hem with gold studs stay on her。
> - 出招方向：**突刺、剪、冲刺、扔针都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/gwen_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/gwen_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/gwen-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧剪刀尖和握剪刀那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`gwen_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/gwen_palette.png`，或直接读 `design/gwen_design_1x.png`）。
4. **贴头**：把造型图的头（`design/gwen_head_1x.png` 里不透明的格子：呆毛、头发、黑蝴蝶结、脸到下巴；不含下巴以下的螺旋卷和剪刀；在 128×128 画布上的范围 x 54–75、y 56–69，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边；螺旋卷接在头两侧，跟着动作晃。
5. 对位：每帧按 `gwen_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/gwen_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/gwen_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/gwen_head.png`、`_1x.png` | 要贴进每一帧的头（呆毛、头发、黑蝴蝶结、脸到下巴） | 贴头 |
| `design/gwen_palette.png` | 造型图的全部 25 色（暗到亮） | 色板 |
| `gwen_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/gwen_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、剪刀和身体的动作 |
| `guide/gwen_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `gwen_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/gwen_picture.png`、`refs/gwen_draft_codex.png` | 用户选的原画 A 和你的生图原稿 bd82（长相参考；比例、剪刀和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（呆毛顶到鞋底 44 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 25 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：in the standing frames (idle, the wind-ups, the hit) she stands on the design's OWN legs square for square - the same stance, the same purple diamond stockings with the gold garter charm and the white heeled boots, never spread wider, never shorter; in the thrusts, the snips, the dash and the throw she may step, lunge, rise on her toes or crouch as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls。
- **剪刀**：her weapon is the design's own: the GIANT SCISSORS - one long cyan crystal blade (the two blades closed together, a light top edge, a blue lower edge) and two silvery-cyan RING HANDLES with small spikes - at the design's length in every frame (about 1.1 times her height from the rings to the point), never shrunk, never bent, never broken into pieces; she holds them by a ring handle; when she snips, the long blade opens into TWO blades (a V) and closes again; when she does not use them they rest behind her hip as in the design, the blade trailing down and back; they are never dropped except in the death。
- **手臂**：the arms are the design's arms: fair skin, purple gloves, black puffed sleeves, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands - and the hand holding the scissors is always in sight in front of or beside her body, never hidden behind it; the white dress with the purple front, the purple bow with the gold star, the cyan choker and the navy hem with gold studs stay on her。
- **头每帧都是造型图的头**（呆毛、头发、黑蝴蝶结、脸逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条），剪刀尖也不能伸到线下。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和她的剪刀**（R 的出手前手里那根小针可以画）：刀光、雾、丝线、飞出去的针、冲刺的拖尾都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/gwen_design.png`，第二张 `now/gwen_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `gwen_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, costume, weapon and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same bright sky-blue hair with the cowlick and the big drill curls, the two black ribbon bows on her head, the big blue eyes with pink blush, the cyan choker, the black puffed sleeves, the white dress with the dark purple front, the purple striped bow with the gold star brooch, the navy ruffled hem with gold studs, the purple diamond stockings with the gold garter charm, the white heeled boots, the fair skin, the purple gloves, the GIANT SCISSORS (one long cyan crystal blade, two spiked silvery-cyan ring handles), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the scissors and the body from it, but keep the FIRST image's proportions (44 squares tall, a big head); never draw her from the back or upside down.
The character: Gwen, the Hallowed Seamstress (a cheerful living doll girl with giant scissors).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares from the top of the cowlick to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 25 colors of the FIRST image, no new colors: #08021A #1D1444 #020375 #0B0BAA #3C2A71 #653A94 #4516EB #025FF8 #0187FA #E0506A #E89620 #03ADFB #7F6BE0 #FABE38 #F39378 #28DDFC #AA93F3 #F6A6A0 #FBE169 #F8B899 #8FF2FE #CEC1FA #FCE3CD #FCF6CB #F3F8FA. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in the standing frames (idle, the wind-ups, the hit) she stands on the design's OWN legs square for square - the same stance, the same purple diamond stockings with the gold garter charm and the white heeled boots, never spread wider, never shorter; in the thrusts, the snips, the dash and the throw she may step, lunge, rise on her toes or crouch as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps and only the death falls.
The scissors: her weapon is the design's own: the GIANT SCISSORS - one long cyan crystal blade (the two blades closed together, a light top edge, a blue lower edge) and two silvery-cyan RING HANDLES with small spikes - at the design's length in every frame (about 1.1 times her height from the rings to the point), never shrunk, never bent, never broken into pieces; she holds them by a ring handle; when she snips, the long blade opens into TWO blades (a V) and closes again; when she does not use them they rest behind her hip as in the design, the blade trailing down and back; they are never dropped except in the death.
The arms: the arms are the design's arms: fair skin, purple gloves, black puffed sleeves, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands - and the hand holding the scissors is always in sight in front of or beside her body, never hidden behind it; the white dress with the purple front, the purple bow with the gold star, the cyan choker and the navy hem with gold studs stay on her.
The head (the cowlick, the hair, the two black bows, the face with the blue eyes, the blush and the mouth, the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it; the drill curls join the sides of the head and bounce with the motion.
Feet line: in every cell her soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in gwen_cells.json). In the run her head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every thrust, snip, dash and throw goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (cut flashes, the mist, threads, flying needles, the dash's trail) - only the character and her scissors (and the small needle in her hand before the R throw). Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the whole scissors at the design's length where the animation needs them, both arms and the hand holding the scissors in sight in every frame, the legs the design's legs, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、剪刀、身体的方向和姿势照图1；站着的动作腿用图2自己的腿；握剪刀的手不能藏到身体后面。
3. 长相、配色、细节全部换成图2：天蓝头发和呆毛、螺旋卷、头两侧的黑蝴蝶结、大蓝眼睛和腮红、青色项圈、黑泡泡袖、白裙和深紫前片、紫蝴蝶结和金星胸针、深藏青裙摆和金饰钉、紫菱格长袜、白色高跟短靴、大剪刀（合着的一整片青蓝长刃、两个带刺的大环，长度和图2一样）。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `gwen_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `gwen_run.png`（跑步） | 8 × 150 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.2 s a cycle): the design's legs under the skirt swing from the hips, left and right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot on the feet line; the body leans a little forward, bobbing at most 1 square; the skirt and the drill curls bounce a little; she carries the scissors as League does in its run: held upright behind her back by a ring handle, the long blade pointing up, at the design's length; the free arm swings; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `gwen_attack.png`（普攻（剪刀突刺）） | 6 帧：60 60 70 70 80 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `SCISSOR THRUST (basic attack), 6 frames: 1 the scissors lifted by the rings, the blade swinging forward; 2-3 drawn back at her side, the blade level and pointing to the image right; 4 THE THRUST (the hit lands here): the arm straight, the long blade thrust out level far to the image right, the body leaning into it 1-2 squares; 5 a small twirl of the scissors in the hand; 6 the scissors back behind her hip, toward the idle stance. The slash flash is an effect - do not draw it.` |
| `gwen_skill.png`（Q 快刀剪乱（连剪 + 大剪）） | 8 帧：50 60 60 60 60 70 80 100 | 第 6 帧（tick 17） | 4 列 × 2 行，4096×1536 | 第 81 行 | `SNIP SNIP! (Q), 8 frames: 1 the scissors brought round in front of her, the blade pointing to the image right; 2-5 QUICK SNIPS held out in front at chest height: the long blade OPENS into two blades (a wide V) on 2 and 4 and SHUTS on 3 and 5, the arms working them; 6 THE FINAL SNIP (the big cut lands here): a wide, low snip across her front to the image right, the body lunging, the skirt flaring; 7 holding it; 8 the scissors back behind her hip, toward the idle stance. The cut flashes are effects.` |
| `gwen_skill2.png`（E 断续疾走接 W 丝缕缠流（旋身冲刺后举剪刀召雾）） | 8 帧：40 40 40 60 80 80 80 100 | 第 6 帧（tick 16） | 4 列 × 2 行，4096×1536 | 第 81 行 | `SKIP 'N SLASH then HALLOWED MIST (E then W), 8 frames: 1-3 THE DASH: a quick twirling skip to the image right on her toes, leaning forward, the skirt swirling out, the scissors held close at her side; 4 landing lightly on both feet; 5-7 she raises the scissors and twirls them high over her head (6 = THE MIST, it settles here), the free arm out for balance; 8 the scissors back behind her hip, toward the idle stance. The mist, the threads and the dash's trail are effects.` |
| `gwen_ult.png`（R 引针簇射（扔针，游戏里连放三次）） | 6 帧：50 60 60 70 80 100 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `NEEDLEWORK (R, one needle throw; the game plays it three times for the three volleys), 6 frames: 1 the free hand draws a small silver needle (2-3 squares) from her side, the scissors kept in the other hand behind her hip; 2-3 the throwing arm swung back and up over her shoulder; 4 THE THROW (the needles leave here): the arm whipped forward to the image right, the needle gone from the hand; 5 the follow-through; 6 back toward the idle stance. The flying needles are effects.` |
| `gwen_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left), the curls swinging; 2 recovering toward the idle stance. The design's legs.` |
| `gwen_dead.png`（死亡（剪刀落地、坐倒后躺下）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: the scissors fall and she sinks down): 1 struck, she staggers back; 2-3 the scissors slip from her hand to the ground beside her; 4-6 sinking down to sit on the ground, the skirt spreading; 7-8 falling back to lie on the ground, the scissors beside her; 7 and 8 the same pose. The head is the design's head turned with the body, never upside down. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；螺旋卷接在头两侧；
- [ ] 每帧大剪刀完整、和造型图一样长（剪的时候张开成两片，平时合成一片）；两只手臂都在，握剪刀的手看得见、不藏在身后；腿和造型图一样的材质和粗细；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `gwen_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比、手和剪刀看不看得见），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；放技能时的身体换回待机的身体，手臂连剪刀整块转（rigkit），不画骨骼。
- 放进 `assets/source/native/`，`gwen_cells.json` 用包里这份，`gwen_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q 快刀剪乱 tick 17、E 断续疾走接 W 丝缕缠流 tick 16、R 引针簇射 tick 10），量剪刀尖和头像截取点；刀光按红方规则画进动作帧（gwen_bake.json）；重跑模拟，做预览 GIF。
