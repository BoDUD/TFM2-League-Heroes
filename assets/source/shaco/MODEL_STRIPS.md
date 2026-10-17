# 萨科：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是你按 46 格一格一格画的 **v4 A 版**（`shaco_native46_A`）：`design/shaco_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799；帽尖到脚底 46 格，37 格宽，17 色；只是整体左移了 4 格，让两脚中点落在第 64 列，像素一格没改）。**造型图就是标准**：双角小丑帽和两个金铃、白面具、冰青色眼睛、大笑的牙、金色褶领、银色尖刺护肩、红上衣、蓝袖子和红色大袖口、黑白格子灯笼裤、带银刺的蓝靴子、红色卷尖鞋、两把锯齿匕首、颜色、明暗，每一帧都照它，只改姿势。
> - **待机条已经做好**（`shaco_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/shaco_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体和匕首的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **两处和参考图不一样，以造型图为准**：① 匕首是造型图里的大小（约 6–7 格长，锯齿银刃、金色护手），参考图里的匕首更长，不要照着画长；② 头是贴上去的（见下），英雄联盟里帽子会甩、弯腰时头会朝下，我们**头每帧不变形、不旋转**（只有死亡倒地的两帧可以和身体一起整体转 90 度），**不画倒立、不画背影**。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/shaco_palette.png`，或直接读 `design/shaco_design_1x.png`）。**先把眼睛的冰青 `#03A7E9` 和亮芯 `#B8FAFF` 从色板里去掉**（吸附时会跑到手、刀刃上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/shaco_head_1x.png` 里不透明的格子：小丑帽的两只角和两个金铃、白面具、两只眼睛、鼻子、大笑的嘴，到下巴的描边为止；在 128×128 画布上的范围 x 50–74、y 54–72，**按图里的形状贴，不是整个方框**——两侧的尖刺护肩不属于头）原样贴进每一帧头的位置（只平移）。这样每帧的脸都和造型图一模一样。头下面接金色褶领和肩膀，不要画脖子。
5. 对位：每帧按 `shaco_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/shaco_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/shaco_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/shaco_head.png`、`_1x.png` | 要贴进每一帧的头（帽子、金铃、面具、眼睛、嘴，不含护肩和身体） | 贴头 |
| `design/shaco_palette.png` | 造型图的全部 17 色（暗到亮） | 色板 |
| `shaco_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/shaco_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体和匕首的动作 |
| `guide/shaco_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `shaco_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/shaco_picture.png` | 造型来源的原画 A（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_martial.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（帽尖到脚底 46 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 17 种颜色**，不加新颜色；明暗照定稿（亮边、金属高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。格子裤的格子保持 2×2 一格，不碎成单点。
- **身体粗细照定稿**：手臂至少 3 格宽（加描边），红色大袖口保持造型图的大小；腿是灯笼裤加细靴子；各部分之间有描边隔开，但身体、手臂、匕首必须连成一个整体，不能有飘在空中的碎块（死亡倒地时掉在地上的匕首除外）。
- **头每帧都是造型图的头**（帽子、金铃、面具、眼睛、鼻子、牙逐格一样），只平移（死亡倒地的帧可以整体转 90 度）；两只眼睛一样大、同一行；冰青 `#03A7E9` 和亮芯 `#B8FAFF` 只用在眼睛上。
- **两把匕首每帧都在手里**（死亡倒地前）：反手握，待机时近侧（图里左边）的刀刃朝后、远侧（右边）的刀刃朝下；挥砍时照第三张图转动；大小照造型图（约 6–7 格，锯齿银刃、金护手），不能飘开，不能挡住眼睛。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），刀尖也在它上面。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两条腿交替（前 4 帧一步、后 4 帧另一步，中间膝盖交错）；上下起伏最多 2 格；首尾能无缝接上。
- 3/4 正面朝右，**不画背影、不画倒立**（死亡最后倒地的帧是躺着，不算）。**只画角色**：飞出去的毒刃、惊吓魔盒、消失的烟、幻像分身、刀光、毒液都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/shaco_design.png`，第二张 `now/shaco_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `shaco_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, hat, mask, face, daggers and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same lanky jester proportions, the same two-horned hat with its bells, the same white mask with the glowing eyes and the toothy grin, the gold ruff, the silver spiked pauldrons, the crimson jacket, the navy upper arms with the big puffy crimson cuffs, the checkered pantaloons, the navy boots with silver spikes, the curled crimson shoes, the same two daggers, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the daggers from it, but keep the FIRST image's proportions and its shorter daggers, and never draw him upside down (where the original bows or falls head first, keep the head upright and only move it lower; only the lying death frames turn body and head together, at most a quarter turn).
The character: Shaco (a lanky demon jester: a two-horned jester hat - the navy horn curling back to the left, the crimson horn rising to the right, a gold bell on each tip - a white mask with two glowing ice-cyan eyes, a beak nose and a huge toothy grin, a gold ruff collar, silver spiked pauldrons, a crimson jacket with a gold belt, navy upper arms ending in big puffy crimson cuffs, pale blue-grey hands, black-and-white checkered pantaloons, navy boots with silver spikes, curled crimson shoes; a serrated silver dagger with a gold hilt in each hand).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (46 squares from the top of the hat to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 17 colors of the FIRST image, no new colors: #0F0419 #1D264A #2F2E40 #9C0D29 #B3112D #334782 #8A5D25 #475C75 #FC2D3F #03A7E9 #F3BF27 #8AAAC2 #AAA3BE #D1CBDE #FFF2A3 #B8FAFF #F7F7F8. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its lit edges and metal highlights move with the pose; no dithering, no noise, no random specks added; the checks of the pantaloons stay 2x2 squares. Arms at least 3 squares wide with the outline, joined to the body; no loose pieces.
The head (the hat with both horns and both bells, the mask with the eyes, the nose and the grin, down to the chin's outline) is COPIED from the FIRST image in every frame, square for square, and only moved (only the lying death frames turn it with the body, at most a quarter turn); never redraw, squash or tilt it, or it flickers when the frames play. It sits on the gold ruff - no neck. His eyes are the FIRST image's eyes (each: two ice-cyan squares, one bright core square and a dark corner), both the same size on the same rows; the cyan #03A7E9 and the core #B8FAFF appear ONLY in the eyes. A dagger is in each hand in EVERY frame (until he falls in the death): held in a reverse grip as in the FIRST image (the near hand's blade pointing back, the far hand's blade pointing down) unless the THIRD image swings it elsewhere; each blade the FIRST image's size (about 6-7 squares, serrated silver with a gold hilt); they move with his hands, never float free, and never cover his eyes.
Feet line: in every cell the lowest row of his feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not a dagger tip - because the game draws the health bar there (only the lying frames of the death may dip at most 2 squares). His place across the cell follows the SECOND image (each frame's standing point is in shaco_cells.json). In the move loop his head keeps the same horizontal place relative to the standing point in every frame and the legs alternate.
3/4 FRONT view facing right, never his back, never upside down. Do not draw effects (the thrown shiv, the jack-in-the-box, smoke puffs, the clone, slash trails, poison) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 112x96 squares (896x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, level and the same size, the cyan only in the eyes, a dagger in each hand in every frame, arms at least 3 squares wide, no loose pieces, nothing below the feet line, never his back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `shaco_idle.png`（待机） | 6 × 180 | — | 3 列 × 2 行，2688×1536 | 第 81 行 | **已做好，不用画** |
| `shaco_run.png`（移动） | 8 × 139 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (8 x 139 ms, the SECOND and THIRD images): Shaco's sly, springy jester run, light on his toes and leaning forward a little; the near arm (the red cuff on the left of the image) swings out in front, the far arm swings back, both daggers kept in his hands with the blades pointing down or back as in the THIRD image; the legs ALTERNATE as in the THIRD image (frames 1-4 one stride, 5-8 the other: the near leg forward in one half, the far leg in the other, the knees passing each other in between); frames 4 and 8 are the low landings (the body at most 2 squares lower), the others upright; his head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `shaco_attack.png`（普攻） | 6 帧：60 60 60 60 70 80 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BASIC ATTACK, 6 frames (League's attack1, a quick double slash): 1 he tenses, the daggers coming up; 2 the wind-up: he leans forward and twists back, the near dagger swung down behind him, the far arm drawn in; 3 THE SLASH (the hit lands here): he whips both arms open - the far dagger slashes out level to the right at the enemy, the near dagger flung back to the left; 4 the second cut: the near arm slashes across to the right, the far dagger swinging down to the left, the body twisted; 5 the far dagger flicked up, the near one still pointing right, leaning back; 6 back to the idle stance. Slash trails are effects - do not draw them.` |
| `shaco_attack_q.png`（Q 后的背刺普攻） | 6 帧：60 60 60 70 80 90 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536 | 第 81 行 | `BACKSTAB (the empowered attack after Deceive), 6 frames (League's attack3): 1 he crouches, both arms spread wide, the daggers out; 2 crouched lower, arms still wide, ready to pounce; 3 THE STAB (the hit lands here): he drops and drives both daggers down into the enemy in front of him, the far blade pointing down and forward, the jacket flaring; 4 still low, both blades pointing down in front; 5 he pulls the far dagger free, pointing right, low; 6 back up to the idle stance.` |
| `shaco_attack_e.png`（E 双面毒刃，掷刀普攻） | 6 帧：60 70 60 70 80 90 | 第 4 帧（tick 11） | 3 列 × 2 行，2688×1536 | 第 81 行 | `TWO-SHIV POISON (the throw that replaces an attack every few seconds), 6 frames (League's spell3): 1 the far hand lifts its dagger; 2 both daggers raised beside his face, the blades pointing down, leaning back a little; 3 the wind-up, the far dagger held high; 4 THE THROW (a poisoned shiv leaves his far hand here - the flying shiv is an effect, he keeps his own two daggers): he whips the arms down and forward, bending forward; 5 the follow-through, bowed forward with both arms low (the head stays upright and only moves lower and forward with the body, so the mask stays visible); 6 rising back to the idle stance.` |
| `shaco_skill.png`（Q 欺诈魔术） | 5 帧：50 60 70 80 90 | 第 3 帧（tick 7） | 3 列 × 2 行，2688×1536，最后 1 格空 | 第 81 行 | `DECEIVE (he vanishes and reappears behind the target), 5 frames (League's spell1): 1 he tenses; 2 a showman's flourish: both arms spread wide and low, the daggers out, knees bent; 3 THE VANISH (he turns invisible here; the puff of smoke is an effect): he spins and ducks, twisted, both daggers swept across in front of him; 4 still ducked low, the daggers crossed in front; 5 back to the idle stance.` |
| `shaco_skill2.png`（W 惊吓魔盒） | 5 帧：60 70 70 80 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2688×1536，最后 1 格空 | 第 81 行 | `JACK IN THE BOX (he tosses the box at the enemy's feet), 5 frames (League's spell2): 1 he crouches a little; 2 the wind-up: he twists back, the far arm drawn back behind him; 3 THE TOSS (the box leaves his far hand here, low and forward - the box is an effect, the dagger stays in his hand): the far arm swung forward and low, body bent forward; 4 the follow-through: he turns back, the near dagger sweeping out to the left; 5 back to the idle stance.` |
| `shaco_ult.png`（R 幻像） | 6 帧：70 80 80 90 90 100 | 第 2 帧（tick 4） | 3 列 × 2 行，2688×1536 | 第 81 行 | `HALLUCINATE (he vanishes for a moment and his clone appears behind the enemy), 6 frames (League's taunt): 1 he lowers his daggers; 2 THE CAST (the clone appears at the target - an effect): he points his far dagger straight out to the right at the target, the near dagger held down behind him; 3 a mocking flourish: the far dagger raised up and to the right; 4 he sweeps the near dagger across in front of him; 5 the far dagger out again, raised to the right; 6 back to the idle stance.` |
| `shaco_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1792×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow: his body and head pushed back 1-2 squares, the arms flung out a little, the daggers still in his hands (the head is the FIRST image's head, the eyes unchanged); 2 recovering toward the idle stance.` |
| `shaco_dead.png`（死亡） | 8 帧：100 100 100 120 120 120 150 400 | — | 4 列 × 2 行，3584×1536 | 第 81 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck, he rocks back, arms out; 2 reeling back, his head thrown back; 3 both daggers raised by his shoulders; 4 a last flourish: both arms flung up high; 5 the arms drop, he hunches over, the daggers crossed in front; 6 his knees buckle and he sinks forward; 7 he topples onto his side (body and head turned together, at most a quarter turn); 8 lying crumpled on the ground, still. The daggers stay in his hands until frame 6; in frames 7-8 they may lie on the ground beside him. Frames 7-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点，格子裤是 2×2 的格子；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡倒地的帧最多整体转 90 度），两只眼睛都在、一样大、同一高度；
- [ ] 冰青 `#03A7E9` 和亮芯 `#B8FAFF` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 两把匕首每帧都在手里（死亡第 7 帧起可以落在身边地上），大小照造型图，不挡眼睛；手臂至少 3 格宽，没有飘着的碎块；
- [ ] 没有背影、没有倒立；脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，两条腿交替，上下起伏不超过 2 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `shaco_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、冰青只在眼睛上、连通块、手臂粗细、每帧面积和待机比、跑步两腿交替），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`shaco_cells.json` 用包里这份，`shaco_idle.png` 用包里已做好的那张。
- `import_native.py --hero shaco`：ORDER 待机一张图 + BOB 呼吸，EYES = `#03A7E9`（按眼睛对齐待机和移动），COMPLETE 补描边，头是贴的：NECK 检查褶领每帧在下巴下同一行。
- 按出手帧核对技能数据的时机（普攻 tick 7、背刺 tick 7、毒刃 tick 11、Q tick 7、W tick 8、R tick 4），幻像分身（`league_shaco_clone`）用这些帧做，量特效挂点（手的高度）和头像截取点，重跑模拟，做预览 GIF。
