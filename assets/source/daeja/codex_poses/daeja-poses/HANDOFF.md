# 迭嘉动作素材交接

## 本包内容

21 张独立动作图已全部生成，采用用户本轮包内的 `0_design.png`、`1_head.png` 和每张对应的模型/骨架参考。使用内置 image_gen，共 27 次成功生图（21 张首稿和 6 张修订），未用代码绘制替代角色。

- 根目录 `daeja-pose-*.png`：21 张整理版，均为 1254×1254 RGBA，alpha 只有 0/255。
- `raw/daeja-pose-*.png`：每张选用的原始生成图，保留原始字节；生图的原始尺寸和 alpha 以文件自身及 manifest 为准。
- `raw/attempt1-*.png`：6 张被修订的首稿，作为过程留档，不能当作额外动作帧混用。
- `pixel_1x/`：21 张整理版的逐格图，逻辑画布 125×125；不是已经缩到游戏内的40格高角色。
- `preview.png`：逐帧总览；`run-loop.gif`：8帧循环预览（每帧120ms，仅作查看）。
- `manifest.json`：尺寸、包围框、格子、基线、源图对应和 SHA-256。
- `generation-prompts.txt`、`generation-history.json`：27次实际提示词及原始生成路径。
- `validation.json`：两包联检结果和未验收事项。

## 处理与坐标

原图由 image_gen 绘制。整理版仅做固定色板取色、逐格读回、硬alpha、等比尺寸/位置整理，没有用代码画新身体、腿或翅膀。逐格时先按透明覆盖率判断占用，再取占用像素的多数颜色；不插值绘画。

定稿实际是10px格子，纵向格线相位为6px，脚底在y=1176。因此整理版使用 `grid_px=10`、`grid_origin=[0,6]`、`baseline_y=1176`。这与说明中的“网格从(0,0)开始”有6px偏差，采用定稿的实际格线以保住1176基线；不要从y=0直接按10px切图。使用 `pixel_1x/` 可跳过该偏移问题。

## 验收边界

通过的机械检查：21张齐全、1254×1254、非空、硬alpha、10px整格、统一1176基线、1倍与10倍整理图一致。跑步八帧和死亡/前扫帧已重绘修订，原始尝试均留档。

**严格美术要求仍未全部达标：生成帧的头部不是逐格复制的同一个头，局部头盔/鬃毛和翼膜结构有变化；与骨架的贴合、双翼实际长度、各动作身体体量和跑步换腿仍需逐帧人工复核或修正。** 文件数量与格式检查通过不能代替这些要求的验收。本包可作完整数量的生成素材交接，不应直接标记为游戏模型最终验收通过。

本轮未修改游戏工程、未导入图集、未连接技能运行时，未做游戏内动作/地形/UI测试。

## 21张清单

- `daeja-pose-a_wind.png`
- `daeja-pose-a_punch.png`
- `daeja-pose-q_raise.png`
- `daeja-pose-q_sweep.png`
- `daeja-pose-e_beat.png`
- `daeja-pose-e_hop.png`
- `daeja-pose-r_up.png`
- `daeja-pose-r_fly1.png`
- `daeja-pose-r_fly2.png`
- `daeja-pose-r_blast.png`
- `daeja-pose-r_land.png`
- `daeja-pose-d_fall.png`
- `daeja-pose-d_down.png`
- `daeja-pose-run1.png`
- `daeja-pose-run2.png`
- `daeja-pose-run3.png`
- `daeja-pose-run4.png`
- `daeja-pose-run5.png`
- `daeja-pose-run6.png`
- `daeja-pose-run7.png`
- `daeja-pose-run8.png`
