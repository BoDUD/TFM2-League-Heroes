# 阿卡丽重做：按新定稿画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定，不许再改。** 用户选的是你按 main 上 18 位英雄那套做法画的 A，Claude 整行整列删到 40 格（用户选的 "A40"）：`design/akali_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799；头顶到脚底 37 格，含马尾 40 格，18 色）。**造型图就是标准**：颜色、形状、明暗、头、脸、面罩、武器一律照它，每一帧和它的区别只能是姿势。
> - **用户对之前几版最不满意的是：脸和眼睛看不清、像素乱不干净。** 所以每帧的头都照造型图逐格复制（只移动），只用造型图的颜色，大块平涂，不要自己加碎点。
> - **待机条已经做好**（`akali_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/akali_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染，**是镜像的**：武器在哪只手以造型图为准）；长相照造型图。英雄联盟里 Q、E 有空翻，**我们不画倒过来的身体**：头最多侧过 90°。突进类动作（E 第二段、R 两段）的位移由游戏引擎做，每帧都画在站位点附近。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/akali_palette.png`，或直接读 `design/akali_design_1x.png`）。**先把眼睛的琥珀色 `#D46A0A` 从色板里去掉**（它和腰包、绳子的颜色近，一吸附就会跑到身上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/akali_head_1x.png`：头发、发带、脸、眼睛、面罩和它们的描边；马尾不在里面，每帧自己画；在 128×128 画布上的范围 x 59–72、y 63–77）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。受击第 1 帧把眼睛改成闭眼（眼睛那两行改成一段深色短线）。
5. 对位：每帧按 `akali_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/akali_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/akali_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/akali_head.png`、`_1x.png` | 要贴进每一帧的头（不含马尾） | 贴头 |
| `design/akali_palette.png` | 造型图的全部 18 色（暗到亮） | 色板 |
| `akali_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/akali_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染（镜像），同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/akali_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `akali_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/akali_redraw4_B.png` | 用户认可的造型原画（你画的第 4 版 B） | 需要时看衣服、武器的结构；比例和颜色以造型图为准 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（头顶到脚底 37 格，含马尾 40 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **干净**：只用造型图的 18 种颜色，不加新颜色；每种材质照造型图的 2–3 个平涂色阶，大块纯色；不要抖动、渐变、噪点，一块颜色里不要夹单个杂色方块；外轮廓 1 格近黑描边，内部深色线条越少越好。
- **身体粗细照定稿**：手臂加描边至少 3 格宽；裤子是宽大的灯笼裤；马尾是几块大的蓝色发束加亮黄绿发带，不是一根根细线。
- **头每帧都是造型图的头**（头发、发带、脸、眼睛、面罩逐格一样），只平移或整体倾斜，否则循环动作里头会"沸腾"；两只眼睛一样大、同一行，不能连成横杠；琥珀色 `#D46A0A` 只用在眼睛上。马尾每帧自己画，跟着动作甩动。
- **苦无在近侧的手（图里左边那只），镰刀在远侧的手（右边那只）**，每帧都拿在手里，不能飘开，不能挡脸。参考渲染是镜像的，武器在哪只手照造型图。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面）。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变，只动腿、手臂、马尾、衣摆；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，不画背影、不画倒立（死亡最后倒地的帧除外）。**只画角色**：飞出的苦无扇、手里剑、斩击拖影、烟雾都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/akali_design.png`，第二张 `now/akali_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `akali_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, mask, weapons and pixel style exactly; do not redesign anything. Every frame is the FIRST image's character in a new pose: the same proportions, the same clean flat shading, the same big readable eyes. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places, MIRRORED - copy the motion of the body from it (but never turn her upside down: where the original flips, keep her upright or leaning at most a quarter turn).
The character: Akali (a slim masked ninja girl: layered navy-blue hair with a low ponytail sweeping back to the left, tied with a bright lime bow; big eyes with white and amber; a teal cloth mask over her nose and mouth; a teal sleeveless crop top with lime edges, bare tan midriff and arms, a small lilac tattoo on the upper arm; lime wrist wraps; a red satchel on an orange rope at her hip; teal loincloth panels; baggy blue trousers; lime-wrapped shins; dark blue shoes; a steel kunai in her near hand and a steel kama (sickle) in her far hand).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (37 squares from the crown to the soles when standing, 40 with the ponytail), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 18 colors of the FIRST image, no new colors: #0A0A14 #111C3E #441221 #094658 #182E61 #1A3E8A #A42D2F #1E6E7E #5F5E69 #789336 #D46A0A #C0602A #AEC926 #9B90BF #EFF92A #B8BCC8 #FDC58D #FDFDFD. Big flat areas, every material in the FIRST image's 2-3 shades; no dithering, no noise, no lone square of a different color inside an area; ONE 1-square near-black outline around the silhouette and very few inner dark lines - never a second black ring.
The head (hair, bow, face, eyes, mask) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. The ponytail is drawn in each frame and swings with the motion. The kunai is always in her NEAR hand (the left one in the image) and the kama in her FAR hand (the right one), as in the FIRST image - the THIRD image is mirrored, so where it shows the weapons the other way round, follow the FIRST image; the weapons move with her hands and never float free. Her eyes are the FIRST image's eyes (white over amber #D46A0A), both on the same rows, never merged into a bar; the amber appears ONLY in the eyes. The teal mask covers her face below the eyes in every frame.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the kunai, not the kama - because the game draws the health bar there (a fall may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in akali_cells.json). Dashes are moved by the game engine: keep her near her standing point. In a move loop her head keeps the same horizontal place relative to the standing point in every frame.
3/4 FRONT view facing right, never her back, never upside down (except a frame lying on the ground). Do not draw effects (flying kunai, shuriken, slash trails, smoke, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, clean flat areas without added specks, the kunai in the near hand and the kama in the far hand, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `akali_idle.png` | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 81 行 | **已做好，不用画** |
| `akali_run.png` | 8 × 105 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `MOVE, 8 frames, one seamless loop of League's run (0.84 s cycle, 8 x 105 ms, the SECOND and THIRD images): she runs low and forward like a ninja, the kunai in her near hand held low and forward, the kama in her far hand trailing, the feet striding as in the THIRD image (frames 1-4 one stride, 5-8 the other); her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); the ponytail streams back and bounces a little; frame 8 flows into frame 1.` |
| `akali_attack.png` | 6 帧：60 60 70 70 80 80 | 第 3 帧（tick 7） | 3 列 × 2 行，2304×1536 | 第 81 行 | `BASIC ATTACK, 6 frames: a kama slash as in the THIRD image: 1 she draws the kama back; 2 wind-up; 3 the release (the hit lands here): a fast horizontal slash forward to the right with the kama, body turned into it; 4 follow-through; 5-6 back toward the idle stance. The slash trail is an effect - do not draw it.` |
| `akali_attack_p.png` | 6 帧：60 70 80 80 90 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2304×1536 | 第 81 行 | `EMPOWERED ATTACK (Assassin's Mark), 6 frames: the long-reach strike as in the THIRD image: 1 she spins the kama back; 2 she steps in and whips it round; 3 the release (the hit lands here, far in front of her): the kama flung out forward to the right at full arm's length on its short chain, body stretched after it; 4 the kama still out; 5-6 pulling it back toward the idle stance. Draw the kama and a short chain only - the green slash is an effect.` |
| `akali_skill.png` | 6 帧：50 50 60 70 80 100 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536 | 第 81 行 | `FIVE POINT STRIKE, 6 frames: 1-3 wind-up: she leaps a little and raises the kunai hand high behind her shoulder (League flips here - keep her upright, the head never more than a quarter turn from upright); 4 the release (the kunai fan leaves here): she throws with the near arm swept forward to the right at shoulder height, fingers spread, body leaning into the throw; 5 follow-through; 6 back toward the idle stance. The five flying kunai are an effect - do not draw them.` |
| `akali_skill2.png` | 6 帧：50 60 60 60 70 90 | 第 5 帧（tick 14） | 3 列 × 2 行，2304×1536 | 第 81 行 | `SHURIKEN FLIP, the flip back, 6 frames: 1 she crouches; 2 she springs up and BACKWARD (a backward hop, League flips upside down here - keep her upright or leaning back at most a quarter turn); 3 landing crouched further back; 4 rising; 5 the release (the shuriken leaves here): she throws with the near arm swept forward to the right; 6 back toward the idle stance. The shuriken is an effect - do not draw it flying.` |
| `akali_skill2_dash.png` | 5 帧：50 50 60 70 90 | 第 4 帧（tick 10） | 3 列 × 2 行，2304×1536，最后 1 格空 | 第 81 行 | `SHURIKEN FLIP, the dash to the mark, 5 frames: 1-2 dashing forward to the right, body low and leaning far forward, the kunai hand stretched out ahead, the kama behind; 3 arriving, rising; 4 the release (the strike lands here): an upward slash with the kunai as in the THIRD image; 5 back toward the idle stance.` |
| `akali_ult.png` | 6 帧：60 50 50 80 90 100 | 第 2 帧（tick 4） | 3 列 × 2 行，2304×1536 | 第 81 行 | `PERFECT EXECUTION, the first dash, 6 frames: 1 a crouched ready pose, weight forward; 2-3 dashing forward to the right, body low and stretched, the kunai pointing ahead (the enemies she passes are hit here); 4 the landing slash: she comes up behind her target with the kama swung up high as in the THIRD image; 5 follow-through; 6 back toward the idle stance. Trails and slashes are effects.` |
| `akali_ult2.png` | 5 帧：50 50 50 70 90 | 第 4 帧（tick 9） | 3 列 × 2 行，2304×1536，最后 1 格空 | 第 81 行 | `PERFECT EXECUTION, the second dash (the execute), 5 frames: 1-3 a very low, fast dash forward to the right, body almost horizontal, the kunai thrust far ahead, the ponytail streaming back; 4 the release (the finishing strike): she ends the dash in a long low lunge, the kunai arm fully extended; 5 back toward the idle stance.` |
| `akali_hit.png` | 2 × 120 | — | 2 列 × 1 行，1536×768 | 第 81 行 | `HIT, 2 frames: 1 jolted back by a blow, eyes squeezed shut (the eye rows become short dark lines: the lash colour over skin); 2 recovering toward the idle stance.` |
| `akali_dead.png` | 8 帧：100 100 120 120 120 150 150 500 | — | 4 列 × 2 行，3072×1536 | 第 81 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck, head thrown back; 2 staggering; 3 swaying, barely standing; 4 still swaying; 5 toppling over; 6 falling; 7 on the ground; 8 lying still on the ground line on her side, the weapons on the ground beside her. Frames 6-8 may reach 2 squares below the feet line, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），大块平涂，没有自己加的碎点；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、一样大、同一高度；
- [ ] 琥珀色 `#D46A0A` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 苦无在近侧的手、镰刀在远侧的手，每帧都在，不挡脸；
- [ ] 没有倒立、没有背影；脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `akali_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、琥珀色只在眼睛上、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`（替换第一版的动作条，`native47/` 和 `shrink_akali.py` 退役），`akali_cells.json` 用包里这份，`akali_idle.png` 用包里已做好的那张。
- `import_native.py --hero akali`：ORDER 待机一张图 + BOB 呼吸（重新找接缝），EYES = `#D46A0A`（按眼睛对齐待机和移动）。
- 按出手帧核对技能数据的时机，重量特效挂点（身体中间的高度）和头像截取点，做预览 GIF。
