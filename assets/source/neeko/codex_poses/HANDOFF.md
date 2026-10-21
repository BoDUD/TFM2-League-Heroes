# 妮蔻 17 个动作姿势交付

17 个姿势均由内置 image_gen 各画一次，参考仅使用 neeko_pose_pack.zip 中的定稿、头、对应骨架、英雄联盟姿势和定稿骨架示意。没有用脚本绘制人体、逐格写角色或重新拼接肢体。

## 文件

- 根目录 `neeko-pose-*.png`：17 张整理版，1254×1254、10px 整格、硬透明。
- `raw/`：17 张 image_gen 原稿，逐字节保留，与 manifest 的哈希一致。
- `pixel_1x/`：整理版的 125×125 格原尺寸，根目录图片由其最近邻放大 10 倍，画布末尾 4px 保留透明。
- `reference/approved-head-1x.png`：由包内 1_head.png 按原 8 倍格读取的 45×41 定稿头，灰底转透明，供 rig 统一使用。
- `generation-prompts.txt`：17 次实际提示词和参考文件顺序。
- `manifest.json`：画布、格子、原稿尺寸和哈希、整体缩放／平移、可见边界、原骨架头框。
- `qa/overview.png`：17 张总览。
- `qa/run-preview.gif`：run1–4 的快速预览，不代表最终游戏时序或跑步已通过实战验收。
- `qa/validation.json`：导出检查结果。

## 姿势清单

stance、thrust、kick、pounce、tuck、throw_air、coil、fling、hunch、soar、land、run1、run2、run3、run4、twirl、sit。

## 整理方式

使用定稿调色板，对生成原稿作整格前景多数取色，alpha 原稿阈值 128、每格前景覆盖阈值 25%；移除不超过 2 格的孤立透明噪点组件。输出 alpha 仅 0/255，透明 RGB 清零。整理过程没有重画身体或旋转、拼接腿臂来替代动作绘制。

着地姿势把最低可见点整体对齐至 y=1180。空中姿势最低可见点按 thrust 1120、tuck 1060、throw_air 1040、coil 1100、soar 980 对齐。最低可见点可能是尾巴或其他肢体，因此它不是自动识别出的脚部关键点证明。如果为了给空中动作留出高度会裁到原稿，则对整张人物等比缩小后再平移，没有独立拉长或压短肢体。

soar 的源骨架头框在画布顶端被截断；生图提示词明确要求完整保留头发和羽刺，避免照抄裁切。

## 已检查

17 张齐全且彼此不同；1254×1254 画布；125×125 格数据；每格 10px 且从 (0,0) 对齐；alpha 只有 0/255；透明 RGB 清零；图像与格子版逐像素对应；可见边界落在记录的位置；原始生成文件哈希未变。已检查总览，姿势之间有清楚差异，没有可见骨架线、网格、地面线或技能特效。

## 后续 rig 的明确工作

这些是生成的动作造型原稿和整理版，不是已通过全部 rig 验收的游戏动作。生成器在每张图重绘了头部，不能声称 17 张脸与定稿逐像素相同；头大小、头框位置、肢体及尾巴长短粗细也没有通过骨架数值校准。manifest 中 head_pixel_identical_to_reference 均明确为 false。

按包内既定流程，后续须用 reference/approved-head-1x.png 统一换头，在 rig_neeko.py 拼帧前测量、校准肢体与尾巴比例，并检查手臂连接、近远侧腿、跑步相位和头部位置。不能只因静态导出检查 PASS 就跳过这些造型验收。尤其 pounce／land 的高尾姿势、hunch 的头身比例和 run1–4 的近远腿交替，需要放到最终游戏尺度再次检查。

动作安排沿用包内方案：普通攻击 stance→thrust；强化攻击 kick→pounce；Q stance→tuck 空翻→throw_air→land；E coil→fling；R hunch→soar→land；死亡 twirl→sit；跑步 run1–4。待机和受击来自定稿。本交付没有修改外部仓库、rig_neeko.py 或游戏运行文件，也没有声称已完成游戏实战验证。
