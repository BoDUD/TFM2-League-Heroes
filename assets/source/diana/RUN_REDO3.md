# 黛安娜：跑步的腿加粗（给 Codex）

> 用户在游戏里看了你上次交回的跑步（`now/diana_run_last_delivery_*.png`）。步子收回来了，换腿也对，但「戴安娜的腿太细」。
>
> 原因：上次的腿是先生成大图（每条腿约 280 像素高），再缩小约 15 倍贴上去的。缩完以后：
> - 小腿只剩 2–3 格宽（含描边），里面几乎没有颜色；
> - 护膝、护胫碎成零星的点。
>
> 待机的腿是：小腿 4–5 格，膝盖 5–6 格，靴子 5–7 格。对比见 `guide/leg_widths.png`：左上是待机，其余是现在跑步的 8 帧，每格下面写着第 72、75、78 行的宽度。

## 这次只把腿加粗

- **腿的位置和动作不变**。下面这些全部照上次交回的，只沿着现在的腿往两边加宽：
  - 每帧两条腿的走向（胯→膝→脚），膝盖和脚的位置；
  - 哪只脚踩地，第 4、8 帧两腿交叉；
  - 步幅：两脚最多相距 10–12 格。
- **宽度照待机**（都含两边各 1 格的黑色描边）：

  | 部位 | 宽度 |
  |---|---|
  | 大腿 | 5–6 格 |
  | 膝盖 | 5–6 格 |
  | 小腿 | 4–5 格 |
  | 靴子 | 5–6 格 |
  | 鞋底那一行 | 5–7 格 |

  远腿（暗的那条）露出来的部分也一样宽；被近腿挡住的地方，用近腿的描边隔开。
- **材质照待机**：
  - 深蓝紧身裤：#22233C、#333B63，亮面 #505169；
  - 金色护膝：#A7804A、#F3D98D，只在膝盖上；
  - 银色护胫：#B8BFC7，暗面 #60637E，在小腿前面；
  - 深色靴子：#22233C、#333B63。

  近腿亮，远腿暗。腿上不要用月刃的浅青色（#D0F6EE、#7BB2B9）。上次第 8 帧的小腿用了浅青色，Claude 导入时已经换成银色，`now/` 里的就是换过的。
- **胯以上逐格不动**：第 0–61 行（头、脸、头发、马尾、盔甲、手臂、月刃、披风、裙甲）一格都不改。腿从裙甲下沿直接接出来，裙甲下沿不要出现浅色横带。
- 每帧踩地那只脚的鞋底在第 79 行，第 80 行以下全透明。每帧是连在一起的一整块，没有碎点。

## 画法（重要）

- **直接在 1 倍图上逐格画**：96×96 的格子里，一格就是游戏里的一个像素。也可以用代码沿着现在腿的中线，按上面的宽度和待机的颜色一格一格填。
- **不要再先生成大图再缩小**：缩小会把腿变细，把颜色打碎。
- 可以把待机的腿当贴片用：大腿、膝盖、小腿、靴子各段，按现在跑步里那一段的角度摆上去。

## 规则

- 格子、排版、帧数、帧长照上次：8 帧，每帧 125 毫秒，4 列 × 2 行；每格 96×96（1 倍）、768×768（8 倍）。站位点和 eye_mark 照 `now/last_manifest.json`。
- 只用定稿的 26 色（`now/diana_idle_8x.png` 里的颜色）；8×8 方块；透明度只有 0 和 255；一格黑色描边。
- 不要贴头，不要擦头周围。

## 交付

- `diana_run.png`（8 倍）、`native/diana_run_1x.png`（1 倍）、`manifest.json`（格式照 `now/last_manifest.json`）、`HANDOFF.md`。
- 一张检查图：8 帧的腿并排放大，旁边放待机的腿，标出每帧膝盖、小腿、靴子的格数。

```text
Pixel art sprite REVISION for a small tactics game: chunky 8x8 squares, hard edges, no anti-aliasing, a 1-square dark outline, only the design's 26 colours. Character: Diana (silver-white hair, silver armour, dark blue leggings with gold knee guards, silver greaves and dark boots, a crescent blade behind her), running to the right, 8 frames of 125 ms. Edit the attached run strip (now/diana_run_last_delivery): keep everything from row 61 up exactly as it is (head, face, hair, ponytail, armour, arms, blade, cape, skirt), and keep the legs' poses exactly: the same hip-knee-foot lines, the same planted foot, the same compact stride and crossing in frames 4 and 8. Only make the legs THICKER, to the idle's widths, counting the 1-square dark outline on both sides: thigh 5-6 squares, knee 5-6, shin 4-5, boot 5-6, the sole row 5-7. Use the idle's materials: dark navy leggings (#22233C, #333B63, light #505169), gold knee guards (#A7804A, #F3D98D) on the knees only, silver greaves (#B8BFC7, shade #60637E) on the shins, dark boots; the near leg bright, the far leg darker; never the blade's pale cyan on the legs. Draw directly at 1x, square by square, in the 96x96 cells (one square = one game pixel); do NOT generate a large image and scale it down. The planted sole stays on row 79, nothing below it, no loose specks. Same layout: 4 columns x 2 rows of 96x96 cells (768x768 at 8x).
```

## 附件

| 文件 | 内容 |
|---|---|
| `now/diana_run_last_delivery_1x.png`、`_8x.png`、`last_manifest.json` | 你上次交回的跑步，第 8 帧小腿已换成银色。在这上面加粗腿 |
| `now/diana_run_in_game_8x.png` | 现在游戏里的跑步：Claude 整理过，贴回定稿的脸、补齐描边、左移站位点 |
| `now/diana_idle_8x.png` | 定稿待机：腿的宽度和材质照它 |
| `guide/leg_widths.png` | 待机和现在 8 帧的腿放大 10 倍，标了第 72、75、78 行的宽度 |
| `league/lol_run_game_size_8x.png`、`lol_run_parts.png` | 英雄联盟原版跑步，按游戏尺寸渲染（腿的位置以上次交回的为准） |
| `diana_cells.json` | 格子和站位点 |
