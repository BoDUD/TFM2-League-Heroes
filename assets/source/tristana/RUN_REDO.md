# 崔丝塔娜：重画跑步（给 Codex 的提示词）

> **为什么重画**：用户在游戏里看了说「跑动的时候头和身体不协调」。上一轮的动作包要求「移动时头相对站位点的横向位置每帧不变」，参考图也是按待机的头渲染的，所以 8 帧跑步里头一直钉在待机的位置，身体在下面前倾、蹦着跑——头像是浮在身体上滑动。英雄联盟原版跑步是**整个人往前倾着、一蹦一蹦地跑**，头比待机靠前约 10 格，跟着每一跳起落。
> **这一轮只重画跑步 8 帧**，其他动作不动。崔丝塔娜已经从 41 行缩到 **34 行**（用户说她是约德尔人、太大了），造型图 `design/tristana_design.png` 就是缩好的定稿：护目镜顶到脚底 34 格，连炮 46 格宽，26 色。**照它的大小和样子画，不要再改造型。**
> - `current/tristana_run_current.png` 是现在的跑步（**错的那版**），`current/run_now_vs_league.gif` 是它和英雄联盟原版并排播放：左边头不动、身体在下面跑；右边整个人一起前倾、起落。
> - 帧数、每帧时长、站位照 `now/tristana_now_run.png`（这次按 34 行、头跟着身体渲染的）；身体和头的动作照 `pose/lol_pose_run.png`；长相照造型图。
> - 交回 `tristana_run.png`（放大 8 倍，3072×1536）和原尺寸的 `native/tristana_run_1x.png`，附 `HANDOFF.md`、`manifest.json`（每帧的格子矩形、站位点、不透明范围、头贴在哪里）、`generation_prompts.json`，打成一个 zip。

## 这一轮的关键要求（和上一轮不一样的地方）

1. **头跟着身体走，头和躯干是一个整体**：每一帧头都正好坐在肩膀上（脖子的位置每帧一样），身体前倾时头一起往前，身体随跳跃上下时头一起上下；头和躯干之间的相对位置 8 帧都一样，**头不能在身体上滑动**。
2. **前倾**：照第三张图，整个上半身（头、躯干、手臂、炮）往前倾，头在臀部前面 2–4 格；落地的帧低一点、腾空的帧高一点（上下起伏 2–4 格，照第二张图每帧的高度）。
3. **头还是造型图的头**：护目镜、白发、两只大耳朵（含耳环）、脸、眼睛、嘴逐格照搬 `design/tristana_head_1x.png`（128×128 画布上的范围 x 43–77、y 66–82），**只平移，不旋转、不重画**；跑动的颠簸靠头整体上下前后移动表现。
4. **炮的拿法照第三张图**：两只手端着短粗炮，炮口朝前、略向下斜（参考图里炮身斜在身前），炮跟着身体一起起落；仍然是造型图的**短粗炮**（钢蓝八角炮口、刻 X 的铜箍、钢蓝炮尾），不要画长；不能挡脸。
5. **两条腿交替**：前 4 帧一步、后 4 帧另一步（近腿在前一半、远腿在前一半，中间膝盖交错），短腿、脚掌踩在脚底线上；首尾无缝循环。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/tristana_design.png` | **定稿造型（34 行）**，放大 8 倍 | 第一张附图 |
| `design/tristana_design_1x.png` | 同一张，原尺寸（128×128） | 色板、贴头 |
| `design/tristana_head.png`、`_1x.png` | 要贴进每一帧的头 | 贴头 |
| `design/tristana_palette.png` | 造型图的全部 26 色 | 色板 |
| `tristana_idle.png` | 34 行的待机条（已做好） | 看大小和站位 |
| `now/tristana_now_run.png` | 英雄联盟原版跑步按游戏尺寸取色（34 行，头跟着身体），放大 8 倍 | 第二张附图：帧数、时机、站位、每帧高低 |
| `pose/lol_pose_run.png` | 同一帧的高清渲染 | 第三张附图：前倾、步伐、炮的拿法 |
| `current/tristana_run_current.png`、`run_now_vs_league.gif` | 现在的跑步（错的）和它与原版的对比 | 看清楚要改什么 |
| `guide/tristana_guide_run.png` | 格子、站位点（蓝十字）、脚底线（红线）和红线下的禁区 | 对位，不要画进图里 |
| `tristana_cells.json` | 跑步每帧的站位点和时长 | 整理对位 |

## 规则

- 像素：每个像素一个 8×8 方块，对齐同一网格，没有抗锯齿、模糊、半透明；站着时 34 格高（护目镜顶到脚底），跑动时整体高度随起伏变化但身体比例不变。
- 只用造型图的 26 色，不加新颜色；1 格近黑外描边；明暗照定稿；没有碎点；手臂至少 3 格宽、连在身上；身体、手臂、大炮连成一个整体。
- 头每帧都是造型图的头（逐格一样，只平移）；琥珀色 `#F6BA30` 只出现在眼睛上。
- 脚底线以下什么都不能有（游戏在脚下画血条）：每格最低一行是第 81 行（像素 648–655），炮也不能低于它。
- 3/4 正面朝右，不画背影；只画角色，不画尘土、速度线等特效。
- 排版和 `now/tristana_now_run.png` 完全一样：4 列 × 2 行，每格 96×96 方块（768×768 像素），图片 3072×1536，帧 N 在同一格；背景透明（做不到用纯品红 `#FF00FF`）。

## 提示词（附三张图：第一张 `design/tristana_design.png`，第二张 `now/tristana_now_run.png`，第三张 `pose/lol_pose_run.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block), 34 squares tall from the top of the goggles to the soles - copy its colors, shapes, goggles, hair, ears, face, cannon and pixel style exactly; do not redesign anything. SECOND: the original run sampled at game size at 8x, 8 frames in a 4x2 grid read left to right, top to bottom - copy the number of frames, where the character stands in each cell and how high she is in each frame (the hops), but NOT its blurry look. THIRD: the original 3D run at the same frames - copy the motion: the whole body leaning forward, the hops, the stride and how both hands carry the cannon.
The character: Tristana, a small cheerful yordle gunner (lavender skin, fluffy white hair, huge pointed ears pink inside with a brass ring, two tall red-and-brass goggle cups pushed up on her head, big amber eyes, an olive vest over a tan shirt, olive shorts, quilted brown leather sleeves and leg wraps, a red cuff, bare lavender feet) with a short, thick bronze cannon (two X-engraved brass bands, a steel-blue octagonal muzzle, a steel-blue rear cap).
Task: a MOVE loop, 8 frames, one seamless cycle of her bouncy run (8 x 117 ms). THE MOST IMPORTANT RULE: the head moves WITH the body. The head and the torso are one piece: in every frame the head sits on the shoulders at the same neck joint, so when the body leans forward the head goes forward with it and when she hops up or lands the head rises and drops with the body by the same amount. Never keep the head in one place while the body moves under it. Her whole upper body (head, torso, arms, cannon) leans forward as in the THIRD image, the head 2 to 4 squares ahead of the hips; she is lower on the landing frames and higher on the airborne ones (2 to 4 squares of bounce, following the SECOND image). The legs ALTERNATE: frames 1-4 one stride, frames 5-8 the other (the near leg forward in one half, the far leg in the other, the knees passing each other in between); short legs, feet on the feet line when they touch the ground. Both hands carry the cannon as in the THIRD image - in front of her body, the muzzle forward and a little down - and it rises and drops with her; it is the FIRST image's SHORT, THICK cannon, never longer, never covering her face. The ears and hair are part of the copied head. Frame 8 flows into frame 1.
The head (the two goggle cups and their strap, the white hair, both huge ears with the brass ring, the face with the eyes and the mouth) is COPIED from the FIRST image in every frame, square for square, and only MOVED - never rotated, never redrawn. Her eyes are the FIRST image's eyes, both the same size on the same rows; the amber #F6BA30 appears ONLY in the eyes.
Pixel rules: every pixel one crisp 8x8 square on a single 8-px grid, nothing smaller, no anti-aliasing, no blur, no semi-transparency. ONLY the 26 colors of the FIRST image: #191421 #442A23 #283447 #41492D #821D3F #734832 #87602E #445E80 #727745 #D13845 #A36A43 #835B9E #C35C80 #7E879E #C8994E #A3A26B #CE9560 #7397C3 #F6BA30 #B889D1 #E6BF86 #F699B4 #BFCCD8 #DFB4EB #B9DDED #FFF4E4. ONE 1-square near-black outline around the silhouette; each material's own dark shade inside; copy the FIRST image's shading; no dithering, no noise, no specks. Arms at least 3 squares wide, joined to the body; no loose pieces.
Feet line: in every cell the lowest row of her feet is square row 81 from the top of the cell (pixels 648 to 655); NOTHING from pixel 656 down, not the cannon either. Her place across each cell follows the SECOND image (the standing points are in tristana_cells.json). 3/4 front view facing right, never her back. Only the character - no dust, no speed lines.
Layout: exactly like the SECOND image - 4 columns x 2 rows, each cell 96x96 squares (768x768 px), 3072x1536 pixels, frame N in the same cell. Transparent background (if not possible: solid #FF00FF magenta). No grid lines, borders, labels or guide marks.
Before finishing, check: every square 8x8 on one grid; only the FIRST image's colors; the head identical to the FIRST image in every frame and sitting on the shoulders in every frame (the same neck joint); the upper body leaning forward with the head ahead of the hips; the head rising and dropping with the body; the legs alternating; the short thick cannon in both hands; nothing below the feet line; frames in the same cells as the SECOND image.
```

## 交回前自查

- [ ] 图片 3072×1536，4×2 格，帧 N 和 now 条在同一格；严格 8×8 方块，透明度只有 0 和 255；
- [ ] 只用造型图色板（逐像素比对），琥珀色只在眼睛上；
- [ ] **每一帧头都坐在肩膀上**（脖子位置和躯干的相对位置 8 帧一样），上半身前倾、头在臀部前面 2–4 格，头跟着身体一起起落；
- [ ] 头是造型图的头逐格照搬，只平移、没有旋转或重画；
- [ ] 两条腿交替，首尾能接上；短粗炮在两只手里、跟着身体动、不挡脸；
- [ ] 脚底线以下没有任何像素；手臂至少 3 格宽，没有碎块；没有背影、没有特效、没有网格文字。

## Claude 导入时（给 Claude 看）

- 检查（方块、二值透明、色板、脚底线、琥珀色只在眼睛、连通块、两腿交替、头和躯干的相对位置每帧一样），然后放进 `assets/source/native/tristana_run.png`（34 行，不再经过 `shrink_tristana.py`），`tristana_cells.json` 的跑步条目换成包里这份。
- `import_native.py --hero tristana`：跑步的 EYES 稳头要关掉或改成跟着身体（这次头本来就该前后起落）；COMPLETE 补描边；NECK 检查脖子每帧同一行。
- 做「我们 vs 英雄联盟」的对比 GIF 给用户看，重做演示 GIF 并重新固定 PR 里的链接。
