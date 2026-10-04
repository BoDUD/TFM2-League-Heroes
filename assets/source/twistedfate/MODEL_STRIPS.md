# 崔斯特：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/twistedfate_design.png`（放大 8 倍，1024×1024；帽顶到脚底 41 行，24 格宽，21 色；脚底在第 99 行，两脚中间在第 64 列）。它是你上一轮生成原稿（`refs/twistedfate_draft_codex.png`）按格子读回、整行整列删到 40 行的版本。**造型图就是标准**：黑色宽檐帽（红色帽檐底、金边）、帽檐下的脸和青色眼睛、胡子、黑色长发、金边黑长外套和红色里衬、红马甲、白领子、棕色长靴、近侧手里的那把牌（蓝、红、金），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`twistedfate_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/twistedfate_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（大帽子、Q 版头、40 行高）；② 头是贴上去的（见下），**头每帧不变形、不旋转、始终是造型图的 3/4 正面**（死亡倒地时整个头跟着身体转），**不画背影**；③ **原版模型手里没有牌，我们每一帧都要画**：the FAN OF CARDS (blue, red, gold, as in design/twistedfate_cards.png) is in his NEAR hand in EVERY frame - held between the fingers, touching the hand, never floating, never dropped (only in the death may the hand open); it moves with the hand. The card he THROWS is an effect: in a throw frame the fan stays in the hand, nothing flies；④ 帽子和外套：the wide-brimmed hat stays on his head in every frame exactly as in the design (the red underside, the gold trim, the crown); the long coat's skirt sways and flares with the motion (its red lining shows) but keeps the design's length and colours。
> - **腿**：in every standing frame (attack, W, Destiny, hit) the legs are the design's own legs square for square - the same stance and the same brown boots; only Wild Cards' small hop lifts the same legs off the ground, the Gate's channel bends the knees, the walk alternates them and the death kneels and falls。
> - 出招方向：**甩牌、扔牌都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/twistedfate-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和 `generation_prompts.json`，最好打成一个 zip（`twistedfate_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**不要把细节比方块还小的高清图压缩下来**。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/twistedfate_palette.png`，或直接读 `design/twistedfate_design_1x.png`）。
4. **贴头**：把造型图的头（`design/twistedfate_head_1x.png` 里不透明的格子：帽子、帽檐下的脸、青色眼睛、胡子、到下巴为止的头发；在 128×128 画布上的范围 x 49–72、y 59–76，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡倒地时整个头跟着转）。这样每帧的脸都和造型图一模一样。贴之前先擦掉你自己画的头，不要在头的旁边留下多余的帽檐、头发或描边。
5. **牌**：那把牌照 `design/twistedfate_cards_1x.png`（蓝、红、金三张，下面是拿牌的手和白袖口），每帧都在近侧手里、和手连着。
6. 对位：每帧按 `twistedfate_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/twistedfate_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/twistedfate_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/twistedfate_head.png`、`_1x.png` | 要贴进每一帧的头（帽子、脸、青色眼睛、胡子、到下巴的头发） | 贴头 |
| `design/twistedfate_cards.png`、`_1x.png` | 近侧手里的那把牌（蓝、红、金）和拿牌的手 | 牌的样子 |
| `design/twistedfate_palette.png` | 造型图的全部 21 色（暗到亮） | 色板 |
| `twistedfate_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/twistedfate_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/twistedfate_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `twistedfate_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/twistedfate_picture.png`、`refs/twistedfate_draft_codex.png` | 用户选的原画 A 和你画的生成原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（帽顶到脚底 41 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 21 种颜色**，不加新颜色；明暗照定稿（黑外套的亮边、金边跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边（`#0D0B12`），描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手和手臂**：袖子 2–3 格粗、金色袖箍、白袖口、实心的手；**不要 1 像素的黑细棍、不要飘着的手**，拿牌的手和牌连在一起。
- **牌**：the FAN OF CARDS (blue, red, gold, as in design/twistedfate_cards.png) is in his NEAR hand in EVERY frame - held between the fingers, touching the hand, never floating, never dropped (only in the death may the hand open); it moves with the hand. The card he THROWS is an effect: in a throw frame the fan stays in the hand, nothing flies。
- **帽子和外套**：the wide-brimmed hat stays on his head in every frame exactly as in the design (the red underside, the gold trim, the crown); the long coat's skirt sways and flares with the motion (its red lining shows) but keeps the design's length and colours。
- **腿**：in every standing frame (attack, W, Destiny, hit) the legs are the design's own legs square for square - the same stance and the same brown boots; only Wild Cards' small hop lifts the same legs off the ground, the Gate's channel bends the knees, the walk alternates them and the death kneels and falls。
- **头每帧都是造型图的头**（帽子、脸、青色眼睛、胡子逐格一样），只平移（死亡倒地时整个转）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），外套下摆在它上面。只有死亡时掉在地上的牌和帽子可以贴着脚底线。
- **走路循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：飞出去的牌、牌的光、头顶轮换的牌、命运的眼睛、传送门的光、骰子都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，**不要洋红**）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/twistedfate_design.png`，第二张 `now/twistedfate_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `twistedfate_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, hat, coat, cards and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same wide-brimmed black hat with the red underside and gold trim, the face under it with the cyan eye and the beard, the long black hair, the gold-trimmed black long coat with its red lining, the red waistcoat, the brown boots, the fan of blue, red and gold cards in his near hand, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the throw, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the legs and the body from it, but keep the FIRST image's proportions (a big hat, a big chibi head, 40 squares tall); never draw him from the back or upside down.
The character: Twisted Fate (a card-master gambler in a wide-brimmed black hat with a red underside and gold trim, a goatee and long black hair, a gold-trimmed black long coat with a red lining, a red waistcoat, brown boots, a fan of blue, red and gold playing cards in his near hand).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares from the hat's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 21 colors of the FIRST image, no new colors: #0D0B12 #171925 #3A2214 #5C0C14 #262A3A #6B3B26 #3A4057 #6B4224 #7A4A0E #A3141E #1A3CD0 #E0302A #A8643E #A8743A #C08A1C #D58C5C #F2C23A #5A9CFF #B8BCC8 #7AF4FF #F2F2F6. ONE outline: a 1-square near-black outline (#0D0B12) around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading - the lit edges of the black coat and the gold trims move with the pose; no dithering, no noise, no random specks added. Hands are solid at the ends of sleeves 2-3 squares wide with gold cuffs - never 1-pixel black sticks or floating hands.
The cards are his signature: the FAN OF CARDS (blue, red, gold, as in design/twistedfate_cards.png) is in his NEAR hand in EVERY frame - held between the fingers, touching the hand, never floating, never dropped (only in the death may the hand open); it moves with the hand. The card he THROWS is an effect: in a throw frame the fan stays in the hand, nothing flies.
The hat and the coat: the wide-brimmed hat stays on his head in every frame exactly as in the design (the red underside, the gold trim, the crown); the long coat's skirt sways and flares with the motion (its red lining shows) but keeps the design's length and colours.
The legs: in every standing frame (attack, W, Destiny, hit) the legs are the design's own legs square for square - the same stance and the same brown boots; only Wild Cards' small hop lifts the same legs off the ground, the Gate's channel bends the knees, the walk alternates them and the death kneels and falls.
The head (the hat, the face under the brim with the cyan eye, the beard, the hair down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. Erase your own head before pasting it, so no extra brim, hair or outline is left beside it.
Feet line: in every cell his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the coat's hem, not a card - because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in twistedfate_cells.json). In the walk his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
3/4 front view like the FIRST image; every throw goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (flying cards, card glow, the cards cycling over his head, the destiny eye, the gate's light, dice) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x96 squares (1024x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green, never magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the fan of cards in the near hand in every frame and touching it, the hat on his head, the idle's legs in every standing frame, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `twistedfate_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | **已做好，不用画** |
| `twistedfate_run.png`（走路） | 8 × 217 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `WALK, 8 frames, one seamless loop (League's walk at his base speed: an upright, confident stroll, 1.7 s a cycle): the body upright, the head steady; the fan of cards held at the hip in the near hand, the far arm swinging gently with the step; the long coat swinging behind his legs; in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 2-3 and 6-7 (the legs CROSS - never the same stance in all frames), both legs the same black trousers and brown boots; the body bobs at most 1 square; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `twistedfate_attack.png`（普攻（甩牌）） | 6 帧：60 70 70 70 80 83 | 第 4 帧（tick 12） | 3 列 × 2 行，3072×1536 | 第 81 行 | `BASIC ATTACK (he flicks a card), 6 frames: 1 the idle stance; 2 the near hand with the fan draws back across his chest; 3 the wind-up at its fullest, the near elbow raised; 4 THE THROW (the card leaves here): the near arm flung forward to the right at shoulder height, the wrist snapped, the fan still in the hand; 5 the follow-through; 6 back toward the idle stance. The flying card is an effect - do not draw it.` |
| `twistedfate_skill.png`（Q 万能牌（扇形扔牌）） | 6 帧：60 70 70 70 70 60 | 第 4 帧（tick 12） | 3 列 × 2 行，3072×1536 | 第 81 行 | `WILD CARDS (Q: he throws three cards in a fan), 6 frames: 1 he gathers, the fan raised to his chest; 2 a small hop (1-2 squares off the ground, the SAME legs lifted), the near arm drawn back; 3 landing in a low crouch, the arm far back; 4 THE THROW (the cards leave here): crouched, the near arm swept forward to the right at chest height, the fan spread WIDE in the hand; 5 the follow-through, still low; 6 rising back toward the idle stance. The three flying cards are effects - do not draw them.` |
| `twistedfate_skill2.png`（W 选牌（起手洗牌）） | 2 帧：80 87 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `PICK A CARD (W: he starts shuffling), 2 frames: 1 the near hand lifts the fan to his chest; 2 he flicks the fan open at the chest, the cards spread. The cards cycling over his head are an effect.` |
| `twistedfate_ult.png`（R 命运（张开双臂）） | 4 帧：100 130 130 140 | — | 4 列 × 1 行，4096×768 | 第 81 行 | `DESTINY (R: he reads the fates), 4 frames: 1 the arms begin to open; 2 both arms spread wide at shoulder height, the fan in the near hand, the far hand open; 3 holding, the chin a little up; 4 holding. The glowing eye and the light are effects.` |
| `twistedfate_ult_gate.png`（R 传送之门的引导（蹲下）） | 6 × 250 | — | 3 列 × 2 行，3072×1536 | 第 81 行 | `GATE'S CHANNEL (he gathers to teleport), 6 frames, a slow loop: a low crouch, knees bent, the far hand raised beside his face, the fan in the near hand held up in front of his chest; the coat flaring behind him; only a slight sway from frame to frame (1 square at most), frame 6 flowing into frame 1. The gate's swirl around him is an effect.` |
| `twistedfate_ult_land.png`（R 落地（站起）） | 3 帧：110 110 113 | — | 3 列 × 1 行，3072×768 | 第 81 行 | `GATE'S ARRIVAL, 3 frames: 1 the channel's low crouch; 2 rising, half way; 3 the idle stance.` |
| `twistedfate_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and hat pushed back 1-2 squares (to the left), the coat swaying; 2 recovering toward the idle stance.` |
| `twistedfate_dead.png`（死亡） | 8 帧：100 110 110 120 130 150 200 300 | — | 4 列 × 2 行，4096×1536 | 第 81 行 | `DEATH, 8 frames (League's death): 1-2 struck, he staggers back; 3-4 he stumbles, the hat tipping; 5 he falls to his knees; 6 kneeling, slumping; 7-8 lying on the ground on his side, the hat beside his head (the same pose in 7 and 8); the head stays visible from the 3/4 front (turned down, never upside down). The cards may spill on the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡倒地时整个转），头旁边没有多余的帽檐、头发、描边；
- [ ] **那把牌每帧都在近侧手里**（蓝、红、金看得出来），和手连着；帽子每帧都在头上；
- [ ] 站着出招的帧腿和待机一模一样；走路两条腿交叉迈步、颜色一样；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 走路循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点、bbox 和出手帧那只手的位置都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `twistedfate_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、牌在不在手里、零散黑格、每帧面积和待机比），不在网格上的重新取样；头不对的帧换回造型图的头，头旁边的残留清掉。
- 放进 `assets/source/native/`，`twistedfate_cells.json` 用包里这份，`twistedfate_idle.png` 用包里已做好的那张。
- `import_native.py --hero twistedfate`：ORDER 待机一张图 + BOB 呼吸（缝选在靴筒的直段），COMPLETE + CLEAN 补描边、清黑边，NECK 检查头每帧在领子上同一行。
- 按出手帧核对技能数据的时机（普攻 tick 12、Q tick 12），量出手那只手的位置定牌的出手点（y_offset），量头像截取点，重跑模拟，做预览 GIF。
