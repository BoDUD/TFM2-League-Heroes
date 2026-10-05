# 赵信：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/xinzhao_design.png`（放大 8 倍，1024×1024；发髻顶到脚底 42 行，65 格宽（连枪），25 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿 03（`refs/xinzhao_draft_codex.png`）按格子读回、整行整列删到 42 行的版本（每一格都是原稿的像素），用户选的「42 行、枪保持原稿长度」。**造型图就是标准**：黑色发髻和金发冠、两条深紫发带、黑发和额前的银白挑染、脸和眼睛、银白胸甲、皇家紫长战袍和金边、后肩金护肩、前肩带亮蓝饰的银护肩、棕色护臂和露指手套、棕色腰带、浅紫宽裤和胯边银甲片、深钢色靴子、紫刃银月牙钩的长枪（深棕枪杆、金箍、枪尾尖锥），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`xinzhao_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 11 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/xinzhao_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、枪和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（42 行高、头大）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 侧脸**，**不画背影**（参考渲染里身体会转过去，我们的头不转）；参考渲染里**头顶没有发髻和发带**（渲染坏了，已经去掉），发髻、金冠照造型图贴上去，两条紫发带你自己画，跟着动作飘；③ **腿**：in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the same wide stance, the same pale lavender trousers, silver hip plates and dark steel boots with gold trim, never spread wider, never crossed, never shorter; in the thrusts and swings (the attacks, Q, W, R) he may step or lunge as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps, only E leaps and only the death falls；④ 长枪：the long spear is the design's own - its head a PURPLE blade with a SILVER CRESCENT HOOK and a purple streamer, a dark brown shaft with gold rings, a short iron butt spike - at the design's length in every frame (it may turn with the motion: level for a thrust, upright, over his head; never shrink, never bend, never break into pieces), held in his hands as the THIRD image shows; it is never dropped except in the death；⑤ 手臂：the arms are the design's arms: brown leather forearm guards and dark fingerless gloves, the purple sleeve, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the gold shoulder guard stays on his back shoulder, the silver pauldron with its bright blue insets on his front shoulder, the silver breastplate, the brown belt and the purple coat with its gold trim stay on him。
> - 出招方向：**突刺、横扫、冲锋都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/xinzhao_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/xinzhao_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/xinzhao-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧枪尖和握枪那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`xinzhao_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/xinzhao_palette.png`，或直接读 `design/xinzhao_design_1x.png`）。
4. **贴头**：把造型图的头（`design/xinzhao_head_1x.png` 里不透明的格子：发髻和金冠、黑发和银白挑染、脸和眼睛、下巴；不含两条紫发带和金护肩；在 128×128 画布上的范围 x 57–73、y 58–75，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边；发带接在发髻后面，跟着动作飘。
5. 对位：每帧按 `xinzhao_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/xinzhao_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/xinzhao_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/xinzhao_head.png`、`_1x.png` | 要贴进每一帧的头（发髻和金冠、黑发和银白挑染、脸、下巴） | 贴头 |
| `design/xinzhao_palette.png` | 造型图的全部 25 色（暗到亮） | 色板 |
| `xinzhao_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/xinzhao_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、枪和身体的动作 |
| `guide/xinzhao_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `xinzhao_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/xinzhao_picture.png`、`refs/xinzhao_draft_codex.png` | 用户选的原画 A 和你的生图原稿 03（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（发髻顶到脚底 42 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 25 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the same wide stance, the same pale lavender trousers, silver hip plates and dark steel boots with gold trim, never spread wider, never crossed, never shorter; in the thrusts and swings (the attacks, Q, W, R) he may step or lunge as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps, only E leaps and only the death falls。
- **长枪**：the long spear is the design's own - its head a PURPLE blade with a SILVER CRESCENT HOOK and a purple streamer, a dark brown shaft with gold rings, a short iron butt spike - at the design's length in every frame (it may turn with the motion: level for a thrust, upright, over his head; never shrink, never bend, never break into pieces), held in his hands as the THIRD image shows; it is never dropped except in the death。
- **手臂**：the arms are the design's arms: brown leather forearm guards and dark fingerless gloves, the purple sleeve, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the gold shoulder guard stays on his back shoulder, the silver pauldron with its bright blue insets on his front shoulder, the silver breastplate, the brown belt and the purple coat with its gold trim stay on him。
- **头每帧都是造型图的头**（发髻、金冠、黑发、银白挑染、脸和眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条），枪也不能伸到线下。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和他的枪**：刀光、突刺的风、冲锋的拖尾、横扫的月牙、护盾的光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/xinzhao_design.png`，第二张 `now/xinzhao_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `xinzhao_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, armour, spear and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 view facing right, the same black topknot with its gold crown and two dark purple ribbons, the black hair with silver-white streaks, the face with both eyes and the brows, the silver breastplate, the long royal purple coat with gold trim, the gold shoulder guard on his back shoulder, the silver pauldron with bright blue insets on his front shoulder, the brown leather forearm guards and dark gloves, the brown belt, the pale lavender trousers with silver hip plates, the dark steel boots, the long spear with its purple blade, silver crescent hook, brown shaft with gold rings and iron butt spike, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the spear and the body from it, but keep the FIRST image's proportions (42 squares tall, a big head); its head has no topknot (removed from the render): the FIRST image's head with its topknot goes there; never draw him from the back or upside down.
The character: Xin Zhao, the Seneschal of Demacia (a stern spear warrior with a black topknot, a royal purple coat over silver armour and a long purple-bladed spear).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (42 squares from the top of the topknot to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 25 colors of the FIRST image, no new colors: #030105 #0D0A19 #1E092F #1B1D31 #341620 #2A0941 #613712 #430F67 #613231 #86523F #A46E21 #654F83 #7F1BB5 #6E6A82 #BB7656 #A72DE2 #41A9D5 #E2A53D #B98F91 #EAB241 #A7A5C0 #AE9BC9 #F3B786 #8ADEF6 #D5C9C6. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in the standing frames (idle, the wind-ups, the hit) he stands on the design's OWN legs square for square - the same wide stance, the same pale lavender trousers, silver hip plates and dark steel boots with gold trim, never spread wider, never crossed, never shorter; in the thrusts and swings (the attacks, Q, W, R) he may step or lunge as the THIRD image shows, the legs keeping the design's materials and thickness (the WHOLE figure moves with them, never the upper body alone over still legs); only the run steps, only E leaps and only the death falls.
The spear: the long spear is the design's own - its head a PURPLE blade with a SILVER CRESCENT HOOK and a purple streamer, a dark brown shaft with gold rings, a short iron butt spike - at the design's length in every frame (it may turn with the motion: level for a thrust, upright, over his head; never shrink, never bend, never break into pieces), held in his hands as the THIRD image shows; it is never dropped except in the death.
The arms: the arms are the design's arms: brown leather forearm guards and dark fingerless gloves, the purple sleeve, the same thickness as in the design in every frame - never thinner, never 1-pixel sticks, never floating hands; the gold shoulder guard stays on his back shoulder, the silver pauldron with its bright blue insets on his front shoulder, the silver breastplate, the brown belt and the purple coat with its gold trim stay on him.
The head (the topknot with its gold crown, the black hair with the silver streaks, the face with the eyes and brows, the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it; the two purple ribbons join the back of the topknot and swing with the motion.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in xinzhao_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 view like the FIRST image; every thrust, sweep and charge goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (slash arcs, the thrust's wind, the charge's trail, the crescent, the guard's glow) - only the character and his spear. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the whole spear with its purple blade and crescent hook, both shoulder pieces and both arms in every frame, the legs the design's legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、长枪、身体的方向和姿势照图1；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：黑色发髻和金冠、两条深紫发带、黑发和银白挑染、脸和眼睛、银白胸甲、紫金长战袍、后肩金护肩、前肩蓝饰银护肩、棕色护臂、棕色腰带、浅紫宽裤和银甲片、深钢色靴子、紫刃银月牙钩的长枪（深棕枪杆、金箍、枪尾尖锥）。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `xinzhao_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `xinzhao_run.png`（跑步） | 8 × 130 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.04 s a cycle): the design's legs swing from the hips, left and right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot on the feet line; the body leans a little forward, bobbing at most 1 square; the spear carried in the back hand slanting behind him as in the design (its purple blade low behind, the butt up past his shoulder), swinging a little; the free arm swings; the purple ribbons stream back; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `xinzhao_attack.png`（普攻（直刺）） | 6 帧：60 60 60 100 100 120 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (a spear thrust), 6 frames: 1 the spear drawn back low at his side, the blade pointing down and forward; 2-3 the spear sweeping low forward, the body turning into it; 4 THE BLOW (the hit lands here): the spear thrust out level to the image right at waist height, the body lunging forward 1-2 squares; 5 the spear still held out level; 6 back toward the idle stance. The thrust's streak is an effect - do not draw it.` |
| `xinzhao_attack_p.png`（被动第三下（双手大挥）） | 6 帧：70 70 70 100 100 100 | 第 4 帧（tick 13） | 3 列 × 2 行，3072×1536 | 第 81 行 | `DETERMINATION (every third attack, a big two-handed swing), 6 frames: 1 the spear lifted, slanting up behind him; 2 swung up higher; 3 swung round level at head height; 4 THE BLOW (the hit lands here): the spear brought round and down in front of him, the body crouched into it; 5 the spear slanting low behind him; 6 back toward the idle stance. The arc is an effect.` |
| `xinzhao_q1.png`（Q 第一下（突刺）） | 6 帧：60 60 60 100 100 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `THREE TALON STRIKE, FIRST THRUST (Q1), 6 frames: 1 the spear raised up behind him; 2 swung over his head; 3 the thrust starting, the spear coming level; 4 THE THRUST (the hit lands here): lunging forward, the spear driven straight out level to the image right; 5 holding the thrust; 6 the spear brought upright, back toward the idle stance.` |
| `xinzhao_q2.png`（Q 第二下（横扫）） | 6 帧：60 60 60 100 100 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1536 | 第 81 行 | `THREE TALON STRIKE, SECOND STRIKE (Q2, a sweep), 6 frames: 1 the spear held level at his chest; 2 the spear twirled upright; 3 swept down and forward in an arc; 4 THE SWEEP (the hit lands here): the spear swung up diagonally in front of him, the body lunging; 5 the spear slanting up the other way; 6 back toward the idle stance.` |
| `xinzhao_q3.png`（Q 第三下（上挑击飞、横举过头）） | 7 帧：70 70 70 100 100 100 100 | 第 4 帧（tick 13） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `THREE TALON STRIKE, THIRD STRIKE (Q3, the knock-up), 7 frames: 1 a crouch, the spear upright; 2 the spear level at his chest; 3 the spear swept up in an arc; 4 THE KNOCK-UP (the hit lands here): the spear swung up from low in front to high, lifting; 5-6 the spear held LEVEL OVER HIS HEAD with both hands (League's pose, the picture's version B); 7 back toward the idle stance. The upward slash is an effect.` |
| `xinzhao_skill.png`（E 无畏冲锋（飞身突刺落地）） | 6 帧：50 50 50 80 80 80 | 第 4 帧（tick 9） | 3 列 × 2 行，3072×1536 | 第 81 行 | `AUDACIOUS CHARGE (E, a leaping charge), 6 frames: 1 a crouch, about to leap; 2-3 flying forward low to the image right, the body stretched out, the spear held level ahead (a row or two above the feet line, inside the cell); 4 THE LANDING (the hit lands here): landing on both feet, the spear driven down and forward; 5 the spear thrust out level; 6 back toward the idle stance. The charge's trail and the ground burst are effects.` |
| `xinzhao_skill2.png`（W 风斩电刺（横扫再直刺）） | 7 帧：70 70 70 70 70 80 100 | 第 4 帧（tick 13） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `WIND BECOMES LIGHTNING (W, a slash then a thrust), 7 frames: 1 the spear swung back slanting; 2 the spear spun upright in front of him; 3 upright at his side; 4 THE SLASH (it lands here): the spear swept out wide and level across his front; 5-6 THE THRUST (it goes out on 5): lunging low forward, the spear driven out level to the image right; 7 back toward the idle stance. The slash arc and the thrust's wind are effects.` |
| `xinzhao_ult.png`（R 新月护卫（绕身横扫）） | 7 帧：80 80 90 90 90 90 100 | 第 3 帧（tick 10） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `CRESCENT GUARD (R, a sweep all round him), 7 frames: 1 the spear held low across his body; 2 the spear swung level behind him; 3 THE SWEEP (it lands here): spinning, the spear swept out round him; 4-6 the spear swung round him, out to the image left, then to the image right, the body turning with it (the head still the design's 3/4 head); 7 the spear brought upright at his side (its butt above the feet line). The crescent and the guard's glow are effects.` |
| `xinzhao_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the ribbons swinging, the spear still in hand; 2 recovering toward the idle stance. The design's legs.` |
| `xinzhao_dead.png`（死亡（单膝跪地后倒下）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: he sinks to one knee on his spear, then falls): 1 struck, he staggers back; 2-5 sinking onto one knee, leaning on the upright spear, the head bowed; 6 tipping forward; 7-8 lying face down on the ground, the spear fallen beside him; 7 and 8 the same pose. The head is the design's head turned with the body, never upside down. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；两条紫发带接在发髻后面；
- [ ] 每帧都有整杆长枪（紫刃、银月牙钩、金箍、枪尾尖锥）、两块护肩、两只手臂和棕色护臂；腿和造型图一样的材质和粗细；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `xinzhao_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`xinzhao_cells.json` 用包里这份，`xinzhao_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 11、被动第三下 tick 13、Q 第一下 tick 11、Q 第二下 tick 11、Q 第三下 tick 13、E 无畏冲锋 tick 9、W 风斩电刺 tick 13、R 新月护卫 tick 10），量枪尖和头像截取点，重跑模拟，做预览 GIF。
