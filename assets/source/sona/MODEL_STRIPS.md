# 娑娜：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 定稿是你画的**版本 B**（大头，40 格）：`design/sona_design.png`（放大 8 倍，1024×1024；马尾顶到裙摆 40 格，34 格宽，23 色；裙摆最下一行在第 99 行、中间在第 64 列）。只改了一格：左马尾里那一格原来用了瞳孔的深青色，换成了马尾的深蓝青，让眼睛的颜色只出现在眼睛上。**造型图就是标准**：双马尾和金色发梢、两个金发饰、刘海、两只 2×3 的青色眼睛和一格玫红的嘴、金边高领、蓝色上衣、宽袖、平浮在腰前的金色叶琴（青色琴弦、木码、前端大卷翼、后端弯角、两条青色飘带）、带浅青裙片和金边的长裙、颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`sona_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/sona_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和琴的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **三处和参考图不一样，以造型图为准**：① 参考图是英雄联盟的比例（头小、裙子长、琴更长），我们**照造型图的比例**：大头、短一点的裙子、造型图里那么大的琴；② 头是贴上去的（见下），英雄联盟里她会低头、仰头、转头，我们**头每帧不变形、不旋转、始终正面**，双马尾跟着头一起平移（死亡跪坐时跟着身体往下沉）；③ **英雄联盟的跑步不迈步**（浮着滑行，脚藏在裙子里）：我们也不画腿和脚，裙摆始终落在脚底线上，只让裙子和飘带摆动、上半身轻轻浮沉 1 格。
> - 出招方向：造型是 3/4 正面朝右，**拨弦、张臂、音波都朝图的右边**（游戏里朝左时会整张镜像）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip（`sona_strips_pack_done.zip`，放在 outputs 里），HANDOFF.md 最后写。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/sona_palette.png`，或直接读 `design/sona_design_1x.png`）。**先把眼睛的三种颜色 #FFFFFF、#0C777A、#22C9B8 从色板里去掉**（吸附时会跑到头发、琴弦、裙片上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/sona_head_1x.png` 里不透明的格子：头发、双马尾、两个金发饰、脸、两只眼睛和嘴，到下巴的描边为止；在 128×128 画布上的范围 x 50–77、y 60–79，**按图里的形状贴，不是整个方框**——两边金边高领的尖不属于头）原样贴进每一帧头的位置（只平移）。这样每帧的脸都和造型图一模一样。头下面直接接高领和上衣，不要拉出脖子。
5. 对位：每帧按 `sona_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），裙摆落在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/sona_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线（裙摆）第 99 行 | 每张动作图的第一张附图 |
| `design/sona_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/sona_head.png`、`_1x.png` | 要贴进每一帧的头（头发、双马尾、发饰、脸，不含高领和身体） | 贴头 |
| `design/sona_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `sona_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/sona_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和琴的动作 |
| `guide/sona_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `sona_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/sona_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_gentle.png` | 团战经理2 原版英雄（含抱琴的吟游诗人、魔导师、牧师、白魔法师），放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿态时和造型图一样高（马尾顶到裙摆 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；明暗照定稿（金边的亮点、头发和裙片的浅青高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **手要像手**：袖子 2–3 格粗（加描边）、金色袖口，末端是 2×2 的皮肤色小手，不能是 1 格的黑细线或爪子；手连着手臂，手臂连着肩膀。
- **琴（叶琴）每帧都是造型图的琴**：同样的大小和形状（金色琴身、青色琴弦、木码、前端大卷翼、后端弯角、两条飘带），只整体平移、最多倾斜一格；不能变短、变细、断开或少一头的卷饰。
- **头每帧都是造型图的头**（头发、双马尾、发饰、脸逐格一样），只平移（死亡跪坐时跟着身体往下沉）；眼睛的三种颜色 #FFFFFF、#0C777A、#22C9B8 只用在眼睛上。
- 头、上衣、手臂、琴、裙子必须连成一个整体，不能有飘在空中的碎块（大招里飞到头顶的琴除外，它和手之间可以有空隙）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），飘带、琴、发梢都在它上面。只有死亡最后几帧可以低于红线，最多 1 格。
- **移动循环**：不画腿和脚，裙摆每帧落在脚底线上；头相对站位点的横向位置每帧不变；上半身上下浮沉最多 1 格；裙子和飘带摆动；首尾能无缝接上。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：音符、光环、护盾、治疗、加速、和弦的光、金色音波都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/sona_design.png`，第二张 `now/sona_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `sona_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, gown, instrument and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the same big head with the two cyan twin tails with golden tips, the two gold hair ornaments, the fringe, the two 2x3 teal eyes and the one rose-red mouth square; the tall gold-edged collar, the blue bodice, the wide blue sleeves with gold cuffs and small skin hands; the golden Etwahl (a floating zither with cyan strings, small brown bridges, a big gold wing-scroll at its front end and a curved gold horn at its back end, two cyan ribbons); the long blue skirt with light-cyan gold-edged panels and a gold hem; the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms and of the instrument from it, but keep the FIRST image's proportions (big head, shorter skirt, its instrument size); never draw her from the back or upside down.
The character: Sona (a gentle musician: two big cyan twin tails with golden tips, gold hair ornaments, a calm face; a royal-blue gown with a tall gold-edged collar and wide sleeves; a floating golden zither, the Etwahl, in front of her hips; a long flared skirt with light-cyan panels and gold trim that hides her feet).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (40 squares from the top of the twin tails to the hem in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #101020 #132350 #09567C #704526 #183F9E #0C777A #137DA7 #AD6C24 #225CD4 #D35669 #B87070 #22C9B8 #D99A35 #20ADE0 #338EF1 #E79F8D #55D9EF #FFD062 #6EF5FF #FFD4B1 #FFF1B0 #FFF0D3 #FFFFFF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its gold glints and light-cyan highlights move with the pose; no dithering, no noise, no random specks added. Sleeves 2-3 squares thick with the outline and a gold cuff, ending in a 2x2 skin hand joined to the arm - never 1-square black sticks or claws; no loose pieces.
The head (the hair, the twin tails, the two gold ornaments, the face with the eyes and the mouth, down to the chin's outline) is COPIED from the FIRST image in every frame, square for square, and only moved (in the death it sinks with the body); never redraw, squash, turn or tilt it, or it flickers when the frames play. Under the chin come the collar and the bodice - no neck. The eye colors #FFFFFF、#0C777A、#22C9B8 appear ONLY in the eyes.
The Etwahl is the FIRST image's instrument in every frame, the same size and shape, only moved and at most tipped by one square at an end; never shortened, thinned, broken or missing a finial; only in the ultimate does it fly up above her head (then it may stand apart from her hands).
Feet line: in every cell the hem's lowest row is on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a ribbon, a finial or a hair tip - because the game draws the health bar there (only the last frames of the death may dip 1 square). Her place across the cell follows the SECOND image (each frame's standing point is in sona_cells.json). In the move loop her head keeps the same horizontal place relative to the standing point in every frame; she has no visible legs or feet.
3/4 front view facing right like the FIRST image; every strum, spread of the arms and the chord goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (notes, auras, shields, heals, speed lines, the chord's glow, the golden wave) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, the eye colors only in the eyes, the Etwahl whole and as big as in the FIRST image in every frame, hands that read as hands, no loose pieces, the hem on the feet line and nothing below it, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `sona_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1536 | 第 79 行 | **已做好，不用画** |
| `sona_run.png`（移动（不迈步，浮着滑行）） | 8 × 160 | — | 4 列 × 2 行，3584×1536 | 第 79 行 | `MOVE, 8 frames, one seamless loop (8 x 160 ms): she GLIDES forward to the right - she takes no steps, her feet stay hidden under the long skirt: the skirt and its light-cyan panels sway and stream a little back to the left from frame to frame, the hem's lowest row always on the feet line; the whole upper figure (head, body, arms, instrument) floats down and up once over the loop by 1 square - frames 1-2 and 8 at the top, 4-6 one square lower - the skirt's top shortening and lengthening with it while the hem stays on the line; the Etwahl floats level in front of her hips, both hands resting on its strings; its two ribbons stream back to the left and wave; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `sona_attack.png`（普攻（拨弦）） | 6 帧：60 60 70 80 90 100 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536 | 第 79 行 | `BASIC ATTACK, 6 frames (League's attack1, a strum that sends a note): 1 both hands on the strings; 2 the hand at image right lifts off the strings, drawing back a little; 3 THE STRUM (the note leaves here): that hand sweeps across the strings and flicks out to the right; 4 the arm at image right stretched out to the right after the flick, the palm open; 5 the hand coming back to the strings; 6 back to the idle stance. The Etwahl stays level; the note is an effect - do not draw it.` |
| `sona_attack_p.png`（能量和弦（强化普攻）） | 6 帧：60 60 70 80 90 100 | 第 4 帧（tick 11） | 3 列 × 2 行，2688×1536 | 第 79 行 | `POWER CHORD (the empowered attack), 6 frames (League's crit): 1 both hands lift a little above the strings; 2 the hand at image right rises high above the instrument, the Etwahl's front end tilting up one square; 3 the wind-up at its highest, the arm raised above her shoulder; 4 THE CHORD (the hit lands here): the hand swept down hard across the strings, the Etwahl's front end tipping down one square; 5 the arm thrown out to the right, the hand open; 6 back to the idle stance. The chord's glow is an effect - do not draw it.` |
| `sona_skill.png`（Q 英勇赞美诗（双臂张开）） | 6 帧：60 60 70 80 90 100 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536 | 第 79 行 | `HYMN OF VALOR (two notes fly out to the two nearest enemies), 6 frames (League's spell1): 1 both hands on the strings; 2 both hands lift off the strings, the arms opening; 3 THE HYMN (the notes leave here): both arms spread wide to the sides at shoulder height, palms open, the Etwahl floating level in front of her hips; 4 the arms still wide, a little higher; 5 the arms coming back down toward the strings; 6 back to the idle stance. The notes and the blue aura are effects - do not draw them.` |
| `sona_skill2.png`（W 坚毅咏叹调（并入 E）） | 6 帧：60 70 70 80 90 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2688×1536 | 第 79 行 | `ARIA OF PERSEVERANCE (a heal and a shield for her and the allies near her, with Song of Celerity), 6 frames (League's spell2): 1 both hands on the strings; 2 the hand at image right lifts toward her face; 3 THE ARIA (the heal and the shields go out here): that hand raised beside her cheek, palm out, the other hand strumming at the instrument's middle, the Etwahl tilting its front end up one square; 4 the same pose, the instrument settling level; 5 the raised hand coming down; 6 back to the idle stance. The green and purple auras are effects - do not draw them.` |
| `sona_ult.png`（R 狂舞终乐章（琴飞到头顶）） | 8 帧：60 70 70 80 90 100 100 100 | 第 3 帧（tick 8） | 4 列 × 2 行，3584×1536 | 第 79 行 | `CRESCENDO (she strikes a chord that stuns the enemies in front of her), 8 frames (League's spell4): 1 she gathers, both hands on the strings, leaning back a little; 2 she throws the Etwahl up: it rises in front of her chest, her arms flung up after it; 3 THE CRESCENDO (the wave leaves here): the Etwahl floats high above her head, level, her arms spread wide and up, her body leaning back a little; 4 and 5 the Etwahl hovers above her head, she holds the pose, the ribbons hanging from it; 6 the Etwahl comes down in front of her chest, her hands reaching for it; 7 the Etwahl back at her hips, her hands on the strings; 8 back to the idle stance. The Etwahl is the FIRST image's instrument in every frame, the same size, only moved (by whole squares); above her head it may reach up to the top of the cell. The golden wave is an effect - do not draw it.` |
| `sona_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1792×768 | 第 79 行 | `HIT, 2 frames: 1 jolted back by a blow: her body and head pushed back 1-2 squares (to the left), the Etwahl tipping, the skirt swinging; 2 recovering toward the idle stance.` |
| `sona_dead.png`（死亡（抱琴跪坐）） | 8 帧：100 100 120 120 150 150 200 400 | — | 4 列 × 2 行，3584×1536 | 第 79 行 | `DEATH, 8 frames (League's death: she hugs the instrument and sinks to her knees): 1 struck, she sways back, the Etwahl tipping; 2 she pulls the Etwahl up against her chest, standing it on its end in her arms; 3 holding it like that she bows forward a little; 4 she starts to sink, the skirt spreading at the hem; 5 lower: kneeling, the skirt a wide pool on the ground, the Etwahl still in her arms; 6 lower still, the head sinking with the body; 7 she sits on the ground, the skirt spread flat, the Etwahl leaning on her; 8 she lies folded on the spread skirt, the Etwahl lying across her, nothing standing. Every frame on the feet line; the last frames may reach 1 square below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡时跟着下沉），两只眼睛都在、同一高度；
- [ ] 眼睛的三种颜色只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 琴每帧都完整、和造型图一样大（大招飞到头顶时也是）；手是 2×2 的小手、连着袖子；没有飘着的碎块（大招的琴除外）；
- [ ] 裙摆每帧在脚底线上，脚底线以下没有任何像素（只有死亡最后几帧可以低 1 格）；没有画腿和脚；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 移动循环：头的横向位置每帧一样，上半身浮沉不超过 1 格，裙子和飘带在摆，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `sona_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛上、连通块、手和袖子、琴的大小、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头；头周围 3 格以内不能有 Codex 自己画的头发碎块。
- 放进 `assets/source/native/`，`sona_cells.json` 用包里这份，`sona_idle.png` 用包里已做好的那张。
- `import_native.py --hero sona`：ORDER 待机一张图 + BOB 呼吸（上半身往下一格，裙子下半截不动），EYES = `#22C9B8`（按眼睛对齐待机和移动），COMPLETE 补描边，头是贴的：NECK 检查高领每帧在下巴两边同一行。
- 按出手帧核对技能数据的时机（普攻 tick 7、能量和弦 tick 11、Q tick 7、W tick 8、R 音波 tick 8），量特效挂点（琴弦、手的高度）和头像截取点，重跑模拟，做预览 GIF。
