# 塔里克：让跑步的交叉步更明显（给 Codex 的提示词）

> 你上次交回的腿（`taric-run-legs`）位置和节奏都对：第 8、1、2 帧近腿着地，第 4、5、6 帧远腿着地，第 3、7 帧交叉。我又清了一遍黑边和只闪一帧的杂点（`current/taric_run.png` 是现在的样子）。用户看了说**"怎么感觉交叉步不是很明显？"**——原因是两条腿颜色一样（都是银白护腿、深褐裤子），游戏尺寸下分不出哪条在前、哪条在后，交叉就看不出来。
> 这次**只改腿的颜色深浅和交叉那一下**，腿的位置、动作、长短照现在的；`guide/edit_mask.png` 黑色区域以外（头、身体、披风、斧锤、每帧的晃动）一格都不要动。

## 要改的

1. **远腿（在后面那条）整体压暗**：每一帧都用暗一到两级的颜色——裤子用最深的褐色（`#2D1725`、`#361B29`、`#502C3F`），护腿和靴子用暗灰（`#4C4E5D`、`#707E8B`），不要银白高光；描边照旧 1 格 `#170F1D`。
2. **近腿（在前面那条）保持亮**：裤子用 `#6F3F53`、`#502C3F`，护腿和靴子用银白（`#CBDDE0`、`#ADBFC7`、`#8FA3AC`），护腿上留一两格亮高光（`#FDFDFD` 或 `#CBDDE0`）。
3. **8 帧里同一条腿始终是同一套颜色**：近腿在第 1–8 帧都是亮的那条，远腿都是暗的那条（不要因为谁在前面就换颜色），这样一眼就能看出两条腿在交替。
4. **第 3、7 帧把交叉画清楚**：两个膝盖在身体下面前后错开、互相经过；第 3 帧暗的远腿往前伸、亮的近腿在后面蹬，第 7 帧亮的近腿往前伸、盖在暗的远腿前面。
5. 每帧都有一只脚在脚底线上（每格从 0 数第 81 行，8 倍图里每格的第 648–655 像素行），往下没有任何像素；每帧连成一块。

## 附图

| 文件 | 内容 |
|---|---|
| `current/taric_run.png`、`current/taric_run_1x.png`、`current/taric_cells.json` | 现在的跑步（8 倍、1 倍）和站位点、时长：在它上面改 |
| `guide/edit_mask.png`、`guide/edit_area.png` | 可以改的范围（白色），和上次一样 |
| `guide/lol_run_legs.png` | 英雄联盟的跑步：近腿橙、远腿蓝（看哪条在前） |
| `design/taric_design.png` | 29 色色板 |

## 提示词（附：`current/taric_run.png`、`guide/edit_mask.png`、`guide/lol_run_legs.png`）

```text
Game-size pixel art edit. Every 8x8 block of the attached sheets is ONE game pixel; edit on that grid only.
FIRST image: Taric's 8-frame run (4x2 cells of 96x96 game pixels). SECOND: the edit mask - change ONLY the white area (the legs); every pixel in the black area must stay exactly as in the FIRST image. THIRD: the original run, near leg orange, far leg blue.
The legs already alternate correctly (frames 8, 1, 2 near leg planted; 4, 5, 6 far leg planted; 3 and 7 crossing) but both legs have the same colours, so the crossing step does not read. Keep every leg's position, pose and length; recolour and touch up so that: the FAR leg is darker in all 8 frames (darkest browns #2D1725 #361B29 #502C3F for the trousers, dark greys #4C4E5D #707E8B for the greaves and boots, no silver highlights); the NEAR leg stays light in all 8 frames (#6F3F53 #502C3F trousers, silver-white #CBDDE0 #ADBFC7 #8FA3AC greaves with one or two bright highlight pixels); the same leg keeps the same colours in every frame; in frames 3 and 7 the two knees clearly pass each other under the body (frame 3: dark far leg reaching forward, light near leg pushing off behind; frame 7: light near leg reaching forward IN FRONT of the dark far leg). 1-pixel #170F1D outline. One foot on the feet line (game-pixel row 81 counted from 0 in each cell, rows 648-655 of each 768-px cell of the 8x sheet) in every frame, nothing below it; each frame one connected piece. Only palette colours (#182CB0 is only for the eyes), alpha 0 or 255. Same sheet size and layout, transparent background, no labels.
```

## 交回（`taric-run-legs2.zip`）

- `taric_run.png`（8 倍，和 `current/taric_run.png` 同样大小、排版）、`logical/taric_run.png`（1 倍）；
- `qa/leg-ownership.png`：每帧近腿、远腿分别涂色的核对图；
- `HANDOFF.md`：每帧改了什么；黑色遮罩区域以外和原图不一致的格子数（应为 0）。
