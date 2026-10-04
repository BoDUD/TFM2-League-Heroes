# 伊芙琳：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/evelynn_design.png`（放大 8 倍，1024×1024；发顶到脚底 41 行，36 格宽，18 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生成原稿（`refs/evelynn_draft_codex.png`，87 行）按格子读回、删到 80 行再每 2×2 格取一色减半到 40 行的版本，两只黄眼睛对齐在同一行。**造型图就是标准**：往后飘的白发粉挑染、肩前两缕头发、淡紫皮肤、两只黄眼睛和紫色眼睑、深靛紫紧身衣和品红 V、品红前臂和淡粉长爪、品红紫的大腿、高跟鞋、背后两条紫色长鞭，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`evelynn_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/evelynn_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、身体和鞭子的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（大头发、Q 版头、40 行高）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡倒地时整个头跟着身体转），**不画背影、不画倒立**（英雄联盟的 E 有空翻，我们不翻）；③ **两条鞭子**：her TWO LASHERS (violet whip tendrils, as in the FIRST image's lower body: 2-3 squares thick, a bright violet edge on top, a sharp pale-tipped blade at each end) grow from her LOWER BACK in EVERY frame - joined to her back, never loose, never cut off; they move with the action (trailing behind her in the walk, whipping forward in the attacks, raised behind her in W and the ult, limp beside her in the death) and stay above the feet line；④ 其余：the big swept-back white-and-pink hair, the two locks in front of her shoulders, the pale lavender skin, the dark indigo suit with the magenta V, the magenta forearms with pale-pink claws and the high heels stay exactly as in the design; the claws are 2-3 pale-pink squares at the end of each magenta hand。
> - **腿**：in the standing frames (W, the hit) the legs are the design's own legs square for square - the same stance and the same heels; the attack, the whip, the dash and the ult bend and stride like the THIRD image (the legs keep the design's colours and thickness, the hips joined to the body), the walk alternates them and the death sinks and falls。
> - 出招方向：**抓、甩、劈、扑都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/evelynn-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和 `generation_prompts.json`，最好打成一个 zip（`evelynn_strips_pack_done.zip`）。**生图原稿也一起交来。**

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**不要把细节比方块还小的高清图压缩下来**。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/evelynn_palette.png`，或直接读 `design/evelynn_design_1x.png`）。
4. **贴头**：把造型图的头（`design/evelynn_head_1x.png` 里不透明的格子：往后飘的头发、脸、两只黄眼睛、到下巴为止；在 128×128 画布上的范围 x 41–67、y 59–75，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡倒地时整个头跟着转）。这样每帧的脸都和造型图一模一样。贴之前先擦掉你自己画的头，不要在头的旁边留下多余的头发或描边。
5. **鞭子**：两条鞭子照 `design/evelynn_lashers_1x.png` 的粗细、颜色和尖刃，每帧都从后腰长出来、和身体连着。
6. 对位：每帧按 `evelynn_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/evelynn_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/evelynn_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/evelynn_head.png`、`_1x.png` | 要贴进每一帧的头（头发、脸、黄眼睛、到下巴） | 贴头 |
| `design/evelynn_lashers.png`、`_1x.png` | 造型的下半身：两条鞭子（从后腰到刃尖）、腿、高跟鞋 | 鞭子的粗细、样子和接在哪里 |
| `design/evelynn_palette.png` | 造型图的全部 18 色（暗到亮） | 色板 |
| `evelynn_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/evelynn_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、身体、鞭子的动作 |
| `guide/evelynn_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `evelynn_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/evelynn_picture.png`、`refs/evelynn_draft_codex.png` | 用户选的原画 A 和你画的生成原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（发顶到脚底 41 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 18 种颜色**，不加新颜色；明暗照定稿（深色紧身衣和鞭子的亮边跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边（`#120C1C`），描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手和手臂**：袖子到手肘、品红前臂 2 格粗、手上 2–3 格淡粉长爪；**不要 1 像素的黑细棍、不要飘着的手**。
- **鞭子**：her TWO LASHERS (violet whip tendrils, as in the FIRST image's lower body: 2-3 squares thick, a bright violet edge on top, a sharp pale-tipped blade at each end) grow from her LOWER BACK in EVERY frame - joined to her back, never loose, never cut off; they move with the action (trailing behind her in the walk, whipping forward in the attacks, raised behind her in W and the ult, limp beside her in the death) and stay above the feet line。
- **头发和身体**：the big swept-back white-and-pink hair, the two locks in front of her shoulders, the pale lavender skin, the dark indigo suit with the magenta V, the magenta forearms with pale-pink claws and the high heels stay exactly as in the design; the claws are 2-3 pale-pink squares at the end of each magenta hand。
- **腿**：in the standing frames (W, the hit) the legs are the design's own legs square for square - the same stance and the same heels; the attack, the whip, the dash and the ult bend and stride like the THIRD image (the legs keep the design's colours and thickness, the hips joined to the body), the walk alternates them and the death sinks and falls。
- **头每帧都是造型图的头**（头发、脸、黄眼睛逐格一样），只平移（死亡倒地时整个转）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），鞭子在它上面。
- **走路循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不空翻**。**只画角色**：尖刺、诅咒、爱心、刀光、拖尾、隐身的雾、恶魔光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，**不要洋红**，她身上有品红）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/evelynn_design.png`，第二张 `now/evelynn_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `evelynn_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, hair, suit, claws, lashers and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same big swept-back white-and-pink hair, the pale lavender face with the two yellow eyes under violet lids, the dark indigo suit with the magenta V, the magenta forearms with pale-pink claws, the magenta-and-indigo legs on high heels, the two violet lashers from her lower back, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the legs, the body and the lashers from it, but keep the FIRST image's proportions (big hair, a big chibi head, 40 squares tall); never draw her from the back, upside down or flipping.
The character: Evelynn (a slender demon woman with big swept-back white hair streaked with pink, pale lavender skin, yellow eyes, a dark indigo bodysuit, magenta forearms with long pale-pink claws, magenta-and-indigo legs on high heels, two long violet lashers growing from her lower back).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares from the hair's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 18 colors of the FIRST image, no new colors: #120C1C #1E1646 #2A0E5C #2E2470 #4A1C96 #463C9E #B81E6A #6A62C8 #EE3C8C #F05AA0 #FFD21E #9C9CCC #B070FF #FF86BC #CACAEE #FFC0DC #ECECFF #F4F4FF. ONE outline: a 1-square near-black outline (#120C1C) around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading - the lit edges of the dark suit and the lashers move with the pose; no dithering, no noise, no random specks added. Hands are magenta forearms 2 squares thick ending in 2-3 pale-pink claw squares - never 1-pixel black sticks or floating hands.
The lashers are her signature: her TWO LASHERS (violet whip tendrils, as in the FIRST image's lower body: 2-3 squares thick, a bright violet edge on top, a sharp pale-tipped blade at each end) grow from her LOWER BACK in EVERY frame - joined to her back, never loose, never cut off; they move with the action (trailing behind her in the walk, whipping forward in the attacks, raised behind her in W and the ult, limp beside her in the death) and stay above the feet line.
The hair and the body: the big swept-back white-and-pink hair, the two locks in front of her shoulders, the pale lavender skin, the dark indigo suit with the magenta V, the magenta forearms with pale-pink claws and the high heels stay exactly as in the design; the claws are 2-3 pale-pink squares at the end of each magenta hand.
The legs: in the standing frames (W, the hit) the legs are the design's own legs square for square - the same stance and the same heels; the attack, the whip, the dash and the ult bend and stride like the THIRD image (the legs keep the design's colours and thickness, the hips joined to the body), the walk alternates them and the death sinks and falls.
The head (the swept-back hair, the face with the two yellow eyes, down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it.
Feet line: in every cell her lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a lasher, not a heel spike - because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in evelynn_cells.json). In the walk her head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every attack goes to the RIGHT of the image; never her back, never upside down, no flips. Do not draw effects (spikes, the curse, hearts, slash trails, the shadow mist, the demonic light) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green, never magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both lashers joined to her lower back in every frame, the claws on both hands, the idle's legs in the standing frames, no loose pieces, no stray black squares, nothing below the feet line, never her back, upside down or flipping, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `evelynn_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `evelynn_run.png`（走路） | 8 × 125 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `WALK, 8 frames, one seamless loop (League's walk at her base speed: a slow, swaying prowl, 1.0 s a cycle): the body upright, the hips swaying, the head steady; the near clawed hand loose at her side, the far arm swinging gently; the two lashers trailing behind her and swaying with the step; in frames 1-4 one heel comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same magenta-and-indigo colours with the same heels; the body bobs at most 1 square; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `evelynn_attack.png`（普攻（前突抓击）） | 6 帧：50 50 60 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (a lunging slash with her claws and lashers), 6 frames: 1 the idle stance; 2 she draws the near clawed hand back, the body coiling; 3 the wind-up at its fullest; 4 THE HIT (the blow lands here): a step forward into a lunge, the near arm and claws thrust forward to the right at chest height, the lashers whipping forward low beside her; 5 the follow-through; 6 back toward the idle stance. The slash's trail is an effect - do not draw it.` |
| `evelynn_attack_e.png`（E 鞭笞（高举下劈）） | 6 帧：50 50 60 70 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `WHIPLASH (E: a big overhead whip), 6 frames: 1 the idle stance; 2 she rears up, the near claws rising; 3 both claws raised high above her head, the body arched back, the lashers flung up behind her; 4 THE WHIP (the blow lands here): a big downward slash into a low lunge, the claws and the lashers sweeping down to the right; 5 still low after the slash; 6 rising back toward the idle stance. The whip's arc is an effect.` |
| `evelynn_attack_e2.png`（E 强化鞭笞（扑击冲刺）） | 6 帧：50 50 60 60 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，3072×1536 | 第 81 行 | `EMPOWERED WHIPLASH (E after her Demon Shade: a pouncing dash), 6 frames: 1 she crouches, the lashers spreading behind her; 2 the lashers flung forward; 3 she launches forward low; 4 the dash: the body stretched forward to the right, the claws out, the lashers streaming behind; 5 landing on the target with a slash; 6 back toward the idle stance. The trail is an effect.` |
| `evelynn_skill.png`（Q 憎恨之刺（甩出尖刺）） | 5 帧：50 50 60 60 70 | 第 3 帧（tick 6） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `HATE SPIKE (Q: she lashes a spike out), 5 frames: 1 a quick wind-up, the near arm drawn back, the lashers swinging; 2 the body turning into the throw; 3 THE LASH (the spike leaves here): the near arm flung forward to the right at chest height, the claws open, a lasher whipping forward beside it; 4 the follow-through; 5 back toward the idle stance. The flying spike is an effect.` |
| `evelynn_skill2.png`（W 引诱（飞吻放诅咒）） | 4 × 70 | 第 2 帧（tick 4） | 4 列 × 1 行，4096×768 | 第 81 行 | `ALLURE (W: she casts her curse), 4 frames: 1 the near hand brought up to her lips; 2 THE CURSE (it leaves here): she flicks the hand forward to the right, blowing a kiss, the lashers rising behind her like a pair of tails; 3 holding, the lashers high; 4 back toward the idle stance. The heart-shaped curse is an effect.` |
| `evelynn_ult.png`（R 最终抚慰（扇形横扫）） | 6 帧：70 70 70 80 80 80 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×1536 | 第 81 行 | `LAST CARESS (R), 6 frames: 1 she crouches, the lashers gathering behind her; 2 she rears up, the lashers raised high above her; 3 THE SLASH (the blow lands here): a wide sweeping slash forward, the claws and both lashers swept out in a fan in front of her to the right; 4 low after the slash; 5 rising; 6 back toward the idle stance. Her warp back and the demonic burst are effects.` |
| `evelynn_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: her body and head pushed back 1-2 squares (to the left), the lashers jerking; 2 recovering toward the idle stance.` |
| `evelynn_dead.png`（死亡） | 8 × 110 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death): 1-2 struck, she recoils; 3-4 she sinks to her knees; 5-6 she falls to her side; 7-8 lying on the ground, the lashers limp beside her (the same pose in 7 and 8); the head stays visible from the 3/4 front (turned with the body, never upside down). Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡倒地时整个转），头旁边没有多余的头发、描边；
- [ ] **两条鞭子每帧都在**，和后腰连着；两只手都有淡粉长爪；
- [ ] 站着的帧（W、受击）腿和待机一模一样；走路两条腿交叉迈步、颜色一样；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有空翻；出招都朝图的右边；
- [ ] 走路循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点、bbox 和出手帧那只手的位置都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `evelynn_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、鞭子连没连着、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头，头旁边的残留清掉。
- 放进 `assets/source/native/`，`evelynn_cells.json` 用包里这份，`evelynn_idle.png` 用包里已做好的那张。
- `import_native.py --hero evelynn`：ORDER 待机一张图（静止待机，或 BOB 呼吸，缝选在小腿的直段），COMPLETE 补描边，NECK 检查头每帧在肩上同一行。
- 按出手帧核对技能数据的时机（普攻 tick 10、Q tick 6、R tick 8），量出手那只手的位置定尖刺的出手点，量头像截取点，重跑模拟，做预览 GIF。
