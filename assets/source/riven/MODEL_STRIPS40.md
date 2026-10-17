# 锐雯：按缩小后的造型重画 10 条动作和 7 组特效（给 Codex）

> 用户在游戏里看锐雯觉得太大（46 行，比盖伦的 37 行高出一截），选了缩到 40 行的造型 `riven_native.png`（从原定稿删行删列缩小，脸逐格保留）。这一轮：
> 1. **10 条动作重画成新大小**：移动、普攻、Q 三段、E+W、R 开启、疾风斩、受击、死亡。姿势、帧数、帧时长、每帧在格子里的位置都照现在游戏里的动作 `riven_now_<动作>.png`（它们是你上次画的，用户已经认可），只是人换成新造型的大小和样子。待机不用画（`riven_idle.png` 已用新造型拼好）。
> 2. **7 组特效在新动作上重画**：Q1、Q2 剑弧，Q3 地裂，E 护盾横扫，W 地面爆发，R 开启剑身绿光，疾风斩月牙。样子照 `fx_now/`（你上次画的、已在游戏里的），但跟着新动作的剑和身体走，大小按新身体缩（绕身体的护盾、地面的圈照新身高缩）。
> 3. **清单里记下每帧剑的断口**：大招时我会沿剑身在剑下面画一把绿色能量大剑，需要知道每帧断剑的断口位置和方向。
> 交回：`strips/riven_<动作>.png`（10 张）、`effects/riven_fx_<组>_<back|front>.png`（14 张）、`HANDOFF.md`、`manifest.json`（每帧的站位点、时长、头贴的位置和旋转 `head_origin` / `head_rotation_clockwise`、剑 `sword`），再附 `reference/head_master_1x.png`（贴进每帧的头）和 `reference/riven_idle.png`。

## 附图

| 文件 | 内容 | 用法 |
|---|---|---|
| `riven_native.png` | 新造型，8 倍，1024×1024，40 行高，脚底第 99 行、站位点 (64, 88) | **第一张图**：大小、颜色、头、衣服、断剑、像素风格全照它 |
| `riven_now_<动作>.png` | 现在游戏里的动作（46 行高，你上次画的），8 倍，每格 96×96 个方块 | **第二张图**：每帧的姿势、时机、在格子里的位置照它，人画成第一张图的大小 |
| `lol_pose_<动作>.png` | 英雄联盟原版动作的同一帧渲染 | 身体动作拿不准时参考 |
| `riven_guide_<动作>.png` | 每帧的站位点（蓝十字）和脚底线（红线），红线以下淡红区不能有像素 | 对位用，不要画进图里 |
| `riven_cells.json` | 每帧站位点和帧时长（和上次一样） | 整理对位 |
| `riven_idle.png` | 新待机条（已拼好，不用画） | 每个动作从这个站姿开始、回到它结束 |
| `riven_design_1x.png` / `riven_palette.png` | 新造型原尺寸 / 它的全部颜色 | 吸色板 |
| `fx_now/riven_fx_<组>_<back|front>.png` | 现在游戏里的特效图层（8 倍，和动作同样的格子） | 第二部分照它的样子重画 |
| `fx_now/riven_fx_final.png` | 这些特效叠在现在动作上的样子（4 倍） | 看整体效果 |
| `tfm2_style_ref_swordsman.png` | 团战经理2 原版英雄 | 像素大小和干净程度 |

## 第一部分：10 条动作

- **只用新造型的 27 种颜色**：#1C0903 #1E1319 #24181F #2D1D1C #272720 #163A22 #293828 #3F2A24 #493328 #593C2C #434A46 #68432C #426E3B #7E4F30 #3E8E48 #996B3D #A8643F #867469 #CB8053 #C79860 #A89588 #E39F6B #BBAA9C #D0BFB0 #FBC697 #F6EADB #FFFFFF。不加新颜色。
- **头每帧照新造型逐格复制**（大小也照新造型，比上次小），只随动作整体移动或倾斜，不重新画；两只眼睛各 2×2、同一行；眼睛三色 `#FFFFFF` `#163A22` `#3E8E48` 只用在眼睛上；不画嘴。
- **大小**：站着时从头顶翘发到脚底约 40 格（上次约 46 格）；断剑也照新造型的大小。每条动作里人都和待机一样大（整理时会比较每帧面积）。
- **只有一圈描边**、干净的大块纯色、不画背影、脚底线（站位点下方第 11 行）以下什么都不能有（死亡倒地帧最多 2 格），规则和上次一样。
- 背景透明（做不到用纯品红 `#FF00FF`）；不要网格线、文字、边框、参考线。

```text
Three attached images. FIRST: the approved pixel-art design of this character at 8x (every pixel an 8x8 block), now SMALLER than before - about 40 pixels from the top of her hair tuft to the soles - copy her size, colors, shapes, head, clothes, broken sword and pixel style exactly. SECOND: her current animation (drawn earlier at a bigger size, about 46 pixels tall), frames in a grid of cells read left to right, top to bottom - keep every frame's pose, timing and place in its cell exactly, and draw her at the FIRST image's smaller size standing on the same standing point (her soles on the same feet line). THIRD: League's original animation at the same frames, only if a pose is unclear.
Task: redraw every frame as clean pixel art at EXACTLY the FIRST image's pixel size, every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller than one square, no anti-aliasing, no blur, no semi-transparency.
Pixel rules (most important): only the colors of the FIRST image, no new ones; big flat areas, 2-3 shades per material; no dithering, no gradients, no noise, no lone square of a different color inside an area; ONE 1-square near-black outline around the silhouette, and inside it the material's own darkest shade - never a second ring of black.
Head and face: copy the head of the FIRST image into every frame square for square - the same outline, white hair with the small tuft, and both eyes - only moved (or tilted in a leap or the fall), never redrawn: each eye 2x2 on one row (#FFFFFF top-left, #163A22 top-right, #3E8E48 bottom row); these three eye colors used nowhere else; no mouth. The broken sword is the FIRST image's, the same size in every frame, in the hand on the right of the image; arms and sword never cover the face; 3/4 FRONT view facing right, never her back.
Feet line: in every cell the lowest row of her soles is the row 11 squares below that frame's standing point (riven_cells.json); NOTHING below it, not the sword tip either (only the lying death frames may reach 2 squares below).
[animation]
Layout: exactly like the SECOND image - [grid], each cell 96x96 squares (768x768 px), [size]. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, no borders, no labels, no guide marks.
```

| 文件 | 帧 × 毫秒 | 排版 | `[animation]` |
|---|---|---|---|
| `riven_run.png`（移动） | 8 × 121 | 4 列 × 2 行，3072×1536 | `Animation: the same 8 frames as riven_now_run.png, each pose kept, the body at the FIRST image's size.` |
| `riven_attack.png`（普攻） | 6 帧：60 60 70 70 80 90 | 3 列 × 2 行，2304×1536 | `Animation: the same 6 frames as riven_now_attack.png, each pose kept, the body at the FIRST image's size.` |
| `riven_skill.png`（Q 第一段） | 7 帧：50 50 60 60 70 80 90 | 4 列 × 2 行，最后 1 格空，3072×1536 | `Animation: the same 7 frames as riven_now_skill.png, each pose kept, the body at the FIRST image's size.` |
| `riven_q2.png`（Q 第二段） | 7 帧：50 50 60 60 70 80 90 | 4 列 × 2 行，最后 1 格空，3072×1536 | `Animation: the same 7 frames as riven_now_q2.png, each pose kept, the body at the FIRST image's size.` |
| `riven_q3.png`（Q 第三段·跃起砸地） | 7 帧：50 60 80 60 70 90 100 | 4 列 × 2 行，最后 1 格空，3072×1536 | `Animation: the same 7 frames as riven_now_q3.png, each pose kept, the body at the FIRST image's size.` |
| `riven_skill2.png`（E 冲刺 + W 怒吼） | 8 帧：50 50 50 60 70 80 90 100 | 4 列 × 2 行，3072×1536 | `Animation: the same 8 frames as riven_now_skill2.png, each pose kept, the body at the FIRST image's size.` |
| `riven_ult.png`（R 开启） | 6 帧：60 70 80 90 100 110 | 3 列 × 2 行，2304×1536 | `Animation: the same 6 frames as riven_now_ult.png, each pose kept, the body at the FIRST image's size.` |
| `riven_r_slash.png`（R 疾风斩） | 6 帧：60 70 70 80 90 110 | 3 列 × 2 行，2304×1536 | `Animation: the same 6 frames as riven_now_r_slash.png, each pose kept, the body at the FIRST image's size.` |
| `riven_hit.png`（受击） | 2 × 100 | 2 列 × 1 行，1536×768 | `Animation: the same 2 frames as riven_now_hit.png, each pose kept, the body at the FIRST image's size.` |
| `riven_dead.png`（死亡） | 8 帧：100 100 100 120 120 150 150 400 | 4 列 × 2 行，3072×1536 | `Animation: the same 8 frames as riven_now_dead.png, each pose kept, the body at the FIRST image's size.` |

## 第二部分：7 组特效（画在新动作上）

- 每组两张图：身后一层 `_back`、身前一层 `_front`（头的范围只放后层，不挡脸），和它所属的动作同样的格子、帧数、时长、站位点：Q1 → `riven_skill`，Q2 → `riven_q2`，Q3 → `riven_q3`，E 和 W → `riven_skill2`，R 开启 → `riven_ult`，疾风斩 → `riven_r_slash`。
- 样子照 `fx_now/`：同样的形状、帧序、颜色（`#F6EADB` `#C9EF9A` `#87D46A` `#4BA85A` `#2D6940`，Q3 碎石加 `#867469` `#493328`），跟着新动作的剑和身体走；绕身体的护盾、地面的圈按新身高缩小。
- **不要描边**：上次每个图形外面都描了一圈最深的绿 `#183A2A`，导入时要去掉；这次 `#183A2A` 只能用在图形里面当阴影，不沿边。
- 特效也不能画到脚底线以下（地面的圈、地裂除外：它们贴着地面画在脚底线附近，和现在一样）。

```text
Pixel-art effects drawn ON the new animation frames above, one layer behind the character (_back) and one in front of her (_front), in the same cells, frames, times and standing points as the animation they belong to; the head's area only in the back layer. Copy the look of the attached current effects (fx_now: the same shapes, frame order and colors #F6EADB #C9EF9A #87D46A #4BA85A #2D6940, Q3's rocks also #867469 #493328) but follow the new, smaller frames' sword and body; rings round her body or on the ground shrink with her. NO dark outline: #183A2A only as a shade inside a shape, never along its edge. Every pixel one 8x8 block, alpha 0 or 255, transparent background.
```

## 第三部分：清单里每帧的剑

`manifest.json` 里每条动作的每一帧加一项 `sword`：断剑断口（锯齿那一端）中点的位置和剑身方向，用这一帧格子里的游戏像素坐标（和 `riven_cells.json` 的站位点同一个坐标系，左上角 (0, 0)）：
`"sword": {"broken_end": [x, y], "direction": [dx, dy]}`，`direction` 是从剑柄指向断口的单位向量（例如剑尖朝右下 `[0.9, 0.4]`）。剑被身体挡住看不见、或正对镜头只剩一个点的帧写 `"sword": null`。所有 10 条动作都记（待机用造型的站姿，不用记）。

## 交回前自查

- 每张图的格子、帧位置和 `riven_now_<动作>.png` 一样；8×8 纯色块；透明度只有 0 和 255；只用新造型的颜色。
- 头和新造型逐格一样；每帧两只眼睛各 2×2、同一行；人和新待机一样大（约 40 行），不是 46 行。
- 特效没有深色描边；每组的帧数、格子和它所属的动作一样。
- `manifest.json` 里每帧都有 `head_origin`、`head_rotation_clockwise` 和 `sword`。
