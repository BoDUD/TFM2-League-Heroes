# 虚空之女 卡莎：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：B44**（你上一轮的 Q 版原稿 B——翼舱抬起半张开——Claude 按它自己的格子逐格读回，删整行整列缩到 44 行，脸和眼睛一格没删）：`design/kaisa_design.png`（放大 8 倍，1024×1024，33×44 格、34 色，鞋底在 y=792–799）。**造型图就是标准**，颜色、形状、翼舱、头、脸、爪手一律照它。
> - **待机条已经做好**（`kaisa_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 8 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/kaisa_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染；渲染里的头已经转成待机的朝向，头巨大是 Q 版放大，**头一律照造型图**；渲染里的翼舱比造型图小，**翼舱的大小和样子一律照造型图**，只跟着动作抬、张、收）。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。最好打成一个 zip（`kaisa_strips_pack_done.zip`）放在 outputs 里。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。**读图时不要用品红抠背景**——她的洋红光、紫色甲壳会被一起抠掉；用透明背景，或者纯绿 `#00FF00` 背景。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/kaisa_palette.png`，或直接读 `design/kaisa_design_1x.png`）。**先把眼睛的颜色从色板里去掉**（虹膜紫 `#823EA3`、`#74368E` 和眼白，和头发、甲壳的紫色容易混），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/kaisa_head_1x.png`：深紫长发到下巴、脸、额头和脸颊的粉紫纹、两只眼睛、嘴；**不含翼舱**；在 128×128 画布上的范围 x 57–74、y 59–77）原样贴进每一帧头的位置，只平移；身体倾斜时整体倾斜；冲刺（R 第 4 帧）和死亡倒地的帧可以不贴。贴的头的下巴下面，颈口和领子从眼睛最下一行往下第 5 行开始，每一帧都一样（不能把头压进身体，也不要拉出一截脖子）。受击第 1 帧把眼睛改成闭眼（眼睛那一行各一段深色短线）。长发在下巴以下的部分跟着身体动（披在背后，往后飘）。
5. **翼舱**：两片翼舱每一帧都在，贴着背、和肩膀连在一起不留缺口、不挡脸：近处的翼舱在画面左边（近肩后面向左上张开的 2–3 片尖刃），远处的翼舱从远肩上方往右上升起；深紫甲壳、金边、各一只洋红椭圆光眼。大小和样子照造型图，只按动作抬高、张开（Q、W 出手时更开）、收拢（死亡时收成合起来的壳）。
6. **爪手**：深紫爪手，读得出是手（护腕 + 手背 + 爪尖），至少 2×2 格，手臂从肩膀到手至少 3 格粗（含描边），不要画成 1 格的黑棍或鸟爪。
7. 对位：每帧按 `kaisa_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），鞋底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
8. 按最后的「交回前自查」逐项检查，尤其是：每帧整个人（连同两片翼舱）连成一块，眼睛颜色只在眼睛上。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/kaisa_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，鞋底第 99 行 | 每张动作图的第一张附图 |
| `design/kaisa_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/kaisa_head.png`、`kaisa_head_1x.png` | 只有头（长发到下巴、脸、眼睛、纹路；不含翼舱），在画布上原来的位置 | 贴头 |
| `design/kaisa_palette.png` | 造型图的全部 34 色（暗到亮） | 色板 |
| `kaisa_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/kaisa_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体、手臂和翼舱的动作 |
| `guide/kaisa_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `kaisa_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/kaisa_picture.png` | 用户选的原图 B（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref_ranged.png`、`style/pack_quality_ref.png` | 团战经理2 原版远程英雄、本包英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（44 格，翼舱尖到鞋底），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 34 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。她通身深紫：甲壳保持造型图的亮边，不要整块涂成描边色。
- **头每帧都是造型图的头**（长发、额头和脸颊的纹、眼睛、嘴逐格一样），只平移或整体倾斜；眼睛的颜色（虹膜紫 `#823EA3`、`#74368E`）只用在眼睛上。
- **翼舱每帧都在**，贴着背不留缺口，不挡脸；形状、大小、配色照造型图，只按动作抬、张、收。
- **手和手臂**：爪手至少 2×2 格，手臂从肩膀到手至少 3 格粗（含描边），不能画成 1–2 格的细线（在游戏里像"无影手"）；每帧整个人连成一块。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面）。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：两条腿交替迈步（前 4 帧一步、后 4 帧另一步，中间有两膝交叉的帧），两条腿颜色和待机一样（深紫腿甲、金边、洋红纹），每帧头相对站位点的横向位置不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，看得到脸，不画背影。**只画角色**：电浆弹、导弹、虚空冲击波、冲刺拖尾、护盾、光环都是单独的特效，不要画。每个动作开始和结束都接近造型图的待机姿势。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯绿 `#00FF00`，**不要用品红**）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/kaisa_design.png`，第二张 `now/kaisa_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `kaisa_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, the two wing-pods, the head, face, clawed hands and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the shot, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms, the legs and the wing-pods from it (its head is oversized and turned like the idle on purpose, and its pods are smaller than the FIRST image's: the head and the pods' size and look always come from the FIRST image).
The character: a chibi young woman in a living alien battle-suit: long dark purple hair, a pale face with lilac eyes and thin pink-violet marks on the forehead and one cheek, a pale steel-blue bodysuit, dark violet armour plates with lighter violet rims and thin gold trims, glowing magenta slits on the thighs and forearms, dark clawed armoured hands, clawed boots. On her back two large WING-PODS raised behind her shoulders: dark violet shells with gold rims, each with a glowing magenta oval eye; the near one spreads to the upper LEFT behind her near shoulder as 2-3 pointed blades, the far one rises over her far shoulder to the upper right. She has no weapon in her hands: she fires from her palms and forearms.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (44 squares tall from the pods' tips to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 34 colors of the FIRST image, no new colors: #160722 #1E0A2A #351036 #2A1F46 #3D1B56 #352657 #4E194C #4B3245 #4F2472 #6A106C #463970 #77504E #9A068B #8D6246 #74368E #8A387A #823EA3 #6D5EA2 #B48451 #6778AB #887CBF #DA26D0 #8E9AB3 #D48D84 #D7A965 #F408EA #8F9FC6 #F291DE #F7D896 #C4CEE3 #FBD3B6 #C3D4F0 #EFF2F6 #F9F6FA. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring; keep the armour's lighter violet rims, never fill armour with the outline color. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (the hair down to the chin, the face, the marks, the eyes and the mouth; NOT the pods) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. Under the chin keep the FIRST image's rows: the collar starts 5 rows under the eyes' lowest row in every frame; never sink the head into the body. The eyes are the FIRST image's eyes; the eye purples #823EA3 and #74368E appear ONLY in the eyes. Both wing-pods are in every frame, joined to her back with no gap, never covering her face, their size and look as in the FIRST image (they only rise, open wider or fold as the animation says). The clawed hands are at least 2x2 squares and read as hands (wrist plate, back of the hand, claw tips), the arms at least 3 squares thick from the shoulder to the hand, never a 1-2 square line; the whole figure with both pods is ONE connected piece in every frame.
Feet line: in every cell the lowest row of her boots is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there (the kneeling frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in kaisa_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame, and the legs alternate.
3/4 FRONT view facing right, her face always visible, never her back. Do not draw effects (plasma bolts, missiles, the void blast, dash trails, shields, glows around her) - only the character; the magenta glow squares that are part of her suit and pods stay. Every animation starts and ends near the FIRST image's idle stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid pure green #00FF00 - never magenta, her glows are magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, the eye purples only in the eyes, both pods in every frame and joined to her back, the hands readable with arms at least 3 squares thick, one connected piece per frame, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `kaisa_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `kaisa_run.png`（移动） | 8 × 116 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of the run in the SECOND and THIRD images (0.93 s, 8 x 116 ms): she runs forward leaning a little, the clawed hands swinging; the two wing-pods stay raised behind her shoulders as in the FIRST image and ride with her upper body (swept back a little, never detached); the legs ALTERNATE like the THIRD image - frames 1-4 one stride, 5-8 the other, the knees crossing in the passing frames, the clawed boots planted flat on the ground line; the long hair swings a little behind her; her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `kaisa_attack.png`（普攻（手掌电浆弹）） | 6 帧：60 60 70 70 70 70 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, a plasma shot from her NEAR hand, 6 frames as in the THIRD image: 1 from the idle she crouches a little, the near arm drawing back; 2 the near arm cocked at her side, the palm glowing; 3 THE SHOT (the plasma bolt leaves here): she thrusts the near hand forward to the right at the height of her belly, palm out, one bright magenta square in the palm, the arm straight; 4 the arm still out; 5 drawing it back; 6 back toward the idle of the FIRST image. The pods stay raised as in the FIRST image.` |
| `kaisa_skill.png`（Q 艾卡西亚暴雨（翼舱张开发射导弹）） | 6 帧：70 70 80 80 100 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2304×1536 | 第 81 行 | `ICATHIAN RAIN, 6 frames as in the THIRD image: 1 she crouches, the pods start to open; 2 the pods swing wide open like wings, their magenta missile bays glowing; 3 THE LAUNCH (the missiles leave here): the pods fully spread, flared up and outward, their magenta eyes at their brightest, her arms thrown back; 4 still spread; 5 the pods folding back toward the FIRST image's raised pose; 6 back toward the idle. The opened pods (frames 2-4) are wider than in the FIRST image but in its colours and style (dark violet shells, gold rims, magenta eyes). Draw NO missiles (they are separate effects).` |
| `kaisa_skill2.png`（W 虚空索敌（前臂炮）） | 7 帧：80 90 100 110 80 70 70 | 第 5 帧（tick 23） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `VOID SEEKER, 7 frames as in the THIRD image: 1 she crouches; 2 she drops low, the near arm drawn back, its forearm armour folding open into a small cannon (a few dark violet and magenta squares on the forearm); 3 aiming: the cannon arm stretched forward to the right, level at chest height; 4 charging, the cannon's magenta glow brightens; 5 THE SHOT (the void blast leaves here): the recoil pushes her arm up 1 square and the pods flare wide open; 6 recovering, the cannon folding away; 7 back toward the idle. Draw NO beam or blast (separate effect).` |
| `kaisa_ult.png`（R 猎手本能·起跳和冲刺） | 4 帧：60 60 60 600 | 第 3 帧（tick 7） | 4 列 × 1 行，3072×768 | 第 81 行 | `KILLER INSTINCT, the launch, 4 frames as in the THIRD image: 1 she crouches deep, the pods raised high; 2 she coils forward; 3 THE LAUNCH: she springs forward to the right, the body leaning low; 4 THE DASH (held while she flies to the target): the body almost horizontal, flying to the right, the clawed hands forward, the pods swept back behind her, the hair streaming back. Keep frame 4 inside its cell and above the feet line (the game moves her); draw NO trail (separate effect).` |
| `kaisa_ult_land.png`（R 猎手本能·落地） | 4 × 60 | — | 4 列 × 1 行，3072×768 | 第 81 行 | `KILLER INSTINCT, the landing, 4 frames as in the THIRD image: 1 landing in a low crouch, the front knee bent, the clawed hands near the ground, the pods spread; 2 still crouched, rising a little; 3 rising; 4 back toward the idle of the FIRST image.` |
| `kaisa_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, head and shoulders pushed back 1 square, eyes squeezed shut (two short dark lines on the eyes' rows), the pods jolted with her back; 2 recovering toward the idle.` |
| `kaisa_dead.png`（死亡） | 8 帧：100 100 110 110 120 130 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames as in the THIRD image: 1 struck, she rises a little, the pods flaring up; 2-3 she twists and sags, the pods drooping; 4-5 she sinks; 6 she falls to her knees; 7-8 kneeling and slumped forward on the ground, the pods folded down over her back like a closed shell, their magenta eyes dimmed to dark magenta. Frames 7-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、同一行；
- [ ] 眼睛的紫（`#823EA3`、`#74368E`）只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 两片翼舱每帧都在、贴着背、不挡脸，形状配色照造型图；
- [ ] 爪手至少 2×2 格、手臂至少 3 格粗；每帧整个人连成一块；
- [ ] 脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：两腿交替、颜色和待机一样，头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `kaisa_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛的紫只在眼睛上、每帧连成一块、两片翼舱都在、每帧面积和待机比），不在网格上的重新取样（**不用品红抠图键**：`(r-g>80)&(b-g>80)` 会吃掉她的紫和洋红）；眼睛不对的帧换回造型图的头；每帧量眼睛到领口的行数，和造型图（5）对照。
- 放进 `assets/source/native/`，`kaisa_cells.json` 用包里这份，`kaisa_idle.png` 用包里已做好的那张。
- `import_native.py --hero kaisa`：ORDER 待机一张图 + BOB 呼吸（分界线选在腰下，不切过翼舱和长发），EYES = `#823EA3`，补描边（COMPLETE），NECK，走路 STEP 起伏。
- 按出手帧核对技能数据的时机（普攻 tick 7、Q 导弹 tick 8、W tick 23、R 起跳 tick 7），量出手点挂点（手掌、翼舱、前臂炮）和头像截取点、选人卡片 banpick_center，重跑模拟，做预览 GIF。
