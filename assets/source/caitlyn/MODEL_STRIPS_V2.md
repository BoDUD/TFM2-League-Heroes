# 皮城女警 凯特琳：第二版造型的动作帧（给 Codex 的提示词）

> **为什么重画**：玩家说凯特琳「腿太短、太胖」。新造型已经定了（用户：「OK完美」）：`design/caitlyn_design.png` —— 你画的 v2 方案 A 的身体（瘦、腿长、直腿、棕色长靴、A 的长步枪），头换回第一版的头（紫色高礼帽、深蓝长发、用户认可的脸），帽子和两侧头发收小了一点。站着 **45 格高、28 格宽**，35 色。**造型图就是标准**。
> - **待机条已经做好**（`caitlyn_idle.png`），不用画。其余 9 张动作图按下面的表重画。
> - **动作照第一版的动作条**（`old/caitlyn_old_<动作>.png`，第一版的身体，用户都看过、认可了这些动作），帧数、每帧时长、出手帧、站位照 `now/caitlyn_now_<动作>.png`（英雄联盟原版按游戏尺寸取色），身体怎么动看 `pose/lol_pose_<动作>.png`（同一帧的渲染，已经按新身材的比例出图）。**身体、腿、步枪照新造型**：腿要长、要细，步枪和造型图一样长。
> - 交回的图每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`、`manifest.json`（每帧的格子矩形、站位点、bbox），打包成 `caitlyn_strips_v2_done.zip` 放在 outputs 里（`outputs/caitlyn-strips-v2/`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序见通用提示词（造型图、now 条、lol_pose、第一版的动作条）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/caitlyn_palette.png`）。**先把眼睛的蓝 `#1454A9` 从色板里去掉**，它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/caitlyn_head_1x.png`：高礼帽、宝石、帽檐、两侧长发、脸；在 128×128 画布上的范围 x 51–70、y 55–70）原样贴进每一帧头的位置，只平移；身体倾斜时整体倾斜；死亡倒地的帧可以不贴。眼睛在第 66 行，身体（衣领）从第 71 行开始：**每一帧眼睛到衣领都是 5 行**，不能把头压进身体，也不要拉出一截脖子。受击第 1 帧把眼睛改成闭眼（眼睛那一行各一段深色短线）。下巴以下的长发跟着身体动（披在背后）。
5. **步枪**：和造型图一样长（约 29 格）、直的、不断开，金色枪管上下有描边，青色枪口；两只手都握在枪上。
6. 对位：每帧按 `caitlyn_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上，脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/caitlyn_design.png` | **新造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张的第一张附图 |
| `design/caitlyn_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/caitlyn_head.png`、`_1x.png` | 只有头，在画布上原来的位置 | 贴头 |
| `design/caitlyn_palette.png` | 造型图的全部 35 色（暗到亮） | 色板 |
| `caitlyn_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/caitlyn_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的渲染（新身材比例），同样的格子 | 第三张附图：身体和步枪的动作 |
| `old/caitlyn_old_<动作>.png` | **第一版造型的动作条（用户认可的动作）**，同样的格子 | 第四张附图：照它的姿势和节奏 |
| `guide/caitlyn_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `caitlyn_cells.json` | 每帧的站位点（格子里第几列、第几行）和帧时长 | 整理对位 |
| `refs/caitlyn_picture.png` | 用户选的原图 A（长相参考；比例以造型图为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（45 格），每个像素一个 8×8 方块，同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 35 种颜色**，大块纯色，不要抖动、噪点、零散的金色碎点；外轮廓 1 格近黑描边，里面用材质自己的暗色。
- **头每帧都是造型图的头**（逐格一样，只平移或整体倾斜）；眼睛的蓝 `#1454A9` 只用在眼睛上。
- **身体照造型图**：细腰、短裙、**长腿**（大腿藏青裤袜、金色袜带、棕色护膝、金色靴口、棕色长靴），两条腿各 3–4 格宽、中间有空隙，不要画成粗短腿。
- **步枪每帧都在**（死亡倒地后躺在她前面）：直的、完整的、和造型图一样长，握在两只手里，不能断开、不能飘开、不能挡脸。
- **开枪的那一帧枪管放低放平**：普攻、爆头、R 的出手帧，枪管是水平的，枪口离站位点最多 8 格高（子弹从枪口飞向目标的站位点，枪口太高子弹会歪）；后坐力用肩膀往后晃来表现，不要把枪口往上甩。
- **手和手臂**：手至少 2×2 格，手臂至少 3 格粗（含描边）；每帧整个人连成一块。
- **脚底线以下什么都不能有**（游戏在脚下画血条），只有死亡倒地的帧可以低 1–2 格。
- **移动循环**：两条腿交替迈步、前后交叉（前 4 帧一条腿在前，后 4 帧另一条腿在前，中间有两膝交叉的帧），两只鞋最多相距 12 格，不要大弓步；头相对站位点的横向位置每帧一样，上下起伏最多 1 格；首尾能接上。
- 3/4 正面朝右，看得到脸。**只画角色**：枪口火光、子弹、夹子、网、准星都是单独的特效，不要画。每个动作开始和结束都接近造型图的待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，不要洋红：会吃掉紫色）。不要网格线、边框、文字、编号、参考线。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附四张图：`design/caitlyn_design.png`、`now/caitlyn_now_<动作>.png`、`pose/lol_pose_<动作>.png`、`old/caitlyn_old_<动作>.png`。输出 `caitlyn_<动作>.png`。

```text
Four attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, slim long-legged body, boots and rifle exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames in the same grid - the motion of the body, the arms and the rifle. FOURTH: the previous, approved version of these frames drawn on an older, stubbier body - copy its poses and timing, but draw the FIRST image's slim body with long legs instead of its short legs.
The character: a chibi sheriff woman: a TALL PURPLE TOP HAT with gold stripes and a cyan gem, very long straight dark navy hair framing her face and falling behind her back, fair skin, blue eyes, a slim body in a purple short dress with gold trim and a white frill, brown gloves, LONG SLIM LEGS in navy tights with gold garters, brown knee pads and knee-high brown boots with gold tops. Her weapon is a long GOLD rifle held in both hands, as long as in the FIRST image.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (45 squares tall from the top of the hat to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 35 colors of the FIRST image, no new colors: #0A020E #0A0011 #0C0011 #0D0012 #0F0115 #100216 #110717 #23102D #211930 #1D1C34 #301A28 #341340 #402835 #272A50 #2F3158 #451B59 #30345C #522063 #683934 #7A4429 #5C2576 #915526 #1454A9 #CB516B #27CCE2 #D7AE50 #FCBE2E #FDC429 #E1A58E #E3CB92 #EAE0A8 #EDDDB1 #FAD3BA #FEEEA3 #F9F8F9. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it. Big flat areas; no dithering, no noise, no scattered gold specks.
The head (the top hat, the brim, the hair down to the chin, the face, eyes and mouth) is COPIED from the FIRST image in every frame, square for square, only moved (or tilted as a whole where the body leans). The body starts 5 rows under the eyes' row in every frame. The blue #1454A9 appears ONLY in the eyes. The rifle is in every frame, whole, STRAIGHT and as long as in the FIRST image, held in both hands; on the frame of a shot the barrel is LEVEL and LOW (the muzzle at most 8 squares above the standing point): the recoil moves her shoulders, never the muzzle upward. The hands at least 2x2 squares and the arms at least 3 squares thick; the whole figure is ONE connected piece in every frame. The legs stay as long and slim as in the FIRST image.
Feet line: in every cell the lowest row of her boots is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down (the lying frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in caitlyn_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate and cross.
3/4 FRONT view facing right, her face always visible. Do not draw effects (muzzle flashes, bullets, the trap, the net, crosshairs, glows) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `caitlyn_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `caitlyn_run.png`（移动） | 8 × 117 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop (as the FOURTH image's run): she jogs forward with the rifle held across her chest as in the FIRST image; the long slim legs ALTERNATE - frames 1-4 one leg forward and planted while the other swings from behind past it (the knees crossing in frames 2-3), frames 5-8 the other way round; the shoes at most 12 squares apart; her head at the same place across the cell in all 8 frames, at most 1 square up or down; frame 8 flows into frame 1.` |
| `caitlyn_attack.png`（普攻） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, a rifle shot, 6 frames (the FOURTH image's motion): 1 from the idle she brings the rifle level to her hip; 2 aiming level to the right; 3 THE SHOT (the bullet leaves here): the barrel LEVEL and LOW, the recoil only rocks her shoulders back 1 square; 4 still aiming level; 5 lowering; 6 back toward the idle.` |
| `caitlyn_passive.png`（爆头（被动的强化射击）） | 6 帧：60 50 50 70 70 67 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `HEADSHOT, the strong shot, 6 frames: 1 a wider, lower stance, the rifle coming level; 2-3 steady, aiming level to the right; 4 THE SHOT (the bullet leaves here): the barrel LEVEL and LOW, a big recoil in her shoulders and hair, never the muzzle up; 5 recovering; 6 rising back toward the idle.` |
| `caitlyn_skill.png`（Q 和平使者） | 8 帧：70 70 70 70 60 60 100 167 | 第 7 帧（tick 24） | 4 列 × 2 行，3072×1536 | 第 81 行 | `PILTOVER PEACEMAKER, 8 frames: 1 she twirls the rifle up over her shoulder; 2 swinging it down in front of her; 3 she drops to one knee; 4-6 kneeling, aiming the rifle level to the right, perfectly steady; 7 THE SHOT (the big round leaves here): the barrel level, her shoulders pushed back; 8 rising back toward the idle.` |
| `caitlyn_skill2.png`（W 约德尔诱捕器（扔夹子）） | 6 帧：60 50 57 80 80 73 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `YORDLE SNAP TRAP, 6 frames: 1 she lifts the rifle upright in her near hand; 2 she bends forward; 3 crouching, she reaches down and forward with her free hand; 4 THE THROW (the trap leaves here): her free hand flicks forward and low to the right - draw NO trap; 5 straightening up; 6 back toward the idle.` |
| `caitlyn_e.png`（E 90口径绳网（射网后跳）） | 8 帧：50 50 67 67 67 83 100 83 | 第 3 帧（tick 6） | 4 列 × 2 行，3072×1536 | 第 81 行 | `90 CALIBER NET, 8 frames: 1 she braces, the rifle pointed forward and a little down; 2 crouched, aiming low to the right; 3 THE NET SHOT (draw NO net): the recoil throws her backward off her feet; 4-5 flying backward, at most 5 squares above the ground line, the rifle still pointing forward, her knees tucked; 6 landing on her feet, knees bent; 7 crouched, recovering; 8 back toward the idle.` |
| `caitlyn_ult.png`（R 让子弹飞（跪射）） | 9 帧：100 100 200 200 200 217 150 150 83 | 第 7 帧（tick 61） | 4 列 × 3 行，3072×2304，最后 3 格空 | 第 81 行 | `ACE IN THE HOLE, 9 frames: 1 she swings the rifle up; 2 she drops to one knee; 3-6 kneeling, aiming down the long rifle to the right, perfectly still (frames 3-6 almost the same); 7 THE SHOT (the bullet leaves here): the barrel level, her shoulder rocks back; 8 still kneeling, lowering the rifle; 9 rising toward the idle.` |
| `caitlyn_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back 1 square, eyes squeezed shut (two short dark lines on the eyes' row); 2 recovering toward the idle.` |
| `caitlyn_dead.png`（死亡） | 8 帧：100 100 110 110 120 130 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames: 1 struck, staggering; 2-5 she sinks to one knee, leaning on the rifle planted upright beside her (the hat still on); 6 she topples over; 7-8 lying on her side on the ground line, the hat beside her head, the rifle lying in front of her. Frames 7-8 may reach 2 squares below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；只用造型图色板里的颜色；
- [ ] 每一帧站着时和造型图一样高（45 格）；头就是造型图的头（逐格一样，只平移），两只眼睛都在、同一行；眼睛到衣领 5 行；
- [ ] 眼睛的蓝 `#1454A9` 只出现在眼睛上；
- [ ] 腿和造型图一样长、一样细；步枪每帧都在、直的、和造型图一样长；开枪那一帧枪管水平、枪口离站位点不超过 8 格；
- [ ] 手至少 2×2 格、手臂至少 3 格粗；每帧整个人连成一块；脚底线以下没有任何像素（死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替、前后交叉，两只鞋最多相距 12 格，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

