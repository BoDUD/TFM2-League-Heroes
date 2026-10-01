# 黛安娜：跑步的胯重画，让腿和身体接上（给 Codex）

> 用户在游戏里看了加粗前、加粗后两版，都说腿和身体是分开的：「你修改后不是上下身体又分离了吗 这个问题一直解决不了？」「这两张不都有腿和身体分离的感觉吗」。
>
> **原因在胯**：前三次返修都要求第 0–61 行逐格不动，你只能从第 62 行往下接腿。结果：
> - 上半身到第 61 行只剩一截 3–4 格宽的深蓝腰，裙甲往身后飘；
> - 腿从第 62 行开始，顶上自带一条横着的黑描边，4–8 格长（`guide/hip_seam_now.png` 里的红线）；
> - 所以不管腿粗还是细，腰和腿之间都有一道横切线，腿像单独贴在身体下面的一块。
>
> 待机没有这个问题（`guide/hip_seam_now.png` 右下）：裙甲的几片甲板从腰带垂下来，盖住两条大腿的上端，腿从裙甲下面接出来，中间没有横线。英雄联盟原版的跑步也是这样，见 `league/lol_run_hips.png`：蓝色的裙甲盖在青色、品红两条腿的上端。

## 这次重画胯（黄框里）

- **可以改的范围**：每帧黄框里的腰、腰带、裙甲和大腿上端，即第 54–67 行、第 30–55 列。黄框里如果有手、手臂或月刃，照旧不动。
- **黄框外一格都不动**：
  - 头、脸、头发、马尾、肩、手臂、月刃；
  - 第 68 行以下的腿，也就是上次加粗的腿：姿势、宽度、颜色、脚的位置都不变。
- **要的样子**（照待机和原版）：
  - 腰带下面挂裙甲。前片盖住近腿（亮的那条）大腿的上端；后片照现在往身后飘，盖住远腿大腿的上端。裙甲用待机裙甲的青绿色，带金边。
  - 大腿从裙甲下面接出来，往上伸进裙甲里面。裙甲和大腿之间只有裙甲下沿那一格描边，**不要有横贯两条腿的黑线**。
  - 腰往下变宽成胯。胯的宽度和第 64 行两条大腿加起来差不多，不能是一根细腰插在一块宽腿上。腿在躯干正下方，不往前也不往后错开。
  - 裙甲跟着腿动：抬起的腿顶起前片，往后蹬的腿从后片下面伸出去。
- 每帧踩地那只脚的鞋底在第 79 行，第 80 行以下全透明。每帧是连在一起的一整块，没有碎点。

## 画法

- **直接在 1 倍图上逐格画**：96×96 的格子，一格就是游戏里的一个像素。不要生成大图再缩小。
- 只用定稿的 26 色：裙甲用待机裙甲的青绿和金边，腿的颜色照上次。

## 规则

- 格子、排版、帧数、帧长照 `now/now_manifest.json`：8 帧，每帧 125 毫秒，4 列 × 2 行；每格 96×96（1 倍）、768×768（8 倍）。站位点和 eye_mark 不变。
- 8×8 方块；透明度只有 0 和 255；一格黑色描边。
- 不要贴头，不要擦头周围。

## 交付

- `diana_run.png`（8 倍）、`native/diana_run_1x.png`（1 倍）、`manifest.json`、`HANDOFF.md`。
- 一张检查图：8 帧的胯放大，和待机的胯并排；写明黄框外和上次逐格相同。

```text
Pixel art sprite REVISION for a small tactics game: chunky 8x8 squares, hard edges, no anti-aliasing, a 1-square dark outline, only the design's 26 colours. Character: Diana (silver-white hair, silver armour, a teal armoured skirt with gold trim, dark navy leggings with gold knee guards, silver greaves and dark boots, a crescent blade behind her), running to the right, 8 frames of 125 ms. In every frame her legs look cut off from her body: the torso ends in a thin waist, the skirt flares back, and the legs start below with their own horizontal dark outline across the hips. Redraw ONLY the hip zone (rows 54-67, columns 30-55 of each 96x96 cell; keep any hand, arm or blade inside it): hang the skirt's plates from the belt so the front plate covers the top of the near (bright) thigh and the back plate, flaring behind as now, covers the top of the far thigh; the thighs continue up under the skirt with no horizontal dark line across them, only the skirt's lower edge outline; the waist widens into hips about as wide as both thighs together, the legs straight under the torso; a raised leg lifts the front plate, a leg pushing back comes out from under the back plate. Keep everything else square for square: head, face, hair, ponytail, shoulders, arms, blade, and the legs from row 68 down (their pose, width, colours and feet). Draw directly at 1x, square by square; do NOT generate a large image and scale it down. The planted sole stays on row 79, nothing below it, one connected piece per frame. Same layout: 4 columns x 2 rows of 96x96 cells (768x768 at 8x).
```

## 附件

| 文件 | 内容 |
|---|---|
| `now/diana_run_now_1x.png`、`_8x.png`、`now_manifest.json` | 现在的跑步（你上次加粗腿的那版），在这上面改胯 |
| `now/diana_run_in_game_8x.png` | 现在游戏里的跑步：Claude 整理过，贴回定稿的脸、补齐描边、左移站位点 |
| `now/diana_idle_8x.png` | 定稿待机：裙甲怎么盖住大腿，照它 |
| `guide/hip_seam_now.png` | 8 帧的胯放大 10 倍。红线是接缝（腿顶的横黑线），黄框是这次可以改的范围；右下是待机的胯 |
| `league/lol_run_hips.png` | 英雄联盟原版跑步按游戏尺寸渲染，胯放大 10 倍。上排原图；下排部件：蓝 = 身体和裙甲，青、品红 = 两条腿 |
| `league/lol_run_game_size_8x.png`、`lol_run_parts.png` | 英雄联盟原版跑步整图和部件图 |
| `diana_cells.json` | 格子和站位点 |
