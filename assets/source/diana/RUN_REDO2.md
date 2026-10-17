# 黛安娜：跑步的腿再返修一次（给 Codex）

> 用户在游戏里看到：「戴安娜走路的时候出现上下身体分割」「有一半腿露在身体外面」。
> 你上次交回的跑步（`now/diana_run_last_delivery_*.png`，已经在游戏里：`now/diana_run_in_game_8x.png`）换腿换对了，但和英雄联盟原版比（`guide/compare_lol_vs_now.png`：上排原版，下排现在）：
> 1. **步子太大**：第 4、8 帧两腿劈得很开，前腿远远伸到身体前面，后腿拖到身体后面，一半腿在身体轮廓外面。原版两腿一直收在身体下面，最大步幅时两脚也只隔 10～12 格。
> 2. **后踢的腿没有大腿**：第 2、5、6 帧往后踢的那条腿，大腿被裙甲挡住，只剩半截小腿横在身后，像从身体外面长出来的。
> 3. **腰上一道浅色横带**：第 1、5、7 帧裙甲下沿有一排金色 / 皮肤色的格子横在腰上，缩到游戏大小像把身体切成上下两段（`guide/waist_now_8frames.png`，红线是第 60、65、70、75 行）。
> 4. 第 4、8 帧各有一小块和身体不相连的碎点。
> 上半身每帧完全不动、腿却大幅摆动，所以播放时上下身像两块各动各的。

## 这次只重画胯以下

- **胯以上逐格不动**：头、脸、头发、马尾、盔甲、手臂、月刃、披风、裙甲，全部照 `now/diana_run_last_delivery_*.png`，头和身体的位置也不动。
- **腿照原版的跑步**（`league/lol_run_game_size_8x.png` 是英雄联盟原版按游戏尺寸渲染的 8 帧，格子和站位与你的一样；`league/lol_run_parts.png` 同一套帧按部件上色：红 = 头发，绿 = 月刃，蓝 = 身体，**青色和品红各是一条腿**）：
  - 两条腿都从裙甲下沿直接长出来，**大腿看得见**；往后踢时画出从胯往后下方的大腿、弯曲的膝盖和往上翘的小腿，不要只画一截悬空的小腿。
  - 步幅照原版：最大（第 4、8 帧）两脚相距不超过 12 格，脚和膝盖都在身体下面附近，不要伸到身体前后很远。
  - 近腿（金色护膝朝着看的人、颜色亮）第 1–4 帧踩地，远腿（暗一点）第 5–8 帧踩地，第 4、8 帧两腿交叉——这点上次已经对了，保持。
  - 每帧踩地那只脚的鞋底在脚底线上（和现在一样的那一行），不浮空，脚底线以下没有像素。
- 腰上不要有浅色横带：裙甲下沿接深蓝的腿，金色只在护膝上。
- 不要有和身体分开的碎点。

## 规则

- 格子、排版、帧数、帧长全部照上次：8 帧 × 125 毫秒，4 列 × 2 行，每格 96×96（1 倍图）、8 倍图每格 768×768；站位点和 `diana_cells.json`、`now/last_manifest.json` 一样。
- 只用定稿的 26 色（`now/diana_idle_8x.png` 里的颜色），8×8 方块，透明度只有 0/255，一格黑色描边。
- 不要贴头、不要擦头周围；整个人一起交。

## 交付

- `diana_run.png`（8 倍）和 `native/diana_run_1x.png`（1 倍），`manifest.json`（格式照 `now/last_manifest.json`：每帧的 pivot 和 eye_mark），`HANDOFF.md`。
- 另交一张检查图：8 帧并排，每帧旁边放同一帧的原版（`league/`），看腿的位置和步幅是不是对得上。

```text
Pixel art sprite REVISION for a small tactics game, chunky 8x8 squares, hard edges, no anti-aliasing, 1-square dark outline, the design's 26 colours only. Character: Diana (silver-white hair, silver armour, dark blue leggings with gold knee guards and silver greaves, a crescent blade behind her), running to the right, 8 frames of 125 ms. Keep everything from the hips up exactly as in the attached run strip (head, face, hair, ponytail, armour, arms, blade, cape, skirt, their positions). Redraw ONLY the legs from the hips down, following League's run in the attached reference (same cells and pivots; in the parts image cyan and magenta are the two legs): both legs grow straight out from under the skirt's lower edge with the thighs visible; a leg kicking back shows its thigh going back and down from the hip, a bent knee and the shin raised behind - never a lone shin floating behind the cape; a compact stride - at its widest (frames 4 and 8) the feet at most 12 squares apart, knees and feet near the body, not reaching far in front or behind; the near leg (bright gold knee guard facing the viewer) planted in frames 1-4, the far leg (darker) in 5-8, crossing in 4 and 8; the planted sole on the same ground row as now, no floating, nothing below it; no light band across the waist (gold only on the knee guards); no loose specks. Same layout: 4 columns x 2 rows of 96x96 cells (768x768 at 8x).
```

## 附件

| 文件 | 内容 |
|---|---|
| `now/diana_run_last_delivery_1x.png`、`_8x.png`、`last_manifest.json` | 你上次交回的跑步（在这上面改腿）和它的清单 |
| `now/diana_run_in_game_8x.png` | 现在游戏里的跑步（Claude 整理后：贴回定稿的脸、落地、左移站位点） |
| `now/diana_idle_8x.png` | 定稿待机（颜色和腿的材质照它） |
| `league/lol_run_game_size_8x.png` | 英雄联盟原版跑步，按游戏尺寸渲染，同样的格子 |
| `league/lol_run_parts.png` | 同上，按部件上色（青、品红 = 两条腿） |
| `guide/compare_lol_vs_now.png` | 上排原版、下排现在，8 帧对比 |
| `guide/waist_now_8frames.png` | 现在每帧腰到脚的放大图（红线第 60、65、70、75 行） |
| `diana_cells.json` | 格子和站位点 |
