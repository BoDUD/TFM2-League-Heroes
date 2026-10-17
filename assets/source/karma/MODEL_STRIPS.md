# 卡尔玛：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/karma_design.png`（放大 8 倍，1024×1024）：你交的生图原稿版本 2，按它自己的格子取回再整行整列删到 42 行（用户选的 2_42）。玉环顶到脚底 42 行，28 格宽，24 色；脚底在第 99 行，两脚中间在第 64 列。**造型图就是标准**：翡翠玉环、黑色短发、金额饰翠绿宝石、深棕皮肤、粉色流苏耳坠、象牙小骨翅、紫色高开衩长裙、白缠布、金边、粉裙摆、腿上翡翠灵纹、深色短靴，颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`karma_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - **跑步单独做，用「骨架 + 皮囊」**：英雄联盟模组包 oppi 里没有卡尔玛，`run_swap/` 里 图1 = oppi 的阿狸跑步（动作骨架，6 帧；**狐狸尾巴和耳朵不要画**），图2 = 定稿造型（皮囊），照 `run_swap/PROMPT.md` 的中文提示词画，交 `karma_run.png`，排版和图1一样。
> - 其余 7 张动作图按下面的表画：帧数、每帧时长、出手帧和站位照 `now/karma_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。**E 鼓舞是新加的一张**（`karma_skill_e.png`，5 帧）。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（大头 Q 版）；② 头（玉环 + 头发 + 脸）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**，**不画背影、不转头**；③ **腿**：in every standing frame (idle, attack, Q, W, E, R, hit) she stands on the design's OWN two dark boots and the bare near leg (with its jade tattoo squares) showing through the skirt's slit, square for square - the same place and width as the design, never spread, never longer; the arms, the skirt's hem, the hair and the floating ornaments move, the boots stay (a cast may move the WHOLE figure, boots included, 1-2 squares forward or back, never the upper body alone sliding over still boots, never the body sunk over the feet)；④ 饰物和衣服：the jade dragon ring floating above and behind her head (part of the head piece, see below), the two pairs of small ivory prongs beside her head and her waist (they float with her body, they may sway 1 square), the gold circlet with the green gem, the pink earring tassels, the violet high-slit skirt with its magenta-pink hem, the white wrap and the gold trims stay in every frame；⑤ 手臂：the arms are the design's bare brown arms with violet bracers, as thick as in the design (2-3 squares), the hands 2x2 squares of skin - never thinner, never 1-pixel sticks, never floating hands, never a black outline stroke instead of a forearm; an arm stretched forward is a whole arm from the shoulder to an open palm。
> - 出招方向：**手掌推出、指向、法术都朝图的右边**（游戏里朝左时会整张镜像）。
> - **死亡照英雄联盟**：玉环和骨翅掉落，人跪下再向左侧倒地（见表）。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/karma_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/karma_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/karma-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧手掌的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`karma_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/karma_palette.png`，或直接读 `design/karma_design_1x.png`）。
4. **贴头**：把造型图的头（`design/karma_head_1x.png` 里不透明的格子：翡翠玉环、黑短发、金额饰、脸、两只眼睛、耳坠；在 128×128 画布上的范围 x 53–73、y 58–75，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的头发、玉环碎块或描边。
5. 对位：每帧按 `karma_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/karma_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/karma_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/karma_head.png`、`_1x.png` | 要贴进每一帧的头（玉环、头发、额饰、脸、眼睛、耳坠） | 贴头 |
| `design/karma_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `karma_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `run_swap/` | 跑步的骨架（oppi 的阿狸跑步，已按我们的大小放大）、皮囊（定稿）和中文提示词 | **跑步照这里画** |
| `now/karma_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/karma_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `karma_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/karma_picture.png`、`refs/karma_draft_codex.png` | 用户选的原画 A 和你的造型生图原稿版本 2（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every standing frame (idle, attack, Q, W, E, R, hit) she stands on the design's OWN two dark boots and the bare near leg (with its jade tattoo squares) showing through the skirt's slit, square for square - the same place and width as the design, never spread, never longer; the arms, the skirt's hem, the hair and the floating ornaments move, the boots stay (a cast may move the WHOLE figure, boots included, 1-2 squares forward or back, never the upper body alone sliding over still boots, never the body sunk over the feet)。
- **饰物和衣服**：the jade dragon ring floating above and behind her head (part of the head piece, see below), the two pairs of small ivory prongs beside her head and her waist (they float with her body, they may sway 1 square), the gold circlet with the green gem, the pink earring tassels, the violet high-slit skirt with its magenta-pink hem, the white wrap and the gold trims stay in every frame。
- **手臂**：the arms are the design's bare brown arms with violet bracers, as thick as in the design (2-3 squares), the hands 2x2 squares of skin - never thinner, never 1-pixel sticks, never floating hands, never a black outline stroke instead of a forearm; an arm stretched forward is a whole arm from the shoulder to an open palm。
- **头每帧都是造型图的头**（玉环、头发、额饰、脸、眼睛、耳坠逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不转头**。**只画角色**：灵弹、火球、连线、护盾、真言光、掉落时的光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯青色 `#00FFFF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（普攻、Q、W、E、R、受击、死亡都用这一段，只替换中括号）

每张附三张图：第一张 `design/karma_design.png`，第二张 `now/karma_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `karma_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, ornaments and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the jade dragon ring floating above and behind her head, the black chin-length bob, the gold circlet with the green gem, the dark brown skin, the pink earring tassels, the small ivory prongs beside her head and waist, the violet high-slit skirt with the magenta-pink hem, the white wrap, the gold trims, the jade tattoo on the bare near leg, the dark boots, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms and the body from it, but keep the FIRST image's proportions (a big chibi head) and, in every standing frame, the FIRST image's own legs and boots; never draw her from the back, never turn her head away, never upside down.
The character: Karma, the Enlightened One (a graceful Ionian spirit mage with dark brown skin, a black bob, a gold circlet, a violet high-slit dress, a floating jade dragon ring and ivory spirit prongs).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (42 squares from the ring's top to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #030202 #150616 #220C25 #370644 #2C302A #452320 #222048 #42074B #780C4B #5F0970 #825238 #1BB663 #5C7D5F #E3118E #C7864A #C4815A #91CD9F #EEB956 #BAB0AD #ABDCB3 #CAE7C0 #DDDBC4 #F2E9C6 #F5EDE8. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every standing frame (idle, attack, Q, W, E, R, hit) she stands on the design's OWN two dark boots and the bare near leg (with its jade tattoo squares) showing through the skirt's slit, square for square - the same place and width as the design, never spread, never longer; the arms, the skirt's hem, the hair and the floating ornaments move, the boots stay (a cast may move the WHOLE figure, boots included, 1-2 squares forward or back, never the upper body alone sliding over still boots, never the body sunk over the feet).
Ornaments and clothes: the jade dragon ring floating above and behind her head (part of the head piece, see below), the two pairs of small ivory prongs beside her head and her waist (they float with her body, they may sway 1 square), the gold circlet with the green gem, the pink earring tassels, the violet high-slit skirt with its magenta-pink hem, the white wrap and the gold trims stay in every frame.
The arms: the arms are the design's bare brown arms with violet bracers, as thick as in the design (2-3 squares), the hands 2x2 squares of skin - never thinner, never 1-pixel sticks, never floating hands, never a black outline stroke instead of a forearm; an arm stretched forward is a whole arm from the shoulder to an open palm.
The head (the jade ring, the bob, the circlet with its gem, the face, both eyes, the earrings) is COPIED from the FIRST image in every frame, square for square, and only moved (tilted a little only while she falls in the death); never redraw, squash or tilt it otherwise, or it flickers when the frames play. Erase your own head before pasting it, so no extra hair, ring bits or outline is left beside it.
Feet line: in every cell her soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. Her place across the cell follows the SECOND image (each frame's standing point is in karma_cells.json).
3/4 front view like the FIRST image; every palm push, point and cast goes to the RIGHT of the image; never her back, never upside down. Do not draw effects (bolts, fireballs, the tether, shields, the mantra glow) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x80 squares (768x640 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FFFF cyan). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both arms whole with hands, both boots, the ring and the prongs in every frame (the death: as the table says), the arms as thick as in the FIRST image, the standing frames on the FIRST image's own legs and boots, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、身体的方向和姿势照图1，不转成背影、不转头；站着的动作腿和靴子用图2自己的。
3. 长相、配色、细节全部换成图2：翡翠玉环、黑色短发、金额饰翠绿宝石、深棕皮肤、粉色流苏耳坠、象牙小骨翅、紫色高开衩长裙、白缠布、金边、粉裙摆、腿上翡翠灵纹、深色短靴。头每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯青色 #00FFFF，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `karma_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1280 | 第 65 行 | **已做好，不用画** |
| `karma_run.png`（跑步（在 run_swap/ 换皮）） | 8 × 100 | — | 4 列 × 2 行，3072×1280 | 第 65 行 | **不用这一行：用 `run_swap/` 的换皮画** |
| `karma_attack.png`（普攻（掌心射出灵弹）） | 6 帧：60 60 70 70 70 70 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1280 | 第 65 行 | `BASIC ATTACK (a spirit bolt from her palm), 6 frames (League's attack): 1 she draws the far arm back and up beside her head, the palm open; 2 the arm high, the body turning a little toward the right; 3 the arm sweeping forward and down; 4 THE SHOT (the bolt leaves her palm here): the far arm stretched forward to the right at chest height, the palm open toward the enemy; 5 the follow-through, the arm lowering; 6 back toward the idle stance. The bolt is an effect - do not draw it.` |
| `karma_skill.png`（Q 心灵烈焰（前跨推掌）） | 6 帧：55 55 60 60 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1280 | 第 65 行 | `INNER FLAME (Q), 6 frames (League's Q cast, the picture's B pose): 1 she pulls both hands back to her hip, gathering; 2 leaning back, the near arm swept back, the skirt swinging; 3 stepping into a lunge toward the right; 4 THE CAST (the fireball leaves here): the far arm thrust straight forward to the right at shoulder height, the palm open and pushing, the near arm swept back, the skirt's hem flying back; 5 holding the push; 6 back toward the idle stance. Keep her in 3/4 front view in every frame (League turns her head away in frame 2 - do not). The fireball is an effect - do not draw it.` |
| `karma_skill2.png`（W 坚定专注（双手上举再指向前）） | 6 帧：55 55 60 60 70 70 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1280 | 第 65 行 | `FOCUSED RESOLVE (W, the tether), 6 frames (League's W cast): 1 both arms rising; 2 both hands raised high above her head, the palms together; 3 leaning forward, bringing the far hand down and forward; 4 THE CAST (the tether leaves here): the far arm pointing forward to the right at chest height, two fingers out, the near arm held back at the hip, a determined look; 5 holding the point; 6 back toward the idle stance. The tether beam is an effect - do not draw it.` |
| `karma_skill_e.png`（E 鼓舞（举手再向外一挥）） | 5 帧：50 50 55 60 55 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 65 行 | `INSPIRE (E, the shield on an ally or herself), 5 frames (League's E cast, short): 1 the far arm rising; 2 the far arm raised straight up above her head, the palm open; 3 THE CAST (the shield appears here): the far arm sweeping out to the right at shoulder height, the palm open, the near arm out to the left a little, the skirt swirling; 4 holding; 5 back toward the idle stance. The shield is an effect - do not draw it.` |
| `karma_ult.png`（R 真言（双手合十上举，裙摆飘起）） | 5 帧：50 50 60 70 70 | 第 3 帧（tick 6） | 3 列 × 2 行，2304×1280，最后 1 格空 | 第 65 行 | `MANTRA (R, she empowers her next spell), 5 frames (League's channel): 1 both hands coming together in front of her chest; 2 the palms pressed together raised in front of her face, the elbows out, the skirt flaring out behind her as if lifted by wind; 3 THE CAST (the mantra lights up here): both hands raised high over her head, the palms together, the jade ring right above them, the skirt fully flared; 4 holding; 5 back toward the idle stance. The glow is an effect - do not draw it.` |
| `karma_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×640 | 第 65 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body pushed back 1-2 squares (to the left), the head tilting back, the arms flung out a little; 2 recovering toward the idle stance. The design's boots.` |
| `karma_dead.png`（死亡（玉环和骨翅掉落，跪下再侧倒）） | 8 帧：100 100 100 120 150 150 200 500 | — | 4 列 × 2 行，3072×1280 | 第 65 行 | `DEATH, 8 frames (League's death: the ring and the prongs drop away, she sinks and falls): 1 struck, she jolts back; 2 the jade ring and the prongs drift off and fall behind her; 3-4 she sinks to her knees, the skirt pooling; 5-6 she falls over sideways to the LEFT, lying on her side along the feet line; 7-8 lying still (the same pose), the ring and the prongs lying on the ground behind her. Nothing below the feet line; the lying body is drawn lying, never rotated pixel art.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样（跑步和 `run_swap/1_动作骨架_oppi跑步.png` 一样），帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的头发、玉环碎块、描边；
- [ ] 每帧都有完整的两条手臂和手掌、两只靴子、玉环、骨翅（死亡按表）；手臂和造型图一样粗；站着的动作是造型图自己的腿和靴子；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有转头；出招都朝图的右边；
- [ ] 跑步：两条腿交替，头的横向位置每帧一样，首尾能接上，没有狐狸尾巴和耳朵；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `karma_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、靴子和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头。动作走样时用造型自己的部件无损重摆（rig_karma.py，见 rig_kogmaw.py / rig_rengar.py），不把身体沉到脚上。
- 放进 `assets/source/native/`，`karma_cells.json` 用包里这份（跑步用 `run_swap/run_layout.json`，6 × 133 毫秒），`karma_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边；E 是 `skill_e` 标签（技能树里用 CasterAnimation 播）。
- 按出手帧核对技能数据的时机（普攻 tick 11、Q tick 10、W tick 10、E tick 6、R tick 6），量头像截取点，重跑模拟，做预览 GIF。
