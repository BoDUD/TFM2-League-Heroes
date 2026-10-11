# 艾瑞莉娅：按定稿造型画动作帧——侧身版（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户定稿的是 `design/irelia_design.png`（放大 8 倍，1024×1024；22 格宽、42 行高，20 色；脚底在第 99 行，站位点在第 64 列）——从你画的格子原稿 `refs/irelia_draft_codex.png`（take B）逐格描下来的（用户：「可以了下一步吧」）。**造型图就是标准**：宝蓝色长发垂到膝盖、银色 V 形头冠、深色斜眉和青色凤眼、**不画嘴**；银白胸甲中间红心、领口青色宝石，带白边的深红前摆，银白卷钩肩甲，白臂环、红护臂、白腕环，深藏青打底裤，银色四角星护膝，红靴（白脚踝环、白鞋尖、灰鞋跟）；背后收着一束弯月形飞刃（深红刃身、白色刃口、刃与刃之间黑描边，左下那把刃根有青色宝石）。颜色、明暗，每一帧都照它，只改姿势。
> **除待机外每个动作都是侧身朝右**——像 oppi 的《League of Legends Reborn》那样一帧一帧手绘（`refs/style_oppi_*.png`：Galio 待机正面，跑步和出招转成侧身；Sion 的斧子每个角度都是同一把斧子；Alistar、Vi 的跑步是清楚的交叉步），和本包其他英雄一样（`refs/style_pack_heroes.png`）；英雄联盟的动作本来就是这样转的（`refs/lol_turned_body.png`、`pose/`）。上一个英雄（诺提勒斯）第一轮画成了正面站着，全部作废；**这一轮一开始就画侧身**。
> - **待机条已经做好**（`irelia_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/irelia_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；手臂、飞刃和身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；它是镜像的）；长相照造型图。**出招一律朝图的右边**。
> - **动作帧是侧身**：身体朝右转（脸朝右、远侧眼睛变窄，近侧肩甲在前、远侧肩甲一半在身后），两腿一前一后侧着站或跑（不是待机那种正面站）；头、身体、腿、手臂、飞刃的大小颜色和造型图一样，只是转过去看；同一个动作里每帧大小形状一致（不能忽大忽小、不能变形）；整个人可以前倾后仰、前冲、下蹲、跳起。
> - **和参考图不一样、以造型图为准的地方**：① 照造型图的比例；② **她没有手持武器：飞刃是一组漂浮的刀刃，从不握在手里**（没有刀柄、不贴在手上，离手至少一格，她用张开的手掌或手指指挥它们）；**英雄联盟里的飞刃一直飘在她身边，我们的飞刃平时收拢悬在背后**（造型图那样），只有表里写的时候才离开背后：普攻飞出一把、Q 两把、W 三把挡在身前再斩出；E 和 R 掷出去的刃是特效，**不画**；③ **不画嘴**；④ **不画背影、不倒立**；⑤ **腿**：SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the other (not the idle's front stance), each leg the design's own leg - dark navy leggings, the silver four-pointed star knee guard on the front of the knee, the crimson boot with its white ankle band, white toe cap and grey heel pointing to the image right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward；⑥ **手臂和飞刃**：the arms are the design's arms - bare upper arm, white arm band, crimson arm guard, white wrist band, the hand with finger tips - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder guard; she NEVER holds a blade - no grip, no hilt, no blade in her hand: the blades FLOAT free (at least one square clear of her hands) and she directs them with open hands, palm out or fingers pointing; the BLADES are the design's crescent blades (a crimson body, a white edge, a black outline between neighbours, the cyan gem at the root of the lower one): each blade ONE rigid object of exactly the design's shape and size, only moved and turned whole, drawn clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; when they are not sent out they hover folded behind her back exactly as in the design；⑦ **身上**：the head keeps the design's size, colours and details (the royal-blue hair dome with its sheen, the silver tiara with its V point, the slanted dark brows over the cyan eyes, NO mouth) but TURNS WITH THE BODY: seen from the front-right, the face toward the image right, the far eye narrower, the long hair falling behind her; the SAME turned head in every frame of an action, never pasted front-on; the silver breastplate with its red heart and cyan collar gem, the crimson tabard with its white edge, the silver-white shoulder guards (the near one in front, the far one partly behind her) stay on her in every frame；⑧ 脚底线以下什么都不能有，飞刃也不行。
> - **你的生图工具画不准游戏尺寸时，用「骨架 + 皮囊」的办法**：图1 = `now/irelia_now_<动作>.png`（骨架），图2 = `design/irelia_design.png`（皮囊），下面有那段简短中文提示词；生成后按格子取回（每格取多数颜色，不要取中心点），**不要用脚本缩小或删行**。**整条画糊了就一帧一帧单独生成**（每帧一张图，最后拼回格子）。上一轮你的生图原稿画成了每格约 15 px（是要求的一半大），按 1 倍取回全是碎点——这一轮**生成后先量格子大小**，不是 8 px 一格（在 1024 的格子里）就重画。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。交付到 `outputs/irelia-strips/`：附 `HANDOFF.md`（**最后写**；每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和所有生图原稿（`raw/`，不要重采样），最好打成一个 zip（`irelia_strips_pack_done.zip`）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose），或者用骨架 + 皮囊的短提示词。
2. 对齐网格：找出方块边界，**每格取多数颜色**，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/irelia_palette.png`，或直接读 `design/irelia_design_1x.png`）。
4. 对位：每帧按 `irelia_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底落在脚底线上；检查线以下没有像素；再放大 8 倍输出。
5. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/irelia_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/irelia_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板 |
| `design/irelia_head.png` | 造型图的头（发顶、头冠、脸、两侧头发），8 倍 | 看头的大小和细节（转到侧面画，不要贴） |
| `design/irelia_palette.png` | 造型图的全部 20 色（暗到亮） | 色板 |
| `irelia_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/irelia_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图（或骨架图）：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：手臂、飞刃和身体的动作 |
| `guide/irelia_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `irelia_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/irelia_draft_codex.png` | 你上一轮画的格子原稿 take B（造型就是从它描的） | 长相参考（大小以定稿为准） |
| `refs/style_oppi_*.png`、`refs/style_pack_heroes.png` | oppi 的手绘精灵、本包已经做好的英雄：**要学的标准**——待机正面，跑步和出招侧身，每帧同一个人、同样大小，武器每个角度都是同一把 | 风格 |
| `refs/lol_turned_body.png` | 英雄联盟里艾瑞莉娅的待机（正面）和各动作（身体转向右边） | 侧身的样子 |

## 规则（每张都一样）

- **和造型图一样的像素**：和造型图一样大，每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 20 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边。
- **腿**：SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the other (not the idle's front stance), each leg the design's own leg - dark navy leggings, the silver four-pointed star knee guard on the front of the knee, the crimson boot with its white ankle band, white toe cap and grey heel pointing to the image right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward。
- **手臂和飞刃**：the arms are the design's arms - bare upper arm, white arm band, crimson arm guard, white wrist band, the hand with finger tips - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder guard; she NEVER holds a blade - no grip, no hilt, no blade in her hand: the blades FLOAT free (at least one square clear of her hands) and she directs them with open hands, palm out or fingers pointing; the BLADES are the design's crescent blades (a crimson body, a white edge, a black outline between neighbours, the cyan gem at the root of the lower one): each blade ONE rigid object of exactly the design's shape and size, only moved and turned whole, drawn clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; when they are not sent out they hover folded behind her back exactly as in the design。
- **身上**：the head keeps the design's size, colours and details (the royal-blue hair dome with its sheen, the silver tiara with its V point, the slanted dark brows over the cyan eyes, NO mouth) but TURNS WITH THE BODY: seen from the front-right, the face toward the image right, the far eye narrower, the long hair falling behind her; the SAME turned head in every frame of an action, never pasted front-on; the silver breastplate with its red heart and cyan collar gem, the crimson tabard with its white edge, the silver-white shoulder guards (the near one in front, the far one partly behind her) stay on her in every frame。
- **脚底线以下什么都不能有**（游戏在这条线下画血条），飞刃也不能低于这条线。
- **跑步循环**：飞刃一直收在背上；每帧头相对站位点的横向位置不变；两腿真正交叉（每半个周期两只靴子交换前后）；上下起伏最多 1 格；首尾能无缝接上。
- 出招朝图的右边，**不画背影、不画倒立、不画嘴**。**只画角色本身**：飞出去的刃（E、R）、刀光、冲击、发光都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/irelia_design.png`，第二张 `now/irelia_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `irelia_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, blades, body and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose, drawn by hand like oppi's sprites, but SIDE-ON: the body turned to face the image right (the face toward the right, the far eye narrower, the near shoulder guard in front, the far one partly behind her, the legs one in front of the other) - only the idle faces the camera. The same royal-blue hair falling to her knees, silver tiara with a V point, slanted dark brows over cyan eyes and NO mouth, the silver breastplate with its red heart and cyan collar gem, the crimson tabard with a white edge, the silver-white hooked shoulder guards, white arm bands, crimson arm guards, white wrist bands, dark navy leggings, silver star knee guards, crimson boots with white ankle bands and toe caps, and the bundle of crescent blades folded behind her back (crimson bodies, white edges, black outlines between them, a cyan gem on the lower one), the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing, the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places (mirrored) - copy the motion of the arms, the blades and the body from it, the body turned the way the THIRD image turns it, with the FIRST image's proportions, colours and details; the blades stay folded on her back unless the animation below sends them out; every cast goes to the RIGHT of the image; never draw her from the back or upside down.
The character: Irelia, the Blade Dancer (a calm, resolute Ionian warrior woman who commands floating crescent blades).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 20 colors of the FIRST image, no new colors: #0B021E #0F1456 #151C7C #A00331 #1A22A0 #D10338 #162DE0 #FB093F #1E4AF6 #008EE9 #00B8E9 #9399B8 #1FE3FD #FEA475 #A9AEC8 #FEB78B #8ED7F1 #C7CBDE #FED4B2 #F4F4F8. A 1-square near-black outline around the silhouette. Copy the FIRST image's shading; no dithering, no noise, no random specks added.
Consistency: within an animation the head, the body, the legs, the arms and every blade keep the same size and shape in every frame; the whole figure may lean, lunge, crouch or hop.
Legs: SIDE-ON legs like the pack's other heroes and oppi's sprites: under the turned body, one leg in front of the other (not the idle's front stance), each leg the design's own leg - dark navy leggings, the silver four-pointed star knee guard on the front of the knee, the crimson boot with its white ankle band, white toe cap and grey heel pointing to the image right - the SAME width and length in every frame (never squashed, stretched, sheared, slid sideways or broken into scraps); a bent knee is drawn as a bent leg; the far leg a shade darker where the near one crosses it; standing or braced frames plant both boots flat on the feet line, a lunge steps the front boot forward.
The arms and the blades: the arms are the design's arms - bare upper arm, white arm band, crimson arm guard, white wrist band, the hand with finger tips - never longer than the design's own arm (no long stretched arms), never thinner, each growing from its shoulder guard; she NEVER holds a blade - no grip, no hilt, no blade in her hand: the blades FLOAT free (at least one square clear of her hands) and she directs them with open hands, palm out or fingers pointing; the BLADES are the design's crescent blades (a crimson body, a white edge, a black outline between neighbours, the cyan gem at the root of the lower one): each blade ONE rigid object of exactly the design's shape and size, only moved and turned whole, drawn clean at every angle like oppi draws Sion's axe (refs/style_oppi_sion.png) - never bent, melted, shortened, thinned or changing shape from frame to frame; when they are not sent out they hover folded behind her back exactly as in the design.
The body: the head keeps the design's size, colours and details (the royal-blue hair dome with its sheen, the silver tiara with its V point, the slanted dark brows over the cyan eyes, NO mouth) but TURNS WITH THE BODY: seen from the front-right, the face toward the image right, the far eye narrower, the long hair falling behind her; the SAME turned head in every frame of an action, never pasted front-on; the silver breastplate with its red heart and cyan collar gem, the crimson tabard with its white edge, the silver-white shoulder guards (the near one in front, the far one partly behind her) stay on her in every frame.
Feet line: in every cell the soles are on square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there - the blades too. Her place across the cell follows the SECOND image (each frame's standing point is in irelia_cells.json). In the run her head keeps the same horizontal place relative to the standing point in every frame.
Side-on facing the image right (only the idle faces the camera); every cast goes to the RIGHT of the image; never her back, never upside down, never a mouth. Do not draw effects (thrown blades in flight for E and R, slash trails, sparks, glows, shockwaves) - only the character and the blades floating around her (never in her hands). Every animation starts and ends near the FIRST image's pose.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x128 squares (1024x1024 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #00FF00 green). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, every frame side-on, the head the design's size and turned to the right, no mouth, both arms growing from the shoulder guards in every frame, every blade rigid and full size, the bundle on her back when no blade is sent, the legs the same thickness in every frame, the run's boots swapping front and back, no loose pieces, no stray black squares, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 骨架 + 皮囊的短提示词（生图画不准尺寸时用；附图1 = now 条，图2 = 造型图）

```text
参考图1这张精灵图的动作序列和构图布局，把图1里的角色替换为图2的角色。
1. 保留图1所有帧的位置、大小、排列顺序和格子，每一格是 8×8 像素的纯色方块，人物不能变大也不能变小。
2. 保留每一帧的动作：身体侧过来朝右（只有待机是正面），手臂、飞刃和身体的方向和姿势照图1（出招都朝图的右边，不画背影、不倒立）；头、身体和腿的颜色、细节、大小用图2的，头跟着身体转过去，不画嘴。
3. 长相、配色、细节全部换成图2：宝蓝长发、银色V形头冠、深色斜眉和青色眼睛、银白胸甲和红心、领口青宝石、带白边的深红前摆、银白卷钩肩甲、白臂环红护臂、深藏青打底裤、银色星形护膝、红靴；背后一束弯月形飞刃（深红刃身、白刃口、黑描边，左下那把带青宝石）。
4. 手臂从肩甲长出来，和图2一样粗、不比图2长；**她从不手握飞刃**：飞刃是漂浮的，离手至少一格，她用张开的手掌或手指指挥；每把飞刃是一整块、大小形状不变；没有送出去的飞刃收在背后；E 和 R 掷出去的飞刃不画；任何东西不能低于脚底线。
5. 动作：[animation]
背景保持纯绿色 #00FF00，方便抠图。风格保持与图2一致。重点在于精准复刻图1的“动作骨架”，只是换了“皮囊”。
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `irelia_idle.png`（待机） | 8 × 160 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | **已做好，不用画** |
| `irelia_run.png`（跑步（交叉步，飞刃收在背上）） | 8 × 125 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | `RUN, 8 frames, one seamless loop (League's run, 1.0 s): the blade bundle stays FOLDED ON HER BACK exactly as in the design, the long hair streaming back, the arms swinging a little; the legs CROSS: in frames 1 and 5 the boots are furthest apart (frame 1 the near leg in front, frame 5 the far leg in front), in frames 3 and 7 the lifted boot passes BESIDE the other 1-2 rows up with the knee bent; the body bobs 1 row with each landing; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `irelia_attack.png`（普攻（一把飞刃斩出）） | 5 帧：60 70 80 80 80 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×2048，最后 1 格空 | 第 99 行 | `BASIC ATTACK (a blade slash), 5 frames: 1 turning to the right, the near hand drawn back, ONE crimson blade lifting off the bundle on her back; 2 crouching, the near arm swung back behind her, the blade floating up behind her shoulder (the design's blade, full size, not in her hand); 3 THE SLASH (the blow lands here): lunging forward, front knee bent, the near arm flung forward to the image right at chest height, the blade flying level a square or two ahead of her open hand, its point to the right; 4 following through, the blade swinging back past her; 5 back toward the stance, the blade back in the bundle.` |
| `irelia_skill.png`（Q 利刃冲击（冲刺穿过）） | 4 帧：60 70 70 70 | 第 3 帧（tick 8） | 4 列 × 1 行，4096×1024 | 第 99 行 | `BLADESURGE (Q, a dash through the target), 4 frames: 1 crouched low, leaning forward to the image right, the near hand forward; 2 dashing: the body low and leaning far forward, the front knee bent, the near hand thrust ahead with two blades shooting forward beside it, the hair and the back leg streaming behind; 3 THE STRIKE (lands here): at the end of the dash, the near arm swept forward and across, the two blades crossing in front of her; 4 rising back toward the stance, the blades folding back onto her back.` |
| `irelia_skill2.png`（E 比翼双刃（掷出双刃）） | 5 帧：70 70 80 70 80 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×2048，最后 1 格空 | 第 99 行 | `FLAWLESS DUET (E, two blades sent to meet), 5 frames: 1 turning to the right, both hands raised in front of her chest; 2 crouching a little, the near arm drawn back by her shoulder; 3 THE THROW (the blades leave here): the near arm flung forward to the image right, the hand open and empty (the thrown blades fly as an effect - do not draw them), the far hand pulled back; 4 straightening; 5 the stance turned right, the bundle on her back.` |
| `irelia_skill2_w.png`（W 距破之舞（格挡蓄力后斩出）） | 6 帧：80 120 160 170 100 100 | 第 5 帧（tick 32） | 3 列 × 2 行，3072×2048 | 第 99 行 | `DEFIANT DANCE (W, a guard, then a slash), 6 frames: 1 drawing the blades off her back around her; 2-4 CHARGING, the same guard in all three: the near knee raised high (a crane stance on the far leg), both forearms crossed in front of her face, three blades fanned upright in front of her as a shield (the design's blades, overlapping, full size), frame 4 the guard drawn tighter; 5 THE RELEASE (the slash goes here): a step forward, both arms swept forward and apart to the image right, the three blades thrust forward in a line at chest height, points to the right; 6 back toward the stance, the blades folding onto her back.` |
| `irelia_ult.png`（R 先锋之刃（飞刃齐射）） | 5 帧：70 80 90 90 100 | 第 3 帧（tick 9） | 3 列 × 2 行，3072×2048，最后 1 格空 | 第 99 行 | `VANGUARD'S EDGE (R, a volley of blades), 5 frames: 1 both arms raised, the blade bundle rising off her back above her head; 2 the blades fanned in a wide arc above and behind her, the near arm drawn back, the body arched; 3 THE LAUNCH (the volley leaves here): crouching low, both arms flung forward to the image right, palms out, NO blades on her or above her (they fly as an effect); 4 holding the crouch, arms forward; 5 rising toward the stance, the blades back on her back.` |
| `irelia_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×1024 | 第 99 行 | `HIT, 2 frames: 1 jolted back by a blow: her whole body and head pushed back 1-2 squares (to the left); 2 recovering toward the stance. The design's legs.` |
| `irelia_dead.png`（死亡（跪下倒地）） | 8 帧：100 100 120 150 150 200 300 400 | — | 4 列 × 2 行，4096×2048 | 第 99 行 | `DEATH, 8 frames: 1 struck: jolted back as in the hit; 2 the blades slipping off her back; 3-4 staggering, sinking to her knees, one hand on the ground; 5-6 collapsing forward onto her side; 7-8 lying still on her side, the blades on the ground beside her. Nothing below the feet line, never upside down.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块（在 1024 的格子里量过），透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色，明暗照定稿，没有自己加的碎点；
- [ ] 除待机外每帧都是侧身朝右；头和造型图一样大、细节一样，转向右边，不画嘴；身体（胸甲、前摆、肩甲、手臂、腿）看得见；同一个动作里各部件大小形状不变；
- [ ] 两只手臂都在、和造型图一样粗、不比造型图的手臂长，从肩甲长出来；手里没有握着任何飞刃（飞刃漂浮、离手至少一格）；每把飞刃是一整块、没有变小变形；没送出去的飞刃收在背后；
- [ ] 跑步飞刃一直收在背上，侧身交叉步（像 `refs/style_oppi_alistar.png`、`refs/style_oppi_vi.png`：每半个周期两只靴子交换前后、抬起的腿屈膝），腿每帧一样粗、没有碎块、没有缺格子；
- [ ] E 掷出那一帧起、R 齐射那一帧起，飞出去的刃不画；
- [ ] 脚底线以下没有任何像素（飞刃也不行）；黑边干净，没有零散的黑格；
- [ ] 没有背影、没有倒立；出招都朝图的右边；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 写全；生图原稿放进 `raw/`；最后写 `HANDOFF.md`。

## Claude 导入时（给 Claude 看）

- 交回的 `irelia_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、连通块、手臂粗细、身体和待机比、零散黑格、每帧面积和待机比），不在网格上的按格取多数色重读；身体变形的帧用造型图的部件重摆（rigkit：飞刃整把只平移和 90° 整转，整个人前倾、前冲、下蹲；不按任意角度转）。
- 放进 `assets/source/native/`，`irelia_cells.json` 用包里这份，待机由 `import_native.py` 的 idle_breathe 从造型图生成。
- `import_native.py`：ORDER 待机，COMPLETE 补描边；红色方：有前后之分、贴在她身上的特效烘进动作帧（`irelia_bake.json`），打击特效左右对称。
- 按出手帧核对技能数据的时机（普攻 tick 8、Q tick 8、E tick 8、W 斩出 tick 32、R tick 9），量头像截取点，重跑模拟，做预览 GIF。
