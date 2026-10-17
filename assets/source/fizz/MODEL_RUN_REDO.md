# 菲兹：照英雄联盟重画移动（给 Codex 的提示词）

> 上次交回的 9 张动作条里，**只有移动要重画**，其余 8 张不动。用户看了说「小鱼人移动时候有点奇怪啊 姿势」，看了对照图（`guide/run_now_vs_lol.png`）选了「照原版重画」：
> - 上次的移动把身体压扁在头下面，像蹲着往前爬：两条腿贴着地往两边摊开，三叉戟横在胸口。
> - 英雄联盟的移动是**直着身子小跑**：身体立起来（和待机一样高），两条腿露出来、交替迈步（第 1–4 帧一步、第 5–8 帧另一步，中间两膝交叉），空着的那只手往前伸、手掌张开，**三叉戟斜在身前**——杆尾在后肩上方（画面左上），叉头在前面脚边（画面右下，不能低于脚底线）。
> - **头照旧是定稿的头逐格贴上**（和上次一样，朝向和待机一样，眼睛看右边），头相对站位点的横向位置每帧不变，上下最多起伏 1–2 格；耳鳍可以随着跑步往后飘一点。
> - 8 帧 × 107 毫秒、4 列 × 2 行的格子（3584×1792）、每帧的站位点和脚底线都和上次一样（`fizz_cells.json`、`guide/fizz_guide_run.png`）。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `design/fizz_design.png` | 定稿造型，放大 8 倍 | 第一张附图：颜色、材质、头、三叉戟、像素风格 |
| `guide/lol_run_parts.png` | 英雄联盟的移动，同样的 8 帧、同样的格子：**近腿橙色**（在前面），**远腿蓝色**（在后面），**三叉戟绿色**，头和身体灰色 | 第二张附图：**每帧身体的姿势、两条腿和三叉戟的位置照它** |
| `pose/lol_pose_run.png` | 同一张的高清渲染（原来的样子） | 第三张附图：身体、手臂、三叉戟的样子 |
| `now/fizz_now_run.png` | 同一张按游戏尺寸取的方块 | 看这个尺寸下腿有多粗、多长 |
| `fizz_run_current.png` | 你上次交回的移动（错的，不要照它的姿势） | 只看颜色和贴的头 |
| `guide/run_now_vs_lol.png` | 逐帧对比：灰底英雄联盟，绿底上次的 | 看错在哪 |
| `guide/fizz_guide_run.png`、`fizz_cells.json` | 格子、站位点（蓝十字）、脚底线（红线） | 对位 |

## 规则

- **整个身体重画**（头除外）：身体立起来、和待机一样高（站着从头顶到脚底约 32 格）；腿的长短、粗细照待机（大腿蓝色、小腿和蹼足深海军蓝，每条腿加描边至少 3 格宽）；**两条腿用待机的同一套颜色**，远处的那条可以整体暗一档，但不能换材质、不能一亮一暗地对着打光；每条腿外面一圈 1 格描边，腿里面不要黑线，被挡住的腿不要画成一块黑。
- **两条腿交替**：照 `guide/lol_run_parts.png` 逐帧画近腿（橙）和远腿（蓝）的位置——第 1–4 帧一步、第 5–8 帧换另一条腿，中间有两膝交叉经过的帧；每帧至少有一只脚踩在脚底线上。
- **三叉戟**：长度和造型图一样（约 55 格），斜在身前：杆尾和金环在后肩上方，叉头（三根齿、钢色刃边、蓝宝石）在前面脚边；握在手里（手至少 2×2 格、连着至少 3 格粗的手臂）；**杆尾和叉头都不能低于脚底线**；杆是 1 格深红加上下描边，斜着的时候是一格一格连着的直线，不断开、不弯。
- **空手**往前伸、手掌张开（照参考图），手臂至少 3 格粗。
- **头**：定稿的头逐格贴上，只平移，每帧横向位置相对站位点不变、上下起伏最多 1–2 格；头下面直接接身体和奶黄色的喉咙（喉咙从眼睛最下一行往下第 4 行开始），不要把头压进身体，也不要拉出一截脖子。
- 只用造型图的 23 种颜色；每个像素一个严格对齐的 8×8 方块，透明度只有 0 和 255；每帧连成一块；外轮廓 1 格近黑描边，描边里面用材质自己的暗色。
- 3/4 正面朝右，看得到脸，不画背影；不要水花、灰尘这些特效。

## 提示词（附三张图：`design/fizz_design.png`、`guide/lol_run_parts.png`、`pose/lol_pose_run.png`）

```text
Three attached images. FIRST: the approved, final pixel-art design of this character at 8x (every pixel an 8x8 block) - his colors, materials, head, trident and pixel style. SECOND: the original run, 8 frames in a 4x2 grid of 112x112-square cells, painted by part: the NEAR leg ORANGE (in front, toward the viewer), the FAR leg BLUE (behind), the TRIDENT GREEN, the head and body grey - copy the pose of the body, both legs and the trident in every frame from it. THIRD: the same 8 frames rendered normally - how the body, the arms and the trident look.
Task: redraw his RUN as clean pixel art identical in style to the FIRST image, at exactly the same pixel size (about 32 squares from the crown to the soles), every pixel one crisp 8x8 square on a single 8-px grid, no anti-aliasing, no blur, no semi-transparency.
The run (League's own, 8 frames x 107 ms, one seamless loop): an upright little trot - the body standing as tall as in the FIRST image, NOT squashed or crouched; the two legs long and clearly visible, ALTERNATING like the SECOND image: frames 1-4 one stride, frames 5-8 the other, the knees passing each other in between, one foot on the ground line in every frame; the free arm reaching forward to the right with the hand open; the trident held in the other hand, slanting across the front of him: the round gold butt end up behind his shoulder (image upper left), the jade three-prong head down in front by his feet (image lower right) - never below the feet line; the fin-ears flowing back a little.
The head (crown spots, fin-ears with their orange frills, face, eyes, grin) is COPIED from the FIRST image in every frame, square for square, facing right as in the FIRST image, and only moved: the same horizontal place relative to the standing point in all 8 frames, at most 1-2 squares up or down; the cream throat starts 4 rows under the eyes' lowest row; never sink the head into the body.
Legs: both legs in the FIRST image's leg colours - blue thighs, deep navy-blue shins and big webbed feet - the far leg at most one shade darker, never a different material; each leg at least 3 squares wide with its outline, one 1-square near-black outline round each leg, no black lines inside a leg, a hidden part of a leg simply not drawn (never a black block).
Trident: as long as in the FIRST image (about 55 squares end to end), a crimson shaft ONE square thick with the outline on both sides, a straight unbroken stepped line, the jade three-prong head with pale steel edges and a blue gem, the round gold ring end.
Pixel rules: ONLY the 23 colors of the FIRST image, a 1-square near-black outline round the silhouette and each material's own dark shade inside it, big flat areas, no dithering or noise, the whole figure ONE connected piece in every frame. 3/4 FRONT view facing right, the face always visible. No effects.
Feet line: the lowest row of his feet is square row 97 of each cell; nothing from row 98 down. Layout: 4 columns x 2 rows of 112x112-square cells, 3584x1792 pixels, frame N in the same cell as in the SECOND image, the standing points as in fizz_cells.json; transparent background (if not possible: solid #FF00FF magenta). No grid lines, labels or guide marks.
```

## 交回（`fizz_run_redo.zip`，放在 outputs 里）

- `fizz_run.png`：整理后的移动（放大 8 倍，3584×1792，定稿的头已贴回）；
- `fizz_run_1x.png`：同一张 1 倍逻辑像素版；
- `HANDOFF.md`：用了哪条提示词、哪里没做到；`manifest.json`（每帧的格子、站位点、bbox）。

## 交回前自查

- [ ] 身体立着、和待机一样高，不再蹲着爬；
- [ ] 两条腿交替（第 1–4 帧一步、第 5–8 帧另一步，有两膝交叉的帧），和 `guide/lol_run_parts.png` 逐帧对过；两条腿颜色和待机一样；
- [ ] 三叉戟斜在身前（杆尾在后肩上方、叉头在前面脚边），整根完整、在脚底线以上；空手往前伸；
- [ ] 头是定稿的头，每帧横向位置不变、上下最多 1–2 格，首尾接得上；
- [ ] 严格 8×8 方块、0/255 透明度、只用造型图 23 色、每帧连成一块、脚底线以下没有像素。
