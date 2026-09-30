# 阿卡丽：按定稿造型画动作帧（第 2 步，第 3 版，给 Codex 的提示词）

> **这一版的前提：造型不许再改。** 上一版（v2）重新设计了造型（变瘦、四肢变细、马尾变成一根根细刺、衣服满是迷彩碎斑、换了眼睛），用户看了觉得很难看。之后造型重做了一次，用户选定的是**你直接按游戏尺寸画的那一版（`akali_model_v2` 的 A）**。这一版只画动作，每一帧的长相都照定稿，不能有任何重新设计。反面例子见 `refs/not_this_v2.png`（左边打叉的是 v2，右边是要照着画的定稿）。
>
> **造型已定**：你画的 A 版原稿，Claude 按原稿自己的格子（13 px 一格）取像素，再逐行逐列删减到游戏尺寸（头顶到脚底 43 格，含马尾 47 格；没有混色、没有模糊），脚底补回描边；眼睛是一行眼线加两行眼睛，近眼 3 格（白、白、棕）、远眼 2 格（白、棕），同一高度：`design/akali_design.png`（放大 8 倍，1024×1024，脚底在 y=792–799）。**造型图就是标准**，颜色、形状、明暗、头、脸、面罩、武器一律照它。
> - **待机条已经做好**（`akali_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 10 张动作图按下面的表画。
> - 帧数、每帧时长、出手帧和站位照 `now/akali_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。英雄联盟里 Q、E 有空翻，**我们不画倒过来的身体**：头最多侧过 90°。突进类动作（E 第二段、R 两段）的位移由游戏引擎做，所以每帧都画在站位点附近，不要画成在格子里跑出很远。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 上一版（v2）的问题，这一版一条都不能再出现

- **重新设计了造型**：身体变瘦，手臂只有 1–2 格宽，马尾变成一根根细刺，眼睛换了。→ 这一版的身体比例、马尾外形、衣服、眼睛**逐格照定稿**，每一帧和定稿的区别只能是姿势。
- **衣服满是随手撒的碎点**，像迷彩。→ 衣服照定稿画：绿上衣和浅一档的斜襟；露出的腰腹；米色腰带和金环、垂下的米色布条；中间的绿腰布和深绿的纹；深色灯笼裤；米色绑腿和金色小饰。定稿里的小方块都是在画东西（褶、边、金环、高光），照着画，只随姿势移动；不要自己另加杂点。
- **伸出去的手臂、发带、上衣肩部没有描边**（v2 的动作帧只有 79–93% 的外轮廓是深色描边，定稿 100%）。→ 每块颜色的外缘都有 1 格近黑描边，包括伸直的手臂；只有苦无、镰刀的刀刃和链子可以不描边。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/akali_palette.png`，或直接读 `design/akali_design_1x.png`）。**先把两个眼睛颜色 `#FFF8E8`、`#714129` 从色板里去掉**（它们和米色、皮肤的颜色很近，一吸附就会跑到身上），它们只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/akali_head_1x.png`：头发、发带、脸、眼睛、面罩和它们的描边；马尾不在里面，每帧自己画；在 128×128 画布上的范围 x 58–73、y 56–68）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。这样每帧的脸都和造型图一模一样。受击第 1 帧把眼睛改成闭眼（眼睛那两行改成一段深色短线）。
5. 对位：每帧按 `akali_cells.json` 的站位点放回格子（和 now 条同一格、同一位置），脚底踩在脚底线上；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/akali_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底） | 每张动作图的第一张附图 |
| `design/akali_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/akali_head.png`、`_1x.png` | 要贴进每一帧的头（不含马尾） | 贴头 |
| `design/akali_palette.png` | 造型图的全部 24 色（暗到亮） | 色板 |
| `akali_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/akali_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体的动作 |
| `guide/akali_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、帧号 | 对位用，不要画进图里 |
| `akali_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/not_this_v2.png` | **反面例子**：左边打叉的是被否定的 v2，右边是定稿 | 看清楚哪些不能做 |
| `refs/akali_picture.png` | 用户给的原图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref*.png` | 团战经理2 原版英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：站着时和造型图一样高（头顶到脚底 43 格，含马尾 47 格），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 24 种颜色**，不加新颜色；明暗照定稿（亮边、褶、高光跟着姿势移动），不要抖动、噪点、自己加的碎点；外轮廓 1 格近黑描边，描边里面用材质自己的暗色，不要再画一圈黑。
- **身体粗细照定稿**：近侧手臂 3 格颜色宽、远侧 2–3 格（再加两边描边），不能只有 1 格；裤子是宽大的灯笼裤，马尾是一整团大的黑发（几个尖角，不是一根根细线）；衣服色块的位置和形状照定稿，只随姿势移动。
- **头每帧都是造型图的头**（头发、发带、脸、眼睛、面罩逐格一样），只平移或整体倾斜；眼睛两只一样大、同一行，不能连成横杠，`#FFF8E8` 和 `#714129` 只用在眼睛上。马尾每帧自己画，跟着动作甩动。
- **苦无在近侧的手（图里左边那只），镰刀在远侧的手（右边那只）**，每帧都拿在手里，不能飘开，不能挡脸。
- **脚底线以下什么都不能有**（游戏在脚下画血条）：每帧最低一行是脚底线（参考线图的红线就在它下面）。只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变，只动腿、手臂、马尾、衣摆；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，不画背影、不画倒立（死亡最后倒地的帧除外）。**只画角色**：飞出的苦无扇、手里剑、斩击拖影、烟雾都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/akali_design.png`，第二张 `now/akali_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `akali_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, mask, weapons and pixel style exactly; do not redesign anything. IMPORTANT: a previous attempt redrew the character (slimmer, thin 1-2 square limbs, a stringy ponytail of thin spikes, camouflage-like specks all over the clothes, different eyes) and was rejected as ugly. Every frame must be the FIRST image's character in a new pose: the same sturdy chibi proportions (arms 2-3 squares of colour wide plus the outline, never 1; wide baggy trousers), the same big solid ponytail with a few spikes, the same clothes and shading (the green top with its lighter diagonal wrap, the bare midriff, the cream sash with its gold ring and hanging cream strip, the green loincloth with darker green chevrons, the dark baggy trousers, the cream shin wraps with gold) and the same big eyes. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character stands in its cell, but NOT its blurry look. THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body from it (but never turn her upside down: where the original flips, keep her upright or leaning at most a quarter turn).
The character: Akali (a chibi ninja girl with a huge spiky black ponytail in a green band, a dark green cloth mask over her nose and mouth, big brown eyes, tan skin, a sleeveless green crop top with a lighter green diagonal wrap, a bare midriff, a tattoo on her near upper arm, dark forearm guards with gold rings, a cream sash with a gold ring over a green loincloth, baggy charcoal trousers and cream shin wraps with gold; a steel kunai in her near hand and a steel kama (sickle) in her far hand).
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (43 squares from the crown to the soles when standing, 47 with the ponytail), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 24 colors of the FIRST image, no new colors: #10101A #191D2B #272633 #1F3831 #2C3040 #3E3C4D #335145 #714129 #755225 #424A61 #56643A #595768 #9C5C39 #81775D #6E7A8C #B88835 #CA8755 #E2B94B #C9BB93 #EFB57F #ACB8C8 #EEE1B7 #E7EEF2 #FFF8E8. ONE outline: a 1-square near-black outline around the silhouette and each material's own dark shade inside it - never a second black ring. Copy the FIRST image's shading - its lit edges, folds and highlights move with the pose; no dithering, no noise, no random specks added.
The head (hair, hair band, face, eyes, mask) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. The ponytail is drawn in each frame and swings with the motion. The kunai is always in her NEAR hand (the left one in the image) and the kama in her FAR hand (the right one), as in the FIRST image; they move with her hands, never float free. Her eyes are the FIRST image's eyes (a near-black liner row over two rows: the near eye white, white, brown iris, the far eye white, brown iris; white #FFF8E8, brown #714129), on the same rows, never merged into a bar; those two eye colours appear ONLY in the eyes. The dark green mask covers her face below the eyes in every frame.
Feet line: in every cell the lowest row of her feet is square row [R] from the top of the cell (pixels [R*8] to [R*8+7]); NOTHING from pixel [R*8+8] down - not the kunai, not the kama - because the game draws the health bar there (a fall may dip at most 2 squares). Her place across the cell follows the SECOND image (each frame's standing point is in akali_cells.json). Dashes are moved by the game engine: keep her near her standing point. In a move loop her head keeps the same horizontal place relative to the standing point in every frame.
3/4 FRONT view facing right, never her back, never upside down (except a frame lying on the ground). Do not draw effects (flying kunai, shuriken, slash trails, smoke, glows) - only the character. Every animation starts and ends in the FIRST image's stance.
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, the body as thick as in the FIRST image and its clothes and shading the same (no added specks), every colour edge outlined except the blades, the kunai in the near hand and the kama in the far hand, nothing below the feet line, the frames in the same cells as the SECOND image.
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
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色），衣服和明暗照定稿，没有自己加的碎点（每帧单格杂色不比定稿多）；
- [ ] 身体比例、马尾外形、衣服色块和定稿一样（和 `refs/not_this_v2.png` 左边那种变瘦、变碎的样子相反）；每块颜色外缘都有描边（刀刃、链子除外）；
- [ ] 每一帧站着时和造型图一样高；头就是造型图的头（逐格一样，只平移），两只眼睛都在、一样大、同一高度；
- [ ] `#FFF8E8`、`#714129` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 苦无在近侧的手、镰刀在远侧的手，每帧都在，不挡脸；
- [ ] 没有倒立、没有背影；脚底线以下没有任何像素（只有死亡帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `akali_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、眼睛只在眼睛上、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`akali_cells.json` 用包里这份，`akali_idle.png` 用包里已做好的那张。
- `import_native.py --hero akali`：ORDER 待机一张图 + BOB 呼吸，EYES = `#FFF8E8`（按眼睛对齐待机和移动）。
- 按出手帧核对技能数据的时机（普攻 tick 7、强化普攻 tick 8、Q tick 10、E 掷出 tick 14、E 突进斩 tick 10、R 冲刺 tick 4、R2 tick 9），重量特效挂点和头像截取点，重跑模拟，做预览 GIF。
