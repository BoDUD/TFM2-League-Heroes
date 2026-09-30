> 第 2 步的结果（2026-09-30）：Codex 交回 `nami_animation_pack`，7 张全部过了检查（方块、色板、脚底线、每帧的头逐格一致，动作和英雄联盟原版的位置只差 1–2 格），但第一版（16:04）有 13 帧手杖散了（宝珠脱开或没了、格子里飘着碎片）；Codex 自己的第二遍（16:11）修好了大半，R 也改成低跳、第 5–6 帧把杖插在地上。返修两轮：`nami_strips_fix_pack` → `nami_animation_fix`（普攻、W、Q、受击的 13 帧，交接说明 `codex_strips/fix_HANDOFF.md`），`nami_ult_fix_pack` → `nami_animation_fix2`（16:11 版 R 的第 2、3 帧，`codex_strips/fix2_HANDOFF.md`）。`tools/art/tidy_nami.py` 拼齐：移动、死亡、R 用 16:11 版，普攻、W、Q、受击用返修版；各动作最后一帧换成定稿站姿；删掉 12 格以下的碎点。

# 娜美：按定稿造型画动作帧（第 2 步，给 Codex 的提示词）

> **造型已定**：你第 3 轮按游戏尺寸画的 A 稿，脸换成用户选的 D（椭圆脸、尖下巴、琥珀色大眼），体型照用户选的 W 逐行逐列删减到和别的英雄一样大（36×50 格、21 色，没有平均模糊），尾鳍的浅色换成原图的淡黄绿 `#E8E6A8`：`design/nami_design.png`（放大 8 倍，1024×1024）。**造型图就是标准**，颜色、形状、头、脸、手杖、尾巴一律照它。
> - **待机条已经做好**（`nami_idle.png`，每帧就是造型图，站在待机的站位点上），不用画；它也告诉你造型图在格子里多大、站在哪里。其余 7 张动作图按下面的表画。
> - **她是浮在空中的人鱼**（和迦娜一样）：待机时尾鳍最低一格在脚底线上方 3 格（参考线图的绿虚线上面那一行）；动作里最低可以到脚底线，但绝不能低于它（游戏在脚下画血条）。
> - 帧数、每帧时长、出手帧和站位照 `now/nami_now_<动作>.png`（英雄联盟原版动作按游戏尺寸取色）；身体的动作照 `pose/lol_pose_<动作>.png`（同一帧的高清渲染）；长相照造型图。英雄联盟的娜美戴紫色头盔、金色鳍状头发，手杖顶上是圆环，尾巴在身下卷起、尾鳍翘在身后；**我们的造型是用户图里的**：红色长发、金冠、蓝宝珠手杖、往左下卷的尾巴和淡黄绿扇形尾鳍。每帧都照造型图画，只有动作跟英雄联盟。
> - 交回的图必须每个像素都是严格对齐的 8×8 纯色块（做法见「建议流程」）。附 `HANDOFF.md`（每张用了哪条提示词、哪里没做到）、`manifest.json`（每帧的格子矩形、站位点 pivot、不透明范围 bbox）和 `generation_prompts.json`。

## 建议流程（每一张动作条）

1. 生图：附图顺序和通用提示词一样（造型图、now 条、lol_pose）。
2. 对齐网格：找出方块边界，每个方块取中心颜色，缩成 1 像素 1 格的原尺寸图；透明度只留 0 和 255。
3. 色板：每个像素换成造型图色板里最近的颜色（`design/nami_palette.png`，或直接读 `design/nami_design_1x.png`）。**先把眼睛的琥珀色 `#F2B233` 从色板里去掉**（它和金饰、头发的颜色很近，一吸附就会跑到身上），它只随第 4 步贴的头回来。
4. **贴头**：把造型图的头（`design/nami_head_1x.png`：金冠、头顶和脸旁的头发、鱼鳍耳、脸、眼睛、嘴和它们的描边；在 128×128 画布上的范围 x 53–71、y 47–62）原样贴进每一帧头的位置（只平移，身体倾斜时整体倾斜；死亡倒地的帧可以不贴）。这样每帧的脸都和造型图一模一样。下巴以下披到腰的红色长发不在贴的头里，跟着动作画。受击第 1 帧把眼睛改成闭眼（眼睛那两行各一段深色短线）。
5. 对位：每帧按 `nami_cells.json` 的站位点放回格子（和 now 条同一格、同一位置）；检查脚底线以下没有像素；再放大 8 倍输出。
6. 按最后的「交回前自查」逐项检查。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/nami_design.png` | **定稿造型**，放大 8 倍（1024×1024，透明底）；站位点 (64, 88)，脚底线第 99 行，尾鳍最低一格在第 96 行（浮空 3 格） | 每张动作图的第一张附图 |
| `design/nami_design_1x.png` | 同一张，原尺寸（128×128） | 脚本用：色板、贴头 |
| `design/nami_head.png`、`nami_head_1x.png` | 只有头，在画布上原来的位置 | 贴头 |
| `design/nami_palette.png` | 造型图的全部 21 色（暗到亮） | 色板 |
| `nami_idle.png` | **已做好的待机条** | 不用画；看大小和站位 |
| `now/nami_now_<动作>.png` | 英雄联盟原版动作按游戏尺寸取色，放大 8 倍，按格子排好 | 第二张附图：帧数、时机、站位 |
| `pose/lol_pose_<动作>.png` | 同一帧的高清渲染，同样的格子、同样的位置 | 第三张附图：身体、手杖、尾巴的动作 |
| `guide/nami_guide_<动作>.png` | 每格边框、站位点（蓝十字）、脚底线（红线）和红线下的禁区、待机浮空线（绿虚线：待机时最低一格在它上面那一行）、帧号 | 对位用，不要画进图里 |
| `nami_cells.json` | 每帧的站位点（格子里第几列、第几行，单位方块）和帧时长 | 整理对位 |
| `refs/nami_picture.png` | 用户给的原图（长相参考；比例以定稿造型为准） | 需要时参考 |
| `style/tfm2_style_ref_support.png` | 团战经理2 原版辅助、法师英雄，放大 8 倍 | 像素大小和干净程度 |

## 规则（每张都一样）

- **和造型图一模一样的像素**：待机姿势时 50 格高（金冠到尾鳍尖），每个像素一个 8×8 方块，对齐同一个网格，没有抗锯齿、模糊、半透明。
- **只用造型图的 21 种颜色**，不加新颜色；大块纯色，不要抖动、噪点；外轮廓 1 格近黑描边 `#0E0B14`，描边里面用材质自己的暗色，不要再画一圈黑。
- **头每帧都是造型图的头**（金冠、头发、鱼鳍耳、脸、眼睛、嘴逐格一样），只平移或整体倾斜；眼睛两只一样大、同一行，不能连成横杠；琥珀色 `#F2B233` 只用在眼睛上。
- **红色长发**从头后披到腰，跟着动作飘动，颜色照造型图。
- **手杖每帧都在**（死亡里飞出手之前）：深蓝杖身、金环，顶上金框蓝宝珠，底下金尖；握在前手（画面右边那只手）里，随动作挥、刺、立，不能飘开，不能挡脸。
- **尾巴**：造型图的青绿鳞片尾巴、深蓝暗面、淡黄绿扇形尾鳍，从腰带下长出；照第三张图的节奏摆动、卷曲，样子照造型图。
- **浮空和脚底线**：待机时最低一格在脚底线上方 3 格；动作里最低到脚底线那一行，**脚底线以下什么都不能有**（参考线图红线以下的淡红区）；只有死亡倒地的帧可以低于红线，最多 2 格。
- **移动循环**：每帧头相对站位点的横向位置不变，只动尾巴、手臂、手杖、头发；上下起伏最多 1 格；首尾能无缝接上。
- 3/4 正面朝右，不画背影。**只画角色**：水弹、泡泡、水流、海浪、水花、光效都是单独的特效，不要画。
- **排版和 now 条完全一样**：同样的图片尺寸、同样的格子，帧 N 在同一格；空格留空。背景透明（做不到时用纯品红 `#FF00FF`）。不要网格线、边框、文字、编号、参考线。
- 如果模型不肯画有名字的角色，把名字删掉，只保留外观描述。

## 通用提示词（每张动作图都用这一段，只替换中括号）

每张附三张图：第一张 `design/nami_design.png`，第二张 `now/nami_now_<动作>.png`，第三张 `pose/lol_pose_<动作>.png`。`[animation]`、`[R]`、`[grid]`、`[size]` 按下表。输出文件名 `nami_<动作>.png`。

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its colors, shapes, head, face, staff, tail and pixel style exactly; do not redesign anything. SECOND: the original animation sampled at game size at 8x, frames in a grid of cells read left to right, top to bottom - copy the number of frames, each frame's timing (which frame is the wind-up, the release, the recovery), the size and where the character is in its cell, but NOT its blurry look (and NOT its purple helmet, its ring-topped staff or its tail curled under the body: our design has red hair with a small gold crown, a staff with a blue orb, and a tail that curls down to the lower left). THIRD: the original 3D animation at the same frames, in the same grid and the same places - copy the motion of the body, the arms, the staff and the swing of the tail from it.
The character: Nami (a chibi mermaid girl with long flowing red-orange hair and a small gold crown set with a blue gem, big amber eyes, pale sea-green skin and a teal fin-shaped ear, a gold-and-blue shell top and belt, a long teal fish tail that curls down to the lower left and ends in a big pale yellow-green fan fin; she holds a tall staff: a dark-blue shaft with gold rings, a blue orb in a gold frame at the top and a gold tip at the bottom). She floats above the ground.
Task: draw every frame as clean pixel art identical in style to the FIRST image, at EXACTLY the same pixel size (50 squares tall from the crown to the fin tip in the stance), every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): ONLY the 21 colors of the FIRST image, no new colors: #0E0B14 #06204A #0C3366 #0B5569 #93321F #1B4F92 #1D7B7C #9C3F46 #9D6B2F #CB552B #1E8FD6 #4FAE8E #F08A3C #D3A04A #F2B233 #9ECB98 #B5D1BC #F6D57F #E8E6A8 #DDEBD0 #F2FDFD. ONE outline: a 1-square near-black outline (#0E0B14) around the silhouette and each material's own dark shade inside it - never a second black ring. Big flat areas; no dithering, no noise, no lone square of a different color inside an area.
The head (crown, hair, fin ear, face, eyes, mouth) is COPIED from the FIRST image in every frame, square for square, and only moved (or tilted as a whole where the body leans); never redraw it, or it flickers when the frames play. Her eyes are the FIRST image's eyes (2x2 each: a white catch-light top left, amber #F2B233 elsewhere, a dark lash row above), both the same size on the same rows, never merged into a bar; the amber appears ONLY in the eyes. The long red hair flows from behind her head down her back and swings with the motion. The staff is in every frame (until it flies out of her hand in the death), held in her front hand (the one on the right of the image): it moves with her arms, never floats free, never covers her face. The tail keeps the FIRST image's shape and colors and grows from under her belt; it sways and curls with the motion as in the THIRD image.
Feet line: in every cell NOTHING may be drawn below square row [R] from the top of the cell (pixels [R*8] to [R*8+7] are the last row allowed; nothing from pixel [R*8+8] down) - not the tail, not the staff - because the game draws the health bar there. She floats: in the stance her lowest pixel is on row [R-3], and in the actions she comes down to row [R] at most (only the lying frames of the death may dip 2 squares lower). Her place across the cell follows the SECOND image (each frame's standing point is in nami_cells.json). In a move loop her head keeps the same horizontal place relative to the standing point in every frame.
3/4 FRONT view facing right, never her back. Do not draw effects (water bolts, the bubble, the stream, the wave, splashes, glows) - only the character. Every animation starts and ends in the FIRST image's stance (the staff upright in her front hand, the tail curled to the lower left).
Animation: [animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size] pixels; frame N in the same cell as in the SECOND image; unused cells stay empty. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
Before finishing, check: every square 8x8 on one grid, only the FIRST image's colors, the head identical to the FIRST image in every frame, both eyes visible and level, the amber only in the eyes, nothing below the feet line, the frames in the same cells as the SECOND image.
```

## 各张动作图

| 文件 | 帧 × 毫秒 | 出手帧 | 排版（列 × 行，像素） | `[R]` 脚底线 | `[animation]` |
|---|---|---|---|---|---|
| `nami_idle.png`（待机） | 6 × 200 | — | 3 列 × 2 行，2304×1536 | 第 84 行 | **已做好，不用画** |
| `nami_run.png`（移动） | 8 × 125 | — | 4 列 × 2 行，3072×1536 | 第 84 行 | `MOVE, 8 frames, one seamless loop of League's swim (1 s, 8 x 125 ms; the SECOND and THIRD images): she glides forward upright, holding the staff level in front of her (the orb forward, to the right), while her tail beats once per loop: frames 1-3 the tail rises behind her with the fin up, 4-6 it sweeps back and down, 7-8 it rises again and flows into frame 1; the long red hair streams back; her head keeps the same place across the cell relative to the standing point in all 8 frames (at most 1 square up or down); nothing below the feet line.` |
| `nami_attack.png`（普攻） | 6 帧：60 60 70 70 90 110 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1536 | 第 84 行 | `BASIC ATTACK, 6 frames: she swings the staff and thrusts its orb at the target (the water bolt is a separate effect - do not draw it): 1 she lifts the staff; 2 she rears back, the staff pulled in to her chest; 3 she swings it forward; 4 THE RELEASE (the bolt leaves here): the staff thrust out level to the right, the orb in front, her body leaning forward, the tail stretched out behind; 5-6 back toward the idle stance.` |
| `nami_skill.png`（W 冲击之潮） | 6 帧：60 70 80 90 100 100 | 第 3 帧（tick 8） | 3 列 × 2 行，2304×1536 | 第 84 行 | `EBB AND FLOW, 6 frames: a quick flick of the staff that sends a stream of water bouncing between enemies and allies (the stream is a separate effect): 1 she turns the staff level; 2 she draws it back, leaning back, the staff level in both hands; 3 THE RELEASE (the stream leaves here): she whips the staff forward, the orb pointing at the target to the right, her body rising a little and the tail sweeping out behind her; 4 holding the follow-through, the tail stretched back; 5-6 settling back into the idle stance.` |
| `nami_skill2.png`（Q 碧波之牢） | 6 帧：60 70 60 70 100 120 | 第 4 帧（tick 11） | 3 列 × 2 行，2304×1536 | 第 84 行 | `AQUA PRISON, 6 frames: she spins and flings a bubble from the staff (the bubble is a separate effect): 1-2 she coils up, the staff pulled back high, the tail swung out behind her; 3 she starts to turn, the staff sweeping round; 4 THE RELEASE (the bubble leaves here): the staff swung level in front of her, the orb thrust forward to the right, her tail curling round beside her; 5-6 back toward the idle stance. Keep her face visible in every frame.` |
| `nami_ult.png`（R 怒涛之啸） | 7 帧：60 70 80 80 100 120 140 | 第 5 帧（tick 17） | 4 列 × 2 行，3072×1536，最后 1 格空 | 第 84 行 | `TIDAL WAVE, 7 frames: she leaps up and plants her staff to call a great wave (the wave is a separate effect): 1 she tosses the staff up above her head; 2-3 she springs upward, her body stretched tall, the tail hanging below her (never below the feet line); 4 at the top she catches the staff; 5 THE RELEASE (the wave rises here): she comes down and plants the staff upright in front of her, the orb high, both hands on it; 6 held, crouched over the planted staff; 7 back toward the idle stance.` |
| `nami_hit.png`（受击） | 2 × 100 | — | 2 列 × 1 行，1536×768 | 第 84 行 | `HIT, 2 frames: 1 jolted back by a blow, eyes squeezed shut (two short dark lines on the eyes' rows); 2 recovering toward the idle stance.` |
| `nami_dead.png`（死亡） | 8 帧：100 100 120 120 120 150 150 500 | — | 4 列 × 2 行，3072×1536 | 第 84 行 | `DEATH, 8 frames, as in the THIRD image: 1 struck, thrown back; 2 flung up, arching back, the staff flying out of her hand; 3 hanging limp in the air, arms out; 4 tipping forward; 5 falling head first; 6 she hits the ground face down; 7 lying face down, the tail up behind her; 8 lying still, the tail resting. The staff is not in her hands from frame 2; from frame 6 it lies flat on the ground behind her. Frames 6-8 lie on the feet line and may reach 2 squares below it, nothing lower.` |

## 交回前自查（每张）

- [ ] 图片尺寸、格子数和 now 条完全一样，帧 N 在同一格，空格是空的；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255；
- [ ] 只用造型图色板里的颜色（逐像素比对，没有新颜色）；
- [ ] 每一帧和造型图一样大；头就是造型图的头（逐格一样，只平移），两只眼睛都在、一样大、同一高度；
- [ ] 琥珀色 `#F2B233` 只出现在眼睛上：头部范围以外 0 个像素；
- [ ] 手杖每帧都在前手里（死亡第 2 帧起除外），不挡脸；尾巴是造型图的样子；
- [ ] 脚底线以下没有任何像素（只有死亡倒地的帧可以低 1–2 格）；
- [ ] 移动循环：头的横向位置每帧一样，上下起伏不超过 1 格，首尾能接上；
- [ ] 出手帧的姿势在表里写的那一帧；
- [ ] 没有特效、网格、文字、编号、参考线；`manifest.json` 里每帧的格子矩形、站位点和 bbox 都写了。

## Claude 导入时（给 Claude 看）

- 交回的 `nami_<动作>.png` 先检查（严格方块、二值透明、色板、脚底线、琥珀色只在眼睛上、每帧面积和待机比），不在网格上的重新取样；眼睛不对的帧换回造型图的头。
- 放进 `assets/source/native/`，`nami_cells.json` 用包里这份，`nami_idle.png` 用包里已做好的那张。
- `import_native.py --hero nami`：ORDER 待机一张图，BOB 让整张图上下浮一格（浮空，像迦娜），EYES = `#F2B233`（按眼睛对齐待机和移动）。
- 按出手帧核对技能数据的时机（普攻 tick 11、W tick 8、Q tick 11、R tick 17），量特效挂点和头像截取点，重跑模拟，做预览 GIF。
