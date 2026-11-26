# 图奇跑步的弩重画：给 Codex 的提示词（改你上次交的 2 张图）

> 用户 2026-11-22：「让 Codex 重画弩」。
>
> - 你上次交的图奇跑步 8 帧（`templates/run_1.png`、`run_2.png` 就是你交的那两张，只多了蓝色标记）动作都好，**只有弩画短了**：
>   附图 3 是第 3 帧叠上设计图弩的轮廓（蓝线）。头完全重合，弩尖却短了约 10 格：设计图的弩从握弩的手到弩尖约 55 格，你画的约 45 格。
> - **这次只改弩**：照附图 2（设计图的弩单独放大）的形状、大小和长度重画每帧的弩。**握把和握弩的手不动**，弩尖伸到每格里那根
>   **蓝竖线**（蓝色虚线从你现在的弩尖连过去）。弩的朝向照你画的：平端朝右，跟着身子上下。弩上的绿药罐、弩箭、金色弩臂都照设计图。
> - **别的一格都不要动**：头、身子、背包、斗篷、腿、手、尾巴，还有每帧的位置，都和你交的一模一样。
> - 交回前把蓝色标记去掉。交回时附 `HANDOFF.md`。

## 画法规矩

- **一格 8 像素**，对齐模板（你交的图）的网格；硬边、没有抗锯齿、没有模糊和柔光。
- **颜色只用附图 1 里有的颜色**；弩外面一圈是设计里那圈近黑的描边。
- **背景真透明**（每个像素透明度只有 0 或 255）。不要画网格线、格子边框、编号、地面线、影子、蓝色标记。
- 不要缩放或裁剪：交付的图和模板一样大（每张 2048×1920，2×2 格，每格 1024×960）。

## 提示词

```text
Edit the two attached sprite sheets (images 4 and 5: your own Twitch run, 8 frames, 2048x1920 each, 2x2 cells of 1024x960,
8x8-pixel squares) - change ONLY the crossbow. In every frame the crossbow is drawn too short: image 3 shows frame 3 with
the design's crossbow outlined in blue - the head matches exactly, but the crossbow's tip stops about 10 squares short
(the design's crossbow is about 55 squares from the gripping hand to the tip, yours about 45).
Redraw the crossbow in every frame with the exact shape, size and length of image 2 (the design's crossbow, 8x): the grip
and the hand holding it stay where they are; the tip reaches the BLUE vertical line in that cell (the dashed blue line
runs from your current tip to it). Keep the crossbow's direction as you drew it (held level, pointing right, moving with
the body). The green chem tank, the bolt and the golden limbs as in image 2.
Do not change anything else: the head, body, backpack, cloak, legs, hands, tail and the position of every frame stay
exactly as in your sheets. Remove the blue marks.
THE PIXEL GRID: every square exactly 8x8 px on the same grid as the sheets, hard edges, no anti-aliasing, no blur; the
near-black outline of image 1 around the crossbow; only the colours of image 1.
Output: two images exactly like the attached sheets, 2048x1920 each, same layout (run_1 = frames 1-4, run_2 = frames 5-8).
Transparent background (every pixel fully transparent or fully opaque). No grid lines, borders, numbers, ground line,
shadow or blue marks.
```

## 附图（在压缩包 `twitch_bow_pack.zip` 里，按顺序附上）

| 文件 | 内容 | 用在 |
|---|---|---|
| `refs/1_twitch_design_8x.png` | 图奇定稿设计（8 倍） | 颜色、描边 |
| `refs/2_crossbow_design_8x.png` | 设计图的弩单独放大（连握弩的手和绿药罐） | **弩就照它**：形状、大小、长度 |
| `refs/3_crossbow_too_short_frame3.png` | 你的第 3 帧叠上设计图弩的轮廓（蓝） | 短了多少 |
| `templates/run_1.png` | 你交的第 1–4 帧 + 蓝色标记 | 改这张：弩尖伸到蓝竖线 |
| `templates/run_2.png` | 你交的第 5–8 帧 + 蓝色标记 | 同上 |

## 交回前请检查

- 两张图都是 2048×1920、2×2 格、和你上次交的排法一样；真透明背景；一格 8 像素、对齐同一张网格；没有蓝色标记。
- 每帧的弩和附图 2 一样：形状、大小、颜色，从握弩的手到弩尖约 55 格，弩尖到蓝竖线；握把和手没挪。
- 除了弩（和挡在弩前后的那一小块），每帧别的方块和你上次交的一模一样。
- 交付放 `outputs/twitch-bow/`：`run_1.png`、`run_2.png`，原始生成图放 `raw/`，最后写 `HANDOFF.md`，打包成 `outputs/twitch_bow_done.zip`。

## Claude 收到后（给 Claude 看）

- 新图放 `assets/source/twitch/codex_run/`（旧的两张留作 `run_*_v1.png`），`tools/art/read_twitch_run.py` 照样读回、理黑边。
- 先和上次那两张逐格比：只该弩那一带变；别处变了要说清楚。再按护目镜把设计图对上去量弩的长度（第 2、3、7 帧上次短 9-11 格）。
- `C:/t/tw_run_work/tools/pipeline.sh` 重走一遍（只变 run / hd_run / lo_run），「现在 | 上次 | 这次」逐像素动图给用户看，点头才装。
