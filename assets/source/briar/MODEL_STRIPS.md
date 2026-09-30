# 贝蕾亚：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：B 版、嘴 3（两格深红）**。Claude 按你交回的 76 格稿逐行逐列删减缩到游戏尺寸（46 格高，含枷锁；没有平均模糊），整理了描边，补了睫毛，把两只眼睛做成同样大小、同一高度：`design/briar_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799）。**造型图就是标准**，颜色、形状、头、脸、枷锁一律照它。
> - **待机条已经做好**（`briar_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/briar_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。英雄联盟里枷锁是一根横杠，**我们的造型是用户图里的拱形枷锁**，每帧都照造型图画拱形枷锁。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/briar_palette.png`，或直接读 `design/briar_design_1x.png`）。**先把两个眼睛颜色 `#F0FCFF`、`#C5E6F5` 从色板里去掉**（它们和头发、皮肤的颜色很近，一吸附就会跑到身上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/briar_head_1x.png`：只有头发、脸、眼睛、嘴和它们的描边，枷锁已去掉；在 128×128 画布上的范围 x 56–71、y 65–79）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。这样每帧的脸都和造型图一模一样。尖叫（`skill2_scream` 第 2–3 帧）和咬（`attack` 第 3–4 帧）的帧，贴头后把嘴改成张开的深红色（2 格宽 2 格高）。受击第 1 帧把眼睛改成闭眼（眼睛那两行各一段深色短线）。
5. 对位：每帧按 `briar_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/briar_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/briar_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/briar_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `briar_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/briar_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/briar_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `briar_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/briar_picture.png` | 用户给的原图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（46 格，含枷锁），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（头发、脸、眼睛、嘴逐格一样），只平移或整体倾斜；眼睛两只一样大、同一行，不能连成横杠，冰白 `#F0FCFF` 和淡蓝 `#C5E6F5` 只用在眼睛上。
- **枷锁每帧都在**：黑铁拱形、金边金刺、顶上的红宝石，两端锁着她的手腕，跟着手臂和肩膀动，不能飘开，不能挡脸。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面）。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变，只动腿、手臂、衣摆、枷锁；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，不画背影（死亡最后趴下的帧除外）。**只画角色**：宝石飞出、尖啸的声波、落地的爆炸、流血这些都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/briar_design.png`，第二张 `now/briar_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `briar_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, pillory and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look (and NOT its straight bar-shaped restraint: our design has an arched pillory). THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
The character: Briar (a chibi vampire girl with messy white hair whose lower ends are rose-red, milky-white glowing eyes, pale skin, a torn black leather dress with gold straps and a crimson under-layer, bare legs with dark shackle bands and bare clawed feet; behind her head and shoulders a big black iron pillory with gold edges, gold spikes and a red diamond gem at the top, its two ends locking her wrists at shoulder height).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (46 squares tall from the gem to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #160F19 #211C29 #292930 #373039 #690E2E #3D3E43 #51414A #96203E #735538 #65636A #C93652 #A48149 #887A82 #977A87 #CEAB61 #B5A3A7 #C9A8B5 #D5C5C0 #E9CAD1 #C5E6F5 #EEE6DB #F6DFDF #F0FCFF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (hair, face, eyes, mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. The black-and-gold pillory with the red gem is in every frame, its two lower ends locked on her wrists: it moves with her arms and shoulders, never floats free, never covers her face. Her eyes are the FIRST image's milky eyes (ice-white #F0FCFF with the pale-blue top row #C5E6F5 and a dark lash row above), both the same size on the same rows, never merged into a bar; those two eye colours appear ONLY in the eyes. The mouth is the FIRST image's two dark-red squares, except where the line below says she screams or bites.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the pillory, not the dress - because the game draws the health bar there (a fall may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in briar_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame.
3/4 FRONT view facing right, never her back (except a frame lying face down). Do not draw effects (the gem, sound waves, blasts, blood, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `briar_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `briar_run.png` | 8 × 125 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (1 s cycle, 8 x 125 ms, the SECOND and THIRD images): she runs hunched forward, her hands still locked in the pillory at shoulder height so the pillory rocks with her steps, the bare feet striding as in the THIRD image (frames 1-4 one stride, 5-8 the other); her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `briar_attack.png` | 6 帧：60 60 70 70 80 80 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, 6 frames: a lunging headbutt-bite as in the THIRD image: 1 she crouches, head drawn down; 2 she springs forward; 3 the release (the hit lands here): her head thrust far forward to the right, mouth open to bite, body leaning forward, the pillory swinging up behind her; 4 held; 5-6 back toward the idle stance.` |
| `briar_skill.png` | 6 帧：50 50 60 60 80 100 | 第 5 帧（tick 13） | 3 列 × 2 行，2304×1536 | 第 81 行 | `HEAD RUSH (a leap onto the target), 6 frames: 1 she crouches low, gathering; 2 she springs up and forward; 3-4 flying forward head first, body stretched out horizontally, the pillory held up behind her head (League does a full forward flip here - keep her head never more than a quarter turn from upright); 5 the impact (the headbutt lands here): she slams down head first onto the target in front of her, crouched; 6 rising back toward the idle stance.` |
| `briar_skill2.png` | 6 帧：160 160 170 170 170 170 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | `CHILLING SCREAM, the charge, 6 frames that loop while she charges (1 s): 1-2 she crouches, hunching forward, head down, the pillory lowered; 3-4 she rears up and back, chest out, head tilted back, the pillory raised; 5-6 held rearing back, trembling a little (a 1-square shift at most). Mouth closed. The feet stay planted.` |
| `briar_skill2_scream.png` | 4 帧：60 80 100 100 | 第 2 帧（tick 4） | 4 列 × 1 行，3072×768 | 第 81 行 | `CHILLING SCREAM, the scream, 4 frames: 1 still reared back; 2 the release (the scream leaves here): she thrusts her head forward to the right and screams, mouth wide open (a dark-red open mouth 2 squares tall), body leaning forward; 3 held screaming; 4 back toward the idle stance. The sound wave is an effect - do not draw it.` |
| `briar_ult.png` | 6 帧：60 70 70 90 100 110 | 第 3 帧（tick 8） | 3 列 × 2 行，2304×1536 | 第 81 行 | `CERTAIN DEATH, the kick, 6 frames: 1 she leans back; 2 she lifts her leg high; 3 the release (the gem leaves here): a big high kick forward to the right, as in the THIRD image; 4 follow-through, the leg coming down; 5 she crouches, ready to leap; 6 back toward the idle stance. The gem is an effect - do not draw a gem flying.` |
| `briar_ult_fly.png` | 4 × 100 | — | 4 列 × 1 行，3072×768 | 第 81 行 | `CERTAIN DEATH, the flight, 4 frames looping while she flies to her prey: flying forward to the right, body horizontal and low, head first, the pillory held back, the legs trailing behind as in the THIRD image; small differences between the 4 frames (the hair and the legs flutter).` |
| `briar_ult_land.png` | 5 帧：70 80 90 100 100 | 第 1 帧（tick 0） | 3 列 × 2 行，2304×1536，最后 1 格空 | 第 81 行 | `CERTAIN DEATH, the landing, 5 frames: 1 the impact (the blast happens here): she lands crouched low, knees bent, head down; 2 still crouched; 3-4 rising; 5 back toward the idle stance. The blast is an effect.` |
| `briar_hit.png` | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, eyes squeezed shut (two short dark lines on the eyes' rows); 2 recovering toward the idle stance.` |
| `briar_dead.png` | 8 帧：100 100 120 120 120 150 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames, going down in ONE movement (each frame lower than the one before), as in the THIRD image: 1 struck, head thrown back; 2 staggering; 3 falling to her knees; 4 slumping forward; 5 falling onto her side; 6-7 lying on the ground; 8 lying still on the ground line, the pillory on the ground beside her head. Frames 4-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、一样大、同一高度；
- [ ] `#F0FCFF`、`#C5E6F5` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 枷锁每帧都在，锁着手腕，不挡脸；
- [ ] 脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `briar_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛只在眼睛上、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`briar_cells.json` 用包里这份，`briar_idle.png` 用包里已做好的那张。
- `import_native.py --hero briar`：ORDER 待机一张图 + BOB 呼吸，EYES = `#F0FCFF`（按眼睛对齐待机和移动）。
- 按出手帧核对技能数据的时机（普攻 tick 7、冲头落地、尖啸 tick 4、踢宝石 tick 8、落地 tick 0），重量特效挂点和头像截取点，重跑模拟，做预览 GIF。
