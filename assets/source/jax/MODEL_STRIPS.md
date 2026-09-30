# 贾克斯：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：A41**。Claude 按你交回的 A 版逐格读回（没有缩放模糊），压到 24 色、只留一圈描边，把右上那颗灯眼放平，去掉脚底线下面的一根刺，再在面具以外删整行整列缩到 41 行：`design/jax_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799）。**造型图就是标准**，颜色、形状、兜帽、面具、灯柱一律照它。
> - **待机条已经做好**（`jax_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 11 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/jax_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。英雄联盟的灯柱比我们的长，**灯柱长度照造型图**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/jax_palette.png`，或直接读 `design/jax_design_1x.png`）。**先把灯眼的青色 `#46F0FF` 从色板里去掉**（它只随第 4 步贴的头回来）。
4. **贴头**：把造型图的头（`design/jax_head_1x.png`：只有蓝色马尾、品红兜帽、青铜面具和四颗灯眼、金扣和它们的描边，羽毛领、手臂和灯柱已去掉；在 128×128 画布上的范围 x 51–75、y 59–78）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。头贴在肩膀和羽毛领上，下巴下面不要露出一截脖子；循环动作（移动）各帧肩膀都在下巴下同一行。
5. 对位：每帧按 `jax_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人和灯柱连成一块、手臂至少 3 格粗、拳头清楚地握在灯柱上。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/jax_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/jax_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/jax_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `design/jax_head.png`、`jax_head_1x.png` | 要贴的头（马尾、兜帽、面具） | 贴头 |
| `jax_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/jax_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/jax_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `jax_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/jax_picture.png` | 用户给的原图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（41 格，含马尾），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（马尾、兜帽、面具逐格一样），只平移或整体倾斜；四颗灯眼每颗 1 格，青色 `#46F0FF` 只用在这四格上；没有嘴、没有人脸。
- **灯柱每帧都在**：一根连续的杆子（2 格粗），一头青铜钩子，一头发橙光的灯笼和带刺圆盘；长度照造型图（英雄联盟的更长，不要照它）；握在拳头里，不能断开、不能飘开、不能挡住面具。
- **手和手臂**：拳头至少 3×3 格（带棕色护腕和缠带），手臂从肩膀到拳头至少 3 格粗，不能画成 1–2 格的细线（在游戏里像“无影手”）；每帧整个人和灯柱连成一块。参考图里灯柱换到另一只手的地方，照造型图的手来画。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），灯笼和尖刺也不能低于它。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到面具，不画背影（死亡最后趴下的帧除外）。**只画角色**：灯柱的光效、反击的旋风、砸地的冲击波这些都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/jax_design.png`，第二张 `now/jax_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `jax_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, mask, lamppost and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look and NOT its longer lamppost. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
The character: a hulking chibi warrior with pale lavender skin and huge arms, a magenta hood whose opening is filled by a bronze faceplate mask with four glowing cyan lights, a spiky dark-purple feather collar, a royal-blue ponytail plume rising from a gold clasp on the hood and sweeping back, a sleeveless magenta vest with pink piping and gold buttons, a magenta cape behind him with dark-purple panels ending in bronze claw hooks, brown forearm wraps and a big brown bracer, a brown belt with a pouch, dark navy trousers with magenta knee pads, bare lavender feet in grey sandals; his weapon is a long lamppost with a bronze hook cap at one end and a spiked bronze lantern glowing orange at the other.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares tall from the plume to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #0F0213 #110315 #17021C #2C1820 #311135 #12166B #550343 #34195F #283354 #8A2901 #1B2496 #732E34 #704A23 #7E0260 #693A5D #242EB4 #C62D57 #A17337 #5D59AE #BB1E8E #B48340 #8580BA #E4BE6A #46F0FF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (plume, hood, mask with its four lights) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play; it sits on the shoulders and the feather collar with no neck showing. The lamppost is in every frame, ONE continuous pole 2 squares thick held in his fists: the bronze hook cap at one end, the orange-lit bronze lantern and the round spiked disc with its long middle spike at the other - the FIRST image's lamppost at the FIRST image's length (the THIRD image's is longer; use ours), never broken, never floating free. His hands are the FIRST image's big fists (at least 3x3 squares, the brown bracer and wraps on the forearms) and his arms at least 3 squares thick from the shoulder to the fist - never a 1-2 square line; the whole figure and the lamppost are ONE connected piece in every frame. Where the THIRD image holds the lamppost in the other hand, follow the FIRST image's hands. The face is the FIRST image's bronze mask with its four cyan lights (#46F0FF, one square each, cyan-gold-cyan / gold-gold-gold / cyan-gold-cyan); that cyan appears ONLY in those four squares. No mouth, no human face.
Feet line: in every cell the lowest row of his feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the lantern, not a spike, not the cape - because the game draws the health bar there (a fall may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in jax_cells.json). In a move loop his head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, the mask always visible, never his back (except the last frames lying face down). Do not draw effects (glows, whirlwinds, shock waves) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the four cyan lights visible and level, arms at least 3 squares thick with fists on the pole, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `jax_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 75 行 | **已做好，不用画** |
| `jax_run.png` | 8 × 133 | — | 4 列 × 2 行，3072×1536 | 第 75 行 | `MOVE, 8 frames, one seamless loop of League's run (1.07 s cycle, 8 x 133 ms, the SECOND and THIRD images): he runs hunched forward, the lamppost held level at hip height in both fists with the spiked lantern pointing forward (right), as in the THIRD image; the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames; his head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `jax_attack.png` | 6 帧：60 60 50 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 75 行 | `BASIC ATTACK, 6 frames, a big lunging swing of the lamppost as in the THIRD image: 1 he draws the lamppost back and up; 2 he lunges forward, arms swinging; 3 the swing sweeps down low in front; 4 the release (the hit lands here): the lantern end smashes down in front of him to the right; 5 follow-through; 6 back toward the idle stance.` |
| `jax_attack_w.png` | 6 帧：60 60 50 80 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 75 行 | `EMPOWER, the charged smash, 6 frames as in the THIRD image: 1-2 he raises the lamppost high over his head and back; 3 he swings it down over his head with both hands; 4 the release (the hit lands here): the lantern end slams the ground in front of him to the right, body crouched low; 5 still crouched, the lamppost on the ground; 6 back toward the idle stance. The glow is an effect - do not draw it.` |
| `jax_attack_e.png` | 6 帧：60 60 50 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 75 行 | `BASIC ATTACK during COUNTER STRIKE, 6 frames as in the THIRD image: 1-2 he whirls the lamppost; 3 a quick spinning strike downward; 4 the release (the hit lands here): the lantern end strikes low in front of him; 5 he swings the lamppost back up; 6 it spins over his head, heading back to the idle stance.` |
| `jax_attack_r.png` | 6 帧：60 60 50 70 80 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 75 行 | `BASIC ATTACK during GRANDMASTER-AT-ARMS, 6 frames as in the THIRD image: 1-2 he raises the lamppost upright on his left, then brings it down; 3 low wind-up; 4 the release (the hit lands here): a long low THRUST forward with the lantern end, his body stretched forward; 5 held low; 6 back toward the idle stance.` |
| `jax_skill.png` | 7 帧：60 60 60 60 90 90 100 | 第 5 帧（tick 14） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 75 行 | `LEAP STRIKE, 7 frames as in the THIRD image: 1 he crouches, gathering; 2 he springs up; 3-4 in the air, the lamppost raised over his head; 5 the release (the hit lands here): he lands and smashes the lantern end down onto the target in front of him, crouched; 6 still crouched; 7 back toward the idle stance. In the air he stays at most about 8 squares above the feet line.` |
| `jax_skill2.png` | 6 × 60 | — | 3 列 × 2 行，2304×1536 | 第 75 行 | `COUNTER STRIKE, the stance starts, 6 frames as in the THIRD image: 1 he lifts the lamppost; 2-6 he spins it over his head like a propeller, with both hands above his head, the lamppost at a different angle in each frame (the spin must read); his feet stay planted.` |
| `jax_skill2_burst.png` | 6 帧：60 70 70 70 80 90 | 第 2 帧（tick 4） | 3 列 × 2 行，2304×1536 | 第 75 行 | `COUNTER STRIKE, the counter, 6 frames as in the THIRD image: 1 gathering; 2 the release (the stun happens here): he spins round with the lamppost swept out wide and low; 3-4 the sweep continues round him; 5 he lands in a crouch; 6 back toward the idle stance.` |
| `jax_ult.png` | 7 帧：60 60 60 60 90 90 100 | 第 5 帧（tick 15） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 75 行 | `GRANDMASTER-AT-ARMS, the slam, 7 frames as in the THIRD image: 1 he crouches; 2 he jumps; 3-4 in the air with the lamppost raised upright; 5 the release (the slam lands here): he plants the lamppost straight down into the ground beside him, lantern end UP, landing crouched; 6 holding it planted upright; 7 back toward the idle stance. In the air he stays at most about 8 squares above the feet line. The shock wave is an effect - do not draw it.` |
| `jax_hit.png` | 2 × 100 | — | 2 列 × 1 行，1536×768 | 第 75 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back; 2 recovering toward the idle stance.` |
| `jax_dead.png` | 8 帧：100 100 100 120 120 120 150 400 | — | 4 列 × 2 行，3072×1536 | 第 75 行 | `DEATH, 8 frames, going down in ONE movement as in the THIRD image: 1 struck; 2 staggering, the lamppost swung up; 3-5 he sinks to one knee leaning on the lamppost planted upright beside him; 6 he falls forward; 7-8 lying face down on the ground line, the lamppost on the ground beside him. Frames 6-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），四颗灯眼都在、各 1 格、上下两对各在同一行；
- [ ] `#46F0FF` 只出现在四颗灯眼上：头部范围以外 0 个像素；
- [ ] 灯柱每帧都在，一根连续的杆子，长度照造型图，握在拳头里；
- [ ] 手臂至少 3 格粗、拳头至少 3×3；每帧整个人和灯柱连成一块（没有飘开的碎块）；
- [ ] 脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `jax_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、灯眼只在面具上、每帧连成一块、每帧面积和待机比），不在网格上的重新取样；灯眼不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`jax_cells.json` 用包里这份，`jax_idle.png` 用包里已做好的那张。
- `import_native.py --hero jax`：ORDER 待机一张图 + BOB 呼吸（呼吸分界线选在小腿，不切过披风下摆、护膝和脚的交界），EYES = `#46F0FF`，补描边（COMPLETE）。
- 按出手帧核对技能数据的时机（普攻四种 tick 10、跳斩落地 tick 14、反击 tick 4、大招砸地 tick 15），重量特效挂点和头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
