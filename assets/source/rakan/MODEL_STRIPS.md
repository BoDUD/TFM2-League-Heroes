# 洛：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/rakan_design.png`（放大 8 倍，1024×1024；羽冠顶到脚底 40 行，32 格宽，22 色；脚底在第 99 行，两脚中间在第 64 列）。**造型图就是标准**：红色羽冠、白发、红耳尖的长耳朵、脸、红领金边、裸上身、手里的金羽毛、金护腕、鸟头骨腰带、深色灯笼裤、红绑带、紫灰鸟爪脚、**拖在身后的羽毛披风**（红色金边的肩部，金橙色的长羽毛，羽毛尖是紫、蓝、青、绿的彩虹色），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`rakan_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/rakan_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、腿、身体和披风的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **和参考图不一样、以造型图为准的地方**：① 参考图是英雄联盟的比例，我们**照造型图的比例**（大头、40 行高）；② 头是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**；③ **he always faces the viewer in the design's 3/4 FRONT view: where League's animation spins him round (the attack, Q, W's spiral, the death), he turns on the spot with his face still toward the viewer and the cloak swirling round him - never his back, never upside down**。
> - **披风（最重要的标志）**：the FEATHER CLOAK is in every frame, the design's own colours: deep red with gold trims at the shoulders, then a long fan of separate pointed feathers - gold, yellow and orange, the tips purple, blue, cyan and green; in the idle, the run, the attack and Q it trails behind him toward image left, in W, E and R it spreads wide behind him like a pair of wings (as in the THIRD image), in the death it lies on the ground; never cut short, never a different colour。
> - **腿**：his legs are the design's legs (dark leg wraps with red bands, purple-grey taloned bird feet, the same thickness): in the hit they stand as in the idle; in the moves where League crouches, leaps or flies (the attack, Q, W, E, R, the death) they bend, lift and stretch as in the THIRD image, hips connected to the body, both legs the same colours。
> - **离地的动作**：W 的俯冲（`skill2`）、W 落地后旋上空中（`w_spin` 第 3–5 帧，离地 8–10 格）、E 的飞行（`e_dash`）照参考图离地；其余动作脚踩在脚底线上。
> - 出招方向：**甩羽毛、冲刺、飞行都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧手的位置）和 `generation_prompts.json`，最好打成一个 zip（`rakan_strips_pack_done.zip`，放在 outputs 里），文件放在 `outputs/rakan-strips/`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**不要把细节比方块还小的高清图压缩下来**（上一轮造型就是这样被删坏了脸和披风）。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/rakan_palette.png`，或直接读 `design/rakan_design_1x.png`）。
4. **贴头**：把造型图的头（`design/rakan_head_1x.png` 里不透明的格子：红羽冠、白发、耳朵、脸到下巴；在 128×128 画布上的范围 x 51–70、y 60–75，**按图里的形状贴，不是整个方框**——领子和手里的羽毛不属于头）原样贴进每一帧头的位置（只平移；死亡倒下时整个头跟着身体转）。这样每帧的脸都和造型图一模一样。头下面直接接红领子，不要拉出一截脖子。
5. 对位：每帧按 `rakan_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），踩地的帧脚底落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/rakan_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/rakan_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/rakan_head.png`、`_1x.png` | 要贴进每一帧的头（红羽冠、白发、耳朵、脸到下巴） | 贴头 |
| `design/rakan_palette.png` | 造型图的全部 22 色（暗到亮） | 色板 |
| `rakan_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/rakan_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、腿、身体和披风的动作 |
| `guide/rakan_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `rakan_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/rakan_picture.png`、`refs/rakan_draft_codex.png` | 造型来源的原画和你画的原稿（长相参考；比例和大小以定稿造型为准） | 需要时参考 |
| `style/pack_heroes_8x.png` | 我们包里用户通过的烬、凯隐、娑娜、塔里克、迦娜，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（羽冠顶到脚底 40 行），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 22 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边（`#160A0E`），描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **手和手臂**：裸露的手臂 2–3 格粗、金护腕、实心的手；**不要 1 像素的黑细棍、不要飘着的手**；近侧手平时捏着金羽毛。
- **披风**：the FEATHER CLOAK is in every frame, the design's own colours: deep red with gold trims at the shoulders, then a long fan of separate pointed feathers - gold, yellow and orange, the tips purple, blue, cyan and green; in the idle, the run, the attack and Q it trails behind him toward image left, in W, E and R it spreads wide behind him like a pair of wings (as in the THIRD image), in the death it lies on the ground; never cut short, never a different colour。
- **脸的朝向**：he always faces the viewer in the design's 3/4 FRONT view: where League's animation spins him round (the attack, Q, W's spiral, the death), he turns on the spot with his face still toward the viewer and the cloak swirling round him - never his back, never upside down。
- **腿**：his legs are the design's legs (dark leg wraps with red bands, purple-grey taloned bird feet, the same thickness): in the hit they stand as in the idle; in the moves where League crouches, leaps or flies (the attack, Q, W, E, R, the death) they bend, lift and stretch as in the THIRD image, hips connected to the body, both legs the same colours。
- **头每帧都是造型图的头**（红羽冠、白发、耳朵、脸逐格一样），只平移（死亡倒下时整个转）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：踩地的帧最低一行是脚底线（参考线图的红线就在它下面），披风的羽毛尖也在它上面。
- **移动和大招循环**：每帧头相对站位点的横向位置不变；两条腿交叉迈步（前 4 帧一条腿在前，后 4 帧另一条），两条腿颜色一样；上下起伏最多 1 格；首尾能无缝接上。
- 出招朝图的右边，**不画背影、不画倒立**。**只画角色**：飞出去的羽毛、拖尾、光、爱心、地面的冲击、旋风都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯蓝 `#0000FF`，**不要洋红也不要纯绿**，会吃掉紫色和绿色的羽毛尖）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/rakan_design.png`，第二张 `now/rakan_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `rakan_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, costume, feather cloak and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same red feather crest, white hair, long pointed red-tipped ear and face, the red collar with gold trim, the bare chest, the golden feather in the near hand, the gold bracers, the belt with two little bird skulls, the dark baggy trousers, the dark leg wraps with red bands, the purple-grey taloned bird feet, the feather cloak, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the throw, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the legs, the body and the cloak from it, but keep the FIRST image's proportions (a big head, a slim body, the cloak's size).
The character: Rakan (a slim, flamboyant young bird-man and dancer: white hair with a red feather crest, long pointed ears with red tips, a bare chest under a high red collar with gold trim, gold bracers, dark baggy trousers, bird-like legs with purple-grey taloned feet, and a long feather cloak of gold and orange feathers with rainbow tips).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the crest's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 22 colors of the FIRST image, no new colors: #160A0E #1E302B #3B2F38 #8E0E14 #8A3A10 #3E6346 #C92214 #5C4A6A #B0663F #8E3CB0 #F0503A #F08A18 #86749A #4FE0A8 #E39A62 #FCC24F #6FD3E8 #C9BFAE #D9CBA8 #F6C79A #FFE9A0 #F2ECDF. ONE outline: a 1-square near-black outline (#160A0E) around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added. Arms are bare skin 2-3 squares wide with the gold bracers and solid hands at their ends - never 1-pixel black sticks or floating hands.
The cloak is his signature: the FEATHER CLOAK is in every frame, the design's own colours: deep red with gold trims at the shoulders, then a long fan of separate pointed feathers - gold, yellow and orange, the tips purple, blue, cyan and green; in the idle, the run, the attack and Q it trails behind him toward image left, in W, E and R it spreads wide behind him like a pair of wings (as in the THIRD image), in the death it lies on the ground; never cut short, never a different colour.
The view: he always faces the viewer in the design's 3/4 FRONT view: where League's animation spins him round (the attack, Q, W's spiral, the death), he turns on the spot with his face still toward the viewer and the cloak swirling round him - never his back, never upside down.
The legs: his legs are the design's legs (dark leg wraps with red bands, purple-grey taloned bird feet, the same thickness): in the hit they stand as in the idle; in the moves where League crouches, leaps or flies (the attack, Q, W, E, R, the death) they bend, lift and stretch as in the THIRD image, hips connected to the body, both legs the same colours.
The head (the red crest, the white hair, the ear and the face down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it turns down with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. It sits on the red collar - no neck.
Feet line: in every cell where he stands his lowest square is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a feather tip - because the game draws the health bar there. Airborne frames (the W dive, the W spiral, the E flight) are off the ground as in the SECOND image. His place across the cell follows the SECOND image (each frame's standing point is in rakan_cells.json). In the move and R loops his head keeps the same horizontal place relative to the standing point in every frame and the legs cross in turn.
Every throw, dash and flight goes to the RIGHT of the image. Do not draw effects (the thrown feather, trails, glows, sparkles, hearts, ground bursts, whirlwinds) - only the character. Every animation starts and ends near the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x88 squares (896x704 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #0000FF blue, never magenta or green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the face toward the viewer in every frame (never his back), the feather cloak in every frame in the design's colours, the hands solid, no loose pieces, no stray black squares, nothing below the feet line in the grounded frames, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `rakan_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1408 | 第 75 行 | **已做好，不用画** |
| `rakan_run.png`（移动（舞者的步子）） | 8 × 100 | — | 4 列 × 2 行，3584×1408 | 第 75 行 | `MOVE, 8 frames, one seamless loop (8 x 100 ms, League's own run at his base speed: a light, swaggering dancer's stride): his near hand still holds the golden feather in front of his chest, the far arm swings lightly; the feather cloak trails behind him and sways with the step; in frames 1-4 one foot comes forward, in frames 5-8 the other, the knees passing in frames 3 and 7 (the legs CROSS - never the same stance in all frames), both legs the same colours; the body bobs 1 square down and up over each half; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `rakan_attack.png`（普攻（转身甩出羽毛）） | 6 帧：100 100 90 90 100 120 | 第 3 帧（tick 12） | 3 列 × 2 行，2688×1408 | 第 75 行 | `BASIC ATTACK (a dancer's flick that throws a feather), 6 frames: 1 he gathers, the near hand with the feather drawn back, the cloak pulled in; 2 he twirls - the cloak swirls round him in a wide arc (a turn on the spot, his face still toward the viewer); 3 THE THROW (the feather leaves his hand here): crouched low, the near arm flung forward to the right, the cloak swept out behind him like an open fan; 4 holding the crouch, the cloak settling; 5 rising; 6 back toward the idle stance. The thrown feather and its trail are effects - do not draw them.` |
| `rakan_skill.png`（Q 微光飞翎（甩出大羽毛）） | 6 帧：55 55 57 60 60 60 | 第 4 帧（tick 10） | 3 列 × 2 行，2688×1408 | 第 75 行 | `GLEAMING QUILL (Q: a flourish that flings a big magic feather), 6 frames: 1 a quick low lunge forward, the cloak trailing low behind; 2 rising; 3 a half twirl, the cloak gathered round him (face toward the viewer); 4 THE THROW (the feather leaves here): the near arm thrown up and forward to the right, the cloak flung open behind him like raised wings; 5 holding the flourish, the cloak spread; 6 settling toward the idle stance. The feather and its glow are effects.` |
| `rakan_skill2.png`（W 盛大登场：俯冲） | 4 帧：60 60 60 300 | — | 4 列 × 1 行，3584×704 | 第 75 行 | `GRAND ENTRANCE - THE DASH (W: he dives at the enemy), 4 frames: 1 the launch: a crouch springing forward; 2-4 he flies forward low and fast, his body almost horizontal, his head forward to the right, the arms swept back, the feather cloak spread out behind him like a pair of wings; frame 4 is held while he flies (frames 3 and 4 nearly the same).` |
| `rakan_w_spin.png`（W 盛大登场：落地旋上空中（击飞）） | 6 帧：67 67 67 67 67 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2688×1408 | 第 75 行 | `GRAND ENTRANCE - THE SPIRAL (W: he lands and spins up into the air, knocking the enemies up), 6 frames: 1 he lands in a low crouch, the cloak wrapped round him; 2 he springs up; 3 THE SPIRAL (the enemies fly up here): spinning in the air about 8-10 squares above the ground, the cloak whirling round him in a spiral, his face toward the viewer; 4 the top of the spin; 5 coming down; 6 landing in a crouch, the cloak settling. The whirl of feathers and the ground burst are effects.` |
| `rakan_e_dash.png`（E 轻舞成双：飞向队友） | 3 帧：60 60 300 | — | 3 列 × 1 行，2688×704 | 第 75 行 | `BATTLE DANCE - THE FLIGHT (E: he flies to an ally), 3 frames: 1 the take-off: he leaps forward, the cloak opening; 2-3 he glides forward through the air, the body nearly horizontal, the head to the right, the cloak spread like wings (frame 3 is held while he flies).` |
| `rakan_e_land.png`（E 轻舞成双：落到队友身边） | 3 帧：80 80 120 | — | 3 列 × 1 行，2688×704 | 第 75 行 | `BATTLE DANCE - THE LANDING (E: beside the ally), 3 frames: 1 he touches down, one knee bent, the cloak swirling; 2 a little twirl; 3 a graceful pose: upright, one arm out with the golden feather, the cloak sweeping on the ground behind him.` |
| `rakan_ult.png`（R 惊鸿过隙（疾跑，披风张开）） | 8 × 107 | — | 4 列 × 2 行，3584×1408 | 第 75 行 | `THE QUICKNESS (R: he dances through the enemy team), 8 frames, one seamless loop (8 x 107 ms, League's R run): a fast, light sprint leaning forward, the feather cloak spread WIDE behind him like a pair of wings (its whole length streaming back), the arms back; in frames 1-4 one foot comes forward, in frames 5-8 the other, the legs crossing; the head keeps the same place across the cell; frame 8 flows into frame 1. The golden glow and the hearts are effects.` |
| `rakan_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1792×704 | 第 75 行 | `HIT, 2 frames: 1 jolted back by a blow: his head and body pushed back 1-2 squares (to the left), the cloak swaying; 2 recovering toward the idle stance.` |
| `rakan_dead.png`（死亡） | 8 帧：100 100 100 120 120 140 160 400 | — | 4 列 × 2 行，3584×1408 | 第 75 行 | `DEATH, 8 frames (League's death): 1 struck, he staggers; 2 he sways back, the golden feather slipping from his hand; 3 he sinks, the cloak folding round him; 4 on his knees; 5-6 he slumps sideways; 7-8 lying on his side on the feet line, the cloak spread on the ground (the same pose in 7 and 8); the head stays visible from the 3/4 front (turned down with the body, never upside down). Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡倒下时整个转），两只眼睛都在；
- [ ] **每帧都是 3/4 正面**，没有背影、没有倒立；转身的动作只让披风绕着他转；
- [ ] **披风每帧都在**，颜色和造型图一样（红色金边的肩部、金橙色羽毛、彩虹色羽毛尖）；
- [ ] 手是实心的、连着手臂；两条腿颜色一样，胯部连着身体；
- [ ] 踩地的帧脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 移动和大招循环：头的横向位置每帧一样，两条腿交叉迈步，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点、bbox 和出手帧手的位置都写了；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `rakan_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、零散黑格、每帧面积和待机比、披风颜色），不在网格上的重新取样；头不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`rakan_cells.json` 用包里这份，`rakan_idle.png` 用包里已做好的那张。
- `import_native.py --hero rakan`：ORDER 待机一张图 + BOB 呼吸（缝选在绑腿的直段），COMPLETE + CLEAN 补描边、清黑边，NECK 检查头每帧在红领子上同一行。
- 按出手帧核对技能数据的时机（普攻 tick 12、Q tick 10、W 击飞 tick 8（落地后）），量手的位置定羽毛的出手点，量头像截取点，重跑模拟，做预览 GIF。
