# 锐雯：按定稿造型画 10 条动作（给 Codex，第二步）

> **这一轮画 10 张动作图**：移动、普攻、Q 第一段、Q 第二段、Q 第三段（跃起砸地）、E 冲刺接 W 怒吼、R 开启、R 疾风斩、受击、死亡。待机不用画（`riven_idle.png` 已经用造型图拼好）。
> - 造型图 `riven_native.png` 是用户确认的锐雯（由用户给的原图按原图自己的像素网格取色、删行删列缩到游戏尺寸，一圈描边，两只眼睛一样大、在同一行）。**每一帧都照它画**：同样的大小、颜色、头、衣服、断剑和像素风格。
> - 帧数、每帧时长、出手帧照下面的表；每帧在格子里的位置照 `riven_now_<动作>.png`（它和 `lol_pose_<动作>.png` 是同一批英雄联盟原版动作渲染，旋转斩里背对镜头的帧已经转成看得到脸）。
> - 交回时附 `HANDOFF.md`（每张用了哪段提示词、没做到的地方）和 `manifest.json`（文件名、尺寸、每帧格子、站位点、不透明区域、眼睛颜色的中心）。

## 附图

| 文件 | 内容 | 用法 |
|---|---|---|
| `riven_native.png` | 确认的造型，8 倍，1024×1024，脚底第 99 行、站位点 (64, 88) | **第一张图**：颜色、形状、头、断剑、像素风格全照它 |
| `riven_now_<动作>.png` | 英雄联盟原版动作按造型身高渲染的游戏尺寸参考条，8 倍，每格 96×96 个方块 | **第二张图**：帧数、每帧的时机、在格子里的位置（它是 3D 渲染的平均色，很糊，不要照它的样子） |
| `lol_pose_<动作>.png` | 同一帧的英雄联盟原版动作渲染，同样的格子、同样的位置 | **第三张图**：身体的动作照它（身材别照它：它比造型瘦得多） |
| `riven_guide_<动作>.png` | 每帧的站位点（蓝十字）和脚底线（红线），红线以下的淡红区不能有像素 | 对位用，不要画进图里 |
| `riven_cells.json` | 每帧的站位点（格子里第几列、第几行）和帧时长 | 整理对位 |
| `riven_idle.png` | 待机条（已拼好，不用画） | 只作参考：每个动作从这个站姿开始、回到这个站姿结束 |
| `riven_design_1x.png` / `riven_palette.png` | 造型图原尺寸 / 它的全部颜色 | 整理时吸色板 |
| `tfm2_style_ref_swordsman.png` | 团战经理2 原版英雄 | 像素大小和干净程度 |

## 规则

- **只用造型图的 27 种颜色**：#1C0903 #1E1319 #24181F #2D1D1C #272720 #163A22 #293828 #3F2A24 #493328 #593C2C #434A46 #68432C #426E3B #7E4F30 #3E8E48 #996B3D #A8643F #867469 #CB8053 #C79860 #A89588 #E39F6B #BBAA9C #D0BFB0 #FBC697 #F6EADB #FFFFFF。不加新颜色。
- **头每帧照造型图逐格复制**：轮廓、白发（包括脑后翘起的一小撮马尾）、两只眼睛都和造型图一样，只随动作整体移动（跳起、倒地时可以倾斜），不重新画；两只眼睛一样大（各 2×2）、同一行，不连成横杠；眼睛的三种颜色 `#FFFFFF`（左上高光）、`#163A22`（右上深绿）、`#3E8E48`（下排绿）只用在眼睛上；不画嘴。
- **断剑**：造型图里那把又宽又厚、断口锯齿状、带绿色符文的断剑，每帧同样大小，握在画面右边那只手里；不要画成细剑、完整的剑或发光的剑（开大时的绿光是特效，另外做）。
- **身材照造型图**：粗手臂、手套、粗腿、靴子、宽站姿；第三张图的 3D 模型很瘦，只照它的动作，不照它的胖瘦（卢锡安那次跑步照着参考图画瘦了，整理时只好加宽）。
- **只有一圈描边**：剪影外一圈 1 格宽的近黑描边，里面的边缘和褶皱用材质自己最暗的色阶，不要第二圈黑（莫甘娜那次多描了一圈，放技能时人就变大一圈）。
- **干净**：大块纯色，每种材质 2–3 个色阶；不要抖动、渐变、噪点、孤立的杂色方块。
- **站姿**：每个动作从造型图的站姿开始、回到它结束——断剑在画面右边那只手里，剑尖朝右下垂在身旁（剑尖在脚底线以上）。
- **脚底线**：每格里鞋底最低一行是那一帧站位点下方第 11 行（`riven_cells.json`），红线以下什么都不能有（游戏在脚下画血条），剑尖也不行；只有死亡倒地的帧可以低于红线，最多 2 格。
- 3/4 正面朝右，**不画背影**：旋转斩的帧也要看得到脸；手臂和剑从肩膀、胸口伸出，不挡脸。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、参考线。

## 提示词

10 张的提示词都以同一段开头，每张只换最后的动作说明和排版。

```text
Three attached images. FIRST: the approved pixel-art design of this character at 8x (every pixel an 8x8 block) - copy her colors, shapes, head, clothes, broken sword and pixel style exactly, the head the same size in every frame. SECOND: a game-size reference of the animation at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the hit, the recovery) and where she stands in her cell, but NOT its look (it is a blurry average of a 3D render). THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it, but NOT its thin build: her body is as stocky as in the FIRST image.
Task: draw every frame as clean pixel art in the style of the FIRST image, at EXACTLY the same pixel size (about 46 pixels from the top of her hair tuft to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): only the colors of the FIRST image, no new ones; big flat areas, 2-3 shades per material as in the FIRST image; no dithering, no gradients, no noise, no lone square of a different color inside an area; ONE 1-square near-black outline around the silhouette, and inside it the material's own darkest shade - never a second ring of black.
Head and face: copy the head of the FIRST image into every frame square for square - the same outline, white hair with the small tuft at the back, and both eyes - only moved (or tilted in a leap or the fall), never redrawn: each eye 2x2 on one row (#FFFFFF top-left, #163A22 top-right, #3E8E48 bottom row), never merged into a bar; these three eye colors used nowhere else; no mouth. The broken sword is the FIRST image's: huge, broad, with a jagged snapped-off end and green runes, the same size in every frame, in the hand on the right of the image. Arms and the sword come from the shoulders and the chest and never cover the face. 3/4 FRONT view facing right, never her back - also in the spinning frames.
Stance: every animation starts and ends in the FIRST image's stance - the broken sword held low at her side in the hand on the right of the image, its tip pointing down to the right, above the feet line.
Feet line: in every cell the lowest row of her soles is the row 11 squares below that frame's standing point (riven_cells.json); NOTHING below it - not the sword tip, not the boots - because the game draws the health bar there. Her place across the cell follows the SECOND image.
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]; frame N in the same cell as in the SECOND image. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| 文件 | 帧 × 毫秒 | 排版 | 出手帧 | `[animation]` |
|---|---|---|---|---|
| `riven_run.png`（移动） | 8 × 121 | 4 列 × 2 行，3072×1536 | — | `Animation: MOVE, 8 frames, one seamless loop of League's run (0.97 s a cycle, 8 x 121 ms, as in the THIRD image): she runs leaning a little forward, the broken sword held low and forward in the hand on the right of the image (its tip above the feet line), the other arm swinging; frames 1-4 one stride, 5-8 the other; the head keeps its place across the cell (at most 1 square up or down) and faces right as in the FIRST image; the feet touch the ground line in the stride frames; frame 8 flows into frame 1.` |
| `riven_attack.png`（普攻） | 6 帧：60 60 70 70 80 90 | 3 列 × 2 行，2304×1536 | 第 4 帧（tick 11） | `Animation: BASIC ATTACK, 6 frames, one heavy chop with the broken sword: 1 leaving her stance, the sword coming up; 2 the sword raised high behind her head; 3 the chop coming down in front of her; 4 THE HIT: the blade low in front of her at the end of the chop, its tip above the feet line; 5 recovering; 6 back to her stance.` |
| `riven_skill.png`（Q 第一段） | 7 帧：50 50 60 60 70 80 90 | 4 列 × 2 行，最后 1 格空，3072×1536 | 第 5 帧（tick 13） | `Animation: BROKEN WINGS, first strike, 7 frames: 1 she crouches to spring; 2-3 a short hop forward, whirling the blade round her in a flat circle - show her face in every frame, never her back; 4 landing; 5 THE HIT: a forward lunge, the blade thrust out to the right at chest height; 6 holding the lunge; 7 back to her stance.` |
| `riven_q2.png`（Q 第二段） | 7 帧：50 50 60 60 70 80 90 | 4 列 × 2 行，最后 1 格空，3072×1536 | 第 5 帧（tick 13） | `Animation: BROKEN WINGS, second strike, 7 frames: 1 she crouches; 2-3 a short hop forward, spinning the blade round her (face visible, never her back); 4 landing low; 5 THE HIT: a low backhand slash, the blade sweeping from low left to the right; 6 follow-through; 7 back to her stance.` |
| `riven_q3.png`（Q 第三段·跃起砸地） | 7 帧：50 60 80 60 70 90 100 | 4 列 × 2 行，最后 1 格空，3072×1536 | 第 5 帧（tick 15） | `Animation: BROKEN WINGS, third strike (the leap), 7 frames: 1 a deep crouch; 2 she leaps up, the blade raised over her head with both hands; 3 at the top of the leap (held a little longer); 4 coming down, the blade still overhead; 5 THE SLAM: she lands on the feet line and drives the blade down in front of her (the ground crack is an effect - do not draw it); 6 holding the slam; 7 back to her stance. No flips, no upside-down frames.` |
| `riven_skill2.png`（E 冲刺 + W 怒吼） | 8 帧：50 50 50 60 70 80 90 100 | 4 列 × 2 行，3072×1536 | 第 5 帧（tick 13） | `Animation: VALOR then KI BURST, 8 frames: 1 she drops low; 2-3 a quick low dash forward to the right, the blade held back along her body, the shoulder with the bronze pauldron leading (off the ground at most 2 squares, never below the feet line); 4 stopping and rising; 5 THE BURST: she stands up straight and thrusts the blade straight up over her head, shouting (the green burst ring and the shield glow are effects); 6 holding it; 7 lowering; 8 back to her stance.` |
| `riven_ult.png`（R 开启） | 6 帧：60 70 80 90 100 110 | 3 列 × 2 行，2304×1536 | 第 3 帧（tick 8） | `Animation: BLADE OF THE EXILE, 6 frames: 1 she lifts the broken blade; 2 she holds it level above her head with both hands; 3 THE POWER: the blade held high, her body tensed (the green energy that reforms the blade is an effect); 4-5 bringing it down in front of her, gripping it firmly; 6 back to her stance.` |
| `riven_r_slash.png`（R 疾风斩） | 6 帧：60 70 70 80 90 110 | 3 列 × 2 行，2304×1536 | 第 3 帧（tick 8） | `Animation: WIND SLASH, 6 frames: 1 she draws the blade back over her shoulder; 2 a big wind-up, the blade high behind her; 3 THE SLASH: a wide horizontal sweep out to the right, the blade fully extended at chest height (the green wind wave is an effect); 4 follow-through; 5 recovering; 6 back to her stance.` |
| `riven_hit.png`（受击） | 2 × 100 | 2 列 × 1 行，1536×768 | — | `Animation: HIT, 2 frames: 1 jolted back by a blow, the blade dipping; 2 recovering toward her stance.` |
| `riven_dead.png`（死亡） | 8 帧：100 100 100 120 120 150 150 400 | 4 列 × 2 行，3072×1536 | — | `Animation: DEATH, 8 frames: 1 struck, she staggers; 2 she drops to one knee, leaning on the blade; 3 kneeling; 4-5 falling onto her side; 6-7 lying on the ground line, the broken blade beside her; 8 lying still. Only here the body may reach 2 squares below the feet line.` |

`[grid]` 和 `[size]` 按上表每行的排版填（例如 `4 columns x 2 rows, the last cell empty` 和 `3072x1536 px`）。

## 交回前自查

- 每张图的格子数、每格大小、每帧位置和 `riven_now_<动作>.png` 一样；每个像素都是对齐的 8×8 纯色块；透明度只有 0 和 255。
- 只用造型图的颜色；眼睛三色只出现在眼睛上；每帧两只眼睛各 2×2、同一行。
- 头和造型图逐格一样（只平移/倾斜）；断剑每帧同样大小；不露背影。
- 脚底线以下没有像素（死亡倒地帧最多 2 格）；每条动作的人和待机一样大（整理后我们会比较每帧面积，放大缩小都要改）。
