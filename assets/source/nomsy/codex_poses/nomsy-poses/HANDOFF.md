# 诺姆希动作包交付

交付日期：2026-10-29。范围：20 张独立像素姿势素材及原稿、预览、清单；尚未导入游戏或制作游戏动画表。

## 文件

- 普攻：`nomsy-pose-a_rear.png`、`nomsy-pose-a_spit.png`。
- 火球：`nomsy-pose-q_rise.png`、`nomsy-pose-q_roar.png`。
- 龙息：`nomsy-pose-e_back.png`、`nomsy-pose-e_breath.png`。
- 飞升：`nomsy-pose-r_up.png`、`nomsy-pose-r_fly1.png`、`nomsy-pose-r_fly2.png`、`nomsy-pose-r_land.png`。
- 移动：`nomsy-pose-run1.png` 至 `nomsy-pose-run8.png`。
- 死亡：`nomsy-pose-d_fall.png`、`nomsy-pose-d_down.png`。
- `pixel_1x/`：同名的一格一像素版本，179×179；1254 画布末尾的 1 像素透明边不参与逻辑格子。
- `raw/`：每项最终选用的 image_gen 原稿，保持原始文件不变；`raw/rejected/` 保存返修前版本，不能用于导入。
- `preview/poses-contact.png`：20 张动作汇总；`run.gif`、`wingbeat.gif`、`attack.gif`、`death.gif` 为动画预览，预览的深灰背景不是成品背景。
- `manifest.json`：逐张尺寸、格子、位置、原稿尺寸及参考边界。
- `generation-prompts.txt`：实际生成及返修提示词；文件开头的最终飞升修正覆盖早期飞升提示。
- `validation.json`：20 张成品的尺寸、硬透明、7 像素整格、地面线和 SHA256 检查。

## 模型与动作

以包内 `0_design.png` 与 `1_head.png` 为身份和配色依据，逐项提供各自的 3D 动作参考及骨架给内置 image_gen。保留粉色圆肚子、绿眼睛、白獠牙、紫色额纹和头刺、两片肩翼及短粗刺尾。细长结构是近侧翼臂，不是尾巴。

张嘴动作不含火球、火焰或伸出的长舌。吸气帧已返修为闭嘴。run6、run7 已移除误生在翼臂上的小刺。飞升平展和下扇帧最终直接从同一张 r_up 原稿编辑，只改变两翼方向，以减少身体与脚的位置跳动。弃用的原版本在 rejected 中。

## 技术导出

成品均为 1254×1254 RGBA，真实透明，alpha 只有 0 和 255，7×7 硬像素格从画布左上角对齐；最后可见像素 y=1175，脚底接触 y=1176 的地面线。空中动作也按这一线导出，游戏端负责抬高。

生成器未稳定输出严格格子，因此保留生图原稿，同时以定稿采样色板和多数色读回进行整数网格导出。按粉色身体面积归一化体量，按身体位置而非翼展边界定位，避免展开翅膀导致身体缩小。没有用代码绘制替代身体或新动作。

姿势为生图对骨架参考的像素画表达，头脸和关节不是逐像素复制或骨骼重投影。帧间仍有像素级造型差异，不能将格式检查理解成游戏内动画/碰撞/UI验收。raw 可供后续高密度导入或局部精修；不要把预览 GIF 当成游戏动画配置。
