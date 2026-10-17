# 塔里克：只重画跑步的腿（给 Codex 的提示词）

> 用户的决定：**跑步只修交叉步**。现在的跑步（`current/taric_run.png`，就是用户认可的那版）上半身、头、脸、披风、斧锤、每帧的晃动全部保留，**一格都不要动**；只把两条腿改成像英雄联盟原版那样**左右腿交替迈步**——现在 8 帧一直是亮的近腿在前、暗的远腿在后，从不交换。
> - 上次精修（`taric-game-redo`）把上半身固定成了第 1 帧、还清理了黑边，用户看了说"改的都不像塔里克了"，所以这次**只动腿**，别的什么都不改，也不要清理黑边。
> - 只在 `guide/edit_mask.png` 的白色区域里改（每格：站位点下面 1 行到鞋底、站位点后方 12 格往前；斧锤头下面从 +8 行往下也可以，给往后蹬的脚留位置）。白色区域以外的每一格必须和 `current/taric_run.png` 完全一样。

## 附图

| 文件 | 内容 |
|---|---|
| `current/taric_run.png`、`current/taric_run_1x.png`、`current/taric_cells.json` | 现在的跑步（8 倍和 1 倍，4 列 × 2 行，每格 96×96 个游戏像素），每帧的站位点和时长 |
| `guide/edit_mask.png` | 可以改的范围：白色 = 可以改，黑色 = 不许动（和 `current/taric_run.png` 同样大小） |
| `guide/edit_area.png` | 同一范围叠在现在的跑步上（不许动的部分压暗） |
| `guide/lol_run_legs.png` | 英雄联盟的跑步，同样的格子：**近腿橙色**、**远腿蓝色** |
| `guide/run_legs_now_vs_lol.png` | 逐帧：上面现在的腿（错），下面原版的腿（对） |
| `design/taric_design.png` | 色板（29 色）和待机，腿的颜色从这里取 |

## 每帧的腿（照 `guide/lol_run_legs.png`）

近腿 = 橙色，画在前面（亮一点，护腿高光朝外）；远腿 = 蓝色，在后面（暗一点，被近腿挡住一部分）。每帧都有一只脚踩在脚底线上：鞋底最低一行是每格从 0 数第 81 行（8 倍图里每格的第 648–655 像素行），往下没有任何像素。

| 帧 | 近腿（橙） | 远腿（蓝） |
|---|---|---|
| 1 | 踩地：在身体下面偏前，伸直 | 在后面：膝盖弯，脚跟抬起 |
| 2 | 还踩着地，往后移到身体下面 | 往前摆：膝盖抬起、弯着 |
| 3 | 往后蹬：在后面，脚跟抬起 | 往前伸、准备落地，从身体下面经过——两腿交叉 |
| 4 | 在后面：膝盖弯，脚离地 | 落地：在前面伸直 |
| 5 | 往前收：膝盖弯，脚离地 | 踩地：在身体下面，伸直 |
| 6 | 往前摆：膝盖抬起、弯着 | 还踩着地，往后移 |
| 7 | 往前伸、准备落地，画在远腿前面——两腿交叉 | 往后蹬：在后面，脚跟抬起 |
| 8 | 落地：在前面伸直 | 在后面：膝盖弯，脚离地；接回第 1 帧 |

腿的粗细、长度、颜色、画法照现在跑步里的腿（深褐裤子、银白分节护腿和靴子、1 格深色描边）；指引图只看哪条腿在前、哪只脚踩地、膝盖怎么弯。

## 提示词（附：`current/taric_run.png`、`guide/edit_mask.png`、`guide/lol_run_legs.png`）

```text
Game-size pixel art edit. Every 8x8 block of the attached sheets is ONE game pixel; edit on that grid only.
FIRST image: Taric's current 8-frame run, 4x2 cells of 96x96 game pixels. SECOND: the edit mask, same size: you may change ONLY the white area (the legs); every pixel in the black area must stay exactly as in the FIRST image - the head, face, hair, upper body, arms, cape, mace and each frame's own small sway. THIRD: the original run in the same cells with the legs painted apart: NEAR leg ORANGE (in front), FAR leg BLUE (behind).
Redraw only the two legs so that they alternate like the THIRD image: frames 8, 1 and 2 the near leg is planted; frames 4, 5 and 6 the far leg is planted; in frames 3 and 7 the legs cross under the body. Near leg in front and lighter, far leg behind and darker. Keep the current legs' thickness, length, colours and style (dark brown trousers, segmented silver-white greaves and boots, a 1-pixel dark outline); join them cleanly to the hips that are already there. One foot on the feet line in every frame (game-pixel row 81 counted from 0 in each cell, i.e. rows 648-655 of each 768-px cell of the 8x sheet); nothing below it. Only the palette's colours (#182CB0 is only for the eyes), alpha 0 or 255. Same sheet size and layout, transparent background, no labels.
```

## 交回（`taric-run-legs.zip`）

- `taric_run.png`：改好的跑步（8 倍，和 `current/taric_run.png` 同样大小、排版）；
- `logical/taric_run.png`：1 倍图；
- `HANDOFF.md`：每帧改了什么；并核对：白色区域以外和原图逐格一致（列出不一致的格子数，应为 0）。

## 交回前自查

- [ ] `guide/edit_mask.png` 黑色区域里的每一格和 `current/taric_run.png` 完全一样（头、身体、披风、斧锤、每帧的晃动都没动）；
- [ ] 第 8、1、2 帧近腿踩地，第 4、5、6 帧远腿踩地，第 3、7 帧两腿交叉；
- [ ] 每帧一只脚在脚底线上、往下没有像素；每帧连成一块；
- [ ] 只用色板里的颜色，每个 8×8 块一种颜色，透明度只有 0 和 255。
