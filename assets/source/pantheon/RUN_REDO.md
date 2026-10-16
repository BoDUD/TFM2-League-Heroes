# 潘森：跑步重画腿（给 Codex 的提示词）

> 你第 2 步交的跑步 8 帧，**上半身很好**（身体前倾、披风往后飘、长矛横握、盾在身前），**只有腿不对**：8 帧都是画面右边那只脚踩在前面、左边那只往后踢，**一直是同一条腿在前**，看起来像单脚往前蹦，没有跑步的交叉步。
> 这一轮**只重画腰带以下的两条腿**（大腿、护胫、凉鞋），其他全部照你上次交的那帧（`now/pantheon_run_<n>.png`）：头盔、上身、手臂、长矛、盾、披风、腰带、蓝布帘都不要动，长矛和盾的样子、位置照旧。
> - **腿的姿势照骨架线**（`guide/pantheon_run_<n>.png`）：**红线 = 近侧的腿**（离看画的人近，颜色亮），**蓝线 = 远侧的腿**（暗一档）。线上的点从上到下是：髋、膝、脚踝、脚尖。
> - **两条腿轮流在前**：第 1–2 帧红腿在前踩地、蓝腿在后踢起；第 3 帧两腿在身体下面交叉而过；第 4–6 帧蓝腿在前踩地、红腿在后踢起；第 7 帧再交叉；第 8 帧红腿往前迈。
> - 踩地的那只脚**脚底贴在红色地面线上**；抬起的那只脚离地，往后踢时小腿往上弯。
> - 腿的样子照造型（`design/pantheon_design.png`）：古铜色大腿、金色分节护胫（亮金高光 + 暗金阴影）、露脚趾的棕色凉鞋；**两条腿一样粗、一样长**，和造型一样（不要画细、不要画长）。**近侧腿画在远侧腿前面**（重叠时挡住它），远侧腿整条暗一档。
> - 腰带下面的**蓝色布帘**还挂在两腿中间，跟着腿稍微摆动。
> - 骨架线的髋点有高有低，那是跑步时身体的上下起伏：**髋点低的帧，整个上半身跟着往下挪**（头盔、上身、矛、盾一起平移，不要变形）。
> - 和上次一样：1536×1536 透明画布，**每格 10 px、对齐同一个网格**，只用造型的 39 色，近黑外描边，没有抖动、渐变、半透明、特效；地面线以下什么都不能有；骨架线、地面线、文字都**不要画进图里**。

## 附图（压缩包 `pantheon_run_pack.zip` 里）

| 文件 | 内容 | 用在 |
|---|---|---|
| `now/pantheon_run_<n>.png` | 你上次交的跑步第 n 帧 | **上半身、长矛、盾、披风原样保留** |
| `guide/pantheon_run_<n>.png` | 同一帧，腰带以下淡化，叠上这一帧的腿部骨架（红 = 近侧腿，蓝 = 远侧腿，红横线 = 地面） | **两条腿的姿势照它** |
| `design/pantheon_design.png` | 造型（10 倍放大，一格 = 一个像素） | 腿、护胫、凉鞋的样子和颜色 |
| `refs/league_pantheon_run.png` | 英雄联盟里潘森的跑步动作（3D 模型） | 跑步的感觉 |
| `legs.json` | 每帧两只脚的位置（格子坐标） | 对照用 |

## 提示词（每帧一次，n = 1…8）

附图顺序：1 `now/pantheon_run_<n>.png`，2 `guide/pantheon_run_<n>.png`，3 `design/pantheon_design.png`，4 你刚画好的第 n−1 帧（第 1 帧不附）。

```text
Image 1 is a pixel-art running frame of this warrior (frame <n> of an 8-frame run loop), drawn on a grid of 10x10-pixel squares on a 1536x1536 transparent canvas. Its upper body is right - the golden helmet, the torso, the arms, the level spear, the round shield, the blue cape, the red rope belt and the blue loincloth - but its LEGS are wrong. Image 2 is the same frame with the legs faded and a SKELETON drawn over them: the RED line is the NEAR leg (closer to the viewer, full tone), the BLUE line is the FAR leg (one shade darker); the dots on each line are hip, knee, ankle, toe; the red horizontal line is the ground. Image 3 is the approved design (10x enlarged: one square = one pixel): how the legs look - bronze-tan thighs, segmented GOLDEN GREAVES (bright gold highlights, dark gold shadows), brown open-toed sandals. (Image 4, when attached, is the frame before this one: keep the legs exactly as thick and long.)
Redraw ONLY THE LEGS below the belt, following Image 2's skeleton exactly: the near leg along the red line, the far leg along the blue line, each foot where its ankle and toe dots are. A foot on the ground stands with its sole ON the red ground line; a lifted foot is off the ground, a leg kicked back bends at the knee. Both legs as thick and as long as in Image 3, never thinner; the near leg drawn OVER the far leg where they overlap, the whole far leg one shade darker. The blue loincloth still hangs between the legs. Keep EVERYTHING ELSE of Image 1 exactly as it is - helmet, body, arms, spear, shield, cape, belt - square for square; only when the hip dots are lower or higher than Image 1's belt, move the whole upper body down or up with them by whole squares (no reshaping).
Same rules as before: the 1536x1536 transparent canvas and the SAME 10-pixel grid, every square one flat colour from the design's 39 colours, a near-black outline, no dithering, no gradients, no semi-transparency, no effects; nothing below the ground line; do NOT draw the skeleton lines, the ground line or any text. Also deliver a 1x copy (one pixel per square) that matches square for square.
```

## 交付（`outputs/pantheon-run/`）

- `pantheon_run_1.png` … `pantheon_run_8.png`（1536×1536）+ 各自的 `_1x.png`（153×153）；原稿放 `raw/`；`HANDOFF.md`（最后写）；打包 `outputs/pantheon_run_done.zip`。

## 交回前请检查

- 8 帧里两条腿**轮流在前**：1–2 红腿在前、4–6 蓝腿在前、3 和 7 交叉；不是 8 帧同一条腿在前。
- 踩地的脚贴着地面线；腿和造型一样粗；远侧腿暗一档；凉鞋露脚趾。
- 上半身、长矛、盾、披风和上次那帧一样（只可能整体上下平移）。
- 没有画进骨架线、地面线、文字。
