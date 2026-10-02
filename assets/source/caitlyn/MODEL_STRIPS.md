# 皮城女警 凯特琳：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：B42**（你上一轮的 Q 版原稿 B，Claude 按它自己的格子逐格读回，帽子、脸、身体、腿分区删行到 42 行；右手前面那段枪管被删歪了，按枪身的斜线重画成 1 格粗的直金色枪管，米色枪管改成金色）：`design/caitlyn_design.png`（放大 8 倍，1024×1024，41×41 格、24 色，鞋底在 y=792–799）。**造型图就是标准**，颜色、形状、高礼帽、头、脸、步枪一律照它。
> - **待机条已经做好**（`caitlyn_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/caitlyn_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；渲染里的头已经转成待机的朝向，帽子巨大是 Q 版放大，**头一律照造型图**）；长相照造型图。**步枪长度照造型图**（枪托到枪口约 39 格）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。最好打成一个 zip（`caitlyn_strips_pack_done.zip`）放在 outputs 里。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/caitlyn_palette.png`，或直接读 `design/caitlyn_design_1x.png`）。**先把眼睛的蓝 `#1454A9` 从色板里去掉**（它和头发的深蓝、步枪的青色都容易混），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/caitlyn_head_1x.png`：紫色高礼帽和金色 V 纹、青色宝石、帽檐、两侧的深蓝长发到下巴、脸、眼睛和嘴；在 128×128 画布上的范围 x 50–72、y 59–77）原样贴进每一帧头的位置，只平移；身体倾斜时整体倾斜；死亡倒地的帧可以不贴。贴的头的下巴下面，白色领巾从眼睛最下一行往下第 5 行开始，每一帧都一样（不能把头压进身体，也不要拉出一截脖子）。受击第 1 帧把眼睛改成闭眼（眼睛那一行各一段深色短线）。长发在下巴以下的部分跟着身体动（披在背后，往后飘）。
5. **步枪**：一件完整的直的东西，长度照造型图（约 39 格）：金色细枪管 1 格粗、上下各一格描边，不断开、不弯；枪身有象牙白护板、青色能量线和两个金框镜片；镂空枪托带白托垫；末端青色枪口。两只手都握在枪上（近处的手在枪柄、远处的手托住枪身）。斜着的时候也是一格一格连着的直线。
6. 对位：每帧按 `caitlyn_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
7. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人连成一块，手至少 2×2 格、连着至少 3 格粗的手臂，步枪是直的。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/caitlyn_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张动作图的第一张附图 |
| `design/caitlyn_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/caitlyn_head.png`、`caitlyn_head_1x.png` | 只有头（高礼帽、长发到下巴、脸），在画布上原来的位置 | 贴头 |
| `design/caitlyn_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `caitlyn_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/caitlyn_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体和步枪的动作 |
| `guide/caitlyn_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `caitlyn_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/caitlyn_picture.png` | 用户选的原图 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref_ranged.png`、`style/pack_quality_ref.png` | 团战经理2 原版远程英雄、本包女英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（41 格，帽顶到鞋底），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（高礼帽、金纹、宝石、帽檐、长发、眼睛、嘴逐格一样），只平移或整体倾斜；眼睛的蓝 `#1454A9` 只用在眼睛上。
- **步枪每帧都在**（死亡倒地后躺在她前面）：直的、完整的，长度照造型图，金色细枪管 1 格粗加上下描边；握在两只手里，不能断开、不能飘开、不能挡脸。
- **手和手臂**：手至少 2×2 格，手臂从肩膀到手至少 3 格粗（含描边），不能画成 1–2 格的细线（在游戏里像"无影手"）；每帧整个人连成一块。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），枪托也不能低于它。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），两条腿颜色和待机一样（深色紧身裤、棕色长靴），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到脸，不画背影。**只画角色**：枪口火光、子弹、夹子、网、准星这些都是单独的特效，不要画。每个动作开始和结束都接近造型图的待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/caitlyn_design.png`，第二张 `now/caitlyn_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `caitlyn_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, top hat, head, face, rifle and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the shot, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the rifle from it (its head is oversized and turned like the idle on purpose: the head always comes from the FIRST image).
The character: a chibi sheriff woman: a TALL PURPLE TOP HAT with two gold stripes and a cyan gem on its band, very long straight dark navy-indigo hair framing her face and falling behind her back, fair skin, blue eyes, a white cravat, a short brown leather jacket with gold-trimmed shoulders, a purple dress with a gold hem, dark leggings and knee-high brown boots with small heels. Her weapon is a long GOLD sniper rifle, held in both hands: a straight barrel ONE square thick with the outline above and below it, a body with an ivory panel, cyan energy lines and two round gold lens rings, a skeletal gold stock with a white butt pad, a cyan tip at the muzzle.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (41 squares tall from the top of the hat to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #0A020E #100216 #23102D #1D1C34 #301A28 #341340 #4E2D22 #272A50 #451B59 #6F4434 #80571A #1454A9 #A07335 #B48830 #CB516B #41B6AE #27CCE2 #D7AE50 #E1A58E #E3CB92 #C4C2C0 #EDDDB1 #FAD3BA #F9F8F9. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (the top hat with its gold stripes and gem, the brim, the hair down to the chin, the face, eyes and mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. Under the chin keep the FIRST image's rows: the white cravat starts 5 rows under the eyes' lowest row in every frame; never sink the head into the body. The eyes are the FIRST image's eyes; the blue #1454A9 appears ONLY in the eyes. The rifle is in every frame, whole, STRAIGHT and as long as in the FIRST image (about 39 squares from the butt to the muzzle), held in both hands; the hands at least 2x2 squares and the arms at least 3 squares thick from the shoulder to the hand, never a 1-2 square line; the whole figure is ONE connected piece in every frame.
Feet line: in every cell the lowest row of her boots is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the rifle's butt - because the game draws the health bar there (the lying frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in caitlyn_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, her face always visible, never her back. Do not draw effects (muzzle flashes, bullets, the trap, the net, crosshairs, glows) - only the character. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the blue only in the eyes, the rifle whole and straight with a 1-square gold barrel, the arms at least 3 squares thick with the hands on the rifle, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `caitlyn_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `caitlyn_run.png`（移动） | 8 × 117 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of the run in the SECOND and THIRD images (0.93 s, 8 x 117 ms): she runs forward with the rifle held across her chest in both hands, the barrel slanting up to the front right as in the FIRST image; the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames, the heeled boots planted flat on the ground line; the long hair swings a little behind her; her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `caitlyn_attack.png`（普攻） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, a rifle shot, 6 frames as in the THIRD image: 1 from the idle she raises the rifle to her shoulder; 2 aiming level to the right, the stock at her shoulder, both hands on the rifle; 3 THE SHOT (the bullet leaves here): a small recoil - the muzzle kicks up 1 square and her shoulder rocks back 1 square; 4 settling, still aimed; 5 lowering the rifle; 6 back toward the idle of the FIRST image.` |
| `caitlyn_passive.png`（爆头（被动的强化射击）） | 6 帧：60 50 50 70 70 67 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `HEADSHOT, the strong shot, 6 frames as in the THIRD image: 1 she drops into a wider, lower stance, bringing the rifle to her shoulder; 2-3 crouched a little, aiming level to the right, steady; 4 THE SHOT (the bullet leaves here): a big recoil - the muzzle kicks up 2 squares, her shoulders pushed back; 5 recovering; 6 rising back toward the idle.` |
| `caitlyn_skill.png`（Q 和平使者） | 8 帧：70 70 70 70 60 60 100 167 | 第 7 帧（tick 24） | 4 列 × 2 行，3072×1536 | 第 81 行 | `PILTOVER PEACEMAKER, 8 frames as in the THIRD image: 1 she twirls the rifle up over her shoulder, the long hair swinging out; 2 swinging it down in front of her; 3 she drops to one knee; 4-6 kneeling, aiming the rifle level to the right, perfectly steady (the wind-up); 7 THE SHOT (the big round leaves here): a strong recoil - the muzzle kicks up 2 squares; 8 rising back toward the idle. The rifle stays one straight piece in every frame.` |
| `caitlyn_skill2.png`（W 约德尔诱捕器（扔夹子）） | 6 帧：60 50 57 80 80 73 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `YORDLE SNAP TRAP, 6 frames as in the THIRD image: 1 she lifts the rifle upright in her near hand; 2 she bends forward; 3 crouching, she reaches down and forward with her free hand; 4 THE THROW (the trap leaves here): her free hand flicks forward and low to the right, tossing - the trap itself is a separate effect, draw NO trap; 5 straightening up; 6 back toward the idle.` |
| `caitlyn_e.png`（E 90口径绳网（射网后跳）） | 8 帧：50 50 67 67 67 83 100 83 | 第 3 帧（tick 6） | 4 列 × 2 行，3072×1536 | 第 81 行 | `90 CALIBER NET, 8 frames as in the SECOND and THIRD images: 1 she braces, the rifle pointed forward and a little down; 2 crouched, aiming low to the right; 3 THE NET SHOT (the net leaves here; draw NO net): the big recoil throws her backward off her feet; 4-5 flying backward through the air, at most 5 squares above the ground line, the rifle still pointing forward to the right, her knees tucked; 6 landing on her feet, knees bent; 7 crouched, recovering; 8 back toward the idle. The game moves her back along the ground; keep her inside her cell and facing right.` |
| `caitlyn_ult.png`（R 让子弹飞（跪射）） | 9 帧：100 100 200 200 200 217 150 150 83 | 第 7 帧（tick 61） | 4 列 × 3 行，3072×2304，最后 3 格空 | 第 81 行 | `ACE IN THE HOLE, 9 frames as in the THIRD image: 1 she swings the rifle up; 2 she drops to one knee; 3-6 kneeling, aiming down the long rifle to the right, perfectly still - the 1 s aim (frames 3-6 almost the same: at most the hair or a fold moves by one square); 7 THE SHOT (the bullet leaves here): a big recoil - the muzzle kicks up 2 squares and her shoulder rocks back; 8 still kneeling, lowering the rifle; 9 rising toward the idle.` |
| `caitlyn_hit.png`（受击） | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back 1 square, eyes squeezed shut (two short dark lines on the eyes' rows); 2 recovering toward the idle.` |
| `caitlyn_dead.png`（死亡） | 8 帧：100 100 110 110 120 130 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames as in the THIRD image: 1 struck, staggering; 2-5 she sinks to one knee, leaning on the rifle planted upright beside her (the hat still on); 6 she topples over; 7-8 lying on her side on the ground line, the hat beside her head, the rifle lying in front of her. Frames 7-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、同一行；
- [ ] 眼睛的蓝 `#1454A9` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 步枪每帧都在（死亡倒地后躺在地上），直的、不断开，枪管 1 格粗加上下描边，长度照造型图；
- [ ] 手至少 2×2 格、手臂至少 3 格粗；每帧整个人连成一块；
- [ ] 脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替、颜色和待机一样，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `caitlyn_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、蓝色只在眼睛上、每帧连成一块、步枪完整且是直的、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头；每帧量眼睛到领巾的行数，和造型图（5）对照，做成表再给用户看。
- 放进 `assets/source/native/`，`caitlyn_cells.json` 用包里这份，`caitlyn_idle.png` 用包里已做好的那张。
- `import_native.py --hero caitlyn`：ORDER 待机一张图 + BOB 呼吸（分界线选在腰下，不切过枪和长发），EYES = `#1454A9`，补描边（COMPLETE），NECK，走路 STEP 起伏。
- 按出手帧核对技能数据的时机（普攻 tick 7、爆头 tick 10、Q tick 24、W 扔夹子 tick 10、E 射网 tick 6、R tick 61），量枪口挂点（火光、子弹从枪口出）和头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
