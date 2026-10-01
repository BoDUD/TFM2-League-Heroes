# 菲兹：移动只改三叉戟（给 Codex 的提示词）

> 上次交回的移动返修（`fizz_run_redo.zip`）**身体、两条腿、空手、头都通过了，不要动**。用户看了说三叉戟还不对，选了「只再修三叉戟」：
> - 现在三叉戟用的是 55 格全长，整根放在身后：叉头在后脚边（像拖在后面），杆尾往左上伸出去 30 多格、最高到第 43 行。
> - 要改成：**总长约 40 格**（把杆子缩短，叉头和金环大小不变），**叉头在身前脚边、杆尾在后肩上方**，不再往后伸那么远。
> - 英雄联盟里三叉戟像钟摆：杆尾一直在后肩后面，叉头第 1–3、8 帧摆到前面的脚边，第 4–7 帧摆回身体下面。因为我们的头比原版大，原版那么陡的角度会让杆子整根藏到头后面，所以角度放平一些（26–55°），让杆子从头下面或头旁边露出来。

## 附图

| 文件 | 内容 | 用在 |
|---|---|---|
| `fizz_run_redo.png`、`fizz_run_redo_1x.png` | 你上次交回的移动（8 倍 / 1 倍） | **底稿：身体、腿、空手、头逐像素保留** |
| `guide/trident_plan.png`、`guide/trident_plan_1x.png` | 示意：三叉戟缩到 40 格、按下表摆好、近腿膝盖以下压在叉头上、头在最上面 | **每帧三叉戟的位置、角度、长短、前后关系照它**；但它的叉头是最近邻旋转出来的碎点，**像素不要照抄** |
| `guide/trident_targets.png` | 示意图上标出：红点 = 中间齿的尖，黄点 = 金环末端，青点 = 握点，粉线 = 杆的中线 | 对位 |
| `guide/trident_targets.json` | 每帧的角度、中间齿尖、金环末端、握点、外框、最低行（1 倍格子坐标） | 精确数值 |
| `guide/redo_vs_plan_2x.png` | 上排返修版、下排示意，2 倍（接近游戏里的大小） | 看改完的整体效果 |
| `trident/trident_40.png`、`trident/trident_55.png` | 40 格版（杆子去掉 15 格）和原来的 55 格版，水平放着，8 倍 | 三叉戟的造型和长度 |
| `guide/lol_run_parts.png`、`pose/lol_pose_run.png` | 英雄联盟的移动：部位分色（三叉戟绿色）和高清渲染 | 三叉戟的摆动 |
| `design/fizz_design.png` | 定稿造型 | 颜色、材质 |
| `fizz_cells.json` | 格子、站位点、时间 | 和上次一样 |

## 每帧目标（1 倍格子坐标，格子 112×112，脚底线第 97 行）

| 帧 | 角度 | 中间齿尖 | 金环末端 | 握点 | 叉头在哪 |
|---|---|---|---|---|---|
| 1 | 28° | (69, 92) | (34, 74) | (55, 85) | 前脚边 |
| 2 | 26° | (71, 91.5) | (36, 74.5) | (57, 85) | 前脚边 |
| 3 | 32° | (72, 92) | (39, 72) | (58, 84) | 前脚边 |
| 4 | 45° | (67, 94) | (40, 66) | (56, 82) | 两脚之间 |
| 5 | 55° | (64, 95) | (41, 63) | (55, 82) | 身体下面 |
| 6 | 52° | (62.2, 93.8) | (38.8, 64.2) | (52, 81) | 身体下面 |
| 7 | 45° | (62, 94) | (35, 66) | (51, 82) | 身体下面 |
| 8 | 36° | (65, 93) | (34, 71) | (52, 84) | 两脚之间偏前 |

角度是杆子和水平线的夹角（叉头在右下、金环在左上）。各点允许 ±1 格，整体观感照 `guide/trident_plan.png`。

## 规则

- **只改三叉戟和握戟的那只手**：身体、两条腿、空手、头和返修版逐像素一样（三叉戟原来盖住的地方，按返修版的画法把被挡住的腿和身体补回来）；握戟的手挪到杆上（青点），前臂从原来的肩膀接过去，手至少 2×2、手臂至少 3 格粗。
- **三叉戟总长 40 格**：金环 9 格 + 杆 + 叉头 15 格，就是 `trident/trident_40.png` 那样——只缩杆子，叉头、金环、蓝宝石大小不变。
- **前后关系（从后到前）**：远腿 → 身体 → 三叉戟 → 近腿膝盖以下 → 握戟的手 → 头。近腿压在叉头上（近腿离镜头最近），**头永远在最上面**，三叉戟被头挡住的那段就不画。
- **叉头每帧按角度重新画干净**：三根齿是分开的、各 1 格宽的玉绿色线加描边，中间那根最长、两边的往外弯；齿的外缘一格浅钢色，根部一颗蓝宝石。不要旋转出来的碎点、断线、孤立的白点；叉头和腿交叠的地方，两者的描边要分得清，不要糊成一块黑。
- **杆子**：1 格深红加两侧近黑描边，一格一格连着的直线，不断开、不弯；金环照定稿。
- 叉头最低一格在第 96 行，第 97 行往下没有三叉戟（脚底线 97 行是脚的）。
- 只用造型图的 23 种颜色；每个像素一个严格对齐的 8×8 方块，透明度只有 0 和 255；每帧连成一块；外轮廓 1 格近黑描边。
- 8 帧的格子、站位点、时间（7 × 107 + 108 毫秒）都不变。

## 英文说明（如果要用图像模型画叉头）

```text
Keep every pixel of the attached run sprite sheet (fizz_run_redo.png) except the trident and the hand that holds it.
Redraw the trident in each of the 8 frames as placed in guide/trident_plan.png and guide/trident_targets.json: 40 squares
long (the design's gold ring end, a shorter crimson shaft, the same jade three-prong head), the prongs down in front by
his feet, the gold ring end up behind his shoulder. Draw the three prongs cleanly at each angle - three separate jade
tines one square wide with a 1-square near-black outline, the middle one longest, the outer two curving outward, pale
steel edges, a blue gem at the base - never rotation noise. The near leg from the knee down stays in front of the
prongs, the head stays in front of everything. Every pixel one crisp 8x8 square, only the design's 23 colors, alpha 0
or 255, nothing below square row 96 except the feet, each frame one connected piece.
```

## 交回（`fizz_run_trident.zip`，放在 outputs 里）

- `fizz_run.png`：改好的移动（8 倍，3584×1792）；`fizz_run_1x.png`：1 倍版；
- `HANDOFF.md`：做了什么、哪里没做到；`manifest.json`（每帧格子、站位点、bbox、三叉戟的角度/两端/握点）。

## 交回前自查

- [ ] 身体、腿、空手、头和返修版逐像素一样（只多了被旧三叉戟挡住、现在补回来的部分）；
- [ ] 三叉戟每帧 40 格左右，位置和角度和 `guide/trident_targets.json` 差不超过 1 格；叉头第 1–3、8 帧在前脚边，第 4–7 帧在身体下面；
- [ ] 叉头三根齿分得清，没有碎点；杆子一条直线不断；
- [ ] 近腿压在叉头上、头在最上面；握戟的手在杆上；
- [ ] 严格 8×8 方块、0/255 透明度、23 色、每帧连成一块、第 97 行往下没有三叉戟。
