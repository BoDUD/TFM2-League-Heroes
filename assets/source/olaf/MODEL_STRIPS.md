# 奥拉夫：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/olaf_design.png`（放大 8 倍，1024×1024）：高的那只角尖到脚底 42 行，39 格宽，21 色；脚底在第 99 行，两脚中间在第 64 列。这张是在你第二轮生图稿（`refs/olaf_draft_codex.png`）的基础上逐格读回、删到 42 行、再精修过的，**造型图就是标准**：蓝灰角盔（两只弯角、涡纹、帽檐、护鼻）、两只眼睛、张开的嘴、亮橙鬃发和编辫大胡子、光膀子粗胳膊、肩上白毛、前臂皮护腕、深棕皮背心、钢铆钉腰带、白灰毛皮围腰和棕皮片、带尖刺的浅钢护胫、棕靴、两手各一把蓝钢斧。颜色、明暗每一帧都照它，只改姿势。
> - **待机条已经做好**（`olaf_idle.png`），不用画（游戏里的待机呼吸由我们的工具自动生成）；它也告诉你造型图在格子里多大、站在哪里。
> - 其余 8 张动作图（包括跑步）按下面的表画：帧数、每帧时长、出手帧和站位照 `now/olaf_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **跑步**：照英雄联盟的跑姿（弓身前冲、两手握斧摆动），两条腿一定要前后交替、膝盖交叉，两条腿颜色一样（以前好几个英雄跑步是平行走路、或者一条腿变了颜色，被退回过）。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头大、手脚短，英雄联盟的手脚更长，不要照）；② 头（两只角 + 角盔 + 脸 + 头顶的橙发）是贴上去的（见下），**头每帧不变形、始终是造型图的 3/4 正面**，**不画背影**；③ **腿**：in every STANDING frame (attack, Q, R, hit) he stands on the design's OWN legs square for square: the bare tanned thighs, the spiky pale steel-and-fur greaves and the heavy brown boots, the same wide stance and width as the design, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the LEAPING, CROUCHING and FALLING frames (Reckless Swing, death) the legs follow League's pose (a hop, bent low, lying) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body；④ 装备：the white fur on both shoulders, the orange mane falling over his left shoulder, the huge braided orange beard hanging from the face onto the chest, the dark brown vest, the steel belt with its studs and buckle, and the white-grey fur loincloth with its brown flap stay in every frame and move with the body；⑤ 手臂：each arm is the design's bare, thick, tanned muscular arm with its brown leather wrist wrap and a big fist; each fist holds one AXE (a brown wooden handle 1 square wide, a big blue-steel blade with a lit edge and a dark rune square, as big as in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; both axes never lost (only in Undertow, after the release, the throwing hand is empty)。
> - 出招方向：**劈、扔斧、砸都朝图的右边**（游戏里朝左时会整张镜像）。
> - **死亡照英雄联盟**：被打得后仰、踉跄，最后仰面倒地躺平（见表），**不画倒立**。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/olaf_now_<动作>.png`（骨架：帧数、每格位置、大小、姿势），图2 = `design/olaf_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行，也不要用脚本拼装身体部件**（以前用脚本拼的木板手臂、火柴腿都被退回了；奥拉夫的造型第一轮用脚本摆色块也被退回了）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/olaf-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧那只手的位置）和所有生图原稿（`raw/`），最好打成一个 zip（`olaf_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/olaf_palette.png`，或直接读 `design/olaf_design_1x.png`）。眼睛的蓝（#0455A6、#022460）和嘴的红、粉、牙白（#B30729、#CA4A60、#F4E6E8）**只用在脸上**。
4. **贴头**：把造型图的头（`design/olaf_head_1x.png` 里不透明的格子：两只角、角盔、脸、头顶的橙发；在 128×128 画布上的范围 x 57–79、y 58–75，**按图里的形状贴，不是整个方框**）原样贴进每一帧头的位置（只平移；死亡躺下的几帧整块转 90°）。贴之前先擦掉你自己画的头，不要在头旁边留下多余的角、头盔或描边。**头下面要接上胡子和肩膀**，胡子从嘴下面垂下来，不要留出空隙或长出一截脖子；披在左肩上的鬃发跟着身体走。
5. 对位：每帧按 `olaf_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/olaf_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/olaf_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/olaf_head.png`、`_1x.png` | 要贴进每一帧的头（两只角、角盔、脸、头顶橙发） | 贴头 |
| `design/olaf_palette.png` | 造型图的全部 21 色（暗到亮） | 色板 |
| `olaf_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/olaf_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂和身体的动作 |
| `guide/olaf_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `olaf_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/olaf_picture.png`、`refs/olaf_draft_codex.png`、`refs/olaf_picture_B_q.png` | 用户选的原画 A、你第二轮的生图稿、原画 B（Q 举斧蓄力，画 Q 第 2–3 帧时参考）（长相参考；比例、大小和脸以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样高，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 21 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，**不要再画一圈黑、不要零散的黑格**。
- **腿**：in every STANDING frame (attack, Q, R, hit) he stands on the design's OWN legs square for square: the bare tanned thighs, the spiky pale steel-and-fur greaves and the heavy brown boots, the same wide stance and width as the design, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the LEAPING, CROUCHING and FALLING frames (Reckless Swing, death) the legs follow League's pose (a hop, bent low, lying) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body。
- **装备**：the white fur on both shoulders, the orange mane falling over his left shoulder, the huge braided orange beard hanging from the face onto the chest, the dark brown vest, the steel belt with its studs and buckle, and the white-grey fur loincloth with its brown flap stay in every frame and move with the body。
- **手臂**：each arm is the design's bare, thick, tanned muscular arm with its brown leather wrist wrap and a big fist; each fist holds one AXE (a brown wooden handle 1 square wide, a big blue-steel blade with a lit edge and a dark rune square, as big as in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; both axes never lost (only in Undertow, after the release, the throwing hand is empty)。
- **头每帧都是造型图的头**（两只角、角盔、眼睛、嘴逐格一样），只平移（死亡躺下时整块转 90°）。
- **脚底线以下什么都不能有**（游戏在脚下画血条）。
- 3/4 正面朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立**。**只画角色**：斧光、飞出去的斧头、红色怒气、砸地的冲击都是单独的特效，不要画。（Q 扔斧那几帧：斧头离手后那只手就空了，飞出去的斧头是特效，不要画在空中。）
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（8 张都用这一段，只替换中括号）

每张附三张图：第一张 `design/olaf_design.png`，第二张 `now/olaf_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `olaf_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, gear, blades and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same 3/4 front view facing right, the round blue-grey steel helmet with its two curved horns, swirl and lit brim, the eyes, the nose guard and the open shouting mouth, the bright orange mane and the huge braided orange beard, the bare tanned muscular arms with brown leather wrist wraps, the white fur on both shoulders, the dark brown vest, the steel belt with studs, the white-grey fur loincloth with its brown flap, the spiky pale steel greaves, the brown boots, a blue-steel axe in each hand, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the arms, the axes and the body from it, but keep the FIRST image's proportions (big head, short limbs - not the long limbs of the 3D model) and, in every standing frame, the FIRST image's own legs; never draw him from the back or upside down.
The character: Olaf, the Berserker (a huge viking with a horned helmet, a braided orange beard and an axe in each hand).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (42 squares from the high horn's tip to the soles in the idle stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 21 colors of the FIRST image, no new colors: #2A1208 #022460 #4A2A1E #2E3448 #B30729 #74442C #A83410 #0455A6 #A4542E #4E5E7E #E94101 #A06A44 #CA4A60 #FC8302 #D47C48 #8494B2 #FCB870 #BCC4D8 #F4E6E8 #ECEAF0 #FFFFFF. The eye blues and the mouth reds, pink and tooth white only on the face. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring, never stray black squares. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Legs: in every STANDING frame (attack, Q, R, hit) he stands on the design's OWN legs square for square: the bare tanned thighs, the spiky pale steel-and-fur greaves and the heavy brown boots, the same wide stance and width as the design, never longer (a cast may move the WHOLE figure, legs included, 1-2 squares forward or back, never the upper body alone sliding over still legs). In the LEAPING, CROUCHING and FALLING frames (Reckless Swing, death) the legs follow League's pose (a hop, bent low, lying) but stay the design's legs: the same materials, colours and thickness, both legs the same colours, the hips joined to the body.
Gear: the white fur on both shoulders, the orange mane falling over his left shoulder, the huge braided orange beard hanging from the face onto the chest, the dark brown vest, the steel belt with its studs and buckle, and the white-grey fur loincloth with its brown flap stay in every frame and move with the body.
The arms: each arm is the design's bare, thick, tanned muscular arm with its brown leather wrist wrap and a big fist; each fist holds one AXE (a brown wooden handle 1 square wide, a big blue-steel blade with a lit edge and a dark rune square, as big as in the design); both arms as thick as in the design - never thinner, never 1-pixel sticks, never floating hands; both axes never lost (only in Undertow, after the release, the throwing hand is empty).
The head (both horns, the helmet, the face and the orange hair crest over it) is COPIED from the FIRST image in every frame, square for square, and only moved (turned a quarter only while he lies dead); never redraw, squash or tilt it otherwise, or it flickers when the frames play. Erase your own head before pasting it, so no extra horn, helmet or outline is left beside it; the beard hangs from under the mouth onto the chest - no gap and no neck.
Feet line: in every cell his soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there. His place across the cell follows the SECOND image (each frame's standing point is in olaf_cells.json).
3/4 front view like the FIRST image; every swing, throw and slam points to the RIGHT of the image; never his back, never upside down. Do not draw effects (swing trails, the flying axe, the red rage glow, the ground impact) - only the character; once the thrown axe leaves his hand in Undertow, that hand is empty. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both axes (one hand empty only after the Undertow throw), both legs and boots in every frame, the shoulder fur, the beard and the loincloth, the arms as thick as in the FIRST image, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：手臂、斧头、身体的方向和姿势照图1，不转成背影；站着的动作腿用图2自己的腿（光大腿、尖刺护胫、棕靴），跨步、蹲下、跃起的动作腿照图1弯，但还是图2的腿。
3. 长相、配色、细节全部换成图2：蓝灰角盔（两只弯角、涡纹、帽檐、护鼻）、两只眼睛、张开的嘴、亮橙鬃发、编辫大胡子、光膀子、肩上白毛、皮护腕、深棕皮背心、钢铆钉腰带、白灰毛皮围腰、尖刺护胫、棕靴、两手各一把蓝钢斧。头（角 + 角盔 + 脸）每帧照图2逐格贴，只平移。
4. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的「动作骨架」，只是换了「皮囊」。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `olaf_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2688×1536 | 第 81 行 | **已做好，不用画** |
| `olaf_run.png`（跑步（弓身前冲，两手握斧摆动）） | 8 × 120 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `RUN (League's run: a heavy forward charge, leaning forward, an axe in each fist swinging with the stride), 8 frames: copy the SECOND image's legs frame by frame - the two legs stepping in turn, one forward and one back, the knees crossing, the lifted foot off the ground and the other foot on the feet line; the body leaning forward and bobbing 1 square; the arms swinging opposite to the legs, the axes held low; the beard and mane swinging. Both legs in the design's colours.` |
| `olaf_attack.png`（普攻（举斧过头下劈）） | 6 帧：60 70 70 80 60 60 | 第 4 帧（tick 12） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BASIC ATTACK (League's: a big overhead axe chop), 6 frames: 1 the near arm (image right) starts to rise; 2 the near axe raised high above and behind his head, the body leaning back; 3 starting down, the body turning forward; 4 THE CHOP (the hit lands here): the near axe swung down and forward to the right at waist height, the body leaning forward, the far axe back by his hip; 5 the follow-through, the axe low in front; 6 back toward the idle stance. The swing trail is an effect - do not draw it.` |
| `olaf_skill.png`（Q 逆流投掷（举斧过头掷出，手里空了）） | 6 帧：60 70 70 80 60 60 | 第 4 帧（tick 12） | 3 列 × 2 行，2688×1536 | 第 81 行 | `UNDERTOW (Q; League's Q: he hurls one axe overhand), 6 frames: 1 turning, the near arm (image right) drawing back; 2 the near axe raised high behind his head, the body leaning back, the far axe held across his chest; 3 winding, the arm cocked behind the head; 4 THE THROW (the axe leaves here): the near arm whipped forward and down to the right, the hand open and EMPTY, the body bent forward; 5 bent low forward, the empty hand low in front; 6 back toward the idle stance, the near hand still empty. The flying axe is an effect - do not draw it.` |
| `olaf_skill2.png`（E 鲁莽挥击（跃起双斧下砸）） | 6 帧：50 60 57 70 70 60 | 第 4 帧（tick 10） | 3 列 × 2 行，2688×1536 | 第 81 行 | `RECKLESS SWING (E; League's E: a leaping two-handed overhead slam), 6 frames: 1 a quick crouch, both axes low; 2 springing up (the whole figure at most 3 squares higher), both axes swung up; 3 at the top, both axes high above his head; 4 THE SLAM (the hit lands here): landed, bent low and forward, both axes driven down in front of him to the right near the ground; 5 crouched low after the blow; 6 rising back toward the idle stance. The impact flash is an effect - do not draw it.` |
| `olaf_ult.png`（R 诸神黄昏（双斧高举怒吼）） | 6 帧：60 60 70 80 90 100 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536 | 第 81 行 | `RAGNAROK (R; League's R: he roars with both axes raised), 6 frames: 1 the arms drawing in; 2 both axes lifted, crossing in front of his chest; 3 THE ROAR (the rage starts here): standing tall, chest out, BOTH axes raised high above his head, the mouth wide open; 4-5 holding the roar, the axes shaking 1 square; 6 lowering back toward the idle stance. The red rage glow is an effect - do not draw it.` |
| `olaf_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1792×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body pushed back 1-2 squares (to the left), the design's head moved back a little (not turned), the arms flung out with the axes; 2 recovering toward the idle stance. The design's legs.` |
| `olaf_dead.png`（死亡（后仰踉跄，仰面倒地）） | 8 帧：100 100 120 150 150 150 150 500 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `DEATH, 8 frames (League's death: struck, he staggers back with the axes raised, then falls on his back): 1 struck, he jolts back; 2-3 staggering back, the arms and axes thrown up; 4-5 tipping backward, the knees bending; 6 falling onto his back; 7 lying on his back on the ground, stretched out, the axes beside him; 8 the same as 7. The head turned a quarter (lying) in 6-8. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；眼睛和嘴的颜色只在脸上；
- [ ] 待机姿态时和造型图一样高；头就是造型图的头（逐格一样，只平移），头旁边没有多余的角、头盔、描边，胡子和头之间没有空隙；
- [ ] 每帧都有两把斧（Q 扔出后那只手是空的）、肩上白毛、胡子、围腰、两条腿和靴子；手臂和造型图一样粗；站着的动作是造型图自己的腿；
- [ ] 脚底线以下没有任何像素；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 跑步：两条腿前后交替、膝盖交叉、颜色一样，头的横向位置每帧一样，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `olaf_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、腿和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头不对的帧换回造型图的头；不合格的动作用 rig 从造型图无损重摆（照 tools/art/rig_zed.py）。
- 放进 `assets/source/native/`，`olaf_cells.json` 用包里这份，`olaf_idle.png` 用包里已做好的那张。
- `import_native.py`：ORDER 待机一张图，COMPLETE 补描边。
- 按出手帧核对技能数据的时机（普攻 tick 12、Q tick 12、E tick 10、R tick 7），量头像截取点，重跑模拟，做预览 GIF。
