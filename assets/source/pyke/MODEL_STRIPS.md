# 派克：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/pyke_design.png`（放大 8 倍，1024×1024；连高举的鱼叉 53 行高、62 格宽，光头顶到脚底 40 行，29 色；脚底在第 99 行，站位点在第 64 列）。它是你上一轮的生图原稿 A（`refs/pyke_draft_codex.png`）按原稿自己的格子读回、整行整列删到 40 行的版本（每一格都是原稿的像素，只把两只眼睛改亮），用户选的「40 行」。**造型图就是标准**：光头和疤、两只发青白光的眼睛、红面巾和白色锯齿条纹、两肩骨白獠牙、青蓝金边外套、背后深蓝下摆、腰带金徽章和红腰布、灰绿宽裤、棕色护膝和靴子、紫棕皮肤的手臂和爪子手、高举的鱼叉（骨白倒钩叉刃、金护手和青宝石、红缠杆、金钩），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`pyke_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/pyke_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的，鱼叉在画面左边那只手里）；长相照造型图。**出招一律朝图的右边**，参考图里朝左的挥动只是往后蓄力。
> - **放技能时的身体就是待机的身体**（同一套像素）：獠牙、外套、下摆、腰带、裤子和靴子的形状和大小不能变，只动手臂和鱼叉；整个人可以前倾后仰、前后挪 1–3 格。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（光头顶到脚底 40 行，头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 光头、两只眼睛和红面巾**，**不画背影**（只有死亡仰躺时整个人连头转 90°）；③ **腿**：the legs are the design's own legs - the grey-green baggy trousers, the brown knee guard with its gold buckle on the near knee, the brown boots - square for square in every standing frame (idle, the attack, Q, E's landing, R's strike, hit): crouched and apart as in the design, never redrawn, never given bare skin; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's dive, R's leap and the death change them. In the run the legs cross (one in front of the other, the far leg one shade darker so the two do not melt together), the hips stay under the body, the body bobs 1 row with each landing, and the legs keep the design's trouser and boot colours with the knee guard in the same place；④ **手臂和鱼叉**：the arms are the design's arms: dark purple-brown skin, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); an arm moves as ONE piece with its hand (and the harpoon in it), turned whole in steps of 45 degrees - never bent like a rubber hose, never shifted row by row; the far arm is drawn under the body but over the coat tail; the hands and the harpoon are NEVER hidden behind the body in any frame; the harpoon keeps the design's size and colours (bone-white barbed blade, gold guard with the cyan gem, red-wrapped shaft, gold hook)；⑤ the bone-white spikes over both shoulders, the teal coat with its gold edge, the long navy coat tail behind him, the belt with its gold medallions and the red waist cloth stay on him in every frame, the same shapes and sizes as in the design。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/pyke_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/pyke_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/pyke-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧鱼叉尖 / 手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`pyke_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/pyke_palette.png`，或直接读 `design/pyke_design_1x.png`）。
4. **贴头**：把造型图的头（`design/pyke_head_1x.png` 里不透明的格子：光头、疤、两只发光的眼睛、红面巾到下巴；不含旁边的獠牙；在 128×128 画布上的范围 x 68–80、y 59–72，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡仰躺的两帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的描边。
5. 对位：每帧按 `pyke_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/pyke_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/pyke_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/pyke_head.png`、`_1x.png` | 要贴进每一帧的头（光头、眼睛、红面巾） | 贴头 |
| `design/pyke_palette.png` | 造型图的全部 29 色（暗到亮） | 色板 |
| `pyke_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/pyke_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/pyke_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `pyke_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/pyke_picture.png`、`refs/pyke_draft_codex.png` | 用户选的原画 A 和你的生图原稿 A（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（光头顶到脚底 40 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 29 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：the legs are the design's own legs - the grey-green baggy trousers, the brown knee guard with its gold buckle on the near knee, the brown boots - square for square in every standing frame (idle, the attack, Q, E's landing, R's strike, hit): crouched and apart as in the design, never redrawn, never given bare skin; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's dive, R's leap and the death change them. In the run the legs cross (one in front of the other, the far leg one shade darker so the two do not melt together), the hips stay under the body, the body bobs 1 row with each landing, and the legs keep the design's trouser and boot colours with the knee guard in the same place。
- **手臂和鱼叉**：the arms are the design's arms: dark purple-brown skin, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); an arm moves as ONE piece with its hand (and the harpoon in it), turned whole in steps of 45 degrees - never bent like a rubber hose, never shifted row by row; the far arm is drawn under the body but over the coat tail; the hands and the harpoon are NEVER hidden behind the body in any frame; the harpoon keeps the design's size and colours (bone-white barbed blade, gold guard with the cyan gem, red-wrapped shaft, gold hook)。
- **身上**：the bone-white spikes over both shoulders, the teal coat with its gold edge, the long navy coat tail behind him, the belt with its gold medallions and the red waist cloth stay on him in every frame, the same shapes and sizes as in the design。
- **头每帧都是造型图的头**（光头、眼睛、红面巾逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），鱼叉尖也不能低于这条线。
- **跑步循环**：每帧头相对站位点的横向位置不变；两腿交叉迈步；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色本身**：飞出去的鱼叉、锁链、水花、魅影、X 形斩击都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/pyke_design.png`，第二张 `now/pyke_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `pyke_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, costume and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same bald scarred head with the two glowing cyan eyes and the red face mask with white jagged stripes, the bone-white spikes over both shoulders, the teal coat with gold trim, the long navy coat tail, the belt with gold medallions and the red waist cloth, the grey-green baggy trousers, the brown knee guard and boots, the dark purple-brown arms with claw hands, and the harpoon (bone-white barbed blade, gold guard with a cyan gem, red-wrapped shaft, gold hook), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored: his harpoon is in the hand on the image left) - copy the motion of the arms and the body from it, but keep the FIRST image's proportions (40 squares from the top of the head to the soles, a big head) and, in every standing frame, the FIRST image's own body and legs; every blow goes to the RIGHT of the image; never draw him from the back or upside down.
The character: Pyke, the Bloodharbor Ripper (a drowned harpooner: bald, glowing eyes, a red mask, bone spikes on his shoulders, a teal coat and a barbed harpoon).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the head to the soles in the idle pose), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 29 colors of the FIRST image, no new colors: #050303 #2F1914 #1C1E2E #113341 #4F2313 #740316 #3A342E #1C4C4F #A10619 #773B23 #67363C #5C5543 #D30919 #974D19 #A23C3E #8D5153 #B7641E #CD7720 #967D53 #EF9D24 #B79D72 #20D8E0 #F9B632 #04F7FA #DEA17E #D6BE92 #EDD9B1 #F9EED2 #C8FFFF. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
The body is the idle body: in every standing frame the shoulder spikes, the coat, the coat tail, the belt, the trousers and the boots keep the FIRST image's shapes and sizes square for square; only the arms and the harpoon move, and the whole figure may lean or move 1-3 squares.
Legs: the legs are the design's own legs - the grey-green baggy trousers, the brown knee guard with its gold buckle on the near knee, the brown boots - square for square in every standing frame (idle, the attack, Q, E's landing, R's strike, hit): crouched and apart as in the design, never redrawn, never given bare skin; a cast may move the WHOLE figure 1-3 squares forward or back (a lunge of the whole body), never the upper body alone over still legs; only the run, E's dive, R's leap and the death change them. In the run the legs cross (one in front of the other, the far leg one shade darker so the two do not melt together), the hips stay under the body, the body bobs 1 row with each landing, and the legs keep the design's trouser and boot colours with the knee guard in the same place.
The arms and the harpoon: the arms are the design's arms: dark purple-brown skin, the same thickness as in the design (never thinner, never 1-pixel sticks), each growing from the OUTER corner of its shoulder (never from the chest); an arm moves as ONE piece with its hand (and the harpoon in it), turned whole in steps of 45 degrees - never bent like a rubber hose, never shifted row by row; the far arm is drawn under the body but over the coat tail; the hands and the harpoon are NEVER hidden behind the body in any frame; the harpoon keeps the design's size and colours (bone-white barbed blade, gold guard with the cyan gem, red-wrapped shaft, gold hook).
The costume: the bone-white spikes over both shoulders, the teal coat with its gold edge, the long navy coat tail behind him, the belt with its gold medallions and the red waist cloth stay on him in every frame, the same shapes and sizes as in the design.
The head (the bald head with its scar, the two glowing eyes, the red mask down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play (only in the two death frames where he lies on his back is it turned 90 degrees with the whole body). Erase your own head before pasting it, so no extra outline is left beside it.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in pyke_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every blow, stab and throw goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (the flying harpoon, chains, water, the phantom, the X slash) - only the character. Every animation starts and ends in the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms growing from the outer shoulder corners in every frame, the hands and the harpoon never behind the body, the standing frames on the FIRST image's own body and legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、鱼叉和身体的方向和姿势照图1（出招都朝图的右边）；站着的帧身体和腿用图2自己的。
3. 长相、配色、细节全部换成图2：光头和疤、两只发青白光的眼睛、红面巾和白色锯齿条纹、两肩骨白獠牙、青蓝金边外套、深蓝下摆、腰带金徽章、灰绿宽裤、棕色护膝和靴子、紫棕手臂和爪子手、骨白倒钩鱼叉（金护手、青宝石、红缠杆、金钩）。
4. 手臂从肩膀外侧长出来，手和鱼叉任何一帧都不能藏在身体后面。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `pyke_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `pyke_run.png`（跑步（交叉步）） | 8 × 135 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, a 1.08 s stride): a hunched, prowling run, the body leaning a little forward; the legs CROSS: in frames 1 and 5 the feet are furthest apart (frame 1 the near leg in front, frame 5 the far leg in front), in frames 3 and 7 the legs pass each other under the body; the body bobs 1 row with each landing (down in 1 and 5, up in 3 and 7); the back arm keeps the harpoon raised behind as in the design, the front claw swings a little against the legs; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `pyke_attack.png`（普攻（鱼叉横扫）） | 6 帧：60 60 80 70 70 60 | 第 4 帧（tick 12） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (a harpoon slash), 6 frames: 1 he draws the harpoon back further behind his head; 2 the backswing at its widest, the body turning a little back; 3 swinging it over and forward; 4 THE HIT (the blow lands here): the harpoon swept forward to the image right, the blade pointing right at chest height, the whole figure lunging 2-3 squares forward; 5 the follow-through; 6 back toward the idle stance. Legs: the design's legs.` |
| `pyke_skill_stab.png`（Q 透骨尖钉（秒放戳刺）） | 5 帧：70 70 80 70 77 | 第 4 帧（tick 13） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `BONE SKEWER, the tap (Q stab), 5 frames: 1-2 he pulls the harpoon back beside his hip, the blade pointing forward, the body coiled; 3 starting the thrust; 4 THE STAB (the hit lands here): the harpoon driven straight forward to the image right at chest height in both hands or the back hand, the whole figure lunging 2-3 squares forward; 5 back toward the idle stance. Legs: the design's legs.` |
| `pyke_skill.png`（Q 透骨尖钉（蓄力扔鱼叉）） | 6 帧：150 150 150 150 120 113 | 第 5 帧（tick 36） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BONE SKEWER, the hold (Q hook throw), 6 frames: 1-4 the charge: the back arm cocks the harpoon back and up behind his head ready to throw (League's wind-up), the body leaning back, the front claw reaching forward to aim, frames 3 and 4 almost the same (a 1-square sway); 5 THE THROW (the harpoon leaves here): the back arm whipped forward to the image right at shoulder height, the hand empty and open (the harpoon is now a separate effect flying away - do NOT draw it in his hand in this frame), the body leaning forward 1-2 squares; 6 the empty hand coming back, toward the idle stance (the harpoon is back in his hand in the idle). Legs: the design's legs.` |
| `pyke_skill2.png`（W→E 魅影浪洄（俯冲）） | 4 帧：60 60 60 53 | — | 4 列 × 1 行，4096×768 | 第 81 行 | `PHANTOM UNDERTOW (E dash), 4 frames, a fast low dive forward to the image right: 1 crouching lower, about to spring; 2-3 the dive: the body stretched forward almost level (leaning about 45 degrees), the harpoon held back along the body, the legs trailing behind, the whole figure 1-2 squares lower; 4 landing in a crouch toward the idle stance. Never upside down, never his back. The water trail and the drowned phantom are effects.` |
| `pyke_ult.png`（R 涌泉之恨（跃起下刺）） | 6 帧：100 100 100 120 120 127 | 第 4 帧（tick 18） | 3 列 × 2 行，3072×1536 | 第 81 行 | `DEATH FROM BELOW (R), 6 frames, a leap and a downward strike: 1 crouching deep, the harpoon raised in both hands; 2 THE LEAP: the whole figure 4-5 squares higher, the knees drawn up, the harpoon held high over his head point down; 3 at the top, the harpoon raised highest; 4 THE STRIKE (the X strikes here): he lands, the harpoon driven down point-first into the ground in front of him (to the image right), the body bent over it; 5 holding the strike; 6 rising toward the idle stance. Nothing below the feet line (the harpoon point stops on it). The X and the water are effects.` |
| `pyke_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the arms flung a little out, the harpoon still in his hand; 2 recovering toward the idle stance. The design's legs.` |
| `pyke_dead.png`（死亡（向后倒、仰躺）） | 8 帧：100 110 120 130 150 200 300 400 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 knocked back 2-3 squares, the arms flung out, the harpoon slipping from his hand; 3-4 the WHOLE body (legs included, as one piece) tipping over backwards: frame 3 turned 45 degrees back (falling to the image left), frame 4 further; 5-6 lying on his back on the ground (the whole body turned 90 degrees, the head to the image left, the feet to the image right, the legs together and straight), the harpoon lying on the ground beside him; 7 and 8 the same as 6, still. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的描边；
- [ ] 每帧身体（獠牙、外套、下摆、腰带、裤子、靴子）和造型图一样；两只手臂都在、和造型图一样粗、从肩膀外侧长出来；手和鱼叉没有藏在身体后面；
- [ ] 跑步两腿交叉、远侧腿暗一档、腿的颜色和护膝位置和待机一样；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；扔鱼叉那一帧手里是空的；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `pyke_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；身体不是待机身体的帧用造型图的部件重摆（rigkit：手臂和鱼叉整块按 45° / 90° 转，整个人前倾后仰）。
- 放进 `assets/source/native/`，`pyke_cells.json` 用包里这份，`pyke_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；红色方：朝向特效烘进动作帧（`pyke_bake.json`）。
- 按出手帧核对技能数据的时机（普攻 tick 12、Q 戳刺 tick 13、Q 扔鱼叉 tick 36、R tick 18），量鱼叉出手点和头像截取点，重跑模拟，做预览 GIF。
