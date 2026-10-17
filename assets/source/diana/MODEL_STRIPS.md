# 戴安娜：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：用户选了 A**。这是你在游戏尺寸画的 A：Claude 按原稿自己的格子读回像素（没有平均、没有模糊），压到 26 色，在脸以外删行删列到头顶到脚底 40 行，脸原样保留，眼睛的三种颜色只用在眼睛上：`design/diana_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799）。**造型图就是标准**，颜色、形状、头、脸、弯刀一律照它。
> - **待机条已经做好**（`diana_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/diana_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。
> - **直接在游戏尺寸画**：造型图里的一格就是游戏里的一个像素，不要画得更细再缩小。交回的图每个像素都是严格对齐的 8×8 纯色块。
> - **这次不要贴头，也不要擦掉头周围的任何像素**：每一帧整个人（包括头、脸、头发、马尾）都照造型图直接画出来。之前的英雄贴头时切出了透明方框（贝蕾亚），导出时擦掉了脖子（薇恩），头和身体看起来是分开的。Claude 收到后会把造型图的脸对准你画的脸补上。
> - **交回时一起附上**：每张动作条的**生图原稿**（对齐网格之前的那张）；`manifest.json` 里每帧的格子矩形、站位点 pivot、不透明范围 bbox，以及**眼睛标记 eye_mark**（这一帧近处那只眼睛左上角那格的坐标，格子坐标）；`HANDOFF.md`（每张用了哪条提示词、哪里没做到）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose；跑步再加 `legs/diana_legs_run.png`）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/diana_palette.png`，或直接读 `design/diana_design_1x.png`）。**眼睛的三种颜色 #F9F7FB, #7211B0, #A950D9 只允许出现在两只眼睛上**：眼睛以外吸到这三种颜色的像素，改用它旁边最近的其他颜色。
4. 对位：每帧按 `diana_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
5. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/diana_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/diana_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板 |
| `design/diana_palette.png` | 造型图的全部 26 色（暗到亮） | 色板 |
| `diana_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/diana_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置（镜像渲染：弯刀在哪只手以造型图为准） | 第三张附图：身体的动作 |
| `legs/diana_legs_run.png` | 跑步 8 帧，两条腿分开上色（一条橙、一条蓝，其余灰），8 倍，红线是脚底线 | 跑步的第四张附图：哪条腿踩地、哪帧交叉 |
| `guide/diana_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `diana_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/diana_picture.png` | 造型所依据的原图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（43 格，含高出头顶的刀尖），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 26 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头和脸每帧都照造型图画**：头发、两条青绿发带、马尾、额头的月亮圆盘、两只眼睛（近处白+紫 2 格宽，远处紫色，同一行）的形状和格子都和造型图一样，只随身体平移或整体倾斜。**不要把造型图的头剪下来贴上去，也不要擦掉头周围的像素**：头连着脖子、肩膀和马尾一起画。
- 眼睛的三种颜色 #F9F7FB, #7211B0, #A950D9 **只用在眼睛上**。
- **弯刀每帧都在，在右手**：待机时是画面左边那只手。`pose/` 是镜像渲染，个别帧弯刀会跑到另一只手，**以造型图的手为准**（之前阿卡丽就是照了参考图拿错了手，重画了一轮）。刀柄在拳头里，刀不离手、不挡脸。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），弯刀、垂甲、披风都不能低于它。英雄联盟里跑步和站立时刀尖会垂到地上，**这里把刀拿高一点**。只有死亡倒地的帧可以低于红线，最多 2 格。
- **跑步两条腿要交替**（之前薇恩 8 帧都画成同一条腿在前，像单脚跳，重画了一轮）：按 `legs/diana_legs_run.png` 和下面的表，踩地的腿每半圈换一次，中间两帧膝盖在身体下面交叉；头的横向位置每帧不变，上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，不画背影（死亡最后躺下的帧除外）。**只画角色**：新月、法球、月亮、拉扯、刀光这些都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里已经没有名字）。

## 跑步：每帧哪条腿踩地

| 帧 | 踩地的腿（`legs/diana_legs_run.png` 的颜色） | 两脚最低点相差（格） |
|---|---|---|
| 1 | 蓝色腿 | 2.9 |
| 2 | 蓝色腿 | 9.0 |
| 3 | 蓝色腿 | 10.0 |
| 4 | 蓝色腿 | 6.0 |
| 5 | 两腿交叉换位 | 0.9 |
| 6 | 橙色腿 | 8.2 |
| 7 | 橙色腿 | 8.8 |
| 8 | 橙色腿 | 4.6 |

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/diana_design.png`，第二张 `now/diana_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`（跑步再附第四张 `legs/diana_legs_run.png`）。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `diana_<动作>.png`。

```text
Three attached images (four for the move). FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, eyes, hair, crescent blade and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it (it is a mirrored render: the blade stays in the FIRST image's hand). FOURTH (move only): the same run with its two legs painted orange and blue - copy which leg is planted in each frame.
The character: a slim chibi moon warrior with pale skin, platinum-blonde hair combed back with two teal bands and a long ponytail, a small glowing lavender moon disc on the forehead, violet eyes; moonsilver armour with a lavender sheen (crescent-spiked pauldrons, a crescent collar piece), a dark navy bodysuit, a gold crescent belt buckle, dark teal-green hip tassets with gold-green edges, a dark purple mantle behind the shoulders, gold knee guards over silver greaves, dark navy heeled boots; a long pale cyan-silver crescent blade in her right hand.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (43 squares tall from the blade's tip to the soles when standing, 40 from the top of the hair), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. Draw at this game size directly - one square of the FIRST image is one game pixel; never draw finer and shrink.
Pixel rules (most important): ONLY the 26 colors of the FIRST image, no new colors: #0A0412 #0C0516 #22233C #264648 #1F5057 #492B5B #333B63 #554743 #505945 #505169 #865744 #7211B0 #60637E #818768 #A7804A #9676AC #A950D9 #7BB2B9 #B9B690 #C7B8A2 #B8BFC7 #F2BA94 #F3D98D #F2E6CF #D0F6EE #F9F7FB. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (hair, teal bands, ponytail, moon disc, face, eyes) is drawn like the FIRST image's in every frame - the same shapes and squares, only moved or tilted with the body - and joined to the neck, shoulders and ponytail like any other part. Do NOT cut the head out of the FIRST image and paste it, and do NOT erase anything around the head. The crescent blade is in every frame, in her RIGHT hand - the hand on the image-left in the idle; where the THIRD image (a mirrored render) shows it in the other hand, keep the FIRST image's hand. It never floats free of the fist. The ponytail falls behind her head and the purple mantle hangs from her shoulders. The eyes are exactly the FIRST image's: the near eye (left, she faces right) white + violet, 2 squares wide, the far eye violet, on the same rows; their three colours #F9F7FB, #7211B0 and #A950D9 appear ONLY in the eyes. The small lavender moon disc on the forehead as in the FIRST image.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the blade, not the tassets, not the mantle - because the game draws the health bar there (where League's blade dips to the floor, hold it higher; a fall may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in diana_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame, and her legs alternate as in the FOURTH image.
3/4 FRONT view facing right, never her back (except a frame lying on the ground). Do not draw effects (the crescent, orbs, moon, slashes, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head and face drawn like the FIRST image in every frame and joined to the body, both eyes visible and level, the eye colors only in the eyes, the blade in the right hand, nothing below the feet line, the frames in the same cells as the SECOND image; for the move, the planted leg changing as in the FOURTH image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `diana_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 79 行 | **已做好，不用画** |
| `diana_run.png` | 8 × 125 | — | 4 列 × 2 行，3072×1536 | 第 79 行 | `MOVE, 8 frames, one seamless loop of League's run (1 s cycle, 8 x 125 ms, the SECOND and THIRD images): she runs leaning a little forward with long strides, the ponytail and the purple mantle streaming out behind her (left); the crescent blade trails behind her in her right hand at hip height - hold it a little higher than the SECOND image, its lower tip never below the soles. Her LEGS ALTERNATE exactly as in legs/diana_legs_run.png (one leg orange, the other blue; the table below says which leg is planted in each frame): the planted leg changes every half cycle and the knees pass each other in between - never the same legs in all frames. Her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `diana_attack.png` | 7 帧：60 60 60 70 70 80 80 | 第 4 帧 | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 79 行 | `BASIC ATTACK (League's first attack), 7 frames: 1 a low crouched wind-up, the blade held low in front; 2-3 rising; 4 the strike (the hit lands here): an upward slash to the right, the blade sweeping up; 5 the follow-through, the blade high overhead; 6-7 back toward the idle stance. Do not draw a slash effect.` |
| `diana_attack_p.png` | 7 帧：60 60 60 60 70 80 90 | 第 5 帧 | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 79 行 | `CLEAVE (every third attack; League's third attack), 7 frames: 1-3 she swings the blade up behind her head, the crescent lying level over her shoulders; 4 she crouches into the swing; 5 the strike (the hit lands here): a long level sweep to the right, the blade stretched out low in front of her; 6 held; 7 back toward the idle stance. Do not draw the crescent arc - it is an effect.` |
| `diana_skill.png` | 7 帧：60 60 60 70 80 90 100 | 第 4 帧 | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 79 行 | `CRESCENT STRIKE, 7 frames: 1 she draws the blade back low; 2-3 swinging it up; 4 the release (the crescent bolt leaves here): the blade whipped up and forward over her head, the free arm stretched forward; 5-6 held; 7 back toward the idle stance. Do not draw the bolt.` |
| `diana_skill2.png` | 5 帧：60 80 80 80 80 | — | 3 列 × 2 行，2304×1536，最后 1 格空 | 第 79 行 | `LUNAR RUSH, a dash, 5 frames: 1 she crouches forward; 2-4 flying forward almost level, the body stretched out to the right, the blade trailing behind her, the ponytail streaming back, the feet off the ground; 5 landing back toward the idle stance. The game moves her across the ground; draw the pose only.` |
| `diana_skill2_w.png` | 7 帧：60 60 60 70 70 80 90 | — | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 79 行 | `PALE CASCADE, 7 frames: 1 she opens her arms; 2-3 a quick hop and turn, the blade swinging round her at waist height; 4-5 arms spread, the blade out to the right; 6 landing; 7 back toward the idle stance. The orbs round her are an effect - do not draw them.` |
| `diana_ult.png` | 8 帧：60 60 70 70 80 100 110 110 | 第 5 帧 | 4 列 × 2 行，3072×1536 | 第 79 行 | `MOONFALL, 8 frames: 1 she raises the blade; 2-3 a leap straight up, the blade held high; 4-5 landing in a low crouch, the blade driven down in front of her (the pull happens here); 6-7 holding the crouch; 8 rising back toward the idle stance. The falling moon and the pull are effects - do not draw them.` |
| `diana_hit.png` | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 79 行 | `HIT, 2 frames: 1 jolted back by a blow, the body leaning back; 2 recovering toward the idle stance.` |
| `diana_dead.png` | 8 帧：100 100 120 120 120 150 150 500 | — | 4 列 × 2 行，3072×1536 | 第 79 行 | `DEATH, 8 frames, going down in ONE movement (each frame lower than the one before), as in the THIRD image: 1 struck; 2 thrown back; 3 falling backward; 4-5 landing on her back; 6-7 lying on the ground; 8 lying still on the ground line, the blade beside her. Frames 4-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头、脸、马尾都是画出来的、和身体连着，没有贴图的方框、没有被擦掉的脖子；
- [ ] 两只眼睛都在、同一行；眼睛的三种颜色在眼睛以外 0 个像素；
- [ ] 弯刀每帧都在右手（待机时画面左边那只手），不离手、不挡脸；
- [ ] 脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 跑步：踩地的腿按上面的表交替，膝盖交叉的帧在表里写的位置；头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；
- [ ] 附上每张的生图原稿，`manifest.json` 里每帧的格子矩形、站位点、bbox 和 eye_mark 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `diana_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛颜色只在眼睛、每帧面积和待机比、跑步的腿有没有交替），不在网格上的按生图原稿的格子重新取样（`.claude/skills/tfm2-hero-mod/scripts/regrid.py` 的做法）。
- 按 eye_mark 在原稿自己画的脸上贴造型图的脸（眼睛、额头月亮、脸颊，不贴头发、不清任何像素，`tools/art/export_vayne.py` 的做法）；然后一圈描边（`tools/art/tidy_codex18.py` 的 `one_outline`）。
- 放进 `assets/source/native/`，`diana_cells.json` 用包里这份，`diana_idle.png` 用包里已做好的那张；`import_native.py --hero diana`：ORDER 待机一张图 + BOB 呼吸（缝在小腿的直段上），EYES = 眼睛的白 `#F9F7FB`（刀尖是每帧的最高处，按眼睛对齐待机和移动）。
- 按出手帧改技能数据的时机（普攻第 4 帧、第三下顺劈第 5 帧、Q 第 4 帧、R 第 5 帧），重跑模拟，量特效挂点和头像截取点，做预览 GIF。
