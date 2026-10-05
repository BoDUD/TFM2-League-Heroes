# 泰达米尔（蛮王）：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/tryndamere_design.png`（放大 8 倍，1024×1024；盔角尖到脚底 40 行，57 格宽（连刀），24 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿 A_retry（`refs/tryndamere_draft_codex.png`）按格子读回、整行整列删到 40 行的版本（每一格都是原稿的像素），用户选的「40 行原样」。**造型图就是标准**：角盔和额头青宝石、侧脸的眼睛、短黑胡子和红色的嘴、身后的黑色长发、古铜色赤膊、前肩带青宝石的大肩甲、白布缠手和深色护腕、斜挎皮带、白布腰带和兽首护裆（青宝石）、层叠深灰甲裙和深青鳞甲裙、深灰甲靴、后手拖着的锯齿大弯刀和两颗青珠，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`tryndamere_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/tryndamere_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、刀和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（40 行高、宽弓步）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸**，**不画背影**（参考渲染里头盔会转过去，我们不转）；③ **腿**：站着的动作**每帧都是造型图自己的腿**，逐格一样，不能叉得更开、不能交叉、不能变短；出手时可以**整个人连腿一起**前后挪 1–2 格，**不能只挪上半身压在腿上**；只有跑步迈腿、E 转身、死亡倒下；④ 大刀：the huge dark grey greatsword with its serrated back, silver edge and the two teal orbs (a big one at the guard, a small one at the pommel) is held in his BACK hand (image left) by its grip as in the design, the design's size and shape in every frame (it may turn with the swing, never shrink, never bend, never break into pieces); it is never dropped except in the death；⑤ 手臂：the arms are the design's arms: thick bronze arms with the grey-white cloth wraps and dark bracers, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the free hand is the design's open clawed hand; the big pauldron with its teal gem stays on his front shoulder, the brown chest strap, the white sash and the beast-head plate with its teal gem stay on him。
> - 出招方向：**劈砍、嘲讽都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/tryndamere_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/tryndamere_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/tryndamere-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧刀尖和握刀那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`tryndamere_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/tryndamere_palette.png`，或直接读 `design/tryndamere_design_1x.png`）。
4. **贴头**：把造型图的头（`design/tryndamere_head_1x.png` 里不透明的格子：两只角、头盔和额头青宝石、护颊、脸和眼睛、胡子和红嘴；不含身后的长发和旁边的肩甲；在 128×128 画布上的范围 x 70–83、y 60–75，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边；长发接在头盔后面，跟着动作飘。
5. 对位：每帧按 `tryndamere_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/tryndamere_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/tryndamere_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/tryndamere_head.png`、`_1x.png` | 要贴进每一帧的头（角、头盔和宝石、护颊、脸、胡子和嘴） | 贴头 |
| `design/tryndamere_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `tryndamere_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/tryndamere_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、刀和身体的动作 |
| `guide/tryndamere_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `tryndamere_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/tryndamere_picture.png`、`refs/tryndamere_draft_codex.png` | 用户选的原画 A 和你的生图原稿 A_retry（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（盔角尖到脚底 40 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：in every standing frame (idle, the attack's wind-up and blow, W, Q, R, hit) he stands on the design's OWN legs square for square - the same wide, low stance, the same dark armoured boots and the teal scale skirt, never spread wider, never crossed, never shorter; the arms, the sword and the shoulders move, the legs stay (a blow may move the WHOLE figure, legs included, 1-2 squares forward, never the upper body alone over still legs); only the run steps, only E spins (the legs turning with the body) and only the death falls。
- **大刀**：the huge dark grey greatsword with its serrated back, silver edge and the two teal orbs (a big one at the guard, a small one at the pommel) is held in his BACK hand (image left) by its grip as in the design, the design's size and shape in every frame (it may turn with the swing, never shrink, never bend, never break into pieces); it is never dropped except in the death。
- **手臂**：the arms are the design's arms: thick bronze arms with the grey-white cloth wraps and dark bracers, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the free hand is the design's open clawed hand; the big pauldron with its teal gem stays on his front shoulder, the brown chest strap, the white sash and the beast-head plate with its teal gem stay on him。
- **头每帧都是造型图的头**（角、头盔、宝石、脸、眼睛、胡子和嘴逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和他的刀**：刀光、旋风、怒吼的冲击、怒火和回血的光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/tryndamere_design.png`，第二张 `now/tryndamere_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `tryndamere_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, armour, sword and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same dark horned helmet with the teal forehead gem, the face with the eye, the short black beard and the red mouth, the long black hair behind, the bronze bare chest and thick arms with grey-white cloth wraps and dark bracers, the big pauldron with a teal gem, the brown chest strap, the white sash with the beast-head plate and its teal gem, the layered dark grey plate skirt over the teal scale skirt, the dark armoured boots, the huge serrated dark grey greatsword with two teal orbs, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the sword and the body from it, but keep the FIRST image's proportions (40 squares tall, a wide low stance) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Tryndamere, the Barbarian King (a huge bare-chested barbarian with a horned helmet, a black beard, long black hair and a giant serrated greatsword).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the horn tips to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #05020B #002534 #1F2030 #003849 #3D2422 #2F344C #00536A #00747F #84422E #444B6C #E90E22 #008E99 #A85638 #8C6D67 #666E90 #C46E45 #04CBC9 #8186A4 #9AA5C2 #F5A66D #B9C2D8 #76EFF0 #CCFBFA #F5F6F8. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, the attack's wind-up and blow, W, Q, R, hit) he stands on the design's OWN legs square for square - the same wide, low stance, the same dark armoured boots and the teal scale skirt, never spread wider, never crossed, never shorter; the arms, the sword and the shoulders move, the legs stay (a blow may move the WHOLE figure, legs included, 1-2 squares forward, never the upper body alone over still legs); only the run steps, only E spins (the legs turning with the body) and only the death falls.
The greatsword: the huge dark grey greatsword with its serrated back, silver edge and the two teal orbs (a big one at the guard, a small one at the pommel) is held in his BACK hand (image left) by its grip as in the design, the design's size and shape in every frame (it may turn with the swing, never shrink, never bend, never break into pieces); it is never dropped except in the death.
The arms: the arms are the design's arms: thick bronze arms with the grey-white cloth wraps and dark bracers, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the free hand is the design's open clawed hand; the big pauldron with its teal gem stays on his front shoulder, the brown chest strap, the white sash and the beast-head plate with its teal gem stay on him.
The head (the horns, the helmet with the gem, the cheek guard, the face with the eye, the beard and the red mouth) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it; the long hair joins the back of the helmet and swings with the motion.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in tryndamere_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every blow and the shout go to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash arcs, the whirl, the shout's ring, the fury aura, the healing glow) - only the character and his sword. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the greatsword with both orbs, the pauldron and both arms in every frame, the standing frames on the FIRST image's own legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、大刀、身体的方向和姿势照图1；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：角盔和额头青宝石、侧脸的眼睛、短黑胡子和红嘴、身后的黑色长发、古铜色赤膊、带青宝石的大肩甲、白布缠手、斜挎皮带、白布腰带和兽首护裆、层叠深灰甲裙和深青鳞甲裙、深灰甲靴、后手的锯齿大弯刀和两颗青珠。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `tryndamere_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `tryndamere_run.png`（跑步） | 8 × 125 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.0 s a cycle): the design's legs swing from the hips, left and right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot on the feet line; the body leans a little forward, bobbing at most 1 square; the greatsword is carried low in the back hand, trailing behind him, swinging a little; the free arm swings; the long black hair streams back; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `tryndamere_attack.png`（普攻（举刀下劈）） | 6 帧：50 50 50 50 100 100 | 第 5 帧（tick 12） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (an overhead chop with the greatsword), 6 frames: 1 the sword swings back low behind him; 2 it comes up behind his back; 3-4 raised high over his head with both hands near the grip, the body rearing back; 5 THE BLOW (the hit lands here): the sword chopped down and forward to the image right at chest height, the body lunging forward 1-2 squares, the free arm flung back; 6 the sword trailing back down toward the idle stance. The slash arc is an effect - do not draw it. Legs: the design's legs.` |
| `tryndamere_skill.png`（E 旋风斩（转一圈）） | 6 帧：44 44 44 44 44 47 | 第 1 帧（tick 0） | 3 列 × 2 行，3072×1536 | 第 81 行 | `SPINNING SLASH (E, he spins through his enemies), 6 frames, one fast turn: the greatsword held out flat at chest height and swept round him - 1 the sword out to the image left behind him, 2 the body turning, the sword passing behind his back, 3 the sword out to the image right in front of him, 4 his back half turned (the sword still out, the head still the design's 3/4 head), 5 the sword round to the left again, 6 coming out of the spin toward the idle stance. Every frame the sword at its full length, flat; the whirl trail is an effect. Legs: turning with the body, the design's leg materials, both feet on the line.` |
| `tryndamere_skill2.png`（W 蔑视（怒吼嘲讽）） | 6 帧：60 60 50 80 80 70 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `MOCKING SHOUT (W), 6 frames: 1 he crouches a little, the sword low; 2 the shoulders pulled back, the chest out; 3 drawing breath, the head back; 4 THE SHOUT (it goes out here): the free arm thrust forward to the image right with the hand open, palm out, mocking, the mouth wide open; 5 holding it; 6 back toward the idle stance. The shout's ring is an effect. Legs: the design's legs.` |
| `tryndamere_skill_q.png`（Q 嗜血杀戮（握拳回血）） | 5 × 80 | — | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `BLOODLUST (Q, he drinks his fury and heals), 5 frames: 1 he straightens a little and clenches the free fist in front of his chest; 2 the fist pulled to his chest, the shoulders tensed, the head bowed; 3 the whole body tensed, the arms flexed; 4 the head comes up; 5 back toward the idle stance. The red healing glow is an effect. Legs: the design's legs.` |
| `tryndamere_ult.png`（R 无尽怒火（仰头怒吼）） | 6 帧：80 80 90 90 80 80 | 第 2 帧（tick 5） | 3 列 × 2 行，3072×1536 | 第 81 行 | `UNDYING RAGE (R), 6 frames, League's roar: 1 the chest thrust out and up, the shoulders pulled back; 2 THE ROAR (it starts here): the head thrown back, the mouth wide open, the free fist clenched at his side, the sword low behind him; 3-5 holding the roar, the shoulders shaking a square; 6 back toward the idle stance. The red fury aura is an effect. Legs: the design's legs.` |
| `tryndamere_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the hair swinging, the sword still in hand; 2 recovering toward the idle stance. The design's legs.` |
| `tryndamere_dead.png`（死亡（刀飞起插地、倒下）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: the greatsword flies up and sticks in the ground): 1 struck, he staggers back; 2-3 the sword flung up from his hand (draw it high in the cell, inside the cell), he falls back; 4-5 falling onto his back, the head still the design's head turned with the body, never upside down; 6-8 lying on the ground, the sword stuck point-down in the ground beside him, standing upright; 7 and 8 the same pose. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；
- [ ] 每帧都有大刀（两颗青珠）、肩甲、两只手臂和白布缠手；站着的动作是造型图自己的腿（逐格一样），手臂和造型图一样粗；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `tryndamere_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`tryndamere_cells.json` 用包里这份，`tryndamere_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 12、W tick 10），量刀尖和头像截取点，重跑模拟，做预览 GIF。
