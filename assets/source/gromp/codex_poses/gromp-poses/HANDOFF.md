# 魔沼蛙姿势包交付说明

18 张动作原画已全部由内置 image_gen 生成，使用本次包内的 `0_design.png`（第一版 A 定稿）、`1_head.png`、对应动作渲染图及骨架作为参考。没有用代码逐格绘制造型或拼出替代身体。

## 交付清单

每个文件均为 1254×1254 RGBA PNG：

| 文件 | 内容 |
|---|---|
| gromp-pose-a_back.png | 普攻蓄势 |
| gromp-pose-a_spit.png | 普攻张嘴吐射 |
| gromp-pose-q_puff.png | 鼓肚蓄力 |
| gromp-pose-q_belch.png | 仰身张嘴打嗝 |
| gromp-pose-e_back.png | 压低身子后缩 |
| gromp-pose-e_spit.png | 前扑、低头张嘴 |
| gromp-pose-r_rear.png | 高高仰身、肚子开始膨胀 |
| gromp-pose-r_belch.png | 大张嘴、鼓肚大嗝 |
| gromp-pose-run1.png | 蹲下准备 |
| gromp-pose-run2.png | 后腿蹬地、起身 |
| gromp-pose-run3.png | 起跳、前爪前伸 |
| gromp-pose-run4.png | 腾空、后腿蹬伸 |
| gromp-pose-run5.png | 后腿拖在后方 |
| gromp-pose-run6.png | 向下落、前爪着地 |
| gromp-pose-run7.png | 落地收腿 |
| gromp-pose-run8.png | 收回蹲姿 |
| gromp-pose-d_fall.png | 向后翻倒、张嘴、四腿抬起 |
| gromp-pose-d_down.png | 仰躺、肚皮朝上、眼睛变暗 |

附带：

- `raw/`：18 张生成器原始 PNG，逐文件哈希与生成器落盘文件一致，未经修改。
- `generation-prompts.txt`：实际提示词及参考图路径。
- `validation.json`：原始边界、交付边界、透明度、原图哈希与未重采样记录。
- `export-checks.json`：导出检查项目和限制。
- `poses-preview.png`：带名称的对照预览，仅供查看。
- `hop-preview.gif`：8 帧蛙跳检查预览，一轮约 0.53 秒；缩放仅用于预览，不是导入源。

## 处理方式与检查结论

交付 PNG 仅把 alpha 按 128 阈值变为 0/255，并平移主体，使最低不透明边界落在 y=1176；画布补为 1254×1254。主体 RGB 像素未缩放、未重新取样，也没有改画头、腿、蘑菇或添加舌头/特效。逐张验证处理后的主体像素与原始生成图裁切完全一致。

视觉检查覆盖蹲姿、张嘴、鼓肚、后腿蹬伸、落地收腿和仰躺死亡；角色配色延续定稿，未画舌头和技能特效。

## 导入时必须注意

生成器未可靠遵守严格的 7 px 方格，原稿实际格子与主体大小存在偏差。为遵守本包“不要再缩放或重新取样”的要求，本次没有通过缩小角色来伪造统一格子。**严格 7 px 网格、与定稿逐格相同的头以及各动作身体同尺寸未认证通过**。这一包是完整的 18 张动作原画交付，不应当作已经验证的游戏最终动画。

请优先按原需求从 `raw/` 测量实际格子读取，对照 `hd/idle.png` 与骨架包校正身体和头部大小，并逐帧检查近/远腿遮挡和尺寸；不要直接假定每张都能按 7 px 无损切格。`validation.json` 保存了本次未重采样处理的坐标。当前没有修改仓库、安装模组、绑定动作或执行游戏内验证。
