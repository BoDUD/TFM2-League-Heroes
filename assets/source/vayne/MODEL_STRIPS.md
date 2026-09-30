# 薇恩：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定：用户选了 B（缩到 48 行）**。这是你第二版在游戏尺寸画的 B：Claude 按原稿自己的格子读回像素（没有平均、没有模糊），在脸以外删了 5 行 4 列，脸原样保留（补回了被清杂点误删的嘴），两片镜片换成只在镜片上用的两种红：`design/vayne_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799）。**造型图就是标准**，颜色、形状、头、脸、两把弩、披风一律照它。
> - **待机条已经做好**（`vayne_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 9 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/vayne_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。英雄联盟的模型是金色的弩，**我们的造型是用户图里的银色弩和红披风**，每帧都照造型图画。
> - 这次和造型一样，**直接在游戏尺寸画**：造型图里的一格就是游戏里的一个像素，不要画得更细再缩小。交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/vayne_palette.png`，或直接读 `design/vayne_design_1x.png`）。**先把两个镜片颜色 `#F8303C`、`#B0102A` 从色板里去掉**（它们和披风、宝石的红很近，一吸附就会跑到身上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/vayne_head_1x.png`：只有头发、马尾、发夹、脸、墨镜、嘴和它们的描边，背后的大弩和红立领已去掉；在 128×128 画布上的范围 x 54–73、y 52–69）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；翻滚中低头的帧、死亡倒地的帧可以不贴）。**只贴头的像素，不要贴整个矩形**（上一个英雄贴了整个矩形，头周围被切出一个透明方框）。这样每帧的脸都和造型图一模一样。
5. 对位：每帧按 `vayne_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/vayne_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/vayne_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/vayne_palette.png` | 造型图的全部 26 色（暗到亮） | 色板 |
| `design/vayne_head.png` / `_1x.png` | 定稿的头（只有头的像素） | 贴头 |
| `vayne_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/vayne_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/vayne_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `vayne_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/vayne_picture.png` | 用户给的原图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（48 格，含马尾和背后的弩），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 26 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（头发、马尾、脸、墨镜、嘴逐格一样），只平移或整体倾斜；两片镜片同一行，亮红 `#F8303C` 和暗红 `#B0102A` 只用在镜片上。
- **两把弩每帧都在**：银色腕弩绑在右前臂上（待机时是画面左边那只手臂）；大弩背在背后，只有恶魔审判和终极时刻双手端着。弩和披风跟着身体动，不能飘开，不能挡脸。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面），披风、弩都不能低于它。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变，只动腿、手臂、披风、马尾；上下起伏最多 1 格；首尾能无缝接上。
- **翻滚**：英雄联盟是整个前空翻，这里头最多转四分之一，不画倒立；往后翻滚（`skill_back`）时她一直面朝右。
- 3/4 正面朝右，不画背影（死亡最后趴下的帧除外）。**只画角色**：弩箭、重箭、击退的冲击、终极时刻的光这些都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述（下面的提示词里已经没有名字）。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/vayne_design.png`，第二张 `now/vayne_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `vayne_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, glasses, both crossbows, cape and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look (and NOT its gold crossbow: our design's crossbows are silver). THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it.
The character: a slim chibi crossbow huntress with pale skin, long black-violet hair in a high ponytail with a silver-and-red clasp, red sunglasses, dark-red lips, a tall collar black outside and crimson inside, a black-navy bodysuit with silver armour pieces and brown straps, a torn crimson cape, black heeled boots with silver toes; a silver wrist crossbow on her right forearm and a big silver crossbow with a brown stock on her back.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (48 squares tall from the ponytail to the soles when standing), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency. Draw at this game size directly - one square of the FIRST image is one game pixel; never draw finer and shrink.
Pixel rules (most important): ONLY the 26 colors of the FIRST image, no new colors: #0B0410 #0D0513 #11071A #240611 #1D1128 #4D0315 #1F1C2F #2D272B #65061A #2A263A #301E3F #442723 #2F2E45 #920115 #8F0B24 #633C35 #B0102A #565156 #CD062B #F8303C #807B7A #BE9282 #A29E9C #C0BCB6 #D0CBC3 #FBD7BF. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (hair, ponytail, clasp, face, glasses, mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. Paste only the head's own pixels, never its whole rectangle. Both crossbows are in every frame: the spiky silver wrist crossbow strapped on her right forearm (the arm on the image-left in the idle), and the big silver crossbow with the brown stock on her back - except in CONDEMN and FINAL HOUR, where she holds it in both hands; neither floats free of her. The torn red cape hangs from her shoulders and flows behind her. Her eyes are behind the FIRST image's red glasses: the two lenses on the same rows, in the lens red #F8303C and its shade #B0102A; those two colours appear ONLY in the lenses. The mouth is the FIRST image's one dark-red square.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the cape, not a crossbow - because the game draws the health bar there (a fall may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in vayne_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame.
3/4 FRONT view facing right, never her back (except a frame lying face down); in a roll her head turns at most a quarter from upright. Do not draw effects (bolts, impacts, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both lenses visible and level, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `vayne_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `vayne_run.png` | 8 × 125 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (1 s cycle, 8 x 125 ms, the SECOND and THIRD images): she runs upright with long strides, the red cape streaming out behind her (left), the ponytail bouncing, the right forearm with the wrist crossbow swinging a little at her side, the big crossbow staying on her back (frames 1-4 one stride, 5-8 the other); her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); frame 8 flows into frame 1.` |
| `vayne_attack.png` | 6 帧：60 60 70 70 80 90 | 第 3 帧 | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, 6 frames: 1 she raises her right forearm with the wrist crossbow to shoulder height, aiming right; 2 aiming, the arm straight out to the right; 3 the release (the bolt leaves here): the crossbow snaps, a small recoil of the arm; 4 held; 5-6 back toward the idle stance. Do not draw the bolt.` |
| `vayne_attack_q.png` | 6 帧：60 60 70 70 80 90 | 第 3 帧 | 3 列 × 2 行，2304×1536 | 第 81 行 | `TUMBLE SHOT (the stronger attack right after a roll), 6 frames: she fires from a low crouch as in the THIRD image: 1 crouched low, the crossbow arm coming up; 2 aiming forward to the right, still crouched; 3 the release (the heavy silver bolt leaves here): a strong recoil; 4 held; 5-6 rising back toward the idle stance. Do not draw the bolt.` |
| `vayne_skill.png` | 7 帧：50 50 50 60 60 70 80 | — | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `TUMBLE, a quick roll forward to the right, 7 frames: 1 she dips forward; 2-4 the roll: tucked into a ball, rolling low along the ground, the cape wrapping round her (League does a full forward flip here - keep her head never more than a quarter turn from upright, no upside-down frames); 5 landing in a low crouch; 6 rising; 7 back toward the idle stance. The feet leave the ground only in frames 2-4.` |
| `vayne_skill_back.png` | 7 帧：50 50 50 60 60 70 80 | — | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `TUMBLE BACK, a quick roll backward (to the left) away from an enemy, 7 frames: she keeps FACING RIGHT the whole time: 1 she crouches; 2-4 she rolls backward, tucked, low along the ground (her head at most a quarter turn from upright, no upside-down frames); 5 landing in a low crouch; 6 rising; 7 back toward the idle stance. The SECOND and THIRD images are League's forward roll played backward: copy the poses, not the direction of travel.` |
| `vayne_skill2.png` | 7 帧：60 70 70 70 80 80 90 | 第 4 帧 | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 81 行 | `CONDEMN, 7 frames: 1 she reaches over her shoulder for the big crossbow on her back; 2 swings it down in front of her; 3 aims it forward to the right at chest height with both hands; 4 the release (the heavy bolt leaves here): the big crossbow fires with a strong recoil, her body pushed back a little; 5 held; 6 swinging it back over her shoulder; 7 back toward the idle stance, the big crossbow on her back again. Do not draw the bolt.` |
| `vayne_ult.png` | 6 帧：70 70 90 120 120 100 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | `FINAL HOUR, 6 frames: 1 she reaches back; 2 draws the big crossbow over her shoulder; 3 holds it forward at the ready with both hands, a proud upright stance (League's Final Hour stance, the THIRD image); 4 held, the cape flaring; 5 still holding; 6 back toward the idle stance, the crossbow on her back again. The glow round her is an effect - do not draw it.` |
| `vayne_hit.png` | 2 × 100 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, the body leaning back; 2 recovering toward the idle stance. The glasses stay on.` |
| `vayne_dead.png` | 8 帧：100 100 100 100 120 150 150 400 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames, going down in ONE movement (each frame lower than the one before), as in the THIRD image: 1 struck, head thrown back; 2 staggering; 3 falling to her knees; 4 slumping forward; 5 falling onto her side; 6-7 lying on the ground; 8 lying still on the ground line, the crossbows beside her. Frames 4-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两片镜片都在、同一行；
- [ ] `#F8303C`、`#B0102A` 只出现在镜片上：头部范围以外 0 个像素；
- [ ] 两把弩每帧都在（大弩只在恶魔审判和终极时刻拿在手上），不挡脸；
- [ ] 脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 翻滚的头最多转四分之一，没有倒立的帧；往后翻滚时一直面朝右；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `vayne_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、镜片红只在镜片、每帧面积和待机比），不在网格上的按格子重新取样（`.claude/skills/tfm2-hero-mod/scripts/regrid.py` 的做法）；镜片不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`vayne_cells.json` 用包里这份，`vayne_idle.png` 用包里已做好的那张。
- `import_native.py --hero vayne`：ORDER 待机一张图 + BOB 呼吸，EYES = `#F8303C`（按镜片对齐待机和移动）。
- 按出手帧改技能数据的时机（普攻、强化普攻、恶魔审判的出手 tick，翻滚和终极时刻的动作长度），重跑模拟，量特效挂点和头像截取点，做预览 GIF。
