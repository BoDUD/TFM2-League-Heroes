# 剑姬：重画走路的上半身，头和身体连成一体（给 Codex 的提示词）

> 用户在游戏里看剑姬走路：「**头和身体不协调**」。原因：上次交回的走路（腿已经交替，很好）里，头是按定稿的高度贴上去的，可定稿是弓步站姿（矮），
> 走路是直起身的（高 3 行），于是**下巴直接压在领口和举剑的手臂上**（眼睛到白衬衫只有 5 行、第 6–8 帧 4 行，定稿是 8 行），
> 而且**身体每帧上下起伏、头却钉在同一处不动**，看起来头在身体上滑。Claude 用像素把头往上搬了 2–3 行、补了定稿的脖子和高领，用户看了「还是有点怪」，
> 所以请重画：**头、脖子、高领、肩膀、手臂上段、披风顶端**画成一个整体，头**坐在**肩膀上、**跟着身体一起**起伏。
> - **不用改的**：两条腿（交替的步子是对的）、披风下半、平举的细剑（1 格、不描边的直线）、每帧在格子里的位置和大小、8 帧 × 114 毫秒、排版（4 列 × 2 行，3840×1792）。
> - **头**还是定稿的头（脸、眼睛、头发逐格照抄），只是位置跟着身体走。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/fiora_design.png` | 定稿造型，放大 8 倍 | 第一张附图：头、脖子、金色高领、肩膀怎么连在一起（**眼睛到白衬衫 8 格，下巴下面 3 格宽的脖子嵌在高领里**） |
| `fiora_run_current.png` | 你上次交回的走路（8 帧，放大 8 倍） | 第二张附图：**腿、披风下半、细剑、位置照它**，上半身重画 |
| `guide/head_height.png` | Claude 拼的示意：每帧的头该在多高（第 1–5 帧比上次高 2 格、第 6–8 帧高 3 格，下巴下面是定稿的脖子和高领），和上次同样的格子 | 第三张附图：**只看头和脖子的高度**；画法以定稿为准，接缝要画顺 |
| `guide/problem.png` | 放大对照：定稿、上次的第 1 帧和第 6 帧（下巴压在领口上）、Claude 拼的（用户说还是怪） | 看问题在哪 |
| `pose/lol_pose_run.png`、`guide/lol_run_legs.png`、`guide/fiora_guide_run.png`、`fiora_cells.json` | 上次给过的英雄联盟走路参考、腿的指引、格子 | 身体动作、对位 |

## 每帧的头（最重要）

| 帧 | 身体 | 头 |
|---|---|---|
| 1–5 | 和上次一样 | 比上次高 **2 格**，坐在肩膀上：下巴下面是定稿那样的短脖子（3 格宽），被金色高领围住，眼睛到白衬衫 8 格 |
| 6–8 | 上次的身体在这 3 帧比前 5 帧高 1 格 | 比上次高 **3 格**（跟着身体高上去的那 1 格），脖子长度和 1–5 帧完全一样 |

头**不能**每帧钉在同一处：身体起伏多少，头就跟着起伏多少；脖子长度每帧一样，不伸长不缩短。肩膀、高领、举剑手臂的上段、披风的顶端要接在脖子上、画顺，不要看得出是贴上去的。

## 提示词（附三张图：`design/fiora_design.png`、`fiora_run_current.png`、`guide/head_height.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block): her head, face, hair, the short neck inside the tall gold collar, the shoulders - exactly how her head sits on her body. SECOND: her current 8-frame walk at 8x in a 4x2 grid of 120x112-square cells. THIRD: the same cells with the head moved to the height it must have in each frame (a rough guide made by moving pixels; follow it for the height only).
The problem to fix in the SECOND image: the head was pasted at the FIRST image's height, but the FIRST image stands crouched en garde and the walk stands upright, so in the walk her chin sinks onto the collar and the raised sword arm (the eyes are only 5 squares above the white shirt, 4 in frames 6-8, against 8 in the FIRST image), and the head stays still while the shoulders rise and fall, so the head seems to slide on the body.
Redraw the upper body of every frame as ONE figure: the head sits ON the shoulders exactly as in the FIRST image - the same short neck (3 squares wide) wrapped by the tall gold collar under the chin, 8 squares from the eyes down to the white shirt. Frames 1-5: the head 2 squares higher than in the SECOND image; frames 6-8: 3 squares higher (the body is 1 square higher there), so the head rises and falls with the shoulders and the neck is the same length in every frame. Draw the gold collar, the shoulders, the upper part of the raised sword arm and the top of the cape so they join the neck naturally - no gap, no seam, nothing that looks pasted.
The head itself is the FIRST image's head copied square for square (the same face, eyes, hair and outline) - only its place changes. Keep from the SECOND image: both legs (the alternating stride), the lower cape streaming behind, the level rapier (a straight bare 1-square line, no outline), each frame's size and place in its cell.
Pixel rules: exactly the FIRST image's pixel size, every pixel one crisp 8x8 square on one 8-px grid, no anti-aliasing, no blur, no semi-transparency, ONLY the FIRST image's 25 colors, a 1-square near-black outline round the silhouette and each material's own dark shade inside it, big flat areas, no dithering or noise.
Feet line: the lowest row of her feet is square row 97 of each cell; nothing from row 98 down. Layout: exactly like the SECOND image - 4 columns x 2 rows of 120x112-square cells, 3840x1792 pixels, frame N in the same cell; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
```

## 交回（`fiora_run_redo2.zip`）

- `fiora_run.png`：整理后的走路（放大 8 倍，3840×1792，定稿的头逐格照抄，细剑 1 格直线）；
- `logical/fiora_run_1x.png`：同一张 1 倍逻辑像素版；
- 生图原稿（`generated_sources/`）、`HANDOFF.md`：用了哪条提示词、哪里没做到。

## 交回前自查

- [ ] 每帧眼睛到白衬衫 8 格，下巴下面是 3 格宽的脖子、被金色高领围住——和定稿一样；
- [ ] 第 1–5 帧头比上次高 2 格、第 6–8 帧高 3 格，头跟着身体起伏，脖子长度每帧一样；
- [ ] 肩膀、高领、手臂上段、披风顶端和脖子接得顺，看不出贴图的接缝；
- [ ] 腿、披风下半、细剑、位置和上次一样；每帧都有一只脚在脚底线上，脚底线以下没有任何像素；
- [ ] 每个像素是严格对齐的 8×8 纯色块，透明度只有 0 和 255，只用造型图的 25 色；每帧连成一块。
