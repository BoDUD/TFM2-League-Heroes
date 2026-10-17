# 韦鲁斯：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/varus_design.png`（放大 8 倍，1024×1024；头顶到脚底 40 行，29 格宽（连弓），24 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生图原稿 A（`refs/varus_draft_codex.png`）按格子读回、按面积缩到 40 行的版本，用户说「这个最好 很不错」。**造型图就是标准**：银白后梳扎发、头带和红宝石、粉紫色眼睛、红围巾和长尾巴、青色纹身、斜挎皮带和金边青色护符、紫红腐化的小臂和爪手、紫黑甲腿和靴子、近侧手里带尖刺发紫光的大弓，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`varus_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/varus_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（Q 版大头、40 行高）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**，**不画背影**；③ **腿**：站着的动作（待机、普攻、Q、E、受击）**每帧都是造型图自己的腿，逐格一样**，不能叉得更开、不能交叉、不能变短；出手时可以**整个人连腿一起**前后挪 1–2 格，**不能只挪上半身压在腿上**；只有跑步迈腿，只有 R 是英雄联盟的全身前冲（屈膝、髋部连着）；④ 弓：the big spiked purple-black bow with its violet glow is held in the NEAR hand (image right) in every frame, the design's size and spikes; when he shoots it is held up and pointing to the right with the string drawn to his cheek by the far hand; in Q it opens wider like spread claws and glows brighter; it is never dropped except in the death；⑤ 手臂：the arms are the design's arms: pale upper arms, the crimson-to-purple corrupted forearms and clawed hands, 2 squares wide, the same thickness as in the design in every frame - never thicker, never 1-pixel sticks, never floating hands; the red scarf and its long tail stay on him (the tail swings with the motion); the gold-and-teal medallion stays on his chest。
> - 出招方向：**箭和锁链都朝图的右边**（游戏里朝左时会整张镜像）；E 朝右上方射向天空。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**（上一轮成功的办法）：图1 = `now/varus_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/varus_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/varus-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`varus_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/varus_palette.png`，或直接读 `design/varus_design_1x.png`）。
4. **贴头**：把造型图的头（`design/varus_head_1x.png` 里不透明的格子：银白头发和扎起的发尾、头带和红宝石、脸和眼睛，到下巴为止，不含旁边的弓；在 128×128 画布上的范围 x 50–69、y 60–73，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发或描边。
5. 对位：每帧按 `varus_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/varus_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/varus_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/varus_head.png`、`_1x.png` | 要贴进每一帧的头（头发、头带和红宝石、脸和眼睛） | 贴头 |
| `design/varus_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `varus_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/varus_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/varus_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `varus_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/varus_picture.png`、`refs/varus_draft_codex.png` | 用户选的原画 A 和你的生图原稿 A（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（头顶到脚底 40 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every standing frame (idle, attack, Q, E, hit) he stands on the design's OWN legs square for square - the same purple armoured legs, boots, stance and width as the design, never spread wider, never crossed, never shorter; the shoulders and arms move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares back or forward with the shot, never the upper body alone over still legs); only the run steps and only R crouches and lunges (League's full-body throw), with the design's leg materials, knees bent, hips joined。
- **弓**：the big spiked purple-black bow with its violet glow is held in the NEAR hand (image right) in every frame, the design's size and spikes; when he shoots it is held up and pointing to the right with the string drawn to his cheek by the far hand; in Q it opens wider like spread claws and glows brighter; it is never dropped except in the death。
- **手臂**：the arms are the design's arms: pale upper arms, the crimson-to-purple corrupted forearms and clawed hands, 2 squares wide, the same thickness as in the design in every frame - never thicker, never 1-pixel sticks, never floating hands; the red scarf and its long tail stay on him (the tail swings with the motion); the gold-and-teal medallion stays on his chest。
- **头每帧都是造型图的头**（头发、头带、脸和眼睛逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- **跑步循环**：每帧头相对站位点的横向位置不变；两条腿交替迈步，着地的脚踩在线上；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色和他的弓**：箭、蓄力光、箭雨、锁链、枯萎标记都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/varus_design.png`，第二张 `now/varus_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `varus_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, scarf, bow and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same swept-back silver hair tied behind, the dark headband with the red gem, the pink-violet eyes, the red scarf and its long tail, the teal shoulder tattoo, the dark harness with the gold-rimmed teal medallion, the crimson-to-purple corrupted forearms and clawed hands, the purple-black armoured legs and boots, the big spiked purple-black glowing bow, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the bow and the body from it, but keep the FIRST image's proportions (a big chibi head, 40 squares tall) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Varus, the Arrow of Retribution (a lean corrupted archer: silver hair swept back, a red scarf, a gold medallion on a bare chest, corrupted purple clawed forearms, purple armoured legs, a huge living darkin bow).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the hair's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #0B0410 #640005 #261432 #9D040A #2D3E46 #3B185F #890851 #5204BA #28767C #652493 #F01A1A #D32087 #ED9201 #7E76AB #908C8E #A112F7 #C18D7D #FDE502 #CA2BFB #E838F3 #E6B99A #B2B1DE #FCDBB2 #E5E7FB. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, attack, Q, E, hit) he stands on the design's OWN legs square for square - the same purple armoured legs, boots, stance and width as the design, never spread wider, never crossed, never shorter; the shoulders and arms move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares back or forward with the shot, never the upper body alone over still legs); only the run steps and only R crouches and lunges (League's full-body throw), with the design's leg materials, knees bent, hips joined.
The bow: the big spiked purple-black bow with its violet glow is held in the NEAR hand (image right) in every frame, the design's size and spikes; when he shoots it is held up and pointing to the right with the string drawn to his cheek by the far hand; in Q it opens wider like spread claws and glows brighter; it is never dropped except in the death.
The arms: the arms are the design's arms: pale upper arms, the crimson-to-purple corrupted forearms and clawed hands, 2 squares wide, the same thickness as in the design in every frame - never thicker, never 1-pixel sticks, never floating hands; the red scarf and its long tail stay on him (the tail swings with the motion); the gold-and-teal medallion stays on his chest.
The head (the hair, the headband with the gem, the face and the eyes, down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair or outline is left beside it.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in varus_cells.json). In the run his head keeps the same horizontal place relative to the standing point in every frame.
3/4 front view like the FIRST image; every shot goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (arrows, the charge glow, the rain of arrows, the tendril, the blight marks) - only the character and his bow. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the bow, the scarf and both clawed hands in every frame, the standing frames on the FIRST image's own legs, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、弓、身体的方向和姿势照图1；站着的动作腿用图2自己的腿。
3. 长相、配色、细节全部换成图2：银白后梳扎发、头带和红宝石、粉紫色眼睛、红围巾和长尾巴、金边青色护符、紫红腐化的爪手、紫黑甲腿和靴子、近侧手里发紫光的大弓。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `varus_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `varus_run.png`（跑步） | 8 × 133 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `RUN, 8 frames, one seamless loop (League's run, 1.07 s a cycle): the design's legs swing from the hips, left and right alternate (the leading foot changes every half cycle, the feet at most 12 squares apart), the planted foot on the feet line; the body upright, bobbing at most 1 square; the far arm swings a little; the bow carried low in the near hand, swinging a little; the scarf tail streams back; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `varus_attack.png`（普攻（射箭）） | 6 帧：70 80 80 70 60 40 | 第 3 帧（tick 9） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (an arrow), 6 frames: 1 the bow comes up level in the near hand pointing right, the far hand reaching for the string; 2 the full draw: the string pulled to his cheek, the bow arm straight to the right, the whole figure leaning back 1 square; 3 THE RELEASE (the arrow leaves here): the far hand snaps open behind his head, the bow kicks, the whole figure pushed forward 1-2 squares; 4 the follow-through, the far hand flung up and back; 5 lowering the bow; 6 back toward the idle stance. The arrow is an effect - do not draw it. Legs: the design's legs.` |
| `varus_skill.png`（Q 穿刺之箭（满蓄力）） | 7 帧：100 150 250 300 300 80 87 | 第 6 帧（tick 66） | 4 列 × 2 行，4096×1536，最后 1 格空 | 第 81 行 | `PIERCING ARROW (Q, the full draw), 7 frames: 1 the bow comes up in front of him pointing right; 2 the draw begins and the bow OPENS wide like spread claws, the violet glow growing; 3-5 HOLDING the full draw (a held charge, 0.85 s): the string at his cheek, the bow open and glowing, the frames differ only in the glow and a square of tremble; 6 THE RELEASE (the long arrow leaves here): the far hand snaps open back, the bow recoils, the whole figure pushed forward 1 square; 7 back toward the idle stance. The arrow and the charge glow around the bow are effects - draw only the bow itself brighter. Legs: the design's legs.` |
| `varus_skill2.png`（E 恶灵箭雨（朝天射）） | 5 帧：80 87 80 80 73 | 第 3 帧（tick 10） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `HAIL OF ARROWS (E, a shot into the sky), 5 frames: 1 the bow swings up, aimed high up-right (about 45 degrees), the far hand drawing; 2 the full draw pointing up-right; 3 THE RELEASE (the arrow flies up here): the far hand snaps back, the bow kicks; 4 the follow-through, the bow still raised; 5 back toward the idle stance. The arrow and the rain are effects. Legs: the design's legs.` |
| `varus_ult.png`（R 腐败锁链（前冲甩出）） | 5 帧：120 130 90 80 80 | 第 3 帧（tick 15） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `CHAIN OF CORRUPTION (R, he hurls a tendril from the bow), 5 frames, League's full-body throw: 1 he crouches, the bow swept back low behind his near hip; 2 lunging forward, the near arm swinging the bow forward; 3 THE THROW (the tendril leaves here): the near arm and the bow thrust forward to the right at chest height, the body low and forward, the near knee bent, the far leg stretched back; 4 holding the lunge; 5 rising back toward the idle stance. The tendril is an effect.` |
| `varus_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and head pushed back 1-2 squares (to the left), the scarf tail swinging, the bow still in hand; 2 recovering toward the idle stance. The design's legs.` |
| `varus_dead.png`（死亡（弓落地、跪倒）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death: the darkin bow leaves him): 1-2 struck, he staggers back, the head thrown back, the far hand clutching his chest; 3-4 the bow falls from his near hand to the ground in front of him; 5-6 he sinks to his knees; 7-8 kneeling, slumped forward, the head down (still the design's head, seen from the 3/4 front, never upside down), the bow lying flat on the ground beside him; 7 and 8 the same pose. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、描边；
- [ ] 每帧都有弓、红围巾、两只爪手和护符；站着的动作是造型图自己的腿（逐格一样），手臂和造型图一样粗；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步循环：头的横向位置每帧一样，两腿交替，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `varus_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`varus_cells.json` 用包里这份，`varus_idle.png` 用包里已做好的那张；`skill_quick`（快速出手）从 Q 条的帧里剪出来（第 1–3 帧加第 6–7 帧）。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 9、Q 满蓄力 tick 66），量出手那只手的位置定弹道的出手点（y_offset），量头像截取点，重跑模拟，做预览 GIF。
