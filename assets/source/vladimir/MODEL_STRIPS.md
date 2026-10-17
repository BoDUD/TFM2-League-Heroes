# 弗拉基米尔：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/vladimir_design.png`（放大 8 倍，1024×1024）：发尖到脚底 40 行，28 格宽，19 色；脚底在第 99 行，两脚中间在第 64 列。这张是在你上一轮生图稿的基础上逐格整理出来的，**造型图就是标准**：向上梳的银白尖顶头发、苍白的脸和两只红眼、脑后巨大的深红高领（桃色镶边）、深红长礼服（桃色镶边）、胸前三个钢扣、带尖刺的钢护肩、大袖口（桃色边 + 钢色宝石）、每只手的钢爪、分成两片的外套后摆、红粉竖条纹裤、浅色护膝、带钢头的红鞋，颜色、明暗每一帧都照它，只改姿势。
> - **待机条已经做好**（`vladimir_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - **跑步单独做，用「骨架 + 皮囊」**：`run_swap/` 里 图1 = oppi 的斯维因跑步（穿长外套的法师，动作骨架，8 帧），图2 = 定稿造型（皮囊），照 `run_swap/PROMPT.md` 的中文提示词画，交 `vladimir_run.png`，排版和图1一样。**两条腿一定要前后交替、膝盖交叉**（以前好几个英雄跑步是平行走路，被退回过）。
> - 其余 7 张动作图按下面的表画：帧数、每帧时长、出手帧和站位照 `now/vladimir_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例；② 头（尖顶头发 + 脸 + 两侧垂发 + 脑后高领）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**，**不画背影**；③ **腿**：in every standing frame (idle, attack, Q, E, R, hit) he stands on the design's OWN legs square for square: the striped red-and-pink trousers, the pale knee cuffs, the red shins and the two red shoes with steel toes, the same place and width as the design, never spread, never longer; the arms, the claws, the coat-tails and the collar move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs)；④ 装备：the tall flared crimson collar with its peach rim standing behind his head (part of the head piece, see below), the crimson frock coat with peach trims, the THREE steel clasps down the chest (light top, dark bottom), the spiky steel pauldrons on both shoulders, the big crimson cuffs with a peach rim and a steel gem, the steel claws on both hands (3-4 per hand), the two coat-tails split over the striped trousers stay in every frame (the W pool and the death: as the table says)；⑤ 手臂：the arms are the design's crimson sleeves with the big cuffs, as thick as in the design (the sleeve 3 squares, the cuff 5) - never thinner, never 1-pixel sticks, never floating hands; the steel claws are 1-square wedges with a lit edge growing out of the hand, 3-4 per hand, never lost。
> - 出招方向：**伸手、甩血弹、抽血都朝图的右边**（游戏里朝左时会整张镜像）。
> - **W 血池**：第 4、5 帧没有身体，只有地上一滩冒泡的血池（见表）；第 2、3、6、7 帧身体陷在血里，只贴露在外面那部分头。
> - **死亡照英雄联盟**：跪倒后仰面倒在地上，外套摊开（见表）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/vladimir_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/vladimir_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/vladimir-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`vladimir_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/vladimir_palette.png`，或直接读 `design/vladimir_design_1x.png`）。红眼的两种颜色（#FF2A2A、#FFC8C8）**只用在眼睛上**。
4. **贴头**：把造型图的头（`design/vladimir_head_1x.png` 里不透明的格子：尖顶头发、脸、两只眼睛、两侧垂发、脑后高领的两翼；在 128×128 画布上的范围 x 51–76、y 60–72，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头和高领，不要在头旁边留下多余的头发、领子或描边。**头下面要接上肩膀和胸口**（高领下沿紧挨着护肩和第一个钢扣），不要在下巴下面留出一截空隙或长出一截脖子。
5. 对位：每帧按 `vladimir_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/vladimir_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/vladimir_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/vladimir_head.png`、`_1x.png` | 要贴进每一帧的头（尖顶头发、脸、眼睛、两侧垂发、高领两翼） | 贴头 |
| `design/vladimir_palette.png` | 造型图的全部 19 色（暗到亮） | 色板 |
| `vladimir_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `run_swap/` | 跑步的骨架（oppi 的斯维因跑步，已按我们的大小放大）、皮囊（定稿）和中文提示词 | **跑步照这里画** |
| `now/vladimir_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/vladimir_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `vladimir_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/vladimir_picture.png`、`refs/vladimir_draft_codex.png` | 用户选的原画 A 和你上一轮的生图稿（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 19 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every standing frame (idle, attack, Q, E, R, hit) he stands on the design's OWN legs square for square: the striped red-and-pink trousers, the pale knee cuffs, the red shins and the two red shoes with steel toes, the same place and width as the design, never spread, never longer; the arms, the claws, the coat-tails and the collar move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs)。
- **装备**：the tall flared crimson collar with its peach rim standing behind his head (part of the head piece, see below), the crimson frock coat with peach trims, the THREE steel clasps down the chest (light top, dark bottom), the spiky steel pauldrons on both shoulders, the big crimson cuffs with a peach rim and a steel gem, the steel claws on both hands (3-4 per hand), the two coat-tails split over the striped trousers stay in every frame (the W pool and the death: as the table says)。
- **手臂**：the arms are the design's crimson sleeves with the big cuffs, as thick as in the design (the sleeve 3 squares, the cuff 5) - never thinner, never 1-pixel sticks, never floating hands; the steel claws are 1-square wedges with a lit edge growing out of the hand, 3-4 per hand, never lost。
- **头每帧都是造型图的头**（尖顶头发、脸、两只红眼、两侧垂发、高领两翼逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：血弹、血流、血球、血雾、瘟疫云都是单独的特效，不要画（W 的血池例外：它就是他的身体，要画）。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（普攻、Q、E、W、R、受击、死亡都用这一段，只替换中括号）

每张附三张图：第一张 `design/vladimir_design.png`，第二张 `now/vladimir_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `vladimir_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, collar, face, coat, claws and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the silver-white hair swept up into a pointed crest, the pale face with two red eyes, the tall flared crimson collar with its peach rim behind the head, the crimson frock coat with peach trims, the three steel clasps on the chest, the spiky steel pauldrons, the big cuffs with a steel gem, the steel claws on both hands, the split coat-tails, the striped trousers, the pale knee cuffs, the red shoes with steel toes, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the coat and the body from it, but keep the FIRST image's proportions and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Vladimir, the Crimson Reaper (a pale vampire aristocrat and blood mage in a crimson coat, with steel claws).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the hair crest's tip to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 19 colors of the FIRST image, no new colors: #1D010B #2E010D #5D0315 #910419 #DA010F #3D496A #FF2A2A #965B70 #B98495 #EC6C80 #87A1C6 #FA9C6B #F3909F #E1B3BB #FBC891 #FFC8C8 #F4E0CC #D5E6F7 #FCEBE8. The two eye reds (#FF2A2A, #FFC8C8) only in the eyes. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, attack, Q, E, R, hit) he stands on the design's OWN legs square for square: the striped red-and-pink trousers, the pale knee cuffs, the red shins and the two red shoes with steel toes, the same place and width as the design, never spread, never longer; the arms, the claws, the coat-tails and the collar move, the legs stay (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs).
Gear: the tall flared crimson collar with its peach rim standing behind his head (part of the head piece, see below), the crimson frock coat with peach trims, the THREE steel clasps down the chest (light top, dark bottom), the spiky steel pauldrons on both shoulders, the big crimson cuffs with a peach rim and a steel gem, the steel claws on both hands (3-4 per hand), the two coat-tails split over the striped trousers stay in every frame (the W pool and the death: as the table says).
The arms: the arms are the design's crimson sleeves with the big cuffs, as thick as in the design (the sleeve 3 squares, the cuff 5) - never thinner, never 1-pixel sticks, never floating hands; the steel claws are 1-square wedges with a lit edge growing out of the hand, 3-4 per hand, never lost.
The head (the hair crest, the face with both eyes, the side locks and the tall collar's two wings) is COPIED from the FIRST image in every frame, square for square, and only moved (tilted only while he falls in the death); never redraw, squash or tilt it otherwise, or it flickers when the frames play. Erase your own head and collar before pasting it, so no extra hair, collar or outline is left beside it; the collar's lower edge meets the pauldrons and the first clasp - no gap and no neck under the chin.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in vladimir_cells.json).
3/4 front view like the FIRST image; every throw, thrust and drain points to the RIGHT of the image; never his back, never upside down. Do not draw effects (blood bolts, blood streams, the blood orb, the burst, the plague cloud) - only the character (the W pool IS his body and is drawn). Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms with their cuffs and claws, both legs and shoes in every standing frame, the three clasps, the arms as thick as in the FIRST image, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、钢爪、外套后摆、身体的方向和姿势照图1，不转成背影；站着的动作腿用图2自己的腿（条纹裤、护膝、红鞋）。
3. 长相、配色、细节全部换成图2：向上梳的银白尖顶头发、苍白的脸和两只红眼、脑后巨大的深红高领（桃色镶边）、深红长礼服、胸前三个钢扣、带尖刺的钢护肩、大袖口（钢色宝石）、每只手的钢爪、分成两片的后摆、条纹裤、浅色护膝、带钢头的红鞋。头和高领每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `vladimir_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 80 行 | **已做好，不用画** |
| `vladimir_run.png`（跑步（在 run_swap/ 换皮）） | 8 × 120 | — | 4 列 × 2 行，3072×1536 | 第 80 行 | **不用这一行：用 `run_swap/` 的换皮画** |
| `vladimir_attack.png`（普攻（甩出血弹）） | 6 帧：60 60 70 70 80 80 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1536 | 第 80 行 | `BASIC ATTACK (League's: he flings a bolt of blood from his hand), 6 frames: 1 he draws the near clawed hand back beside his shoulder, the coat-tails swinging; 2 winding up, the far arm opening; 3 the near arm sweeping forward; 4 THE THROW (the blood bolt leaves the near hand here): the near arm stretched forward to the right at chest height, the claws open, the coat-tails flaring back; 5 the follow-through, both arms spreading; 6 back toward the idle stance. The blood bolt is an effect - do not draw it.` |
| `vladimir_skill.png`（Q 鲜血转换（前冲伸爪抽血）） | 6 帧：60 60 70 70 90 90 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1536 | 第 80 行 | `TRANSFUSION (Q), 6 frames (League's Q): 1 he lifts the near clawed hand; 2 leaning back a little, the claws raised; 3 a lunge (the WHOLE figure 1-2 squares to the right) with the near arm thrust toward the enemy; 4 THE DRAIN (the blood is torn out of the enemy here): the near arm fully stretched forward to the right at chest height, the claws hooked as if pulling, the coat-tails streaming back, a hungry grin; 5 pulling the clenched hand back toward his chest, savouring; 6 back toward the idle stance. The blood stream is an effect - do not draw it.` |
| `vladimir_skill2.png`（E 血之潮汐（举手蓄力，再张开双臂爆发）） | 7 帧：80 100 120 150 60 80 90 | 第 6 帧（tick 31） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 80 行 | `TIDES OF BLOOD (E), 7 frames (League's E: a charge, then a burst): 1-4 THE CHARGE: he raises the near clawed hand high above his head, palm up, the other hand down at his side, standing tall; frames 2-4 hold that pose with a slight sway (the hand 1 square higher / lower, the coat-tails stirring) - a blood orb gathers over the hand there (an effect, do not draw it); 5 he brings the hand down to his chest, crouching a little; 6 THE BURST (the blood bolts fly out in every direction here): both arms flung wide open to both sides, claws spread, chest out, the coat-tails flaring; 7 back toward the idle stance.` |
| `vladimir_skill_w.png`（W 血红之池（化成血池再升起）） | 8 帧：60 60 70 600 600 70 70 80 | 第 4 帧（tick 11） | 4 列 × 2 行，3072×1536 | 第 80 行 | `SANGUINE POOL (W), 8 frames (League's W: he melts into a pool of blood and rises from it): 1 he flinches, the arms pulled in to the chest; 2 MELTING: the whole body sinks and melts down into dark-red blood from the shoes up (about two thirds of his height left, the coat and arms running down as liquid, the head and collar lower but still the design's head); 3 only the collar's tips and the top of the head stick out of a spreading red puddle; 4 THE POOL: no body at all - a flat pool of dark-red blood on the ground, about 22 squares wide and 3-4 squares tall, the coat's reds with bright scarlet highlights and two or three round bubbles, a near-black outline, its bottom ON the feet line; 5 the same pool, the bubbles in other places (frames 4 and 5 loop while he is untargetable); 6 RISING: the head and collar coming up out of the pool, blood running off; 7 half risen, the arms spreading, the pool shrinking under his shoes; 8 back toward the idle stance. Where the body is sunk, paste only the part of the design's head that is above the pool.` |
| `vladimir_ult.png`（R 血之瘟疫（双臂交叉再大张）） | 6 帧：60 60 70 80 80 80 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1536 | 第 80 行 | `HEMOPLAGUE (R), 6 frames (League's R): 1 he crouches a little and crosses both clawed hands in front of his chest; 2 gathering, the shoulders hunched; 3 the arms opening; 4 THE CAST (the plague falls on the enemies here): both arms thrown wide open and up to both sides, the claws spread, the coat-tails flaring out, a cruel smile; 5 holding the pose; 6 back toward the idle stance. The blood cloud is an effect - do not draw it.` |
| `vladimir_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 80 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body pushed back 1-2 squares (to the left), the collar and the head tilting back a little, the arms flung out; 2 recovering toward the idle stance. The design's legs.` |
| `vladimir_dead.png`（死亡（跪倒后仰面倒地）） | 8 帧：100 100 100 120 120 150 200 500 | — | 4 列 × 2 行，3072×1536 | 第 80 行 | `DEATH, 8 frames (League's death: he sinks to his knees and falls on his back): 1 struck, he jolts back; 2 he staggers, the knees buckling; 3 down on his knees, the coat-tails spread on the ground around him; 4 falling backward; 5 hitting the ground; 6-8 lying on his back on the ground, the coat spread round him, the arms limp, the head (the design's head turned on its side) at the left end; 7 and 8 the same pose. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样（跑步和 `run_swap/1_动作骨架_oppi跑步.png` 一样），帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；红眼的颜色只在眼睛上；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、领子、描边，下巴下面没有空隙；
- [ ] 每帧都有两只袖口和钢爪、三个钢扣、两条腿和鞋（W 血池和死亡按表）；手臂和造型图一样粗；站着的动作是造型图自己的腿；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步：两条腿前后交替、膝盖交叉，头的横向位置每帧一样，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效（W 的血池除外）、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `vladimir_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`vladimir_cells.json` 用包里这份（跑步用 `run_swap/run_layout.json`，8 × 120 毫秒），`vladimir_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q tick 11、E tick 31、W 血池开始 tick 11、R tick 11），量头像截取点，重跑模拟，做预览 GIF。
