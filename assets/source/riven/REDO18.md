# 锐雯：照英雄联盟原版重画 18 帧（给 Codex）

> 上一轮缩到 40 行的动作交回后，用户逐帧看出“脖子拉伸、手脱节、各种身体脱节、还有无影手”。查下来是这 18 帧的姿势没有照原版：剑画到了头顶上方，握剑的手搭在头发上、手臂被头挡住，有的剑和手直接断开（Q1 第 5、6 帧），有的手臂只有 1 格粗像一根线。英雄联盟原版里剑始终握在肩旁或胸前，手臂连着肩膀。
> 这一轮：**只重画下面 18 帧**，每帧的上半身（两只手臂、握剑的手、剑、肩膀、上身倾斜）**照英雄联盟原版同一帧**（`lol40/`，已按 40 行的大小渲染好，并且放在我们自己的格子和站位点上，可以直接对齐描）；其他帧一格都不改。受影响动作的特效，只改这些帧的格子，让刀光跟着新的剑走。
> 交回：`strips/riven_<动作>.png`（下表 7 张，整条，未列出的帧和 `now/` 逐格一样）、`effects/riven_fx_<组>_<back|front>.png`（改过的组）、`manifest.json`（改过的每一帧的 `head_origin`、`head_rotation_clockwise`、`sword`）、`HANDOFF.md`。

## 附图

| 文件 | 内容 | 用法 |
|---|---|---|
| `design/riven_native.png` | 40 行定稿，8 倍 | **第一张图**：大小、颜色、头、衣服、手臂粗细、断剑、像素风格全照它 |
| `cards/<序号>_<动作>_<帧>.png` | 每帧一张卡：原版 / 原版分色 / 现在 / 原版轮廓（品红）叠在现在上 | **每帧照它画**：上半身和剑照原版，品红轮廓是原版人在这一格里的位置和大小 |
| `lol40/riven_lol_<动作>.png`、`riven_parts_<动作>.png` | 原版整条动作（40 行大小，我们的格子和站位点），分色图红=头、绿=剑、蓝=身体 | 看前后帧怎么衔接；剑的角度、手的位置看分色图最清楚 |
| `now/riven_<动作>.png` | 现在的 7 条动作（40 行，8 倍，透明底） | 在它上面改：只动列出的帧，其他帧原样保留 |
| `design/head_master_1x.png` | 每帧贴的头（24×16） | 原样贴，不改 |
| `fx_now/` | 现在的特效图层 | 改过的帧里刀光跟着新剑重画 |
| `riven_cells.json` | 每帧站位点和时长 | 不变 |
| `problems.png` | 18 帧一览：左原版，右现在 | 总览 |

## 要重画的 18 帧

| 序号 | 文件 | 帧 | 现在的问题 |
|---|---|---|---|
| 01 | `riven_attack.png`（普攻） | 第 1 帧 | 剑压在头顶，没有手和手臂 |
| 02 | `riven_attack.png`（普攻） | 第 2 帧 | 剑举过头顶，靠一根 1 格细杆连在头上 |
| 03 | `riven_skill.png`（Q1） | 第 5 帧 | 剑和手断开，整把剑浮在右边 |
| 04 | `riven_skill.png`（Q1） | 第 6 帧 | 剑和手断开，整把剑浮在右边 |
| 05 | `riven_q2.png`（Q2） | 第 3 帧 | 后面那只手是一根 1 格细线 |
| 06 | `riven_q2.png`（Q2） | 第 5 帧 | 后面那只手细得像棍子 |
| 07 | `riven_q2.png`（Q2） | 第 6 帧 | 后面那只手细得像棍子 |
| 08 | `riven_q3.png`（Q3） | 第 2 帧 | 剑在头顶上方，手臂横在头上 |
| 09 | `riven_q3.png`（Q3） | 第 3 帧 | 剑在头顶上方，手臂横在头上 |
| 10 | `riven_q3.png`（Q3） | 第 4 帧 | 剑在头顶上方，手臂横在头上 |
| 11 | `riven_skill2.png`（E+W） | 第 5 帧 | 手搭在头顶上，没有手臂 |
| 12 | `riven_skill2.png`（E+W） | 第 6 帧 | 手搭在头顶上，没有手臂 |
| 13 | `riven_skill2.png`（E+W） | 第 7 帧 | 握剑的手臂藏在头后面 |
| 14 | `riven_ult.png`（R 开启） | 第 1 帧 | 剑压在头顶，没有手和手臂 |
| 15 | `riven_ult.png`（R 开启） | 第 2 帧 | 剑横在头顶上，手悬空 |
| 16 | `riven_ult.png`（R 开启） | 第 3 帧 | 剑横在头顶上，手悬空 |
| 17 | `riven_r_slash.png`（疾风斩） | 第 1 帧 | 握柄贴在头顶左边，看不到手臂 |
| 18 | `riven_r_slash.png`（疾风斩） | 第 2 帧 | 剑在头顶左上，手臂从头后伸出 |

## 硬性要求（交回前逐帧自查）

1. **剑永远握在看得见的手里**：一只拳头握住剑柄，拳头连着手臂，手臂连到肩膀。不允许手或剑悬空，不允许剑和手之间有空隙，不允许靠头发、细杆把剑“粘”在头上。
2. **握剑的手不在头顶上**：照原版，手在肩旁、下巴旁或胸前；手臂被头挡住时，拳头也要紧挨着肩膀或脖子，像原版一样。
3. **手臂和定稿一样粗**：连描边 3–4 格宽，决不能是 1 格的线；前臂、上臂的形状照原版分色图的蓝色。
4. **脖子照定稿**：下巴下面最多 2 行皮肤、2–3 格宽，左右接肩膀或衣领，不要 1 格宽的细脖子。
5. **每帧是一整块**：除了死亡倒地时落地的剑，人、手臂、剑连成一个整体，没有分离的碎块。
6. **头每帧原样贴** `design/head_master_1x.png`，不重画、不缩放；两只眼睛各 2×2 同一行，眼睛三色只用在眼睛上；3/4 正面朝右，不画背影。
7. 只用定稿的 27 种颜色：#1C0903 #1E1319 #24181F #2D1D1C #272720 #163A22 #293828 #3F2A24 #493328 #593C2C #434A46 #68432C #426E3B #7E4F30 #3E8E48 #996B3D #A8643F #867469 #CB8053 #C79860 #A89588 #E39F6B #BBAA9C #D0BFB0 #FBC697 #F6EADB #FFFFFF；8×8 纯色块；透明度只有 0 和 255；一圈描边；脚底线（站位点下方第 11 行）以下不能有像素。
8. 剑是定稿里的断剑，大小不变（R 的绿色能量大剑我这边画，不要画进动作里）。
9. **不改的帧逐格保持原样**；腿和人在格子里的位置尽量保持现在的，让改过的帧和前后帧接得上；要改腿时照原版。

```text
Attached: FIRST the approved 40-row pixel-art design of this character at 8x (every pixel an 8x8 block) - copy its size, colors, head, clothes, arm thickness, broken sword and pixel style exactly. For each listed frame, a card: League's original frame rendered at this sprite's size in the same cell and standing point, its parts (red head, green sword, blue body), the frame now, and League's outline (magenta) over the frame now.
Task: redraw ONLY the listed frames in the strips under now/, every other frame kept square for square. In each listed frame redraw the upper body after League's frame: both arms, the hand holding the sword, the sword's place and angle, the shoulders and the lean of the torso; keep the legs and her place in the cell unless League's frame needs them changed, so the frame flows with its neighbours.
Hard rules: the sword is always held in a visible fist, the fist joined to an arm that runs to the shoulder - no floating hand, no gap between sword and hand, no sword glued to the head by hair or a rod; the sword hand is never on top of the head: by the shoulder, the chin or the chest like League (when the arm is behind the head the fist still sits right by the shoulder or neck); arms 3-4 squares wide with the outline like the design, never a 1-square line; under the chin at most 2 rows of neck, 2-3 squares wide, joined to the shoulders or collar; every frame one connected piece.
Head: paste design/head_master_1x.png unchanged into every frame (record head_origin), eyes 2x2 on one row, the three eye colors only in the eyes, 3/4 FRONT view facing right. Only the design's colors, one outline, every pixel an 8x8 block, alpha 0 or 255, nothing below the feet line (11 squares under the standing point). The sword is the design's broken sword at its size; no green energy blade.
```

## 特效

- Q1 → `riven_skill`，Q2 → `riven_q2`，Q3 → `riven_q3`，E、W → `riven_skill2`，R 开启 → `riven_ult`，疾风斩 → `riven_r_slash`。
- 只改重画过的帧的格子：刀光、剑身绿光跟着新的剑走，样子、颜色、前后层照 `fx_now/` 现在的；其他帧的格子原样保留。
- 颜色和上次一样（`#F6EADB` `#C9EF9A` `#87D46A` `#4BA85A` `#2D6940`，Q3 碎石加 `#867469` `#493328`）；不描深色边；头的范围只放后层。

## manifest.json

每个改过的帧记：`head_origin`（头贴左上角，格子里的游戏像素坐标）、`head_rotation_clockwise`、`sword`：`{"broken_end": [x, y], "direction": [dx, dy]}`，断口（锯齿端）中点和从剑柄指向断口的单位向量；看不见剑写 `null`。

## 交回前自查

- 18 帧逐帧对照卡片：剑、握剑的手、两只手臂的位置和原版一致，品红轮廓内外没有多出的部分。
- 每帧连成一块（可以用连通区域检查），没有悬空的手或剑；手臂没有 1 格细线；脖子不超过 2 行。
- 未列出的帧和 `now/` 逐格相同；颜色、透明度、8×8 方块、脚底线都合规。
