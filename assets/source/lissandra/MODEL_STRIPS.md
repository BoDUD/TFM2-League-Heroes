# 丽桑卓：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/lissandra_design.png`（放大 8 倍，1024×1024；冠顶到裙摆 42 行，27 格宽，21 色；裙摆最低一行在第 99 行，裙摆中间在第 64 列）。它是你上一轮「骨架 + 皮囊」换皮的 B 版（`refs/lissandra_skin_codex.png`）按格子读回、修好脸的版本。**造型图就是标准**：深蓝冰冠（两边长刃、青色月牙）、遮眼面罩、淡蓝下半脸和一格深蓝嘴唇、深色兜帽发绺、冰蓝编织长辫、亮青色水晶护肩、V 领胸甲、发青光的手臂和爪手、拖地深蓝长裙和裙摆的钢蓝冰晶，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`lissandra_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/lissandra_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（大冰冠、Q 版头、42 行高）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**，**不画背影**；③ **没有腿**：she has NO legs: the long navy gown reaches the ground in EVERY frame and its hem of steel-blue ice crystals stays on the hem line (she glides, never steps); the gown sways and flares with the motion but keeps the design's length, folds and crystal hem - never draw feet, never lift the hem off the line (only the death's ice rises over it)；④ 冰冠和辫子：the wide crown with its two blades and the cyan crescent stays on her head in every frame exactly as in the design; the long ice-blue braid hangs behind her and swings with the motion, the same width and plait pattern as in the design；⑤ 手臂：the arms are the design's arms: navy sleeves on the upper arm, the forearms and the long clawed hands glowing cyan, 2 squares wide; a cast flings them out or up as the THIRD image shows, the claws open - never 1-pixel sticks, never floating hands; the cyan shoulder crystals stay on the shoulders。
> - 出招方向：**冰弹、冰锥、冰爪都朝图的右边**（游戏里朝左时会整张镜像）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**（上一轮成功的办法）：图1 = `now/lissandra_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/lissandra_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/lissandra-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`lissandra_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/lissandra_palette.png`，或直接读 `design/lissandra_design_1x.png`）。
4. **贴头**：把造型图的头（`design/lissandra_head_1x.png` 里不透明的格子：冰冠、面罩、脸和嘴唇、到下巴为止的兜帽发绺；在 128×128 画布上的范围 x 50–75、y 58–71，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的冠刃、头发或描边。
5. 对位：每帧按 `lissandra_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），裙摆落在裙摆线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/lissandra_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，裙摆线第 99 行 | 每张动作图的第一张附图 |
| `design/lissandra_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/lissandra_head.png`、`_1x.png` | 要贴进每一帧的头（冰冠、面罩、脸和嘴唇、兜帽发绺） | 贴头 |
| `design/lissandra_palette.png` | 造型图的全部 21 色（暗到亮） | 色板 |
| `lissandra_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/lissandra_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/lissandra_guide_<动作>.png` | 每格边框、站位点（蓝十字）、裙摆线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `lissandra_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/lol_death_crystals.png` | 英雄联盟的死亡：冰晶从裙摆往上把她冻成冰雕 | 死亡动作 |
| `refs/lissandra_picture.png`、`refs/lissandra_skin_codex.png` | 用户选的原画 A 和你换皮的 B 原图（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高（冠顶到裙摆 42 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 21 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **没有腿**：she has NO legs: the long navy gown reaches the ground in EVERY frame and its hem of steel-blue ice crystals stays on the hem line (she glides, never steps); the gown sways and flares with the motion but keeps the design's length, folds and crystal hem - never draw feet, never lift the hem off the line (only the death's ice rises over it)。
- **冰冠和辫子**：the wide crown with its two blades and the cyan crescent stays on her head in every frame exactly as in the design; the long ice-blue braid hangs behind her and swings with the motion, the same width and plait pattern as in the design。
- **手臂**：the arms are the design's arms: navy sleeves on the upper arm, the forearms and the long clawed hands glowing cyan, 2 squares wide; a cast flings them out or up as the THIRD image shows, the claws open - never 1-pixel sticks, never floating hands; the cyan shoulder crystals stay on the shoulders。
- **头每帧都是造型图的头**（冰冠、面罩、脸和嘴唇逐格一样），只平移。
- **裙摆线以下什么都不能有**（游戏在脚下画血条）。
- **滑行循环**：每帧头相对站位点的横向位置不变；裙摆一直贴着线、轻轻起伏；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：冰弹、冰锥、冰环、冰爪、冰墓、冰仆、冰块都是单独的特效，不要画（只有死亡时裙摆上长出来的冰晶要画）。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/lissandra_design.png`，第二张 `now/lissandra_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `lissandra_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, crown, braid, gown and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same wide navy crown with two blades and a cyan crescent, the dark mask over the eyes, the pale blue lower face with the dark blue lips, the dark hood-locks, the long plaited ice-blue braid, the bright cyan shoulder crystals, the V neckline, the glowing cyan forearms and clawed hands, the long navy gown with the steel-blue ice crystals at its hem, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the body and the braid from it, but keep the FIRST image's proportions (a big crown, a big chibi head, 42 squares tall); never draw her from the back or upside down.
The character: Lissandra, the Ice Witch (a tall sorceress with no visible legs: a long navy gown to the ground with ice crystals at the hem, a wide crown-helm with blades, a mask over her eyes, a long plaited ice-blue braid, crystal shoulders, glowing cyan clawed hands).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (42 squares from the crown's top to the hem in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 21 colors of the FIRST image, no new colors: #080716 #0B0A14 #09081A #0A091F #0C0C26 #141233 #19173D #1F1D48 #212454 #23275C #232C6B #2B3C8D #334BAF #3F62CE #4483F0 #13AEFD #6A97F5 #84A8ED #4FD1FD #83EDFE #D2F2FD. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
No legs: she has NO legs: the long navy gown reaches the ground in EVERY frame and its hem of steel-blue ice crystals stays on the hem line (she glides, never steps); the gown sways and flares with the motion but keeps the design's length, folds and crystal hem - never draw feet, never lift the hem off the line (only the death's ice rises over it).
The crown and the braid: the wide crown with its two blades and the cyan crescent stays on her head in every frame exactly as in the design; the long ice-blue braid hangs behind her and swings with the motion, the same width and plait pattern as in the design.
The arms: the arms are the design's arms: navy sleeves on the upper arm, the forearms and the long clawed hands glowing cyan, 2 squares wide; a cast flings them out or up as the THIRD image shows, the claws open - never 1-pixel sticks, never floating hands; the cyan shoulder crystals stay on the shoulders.
The head (the crown, the mask, the lower face with the lips, the hood-locks down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved; never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra blade, hair or outline is left beside it.
Hem line: in every cell her lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in lissandra_cells.json). In the glide her head keeps the same horizontal place relative to the standing point in every frame.
3/4 front view like the FIRST image; every cast goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (ice bolts, shards, rings, claws, tombs, thralls, ice blocks) - only the character (in the death, the ice crystals growing up her gown are part of her). Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the braid and both glowing hands in every frame, the hem on the hem line and no feet, no loose pieces, no stray black squares, nothing below the hem line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、身体、辫子的方向和姿势照图1。
3. 长相、配色、细节全部换成图2：深蓝冰冠（两刃和青色月牙）、遮眼面罩、淡蓝下半脸和一格深蓝嘴唇、冰蓝编织长辫、青色水晶护肩、发青光的爪手、拖地深蓝长裙和裙摆冰晶；她没有腿，裙摆一直贴着地面。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 裙摆线 | `[animation]` |
|---|---|---|---|---|---|
| `lissandra_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `lissandra_run.png`（滑行） | 8 × 250 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `GLIDE, 8 frames, one seamless loop (League's run: she floats forward, 2 s a cycle - no steps): the body leaning a little forward, the arms trailing a little back with the claws open, the braid streaming behind; the gown's hem stays on the hem line and ripples (its crystals shift by a square from frame to frame); the body sways up and down by at most 1 square; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `lissandra_attack.png`（普攻（冰弹）） | 6 帧：70 70 80 80 70 63 | 第 4 帧（tick 13） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (an ice bolt from the near hand), 6 frames: 1 the idle stance; 2 the near arm draws back, the claw cupped; 3 the wind-up, the near arm raised; 4 THE CAST (the bolt leaves here): the near arm flung forward to the right at shoulder height, the claw open; 5 the follow-through; 6 back toward the idle stance. The bolt is an effect - do not draw it.` |
| `lissandra_skill.png`（Q 寒冰碎片） | 6 帧：60 70 70 80 80 73 | 第 4 帧（tick 12） | 3 列 × 2 行，3072×1536 | 第 81 行 | `ICE SHARD (Q), 6 frames: 1 she gathers, both arms drawn in; 2 the body twists back, the near arm swept far back, the braid swinging; 3 the wind-up at its fullest; 4 THE THROW (the shard leaves here): the body turned forward, the near arm thrust straight forward to the right, the claw open, the far arm back; 5 the follow-through; 6 back toward the idle stance. The shard is an effect.` |
| `lissandra_skill2.png`（W 冰霜之环） | 5 帧：60 70 80 90 100 | — | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `RING OF FROST (W), 5 frames: 1 both arms snap down and out to the sides, the claws spread, the braid flying up behind; 2-3 holding the arms flung wide and low; 4 the arms rising back; 5 toward the idle stance. The ring of ice around her is an effect.` |
| `lissandra_skill2_e.png`（E 冰川之径（掷冰爪）） | 6 帧：60 80 90 120 160 223 | 第 2 帧（tick 4） | 3 列 × 2 行，3072×1536 | 第 81 行 | `GLACIAL PATH (E, she hurls the claw and waits to glide after it), 6 frames: 1 she gathers, the near arm drawn back; 2 THE THROW (the claw leaves here): the near arm swung forward and low to the right; 3-6 she holds the arm forward and leans after it, slowly straightening (frames 4-6 differ by at most a square: a held pose). The claw and the ice path are effects.` |
| `lissandra_ult.png`（R 冰封陵墓（冻敌人）） | 5 帧：80 80 90 100 150 | 第 3 帧（tick 10） | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `FROZEN TOMB (R on an enemy), 5 frames: 1 both arms raised; 2 the arms high, the body arched back; 3 THE STRIKE (the tomb forms here): both arms swept down and forward to the right, the claws open, the body bent forward; 4 the follow-through, low; 5 rising back toward the idle stance. The ice tomb is an effect.` |
| `lissandra_ult_self.png`（R 冰封陵墓（冻自己，定格）） | 5 × 500 | — | 3 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `FROZEN TOMB ON HERSELF, 5 frames, a held loop (she stands frozen 2.5 s): upright, both arms spread out to the sides and a little up, the claws open, the chin up; only the braid and the gown's hem move by at most a square from frame to frame; frame 5 flows into frame 1. The ice block around her is an effect - do not draw it.` |
| `lissandra_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: her body and crown pushed back 1-2 squares (to the left), the braid swinging; 2 recovering toward the idle stance. The hem stays on the hem line.` |
| `lissandra_dead.png`（死亡（冻成冰雕）） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death, see refs/lol_death_crystals.png): 1-2 struck, she throws her head back and both arms rise; 3-4 dark ice crystals (the gown's navy and steel-blue) burst up from the hem round her gown; 5-6 the crystals climb to her waist, then to her chest, the arms still raised; 7-8 she stands frozen as an ice statue: the same pose in 7 and 8, the crystals up to her chest, her raised arms and head above them (the head stays visible from the 3/4 front, never upside down). Nothing below the hem line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的冠刃、头发、描边；
- [ ] 每帧都有辫子、两只发光的手和水晶护肩；没有腿，裙摆贴着裙摆线；
- [ ] 裙摆线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 滑行循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效（死亡的冰晶除外）、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `lissandra_<动作>.png` 先检查（严格方块、二值透明、色板、裙摆线、连通块、手臂粗细、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`lissandra_cells.json` 用包里这份，`lissandra_idle.png` 用包里已做好的那张。
- `import_native.py --hero lissandra`：ORDER 待机一张图 + BOB 呼吸（缝选在长裙的直段），COMPLETE + CLEAN 补描边、清黑边。
- 按出手帧核对技能数据的时机（普攻 tick 13、Q tick 12），量出手那只手的位置定弹道的出手点（y_offset），量头像截取点，重跑模拟，做预览 GIF。
