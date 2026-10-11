# 诺提勒斯：动作帧重画——侧身版（第 2 步第二轮，给 Codex 的提示词）

> **这一轮为什么重画**：上一轮的提示词要求「放技能时的身体就是待机的身体、头盔贴上去」，结果每个动作都是正面站着（`refs/rejected_first_delivery.png`、`refs/rejected_front_on.png`）；把造型图的头盔贴到英雄联盟的身体上又把身体全盖住了、锚每帧变形（`refs/rejected_pasted_helmet.png`）。用户：「我现在完成的所有英雄都是侧面吧 除了待机姿势」「武器变形了吧？头大的把身体全盖住了？」「学隔壁oppi怎么弄的吧」。
> **这一轮的标准：像 oppi 的《League of Legends Reborn》那样一帧一帧手绘**（`refs/style_oppi_*.png`：Galio 待机正面、跑步和出招转成侧身；Sion 的斧子每个角度都是同一把斧子；Alistar、Vi 的跑步是清楚的交叉步）。**除待机外每个动作都是侧身朝右**（和本包其他英雄一样：`refs/style_pack_heroes.png`），身体转向右边——英雄联盟的动作本来就是这样转的（`refs/lol_turned_body.png`、`pose/`）。

> **造型已定，不许再改。** 用户选定的是 `design/nautilus_design.png`（放大 8 倍，1024×1024；48 行高、39 格宽，23 色；脚底在第 99 行，站位点在第 64 列）——从你上一轮第二次的生图原稿 `A_simple` 按格子取回、整行整列按比例删到头盔顶到脚底 37 行（锚再高出 11 行）（用户：「用这个吧 感觉这个最还原」；头盔缩小的重画 1b 没有采用：「还是用 p35」）。**造型图就是标准**：圆铜潜水头盔（锈红铜管兜帽、顶上三个通气孔、黑色观察窗里两只红橙眼睛、方形铜护颌）、锈铜胸甲肩甲 + 海绿发光缝线、深灰黑潜水服、大灰手套、铜护膝、厚底潜水靴、近侧手握的粗铁链、背在背上的灰色大锚（红箍、棕绳、两只弯钩锚爪），颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`nautilus_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/nautilus_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、锚和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **动作帧是侧身**：身体朝右转（头盔的观察窗转到头盔右侧、远侧那只眼睛变窄，近侧肩甲在前、远侧肩甲一半在头盔后面），两腿一前一后侧着站或跑（不是待机那种正面八字站）；头盔大小、颜色、细节和造型图一样，只是转过去看；同一个动作里每帧的头盔、身体、腿、手臂、锚的大小和形状都一致（不能忽大忽小、不能变形），整个人可以前倾后仰、前冲、下蹲、跳起。
> - **和参考图不一样、以造型图为准的地方**：① 我们照造型图的比例（头盔大、身体短）；② **头盔跟着身体转向右边，不贴正面头盔**，也不能把身体全盖住（胸甲、肩甲、腰带、手臂、腿都要看得见）；**不画背影**；③ **腿**：SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the other (not the idle's wide front stance), each leg the design's own leg - the dark grey-black suit, the bronze knee guard on the front of the knee, the huge diving boot with its thick bronze sole pointing to the image right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward；④ **手臂和锚**：the arms are the design's arms - thick dark grey-black suit arms with bronze bracers and big grey gloves - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder plate; the ANCHOR is ONE rigid object with exactly the design's shape and size (the grey stone-iron shank with its red band and brown rope, the ring, the wide crown and the two hooked flukes): only moved and turned whole, drawn clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; the iron chain runs from his near hand to the anchor's ring; the hand holding it is never hidden behind the body；⑤ the helmet keeps the design's size and details (the rusty-red pipe hood, the three vent holes, the black viewing slit with the two red-orange eyes, the square jaw guard) but TURNS WITH THE BODY: seen from the front-right, the viewing slit moved toward the helmet's right side, the far eye narrower, the hood and the vent holes following; the SAME turned helmet in every frame of an action, never pasted front-on and never covering the whole body - under and beside it the bronze chest and shoulder plates with their sea-green seams, the belt, the arms and the legs stay visible as on League's model (pose/), the near shoulder plate in front, the far one partly behind the helmet；⑥ 锚和铁链**永远不低于脚底线**（英雄联盟里锚扫过地面、砸进地里，我们只画到地面为止）；⑦ **Q 抛出去以后的帧里没有锚**（锚是飞出去的特效），被拉过去落地时锚才回到手里。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/nautilus_now_<动作>.png`（骨架），图2 = `design/nautilus_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。**整条画糊了就一帧一帧单独生成**（每帧一张图，最后拼回格子）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/nautilus-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及出手帧握锚的手和锚冠的位置）和所有生图原稿（`raw/`，不要重采样），最好打成一个 zip（`nautilus_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/nautilus_palette.png`，或直接读 `design/nautilus_design_1x.png`）。
4. **不要贴头盔**（上一轮的做法，已经作废）。原来是：把造型图的头盔（`design/nautilus_head_1x.png` 里不透明的格子：铜管兜帽、带三个通气孔的圆顶、黑色观察窗和两只红眼、方形护颌到它下面的海绿缝线；不含左边的锚杆和上面的锚爪；在 128×128 画布上的范围 x 56–74、y 63–86，**按图里的形状贴，不是整个方框**）原样贴进每一帧头盔的位置（只平移；死亡低头的几帧也只平移）。贴之前先擦掉你自己画的头盔，不要在头盔旁边留下多余的描边。
5. 对位：每帧按 `nautilus_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/nautilus_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/nautilus_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头盔 |
| `design/nautilus_head.png`、`_1x.png` | 要贴进每一帧的头盔（兜帽、圆顶、通气孔、观察窗、红眼、护颌） | 贴头盔 |
| `design/nautilus_palette.png` | 造型图的全部 23 色（暗到亮） | 色板 |
| `nautilus_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/nautilus_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、锚和身体的动作 |
| `guide/nautilus_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `nautilus_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/nautilus_picture.png`、`refs/nautilus_draft_codex.png` | 用户选的原画 A 和你上一轮第二次的生图原稿 A_simple（长相参考；比例和大小以定稿造型为准） | 需要时参考 |

## 规则（每张都一样）

- **和造型图一样的像素**：待机姿态时和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 23 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the other (not the idle's wide front stance), each leg the design's own leg - the dark grey-black suit, the bronze knee guard on the front of the knee, the huge diving boot with its thick bronze sole pointing to the image right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward。
- **手臂和锚**：the arms are the design's arms - thick dark grey-black suit arms with bronze bracers and big grey gloves - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder plate; the ANCHOR is ONE rigid object with exactly the design's shape and size (the grey stone-iron shank with its red band and brown rope, the ring, the wide crown and the two hooked flukes): only moved and turned whole, drawn clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; the iron chain runs from his near hand to the anchor's ring; the hand holding it is never hidden behind the body。
- **身上**：the helmet keeps the design's size and details (the rusty-red pipe hood, the three vent holes, the black viewing slit with the two red-orange eyes, the square jaw guard) but TURNS WITH THE BODY: seen from the front-right, the viewing slit moved toward the helmet's right side, the far eye narrower, the hood and the vent holes following; the SAME turned helmet in every frame of an action, never pasted front-on and never covering the whole body - under and beside it the bronze chest and shoulder plates with their sea-green seams, the belt, the arms and the legs stay visible as on League's model (pose/), the near shoulder plate in front, the far one partly behind the helmet。
- **头盔每帧都是造型图的头盔**（兜帽、通气孔、观察窗、红眼、护颌逐格一样），只平移。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），锚和铁链也不能低于这条线。
- **跑步循环**：锚一直背在背上；每帧头盔相对站位点的横向位置不变；两腿真正交叉（每半个周期两只靴子交换前后）；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 侧前方朝右（和造型图一样），出招朝图的右边，**不画背影、不画倒立、不趴在地上**。**只画角色本身**：护盾、水花、漩涡、冲击波、飞出去的锚都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/nautilus_design.png`，第二张 `now/nautilus_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `nautilus_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, helmet, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose, drawn by hand like oppi's sprites, but SIDE-ON: the body turned to face the image right (the helmet's viewing slit on the helmet's right side, the near shoulder plate in front, the far one partly behind the helmet, the legs one in front of the other) - only the idle faces the camera. The same the same round bronze diving helmet with its rusty-red pipe hood, three vent holes, black viewing slit with two red-orange eyes and square jaw guard, the rusted bronze chest and shoulder plates with glowing sea-green seams, the dark grey-black suit, the big grey gloves, the bronze knee guards, the huge diving boots, the thick iron chain in his near hand and the grey stone-iron anchor on his back (red band, brown rope, two hooked flukes), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the anchor and the body from it, the body turned the way the THIRD image turns it, with the FIRST image's proportions, colours and details; every cast goes to the RIGHT of the image; never draw him from the back, upside down or lying flat on the ground.
The character: Nautilus, the Titan of the Depths (a heavy giant in an ancient rusted bronze diving suit with a huge stone anchor).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 23 colors of the FIRST image, no new colors: #070211 #0B021A #28160F #351215 #093742 #552113 #2D3041 #03455C #6F2610 #3D4150 #8C3815 #A84217 #E4221F #F94102 #E55222 #70747A #DC741C #00E9BE #01F3C5 #FAAC2A #FDCC31 #B2B0A8 #F6E4C8. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Consistency: within an animation the helmet, the body, the legs, the arms and the anchor keep the same size and shape in every frame (the turned helmet is the same turned helmet in every frame); the whole figure may lean, lunge, crouch or hop.
Legs: SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the other (not the idle's wide front stance), each leg the design's own leg - the dark grey-black suit, the bronze knee guard on the front of the knee, the huge diving boot with its thick bronze sole pointing to the image right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward.
The arms and the anchor: the arms are the design's arms - thick dark grey-black suit arms with bronze bracers and big grey gloves - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder plate; the ANCHOR is ONE rigid object with exactly the design's shape and size (the grey stone-iron shank with its red band and brown rope, the ring, the wide crown and the two hooked flukes): only moved and turned whole, drawn clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; the iron chain runs from his near hand to the anchor's ring; the hand holding it is never hidden behind the body.
The body parts: the helmet keeps the design's size and details (the rusty-red pipe hood, the three vent holes, the black viewing slit with the two red-orange eyes, the square jaw guard) but TURNS WITH THE BODY: seen from the front-right, the viewing slit moved toward the helmet's right side, the far eye narrower, the hood and the vent holes following; the SAME turned helmet in every frame of an action, never pasted front-on and never covering the whole body - under and beside it the bronze chest and shoulder plates with their sea-green seams, the belt, the arms and the legs stay visible as on League's model (pose/), the near shoulder plate in front, the far one partly behind the helmet.
The helmet keeps the FIRST image's size, colours and details, turned to the right with the body; do not paste the FIRST image's front-on helmet and do not let the helmet cover the whole body.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there - the anchor and the chain too. His place across the cell follows the SECOND image (each frame's standing point is in nautilus_cells.json). In the run his helmet keeps the same horizontal place relative to the standing point in every frame.
Side-on facing the image right (only the idle faces the camera); every cast goes to the RIGHT of the image; never his back, never upside down. Do not draw effects (shields, water, splashes, whirlpools, shockwaves, a flying anchor, glows, sparks) - only the character. Every animation starts and ends near the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x128 squares (1024x1024 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, every frame side-on with the turned helmet, both arms growing from the outer shoulder corners in every frame, the hand holding the anchor never behind the body, the anchor rigid, full size with both flukes, no anchor after Q's throw until he lands, the body visible under the helmet, the legs the same thickness in every frame, the run's boots swapping front and back, no loose pieces, no stray black squares, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：身体侧过来朝右（只有待机是正面），手臂、锚和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不趴在地上）；头盔、身体和腿的颜色、细节、大小用图2的，头盔跟着身体转过去，不能把身体全盖住。
3. 长相、配色、细节全部换成图2：圆铜潜水头盔（铜管兜帽、三个通气孔、黑色观察窗和两只红橙眼睛、方形护颌）、锈铜胸甲肩甲和海绿缝线、深灰黑潜水服、大灰手套、铜护膝、厚底潜水靴、粗铁链、灰色大锚（红箍、棕绳、两只弯钩锚爪）。
4. 手臂从肩甲外侧长出来，握锚的手任何一帧都不能藏在身体后面，锚始终是一整块、大小不变；锚和铁链不能低于脚底线；Q 抛出去以后到落地前的帧里没有锚。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `nautilus_idle.png`（待机） | 8 × 160 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | **已做好，不用画** |
| `nautilus_run.png`（跑步（交叉步，锚背在背上）） | 8 × 116 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | `RUN, 8 frames, one seamless loop (League's run, 0.93 s): the anchor stays ON HIS BACK exactly as in the design (League keeps it there too), the near hand with the chain and the far fist swinging a little; the legs CROSS: in frames 1 and 5 the boots are furthest apart (frame 1 the near leg in front, frame 5 the far leg in front), in frames 3 and 7 the lifted boot passes BESIDE the other 1-2 rows up; the body bobs 1 row with each landing; his helmet keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `nautilus_attack.png`（普攻（抡锚横扫）） | 6 帧：70 80 60 90 80 80 | 第 4 帧（tick 13） | 3 列 × 2 行，3072×2048 | 第 99 行 | `BASIC ATTACK (a sweep of the anchor), 6 frames: 1 the design's stance, the near hand taking the anchor off his back; 2 the anchor swung down and back behind him, low, held by the shank, the body coiled; 3 the anchor swinging forward along the ground (its flukes just ABOVE the feet line); 4 THE SWEEP (the blow lands here): lunging forward, front knee bent, the anchor swung out level to the image right at knee height, held by the shank at arm's length; 5 the anchor coming back up in front of him; 6 back toward the design's stance, the anchor going onto his back.` |
| `nautilus_skill.png`（Q 疏通航道（抛锚）） | 6 帧：60 60 60 60 80 140 | 第 5 帧（tick 14） | 3 列 × 2 行，3072×2048 | 第 99 行 | `DREDGE LINE (Q, the anchor thrown), 6 frames: 1 the anchor lifted off his back; 2 the anchor swung up over his head, held by the shank; 3 the anchor drawn back behind his head, the body leaning back; 4 swinging it forward over his head, the body leaning forward; 5 THE THROW (the anchor leaves his hand here): the near arm flung out forward to the image right, the hand open, the chain running from the hand out of the cell to the right - NO anchor in this frame (it flies as an effect); 6 holding the throw: braced, leaning back a little, both hands on the taut chain in front of him (no anchor).` |
| `nautilus_skill_pull.png`（Q 疏通航道（锚钩中后被拉过去）） | 4 帧：100 120 100 80 | — | 4 列 × 1 行，4096×1024 | 第 99 行 | `DREDGE LINE, PULLED IN (after the anchor hooks), 4 frames: 1 pulled forward along the chain: the whole body leaning far forward to the image right, both hands on the chain in front of him, the boots trailing (no anchor); 2 the same, lower, the boots just above the feet line (no anchor); 3 landing, the anchor back in his near hand, held low in front of him; 4 the design's stance, the anchor on his back.` |
| `nautilus_skill2.png`（W 泰坦之怒 + E 暗流涌动（护盾、捶地）） | 6 帧：70 70 100 90 90 90 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×2048 | 第 99 行 | `TITAN'S WRATH + RIPTIDE (W then E: a shield, then a slam), 6 frames: 1 the design's stance, the fists clenched (the shield is an effect, do not draw it); 2 the far fist raised high; 3 THE SLAM (the riptide bursts here): crouching, the far fist punched DOWN onto the ground in front of him (the fist on the feet line), the anchor still on his back; 4 rising, the fist coming up; 5 standing braced, fists clenched; 6 back to the design's stance.` |
| `nautilus_ult.png`（R 深海冲击（把锚砸进地里）） | 8 帧：60 70 60 70 100 110 90 90 | 第 5 帧（tick 16） | 4 列 × 2 行，4096×2048 | 第 99 行 | `DEPTH CHARGE (R, the anchor slammed into the ground), 8 frames: 1 the near hand taking the anchor off his back; 2 the anchor raised high over his head, held by the shank in both hands; 3 the anchor drawn back behind him, the body arched back; 4 swinging it over his head, the body leaning forward; 5 THE SLAM (the shockwave leaves here): crouched low, the anchor driven straight DOWN into the ground in front of him to the image right (its crown and flukes ON the feet line - the part in the ground is not drawn); 6 holding the slam, the anchor upright in the ground; 7 pulling the anchor up; 8 back toward the design's stance, the anchor going onto his back.` |
| `nautilus_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×1024 | 第 99 行 | `HIT, 2 frames: 1 jolted back by a blow: his whole body and helmet pushed back 1-2 squares (to the left); 2 recovering toward the design's stance. The design's legs.` |
| `nautilus_dead.png`（死亡（靠着锚倒下）） | 8 帧：100 100 120 150 200 150 200 400 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 the anchor slipping off his back and thudding upright onto the ground beside him (image left), the chain still in his hand; 3 staggering, slumping forward; 4-6 sinking down to sit against the anchor, the helmet bowed, the red eyes dimmed; 7-8 the same, still, lying back against the anchor. Nothing below the feet line.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 除待机外每帧都是侧身朝右；头盔和造型图一样大、细节一样，跟着身体转向右边；身体（胸甲、肩甲、腰带、手臂、腿）看得见，没有被头盔全盖住；同一个动作里各部件大小形状不变；
- [ ] 两只手臂都在、和造型图一样粗、不比造型图的手臂长，从肩甲长出来；握锚的手没有藏在身体后面，锚是一整块、没有变小变形，两只锚爪完整；
- [ ] 跑步锚一直背在背上，侧身交叉步（像 `refs/style_oppi_alistar.png`、`refs/style_oppi_vi.png`：每半个周期两只靴子交换前后、抬起的腿屈膝），腿每帧一样粗、没有碎块、没有缺格子；
- [ ] Q 抛出那一帧起到被拉过去落地前没有锚；
- [ ] 脚底线以下没有任何像素（锚、铁链也不行）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立、没有趴在地上；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `nautilus_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；头盔不对的帧换回造型图的头盔；身体不是待机身体的帧用造型图的部件重摆（rigkit：锚和握锚的手整块只平移和 90° 整转，整个人前倾、前冲、下蹲；不按任意角度转）。
- 放进 `assets/source/native/`，`nautilus_cells.json` 用包里这份，待机由 `import_native.py` 的 idle_breathe 从造型图生成。
- `import_native.py`：ORDER 待机，COMPLETE 补描边；红色方：有前后之分、贴在他身上的特效烘进动作帧（`nautilus_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick 13、Q 抛出 tick 14、W+E 捶地 tick 8、R 砸地 tick 16；skill_pull 由锚钩中时的 CasterAnimation 播放），量头像截取点，重跑模拟，做预览 GIF。

## 这一轮新增的参考图（`refs/`）

| 文件 | 内容 |
|---|---|
| `style_oppi_galio.png`、`style_oppi_sion.png`、`style_oppi_alistar.png`、`style_oppi_vi.png` | oppi 的手绘精灵（待机、跑步、普攻）：**要学的标准**——待机正面，跑步和出招侧身；每帧都是同一个人、同样大小；武器每个角度都是同一把武器 |
| `style_pack_heroes.png` | 本包已经做好的英雄（每行：待机、跑步 4 帧、普攻 1 帧）：动作都是侧身 |
| `lol_turned_body.png` | 英雄联盟里诺提勒斯的待机（正面）和跑步、普攻、W+E、R（身体都转向右边） |
| `lol_run_legs.png` | 英雄联盟跑步 8 帧的腿（交叉步、屈膝抬腿） |
| `rejected_first_delivery.png` | 上一轮交付（全是正面站着，锚变形）：**不要这样** |
| `rejected_front_on.png` | 用定稿零件摆出来的跑步（正面八字腿）：**不要这样** |
| `rejected_pasted_helmet.png` | 把正面头盔贴到英雄联盟身体上（身体被盖住、锚每帧变形）：**不要这样** |
