# 青钢影：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选定的是 `design/camille_design.png`（放大 8 倍，1024×1024，刀尖在 y=792–799；头顶到刀尖 46 格，21 格宽，49 色）。它来自你之前生成的那张 65 格的青钢影（`refs/camille_source_65.png`），头一行不删、身体按行删到 46 格。**造型图就是标准**：银白偏薄荷的尖角短发和后脑发髻、青蓝眼睛、深蓝高立领和深蓝宝石、天蓝胸甲、黑手套和金腕带、宽胯和金色电路纹、近侧胯上的浅青核心、金色膝关节、两把长长的银蓝刀刃小腿，颜色、明暗，每一帧都照它，只改姿势。
> - **她没有脚**：小腿就是刀刃，刀尖就是脚，站在刀尖上。
> - **待机条已经做好**（`camille_idle.png`），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/camille_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体和腿的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；`parts/lol_parts_<动作>.png` 把两条腿涂成不同颜色（跑步要两腿交替）；长相照造型图。
> - 头是贴上去的（见下），**每帧不变形、不旋转**（只有死亡倒地的两帧可以和身体一起整体转 90 度），**不画倒立、不画背影**——英雄联盟里她有翻跟头的动作，我们不画翻转。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`，最好打成一个 zip。**生图做不到精确方块时，请自己按格子读回、清理，不要用代码重新拼色块**（上次的 46 格造型用代码拼出来的版本没被采用）。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/camille_palette.png`，或直接读 `design/camille_design_1x.png`）。**先把眼睛的青色 `#029FD9` 从色板里去掉**（吸附时会跑到核心、刀刃上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/camille_head_1x.png` 里不透明的格子：头发、发髻、脸、眼睛、嘴，到下巴为止；在 128×128 画布上的第 54–65 行、第 56–71 列）原样贴进每一帧头的位置（只平移）。下巴下面接**高立领**：立领每帧都要有（这件衣服本身有领子，不是脖子）。
5. 对位：每帧按 `camille_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），刀尖踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/camille_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行 | 每张动作图的第一张附图 |
| `design/camille_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/camille_head.png`、`_1x.png` | 要贴进每一帧的头（头发、发髻、脸、眼睛、嘴，到下巴） | 贴头 |
| `design/camille_palette.png` | 造型图的全部 49 色（暗到亮） | 色板 |
| `camille_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/camille_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体、手臂和刀刃腿的动作 |
| `parts/lol_parts_<动作>.png` | 同一帧按部位涂色（两条腿不同颜色） | 看清哪条腿在前 |
| `guide/camille_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `camille_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/camille_source_65.png` | 造型来源：你生成的 65 格青钢影 | 细节参考（比例以定稿为准） |
| `style/tfm2_style_ref.png`、`tfm2_style_ref_swordsman.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（头顶到刀尖 46 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 49 种颜色**，不加新颜色；明暗照定稿，不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **身体粗细照定稿**：手臂至少 2–3 格宽（加描边），黑手套的手要看得见；两把刀刃腿每帧都完整（上宽下尖，银蓝色），各部分之间有描边隔开，但身体、手臂、刀刃腿必须连成一个整体，不能有飘在空中的碎块。
- **头每帧都是造型图的头**（逐格一样，只平移；死亡倒地的帧可以整体转 90 度）；眼睛的青色 `#029FD9` 只用在眼睛上；胯上的核心用它自己的浅青色。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线，刀尖也在它上面。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变；两条刀刃腿交替（前 4 帧一步、后 4 帧另一步，中间刀刃交错）；上下起伏最多 2 格；首尾能无缝接上。
- 3/4 正面朝右，**不画背影、不画倒立**。**只画角色**：钩索和绳子、扫出去的刀光、力场、冲击波都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/camille_design.png`，第二张 `now/camille_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`（跑步和踢腿可以再附 `parts/lol_parts_<动作>.png`）。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `camille_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, hair, face, armour and pixel style exactly; do not redesign anything. Every frame must be the FIRST image's character in a new pose: the same proportions (a big head, a short torso, very wide hips, long leg blades), the same swept-back mint-silver hair with the bun, the same face with the cyan eyes, the navy high collar with the gold edge and the dark sapphire gem, the sky-blue bodice, the black gloves with gold wrist bands, the wide navy hips with gold circuit lines, the glowing core on the near hip, the gold knee joints and the two long silver-steel leg blades, the same shading. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms and the leg blades from it, but keep the FIRST image's proportions, and never draw her upside down (where the original flips or falls head first, keep the head upright and only move it lower; only the lying death frames turn body and head together, at most a quarter turn).
The character: Camille (an elegant woman whose lower legs are long steel BLADES - she has no feet and stands on the blade tips; she fights by kicking with them).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (46 squares from the top of the hair to the blade tips when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 49 colors of the FIRST image, no new colors: #03010F #0A0E21 #05054C #352503 #18202E #29241A #1B2445 #4D3907 #283357 #2F3F44 #724D08 #545321 #3C5153 #35416D #901D49 #515856 #8F680A #7E671D #3B4C80 #7D5346 #857131 #B48200 #3F65A4 #637D78 #2D7EB3 #B48C2C #CF9D03 #029FD9 #C6A119 #728D85 #4881CC #E9B203 #E0AF1A #859B95 #FAC20A #D18F67 #90AEA3 #0AE3FB #5CA2F1 #B0C8BF #E9B698 #A2BFE8 #F7C8A3 #C3D8CE #BACFF7 #FDD2B7 #DEEEE5 #D7E6FD #FBFBFB. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its highlights move with the pose; no dithering, no noise, no random specks added. Arms at least 2-3 squares wide with the outline, joined to the body, the black-gloved hands visible; the two leg blades whole in every frame (wide at the knee, pointed at the tip); no loose pieces.
The head (the hair with the bun, the face with the eyes and the mouth, down to the chin) is COPIED from the FIRST image in every frame, square for square, and only moved (only the lying death frames turn it with the body, at most a quarter turn); never redraw, squash or tilt it, or it flickers when the frames play. Under the chin the navy high collar stays in every frame. The cyan #029FD9 appears ONLY in the eyes (the hip core has its own lighter aqua).
Feet line: in every cell the lowest row of her blade tips is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down, because the game draws the health bar there (only the lying frames of the death may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in camille_cells.json). In the move loop her head keeps the same horizontal place relative to the standing point in every frame and the leg blades alternate.
3/4 FRONT view facing right, never her back, never upside down. Do not draw effects (the hook and its cable, slash arcs, the force field, shock waves) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 128x112 squares (1024x896 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible, the cyan only in the eyes, the collar under the chin, two whole leg blades in every frame, no feet, no loose pieces, nothing below the feet line, never her back or upside down, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `camille_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，3072×1792 | 第 97 行 | **已做好，不用画** |
| `camille_run.png`（移动） | 8 × 125 | — | 4 列 × 2 行，4096×1792 | 第 97 行 | `MOVE, 8 frames, one seamless loop of League's run (8 x 125 ms, the SECOND and THIRD images): Camille's poised, elegant walk on her leg blades, upright and a little haughty, her near hand resting on her hip as in the FIRST image, her far arm swinging lightly; the two leg blades ALTERNATE as in the THIRD image (frames 1-4 one stride, 5-8 the other: the near blade forward in one half, the far blade in the other, the blades crossing in between - the parts image shows the two legs in different colours); each planted blade tip touches the feet line; frames 4 and 8 the low point (the body at most 2 squares lower), the others upright; her head keeps the same place across the cell relative to the standing point in all 8 frames; frame 8 flows into frame 1.` |
| `camille_attack.png`（普攻（刀刃踢）） | 6 帧：60 60 60 70 80 90 | 第 3 帧（tick 7） | 3 列 × 2 行，3072×1792 | 第 97 行 | `BASIC ATTACK, 6 frames (League's attack1, a blade-leg kick): 1 she shifts her weight back, the far arm rising; 2 the wind-up: her near leg blade swung back and up behind her, the far arm raised high; 3 THE KICK (the hit lands here): the leg blade sweeps forward and down at the enemy in front of her, the blade's point leading, the body leaning into it; 4 the follow-through, the blade low in front; 5 she draws the leg back under her; 6 back to the idle stance. Slash trails are effects - do not draw them.` |
| `camille_attack_q.png`（Q 精准礼仪第一踢） | 6 帧：60 60 60 70 80 90 | 第 3 帧（tick 7） | 3 列 × 2 行，3072×1792 | 第 97 行 | `PRECISION PROTOCOL, the first empowered kick, 6 frames (League's spell1): 1 she draws one leg blade up in front of her body, knee bent; 2 the blade raised high, poised; 3 THE KICK (the hit lands here): a powerful straight kick forward at chest height, the blade fully extended toward the enemy, the body leaning back to balance; 4 the blade still extended, a little lower; 5 she brings the leg back; 6 back to the idle stance.` |
| `camille_attack_q2.png`（Q 精准礼仪第二踢（下劈）） | 6 帧：60 70 60 80 90 90 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×1792 | 第 97 行 | `PRECISION PROTOCOL, the second, charged kick, 6 frames (League's Spell1_2): 1 she lifts one leg blade straight up in front of her; 2 the blade pointing straight up above her head (an axe-kick wind-up), the body upright on the other blade; 3 THE AXE KICK (the hit lands here): the blade slammed down in front of her, the body bending forward; 4 the blade low in front, the other leg bent; 5 rising; 6 back to the idle stance. Never upside down; the slammed blade's tip reaches the feet line at most.` |
| `camille_skill.png`（W 战术横扫） | 8 帧：80 90 90 90 80 90 110 110 | 第 5 帧（tick 21） | 4 列 × 2 行，4096×1792 | 第 97 行 | `TACTICAL SWEEP, 8 frames (League's spell2): 1 she crouches low; 2 crouched deeper, gathering; 3 springing up, one leg drawn back; 4 in the air, the leg blade swinging round from behind; 5 THE SWEEP (the hit lands here): the leg blade extended straight forward and level at waist height, sweeping across in front of her; 6 the blade carried through to the far side; 7 landing low with one leg extended; 8 back to the idle stance. The sweep's arc is an effect - do not draw it. Rise at most 6 squares off the ground.` |
| `camille_skill2.png`（E 钩索（射钩）） | 5 帧：70 70 80 90 90 | 第 3 帧（tick 8） | 3 列 × 2 行，3072×1792，最后 1 格空 | 第 97 行 | `HOOKSHOT, 5 frames (League's spell3): 1 she crouches slightly; 2 she rises, turning her near hip toward the enemy; 3 THE SHOT (the hook leaves the glowing core on her near hip here): her near arm extended forward, the core bright (the hook and its cable are effects - do not draw them); 4 leaning forward as the cable pulls her, arms out; 5 leaning further forward, ready to dash.` |
| `camille_skill2_dash.png`（E 冲刺 + 落地） | 6 帧：60 60 60 70 80 100 | 第 4 帧（tick 11） | 3 列 × 2 行，3072×1792 | 第 97 行 | `WALL DIVE, 6 frames (League's Spell3_Dash2 + Spell3_Hit): 1 she flies forward, body level, the leading leg blade pointing ahead (a flying kick); 2 the same flight, the blade forward; 3 the dive downward, the blade leading toward the ground in front; 4 THE LANDING (the impact and the stun here): she lands in a deep crouch, one blade planted in front, the other leg stretched back; 5 still crouched, rising a little; 6 back to the idle stance. Keep the flight frames inside the cell, at most 4 squares above the ground.` |
| `camille_ult.png`（R 海克斯最后通牒（跳跃落地）） | 6 帧：80 80 80 80 100 110 | 第 4 帧（tick 14） | 3 列 × 2 行，3072×1792 | 第 97 行 | `THE HEXTECH ULTIMATUM, 6 frames (League's spell4): 1 she crouches; 2 she leaps up and forward (off the ground, legs tucked); 3 coming down from above, both leg blades pointing down, arms raised; 4 THE LANDING (the force field forms here): she lands in a crouch, one blade planted forward; 5 rising from the crouch, one leg extended to the side; 6 back to the idle stance. Keep every frame inside the cell (the leap at most 12 squares up).` |
| `camille_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，2048×896 | 第 97 行 | `HIT, 2 frames: 1 jolted back by a blow: her body and head pushed back 1-2 squares, the arms flung out a little (the head is the FIRST image's head, the eyes unchanged); 2 recovering toward the idle stance.` |
| `camille_dead.png`（死亡） | 8 帧：100 100 110 120 120 130 150 400 | — | 4 列 × 2 行，4096×1792 | 第 97 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck, she rocks back, arms out; 2 reeling, her head thrown back; 3 staggering on her blades; 4 her knees giving way; 5 sinking forward; 6 falling onto her side; 7 lying on the ground (body and head turned together, at most a quarter turn); 8 lying still. Frames 7-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），明暗照定稿，没有自己加的碎点；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移；死亡倒地的帧最多整体转 90 度），两只眼睛都在，下巴下面有立领；
- [ ] 眼睛的青色 `#029FD9` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 两把刀刃腿每帧都完整，没有脚；手臂和手看得见；没有飘着的碎块；
- [ ] 没有背影、没有倒立；脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，两条刀刃腿交替，上下起伏不超过 2 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `camille_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、青色只在眼睛上、连通块、手臂粗细、每帧面积和待机比、跑步两腿交替），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`camille_cells.json` 用包里这份，`camille_idle.png` 用包里已做好的那张。
- `import_native.py --hero camille`：ORDER 待机一张图 + BOB 呼吸，EYES = `#029FD9`，COMPLETE 补描边，NECK 检查立领每帧在下巴下同一行。
- 按出手帧核对技能数据的时机（普攻 tick 7、Q 第一踢 tick 7、Q 第二踢 tick 8、W tick 21、E 射钩 tick 8、E 落地 tick 11、R 落地 tick 14），重跑模拟，做预览 GIF。
